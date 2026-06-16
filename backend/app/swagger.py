# -*- coding: utf-8 -*-
"""
Exitus - OpenAPI / Swagger (EXITUS-SWAGGER-001)
Auto-documentação via flask-restx.

UI disponível em: GET /api/docs
Spec JSON em:    GET /api/swagger.json

Namespaces documentados:
  auth        — /api/auth      (login, refresh, me)
  ativos      — /api/ativos    (CRUD de ativos)
  transacoes  — /api/transacoes (CRUD + filtros)
  ir          — /api/ir        (apuração, DARF, histórico, DIRPF)
  export      — /api/export    (CSV, Excel, JSON, PDF)
"""

from flask import Blueprint
from flask_restx import Api, Namespace, Resource, fields

# ---------------------------------------------------------------------------
# Instância principal
# ---------------------------------------------------------------------------

authorizations = {
    'Bearer': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': 'JWT token. Formato: **Bearer &lt;token&gt;**',
    }
}

_swagger_bp = Blueprint('swagger', __name__)

api = Api(
    _swagger_bp,
    title='Exitus API',
    version='1.6',
    description=(
        'API de gestão e análise de investimentos. '
        'Autenticação via JWT Bearer token — obtenha o token em POST /api/auth/login.'
    ),
    doc='/docs',
    authorizations=authorizations,
    security='Bearer',
)

# ---------------------------------------------------------------------------
# Modelos de resposta compartilhados
# ---------------------------------------------------------------------------

_envelope = api.model('Envelope', {
    'success': fields.Boolean(description='Indicador de sucesso'),
    'message': fields.String(description='Mensagem descritiva'),
    'data':    fields.Raw(description='Payload da resposta'),
})

_erro = api.model('Erro', {
    'success': fields.Boolean(description='Sempre false em erros', example=False),
    'message': fields.String(description='Descrição do erro'),
})

# ---------------------------------------------------------------------------
# Namespace: Auth
# ---------------------------------------------------------------------------

ns_auth = Namespace('auth', description='Autenticação e tokens JWT', path='/auth')

_login_input = ns_auth.model('LoginInput', {
    'username': fields.String(required=True, description='Nome de usuário ou e-mail', example='admin'),
    'password': fields.String(required=True, description='Senha', example='senha123'),
})

_login_data = ns_auth.model('LoginData', {
    'access_token':  fields.String(description='JWT de acesso (validade 1h)'),
    'refresh_token': fields.String(description='JWT de refresh (validade 30d)'),
    'user': fields.Raw(description='Dados básicos do usuário autenticado'),
})

_login_response = ns_auth.model('LoginResponse', {
    'success': fields.Boolean(example=True),
    'message': fields.String(example='Login realizado com sucesso'),
    'data':    fields.Nested(_login_data),
})


@ns_auth.route('/login')
class AuthLogin(Resource):
    @ns_auth.doc('login', security=[])
    @ns_auth.expect(_login_input)
    @ns_auth.response(200, 'Sucesso', _login_response)
    @ns_auth.response(400, 'Dados inválidos', _erro)
    @ns_auth.response(401, 'Credenciais inválidas', _erro)
    def post(self):
        """Login e geração de tokens JWT."""
        pass


@ns_auth.route('/refresh')
class AuthRefresh(Resource):
    @ns_auth.doc('refresh')
    @ns_auth.response(200, 'Token renovado', _envelope)
    @ns_auth.response(401, 'Refresh token inválido', _erro)
    def post(self):
        """Renova o access_token usando o refresh_token."""
        pass


@ns_auth.route('/me')
class AuthMe(Resource):
    @ns_auth.doc('me')
    @ns_auth.response(200, 'Dados do usuário autenticado', _envelope)
    @ns_auth.response(401, 'Não autenticado', _erro)
    def get(self):
        """Retorna dados do usuário autenticado."""
        pass


@ns_auth.route('/logout')
class AuthLogout(Resource):
    @ns_auth.doc('logout')
    @ns_auth.response(200, 'Logout realizado', _envelope)
    def post(self):
        """Invalida o refresh token (logout)."""
        pass


