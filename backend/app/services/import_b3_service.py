#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Service de Importação B3 Portal Investidor
GAP: EXITUS-IMPORT-001
Arquiteto: Perplexity AI (Persona 2)
"""

import hashlib
import os
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
import re

from app.database import db
from app.models.ativo import Ativo, ClasseAtivo, TipoAtivo
from app.models.corretora import Corretora
from app.models.provento import Provento, TipoProvento
from app.models.transacao import Transacao, TipoTransacao
from app.models.evento_custodia import EventoCustodia, TipoEventoCustodia
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
        self.arquivo_origem = None
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
                    
                    # Pular registros com valor zero ou quantidade zero (violates check constraint)
                    if movimento['valor_operacao'] == 0 or movimento['quantidade'] == 0:
                        logger.warning(f"Registro com valor/quantidade zero ignorado: {movimento['produto']} em {movimento['data']}")
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

    def _sanitizar_texto(self, texto: str) -> str:
        """Remove caracteres perigosos de campos de texto (XSS, Unicode malicioso)"""
        if not texto:
            return ''
        texto = str(texto).strip()
        texto = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', texto)
        texto = re.sub(r'<[^>]+>', '', texto)
        return texto[:500]

    def _gerar_hash_linha(self, row: Dict) -> str:
        """Gera hash MD5 da linha original do arquivo B3 para deduplicação"""
        conteudo = (
            f"{row.get('data')}|"
            f"{row.get('tipo_movimentacao', '')}|"
            f"{row.get('produto', row.get('codigo_negociacao', ''))}|"
            f"{row.get('instituicao', '')}|"
            f"{row.get('quantidade', '')}|"
            f"{row.get('preco_unitario', row.get('preco', ''))}|"
            f"{row.get('valor_operacao', row.get('valor', ''))}"
        )
        arquivo = self.arquivo_origem or ''
        chave = f"{arquivo}|{conteudo}"
        return hashlib.md5(chave.encode('utf-8')).hexdigest()

    def importar_movimentacoes(self, movimentacoes: List[Dict], sobrescrever: bool = True,
                                dry_run: bool = False) -> Dict:
        """
        Importar movimentações como proventos e eventos de custódia.
        dry_run=True retorna preview sem persistir.
        """
        resultado = {
            'proventos': {'sucesso': 0, 'erros': 0, 'erros_lista': [], 'duplicatas_ignoradas': 0, 'duplicatas_lista': []},
            'eventos_custodia': {'sucesso': 0, 'erros': 0, 'erros_lista': [], 'duplicatas_ignoradas': 0},
            'ativos_criados': 0,
            'corretoras_criadas': 0
        }
        
        try:
            # Separar tipos
            proventos = []
            eventos_custodia = []
            
            for mov in movimentacoes:
                if mov['tipo_movimentacao'] in ['Transferência - Liquidação']:
                    eventos_custodia.append(mov)
                elif mov['tipo_movimentacao'] not in ['Cessão de Direitos - Solicitada']:
                    proventos.append(mov)
            
            # Importar proventos
            if proventos:
                resultado_proventos = self._importar_proventos(proventos, sobrescrever, dry_run)
                resultado['proventos'] = resultado_proventos
                resultado['ativos_criados'] += resultado_proventos.get('ativos_criados', 0)
                resultado['corretoras_criadas'] += resultado_proventos.get('corretoras_criadas', 0)

            # Importar eventos de custódia
            if eventos_custodia:
                resultado_eventos = self._processar_eventos_custodia(eventos_custodia, dry_run)
                resultado['eventos_custodia'] = resultado_eventos
                resultado['ativos_criados'] += resultado_eventos.get('ativos_criados', 0)
                resultado['corretoras_criadas'] += resultado_eventos.get('corretoras_criadas', 0)

            # Calcular totais
            resultado['sucesso'] = resultado['proventos']['sucesso'] + resultado['eventos_custodia']['sucesso']
            resultado['erros'] = resultado['proventos']['erros'] + resultado['eventos_custodia']['erros']
            resultado['erros_lista'] = resultado['proventos']['erros_lista'] + resultado['eventos_custodia']['erros_lista']
            resultado['duplicatas_ignoradas'] = (
                resultado['proventos'].get('duplicatas_ignoradas', 0) +
                resultado['eventos_custodia'].get('duplicatas_ignoradas', 0)
            )
            resultado['dry_run'] = dry_run

            if dry_run:
                db.session.rollback()
                logger.info(f"Dry-run: {resultado['sucesso']} seriam inseridos, "
                            f"{resultado['duplicatas_ignoradas']} duplicatas ignoradas")
            else:
                db.session.commit()
                logger.info(f"Importação concluída: {resultado['sucesso']} sucessos, "
                            f"{resultado['erros']} erros, "
                            f"{resultado['duplicatas_ignoradas']} duplicatas ignoradas")

        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro na importação: {e}")
            raise

        return resultado

    def importar_negociacoes(self, negociacoes: List[Dict], sobrescrever: bool = True,
                              dry_run: bool = False) -> Dict:
        """
        Importar negociações como transações.
        dry_run=True retorna preview sem persistir.
        """
        resultado = {
            'sucesso': 0,
            'erros': 0,
            'erros_lista': [],
            'duplicatas_ignoradas': 0,
            'duplicatas_lista': [],
            'ativos_criados': 0,
            'corretoras_criadas': 0,
            'dry_run': dry_run
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

                    # Sanitizar campos de texto
                    neg['codigo_negociacao'] = self._sanitizar_texto(neg.get('codigo_negociacao', ''))
                    neg['instituicao'] = self._sanitizar_texto(neg.get('instituicao', ''))

                    # Gerar hash da linha para deduplicação
                    hash_linha = self._gerar_hash_linha(neg)

                    # Verificar duplicata por hash
                    existente = Transacao.query.filter_by(hash_importacao=hash_linha).first()
                    if existente:
                        ticker = self._extrair_ticker(neg['codigo_negociacao'])
                        resultado['duplicatas_ignoradas'] += 1
                        resultado['duplicatas_lista'].append(
                            f"Duplicata ignorada: {ticker} em {neg['data']} (hash={hash_linha[:8]}...)"
                        )
                        logger.debug(f"Duplicata por hash ignorada: {ticker} {neg['data']}")
                        continue

                    # Obter ou criar ativo
                    ticker = self._extrair_ticker(neg['codigo_negociacao'])
                    ativo = self._obter_ou_criar_ativo(ticker, resultado)

                    # Obter ou criar corretora
                    corretora = self._obter_ou_criar_corretora(neg['instituicao'], resultado)

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
                        observacoes=self._sanitizar_texto(f"Importação B3 - {neg['codigo_negociacao']}"),
                        hash_importacao=hash_linha,
                        arquivo_origem=self.arquivo_origem
                    )

                    db.session.add(transacao)
                    resultado['sucesso'] += 1

                except Exception as e:
                    resultado['erros'] += 1
                    resultado['erros_lista'].append(f"Erro ao importar negociação: {e}")
                    continue

            if dry_run:
                db.session.rollback()
                logger.info(f"Dry-run: {resultado['sucesso']} seriam inseridos, "
                            f"{resultado['duplicatas_ignoradas']} duplicatas ignoradas")
            else:
                db.session.commit()
                logger.info(f"Importação concluída: {resultado['sucesso']} sucessos, "
                            f"{resultado['erros']} erros, "
                            f"{resultado['duplicatas_ignoradas']} duplicatas ignoradas")

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
                tipo_ativo = TipoAtivo.FII
                classe_ativo = ClasseAtivo.RENDA_VARIAVEL
            else:
                tipo_ativo = TipoAtivo.ACAO
                classe_ativo = ClasseAtivo.RENDA_VARIAVEL
            
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

    def _importar_proventos(self, proventos: List[Dict], sobrescrever: bool = True,
                             dry_run: bool = False) -> Dict:
        """Importa apenas proventos (método auxiliar)"""
        resultado = {
            'sucesso': 0,
            'erros': 0,
            'erros_lista': [],
            'duplicatas_ignoradas': 0,
            'duplicatas_lista': [],
            'ativos_criados': 0,
            'corretoras_criadas': 0
        }

        try:
            for mov in proventos:
                try:
                    # Mapear tipo de provento
                    tipo_provento_enum = self.mapeamento_tipos_provento.get(mov['tipo_movimentacao'])
                    if not tipo_provento_enum:
                        resultado['erros'] += 1
                        resultado['erros_lista'].append(f"Tipo de provento não mapeado: {mov['tipo_movimentacao']}")
                        continue

                    # Sanitizar campos de texto
                    mov['produto'] = self._sanitizar_texto(mov.get('produto', ''))
                    mov['instituicao'] = self._sanitizar_texto(mov.get('instituicao', ''))

                    # Gerar hash da linha para deduplicação
                    hash_linha = self._gerar_hash_linha(mov)

                    # Verificar duplicata por hash
                    existente = Provento.query.filter_by(hash_importacao=hash_linha).first()
                    if existente:
                        ticker = self._extrair_ticker(mov['produto'])
                        resultado['duplicatas_ignoradas'] += 1
                        resultado['duplicatas_lista'].append(
                            f"Duplicata ignorada: {ticker} em {mov['data']} (hash={hash_linha[:8]}...)"
                        )
                        logger.debug(f"Duplicata por hash ignorada: {ticker} {mov['data']}")
                        continue

                    # Obter ou criar ativo
                    ticker = self._extrair_ticker(mov['produto'])
                    ativo = self._obter_ou_criar_ativo(ticker, resultado)

                    # Obter ou criar corretora
                    corretora = self._obter_ou_criar_corretora(mov['instituicao'], resultado)

                    # Criar provento
                    provento = Provento(
                        ativo_id=ativo.id,
                        data_pagamento=mov['data'],
                        data_com=mov['data'] - timedelta(days=2),
                        tipo_provento=tipo_provento_enum,
                        quantidade_ativos=mov['quantidade'],
                        valor_por_acao=mov['preco_unitario'],
                        valor_bruto=mov['valor_operacao'],
                        valor_liquido=mov['valor_operacao'],
                        hash_importacao=hash_linha,
                        arquivo_origem=self.arquivo_origem
                    )

                    db.session.add(provento)
                    resultado['sucesso'] += 1

                except Exception as e:
                    resultado['erros'] += 1
                    resultado['erros_lista'].append(f"Erro ao importar provento {mov.get('produto', 'N/A')}: {e}")
                    logger.error(f"Erro detalhado: {e} - Dados: {mov}")
                    continue

            return resultado

        except Exception as e:
            logger.error(f"Erro na importação de proventos: {e}")
            raise

    def _processar_eventos_custodia(self, movimentacoes: List[Dict],
                                     dry_run: bool = False) -> Dict:
        """Processa Transferência - Liquidação como eventos de custódia"""
        resultado = {
            'sucesso': 0,
            'erros': 0,
            'erros_lista': []
        }
        
        tipos_custodia = ['Transferência - Liquidação']
        
        for mov in movimentacoes:
            if mov['tipo_movimentacao'] in tipos_custodia:
                try:
                    # Obter ativo
                    ticker = self._extrair_ticker(mov['produto'])
                    ativo = self._obter_ou_criar_ativo(ticker, resultado)
                    corretora = self._obter_ou_criar_corretora(mov['instituicao'], resultado)
                    
                    # Criar evento de custódia
                    evento = EventoCustodia(
                        usuario_id=self._get_usuario_id(),
                        ativo_id=ativo.id,
                        corretora_id=corretora.id,
                        tipo_evento=TipoEventoCustodia.LIQUIDACAO_D2,
                        data_evento=mov['data'],
                        quantidade=mov['quantidade'],
                        valor_operacao=mov['valor_operacao'],
                        observacoes=f"Liquidação D+2 - {mov['tipo_movimentacao']}",
                        fonte='B3_IMPORT',
                        dados_origem=mov
                    )
                    
                    db.session.add(evento)
                    resultado['sucesso'] += 1
                    logger.info(f"Evento de custódia criado: {ticker} - {mov['data']}")
                    
                except Exception as e:
                    resultado['erros'] += 1
                    resultado['erros_lista'].append(f"Erro no evento de custódia: {e}")
                    logger.error(f"Erro ao processar evento de custódia: {e}")
        
        return resultado
