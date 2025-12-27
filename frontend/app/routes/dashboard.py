# frontend/app/routes/dashboard.py
# -*- coding: utf-8 -*-
"""
Exitus Frontend - Dashboard Routes
MÓDULOS 6 e 7 (Restaurado e Corrigido)
"""

from flask import Blueprint, render_template, session, redirect, url_for, flash, request
import requests
from functools import wraps
from app.config import Config

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('username') and not session.get('access_token'):
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Rota Principal (Home) ---
@bp.route('/', methods=['GET'])
@login_required
def index():
    """Dashboard Principal (Home) - Integrado M7"""
    token = session.get('access_token')

    # Estrutura padrão (zerada) para evitar erros no template
    dados = {
        "patrimonio_total": 0.0,
        "rentabilidade_geral": 0.0,
        "total_portfolios": 0,
        "total_ativos": 0,
        "alocacao": {},
        "evolucao": [],
        "ultimas_transacoes": []
    }

    if token:
        try:
            headers = {'Authorization': f'Bearer {token}'}

            # Chamada A: Resumo Portfolio
            resp_dash = requests.get(f'{Config.BACKEND_API_URL}/api/portfolios/dashboard', headers=headers, timeout=5)
            if resp_dash.status_code == 200:
                data = resp_dash.json().get('data', {})
                resumo = data.get('resumo', {})
                dados.update({
                    "patrimonio_total": resumo.get('patrimonio_total', 0.0),
                    "rentabilidade_geral": resumo.get('rentabilidade_geral', 0.0),
                    "total_portfolios": resumo.get('total_portfolios', 0),
                    "total_ativos": resumo.get('total_posicoes', 0)
                })

        except Exception as e:
            print(f"Erro no dashboard home: {e}")

    return render_template('dashboard/index.html', dados=dados)


# --- Rotas Restauradas do Módulo 6 ---
@bp.route('/buy-signals')
@login_required
def buy_signals():
    """Buy Signals - M6.1"""
    token = session.get('access_token')
    signals = []
    
    if token:
        try:
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get(
                f'{Config.BACKEND_API_URL}/api/buy-signals/watchlist-top',
                headers=headers,
                timeout=5
            )
            if response.status_code == 200:
                raw_signals = response.json().get('data', [])
                # ✅ CORREÇÃO 1: Mapear buy_score → buyscore para compatibilidade com template
                for item in raw_signals:
                    signals.append({
                        'ticker': item.get('ticker'),
                        'nome': item.get('nome'),
                        'mercado': item.get('mercado'),
                        'buyscore': item.get('buy_score', 0),  # ← Mapeamento
                        'margem': item.get('margem_seguranca', 0)
                    })
        except Exception as e:
            print(f"Erro buy-signals: {e}")
    
    return render_template('dashboard/buy_signals.html', signals=signals)


@bp.route('/portfolios')
@login_required
def portfolios():
    """M7 - Dashboard Portfolios integrado com Backend API"""
    token = session.get('access_token')
    
    if token:
        try:
            headers = {'Authorization': f'Bearer {token}'}
            portfolios_response = requests.get(
                f"{Config.BACKEND_API_URL}/api/portfolios",
                headers=headers,
                params={'page': 1, 'per_page': 50},
                timeout=10
            )

            if portfolios_response.status_code == 200:
                portfolios_data = portfolios_response.json()
                portfolios = portfolios_data.get('data', [])

                stats = {
                    "total": portfolios_data.get('total', 0),
                    "ativas": len([p for p in portfolios if p.get('ativo', True)]),
                    "saldo_total": 0.0,
                    "saldo_br": 0.0,
                    "saldo_us": 0.0
                }

                corretoras = []
                for portfolio in portfolios:
                    corretoras.append({
                        "id": portfolio['id'],
                        "nome": portfolio['nome'],
                        "descricao": portfolio['descricao'] or '',
                        "objetivo": portfolio['objetivo'] or 'Geral',
                        "ativo": portfolio['ativo'],
                        "created_at": portfolio.get('created_at', '2025-12-25T00:00:00')
                    })

                return render_template(
                    'dashboard/portfolios.html',
                    stats=stats,
                    corretoras=corretoras,
                    filtros={"tipo": "todos", "status": "ativos", "periodo": "12m"},
                    backend_status="ok"
                )
        except Exception as e:
            print(f"Erro portfolios API: {e}")

    # Backend offline → Mock ROBUSTO
    return _render_portfolios_mock(backend_status="backend_offline")


