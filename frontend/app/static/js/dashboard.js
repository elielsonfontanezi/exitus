/**
 * Dashboard Multi-Mercado V2.0 - JavaScript
 * Sistema de dados modernos com APIs reais e gráficos Chart.js
 */

// Função Alpine.js para gerenciar dados do dashboard
function dashboardData() {
    return {
        currency: localStorage.getItem('preferredCurrency') || 'BRL',
        exchangeRate: 5.00,
        period: '1A',
        loading: true,
        
        // Dados dos mercados
        marketData: {
            br: { total: 0, change: 0, changePercent: 0 },
            us: { total: 0, change: 0, changePercent: 0 },
            intl: { total: 0, change: 0, changePercent: 0 },
            total: 0
        },
        
        // Top 5 ativos
        topAssets: [],
        
        // Alertas recentes
        recentAlerts: [],
        
        // Transações recentes
        recentTransactions: [],
        
        // Inicialização
        init() {
            this.loadDashboardData();
            this.initCharts();
        },
        
        // Carregar dados do dashboard
        async loadDashboardData() {
            this.loading = true;
            
            try {
                // Carregar dados do portfolio
                const response = await window.auth.fetch('/api/portfolios/dashboard');
                if (response && response.ok) {
                    const data = await response.json();
                    this.updateMarketData(data.data);
                }
                
                // Carregar taxa de câmbio
                const cambioResponse = await window.auth.fetch('/api/cambio/taxa-atual?de=USD&para=BRL');
                if (cambioResponse && cambioResponse.ok) {
                    const cambioData = await cambioResponse.json();
                    this.exchangeRate = cambioData.data.taxa || 5.00;
                }
                
                // Carregar posições
                const positionsResponse = await window.auth.fetch('/api/posicoes');
                if (positionsResponse && positionsResponse.ok) {
                    const positionsData = await positionsResponse.json();
                    this.updateTopAssets(positionsData.data);
                }
                
                // Carregar alertas (endpoint pode não existir)
                try {
                    const alertsResponse = await window.auth.fetch('/api/alerts?limit=5');
                    if (alertsResponse && alertsResponse.ok) {
                        const alertsData = await alertsResponse.json();
                        this.recentAlerts = alertsData.data || [];
                    }
                } catch (alertError) {
                    console.log('Endpoint de alertas não disponível (OK)');
                    this.recentAlerts = [];
                }
                
                // Carregar transações
                const transactionsResponse = await window.auth.fetch('/api/transacoes?limit=5');
                if (transactionsResponse && transactionsResponse.ok) {
                    const transactionsData = await transactionsResponse.json();
                    this.recentTransactions = transactionsData.data || [];
                }
                
            } catch (error) {
                console.error('Erro ao carregar dados do dashboard:', error);
            } finally {
                this.loading = false;
            }
        },
        
        // Atualizar dados dos mercados
        updateMarketData(data) {
            // Mock: dividir por mercado (em produção, virá da API)
            const total = data.valor_total_patrimonio || 0;
            
            this.marketData = {
                br: { 
                    total: total * 0.6, 
                    change: 12450, 
                    changePercent: 2.4 
                },
                us: { 
                    total: total * 0.25, 
                    change: 2340, 
                    changePercent: 1.8 
                },
                intl: { 
                    total: total * 0.15, 
                    change: 890, 
                    changePercent: 0.9 
                },
                total: total
            };
        },
        
        // Atualizar top ativos
        updateTopAssets(positions) {
            this.topAssets = positions.slice(0, 5).map(pos => ({
                ticker: pos.ativo.ticker,
                name: pos.ativo.nome,
                value: pos.quantidade * pos.preco_medio,
                change: Math.random() * 10 - 5 // Mock: -5% a +5%
            }));
        },
        
        // Inicializar gráficos
        initCharts() {
            this.initAllocationChart();
            this.initEvolutionChart();
        },
        
        // Gráfico de Alocação
        initAllocationChart() {
            const ctx = document.getElementById('allocation-chart');
            if (!ctx) return;
            
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Brasil', 'Estados Unidos', 'Internacional'],
                    datasets: [{
                        data: [
                            this.marketData.br.total,
                            this.marketData.us.total,
                            this.marketData.intl.total
                        ],
                        backgroundColor: [
                            'rgba(59, 130, 246, 0.8)',
                            'rgba(99, 102, 241, 0.8)',
                            'rgba(245, 158, 11, 0.8)'
                        ],
                        borderColor: [
                            'rgba(59, 130, 246, 1)',
                            'rgba(99, 102, 241, 1)',
                            'rgba(245, 158, 11, 1)'
                        ],
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
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
                                    const value = this.formatCurrency(context.raw, this.currency);
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percent = ((context.raw / total) * 100).toFixed(1);
                                    return `${context.label}: ${value} (${percent}%)`;
                                }
                            }
                        }
                    }
                }
            });
        },
        
        // Gráfico de Evolução
        initEvolutionChart() {
            const ctx = document.getElementById('evolution-chart');
            if (!ctx) return;
            
            // Gerar dados mock para evolução
            const months = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
            const data = months.map(() => this.marketData.total * (0.8 + Math.random() * 0.4));
            
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: months,
                    datasets: [{
                        label: 'Patrimônio',
                        data: data,
                        borderColor: 'rgba(59, 130, 246, 1)',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 4,
                        pointHoverRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            callbacks: {
                                label: (context) => `Patrimônio: ${this.formatCurrency(context.raw, this.currency)}`
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: false,
                            ticks: {
                                callback: (value) => this.formatCurrency(value, this.currency, false)
                            }
                        }
                    }
                }
            });
        },
        
        // Mudar período do gráfico
        changePeriod(newPeriod) {
            this.period = newPeriod;
            // Recarregar gráfico com novo período
            this.initEvolutionChart();
        },
        
        // Handle mudança de moeda
        handleCurrencyChange(detail) {
            this.currency = detail.currency;
            this.exchangeRate = detail.rate;
            localStorage.setItem('preferredCurrency', this.currency);
            
            // Atualizar gráficos
            this.initCharts();
        },
        
        // Formatar moeda
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
        },
        
        // Cor para alertas
        getAlertColorClass(type) {
            const colors = {
                'OPORTUNIDADE': 'bg-success-500',
                'PRECO': 'bg-primary-500',
                'DIVIDENDO': 'bg-warning-500',
                'IR': 'bg-danger-500'
            };
            return colors[type] || 'bg-gray-500';
        },
        
        // Cor para transações
        getTransactionColorClass(type) {
            return type === 'COMPRA' ? 'bg-danger-500' : 'bg-success-500';
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