# ---------------------------------------------------------------------------
# Namespace: Ativos
# ---------------------------------------------------------------------------

ns_ativos = Namespace('ativos', description='Cadastro de ativos financeiros', path='/ativos')

_ativo = ns_ativos.model('Ativo', {
    'id':      fields.String(description='UUID do ativo'),
    'ticker':  fields.String(description='Código de negociação', example='PETR4'),
    'nome':    fields.String(description='Nome do ativo', example='Petrobras PN'),
    'tipo':    fields.String(description='Tipo: ACAO, FII, ETF, BDR, STOCK_US, ...'),
    'mercado': fields.String(description='Mercado: BR ou US', example='BR'),
    'ativo':   fields.Boolean(description='Se o ativo está ativo/negociado'),
})

_ativo_input = ns_ativos.model('AtivoInput', {
    'ticker':  fields.String(required=True, example='PETR4'),
    'nome':    fields.String(required=True, example='Petrobras PN'),
    'tipo':    fields.String(required=True, example='ACAO'),
    'mercado': fields.String(required=True, example='BR'),
})

_ativos_list = ns_ativos.model('AtivosList', {
    'ativos':   fields.List(fields.Nested(_ativo)),
    'total':    fields.Integer(description='Total de registros'),
    'pages':    fields.Integer(description='Total de páginas'),
    'page':     fields.Integer(description='Página atual'),
    'per_page': fields.Integer(description='Registros por página'),
})


@ns_ativos.route('/')
class AtivosList(Resource):
    @ns_ativos.doc('list_ativos', params={
        'page':      {'description': 'Página', 'type': 'int', 'default': 1},
        'per_page':  {'description': 'Registros por página', 'type': 'int', 'default': 20},
        'tipo':      {'description': 'Filtro por tipo (ACAO, FII, ETF, ...)', 'type': 'str'},
        'mercado':   {'description': 'Filtro por mercado (BR, US)', 'type': 'str'},
        'search':    {'description': 'Busca por ticker ou nome', 'type': 'str'},
    })
    @ns_ativos.response(200, 'Lista de ativos', _ativos_list)
    @ns_ativos.response(401, 'Não autenticado', _erro)
    def get(self):
        """Lista ativos com filtros e paginação."""
        pass

    @ns_ativos.doc('create_ativo')
    @ns_ativos.expect(_ativo_input)
    @ns_ativos.response(201, 'Ativo criado', _envelope)
    @ns_ativos.response(400, 'Dados inválidos', _erro)
    @ns_ativos.response(403, 'Permissão negada (admin only)', _erro)
    def post(self):
        """Criar novo ativo (requer perfil admin)."""
        pass


@ns_ativos.route('/<string:id>')
@ns_ativos.param('id', 'UUID do ativo')
class AtivosDetail(Resource):
    @ns_ativos.doc('get_ativo')
    @ns_ativos.response(200, 'Dados do ativo', _envelope)
    @ns_ativos.response(404, 'Ativo não encontrado', _erro)
    def get(self, id):
        """Buscar ativo por ID."""
        pass

    @ns_ativos.doc('update_ativo')
    @ns_ativos.expect(_ativo_input)
    @ns_ativos.response(200, 'Ativo atualizado', _envelope)
    @ns_ativos.response(403, 'Permissão negada (admin only)', _erro)
    def put(self, id):
        """Atualizar ativo (requer perfil admin)."""
        pass

    @ns_ativos.doc('delete_ativo')
    @ns_ativos.response(200, 'Ativo removido', _envelope)
    @ns_ativos.response(403, 'Permissão negada (admin only)', _erro)
    @ns_ativos.response(404, 'Ativo não encontrado', _erro)
    def delete(self, id):
        """Remover ativo (requer perfil admin)."""
        pass


