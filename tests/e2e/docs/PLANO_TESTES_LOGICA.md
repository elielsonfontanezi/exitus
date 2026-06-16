# 🧪 Plano de Testes de Lógica de Negócio — Exitus E2E v3

> **Branch:** `feature/testes-e2e-v3`  
> **Data:** 16/06/2026 | **Versão:** v1.0  
> **Objetivo:** Cobrir toda lógica de negócio do frontend — não apenas carregamento, mas comportamento real: cálculos, formulários, persistência, feedback ao usuário.

---

## 📋 Índice

1. [Pré-condições Gerais](#pré-condições-gerais)
2. [Módulo Operações — Compra](#módulo-operações--compra)
3. [Módulo Operações — Venda](#módulo-operações--venda)
4. [Módulo Operações — Importação B3](#módulo-operações--importação-b3)
5. [Módulo Fiscal — IR e DARF](#módulo-fiscal--ir-e-darf)
6. [Módulo Portfolio — Rentabilidade](#módulo-portfolio--rentabilidade)
7. [Módulo Ferramentas — Calculadora IR](#módulo-ferramentas--calculadora-ir)
8. [Módulo Ferramentas — Screener](#módulo-ferramentas--screener)
9. [Módulo Ferramentas — Simulador](#módulo-ferramentas--simulador)
10. [Módulo Relatórios — Exportação CSV](#módulo-relatórios--exportação-csv)
11. [Regressão — Fluxo Ponta a Ponta](#regressão--fluxo-ponta-a-ponta)
12. [Mapeamento Specs → Arquivos](#mapeamento-specs--arquivos)

---

## Pré-condições Gerais

| Item | Valor |
|------|-------|
| **Usuário de teste** | `e2e_user` / `e2e_senha_123` |
| **Usuário admin** | `e2e_admin` / `e2e_senha_123` |
| **Seed recomendado** | `test_full` (30 ativos, 48 transações, 32 proventos) |
| **URL base** | `http://localhost:8080` |
| **Ambiente** | Desenvolvimento local com containers Podman |

### Reset de dados antes dos testes de escrita

Testes que criam/modificam dados (compra, venda) devem:
1. Registrar o estado inicial via API antes do teste
2. Desfazer a operação via API após o teste (teardown)
3. Ou usar um ticker/valor único que permita identificar e remover o registro criado

---

## Módulo Operações — Compra

**Arquivo:** `specs/operacoes/08-compra-logica.spec.js`  
**Rota:** `/operacoes/`

### CT-001 — Seleção de tipo revela campos do formulário

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Usuário logado, na tela `/operacoes/` |
| **Ação** | Clicar no card de tipo "Ação BR" |
| **Resultado esperado** | Campo de busca de ticker fica visível |
| **Resultado esperado** | Modo "Compra" está selecionado por padrão |

### CT-002 — Busca de ativo retorna sugestões

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Tipo "Ação BR" selecionado |
| **Ação** | Digitar "PETR" no campo de busca |
| **Resultado esperado** | Lista de sugestões aparece com PETR4 |
| **Resultado esperado** | Sugestão exibe ticker em negrito |

### CT-003 — Seleção de ativo preenche resumo

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Sugestões de "PETR" visíveis |
| **Ação** | Clicar em PETR4 na lista |
| **Resultado esperado** | Campos de quantidade e preço ficam visíveis |
| **Resultado esperado** | Seção "Resumo da Operação" exibe ticker PETR4 |
| **Resultado esperado** | Cotação atual é exibida (ou placeholder) |

### CT-004 — Validação de quantidade inteira para Ação BR

| Campo | Valor |
|-------|-------|
| **Pré-condição** | PETR4 selecionado, tipo Ação BR (não aceita fração) |
| **Ação** | Preencher quantidade com "1.5" |
| **Resultado esperado** | Alerta exibido: "Quantidade deve ser inteira" |
| **Resultado esperado** | Botão submit permanece desabilitado |

### CT-005 — Resumo calcula total corretamente

| Campo | Valor |
|-------|-------|
| **Pré-condição** | PETR4 selecionado |
| **Ação** | Preencher quantidade "10", preço "30,00" |
| **Resultado esperado** | Resumo exibe total "R$ 300,00" |
| **Resultado esperado** | Fórmula: quantidade × preço = total |

### CT-006 — Compra bem-sucedida exibe confirmação

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Formulário preenchido corretamente (PETR4, qtd=1, preço=R$1,00, corretora selecionada, data válida) |
| **Ação** | Clicar em "Confirmar Operação" |
| **Resultado esperado** | Mensagem de sucesso exibida ("operação registrada" ou similar) |
| **Resultado esperado** | Formulário é resetado após confirmação |
| **Teardown** | Remover a transação criada via API |

### CT-007 — Toggle Compra/Venda alterna modo corretamente

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Na tela operações, modo Compra ativo |
| **Ação** | Clicar no botão "Venda" |
| **Resultado esperado** | Interface muda para modo Venda |
| **Resultado esperado** | Campo de busca de posições fica visível (não ticker livre) |

### CT-008 — Corretora é obrigatória

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Formulário preenchido exceto corretora |
| **Ação** | Tentar submeter o formulário |
| **Resultado esperado** | Botão submit permanece desabilitado sem corretora selecionada |

---

## Módulo Operações — Venda

**Arquivo:** `specs/operacoes/09-venda-logica.spec.js`  
**Rota:** `/operacoes/`

### CT-009 — Modo venda exibe posições do usuário

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Usuário com posições (seed test_full), modo Venda, tipo "Ação BR" |
| **Ação** | Aguardar carregamento das posições |
| **Resultado esperado** | Lista de posições disponíveis é exibida |
| **Resultado esperado** | Cada posição exibe ticker, quantidade e PM |

### CT-010 — Busca filtra posições

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Posições carregadas no modo Venda |
| **Ação** | Digitar "PETR" no campo de busca de posições |
| **Resultado esperado** | Apenas posições com PETR no ticker são exibidas |

### CT-011 — Quantidade máxima é limitada ao disponível

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Posição selecionada com quantidade conhecida (seed) |
| **Ação** | Preencher quantidade maior que o disponível |
| **Resultado esperado** | Mensagem de erro "Quantidade excede o disponível" exibida |
| **Resultado esperado** | Botão submit permanece desabilitado |

### CT-012 — Botão "Máx" preenche quantidade máxima

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Posição selecionada, botão "Máx" visível |
| **Ação** | Clicar no botão "Máx" |
| **Resultado esperado** | Campo quantidade preenchido com valor máximo da posição |

### CT-013 — Resumo de venda exibe ganho/perda estimado

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Posição selecionada, quantidade e preço preenchidos |
| **Ação** | Observar seção Resumo |
| **Resultado esperado** | Exibe PM de compra, preço de venda e resultado (positivo/negativo) |

---

## Módulo Operações — Importação B3

**Arquivo:** `specs/operacoes/10-importacao-b3.spec.js`  
**Rota:** `/operacoes/`

### CT-014 — Aba de importação B3 é acessível

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Na tela `/operacoes/` |
| **Ação** | Clicar na aba/botão de Importação B3 |
| **Resultado esperado** | Área de upload de arquivo fica visível |
| **Resultado esperado** | Instruções de formato exibidas (CSV/XLSX) |

### CT-015 — Upload de arquivo inválido exibe erro

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Área de upload visível |
| **Ação** | Fazer upload de arquivo .txt (formato inválido) |
| **Resultado esperado** | Mensagem de erro sobre formato inválido |

### CT-016 — Upload de CSV B3 válido processa corretamente

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Arquivo CSV B3 de teste disponível em `tests/e2e/fixtures/b3_sample.csv` |
| **Ação** | Fazer upload do arquivo CSV |
| **Resultado esperado** | Barra de progresso ou mensagem de processamento |
| **Resultado esperado** | Resultado exibe número de transações importadas |
| **Resultado esperado** | Sem erros críticos |

---

## Módulo Fiscal — IR e DARF

**Arquivo:** `specs/fiscal/11-ir-calculo.spec.js`  
**Rotas:** `/imposto-renda/mensal`, `/imposto-renda/darf`, `/imposto-renda/historico`, `/imposto-renda/dirpf`

### CT-017 — Apuração mensal exibe categorias corretas

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Usuário com transações no seed (test_full tem vendas com IR) |
| **Ação** | Acessar `/imposto-renda/mensal` |
| **Resultado esperado** | Categorias exibidas: Ações, FIIs, ETFs, Renda Fixa |
| **Resultado esperado** | Valores numéricos presentes (não apenas zeros) |

### CT-018 — Isenção de IR para vendas ≤ R$20.000 em Ações

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Mês com vendas de Ações abaixo do limite de isenção |
| **Ação** | Verificar apuração do mês |
| **Resultado esperado** | IR = R$ 0,00 para categoria Ações no mês isento |
| **Resultado esperado** | Badge/indicador "Isento" ou similar exibido |

### CT-019 — Seletor de mês/ano filtra apuração

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Na tela de apuração mensal |
| **Ação** | Alterar mês/ano no seletor |
| **Resultado esperado** | Dados da apuração atualizam para o período selecionado |
| **Resultado esperado** | Sem reload completo da página (Alpine.js reativo) |

### CT-020 — DARFs exibem valor e código de receita

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Acesso a `/imposto-renda/darf`, mês com IR devido |
| **Ação** | Observar tabela de DARFs |
| **Resultado esperado** | Cada DARF exibe: código de receita, competência, valor, vencimento |
| **Resultado esperado** | Código 6015 para Ações, 3317 para FIIs |

### CT-021 — Histórico anual exibe 12 meses

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Acesso a `/imposto-renda/historico` |
| **Ação** | Observar tabela/gráfico |
| **Resultado esperado** | 12 meses listados (Jan a Dez do ano selecionado) |
| **Resultado esperado** | Total anual calculado corretamente (soma dos meses) |

### CT-022 — DIRPF exibe bens e direitos

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Acesso a `/imposto-renda/dirpf`, usuário com posições |
| **Ação** | Observar tabela de bens |
| **Resultado esperado** | Cada ativo exibe: código, discriminação, valor em 31/12 |
| **Resultado esperado** | Valores em moeda BRL formatados corretamente (R$ X.XXX,XX) |

---

## Módulo Portfolio — Rentabilidade

**Arquivo:** `specs/portfolio/12-rentabilidade.spec.js`  
**Rotas:** `/analises/rentabilidade`, `/analises/alocacao`, `/analises/evolucao`, `/analises/performance`

### CT-023 — Rentabilidade exibe TWR e MWR

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Usuário com histórico (seed test_full tem TWR 81.14%, MWR -65.4%) |
| **Ação** | Acessar `/analises/rentabilidade` |
| **Resultado esperado** | TWR exibido com % |
| **Resultado esperado** | MWR exibido com % |
| **Resultado esperado** | Benchmark CDI exibido para comparação |

### CT-024 — Alocação exibe distribuição por classe

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Acesso a `/analises/alocacao` |
| **Ação** | Observar gráfico/tabela |
| **Resultado esperado** | Percentuais somam ~100% |
| **Resultado esperado** | Categorias: RF, RV, FII, ETF, Cripto ou similar |

### CT-025 — Evolução patrimonial exibe série histórica

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Acesso a `/analises/evolucao`, seed test_full com 12 snapshots |
| **Ação** | Observar gráfico de evolução |
| **Resultado esperado** | Série histórica com múltiplos pontos exibida |
| **Resultado esperado** | Valores monetários formatados (R$ X.XXX,XX) |

### CT-026 — Performance exibe métricas de risco

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Acesso a `/analises/performance` |
| **Ação** | Observar métricas |
| **Resultado esperado** | Sharpe Ratio exibido |
| **Resultado esperado** | Drawdown máximo exibido |
| **Resultado esperado** | Top ativos por rentabilidade listados |

---

## Módulo Ferramentas — Calculadora IR

**Arquivo:** `specs/ferramentas/13-calculadora-ir.spec.js`  
**Rota:** `/ferramentas/calculadora-ir`

### CT-027 — Formulário calcula IR client-side para Ações

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Na tela da calculadora |
| **Ação** | Preencher: tipo=Ação, preço venda=R$50,00, quantidade=100, preço médio=R$30,00 |
| **Resultado esperado** | Ganho bruto = R$ 2.000,00 |
| **Resultado esperado** | IR (15%) = R$ 300,00 |
| **Resultado esperado** | Ganho líquido = R$ 1.700,00 |

### CT-028 — Isenção aplicada para vendas ≤ R$20.000 em Ações

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Calculadora, tipo=Ação |
| **Ação** | Preencher: preço venda=R$25,00, quantidade=100 (total R$2.500 < R$20k) |
| **Resultado esperado** | IR = R$ 0,00 (isento) |
| **Resultado esperado** | Indicador "Isento" visível |

### CT-029 — Alíquota de FII é 20%

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Calculadora, tipo=FII |
| **Ação** | Preencher: preço venda=R$120, quantidade=100, PM=R$100 |
| **Resultado esperado** | Ganho bruto = R$ 2.000,00 |
| **Resultado esperado** | IR (20%) = R$ 400,00 |

### CT-030 — Day Trade tem alíquota 20% para Ações

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Calculadora, tipo=Ação, marcar Day Trade |
| **Ação** | Preencher valores com lucro |
| **Resultado esperado** | Alíquota exibida: 20% (e não 15%) |

### CT-031 — Compensação de prejuízo reduz base de cálculo

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Calculadora com campo de prejuízo acumulado |
| **Ação** | Preencher prejuízo acumulado=R$500, ganho=R$1.000 |
| **Resultado esperado** | Base de cálculo = R$500 (1.000 - 500) |
| **Resultado esperado** | IR calculado sobre R$500 |

---

## Módulo Ferramentas — Screener

**Arquivo:** `specs/ferramentas/14-screener-filtros.spec.js`  
**Rota:** `/ferramentas/screener`

### CT-032 — Screener carrega lista de ativos

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Acesso a `/ferramentas/screener` |
| **Ação** | Aguardar carregamento |
| **Resultado esperado** | Tabela com ativos exibida |
| **Resultado esperado** | Colunas: Ticker, Tipo, Preço, DY, P/VP, P/L |

### CT-033 — Filtro por tipo filtra corretamente

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Screener com ativos carregados |
| **Ação** | Selecionar filtro "FII" |
| **Resultado esperado** | Apenas ativos do tipo FII exibidos na tabela |
| **Resultado esperado** | Contador de resultados atualizado |

### CT-034 — Filtro por DY mínimo funciona

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Screener carregado |
| **Ação** | Preencher DY mínimo = "5" |
| **Resultado esperado** | Apenas ativos com DY ≥ 5% exibidos |
| **Resultado esperado** | Ativos com DY null não exibidos (ou exibidos com indicador) |

### CT-035 — Filtro por P/VP máximo funciona

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Screener carregado |
| **Ação** | Preencher P/VP máximo = "1" |
| **Resultado esperado** | Apenas ativos com P/VP ≤ 1 exibidos |

### CT-036 — Múltiplos filtros combinados

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Screener carregado |
| **Ação** | Tipo=FII + DY mínimo=5 |
| **Resultado esperado** | Intersecção: somente FIIs com DY ≥ 5% |

### CT-037 — Limpar filtros restaura lista completa

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Filtros aplicados |
| **Ação** | Clicar em "Limpar" ou "Resetar filtros" |
| **Resultado esperado** | Lista retorna ao estado inicial com todos os ativos |

---

## Módulo Ferramentas — Simulador

**Arquivo:** `specs/ferramentas/15-simulador.spec.js`  
**Rota:** `/ferramentas/simulador`

### CT-038 — Simulador calcula montante com juros compostos

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Na tela do simulador |
| **Ação** | Preencher: aporte inicial=R$10.000, aporte mensal=R$500, taxa=1%/mês, prazo=12 meses |
| **Resultado esperado** | Montante final > R$16.000 (com juros compostos) |
| **Resultado esperado** | Resultado exibido formatado em R$ |

### CT-039 — Tabela de marcos exibe marcos patrimoniais

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Simulação preenchida |
| **Ação** | Observar tabela de marcos |
| **Resultado esperado** | Marcos exibidos: R$50k, R$100k, R$500k, R$1M (ou similar) |
| **Resultado esperado** | Data estimada para cada marco calculada |

### CT-040 — Simulador considera inflação quando preenchida

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Simulador com campo de inflação |
| **Ação** | Preencher inflação = 5% a.a. |
| **Resultado esperado** | Montante real (descontada inflação) menor que montante nominal |
| **Resultado esperado** | Ambos exibidos para comparação |

### CT-041 — Alterar parâmetros recalcula em tempo real

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Simulação em andamento |
| **Ação** | Alterar aporte mensal |
| **Resultado esperado** | Resultado recalculado automaticamente (sem clicar em botão) |

---

## Módulo Relatórios — Exportação CSV

**Arquivo:** `specs/relatorios/16-exportacao-csv.spec.js`  
**Rotas:** `/relatorios/mensal`, `/relatorios/anual`, `/relatorios/extrato`, `/relatorios/exportar/csv`

### CT-042 — Relatório mensal exibe dados do período

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Acesso a `/relatorios/mensal`, seed com transações |
| **Ação** | Selecionar mês com transações |
| **Resultado esperado** | Transações do mês listadas |
| **Resultado esperado** | Total de entradas/saídas calculado |

### CT-043 — Filtro de período em extrato funciona

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Acesso a `/relatorios/extrato` |
| **Ação** | Selecionar data início e fim |
| **Resultado esperado** | Apenas transações do período exibidas |
| **Resultado esperado** | Transações fora do período não aparecem |

### CT-044 — Exportação CSV dispara download

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Acesso a `/relatorios/exportar/csv` |
| **Ação** | Clicar no botão de exportar CSV |
| **Resultado esperado** | Download de arquivo `.csv` iniciado |
| **Resultado esperado** | Arquivo tem extensão .csv |

### CT-045 — Relatório anual exibe resumo por mês

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Acesso a `/relatorios/anual`, seed com histórico |
| **Ação** | Selecionar ano |
| **Resultado esperado** | 12 linhas (Jan-Dez) exibidas |
| **Resultado esperado** | Total do ano calculado na linha de rodapé |

---

## Regressão — Fluxo Ponta a Ponta

**Arquivo:** `specs/regressao/17-fluxo-completo.spec.js`

### CT-046 — Fluxo completo: Compra → Dashboard → Posição

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Usuário logado |
| **Ação 1** | Registrar compra de 1 ação de ITUB4 a R$25,00 |
| **Ação 2** | Navegar para `/dashboard/` |
| **Ação 3** | Navegar para posições do portfolio |
| **Resultado esperado** | ITUB4 aparece nas posições com PM R$25,00 |
| **Teardown** | Remover transação via API |

### CT-047 — Fluxo fiscal: Transação → IR → DARF

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Seed test_full com vendas tributáveis |
| **Ação 1** | Acessar apuração mensal |
| **Ação 2** | Verificar se há IR calculado |
| **Ação 3** | Navegar para DARFs |
| **Resultado esperado** | DARF correspondente ao IR calculado existe |
| **Resultado esperado** | Valor da DARF bate com IR apurado |

### CT-048 — Navegação entre módulos preserva sessão

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Usuário logado |
| **Ação** | Navegar sequencialmente: Dashboard → Operações → Fiscal → Ferramentas → Relatórios |
| **Resultado esperado** | Nenhum redirect para login durante a navegação |
| **Resultado esperado** | Dados do usuário persistem em cada tela |

### CT-049 — Logout invalida sessão

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Usuário logado |
| **Ação 1** | Clicar em logout |
| **Ação 2** | Tentar acessar `/dashboard/` diretamente |
| **Resultado esperado** | Redirect para `/auth/login` |
| **Resultado esperado** | Dashboard não carrega sem autenticação |

### CT-050 — Comparador exibe dados de 2 ativos lado a lado

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Acesso a `/ferramentas/comparador` |
| **Ação** | Selecionar PETR4 e VALE3 para comparar |
| **Resultado esperado** | Dados de ambos exibidos em colunas lado a lado |
| **Resultado esperado** | Métricas: P/L, P/VP, DY, Preço |

---

## Módulo Ativos — Catálogo por Categoria

**Arquivo:** `specs/ativos/18-ativos-logica.spec.js`  
**Rotas:** `/ativos/acoes`, `/ativos/fiis`, `/ativos/etfs`, `/ativos/renda-fixa`, `/ativos/cripto`

### CT-051 — Ações: lista com ticker e tipo

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Acesso a `/ativos/acoes` |
| **Ação** | Aguardar carregamento |
| **Resultado esperado** | Lista com tickers (ON/PN) e dados fundamentalistas |

### CT-052 — Ações: campo de busca funcional

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Catálogo de ações carregado |
| **Ação** | Verificar presença de campo de busca |
| **Resultado esperado** | Input de busca/filtro visível e habilitado |

### CT-053 — Ações: dados fundamentalistas (P/L, P/VP, DY)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Catálogo de ações carregado |
| **Resultado esperado** | Preço, P/L, P/VP ou DY exibidos na listagem |

### CT-054 — FIIs: itens da categoria FII

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Acesso a `/ativos/fiis` |
| **Resultado esperado** | Terminologia FII: fundo, imobiliário, cota |

### CT-055 — FIIs: dividend yield disponível

| Campo | Valor |
|-------|-------|
| **Resultado esperado** | DY ou rendimento com % exibido |

### CT-056 — ETFs: lista com dados

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Acesso a `/ativos/etfs` |
| **Resultado esperado** | Tickers de ETF (IVVB, BOVA, etc.) ou dados de índice |

### CT-057 — Renda Fixa: ativos de RF

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Acesso a `/ativos/renda-fixa` |
| **Resultado esperado** | CDI, IPCA, Tesouro, LCI/LCA ou similar |

### CT-058 — Cripto: ativos digitais

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Acesso a `/ativos/cripto` |
| **Resultado esperado** | BTC, ETH, USDT ou terminologia cripto |

### CT-059 — Menu de Ativos: links para todas as categorias

| Campo | Valor |
|-------|-------|
| **Resultado esperado** | ≥ 4 links `/ativos/*` no menu de navegação |

---

## Módulo Planos — Compra e Venda

**Arquivo:** `specs/planos/19-planos-logica.spec.js`  
**Rotas:** `/planos-compra/`, `/planos-venda/`

### CT-060 — Planos de Compra: lista do usuário

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Usuário com planos (seed test_full: 4 planos compra) |
| **Resultado esperado** | Lista com ticker, meta e aporte exibidos |

### CT-061 — Planos de Compra: dados do plano (valor, progresso)

| Campo | Valor |
|-------|-------|
| **Resultado esperado** | R$, %, meta ou progresso visíveis |

### CT-062 — Planos de Compra: ação de criar novo

| Campo | Valor |
|-------|-------|
| **Resultado esperado** | Botão/link "Novo", "Criar" ou "Adicionar" presente |

### CT-063 — Planos de Compra: detalhe do plano acessível

| Campo | Valor |
|-------|-------|
| **Ação** | Clicar em link de detalhe de um plano existente |
| **Resultado esperado** | Página de detalhe carrega sem 404/login redirect |

### CT-064 — Planos de Venda: lista do usuário

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Usuário com planos (seed test_full: 3 planos venda) |
| **Resultado esperado** | Stop Loss, Stop Gain, preço alvo visíveis |

### CT-065 — Planos de Venda: preços de saída

| Campo | Valor |
|-------|-------|
| **Resultado esperado** | Terminologia stop/gain/loss/alvo presente |

### CT-066 — Planos de Venda: ação de criar novo

| Campo | Valor |
|-------|-------|
| **Resultado esperado** | Botão/link de criação presente |

---

## Módulo Alertas — Todos + Sub-páginas

**Arquivo:** `specs/alertas/20-alertas-logica.spec.js`  
**Rotas:** `/alertas/`, `/alertas/preco`, `/alertas/dividendos`, `/alertas/personalizados`

### CT-067 — Todos os alertas: lista do usuário

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Usuário com alertas (seed test_full: 5 alertas) |
| **Resultado esperado** | Lista com ticker, tipo e condição exibidos |

### CT-068 — Alertas: botão de criação presente

| Campo | Valor |
|-------|-------|
| **Resultado esperado** | Botão "Novo", "Criar" ou "Adicionar" disponível |

### CT-069 — Alertas de Preço: rota carrega com conteúdo

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Acesso a `/alertas/preco` |
| **Resultado esperado** | Sem 404, sem redirect login; conteúdo de alerta de preço |

### CT-070 — Alertas de Dividendos: rota carrega com conteúdo

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Acesso a `/alertas/dividendos` |
| **Resultado esperado** | Sem 404; terminologia de dividendo/provento |

### CT-071 — Alertas Personalizados: rota carrega com conteúdo

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Acesso a `/alertas/personalizados` |
| **Resultado esperado** | Sem 404; conteúdo de alerta personalizado/condição |

### CT-072 — Alertas: indicador de status (ativo/inativo)

| Campo | Valor |
|-------|-------|
| **Resultado esperado** | Badge ou texto "ativo"/"inativo"/"habilitado" visível |

### CT-073 — Alertas: campo de busca ou filtro presente

| Campo | Valor |
|-------|-------|
| **Resultado esperado** | Input ou select para filtrar alertas disponível |

---

## Mapeamento Specs → Arquivos

| Arquivo | CTs | Módulo |
|---------|-----|--------|
| `specs/operacoes/08-compra-logica.spec.js` | CT-001 a CT-008 | Compra |
| `specs/operacoes/09-venda-logica.spec.js` | CT-009 a CT-013 | Venda |
| `specs/operacoes/10-importacao-b3.spec.js` | CT-014 a CT-016 | Importação |
| `specs/fiscal/11-ir-calculo.spec.js` | CT-017 a CT-022 | IR e DARF |
| `specs/portfolio/12-rentabilidade.spec.js` | CT-023 a CT-026 | Portfolio |
| `specs/ferramentas/13-calculadora-ir.spec.js` | CT-027 a CT-031 | Calculadora IR |
| `specs/ferramentas/14-screener-filtros.spec.js` | CT-032 a CT-037 | Screener |
| `specs/ferramentas/15-simulador.spec.js` | CT-038 a CT-041 | Simulador |
| `specs/relatorios/16-exportacao-csv.spec.js` | CT-042 a CT-045 | Relatórios |
| `specs/regressao/17-fluxo-completo.spec.js` | CT-046 a CT-050 | Regressão E2E |
| `specs/ativos/18-ativos-logica.spec.js` | CT-051 a CT-059 | Ativos (5 categorias) |
| `specs/planos/19-planos-logica.spec.js` | CT-060 a CT-066 | Planos Compra/Venda |
| `specs/alertas/20-alertas-logica.spec.js` | CT-067 a CT-073 | Alertas (4 rotas) |

**Total: 73 casos de teste de lógica de negócio**

---

## Regras de Implementação dos Specs

1. **Teardown obrigatório** para qualquer teste que crie dados (compra, venda)
2. **Seed test_full** deve estar carregado antes de executar a suite completa
3. **Dados determinísticos**: assertions sempre baseadas em valores conhecidos do seed
4. **Sem dependência entre testes**: cada `test()` deve ser independente
5. **`networkidle` antes de assertions** em telas com Alpine.js e chamadas de API
6. **Filtrar `Failed to fetch`** nos testes de console (race condition conhecida)

---

*Criado em: 16/06/2026 | Branch: feature/testes-e2e-v3*
