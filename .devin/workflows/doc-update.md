---
description: Atualizar documentação após mudança de código ou estrutura
---

## /doc-update — Fluxo de atualização de documentação

Use este workflow quando for necessário atualizar docs sem fechar um GAP completo
(ex: corrigir inconsistência, adicionar lição aprendida, atualizar status de roadmap).

1. Identificar quais documentos precisam de atualização:

   | Documento | Atualizar quando |
   |---|---|
   | `docs/CHANGELOG.md` | Qualquer mudança relevante |
   | `docs/ROADMAP.md` | Status de GAP mudou |
   | `docs/LESSONS_LEARNED.md` | Nova lição identificada |
   | `docs/CODING_STANDARDS.md` | Novo padrão de código introduzido |
   | `docs/ARCHITECTURE.md` | Componente, endpoint ou container novo |
   | `docs/API_REFERENCE.md` | Endpoint novo ou contrato alterado |
   | `docs/OPERATIONS_RUNBOOK.md` | Script ou procedimento novo |
   | `docs/EXITUS_DB_STRUCTURE.txt` | Schema do banco alterado → rodar `./scripts/update_db_structure.sh` |

2. Aplicar as atualizações nos arquivos relevantes.

3. Apresentar commit de docs ao usuário e aguardar aprovação:
   ```bash
   git add -A
   git commit -m "docs: atualização de documentação — [resumo]

   - doc A: descrição da mudança
   - doc B: descrição da mudança"
   ```
