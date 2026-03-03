# Changelog — Sistema Exitus

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.
O formato é baseado em [Keep a Changelog](https://keepachangelog.com/),
e este projeto adere semanticamente à versão v0.8.0.

---

## [Unreleased]

### Added
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
