# 🚀 Plano de Integração Frontend-Backend — Exitus

**Data:** 26/03/2026 | **Versão:** v1.1 | **Status:** � Em andamento  
**Modelo IA:** Claude Sonnet 4.6 Thinking

---

## 📋 Visão Geral

### Objetivo
Integrar **156 APIs do backend** com frontend de forma estruturada.

### Contexto
- ✅ Backend: 48 GAPs, 156 endpoints, 87.7% testes
- ✅ Dashboard: Implementado (R$ 257.677,50)
- ⚠️ Gap: APIs sem telas correspondentes
- ⚠️ Problema: Navegação duplicada

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
| Operações | 25 | Compra, Venda, Import | 🚀 P0 |
| Análises | 30 | Dashboard, Gráficos | 🚀 P0 |
| Rendimentos | 15 | Proventos, Calendário | 🔥 P1 |
| Fiscal | 20 | IR, DARF, Relatórios | 🔥 P1 |
| Portfolio | 20 | Posições, Carteiras | 🔥 P1 |
| Ativos | 15 | Catálogo, Detalhes | 📊 P2 |
| Config | 10 | Alertas, Preferências | 📉 P3 |

---

## 📅 Roadmap (8 semanas)

### Sprint 1-2: Operações (P0)
- Compra/Venda/Importação
- APIs: POST /api/transacoes, /api/import/b3
- Critério: Usuário registra investimentos

### Sprint 3-4: Análises (P0)
- Gráficos, Evolução, Setores
- APIs: GET /api/analises/*, /api/portfolios/evolucao
- Critério: Usuário vê insights

### Sprint 5-6: Rendimentos + Fiscal (P1)
- Proventos, IR, DARF
- APIs: GET /api/proventos/*, /api/ir/*
- Critério: Usuário gerencia proventos e IR

### Sprint 7: Portfolio (P1)
- Carteiras, Posições
- APIs: CRUD /api/portfolios, /api/posicoes
- Critério: Usuário organiza carteiras

### Sprint 8: Config (P3)
- Alertas, Preferências
- APIs: CRUD /api/alertas, /api/usuarios/*
- Critério: Usuário personaliza sistema

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
5. ⏳ Implementar tela de venda com estilo consistente (Próximo)
6. ⏳ Implementar Importação B3 (upload drag & drop)

---

## 📚 Documentação de Referência

- **`FRONTEND_INTEGRATION_PLAN.md`** (este documento) — Estratégia geral
- **`API_FRONTEND_MAPPING.md`** — Mapeamento API ↔ Tela
- **`DASHBOARD_EVOLUTION.md`** — Evolução do dashboard
- **`FRONTEND_WIREFRAMES.md`** — Wireframes completos
- **`API_REFERENCE.md`** — Contratos das APIs
- **`UX_DESIGN_SYSTEM.md`** — Componentes visuais
