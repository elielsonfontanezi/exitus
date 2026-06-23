# Dashboard Admin — Gestão de Assessoras

> **Status:** ✅ Implementado (03/04/2026)  
> **GAP:** MULTICLIENTE-001 Parte 6 - Dashboard Admin  
> **Modelo IA:** Claude Sonnet  
> **Acesso:** Apenas usuários com `role=admin`

---

## 🎯 Objetivo

Fornecer interface administrativa para gestão completa de assessoras no sistema Exitus, permitindo CRUD, visualização de métricas e controle de limites.

---

## 🔐 Controle de Acesso

**Permissão:** Apenas usuários com `role=admin` podem acessar os endpoints de assessoras.

**Validação:**
```python
jwt_data = get_jwt()
role = jwt_data.get('role', 'user')

if role != 'admin':
    return error('Acesso negado. Apenas administradores.', 403)
```

---

## 📡 Endpoints API

### **GET /api/assessoras**
Lista todas as assessoras (paginado)

**Query params:**
- `page` (int): Página atual (default: 1)
- `per_page` (int): Registros por página (default: 20)
- `ativo` (string): Filtrar por status ("true", "false", null = todos)

**Response 200:**
```json
{
  "success": true,
  "message": "Assessoras listadas com sucesso",
  "data": {
    "items": [
      {
        "id": "23c54cb4-cb0a-438f-b985-def21d70904e",
        "nome": "Assessora XYZ",
        "razao_social": "Assessora XYZ Ltda",
        "cnpj": "12345678000199",
        "email": "contato@assessora.com",
        "ativo": true,
        "plano": "profissional",
        "max_usuarios": 50,
        "max_portfolios": 100,
        "total_usuarios": 15,
        "total_portfolios": 45
      }
    ],
    "total": 10,
    "page": 1,
    "per_page": 20
  }
}
```

---

### **GET /api/assessoras/:id**
Busca assessora por ID

**Response 200:**
```json
{
  "success": true,
  "message": "Assessora encontrada",
  "data": {
    "id": "23c54cb4-cb0a-438f-b985-def21d70904e",
    "nome": "Assessora XYZ",
    "razao_social": "Assessora XYZ Ltda",
    "cnpj": "12345678000199",
    "email": "contato@assessora.com",
    "telefone": "11999999999",
    "ativo": true,
    "plano": "profissional",
    "max_usuarios": 50,
    "max_portfolios": 100,
    "created_at": "2026-03-16T15:40:00Z"
  }
}
```

---

### **POST /api/assessoras**
Cria nova assessora

**Body (required):**
```json
{
  "nome": "Nova Assessora",
  "razao_social": "Nova Assessora Ltda",
  "cnpj": "99888777000166",
  "email": "nova@assessora.com",
  "telefone": "11988887777",
  "plano": "profissional",
  "max_usuarios": 50,
  "max_portfolios": 100
}
```

**Response 201:**
```json
{
  "success": true,
  "message": "Assessora criada com sucesso",
  "data": {
    "id": "8f9a2b1c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
    "nome": "Nova Assessora",
    "ativo": true
  }
}
```

**Validações:**
- `nome`, `razao_social`, `cnpj`, `email` são obrigatórios
- CNPJ deve ser único
- Email deve ser único
- CNPJ deve ter 14 dígitos

---

### **PUT /api/assessoras/:id**
Atualiza assessora existente

**Body (todos opcionais):**
```json
{
  "nome": "Nome Atualizado",
  "plano": "enterprise",
  "max_usuarios": 100,
  "ativo": true
}
```

**Response 200:**
```json
{
  "success": true,
  "message": "Assessora atualizada com sucesso",
  "data": { ... }
}
```

---

### **DELETE /api/assessoras/:id**
Deleta assessora (soft delete por padrão)

**Query params:**
- `hard` (boolean): Se true, deleta fisicamente (default: false)

**Response 200:**
```json
{
  "success": true,
  "message": "Assessora deletada (desativada) com sucesso"
}
```

**Soft delete:** Define `ativo=false` (recomendado)  
**Hard delete:** Deleta fisicamente (CASCADE), apenas se não houver usuários ativos

---

### **GET /api/assessoras/:id/stats**
Retorna métricas da assessora

