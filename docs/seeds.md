# Credenciais de Teste - Sistema Exitus (Development)

⚠️ **APENAS PARA AMBIENTE DE DESENVOLVIMENTO**

## Usuários Seedados

| Username     | Email                    | Senha      | Perfil        |
|--------------|--------------------------|------------|---------------|
| admin        | admin@exitus.com         | senha123   | Administrador |
| joao.silva   | joao.silva@example.com   | senha123   | Usuário       |
| maria.santos | maria.santos@example.com | senha123   | Usuário       |
| viewer       | viewer@exitus.com        | senha123   | Visualizador  |
| teste.user   | teste@exitus.com         | senha123   | Teste         |

## Teste de Login (cURL)
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@exitus.com","password":"senha123"}'
```

## Exemplo de Response Login Bem-Sucedido
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "783c2bfd-9e36-4cbd-a4fb-901afae9fad3",
    "username": "admin",
    "email": "admin@exitus.com"
  }
}
```

## Uso do Token em Requisições
```bash
# Exportar token para variável de ambiente
export TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@exitus.com","password":"senha123"}' \
  | jq -r '.access_token')

# Usar token em requisições protegidas
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/usuarios
```

## Dados Seedados por Tabela

### Usuários (5 registros)
- 5 usuários ativos com perfis diversos (admin, usuário padrão, visualizador, teste)

### Ativos (44 registros)
- Ações brasileiras (PETR4, VALE3, ITUB4, etc.)
- Ações internacionais (AAPL, MSFT, GOOGL, etc.)
- Fundos Imobiliários (HGLG11, MXRF11, etc.)
- Criptomoedas (BTC, ETH, etc.)

### Corretoras (13 registros)
- Corretoras nacionais e internacionais
- Diversos tipos: NACIONAL, INTERNACIONAL

### Portfolios (4 registros)
- Portfolios diversificados por usuário
- Estratégias: conservador, moderado, agressivo

### Transações (17 registros)
- Tipos: COMPRA, VENDA, DIVIDENDO, JCP
- Distribuídas entre múltiplos ativos e corretoras

### Posições (17 registros)
- Posições ativas em diversos ativos
- Vinculadas a portfolios e corretoras

### Proventos (29 registros)
- Tipos: DIVIDENDO, JCP, RENDIMENTO
- Histórico de pagamentos por ativo

### Movimentações de Caixa (2 registros)
- Transferências entre corretoras
- Depósitos e retiradas

## Scripts de Seeds

### Executar todos os seeds
```bash
podman exec exitus-backend bash seeds/seedall.sh
```

### Limpar e repopular banco
```bash
# Atenção: Este comando apaga todos os dados!
podman exec exitus-db psql -U exitus -d exitusdb -c "
  TRUNCATE TABLE movimentacao_caixa, provento, transacao, posicao, 
               portfolio, corretora, ativo, usuario CASCADE;
"

# Repopular
podman exec exitus-backend bash seeds/seedall.sh
```

## Verificar Seeds Instalados
```bash
podman exec exitus-db psql -U exitus -d exitusdb -c "
SELECT 
  'usuario' AS tabela, COUNT(*) AS registros FROM usuario UNION ALL
SELECT 'ativo', COUNT(*) FROM ativo UNION ALL
SELECT 'corretora', COUNT(*) FROM corretora UNION ALL
SELECT 'portfolio', COUNT(*) FROM portfolio UNION ALL
SELECT 'transacao', COUNT(*) FROM transacao UNION ALL
SELECT 'posicao', COUNT(*) FROM posicao UNION ALL
SELECT 'provento', COUNT(*) FROM provento UNION ALL
SELECT 'movimentacao_caixa', COUNT(*) FROM movimentacao_caixa
ORDER BY tabela;
"
```

## Notas de Segurança

⚠️ **IMPORTANTE**: 
- Estas credenciais são APENAS para ambiente de desenvolvimento
- NUNCA use senhas simples como "senha123" em produção
- Altere todas as credenciais antes de deploy em produção
- Mantenha este arquivo fora do controle de versão em ambientes produtivos

## Data de Criação
- Validado em: 2026-02-09
- Sistema Exitus v0.7.6+
- PostgreSQL 16.11
- 131 registros totais seedados
EOF
```

Agora você pode:

1. **Adicionar ao Git** (se desejar versioná-lo):
```bash
git add docs/seeds.md
git commit -m "docs: adicionar documentação de seeds e credenciais de teste"
```

2. **Ou adicionar ao .gitignore** (se contiver dados sensíveis):
```bash
echo "docs/seeds.md" >> .gitignore
```

3. **Testar o login documentado**:
```bash
# Teste rápido conforme documentado
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@exitus.com","password":"senha123"}' | jq
```

