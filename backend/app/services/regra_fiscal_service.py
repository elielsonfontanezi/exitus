# -*- coding: utf-8 -*-
"""Exitus - RegraFiscal Service - CRUD (EXITUS-CRUD-001)"""

from decimal import Decimal
from app.database import db
from app.models.regra_fiscal import RegraFiscal, IncidenciaImposto
from app.utils.db_utils import safe_commit, safe_delete_commit
import logging

logger = logging.getLogger(__name__)


class RegraFiscalService:
    @staticmethod
    def get_all(page=1, per_page=50, pais=None, tipo_ativo=None, ativa=None):
        query = RegraFiscal.query
        if pais:
            query = query.filter_by(pais=pais.upper())
        if tipo_ativo:
            query = query.filter_by(tipo_ativo=tipo_ativo.upper())
        if ativa is not None:
            query = query.filter_by(ativa=ativa)
        return query.order_by(RegraFiscal.pais, RegraFiscal.tipo_ativo).paginate(
            page=page, per_page=per_page, error_out=False
        )

    @staticmethod
    def get_by_id(regra_id):
        return RegraFiscal.query.get(regra_id)

    @staticmethod
    def create(data):
        regra = RegraFiscal(
            pais=data['pais'].upper(),
            tipo_ativo=data.get('tipo_ativo', '').upper() if data.get('tipo_ativo') else None,
            tipo_operacao=data.get('tipo_operacao', '').upper() if data.get('tipo_operacao') else None,
            aliquota_ir=Decimal(str(data['aliquota_ir'])),
            valor_isencao=Decimal(str(data['valor_isencao'])) if data.get('valor_isencao') is not None else None,
            incide_sobre=IncidenciaImposto(data['incide_sobre']),
            descricao=data['descricao'],
            vigencia_inicio=data['vigencia_inicio'],
            vigencia_fim=data.get('vigencia_fim'),
            ativa=data.get('ativa', True),
        )
        db.session.add(regra)
        safe_commit()
        db.session.refresh(regra)
        return regra

    @staticmethod
    def update(regra_id, data):
        regra = RegraFiscal.query.get(regra_id)
        if not regra:
            raise ValueError("Regra fiscal não encontrada")

        if 'pais' in data:
            regra.pais = data['pais'].upper()
        if 'tipo_ativo' in data:
            regra.tipo_ativo = data['tipo_ativo'].upper() if data['tipo_ativo'] else None
        if 'tipo_operacao' in data:
            regra.tipo_operacao = data['tipo_operacao'].upper() if data['tipo_operacao'] else None
        if 'aliquota_ir' in data:
            regra.aliquota_ir = Decimal(str(data['aliquota_ir']))
        if 'valor_isencao' in data:
            regra.valor_isencao = Decimal(str(data['valor_isencao'])) if data['valor_isencao'] is not None else None
        if 'incide_sobre' in data:
            regra.incide_sobre = IncidenciaImposto(data['incide_sobre'])
        if 'descricao' in data:
            regra.descricao = data['descricao']
        if 'vigencia_inicio' in data:
            regra.vigencia_inicio = data['vigencia_inicio']
        if 'vigencia_fim' in data:
            regra.vigencia_fim = data['vigencia_fim']
        if 'ativa' in data:
            regra.ativa = data['ativa']

        safe_commit()
        return regra

    @staticmethod
    def delete(regra_id):
        regra = RegraFiscal.query.get(regra_id)
        if not regra:
            raise ValueError("Regra fiscal não encontrada")
        safe_delete_commit(regra)
        return True
