# PLANO DE TESTES MULTI-TENANCY — Sistema Exitus

> **Status:** 🟡 Em Execução  
> **Data Criação:** 03/04/2026  
> **Modelo IA:** Claude Sonnet  
> **GAP:** MULTICLIENTE-001 (Parte 4 — Validação)  
> **Objetivo:** Validar isolamento completo entre assessoras e row-level security

---

## 🎯 Objetivo

Garantir que o sistema multi-tenant implementado em MULTICLIENTE-001 funcione corretamente, com **isolamento total** entre assessoras e **validação rigorosa** de acesso cross-tenant.

---

## 🏗️ Arquitetura Multi-Tenant (Recap)

### Modelo: Shared Database + Tenant Column

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

### Assessora Padrão

- **ID:** `23c54cb4-cb0a-438f-b985-def21d70904e`
- **Nome:** Assessora E2E Teste
- **Usuários:** e2e_admin, e2e_user, e2e_viewer

---

## 📋 Escopo de Testes

### 1. Testes de Isolamento (Cross-Tenant)

**Objetivo:** Garantir que usuários de uma assessora **não vejam/modifiquem** dados de outra.

#### Cenários:
- ✅ Usuário A não vê portfolios de Assessora B
- ✅ Usuário A não vê transações de Assessora B
- ✅ Usuário A não vê posições de Assessora B
- ✅ Usuário A não vê proventos de Assessora B
- ✅ Usuário A não vê movimentações de Assessora B
- ✅ Usuário A não vê planos de compra/venda de Assessora B
- ✅ Usuário A não vê alertas de Assessora B
- ✅ Usuário A não vê histórico patrimonial de Assessora B

#### Validações:
- **GET /api/resource** → retorna apenas dados da própria assessora
- **GET /api/resource/{id}** → 403 Forbidden se recurso de outra assessora
- **PUT /api/resource/{id}** → 403 Forbidden se recurso de outra assessora
- **DELETE /api/resource/{id}** → 403 Forbidden se recurso de outra assessora

---

### 2. Testes de Filtros Automáticos

**Objetivo:** Validar que `filter_by_assessora()` funciona em todos os services.

#### Services a Testar (10/10):
1. ✅ `usuario_service.py`
2. ✅ `portfolio_service.py`
3. ✅ `transacao_service.py`
4. ✅ `posicao_service.py`
5. ✅ `plano_venda_service.py`
6. ✅ `plano_compra_service.py`
7. ✅ `movimentacao_caixa_service.py`
8. ✅ `provento_service.py`
9. ✅ `alerta_service.py`
10. ✅ `evento_corporativo_service.py`

#### Validações:
- Queries retornam apenas dados com `assessora_id` do JWT
- Sem vazamento de dados entre tenants
- Performance adequada (índices funcionando)

---

### 3. Testes de JWT com assessora_id

**Objetivo:** Garantir que o token JWT contém `assessora_id` e é validado corretamente.

#### Cenários:
- ✅ Login retorna JWT com `assessora_id`
- ✅ Endpoints extraem `assessora_id` do token via `get_current_assessora_id()`
- ✅ Token sem `assessora_id` → 403 Forbidden (se `@require_assessora`)
- ✅ Token com `assessora_id` inválido → 403 Forbidden

---

### 4. Testes de Row-Level Security

**Objetivo:** Validar que decorators `@require_assessora` bloqueiam acesso não autorizado.

#### Endpoints Críticos (a implementar):
- [ ] `/api/portfolios/*` → requer `@require_assessora`
- [ ] `/api/transacoes/*` → requer `@require_assessora`
- [ ] `/api/posicoes/*` → requer `@require_assessora`
- [ ] `/api/proventos/*` → requer `@require_assessora`
- [ ] `/api/movimentacoes/*` → requer `@require_assessora`
- [ ] `/api/plano-compra/*` → requer `@require_assessora`
- [ ] `/api/plano-venda/*` → requer `@require_assessora`
- [ ] `/api/alertas/*` → requer `@require_assessora`

#### Validações:
- Usuário sem `assessora_id` no JWT → 403 Forbidden
- Acesso a recurso de outra assessora → 403 Forbidden (não 404)

---

### 5. Testes de Migração de Dados

**Objetivo:** Validar que dados existentes foram migrados corretamente.

#### Cenários:
- ✅ Todos os usuários têm `assessora_id` preenchido
- ✅ Todos os portfolios têm `assessora_id` preenchido
- ✅ Todas as transações têm `assessora_id` preenchido
- ✅ Todas as posições têm `assessora_id` preenchido
- ✅ Assessora padrão existe e está ativa

---

### 6. Testes de Performance

**Objetivo:** Garantir que filtros multi-tenant não degradam performance.

#### Cenários:
- ✅ Índices em `assessora_id` funcionando
- ✅ Queries com `WHERE assessora_id = X` usam índice
- ✅ Tempo de resposta < 200ms para queries simples
- ✅ Tempo de resposta < 1s para queries complexas

---

## 🧪 Estrutura de Testes

### Fixtures Necessárias

