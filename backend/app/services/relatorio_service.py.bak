# backend/app/services/relatorio_service.py

from datetime import date
from typing import Dict, Any, Optional

from app.models import TipoRelatorio, FormatoExport
from app.services.auditoria_relatorio_service import AuditoriaRelatorioService
from app.services.relatorio_performance_service import RelatorioPerformanceService
# futuramente: from app.services.projecao_renda_service import ProjecaoRendaService
# futuramente: from app.services.analise_service import AnaliseService


class RelatorioService:
    @staticmethod
    def gerar_relatorio_performance(
        usuario_id: str,
        periodo_inicio: str,
        periodo_fim: str,
        formato_export: FormatoExport = FormatoExport.VISUALIZACAO,
        filtros: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Gera relatório de performance para um usuário em um período
        e registra auditoria.
        """
        # 1) Gerar dados de performance (ainda com cálculo simplificado)
        resultado_perf = RelatorioPerformanceService.calcular_performance(
            usuario_id=usuario_id,
            periodo_inicio=periodo_inicio,
            periodo_fim=periodo_fim,
        )

        # 2) Registrar auditoria
        data_inicio = date.fromisoformat(periodo_inicio)
        data_fim = date.fromisoformat(periodo_fim)

        AuditoriaRelatorioService.registrar_geracao(
            usuario_id=usuario_id,
            tipo_relatorio=TipoRelatorio.PERFORMANCE,
            data_inicio=data_inicio,
            data_fim=data_fim,
            filtros=filtros or {},
            resultado_json=resultado_perf,
            formato_export=formato_export,
            chave_api_auditoria=None,
        )

        return resultado_perf

    @staticmethod
    def listar_auditoria(usuario_id: str, limite: int = 50):
        """
        Retorna histórico de relatórios gerados para o usuário.
        """
        return AuditoriaRelatorioService.listar_por_usuario(
            usuario_id=usuario_id,
            tipo_relatorio=None,
            limite=limite,
        )
