# Documentação do Sistema Exitus

## 📁 Estrutura de Documentos

### 🎯 Visão e Estratégia
- **[VISION.md](VISION.md)** — Visão de negócio, proposta de valor, roadmap funcional
- **[PERSONAS.md](PERSONAS.md)** — **Manual de Operação da IA** — define como a assistente deve se comportar, fontes de verdade, fluxo de trabalho

### 🏗️ Arquitetura e Design
- **[ARCHITECTURE.md](ARCHITECTURE.md)** — Arquitetura técnica, containers, stack, princípios de design
- **[MODULES.md](MODULES.md)** — Status dos módulos M0-M7, endpoints por módulo, roadmap de implementação
- **[CODING_STANDARDS.md](CODING_STANDARDS.md)** — Padrões de codificação (snake_case obrigatório)

### 🔌 APIs e Contratos
- **[API_REFERENCE.md](API_REFERENCE.md)** — **Referência completa** de todas as APIs com exemplos cURL
- **[ENUMS.md](ENUMS.md)** — Enums do sistema (TipoAtivo, TipoOperacao, etc.) com mapeamentos

### 🗄️ Database e Dados
- **[EXITUS_DB_STRUCTURE.txt](EXITUS_DB_STRUCTURE.txt)** — Schema completo do PostgreSQL (21 tabelas, 86+ índices)
- **[SEEDS.md](SEEDS.md)** — Dados iniciais, credenciais de desenvolvimento, usuários teste

### 📋 Operações e Manuais
- **[OPERATIONS_RUNBOOK.md](OPERATIONS_RUNBOOK.md)** — **Manual de Operações** — deploy, troubleshooting, scripts úteis
- **[USER_GUIDE.md](USER_GUIDE.md)** — **Guia do Usuário Final** — como usar o sistema (dashboards, operações)
- **[CHANGELOG.md](CHANGELOG.md)** — Histórico de versões, GAPs registrados, roadmap futuro
- **[ROADMAP.md](ROADMAP.md)** — Roadmap de implementação — GAPs identificados e plano de desenvolvimento

---

## 🔄 Como Usar Esta Documentação

### Para Desenvolvedores/Manutenção
1. **PERSONAS.md** — Entender como interagir com a IA assistente
2. **API_REFERENCE.md** — Contratos dos endpoints
3. **ARCHITECTURE.md** — Decisões arquiteturais
4. **CHANGELOG.md** — O que mudou recentemente
5. **ROADMAP.md** — O que falta implementar e plano de desenvolvimento

### Para Operações/DevOps
1. **OPERATIONS_RUNBOOK.md** — Comandos e troubleshooting
2. **SEEDS.md** — Credenciais e dados de teste
3. **MODULES.md** — Status de cada módulo

### Para Usuários Finais
1. **USER_GUIDE.md** — Como usar o sistema
2. **VISION.md** — O que o sistema oferece

### Para IA Assistente (Cascade/Perplexity)
1. **PERSONAS.md** — **Manual de operação principal**
2. **API_REFERENCE.md** — Contratos para validação
3. **ENUMS.md** — Valores válidos para campos
4. **CODING_STANDARDS.md** — snake_case obrigatório

**🚨 REGRA CRÍTICA:** A IA pode opinar e propor ideias, mas **NUNCA** deve executar mudanças sem aprovação explícita. Fluxo: 1) Propor → 2) Aguardar "APROVADO" → 3) Implementar

---

## 📈 Fluxo de Trabalho com IA

```
1. PERSONAS.md define o comportamento da IA
2. IA consulta as Fontes de Verdade (API_REFERENCE, ENUMS, etc.)
3. IA segue o fluxo: ANÁLISE → PROPOSTA → APROVADO → IMPLEMENTAÇÃO
4. CHANGELOG.md registra todos os GAPs e correções
```

---

## 🚨 Importante

- **PERSONAS.md** é o manual de controle da IA — não altere sem entender o impacto
- **API_REFERENCE.md** é sempre a fonte da verdade para contratos de API
- **CHANGELOG.md** mantém o histórico de todas as decisões técnicas
- **OPERATIONS_RUNBOOK.md** contém comandos que podem afetar o sistema em produção

---

*Atualizado: 27 de Fevereiro de 2026*  
*Versão: 1.0 — Estrutura organizada por propósito*