@ns_ativos.route('/ticker/<string:ticker>')
@ns_ativos.param('ticker', 'Código de negociação (ex: PETR4)')
class AtivosByTicker(Resource):
    @ns_ativos.doc('get_by_ticker', params={
        'mercado': {'description': 'Mercado (BR ou US)', 'type': 'str', 'default': 'BR'},
    })
    @ns_ativos.response(200, 'Dados do ativo', _envelope)
    @ns_ativos.response(404, 'Ativo não encontrado', _erro)
    def get(self, ticker):
        """Buscar ativo por ticker e mercado."""
        pass


# ---------------------------------------------------------------------------
# Namespace: Transações
# ---------------------------------------------------------------------------

ns_transacoes = Namespace('transacoes', description='Registro de operações (compra, venda, proventos)', path='/transacoes')

_transacao = ns_transacoes.model('Transacao', {
    'id':             fields.String(description='UUID da transação'),
    'ativo_id':       fields.String(description='UUID do ativo'),
    'corretora_id':   fields.String(description='UUID da corretora'),
    'tipo':           fields.String(description='Tipo: compra, venda, dividendo, jcp, aluguel'),
    'data_transacao': fields.String(description='Data/hora da operação (ISO 8601)'),
    'quantidade':     fields.Float(description='Quantidade negociada'),
    'preco_unitario': fields.Float(description='Preço por unidade'),
    'valor_total':    fields.Float(description='Valor total bruto'),
    'custos_totais':  fields.Float(description='Custos e corretagem'),
    'valor_liquido':  fields.Float(description='Valor líquido (total ± custos)'),
})

_transacao_input = ns_transacoes.model('TransacaoInput', {
    'ativo_id':       fields.String(required=True, description='UUID do ativo'),
    'corretora_id':   fields.String(required=True, description='UUID da corretora'),
    'tipo':           fields.String(required=True, description='compra | venda | dividendo | jcp | aluguel'),
    'data_transacao': fields.String(required=True, description='ISO 8601: 2025-03-15T10:00:00'),
    'quantidade':     fields.Float(required=True, description='Quantidade'),
    'preco_unitario': fields.Float(required=True, description='Preço unitário'),
    'custos_totais':  fields.Float(description='Custos totais (default 0)'),
})


@ns_transacoes.route('')
class TransacoesList(Resource):
    @ns_transacoes.doc('list_transacoes', params={
        'page':         {'description': 'Página', 'type': 'int', 'default': 1},
        'per_page':     {'description': 'Registros por página', 'type': 'int', 'default': 20},
        'tipo':         {'description': 'Filtro por tipo (compra, venda, ...)', 'type': 'str'},
        'ativo_id':     {'description': 'Filtro por UUID do ativo', 'type': 'str'},
        'corretora_id': {'description': 'Filtro por UUID da corretora', 'type': 'str'},
        'data_inicio':  {'description': 'Data início (YYYY-MM-DD)', 'type': 'str'},
        'data_fim':     {'description': 'Data fim (YYYY-MM-DD)', 'type': 'str'},
    })
    @ns_transacoes.response(200, 'Lista de transações', _envelope)
    @ns_transacoes.response(401, 'Não autenticado', _erro)
    def get(self):
        """Lista transações do usuário com filtros e paginação."""
        pass

    @ns_transacoes.doc('create_transacao')
    @ns_transacoes.expect(_transacao_input)
    @ns_transacoes.response(201, 'Transação registrada', _envelope)
    @ns_transacoes.response(400, 'Dados inválidos', _erro)
    def post(self):
        """Registrar nova transação."""
        pass


@ns_transacoes.route('/<string:id>')
@ns_transacoes.param('id', 'UUID da transação')
class TransacoesDetail(Resource):
    @ns_transacoes.doc('get_transacao')
    @ns_transacoes.response(200, 'Dados da transação', _envelope)
    @ns_transacoes.response(404, 'Transação não encontrada', _erro)
    def get(self, id):
        """Buscar transação por ID."""
        pass

    @ns_transacoes.doc('update_transacao')
    @ns_transacoes.expect(_transacao_input)
    @ns_transacoes.response(200, 'Transação atualizada', _envelope)
    @ns_transacoes.response(403, 'Permissão negada', _erro)
    def put(self, id):
        """Atualizar transação."""
        pass

    @ns_transacoes.doc('delete_transacao')
    @ns_transacoes.response(200, 'Transação removida', _envelope)
    @ns_transacoes.response(403, 'Permissão negada', _erro)
    @ns_transacoes.response(404, 'Transação não encontrada', _erro)
    def delete(self, id):
        """Remover transação."""
        pass


