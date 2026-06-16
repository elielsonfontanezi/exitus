/**
 * Movimentações Page JavaScript - Alpine.js Data Functions
 * Sistema de controle de movimentações de caixa
 */

// Função Alpine.js para gerenciar dados de movimentações
function movimentacoesData() {
    return {
        currency: localStorage.getItem('preferredCurrency') || 'BRL',
        exchangeRate: 5.00,
        loading: false,
        
        // Dados das movimentações
        movimentacoes: [],
        
        // Estatísticas
        stats: {
            total: 0,
            saldo: 0.00
        },
        
        // Inicialização
        init() {
            this.loadMovimentacoes();
        },
        
        // Carregar movimentações
        async loadMovimentacoes() {
            this.loading = true;
            
            try {
                // Mock data - em produção viria da API
                this.movimentacoes = [
                    {
                        data: '2026-01-05',
                        tipo: 'deposito',
                        valor: 5000.00,
                        corretora: 'XP',
                        descricao: '-'
                    }
                ];
                
                this.updateStats();
            } catch (error) {
                console.error('Erro ao carregar movimentações:', error);
            } finally {
                this.loading = false;
            }
        },
        
        // Atualizar estatísticas
        updateStats() {
            this.stats.total = this.movimentacoes.length;
            this.stats.saldo = this.movimentacoes.reduce((total, mov) => {
                return mov.tipo === 'deposito' ? total + mov.valor : total - mov.valor;
            }, 0);
        },
        
        // Exportar CSV
        exportarCSV() {
            const headers = ['Data', 'Tipo', 'Valor', 'Corretora', 'Descrição'];
            const rows = this.movimentacoes.map(mov => [
                mov.data,
                mov.tipo,
                `R$ ${mov.valor.toFixed(2)}`,
                mov.corretora,
                mov.descricao
            ]);
            
            const csv = [headers, ...rows]
                .map(row => row.join(','))
                .join('\n');
            
            this.downloadFile(csv, 'movimentacoes.csv', 'text/csv');
        },
        
        // Exportar Excel
        exportarExcel() {
            this.exportarCSV(); // Por enquanto exporta como CSV
        },
        
        // Download de arquivo
        downloadFile(content, filename, type) {
            const blob = new Blob([content], { type });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            a.click();
            window.URL.revokeObjectURL(url);
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
