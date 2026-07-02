#!/usr/bin/env python3
"""Gera test_menu_full.json a partir de test_full + extensões SEED-MENU-001."""
import json
from copy import deepcopy
from datetime import date, timedelta
from pathlib import Path

SCENARIOS = Path(__file__).resolve().parent.parent / 'seed_data' / 'scenarios'


def _monthly_prices(ticker, base_price, months=12, start_year=2024, start_month=1):
    rows = []
    y, m = start_year, start_month
    price = float(base_price)
    for i in range(months):
        d = date(y, m, 28)
        drift = 1 + (i % 5 - 2) * 0.01
        close = round(price * drift, 2)
        rows.append({
            'ativo_ticker': ticker,
            'data': d.isoformat(),
            'preco_abertura': round(close * 0.99, 2),
            'preco_fechamento': close,
            'preco_minimo': round(close * 0.98, 2),
            'preco_maximo': round(close * 1.02, 2),
            'volume': 500000 + i * 10000,
        })
        m += 1
        if m > 12:
            m = 1
            y += 1
        price = close
    return rows


def build():
    with open(SCENARIOS / 'test_full.json', encoding='utf-8') as f:
        data = deepcopy(json.load(f))

    with open(SCENARIOS / 'test_e2e.json', encoding='utf-8') as f:
        e2e = json.load(f)

    data['version'] = '3.0'
    data['description'] = (
        'SEED-MENU-001 — massa completa menu 43 telas: test_full + tipos faltantes '
        '+ blocos auxiliares (calendário, projeções, regras, câmbio, histórico)'
    )
    data['timestamp'] = '2026-07-02T00:00:00Z'

    existing_tickers = {a['ticker'] for a in data['ativos']}

    extra_ativos = [
        {'ticker': 'BOVA11', 'nome': 'iShares Ibovespa ETF', 'tipo': 'ETF', 'classe': 'RENDA_VARIAVEL',
         'mercado': 'BR', 'moeda': 'BRL', 'preco_atual': 125.40, 'preco_teto': 140.00,
         'dividend_yield': 2.1, 'observacoes': 'ETF Ibovespa BR', 'ativo': True},
        {'ticker': 'SMAL11', 'nome': 'iShares Small Cap ETF', 'tipo': 'ETF', 'classe': 'RENDA_VARIAVEL',
         'mercado': 'BR', 'moeda': 'BRL', 'preco_atual': 98.70, 'preco_teto': 115.00,
         'dividend_yield': 1.8, 'observacoes': 'ETF Small Cap Brasil', 'ativo': True},
        {'ticker': 'LCI110XP', 'nome': 'XP LCI 110% CDI', 'tipo': 'LCI_LCA', 'classe': 'RENDA_FIXA',
         'mercado': 'BR', 'moeda': 'BRL', 'preco_atual': 1000.00,
         'observacoes': 'LCI isenta IR, 110% CDI', 'ativo': True},
        {'ticker': 'LCA105IT', 'nome': 'Itaú LCA 105% CDI', 'tipo': 'LCI_LCA', 'classe': 'RENDA_FIXA',
         'mercado': 'BR', 'moeda': 'BRL', 'preco_atual': 1000.00,
         'observacoes': 'LCA isenta IR, 105% CDI', 'ativo': True},
        {'ticker': 'AGG', 'nome': 'iShares Core US Aggregate Bond ETF', 'tipo': 'BOND', 'classe': 'RENDA_FIXA',
         'mercado': 'US', 'moeda': 'USD', 'preco_atual': 102.15,
         'observacoes': 'Bond ETF US', 'ativo': True},
        {'ticker': 'TLT', 'nome': 'iShares 20+ Year Treasury Bond ETF', 'tipo': 'BOND', 'classe': 'RENDA_FIXA',
         'mercado': 'US', 'moeda': 'USD', 'preco_atual': 88.50,
         'observacoes': 'Treasury Bond ETF US', 'ativo': True},
        {'ticker': 'BTC', 'nome': 'Bitcoin', 'tipo': 'CRIPTO', 'classe': 'CRIPTO',
         'mercado': 'US', 'moeda': 'USD', 'preco_atual': 61500.00,
         'observacoes': 'Cripto BTC', 'ativo': True},
        {'ticker': 'ETH', 'nome': 'Ethereum', 'tipo': 'CRIPTO', 'classe': 'CRIPTO',
         'mercado': 'US', 'moeda': 'USD', 'preco_atual': 3200.00,
         'observacoes': 'Cripto ETH', 'ativo': True},
        {'ticker': 'SOL', 'nome': 'Solana', 'tipo': 'CRIPTO', 'classe': 'CRIPTO',
         'mercado': 'US', 'moeda': 'USD', 'preco_atual': 145.00,
         'observacoes': 'Cripto SOL', 'ativo': True},
    ]
    for a in extra_ativos:
        if a['ticker'] not in existing_tickers:
            data['ativos'].append(a)

    extra_tx = [
        {'usuario': 'e2e_user', 'ativo': 'BOVA11', 'corretora': 'XP INVESTIMENTOS', 'tipo': 'COMPRA',
         'data_transacao': '2024-03-25', 'quantidade': 40, 'preco_unitario': 120.00,
         'taxa_corretagem': 4.80, 'custos_totais': 6.00, 'observacoes': 'ETF Ibovespa BR'},
        {'usuario': 'e2e_user', 'ativo': 'SMAL11', 'corretora': 'XP INVESTIMENTOS', 'tipo': 'COMPRA',
         'data_transacao': '2024-04-10', 'quantidade': 30, 'preco_unitario': 95.00,
         'taxa_corretagem': 2.85, 'custos_totais': 4.00, 'observacoes': 'ETF Small Cap BR'},
        {'usuario': 'e2e_user', 'ativo': 'LCI110XP', 'corretora': 'XP INVESTIMENTOS', 'tipo': 'COMPRA',
         'data_transacao': '2024-05-20', 'quantidade': 10, 'preco_unitario': 1000.00,
         'taxa_corretagem': 0.00, 'custos_totais': 0.00, 'observacoes': 'LCI XP 110% CDI'},
        {'usuario': 'e2e_user', 'ativo': 'LCA105IT', 'corretora': 'ITAU CV S/A', 'tipo': 'COMPRA',
         'data_transacao': '2024-06-15', 'quantidade': 5, 'preco_unitario': 1000.00,
         'taxa_corretagem': 0.00, 'custos_totais': 0.00, 'observacoes': 'LCA Itaú 105% CDI'},
        {'usuario': 'e2e_user', 'ativo': 'AGG', 'corretora': 'AVENUE SECURITIES', 'tipo': 'COMPRA',
         'data_transacao': '2024-07-10', 'quantidade': 15, 'preco_unitario': 100.00,
         'taxa_corretagem': 1.00, 'custos_totais': 1.50, 'observacoes': 'Bond ETF US'},
        {'usuario': 'e2e_user', 'ativo': 'TLT', 'corretora': 'AVENUE SECURITIES', 'tipo': 'COMPRA',
         'data_transacao': '2024-08-05', 'quantidade': 10, 'preco_unitario': 86.00,
         'taxa_corretagem': 1.00, 'custos_totais': 1.50, 'observacoes': 'Treasury Bond ETF'},
        {'usuario': 'e2e_user', 'ativo': 'BTC', 'corretora': 'XP INVESTIMENTOS', 'tipo': 'COMPRA',
         'data_transacao': '2024-09-01', 'quantidade': 0.05, 'preco_unitario': 58000.00,
         'taxa_corretagem': 29.00, 'custos_totais': 35.00, 'observacoes': 'Cripto BTC'},
        {'usuario': 'e2e_user', 'ativo': 'ETH', 'corretora': 'XP INVESTIMENTOS', 'tipo': 'COMPRA',
         'data_transacao': '2024-09-15', 'quantidade': 1.5, 'preco_unitario': 3000.00,
         'taxa_corretagem': 4.50, 'custos_totais': 6.00, 'observacoes': 'Cripto ETH'},
        {'usuario': 'e2e_user', 'ativo': 'SOL', 'corretora': 'INTER BANCO', 'tipo': 'COMPRA',
         'data_transacao': '2024-10-01', 'quantidade': 20, 'preco_unitario': 140.00,
         'taxa_corretagem': 2.80, 'custos_totais': 4.00, 'observacoes': 'Cripto SOL'},
        {'usuario': 'e2e_user', 'ativo': 'BOVA11', 'corretora': 'XP INVESTIMENTOS', 'tipo': 'VENDA',
         'data_transacao': '2024-11-15', 'quantidade': 10, 'preco_unitario': 128.00,
         'taxa_corretagem': 1.28, 'custos_totais': 2.00, 'observacoes': 'Venda parcial BOVA11'},
        {'usuario': 'e2e_user', 'ativo': 'BTC', 'corretora': 'XP INVESTIMENTOS', 'tipo': 'VENDA',
         'data_transacao': '2024-12-10', 'quantidade': 0.01, 'preco_unitario': 62000.00,
         'taxa_corretagem': 6.20, 'custos_totais': 8.00, 'observacoes': 'Venda parcial BTC — lucro'},
    ]
    data.setdefault('transacoes', []).extend(extra_tx)

    extra_mov = [
        {'usuario': 'e2e_user', 'corretora': 'XP INVESTIMENTOS', 'tipo': 'imposto',
         'data_movimentacao': '2024-10-31', 'valor': 685.50, 'moeda': 'BRL',
         'observacoes': 'DARF outubro — vendas PETR4/ITUB4'},
        {'usuario': 'e2e_user', 'corretora': 'XP INVESTIMENTOS', 'corretora_destino': 'INTER BANCO',
         'tipo': 'transferencia_enviada', 'data_movimentacao': '2024-06-01', 'valor': 3000.00, 'moeda': 'BRL',
         'observacoes': 'Transferência XP → Inter para BDRs'},
        {'usuario': 'e2e_user', 'corretora': 'INTER BANCO', 'corretora_destino': 'XP INVESTIMENTOS',
         'tipo': 'transferencia_recebida', 'data_movimentacao': '2024-06-01', 'valor': 3000.00, 'moeda': 'BRL',
         'observacoes': 'Transferência recebida da XP'},
        {'usuario': 'e2e_user', 'corretora': 'XP INVESTIMENTOS', 'tipo': 'taxa_custodia',
         'data_movimentacao': '2024-07-31', 'valor': 12.90, 'moeda': 'BRL',
         'observacoes': 'Taxa custódia mensal'},
    ]
    data.setdefault('movimentacoes_caixa', []).extend(extra_mov)

    data['calendario_dividendo'] = e2e.get('calendario_dividendo', [])
    data['projecoes_renda'] = e2e.get('projecoes_renda', [])
    data['regras_fiscais'] = e2e.get('regras_fiscais', [])

    data['meta_alocacao'] = [
        {'usuario': 'e2e_user', 'classe': 'renda_variavel', 'percentual_target': 70.0, 'tolerancia_pct': 2.0},
        {'usuario': 'e2e_user', 'classe': 'renda_fixa', 'percentual_target': 25.0, 'tolerancia_pct': 2.0},
        {'usuario': 'e2e_user', 'classe': 'cripto', 'percentual_target': 5.0, 'tolerancia_pct': 1.0},
    ]

    data['fontes_dados'] = [
        {'nome': 'brapi.dev', 'tipo_fonte': 'api', 'url_base': 'https://brapi.dev/api',
         'requer_autenticacao': False, 'rate_limit': '100/minute', 'ativa': True, 'prioridade': 1,
         'total_consultas': 1200, 'total_erros': 15, 'observacoes': 'API B3 primária'},
        {'nome': 'yfinance', 'tipo_fonte': 'api', 'url_base': 'https://query1.finance.yahoo.com',
         'requer_autenticacao': False, 'rate_limit': '2000/hour', 'ativa': True, 'prioridade': 2,
         'total_consultas': 800, 'total_erros': 40, 'observacoes': 'Fallback global'},
        {'nome': 'Alpha Vantage', 'tipo_fonte': 'api', 'url_base': 'https://www.alphavantage.co/query',
         'requer_autenticacao': True, 'rate_limit': '5/minute', 'ativa': True, 'prioridade': 3,
         'total_consultas': 200, 'total_erros': 10, 'observacoes': 'US stocks'},
        {'nome': 'Finnhub', 'tipo_fonte': 'api', 'url_base': 'https://finnhub.io/api/v1',
         'requer_autenticacao': True, 'rate_limit': '60/minute', 'ativa': True, 'prioridade': 4,
         'total_consultas': 150, 'total_erros': 5, 'observacoes': 'US mercado'},
    ]

    taxas = []
    base_usd_brl = 5.45
    for i in range(12):
        d = date(2024, 1, 15) + timedelta(days=30 * i)
        rate = round(base_usd_brl + (i % 4 - 1) * 0.08, 4)
        taxas.append({
            'par_moeda': 'USD/BRL', 'moeda_base': 'USD', 'moeda_cotacao': 'BRL',
            'taxa': rate, 'data_referencia': d.isoformat(), 'fonte': 'manual',
        })
        taxas.append({
            'par_moeda': 'BRL/USD', 'moeda_base': 'BRL', 'moeda_cotacao': 'USD',
            'taxa': round(1 / rate, 6), 'data_referencia': d.isoformat(), 'fonte': 'manual',
        })
    data['taxas_cambio'] = taxas

    historico = []
    for ticker, base in [('PETR4', 38.50), ('ITUB4', 32.45), ('HGLG11', 185.20), ('AAPL', 172.50)]:
        historico.extend(_monthly_prices(ticker, base))
    data['historico_preco'] = historico

    data['saldo_prejuizo'] = [
        {'usuario': 'e2e_user', 'categoria': 'swing_acoes', 'ano_mes': '2024-08', 'saldo': 616.00},
        {'usuario': 'e2e_user', 'categoria': 'swing_acoes', 'ano_mes': '2024-09', 'saldo': 245.00},
        {'usuario': 'e2e_user', 'categoria': 'fiis', 'ano_mes': '2024-09', 'saldo': 45.00},
        {'usuario': 'e2e_user', 'categoria': 'exterior', 'ano_mes': '2024-11', 'saldo': 136.00},
    ]

    out = SCENARIOS / 'test_menu_full.json'
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f'✅ Gerado: {out} ({len(data["ativos"])} ativos, {len(data["transacoes"])} transações)')


if __name__ == '__main__':
    build()
