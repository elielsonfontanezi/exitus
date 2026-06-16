# Planos de Assessoras — Sistema Exitus

> **Data:** 03/04/2026  
> **Status:** ✅ Implementado  
> **GAP:** MULTICLIENTE-001 Parte 6  
> **Modelo:** 3 planos (básico, profissional, enterprise)

---

## 🎯 Objetivo

Definir limites e características de cada plano de assessora no sistema Exitus, permitindo escalabilidade e controle de uso por tipo de cliente.

---

## 📊 Planos Disponíveis

### **1. Plano Básico**

**Código:** `basico`

**Limites:**
- **max_usuarios:** 10 usuários
- **max_portfolios:** 20 portfolios

**Características:**
- ✅ Acesso completo ao sistema
- ✅ Gestão de portfolios e transações
- ✅ Relatórios básicos
- ✅ Cálculo de IR automático
- ✅ Importação B3
- ⚠️ Limite de 10 usuários
- ⚠️ Limite de 20 portfolios

**Ideal para:**
- Assessoras pequenas
- Escritórios iniciantes
- Até 10 clientes

**Preço sugerido:** R$ 299/mês

---

### **2. Plano Profissional**

**Código:** `profissional`

**Limites:**
- **max_usuarios:** 50 usuários
- **max_portfolios:** 100 portfolios

**Características:**
- ✅ Tudo do plano básico
- ✅ Até 50 usuários
- ✅ Até 100 portfolios
- ✅ Relatórios avançados
- ✅ Exportação completa (CSV, Excel, PDF)
- ✅ API de integração
- ✅ Suporte prioritário

**Ideal para:**
- Assessoras médias
- Escritórios estabelecidos
- 10-50 clientes

**Preço sugerido:** R$ 999/mês

---

### **3. Plano Enterprise**

**Código:** `enterprise`

**Limites:**
- **max_usuarios:** `null` (ilimitado)
- **max_portfolios:** `null` (ilimitado)

**Características:**
- ✅ Tudo do plano profissional
- ✅ Usuários ilimitados
- ✅ Portfolios ilimitados
- ✅ Customização de marca (logo, cores)
- ✅ White-label (opcional)
- ✅ SLA garantido
- ✅ Suporte dedicado
- ✅ Treinamento personalizado
- ✅ Integração customizada

**Ideal para:**
- Assessoras grandes
- Instituições financeiras
- 50+ clientes
- Multi-escritórios

**Preço sugerido:** Sob consulta (R$ 2.999+/mês)

---

## 🔧 Implementação Técnica

### **Model Assessora**

```python
class Assessora(db.Model):
    # ...
    max_usuarios = db.Column(db.Integer, nullable=True)
    max_portfolios = db.Column(db.Integer, nullable=True)
    plano = db.Column(db.String(20), default='basico')
    
    @property
    def pode_adicionar_usuario(self):
        if self.max_usuarios is None:
            return True  # Enterprise ilimitado
        return self.total_usuarios < self.max_usuarios
    
    @property
    def pode_adicionar_portfolio(self):
        if self.max_portfolios is None:
            return True  # Enterprise ilimitado
        return self.total_portfolios < self.max_portfolios
```

### **Validação no Service**

```python
# Ao criar usuário
assessora = Assessora.query.get(assessora_id)
if not assessora.pode_adicionar_usuario:
    raise ValidationError(
        f"Limite de usuários atingido ({assessora.max_usuarios}). "
        f"Faça upgrade do plano."
    )

# Ao criar portfolio
if not assessora.pode_adicionar_portfolio:
    raise ValidationError(
        f"Limite de portfolios atingido ({assessora.max_portfolios}). "
        f"Faça upgrade do plano."
    )
```

---

## 📈 Comparativo de Planos

| Recurso | Básico | Profissional | Enterprise |
|---------|--------|--------------|------------|
| **Usuários** | 10 | 50 | Ilimitado |
| **Portfolios** | 20 | 100 | Ilimitado |
| **Transações** | Ilimitado | Ilimitado | Ilimitado |
| **Importação B3** | ✅ | ✅ | ✅ |
| **Cálculo IR** | ✅ | ✅ | ✅ |
| **Relatórios Básicos** | ✅ | ✅ | ✅ |
| **Relatórios Avançados** | ❌ | ✅ | ✅ |
| **Exportação** | CSV | CSV, Excel, PDF | CSV, Excel, PDF, API |
| **API Integração** | ❌ | ✅ | ✅ |
| **Customização Marca** | ❌ | ❌ | ✅ |
| **White-label** | ❌ | ❌ | ✅ (opcional) |
| **Suporte** | Email | Prioritário | Dedicado |
| **SLA** | - | - | 99.9% |
| **Treinamento** | Docs | Webinar | Personalizado |

---

## 🚀 Upgrade de Plano

### **Fluxo de Upgrade**

1. **Admin acessa** `/api/assessoras/:id`
2. **Atualiza plano** via `PUT /api/assessoras/:id`
   ```json
   {
     "plano": "profissional",
     "max_usuarios": 50,
     "max_portfolios": 100
   }
   ```
