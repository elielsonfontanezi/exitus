#!/usr/bin/env python3
"""
Carregador de cenários de teste JSON para o sistema Exitus
Integra cenários JSON ao sistema de seeds
"""

import json
import sys
from pathlib import Path
from datetime import datetime, date
from decimal import Decimal

# Adicionar path do backend
sys.path.append('./backend')

try:
    from app import create_app
    from app.database import db
    from app.models.usuario import Usuario, UserRole
    from app.models.assessora import Assessora
    from app.models.ativo import Ativo, TipoAtivo, ClasseAtivo
    from app.models.corretora import Corretora
    from app.models.transacao import Transacao, TipoTransacao
    from app.models.provento import Provento, TipoProvento
    from app.models.movimentacao_caixa import MovimentacaoCaixa, TipoMovimentacao
    from app.models.alerta import Alerta
    from app.models.portfolio import Portfolio
    from app.models.plano_compra import PlanoCompra, StatusPlanoCompra
    from app.models.plano_venda import PlanoVenda, StatusPlanoVenda, TipoGatilho
    from app.models.historico_patrimonio import HistoricoPatrimonio
    from app.models.calendario_dividendo import CalendarioDividendo
    from app.models.projecao_renda import ProjecaoRenda
    from app.models.regra_fiscal import RegraFiscal, IncidenciaImposto
    from app.models.evento_corporativo import EventoCorporativo, TipoEventoCorporativo
    from app.models.meta_alocacao import MetaAlocacao
    from app.models.taxa_cambio import TaxaCambio
    from app.models.fonte_dados import FonteDados, TipoFonteDados
    from app.models.historico_preco import HistoricoPreco
    from app.models.saldo_prejuizo import SaldoPrejuizo
    from werkzeug.security import generate_password_hash
except ImportError as e:
    print(f"Erro ao importar módulos: {e}")
    print("Execute este script na raiz do projeto")
    sys.exit(1)


