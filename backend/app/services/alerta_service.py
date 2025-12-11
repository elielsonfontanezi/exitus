# -*- coding: utf-8 -*-
"""
Exitus - AlertaService (M7.2)
Service para validação e gestão de alertas inteligentes
"""

from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import and_, or_

from app.database import db
from app.models.configuracao_alerta import ConfiguracaoAlerta
from app.models.ativo import Ativo
from app.models.posicao import Posicao
from app.models.provento import Provento


class AlertaService:
    """Service para operações de alertas personalizados."""

    @staticmethod
    def listar_alertas(
        usuario_id: UUID,
        ativo_id: Optional[UUID] = None,
        apenas_ativos: bool = True
    ) -> List[Dict]:
        """
        Lista alertas do usuário com filtros opcionais.
        
        Args:
            usuario_id: ID do usuário
            ativo_id: Filtrar por ativo específico (opcional)
            apenas_ativos: Se True, retorna apenas alertas ativos
            
        Returns:
            Lista de dicts com alertas
        """
        query = ConfiguracaoAlerta.query.filter_by(usuario_id=usuario_id)
        
        if ativo_id:
            query = query.filter_by(ativo_id=ativo_id)
        
        if apenas_ativos:
            query = query.filter_by(ativo=True)
        
        alertas = query.order_by(ConfiguracaoAlerta.timestamp_criacao.desc()).all()
        
        return [a.to_dict() for a in alertas]

    @staticmethod
    def obter_alerta(usuario_id: UUID, alerta_id: UUID) -> Dict:
        """
        Obtém alerta específico por ID.
        
        Args:
            usuario_id: ID do usuário proprietário
            alerta_id: ID do alerta
            
        Returns:
            Dict com dados do alerta
            
        Raises:
            ValueError: Se alerta não encontrado
        """
        alerta = ConfiguracaoAlerta.query.filter_by(
            id=alerta_id,
            usuario_id=usuario_id
        ).first()
        
        if not alerta:
            raise ValueError("Alerta não encontrado")
        
        return alerta.to_dict()

    @staticmethod
    def criar_alerta(usuario_id: UUID, dados: Dict) -> Dict:
        """
        Cria novo alerta.
        
        Args:
            usuario_id: ID do usuário
            dados: Dict com campos:
                - nome: str (obrigatório)
                - tipo_alerta: str (obrigatório)
                - condicao_valor: Decimal (obrigatório)
                - condicao_operador: str (default: 'MAIOR')
                - condicao_valor2: Decimal (opcional, para ENTRE)
                - ativo_id: UUID (opcional)
                - portfolio_id: UUID (opcional)
                - frequencia_notificacao: str (default: 'IMEDIATA')
                - canais_entrega: list (default: ['email', 'webapp'])
                
        Returns:
            Dict com alerta criado
            
        Raises:
            ValueError: Se dados inválidos
        """
        # Validações
        if not dados.get('nome'):
            raise ValueError("Nome do alerta é obrigatório")
        
        if not dados.get('tipo_alerta'):
            raise ValueError("Tipo de alerta é obrigatório")
        
        if 'condicao_valor' not in dados:
            raise ValueError("Valor da condição é obrigatório")
        
        # Validar operador ENTRE
        operador = dados.get('condicao_operador', 'MAIOR')
        if operador == 'ENTRE' and 'condicao_valor2' not in dados:
            raise ValueError("Operador ENTRE requer condicao_valor2")
        
        # Criar alerta
        alerta = ConfiguracaoAlerta(
            usuario_id=usuario_id,
            nome=dados['nome'],
            tipo_alerta=dados['tipo_alerta'],
            condicao_valor=Decimal(str(dados['condicao_valor'])),
            condicao_operador=operador,
            condicao_valor2=Decimal(str(dados['condicao_valor2'])) if dados.get('condicao_valor2') else None,
            ativo_id=dados.get('ativo_id'),
            portfolio_id=dados.get('portfolio_id'),
            frequencia_notificacao=dados.get('frequencia_notificacao', 'IMEDIATA'),
            canais_entrega=dados.get('canais_entrega', ['email', 'webapp']),
            ativo=True
        )
        
        db.session.add(alerta)
        db.session.commit()
        db.session.refresh(alerta)
        
        return alerta.to_dict()

    @staticmethod
    def atualizar_alerta(usuario_id: UUID, alerta_id: UUID, dados: Dict) -> Dict:
        """
        Atualiza alerta existente.
        
        Args:
            usuario_id: ID do usuário proprietário
            alerta_id: ID do alerta
            dados: Dict com campos a atualizar
            
        Returns:
            Dict com alerta atualizado
            
        Raises:
            ValueError: Se alerta não encontrado
        """
        alerta = ConfiguracaoAlerta.query.filter_by(
            id=alerta_id,
            usuario_id=usuario_id
        ).first()
        
        if not alerta:
            raise ValueError("Alerta não encontrado")
        
        # Atualizar campos permitidos
        campos_permitidos = [
            'nome', 'condicao_valor', 'condicao_operador', 'condicao_valor2',
            'ativo', 'frequencia_notificacao', 'canais_entrega'
        ]
        
        for campo in campos_permitidos:
            if campo in dados:
                valor = dados[campo]
                if campo in ['condicao_valor', 'condicao_valor2'] and valor is not None:
                    valor = Decimal(str(valor))
                setattr(alerta, campo, valor)
        
        db.session.commit()
        db.session.refresh(alerta)
        
        return alerta.to_dict()

    @staticmethod
    def deletar_alerta(usuario_id: UUID, alerta_id: UUID) -> bool:
        """
        Deleta alerta.
        
        Args:
            usuario_id: ID do usuário proprietário
            alerta_id: ID do alerta
            
        Returns:
            True se deletado com sucesso
            
        Raises:
            ValueError: Se alerta não encontrado
        """
        alerta = ConfiguracaoAlerta.query.filter_by(
            id=alerta_id,
            usuario_id=usuario_id
        ).first()
        
        if not alerta:
            raise ValueError("Alerta não encontrado")
        
        db.session.delete(alerta)
        db.session.commit()
        
        return True

    @staticmethod
    def validar_condicao(alerta: ConfiguracaoAlerta, valor_atual: Decimal) -> bool:
        """
        Valida se condição do alerta foi atingida.
        
        Args:
            alerta: Objeto ConfiguracaoAlerta
            valor_atual: Valor atual para comparação
            
        Returns:
            True se condição foi atingida
        """
        operador = alerta.condicao_operador.value if hasattr(alerta.condicao_operador, 'value') else alerta.condicao_operador
        threshold = alerta.condicao_valor
        
        if operador == 'MAIOR':
            return valor_atual > threshold
        elif operador == 'MAIOR_IGUAL':
            return valor_atual >= threshold
        elif operador == 'MENOR':
            return valor_atual < threshold
        elif operador == 'MENOR_IGUAL':
            return valor_atual <= threshold
        elif operador == 'IGUAL':
            return valor_atual == threshold
        elif operador == 'DIFERENTE':
            return valor_atual != threshold
        elif operador == 'ENTRE':
            if alerta.condicao_valor2 is None:
                return False
            return threshold <= valor_atual <= alerta.condicao_valor2
        
        return False

    @staticmethod
    def processar_alertas_batch(usuario_id: UUID, limite: int = 50) -> Dict:
        """
        Processa lote de alertas ativos do usuário.
        
        Args:
            usuario_id: ID do usuário
            limite: Máximo de alertas a processar (default: 50)
            
        Returns:
            Dict com resultados do processamento
        """
        # Buscar alertas ativos
        alertas = ConfiguracaoAlerta.query.filter_by(
            usuario_id=usuario_id,
            ativo=True
        ).limit(limite).all()
        
        resultados = {
            'total_processados': 0,
            'alertas_disparados': [],
            'alertas_inativos': [],
            'erros': []
        }
        
        for alerta in alertas:
            try:
                # Obter valor atual baseado no tipo de alerta
                valor_atual = AlertaService._obter_valor_atual(alerta)
                
                if valor_atual is None:
                    resultados['alertas_inativos'].append(str(alerta.id))
                    continue
                
                # Validar condição
                if AlertaService.validar_condicao(alerta, valor_atual):
                    # Registrar acionamento
                    alerta.timestamp_ultimo_acionamento = datetime.utcnow()
                    db.session.commit()
                    
                    resultados['alertas_disparados'].append({
                        'alerta_id': str(alerta.id),
                        'nome': alerta.nome,
                        'tipo': alerta.tipo_alerta.value if hasattr(alerta.tipo_alerta, 'value') else alerta.tipo_alerta,
                        'valor_atual': float(valor_atual),
                        'threshold': float(alerta.condicao_valor)
                    })
                
                resultados['total_processados'] += 1
                
            except Exception as e:
                resultados['erros'].append({
                    'alerta_id': str(alerta.id),
                    'erro': str(e)
                })
        
        return resultados

    @staticmethod
    def testar_alerta(usuario_id: UUID, alerta_id: UUID) -> Dict:
        """
        Testa alerta sem disparar notificação.
        
        Args:
            usuario_id: ID do usuário
            alerta_id: ID do alerta
            
        Returns:
            Dict com resultado do teste
            
        Raises:
            ValueError: Se alerta não encontrado
        """
        alerta = ConfiguracaoAlerta.query.filter_by(
            id=alerta_id,
            usuario_id=usuario_id
        ).first()
        
        if not alerta:
            raise ValueError("Alerta não encontrado")
        
        # Obter valor atual
        valor_atual = AlertaService._obter_valor_atual(alerta)
        
        if valor_atual is None:
            return {
                'alerta_id': str(alerta.id),
                'status': 'erro',
                'mensagem': 'Não foi possível obter valor atual'
            }
        
        # Validar condição
        condicao_atingida = AlertaService.validar_condicao(alerta, valor_atual)
        
        return {
            'alerta_id': str(alerta.id),
            'nome': alerta.nome,
            'tipo': alerta.tipo_alerta.value if hasattr(alerta.tipo_alerta, 'value') else alerta.tipo_alerta,
            'valor_atual': float(valor_atual),
            'threshold': float(alerta.condicao_valor),
            'operador': alerta.condicao_operador.value if hasattr(alerta.condicao_operador, 'value') else alerta.condicao_operador,
            'condicao_atingida': condicao_atingida,
            'status': 'dispararia' if condicao_atingida else 'aguardando'
        }

    @staticmethod
    def obter_historico_acionamentos(
        usuario_id: UUID,
        limite: int = 20
    ) -> List[Dict]:
        """
        Obtém histórico de alertas acionados.
        
        Args:
            usuario_id: ID do usuário
            limite: Número máximo de registros
            
        Returns:
            Lista com histórico de acionamentos
        """
        alertas = ConfiguracaoAlerta.query.filter(
            ConfiguracaoAlerta.usuario_id == usuario_id,
            ConfiguracaoAlerta.timestamp_ultimo_acionamento.isnot(None)
        ).order_by(
            ConfiguracaoAlerta.timestamp_ultimo_acionamento.desc()
        ).limit(limite).all()
        
        return [{
            'alerta_id': str(a.id),
            'nome': a.nome,
            'tipo': a.tipo_alerta.value if hasattr(a.tipo_alerta, 'value') else a.tipo_alerta,
            'ultimo_acionamento': a.timestamp_ultimo_acionamento.isoformat() if a.timestamp_ultimo_acionamento else None,
            'ativo': a.ativo
        } for a in alertas]

    # ============ MÉTODOS PRIVADOS ============

    @staticmethod
    def _obter_valor_atual(alerta: ConfiguracaoAlerta) -> Optional[Decimal]:
        """
        Obtém valor atual baseado no tipo de alerta.
        
        Args:
            alerta: Objeto ConfiguracaoAlerta
            
        Returns:
            Valor atual ou None se não disponível
        """
        tipo = alerta.tipo_alerta.value if hasattr(alerta.tipo_alerta, 'value') else alerta.tipo_alerta
        
        if tipo in ['QUEDA_PRECO', 'ALTA_PRECO'] and alerta.ativo_id:
            # Buscar preço atual do ativo
            ativo = Ativo.query.get(alerta.ativo_id)
            if ativo and ativo.preco_atual:
                return ativo.preco_atual
        
        elif tipo == 'DIVIDENDO_PREVISTO' and alerta.ativo_id:
            # Buscar próximo dividendo previsto
            provento = Provento.query.filter_by(
                ativo_id=alerta.ativo_id,
                status_pagamento='PREVISTO'
            ).order_by(Provento.data_pagamento).first()
            
            if provento:
                return provento.valor_por_cota
        
        elif tipo == 'META_RENTABILIDADE' and alerta.portfolio_id:
            # Calcular rentabilidade do portfolio
            posicoes = Posicao.query.filter_by(
                usuario_id=alerta.usuario_id,
                portfolio_id=alerta.portfolio_id
            ).all()
            
            total_custo = sum(p.custo_total for p in posicoes)
            total_atual = sum(p.valor_atual or Decimal('0.00') for p in posicoes)
            
            if total_custo > 0:
                rentabilidade = ((total_atual - total_custo) / total_custo) * 100
                return rentabilidade
        
        return None
