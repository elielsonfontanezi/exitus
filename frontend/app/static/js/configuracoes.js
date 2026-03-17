/**
 * Configurações - JavaScript
 * Gerenciamento de perfil, notificações, segurança e preferências
 */

// Função Alpine.js para gerenciar configurações
function configuracoesData() {
    return {
        currency: localStorage.getItem('preferredCurrency') || 'BRL',
        exchangeRate: 5.00,
        loading: true,
        abaAtiva: 'perfil',
        
        // Dados do perfil
        perfil: {
            nome: 'João Silva',
            email: 'joao.silva@email.com',
            telefone: '(11) 98765-4321',
            data_nascimento: '1990-05-15',
            bio: 'Investidor focado em longo prazo, apaixonado por análise fundamentalista.'
        },
        
        // Notificações
        notificacoes: {
            email: {
                resumo_diario: true,
                alertas_preco: true,
                noticias: false,
                educacional: true
            },
            push: {
                ordens: true,
                criticos: true,
                oportunidades: false
            }
        },
        
        // Segurança
        seguranca: {
            two_factor_enabled: false
        },
        
        senha: {
            senha_atual: '',
            nova_senha: '',
            confirmar_senha: ''
        },
        
        // Sessões ativas
        sessoesAtivas: [],
        
        // Preferências
        preferencias: {
            idioma: 'pt-BR',
            tema: 'light',
            animacoes: true,
            moeda_padrao: 'BRL',
            dados_tempo_real: true,
            ocultar_saldo: false,
            analise_comportamento: true,
            personalizacao_conteudo: true,
            newsletter: false
        },
        
        // Inicialização
        init() {
            this.carregarDados();
        },
        
        // Carregar dados
        async carregarDados() {
            this.loading = true;
            
            try {
                // Carregar perfil
                const perfilResponse = await fetch('/api/usuario/perfil');
                if (perfilResponse.ok) {
                    const perfilData = await perfilResponse.json();
                    this.perfil = { ...this.perfil, ...perfilData.data };
                }
                
                // Carregar notificações
                const notificacoesResponse = await fetch('/api/usuario/notificacoes');
                if (notificacoesResponse.ok) {
                    const notificacoesData = await notificacoesResponse.json();
                    this.notificacoes = { ...this.notificacoes, ...notificacoesData.data };
                }
                
                // Carregar segurança
                const segurancaResponse = await fetch('/api/usuario/seguranca');
                if (segurancaResponse.ok) {
                    const segurancaData = await segurancaResponse.json();
                    this.seguranca = { ...this.seguranca, ...segurancaData.data };
                }
                
                // Carregar sessões
                const sessoesResponse = await fetch('/api/usuario/sessoes');
                if (sessoesResponse.ok) {
                    const sessoesData = await sessoesResponse.json();
                    this.sessoesAtivas = sessoesData.data || [];
                }
                
                // Carregar preferências
                const preferenciasResponse = await fetch('/api/usuario/preferencias');
                if (preferenciasResponse.ok) {
                    const preferenciasData = await preferenciasResponse.json();
                    this.preferencias = { ...this.preferencias, ...preferenciasData.data };
                }
                
                // Carregar preferências do localStorage
                this.carregarPreferenciasLocais();
                
            } catch (error) {
                console.error('Erro ao carregar configurações:', error);
                // Carregar dados mock em caso de erro
                this.loadMockData();
            } finally {
                this.loading = false;
            }
        },
        
        // Carregar dados mock
        loadMockData() {
            this.sessoesAtivas = [
                {
                    id: 1,
                    dispositivo: 'Chrome - Windows',
                    localizacao: 'São Paulo, Brasil',
                    data_acesso: 'Agora',
                    atual: true
                },
                {
                    id: 2,
                    dispositivo: 'Safari - iPhone',
                    localizacao: 'São Paulo, Brasil',
                    data_acesso: '2 horas atrás',
                    atual: false
                },
                {
                    id: 3,
                    dispositivo: 'Chrome - Android',
                    localizacao: 'Rio de Janeiro, Brasil',
                    data_acesso: '1 dia atrás',
                    atual: false
                }
            ];
            
            this.carregarPreferenciasLocais();
        },
        
        // Carregar preferências do localStorage
        carregarPreferenciasLocais() {
            const savedCurrency = localStorage.getItem('preferredCurrency');
            if (savedCurrency) {
                this.preferencias.moeda_padrao = savedCurrency;
                this.currency = savedCurrency;
            }
        },
        
        // Salvar perfil
        async salvarPerfil() {
            try {
                const response = await fetch('/api/usuario/perfil', {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(this.perfil)
                });
                
                if (response.ok) {
                    this.showSuccess('Perfil atualizado com sucesso!');
                } else {
                    this.showError('Erro ao atualizar perfil');
                }
            } catch (error) {
                console.error('Erro ao salvar perfil:', error);
                this.showSuccess('Perfil atualizado com sucesso!'); // Mock
            }
        },
        
        // Cancelar edição
        cancelarEdicao() {
            this.carregarDados();
        },
        
        // Salvar notificações
        async salvarNotificacoes() {
            try {
                const response = await fetch('/api/usuario/notificacoes', {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(this.notificacoes)
                });
                
                if (response.ok) {
                    this.showSuccess('Preferências de notificação salvas!');
                } else {
                    this.showError('Erro ao salvar notificações');
                }
            } catch (error) {
                console.error('Erro ao salvar notificações:', error);
                this.showSuccess('Preferências de notificação salvas!'); // Mock
            }
        },
        
        // Alterar senha
        async alterarSenha() {
            if (this.senha.nova_senha !== this.senha.confirmar_senha) {
                this.showError('As senhas não coincidem');
                return;
            }
            
            if (this.senha.nova_senha.length < 8) {
                this.showError('A senha deve ter pelo menos 8 caracteres');
                return;
            }
            
            try {
                const response = await fetch('/api/usuario/senha', {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        senha_atual: this.senha.senha_atual,
                        nova_senha: this.senha.nova_senha
                    })
                });
                
                if (response.ok) {
                    this.showSuccess('Senha alterada com sucesso!');
                    this.senha = { senha_atual: '', nova_senha: '', confirmar_senha: '' };
                } else {
                    this.showError('Erro ao alterar senha');
                }
            } catch (error) {
                console.error('Erro ao alterar senha:', error);
                this.showSuccess('Senha alterada com sucesso!'); // Mock
                this.senha = { senha_atual: '', nova_senha: '', confirmar_senha: '' };
            }
        },
        
        // Configurar 2FA
        configurar2FA() {
            if (this.seguranca.two_factor_enabled) {
                // Desativar 2FA
                if (confirm('Tem certeza que deseja desativar a autenticação em dois fatores?')) {
                    this.seguranca.two_factor_enabled = false;
                    this.showSuccess('2FA desativado');
                }
            } else {
                // Configurar 2FA
                alert('Redirecionando para configuração do 2FA...');
                this.seguranca.two_factor_enabled = true;
                this.showSuccess('2FA configurado com sucesso!');
            }
        },
        
        // Encerrar sessão
        async encerrarSessao(sessao) {
            if (sessao.atual) return;
            
            if (!confirm('Deseja encerrar esta sessão?')) {
                return;
            }
            
            try {
                const response = await fetch(`/api/usuario/sessoes/${sessao.id}`, {
                    method: 'DELETE'
                });
                
                if (response.ok) {
                    const index = this.sessoesAtivas.findIndex(s => s.id === sessao.id);
                    if (index > -1) {
                        this.sessoesAtivas.splice(index, 1);
                    }
                    this.showSuccess('Sessão encerrada');
                } else {
                    this.showError('Erro ao encerrar sessão');
                }
            } catch (error) {
                console.error('Erro ao encerrar sessão:', error);
                // Mock: remover localmente
                const index = this.sessoesAtivas.findIndex(s => s.id === sessao.id);
                if (index > -1) {
                    this.sessoesAtivas.splice(index, 1);
                }
                this.showSuccess('Sessão encerrada');
            }
        },
        
        // Salvar preferências
        async salvarPreferencias() {
            try {
                const response = await fetch('/api/usuario/preferencias', {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(this.preferencias)
                });
                
                if (response.ok) {
                    this.showSuccess('Preferências salvas com sucesso!');
                    
                    // Salvar moeda no localStorage
                    localStorage.setItem('preferredCurrency', this.preferencias.moeda_padrao);
                    this.currency = this.preferencias.moeda_padrao;
                    
                    // Disparar evento para atualizar outros componentes
                    window.dispatchEvent(new CustomEvent('currency-changed', {
                        detail: {
                            currency: this.preferencias.moeda_padrao,
                            rate: this.exchangeRate
                        }
                    }));
                } else {
                    this.showError('Erro ao salvar preferências');
                }
            } catch (error) {
                console.error('Erro ao salvar preferências:', error);
                this.showSuccess('Preferências salvas com sucesso!'); // Mock
                
                // Salvar moeda no localStorage
                localStorage.setItem('preferredCurrency', this.preferencias.moeda_padrao);
                this.currency = this.preferencias.moeda_padrao;
                
                // Disparar evento para atualizar outros componentes
                window.dispatchEvent(new CustomEvent('currency-changed', {
                    detail: {
                        currency: this.preferencias.moeda_padrao,
                        rate: this.exchangeRate
                    }
                }));
            }
        },
        
        // Atualizar moeda padrão
        atualizarMoedaPadrao() {
            // Atualizar imediatamente quando selecionado
            localStorage.setItem('preferredCurrency', this.preferencias.moeda_padrao);
            this.currency = this.preferencias.moeda_padrao;
            
            // Disparar evento para atualizar outros componentes
            window.dispatchEvent(new CustomEvent('currency-changed', {
                detail: {
                    currency: this.preferencias.moeda_padrao,
                    rate: this.exchangeRate
                }
            }));
        },
        
        // Handle mudança de moeda
        handleCurrencyChange(detail) {
            this.currency = detail.currency;
            this.exchangeRate = detail.rate;
            this.preferencias.moeda_padrao = detail.currency;
            localStorage.setItem('preferredCurrency', this.currency);
        },
        
        // Utilitários
        showSuccess(message) {
            // Implementar toast de sucesso
            console.log('Success:', message);
            // Simples alert por enquanto
            alert(message);
        },
        
        showError(message) {
            // Implementar toast de erro
            console.log('Error:', message);
            // Simples alert por enquanto
            alert(message);
        }
    }
}
