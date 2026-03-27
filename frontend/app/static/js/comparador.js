/**
 * Comparador de Ativos - JavaScript
 * Sistema de comparação lado a lado de múltiplos ativos
 */

// Função Alpine.js para gerenciar dados de comparação
function comparadorData() {
    return {
        currency: localStorage.getItem('preferredCurrency') || 'BRL',
        exchangeRate: 5.00,
        loading: true,
        ativosSelecionados: [],
        mostrarComparacao: false,
        
        // Dados dos ativos disponíveis
        ativosComparacao: [],
        
        // Dados da comparação
        dadosComparacao: [],
        
        // Análise setorial
        analiseSetorial: [],
        
        // Recomendações
        recomendacoes: {
            melhor_custo_beneficio: {},
            maior_potencial: {},
            mais_seguro: {}
        },
        
        // Inicialização
        init() {
            this.carregarAtivos();
        },
        
        // Carregar ativos disponíveis
        async carregarAtivos() {
            this.loading = true;
            
            try {
                // Carregar ativos do backend
                const response = await fetch('/api/ativos');
                if (response.ok) {
                    const data = await response.json();
                    this.ativosComparacao = data.data?.ativos || [];
                }
            } catch (error) {
                console.error('Erro ao carregar ativos:', error);
                // Carregar dados mock em caso de erro
                this.loadMockAtivos();
            } finally {
                this.loading = false;
            }
        },
        
        // Carregar dados mock
        loadMockAtivos() {
            this.ativosComparacao = [
                { ticker: 'PETR4', nome: 'Petrobras PN', setor: 'Petróleo e Gás' },
                { ticker: 'VALE3', nome: 'Vale ON', setor: 'Mineração' },
                { ticker: 'ITUB4', nome: 'Itaú Unibanco PN', setor: 'Financeiro' },
                { ticker: 'BBDC4', nome: 'Bradesco PN', setor: 'Financeiro' },
                { ticker: 'WEGE3', nome: 'WEG ON', setor: 'Industrial' },
                { ticker: 'MGLU3', nome: 'Magazine Luiza ON', setor: 'Varejo' },
                { ticker: 'B3SA3', nome: 'B3 ON', setor: 'Financeiro' },
                { ticker: 'HGLG11', nome: 'CSHG Logística', setor: 'Fundos Imobiliários' }
            ];
        },
        
        // Toggle seleção de ativo
        toggleAtivo(ticker) {
            const index = this.ativosSelecionados.indexOf(ticker);
            if (index > -1) {
                this.ativosSelecionados.splice(index, 1);
            } else {
                if (this.ativosSelecionados.length < 6) { // Limite de 6 ativos
                    this.ativosSelecionados.push(ticker);
                } else {
                    alert('Máximo de 6 ativos para comparação');
                }
            }
        },
        
        // Comparar ativos selecionados
        async compararAtivos() {
            if (this.ativosSelecionados.length < 2) {
                alert('Selecione pelo menos 2 ativos para comparar');
                return;
            }
            
            this.loading = true;
            
            try {
                // Carregar dados detalhados dos ativos selecionados
                const promises = this.ativosSelecionados.map(ticker => 
                    fetch(`/api/ativos/ticker/${ticker}`).then(res => res.json())
                );
                
                const results = await Promise.all(promises);
                this.dadosComparacao = results.map(result => this.processarDadosAtivo(result.data));
                
                // Calcular análises
                this.calcularAnaliseSetorial();
                this.gerarRecomendacoes();
                
                // Mostrar comparação
                this.mostrarComparacao = true;
                
                // Inicializar gráficos
                this.$nextTick(() => {
                    this.initCharts();
                });
                
            } catch (error) {
                console.error('Erro ao comparar ativos:', error);
                // Carregar dados mock da comparação
                this.loadMockComparacao();
            } finally {
                this.loading = false;
            }
        },
        
        // Processar dados do ativo
        processarDadosAtivo(ativo) {
            return {
                ticker: ativo.ticker,
                nome: ativo.nome,
                setor: ativo.setor || 'Outros',
                preco_atual: ativo.preco_atual || (Math.random() * 100 + 10),
                variacao: (Math.random() * 10 - 5), // -5% a +5%
                indicadores: {
                    pl: ativo.indicadores?.pl || (Math.random() * 20 + 5),
                    pvp: ativo.indicadores?.pvp || (Math.random() * 3 + 0.5),
                    roe: ativo.indicadores?.roe || (Math.random() * 30 + 5),
                    dy: ativo.indicadores?.dy || (Math.random() * 10 + 2),
                    liquidez: ativo.indicadores?.liquidez || (Math.random() * 10000000 + 1000000)
                },
                buy_score: ativo.buy_score || (Math.random() * 100)
            };
        },
        
        // Carregar dados mock da comparação
        loadMockComparacao() {
            this.dadosComparacao = this.ativosSelecionados.map(ticker => {
                const ativo = this.ativosComparacao.find(a => a.ticker === ticker);
                return this.processarDadosAtivo(ativo);
            });
            
            this.calcularAnaliseSetorial();
            this.gerarRecomendacoes();
            this.mostrarComparacao = true;
            
            this.$nextTick(() => {
                this.initCharts();
            });
        },
        
        // Calcular análise setorial
        calcularAnaliseSetorial() {
            const setores = {};
            const cores = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'];
            
            this.dadosComparacao.forEach((ativo, index) => {
                const setor = ativo.setor || 'Outros';
                
                if (!setores[setor]) {
                    setores[setor] = {
                        nome: setor,
                        ativos: 0,
                        cor: cores[Object.keys(setores).length % cores.length]
                    };
                }
                setores[setor].ativos += 1;
            });
            
            const total = this.dadosComparacao.length;
            
            this.analiseSetorial = Object.values(setores).map(setor => ({
                ...setor,
                percentual: (setor.ativos / total) * 100
            }));
        },
        
        // Gerar recomendações
        gerarRecomendacoes() {
            if (this.dadosComparacao.length === 0) return;
            
            // Melhor custo-benefício (menor P/L com DY razoável)
            const melhorCustoBeneficio = this.dadosComparacao
                .filter(a => a.indicadores.dy >= 3)
                .sort((a, b) => a.indicadores.pl - b.indicadores.pl)[0] || this.dadosComparacao[0];
            
            // Maior potencial (maior Buy Score)
            const maiorPotencial = this.dadosComparacao
                .sort((a, b) => b.buy_score - a.buy_score)[0];
            
            // Mais seguro (maior liquidez)
            const maisSeguro = this.dadosComparacao
                .sort((a, b) => b.indicadores.liquidez - a.indicadores.liquidez)[0];
            
            this.recomendacoes = {
                melhor_custo_beneficio: {
                    ticker: melhorCustoBeneficio.ticker,
                    pl: melhorCustoBeneficio.indicadores.pl.toFixed(1),
                    dy: melhorCustoBeneficio.indicadores.dy.toFixed(1)
                },
                maior_potencial: {
                    ticker: maiorPotencial.ticker,
                    roe: maiorPotencial.indicadores.roe.toFixed(1),
                    buy_score: maiorPotencial.buy_score.toFixed(0)
                },
                mais_seguro: {
                    ticker: maisSeguro.ticker,
                    liquidez: maisSeguro.indicadores.liquidez,
                    pvp: maisSeguro.indicadores.pvp.toFixed(2)
                }
            };
        },
        
        // Inicializar gráficos
        initCharts() {
            this.initPrecosChart();
            this.initRadarChart();
            this.initSetorChart();
        },
        
        // Gráfico de evolução de preços
        initPrecosChart() {
            const ctx = document.getElementById('precos-chart');
            if (!ctx) return;
            
            // Gerar dados mock de 30 dias
            const labels = [];
            const datasets = [];
            
            for (let i = 29; i >= 0; i--) {
                const date = new Date();
                date.setDate(date.getDate() - i);
                labels.push(date.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' }));
            }
            
            const cores = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'];
            
            this.dadosComparacao.forEach((ativo, index) => {
                const data = [];
                let preco = ativo.preco_atual;
                
                for (let i = 0; i < 30; i++) {
                    data.push(preco * (1 + (Math.random() * 0.1 - 0.05)));
                }
                
                datasets.push({
                    label: ativo.ticker,
                    data: data,
                    borderColor: cores[index % cores.length],
                    backgroundColor: cores[index % cores.length] + '20',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.4
                });
            });
            
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
                                label: (context) => {
                                    const value = this.formatCurrency(context.raw, this.currency);
                                    return `${context.dataset.label}: ${value}`;
                                }
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
        
        // Gráfico radar
        initRadarChart() {
            const ctx = document.getElementById('radar-chart');
            if (!ctx) return;
            
            const labels = ['P/L', 'P/VP', 'ROE', 'DY', 'Buy Score'];
            const datasets = [];
            
            const cores = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'];
            
            this.dadosComparacao.forEach((ativo, index) => {
                // Normalizar valores para 0-100
                const plScore = Math.max(0, 100 - (ativo.indicadores.pl * 5)); // Invertido (menor é melhor)
                const pvpScore = Math.max(0, 100 - (ativo.indicadores.pvp * 20)); // Invertido
                const roeScore = Math.min(100, ativo.indicadores.roe * 3);
                const dyScore = Math.min(100, ativo.indicadores.dy * 10);
                
                datasets.push({
                    label: ativo.ticker,
                    data: [plScore, pvpScore, roeScore, dyScore, ativo.buy_score],
                    borderColor: cores[index % cores.length],
                    backgroundColor: cores[index % cores.length] + '20',
                    borderWidth: 2,
                    pointBackgroundColor: cores[index % cores.length],
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: cores[index % cores.length]
                });
            });
            
            new Chart(ctx, {
                type: 'radar',
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
                        }
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
        
        // Gráfico setorial
        initSetorChart() {
            const ctx = document.getElementById('setor-chart');
            if (!ctx) return;
            
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: this.analiseSetorial.map(s => s.nome),
                    datasets: [{
                        data: this.analiseSetorial.map(s => s.ativos),
                        backgroundColor: this.analiseSetorial.map(s => s.cor),
                        borderColor: this.analiseSetorial.map(s => s.cor),
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
                                    const setor = this.analiseSetorial[context.dataIndex];
                                    return `${context.label}: ${setor.ativos} ativos (${setor.percentual.toFixed(1)}%)`;
                                }
                            }
                        }
                    }
                }
            });
        },
        
        // Exportar comparação
        exportarComparacao() {
            // Implementar exportação CSV/Excel
            alert('Função de exportação em desenvolvimento...');
        },
        
        // Obter classe do Buy Score
        getBuyScoreClass(score) {
            if (score >= 80) return 'bg-success-500';
            if (score >= 60) return 'bg-warning-500';
            return 'bg-danger-500';
        },
        
        // Handle mudança de moeda
        handleCurrencyChange(detail) {
            this.currency = detail.currency;
            this.exchangeRate = detail.rate;
            localStorage.setItem('preferredCurrency', this.currency);
            
            // Atualizar gráficos se estiverem visíveis
            if (this.mostrarComparacao) {
                this.initCharts();
            }
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
