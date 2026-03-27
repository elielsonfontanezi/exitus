/**
 * Imposto de Renda - JavaScript
 * Sistema de calculadora, DARFs e compensação de prejuízos
 */

// Função Alpine.js para gerenciar dados de IR
function impostoRendaData() {
    return {
        currency: localStorage.getItem('preferredCurrency') || 'BRL',
        exchangeRate: 5.00,
        loading: true,
        abaAtiva: 'calculadora',
        anoRelatorio: '2024',
        
        // Resumo
        resumo: {
            ir_acumulado: 0,
            ir_acumulado_qtd: 0,
            proximo_vencimento: '',
            prejuizos_acumulados: 0,
            prejuizos_economia: 0,
            ir_pago_ano: 0,
            ir_pago_qtd: 0,
            ir_pago_medio: 0,
            aliquota_efetiva: 0,
            aliquota_oficial: 15
        },
        
        // Calculadora
        calculadora: {
            ativo: '',
            quantidade: 0,
            preco_venda: 0,
            preco_compra: 0,
            valor_total_venda: 0,
            custo_total: 0,
            lucro_prejuizo: 0,
            ir_devido: 0,
            prejuizo_compensado: 0,
            ir_a_pagar: 0
        },
        
        // Dados
        ativos: [],
        darfs: [],
        prejuizos: [],
        relatorio: {
            lucros: 0,
            prejuizos_compensados: 0,
            base_calculo: 0,
            ir_total: 0
        },
        
        // Inicialização
        init() {
            this.carregarDados();
            this.initCharts();
        },
        
        // Carregar dados
        async carregarDados() {
            this.loading = true;
            
            try {
                // Carregar posições para calculadora
                const positionsResponse = await fetch('/api/posicoes');
                if (positionsResponse.ok) {
                    const positionsData = await positionsResponse.json();
                    this.ativos = positionsData.data.map(p => ({
                        ticker: p.ativo.ticker,
                        nome: p.ativo.nome,
                        preco_medio: p.preco_medio,
                        quantidade: p.quantidade
                    }));
                }
                
                // Carregar DARFs
                const darfsResponse = await fetch('/api/darfs');
                if (darfsResponse.ok) {
                    const darfsData = await darfsResponse.json();
                    this.darfs = darfsData.data || [];
                }
                
                // Carregar prejuízos
                const prejuizosResponse = await fetch('/api/prejuizos-acumulados');
                if (prejuizosResponse.ok) {
                    const prejuizosData = await prejuizosResponse.json();
                    this.prejuizos = prejuizosData.data || [];
                }
                
                // Carregar relatório
                this.carregarRelatorio();
                
                // Calcular resumo
                this.calcularResumo();
                
                // Inicializar gráficos após carregar dados
                this.$nextTick(() => {
                    this.initCharts();
                });
                
            } catch (error) {
                console.error('Erro ao carregar dados de IR:', error);
                // Carregar dados mock em caso de erro
                this.loadMockData();
            } finally {
                this.loading = false;
            }
        },
        
        // Calcular resumo
        calcularResumo() {
            // DARFs acumulados (não pagos)
            const darfsAcumulados = this.darfs.filter(d => d.status !== 'PAGO');
            const irAcumulado = darfsAcumulados.reduce((sum, d) => sum + d.valor, 0);
            
            // Prejuízos acumulados
            const prejuizosAcumulados = this.prejuizos.reduce((sum, p) => sum + p.disponivel, 0);
            const economiaPrejuizos = prejuizosAcumulados * 0.15; // 15% de economia
            
            // IR pago no ano
            const agora = new Date();
            const darfsPagosAno = this.darfs.filter(d => 
                d.status === 'PAGO' && 
                new Date(d.data_pagamento).getFullYear() === agora.getFullYear()
            );
            const irPagoAno = darfsPagosAno.reduce((sum, d) => sum + d.valor, 0);
            
            // Próximo vencimento
            const proximosVencimentos = darfsAcumulados
                .filter(d => d.status === 'ABERTO')
                .sort((a, b) => new Date(a.vencimento) - new Date(b.vencimento));
            
            this.resumo = {
                ir_acumulado: irAcumulado,
                ir_acumulado_qtd: darfsAcumulados.length,
                proximo_vencimento: proximosVencimentos.length > 0 ? 
                    this.formatDate(proximosVencimentos[0].vencimento) : '',
                prejuizos_acumulados: prejuizosAcumulados,
                prejuizos_economia: economiaPrejuizos,
                ir_pago_ano: irPagoAno,
                ir_pago_qtd: darfsPagosAno.length,
                ir_pago_medio: darfsPagosAno.length > 0 ? irPagoAno / darfsPagosAno.length : 0,
                aliquota_efetiva: this.relatorio.lucros > 0 ? 
                    (this.relatorio.ir_total / this.relatorio.lucros) * 100 : 0,
                aliquota_oficial: 15
            };
        },
        
        // Carregar relatório
        async carregarRelatorio() {
            try {
                const response = await fetch(`/api/relatorio-ir?ano=${this.anoRelatorio}`);
                if (response.ok) {
                    const data = await response.json();
                    this.relatorio = data.data || this.getMockRelatorio();
                }
            } catch (error) {
                this.relatorio = this.getMockRelatorio();
            }
        },
        
        // Mock relatório
        getMockRelatorio() {
            return {
                lucros: 50000,
                prejuizos_compensados: 8000,
                base_calculo: 42000,
                ir_total: 6300
            };
        },
        
        // Calcular IR
        calcularIR() {
            const { ativo, quantidade, preco_venda, preco_compra } = this.calculadora;
            
            if (!quantidade || !preco_venda || !preco_compra) {
                this.limparCalculo();
                return;
            }
            
            const valorVenda = quantidade * preco_venda;
            const custo = quantidade * preco_compra;
            const lucroPrejuizo = valorVenda - custo;
            
            let irDevido = 0;
            let prejuizoCompensado = 0;
            
            if (lucroPrejuizo > 0) {
                // Simular compensação de prejuízos
                const prejuizosDisponiveis = this.resumo.prejuizos_acumulados;
                prejuizoCompensado = Math.min(lucroPrejuizo, prejuizosDisponiveis);
                const baseCalculo = lucroPrejuizo - prejuizoCompensado;
                irDevido = baseCalculo * 0.15; // 15%
            }
            
            this.calculadora = {
                ...this.calculadora,
                valor_total_venda: valorVenda,
                custo_total: custo,
                lucro_prejuizo: lucroPrejuizo,
                ir_devido: irDevido,
                prejuizo_compensado: prejuizoCompensado,
                ir_a_pagar: irDevido
            };
        },
        
        // Limpar cálculo
        limparCalculo() {
            this.calculadora = {
                ...this.calculadora,
                valor_total_venda: 0,
                custo_total: 0,
                lucro_prejuizo: 0,
                ir_devido: 0,
                prejuizo_compensado: 0,
                ir_a_pagar: 0
            };
        },
        
        // Gerar DARF
        gerarDARF() {
            // Implementar geração de DARF
            alert('Função de geração de DARF em desenvolvimento...');
        },
        
        // Visualizar DARF
        visualizarDARF(darf) {
            // Implementar visualização
            console.log('Visualizar DARF:', darf);
        },
        
        // Baixar DARF
        baixarDARF(darf) {
            // Implementar download
            console.log('Baixar DARF:', darf);
        },
        
        // Exportar relatório
        exportarRelatorio() {
            // Implementar exportação
            alert('Função de exportação em desenvolvimento...');
        },
        
        // Carregar dados mock
        loadMockData() {
            // Mock ativos
            this.ativos = [
                { ticker: 'PETR4', nome: 'Petrobras PN', preco_medio: 28.50, quantidade: 300 },
                { ticker: 'VALE3', nome: 'Vale ON', preco_medio: 65.20, quantidade: 200 },
                { ticker: 'ITUB4', nome: 'Itaú Unibanco PN', preco_medio: 22.80, quantidade: 400 }
            ];
            
            // Mock DARFs
            this.darfs = [
                {
                    id: 1,
                    codigo: '6015',
                    periodo: '03/2024',
                    valor: 450.00,
                    vencimento: '2024-04-30',
                    status: 'ABERTO'
                },
                {
                    id: 2,
                    codigo: '6015',
                    periodo: '02/2024',
                    valor: 320.50,
                    vencimento: '2024-03-31',
                    status: 'PAGO'
                }
            ];
            
            // Mock prejuízos
            this.prejuizos = [
                {
                    ano: 2024,
                    mes: 'Janeiro',
                    valor: 5000,
                    disponivel: 3000,
                    ativos: 3
                },
                {
                    ano: 2023,
                    mes: 'Dezembro',
                    valor: 2000,
                    disponivel: 1500,
                    ativos: 2
                }
            ];
            
            this.relatorio = this.getMockRelatorio();
            this.calcularResumo();
        },
        
        // Inicializar gráficos
        initCharts() {
            this.initPrejuizosChart();
            this.initRelatorioChart();
        },
        
        // Gráfico de prejuízos
        initPrejuizosChart() {
            const ctx = document.getElementById('prejuizos-chart');
            if (!ctx) return;
            
            const labels = this.prejuizos.map(p => `${p.mes}/${p.ano}`);
            const valores = this.prejuizos.map(p => p.valor);
            const disponiveis = this.prejuizos.map(p => p.disponivel);
            
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Prejuízo Total',
                            data: valores,
                            backgroundColor: 'rgba(239, 68, 68, 0.8)',
                            borderColor: 'rgba(239, 68, 68, 1)',
                            borderWidth: 2
                        },
                        {
                            label: 'Disponível',
                            data: disponiveis,
                            backgroundColor: 'rgba(16, 185, 129, 0.8)',
                            borderColor: 'rgba(16, 185, 129, 1)',
                            borderWidth: 2
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
        
        // Gráfico de relatório
        initRelatorioChart() {
            const ctx = document.getElementById('relatorio-chart');
            if (!ctx) return;
            
            // Mock dados mensais
            const meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
            const lucros = meses.map(() => Math.random() * 10000 + 2000);
            const ir = lucros.map(l => l * 0.15);
            
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: meses,
                    datasets: [
                        {
                            label: 'Lucros',
                            data: lucros,
                            borderColor: 'rgba(16, 185, 129, 1)',
                            backgroundColor: 'rgba(16, 185, 129, 0.1)',
                            borderWidth: 3,
                            fill: true,
                            tension: 0.4
                        },
                        {
                            label: 'IR Pago',
                            data: ir,
                            borderColor: 'rgba(239, 68, 68, 1)',
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
        
        // Handle mudança de moeda
        handleCurrencyChange(detail) {
            this.currency = detail.currency;
            this.exchangeRate = detail.rate;
            localStorage.setItem('preferredCurrency', this.currency);
            
            // Atualizar gráficos
            this.initCharts();
        },
        
        // Utilitários
        get anoAtual() {
            return new Date().getFullYear();
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
