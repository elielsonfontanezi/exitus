# 📡 API REFERENCE COMPLETA - SISTEMA EXITUS

**ATENÇÃO:** Este arquivo é gerado automaticamente pelo script \`generate_api_docs.sh\`.  
**Não editar manualmente.** Rode o script para atualizar.

**Base URL:** \`http://localhost:5000/api\`  
**Gerado em:** $(date)

---

## 📋 ROTAS DISPONÍVEIS

[alertas] 'DELETE' /<alerta_id>
[alertas] 'GET' 
[alertas] 'PATCH' /<alerta_id>/toggle
[alertas] 'POST' 
[buy_signals] 'GET' /buy-score/<string:ticker>
[buy_signals] 'GET' /margem-seguranca/<string:ticker>
[buy_signals] 'GET' /watchlist-top
[buy_signals] 'GET' /zscore/<string:ticker>
[calculos] 'GET' /portfolio
[calculos] 'GET' /preco_teto/<string:ticker>
[cotacoes] 'GET' /batch
[cotacoes] 'GET' /health
[cotacoes] 'GET' /<ticker>
[evento_corporativo] 'GET' /
[evento_corporativo] 'POST' /<uuid:evento_id>/aplicar
[feriadosblueprint] 'DELETE' /<string:id>
[feriadosblueprint] 'GET' /
[feriadosblueprint] 'GET' /<string:id>
[feriadosblueprint] 'POST' /
[fontesblueprint] 'DELETE' /<string:id>
[fontesblueprint] 'GET' /
[fontesblueprint] 'GET' /<string:id>
[fontesblueprint] 'POST' /
[movimentacao_caixa] 'DELETE' /<uuid:movimentacao_id>
[movimentacao_caixa] 'GET' 
[movimentacao_caixa] 'GET' /extrato
[movimentacao_caixa] 'GET' /saldo/<uuid:corretora_id>
[movimentacao_caixa] 'GET' /<uuid:movimentacao_id>
[movimentacao_caixa] 'POST' 
[movimentacao_caixa] 'PUT' /<uuid:movimentacao_id>
[movimentacao] 'GET' /
[movimentacao] 'GET' /saldo/<uuid:corretora_id>
[movimentacao] 'POST' /
@performance_bp.route("/benchmark", methods=["GET"])
@performance_bp.route("/correlacao", methods=["GET"])
@performance_bp.route("/desvio-alocacao", methods=["GET"])
@performance_bp.route("/performance", methods=["GET"])
[portfolio] 'DELETE' /<uuid:portfolio_id>
[portfolio] 'GET' /
[portfolio] 'GET' /alocacao
[portfolio] 'GET' /dashboard
[portfolio] 'GET' /distribuicao/classes
[portfolio] 'GET' /distribuicao/setores
[portfolio] 'GET' /evolucao
[portfolio] 'GET' /metricas-risco
[portfolio] 'GET' /performance
[portfolio] 'GET' /<uuid:portfolio_id>
[portfolio] 'POST' /
[portfolio] 'PUT' /<uuid:portfolio_id>
[posicao] 'GET' 
[posicao] 'GET' /
@projecoes_bp.route("/cenarios", methods=["GET"])
@projecoes_bp.route("/recalcular", methods=["POST"])
@projecoes_bp.route("/renda", methods=["GET"])
@projecoes_bp.route("/renda/<string:portfolio_id>", methods=["GET"])
@provento_bp.route("/<uuid:id>", methods=["GET"])
[provento] 'DELETE' /<uuid:id>
[provento] 'GET' /
# [provento] 'GET' /<uuid:id>
[provento] 'POST' /
[provento] 'PUT' /<uuid:id>
[regras_fiscaisblueprint] 'DELETE' /<string:id>
[regras_fiscaisblueprint] 'GET' /
[regras_fiscaisblueprint] 'GET' /<string:id>
[regras_fiscaisblueprint] 'POST' /
@relatorios_bp.route("/gerar", methods=["POST"])
@relatorios_bp.route("/lista", methods=["GET"])
@relatorios_bp.route("/<string:relatorio_id>/exportar", methods=["POST"])
@relatorios_bp.route("/<string:relatorio_id>", methods=["DELETE"])
@relatorios_bp.route("/<string:relatorio_id>", methods=["GET"])
[relatorios] 'GET' /relatorios
[relatorios] 'POST' /relatorios
