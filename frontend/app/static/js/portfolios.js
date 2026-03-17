/**
 * Portfolios - JavaScript (Redesign)
 * Gestão de carteiras de investimento com design moderno
 */

// Função Alpine.js para gerenciar portfolios
function portfoliosData() {
    return {
        currency: localStorage.getItem('preferredCurrency') || 'BRL',
        exchangeRate: 5.00,
        loading: true,
        vista: 'grid',
        showModal: false,
        
        // Dados
        resumo: {
            total_carteiras: 0,
            carteiras_ativas: 0,
            saldo_brl: 0,
            variacao_brl: 0,
            saldo_usd: 0,
            variacao_usd: 0,
            patrimonio_total: 0,
            total_investido: 0
        },
        
        carteiras: [],
        
        // Nova carteira
        novaCarteira: {
            nome: '',
            corretora: '',
            tipo: '',
            mercado: ''
        },
        
        // Inicialização
        init() {
            this.carregarDados();
        },
        
        // Carregar dados
        async carregarDados() {
            this.loading = true;
            
            try {
                // Carregar carteiras
                const response = await fetch('/api/carteiras');
                if (response.ok) {
                    const data = await response.json();
                    this.carteiras = data.data || [];
                }
                
                // Calcular resumo
                this.calcularResumo();
                
            } catch (error) {
                console.error('Erro ao carregar carteiras:', error);
                this.loadMockData();
            } finally {
                this.loading = false;
            }
        },
        
        // Carregar dados mock
        loadMockData() {
            this.carteiras = [
                {
                    id: 1,
                    nome: 'Carteira Principal',
                    corretora: 'XP Investimentos',
                    tipo_conta: 'Normal',
                    tipo: 'normal',
                    mercado: 'brasil',
                    moeda: 'BRL',
                    saldo: 125000.00,
                    variacao: 12.5,
                    quantidade_ativos: 15,
                    status: 'ativa'
                },
                {
                    id: 2,
                    nome: 'Ações EUA',
                    corretora: 'NuInvest',
                    tipo_conta: 'Normal',
                    tipo: 'normal',
                    mercado: 'usa',
                    moeda: 'USD',
                    saldo: 45000.00,
                    variacao: -3.2,
                    quantidade_ativos: 8,
                    status: 'ativa'
                },
                {
                    id: 3,
                    nome: 'Day Trade',
                    corretora: 'Clear',
                    tipo_conta: 'Day Trade',
                    tipo: 'day_trade',
                    mercado: 'brasil',
                    moeda: 'BRL',
                    saldo: 15000.00,
                    variacao: 8.7,
                    quantidade_ativos: 5,
                    status: 'ativa'
                },
                {
                    id: 4,
                    nome: 'Previdência Privada',
                    corretora: 'BTG Pactual',
                    tipo_conta: 'Normal',
                    tipo: 'normal',
                    mercado: 'brasil',
                    moeda: 'BRL',
                    saldo: 80000.00,
                    variacao: 0.0,
                    quantidade_ativos: 10,
                    status: 'inativa'
                }
            ];
            
            this.calcularResumo();
        },
        
        // Calcular resumo
        calcularResumo() {
            const carteirasAtivas = this.carteiras.filter(c => c.status === 'ativa');
            const saldoBRL = this.carteiras
                .filter(c => c.mercado === 'brasil')
                .reduce((sum, c) => sum + c.saldo, 0);
            const saldoUSD = this.carteiras
                .filter(c => c.mercado === 'usa')
                .reduce((sum, c) => sum + c.saldo, 0);
            
            // Calcular variações
            const variacaoBRL = this.carteiras
                .filter(c => c.mercado === 'brasil')
                .reduce((sum, c) => sum + (c.saldo * c.variacao / 100), 0) / (saldoBRL || 1) * 100;
            const variacaoUSD = this.carteiras
                .filter(c => c.mercado === 'usa')
                .reduce((sum, c) => sum + (c.saldo * c.variacao / 100), 0) / (saldoUSD || 1) * 100;
            
            // Patrimônio total em BRL
            const patrimonioBRL = saldoBRL + (saldoUSD * this.exchangeRate);
            const totalInvestido = patrimonioBRL / 1.15; // Simulação de 15% de ganho médio
            
            this.resumo = {
                total_carteiras: this.carteiras.length,
                carteiras_ativas: carteirasAtivas.length,
                saldo_brl: saldoBRL,
                variacao_brl: variacaoBRL,
                saldo_usd: saldoUSD,
                variacao_usd: variacaoUSD,
                patrimonio_total: patrimonioBRL,
                total_investido: totalInvestido
            };
        },
        
        // Criar carteira
        async criarCarteira() {
            if (!this.novaCarteira.nome || !this.novaCarteira.corretora || !this.novaCarteira.tipo || !this.novaCarteira.mercado) {
                alert('Preencha todos os campos');
                return;
            }
            
            try {
                const response = await fetch('/api/carteiras', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(this.novaCarteira)
                });
                
                if (response.ok) {
                    const data = await response.json();
                    this.carteiras.push(data.data);
                    this.calcularResumo();
                    this.showModal = false;
                    this.resetForm();
                } else {
                    alert('Erro ao criar carteira');
                }
            } catch (error) {
                console.error('Erro ao criar carteira:', error);
                // Mock: adicionar localmente
                const nova = {
                    id: Date.now(),
                    ...this.novaCarteira,
                    tipo_conta: this.novaCarteira.tipo === 'day_trade' ? 'Day Trade' : 'Normal',
                    moeda: this.novaCarteira.mercado === 'usa' ? 'USD' : 'BRL',
                    saldo: 0,
                    variacao: 0,
                    quantidade_ativos: 0,
                    status: 'ativa'
                };
                this.carteiras.push(nova);
                this.calcularResumo();
                this.showModal = false;
                this.resetForm();
            }
        },
        
        // Reset formulário
        resetForm() {
            this.novaCarteira = {
                nome: '',
                corretora: '',
                tipo: '',
                mercado: ''
            };
        },
        
        // Ver detalhes
        verDetalhes(carteira) {
            // Implementar navegação para detalhes da carteira
            console.log('Ver detalhes:', carteira);
            alert(`Detalhes da carteira: ${carteira.nome}`);
        },
        
        // Editar carteira
        editarCarteira(carteira) {
            // Implementar modal de edição
            console.log('Editar carteira:', carteira);
            alert(`Editar carteira: ${carteira.nome}`);
        },
        
        // Excluir carteira
        async excluirCarteira(carteira) {
            if (!confirm(`Deseja excluir a carteira "${carteira.nome}"?`)) {
                return;
            }
            
            try {
                const response = await fetch(`/api/carteiras/${carteira.id}`, {
                    method: 'DELETE'
                });
                
                if (response.ok) {
                    const index = this.carteiras.findIndex(c => c.id === carteira.id);
                    if (index > -1) {
                        this.carteiras.splice(index, 1);
                        this.calcularResumo();
                    }
                } else {
                    alert('Erro ao excluir carteira');
                }
            } catch (error) {
                console.error('Erro ao excluir carteira:', error);
                // Mock: remover localmente
                const index = this.carteiras.findIndex(c => c.id === carteira.id);
                if (index > -1) {
                    this.carteiras.splice(index, 1);
                    this.calcularResumo();
                }
            }
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
        }
    }
}
