/**
 * Buy Signals - JavaScript (Redesign)
 * Sistema de sinais de compra com IA e análise multi-fator
 */

// Função Alpine.js para gerenciar Buy Signals
function buySignalsData() {
    return {
        currency: localStorage.getItem('preferredCurrency') || 'BRL',
        exchangeRate: 5.00,
        loading: true,
        searching: false,
        searchTicker: '',
        filtroSinal: 'todos',
        
        // Dados
        selectedAsset: null,
        sinais: [],
        radarChart: null,
        
        // Inicialização
        init() {
            this.carregarSinais();
        },
        
        // Carregar sinais do mercado
        async carregarSinais() {
            this.loading = true;
            
            try {
                const response = await fetch('/api/buy-signals');
                if (response.ok) {
                    const data = await response.json();
                    this.sinais = data.data || [];
                }
            } catch (error) {
                console.error('Erro ao carregar sinais:', error);
                this.loadMockData();
            } finally {
                this.loading = false;
            }
        },
        
        // Carregar dados mock
        loadMockData() {
            this.sinais = [
                {
                    ticker: 'PETR4',
                    nome: 'Petrobras PN',
                    signal: 'COMPRA',
                    score: 85,
                    preco_atual: 27.80,
                    variacao: 2.35,
                    pl: 4.2,
                    pvp: 1.1,
                    dy: 12.5,
                    roe: 18.5
                },
                {
                    ticker: 'VALE3',
                    nome: 'Vale ON',
                    signal: 'COMPRA',
                    score: 78,
                    preco_atual: 72.40,
                    variacao: -1.2,
                    pl: 5.8,
                    pvp: 1.3,
                    dy: 8.9,
                    roe: 22.1
                },
                {
                    ticker: 'ITUB4',
                    nome: 'Itaú Unibanco PN',
                    signal: 'AGUARDAR',
                    score: 65,
                    preco_atual: 22.10,
                    variacao: 0.8,
                    pl: 10.2,
                    pvp: 1.5,
                    dy: 6.5,
                    roe: 15.8
                },
                {
                    ticker: 'BBDC4',
                    nome: 'Bradesco PN',
                    signal: 'AGUARDAR',
                    score: 62,
                    preco_atual: 19.20,
                    variacao: 1.5,
                    pl: 11.5,
                    pvp: 1.6,
                    dy: 7.2,
                    roe: 14.2
                },
                {
                    ticker: 'WEGE3',
                    nome: 'WEG ON',
                    signal: 'VENDA',
                    score: 35,
                    preco_atual: 35.60,
                    variacao: -3.2,
                    pl: 28.5,
                    pvp: 4.2,
                    dy: 2.1,
                    roe: 18.9
                },
                {
                    ticker: 'B3SA3',
                    nome: 'B3 ON',
                    signal: 'COMPRA',
                    score: 82,
                    preco_atual: 12.80,
                    variacao: 3.5,
                    pl: 15.2,
                    pvp: 2.8,
                    dy: 4.5,
                    roe: 25.3
                }
            ];
        },
        
        // Buscar ativo específico
        async searchAsset() {
            if (!this.searchTicker) return;
            
            this.searching = true;
            
            try {
                const response = await fetch(`/api/buy-signals/${this.searchTicker.toUpperCase()}`);
                if (response.ok) {
                    const data = await response.json();
                    this.selectedAsset = data.data;
                    this.$nextTick(() => {
                        this.initRadarChart();
                    });
                } else {
                    // Mock: criar análise simulada
                    this.selectedAsset = this.createMockAnalysis(this.searchTicker.toUpperCase());
                    this.$nextTick(() => {
                        this.initRadarChart();
                    });
                }
            } catch (error) {
                console.error('Erro ao buscar ativo:', error);
                // Mock: criar análise simulada
                this.selectedAsset = this.createMockAnalysis(this.searchTicker.toUpperCase());
                this.$nextTick(() => {
                    this.initRadarChart();
                });
            } finally {
                this.searching = false;
            }
        },
        
        // Criar análise mock
        createMockAnalysis(ticker) {
            const mockAssets = {
                'PETR4': {
                    nome: 'Petrobras PN',
                    signal: 'COMPRA',
                    score: 85,
                    preco_atual: 27.80,
                    variacao: 2.35,
                    pl: 4.2,
                    pvp: 1.1,
                    dy: 12.5,
                    roe: 18.5,
                    insights: {
                        forte: 'Excelente relação P/L e forte geração de caixa',
                        atencao: 'Dependência de preços do petróleo',
                        oportunidade: 'Potencial de dividendos acima da média'
                    }
                },
                'VALE3': {
                    nome: 'Vale ON',
                    signal: 'COMPRA',
                    score: 78,
                    preco_atual: 72.40,
                    variacao: -1.2,
                    pl: 5.8,
                    pvp: 1.3,
                    dy: 8.9,
                    roe: 22.1,
                    insights: {
                        forte: 'Baixo custo de produção e forte demanda',
                        atencao: 'Volatilidade com preços commodities',
                        oportunidade: 'Expansão da produção nos próximos anos'
                    }
                }
            };
            
            const asset = mockAssets[ticker] || {
                nome: `${ticker} - Empresa Anônima`,
                signal: 'AGUARDAR',
                score: 60,
                preco_atual: Math.random() * 100 + 10,
                variacao: (Math.random() - 0.5) * 10,
                pl: Math.random() * 20 + 5,
                pvp: Math.random() * 3 + 0.5,
                dy: Math.random() * 15,
                roe: Math.random() * 25 + 5,
                insights: {
                    forte: 'Empresa sólida no setor',
                    atencao: 'Analisar fundamentos mais detalhadamente',
                    oportunidade: 'Potencial de crescimento no longo prazo'
                }
            };
            
            return {
                ...asset,
                ticker,
                preco_alvo: {
                    conservador: asset.preco_atual * 1.1,
                    moderado: asset.preco_atual * 1.25,
                    otimista: asset.preco_atual * 1.4
                }
            };
        },
        
        // Selecionar sinal do grid
        selectSignal(signal) {
            this.selectedAsset = this.createMockAnalysis(signal.ticker);
            this.$nextTick(() => {
                this.initRadarChart();
            });
        },
        
        // Inicializar gráfico radar
        initRadarChart() {
            if (!this.selectedAsset) return;
            
            const ctx = document.getElementById('radar-chart');
            if (!ctx) return;
            
            // Destruir gráfico anterior se existir
            if (this.radarChart) {
                this.radarChart.destroy();
            }
            
            // Dados para o radar
            const radarData = {
                labels: [
                    'Valuation (P/L)',
                    'Valuation (P/VP)',
                    'Rentabilidade (ROE)',
                    'Dividendos (DY)',
                    'Liquidez',
                    'Volatilidade',
                    'Tendência',
                    'Volume'
                ],
                datasets: [{
                    label: this.selectedAsset.ticker,
                    data: [
                        Math.max(0, 100 - (this.selectedAsset.pl || 10) * 5),
                        Math.max(0, 100 - (this.selectedAsset.pvp || 1.5) * 30),
                        (this.selectedAsset.roe || 10) * 3,
                        (this.selectedAsset.dy || 5) * 5,
                        75, // Mock
                        Math.max(0, 100 - Math.abs(this.selectedAsset.variacao || 0) * 5),
                        this.selectedAsset.variacao > 0 ? 80 : 40,
                        70 // Mock
                    ],
                    backgroundColor: 'rgba(59, 130, 246, 0.2)',
                    borderColor: 'rgba(59, 130, 246, 1)',
                    borderWidth: 2,
                    pointBackgroundColor: 'rgba(59, 130, 246, 1)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgba(59, 130, 246, 1)'
                }, {
                    label: 'Ideal',
                    data: [85, 85, 75, 70, 80, 70, 85, 75],
                    backgroundColor: 'rgba(34, 197, 94, 0.1)',
                    borderColor: 'rgba(34, 197, 94, 1)',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    pointBackgroundColor: 'rgba(34, 197, 94, 1)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgba(34, 197, 94, 1)'
                }]
            };
            
            this.radarChart = new Chart(ctx, {
                type: 'radar',
                data: radarData,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        r: {
                            beginAtZero: true,
                            max: 100,
                            ticks: {
                                stepSize: 20
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 20,
                                font: { size: 12 }
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: (context) => {
                                    return `${context.dataset.label}: ${context.raw}/100`;
                                }
                            }
                        }
                    }
                }
            });
        },
        
        // Computed: sinais filtrados
        get sinaisFiltrados() {
            if (this.filtroSinal === 'todos') {
                return this.sinais;
            }
            
            const signalMap = {
                'compra': 'COMPRA',
                'aguardar': 'AGUARDAR',
                'venda': 'VENDA'
            };
            
            return this.sinais.filter(s => s.signal === signalMap[this.filtroSinal]);
        },
        
        // Obter classe CSS do sinal
        getSignalClass(signal) {
            const classMap = {
                'COMPRA': 'badge-success',
                'AGUARDAR': 'badge-warning',
                'VENDA': 'badge-danger'
            };
            return classMap[signal] || 'badge-gray';
        },
        
        // Obter cor do sinal
        getSignalColor(signal) {
            const colorMap = {
                'COMPRA': 'bg-success-500',
                'AGUARDAR': 'bg-warning-500',
                'VENDA': 'bg-danger-500'
            };
            return colorMap[signal] || 'bg-gray-500';
        },
        
        // Handle mudança de moeda
        handleCurrencyChange(detail) {
            this.currency = detail.currency;
            this.exchangeRate = detail.rate;
            localStorage.setItem('preferredCurrency', this.currency);
        },
        
        // Utilitários
        formatCurrency(value, currency = null, showSymbol = true) {
            if (!value) return '0,00';
            
            const targetCurrency = currency || this.currency;
            let convertedValue = value;
            
            // Converter se necessário
            if (targetCurrency === 'USD' && this.currency === 'BRL') {
                convertedValue = value / this.exchangeRate;
            } else if (targetCurrency === 'BRL' && this.currency === 'USD') {
                convertedValue = value * this.exchangeRate;
            }
            
            // Formatar
            const symbol = showSymbol ? (targetCurrency === 'BRL' ? 'R$ ' : '$ ') : '';
            const formatted = convertedValue.toLocaleString('pt-BR', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
            
            return symbol + formatted;
        }
    }
}
