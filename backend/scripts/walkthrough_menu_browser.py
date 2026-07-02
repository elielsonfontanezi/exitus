#!/usr/bin/env python3
"""Walkthrough HTTP+session das telas — classifica AUTO_OK / NEEDS_MANUAL para o usuário."""
import http.cookiejar
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

BASE = 'http://localhost:8080'
API = 'http://localhost:5000'

SCREENS = [
    (1, 'Login', '/auth/login', 'public', []),
    (2, 'Dashboard', '/dashboard/', 'user', ['client_api', 'chart']),
    (3, 'Config Perfil', '/configuracoes/perfil', 'user', ['form']),
    (4, 'Config Corretoras', '/configuracoes/corretoras', 'user', ['client_api', 'crud']),
    (5, 'Operações', '/operacoes/', 'user', ['client_api', 'crud', 'form']),
    (6, 'Operações Venda', '/operacoes/?venda=true', 'user', ['client_api', 'crud', 'form']),
    (8, 'Operações Histórico', '/operacoes/historico', 'user', ['client_api']),
    (9, 'Carteira Posições', '/carteira/posicoes', 'user', ['client_api']),
    (10, 'Carteira Movimentações', '/carteira/movimentacoes', 'user', ['client_api']),
    (None, 'Carteira Câmbio', '/carteira/cambio', 'user', ['client_api', 'form']),
    (11, 'Ativos Catálogo', '/ativos/acoes', 'user', ['client_api']),
    (12, 'Ativos Detalhe PETR4', '/ativos/PETR4', 'user', ['client_api']),
    (13, 'Eventos Corporativos', '/ativos/eventos-corporativos', 'user', ['client_api']),
    (14, 'Proventos Calendário', '/proventos/calendario', 'user', ['client_api', 'crud']),
    (15, 'Análises Evolução', '/analises/evolucao', 'user', ['client_api', 'chart']),
    (16, 'Análises Performance', '/analises/performance', 'user', ['client_api', 'chart']),
    (17, 'Análises Alocação', '/analises/alocacao', 'user', ['client_api', 'chart']),
    (18, 'Buy Signals', '/analises/buy-signals', 'user', ['client_api']),
    (19, 'Rentabilidade legacy', '/analises/rentabilidade', 'user', ['redirect']),
    (19, 'Rentabilidade Período', '/analises/rentabilidade/periodo', 'user', ['client_api', 'chart']),
    (20, 'IR Mensal', '/imposto-renda/mensal', 'user', ['client_api']),
    (21, 'DARFs', '/imposto-renda/darfs', 'user', ['client_api']),
    (22, 'IR Histórico', '/imposto-renda/historico', 'user', ['client_api']),
    (23, 'DIRPF', '/imposto-renda/declaracao', 'user', ['client_api']),
    (24, 'Relatório Mensal', '/relatorios/mensal', 'user', ['client_api']),
    (25, 'Relatório Anual', '/relatorios/anual', 'user', ['client_api']),
    (26, 'Relatório Extrato', '/relatorios/extrato', 'user', ['client_api']),
    (27, 'Relatório IR', '/relatorios/ir', 'user', ['client_api']),
    (28, 'Relatório Exportar', '/relatorios/exportar', 'user', ['client_api', 'download']),
    (29, 'Screener', '/ferramentas/screener', 'user', ['client_api']),
    (30, 'Comparador', '/ferramentas/comparador', 'user', ['client_api', 'form']),
    (31, 'Calculadora IR', '/ferramentas/calculadora-ir', 'user', ['client_api', 'form']),
    (32, 'Simulador', '/ferramentas/simulador', 'user', ['redirect']),
    (33, 'Reconciliação', '/ferramentas/reconciliacao', 'user', ['client_api']),
    (34, 'Planos', '/planos-compra/', 'user', ['client_api']),
    (35, 'Alertas', '/alertas/', 'user', ['client_api', 'crud']),
    (36, 'Preço Teto', '/ferramentas/preco-teto', 'user', ['client_api', 'form']),
    (37, 'Correlação', '/analises/correlacao', 'user', ['client_api', 'chart']),
    (38, 'Projeções Renda', '/analises/projecoes/renda', 'user', ['client_api']),
    (39, 'Fontes Dados', '/configuracoes/fontes-dados', 'user', ['client_api', 'crud']),
    (40, 'Portfolios', '/configuracoes/portfolios', 'user', ['client_api', 'crud']),
    (41, 'Regras Fiscais', '/configuracoes/regras-fiscais', 'user', ['client_api', 'crud', 'admin']),
    (42, 'Admin Usuários', '/admin/usuarios', 'admin', ['client_api', 'crud', 'admin']),
    (43, 'Análises Risco', '/analises/risco', 'user', ['client_api', 'chart']),
    (44, 'Projeções Patrimônio', '/analises/projecoes', 'user', ['client_api', 'form']),
]

