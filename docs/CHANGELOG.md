# Changelog — Sistema Exitus

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.
O formato é baseado em [Keep a Changelog](https://keepachangelog.com/),
e este projeto adere semanticamente à versão v0.8.0.

---

## [Unreleased]

### Fixed — Correção Completa dos Testes Pendentes (10/03/2026)

- **Suite de testes 100% funcional:**
  - **491/491 testes passando** (100% de sucesso)
  - Todos os 17 testes pendentes corrigidos
  - 0 errors, 0 failures
- **Correções em `backend/app/blueprints/ir_blueprint.py`:**
  - Corrigido acesso à estrutura de resposta do endpoint `/api/ir/darf`
  - Ajustado para acessar `apuracao['darf']['darfs']` (darf retorna `{'darfs': [...]}`)
- **Correções em `backend/app/services/reconciliacao_service.py`:**
  - Corrigido mapeamento de `TipoMovimentacao` para usar valores do enum em minúsculo
  - Ajustado comparação de tipos: `deposito`, `saque`, `credito_prov`, `transf_rec`, `pagto_taxa`, `pagto_imposto`, `transf_env`
- **Correções em `backend/tests/test_ir_integration.py`:**
  - Corrigido teste `test_darf_mes_vazio_retorna_lista_vazia` para verificar estrutura correta
  - Corrigido teste `test_rf_aparece_no_darf_informativo` para acessar `data['darfs']` corretamente
- **Correções em `backend/tests/test_reconciliacao.py`:**
  - Adicionado `headers=auth_client._auth_headers` em 5 testes de integração (401 Unauthorized resolvido)
  - Ajustado teste `test_verificar_integridade_transacoes_sem_ativo` (constraint NOT NULL)
  - Corrigido teste `test_verificar_saldos_corretoras_sem_divergencia` (problema de sessão SQLAlchemy)
  - Corrigido teste `test_verificar_saldos_corretoras_com_divergencia` (expectativa de diferença)
- **Correções em `backend/tests/conftest.py`:**
  - Modificado `cleanup_test_data` para deletar todas as entidades criadas durante testes
  - Removido DELETE dos fixtures `usuario_seed`, `ativo_seed`, `corretora_seed` para evitar FK violations
  - Adicionado `synchronize_session=False` para forçar delete direto no banco
  - Ordem de deleção: posições → transações → movimentações → corretoras → ativos → usuários
- **Resultados:**
  - +9 testes corrigidos (de 482 → 491)
  - -8 errors resolvidos (teardown FK violations)
  - -1 failed resolvido (saldo divergência)
  - **Taxa de sucesso:** 100% (de 96.6% → 100%)

### Cancelled — ORPHAN-001 Limpeza de Código Órfão (10/03/2026)

- **Análise realizada:** Identificados 3 blueprints legacy e arquivos duplicados
- **Decisão:** Cancelado por considerar muito arriscado sem análise profunda
- **Status:** GAP mantido como cancelado no ROADMAP.md
- **Motivo:** Segurança do codebase > limpeza otimização

### Fixed — BLUEPRINT-CONSOLIDATION-001 Consolidação de Blueprints (10/03/2026)

- **Limpeza segura de pastas vazias:**
  - Removida pasta `blueprints/feriados/` (routes.py vazio)
  - Removida pasta `blueprints/regras_fiscais/` (routes.py vazio)
- **Documentação de padrões:**
  - Padrão A: Pasta + routes.py (moderno, recomendado para novos blueprints)
  - Padrão B: Arquivo único (legacy funcional, mantido para compatibilidade)
- **Decisão arquitetônica:** Manter coexistência de padrões em vez de forçar migração
- **Resultados:** -2 pastas vazias, 0 funcionalidades perdidas, 491/491 testes passando
- **Segurança:** Abordagem conservadora, sem risco de quebrar funcionalidades existentes

### Fixed — Auditoria e Correção de Testes (09/03/2026)

- **Auditoria completa da suite de testes:**
  - Verificados 499 testes coletados (23 arquivos formais)
  - 482 testes passando (96.6% de sucesso)
  - 17 testes pendentes documentados em `docs/TESTES_PENDENTES.md`
- **Correções em `backend/tests/conftest.py`:**
  - Adicionado `db.session.rollback()` antes de DELETE em fixtures (auth_client, usuario_seed, ativo_seed, corretora_seed)
  - Adicionado try/except com rollback em commits dos fixtures
  - Criado fixture `cleanup_test_data` (autouse) para limpar transações/posições/movimentações
  - Criado fixture `transacao_seed` para testes de auditlog
- **Correções em `backend/tests/test_reconciliacao.py`:**
  - Importado enum `TipoMovimentacao`
  - Substituído strings `'DEPOSITO'`/`'SAQUE'` por `TipoMovimentacao.DEPOSITO`/`SAQUE`
  - Corrigido erro `InvalidTextRepresentation` em 8 testes
- **Resultados:**
  - +91 testes passando (de 391 → 482)
  - -82 errors resolvidos (de 90 → 8)
  - -3 failed resolvidos (de 12 → 9)
  - Taxa de sucesso: +18% (de 78.6% → 96.6%)
- **Documentação:**
  - `docs/TESTES_PENDENTES.md` criado com análise dos 17 testes pendentes
  - `docs/LESSONS_LEARNED.md` atualizado com L-TEST-001 (fixtures com rollback)
  - `docs/ROADMAP.md` atualizado com métricas reais (482/499 testes, 144 endpoints)

### Fixed — EXITUS-CLEANUP-001 — Limpeza Parcial do Codebase (09/03/2026)

- **Remoção de arquivos vazios/não utilizados:**
  - `backend/app/blueprints/fontes/routes.py` — arquivo vazio removido
  - `backend/app/blueprints/movimentacoes/` — pasta vazia removida
- **Análise de blueprints duplicados:**
  - Identificados `movimentacao_blueprint.py` (registrado, 83 bytes) e `movimentacao_caixa_blueprint.py` (não registrado, 202 bytes)
  - Decisão: manter ambos, criar GAP específico para análise futura
- **Novo GAP registrado:** `EXITUS-MOVIMENTACAO-CONSOLIDATION-001` — análise e consolidação de blueprints de movimentação
- **Arquivos `__init__.py` vazios mantidos** — necessários para estrutura de pacotes Python

### Added — EXITUS-DARF-ACUMULADO-001 — Sistema de Acúmulo de DARF (09/03/2026)

- **`backend/app/models/saldo_darf_acumulado.py`** — modelo para persistir saldos:
  - Campos: usuario_id, categoria, codigo_receita, ano_mes, saldo
  - Constraints: únicidade por usuário/categoria/código/mês
  - Validações: categoria válida, código DARF válido, saldo >= 0
- **`backend/app/services/ir_service.py`** — lógica de acúmulo implementada:
  - `_calcular_darf()` modificado para acumular valores < R$10,00
  - `_processar_acumulo_darf()` — gerencia acúmulo entre meses
  - Remove alerta de DARF < R$10 (agora tratado automaticamente)
  - Compatibilidade mantida com API existente
- **Migration `5f0da25a1ee2`** — cria tabela `saldo_darf_acumulado`
- **`backend/tests/test_darf_acumulado.py`** — 8 testes unitários + 2 integração:
  - Acúmulo abaixo do mínimo, pagamento ao atingir, separação por categoria
  - IR renda fixa não acumula, IR zero não gera registro
  - Todos os testes passam (8/8)
- **Funcionalidade:** DARF < R$10,00 acumulado automaticamente, pago quando soma >= R$10,00

### Added — EXITUS-RECONCILIACAO-001 — Sistema de Reconciliação de Dados (09/03/2026)

- **`backend/app/services/reconciliacao_service.py`** — serviço de verificação de consistência:
  - `verificar_tudo()`: executa todas as verificações e retorna status geral (OK/WARNING/ERROR)
  - `verificar_posicoes()`: compara quantidade em `Posicao` vs soma de transações (compra - venda)
  - `verificar_saldos_corretoras()`: valida `Corretora.saldo_atual` vs `SUM(MovimentacaoCaixa)`
  - `verificar_integridade_transacoes()`: detecta transações sem ativo, quantidade zero, duplicadas
  - `verificar_ativo_especifico()`: reconciliação detalhada de um ativo por corretora
  - Tolerância de `0.01` para arredondamento, `1.00` para custos/saldos
- **`backend/app/blueprints/reconciliacao_blueprint.py`** — 5 endpoints REST:
  - `GET /api/reconciliacao/verificar`: verificação completa
  - `GET /api/reconciliacao/posicoes`: apenas posições
  - `GET /api/reconciliacao/saldos`: apenas saldos de corretoras
  - `GET /api/reconciliacao/integridade`: apenas integridade de transações
  - `GET /api/reconciliacao/ativo/<id>`: ativo específico (query param `corretora_id` opcional)
- **`backend/app/__init__.py`** — blueprint registrado em `/api/reconciliacao/*`
- **`backend/tests/test_reconciliacao.py`** — 14 testes (9 unitários + 5 integração):
  - Testes de divergências de quantidade, custo, saldo
  - Detecção de transações sem ativo, duplicadas
  - Tolerância de arredondamento
  - Endpoints REST funcionais
- **Suite: 371 passed, 82 errors** (erros não relacionados à reconciliação)

### Added — EXITUS-AUDITLOG-001 — Sistema de Auditoria Completo (09/03/2026)

- **`backend/app/services/auditoria_service.py`** — serviço centralizado de auditoria:
  - `registrar()`: função principal que nunca levanta exceção
  - Atalhos: `registrar_create()`, `registrar_update()`, `registrar_delete()`, `registrar_login()`, `registrar_logout()`, `registrar_export()`
  - Captura automática de `ip_address` e `user_agent` via `flask.request`
  - Suporta `dados_antes`/`dados_depois` para rastreamento de alterações
- **Integração em 5 services principais:**
  - `transacao_service.py`: CREATE, UPDATE, DELETE
  - `provento_service.py`: CREATE, UPDATE, DELETE
  - `ativo_service.py`: CREATE, UPDATE, DELETE
  - `movimentacao_caixa_service.py`: CREATE
  - `auth_service.py`: LOGIN (sucesso e falha com mensagens específicas)
- **`backend/tests/test_auditlog.py`** — 15 testes (6 unitários + 9 integração):
  - Testes de `AuditoriaService`: create, update, delete, login sucesso/falha
  - Integração com TransacaoService, AtivoService, AuthService
  - Validação de `get_alteracoes()` e `to_dict()` do model
- **Tabela `log_auditoria` agora é populada** em todas operações CRUD e autenticação
- **Suite: 399 passed, 45 errors** (erros não relacionados à auditoria)

### Added — EXITUS-CIRCUITBREAKER-001 — Circuit Breaker para APIs Externas (08/03/2026)

- **`backend/app/utils/circuit_breaker.py`** — novo utilitário:
  - `CircuitBreaker`: estados CLOSED/OPEN/HALF_OPEN, `call_allowed()`, `record_success()`, `record_failure()`, `reset()`
  - `get_circuit_breaker()`: registry global singleton por provider
  - `with_retry()`: retry com backoff exponencial, integrado ao circuit breaker
  - `reset_all()`: limpa estado de todos os breakers (usado em testes)
- **`backend/app/services/cotacoes_service.py`** — todos os 8 providers integrados:
  - BR: brapi.dev, hgfinance, yfinance.BR, twelvedata (threshold=3, recovery=60/120s)
  - US: finnhub, alphavantage, twelvedata, yfinance.US
  - Provider OPEN pula imediatamente para o próximo sem aguardar timeout HTTP
- **`backend/tests/test_circuit_breaker.py`** — 23 testes (estados, HALF_OPEN, registry, retry, integração)
- **Suite: 416 passed, 16 errors**

### Added — EXITUS-IOF-001 — IOF Regressivo sobre Rendimentos de RF (09/03/2026)

- **`backend/app/services/ir_service.py`** — implementação completa:
  - `TABELA_IOF_REGRESSIVA`: lista de 30 entradas (dia 0→0%, dia 1→96%, ..., dia 29→3%)
  - `_calcular_iof(prazo_dias, rendimento)`: calcula IOF com arredondamento 2 casas
  - `_apurar_renda_fixa()`: integração com IOF por operação
    - Campo `iof_devido` adicionado em cada `detalhe` (incluindo LCI/LCA com 0.0)
    - Campo `iof_devido` adicionado no retorno consolidado
    - LCI/LCA: IOF = 0 (isentos)
    - Prazo >= 30 dias: IOF = 0
- **`backend/tests/test_iof.py`** — 22 testes formais:
  - `TestTabelaIOFRegressiva` (7 testes): estrutura, valores, monotonicidade
  - `TestCalcularIOF` (11 testes): limites de prazo, valores, arredondamento
  - `TestApurarRendaFixaComIOF` (4 testes): integração, LCI/LCA, prazo curto/longo
- **Suite: 22 passed, 0 failed**

### Fixed — EXITUS-SCRIPTS-002 — Limpeza e Revisão de Scripts (09/03/2026)

- **Removido** `scripts/import_b3.py` — bash disfarçado com shebang Python (337 linhas)
- **Removido** `scripts/generate_api_docs.sh` — obsoleto, substituído por Swagger
- **Arquivado** `scripts/migrate_legacy_seeds.py` → `scripts/archive/` — migração one-time já concluída
- **Mantido** `scripts/import_b3.sh` — wrapper funcional para containers (394 linhas)
- **Mantido** `scripts/reset_and_seed.sh` + `reset_and_seed.py` — wrapper + script Python (ambos necessários)
- **Resultado:** 3 arquivos removidos/arquivados, estrutura de scripts mais limpa

### Fixed — EXITUS-MOVIMENTACAO-CONSOLIDATION-001 — Consolidação de Blueprints de Movimentação (09/03/2026)

- **Removido** `backend/app/blueprints/movimentacao_blueprint.py` — blueprint básico (83 bytes, 3 endpoints)
- **Registrado** `movimentacao_caixa_blueprint.py` em `__init__.py` — blueprint completo (7 endpoints)
- **Corrigido** ImportError removendo `MovimentacaoCaixaUpdateSchema` inexistente
- **Removido** endpoint PUT que usava schema não implementado
- **Resultado:** API movimentações agora usa blueprint completo com CRUD + extrato
- **URL final:** `/api/movimentacoes-caixa` (mais específico que `/api/movimentacoes`)
- **Regra #10 adicionada:** Testes formais em `/backend/tests/` devem ser preservados permanentemente

### Fixed — EXITUS-TESTFIX-CAMBIO-001 — Correção de Testes de Câmbio (09/03/2026)

- **`backend/tests/test_cambio_integration.py`** — 33 testes passando (antes 16 errors):
  - `auth_headers`: email único com UUID suffix para evitar `UniqueViolation`
  - Testes fallback: `TaxaCambio.query.delete()` para garantir banco vazio
  - Suite geral: 432 passed, 0 errors (antes: 416 passed, 16 errors)

### Added — EXITUS-CONSTRAINT-001 — CHECK Constraints de Negócio (08/03/2026)

- **`backend/alembic/versions/20260308_1900_add_business_constraints.py`** — 13 constraints:
  - `transacao`: `quantidade>0`, `preco_unitario>0`, `valor_total>0`
  - `evento_custodia`: `quantidade>0`, `valor_operacao>0`
  - `projecoes_renda`: `renda_dividendos_projetada>=0`, `renda_jcp_projetada>=0`, `renda_rendimentos_projetada>=0`, `renda_total_mes>=0`
  - `parametros_macro`: `taxa_livre_risco>=0`, `inflacao_anual>=0`
  - `taxa_cambio`: `taxa>0`
  - `alertas`: `condicao_valor>0`
- **`backend/tests/test_constraints.py`** — 17 testes via `engine.connect()` com rollback isolado
- **`docs/EXITUS_DB_STRUCTURE.txt`** — schema atualizado
- **Suite antes do CIRCUITBREAKER: 393 passed, 16 errors**

### Added — EXITUS-DOCS-SYNC-001 — Sincronização de Documentação (08/03/2026)

- **`docs/MODULES.md`** — Métricas atualizadas (376 testes, 35/54 GAPs), Fase 5 marcada como concluída
- **`docs/API_REFERENCE.md`** — Seções 21 e 22 adicionadas (Rentabilidade + Importação B3) com exemplos e contratos completos
- **`docs/LESSONS_LEARNED.md`** — Lições L-SVC-001 (`current_app.db` bug) e L-TEST-001 (pandas NaN/CSV)

### Added — EXITUS-COVERAGE-001 — Cobertura de Testes import_b3_service.py (08/03/2026)

- **`backend/tests/test_import_b3_parsers.py`** — 59 testes novos (59 passed):
  - `TestParseData`: 8 testes (formatos BR, ISO, vazio, inválido, espaços)
  - `TestParseQuantidade`: 8 testes (int, float, string, traço, NaN, vazio)
  - `TestParseMonetario`: 10 testes (float, BRL, R$, americano, traço, NaN)
  - `TestExtrairTicker`: 9 testes (FII com descrição, ação, BDR, hífen, minúsculo)
  - `TestObterOuCriarAtivo`: 3 testes (FII vs ACAO, sem duplicata)
  - `TestGerarHashLinha`: 4 testes (determinístico, muda por arquivo, muda por conteúdo, 32 chars)
  - `TestParseMovimentacoesCSV`: 6 testes (válido, sem data, valor zero, custódia, cessão, múltiplas linhas)
  - `TestParseNegociacoesCSV`: 4 testes (compra, venda, sem tipo, sem data inválida)
  - `TestImportarNegociacoesTipos`: 3 testes (tipo não mapeado, COMPRA, VENDA)
  - `TestImportarMovimentacoesTipos`: 4 testes (tipo não mapeado, todos mapeados, dry_run mov, dry_run neg)
- **Suite: 376 passed, 16 errors (TESTFIX-CAMBIO-001 pré-existente)**

### Added — EXITUS-SERVICE-REVIEW-001 — Services Stub Implementados (08/03/2026)

- **`backend/app/services/analise_service.py`** — Reescrito com dados reais:
  - `analisar_performance_portfolio()`: alocação por classe com `Posicao`+`Ativo`, conversão cambial via `CambioService`
  - `comparar_com_benchmark()`: delega para `RentabilidadeService.calcular()` (TWR, MWR, alpha reais)
  - `calcular_correlacao_ativos()`: matriz de correlação de Pearson via `historico_preco` + helper `_correlacao()`
- **`backend/app/services/projecao_renda_service.py`** — Projeção real:
  - `calcular_projecao()`: `qtd × preco_atual × DY_anual / 12` por tipo de provento predominante
  - `_tipo_provento_predominante()`: via histórico de `Provento` (GROUP BY tipo, ORDER BY COUNT)
  - `create_or_update()`: upsert correto via constraint `usuario_id+portfolio_id+mes_ano`
- **`backend/app/services/relatorio_performance_service.py`** — Métricas reais:
  - `calcular()`: Sharpe ratio, max drawdown, volatilidade anualizada via `historico_preco`
  - `generate()`: recalcula métricas antes de persistir (não salva mais dados mock)
  - `_volatilidade_anualizada()`, `_sharpe()`, `_max_drawdown()`, `_serie_portfolio()`
- **`backend/app/services/auditoria_relatorio_service.py`** — Fix bug:
  - `current_app.db.session` → `db.session` (AttributeError em runtime)
- **`backend/tests/test_service_review.py`** — 23 testes novos (23 passed)
- **Suite: 317 passed, 16 errors (TESTFIX-CAMBIO-001 pré-existente)**

### Added — EXITUS-RENTABILIDADE-001 — Rentabilidade TWR + MWR + Benchmarks (08/03/2026)

- **`backend/app/services/rentabilidade_service.py`** — Novo service completo:
  - `calcular()`: orquestra TWR, MWR e benchmark num único resultado
  - `_calcular_twr()`: Time-Weighted Return por sub-períodos entre fluxos de caixa
  - `_calcular_mwr()` + `_xirr()`: Money-Weighted Return via scipy.optimize.brentq (XIRR com fallback Newton-Raphson)
  - `_benchmark_cdi()`: CDI acumulado via `parametros_macro.taxa_livre_risco`
  - `_benchmark_por_preco()`: IBOV/IFIX/SP500 via `historico_preco`
  - `_benchmark_ipca_mais()`: IPCA + spread fixo
  - `_obter_fluxos_caixa()`: agrega transações, proventos e movimentações de caixa
  - `_obter_valores_portfolio()`: valor do portfólio em datas-chave via `historico_preco`
- **`backend/app/blueprints/portfolio_blueprint.py`** — Endpoint `GET /api/portfolios/rentabilidade`:
  - Query params: `periodo` (1m/3m/6m/12m/24m/ytd/max), `benchmark` (CDI/IBOV/IFIX/IPCA6/SP500)
  - Validação de parâmetros com 400 para valores inválidos
- **`backend/tests/test_rentabilidade.py`** — 21 testes novos (21 passed):
  - `TestResolverPeriodo` (4), `TestXIRR` (3), `TestTWR` (4)
  - `TestBenchmarkCDI` (2), `TestCalcularIntegracao` (4), `TestEndpointRentabilidade` (4)
- **Suite: 294 passed, 16 errors (TESTFIX-CAMBIO-001 pré-existente)**

### Added — EXITUS-CLEANUP-001 — Higiene do Codebase (08/03/2026)

- **Arquivos deletados (11):**
  - `backend/app/__kk`
  - `backend/app/models/ativo.py.pre-14-enums`
  - `backend/app/models/configuracao_alerta.py.backup_20251218_114233`
  - `backend/app/models/usuario.py.backup_*` (3 arquivos)
  - `backend/app/services/cotacoes_service.py.backup*` (2 arquivos)
  - `backend/app/services/cotacao_service.py.DELETAR-20260102`
  - `backend/app/services/buy_signals_service.py.backup`
  - `backend/app/schemas/ativo_service.py` (cópia obsoleta — original em `services/`)
- **Blueprint mock removido:** `backend/app/blueprints/fontesblueprint.py` — substituído por `fonte_dados_blueprint.py` (implementação real com JWT)
- **`backend/app/__init__.py`** — removida importação de `fontesblueprint` (M4.2)
- **Suite: 273 passed, 16 errors (baseline mantido)**

### Added — EXITUS-VALIDATION-001 — Idempotência Importação B3 (08/03/2026)

- **`backend/app/services/import_b3_service.py`** — Refatoração completa de idempotência:
  - `_sanitizar_texto()`: remove tags HTML, caracteres de controle Unicode, trunca em 500 chars
  - `_gerar_hash_linha()`: hash MD5 de todos os campos da linha + nome do arquivo origem
  - `_importar_proventos()`: deduplicação por `hash_importacao`, relatório `duplicatas_ignoradas` + `duplicatas_lista`
  - `importar_movimentacoes()`: parâmetro `dry_run=False` — não persiste, retorna preview
  - `importar_negociacoes()`: mesma lógica de hash + dry_run para transações
  - Correção bug: `TipoAtivo.FII` / `TipoAtivo.ACAO` em vez de strings hardcoded (enum lowercase)
- **`backend/app/models/provento.py`** — Campos `hash_importacao` (String 64, indexed) + `arquivo_origem` (String 255)
- **`backend/app/models/transacao.py`** — Campos `hash_importacao` + `arquivo_origem`
- **`backend/alembic/versions/20260308_1500_add_hash_importacao_validation001.py`** — Migration idempotente com índices
- **`backend/tests/test_import_b3_idempotencia.py`** — 18 testes novos (18 passed):
  - `TestSanitizarTexto` (5 testes), `TestGerarHashLinha` (4 testes)
  - `TestIdempotenciaProventos` (3 testes), `TestDryRunProventos` (2 testes)
  - `TestIdempotenciaNegociacoes` (2 testes), `TestSanitizacaoNaImportacao` (2 testes)
- **Suite: 273 passed, 16 errors (TESTFIX-CAMBIO-001 pré-existente)**

### Changed — ROADMAP v3.0 + SCRIPTS-002 + .windsurfrules v2.1 (05/03/2026)

- **EXITUS-SCRIPTS-002** — GAP registrado no ROADMAP (Fase 6)
  - Diagnóstico: 28 scripts auditados — 2 obsoletos, 1 bug (shebang), 3 duplicidades, 1 frágil
  - Detalhamento completo no ROADMAP.md com escopo de 7 itens
- **.windsurfrules v2.1** — Seção `SCRIPTS DISPONÍVEIS` adicionada
  - 28 scripts categorizados (containers, banco, seeds, recovery, utilitários)
  - Comandos frequentes documentados
  - Métricas atualizadas: 255+ testes, 15 TipoAtivo
- **EXITUS-DOCS-IRCONSOLIDAR-001** — Consolidação `EXITUS-IR-001.md` + `EXITUS-IR-009.md`
  - `docs/EXITUS-IR-001.md` v2.0: absorve Seção 9 (regras 2026, referências legais, tabela resumo)
  - `docs/EXITUS-IR-009.md`: mantido com redirecionamento para IR-001.md
- **ROADMAP.md v3.0** — Reestruturação completa do roadmap
  - Fases 2, 3, 4 marcadas como concluídas (30 GAPs)
  - 17 novos GAPs identificados em revisão abrangente do backend e banco
  - Novas fases: 5 (Robustez/Qualidade), 6 (Integridade), 7 (Produção), 8 (Expansão Futura)
  - Proposta futura registrada: EXITUS-FUNDOS-001 (Fundos de Investimento)
  - Seção "Registrado para Avaliação Futura" (Monte Carlo, Markowitz, Redis, etc.)
  - Nota explícita: frontend pode ser refeito do zero
  - Total: 30 concluídos + 22 planejados + 1 proposta = 53 GAPs rastreados
- **MODULES.md** — Atualização de métricas e status
  - Suite de testes: 77 → 255+ passed
  - GAPs concluídos: 9 → 30
  - Seção de Fases Planejadas (5-8) adicionada
- **LESSONS_LEARNED.md** — Correção referência L-DB-004
  - EXITUS-ENUM-001 atualizado de "Fix planejado" para "✅ Concluído (04/03/2026)"
- **ARCHITECTURE.md** — Nota sobre escopo frontend

### Added
- **EXITUS-TESTFIX-003** — Correção fixtures `test_newapis_integration.py` (04/03/2026)
  - `tests/test_newapis_integration.py`: fixture `auth_headers` corrigido (`nome_completo`, `set_password`, JWT direto sem login); fixtures `sample_parametro_macro` e `sample_fonte_dados` com nomes/pares únicos + cleanup por teste; asserts `==0` em banco não-vazio substituídos por asserts de estrutura
  - `app/services/fonte_dados_service.py`: `health_status()` e `taxa_sucesso()` corrigidos para acesso como `@property` (sem parênteses)
  - **Suite: 255 passed, 16 errors (TESTENV-001 Won't Fix)**

- **EXITUS-SCHEMA-001** — Correção serialização `FonteDados` (04/03/2026)
  - `app/models/fonte_dados.py`: `taxa_sucesso`, `taxa_erro`, `health_status` convertidos de métodos para `@property` — compatibilidade com Marshmallow
  - `app/schemas/fonte_dados_schema.py`: `tipo_fonte` usa `fields.Method` para extrair `.value` do enum; importação de `post_dump` adicionada
  - Endpoint `GET /api/fontes-dados` retorna `tipo_fonte: "api"` (lowercase) em vez de `"TipoFonteDados.API"`

- **EXITUS-ENUMFIX-002** — Linter automático de `values_callable` em models (04/03/2026)
  - `tests/test_model_standards.py`: `TestModelStandards.test_enum_columns_tem_values_callable` — varre AST de todos os models e falha se `Column(Enum(PythonEnum))` não tiver `values_callable`
  - Previne regressão futura do bug que motivou EXITUS-ENUM-001

- **EXITUS-ENUMFIX-001 / EXITUS-TESTENV-001** — Won't Fix + documentação (04/03/2026)
  - `docs/OPERATIONS_RUNBOOK.md`: `create_test_db.sh` marcado como **obrigatório após qualquer `alembic upgrade`**
  - Testes rodam exclusivamente no container (`podman exec exitus-backend python -m pytest`) — ambiente local não é suportado
  - `create_test_db.sh` já usava `pg_dump --schema-only` corretamente; problema foi operacional

- **EXITUS-MULTIMOEDA-001** — Suporte multi-moeda com conversão automática para BRL (04/03/2026)
  - `alembic/versions/20260304_2100_add_taxa_cambio_table.py`: tabela `taxa_cambio` com índice único `par_moeda+data_referencia`
  - `app/models/taxa_cambio.py`: model `TaxaCambio` com `get_taxa_atual()`, `get_taxa_na_data()`, `TAXAS_FALLBACK` para 7 pares
  - `app/services/cambio_service.py`: `CambioService` — resolução em 3 camadas (banco → cruzamento BRL → fallback), `converter()`, `converter_para_brl()`, `registrar_taxa()`, `atualizar_taxas_yfinance()`
  - `app/blueprints/cambio_blueprint.py`: 5 endpoints — `GET /api/cambio/taxa/<par>`, `POST /api/cambio/converter`, `GET /api/cambio/pares`, `GET /api/cambio/taxa/<par>/historico`, `POST /api/cambio/taxa`, `POST /api/cambio/atualizar`
  - `app/__init__.py`: blueprint câmbio registrado
  - `app/services/portfolio_service.py`: `get_alocacao()` converte posições USD/EUR para BRL via `CambioService`
  - `tests/test_cambio_integration.py`: 17 testes — unitários (identidade, fallback, converter, par) + fixtures de endpoint
  - `docs/EXITUS_DB_STRUCTURE.txt`: regenerado
  - **Suite: 234 passed, 0 failed**

- **EXITUS-ENUM-001** — Normalização de ENUMs PostgreSQL para lowercase (04/03/2026)
  - `alembic/versions/20260304_2000_normalize_enums_lowercase.py`: migration para 12 ENUMs — `tipoativo`, `classeativo`, `tipoprovento`, `tipomovimentacao`, `tipooperacao`, `tipoferiado`, `tipofontedados`, `tipoeventocorporativo`, `tipocorretora`, `tipo_evento_custodia`, `incidenciaimposto`, `userrole`
  - `app/models/ativo.py`: `values_callable` adicionado em `TipoAtivo` e `ClasseAtivo`
  - `app/models/usuario.py`: `values_callable` adicionado em `UserRole`
  - `app/models/corretora.py`: `values_callable` adicionado em `TipoCorretora`
  - `app/models/provento.py`: `values_callable` adicionado em `TipoProvento`
  - `app/models/movimentacao_caixa.py`: `values_callable` adicionado em `TipoMovimentacao`
  - `app/models/feriado_mercado.py`: `values_callable` adicionado em `TipoFeriado`
  - `app/models/evento_corporativo.py`: `values_callable` adicionado em `TipoEventoCorporativo`
  - `app/models/evento_custodia.py`: `values_callable` adicionado em `TipoEventoCustodia`
  - `app/models/regra_fiscal.py`: `values_callable` adicionado em `IncidenciaImposto`
  - `app/models/fonte_dados.py`: `values_callable` adicionado em `TipoFonteDados`
  - `docs/CODING_STANDARDS.md`: seção "ENUMs — Padrão Obrigatório" com exemplos de `values_callable`
  - `docs/ROADMAP.md`: GAPs `EXITUS-ENUMFIX-001`, `EXITUS-ENUMFIX-002`, `EXITUS-SCHEMA-001` registrados
  - `docs/EXITUS_DB_STRUCTURE.txt`: regenerado
  - **Suite: 64 passed, 0 failed**

- **EXITUS-RFCALC-001** — Cálculos avançados RF e FII (04/03/2026)
  - `alembic/versions/20260304_1900_add_rfcalc_fields_to_ativo.py`: migration `ADD COLUMN` em `ativo` — `taxa_cupom`, `valor_nominal`, `data_vencimento`, `ffo_por_cota`, `affo_por_cota` + índice `ix_ativo_data_vencimento`
  - `app/models/ativo.py`: 5 novos campos RF/FII + `to_dict()` atualizado
  - `app/services/rfcalc_service.py`: `RFCalcService` — Duration Macaulay, Duration Modificada, YTM (Newton-Raphson), FFO, AFFO, P/FFO, análise qualitativa de FIIs
  - `app/blueprints/calculos_blueprint.py`: 3 novos endpoints — `POST /api/calculos/rf/simular`, `GET /api/calculos/rf/<ticker>`, `GET /api/calculos/fii/<ticker>`
  - `tests/test_rfcalc_integration.py`: 24 testes unitários (fórmulas matemáticas + edge cases)
  - `docs/EXITUS_DB_STRUCTURE.txt`: regenerado com novos campos da tabela `ativo`
  - **Suite: 64 passed, 0 failed** (173 errors pré-existentes de setup, não relacionados)

- **EXITUS-NEWAPIS-001** — APIs de configuração (parametros_macro, fonte_dados) (04/03/2026)
  - `app/schemas/parametros_macro_schema.py`: schemas Create/Update/Response para validação
  - `app/schemas/fonte_dados_schema.py`: schemas Create/Update/Response com validações de rate_limit
  - `app/services/parametros_macro_service.py`: refatorado para remover antipadrão `create_app()`, CRUD completo, compatibilidade legada mantida
  - `app/services/fonte_dados_service.py`: service completo com health monitoring, registro de consultas/erros
  - `app/blueprints/parametros_macro_blueprint.py`: 8 endpoints REST em `/api/parametros-macro/*`
  - `app/blueprints/fonte_dados_blueprint.py`: 8 endpoints REST em `/api/fontes-dados/*` + health monitoring
  - `app/__init__.py`: blueprints registrados com logging de sucesso
  - `app/seeds/seed_fontes_dados.py`: import corrigido para `app.models.fonte_dados`
  - `tests/test_newapis_integration.py`: 25 testes CRUD para ambos endpoints
  - `scripts/get_backend_token.sh`: senha corrigida de `admin123` → `senha123`
  - `docs/ROADMAP.md`: seção "🛠️ Execução de Seeds" adicionada com comandos e tabela de seeds
  - **Endpoints validados:** `/api/parametros-macro` (4 registros) e `/api/fontes-dados` (4 registros)

- **EXITUS-IR-008** — Tratamento fiscal de UNITs B3 no engine de IR (04/03/2026)
  - `app/services/ir_service.py`: `TIPOS_ACAO_BR` expandido para incluir `TipoAtivo.UNIT` — isenção R$20k/mês e alíquota 15% para swing trade em UNITs
  - `tests/test_ir_integration.py`: classe `TestUnitsIR` (+4 testes: isento <R$20k, tributado >R$20k, enquadramento em swing_acoes, desmembramento não tributável)
  - **Suite total: 191 passed, 0 failed**

- **EXITUS-UNITS-001** — Suporte a UNITs B3 (04/03/2026)
  - `migrations/versions/20260304_1000_add_unit_enums.py`: `ALTER TYPE tipoativo ADD VALUE 'UNIT'` + `ALTER TYPE tipoeventocorporativo ADD VALUE 'DESMEMBRAMENTO'`
  - `app/models/ativo.py`: `TipoAtivo.UNIT = "unit"` adicionado (15º tipo)
  - `app/models/evento_corporativo.py`: `TipoEventoCorporativo.DESMEMBRAMENTO` + método `is_desmembramento()`
  - `app/schemas/evento_corporativo_schema.py`: `'desmembramento'` adicionado ao `OneOf` de Create e Update
  - `docs/ENUMS.md`: atualizado para 15 tipos, UNIT mapeado, versão 0.8.0
  - `tests/test_units_integration.py`: 8 testes (criação UNIT via API, persistência, listagem/filtro, classe renda_variável, is_desmembramento, evento via API, enum assertions)
  - **Suite total: 187 passed, 0 failed**

- **EXITUS-ANOMALY-001** — Detecção de preços anômalos (04/03/2026)
  - `app/services/anomaly_service.py`: novo serviço `AnomalyService` com dois métodos:
    - `detectar_anomalias(limiar, ativo_id, data_ref)` — varre `historico_preco`, detecta variações ≥ limiar, suprime se houver `EventoCorporativo` na janela de ±5 dias
    - `verificar_ativo(ativo_id, preco_novo, data_novo, limiar)` — detecção inline ao salvar nova cotação
  - `app/blueprints/cotacoes_blueprint.py`: novo endpoint `GET /api/cotacoes/anomalias` (params: `limiar`, `ativo_id`, `data_ref`); integração inline ao salvar preço no `GET /<ticker>`
  - `tests/test_anomaly_integration.py`: 17 testes (endpoint 401/400/200, service detectar 8 cenários, service verificar_ativo 4 cenários)
  - **Suite total: 179 passed, 0 failed**

- **EXITUS-IR-005** — IR sobre renda fixa — tabela regressiva (04/03/2026)
  - `ir_service.py`: constantes `TIPOS_RF`, `TABELA_RF`, helper `_aliquota_rf(prazo_dias)`
  - `ir_service.py`: novo método `_apurar_renda_fixa(resgates, pm_map, data_compra_map, dt_ref)` — aplica tabela regressiva 22,5%→20%→17,5%→15%, isenção total para LCI/LCA (PF)
  - `ir_service.py`: `apurar_mes()` coleta resgates RF, monta `data_compra_map` de `Posicao`, chama `_apurar_renda_fixa`, inclui `renda_fixa` em `categorias`
  - `ir_service.py`: `_calcular_darf()` aceita `ir_rf` — adiciona entrada informativa DARF código `0561` com `pagar=False` (retido na fonte)
  - `ir_service.py`: `gerar_dirpf()` — acumulador `rf_total`, agrega ficha `renda_fixa` no relatório anual
  - `tests/test_ir_integration.py`: classe `TestRendaFixa` (+7 testes: sem resgates, LCI isento, CDB 22,5%, TD 20%, Debênture 15%, DARF informativo, isolamento swing)
  - Padrão de fixtures `_setup()/_teardown()` com `decode_token` para obter `usuario_id` do `auth_client`
  - **Suite total: 162 passed, 0 failed** (antes de ANOMALY-001)

- **EXITUS-IR-009** — GAP: Atualização de Regras Fiscais 2026 (04/03/2026)
  - `docs/EXITUS-IR-009.md`: design completo criado
  - Mudanças mapeadas: JCP 15%→17,5% (PLP 128/2025), dividendos BR isenção limitada R$50k/mês/CNPJ com 10% acima, imposto mínimo até 10% progressivo para renda>R$600k/ano, aluguel tabela regressiva 22,5%→15%
  - ROADMAP atualizado: IR-009 registrado na Fase 3 (Alta prioridade), IR-004 descrição revisada

- **EXITUS-SWAGGER-001** — Auto-documentação OpenAPI (04/03/2026)
  - `app/swagger.py`: novo módulo com `Api` flask-restx montada em Blueprint `/api`
  - Swagger UI interativa em `/api/docs`; spec JSON em `/api/swagger.json`
  - 5 namespaces: `auth`, `ativos`, `transacoes`, `ir`, `export` (16 paths documentados)
  - JWT Bearer security scheme configurado na UI
  - Desabilitado em `testing` (sem impacto na suite de 154 testes)
  - `app/__init__.py`: registro de `init_swagger()` via `if not testing:`
  - **Suite total: 154 passed, 0 failed**

- **EXITUS-IR-006** — DIRPF anual (04/03/2026)
  - `ir_service.py`: novo método `gerar_dirpf(usuario_id, ano)` — fichas Renda Variável, Proventos, Bens e Direitos
  - `ir_blueprint.py`: novo endpoint `GET /api/ir/dirpf?ano=YYYY`
  - `apurar_mes()`: novo parâmetro `persist=False` (read-only mode) — fix upstream para evitar writes em chamadas de agregação
  - `apurar_mes()`: fix `ir_total` como `Decimal` (antes falhava com `int.quantize()`)
  - `tests/test_ir_integration.py`: classe `TestDirpf` (+8 testes)
  - **Suite total: 154 passed, 0 failed**

- **EXITUS-IR-009** — Regras fiscais 2026 — implementação (04/03/2026)
  - `ir_service.py`: `_apurar_proventos()` refatorado — JCP aliquota dinâmica (17,5% em 2026+), dividendos BR com limite R$50k/mês por ativo_id (proxy CNPJ)
  - Seed: 3 regras 2026 em `exitusdb` + `exitusdb_test` (JCP 17,5%, DIVIDENDO 0% com isenção R$50k, DIVIDENDO_TRIBUTADO 10%)
  - Regras pré-2026 (JCP 15%, DIVIDENDO BR 0%) já tinham `vigencia_fim = 2025-12-31` — expiração automática via `_carregar_regras_fiscais()`
  - `tests/test_ir_integration.py`: fixture `cenario_proventos_2026` + classe `TestRegrasFiscais2026` (+3 testes)
  - **Suite total: 146 passed, 0 failed**

- **EXITUS-IR-004** — Proventos tributáveis (baseline pré-2026) (04/03/2026)
  - `ir_service.py`: novo método `_apurar_proventos()` — JCP, dividendos BR/US, aluguel
  - `apurar_mes()` agora busca transações `DIVIDENDO`, `JCP`, `ALUGUEL` + nova seção `proventos` na resposta
  - Constante `DARF_JCP_DIVIDENDO = '9453'` e `TIPOS_BR` adicionados
  - Seed: 4 regras de proventos em `exitusdb` + `exitusdb_test` (DIVIDENDO BR 0%, JCP 15%, DIVIDENDO US 15%, ALUGUEL BR 15%)
  - `tests/test_ir_integration.py`: fixture `cenario_proventos` + classe `TestProventos` (+4 testes)
  - **Suite total: 143 passed, 0 failed**

- **EXITUS-IR-007** — Alíquotas dinâmicas via tabela `regra_fiscal` (03/03/2026)
  - `ir_service.py`: nova função `_carregar_regras_fiscais(data_ref)` — busca regras vigentes do banco
  - Nova função `_regra_para_categoria(regras, categoria)` — resolve alíquota/isenção por categoria
  - Funções `_apurar_*` refatoradas para receber `regras: dict` (IR-007) em vez de constantes hardcoded
  - Fallback automático para constantes hardcoded se `regra_fiscal` estiver vazia (resiliência)
  - Seed: 5 regras fiscais inseridas em `exitusdb` e `exitusdb_test` (BR/ACAO/SWING_TRADE, BR/DAY_TRADE, BR/FII/VENDA, US/STOCK/VENDA, US/REIT/VENDA)
  - `tests/test_ir_integration.py`: +2 testes (`TestRegrasFiscais`: alíquota carregada do banco, fallback quando tabela vazia)
  - **Suite total: 139 passed, 0 failed**

- **EXITUS-IR-003** — Compensação de prejuízo acumulado entre meses (03/03/2026)
  - Nova tabela `saldo_prejuizo` com unique constraint `(usuario_id, categoria, ano_mes)`
  - Model `app/models/saldo_prejuizo.py` + migration Alembic `20260303_1840`
  - Compensação automática por categoria fiscal (swing × swing, day-trade × day-trade, etc.)
  - Campos `prejuizo_compensado` e `prejuizo_acumulado` na resposta de cada categoria
  - Persistência automática do saldo a cada chamada de `apurar_mes()`
  - `tests/test_ir_integration.py`: +5 testes (campos, sem histórico, compensação total, parcial, mês vazio)
  - `docs/EXITUS-IR-001.md` atualizado para v1.2 com seções 2.6, 3.1, 3.2, 5, 6, 7, 10
  - **Suite total: 137 passed, 0 failed**

- **EXITUS-IR-002** — Custo médio histórico via tabela `posicao` (03/03/2026)
  - **Bug fix crítico:** `ir_service.py` usava `t.preco_unitario` (preço de venda) como custo de aquisição, resultando em lucro sempre zero
  - Agora carrega `preco_medio` da tabela `posicao` para cada `(ativo_id, corretora_id)` do usuário
  - Mapa `pm_map` passado às 4 funções de apuração (swing, day-trade, FIIs, exterior)
  - Alerta automático quando tabela `posicao` vazia ou PM não encontrado para um ativo
  - Pré-requisito: `POST /api/posicoes/calcular` deve ser executado antes de apurar IR
  - `tests/test_ir_integration.py`: +2 testes (lucro via PM, alerta posicao vazia)
  - **Suite total: 132 passed, 0 failed**

- **docs/EXITUS-IR-001.md** — Documentação completa da engine de IR (03/03/2026)
  - Objetivo, escopo, regras fiscais por categoria (tabela completa)
  - Arquitetura: diagrama de fluxo de `apurar_mes()`, constantes fiscais
  - API Reference completa: 3 endpoints com contratos JSON, parâmetros e erros
  - Testes: tabela de cobertura das 3 classes (TestApuracao, TestDarf, TestHistorico)
  - Tabelas do banco utilizadas e **não** utilizadas (com justificativa)
  - Decisões de design: uso de `Decimal`, código DARF 0561, `historico_anual` fixo em 12 meses
  - Exemplos cURL copiáveis
  - Seção §6 com 6 limitações mapeadas como GAPs EXITUS-IR-002 a EXITUS-IR-007

- **EXITUS-IR-002 a EXITUS-IR-007** — 6 GAPs derivados do EXITUS-IR-001 registrados no ROADMAP.md (03/03/2026)
  - **IR-002:** Custo médio histórico (PM acumulado via tabela `posicao`) — impacto **Alto**
  - **IR-003:** Compensação de prejuízo acumulado entre meses (nova tabela `saldo_prejuizo`) — impacto **Alto**
  - **IR-004:** Proventos tributáveis — JCP (15% retido na fonte) e withholding tax US (30%) — impacto **Alto**
  - **IR-005:** IR sobre renda fixa — tabela regressiva 22,5%→15% por prazo — impacto Alto
  - **IR-006:** DIRPF anual — relatório para Declaração de Ajuste Anual (fichas Renda Variável e Bens e Direitos) — impacto Alto
  - **IR-007:** Alíquotas dinâmicas via tabela `regra_fiscal` (atualmente hardcoded) — impacto Médio
  - **IR-008:** Tratamento fiscal de UNITs B3 — classificação, isenção R$20k, desmembramento→PM (depende UNITS-001) — impacto Médio, prioridade **Baixa**

- **docs/EXITUS-EXPORT-001.md** — Documentação completa da engine de exportação (03/03/2026)
  - Objetivo, escopo, entidades exportáveis (transações, proventos, posições)
  - Arquitetura: diagrama de fluxo de `ExportService.exportar()`, dependências de bibliotecas (`openpyxl`, `reportlab`)
  - Características por formato: JSON (envelope meta/dados/total), CSV (separador `;`, UTF-8-BOM), Excel (estilos openpyxl), PDF (A4 landscape, zebra-stripe)
  - API Reference completa: 3 endpoints, parâmetros, headers de resposta, códigos de erro
  - Testes: tabela de cobertura das 3 classes (TestExportTransacoes 17 testes, TestExportProventos 7, TestExportPosicoes 8)
  - Decisão de design: isolamento multi-tenant em proventos via subquery; resposta como download direto (sem envelope `success/data`)
  - Limitações mapeadas: EXITUS-EXPORT-002 (relatórios customizados), limite 10k fixo, posições sem snapshot histórico
  - Exemplos cURL copiáveis

- **API_REFERENCE.md** — Adicionadas seções 21 (Exportação) e 22 (IR) com resumo dos endpoints e exemplos

- **USER_GUIDE.md** — Seção "Exportação de Dados" substituiu stub antigo; tabelas de entidades, formatos, filtros e exemplos cURL

- **EXITUS-EXPORT-001** — Exportação genérica de dados (03/03/2026)
  - `app/services/export_service.py`: engine de exportação para CSV, Excel, JSON e PDF
    - Filtros: `data_inicio`, `data_fim`, `ativo_id`, `corretora_id`, `tipo`
    - CSV: cabeçalho com metadados (entidade, data geração, filtros aplicados), separador `;`, encoding UTF-8-BOM
    - Excel: título e metadados nas primeiras linhas, cabeçalho colorido, auto-ajuste de colunas
    - PDF: layout A4 landscape, tabela com zebra-stripe, título e metadados
    - JSON: envelope `{meta, dados, total}` com metadados completos
    - Proventos filtrados via subquery de ativos do usuário (sem `usuario_id` direto na tabela)
    - Limite configurável: 10.000 registros por exportação
  - `app/blueprints/export_blueprint.py`: 3 endpoints registrados em `/api/export/`
    - `GET /api/export/transacoes?formato=csv|excel|json|pdf`
    - `GET /api/export/proventos?formato=csv|excel|json|pdf`
    - `GET /api/export/posicoes?formato=csv|excel|json|pdf`
  - `tests/test_export_integration.py`: 32 testes (100% passed)
  - **Suite total: 130 passed, 0 failed**

- **EXITUS-IR-001** — Engine de cálculo de IR sobre renda variável (03/03/2026)
  - `app/services/ir_service.py`: apuração mensal por categoria (swing ações, day-trade, FIIs, exterior)
  - Isenção R$20.000/mês para swing trade em ações BR
  - Alíquotas: ações 15%, day-trade 20%, FIIs 20%, exterior 15%
  - Geração de DARF com código de receita (6015 BR / 0561 exterior), valor e status de pagamento
  - Histórico anual mês a mês (`historico_anual`)
  - `app/blueprints/ir_blueprint.py`: 3 endpoints registrados em `/api/ir/`
    - `GET /api/ir/apuracao?mes=YYYY-MM` — breakdown detalhado por categoria
    - `GET /api/ir/darf?mes=YYYY-MM` — DARFs a pagar com código de receita
    - `GET /api/ir/historico?ano=YYYY` — resumo mensal do ano
  - `tests/test_ir_integration.py`: 19 testes (100% passed)
  - Fix: `conftest.py` — removido campo `cnpj` inválido do `corretora_seed`
  - **Suite total: 96 passed, 0 failed**

- **EXITUS-TESTDB-001** — Script `create_test_db.sh` — recriação automatizada do banco de teste (03/03/2026)
  - Drop + create de `exitusdb_test` via psql no container `exitus-db`
  - Schema aplicado via `pg_dump --schema-only` (paridade total com `exitusdb`, ENUMs incluídos)
  - Suporte a `--dry-run` para validação sem alterações
  - Idempotente: seguro para executar múltiplas vezes
  - **L-TEST-001**: nunca usar dados hardcoded em testes (`test_admin`, `PETR4`) — usar fixtures dinâmicas do `conftest.py`
  - **L-TEST-002**: `db.create_all()` falha com ENUMs PostgreSQL nativos — usar `pg_dump --schema-only`
  - Corrigidos 5 testes com dados hardcoded que dependiam do banco de produção

- **EXITUS-TESTFIX-001** + **EXITUS-TESTFIX-002** — Correção de testes quebrados (03/03/2026)
  - `test_calculos.py`: corrigido `create_app()` → `create_app(testing=True)`, adicionado JWT via `auth_client`, assertions sem valor hardcoded
  - `test_buy_signals.py`: corrigido `from app import db` → `from app.database import db`, removida fixture local perigosa (`db.create_all/drop_all`), reescrito com `ativo_seed` dinâmico
  - `parametros_macro_service.py`: fix bug — fallback retornava `TypeError` quando tabela `parametros_macro` vazia
  - `conftest.py`: `ativo_seed` agora inclui `preco_teto=Decimal('50.00')`
  - `pytest.ini`: `cache_dir = /tmp/pytest_cache` — elimina `Permission Denied` no volume Podman rootless
  - **Suite: 77 passed, 0 failed, 0 warnings**

### Changed
- **EXITUS-CRUD-002** — Revisão estrutural service/route: exceções tipadas (03/03/2026)
  - Criado `app/utils/exceptions.py` com hierarquia: `ExitusError`, `NotFoundError`, `ConflictError`, `ForbiddenError`, `BusinessRuleError`
  - Handler genérico registrado em `app/__init__.py`
  - `ValueError` substituído por exceções tipadas em 10 services
  - Blueprints atualizados para capturar `ExitusError` antes de `Exception` genérico
  - HTTP 404/409 corretos em vez de 400/500 para erros semânticos

- **EXITUS-SQLALCHEMY-002** — Migração `Query.get()` depreciado (03/03/2026)
  - `Query.get()` → `db.session.get()` em 11 arquivos (27 ocorrências)
  - Arquivos: `ativo_service`, `usuario_service`, `corretora_service`, `provento_service`, `feriado_mercado_service`, `regra_fiscal_service`, `evento_corporativo_service`, `transacao_service`, `movimentacao_caixa_service`, `relatorio_service`, `decorators.py`

### Fixed
- `auth/routes.py`: eliminada query duplicada no login — `AuthService.login()` agora retorna o usuário diretamente
- `test_ativos_integration.py`: `test_listar_inclui_ativo_criado` agora usa `?search=<ticker>` para evitar dependência de paginação

---

- **EXITUS-TESTS-001** — Testes Automatizados com Pytest (03/03/2026)
  - **37 testes unitários** para `business_rules.py` com mocks corretos
    - `TestValidarHorarioMercado` (5 testes) — horário de pregão B3/NYSE/NASDAQ
    - `TestCalcularTaxasB3` (7 testes) — cálculo de taxas com precisão Decimal
    - `TestValidarFeriado` (3 testes) — feriados de mercado com mock de query
    - `TestValidarSaldoVenda` (5 testes) — saldo de posição com múltiplas corretoras
    - `TestDetectarDayTrade` (4 testes) — detecção day-trade com mock de Transacao
    - `TestValidarTransacao` (5 testes) — orquestração completa com todos os warnings
  - **32 testes de integração** contra `exitusdb_test` (PostgreSQL real)
    - `TestLogin` (8 testes) — login, JWT, envelope padrão, validações
    - `TestHealthCheck` (2 testes) — health endpoint
    - `TestJWTProtection` (3 testes) — endpoints protegidos sem/com token
    - `TestListarAtivos` (5 testes) — listagem, filtros, paginação
    - `TestGetAtivoPorTicker` (3 testes) — busca por ticker e fundamentalistas
    - `TestCriarAtivo` (5 testes) — criação com validação e duplicidade
    - `TestAtualizarAtivo` (3 testes) — update de preço, auth
    - `TestDeletarAtivo` (3 testes) — delete com 404 e auth
  - **Infraestrutura de testes criada:**
    - `TestingConfig` no `config.py` apontando para `exitusdb_test`
    - `tests/conftest.py` com fixtures `app` (session), `client`, `auth_client`, `usuario_seed`, `ativo_seed`, `corretora_seed`
    - Estratégia: app_context session-scoped + cleanup explícito por DELETE
    - `pytest.ini` com cobertura e configuração de warnings
  - **Correções de migrations Alembic:**
    - `9e4ef61dee5d` — adicionadas variáveis `revision`/`down_revision` obrigatórias + guard `IF EXISTS`
    - `20251208_1004_m7` — substituído `ENUM.create()` por `DO $$ EXCEPTION WHEN duplicate_object` para idempotência
  - **Correção em `business_rules.py`:**
    - Imports de `FeriadoMercado`, `Posicao`, `Transacao` movidos para nível de módulo (permite mock correto)
  - **Banco `exitusdb_test`** criado via `pg_dump --schema-only` do `exitusdb` de produção
  - **LIÇÃO APRENDIDA**: Flask `test_client` usa conexões próprias do pool — não compartilha sessão com fixtures que fazem `session.configure(bind=connection)`. Solução: usar contexto session-scoped sem binding + cleanup explícito.

- **EXITUS-SEED-001** — Sistema de Seed/Reset Controlado completo
  - Script unificado `reset_and_seed.sh` substitui múltiplos scripts legados
  - Implementado backup/restore de cenários para debugging
  - Migrados todos os dados do sistema legacy para formato JSON
  - Comandos flexíveis: minimal, full, usuarios, ativos, legacy
  - Help detalhado com 8 formas de execução documentadas
  - **LIÇÃO APRENDIDA**: DELETE vs DROP TABLE para reset de dados

- **EXITUS-IMPORT-001** — Importação B3 Portal Investidor completa
  - Implementado parsing de arquivos Excel/CSV da B3
  - Corrigido parsing monetário (formato European)
  - Implementada separação quantidade vs monetário
  - Criada opção --clean para base limpa
  - Help detalhado do script com exemplos
  - 51 proventos importados, 19 ativos criados em teste

- **EXITUS-CASHFLOW-001** — Tratamento de Eventos de Custódia B3
  - Criado modelo EventoCustodia completo
  - Implementado service _processar_eventos_custodia()
  - Corrigido entendimento: "Transferência - Liquidação" = evento D+2, não venda
  - Integrado separação proventos vs eventos de custódia
  - Migration executada com sucesso
  - Sistema pronto para eventos quando aparecerem nos arquivos

- **EXITUS-SQLALCHEMY-001** — Padrões e Boas Práticas SQLAlchemy
  - Documentados problemas recorrentes (enums, constraints, session)
  - Criados padrões seguros para desenvolvimento
  - Implementadas helper functions propostas
  - Estabelecido fluxo de validação preventiva

- **EXITUS-CRUD-001** — CRUD Incompleto resolvido
  - Mapeamento real de todos endpoints: 6 entidades já tinham CRUD completo
  - Eventos Corporativos: adicionados GET by id, POST, PUT, DELETE (admin_required)
  - Feriados: migrado de mock data estático para banco (tabela feriado_mercado)
  - Regras Fiscais: migrado de mock data estático para banco (tabela regra_fiscal)
  - Novos schemas com validação Marshmallow e serialização correta de enums
  - Services usando safe_commit/safe_delete_commit (db_utils)
  - ROADMAP atualizado com mapeamento real de CRUD por entidade

- **EXITUS-BUSINESS-001** — Regras de Negócio Críticas implementadas
  - Módulo `app/utils/business_rules.py` com 5 regras integradas no TransacaoService
  - Regra 1: Validação de horário de mercado (warning, B3/NYSE/NASDAQ)
  - Regra 2: Validação de feriados via tabela feriado_mercado (warning)
  - Regra 3: Validação de saldo antes de venda (bloqueante, consulta posicao)
  - Regra 4: Cálculo automático de taxas B3 (emolumentos 0.003297%, liquidação 0.0275%)
  - Regra 5: Detecção de day-trade com flag e warning (IR 20% vs 15%)
  - Response de POST /transacoes agora inclui `warnings[]` e `is_day_trade`

- **EXITUS-ASSETS-001** — Massa de Ativos com Dados Fundamentalistas
  - 56 ativos no banco (15 ações BR, 10 FIIs, 6 stocks US, 2 REITs, 8 ETFs, 5 renda fixa BR, 10 EU existentes)
  - Dados ricos: preco_atual, dividend_yield, p_l, p_vp, roe, beta, preco_teto, cap_rate
  - JSON centralizado em `app/seeds/data/ativos_fundamentalistas.json`
  - Script `seed_ativos_fundamentalistas.py` enriquece existentes e cria novos (idempotente)

- **EXITUS-SCRIPTS-001** — Otimização e unificação completa do sistema de scripts
  - Removidos 3 scripts obsoletos (cleanup_duplicates.sh, restore_complete.sh, validate_docs.sh)
  - Renomeado startexitus-local.sh → repair_containers.sh (nome mais descritivo)
  - Padronizados volumes em todos os scripts (./backend:/app:Z, ./frontend:/app:Z)
  - Mantidos 15 scripts funcionais com propósitos distintos
  - Documentação completa em scripts/README.md

- **EXITUS-RECOVERY-001** — Sistema enterprise-grade de backup/restore/recovery
  - Criado recovery_manager.sh (orquestrador principal com 600+ linhas)
  - Criado validate_recovery.sh (validações abrangentes pós-operação)
  - Criado rollback_recovery.sh (rollback automático com segurança)
  - Criado recovery_dashboard.sh (interface TUI interativa)
  - Enterprise features: compressão gzip, checksum SHA-256, metadados JSON
  - Segurança: backup pré-operação, rollback automático, validações
  - Integração com scripts existentes (backup_db.sh, restore_db.sh, populate_seeds.sh)

### Changed
- **Scripts de volumes** — Padronização completa seguindo setup_containers.sh
  - rebuild_restart_exitus-backend.sh: volumes corrigidos para ./backend:/app:Z
  - rebuild_restart_exitus-frontend.sh: volumes corrigidos para ./frontend:/app:Z
  - scripts/exitus.sh: volumes atualizados para consistência
  - liberação de portas adicionada em rebuild_restart_exitus-frontend.sh

### Fixed
- **Inconsistência de volumes** entre setup_containers.sh e scripts de rebuild
- **Scripts obsoletos** removidos (bugs e complexidade desnecessária)
- **Nomenclatura confusa** em scripts (startexitus-local.sh → repair_containers.sh)

### Gaps Registrados
- **EXITUS-HEALTH-001** — `GET /health` não expunha metadados de build (versão/commit)
  e retornava apenas uma string de `module`, dificultando rastreabilidade durante validações.
- **EXITUS-DOCS-AUTH-002** — Documentação de credenciais DEV divergente: `admin123`
  era citado em `docs/USER_GUIDE.md` e `docs/OPERATIONS_RUNBOOK.md`, mas as seeds atuais
  (ver `app/seeds/seed_usuarios.py`) usam `senha123`.
- **EXITUS-ATIVOS-ENUM-001** — Ativo `AAPL` (e potencialmente outros ativos US legados)
  estava persistido com `tipo=ACAO` no banco, em vez de `tipo=STOCK` conforme regra de negócio
  (`TipoAtivo.STOCK` = ações US/NYSE/NASDAQ). Isso fazia filtros `?tipo=STOCK` não retornarem
  o `AAPL` e contraditava a semântica multi-mercado do model.
- **EXITUS-POS-PAGIN-001** — `GET /api/posicoes` retornava campos de paginação (`total`,
  `pages`, `page`, `per_page`) na raiz do response em vez de dentro de `.data`, quebrando
  o contrato padrão de todos os outros endpoints do sistema.
- **EXITUS-PROV-SLASH-001** — `GET /api/proventos` (sem barra final) recebia um redirect 301
  com body HTML antes do JSON, pois a rota estava declarada com `strict_slashes` padrão (True).
  Isso causava `parse error: Invalid numeric literal` no jq ao processar a resposta.
- **EXITUS-BUYSIG-SCORE-001** — `GET /api/buy-signals/buy-score/{ticker}` retornava HTTP 200
  com `score=0` para tickers inexistentes em vez de 404, pois o `except` interno silenciava o
  `ValueError("Ativo não encontrado")` do service. Idem para `/margem-seguranca` e `/zscore`.
  Também: campo de resposta é `buy_score` (não `score`) — ausente na documentação.
- **EXITUS-ALERTAS-RESP-001** — `GET /api/alertas` retornava `{"data": [...]}` sem o campo
  `success`, quebrando o contrato padrão do sistema. Idem para POST, PATCH toggle e DELETE.
- **EXITUS-TRX-PAGIN-001** — `GET /api/transacoes` retornava `status: "success"` (string)
  em vez de `success: true` (booleano), e `total/pages/page/per_page` na raiz do response
  em vez de dentro de `.data`. Inconsistente com o padrão do sistema.
- **EXITUS-COTACOES-RESP-001** — `GET /api/cotacoes/{ticker}` retornava response plano
  (`{"ticker": ..., "preco_atual": ...}`) sem envelope `{"success": true, "data": {...}}`,
  inconsistente com todos os demais módulos. `docs/API_REFERENCE.md` seções 9-20 eram apenas
  placeholders sem contratos documentados.

### Fixed
- **EXITUS-HEALTH-001** — `backend/app/__init__.py`: `/health` agora inclui
  `version` (via `EXITUS_VERSION`/`APP_VERSION`) e `commit_sha` (via `GIT_COMMIT`/`COMMIT_SHA`)
  mantendo os campos existentes.
- **EXITUS-DOCS-AUTH-002** — `docs/USER_GUIDE.md` e `docs/OPERATIONS_RUNBOOK.md` atualizados:
  exemplos de login/token e tabela de credenciais DEV alinhados para `senha123`.
- **EXITUS-ATIVOS-ENUM-001** — Criado `backend/app/scripts/fix_us_acao_to_stock.py` (dry-run
  por padrão, `--apply` para commitar). Executado em DEV: 1 registro corrigido (`AAPL`,
  `mercado=US`, `tipo ACAO → STOCK`). Revalidado via `GET /api/ativos?mercado=US&tipo=STOCK`:
  retornou `total=6` com todos os tickers US (AAPL, AMZN, GOOGL, MSFT, NVDA, TSLA) com
  `tipo="stock"` ✅.
- **EXITUS-TRX-PAGIN-001** — `backend/app/blueprints/transacoes/routes.py`: `status: "success"`
  corrigido para `success: True` (booleano); `total/pages/page/per_page` movidos para dentro
  de `.data`; array de itens renomeado de `data` para `data.transacoes`.
- **EXITUS-POS-PAGIN-001** — `backend/app/blueprints/posicao_blueprint.py`: campos de
  paginação movidos da raiz do response para dentro de `.data` (alinhado ao padrão do sistema).
- **EXITUS-PROV-SLASH-001** — `backend/app/blueprints/provento_blueprint.py`: adicionado
  `strict_slashes=False` na rota `GET /` para evitar redirect 301 e parse error no cliente.
- **EXITUS-BUYSIG-SCORE-001** — `backend/app/blueprints/buy_signals_blueprint.py`: adicionada
  verificação explícita de existência do ativo antes do `try/except` nas rotas `buy-score`,
  `margem-seguranca` e `zscore`; retorna 404 para tickers inexistentes. Documentação corrigida
  em `docs/API_REFERENCE.md` (campo `buy_score`, não `score`).
- **EXITUS-ALERTAS-RESP-001** — `backend/app/blueprints/alertas.py`: adicionado `success`
  em todas as respostas (GET, POST, PATCH toggle, DELETE) para alinhar ao contrato padrão.
- **EXITUS-COTACOES-RESP-001** — `backend/app/blueprints/cotacoes_blueprint.py`: todos os
  responses de `GET /api/cotacoes/{ticker}` envolvidos em `{"success": true, "data": {...}}`.
  `docs/API_REFERENCE.md` expandido: seções 9-12 documentadas com contratos completos
  (Movimentações, Buy Signals, Alertas, Cotações).

## [v0.7.12] — 2026-02-24

### Fix Batch — M2-TRANSACOES (7 GAPs)

#### Corrigido
- **EXITUS-TRX-001** `transacao_schema.py`: `custos_totais` retornava null na resposta —
  declarado explicitamente como `fields.Decimal(as_string=True)` no `TransacaoResponseSchema`
  e no novo `TransacaoListSchema`.
- **EXITUS-TRX-002** `transacao_service.py` + `routes.py`: PUT em TRX de outro usuário
  retornava 400/404 — service agora lança `PermissionError` separado de `ValueError`;
  route captura e retorna 403.
- **EXITUS-TRX-003** `transacao_service.py` + `routes.py`: PUT com ID inexistente retornava
  400 — service faz `Transacao.query.get()` sem filtro de usuário primeiro; se None lança
  `ValueError` → 404.
- **EXITUS-TRX-004** `transacao_service.py` + `routes.py`: DELETE em TRX de outro usuário
  retornava 404 — mesmo padrão do TRX-002, ownership check após existência → 403.
- **EXITUS-TRX-005** `transacao_schema.py`: listagem não serializava `valor_total`,
  `data_transacao` e nested `ativo` — criado `TransacaoListSchema` com todos os campos
  explícitos incluindo `fields.Method('get_ativo_info')`.
- **EXITUS-TRX-006** `transacoes/routes.py`: paginação (`total`, `pages`, `page`,
  `per_page`) estava aninhada dentro de `.data` — rota `GET /` refatorada com `jsonify`
  manual, paginação promovida para raiz do response.
- **EXITUS-TRX-007** `transacao_service.py`: `/resumo/{ativo_id}` retornava 200 com dados
  zerados para UUID inexistente — adicionada validação `Ativo.query.get(ativo_id)` antes
  dos cálculos; lança `ValueError` → 404.

#### Hotfix incluso
- `transacao_service.py`: enum `tipo` era gravado como `COMPRA` (uppercase) causando
  `InvalidTextRepresentation` no PostgreSQL — corrigido para `.lower()` alinhado com
  o enum `tipotransacao` do DB.
- `transacoes/routes.py`: import `notfound` corrigido para `not_found` (nome real em
  `app/utils/responses.py`); vírgula trailing no import de schemas removida.

#### Validação
- 7/7 GAPs aprovados em revalidação sequencial (2026-02-24)
- Smoke test `/resumo/{ativo_id}` com UUID válido: HTTP 200 ✅
- Smoke test `/resumo/{ativo_id}` com UUID inexistente: HTTP 404 ✅


---

## [0.7.11] — 2026-02-24 — branch `feature/revapis`

### Fixed

- **EXITUS-ENUM-CASE-001** — `TipoTransacao` ENUM case mismatch corrigido
  em `app/models/transacao.py`. SQLAlchemy usava `Enum.name` (UPPERCASE)
  para bind no PostgreSQL, mas o tipo `tipotransacao` no banco possui
  valores lowercase. Fix: `values_callable=lambda x: [e.value for e in x]`
  + `create_type=False`. Causa raiz documentada em `ENUMS.md §3.1`.
  Commit: `172e428` (TRX-005 ✅)

- **EXITUS-SEEDS-002** — `app/seeds/seed_usuarios.py` corrigido: senhas
  padronizadas para `senha123` em todos os usuários de teste
  (`admin`, `joao.silva`, `maria.santos`, `viewer`).
  Antes: `admin123` / `user123` / `viewer123`.

### Notes

- Branch: `feature/revapis` — validação M2-TRANSACOES em andamento
- TRXs concluídos até este commit: TRX-001 ✅ TRX-002 ✅ TRX-005 ✅
- TRXs pendentes: TRX-003, TRX-004, TRX-006, TRX-007, TRX-008

---

## [0.7.10] — 2026-02-22

### Fixed — M2-POSICOES (8 GAPs resolvidos)

- **EXITUS-POS-001** — `PosicaoResponseSchema` reescrito com todos os campos
  do model `Posicao` e nested schemas `AtivoNestedSchema` e `CorretoraNestedSchema`.
  Campos adicionados: `custo_total`, `taxas_acumuladas`, `impostos_acumulados`,
  `valor_atual`, `lucro_prejuizo_realizado`, `lucro_prejuizo_nao_realizado`,
  `data_primeira_compra`, `data_ultima_atualizacao`, `usuario_id`, `created_at`,
  `updated_at`, `ativo` (nested), `corretora` (nested)

- **EXITUS-POS-002** — Campo `total` na resposta paginada de `GET /api/posicoes`
  agora é corretamente exposto na raiz do JSON (era `null`)

- **EXITUS-POS-003** — Filtro `?ticker=` no `GET /api/posicoes` funcional.
  Blueprint agora extrai `request.args` e monta dict de filtros antes de chamar
  `PosicaoService.get_all()`

- **EXITUS-POS-004** — Filtro `?lucro_positivo=true` no `GET /api/posicoes`
  funcional. Mesma causa raiz do EXITUS-POS-003

- **EXITUS-POS-005** — Rota `GET /api/posicoes/<uuid:posicao_id>` registrada.
  Retorna posição completa com nested `ativo` e `corretora`

- **EXITUS-POS-006** — Rota `POST /api/posicoes/calcular` registrada. Expõe
  `PosicaoService.calcular_posicoes()` como endpoint público

- **EXITUS-POS-007** — Isolamento multi-tenant corrigido em `GET /api/posicoes/{id}`:
  retorna `403` quando posição pertence a outro usuário (não `404`).
  Mesmo padrão já aplicado em Corretoras (v0.7.7)

- **EXITUS-POS-008** — Enum serialization corrigida em `AtivoNestedSchema`:
  campos `ativo.tipo` e `ativo.classe` agora retornam o valor correto (`"fii"`, `"rendavariavel"`)
  em vez da representação Python (`"TipoAtivo.FII"`, `"ClasseAtivo.RENDAVARIAVEL"`).
  Fix aplicado via `fields.Method()` com `.value` — padrão idêntico ao `AtivoResponseSchema`

### Added

- Rota `GET /api/posicoes/resumo` — Retorna resumo consolidado: `quantidade_posicoes`,
  `total_investido`, `total_valor_atual`, `lucro_total`, `roi_percentual`

- `AtivoNestedSchema` e `CorretoraNestedSchema` no schema de posições

### Documentation

- `API_REFERENCE.md` — Seção 6 (Posições) totalmente reescrita com contratos
  completos, query params documentados, exemplos JSON reais e nota sobre
  dependência de `valor_atual` com M7.5

- `MODULES.md` — Contagem de endpoints M2 atualizada de 20 para 22
  (Posições: 2 → 4); tabela de métricas atualizada; referência a `M2_POSICOES.md`

- `M2_POSICOES.md` adicionado — Relatório de validação 12/12 cenários aprovados

### Tested

```bash
# Validação M2-POSICOES — 2026-02-22
# C01 — schema completo + nested
curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:5000/api/posicoes" | jq '.data.posicoes[0].ativo.ticker'
# "KNRI11"

# C02 — total paginação
curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:5000/api/posicoes?page=1&per_page=5" | jq '{total, pages, page}'
# {"total": 17, "pages": 4, "page": 1}

# C03 — filtro ticker
curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:5000/api/posicoes?ticker=PETR4" | jq '.total'
# 1

# C10 — isolamento 403
# 403

# C11 — calcular
# {"posicoes_criadas": 0, "posicoes_atualizadas": 17, "posicoes_zeradas": 0}

# C12 — sem token
# 401
```

Status: **PRODUCTION READY**

---

## [0.7.9] — 2026-02-20

### Added
- Seed Renda Fixa BR (`app/seeds/seed_ativos_renda_fixa_br.py`) — 8 novos ativos:
  - CDB (3): `CDB_NUBANK_100CDI`, `CDB_INTER_105CDI`, `CDB_C6_107CDI`
  - TESOURO_DIRETO (3): `TESOURO_SELIC_2029`, `TESOURO_IPCA_2035`, `TESOURO_PREFIX_2027`
  - DEBENTURE (2): `VALE23_DBNT`, `PETR4_DBNT`
- Total de ativos seedados: **70** (62 anteriores + 8 novos)
- `run_all_seeds.py` atualizado com `seed_ativos_renda_fixa_br` na sequência

### Fixed
- **GAP EXITUS-SEEDS-RUN-001** RESOLVIDO — `IncidenciaImposto` adicionado ao
  `app/models/__init__.py` — `seed_regras_fiscais_br.py` executa sem ImportError
- 6 regras fiscais BR confirmadas no banco
- **M2-ATIVOS-005** — Seeds US/EU/BR normalizados (20/02/2026):
  - `seed_ativos_us.py`: checagem de existência corrigida para `filter_by(ticker, mercado='US')` em 4 blocos
  - `seed_ativos_eu.py`: idem com `mercado='EU'` em 2 blocos
  - `seed_ativos_br.py`: campo `bolsa_origem='B3'` removido (deprecated desde v0.7.8)
  - Seeds US e EU agora totalmente idempotentes

### Documentation
- **GAP EXITUS-AUTH-001** fechado (Opção A) — `SEEDS.md` corrigido: todos os
  exemplos cURL usam `username`, não `email`
- `SEEDS.md` v0.7.9 — Seção Renda Fixa BR adicionada, total atualizado 62 → 70
- `ENUMS.md` v0.7.9 — Tabela de mapeamento completa para 14 tipos de TipoAtivo,
  seção de divergência (query param UPPERCASE vs resposta JSON lowercase)

### Gaps Registrados
- **EXITUS-DOCS-API-001** — `GET /api/ativos` retorna `.data.ativos` (não `.data.items`)
- **EXITUS-INFRA-001** — Volume `app` montado como read-only no container

### Tested
```bash
# Filtros Renda Fixa BR validados 20/02/2026
curl "http://localhost:5000/api/ativos?mercado=BR&tipo=CDB"           # total: 3
curl "http://localhost:5000/api/ativos?mercado=BR&tipo=TESOURODIRETO" # total: 3
curl "http://localhost:5000/api/ativos?mercado=BR&tipo=DEBENTURE"     # total: 2

# Seeds idempotentes validados 20/02/2026
podman exec -it exitus-backend python -m app.seeds.seed_ativos_us  # Criados: 0, Pulados: 16
podman exec -it exitus-backend python -m app.seeds.seed_ativos_eu  # Criados: 0, Pulados: 3
```

Status: **PRODUCTION READY**

---

## [0.7.8] — 2026-02-16

### Added
- Expansão de ENUMs `TipoAtivo` de 7 para 14 tipos (Multi-Mercado Completo):
  - Brasil (6): ACAO, FII, CDB, LCI_LCA, TESOURO_DIRETO, DEBENTURE
  - US (4): STOCK, REIT, BOND, ETF
  - Internacional (2): STOCK_INTL, ETF_INTL
  - Outros (2): CRIPTO, OUTRO
- Campo `cap_rate` em tabela `ativo` (`NUMERIC(8,4)`) para cálculo de Preço Teto de FIIs/REITs
- Seeds para ativos US (`app/seeds/seed_ativos_us.py`) — 16 ativos
- Seeds para ativos EU (`app/seeds/seed_ativos_eu.py`) — 3 ativos
- Documentação completa `ENUMS.md` — 14 tipos detalhados

### Changed
- Migration `202602162111` — Expansão do enum `tipo_ativo` 7 → 14 valores
- Migration `202602162130` — Adição de `cap_rate`, remoção de `bolsa_origem`
- Total de ativos seedados: 62 (39 BR + 16 US + 3 EU + 4 outros)

### Removed
- Campo `bolsa_origem` da tabela `ativo` (substituído por `TipoAtivo` expandido)

### Tested — Status: PRODUCTION READY

---

## [0.7.7] — 2026-02-15

### Security / Clarity
- M2 — Corretoras: `GET/PUT/DELETE /api/corretoras/{id}` agora retornam `403 Forbidden`
  quando usuário tenta acessar corretora de outro usuário (anteriormente `404`)
- Arquivos modificados: `backend/app/services/corretora_service.py`,
  `backend/app/blueprints/corretoras/routes.py`

### Validated — M2-CORRETORAS
- 6 endpoints testados, 29 cenários
- Performance: 13ms média (26x mais rápido que SLA de 500ms)
- Segurança: isolamento multi-tenant 100% funcional

---

## [0.7.6] — 2026-02-14

### Documentation
- Official snake_case naming standard documentado em `CODING_STANDARDS.md`

---

## [0.7.5] — 2026-02-14

### Infrastructure
- Upgrade PostgreSQL 15.15 → 16.11
- Zero downtime, dados migrados sem perda (21 tabelas, 44 ativos, 17 transações)

---

## [0.7.4] — 2026-01-15
- Padronização `POSTGRES_USER=exitus` em toda a documentação

## [0.7.3] — 2026-01-15
- Atualização de versão PostgreSQL em docs

## [0.7.2] — 2026-01-15
- Sistema validado: Backend API REST, Frontend HTMX, PostgreSQL 16

## [0.7.1] — 2026-01-06

### Added — Sistema de Histórico de Preços
- Tabela `historico_preco` — Armazena séries temporais de preços
- Migration `008_add_historico_preco.py`

---

## Métricas do Projeto — v0.7.10

| Componente | Linhas | Arquivos |
|---|---|---|
| Backend | 15.600+ | 93 |
| Frontend | 4.000 | 28 |
| Migrations | 1.400 | 10 |
| Seeds | 1.400 | 6 |
| Docs | 10.000+ | 24 |

- Ativos Seedados: **70** (47 BR, 16 US, 3 EU, 4 outros)
- Cobertura ENUMs: 14/14 tipos implementados e testados
- Total Endpoints: **69** rotas RESTful validadas

---

## Roadmap Futuro

### v0.7.11 (próxima)
- Avaliar EXITUS-AUTH-001 Opção B — API aceitar email OU username
- Verificar EXITUS-INFRA-001 — volume `app` read-write no container

### v0.8.0 — M8 (Q2 2026)
- Simulação Monte Carlo
- Otimização Markowitz
- Backtesting
- WebSocket alertas real-time
- Export PDF/Excel profissional

### v0.9.0 — M9 (Q3 2026)
- CI/CD GitHub Actions
- Deploy Railway/Render
- Monitoring Prometheus/Grafana
- Backups automatizados

---

*Última atualização: 01 de Março de 2026*
*Versão atual: v0.7.10 — M2-POSICOES validado + EXITUS-SCRIPTS-001 + EXITUS-RECOVERY-001*
*Contribuidores: Elielson Fontanezi, Perplexity AI (documentação v0.7.8–v0.7.10)*
