# 🚀 Plano de Integração Frontend-Backend — Exitus

**Data:** 09/06/2026 | **Versão:** v1.7 | **Status:** ✅ Sprints 1–7 Concluídos | 🎯 Sprint 8 Próximo  
**Modelo IA:** GPT 5.1 Codex Medium ($) para CRUD | Claude Sonnet 4.6 Thinking ($$$) para lógica complexa  
**Plano detalhado:** `docs/FRONTEND_IMPLEMENTATION_PLAN.md` ⭐

---

## 📋 Visão Geral

### Objetivo
Integrar **156 APIs do backend** com frontend de forma estruturada.

### Contexto
- ✅ Backend: 48 GAPs, 156 endpoints, 93.0% testes
- ✅ Dashboard: Implementado (R$ 257.677,50)
- ✅ Frontend API-Driven: 9 APIs integradas, Sprints 1–4 completos
- ✅ Sprint 1: Operações Essenciais 100% funcional (05/04/2026)
- ✅ Sprint 2: Proventos e Rendimentos (09/06/2026)
- ✅ Sprint 3: Catálogo de Ativos (09/06/2026)
- ✅ Sprint 4: Planos Disciplinados e Alertas (09/06/2026)
- ✅ Sprint 5: Imposto de Renda e DARF (09/06/2026)
- ✅ Sprint 6: Rentabilidade e Análises (09/06/2026)
- ✅ Sprint 7: Relatórios e Exportação (09/06/2026)
- 🎯 Sprint 8: Ferramentas (opcional, Set/2026)
- ⚠️ Menu horizontal: ~50 links, ~8 ainda retornam 404

---

## 🎯 Estratégia

### Princípios
1. **API-Driven:** Cada tela consome APIs existentes
2. **User-Centric:** Priorizar por valor ao usuário
3. **Progressive:** Implementação incremental

### Arquitetura de Navegação

**Menu Principal (completo):**
```
📊 Dashboard | 💼 Operações | 📈 Análises | 💰 Rendimentos
📋 Fiscal | ⚙️ Config | 👤 Perfil
```

**Quick Actions (dashboard apenas):**
```
➕ Nova Compra | 📊 Ver Análises | 📅 Calendário
```

---

## 🗺️ Mapeamento APIs → Telas

| Categoria | APIs | Telas | Prioridade |
|-----------|------|-------|------------|
| Operações | 25 | Compra, Venda, Import | ✅ P0 Concluído |
| Análises | 30 | Dashboard, Gráficos | 🚀 P0 |
| Rendimentos | 15 | Proventos, Calendário | 🔥 P1 |
| Fiscal | 20 | IR, DARF, Relatórios | 🔥 P1 |
| Portfolio | 20 | Posições, Carteiras | 🔥 P1 |
| Ativos | 15 | Catálogo, Detalhes | 📊 P2 |
| Config | 10 | Alertas, Preferências | 📉 P3 |

### ✅ APIs Integradas (18/156)

**Sprint 1 — Operações (5 APIs):**
- ✅ POST `/api/transacoes` - Criar transação
- ✅ GET `/api/ativos?search=` - Buscar ativos
- ✅ GET `/api/cotacoes/<ticker>` - Cotações em tempo real
- ✅ GET `/api/posicoes` - Posições do usuário
- ✅ POST `/api/import/b3` - Importação B3

**Sprint 2 — Proventos (1 API):**
- ✅ GET `/api/proventos` - Lista, projetação e calendário

**Sprint 3 — Catálogo Ativos (1 API):**
- ✅ GET `/api/ativos?tipo=X` - Filtro por categoria

**Sprint 4 — Planos e Alertas (2 APIs):**
- ✅ GET `/api/plano-compra/` - Planos de acumulação
- ✅ GET `/api/alertas/` - Alertas de preço e dividendos

**Sprint 5 — IR e DARF (4 APIs):**
- ✅ GET `/api/ir/apuracao` - Apuração mensal por categoria
- ✅ GET `/api/ir/darf` - DARFs geradas no mês
- ✅ GET `/api/ir/historico` - Histórico anual 12 meses
- ✅ GET `/api/ir/dirpf` - Bens e direitos DIRPF

**Sprint 6 — Rentabilidade e Análises (5 APIs):**
- ✅ GET `/api/portfolios/rentabilidade` - TWR 81.14%, MWR -65.4%, benchmark CDI
- ✅ GET `/api/portfolios/alocacao` - RF 61.6% / RV 38.4% / Cripto
- ✅ GET `/api/portfolios/evolucao` - Série histórica 30 meses (R$119k → R$795k)
- ✅ GET `/api/performance/performance` - Sharpe 1.45, Drawdown -8.3%, top ativos
- ✅ GET `/api/buy-signals/buy-score/<ticker>` - Buy Score por ticker

---

## 📅 Roadmap (8 semanas)

### ✅ Sprint 1: Operações (CONCLUÍDO 05/04/2026)
- ✅ Compra/Venda unificada com toggle
- ✅ Importação B3 com detecção automática
- Resultado: 5 APIs integradas

