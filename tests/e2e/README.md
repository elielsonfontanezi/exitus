# 🧪 Testes E2E - Frontend V2.0

Testes End-to-End do Frontend V2.0 usando Playwright.

## 📋 Fase 1 - Testes de Fumaça (Semana 1)

### Status Atual
- ✅ Estrutura de testes criada
- ✅ Configuração Playwright
- ✅ Testes de fumaça: Dashboard, Imposto Renda
- ⏳ Instalação de dependências
- ⏳ Execução dos testes

## 🚀 Setup Rápido

```bash
# 1. Instalar dependências
cd tests/e2e
npm install

# 2. Instalar browsers
npm run install-browsers

# 3. Executar testes
npm test
```

## 📊 Comandos Disponíveis

```bash
# Executar todos os testes
npm test

# Executar com interface gráfica
npm run test:headed

# Executar em modo debug
npm run test:debug

# Executar apenas smoke tests
npm run test:smoke

# Executar apenas testes críticos
npm run test:critical

# Executar em browser específico
npm run test:chromium
npm run test:firefox
npm run test:webkit

# Executar testes mobile
npm run test:mobile

# Ver relatório HTML
npm run report
```

## 📁 Estrutura

```
tests/e2e/
├── playwright.config.js    # Configuração principal
├── package.json            # Dependências
├── specs/                  # Testes organizados
│   ├── smoke/             # Testes de fumaça (Fase 1)
│   │   ├── 01-dashboard.spec.js
│   │   ├── 02-imposto-renda.spec.js
│   │   └── ...
│   ├── functional/        # Testes funcionais (Fase 2)
│   └── ux/               # Testes de UX (Fase 3)
├── reports/              # Relatórios gerados
│   ├── html/
│   ├── results.json
│   └── junit.xml
└── README.md
```

## 🎯 Testes de Fumaça Implementados

### Dashboard (17 testes)
- ✅ Carregamento < 3s
- ✅ Cards de resumo
- ✅ Gráficos renderizando
- ✅ Currency toggle
- ✅ Responsividade
- ✅ Mock data fallback

### Imposto Renda (7 testes)
- ✅ Carregamento < 3s
- ✅ 4 cards de resumo
- ✅ 4 abas funcionais
- ✅ Cálculo automático
- ✅ Lista de DARFs
- ✅ Calculadora

## 📊 Cobertura Planejada

| Tela | Testes | Status |
|------|--------|--------|
| Dashboard | 17 | ✅ |
| Imposto Renda | 7 | ✅ |
| Planos Compra | 0 | ⏳ |
| Planos Venda | 0 | ⏳ |
| Portfolios | 0 | ⏳ |
| Transações | 0 | ⏳ |
| Relatórios | 0 | ⏳ |
| ... | ... | ⏳ |

**Total:** 24/170 testes (14%)

## 🐛 Relatório de Bugs

Nenhum bug identificado ainda. Aguardando execução dos testes.

## 📈 Próximos Passos

1. ✅ Criar estrutura de testes
2. ✅ Implementar testes Dashboard
3. ✅ Implementar testes IR
4. ⏳ Instalar dependências
5. ⏳ Executar testes
6. ⏳ Analisar resultados
7. ⏳ Criar testes para demais telas

## 📞 Suporte

Para dúvidas ou problemas:
- Documentação: `docs/ROADMAP_TESTES_FRONTEND.md`
- Slack: #frontend-tests
