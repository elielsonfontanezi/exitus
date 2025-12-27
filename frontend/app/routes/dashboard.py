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
    """Proventos Integrado - Alinhado com o template M6"""
    from collections import defaultdict
    from datetime import datetime

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
    dividendstimeline = []
    ativos = []
    corretoras = []
    tiposprovento = []

    if token:
        try:
            headers = {"Authorization": f"Bearer {token}"}
            resp = requests.get(
                f"{Config.BACKEND_API_URL}/api/proventos?per_page=100",
                headers=headers,
                timeout=5,
            )

            if resp.status_code == 200:
                payload = resp.json()
                data_container = payload.get("data", {})
                raw_data = (
                    data_container
                    if isinstance(data_container, list)
                    else data_container.get("proventos", [])
                )

                timeline = defaultdict(float)

                for item in raw_data:
                    data_pag = item.get("data_pagamento")
                    data_com = item.get("data_com")

                    # Tipo vem como "TipoProvento.DIVIDENDO" etc.
                    raw_tipo = item.get("tipo_provento", "TipoProvento.DIVIDENDO")
                    tipo = raw_tipo.split(".")[-1]  # DIVIDENDO / RENDIMENTO / JCP etc.

                    valor = float(item.get("valor_liquido") or item.get("valor_bruto") or 0.0)
                    valor_unitario = float(item.get("valor_por_acao") or 0.0)

                    # Template espera 'ativo' como objeto com ticker/nome
                    ticker_label = f"ID {str(item.get('ativo_id'))[:4]}"
                    ativo_obj = {
                        "ticker": ticker_label,
                        "nome": ticker_label,
                    }

                    # Status: inferido pela data de pagamento
                    status = "PREVISTO"
                    if data_pag:
                        try:
                            dt_pag = datetime.strptime(data_pag, "%Y-%m-%d")
                            if dt_pag <= datetime.now():
                                status = "PAGO"
                        except Exception:
                            pass

                    quantidade = item.get("quantidade", 0)

                    proventos.append(
                        {
                            "datacom": data_com,
                            "datapagamento": data_pag,
                            "ativo": ativo_obj,
                            "tipo": tipo,
                            "moeda": "R$",
                            "valor_unitario": valor_unitario,
                            "quantidade": quantidade,
                            "valor_total": valor,
                            "status": status,
                        }
                    )

                    stats["total"] += 1
                    stats["total_geral"] += valor
                    if status == "PAGO":
                        stats["recebido"] += valor
                    else:
                        stats["previsto"] += valor

                    # Timeline por mês (usa data_pagamento ou data_com)
                    d_ref = data_pag or data_com
                    if d_ref:
                        chave = d_ref[:7]  # YYYY-MM
                        timeline[chave] += valor

                dividendstimeline = [
                    {"mes": k, "valor": v} for k, v in sorted(timeline.items())
                ]

        except Exception as e:
            print(f"Erro dividends: {e}")

    return render_template(
        "dashboard/dividends.html",
        stats=stats,
        proventos=proventos,
        filtros=filtros,
        ativos=ativos,
        corretoras=corretoras,
        tiposprovento=tiposprovento,
        dividendstimeline=dividendstimeline,
    )