def _render_portfolios_mock(backend_status="mock"):
    """Mock ROBUSTO com created_at sempre presente ✅"""
    stats = {
        "total": 2,
        "ativas": 2,
        "saldo_total": 125000.50,
        "saldo_br": 95000.00,
        "saldo_us": 30000.50
    }

    corretoras = [
        {
            "id": "1e1c2bfe-e3b8-4ab7-81f5-40d925ffe2e3",
            "nome": "Portfolio Principal - admin",
            "descricao": "Carteira principal de investimentos",
            "objetivo": "Crescimento",
            "ativo": True,
            "created_at": "2025-12-18T15:47:24"
        },
        {
            "id": "b6629879-1a9e-460f-944f-3f31b7f34d01",
            "nome": "Aposentadoria 2050",
            "descricao": "Foco em dividendos",
            "objetivo": "Longo Prazo",
            "ativo": True,
            "created_at": "2025-12-19T18:21:19"
        }
    ]

    return render_template(
        'dashboard/portfolios.html',
        stats=stats,
        corretoras=corretoras,
        filtros={"tipo": "todos", "status": "ativos", "periodo": "12m"},
        backend_status=backend_status
    )


@bp.route('/assets')
@login_required
def assets():
    """M7 - Dashboard Ativos integrado com Backend API"""
    token = session.get('access_token')

    stats = {
        "total": 0,
        "acoes": 0,
        "fiis": 0,
        "bdrs": 0,
        "etfs": 0
    }

    ativos = []
    tipo_filtro = request.args.get('tipo', 'todos')
    setor_filtro = request.args.get('setor', '')

    if token:
        try:
            headers = {'Authorization': f'Bearer {token}'}
            params = {'page': request.args.get('page', 1), 'per_page': 50}

            # ✅ CORREÇÃO 2: Endpoint sem barra final
            response = requests.get(
                f'{Config.BACKEND_API_URL}/api/ativos',  # ← SEM /
                headers=headers,
                params=params,
                timeout=5
            )

            if response.status_code == 200:
                payload = response.json()
                ativos_raw = payload.get('data', {}).get('ativos', [])

                for item in ativos_raw:
                    ativos.append({
                        "id": item.get('id'),
                        "ticker": item.get('ticker'),
                        "nome": item.get('nome') or item.get('ticker'),
                        "tipo": item.get('tipo', 'OUTROS'),
                        "setor": item.get('setor', 'N/A'),
                        "cotacao": item.get('cotacao_atual', 0.0)
                    })

                stats["total"] = payload.get('total', len(ativos))
                stats["acoes"] = len([a for a in ativos if a['tipo'] == 'ACAO'])
                stats["fiis"] = len([a for a in ativos if a['tipo'] == 'FII'])
                stats["bdrs"] = len([a for a in ativos if a['tipo'] == 'BDR'])
                stats["etfs"] = len([a for a in ativos if a['tipo'] == 'ETF'])

        except Exception as e:
            print(f"Erro ao buscar ativos: {e}")
            flash('Não foi possível carregar a lista de ativos.', 'error')

    return render_template(
        'dashboard/assets.html',
        ativos=ativos,
        stats=stats,
        filtros={
            "tipo": tipo_filtro,
            "setor": setor_filtro
        }
    )


