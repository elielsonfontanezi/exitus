# -*- coding: utf-8 -*-
"""
Exitus - Service para FonteDados
CRUD e operações de fontes de dados externas
"""

from app.database import db
from app.models.fonte_dados import FonteDados, TipoFonteDados
from datetime import datetime


class FonteDadosService:
    """Service para operações com FonteDados"""
    
    @staticmethod
    def get_all(ativa_only=False):
        """Lista todas as fontes de dados"""
        query = FonteDados.query
        
        if ativa_only:
            query = query.filter_by(ativa=True)
        
        return query.order_by(FonteDados.prioridade, FonteDados.nome).all()
    
    @staticmethod
    def get_by_id(fonte_id):
        """Obtém fonte por ID"""
        return FonteDados.query.get(fonte_id)
    
    @staticmethod
    def get_by_nome(nome):
        """Obtém fonte por nome"""
        return FonteDados.query.filter_by(nome=nome).first()
    
    @staticmethod
    def get_by_tipo(tipo_fonte, ativa_only=False):
        """Lista fontes por tipo"""
        query = FonteDados.query.filter_by(tipo_fonte=tipo_fonte)
        
        if ativa_only:
            query = query.filter_by(ativa=True)
        
        return query.order_by(FonteDados.prioridade, FonteDados.nome).all()
    
    @staticmethod
    def create(data, usuario_id=None):
        """Cria nova fonte de dados"""
        # Verifica duplicata de nome
        existing = FonteDados.query.filter_by(nome=data['nome']).first()
        if existing:
            raise ValueError(f"Fonte de dados '{data['nome']}' já existe")
        
        # Converte string para enum se necessário
        if 'tipo_fonte' in data and isinstance(data['tipo_fonte'], str):
            try:
                data['tipo_fonte'] = TipoFonteDados(data['tipo_fonte'])
            except ValueError:
                raise ValueError(f"Tipo de fonte inválido: {data['tipo_fonte']}")
        
        # Define valores padrão
        if 'prioridade' not in data:
            data['prioridade'] = 100
        if 'ativa' not in data:
            data['ativa'] = True
        if 'requer_autenticacao' not in data:
            data['requer_autenticacao'] = False
        if 'total_consultas' not in data:
            data['total_consultas'] = 0
        if 'total_erros' not in data:
            data['total_erros'] = 0
        
        fonte = FonteDados(**data)
        db.session.add(fonte)
        db.session.commit()
        
        return fonte
    
    @staticmethod
    def update(fonte_id, data):
        """Atualiza fonte existente"""
        fonte = FonteDados.query.get(fonte_id)
        
        if not fonte:
            raise ValueError("Fonte de dados não encontrada")
        
        # Se mudou nome, verifica duplicata
        if 'nome' in data and data['nome'].lower() != fonte.nome.lower():
            existing = FonteDados.query.filter(
                FonteDados.id != fonte_id,
                FonteDados.nome == data['nome']
            ).first()
            
            if existing:
                raise ValueError(f"Fonte de dados '{data['nome']}' já existe")
        
        # Converte string para enum se necessário
        if 'tipo_fonte' in data and isinstance(data['tipo_fonte'], str):
            try:
                data['tipo_fonte'] = TipoFonteDados(data['tipo_fonte'])
            except ValueError:
                raise ValueError(f"Tipo de fonte inválido: {data['tipo_fonte']}")
        
        # Atualiza campos
        for key, value in data.items():
            if hasattr(fonte, key):
                setattr(fonte, key, value)
        
        db.session.commit()
        
        return fonte
    
    @staticmethod
    def delete(fonte_id):
        """Remove fonte de dados"""
        fonte = FonteDados.query.get(fonte_id)
        
        if not fonte:
            raise ValueError("Fonte de dados não encontrada")
        
        db.session.delete(fonte)
        db.session.commit()
        
        return True
    
    @staticmethod
    def registrar_consulta_sucesso(fonte_id):
        """Registra consulta bem-sucedida"""
        fonte = FonteDados.query.get(fonte_id)
        
        if not fonte:
            raise ValueError("Fonte de dados não encontrada")
        
        fonte.registrar_consulta_sucesso()
        db.session.commit()
        
        return fonte
    
    @staticmethod
    def registrar_erro(fonte_id):
        """Registra erro na consulta"""
        fonte = FonteDados.query.get(fonte_id)
        
        if not fonte:
            raise ValueError("Fonte de dados não encontrada")
        
        fonte.registrar_erro()
        db.session.commit()
        
        return fonte
    
    @staticmethod
    def get_ativas_por_prioridade():
        """Obtém fontes ativas ordenadas por prioridade"""
        return FonteDados.query.filter_by(ativa=True).order_by(
            FonteDados.prioridade.asc(), 
            FonteDados.nome.asc()
        ).all()
    
    @staticmethod
    def get_por_tipo_e_prioridade(tipo_fonte):
        """Obtém fontes de um tipo específico ordenadas por prioridade"""
        return FonteDados.query.filter_by(
            tipo_fonte=tipo_fonte, 
            ativa=True
        ).order_by(
            FonteDados.prioridade.asc(), 
            FonteDados.nome.asc()
        ).all()
    
    @staticmethod
    def get_health_summary():
        """Resumo de saúde de todas as fontes ativas"""
        fontes = FonteDados.query.filter_by(ativa=True).all()
        
        summary = {
            'total': len(fontes),
            'healthy': 0,
            'degraded': 0,
            'down': 0,
            'unknown': 0,
            'detalhes': []
        }
        
        for fonte in fontes:
            status = fonte.health_status
            summary[status] += 1
            
            summary['detalhes'].append({
                'id': str(fonte.id),
                'nome': fonte.nome,
                'tipo': fonte.tipo_fonte.value,
                'status': status,
                'taxa_sucesso': round(fonte.taxa_sucesso, 2),
                'total_consultas': fonte.total_consultas,
                'ultima_consulta': fonte.ultima_consulta.isoformat() if fonte.ultima_consulta else None
            })
        
        return summary
