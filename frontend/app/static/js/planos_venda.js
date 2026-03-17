/**
 * Planos de Venda Disciplinada - JavaScript
 * Sistema de stop gain e stop loss inteligentes
 */

// Função Alpine.js para gerenciar planos de venda
function planosVendaData() {
    return {
        currency: localStorage.getItem('preferredCurrency') || 'BRL',
        exchangeRate: 5.00,
        loading: true,
        abaAtiva: 'planos',
        
        // Resumo
        resumo: {
            planos_ativos: 0,
            posicoes_monitoradas: 0,
            stop_gains: 0,
            stop_losses: 0,
            lucro_protegido: 0,
            media_gains: 0,
            prejuizo_limitado: 0,
            media_losses: 0,
            execucoes_hoje: 0,
            gains_hoje: 0,
            losses_hoje: 0
        },
        
        // Dados
        planos: [],
        posicoesDisponiveis: [],
        historico: [],
        posicaoSelecionada: null,
        
        // Novo plano
        novoPlano: {
            nome: '',
            ativo: '',
            tipo: 'ambos',
            stop_gain: 20,
            stop_loss: 10,
            quantidade: 0,
            data_vencimento: ''
        },
        
        // Inicialização
        init() {
            this.carregarDados();
        },
        
        // Carregar dados
        async carregarDados() {
            this.loading = true;
            
            try {
                // Carregar planos
                const planosResponse = await fetch('/api/planos-venda');
                if (planosResponse.ok) {
                    const planosData = await planosResponse.json();
                    this.planos = planosData.data || [];
                }
                
                // Carregar posições disponíveis
                const posicoesResponse = await fetch('/api/posicoes');
                if (posicoesResponse.ok) {
                    const posicoesData = await posicoesResponse.json();
                    this.posicoesDisponiveis = posicoesData.data || [];
                }
                
                // Carregar histórico
                const historicoResponse = await fetch('/api/planos-venda/historico');
                if (historicoResponse.ok) {
                    const historicoData = await historicoResponse.json();
                    this.historico = historicoData.data || [];
                }
                
                // Calcular resumo
                this.calcularResumo();
                
            } catch (error) {
                console.error('Erro ao carregar dados de planos de venda:', error);
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
                    nome: 'Stop Gain PETR4',
                    ativo: 'PETR4',
                    tipo: 'stop_gain',
                    stop_gain: 25,
                    stop_loss: 0,
                    quantidade: 100,
                    preco_entrada: 22.50,
                    preco_atual: 27.80,
                    status: 'ativo',
                    variacao: 23.56
                },
                {
                    id: 2,
                    nome: 'Stop Loss ITUB4',
                    ativo: 'ITUB4',
                    tipo: 'stop_loss',
                    stop_gain: 0,
                    stop_loss: 15,
                    quantidade: 200,
                    preco_entrada: 25.30,
                    preco_atual: 22.10,
                    status: 'ativo',
                    variacao: -12.65
                },
                {
                    id: 3,
                    nome: 'Stop Ambos VALE3',
                    ativo: 'VALE3',
                    tipo: 'ambos',
                    stop_gain: 30,
                    stop_loss: 20,
                    quantidade: 50,
                    preco_entrada: 68.90,
                    preco_atual: 72.40,
                    status: 'pausado',
                    variacao: 5.08
                }
            ];
            
            this.posicoesDisponiveis = [
                {
                    ativo: { ticker: 'PETR4', nome: 'Petrobras PN' },
                    quantidade: 500,
                    preco_medio: 22.50,
                    preco_atual: 27.80,
                    variacao: 23.56
                },
                {
                    ativo: { ticker: 'VALE3', nome: 'Vale ON' },
                    quantidade: 200,
                    preco_medio: 68.90,
                    preco_atual: 72.40,
                    variacao: 5.08
                },
                {
                    ativo: { ticker: 'ITUB4', nome: 'Itaú Unibanco PN' },
                    quantidade: 300,
                    preco_medio: 25.30,
                    preco_atual: 22.10,
                    variacao: -12.65
                },
                {
                    ativo: { ticker: 'BBDC4', nome: 'Bradesco PN' },
                    quantidade: 150,
                    preco_medio: 18.75,
                    preco_atual: 19.20,
                    variacao: 2.40
                }
            ];
            
            this.historico = [
                {
                    id: 1,
                    data: '2024-03-15T14:30:00',
                    plano: 'Stop Gain PETR4',
                    ativo: 'PETR4',
                    quantidade: 100,
                    preco: 28.12,
                    total: 2812.00,
                    tipo: 'gain',
                    status: 'executado'
                },
                {
                    id: 2,
                    data: '2024-03-14T10:15:00',
                    plano: 'Stop Loss ITUB4',
                    ativo: 'ITUB4',
                    quantidade: 50,
                    preco: 21.50,
                    total: 1075.00,
                    tipo: 'loss',
                    status: 'executado'
                }
            ];
            
            this.calcularResumo();
        },
        
        // Calcular resumo
        calcularResumo() {
            const planosAtivos = this.planos.filter(p => p.status === 'ativo');
            const stopGains = planosAtivos.filter(p => p.stop_gain > 0);
            const stopLosses = planosAtivos.filter(p => p.stop_loss > 0);
            
            // Calcular lucro protegido e prejuízo limitado
            const lucroProtegido = stopGains.reduce((sum, p) => {
                const lucroEstimado = (p.preco_entrada * (1 + p.stop_gain / 100) - p.preco_entrada) * p.quantidade;
                return sum + lucroEstimado;
            }, 0);
            
            const prejuizoLimitado = stopLosses.reduce((sum, p) => {
                const prejuizoEstimado = (p.preco_entrada - p.preco_entrada * (1 - p.stop_loss / 100)) * p.quantidade;
                return sum + prejuizoEstimado;
            }, 0);
            
            // Execuções hoje
            const hoje = new Date();
            const inicioDia = new Date(hoje.getFullYear(), hoje.getMonth(), hoje.getDate());
            const execucoesHoje = this.historico.filter(h => 
                new Date(h.data) >= inicioDia && h.status === 'executado'
            );
            
            const gainsHoje = execucoesHoje.filter(e => e.tipo === 'gain').length;
            const lossesHoje = execucoesHoje.filter(e => e.tipo === 'loss').length;
            
            this.resumo = {
                planos_ativos: planosAtivos.length,
                posicoes_monitoradas: new Set(planosAtivos.map(p => p.ativo)).size,
                stop_gains: stopGains.length,
                stop_losses: stopLosses.length,
                lucro_protegido: lucroProtegido,
                media_gains: stopGains.length > 0 ? stopGains.reduce((sum, p) => sum + p.stop_gain, 0) / stopGains.length : 0,
                prejuizo_limitado: prejuizoLimitado,
                media_losses: stopLosses.length > 0 ? stopLosses.reduce((sum, p) => sum + p.stop_loss, 0) / stopLosses.length : 0,
                execucoes_hoje: execucoesHoje.length,
                gains_hoje: gainsHoje,
                losses_hoje: lossesHoje
            };
        },
        
        // Carregar posição selecionada
        carregarPosicao() {
            if (!this.novoPlano.ativo) {
                this.posicaoSelecionada = null;
                return;
            }
            
            const posicao = this.posicoesDisponiveis.find(p => p.ativo.ticker === this.novoPlano.ativo);
            this.posicaoSelecionada = posicao || null;
            
            if (posicao) {
                this.novoPlano.quantidade = posicao.quantidade;
            }
        },
        
        // Criar plano
        async criarPlano() {
            if (!this.novoPlano.nome || !this.novoPlano.ativo || !this.novoPlano.quantidade) {
                alert('Preencha todos os campos obrigatórios');
                return;
            }
            
            if ((this.novoPlano.tipo === 'stop_gain' || this.novoPlano.tipo === 'ambos') && !this.novoPlano.stop_gain) {
                alert('Informe o Stop Gain');
                return;
            }
            
            if ((this.novoPlano.tipo === 'stop_loss' || this.novoPlano.tipo === 'ambos') && !this.novoPlano.stop_loss) {
                alert('Informe o Stop Loss');
                return;
            }
            
            try {
                const response = await fetch('/api/planos-venda', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        ...this.novoPlano,
                        preco_entrada: this.posicaoSelecionada.preco_medio
                    })
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
                    preco_entrada: this.posicaoSelecionada.preco_medio,
                    preco_atual: this.posicaoSelecionada.preco_atual,
                    status: 'ativo',
                    variacao: this.posicaoSelecionada.variacao
                };
                this.planos.push(novo);
                this.calcularResumo();
                this.abaAtiva = 'planos';
                this.resetForm();
            }
        },
        
        // Criar plano para posição
        criarPlanoParaPosicao(posicao) {
            this.novoPlano.ativo = posicao.ativo.ticker;
            this.novoPlano.quantidade = posicao.quantidade;
            this.carregarPosicao();
            this.abaAtiva = 'novo';
        },
        
        // Reset formulário
        resetForm() {
            this.novoPlano = {
                nome: '',
                ativo: '',
                tipo: 'ambos',
                stop_gain: 20,
                stop_loss: 10,
                quantidade: 0,
                data_vencimento: ''
            };
            this.posicaoSelecionada = null;
        },
        
        // Pausar/ativar plano
        async pausarPlano(plano) {
            const novoStatus = plano.status === 'ativo' ? 'pausado' : 'ativo';
            
            try {
                const response = await fetch(`/api/planos-venda/${plano.id}`, {
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
                const response = await fetch(`/api/planos-venda/${plano.id}`, {
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
        
        // Cálculos para preview
        getValorPosicao() {
            if (!this.posicaoSelecionada) return 0;
            return this.posicaoSelecionada.quantidade * this.posicaoSelecionada.preco_medio;
        },
        
        getPrecoStopGain() {
            if (!this.posicaoSelecionada || !this.novoPlano.stop_gain) return 0;
            return this.posicaoSelecionada.preco_medio * (1 + this.novoPlano.stop_gain / 100);
        },
        
        getPrecoStopLoss() {
            if (!this.posicaoSelecionada || !this.novoPlano.stop_loss) return 0;
            return this.posicaoSelecionada.preco_medio * (1 - this.novoPlano.stop_loss / 100);
        },
        
        getLucroEstimado() {
            if (!this.posicaoSelecionada || !this.novoPlano.stop_gain) return 0;
            const precoGain = this.getPrecoStopGain();
            return (precoGain - this.posicaoSelecionada.preco_medio) * this.novoPlano.quantidade;
        },
        
        getPrejuizoMaximo() {
            if (!this.posicaoSelecionada || !this.novoPlano.stop_loss) return 0;
            const precoLoss = this.getPrecoStopLoss();
            return (this.posicaoSelecionada.preco_medio - precoLoss) * this.novoPlano.quantidade;
        },
        
        // Handle mudança de moeda
        handleCurrencyChange(detail) {
            this.currency = detail.currency;
            this.exchangeRate = detail.rate;
            localStorage.setItem('preferredCurrency', this.currency);
        },
        
        // Utilitários
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
