/**
 * Reports - JavaScript (Redesign)
 * Sistema de geração e gerenciamento de relatórios
 */

// Função Alpine.js para gerenciar relatórios
function reportsData() {
    return {
        currency: localStorage.getItem('preferredCurrency') || 'BRL',
        exchangeRate: 5.00,
        loading: true,
        showModal: false,
        gerando: false,
        previewRelatorio: false,
        
        // Dados
        resumo: {
            total_relatorios: 0,
            relatorios_mes: 0,
            relatorios_portfolio: 0,
            relatorios_performance: 0,
            ultimo_portfolio: null,
            ultimo_performance: null,
            downloads_hoje: 0,
            total_downloads: 0
        },
        
        relatorios: [],
        relatorioSelecionado: null,
        
        // Configuração do relatório
        configRelatorio: {
            data_inicio: '',
            data_fim: '',
            formato: 'PDF',
            opcoes: {}
        },
        
        // Tipos de relatórios disponíveis
        tiposRelatorios: [
            {
                id: 'portfolio',
                nome: 'Portfolio Geral',
                descricao: 'Visão completa do seu portfólio',
                icone: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z',
                corBg: 'bg-blue-100',
                corIcon: 'text-blue-600',
                opcoes: [
                    { id: 'graficos', nome: 'Incluir gráficos' },
                    { id: 'detalhes', nome: 'Detalhes por ativo' },
                    { id: 'dividendos', nome: 'Histórico de dividendos' }
                ]
            },
            {
                id: 'performance',
                nome: 'Performance Mensal',
                descricao: 'Análise de rentabilidade',
                icone: 'M13 7h8m0 0v8m0-8l-8 8-4-4-6 6',
                corBg: 'bg-green-100',
                corIcon: 'text-green-600',
                opcoes: [
                    { id: 'benchmark', nome: 'Comparação com benchmark' },
                    { id: 'ir', nome: 'Cálculo de IR' },
                    { id: 'proventos', nome: 'Proventos recebidos' }
                ]
            },
            {
                id: 'imposto_renda',
                nome: 'Imposto de Renda',
                descricao: 'Relatório fiscal completo',
                icone: 'M9 14l6-6m-5.5.5h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z',
                corBg: 'bg-red-100',
                corIcon: 'text-red-600',
                opcoes: [
                    { id: 'darf', nome: 'DARFs geradas' },
                    { id: 'prejuizo', nome: 'Prejuízos acumulados' },
                    { id: 'detalhe_mes', nome: 'Detalhe mensal' }
                ]
            },
            {
                id: 'dividendos',
                nome: 'Relatório de Dividendos',
                descricao: 'Histórico e projeções',
                icone: 'M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z',
                corBg: 'bg-yellow-100',
                corIcon: 'text-yellow-600',
                opcoes: [
                    { id: 'recebidos', nome: 'Dividendos recebidos' },
                    { id: 'projetados', nome: 'Projeções futuras' },
                    { id: 'yield', nome: 'Yield on Cost' }
                ]
            },
            {
                id: 'alocacao',
                nome: 'Análise de Alocação',
                descricao: 'Distribuição por classe/ativo',
                icone: 'M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z',
                corBg: 'bg-purple-100',
                corIcon: 'text-purple-600',
                opcoes: [
                    { id: 'setores', nome: 'Análise por setor' },
                    { id: 'concentracao', nome: 'Risco de concentração' },
                    { id: 'rebalanceamento', nome: 'Sugestões de rebalanceamento' }
                ]
            },
            {
                id: 'custos',
                nome: 'Relatório de Custos',
                descricao: 'Taxas e custos operacionais',
                icone: 'M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
                corBg: 'bg-orange-100',
                corIcon: 'text-orange-600',
                opcoes: [
                    { id: 'corretagem', nome: 'Taxas de corretagem' },
                    { id: 'custodia', nome: 'Taxas de custódia' },
                    { id: 'impostos', nome: 'Impostos pagos' }
                ]
            }
        ],
        
        // Inicialização
        init() {
            this.carregarRelatorios();
        },
        
        // Carregar relatórios
        async carregarRelatorios() {
            this.loading = true;
            
            try {
                const response = await fetch('/api/relatorios');
                if (response.ok) {
                    const data = await response.json();
                    this.relatorios = data.data || [];
                }
                
                // Calcular resumo
                this.calcularResumo();
                
            } catch (error) {
                console.error('Erro ao carregar relatórios:', error);
                this.loadMockData();
            } finally {
                this.loading = false;
            }
        },
        
        // Carregar dados mock
        loadMockData() {
            this.relatorios = [
                {
                    id: 1,
                    nome: 'Portfolio Março 2024',
                    tipo: 'portfolio',
                    periodo: '01/03/2024 - 31/03/2024',
                    formato: 'PDF',
                    tamanho: '2.5 MB',
                    status: 'concluido',
                    data_criacao: '2024-03-15T10:30:00',
                    arquivo: 'portfolio_marco_2024.pdf'
                },
                {
                    id: 2,
                    nome: 'Performance Q1 2024',
                    tipo: 'performance',
                    periodo: '01/01/2024 - 31/03/2024',
                    formato: 'Excel',
                    tamanho: '1.8 MB',
                    status: 'concluido',
                    data_criacao: '2024-04-01T14:20:00',
                    arquivo: 'performance_q1_2024.xlsx'
                },
                {
                    id: 3,
                    nome: 'IR Anual 2023',
                    tipo: 'imposto_renda',
                    periodo: '01/01/2023 - 31/12/2023',
                    formato: 'PDF',
                    tamanho: '3.2 MB',
                    status: 'processando',
                    data_criacao: '2024-04-02T09:15:00',
                    arquivo: null
                },
                {
                    id: 4,
                    nome: 'Dividendos 2024',
                    tipo: 'dividendos',
                    periodo: '01/01/2024 - 31/12/2024',
                    formato: 'CSV',
                    tamanho: '0.8 MB',
                    status: 'concluido',
                    data_criacao: '2024-03-28T16:45:00',
                    arquivo: 'dividendos_2024.csv'
                },
                {
                    id: 5,
                    nome: 'Alocação Atual',
                    tipo: 'alocacao',
                    periodo: 'Atual',
                    formato: 'PDF',
                    tamanho: '1.5 MB',
                    status: 'concluido',
                    data_criacao: '2024-04-03T11:00:00',
                    arquivo: 'alocacao_atual.pdf'
                },
                {
                    id: 6,
                    nome: 'Custos Mensal',
                    tipo: 'custos',
                    periodo: '01/03/2024 - 31/03/2024',
                    formato: 'Excel',
                    tamanho: '0.5 MB',
                    status: 'erro',
                    data_criacao: '2024-04-03T08:30:00',
                    arquivo: null
                }
            ];
            
            this.calcularResumo();
        },
        
        // Calcular resumo
        calcularResumo() {
            const agora = new Date();
            const inicioMes = new Date(agora.getFullYear(), agora.getMonth(), 1);
            const inicioDia = new Date(agora.getFullYear(), agora.getMonth(), agora.getDate());
            
            const relatoriosMes = this.relatorios.filter(r => new Date(r.data_criacao) >= inicioMes);
            const relatoriosPortfolio = this.relatorios.filter(r => r.tipo === 'portfolio');
            const relatoriosPerformance = this.relatorios.filter(r => r.tipo === 'performance');
            const downloadsHoje = 5; // Mock
            
            this.resumo = {
                total_relatorios: this.relatorios.length,
                relatorios_mes: relatoriosMes.length,
                relatorios_portfolio: relatoriosPortfolio.length,
                relatorios_performance: relatoriosPerformance.length,
                ultimo_portfolio: relatoriosPortfolio.length > 0 ? this.formatDate(relatoriosPortfolio[0].data_criacao) : null,
                ultimo_performance: relatoriosPerformance.length > 0 ? this.formatDate(relatoriosPerformance[0].data_criacao) : null,
                downloads_hoje: downloadsHoje,
                total_downloads: this.relatorios.filter(r => r.status === 'concluido').length * 2.5 // Mock
            };
        },
        
        // Selecionar tipo de relatório
        selecionarTipoRelatorio(tipo) {
            this.relatorioSelecionado = tipo;
            this.configRelatorio = {
                data_inicio: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
                data_fim: new Date().toISOString().split('T')[0],
                formato: 'PDF',
                opcoes: {}
            };
            
            // Inicializar opções
            if (tipo.opcoes) {
                tipo.opcoes.forEach(opcao => {
                    this.configRelatorio.opcoes[opcao.id] = true;
                });
            }
            
            this.showModal = true;
            this.previewRelatorio = true;
        },
        
        // Gerar relatório
        async gerarRelatorio() {
            this.gerando = true;
            
            try {
                const response = await fetch('/api/relatorios', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        tipo: this.relatorioSelecionado.id,
                        ...this.configRelatorio
                    })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    this.relatorios.unshift(data.data);
                    this.calcularResumo();
                    this.showModal = false;
                    this.gerando = false;
                    
                    // Simular download após processamento
                    setTimeout(() => {
                        data.data.status = 'concluido';
                        data.data.arquivo = `${this.relatorioSelecionado.id}_${Date.now()}.${this.configRelatorio.formato.toLowerCase()}`;
                        this.calcularResumo();
                    }, 3000);
                } else {
                    alert('Erro ao gerar relatório');
                    this.gerando = false;
                }
            } catch (error) {
                console.error('Erro ao gerar relatório:', error);
                // Mock: adicionar localmente
                const novo = {
                    id: Date.now(),
                    nome: `${this.relatorioSelecionado.nome} - ${new Date().toLocaleDateString('pt-BR')}`,
                    tipo: this.relatorioSelecionado.id,
                    periodo: `${this.formatDate(this.configRelatorio.data_inicio)} - ${this.formatDate(this.configRelatorio.data_fim)}`,
                    formato: this.configRelatorio.formato,
                    tamanho: '~2.5 MB',
                    status: 'processando',
                    data_criacao: new Date().toISOString(),
                    arquivo: null
                };
                this.relatorios.unshift(novo);
                this.calcularResumo();
                this.showModal = false;
                this.gerando = false;
                
                // Simular conclusão
                setTimeout(() => {
                    novo.status = 'concluido';
                    novo.arquivo = `${this.relatorioSelecionado.id}_${Date.now()}.${this.configRelatorio.formato.toLowerCase()}`;
                    this.calcularResumo();
                }, 3000);
            }
        },
        
        // Baixar relatório
        baixarRelatorio(relatorio) {
            if (relatorio.status !== 'concluido' || !relatorio.arquivo) {
                alert('Relatório não está disponível para download');
                return;
            }
            
            // Simular download
            const link = document.createElement('a');
            link.href = `/api/relatorios/${relatorio.id}/download`;
            link.download = relatorio.arquivo;
            link.click();
            
            // Atualizar contador de downloads
            this.resumo.downloads_hoje++;
            this.resumo.total_downloads++;
        },
        
        // Excluir relatório
        async excluirRelatorio(relatorio) {
            if (!confirm(`Deseja excluir o relatório "${relatorio.nome}"?`)) {
                return;
            }
            
            try {
                const response = await fetch(`/api/relatorios/${relatorio.id}`, {
                    method: 'DELETE'
                });
                
                if (response.ok) {
                    const index = this.relatorios.findIndex(r => r.id === relatorio.id);
                    if (index > -1) {
                        this.relatorios.splice(index, 1);
                        this.calcularResumo();
                    }
                } else {
                    alert('Erro ao excluir relatório');
                }
            } catch (error) {
                console.error('Erro ao excluir relatório:', error);
                // Mock: remover localmente
                const index = this.relatorios.findIndex(r => r.id === relatorio.id);
                if (index > -1) {
                    this.relatorios.splice(index, 1);
                    this.calcularResumo();
                }
            }
        },
        
        // Atualizar lista
        atualizarLista() {
            this.carregarRelatorios();
        },
        
        // Obter tipo de relatório
        getTipoRelatorio(tipoId) {
            return this.tiposRelatorios.find(t => t.id === tipoId) || this.tiposRelatorios[0];
        },
        
        // Obter classe CSS do status
        getStatusClass(status) {
            const classMap = {
                'concluido': 'badge-success',
                'processando': 'badge-warning',
                'erro': 'badge-danger'
            };
            return classMap[status] || 'badge-gray';
        },
        
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
                month: '2-digit',
                year: '2-digit'
            });
        },
        
        formatDateTime(dateStr) {
            if (!dateStr) return '';
            const date = new Date(dateStr);
            return date.toLocaleDateString('pt-BR', { 
                day: '2-digit', 
                month: '2-digit',
                year: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            });
        }
    }
}
