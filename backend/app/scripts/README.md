# Scripts de Manutenção - Exitus Backend

## 📋 popular_historico_inicial.py

Script para popular a tabela `historico_preco` com dados históricos de ativos.

### Uso Básico

```bash
# Dentro do container
python3 app/scripts/popular_historico_inicial.py [OPTIONS]
```

### Opções

| Opção | Tipo | Default | Descrição |
|-------|------|---------|-----------|
| `--dias` | int | 365 | Quantidade de dias para buscar |
| `--ticker` | str | None | Ticker específico (ex: PETR4) |
| `--incluir-deslistados` | flag | False | Incluir ativos deslistados |

### Exemplos

```bash
# Popular PETR4 com 30 dias
podman exec -it exitus-backend python3 app/scripts/popular_historico_inicial.py --ticker PETR4 --dias 30

# Popular todos os ativos ativos com 90 dias
podman exec -it exitus-backend python3 app/scripts/popular_historico_inicial.py --dias 90

# Popular todos incluindo deslistados (1 ano)
podman exec -it exitus-backend python3 app/scripts/popular_historico_inicial.py --incluir-deslistados
```

### Comportamento

- ✅ **Lazy Loading**: Se histórico já existe no banco, não busca novamente
- ✅ **Fallback Gracioso**: Continua processando mesmo se API falhar
- ✅ **Multi-Mercado**: Adiciona `.SA` apenas para BR, US sem sufixo
- ✅ **Resumo Final**: Estatísticas de sucesso/erro ao final

### Logs de Exemplo

```
🚀 Iniciando população de histórico
📊 Total de ativos: 5
📅 Dias a buscar: 90

============================================================
[1/5] PETR4 (BR)... ✅ 63 registros
[2/5] VALE3 (BR)... ✅ 58 registros
[3/5] ITUB4 (BR)... ⚠️ Sem dados
[4/5] AAPL (US)... ✅ 90 registros
[5/5] TSLA (US)... ❌ Erro: Ativo não encontrado

============================================================
📊 RESUMO FINAL
============================================================
✅ Processados: 3
⚠️ Sem dados: 1
❌ Erros: 1
📈 Total registros: 211
```

### Notas

- **Primeira execução**: Pode demorar devido às chamadas de API
- **Execuções subsequentes**: Rápidas devido ao lazy loading
- **Rate Limits**: yfinance pode bloquear se muitas requisições simultâneas
- **Solução**: Execute em lotes usando `--ticker` para ativos críticos primeiro

---

**Relacionado**: Issues #1, #2, #3, #4 - Sistema de Histórico de Preços
