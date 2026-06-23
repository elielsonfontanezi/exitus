# 🧪 Correção de Testes Backend — Fase 2

> **Status:** Pendente  
> **Data Prevista:** 04/04/2026  
> **Tempo Estimado:** 1.5-2 horas  
> **Modelo IA:** Claude Sonnet

---

## 📊 Status Atual (Pós-Fase 1)

**Resultado da Suite:**
```
546 testes coletados
475 passed (87.0%) ✅
39 failed (7.1%) ❌
88 errors (16.1%) ⚠️ (teardown/cleanup)
```

**Fase 1 Concluída (03/04/2026):**
- ✅ Corrigido `test_model_standards` (enum validation)
- ✅ Corrigido `test_assessora_crud` (blueprint registration)
- ✅ Progresso: +4 testes passando

---

## 🎯 Objetivo da Fase 2

**Meta:** Corrigir 36 testes de IR falhando  
**Resultado Esperado:** 507/546 passed (92.9%)

---

## 📋 Testes Falhando (36 testes de IR)

### **Arquivo:** `test_ir_integration.py`

#### **1. TestApuracao (14 testes)**
```
- test_apuracao_mes_vazio_retorna_envelope_correto
- test_apuracao_envelope_tem_todas_categorias
- test_apuracao_com_venda_abaixo_isencao
- test_apuracao_retorna_mes_correto
- test_apuracao_inclui_por_corretora
- test_apuracao_mes_vazio_por_corretora_lista_vazia
- test_lucro_calculado_via_preco_medio_posicao
- test_alerta_posicao_vazia_quando_sem_pm
- test_apuracao_retorna_campos_prejuizo
- test_prejuizo_acumulado_quando_sem_historico
- test_compensacao_prejuizo_entre_meses
- test_compensacao_parcial_preserva_saldo
- test_mes_vazio_preserva_saldo_anterior
```

#### **2. TestDarf (3 testes)**
```
- test_darf_mes_vazio_retorna_lista_vazia
- test_darf_retorna_mes_correto
- test_darf_envelope_padrao
```

#### **3. TestRegrasFiscais (3 testes)**
```
- test_aliquota_swing_carregada_do_banco
- test_fallback_quando_regra_fiscal_vazia
- test_dividendo_br_isento_abaixo_50k_em_2026
```

#### **4. TestDirpf (6 testes)**
```
- test_estrutura_resposta
- test_campos_renda_variavel
- test_campos_proventos
- test_campos_bens_e_direitos
- test_dirpf_agrega_dados_do_cenario
- test_dirpf_contem_ficha_renda_fixa
```

#### **5. TestRendaFixa (7 testes)**
```
- test_sem_resgates_rf_retorna_zero
- test_lci_isento
- test_cdb_curto_prazo_22_5
- test_tesouro_direto_prazo_medio_20
- test_debenture_prazo_longo_15
- test_rf_aparece_no_darf_informativo
- test_rf_nao_afeta_swing_acoes
```

#### **6. TestUnitsIR (3 testes)**
```
- test_unit_isento_abaixo_20k
- test_unit_tributado_acima_20k
- test_unit_enquadrada_em_swing_acoes_nao_em_rf
```

---

## 🔍 Estratégia de Correção

### **Passo 1: Análise de Padrão (30 min)**

1. **Executar 1 teste de cada subcategoria** para identificar padrão comum:
   ```bash
   podman exec exitus-backend python -m pytest \
     tests/test_ir_integration.py::TestApuracao::test_apuracao_mes_vazio_retorna_envelope_correto \
     -xvs 2>&1 | grep -A 30 "FAILED\|AssertionError"
   ```

2. **Identificar causas prováveis:**
   - ❌ Fixtures desatualizadas (falta `assessora_id`)
   - ❌ Mudanças no schema do banco (multi-tenancy)
   - ❌ Services com filtros por assessora
   - ❌ Mudanças em estrutura de resposta

3. **Documentar padrão encontrado** para correção em lote

---

### **Passo 2: Correção de Fixtures (30 min)**

**Arquivos a modificar:**
- `tests/conftest.py` - Fixtures globais
- `tests/test_ir_integration.py` - Fixtures locais

