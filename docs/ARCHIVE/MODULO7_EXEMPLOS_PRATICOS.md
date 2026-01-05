# 🎨 MÓDULO 7: EXEMPLOS PRÁTICOS E DIAGRAMAS

**Data:** 07/12/2025
**Status:** GUIA DE REFERÊNCIA
**Objetivo:** Exemplos de entrada/saída, diagramas, casos de uso

---

## 📊 EXEMPLO 1: FLUXO RELATÓRIO COMPLETO

### Entrada: POST /api/relatorios/gerar
```json
{
  "usuario_id": "usr_12345",
  "portfolio_id": "prt_67890",
  "tipo_relatorio": "PERFORMANCE",
  "data_inicio": "2024-10-01",
  "data_fim": "2024-12-31",
  "filtros": {
    "mercados": ["BR", "US"],
    "setores": ["Energias Renováveis", "Tecnologia"],
    "classes": ["ACAO", "ETF"]
  },
  "formato_export": "VISUALIZACAO"
}
```

### Processamento (Backend)
```
1. Validar JWT + permissões
2. Buscar Portfolio (user_id, portfolio_id)
3. Buscar Posições (portfolio_id, data_inicio-fim, filtros)
4. Buscar Proventos (posições, data_inicio-fim)
5. Buscar Movimentações (compras/vendas)
6. Calcular métricas:
   - Retorno bruto/líquido
   - Volatilidade (desvio padrão retornos diários)
   - Índice Sharpe: (Retorno - 3%) / Volatilidade
   - Índice Sortino: idem com downside only
   - IRR: scipy.optimize.newton()
   - Max Drawdown: peak-to-trough
7. Estruturar JSON resposta
8. Persistir em AuditoriaRelatorio
9. Retornar para frontend
```

### Saída: Response 200 OK
```json
{
  "id": "rlt_aabbcc",
  "usuario_id": "usr_12345",
  "portfolio_id": "prt_67890",
  "periodo": "2024-10-01 a 2024-12-31",
  "timestamp_criacao": "2024-12-07T15:30:00Z",

  "metricas": {
    "valor_inicial": 250000.00,
    "valor_final": 281500.00,
    "retorno_bruto": 26.5,
    "retorno_liquido": 24.8,
    "volatilidade": 18.3,
    "indice_sharpe": 0.98,
    "indice_sortino": 1.42,
    "irr": 32.5,
    "max_drawdown": -8.2,
    "beta_mercado": 1.05,
    "alfa_jensen": 2.3
  },

  "alocacao": {
    "por_classe": {
      "ACAO": { "percentual": 45, "valor": 126675 },
      "ETF": { "percentual": 35, "valor": 98525 },
      "FII": { "percentual": 20, "valor": 56300 }
    },
    "por_pais": {
      "BR": { "percentual": 65, "valor": 182975 },
      "US": { "percentual": 35, "valor": 98525 }
    },
    "por_setor": {
      "Energias_Renoveaveis": { "percentual": 25, "valor": 70375 },
      "Tecnologia": { "percentual": 22, "valor": 61930 },
      "Financeiro": { "percentual": 18, "valor": 50670 },
      "Utilidades": { "percentual": 35, "valor": 98525 }
    }
  },

  "top_ativos": [
    {
      "ativo": "PETR4",
      "quantidade": 500,
      "preco_medio": 28.50,
      "valor_atual": 15000,
      "rentabilidade": 12.5,
      "dividend_yield": 8.2
    },
    {
      "ativo": "VALE3",
      "quantidade": 300,
      "preco_medio": 54.20,
      "valor_atual": 16800,
      "rentabilidade": 3.2,
      "dividend_yield": 5.1
    },
    {
      "ativo": "AAPL",
      "quantidade": 50,
      "preco_medio": 155.30,
      "valor_atual": 8500,
      "rentabilidade": 45.8,
      "dividend_yield": 0.5
    }
  ],

  "proventos_recebidos": {
    "total": 12500.00,
    "dividendos": 10200.00,
    "jcp": 1800.00,
    "rendimentos": 500.00,
    "detalhes": [
      {
        "data": "2024-10-15",
        "ativo": "PETR4",
        "tipo": "DIVIDENDO",
        "valor_unitario": 1.25,
        "valor_total": 625.00
      },
      {
        "data": "2024-11-20",
        "ativo": "MXRF11",
        "tipo": "RENDIMENTO",
        "valor_unitario": 0.08,
        "valor_total": 240.00
      }
    ]
  },

  "evolucao_patrimonio": [
    { "data": "2024-10-01", "valor": 250000 },
    { "data": "2024-10-15", "valor": 255000 },
    { "data": "2024-11-01", "valor": 268000 },
    { "data": "2024-11-30", "valor": 275000 },
    { "data": "2024-12-07", "valor": 281500 }
  ]
}
```

