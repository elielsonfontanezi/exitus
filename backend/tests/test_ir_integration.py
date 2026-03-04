# -*- coding: utf-8 -*-
"""
EXITUS-IR-001 + IR-002 — Testes de integração para engine de IR.
Cobre os 3 endpoints: /api/ir/apuracao, /api/ir/darf, /api/ir/historico
IR-002: valida cálculo de lucro via preco_medio da tabela posicao.
"""
import uuid
import pytest
from decimal import Decimal
from datetime import datetime


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _criar_transacao(db, usuario_id, ativo_id, corretora_id, tipo, data_str,
                     quantidade, preco, custos=Decimal('0')):
    from app.models.transacao import Transacao, TipoTransacao
    qtd = Decimal(str(quantidade))
    preco_d = Decimal(str(preco))
    valor_total = qtd * preco_d
    if tipo == 'compra':
        valor_liquido = valor_total + custos
    else:
        valor_liquido = valor_total - custos

    t = Transacao(
        usuario_id=usuario_id,
        ativo_id=ativo_id,
        corretora_id=corretora_id,
        tipo=TipoTransacao(tipo),
        data_transacao=datetime.fromisoformat(data_str),
        quantidade=qtd,
        preco_unitario=preco_d,
        valor_total=valor_total,
        taxa_corretagem=Decimal('0'),
        taxa_liquidacao=Decimal('0'),
        emolumentos=Decimal('0'),
        imposto=Decimal('0'),
        outros_custos=Decimal('0'),
        custos_totais=custos,
        valor_liquido=valor_liquido,
    )
    db.session.add(t)
    db.session.flush()
    return t


# ---------------------------------------------------------------------------
# Fixture: cenário com transações no mês 2025-03
# ---------------------------------------------------------------------------

@pytest.fixture
def cenario_ir(app, auth_client, ativo_seed):
    """
    Cria corretora + compra + venda vinculadas ao usuário do auth_client.
    Venda total: R$5.000 (abaixo de R$20k) → swing trade isento.
    """
    import uuid as uuid_lib
    from flask_jwt_extended import decode_token
    from app.database import db
    from app.models.corretora import Corretora, TipoCorretora
    from app.models.transacao import Transacao
    from app.models.posicao import Posicao

    # Descobrir o usuario_id a partir do token do auth_client
    token = auth_client._auth_headers['Authorization'].split(' ')[1]
    with app.app_context():
        decoded = decode_token(token)
    usuario_id = decoded['sub']

    # Criar corretora vinculada ao mesmo usuário
    suffix = str(uuid_lib.uuid4())[:8]
    corretora = Corretora(
        nome=f'XP Teste {suffix}',
        tipo=TipoCorretora.CORRETORA,
        pais='BR',
        usuario_id=usuario_id,
    )
    db.session.add(corretora)
    db.session.flush()

    compra = _criar_transacao(
        db, usuario_id, ativo_seed.id, corretora.id,
        'compra', '2025-03-10T10:00:00', 100, 30.00,
    )
    venda = _criar_transacao(
        db, usuario_id, ativo_seed.id, corretora.id,
        'venda', '2025-03-20T14:00:00', 100, 50.00,
    )

    # Criar posição com preco_medio = 30.00 (preço da compra) — IR-002
    posicao = Posicao(
        usuario_id=usuario_id,
        ativo_id=ativo_seed.id,
        corretora_id=corretora.id,
        quantidade=Decimal('0'),
        preco_medio=Decimal('30.00'),
        custo_total=Decimal('0'),
        taxas_acumuladas=Decimal('0'),
        impostos_acumulados=Decimal('0'),
        lucro_prejuizo_realizado=Decimal('2000.00'),
    )
    db.session.add(posicao)
    db.session.commit()

    yield {
        'compra': compra,
        'venda': venda,
        'mes': '2025-03',
        'usuario_id': str(usuario_id),
        'corretora_nome': corretora.nome,
        'posicao_id': posicao.id,
    }

    Transacao.query.filter_by(id=compra.id).delete()
    Transacao.query.filter_by(id=venda.id).delete()
    Posicao.query.filter_by(id=posicao.id).delete()
    Corretora.query.filter_by(id=corretora.id).delete()
    db.session.commit()


