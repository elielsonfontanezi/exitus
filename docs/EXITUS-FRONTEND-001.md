# EXITUS-FRONTEND-001 — Correção Token Expirado e Template Resiliente

## Data
2026-03-26

## Problema
- Página `/analises` retornava 500 Internal Server Error
- Causa: Token JWT expirado na sessão (`{"msg":"Token has expired"}`)
- Template quebrava ao acessar `dashboard.resumo` quando dados vazios
- Erro adicional: `TypeError: unhashable type: 'slice'` em transações

## Solução Implementada

### 1. Autenticação com Refresh Token
**Arquivo:** `frontend/app/routes/auth.py`
- Armazenar `refresh_token`, `expires_in` e `expires_at` na sessão ao logar
- Função `get_api_headers()`:
  - Verifica validade do token (renova 5 min antes de expirar)
  - Chama `/api/auth/refresh` automaticamente se necessário
  - Limpa sessão e retorna `None` se refresh falhar
  - Retorna headers com Authorization válido

### 2. Uso do Helper em Rotas
**Arquivo:** `frontend/app/routes/analises.py`
- Importar e usar `get_api_headers()` em todas as chamadas API
- Tratar respostas 401/403 com redirect para login
- Evitar token expirado durante navegação

### 3. Template Resiliente
**Arquivo:** `frontend/app/templates/analises/index.html`
- Usar `.get()` com valores padrão: `dashboard.get('resumo', {}).get('patrimonio_total', 0)`
- Corrigir sintaxe CSS em progress-bar: `width: {{ '%.1f'|format(dados.percentual) }}%;`
- Tratar transações com `is defined` para evitar erros de objeto vs string

### 4. Correções Adicionais
- Limitar transações no Python: `list(data)[:10] if data else []`
- Remover slice do template para evitar TypeError
- Remover debug prints desnecessários

## Resultados
- ✅ Página `/analises` carrega corretamente após login
- ✅ Token renovado automaticamente quando expira
- ✅ Template não quebra com dados vazios
- ✅ Dashboard exibe valores reais (R$ 249.907,10)

## Testes
- Login com usuário `e2e_user`
- Acessar `/analises` → página carrega com dados
- Forçar expiração de token → redirect para login
- Re-login → página funciona novamente

## Lições Aprendidas
- Sempre usar `.get()` em templates Jinja2 com dados de API
- Implementar refresh token para melhor UX
- Tratar slices em Python antes do template
- Validar sintaxe CSS em atributos style

## Próximos Passos
- Aplicar mesmo padrão em outras rotas (`operacoes.py`, `dashboard.py`)
- Implementar testes E2E para fluxo de expiração
- Considerar toast notification para refresh silencioso