@bp.route('/reports', methods=['GET'])
@login_required
def reports():
    """Relatórios e Auditoria - M7.4 Integrado"""
    token = session.get('access_token')
    
    # Paginação
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    relatorios = []
    pagination = {'page': 1, 'pages': 1, 'total': 0}

    if token:
        try:
            headers = {'Authorization': f"Bearer {token}"}
            # Padronização sem barra final
            url = f"{Config.BACKEND_API_URL}/api/relatorios/lista"
            
            params = {'page': page, 'perpage': per_page}
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                payload = response.json()
                # A API retorna { "relatorios": [...], "total": N, "pages": N, ... } na raiz ou dentro de data?
                # Pelo seu curl: { "relatorios": [...], "current_page": 1, ... } (na raiz)
                
                # Adaptação para garantir leitura correta
                data_source = payload if 'relatorios' in payload else payload.get('data', {})
                
                raw_relatorios = data_source.get('relatorios', [])
                pagination = {
                    'page': data_source.get('current_page', page),
                    'pages': data_source.get('pages', 1),
                    'total': data_source.get('total', len(raw_relatorios))
                }

                for item in raw_relatorios:
                    # Formata dados para exibição
                    tipo = item.get('tipo_relatorio', 'N/A').upper()
                    periodo = item.get('resultado_json', {}).get('periodo') or 'N/A'
                    
                    # Tenta formatar data de criação
                    criado_em = item.get('timestamp_criacao')
                    try:
                        # Ex: 2025-12-12T11:15:11.041026+00:00 -> 12/12/2025 11:15
                        dt = datetime.fromisoformat(criado_em.replace('Z', '+00:00'))
                        criado_fmt = dt.strftime('%d/%m/%Y %H:%M')
                    except:
                        criado_fmt = criado_em

                    relatorios.append({
                        'id': item.get('id'),
                        'tipo': tipo,
                        'periodo': periodo,
                        'criado_em': criado_fmt,
                        'formato': item.get('formato_export', 'visualizacao'),
                        'status': 'Disponível'
                    })

        except Exception as e:
            print(f"[ERROR] Reports Route: {e}")
            flash('Erro ao carregar lista de relatórios.', 'error')

    return render_template('dashboard/reports.html',
                         relatorios=relatorios,
                         pagination=pagination)

@bp.route('/reports/generate', methods=['POST'])
@login_required
def reports_generate():
    """Gera novo relatório via API"""
    token = session.get('access_token')
    tipo = request.form.get('tipo')
    
    payload = {
        'tipo': tipo,
        'filtros': {}
    }
    
    # Se for PERFORMANCE, adiciona datas (pode pegar do form ou fixar últimos 30 dias por enquanto)
    if tipo == 'PERFORMANCE':
        # Simplificação: pega mês atual se não vier no form
        hoje = datetime.now()
        inicio_mes = hoje.replace(day=1).strftime('%Y-%m-%d')
        fim_mes = hoje.strftime('%Y-%m-%d')
        
        payload['datainicio'] = request.form.get('datainicio') or inicio_mes
        payload['datafim'] = request.form.get('datafim') or fim_mes

    if token:
        try:
            headers = {
                'Authorization': f"Bearer {token}",
                'Content-Type': 'application/json'
            }
            url = f"{Config.BACKEND_API_URL}/api/relatorios/gerar"
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code in [200, 201]:
                flash('Relatório gerado com sucesso!', 'success')
            else:
                flash(f'Erro ao gerar relatório: {response.text}', 'error')
                
        except Exception as e:
            flash(f'Erro de conexão: {str(e)}', 'error')
            
    return redirect(url_for('dashboard.reports'))

@bp.route('/reports/delete/<id>', methods=['POST'])
@login_required
def reports_delete(id):
    """Deleta relatório"""
    token = session.get('access_token')
    if token:
        try:
            headers = {'Authorization': f"Bearer {token}"}
            url = f"{Config.BACKEND_API_URL}/api/relatorios/{id}"
            requests.delete(url, headers=headers)
            flash('Relatório removido.', 'success')
        except:
            flash('Erro ao deletar.', 'error')
            
    return redirect(url_for('dashboard.reports'))

@bp.route('/reports/<id>', methods=['GET'])
@login_required
def reports_view(id):
    """Visualizar detalhes de um relatório específico"""
    token = session.get('access_token')
    relatorio = None
    
    if token:
        try:
            headers = {'Authorization': f"Bearer {token}"}
            url = f"{Config.BACKEND_API_URL}/api/relatorios/{id}"
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                relatorio = response.json()
            else:
                flash('Relatório não encontrado.', 'error')
                return redirect(url_for('dashboard.reports'))
                
        except Exception as e:
            flash(f'Erro ao carregar relatório: {str(e)}', 'error')
            return redirect(url_for('dashboard.reports'))
    
    # Renderiza um template simples de visualização (JSON pretty print)
    return render_template('dashboard/report_detail.html', relatorio=relatorio)


