import pytest
from decimal import Decimal


def test_preco_teto_ativo_existente(auth_client, ativo_seed):
    """Endpoint protegido — retorna preço teto para ativo existente no banco de teste."""
    rv = auth_client.get(
        f'/api/calculos/preco_teto/{ativo_seed.ticker}',
        headers=auth_client._auth_headers,
    )
    data = rv.get_json()
    assert rv.status_code == 200
    assert data['ativo'] == ativo_seed.ticker
    assert data['mercado'] == ativo_seed.mercado
    assert 'pt_medio' in data
    assert 'parametros_regiao' in data
    assert 'taxa_livre_risco' in data['parametros_regiao']


def test_preco_teto_ativo_inexistente(auth_client):
    """Ativo não encontrado retorna 404."""
    rv = auth_client.get(
        '/api/calculos/preco_teto/TICKER_FAKE_XYZ',
        headers=auth_client._auth_headers,
    )
    assert rv.status_code == 404


def test_preco_teto_sem_auth_retorna_401(client):
    """Endpoint protegido por JWT — sem token retorna 401."""
    rv = client.get('/api/calculos/preco_teto/QUALQUER')
    assert rv.status_code == 401


# ---------------------------------------------------------------------------
# BUG-VAL-006 — Fórmula FII: dy_anual / cap_rate (não 1 / cap_rate)
# ---------------------------------------------------------------------------

@pytest.fixture(scope='function')
def fii_seed(app):
    """
    FII de teste com dados realistas para validação da fórmula de cap rate.
    HGLG11-like: preco_atual=152.30, dividend_yield=0.082, mercado=BR.
    Esperado pt_cap_rate = (0.082 * 152.30) / cap_rate_fii_BR
    Com cap_rate_fii_BR=0.089 → pt ≈ 140.22; com fallback 0.08 → pt ≈ 156.11
    """
    import uuid as uuid_lib
    from app.models.ativo import Ativo, TipoAtivo, ClasseAtivo
    from app.database import db as _db

    suffix = str(uuid_lib.uuid4().int)[:6]
    ticker = f'FI{suffix}'
    a = Ativo(
        ticker=ticker,
        nome=f'FII Seed {ticker}',
        tipo=TipoAtivo.FII,
        classe=ClasseAtivo.RENDA_VARIAVEL,
        mercado='BR',
        moeda='BRL',
        preco_atual=Decimal('152.30'),
        dividend_yield=Decimal('0.082'),
        ativo=True,
    )
    _db.session.add(a)
    try:
        _db.session.commit()
    except Exception:
        _db.session.rollback()
        raise
    _db.session.refresh(a)

    yield a

    # Limpeza feita por cleanup_test_data


def test_preco_teto_fii_formula_dy_anual(auth_client, fii_seed):
    """
    BUG-VAL-006 — FII: pt_medio deve ser dy_anual / cap_rate_fii, NÃO 1 / cap_rate.

    Com preco_atual=152.30, dividend_yield=0.082 e cap_rate_fii regional (BR default=0.08):
      dy_anual = 0.082 * 152.30 = 12.489
      pt_esperado = 12.489 / 0.08 ≈ 156.11  (usando fallback; varia com banco)

    Garantias do teste:
      1. Retorna HTTP 200 e ativo correto.
      2. pt_medio > 50 (elimina o resultado absurdo antigo 1/0.08 = 12.50).
      3. pt_medio está na faixa razoável: 0.5x a 2.0x o preco_atual (80% a 305).
      4. metodos['cap_rate']['pt'] == pt_medio (único método para FII).
    """
    rv = auth_client.get(
        f'/api/calculos/preco_teto/{fii_seed.ticker}',
        headers=auth_client._auth_headers,
    )
    data = rv.get_json()
    assert rv.status_code == 200
    assert data['ativo'] == fii_seed.ticker

    pt_medio = data['pt_medio']
    preco_atual = float(fii_seed.preco_atual)

    # Resultado antigo (1/cap_rate) seria ~12.50; novo deve ser muito maior
    assert pt_medio > 50, (
        f"pt_medio={pt_medio} parece ser resultado da fórmula antiga (1/cap_rate)"
    )

    # Faixa razoável: 50% a 200% do preço atual
    assert preco_atual * 0.5 <= pt_medio <= preco_atual * 2.0, (
        f"pt_medio={pt_medio} fora da faixa esperada [{preco_atual*0.5:.2f}, {preco_atual*2.0:.2f}]"
    )

    # Único método para FII: cap_rate
    assert 'cap_rate' in data['metodos']
    assert data['metodos']['cap_rate']['pt'] == pt_medio


def test_preco_teto_fii_sem_dividend_yield(auth_client, app):
    """
    BUG-VAL-006 — FII sem dividend_yield explícito (None): o blueprint usa dy=0.06 por padrão
    e o pt_meio deve ser >0 e coerente com dy_anual/cap_rate (não 1/cap_rate).

    Nota: Decimal('0.00') é falsy em Python, portanto o blueprint aplica o fallback 0.06;
    este teste documenta esse comportamento pré-existente e garante que não há exceção.
    """
    import uuid as uuid_lib
    from app.models.ativo import Ativo, TipoAtivo, ClasseAtivo
    from app.database import db as _db

    suffix = str(uuid_lib.uuid4().int)[:6]
    ticker = f'FZ{suffix}'
    a = Ativo(
        ticker=ticker,
        nome=f'FII Sem DY {ticker}',
        tipo=TipoAtivo.FII,
        classe=ClasseAtivo.RENDA_VARIAVEL,
        mercado='BR',
        moeda='BRL',
        preco_atual=Decimal('100.00'),
        # dividend_yield=None → blueprint usa fallback dy=0.06
        ativo=True,
    )
    _db.session.add(a)
    try:
        _db.session.commit()
    except Exception:
        _db.session.rollback()
        raise
    _db.session.refresh(a)

    try:
        rv = auth_client.get(
            f'/api/calculos/preco_teto/{ticker}',
            headers=auth_client._auth_headers,
        )
        data = rv.get_json()
        assert rv.status_code == 200
        pt_medio = data['pt_medio']
        # dy=0.06 (fallback), preco=100, cap_rate~0.08 → pt≈75; antigo seria 1/0.08=12.5
        assert pt_medio > 50, (
            f"pt_medio={pt_medio} parece resultado da fórmula antiga (1/cap_rate~12.5)"
        )
        assert pt_medio > 0
    finally:
        _db.session.rollback()
        Ativo.query.filter_by(ticker=ticker).delete()
        _db.session.commit()