### ✅ Sprint 2: Proventos e Rendimentos (CONCLUÍDO 09/06/2026)
- ✅ Recebidos, Projetados, Calendário
- Resultado: 1 API integrada, 100 proventos reais

### ✅ Sprint 3: Catálogo de Ativos (CONCLUÍDO 09/06/2026)
- ✅ Ações, FIIs, ETFs, RF, Cripto, Detalhe
- Resultado: 1 API integrada, 73 ativos reais

### ✅ Sprint 4: Planos e Alertas (CONCLUÍDO 09/06/2026)
- ✅ Planos Compra (lista/detalhe), Alertas, stub Planos Venda
- Resultado: 2 APIs integradas, 12 planos + 15 alertas reais

### ✅ Sprint 5: Imposto de Renda e DARF (CONCLUÍDO 09/06/2026)
- ✅ Apuração Mensal, DARFs, Histórico Anual, Declaração DIRPF
- Resultado: 4 APIs integradas, custo total carteira R$ 642k real

### ✅ Sprint 6: Rentabilidade e Análises (CONCLUÍDO 09/06/2026)
- ✅ Rentabilidade TWR/MWR, Alocação, Evolução Patrimonial, Performance (Sharpe), Buy Signals
- Resultado: 5 APIs integradas, patrimônio R$795k real

### 🎯 Sprint 7: Relatórios e Exportação (PRÓXIMO)
- Mensais, Anuais, Excel/PDF/CSV
- APIs: GET /api/relatorios/*, /api/export/*

### Sprint 8: Ferramentas (Opcional)
- Comparador, Calculadora IR, Simulador, Screeners

---

## 🔐 Gerenciamento de Sessão JWT

**Implementado em:** 29/03/2026 | EXITUS-JWT-001

### Configuração
| Parâmetro | Valor |
|-----------|-------|
| Access Token | 30 minutos |
| Refresh Token | 7 dias |
| Inatividade | 15 minutos → modal de relogin |
| Verificação | A cada 1 minuto via `/auth/check-session` |

### Padrão Europeu — Datas e Valores
O sistema Exitus segue o **padrão Europeu** para formatação:
- **Datas:** DD/MM/AAAA (ex: 29/03/2026)
- **Valores monetários:** R$ 9.999,99 (ponto milhar, vírgula decimal)
- **Percentuais:** 99,99%

Ver detalhes completos em `docs/CODING_STANDARDS.md` — seção "Padrão Europeu".

### Padrão obrigatório para todas as telas
```python
from .auth import login_required, get_api_headers

@bp.route('/minha-tela')
@login_required
def minha_tela():
    headers = get_api_headers()   # ✅ ÚNICO padrão autorizado
    if not headers:
        return redirect(url_for('auth.login'))
```

### Dívida técnica — `dashboard.py`
As rotas em `dashboard.py` ainda usam `session.get('access_token')` diretamente. Serão migradas para `get_api_headers()` de forma gradual a cada nova tela implementada, para evitar regressões.

---

## � Padrão de Tipos de Ativo (Multi-Mercado)

**Implementado em:** 29/03/2026 | EXITUS-COMP-002

O sistema suporta **15 tipos de ativos** em **4 mercados** (BR, US, INTL, Cripto). Todas as telas de operação devem usar o seletor de tipo com comportamento dinâmico.

### Configuração Padrão (8 Categorias)

| Categoria | Tipos Incluídos | Quantidade | Moeda |
|-----------|-----------------|------------|-------|
| **Ação BR** | ACAO, UNIT | Inteiro (step=1) | R$ |
| **FII** | FII | Inteiro (step=1) | R$ |
| **Renda Fixa** | CDB, LCI_LCA, TESOURO, DEBENTURE | Inteiro (step=1) | R$ |
| **Stock EUA** | STOCK | Fração 6 decimais | $ |
| **REIT** | REIT | Fração 6 decimais | $ |
| **ETF** | ETF, ETF_INTL | Fração 6 decimais | $ |
| **Intl** | STOCK_INTL, BOND | Fração 6 decimais | $ |
| **Cripto** | CRIPTO | Fração 8 decimais | $ |

### Implementação

Ver `docs/LESSONS_LEARNED.md` — L-FE-003 para código completo do `tiposAtivo` array e funções auxiliares.

### APIs Envolvidas

- `GET /api/ativos?search=TICKER&tipo=STOCK` — Busca com filtro por tipo
- `GET /api/cotacoes/<ticker>` — Cotação atual (TTL 15min)

---

## 🔄 Toggle Compra/Venda — Padrão Unificado

**Implementado em:** 29/03/2026 | Sprint 1

A tela de operações foi unificada com um toggle para alternar entre Compra e Venda, eliminando a necessidade de duas telas separadas.

### Componentes Chave

| Elemento | Comportamento | APIs |
|----------|---------------|-------|
| **Toggle** | Botões verde/vermelho com ícones e animação | Nenhuma |
| **Header** | Título/subtítulo dinâmicos (➕/💰) | Nenhuma |
| **Ativo (Compra)** | Busca livre com filtro por tipo | `GET /api/ativos?search=TICKER&tipo=...` |
| **Ativo (Venda)** | Lista apenas posições do usuário | `GET /api/posicoes` |
| **Quantidade (Venda)** | Badge "Máx: X" + validação `max` | Nenhuma (frontend) |
| **Resumo** | 4 colunas com cores dinâmicas | Nenhuma (frontend) |
| **Botão** | "Confirmar Compra" (verde) ↔ "Confirmar Venda" (vermelho) | `POST /api/transacoes` |

### Padrões de UX

- Ao trocar modo: limpa ativo e tipo selecionados
- Em Venda: busca posições apenas ao selecionar tipo
- Mensagem "Nenhuma posição encontrada" quando sem ativos
- Preço médio sugerido ao selecionar posição

### JavaScript — `operacaoForm()`

```javascript
// Estado
modoOperacao: 'compra',  // 'compra' | 'venda'
posicoes: [],           // Array de posições do usuário
quantidadeMaxima: 0,     // Máximo vendível para ativo selecionado

// Computed
get isCompra() { return this.modoOperacao === 'compra'; }
get isVenda() { return this.modoOperacao === 'venda'; }
get posicoesPorTipo() { /* filtra por selectedTipo */ }

