# Diagrama Entidade-Relacionamento - Exitus

> **Data:** 09/03/2026  
> **Banco:** PostgreSQL 16  
> **Tabelas:** 25 (incluindo alembic_version)  
> **Tabelas de negócio:** 23

---

## 📊 Visão Geral do Schema

### Entidades Principais (Core)
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   usuario   │    │   ativo     │    │  corretora  │
├─────────────┤    ├─────────────┤    ├─────────────┤
│ id (PK)     │◄───┤ id (PK)     │◄───┤ id (PK)     │
│ username    │    │ ticker      │    │ nome        │
│ email       │    │ nome        │    │ tipo        │
│ role        │    │ tipo        │    │ pais        │
│ created_at  │    │ classe      │    │ usuario_id  │
└─────────────┘    └─────────────┘    └─────────────┘
```

### Transações e Posições
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  transacao  │    │   posicao   │    │movimentacao │
├─────────────┤    ├─────────────┤    │   _caixa    │
│ id (PK)     │◄───┤ id (PK)     │    ├─────────────┤
│ usuario_id  │    │ usuario_id  │    │ id (PK)     │
│ ativo_id    │    │ ativo_id    │    │ usuario_id  │
│ corretora_id│    │ corretora_id│    │ corretora_id│
│ tipo        │    │ quantidade  │    │ tipo_mov    │
│ data_trans  │    │ preco_medio │    │ valor       │
│ quantidade  │    │ custo_total │    │ data_mov    │
└─────────────┘    └─────────────┘    └─────────────┘
```

### Proventos e Eventos
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   provento  │    │evento_cust  │    │evento_corp  │
├─────────────┤    │   odia      │    │   orativo   │
│ id (PK)     │    ├─────────────┤    ├─────────────┤
│ usuario_id  │    │ id (PK)     │    │ id (PK)     │
│ ativo_id    │    │ usuario_id  │    │ ativo_id    │
│ corretora_id│    │ ativo_id    │    │ tipo_evento │
│ tipo        │    │ tipo_evento │    │ data_evento │
│ data_com    │    │ data_evento │    │ quantidade  │
│ valor       │    │ quantidade  │    │ preco_unit  │
└─────────────┘    └─────────────┘    └─────────────┘
```

---

## 🔗 Relacionamentos Principais

### 1. Multi-Tenant (Usuario-centric)
```
usuario (1) ──→ (N) transacao
usuario (1) ──→ (N) posicao
usuario (1) ──→ (N) movimentacao_caixa
usuario (1) ──→ (N) provento
usuario (1) ──→ (N) portfolio
usuario (1) ──→ (N) alertas
```

### 2. Ativo como Entidade Central
```
ativo (1) ──→ (N) transacao
ativo (1) ──→ (N) posicao
ativo (1) ──→ (N) provento
ativo (1) ──→ (N) historico_preco
ativo (1) ──→ (N) evento_corporativo
ativo (1) ──→ (N) evento_custodia
```

### 3. Corretora como Intermediária
```
corretora (1) ──→ (N) transacao
corretora (1) ──→ (N) posicao
corretora (1) ──→ (N) movimentacao_caixa
corretora (1) ──→ (N) provento
```

---

## 📋 Tabelas de Apoio (Support)

### Sistema e Auditoria
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│log_auditoria│    │auditoria_rel│    │alembic_ver  │
├─────────────┤    │   atorios   │    │   sion      │
│ id (PK)     │    ├─────────────┤    ├─────────────┤
│ usuario_id  │    │ id (PK)     │    │ version_num │
│ acao        │    │ usuario_id  │    └─────────────┘
│ entidade    │    │ tipo_rel    │
│ timestamp   │    │ data_ger    │
└─────────────┘    │ parametros  │
                   └─────────────┘
```

### Configurações e Referências
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│regra_fiscal │    │feriado_merc │    │fonte_dados  │
├─────────────┤    │     ado     │    ├─────────────┤
│ id (PK)     │    ├─────────────┤    │ id (PK)     │
│ pais        │    │ id (PK)     │    │ nome        │
│ tipo_ativo  │    │ data_feriado│    │ tipo        │
│ aliquota    │    │ descricao   │    │ url         │
└─────────────┘    └─────────────┘    └─────────────┘
```

### Dados de Mercado
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│historico_pre│    │ parametros  │    │ taxa_cambio │
│     co      │    │   _macro    │    ├─────────────┤
├─────────────┤    ├─────────────┤    │ id (PK)     │
│ id (PK)     │    │ id (PK)     │    │ moeda_orig  │
│ ativo_id    │    │ nome_param  │    │ moeda_dest  │
│ data_preco  │    │ valor       │    │ taxa        │
│ preco       │    │ data_atual  │    │ data_ref    │
└─────────────┘    └─────────────┘    └─────────────┘
```

