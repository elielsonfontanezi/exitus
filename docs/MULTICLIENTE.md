# MULTICLIENTE-001 — Multi-Tenancy (Documento Consolidado)

> **Status:** 🟡 85% Concluído (Partes 1-3)  
> **Início:** 16/03/2026  
> **Modelo IA:** Claude Sonnet  
> **Arquitetura:** Shared Database + Tenant Column  
> **Assessora Padrão ID:** `23c54cb4-cb0a-438f-b985-def21d70904e`

---

## 🎯 Objetivo

Implementar sistema multi-tenant para permitir que múltiplas assessoras de investimento utilizem o Exitus, cada uma com seus próprios usuários, portfolios e dados isolados.

---

## 🏗️ Arquitetura Multi-Tenant

### Modelo: Shared Database + Tenant Column

```
┌─────────────────────────────────────────────────┐
│              Banco de Dados Único               │
│                                                 │
│  ┌──────────────┐  ┌──────────────┐           │
│  │  Assessora A │  │  Assessora B │           │
│  │              │  │              │           │
│  │ - Usuários   │  │ - Usuários   │           │
│  │ - Portfolios │  │ - Portfolios │           │
│  │ - Transações │  │ - Transações │           │
│  └──────────────┘  └──────────────┘           │
│                                                 │
│  Isolamento via assessora_id em WHERE clauses  │
└─────────────────────────────────────────────────┘
```

### Tabelas Globais (Sem assessora_id)

- `ativo` — Ativos são compartilhados
- `corretora` — Corretoras são globais
- `feriado_mercado` — Feriados são globais
- `fonte_dados` — Fontes são globais
- `regra_fiscal` — Regras fiscais são globais
- `parametros_macro` — Parâmetros são globais
- `taxa_cambio` — Taxas de câmbio são globais

### Trade-offs

- ✅ Simples de implementar — coluna adicional
- ✅ Performance adequada — índices otimizados
- ✅ Migração incremental — nullable inicialmente
- ✅ Backup/restore simples — um banco só
- ⚠️ Isolamento lógico (não físico) — requer validações rigorosas
- ⚠️ Queries mais complexas — WHERE assessora_id em tudo

---

## ✅ Parte 1 — Model e Migrations (16/03/2026)

### Model Assessora (`assessora.py`)

- **23 campos:** id, nome, razao_social, cnpj, email, telefone, site, endereco, cidade, estado, cep, numero_cvm, anbima, ativo, data_cadastro, logo_url, cor_primaria, cor_secundaria, max_usuarios, max_portfolios, plano, created_at, updated_at
- **15 relacionamentos:** usuarios, portfolios, transacoes, posicoes, planos_compra, planos_venda, movimentacoes_caixa, proventos, saldos_prejuizo, saldos_darf_acumulados, historicos_precos, eventos_corporativos, configuracoes_alertas, auditorias_relatorios, logs_auditoria
- **4 properties:** total_usuarios, total_portfolios, pode_adicionar_usuario, pode_adicionar_portfolio

### Migrations

**Migration 1: `20260316_1540_assessora`**
- Tabela `assessora` criada
- 4 índices: nome (unique), cnpj (unique), email (unique), ativo

**Migration 2: `20260316_1545_assessora_id`**
- `assessora_id` adicionado em **20 tabelas**
- 20 foreign keys com `ondelete='CASCADE'`
- 24 índices (20 simples + 4 compostos)

---

## ✅ Parte 2 — Models Atualizados (16/03/2026)

### 20/20 Models com `assessora_id` (100%)

**Parte 1 (4 models):** Usuario, Portfolio, PlanoVenda, PlanoCompra  
**Parte 2A (7 models):** Posicao, Transacao, Alerta, RelatorioPerformance, ProjecaoRenda, CalendarioDividendo  
**Parte 2B (9 models):** MovimentacaoCaixa, Provento, SaldoPrejuizo, SaldoDarfAcumulado, HistoricoPreco, EventoCorporativo, ConfiguracaoAlerta, AuditoriaRelatorio, LogAuditoria

### Problemas Resolvidos