# ---------------------------------------------------------------------------
# Namespace: IR (Imposto de Renda)
# ---------------------------------------------------------------------------

ns_ir = Namespace('ir', description='Apuração de IR sobre renda variável (IR-001 a IR-007, IR-009)', path='/ir')

_ir_categoria = ns_ir.model('IRCategoria', {
    'lucro_liquido':       fields.Float(description='Lucro líquido após compensação de prejuízo'),
    'ir_devido':           fields.Float(description='IR calculado para esta categoria'),
    'aliquota':            fields.Float(description='Alíquota aplicada (%)'),
    'operacoes':           fields.Integer(description='Número de operações no mês'),
    'isento':              fields.Boolean(description='Se há isenção (ex: vendas <R$20k em ações)'),
    'prejuizo_acumulado':  fields.Float(description='Saldo de prejuízo após o mês'),
    'prejuizo_compensado': fields.Float(description='Prejuízo compensado neste mês'),
})

_ir_proventos = ns_ir.model('IRProventos', {
    'valor_bruto': fields.Float(description='Valor bruto recebido'),
    'ir_retido':   fields.Float(description='IR retido na fonte'),
    'ir_esperado': fields.Float(description='IR calculado pelo sistema'),
    'operacoes':   fields.Integer(description='Número de lançamentos'),
})

_ir_apuracao = ns_ir.model('IRApuracao', {
    'mes':        fields.String(description='Mês de referência (YYYY-MM)', example='2025-03'),
    'usuario_id': fields.String(description='UUID do usuário'),
    'categorias': fields.Raw(description='Breakdown por categoria (swing_acoes, day_trade, fiis, exterior)'),
    'proventos':  fields.Raw(description='Proventos do mês (dividendos_br, jcp, dividendos_us, aluguel)'),
    'ir_total':   fields.Float(description='IR total devido no mês'),
    'darf':       fields.List(fields.Raw(), description='DARFs a pagar'),
    'alertas':    fields.List(fields.String(), description='Alertas e observações fiscais'),
})

_dirpf = ns_ir.model('DIRPF', {
    'ano':                    fields.Integer(description='Ano-calendário', example=2025),
    'usuario_id':             fields.String(description='UUID do usuário'),
    'renda_variavel':         fields.Raw(description='Fichas de renda variável por categoria'),
    'proventos':              fields.Raw(description='Proventos recebidos no ano'),
    'bens_e_direitos':        fields.Raw(description='Posições em carteira ao 31/dez'),
    'ir_total_ano':           fields.Float(description='IR total pago no ano'),
    'prejuizo_remanescente':  fields.Raw(description='Saldos de prejuízo compensável ao final do ano'),
    'obs':                    fields.String(description='Orientações de preenchimento DIRPF'),
})


@ns_ir.route('/apuracao')
class IRApuracao(Resource):
    @ns_ir.doc('apuracao', params={
        'mes': {'description': 'Mês de referência no formato YYYY-MM', 'type': 'str', 'required': True, 'example': '2025-03'},
    })
    @ns_ir.response(200, 'Apuração detalhada', _ir_apuracao)
    @ns_ir.response(400, 'Parâmetro inválido ou ausente', _erro)
    @ns_ir.response(401, 'Não autenticado', _erro)
    def get(self):
        """Apuração detalhada de IR por categoria para o mês informado."""
        pass


@ns_ir.route('/darf')
class IRDarf(Resource):
    @ns_ir.doc('darf', params={
        'mes': {'description': 'Mês de referência no formato YYYY-MM', 'type': 'str', 'required': True, 'example': '2025-03'},
    })
    @ns_ir.response(200, 'DARFs a pagar no mês', _envelope)
    @ns_ir.response(400, 'Parâmetro inválido ou ausente', _erro)
    @ns_ir.response(401, 'Não autenticado', _erro)
    def get(self):
        """DARFs a pagar no mês informado (código de receita, valor, status)."""
        pass


