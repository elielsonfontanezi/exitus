# -*- coding: utf-8 -*-
"""
Exitus - EventoCorporativo Service M3.3 (Corrigido)
"""
from app.database import db
from app.models import EventoCorporativo, Posicao, Ativo
from app.models.evento_corporativo import TipoEventoCorporativo
from app.utils.db_utils import safe_commit, safe_delete_commit
from app.utils.exceptions import NotFoundError
from app.utils.tenant import filter_by_assessora
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
    def get_by_id(evento_id):
        return db.session.get(EventoCorporativo, evento_id)

    @staticmethod
    def create(data):
        try:
            evento = EventoCorporativo(
                ativo_id=data['ativo_id'],
                tipo_evento=TipoEventoCorporativo(data['tipo_evento']),
                data_evento=data['data_evento'],
                descricao=data['descricao'],
                data_com=data.get('data_com'),
                proporcao=data.get('proporcao'),
                ativo_novo_id=data.get('ativo_novo_id'),
                observacoes=data.get('observacoes'),
            )
            db.session.add(evento)
            safe_commit()
            db.session.refresh(evento)
            return evento
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao criar evento: {e}")
            raise

    @staticmethod
    def update(evento_id, data):
        try:
            evento = db.session.get(EventoCorporativo, evento_id)
            if not evento:
                raise NotFoundError("Evento corporativo não encontrado")

            if 'tipo_evento' in data:
                evento.tipo_evento = TipoEventoCorporativo(data['tipo_evento'])
            if 'data_evento' in data:
                evento.data_evento = data['data_evento']
            if 'descricao' in data:
                evento.descricao = data['descricao']
            if 'data_com' in data:
                evento.data_com = data['data_com']
            if 'proporcao' in data:
                evento.proporcao = data['proporcao']
            if 'ativo_novo_id' in data:
                evento.ativo_novo_id = data['ativo_novo_id']
            if 'observacoes' in data:
                evento.observacoes = data['observacoes']

            safe_commit()
            return evento
        except ValueError:
            raise
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao atualizar evento: {e}")
            raise

    @staticmethod
    def delete(evento_id):
        evento = db.session.get(EventoCorporativo, evento_id)
        if not evento:
            raise NotFoundError("Evento corporativo não encontrado")
        safe_delete_commit(evento)
        return True

    @staticmethod
    def aplicar_evento(evento_id, usuario_id):
        try:
            evento = db.session.get(EventoCorporativo, evento_id)
            if not evento:
                raise NotFoundError("Evento não encontrado")

            query = Posicao.query.filter_by(
                usuario_id=usuario_id, 
                ativo_id=evento.ativo_id
            )
            query = filter_by_assessora(query, Posicao)
            posicao = query.first()

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
