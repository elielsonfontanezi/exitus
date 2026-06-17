# Status E2E v3 — Lógica de Negócio

**Branch:** `feature/testes-e2e-v3`  
**Data:** 16/06/2026  
**Autor:** Elielson Fontanezi + Cascade AI

---

## Resultado da Primeira Execução (16/06/2026)

```
180 passed
 22 failed
  1 flaky (smoke — /relatorios/mensal timeout login)
```

**Total de specs:** 20 arquivos (8 v2 + 12 v3 lógica)  
**Total de CTs lógica:** 73 (CT-001 a CT-073)

---

## Falhos por Módulo

| Módulo | Spec | CTs falhando | Causa identificada |
|--------|------|--------------|--------------------|
| Venda | `09-venda-logica` | 5/5 | Seletores modo venda / posições Alpine.js |
| Importação B3 | `10-importacao-b3` | 3/3 | Aba B3 — seletor/texto diverge do template |
| IR/DARF | `11-ir-calculo` | 3/6 | Seletor mês/ano, campos DARF, bens DIRPF |
| Compra | `08-compra-logica` | 1/8 | Toggle compra/venda |
| Rentabilidade | `12-rentabilidade` | 1/4 | Texto TWR/MWR exato |
| Calculadora IR | `13-calculadora-ir` | 1/5 | Campo compensação de prejuízo |
| Screener | `14-screener-filtros` | 1/6 | Botão limpar filtros |
| Exportação CSV | `16-exportacao-csv` | 2/5 | Botão CSV + interceptação download |
| Regressão | `17-fluxo-completo` | 2/5 | Fluxo fiscal + logout |
| Planos | `19-planos-logica` | 1/7 | Detalhe de plano de compra |
| Alertas | `20-alertas-logica` | 2/7 | Botão criar alerta + campo busca/filtro |

---

## Decisão

**Análise tela a tela** antes de corrigir os specs.

Fluxo acordado:
1. Inspecionar cada tela com falha no browser (localhost:8080)
2. Identificar seletores reais (IDs, classes Alpine.js, textos)
3. Reconstruir/corrigir os specs v3 com seletores corretos
4. Re-executar e validar 73/73

---

## Próximo Passo

Iniciar análise pela tela `/operacoes/` (toggle compra/venda, modo venda, importação B3).
