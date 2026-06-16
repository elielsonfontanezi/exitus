# EXITUS-EXPORT-001 — Exportação Genérica de Dados

> **Status:** ✅ Concluído (03/03/2026)  
> **Versão:** 1.0  
> **Branch:** `feature/revisao-negocio-vision`  
> **Testes:** 32 testes de integração — 100% passou

---

## 1. Objetivo

Permitir que o usuário exporte seus dados de investimento em múltiplos formatos (CSV, Excel, JSON, PDF) para análise externa, declaração de IR, planilhas pessoais ou integração com outras ferramentas. Antes deste GAP, o sistema possuía apenas importação (B3) mas nenhuma saída de dados estruturada.

---

## 2. Escopo Implementado

### 2.1 Entidades exportáveis

| Entidade | Dados incluídos | Filtros suportados |
|----------|----------------|-------------------|
| `transacoes` | data, tipo, ticker, ativo, corretora, quantidade, preço unitário, valor total, custos, valor líquido, observações | `data_inicio`, `data_fim`, `ativo_id`, `corretora_id`, `tipo` |
| `proventos` | data pagamento, data com, tipo, ticker, ativo, quantidade, valor/ação, bruto, imposto retido, líquido | `data_inicio`, `data_fim`, `ativo_id`, `tipo` |
| `posicoes` | ticker, nome, tipo, quantidade, preço médio, preço atual, valor investido, valor atual, lucro/prejuízo, rentabilidade % | `ativo_id` |

### 2.2 Formatos disponíveis

