/**
 * Transactions - JavaScript (Redesign)
 * Histórico de transações com filtros avançados e exportação
 */

// Função Alpine.js para gerenciar transações
function transactionsData() {
    return {
        currency: localStorage.getItem('preferredCurrency') || 'BRL',
        exchangeRate: 5.00,
        loading: true,
        showModal: false,
        paginaAtual: 1,
        itensPorPagina: 20,
        
        // Dados
        resumo: {
            total_transacoes: 0,
            transacoes_mes: 0,
            total_compras: 0,
            total_vendas: 0,
            valor_compras: 0,
            valor_vendas: 0,
            volume_total: 0
        },
        
        transacoes: [],
        
        // Filtros
        filtros: {
            periodo: '',
            tipo: '',
            ativo: '',
            corretora: '',
            status: ''
        },
        
        // Nova transação
        novaTransacao: {
            tipo: '',
            ativo: '',
            quantidade: '',
            preco: '',
            data: new Date().toISOString().split('T')[0]
        },
        
        // Inicialização
        init() {
            this.carregarTransacoes();
        },
        
        // Carregar transações
        async carregarTransacoes() {
            this.loading = true;
            
            try {
                const response = await fetch('/api/transacoes');
                if (response.ok) {
                    const data = await response.json();
                    this.transacoes = data.data || [];
                }
                
                // Calcular resumo
                this.calcularResumo();
                
            } catch (error) {
                console.error('Erro ao carregar transações:', error);
                this.loadMockData();
            } finally {
                this.loading = false;
            }
        },
        
        // Carregar dados mock
        loadMockData() {
            this.transacoes = [
                {
                    id: 1,
                    data: '2024-03-15',
                    hora: '10:30',
                    ativo: { ticker: 'PETR4', nome: 'Petrobras PN' },
                    tipo: 'compra',
                    quantidade: 100,
                    preco: 27.50,
                    total: 2750.00,
                    moeda: 'BRL',
                    corretora: 'XP Investimentos',
                    status: 'executada'
                },
                {
                    id: 2,
                    data: '2024-03-14',
                    hora: '14:15',
                    ativo: { ticker: 'VALE3', nome: 'Vale ON' },
                    tipo: 'compra',
                    quantidade: 50,
                    preco: 71.80,
                    total: 3590.00,
                    moeda: 'BRL',
                    corretora: 'NuInvest',
                    status: 'executada'
                },
                {
                    id: 3,
                    data: '2024-03-13',
                    hora: '09:45',
                    ativo: { ticker: 'AAPL', nome: 'Apple Inc.' },
                    tipo: 'venda',
                    quantidade: 10,
                    preco: 178.50,
                    total: 1785.00,
                    moeda: 'USD',
                    corretora: 'Inter Investimentos',
                    status: 'executada'
                },
                {
                    id: 4,
                    data: '2024-03-12',
                    hora: '11:20',
                    ativo: { ticker: 'ITUB4', nome: 'Itaú Unibanco PN' },
                    tipo: 'compra',
                    quantidade: 200,
                    preco: 22.10,
                    total: 4420.00,
                    moeda: 'BRL',
                    corretora: 'XP Investimentos',
                    status: 'executada'
                },
                {
                    id: 5,
                    data: '2024-03-11',
                    hora: '15:30',
                    ativo: { ticker: 'WEGE3', nome: 'WEG ON' },
                    tipo: 'compra',
                    quantidade: 75,
                    preco: 35.20,
                    total: 2640.00,
                    moeda: 'BRL',
                    corretora: 'Clear',
                    status: 'pendente'
                },
                {
                    id: 6,
                    data: '2024-03-10',
                    hora: '10:00',
                    ativo: { ticker: 'B3SA3', nome: 'B3 ON' },
                    tipo: 'venda',
                    quantidade: 100,
                    preco: 12.50,
                    total: 1250.00,
                    moeda: 'BRL',
                    corretora: 'BTG Pactual',
                    status: 'cancelada'
                }
            ];
            
            this.calcularResumo();
        },
        
        // Calcular resumo
        calcularResumo() {
            const compras = this.transacoes.filter(t => t.tipo === 'compra');
            const vendas = this.transacoes.filter(t => t.tipo === 'venda');
            
            // Transações do mês
            const agora = new Date();
            const inicioMes = new Date(agora.getFullYear(), agora.getMonth(), 1);
            const transacoesMes = this.transacoes.filter(t => new Date(t.data) >= inicioMes);
            
            // Calcular valores
            const valorComprasBRL = compras
                .filter(t => t.moeda === 'BRL')
                .reduce((sum, t) => sum + t.total, 0);
            const valorComprasUSD = compras
                .filter(t => t.moeda === 'USD')
                .reduce((sum, t) => sum + t.total, 0);
            
            const valorVendasBRL = vendas
                .filter(t => t.moeda === 'BRL')
                .reduce((sum, t) => sum + t.total, 0);
            const valorVendasUSD = vendas
                .filter(t => t.moeda === 'USD')
                .reduce((sum, t) => sum + t.total, 0);
            
            // Converter tudo para BRL
            const valorComprasTotal = valorComprasBRL + (valorComprasUSD * this.exchangeRate);
            const valorVendasTotal = valorVendasBRL + (valorVendasUSD * this.exchangeRate);
            
            this.resumo = {
                total_transacoes: this.transacoes.length,
                transacoes_mes: transacoesMes.length,
                total_compras: compras.length,
                total_vendas: vendas.length,
                valor_compras: valorComprasTotal,
                valor_vendas: valorVendasTotal,
                volume_total: valorComprasTotal + valorVendasTotal
            };
        },
        
        // Computed: transações filtradas
        get transacoesFiltradas() {
            let filtradas = [...this.transacoes];
            
            // Filtrar por período
            if (this.filtros.periodo) {
                const dias = parseInt(this.filtros.periodo);
                const dataLimite = new Date();
                dataLimite.setDate(dataLimite.getDate() - dias);
                filtradas = filtradas.filter(t => new Date(t.data) >= dataLimite);
            }
            
            // Filtrar por tipo
            if (this.filtros.tipo) {
                filtradas = filtradas.filter(t => t.tipo === this.filtros.tipo);
            }
            
            // Filtrar por ativo
            if (this.filtros.ativo) {
                const busca = this.filtros.ativo.toUpperCase();
                filtradas = filtradas.filter(t => 
                    t.ativo.ticker.toUpperCase().includes(busca) ||
                    t.ativo.nome.toUpperCase().includes(busca)
                );
            }
            
            // Filtrar por corretora
            if (this.filtros.corretora) {
                filtradas = filtradas.filter(t => t.corretora === this.filtros.corretora);
            }
            
            // Filtrar por status
            if (this.filtros.status) {
                filtradas = filtradas.filter(t => t.status === this.filtros.status);
            }
            
            // Paginação
            const inicio = (this.paginaAtual - 1) * this.itensPorPagina;
            const fim = inicio + this.itensPorPagina;
            return filtradas.slice(inicio, fim);
        },
        
        // Computed: total de páginas
        get totalPaginas() {
            let filtradas = [...this.transacoes];
            
            // Aplicar mesmos filtros da computed property
            if (this.filtros.periodo) {
                const dias = parseInt(this.filtros.periodo);
                const dataLimite = new Date();
                dataLimite.setDate(dataLimite.getDate() - dias);
                filtradas = filtradas.filter(t => new Date(t.data) >= dataLimite);
            }
            
            if (this.filtros.tipo) {
                filtradas = filtradas.filter(t => t.tipo === this.filtros.tipo);
            }
            
            if (this.filtros.ativo) {
                const busca = this.filtros.ativo.toUpperCase();
                filtradas = filtradas.filter(t => 
                    t.ativo.ticker.toUpperCase().includes(busca) ||
                    t.ativo.nome.toUpperCase().includes(busca)
                );
            }
            
            if (this.filtros.corretora) {
                filtradas = filtradas.filter(t => t.corretora === this.filtros.corretora);
            }
            
            if (this.filtros.status) {
                filtradas = filtradas.filter(t => t.status === this.filtros.status);
            }
            
            return Math.ceil(filtradas.length / this.itensPorPagina);
        },
        
        // Aplicar filtros
        aplicarFiltros() {
            this.paginaAtual = 1;
        },
        
        // Limpar filtros
        limparFiltros() {
            this.filtros = {
                periodo: '',
                tipo: '',
                ativo: '',
                corretora: '',
                status: ''
            };
            this.paginaAtual = 1;
        },
        
        // Criar transação
        async criarTransacao() {
            if (!this.novaTransacao.tipo || !this.novaTransacao.ativo || !this.novaTransacao.quantidade || !this.novaTransacao.preco) {
                alert('Preencha todos os campos');
                return;
            }
            
            try {
                const response = await fetch('/api/transacoes', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        ...this.novaTransacao,
                        quantidade: parseInt(this.novaTransacao.quantidade),
                        preco: parseFloat(this.novaTransacao.preco),
                        total: parseInt(this.novaTransacao.quantidade) * parseFloat(this.novaTransacao.preco)
                    })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    this.transacoes.unshift(data.data);
                    this.calcularResumo();
                    this.showModal = false;
                    this.resetForm();
                } else {
                    alert('Erro ao criar transação');
                }
            } catch (error) {
                console.error('Erro ao criar transação:', error);
                // Mock: adicionar localmente
                const nova = {
                    id: Date.now(),
                    ...this.novaTransacao,
                    data: this.novaTransacao.data,
                    hora: new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }),
                    ativo: { ticker: this.novaTransacao.ativo, nome: `${this.novaTransacao.ativo} - Nome Completo` },
                    quantidade: parseInt(this.novaTransacao.quantidade),
                    preco: parseFloat(this.novaTransacao.preco),
                    total: parseInt(this.novaTransacao.quantidade) * parseFloat(this.novaTransacao.preco),
                    moeda: 'BRL',
                    corretora: 'XP Investimentos',
                    status: 'executada'
                };
                this.transacoes.unshift(nova);
                this.calcularResumo();
                this.showModal = false;
                this.resetForm();
            }
        },
        
        // Reset formulário
        resetForm() {
            this.novaTransacao = {
                tipo: '',
                ativo: '',
                quantidade: '',
                preco: '',
                data: new Date().toISOString().split('T')[0]
            };
        },
        
        // Ver detalhes
        verDetalhes(transacao) {
            console.log('Ver detalhes:', transacao);
            alert(`Detalhes da transação: ${transacao.ativo.ticker} - ${transacao.tipo}`);
        },
        
        // Editar transação
        editarTransacao(transacao) {
            console.log('Editar transação:', transacao);
            alert(`Editar transação: ${transacao.ativo.ticker}`);
        },
        
        // Excluir transação
        async excluirTransacao(transacao) {
            if (!confirm(`Deseja excluir esta transação de ${transacao.tipo} de ${transacao.ativo.ticker}?`)) {
                return;
            }
            
            try {
                const response = await fetch(`/api/transacoes/${transacao.id}`, {
                    method: 'DELETE'
                });
                
                if (response.ok) {
                    const index = this.transacoes.findIndex(t => t.id === transacao.id);
                    if (index > -1) {
                        this.transacoes.splice(index, 1);
                        this.calcularResumo();
                    }
                } else {
                    alert('Erro ao excluir transação');
                }
            } catch (error) {
                console.error('Erro ao excluir transação:', error);
                // Mock: remover localmente
                const index = this.transacoes.findIndex(t => t.id === transacao.id);
                if (index > -1) {
                    this.transacoes.splice(index, 1);
                    this.calcularResumo();
                }
            }
        },
        
        // Exportar CSV
        exportarCSV() {
            const headers = ['Data', 'Hora', 'Ativo', 'Tipo', 'Quantidade', 'Preço', 'Total', 'Corretora', 'Status'];
            const rows = this.transacoes.map(t => [
                t.data,
                t.hora,
                t.ativo.ticker,
                t.tipo,
                t.quantidade,
                t.preco.toFixed(2),
                t.total.toFixed(2),
                t.corretora,
                t.status
            ]);
            
            let csv = headers.join(',') + '\n';
            rows.forEach(row => {
                csv += row.join(',') + '\n';
            });
            
            const blob = new Blob([csv], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `transacoes_${new Date().toISOString().split('T')[0]}.csv`;
            a.click();
            window.URL.revokeObjectURL(url);
        },
        
        // Exportar Excel (simulação)
        exportarExcel() {
            alert('Exportação para Excel em desenvolvimento...');
        },
        
        // Obter classe CSS do status
        getStatusClass(status) {
            const classMap = {
                'executada': 'badge-success',
                'pendente': 'badge-warning',
                'cancelada': 'badge-danger'
            };
            return classMap[status] || 'badge-gray';
        },
        
        // Handle mudança de moeda
        handleCurrencyChange(detail) {
            this.currency = detail.currency;
            this.exchangeRate = detail.rate;
            localStorage.setItem('preferredCurrency', this.currency);
            this.calcularResumo();
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
        },
        
        formatDate(dateStr) {
            if (!dateStr) return '';
            const date = new Date(dateStr);
            return date.toLocaleDateString('pt-BR', { 
                day: '2-digit', 
                month: '2-digit',
                year: '2-digit'
            });
        }
    }
}
