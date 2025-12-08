# -*- coding: utf-8 -*-
"""
Exitus - ConfiguracaoAlertaService
Service para gerenciamento de alertas
"""
from decimal import Decimal
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.database import db
from app.models import Usuario, ConfiguracaoAlerta
from app.models.enums_m7 import TipoAlerta, OperadorCondicao, FrequenciaNotificacao

class ConfiguracaoAlertaService:
    """Service para alertas inteligentes"""
    
    @staticmethod
    def criar_alerta(
        usuario_id: str,
        nome: str,
        tipo_alerta: TipoAlerta,
        condicao_valor: Decimal,
        condicao_operador: OperadorCondicao = OperadorCondicao.MAIOR,
        ativo_id: Optional[str] = None,
        canais_entrega: List[str] = None
    ) -> ConfiguracaoAlerta:
        """Cria novo alerta"""
        alerta = ConfiguracaoAlerta(
            usuario_id=usuario_id,
            nome=nome,
            tipo_alerta=tipo_alerta,
            condicao_valor=condicao_valor,
            condicao_operador=condicao_operador,
            ativo_id=ativo_id,
            canais_entrega=canais_entrega or ['email', 'webapp']
        )
        db.session.add(alerta)
        db.session.commit()
        return alerta
    
    @staticmethod
    def listar_alertas_usuario(usuario_id: str) -> List[ConfiguracaoAlerta]:
        """Lista todos os alertas de um usuário"""
        return (db.session.query(ConfiguracaoAlerta)
               .filter_by(usuario_id=usuario_id)
               .order_by(ConfiguracaoAlerta.nome)
               .all())
