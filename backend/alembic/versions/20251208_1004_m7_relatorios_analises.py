"""M7.1: Relatórios e Análises Avançadas

Revision ID: 20251208_1004_m7
Revises: [COLOCAR_ULTIMA_REVISION_AQUI]
Create Date: 2025-12-08 10:04:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251208_1004_m7'
down_revision = None  # SUBSTITUIR pela última revision existente
branch_labels = None
depends_on = None


def upgrade():
    """
    Cria tabelas do Módulo 7:
    - auditoria_relatorios
    - configuracoes_alertas
    - projecoes_renda
    - relatorios_performance
    """
    
    # ========================================
    # ENUMS M7
    # ========================================
    
    # Enum TipoRelatorio
    tipo_relatorio_enum = postgresql.ENUM(
        'portfolio', 'performance', 'renda_passiva', 'investimento', 'customizado',
        name='tiporelatorio',
        create_type=True
    )
    tipo_relatorio_enum.create(op.get_bind(), checkfirst=True)
    
    # Enum FormatoExport
    formato_export_enum = postgresql.ENUM(
        'visualizacao', 'pdf', 'excel',
        name='formatoexport',
        create_type=True
    )
    formato_export_enum.create(op.get_bind(), checkfirst=True)
    
    # Enum TipoAlerta
    tipo_alerta_enum = postgresql.ENUM(
        'queda_preco', 'alta_preco', 'dividendo_previsto', 'meta_rentabilidade',
        'volatilidade_alta', 'desvio_alocacao', 'noticias_ativo',
        name='tipoalerta',
        create_type=True
    )
    tipo_alerta_enum.create(op.get_bind(), checkfirst=True)
    
    # Enum OperadorCondicao
    operador_condicao_enum = postgresql.ENUM(
        '>', '<', '==', '>=', '<=', 'ENTRE',
        name='operadorcondicao',
        create_type=True
    )
    operador_condicao_enum.create(op.get_bind(), checkfirst=True)
    
    # Enum FrequenciaNotificacao
    frequencia_notificacao_enum = postgresql.ENUM(
        'imediata', 'diaria', 'semanal', 'mensal',
        name='frequencianotificacao',
        create_type=True
    )
    frequencia_notificacao_enum.create(op.get_bind(), checkfirst=True)
    
    # ========================================
    # TABELA: auditoria_relatorios
    # ========================================
    op.create_table(
        'auditoria_relatorios',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, comment='Identificador único da auditoria'),
        sa.Column('usuario_id', postgresql.UUID(as_uuid=True), nullable=False, comment='ID do usuário proprietário'),
        sa.Column('tipo_relatorio', tipo_relatorio_enum, nullable=False, comment='Tipo do relatório gerado'),
        sa.Column('data_inicio', sa.Date(), nullable=True, comment='Data início do período analisado'),
        sa.Column('data_fim', sa.Date(), nullable=True, comment='Data fim do período analisado'),
        sa.Column('filtros', postgresql.JSON(astext_type=sa.Text()), nullable=True, comment='Filtros aplicados (país, mercado, setor, classe_ativo)'),
        sa.Column('resultado_json', postgresql.JSON(astext_type=sa.Text()), nullable=True, comment='Dados completos do relatório em JSON'),
        sa.Column('timestamp_criacao', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'), comment='Timestamp de criação do relatório'),
        sa.Column('timestamp_download', sa.DateTime(timezone=True), nullable=True, comment='Timestamp do primeiro download (null se nunca baixado)'),
        sa.Column('formato_export', formato_export_enum, nullable=False, server_default='visualizacao', comment='Formato de exportação'),
        sa.Column('chave_api_auditoria', sa.String(length=64), nullable=True, comment='Chave para rastreamento de API'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'), comment='Data de criação do registro'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'), comment='Data da última atualização'),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuario.id'], ondelete='CASCADE'),
        sa.CheckConstraint(
            "data_inicio IS NULL OR data_fim IS NULL OR data_inicio <= data_fim",
            name='auditoria_relatorio_datas_validas'
        ),
        
        comment='Tabela de auditoria de relatórios gerados'
    )
    
    # Índices auditoria_relatorios
    op.create_index('ix_auditoria_relatorios_usuario_id', 'auditoria_relatorios', ['usuario_id'])
    op.create_index('ix_auditoria_relatorios_tipo_relatorio', 'auditoria_relatorios', ['tipo_relatorio'])
    op.create_index('ix_auditoria_relatorios_data_inicio', 'auditoria_relatorios', ['data_inicio'])
    op.create_index('ix_auditoria_relatorios_data_fim', 'auditoria_relatorios', ['data_fim'])
    op.create_index('ix_auditoria_relatorios_timestamp_criacao', 'auditoria_relatorios', ['timestamp_criacao'])
    op.create_index('ix_auditoria_relatorios_timestamp_download', 'auditoria_relatorios', ['timestamp_download'])
    op.create_index('ix_auditoria_relatorios_formato_export', 'auditoria_relatorios', ['formato_export'])
    op.create_index('ix_auditoria_relatorios_chave_api_auditoria', 'auditoria_relatorios', ['chave_api_auditoria'])
    
    # ========================================
    # TABELA: configuracoes_alertas
    # ========================================
    op.create_table(
        'configuracoes_alertas',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, comment='Identificador único do alerta'),
        sa.Column('usuario_id', postgresql.UUID(as_uuid=True), nullable=False, comment='ID do usuário proprietário'),
        sa.Column('ativo_id', postgresql.UUID(as_uuid=True), nullable=True, comment='ID do ativo (opcional)'),
        sa.Column('portfolio_id', postgresql.UUID(as_uuid=True), nullable=True, comment='ID do portfolio (opcional)'),
        sa.Column('nome', sa.String(length=200), nullable=False, comment="Nome descritivo do alerta (ex: 'Alerta PETR4 > 30%')"),
        sa.Column('tipo_alerta', tipo_alerta_enum, nullable=False, comment='Tipo do alerta'),
        sa.Column('condicao_valor', sa.Numeric(precision=18, scale=6), nullable=False, comment='Valor threshold da condição'),
        sa.Column('condicao_operador', operador_condicao_enum, nullable=False, server_default='>', comment='Operador de comparação (>, <, ==, >=, <=, ENTRE)'),
        sa.Column('condicao_valor2', sa.Numeric(precision=18, scale=6), nullable=True, comment='Segundo valor (usado quando operador é ENTRE)'),
        sa.Column('ativo', sa.Boolean(), nullable=False, server_default=sa.text('true'), comment='Indica se o alerta está ativo'),
        sa.Column('frequencia_notificacao', frequencia_notificacao_enum, nullable=False, server_default='imediata', comment='Frequência de notificação'),
        sa.Column('canais_entrega', postgresql.ARRAY(sa.String()), nullable=False, server_default='{email,webapp}', comment='Canais de entrega (email, webapp, sms, telegram)'),
        sa.Column('timestamp_criacao', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'), comment='Data de criação do alerta'),
        sa.Column('timestamp_ultimo_acionamento', sa.DateTime(timezone=True), nullable=True, comment='Data do último acionamento (null se nunca acionado)'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'), comment='Data de criação do registro'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'), comment='Data da última atualização'),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuario.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['ativo_id'], ['ativo.id'], ondelete='CASCADE'),
        # sa.ForeignKeyConstraint(['portfolio_id'], ['portfolio.id'], ondelete='CASCADE'),  # Descomentar quando Portfolio existir
        sa.CheckConstraint(
            "condicao_operador != 'ENTRE' OR condicao_valor2 IS NOT NULL",
            name='alerta_entre_requer_valor2'
        ),
        sa.CheckConstraint(
            "condicao_operador = 'ENTRE' OR condicao_valor2 IS NULL",
            name='alerta_valor2_apenas_entre'
        ),
        
        comment='Tabela de configurações de alertas'
    )
    
    # Índices configuracoes_alertas
    op.create_index('ix_configuracoes_alertas_usuario_id', 'configuracoes_alertas', ['usuario_id'])
    op.create_index('ix_configuracoes_alertas_ativo_id', 'configuracoes_alertas', ['ativo_id'])
    op.create_index('ix_configuracoes_alertas_portfolio_id', 'configuracoes_alertas', ['portfolio_id'])
    op.create_index('ix_configuracoes_alertas_tipo_alerta', 'configuracoes_alertas', ['tipo_alerta'])
    op.create_index('ix_configuracoes_alertas_ativo', 'configuracoes_alertas', ['ativo'])
    op.create_index('ix_configuracoes_alertas_timestamp_criacao', 'configuracoes_alertas', ['timestamp_criacao'])
    op.create_index('ix_configuracoes_alertas_timestamp_ultimo_acionamento', 'configuracoes_alertas', ['timestamp_ultimo_acionamento'])
    
    # ========================================
    # TABELA: projecoes_renda
    # ========================================
    op.create_table(
        'projecoes_renda',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, comment='Identificador único da projeção'),
        sa.Column('usuario_id', postgresql.UUID(as_uuid=True), nullable=False, comment='ID do usuário proprietário'),
        sa.Column('portfolio_id', postgresql.UUID(as_uuid=True), nullable=True, comment='ID do portfolio (opcional, null = todos portfolios)'),
        sa.Column('mes_ano', sa.String(length=7), nullable=False, comment='Mês/ano da projeção (ex: 2025-12)'),
        sa.Column('renda_dividendos_projetada', sa.Numeric(precision=18, scale=2), nullable=False, server_default='0', comment='Renda projetada de dividendos'),
        sa.Column('renda_jcp_projetada', sa.Numeric(precision=18, scale=2), nullable=False, server_default='0', comment='Renda projetada de JCP'),
        sa.Column('renda_rendimento_projetada', sa.Numeric(precision=18, scale=2), nullable=False, server_default='0', comment='Renda projetada de rendimentos (FIIs, REITs, etc)'),
        sa.Column('renda_total_mes', sa.Numeric(precision=18, scale=2), nullable=False, server_default='0', comment='Soma total de renda do mês'),
        sa.Column('renda_anual_projetada', sa.Numeric(precision=18, scale=2), nullable=True, comment='Projeção de renda anual (12 meses)'),
        sa.Column('crescimento_percentual_mes', sa.Numeric(precision=8, scale=4), nullable=True, comment='% crescimento em relação ao mês anterior'),
        sa.Column('crescimento_percentual_ano', sa.Numeric(precision=8, scale=4), nullable=True, comment='% crescimento em relação ao ano anterior'),
        sa.Column('ativos_contribuindo', sa.Integer(), nullable=False, server_default='0', comment='Quantidade de ativos contribuindo com renda'),
        sa.Column('timestamp_calculo', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'), comment='Timestamp do cálculo da projeção'),
        sa.Column('metadados', postgresql.JSON(astext_type=sa.Text()), nullable=True, comment='Detalhes por ativo (JSON com breakdown)'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'), comment='Data de criação do registro'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'), comment='Data da última atualização'),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuario.id'], ondelete='CASCADE'),
        # sa.ForeignKeyConstraint(['portfolio_id'], ['portfolio.id'], ondelete='CASCADE'),  # Descomentar quando Portfolio existir
        sa.UniqueConstraint('usuario_id', 'portfolio_id', 'mes_ano', name='unique_projecao_usuario_portfolio_mes'),
        sa.CheckConstraint('renda_dividendos_projetada >= 0', name='projecao_dividendos_positivo'),
        sa.CheckConstraint('renda_jcp_projetada >= 0', name='projecao_jcp_positivo'),
        sa.CheckConstraint('renda_rendimento_projetada >= 0', name='projecao_rendimento_positivo'),
        sa.CheckConstraint('renda_total_mes >= 0', name='projecao_total_positivo'),
        sa.CheckConstraint('ativos_contribuindo >= 0', name='projecao_ativos_positivo'),
        sa.CheckConstraint("mes_ano ~ '^[0-9]{4}-[0-9]{2}$'", name='projecao_mesano_formato'),
        
        comment='Tabela de projeções de renda passiva mensal'
    )
    
    # Índices projecoes_renda
    op.create_index('ix_projecoes_renda_usuario_id', 'projecoes_renda', ['usuario_id'])
    op.create_index('ix_projecoes_renda_portfolio_id', 'projecoes_renda', ['portfolio_id'])
    op.create_index('ix_projecoes_renda_mes_ano', 'projecoes_renda', ['mes_ano'])
    op.create_index('ix_projecoes_renda_timestamp_calculo', 'projecoes_renda', ['timestamp_calculo'])
    
    # ========================================
    # TABELA: relatorios_performance
    # ========================================
    op.create_table(
        'relatorios_performance',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, comment='Identificador único do relatório'),
        sa.Column('usuario_id', postgresql.UUID(as_uuid=True), nullable=False, comment='ID do usuário proprietário'),
        sa.Column('portfolio_id', postgresql.UUID(as_uuid=True), nullable=True, comment='ID do portfolio (opcional, null = todos portfolios)'),
        sa.Column('periodo_inicio', sa.Date(), nullable=False, comment='Data início do período analisado'),
        sa.Column('periodo_fim', sa.Date(), nullable=False, comment='Data fim do período analisado'),
        sa.Column('retorno_bruto_percentual', sa.Numeric(precision=10, scale=4), nullable=True, comment='Retorno bruto em % (sem descontar custos)'),
        sa.Column('retorno_liquido_percentual', sa.Numeric(precision=10, scale=4), nullable=True, comment='Retorno líquido em % (após custos e impostos)'),
        sa.Column('volatilidade_percentual', sa.Numeric(precision=10, scale=4), nullable=True, comment='Volatilidade anualizada em %'),
        sa.Column('indice_sharpe', sa.Numeric(precision=10, scale=4), nullable=True, comment='Índice de Sharpe (risk-adjusted return)'),
        sa.Column('indice_sortino', sa.Numeric(precision=10, scale=4), nullable=True, comment='Índice de Sortino (downside risk)'),
        sa.Column('max_drawdown_percentual', sa.Numeric(precision=10, scale=4), nullable=True, comment='Máximo drawdown em % (maior queda do pico)'),
        sa.Column('taxa_interna_retorno_irr', sa.Numeric(precision=10, scale=4), nullable=True, comment='Taxa Interna de Retorno (IRR) anual em %'),
        sa.Column('beta_mercado', sa.Numeric(precision=8, scale=4), nullable=True, comment='Beta em relação ao mercado (sensibilidade)'),
        sa.Column('alfa_de_jensen', sa.Numeric(precision=10, scale=4), nullable=True, comment='Alfa de Jensen (retorno excedente vs esperado)'),
        sa.Column('valor_patrimonial_inicio', sa.Numeric(precision=18, scale=2), nullable=True, comment='Valor patrimonial no início do período'),
        sa.Column('valor_patrimonial_fim', sa.Numeric(precision=18, scale=2), nullable=True, comment='Valor patrimonial no fim do período'),
        sa.Column('alocacao_por_classe', postgresql.JSON(astext_type=sa.Text()), nullable=True, comment='Distribuição por classe de ativo (JSON)'),
        sa.Column('alocacao_por_setor', postgresql.JSON(astext_type=sa.Text()), nullable=True, comment='Distribuição por setor (JSON)'),
        sa.Column('alocacao_por_pais', postgresql.JSON(astext_type=sa.Text()), nullable=True, comment='Distribuição por país (JSON)'),
        sa.Column('rentabilidade_por_ativo', postgresql.JSON(astext_type=sa.Text()), nullable=True, comment='Rentabilidade de cada ativo (JSON)'),
        sa.Column('timestamp_calculo', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'), comment='Timestamp do cálculo do relatório'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'), comment='Data de criação do registro'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'), comment='Data da última atualização'),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuario.id'], ondelete='CASCADE'),
        # sa.ForeignKeyConstraint(['portfolio_id'], ['portfolio.id'], ondelete='CASCADE'),  # Descomentar quando Portfolio existir
        sa.CheckConstraint('periodo_inicio <= periodo_fim', name='performance_periodo_valido'),
        sa.CheckConstraint('valor_patrimonial_inicio IS NULL OR valor_patrimonial_inicio >= 0', name='performance_patrimonio_inicio_positivo'),
        sa.CheckConstraint('valor_patrimonial_fim IS NULL OR valor_patrimonial_fim >= 0', name='performance_patrimonio_fim_positivo'),
        
        comment='Tabela de relatórios de performance'
    )
    
    # Índices relatorios_performance
    op.create_index('ix_relatorios_performance_usuario_id', 'relatorios_performance', ['usuario_id'])
    op.create_index('ix_relatorios_performance_portfolio_id', 'relatorios_performance', ['portfolio_id'])
    op.create_index('ix_relatorios_performance_periodo_inicio', 'relatorios_performance', ['periodo_inicio'])
    op.create_index('ix_relatorios_performance_periodo_fim', 'relatorios_performance', ['periodo_fim'])
    op.create_index('ix_relatorios_performance_timestamp_calculo', 'relatorios_performance', ['timestamp_calculo'])


def downgrade():
    """
    Remove tabelas do Módulo 7
    """
    
    # Drop tabelas
    op.drop_table('relatorios_performance')
    op.drop_table('projecoes_renda')
    op.drop_table('configuracoes_alertas')
    op.drop_table('auditoria_relatorios')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS frequencianotificacao CASCADE')
    op.execute('DROP TYPE IF EXISTS operadorcondicao CASCADE')
    op.execute('DROP TYPE IF EXISTS tipoalerta CASCADE')
    op.execute('DROP TYPE IF EXISTS formatoexport CASCADE')
    op.execute('DROP TYPE IF EXISTS tiporelatorio CASCADE')
