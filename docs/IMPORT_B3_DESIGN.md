# Design: Importação B3 Portal Investidor

> **GAP:** EXITUS-IMPORT-001  
> **Foco:** Importação de arquivos CSV da B3  
> **Data:** 27 de Fevereiro de 2026

---

## 📋 Decisões do Usuário

1. **Ativos não encontrados:** Criar automaticamente ✅
2. **Corretora:** Não há relação (usar padrão) ✅
3. **Taxas:** Assumir R$ 0,00 ✅
4. **Duplicatas:** Sobrescrever ✅

---

## 🎯 APIs Propostas

### 1. Importar Movimentações (Proventos)
```http
POST /api/import/b3/movimentacoes
Content-Type: multipart/form-data

file: movimentacao-20260101-20260131.csv
```

### 2. Importar Negociações (Compras/Vendas)
```http
POST /api/import/b3/negociacoes
Content-Type: multipart/form-data

file: negociacao-20260101-20260131.csv
```

---

## 📊 Estrutura Real dos Arquivos B3 (Excel)

### Movimentações (movimentacao-*.xlsx)
**Colunas:**
- `Entrada/Saída` (Credito)
- `Data` (25/02/2026)
- `Movimentação` (Rendimento, Dividendo, Juros Sobre Capital, etc.)
- `Produto` (ALZR11 - ALIANZA TRUST RENDA IMOBILIARIA...)
- `Instituição` (ITAU CV S/A)
- `Quantidade`, `Preço unitário`, `Valor da Operação`

### Negociações (negociacao-*.xlsx)
**Colunas:**
- `Data do Negócio` (20/01/2026)
- `Tipo de Movimentação` (Compra, Venda)
- `Mercado` (Mercado à Vista)
- `Prazo/Vencimento` (-)
- `Instituição` (ITAU CV S/A)
- `Código de Negociação` (BTLG11)
- `Quantidade`, `Preço`, `Valor`

---

## 🔄 Mapeamento Portal B3 → Exitus

### Tipos de Movimentação
| Portal B3 | ENUM Exitus | Observações |
|---|---|---|
| Rendimento | RENDIMENTO | ✅ Já previsto |
| Juros Sobre Capital Próprio | JUROS_CAPITAL | ✅ Já previsto |
| Dividendo | DIVIDENDO | ✅ Já previsto |
| Direito de Subscrição | DIREITO_SUBSCRICAO | ✅ Já previsto |
| Atualização | ATUALIZACAO | ✅ Já previsto |
| Cessão de Direitos | CESSAO_DIREITOS | ✅ Já previsto |
| Transferência - Liquidação | TRANSFERENCIA | ✅ Já previsto |
| Reembolso | REEMBOLSO | ✅ Já previsto |

### Formato Híbrido (CSV + Excel)
```bash
# Suporte a ambos os formatos
python scripts/import_b3.py movimentacao.xlsx negociacao.xlsx
python scripts/import_b3.py movimentacao.csv negociacao.csv
```

---

## 🗃️ Mapeamento para Banco de Dados

### Movimentações → `provento`
| Campo B3 | Campo Exitus | Transformação |
|---|---|---|
| Data | `data_pagamento` | DD/MM/YYYY → DATE |
| Movimentação | `tipo_provento` | Mapeamento Portal B3 → ENUM |
| Produto | `ativo_id` | Split no hífen, criar se não existir |
| Instituição | `corretora_id` | Criar/associar corretora real |
| Quantidade | `quantidade` | Direct |
| Preço unitário | `valor_unitario` | Direct |
| Valor da Operação | `valor_bruto` | Direct |
| (calculado) | `valor_liquido` | `valor_bruto` (sem IR explicito) |
| (calculado) | `data_com` | `data_pagamento - 2 dias úteis` |

