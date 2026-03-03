# -*- coding: utf-8 -*-
"""Exitus - FeriadoMercado Service - CRUD (EXITUS-CRUD-001)"""

from app.database import db
from app.models.feriado_mercado import FeriadoMercado, TipoFeriado
from app.utils.db_utils import safe_commit, safe_delete_commit
import logging

logger = logging.getLogger(__name__)


class FeriadoMercadoService:
    @staticmethod
    def get_all(page=1, per_page=50, pais=None, mercado=None, ano=None):
        query = FeriadoMercado.query
        if pais:
            query = query.filter_by(pais=pais.upper())
        if mercado:
            query = query.filter_by(mercado=mercado.upper())
        if ano:
            query = query.filter(
                db.extract('year', FeriadoMercado.data_feriado) == ano
            )
        return query.order_by(FeriadoMercado.data_feriado.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

    @staticmethod
    def get_by_id(feriado_id):
        return FeriadoMercado.query.get(feriado_id)

    @staticmethod
    def create(data):
        feriado = FeriadoMercado(
            pais=data['pais'].upper(),
            mercado=data.get('mercado', '').upper() if data.get('mercado') else None,
            data_feriado=data['data_feriado'],
            tipo_feriado=TipoFeriado(data['tipo_feriado']),
            nome=data['nome'],
            horario_fechamento=data.get('horario_fechamento'),
            recorrente=data.get('recorrente', False),
            observacoes=data.get('observacoes'),
        )
        db.session.add(feriado)
        safe_commit()
        db.session.refresh(feriado)
        return feriado

    @staticmethod
    def update(feriado_id, data):
        feriado = FeriadoMercado.query.get(feriado_id)
        if not feriado:
            raise ValueError("Feriado não encontrado")

        if 'pais' in data:
            feriado.pais = data['pais'].upper()
        if 'mercado' in data:
            feriado.mercado = data['mercado'].upper() if data['mercado'] else None
        if 'data_feriado' in data:
            feriado.data_feriado = data['data_feriado']
        if 'tipo_feriado' in data:
            feriado.tipo_feriado = TipoFeriado(data['tipo_feriado'])
        if 'nome' in data:
            feriado.nome = data['nome']
        if 'horario_fechamento' in data:
            feriado.horario_fechamento = data['horario_fechamento']
        if 'recorrente' in data:
            feriado.recorrente = data['recorrente']
        if 'observacoes' in data:
            feriado.observacoes = data['observacoes']

        safe_commit()
        return feriado

    @staticmethod
    def delete(feriado_id):
        feriado = FeriadoMercado.query.get(feriado_id)
        if not feriado:
            raise ValueError("Feriado não encontrado")
        safe_delete_commit(feriado)
        return True