@bp.route('/analytics')
@login_required
def analytics():
    return render_template('dashboard/analytics.html')

@bp.route('/alerts', methods=['GET'])
@login_required
def alerts():
    """Alertas Integrado (Correção M7.3 - Campos Template)"""
    token = session.get('access_token')
    
    # Stats iniciais
    stats = {
        'total': 0,
        'ativos': 0,
        'alta_preco': 0,
        'acionados': 0
    }
    
    alertas = []
    ativos_unicos = [] 
    
    # Filtros
    tipo_filtro = request.args.get('tipo')
    status_filtro = request.args.get('status')
    ativo_filtro = request.args.get('ativo')

    if token:
        try:
            headers = {'Authorization': f"Bearer {token}"}
            params = {}
            
            if tipo_filtro and tipo_filtro != 'Todos':
                params['tipo_alerta'] = tipo_filtro
            if status_filtro and status_filtro != 'Todos':
                params['ativo'] = 'true' if status_filtro == 'Ativo' else 'false'
            if ativo_filtro:
                params['ticker'] = ativo_filtro

            # URL Padronizada (sem barra)
            url = f"{Config.BACKEND_API_URL}/api/alertas"
            
            # Debug
            print(f"[DEBUG] Requesting Alerts: {url}")
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                payload = response.json()
                # Extração robusta da lista
                payload_data = payload.get('data', [])
                if isinstance(payload_data, dict):
                    raw_alertas = payload_data.get('alertas', [])
                elif isinstance(payload_data, list):
                    raw_alertas = payload_data
                else:
                    raw_alertas = []

                print(f"[DEBUG] Alerts Found: {len(raw_alertas)}")

                for item in raw_alertas:
                    ticker = item.get('ticker') or 'GERAL'
                    ativo_flag = item.get('ativo', True)
                    foi_acionado = item.get('foi_acionado', False)
                    tipo_alerta = item.get('tipo_alerta', 'OUTROS')
                    
                    # Valores brutos para o template
                    cond_op = item.get('condicao_operador', '')
                    cond_val = float(item.get('condicao_valor') or 0.0)
                    
                    alerta_dict = {
                        'id': item.get('id'),
                        'nome': item.get('nome'),
                        
                        # Tipos
                        'tipo': tipo_alerta,
                        'tipo_alerta': tipo_alerta,
                        
                        # Ativo
                        'ticker': ticker,
                        'ativo_ticker': ticker,
                        
                        # Condição (RAW + Formatada)
                        'condicao': f"{cond_op} {cond_val}",
                        'condicao_operador': cond_op,    # <--- O que faltava
                        'condicao_valor': cond_val,      # <--- O que faltava
                        
                        # Status
                        'ativo': ativo_flag,
                        'status': 'ATIVO' if ativo_flag else 'INATIVO',
                        
                        # Disparos
                        'foi_acionado': foi_acionado,
                        'disparos': item.get('contagem_disparos', 0) if foi_acionado else 0,
                        'ultimo_disparo': item.get('data_ultimo_disparo'),
                        'created_at': item.get('created_at')
                    }
                    
                    alertas.append(alerta_dict)
                    
                    if ticker and ticker != 'GERAL' and ticker not in ativos_unicos:
                        ativos_unicos.append(ticker)

                    # Stats
                    stats['total'] += 1
                    if ativo_flag: stats['ativos'] += 1
                    if 'ALTA' in str(tipo_alerta).upper(): stats['alta_preco'] += 1
                    if foi_acionado: stats['acionados'] += 1

        except Exception as e:
            print(f"[ERROR] Alerts Route: {e}")
            flash('Erro ao carregar alertas.', 'error')
            
    ativos_unicos.sort()

    return render_template('dashboard/alerts.html',
                         alertas=alertas,
                         stats=stats,
                         filtros={'tipo': tipo_filtro, 'status': status_filtro, 'ativo': ativo_filtro},
                         ativos=ativos_unicos)



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
