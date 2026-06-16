# EXITUS-ASSETS-001 - Importação de Ativos Exemplo (Massa de Teste)

> **Versão:** 1.0  
> **Data:** 02 de Março de 2026  
> **Status:** Análise  
> **Prioridade:** Média  
> **Tipo:** Funcionalidade

---

## 📋 **Descrição do Problema**

### **Distinção em relação ao EXITUS-IMPORT-001**

> ⚠️ **Estes dois GAPs NÃO se sobrepõem — têm escopos distintos:**

| | EXITUS-IMPORT-001 | EXITUS-ASSETS-001 |
|---|---|---|
| **O quê** | Importar transações reais do usuário via arquivo B3 | Popular banco com ativos de todos os tipos |
| **Fonte** | Arquivo Excel/CSV do Portal B3 | Seed JSON controlado |
| **Audiência** | Usuário final | Desenvolvedor / testes |
| **Resultado** | `transacao`, `provento`, `evento_custodia` | `ativo` com dados fundamentalistas |
| **Status** | ✅ Implementado | Não implementado |

**Nota:** IMPORT-001 cria ativos automaticamente durante importação, mas apenas com dados mínimos (ticker + tipo). ASSETS-001 quer ativos **completos** com preço, DY, P/L, ROE, setor — para testes realistas de valuation e buy signals.

### **Necessidade Identificada**
O Sistema Exitus precisa de uma massa de dados robusta e realista para testes, desenvolvimento e demonstrações. Atualmente, os ativos existentes são limitados e não cobrem todos os tipos previstos no sistema.

### **Escopo Incompleto Atual**
- **Ações brasileiras:** Apenas algumas (VALE3, BBAS3, etc.)
- **FIIs:** Apenas alguns exemplos
- **Ações internacionais:** Pouca cobertura
- **Outros ativos:** Criptomoedas, ETFs, BDRs não representados

---

## 🎯 **Objetivo do GAP**

Implementar importação de ativos exemplo de todos os tipos previstos no Sistema Exitus, criando uma massa de dados completa e realista para testes.

---

## 📊 **Análise de Requisitos**

### **Tipos de Ativos Previstos no Exitus**

#### **1. Ações Brasileiras (B3)**
| Categoria | Exemplos | Setores |
|-----------|----------|---------|
| Blue Chips | PETR4, VALE3, ITUB4, BBDC4 | Bancário, Petróleo, Tecnologia |
| Small Caps | MGLU3, LREN3, AMER3 | Varejo, Consumo |
| Setor Elétrico | ELET3, CMIG4, ENBR3 | Energia |
| Mineração | VALE3, CSNA3 | Recursos naturais |

#### **2. Fundos Imobiliários (FIIs)**
| Categoria | Exemplos | Tipo |
|-----------|----------|------|
| Shoppings | HGLG11, MALL11, CTRI11 | Varejo comercial |
| Logística | BTLG11, PLRI11, VILG11 | Galpões/Armazéns |
| Híbridos | HGRE11, HGBS11 | Múltiplos setores |
| Agro | XPLG11, RBRP11 | Agronegócio |

#### **3. Ações Internacionais**
| Mercado | Exemplos | Moeda |
|---------|----------|--------|
| EUA (NYSE/NASDAQ) | AAPL, MSFT, GOOGL, TSLA | USD |
| Europa | LVMH, ASML, SAP | EUR |
| Ásia | BABA, TCEHY, SONY | USD/CNY |

#### **4. ETFs Brasileiros**
| Categoria | Exemplos | Índice |
|-----------|----------|--------|
| Ibovespa | BOVA11, SMAL11 | Índices amplos |
| Setorial | ETF4, ISUS11 | Setores específicos |
| Internacional | EWZ11, IVVB11 | Exterior |

#### **5. BDRs**
| Tipo | Exemplos | Empresa original |
|------|----------|------------------|
| Nível 1 | AAPL34, GOOGL34 | Empresas EUA |
| Nível 2 | MSFT34, AMZN34 | Empresas globais |

#### **6. Criptomoedas**
| Categoria | Exemplos | Tipo |
|-----------|----------|------|
| Principais | BTC, ETH, BNB | Layer 1 |
| DeFi | UNI, LINK, AAVE | Protocolos |
| Stablecoins | USDT, USDC, DAI | Indexadas |

#### **7. Renda Fixa**
| Tipo | Exemplos | Emissor |
|------|----------|---------|
| Tesouro Direto | SELIC, IPCA, Prefixado | Governo |
| CDBs | Bancos grandes | Bancos |
| Debêntures | Empresas | Empresas |

---

## 🏗️ **Design da Solução**