3. **Sistema valida** e atualiza limites
4. **Assessora pode** adicionar mais usuários/portfolios

### **Downgrade de Plano**

⚠️ **Atenção:** Ao fazer downgrade, verificar se:
- Total de usuários <= novo limite
- Total de portfolios <= novo limite

Se exceder, avisar admin para:
1. Desativar usuários excedentes
2. Desativar portfolios excedentes
3. Ou manter plano atual

---

## 💰 Modelo de Precificação

### **Básico — R$ 299/mês**
- R$ 29,90 por usuário (10 usuários)
- Ideal para começar

### **Profissional — R$ 999/mês**
- R$ 19,98 por usuário (50 usuários)
- Melhor custo-benefício

### **Enterprise — Sob consulta**
- A partir de R$ 2.999/mês
- Preço customizado por volume
- Desconto para contratos anuais

---

## 📊 Métricas por Plano

### **Endpoint de Estatísticas**

`GET /api/assessoras/:id/stats`

```json
{
  "assessora_id": "23c54cb4-cb0a-438f-b985-def21d70904e",
  "nome": "Assessora XYZ",
  "plano": "profissional",
  "max_usuarios": 50,
  "total_usuarios": 32,
  "usuarios_ativos": 28,
  "pode_adicionar_usuario": true,
  "max_portfolios": 100,
  "total_portfolios": 75,
  "portfolios_ativos": 68,
  "pode_adicionar_portfolio": true,
  "total_transacoes": 1250,
  "volume_total": 2500000.50
}
```

### **Indicadores de Uso**

- **Taxa de ocupação usuários:** `total_usuarios / max_usuarios * 100`
- **Taxa de ocupação portfolios:** `total_portfolios / max_portfolios * 100`
- **Alerta upgrade:** Se ocupação > 80%, sugerir upgrade

---

## 🔄 Migração de Planos

### **Assessoras Existentes**

Ao implementar sistema de planos:

1. **Assessoras sem plano definido** → `plano = 'basico'`
2. **Assessoras com muitos usuários** → Upgrade automático para `profissional`
3. **Assessoras com 50+ usuários** → Upgrade automático para `enterprise`

### **Script de Migração**

```python
# Atualizar planos baseado em uso atual
for assessora in Assessora.query.all():
    if assessora.plano is None:
        if assessora.total_usuarios > 50:
            assessora.plano = 'enterprise'
            assessora.max_usuarios = None
            assessora.max_portfolios = None
        elif assessora.total_usuarios > 10:
            assessora.plano = 'profissional'
            assessora.max_usuarios = 50
            assessora.max_portfolios = 100
        else:
            assessora.plano = 'basico'
            assessora.max_usuarios = 10
            assessora.max_portfolios = 20
        
        db.session.commit()
```

---

## 🎨 Interface Admin (Futuro)

### **Dashboard de Planos**

**Tela sugerida:**
```
┌─────────────────────────────────────────────────┐
│  Assessora XYZ - Plano Profissional            │
├─────────────────────────────────────────────────┤
│  Usuários: 32/50 (64% ocupado) ████████░░       │
│  Portfolios: 75/100 (75% ocupado) ███████░░░    │
│  Volume: R$ 2.500.000,50                        │
│                                                  │
│  [Fazer Upgrade para Enterprise]                │
└─────────────────────────────────────────────────┘
```

---

## 📝 Comandos Úteis

```bash
# Listar assessoras por plano
podman exec exitus-db psql -U exitus -d exitusdb -c "
  SELECT plano, COUNT(*) as total, 
         SUM(CASE WHEN ativo THEN 1 ELSE 0 END) as ativos
  FROM assessora 
  GROUP BY plano;
"

# Assessoras próximas do limite
podman exec exitus-db psql -U exitus -d exitusdb -c "
  SELECT a.nome, a.plano, 
         COUNT(DISTINCT u.id) as usuarios,
         a.max_usuarios,
         COUNT(DISTINCT p.id) as portfolios,
         a.max_portfolios
  FROM assessora a
  LEFT JOIN usuario u ON u.assessora_id = a.id
  LEFT JOIN portfolio p ON p.assessora_id = a.id
  WHERE a.max_usuarios IS NOT NULL
  GROUP BY a.id
  HAVING COUNT(DISTINCT u.id) >= a.max_usuarios * 0.8;
"
```

---

## 🔮 Roadmap Futuro

### **Fase 1 (Atual)** ✅
- [x] Definição de 3 planos
- [x] Limites por plano
- [x] Validação de limites
- [x] API de gestão

### **Fase 2 (Próxima)**
- [ ] Interface admin de planos
- [ ] Alertas de limite próximo
- [ ] Sugestão automática de upgrade
- [ ] Histórico de mudanças de plano

### **Fase 3 (Futuro)**
- [ ] Billing automático
- [ ] Integração com gateway de pagamento
- [ ] Trial gratuito (14 dias)
- [ ] Planos customizados

---

*Última atualização: 03/04/2026*  
*Modelo IA utilizado: Claude Sonnet*  
*Status: ✅ Implementado (backend), Interface admin pendente*
