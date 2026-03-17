# 📋 Testes e Validação - Exitus

> **Status:** 491/491 testes passando (100%) ✅  
> **Total:** 39 arquivos entre scripts e testes formais  
> **Última atualização:** 11/03/2026

---

## 📁 Estrutura de Testes

### 🧪 **Scripts de Validação (`tests/`)**
Scripts bash para validação por fase do desenvolvimento.

| Script | Propósito | Fase |
|--------|----------|------|
| **[mod0_validacao_final.sh](mod0_validacao_final.sh)** | Health checks completos | Módulo 0 |
| **[mod1_validacao_final_fase1.sh](mod1_validacao_final_fase1.sh)** | Verificação containers | Fase 1 |
| **[mod1_validacao_final_fase2.sh](mod1_validacao_final_fase2.sh)** | Estrutura básica | Fase 2 |
| **[mod1_validacao_final_fase3.sh](mod1_validacao_final_fase3.sh)** | Models complementares | Fase 3 |
| **[mod1_validacao_final_fase4.sh](mod1_validacao_final_fase4.sh)** | Novos endpoints | Fase 4 |
| **[mod1_validacao_final_fase5.sh](mod1_validacao_final_fase5.sh)** | Qualidade e performance | Fase 5 |

### 🐍 **Testes Formais (`backend/tests/`)**
Testes Python com pytest para validação completa do sistema.

| Categoria | Arquivos Principais | Testes |
|-----------|-------------------|--------|
| **Motor IR** | `test_ir_integration.py` (47KB) | Cálculo fiscal completo |
| **Importação B3** | `test_import_b3_parsers.py` (59) | Parsers de extratos |
| **DARF Acumulado** | `test_darf_acumulado.py` (8) | Acúmulo < R$10 |
| **Rentabilidade** | `test_rentabilidade.py` (21) | Métricas de retorno |
| **Idempotência** | `test_import_b3_idempotencia.py` (18) | Sem duplicação |
| **Reconciliação** | `test_reconciliacao.py` | Verificação de dados |
| **IOF** | `test_iof.py` | Cálculo de IOF |
| **Exportação** | `test_export_integration.py` | Múltiplos formatos |
| **Autenticação** | `test_auth_integration.py` | JWT e RBAC |
| **APIs** | `test_newapis_integration.py` | Endpoints REST |
| **Câmbio** | `test_cambio_integration.py` | Multi-moeda |
| **Circuit Breaker** | `test_circuit_breaker.py` | Resiliência |
| **Logs** | `test_auditlog.py` | Auditoria |
| **Calendário** | `test_calendario_dividendos.py` | Dividendos |
| **Constraints** | `test_constraints.py` | Integridade DB |

---

## 🚀 Como Executar

### Scripts de Validação
```bash
# Validação completa (todas as fases)
./tests/mod0_validacao_final.sh

# Fase específica
./tests/mod1_validacao_final_fase3.sh
```

### Testes Formais
```bash
# Todos os testes
podman exec exitus-backend python -m pytest --no-cov -q

# Teste específico
podman exec exitus-backend python -m pytest backend/tests/test_darf_acumulado.py

# Com coverage
podman exec exitus-backend python -m pytest --cov=app
```

---

## 📊 Métricas Atuais

| Métrica | Valor | Status |
|---------|-------|--------|
| **Testes totais** | 491 | ✅ |
| **Passando** | 491 | 100% |
| **Falhando** | 0 | ✅ |
| **Erros** | 0 | ✅ |
| **Coverage** | ?% | ⚠️ Medir |

---

## 🎯 Boas Práticas

1. **Antes de commitar:** Rodar `mod0_validacao_final.sh`
2. **Após mudanças:** Rodar testes específicos do módulo
3. **IR/Importação:** Sempre testar com `test_ir_integration.py`
4. **Novos endpoints:** Adicionar teste em `test_*_integration.py`

---

## 📚 Documentação Relacionada

- **[TESTES_HISTORICO.md](../docs/TESTES_HISTORICO.md)** - Histórico de correções
- **[CODING_STANDARDS.md](../docs/CODING_STANDARDS.md)** - Padrões de código
- **[ROADMAP.md](../docs/ROADMAP.md)** - GAPs implementados

---

*Última atualização: 11/03/2026*  
*Total de testes: 491 (100% passando)*