@bp.route('/transactions', methods=['GET'])
@login_required
def transactions():
    """Transações Integrado (Correção M7.2)"""
    token = session.get('access_token')
    
    # Estrutura inicial de stats
    stats = {
        'total': 0,
        'compras': 0,
        'vendas': 0,
        'volume_total': 0.0,
        'volume_compras': 0.0,
        'volume_vendas': 0.0,
        'volume_acoes': 0.0,
        'volume_fii': 0.0,
        'volume_cripto': 0.0,
        'volume_outros': 0.0
    }
    
    # Estrutura inicial de filtros
    filtros = {
        'tipo': '',
        'classe': '',
        'mercado': '',
        'corretora_id': '',
        'data_inicio': '',
        'data_fim': ''
    }
    
    transacoes = []
    
    # Listas auxiliares para os filtros da tela
    corretoras = []
    tipos_ativo = [
        {'value': 'ACAO', 'label': 'Ações'}, 
        {'value': 'FII', 'label': 'FIIs'}, 
        {'value': 'ETF', 'label': 'ETFs'}, 
        {'value': 'BDR', 'label': 'BDRs'}, 
        {'value': 'CRIPTO', 'label': 'Cripto'}
    ]
    classes_ativo = [
        {'value': 'Renda Variável', 'label': 'Renda Variável'}, 
        {'value': 'Renda Fixa', 'label': 'Renda Fixa'}
    ]
    mercados = [
        {'value': 'BR', 'label': 'Brasil'}, 
        {'value': 'US', 'label': 'EUA'}
    ]

    if token:
        try:
            headers = {'Authorization': f"Bearer {token}"}
            # Removemos a barra final para evitar redirecionamentos (308)
            response = requests.get(f"{Config.BACKEND_API_URL}/api/transacoes", headers=headers, timeout=5)
            
            if response.status_code == 200:
                payload = response.json()
                
                # --- PARSING ROBUSTO (M7.2) ---
                # 1. Tenta pegar 'data'
                payload_data = payload.get('data', {})
                
                # 2. Extrai a lista real de transações, lidando com paginação
                if isinstance(payload_data, dict):
                    # Padrão novo: { data: { transacoes: [], total: 17, ... } }
                    raw_data = payload_data.get('transacoes', [])
                elif isinstance(payload_data, list):
                    # Padrão antigo: { data: [] }
                    raw_data = payload_data
                else:
                    raw_data = []
                
                for item in raw_data:
                    # Parsing seguro de objetos aninhados
                    ativo_obj = item.get('ativo') or {}
                    corretora_obj = item.get('corretora') or {}
                    
                    # Normalização de dados
                    ticker = ativo_obj.get('ticker', 'N/A')
                    tipo_ativo_str = ativo_obj.get('tipo', 'OUTROS').upper()
                    mercado = (ativo_obj.get('mercado') or 'BR').upper()
                    moeda = 'R$' if mercado == 'BR' else '$'
                    
                    # Normalização de tipo de operação (template espera lowercase 'compra'/'venda')
                    tipo_raw = (item.get('tipo') or 'COMPRA').lower()
                    
                    # Valores numéricos seguros
                    qtd = float(item.get('quantidade') or 0)
                    preco_unit = float(item.get('preco_unitario') or 0)
                    # Prioriza valor_total da API, senão calcula
                    valor_total = float(item.get('valor_total') or (qtd * preco_unit))
                    
                    # Monta objeto compatível com o template (incluindo aliases)
                    transacao_dict = {
                        # Datas
                        'data': item.get('data_transacao'),
                        'data_transacao': item.get('data_transacao'),
                        
                        # Operação
                        'tipo_operacao': tipo_raw,  # snake_case
                        'tipooperacao': tipo_raw,   # compatibilidade
                        
                        # Objetos aninhados (para acesso via ponto: trans.ativo.ticker)
                        'ativo': ativo_obj,
                        'corretora': corretora_obj,
                        
                        # Valores
                        'quantidade': qtd,
                        'preco_unitario': preco_unit, # snake_case
                        'precounitario': preco_unit,  # compatibilidade
                        'valor_total': valor_total,   # snake_case
                        'valortotal': valor_total,    # compatibilidade
                        
                        # Extras UI
                        'moeda': moeda
                    }
                    
                    transacoes.append(transacao_dict)
                    
                    # --- Atualiza Stats ---
                    stats['total'] += 1
                    stats['volume_total'] += valor_total
                    
                    if tipo_raw == 'compra':
                        stats['compras'] += 1
                        stats['volume_compras'] += valor_total
                    elif tipo_raw == 'venda':
                        stats['vendas'] += 1
                        stats['volume_vendas'] += valor_total
                        
                    # Stats por tipo de ativo
                    if 'ACAO' in tipo_ativo_str:
                        stats['volume_acoes'] += valor_total
                    elif 'FII' in tipo_ativo_str:
                        stats['volume_fii'] += valor_total
                    elif 'CRIPTO' in tipo_ativo_str:
                        stats['volume_cripto'] += valor_total
                    else:
                        stats['volume_outros'] += valor_total

        except Exception as e:
            print(f"Erro transactions: {e}")
            flash('Erro ao carregar transações.', 'error')

    # Renderiza template passando todas as variáveis
    return render_template('dashboard/transactions.html',
                         stats=stats,
                         transacoes=transacoes,
                         filtros=filtros,
                         corretoras=corretoras,
                         tipos_ativo=tipos_ativo,
                         classes_ativo=classes_ativo,
                         mercados=mercados)