@ns_ir.route('/historico')
class IRHistorico(Resource):
    @ns_ir.doc('historico', params={
        'ano': {'description': 'Ano inteiro (ex: 2025)', 'type': 'int', 'required': True, 'example': 2025},
    })
    @ns_ir.response(200, 'Resumo anual mês a mês', _envelope)
    @ns_ir.response(400, 'Parâmetro inválido ou ausente', _erro)
    @ns_ir.response(401, 'Não autenticado', _erro)
    def get(self):
        """Resumo de apuração IR mês a mês para o ano informado."""
        pass


@ns_ir.route('/dirpf')
class IRDirpf(Resource):
    @ns_ir.doc('dirpf', params={
        'ano': {'description': 'Ano-calendário (ex: 2025)', 'type': 'int', 'required': True, 'example': 2025},
    })
    @ns_ir.response(200, 'Relatório DIRPF anual', _dirpf)
    @ns_ir.response(400, 'Parâmetro inválido ou ausente', _erro)
    @ns_ir.response(401, 'Não autenticado', _erro)
    def get(self):
        """Relatório DIRPF anual: Renda Variável, Proventos e Bens e Direitos."""
        pass


# ---------------------------------------------------------------------------
# Namespace: Export
# ---------------------------------------------------------------------------

ns_export = Namespace('export', description='Exportação de dados (CSV, Excel, JSON, PDF)', path='/export')

_export_params = {
    'formato':      {'description': 'Formato: csv | excel | json | pdf', 'type': 'str', 'default': 'json'},
    'data_inicio':  {'description': 'Data início (YYYY-MM-DD)', 'type': 'str'},
    'data_fim':     {'description': 'Data fim (YYYY-MM-DD)', 'type': 'str'},
    'ativo_id':     {'description': 'Filtro por UUID do ativo', 'type': 'str'},
    'corretora_id': {'description': 'Filtro por UUID da corretora', 'type': 'str'},
    'tipo':         {'description': 'Filtro por tipo de operação', 'type': 'str'},
}


@ns_export.route('/transacoes')
class ExportTransacoes(Resource):
    @ns_export.doc('export_transacoes', params=_export_params)
    @ns_export.response(200, 'Arquivo exportado (Content-Disposition: attachment)')
    @ns_export.response(400, 'Formato inválido', _erro)
    @ns_export.response(401, 'Não autenticado', _erro)
    def get(self):
        """Exporta transações do usuário em CSV, Excel, JSON ou PDF."""
        pass


@ns_export.route('/proventos')
class ExportProventos(Resource):
    @ns_export.doc('export_proventos', params=_export_params)
    @ns_export.response(200, 'Arquivo exportado')
    @ns_export.response(401, 'Não autenticado', _erro)
    def get(self):
        """Exporta proventos recebidos (dividendos, JCP, aluguéis) em CSV, Excel, JSON ou PDF."""
        pass


@ns_export.route('/posicoes')
class ExportPosicoes(Resource):
    @ns_export.doc('export_posicoes', params=_export_params)
    @ns_export.response(200, 'Arquivo exportado')
    @ns_export.response(401, 'Não autenticado', _erro)
    def get(self):
        """Exporta posição consolidada atual do portfólio em CSV, Excel, JSON ou PDF."""
        pass


# ---------------------------------------------------------------------------
# Registro dos namespaces na Api
# ---------------------------------------------------------------------------

def init_swagger(app):
    """
    Registra a Api flask-restx no app Flask via Blueprint /api.
    Swagger UI em /api/docs, spec JSON em /api/swagger.json.

    Args:
        app: instância Flask
    """
    api.add_namespace(ns_auth)
    api.add_namespace(ns_ativos)
    api.add_namespace(ns_transacoes)
    api.add_namespace(ns_ir)
    api.add_namespace(ns_export)
    app.register_blueprint(_swagger_bp, url_prefix='/api')
