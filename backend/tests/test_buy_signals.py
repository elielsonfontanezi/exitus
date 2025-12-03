import pytest
from app.blueprints.buy_signals_blueprint import buy_signals_bp
from app import create_app, db

@pytest.fixture
def client():
    app = create_app(testing=True)
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_margem_seguranca_petr4(client):
    response = client.get('/api/buy-signals/margem-seguranca/PETR4')
    data = response.get_json()
    assert data['success'] == True
    assert data['data']['margem_seguranca'] > 5  # 🟢 COMPRA

def test_buy_score_petr4(client):
    response = client.get('/api/buy-signals/buy-score/PETR4')
    data = response.get_json()
    assert data['success'] == True
    assert data['data']['buy_score'] >= 50

def test_zscore_petr4(client):
    response = client.get('/api/buy-signals/zscore/PETR4')
    data = response.get_json()
    assert data['success'] == True

def test_watchlist_top(client):
    response = client.get('/api/buy-signals/watchlist-top')
    data = response.get_json()
    assert data['success'] == True
    assert len(data['data']) <= 10
