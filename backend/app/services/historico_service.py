"""
Serviço para gerenciar histórico de preços dos ativos.
Implementa lazy loading: busca da API sob demanda e cacheia no PostgreSQL.
"""

from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import List, Optional
import logging

from app.database import db
from app.models.ativo import Ativo
from app.models.historico_preco import HistoricoPreco
from app.services.cotacoes_service import CotacoesService

logger = logging.getLogger(__name__)


class HistoricoService:
    """Serviço para popular e consultar histórico de preços."""
    
    @staticmethod
    def obter_ou_criar_historico(ativo_id: str, dias: int = 90) -> List[HistoricoPreco]:
        """
        Retorna histórico do banco ou busca da API se insuficiente.
        
        Args:
            ativo_id: UUID do ativo
            dias: Número de dias de histórico necessários
            
        Returns:
            Lista de HistoricoPreco ordenada por data DESC
        """
        # 1. Verificar quantos registros existem
        count = HistoricoPreco.query.filter_by(ativoid=ativo_id).count()
        threshold = int(dias * 0.8)  # 80% dos dias solicitados
        
        # 2. Se insuficiente, popular da API
        if count < threshold:
            logger.info(f"Histórico insuficiente ({count}/{dias} dias). Populando...")
            sucesso = HistoricoService.popular_historico_ativo(ativo_id, dias=dias)
            
            if not sucesso:
                logger.warning(f"Falha ao popular histórico do ativo {ativo_id}")
        
        # 3. Retornar dados do banco
        return HistoricoPreco.query\
            .filter_by(ativoid=ativo_id)\
            .order_by(HistoricoPreco.data.desc())\
            .limit(dias)\
            .all()
    
    @staticmethod
    def popular_historico_ativo(ativo_id: str, dias: int = 365) -> bool:
        """
        Busca histórico da API e salva no banco.
        
        Args:
            ativo_id: UUID do ativo
            dias: Número de dias retroativos
            
        Returns:
            True se sucesso, False se falha
        """
        try:
            # 1. Buscar ativo
            ativo = Ativo.query.get(ativo_id)
            if not ativo:
                logger.error(f"Ativo {ativo_id} não encontrado")
                return False
            
            logger.info(f"Populando histórico: {ativo.ticker} ({dias} dias)")
            
            # 2. Calcular período
            data_fim = date.today()
            data_inicio = data_fim - timedelta(days=dias)
            
            # 3. Buscar dados da API
            cotacoes_service = CotacoesService()
            # historico_api = cotacoes_service.buscar_historico(
            #     ticker=ativo.ticker,
            #     data_inicio=data_inicio,
            #     data_fim=data_fim
            # )
            historico_api = cotacoes_service.buscar_historico(
                ticker=ativo.ticker,
                data_inicio=data_inicio,
                data_fim=data_fim,
                mercado=ativo.mercado
            )
                        
            if not historico_api:
                logger.warning(f"API não retornou dados para {ativo.ticker}")
                return False
            
            # 4. Salvar no banco (upsert)
            registros_inseridos = 0
            registros_atualizados = 0
            
            for registro in historico_api:
                historico = HistoricoPreco.query.filter_by(
                    ativoid=ativo_id,
                    data=registro['data']
                ).first()
                
                if historico:
                    # Atualizar registro existente
                    historico.preco_abertura = registro.get('abertura')
                    historico.preco_fechamento = registro['fechamento']
                    historico.preco_minimo = registro.get('minimo')
                    historico.preco_maximo = registro.get('maximo')
                    historico.volume = registro.get('volume')
                    historico.updatedat = datetime.utcnow()
                    registros_atualizados += 1
                else:
                    # Criar novo registro
                    historico = HistoricoPreco(
                        ativoid=ativo_id,
                        data=registro['data'],
                        preco_abertura=registro.get('abertura'),
                        preco_fechamento=registro['fechamento'],
                        preco_minimo=registro.get('minimo'),
                        preco_maximo=registro.get('maximo'),
                        volume=registro.get('volume')
                    )
                    db.session.add(historico)
                    registros_inseridos += 1
            
            # 5. Commit
            db.session.commit()
            
            logger.info(
                f"Histórico salvo: {ativo.ticker} - "
                f"{registros_inseridos} inseridos, {registros_atualizados} atualizados"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao popular histórico: {str(e)}", exc_info=True)
            db.session.rollback()
            return False
    
    @staticmethod
    def popular_todos_ativos(dias: int = 365, apenas_ativos: bool = True) -> dict:
        """
        Popula histórico de todos os ativos do sistema.
        
        Args:
            dias: Número de dias retroativos
            apenas_ativos: Se True, popula apenas ativos com posições abertas
            
        Returns:
            Dict com estatísticas da operação
        """
        query = Ativo.query
        
        if apenas_ativos:
            # Filtrar apenas ativos com posições
            query = query.join(Ativo.posicoes).distinct()
        
        ativos = query.all()
        
        stats = {
            'total': len(ativos),
            'sucesso': 0,
            'falha': 0,
            'erros': []
        }
        
        logger.info(f"Iniciando população de {stats['total']} ativos...")
        
        for ativo in ativos:
            try:
                if HistoricoService.popular_historico_ativo(str(ativo.id), dias=dias):
                    stats['sucesso'] += 1
                else:
                    stats['falha'] += 1
                    stats['erros'].append(f"{ativo.ticker}: Falha na API")
            except Exception as e:
                stats['falha'] += 1
                stats['erros'].append(f"{ativo.ticker}: {str(e)}")
        
        logger.info(
            f"População concluída: {stats['sucesso']} sucesso, "
            f"{stats['falha']} falhas"
        )
        
        return stats
