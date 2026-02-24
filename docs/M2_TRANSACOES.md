# Relatório de Validação — M2-TRANSACOES
**Versão:** v0.7.12
**Data:** 2026-02-24
**Status:** ✅ APROVADO — 7/7 GAPs corrigidos e revalidados

---

## Escopo

Endpoints validados do módulo de Transações:

| Endpoint | Método | Descrição |
|---|---|---|
| `/api/transacoes` | GET | Listagem paginada com filtros |
| `/api/transacoes` | POST | Criação de transação |
| `/api/transacoes/<id>` | GET | Busca por ID |
| `/api/transacoes/<id>` | PUT | Atualização |
| `/api/transacoes/<id>` | DELETE | Deleção |
| `/api/transacoes/resumo/<ativo_id>` | GET | Resumo agregado por ativo |

---

## Cenários Validados (TRX-003 a TRX-008 — aprovados antes do fix batch)

| ID | Cenário | HTTP | Resultado |
|---|---|---|---|
| TRX-003 | POST compra válida | 201 | ✅ |
| TRX-004 | POST venda válida | 201 | ✅ |
| TRX-005 | POST dividendo válido | 201 | ✅ |
| TRX-006 | GET listagem paginada | 200 | ✅ |
| TRX-007 | GET por ID próprio | 200 | ✅ |
| TRX-008 | GET resumo ativo válido | 200 | ✅ |

---

## GAPs Identificados e Corrigidos (Fix Batch v0.7.12)

### EXITUS-TRX-001 — `custos_totais` null na resposta
- **Arquivo:** `app/schemas/transacao_schema.py`
- **Causa:** `SQLAlchemyAutoSchema` não incluía `custos_totais` com `as_string=True`
  de forma confiável; campo aparecia null no dump.
- **Fix:** Declarado explicitamente em `TransacaoResponseSchema` e `TransacaoListSchema`
  como `fields.Decimal(as_string=True)`.
- **Revalidação:** `custos_totais: "10.50"` ✅

### EXITUS-TRX-002 — PUT retorna 400/404 para TRX de outro usuário (esperado: 403)
- **Arquivos:** `transacao_service.py`, `transacoes/routes.py`
- **Causa:** `update()` lançava `ValueError` único para não-encontrado e não-autorizado;
  route capturava tudo como 400.
- **Fix:** Service separa `ValueError` (not found → 404) de `PermissionError`
  (ownership → 403); route captura cada exceção no handler correto.
- **Revalidação:** `"Acesso negado: transação pertence a outro usuário"` HTTP 403 ✅

### EXITUS-TRX-003 — PUT retorna 400 para ID inexistente (esperado: 404)
- **Arquivos:** `transacao_service.py`, `transacoes/routes.py`
- **Causa:** Busca usava `filter_by(id=..., usuario_id=...)` — ID de outro usuário e
  ID inexistente produziam o mesmo resultado (None), ambos caíam em `ValueError` → 400.
- **Fix:** `update()` faz `Transacao.query.get(id)` sem filtro de usuário primeiro;
  None → `ValueError` → 404. Só então verifica ownership.
- **Revalidação:** `"Transação ... não encontrada"` HTTP 404 ✅

### EXITUS-TRX-004 — DELETE retorna 404 para TRX de outro usuário (esperado: 403)
- **Arquivos:** `transacao_service.py`, `transacoes/routes.py`
- **Causa:** Mesmo padrão do TRX-002 — `delete()` usava `filter_by` combinado,
  retornando None para TRX alheia; route devolvia 404.
- **Fix:** Mesmo padrão do TRX-002 — existência primeiro, ownership depois.
- **Revalidação:** `"Acesso negado: transação pertence a outro usuário"` HTTP 403 ✅

### EXITUS-TRX-005 — Lista não serializa `valor_total`, `data_transacao`, nested `ativo`
- **Arquivo:** `app/schemas/transacao_schema.py`
- **Causa:** `TransacaoResponseSchema` (SQLAlchemyAutoSchema) não garantia os campos
  na listagem — lazy load do relacionamento `ativo` não era executado.
- **Fix:** Criado `TransacaoListSchema` (Schema puro) com todos os campos explícitos
  incluindo `data_transacao = fields.DateTime()`, `valor_total = fields.Decimal()` e
  `ativo = fields.Method('get_ativo_info')`. Service usa `joinedload` na listagem.
- **Revalidação:** `valor_total`, `data_transacao`, `ativo.ticker`, `custos_totais`
  presentes e não-null ✅

### EXITUS-TRX-006 — Paginação dentro de `.data` em vez da raiz
- **Arquivo:** `app/blueprints/transacoes/routes.py`
- **Causa:** `return success({transacoes: ..., total: ..., pages: ...})` aninhava
  os metadados de paginação dentro de `.data`.
- **Fix:** `GET /` refatorado com `jsonify` manual; `total`, `pages`, `page`,
  `per_page` promovidos para raiz do JSON; `data` contém apenas o array de itens.
- **Revalidação:** `{total: 21, pages: 7, page: 1, per_page: 3, data: [...]}` ✅

### EXITUS-TRX-007 — `/resumo/{ativo_id}` retorna 200 para UUID inexistente
- **Arquivo:** `app/services/transacao_service.py`
- **Causa:** `get_resumo_por_ativo()` não validava existência do ativo — retornava
  dict com zeros para qualquer UUID.
- **Fix:** `Ativo.query.get(ativo_id)` antes dos cálculos; None → `ValueError` → 404.
- **Revalidação:** HTTP 404 para UUID fake ✅; HTTP 200 com dados reais para UUID válido ✅

---

## Hotfixes Inclusos no Mesmo Commit

| Problema | Arquivo | Fix |
|---|---|---|
| `tipo` gravado como `'COMPRA'` (uppercase) — `InvalidTextRepresentation` no PostgreSQL | `transacao_service.py` | `.upper()` → `.lower()` no `create()` |
| Import `notfound` inexistente em `responses.py` | `transacoes/routes.py` | Corrigido para `not_found` |
| Vírgula trailing no import de schemas | `transacoes/routes.py` | Removida |

---

## Resultado Final

| Métrica | Valor |
|---|---|
| GAPs identificados | 7 |
| GAPs corrigidos | 7 |
| Hotfixes inclusos | 3 |
| Cenários revalidados | 7/7 ✅ |
| Cobertura de endpoints | 6/6 ✅ |
| Performance | < 500ms ✅ |

---

*Gerado em 2026-02-24 — Sistema Exitus v0.7.12*
