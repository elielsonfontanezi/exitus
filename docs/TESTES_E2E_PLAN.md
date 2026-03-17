# 🧪 Plano de Testes End-to-End (E2E) — Frontend Exitus

> **Versão:** 1.0  
> **Data:** 17/03/2026  
> **Status:** 📋 Planejamento  
> **Modelo IA Recomendado:** Claude Sonnet (testes complexos, múltiplos fluxos)

---

## 📊 Visão Geral

### **Objetivo**
Garantir que todas as telas e fluxos críticos do frontend funcionem corretamente de ponta a ponta, incluindo:
- Autenticação e autorização
- Navegação entre telas
- Interação com backend (APIs)
- Manipulação de dados (CRUD)
- Validações e mensagens de erro
- Responsividade e UX

### **Escopo**
- **15 telas principais** identificadas
- **8 fluxos críticos** de negócio
- **50+ casos de teste** estimados
- **Cobertura:** Login, Dashboard, Buy Signals, Portfolios, Transações, Alertas, Relatórios

---

## 🎯 Estratégia de Testes

### **Framework Recomendado: Playwright**

**Por quê Playwright?**
- ✅ Suporte nativo a Python (integração com backend)
- ✅ Execução paralela e rápida
- ✅ Auto-wait inteligente (reduz flakiness)
- ✅ Suporte a múltiplos navegadores (Chromium, Firefox, WebKit)
- ✅ Screenshots e vídeos automáticos em falhas
- ✅ Melhor para SPAs com Alpine.js/HTMX

**Alternativa:** Selenium (mais maduro, mas mais lento e verboso)

### **Estrutura de Testes**

```
tests/e2e/
├── conftest.py                 # Fixtures compartilhadas (login, setup)
├── test_auth_flows.py          # Autenticação e autorização
├── test_dashboard_flows.py     # Dashboard e navegação
├── test_buy_signals_flows.py   # Buy Signals e análise
├── test_portfolio_flows.py     # Portfolios e posições
├── test_transaction_flows.py   # Transações e movimentações
├── test_alert_flows.py         # Alertas e notificações
├── test_report_flows.py        # Relatórios e exportação
└── utils/
    ├── page_objects.py         # Page Object Model
    └── helpers.py              # Funções auxiliares
```

---

## 📋 Inventário de Telas

### **1. Autenticação (3 telas)**
| Tela | Rota | Prioridade | Status |
|------|------|------------|--------|
| Login | `/auth/login` | 🔴 Crítica | ✅ Funcional |
| Registro | `/auth/register` | 🟡 Média | ⚠️ M7 |
| Perfil | `/auth/profile` | 🟡 Média | ⚠️ Básico |

### **2. Dashboard (1 tela)**
| Tela | Rota | Prioridade | Status |
|------|------|------------|--------|
| Dashboard Multi-Mercado | `/dashboard/` | 🔴 Crítica | ✅ Funcional |

### **3. Buy Signals (1 tela)**
| Tela | Rota | Prioridade | Status |
|------|------|------------|--------|
| Buy Signals | `/dashboard/buy-signals` | 🔴 Crítica | ✅ Funcional |

### **4. Portfolios (1 tela)**
| Tela | Rota | Prioridade | Status |
|------|------|------------|--------|
| Portfolios | `/dashboard/portfolios` | 🔴 Crítica | ✅ Funcional |

### **5. Transações (2 telas)**
| Tela | Rota | Prioridade | Status |
|------|------|------------|--------|
| Transações | `/dashboard/transactions` | 🔴 Crítica | ⚠️ Básico |
| Movimentações | `/dashboard/movimentacoes` | 🟡 Média | ⚠️ Básico |

### **6. Planos de Compra (3 telas)**
| Tela | Rota | Prioridade | Status |
|------|------|------------|--------|
| Planos de Compra | `/dashboard/planos-compra` | 🟢 Baixa | ⚠️ Básico |
| Novo Plano | `/dashboard/planos-compra/novo` | 🟢 Baixa | ⚠️ Básico |
| Detalhes Plano | `/dashboard/planos-compra/<id>` | 🟢 Baixa | ⚠️ Básico |

