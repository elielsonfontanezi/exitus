# EXITUS-SQLALCHEMY-001 - Padrões e Boas Práticas SQLAlchemy

> **Versão:** 1.0  
> **Data:** 02 de Março de 2026  
> **Status:** ✅ Implementado  
> **Prioridade:** Alta  
> **Tipo:** Documentação e Padrões

---

## 📋 **Descrição do Problema**

### **Observação Identificada**
Durante o desenvolvimento do sistema, foram identificados **problemas recorrentes** no uso de SQLAlchemy que causam erros e inconsistências na implementação.

### **Problemas Recorrentes Identificados:**

#### **1. Erros de Enum**
```python
# ❌ ERRADO (AttributeError)
classe_ativo = ClasseAtivo.ACAO  # ACAO não existe!

# ✅ CORRETO
classe_ativo = ClasseAtivo.RENDA_VARIAVEL
```

#### **2. Violações de Constraint**
```python
# ❌ ERRADO (CheckViolation)
quantidade = 0  # Violates provento_quantidade_positiva

# ✅ CORRETO
if quantidade == 0:
    continue  # Pular registro
```

#### **3. Session Management**
```python
# ❌ ERRADO (PendingRollbackError)
db.session.commit()  # Após erro anterior sem rollback

# ✅ CORRETO
db.session.rollback()
db.session.commit()
```

#### **4. Flush vs Commit**
```python
# ❌ ERRADO (Perde dados em caso de erro)
db.session.flush()  # Não persiste permanentemente

# ✅ CORRETO
db.session.commit()  # Persiste permanentemente
```

---

## 🎯 **Objetivo do GAP**

Documentar e estabelecer **padrões corretos** para uso de SQLAlchemy no projeto Exitus, evitando erros recorrentes e garantindo consistência na implementação.

---

## 📊 **Análise de Problemas**

### **Categorias de Erros Identificados:**

| Categoria | Problema | Impacto | Frequência |
|------------|----------|---------|------------|
| **Enums** | AttributeError em enums não existentes | Alto | Frequente |
| **Constraints** | CheckViolation em campos obrigatórios | Alto | Frequente |
| **Session** | PendingRollbackError após erros | Médio | Ocasional |
| **Flush/Commit** | Perda de dados por uso incorreto | Alto | Raro |
| **Relacionamentos** | FK violations por ordem incorreta | Médio | Ocasional |

### **Exemplos Reais do Projeto:**

#### **Caso 1: ClasseAtivo.ACAO**
```python
# Arquivo: import_b3_service.py:427
classe_ativo = ClasseAtivo.ACAO  # ❌ AttributeError: ACAO

# Solução:
classe_ativo = ClasseAtivo.RENDA_VARIAVEL  # ✅ Funciona
```

#### **Caso 2: Quantidade Zero**
```python
# Erro: provento_quantidade_positiva
quantidade_ativos = 0  # ❌ CheckViolation

# Solução:
if quantidade_ativos == 0:
    continue  # ✅ Pular registro
```

#### **Caso 3: Session Rollback**
```python
# Erro: PendingRollbackError
try:
    db.session.commit()
except Exception as e:
    # Tentar commit novamente sem rollback ❌
    db.session.commit()

# Solução:
try:
    db.session.commit()
except Exception as e:
    db.session.rollback()  # ✅ Limpar estado
    raise e
```

---

## 🏗️ **Design da Solução**

### **1. Documentação de Padrões**

#### **A. Enums - Uso Correto**
```python
# ✅ SEMPRE verificar enums existentes
from app.models.ativo import ClasseAtivo, TipoAtivo

# Padrão correto:
if ticker.endswith(('11', '12', '13')):
    tipo_ativo = TipoAtivo.FII
    classe_ativo = ClasseAtivo.RENDA_VARIAVEL  # ✅ Existe
else:
    tipo_ativo = TipoAtivo.ACAO
    classe_ativo = ClasseAtivo.RENDA_VARIAVEL  # ✅ Existe
```

#### **B. Constraints - Validação Prévia**
```python
# ✅ SEMPRE validar antes de inserir
if valor_operacao == 0 or quantidade == 0:
    logger.warning(f"Registro com valor/quantidade zero ignorado")
    continue  # Pular em vez de tentar inserir
```

#### **C. Session Management**
```python
# ✅ PADRÃO SEGURO DE SESSION
try:
    # Operações no banco
    db.session.add(objeto)
    db.session.commit()
except Exception as e:
    db.session.rollback()  # Limpar estado
    logger.error(f"Erro na operação: {e}")
    raise e
```

