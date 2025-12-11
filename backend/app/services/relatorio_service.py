# -*- coding: utf-8 -*-
"""Exitus - RelatorioService (M7.2)"""
from datetime import date, datetime
from decimal import Decimal
from typing import Dict, List, Optional
from uuid import UUID
from sqlalchemy import func, and_
from app.database import db
from app.models.auditoria_relatorio import AuditoriaRelatorio
from app.models.posicao import Posicao
from app.models.transacao import Transacao
from app.models.provento import Provento
from app.models.ativo import Ativo

class RelatorioService:
    @staticmethod
    def listar_relatorios(usuario_id: UUID, page: int = 1, per_page: int = 10) -> Dict:
        query = AuditoriaRelatorio.query.filter_by(usuario_id=usuario_id).order_by(
            AuditoriaRelatorio.timestamp_criacao.desc()
        )
        total = query.count()
        relatorios = query.offset((page-1)*per_page).limit(per_page).all()
        return {
            "relatorios": [r.to_dict() for r in relatorios],
            "current_page": page,
            "total": total,
            "pages": (total + per_page - 1) // per_page
        }

    @staticmethod
    def obter_relatorio(usuario_id: UUID, relatorio_id: UUID) -> Dict:
        relatorio = AuditoriaRelatorio.query.filter_by(
            id=relatorio_id, usuario_id=usuario_id
        ).first()
        if not relatorio:
            raise ValueError("Relatório não encontrado")
        return relatorio.to_dict()

    @staticmethod
    def gerar_relatorio_portfolio(usuario_id: UUID, filtros: Dict = {}) -> Dict:
        posicoes = Posicao.query.filter_by(usuario_id=usuario_id).filter(
            Posicao.quantidade > 0
        ).all()
        
        if not posicoes:
            return {"message": "Nenhuma posição encontrada", "portfolio": []}
        
        metricas = RelatorioService._calcular_metricas_portfolio(posicoes)
        
        relatorio = AuditoriaRelatorio(
            usuario_id=usuario_id,
            tipo_relatorio="PORTFOLIO",
            filtros=filtros,
            resultado_json={
                "metricas": metricas,
                "posicoes": [p.to_dict_resumo() for p in posicoes]
            }
        )
        db.session.add(relatorio)
        db.session.commit()
        db.session.refresh(relatorio)
        
        return relatorio.to_dict()

    @staticmethod
    def gerar_relatorio_performance(usuario_id: UUID, data_inicio: Optional[date], data_fim: Optional[date], filtros: Dict = {}) -> Dict:
        if not data_inicio or not data_fim:
            raise ValueError("Datas obrigatórias para performance")
        
        transacoes = Transacao.query.filter(
            and_(
                Transacao.usuario_id == usuario_id,
                Transacao.data_operacao >= data_inicio,
                Transacao.data_operacao <= data_fim
            )
        ).order_by(Transacao.data_operacao).all()
        
        posicoes = Posicao.query.filter_by(usuario_id=usuario_id).all()
        proventos = Provento.query.filter_by(usuario_id=usuario_id).all()
        
        resultado = {
            "periodo": f"{data_inicio} a {data_fim}",
            "transacoes": len(transacoes),
            "posicoes": len([p for p in posicoes if p.quantidade > 0]),
            "proventos": len(proventos),
            "patrimonio_final": sum(p.valor_atual or 0 for p in posicoes),
            "rentabilidade": "0%"  # Placeholder
        }
        
        relatorio = AuditoriaRelatorio(
            usuario_id=usuario_id,
            tipo_relatorio="PERFORMANCE",
            data_inicio=data_inicio,
            data_fim=data_fim,
            filtros=filtros,
            resultado_json=resultado
        )
        db.session.add(relatorio)
        db.session.commit()
        db.session.refresh(relatorio)
        
        return relatorio.to_dict()

    @staticmethod
    def _calcular_metricas_portfolio(posicoes: List[Posicao]) -> Dict:
        total_custo = sum(p.custo_total for p in posicoes)
        total_atual = sum(p.valor_atual or Decimal('0') for p in posicoes)
        total_lucro = total_atual - total_custo
        
        rentabilidade = (total_lucro / total_custo * 100) if total_custo > 0 else Decimal('0')
        
        # Alocação por classe
        alocacao_classe = {}
        for p in posicoes:
            ativo = Ativo.query.get(p.ativo_id)
            classe = getattr(ativo, 'classe', 'OUTRO')
            alocacao_classe[classe] = alocacao_classe.get(classe, 0) + float(p.valor_atual or 0)
        
        return {
            "total_custo": float(total_custo),
            "total_atual": float(total_atual),
            "lucro_prejuizo": float(total_lucro),
            "rentabilidade_percentual": float(rentabilidade),
            "alocacao_por_classe": alocacao_classe
        }

    @staticmethod
    def deletar_relatorio(usuario_id: UUID, relatorio_id: UUID) -> bool:
        relatorio = AuditoriaRelatorio.query.filter_by(
            id=relatorio_id, usuario_id=usuario_id
        ).first()
        if not relatorio:
            raise ValueError("Relatório não encontrado")
        db.session.delete(relatorio)
        db.session.commit()
        return True
