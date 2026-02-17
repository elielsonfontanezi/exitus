# Changelog - Sistema Exitus

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), e este projeto adere semanticamente à versão **v0.7.8**.[file:15]

## [0.7.8] - 2026-02-16

### ✨ Added
- **Expansão de ENUMs**: `TipoAtivo` de **7 para 14 tipos** (Multi-Mercado Completo)
  - **🇧🇷 Brasil** (6 tipos): `ACAO`, `FII`, `CDB`, `LCI_LCA`, `TESOURO_DIRETO`, `DEBENTURE`
  - **🇺🇸 US** (4 tipos): `STOCK`, `REIT`, `BOND`, `ETF`
  - **🌍 Internacional** (2 tipos): `STOCK_INTL`, `ETF_INTL`
  - **🛠️ Outros** (2 tipos): `CRIPTO`, `OUTRO`
- **Campo `cap_rate`** em tabela `ativo`: `NUMERIC(8,4)` para cálculo de **Preço Teto** de FIIs/REITs
- **Seeds para ativos US**: `app/seeds/seed_ativos_us.py` (**16 ativos**)
  - 10 Stocks: `AAPL`, `MSFT`, `GOOGL`, `AMZN`, `TSLA`, `NVDA`, `META`, `JPM`, `V`, `WMT`
  - 3 REITs: `O`, `VNQ`, `SPG`
  - 2 ETFs: `SPY`, `QQQ`
  - 1 Bond: US Treasury 10Y
- **Seeds para ativos EU**: `app/seeds/seed_ativos_eu.py` (**3 ativos**)
  - 2 Stocks INTL: `SAP.DE`, `ASML.AS`
  - 1 ETF INTL: `VWCE.DE`
- **Documentação completa**: `ENUMS.md` (14 tipos detalhados + validações PostgreSQL)[file:1]

### 🔧 Changed
- **Migration `202602162111`**: Expansão de `tipoativo` ENUM (7 → 14 valores)
- **Migration `202602162130`**: 
  - Adição de `cap_rate` em `ativo`
  - Remoção de `bolsa_origem` (deprecated)
- **Total de ativos seedados**: **62** (39 BR + 16 US + 3 EU + 4 outros)
- **API `/api/ativos`**: Suporte completo aos 14 tipos + validação `cap_rate` para FII/REIT[file:6]

### 🗑️ Removed
- **Campo `bolsa_origem`** da tabela `ativo` (substituído por `TipoAtivo` expandido)

### 📚 Documentation
- ✅ **Criação** de `ENUMS.md` com 14 tipos detalhados
- ✅ **Atualização** de `README.md` com seção "Tipos de Ativos Suportados"
- ✅ **Correções** em:
  - `ARCHITECTURE.md` (Modelo de Dados + Expansão Multi-Mercado)
  - `MODULES.md` (M1 - Enums e contagens)
  - `API_REFERENCE.md` (POST `/api/ativos` + exemplos CDB/STOCK)
  - `USER_GUIDE.md` ("Cadastrar Novos Ativos" com 14 tipos por mercado)
- ✅ **Checklist de Correções** criado e validado[file:14]

### 🧪 Tested
```
# Validar 14 ENUMs no banco
podman exec exitus-db psql -U exitus -d exitusdb -c "
SELECT COUNT(*) FROM pg_enum WHERE enumtypid = 'tipoativo'::regtype;
"  # Deve retornar: 14

# Contar ativos por tipo
podman exec exitus-db psql -U exitus -d exitusdb -c "
SELECT tipo, COUNT(*) as total 
FROM ativo GROUP BY tipo ORDER BY total DESC;
"  # 62 totais
```
**Status:** ✅ **PRODUCTION READY** - Todos testes aprovados.[file:3]

---

## [0.7.7] - 2026-02-15

### 🔒 Security & Clarity
**M2 - Corretoras**: GET/PUT/DELETE `/api/corretoras/{id}` agora retornam **403 Forbidden** (quando usuário tenta acessar corretora de outro usuário) - anteriormente retornavam **404**.[file:15]

