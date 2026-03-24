# 📊 Dívida Técnica: Histórico Patrimonial - Processo Agendado

> **Status:** 🔄 **Ação necessária** | **Prioridade:** Média | **Data:** 23/03/2026  
> **Impacto:** Visualização do dashboard (gráfico de evolução) | **Complexidade:** Baixa

---

## 🎯 Problema Identificado

### **Inconsistência de Dados**
- **Patrimônio atual:** R$ 249.907,10 (calculado em tempo real)
- **Último snapshot histórico:** R$ 58.050 (jun/2024)
- **Gap:** 21 meses de dados ausentes no histórico

### **Sintomas Visuais**
1. Gráfico "Evolução do Patrimônio - Histórico Completo" com eixo Y incorreto (~60k vs ~250k)
2. Usuários confusos com discrepância entre valor atual e gráfico histórico
3. Perda de confiança na acuracidade dos dados

---

## 🔍 Análise da Causa Raiz

### **Arquitetura Atual**
```python
# Modelo: HistoricoPatrimonio
class HistoricoPatrimonio(db.Model):
    usuario_id = db.Column(UUID(as_uuid=True), db.ForeignKey('usuario.id'))
    data = db.Column(db.Date, nullable=False)
    patrimonio_total = db.Column(db.Numeric(20, 2), nullable=False)
    # ... outros campos
```

### **Processo Existente**
- ✅ Modelo `HistoricoPatrimonio` criado (22/03/2026)
- ✅ Migration aplicada
- ✅ Seed data inicial (até jun/2024)
- ❌ **Processo de atualização automática ausente**

### **Por que aconteceu?**
1. Foco na implementação do modelo e seed inicial
2. Processo agendado (job/scheduler) não foi priorizado
3. Assumiu que "alguém" atualizaria manualmente ou via outro processo

---

## 💡 Soluções Propostas

### **Opção 1: Job Mensal Simples (Recomendado)**
```python
# backend/app/jobs/historico_patrimonio_job.py
from datetime import date
from app import create_app
from app.models.usuario import Usuario
from app.models.historico_patrimonio import HistoricoPatrimonio
from app.services.portfolio_service import PortfolioService

def atualizar_historico_mensal():
    """Job mensal para criar snapshots de patrimônio"""
    app = create_app()
    
    with app.app_context():
        usuarios = Usuario.query.filter_by(ativo=True).all()
        
        for usuario in usuarios:
            try:
                # Calcular patrimônio atual
                dashboard = PortfolioService.get_dashboard(usuario.id)
                patrimonio_total = dashboard['resumo']['patrimonio_total']
                
                # Verificar se já existe snapshot deste mês
                hoje = date.today()
                existing = HistoricoPatrimonio.query.filter_by(
                    usuario_id=usuario.id,
                    data=hoje
                ).first()
                
                if existing:
                    # Atualizar existente
                    existing.patrimonio_total = patrimonio_total
                    existing.observacoes = "Atualizado automaticamente"
                else:
                    # Criar novo snapshot
                    historico = HistoricoPatrimonio(
                        usuario_id=usuario.id,
                        data=hoje,
                        patrimonio_total=patrimonio_total,
                        patrimonio_renda_variavel=dashboard['resumo'].get('renda_variavel', 0),
                        patrimonio_renda_fixa=dashboard['resumo'].get('renda_fixa', 0),
                        saldo_caixa=dashboard.get('saldo_caixa', {}).get('saldo_total_brl', 0),
                        observacoes="Atualizado automaticamente"
                    )
                    db.session.add(historico)
                
                db.session.commit()
                print(f"✅ Histórico atualizado: {usuario.username} - R$ {patrimonio_total:,.2f}")
                
            except Exception as e:
                print(f"❌ Erro ao atualizar {usuario.username}: {e}")
                db.session.rollback()
```

### **Opção 2: Integração com Scheduler**
```python
# backend/app/scheduler.py (usando APScheduler ou similar)
from apscheduler.schedulers.background import BackgroundScheduler
from app.jobs.historico_patrimonio_job import atualizar_historico_mensal

scheduler = BackgroundScheduler()
scheduler.add_job(
    atualizar_historico_mensal,
    'cron',
    day=1,  # Todo dia 1 do mês
    hour=2,  # 2 da manhã
    minute=0
)
scheduler.start()
```

### **Opção 3: Trigger Pós-Transação (Alternativa)**
```python
# Atualizar histórico após transações significativas
def pos_transacao_hook(usuario_id, valor_transacao):
    """Atualiza histórico se transação > 5% do patrimônio"""
    if valor_transacao > patrimonio_atual * 0.05:
        # Criar snapshot imediato
        criar_snapshot_historico(usuario_id)
```

---

## 📋 Plano de Implementação

### **Fase 1: Job Mensal (Sprint 7)**
- [ ] Criar `backend/app/jobs/historico_patrimonio_job.py`
- [ ] Implementar lógica de snapshot mensal
- [ ] Adicionar script de execução manual
- [ ] Testar com usuário e2e_user

### **Fase 2: Scheduler (Sprint 7)**
- [ ] Avaliar APScheduler vs cron nativo
- [ ] Implementar scheduler na inicialização da app
- [ ] Configurar job mensal (dia 1, 2h da manhã)
- [ ] Adicionar logging e monitoramento

### **Fase 3: Melhorias (Sprint 8)**
- [ ] Dashboard administrativo para jobs
- [ ] Recuperação de snapshots retroativos
- [ ] Alertas em caso de falha do job
- [ ] Configuração por usuário (frequência customizada)

---

## 🎁 Benefícios Esperados

1. **Consistência visual:** Gráfico sempre reflete valor atual
2. **Confiança do usuário:** Dados históricos confiáveis
3. **Análise temporal:** Evolução real do patrimônio
4. **Relatórios:** Dados precisos para exportação
5. **Compliance:** Auditoria com histórico completo

---

## ⚠️ Riscos e Mitigações

### **Risco 1: Performance**
- **Descrição:** Job pode ser lento com muitos usuários
- **Mitigação:** Processamento em batches, limit rate

### **Risco 2: Falhas**
- **Descrição:** Job pode falhar silenciosamente
- **Mitigação:** Logging robusto, alertas, retry

### **Risco 3: Dados incorretos**
- **Descrição:** Snapshot com patrimônio errado
- **Mitigação:** Validações, checksum, rollback

---

## 📊 Critérios de Sucesso

- [ ] Job executando mensalmente sem falhas
- [ ] Dashboard mostrando eixo Y correto
- [ ] Histórico completo para todos os usuários ativos
- [ ] Zero discrepâncias entre valor atual e último snapshot
- [ ] Logs de execução visíveis e monitoráveis

---

## 🔄 Próximos Passos

1. **Discussão em equipe:** Validar abordagem (job mensal vs scheduler)
2. **Aprovação técnica:** Arquitetura e implementação
3. **Implementação:** Fase 1 (job manual)
4. **Testes:** Validação com usuários reais
5. **Produção:** Deploy e monitoramento

---

**Documentação relacionada:**
- `docs/CHANGELOG.md` - Registro da correção manual
- `docs/LESSONS_LEARNED.md` - L-FE-003
- `backend/app/models/historico_patrimonio.py` - Modelo de dados
- `backend/app/services/portfolio_service.py` - Cálculo do patrimônio
