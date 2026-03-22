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
1. `scripts/load_scenario.py` - Carregador de cenários
2. `backend/app/seeds/seed_movimentacoes.py` - Seed movimentações
3. `backend/app/seeds/seed_alertas.py` - Seed alertas

**Arquivos a modificar:**
1. `scripts/reset_and_seed.py` - Adicionar opção --scenario

**Resultado esperado:**
- Dashboard com saldo caixa != 0
- Alertas carregados
- Dados completos do test_e2e.json

---

**LEIA:** `docs/TEST_SCENARIOS.md`, `scripts/seed_data/scenarios/test_e2e.json`, `docs/EXITUS_DB_STRUCTURE.txt` 

**BOA IMPLEMENTAÇÃO! 🎨**
