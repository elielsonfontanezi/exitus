# EXITUS-CASHFLOW-001 - Tratamento de "Transferência - Liquidação" B3

> **Versão:** 1.0  
> **Data:** 02 de Março de 2026  
> **Status:** Análise  
> **Prioridade:** Média  
> **Tipo:** Funcionalidade

---

## 📋 **Descrição do Problema**

### **Observação Identificada**
Durante a implementação do `EXITUS-IMPORT-001`, foi identificado que o tipo de movimentação **"Transferência - Liquidação"** exportado pelo Portal da B3 representa **VENDAS de ativos** que liquidaram e geraram crédito em caixa, e não transferências de caixa da conta da corretora.

### **Análise Corrigida**
- **Natureza:** VENDA de ativo (não transferência de caixa)
- **Impacto:** Afeta preço médio do ativo
- **Necessidade:** Importar como Transação (tipo VENDA)
- **Resultado:** Reduz posição, recalcula custo médio

### **Comportamento Atual**
- **Status:** Identificado como venda, mas não implementado
- **Motivo:** Requer tratamento específico como Transacao
- **Perda:** Informação crítica para cálculo de preço médio

---

## 🎯 **Objetivo do GAP**

Implementar tratamento adequado para movimentações do tipo **"Transferência - Liquidação"** registrando-as como **Transações de VENDA** na tabela `transacao` para afetar corretamente o cálculo de preço médio dos ativos.

---

## 📊 **Análise de Requisitos**

### **Tipos de Movimentação Identificados**
| Tipo B3 | Natureza | Tratamento Atual | Tratamento Desejado |
|---------|----------|------------------|-------------------|
| "Transferência - Liquidação" | VENDA de ativo | Identificado, não implementado | Transação (VENDA) |
| "Cessão de Direitos - Solicitada" | Operação especial | Ignorado | Ignorar (não aplicável) |
| "Transferência - Ingresso" | Aporte de caixa | Ignorado | Movimentação Caixa |
| "Transferência - Saída" | Débito de caixa | Ignorado | Movimentação Caixa |

### **Mapeamento Proposto**
```python
MAPEAMENTO_VENDAS = {
    "Transferência - Liquidação": {
        "tipo_transacao": "venda",
        "descricao": "Venda - Liquidação B3"
    }
}

MAPEAMENTO_CAIXA = {
    "Transferência - Ingresso": {
        "tipo": "APORTE",
        "descricao": "Aporte de caixa B3"
    },
    "Transferência - Saída": {
        "tipo": "DEBITO", 
        "descricao": "Débito de caixa B3"
    }
}
```

---

## 🏗️ **Design da Solução**

### **1. Modelo de Dados**
Utilizar tabela existente `transacao` para vendas:

```python
class Transacao(db.Model):
    id = Column(UUID(as_uuid=True), primary_key=True)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey('usuario.id'))
    ativo_id = Column(UUID(as_uuid=True), ForeignKey('ativo.id'))
    corretora_id = Column(UUID(as_uuid=True), ForeignKey('corretora.id'))
    tipo = Column(Enum(TipoTransacao))  # "venda"
    data_transacao = Column(DateTime, nullable=False)
    quantidade = Column(Numeric(18, 8), nullable=False)
    preco_unitario = Column(Numeric(18, 6), nullable=False)
    valor_total = Column(Numeric(18, 2), nullable=False)
    observacoes = Column(Text)
    fonte = Column(String(50))  # "B3_IMPORT"
```

### **2. Service Extension**
Estender `ImportB3Service`:

```python
def _processar_vendas(self, movimentacoes: List[Dict]) -> Dict:
    """Processa Transferência - Liquidação como vendas de ativos"""
    resultado = {
        'sucesso': 0,
        'erros': 0,
        'erros_lista': []
    }
    
    tipos_venda = ['Transferência - Liquidação']
    
    for mov in movimentacoes:
        if mov['tipo_movimentacao'] in tipos_venda:
            try:
                # Obter ativo
                ticker = self._extrair_ticker(mov['produto'])
                ativo = self._obter_ou_criar_ativo(ticker, resultado)
                corretora = self._obter_ou_criar_corretora(mov['instituicao'], resultado)
                
                # Criar transação de venda
                venda = Transacao(
                    usuario_id=self._get_usuario_id(),
                    ativo_id=ativo.id,
                    corretora_id=corretora.id,
                    tipo=TipoTransacao.VENDA,
                    data_transacao=mov['data'],
                    quantidade=mov['quantidade'],
                    preco_unitario=mov['valor_operacao'] / mov['quantidade'],  # Calcular preço
                    valor_total=mov['valor_operacao'],
                    observacoes=f"Venda - Liquidação B3 - {mov['tipo_movimentacao']}"
                )
                
                db.session.add(venda)
                resultado['sucesso'] += 1
                
            except Exception as e:
                resultado['erros'] += 1
                resultado['erros_lista'].append(f"Erro na venda: {e}")
    
    return resultado
```

