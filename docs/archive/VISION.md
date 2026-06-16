# Exitus — Visão de Negócio

## Proposta de Valor

**Exitus** é uma plataforma multi-usuário de gestão e análise de investimentos, projetada para investidores individuais e profissionais que operam em múltiplos mercados e classes de ativos.

### Principais Diferenciais

- **Consolidação Multi-Mercado**: Gestão unificada de ativos brasileiros, americanos, europeus e asiáticos
- **Multi-Classe de Ativos**: Ações, FIIs, REITs, renda fixa nacional e internacional, criptoativos
- **Multi-Corretora**: Abstração de caixa unificado com controle por corretora
- **Análise Fundamentalista Avançada**: Buy Score, Preço Teto (4 métodos), Z-Score com histórico real
- **Cotações Near Real-Time**: Multi-provider com cache inteligente (delay até 15 minutos)
- **Dashboards Interativos**: Performance, alocação, evolução patrimonial e métricas de risco
- **Sistema de Alertas**: Notificações configuráveis por preço, percentual e indicadores
- **Cálculos Fiscais**: Regras configuráveis por país e tipo de ativo

---

## Mercados e Ativos Suportados

### 🇧🇷 Brasil (6 tipos)
- **Ações** (ACAO): B3 — PETR4, VALE3, ITUB4
- **FIIs** (FII): Fundos Imobiliários — HGLG11, KNRI11
- **CDB** (CDB): Certificados de Depósito Bancário
- **LCI/LCA** (LCI_LCA): Letras de Crédito
- **Tesouro Direto** (TESOURO_DIRETO): Selic, IPCA+, Prefixado
- **Debêntures** (DEBENTURE): Títulos corporativos

### 🇺🇸 Estados Unidos (4 tipos)
- **Stocks** (STOCK): NYSE/NASDAQ — AAPL, MSFT, GOOGL
- **REITs** (REIT): Real Estate Investment Trusts — O, VNQ
- **Bonds** (BOND): Títulos corporativos e governamentais
- **ETFs** (ETF): Fundos negociados em bolsa — SPY, QQQ

### 🌍 Internacional (2 tipos)
- **Stocks Internacionais** (STOCK_INTL): Europa/Ásia — SAP.DE, 7203.T
- **ETFs Internacionais** (ETF_INTL): VWCE.DE

### 🔷 Outros (2 tipos)
- **Criptomoedas** (CRIPTO): BTC, ETH, SOL
- **Outros** (OUTRO): Commodities, derivatives

---

## Funcionalidades Estratégicas

### 1. Autenticação e Controle de Acesso
- JWT com RBAC granular
- Rate limiting e segurança por camadas
- Multi-tenant isolado por usuário

### 2. Gestão de Portfólio
- Posicionamento consolidado por corretora
- Cálculo automático de preço médio e custos
- Ajustes automáticos por eventos corporativos

### 3. Análise Fundamentalista
- **Buy Score (0-100)**: Métrica composta baseada em DY, P/L, P/VP, ROE
- **Preço Teto**: 4 métodos (Bazin, Graham, Gordon, DCF) com parâmetros regionais
- **Z-Score**: Análise estatística baseada em histórico de preços (mínimo 30 dias)

### 4. Cotações e Dados de Mercado
- Multi-provider: brapi.dev, yfinance, Alpha Vantage, Finnhub
- Cache inteligente com TTL de 15 minutos
- Fallback automático entre providers

### 5. Eventos Corporativos
- Tratamento automático: splits, bonificações, dividendos, grupamentos
- Aplicação manual com controle de auditoria
- Histórico completo para rastreabilidade

### 6. Movimentações Financeiras
- Depósitos, saques, transferências intercorretoras
- Controle multi-moeda com conversão automática
- Auditoria completa de fluxo de caixa

### 7. Cálculos Fiscais
- Regras configuráveis por jurisdição
- Cálculo automático de IR sobre ganho de capital
- Suporte para diferentes tipos de ativos e operações

### 8. Alertas e Notificações
- Alertas por preço, percentual e indicadores
- Configuração por ativo ou portfólio
- Histórico de alertas disparados

### 9. Relatórios e Performance
- Métricas de rentabilidade (YTD, 1A, 3A)
- Análise de risco: volatilidade, Sharpe, max drawdown
- Alocação por classe de ativos e mercado

---

## Arquitetura e Tecnologia

### Stack Principal
- **Backend**: Python 3.11+ / Flask (API RESTful)
- **Frontend**: Flask Templates + HTMX + Alpine.js + TailwindCSS
- **Database**: PostgreSQL 16+ (relacional otimizado)
- **Containers**: Podman (rootless, sem Docker daemon)
- **APIs Externas**: brapi.dev, yfinance, Alpha Vantage, Finnhub

### Arquitetura de 3 Containers
1. **PostgreSQL** — Armazenamento persistente
2. **Flask Backend** — API RESTful + Business Logic
3. **Flask Frontend** — Templates + HTMX + Assets

### Princípios de Design
- Separação de responsabilidades
- Escalabilidade independente
- Desenvolvimento paralelo
- Hot reload independente
- Segurança por camadas
- Deploy flexível

---

## Compliance e Segurança

### Conformidade Regulatória
- Regras fiscais configuráveis por país
- Tratamento de eventos corporativos conforme normas
- Auditoria completa de operações

### Segurança (Roadmap Futuro)
- Criptografia AES-256 para dados sensíveis
- TLS 1.3 para trânsito
- Logs imutáveis com hash encadeado
- Controle de acesso granular
- Direitos LGPD/GDPR (consentimento, esquecimento, portabilidade)

---

## Roadmap de Funcionalidades

### Implementado ✅
- Autenticação JWT e RBAC
- CRUD completo de entidades principais
- Análise fundamentalista (Buy Score, Preço Teto, Z-Score)
- Cotações multi-provider com cache
- Eventos corporativos básicos
- Alertas configuráveis
- Dashboards interativos

### Em Desenvolvimento 📅
- Importação/Exportação (CSV, Excel, JSON, PDF)
- Auditoria avançada com logs imutáveis
- Projeções de renda passiva
- Relatórios consolidados multi-dimensão
- Monitoramento e alertas em tempo real

### Futuro 🚀
- Analytics avançados (Monte Carlo, otimização)
- Deploy em cloud com CI/CD
- Monitoramento (Prometheus/Grafana)
- APIs de mercado adicionais
- Machine Learning para previsões

---

## Público-Alvo

### Investidores Individuais
- Gestão consolidada de portfólio multi-mercado
- Análise fundamentalista automatizada
- Controle fiscal simplificado

### Assessoras de Investimento
- Gestão multi-cliente com isolamento de dados
- Relatórios profissionais customizados
- Compliance regulatório automático

### Desenvolvedores Fintech
- API RESTful completa para integrações
- Documentação detalhada e exemplos
- Arquitetura escalável e extensível

---

## Métricas de Sucesso

### Técnicas
- 99.9% uptime da API
- <500ms tempo de resposta médio
- 85-95% cache hit rate
- 0% perda de dados

### de Negócio
- Adoção multi-mercado (>3 países)
- Retenção de usuários (>80% mensal)
- Volume de ativos gerenciados
- Precisão das análises (>90% acurácia)

---

*Documento atualizado: 27 de Fevereiro de 2026*  
*Versão: 1.0 — Baseado no Prompt Mestre original, limpo para referência de negócio*
