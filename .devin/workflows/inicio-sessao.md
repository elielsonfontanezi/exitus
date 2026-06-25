---
description: Iniciar sessão nova — ler fontes de verdade e retomar contexto
---

## /inicio-sessao — Fluxo obrigatório ao iniciar qualquer sessão

Execute este workflow ANTES de qualquer ação, análise ou código.

1. Ler **obrigatoriamente** nesta ordem:
   ```
   1. docs/LESSONS_LEARNED.md        ← erros reais — ler PRIMEIRO
   2. docs/PROJECT_STATUS.md         ← estado atual, métricas, versão
   3. docs/AUDITORIA_FUNCIONAL_18_06_2026.md  ← P-items pendentes/resolvidos
   4. docs/ROADMAP.md                ← GAPs planejados e status
   5. docs/CHANGELOG.md              ← últimas mudanças (top 30 linhas)
   ```

2. Apresentar ao usuário o **resumo de contexto**:
   ```
   📋 Contexto retomado:
   - Versão: vX.Y.Z (data)
   - Suite: N passed / M failed
   - P-items pendentes: P3, P5, P6, P7
   - Último commit: [hash] — [mensagem]
   - Próximo passo sugerido: [item]
   ```

3. Perguntar ao usuário o que deseja fazer nesta sessão.

4. Só então iniciar análise/implementação seguindo o fluxo do .windsurfrules REGRA #1.

---

## ⚠️ REGRA ANTI-PERDA: Toda síntese deve ir para documento ANTES de apresentar ao usuário

**Problema documentado (24/06/2026):** Análise de priorização (sequência P3 → CONSTRAINT-001 → P8, pré-requisitos das NEW-XX) foi gerada apenas no chat e se perdeu ao fechar a sessão.

**Regra obrigatória:** Toda vez que a IA gerar qualquer um dos itens abaixo, ele DEVE ser escrito no documento relevante ANTES de ser apresentado ao usuário:

- Sequência de execução de pendências (ex: "fazer P3 antes de P8 porque...")
- Pré-requisitos entre tarefas
- Decisões técnicas descartadas e o motivo
- Análise de impacto de um bug ou mudança
- Sugestões de próximos passos com justificativa

**Onde registrar:**
- Pendências e priorização → `docs/AUDITORIA_FUNCIONAL_18_06_2026.md` (seção "Análise de Sessão — DD/MM/AAAA")
- Decisões técnicas → `docs/LESSONS_LEARNED.md` (lição L-XXX-NNN)
- Próximos passos do roadmap → `docs/ROADMAP.md`

**Formato obrigatório para seção de análise:**
```markdown
## 🧭 Análise de Sessão — DD/MM/AAAA

### Contexto
[o que motivou a análise]

### Sequência recomendada
1. **ITEM** (estimativa) — justificativa
2. ...

### Pré-requisitos identificados
- ITEM-A bloqueia ITEM-B porque: ...

### Decisões descartadas
- Alternativa X descartada porque: ...
```

---

## Checklist de docs obrigatórios ao FECHAR qualquer sessão

Antes do commit final, verificar CADA item abaixo e confirmar ou justificar:

| Documento | Obrigatório | Condição |
|---|---|---|
| `docs/CHANGELOG.md` | ✅ Sempre | Entrada com artefatos e suite |
| `docs/PROJECT_STATUS.md` | ✅ Sempre | Data, versão, métricas |
| `docs/AUDITORIA_FUNCIONAL_18_06_2026.md` | ✅ Se P-item resolvido | Marcar ✅, detalhar fix |
| `docs/ROADMAP.md` | ✅ Sempre verificar | Marcar GAP como concluído se aplicável; atualizar "Próximo" |
| `docs/LESSONS_LEARNED.md` | Se nova lição | Adicionar entrada L-XXX-NNN |
| `docs/CODING_STANDARDS.md` | Se novo padrão | Documentar convenção |
| `docs/MODULES.md` | Se endpoint mudou | Status M0-M7, endpoints por módulo |
| `docs/ARCHITECTURE.md` | Se novo componente | Atualizar diagrama/tabela |
| `docs/OPERATIONS_RUNBOOK.md` | Se novo script | Documentar uso |
