
# 🔌 API Reference - Exitus v0.7.5

**Autenticação**: JWT Bearer token (1h expiry)  
**Formato Erro**: `{error: 'msg', status_code: 400}`  
**Paginação**: `?page=1&per_page=10` (total/pages no root)  
**Base URL**: `http://localhost:5000/api/`

## Endpoints por Domínio (Principais)

### Autenticação (M1)
| Método | Path | Descrição | Exemplo cURL |
|--------|------|-----------|--------------|
| `POST` | `/auth/login` | Login admin | `curl -X POST /api/auth/login -d '{"username":"admin","password":"admin123"}'` → `{access_token: 'eyJ...'} ` |
| `POST` | `/auth/register` | Novo usuário | `-d '{"username":"user","email":"u@test.com","password":"123"}'` |

### Portfólios (M3/M4)
| Método | Path | Descrição | Response Exemplo |
|--------|------|-----------|------------------|
| `GET` | `/portfolios/dashboard` | Stats agregados | `{total_patrimonio: 3250, alocacao: {"acoes":65}}` |
| `GET` | `/portfolios` | Lista paginada | `{total:2, portfolios: [{id:'uuid', nome:'Meu BR'}]}` |
| `POST` | `/portfolios` | Criar | `{id:'uuid', message:'Criado'}` |

### Transações (M2/M3)
| Método | Path | Descrição | Body Exemplo |
|--------|------|-----------|--------------|
| `GET` | `/transacoes` | Histórico | `{data: [{ticker:'PETR4', tipo:'COMPRA', valor:3250}]}` |
| `POST` | `/transacoes` | Nova compra | `{"ativo_id": "uuid_petr4", "tipo": "COMPRA", "quantidade":100, "preco":32.50}` |

### Alertas (M7.3)
| Método | Path | Descrição | Body Exemplo |
|--------|------|-----------|--------------|
| `GET` | `/alertas` | Lista (filtros: tipo/status) | `{data: [{id:'5c09...', nome:'PETR4 >R$35', ativo:true}]}` |
| `POST` | `/alertas` | Novo | `{"nome": "PETR4 Breakout", "tipo_alerta": "alta_preco", "ticker": "PETR4", "condicao_operador": ">", "condicao_valor": 35.0}` |
| `PATCH` | `/alertas/{id}/toggle` | Ativar/Desativar | `{ativo: false}` |
| `DELETE` | `/alertas/{id}` | Deletar | `{message: 'Deletado'}` |

### Relatórios (M7.4)
| Método | Path | Descrição | Body Exemplo |
|--------|------|-----------|--------------|
| `GET` | `/relatorios/lista` | Lista paginada (15+) | `{total:15, pages:2, relatorios: [{id:'247e...', tipo:'PERFORMANCE'}]}` |
| `POST` | `/relatorios/gerar` | Gerar novo | `{"tipo": "PERFORMANCE", "data_inicio": "2026-01-01", "data_fim": "2026-01-31"}` → `{id:'247e...', sharpe_ratio:1.45}` |

### Cotações (M7.5)
| Método | Path | Descrição | Exemplo |
|--------|------|-----------|---------|
| `GET` | `/cotacoes/PETR4` | Cotação atual (cache 15min) | `{ticker:'PETR4', preco:32.50, variacao:'+1.2%'}` |
| `GET` | `/cotacoes/batch?tickers=PETR4,VALE3` | Lote | `[{PETR4: {...}}, {VALE3: {...}}]` |

### Buy Signals (M4)
| Método | Path | Descrição | Exemplo |
|--------|------|-----------|---------|
| `GET` | `/buy-signals/buy-score/PETR4` | Score 0-100 | `{buy_score:80, recomendacao:'COMPRA', preco_teto:34.39}` |

## Padrões de Response

**Sucesso**:
```json
{
  "success": true,
  "data": {...},  // ou "relatorios": [...]
  "message": "Operação realizada com sucesso"
}
```

**Lista Paginada**:
```json
{
  "total": 15,
  "pages": 2,
  "per_page": 10,
  "relatorios": [...]
}
```

**Erro**:
```json
{
  "error": "data_inicio e data_fim são obrigatórias",
  "status_code": 400
}
```

## Health Checks

```
GET /health → {"status": "ok", "module": "M4 - Buy Signals + Alertas ✅"}
```

**Geração Automática**: Rode `./scripts/generate_api_docs.sh` → `docs/api/full.json` para lista exaustiva (67+ rotas).

---
**Geração**: Perplexity AI | **Base**: M1-M7.5 endpoints validados | **Próximo**: OPERATIONS_RUNBOOK.md
