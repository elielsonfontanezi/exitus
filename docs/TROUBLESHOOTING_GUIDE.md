# 🔧 GUIA DE TROUBLESHOOTING - SISTEMA EXITUS

**Sistema Exitus - Soluções para Problemas Comuns**  
**Data:** 13/12/2025  
**Versão:** 1.0

---

## 🎯 COMO USAR ESTE GUIA

1. Use **Ctrl+F** para buscar a mensagem de erro
2. Cada seção tem:
   - ❌ **Erro**: Mensagem que você vê
   - 🔍 **Causa**: Por que acontece
   - ✅ **Solução**: Código/comando para corrigir
   - 📝 **Prevenção**: Como evitar no futuro

---

## 📦 CATEGORIA: SERIALIZAÇÃO JSON

### ❌ Erro: "Object of type Decimal is not JSON serializable"

**Mensagem Completa:**
```
TypeError: Object of type Decimal is not JSON serializable
```

**🔍 Causa:**
PostgreSQL retorna valores `NUMERIC(15,2)` como `Decimal` do Python. O Flask por padrão não sabe serializar `Decimal` para JSON.

**✅ Solução:**
```python
# backend/app/__init__.py
from flask.json.provider import DefaultJSONProvider
from decimal import Decimal

class DecimalJSONProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

# Registrar no app
app.json = DecimalJSONProvider(app)
```

**📝 Prevenção:**
- Sempre adicionar este provider ao criar novos apps Flask
- Considerar usar `Float` no schema Marshmallow para forçar conversão

---

### ❌ Erro: "Object of type UUID is not JSON serializable"

**🔍 Causa:**
UUIDs do PostgreSQL não são JSON-serializáveis por padrão.

**✅ Solução:**
```python
# Adicionar ao DecimalJSONProvider
from uuid import UUID

class DecimalJSONProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, UUID):
            return str(obj)
        return super().default(obj)
```

**📝 Prevenção:**
- Usar `fields.Str()` para UUIDs nos schemas Marshmallow
- Converter UUIDs para string antes de retornar

---

### ❌ Erro: "Object of type datetime is not JSON serializable"

**✅ Solução:**
```python
from datetime import datetime, date

class DecimalJSONProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)
```

---

## 🔀 CATEGORIA: ROTAS E REDIRECIONAMENTO

### ❌ Erro: 308 Permanent Redirect

**Mensagem:**
```
curl http://localhost:5000/api/posicoes
< HTTP/1.1 308 PERMANENT REDIRECT
< Location: http://localhost:5000/api/posicoes/
```

**🔍 Causa:**
Flask redireciona `/api/posicoes` para `/api/posicoes/` (com barra final) quando `strict_slashes=True` (padrão).

**✅ Solução:**
```python
# Em TODOS os blueprints
@posicao_bp.route('/', methods=['GET'], strict_slashes=False)
@posicao_bp.route('', methods=['GET'], strict_slashes=False)
def listar_posicoes():
    # ...
```

**📝 Prevenção:**
- Sempre usar `strict_slashes=False` em todas as rotas
- Declarar ambas as variações (`'/'` e `''`)

---

### ❌ Erro: 404 Not Found (Blueprint não registrado)

**Mensagem:**
```html
<!doctype html>
<html lang=en>
<title>404 Not Found</title>
```

**🔍 Causa:**
Blueprint criado mas não registrado em `app/__init__.py`.

**✅ Solução:**
```python
# backend/app/__init__.py
from flask import Flask

def create_app():
    app = Flask(__name__)

    # ... configurações ...

    # REGISTRAR TODOS OS BLUEPRINTS
    from .blueprints.auth_blueprint import auth_bp
    from .blueprints.usuario_blueprint import usuario_bp
    from .blueprints.corretora_blueprint import corretora_bp
    from .blueprints.ativo_blueprint import ativo_bp
    from .blueprints.transacao_blueprint import transacao_bp
    from .blueprints.posicao_blueprint import posicao_bp
    from .blueprints.movimentacao_blueprint import movimentacao_bp
    from .blueprints.portfolio_blueprint import portfolio_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(usuario_bp)
    app.register_blueprint(corretora_bp)
    app.register_blueprint(ativo_bp)
    app.register_blueprint(transacao_bp)
    app.register_blueprint(posicao_bp)
    app.register_blueprint(movimentacao_bp)
    app.register_blueprint(portfolio_bp)

    return app
```

**📝 Prevenção:**
- Criar checklist de registro ao criar novo blueprint
- Adicionar teste básico `GET /api/{recurso}` após criar rota

---

## 📋 CATEGORIA: SCHEMAS E VALIDAÇÃO

### ❌ Erro: "Unknown field" (Marshmallow)

**Mensagem:**
```json
{
  "error": {
    "moeda": ["Unknown field."]
  },
  "success": false
}
```

**🔍 Causa:**
Campo enviado no JSON não existe no schema Marshmallow.

