# 🚀 Plano de Integração Frontend-Backend — Exitus

**Data:** 26/03/2026 | **Versão:** v1.0 | **Status:** 📋 Planejamento  
**Modelo IA:** Claude Sonnet (análise estratégica)

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

## 🔄 Próximos Passos

1. ✅ Arquivar docs UX obsoletos
2. ⏳ Criar API_FRONTEND_MAPPING.md detalhado
3. ⏳ Fechar branch atual
4. ⏳ Criar branch feature/frontend-api-integration
5. ⏳ Iniciar Sprint 1

---

**Consultar:** `API_FRONTEND_MAPPING.md` para detalhes de cada endpoint