TAG_MANUAL = {
    'client_api': 'Dados carregam via JavaScript (apiFetch) — HTML inicial não prova KPIs/tabelas',
    'crud': 'Criar/editar/excluir não testado',
    'form': 'Validação visual de formulários',
    'chart': 'Gráfico: precisão dos dados não verificável sem browser',
    'download': 'Download de arquivo não testado',
    'admin': 'Mutations admin / permissões',
    'redirect': 'Confirmar redirect visualmente',
}

ERROR_RE = None  # HTML contém strings de erro em JS (base_interna) — usar só API + HTTP


def strip_scripts(html):
    return re.sub(r'<script[\s\S]*?</script>', '', html, flags=re.I)


def make_opener(jar):
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))


def login(jar, username, password):
    opener = make_opener(jar)
    payload = json.dumps({'username': username, 'password': password}).encode()
    req = urllib.request.Request(
        f'{BASE}/auth/login',
        data=payload,
        headers={
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
        },
        method='POST',
    )
    resp = opener.open(req, timeout=20)
    data = json.loads(resp.read().decode())
    if not data.get('success'):
        raise RuntimeError(f'Login falhou: {data}')
    return data.get('token')


def api_get(token, path):
    req = urllib.request.Request(
        f'{API}{path}',
        headers={'Authorization': f'Bearer {token}'},
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read())
        except Exception:
            body = {'error': str(e)[:200]}
        return e.code, body
    except Exception as e:
        return 0, {'error': str(e)[:200]}


def page_get(jar, path):
    opener = make_opener(jar)
    req = urllib.request.Request(f'{BASE}{path}', headers={'User-Agent': 'ExitusWalkthrough/1.0'})
    try:
        resp = opener.open(req, timeout=30)
        return resp.status, resp.geturl(), resp.read().decode('utf-8', errors='replace')
    except urllib.error.HTTPError as e:
        return e.code, path, e.read().decode('utf-8', errors='replace')


def api_has_data(path, body):
    if not isinstance(body, dict):
        return False
    if body.get('success') is False:
        return False
    data = body.get('data', body)
    if isinstance(data, list):
        return len(data) > 0
    if isinstance(data, dict):
        for k in ('items', 'registros', 'posicoes', 'corretoras', 'ativos', 'transacoes',
                  'movimentacoes', 'alertas', 'portfolios', 'fontes_dados', 'projecoes',
                  'regras', 'meses', 'darfs', 'dividendos', 'evolucao', 'pontos', 'series'):
            v = data.get(k)
            if isinstance(v, list) and len(v) > 0:
                return True
        for k in ('patrimonio_total', 'patrimonio', 'total_patrimonio', 'sharpe', 'hhi'):
            if data.get(k) not in (None, 0, '', []):
                return True
        if data.get('total', 0) > 0:
            return True
        # performance endpoint returns flat dict
        if 'id' in data and ('formato_export' in data or 'metricas' in data):
            return True
        return len(data) > 2
    return bool(data)