### Negociações → `transacao`
| Campo B3 | Campo Exitus | Transformação |
|---|---|---|
| Data do Negócio | `data_operacao` | DD/MM/YYYY → DATE |
| Tipo de Movimentação | `tipo_operacao` | "Compra"→COMPRA, "Venda"→VENDA |
| Código de Negociação | `ativo_id` | Criar se não existir |
| Instituição | `corretora_id` | Criar/associar corretora real |
| Quantidade | `quantidade` | Direct |
| Preço | `preco_unitario` | Direct |
| Valor | `valor_total` | Direct |
| (calculado) | `taxas` | 0.00 (não informado) |
| (calculado) | `custo_total` | `valor_total + taxas` |

---

## ⚙️ Lógica de Implementação

### 1. Parse Híbrido (CSV + Excel)
```python
import pandas as pd
import csv
from pathlib import Path

def parse_b3_file(arquivo_path, tipo):
    """Parse CSV ou Excel do Portal B3"""
    arquivo_path = Path(arquivo_path)
    
    # Detectar formato
    if arquivo_path.suffix.lower() == '.xlsx':
        return parse_excel(arquivo_path, tipo)
    elif arquivo_path.suffix.lower() == '.csv':
        return parse_csv(arquivo_path, tipo)
    else:
        raise ValueError("Formato não suportado. Use .csv ou .xlsx")

def parse_excel(arquivo_path, tipo):
    """Parse arquivo Excel do Portal B3"""
    df = pd.read_excel(arquivo_path)
    operacoes = []
    
    for _, row in df.iterrows():
        if tipo == 'movimentacao':
            # Extrair ticker do Produto (ex: "ALZR11 - ALIANZA TRUST...")
            produto = row['Produto']
            ticker = produto.split(' - ')[0].strip() if ' - ' in produto else produto
            
            op = {
                'data': parse_date(row['Data']),
                'tipo_provento': mapear_tipo_provento(row['Movimentação']),
                'ticker': ticker,
                'corretora': row['Instituição'],
                'quantidade': int(row['Quantidade']) if pd.notna(row['Quantidade']) else 0,
                'valor_unitario': float(row['Preço unitário']) if pd.notna(row['Preço unitário']) else 0.0,
                'valor_bruto': float(row['Valor da Operação']) if pd.notna(row['Valor da Operação']) else 0.0
            }
        elif tipo == 'negociacao':
            op = {
                'data': parse_date(row['Data do Negócio']),
                'tipo_operacao': mapear_tipo_operacao(row['Tipo de Movimentação']),
                'ticker': row['Código de Negociação'],
                'corretora': row['Instituição'],
                'quantidade': int(row['Quantidade']),
                'preco_unitario': float(row['Preço']),
                'valor_total': float(row['Valor'])
            }
        operacoes.append(op)
    
    return operacoes

def parse_csv(arquivo_path, tipo):
    """Parse arquivo CSV (se usuário converter)"""
    df = pd.read_csv(arquivo_path, delimiter=';')
    # Lógica similar ao parse_excel mas com colunas CSV
    return operacoes
```

