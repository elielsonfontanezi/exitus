/**
 * Assets Page JavaScript - Alpine.js Data Functions
 * Sistema de gerenciamento de ativos com filtros e exportação
 */

// Função Alpine.js para gerenciar dados de ativos
function assetsData() {
    return {
        currency: localStorage.getItem('preferredCurrency') || 'BRL',
        exchangeRate: 5.00,
        loading: false,
        
        // Dados dos ativos
        assets: [],
        filteredAssets: [],
        
        // Filtros
        filters: {
            tipo: 'Todos os Tipos',
            busca: '',
            ordenar: 'ticker'
        },
        
        // Estatísticas
        stats: {
            total: 0,
            acoes: 0,
            fiis: 0,
            etfs: 0,
            bdrs: 0
        },
        
        // Inicialização
        init() {
            this.loadAssets();
            this.updateStats();
        },
        
        // Carregar ativos
        async loadAssets() {
            this.loading = true;
            
            try {
                // Mock data - em produção viria da API
                this.assets = [
                    { ticker: 'AAPL', nome: 'Apple Inc.', tipo: 'stock', setor: 'Technology', cotacao: 0.00 },
                    { ticker: 'ABEV3', nome: 'Ambev ON', tipo: 'acao', setor: 'Consumo', cotacao: 0.00 },
                    { ticker: 'TRXF11', nome: 'TRX Real Estate FII', tipo: 'fii', setor: 'FIIs', cotacao: 0.00 },
                    // ... mais ativos
                ];
                
                this.filteredAssets = [...this.assets];
                this.updateStats();
            } catch (error) {
                console.error('Erro ao carregar ativos:', error);
            } finally {
                this.loading = false;
            }
        },
        
        // Atualizar estatísticas
        updateStats() {
            this.stats.total = this.assets.length;
            this.stats.acoes = this.assets.filter(a => a.tipo === 'acao').length;
            this.stats.fiis = this.assets.filter(a => a.tipo === 'fii').length;
            this.stats.etfs = this.assets.filter(a => a.tipo === 'etf').length;
            this.stats.bdrs = this.assets.filter(a => a.tipo === 'bdr').length;
        },
        
        // Aplicar filtros
        aplicarFiltros() {
            let filtered = [...this.assets];
            
            // Filtro por tipo
            if (this.filters.tipo !== 'Todos os Tipos') {
                filtered = filtered.filter(asset => 
                    asset.tipo === this.filters.tipo.toLowerCase()
                );
            }
            
            // Filtro por busca
            if (this.filters.busca) {
                const busca = this.filters.busca.toLowerCase();
                filtered = filtered.filter(asset => 
                    asset.ticker.toLowerCase().includes(busca) ||
                    asset.nome.toLowerCase().includes(busca)
                );
            }
            
            // Ordenação
            filtered.sort((a, b) => {
                switch (this.filters.ordenar) {
                    case 'ticker':
                        return a.ticker.localeCompare(b.ticker);
                    case 'nome':
                        return a.nome.localeCompare(b.nome);
                    case 'tipo':
                        return a.tipo.localeCompare(b.tipo);
                    default:
                        return 0;
                }
            });
            
            this.filteredAssets = filtered;
        },
        
        // Limpar filtros
        limparFiltros() {
            this.filters = {
                tipo: 'Todos os Tipos',
                busca: '',
                ordenar: 'ticker'
            };
            this.aplicarFiltros();
        },
        
        // Exportar CSV
        exportarCSV() {
            const headers = ['Ticker', 'Nome', 'Tipo', 'Setor', 'Cotação (R$)'];
            const rows = this.filteredAssets.map(asset => [
                asset.ticker,
                asset.nome,
                asset.tipo,
                asset.setor || 'N/A',
                asset.cotacao.toFixed(2)
            ]);
            
            const csv = [headers, ...rows]
                .map(row => row.join(','))
                .join('\n');
            
            this.downloadFile(csv, 'ativos.csv', 'text/csv');
        },
        
        // Exportar Excel
        exportarExcel() {
            // Implementação simplificada - em produção usaría biblioteca como xlsx
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
