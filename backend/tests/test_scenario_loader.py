# -*- coding: utf-8 -*-
"""Testes do cenário test_menu_full e extensões do ScenarioLoader (SEED-MENU-001)."""
import json
from pathlib import Path

import pytest

from app.models.ativo import Ativo, TipoAtivo
from app.models.calendario_dividendo import CalendarioDividendo
from app.models.fonte_dados import FonteDados
from app.models.historico_preco import HistoricoPreco
from app.models.meta_alocacao import MetaAlocacao
from app.models.projecao_renda import ProjecaoRenda
from app.models.regra_fiscal import RegraFiscal
from app.models.saldo_prejuizo import SaldoPrejuizo
from app.models.taxa_cambio import TaxaCambio
from app.models.transacao import Transacao, TipoTransacao
from load_scenario import ScenarioLoader

SCENARIOS_DIR = Path(__file__).resolve().parent.parent / 'seed_data' / 'scenarios'
MENU_FULL_JSON = SCENARIOS_DIR / 'test_menu_full.json'

REQUIRED_TIPOS = {
    'ACAO', 'FII', 'UNIT', 'CDB', 'LCI_LCA', 'TESOURO_DIRETO', 'DEBENTURE',
    'STOCK', 'REIT', 'BOND', 'ETF', 'STOCK_INTL', 'ETF_INTL', 'CRIPTO',
}

REQUIRED_BLOCKS = [
    'calendario_dividendo', 'projecoes_renda', 'regras_fiscais',
    'meta_alocacao', 'fontes_dados', 'taxas_cambio', 'historico_preco', 'saldo_prejuizo',
]


@pytest.fixture
def menu_full_data():
    assert MENU_FULL_JSON.exists(), f'Arquivo ausente: {MENU_FULL_JSON}'
    with open(MENU_FULL_JSON, encoding='utf-8') as f:
        return json.load(f)


class TestMenuFullJsonStructure:
    def test_required_blocks_present(self, menu_full_data):
        for block in REQUIRED_BLOCKS:
            assert block in menu_full_data, f'Bloco ausente: {block}'
            assert len(menu_full_data[block]) > 0, f'Bloco vazio: {block}'

    def test_tipo_ativo_coverage(self, menu_full_data):
        tipos = {a['tipo'] for a in menu_full_data.get('ativos', [])}
        missing = REQUIRED_TIPOS - tipos
        assert not missing, f'Tipos faltando no JSON: {sorted(missing)}'

    def test_required_tickers_with_compra(self, menu_full_data):
        tickers = {a['ticker'] for a in menu_full_data['ativos']}
        for t in ('BOVA11', 'SMAL11', 'BTC', 'ETH', 'AGG', 'LCI110XP'):
            assert t in tickers, f'Ticker ausente: {t}'
        compras = {
            tx['ativo'] for tx in menu_full_data['transacoes']
            if tx.get('tipo') == 'COMPRA'
        }
        for t in ('BOVA11', 'BTC'):
            assert t in compras, f'Sem COMPRA para {t}'


@pytest.mark.parametrize('scenario', ['test_menu_full'])
def test_menu_full_loader_integration(app, scenario):
    """Carrega test_menu_full via ScenarioLoader e valida integridade mínima."""
    loader = ScenarioLoader(app=app)
    loader.load_scenario(scenario)
    assert loader.seed_all() is True

    tipos = {a.tipo.name for a in Ativo.query.filter_by(ativo=True).all()}
    assert REQUIRED_TIPOS <= tipos

    assert FonteDados.query.count() >= 1
    assert MetaAlocacao.query.count() >= 1
    assert TaxaCambio.query.count() >= 1
    assert HistoricoPreco.query.count() >= 12
    assert SaldoPrejuizo.query.count() >= 1
    assert CalendarioDividendo.query.count() >= 1
    assert ProjecaoRenda.query.count() >= 1
    assert RegraFiscal.query.count() >= 1
    assert Transacao.query.filter_by(tipo=TipoTransacao.COMPRA).count() >= 30
