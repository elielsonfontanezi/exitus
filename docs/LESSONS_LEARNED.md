# Lições Aprendidas - Exitus Development

> **Registro de lições aprendidas durante o desenvolvimento**  
> **Data:** 02 de Março de 2026  
> **Status:** Documento em evolução

---

## 📋 **LIÇÃO 001 - DELETE vs DROP TABLE (02/03/2026)**

### **❌ Problema Identificado**
Durante implementação do `EXITUS-SEED-001`, optei por usar `DROP TABLE` para reset de dados:

```python
# ERRADO - Destrutivo e desnecessário
db.drop_all()    # Perde schema inteiro
db.create_all()  # Recria do zero (arriscado)
```

### **🎯 Pensamento Incorreto**
- **"Reset completo"** → Pensei em "recriar tudo"
- **"Limpar banco"** → Interpretei como "apagar e refazer"
- **Preocupação excessiva** com dados residuais
- **Mentalidade de "Fresh Start"** equivocada

### **✅ Solução Correta**
Usar `DELETE` para limpar apenas dados:

```python
# CORRETO - Seguro e eficiente
db.session.execute(text("DELETE FROM usuario"))
db.session.execute(text("ALTER SEQUENCE usuario_id_seq RESTART WITH 1"))
```

### **🎯 Por Que DELETE é Superior**
- **🛡️ Preserva schema** (tabelas, constraints, índices)
- **📦 Mantém migrations** intactas
- **⚡ Performance superior** (mais rápido)
- **🔒 Mais seguro** (não perde definições)
- **🎲 IDs controlados** (reset de sequences)

### **📚 Contexto do Problema**
- **Objetivo:** "Seed controlado" = limpar dados, não estrutura
- **Schema:** Gerenciado por Alembic migrations
- **Resultado:** Dados limpos, estrutura intacta

### **🔍 Pergunta-Chave Aprendida**
"O que realmente preciso resetar?"
- **Dados?** → DELETE ✅
- **Schema?** → DROP (raramente necessário) ⚠️

### **💡 Impacto da Lição**
- **Implementação corrigida** do sistema de seed
- **Documentação atualizada** com padrões
- **Futuros desenvolvedores** evitarão o mesmo erro
- **Performance melhorada** do sistema

---

## 📋 **LIÇÃO 002 - Sempre Verificar Tabelas Existentes (02/03/2026)**

### **❌ Problema Identificado**
Durante implementação do `EXITUS-SEED-001`, a lista de tabelas para DELETE foi escrita **deduzindo** os nomes baseado no domínio:

```python
# ERRADO - Dedução sem verificar
tables_to_clean = [
    'movimentacao',   # ❌ Não existe! É movimentacao_caixa
    'transacao',
    ...
]
```

Resultado: Erro em runtime + transação abortada bloqueando os DELETEs seguintes.

### **✅ Solução Correta**
**Sempre consultar o banco antes de listar tabelas:**

```python
# CORRETO - Verificar tabelas reais
from sqlalchemy import inspect
inspector = inspect(db.engine)
tables = inspector.get_table_names()
print(sorted(tables))
# → ['ativo', 'corretora', 'evento_corporativo', 'evento_custodia',
#    'movimentacao_caixa', 'portfolio', 'posicao', 'provento',
#    'transacao', 'usuario', ...]
```

### **🎯 Por Que Deduzir é Errado**
- **Nome != Domínio:** `movimentacao` não existe, existe `movimentacao_caixa`
- **Efeito cascata:** Um erro aborta toda a transação PostgreSQL
- **Tabelas extras:** `evento_corporativo` não estava na lista inicial
- **Tabelas de suporte:** `feriado_mercado`, `fonte_dados`, `regra_fiscal` também existem

### **🔍 Comando de Verificação (usar antes de implementar)**
```python
# Dentro do app context
from sqlalchemy import inspect
inspector = inspect(db.engine)
print(sorted(inspector.get_table_names()))

# Ou via psql/podman
podman exec exitus-db psql -U exitus -c "\dt"
```

### **📚 Regra de Ouro**
> **"Nunca deduza nomes de tabelas. Sempre consulte o banco."**

### **✅ Checklist Antes de Listar Tabelas**
- [ ] Consultei `inspect(db.engine).get_table_names()`?
- [ ] Verifiquei os `__tablename__` dos models?
- [ ] Testei com uma tabela antes de iterar todas?

---

## 🎓 **Como Aplicar Esta Lição**

### **✅ Fazer Sempre**
```python
# Para reset de dados:
DELETE FROM tabela;
ALTER SEQUENCE tabela_id_seq RESTART WITH 1;
```

### **❌ Evitar**
```python
# Nunca para reset de dados:
db.drop_all()
db.create_all()
```

### **🎯 Testar Aplicação**
- **Schema intacto?** ✅
- **Constraints preservadas?** ✅
- **Índices mantidos?** ✅
- **IDs reiniciados?** ✅

---

## 📋 **Padrão Estabelecido**

### **Para Sistemas de Seed/Reset:**
1. **Identificar objetivo** (dados vs schema)
2. **Usar DELETE** para limpar dados
3. **Reset sequences** para IDs controlados
4. **Preservar estrutura** do banco
5. **Documentar padrão** para equipe

### **Para Debugging:**
- **Backup/Restore** de cenários
- **Dados controlados** para testes
- **Schema estável** para consistência

---

## 🔄 **Próximos Passos**

1. **✅ Documentar** lição aprendida
2. **✅ Implementar** solução correta
3. **✅ Testar** funcionalidade
4. **✅ Compartilhar** com equipe
5. **📋 Monitorar** aplicações futuras

---

*Esta lição foi aprendida graças a uma excelente pergunta do usuário sobre a necessidade de DROP TABLE.*  
*Sempre questione "por que" das decisões técnicas!*

---

## 📞 **Referências**

- **[CODING_STANDARDS.md](CODING_STANDARDS.md)** - Padrões atualizados
- **[EXITUS-SEED-001.md](EXITUS-SEED-001.md)** - Implementação corrigida
- **[CHANGELOG.md](CHANGELOG.md)** - Histórico de mudanças
