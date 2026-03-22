# 🎯 Handoff para Sonnet - Integração de Cenários de Teste

> **Data:** 22/03/2026  
> **Modelo:** Claude Sonnet (recomendado)  
> **Tarefa:** Integrar cenários de teste JSON ao sistema de seeds

---

## 📋 **CONTEXTO COMPLETO**

### **Situação Atual:**
1. ✅ Dashboard v2 implementado e funcionando
2. ✅ Cenários de teste criados em `scripts/seed_data/scenarios/` 
3. ❌ Cenários NÃO integrados ao sistema de seeds
4. ❌ Dados faltantes no dashboard (saldo caixa = R$ 0, alertas = [])

### **Problema:**
O dashboard não mostra todos os dados porque:
- Não há **movimentações de caixa** no banco
- Não há **alertas** no banco
- Os cenários JSON existem mas não são carregados

---

## 🎯 **SUA MISSÃO**

Implementar integração completa dos cenários JSON com sistema de seeds.

**Arquivos a criar:**
1. `scripts/load_scenario.py` - Carregador de cenários JSON
2. `backend/app/seeds/seed_movimentacoes.py` - Seed movimentações de caixa
3. `backend/app/seeds/seed_alertas.py` - Seed alertas (3 tipos: PRECO_ALVO, STOP_LOSS, DIVIDENDO)

**Arquivos a modificar:**
1. `scripts/reset_and_seed.py` - Adicionar opção --scenario

**Dados do test_e2e.json (ATUALIZADO 22/03/2026):**
- ✅ 3 usuários (admin, user, viewer)
- ✅ 1 assessora
- ✅ 7 ativos (3 ações BR, 2 FIIs, 2 stocks US)
- ✅ 3 corretoras
- ✅ 4 transações (compras e vendas)
- ✅ 2 proventos (dividendo + rendimento FII)
- ✅ 2 movimentações de caixa (depósito R$ 10.000, saque R$ 500)
- ✅ **3 alertas** (preço alvo, stop loss, dividendo) ← NOVO!

**Resultado esperado:**
- Dashboard com saldo caixa = R$ 9.500,00 (10.000 - 500)
- 3 alertas carregados e visíveis
- Tela de alertas funcional
- Dados completos para todas as telas principais

---

**LEIA:** `docs/TEST_SCENARIOS.md`, `scripts/seed_data/scenarios/test_e2e.json`, `docs/EXITUS_DB_STRUCTURE.txt` 

**BOA IMPLEMENTAÇÃO! 🎨**