---

## 🔔 EXEMPLO 2: ALERTA EM TEMPO REAL (WebSocket)

### Configuração: POST /api/alertas/criar
```json
{
  "usuario_id": "usr_12345",
  "nome": "PETR4 acima de 30 reais",
  "tipo_alerta": "ALTA_PRECO",
  "ativo_id": "avo_petr4",
  "portfolio_id": null,
  "condicao_operador": ">",
  "condicao_valor": 30.00,
  "condicao_valor2": null,
  "ativo": true,
  "frequencia_notificacao": "IMEDIATA",
  "canais_entrega": ["WEBAPP", "EMAIL"]
}
```

### Resposta: 201 Created
```json
{
  "id": "alt_xyz123",
  "usuario_id": "usr_12345",
  "nome": "PETR4 acima de 30 reais",
  "tipo_alerta": "ALTA_PRECO",
  "ativo_id": "avo_petr4",
  "condicao": "PETR4 > 30.00",
  "timestamp_criacao": "2024-12-07T10:00:00Z",
  "timestamp_ultimo_acionamento": null,
  "total_acionamentos": 0,
  "status": "ON"
}
```

### WebSocket: Alerta Acionado (Broadcast)
```javascript
// Servidor dispara quando PETR4 >= 30.00
{
  "tipo": "alerta_disparado",
  "alerta_id": "alt_xyz123",
  "usuario_id": "usr_12345",
  "nome": "PETR4 acima de 30 reais",
  "ativo": "PETR4",
  "preco_atual": 30.15,
  "preco_target": 30.00,
  "timestamp": "2024-12-07T14:35:22Z",
  "mensagem": "🔔 PETR4 atingiu R$ 30.15 (acima do alvo R$ 30.00)",
  "url": "/dashboard/ativos/petr4"
}

// Frontend: Toast Notification
{
  tipo: "success",
  titulo: "PETR4 acima de 30 reais",
  mensagem: "Preço atual: R$ 30.15",
  duracao: 5000,
  acoes: [
    { label: "Ver Ativo", onClick: () => navigate('/dashboard/ativos/petr4') }
  ]
}
```

---

## 📈 EXEMPLO 3: PROJEÇÃO RENDA PASSIVA (12 MESES)

### Entrada: GET /api/projecoes/renda?portfolio_id=prt_67890&cenario=BASE

### Saída: Response 200 OK
```json
{
  "portfolio_id": "prt_67890",
  "nome_portfolio": "XP Investimentos",
  "cenario": "BASE",
  "periodo": "2024-12 a 2025-11",

  "resumo": {
    "renda_total_12meses": 18500.00,
    "renda_media_mensal": 1541.67,
    "crescimento_projetado": 3.2,
    "ativos_contribuindo": 15
  },

  "projecoes_mensais": [
    {
      "mes": "2024-12",
      "dividendos": 850.00,
      "jcp": 150.00,
      "rendimentos": 45.00,
      "total_mes": 1045.00,
      "acumulado": 1045.00,
      "crescimento_percentual": 0.0
    },
    {
      "mes": "2025-01",
      "dividendos": 825.00,
      "jcp": 0.00,
      "rendimentos": 48.00,
      "total_mes": 873.00,
      "acumulado": 1918.00,
      "crescimento_percentual": -16.5
    },
    {
      "mes": "2025-02",
      "dividendos": 900.00,
      "jcp": 200.00,
      "rendimentos": 50.00,
      "total_mes": 1150.00,
      "acumulado": 3068.00,
      "crescimento_percentual": 31.7
    },
    {
      "mes": "2025-03",
      "dividendos": 950.00,
      "jcp": 0.00,
      "rendimentos": 52.00,
      "total_mes": 1002.00,
      "acumulado": 4070.00,
      "crescimento_percentual": -12.9
    }
  ],

  "cenarios": {
    "PESSIMISTA": {
      "renda_total": 15200.00,
      "media_mensal": 1266.67,
      "motivo": "-18% redução de dividendos, sem JCP"
    },
    "BASE": {
      "renda_total": 18500.00,
      "media_mensal": 1541.67,
      "motivo": "Histórico extrapolado com +3% crescimento"
    },
    "OTIMISTA": {
      "renda_total": 22400.00,
      "media_mensal": 1866.67,
      "motivo": "+21% aumento dividendos, dobragem de JCP"
    }
  },

  "contribuicao_por_ativo": [
    {
      "ativo": "PETR4",
      "tipo": "Ação",
      "dividendo_previsto": 5200.00,
      "jcp_previsto": 800.00,
      "total_contribuicao": 6000.00,
      "percentual_renda": 32.4
    },
    {
      "ativo": "MXRF11",
      "tipo": "FII",
      "dividendo_previsto": 0.00,
      "jcp_previsto": 0.00,
      "rendimento_previsto": 4200.00,
      "total_contribuicao": 4200.00,
      "percentual_renda": 22.7
    },
    {
      "ativo": "VALE3",
      "tipo": "Ação",
      "dividendo_previsto": 3800.00,
      "jcp_previsto": 1200.00,
      "total_contribuicao": 5000.00,
      "percentual_renda": 27.0
    }
  ]
}
```

