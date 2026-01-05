# -*- coding: utf-8 -*-
"""
Exitus Backend M4 - Application Factory
Sistema de Gestão e Análise de Investimentos
Módulos: M2 (API REST) + M3 (Portfolio) + M4 (Buy Signals + Fiscais) + M7.4 (Alertas) + M7.5 (Cotações)
"""
from flask import Flask
from flask.json.provider import DefaultJSONProvider
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .config import Config
from .database import init_db
from decimal import Decimal
from uuid import UUID


class DecimalJSONProvider(DefaultJSONProvider):
    """Custom JSON provider para serializar Decimal e UUID"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, UUID):
            return str(obj)
        return super().default(obj)


def create_app(testing=False):
    """
    Factory para criar a aplicação Flask do Exitus Backend.

    Args:
        testing (bool): Modo de teste (configurações específicas)

    Returns:
        Flask: Aplicação Flask configurada com todos os módulos
    """
    app = Flask(__name__)

    # Carregar configurações
    app.config.from_object(Config)

    # Configurações JWT
    app.config['JWT_SECRET_KEY'] = app.config.get('SECRET_KEY', 'super-secret-key-mudar-no-env')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600  # 1 hora
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = 2592000  # 30 dias

    # Custom JSON Provider (Decimal/UUID)
    app.json = DecimalJSONProvider(app)

    # Inicializar extensões
    jwt = JWTManager(app)

    # CORS configurado para frontend
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:8080", "http://127.0.0.1:8080"],
            "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"]
        }
    })

    # Inicializar banco de dados
    init_db(app)

    # ============================================
    # HEALTH CHECK
    # ============================================
    @app.route('/health')
    def health():
        return {
            "env": app.config.get('FLASK_ENV', 'development'),
            "service": "exitus-backend",
            "status": "ok",
            "module": "M4 - Buy Signals + Fiscais + Portfolio + Alertas ✅"
        }

    # ============================================
    # M2 - API REST BÁSICA (Core)
    # ============================================
    from .blueprints.auth.routes import bp as auth_bp
    app.register_blueprint(auth_bp)

    from .blueprints.usuarios.routes import bp as usuarios_bp
    app.register_blueprint(usuarios_bp)

    from .blueprints.corretoras.routes import bp as corretoras_bp
    app.register_blueprint(corretoras_bp)

    from .blueprints.ativos.routes import bp as ativos_bp
    app.register_blueprint(ativos_bp)

    from .blueprints.transacoes.routes import bp as transacoes_bp
    app.register_blueprint(transacoes_bp)

    # ============================================
    # M3 - GESTÃO DE PORTFOLIO
    # ============================================
    from .blueprints.posicao_blueprint import posicao_bp
    app.register_blueprint(posicao_bp)

    from .blueprints.provento_blueprint import provento_bp
    app.register_blueprint(provento_bp)

    from .blueprints.movimentacao_blueprint import movimentacao_bp
    app.register_blueprint(movimentacao_bp)

    from .blueprints.evento_corporativo_blueprint import evento_bp
    app.register_blueprint(evento_bp)

    # 🆕 Portfolio consolidado (M7)
    # 🆕 Portfolio consolidado (M7)
    try:
        # CORREÇÃO: Ponto no início (.) e importando 'bp' como 'portfolio_bp'
        from .blueprints.portfolio_blueprint import portfolio_bp
        app.register_blueprint(portfolio_bp)

        print("✅ Portfolio blueprint registrado: /api/portfolios")
    except ImportError as e:
        print(f"⚠️  Portfolio blueprint não encontrado: {e}")
    except Exception as e:
        print(f"⚠️  Erro genérico ao registrar Portfolio: {e}")


    # ============================================
    # M4 - BUY SIGNALS + FERIADOS/FONTES/REGRAS/CÁLCULOS
    # ============================================

    # M4.1 - Feriados
    try:
        from .blueprints.feriadosblueprint import feriadosbp
        app.register_blueprint(feriadosbp)
        print("✅ Feriados blueprint registrado: /api/feriados")
    except ImportError as e:
        print(f"⚠️  Feriados blueprint não encontrado: {e}")

    # M4.2 - Fontes de Dados
    try:
        from .blueprints.fontesblueprint import fontesbp
        app.register_blueprint(fontesbp)
        print("✅ Fontes blueprint registrado: /api/fontes")
    except ImportError as e:
        print(f"⚠️  Fontes blueprint não encontrado: {e}")

    # M4.3 - Regras Fiscais
    try:
        from .blueprints.regras_fiscaisblueprint import regrasbp
        app.register_blueprint(regrasbp)
        print("✅ Regras fiscais blueprint registrado: /api/regras-fiscais")
    except ImportError as e:
        print(f"⚠️  Regras fiscais blueprint não encontrado: {e}")

    # M4.4 - Cálculos Financeiros
    try:
        from .blueprints.calculos_blueprint import calculos_bp
        app.register_blueprint(calculos_bp)
        print("✅ Cálculos blueprint registrado: /api/calculos")
    except ImportError as e:
        print(f"⚠️  Cálculos blueprint não encontrado: {e}")

    # M4.5 - Buy Signals (Análise Fundamentalista)
    try:
        from .blueprints.buy_signals_blueprint import buy_signals_bp
        app.register_blueprint(buy_signals_bp, url_prefix='/api/buy-signals')
        print("✅ Buy Signals blueprint registrado: /api/buy-signals/*")
    except ImportError as e:
        print(f"⚠️  Buy Signals blueprint não encontrado: {e}")

    # ============================================
    # M7.4 - ALERTAS (NOVO!)
    # ============================================
    try:
        from .blueprints.alertas import bp as alertas_bp
        app.register_blueprint(alertas_bp)
        print("✅ Alertas blueprint registrado: /api/alertas")
    except ImportError as e:
        print(f"⚠️  Alertas blueprint não encontrado: {e}")

    # ============================================
    # M7.5 - COTAÇÕES EM TEMPO REAL
    # ============================================
    try:
        from .blueprints.cotacoes_blueprint import cotacoes_bp
        app.register_blueprint(cotacoes_bp, url_prefix='/api/cotacoes')
        print("✅ Cotações blueprint registrado: /api/cotacoes/*")
    except ImportError as e:
        print(f"⚠️  Cotações blueprint não encontrado: {e}")

    # ============================================
    # M7 - RELATÓRIOS E ANÁLISES (Legacy - Opcional)
    # ============================================
    try:
        from .blueprints.relatorios_blueprint import relatorios_bp
        app.register_blueprint(relatorios_bp)
    except ImportError:
        pass

    try:
        from .blueprints.projecoes_blueprint import projecoes_bp
        app.register_blueprint(projecoes_bp)
    except ImportError:
        pass

    try:
        from .blueprints.performance_blueprint import performance_bp
        app.register_blueprint(performance_bp)
    except ImportError:
        pass

    # ============================================
    # LOGS DE INICIALIZAÇÃO
    # ============================================
    print("=" * 60)
    print("🚀 Exitus Backend M4 - Inicialização Completa")
    print("=" * 60)
    print(f"📍 Environment: {app.config.get('FLASK_ENV')}")
    print(f"🔐 JWT Secret: {'*' * 16}")
    print(f"🌐 CORS: http://localhost:8080")
    print("")
    print("✅ M2 - API REST (5 blueprints):")
    print("   - auth, usuarios, corretoras, ativos, transacoes")
    print("")
    print("✅ M3 - Portfolio (5 blueprints):")
    print("   - posicoes, proventos, movimentacoes, eventos, portfolio")
    print("")
    print("✅ M4 - Buy Signals + Fiscais (5 blueprints):")
    print("   - feriados, fontes, regras-fiscais, calculos, buy-signals")
    print("")
    print("✅ M7.4 - Alertas (1 blueprint):")
    print("   - alertas")
    print("")
    print("✅ M7.5 - Cotações (1 blueprint):")
    print("   - cotacoes")
    print("")
    print("📊 Total de Blueprints Ativos: Verifique os logs ✅ acima")
    print("=" * 60)

    return app
