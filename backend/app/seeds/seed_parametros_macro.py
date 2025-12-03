from app import create_app
from app.database import db
from app.models.parametros_macro import ParametrosMacro

app = create_app()
with app.app_context():
    def seed_parametros_macro():
        params = [
            {'pais': 'BR', 'mercado': 'B3', 'taxa_livre_risco': 0.1050, 'crescimento_medio': 0.045, 
             'custo_capital': 0.125, 'inflacao_anual': 0.042, 'cap_rate_fii': 0.085, 'ytm_rf': 0.115},
            {'pais': 'US', 'mercado': 'NYSE', 'taxa_livre_risco': 0.0420, 'crescimento_medio': 0.025, 
             'custo_capital': 0.085, 'inflacao_anual': 0.022, 'cap_rate_fii': 0.065, 'ytm_rf': 0.045},
            {'pais': 'EU', 'mercado': 'Euronext', 'taxa_livre_risco': 0.0280, 'crescimento_medio': 0.018, 
             'custo_capital': 0.072, 'inflacao_anual': 0.020, 'cap_rate_fii': 0.045, 'ytm_rf': 0.032},
            {'pais': 'JP', 'mercado': 'Tokyo', 'taxa_livre_risco': 0.0015, 'crescimento_medio': 0.012, 
             'custo_capital': 0.035, 'inflacao_anual': 0.015, 'cap_rate_fii': 0.035, 'ytm_rf': 0.018},
        ]
        
        for p in params:
            if not ParametrosMacro.query.filter_by(pais=p['pais'], mercado=p['mercado']).first():
                macro = ParametrosMacro(**p)
                db.session.add(macro)
        
        db.session.commit()
        print(f"✅ Seed Parâmetros Macro: {len(params)} mercados")

    seed_parametros_macro()
