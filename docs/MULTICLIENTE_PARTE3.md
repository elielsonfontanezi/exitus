# MULTICLIENTE-001 - Multi-Tenancy (Parte 3)

## 🎯 Status: Parte 3 Iniciada (16/03/2026 21:25)

### ✅ Implementado na Parte 3

#### 1. Migração de Dados Completa

**Tabelas Migradas para Assessora Padrão:**
- ID: `23c54cb4-cb0a-438f-b985-def21d70904e`

```sql
-- Parte 1 + 2A (já migradas)
✅ usuario (5 registros)
✅ portfolio (0 registros)
✅ transacao (0 registros)
✅ posicao (0 registros)
✅ plano_compra (0 registros)
✅ plano_venda (0 registros)

-- Parte 3 (novas migrações)
✅ movimentacao_caixa (0 registros)
✅ provento (0 registros)
✅ saldo_prejuizo (0 registros)
✅ saldo_darf_acumulado (0 registros)
✅ historico_preco (0 registros)
✅ evento_corporativo (1 registro)
✅ configuracoes_alertas (0 registros)
✅ auditoria_relatorios (0 registros)
✅ log_auditoria (7 registros)
✅ alertas (0 registros)
✅ relatorios_performance (0 registros)
✅ calendario_dividendo (0 registros)
```

**Total: 13 registros migrados (5 usuários + 1 evento + 7 logs)**

#### 2. Helper de Tenant Criado

**Arquivo: `backend/app/utils/tenant.py`**

**Funções Implementadas:**

1. **`get_current_assessora_id()`**
   - Extrai assessora_id do JWT atual
   - Retorna UUID ou None
   - Usa `verify_jwt_in_request(optional=True)`

2. **`require_assessora(f)`**
   - Decorator para garantir assessora no token
   - Retorna 403 se assessora_id não existe
   - Armazena assessora_id em `g.assessora_id`

3. **`require_same_assessora(model_assessora_id)`**
   - Valida que registro pertence à mesma assessora
   - Lança `PermissionError` se assessoras diferentes
   - Permite acesso se sem assessora no token

4. **`filter_by_assessora(query, model_class)`**
   - Adiciona filtro automático de assessora_id
   - Verifica se model tem atributo `assessora_id`
   - Retorna query filtrada

**Exemplo de Uso:**
```python
from app.utils.tenant import get_current_assessora_id, filter_by_assessora

# Em um service
def listar_usuarios():
    query = Usuario.query
    query = filter_by_assessora(query, Usuario)
    return query.all()

# Com decorator
from app.utils.tenant import require_assessora

@require_assessora
def criar_portfolio(data):
    assessora_id = get_current_assessora_id()
    portfolio = Portfolio(**data, assessora_id=assessora_id)
    # ...
```

#### 3. JWT Atualizado

**Arquivo: `backend/app/services/auth_service.py`**

**Modificação no Login:**
```python
# Antes
access_token = create_access_token(
    identity=str(user.id),
    additional_claims={'role': user.role.value}
)

# Depois
additional_claims = {'role': user.role.value}
if user.assessora_id:
    additional_claims['assessora_id'] = str(user.assessora_id)

access_token = create_access_token(
    identity=str(user.id),
    additional_claims=additional_claims
)
```

**Payload do Token:**
```json
{
  "sub": "uuid-do-usuario",
  "role": "admin",
  "assessora_id": "23c54cb4-cb0a-438f-b985-def21d70904e"
}
```

#### 4. Backend Testado

- ✅ Tenant utils importam sem erros
- ✅ Auth service modificado
- ✅ JWT inclui assessora_id

---

## 📋 Pendente para Finalização da Parte 3

### 🔴 Atualizar Services com Filtros

**Services Prioritários (5-10):**

1. **usuario_service.py**
   ```python
   def listar_usuarios():
       query = Usuario.query
       query = filter_by_assessora(query, Usuario)
       return query.all()
   ```

2. **portfolio_service.py**
   ```python
   def listar_portfolios(usuario_id):
       query = Portfolio.query.filter_by(usuario_id=usuario_id)
       query = filter_by_assessora(query, Portfolio)
       return query.all()
   ```

3. **transacao_service.py**
4. **posicao_service.py**
5. **plano_venda_service.py**

### 🔴 Middleware de Tenant Isolation

**Criar `app/middleware/tenant.py`:**
```python
from functools import wraps
from flask import g, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt

def tenant_isolation():
    """Middleware global para isolamento de tenant"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Verifica JWT se presente
        try:
            verify_jwt_in_request(optional=True)
            claims = get_jwt()
            g.assessora_id = claims.get('assessora_id')
        except:
            g.assessora_id = None
        
        return f(*args, **kwargs)
    return decorated
```

### 🔴 Testes de Multi-Tenancy

**Criar `backend/tests/test_multi_tenancy.py`:**
```python
def test_jwt_inclui_assessora_id(client, assessora_padrao, usuario_teste):
    """Testa que JWT inclui assessora_id"""
    response = client.post('/api/auth/login', json={
        'username': 'teste',
        'password': 'senha123'
    })
    
    assert response.status_code == 200
    token = response.json['access_token']
    
    # Decodificar token
    from flask_jwt_extended import decode_token
    decoded = decode_token(token)
    
    assert 'assessora_id' in decoded
    assert decoded['assessora_id'] == str(assessora_padrao.id)

def test_filtro_por_assessora(client, assessora_a, assessora_b, usuario_a, usuario_b):
    """Testa que usuário A não vê dados de assessora B"""
    # Login como usuário A
    token_a = login(client, usuario_a)
    
    # Buscar portfolios
    response = client.get('/api/portfolios', headers={'Authorization': f'Bearer {token_a}'})
    
    portfolios = response.json
    # Verificar que só retorna portfolios da assessora A
    for p in portfolios:
        assert p['assessora_id'] == str(assessora_a.id)
```

### 🔴 Documentação de API

**Atualizar `docs/API_REFERENCE.md`:**
- Adicionar campo `assessora_id` em todos os endpoints
- Documentar header `X-Assessora-ID` (opcional)
- Explicar isolamento de dados

---

## 📊 Estatísticas Parte 3

- **Dados migrados:** 13 registros (5 usuários + 1 evento + 7 logs)
- **Helper criado:** 4 funções utilitárias
- **JWT atualizado:** Inclui assessora_id
- **Services atualizados:** 0/20 (pendente)
- **Testes criados:** 0 (pendente)

---

## 🎯 Critérios de Sucesso (Parte 3 Completa)

- [x] Dados migrados para assessora padrão
- [x] Helper de tenant criado
- [x] JWT inclui assessora_id
- [ ] 5-10 services principais com filtros
- [ ] Middleware de isolamento (opcional)
- [ ] 3-5 testes de multi-tenancy
- [ ] 491 testes passando
- [ ] Documentação atualizada

---

## 📝 Próximos Passos

1. **Atualizar 5 services principais** com `filter_by_assessora()`
2. **Criar 3 testes básicos** de multi-tenancy
3. **Rodar suite de testes** (491 testes)
4. **Atualizar documentação** (API_REFERENCE.md)
5. **Commit final** da Parte 3

---

*Última atualização: 16/03/2026 21:25*  
*Modelo IA utilizado: Claude Sonnet*  
*Status: Parte 3 Iniciada - Helper e JWT implementados*  
*Progresso: 60% (dados migrados, helper criado, JWT atualizado)*