### 2. Criação Automática de Ativos (Híbrida)
```python
# Mapeamento manual como fallback
MAPEAMENTO_ATIVOS = {
    "PETR4": "PETRÓBRAS",
    "VALE3": "VALE",
    "ITUB4": "ITAÚ UNIBANCO",
    "BBDC4": "BANCO DO BRASIL",
    "BBAS3": "BANCO DO BRASIL",
    "WEGE3": "WEG",
    "ABEV3": "AMBEV",
    "EQTL3": "EQUATORIAL",
    "SANB4": "SANTANDER BRASIL",
    "B3SA3": "B3",
    # ... expandir conforme necessário
}

def buscar_nome_ativo_api(ticker):
    """Tenta buscar nome via API externa"""
    try:
        # Opção 1: brapi.dev (brasileiro, gratuito)
        response = requests.get(f"https://brapi.dev/api/quote/{ticker}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('results'):
                return data['results'][0].get('shortName', ticker)
        
        # Opção 2: yfinance (fallback)
        import yfinance as yf
        stock = yf.Ticker(f"{ticker}.SA")
        info = stock.info
        return info.get('shortName', ticker)
    except:
        return None

def garantir_ativo_existente(ticker):
    ativo = Ativo.query.filter_by(ticker=ticker).first()
    if not ativo:
        # Buscar nome real (API + fallback)
        nome = buscar_nome_ativo_api(ticker)
        if not nome:
            nome = MAPEAMENTO_ATIVOS.get(ticker, ticker)  # Fallback manual
        
        # Detectar tipo de ativo baseado no ticker
        tipo = detectar_tipo_ativo(ticker)
        
        ativo = Ativo(
            ticker=ticker,
            nome=nome,  # Nome real!
            tipo=tipo,
            pais="BR",
            moeda="BRL"
        )
        db.session.add(ativo)
        db.session.commit()
    return ativo

def detectar_tipo_ativo(ticker):
    """Detecta tipo baseado no padrão do ticker"""
    if ticker.endswith(("11", "12", "13", "14", "15", "16")):
        return "FII"
    elif ticker.endswith(("34", "35", "36")):
        return "ETF"
    elif ticker == "BDRX11" or ticker.startswith(("BDR", "35")):
        return "BDR"
    elif ticker.endswith(("31", "32", "33", "41", "42", "43", "44", "51", "52", "53", "54", "55", "56", "61", "62", "63", "64", "71", "72", "73", "74", "81", "82", "83", "84")):
        return "ACAO"
    else:
        return "ACAO"  # Default
```

### 3. Corretora Padrão
```python
def get_corretora_padrao(usuario_id):
    # Buscar primeira corretora do usuário ou criar padrão
    corretora = Corretora.query.filter_by(usuario_id=usuario_id).first()
    if not corretora:
        corretora = Corretora(
            nome="Corretora Padrão",
            tipo="OUTRA",
            pais="BR",
            moeda_padrao="BRL",
            usuario_id=usuario_id
        )
        db.session.add(corretora)
        db.session.commit()
    return corretora
```

### 4. Sobrescrever Duplicatas
```python
def importar_movimentacao(usuario_id, dados):
    ativo = garantir_ativo_existente(dados['ticker'])
    
    # Buscar duplicata
    existente = Provento.query.filter_by(
        usuario_id=usuario_id,
        ativo_id=ativo.id,
        data_pagamento=dados['data'],
        tipo_provento=dados['tipo_provento']
    ).first()
    
    if existente:
        # Sobrescrever
        existente.quantidade = dados['quantidade']
        existente.valor_unitario = dados['valor_unitario']
        existente.valor_bruto = dados['valor_bruto']
        existente.imposto_retido = dados['imposto_retido']
        existente.valor_liquido = dados['valor_bruto'] - dados['imposto_retido']
    else:
        # Criar novo
        novo = Provento(
            usuario_id=usuario_id,
            ativo_id=ativo.id,
            data_pagamento=dados['data'],
            tipo_provento=dados['tipo_provento'],
            quantidade=dados['quantidade'],
            valor_unitario=dados['valor_unitario'],
            valor_bruto=dados['valor_bruto'],
            imposto_retido=dados['imposto_retido'],
            valor_liquido=dados['valor_bruto'] - dados['imposto_retido']
        )
        db.session.add(novo)
```

### 5. Atualizar Posições (pós-importação)
```python
def atualizar_posicoes_usuario(usuario_id):
    # Recalcular todas as posições do usuário
    posicoes = db.session.query(Posicao).filter_by(usuario_id=usuario_id).all()
    
    for posicao in posicoes:
        # Recalcular quantidade, preço médio, custo total
        transacoes = db.session.query(Transacao).filter_by(
            usuario_id=usuario_id,
            ativo_id=posicao.ativo_id
        ).all()
        
        # Lógica de cálculo...
        posicao.quantidade = calcular_quantidade(transacoes)
        posicao.preco_medio = calcular_preco_medio(transacoes)
        posicao.custo_total = calcular_custo_total(transacoes)
    
    db.session.commit()
```