### **1. Estrutura de Dados**

```python
# Dados de exemplo por categoria
ATIVOS_EXEMPLO = {
    "acoes_br": [
        {"ticker": "PETR4", "nome": "Petrobras PN", "tipo": "ACAO", "classe": "ACAO"},
        {"ticker": "VALE3", "nome": "Vale ON", "tipo": "ACAO", "classe": "ACAO"},
        {"ticker": "ITUB4", "nome": "Itaú Unibanco PN", "tipo": "ACAO", "classe": "ACAO"},
        # ... mais 50+ exemplos
    ],
    "fii": [
        {"ticker": "HGLG11", "nome": "CSHG Logística FII", "tipo": "FII", "classe": "FII"},
        {"ticker": "BTLG11", "nome": "BTG Pactual Logística FII", "tipo": "FII", "classe": "FII"},
        # ... mais 30+ exemplos
    ],
    "acoes_us": [
        {"ticker": "AAPL", "nome": "Apple Inc.", "tipo": "ACAO", "classe": "ACAO_US"},
        {"ticker": "MSFT", "nome": "Microsoft Corp.", "tipo": "ACAO", "classe": "ACAO_US"},
        # ... mais 40+ exemplos
    ],
    "etf": [
        {"ticker": "BOVA11", "nome": "iShares Ibovespa", "tipo": "ETF", "classe": "ETF"},
        {"ticker": "SMAL11", "nome": "iShares Small Cap", "tipo": "ETF", "classe": "ETF"},
        # ... mais 20+ exemplos
    ],
    "bdr": [
        {"ticker": "AAPL34", "nome": "Apple BDR Nível 1", "tipo": "BDR", "classe": "BDR"},
        {"ticker": "MSFT34", "nome": "Microsoft BDR Nível 1", "tipo": "BDR", "classe": "BDR"},
        # ... mais 30+ exemplos
    ],
    "cripto": [
        {"ticker": "BTC", "nome": "Bitcoin", "tipo": "CRYPTO", "classe": "CRYPTO"},
        {"ticker": "ETH", "nome": "Ethereum", "tipo": "CRYPTO", "classe": "CRYPTO"},
        # ... mais 20+ exemplos
    ]
}
```

### **2. Service de Importação**

```python
class ImportAtivosService:
    """Service para importação de ativos exemplo"""
    
    def __init__(self):
        self.ativos_dados = self._carregar_ativos_exemplo()
    
    def importar_todos_ativos(self) -> Dict:
        """Importar todos os ativos exemplo"""
        resultado = {
            'sucesso': 0,
            'erros': 0,
            'categorias': {}
        }
        
        for categoria, ativos in self.ativos_dados.items():
            resultado_categoria = self._importar_categoria(categoria, ativos)
            resultado['categorias'][categoria] = resultado_categoria
            resultado['sucesso'] += resultado_categoria['sucesso']
            resultado['erros'] += resultado_categoria['erros']
        
        return resultado
    
    def _importar_categoria(self, categoria: str, ativos: List[Dict]) -> Dict:
        """Importar ativos de uma categoria específica"""
        resultado = {'sucesso': 0, 'erros': 0, 'erros_lista': []}
        
        for ativo_data in ativos:
            try:
                # Verificar se já existe
                existente = Ativo.query.filter_by(ticker=ativo_data['ticker']).first()
                if existente:
                    logger.info(f"Ativo {ativo_data['ticker']} já existe")
                    continue
                
                # Criar novo ativo
                ativo = Ativo(
                    ticker=ativo_data['ticker'],
                    nome=ativo_data['nome'],
                    tipo=ativo_data['tipo'],
                    classe=ativo_data['classe'],
                    preco_atual=self._gerar_preco_realista(ativo_data),
                    usuario_id=self._get_usuario_id()
                )
                
                db.session.add(ativo)
                resultado['sucesso'] += 1
                
            except Exception as e:
                resultado['erros'] += 1
                resultado['erros_lista'].append(f"Erro ao importar {ativo_data['ticker']}: {e}")
        
        return resultado
    
    def _gerar_preco_realista(self, ativo_data: Dict) -> Decimal:
        """Gerar preço realista baseado no tipo de ativo"""
        precos_base = {
            "ACAO": random.uniform(5.0, 500.0),
            "FII": random.uniform(50.0, 200.0),
            "ACAO_US": random.uniform(50.0, 1000.0),
            "ETF": random.uniform(80.0, 300.0),
            "BDR": random.uniform(10.0, 500.0),
            "CRYPTO": random.uniform(1000.0, 100000.0)
        }
        
        return Decimal(str(precos_base.get(ativo_data['tipo'], 100.0)))
```