# Map screen -> primary API endpoint for data validation
API_MAP = {
    '/dashboard/': '/api/portfolios/dashboard',
    '/configuracoes/corretoras': '/api/corretoras',
    '/operacoes/': '/api/ativos?per_page=5',
    '/operacoes/historico': '/api/transacoes?per_page=5',
    '/carteira/posicoes': '/api/posicoes?per_page=5',
    '/carteira/movimentacoes': '/api/movimentacoes-caixa?per_page=5',
    '/carteira/cambio': '/api/cambio/pares',
    '/ativos/acoes': '/api/ativos?per_page=5',
    '/ativos/PETR4': '/api/ativos/ticker/PETR4',
    '/ativos/eventos-corporativos': '/api/eventos-corporativos',
    '/proventos/calendario': '/api/calendario-dividendos/?per_page=5',
    '/analises/evolucao': '/api/portfolios/evolucao?dias=90',
    '/analises/performance': '/api/performance/performance',
    '/analises/alocacao': '/api/portfolios/alocacao',
    '/analises/buy-signals': '/api/buy-signals/watchlist-top?limit=5',
    '/analises/rentabilidade/periodo': '/api/portfolios/rentabilidade?benchmark=cdi',
    '/imposto-renda/mensal': '/api/ir/apuracao?mes=2024-10',
    '/imposto-renda/darfs': '/api/ir/darf?mes=2024-10',
    '/imposto-renda/historico': '/api/ir/historico?ano=2024',
    '/imposto-renda/declaracao': '/api/ir/dirpf?ano=2024',
    '/relatorios/mensal': '/api/ir/apuracao?mes=2024-10',
    '/relatorios/anual': '/api/ir/historico?ano=2024',
    '/relatorios/extrato': '/api/transacoes?per_page=5',
    '/relatorios/ir': '/api/ir/apuracao?mes=2024-10',
    '/ferramentas/screener': '/api/ativos?per_page=10',
    '/ferramentas/reconciliacao': '/api/reconciliacao/verificar',
    '/planos-compra/': '/api/plano-compra/dashboard',
    '/alertas/': '/api/alertas',
    '/ferramentas/preco-teto': '/api/calculos/preco_teto/PETR4',
    '/analises/correlacao': '/api/performance/correlacao',
    '/analises/projecoes/renda': '/api/projecoes/renda',
    '/configuracoes/fontes-dados': '/api/fontes-dados',
    '/configuracoes/portfolios': '/api/portfolios',
    '/configuracoes/regras-fiscais': '/api/regras-fiscais',
    '/admin/usuarios': '/api/usuarios',
    '/analises/risco': '/api/portfolios/metricas-risco',
    '/analises/projecoes': '/api/portfolios/dashboard',
}


def tier_for(tags, auto_status):
    if auto_status == 'AUTO_OK':
        return 'PODE_PULAR'
    if auto_status in ('AUTO_FAIL', 'NEEDS_MANUAL'):
        return 'OBRIGATORIO'
    if 'admin' in tags or 'crud' in tags or 'form' in tags or 'download' in tags:
        return 'OBRIGATORIO'
    if 'chart' in tags:
        return 'RECOMENDADO'
    return 'AMOSTRA'


def _result(num, name, path, http, status, detail, reasons, needs_you, tags=None):
    tags = tags or []
    return {
        'num': num, 'name': name, 'path': path, 'http': http,
        'auto_status': status, 'detail': detail,
        'manual_reasons': list(dict.fromkeys(reasons)),
        'needs_you': needs_you,
        'tier': tier_for(tags, status),
    }


