/**
 * Dashboard Multi-Mercado - JavaScript
 * Sistema de conversão dinâmica de moedas e gerenciamento de dados
 */

// Função Alpine.js para gerenciar dados do dashboard
function dashboardData() {
    return {
        currency: localStorage.getItem('preferredCurrency') || 'BRL',
        exchangeRate: 5.00,
        
        handleCurrencyChange(detail) {
            this.currency = detail.currency;
            this.exchangeRate = detail.rate;
            console.log('Moeda alterada para:', this.currency, 'Taxa:', this.exchangeRate);
        },
        
        formatValue(value, fromCurrency = 'BRL') {
            if (!value) return '0,00';
            
            let convertedValue = value;
            
            // Converter se necessário
            if (this.currency === 'USD' && fromCurrency === 'BRL') {
                convertedValue = value / this.exchangeRate;
            } else if (this.currency === 'BRL' && fromCurrency === 'USD') {
                convertedValue = value * this.exchangeRate;
            }
            
            // Formatar
            const symbol = this.currency === 'BRL' ? 'R$' : '$';
            const formatted = convertedValue.toLocaleString('pt-BR', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
            
            return `${symbol} ${formatted}`;
        },
        
        getCurrencySymbol() {
            return this.currency === 'BRL' ? 'R$' : '$';
        }
    }
}

// Utilitário para formatar valores monetários
function formatCurrency(value, currency = 'BRL', exchangeRate = 5.00) {
    if (!value) return '0,00';
    
    const symbol = currency === 'BRL' ? 'R$' : '$';
    const formatted = value.toLocaleString('pt-BR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
    
    return `${symbol} ${formatted}`;
}

// Utilitário para converter valores
function convertCurrency(value, fromCurrency, toCurrency, exchangeRate) {
    if (fromCurrency === toCurrency) return value;
    
    if (toCurrency === 'USD' && fromCurrency === 'BRL') {
        return value / exchangeRate;
    } else if (toCurrency === 'BRL' && fromCurrency === 'USD') {
        return value * exchangeRate;
    }
    
    return value;
}