### **7. Alertas (1 tela)**
| Tela | Rota | Prioridade | Status |
|------|------|------------|--------|
| Alertas | `/dashboard/alerts` | 🟡 Média | ⚠️ Básico |

### **8. Relatórios (3 telas)**
| Tela | Rota | Prioridade | Status |
|------|------|------------|--------|
| Relatórios | `/dashboard/reports` | 🟡 Média | ⚠️ Básico |
| Detalhe Relatório | `/dashboard/reports/<id>` | 🟡 Média | ⚠️ Básico |
| Analytics | `/dashboard/analytics` | 🟢 Baixa | ⚠️ Básico |

### **9. Ativos e Dividendos (2 telas)**
| Tela | Rota | Prioridade | Status |
|------|------|------------|--------|
| Ativos | `/dashboard/assets` | 🟡 Média | ⚠️ Básico |
| Dividendos | `/dashboard/dividends` | 🟡 Média | ⚠️ Básico |

**Total:** 15 telas principais

---

## 🔄 Fluxos Críticos de Negócio

### **FC-001: Autenticação Completa**
**Prioridade:** 🔴 Crítica  
**Descrição:** Login, navegação autenticada, logout

**Cenários:**
1. Login com credenciais válidas (admin/senha123)
2. Login com credenciais inválidas
3. Redirecionamento para dashboard após login
4. Acesso a rota protegida sem login (redirect para login)
5. Logout e limpeza de sessão
6. Persistência de sessão (refresh da página)

**Estimativa:** 6 testes

---

### **FC-002: Dashboard Multi-Mercado**
**Prioridade:** 🔴 Crítica  
**Descrição:** Visualização de dados consolidados por mercado

**Cenários:**
1. Carregar dashboard com dados de BR, US, INTL
2. Exibir cards de resumo (Patrimônio, Rentabilidade, Carteiras, Posições)
3. Toggle BRL/USD funcionando
4. Navegação para Buy Signals
5. Navegação para Portfolios
6. Gráficos carregando (Alocação Geográfica, Evolução)

**Estimativa:** 6 testes

---

### **FC-003: Buy Signals - Análise de Ativos**
**Prioridade:** 🔴 Crítica  
**Descrição:** Busca e análise individual de ativos

**Cenários:**
1. Carregar watchlist top (melhores buy signals)
2. Buscar ativo específico (PETR4)
3. Exibir análise completa (buy_score, margem, métricas)
4. Exibir gráfico radial de indicadores
5. Buscar ativo inexistente (erro tratado)
6. Buscar ativo sem dados suficientes

**Estimativa:** 6 testes

---

### **FC-004: Portfolios - Gestão de Carteiras**
**Prioridade:** 🔴 Crítica  
**Descrição:** Visualização e gestão de portfolios

**Cenários:**
1. Listar todos os portfolios do usuário
2. Exibir resumo de cada portfolio (saldo, ativos, rentabilidade)
3. Filtrar portfolios por status (ativo/inativo)
4. Criar novo portfolio
5. Editar portfolio existente
6. Desativar portfolio

**Estimativa:** 6 testes

---

### **FC-005: Transações - CRUD Completo**
**Prioridade:** 🔴 Crítica  
**Descrição:** Criar, visualizar, editar e excluir transações

**Cenários:**
1. Listar transações do usuário
2. Filtrar transações por tipo (COMPRA/VENDA)
3. Filtrar transações por mercado (BR/US/INTL)
4. Criar nova transação de compra
5. Criar nova transação de venda
6. Editar transação existente
7. Excluir transação
8. Validações de formulário (campos obrigatórios)

**Estimativa:** 8 testes

---

### **FC-006: Alertas - Notificações**
**Prioridade:** 🟡 Média  
**Descrição:** Visualização e gestão de alertas

**Cenários:**
1. Listar alertas ativos
2. Filtrar alertas por tipo
3. Marcar alerta como lido
4. Criar novo alerta de preço
5. Excluir alerta

