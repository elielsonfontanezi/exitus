
# Exitus – Proposta de Nova Documentação Unificada (Pós‑M7)

## Objetivos da Revisão

- Remover redundâncias entre README, READMEs parciais e dezenas de docs de módulo.[file:1][file:5]
- Criar um **núcleo enxuto** de documentação para onboarding rápido, deixando detalhes profundos em anexos temáticos.[file:7]
- Preparar terreno para M8+ (APIs de mercado, analytics avançado) sem reescrever tudo a cada módulo.[file:1]

---

## Arquitetura Proposta de Documentação

### 1. `README.md` (Visão Geral Executiva)

Função: Landing page do GitHub – explicar o que é o Exitus, mostrar screenshots-chave e como subir o stack local.

Conteúdo sugerido:

1. **Resumo em 5 bullets**
   - O que o sistema faz (gestão de investimentos multi-corretora, BR/US).[file:1]
   - Tecnologias principais (Flask, PostgreSQL, Jinja/Tailwind, Podman).[file:1]
   - Módulos concluídos (M0–M7.5) e o que está em desenvolvimento (M8 analytics).[file:5]
   - Status atual: "M7 – Dashboards + Relatórios production‑ready".[file:5]
   - Link para docs completas em `docs/`.

2. **Arquitetura em alto nível**
   - Diagrama simples (mermaid ou imagem) com 3 blocos: Frontend (Flask/Jinja) ↔ Backend API ↔ PostgreSQL.[file:1]
   - Citar containers `exitus-frontend`, `exitus-backend`, `exitus-db` e rede `exitus-net`.[file:1]

3. **Getting Started rápido**
   - Bloco único de comandos: `git clone`, `.env.example → .env`, `./scripts/dev_up.sh` (ou equivalente), `http://localhost:8080`.[file:1]
   - Como gerar seeds rápidas (`seed_all`) e usuário admin padrão.[file:1]

4. **Mapa dos principais dashboards** (tabela)
   - Colunas: Dashboard, URL, Fonte de dados principal, Status (✅ Prod / 🔄 WIP).[file:1]

5. **Links para documentação detalhada**
   - `docs/ARCHITECTURE.md`
   - `docs/USER_GUIDE.md`
   - `docs/API_REFERENCE.md`
   - `docs/OPERATIONS_RUNBOOK.md`
   - `docs/CHANGELOG_MODOLOS.md`

`README_UPDATED.md` pode ser removido ou renomeado para um histórico (`docs/ARCHIVE/README_2025-12.md`) para evitar duplicidade.[file:5]

---

### 2. `docs/ARCHITECTURE.md` (Visão Técnica)

Função: Documento único que substitui vários textos longos de análise de módulos.[file:1][file:5]

Seções sugeridas:

1. **Contexto de domínio**
   - Descrever entidades centrais (Usuário, Corretora, Ativo, Transação, Posição, Provento, Movimentação, Portfolio, Alerta, Relatório).[file:1]
   - Pequeno diagrama entidade‑relacionamento simplificado (mermaid) focando chaves principais.

2. **Arquitetura lógica**
   - Backend: camadas `models` → `services` → `blueprints`, uso de Marshmallow e JWT.[file:1]
   - Frontend: `routes/dashboard.py` + templates por dashboard, HTMX/Alpine.[file:1][file:19]
   - Integração M7.5 cotações: provider externo + cache PostgreSQL.[file:1]

3. **Fluxos de dados principais**
   - Compra/Venda → Transações → Posições → Portfolio dashboard.[file:1]
   - Proventos → Relatórios de performance/renda.[file:1]
   - Alertas configurados → verificação (futuro Celery) → notificações.[file:17]
   - Cada fluxo pode usar mini‑diagramas de sequência (mermaid) ao invés de parágrafos grandes.

4. **Módulos e responsabilidades (M0–M8)**
   - Tabela com colunas: Módulo, Escopo, Principais arquivos, Status.[file:5][file:7]
   - Resumir listas já existentes em `ANALISE_COMPLETA_STATUS_M7.md` e checklists M4–M6 em parágrafos menores.[file:5][file:7][file:19]

5. **Decisões de design importantes**
   - Uso de `NUMERIC` no banco para valores em dinheiro.[file:1]
   - Estratégia de fallback mock data quando backend cai.[file:19]
   - Padronização de enums (snake_case vs UPPER) e lições aprendidas de bugs.[file:5][file:7]

---

### 3. `docs/USER_GUIDE.md` (Guia para Usuário Final)

Função: Manual curto para alguém que só quer usar o sistema.

Estrutura proposta:

1. **Tour pelos dashboards**
   - 1–2 parágrafos por tela: Buy Signals, Portfólios, Ativos, Transações, Proventos, Movimentações, Alertas, Relatórios.[file:19][file:17]
   - Pequenos wireframes/prints com legenda, referenciando os gráficos já descritos em M6.[file:19]

2. **Cenários de uso guiados**
   - "Criar um portfolio e registrar primeiras compras".[file:1]
   - "Cadastrar um alerta de alta de preço".[file:17]
   - "Gerar um relatório de performance anual".[file:7]

3. **Glossário mínimo**
   - Explicar conceitos como PM, rentabilidade bruta/liquida, Sharpe, drawdown – com fórmulas simplificadas.[file:7]

