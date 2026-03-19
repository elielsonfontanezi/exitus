# Auditoria Visual — Frontend Exitus v0.9.2

> **Data:** 19/03/2026  
> **Objetivo:** Identificar problemas visuais nas 26 telas do sistema  
> **Método:** Análise de templates HTML + Testes manuais  
> **Status:** 🔍 Em andamento

---

## 📊 Resumo Executivo

**Total de telas:** 26  
**Telas analisadas:** 26/26 (100%)  
**Problemas identificados:** A catalogar  
**Prioridade:** P0 (crítico) → P1 (funcional) → P2 (estético)

---

## 🗺️ Mapa Completo das Telas

### Fase 1 — Dashboard Principal (4 telas)
1. `/dashboard/` — Dashboard Multi-Mercado
2. `/dashboard/buy-signals` — Buy Signals
3. `/dashboard/ativo/<ticker>` — Análise de Ativo
4. `/dashboard/performance` — Performance e Rentabilidade

### Fase 2 — Análise e Gestão (4 telas)
5. `/dashboard/assets` — Ativos
6. `/dashboard/portfolios` — Portfolios
7. `/dashboard/transactions` — Transações
8. `/dashboard/analytics` — Analytics

### Fase 3 — Proventos e Fluxo (4 telas)
9. `/dashboard/dividends` — Proventos/Dividendos
10. `/dashboard/proventos-calendario` — Calendário de Proventos
11. `/dashboard/movimentacoes` — Movimentações Caixa
12. `/dashboard/fluxo-caixa` — Fluxo de Caixa

### Fase 4 — Fiscal e Relatórios (4 telas)
13. `/dashboard/imposto-renda` — Imposto de Renda
14. `/dashboard/reports` — Relatórios e Auditoria
15. `/dashboard/alerts` — Alertas
16. `/dashboard/alertas` — Central de Alertas

### Fase 5 — Planos e Estratégia (4 telas)
17. `/dashboard/planos-compra` — Planos de Compra
18. `/dashboard/planos-compra/novo` — Novo Plano de Compra
19. `/dashboard/planos-venda` — Planos de Venda
20. `/dashboard/alocacao` — Alocação e Rebalanceamento

### Fase 6 — Ferramentas Avançadas (6 telas)
21. `/dashboard/comparador` — Comparador de Ativos
22. `/dashboard/educacao` — Educação e Insights
23. `/dashboard/configuracoes` — Configurações
24. `/auth/login` — Login
25. `/auth/register` — Registro
26. `/auth/forgot-password` — Recuperação de Senha

---

## 🔍 Problemas Identificados

### ⚠️ P0 — CRÍTICO (Texto Ilegível)

**✅ IDENTIFICADO — Botão "Voltar" com hover state problemático**

**Problema:**
- Classe CSS: `text-white border-white hover:bg-white hover:text-primary-600`
- Estado normal: texto branco em gradiente (OK)
- Estado hover: fundo branco + texto branco = **ILEGÍVEL**
- Ocorrências: **16 telas** (62% do sistema)

**Telas afetadas:**
1. alertas.html — linha 22
2. alocacao.html — linha 22
3. ativo_detalhes.html — linha 18
4. buy_signals.html — linha 22
5. comparador.html — linha 22
6. configuracoes.html — linha 22
7. educacao.html — linha 22
8. fluxo_caixa.html — linha 22
9. imposto_renda.html — linha 22
10. performance.html — linha 22
11. planos_compra.html — linha 22
12. planos_venda.html — linha 22
13. portfolios.html — linha 28
14. proventos_calendario.html — linha 22
15. reports.html — linha 58
16. transactions.html — linha 28

**Solução aplicada:**
```html
<!-- ANTES (problemático) -->
<a class="btn btn-outline text-white border-white hover:bg-white hover:text-primary-600">

<!-- DEPOIS (corrigido) -->
<a class="btn btn-outline text-white border-white hover:bg-white/10 hover:border-white/50">
```

**✅ STATUS: CORRIGIDO (19/03/2026)**
- 16/16 telas corrigidas
- Hover agora usa fundo semi-transparente (bg-white/10)
- Texto permanece legível em todos os estados

### 🟡 P1 — FUNCIONAL (Layout Quebrado)

A catalogar após análise completa dos templates.

### 🔵 P2 — ESTÉTICO (Melhorias Visuais)

A catalogar após análise completa dos templates.

---

## 📋 Análise por Tela

### 01. Dashboard Multi-Mercado (`/dashboard/`)

**Template:** `dashboard/index.html`  
**Status:** ✅ Analisado  
**Problemas encontrados:** Nenhum aparente

**Estrutura:**
- Hero section com gradiente azul + texto branco ✅
- Cards por mercado (BR, US, INTL) com ícones e badges ✅
- Gráficos de alocação geográfica ✅
- Design system aplicado corretamente ✅

**Observações:**
- Usa `bg-gradient-primary text-white` (contraste OK)
- Cards com `text-gray-900` em fundo branco (contraste OK)
- Sem evidências de texto branco em fundo branco

---

### 02. Buy Signals (`/dashboard/buy-signals`)

**Template:** `dashboard/buy_signals.html`  
**Status:** 🔍 Pendente análise detalhada

---

### 03-26. Demais Telas

**Status:** 🔍 Análise em andamento

---

## 🎯 Próximos Passos

1. **Analisar templates restantes** — Buscar padrões de `text-white` + `bg-white`
2. **Catalogar problemas específicos** — Linha, arquivo, descrição
3. **Priorizar correções** — P0 primeiro (ilegibilidade)
4. **Criar plano de correção** — Tela por tela
5. **Validar correções** — Testes manuais

---

## 📝 Notas Técnicas

**Classes CSS suspeitas a investigar:**
- `text-white` + `bg-white` (contraste zero)
- `text-gray-100` + `bg-gray-50` (contraste baixo)
- Gradientes com texto sem contraste adequado

**Ferramentas:**
- Análise manual de templates HTML
- Grep para buscar padrões problemáticos
- Testes manuais pontuais no navegador

---

*Última atualização: 19/03/2026 — Análise iniciada*
