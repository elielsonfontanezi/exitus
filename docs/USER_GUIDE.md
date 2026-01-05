
# 📖 Guia do Usuário - Exitus v0.7.5

**Data**: 05/Jan/2026 | **Status**: M7 Production Ready | **Acesso**: `http://localhost:8080`

## Tour Rápido pelos Dashboards (10 Telas)

| Dashboard | URL | O que você vê | Ações Principais |
|-----------|-----|---------------|------------------|
| **Dashboard Principal** | `/dashboard` | Buy Signals TOP 10 (PETR4 80/100) | Sidebar → outras telas |
| **Buy Signals** | `/dashboard/buy-signals` | Ativos com score compra/venda, preço teto | Filtros mercado/ticker |
| **Portfólios** | `/dashboard/portfolios` | Patrimônio total, alocação % (ações/FII), rentabilidade | Recalcular posições, + Novo |
| **Ativos** | `/dashboard/assets` | Lista ativos (ticker, mercado B3/NASDAQ) | Detalhes ticker |
| **Transações** | `/dashboard/transactions` | Histórico compra/venda, volume R$, gráficos | + Nova transação |
| **Proventos** | `/dashboard/dividends` | Dividendos/JCP pagos/previsão, badges status | Filtros tipo/status |
| **Movimentações** | `/dashboard/movimentacoes` | Depósitos/saques (XP corretora R$5k) | + Nova movimentação |
| **Alertas** | `/dashboard/alerts` | PETR4 >R$35 (ativo/inativo), toggle/delete | + Novo alerta |
| **Relatórios** | `/dashboard/reports` | 15+ relatórios PERFORMANCE (paginação 2p) | Gerar novo (data início/fim) |
| **Analytics** | `/dashboard/analytics` | Monte Carlo simulações (futuro M8) | Gerar simulação |

**Navegação**: Sidebar esquerdo (colapsível mobile) + Navbar superior.

## Cenários Práticos (Passo a Passo)

### 1. Criar Portfolio + Primeira Compra (10min)

1. **Login**: `admin` / `admin123` → Dashboard.
2. **Novo Portfolio**: `/portfolios` → "+ Novo" → Nome "Meu Portfolio BR" → Submit.
3. **Nova Transação**: `/transactions` → "+ Nova" → 
   - Ticker: `PETR4`
   - Corretora: `XP` 
   - Tipo: `COMPRA`
   - Quantidade: `100`
   - Preço unit: `R$ 32,50`
   - Data: hoje
4. **Recalcular**: Portfolio → "Recalcular Posições" → PM R$32,50 | Valor R$3.250.
5. **Ver Dashboard**: Alocação Ações 100% | Patrimônio R$3.250.

### 2. Configurar Alerta PETR4 Alta (3min)

1. **Alertas** → "+ Novo":
   - Nome: "PETR4 Breakout"
   - Ticker: `PETR4`
   - Tipo: `alta_preco`
   - Operador: `>`
   - Valor: `35.00`
   - Frequência: `imediata`
   - Canais: `webapp`
2. **Salvar** → Verde "ATIVO" | Toggle para pausar.

### 3. Gerar Relatório Performance (2min)

1. **Relatórios** → "Gerar Novo":
   - Tipo: `PERFORMANCE`
   - Data início: `2026-01-01`
   - Data fim: `2026-01-31`
   - Formato: `PDF`
2. **Submit** → Novo item tabela (ID gerado) | Sharpe 1.45, Rentabilidade 12.5%.

## Dicas Rápidas

**Recalcular Posições**: Sempre após compra/venda/provento (manual por performance).
**Filtros**: Todos dashboards suportam ticker/mercado/data (HTMX live).
**Mock Fallback**: Se backend offline, dados demo carregam sem quebrar.
**Export**: Futuro M8 (CSV relatórios).

**Métricas Explicadas**:
- **PM (Preço Médio)**: Valor médio ponderado das compras.
- **Sharpe Ratio**: Rentabilidade ajustada por risco (1.45 = bom).
- **Drawdown Máximo**: Maior perda acumulada (-8.3%).

**Ajuda**: `docs/OPERATIONS_RUNBOOK.md` (erros comuns) | Logs Podman.

---
**Geração**: Perplexity AI | **Base**: M5-M7 dashboards validados | **Próximo**: API_REFERENCE.md
