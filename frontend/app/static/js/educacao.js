/**
 * Educação e Insights - JavaScript
 * Centro de aprendizado e ferramentas educacionais
 */

// Função Alpine.js para gerenciar educação
function educacaoData() {
    return {
        currency: localStorage.getItem('preferredCurrency') || 'BRL',
        exchangeRate: 5.00,
        loading: true,
        abaAtiva: 'artigos',
        filtroCategoria: '',
        ordenarPor: 'recentes',
        
        // Dados
        artigos: [],
        videos: [],
        cursos: [],
        calculadoras: [],
        
        // Inicialização
        init() {
            this.carregarDados();
        },
        
        // Carregar dados
        async carregarDados() {
            this.loading = true;
            
            try {
                // Carregar artigos
                const artigosResponse = await fetch('/api/educacao/artigos');
                if (artigosResponse.ok) {
                    const artigosData = await artigosResponse.json();
                    this.artigos = artigosData.data || [];
                }
                
                // Carregar vídeos
                const videosResponse = await fetch('/api/educacao/videos');
                if (videosResponse.ok) {
                    const videosData = await videosResponse.json();
                    this.videos = videosData.data || [];
                }
                
                // Carregar cursos
                const cursosResponse = await fetch('/api/educacao/cursos');
                if (cursosResponse.ok) {
                    const cursosData = await cursosResponse.json();
                    this.cursos = cursosData.data || [];
                }
                
                // Carregar calculadoras
                const calculadorasResponse = await fetch('/api/educacao/calculadoras');
                if (calculadorasResponse.ok) {
                    const calculadorasData = await calculadorasResponse.json();
                    this.calculadoras = calculadorasData.data || [];
                }
                
            } catch (error) {
                console.error('Erro ao carregar dados de educação:', error);
                // Carregar dados mock em caso de erro
                this.loadMockData();
            } finally {
                this.loading = false;
            }
        },
        
        // Carregar dados mock
        loadMockData() {
            this.artigos = [
                {
                    id: 1,
                    titulo: 'Guia Completo de Análise Fundamentalista',
                    resumo: 'Aprenda a analisar empresas usando indicadores financeiros fundamentais.',
                    categoria: 'fundamentos',
                    tempo_leitura: 15,
                    visualizacoes: '2.3k',
                    data: '2024-03-15',
                    imagem: '/static/images/artigos/fundamentalista.jpg',
                    conteudo: '# Conteúdo do artigo...'
                },
                {
                    id: 2,
                    titulo: 'Diversificação: A Chave do Sucesso',
                    resumo: 'Descubra como montar um portfolio diversificado e reduzir riscos.',
                    categoria: 'estrategias',
                    tempo_leitura: 10,
                    visualizacoes: '1.8k',
                    data: '2024-03-14',
                    imagem: '/static/images/artigos/diversificacao.jpg',
                    conteudo: '# Conteúdo do artigo...'
                },
                {
                    id: 3,
                    titulo: 'Entendendo Indicadores Macroeconômicos',
                    resumo: 'Como Selic, IPCA e dólar impactam seus investimentos.',
                    categoria: 'macro',
                    tempo_leitura: 12,
                    visualizacoes: '1.5k',
                    data: '2024-03-13',
                    imagem: '/static/images/artigos macro.jpg',
                    conteudo: '# Conteúdo do artigo...'
                },
                {
                    id: 4,
                    titulo: 'Análise Técnica: Suportes e Resistências',
                    resumo: 'Identifique os melhores pontos de entrada e saída usando gráficos.',
                    categoria: 'analise',
                    tempo_leitura: 20,
                    visualizacoes: '3.1k',
                    data: '2024-03-12',
                    imagem: '/static/images/artigos/tecnica.jpg',
                    conteudo: '# Conteúdo do artigo...'
                },
                {
                    id: 5,
                    titulo: 'Investindo em FIIs: Passo a Passo',
                    resumo: 'Tudo sobre Fundos Imobiliários e como receber renda mensal.',
                    categoria: 'fundamentos',
                    tempo_leitura: 18,
                    visualizacoes: '2.7k',
                    data: '2024-03-11',
                    imagem: '/static/images/artigos/fii.jpg',
                    conteudo: '# Conteúdo do artigo...'
                },
                {
                    id: 6,
                    titulo: 'Stop Loss: Como Proteger seu Capital',
                    resumo: 'Estratégias eficazes para limitar prejuízos e preservar patrimônio.',
                    categoria: 'estrategias',
                    tempo_leitura: 8,
                    visualizacoes: '1.2k',
                    data: '2024-03-10',
                    imagem: '/static/images/artigos/stoploss.jpg',
                    conteudo: '# Conteúdo do artigo...'
                }
            ];
            
            this.videos = [
                {
                    id: 1,
                    titulo: 'Como Montar sua Primeira Carteira',
                    descricao: 'Aprenda passo a passo a montar um portfolio de investimentos.',
                    categoria: 'fundamentos',
                    duracao: '25:30',
                    visualizacoes: '5.2k',
                    data: '2024-03-15',
                    thumbnail: '/static/images/videos/carteira.jpg',
                    url: '#'
                },
                {
                    id: 2,
                    titulo: 'Análise de Balanço Patrimonial',
                    descricao: 'Entenda os principais itens do balanço e como usá-los na análise.',
                    categoria: 'analise',
                    duracao: '32:15',
                    visualizacoes: '3.8k',
                    data: '2024-03-14',
                    thumbnail: '/static/images/videos/balanco.jpg',
                    url: '#'
                },
                {
                    id: 3,
                    titulo: 'Estratégias de DCA (Dollar Cost Averaging)',
                    descricao: 'Como usar o DCA para suavizar volatilidade e maximizar retornos.',
                    categoria: 'estrategias',
                    duracao: '18:45',
                    visualizacoes: '2.1k',
                    data: '2024-03-13',
                    thumbnail: '/static/images/videos/dca.jpg',
                    url: '#'
                },
                {
                    id: 4,
                    titulo: 'Mercado de Ações em 2024',
                    descricao: 'Perspectivas e tendências para o mercado brasileiro este ano.',
                    categoria: 'macro',
                    duracao: '28:00',
                    visualizacoes: '4.5k',
                    data: '2024-03-12',
                    thumbnail: '/static/images/videos/2024.jpg',
                    url: '#'
                }
            ];
            
            this.cursos = [
                {
                    id: 1,
                    titulo: 'Investidor Inteligente',
                    descricao: 'Curso completo do básico ao avançado em investimentos.',
                    tipo: 'curso',
                    nivel: 'Iniciante',
                    modulos: 12,
                    duracao: '16 horas',
                    preco: 'R$ 197,00',
                    progresso: 75
                },
                {
                    id: 2,
                    titulo: 'Análise Técnica Profissional',
                    descricao: 'Domine a análise técnica e padrões gráficos.',
                    tipo: 'curso',
                    nivel: 'Intermediário',
                    modulos: 8,
                    duracao: '12 horas',
                    preco: 'R$ 297,00',
                    progresso: 30
                },
                {
                    id: 3,
                    titulo: 'Guia de Fundos Imobiliários',
                    descricao: 'E-book completo sobre investimentos em FIIs.',
                    tipo: 'e-book',
                    nivel: 'Iniciante',
                    modulos: 6,
                    duracao: '3 horas',
                    preco: 'R$ 47,00',
                    progresso: 100
                },
                {
                    id: 4,
                    titulo: 'Trading para Iniciantes',
                    descricao: 'Primeiros passos no day trade e swing trade.',
                    tipo: 'curso',
                    nivel: 'Iniciante',
                    modulos: 10,
                    duracao: '14 horas',
                    preco: 'R$ 397,00',
                    progresso: 0
                }
            ];
            
            this.calculadoras = [
                {
                    id: 1,
                    nome: 'Simulador de Juros Compostos',
                    descricao: 'Calcule o poder dos juros compostos ao longo do tempo.'
                },
                {
                    id: 2,
                    nome: 'Calculadora de IR',
                    descricao: 'Simule o imposto de renda sobre ganhos de capital.'
                },
                {
                    id: 3,
                    nome: 'Análise de Risco-Retorno',
                    descricao: 'Avalie o risco e retorno potencial dos seus investimentos.'
                },
                {
                    id: 4,
                    nome: 'Simulador de Aposentadoria',
                    descricao: 'Planeje sua aposentadoria e calcule quanto precisa investir.'
                },
                {
                    id: 5,
                    nome: 'Calculadora de Dividendos',
                    descricao: 'Projeta seus rendimentos com dividendos e proventos.'
                },
                {
                    id: 6,
                    nome: 'Análise de Portfolio',
                    descricao: 'Verifique a diversificação e alocação do seu portfolio.'
                }
            ];
        },
        
        // Computed: artigos filtrados
        get artigosFiltrados() {
            let filtrados = [...this.artigos];
            
            // Filtrar por categoria
            if (this.filtroCategoria) {
                filtrados = filtrados.filter(a => a.categoria === this.filtroCategoria);
            }
            
            // Ordenar
            switch (this.ordenarPor) {
                case 'recentes':
                    filtrados.sort((a, b) => new Date(b.data) - new Date(a.data));
                    break;
                case 'populares':
                    filtrados.sort((a, b) => {
                        const viewsA = parseFloat(a.visualizacoes.replace('k', '')) * (a.visualizacoes.includes('k') ? 1000 : 1);
                        const viewsB = parseFloat(b.visualizacoes.replace('k', '')) * (b.visualizacoes.includes('k') ? 1000 : 1);
                        return viewsB - viewsA;
                    });
                    break;
                case 'lidos':
                    filtrados.sort((a, b) => b.tempo_leitura - a.tempo_leitura);
                    break;
            }
            
            return filtrados;
        },
        
        // Abrir artigo
        abrirArtigo(artigo) {
            // Implementar modal ou navegação para artigo completo
            console.log('Abrir artigo:', artigo);
            alert(`Abrindo artigo: ${artigo.titulo}`);
        },
        
        // Abrir vídeo
        abrirVideo(video) {
            // Implementar player de vídeo
            console.log('Abrir vídeo:', video);
            alert(`Abrindo vídeo: ${video.titulo}`);
        },
        
        // Continuar curso
        continuarCurso(curso) {
            // Implementar navegação para curso
            console.log('Continuar curso:', curso);
            alert(`Continuando curso: ${curso.titulo}`);
        },
        
        // Ver detalhes do curso
        verDetalhesCurso(curso) {
            // Implementar modal com detalhes
            console.log('Ver detalhes:', curso);
            alert(`Detalhes do curso: ${curso.titulo}`);
        },
        
        // Abrir calculadora
        abrirCalculadora(calculadora) {
            // Implementar calculadora específica
            console.log('Abrir calculadora:', calculadora);
            alert(`Abrindo calculadora: ${calculadora.nome}`);
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
        }
    }
}
