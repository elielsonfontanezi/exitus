from app import create_app
from app.database import db
from sqlalchemy import text

def get_parametros_macro(pais, mercado):
    """Carrega parâmetros macroeconômicos por país/mercado COM APP CONTEXT"""
    app = create_app()
    with app.app_context():
        query = text("""
            SELECT taxa_livre_risco, crescimento_medio, custo_capital,
                   inflacao_anual, cap_rate_fii, ytm_rf
            FROM parametros_macro 
            WHERE pais ILIKE :pais AND mercado ILIKE :mercado AND ativo = true
            LIMIT 1
        """)
        
        result = db.session.execute(query, {'pais': pais, 'mercado': mercado}).fetchone()
        
        if result:
            return {
                'taxa_livre_risco': float(result[0] or 0.10),
                'crescimento_medio': float(result[1] or 0.05),
                'custo_capital': float(result[2] or 0.12),
                'inflacao_anual': float(result[3] or 0.03),
                'cap_rate_fii': float(result[4] or 0.08),
                'ytm_rf': float(result[5] or 0.10)
            }
        
        # Fallback Brasil B3
        result = db.session.execute(query, {'pais': 'BR', 'mercado': 'B3'}).fetchone()
        return {
            'taxa_livre_risco': float(result[0] or 0.10),
            'crescimento_medio': float(result[1] or 0.05),
            'custo_capital': float(result[2] or 0.12),
            'inflacao_anual': float(result[3] or 0.03),
            'cap_rate_fii': float(result[4] or 0.08),
            'ytm_rf': float(result[5] or 0.10)
        }