**Estimativa:** 5 testes

---

### **FC-007: Relatórios - Geração e Exportação**
**Prioridade:** 🟡 Média  
**Descrição:** Gerar e exportar relatórios fiscais

**Cenários:**
1. Listar relatórios disponíveis
2. Visualizar relatório de IR
3. Visualizar relatório de DARF
4. Exportar relatório em PDF
5. Exportar relatório em Excel
6. Filtrar relatórios por período

**Estimativa:** 6 testes

---

### **FC-008: Planos de Compra - Gestão**
**Prioridade:** 🟢 Baixa  
**Descrição:** Criar e gerenciar planos de compra

**Cenários:**
1. Listar planos de compra
2. Criar novo plano de compra
3. Visualizar detalhes do plano
4. Editar plano existente
5. Marcar plano como concluído
6. Excluir plano

**Estimativa:** 6 testes

---

## 📦 Casos de Teste Detalhados

### **Exemplo: TC-001 - Login com Credenciais Válidas**

```python
# tests/e2e/test_auth_flows.py

import pytest
from playwright.sync_api import Page, expect

def test_login_com_credenciais_validas(page: Page, base_url: str):
    """
    TC-001: Login com credenciais válidas
    
    Pré-condições:
    - Usuário admin existe no banco
    - Senha é senha123
    
    Passos:
    1. Acessar página de login
    2. Preencher username: admin
    3. Preencher password: senha123
    4. Clicar em "Entrar"
    
    Resultado Esperado:
    - Redirecionado para /dashboard/
    - Dashboard carrega com sucesso
    - Navbar exibe nome do usuário
    """
    # Arrange
    page.goto(f"{base_url}/auth/login")
    
    # Act
    page.fill('input[name="username"]', 'admin')
    page.fill('input[name="password"]', 'senha123')
    page.click('button[type="submit"]')
    
    # Assert
    expect(page).to_have_url(f"{base_url}/dashboard/")
    expect(page.locator('h1')).to_contain_text('Dashboard')
    expect(page.locator('.navbar')).to_contain_text('admin')
```

---

## 🛠️ Configuração do Ambiente de Testes

### **1. Instalação do Playwright**

```bash
# Instalar Playwright
pip install pytest-playwright

# Instalar navegadores
playwright install chromium firefox webkit
```

### **2. Configuração pytest.ini**

```ini
# pytest.ini
[pytest]
testpaths = tests/e2e
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --capture=no
    --tb=short
    --strict-markers
    --playwright-headed  # Executar com navegador visível (debug)
markers =
    smoke: Testes de fumaça (críticos)
    regression: Testes de regressão (completos)
    slow: Testes lentos (skip em CI rápido)
```

### **3. Fixtures Compartilhadas**

```python
# tests/e2e/conftest.py

import pytest
from playwright.sync_api import Page, Browser

@pytest.fixture(scope="session")
def base_url():
    """URL base do frontend"""
    return "http://localhost:8080"

@pytest.fixture(scope="session")
def api_url():
    """URL base do backend"""
    return "http://localhost:5000"

@pytest.fixture
def authenticated_page(page: Page, base_url: str):
    """Página já autenticada como admin"""
    page.goto(f"{base_url}/auth/login")
    page.fill('input[name="username"]', 'admin')
    page.fill('input[name="password"]', 'senha123')
    page.click('button[type="submit"]')
    page.wait_for_url(f"{base_url}/dashboard/")
    return page

@pytest.fixture
def test_data():
    """Dados de teste compartilhados"""
    return {
        "admin_user": {"username": "admin", "password": "senha123"},
        "test_ticker": "PETR4",
        "test_portfolio": {"nome": "Carteira Teste E2E", "descricao": "Teste automatizado"}
    }
```

---

## 📈 Métricas e Cobertura

### **Meta de Cobertura**
- **Fluxos Críticos (FC-001 a FC-003):** 100% de cobertura
- **Fluxos Importantes (FC-004 a FC-005):** 90% de cobertura
- **Fluxos Secundários (FC-006 a FC-008):** 70% de cobertura

