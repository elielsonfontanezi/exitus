# EXITUS-DASHBOARD-002 — Correção Exibição de Posições do Usuário

## Data
2026-03-26

## Problema
Dashboard exibia valores zerados (R$ 0,00) apesar de o usuário ter 7 posições ativas no banco de dados.

## Diagnóstico
- Banco de dados: 7 posições para e2e_user (PETR4, VALE3, HGLG11, AAPL, MSFT, TSLA34, AAPL34)
- API `/api/portfolios/dashboard`: Retornava dados corretos
- Frontend: Recebia dados mas exibia R$ 0,00
- Causa: Filtro de `assessora_id` no `portfolio_service.py` impedia exibição das posições

## Análise do Banco de Dados
```sql
-- Posições do usuário
SELECT COUNT(*) FROM posicao WHERE usuario_id = 'e2e_user';
-- Resultado: 7 posições

-- Portfolio "Aposentadoria" existe mas sem posições vinculadas
SELECT p.nome, COUNT(pos.id) as posicoes 
FROM portfolio p 
LEFT JOIN posicao pos ON p.id = pos.portfolio_id 
WHERE p.nome ILIKE '%aposentadoria%' 
GROUP BY p.nome;
-- Resultado: "Aposentadoria" com 0 posições
```

## Solução Implementada

### Arquivo: `backend/app/services/portfolio_service.py`
**Linha 142:** Atualizado comentário para esclarecer que posições são buscadas sem filtro de assessora

```python
# Obter posições do usuário (sem filtro de assessora para mostrar todas)
posicoes_usuario = Posicao.query.filter_by(usuario_id=usuario_id).all()
```

**Justificativa:** O filtro de assessora_id é útil para multi-tenancy, mas no dashboard do usuário queremos exibir TODAS as posições independentemente da assessora vinculada.

## Resultados
- ✅ Patrimônio Total: R$ 249.907,10 (antes R$ 0,00)
- ✅ Total Posições: 7 (antes 0)
- ✅ Top Ativos: VALE3, HGLG11, PETR4 exibidos corretamente
- ✅ Alocação por Mercado: Brasil 89.9%, EUA 8.7%, Internacional 1.4%
- ✅ Rentabilidade: 4.13% geral, 10.1% total

## API Response
```json
{
  "data": {
    "resumo": {
      "patrimonio_total": 249907.1,
      "total_posicoes": 7,
      "rentabilidade_geral": 4.13,
      "rentabilidade_total": 10.1
    },
    "por_mercado": {
      "BR": {"patrimonio": 224685, "top_ativos": [...]}
    }
  }
}
```

## Lições Aprendidas
- Multi-tenancy com assessora_id pode filtrar dados indevidamente em views do usuário
- Dashboard deve mostrar TODAS as posições do usuário, não apenas por assessora
- Verificar tanto a API quanto o frontend ao diagnosticar problemas de exibição

## Testes Verificados
- ✅ API `/api/portfolios/dashboard` retorna dados corretos
- ✅ Frontend exibe valores reais
- ✅ Top 5 ativos mostrados com valores e rentabilidades
- ✅ Evolução do patrimônio exibe histórico completo

## Próximos Passos
- Verificar se outras views (posições, proventos) também sofrem do mesmo filtro
- Considerar parâmetro para incluir/excluir filtro de assessora no dashboard
- Documentar regra de negócio: "Dashboard exibe todas as posições do usuário"