**✅ Solução:**
```python
# backend/app/schemas/movimentacao_caixa_schema.py
class MovimentacaoCaixaCreateSchema(Schema):
    corretora_id = fields.Str(required=True)
    tipo_movimentacao = fields.Str(required=True)
    valor = fields.Float(required=True)
    data_movimentacao = fields.Date(required=True)
    moeda = fields.Str(load_default="BRL")  # ← ADICIONAR CAMPO
    descricao = fields.Str(load_default="")
```

**📝 Prevenção:**
- Sincronizar schemas com models
- Usar `unknown=EXCLUDE` para ignorar campos extras (não recomendado)

---

### ❌ Erro: "DetachedInstanceError" (SQLAlchemy)

**Mensagem:**
```
sqlalchemy.orm.exc.DetachedInstanceError: Instance <Posicao at 0x...> is not bound to a Session
```

**🔍 Causa:**
Tentar acessar relacionamento (`posicao.ativo`) após fechar a sessão ou sem `joinedload`.

**✅ Solução:**
```python
# OPÇÃO 1: Usar joinedload (RECOMENDADO)
from sqlalchemy.orm import joinedload

posicoes = Posicao.query.filter_by(usuario_id=usuario_id) \
    .options(joinedload(Posicao.ativo), joinedload(Posicao.corretora)) \
    .all()

# OPÇÃO 2: Schemas explícitos (evitar lazy loading)
class PosicaoResponseSchema(Schema):
    id = fields.Str()
    ativo_id = fields.Str()  # Não acessar posicao.ativo.nome
    quantidade = fields.Float()
```

**📝 Prevenção:**
- Nunca usar `SQLAlchemyAutoSchema` para evitar lazy loading
- Sempre usar `joinedload` quando precisar de relacionamentos

---

## 🗄️ CATEGORIA: BANCO DE DADOS

### ❌ Erro: "Table 'usuarios' does not exist" (Plural inesperado)

**🔍 Causa:**
SQLAlchemy pluraliza automaticamente `__tablename__` se não for explícito. `Usuario` vira `usuarios`, mas a tabela real é `usuario` (singular).

**✅ Solução:**
```python
# backend/app/models/usuario.py
class Usuario(db.Model):
    __tablename__ = 'usuario'  # ✅ SEMPRE EXPLÍCITO E SINGULAR

    id = db.Column(UUID(as_uuid=True), primary_key=True)
    # ...
```

**📝 Prevenção:**
- **REGRA DE OURO:** Sempre declarar `__tablename__` explicitamente
- Usar singular em todos os models (padrão Exitus)
- Verificar `exitus_db_structure.txt` para confirmar nome real

---

### ❌ Erro: "relation does not exist" após migration

**Mensagem:**
```
psycopg2.errors.UndefinedTable: relation "posicao" does not exist
```

**🔍 Causa:**
Migration gerada mas não aplicada no banco.

**✅ Solução:**
```bash
# Verificar migrations pendentes
podman exec -it exitus-backend bash -c "cd /app && alembic current"
podman exec -it exitus-backend bash -c "cd /app && alembic history"

# Aplicar migrations
podman exec -it exitus-backend bash -c "cd /app && alembic upgrade head"

# Se necessário, resetar banco
podman exec -it exitus-db psql -U exitus -d exitusdb -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
podman exec -it exitus-backend bash -c "cd /app && alembic upgrade head"
podman exec -it exitus-backend bash -c "cd /app && python -c 'from app.seeds import seed_all; seed_all()'"
```

**📝 Prevenção:**
- Sempre rodar `alembic upgrade head` após gerar migration
- Adicionar ao script `rebuild_restart_exitus-backend.sh`

---

## 🔐 CATEGORIA: AUTENTICAÇÃO JWT

### ❌ Erro: "Token has expired"

**Mensagem:**
```json
{
  "msg": "Token has expired"
}
```

**✅ Solução:**
```bash
# Gerar novo token
export TOKEN=$(curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' | \
  jq -r '.data.access_token')

# Verificar
echo $TOKEN
```

**📝 Prevenção:**
- Aumentar `JWT_ACCESS_TOKEN_EXPIRES` em `.env` (padrão: 1 hora)
- Implementar refresh token

---

### ❌ Erro: 401 Unauthorized (Token ausente)

**🔍 Causa:**
Requisição sem header `Authorization`.

**✅ Solução:**
```bash
# CORRETO
curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/posicoes

# ERRADO (sem header)
curl http://localhost:5000/api/posicoes
```

---

## 🐳 CATEGORIA: CONTAINERS PODMAN

### ❌ Erro: "Connection refused" ao acessar API

**🔍 Causa:**
Container backend não está rodando ou não expôs porta 5000.

**✅ Solução:**
```bash
# Verificar status
podman ps | grep exitus-backend

# Se não estiver rodando
podman start exitus-backend

# Ver logs
podman logs exitus-backend --tail 50

# Rebuild se necessário
./scripts/rebuild_restart_exitus-backend.sh
```

**📝 Prevenção:**
- Adicionar healthcheck no Dockerfile
- Usar `restart=always` em produção

---

### ❌ Erro: "Address already in use" ao iniciar container