# ===========================================================================
# GET /api/ir/apuracao
# ===========================================================================
class TestApuracao:

    def test_apuracao_sem_token_retorna_401(self, client):
        rv = client.get('/api/ir/apuracao?mes=2025-03')
        assert rv.status_code == 401

    def test_apuracao_sem_parametro_mes_retorna_400(self, auth_client):
        rv = auth_client.get('/api/ir/apuracao', headers=auth_client._auth_headers)
        assert rv.status_code == 400
        assert rv.get_json()['success'] is False

    def test_apuracao_mes_invalido_retorna_422(self, auth_client):
        rv = auth_client.get('/api/ir/apuracao?mes=2025-13', headers=auth_client._auth_headers)
        assert rv.status_code == 422

    def test_apuracao_mes_formato_errado_retorna_422(self, auth_client):
        rv = auth_client.get('/api/ir/apuracao?mes=03-2025', headers=auth_client._auth_headers)
        assert rv.status_code == 422

    def test_apuracao_mes_vazio_retorna_envelope_correto(self, auth_client):
        """Mês sem transações retorna IR 0 e estrutura válida."""
        rv = auth_client.get('/api/ir/apuracao?mes=2000-01', headers=auth_client._auth_headers)
        assert rv.status_code == 200
        data = rv.get_json()
        assert data['success'] is True
        assert data['data']['ir_total'] == 0.0
        assert 'categorias' in data['data']
        assert 'darf' in data['data']

    def test_apuracao_envelope_tem_todas_categorias(self, auth_client):
        """Estrutura de resposta contém todas as 4 categorias."""
        rv = auth_client.get('/api/ir/apuracao?mes=2000-01', headers=auth_client._auth_headers)
        categorias = rv.get_json()['data']['categorias']
        assert 'swing_acoes' in categorias
        assert 'day_trade' in categorias
        assert 'fiis' in categorias
        assert 'exterior' in categorias

    def test_apuracao_com_venda_abaixo_isencao(self, auth_client, cenario_ir):
        """Venda de R$5.000 (< R$20k) → isento = True, ir_total swing = 0."""
        rv = auth_client.get(
            f'/api/ir/apuracao?mes={cenario_ir["mes"]}',
            headers=auth_client._auth_headers,
        )
        assert rv.status_code == 200
        data = rv.get_json()['data']
        swing = data['categorias']['swing_acoes']
        assert swing['isento'] is True
        assert swing['ir_devido'] == 0.0

    def test_apuracao_retorna_mes_correto(self, auth_client, cenario_ir):
        rv = auth_client.get(
            f'/api/ir/apuracao?mes={cenario_ir["mes"]}',
            headers=auth_client._auth_headers,
        )
        assert rv.get_json()['data']['mes'] == cenario_ir['mes']

    def test_apuracao_inclui_por_corretora(self, auth_client, cenario_ir):
        """Resposta deve incluir breakdown por_corretora com nome e total_vendas."""
        rv = auth_client.get(
            f'/api/ir/apuracao?mes={cenario_ir["mes"]}',
            headers=auth_client._auth_headers,
        )
        assert rv.status_code == 200
        data = rv.get_json()['data']
        assert 'por_corretora' in data
        assert isinstance(data['por_corretora'], list)
        assert len(data['por_corretora']) >= 1
        corretora = data['por_corretora'][0]
        assert 'corretora_id' in corretora
        assert 'corretora_nome' in corretora
        assert 'total_vendas' in corretora
        assert 'operacoes' in corretora

    def test_apuracao_mes_vazio_por_corretora_lista_vazia(self, auth_client):
        """Mês sem transações retorna por_corretora como lista vazia."""
        rv = auth_client.get('/api/ir/apuracao?mes=2000-01', headers=auth_client._auth_headers)
        assert rv.get_json()['data']['por_corretora'] == []

    # --- IR-002: Testes de cálculo via preço médio (posicao) ---

    def test_lucro_calculado_via_preco_medio_posicao(self, auth_client, cenario_ir):
        """IR-002: Lucro = valor_venda - (PM × qtd). PM=30, venda 100×50 → lucro bruto R$2000."""
        rv = auth_client.get(
            f'/api/ir/apuracao?mes={cenario_ir["mes"]}',
            headers=auth_client._auth_headers,
        )
        assert rv.status_code == 200
        swing = rv.get_json()['data']['categorias']['swing_acoes']
        # 100 × 50 = 5000 (receita) - 100 × 30 = 3000 (custo PM) = 2000 lucro bruto
        assert swing['lucro_liquido'] == 2000.0

    def test_alerta_posicao_vazia_quando_sem_pm(self, auth_client):
        """IR-002: Se tabela posicao vazia, alertas deve conter aviso."""
        rv = auth_client.get('/api/ir/apuracao?mes=2000-01', headers=auth_client._auth_headers)
        alertas = rv.get_json()['data']['alertas']
        assert any('posicao vazia' in a.lower() for a in alertas)

    # --- IR-003: Testes de compensação de prejuízo acumulado ---

    def test_apuracao_retorna_campos_prejuizo(self, auth_client, cenario_ir):
        """IR-003: Resposta deve conter prejuizo_compensado e prejuizo_acumulado."""
        rv = auth_client.get(
            f'/api/ir/apuracao?mes={cenario_ir["mes"]}',
            headers=auth_client._auth_headers,
        )
        assert rv.status_code == 200
        swing = rv.get_json()['data']['categorias']['swing_acoes']
        assert 'prejuizo_compensado' in swing
        assert 'prejuizo_acumulado' in swing

    def test_prejuizo_acumulado_quando_sem_historico(self, auth_client, cenario_ir):
        """IR-003: Sem prejuízo anterior, prejuizo_acumulado = 0."""
        rv = auth_client.get(
            f'/api/ir/apuracao?mes={cenario_ir["mes"]}',
            headers=auth_client._auth_headers,
        )
        swing = rv.get_json()['data']['categorias']['swing_acoes']
        assert swing['prejuizo_acumulado'] == 0.0
        assert swing['prejuizo_compensado'] == 0.0

    def test_compensacao_prejuizo_entre_meses(self, app, auth_client, cenario_ir):
        """IR-003: Prejuízo de mês anterior é compensado contra lucro do mês atual."""
        from app.database import db
        from app.models.saldo_prejuizo import SaldoPrejuizo

        # Inserir prejuízo anterior de R$500 em swing_acoes para 2025-02
        saldo = SaldoPrejuizo(
            usuario_id=cenario_ir['usuario_id'],
            categoria='swing_acoes',
            ano_mes='2025-02',
            saldo=Decimal('500.00'),
        )
        db.session.add(saldo)
        db.session.commit()

        try:
            rv = auth_client.get(
                f'/api/ir/apuracao?mes={cenario_ir["mes"]}',
                headers=auth_client._auth_headers,
            )
            assert rv.status_code == 200
            swing = rv.get_json()['data']['categorias']['swing_acoes']
            # Lucro bruto era R$2000; com compensação de R$500 → lucro líquido R$1500
            assert swing['prejuizo_compensado'] == 500.0
            assert swing['lucro_liquido'] == 1500.0
            # Prejuízo acumulado após compensação = 0 (todo compensado)
            assert swing['prejuizo_acumulado'] == 0.0
        finally:
            SaldoPrejuizo.query.filter_by(
                usuario_id=cenario_ir['usuario_id'],
                categoria='swing_acoes',
            ).delete()
            db.session.commit()

    def test_compensacao_parcial_preserva_saldo(self, app, auth_client, cenario_ir):
        """IR-003: Se prejuízo > lucro (isento), saldo não deve crescer por lucro isento."""
        from app.database import db
        from app.models.saldo_prejuizo import SaldoPrejuizo

        # Prejuízo anterior de R$5000 — lucro de R$2000 (isento, vendas < 20k)
        saldo = SaldoPrejuizo(
            usuario_id=cenario_ir['usuario_id'],
            categoria='swing_acoes',
            ano_mes='2025-02',
            saldo=Decimal('5000.00'),
        )
        db.session.add(saldo)
        db.session.commit()

        try:
            rv = auth_client.get(
                f'/api/ir/apuracao?mes={cenario_ir["mes"]}',
                headers=auth_client._auth_headers,
            )
            assert rv.status_code == 200
            swing = rv.get_json()['data']['categorias']['swing_acoes']
            # Houve compensação parcial: R$2000 de lucro compensa parte do R$5000
            assert swing['prejuizo_compensado'] == 2000.0
            # Saldo restante: 5000 - 2000 = 3000
            assert swing['prejuizo_acumulado'] == 3000.0
            # IR = 0 porque swing é isento (vendas < 20k)
            assert swing['ir_devido'] == 0.0
        finally:
            SaldoPrejuizo.query.filter_by(
                usuario_id=cenario_ir['usuario_id'],
                categoria='swing_acoes',
            ).delete()
            db.session.commit()

    def test_mes_vazio_preserva_saldo_anterior(self, auth_client):
        """IR-003: Mês sem transações preserva saldo = 0 (sem prejuízo e sem lucro)."""
        rv = auth_client.get('/api/ir/apuracao?mes=2000-01', headers=auth_client._auth_headers)
        swing = rv.get_json()['data']['categorias']['swing_acoes']
        assert swing['prejuizo_acumulado'] == 0.0
        assert swing['prejuizo_compensado'] == 0.0


