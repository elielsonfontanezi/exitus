/**
 * Fluxo de Caixa - JavaScript
 * Sistema de acompanhamento de entradas, saídas e saldo
 */

// Função Alpine.js para gerenciar dados de fluxo de caixa
function fluxoCaixaData() {
    return {
        currency: localStorage.getItem('preferredCurrency') || 'BRL',
        exchangeRate: 5.00,
        loading: true,
        periodo: '30d',
        tipoMovimento: 'todos',
        categoria: 'todas',
        chartType: 'line',
        
        // Resumo
        resumo: {
            saldo_atual: 0,
            ultima_atualizacao: '',
            entradas_mes: 0,
            entradas_quantidade: 0,
            entradas_media: 0,
            saidas_mes: 0,
            saidas_quantidade: 0,
            saidas_media: 0,
            saldo_liquido: 0,
            saldo_liquido_percentual: 0
        },
        
        // Movimentações
        movimentos: [],
        
        // Inicialização
        init() {
            this.carregarDados();
            this.initCharts();
        },
        
        // Carregar dados
        async carregarDados() {
            this.loading = true;
            
            try {
                // Carregar movimentações
                const movimentosResponse = await fetch(`/api/movimentacoes?periodo=${this.periodo}`);
                if (movimentosResponse.ok) {
                    const movimentosData = await movimentosResponse.json();
                    this.processarDados(movimentosData.data || []);
                }
                
                // Carregar saldo
                const saldoResponse = await fetch('/api/saldo');
                if (saldoResponse.ok) {
                    const saldoData = await saldoResponse.json();
                    this.resumo.saldo_atual = saldoData.data.valor || 0;
                    this.resumo.ultima_atualizacao = this.formatDateTime(saldoData.data_atualizado);
                }
                
                // Inicializar gráficos após carregar dados
                this.$nextTick(() => {
                    this.initCharts();
                });
                
            } catch (error) {
                console.error('Erro ao carregar dados de fluxo de caixa:', error);
                // Carregar dados mock em caso de erro
                this.loadMockData();
            } finally {
                this.loading = false;
            }
        },
        
        // Processar dados
        processarDados(dados) {
            this.movimentos = dados.map(mov => ({
                id: mov.id,
                data: mov.data,
                descricao: mov.descricao || mov.tipomovimentacao,
                categoria: this.getCategoria(mov.tipomovimentacao),
                conta: mov.corretora?.nome || 'Conta Principal',
                valor: parseFloat(mov.valor),
                tipo: this.getTipoMovimento(mov.tipomovimentacao),
                detalhes: mov.observacao
            }));
            
            // Ordenar por data (mais recente primeiro)
            this.movimentos.sort((a, b) => new Date(b.data) - new Date(a.data));
            
            // Calcular resumo
            this.calcularResumo();
        },
        
        // Calcular resumo
        calcularResumo() {
            const agora = new Date();
            const mesAtual = agora.getMonth();
            const anoAtual = agora.getFullYear();
            
            // Filtrar movimentos do mês atual
            const movimentosMes = this.movimentos.filter(mov => {
                const data = new Date(mov.data);
                return data.getMonth() === mesAtual && data.getFullYear() === anoAtual;
            });
            
            const entradas = movimentosMes.filter(m => m.tipo === 'entrada');
            const saidas = movimentosMes.filter(m => m.tipo === 'saida');
            
            const totalEntradas = entradas.reduce((sum, e) => sum + e.valor, 0);
            const totalSaidas = saidas.reduce((sum, s) => sum + s.valor, 0);
            const saldoLiquido = totalEntradas - totalSaidas;
            
            this.resumo = {
                ...this.resumo,
                entradas_mes: totalEntradas,
                entradas_quantidade: entradas.length,
                entradas_media: entradas.length > 0 ? totalEntradas / entradas.length : 0,
                saidas_mes: totalSaidas,
                saidas_quantidade: saidas.length,
                saidas_media: saidas.length > 0 ? totalSaidas / saidas.length : 0,
                saldo_liquido: saldoLiquido,
                saldo_liquido_percentual: totalEntradas > 0 ? (saldoLiquido / totalEntradas) * 100 : 0
            };
        },
        
        // Obter categoria do movimento
        getCategoria(tipo) {
            const categorias = {
                'deposito': 'Aporte',
                'saque': 'Resgate',
                'dividendo': 'Dividendo',
                'jcp': 'JCP',
                'taxa': 'Taxa',
                'transferencia': 'Transferência'
            };
            return categorias[tipo] || 'Outros';
        },
        
        // Obter tipo de movimento
        getTipoMovimento(tipo) {
            const entradas = ['deposito', 'dividendo', 'jcp'];
            return entradas.includes(tipo) ? 'entrada' : 'saida';
        },
        
        // Carregar dados mock
        loadMockData() {
            const mockMovimentos = [
                {
                    id: 1,
                    data: '2024-03-15T10:30:00',
                    tipomovimentacao: 'dividendo',
                    descricao: 'Dividendo PETR4',
                    valor: '1500.00',
                    corretora: { nome: 'XP Investimentos' },
                    observacao: 'Pagamento de dividendos Mar/2024'
                },
                {
                    id: 2,
                    data: '2024-03-14T14:20:00',
                    tipomovimentacao: 'deposito',
                    descricao: 'Aporte',
                    valor: '5000.00',
                    corretora: { nome: 'Nu Invest' }
                },
                {
                    id: 3,
                    data: '2024-03-13T09:15:00',
                    tipomovimentacao: 'taxa',
                    descricao: 'Taxa de Corretagem',
                    valor: '25.50',
                    corretora: { nome: 'XP Investimentos' }
                },
                {
                    id: 4,
                    data: '2024-03-12T16:45:00',
                    tipomovimentacao: 'saque',
                    descricao: 'Resgate parcial',
                    valor: '2000.00',
                    corretora: { nome: 'Rico Investimentos' }
                },
                {
                    id: 5,
                    data: '2024-03-10T11:00:00',
                    tipomovimentacao: 'jcp',
                    descricao: 'JCP ITUB4',
                    valor: '800.00',
                    corretora: { nome: 'XP Investimentos' }
                }
            ];
            
            this.processarDados(mockMovimentos);
            this.resumo.saldo_atual = 25000;
            this.resumo.ultima_atualizacao = this.formatDateTime(new Date());
        },
        
        // Inicializar gráficos
        initCharts() {
            this.initFluxoCaixaChart();
        },
        
        // Gráfico de fluxo de caixa
        initFluxoCaixaChart() {
            const ctx = document.getElementById('fluxo-caixa-chart');
            if (!ctx) return;
            
            // Agrupar dados por dia
            const dadosAgrupados = this.agruparPorDia();
            
            const labels = dadosAgrupados.map(d => d.data);
            const entradas = dadosAgrupados.map(d => d.entradas);
            const saidas = dadosAgrupados.map(d => d.saidas);
            const saldo = dadosAgrupados.map(d => d.saldo);
            
            new Chart(ctx, {
                type: this.chartType,
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Entradas',
                            data: entradas,
                            borderColor: 'rgba(16, 185, 129, 1)',
                            backgroundColor: 'rgba(16, 185, 129, 0.1)',
                            borderWidth: 3,
                            fill: this.chartType === 'line',
                            tension: 0.4
                        },
                        {
                            label: 'Saídas',
                            data: saidas,
                            borderColor: 'rgba(239, 68, 68, 1)',
                            backgroundColor: 'rgba(239, 68, 68, 0.1)',
                            borderWidth: 3,
                            fill: this.chartType === 'line',
                            tension: 0.4
                        },
                        {
                            label: 'Saldo Acumulado',
                            data: saldo,
                            borderColor: 'rgba(59, 130, 246, 1)',
                            backgroundColor: 'rgba(59, 130, 246, 0.1)',
                            borderWidth: 3,
                            fill: false,
                            tension: 0.4,
                            borderDash: [5, 5]
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
        
        // Agrupar movimentos por dia
        agruparPorDia() {
            const agrupado = {};
            
            this.movimentos.forEach(mov => {
                const data = new Date(mov.data).toLocaleDateString('pt-BR');
                
                if (!agrupado[data]) {
                    agrupado[data] = {
                        data: data,
                        entradas: 0,
                        saidas: 0,
                        saldo: 0
                    };
                }
                
                if (mov.tipo === 'entrada') {
                    agrupado[data].entradas += mov.valor;
                } else {
                    agrupado[data].saidas += mov.valor;
                }
            });
            
            // Calcular saldo acumulado
            let saldoAcumulado = 0;
            Object.values(agrupado).forEach(dia => {
                saldoAcumulado += dia.entradas - dia.saidas;
                dia.saldo = saldoAcumulado;
            });
            
            return Object.values(agrupado).slice(-30); // Últimos 30 dias
        },
        
        // Mudar tipo de gráfico
        changeChartType(type) {
            this.chartType = type;
            this.initFluxoCaixaChart();
        },
        
        // Filtrar movimentos
        filtrarMovimentos() {
            // A reatividade do Alpine.js vai atualizar automaticamente
        },
        
        // Movimentos filtrados
        get filteredMovimentos() {
            let filtered = this.movimentos;
            
            // Filtrar por tipo
            if (this.tipoMovimento !== 'todos') {
                filtered = filtered.filter(m => m.tipo === this.tipoMovimento);
            }
            
            // Filtrar por categoria
            if (this.categoria !== 'todas') {
                filtered = filtered.filter(m => m.categoria.toLowerCase() === this.categoria.toLowerCase());
            }
            
            return filtered;
        },
        
        // Exportar dados
        exportarDados() {
            // Implementar exportação CSV
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
        
        // Utilitários
        get mesAtual() {
            const meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
                          'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];
            const agora = new Date();
            return meses[agora.getMonth()];
        },
        
        getMesNome(mes) {
            const meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                          'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
            return meses[parseInt(mes) - 1] || '';
        },
        
        formatDate(dateStr) {
            const date = new Date(dateStr);
            return date.toLocaleDateString('pt-BR', { 
                day: '2-digit', 
                month: '2-digit', 
                year: 'numeric' 
            });
        },
        
        formatTime(dateStr) {
            const date = new Date(dateStr);
            return date.toLocaleTimeString('pt-BR', { 
                hour: '2-digit', 
                minute: '2-digit' 
            });
        },
        
        formatDateTime(date) {
            if (typeof date === 'string') {
                date = new Date(date);
            }
            return date.toLocaleDateString('pt-BR', { 
                day: '2-digit', 
                month: '2-digit', 
                year: 'numeric',
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
