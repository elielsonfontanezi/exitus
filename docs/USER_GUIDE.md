# Guia do Usuário - Sistema Exitus

## 📋 Índice

- [Introdução](#introdução)
- [Primeiros Passos](#primeiros-passos)
- [Gestão de Carteiras](#gestão-de-carteiras)
- [Registro de Operações](#registro-de-operações)
- [Análises e Relatórios](#análises-e-relatórios)
- [Sistema de Alertas](#sistema-de-alertas)
- [Cotações em Tempo Real](#cotações-em-tempo-real)
- [Troubleshooting](#troubleshooting)

---

## Introdução

O **Sistema Exitus** é uma plataforma completa de gestão de investimentos que permite consolidar suas operações em múltiplos mercados (Brasil, EUA, Europa, Ásia), acompanhar performance, receber alertas e tomar decisões baseadas em análise fundamentalista.

### Principais Funcionalidades

- **Consolidação Multi-Mercado**: Visualize todas as suas posições em um único lugar
- **Buy Signals**: Análise automática com Buy Score (0-100) e Preço Teto
- **Dashboard Interativo**: Gráficos de alocação, performance e evolução patrimonial
- **Alertas Configuráveis**: Notificações por preço, DY, P/L e outros indicadores
- **Relatórios Avançados**: Performance, alocação e análise fiscal
- **Cotações Live**: Atualização automática com cache inteligente (15min)

---

## Primeiros Passos

### 1. Acessar o Sistema

**URL**: http://localhost:8080

O sistema abrirá na página de login.

### 2. Login e Registro

#### Login com Credenciais Padrão

Para ambiente de desenvolvimento, use:

```
Usuário: admin
Senha: admin123
```

**Tela de Login**:
- Campo "Nome de Usuário"
- Campo "Senha"
- Botão "Entrar"
- Link "Criar nova conta" (para registro)

#### Criar Nova Conta

1. Clique em "Criar nova conta"
2. Preencha os dados:
   - Nome de usuário (mínimo 3 caracteres, único)
   - E-mail (formato válido, único)
   - Senha (mínimo 6 caracteres)
   - Confirmar senha
3. Clique em "Registrar"
4. Você será redirecionado para o login

### 3. Interface Principal

Após o login, você verá:

**Navbar Superior**:
- Logo "Exitus"
- Menu: Dashboard | Buy Signals | Portfolios | Transações | Proventos
- Dropdown do usuário (canto superior direito):
  - Perfil
  - Configurações
  - Sair

**Sidebar (Mobile)**:
- Menu hamburguer para navegação

### 4. Navegação

A navegação é feita pelos links do menu superior:

| Menu | Descrição |
|------|-----------|
| **Dashboard** | Visão geral consolidada |
| **Buy Signals** | Análise de oportunidades de compra |
| **Portfolios** | Posições, alocação e performance |
| **Transações** | Histórico de compras/vendas |
| **Proventos** | Dividendos e JCP recebidos |

---

## Gestão de Carteiras

### Dashboard Principal

**Rota**: `/dashboard`

#### Métricas Principais (Cards)

Ao acessar o dashboard, você verá 6 cards com métricas principais:

1. **Patrimônio em Ativos**: Valor atual de todas as posições
2. **Custo de Aquisição**: Quanto você investiu
3. **Saldo em Caixa**: Disponível em corretoras
4. **Patrimônio Total**: Ativos + Caixa
5. **Lucro Bruto**: Diferença entre valor atual e custo
6. **Rentabilidade %**: Percentual de ganho/perda

**Exemplo**:
```
╔═══════════════════════════════════╗
║  Patrimônio em Ativos             ║
║  R$ 125.430,50                    ║
╚═══════════════════════════════════╝

╔═══════════════════════════════════╗
║  Rentabilidade                    ║
║  +25,43%  ↑                       ║
╚═══════════════════════════════════╝
```

#### Gráfico de Alocação

**Gráfico Pizza (Chart.js)**:
- Distribuição por classe de ativo
- Cores distintas para cada classe
- Percentual e valor absoluto
- Legenda interativa

**Classes**:
- Renda Variável (Ações)
- Renda Fixa
- FIIs (Fundos Imobiliários)
- REITs (internacional)

### Visualizar Posições

**Rota**: `/portfolios`

#### Tabela de Posições

A tabela mostra todas as suas holdings:

| Ticker | Quantidade | Preço Médio | Preço Atual | Custo Total | Valor Atual | Lucro | Rent. % |
|--------|------------|-------------|-------------|-------------|-------------|-------|---------|
| PETR4 | 100 | R$ 28,50 | R$ 31,46 | R$ 2.850,00 | R$ 3.146,00 | +R$ 296,00 | +10,39% |
| VALE3 | 50 | R$ 68,00 | R$ 69,39 | R$ 3.400,00 | R$ 3.469,50 | +R$ 69,50 | +2,04% |

**Funcionalidades**:
- Ordenação por coluna (clique no cabeçalho)
- Paginação (10 itens por página)
- Filtro por ticker (busca)
- Cores: Verde (lucro) | Vermelho (prejuízo)

### Criar Nova Carteira

**Funcionalidade**: Permite criar carteiras customizadas (ex: "Carteira Dividendos")

**Passos**:
1. Clique no botão "+ Nova Carteira"
2. Modal abrirá com campos:
   - Nome da carteira
   - Descrição (opcional)
3. Clique em "Criar"
4. Carteira aparecerá na lista

**Exemplo de Uso**:
- **Carteira 1**: "High Yield" (foco em DY alto)
- **Carteira 2**: "Growth" (foco em crescimento)
- **Carteira 3**: "Internacional" (apenas ativos US/EU)

---

## Registro de Operações

### Registrar Transação (Compra/Venda)

**Rota**: `/transacoes`

#### Criar Nova Transação

1. Clique no botão "+ Nova Transação"
2. Preencha o formulário:
   - **Tipo**: Compra ou Venda
   - **Ativo**: Selecione da lista (ou digite ticker)
   - **Corretora**: Selecione corretora
   - **Quantidade**: Número de ações/cotas
   - **Preço Unitário**: R$ por ação
   - **Taxas**: Corretagem + emolumentos
   - **Data da Operação**: YYYY-MM-DD

3. Clique em "Salvar"

**Validações**:
- Quantidade > 0
- Preço unitário > 0
- Data não pode ser futura
- Corretora deve existir
- Ativo deve estar cadastrado

**Exemplo**:
```
Tipo: COMPRA
Ativo: PETR4
Quantidade: 100
Preço Unitário: R$ 31,50
Taxas: R$ 5,00
Data: 2026-01-06
────────────────────
Valor Total: R$ 3.155,00
```

#### Visualizar Histórico

**Tabela de Transações**:
- Ordenação por data (mais recente primeiro)
- Filtros:
  - Por ticker
  - Por tipo (COMPRA/VENDA)
  - Por período (data início/fim)
- Paginação (10 por página)

### Registrar Proventos

**Rota**: `/proventos`

#### Criar Novo Provento

1. Clique no botão "+ Novo Provento"
2. Preencha:
   - **Ativo**: Selecione da lista
   - **Tipo**: Dividendo, JCP ou Rendimento
   - **Valor Bruto**: R$ total recebido
   - **Valor Líquido**: Após IR (calculado automaticamente)
   - **Data de Pagamento**
   - **Data COM**: Última data para receber

3. Clique em "Salvar"

**Cálculo Automático de IR**:
- **Dividendos (ações BR)**: Isento
- **JCP**: 15% na fonte
- **FII**: Isento (pessoa física)
- **REITs (US)**: 30% conforme tratado

#### Gráfico de Proventos

**Gráfico de Linha (12 meses)**:
- Eixo X: Meses
- Eixo Y: Valor recebido (R$)
- Tooltip: Detalhes ao passar mouse
- Total YTD: Soma do ano corrente

### Movimentações de Caixa

**Rota**: `/movimentacoes` (menu: Mais → Movimentações)

#### Registrar Depósito/Saque

**Tipos**:
- **DEPOSITO**: Transferência para corretora
- **SAQUE**: Resgate de corretora
- **TRANSFERENCIA**: Entre corretoras

**Campos**:
- Corretora
- Tipo
- Valor
- Data

**Saldo Atualizado**:
- Sistema atualiza automaticamente `saldo_caixa` da corretora

---

## Análises e Relatórios

### Buy Signals (Oportunidades de Compra)

**Rota**: `/buy-signals`

#### Tabela de Buy Scores

Mostra todos os ativos com análise fundamentalista:

| Ticker | Buy Score | Recomendação | Preço Atual | Preço Teto | Margem Seg. |
|--------|-----------|--------------|-------------|------------|-------------|
| PETR4 | 80 | COMPRA | R$ 31,46 | R$ 34,39 | 9,1% |
| VALE3 | 72 | COMPRA | R$ 69,39 | R$ 75,20 | 8,4% |
| ITUB4 | 55 | NEUTRO | R$ 28,90 | R$ 29,50 | 2,1% |

**Legenda de Cores**:
- **Verde (80-100)**: COMPRA FORTE
- **Verde claro (60-79)**: COMPRA
- **Amarelo (40-59)**: NEUTRO
- **Laranja (20-39)**: VENDA
- **Vermelho (0-19)**: VENDA FORTE

#### Como Interpretar o Buy Score

O Buy Score (0-100) é calculado com base em 5 critérios:

1. **P/L (20 pontos)**: Preço/Lucro baixo = mais pontos
2. **P/VP (20 pontos)**: Preço/Valor Patrimonial baixo = mais pontos
3. **Dividend Yield (20 pontos)**: DY alto = mais pontos
4. **ROE (20 pontos)**: Return on Equity alto = mais pontos
5. **Margem de Segurança (20 pontos)**: Preço abaixo do teto = mais pontos

**Exemplo: PETR4 com Score 80**
```
P/L: 18/20 (P/L = 4.8, muito baixo)
P/VP: 15/20 (P/VP = 1.2, razoável)
DY: 19/20 (DY = 9.5%, excelente)
ROE: 15/20 (ROE = 18.5%, bom)
Margem: 13/20 (9.1% abaixo do teto)
─────────────
Total: 80/100 → COMPRA
```

#### Preço Teto (4 Métodos)

**Clique em um ativo** para ver detalhes:

**Método Bazin**:
- Fórmula: `(DY * 100) / 6`
- Ideal para: Ações de dividendos

**Método Graham**:
- Fórmula: `√(22.5 * VPA * LPA)`
- Ideal para: Value investing

**Método Gordon**:
- Fórmula: `Dividendo / (Taxa Desconto - g)`
- Ideal para: Dividend growth stocks

**Preço Médio**:
- Média dos 3 métodos

#### Z-Score (Análise Estatística)

**Interpretação**:
```
Z = (Preço Atual - Média 252d) / Desvio Padrão

Z < -2: Muito subvalorizado (forte compra)
-2 < Z < -1: Subvalorizado
-1 < Z < 1: Neutro (preço justo)
1 < Z < 2: Sobrevalorizado
Z > 2: Muito sobrevalorizado (venda)
```

**Exemplo**: PETR4 com Z-Score = -1.35
- Preço atual: R$ 31,46
- Média 252 dias: R$ 34,80
- Desvio padrão: R$ 2,48
- **Interpretação**: Subvalorizado (oportunidade de compra)

#### Gráfico de Buy Scores

**Gráfico de Barras Horizontais (Chart.js)**:
- Top 10 ativos por Buy Score
- Cores conforme recomendação
- Clique para ver detalhes

### Dashboard de Portfolios

**Rota**: `/portfolios`

#### Gráficos Disponíveis

**1. Alocação por Classe (Pizza)**:
- Renda Variável: 63,8%
- Renda Fixa: 23,9%
- FIIs: 12,3%

**2. Evolução Patrimonial (Linha)**:
- Últimos 12 meses
- Eixo Y: Patrimônio (R$)
- Eixo X: Meses

**3. Distribuição Setorial (Barras)**:
- Energia: 25%
- Mineração: 18%
- Bancos: 15%
- Varejo: 12%
- Outros: 30%

### Relatórios Avançados

**Rota**: `/relatorios`

#### Gerar Relatório de Performance

**Passos**:
1. Clique em "+ Novo Relatório"
2. Selecione:
   - **Tipo**: Performance, Fiscal ou Alocação
   - **Período**: Data início e fim
3. Clique em "Gerar"
4. Sistema processará (2-5 segundos)
5. Relatório aparecerá na lista

**Campos do Relatório**:
- **Sharpe Ratio**: 1,45 (risco ajustado)
- **Max Drawdown**: -12,3% (maior queda)
- **Rentabilidade Período**: +8,5%
- **Volatilidade**: 18,2% (anualizada)

#### Exportar Relatório

**Funcionalidade**: Exportar para PDF (stub implementado)

1. Clique no ícone de download
2. Selecione formato: PDF ou Excel
3. Download inicia automaticamente

**Status**: PDF básico implementado, layout avançado planejado para M8

---

## Sistema de Alertas

**Rota**: `/alertas`

### Criar Alerta

**Tipos de Alerta Disponíveis**:

1. **Alta de Preço**: Notifica quando preço > X
2. **Baixa de Preço**: Notifica quando preço < X
3. **DY Mínimo**: Notifica quando DY < X%
4. **P/L Máximo**: Notifica quando P/L > X
5. **Volume Anormal**: Notifica quando volume > 2x média
6. **Margem de Segurança**: Notifica quando margem >= X%

**Passos para Criar**:

1. Clique em "+ Novo Alerta"
2. Preencha:
   - **Nome**: Ex: "PETR4 oportunidade"
   - **Tipo**: Selecione da lista
   - **Ativo**: Selecione ticker
   - **Condição**: Operador (>, <, >=, <=)
   - **Valor**: Valor de referência
3. Clique em "Criar"

**Exemplo**:
```
Nome: PETR4 abaixo de R$ 30
Tipo: BAIXA_PRECO
Ativo: PETR4
Condição: <
Valor: 30.00
Status: ATIVO ✓
```

### Gerenciar Alertas

**Tabela de Alertas**:

| Nome | Ativo | Tipo | Condição | Status | Ações |
|------|-------|------|----------|--------|-------|
| PETR4 oportunidade | PETR4 | Baixa Preço | < 30.00 | 🟢 ATIVO | [Toggle] [Excluir] |
| VALE3 alta DY | VALE3 | DY Mínimo | >= 8.0 | 🔴 INATIVO | [Toggle] [Excluir] |

**Ações**:
- **Toggle**: Ativar/desativar alerta (sem deletar)
- **Excluir**: Deletar permanentemente

**Verificação de Alertas**:
- Sistema verifica a cada **15 minutos** (junto com atualização de cotações)
- Alertas disparados: Planejado para M8 (notificação em tela)
- Futuro: Notificações por e-mail/Telegram (M9)

---

## Cotações em Tempo Real

**Integração**: Módulo M7.5 - Cotações Live

### Como Funciona

O sistema atualiza cotações automaticamente usando **multi-provider fallback**:

**Ordem de Tentativa**:
1. **Cache PostgreSQL** (15min TTL) - 85-95% dos casos
2. **brapi.dev** (B3 - primário)
3. **yfinance** (global - fallback 1)
4. **Alpha Vantage** (US - fallback 2)
5. **Finnhub** (US/EU - fallback 3)

**Vantagens**:
- **99,9% disponibilidade**: 5 camadas de fallback
- **Performance**: 85-95% requests em <0.3s (cache)
- **Zero downtime**: Funciona mesmo com todas APIs offline

### Atualização Manual

**Botão "Atualizar Cotações"**:
- Aparece nos dashboards de Buy Signals e Portfolios
- Força atualização via API (ignora cache)
- Útil para decisões em tempo real

**Exemplo de Uso**:
1. Acesse `/buy-signals`
2. Veja Buy Score de PETR4: 80 (preço R$ 31,46)
3. Clique em "Atualizar Cotações"
4. Sistema busca preço atual: R$ 31,20 (caiu)
5. Buy Score recalculado: 82 (oportunidade melhorou!)

### Indicador de Frescor

**Badge no Preço**:
```
R$ 31,46  [Cache: 5 min] 🟢
R$ 69,39  [API: agora]   🔵
R$ 28,90  [Cache: 14 min] 🟡
```

**Cores**:
- 🟢 Verde: Cache < 5 min
- 🟡 Amarelo: Cache 5-10 min
- 🟠 Laranja: Cache 10-15 min
- 🔵 Azul: Atualizado via API agora

---

## Troubleshooting

### Problemas Comuns

#### 1. "Token JWT expirado"

**Erro**: `401 Unauthorized - Token expired`

**Solução**:
1. Faça logout
2. Faça login novamente
3. Token válido por 1 hora

**Futuro**: Renovação automática (M8)

---

#### 2. "Ativo não encontrado"

**Erro**: Ao criar transação, ativo não aparece na lista

**Solução**:
1. Acesse menu "Ativos"
2. Cadastre novo ativo:
   - Ticker: EXEMPLO4
   - Nome: Empresa Exemplo
   - Tipo: ACAO
   - Mercado: BR
3. Ativo aparecerá na lista de transações

---

#### 3. "Cotação indisponível"

**Erro**: `provider: cache-postgresql, preco_atual: null`

**Causa**: Ativo sem histórico + todas APIs offline

**Solução**:
1. Aguarde 1-2 minutos
2. Clique em "Atualizar Cotações"
3. Se persistir, verifique conexão com internet
4. Para ativos BR: brapi.dev pode estar em manutenção (raro)

**Fallback**: Sistema usa último preço conhecido

---

#### 4. "Gráfico não carrega"

**Sintoma**: Dashboard mostra cards mas não gráficos

**Causas Possíveis**:
- Backend offline
- Dados insuficientes (menos de 2 ativos)
- Chart.js não carregou (CDN)

**Solução**:
1. Verifique se backend está rodando:
   ```bash
   curl http://localhost:5000/health
   ```
2. Recarregue a página (Ctrl+F5)
3. Se persistir, veja console do navegador (F12)

---

#### 5. "Cálculos incorretos"

**Exemplo**: Rentabilidade mostrando valores estranhos

**Causa**: Eventos corporativos não aplicados (splits, bonificações)

**Solução**:
1. Acesse menu "Eventos Corporativos"
2. Registre evento:
   - Ativo: PETR4
   - Tipo: SPLIT
   - Fator: 2.0 (1 ação → 2 ações)
   - Data: 2025-10-01
3. Clique em "Aplicar Evento"
4. Sistema ajustará:
   - Preço médio: ÷ 2
   - Quantidade: × 2
   - Transações anteriores ajustadas

---

### Como Reportar Bugs

**Passos**:
1. Acesse: https://github.com/elielsonfontanezi/exitus/issues
2. Clique em "New Issue"
3. Preencha:
   - **Título**: Descrição curta
   - **Descrição**:
     - O que você fez
     - O que esperava
     - O que aconteceu
     - Prints (se aplicável)
4. Submit

**Informações Úteis**:
- Versão do sistema: v0.7.6
- Navegador: Chrome/Firefox/Safari
- Sistema operacional
- Logs do console (F12 → Console)

---

### FAQ (Perguntas Frequentes)

**Q: Posso importar transações via CSV?**  
A: Planejado para M8. Atualmente, registro manual.

**Q: Sistema funciona offline?**  
A: Parcialmente. Dados carregados (posições, transações) funcionam. Cotações usam cache local.

**Q: Posso usar em múltiplos dispositivos?**  
A: Sim. Login com mesmas credenciais. Dados sincronizados no servidor.

**Q: Como deletar minha conta?**  
A: Contate administrador ou use opção "Configurações → Excluir conta" (LGPD compliance).

**Q: Suporta criptomoedas?**  
A: Não implementado em v0.7.6. Planejado para M9.

**Q: Relatório fiscal automático?**  
A: Básico implementado. Cálculo de IR planejado para M8.

---

## Referências

- [API_REFERENCE.md](API_REFERENCE.md) - Documentação completa de APIs
- [MODULES.md](MODULES.md) - Detalhes técnicos dos módulos
- [OPERATIONS_RUNBOOK.md](OPERATIONS_RUNBOOK.md) - Operações e deploy

---

## Suporte

**GitHub Issues**: https://github.com/elielsonfontanezi/exitus/issues  
**Documentação**: https://github.com/elielsonfontanezi/exitus/tree/main/docs

---

**Documento gerado**: 07 de Janeiro de 2026  
**Versão**: v0.7.6  
**Baseado em**: Validações M5/M6, experiência real de uso, checklists frontend
