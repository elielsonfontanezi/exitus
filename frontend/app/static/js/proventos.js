/**
 * Gestão de Proventos - JavaScript
 * Sistema de calendário e análise de dividendos
 */

// Função Alpine.js para gerenciar dados de proventos
function proventosData() {
    return {
        currency: localStorage.getItem('preferredCurrency') || 'BRL',
        exchangeRate: 5.00,
        loading: true,
        anoSelecionado: '2024',
        tipoProvento: 'todos',
        vista: 'calendario',
        
        // Resumo
        resumo: {
            total_recebido: 0,
            media_mensal: 0,
            valor_a_receber: 0,
            proventos_a_receber: 0,
            proximo_provento: { data: '', valor: 0 },
            yield_on_cost: 0,
            dy_atual: 0,
            projecao_anual: 0
        },
        
        // Dados dos proventos
        proventos: [],
        
        // Top proventos
        topProventos: [],
        
        // Análise setorial
        analiseSetorial: [],
        
        // Calendário mensal
        calendarioMensal: {},
        
        // Inicialização
        init() {
            this.carregarDados();
            this.initCharts();
        },
        
        // Carregar dados
        async carregarDados() {
            this.loading = true;
            
            try {
                // Carregar proventos
                const proventosResponse = await fetch(`/api/proventos?ano=${this.anoSelecionado}`);
                if (proventosResponse.ok) {
                    const proventosData = await proventosResponse.json();
                    this.proventos = proventosData.data || [];
                    this.processarDados();
                }
                
                // Carregar posições para yield on cost
                const positionsResponse = await fetch('/api/posicoes');
                if (positionsResponse.ok) {
                    const positionsData = await positionsResponse.json();
                    this.calcularYieldOnCost(positionsData.data || []);
                }
                
                // Inicializar gráficos após carregar dados
                this.$nextTick(() => {
                    this.initCharts();
                });
                
            } catch (error) {
                console.error('Erro ao carregar dados de proventos:', error);
                // Carregar dados mock em caso de erro
                this.loadMockData();
            } finally {
                this.loading = false;
            }
        },
        
        // Processar dados
        processarDados() {
            // Calcular resumo
            this.calcularResumo();
            
            // Gerar calendário
            this.gerarCalendario();
            
            // Top proventos
            this.calcularTopProventos();
            
            // Análise setorial
            this.calcularAnaliseSetorial();
        },
        
        // Calcular resumo
        calcularResumo() {
            const recebidos = this.proventos.filter(p => p.status === 'RECEBIDO');
            const aReceber = this.proventos.filter(p => p.status === 'A_RECEBER');
            
            const totalRecebido = recebidos.reduce((sum, p) => sum + p.valor, 0);
            const valorAReceber = aReceber.reduce((sum, p) => sum + p.valor, 0);
            
            this.resumo = {
                total_recebido: totalRecebido,
                media_mensal: totalRecebido / 12,
                valor_a_receber: valorAReceber,
                proventos_a_receber: aReceber.length,
                proximo_provento: aReceber.length > 0 ? {
                    data: this.formatDate(aReceber[0].data_com),
                    valor: aReceber[0].valor
                } : { data: '-', valor: 0 },
                yield_on_cost: 8.5, // Mock
                dy_atual: 6.2, // Mock
                projecao_anual: totalRecebido * 1.15 // Mock: +15% YTD
            };
        },
        
        // Gerar calendário
        gerarCalendario() {
            const meses = [
                { numero: 1, nome: 'Janeiro', proventos: [] },
                { numero: 2, nome: 'Fevereiro', proventos: [] },
                { numero: 3, nome: 'Março', proventos: [] },
                { numero: 4, nome: 'Abril', proventos: [] },
                { numero: 5, nome: 'Maio', proventos: [] },
                { numero: 6, nome: 'Junho', proventos: [] },
                { numero: 7, nome: 'Julho', proventos: [] },
                { numero: 8, nome: 'Agosto', proventos: [] },
                { numero: 9, nome: 'Setembro', proventos: [] },
                { numero: 10, nome: 'Outubro', proventos: [] },
                { numero: 11, nome: 'Novembro', proventos: [] },
                { numero: 12, nome: 'Dezembro', proventos: [] }
            ];
            
            // Distribuir proventos nos meses
            this.proventos.forEach(provento => {
                const data = new Date(provento.data_com);
                const mes = data.getMonth() + 1;
                const mesObj = meses.find(m => m.numero === mes);
                if (mesObj) {
                    mesObj.proventos.push(provento);
                }
            });
            
            // Calcular totais mensais
            meses.forEach(mes => {
                mes.total = mes.proventos.reduce((sum, p) => sum + p.valor, 0);
            });
            
            this.calendarioMensal = meses;
        },
        
        // Calcular top proventos
        calcularTopProventos() {
            const totaisPorAtivo = {};
            
            this.proventos.forEach(provento => {
                if (!totaisPorAtivo[provento.ativo.ticker]) {
                    totaisPorAtivo[provento.ativo.ticker] = {
                        ticker: provento.ativo.ticker,
                        nome: provento.ativo.nome,
                        total: 0,
                        eventos: 0
                    };
                }
                totaisPorAtivo[provento.ativo.ticker].total += provento.valor;
                totaisPorAtivo[provento.ativo.ticker].eventos += 1;
            });
            
            this.topProventos = Object.values(totaisPorAtivo)
                .sort((a, b) => b.total - a.total)
                .slice(0, 10);
        },
        
        // Calcular análise setorial
        calcularAnaliseSetorial() {
            const setores = {};
            const cores = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'];
            
            this.proventos.forEach((provento, index) => {
                const setor = provento.ativo.setor || 'Outros';
                
                if (!setores[setor]) {
                    setores[setor] = {
                        nome: setor,
                        total: 0,
                        cor: cores[Object.keys(setores).length % cores.length]
                    };
                }
                setores[setor].total += provento.valor;
            });
            
            const total = Object.values(setores).reduce((sum, s) => sum + s.total, 0);
            
            this.analiseSetorial = Object.values(setores)
                .map(setor => ({
                    ...setor,
                    percentual: (setor.total / total) * 100
                }))
                .sort((a, b) => b.total - a.total);
        },
        
        // Calcular Yield on Cost
        calcularYieldOnCost(posicoes) {
            // Mock: em produção calcular com base no custo médio vs dividendos
            this.resumo.yield_on_cost = 8.5;
            this.resumo.dy_atual = 6.2;
        },
        
        // Carregar dados mock
        loadMockData() {
            // Mock de proventos
            this.proventos = [
                {
                    id: 1,
                    data_com: '2024-01-15',
                    tipo: 'DIVIDENDO',
                    valor: 1500,
                    valor_por_acao: 0.50,
                    quantidade: 3000,
                    status: 'RECEBIDO',
                    ativo: { ticker: 'PETR4', nome: 'Petrobras PN', setor: 'Petróleo e Gás' }
                },
                {
                    id: 2,
                    data_com: '2024-02-10',
                    tipo: 'JCP',
                    valor: 900,
                    valor_por_acao: 0.30,
                    quantidade: 3000,
                    status: 'RECEBIDO',
                    ativo: { ticker: 'PETR4', nome: 'Petrobras PN', setor: 'Petróleo e Gás' }
                },
                {
                    id: 3,
                    data_com: '2024-03-20',
                    tipo: 'DIVIDENDO',
                    valor: 800,
                    valor_por_acao: 0.40,
                    quantidade: 2000,
                    status: 'RECEBIDO',
                    ativo: { ticker: 'VALE3', nome: 'Vale ON', setor: 'Mineração' }
                },
                {
                    id: 4,
                    data_com: '2024-04-15',
                    tipo: 'DIVIDENDO',
                    valor: 1200,
                    valor_por_acao: 0.60,
                    quantidade: 2000,
                    status: 'A_RECEBER',
                    ativo: { ticker: 'ITUB4', nome: 'Itaú Unibanco PN', setor: 'Financeiro' }
                },
                {
                    id: 5,
                    data_com: '2024-05-10',
                    tipo: 'RENDIMENTO',
                    valor: 450,
                    valor_por_acao: 0.45,
                    quantidade: 1000,
                    status: 'A_RECEBER',
                    ativo: { ticker: 'HGLG11', nome: 'CSHG Logística', setor: 'Fundos Imobiliários' }
                }
            ];
            
            this.processarDados();
        },
        
        // Inicializar gráficos
        initCharts() {
            this.initProventosChart();
            this.initSectorChart();
        },
        
        // Gráfico de evolução mensal
        initProventosChart() {
            const ctx = document.getElementById('proventos-chart');
            if (!ctx) return;
            
            const labels = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
            const data = labels.map((mes, index) => {
                const mesObj = this.calendarioMensal[index];
                return mesObj ? mesObj.total : 0;
            });
            
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Proventos',
                        data: data,
                        backgroundColor: 'rgba(16, 185, 129, 0.8)',
                        borderColor: 'rgba(16, 185, 129, 1)',
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
                                label: (context) => `Proventos: ${this.formatCurrency(context.raw, this.currency)}`
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
        
        // Gráfico setorial
        initSectorChart() {
            const ctx = document.getElementById('sector-chart');
            if (!ctx) return;
            
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: this.analiseSetorial.map(s => s.nome),
                    datasets: [{
                        data: this.analiseSetorial.map(s => s.total),
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
                                    const value = this.formatCurrency(context.raw, this.currency);
                                    const percent = this.analiseSetorial[context.dataIndex].percentual.toFixed(1);
                                    return `${context.label}: ${value} (${percent}%)`;
                                }
                            }
                        }
                    }
                }
            });
        },
        
        // Filtrar proventos
        filtrarProventos() {
            // A reatividade do Alpine.js vai atualizar automaticamente
        },
        
        // Mudar vista
        mudarVista() {
            // A reatividade do Alpine.js vai atualizar automaticamente
        },
        
        // Exportar dados
        exportarDados() {
            // Implementar exportação CSV/Excel
            alert('Função de exportação em desenvolvimento...');
        },
        
        // Handle mudança de moeda
        handleCurrencyChange(detail) {
            this.currency = detail.currency;
            this.exchangeRate = detail.rate;
            localStorage.setItem('preferredCurrency', this.currency);
            
            // Atualizar gráficos
            this.initCharts();
        },
        
        // Proventos filtrados
        get filteredProventos() {
            let filtered = this.proventos;
            
            // Filtrar por tipo
            if (this.tipoProvento !== 'todos') {
                filtered = filtered.filter(p => 
                    p.tipo.toLowerCase() === this.tipoProvento.toLowerCase()
                );
            }
            
            return filtered.sort((a, b) => new Date(b.data_com) - new Date(a.data_com));
        },
        
        // Utilitários
        getTrimestreNome(trimestre) {
            return `${trimestre}º Trimestre`;
        },
        
        getMesesTrimestre(trimestre) {
            const inicio = (trimestre - 1) * 3;
            return this.calendarioMensal.slice(inicio, inicio + 3);
        },
        
        getTipoProventoClass(tipo) {
            const classes = {
                'DIVIDENDO': 'badge-success',
                'JCP': 'badge-primary',
                'RENDIMENTO': 'badge-warning'
            };
            return classes[tipo] || 'badge-gray';
        },
        
        formatDate(dateStr) {
            const date = new Date(dateStr);
            return date.toLocaleDateString('pt-BR', { 
                day: '2-digit', 
                month: '2-digit', 
                year: 'numeric' 
            });
        },
        
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
