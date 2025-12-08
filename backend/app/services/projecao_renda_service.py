# -*- coding: utf-8 -*-
from decimal import Decimal
from flask import jsonify
from app.database import db
from app.models import ProjecaoRenda

class ProjecaoRendaService:
    @staticmethod
    def listar_projecoes(usuario_id: str):
        return {'projecoes': [], 'message': 'Nenhuma projeção encontrada'}
