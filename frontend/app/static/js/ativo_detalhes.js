/**
 * Análise de Ativos - JavaScript
 * Sistema de dados com APIs reais e gráficos Chart.js
 */

// Função Alpine.js para gerenciar dados do ativo
function ativoData() {
    return {
        currency: localStorage.getItem('preferredCurrency') || 'BRL',
        exchangeRate: 5.00,
        period: '1A',
        loading: true,
        ticker: '', // Será extraído da URL
        
        // Dados do ativo
        ativo: {
            ticker: '',
            nome: '',
            preco_atual: 0,
            variacao_dia: 0,
            buy_score: 0
        },
        
        // Indicadores
        indicadores: [],
        
        // Buy Score breakdown
        buy_score_breakdown: [],
        
        // Proventos
        proventos: [],
        
        // Eventos
        eventos: [],
        
        // Comparação setorial
        comparacao_setorial: [],
        
        // Inicialização
        init() {
            // Extrair ticker da URL
            const pathParts = window.location.pathname.split('/');
            this.ticker = pathParts[pathParts.length - 1];
            
            this.loadAtivoData();
            this.initCharts();
        },
        
        // Carregar dados do ativo
        async loadAtivoData() {
            this.loading = true;
            
            try {
                // Carregar dados básicos do ativo
                const ativoResponse = await fetch(`/api/ativos/ticker/${this.ticker}`);
                if (ativoResponse.ok) {
                    const ativoData = await ativoResponse.json();
                    this.ativo = ativoData.data;
                }
                
                // Carregar cotações
                const cotacaoResponse = await fetch(`/api/cotacoes/${this.ticker}`);
                if (cotacaoResponse.ok) {
                    const cotacaoData = await cotacaoResponse.json();
                    this.ativo.preco_atual = cotacaoData.data.preco;
                    this.ativo.variacao_dia = cotacaoData.data.variacao_percentual;
                }
                
                // Carregar buy score
                const scoreResponse = await fetch(`/api/buy-signals/buy-score/${this.ticker}`);
                if (scoreResponse.ok) {
                    const scoreData = await scoreResponse.json();
                    this.ativo.buy_score = scoreData.data.score;
                    this.buy_score_breakdown = scoreData.data.breakdown || [];
                }
                
                // Carregar indicadores
                this.loadIndicadores();
                
                // Carregar proventos
                const proventosResponse = await fetch(`/api/proventos?ativo_ticker=${this.ticker}&limit=10`);
                if (proventosResponse.ok) {
                    const proventosData = await proventosResponse.json();
                    this.proventos = proventosData.data || [];
                }
                
                // Carregar eventos
                const eventosResponse = await fetch(`/api/eventos-corporativos?ativo_ticker=${this.ticker}&limit=10`);
                if (eventosResponse.ok) {
                    const eventosData = await eventosResponse.json();
                    this.eventos = eventosData.data || [];
                }
                
                // Carregar comparação setorial
                this.loadComparacaoSetorial();
                
                // Inicializar gráficos após carregar dados
                this.$nextTick(() => {
                    this.initCharts();
                });
                
            } catch (error) {
                console.error('Erro ao carregar dados do ativo:', error);
                // Carregar dados mock em caso de erro
                this.loadMockData();
            } finally {
                this.loading = false;
            }
        },
        
        // Carregar indicadores fundamentalistas
        loadIndicadores() {
            // Mock: em produção virá da API
            this.indicadores = [
                { nome: 'P/L', valor: '8.5', cor: 'text-primary-600', descricao: 'Preço/Lucro' },
                { nome: 'P/VP', valor: '1.2', cor: 'text-success-600', descricao: 'Preço/Valor Patrimonial' },
                { nome: 'ROE', valor: '15%', cor: 'text-success-600', descricao: 'Return on Equity' },
                { nome: 'DY', valor: '5.2%', cor: 'text-warning-600', descricao: 'Dividend Yield' },
                { nome: 'Margem', valor: '12%', cor: 'text-primary-600', descricao: 'Margem Líquida' },
                { nome: 'LPA', valor: '4.52', cor: 'text-gray-600', descricao: 'Lucro por Ação' }
            ];
        },
        
        // Carregar comparação setorial
        loadComparacaoSetorial() {
            // Mock: em produção virá da API
            this.comparacao_setorial = [
                { ticker: this.ticker, pl: '8.5', pvp: '1.2', dy: 5.2, score: 85 },
                { ticker: 'VALE3', pl: '6.2', pvp: '0.9', dy: 8.1, score: 92 },
                { ticker: 'ITUB4', pl: '10.3', pvp: '1.5', dy: 3.8, score: 78 },
                { ticker: 'BBDC4', pl: '9.8', pvp: '1.3', dy: 4.5, score: 82 },
                { ticker: 'SANB11', pl: '11.2', pvp: '1.6', dy: 3.2, score: 75 }
            ];
        },
        
        // Carregar dados mock
        loadMockData() {
            this.ativo = {
                ticker: this.ticker,
                nome: 'Petrobras PN',
                preco_atual: 38.50,
                variacao_dia: 2.45,
                buy_score: 85
            };
            
            this.loadIndicadores();
            this.loadComparacaoSetorial();
            
            this.buy_score_breakdown = [
                { nome: 'Valuation', pontos: 22, cor: 'bg-success-500' },
                { nome: 'Rentabilidade', pontos: 18, cor: 'bg-primary-500' },
                { nome: 'Endividamento', pontos: 15, cor: 'bg-warning-500' },
                { nome: 'Eficiência', pontos: 20, cor: 'bg-success-500' },
                { nome: 'Crescimento', pontos: 10, cor: 'bg-danger-500' }
            ];
            
            this.proventos = [
                { id: 1, tipo: 'Dividendo', data_com: '2024-03-15', valor: 1500, valor_por_acao: 0.50 },
                { id: 2, tipo: 'JCP', data_com: '2024-02-10', valor: 900, valor_por_acao: 0.30 },
                { id: 3, tipo: 'Dividendo', data_com: '2024-01-12', valor: 1200, valor_por_acao: 0.40 }
            ];
            
            this.eventos = [
                { id: 1, tipo: 'Split 1:2', data: '2024-01-01', descricao: 'Ações desdobradas' }
            ];
        },
        
        // Inicializar gráficos
        initCharts() {
            this.initPriceChart();
            this.initRadarChart();
            this.initSectorChart();
        },
        
        // Gráfico de Preço
        initPriceChart() {
            const ctx = document.getElementById('price-chart');
            if (!ctx) return;
            
            // Gerar dados mock para o gráfico
            const labels = this.generateDateLabels(this.period);
            const data = labels.map(() => this.ativo.preco_atual * (0.9 + Math.random() * 0.2));
            
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Preço',
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
                                label: (context) => `Preço: ${this.formatCurrency(context.raw, this.currency)}`
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
        
        // Gráfico Radar
        initRadarChart() {
            const ctx = document.getElementById('radar-chart');
            if (!ctx) return;
            
            new Chart(ctx, {
                type: 'radar',
                data: {
                    labels: ['Valuation', 'Rentabilidade', 'Endividamento', 'Eficiência', 'Crescimento', 'DY'],
                    datasets: [{
                        label: this.ativo.ticker,
                        data: [85, 75, 90, 80, 60, 85],
                        borderColor: 'rgba(59, 130, 246, 1)',
                        backgroundColor: 'rgba(59, 130, 246, 0.2)',
                        borderWidth: 2,
                        pointRadius: 4,
                        pointHoverRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        r: {
                            beginAtZero: true,
                            max: 100,
                            ticks: {
                                stepSize: 20
                            }
                        }
                    }
                }
            });
        },
        
        // Gráfico Setorial
        initSectorChart() {
            const ctx = document.getElementById('sector-chart');
            if (!ctx) return;
            
            const labels = this.comparacao_setorial.map(c => c.ticker);
            const scores = this.comparacao_setorial.map(c => c.score);
            
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Buy Score',
                        data: scores,
                        backgroundColor: scores.map(s => 
                            s >= 90 ? 'rgba(16, 185, 129, 0.8)' :
                            s >= 80 ? 'rgba(59, 130, 246, 0.8)' :
                            s >= 70 ? 'rgba(245, 158, 11, 0.8)' :
                            'rgba(239, 68, 68, 0.8)'
                        ),
                        borderColor: scores.map(s => 
                            s >= 90 ? 'rgba(16, 185, 129, 1)' :
                            s >= 80 ? 'rgba(59, 130, 246, 1)' :
                            s >= 70 ? 'rgba(245, 158, 11, 1)' :
                            'rgba(239, 68, 68, 1)'
                        ),
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            ticks: {
                                stepSize: 20
                            }
                        }
                    }
                }
            });
        },
        
        // Gerar labels de data
        generateDateLabels(period) {
            const labels = [];
            const now = new Date();
            
            let days = 30;
            if (period === '3M') days = 90;
            else if (period === '6M') days = 180;
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
            this.initPriceChart();
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
        
        // Formatar data
        formatDate(dateStr) {
            const date = new Date(dateStr);
            return date.toLocaleDateString('pt-BR', { 
                day: '2-digit', 
                month: '2-digit', 
                year: 'numeric' 
            });
        },
        
        // Cor para Buy Score
        getBuyScoreClass(score) {
            if (score >= 90) return 'badge-gradient-success';
            if (score >= 80) return 'badge-gradient-primary';
            if (score >= 70) return 'badge-gradient-warning';
            return 'badge-gradient-danger';
        },
        
        // Gradiente para Buy Score
        getBuyScoreGradient(score) {
            if (score >= 90) return 'bg-gradient-success';
            if (score >= 80) return 'bg-gradient-primary';
            if (score >= 70) return 'bg-gradient-warning';
            return 'bg-gradient-danger';
        }
    }
}
