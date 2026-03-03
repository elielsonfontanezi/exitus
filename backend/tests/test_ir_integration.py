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
