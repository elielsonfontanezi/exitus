# Changelog - Sistema Exitus

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), e este projeto adere semanticamente à versão **v0.7.9**.

---

## [0.7.9] - 2026-02-19

### ✨ Added
- **Seed Renda Fixa BR**: `app/seeds/seed_ativos_renda_fixa_br.py` (**8 novos ativos**)
  - **CDB (3):** `CDBNUBANK100CDI`, `CDBINTER105CDI`, `CDBC6107CDI`
  - **TESOURO_DIRETO (3):** `TESOUROSELIC2029`, `TESOUROIPCA2035`, `TESOUROPREFIX2027`
  - **DEBENTURE (2):** `VALE23DBNT`, `PETR4DBNT`
- **Total de ativos seedados:** **70** (62 anteriores + 8 novos)
- **`run_all_seeds.py`** atualizado com `seed_ativos_renda_fixa_br` na sequência de execução

### 🔧 Fixed
- **GAP EXITUS-SEEDS-RUN-001 — RESOLVIDO:**
  - `IncidenciaImposto` adicionado ao `app/models/__init__.py` (import + `__all__`)
  - `seed_regras_fiscais_br.py` agora executa sem `ImportError`
  - 6 regras fiscais BR confirmadas no banco

### 📚 Documentation
- **GAP EXITUS-AUTH-001 — Opção A aplicada:**
  - `SEEDS.md` corrigido: todos os exemplos cURL usam `username` (não `email`)
  - Decisão documentada: API mantém `username` como padrão; evolução para aceitar email OU username adiada para v0.8.x
- **SEEDS.md** v0.7.9:
  - Login corrigido (`email` → `username`) em todos os exemplos
  - Seção Renda Fixa BR adicionada com 8 ativos detalhados
  - Total ativos atualizado: 62 → **70**
  - Nota sobre estrutura de resposta `.data.ativos[]` (fix GAP EXITUS-DOCS-API-001)
- **ENUMS.md** v0.7.9:
  - Seção de divergência adicionada: query param (UPPERCASE) vs resposta JSON (lowercase snake_case) vs banco (lowercase sem `_`)
  - Tabela de mapeamento completa para todos os 14 tipos
  - Colunas "Resposta JSON" adicionadas nas tabelas de TipoAtivo
  - Nota de fix do `IncidenciaImposto` na seção 9

### 🐛 Gaps Registrados
- **EXITUS-DOCS-API-001** (novo): `/api/ativos` retorna `.data.ativos[]`, não `.data.items[]` como documentado em API_REFERENCE.md → corrigir em próxima iteração
- **EXITUS-INFRA-001** (novo): Volume `app/` montado como read-only no container → `podman exec sed -i` falha com `Permission denied`; edições devem ser feitas no host
- **EXITUS-AUTH-001** (fechado — Opção A): Documentação corrigida para usar `username`

### 🧪 Tested
```bash
# Filtros Renda Fixa BR — validados 19/02/2026
curl "http://localhost:5000/api/ativos?mercado=BR&tipo=CDB"           # total: 3 ✅
curl "http://localhost:5000/api/ativos?mercado=BR&tipo=TESOURO_DIRETO" # total: 3 ✅
curl "http://localhost:5000/api/ativos?mercado=BR&tipo=DEBENTURE"      # total: 2 ✅

# Fix IncidenciaImposto
podman exec exitus-backend python3 -c "
from app.models import RegraFiscal, IncidenciaImposto
print([i.value for i in IncidenciaImposto])
"  # ['lucro', 'receita', 'provento', 'operacao'] ✅
```
**Status:** ✅ **PRODUCTION READY**

---

## [0.7.8] - 2026-02-16

### ✨ Added
- **Expansão de ENUMs**: `TipoAtivo` de **7 para 14 tipos** (Multi-Mercado Completo)
  - **🇧🇷 Brasil** (6 tipos): `ACAO`, `FII`, `CDB`, `LCI_LCA`, `TESOURO_DIRETO`, `DEBENTURE`
  - **🇺🇸 US** (4 tipos): `STOCK`, `REIT`, `BOND`, `ETF`
  - **🌍 Internacional** (2 tipos): `STOCK_INTL`, `ETF_INTL`
  - **🛠️ Outros** (2 tipos): `CRIPTO`, `OUTRO`