class ScenarioLoader:
    """Carregador de cenários de teste JSON"""
    
    def __init__(self, app=None):
        import os
        testing = os.getenv('TESTING', '').lower() in ('true', '1', 'yes')
        self.app = app or create_app(testing=testing)
        self.scenario_data = {}
        self.references = {
            'usuarios': {},      # username -> id
            'assessoras': {},    # nome -> id
            'ativos': {},        # ticker -> id
            'corretoras': {},    # nome -> id
            'proventos': {}      # (ativo_ticker, data_com) -> id
        }
    
    def load_scenario_file(self, scenario_path):
        """Carrega arquivo JSON de cenário"""
        print(f"📁 Carregando cenário: {scenario_path}")
        
        with open(scenario_path, 'r', encoding='utf-8') as f:
            self.scenario_data = json.load(f)
        
        print(f"✅ Cenário carregado: {self.scenario_data.get('description', 'N/A')}")
        return self.scenario_data
    
    def load_scenario(self, scenario_name):
        """Carrega cenário por nome (busca em scenarios/)"""
        # Suporta execução via container ou direto
        container_dir = Path('/app/seed_data/scenarios')
        local_dir = Path(__file__).parent / 'seed_data' / 'scenarios'
        scenarios_dir = container_dir if container_dir.exists() else local_dir
        
        scenario_file = scenarios_dir / f'{scenario_name}.json'
        
        if not scenario_file.exists():
            raise FileNotFoundError(f"Cenário não encontrado: {scenario_file}")
        
        return self.load_scenario_file(scenario_file)
    
    def seed_all(self):
        """Executa seed de todos os dados do cenário"""
        with self.app.app_context():
            try:
                # Ordem de criação respeitando dependências
                self._seed_assessoras()
                self._seed_usuarios()
                self._seed_ativos()
                self._seed_fontes_dados()
                self._seed_taxas_cambio()
                self._seed_corretoras()
                self._seed_transacoes()
                self._seed_proventos()
                self._seed_movimentacoes_caixa()
                self._seed_portfolios()
                self._seed_meta_alocacao()
                self._seed_alertas()
                self._seed_planos_compra()
                self._seed_planos_venda()
                self._seed_historico_patrimonio()
                self._seed_historico_preco()
                self._seed_saldo_prejuizo()
                self._seed_calendario_dividendo()
                self._seed_projecoes_renda()
                self._seed_regras_fiscais()
                self._seed_eventos_corporativos()
                
                db.session.commit()
                print("✅ Cenário carregado com sucesso!")
                return True
                
            except Exception as e:
                db.session.rollback()
                print(f"❌ Erro ao carregar cenário: {e}")
                import traceback
                traceback.print_exc()
                return False
    
    def _seed_assessoras(self):
        """Seed de assessoras"""
        assessoras_data = self.scenario_data.get('assessoras', [])
        
        if not assessoras_data:
            # Criar assessora padrão se não existir
            existing = Assessora.query.first()
            if not existing:
                print("📊 Criando assessora padrão...")
                assessora = Assessora(
                    nome='Assessora Padrão',
                    razao_social='Assessora Padrão LTDA',
                    cnpj='00000000000000',
                    email='contato@assessora.exitus',
                    ativo=True,
                    plano='basico',
                    data_cadastro=datetime.utcnow(),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.session.add(assessora)
                db.session.flush()
                self.references['assessoras']['default'] = assessora.id
                print(f"✅ Assessora padrão criada: {assessora.id}")
            else:
                self.references['assessoras']['default'] = existing.id
                print(f"✅ Usando assessora existente: {existing.id}")
            return
        
        print(f"📊 Criando {len(assessoras_data)} assessoras...")
        
        for assessora_data in assessoras_data:
            existing = Assessora.query.filter_by(nome=assessora_data['nome']).first()
            if existing:
                self.references['assessoras'][assessora_data['nome']] = existing.id
                print(f"⚠️  Assessora {assessora_data['nome']} já existe")
                continue
            
            assessora = Assessora(
                nome=assessora_data['nome'],
                razao_social=assessora_data.get('razao_social'),
                cnpj=assessora_data.get('cnpj'),
                email=assessora_data['email'],
                telefone=assessora_data.get('telefone'),
                ativo=assessora_data.get('ativo', True),
                plano='basico',
                data_cadastro=datetime.utcnow(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.session.add(assessora)
            db.session.flush()
            self.references['assessoras'][assessora_data['nome']] = assessora.id
            print(f"✅ Assessora criada: {assessora_data['nome']}")
    
    def _seed_usuarios(self):
        """Seed de usuários"""
        usuarios_data = self.scenario_data.get('usuarios', [])
        if not usuarios_data:
            return
        
        print(f"👥 Criando {len(usuarios_data)} usuários...")
        
        # Obter assessora padrão
        assessora_id = list(self.references['assessoras'].values())[0] if self.references['assessoras'] else None
        
        for user_data in usuarios_data:
            existing = Usuario.query.filter_by(username=user_data['username']).first()
            if existing:
                self.references['usuarios'][user_data['username']] = existing.id
                print(f"⚠️  Usuário {user_data['username']} já existe")
                continue
            
            role_map = {
                'ADMIN': UserRole.ADMIN,
                'USER': UserRole.USER,
                'READONLY': UserRole.READONLY
            }
            
            usuario = Usuario(
                username=user_data['username'],
                email=user_data['email'],
                nome_completo=user_data.get('nome_completo', user_data['username']),
                role=role_map.get(user_data['role'], UserRole.USER),
                password_hash=generate_password_hash(user_data['password']),
                ativo=user_data.get('ativo', True),
                assessora_id=assessora_id
            )
            
            db.session.add(usuario)
            db.session.flush()
            self.references['usuarios'][user_data['username']] = usuario.id
            print(f"✅ Usuário criado: {user_data['username']}")
    
    def _seed_ativos(self):
        """Seed de ativos"""
        ativos_data = self.scenario_data.get('ativos', [])
        if not ativos_data:
            return
        
        print(f"📈 Criando {len(ativos_data)} ativos...")
        
        for ativo_data in ativos_data:
            existing = Ativo.query.filter_by(ticker=ativo_data['ticker']).first()
            if existing:
                self.references['ativos'][ativo_data['ticker']] = existing.id
                print(f"⚠️  Ativo {ativo_data['ticker']} já existe")
                continue
            
            tipo_map = {
                'ACAO': TipoAtivo.ACAO,
                'FII': TipoAtivo.FII,
                'STOCK': TipoAtivo.STOCK,
                'ETF': TipoAtivo.ETF,
                'REIT': TipoAtivo.REIT,
                'BDR': TipoAtivo.STOCK,  # BDR mapeia para STOCK
                'CDB': TipoAtivo.CDB,
                'LCI': TipoAtivo.LCI_LCA,
                'LCA': TipoAtivo.LCI_LCA,
                'LCI_LCA': TipoAtivo.LCI_LCA,
                'DEBENTURE': TipoAtivo.DEBENTURE,
                'TESOURO_DIRETO': TipoAtivo.TESOURO_DIRETO,
                'UNIT': TipoAtivo.UNIT,
                'CRIPTO': TipoAtivo.CRIPTO,
                'FUNDO': TipoAtivo.OUTRO,  # FUNDO mapeia para OUTRO
                'BOND': TipoAtivo.BOND,
                'STOCK_INTL': TipoAtivo.STOCK_INTL,
                'ETF_INTL': TipoAtivo.ETF_INTL,
                'OUTRO': TipoAtivo.OUTRO
            }
            
            classe_map = {
                'RENDA_VARIAVEL': ClasseAtivo.RENDA_VARIAVEL,
                'RENDA_FIXA': ClasseAtivo.RENDA_FIXA,
                'CRIPTO': ClasseAtivo.CRIPTO,
                'COMMODITY': ClasseAtivo.COMMODITY,
                'HIBRIDO': ClasseAtivo.HIBRIDO,
                'MULTIMERCADO': ClasseAtivo.HIBRIDO,  # Mapear MULTIMERCADO para HIBRIDO
                'CAMBIO': ClasseAtivo.HIBRIDO,  # Mapear CAMBIO para HIBRIDO
                'DERIVATIVO': ClasseAtivo.HIBRIDO  # Mapear DERIVATIVO para HIBRIDO
            }
            
            ativo = Ativo(
                ticker=ativo_data['ticker'],
                nome=ativo_data['nome'],
                mercado=ativo_data.get('mercado', 'BR'),
                tipo=tipo_map.get(ativo_data['tipo'], TipoAtivo.ACAO),
                classe=classe_map.get(ativo_data.get('classe', 'RENDA_VARIAVEL'), ClasseAtivo.RENDA_VARIAVEL),
                moeda=ativo_data.get('moeda', 'BRL'),
                preco_atual=ativo_data.get('preco_atual'),
                preco_teto_usuario=ativo_data.get('preco_teto_usuario') or ativo_data.get('preco_teto'),
                dividend_yield=ativo_data.get('dividend_yield'),
                p_l=ativo_data.get('p_l'),
                p_vp=ativo_data.get('p_vp'),
                eps=ativo_data.get('eps'),
                fcf=ativo_data.get('fcf'),
                ffo_por_cota=ativo_data.get('ffo_por_cota'),
                affo_por_cota=ativo_data.get('affo_por_cota'),
                observacoes=ativo_data.get('observacoes'),
                ativo=ativo_data.get('ativo', True),
                deslistado=False
            )
            
            db.session.add(ativo)
            db.session.flush()
            self.references['ativos'][ativo_data['ticker']] = ativo.id
            print(f"✅ Ativo criado: {ativo_data['ticker']}")
    
    def _seed_corretoras(self):
        """Seed de corretoras"""
        corretoras_data = self.scenario_data.get('corretoras', [])
        if not corretoras_data:
            return
        
        print(f"🏦 Criando {len(corretoras_data)} corretoras...")
        
        # Obter primeiro usuário para associar
        usuario_id = list(self.references['usuarios'].values())[0] if self.references['usuarios'] else None
        assessora_id = list(self.references['assessoras'].values())[0] if self.references['assessoras'] else None
        
        for corretora_data in corretoras_data:
            existing = Corretora.query.filter_by(nome=corretora_data['nome']).first()
            if existing:
                self.references['corretoras'][corretora_data['nome']] = existing.id
                print(f"⚠️  Corretora {corretora_data['nome']} já existe")
                continue
            
            corretora = Corretora(
                nome=corretora_data['nome'],
                usuario_id=usuario_id,
                pais=corretora_data.get('pais', 'BR'),
                moeda_padrao=corretora_data.get('moeda_padrao', 'BRL'),
                saldo_atual=Decimal('0.00'),
                ativa=corretora_data.get('ativa', True)
            )
            
            db.session.add(corretora)
            db.session.flush()
            self.references['corretoras'][corretora_data['nome']] = corretora.id
            print(f"✅ Corretora criada: {corretora_data['nome']}")
    
    def _seed_transacoes(self):
        """Seed de transações"""
        transacoes_data = self.scenario_data.get('transacoes', [])
        if not transacoes_data:
            return
        
        print(f"💼 Criando {len(transacoes_data)} transações...")
        
        assessora_id = list(self.references['assessoras'].values())[0] if self.references['assessoras'] else None
        
        for trans_data in transacoes_data:
            usuario_id = self.references['usuarios'].get(trans_data['usuario'])
            ativo_id = self.references['ativos'].get(trans_data['ativo'])
            corretora_id = self.references['corretoras'].get(trans_data['corretora'])
            
            if not all([usuario_id, ativo_id, corretora_id]):
                print(f"⚠️  Referências faltando para transação: {trans_data}")
                continue
            
            tipo_map = {
                'COMPRA': TipoTransacao.COMPRA,
                'VENDA': TipoTransacao.VENDA
            }
            
            # Calcular valores obrigatórios
            quantidade = Decimal(str(trans_data['quantidade']))
            preco_unitario = Decimal(str(trans_data['preco_unitario']))
            taxa_corretagem = Decimal(str(trans_data.get('taxa_corretagem', 0)))
            custos_totais = Decimal(str(trans_data.get('custos_totais', 0)))
            
            valor_total = quantidade * preco_unitario
            valor_liquido = valor_total + custos_totais  # Para compra, soma custos
            
            transacao = Transacao(
                usuario_id=usuario_id,
                ativo_id=ativo_id,
                corretora_id=corretora_id,
                assessora_id=assessora_id,
                tipo=tipo_map.get(trans_data['tipo'], TipoTransacao.COMPRA),
                data_transacao=datetime.strptime(trans_data['data_transacao'], '%Y-%m-%d').date(),
                quantidade=quantidade,
                preco_unitario=preco_unitario,
                valor_total=valor_total,
                taxa_corretagem=taxa_corretagem,
                custos_totais=custos_totais,
                valor_liquido=valor_liquido
            )
            
            db.session.add(transacao)
            print(f"✅ Transação criada: {trans_data['tipo']} {trans_data['ativo']}")
        
        db.session.flush()
    
    def _seed_proventos(self):
        """Seed de proventos"""
        proventos_data = self.scenario_data.get('proventos', [])
        if not proventos_data:
            return
        
        print(f"💰 Criando {len(proventos_data)} proventos...")
        
        assessora_id = list(self.references['assessoras'].values())[0] if self.references['assessoras'] else None
        
        for prov_data in proventos_data:
            ativo_id = self.references['ativos'].get(prov_data['ativo'])
            
            if not ativo_id:
                print(f"⚠️  Ativo não encontrado para provento: {prov_data['ativo']}")
                continue
            
            tipo_map = {
                'DIVIDENDO': TipoProvento.DIVIDENDO,
                'JCP': TipoProvento.JCP,
                'RENDIMENTO': TipoProvento.RENDIMENTO
            }
            
            # Calcular valores do provento
            valor_por_acao = Decimal(str(prov_data['valor_unitario']))
            quantidade_ativos = Decimal(str(prov_data.get('quantidade_ativos', 100)))
            valor_bruto = valor_por_acao * quantidade_ativos
            imposto_retido = Decimal(str(prov_data.get('imposto_retido', 0)))
            valor_liquido = valor_bruto - imposto_retido
            
            provento = Provento(
                ativo_id=ativo_id,
                assessora_id=assessora_id,
                tipo_provento=tipo_map.get(prov_data['tipo_provento'], TipoProvento.DIVIDENDO),
                data_com=datetime.strptime(prov_data['data_com'], '%Y-%m-%d').date(),
                data_pagamento=datetime.strptime(prov_data['data_pagamento'], '%Y-%m-%d').date(),
                valor_por_acao=valor_por_acao,
                quantidade_ativos=quantidade_ativos,
                valor_bruto=valor_bruto,
                imposto_retido=imposto_retido,
                valor_liquido=valor_liquido,
                observacoes=prov_data.get('observacoes')
            )
            
            db.session.add(provento)
            db.session.flush()
            
            # Guardar referência para movimentações de caixa
            key = (prov_data['ativo'], prov_data['data_com'])
            self.references['proventos'][key] = provento.id
            print(f"✅ Provento criado: {prov_data['tipo_provento']} {prov_data['ativo']}")
    
    def _seed_movimentacoes_caixa(self):
        """Seed de movimentações de caixa"""
        movs_data = self.scenario_data.get('movimentacoes_caixa', [])
        if not movs_data:
            return
        
        print(f"💳 Criando {len(movs_data)} movimentações de caixa...")
        
        assessora_id = list(self.references['assessoras'].values())[0] if self.references['assessoras'] else None
        
        for mov_data in movs_data:
            usuario_id = self.references['usuarios'].get(mov_data['usuario'])
            corretora_id = self.references['corretoras'].get(mov_data['corretora'])
            
            if not all([usuario_id, corretora_id]):
                print(f"⚠️  Referências faltando para movimentação: {mov_data}")
                continue
            
            tipo_map = {
                'aporte': TipoMovimentacao.APORTE,
                'resgate': TipoMovimentacao.RESGATE,
                'transferencia_enviada': TipoMovimentacao.TRANSFERENCIA_ENVIADA,
                'transferencia_recebida': TipoMovimentacao.TRANSFERENCIA_RECEBIDA,
                'credito_provento': TipoMovimentacao.CREDITO_PROVENTO,
                'taxa_custodia': TipoMovimentacao.TAXA_CUSTODIA,
                'taxa_corretagem': TipoMovimentacao.TAXA_CORRETAGEM,
                'imposto': TipoMovimentacao.IMPOSTO,
                'ajuste': TipoMovimentacao.AJUSTE,
                'outro': TipoMovimentacao.OUTRO
            }
            
            corretora_destino_id = None
            if mov_data.get('corretora_destino'):
                corretora_destino_id = self.references['corretoras'].get(mov_data['corretora_destino'])

            movimentacao = MovimentacaoCaixa(
                usuario_id=usuario_id,
                corretora_id=corretora_id,
                corretora_destino_id=corretora_destino_id,
                assessora_id=assessora_id,
                tipo_movimentacao=tipo_map.get(mov_data['tipo'], TipoMovimentacao.APORTE),
                valor=Decimal(str(mov_data['valor'])),
                moeda=mov_data.get('moeda', 'BRL'),
                data_movimentacao=datetime.strptime(mov_data['data_movimentacao'], '%Y-%m-%d').date(),
                descricao=mov_data.get('observacoes')
            )
            
            db.session.add(movimentacao)
            print(f"✅ Movimentação criada: {mov_data['tipo']} R$ {mov_data['valor']}")
        
        db.session.flush()
    
    def _seed_portfolios(self):
        """Seed de portfolios"""
        portfolios_data = self.scenario_data.get('portfolios', [])
        if not portfolios_data:
            return
        
        print(f"📁 Criando {len(portfolios_data)} portfolios...")
        
        assessora_id = list(self.references['assessoras'].values())[0] if self.references['assessoras'] else None
        
        for port_data in portfolios_data:
            usuario_id = self.references['usuarios'].get(port_data['usuario'])
            
            if not usuario_id:
                print(f"⚠️  Usuário não encontrado para portfolio: {port_data['usuario']}")
                continue
            
            portfolio = Portfolio(
                usuario_id=usuario_id,
                assessora_id=assessora_id,
                nome=port_data['nome'],
                descricao=port_data.get('descricao'),
                objetivo=port_data.get('objetivo'),
                ativo=port_data.get('ativo', True)
            )
            
            db.session.add(portfolio)
            print(f"✅ Portfolio criado: {port_data['nome']}")
        
        db.session.flush()
    
    def _seed_alertas(self):
        """Seed de alertas"""
        alertas_data = self.scenario_data.get('alertas', [])
        if not alertas_data:
            return
        
        print(f"🔔 Criando {len(alertas_data)} alertas...")
        
        assessora_id = list(self.references['assessoras'].values())[0] if self.references['assessoras'] else None
        
        for alerta_data in alertas_data:
            usuario_id = self.references['usuarios'].get(alerta_data['usuario'])
            
            if not usuario_id:
                print(f"⚠️  Usuário não encontrado para alerta: {alerta_data['usuario']}")
                continue
            
            # Mapear campos do JSON para o model
            tipo_alerta = alerta_data.get('tipo_alerta', 'PRECO_ALVO')
            condicao = alerta_data.get('condicao', 'MAIOR_IGUAL')
            valor_ref = alerta_data.get('valor_referencia', 1.0)  # Usar 1.0 como padrão (constraint > 0)
            ticker = alerta_data.get('ativo_ticker', '')
            
            # Mapear condições para valores curtos (max 10 chars)
            condicao_map = {
                'MAIOR_IGUAL': '>=',
                'MENOR_IGUAL': '<=',
                'MAIOR': '>',
                'MENOR': '<',
                'IGUAL': '=',
                'DIFERENTE': '!='
            }
            
            # Criar nome descritivo
            nome = alerta_data.get('mensagem', f"Alerta {ticker} {tipo_alerta}")
            
            alerta = Alerta(
                usuario_id=usuario_id,
                assessora_id=assessora_id,
                nome=nome[:100],  # Limitar a 100 chars
                tipo_alerta=tipo_alerta,
                ticker=ticker,
                condicao_operador=condicao_map.get(condicao, '>='),
                condicao_valor=Decimal(str(valor_ref)),
                ativo=alerta_data.get('ativo', True),
                frequencia_notificacao='UNICA',
                canais_entrega=['email'] if alerta_data.get('notificar_email', False) else []
            )
            
            db.session.add(alerta)
            print(f"✅ Alerta criado: {nome[:50]}...")
        
        db.session.flush()
    
    def _seed_planos_compra(self):
        """Seed de planos de compra"""
        planos_data = self.scenario_data.get('planos_compra', [])
        if not planos_data:
            return
        
        print(f"📋 Criando {len(planos_data)} planos de compra...")
        
        assessora_id = list(self.references['assessoras'].values())[0] if self.references['assessoras'] else None
        
        for plano_data in planos_data:
            usuario_id = self.references['usuarios'].get(plano_data['usuario'])
            ativo_id = self.references['ativos'].get(plano_data['ativo_ticker'])
            
            if not all([usuario_id, ativo_id]):
                print(f"⚠️  Referências faltando para plano de compra: {plano_data}")
                continue
            
            # Mapear status do JSON para enum (usar enum diretamente, não string)
            status_str = plano_data.get('status', 'ATIVO')
            if status_str == 'ATIVO' or status_str == 'PENDENTE':
                status_enum = StatusPlanoCompra.ATIVO
            elif status_str == 'PAUSADO':
                status_enum = StatusPlanoCompra.PAUSADO
            elif status_str == 'CONCLUIDO':
                status_enum = StatusPlanoCompra.CONCLUIDO
            elif status_str == 'CANCELADO':
                status_enum = StatusPlanoCompra.CANCELADO
            else:
                status_enum = StatusPlanoCompra.ATIVO
            
            # Adaptar campos do JSON para o model PlanoCompra
            plano = PlanoCompra(
                usuario_id=usuario_id,
                ativo_id=ativo_id,
                assessora_id=assessora_id,
                nome=f"Plano {plano_data['ativo_ticker']}",
                quantidade_alvo=plano_data.get('quantidade_desejada', 0),
                valor_aporte_mensal=Decimal(str(plano_data.get('valor_total_planejado', 0))) / 12,  # Dividir em 12 meses
                data_fim_prevista=datetime.strptime(plano_data['data_limite'], '%Y-%m-%d') if plano_data.get('data_limite') else None,
                status=status_enum
            )
            
            db.session.add(plano)
            print(f"✅ Plano de compra criado: {plano_data['ativo_ticker']}")
        
        db.session.flush()
    
    def _seed_planos_venda(self):
        """Seed de planos de venda"""
        planos_data = self.scenario_data.get('planos_venda', [])
        if not planos_data:
            return
        
        print(f"📋 Criando {len(planos_data)} planos de venda...")
        
        assessora_id = list(self.references['assessoras'].values())[0] if self.references['assessoras'] else None
        
        for plano_data in planos_data:
            usuario_id = self.references['usuarios'].get(plano_data['usuario'])
            ativo_id = self.references['ativos'].get(plano_data['ativo_ticker'])
            
            if not all([usuario_id, ativo_id]):
                print(f"⚠️  Referências faltando para plano de venda: {plano_data}")
                continue
            
            # Mapear status do JSON para enum (usar enum diretamente, não string)
            status_str = plano_data.get('status', 'ATIVO')
            if status_str == 'ATIVO' or status_str == 'PENDENTE':
                status_enum = StatusPlanoVenda.ATIVO
            elif status_str == 'PAUSADO':
                status_enum = StatusPlanoVenda.PAUSADO
            elif status_str == 'EXECUTADO' or status_str == 'CONCLUIDO':
                status_enum = StatusPlanoVenda.CONCLUIDO  # EXECUTADO mapeia para CONCLUIDO
            elif status_str == 'CANCELADO':
                status_enum = StatusPlanoVenda.CANCELADO
            else:
                status_enum = StatusPlanoVenda.ATIVO
            
            # Adaptar campos do JSON para o model PlanoVenda
            from app.models.plano_venda import TipoGatilho
            
            plano = PlanoVenda(
                usuario_id=usuario_id,
                ativo_id=ativo_id,
                assessora_id=assessora_id,
                nome=f"Venda {plano_data['ativo_ticker']}",
                quantidade_total=plano_data.get('quantidade_planejada', 0),
                preco_alvo=Decimal(str(plano_data['preco_alvo'])),
                tipo_gatilho=TipoGatilho.PRECO_ALVO,  # Usar PRECO_ALVO como padrão
                data_limite=datetime.strptime(plano_data['data_limite'], '%Y-%m-%d').date() if plano_data.get('data_limite') else None,
                status=status_enum
            )
            
            db.session.add(plano)
            print(f"✅ Plano de venda criado: {plano_data['ativo_ticker']}")
        
        db.session.flush()
    
    def _seed_historico_patrimonio(self):
        """Seed de histórico de patrimônio"""
        historico_data = self.scenario_data.get('historico_patrimonio', [])
        
        if not historico_data:
            print("⏭️  Sem histórico de patrimônio para carregar")
            return
        
        print(f"📊 Carregando {len(historico_data)} registros de histórico de patrimônio...")
        
        for hist_data in historico_data:
            usuario_username = hist_data['usuario']
            usuario_id = self.references['usuarios'].get(usuario_username)
            
            if not usuario_id:
                print(f"⚠️  Usuário não encontrado: {usuario_username}")
                continue
            
            data_snapshot = datetime.strptime(hist_data['data'], '%Y-%m-%d').date()
            
            existing = HistoricoPatrimonio.query.filter_by(
                usuario_id=usuario_id,
                data=data_snapshot
            ).first()
            
            if existing:
                print(f"⏭️  Histórico já existe: {usuario_username} - {data_snapshot}")
                continue
            
            historico = HistoricoPatrimonio(
                usuario_id=usuario_id,
                data=data_snapshot,
                patrimonio_total=Decimal(str(hist_data['patrimonio_total'])),
                patrimonio_renda_variavel=Decimal(str(hist_data.get('patrimonio_renda_variavel', 0))),
                patrimonio_renda_fixa=Decimal(str(hist_data.get('patrimonio_renda_fixa', 0))),
                saldo_caixa=Decimal(str(hist_data.get('saldo_caixa', 0))),
                observacoes=hist_data.get('observacoes')
            )
            
            db.session.add(historico)
            print(f"✅ Histórico criado: {usuario_username} - {data_snapshot} - R$ {hist_data['patrimonio_total']}")
        
        db.session.flush()
    
    def _seed_calendario_dividendo(self):
        """Seed de calendário de dividendos"""
        cal_data = self.scenario_data.get('calendario_dividendo', [])
        if not cal_data:
            return
        
        print(f"📅 Criando {len(cal_data)} entradas de calendário de dividendos...")
        
        assessora_id = list(self.references['assessoras'].values())[0] if self.references['assessoras'] else None
        
        for item in cal_data:
            usuario_id = self.references['usuarios'].get(item['usuario'])
            ativo_id = self.references['ativos'].get(item['ativo_ticker'])
            
            if not all([usuario_id, ativo_id]):
                print(f"⚠️  Referências faltando para calendário: {item}")
                continue
            
            cal = CalendarioDividendo(
                ativo_id=ativo_id,
                assessora_id=assessora_id,
                usuario_id=usuario_id,
                data_esperada=datetime.strptime(item['data_esperada'], '%Y-%m-%d').date(),
                tipo_provento=item.get('tipo_provento', 'dividendo'),
                yield_estimado=Decimal(str(item.get('yield_estimado', 0))) if item.get('yield_estimado') else None,
                valor_estimado=Decimal(str(item.get('valor_estimado', 0))) if item.get('valor_estimado') else None,
                quantidade=int(item.get('quantidade', 0)),
                status=item.get('status', 'previsto'),
                observacoes=item.get('observacoes')
            )
            
            db.session.add(cal)
            print(f"✅ Calendário criado: {item['ativo_ticker']} - {item['data_esperada']}")
        
        db.session.flush()
    
    def _seed_projecoes_renda(self):
        """Seed de projeções de renda"""
        proj_data = self.scenario_data.get('projecoes_renda', [])
        if not proj_data:
            return
        
        print(f"📊 Criando {len(proj_data)} projeções de renda...")
        
        assessora_id = list(self.references['assessoras'].values())[0] if self.references['assessoras'] else None
        
        for item in proj_data:
            usuario_id = self.references['usuarios'].get(item['usuario'])
            
            if not usuario_id:
                print(f"⚠️  Usuário não encontrado para projeção: {item['usuario']}")
                continue
            
            existing = ProjecaoRenda.query.filter_by(
                usuario_id=usuario_id,
                mes_ano=item['mes_ano']
            ).first()
            
            if existing:
                print(f"⏭️  Projeção já existe: {item['usuario']} - {item['mes_ano']}")
                continue
            
            proj = ProjecaoRenda(
                usuario_id=usuario_id,
                assessora_id=assessora_id,
                mes_ano=item['mes_ano'],
                renda_dividendos_projetada=Decimal(str(item.get('renda_dividendos_projetada', 0))),
                renda_jcp_projetada=Decimal(str(item.get('renda_jcp_projetada', 0))),
                renda_rendimentos_projetada=Decimal(str(item.get('renda_rendimentos_projetada', 0))),
                renda_total_mes=Decimal(str(item.get('renda_total_mes', 0))),
                renda_anual_projetada=Decimal(str(item['renda_anual_projetada'])) if item.get('renda_anual_projetada') else None
            )
            
            db.session.add(proj)
            print(f"✅ Projeção criada: {item['usuario']} - {item['mes_ano']}")
        
        db.session.flush()
    
    def _seed_regras_fiscais(self):
        """Seed de regras fiscais"""
        regras_data = self.scenario_data.get('regras_fiscais', [])
        if not regras_data:
            return
        
        print(f"⚖️  Criando {len(regras_data)} regras fiscais...")
        
        incidencia_map = {
            'lucro': IncidenciaImposto.LUCRO,
            'receita': IncidenciaImposto.RECEITA,
            'provento': IncidenciaImposto.PROVENTO,
            'operacao': IncidenciaImposto.OPERACAO
        }
        
        for item in regras_data:
            existing = RegraFiscal.query.filter_by(
                pais=item['pais'],
                tipo_ativo=item.get('tipo_ativo'),
                tipo_operacao=item.get('tipo_operacao')
            ).first()
            
            if existing:
                print(f"⏭️  Regra fiscal já existe: {item['pais']} {item.get('tipo_ativo')} {item.get('tipo_operacao')}")
                continue
            
            regra = RegraFiscal(
                pais=item['pais'],
                tipo_ativo=item.get('tipo_ativo'),
                tipo_operacao=item.get('tipo_operacao'),
                aliquota_ir=Decimal(str(item['aliquota_ir'])),
                valor_isencao=Decimal(str(item['valor_isencao'])) if item.get('valor_isencao') else None,
                incide_sobre=incidencia_map.get(item['incide_sobre'], IncidenciaImposto.LUCRO),
                descricao=item['descricao'],
                vigencia_inicio=datetime.strptime(item['vigencia_inicio'], '%Y-%m-%d').date(),
                vigencia_fim=datetime.strptime(item['vigencia_fim'], '%Y-%m-%d').date() if item.get('vigencia_fim') else None,
                ativa=item.get('ativa', True)
            )
            
            db.session.add(regra)
            print(f"✅ Regra fiscal criada: {item['pais']} {item.get('tipo_ativo')} {item.get('tipo_operacao')}")
        
        db.session.flush()

    def _seed_eventos_corporativos(self):
        """Seed de eventos corporativos"""
        eventos_data = self.scenario_data.get('eventos_corporativos', [])
        if not eventos_data:
            return

        print(f"📋 Criando {len(eventos_data)} eventos corporativos...")

        assessora_id = list(self.references['assessoras'].values())[0] if self.references['assessoras'] else None
        tipo_map = {e.value: e for e in TipoEventoCorporativo}

        for item in eventos_data:
            ativo_id = self.references['ativos'].get(item['ativo_ticker'])
            if not ativo_id:
                print(f"⚠️  Ativo não encontrado para evento: {item['ativo_ticker']}")
                continue

            tipo_raw = item.get('tipo_evento', 'outro')
            tipo_evento = tipo_map.get(tipo_raw)
            if not tipo_evento:
                print(f"⚠️  Tipo de evento inválido: {tipo_raw}")
                continue

            data_evento = datetime.strptime(item['data_evento'], '%Y-%m-%d').date()
            data_com = (
                datetime.strptime(item['data_com'], '%Y-%m-%d').date()
                if item.get('data_com') else None
            )

            existing = EventoCorporativo.query.filter_by(
                ativo_id=ativo_id,
                tipo_evento=tipo_evento,
                data_evento=data_evento,
            ).first()
            if existing:
                print(f"⏭️  Evento já existe: {item['ativo_ticker']} {tipo_raw} {data_evento}")
                continue

            evento = EventoCorporativo(
                ativo_id=ativo_id,
                assessora_id=assessora_id,
                tipo_evento=tipo_evento,
                data_evento=data_evento,
                data_com=data_com,
                proporcao=item.get('proporcao'),
                descricao=item['descricao'],
                impacto_posicoes=item.get('impacto_posicoes', False),
            )
            db.session.add(evento)
            print(f"✅ Evento corporativo criado: {item['ativo_ticker']} — {tipo_raw}")

        db.session.flush()

    def _seed_fontes_dados(self):
        """Seed de fontes de dados externas"""
        fontes_data = self.scenario_data.get('fontes_dados', [])
        if not fontes_data:
            return

        tipo_map = {
            'api': TipoFonteDados.API,
            'scraper': TipoFonteDados.SCRAPER,
            'manual': TipoFonteDados.MANUAL,
            'arquivo': TipoFonteDados.ARQUIVO,
            'outro': TipoFonteDados.OUTRO,
        }

        print(f"🔌 Criando {len(fontes_data)} fontes de dados...")

        for item in fontes_data:
            existing = FonteDados.query.filter_by(nome=item['nome']).first()
            if existing:
                print(f"⏭️  Fonte já existe: {item['nome']}")
                continue

            fonte = FonteDados(
                nome=item['nome'],
                tipo_fonte=tipo_map.get(item.get('tipo_fonte', 'api'), TipoFonteDados.API),
                url_base=item.get('url_base'),
                requer_autenticacao=item.get('requer_autenticacao', False),
                rate_limit=item.get('rate_limit'),
                ativa=item.get('ativa', True),
                prioridade=item.get('prioridade', 100),
                total_consultas=item.get('total_consultas', 0),
                total_erros=item.get('total_erros', 0),
                observacoes=item.get('observacoes'),
            )
            db.session.add(fonte)
            print(f"✅ Fonte criada: {item['nome']}")

        db.session.flush()

    def _seed_taxas_cambio(self):
        """Seed de taxas de câmbio históricas"""
        taxas_data = self.scenario_data.get('taxas_cambio', [])
        if not taxas_data:
            return

        print(f"💱 Criando {len(taxas_data)} taxas de câmbio...")

        for item in taxas_data:
            data_ref = datetime.strptime(item['data_referencia'], '%Y-%m-%d').date()
            existing = TaxaCambio.query.filter_by(
                par_moeda=item['par_moeda'],
                data_referencia=data_ref,
            ).first()
            if existing:
                continue

            taxa = TaxaCambio(
                par_moeda=item['par_moeda'],
                moeda_base=item['moeda_base'],
                moeda_cotacao=item['moeda_cotacao'],
                taxa=Decimal(str(item['taxa'])),
                data_referencia=data_ref,
                fonte=item.get('fonte', 'manual'),
            )
            db.session.add(taxa)

        db.session.flush()
        print(f"✅ Taxas de câmbio inseridas")

    def _seed_meta_alocacao(self):
        """Seed de metas de alocação por classe"""
        metas_data = self.scenario_data.get('meta_alocacao', [])
        if not metas_data:
            return

        assessora_id = list(self.references['assessoras'].values())[0] if self.references['assessoras'] else None
        print(f"🎯 Criando {len(metas_data)} metas de alocação...")

        for item in metas_data:
            usuario_id = self.references['usuarios'].get(item['usuario'])
            if not usuario_id:
                continue

            existing = MetaAlocacao.query.filter_by(
                usuario_id=usuario_id,
                classe=item['classe'],
            ).first()
            if existing:
                continue

            meta = MetaAlocacao(
                usuario_id=usuario_id,
                assessora_id=assessora_id,
                classe=item['classe'],
                percentual_target=Decimal(str(item['percentual_target'])),
                tolerancia_pct=Decimal(str(item.get('tolerancia_pct', 2.0))),
            )
            db.session.add(meta)
            print(f"✅ Meta alocação: {item['usuario']} — {item['classe']}")

        db.session.flush()

    def _seed_historico_preco(self):
        """Seed de histórico de preços"""
        hist_data = self.scenario_data.get('historico_preco', [])
        if not hist_data:
            return

        assessora_id = list(self.references['assessoras'].values())[0] if self.references['assessoras'] else None
        print(f"📉 Criando {len(hist_data)} registros de histórico de preços...")

        for item in hist_data:
            ativo_id = self.references['ativos'].get(item['ativo_ticker'])
            if not ativo_id:
                continue

            data_ref = datetime.strptime(item['data'], '%Y-%m-%d').date()
            existing = HistoricoPreco.query.filter_by(
                ativoid=ativo_id,
                data=data_ref,
            ).first()
            if existing:
                continue

            hist = HistoricoPreco(
                ativoid=ativo_id,
                assessora_id=assessora_id,
                data=data_ref,
                preco_abertura=Decimal(str(item['preco_abertura'])) if item.get('preco_abertura') else None,
                preco_fechamento=Decimal(str(item['preco_fechamento'])),
                preco_minimo=Decimal(str(item['preco_minimo'])) if item.get('preco_minimo') else None,
                preco_maximo=Decimal(str(item['preco_maximo'])) if item.get('preco_maximo') else None,
                volume=item.get('volume'),
            )
            db.session.add(hist)

        db.session.flush()
        print(f"✅ Histórico de preços inserido")

    def _seed_saldo_prejuizo(self):
        """Seed de saldos de prejuízo para compensação IR"""
        saldos_data = self.scenario_data.get('saldo_prejuizo', [])
        if not saldos_data:
            return

        assessora_id = list(self.references['assessoras'].values())[0] if self.references['assessoras'] else None
        print(f"📊 Criando {len(saldos_data)} saldos de prejuízo...")

        for item in saldos_data:
            usuario_id = self.references['usuarios'].get(item['usuario'])
            if not usuario_id:
                continue

            existing = SaldoPrejuizo.query.filter_by(
                usuario_id=usuario_id,
                categoria=item['categoria'],
                ano_mes=item['ano_mes'],
            ).first()
            if existing:
                continue

            saldo = SaldoPrejuizo(
                usuario_id=usuario_id,
                assessora_id=assessora_id,
                categoria=item['categoria'],
                ano_mes=item['ano_mes'],
                saldo=Decimal(str(item['saldo'])),
            )
            db.session.add(saldo)
            print(f"✅ Saldo prejuízo: {item['categoria']} {item['ano_mes']}")

        db.session.flush()


def main():
    """Função principal para teste standalone"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Carregador de cenários de teste JSON')
    parser.add_argument('scenario', help='Nome do cenário (sem .json)')
    
    args = parser.parse_args()
    
    loader = ScenarioLoader()
    loader.load_scenario(args.scenario)
    success = loader.seed_all()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