**Correções esperadas:**
```python
# Adicionar assessora_id em fixtures de transações
transacao = Transacao(
    usuario_id=usuario.id,
    assessora_id=assessora.id,  # ← Adicionar
    ativo_id=ativo.id,
    # ...
)

# Adicionar assessora_id em fixtures de portfolios
portfolio = Portfolio(
    usuario_id=usuario.id,
    assessora_id=assessora.id,  # ← Adicionar
    # ...
)
```

---

### **Passo 3: Correção em Lote (30-45 min)**

**Aplicar correções por subcategoria:**

1. **TestApuracao** (14 testes)
   - Atualizar fixtures de transações
   - Adicionar `assessora_id` em queries
   - Validar estrutura de resposta

2. **TestDarf** (3 testes)
   - Atualizar fixtures de DARF
   - Verificar cálculos com multi-tenancy

3. **TestRegrasFiscais** (3 testes)
   - Verificar regras fiscais no banco de testes
   - Adicionar seeds se necessário

4. **TestDirpf** (6 testes)
   - Atualizar estrutura de resposta
   - Verificar agregação de dados

5. **TestRendaFixa** (7 testes)
   - Atualizar fixtures de ativos RF
   - Verificar cálculos de IR

6. **TestUnitsIR** (3 testes)
   - Verificar enum TipoAtivo.UNIT
   - Atualizar fixtures de units

---

### **Passo 4: Validação (15 min)**

```bash
# Executar suite completa de IR
podman exec exitus-backend python -m pytest tests/test_ir_integration.py -v --tb=short

# Executar suite completa
podman exec exitus-backend python -m pytest --no-cov -q --tb=no
```

**Meta:** 507/546 passed (92.9%)

---

## 📝 Checklist de Execução

- [ ] Executar 1 teste de cada subcategoria
- [ ] Identificar padrão comum de falha
- [ ] Documentar causas raiz
- [ ] Corrigir fixtures globais (conftest.py)
- [ ] Corrigir fixtures locais (test_ir_integration.py)
- [ ] Aplicar correções em TestApuracao (14 testes)
- [ ] Aplicar correções em TestDarf (3 testes)
- [ ] Aplicar correções em TestRegrasFiscais (3 testes)
- [ ] Aplicar correções em TestDirpf (6 testes)
- [ ] Aplicar correções em TestRendaFixa (7 testes)
- [ ] Aplicar correções em TestUnitsIR (3 testes)
- [ ] Executar suite de IR completa
- [ ] Executar suite completa
- [ ] Validar 507/546 passed (92.9%)
- [ ] Commit Fase 2
- [ ] Atualizar PROJECT_STATUS.md

---

## 🚀 Comandos Úteis

```bash
# Executar teste específico com debug
podman exec exitus-backend python -m pytest \
  tests/test_ir_integration.py::TestApuracao::test_apuracao_mes_vazio_retorna_envelope_correto \
  -xvs

# Executar subcategoria completa
podman exec exitus-backend python -m pytest \
  tests/test_ir_integration.py::TestApuracao \
  -v --tb=short

# Executar suite de IR completa
podman exec exitus-backend python -m pytest \
  tests/test_ir_integration.py \
  -v --tb=short

# Ver apenas falhas
podman exec exitus-backend python -m pytest \
  tests/test_ir_integration.py \
  -q --tb=no 2>&1 | grep "FAILED"
```

---

## 📊 Progresso Esperado

| Fase | Testes Passando | % | Status |
|------|-----------------|---|--------|
| Inicial | 471/546 | 86.3% | ✅ |
| Fase 1 | 475/546 | 87.0% | ✅ Concluída |
| **Fase 2** | **507/546** | **92.9%** | ⏳ Pendente |
| Fase 3 | 513/546 | 94.0% | 📋 Planejada |

---

## 🔗 Próximas Fases

**Fase 3: Investigação de RLS (6 testes)**
- Tempo: 1-1.5 horas
- Meta: 513/546 passed (94.0%)

**Fase 4: Cleanup de Errors (Opcional)**
- Tempo: 1 hora
- Meta: 513/546 passed, 0 errors