---

## 💰 Tabelas Fiscais

```
┌─────────────┐    ┌─────────────┐
│saldo_darf_a │    │saldo_preju  │
│   cumulado  │    │     izo     │
├─────────────┤    ├─────────────┤
│ id (PK)     │    │ id (PK)     │
│ usuario_id  │    │ usuario_id  │
│ categoria   │    │ ativo_id    │
│ codigo_rec  │    │ ano_mes     │
│ ano_mes     │    │ valor       │
│ saldo       │    └─────────────┘
└─────────────┘
```

---

## 📈 Analytics e Relatórios

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   portfolio │    │projecoes_ren│    │relatorios_  │
├─────────────┤    │     da      │    │ performance │
│ id (PK)     │    ├─────────────┤    ├─────────────┤
│ usuario_id  │    │ id (PK)     │    │ id (PK)     │
│ nome        │    │ usuario_id  │    │ usuario_id  │
│ descricao   │    │ ativo_id    │    │ tipo_rel    │
│ data_ref    │    │ tipo_proj   │    │ data_ger    │
└─────────────┘    │ valor_proj  │    │ parametros  │
                   │ data_proj   │    └─────────────┘
                   └─────────────┘
```

---

## 🔔 Sistema de Alertas

```
┌─────────────┐    ┌─────────────┐
│  alertas    │    │config_alerta│
├─────────────┤    │     es      │
│ id (PK)     │    ├─────────────┤
│ usuario_id  │    │ id (PK)     │
│ ativo_id    │    │ usuario_id  │
│ tipo_alerta │    │ tipo_alerta │
│ valor_alvo  │    │ valor_alvo  │
│ ativo       │    │ ativo       │
│ data_cria   │    └─────────────┘
└─────────────┘
```

---

## 🎯 Principais Chaves Estrangeiras

| Tabela | FK | Referência |
|--------|----|------------|
| transacao | usuario_id | usuario.id |
| transacao | ativo_id | ativo.id |
| transacao | corretora_id | corretora.id |
| posicao | usuario_id | usuario.id |
| posicao | ativo_id | ativo.id |
| posicao | corretora_id | corretora.id |
| movimentacao_caixa | usuario_id | usuario.id |
| movimentacao_caixa | corretora_id | corretora.id |
| provento | usuario_id | usuario.id |
| provento | ativo_id | ativo.id |
| provento | corretora_id | corretora.id |
| corretora | usuario_id | usuario.id |
| historico_preco | ativo_id | ativo.id |
| evento_corporativo | ativo_id | ativo.id |
| evento_custodia | usuario_id | usuario.id |
| evento_custodia | ativo_id | ativo.id |

---

## 📊 Estatísticas do Schema

| Categoria | Quantidade |
|-----------|------------|
| **Tabelas totais** | 25 |
| **Tabelas de negócio** | 23 |
| **Tabelas de sistema** | 2 (alembic_version, log_auditoria) |
| **Entidades core** | 3 (usuario, ativo, corretora) |
| **Tabelas transacionais** | 5 (transacao, posicao, movimentacao_caixa, provento, evento_custodia) |
| **Tabelas de mercado** | 3 (historico_preco, parametros_macro, taxa_cambio) |
| **Tabelas fiscais** | 2 (saldo_darf_acumulado, saldo_prejuizo) |
| **Tabelas analytics** | 3 (portfolio, projecoes_renda, relatorios_performance) |
| **Tabelas configuração** | 3 (regra_fiscal, feriado_mercado, fonte_dados) |
| **Tabelas alertas** | 2 (alertas, configuracoes_alertas) |
| **Tabelas auditoria** | 2 (log_auditoria, auditoria_relatorios) |

---

## 🔄 Como Manter Este Diagrama

1. **Atualização automática:** Usar script `scripts/exitus_db_doc.sh` para gerar `EXITUS_DB_STRUCTURE.txt`
2. **Atualização manual:** Editar este arquivo quando houver mudanças estruturais
3. **Versionamento:** Sempre commitar junto com migrations que alteram o schema
4. **Validação:** Comparar com `EXITUS_DB_STRUCTURE.txt` mensalmente

---

## 📝 Notas de Design

- **Multi-tenant:** Todas as tabelas de negócio possuem `usuario_id`
- **UUID PKs:** Todas as tabelas usam UUID como chave primária
- **Auditoria:** `log_auditoria` registra todas as operações CRUD
- **Soft delete:** Implementado via campo `ativo` em tabelas principais
- **Timestamps:** `created_at`/`updated_at` em todas as tabelas principais
- **Enums:** Usados para campos com valores fixos (tipo_movimentacao, tipo_ativo, etc)

**Status:** ✅ Diagrama atualizado refletindo schema atual (25 tabelas)