# ===========================================================================
# GET /api/ir/darf
# ===========================================================================
class TestDarf:

    def test_darf_sem_token_retorna_401(self, client):
        rv = client.get('/api/ir/darf?mes=2025-03')
        assert rv.status_code == 401

    def test_darf_sem_parametro_retorna_400(self, auth_client):
        rv = auth_client.get('/api/ir/darf', headers=auth_client._auth_headers)
        assert rv.status_code == 400

    def test_darf_mes_vazio_retorna_lista_vazia(self, auth_client):
        """Sem lucro tributável → nenhum DARF."""
        rv = auth_client.get('/api/ir/darf?mes=2000-02', headers=auth_client._auth_headers)
        assert rv.status_code == 200
        data = rv.get_json()['data']
        assert data['darfs'] == []
        assert data['ir_total'] == 0.0

    def test_darf_retorna_mes_correto(self, auth_client):
        rv = auth_client.get('/api/ir/darf?mes=2025-06', headers=auth_client._auth_headers)
        assert rv.status_code == 200
        assert rv.get_json()['data']['mes'] == '2025-06'

    def test_darf_envelope_padrao(self, auth_client):
        rv = auth_client.get('/api/ir/darf?mes=2025-06', headers=auth_client._auth_headers)
        data = rv.get_json()
        assert 'success' in data
        assert 'data' in data


