# MISSION: FRONTEND RE-ENGINEERING & UX REVAMP (EXITUS SYSTEM)

**Persona:** veja persona 2 em docs/PERSONAS.md.

**Contexto:**
O sistema Exitus está com um backend robusto em Python/Flask e PostgreSQL, com 491 testes aprovados. Agora, preciso reavaliar e remodelar o frontend (atualmente em HTMX + Alpine.js + Tailwind) para elevar o nível de profissionalismo, usabilidade e suporte a investimentos globais (RF e RV, BRL e USD).

**Regras de Operação (LEITURA OBRIGATÓRIA):**
Antes de propor qualquer mudança, você deve ler e processar os seguintes documentos para garantir alinhamento técnico:
1. `API_REFERENCE.md` e `ENUMS.md`: Para entender os contratos de dados e tipos de ativos.
2. `EXITUS_DB_STRUCTURE.txt`: Para conhecer os campos reais disponíveis.
3. `ROADMAP.md` e `VISION.md`: Para entender onde o sistema está e para onde vai.
4. `CODING_STANDARDS.md`: Para manter o padrão de nomenclatura e integração.

**Objetivos da Reavaliação:**
1. **Consistência de Stack:** Avalie se HTMX + Alpine.js continua sendo a melhor escolha para este nível de complexidade ou se sugere uma transição (ex: Next.js). Justifique sua visão.
2. **Dashboard Global:** Proponha uma interface que diferencie visualmente ativos nacionais e internacionais, com foco em métricas de performance e alocação geográfica.
3. **Componentização:** Planeje a criação de fragmentos Jinja2 reutilizáveis (cards, badges de status, tabelas dinâmicas) que consumam as rotas existentes.
4. **UX de Dividendos e IR:** Melhore a visualização baseando-se nos GAPs `EXITUS-DIVCALENDAR-001.md` e `EXITUS-IR-001.md`.

**🚨 REGRA CRÍTICA DE FLUXO:**
Não execute alterações de código agora. Siga o fluxo:
1. Realize uma ANÁLISE profunda da estrutura atual do frontend.
2. Apresente um **PLANO DE REMODELAGEM VISUAL** detalhado.
3. Aguarde minha aprovação explícita ("APROVADO") para cada etapa da implementação.

**Ação Imediata:**
Confirme que leu os arquivos mencionados e apresente sua análise inicial sobre a stack atual e a proposta de design para o Dashboard Principal.
