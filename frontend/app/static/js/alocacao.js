/**
 * Alocação e Rebalanceamento - JavaScript
 * Sistema de visualização e gerenciamento de alocação de ativos
 */

// Função Alpine.js para gerenciar dados de alocação
function alocacaoData() {
    return {
        currency: localStorage.getItem('preferredCurrency') || 'BRL',
        exchangeRate: 5.00,
        loading: true,
        searchAtivo: '',
        sortBy: 'valor',
        view: 'pizza',
        
        // Resumo
        resumo: {
            patrimonio_total: 0,
            numero_ativos: 0,
            maior_alocacao: { ticker: '', valor: 0, percentual: 0 },
            top5_valor: 0,
            top5_percentual: 0,
            hhi_score: 0,
            diversificacao_nivel: ''
        },
        
        // Dados dos ativos
        ativos: [],
        
        // Top ativos
        topAtivos: [],
        
        // Análise setorial
        analiseSetorial: [],
        
        // Inicialização
        init() {
            this.loadAlocacaoData();
            this.initCharts();
        },
        
        // Carregar dados
        async loadAlocacaoData() {
            this.loading = true;
            
            try {
                // Carregar posições
                const positionsResponse = await fetch('/api/posicoes');
                if (positionsResponse.ok) {
                    const positionsData = await positionsResponse.json();
                    this.processarDados(positionsData.data || []);
                }
                
                // Inicializar gráficos após carregar dados
                this.$nextTick(() => {
                    this.initCharts();
                });
                
            } catch (error) {
                console.error('Erro ao carregar dados de alocação:', error);
                // Carregar dados mock em caso de erro
                this.loadMockData();
            } finally {
                this.loading = false;
            }
        },
        
        // Processar dados
        processarDados(posicoes) {
            // Processar ativos
            this.ativos = posicoes.map(pos => {
                const valorTotal = pos.quantidade * pos.preco_medio * (1 + (Math.random() * 0.3 - 0.15));
                return {
                    ticker: pos.ativo.ticker,
                    nome: pos.ativo.nome,
                    quantidade: pos.quantidade,
                    preco_medio: pos.preco_medio,
                    preco_atual: valorTotal / pos.quantidade,
                    valor_total: valorTotal,
                    setor: pos.ativo.setor || 'Outros'
                };
            });
            
            // Calcular percentuais
            const patrimonioTotal = this.ativos.reduce((sum, a) => sum + a.valor_total, 0);
            this.ativos.forEach(ativo => {
                ativo.percentual = (ativo.valor_total / patrimonioTotal) * 100;
            });
            
            // Ordenar por valor
            this.ativos.sort((a, b) => b.valor_total - a.valor_total);
            
            // Calcular resumo
            this.calcularResumo(patrimonioTotal);
            
            // Top ativos
            this.topAtivos = this.ativos.slice(0, 15);
            
            // Análise setorial
            this.calcularAnaliseSetorial();
        },
        
        // Calcular resumo
        calcularResumo(patrimonioTotal) {
            const top5 = this.ativos.slice(0, 5);
            const top5Valor = top5.reduce((sum, a) => sum + a.valor_total, 0);
            
            // Calcular HHI (Herfindahl-Hirschman Index)
            let hhi = 0;
            this.ativos.forEach(ativo => {
                const share = ativo.percentual / 100;
                hhi += share * share;
            });
            hhi *= 10000; // Converter para escala 0-10000
            
            // Nível de diversificação
            let nivel = 'Excelente';
            if (hhi > 2500) nivel = 'Baixa';
            else if (hhi > 1500) nivel = 'Média';
            else if (hhi > 1000) nivel = 'Boa';
            
            this.resumo = {
                patrimonio_total: patrimonioTotal,
                numero_ativos: this.ativos.length,
                maior_alocacao: this.ativos.length > 0 ? {
                    ticker: this.ativos[0].ticker,
                    valor: this.ativos[0].valor_total,
                    percentual: this.ativos[0].percentual
                } : { ticker: '', valor: 0, percentual: 0 },
                top5_valor: top5Valor,
                top5_percentual: (top5Valor / patrimonioTotal) * 100,
                hhi_score: Math.round(hhi),
                diversificacao_nivel: nivel
            };
        },
        
        // Calcular análise setorial
        calcularAnaliseSetorial() {
            const setores = {};
            const cores = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#14B8A6', '#F97316'];
            
            this.ativos.forEach((ativo, index) => {
                const setor = ativo.setor || 'Outros';
                
                if (!setores[setor]) {
                    setores[setor] = {
                        nome: setor,
                        valor: 0,
                        cor: cores[Object.keys(setores).length % cores.length]
                    };
                }
                setores[setor].valor += ativo.valor_total;
            });
            
            const total = Object.values(setores).reduce((sum, s) => sum + s.valor, 0);
            
            this.analiseSetorial = Object.values(setores)
                .map(setor => ({
                    ...setor,
                    percentual: (setor.valor / total) * 100
                }))
                .sort((a, b) => b.valor - a.valor);
        },
        
        // Carregar dados mock
        loadMockData() {
            const mockPosicoes = [
                { ativo: { ticker: 'PETR4', nome: 'Petrobras PN', setor: 'Petróleo e Gás' }, quantidade: 300, preco_medio: 28.50 },
                { ativo: { ticker: 'VALE3', nome: 'Vale ON', setor: 'Mineração' }, quantidade: 200, preco_medio: 65.20 },
                { ativo: { ticker: 'ITUB4', nome: 'Itaú Unibanco PN', setor: 'Financeiro' }, quantidade: 400, preco_medio: 22.80 },
                { ativo: { ticker: 'BBDC4', nome: 'Bradesco PN', setor: 'Financeiro' }, quantidade: 350, preco_medio: 18.50 },
                { ativo: { ticker: 'WEGE3', nome: 'WEG ON', setor: 'Industrial' }, quantidade: 150, preco_medio: 32.50 },
                { ativo: { ticker: 'MGLU3', nome: 'Magazine Luiza ON', setor: 'Varejo' }, quantidade: 500, preco_medio: 3.80 },
                { ativo: { ticker: 'B3SA3', nome: 'B3 ON', setor: 'Financeiro' }, quantidade: 100, preco_medio: 15.20 },
                { ativo: { ticker: 'HGLG11', nome: 'CSHG Logística', setor: 'Fundos Imobiliários' }, quantidade: 200, preco_medio: 180.50 }
            ];
            
            this.processarDados(mockPosicoes);
        },
        
        // Inicializar gráficos
        initCharts() {
            this.initAlocacaoChart();
            this.initCategoriaChart();
        },
        
        // Gráfico de alocação
        initAlocacaoChart() {
            const ctx = document.getElementById('alocacao-chart');
            if (!ctx) return;
            
            const data = this.ativos.slice(0, 10).map(a => a.valor_total);
            const labels = this.ativos.slice(0, 10).map(a => a.ticker);
            const cores = [
                '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6',
                '#EC4899', '#14B8A6', '#F97316', '#06B6D4', '#84CC16'
            ];
            
            new Chart(ctx, {
                type: this.view === 'pizza' ? 'doughnut' : 'treemap',
                data: {
                    labels: labels,
                    datasets: [{
                        data: data,
                        backgroundColor: cores,
                        borderColor: cores,
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
                                    const percent = this.ativos[context.dataIndex].percentual.toFixed(1);
                                    return `${context.label}: ${value} (${percent}%)`;
                                }
                            }
                        }
                    }
                }
            });
        },
        
        // Gráfico por categoria
        initCategoriaChart() {
            const ctx = document.getElementById('categoria-chart');
            if (!ctx) return;
            
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: this.analiseSetorial.map(s => s.nome),
                    datasets: [{
                        label: 'Valor por Setor',
                        data: this.analiseSetorial.map(s => s.valor),
                        backgroundColor: this.analiseSetorial.map(s => s.cor),
                        borderColor: this.analiseSetorial.map(s => s.cor),
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            callbacks: {
                                label: (context) => {
                                    const value = this.formatCurrency(context.raw, this.currency);
                                    const percent = this.analiseSetorial[context.dataIndex].percentual.toFixed(1);
                                    return `${context.label}: ${value} (${percent}%)`;
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: (value) => this.formatCurrency(value, this.currency, false)
                            }
                        }
                    }
                }
            });
        },
        
        // Mudar visualização
        changeView(newView) {
            this.view = newView;
            this.initAlocacaoChart();
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
                        return b.valor_total - a.valor_total;
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
        
        // Ver detalhes
        verDetalhes(ticker) {
            window.location.href = `/dashboard/ativo/${ticker}`;
        },
        
        // Editar posição
        editarPosicao(ativo) {
            // Implementar modal de edição
            console.log('Editar posição:', ativo);
        },
        
        // Abrir rebalanceamento
        openRebalanceamento() {
            // Implementar modal de rebalanceamento
            console.log('Abrir rebalanceamento');
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
        }
    }
}