# ===========================================================================
# GET /api/ir/historico
# ===========================================================================
class TestHistorico:

    def test_historico_sem_token_retorna_401(self, client):
        rv = client.get('/api/ir/historico?ano=2025')
        assert rv.status_code == 401

    def test_historico_sem_parametro_retorna_400(self, auth_client):
        rv = auth_client.get('/api/ir/historico', headers=auth_client._auth_headers)
        assert rv.status_code == 400

    def test_historico_ano_invalido_retorna_400(self, auth_client):
        rv = auth_client.get('/api/ir/historico?ano=abc', headers=auth_client._auth_headers)
        assert rv.status_code == 400

    def test_historico_retorna_12_meses(self, auth_client):
        """Histórico anual sempre retorna 12 entradas."""
        rv = auth_client.get('/api/ir/historico?ano=2024', headers=auth_client._auth_headers)
        assert rv.status_code == 200
        data = rv.get_json()['data']
        assert data['ano'] == 2024
        assert len(data['meses']) == 12

    def test_historico_meses_tem_campos_obrigatorios(self, auth_client):
        rv = auth_client.get('/api/ir/historico?ano=2024', headers=auth_client._auth_headers)
        meses = rv.get_json()['data']['meses']
        for m in meses:
            assert 'mes' in m
            assert 'ir_total' in m
            assert 'operacoes' in m

    def test_historico_meses_formato_yyyy_mm(self, auth_client):
        rv = auth_client.get('/api/ir/historico?ano=2024', headers=auth_client._auth_headers)
        meses = rv.get_json()['data']['meses']
        for i, m in enumerate(meses):
            assert m['mes'] == f'2024-{(i+1):02d}'