- **Revision ID longo:** Reduzido para 32 chars
- **Coluna inexistente:** Corrigido `data` → `data_transacao`
- **Import faltando:** Adicionado `from sqlalchemy.orm import relationship` em SaldoDarfAcumulado e HistoricoPreco

---

## ✅ Parte 3 — Implementação Funcional (16/03/2026)

### Migração de Dados

- **Assessora padrão criada:** `23c54cb4-cb0a-438f-b985-def21d70904e`
- **13 registros migrados:** 5 usuários + 1 evento corporativo + 7 logs de auditoria

### Helper de Tenant (`backend/app/utils/tenant.py`)

4 funções utilitárias:
1. `get_current_assessora_id()` — extrai assessora_id do JWT
2. `require_assessora(f)` — decorator (retorna 403 se sem assessora)
3. `require_same_assessora(model_assessora_id)` — valida registro
4. `filter_by_assessora(query, model_class)` — filtro automático

### JWT Atualizado (`backend/app/services/auth_service.py`)

```python
additional_claims = {'role': user.role.value}
if user.assessora_id:
    additional_claims['assessora_id'] = str(user.assessora_id)
```

### Services com Filtros (5/20 principais)

1. ✅ usuario_service.py
2. ✅ portfolio_service.py
3. ✅ transacao_service.py
4. ✅ posicao_service.py
5. ✅ plano_venda_service.py

### Testes (3/3 passando)

1. ✅ test_jwt_com_assessora_id
2. ✅ test_tenant_helper_functions
3. ✅ test_services_importam_tenant_utils

---

## 🔴 Pendências (15% restante)

### Services Restantes (15+)

Precisam de `filter_by_assessora()`:
- movimentacao_caixa_service.py
- provento_service.py
- saldo_prejuizo_service.py
- plano_compra_service.py
- alerta_service.py
- relatorio_performance_service.py
- E mais 9+ services

### Middleware Completo

- [ ] Implementar `@require_assessora` em todos os endpoints
- [ ] Row-level security completa
- [ ] Validação cross-tenant em todos os CRUDs

### Dashboard Admin

- [ ] Dashboard de gestão por assessora
- [ ] Métricas e limites por assessora
- [ ] CRUD de assessoras

### Testes Ampliados

- [ ] Testes de isolamento cross-tenant
- [ ] Atualizar fixtures com múltiplas assessoras
- [ ] Garantir 491 testes passando após alterações

---

## 📊 Estatísticas Consolidadas

| Métrica | Valor |
|---------|-------|
| **Arquivos criados** | 6 (model, 2 migrations, script, tenant.py, test) |
| **Arquivos modificados** | 25+ (20 models + 5 services) |
| **Tabelas afetadas** | 21 (1 nova + 20 com assessora_id) |
| **Índices criados** | 24 (20 simples + 4 compostos) |
| **Foreign keys** | 20 |
| **Dados migrados** | 13 registros |
| **Testes criados** | 3 |

---

## 📝 Comandos Úteis

```bash
# Verificar assessoras
podman exec exitus-db psql -U exitus -d exitusdb -c "SELECT id, nome, email FROM assessora;"

# Verificar usuários com assessora
podman exec exitus-db psql -U exitus -d exitusdb -c "SELECT username, assessora_id FROM usuario;"

# Verificar tabela tem assessora_id
podman exec exitus-db psql -U exitus -d exitusdb -c "\d+ usuario" | grep assessora

# Verificar imports
podman exec exitus-backend python -c "from app.models import Assessora; print('OK')"
```

---

## 📚 Referências Arquivadas

Documentos detalhados de cada parte estão em `docs/archive/`:
- `MULTICLIENTE_PARTE1.md` — Model, migrations, 4 models iniciais
- `MULTICLIENTE_PARTE2A.md` — Migrations aplicadas, 11 models, assessora padrão
- `MULTICLIENTE_PARTE2B.md` — 9 models restantes, relacionamentos completos
- `MULTICLIENTE_PARTE3.md` — Migração dados, helper tenant, JWT, 5 services

---

*Última atualização: 18/03/2026*  
*Modelo IA utilizado: Claude Sonnet*  
*Status: 85% — Aguardando conclusão dos services restantes e testes ampliados*
