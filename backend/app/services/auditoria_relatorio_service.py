# -*- coding: utf-8 -*-
from flask import jsonify
from app.database import db
from app.models import AuditoriaRelatorio

class AuditoriaRelatorioService:
    @staticmethod
    def listar_por_usuario(usuario_id: str):
        return {'relatorios': [], 'message': 'Nenhum relatório encontrado'}
