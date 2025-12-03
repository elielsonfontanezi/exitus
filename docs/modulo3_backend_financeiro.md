# MÓDULO 3 - DOCUMENTAÇÃO TÉCNICA COMPLETA

**Sistema Exitus - Entidades Financeiras Avançadas + Portfolio Analytics**

---

## 📑 ÍNDICE

1. [Visão Geral](#visão-geral)
2. [Arquitetura](#arquitetura)
3. [Fase 3.1 - Posições](#fase-31---posições)
4. [Fase 3.2 - Proventos](#fase-32---proventos)
5. [Fase 3.3 - Movimentação de Caixa](#fase-33---movimentação-de-caixa)
6. [Fase 3.4 - Eventos Corporativos](#fase-34---eventos-corporativos)
7. [Fase 3.5 - Portfolio Analytics](#fase-35---portfolio-analytics)
8. [Integrações](#integrações)
9. [Exemplos de Uso](#exemplos-de-uso)
10. [Troubleshooting](#troubleshooting)

---

## VISÃO GERAL

O Módulo 3 implementa as funcionalidades avançadas de gestão financeira do Exitus:

### Objetivos
- Calcular e gerenciar posições de investimento (holdings)
- Controlar proventos recebidos (dividendos, JCP, etc)
- Gerenciar movimentações de caixa entre corretoras
- Rastrear eventos corporativos (splits, bonificações, etc)
- Fornecer analytics avançados de portfólio

### Tecnologias
- **Backend:** Flask + SQLAlchemy
- **Validação:** Marshmallow
- **Autenticação:** JWT
- **Banco de Dados:** PostgreSQL
- **Decimal:** Precisão em cálculos financeiros

---

## ARQUITETURA

### Camadas da Aplicação

```
┌─────────────────────────────────────────┐
│           API REST (Flask)              │
│  Blueprints: posicao, provento, etc.    │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│      Schemas (Marshmallow)              │
│  Validação e Serialização               │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Services (Lógica)               │
│  Cálculos financeiros e regras          │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│       Models (SQLAlchemy)               │
│  Posicao, Provento, MovimentacaoCaixa   │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│      Banco de Dados (PostgreSQL)        │
└─────────────────────────────────────────┘
```

### Fluxo de Dados

1. **Transações** → Geram **Posições**
2. **Posições** + **Preços Atuais** → Calculam **Lucro/Prejuízo**
3. **Proventos** + **Posições** → Calculam **Proventos Recebidos**
4. **Movimentações** → Atualizam **Saldo das Corretoras**
5. **Eventos Corporativos** → Ajustam **Posições**
6. **Tudo** → Alimenta **Portfolio Analytics**

---

## FASE 3.1 - POSIÇÕES

### Conceito

Posições representam os **holdings** do usuário - quanto de cada ativo ele possui em cada corretora.

### Model: Posicao

```python
class Posicao(db.Model):
    id = UUID (PK)
    usuario_id = UUID (FK → Usuario)
    ativo_id = UUID (FK → Ativo)
    corretora_id = UUID (FK → Corretora)

    quantidade = Decimal          # Quantidade de ativos
    preco_medio = Decimal          # Preço médio de compra
    custo_total = Decimal          # Investimento total

    taxas_acumuladas = Decimal
    impostos_acumulados = Decimal

    valor_atual = Decimal          # Valor de mercado
    lucro_prejuizo_realizado = Decimal
    lucro_prejuizo_nao_realizado = Decimal

    data_primeira_compra = Date
    data_ultima_atualizacao = DateTime
```

### Cálculos Principais

#### 1. Preço Médio Ponderado

```python
preco_medio = custo_total / quantidade
```

**Exemplo:**
- Compra 1: 10 ações a R$ 20,00 = R$ 200,00
- Compra 2: 5 ações a R$ 25,00 = R$ 125,00
- **Total:** 15 ações custando R$ 325,00
- **Preço Médio:** R$ 325,00 / 15 = R$ 21,67

#### 2. Lucro/Prejuízo Não Realizado

```python
lucro_nao_realizado = (preco_atual * quantidade) - custo_total
```

**Exemplo:**
- Quantidade: 15 ações
- Preço Médio: R$ 21,67
- Preço Atual: R$ 30,00
- Valor Atual: 15 × R$ 30,00 = R$ 450,00
- Custo Total: R$ 325,00
- **Lucro Não Realizado:** R$ 450,00 - R$ 325,00 = R$ 125,00

#### 3. Lucro/Prejuízo Realizado (Venda)

```python
lucro_realizado = (preco_venda * quantidade_vendida) - (preco_medio * quantidade_vendida)
```

**Exemplo:**
- Venda: 5 ações a R$ 35,00 = R$ 175,00
- Custo dessas 5: 5 × R$ 21,67 = R$ 108,35
- **Lucro Realizado:** R$ 175,00 - R$ 108,35 = R$ 66,65

### Endpoints

#### GET /api/posicoes
Lista posições do usuário

**Query Params:**
- `page` (int): Página
- `per_page` (int): Itens por página
- `ativo_id` (UUID): Filtrar por ativo
- `corretora_id` (UUID): Filtrar por corretora
- `ticker` (str): Buscar por ticker
- `lucro_positivo` (bool): Apenas lucros

**Resposta:**
```json
{
  "success": true,
  "data": {
    "posicoes": [...],
    "total": 10,
    "page": 1,
    "pages": 2
  }
}
```

#### POST /api/posicoes/calcular
Recalcula todas as posições a partir das transações

**Resposta:**
```json
{
  "success": true,
  "data": {
    "posicoes_criadas": 3,
    "posicoes_atualizadas": 5,
    "posicoes_zeradas": 1
  }
}
```

#### GET /api/posicoes/resumo
Resumo consolidado do portfólio

**Resposta:**
```json
{
  "success": true,
  "data": {
    "quantidade_posicoes": 8,
    "total_investido": 50000.00,
    "total_valor_atual": 62000.00,
    "total_lucro_realizado": 3500.00,
    "total_lucro_nao_realizado": 12000.00,
    "lucro_total": 15500.00,
    "roi_percentual": 31.0
  }
}
```

---

## FASE 3.2 - PROVENTOS

### Conceito

Proventos são pagamentos feitos pelas empresas aos acionistas (dividendos, JCP, rendimentos).

### Model: Provento

```python
class Provento(db.Model):
    id = UUID (PK)
    ativo_id = UUID (FK → Ativo)

    tipo_provento = Enum          # dividendo, jcp, rendimento, bonificacao
    valor_por_acao = Decimal
    quantidade_ativos = Decimal

    valor_bruto = Decimal
    imposto_retido = Decimal
    valor_liquido = Decimal

    data_com = Date               # Data COM (para ter direito)
    data_pagamento = Date
    observacoes = Text
```

### Tipos de Provento

1. **Dividendo:** Distribuição de lucros (isento IR)
2. **JCP:** Juros sobre Capital Próprio (15% IR)
3. **Rendimento:** Rendimento de FIIs (isento IR)
4. **Bonificação:** Novas ações grátis
5. **Direito:** Direito de subscrição

### Cálculos

#### Provento Recebido por Usuário

```python
valor_recebido = valor_por_acao × quantidade_possuida
```

**Exemplo:**
- Provento: R$ 0,50 por ação
- Posição do usuário: 100 ações
- **Valor Bruto:** R$ 0,50 × 100 = R$ 50,00
- Se JCP (15% IR): **Valor Líquido:** R$ 50,00 × 0,85 = R$ 42,50

### Endpoints

#### GET /api/proventos
Lista proventos disponíveis

#### GET /api/proventos/recebidos
Lista proventos que o usuário recebeu

**Query Params:**
- `data_inicio` (YYYY-MM-DD)
- `data_fim` (YYYY-MM-DD)

**Resposta:**
```json
{
  "success": true,
  "data": {
    "proventos": [
      {
        "ativo": {"ticker": "PETR4", "nome": "Petrobras"},
        "tipo_provento": "dividendo",
        "valor_por_acao": "0.50",
        "quantidade_recebida": 100,
        "valor_bruto_recebido": 50.00,
        "valor_liquido_recebido": 50.00
      }
    ]
  }
}
```

#### GET /api/proventos/total-recebido
Total de proventos recebidos

**Resposta:**
```json
{
  "success": true,
  "data": {
    "total_geral_bruto": 5000.00,
    "total_geral_liquido": 4750.00,
    "por_tipo": {
      "dividendo": {
        "quantidade": 12,
        "valor_bruto": 3000.00,
        "valor_liquido": 3000.00
      },
      "jcp": {
        "quantidade": 5,
        "valor_bruto": 2000.00,
        "valor_liquido": 1700.00
      }
    }
  }
}
```

---

## FASE 3.3 - MOVIMENTAÇÃO DE CAIXA

### Conceito

Controla entrada e saída de dinheiro das corretoras (depósitos, saques, transferências).

### Model: MovimentacaoCaixa

```python
class MovimentacaoCaixa(db.Model):
    id = UUID (PK)
    usuario_id = UUID (FK → Usuario)
    corretora_id = UUID (FK → Corretora)
    corretora_destino_id = UUID (FK → Corretora, optional)
    provento_id = UUID (FK → Provento, optional)

    tipo_movimentacao = Enum      # deposito, saque, transferencia, etc
    valor = Decimal
    moeda = String                # BRL, USD, EUR

    data_movimentacao = Date
    descricao = Text
    comprovante = String (URL)
```

### Tipos de Movimentação

1. **DEPOSITO:** Entrada de dinheiro (+)
2. **SAQUE:** Saída de dinheiro (-)
3. **TRANSFERENCIA_ENVIADA:** Envio para outra corretora (-)
4. **TRANSFERENCIA_RECEBIDA:** Recebimento de outra corretora (+)
5. **CREDITO_PROVENTO:** Recebimento de provento (+)
6. **PAGAMENTO_TAXA:** Pagamento de taxa (-)
7. **PAGAMENTO_IMPOSTO:** Pagamento de imposto (-)

### Impacto no Saldo

```python
@property
def impacto_saldo(self):
    if tipo in ['deposito', 'transferencia_recebida', 'credito_provento']:
        return +valor
    else:
        return -valor
```

### Endpoints

#### POST /api/movimentacoes-caixa
Criar movimentação

**Body:**
```json
{
  "corretora_id": "uuid",
  "tipo_movimentacao": "deposito",
  "valor": "1000.00",
  "moeda": "BRL",
  "data_movimentacao": "2025-12-02",
  "descricao": "Aporte mensal"
}
```

#### GET /api/movimentacoes-caixa/saldo/{corretora_id}
Saldo consolidado da corretora

**Resposta:**
```json
{
  "success": true,
  "data": {
    "saldos": {
      "BRL": 15000.00,
      "USD": 500.00
    }
  }
}
```

#### GET /api/movimentacoes-caixa/extrato
Extrato de movimentações

**Query Params:**
- `corretora_id` (UUID)
- `data_inicio` (YYYY-MM-DD)
- `data_fim` (YYYY-MM-DD)

**Resposta:**
```json
{
  "success": true,
  "data": {
    "extrato": [
      {
        "data": "2025-12-01",
        "tipo": "deposito",
        "valor": 1000.00,
        "impacto": 1000.00,
        "saldo_acumulado": 1000.00
      },
      {
        "data": "2025-12-02",
        "tipo": "saque",
        "valor": 200.00,
        "impacto": -200.00,
        "saldo_acumulado": 800.00
      }
    ]
  }
}
```

---

## FASE 3.4 - EVENTOS CORPORATIVOS

### Conceito

Eventos corporativos são ações das empresas que afetam as ações (splits, bonificações, fusões).

### Model: EventoCorporativo

```python
class EventoCorporativo(db.Model):
    id = UUID (PK)
    ativo_id = UUID (FK → Ativo)

    tipo_evento = Enum            # desdobramento, grupamento, etc
    descricao = Text

    data_anuncio = Date
    data_com = Date
    data_aprovacao = Date
    data_execucao = Date

    proporcao = String            # Ex: "2:1", "1:10"
    preco_subscricao = Decimal

    observacoes = Text
    url_informacao = String
```

### Tipos de Evento

1. **DESDOBRAMENTO (Split):** 1 ação vira N ações
2. **GRUPAMENTO (Reverse Split):** N ações viram 1 ação
3. **BONIFICACAO:** Novas ações grátis
4. **SUBSCRICAO:** Direito de comprar novas ações
5. **INCORPORACAO:** Empresa A incorpora empresa B
6. **CISAO:** Empresa se divide em duas
7. **FUSAO:** Duas empresas se fundem
8. **MUDANCA_TICKER:** Mudança de código de negociação

### Cálculo de Impacto

#### Desdobramento (Split 2:1)

```python
nova_quantidade = quantidade_antiga × 2
novo_preco_medio = preco_medio_antigo / 2
```

**Exemplo:**
- Antes: 100 ações a R$ 50,00
- Após split 2:1: 200 ações a R$ 25,00
- **Custo total permanece:** R$ 5.000,00

#### Grupamento (1:10)

```python
nova_quantidade = quantidade_antiga / 10
novo_preco_medio = preco_medio_antigo × 10
```

**Exemplo:**
- Antes: 1.000 ações a R$ 1,00
- Após grupamento 1:10: 100 ações a R$ 10,00
- **Custo total permanece:** R$ 1.000,00

### Endpoints

#### GET /api/eventos-corporativos/meus-eventos
Eventos que afetam o usuário

**Resposta:**
```json
{
  "success": true,
  "data": {
    "eventos": [
      {
        "ativo": {"ticker": "PETR4"},
        "tipo_evento": "desdobramento",
        "data_anuncio": "2025-11-15",
        "proporcao": "2:1",
        "quantidade_afetada": 100,
        "impacto_estimado": {
          "tipo": "aumento_quantidade",
          "nova_quantidade": 200,
          "diferenca": 100
        }
      }
    ]
  }
}
```

#### POST /api/eventos-corporativos/{id}/aplicar-split
Aplicar desdobramento/grupamento

**Resposta:**
```json
{
  "success": true,
  "data": {
    "posicoes_afetadas": 3,
    "tipo_evento": "desdobramento",
    "proporcao": "2:1"
  },
  "message": "Evento aplicado a 3 posições"
}
```

---

## FASE 3.5 - PORTFOLIO ANALYTICS

### Conceito

Analytics avançados para análise de performance e risco do portfólio.

### Métricas Principais

#### 1. ROI (Return on Investment)

```python
roi = (lucro_total / investimento_total) × 100
```

#### 2. HHI (Índice Herfindahl-Hirschman)

Mede concentração do portfólio:

```python
hhi = Σ (percentual_ativo²)
```

**Classificação:**
- HHI < 1500: Baixa concentração ✅
- 1500 ≤ HHI < 2500: Concentração moderada ⚠️
- HHI ≥ 2500: Alta concentração ❌

**Exemplo:**
- Ativo A: 40% → 40² = 1600
- Ativo B: 30% → 30² = 900
- Ativo C: 20% → 20² = 400
- Ativo D: 10% → 10² = 100
- **HHI:** 1600 + 900 + 400 + 100 = 3000 (Alta concentração)

#### 3. Diversificação

- **Ideal:** 5-10 ativos diferentes
- **Bom:** 10-20 ativos
- **Muito diversificado:** >20 ativos

### Endpoints

#### GET /api/portfolio/dashboard
Dashboard completo

**Resposta:**
```json
{
  "success": true,
  "data": {
    "resumo_geral": {
      "total_investido": 50000.00,
      "valor_atual": 62000.00,
      "lucro_total": 12000.00,
      "roi_percentual": 24.0
    },
    "proventos": {...},
    "distribuicao_classes": {...},
    "top_posicoes": [...]
  }
}
```

#### GET /api/portfolio/distribuicao/classes
Distribuição por classe

**Resposta:**
```json
{
  "success": true,
  "data": {
    "acao": {
      "valor": 40000.00,
      "percentual": 64.5,
      "quantidade_ativos": 10
    },
    "fii": {
      "valor": 15000.00,
      "percentual": 24.2,
      "quantidade_ativos": 5
    },
    "renda_fixa": {
      "valor": 7000.00,
      "percentual": 11.3,
      "quantidade_ativos": 3
    }
  }
}
```

#### GET /api/portfolio/metricas-risco
Métricas de risco

**Resposta:**
```json
{
  "success": true,
  "data": {
    "quantidade_ativos": 18,
    "maior_posicao": {
      "ticker": "PETR4",
      "percentual": 15.5
    },
    "hhi": 1250.5,
    "nivel_concentracao": "Baixa",
    "recomendacao": ["Portfólio com boa diversificação"]
  }
}
```

#### GET /api/portfolio/performance
Performance dos ativos

**Resposta:**
```json
{
  "success": true,
  "data": {
    "ativos": [
      {
        "ticker": "PETR4",
        "quantidade": 100,
        "preco_medio": 25.50,
        "preco_atual": 35.00,
        "custo_total": 2550.00,
        "valor_atual": 3500.00,
        "lucro_prejuizo": 950.00,
        "roi_percentual": 37.25
      }
    ]
  }
}
```

---

## INTEGRAÇÕES

### Fluxo Completo

```
1. Usuário cria TRANSACAO (compra/venda)
   ↓
2. Sistema calcula POSICAO automaticamente
   ↓
3. Proventos são lançados (ADMIN)
   ↓
4. Sistema calcula proventos RECEBIDOS baseado em POSICAO
   ↓
5. Proventos geram MOVIMENTACAO_CAIXA (crédito)
   ↓
6. Eventos corporativos ajustam POSICAO
   ↓
7. PORTFOLIO_ANALYTICS consolida tudo
```

### Dependências entre Módulos

```
Posicao ← depende de → Transacao (Módulo 2)
Provento → calcula com → Posicao
MovimentacaoCaixa ← referencia → Provento
EventoCorporativo → modifica → Posicao
Portfolio → agrega → Todos os acima
```

---

## EXEMPLOS DE USO

### Exemplo 1: Acompanhar Posições

```bash
# 1. Criar transações
curl -X POST http://localhost:5000/api/transacoes \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"ativo_id":"...","tipo":"compra","quantidade":100}'

# 2. Recalcular posições
curl -X POST http://localhost:5000/api/posicoes/calcular \
  -H "Authorization: Bearer $TOKEN"

# 3. Ver resumo
curl http://localhost:5000/api/posicoes/resumo \
  -H "Authorization: Bearer $TOKEN"
```

### Exemplo 2: Consultar Proventos

```bash
# Ver proventos recebidos no último ano
curl "http://localhost:5000/api/proventos/recebidos?data_inicio=2024-01-01" \
  -H "Authorization: Bearer $TOKEN"

# Ver total recebido
curl http://localhost:5000/api/proventos/total-recebido \
  -H "Authorization: Bearer $TOKEN"
```

### Exemplo 3: Gestão de Caixa

```bash
# Fazer depósito
curl -X POST http://localhost:5000/api/movimentacoes-caixa \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "corretora_id":"uuid",
    "tipo_movimentacao":"deposito",
    "valor":"5000.00",
    "moeda":"BRL",
    "data_movimentacao":"2025-12-02"
  }'

# Ver saldo
curl http://localhost:5000/api/movimentacoes-caixa/saldo/{corretora_id} \
  -H "Authorization: Bearer $TOKEN"
```

### Exemplo 4: Dashboard Completo

```bash
# Ver dashboard
curl http://localhost:5000/api/portfolio/dashboard \
  -H "Authorization: Bearer $TOKEN"
```

---

## TROUBLESHOOTING

### Erro: Posições não calculadas

**Sintoma:** GET /api/posicoes retorna vazio

**Solução:**
```bash
curl -X POST http://localhost:5000/api/posicoes/calcular \
  -H "Authorization: Bearer $TOKEN"
```

### Erro: Preço médio incorreto

**Causa:** Transações antigas não processadas

**Solução:** Recalcular todas as posições

### Erro: Proventos não aparecem

**Causa:** Usuário não possui o ativo na data COM

**Verificação:** Conferir se possuía o ativo na data_com do provento

### Erro: Saldo incorreto na corretora

**Causa:** Movimentações inconsistentes

**Solução:** Revisar extrato e corrigir movimentações

---

## CONCLUSÃO

O Módulo 3 completa a estrutura financeira do Exitus, permitindo:

✅ Controle completo de posições e holdings  
✅ Acompanhamento de proventos recebidos  
✅ Gestão de caixa entre corretoras  
✅ Rastreamento de eventos corporativos  
✅ Analytics avançados de portfólio  

**Próximos passos:** Implementar Módulo 4 (Frontend) para visualização dos dados.

---

**Documentação gerada em:** 02/12/2025  
**Versão:** 1.0  
**Sistema:** Exitus - Controle e Análise de Investimentos
