# -*- coding: utf-8 -*-
"""
Exitus - EventoCorporativo Service M3.3 (Corrigido)
"""
from app.database import db
from app.models import EventoCorporativo, Posicao, Ativo
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class EventoCorporativoService:
    @staticmethod
    def get_all(page=1, per_page=50, ativo_id=None):
        try:
            query = EventoCorporativo.query
            if ativo_id:
                query = query.filter_by(ativo_id=ativo_id)
            
            # CORRIGIDO: data_aprovacao -> data_evento
            return query.order_by(EventoCorporativo.data_evento.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
        except Exception as e:
            logger.error(f"Erro ao listar eventos: {e}")
            raise

    @staticmethod
    def aplicar_evento(evento_id, usuario_id):
        try:
            evento = EventoCorporativo.query.get(evento_id)
            if not evento:
                raise ValueError("Evento não encontrado")

            posicao = Posicao.query.filter_by(
                usuario_id=usuario_id, 
                ativo_id=evento.ativo_id
            ).first()

            if not posicao:
                return {"status": "ignored", "message": "Usuário não possui posição neste ativo"}

            fator = Decimal('1')
            if evento.proporcao and ':' in str(evento.proporcao):
                try:
                    a, b = str(evento.proporcao).split(':')
                    if float(a) == 1:
                        fator = Decimal(b)
                    elif float(b) == 1:
                        fator = Decimal('1') / Decimal(a)
                except:
                    pass

            tipo = str(evento.tipo_evento).upper()
            qtd_antes = posicao.quantidade
            pm_antes = posicao.preco_medio

            if tipo in ['DESDOBRAMENTO', 'SPLIT', 'BONIFICACAO']:
                posicao.quantidade = qtd_antes * fator
                posicao.preco_medio = pm_antes / fator
                
            elif tipo in ['GRUPAMENTO', 'INPLIT']:
                if fator > 1:
                     posicao.quantidade = qtd_antes / fator
                     posicao.preco_medio = pm_antes * fator
                else:
                     posicao.quantidade = qtd_antes * fator
                     posicao.preco_medio = pm_antes / fator

            db.session.commit()
            
            return {
                "status": "applied",
                "ativo": str(evento.ativo_id), # Simplificado
                "antes": {"qtd": float(qtd_antes), "pm": float(pm_antes)},
                "depois": {"qtd": float(posicao.quantidade), "pm": float(posicao.preco_medio)}
            }

        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao aplicar evento: {e}")
            raise