---

## 🔍 Mapeamentos de Tipo

### Tipo Provento
| B3 | Exitus |
|---|---|
| DIVIDENDO | DIVIDENDO |
| JUROS SOBRE CAPITAL | JUROS_CAPITAL |
| BONIFICACAO | BONIFICACAO |
| RENDIMENTO | RENDIMENTO |

### Tipo Operação
| B3 | Exitus |
|---|---|
| Compra | COMPRA |
| Venda | VENDA |

---

## 📈 Response da API

```json
{
  "success": true,
  "data": {
    "total_linhas": 45,
    "importadas": 45,
    "ignoradas": 0,
    "erros": [],
    "ativos_criados": 3,
    "resumo": {
      "proventos": 12,
      "compras": 18,
      "vendas": 15
    }
  }
}
```

---

## 🧪 Testes Necessários

1. **Parse CSV** com diferentes formatos de data
2. **Criação automática de ativos**
3. **Sobrescrita de duplicatas**
4. **Atualização de posições**
5. **Rollback em erro**
6. **Arquivo malformado**

---

## 🔄 Mapeamento Portal B3 → ENUMs

```python
def mapear_tipo_provento(tipo_b3):
    """Mapeia tipo do Portal B3 para ENUM Exitus"""
    mapeamento = {
        "Rendimento": "RENDIMENTO",
        "Juros Sobre Capital Próprio": "JUROS_CAPITAL",
        "Dividendo": "DIVIDENDO",
        "Direito de Subscrição": "DIREITO_SUBSCRICAO",
        "Atualização": "ATUALIZACAO",
        "Cessão de Direitos": "CESSAO_DIREITOS",
        "Transferência - Liquidação": "TRANSFERENCIA",
        "Reembolso": "REEMBOLSO",
        "Direitos de Subscrição - Não Exercido": "DIREITO_SUBSCRICAO_NAO_EXERCIDO",
        "Cessão de Direitos - Solicitada": "CESSAO_DIREITOS_SOLICITADA"
    }
    return mapeamento.get(tipo_b3, tipo_b3)  # Fallback para o próprio nome

def mapear_tipo_operacao(tipo_b3):
    """Mapeia tipo do Portal B3 para ENUM Exitus"""
    mapeamento = {
        "Compra": "COMPRA",
        "Venda": "VENDA"
    }
    return mapeamento.get(tipo_b3, tipo_b3)
```

## 📦 Dependências Necessárias

```bash
# requirements.txt (adicionar)
requests>=2.31.0      # Para APIs externas
yfinance>=0.2.18     # Fallback para dados de ativos
pandas>=2.0.0        # Parse Excel/CSV
openpyxl>=3.1.0      # Suporte Excel
```

---

## 📝 Próximos Passos

1. Adicionar dependências ao requirements.txt (pandas, openpyxl)
2. Criar `scripts/import_b3.py` (script padrão híbrido)
3. Criar `backend/app/services/import_b3_service.py` (service compartilhado)
4. Criar `backend/app/services/import_b3_adapter.py` (adapter Excel/CSV)
5. Implementar mapeamento Portal B3 → ENUMs
6. Implementar parse híbrido (Excel prioritário, CSV fallback)
7. Implementar criação automática de corretoras reais
8. Criar blueprint `import_export_blueprint.py` (APIs opcionais)
9. Escrever testes com arquivos reais da B3
10. Documentar em API_REFERENCE.md
11. Testar com seus arquivos reais (movimentacao-*.xlsx, negociacao-*.xlsx)

---

*Design aprovado pelo usuário. Pronto para implementação.*