---

## 📊 EXEMPLO 4: ANÁLISE DE PERFORMANCE (ÍNDICES)

### Entrada: GET /api/analises/performance?portfolio_id=prt_67890&data_inicio=2024-01-01&data_fim=2024-12-07

### Saída: Response 200 OK
```json
{
  "portfolio_id": "prt_67890",
  "periodo": "2024-01-01 a 2024-12-07",
  "dias_uteis": 241,

  "retornos": {
    "bruto_percentual": 26.5,
    "liquido_percentual": 24.8,
    "vs_ibovespa": "+8.3%",
    "vs_sp500": "+12.1%",
    "valor_inicial": 250000.00,
    "valor_final": 281500.00,
    "lucro_liquido": 31500.00
  },

  "volatilidade": {
    "percentual_anual": 18.3,
    "percentual_mensal": 5.2,
    "percentual_diaria": 1.1,
    "benchmark_ibovespa": 22.1,
    "benchmark_sp500": 18.8
  },

  "indices_risco_retorno": {
    "sharpe_ratio": 0.98,
    "benchmark_sharpe": 0.72,
    "sortino_ratio": 1.42,
    "calmar_ratio": 3.23,
    "informacao_ratio": 0.35
  },

  "drawdown": {
    "max_drawdown_percentual": -8.2,
    "periodo_max_drawdown": "2024-08-15 a 2024-09-10",
    "recuperacao_dias": 18,
    "media_drawdown": -3.5
  },

  "medidas_avancadas": {
    "irr_anual": 32.5,
    "beta_mercado": 1.05,
    "alfa_jensen": 2.3,
    "correlacao_ibovespa": 0.72,
    "correlacao_sp500": 0.58
  },

  "metricas_por_periodo": {
    "Q1_2024": { "retorno": 8.2, "volatilidade": 15.3, "sharpe": 0.54 },
    "Q2_2024": { "retorno": 5.1, "volatilidade": 12.1, "sharpe": 0.42 },
    "Q3_2024": { "retorno": 7.8, "volatilidade": 22.3, "sharpe": 0.35 },
    "Q4_2024": { "retorno": 5.4, "volatilidade": 16.2, "sharpe": 0.33 }
  }
}
```

---

## 🔗 EXEMPLO 5: EXPORTAÇÃO PDF

### Request: POST /api/relatorios/abc123/exportar
```json
{
  "formato": "PDF",
  "incluir_graficos": true,
  "incluir_tabelas": true,
  "confidencialidade": "PRIVADO"
}
```

### Response: Binary PDF
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="relatorio_perf_2024_12.pdf"
Content-Length: 258456

[Binary PDF Data...]

Estrutura do PDF:
1. CAPA
   └─ Logo Exitus + Data + Período

2. ÍNDICE
   └─ 4 seções

3. SEÇÃO 1: RESUMO EXECUTIVO
   └─ Tabela 4 colunas: Métrica | Valor | vs Benchmark | Status
   └─ Cards: Retorno | Sharpe | Drawdown | Volatilidade

4. SEÇÃO 2: GRÁFICOS
   └─ Evolução patrimonial (linha)
   └─ Alocação por classe (pie)
   └─ Alocação por país (pie)
   └─ Rentabilidade por ativo (bar)

5. SEÇÃO 3: TABELAS DETALHADAS
   └─ Tabela ativos: Ativo | Qtd | Preço | Valor | Rentab
   └─ Tabela proventos: Data | Ativo | Tipo | Valor