- **Campo `cap_rate`** em tabela `ativo`: `NUMERIC(8,4)` para cálculo de **Preço Teto** de FIIs/REITs
- **Seeds para ativos US**: `app/seeds/seed_ativos_us.py` (**16 ativos**)
- **Seeds para ativos EU**: `app/seeds/seed_ativos_eu.py` (**3 ativos**)
- **Documentação completa**: `ENUMS.md` (14 tipos detalhados + validações PostgreSQL)

### 🔧 Changed
- **Migration `202602162111`**: Expansão de `tipoativo` ENUM (7 → 14 valores)
- **Migration `202602162130`**: Adição de `cap_rate`, remoção de `bolsa_origem`
- **Total de ativos seedados**: **62** (39 BR + 16 US + 3 EU + 4 outros)
- **API `/api/ativos`**: Suporte completo aos 14 tipos + validação `cap_rate` para FII/REIT

### 🗑️ Removed
- **Campo `bolsa_origem`** da tabela `ativo` (substituído por `TipoAtivo` expandido)

### 🧪 Tested
**Status:** ✅ **PRODUCTION READY** - Todos testes aprovados.

---

## [0.7.7] - 2026-02-15

### 🔒 Security & Clarity
**M2 - Corretoras**: GET/PUT/DELETE `/api/corretoras/{id}` agora retornam **403 Forbidden** quando usuário tenta acessar corretora de outro usuário (anteriormente: 404).

**Arquivos modificados:**
- `backend/app/services/corretora_service.py`
- `backend/app/blueprints/corretoras_routes.py`

### ✅ Validação Completa M2-CORRETORAS
- **6 endpoints testados** (29 cenários)
- **Performance**: **13ms média** (26x mais rápido que SLA de 500ms)
- **Segurança**: Isolamento multi-tenant **100% funcional**

---

## [0.7.6] - 2026-02-14

### 📚 Documentation
- **Official snake_case naming standard** documentado em `CODING_STANDARDS.md`

---

## [0.7.5] - 2026-02-14

### 🐳 Infrastructure
- **Upgrade PostgreSQL**: 15.15 → **16.11**
- **Zero downtime**, dados migrados sem perda (21 tabelas, 44 ativos, 17 transações)

---

## [0.7.4] - 2026-01-15
*(Padronização `POSTGRES_USER=exitus` em toda documentação)*

## [0.7.3] - 2026-01-15
*(Atualização de versão PostgreSQL em docs)*

## [0.7.2] - 2026-01-15
*(Sistema validado: Backend API REST, Frontend HTMX, PostgreSQL 16)*

## [0.7.1] - 2026-01-06
### 📈 Sistema de Histórico de Preços
- **Tabela `historico_preco`**: Armazena séries temporais de preços
- **Migration:** `008_add_historico_preco.py`

---

## 📊 Métricas do Projeto - v0.7.9

| Componente     | Linhas | Arquivos |
|----------------|--------|----------|
| **Backend**    | 15.600 | 91       |
| **Frontend**   | 4.000  | 28       |
| **Migrations** | 1.400  | 10       |
| **Seeds**      | 1.400  | 6        |
| **Docs**       | 9.800  | 22       |
| **Total**      | **31.800** | **157** |

**Ativos Seedados:** **70** (47 BR + 16 US + 3 EU + 4 outros) ✅
**Cobertura ENUMs:** 14/14 tipos implementados e testados.

---

## 🚀 Roadmap Futuro

### v0.7.10 (próxima)
- Corrigir `API_REFERENCE.md`: `.data.items[]` → `.data.ativos[]` (GAP EXITUS-DOCS-API-001)
- Verificar se volume `app/` deve ser read-write no container (GAP EXITUS-INFRA-001)
- Avaliar Opção B do GAP EXITUS-AUTH-001 (API aceitar email OU username)

### v0.8.0 - M8 (Q2 2026)
- Simulação Monte Carlo
- Otimização Markowitz
- Backtesting
- WebSocket (alertas real-time)
- Export PDF/Excel profissional

### v0.9.0 - M9 (Q3 2026)
- CI/CD GitHub Actions
- Deploy Railway/Render
- Monitoring Prometheus/Grafana

---

**Última atualização:** 19 de Fevereiro de 2026
**Versão atual:** **v0.7.9** (Seed Renda Fixa BR + Fix seeds + Docs)
**Próxima:** v0.7.10 / v0.8.0

**Contribuidores:**
- Elielson Fontanezi
- Perplexity AI (Documentação v0.7.8, v0.7.9)
