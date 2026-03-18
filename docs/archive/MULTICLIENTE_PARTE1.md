# MULTICLIENTE-001 - Multi-Tenancy (Parte 1)

## 🎯 Objetivo

Implementar sistema multi-tenant para permitir que múltiplas assessoras de investimento utilizem o Exitus, cada uma com seus próprios usuários, portfolios e dados isolados.

## 📊 Status: Parte 1 Concluída (16/03/2026)

### ✅ Implementado

#### 1. Model Assessora (`assessora.py`)
- **23 campos completos:**
  - Identificação: id, nome, razao_social, cnpj
  - Contato: email, telefone, site
  - Endereço: endereco, cidade, estado, cep
  - Regulamentação: numero_cvm, anbima
  - Controle: ativo, data_cadastro
  - Customização: logo_url, cor_primaria, cor_secundaria
  - Limites: max_usuarios, max_portfolios, plano
  - Timestamps: created_at, updated_at

- **Relacionamentos:**
  - usuarios (lazy='dynamic')
  - portfolios (lazy='dynamic')
  - transacoes (lazy='dynamic')
  - posicoes (lazy='dynamic')
  - planos_compra (lazy='dynamic')
  - planos_venda (lazy='dynamic')

- **Properties:**
  - `total_usuarios`: Conta usuários ativos
  - `total_portfolios`: Conta portfolios
  - `pode_adicionar_usuario`: Valida limite
  - `pode_adicionar_portfolio`: Valida limite

- **Métodos:**
  - `to_dict()`: Serialização JSON

#### 2. Migrations

**Migration 1: `20260316_1540_create_assessora_table.py`**
- Cria tabela `assessora`
- 4 índices: nome (unique), cnpj (unique), email (unique), ativo
- Merge de heads do Alembic

**Migration 2: `20260316_1545_add_assessora_id_to_tables.py`**
- Adiciona `assessora_id` em **20 tabelas:**
  - Dados do Usuário: usuario, portfolio, posicao, transacao, movimentacao_caixa, provento, plano_compra, plano_venda
  - Dados Fiscais: saldo_prejuizo, saldo_darf_acumulado
  - Alertas/Relatórios: configuracoes_alertas, alertas, relatorios_performance, auditoria_relatorios, projecoes_renda
  - Logs: log_auditoria, evento_custodia
  - Dados de Mercado: historico_preco, calendario_dividendo, evento_corporativo

- **20 foreign keys** com `ondelete='CASCADE'`
- **24 índices:**
  - 20 índices simples: `ix_{table}_assessora_id`
  - 4 índices compostos:
    - `ix_usuario_assessora_ativo`
    - `ix_transacao_assessora_data`
    - `ix_posicao_assessora_ativo`
    - `ix_portfolio_assessora_usuario`

#### 3. Models Atualizados (4/20)

**✅ Usuario**
- Campo: `assessora_id` (UUID, FK, nullable, indexed)
- Relacionamento: `assessora = relationship('Assessora', back_populates='usuarios')`
- `to_dict()`: Inclui `assessora_id` e `assessora_nome`

**✅ Portfolio**
- Campo: `assessora_id` (UUID, FK, nullable, indexed)
- Relacionamento: `assessora = relationship('Assessora', back_populates='portfolios')`

**✅ PlanoVenda**
- Campo: `assessora_id` (UUID, FK, nullable, indexed)
- Relacionamento: `assessora = relationship('Assessora', back_populates='planos_venda')`

**✅ PlanoCompra**
- Campo: `assessora_id` (UUID, FK, nullable, indexed)
- Relacionamento: `assessora = relationship('Assessora', back_populates='planos_compra')`

#### 4. Scripts Auxiliares

**`add_assessora_to_models.py`**
- Script Python para automatizar atualização dos 16 models restantes
- Adiciona `assessora_id` e relacionamento automaticamente
- Validações e relatório de progresso

#### 5. Exports

**`models/__init__.py`**
- Import: `from .assessora import Assessora`
- Export: `"Assessora"` em `__all__`

---

## 📋 Próximos Passos (Parte 2)

### 🔴 Pendente

