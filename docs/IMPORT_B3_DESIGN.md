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

## 🎯 Abordagem Aprovada: Script Padrão + API

### 1. Script Padrão (Recomendado para uso direto)
```bash
# scripts/import_b3.py
python scripts/import_b3.py <arquivo_movimentacoes> <arquivo_negociacoes>

# Exemplos:
python scripts/import_b3.py movimentacao-20260101-20260131.csv negociacao-20260101-20260131.csv
python scripts/import_b3.py movimentacao-20260101-20260131.csv  # Apenas movimentações
```

### 2. APIs (Para integrações futuras)
```http
POST /api/import/b3/movimentacoes
Content-Type: multipart/form-data
file: movimentacao-20260101-20260131.csv
```

```http
POST /api/import/b3/negociacoes
Content-Type: multipart/form-data
file: negociacao-20260101-20260131.csv
```

### 3. Vantagens do Script Padrão
- ✅ **Flexibilidade:** Linha de comando, agendável (cron)
- ✅ **Testabilidade:** Fácil testar localmente
- ✅ **Independência:** Não depende da API estar rodando
- ✅ **Backup:** Importação manual possível

---

## 📊 Estrutura dos Arquivos B3

### Movimentações
```csv
Data;Tipo;Ativo;Quantidade;Valor Unitário;Valor Total;IR
15/01/2026;DIVIDENDO;PETR4;100;0.50;50.00;0.00
20/01/2026;JUROS SOBRE CAPITAL;VALE3;50;2.00;100.00;13.00
```

### Negociações
```csv
Data;Tipo Operação;Mercado;Papel;Quantidade;Preço;Valor Total;Taxas
10/01/2026;Compra;Vista;PETR4;100;35.50;3550.00;2.50
15/01/2026;Venda;Vista;VALE3;200;42.00;8400.00;4.20
```

---

## 🗃️ Mapeamento para Banco de Dados

### Movimentações → `provento`
| Campo B3 | Campo Exitus | Transformação |
|---|---|---|
| Data | `data_pagamento` | DD/MM/YYYY → DATE |
| Tipo | `tipo_provento` | Mapeamento direto |
| Ativo | `ativo_id` | Criar se não existir |
| Quantidade | `quantidade` | Direct |
| Valor Unitário | `valor_unitario` | Direct |
| Valor Total | `valor_bruto` | Direct |
| IR | `imposto_retido` | Direct |
| (calculado) | `valor_liquido` | `valor_bruto - imposto_retido` |
| (calculado) | `data_com` | `data_pagamento - 2 dias úteis` |

### Negociações → `transacao`
| Campo B3 | Campo Exitus | Transformação |
|---|---|---|
| Data | `data_operacao` | DD/MM/YYYY → DATE |
| Tipo Operação | `tipo_operacao` | "Compra"→COMPRA, "Venda"→VENDA |
| Papel | `ativo_id` | Criar se não existir |
| Quantidade | `quantidade` | Direct |
| Preço | `preco_unitario` | Direct |
| Valor Total | `valor_total` | Direct |
| Taxas | `taxas` | 0.00 (ignorar) |
| (calculado) | `custo_total` | `valor_total + taxas` |

---

## ⚙️ Lógica de Implementação

### 1. Upload e Parse
```python
def parse_b3_csv(file_content, tipo):
    reader = csv.DictReader(file_content, delimiter=';')
    operacoes = []
    
    for row in reader:
        if tipo == 'movimentacao':
            op = {
                'data': parse_date(row['Data']),
                'tipo_provento': mapear_tipo_provento(row['Tipo']),
                'ticker': row['Ativo'],
                'quantidade': int(row['Quantidade']),
                'valor_unitario': float(row['Valor Unitário']),
                'valor_bruto': float(row['Valor Total']),
                'imposto_retido': float(row['IR'])
            }
        elif tipo == 'negociacao':
            op = {
                'data': parse_date(row['Data']),
                'tipo_operacao': mapear_tipo_operacao(row['Tipo Operação']),
                'ticker': row['Papel'],
                'quantidade': int(row['Quantidade']),
                'preco_unitario': float(row['Preço']),
                'valor_total': float(row['Valor Total']),
                'taxas': 0.00  # Ignorar taxas
            }
        operacoes.append(op)
    
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

## 📦 Estrutura do Script

### scripts/import_b3.py
```python
#!/usr/bin/env python3
"""
Script padrão para importação de dados da B3
Uso: python scripts/import_b3.py <arquivo_movimentacoes> <arquivo_negociacoes>
"""

import sys
import os
from pathlib import Path

# Adicionar backend ao path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from backend.app import create_app
from backend.app.services.import_b3_service import ImportB3Service

def main():
    app = create_app()
    
    with app.app_context():
        service = ImportB3Service()
        usuario_id = os.getenv('EXITUS_USER_ID')  # Opcional
        
        # Importar movimentações
        if len(sys.argv) > 1:
            arquivo_mov = Path(sys.argv[1])
            if arquivo_mov.exists():
                print(f"📁 Importando movimentações de: {arquivo_mov}")
                result = service.importar_movimentacoes(arquivo_mov, usuario_id)
                print(f"✅ Movimentações: {result}")
        
        # Importar negociações
        if len(sys.argv) > 2:
            arquivo_neg = Path(sys.argv[2])
            if arquivo_neg.exists():
                print(f"📁 Importando negociações de: {arquivo_neg}")
                result = service.importar_negociacoes(arquivo_neg, usuario_id)
                print(f"✅ Negociações: {result}")

if __name__ == "__main__":
    main()
```

### backend/app/services/import_b3_service.py
```python
"""Service compartilhado para importação B3 (usado por script e API)"""

class ImportB3Service:
    def importar_movimentacoes(self, arquivo, usuario_id=None):
        """Importa arquivo de movimentações CSV"""
        # Implementação usando B3CSVAdapter
        pass
    
    def importar_negociacoes(self, arquivo, usuario_id=None):
        """Importa arquivo de negociações CSV"""
        # Implementação usando B3CSVAdapter
        pass
```

## 📦 Dependências Necessárias

```bash
# requirements.txt (adicionar)
requests>=2.31.0      # Para APIs externas
yfinance>=0.2.18     # Fallback para dados de ativos
```

---

## 📝 Próximos Passos

1. Adicionar dependências ao requirements.txt
2. Criar `scripts/import_b3.py` (script padrão)
3. Criar `backend/app/services/import_b3_service.py` (service compartilhado)
4. Criar `backend/app/services/import_b3_adapter.py` (adapter CSV)
5. Implementar parsers CSV e lógica de importação
6. Criar blueprint `import_export_blueprint.py` (APIs opcionais)
7. Escrever testes para script e service
8. Documentar em API_REFERENCE.md
9. Testar com arquivos reais da B3

---

*Design aprovado pelo usuário. Pronto para implementação.*
