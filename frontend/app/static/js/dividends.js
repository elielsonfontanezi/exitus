/**
 * Dividends Page JavaScript - Alpine.js Data Functions
 * Sistema de gerenciamento de proventos e dividendos
 */

// Função Alpine.js para gerenciar dados de proventos
function dividendsData() {
    return {
        currency: localStorage.getItem('preferredCurrency') || 'BRL',
        exchangeRate: 5.00,
        loading: false,
        
        // Dados dos proventos
        dividends: [],
        
        // Filtros
        filters: {
            ativo: 'Todos',
            tipo: 'Todos',
            status: 'Todos',
            dataInicio: ''
        },
        
        // Estatísticas
        stats: {
            total: 0,
            recebido: 0.00,
            receber: 0.00,
            geral: 0.00
        },
        
        // Inicialização
        init() {
            this.loadDividends();
        },
        
        // Carregar proventos
        async loadDividends() {
            this.loading = true;
            
            try {
                // Mock data - em produção viria da API
                this.dividends = [];
                
                this.updateStats();
            } catch (error) {
                console.error('Erro ao carregar proventos:', error);
            } finally {
                this.loading = false;
            }
        },
        
        // Atualizar estatísticas
        updateStats() {
            this.stats.total = this.dividends.length;
            this.stats.recebido = this.dividends
                .filter(d => d.status === 'Pago')
                .reduce((total, d) => total + d.total, 0);
            this.stats.receber = this.dividends
                .filter(d => d.status === 'Previsto')
                .reduce((total, d) => total + d.total, 0);
            this.stats.geral = this.stats.recebido + this.stats.receber;
        },
        
        // Aplicar filtros
        aplicarFiltros() {
            // Implementação de filtros
            console.log('Filtros aplicados:', this.filters);
        },
        
        // Limpar filtros
        limparFiltros() {
            this.filters = {
                ativo: 'Todos',
                tipo: 'Todos',
                status: 'Todos',
                dataInicio: ''
            };
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