@pytest.fixture
def cenario_proventos(app, auth_client, ativo_seed):
    """
    IR-004: Cria transações de JCP, dividendo BR, dividendo US e aluguel
    para o mês 2025-06. O campo `imposto` simula o IR retido na fonte.
    """
    import uuid as uuid_lib
    from flask_jwt_extended import decode_token
    from app.database import db
    from app.models.corretora import Corretora, TipoCorretora
    from app.models.transacao import Transacao, TipoTransacao
    from app.models.ativo import Ativo, TipoAtivo

    token = auth_client._auth_headers['Authorization'].split(' ')[1]
    with app.app_context():
        decoded = decode_token(token)
    usuario_id = decoded['sub']

    suffix = str(uuid_lib.uuid4())[:8]
    corretora = Corretora(
        nome=f'Inter Teste {suffix}',
        tipo=TipoCorretora.CORRETORA,
        pais='BR',
        usuario_id=usuario_id,
    )
    db.session.add(corretora)
    db.session.flush()

    # Ativo BR (ACAO já existe em ativo_seed)
    ativo_br = ativo_seed  # tipo ACAO, país BR

    # Ativo US (STOCK) — criar separado
    from app.models.ativo import ClasseAtivo
    ativo_us = Ativo(
        ticker=f'AAPL{suffix}',
        nome='Apple Inc Test',
        tipo=TipoAtivo.STOCK,
        classe=ClasseAtivo.RENDA_VARIAVEL,
        mercado='US',
        moeda='USD',
        ativo=True,
    )
    db.session.add(ativo_us)
    db.session.flush()

    def _criar_provento(tipo_str, ativo_id, valor, imposto_retido):
        qtd = Decimal('1')
        val = Decimal(str(valor))
        imp = Decimal(str(imposto_retido))
        t = Transacao(
            usuario_id=usuario_id,
            ativo_id=ativo_id,
            corretora_id=corretora.id,
            tipo=TipoTransacao(tipo_str),
            data_transacao=__import__('datetime').datetime(2025, 6, 15, 10, 0),
            quantidade=qtd,
            preco_unitario=val,
            valor_total=val,
            taxa_corretagem=Decimal('0'),
            taxa_liquidacao=Decimal('0'),
            emolumentos=Decimal('0'),
            imposto=imp,
            outros_custos=Decimal('0'),
            custos_totais=imp,
            valor_liquido=val - imp,
        )
        db.session.add(t)
        db.session.flush()
        return t

    t_dividendo_br = _criar_provento('dividendo', ativo_br.id, 1000.00, 0.00)
    t_jcp          = _criar_provento('jcp',        ativo_br.id, 2000.00, 300.00)  # 15% retido
    t_dividendo_us = _criar_provento('dividendo',  ativo_us.id, 500.00,  150.00)  # 30% IRS retido
    t_aluguel      = _criar_provento('aluguel',    ativo_br.id, 400.00,  60.00)   # 15% retido

    db.session.commit()

    yield {
        'mes': '2025-06',
        'usuario_id': str(usuario_id),
        't_dividendo_br': t_dividendo_br,
        't_jcp': t_jcp,
        't_dividendo_us': t_dividendo_us,
        't_aluguel': t_aluguel,
        'ativo_us_id': ativo_us.id,
        'corretora_id': corretora.id,
    }

    for tid in [t_dividendo_br.id, t_jcp.id, t_dividendo_us.id, t_aluguel.id]:
        Transacao.query.filter_by(id=tid).delete()
    Ativo.query.filter_by(id=ativo_us.id).delete()
    Corretora.query.filter_by(id=corretora.id).delete()
    db.session.commit()