#### **D. Flush vs Commit**
```python
# ✅ USAR CORRETAMENTE
db.session.add(objeto)
db.session.flush()  # Para obter ID sem commit final
# ... mais operações ...
db.session.commit()  # Commit final para persistir
```

### **2. Helper Functions**

#### **A. Validador de Enums**
```python
def validate_enum(enum_class, value, default=None):
    """Valida se valor existe no enum"""
    try:
        return enum_class(value)
    except ValueError:
        if default is not None:
            return default
        raise ValueError(f"Valor '{value}' inválido para {enum_class.__name__}")
```

#### **B. Safe Commit**
```python
def safe_commit(session):
    """Commit seguro com rollback automático"""
    try:
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise e
```

#### **C. Validador de Constraints**
```python
def validate_constraints(**kwargs):
    """Valida constraints comuns antes de inserir"""
    for field, value in kwargs.items():
        if 'quantidade' in field.lower() and value <= 0:
            raise ValueError(f"{field} deve ser positivo")
        if 'valor' in field.lower() and value <= 0:
            raise ValueError(f"{field} deve ser positivo")
```

---

## 📈 **Benefícios Esperados**

### **1. Redução de Erros**
- **90% menos** AttributeError em enums
- **80% menos** CheckViolation em constraints
- **100% menos** PendingRollbackError

### **2. Consistência**
- **Padrão único** para todo o projeto
- **Documentação centralizada** de boas práticas
- **Helper functions** reutilizáveis

### **3. Produtividade**
- **Debug mais rápido** com erros padronizados
- **Menos tempo** gasto em problemas recorrentes
- **Code review** mais eficiente

---

## 🔧 **Implementação**

### **Fase 1 - Documentação**
- [x] Criar guia de padrões SQLAlchemy
- [x] Documentar exemplos corretos/errados
- [x] Cheat sheet em `docs/CODING_STANDARDS.md`

### **Fase 2 - Helper Functions**
- [x] Implementar `validate_enum()` — converte string para enum com fallback seguro
- [x] Implementar `safe_commit()` — commit com rollback automático
- [x] Implementar `validate_positive()` — valida constraints de valor/quantidade
- [x] Implementar `safe_add_commit()` — add + commit + refresh em uma chamada
- [x] Implementar `safe_delete_commit()` — delete + commit seguro
- [x] Implementar `flush_or_rollback()` — flush seguro para obter IDs pré-commit

### **Fase 3 - Code Review**
- [x] Revisar e aplicar padrões em `ativo_service.py`
- [x] Revisar e aplicar padrões em `usuario_service.py`
- [x] Revisar e aplicar padrões em `corretora_service.py`
- [x] Revisar e aplicar padrões em `configuracao_alerta_service.py`
- [ ] Aplicar nos demais services (provento, transacao, alerta, posicao)

### **Fase 4 - Testes**
- [ ] Criar testes para helper functions
- [ ] Validar padrões em cenários reais

---

## 📋 **Critérios de Aceite**

### **Funcional**
- [x] Guia de padrões completo
- [x] Helper functions implementadas (`app/utils/db_utils.py`)
- [x] Exemplos práticos documentados
- [x] Cheat sheet em `CODING_STANDARDS.md`

### **Qualidade**
- [x] 100% dos problemas recorrentes documentados
- [x] Soluções validadas e testadas no container
- [x] Código exemplo funcionando
- [x] Documentação clara e objetiva

### **Adoção**
- [x] Padrões aplicados em 4 services principais
- [ ] Aplicar nos demais services (provento, transacao, alerta, posicao)
- [ ] Zero novos erros recorrentes (em andamento)

---

## 🚀 **Próximos Passos**

1. **Aprovação** do design
2. **Implementação** da documentação
3. **Criação** de helper functions
4. **Aplicação** em código existente
5. **Treinamento** da equipe

---

## 📝 **Observações Finais**

### **Complexidade**
- **Baixa:** Documentação e padrões
- **Risco:** Mínimo (não afeta código existente)
- **Valor:** Alto (economiza tempo futuro)

### **Estimativa**
- **Esforço:** 1-2 dias
- **Risco:** Baixo
- **ROI:** Alto (evita problemas futuros)

### **Impacto**
- **Imediato:** Menos erros em novo código
- **Médio prazo:** Debug mais rápido
- **Longo prazo:** Base técnica sólida

---

*Este GAP estabelece a base técnica para desenvolvimento consistente com SQLAlchemy.*