### **3. Script de Importação**

```bash
#!/bin/bash
# import_ativos_exemplo.sh

show_help() {
    cat << 'EOF'
🎯 Importação de Ativos Exemplo - EXITUS-ASSETS-001

📋 USO:
    ./scripts/import_ativos_exemplo.sh [opções]

⚙️  OPÇÕES:
    --clean              Limpar ativos existentes antes de importar
    --categoria TIPO     Importar apenas categoria específica
    --dry-run           Apenas analisar sem importar
    --help, -h          Mostrar esta ajuda

📁 CATEGORIAS DISPONÍVEIS:
    acoes_br           Ações brasileiras (B3)
    fii                Fundos imobiliários
    acoes_us           Ações internacionais (EUA)
    etf                ETFs brasileiros
    bdr                BDRs nível 1
    cripto             Criptomoedas
    todos              Todas as categorias (padrão)

🎯 EXEMPLOS:
    ./scripts/import_ativos_exemplo.sh
    ./scripts/import_ativos_exemplo.sh --clean
    ./scripts/import_ativos_exemplo.sh --categoria fii
    ./scripts/import_ativos_exemplo.sh --categoria acoes_br --clean

EOF
}
```

---

## 📈 **Benefícios Esperados**

### **1. Massa de Teste Completa**
- **200+ ativos** de todos os tipos
- **Cobertura completa** do sistema
- **Dados realistas** para testes

### **2. Desenvolvimento Acelerado**
- **Testes consistentes** entre ambientes
- **Demonstrações impactantes** com dados reais
- **Validação completa** de funcionalidades

### **3. Documentação Viva**
- **Exemplos concretos** de cada tipo
- **Preços realistas** para simulações
- **Categorias bem definidas**

---

## 🔧 **Implementação**

### **Fase 1 - Preparação de Dados**
- [ ] Compilar lista completa de ativos exemplo
- [ ] Definir preços realistas por categoria
- [ ] Criar estrutura JSON de dados
- [ ] Validar tipos e enums

### **Fase 2 - Service Implementation**
- [ ] Criar `ImportAtivosService`
- [ ] Implementar importação por categoria
- [ ] Adicionar validação de duplicatas
- [ ] Implementar geração de preços

### **Fase 3 - Script e CLI**
- [ ] Criar script `import_ativos_exemplo.sh`
- [ ] Implementar opções de linha de comando
- [ ] Adicionar modo --dry-run
- [ ] Integrar com sistema existente

### **Fase 4 - Testes e Validação**
- [ ] Testar importação completa
- [ ] Validar dados gerados
- [ ] Verificar integridade do sistema
- [ ] Documentar resultados

---

## 📋 **Critérios de Aceite**

### **Funcional**
- [ ] Importar todos os tipos de ativos previstos
- [ ] Gerar preços realistas por categoria
- [ ] Permitir importação seletiva por categoria
- [ ] Evitar duplicatas de ativos

### **Qualidade**
- [ ] Dados consistentes e realistas
- [ ] Logs detalhados do processo
- [ ] Tratamento robusto de erros
- [ ] Performance adequada

### **Integração**
- [ ] Compatível com sistema atual
- [ ] Preservar dados existentes (sem --clean)
- [ ] Integrar com models existentes
- [ ] Funcionar em ambiente container

---

## 🚀 **Próximos Passos**

1. **Aprovação** do design
2. **Compilação** de dados reais
3. **Implementação** do service
4. **Criação** do script CLI
5. **Testes** em ambiente dev
6. **Documentação** final

---

## 📝 **Observações**

### **Complexidade**
- **Baixa:** Extensão de funcionalidade existente
- **Risco:** Mínimo (não afeta sistema principal)
- **Impacto:** Alto (massa de dados completa)

### **Dependências**
- `EXITUS-IMPORT-001` (✅ completo)
- `EXITUS-SEED-001` (recomendado primeiro)
- Modelo `Ativo` (existente)
- Sistema de importação (estabelecido)

### **Relacionamento com EXITUS-SEED-001**
- **EXITUS-SEED-001:** Dados essenciais do sistema (usuários, configurações)
- **EXITUS-ASSETS-001:** Dados complementares de teste (ativos exemplo)
- **Recomendação:** Implementar EXITUS-SEED-001 primeiro, depois EXITUS-ASSETS-001
- **Independência:** Pode funcionar sem EXITUS-SEED-001, mas ideal com ambos

### **Estimativa**
- **Esforço:** 2-3 dias
- **Risco:** Baixo
- **Valor:** Alto para testes e demos

---

*Este GAP complementa EXITUS-IMPORT-001 fornecendo massa de dados completa para o sistema.*