| Formato | Content-Type | Extensão | Características |
|---------|-------------|----------|----------------|
| `json` | `application/json` | `.json` | Envelope `{meta, dados, total}` com metadados completos |
| `csv` | `text/csv; charset=utf-8` | `.csv` | Cabeçalho de metadados `#`, separador `;`, encoding UTF-8-BOM |
| `excel` | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` | `.xlsx` | Título + metadados nas primeiras linhas, cabeçalho azul escuro, auto-ajuste de colunas |
| `pdf` | `application/pdf` | `.pdf` | Layout A4 landscape, tabela zebra-stripe, título e metadados |

### 2.3 Limites e defaults

- **Limite de registros:** 10.000 por exportação (`LIMITE_REGISTROS`)
- **Formato default:** `json` (quando `?formato=` não é informado)
- **Ordenação:** sempre decrescente por data (`data_transacao.desc()` / `data_pagamento.desc()`)
- **Filename gerado automaticamente:** `exitus_{entidade}_{YYYYMMDD_HHMM}.{ext}`

---

## 3. Arquitetura

### 3.1 Arquivos

| Arquivo | Responsabilidade |
|---------|-----------------|
| `backend/app/services/export_service.py` | Engine: queries, renderers, entry point `ExportService.exportar()` |
| `backend/app/blueprints/export_blueprint.py` | 3 endpoints REST em `/api/export/` |
| `backend/tests/test_export_integration.py` | Suite de 32 testes de integração |

### 3.2 Diagrama de fluxo — `ExportService.exportar()`

```
exportar(usuario_id, entidade, formato, params)
│
├── 1. Valida entidade (transacoes | proventos | posicoes)
├── 2. Valida formato (csv | excel | json | pdf)
├── 3. Processa filtros de data e IDs
│
├── 4. Executa query da entidade:
│       ├── _query_transacoes()  → JOIN Ativo + Corretora
│       ├── _query_proventos()   → filtra via subquery de ativos do usuário
│       └── _query_posicoes()    → delega para PortfolioService.get_portfolio_metrics()
│
├── 5. Monta metadados (entidade, formato, gerado_em, filtros, usuario_id)
│
├── 6. Renderiza no formato:
│       ├── _render_json()   → json.dumps com ensure_ascii=False
│       ├── _render_csv()    → csv.DictWriter, separador ';', UTF-8-BOM
│       ├── _render_excel()  → openpyxl com estilos
│       └── _render_pdf()    → reportlab A4 landscape
│
└── 7. Retorna (conteudo_bytes, content_type, filename)
```

### 3.3 Padrão de resposta HTTP

Os endpoints de exportação **não** usam o envelope padrão `{"success": true, "data": ...}`. Retornam diretamente o arquivo como download com:

```
HTTP 200
Content-Type: <mime_type>
Content-Disposition: attachment; filename="exitus_transacoes_20250303_1800.csv"
X-Total-Records: <tamanho_em_bytes>
```

Erros (`422`, `500`) continuam usando o envelope padrão `{"success": false, "message": "..."}`.

### 3.4 Isolamento multi-tenant em proventos

A tabela `provento` não possui `usuario_id` diretamente. O filtro de isolamento é feito via subquery:

```python
ativos_do_usuario = (
    db.session.query(Transacao.ativo_id)
    .filter(Transacao.usuario_id == usuario_id)
    .distinct()
    .subquery()
)
Provento.query.filter(Provento.ativo_id.in_(ativos_do_usuario))
```

> **Decisão de design:** proventos são dados públicos do ativo (PETR4 paga dividendo para todos os holders). O isolamento por usuário é feito via ativos que o usuário transacionou — correto semanticamente.

### 3.5 Dependências de bibliotecas

| Biblioteca | Uso | Instalação |
|-----------|-----|-----------|
| `openpyxl` | Geração de arquivos Excel (`.xlsx`) | `pip install openpyxl` |
| `reportlab` | Geração de arquivos PDF | `pip install reportlab` |
| `csv` | Geração de CSV | Stdlib Python |
| `json` | Geração de JSON | Stdlib Python |

> `openpyxl` e `reportlab` são importados de forma lazy (dentro da função `_render_*`) para não impactar o tempo de startup da aplicação.

---

## 4. API Reference

### 4.1 Parâmetros comuns

Todos os endpoints aceitam os mesmos parâmetros opcionais:

| Parâmetro | Tipo | Formato | Descrição |
|-----------|------|---------|-----------|
| `formato` | string | `csv\|excel\|json\|pdf` | Formato de saída. Default: `json` |
| `data_inicio` | string | `YYYY-MM-DD` | Filtro de data inicial |
| `data_fim` | string | `YYYY-MM-DD` | Filtro de data final |
| `ativo_id` | UUID | — | Filtrar por ativo específico |
| `corretora_id` | UUID | — | Filtrar por corretora (apenas transações) |
| `tipo` | string | enum | Filtrar por tipo (depende da entidade) |

**Erros comuns:**

| HTTP | Situação |
|------|----------|
| 400 | Erro interno inesperado |
| 401 | Token JWT ausente ou inválido |
| 422 | Formato inválido, data com formato errado, tipo inválido |
| 500 | Erro interno (biblioteca de render, query, etc.) |

---

### 4.2 `GET /api/export/transacoes`

Exporta transações do usuário (compras, vendas, dividendos, etc.).

**Filtro `tipo` — valores válidos:** `compra`, `venda`, `dividendo`, `jcp`, `amortizacao`, `bonificacao`, `subscricao`, `desdobramento`, `grupamento`

**Colunas exportadas:**

| Campo | Descrição |
|-------|-----------|
| `id` | UUID da transação |
| `data` | Data no formato `DD/MM/YYYY` |
| `tipo` | Tipo da operação |
| `ticker` | Ticker do ativo |
| `ativo` | Nome completo do ativo |
| `corretora` | Nome da corretora |
| `quantidade` | Quantidade de ativos |
| `preco_unitario` | Preço por unidade |
| `valor_total` | Valor bruto total |
| `custos_totais` | Taxas + corretagem + emolumentos |
| `valor_liquido` | Valor total ± custos |
| `observacoes` | Observações livres |

**Exemplo JSON:**
```json
{
  "meta": {
    "entidade": "transacoes",
    "formato": "json",
    "gerado_em": "03/03/2026 18:00",
    "filtros": {"data_inicio": "2025-01-01"},
    "usuario_id": "uuid"
  },
  "dados": [
    {
      "id": "uuid",
      "data": "20/03/2025",
      "tipo": "venda",
      "ticker": "PETR4",
      "ativo": "Petrobras PN",
      "corretora": "XP Investimentos",
      "quantidade": 100.0,
      "preco_unitario": 35.50,
      "valor_total": 3550.0,
      "custos_totais": 12.30,
      "valor_liquido": 3537.70,
      "observacoes": ""
    }
  ],
  "total": 1
}
```

---

### 4.3 `GET /api/export/proventos`

Exporta proventos recebidos (dividendos, JCP, aluguéis, amortizações).

**Filtro `tipo` — valores válidos:** `dividendo`, `jcp`, `rendimento`, `amortizacao`, `aluguel`, `outro`

**Colunas exportadas:**

| Campo | Descrição |
|-------|-----------|
| `id` | UUID do provento |
| `data_pagamento` | Data de pagamento (`DD/MM/YYYY`) |
| `data_com` | Data com (`DD/MM/YYYY`) |
| `tipo` | Tipo do provento |
| `ticker` | Ticker do ativo |
| `ativo` | Nome completo do ativo |
| `quantidade` | Quantidade de ativos na data com |
| `valor_por_acao` | Valor do provento por ativo |
| `valor_bruto` | Total bruto recebido |
| `imposto_retido` | IR retido na fonte (JCP: 15%) |
| `valor_liquido` | Líquido após IR |

---

### 4.4 `GET /api/export/posicoes`

Exporta a posição consolidada atual do portfólio.

> **Atenção:** posições são calculadas em tempo real via `PortfolioService.get_portfolio_metrics()`. Não há filtros de data (posição é um snapshot atual). Somente `ativo_id` é suportado.

**Colunas exportadas:**

| Campo | Descrição |
|-------|-----------|
| `ticker` | Ticker do ativo |
| `nome` | Nome completo |
| `tipo` | Tipo do ativo |
| `quantidade` | Quantidade atual |
| `preco_medio` | Preço médio de aquisição |
| `preco_atual` | Preço atual de mercado |
| `valor_investido` | `quantidade × preco_medio` |
| `valor_atual` | `quantidade × preco_atual` |
| `lucro_prejuizo` | `valor_atual − valor_investido` |
| `rentabilidade_pct` | Rentabilidade em % |

---

## 5. Testes

Suite em `backend/tests/test_export_integration.py` — 32 testes, 100% passou.

| Classe | Testes | O que cobre |
|--------|--------|-------------|
| `TestExportTransacoes` | 17 | 401 sem token; 4 formatos (JSON/CSV/Excel/PDF) retornam 200 + content-type correto; formato inválido → 422; estrutura JSON (`meta`, `dados`, `total`); campos obrigatórios no `meta`; `Content-Disposition` com filename; filtros de data (válido/inválido); filtro `tipo` (válido/inválido); CSV tem cabeçalho `# Exitus`; PDF inicia com `%PDF`; Excel não vazio; default `json` sem parâmetro |
| `TestExportProventos` | 7 | 401 sem token; 4 formatos; entidade correta no `meta`; `Content-Disposition` com filename |
| `TestExportPosicoes` | 8 | 401 sem token; 4 formatos; entidade correta no `meta`; formato inválido → 422 |

