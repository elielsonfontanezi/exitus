// Modernização da tela de compra com API REST
const API_URL = 'http://localhost:5000';

async function searchAtivos(query) {
    const token = localStorage.getItem('access_token');
    const response = await fetch(`${API_URL}/api/ativos?search=${query}`, {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    return response.json();
}

async function createTransacao(data) {
    const token = localStorage.getItem('access_token');
    const response = await fetch(`${API_URL}/api/transacoes`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });
    return response.json();
}

function showToast(title, message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.querySelector('.toast-header strong').textContent = title;
    toast.querySelector('.toast-body').textContent = message;
    toast.style.display = 'block';
    setTimeout(() => toast.style.display = 'none', 5000);
}
