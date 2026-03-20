# 🚀 Week 1: Design System Moderno - Implementação Prática

## 📋 Objetivo da Semana

Transformar o design system atual de corporativo para moderno, com cores emocionais, tipografia acessível e componentes interativos.

---

## 🎨 **DIA 1-2: FUNDAÇÃO VISUAL**

### **🌈 1.1 Implementar Cores Emocionais**

#### **Arquivo: `/frontend/app/static/css/design-system.css`**

```css
/* Adicionar ao final do arquivo existente */

/* ===== CORES EMOCIONAIS ===== */
:root {
  /* Cores Primárias - Inspiradas em Apps Populares */
  --color-primary-50: #eef2ff;
  --color-primary-500: #6366f1;  /* Índigo vibrante */
  --color-primary-600: #4f46e5;
  --color-primary-700: #4338ca;
  
  --color-secondary-50: #faf5ff;
  --color-secondary-500: #8b5cf6;  /* Roxo suave */
  --color-secondary-600: #7c3aed;
  --color-secondary-700: #6d28d9;
  
  /* Cores Semânticas */
  --color-success-50: #ecfdf5;
  --color-success-500: #10b981;  /* Verde forte */
  --color-success-600: #059669;
  
  --color-attention-50: #fffbeb;
  --color-attention-500: #f59e0b;  /* Laranja vibrante */
  --color-attention-600: #d97706;
  
  --color-danger-50: #fef2f2;
  --color-danger-500: #ef4444;  /* Vermelho claro */
  --color-danger-600: #dc2626;
  
  /* Gradientes Modernos */
  --gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --gradient-success: linear-gradient(135deg, #10b981 0%, #059669 100%);
  --gradient-card: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
  --gradient-hero: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  
  /* Sombras Modernas */
  --shadow-soft: 0 2px 15px -3px rgba(0, 0, 0, 0.07), 0 10px 20px -2px rgba(0, 0, 0, 0.04);
  --shadow-medium: 0 4px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  --shadow-strong: 0 10px 40px -10px rgba(0, 0, 0, 0.15), 0 4px 25px -5px rgba(0, 0, 0, 0.1);
}

/* ===== UTILITÁRIAS DE COR ===== */
.bg-primary-50 { background-color: var(--color-primary-50); }
.bg-primary-500 { background-color: var(--color-primary-500); }
.bg-primary-600 { background-color: var(--color-primary-600); }
.bg-secondary-50 { background-color: var(--color-secondary-50); }
.bg-secondary-500 { background-color: var(--color-secondary-500); }
.bg-success-50 { background-color: var(--color-success-50); }
.bg-success-500 { background-color: var(--color-success-500); }
.bg-attention-50 { background-color: var(--color-attention-50); }
.bg-attention-500 { background-color: var(--color-attention-500); }
.bg-danger-50 { background-color: var(--color-danger-50); }
.bg-danger-500 { background-color: var(--color-danger-500); }

.text-primary-500 { color: var(--color-primary-500); }
.text-primary-600 { color: var(--color-primary-600); }
.text-secondary-500 { color: var(--color-secondary-500); }
.text-success-500 { color: var(--color-success-500); }
.text-success-600 { color: var(--color-success-600); }
.text-attention-500 { color: var(--color-attention-500); }
.text-attention-600 { color: var(--color-attention-600); }
.text-danger-500 { color: var(--color-danger-500); }
.text-danger-600 { color: var(--color-danger-600); }

/* ===== GRADIENTES ===== */
.bg-gradient-primary { background: var(--gradient-primary); }
.bg-gradient-success { background: var(--gradient-success); }
.bg-gradient-card { background: var(--gradient-card); }
.bg-gradient-hero { background: var(--gradient-hero); }

/* ===== SOMBRAS ===== */
.shadow-soft { box-shadow: var(--shadow-soft); }
.shadow-medium { box-shadow: var(--shadow-medium); }
.shadow-strong { box-shadow: var(--shadow-strong); }
```