```python
# backend/tests/conftest.py

@pytest.fixture
def assessora_a(db_session):
    """Assessora A para testes cross-tenant"""
    assessora = Assessora(
        id=uuid.uuid4(),
        nome='Assessora A Teste',
        razao_social='Assessora A Ltda',
        cnpj='11111111000111',
        email='assessora_a@teste.com',
        ativo=True
    )
    db_session.add(assessora)
    db_session.commit()
    return assessora

@pytest.fixture
def assessora_b(db_session):
    """Assessora B para testes cross-tenant"""
    assessora = Assessora(
        id=uuid.uuid4(),
        nome='Assessora B Teste',
        razao_social='Assessora B Ltda',
        cnpj='22222222000222',
        email='assessora_b@teste.com',
        ativo=True
    )
    db_session.add(assessora)
    db_session.commit()
    return assessora

@pytest.fixture
def usuario_a(db_session, assessora_a):
    """Usuário da Assessora A"""
    usuario = Usuario(
        id=uuid.uuid4(),
        username='usuario_a',
        email='usuario_a@teste.com',
        assessora_id=assessora_a.id,
        role=UserRole.USER
    )
    usuario.set_password('senha123')
    db_session.add(usuario)
    db_session.commit()
    return usuario

@pytest.fixture
def usuario_b(db_session, assessora_b):
    """Usuário da Assessora B"""
    usuario = Usuario(
        id=uuid.uuid4(),
        username='usuario_b',
        email='usuario_b@teste.com',
        assessora_id=assessora_b.id,
        role=UserRole.USER
    )
    usuario.set_password('senha123')
    db_session.add(usuario)
    db_session.commit()
    return usuario
```

---

## 📝 Casos de Teste

### Teste 1: Isolamento de Portfolios

```python
def test_usuario_nao_ve_portfolios_de_outra_assessora(
    client, usuario_a, usuario_b, assessora_a, assessora_b
):
    """Usuário A não deve ver portfolios da Assessora B"""
    
    # Criar portfolio para Assessora A
    portfolio_a = Portfolio(
        usuario_id=usuario_a.id,
        assessora_id=assessora_a.id,
        nome='Portfolio A'
    )
    db.session.add(portfolio_a)
    
    # Criar portfolio para Assessora B
    portfolio_b = Portfolio(
        usuario_id=usuario_b.id,
        assessora_id=assessora_b.id,
        nome='Portfolio B'
    )
    db.session.add(portfolio_b)
    db.session.commit()
    
    # Login como usuário A
    token_a = get_jwt_token(usuario_a)
    
    # Listar portfolios (deve retornar apenas Portfolio A)
    response = client.get(
        '/api/portfolios/',
        headers={'Authorization': f'Bearer {token_a}'}
    )
    
    assert response.status_code == 200
    data = response.json['data']
    assert len(data) == 1
    assert data[0]['nome'] == 'Portfolio A'
    
    # Tentar acessar Portfolio B diretamente (deve retornar 403)
    response = client.get(
        f'/api/portfolios/{portfolio_b.id}',
        headers={'Authorization': f'Bearer {token_a}'}
    )
    
    assert response.status_code == 403
    assert 'Acesso negado' in response.json['message']
```

### Teste 2: Isolamento de Transações

```python
def test_usuario_nao_ve_transacoes_de_outra_assessora(
    client, usuario_a, usuario_b, assessora_a, assessora_b
):
    """Usuário A não deve ver transações da Assessora B"""
    
    # Criar transação para Assessora A
    transacao_a = Transacao(
        usuario_id=usuario_a.id,
        assessora_id=assessora_a.id,
        ativo_id=ativo.id,
        tipo=TipoTransacao.COMPRA,
        quantidade=100,
        preco=50.00
    )
    db.session.add(transacao_a)
    
    # Criar transação para Assessora B
    transacao_b = Transacao(
        usuario_id=usuario_b.id,
        assessora_id=assessora_b.id,
        ativo_id=ativo.id,
        tipo=TipoTransacao.COMPRA,
        quantidade=200,
        preco=60.00
    )
    db.session.add(transacao_b)
    db.session.commit()
    
    # Login como usuário A
    token_a = get_jwt_token(usuario_a)
    
    # Listar transações (deve retornar apenas Transação A)
    response = client.get(
        '/api/transacoes/',
        headers={'Authorization': f'Bearer {token_a}'}
    )
    
    assert response.status_code == 200
    data = response.json['data']
    assert len(data) == 1
    assert data[0]['quantidade'] == 100
    
    # Tentar acessar Transação B diretamente (deve retornar 403)
    response = client.get(
        f'/api/transacoes/{transacao_b.id}',
        headers={'Authorization': f'Bearer {token_a}'}
    )
    
    assert response.status_code == 403
```

### Teste 3: JWT com assessora_id

```python
def test_jwt_contem_assessora_id(client, usuario_a, assessora_a):
    """JWT deve conter assessora_id após login"""
    
    response = client.post('/api/auth/login', json={
        'username': 'usuario_a',
        'password': 'senha123'
    })
    
    assert response.status_code == 200
    token = response.json['data']['access_token']
    
    # Decodificar JWT
    payload = jwt.decode(token, options={"verify_signature": False})
    
    assert 'assessora_id' in payload
    assert payload['assessora_id'] == str(assessora_a.id)
```

