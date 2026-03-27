/**
 * Analytics Page JavaScript - Alpine.js Data Functions
 * Sistema de análise avançada de portfólio
 */

// Função Alpine.js para gerenciar dados de analytics
function analyticsData() {
    return {
        currency: localStorage.getItem('preferredCurrency') || 'BRL',
        exchangeRate: 5.00,
        loading: false,
        
        // Dados de analytics
        analytics: {
            sharpe: 0.00,
            volatilidade: 0.00,
            correlacao: [],
            projecoes: []
        },
        
        // Inicialização
        init() {
            this.loadAnalytics();
        },
        
        // Carregar analytics
        async loadAnalytics() {
            this.loading = true;
            
            try {
                // Mock data - em produção viria da API
                this.analytics = {
                    sharpe: 1.45,
                    volatilidade: 18.5,
                    correlacao: [],
                    projecoes: []
                };
            } catch (error) {
                console.error('Erro ao carregar analytics:', error);
            } finally {
                this.loading = false;
            }
        },
        
        // Handle mudança de moeda
        handleCurrencyChange(detail) {
            this.currency = detail.currency;
            this.exchangeRate = detail.rate;
            localStorage.setItem('preferredCurrency', this.currency);
        },
        
        // Formatar moeda
        formatCurrency(value, currency = null, showSymbol = true) {
            if (!value) return '0,00';
            
            const targetCurrency = currency || this.currency;
            const rate = targetCurrency === 'USD' ? 1 / this.exchangeRate : 1;
            const convertedValue = value * rate;
            
            const formatted = convertedValue.toFixed(2).replace('.', ',');
            return showSymbol ? (targetCurrency === 'USD' ? '$ ' : 'R$ ') + formatted : formatted;
        }
    };
}