### **📝 1.2 Tipografia Acessível**

```css
/* ===== TIPOGRAFIA ESCALONADA ===== */
.text-xs { font-size: 12px; line-height: 16px; }
.text-sm { font-size: 14px; line-height: 20px; }
.text-base { font-size: 16px; line-height: 24px; }
.text-lg { font-size: 18px; line-height: 28px; }
.text-xl { font-size: 20px; line-height: 30px; }
.text-2xl { font-size: 24px; line-height: 36px; } /* Aumentado de 20px */
.text-3xl { font-size: 30px; line-height: 40px; } /* Aumentado de 24px */
.text-4xl { font-size: 36px; line-height: 48px; } /* Aumentado de 28px */

/* ===== PESOS E CONTRASTES ===== */
.font-light { font-weight: 300; }
.font-normal { font-weight: 400; }
.font-medium { font-weight: 500; }
.font-semibold { font-weight: 600; }
.font-bold { font-weight: 700; }

/* ===== HIERARQUIA CLARA ===== */
h1 { @apply text-4xl font-bold text-gray-900 mb-4; }
h2 { @apply text-3xl font-semibold text-gray-900 mb-3; }
h3 { @apply text-2xl font-semibold text-gray-900 mb-2; }
h4 { @apply text-xl font-medium text-gray-900 mb-1; }
h5 { @apply text-lg font-medium text-gray-900 mb-1; }
h6 { @apply text-base font-medium text-gray-900 mb-1; }

/* ===== CONTRASTE GARANTIDO ===== */
.text-gray-900 { color: #111827; } /* Mais escuro para melhor contraste */
.text-gray-800 { color: #1f2937; }
.text-gray-700 { color: #374151; }
.text-gray-600 { color: #4b5563; }
.text-gray-500 { color: #6b7280; }
.text-gray-400 { color: #9ca3af; }
.text-gray-300 { color: #d1d5db; }
```

---

## 🎯 **DIA 3-4: COMPONENTES BASE**

### **🃏 2.1 Cards Modernos**

```css
/* ===== CARDS MODERNOS ===== */
.card-moderno {
  @apply bg-white rounded-2xl shadow-soft hover:shadow-medium;
  @apply transition-all duration-300 hover:-translate-y-1;
  @apply border border-gray-100;
}

.card-header {
  @apply p-6 border-b border-gray-100;
}

.card-body {
  @apply p-6;
}

.card-footer {
  @apply p-6 border-t border-gray-100 bg-gray-50;
}

/* ===== VARIANTS DE CARDS ===== */
.card-ativo {
  @apply card-moderno;
  @apply hover:scale-[1.02] cursor-pointer;
}

.card-ativo .header {
  @apply flex justify-between items-start mb-4;
}

.card-ativo .ticker {
  @apply text-lg font-bold text-gray-900;
}

.card-ativo .categoria {
  @apply text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded-lg;
}

.card-ativo .preco {
  @apply text-2xl font-bold text-gray-900;
}

.card-ativo .variacao.positiva {
  @apply text-success-600 font-medium;
}

.card-ativo .variacao.negativa {
  @apply text-danger-600 font-medium;
}

.card-metrica {
  @apply bg-white rounded-xl p-4 shadow-soft;
  @apply border border-gray-100;
}

.card-metrica .valor {
  @apply text-2xl font-bold text-gray-900;
}

.card-metrica .descricao {
  @apply text-sm text-gray-500 mt-1;
}

.card-metrica.positiva {
  @apply bg-success-50 border-success-200;
}

.card-metrica.positiva .valor {
  @apply text-success-600;
}
```

### **🔘 2.2 Botões e Ícones**

