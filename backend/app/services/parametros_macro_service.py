# -*- coding: utf-8 -*-
"""
Exitus - Service para ParametrosMacro
CRUD e consultas de parâmetros macroeconômicos
"""

from app.database import db
from app.models.parametros_macro import ParametrosMacro


class ParametrosMacroService:
    """Service para operações com ParametrosMacro"""
    
    @staticmethod
    def get_all(ativo_only=True):
        """Lista todos os parâmetros macroeconômicos"""
        query = ParametrosMacro.query
        
        if ativo_only:
            query = query.filter_by(ativo=True)
        
        return query.order_by(ParametrosMacro.pais, ParametrosMacro.mercado).all()
    
    @staticmethod
    def get_by_id(param_id):
        """Obtém parâmetro por ID"""
        return ParametrosMacro.query.get(param_id)
    
    @staticmethod
    def get_by_pais_mercado(pais, mercado, ativo_only=True):
        """Obtém parâmetro por país/mercado"""
        query = ParametrosMacro.query.filter_by(pais=pais.upper(), mercado=mercado)
        
        if ativo_only:
            query = query.filter_by(ativo=True)
        
        return query.first()
    
    @staticmethod
    def create(data):
        """Cria novo parâmetro macroeconômico"""
        # Normaliza país para uppercase
        data['pais'] = data['pais'].upper()
        
        # Verifica duplicata
        existing = ParametrosMacro.query.filter_by(
            pais=data['pais'], 
            mercado=data['mercado']
        ).first()
        
        if existing:
            raise ValueError(f"Parâmetros para {data['pais']}/{data['mercado']} já existem")
        
        parametro = ParametrosMacro(**data)
        db.session.add(parametro)
        db.session.commit()
        
        return parametro
    
    @staticmethod
    def update(param_id, data):
        """Atualiza parâmetro existente"""
        parametro = ParametrosMacro.query.get(param_id)
        
        if not parametro:
            raise ValueError("Parâmetro não encontrado")
        
        # Normaliza país se fornecido
        if 'pais' in data:
            data['pais'] = data['pais'].upper()
        
        # Se mudou país/mercado, verifica duplicata
        if 'pais' in data or 'mercado' in data:
            pais = data.get('pais', parametro.pais)
            mercado = data.get('mercado', parametro.mercado)
            
            duplicate = ParametrosMacro.query.filter(
                ParametrosMacro.id != param_id,
                ParametrosMacro.pais == pais,
                ParametrosMacro.mercado == mercado
            ).first()
            
            if duplicate:
                raise ValueError(f"Parâmetros para {pais}/{mercado} já existem")
        
        # Atualiza campos
        for key, value in data.items():
            if hasattr(parametro, key):
                setattr(parametro, key, value)
        
        db.session.commit()
        
        return parametro
    
    @staticmethod
    def delete(param_id):
        """Remove parâmetro"""
        parametro = ParametrosMacro.query.get(param_id)
        
        if not parametro:
            raise ValueError("Parâmetro não encontrado")
        
        db.session.delete(parametro)
        db.session.commit()
        
        return True
    
    @staticmethod
    def get_parametros_dict(pais, mercado):
        """
        Obtém parâmetros como dicionário (compatível com código legado)
        Mantém a mesma interface da função original para não quebrar dependências
        """
        # Tenta buscar país/mercado específico
        parametro = ParametrosMacroService.get_by_pais_mercado(pais, mercado, ativo_only=True)
        
        if parametro:
            return {
                'taxa_livre_risco': float(parametro.taxa_livre_risco or 0.10),
                'crescimento_medio': float(parametro.crescimento_medio or 0.05),
                'custo_capital': float(parametro.custo_capital or 0.12),
                'inflacao_anual': float(parametro.inflacao_anual or 0.03),
                'cap_rate_fii': float(parametro.cap_rate_fii or 0.08),
                'ytm_rf': float(parametro.ytm_rf or 0.10)
            }
        
        # Fallback Brasil B3
        parametro_br = ParametrosMacroService.get_by_pais_mercado('BR', 'B3', ativo_only=True)
        if parametro_br:
            return {
                'taxa_livre_risco': float(parametro_br.taxa_livre_risco or 0.10),
                'crescimento_medio': float(parametro_br.crescimento_medio or 0.05),
                'custo_capital': float(parametro_br.custo_capital or 0.12),
                'inflacao_anual': float(parametro_br.inflacao_anual or 0.03),
                'cap_rate_fii': float(parametro_br.cap_rate_fii or 0.08),
                'ytm_rf': float(parametro_br.ytm_rf or 0.10)
            }
        
        # Defaults hardcoded — tabela parametros_macro vazia (ex: banco de teste)
        return {
            'taxa_livre_risco': 0.105,
            'crescimento_medio': 0.05,
            'custo_capital': 0.12,
            'inflacao_anual': 0.045,
            'cap_rate_fii': 0.08,
            'ytm_rf': 0.105
        }


# Mantém função legada para compatibilidade com código existente
def get_parametros_macro(pais, mercado):
    """Função legada para compatibilidade"""
    return ParametrosMacroService.get_parametros_dict(pais, mercado)
