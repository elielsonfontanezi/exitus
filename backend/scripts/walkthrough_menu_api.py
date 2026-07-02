#!/usr/bin/env python3
"""Smoke walkthrough APIs — 43 telas menu (SEED-MENU-001 passo 3)."""
import json
import sys
import urllib.request

BASE = 'http://localhost:5000'


def login():
    req = urllib.request.Request(
        f'{BASE}/api/auth/login',
        data=json.dumps({'username': 'e2e_user', 'password': 'e2e_senha_123'}).encode(),
        headers={'Content-Type': 'application/json'},
        method='POST',
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read())
    return data['data']['access_token']


def _count_items(data):
    """Conta registros em respostas heterogêneas da API Exitus."""
    if data is None:
        return 0
    if isinstance(data, list):
        return len(data)
    if not isinstance(data, dict):
        return 1 if data else 0
    for key in (
        'items', 'registros', 'posicoes', 'darfs', 'corretoras', 'ativos',
        'transacoes', 'movimentacoes', 'eventos', 'alertas', 'portfolios',
        'fontes_dados', 'projecoes', 'regras', 'meses', 'relatorios',
        'dividendos', 'proventos',
    ):
        nested = data.get(key)
        if isinstance(nested, list) and nested:
            return len(nested)
    if data.get('total', 0) > 0:
        return int(data['total'])
    if data.get('qtd_posicoes', 0) > 0:
        return int(data['qtd_posicoes'])
    return len(data) if data else 0


def get(path, token, expect_list=False):
    req = urllib.request.Request(
        f'{BASE}{path}',
        headers={'Authorization': f'Bearer {token}'},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            body = json.loads(r.read())
        if r.status != 200:
            return 'ERRO', f'HTTP {r.status}'
        if isinstance(body, dict) and body.get('success') is False:
            return 'ERRO', body.get('message', 'success=false')
        data = body.get('data', body)
        if expect_list:
            n = _count_items(data)
            if n == 0:
                return 'VAZIO', '0 registros'
            return 'OK', f'{n} itens'
        if _count_items(data) == 0 and isinstance(data, dict) and not data.get('patrimonio_total'):
            return 'VAZIO', 'sem dados'
        return 'OK', 'dados presentes'
    except Exception as e:
        return 'ERRO', str(e)[:80]


CHECKS = [
    ('1 Login', '/api/auth/me', False),
    ('2 Dashboard indicadores', '/api/indicadores/dashboard', False),
    ('4 Corretoras', '/api/corretoras', True),
    ('8 Histórico transações', '/api/transacoes?per_page=5', True),
    ('9 Posições', '/api/posicoes?per_page=5', True),
    ('10 Movimentações caixa', '/api/movimentacoes-caixa?per_page=5', True),
    ('11 Ativos catálogo', '/api/ativos?per_page=10', True),
    ('12 Detalhe PETR4', '/api/ativos/ticker/PETR4', False),
    ('13 Eventos corp.', '/api/eventos-corporativos', True),
    ('14 Calendário div.', '/api/calendario-dividendos', True),
    ('15 Evolução', '/api/portfolios/evolucao?dias=90', False),
    ('16 Performance', '/api/performance/performance', False),
    ('17 Alocação', '/api/portfolios/alocacao', False),
    ('17 Metas alocação', '/api/portfolios/meta-alocacao', True),
    ('18 Buy signals', '/api/buy-signals/watchlist-top?limit=5', True),
    ('19b Rentabilidade', '/api/portfolios/rentabilidade?benchmark=cdi', False),
    ('20 IR mensal', '/api/ir/apuracao?mes=2024-10', False),
    ('21 DARFs', '/api/ir/darf?mes=2024-10', True),
    ('22 IR histórico', '/api/ir/historico?ano=2024', True),
    ('24 Relatórios lista', '/api/relatorios/lista', True),
    ('29 Screener ativos', '/api/ativos?per_page=20', True),
    ('31 Preço teto PETR4', '/api/calculos/preco_teto/PETR4', False),
    ('33 Reconciliação', '/api/reconciliacao/verificar', False),
    ('34 Planos compra', '/api/plano-compra/dashboard', False),
    ('35 Alertas', '/api/alertas', True),
    ('43 Risco', '/api/portfolios/metricas-risco', False),
    ('44 Projeções patrimônio', '/api/portfolios/dashboard', False),
    ('36 Preço teto calc', '/api/calculos/preco_teto/ITUB4', False),
    ('37 Correlação', '/api/performance/correlacao', False),
    ('38 Projeções renda', '/api/projecoes/renda', True),
    ('39 Fontes dados', '/api/fontes-dados', True),
    ('40 Portfolios', '/api/portfolios', True),
    ('41 Regras fiscais', '/api/regras-fiscais', True),
    ('Câmbio pares', '/api/cambio/pares', True),
    ('Concentração', '/api/portfolios/concentracao', False),
    ('Cotações health', '/api/cotacoes/health', False),
]


def main():
    token = login()
    results = []
    for label, path, expect_list in CHECKS:
        status, detail = get(path, token, expect_list)
        results.append((label, path, status, detail))
        print(f'{status:6} {label:28} {detail}')

    errors = [r for r in results if r[2] == 'ERRO']
    empty = [r for r in results if r[2] == 'VAZIO']
    print(f'\n--- Resumo: {len(results)} checks, {len(errors)} erros, {len(empty)} vazios ---')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
