# AI Operations — Sistema Exitus

> **Propósito:** Manual operacional estendido para o Cursor Agent.  
> **Fonte canônica de regras inegociáveis:** `.cursorrules` (raiz do repositório).  
> **Versão:** 1.3 — 29/06/2026  
> **Nota:** `.windsurfrules` descontinuado (CURSORRULES-001); regras inegociáveis em `.cursorrules`.

---

## Plano de controle (próximas atualizações)

Consultar estes docs para **o que fazer** — não duplicar conteúdo aqui.

| Documento | Pergunta | Quando |
|-----------|----------|--------|
| `docs/ROADMAP.md` | Qual GAP vem agora? Dependências? | Início de sessão; antes de propor implementação |
| `docs/AUDITORIA_FUNCIONAL.md` | Quais telas PARCIAL/QUEBRADO? P-items? | Tarefa frontend, UX, integração de tela |
| `docs/PROJECT_STATUS.md` | Versão, testes, progresso geral? | Checkpoint, métricas, commit |
| `docs/CHANGELOG.md` | O que já foi entregue? | Contexto histórico |

Atualizar `AUDITORIA_FUNCIONAL.md` no commit quando resolver P-item ou mudar status de tela (REGRA #6).

---

## Índice de lições por domínio

Consultar `docs/LESSONS_LEARNED.md` — **nunca duplicar** lições neste arquivo.

| Domínio | IDs relevantes |
|---------|----------------|
| Frontend / API URL | L-FE-011, L-FE-010, L-FE-009 |
| Frontend / templates | L-FE-001 a L-FE-008, L-FE-012 |
| Database / migrations | L-DB-015, L-MIG-001, L-DB-008, L-DB-014 |
| Backend / services | L-BE-001, L-SA-001 |
| Testes | L-TEST-001 a L-TEST-005 |
| Documentação | L-DOCS-001 |
| Multi-tenant / segurança | L-SEC-001 |
| Operações IA | L-OPS-001 |

---

## Modelos IA (REGRA #3)

Ao iniciar qualquer GAP, indicar obrigatoriamente:

```
[IDENTIFICAÇÃO DO CENÁRIO]: [tipo da tarefa]
Modelo free (custo zero): [MODELO] (Free)
Modelo recomendado (menor custo): [MODELO] ($/$$/$$$)
Modelo ideal (melhor resultado): [MODELO] ($/$$/$$$)
Justificativa: [1 linha]
```

**Regra:** "Modelo free" deve ser o melhor modelo gratuito para o cenário específico da tarefa.

### Modelos Cursor (referência 29/06/2026)

Usar esta tabela ao indicar modelo na REGRA #3. Adaptar se novos modelos forem adicionados ao Cursor.

| Tipo de tarefa | Free | Recomendado ($) | Ideal ($$) |
|----------------|------|-----------------|------------|
| CRUD / refatoração | — | Composer 2.5 Fast | GPT-5.3 Codex |
| Lógica / testes | GLM 5.2 | GPT-5.2 / Gemini 3.1 Pro | Sonnet 4.6 |
| Arquitetura | GLM 5.2 | GPT-5.4 | Opus 4.8 |
| Code review / segurança | GLM 5.2 | Codex 5.1 Max | Sonnet 4.6 |
| Debug financeiro | GLM 5.2 | Codex 5.3 | Opus 4.8 |
| Contexto extenso | Kimi K2.5 | Gemini 3.5 Flash | Opus 1M |

---

### Referência histórica (Windsurf/Devin)

**Nota:** Tabela abaixo preservada para contexto de CHANGELOG. **Preferir a tabela Cursor acima** na operação diária.

### Tabela de Modelos Disponíveis

**FREE (Custo Zero):** SWE-1.5, GLM 5.2, Kimi K2.5

**$ (Baixo Custo):** SWE-1.5 Fast, GPT-5.1, GPT-5.2, GPT-5.4 Mini, Codex 5.1 Mini, Codex 5.2, Grok Code Fast 1, Gemini 2.5 Pro, Gemini 3 Flash, Gemini 3.1 Pro Low Thinking

**$$ (Custo Médio):** Composer 2.5, GPT-5.4, GPT-5.5, Sonnet 4.6, Gemini 3.1 Pro High Thinking, DeepSeek V4

**$$$ (Alto Custo):** Opus 4.7, Opus 4.8, Claude Opus Thinking, Claude Opus 1M

### Recomendações por Tipo de Tarefa

| Tipo | Melhor Free | Menor custo | Ideal |
|------|-------------|---------------|-------|
| CRUD / refatoração pontual | SWE-1.5 | Codex 5.1 Mini | Codex 5.2 |
| Lógica de negócio / testes | GLM 5.2 | GPT-5.2 | Sonnet 4.6 |
| Arquitetura / decisões críticas | GLM 5.2 | GPT-5.4 | Opus 4.8 |
| Code review / segurança | GLM 5.2 | Codex 5.1 Max | Sonnet 4.6 |
| Debugging financeiro | GLM 5.2 | Codex 5.3 | Opus 4.8 |
| Contexto extenso | Kimi K2.5 | Gemini 3.5 Flash | Opus 1M |

**Regra de ouro:** Começar com free ou menor custo adequado; escalar conforme impacto do código.

---

## Formato de commit (REGRA #5)

Apresentar ao usuário antes de executar; aguardar aprovação explícita:

```bash
git add -A
git commit -m "feat(módulo): EXITUS-XXX-000 — resumo em uma linha

GAPs: EXITUS-XXX-000
- Artefato A: descrição
- Artefato B: descrição
- docs: arquivos atualizados
- Suite: N passed, M failed (pré-existentes), K skipped"
```

Tipos: `feat` / `fix` / `docs` / `refactor` / `test` — uma atividade por commit.

---

## MCP PostgreSQL (REGRA #3.1)

Conexão: `postgresql://exitus:exitus123@127.0.0.1:5433/exitusdb`  
Configuração: `.cursor/mcp.json` e `.cursor/mcp_postgres.sh`  
Server ID no Cursor: `project-0-exitus-postgres` — tool `query` (SQL read-only)

### Quando acionar

1. **Refatoração:** ler schema real antes de alterar models/ORM
2. **Debugging:** inspecionar registros reais em bugs de cálculo/saldo
3. **Testes:** validar dados simulados vs constraints/enums do banco

### Atalhos

- Schema estático: `docs/EXITUS_DB_STRUCTURE.txt`
- Resources MCP: `list_resources` / `read_resource` na tabela desejada
- Query direta: tool `query` com SQL read-only

---

## MCP Browser (Cursor)

Server: `cursor-ide-browser`  
Uso: testes E2E, debug de frontend, screenshots

Fluxo recomendado: `browser_navigate` → `browser_lock` → interações → `browser_unlock`  
Preferir `browser_snapshot` antes de cliques; `browser_take_screenshot` para verificação visual.

---

## Métricas de testes

**Nunca citar números fixos sem rodar a suite.** Consultar `docs/PROJECT_STATUS.md`.

Baseline atual (29/06/2026): **565 passed, 3 failed, 6 skipped** (98,4%)

```bash
podman exec exitus-backend python -m pytest --no-cov -q
```

Falhas pré-existentes conhecidas: `test_circuit_breaker.py` (×2), `test_ir_integration.py` (IR 2026+).

---

## Scripts disponíveis (`scripts/`)

### Containers

- `scripts/start_exitus.sh` — iniciar todos
- `scripts/stop_exitus.sh` — parar todos
- `scripts/restart_exitus.sh` — restart completo
- `scripts/restart_backend.sh` — restart só backend (pós-código Python)
- `scripts/restart_frontend.sh` — restart só frontend
- `scripts/setup_containers.sh` — setup inicial
- `scripts/repair_containers.sh` — reparar containers
- `scripts/cleanup_containers.sh` — remover containers e volumes
- `scripts/rebuild_restart_exitus-backend.sh`
- `scripts/rebuild_restart_exitus-frontend.sh`

### Banco de dados

- `scripts/create_test_db.sh` — recriar `exitusdb_test` (obrigatório pós-migration)
- `scripts/update_db_structure.sh` — gerar `docs/EXITUS_DB_STRUCTURE.txt` (REGRA #9)
- `scripts/backup_db.sh` / `scripts/restore_db.sh`

### Seeds e dados

- `scripts/populate_seeds.sh` — todos os seeds
- `scripts/reset_and_seed.sh` / `scripts/reset_and_seed.py`
- `scripts/import_b3.sh` / `scripts/import_b3.py`

### Utilitários

- `scripts/get_backend_token.sh` — JWT para testes de API
- `scripts/generate_api_docs.sh`
- `scripts/setup_env.sh`
- `scripts/exitus.sh` — orquestração principal

### Recovery

- `scripts/recovery_manager.sh`
- `scripts/recovery_dashboard.sh`
- `scripts/validate_recovery.sh`
- `scripts/rollback_recovery.sh`

### Comandos frequentes

```bash
podman ps
podman logs -f exitus-backend
podman exec -it exitus-backend bash
export TOKEN=$(bash scripts/get_backend_token.sh)
bash scripts/restart_backend.sh
./scripts/update_db_structure.sh
```

---

## Migrations (L-MIG-001)

Diretório ativo: `backend/migrations/versions/` (Flask-Migrate).  
**Não usar** `backend/alembic/` — dívida técnica CLEANUP-MIGRATIONS-001 (L-DB-015).

```bash
# Banco dev
podman exec exitus-backend flask db upgrade

# Banco teste — paridade DDL obrigatória
./scripts/create_test_db.sh
# ou ALTER TABLE manual em exitusdb_test
```

Após qualquer DDL: `./scripts/update_db_structure.sh`

---

## Checklist de início de atividade

- [ ] Li `docs/LESSONS_LEARNED.md`?
- [ ] Estou em Plan mode até "APROVADO"? (REGRA #2)
- [ ] Indiquei modelo de IA? (REGRA #3)
- [ ] Apresentei estratégia e aguardei "APROVADO"? (REGRA #4)
- [ ] Sei quais docs atualizar? (REGRA #6)
- [ ] Altera banco? → `flask db upgrade` + `exitusdb_test` + `update_db_structure.sh`
- [ ] Novo blueprint? → padrão A/B + `app/__init__.py` com try/except
- [ ] Chaves de API? → variáveis de ambiente, nunca no código

---

## Checklist models/banco

- [ ] Li `models/nome_model.py` completo?
- [ ] PKs são UUID — nunca resetar sequences
- [ ] `DELETE` para dados, nunca `DROP TABLE` para reset
- [ ] `db.session.get(Model, pk)` — não `Model.query.get(pk)` (depreciado)
- [ ] Schema real: MCP Postgres ou `EXITUS_DB_STRUCTURE.txt`

---

## Blueprints e estrutura

- **Padrão A (recomendado):** pasta + `routes.py` (ex: `blueprints/nome/routes.py`)
- **Padrão B (legacy):** arquivo único (ex: `blueprints/nome_blueprint.py`)
- Registrar em `app/__init__.py` com try/except para fallback

---

## Testes formais

Diretório: `backend/tests/` — **nunca remover** arquivos desta pasta.

Principais: `test_darf_acumulado.py`, `test_rentabilidade.py`, `test_import_b3_parsers.py`, `test_ir_integration.py`

Scripts temporários na raiz: remover após validação.

---

## Chaves de API

Nunca escrever chaves no código Python. Usar variáveis de ambiente.

---

## Módulos e endpoints

Consultar `docs/PROJECT_STATUS.md` e `docs/MODULES.md` para contagens atuais (versão, endpoints, tabelas). Não duplicar números neste arquivo.

---

## Validação migração `.windsurfrules` → `.cursorrules`

Executar após CURSORRULES-001 para confirmar que referências operacionais foram migradas:

```bash
# 1. Arquivo legado removido
test ! -f .windsurfrules && echo "PASS: .windsurfrules removido"

# 2. Stub MODULES ativo
test -f docs/MODULES.md && echo "PASS: docs/MODULES.md existe"

# 3. .cursorrules enxuto (v3.x)
LINES=$(wc -l < .cursorrules)
test "$LINES" -le 200 && echo "PASS: .cursorrules tem $LINES linhas (<= 200)"

# 4. Zero refs operacionais fora de histórico (archive + CHANGELOG + LESSONS + ROADMAP + PROJECT_STATUS + este arquivo)
REFS=$(rg '\.windsurfrules' \
  --glob '!docs/archive/**' \
  --glob '!docs/CHANGELOG.md' \
  --glob '!docs/AI_OPERATIONS.md' \
  --glob '!docs/LESSONS_LEARNED.md' \
  --glob '!docs/ROADMAP.md' \
  --glob '!docs/PROJECT_STATUS.md' \
  -c 2>/dev/null | awk -F: '{s+=$2} END {print s+0}')
test "$REFS" -eq 0 && echo "PASS: 0 refs operacionais a .windsurfrules" || echo "FAIL: $REFS refs restantes"

# 5. Sem refs Cascade operacionais em docs ativos (excluir este arquivo e LESSONS — contêm o script)
rg 'Cascade AI|Para Próxima Sessão Cascade' docs/ \
  --glob '!archive/**' \
  --glob '!CHANGELOG.md' \
  --glob '!AI_OPERATIONS.md' \
  --glob '!LESSONS_LEARNED.md' \
  -q \
  && echo "FAIL: refs Cascade operacionais restantes" || echo "PASS: sem refs Cascade operacionais"

# 6. Novo caminho presente nos docs operacionais
rg '\.cursorrules' docs/PERSONAS.md docs/LESSONS_LEARNED.md docs/AUDITORIA_FUNCIONAL.md -q \
  && echo "PASS: .cursorrules referenciado nos docs operacionais"
```

**Mapeamento de caminhos:**

| Antes | Depois |
|-------|--------|
| `.windsurfrules` (regras inegociáveis) | `.cursorrules` |
| `.windsurfrules` REGRA #3 (modelos IA) | `docs/AI_OPERATIONS.md` § Modelos IA |
| `.windsurfrules` REGRA #8 (scripts/MCPs) | `docs/AI_OPERATIONS.md` § Scripts / MCPs |
| `.windsurf/mcp_postgres.sh` | `.cursor/mcp_postgres.sh` |
| `@mcp0_browser_*` / playwright | `cursor-ide-browser` |
| Cascade / Windsurf | Cursor Agent |