### **3. Integração com Importação Atual**
Modificar fluxo principal:

```python
def importar_movimentacoes(self, dados: List[Dict]) -> Dict:
    """Importação completa com tratamento de vendas"""
    
    # Separar tipos
    proventos = [m for m in dados if m['tipo_movimentacao'] not in ['Transferência - Liquidação']]
    vendas = [m for m in dados if m['tipo_movimentacao'] == 'Transferência - Liquidação']
    
    resultado = {
        'proventos': {'sucesso': 0, 'erros': 0},
        'vendas': {'sucesso': 0, 'erros': 0}
    }
    
    # Importar proventos (existente)
    resultado['proventos'] = self._importar_proventos(proventos)
    
    # Importar vendas (novo)
    resultado['vendas'] = self._processar_vendas(vendas)
    
    return resultado
```

---

## 📈 **Benefícios Esperados**

### **1. Cálculo de Preço Médio Correto**
- **Vendas registradas:** Reduzem posição do ativo
- **Custo médio recalculado:** Baseado em transações reais
- **Performance precisa:** Métricas corretas de ganho/perda

### **2. Relatórios de Performance**
- **Rentabilidade real:** Considerando todas as vendas
- **IR correto:** Base de cálculo precisa com vendas
- **Track record:** Histórico completo de operações

### **3. Auditoria e Conformidade**
- **Rastreabilidade:** Todas as vendas registradas
- **Transparência:** Histórico completo de operações
- **Conformidade:** Registro para fiscalização

---

## 🔧 **Implementação**

### **Fase 1 - Extensão Service**
- [ ] Adicionar método `_processar_vendas`
- [ ] Mapear "Transferência - Liquidação" como venda
- [ ] Implementar criação de `Transacao` (VENDA)

### **Fase 2 - Integração**
- [ ] Modificar fluxo principal de importação
- [ ] Separar proventos vs vendas
- [ ] Calcular preço unitário da venda

### **Fase 3 - Testes**
- [ ] Testar com arquivos B3 reais
- [ ] Validar impacto no preço médio
- [ ] Verificar cálculo de performance

### **Fase 4 - Documentação**
- [ ] Atualizar help do script
- [ ] Documentar tratamento de vendas
- [ ] Exemplos de impacto no preço médio

---

## 📋 **Critérios de Aceite**

### **Funcional**
- [ ] "Transferência - Liquidação" importada como `Transacao` (VENDA)
- [ ] Preço médio recalculado após venda
- [ ] Quantidade reduzida corretamente
- [ ] Valores e datas preservados

### **Qualidade**
- [ ] Sem perda de dados de venda
- [ ] Tratamento de erros robusto
- [ ] Logs detalhados de vendas
- [ ] Performance adequada

### **Integração**
- [ ] Compatível com importação existente
- [ ] Preço médio atualizado corretamente
- [ ] Script unificado funcionando
- [ ] Relatórios de performance atualizados

---

## 🚀 **Próximos Passos**

1. **Aprovação** do design
2. **Estimativa** de esforço (2-3 dias)
3. **Priorização** no roadmap
4. **Implementação** Fase 1
5. **Testes** com dados reais
6. **Deploy** e documentação

---

## 📝 **Observações**

### **Complexidade**
- **Baixa:** Extensão de funcionalidade existente
- **Risco:** Mínimo (não afeta importação atual)
- **Impacto:** Alto (visibilidade completa)

### **Dependências**
- `EXITUS-IMPORT-001` (90% completo)
- Modelo `MovimentacaoCaixa` (existente)
- Service pattern (estabelecido)

---

*Este GAP será implementado após conclusão de EXITUS-IMPORT-001.*