### Teste 4: Decorator @require_assessora

```python
def test_endpoint_sem_assessora_id_retorna_403(client):
    """Endpoint com @require_assessora deve retornar 403 se JWT sem assessora_id"""
    
    # Criar usuário sem assessora_id
    usuario_sem_assessora = Usuario(
        username='sem_assessora',
        email='sem@teste.com',
        assessora_id=None,
        role=UserRole.USER
    )
    usuario_sem_assessora.set_password('senha123')
    db.session.add(usuario_sem_assessora)
    db.session.commit()
    
    # Login
    token = get_jwt_token(usuario_sem_assessora)
    
    # Tentar acessar endpoint protegido
    response = client.get(
        '/api/portfolios/',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    assert response.status_code == 403
    assert 'assessora_id' in response.json['message'].lower()
```

### Teste 5: Filtro Automático em Services

```python
def test_filter_by_assessora_funciona_em_portfolio_service(
    db_session, usuario_a, usuario_b, assessora_a, assessora_b
):
    """Service deve filtrar automaticamente por assessora_id"""
    
    # Criar portfolios para ambas assessoras
    portfolio_a = Portfolio(
        usuario_id=usuario_a.id,
        assessora_id=assessora_a.id,
        nome='Portfolio A'
    )
    portfolio_b = Portfolio(
        usuario_id=usuario_b.id,
        assessora_id=assessora_b.id,
        nome='Portfolio B'
    )
    db_session.add_all([portfolio_a, portfolio_b])
    db_session.commit()
    
    # Simular JWT com assessora_id de A
    with mock_jwt_claims({'assessora_id': str(assessora_a.id)}):
        portfolios = PortfolioService.get_all(usuario_a.id)
        
        assert len(portfolios) == 1
        assert portfolios[0].nome == 'Portfolio A'
```

---

## 🎯 Critérios de Sucesso

### Mínimo Aceitável
- ✅ 100% dos testes de isolamento passando
- ✅ 0 vazamentos de dados cross-tenant
- ✅ JWT com `assessora_id` funcionando
- ✅ Filtros automáticos em todos os 10 services

### Ideal
- ✅ Decorators `@require_assessora` em todos os endpoints críticos
- ✅ Testes de performance validados
- ✅ Dashboard admin por assessora (futuro)
- ✅ 491/497 testes passando (100%)

---

## 📊 Cobertura de Testes

### Testes a Implementar

| Categoria | Testes | Status |
|-----------|--------|--------|
| **Isolamento Cross-Tenant** | 8 | ⏳ Pendente |
| **Filtros Automáticos** | 10 | ⏳ Pendente |
| **JWT com assessora_id** | 3 | ⏳ Pendente |
| **Decorators @require_assessora** | 8 | ⏳ Pendente |
| **Migração de Dados** | 5 | ⏳ Pendente |
| **Performance** | 4 | ⏳ Pendente |
| **Total** | **38** | **0/38** |

---

## 🔧 Comandos Úteis

### Executar Testes Multi-Tenancy

```bash
# Todos os testes multi-tenancy
podman exec exitus-backend python -m pytest backend/tests/test_multitenancy.py -v

# Teste específico
podman exec exitus-backend python -m pytest backend/tests/test_multitenancy.py::test_isolamento_portfolios -v

# Com cobertura
podman exec exitus-backend python -m pytest backend/tests/test_multitenancy.py --cov=app.utils.tenant --cov-report=term
```

### Verificar Dados no Banco

```bash
# Listar assessoras
podman exec exitus-db psql -U exitus -d exitusdb -c "SELECT id, nome, email FROM assessora;"

# Verificar usuários com assessora
podman exec exitus-db psql -U exitus -d exitusdb -c "SELECT username, assessora_id FROM usuario;"

# Verificar portfolios por assessora
podman exec exitus-db psql -U exitus -d exitusdb -c "SELECT p.nome, u.username, a.nome as assessora FROM portfolio p JOIN usuario u ON p.usuario_id = u.id JOIN assessora a ON p.assessora_id = a.id;"
```

---

## 📝 Próximos Passos

1. **Implementar testes** em `/backend/tests/test_multitenancy.py`
2. **Adicionar decorators** `@require_assessora` nos endpoints críticos
3. **Executar suite** e validar 491/497 testes passando
4. **Atualizar docs** (MULTICLIENTE.md, CHANGELOG.md, PROJECT_STATUS.md)
5. **Commit** com documentação completa

---

## 📚 Referências

- `docs/MULTICLIENTE.md` — Documento consolidado multi-tenancy
- `backend/app/utils/tenant.py` — Helper functions
- `backend/app/services/auth_service.py` — JWT com assessora_id
- `.windsurfrules` — Regras de processo e testes

---

*Criado em: 03/04/2026*  
*Modelo IA: Claude Sonnet*  
*Status: 🟡 Em Execução*
