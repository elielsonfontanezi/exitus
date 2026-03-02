#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Service de Importação B3 Portal Investidor
GAP: EXITUS-IMPORT-001
Arquiteto: Perplexity AI (Persona 2)
"""

import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
import re

from app.database import db
from app.models.ativo import Ativo, ClasseAtivo
from app.models.corretora import Corretora
from app.models.provento import Provento, TipoProvento
from app.models.transacao import Transacao, TipoTransacao
from app.models.usuario import Usuario
from app.services.ativo_service import AtivoService
from app.services.corretora_service import CorretoraService
from app.services.provento_service import ProventoService
from app.services.transacao_service import TransacaoService

logger = logging.getLogger(__name__)


class ImportB3Service:
    """Service para importação de arquivos B3 Portal Investidor"""

    def __init__(self):
        # TODO: Obter do contexto/auth
        self.usuario_id = None
        self.mapeamento_tipos_provento = {
            'Rendimento': TipoProvento.RENDIMENTO,
            'Juros Sobre Capital Próprio': TipoProvento.JCP,
            'Dividendo': TipoProvento.DIVIDENDO,
            'Direito de Subscrição': TipoProvento.BONIFICACAO,
            'Direitos de Subscrição - Não Exercido': TipoProvento.BONIFICACAO,
            'Atualização': TipoProvento.OUTRO,
            'Cessão de Direitos': TipoProvento.OUTRO,
            'Cessão de Direitos - Solicitada': TipoProvento.OUTRO,
            'Transferência - Liquidação': TipoProvento.OUTRO,
            'Reembolso': TipoProvento.OUTRO,
            'Bonificação em Dinheiro': TipoProvento.BONIFICACAO,
            'Amortização': TipoProvento.OUTRO
        }
        
        self.mapeamento_tipos_transacao = {
            'Compra': TipoTransacao.COMPRA,
            'Venda': TipoTransacao.VENDA
        }

    def parse_movimentacoes(self, file_path: str) -> List[Dict]:
        """
        Parse arquivo de movimentações (CSV ou Excel)
        Formato B3: Entrada/Saída, Data, Movimentação, Produto, Instituição, Quantidade, Preço unitário, Valor da Operação
        """
        try:
            # Detectar formato e ler arquivo
            if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
                df = pd.read_excel(file_path)
            else:
                df = pd.read_csv(file_path, encoding='utf-8')
            
            logger.info(f"Arquivo lido: {len(df)} linhas")
            logger.info(f"Colunas encontradas: {list(df.columns)}")
            
            movimentacoes = []
            
            for _, row in df.iterrows():
                try:
                    # Mapear colunas (variações possíveis)
                    data = self._parse_data(row.get('Data', row.get('Data da Operação', '')))
                    if not data:
                        continue
                    
                    movimento = {
                        'data': self._parse_data(row.get('Data')),
                        'tipo_movimentacao': str(row.get('Movimentação', '')).strip(),
                        'produto': str(row.get('Produto', '')).strip(),
                        'instituicao': str(row.get('Instituição', '')).strip(),
                        'quantidade': self._parse_quantidade(row.get('Quantidade', 0)),
                        'preco_unitario': self._parse_monetario(row.get('Preço unitário', row.get('Preço', 0))),
                        'valor_operacao': self._parse_monetario(row.get('Valor da Operação', row.get('Valor', 0)))
                    }
                    
                    # Validar dados mínimos
                    if not movimento['tipo_movimentacao'] or not movimento['produto']:
                        continue
                    
                    # Pular registros com valor zero (violates check constraint)
                    if movimento['valor_operacao'] == 0:
                        logger.warning(f"Registro com valor zero ignorado: {movimento['produto']} em {movimento['data']}")
                        continue
                    
                    # Pular tipos que não devem ser importados como proventos
                    tipos_custodia = ['Transferência - Liquidação']  # Tratar como evento de custódia
                    tipos_ignorados = ['Cessão de Direitos - Solicitada']  # Não tratável
                    
                    if movimento['tipo_movimentacao'] in tipos_custodia:
                        logger.info(f"Tipo identificado como EVENTO DE CUSTÓDIA: {movimento['tipo_movimentacao']} - {movimento['produto']} em {movimento['data']}")
                        # TODO: Implementar tratamento como evento de custódia (EventoCustodia)
                        continue
                    
                    if movimento['tipo_movimentacao'] in tipos_ignorados:
                        logger.info(f"Tipo ignorado (não aplicável): {movimento['tipo_movimentacao']} - {movimento['produto']} em {movimento['data']}")
                        continue
                    
                    movimentacoes.append(movimento)
                    
                except Exception as e:
                    logger.warning(f"Erro ao processar linha {_}: {e}")
                    continue
            
            logger.info(f"{len(movimentacoes)} movimentações válidas processadas")
            return movimentacoes
            
        except Exception as e:
            logger.error(f"Erro ao ler arquivo {file_path}: {e}")
            raise

    def parse_negociacoes(self, file_path: str) -> List[Dict]:
        """
        Parse arquivo de negociações (CSV ou Excel)
        Formato B3: Data do Negócio, Tipo de Movimentação, Mercado, Prazo/Vencimento, Instituição, Código de Negociação, Quantidade, Preço, Valor
        """
        try:
            # Detectar formato e ler arquivo
            if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
                df = pd.read_excel(file_path)
            else:
                df = pd.read_csv(file_path, encoding='utf-8')
            
            logger.info(f"Arquivo lido: {len(df)} linhas")
            logger.info(f"Colunas encontradas: {list(df.columns)}")
            
            negociacoes = []
            
            for _, row in df.iterrows():
                try:
                    # Mapear colunas (variações possíveis)
                    data = self._parse_data(row.get('Data do Negócio', row.get('Data', '')))
                    if not data:
                        continue
                    
                    negociacao = {
                        'data': data,
                        'tipo_movimentacao': str(row.get('Tipo de Movimentação', '')).strip(),
                        'mercado': str(row.get('Mercado', '')).strip(),
                        'prazo_vencimento': str(row.get('Prazo/Vencimento', '')).strip(),
                        'instituicao': str(row.get('Instituição', '')).strip(),
                        'codigo_negociacao': str(row.get('Código de Negociação', row.get('Ativo', ''))).strip(),
                        'quantidade': self._parse_quantidade(row.get('Quantidade', 0)),
                        'preco': self._parse_monetario(row.get('Preço', row.get('Preço unitário', 0))),
                        'valor': self._parse_monetario(row.get('Valor', row.get('Valor da Operação', 0)))
                    }
                    
                    # Validar dados mínimos
                    if not negociacao['tipo_movimentacao'] or not negociacao['codigo_negociacao']:
                        continue
                    
                    negociacoes.append(negociacao)
                    
                except Exception as e:
                    logger.warning(f"Erro ao processar linha {_}: {e}")
                    continue
            
            logger.info(f"{len(negociacoes)} negociações válidas processadas")
            return negociacoes
            
        except Exception as e:
            logger.error(f"Erro ao ler arquivo {file_path}: {e}")
            raise

    def importar_movimentacoes(self, movimentacoes: List[Dict], sobrescrever: bool = True) -> Dict:
        """
        Importar movimentações como proventos
        """
        resultado = {
            'sucesso': 0,
            'erros': 0,
            'erros_lista': [],
            'ativos_criados': 0,
            'corretoras_criadas': 0
        }
        
        try:
            for mov in movimentacoes:
                try:
                    # Mapear tipo de provento
                    tipo_provento_enum = self.mapeamento_tipos_provento.get(mov['tipo_movimentacao'])
                    if not tipo_provento_enum:
                        resultado['erros'] += 1
                        resultado['erros_lista'].append(f"Tipo de provento não mapeado: {mov['tipo_movimentacao']}")
                        continue
                    
                    # Obter ou criar ativo
                    ticker = self._extrair_ticker(mov['produto'])
                    ativo = self._obter_ou_criar_ativo(ticker, resultado)
                    
                    # Obter ou criar corretora
                    corretora = self._obter_ou_criar_corretora(mov['instituicao'], resultado)
                    
                    # Verificar duplicata
                    if not sobrescrever:
                        existente = Provento.query.filter_by(
                            ativo_id=ativo.id,
                            data_pagamento=mov['data'],
                            tipo_provento=tipo_provento_enum
                        ).first()
                        
                        if existente:
                            resultado['erros'] += 1
                            resultado['erros_lista'].append(f"Provento duplicado: {ticker} em {mov['data']}")
                            continue
                    
                    # Criar provento
                    provento = Provento(
                        ativo_id=ativo.id,
                        data_pagamento=mov['data'],
                        data_com=mov['data'] - timedelta(days=2),  # Estimativa
                        tipo_provento=tipo_provento_enum,
                        quantidade_ativos=mov['quantidade'],
                        valor_por_acao=mov['preco_unitario'],
                        valor_bruto=mov['valor_operacao'],
                        valor_liquido=mov['valor_operacao']  # Sem IR explicito
                    )
                    
                    db.session.add(provento)
                    resultado['sucesso'] += 1
                    
                except Exception as e:
                    resultado['erros'] += 1
                    resultado['erros_lista'].append(f"Erro ao importar movimentação {mov.get('produto', 'N/A')}: {e}")
                    logger.error(f"Erro detalhado: {e} - Dados: {mov}")
                    continue
            
            db.session.commit()
            logger.info(f"Importação concluída: {resultado['sucesso']} sucessos, {resultado['erros']} erros")
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro na importação: {e}")
            raise
        
        return resultado

    def importar_negociacoes(self, negociacoes: List[Dict], sobrescrever: bool = True) -> Dict:
        """
        Importar negociações como transações
        """
        resultado = {
            'sucesso': 0,
            'erros': 0,
            'erros_lista': [],
            'ativos_criados': 0,
            'corretoras_criadas': 0
        }
        
        try:
            for neg in negociacoes:
                try:
                    # Mapear tipo de transação
                    tipo_transacao_enum = self.mapeamento_tipos_transacao.get(neg['tipo_movimentacao'])
                    if not tipo_transacao_enum:
                        resultado['erros'] += 1
                        resultado['erros_lista'].append(f"Tipo de transação não mapeado: {neg['tipo_movimentacao']}")
                        continue
                    
                    # Obter ou criar ativo
                    ticker = self._extrair_ticker(neg['codigo_negociacao'])
                    ativo = self._obter_ou_criar_ativo(ticker, resultado)
                    
                    # Obter ou criar corretora
                    corretora = self._obter_ou_criar_corretora(neg['instituicao'], resultado)
                    
                    # Verificar duplicata
                    if not sobrescrever:
                        existente = Transacao.query.filter_by(
                            ativo_id=ativo.id,
                            data_transacao=neg['data'],
                            tipo_transacao=tipo_transacao_enum
                        ).first()
                        
                        if existente:
                            resultado['erros'] += 1
                            resultado['erros_lista'].append(f"Transação duplicada: {ticker} em {neg['data']}")
                            continue
                    
                    # Criar transação
                    transacao = Transacao(
                        usuario_id=self._get_usuario_id(),
                        ativo_id=ativo.id,
                        corretora_id=corretora.id if corretora else None,
                        data_transacao=neg['data'],
                        tipo=tipo_transacao_enum,
                        quantidade=neg['quantidade'],
                        preco_unitario=neg['preco'],
                        valor_total=neg['valor'],
                        taxa_corretagem=0,
                        taxa_liquidacao=0,
                        emolumentos=0,
                        imposto=0,
                        outros_custos=0,
                        custos_totais=0,
                        valor_liquido=neg['valor'],
                        observacoes=f"Importação B3 - {neg['codigo_negociacao']}"
                    )
                    
                    db.session.add(transacao)
                    resultado['sucesso'] += 1
                    
                except Exception as e:
                    resultado['erros'] += 1
                    resultado['erros_lista'].append(f"Erro ao importar negociação: {e}")
                    continue
            
            db.session.commit()
            logger.info(f"Importação concluída: {resultado['sucesso']} sucessos, {resultado['erros']} erros")
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro na importação: {e}")
            raise
        
        return resultado

    def _parse_data(self, data_str: str) -> Optional[datetime]:
        """Parse data em formatos brasileiros"""
        if not data_str or pd.isna(data_str):
            return None
        
        try:
            # Remover espaços e converter para string
            data_str = str(data_str).strip()
            
            # Formatos possíveis: DD/MM/YYYY, DD/MM/YY, YYYY-MM-DD
            formatos = ['%d/%m/%Y', '%d/%m/%y', '%Y-%m-%d']
            
            for formato in formatos:
                try:
                    return datetime.strptime(data_str, formato).date()
                except ValueError:
                    continue
            
            logger.warning(f"Formato de data não reconhecido: {data_str}")
            return None
            
        except Exception as e:
            logger.warning(f"Erro ao parsear data '{data_str}': {e}")
            return None

    def _parse_quantidade(self, value) -> Decimal:
        """Parse quantidade (inteiro)"""
        if pd.isna(value) or value == '' or value is None:
            return Decimal('0')
        
        try:
            # Quantidade é sempre inteira
            if isinstance(value, (int, float)):
                return Decimal(str(int(value)))
            
            # Tratar como string
            value_str = str(value).strip()
            
            if value_str == '-':
                return Decimal('0')
            
            # Remover formatação
            value_str = re.sub(r'[^\d]', '', value_str)
            
            return Decimal(int(value_str)) if value_str else Decimal('0')
            
        except Exception as e:
            logger.warning(f"Erro ao converter quantidade '{value}': {e}")
            return Decimal('0')

    def _parse_monetario(self, value) -> Decimal:
        """Parse valor monetário (BRL)"""
        if pd.isna(value) or value == '' or value is None:
            return Decimal('0')
        
        try:
            # Se veio como número do Excel (float), já está no formato correto
            if isinstance(value, (int, float)):
                # Excel já lê os valores monetários brasileiros corretamente
                return Decimal(str(float(value)))
            
            # Tratar como string (formato brasileiro)
            value_str = str(value).strip()
            
            if value_str == '-':
                return Decimal('0')
            
            # Verificar se já tem ponto decimal (formato americano)
            if '.' in value_str and ',' not in value_str:
                # Já está em formato americano (veio do Excel)
                return Decimal(value_str)
            
            # Formato brasileiro: remover pontos de milhar, converter vírgula para ponto
            value_str = re.sub(r'R\$|\s', '', value_str)  # Remover R$ e espaços
            value_str = re.sub(r'\.', '', value_str)     # Remover pontos de milhar
            value_str = re.sub(r',', '.', value_str)    # Converter vírgula para ponto
            
            return Decimal(value_str)
            
        except Exception as e:
            logger.warning(f"Erro ao converter valor monetário '{value}': {e}")
            return Decimal('0')

    def _extrair_ticker(self, produto: str) -> str:
        """Extrair ticker do produto B3"""
        if not produto:
            return ''
        
        # Formato B3: "BTLG11 - BTG PACTUAL..." ou "ALZR11"
        match = re.match(r'^([A-Z]{4}\d{1,2})', produto.upper())
        if match:
            return match.group(1)
        
        # Fallback: remover tudo após espaço ou hífen
        ticker = re.split(r'[\s\-]', produto)[0]
        return ticker.strip()

    def _get_usuario_id(self):
        """Obter ID do primeiro usuário se não estiver definido"""
        if not self.usuario_id:
            from app.models.usuario import Usuario
            usuario = Usuario.query.first()
            self.usuario_id = usuario.id if usuario else None
        return self.usuario_id

    def _obter_ou_criar_ativo(self, ticker: str, resultado: Dict) -> Ativo:
        """Obter ativo existente ou criar novo"""
        ativo = Ativo.query.filter_by(ticker=ticker).first()
        
        if not ativo:
            # Criar novo ativo
            # Determinar tipo e classe baseado no ticker
            if ticker.endswith(('11', '12', '13', '31', '32', '33', '34', '35', '36')):
                tipo_ativo = 'FII'
                classe_ativo = ClasseAtivo.FII
            else:
                tipo_ativo = 'ACAO'
                classe_ativo = ClasseAtivo.ACAO
            
            ativo = Ativo(
                ticker=ticker,
                nome=ticker,  # Nome temporário
                mercado='B3',  # Padrão
                tipo=tipo_ativo,
                classe=classe_ativo,
                moeda='BRL',
                ativo=True
            )
            
            db.session.add(ativo)
            db.session.flush()  # Obter ID sem commit
            resultado['ativos_criados'] += 1
            logger.info(f"Ativo criado: {ticker}")
        
        return ativo

    def _obter_ou_criar_corretora(self, instituicao: str, resultado: Dict) -> Optional[Corretora]:
        """Obter corretora existente ou criar nova"""
        if not instituicao:
            return None
        
        # Normalizar nome
        nome_normalizado = instituicao.upper().strip()
        
        corretora = Corretora.query.filter_by(nome=nome_normalizado).first()
        
        if not corretora:
            # Criar nova corretora
            corretora = Corretora(
                nome=nome_normalizado,
                usuario_id=self._get_usuario_id()
            )
            
            db.session.add(corretora)
            db.session.flush()  # Obter ID sem commit
            resultado['corretoras_criadas'] += 1
            logger.info(f"Corretora criada: {nome_normalizado}")
        
        return corretora