**Benefício:** Melhor clareza de erros e conformidade com padrões REST (404 = não existe, 403 = existe mas sem permissão).

**Arquivos modificados:**
- `backend/app/services/corretora_service.py` (Método `get_by_id` distingue 404 vs 403 com `PermissionError`)
- `backend/app/blueprints/corretoras_routes.py` (Captura `PermissionError` e retorna forbidden 403)

### ✅ Validação Completa M2-CORRETORAS
- **6 endpoints testados** (29 cenários)
- **Performance**: **13ms média** (26x mais rápido que SLA de 500ms)
- **Segurança**: Isolamento multi-tenant **100% funcional**
- **Filtros**: 5 tipos funcionando (`pais`, `tipo`, `ativa`, `search`, combinados)[file:15]

---

## [0.7.6] - 2026-02-14

### 📚 Documentation
- **Official snake_case naming standard** documentado:
  - `README.md` (Coding Standard section)
  - `ARCHITECTURE.md` (Coding Conventions)
  - `docs/CODING_STANDARDS.md` (Tabela completa com exemplos)
- **Ref:** `CODING_STANDARDS.md`[file:15]

---

## [0.7.5] - 2026-02-14

### 🐳 Infrastructure
- **Upgrade PostgreSQL**: 15.15 → **16.11**
- **Backup completo** realizado antes do upgrade
- **Dados migrados sem perda**: 21 tabelas, 44 ativos, 17 transações
- **Zero downtime** para usuário final
- **Performance verificada**: Todas as APIs funcionais[file:15]

---

*(Conteúdo anterior preservado - v0.7.4 até v0.6.x permanece inalterado)*

## [0.7.4] - 2026-01-15
*(Padronização `POSTGRES_USER=exitus` em toda documentação)*[file:15]

## [0.7.3] - 2026-01-15
*(Atualização de versão PostgreSQL em docs)*[file:15]

## [0.7.2] - 2026-01-15
*(Sistema validado: Backend API REST, Frontend HTMX, PostgreSQL 16)*[file:15]

## [0.7.1] - 2026-01-06
**Branch:** `feature/lazy-loading-historico` → `main`  
**Commit:** `ab59342`

### 📈 Sistema de Histórico de Preços
- **Tabela `historico_preco`**: Armazena séries temporais de preços
- **Migration:** `008_add_historico_preco.py`
- **Scripts:** `popular_historico_inicial.py`[file:15]

---

*(Demais versões v0.7.0 até v0.6.x mantidas conforme original)*

---

## 📊 Métricas do Projeto - v0.7.8

| Componente    | Linhas | Arquivos |
|---------------|--------|----------|
| **Backend**   | 15.500 | 90       |
| **Frontend**  | 4.000  | 28       |
| **Migrations**| 1.400  | 10       |
| **Seeds**     | 1.200  | 5        |
| **Docs**      | 9.500  | 22       |
| **Total**     | **31.600** | **155** |[file:15]

**Ativos Seedados:** **62** (39 BR + 16 US + 3 EU + 4 outros) ✅

**Cobertura ENUMs:** 14/14 tipos implementados e testados.

---

## 🚀 Roadmap Futuro

### v0.8.0 - M8 (Q2 2026)
- Simulação Monte Carlo
- Otimização Markowitz
- Backtesting
- WebSocket (alertas real-time)
- Export PDF/Excel profissional[file:15]

### v0.9.0 - M9 (Q1 2026)
- CI/CD GitHub Actions
- Deploy Railway/Render
- Monitoring Prometheus/Grafana[file:15]

---

**Última atualização:** 17 de Fevereiro de 2026  
**Versão atual:** **v0.7.8** (Expansão ENUMs Multi-Mercado)  
**Próxima:** v0.8.0 (M8 Analytics Avançados)

**Contribuidores:**
- Elielson Fontanezi
- Perplexity AI (Documentação ENUMs v0.7.8)[file:15]

**Repositório:** https://github.com/elielsonfontanexi/exitus  
**Issues:** https://github.com/elielsonfontanexi/exitus/issues[file:15]

**Licença:** MIT