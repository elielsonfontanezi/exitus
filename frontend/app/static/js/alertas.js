/**
 * Central de Alertas - JavaScript
 * Sistema de monitoramento de preços, notícias e eventos
 */

// Função Alpine.js para gerenciar alertas
function alertasData() {
    return {
        currency: localStorage.getItem('preferredCurrency') || 'BRL',
        exchangeRate: 5.00,
        loading: true,
        filtroTipo: 'todos',
        filtroStatus: 'todos',
        filtroAtivo: '',
        showModal: false,
        
        // Resumo
        resumo: {
            alertas_ativos: 0,
            total_alertas: 0,
            alertas_hoje: 0,
            preco_alvo_qtd: 0,
            preco_alvo_ativos: 0,
            preco_alvo_acionados: 0,
            noticias_qtd: 0,
            noticias_ativos: 0,
            noticias_novas: 0,
            eventos_qtd: 0,
            eventos_proximos: 0
        },
        
        // Dados
        alertas: [],
        ativosDisponiveis: [],
        
        // Novo alerta
        novoAlerta: {
            tipo: 'preco',
            ativo: '',
            descricao: ''
        },
        
        // Inicialização
        init() {
            this.carregarDados();
        },
        
        // Carregar dados
        async carregarDados() {
            this.loading = true;
            
            try {
                // Carregar alertas
                const alertasResponse = await fetch('/api/alertas');
                if (alertasResponse.ok) {
                    const alertasData = await alertasResponse.json();
                    this.alertas = alertasData.data || [];
                }
                
                // Carregar ativos disponíveis
                const ativosResponse = await fetch('/api/ativos');
                if (ativosResponse.ok) {
                    const ativosData = await ativosResponse.json();
                    this.ativosDisponiveis = ativosData.data?.ativos || [];
                }
                
                // Calcular resumo
                this.calcularResumo();
                
            } catch (error) {
                console.error('Erro ao carregar dados de alertas:', error);
                // Carregar dados mock em caso de erro
                this.loadMockData();
            } finally {
                this.loading = false;
            }
        },
        
        // Calcular resumo
        calcularResumo() {
            const ativos = this.alertasAtivos;
            const hoje = new Date().toDateString();
            
            const alertasAtivos = this.alertas.filter(a => a.status === 'ativo');
            const alertasHoje = this.alertas.filter(a => 
                new Date(a.ultimo_acionamento).toDateString() === hoje
            );
            
            const precoAlvo = this.alertas.filter(a => a.tipo === 'preco');
            const precoAlvoAtivos = [...new Set(precoAlvo.map(a => a.ativo))].length;
            const precoAlvoAcionados = precoAlvo.filter(a => a.ultimo_acionamento).length;
            
            const noticias = this.alertas.filter(a => a.tipo === 'noticia');
            const noticiasAtivos = [...new Set(noticias.map(a => a.ativo))].length;
            const noticiasNovas = noticias.filter(a => 
                new Date(a.ultimo_acionamento).toDateString() === hoje
            ).length;
            
            const eventos = this.alertas.filter(a => a.tipo === 'evento');
            const agora = new Date();
            const trintaDias = new Date(agora.getTime() + (30 * 24 * 60 * 60 * 1000));
            const eventosProximos = eventos.filter(e => 
                new Date(e.data_evento) <= trintaDias && new Date(e.data_evento) >= agora
            ).length;
            
            this.resumo = {
                alertas_ativos: alertasAtivos.length,
                total_alertas: this.alertas.length,
                alertas_hoje: alertasHoje.length,
                preco_alvo_qtd: precoAlvo.length,
                preco_alvo_ativos: precoAlvoAtivos,
                preco_alvo_acionados: precoAlvoAcionados,
                noticias_qtd: noticias.length,
                noticias_ativos: noticiasAtivos,
                noticias_novas: noticiasNovas,
                eventos_qtd: eventos.length,
                eventos_proximos: eventosProximos
            };
        },
        
        // Alertas por ativo (para filtro)
        get alertasAtivos() {
            return [...new Set(this.alertas.map(a => a.ativo))];
        },
        
        // Ativos monitorados (para filtro)
        get ativosMonitorados() {
            return this.alertasAtivos.sort();
        },
        
        // Alertas filtrados
        get filteredAlertas() {
            let filtered = this.alertas;
            
            // Filtrar por tipo
            if (this.filtroTipo !== 'todos') {
                filtered = filtered.filter(a => a.tipo === this.filtroTipo);
            }
            
            // Filtrar por status
            if (this.filtroStatus !== 'todos') {
                filtered = filtered.filter(a => a.status === this.filtroStatus);
            }
            
            // Filtrar por ativo
            if (this.filtroAtivo) {
                filtered = filtered.filter(a => a.ativo === this.filtroAtivo);
            }
            
            return filtered.sort((a, b) => new Date(b.data_criacao) - new Date(a.data_criacao));
        },
        
        // Filtrar alertas
        filtrarAlertas() {
            // A reatividade do Alpine.js vai atualizar automaticamente
        },
        
        // Abrir modal de novo alerta
        abrirModalAlerta() {
            this.novoAlerta = {
                tipo: 'preco',
                ativo: '',
                descricao: ''
            };
            this.showModal = true;
        },
        
        // Criar alerta
        async criarAlerta() {
            if (!this.novoAlerta.ativo || !this.novoAlerta.descricao) {
                alert('Preencha todos os campos');
                return;
            }
            
            try {
                const response = await fetch('/api/alertas', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(this.novoAlerta)
                });
                
                if (response.ok) {
                    const data = await response.json();
                    this.alertas.push(data.data);
                    this.calcularResumo();
                    this.showModal = false;
                } else {
                    alert('Erro ao criar alerta');
                }
            } catch (error) {
                console.error('Erro ao criar alerta:', error);
                // Mock: adicionar localmente
                const novo = {
                    id: Date.now(),
                    ...this.novoAlerta,
                    titulo: `${this.getTipoNome(this.novoAlerta.tipo)} - ${this.novoAlerta.ativo}`,
                    status: 'ativo',
                    data_criacao: new Date().toISOString(),
                    condicoes: [{
                        id: 1,
                        descricao: this.novoAlerta.descricao
                    }]
                };
                this.alertas.push(novo);
                this.calcularResumo();
                this.showModal = false;
            }
        },
        
        // Toggle status do alerta
        async toggleAlerta(alerta) {
            const novoStatus = alerta.status === 'ativo' ? 'pausado' : 'ativo';
            
            try {
                const response = await fetch(`/api/alertas/${alerta.id}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ status: novoStatus })
                });
                
                if (response.ok) {
                    alerta.status = novoStatus;
                    this.calcularResumo();
                }
            } catch (error) {
                console.error('Erro ao atualizar alerta:', error);
                // Mock: atualizar localmente
                alerta.status = novoStatus;
                this.calcularResumo();
            }
        },
        
        // Editar alerta
        editarAlerta(alerta) {
            // Implementar modal de edição
            console.log('Editar alerta:', alerta);
        },
        
        // Excluir alerta
        async excluirAlerta(alerta) {
            if (!confirm('Deseja excluir este alerta?')) {
                return;
            }
            
            try {
                const response = await fetch(`/api/alertas/${alerta.id}`, {
                    method: 'DELETE'
                });
                
                if (response.ok) {
                    const index = this.alertas.findIndex(a => a.id === alerta.id);
                    if (index > -1) {
                        this.alertas.splice(index, 1);
                        this.calcularResumo();
                    }
                }
            } catch (error) {
                console.error('Erro ao excluir alerta:', error);
                // Mock: remover localmente
                const index = this.alertas.findIndex(a => a.id === alerta.id);
                if (index > -1) {
                    this.alertas.splice(index, 1);
                    this.calcularResumo();
                }
            }
        },
        
        // Testar todos os alertas
        testarTodos() {
            alert('Função de teste em desenvolvimento...');
        },
        
        // Carregar dados mock
        loadMockData() {
            this.alertas = [
                {
                    id: 1,
                    tipo: 'preco',
                    ativo: 'PETR4',
                    titulo: 'Preço Alvo - PETR4',
                    descricao: 'Alertar quando atingir R$ 40,00',
                    status: 'ativo',
                    data_criacao: '2024-03-10T10:00:00',
                    ultimo_acionamento: null,
                    condicoes: [
                        { id: 1, descricao: 'Preço >= R$ 40,00' }
                    ]
                },
                {
                    id: 2,
                    tipo: 'noticia',
                    ativo: 'VALE3',
                    titulo: 'Notícias - VALE3',
                    descricao: 'Alertar sobre notícias relevantes',
                    status: 'ativo',
                    data_criacao: '2024-03-12T14:30:00',
                    ultimo_acionamento: '2024-03-15T09:15:00',
                    condicoes: [
                        { id: 1, descricao: 'Notícias com palavras-chave: "lucro", "resultado", "dividendo"' }
                    ]
                },
                {
                    id: 3,
                    tipo: 'evento',
                    ativo: 'ITUB4',
                    titulo: 'Eventos - ITUB4',
                    descricao: 'Pagamento de dividendos',
                    status: 'ativo',
                    data_criacao: '2024-03-08T16:45:00',
                    ultimo_acionamento: null,
                    data_evento: '2024-04-15T00:00:00',
                    condicoes: [
                        { id: 1, descricao: 'Data Com: 15/04/2024' }
                    ]
                },
                {
                    id: 4,
                    tipo: 'variacao',
                    ativo: 'WEGE3',
                    titulo: 'Variação % - WEGE3',
                    descricao: 'Alertar se cair mais de 5%',
                    status: 'pausado',
                    data_criacao: '2024-03-05T11:20:00',
                    ultimo_acionamento: '2024-03-14T13:30:00',
                    condicoes: [
                        { id: 1, descricao: 'Variação diária <= -5%' }
                    ]
                }
            ];
            
            this.ativosDisponiveis = [
                { ticker: 'PETR4', nome: 'Petrobras PN' },
                { ticker: 'VALE3', nome: 'Vale ON' },
                { ticker: 'ITUB4', nome: 'Itaú Unibanco PN' },
                { ticker: 'WEGE3', nome: 'WEG ON' },
                { ticker: 'BBDC4', nome: 'Bradesco PN' }
            ];
            
            this.calcularResumo();
        },
        
        // Utilitários
        getTipoNome(tipo) {
            const nomes = {
                'preco': 'Preço Alvo',
                'noticia': 'Notícias',
                'evento': 'Eventos',
                'variacao': 'Variação %'
            };
            return nomes[tipo] || tipo;
        },
        
        getStatusClass(status) {
            const classes = {
                'ativo': 'bg-success-100',
                'pausado': 'bg-warning-100',
                'acionado': 'bg-info-100'
            };
            return classes[status] || 'bg-gray-100';
        },
        
        getStatusIconClass(status) {
            const classes = {
                'ativo': 'text-success-600',
                'pausado': 'text-warning-600',
                'acionado': 'text-info-600'
            };
            return classes[status] || 'text-gray-600';
        },
        
        getStatusBadgeClass(status) {
            const classes = {
                'ativo': 'badge-success',
                'pausado': 'badge-warning',
                'acionado': 'badge-info'
            };
            return classes[status] || 'badge-gray';
        },
        
        formatDate(dateStr) {
            if (!dateStr) return '';
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
        },
        
        // Handle mudança de moeda
        handleCurrencyChange(detail) {
            this.currency = detail.currency;
            this.exchangeRate = detail.rate;
            localStorage.setItem('preferredCurrency', this.currency);
        }
    }
}