---

## 6. Características por formato

### 6.1 JSON
```json
{
  "meta": { "entidade": "...", "formato": "json", "gerado_em": "DD/MM/YYYY HH:MM", "filtros": {}, "usuario_id": "uuid" },
  "dados": [ { ... } ],
  "total": 42
}
```

### 6.2 CSV
```
# Exitus — Transacoes
# Gerado em: 03/03/2026 18:00
# Total de registros: 42
# Filtros: {}
id;data;tipo;ticker;ativo;corretora;...
uuid;20/03/2025;venda;PETR4;Petrobras PN;XP;...
```
- Separador: `;` (compatível com Excel BR por padrão)
- Encoding: `UTF-8-BOM` (Excel abre corretamente sem configuração extra)
- Valores monetários: `1.234,56` (vírgula decimal, padrão BR)

### 6.3 Excel (`.xlsx`)
- Linha 1: título em bold `"Exitus — Transacoes"` (fonte 13pt)
- Linha 2: metadados em itálico cinza
- Linha 3: vazia
- Linha 4: cabeçalho das colunas (fundo azul escuro `#1F4E79`, texto branco, bold)
- Linhas 5+: dados
- Auto-ajuste de largura de colunas (máx. 40 caracteres)

### 6.4 PDF
- Orientação: A4 landscape (paisagem)
- Margens: 1,5cm laterais, 2cm topo, 1,5cm base
- Cabeçalho: título em bold + linha de metadados
- Tabela: cabeçalho azul escuro, zebra-stripe (`branco` / `#EBF0FA`), bordas `#CCCCCC`
- Fontes: Helvetica-Bold 8pt no cabeçalho, Helvetica 7pt nos dados
- `repeatRows=1`: cabeçalho repetido em cada página