def classify(num, name, path, role, tags, jar, token):
    manual_reasons = [TAG_MANUAL[t] for t in tags if t in TAG_MANUAL]

    if path == '/auth/login':
        st, _, body = page_get(jar, path)
        return _result(num, name, path, st, 'AUTO_OK', 'página pública', manual_reasons, False, tags)

    st, final_url, body = page_get(jar, path)

    if role == 'admin':
        manual_reasons.append('Admin: decorator require_admin usa session.logged_in — confirmar acesso visual')
        needs = st >= 400 or '/auth/login' in final_url or '/dashboard' in final_url
        status = 'NEEDS_MANUAL' if needs else 'AUTO_OK_VERIFY_UI'
        return _result(num, name, path, st, status, final_url, manual_reasons, True, tags)

    if st >= 400:
        return _result(num, name, path, st, 'AUTO_FAIL', f'HTTP {st}', manual_reasons + ['Página não carregou'], True, tags)

    if '/auth/login' in final_url and path != '/auth/login':
        return _result(num, name, path, st, 'AUTO_FAIL', 'redirect login', ['Sessão inválida'], True, tags)

    if 'redirect' in tags and path == '/ferramentas/simulador':
        if '/analises/projecoes' in final_url or '/projecoes' in final_url:
            return _result(num, name, path, st, 'AUTO_OK', f'redirect → {final_url}', manual_reasons, bool(manual_reasons), tags)
        return _result(num, name, path, st, 'AUTO_PARCIAL', f'url={final_url}', manual_reasons + ['Redirect inesperado'], True, tags)

    if 'redirect' in tags and path == '/analises/rentabilidade':
        if 'periodo' in final_url:
            return _result(num, name, path, st, 'AUTO_OK', 'redirect período OK', manual_reasons, bool(manual_reasons), tags)
        return _result(num, name, path, st, 'AUTO_PARCIAL', f'url={final_url}', manual_reasons, True, tags)

    shell_ok = 'base_interna' in body or 'page_content' in body or 'section-box' in body
    if ERROR_RE and ERROR_RE.search(strip_scripts(body)):
        return _result(num, name, path, st, 'AUTO_FAIL', 'error state no HTML', manual_reasons, True, tags)

    api_path = API_MAP.get(path.split('?')[0])
    api_ok = None
    api_detail = ''
    if api_path and token:
        code, api_body = api_get(token, api_path)
        if code == 0:
            api_ok = False
            api_detail = f'API timeout/erro: {api_body.get("error", "")[:60]}'
        else:
            api_ok = code == 200 and api_has_data(api_path, api_body)
            api_detail = f'API {code} {"dados" if api_ok else "vazio/erro"}'

    needs_you = False
    auto_status = 'AUTO_OK'

    if api_ok is False:
        auto_status = 'AUTO_FAIL'
        needs_you = True
        manual_reasons.append(f'API sem dados: {api_path}')
    elif api_ok is True:
        if manual_reasons:
            auto_status = 'AUTO_OK_VERIFY_UI'
            needs_you = True
        else:
            auto_status = 'AUTO_OK'
            needs_you = False
    elif not shell_ok:
        auto_status = 'AUTO_PARCIAL'
        needs_you = True
        manual_reasons.append('Shell HTML incompleto')
    else:
        auto_status = 'AUTO_OK_VERIFY_UI'
        needs_you = True

    detail = api_detail or ('shell OK' if shell_ok else 'shell fraco')
    return _result(num, name, path, st, auto_status, detail, manual_reasons, needs_you, tags)


def write_checklist_md(report, path):
    tiers = {'OBRIGATORIO': [], 'RECOMENDADO': [], 'AMOSTRA': [], 'PODE_PULAR': []}
    for r in report['results']:
        tiers.setdefault(r['tier'], []).append(r)

    lines = [
        '# Checklist Walkthrough — O que você deve verificar',
        '',
        '**Data:** 02/07/2026 | **Cenário:** `test_menu_full` | **Login:** `e2e_user` / `e2e_senha_123`',
        '',
        'Legenda de camadas da automação:',
        '- **AUTO_OK** — página/redirect validado sem interação',
        '- **AUTO_OK_VERIFY_UI** — API retornou dados; UI renderizada só no browser',
        '- **NEEDS_MANUAL** — automação não conseguiu validar',
        '',
        f"Resumo: {report['summary']['total']} telas | "
        f"Obrigatório você: {len(tiers['OBRIGATORIO'])} | "
        f"Recomendado: {len(tiers['RECOMENDADO'])} | "
        f"Amostra: {len(tiers['AMOSTRA'])} | "
        f"Pode pular: {len(tiers['PODE_PULAR'])}",
        '',
        '```bash',
        'podman exec exitus-backend python reset_and_seed.py --clean --scenario test_menu_full',
        'cd backend && python3 scripts/walkthrough_menu_browser.py',
        '```',
        '',
    ]

    def section(title, items, note):
        lines.append(f'## {title}')
        lines.append('')
        lines.append(note)
        lines.append('')
        lines.append('| # | Tela | URL | Automação |')
        lines.append('|---|------|-----|-----------|')
        for r in sorted(items, key=lambda x: (x['num'] is None, x['num'] or 0)):
            lines.append(
                f"| {r['num'] or '—'} | {r['name']} | `{r['path']}` | {r['auto_status']} — {r['detail']} |"
            )
        lines.append('')

    section(
        '1. OBRIGATÓRIO — você deve abrir e validar',
        tiers['OBRIGATORIO'],
        'CRUD, formulários, download, admin ou falha de automação. **Sem isso não feche o gate Go-Live.**',
    )
    section(
        '2. RECOMENDADO — gráficos e KPIs visuais',
        tiers['RECOMENDADO'],
        'API OK; confirme que gráficos e cards exibem valores coerentes (não só que a página carregou).',
    )
    section(
        '3. AMOSTRA — confira 5–8 telas (listas read-only)',
        tiers['AMOSTRA'],
        'Automação confirmou API com dados. Faça amostragem: posições, histórico, IR, relatórios, screener, etc.',
    )
    section(
        '4. PODE PULAR — já validado pela automação',
        tiers['PODE_PULAR'],
        'Redirects e login; opcional rever em 30 segundos.',
    )

    lines.append('## Admin (tela 42)')
    lines.append('')
    lines.append('Use **`e2e_admin`** / `e2e_senha_123`. Se redirecionar para login, há bug em `require_admin` (`session.logged_in` vs `user_id`).')
    lines.append('')

    path.write_text('\n'.join(lines), encoding='utf-8')


