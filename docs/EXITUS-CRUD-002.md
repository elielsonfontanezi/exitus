# EXITUS-CRUD-002 — Revisão Estrutural da Camada Service/Route

> **Versão:** 1.0  
> **Data:** 03 de Março de 2026  
> **Status:** Não implementado  
> **Fase:** 3 — Qualidade  
> **Prioridade:** Alta  
> **Origem:** Descoberto durante EXITUS-TESTS-001  
> **Modelo IA recomendado:** Sonnet (refatoração estrutural com impacto amplo)

---

## 1. Descrição do Problema

Durante a implementação dos testes de integração (EXITUS-TESTS-001), foram identificados **3 problemas estruturais sistêmicos** na camada service/route que afetam toda a API:

### 1.1 — `ValueError` com papel duplo (404 + 400)

Os services lançam `ValueError` para **situações semanticamente diferentes**:

```python
# Ambos lançam ValueError, mas significados opostos:
raise ValueError("Ativo não encontrado")        # → deveria ser 404 Not Found
raise ValueError("Ativo já existe no mercado")  # → deveria ser 409 Conflict
raise ValueError("Email já existe")             # → deveria ser 409 Conflict
raise ValueError("Senha atual incorreta")       # → deveria ser 400 Bad Request
raise ValueError("Apenas admin pode alterar")   # → deveria ser 403 Forbidden
```

O route captura tudo indiscriminadamente como 400:
```python
except ValueError as e:
    return error(str(e), 400)  # engloba 404, 409, 403 incorretamente
```

**Impacto:** Clientes da API recebem status codes semanticamente errados. Testes precisam aceitar 400 onde deveriam receber 404. Frontend não consegue distinguir "não encontrado" de "dados inválidos".

---

### 1.2 — `delete()` sem validação de integridade referencial

Todos os services implementam `delete()` sem verificar dependências:

```python
# AtivoService.delete() — ativo_service.py:176
# TODO: Verificar se há posições/transações vinculadas
# Por enquanto, permite deletar
safe_delete_commit(ativo)
```

O banco tem `ondelete='CASCADE'` em algumas FKs — apagar um ativo **destrói silenciosamente** posições, transações, proventos e histórico vinculados. Isso é uma **perda irreversível de dados financeiros**.

---

### 1.3 — Query duplicada no login

`auth/routes.py` faz uma segunda query desnecessária ao banco após `AuthService.login()`:

```python
# auth/routes.py:41-54
tokens = AuthService.login(...)  # já autentica e carrega o usuário internamente

# Query redundante — usuário já foi buscado dentro do AuthService
user = Usuario.query.filter_by(username=validated_data['username']).first()
```

**Impacto:** 2 queries ao banco por login. `AuthService` deveria retornar o usuário autenticado diretamente.

---

## 2. Escopo de Arquivos Afetados

### Services com `ValueError` dual (10 arquivos):

| Arquivo | Casos ValueError | Tipos misturados |
|---|---|---|
| `ativo_service.py` | 3 | 404 + 409 |
| `usuario_service.py` | 5 | 404 + 409 + 400 + 403 |
| `corretora_service.py` | 3 | 404 + 409 |
| `transacao_service.py` | 5 | 404 + 400 |
| `provento_service.py` | 3 | 404 |
| `feriado_mercado_service.py` | 2 | 404 |
| `regra_fiscal_service.py` | 2 | 404 |
| `evento_corporativo_service.py` | 3 | 404 |
| `relatorio_service.py` | 2 | 404 |
| `movimentacao_caixa_service.py` | 1 | 404 |
| `buy_signals_service.py` | 2 | 404 + 400 |

**Total:** ~31 ocorrências de `ValueError` com semânticas mistas.

### Services com `delete()` sem validação de integridade:

| Service | Entidade | Dependentes em cascata |
|---|---|---|
| `AtivoService.delete()` | `ativo` | `posicao`, `transacao`, `provento`, `historico_preco`, `alerta` |
| `CorretoraService.delete()` | `corretora` | `transacao`, `posicao`, `movimentacao_caixa` |
| `UsuarioService.delete()` | `usuario` | tudo (CASCADE total) |
| `ProventoService.delete()` | `provento` | `movimentacao_caixa` |
| `EventoCorporativoService.delete()` | `evento_corporativo` | — |

---

## 3. Solução Proposta

### 3.1 — Criar hierarquia de exceções tipadas em `app/utils/exceptions.py`