// Métodos
toggleModo(modo)          // Alterna entre compra/venda
fetchPosicoes()           // Busca posições via API
selectPosicao(posicao)   // Seleciona ativo da posição
usarQuantidadeMaxima()    // Preenche quantidade máxima
submitOperacao()          // Envia transação (compra ou venda)
```

### APIs Envolvidas

- `GET /api/posicoes` — Lista posições do usuário (modo Venda)
- `POST /api/transacoes` — Registra compra ou venda (ambos modos)

---

## 🛠️ Metodologia

### Fluxo por Tela
1. Mapear APIs necessárias
2. Validar contratos (Swagger)
3. Criar componentes UI
4. Integrar com APIs
5. Testes E2E
6. Deploy incremental

### Documentação Viva
- `API_FRONTEND_MAPPING.md` - Mapeamento completo
- Atualizar a cada sprint
- Rastrear progresso

---

## 📊 Métricas de Sucesso

- **Cobertura:** % de APIs integradas
- **Fluxos:** Número de jornadas completas
- **Testes:** E2E passing por funcionalidade
- **UX:** Tempo para completar tarefas

---

## � Dashboard Evolution Strategy

### Decisão: EVOLUIR, não substituir

O dashboard atual (`/dashboard`) está **100% funcional** com dados reais (R$ 257.677,50).

**Estratégia:**
- ✅ **Manter** 6 cards principais e quick actions
- ➕ **Adicionar** widgets incrementalmente (Sprints 3-8)
- �🔄 **Evoluir** para multi-moeda quando backend suportar

**Roadmap de Widgets:**
- Sprint 3-4: Gráficos (Evolução, Alocação, Top 5)
- Sprint 5: Proventos (Calendário, Próximos)
- Sprint 6: Fiscal (IR, DARF)
- Sprint 7-8: Multi-moeda (se backend pronto)

**Detalhes:** Consultar `DASHBOARD_EVOLUTION.md`

---

## 🔄 Próximos Passos

1. ✅ Arquivar docs UX obsoletos
2. ✅ Criar API_FRONTEND_MAPPING.md detalhado
3. ✅ Documentar estratégia de dashboard
4. ✅ Sprint 1: Tela Compra refatorada (Tailwind/API REST) - 28/03/2026
5. ✅ Implementar tela de venda com estilo consistente - 02/04/2026
6. ✅ Implementar Importação B3 (upload drag & drop) - 05/04/2026
7. ⏳ Sprint 2: Proventos Recebidos (`/proventos/recebidos`)
8. ⏳ Sprint 2: Proventos Projetados (`/proventos/projetados`)
9. ⏳ Sprint 2: Calendário de Dividendos (`/proventos/calendario`)
10. ⏳ Sprint 3: Catálogo de Ativos (Ações, FIIs, ETFs, Renda Fixa, Cripto)
11. ⏳ Sprint 4: Planos de Compra e Venda Disciplinados
12. ⏳ Sprint 5: Imposto de Renda / DARFs
13. ⏳ Sprint 6: Rentabilidade e Análises
14. ⏳ Sprint 7: Relatórios e Exportação

**Ver plano completo:** `docs/FRONTEND_IMPLEMENTATION_PLAN.md`

---

## 📚 Documentação de Referência

- **`FRONTEND_IMPLEMENTATION_PLAN.md`** ⭐ — Plano de sprints detalhado (NOVO 09/06/2026)
- **`FRONTEND_INTEGRATION_PLAN.md`** (este documento) — Estratégia e padrões de integração
- **`API_FRONTEND_MAPPING.md`** — Mapeamento API ↔ Tela
- **`API_REFERENCE.md`** — Contratos das APIs
- **`UX_DESIGN_SYSTEM.md`** — Componentes visuais
