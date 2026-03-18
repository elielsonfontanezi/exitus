// Sistema de Autenticação Frontend
class AuthManager {
    constructor() {
        // Token mock para testes (válido por 24h)
        this.token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token') || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc3Mzg2NzQ0NCwianRpIjoiZmJmY2FmZDEtYzMzYi00ZTQ4LTgxODUtOWFkYWY0MDU1MTc5IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6ImFiZTVkNDFhLWFkYTctNDc4MC1hNGNkLWRkZGNlM2E5NGNkMiIsIm5iZiI6MTc3Mzg2NzQ0NCwiZXhwIjoxNzczODcxMDQ0LCJyb2xlIjoiYWRtaW4iLCJhc3Nlc3NvcmFfaWQiOiIyM2M1NGNiNC1jYjBhLTQzOGYtYjk4NS1kZWYyMWQ3MDkwNGUifQ.AZ1yWosV1BImNwDY7HjytwXWYLt5GXNK8osNNF6KWK0';
        this.user = JSON.parse(localStorage.getItem('user') || sessionStorage.getItem('user') || '{"id":"abe5d41a-ada7-4780-a4cd-dddc3ea94cd2","username":"admin","role":"admin"}');
    }
    
    // Salvar token e usuário
    saveToken(token, user) {
        this.token = token;
        this.user = user;
        
        // Salvar em localStorage (persistente)
        localStorage.setItem('access_token', token);
        localStorage.setItem('user', JSON.stringify(user));
        
        // Também em sessionStorage (para a sessão atual)
        sessionStorage.setItem('access_token', token);
        sessionStorage.setItem('user', JSON.stringify(user));
    }
    
    // Remover token (logout)
    removeToken() {
        this.token = null;
        this.user = null;
        
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        sessionStorage.removeItem('access_token');
        sessionStorage.removeItem('user');
    }
    
    // Verificar se está autenticado
    isAuthenticated() {
        return !!this.token;
    }
    
    // Obter headers para requisições API
    getHeaders() {
        if (!this.token) return {};
        
        return {
            'Authorization': `Bearer ${this.token}`,
            'Content-Type': 'application/json'
        };
    }
    
    // Fazer requisição autenticada
    async fetch(url, options = {}) {
        const headers = this.getHeaders();
        
        const config = {
            headers: {
                ...headers,
                ...(options.headers || {})
            },
            ...options
        };
        
        try {
            const response = await fetch(url, config);
            
            // Se receber 401, remover token e redirecionar
            if (response.status === 401) {
                this.removeToken();
                window.location.href = '/auth/login';
                return null;
            }
            
            return response;
        } catch (error) {
            console.error('Erro na requisição autenticada:', error);
            throw error;
        }
    }
    
    // Obter usuário atual
    getUser() {
        return this.user;
    }
    
    // Verificar se é admin
    isAdmin() {
        return this.user && this.user.role === 'admin';
    }
}

// Instância global
window.auth = new AuthManager();

// Auto-redirecionar se não estiver autenticado
document.addEventListener('DOMContentLoaded', function() {
    // Se não for página de login e não estiver autenticado
    if (!window.location.pathname.includes('/auth/') && !window.auth.isAuthenticated()) {
        window.location.href = '/auth/login';
    }
});
