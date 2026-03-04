---
description: Fechar GAP com commit — testes, docs e commit atômico por atividade
---

## /commit — Fluxo de fechamento de GAP

1. Rodar a suite completa e confirmar 0 falhas:
   ```bash
   podman exec exitus-backend python -m pytest --no-cov -q
   ```

2. Se o banco foi alterado (nova tabela, migration, índice), atualizar schema:
   ```bash
   ./scripts/exitus_db_doc.sh
   ```

3. Atualizar documentação no mesmo commit (REGRA #8):
   - `docs/CHANGELOG.md` — sempre
   - `docs/ROADMAP.md` — sempre (status "✅ Concluído (DD/MM/AAAA)")
   - `docs/CODING_STANDARDS.md` — se introduz novo padrão
   - `docs/ARCHITECTURE.md` — se adiciona componentes ou endpoints
   - `docs/OPERATIONS_RUNBOOK.md` — se adiciona scripts
   - `docs/LESSONS_LEARNED.md` — se gerou lição nova

4. Apresentar o comando de commit ao usuário e aguardar aprovação:
   ```bash
   git add -A
   git commit -m "feat(módulo): EXITUS-XXX-000 — resumo em uma linha

   GAPs: EXITUS-XXX-000
   - Artefato A: descrição
   - Artefato B: descrição
   - docs: arquivos atualizados
   - Suite: N passed, 0 failed"
   ```

5. **NUNCA** agrupar múltiplos GAPs em um único commit — uma atividade por commit.

6. Após aprovação, executar o commit e emitir checkpoint:
   ```
   GAP EXITUS-XXX-000 concluído. Suite: N passed, 0 failed. Docs atualizados.
   ```