**Mensagem:**
```
Error: cannot listen on the TCP port: listen tcp4 :5000: bind: address already in use
```

**✅ Solução:**
```bash
# Verificar o que está usando a porta 5000
sudo lsof -i :5000

# Parar container antigo
podman stop exitus-backend
podman rm exitus-backend

# Ou mudar porta
podman run -p 5001:5000 ...
```

---

## 🧪 CATEGORIA: TESTES

### ❌ Erro: AssertionError em testes

**Mensagem:**
```
AssertionError: Esperado 2, Encontrado 0. IDs procurados: uuid1, uuid2
```

**🔍 Causa:**
Posições não foram calculadas após criar transações.

**✅ Solução:**
```python
# Adicionar recálculo explícito no teste
resp = requests.post(f"{BASE_URL}/posicoes/calcular", headers=headers)
assert resp.status_code == 200, f"Recálculo falhou: {resp.text}"

# Agora sim, verificar posições
resp = requests.get(f"{BASE_URL}/posicoes", headers=headers)
posicoes = resp.json()['data']['posicoes']
```

**📝 Prevenção:**
- Sempre chamar `/posicoes/calcular` após criar/atualizar transações
- Considerar trigger automático no futuro

---

## 📊 CATEGORIA: PERFORMANCE

### ❌ Erro: Consulta lenta (N+1 queries)

**🔍 Causa:**
Acessar relacionamentos sem `joinedload` causa uma query por item.

**✅ Solução:**
```python
# LENTO (N+1)
posicoes = Posicao.query.filter_by(usuario_id=usuario_id).all()
for p in posicoes:
    print(p.ativo.ticker)  # Query extra para cada posição

# RÁPIDO (1 query)
from sqlalchemy.orm import joinedload

posicoes = Posicao.query.filter_by(usuario_id=usuario_id) \
    .options(joinedload(Posicao.ativo)) \
    .all()
for p in posicoes:
    print(p.ativo.ticker)  # Sem query extra
```

---

## 🔍 CATEGORIA: DEBUGGING

### Como Ver Logs do Backend

```bash
# Logs em tempo real
podman logs -f exitus-backend

# Últimas 100 linhas
podman logs exitus-backend --tail 100

# Logs com timestamp
podman logs exitus-backend --timestamps

# Exportar logs
podman logs exitus-backend > backend_logs.txt
```

---

### Como Acessar PostgreSQL Diretamente

```bash
# Conectar ao psql
podman exec -it exitus-db psql -U exitus -d exitusdb

# Comandos úteis
\dt                    # Listar tabelas
\d+ posicao            # Estrutura da tabela posicao
SELECT * FROM posicao;  # Ver dados

# Contar registros
SELECT COUNT(*) FROM transacao WHERE usuario_id = 'uuid-aqui';
```

---

### Como Testar Endpoint Manualmente

```bash
# 1. Login
TOKEN=$(curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' | \
  jq -r '.data.access_token')

# 2. Testar endpoint
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/posicoes | jq .

# 3. Ver status code
curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/posicoes
```

---

## 📚 REFERÊNCIAS RÁPIDAS

### Comandos Essenciais

```bash
# Containers
podman ps                                    # Listar containers rodando
podman start exitus-backend                  # Iniciar container
podman restart exitus-backend                # Reiniciar container
podman logs -f exitus-backend                # Ver logs

# Banco de Dados
podman exec -it exitus-db psql -U exitus -d exitusdb
./scripts/exitus_db_doc.sh                   # Gerar docs do banco

# Migrations
podman exec -it exitus-backend bash -c "cd /app && alembic upgrade head"
podman exec -it exitus-backend bash -c "cd /app && alembic revision --autogenerate -m 'msg'"

# Testes
pytest backend/tests/ -v -s
pytest backend/tests/test_posicao.py::test_nome -v -s

# API
export TOKEN=$(curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' | \
  jq -r '.data.access_token')
```

---

## 🆘 QUANDO TUDO FALHA

### Reset Completo do Sistema

```bash
# 1. Parar tudo
podman stop exitus-backend exitus-frontend exitus-db

# 2. Remover containers
podman rm exitus-backend exitus-frontend exitus-db

# 3. Resetar banco
podman volume rm exitus-db-data

# 4. Rebuild tudo
./scripts/rebuild_restart_exitus-backend.sh
./scripts/rebuild_restart_exitus-frontend.sh

# 5. Seeds
podman exec -it exitus-backend bash -c "cd /app && python -c 'from app.seeds import seed_all; seed_all()'"
```

---

## 📞 PRECISA DE MAIS AJUDA?

Se o erro não está aqui:

1. Verifique logs: `podman logs exitus-backend --tail 100`
2. Consulte `docs/EXITUS_DB_STRUCTURE.txt` para estrutura do banco
3. Veja `docs/API_REFERENCE_COMPLETE.md` para endpoints disponíveis
4. Revise commit do Git onde funcionava: `git log --oneline`

---

**Última Atualização:** 13/12/2025  
**Versão:** 1.0  
**Mantenedor:** Elielson