4. **FAQ curta**
   - Por que preciso clicar em "Recalcular Posições" em alguns fluxos.[file:1]
   - Como lidar com múltiplas corretoras.[file:1]

---

### 4. `docs/API_REFERENCE.md` (Visão de API para Devs)

Função: Centralizar referências hoje espalhadas em várias checklists e validações.[file:1][file:7]

Modelo sugerido:

1. **Overview**
   - Estrutura de autenticação JWT, formato de erro padrão, paginação.[file:7]

2. **Tabela de endpoints principais**
   - Colunas: Recurso, Método/Path, Descrição, Módulo, Status.
   - Ex.: `GET /api/relatorios/lista` – Lista relatórios com paginação – M7 – ✅.[file:7]

3. **Blocos por domínio**
   - Autenticação, Portfolios, Transações, Proventos, Movimentações, Alertas, Relatórios, Cotações.[file:1]
   - Para cada grupo, 1 exemplo cURL e estrutura JSON resumida (não colar respostas gigantes).[file:7]

4. **Ganchos para ferramentas**
   - Referenciar `scripts/generate_api_docs.sh` e saída em `docs/api/` para detalhes brutos gerados automaticamente.[file:7]

---

### 5. `docs/OPERATIONS_RUNBOOK.md` (Operação & Troubleshooting)

Função: Condensar o enorme `TROUBLESHOOTING_GUIDE` e notas de validação em um manual acionável para produção.[file:8]

Seções sugeridas:

1. **Subir/derrubar o ambiente**
   - Comandos essenciais Podman (start/stop, rebuild, seeds).[file:8]

2. **Playbooks de incidentes comuns**
   - API 500 por enum inválido.
   - `relation does not exist` após migrations.[file:8]
   - Token expirado / 401.[file:8]
   - Backend offline com frontend no ar.[file:8]

3. **Checklist de saúde**
   - Como usar `/health`, verificar logs, checar conexões DB.[file:7][file:8]

4. **Reset completo com segurança**
   - Passo a passo consolidado em 6–8 comandos.[file:8]

---

### 6. `docs/CHANGELOG_MODULOS.md` (Histórico por Módulo)

Função: Substituir documentos longos de auditoria (M4, M5, M6, M7.3, ANÁLISE_COMPLETA) como registro linear de evolução.[file:3][file:5][file:7][file:19]

Formato sugerido:

- Seções por versão/tag (`v0.7.5-m7-complete`, etc.).[file:5]
- Dentro de cada versão, subseções por módulo (M4, M5, M6, M7, M7.5) com bullets curtos:
  - "M7.3 Alertas – frontend 100% + backend CRUD integrado".[file:17]
  - "M7.4 Relatórios – endpoint /api/relatorios/lista, geração PERFORMANCE".[file:7]

Docs antigos (`ANALISE_COMPLETA_STATUS_M7.md`, `MODULO5_CHECKLIST.md`, `VALIDACAO_M4_COMPLETA.md`, `MODULO7.3_CHECKLIST_COMPLETO.md`) podem ser movidos para `docs/ARCHIVE/` como base histórica.[file:5][file:7][file:19][file:17]

---

## Estratégia de Implementação (sem redundância)

1. **Mapeamento e arquivamento**
   - Mover documentos longos e altamente redundantes para `docs/ARCHIVE/`.
   - Manter apenas um documento "fonte" por tipo de informação (arquitetura, guia usuário, API, operação, changelog).

2. **Extração de conteúdo útil**
   - Para cada doc de módulo, extrair:
     - Métricas relevantes (número de endpoints, rotas, gráficos, etc.).[file:5][file:19]
     - Decisões de design que ainda se aplicam.[file:1][file:7]
     - Comandos de teste e operação.
   - Incorporar esses pontos nas seções equivalentes dos novos arquivos.

3. **Adoção de mermaid e tabelas**
   - Usar 3–4 diagramas chave ao invés de dezenas de parágrafos narrativos:
     - Arquitetura geral.
     - Fluxo Transação → Posição → Portfolio.
     - Fluxo Alertas.
     - Fluxo Relatórios.[file:1][file:17]

4. **Automatização parcial**
   - Reaproveitar `generate_api_docs.sh` como fonte para seções "Lista completa de endpoints" dentro de `docs/api/`, e manter `API_REFERENCE.md` apenas como visão humana enxuta.[file:7]

---

## Próximos Passos com `execute_python`

Sugestão de arquivos a gerar na próxima rodada (via `execute_python`):

1. `docs/ARCHITECTURE.md` – usando sumário de `exitus_fontes.txt` + `ANALISE_COMPLETA_STATUS_M7.md`.
2. `docs/USER_GUIDE.md` – condensando partes descritivas de M5/M6/M7.3.
3. `docs/API_REFERENCE.md` – cruzando checklists de M4/M6 com o que o script de API produz.[file:7][file:19]
4. `docs/OPERATIONS_RUNBOOK.md` – fortemente baseado em `TROUBLESHOOTING_GUIDE.md`.[file:8]
5. `docs/CHANGELOG_MODULOS.md` – resumindo milestones dos docs de análise e checklists.[file:3][file:5][file:7][file:19]

Cada arquivo será **curto (3–5 páginas)**, com diagramas e tabelas, evitando narrativas repetidas e mantendo os documentos de módulo como referência histórica apenas.