6. SEÇÃO 4: ANÁLISES
   └─ Índices financeiros (Sharpe, Sortino, IRR)
   └─ Comparação benchmarks

7. RODAPÉ
   └─ Data geração
   └─ "Documento confidencial"
   └─ Páginas
```

---

## 📊 EXEMPLO 6: EXPORTAÇÃO EXCEL

### Request: POST /api/relatorios/abc123/exportar
```json
{
  "formato": "EXCEL",
  "estrutura": "COMPLETA"
}
```

### Response: Binary XLSX
```
Arquivo: relatorio_perf_2024_12.xlsx

SHEETS:
1. "Resumo"
   ├─ Métrica (col A) | Valor (col B) | vs Benchmark (col C) | Interpretação (col D)
   ├─ Retorno Bruto | 26.5% | +8.3% vs IBOV | ✅ Acima da média
   ├─ Volatilidade | 18.3% | -3.8% vs IBOV | ✅ Menor risco
   ├─ Sharpe Ratio | 0.98 | +0.26 vs IBOV | ✅ Superior
   └─ ... (20+ métricas)

2. "Ativos"
   ├─ Ativo (A) | Qtd (B) | Preço Médio (C) | Valor Atual (D) | Rentab % (E) | Dividend Yield (F)
   ├─ PETR4 | 500 | R$ 28,50 | R$ 15.000,00 | 12,5% | 8,2%
   ├─ VALE3 | 300 | R$ 54,20 | R$ 16.800,00 | 3,2% | 5,1%
   ├─ AAPL | 50 | US$ 155,30 | R$ 8.500,00 | 45,8% | 0,5%
   └─ ... (TOTAL em bold)

3. "Proventos"
   ├─ Data (A) | Ativo (B) | Tipo (C) | Valor Unitário (D) | Qtd (E) | Valor Total (F)
   ├─ 2024-10-15 | PETR4 | Dividendo | R$ 1,25 | 500 | R$ 625,00
   ├─ 2024-11-20 | MXRF11 | Rendimento | R$ 0,08 | 3000 | R$ 240,00
   └─ ... (TOTAL em bold)

4. "Gráficos" (embedded charts)
   ├─ Chart 1: Evolução Patrimonial (Line)
   ├─ Chart 2: Alocação Classe (Pie)
   └─ Chart 3: Top Ativos (Bar)

5. "Cálculos"
   ├─ Fórmula Sharpe: (Retorno - TaxaLivre) / StdDev
   ├─ Fórmula IRR: TIR(Fluxos)
   └─ ... (documentação)

FORMATAÇÃO:
- Headers: Bold + Fundo azul + Texto branco
- Números: 2 casas decimais + separador milhar (R$ 1.234,56)
- Datas: DD/MM/YYYY (07/12/2024)
- Moedas: R$ ou US$ conforme coluna
- Totalizações: Bold + Fundo cinza
- Links: Blue + Underline
```

---

## 🎨 EXEMPLO 7: INTERFACE FRONTEND - RELATÓRIOS

### Página: /dashboard/relatorios

```
┌─────────────────────────────────────────────────────────────────┐
│ RELATÓRIOS E ANÁLISES AVANÇADAS                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ [+ Novo Relatório ▼]  [Filtros ▼]  🔍 Buscar...                │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ 📋 Relatórios Recentes (3)                                       │
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Data       │ Período      │ Portfolio    │ Retorno │ Ações  │ │
│ ├─────────────────────────────────────────────────────────────┤ │
│ │ 07/12/24   │ Out-Dez 2024 │ XP Invest.  │ +26,5%  │ ⋯ │ │ │
│ │ 05/12/24   │ Set-Nov 2024 │ Clear       │ +12,3%  │ ⋯ │ │ │
│ │ 01/12/24   │ Ago-Out 2024 │ Avenue      │ +18,7%  │ ⋯ │ │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ < 1 2 3 ... > (Paginação HTMX)                                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