```python
# app/utils/exceptions.py (arquivo novo)

class ExitusError(Exception):
    """Exceção base do sistema Exitus."""
    http_status = 500

class NotFoundError(ExitusError):
    """Recurso não encontrado — HTTP 404."""
    http_status = 404

class ConflictError(ExitusError):
    """Conflito de unicidade — HTTP 409."""
    http_status = 409

class ForbiddenError(ExitusError):
    """Acesso negado — HTTP 403."""
    http_status = 403

class BusinessRuleError(ExitusError):
    """Violação de regra de negócio — HTTP 422."""
    http_status = 422
```

### 3.2 — Substituir `ValueError` nos services

```python
# ANTES
raise ValueError("Ativo não encontrado")
raise ValueError("Ativo já existe no mercado")

# DEPOIS
from app.utils.exceptions import NotFoundError, ConflictError
raise NotFoundError("Ativo não encontrado")
raise ConflictError(f"Ativo {ticker} já existe no mercado {mercado}")
```

### 3.3 — Handler genérico nos blueprints (ou `app/__init__.py`)

```python
# app/__init__.py — register_error_handlers(app)
from app.utils.exceptions import ExitusError

@app.errorhandler(ExitusError)
def handle_exitus_error(e):
    return error(str(e), e.http_status)
```

Ou por blueprint, usando `except ExitusError as e: return error(str(e), e.http_status)`.

### 3.4 — Adicionar validação de integridade no `delete()`

```python
# AtivoService.delete() — padrão a replicar nos demais
@staticmethod
def delete(ativo_id):
    ativo = db.session.get(Ativo, ativo_id)
    if not ativo:
        raise NotFoundError("Ativo não encontrado")

    # Verificar dependências antes de deletar
    from app.models.transacao import Transacao
    from app.models.posicao import Posicao
    tem_transacoes = Transacao.query.filter_by(ativo_id=ativo_id).count() > 0
    tem_posicoes   = Posicao.query.filter_by(ativo_id=ativo_id).count() > 0

    if tem_transacoes or tem_posicoes:
        raise ConflictError(
            f"Ativo {ativo.ticker} possui transações/posições vinculadas. "
            "Desative o ativo (ativo=False) em vez de deletar."
        )

    safe_delete_commit(ativo)
    return True
```

### 3.5 — Corrigir query duplicada no login

```python
# AuthService.login() deve retornar o usuário junto com os tokens
# auth/routes.py usa diretamente o retorno do service, sem nova query
```

---

## 4. Plano de Implementação

### Fase A — Fundação (sem quebra de contrato)
1. Criar `app/utils/exceptions.py` com a hierarquia de exceções
2. Criar handler de erro genérico em `app/__init__.py`
3. Escrever testes unitários para as novas exceções

### Fase B — Substituição nos services (10 arquivos)
4. `ativo_service.py` — substituir ValueError + adicionar validação de delete
5. `usuario_service.py` — substituir ValueError
6. `corretora_service.py` — substituir ValueError + validação de delete
7. `transacao_service.py` — substituir ValueError
8. `provento_service.py` — substituir ValueError + validação de delete
9. `feriado_mercado_service.py`, `regra_fiscal_service.py`, `evento_corporativo_service.py`, `relatorio_service.py`, `movimentacao_caixa_service.py` — substituir ValueError

### Fase C — Correções pontuais
10. Corrigir query duplicada em `auth/routes.py`
11. Atualizar testes de integração para usar status codes corretos (404, 409)

### Fase D — Verificação
12. Rodar suite completa de testes (69 testes devem continuar passando)
13. Verificar que nenhum endpoint existente quebrou

---

## 5. Critérios de Aceite

- [ ] `GET/PUT/DELETE /<id>` com ID inexistente retorna **404**, não 400
- [ ] `POST` com ticker/email duplicado retorna **409**, não 400
- [ ] `DELETE` de ativo com transações retorna **409** com mensagem clara
- [ ] `DELETE` de ativo sem dependências continua funcionando normalmente
- [ ] Login retorna dados do usuário sem query duplicada
- [ ] 69 testes existentes continuam passando
- [ ] Novos testes cobrem os cenários de 404 e 409

---

## 6. Impacto nos Testes Existentes

Os testes atuais aceitam 400 onde deveriam receber 404. Após a implementação, precisam ser atualizados:

```python
# test_ativos_integration.py — ANTES
assert response.status_code in (400, 404)  # 400 aceito como workaround

# DEPOIS
assert response.status_code == 404  # 404 correto e garantido
```

---

## 7. Relação com Outros GAPs

| GAP | Relação |
|---|---|
| **EXITUS-SQLALCHEMY-002** | Implementar junto: trocar `Query.get()` → `db.session.get()` no mesmo passe |
| **EXITUS-TESTS-001** | Base de testes que valida as correções |
| **EXITUS-SWAGGER-001** | Documentar os novos status codes 404/409 no OpenAPI |
