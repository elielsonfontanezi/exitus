#!/usr/bin/env python3
"""Verifica cobertura mínima do cenário test_menu_full (SEED-MENU-001)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app
from app.database import db
from app.models.ativo import Ativo, TipoAtivo
from app.models.fonte_dados import FonteDados
from app.models.meta_alocacao import MetaAlocacao
from app.models.taxa_cambio import TaxaCambio
from app.models.historico_preco import HistoricoPreco
from app.models.saldo_prejuizo import SaldoPrejuizo
from app.models.calendario_dividendo import CalendarioDividendo
from app.models.projecao_renda import ProjecaoRenda
from app.models.regra_fiscal import RegraFiscal
from app.models.portfolio import Portfolio
from app.models.transacao import Transacao, TipoTransacao
from app.models.usuario import Usuario

REQUIRED_TIPOS = {
    TipoAtivo.ACAO, TipoAtivo.FII, TipoAtivo.UNIT, TipoAtivo.CDB, TipoAtivo.LCI_LCA,
    TipoAtivo.TESOURO_DIRETO, TipoAtivo.DEBENTURE, TipoAtivo.STOCK, TipoAtivo.REIT,
    TipoAtivo.BOND, TipoAtivo.ETF, TipoAtivo.STOCK_INTL, TipoAtivo.ETF_INTL,
    TipoAtivo.CRIPTO,
}

REQUIRED_TICKERS = [
    'BOVA11', 'SMAL11', 'LCI110XP', 'AGG', 'BTC', 'ETH',
]


def verify():
    app = create_app()
    errors = []
    warnings = []

    with app.app_context():
        tipos_presentes = {a.tipo for a in Ativo.query.filter_by(ativo=True).all()}
        missing_tipos = REQUIRED_TIPOS - tipos_presentes
        if missing_tipos:
            errors.append(f'Tipos ativo faltando: {[t.name for t in missing_tipos]}')

        tickers = {a.ticker for a in Ativo.query.all()}
        for t in REQUIRED_TICKERS:
            if t not in tickers:
                errors.append(f'Ticker obrigatório ausente: {t}')

        compra_tickers = {
            tx.ativo.ticker for tx in Transacao.query.join(Ativo).filter(
                Transacao.tipo == TipoTransacao.COMPRA
            ).all() if tx.ativo
        }
        for t in REQUIRED_TICKERS:
            if t in tickers and t not in compra_tickers:
                warnings.append(f'Sem COMPRA para: {t}')

        checks = [
            (FonteDados.query.count(), 1, 'fontes_dados'),
            (MetaAlocacao.query.count(), 1, 'meta_alocacao'),
            (TaxaCambio.query.count(), 1, 'taxas_cambio'),
            (HistoricoPreco.query.count(), 12, 'historico_preco'),
            (SaldoPrejuizo.query.count(), 1, 'saldo_prejuizo'),
            (CalendarioDividendo.query.count(), 1, 'calendario_dividendo'),
            (ProjecaoRenda.query.count(), 1, 'projecoes_renda'),
            (RegraFiscal.query.count(), 1, 'regras_fiscais'),
            (Transacao.query.count(), 50, 'transacoes'),
        ]
        for count, minimum, label in checks:
            if count < minimum:
                errors.append(f'{label}: esperado >= {minimum}, encontrado {count}')

        e2e_user = Usuario.query.filter_by(username='e2e_user').first()
        if e2e_user:
            ativos_count = Portfolio.query.filter_by(usuario_id=e2e_user.id, ativo=True).count()
            if ativos_count > 4:
                errors.append(
                    f'portfolios ativos e2e_user: esperado <= 4, encontrado {ativos_count}'
                )

    print('=== verify_menu_seed ===')
    if warnings:
        for w in warnings:
            print(f'⚠️  {w}')
    if errors:
        for e in errors:
            print(f'❌ {e}')
        print(f'FALHOU ({len(errors)} erros)')
        return 1

    print('✅ Cenário test_menu_full OK')
    return 0


if __name__ == '__main__':
    sys.exit(verify())