---

## 7. Limitações e GAPs derivados

### 7.1 Sem exportação de relatórios customizados

O endpoint `GET /api/export/relatorio/{id}` previsto no escopo original não foi implementado. Relatórios gerados pelo `RelatorioService` não são exportáveis diretamente. GAP futuro: **EXITUS-EXPORT-002**.

### 7.2 Posições sem filtro de data histórica

A exportação de posições reflete o estado atual calculado pelo `PortfolioService`. Não é possível exportar a posição de uma data passada (ex: posição em 31/12/2024 para DIRPF). Esse cenário depende de `EXITUS-IR-006` (DIRPF anual).

### 7.3 Limite fixo de 10.000 registros

O limite é hardcoded em `LIMITE_REGISTROS = 10_000`. Para usuários com histórico muito longo, pode ser necessário exportar com filtros de data. Futuramente: paginação ou streaming.

### 7.4 Sem agendamento / exportação automática

Não há endpoint para agendar exportações periódicas (ex: exportar CSV de proventos toda sexta). Dependeria de `EXITUS-MONITOR-001` (Fase 5).

---

## 8. Dependências de instalação

Verificar que `openpyxl` e `reportlab` estão no `requirements.txt` do backend:

```bash
# Dentro do container
podman exec exitus-backend pip list | grep -E 'openpyxl|reportlab'
```

---

## 9. Exemplos de uso (cURL)

```bash
# Obter token
TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "joao.silva", "password": "senha123"}' \
  | jq -r '.data.access_token')

# Exportar transações em CSV (período 2025)
curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:5000/api/export/transacoes?formato=csv&data_inicio=2025-01-01&data_fim=2025-12-31" \
  -o transacoes_2025.csv

# Exportar proventos em Excel
curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:5000/api/export/proventos?formato=excel" \
  -o proventos.xlsx

# Exportar posições em PDF
curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:5000/api/export/posicoes?formato=pdf" \
  -o posicoes.pdf

# Exportar só compras de PETR4 em JSON
curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:5000/api/export/transacoes?formato=json&tipo=compra" \
  | jq '.dados[] | select(.ticker == "PETR4")'
```

---

## 10. Histórico de revisões

| Data | Versão | Alteração |
|------|--------|-----------|
| 03/03/2026 | 1.0 | Implementação inicial — engine, 3 endpoints, 32 testes |

---

*GAPs derivados: EXITUS-EXPORT-002 (relatórios customizados), integração com EXITUS-IR-006 (DIRPF anual).*