class TestProventos:
    """IR-004: Proventos tributáveis — JCP, dividendos, aluguel, withholding US."""

    def test_apuracao_retorna_secao_proventos(self, auth_client, cenario_proventos):
        """Resposta de apuração deve conter a seção 'proventos'."""
        rv = auth_client.get('/api/ir/apuracao?mes=2025-06', headers=auth_client._auth_headers)
        assert rv.status_code == 200
        data = rv.get_json()['data']
        assert 'proventos' in data

    def test_proventos_tem_campos_obrigatorios(self, auth_client, cenario_proventos):
        """Seção proventos deve conter subseções e campo ir_retido_total."""
        rv = auth_client.get('/api/ir/apuracao?mes=2025-06', headers=auth_client._auth_headers)
        proventos = rv.get_json()['data']['proventos']
        for campo in ('dividendos_br', 'jcp', 'dividendos_us', 'aluguel', 'ir_retido_total'):
            assert campo in proventos

    def test_dividendo_br_isento(self, auth_client, cenario_proventos):
        """Dividendos BR devem ser isentos (alíquota 0%, ir_retido 0)."""
        rv = auth_client.get('/api/ir/apuracao?mes=2025-06', headers=auth_client._auth_headers)
        div_br = rv.get_json()['data']['proventos']['dividendos_br']
        assert div_br['isento'] is True
        assert div_br['aliquota'] == 0.0
        assert div_br['valor_bruto'] == 1000.0

    def test_jcp_aliquota_e_ir_retido(self, auth_client, cenario_proventos):
        """JCP deve registrar 15% de alíquota e o IR retido da transação."""
        rv = auth_client.get('/api/ir/apuracao?mes=2025-06', headers=auth_client._auth_headers)
        jcp = rv.get_json()['data']['proventos']['jcp']
        assert jcp['aliquota'] == 15.0
        assert jcp['valor_bruto'] == 2000.0
        assert jcp['ir_retido'] == 300.0
        assert jcp['isento'] is False


class TestRegrasFiscais:
    """IR-007: Alíquotas dinâmicas via tabela regra_fiscal."""

    def test_aliquota_swing_carregada_do_banco(self, auth_client, cenario_ir):
        """Alíquota de swing trade deve ser 15.0 (carregada da tabela regra_fiscal)."""
        rv = auth_client.get('/api/ir/apuracao?mes=2025-03', headers=auth_client._auth_headers)
        assert rv.status_code == 200
        swing = rv.get_json()['data']['categorias']['swing_acoes']
        assert swing['aliquota'] == 15.0

    def test_fallback_quando_regra_fiscal_vazia(self, app, auth_client, cenario_ir):
        """Se regra_fiscal estiver vazia, deve usar constantes hardcoded sem erro."""
        from app.database import db
        from app.models.regra_fiscal import RegraFiscal

        with app.app_context():
            regras = RegraFiscal.query.all()
            ids_backup = [(r.id, r.ativa) for r in regras]
            # Desativa todas as regras temporariamente
            for r in regras:
                r.ativa = False
            db.session.commit()

        try:
            rv = auth_client.get('/api/ir/apuracao?mes=2025-03', headers=auth_client._auth_headers)
            assert rv.status_code == 200
            swing = rv.get_json()['data']['categorias']['swing_acoes']
            # Fallback: deve retornar 15.0 (hardcoded)
            assert swing['aliquota'] == 15.0
        finally:
            with app.app_context():
                for r_id, r_ativa in ids_backup:
                    r = RegraFiscal.query.get(r_id)
                    if r:
                        r.ativa = r_ativa
                db.session.commit()


@pytest.fixture
def cenario_proventos_2026(app, auth_client, ativo_seed):
    """
    IR-009: Cria transações de JCP e dividendo BR em 2026-03.
    - JCP R$1.000 → 17,5% retido = R$175
    - Dividendo BR R$60.000 (acima do limite de R$50k) → 10% esperado sobre todo o valor = R$6.000
    """
    import uuid as uuid_lib
    from flask_jwt_extended import decode_token
    from app.database import db
    from app.models.corretora import Corretora, TipoCorretora
    from app.models.transacao import Transacao, TipoTransacao

    token = auth_client._auth_headers['Authorization'].split(' ')[1]
    with app.app_context():
        decoded = decode_token(token)
    usuario_id = decoded['sub']

    suffix = str(uuid_lib.uuid4())[:8]
    corretora = Corretora(
        nome=f'BTG 2026 {suffix}',
        tipo=TipoCorretora.CORRETORA,
        pais='BR',
        usuario_id=usuario_id,
    )
    db.session.add(corretora)
    db.session.flush()

    def _criar_provento_2026(tipo_str, ativo_id, valor, imposto_retido):
        val = Decimal(str(valor))
        imp = Decimal(str(imposto_retido))
        t = Transacao(
            usuario_id=usuario_id,
            ativo_id=ativo_id,
            corretora_id=corretora.id,
            tipo=TipoTransacao(tipo_str),
            data_transacao=__import__('datetime').datetime(2026, 3, 15, 10, 0),
            quantidade=Decimal('1'),
            preco_unitario=val,
            valor_total=val,
            taxa_corretagem=Decimal('0'),
            taxa_liquidacao=Decimal('0'),
            emolumentos=Decimal('0'),
            imposto=imp,
            outros_custos=Decimal('0'),
            custos_totais=imp,
            valor_liquido=val - imp,
        )
        db.session.add(t)
        db.session.flush()
        return t

    t_jcp      = _criar_provento_2026('jcp',       ativo_seed.id, 1000.00, 175.00)   # 17,5% retido
    t_div_br   = _criar_provento_2026('dividendo', ativo_seed.id, 60000.00, 6000.00)  # 10% retido (>R$50k)

    db.session.commit()

    yield {
        'mes': '2026-03',
        't_jcp': t_jcp,
        't_div_br': t_div_br,
        'corretora_id': corretora.id,
    }

    for tid in [t_jcp.id, t_div_br.id]:
        Transacao.query.filter_by(id=tid).delete()
    Corretora.query.filter_by(id=corretora.id).delete()
    db.session.commit()