Modal "Novo Relatório":
┌─────────────────────────────────────────────┐
│ ✕ Novo Relatório                            │
├─────────────────────────────────────────────┤
│                                              │
│ Portfolio *                                  │
│ [▼ Selecionar Portfolio]                    │
│                                              │
│ Data Início *                                │
│ [📅 01/10/2024]                              │
│                                              │
│ Data Fim *                                  │
│ [📅 31/12/2024]                              │
│                                              │
│ Filtros (opcional)                          │
│ ☐ Mercados:  ☐BR  ☐US  ☐EU                 │
│ ☐ Setores:   ☐Financeiro  ☐Tech ☐Energia  │
│ ☐ Classes:   ☐Ação ☐FII ☐ETF              │
│                                              │
│ Formato                                      │
│ ◉ Visualização  ◉ PDF  ◉ Excel              │
│                                              │
│        [Cancelar]  [Gerar Relatório]        │
│                                              │
└─────────────────────────────────────────────┘
```

---

## 🔔 EXEMPLO 8: INTERFACE FRONTEND - ALERTAS

### Página: /dashboard/alertas

```
┌─────────────────────────────────────────────────────────────────┐
│ ALERTAS E NOTIFICAÇÕES                                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ [+ Novo Alerta]  Ativos: [toggle]  Histórico  🔔 3 novos        │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Nome                   │ Tipo    │ Status │ Último │ Ações  │ │
│ ├─────────────────────────────────────────────────────────────┤ │
│ │ PETR4 > 30             │ Preço   │ 🟢 ON │ Hoje   │ ⋯      │ │
│ │ Div VALE3 Previsto     │ Renda   │ 🟢 ON │ -      │ ⋯      │ │
│ │ Portfolio Volatil +20% │ Risco   │ 🔴OFF │ 2d atrás│ ⋯      │ │
│ │ MXRF11 Rendimento < 7% │ Renda   │ 🟢 ON │ 5h atrás│ ⋯      │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ Notificações Recentes:                                           │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 🔔 PETR4 atingiu R$ 30,15 (acima do alvo R$ 30,00)          │ │
│ │    Hoje às 14:35  [Ver Ativo]                               │ │
│ ├─────────────────────────────────────────────────────────────┤ │
│ │ 🔔 Dividendo VALE3 confirmado: R$ 2,45 por ação             │ │
│ │    Ontem às 10:20  [Ver Proventos]                          │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

Modal "Novo Alerta":
┌──────────────────────────────────────────────────┐
│ ✕ Novo Alerta                                    │
├──────────────────────────────────────────────────┤
│                                                  │
│ Nome do Alerta *                                 │
│ [Alerta PETR4 > 30]                              │
│                                                  │
│ Tipo *                                           │
│ [▼ ALTA_PRECO]                                   │
│                                                  │
│ Ativo Alvo *                                     │
│ [🔍 PETR4            ]                            │
│                                                  │
│ Condição *                                       │
│ [ > ]  Valor: [30.00]  [ Valor2: ]              │
│                                                  │
│ Frequência                                       │
│ ◉ IMEDIATA  ◉ DIÁRIA  ◉ SEMANAL  ◉ MENSAL       │
│                                                  │
│ Canais de Entrega                                │
│ ☑ Web App  ☐ Email  ☐ SMS  ☐ Telegram           │
│                                                  │
│      [Cancelar]  [Testar]  [Criar Alerta]      │
│                                                  │
└──────────────────────────────────────────────────┘
```

---

## 📈 EXEMPLO 9: MATRIZ DE CORRELAÇÃO

### GET /api/analises/correlacao?portfolio_id=prt_67890

```json
{
  "portfolio_id": "prt_67890",
  "periodo_calculo": "90 dias",
  "timestamp": "2024-12-07T15:30:00Z",

  "matriz_correlacao": [
    ["Ativo", "PETR4", "VALE3", "AAPL", "MXRF11", "IBOVESPA"],
    ["PETR4", 1.00, 0.72, 0.35, -0.12, 0.95],
    ["VALE3", 0.72, 1.00, 0.28, -0.05, 0.88],
    ["AAPL", 0.35, 0.28, 1.00, 0.45, 0.58],
    ["MXRF11", -0.12, -0.05, 0.45, 1.00, 0.32],
    ["IBOVESPA", 0.95, 0.88, 0.58, 0.32, 1.00]
  ],

  "interpretacao": {
    "altamente_correlacionados": [
      {
        "ativo1": "PETR4",
        "ativo2": "IBOVESPA",
        "correlacao": 0.95,
        "implicacao": "Risco sistemático alto, pouca diversificação"
      }
    ],
    "descorrelacionados": [
      {
        "ativo1": "PETR4",
        "ativo2": "MXRF11",
        "correlacao": -0.12,
        "implicacao": "Diversificação excelente"
      }
    ]
  }
}
```

---

*Documento de exemplos prático | 07/12/2025 18:15 | Referência para implementação*
