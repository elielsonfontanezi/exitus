/**
 * Planos de Compra Disciplinada - JavaScript
 * Sistema de automação de compras com inteligência artificial
 */

// Função Alpine.js para gerenciar planos de compra
function planosCompraData() {
    return {
        currency: localStorage.getItem('preferredCurrency') || 'BRL',
        exchangeRate: 5.00,
        loading: true,
        abaAtiva: 'planos',
        
        // Resumo
        resumo: {
            planos_ativos: 0,
            total_planos: 0,
            compras_mes: 0,
            total_investido: 0,
            media_investimento: 0,
            economia_percentual: 15.5,
            economia_total: 1250.50,
            proximas_execucoes: 3,
            proxima_data: '18/03',
            proximo_horario: '10:00'
        },
        
        // Dados
        planos: [],
        ativosDisponiveis: [],
        historico: [],
        
        // Novo plano
        novoPlano: {
            nome: '',
            ativo: '',
            tipo: 'valor_fixo',
            valor: 0,
            quantidade: 0,
            frequencia: 'mensal',
            data_inicio: ''
        },
        
        // Inicialização
        init() {
            this.carregarDados();
            this.setDataInicioPadrao();
        },
        
        // Carregar dados
        async carregarDados() {
            this.loading = true;
            
            try {
                // Carregar planos
                const planosResponse = await fetch('/api/planos-compra');
                if (planosResponse.ok) {
                    const planosData = await planosResponse.json();
                    this.planos = planosData.data || [];
                }
                
                // Carregar ativos disponíveis
                const ativosResponse = await fetch('/api/ativos');
                if (ativosResponse.ok) {
                    const ativosData = await ativosResponse.json();
                    this.ativosDisponiveis = ativosData.data?.ativos || [];
                }
                
                // Carregar histórico
                const historicoResponse = await fetch('/api/planos-compra/historico');
                if (historicoResponse.ok) {
                    const historicoData = await historicoResponse.json();
                    this.historico = historicoData.data || [];
                }
                
                // Calcular resumo
                this.calcularResumo();
                
                // Inicializar gráficos se necessário
                this.$nextTick(() => {
                    if (this.abaAtiva === 'ai-insights') {
                        this.initPerformanceChart();
                    }
                });
                
            } catch (error) {
                console.error('Erro ao carregar dados de planos:', error);
                // Carregar dados mock em caso de erro
                this.loadMockData();
            } finally {
                this.loading = false;
            }
        },
        
        // Carregar dados mock
        loadMockData() {
            this.planos = [
                {
                    id: 1,
                    nome: 'Compra Mensal PETR4',
                    ativo: 'PETR4',
                    tipo: 'valor_fixo',
                    valor: 500,
                    frequencia: 'mensal',
                    status: 'ativo',
                    data_inicio: '2024-01-15',
                    proxima_execucao: '2024-03-15',
                    total_investido: 2500
                },
                {
                    id: 2,
                    nome: 'DCA Semanal ITUB4',
                    ativo: 'ITUB4',
                    tipo: 'smart',
                    valor: 200,
                    frequencia: 'semanal',
                    status: 'ativo',
                    data_inicio: '2024-02-01',
                    proxima_execucao: '2024-03-18',
                    total_investido: 1800
                },
                {
                    id: 3,
                    nome: 'Compra VALE3',
                    ativo: 'VALE3',
                    tipo: 'quantidade_fixa',
                    quantidade: 10,
                    frequencia: 'quinzenal',
                    status: 'pausado',
                    data_inicio: '2024-01-10',
                    proxima_execucao: '2024-03-20',
                    total_investido: 3200
                }
            ];
            
            this.ativosDisponiveis = [
                { ticker: 'PETR4', nome: 'Petrobras PN' },
                { ticker: 'VALE3', nome: 'Vale ON' },
                { ticker: 'ITUB4', nome: 'Itaú Unibanco PN' },
                { ticker: 'BBDC4', nome: 'Bradesco PN' },
                { ticker: 'WEGE3', nome: 'WEG ON' }
            ];
            
            this.historico = [
                {
                    id: 1,
                    data: '2024-03-15T10:00:00',
                    plano: 'Compra Mensal PETR4',
                    ativo: 'PETR4',
                    quantidade: 18,
                    preco: 27.80,
                    total: 500.40,
                    status: 'executado'
                },
                {
                    id: 2,
                    data: '2024-03-14T10:30:00',
                    plano: 'DCA Semanal ITUB4',
                    ativo: 'ITUB4',
                    quantidade: 9,
                    preco: 22.10,
                    total: 198.90,
                    status: 'executado'
                },
                {
                    id: 3,
                    data: '2024-03-13T10:15:00',
                    plano: 'Compra Mensal PETR4',
                    ativo: 'PETR4',
                    quantidade: 17,
                    preco: 29.40,
                    total: 499.80,
                    status: 'executado'
                }
            ];
            
            this.calcularResumo();
        },
        
        // Calcular resumo
        calcularResumo() {
            const planosAtivos = this.planos.filter(p => p.status === 'ativo');
            const totalInvestido = this.planos.reduce((sum, p) => sum + p.total_investido, 0);
            
            // Simular compras do mês
            const agora = new Date();
            const inicioMes = new Date(agora.getFullYear(), agora.getMonth(), 1);
            const comprasMes = this.historico.filter(h => 
                new Date(h.data) >= inicioMes && h.status === 'executado'
            ).length;
            
            // Calcular próxima execução
            const proximasExecucoes = planosAtivos.filter(p => 
                new Date(p.proxima_execucao) > agora
            ).length;
            
            const proximaExecucao = planosAtivos
                .filter(p => new Date(p.proxima_execucao) > agora)
                .sort((a, b) => new Date(a.proxima_execucao) - new Date(b.proxima_execucao))[0];
            
            this.resumo = {
                planos_ativos: planosAtivos.length,
                total_planos: this.planos.length,
                compras_mes: comprasMes,
                total_investido: totalInvestido,
                media_investimento: this.planos.length > 0 ? totalInvestido / this.planos.length : 0,
                economia_percentual: 15.5,
                economia_total: totalInvestido * 0.155,
                proximas_execucoes: proximasExecucoes,
                proxima_data: proximaExecucao ? this.formatDate(proximaExecucao.proxima_execucao) : '18/03',
                proximo_horario: '10:00'
            };
        },
        
        // Set data início padrão
        setDataInicioPadrao() {
            const hoje = new Date();
            this.novoPlano.data_inicio = hoje.toISOString().split('T')[0];
        },
        
        // Atualizar campos baseado no tipo
        atualizarCamposTipo() {
            if (this.novoPlano.tipo === 'quantidade_fixa') {
                this.novoPlano.valor = 0;
            } else {
                this.novoPlano.quantidade = 0;
            }
        },
        
        // Criar plano
        async criarPlano() {
            if (!this.novoPlano.nome || !this.novoPlano.ativo || !this.novoPlano.data_inicio) {
                alert('Preencha todos os campos obrigatórios');
                return;
            }
            
            if (this.novoPlano.tipo === 'valor_fixo' && !this.novoPlano.valor) {
                alert('Informe o valor por compra');
                return;
            }
            
            if (this.novoPlano.tipo === 'quantidade_fixa' && !this.novoPlano.quantidade) {
                alert('Informe a quantidade por compra');
                return;
            }
            
            try {
                const response = await fetch('/api/planos-compra', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(this.novoPlano)
                });
                
                if (response.ok) {
                    const data = await response.json();
                    this.planos.push(data.data);
                    this.calcularResumo();
                    this.abaAtiva = 'planos';
                    this.resetForm();
                } else {
                    alert('Erro ao criar plano');
                }
            } catch (error) {
                console.error('Erro ao criar plano:', error);
                // Mock: adicionar localmente
                const novo = {
                    id: Date.now(),
                    ...this.novoPlano,
                    status: 'ativo',
                    proxima_execucao: this.calcularProximaExecucao(),
                    total_investido: 0
                };
                this.planos.push(novo);
                this.calcularResumo();
                this.abaAtiva = 'planos';
                this.resetForm();
            }
        },
        
        // Calcular próxima execução
        calcularProximaExecucao() {
            const data = new Date(this.novoPlano.data_inicio);
            
            switch (this.novoPlano.frequencia) {
                case 'diario':
                    data.setDate(data.getDate() + 1);
                    break;
                case 'semanal':
                    data.setDate(data.getDate() + 7);
                    break;
                case 'quinzenal':
                    data.setDate(data.getDate() + 15);
                    break;
                case 'mensal':
                    data.setMonth(data.getMonth() + 1);
                    break;
            }
            
            return data.toISOString().split('T')[0];
        },
        
        // Reset formulário
        resetForm() {
            this.novoPlano = {
                nome: '',
                ativo: '',
                tipo: 'valor_fixo',
                valor: 0,
                quantidade: 0,
                frequencia: 'mensal',
                data_inicio: ''
            };
            this.setDataInicioPadrao();
        },
        
        // Pausar/ativar plano
        async pausarPlano(plano) {
            const novoStatus = plano.status === 'ativo' ? 'pausado' : 'ativo';
            
            try {
                const response = await fetch(`/api/planos-compra/${plano.id}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ status: novoStatus })
                });
                
                if (response.ok) {
                    plano.status = novoStatus;
                    this.calcularResumo();
                }
            } catch (error) {
                console.error('Erro ao atualizar plano:', error);
                // Mock: atualizar localmente
                plano.status = novoStatus;
                this.calcularResumo();
            }
        },
        
        // Editar plano
        editarPlano(plano) {
            // Implementar modal de edição
            console.log('Editar plano:', plano);
        },
        
        // Excluir plano
        async excluirPlano(plano) {
            if (!confirm('Deseja excluir este plano?')) {
                return;
            }
            
            try {
                const response = await fetch(`/api/planos-compra/${plano.id}`, {
                    method: 'DELETE'
                });
                
                if (response.ok) {
                    const index = this.planos.findIndex(p => p.id === plano.id);
                    if (index > -1) {
                        this.planos.splice(index, 1);
                        this.calcularResumo();
                    }
                }
            } catch (error) {
                console.error('Erro ao excluir plano:', error);
                // Mock: remover localmente
                const index = this.planos.findIndex(p => p.id === plano.id);
                if (index > -1) {
                    this.planos.splice(index, 1);
                    this.calcularResumo();
                }
            }
        },
        
        // Simular plano
        simularPlano() {
            alert('Função de simulação em desenvolvimento...');
        },
        
        // Calcular investimento mensal
        getInvestimentoMensal() {
            if (!this.novoPlano.valor) return 0;
            
            let multiplicador = 1;
            switch (this.novoPlano.frequencia) {
                case 'diario':
                    multiplicador = 22; // dias úteis
                    break;
                case 'semanal':
                    multiplicador = 4;
                    break;
                case 'quinzenal':
                    multiplicador = 2;
                    break;
                case 'mensal':
                    multiplicador = 1;
                    break;
            }
            
            return this.novoPlano.valor * multiplicador;
        },
        
        // Calcular investimento anual
        getInvestimentoAnual() {
            return this.getInvestimentoMensal() * 12;
        },
        
        // Get taxa de sucesso (mock)
        getTaxaSucesso() {
            // Simulação baseada no tipo e frequência
            let base = 85;
            
            if (this.novoPlano.tipo === 'smart') {
                base += 10;
            }
            
            if (this.novoPlano.frequencia === 'mensal') {
                base += 5;
            } else if (this.novoPlano.frequencia === 'diario') {
                base -= 5;
            }
            
            return Math.min(99, base);
        },
        
        // Inicializar gráfico de performance
        initPerformanceChart() {
            const ctx = document.getElementById('performance-chart');
            if (!ctx) return;
            
            // Mock dados de performance
            const labels = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'];
            const planosData = [1000, 1200, 1350, 1500, 1750, 2000];
            const ibovData = [1000, 1050, 1100, 1080, 1150, 1200];
            
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Meus Planos',
                            data: planosData,
                            borderColor: '#3B82F6',
                            backgroundColor: 'rgba(59, 130, 246, 0.1)',
                            borderWidth: 3,
                            fill: true,
                            tension: 0.4
                        },
                        {
                            label: 'IBOV',
                            data: ibovData,
                            borderColor: '#EF4444',
                            backgroundColor: 'rgba(239, 68, 68, 0.1)',
                            borderWidth: 3,
                            fill: true,
                            tension: 0.4
                        }
                    ]
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
                            beginAtZero: true,
                            ticks: {
                                callback: (value) => this.formatCurrency(value, this.currency, false)
                            }
                        }
                    }
                }
            });
        },
        
        // Watch mudança de aba
        $watch('abaAtiva', (value) => {
            if (value === 'ai-insights') {
                this.$nextTick(() => {
                    this.initPerformanceChart();
                });
            }
        }),
        
        // Handle mudança de moeda
        handleCurrencyChange(detail) {
            this.currency = detail.currency;
            this.exchangeRate = detail.rate;
            localStorage.setItem('preferredCurrency', this.currency);
        },
        
        // Utilitários
        formatDate(dateStr) {
            if (!dateStr) return '';
            const date = new Date(dateStr);
            return date.toLocaleDateString('pt-BR', { 
                day: '2-digit', 
                month: '2-digit' 
            });
        },
        
        formatDateTime(dateStr) {
            if (!dateStr) return '';
            const date = new Date(dateStr);
            return date.toLocaleDateString('pt-BR', { 
                day: '2-digit', 
                month: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
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