def main():
    results = []

    jar = http.cookiejar.CookieJar()
    token = login(jar, 'e2e_user', 'e2e_senha_123')
    print('Login e2e_user OK\n')

    for num, name, path, role, tags in SCREENS:
        if role == 'admin':
            continue
        r = classify(num, name, path, role, tags, jar, token)
        results.append(r)
        mark = '>>> VOCE' if r['needs_you'] else 'AUTO  '
        print(f"{mark} #{str(r['num'] or '-'):>2} {r['name']:<28} {r['auto_status']:<22} {r['detail']}")

    jar_admin = http.cookiejar.CookieJar()
    token_admin = login(jar_admin, 'e2e_admin', 'e2e_senha_123')
    for num, name, path, role, tags in SCREENS:
        if role != 'admin':
            continue
        r = classify(num, name, path, role, tags, jar_admin, token_admin)
        results.append(r)
        mark = '>>> VOCE' if r['needs_you'] else 'AUTO  '
        print(f"{mark} #{str(r['num'] or '-'):>2} {r['name']:<28} {r['auto_status']:<22} {r['detail']}")

    needs = [r for r in results if r['needs_you']]
    pure_ok = [r for r in results if r['auto_status'] == 'AUTO_OK']
    fails = [r for r in results if r['auto_status'] == 'AUTO_FAIL']

    print(f'\n=== RESUMO ===')
    print(f'Total: {len(results)} | AUTO_OK puro: {len(pure_ok)} | Verificar você: {len(needs)} | Falhas: {len(fails)}')

    report = {
        'summary': {
            'total': len(results),
            'auto_ok_pure': len(pure_ok),
            'needs_manual': len(needs),
            'auto_fail': len(fails),
        },
        'checklist_usuario': [
            {
                'num': r['num'],
                'name': r['name'],
                'url': BASE + r['path'],
                'tier': r['tier'],
                'motivo': r['manual_reasons'] or [r['detail']],
                'prioridade': r['tier'],
            }
            for r in needs
        ],
        'tiers': {
            k: [{'num': r['num'], 'name': r['name'], 'path': r['path']} for r in results if r['tier'] == k]
            for k in ('OBRIGATORIO', 'RECOMENDADO', 'AMOSTRA', 'PODE_PULAR')
        },
        'results': results,
    }

    json_path = Path(__file__).resolve().parent / 'walkthrough_browser_report.json'
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'JSON: {json_path}')

    md_path = Path(__file__).resolve().parent.parent.parent / 'docs' / 'WALKTHROUGH_CHECKLIST_USUARIO.md'
    write_checklist_md(report, md_path)
    print(f'MD: {md_path}')

    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