@bp.route('/dividends')
@login_required
def dividends():
    """Proventos Integrado"""
    token = session.get('access_token')
    
    stats = {
        "total": 0,
        "recebido": 0.0,
        "previsto": 0.0,
        "total_geral": 0.0,
    }

    filtros = {
        "status": "todos",
        "tipo": "todos",
        "periodo": "12m",
        "ativo": "",
        "corretora": "",
        "datainicio": "",
        "datafim": "",
    }

    proventos = []
    
    if token:
        try:
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get(
                f'{Config.BACKEND_API_URL}/api/proventos',
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                payload = response.json()
                raw_data = payload.get('data', [])
                
                for item in raw_data:
                    # Parsing seguro para campo nested ativo
                    ativo_obj = item.get('ativo', {})
                    if isinstance(ativo_obj, dict):
                        ticker = ativo_obj.get('ticker', 'N/A')
                    else:
                        ticker = 'N/A'
                    
                    valor = float(item.get('valor_liquido') or item.get('valor_bruto') or 0)
                    status = item.get('status', 'PREVISTO')
                    
                    proventos.append({
                        'data_pagamento': item.get('data_pagamento'),
                        'ativo': ticker,
                        'tipo': item.get('tipo_provento'),
                        'valor': valor,
                        'status': status
                    })
                    
                    stats['total'] += 1
                    stats['total_geral'] += valor
                    if status == 'PAGO':
                        stats['recebido'] += valor
                    else:
                        stats['previsto'] += valor
                        
        except Exception as e:
            print(f"Erro dividends: {e}")

    ativos = []
    corretoras = []
    tiposprovento = []
    dividendstimeline = []

    return render_template(
        'dashboard/dividends.html',
        stats=stats,
        proventos=proventos,
        filtros=filtros,
        ativos=ativos,
        corretoras=corretoras,
        tiposprovento=tiposprovento,
        dividendstimeline=dividendstimeline,
    )


@bp.route('/reports')
@login_required
def reports():
    return render_template('dashboard/reports.html')


@bp.route('/analytics')
@login_required
def analytics():
    return render_template('dashboard/analytics.html')


@bp.route('/alerts', methods=['GET'])
@login_required
def alerts():
    token = session.get('access_token')
    alertas = []
    stats = {'total': 0, 'ativos': 0, 'alta_preco': 0, 'acionados': 0}

    tipo = request.args.get('tipo')
    status = request.args.get('status')
    ativo = request.args.get('ativo')

    if token:
        try:
            headers = {'Authorization': f'Bearer {token}'}
            params = {}
            if tipo and tipo != 'Todos': params['tipo_alerta'] = tipo
            if status and status != 'Todos': params['ativo'] = 'true' if status == 'ativo' else 'false'

            response = requests.get(
                f'{Config.BACKEND_API_URL}/api/alertas/',
                headers=headers, params=params, timeout=5
            )

            if response.status_code == 200:
                payload = response.json()
                alertas = payload.get('data', [])

                stats['total'] = len(alertas)
                stats['ativos'] = len([a for a in alertas if a.get('ativo')])
                stats['alta_preco'] = len([a for a in alertas if str(a.get('tipo_alerta') or '').upper() == 'ALTA_PRECO'])
                stats['acionados'] = len([a for a in alertas if a.get('foi_acionado')])

        except Exception as e:
            print(f"Erro ao buscar alertas: {e}")
            flash('Erro ao carregar alertas.', 'error')

    ativos_unicos = sorted(list(set(a.get('ticker') for a in alertas if a.get('ticker'))))

    return render_template(
        'dashboard/alerts.html',
        alertas=alertas,
        stats=stats,
        filtros={'tipo': tipo, 'status': status, 'ativo': ativo},
        ativos=ativos_unicos
    )


@bp.route('/alerts/create', methods=['POST'])
@login_required
def alerts_create():
    try:
        token = session.get('access_token')

        val_str = request.form.get('condicaovalor', '0').replace(',', '.')
        val2_str = request.form.get('condicaovalor2', '').replace(',', '.')

        payload = {
            "nome": request.form.get('nome'),
            "tipo_alerta": request.form.get('tipoalerta'),
            "ticker": request.form.get('ticker') or None,
            "condicao_operador": request.form.get('condicaooperador'),
            "condicao_valor": float(val_str),
            "condicao_valor2": float(val2_str) if val2_str else None,
            "frequencia_notificacao": request.form.get('frequencianotificacao'),
            "canais_entrega": request.form.getlist('canais'),
            "ativo": True
        }

        headers = {'Authorization': f'Bearer {token}'}
        response = requests.post(
            f'{Config.BACKEND_API_URL}/api/alertas/',
            json=payload, headers=headers, timeout=10
        )

        if response.status_code in [200, 201]:
            flash('✅ Alerta criado com sucesso!', 'success')
        else:
            flash(f'Erro ({response.status_code}): {response.text}', 'error')

    except Exception as e:
        flash(f'Erro de sistema: {str(e)}', 'error')

    return redirect(url_for('dashboard.alerts'))


@bp.route('/alerts/toggle/<alert_id>', methods=['POST'])
@login_required
def alerts_toggle(alert_id):
    token = session.get('access_token')
    headers = {'Authorization': f'Bearer {token}'}
    requests.patch(f'{Config.BACKEND_API_URL}/api/alertas/{alert_id}/toggle', headers=headers)
    return redirect(url_for('dashboard.alerts'))


@bp.route('/alerts/delete/<alert_id>', methods=['POST'])
@login_required
def alerts_delete(alert_id):
    token = session.get('access_token')
    headers = {'Authorization': f'Bearer {token}'}
    requests.delete(f'{Config.BACKEND_API_URL}/api/alertas/{alert_id}', headers=headers)
    return redirect(url_for('dashboard.alerts'))