**Response 200:**
```json
{
  "success": true,
  "message": "Métricas obtidas com sucesso",
  "data": {
    "assessora_id": "23c54cb4-cb0a-438f-b985-def21d70904e",
    "nome": "Assessora XYZ",
    "ativo": true,
    "plano": "profissional",
    "total_usuarios": 15,
    "usuarios_ativos": 12,
    "total_portfolios": 45,
    "portfolios_ativos": 40,
    "total_transacoes": 1250,
    "volume_total": 2500000.50,
    "max_usuarios": 50,
    "max_portfolios": 100,
    "pode_adicionar_usuario": true,
    "pode_adicionar_portfolio": true
  }
}
```

---

### **POST /api/assessoras/:id/toggle**
Ativa/desativa assessora

**Response 200:**
```json
{
  "success": true,
  "message": "Assessora desativada com sucesso",
  "data": {
    "id": "23c54cb4-cb0a-438f-b985-def21d70904e",
    "ativo": false
  }
}
```

---

## 🧪 Testes

**Arquivo:** `backend/tests/test_assessora_crud.py`

**11 testes implementados:**
1. ✅ `test_list_assessoras_admin` — Admin pode listar
2. ✅ `test_list_assessoras_sem_auth` — Sem auth retorna 401
3. ✅ `test_create_assessora_admin` — Admin pode criar
4. ✅ `test_create_assessora_cnpj_duplicado` — Valida CNPJ único
5. ✅ `test_get_assessora_by_id` — Busca por ID
6. ✅ `test_update_assessora` — Admin pode atualizar
7. ✅ `test_delete_assessora_soft` — Soft delete funciona
8. ✅ `test_get_assessora_stats` — Métricas corretas
9. ✅ `test_toggle_assessora_ativo` — Toggle ativo/inativo
10. ✅ `test_create_assessora_campos_obrigatorios` — Valida campos required
11. ✅ Validação de permissões admin

---

## 📊 Planos Disponíveis

| Plano | max_usuarios | max_portfolios | Características |
|-------|--------------|----------------|-----------------|
| **basico** | 10 | 20 | Ideal para assessoras pequenas |
| **profissional** | 50 | 100 | Assessoras médias |
| **enterprise** | ilimitado | ilimitado | Assessoras grandes |

---

## 🔧 Comandos Úteis

```bash
# Listar assessoras via API
curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/assessoras

# Criar assessora
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nome":"Nova","razao_social":"Nova Ltda","cnpj":"12345678000199","email":"nova@teste.com"}' \
  http://localhost:5000/api/assessoras

# Obter métricas
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/assessoras/23c54cb4-cb0a-438f-b985-def21d70904e/stats

# Verificar assessoras no banco
podman exec exitus-db psql -U exitus -d exitusdb -c "SELECT id, nome, ativo, plano FROM assessora;"
```

---

## 🎨 Frontend (Futuro)

**Planejado para próxima fase:**
- Tela de listagem com tabela paginada
- Formulário de criação/edição
- Dashboard de métricas por assessora
- Gráficos de uso (usuários, portfolios, volume)
- Gestão de limites e planos

**Stack sugerido:** Alpine.js + Fetch API (consistente com Sprint 1)

---

## 📝 Arquivos Implementados

| Arquivo | Linhas | Descrição |
|---------|--------|-----------|
| `backend/app/services/assessora_service.py` | 257 | Service CRUD completo |
| `backend/app/schemas/assessora_schema.py` | 127 | Validação Marshmallow |
| `backend/app/blueprints/assessora_blueprint.py` | 282 | Endpoints REST |
| `backend/tests/test_assessora_crud.py` | 224 | Suite de testes |
| `backend/app/__init__.py` | +8 | Registro do blueprint |

**Total:** 898 linhas de código + testes

---

## 🔒 Segurança

**Validações implementadas:**
- ✅ Apenas admin pode acessar endpoints
- ✅ CNPJ único validado
- ✅ Email único validado
- ✅ Soft delete por padrão (preserva dados)
- ✅ Hard delete apenas se sem usuários ativos
- ✅ Validação de campos obrigatórios
- ✅ Validação de formato (CNPJ, email, cores)

---

*Última atualização: 03/04/2026*  
*Modelo IA utilizado: Claude Sonnet*  
*Status: ✅ Backend completo, Frontend pendente*