### **Tempo de Execução Esperado**
- **Suite Completa:** ~15-20 minutos (50 testes)
- **Smoke Tests:** ~3-5 minutos (15 testes críticos)
- **Execução Paralela:** ~5-8 minutos (4 workers)

### **Relatórios**
- HTML Report (pytest-html)
- Allure Report (allure-pytest)
- Screenshots em falhas
- Vídeos de execução (opcional)

---

## 🚀 Roadmap de Implementação

### **Fase 1: Setup e Testes Críticos (Prioridade 🔴)**
**Duração:** 2-3 dias  
**Modelo IA:** Claude Sonnet

- [ ] Instalar e configurar Playwright
- [ ] Criar estrutura de testes (conftest.py, fixtures)
- [ ] Implementar FC-001: Autenticação Completa (6 testes)
- [ ] Implementar FC-002: Dashboard Multi-Mercado (6 testes)
- [ ] Implementar FC-003: Buy Signals (6 testes)
- [ ] Configurar CI/CD para executar testes E2E

**Entrega:** 18 testes críticos funcionando

---

### **Fase 2: Testes Importantes (Prioridade 🟡)**
**Duração:** 3-4 dias  
**Modelo IA:** Claude Sonnet

- [ ] Implementar FC-004: Portfolios (6 testes)
- [ ] Implementar FC-005: Transações (8 testes)
- [ ] Implementar FC-006: Alertas (5 testes)
- [ ] Implementar FC-007: Relatórios (6 testes)

**Entrega:** +25 testes (total 43)

---

### **Fase 3: Testes Secundários (Prioridade 🟢)**
**Duração:** 2 dias  
**Modelo IA:** SWE-1.5

- [ ] Implementar FC-008: Planos de Compra (6 testes)
- [ ] Testes de responsividade (mobile/tablet)
- [ ] Testes de acessibilidade (WCAG)
- [ ] Testes de performance (Lighthouse)

**Entrega:** +10 testes (total 53)

---

### **Fase 4: Otimização e Manutenção**
**Duração:** Contínuo

- [ ] Refatorar testes duplicados
- [ ] Implementar Page Object Model
- [ ] Adicionar testes de regressão visual
- [ ] Documentar padrões de testes

---

## 📚 Referências e Recursos

### **Documentação**
- [Playwright Python](https://playwright.dev/python/)
- [pytest-playwright](https://github.com/microsoft/playwright-pytest)
- [Page Object Model](https://playwright.dev/python/docs/pom)

### **Exemplos de Código**
- `backend/tests/` - Testes unitários existentes (491 testes)
- `docs/CODING_STANDARDS.md` - Padrões de código
- `docs/LESSONS_LEARNED.md` - Lições aprendidas

### **Ferramentas Complementares**
- **Allure:** Relatórios visuais de testes
- **pytest-xdist:** Execução paralela
- **pytest-rerunfailures:** Retry de testes flaky

---

## ✅ Checklist de Aprovação

Antes de considerar os testes E2E completos:

- [ ] Todos os fluxos críticos (FC-001 a FC-003) têm 100% de cobertura
- [ ] Suite completa executa em < 20 minutos
- [ ] Testes executam com sucesso em CI/CD
- [ ] Documentação de testes está atualizada
- [ ] Screenshots e vídeos são gerados em falhas
- [ ] Relatórios HTML/Allure são gerados automaticamente
- [ ] Testes são estáveis (< 5% de flakiness)

---

## 🎯 Próximos Passos

1. **Revisar e aprovar este plano** com o time
2. **Iniciar Fase 1** - Setup e Testes Críticos
3. **Executar primeira suite** de testes E2E
4. **Iterar e melhorar** com base nos resultados

---

**Documento criado em:** 17/03/2026  
**Última atualização:** 17/03/2026  
**Responsável:** Sistema Exitus - Testes E2E  
**Status:** 📋 Aguardando aprovação para implementação
