# Coding Standards - Sistema Exitus

## 🎯 **Naming Convention**
- **snake_case obrigatório** para todos os identificadores.
- Exemplos:
  | Tipo | Exemplo |
  |------|---------|
  | Tabelas | `historico_preco` |
  | Variáveis | `preco_medio` |
  | Arquivos | `portfolio_service.py` |

---

## 🐍 **Python/Flask Patterns**

### **Imports**
```python
# ✅ PADRÃO CORRETO
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, List, Optional

from app.database import db
from app.models.ativo import Ativo, TipoAtivo, ClasseAtivo
```

### **Models - SQLAlchemy**
```python
# ✅ PADRÕES SEGUROS

# 1. Enums - SEMPRE validar antes de usar
if ticker.endswith(('11', '12', '13')):
    tipo_ativo = TipoAtivo.FII
    classe_ativo = ClasseAtivo.RENDA_VARIAVEL  # ✅ Existe!
else:
    tipo_ativo = TipoAtivo.ACAO
    classe_ativo = ClasseAtivo.RENDA_VARIAVEL  # ✅ Existe!

# 2. Constraints - SEMPRE validar antes de inserir
if valor_operacao == 0 or quantidade == 0:
    logger.warning(f"Registro com valor/quantidade zero ignorado")
    continue  # ✅ Pular em vez de tentar inserir

# 3. Session Management - PADRÃO SEGURO
try:
    db.session.add(objeto)
    db.session.commit()
except Exception as e:
    db.session.rollback()  # ✅ Limpar estado
    logger.error(f"Erro na operação: {e}")
    raise e

# 4. Flush vs Commit
db.session.add(objeto)
db.session.flush()  # ✅ Para obter ID sem commit final
# ... mais operações ...
db.session.commit()  # ✅ Commit final para persistir
```

### **Services**
```python
# ✅ PADRÃO DE SERVICE
class ImportService:
    def __init__(self):
        self.usuario_id = None
    
    def _validate_constraints(self, **kwargs):
        """Valida constraints comuns antes de inserir"""
        for field, value in kwargs.items():
            if 'quantidade' in field.lower() and value <= 0:
                raise ValueError(f"{field} deve ser positivo")
            if 'valor' in field.lower() and value <= 0:
                raise ValueError(f"{field} deve ser positivo")
    
    def safe_commit(self):
        """Commit seguro com rollback automático"""
        try:
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e
```

---

## 🔧 **Database Patterns**

### **Migrations**
```python
# ✅ PADRÃO DE MIGRATION
def upgrade():
    # Criar enum primeiro
    op.execute("CREATE TYPE tipo_evento_custodia AS ENUM (...)")
    
    # Criar tabela
    op.create_table('evento_custodia', ...)
    
    # Criar índices
    op.create_index('ix_evento_custodia_tipo', 'evento_custodia', ['tipo'])
```

### **Queries**
```python
# ✅ QUERIES EFICIENTES
# Usar filter_by para campos diretos
ativo = Ativo.query.filter_by(ticker='PETR4').first()

# Usar filter para condições complexas
proventos = Provento.query.filter(
    Provento.data_pagamento >= data_inicio,
    Provento.tipo_provento == TipoProvento.DIVIDENDO
).all()
```

---

## 🚨 **Anti-Patterns (EVITAR)**

### **❌ NÃO FAZER**
```python
# ❌ Enums sem validar
classe_ativo = ClasseAtivo.ACAO  # AttributeError!

# ❌ Inserir sem validar constraints
provento.quantidade = 0  # CheckViolation!

# ❌ Session sem rollback
try:
    db.session.commit()
except:
    db.session.commit()  # PendingRollbackError!

# ❌ Flush sem commit
db.session.flush()  # Dados perdidos se der erro

# ❌ DROP TABLE para reset de dados (LIÇÃO APRENDIDA 02/03/2026)
db.drop_all()        # 😱 Destrói schema!
db.create_all()      # 😱 Recria do zero!
# → Perde constraints, índices, migrations
```

---

## 🎓 **Lições Aprendidas (Casos Reais)**

### **📋 LIÇÃO 002 - Sempre Verificar Tabelas Existentes (02/03/2026)**

**❌ Problema:** Deduzir nomes de tabelas sem verificar
```python
# ERRADO - causou erro em runtime
tables = ['movimentacao', 'transacao']  # movimentacao não existe!
```

**✅ Solução:** Sempre consultar o banco primeiro
```python
# CORRETO - verificar antes de usar
from sqlalchemy import inspect
tables = inspect(db.engine).get_table_names()
# → confirmar nomes reais antes de iterar
```

**📚 Regra de Ouro:** `"Nunca deduza nomes de tabelas. Sempre consulte o banco."`

**🔍 Impacto do Erro:**
- Um nome errado aborta **toda a transação** PostgreSQL
- Os DELETEs seguintes falham em cascata por `InFailedSqlTransaction`
- Runtime error difícil de debugar

---

### **📋 LIÇÃO 001 - DELETE vs DROP TABLE (02/03/2026)**

**❌ Problema:** Usar `DROP TABLE` para reset de dados
```python
# ERRADO - Destrutivo e desnecessário
db.drop_all()    # Perde schema inteiro
db.create_all()  # Recria do zero (arriscado)
```

**✅ Solução:** Usar `DELETE` para limpar apenas dados
```python
# CORRETO - Seguro e eficiente
db.session.execute(text("DELETE FROM usuario"))
db.session.execute(text("ALTER SEQUENCE usuario_id_seq RESTART WITH 1"))
```

**🎯 Por Que DELETE é Melhor:**
- **Preserva schema** (tabelas, constraints, índices)
- **Mantém migrations** intactas
- **Performance superior** (mais rápido)
- **Mais seguro** (não perde definições)
- **IDs controlados** (reset de sequences)

**📚 Contexto:**
- **Objetivo:** "Seed controlado" = limpar dados, não estrutura
- **Schema:** Gerenciado por Alembic migrations
- **Resultado:** Dados limpos, estrutura intacta

**🔍 Pergunta-Chave:** "O que realmente preciso resetar?"
- **Dados?** → DELETE ✅
- **Schema?** → DROP (raramente necessário) ⚠️

---

## 📋 **GAPs e Documentação**

### **Fluxo Obrigatório**
1. **Problema recorrente?** → Criar GAP
2. **Implementar solução** → Documentar
3. **Testar** → Validar
4. **Atualizar ROADMAP** → Status completo
5. **Fazer commit** → Com mudanças documentadas

### **Referências Obrigatórias**
- **[EXITUS-SQLALCHEMY-001.md](EXITUS-SQLALCHEMY-001.md)** - Padrões SQLAlchemy
- **[ROADMAP.md](ROADMAP.md)** - Status dos GAPs
- **[CHANGELOG.md](CHANGELOG.md)** - Histórico de mudanças

---

## 🎯 **Regras de Ouro**

1. **🔍 SEMPRE validar** enums antes de usar
2. **✅ SEMPRE validar** constraints antes de inserir  
3. **🔄 SEMPRE fazer** rollback após erros
4. **📝 SEMPRE documentar** problemas recorrentes
5. **🚀 SEMPRE seguir** fluxo de GAPs

---

*Atualizado: 02 de Março de 2026*  
*Versão: 2.0 - Padrões SQLAlchemy incluídos*