1. **Atualizar 16 Models Restantes:**
   - posicao, transacao, movimentacao_caixa, provento
   - saldo_prejuizo, saldo_darf_acumulado
   - configuracao_alerta, alerta
   - relatorio_performance, auditoria_relatorio, projecao_renda
   - log_auditoria, evento_custodia
   - historico_preco, calendario_dividendo, evento_corporativo

2. **Aplicar Migrations:**
   - Executar `alembic upgrade head`
   - Criar assessora padrão para dados existentes
   - Migrar dados: `UPDATE {table} SET assessora_id = {default_id}`

3. **Atualizar Services:**
   - Adicionar filtros automáticos por `assessora_id`
   - Validar acesso em todos os CRUDs
   - Implementar helper `get_current_assessora()`

4. **JWT e Autenticação:**
   - Incluir `assessora_id` no payload do JWT
   - Atualizar `@jwt_required` para validar assessora
   - Modificar login para retornar assessora

5. **Middleware de Tenant Isolation:**
   - Criar decorator `@require_assessora`
   - Implementar filtro automático em queries
   - Validação de acesso cross-tenant

6. **Testes:**
   - Atualizar fixtures com assessoras
   - Testes de isolamento de dados
   - Testes de validação de acesso

7. **Documentação:**
   - API Reference com multi-tenancy
   - Guia de uso para assessoras
   - Atualizar ROADMAP

---

## 🏗️ Arquitetura Multi-Tenant

### Modelo Escolhido: Shared Database + Tenant Column

```
┌─────────────────────────────────────────────────┐
│              Banco de Dados Único               │
│                                                 │
│  ┌──────────────┐  ┌──────────────┐           │
│  │  Assessora A │  │  Assessora B │           │
│  │              │  │              │           │
│  │ - Usuários   │  │ - Usuários   │           │
│  │ - Portfolios │  │ - Portfolios │           │
│  │ - Transações │  │ - Transações │           │
│  └──────────────┘  └──────────────┘           │
│                                                 │
│  Isolamento via assessora_id em WHERE clauses  │
└─────────────────────────────────────────────────┘
```

### Tabelas Globais (Sem assessora_id)

- `ativo` - Ativos são compartilhados
- `corretora` - Corretoras são globais
- `feriado_mercado` - Feriados são globais
- `fonte_dados` - Fontes são globais
- `regra_fiscal` - Regras fiscais são globais
- `parametros_macro` - Parâmetros são globais
- `taxa_cambio` - Taxas de câmbio são globais

### Benefícios

✅ **Simples de implementar** - Coluna adicional
✅ **Performance adequada** - Índices otimizados
✅ **Migração incremental** - Nullable inicialmente
✅ **Backup/restore simples** - Um banco só
✅ **Custo reduzido** - Infraestrutura compartilhada

### Trade-offs

⚠️ **Isolamento lógico** (não físico) - Requer validações rigorosas
⚠️ **Queries mais complexas** - WHERE assessora_id em tudo
⚠️ **Risco de vazamento** - Se esquecer filtro

---

## 📊 Estatísticas

- **Arquivos criados:** 4
  - assessora.py
  - 2 migrations
  - add_assessora_to_models.py

- **Arquivos modificados:** 5
  - usuario.py
  - portfolio.py
  - plano_venda.py
  - plano_compra.py
  - models/__init__.py

- **Linhas adicionadas:** ~600
- **Tabelas afetadas:** 20
- **Índices criados:** 24
- **Foreign keys:** 20

---

## 🎯 Critérios de Sucesso (Parte 2)

- [ ] Todos os 20 models com `assessora_id`
- [ ] Migrations aplicadas sem erros
- [ ] Assessora padrão criada
- [ ] Dados existentes migrados
- [ ] JWT inclui `assessora_id`
- [ ] Services filtram por assessora
- [ ] Middleware de isolamento funcional
- [ ] 491 testes passando
- [ ] Backend inicia sem erros
- [ ] Documentação atualizada

---

*Última atualização: 16/03/2026 18:11*  
*Modelo IA utilizado: Claude Sonnet*  
*Status: Parte 1 Concluída - Aguardando Parte 2*