```css
/* ===== BOTÕES MODERNOS ===== */
.btn {
  @apply px-4 py-2 rounded-xl font-medium transition-all duration-200;
  @apply focus:outline-none focus:ring-2 focus:ring-offset-2;
  @apply cursor-pointer inline-flex items-center justify-center;
  @apply hover:scale-105 active:scale-95;
}

.btn-primario {
  @apply bg-primary-500 text-white hover:bg-primary-600;
  @apply focus:ring-primary-500 shadow-soft hover:shadow-medium;
}

.btn-secundario {
  @apply bg-gray-100 text-gray-700 hover:bg-gray-200;
  @apply focus:ring-gray-500;
}

.btn-sucesso {
  @apply bg-success-500 text-white hover:bg-success-600;
  @apply focus:ring-success-500 shadow-soft hover:shadow-medium;
}

.btn-atencao {
  @apply bg-attention-500 text-white hover:bg-attention-600;
  @apply focus:ring-attention-500 shadow-soft hover:shadow-medium;
}

.btn-perigo {
  @apply bg-danger-500 text-white hover:bg-danger-600;
  @apply focus:ring-danger-500 shadow-soft hover:shadow-medium;
}

/* ===== TAMANHOS ===== */
.btn-pequeno { @apply px-3 py-1.5 text-sm; }
.btn-medio { @apply px-4 py-2 text-base; }
.btn-grande { @apply px-6 py-3 text-lg; }

/* ===== BOTÕES DE AÇÃO RÁPIDA ===== */
.btn-acao {
  @apply btn-grande bg-gradient-to-r text-white rounded-2xl;
  @apply flex flex-col items-center space-y-2 p-6;
  @apply shadow-medium hover:shadow-strong;
}

.btn-acao.comprar {
  @apply from-success-500 to-success-600 hover:from-success-600 hover:to-success-700;
}

.btn-acao.vender {
  @apply from-danger-500 to-danger-600 hover:from-danger-600 hover:to-danger-700;
}

.btn-acao.depositar {
  @apply from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700;
}

/* ===== ÍCONES ===== */
.icone {
  @apply w-6 h-6 flex items-center justify-center;
}

.icone-grande {
  @apply w-8 h-8 flex items-center justify-center;
}

.icone-gigante {
  @apply w-12 h-12 flex items-center justify-center text-2xl;
}
```

---

## 🌊 **DIA 5: ANIMAÇÕES E TRANSIÇÕES**

### **✨ 3.1 Microinterações**

```css
/* ===== ANIMAÇÕES SUAVES ===== */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { 
    opacity: 0;
    transform: translateY(20px);
  }
  to { 
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes scaleIn {
  from { 
    opacity: 0;
    transform: scale(0.95);
  }
  to { 
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes pulseSoft {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.8; }
}

/* ===== CLASSES DE ANIMAÇÃO ===== */
.animate-fade-in {
  animation: fadeIn 0.3s ease-in-out;
}

.animate-slide-up {
  animation: slideUp 0.4s ease-out;
}

.animate-scale-in {
  animation: scaleIn 0.2s ease-out;
}

.animate-pulse-soft {
  animation: pulseSoft 2s infinite;
}

/* ===== DELAYS PARA ENTRADAS SUCESSIVAS ===== */
.animate-delay-100 { animation-delay: 0.1s; }
.animate-delay-200 { animation-delay: 0.2s; }
.animate-delay-300 { animation-delay: 0.3s; }
.animate-delay-400 { animation-delay: 0.4s; }
.animate-delay-500 { animation-delay: 0.5s; }

/* ===== HOVER STATES ===== */
.hover-lift {
  @apply transition-transform duration-300 hover:-translate-y-1;
}

.hover-scale {
  @apply transition-transform duration-200 hover:scale-105;
}

.hover-glow {
  @apply transition-shadow duration-300 hover:shadow-medium;
}

/* ===== LOADING STATES ===== */
.loading-skeleton {
  @apply bg-gray-200 rounded animate-pulse;
}

.loading-skeleton.text {
  @apply h-4 w-3/4;
}

.loading-skeleton.title {
  @apply h-6 w-1/2;
}

.loading-skeleton.card {
  @apply h-32 w-full;
}
```