class TestRegrasFiscais2026:
    """IR-009: Regras fiscais 2026 — Lei 15.270/2025 e PLP 128/2025."""

    def test_jcp_aliquota_17_5_em_2026(self, auth_client, cenario_proventos_2026):
        """JCP em 2026 deve usar alíquota 17,5% (PLP 128/2025)."""
        rv = auth_client.get('/api/ir/apuracao?mes=2026-03', headers=auth_client._auth_headers)
        assert rv.status_code == 200
        jcp = rv.get_json()['data']['proventos']['jcp']
        assert jcp['aliquota'] == 17.5
        assert jcp['ir_retido'] == 175.0

    def test_dividendo_br_tributado_acima_50k_em_2026(self, auth_client, cenario_proventos_2026):
        """Dividendo BR de R$60k em 2026: deve ser tributado (isento=False, regime='2026+')."""
        rv = auth_client.get('/api/ir/apuracao?mes=2026-03', headers=auth_client._auth_headers)
        div_br = rv.get_json()['data']['proventos']['dividendos_br']
        assert div_br['isento'] is False
        assert div_br['regime'] == '2026+'
        assert div_br['ir_esperado'] == 6000.0
        assert div_br['limite_isencao_por_cnpj'] == 50000.0

    def test_dividendo_br_isento_abaixo_50k_em_2026(self, app, auth_client, ativo_seed):
        """Dividendo BR de R$30k em 2026: deve ser isento (abaixo do limite)."""
        import uuid as uuid_lib
        from flask_jwt_extended import decode_token
        from app.database import db
        from app.models.corretora import Corretora, TipoCorretora
        from app.models.transacao import Transacao, TipoTransacao

        token = auth_client._auth_headers['Authorization'].split(' ')[1]
        with app.app_context():
            decoded = decode_token(token)
        usuario_id = decoded['sub']

        suffix = str(uuid_lib.uuid4())[:8]
        corretora = Corretora(
            nome=f'Rico 2026 {suffix}',
            tipo=TipoCorretora.CORRETORA,
            pais='BR',
            usuario_id=usuario_id,
        )
        db.session.add(corretora)
        db.session.flush()

        val = Decimal('30000.00')
        t = Transacao(
            usuario_id=usuario_id,
            ativo_id=ativo_seed.id,
            corretora_id=corretora.id,
            tipo=TipoTransacao.DIVIDENDO,
            data_transacao=__import__('datetime').datetime(2026, 3, 20, 10, 0),
            quantidade=Decimal('1'),
            preco_unitario=val,
            valor_total=val,
            taxa_corretagem=Decimal('0'),
            taxa_liquidacao=Decimal('0'),
            emolumentos=Decimal('0'),
            imposto=Decimal('0'),
            outros_custos=Decimal('0'),
            custos_totais=Decimal('0'),
            valor_liquido=val,
        )
        db.session.add(t)
        db.session.commit()

        try:
            rv = auth_client.get('/api/ir/apuracao?mes=2026-03', headers=auth_client._auth_headers)
            div_br = rv.get_json()['data']['proventos']['dividendos_br']
            assert div_br['isento'] is True
            assert div_br['ir_esperado'] == 0.0
        finally:
            Transacao.query.filter_by(id=t.id).delete()
            Corretora.query.filter_by(id=corretora.id).delete()
            db.session.commit()
