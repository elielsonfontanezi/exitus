/**
 * Performance e Rentabilidade - JavaScript
 * Sistema de métricas e gráficos de performance
 */

// Função Alpine.js para gerenciar dados de performance
function performanceData() {
    return {
        currency: localStorage.getItem('preferredCurrency') || 'BRL',
        exchangeRate: 5.00,
        period: '1A',
        loading: true,
        searchAtivo: '',
        sortBy: 'valor',
        heatmapYear: '2024',
        showCDI: true,
        showIBOV: true,
        showIFIX: false,
        
        // Dados de performance
        performance: {
            rentabilidade_total: { valor: 0, percentual: 0 },
            mes_atual: { valor: 0, percentual: 0 },
            maior_ganhador: { ticker: '', valor: 0, percentual: 0, quantidade: 0 },
            maior_perdedor: { ticker: '', valor: 0, percentual: 0, quantidade: 0 }
        },
        
        // Lista de ativos
        ativos: [],
        
        // Inicialização
        init() {
            this.loadPerformanceData();
            this.initCharts();
        },
        
        // Carregar dados de performance
        async loadPerformanceData() {
            this.loading = true;
            
            try {
                // Carregar performance do portfolio
                const performanceResponse = await fetch('/api/portfolios/performance');
                if (performanceResponse.ok) {
                    const performanceData = await performanceResponse.json();
                    this.updatePerformanceData(performanceData.data);
                }
                
                // Carregar posições para performance por ativo
                const positionsResponse = await fetch('/api/posicoes');
                if (positionsResponse.ok) {
                    const positionsData = await positionsResponse.json();
                    this.updateAtivosPerformance(positionsData.data);
                }
                
                // Inicializar gráficos após carregar dados
                this.$nextTick(() => {
                    this.initCharts();
                    this.initSparklines();
                });
                
            } catch (error) {
                console.error('Erro ao carregar dados de performance:', error);
                // Carregar dados mock em caso de erro
                this.loadMockData();
            } finally {
                this.loading = false;
            }
        },
        
        // Atualizar dados de performance
        updatePerformanceData(data) {
            // Mock: em produção virá da API
            this.performance = {
                rentabilidade_total: { 
                    valor: 45000, 
                    percentual: 18.5 
                },
                mes_atual: { 
                    valor: 8500, 
                    percentual: 2.8 
                },
                maior_ganhador: { 
                    ticker: 'PETR4', 
                    valor: 12500, 
                    percentual: 28.5, 
                    quantidade: 300 
                },
                maior_perdedor: { 
                    ticker: 'MGLU3', 
                    valor: -3200, 
                    percentual: -15.2, 
                    quantidade: 500 
                }
            };
        },
        
        // Atualizar performance por ativo
        updateAtivosPerformance(positions) {
            this.ativos = positions.map(pos => {
                const valorAtual = pos.quantidade * (pos.preco_medio * (1 + (Math.random() * 0.4 - 0.2)));
                const resultado = valorAtual - (pos.quantidade * pos.preco_medio);
                const percentual = (resultado / (pos.quantidade * pos.preco_medio)) * 100;
                
                return {
                    ticker: pos.ativo.ticker,
                    nome: pos.ativo.nome,
                    quantidade: pos.quantidade,
                    custo_medio: pos.preco_medio,
                    valor_atual: valorAtual / pos.quantidade,
                    resultado: resultado,
                    percentual: percentual,
                    sparkline: this.generateSparklineData()
                };
            });
        },
        
        // Carregar dados mock
        loadMockData() {
            this.updatePerformanceData({});
            
            this.ativos = [
                {
                    ticker: 'PETR4',
                    nome: 'Petrobras PN',
                    quantidade: 300,
                    custo_medio: 28.50,
                    valor_atual: 36.80,
                    resultado: 12500,
                    percentual: 28.5,
                    sparkline: this.generateSparklineData()
                },
                {
                    ticker: 'VALE3',
                    nome: 'Vale ON',
                    quantidade: 200,
                    custo_medio: 65.20,
                    valor_atual: 72.40,
                    resultado: 1440,
                    percentual: 11.0,
                    sparkline: this.generateSparklineData()
                },
                {
                    ticker: 'ITUB4',
                    nome: 'Itaú Unibanco PN',
                    quantidade: 400,
                    custo_medio: 22.80,
                    valor_atual: 25.60,
                    resultado: 1120,
                    percentual: 12.3,
                    sparkline: this.generateSparklineData()
                },
                {
                    ticker: 'MGLU3',
                    nome: 'Magazine Luiza ON',
                    quantidade: 500,
                    custo_medio: 3.80,
                    valor_atual: 3.22,
                    resultado: -3200,
                    percentual: -15.2,
                    sparkline: this.generateSparklineData()
                },
                {
                    ticker: 'WEGE3',
                    nome: 'WEG ON',
                    quantidade: 100,
                    custo_medio: 32.50,
                    valor_atual: 38.90,
                    resultado: 640,
                    percentual: 19.7,
                    sparkline: this.generateSparklineData()
                }
            ];
        },
        
        // Gerar dados para sparkline
        generateSparklineData() {
            const points = 20;
            const data = [];
            let value = 100;
            
            for (let i = 0; i < points; i++) {
                value += (Math.random() - 0.5) * 10;
                data.push(Math.max(80, Math.min(120, value)));
            }
            
            return data;
        },
        
        // Inicializar gráficos
        initCharts() {
            this.initPerformanceChart();
            this.initBenchmarkChart();
            this.updateHeatmap();
        },
        
        // Gráfico de Performance Acumulada
        initPerformanceChart() {
            const ctx = document.getElementById('performance-chart');
            if (!ctx) return;
            
            const labels = this.generateDateLabels(this.period);
            const portfolioData = labels.map(() => 100000 * (1 + Math.random() * 0.3));
            
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Portfolio',
                        data: portfolioData,
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
                                label: (context) => `Portfolio: ${this.formatCurrency(context.raw, this.currency)}`
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
        
        // Gráfico de Benchmarks
        initBenchmarkChart() {
            const ctx = document.getElementById('benchmark-chart');
            if (!ctx) return;
            
            const labels = this.generateDateLabels(this.period);
            const datasets = [
                {
                    label: 'Portfolio',
                    data: labels.map(() => 100000 * (1 + Math.random() * 0.3)),
                    borderColor: 'rgba(59, 130, 246, 1)',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 3,
                    fill: false,
                    tension: 0.4
                }
            ];
            
            if (this.showCDI) {
                datasets.push({
                    label: 'CDI',
                    data: labels.map(() => 100000 * (1 + Math.random() * 0.2)),
                    borderColor: 'rgba(16, 185, 129, 1)',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.4
                });
            }
            
            if (this.showIBOV) {
                datasets.push({
                    label: 'IBOV',
                    data: labels.map(() => 100000 * (1 + Math.random() * 0.25)),
                    borderColor: 'rgba(245, 158, 11, 1)',
                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.4
                });
            }
            
            if (this.showIFIX) {
                datasets.push({
                    label: 'IFIX',
                    data: labels.map(() => 100000 * (1 + Math.random() * 0.15)),
                    borderColor: 'rgba(239, 68, 68, 1)',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.4
                });
            }
            
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: datasets
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
                                label: (context) => `${context.dataset.label}: ${this.formatCurrency(context.raw, this.currency)}`
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
        
        // Atualizar gráfico de benchmarks
        updateBenchmarkChart() {
            // Destruir gráfico existente e recriar
            const ctx = document.getElementById('benchmark-chart');
            if (ctx) {
                const chart = Chart.getChart(ctx);
                if (chart) {
                    chart.destroy();
                }
                this.initBenchmarkChart();
            }
        },
        
        // Atualizar heatmap
        updateHeatmap() {
            const container = document.getElementById('heatmap-container');
            if (!container) return;
            
            const months = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
            let html = '<div class="grid grid-cols-13 gap-1">';
            
            // Header
            html += '<div></div>';
            for (const month of months) {
                html += `<div class="text-xs text-center text-gray-600 font-medium">${month}</div>`;
            }
            
            // Dados (mock)
            for (let week = 0; week < 5; week++) {
                html += `<div class="text-xs text-center text-gray-600 font-medium pr-2">S${week + 1}</div>`;
                for (let month = 0; month < 12; month++) {
                    const value = Math.random() * 20 - 10; // -10% a +10%
                    const colorClass = value > 5 ? 'bg-success-500' : 
                                      value > 0 ? 'bg-success-300' : 
                                      value > -5 ? 'bg-danger-300' : 'bg-danger-500';
                    
                    html += `<div class="w-8 h-8 ${colorClass} rounded flex items-center justify-center text-xs font-medium text-white cursor-pointer hover:opacity-80" 
                              title="${value.toFixed(1)}%">${value > 0 ? '+' : ''}${value.toFixed(0)}%</div>`;
                }
            }
            
            html += '</div>';
            container.innerHTML = html;
        },
        
        // Inicializar sparklines
        initSparklines() {
            this.ativos.forEach(ativo => {
                const ctx = document.getElementById(`sparkline-${ativo.ticker}`);
                if (ctx) {
                    new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: ativo.sparkline.map((_, i) => i),
                            datasets: [{
                                data: ativo.sparkline,
                                borderColor: ativo.percentual >= 0 ? 'rgba(16, 185, 129, 1)' : 'rgba(239, 68, 68, 1)',
                                borderWidth: 2,
                                fill: false,
                                tension: 0.4,
                                pointRadius: 0
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: { display: false },
                                tooltip: { enabled: false }
                            },
                            scales: {
                                x: { display: false },
                                y: { display: false }
                            }
                        }
                    });
                }
            });
        },
        
        // Gerar labels de data
        generateDateLabels(period) {
            const labels = [];
            const now = new Date();
            
            let days = 30;
            if (period === '6M') days = 180;
            else if (period === '1A') days = 365;
            else if (period === '5A') days = 1825;
            
            for (let i = days; i >= 0; i -= Math.max(1, Math.floor(days / 20))) {
                const date = new Date(now);
                date.setDate(date.getDate() - i);
                labels.push(date.toLocaleDateString('pt-BR', { month: 'short', day: 'numeric' }));
            }
            
            return labels;
        },
        
        // Mudar período
        changePeriod(newPeriod) {
            this.period = newPeriod;
            this.initCharts();
        },
        
        // Handle mudança de moeda
        handleCurrencyChange(detail) {
            this.currency = detail.currency;
            this.exchangeRate = detail.rate;
            localStorage.setItem('preferredCurrency', this.currency);
            
            // Atualizar gráficos
            this.initCharts();
        },
        
        // Filtrar ativos
        get filteredAtivos() {
            let filtered = this.ativos;
            
            // Filtrar por busca
            if (this.searchAtivo) {
                filtered = filtered.filter(a => 
                    a.ticker.toLowerCase().includes(this.searchAtivo.toLowerCase()) ||
                    a.nome.toLowerCase().includes(this.searchAtivo.toLowerCase())
                );
            }
            
            // Ordenar
            return filtered.sort((a, b) => {
                switch (this.sortBy) {
                    case 'valor':
                        return b.resultado - a.resultado;
                    case 'percentual':
                        return b.percentual - a.percentual;
                    case 'ticker':
                        return a.ticker.localeCompare(b.ticker);
                    default:
                        return 0;
                }
            });
        },
        
        // Ordenar ativos
        sortAtivos() {
            // A reatividade do Alpine.js vai atualizar automaticamente
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
        }
    }
}