---

## 🧪 **TESTES RÁPIDOS - DIA 5**

### **📱 4.1 Validação Visual**

#### **Teste 1: Cores**
```html
<!-- Adicionar temporariamente ao dashboard para teste -->
<div class="p-8 space-y-4">
  <div class="bg-primary-500 text-white p-4 rounded">Primário</div>
  <div class="bg-secondary-500 text-white p-4 rounded">Secundário</div>
  <div class="bg-success-500 text-white p-4 rounded">Sucesso</div>
  <div class="bg-attention-500 text-white p-4 rounded">Atenção</div>
  <div class="bg-danger-500 text-white p-4 rounded">Perigo</div>
</div>
```

#### **Teste 2: Tipografia**
```html
<div class="p-8 space-y-4">
  <h1>Título H1 - 36px</h1>
  <h2>Título H2 - 30px</h2>
  <h3>Título H3 - 24px</h3>
  <h4>Título H4 - 20px</h4>
  <p class="text-base">Texto base - 16px</p>
  <p class="text-sm">Texto pequeno - 14px</p>
  <p class="text-xs">Texto tiny - 12px</p>
</div>
```

#### **Teste 3: Cards**
```html
<div class="p-8 grid grid-cols-1 md:grid-cols-3 gap-6">
  <div class="card-ativo animate-scale-in">
    <div class="header">
      <span class="ticker">PETR4</span>
      <span class="categoria">Ação</span>
    </div>
    <div class="preco">R$ 45,67</div>
    <div class="variacao positiva">+2.3%</div>
  </div>
  
  <div class="card-ativo animate-scale-in animate-delay-100">
    <div class="header">
      <span class="ticker">VALE3</span>
      <span class="categoria">Ação</span>
    </div>
    <div class="preco">R$ 78,90</div>
    <div class="variacao negativa">-0.8%</div>
  </div>
  
  <div class="card-ativo animate-scale-in animate-delay-200">
    <div class="header">
      <span class="ticker">TRXF11</span>
      <span class="categoria">FII</span>
    </div>
    <div class="preco">R$ 120,00</div>
    <div class="variacao positiva">+1.2%</div>
  </div>
</div>
```

---

## 📋 **CHECKLIST SEMANA 1**

### **✅ Dia 1-2: Fundação Visual**
- [ ] Implementar cores emocionais no CSS
- [ ] Adicionar gradientes modernos
- [ ] Aumentar tipografia (títulos 24px→36px)
- [ ] Garantir contraste 4.5:1

### **✅ Dia 3-4: Componentes Base**
- [ ] Criar classes de card modernas
- [ ] Implementar botões com hover states
- [ ] Adicionar ícones de 24px mínimos
- [ ] Testar responsividade

### **✅ Dia 5: Animações**
- [ ] Implementar fade-in, slide-up, scale-in
- [ ] Adicionar hover states suaves
- [ ] Criar loading skeletons
- [ ] Testar performance

### **📊 Métricas de Sucesso Week 1:**
- **Cores implementadas:** 5 paletas + gradientes
- **Tipografia atualizada:** Títulos +40% tamanho
- **Componentes criados:** Cards, botões, ícones
- **Animações funcionando:** 4 tipos + delays
- **Performance:** < 2s carregamento

---

## 🚀 **PREPARANDO WEEK 2**

### **📋 Entregas Week 1:**
1. **CSS atualizado** com design system moderno
2. **Componentes base** funcionais
3. **Animações suaves** implementadas
4. **Testes visuais** validados

### **🎯 Foco Week 2:**
- **Navegação simplificada** (22→8 itens)
- **Menu por contexto** (abas + sub-menu)
- **Busca inteligente**
- **Mobile-first**

---

**Status Week 1:** 📋 **Planejamento Completo**  
**Próximo:** 🎨 **Implementação CSS**  
**Timeline:** 5 dias | **Entrega:** Design System Moderno
