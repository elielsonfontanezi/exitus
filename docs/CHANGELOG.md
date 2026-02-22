# Changelog — Sistema Exitus

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.
O formato é baseado em [Keep a Changelog](https://keepachangelog.com/),
e este projeto adere semanticamente à versão v0.7.10.

---

## [0.7.10] — 2026-02-22

### Fixed — M2-POSICOES (7 GAPs resolvidos)

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

### Known Issues (não-bloqueantes)

- **EXITUS-POS-008** (novo) — `ativo.tipo` e `ativo.classe` no nested de posições
  retornam com prefixo Python (`"TipoAtivo.FII"` em vez de `"fii"`).
  `AtivoNestedSchema` usa `fields.Str()` direto — serializa `repr()` do enum.
  Fix: usar `fields.Method()` com `.value` no `AtivoNestedSchema`.
  Prioridade: 🟡 Baixa — não bloqueia funcionalidade

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
curl "http://localhost:5000/api/ativos?mercado=BR&tipo=CDB"        # total: 3
curl "http://localhost:5000/api/ativos?mercado=BR&tipo=TESOURODIRETO" # total: 3
curl "http://localhost:5000/api/ativos?mercado=BR&tipo=DEBENTURE"  # total: 2

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
- Corrigir EXITUS-POS-008 — enum serialization em nested (AtivoNestedSchema)
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

*Última atualização: 22 de Fevereiro de 2026*
*Versão atual: v0.7.10 — M2-POSICOES validado (7 GAPs fechados)*
*Contribuidores: Elielson Fontanezi, Perplexity AI (documentação v0.7.8–v0.7.10)*
