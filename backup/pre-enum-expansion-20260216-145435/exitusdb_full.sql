--
-- PostgreSQL database dump
--

\restrict YnvsWSHL3LVi5oKitdQsVovqeAlTbWZqRV5mX5tgxK2hBWKWEOIwWEAkpsDqw0i

-- Dumped from database version 16.11 (Debian 16.11-1.pgdg13+1)
-- Dumped by pg_dump version 16.11 (Debian 16.11-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: classeativo; Type: TYPE; Schema: public; Owner: exitus
--

CREATE TYPE public.classeativo AS ENUM (
    'RENDA_VARIAVEL',
    'RENDA_FIXA',
    'CRIPTO',
    'HIBRIDO'
);


ALTER TYPE public.classeativo OWNER TO exitus;

--
-- Name: formatoexport; Type: TYPE; Schema: public; Owner: exitus
--

CREATE TYPE public.formatoexport AS ENUM (
    'visualizacao',
    'pdf',
    'excel'
);


ALTER TYPE public.formatoexport OWNER TO exitus;

--
-- Name: frequencianotificacao; Type: TYPE; Schema: public; Owner: exitus
--

CREATE TYPE public.frequencianotificacao AS ENUM (
    'imediata',
    'diaria',
    'semanal',
    'mensal'
);


ALTER TYPE public.frequencianotificacao OWNER TO exitus;

--
-- Name: incidenciaimposto; Type: TYPE; Schema: public; Owner: exitus
--

CREATE TYPE public.incidenciaimposto AS ENUM (
    'LUCRO',
    'RECEITA',
    'PROVENTO',
    'OPERACAO'
);


ALTER TYPE public.incidenciaimposto OWNER TO exitus;

--
-- Name: operadorcondicao; Type: TYPE; Schema: public; Owner: exitus
--

CREATE TYPE public.operadorcondicao AS ENUM (
    '>',
    '<',
    '==',
    '>=',
    '<=',
    'ENTRE'
);


ALTER TYPE public.operadorcondicao OWNER TO exitus;

--
-- Name: tipoalerta; Type: TYPE; Schema: public; Owner: exitus
--

CREATE TYPE public.tipoalerta AS ENUM (
    'queda_preco',
    'alta_preco',
    'dividendo_previsto',
    'meta_rentabilidade',
    'volatilidade_alta',
    'desvio_alocacao',
    'noticias_ativo'
);


ALTER TYPE public.tipoalerta OWNER TO exitus;

--
-- Name: tipoativo; Type: TYPE; Schema: public; Owner: exitus
--

CREATE TYPE public.tipoativo AS ENUM (
    'ACAO',
    'FII',
    'REIT',
    'BOND',
    'ETF',
    'CRIPTO',
    'OUTRO'
);


ALTER TYPE public.tipoativo OWNER TO exitus;

--
-- Name: tipocorretora; Type: TYPE; Schema: public; Owner: exitus
--

CREATE TYPE public.tipocorretora AS ENUM (
    'CORRETORA',
    'EXCHANGE'
);


ALTER TYPE public.tipocorretora OWNER TO exitus;

--
-- Name: tipoeventocorporativo; Type: TYPE; Schema: public; Owner: exitus
--

CREATE TYPE public.tipoeventocorporativo AS ENUM (
    'SPLIT',
    'GRUPAMENTO',
    'BONIFICACAO',
    'DIREITO_SUBSCRICAO',
    'FUSAO',
    'CISAO',
    'INCORPORACAO',
    'MUDANCA_TICKER',
    'DESLISTAGEM',
    'RELISTING',
    'CANCELAMENTO',
    'OUTRO'
);


ALTER TYPE public.tipoeventocorporativo OWNER TO exitus;

--
-- Name: tipoferiado; Type: TYPE; Schema: public; Owner: exitus
--

CREATE TYPE public.tipoferiado AS ENUM (
    'NACIONAL',
    'BOLSA',
    'PONTE',
    'FECHAMENTO_ANTECIPADO',
    'MANUTENCAO',
    'OUTRO'
);


ALTER TYPE public.tipoferiado OWNER TO exitus;

--
-- Name: tipofontedados; Type: TYPE; Schema: public; Owner: exitus
--

CREATE TYPE public.tipofontedados AS ENUM (
    'API',
    'SCRAPER',
    'MANUAL',
    'ARQUIVO',
    'OUTRO'
);


ALTER TYPE public.tipofontedados OWNER TO exitus;

--
-- Name: tipomovimentacao; Type: TYPE; Schema: public; Owner: exitus
--

CREATE TYPE public.tipomovimentacao AS ENUM (
    'DEPOSITO',
    'SAQUE',
    'TRANSFERENCIA_ENVIADA',
    'TRANSFERENCIA_RECEBIDA',
    'CREDITO_PROVENTO',
    'PAGAMENTO_TAXA',
    'PAGAMENTO_IMPOSTO',
    'AJUSTE',
    'OUTRO'
);


ALTER TYPE public.tipomovimentacao OWNER TO exitus;

--
-- Name: tipooperacao; Type: TYPE; Schema: public; Owner: exitus
--

CREATE TYPE public.tipooperacao AS ENUM (
    'COMPRA',
    'VENDA'
);


ALTER TYPE public.tipooperacao OWNER TO exitus;

--
-- Name: tipoprovento; Type: TYPE; Schema: public; Owner: exitus
--

CREATE TYPE public.tipoprovento AS ENUM (
    'DIVIDENDO',
    'JCP',
    'RENDIMENTO',
    'CUPOM',
    'BONIFICACAO',
    'DIREITO_SUBSCRICAO',
    'OUTRO'
);


ALTER TYPE public.tipoprovento OWNER TO exitus;

--
-- Name: tiporelatorio; Type: TYPE; Schema: public; Owner: exitus
--

CREATE TYPE public.tiporelatorio AS ENUM (
    'portfolio',
    'performance',
    'renda_passiva',
    'investimento',
    'customizado'
);


ALTER TYPE public.tiporelatorio OWNER TO exitus;

--
-- Name: tipotransacao; Type: TYPE; Schema: public; Owner: exitus
--

CREATE TYPE public.tipotransacao AS ENUM (
    'COMPRA',
    'VENDA',
    'DIVIDENDO',
    'JCP',
    'BONIFICACAO',
    'DESDOBRAMENTO',
    'GRUPAMENTO'
);


ALTER TYPE public.tipotransacao OWNER TO exitus;

--
-- Name: userrole; Type: TYPE; Schema: public; Owner: exitus
--

CREATE TYPE public.userrole AS ENUM (
    'ADMIN',
    'USER',
    'READONLY'
);


ALTER TYPE public.userrole OWNER TO exitus;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: exitus
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO exitus;

--
-- Name: alertas; Type: TABLE; Schema: public; Owner: exitus
--

CREATE TABLE public.alertas (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    usuario_id uuid NOT NULL,
    nome character varying(100) NOT NULL,
    tipo_alerta character varying(50) NOT NULL,
    ticker character varying(20),
    condicao_operador character varying(10) NOT NULL,
    condicao_valor numeric(18,4) NOT NULL,
    condicao_valor2 numeric(18,4),
    ativo boolean DEFAULT true NOT NULL,
    frequencia_notificacao character varying(20) NOT NULL,
    canais_entrega jsonb DEFAULT '[]'::jsonb NOT NULL,
    total_acionamentos integer DEFAULT 0,
    timestamp_ultimo_acionamento timestamp without time zone,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.alertas OWNER TO exitus;

--
-- Name: ativo; Type: TABLE; Schema: public; Owner: exitus
--

CREATE TABLE public.ativo (
    id uuid NOT NULL,
    ticker character varying(20) NOT NULL,
    nome character varying(200) NOT NULL,
    tipo public.tipoativo NOT NULL,
    classe public.classeativo NOT NULL,
    mercado character varying(10) NOT NULL,
    moeda character varying(3) NOT NULL,
    preco_atual numeric(18,6),
    data_ultima_cotacao timestamp with time zone,
    dividend_yield numeric(8,4),
    p_l numeric(10,2),
    p_vp numeric(10,2),
    roe numeric(8,4),
    ativo boolean NOT NULL,
    deslistado boolean NOT NULL,
    data_deslistagem date,
    observacoes text,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    preco_teto numeric(18,6),
    beta numeric(8,4),
    CONSTRAINT ativo_nome_min_length CHECK ((length((nome)::text) >= 2)),
    CONSTRAINT ativo_preco_positivo CHECK (((preco_atual IS NULL) OR (preco_atual >= (0)::numeric))),
    CONSTRAINT ativo_ticker_min_length CHECK ((length((ticker)::text) >= 1))
);


ALTER TABLE public.ativo OWNER TO exitus;

--
-- Name: auditoria_relatorios; Type: TABLE; Schema: public; Owner: exitus
--

CREATE TABLE public.auditoria_relatorios (
    id uuid NOT NULL,
    usuario_id uuid NOT NULL,
    tipo_relatorio character varying(50) NOT NULL,
    data_inicio date,
    data_fim date,
    filtros json,
    resultado_json json,
    timestamp_criacao timestamp with time zone DEFAULT now() NOT NULL,
    timestamp_download timestamp with time zone,
    formato_export character varying(50) DEFAULT 'visualizacao'::public.formatoexport NOT NULL,
    chave_api_auditoria character varying(64),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT auditoria_relatorio_datas_validas CHECK (((data_inicio IS NULL) OR (data_fim IS NULL) OR (data_inicio <= data_fim)))
);


ALTER TABLE public.auditoria_relatorios OWNER TO exitus;

--
-- Name: TABLE auditoria_relatorios; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON TABLE public.auditoria_relatorios IS 'Tabela de auditoria de relatórios gerados';


--
-- Name: COLUMN auditoria_relatorios.id; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.auditoria_relatorios.id IS 'Identificador único da auditoria';


--
-- Name: COLUMN auditoria_relatorios.usuario_id; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.auditoria_relatorios.usuario_id IS 'ID do usuário proprietário';


--
-- Name: COLUMN auditoria_relatorios.tipo_relatorio; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.auditoria_relatorios.tipo_relatorio IS 'Tipo do relatório gerado';


--
-- Name: COLUMN auditoria_relatorios.data_inicio; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.auditoria_relatorios.data_inicio IS 'Data início do período analisado';


--
-- Name: COLUMN auditoria_relatorios.data_fim; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.auditoria_relatorios.data_fim IS 'Data fim do período analisado';


--
-- Name: COLUMN auditoria_relatorios.filtros; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.auditoria_relatorios.filtros IS 'Filtros aplicados (país, mercado, setor, classe_ativo)';


--
-- Name: COLUMN auditoria_relatorios.resultado_json; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.auditoria_relatorios.resultado_json IS 'Dados completos do relatório em JSON';


--
-- Name: COLUMN auditoria_relatorios.timestamp_criacao; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.auditoria_relatorios.timestamp_criacao IS 'Timestamp de criação do relatório';


--
-- Name: COLUMN auditoria_relatorios.timestamp_download; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.auditoria_relatorios.timestamp_download IS 'Timestamp do primeiro download (null se nunca baixado)';


--
-- Name: COLUMN auditoria_relatorios.formato_export; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.auditoria_relatorios.formato_export IS 'Formato de exportação';


--
-- Name: COLUMN auditoria_relatorios.chave_api_auditoria; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.auditoria_relatorios.chave_api_auditoria IS 'Chave para rastreamento de API';


--
-- Name: COLUMN auditoria_relatorios.created_at; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.auditoria_relatorios.created_at IS 'Data de criação do registro';


--
-- Name: COLUMN auditoria_relatorios.updated_at; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.auditoria_relatorios.updated_at IS 'Data da última atualização';


--
-- Name: configuracoes_alertas; Type: TABLE; Schema: public; Owner: exitus
--

CREATE TABLE public.configuracoes_alertas (
    id uuid NOT NULL,
    usuario_id uuid NOT NULL,
    ativo_id uuid,
    portfolio_id uuid,
    nome character varying(200) NOT NULL,
    tipo_alerta public.tipoalerta NOT NULL,
    condicao_valor numeric(18,6) NOT NULL,
    condicao_operador public.operadorcondicao DEFAULT '>'::public.operadorcondicao NOT NULL,
    condicao_valor2 numeric(18,6),
    ativo boolean DEFAULT true NOT NULL,
    frequencia_notificacao public.frequencianotificacao DEFAULT 'imediata'::public.frequencianotificacao NOT NULL,
    canais_entrega character varying[] DEFAULT '{email,webapp}'::character varying[] NOT NULL,
    timestamp_criacao timestamp with time zone DEFAULT now() NOT NULL,
    timestamp_ultimo_acionamento timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT alerta_entre_requer_valor2 CHECK (((condicao_operador <> 'ENTRE'::public.operadorcondicao) OR (condicao_valor2 IS NOT NULL))),
    CONSTRAINT alerta_valor2_apenas_entre CHECK (((condicao_operador = 'ENTRE'::public.operadorcondicao) OR (condicao_valor2 IS NULL)))
);


ALTER TABLE public.configuracoes_alertas OWNER TO exitus;

--
-- Name: TABLE configuracoes_alertas; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON TABLE public.configuracoes_alertas IS 'Tabela de configurações de alertas';


--
-- Name: COLUMN configuracoes_alertas.id; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.configuracoes_alertas.id IS 'Identificador único do alerta';


--
-- Name: COLUMN configuracoes_alertas.usuario_id; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.configuracoes_alertas.usuario_id IS 'ID do usuário proprietário';


--
-- Name: COLUMN configuracoes_alertas.ativo_id; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.configuracoes_alertas.ativo_id IS 'ID do ativo (opcional)';


--
-- Name: COLUMN configuracoes_alertas.portfolio_id; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.configuracoes_alertas.portfolio_id IS 'ID do portfolio (opcional)';


--
-- Name: COLUMN configuracoes_alertas.nome; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.configuracoes_alertas.nome IS 'Nome descritivo do alerta (ex: ''Alerta PETR4 > 30%'')';


--
-- Name: COLUMN configuracoes_alertas.tipo_alerta; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.configuracoes_alertas.tipo_alerta IS 'Tipo do alerta';


--
-- Name: COLUMN configuracoes_alertas.condicao_valor; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.configuracoes_alertas.condicao_valor IS 'Valor threshold da condição';


--
-- Name: COLUMN configuracoes_alertas.condicao_operador; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.configuracoes_alertas.condicao_operador IS 'Operador de comparação (>, <, ==, >=, <=, ENTRE)';


--
-- Name: COLUMN configuracoes_alertas.condicao_valor2; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.configuracoes_alertas.condicao_valor2 IS 'Segundo valor (usado quando operador é ENTRE)';


--
-- Name: COLUMN configuracoes_alertas.ativo; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.configuracoes_alertas.ativo IS 'Indica se o alerta está ativo';


--
-- Name: COLUMN configuracoes_alertas.frequencia_notificacao; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.configuracoes_alertas.frequencia_notificacao IS 'Frequência de notificação';


--
-- Name: COLUMN configuracoes_alertas.canais_entrega; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.configuracoes_alertas.canais_entrega IS 'Canais de entrega (email, webapp, sms, telegram)';


--
-- Name: COLUMN configuracoes_alertas.timestamp_criacao; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.configuracoes_alertas.timestamp_criacao IS 'Data de criação do alerta';


--
-- Name: COLUMN configuracoes_alertas.timestamp_ultimo_acionamento; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.configuracoes_alertas.timestamp_ultimo_acionamento IS 'Data do último acionamento (null se nunca acionado)';


--
-- Name: COLUMN configuracoes_alertas.created_at; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.configuracoes_alertas.created_at IS 'Data de criação do registro';


--
-- Name: COLUMN configuracoes_alertas.updated_at; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.configuracoes_alertas.updated_at IS 'Data da última atualização';


--
-- Name: corretora; Type: TABLE; Schema: public; Owner: exitus
--

CREATE TABLE public.corretora (
    id uuid NOT NULL,
    usuario_id uuid NOT NULL,
    nome character varying(100) NOT NULL,
    tipo public.tipocorretora NOT NULL,
    pais character varying(2) NOT NULL,
    moeda_padrao character varying(3) NOT NULL,
    saldo_atual numeric(18,2) NOT NULL,
    ativa boolean NOT NULL,
    observacoes text,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    CONSTRAINT corretora_moeda_iso_format CHECK (((moeda_padrao)::text ~* '^[A-Z]{3}$'::text)),
    CONSTRAINT corretora_nome_min_length CHECK ((length((nome)::text) >= 2)),
    CONSTRAINT corretora_pais_iso_format CHECK (((pais)::text ~* '^[A-Z]{2}$'::text)),
    CONSTRAINT corretora_saldo_positivo CHECK ((saldo_atual >= (0)::numeric))
);


ALTER TABLE public.corretora OWNER TO exitus;

--
-- Name: evento_corporativo; Type: TABLE; Schema: public; Owner: exitus
--

CREATE TABLE public.evento_corporativo (
    id uuid NOT NULL,
    ativo_id uuid NOT NULL,
    ativo_novo_id uuid,
    tipo_evento public.tipoeventocorporativo NOT NULL,
    data_evento date NOT NULL,
    data_com date,
    proporcao character varying(20),
    descricao text NOT NULL,
    impacto_posicoes boolean NOT NULL,
    observacoes text,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    CONSTRAINT evento_data_com_valida CHECK (((data_com IS NULL) OR (data_com <= data_evento)))
);


ALTER TABLE public.evento_corporativo OWNER TO exitus;

--
-- Name: TABLE evento_corporativo; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON TABLE public.evento_corporativo IS 'Tabela de eventos corporativos que afetam ativos';


--
-- Name: COLUMN evento_corporativo.id; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.evento_corporativo.id IS 'Identificador único do evento';


--
-- Name: COLUMN evento_corporativo.ativo_id; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.evento_corporativo.ativo_id IS 'ID do ativo afetado pelo evento';


--
-- Name: COLUMN evento_corporativo.ativo_novo_id; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.evento_corporativo.ativo_novo_id IS 'ID do novo ativo (fusões, mudanças de ticker)';


--
-- Name: COLUMN evento_corporativo.tipo_evento; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.evento_corporativo.tipo_evento IS 'Tipo do evento corporativo';


--
-- Name: COLUMN evento_corporativo.data_evento; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.evento_corporativo.data_evento IS 'Data do evento';


--
-- Name: COLUMN evento_corporativo.data_com; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.evento_corporativo.data_com IS 'Data COM (último dia para ter direito ao evento)';


--
-- Name: COLUMN evento_corporativo.proporcao; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.evento_corporativo.proporcao IS 'Proporção do evento (ex: ''2:1'', ''1:10'', ''1:1.5'')';


--
-- Name: COLUMN evento_corporativo.descricao; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.evento_corporativo.descricao IS 'Descrição detalhada do evento';


--
-- Name: COLUMN evento_corporativo.impacto_posicoes; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.evento_corporativo.impacto_posicoes IS 'Indica se as posições já foram ajustadas';


--
-- Name: COLUMN evento_corporativo.observacoes; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.evento_corporativo.observacoes IS 'Observações adicionais sobre o evento';


--
-- Name: COLUMN evento_corporativo.created_at; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.evento_corporativo.created_at IS 'Data de criação do registro';


--
-- Name: COLUMN evento_corporativo.updated_at; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.evento_corporativo.updated_at IS 'Data da última atualização';


--
-- Name: feriado_mercado; Type: TABLE; Schema: public; Owner: exitus
--

CREATE TABLE public.feriado_mercado (
    id uuid NOT NULL,
    pais character varying(2) NOT NULL,
    mercado character varying(20),
    data_feriado date NOT NULL,
    tipo_feriado public.tipoferiado NOT NULL,
    nome character varying(200) NOT NULL,
    horario_fechamento time without time zone,
    recorrente boolean NOT NULL,
    observacoes text,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    CONSTRAINT feriado_nome_min_length CHECK ((length((nome)::text) >= 3)),
    CONSTRAINT feriado_pais_iso_format CHECK (((pais)::text ~* '^[A-Z]{2}$'::text))
);


ALTER TABLE public.feriado_mercado OWNER TO exitus;

--
-- Name: TABLE feriado_mercado; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON TABLE public.feriado_mercado IS 'Tabela de feriados e dias sem pregão nos mercados';


--
-- Name: COLUMN feriado_mercado.id; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.feriado_mercado.id IS 'Identificador único do feriado';


--
-- Name: COLUMN feriado_mercado.pais; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.feriado_mercado.pais IS 'Código ISO do país (BR, US, etc.)';


--
-- Name: COLUMN feriado_mercado.mercado; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.feriado_mercado.mercado IS 'Mercado/bolsa específica (B3, NYSE, NASDAQ, etc.) - NULL = todos';


--
-- Name: COLUMN feriado_mercado.data_feriado; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.feriado_mercado.data_feriado IS 'Data do feriado';


--
-- Name: COLUMN feriado_mercado.tipo_feriado; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.feriado_mercado.tipo_feriado IS 'Tipo do feriado';


--
-- Name: COLUMN feriado_mercado.nome; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.feriado_mercado.nome IS 'Nome do feriado';


--
-- Name: COLUMN feriado_mercado.horario_fechamento; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.feriado_mercado.horario_fechamento IS 'Horário de fechamento antecipado (se aplicável)';


--
-- Name: COLUMN feriado_mercado.recorrente; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.feriado_mercado.recorrente IS 'Indica se é feriado anual fixo (sempre no mesmo dia/mês)';


--
-- Name: COLUMN feriado_mercado.observacoes; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.feriado_mercado.observacoes IS 'Observações sobre o feriado';


--
-- Name: COLUMN feriado_mercado.created_at; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.feriado_mercado.created_at IS 'Data de criação do registro';


--
-- Name: COLUMN feriado_mercado.updated_at; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.feriado_mercado.updated_at IS 'Data da última atualização';


--
-- Name: fonte_dados; Type: TABLE; Schema: public; Owner: exitus
--

CREATE TABLE public.fonte_dados (
    id uuid NOT NULL,
    nome character varying(100) NOT NULL,
    tipo_fonte public.tipofontedados NOT NULL,
    url_base character varying(500),
    requer_autenticacao boolean NOT NULL,
    rate_limit character varying(50),
    ativa boolean NOT NULL,
    prioridade integer NOT NULL,
    ultima_consulta timestamp with time zone,
    total_consultas integer NOT NULL,
    total_erros integer NOT NULL,
    observacoes text,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    CONSTRAINT fonte_consultas_positivas CHECK ((total_consultas >= 0)),
    CONSTRAINT fonte_erros_positivos CHECK ((total_erros >= 0)),
    CONSTRAINT fonte_nome_min_length CHECK ((length((nome)::text) >= 2)),
    CONSTRAINT fonte_prioridade_positiva CHECK ((prioridade > 0))
);


ALTER TABLE public.fonte_dados OWNER TO exitus;

--
-- Name: TABLE fonte_dados; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON TABLE public.fonte_dados IS 'Tabela de fontes de dados externas (APIs, scrapers)';


--
-- Name: COLUMN fonte_dados.id; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.fonte_dados.id IS 'Identificador único da fonte';


--
-- Name: COLUMN fonte_dados.nome; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.fonte_dados.nome IS 'Nome da fonte de dados (ex: yfinance, Alpha Vantage)';


--
-- Name: COLUMN fonte_dados.tipo_fonte; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.fonte_dados.tipo_fonte IS 'Tipo da fonte de dados';


--
-- Name: COLUMN fonte_dados.url_base; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.fonte_dados.url_base IS 'URL base da API ou site';


--
-- Name: COLUMN fonte_dados.requer_autenticacao; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.fonte_dados.requer_autenticacao IS 'Indica se requer chave API ou autenticação';


--
-- Name: COLUMN fonte_dados.rate_limit; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.fonte_dados.rate_limit IS 'Limite de requisições (ex: ''5/minute'', ''500/day'')';


--
-- Name: COLUMN fonte_dados.ativa; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.fonte_dados.ativa IS 'Indica se fonte está ativa';


--
-- Name: COLUMN fonte_dados.prioridade; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.fonte_dados.prioridade IS 'Ordem de prioridade (1 = maior prioridade)';


--
-- Name: COLUMN fonte_dados.ultima_consulta; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.fonte_dados.ultima_consulta IS 'Timestamp da última consulta bem-sucedida';


--
-- Name: COLUMN fonte_dados.total_consultas; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.fonte_dados.total_consultas IS 'Total de consultas realizadas';


--
-- Name: COLUMN fonte_dados.total_erros; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.fonte_dados.total_erros IS 'Total de erros encontrados';


--
-- Name: COLUMN fonte_dados.observacoes; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.fonte_dados.observacoes IS 'Observações sobre a fonte de dados';


--
-- Name: COLUMN fonte_dados.created_at; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.fonte_dados.created_at IS 'Data de criação do registro';


--
-- Name: COLUMN fonte_dados.updated_at; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.fonte_dados.updated_at IS 'Data da última atualização';


--
-- Name: historico_preco; Type: TABLE; Schema: public; Owner: exitus
--

CREATE TABLE public.historico_preco (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    ativoid uuid NOT NULL,
    data date NOT NULL,
    preco_abertura numeric(18,6),
    preco_fechamento numeric(18,6) NOT NULL,
    preco_minimo numeric(18,6),
    preco_maximo numeric(18,6),
    volume bigint,
    createdat timestamp without time zone DEFAULT now() NOT NULL,
    updatedat timestamp without time zone,
    CONSTRAINT ck_historico_fechamento_positivo CHECK ((preco_fechamento > (0)::numeric)),
    CONSTRAINT ck_historico_minmax CHECK (((preco_minimo IS NULL) OR (preco_maximo IS NULL) OR (preco_minimo <= preco_maximo)))
);


ALTER TABLE public.historico_preco OWNER TO exitus;

--
-- Name: log_auditoria; Type: TABLE; Schema: public; Owner: exitus
--

CREATE TABLE public.log_auditoria (
    id uuid NOT NULL,
    usuario_id uuid,
    acao character varying(50) NOT NULL,
    entidade character varying(100),
    entidade_id uuid,
    dados_antes json,
    dados_depois json,
    ip_address character varying(45),
    user_agent character varying(500),
    "timestamp" timestamp with time zone NOT NULL,
    sucesso boolean NOT NULL,
    mensagem text,
    CONSTRAINT log_acao_min_length CHECK ((length((acao)::text) >= 3))
);


ALTER TABLE public.log_auditoria OWNER TO exitus;

--
-- Name: TABLE log_auditoria; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON TABLE public.log_auditoria IS 'Tabela de logs de auditoria para compliance';


--
-- Name: COLUMN log_auditoria.id; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.log_auditoria.id IS 'Identificador único do log';


--
-- Name: COLUMN log_auditoria.usuario_id; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.log_auditoria.usuario_id IS 'ID do usuário (NULL para ações anônimas)';


--
-- Name: COLUMN log_auditoria.acao; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.log_auditoria.acao IS 'Tipo de ação (LOGIN, LOGOUT, CREATE, UPDATE, DELETE, VIEW, EXPORT, etc.)';


--
-- Name: COLUMN log_auditoria.entidade; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.log_auditoria.entidade IS 'Nome da entidade afetada (Usuario, Transacao, Posicao, etc.)';


--
-- Name: COLUMN log_auditoria.entidade_id; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.log_auditoria.entidade_id IS 'ID do registro afetado';


--
-- Name: COLUMN log_auditoria.dados_antes; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.log_auditoria.dados_antes IS 'Estado anterior do registro (JSON)';


--
-- Name: COLUMN log_auditoria.dados_depois; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.log_auditoria.dados_depois IS 'Estado posterior do registro (JSON)';


--
-- Name: COLUMN log_auditoria.ip_address; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.log_auditoria.ip_address IS 'Endereço IP de origem';


--
-- Name: COLUMN log_auditoria.user_agent; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.log_auditoria.user_agent IS 'User-Agent (navegador/cliente)';


--
-- Name: COLUMN log_auditoria."timestamp"; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.log_auditoria."timestamp" IS 'Data/hora da ação';


--
-- Name: COLUMN log_auditoria.sucesso; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.log_auditoria.sucesso IS 'Indica se ação foi bem-sucedida';


--
-- Name: COLUMN log_auditoria.mensagem; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.log_auditoria.mensagem IS 'Mensagem de erro ou detalhes adicionais';


--
-- Name: movimentacao_caixa; Type: TABLE; Schema: public; Owner: exitus
--

CREATE TABLE public.movimentacao_caixa (
    id uuid NOT NULL,
    usuario_id uuid NOT NULL,
    corretora_id uuid NOT NULL,
    corretora_destino_id uuid,
    provento_id uuid,
    tipo_movimentacao public.tipomovimentacao NOT NULL,
    valor numeric(18,2) NOT NULL,
    moeda character varying(3) NOT NULL,
    data_movimentacao date NOT NULL,
    descricao text,
    comprovante character varying(200),
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    CONSTRAINT movimentacao_moeda_iso_format CHECK (((moeda)::text ~* '^[A-Z]{3}$'::text)),
    CONSTRAINT movimentacao_valor_positivo CHECK ((valor > (0)::numeric))
);


ALTER TABLE public.movimentacao_caixa OWNER TO exitus;

--
-- Name: TABLE movimentacao_caixa; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON TABLE public.movimentacao_caixa IS 'Tabela de movimentações de caixa em corretoras';


--
-- Name: COLUMN movimentacao_caixa.id; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.movimentacao_caixa.id IS 'Identificador único da movimentação';


--
-- Name: COLUMN movimentacao_caixa.usuario_id; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.movimentacao_caixa.usuario_id IS 'ID do usuário';


--
-- Name: COLUMN movimentacao_caixa.corretora_id; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.movimentacao_caixa.corretora_id IS 'ID da corretora (origem)';


--
-- Name: COLUMN movimentacao_caixa.corretora_destino_id; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.movimentacao_caixa.corretora_destino_id IS 'ID da corretora destino (apenas para transferências)';


--
-- Name: COLUMN movimentacao_caixa.provento_id; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.movimentacao_caixa.provento_id IS 'ID do provento (apenas para crédito de provento)';


--
-- Name: COLUMN movimentacao_caixa.tipo_movimentacao; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.movimentacao_caixa.tipo_movimentacao IS 'Tipo da movimentação';


--
-- Name: COLUMN movimentacao_caixa.valor; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.movimentacao_caixa.valor IS 'Valor da movimentação';


--
-- Name: COLUMN movimentacao_caixa.moeda; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.movimentacao_caixa.moeda IS 'Código ISO 4217 da moeda (BRL, USD, EUR)';


--
-- Name: COLUMN movimentacao_caixa.data_movimentacao; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.movimentacao_caixa.data_movimentacao IS 'Data da movimentação';


--
-- Name: COLUMN movimentacao_caixa.descricao; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.movimentacao_caixa.descricao IS 'Descrição da movimentação';


--
-- Name: COLUMN movimentacao_caixa.comprovante; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.movimentacao_caixa.comprovante IS 'Referência ao comprovante (número, hash, arquivo)';


--
-- Name: COLUMN movimentacao_caixa.created_at; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.movimentacao_caixa.created_at IS 'Data de criação do registro';


--
-- Name: COLUMN movimentacao_caixa.updated_at; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.movimentacao_caixa.updated_at IS 'Data da última atualização';


--
-- Name: parametros_macro; Type: TABLE; Schema: public; Owner: exitus
--

CREATE TABLE public.parametros_macro (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    pais character varying(2) NOT NULL,
    mercado character varying(10) NOT NULL,
    taxa_livre_risco numeric(8,6) NOT NULL,
    crescimento_medio numeric(8,6) NOT NULL,
    custo_capital numeric(8,6) NOT NULL,
    inflacao_anual numeric(8,6) NOT NULL,
    cap_rate_fii numeric(8,6),
    ytm_rf numeric(8,6),
    ativo boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.parametros_macro OWNER TO exitus;

--
-- Name: portfolio; Type: TABLE; Schema: public; Owner: exitus
--

CREATE TABLE public.portfolio (
    id uuid NOT NULL,
    usuario_id uuid NOT NULL,
    nome character varying(100) NOT NULL,
    descricao text,
    objetivo character varying(50),
    ativo boolean DEFAULT true NOT NULL,
    valor_inicial numeric(18,2),
    percentual_alocacao_target numeric(5,2),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT portfolio_nome_min_length CHECK ((length((nome)::text) >= 3)),
    CONSTRAINT portfolio_percentual_valido CHECK (((percentual_alocacao_target IS NULL) OR ((percentual_alocacao_target >= (0)::numeric) AND (percentual_alocacao_target <= (100)::numeric)))),
    CONSTRAINT portfolio_valor_inicial_positivo CHECK (((valor_inicial IS NULL) OR (valor_inicial >= (0)::numeric)))
);


ALTER TABLE public.portfolio OWNER TO exitus;

--
-- Name: TABLE portfolio; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON TABLE public.portfolio IS 'Tabela de portfolios (agrupamento de posições)';


--
-- Name: COLUMN portfolio.id; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.portfolio.id IS 'Identificador único do portfolio';


--
-- Name: COLUMN portfolio.usuario_id; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.portfolio.usuario_id IS 'ID do usuário proprietário';


--
-- Name: COLUMN portfolio.nome; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.portfolio.nome IS 'Nome do portfolio (ex: Portfolio Principal, Trade, Longo Prazo)';


--
-- Name: COLUMN portfolio.descricao; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.portfolio.descricao IS 'Descrição detalhada do portfolio e sua estratégia';


--
-- Name: COLUMN portfolio.objetivo; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.portfolio.objetivo IS 'Objetivo do portfolio (Renda Passiva, Crescimento, Proteção, etc.)';


--
-- Name: COLUMN portfolio.ativo; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.portfolio.ativo IS 'Indica se o portfolio está ativo';


--
-- Name: COLUMN portfolio.valor_inicial; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.portfolio.valor_inicial IS 'Valor inicial investido no portfolio (R$)';


--
-- Name: COLUMN portfolio.percentual_alocacao_target; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.portfolio.percentual_alocacao_target IS 'Percentual de alocação desejada do patrimônio total (0-100)';


--
-- Name: COLUMN portfolio.created_at; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.portfolio.created_at IS 'Data de criação do registro';


--
-- Name: COLUMN portfolio.updated_at; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.portfolio.updated_at IS 'Data da última atualização';


--
-- Name: posicao; Type: TABLE; Schema: public; Owner: exitus
--

CREATE TABLE public.posicao (
    id uuid NOT NULL,
    usuario_id uuid NOT NULL,
    corretora_id uuid NOT NULL,
    ativo_id uuid NOT NULL,
    quantidade numeric(18,8) NOT NULL,
    preco_medio numeric(18,6) NOT NULL,
    custo_total numeric(18,2) NOT NULL,
    taxas_acumuladas numeric(18,2) NOT NULL,
    impostos_acumulados numeric(18,2) NOT NULL,
    valor_atual numeric(18,2),
    lucro_prejuizo_realizado numeric(18,2) NOT NULL,
    lucro_prejuizo_nao_realizado numeric(18,2),
    data_primeira_compra date,
    data_ultima_atualizacao timestamp with time zone,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    CONSTRAINT posicao_custo_total_positivo CHECK ((custo_total >= (0)::numeric)),
    CONSTRAINT posicao_impostos_positivos CHECK ((impostos_acumulados >= (0)::numeric)),
    CONSTRAINT posicao_preco_medio_positivo CHECK ((preco_medio >= (0)::numeric)),
    CONSTRAINT posicao_quantidade_positiva CHECK ((quantidade >= (0)::numeric)),
    CONSTRAINT posicao_taxas_positivas CHECK ((taxas_acumuladas >= (0)::numeric))
);


ALTER TABLE public.posicao OWNER TO exitus;

--
-- Name: TABLE posicao; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON TABLE public.posicao IS 'Tabela de posições em carteira (holdings)';


--
-- Name: COLUMN posicao.id; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.posicao.id IS 'Identificador único da posição';


--
-- Name: COLUMN posicao.usuario_id; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.posicao.usuario_id IS 'ID do usuário proprietário';


--
-- Name: COLUMN posicao.corretora_id; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.posicao.corretora_id IS 'ID da corretora onde está a posição';


--
-- Name: COLUMN posicao.ativo_id; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.posicao.ativo_id IS 'ID do ativo';


--
-- Name: COLUMN posicao.quantidade; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.posicao.quantidade IS 'Quantidade de ativos (suporta fracionários)';


--
-- Name: COLUMN posicao.preco_medio; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.posicao.preco_medio IS 'Preço médio de aquisição';


--
-- Name: COLUMN posicao.custo_total; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.posicao.custo_total IS 'Custo total investido (quantidade * preço médio)';


--
-- Name: COLUMN posicao.taxas_acumuladas; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.posicao.taxas_acumuladas IS 'Taxas de corretagem e custódia acumuladas';


--
-- Name: COLUMN posicao.impostos_acumulados; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.posicao.impostos_acumulados IS 'Impostos pagos acumulados (IR, IOF, etc.)';


--
-- Name: COLUMN posicao.valor_atual; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.posicao.valor_atual IS 'Valor de mercado atual da posição';


--
-- Name: COLUMN posicao.lucro_prejuizo_realizado; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.posicao.lucro_prejuizo_realizado IS 'Lucro/prejuízo realizado em vendas';


--
-- Name: COLUMN posicao.lucro_prejuizo_nao_realizado; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.posicao.lucro_prejuizo_nao_realizado IS 'Lucro/prejuízo não realizado (marcação a mercado)';


--
-- Name: COLUMN posicao.data_primeira_compra; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.posicao.data_primeira_compra IS 'Data da primeira aquisição deste ativo';


--
-- Name: COLUMN posicao.data_ultima_atualizacao; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.posicao.data_ultima_atualizacao IS 'Data da última atualização de valores';


--
-- Name: COLUMN posicao.created_at; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.posicao.created_at IS 'Data de criação do registro';


--
-- Name: COLUMN posicao.updated_at; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.posicao.updated_at IS 'Data da última atualização';


--
-- Name: projecoes_renda; Type: TABLE; Schema: public; Owner: exitus
--

CREATE TABLE public.projecoes_renda (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    usuario_id uuid NOT NULL,
    portfolio_id uuid,
    mes_ano character varying(7) NOT NULL,
    renda_dividendos_projetada numeric(18,2) DEFAULT 0 NOT NULL,
    renda_jcp_projetada numeric(18,2) DEFAULT 0 NOT NULL,
    renda_rendimentos_projetada numeric(18,2) DEFAULT 0 NOT NULL,
    renda_total_mes numeric(18,2) DEFAULT 0 NOT NULL,
    renda_anual_projetada numeric(18,2),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.projecoes_renda OWNER TO exitus;

--
-- Name: provento; Type: TABLE; Schema: public; Owner: exitus
--

CREATE TABLE public.provento (
    id uuid NOT NULL,
    ativo_id uuid NOT NULL,
    tipo_provento public.tipoprovento NOT NULL,
    valor_por_acao numeric(18,6) NOT NULL,
    quantidade_ativos numeric(18,8) NOT NULL,
    valor_bruto numeric(18,2) NOT NULL,
    imposto_retido numeric(18,2) NOT NULL,
    valor_liquido numeric(18,2) NOT NULL,
    data_com date NOT NULL,
    data_pagamento date NOT NULL,
    observacoes text,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    CONSTRAINT provento_data_pagamento_valida CHECK ((data_pagamento >= data_com)),
    CONSTRAINT provento_imposto_positivo CHECK ((imposto_retido >= (0)::numeric)),
    CONSTRAINT provento_liquido_menor_bruto CHECK ((valor_liquido <= valor_bruto)),
    CONSTRAINT provento_quantidade_positiva CHECK ((quantidade_ativos > (0)::numeric)),
    CONSTRAINT provento_valor_bruto_positivo CHECK ((valor_bruto > (0)::numeric)),
    CONSTRAINT provento_valor_liquido_positivo CHECK ((valor_liquido > (0)::numeric)),
    CONSTRAINT provento_valor_por_acao_positivo CHECK ((valor_por_acao > (0)::numeric))
);


ALTER TABLE public.provento OWNER TO exitus;

--
-- Name: TABLE provento; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON TABLE public.provento IS 'Tabela de proventos recebidos (dividendos, JCP, rendimentos)';


--
-- Name: COLUMN provento.id; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.provento.id IS 'Identificador único do provento';


--
-- Name: COLUMN provento.ativo_id; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.provento.ativo_id IS 'ID do ativo que pagou o provento';


--
-- Name: COLUMN provento.tipo_provento; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.provento.tipo_provento IS 'Tipo do provento (dividendo, JCP, rendimento, etc.)';


--
-- Name: COLUMN provento.valor_por_acao; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.provento.valor_por_acao IS 'Valor unitário por ativo';


--
-- Name: COLUMN provento.quantidade_ativos; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.provento.quantidade_ativos IS 'Quantidade de ativos que geraram o provento';


--
-- Name: COLUMN provento.valor_bruto; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.provento.valor_bruto IS 'Valor bruto recebido';


--
-- Name: COLUMN provento.imposto_retido; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.provento.imposto_retido IS 'IR retido na fonte';


--
-- Name: COLUMN provento.valor_liquido; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.provento.valor_liquido IS 'Valor líquido creditado';


--
-- Name: COLUMN provento.data_com; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.provento.data_com IS 'Data COM (último dia para ter direito ao provento)';


--
-- Name: COLUMN provento.data_pagamento; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.provento.data_pagamento IS 'Data efetiva do pagamento';


--
-- Name: COLUMN provento.observacoes; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.provento.observacoes IS 'Observações sobre o provento';


--
-- Name: COLUMN provento.created_at; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.provento.created_at IS 'Data de criação do registro';


--
-- Name: COLUMN provento.updated_at; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.provento.updated_at IS 'Data da última atualização';


--
-- Name: regra_fiscal; Type: TABLE; Schema: public; Owner: exitus
--

CREATE TABLE public.regra_fiscal (
    id uuid NOT NULL,
    pais character varying(2) NOT NULL,
    tipo_ativo character varying(20),
    tipo_operacao character varying(20),
    aliquota_ir numeric(6,4) NOT NULL,
    valor_isencao numeric(18,2),
    incide_sobre public.incidenciaimposto NOT NULL,
    descricao text NOT NULL,
    vigencia_inicio date NOT NULL,
    vigencia_fim date,
    ativa boolean NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    CONSTRAINT regra_aliquota_valida CHECK (((aliquota_ir >= (0)::numeric) AND (aliquota_ir <= (100)::numeric))),
    CONSTRAINT regra_isencao_positiva CHECK (((valor_isencao IS NULL) OR (valor_isencao >= (0)::numeric))),
    CONSTRAINT regra_pais_iso_format CHECK (((pais)::text ~* '^[A-Z]{2}$'::text)),
    CONSTRAINT regra_vigencia_valida CHECK (((vigencia_fim IS NULL) OR (vigencia_fim >= vigencia_inicio)))
);


ALTER TABLE public.regra_fiscal OWNER TO exitus;

--
-- Name: TABLE regra_fiscal; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON TABLE public.regra_fiscal IS 'Tabela de regras tributárias por país e tipo de ativo';


--
-- Name: COLUMN regra_fiscal.id; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.regra_fiscal.id IS 'Identificador único da regra';


--
-- Name: COLUMN regra_fiscal.pais; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.regra_fiscal.pais IS 'Código ISO do país (BR, US, etc.)';


--
-- Name: COLUMN regra_fiscal.tipo_ativo; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.regra_fiscal.tipo_ativo IS 'Tipo de ativo (ACAO, FII, REIT, BOND, etc.) - NULL = todos';


--
-- Name: COLUMN regra_fiscal.tipo_operacao; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.regra_fiscal.tipo_operacao IS 'Tipo de operação (COMPRA, VENDA, DAY_TRADE, SWING_TRADE) - NULL = todas';


--
-- Name: COLUMN regra_fiscal.aliquota_ir; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.regra_fiscal.aliquota_ir IS 'Alíquota de IR em % (ex: 15.0000 = 15%)';


--
-- Name: COLUMN regra_fiscal.valor_isencao; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.regra_fiscal.valor_isencao IS 'Valor de isenção mensal (ex: R$ 20.000,00 no Brasil)';


--
-- Name: COLUMN regra_fiscal.incide_sobre; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.regra_fiscal.incide_sobre IS 'Sobre o que incide o imposto';


--
-- Name: COLUMN regra_fiscal.descricao; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.regra_fiscal.descricao IS 'Descrição detalhada da regra fiscal';


--
-- Name: COLUMN regra_fiscal.vigencia_inicio; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.regra_fiscal.vigencia_inicio IS 'Data de início da vigência da regra';


--
-- Name: COLUMN regra_fiscal.vigencia_fim; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.regra_fiscal.vigencia_fim IS 'Data de fim da vigência (NULL = vigente indefinidamente)';


--
-- Name: COLUMN regra_fiscal.ativa; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.regra_fiscal.ativa IS 'Indica se regra está ativa';


--
-- Name: COLUMN regra_fiscal.created_at; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.regra_fiscal.created_at IS 'Data de criação do registro';


--
-- Name: COLUMN regra_fiscal.updated_at; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.regra_fiscal.updated_at IS 'Data da última atualização';


--
-- Name: relatorios_performance; Type: TABLE; Schema: public; Owner: exitus
--

CREATE TABLE public.relatorios_performance (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    usuario_id uuid NOT NULL,
    portfolio_id uuid,
    periodo_inicio date NOT NULL,
    periodo_fim date NOT NULL,
    retorno_bruto_percentual numeric(10,4),
    retorno_liquido_percentual numeric(10,4),
    indice_sharpe numeric(8,4),
    max_drawdown_percentual numeric(8,4),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT relatorios_performance_check CHECK ((periodo_inicio <= periodo_fim))
);


ALTER TABLE public.relatorios_performance OWNER TO exitus;

--
-- Name: transacao; Type: TABLE; Schema: public; Owner: exitus
--

CREATE TABLE public.transacao (
    id uuid NOT NULL,
    usuario_id uuid NOT NULL,
    tipo public.tipotransacao NOT NULL,
    ativo_id uuid NOT NULL,
    corretora_id uuid NOT NULL,
    data_transacao timestamp with time zone NOT NULL,
    quantidade numeric(18,8) NOT NULL,
    preco_unitario numeric(18,6) NOT NULL,
    valor_total numeric(18,2) NOT NULL,
    taxa_corretagem numeric(18,2) NOT NULL,
    taxa_liquidacao numeric(18,2) NOT NULL,
    emolumentos numeric(18,2) NOT NULL,
    imposto numeric(18,2) NOT NULL,
    outros_custos numeric(18,2) NOT NULL,
    custos_totais numeric(18,2) NOT NULL,
    valor_liquido numeric(18,2) NOT NULL,
    observacoes text,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);


ALTER TABLE public.transacao OWNER TO exitus;

--
-- Name: usuario; Type: TABLE; Schema: public; Owner: exitus
--

CREATE TABLE public.usuario (
    id uuid NOT NULL,
    username character varying(50) NOT NULL,
    email character varying(120) NOT NULL,
    password_hash character varying(255) NOT NULL,
    nome_completo character varying(200),
    ativo boolean NOT NULL,
    role public.userrole NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);


ALTER TABLE public.usuario OWNER TO exitus;

--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: exitus
--

COPY public.alembic_version (version_num) FROM stdin;
ffdaac46cd7a
\.


--
-- Data for Name: alertas; Type: TABLE DATA; Schema: public; Owner: exitus
--

COPY public.alertas (id, usuario_id, nome, tipo_alerta, ticker, condicao_operador, condicao_valor, condicao_valor2, ativo, frequencia_notificacao, canais_entrega, total_acionamentos, timestamp_ultimo_acionamento, created_at, updated_at) FROM stdin;
9857e07d-ed91-4fb8-9d89-906d653b22f0	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	PETR4 > R$35,00	ALTA_PRECO	PETR4	>	35.0000	\N	t	IMEDIATA	["WEBAPP", "EMAIL"]	0	\N	2025-12-23 15:39:32.795504	2025-12-23 15:39:32.795504
e6b143b3-6cfe-43ad-9b81-952c49135cf6	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	VALE3 < R$60,00	QUEDA_PRECO	VALE3	<	60.0000	\N	t	DIARIA	["WEBAPP"]	0	\N	2025-12-23 15:39:32.795504	2025-12-23 15:39:32.795504
f8c5ec6c-982d-4c07-8409-4000a73152a7	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	VALE3 caiu 5%	QUEDA_PRECO	VALE3	<	60.0000	\N	t	IMEDIATA	["WEBAPP", "EMAIL"]	0	\N	2025-12-23 23:20:21.187052	2025-12-23 23:20:21.187052
\.


--
-- Data for Name: ativo; Type: TABLE DATA; Schema: public; Owner: exitus
--

COPY public.ativo (id, ticker, nome, tipo, classe, mercado, moeda, preco_atual, data_ultima_cotacao, dividend_yield, p_l, p_vp, roe, ativo, deslistado, data_deslistagem, observacoes, created_at, updated_at, preco_teto, beta) FROM stdin;
87ac8225-0956-4b04-9d8e-fb20910af804	ITUB4	Itaú Unibanco PN	ACAO	RENDA_VARIAVEL	BR	BRL	28.450000	\N	\N	\N	\N	\N	t	f	\N	Setor: Bancos	2025-12-01 11:40:20.681106-03	2025-12-01 11:40:20.681106-03	\N	\N
1e515bec-6cc0-411c-9b8c-14917c796368	BBDC4	Bradesco PN	ACAO	RENDA_VARIAVEL	BR	BRL	13.200000	\N	\N	\N	\N	\N	t	f	\N	Setor: Bancos	2025-12-01 11:40:20.681109-03	2025-12-01 11:40:20.68111-03	\N	\N
0deec67c-0ca0-48d7-bb32-a815497f506c	BBAS3	Banco do Brasil ON	ACAO	RENDA_VARIAVEL	BR	BRL	25.600000	\N	\N	\N	\N	\N	t	f	\N	Setor: Bancos	2025-12-01 11:40:20.681112-03	2025-12-01 11:40:20.681112-03	\N	\N
cfb88347-f421-4a04-adcd-c6bf21e1cd22	MGLU3	Magazine Luiza ON	ACAO	RENDA_VARIAVEL	BR	BRL	8.750000	\N	\N	\N	\N	\N	t	f	\N	Setor: Varejo	2025-12-01 11:40:20.681115-03	2025-12-01 11:40:20.681115-03	\N	\N
dfed2549-214a-472e-9f6d-17169d54d30d	WEGE3	WEG ON	ACAO	RENDA_VARIAVEL	BR	BRL	42.300000	\N	\N	\N	\N	\N	t	f	\N	Setor: Máquinas e Equipamentos	2025-12-01 11:40:20.681117-03	2025-12-01 11:40:20.681117-03	\N	\N
4bcc406e-7831-4923-9477-89c2a4731ab2	RENT3	Localiza ON	ACAO	RENDA_VARIAVEL	BR	BRL	56.900000	\N	\N	\N	\N	\N	t	f	\N	Setor: Locação de Veículos	2025-12-01 11:40:20.681119-03	2025-12-01 11:40:20.68112-03	\N	\N
4f53220f-7f99-490d-820a-5c7e1a23c480	RAIL3	Rumo ON	ACAO	RENDA_VARIAVEL	BR	BRL	18.450000	\N	\N	\N	\N	\N	t	f	\N	Setor: Transporte	2025-12-01 11:40:20.681122-03	2025-12-01 11:40:20.681122-03	\N	\N
9ad84d24-1725-4d23-9ad4-ddb32f8869a1	SUZB3	Suzano ON	ACAO	RENDA_VARIAVEL	BR	BRL	52.800000	\N	\N	\N	\N	\N	t	f	\N	Setor: Papel e Celulose	2025-12-01 11:40:20.681124-03	2025-12-01 11:40:20.681124-03	\N	\N
bdc084b6-14e3-4068-91b6-4940cb4a5023	KLBN11	Klabin Units	ACAO	RENDA_VARIAVEL	BR	BRL	22.150000	\N	\N	\N	\N	\N	t	f	\N	Setor: Papel e Celulose	2025-12-01 11:40:20.681127-03	2025-12-01 11:40:20.681127-03	\N	\N
ae8cb2b0-6aa6-45d0-adc7-16cd55e6c79e	ELET3	Eletrobras ON	ACAO	RENDA_VARIAVEL	BR	BRL	42.100000	\N	\N	\N	\N	\N	t	f	\N	Setor: Energia Elétrica	2025-12-01 11:40:20.681129-03	2025-12-01 11:40:20.681129-03	\N	\N
4f93d48e-0d6a-4a7f-97b4-014721b09969	CMIG4	Cemig PN	ACAO	RENDA_VARIAVEL	BR	BRL	10.850000	\N	\N	\N	\N	\N	t	f	\N	Setor: Energia Elétrica	2025-12-01 11:40:20.681133-03	2025-12-01 11:40:20.681133-03	\N	\N
5765bb47-a6f0-4cd0-9b86-46bd9f5e8c8b	CPLE6	Copel PNB	ACAO	RENDA_VARIAVEL	BR	BRL	8.950000	\N	\N	\N	\N	\N	t	f	\N	Setor: Energia Elétrica	2025-12-01 11:40:20.681135-03	2025-12-01 11:40:20.681136-03	\N	\N
3a4810a7-736e-4748-a922-fb4d0dfac8b8	ABEV3	Ambev ON	ACAO	RENDA_VARIAVEL	BR	BRL	11.200000	\N	\N	\N	\N	\N	t	f	\N	Setor: Bebidas	2025-12-01 11:40:20.681138-03	2025-12-01 11:40:20.681139-03	\N	\N
787df1e0-fb6c-419d-9db1-e40eeb8e6179	HGLG11	CSHG Logística FII	FII	RENDA_VARIAVEL	BR	BRL	152.300000	\N	\N	\N	\N	\N	t	f	\N	Segmento: Logística	2025-12-01 11:40:20.681141-03	2025-12-01 11:40:20.681141-03	\N	\N
d1fb382b-6e04-47e4-9c37-a962ec872e68	VISC11	Vinci Shopping Centers FII	FII	RENDA_VARIAVEL	BR	BRL	105.800000	\N	\N	\N	\N	\N	t	f	\N	Segmento: Shopping	2025-12-01 11:40:20.681143-03	2025-12-01 11:40:20.681144-03	\N	\N
5f19e852-0851-4357-94e3-41a8a320a871	BTLG11	BTG Pactual Logística FII	FII	RENDA_VARIAVEL	BR	BRL	102.700000	\N	\N	\N	\N	\N	t	f	\N	Segmento: Logística	2025-12-01 11:40:20.68115-03	2025-12-01 11:40:20.68115-03	\N	\N
16989c21-28e2-4dce-9607-8926db9e2672	XPML11	XP Malls FII	FII	RENDA_VARIAVEL	BR	BRL	95.600000	\N	\N	\N	\N	\N	t	f	\N	Segmento: Shopping	2025-12-01 11:40:20.681152-03	2025-12-01 11:40:20.681152-03	\N	\N
88168342-8c56-4fdc-9713-7e0caadc9ef7	MXRF11	Maxi Renda FII	FII	RENDA_VARIAVEL	BR	BRL	10.250000	\N	\N	\N	\N	\N	t	f	\N	Segmento: Híbrido	2025-12-01 11:40:20.681155-03	2025-12-01 11:40:20.681155-03	\N	\N
acc05091-f495-44a2-ba65-ae09c8c8a298	TRXF11	TRX Real Estate FII	FII	RENDA_VARIAVEL	BR	BRL	95.300000	\N	\N	\N	\N	\N	t	f	\N	Segmento: Lajes Corporativas	2025-12-01 11:40:20.681157-03	2025-12-01 11:40:20.681157-03	\N	\N
b48c4dec-62ca-410e-b3f7-087cbc0fa172	KNCR11	Kinea Rendimentos Imobiliários FII	FII	RENDA_VARIAVEL	BR	BRL	110.500000	\N	\N	\N	\N	\N	t	f	\N	Segmento: Papel	2025-12-01 11:40:20.681159-03	2025-12-01 11:40:20.68116-03	\N	\N
ec4ca9cc-1779-472b-9706-5c45755a4d16	LVBI11	VBI Logístico FII	FII	RENDA_VARIAVEL	BR	BRL	98.200000	\N	\N	\N	\N	\N	t	f	\N	Segmento: Logística	2025-12-01 11:40:20.681162-03	2025-12-01 11:40:20.681162-03	\N	\N
7a51e943-5420-4103-8e81-301dfea899dd	GGRC11	GGR Covepi Renda FII	FII	RENDA_VARIAVEL	BR	BRL	105.400000	\N	\N	\N	\N	\N	t	f	\N	Segmento: Lajes Corporativas	2025-12-01 11:40:20.681165-03	2025-12-01 11:40:20.681165-03	\N	\N
957bf5cd-a622-41a6-8cfd-f572e654da11	BTC	Bitcoin	CRIPTO	CRIPTO	CRIPTO	USD	43500.000000	\N	\N	\N	\N	\N	t	f	\N	\N	2025-12-02 12:00:01.294043-03	2025-12-02 12:00:01.294047-03	\N	\N
46d148cd-24e3-454a-a9d3-abb35f5be02f	LVMH	LVMH Moët Hennessy	ACAO	RENDA_VARIAVEL	EURONEXT	EUR	750.000000	\N	0.0180	\N	\N	\N	t	f	\N	\N	2025-12-03 17:09:47.271791-03	2025-12-03 17:09:47.271795-03	\N	\N
980d3138-a670-4478-b0c6-b042eacc4964	FII372211	Fundo Teste	FII	RENDA_VARIAVEL	BR	BRL	\N	\N	\N	\N	\N	\N	t	f	\N	\N	2025-12-13 01:01:21.839204-03	2025-12-13 01:01:21.839207-03	\N	\N
0103f083-addd-4960-9b2e-f090a89b9407	BTC-USD	Bitcoin USD	CRIPTO	RENDA_VARIAVEL	GLOBAL	USD	\N	\N	\N	\N	\N	\N	t	f	\N	\N	2025-12-08 15:28:04.058377-03	2025-12-08 15:28:04.058377-03	\N	\N
89350282-9805-4620-b563-6898cbb33391	ACAO78263	Empresa Teste SA	ACAO	RENDA_VARIAVEL	BR	BRL	\N	\N	\N	\N	\N	\N	t	f	\N	\N	2025-12-13 01:03:54.070428-03	2025-12-13 01:03:54.07043-03	\N	\N
249ce95d-8e26-41f3-9eec-c21c1617004e	FII782611	Fundo Teste	FII	RENDA_VARIAVEL	BR	BRL	\N	\N	\N	\N	\N	\N	t	f	\N	\N	2025-12-13 01:03:54.093342-03	2025-12-13 01:03:54.093346-03	\N	\N
9543442c-8678-4c1c-8abe-9ab3095950be	ACAO15543	Empresa Teste SA	ACAO	RENDA_VARIAVEL	BR	BRL	\N	\N	\N	\N	\N	\N	t	f	\N	\N	2025-12-13 01:08:25.214559-03	2025-12-13 01:08:25.214562-03	\N	\N
b8e4ccc8-3dfe-4a97-a8eb-e21a24c2e2ad	KNRI11	Kinea Renda Imobiliária FII	FII	RENDA_VARIAVEL	BR	BRL	149.510000	2025-12-09 17:43:14.872381-03	9.8000	\N	\N	\N	t	f	\N	Segmento: Híbrido	2025-12-01 11:40:20.681146-03	2025-12-09 17:43:14.878957-03	\N	\N
e80cc697-1715-4977-9788-34e6ce87aec2	ACAO69453	Empresa Teste SA	ACAO	RENDA_VARIAVEL	BR	BRL	\N	\N	\N	\N	\N	\N	t	f	\N	\N	2025-12-13 01:01:10.746823-03	2025-12-13 01:01:10.746827-03	\N	\N
ffb9b04e-e83a-4122-8da5-0bd8047cdee0	FII694511	Fundo Teste	FII	RENDA_VARIAVEL	BR	BRL	\N	\N	\N	\N	\N	\N	t	f	\N	\N	2025-12-13 01:01:10.767592-03	2025-12-13 01:01:10.767596-03	\N	\N
483502a0-6759-4d7b-9d72-ddaeea5ae396	ACAO37223	Empresa Teste SA	ACAO	RENDA_VARIAVEL	BR	BRL	\N	\N	\N	\N	\N	\N	t	f	\N	\N	2025-12-13 01:01:21.816883-03	2025-12-13 01:01:21.816884-03	\N	\N
2f956755-0161-4a78-b083-791152768783	FII155411	Fundo Teste	FII	RENDA_VARIAVEL	BR	BRL	\N	\N	\N	\N	\N	\N	t	f	\N	\N	2025-12-13 01:08:25.229904-03	2025-12-13 01:08:25.229906-03	\N	\N
c3401627-f629-48ff-bb1e-b72fb7c6672e	ACAO26893	Empresa Teste SA	ACAO	RENDA_VARIAVEL	BR	BRL	\N	\N	\N	\N	\N	\N	t	f	\N	\N	2025-12-13 01:09:06.344546-03	2025-12-13 01:09:06.344549-03	\N	\N
9634a345-c627-4b87-a9bc-e7a4bb753117	FII268911	Fundo Teste	FII	RENDA_VARIAVEL	BR	BRL	\N	\N	\N	\N	\N	\N	t	f	\N	\N	2025-12-13 01:09:06.361717-03	2025-12-13 01:09:06.361719-03	\N	\N
22f6162e-041b-471d-af55-bb7c0fdf7b19	ACAO67803	Empresa Teste SA	ACAO	RENDA_VARIAVEL	BR	BRL	\N	\N	\N	\N	\N	\N	t	f	\N	\N	2025-12-13 01:09:37.950496-03	2025-12-13 01:09:37.9505-03	\N	\N
5f6e42e4-0382-481b-8c9e-276ea8e507e4	FII678011	Fundo Teste	FII	RENDA_VARIAVEL	BR	BRL	\N	\N	\N	\N	\N	\N	t	f	\N	\N	2025-12-13 01:09:37.964264-03	2025-12-13 01:09:37.964266-03	\N	\N
c8feeb6c-8e83-4204-8f3f-441df479d4d1	ACAO81863	Empresa Teste SA	ACAO	RENDA_VARIAVEL	BR	BRL	\N	\N	\N	\N	\N	\N	t	f	\N	\N	2025-12-13 01:11:48.61013-03	2025-12-13 01:11:48.610132-03	\N	\N
a40d824e-d186-47e1-94cc-1a1fed8cda7b	FII818611	Fundo Teste	FII	RENDA_VARIAVEL	BR	BRL	\N	\N	\N	\N	\N	\N	t	f	\N	\N	2025-12-13 01:11:48.626094-03	2025-12-13 01:11:48.626098-03	\N	\N
3af7860e-e74c-40d2-b1b2-e49e784e25ea	VALE3	Vale ON	ACAO	RENDA_VARIAVEL	BR	BRL	69.020000	2025-12-15 13:59:35.934941-03	0.0000	0.00	\N	\N	t	f	\N	Setor: Mineração	2025-12-01 11:40:20.681102-03	2025-12-15 16:59:36.129752-03	\N	\N
16836286-2538-41bd-9896-f975721df9c0	PETR4	Petrobras PN	ACAO	RENDA_VARIAVEL	BR	BRL	31.700000	2025-12-16 07:01:10.428864-03	0.0000	0.00	\N	\N	t	f	\N	Setor: Petróleo e Gás	2025-12-01 11:40:20.681096-03	2025-12-16 10:01:15.826281-03	42.350000	0.9000
69870f88-f1bb-4b21-8194-0d18fee4b81b	AAPL	Apple Inc	ACAO	RENDA_VARIAVEL	US	USD	274.110000	2025-12-16 07:04:05.512152-03	0.0000	0.00	45.20	147.5000	t	f	\N	\N	2025-12-02 12:00:01.26274-03	2025-12-16 10:04:11.641488-03	\N	\N
4cde7bd8-3a83-4537-bdb4-e78fe429c227	AAPL	Apple Inc	ACAO	RENDA_VARIAVEL	NYSE	USD	274.110000	2025-12-16 07:05:13.181307-03	0.0000	0.00	\N	\N	t	f	\N	\N	2025-12-03 17:09:47.234188-03	2025-12-16 10:05:13.380961-03	\N	\N
\.


--
-- Data for Name: auditoria_relatorios; Type: TABLE DATA; Schema: public; Owner: exitus
--

COPY public.auditoria_relatorios (id, usuario_id, tipo_relatorio, data_inicio, data_fim, filtros, resultado_json, timestamp_criacao, timestamp_download, formato_export, chave_api_auditoria, created_at, updated_at) FROM stdin;
33a90773-cb78-43ac-9efa-6fc009cee690	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	performance	2025-01-01	2025-12-31	{}	{"periodo": "2025-01-01 a 2025-12-31", "transacoes": 3, "posicoes_ativas": 3, "proventos": 28, "patrimonio_final": 0.0, "rentabilidade_bruta": "12.5%", "rentabilidade_liquida": "10.2%", "sharpe_ratio": 1.45, "max_drawdown": "-8.3%", "ativos_top": ["16836286-2538-41bd-9896-f975721df9c0", "3af7860e-e74c-40d2-b1b2-e49e784e25ea", "b8e4ccc8-3dfe-4a97-a8eb-e21a24c2e2ad"]}	2025-12-11 21:02:04.818755-03	\N	visualizacao	\N	2025-12-11 21:02:04.818757-03	2025-12-11 21:02:04.818758-03
6ec84fdb-3283-4ffb-b60d-d0e1d9cd329e	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	performance	2025-01-01	2025-12-31	{}	{"periodo": "2025-01-01 a 2025-12-31", "transacoes": 3, "posicoes_ativas": 3, "proventos": 28, "patrimonio_final": 0.0, "rentabilidade_bruta": "12.5%", "rentabilidade_liquida": "10.2%", "sharpe_ratio": 1.45, "max_drawdown": "-8.3%", "ativos_top": ["16836286-2538-41bd-9896-f975721df9c0", "3af7860e-e74c-40d2-b1b2-e49e784e25ea", "b8e4ccc8-3dfe-4a97-a8eb-e21a24c2e2ad"]}	2025-12-11 21:04:18.480514-03	\N	visualizacao	\N	2025-12-11 21:04:18.480517-03	2025-12-11 21:04:18.480518-03
950a9c9f-5a8a-4906-be01-5dfa4b972cd3	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	performance	2025-01-01	2025-12-31	{}	{"periodo": "2025-01-01 a 2025-12-31", "transacoes": 3, "posicoes_ativas": 3, "proventos": 28, "patrimonio_final": 0.0, "rentabilidade_bruta": "12.5%", "rentabilidade_liquida": "10.2%", "sharpe_ratio": 1.45, "max_drawdown": "-8.3%", "ativos_top": ["16836286-2538-41bd-9896-f975721df9c0", "3af7860e-e74c-40d2-b1b2-e49e784e25ea", "b8e4ccc8-3dfe-4a97-a8eb-e21a24c2e2ad"]}	2025-12-11 21:11:20.990073-03	\N	visualizacao	\N	2025-12-11 21:11:20.990077-03	2025-12-11 21:11:20.990077-03
42d34e13-20bf-483f-ae13-4a23f4ac663c	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	performance	2025-01-01	2025-12-31	{}	{"periodo": "2025-01-01 a 2025-12-31", "transacoes": 3, "posicoes_ativas": 3, "proventos": 28, "patrimonio_final": 0.0, "rentabilidade_bruta": "12.5%", "rentabilidade_liquida": "10.2%", "sharpe_ratio": 1.45, "max_drawdown": "-8.3%", "ativos_top": ["16836286-2538-41bd-9896-f975721df9c0", "3af7860e-e74c-40d2-b1b2-e49e784e25ea", "b8e4ccc8-3dfe-4a97-a8eb-e21a24c2e2ad"]}	2025-12-11 21:13:07.067449-03	\N	visualizacao	\N	2025-12-11 21:13:07.067452-03	2025-12-11 21:13:07.067452-03
15256ac5-e0d3-4fec-9814-9d747f45b3d9	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	performance	2025-01-01	2025-12-31	{}	{"periodo": "2025-01-01 a 2025-12-31", "transacoes": 3, "posicoes_ativas": 3, "proventos": 28, "patrimonio_final": 0.0, "rentabilidade_bruta": "12.5%", "rentabilidade_liquida": "10.2%", "sharpe_ratio": 1.45, "max_drawdown": "-8.3%", "ativos_top": ["16836286-2538-41bd-9896-f975721df9c0", "3af7860e-e74c-40d2-b1b2-e49e784e25ea", "b8e4ccc8-3dfe-4a97-a8eb-e21a24c2e2ad"]}	2025-12-11 21:14:26.31465-03	\N	visualizacao	\N	2025-12-11 21:14:26.314652-03	2025-12-11 21:14:26.314653-03
b5e716aa-04f9-4af0-8643-b4279ac0e71c	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	performance	2025-01-01	2025-12-31	{}	{"periodo": "2025-01-01 a 2025-12-31", "transacoes": 3, "posicoes_ativas": 3, "proventos": 28, "patrimonio_final": 0.0, "rentabilidade_bruta": "12.5%", "rentabilidade_liquida": "10.2%", "sharpe_ratio": 1.45, "max_drawdown": "-8.3%", "ativos_top": ["16836286-2538-41bd-9896-f975721df9c0", "3af7860e-e74c-40d2-b1b2-e49e784e25ea", "b8e4ccc8-3dfe-4a97-a8eb-e21a24c2e2ad"]}	2025-12-11 21:16:28.808277-03	\N	visualizacao	\N	2025-12-11 21:16:28.808278-03	2025-12-11 21:16:28.808279-03
9954bf6e-ba94-4b5d-8afb-0b362a78cf89	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	performance	2025-01-01	2025-12-31	{}	{"periodo": "2025-01-01 a 2025-12-31", "transacoes": 3, "posicoes_ativas": 3, "proventos": 28, "patrimonio_final": 0.0, "rentabilidade_bruta": "12.5%", "rentabilidade_liquida": "10.2%", "sharpe_ratio": 1.45, "max_drawdown": "-8.3%", "ativos_top": ["16836286-2538-41bd-9896-f975721df9c0", "3af7860e-e74c-40d2-b1b2-e49e784e25ea", "b8e4ccc8-3dfe-4a97-a8eb-e21a24c2e2ad"]}	2025-12-11 23:26:47.780342-03	\N	visualizacao	\N	2025-12-11 23:26:47.780345-03	2025-12-11 23:26:47.780345-03
d9c6f0b0-efeb-4c40-a3a5-7c18e492849e	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	performance	2025-01-01	2025-12-31	{}	{"periodo": "2025-01-01 a 2025-12-31", "transacoes": 3, "posicoes_ativas": 3, "proventos": 28, "patrimonio_final": 0.0, "rentabilidade_bruta": "12.5%", "rentabilidade_liquida": "10.2%", "sharpe_ratio": 1.45, "max_drawdown": "-8.3%", "ativos_top": ["16836286-2538-41bd-9896-f975721df9c0", "3af7860e-e74c-40d2-b1b2-e49e784e25ea", "b8e4ccc8-3dfe-4a97-a8eb-e21a24c2e2ad"]}	2025-12-11 23:28:24.855964-03	\N	visualizacao	\N	2025-12-11 23:28:24.855988-03	2025-12-11 23:28:24.855989-03
b48d7627-f2ac-4c16-a6d3-1c4a77a8fb13	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	performance	2025-01-01	2025-12-31	{}	{"periodo": "2025-01-01 a 2025-12-31", "transacoes": 3, "posicoes_ativas": 3, "proventos": 28, "patrimonio_final": 0, "rentabilidade_bruta": "12.5%", "rentabilidade_liquida": "10.2%", "sharpe_ratio": 1.45, "max_drawdown": "-8.3%", "ativos_top": ["PETR4", "VALE3", "AAPL"]}	2025-12-12 08:03:43.398417-03	\N	visualizacao	\N	2025-12-12 08:03:43.398422-03	2025-12-12 08:03:43.398424-03
9262dc82-eeb9-423c-a367-5fdb4d9123f7	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	performance	2025-01-01	2025-12-31	{}	{"periodo": "2025-01-01 a 2025-12-31", "transacoes": 3, "posicoes_ativas": 3, "proventos": 28, "patrimonio_final": 0, "rentabilidade_bruta": "12.5%", "rentabilidade_liquida": "10.2%", "sharpe_ratio": 1.45, "max_drawdown": "-8.3%", "ativos_top": ["PETR4", "VALE3", "AAPL"]}	2025-12-12 08:05:21.424109-03	\N	visualizacao	\N	2025-12-12 08:05:21.424113-03	2025-12-12 08:05:21.424114-03
85635f06-2fcd-4e88-8a83-3e4a879e8b0d	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	performance	2025-01-01	2025-12-31	{}	{"periodo": "2025-01-01 a 2025-12-31", "transacoes": 3, "posicoes_ativas": 3, "proventos": 28, "patrimonio_final": 0, "rentabilidade_bruta": "12.5%", "rentabilidade_liquida": "10.2%", "sharpe_ratio": 1.45, "max_drawdown": "-8.3%", "ativos_top": ["PETR4", "VALE3", "AAPL"]}	2025-12-12 08:08:29.34556-03	\N	visualizacao	\N	2025-12-12 08:08:29.345565-03	2025-12-12 08:08:29.345565-03
92510130-ce81-4821-9700-428835686f01	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	performance	2025-01-01	2025-12-31	{}	{"periodo": "2025-01-01 a 2025-12-31", "transacoes": 3, "posicoes_ativas": 3, "proventos": 28, "patrimonio_final": 0, "rentabilidade_bruta": "12.5%", "rentabilidade_liquida": "10.2%", "sharpe_ratio": 1.45, "max_drawdown": "-8.3%", "ativos_top": ["PETR4", "VALE3", "AAPL"]}	2025-12-12 08:13:14.278386-03	\N	visualizacao	\N	2025-12-12 08:13:14.278388-03	2025-12-12 08:13:14.278389-03
da6c165f-e471-48d5-ab87-aea77bc8c2c7	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	performance	2025-01-01	2025-12-31	{}	{"periodo": "2025-01-01 a 2025-12-31", "transacoes": 3, "posicoes_ativas": 3, "proventos": 28, "patrimonio_final": 0, "rentabilidade_bruta": "12.5%", "rentabilidade_liquida": "10.2%", "sharpe_ratio": 1.45, "max_drawdown": "-8.3%", "ativos_top": ["PETR4", "VALE3", "AAPL"]}	2025-12-12 08:15:11.041026-03	\N	visualizacao	\N	2025-12-12 08:15:11.041029-03	2025-12-12 08:15:11.04103-03
e5a64072-664a-4196-9289-9c64305898bc	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	portfolio	\N	\N	{}	{"total_posicoes": 3, "patrimonio_total": 125000.5, "rentabilidade": "12.5%", "lucro_total": 12500.0, "top_ativos": ["PETR4 (R$ 50k)", "VALE3 (R$ 40k)", "ITUB4 (R$ 35k)"], "alocacao_classe": {"Acoes": "65%", "FIIs": "20%", "Renda_Fixa": "15%"}}	2025-12-27 16:29:47.599529-03	\N	visualizacao	\N	2025-12-27 16:29:47.59959-03	2025-12-27 16:29:47.599592-03
247e5178-19d3-41ff-9303-c258154bebce	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	performance	2026-01-01	2026-01-31	{}	{"periodo": "2026-01-01 a 2026-01-31", "transacoes": 3, "posicoes_ativas": 3, "proventos": 28, "patrimonio_final": 0, "rentabilidade_bruta": "12.5%", "rentabilidade_liquida": "10.2%", "sharpe_ratio": 1.45, "max_drawdown": "-8.3%", "ativos_top": ["PETR4", "VALE3", "AAPL"]}	2026-01-05 15:26:57.393705-03	\N	visualizacao	\N	2026-01-05 15:26:57.393725-03	2026-01-05 15:26:57.393727-03
\.


--
-- Data for Name: configuracoes_alertas; Type: TABLE DATA; Schema: public; Owner: exitus
--

COPY public.configuracoes_alertas (id, usuario_id, ativo_id, portfolio_id, nome, tipo_alerta, condicao_valor, condicao_operador, condicao_valor2, ativo, frequencia_notificacao, canais_entrega, timestamp_criacao, timestamp_ultimo_acionamento, created_at, updated_at) FROM stdin;
5c09a4fb-cc0e-4cc7-bb0b-6191f667215a	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	\N	\N	PETR4 > R$35	alta_preco	35.000000	>	\N	t	imediata	{WEBAPP}	2026-01-05 15:14:29.01301-03	\N	2026-01-05 15:14:29.013012-03	2026-01-05 15:16:46.149595-03
\.


--
-- Data for Name: corretora; Type: TABLE DATA; Schema: public; Owner: exitus
--

COPY public.corretora (id, usuario_id, nome, tipo, pais, moeda_padrao, saldo_atual, ativa, observacoes, created_at, updated_at) FROM stdin;
b5a6d786-ed76-4213-b819-45c6fdcd949d	09f8f28f-5ffc-4dff-8256-ab0cef3dd25d	Binance	EXCHANGE	US	USD	5000.00	t	Exchange de criptomoedas	2025-12-02 11:39:10.866109-03	2025-12-02 11:39:10.866112-03
46228e06-200f-49b8-91b6-94ec70601e5c	09f8f28f-5ffc-4dff-8256-ab0cef3dd25d	XP Investimentos	CORRETORA	BR	BRL	15000.00	t	Saldo atualizado	2025-12-02 11:39:10.792426-03	2025-12-02 11:39:11.103585-03
c5c2bc9d-2dde-4d16-ad9b-868628a746d1	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	Clear Corretora	CORRETORA	BR	BRL	10000.00	t	Corretora criada pelo seed M7 para testes de projeção.	2025-12-09 16:34:06.97961-03	2025-12-09 16:34:06.979612-03
011c0c54-58ba-47fd-b9a6-1fb71dbf4bde	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	Corretora Teste a7742a	CORRETORA	BR	BRL	0.00	t	\N	2025-12-13 00:56:07.747828-03	2025-12-13 00:56:07.747833-03
092985a5-ea3f-4e46-ace7-334cede57f10	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	Corretora Teste a684c6	CORRETORA	BR	BRL	0.00	t	\N	2025-12-13 00:58:06.454473-03	2025-12-13 00:58:06.454476-03
81a84ab5-694b-468d-bf7c-8cbfb58e3230	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	Corretora Teste 6945	CORRETORA	BR	BRL	0.00	t	\N	2025-12-13 01:01:10.716771-03	2025-12-13 01:01:10.716775-03
d7546705-2c9b-45c9-bdeb-4c01eb0869e1	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	Corretora Teste 3722	CORRETORA	BR	BRL	0.00	t	\N	2025-12-13 01:01:21.800222-03	2025-12-13 01:01:21.800223-03
6227a455-fbe5-42b8-9f54-d54b1d128c94	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	Corretora Teste 7826	CORRETORA	BR	BRL	0.00	t	\N	2025-12-13 01:03:54.047388-03	2025-12-13 01:03:54.047391-03
2921d0e6-8012-41c2-9107-645af344c854	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	Corretora Teste 1554	CORRETORA	BR	BRL	0.00	t	\N	2025-12-13 01:08:25.193828-03	2025-12-13 01:08:25.193831-03
c991b224-2a04-4295-a80e-81e5fb0b0ffb	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	Corretora Teste 2689	CORRETORA	BR	BRL	0.00	t	\N	2025-12-13 01:09:06.326812-03	2025-12-13 01:09:06.326815-03
11e0673b-7ecc-4ded-a826-753602dffca2	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	Corretora Teste 6780	CORRETORA	BR	BRL	0.00	t	\N	2025-12-13 01:09:37.936949-03	2025-12-13 01:09:37.936951-03
718f4391-a9c3-47f5-a1b9-328758d42ab7	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	Corretora Teste 8186	CORRETORA	BR	BRL	0.00	t	\N	2025-12-13 01:11:48.568585-03	2025-12-13 01:11:48.568587-03
3e0a5a6c-f168-4ef6-96d5-226a25bb1bc4	09f8f28f-5ffc-4dff-8256-ab0cef3dd25d	Clear Corretora	CORRETORA	BR	BRL	0.00	t	\N	2026-02-14 19:47:48.300267-03	2026-02-14 19:47:48.30027-03
3b521621-eddc-4d41-b1cc-8c9f272edd4e	09f8f28f-5ffc-4dff-8256-ab0cef3dd25d	Inter Invest	CORRETORA	BR	BRL	3000.00	t	Conta teste validação	2026-02-16 00:34:39.341822-03	2026-02-16 00:34:39.341828-03
1db3e577-55d9-4873-aff3-2710ab796f50	09f8f28f-5ffc-4dff-8256-ab0cef3dd25d	Avenue Securities	CORRETORA	US	USD	5000.00	t	Saldo atualizado via validação	2025-12-02 11:39:10.900263-03	2026-02-16 00:51:13.359546-03
\.


--
-- Data for Name: evento_corporativo; Type: TABLE DATA; Schema: public; Owner: exitus
--

COPY public.evento_corporativo (id, ativo_id, ativo_novo_id, tipo_evento, data_evento, data_com, proporcao, descricao, impacto_posicoes, observacoes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: feriado_mercado; Type: TABLE DATA; Schema: public; Owner: exitus
--

COPY public.feriado_mercado (id, pais, mercado, data_feriado, tipo_feriado, nome, horario_fechamento, recorrente, observacoes, created_at, updated_at) FROM stdin;
ef412b6a-8af8-4dcb-96e7-92bfe8caa457	BR	B3	2025-01-01	NACIONAL	Confraternização Universal	\N	t	\N	2025-12-01 11:40:20.740643-03	2025-12-01 11:40:20.740645-03
195d17d1-dc41-4f24-a4ac-b776f396bcb7	BR	B3	2025-03-03	NACIONAL	Carnaval	\N	f	\N	2025-12-01 11:40:20.740649-03	2025-12-01 11:40:20.74065-03
acb20f5e-81d4-40aa-b5d7-0b03bc3163fc	BR	B3	2025-03-04	NACIONAL	Carnaval (Quarta de Cinzas - meio período)	\N	f	\N	2025-12-01 11:40:20.740652-03	2025-12-01 11:40:20.740652-03
fb7c9120-eedb-4d4e-ab26-6dc4473c6c98	BR	B3	2025-04-18	NACIONAL	Sexta-feira Santa	\N	t	\N	2025-12-01 11:40:20.740654-03	2025-12-01 11:40:20.740654-03
48c0c74d-6329-405c-b85b-bfe5c2a258c3	BR	B3	2025-04-21	NACIONAL	Tiradentes	\N	t	\N	2025-12-01 11:40:20.740656-03	2025-12-01 11:40:20.740657-03
60a4ae44-42ca-4985-9fa1-e0a65a24b276	BR	B3	2025-05-01	NACIONAL	Dia do Trabalho	\N	t	\N	2025-12-01 11:40:20.740659-03	2025-12-01 11:40:20.740659-03
006b682c-3206-4efc-b3e5-5a742a70ebc2	BR	B3	2025-06-19	NACIONAL	Corpus Christi	\N	f	\N	2025-12-01 11:40:20.740661-03	2025-12-01 11:40:20.740661-03
aee541fc-da57-4ae7-92e6-23dd73c01afb	BR	B3	2025-09-07	NACIONAL	Independência do Brasil	\N	t	\N	2025-12-01 11:40:20.740663-03	2025-12-01 11:40:20.740663-03
10904290-0850-4e97-81de-11e3206a9de9	BR	B3	2025-10-12	NACIONAL	Nossa Senhora Aparecida	\N	t	\N	2025-12-01 11:40:20.740665-03	2025-12-01 11:40:20.740665-03
bdd99f3f-8a55-419a-815e-358a7653a25d	BR	B3	2025-11-02	NACIONAL	Finados	\N	t	\N	2025-12-01 11:40:20.740667-03	2025-12-01 11:40:20.740668-03
74f831c6-94e0-4b17-b385-0f16956ba594	BR	B3	2025-11-15	NACIONAL	Proclamação da República	\N	t	\N	2025-12-01 11:40:20.740669-03	2025-12-01 11:40:20.74067-03
807176a5-b99d-400d-9b37-3779eec2012d	BR	B3	2025-11-20	NACIONAL	Dia da Consciência Negra	\N	t	\N	2025-12-01 11:40:20.740672-03	2025-12-01 11:40:20.740672-03
afa7c876-f66c-4ae5-9914-e4e7b66ac2a1	BR	B3	2025-12-24	FECHAMENTO_ANTECIPADO	Véspera de Natal (meio período)	\N	f	\N	2025-12-01 11:40:20.740674-03	2025-12-01 11:40:20.740674-03
cd09a825-7d16-46c3-bd75-76ebc374d03a	BR	B3	2025-12-25	NACIONAL	Natal	\N	t	\N	2025-12-01 11:40:20.740676-03	2025-12-01 11:40:20.740676-03
5779203e-7863-461d-8e6b-60c9a2b58eaa	BR	B3	2025-12-31	FECHAMENTO_ANTECIPADO	Véspera de Ano Novo (meio período)	\N	f	\N	2025-12-01 11:40:20.740678-03	2025-12-01 11:40:20.740678-03
b7fb2237-02d3-495d-ba50-da60ec7557f4	BR	B3	2026-01-01	NACIONAL	Confraternização Universal	\N	t	\N	2025-12-01 11:40:20.74068-03	2025-12-01 11:40:20.740681-03
acc243c5-314b-4b0e-b0e4-ede4d53621a2	BR	B3	2026-02-16	NACIONAL	Carnaval	\N	f	\N	2025-12-01 11:40:20.740682-03	2025-12-01 11:40:20.740683-03
d48dbdd6-e639-4540-a96a-d52b36079444	BR	B3	2026-02-17	NACIONAL	Carnaval (Quarta de Cinzas - meio período)	\N	f	\N	2025-12-01 11:40:20.740687-03	2025-12-01 11:40:20.740687-03
e978aae1-97cb-482d-94d9-107bb1e414a1	BR	B3	2026-04-03	NACIONAL	Sexta-feira Santa	\N	t	\N	2025-12-01 11:40:20.740689-03	2025-12-01 11:40:20.740689-03
82539b9a-3c46-40de-ab84-0416f21548b1	BR	B3	2026-04-21	NACIONAL	Tiradentes	\N	t	\N	2025-12-01 11:40:20.740691-03	2025-12-01 11:40:20.740691-03
11f431de-76b6-42ef-9183-d56b534d7526	BR	B3	2026-05-01	NACIONAL	Dia do Trabalho	\N	t	\N	2025-12-01 11:40:20.740693-03	2025-12-01 11:40:20.740693-03
439f68f2-dfd4-455f-9782-b58ae0e10dee	BR	B3	2026-06-04	NACIONAL	Corpus Christi	\N	f	\N	2025-12-01 11:40:20.740695-03	2025-12-01 11:40:20.740695-03
c77b784a-6435-414b-a6cb-68e4d99b7b56	BR	B3	2026-09-07	NACIONAL	Independência do Brasil	\N	t	\N	2025-12-01 11:40:20.740697-03	2025-12-01 11:40:20.740698-03
e2f0fd1e-c12c-4ffe-af89-92551a905801	BR	B3	2026-10-12	NACIONAL	Nossa Senhora Aparecida	\N	t	\N	2025-12-01 11:40:20.740699-03	2025-12-01 11:40:20.7407-03
bc78c84e-e1c5-46a8-b5cd-7de51aa3bfcb	BR	B3	2026-11-02	NACIONAL	Finados	\N	t	\N	2025-12-01 11:40:20.740702-03	2025-12-01 11:40:20.740702-03
a3f9060e-a506-47a8-b7eb-5e38afa8a8a8	BR	B3	2026-11-15	NACIONAL	Proclamação da República	\N	t	\N	2025-12-01 11:40:20.740707-03	2025-12-01 11:40:20.740708-03
e432a732-6d1c-4f19-9619-f9a2f8faa020	BR	B3	2026-11-20	NACIONAL	Dia da Consciência Negra	\N	t	\N	2025-12-01 11:40:20.74071-03	2025-12-01 11:40:20.74071-03
98d3c0aa-3f61-4f90-b93a-e25bb04ad859	BR	B3	2026-12-24	FECHAMENTO_ANTECIPADO	Véspera de Natal (meio período)	\N	f	\N	2025-12-01 11:40:20.740712-03	2025-12-01 11:40:20.740712-03
33be522d-6c20-4661-bf5e-dbd473e67d9e	BR	B3	2026-12-25	NACIONAL	Natal	\N	t	\N	2025-12-01 11:40:20.740714-03	2025-12-01 11:40:20.740715-03
2ec52f33-6f67-4426-9c82-37e40005cc8d	BR	B3	2026-12-31	FECHAMENTO_ANTECIPADO	Véspera de Ano Novo (meio período)	\N	f	\N	2025-12-01 11:40:20.740717-03	2025-12-01 11:40:20.740717-03
\.


--
-- Data for Name: fonte_dados; Type: TABLE DATA; Schema: public; Owner: exitus
--

COPY public.fonte_dados (id, nome, tipo_fonte, url_base, requer_autenticacao, rate_limit, ativa, prioridade, ultima_consulta, total_consultas, total_erros, observacoes, created_at, updated_at) FROM stdin;
08119457-0bba-48e9-92f7-a0416310b3a2	yfinance	API	https://query1.finance.yahoo.com	f	2000/hour	t	1	\N	0	0	Biblioteca Python gratuita para Yahoo Finance. Boa cobertura global, incluindo B3.	2025-12-01 11:40:20.772238-03	2025-12-01 11:40:20.77224-03
624fcc51-0476-4659-ad78-a8f051dae452	brapi.dev	API	https://brapi.dev/api	f	100/minute	t	1	\N	0	0	API brasileira gratuita especializada em ativos da B3. Dados em tempo real.	2025-12-01 11:40:20.772243-03	2025-12-01 11:40:20.772244-03
5f6f1925-5d98-4b32-bccc-d49a565e837c	Alpha Vantage	API	https://www.alphavantage.co/query	t	5/minute	t	2	\N	0	0	API gratuita com chave. Limite de 5 requisições por minuto (plano free).	2025-12-01 11:40:20.772246-03	2025-12-01 11:40:20.772246-03
34ed366d-d6d8-4954-85f1-6935a2b66950	Finnhub	API	https://finnhub.io/api/v1	t	60/minute	t	2	\N	0	0	API com plano gratuito. Boa cobertura de mercados globais e notícias.	2025-12-01 11:40:20.772248-03	2025-12-01 11:40:20.772249-03
672c9061-7221-4f35-9703-d2b2cd989e29	IEX Cloud	API	https://cloud.iexapis.com/stable	t	50000/month	t	3	\N	0	0	API focada em mercado americano. Plano gratuito com limite mensal.	2025-12-01 11:40:20.772251-03	2025-12-01 11:40:20.772251-03
fc995d6e-ec1a-4909-a50a-d1595cd08d0f	Polygon.io	API	https://api.polygon.io	t	5/minute	f	4	\N	0	0	API premium com dados históricos detalhados. Desativada por padrão.	2025-12-01 11:40:20.772253-03	2025-12-01 11:40:20.772253-03
327825fc-117c-48a9-8c83-2302f26c0746	Manual	MANUAL	\N	f	\N	t	99	\N	0	0	Entrada manual de dados pelo usuário.	2025-12-01 11:40:20.772256-03	2025-12-01 11:40:20.772256-03
\.


--
-- Data for Name: historico_preco; Type: TABLE DATA; Schema: public; Owner: exitus
--

COPY public.historico_preco (id, ativoid, data, preco_abertura, preco_fechamento, preco_minimo, preco_maximo, volume, createdat, updatedat) FROM stdin;
2ac52200-e300-42eb-8645-5da9c7e11b49	16836286-2538-41bd-9896-f975721df9c0	2026-01-06	31.500000	31.260000	31.100000	31.800000	125000000	2026-01-06 18:15:33.19132	\N
\.


--
-- Data for Name: log_auditoria; Type: TABLE DATA; Schema: public; Owner: exitus
--

COPY public.log_auditoria (id, usuario_id, acao, entidade, entidade_id, dados_antes, dados_depois, ip_address, user_agent, "timestamp", sucesso, mensagem) FROM stdin;
\.


--
-- Data for Name: movimentacao_caixa; Type: TABLE DATA; Schema: public; Owner: exitus
--

COPY public.movimentacao_caixa (id, usuario_id, corretora_id, corretora_destino_id, provento_id, tipo_movimentacao, valor, moeda, data_movimentacao, descricao, comprovante, created_at, updated_at) FROM stdin;
14fbe1d6-66e6-4b24-8781-749fc22a0353	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	718f4391-a9c3-47f5-a1b9-328758d42ab7	\N	\N	DEPOSITO	5000.00	BRL	2026-01-05	FASE 2 Test ✅	\N	2026-01-05 14:34:44.515389-03	2026-01-05 14:34:44.515394-03
1cba84e5-25bc-407f-8f28-425d1f0c70b3	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	718f4391-a9c3-47f5-a1b9-328758d42ab7	\N	\N	DEPOSITO	5000.00	BRL	2026-01-05	FASE 2 ✅	\N	2026-01-05 14:35:18.584903-03	2026-01-05 14:35:18.58491-03
\.


--
-- Data for Name: parametros_macro; Type: TABLE DATA; Schema: public; Owner: exitus
--

COPY public.parametros_macro (id, pais, mercado, taxa_livre_risco, crescimento_medio, custo_capital, inflacao_anual, cap_rate_fii, ytm_rf, ativo, created_at, updated_at) FROM stdin;
a2514d2b-ee8d-473b-8348-26764098428a	BR	B3	0.105000	0.045000	0.125000	0.042000	0.085000	0.115000	t	2025-12-03 16:51:53.63942-03	2025-12-03 16:51:53.63942-03
a9e83385-b498-40a9-81f2-320443fa721b	US	NYSE	0.042000	0.025000	0.085000	0.022000	0.065000	0.045000	t	2025-12-03 16:51:53.63942-03	2025-12-03 16:51:53.63942-03
3bf5e012-068d-4879-87da-0f6a86478a7d	EU	Euronext	0.028000	0.018000	0.072000	0.020000	0.045000	0.032000	t	2025-12-03 16:51:53.63942-03	2025-12-03 16:51:53.63942-03
47f6188d-cd0d-4000-9f3a-0a95a52a97b1	JP	Tokyo	0.001500	0.012000	0.035000	0.015000	0.035000	0.018000	t	2025-12-03 16:51:53.63942-03	2025-12-03 16:51:53.63942-03
\.


--
-- Data for Name: portfolio; Type: TABLE DATA; Schema: public; Owner: exitus
--

COPY public.portfolio (id, usuario_id, nome, descricao, objetivo, ativo, valor_inicial, percentual_alocacao_target, created_at, updated_at) FROM stdin;
1e1c2bfe-e3b8-4ab7-81f5-40d925ffe2e3	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	Portfolio Principal - admin	Carteira principal de investimentos	Crescimento	t	\N	\N	2025-12-18 12:47:24.52581-03	2025-12-18 12:47:24.525813-03
b6629879-1a9e-460f-944f-3f31b7f34d01	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	Aposentadoria 2050	Foco em dividendos	Longo Prazo	t	\N	\N	2025-12-19 15:21:19.002591-03	2025-12-19 15:21:19.002593-03
dd225cba-192b-40a7-abd3-80493ab11c6c	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	Talita 2040	Foco em dividendos e renda passiva	Longo Prazo	t	\N	\N	2025-12-27 07:59:43.637571-03	2025-12-27 07:59:43.637576-03
246148c5-a129-4963-a0e1-eccfba8105a7	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	Portfolio EDITADO	Teste de update	CRESCIMENTO	f	\N	\N	2026-01-02 12:48:00.541562-03	2026-01-02 12:49:21.203916-03
\.


--
-- Data for Name: posicao; Type: TABLE DATA; Schema: public; Owner: exitus
--

COPY public.posicao (id, usuario_id, corretora_id, ativo_id, quantidade, preco_medio, custo_total, taxas_acumuladas, impostos_acumulados, valor_atual, lucro_prejuizo_realizado, lucro_prejuizo_nao_realizado, data_primeira_compra, data_ultima_atualizacao, created_at, updated_at) FROM stdin;
fde0b8b0-e967-4e10-87e6-4e3fd68f05f1	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	c5c2bc9d-2dde-4d16-ad9b-868628a746d1	16836286-2538-41bd-9896-f975721df9c0	100.00000000	35.070000	3507.00	7.00	0.00	\N	0.00	\N	2025-04-09	2025-12-13 01:11:48.699369-03	2025-12-09 16:39:39.209873-03	2025-12-13 01:11:48.70172-03
575d8806-f41f-4625-895d-d1169aefaafa	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	c5c2bc9d-2dde-4d16-ad9b-868628a746d1	3af7860e-e74c-40d2-b1b2-e49e784e25ea	50.00000000	60.140000	3007.00	7.00	0.00	\N	0.00	\N	2025-02-09	2025-12-13 01:11:48.708138-03	2025-12-09 16:39:39.215319-03	2025-12-13 01:11:48.708736-03
4990b451-0dbd-4235-93e9-2a950b0758cf	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	c5c2bc9d-2dde-4d16-ad9b-868628a746d1	b8e4ccc8-3dfe-4a97-a8eb-e21a24c2e2ad	30.00000000	150.233333	4507.00	7.00	0.00	\N	0.00	\N	2025-06-09	2025-12-13 01:11:48.710462-03	2025-12-09 16:39:39.217447-03	2025-12-13 01:11:48.711226-03
300df14f-c910-4495-94de-3f935013d959	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	81a84ab5-694b-468d-bf7c-8cbfb58e3230	e80cc697-1715-4977-9788-34e6ce87aec2	100.00000000	10.000000	1000.00	0.00	0.00	\N	0.00	\N	2025-12-13	2025-12-13 01:11:48.713071-03	2025-12-13 01:11:48.71444-03	2025-12-13 01:11:48.714442-03
6e0e0d00-dabc-4101-99be-d418e83c9fe8	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	81a84ab5-694b-468d-bf7c-8cbfb58e3230	ffb9b04e-e83a-4122-8da5-0bd8047cdee0	10.00000000	100.000000	1000.00	0.00	0.00	\N	0.00	\N	2025-12-13	2025-12-13 01:11:48.717948-03	2025-12-13 01:11:48.71846-03	2025-12-13 01:11:48.718461-03
a012137d-8f47-49ad-b4ba-98a99720f7f9	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	d7546705-2c9b-45c9-bdeb-4c01eb0869e1	483502a0-6759-4d7b-9d72-ddaeea5ae396	100.00000000	10.000000	1000.00	0.00	0.00	\N	0.00	\N	2025-12-13	2025-12-13 01:11:48.720421-03	2025-12-13 01:11:48.720861-03	2025-12-13 01:11:48.720862-03
61b240d0-21da-4537-8cdc-e363590063da	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	d7546705-2c9b-45c9-bdeb-4c01eb0869e1	980d3138-a670-4478-b0c6-b042eacc4964	10.00000000	100.000000	1000.00	0.00	0.00	\N	0.00	\N	2025-12-13	2025-12-13 01:11:48.722628-03	2025-12-13 01:11:48.723006-03	2025-12-13 01:11:48.723007-03
435da084-3773-409c-84c4-b0c0cdce4396	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	6227a455-fbe5-42b8-9f54-d54b1d128c94	89350282-9805-4620-b563-6898cbb33391	100.00000000	10.000000	1000.00	0.00	0.00	\N	0.00	\N	2025-12-13	2025-12-13 01:11:48.724944-03	2025-12-13 01:11:48.725367-03	2025-12-13 01:11:48.725368-03
ff2f8e6d-f2b5-402a-abde-6841236297f6	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	6227a455-fbe5-42b8-9f54-d54b1d128c94	249ce95d-8e26-41f3-9eec-c21c1617004e	10.00000000	100.000000	1000.00	0.00	0.00	\N	0.00	\N	2025-12-13	2025-12-13 01:11:48.72716-03	2025-12-13 01:11:48.72753-03	2025-12-13 01:11:48.727531-03
70a095fa-5681-4b58-92e6-59882f09b0ee	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	2921d0e6-8012-41c2-9107-645af344c854	9543442c-8678-4c1c-8abe-9ab3095950be	100.00000000	10.000000	1000.00	0.00	0.00	\N	0.00	\N	2025-12-13	2025-12-13 01:11:48.729433-03	2025-12-13 01:11:48.729938-03	2025-12-13 01:11:48.729939-03
be5f3ec0-fd84-47be-bc9f-15c26501ebf1	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	2921d0e6-8012-41c2-9107-645af344c854	2f956755-0161-4a78-b083-791152768783	10.00000000	100.000000	1000.00	0.00	0.00	\N	0.00	\N	2025-12-13	2025-12-13 01:11:48.73202-03	2025-12-13 01:11:48.732493-03	2025-12-13 01:11:48.732494-03
8dab47a2-3603-44e9-a964-362464bc19c6	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	c991b224-2a04-4295-a80e-81e5fb0b0ffb	c3401627-f629-48ff-bb1e-b72fb7c6672e	100.00000000	10.000000	1000.00	0.00	0.00	\N	0.00	\N	2025-12-13	2025-12-13 01:11:48.734228-03	2025-12-13 01:11:48.734611-03	2025-12-13 01:11:48.734612-03
0ae276d7-8547-4140-b430-84318148b412	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	c991b224-2a04-4295-a80e-81e5fb0b0ffb	9634a345-c627-4b87-a9bc-e7a4bb753117	10.00000000	100.000000	1000.00	0.00	0.00	\N	0.00	\N	2025-12-13	2025-12-13 01:11:48.73649-03	2025-12-13 01:11:48.736883-03	2025-12-13 01:11:48.736884-03
e91987a3-09f4-4d96-a145-41ed1e556b77	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	11e0673b-7ecc-4ded-a826-753602dffca2	22f6162e-041b-471d-af55-bb7c0fdf7b19	100.00000000	10.000000	1000.00	0.00	0.00	\N	0.00	\N	2025-12-13	2025-12-13 01:11:48.738581-03	2025-12-13 01:11:48.738957-03	2025-12-13 01:11:48.738958-03
fe7d6c9e-393a-4f9a-a8e4-7923960b72f1	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	11e0673b-7ecc-4ded-a826-753602dffca2	5f6e42e4-0382-481b-8c9e-276ea8e507e4	10.00000000	100.000000	1000.00	0.00	0.00	\N	0.00	\N	2025-12-13	2025-12-13 01:11:48.740599-03	2025-12-13 01:11:48.740978-03	2025-12-13 01:11:48.740979-03
0215333f-8c4d-4a4b-97ee-85c7b3fa020c	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	718f4391-a9c3-47f5-a1b9-328758d42ab7	c8feeb6c-8e83-4204-8f3f-441df479d4d1	100.00000000	10.000000	1000.00	0.00	0.00	\N	0.00	\N	2025-12-13	2025-12-13 01:11:48.742636-03	2025-12-13 01:11:48.743002-03	2025-12-13 01:11:48.743003-03
f30a4b22-2d89-4b14-a458-8dc4a3eb091e	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	718f4391-a9c3-47f5-a1b9-328758d42ab7	a40d824e-d186-47e1-94cc-1a1fed8cda7b	10.00000000	100.000000	1000.00	0.00	0.00	\N	0.00	\N	2025-12-13	2025-12-13 01:11:48.744721-03	2025-12-13 01:11:48.74511-03	2025-12-13 01:11:48.745111-03
\.


--
-- Data for Name: projecoes_renda; Type: TABLE DATA; Schema: public; Owner: exitus
--

COPY public.projecoes_renda (id, usuario_id, portfolio_id, mes_ano, renda_dividendos_projetada, renda_jcp_projetada, renda_rendimentos_projetada, renda_total_mes, renda_anual_projetada, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: provento; Type: TABLE DATA; Schema: public; Owner: exitus
--

COPY public.provento (id, ativo_id, tipo_provento, valor_por_acao, quantidade_ativos, valor_bruto, imposto_retido, valor_liquido, data_com, data_pagamento, observacoes, created_at, updated_at) FROM stdin;
0950b7af-f4c8-4471-b8a2-938d0c5e8e44	16836286-2538-41bd-9896-f975721df9c0	DIVIDENDO	0.500000	1.00000000	0.50	0.00	0.50	2025-12-02	2025-12-09	Dividendo mensal PETR4 M-0 - seed M7	2025-12-09 16:39:39.114284-03	2025-12-09 16:39:39.114286-03
fc12a9d4-f860-48b5-b944-cada00aa9d53	16836286-2538-41bd-9896-f975721df9c0	DIVIDENDO	0.500000	1.00000000	0.50	0.00	0.50	2025-11-02	2025-11-09	Dividendo mensal PETR4 M-1 - seed M7	2025-12-09 16:39:39.119835-03	2025-12-09 16:39:39.119838-03
2768c5c1-28c7-4b66-b484-982e33f15cba	16836286-2538-41bd-9896-f975721df9c0	DIVIDENDO	0.490000	1.00000000	0.49	0.00	0.49	2025-10-02	2025-10-09	Dividendo mensal PETR4 M-2 - seed M7	2025-12-09 16:39:39.122487-03	2025-12-09 16:39:39.122489-03
b8aa92ea-f932-4129-8a66-93b77b4084a6	16836286-2538-41bd-9896-f975721df9c0	DIVIDENDO	0.490000	1.00000000	0.49	0.00	0.49	2025-09-02	2025-09-09	Dividendo mensal PETR4 M-3 - seed M7	2025-12-09 16:39:39.125498-03	2025-12-09 16:39:39.1255-03
9df7f75f-0de7-45e0-9ff7-357bbfbfdac8	16836286-2538-41bd-9896-f975721df9c0	DIVIDENDO	0.480000	1.00000000	0.48	0.00	0.48	2025-08-02	2025-08-09	Dividendo mensal PETR4 M-4 - seed M7	2025-12-09 16:39:39.128124-03	2025-12-09 16:39:39.128126-03
ae86c7a4-58bc-428f-bcc1-b9ba79d0103d	16836286-2538-41bd-9896-f975721df9c0	DIVIDENDO	0.480000	1.00000000	0.48	0.00	0.48	2025-07-02	2025-07-09	Dividendo mensal PETR4 M-5 - seed M7	2025-12-09 16:39:39.131435-03	2025-12-09 16:39:39.13144-03
f049b80d-39bb-4003-b5b3-7cb4597624c9	16836286-2538-41bd-9896-f975721df9c0	DIVIDENDO	0.480000	1.00000000	0.48	0.00	0.48	2025-06-02	2025-06-09	Dividendo mensal PETR4 M-6 - seed M7	2025-12-09 16:39:39.13444-03	2025-12-09 16:39:39.134443-03
4e17a11e-5039-4543-8a97-75ca240fd95e	16836286-2538-41bd-9896-f975721df9c0	DIVIDENDO	0.470000	1.00000000	0.47	0.00	0.47	2025-05-02	2025-05-09	Dividendo mensal PETR4 M-7 - seed M7	2025-12-09 16:39:39.136921-03	2025-12-09 16:39:39.136923-03
5b885cc4-41dd-4753-a598-afe1135e8e95	16836286-2538-41bd-9896-f975721df9c0	DIVIDENDO	0.470000	1.00000000	0.47	0.00	0.47	2025-04-02	2025-04-09	Dividendo mensal PETR4 M-8 - seed M7	2025-12-09 16:39:39.139711-03	2025-12-09 16:39:39.139714-03
15c4e383-8a0e-4819-9eef-e21adbdc0ec9	16836286-2538-41bd-9896-f975721df9c0	DIVIDENDO	0.460000	1.00000000	0.46	0.00	0.46	2025-03-02	2025-03-09	Dividendo mensal PETR4 M-9 - seed M7	2025-12-09 16:39:39.142605-03	2025-12-09 16:39:39.142607-03
a0889dfc-b8ab-4955-9e21-5d2e0dbc78da	16836286-2538-41bd-9896-f975721df9c0	DIVIDENDO	0.460000	1.00000000	0.46	0.00	0.46	2025-02-02	2025-02-09	Dividendo mensal PETR4 M-10 - seed M7	2025-12-09 16:39:39.145256-03	2025-12-09 16:39:39.145259-03
a0e45acb-a998-46f3-8ad1-6d77c4ae8181	16836286-2538-41bd-9896-f975721df9c0	DIVIDENDO	0.450000	1.00000000	0.45	0.00	0.45	2025-01-02	2025-01-09	Dividendo mensal PETR4 M-11 - seed M7	2025-12-09 16:39:39.148527-03	2025-12-09 16:39:39.148529-03
73c95b64-3fc4-4985-a25a-70ded29266c3	3af7860e-e74c-40d2-b1b2-e49e784e25ea	DIVIDENDO	1.200000	1.00000000	1.20	0.00	1.20	2025-12-02	2025-12-09	Dividendo trimestral VALE3 Q-0 - seed M7	2025-12-09 16:39:39.152148-03	2025-12-09 16:39:39.15215-03
a88d4676-734a-4117-9884-48bbc5fd9287	3af7860e-e74c-40d2-b1b2-e49e784e25ea	DIVIDENDO	1.200000	1.00000000	1.20	0.00	1.20	2025-09-02	2025-09-09	Dividendo trimestral VALE3 Q-1 - seed M7	2025-12-09 16:39:39.154599-03	2025-12-09 16:39:39.154601-03
90c61acb-8799-4e6a-94be-539dfd4b2d61	3af7860e-e74c-40d2-b1b2-e49e784e25ea	DIVIDENDO	1.200000	1.00000000	1.20	0.00	1.20	2025-06-02	2025-06-09	Dividendo trimestral VALE3 Q-2 - seed M7	2025-12-09 16:39:39.157356-03	2025-12-09 16:39:39.157358-03
cc27bd19-01c9-4420-a42d-24e02fc0c633	3af7860e-e74c-40d2-b1b2-e49e784e25ea	DIVIDENDO	1.200000	1.00000000	1.20	0.00	1.20	2025-03-02	2025-03-09	Dividendo trimestral VALE3 Q-3 - seed M7	2025-12-09 16:39:39.159799-03	2025-12-09 16:39:39.159801-03
8b2157a0-cd44-4077-a43e-d911229de56d	b8e4ccc8-3dfe-4a97-a8eb-e21a24c2e2ad	RENDIMENTO	1.170000	1.00000000	1.17	0.00	1.17	2025-11-02	2025-11-09	Rendimento KNRI11 M-1 - seed M7	2025-12-09 16:39:39.166935-03	2025-12-09 16:39:39.166936-03
5ccbb39b-106a-4628-9288-9dae3976a74a	b8e4ccc8-3dfe-4a97-a8eb-e21a24c2e2ad	RENDIMENTO	1.170000	1.00000000	1.17	0.00	1.17	2025-10-02	2025-10-09	Rendimento KNRI11 M-2 - seed M7	2025-12-09 16:39:39.169321-03	2025-12-09 16:39:39.169322-03
107206c4-53d9-42b1-aa26-7f0e45fc14ab	b8e4ccc8-3dfe-4a97-a8eb-e21a24c2e2ad	RENDIMENTO	1.160000	1.00000000	1.16	0.00	1.16	2025-09-02	2025-09-09	Rendimento KNRI11 M-3 - seed M7	2025-12-09 16:39:39.172637-03	2025-12-09 16:39:39.172639-03
b6ae1fe9-aba6-4b2a-b166-ad6b8f634a75	b8e4ccc8-3dfe-4a97-a8eb-e21a24c2e2ad	RENDIMENTO	1.160000	1.00000000	1.16	0.00	1.16	2025-08-02	2025-08-09	Rendimento KNRI11 M-4 - seed M7	2025-12-09 16:39:39.175009-03	2025-12-09 16:39:39.175011-03
023a32d1-271b-4a4d-8587-20ec0d301a41	b8e4ccc8-3dfe-4a97-a8eb-e21a24c2e2ad	RENDIMENTO	1.160000	1.00000000	1.16	0.00	1.16	2025-07-02	2025-07-09	Rendimento KNRI11 M-5 - seed M7	2025-12-09 16:39:39.177366-03	2025-12-09 16:39:39.177368-03
397d9005-d06c-4d67-9727-e51fe5281cfe	b8e4ccc8-3dfe-4a97-a8eb-e21a24c2e2ad	RENDIMENTO	1.160000	1.00000000	1.16	0.00	1.16	2025-06-02	2025-06-09	Rendimento KNRI11 M-6 - seed M7	2025-12-09 16:39:39.180565-03	2025-12-09 16:39:39.180567-03
56397005-e37a-4893-9491-434b1d02df89	b8e4ccc8-3dfe-4a97-a8eb-e21a24c2e2ad	RENDIMENTO	1.160000	1.00000000	1.16	0.00	1.16	2025-05-02	2025-05-09	Rendimento KNRI11 M-7 - seed M7	2025-12-09 16:39:39.183205-03	2025-12-09 16:39:39.183208-03
9e602c2d-fc85-4c56-b261-096ad697fed8	b8e4ccc8-3dfe-4a97-a8eb-e21a24c2e2ad	RENDIMENTO	1.160000	1.00000000	1.16	0.00	1.16	2025-04-02	2025-04-09	Rendimento KNRI11 M-8 - seed M7	2025-12-09 16:39:39.185674-03	2025-12-09 16:39:39.185677-03
5c451813-93f8-4121-9e3b-9abaf4c261a1	b8e4ccc8-3dfe-4a97-a8eb-e21a24c2e2ad	RENDIMENTO	1.160000	1.00000000	1.16	0.00	1.16	2025-03-02	2025-03-09	Rendimento KNRI11 M-9 - seed M7	2025-12-09 16:39:39.188569-03	2025-12-09 16:39:39.188571-03
37e9ebed-0610-4cd8-8744-3e42e062b163	b8e4ccc8-3dfe-4a97-a8eb-e21a24c2e2ad	RENDIMENTO	1.150000	1.00000000	1.15	0.00	1.15	2025-02-02	2025-02-09	Rendimento KNRI11 M-10 - seed M7	2025-12-09 16:39:39.191024-03	2025-12-09 16:39:39.191026-03
26605313-954c-4240-a751-cd5ea68f9a85	b8e4ccc8-3dfe-4a97-a8eb-e21a24c2e2ad	RENDIMENTO	1.150000	1.00000000	1.15	0.00	1.15	2025-01-02	2025-01-09	Rendimento KNRI11 M-11 - seed M7	2025-12-09 16:39:39.193089-03	2025-12-09 16:39:39.193092-03
dae6d91f-741c-4724-918a-311b9b920219	b8e4ccc8-3dfe-4a97-a8eb-e21a24c2e2ad	RENDIMENTO	1.170000	1.00000000	1.17	0.00	1.17	2025-12-02	2025-12-09	Observação atualizada via API	2025-12-09 16:39:39.164017-03	2026-01-03 11:07:40.978196-03
829b05be-ed57-4145-bf8b-ef31f7346768	69870f88-f1bb-4b21-8194-0d18fee4b81b	DIVIDENDO	1.500000	100.00000000	150.00	0.00	150.00	2025-12-15	2025-12-22	Provento de teste criado via API	2026-01-03 12:13:47.346983-03	2026-01-03 12:13:47.346986-03
\.


--
-- Data for Name: regra_fiscal; Type: TABLE DATA; Schema: public; Owner: exitus
--

COPY public.regra_fiscal (id, pais, tipo_ativo, tipo_operacao, aliquota_ir, valor_isencao, incide_sobre, descricao, vigencia_inicio, vigencia_fim, ativa, created_at, updated_at) FROM stdin;
881ed004-6665-4459-96d0-097639c7d0d4	BR	ACAO	SWING_TRADE	15.0000	20000.00	LUCRO	IR sobre ganho de capital em ações - Swing Trade. Isenção para vendas até R$ 20.000,00 por mês.	2024-01-01	\N	t	2025-12-01 11:40:20.70985-03	2025-12-01 11:40:20.709853-03
541ca12c-2698-4637-9735-034c111485c8	BR	ACAO	DAY_TRADE	20.0000	\N	LUCRO	IR sobre ganho de capital em Day Trade. SEM isenção, alíquota de 20%.	2024-01-01	\N	t	2025-12-01 11:40:20.709857-03	2025-12-01 11:40:20.709857-03
dad45709-3222-4319-a5ef-a361c6c5ab14	BR	FII	SWING_TRADE	20.0000	\N	LUCRO	IR sobre ganho de capital em FIIs. SEM isenção, alíquota de 20%.	2024-01-01	\N	t	2025-12-01 11:40:20.70986-03	2025-12-01 11:40:20.70986-03
f9fb9e58-29e2-4050-aa57-cc5517e9ec76	BR	\N	\N	15.0000	\N	PROVENTO	IR sobre JCP (Juros sobre Capital Próprio). Retido na fonte, alíquota de 15%.	2024-01-01	\N	t	2025-12-01 11:40:20.709862-03	2025-12-01 11:40:20.709863-03
e2f14fb7-018c-4305-9af9-9dd659a43e24	BR	FII	\N	0.0000	\N	PROVENTO	Rendimentos de FII são ISENTOS de IR para pessoa física (requisitos: FII com +50 cotistas, cotas negociadas em bolsa, investidor com <10% das cotas).	2024-01-01	\N	t	2025-12-01 11:40:20.709865-03	2025-12-01 11:40:20.709865-03
ad2e3d5e-3a17-4960-b657-e778219d87d4	BR	ACAO	\N	0.0000	\N	PROVENTO	Dividendos de ações são ISENTOS de IR para pessoa física no Brasil.	2024-01-01	\N	t	2025-12-01 11:40:20.709867-03	2025-12-01 11:40:20.709868-03
\.


--
-- Data for Name: relatorios_performance; Type: TABLE DATA; Schema: public; Owner: exitus
--

COPY public.relatorios_performance (id, usuario_id, portfolio_id, periodo_inicio, periodo_fim, retorno_bruto_percentual, retorno_liquido_percentual, indice_sharpe, max_drawdown_percentual, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: transacao; Type: TABLE DATA; Schema: public; Owner: exitus
--

COPY public.transacao (id, usuario_id, tipo, ativo_id, corretora_id, data_transacao, quantidade, preco_unitario, valor_total, taxa_corretagem, taxa_liquidacao, emolumentos, imposto, outros_custos, custos_totais, valor_liquido, observacoes, created_at, updated_at) FROM stdin;
51d38bb0-5697-465d-8088-060b4267896e	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	COMPRA	16836286-2538-41bd-9896-f975721df9c0	c5c2bc9d-2dde-4d16-ad9b-868628a746d1	2025-04-08 21:00:00-03	100.00000000	35.000000	3500.00	5.00	1.00	1.00	0.00	0.00	7.00	3507.00	Transação de compra criada pelo seed M7.	2025-12-09 16:37:45.97062-03	2025-12-09 16:37:45.970622-03
011f3061-9b26-46f3-964c-6196d78563d7	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	COMPRA	3af7860e-e74c-40d2-b1b2-e49e784e25ea	c5c2bc9d-2dde-4d16-ad9b-868628a746d1	2025-02-08 21:00:00-03	50.00000000	60.000000	3000.00	5.00	1.00	1.00	0.00	0.00	7.00	3007.00	Transação de compra criada pelo seed M7.	2025-12-09 16:37:45.979348-03	2025-12-09 16:37:45.979352-03
7fe2cc82-4b8e-4e34-8280-461a8a1d52f2	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	COMPRA	b8e4ccc8-3dfe-4a97-a8eb-e21a24c2e2ad	c5c2bc9d-2dde-4d16-ad9b-868628a746d1	2025-06-08 21:00:00-03	30.00000000	150.000000	4500.00	5.00	1.00	1.00	0.00	0.00	7.00	4507.00	Transação de compra criada pelo seed M7.	2025-12-09 16:37:45.982344-03	2025-12-09 16:37:45.982347-03
c6f7231d-aaf1-4166-acae-4c0b8528b65e	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	COMPRA	e80cc697-1715-4977-9788-34e6ce87aec2	81a84ab5-694b-468d-bf7c-8cbfb58e3230	2025-12-12 22:01:10.775015-03	100.00000000	10.000000	1000.00	0.00	0.00	0.00	0.00	0.00	0.00	1000.00	\N	2025-12-13 01:01:10.788178-03	2025-12-13 01:01:10.78818-03
bdd657c2-bd84-409a-b442-8e73be138c41	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	COMPRA	ffb9b04e-e83a-4122-8da5-0bd8047cdee0	81a84ab5-694b-468d-bf7c-8cbfb58e3230	2025-12-12 22:01:10.802785-03	10.00000000	100.000000	1000.00	0.00	0.00	0.00	0.00	0.00	0.00	1000.00	\N	2025-12-13 01:01:10.808969-03	2025-12-13 01:01:10.808971-03
ee635113-1080-4abe-8cf4-e7320d489839	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	COMPRA	483502a0-6759-4d7b-9d72-ddaeea5ae396	d7546705-2c9b-45c9-bdeb-4c01eb0869e1	2025-12-12 22:01:21.848606-03	100.00000000	10.000000	1000.00	0.00	0.00	0.00	0.00	0.00	0.00	1000.00	\N	2025-12-13 01:01:21.854421-03	2025-12-13 01:01:21.854422-03
0290e9c7-c6b0-4ece-8051-b42fb49b238d	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	COMPRA	980d3138-a670-4478-b0c6-b042eacc4964	d7546705-2c9b-45c9-bdeb-4c01eb0869e1	2025-12-12 22:01:21.862683-03	10.00000000	100.000000	1000.00	0.00	0.00	0.00	0.00	0.00	0.00	1000.00	\N	2025-12-13 01:01:21.867568-03	2025-12-13 01:01:21.867569-03
6253cc29-7096-496b-8d78-7fd349e498c1	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	COMPRA	89350282-9805-4620-b563-6898cbb33391	6227a455-fbe5-42b8-9f54-d54b1d128c94	2025-12-12 22:03:54.101489-03	100.00000000	10.000000	1000.00	0.00	0.00	0.00	0.00	0.00	0.00	1000.00	\N	2025-12-13 01:03:54.108781-03	2025-12-13 01:03:54.108784-03
9b6a9e8a-603f-4e22-96cf-3deaa1c6ef37	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	COMPRA	249ce95d-8e26-41f3-9eec-c21c1617004e	6227a455-fbe5-42b8-9f54-d54b1d128c94	2025-12-12 22:03:54.11802-03	10.00000000	100.000000	1000.00	0.00	0.00	0.00	0.00	0.00	0.00	1000.00	\N	2025-12-13 01:03:54.136642-03	2025-12-13 01:03:54.136645-03
bbfb0e7b-aef3-4884-87f7-1115c96f5318	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	COMPRA	9543442c-8678-4c1c-8abe-9ab3095950be	2921d0e6-8012-41c2-9107-645af344c854	2025-12-12 22:08:25.236986-03	100.00000000	10.000000	1000.00	0.00	0.00	0.00	0.00	0.00	0.00	1000.00	\N	2025-12-13 01:08:25.2443-03	2025-12-13 01:08:25.244302-03
c24e0323-0743-4251-b0dd-85dd36886ad3	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	COMPRA	2f956755-0161-4a78-b083-791152768783	2921d0e6-8012-41c2-9107-645af344c854	2025-12-12 22:08:25.255343-03	10.00000000	100.000000	1000.00	0.00	0.00	0.00	0.00	0.00	0.00	1000.00	\N	2025-12-13 01:08:25.262497-03	2025-12-13 01:08:25.262499-03
750d7b4d-e69a-4d25-b515-9ffca8226f51	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	COMPRA	c3401627-f629-48ff-bb1e-b72fb7c6672e	c991b224-2a04-4295-a80e-81e5fb0b0ffb	2025-12-12 22:09:06.368853-03	100.00000000	10.000000	1000.00	0.00	0.00	0.00	0.00	0.00	0.00	1000.00	\N	2025-12-13 01:09:06.380818-03	2025-12-13 01:09:06.38082-03
25de0a7b-9034-4458-a727-59ce181307c3	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	COMPRA	9634a345-c627-4b87-a9bc-e7a4bb753117	c991b224-2a04-4295-a80e-81e5fb0b0ffb	2025-12-12 22:09:06.39438-03	10.00000000	100.000000	1000.00	0.00	0.00	0.00	0.00	0.00	0.00	1000.00	\N	2025-12-13 01:09:06.400868-03	2025-12-13 01:09:06.400871-03
ea97a3b0-52c1-4868-b45a-a66539598fda	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	COMPRA	22f6162e-041b-471d-af55-bb7c0fdf7b19	11e0673b-7ecc-4ded-a826-753602dffca2	2025-12-12 22:09:37.970751-03	100.00000000	10.000000	1000.00	0.00	0.00	0.00	0.00	0.00	0.00	1000.00	\N	2025-12-13 01:09:37.977218-03	2025-12-13 01:09:37.97722-03
893d4859-a3b4-4068-a2e9-781ea69ac6b5	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	COMPRA	5f6e42e4-0382-481b-8c9e-276ea8e507e4	11e0673b-7ecc-4ded-a826-753602dffca2	2025-12-12 22:09:37.986088-03	10.00000000	100.000000	1000.00	0.00	0.00	0.00	0.00	0.00	0.00	1000.00	\N	2025-12-13 01:09:37.999285-03	2025-12-13 01:09:37.999287-03
d4a35b6c-1d2a-4f2c-bdcc-2b1ae31f8ff3	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	COMPRA	c8feeb6c-8e83-4204-8f3f-441df479d4d1	718f4391-a9c3-47f5-a1b9-328758d42ab7	2025-12-12 22:11:48.63312-03	100.00000000	10.000000	1000.00	0.00	0.00	0.00	0.00	0.00	0.00	1000.00	\N	2025-12-13 01:11:48.647201-03	2025-12-13 01:11:48.647204-03
d0d2d31f-128e-4270-986f-3b292aa90312	783c2bfd-9e36-4cbd-a4fb-901afae9fad3	COMPRA	a40d824e-d186-47e1-94cc-1a1fed8cda7b	718f4391-a9c3-47f5-a1b9-328758d42ab7	2025-12-12 22:11:48.660396-03	10.00000000	100.000000	1000.00	0.00	0.00	0.00	0.00	0.00	0.00	1000.00	\N	2025-12-13 01:11:48.672123-03	2025-12-13 01:11:48.672125-03
\.


--
-- Data for Name: usuario; Type: TABLE DATA; Schema: public; Owner: exitus
--

COPY public.usuario (id, username, email, password_hash, nome_completo, ativo, role, created_at, updated_at) FROM stdin;
09f8f28f-5ffc-4dff-8256-ab0cef3dd25d	joao.silva	joao.silva@example.com	scrypt:32768:8:1$YEbDvhVA6Y6tPTfJ$a11e9d3f6a09a1e0575216be12c988688ab5b7f0c6920e65e3bf67c5800ce2e8d7acd7517bd08713c7525d2a6bf667efc2ce0dcc0aeb036f466cc674a6029e08	João Silva Atualizado	t	USER	2025-12-01 11:40:20.6397-03	2026-02-15 23:47:01.74037-03
155d5548-2cc5-40f9-953d-d8daf04dd6d8	novo_admin	novoadmin@test.com	scrypt:32768:8:1$588yirlDzpLCTnII$40d6b33eeece617ae8bba287b9071224016401ec11ac93307c23d88e8f426bddfd6570676735128a9fd0fb6fccaf7a59fb92e4e1bd195296968ecbf7fccc87b1	Novo Administrador	t	ADMIN	2026-02-15 15:25:52.784713-03	2026-02-15 15:25:52.784715-03
1f977dd3-c810-49af-a896-4862dbb375e0	teste.user	teste@exitus.com	scrypt:32768:8:1$FOqqzJW7Fxo5b8Ao$8b0882f5f3f8048d4a763b3b4077d42a89b2aa96e32b71acafcf26c5d21bff211d3c1cd1ff9dd4d2a35195834ec586f82a233fa2cee74b598d6d7b7200401783	Usuário de Teste	t	USER	2025-12-02 11:32:30.74402-03	2026-02-15 23:47:01.740372-03
783c2bfd-9e36-4cbd-a4fb-901afae9fad3	admin	admin@exitus.com	scrypt:32768:8:1$W97XVrjluI9CQPnv$a8e687fb93a9c4d0c8521e080a0809000e66c15f748f86f63ba4f52d072e58c723b32148bb63f43af8fb4bbb80798fdb598af8beef4e461d5f8111cd03fc5661	Administrador do Sistema	t	ADMIN	2025-12-01 11:40:20.639694-03	2026-02-15 23:47:01.740372-03
8d11c310-fa71-4b1b-b2c9-13331563803f	viewer	viewer@exitus.com	scrypt:32768:8:1$gbN2lNyc0JciwZVe$d0cfc4f26573a362b779241b512103ed63f23ea05b375bbc7d2ff66659fbb14452ea78813456a87f0bd00c8827cc2d67f32d31b710cdbf6284d280c961088904	Usuário Visualizador	t	READONLY	2025-12-01 11:40:20.639711-03	2026-02-15 23:47:01.740373-03
d40de14b-1079-4f7b-9162-94ded563e65d	maria.santos	maria.santos@example.com	scrypt:32768:8:1$NMsXNJQ6c6OgqXeM$6bcd0b41b17b11fa49da20574d26e645dc590039099405a2b382c4c0a2270e5c021a8befa7a7dbfe7f6884c862cd494f3a15c2a17530e6ae29bc7fa7c4249623	Maria Santos - Teste após GAP-005	f	USER	2025-12-01 11:40:20.639704-03	2026-02-15 23:47:01.740375-03
\.


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: alertas alertas_pkey; Type: CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.alertas
    ADD CONSTRAINT alertas_pkey PRIMARY KEY (id);


--
-- Name: ativo ativo_pkey; Type: CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.ativo
    ADD CONSTRAINT ativo_pkey PRIMARY KEY (id);


--
-- Name: auditoria_relatorios auditoria_relatorios_pkey; Type: CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.auditoria_relatorios
    ADD CONSTRAINT auditoria_relatorios_pkey PRIMARY KEY (id);


--
-- Name: configuracoes_alertas configuracoes_alertas_pkey; Type: CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.configuracoes_alertas
    ADD CONSTRAINT configuracoes_alertas_pkey PRIMARY KEY (id);


--
-- Name: corretora corretora_pkey; Type: CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.corretora
    ADD CONSTRAINT corretora_pkey PRIMARY KEY (id);


--
-- Name: evento_corporativo evento_corporativo_pkey; Type: CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.evento_corporativo
    ADD CONSTRAINT evento_corporativo_pkey PRIMARY KEY (id);


--
-- Name: feriado_mercado feriado_mercado_pkey; Type: CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.feriado_mercado
    ADD CONSTRAINT feriado_mercado_pkey PRIMARY KEY (id);


--
-- Name: fonte_dados fonte_dados_pkey; Type: CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.fonte_dados
    ADD CONSTRAINT fonte_dados_pkey PRIMARY KEY (id);


--
-- Name: historico_preco historico_preco_pkey; Type: CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.historico_preco
    ADD CONSTRAINT historico_preco_pkey PRIMARY KEY (id);


--
-- Name: log_auditoria log_auditoria_pkey; Type: CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.log_auditoria
    ADD CONSTRAINT log_auditoria_pkey PRIMARY KEY (id);


--
-- Name: movimentacao_caixa movimentacao_caixa_pkey; Type: CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.movimentacao_caixa
    ADD CONSTRAINT movimentacao_caixa_pkey PRIMARY KEY (id);


--
-- Name: parametros_macro parametros_macro_pkey; Type: CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.parametros_macro
    ADD CONSTRAINT parametros_macro_pkey PRIMARY KEY (id);


--
-- Name: portfolio portfolio_pkey; Type: CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.portfolio
    ADD CONSTRAINT portfolio_pkey PRIMARY KEY (id);


--
-- Name: posicao posicao_pkey; Type: CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.posicao
    ADD CONSTRAINT posicao_pkey PRIMARY KEY (id);


--
-- Name: projecoes_renda projecoes_renda_pkey; Type: CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.projecoes_renda
    ADD CONSTRAINT projecoes_renda_pkey PRIMARY KEY (id);


--
-- Name: projecoes_renda projecoes_renda_usuario_id_portfolio_id_mes_ano_key; Type: CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.projecoes_renda
    ADD CONSTRAINT projecoes_renda_usuario_id_portfolio_id_mes_ano_key UNIQUE (usuario_id, portfolio_id, mes_ano);


--
-- Name: provento provento_pkey; Type: CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.provento
    ADD CONSTRAINT provento_pkey PRIMARY KEY (id);


--
-- Name: regra_fiscal regra_fiscal_pkey; Type: CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.regra_fiscal
    ADD CONSTRAINT regra_fiscal_pkey PRIMARY KEY (id);


--
-- Name: relatorios_performance relatorios_performance_pkey; Type: CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.relatorios_performance
    ADD CONSTRAINT relatorios_performance_pkey PRIMARY KEY (id);


--
-- Name: transacao transacao_pkey; Type: CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.transacao
    ADD CONSTRAINT transacao_pkey PRIMARY KEY (id);


--
-- Name: feriado_mercado unique_feriado_pais_mercado_data; Type: CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.feriado_mercado
    ADD CONSTRAINT unique_feriado_pais_mercado_data UNIQUE (pais, mercado, data_feriado);


--
-- Name: posicao unique_posicao_usuario_corretora_ativo; Type: CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.posicao
    ADD CONSTRAINT unique_posicao_usuario_corretora_ativo UNIQUE (usuario_id, corretora_id, ativo_id);


--
-- Name: historico_preco uq_historico_ativo_data; Type: CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.historico_preco
    ADD CONSTRAINT uq_historico_ativo_data UNIQUE (ativoid, data);


--
-- Name: usuario usuario_pkey; Type: CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_pkey PRIMARY KEY (id);


--
-- Name: idx_alertas_nome; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX idx_alertas_nome ON public.alertas USING btree (nome);


--
-- Name: idx_alertas_tipo; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX idx_alertas_tipo ON public.alertas USING btree (tipo_alerta);


--
-- Name: idx_alertas_usuario_id; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX idx_alertas_usuario_id ON public.alertas USING btree (usuario_id);


--
-- Name: ix_ativo_ativo; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_ativo_ativo ON public.ativo USING btree (ativo);


--
-- Name: ix_ativo_classe; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_ativo_classe ON public.ativo USING btree (classe);


--
-- Name: ix_ativo_data_ultima_cotacao; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_ativo_data_ultima_cotacao ON public.ativo USING btree (data_ultima_cotacao);


--
-- Name: ix_ativo_deslistado; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_ativo_deslistado ON public.ativo USING btree (deslistado);


--
-- Name: ix_ativo_mercado; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_ativo_mercado ON public.ativo USING btree (mercado);


--
-- Name: ix_ativo_moeda; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_ativo_moeda ON public.ativo USING btree (moeda);


--
-- Name: ix_ativo_nome; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_ativo_nome ON public.ativo USING btree (nome);


--
-- Name: ix_ativo_ticker; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_ativo_ticker ON public.ativo USING btree (ticker);


--
-- Name: ix_ativo_tipo; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_ativo_tipo ON public.ativo USING btree (tipo);


--
-- Name: ix_auditoria_relatorios_chave_api_auditoria; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_auditoria_relatorios_chave_api_auditoria ON public.auditoria_relatorios USING btree (chave_api_auditoria);


--
-- Name: ix_auditoria_relatorios_data_fim; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_auditoria_relatorios_data_fim ON public.auditoria_relatorios USING btree (data_fim);


--
-- Name: ix_auditoria_relatorios_data_inicio; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_auditoria_relatorios_data_inicio ON public.auditoria_relatorios USING btree (data_inicio);


--
-- Name: ix_auditoria_relatorios_formato_export; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_auditoria_relatorios_formato_export ON public.auditoria_relatorios USING btree (formato_export);


--
-- Name: ix_auditoria_relatorios_timestamp_criacao; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_auditoria_relatorios_timestamp_criacao ON public.auditoria_relatorios USING btree (timestamp_criacao);


--
-- Name: ix_auditoria_relatorios_timestamp_download; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_auditoria_relatorios_timestamp_download ON public.auditoria_relatorios USING btree (timestamp_download);


--
-- Name: ix_auditoria_relatorios_tipo_relatorio; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_auditoria_relatorios_tipo_relatorio ON public.auditoria_relatorios USING btree (tipo_relatorio);


--
-- Name: ix_auditoria_relatorios_usuario_id; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_auditoria_relatorios_usuario_id ON public.auditoria_relatorios USING btree (usuario_id);


--
-- Name: ix_configuracoes_alertas_ativo; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_configuracoes_alertas_ativo ON public.configuracoes_alertas USING btree (ativo);


--
-- Name: ix_configuracoes_alertas_ativo_id; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_configuracoes_alertas_ativo_id ON public.configuracoes_alertas USING btree (ativo_id);


--
-- Name: ix_configuracoes_alertas_portfolio_id; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_configuracoes_alertas_portfolio_id ON public.configuracoes_alertas USING btree (portfolio_id);


--
-- Name: ix_configuracoes_alertas_timestamp_criacao; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_configuracoes_alertas_timestamp_criacao ON public.configuracoes_alertas USING btree (timestamp_criacao);


--
-- Name: ix_configuracoes_alertas_timestamp_ultimo_acionamento; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_configuracoes_alertas_timestamp_ultimo_acionamento ON public.configuracoes_alertas USING btree (timestamp_ultimo_acionamento);


--
-- Name: ix_configuracoes_alertas_tipo_alerta; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_configuracoes_alertas_tipo_alerta ON public.configuracoes_alertas USING btree (tipo_alerta);


--
-- Name: ix_configuracoes_alertas_usuario_id; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_configuracoes_alertas_usuario_id ON public.configuracoes_alertas USING btree (usuario_id);


--
-- Name: ix_corretora_ativa; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_corretora_ativa ON public.corretora USING btree (ativa);


--
-- Name: ix_corretora_moeda_padrao; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_corretora_moeda_padrao ON public.corretora USING btree (moeda_padrao);


--
-- Name: ix_corretora_nome; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_corretora_nome ON public.corretora USING btree (nome);


--
-- Name: ix_corretora_pais; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_corretora_pais ON public.corretora USING btree (pais);


--
-- Name: ix_corretora_tipo; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_corretora_tipo ON public.corretora USING btree (tipo);


--
-- Name: ix_corretora_usuario_id; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_corretora_usuario_id ON public.corretora USING btree (usuario_id);


--
-- Name: ix_evento_corporativo_ativo_id; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_evento_corporativo_ativo_id ON public.evento_corporativo USING btree (ativo_id);


--
-- Name: ix_evento_corporativo_ativo_novo_id; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_evento_corporativo_ativo_novo_id ON public.evento_corporativo USING btree (ativo_novo_id);


--
-- Name: ix_evento_corporativo_data_com; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_evento_corporativo_data_com ON public.evento_corporativo USING btree (data_com);


--
-- Name: ix_evento_corporativo_data_evento; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_evento_corporativo_data_evento ON public.evento_corporativo USING btree (data_evento);


--
-- Name: ix_evento_corporativo_impacto_posicoes; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_evento_corporativo_impacto_posicoes ON public.evento_corporativo USING btree (impacto_posicoes);


--
-- Name: ix_evento_corporativo_tipo_evento; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_evento_corporativo_tipo_evento ON public.evento_corporativo USING btree (tipo_evento);


--
-- Name: ix_feriado_mercado_data_feriado; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_feriado_mercado_data_feriado ON public.feriado_mercado USING btree (data_feriado);


--
-- Name: ix_feriado_mercado_mercado; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_feriado_mercado_mercado ON public.feriado_mercado USING btree (mercado);


--
-- Name: ix_feriado_mercado_pais; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_feriado_mercado_pais ON public.feriado_mercado USING btree (pais);


--
-- Name: ix_feriado_mercado_recorrente; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_feriado_mercado_recorrente ON public.feriado_mercado USING btree (recorrente);


--
-- Name: ix_feriado_mercado_tipo_feriado; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_feriado_mercado_tipo_feriado ON public.feriado_mercado USING btree (tipo_feriado);


--
-- Name: ix_fonte_dados_ativa; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_fonte_dados_ativa ON public.fonte_dados USING btree (ativa);


--
-- Name: ix_fonte_dados_nome; Type: INDEX; Schema: public; Owner: exitus
--

CREATE UNIQUE INDEX ix_fonte_dados_nome ON public.fonte_dados USING btree (nome);


--
-- Name: ix_fonte_dados_prioridade; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_fonte_dados_prioridade ON public.fonte_dados USING btree (prioridade);


--
-- Name: ix_fonte_dados_tipo_fonte; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_fonte_dados_tipo_fonte ON public.fonte_dados USING btree (tipo_fonte);


--
-- Name: ix_fonte_dados_ultima_consulta; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_fonte_dados_ultima_consulta ON public.fonte_dados USING btree (ultima_consulta);


--
-- Name: ix_historico_ativoid_data; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_historico_ativoid_data ON public.historico_preco USING btree (ativoid, data);


--
-- Name: ix_log_auditoria_acao; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_log_auditoria_acao ON public.log_auditoria USING btree (acao);


--
-- Name: ix_log_auditoria_entidade; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_log_auditoria_entidade ON public.log_auditoria USING btree (entidade);


--
-- Name: ix_log_auditoria_entidade_id; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_log_auditoria_entidade_id ON public.log_auditoria USING btree (entidade_id);


--
-- Name: ix_log_auditoria_ip_address; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_log_auditoria_ip_address ON public.log_auditoria USING btree (ip_address);


--
-- Name: ix_log_auditoria_sucesso; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_log_auditoria_sucesso ON public.log_auditoria USING btree (sucesso);


--
-- Name: ix_log_auditoria_timestamp; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_log_auditoria_timestamp ON public.log_auditoria USING btree ("timestamp");


--
-- Name: ix_log_auditoria_usuario_id; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_log_auditoria_usuario_id ON public.log_auditoria USING btree (usuario_id);


--
-- Name: ix_movimentacao_caixa_corretora_destino_id; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_movimentacao_caixa_corretora_destino_id ON public.movimentacao_caixa USING btree (corretora_destino_id);


--
-- Name: ix_movimentacao_caixa_corretora_id; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_movimentacao_caixa_corretora_id ON public.movimentacao_caixa USING btree (corretora_id);


--
-- Name: ix_movimentacao_caixa_data_movimentacao; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_movimentacao_caixa_data_movimentacao ON public.movimentacao_caixa USING btree (data_movimentacao);


--
-- Name: ix_movimentacao_caixa_moeda; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_movimentacao_caixa_moeda ON public.movimentacao_caixa USING btree (moeda);


--
-- Name: ix_movimentacao_caixa_provento_id; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_movimentacao_caixa_provento_id ON public.movimentacao_caixa USING btree (provento_id);


--
-- Name: ix_movimentacao_caixa_tipo_movimentacao; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_movimentacao_caixa_tipo_movimentacao ON public.movimentacao_caixa USING btree (tipo_movimentacao);


--
-- Name: ix_movimentacao_caixa_usuario_id; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_movimentacao_caixa_usuario_id ON public.movimentacao_caixa USING btree (usuario_id);


--
-- Name: ix_parametros_macro_ativo; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_parametros_macro_ativo ON public.parametros_macro USING btree (ativo);


--
-- Name: ix_parametros_macro_mercado; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_parametros_macro_mercado ON public.parametros_macro USING btree (mercado);


--
-- Name: ix_parametros_macro_pais; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_parametros_macro_pais ON public.parametros_macro USING btree (pais);


--
-- Name: ix_parametros_macro_pais_mercado; Type: INDEX; Schema: public; Owner: exitus
--

CREATE UNIQUE INDEX ix_parametros_macro_pais_mercado ON public.parametros_macro USING btree (pais, mercado);


--
-- Name: ix_portfolio_ativo; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_portfolio_ativo ON public.portfolio USING btree (ativo);


--
-- Name: ix_portfolio_usuario_id; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_portfolio_usuario_id ON public.portfolio USING btree (usuario_id);


--
-- Name: ix_posicao_ativo_id; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_posicao_ativo_id ON public.posicao USING btree (ativo_id);


--
-- Name: ix_posicao_corretora_id; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_posicao_corretora_id ON public.posicao USING btree (corretora_id);


--
-- Name: ix_posicao_data_primeira_compra; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_posicao_data_primeira_compra ON public.posicao USING btree (data_primeira_compra);


--
-- Name: ix_posicao_data_ultima_atualizacao; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_posicao_data_ultima_atualizacao ON public.posicao USING btree (data_ultima_atualizacao);


--
-- Name: ix_posicao_usuario_id; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_posicao_usuario_id ON public.posicao USING btree (usuario_id);


--
-- Name: ix_projecoes_renda_mes_ano; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_projecoes_renda_mes_ano ON public.projecoes_renda USING btree (mes_ano);


--
-- Name: ix_projecoes_renda_usuario_id; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_projecoes_renda_usuario_id ON public.projecoes_renda USING btree (usuario_id);


--
-- Name: ix_provento_ativo_id; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_provento_ativo_id ON public.provento USING btree (ativo_id);


--
-- Name: ix_provento_data_com; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_provento_data_com ON public.provento USING btree (data_com);


--
-- Name: ix_provento_data_pagamento; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_provento_data_pagamento ON public.provento USING btree (data_pagamento);


--
-- Name: ix_provento_tipo_provento; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_provento_tipo_provento ON public.provento USING btree (tipo_provento);


--
-- Name: ix_regra_fiscal_ativa; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_regra_fiscal_ativa ON public.regra_fiscal USING btree (ativa);


--
-- Name: ix_regra_fiscal_incide_sobre; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_regra_fiscal_incide_sobre ON public.regra_fiscal USING btree (incide_sobre);


--
-- Name: ix_regra_fiscal_pais; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_regra_fiscal_pais ON public.regra_fiscal USING btree (pais);


--
-- Name: ix_regra_fiscal_tipo_ativo; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_regra_fiscal_tipo_ativo ON public.regra_fiscal USING btree (tipo_ativo);


--
-- Name: ix_regra_fiscal_tipo_operacao; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_regra_fiscal_tipo_operacao ON public.regra_fiscal USING btree (tipo_operacao);


--
-- Name: ix_regra_fiscal_vigencia_fim; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_regra_fiscal_vigencia_fim ON public.regra_fiscal USING btree (vigencia_fim);


--
-- Name: ix_regra_fiscal_vigencia_inicio; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_regra_fiscal_vigencia_inicio ON public.regra_fiscal USING btree (vigencia_inicio);


--
-- Name: ix_relatorios_performance_usuario_id; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_relatorios_performance_usuario_id ON public.relatorios_performance USING btree (usuario_id);


--
-- Name: ix_usuario_email; Type: INDEX; Schema: public; Owner: exitus
--

CREATE UNIQUE INDEX ix_usuario_email ON public.usuario USING btree (email);


--
-- Name: ix_usuario_username; Type: INDEX; Schema: public; Owner: exitus
--

CREATE UNIQUE INDEX ix_usuario_username ON public.usuario USING btree (username);


--
-- Name: alertas alertas_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.alertas
    ADD CONSTRAINT alertas_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuario(id) ON DELETE CASCADE;


--
-- Name: auditoria_relatorios auditoria_relatorios_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.auditoria_relatorios
    ADD CONSTRAINT auditoria_relatorios_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuario(id) ON DELETE CASCADE;


--
-- Name: configuracoes_alertas configuracoes_alertas_ativo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.configuracoes_alertas
    ADD CONSTRAINT configuracoes_alertas_ativo_id_fkey FOREIGN KEY (ativo_id) REFERENCES public.ativo(id) ON DELETE CASCADE;


--
-- Name: configuracoes_alertas configuracoes_alertas_portfolio_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.configuracoes_alertas
    ADD CONSTRAINT configuracoes_alertas_portfolio_id_fkey FOREIGN KEY (portfolio_id) REFERENCES public.portfolio(id) ON DELETE CASCADE;


--
-- Name: configuracoes_alertas configuracoes_alertas_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.configuracoes_alertas
    ADD CONSTRAINT configuracoes_alertas_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuario(id) ON DELETE CASCADE;


--
-- Name: corretora corretora_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.corretora
    ADD CONSTRAINT corretora_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuario(id) ON DELETE CASCADE;


--
-- Name: evento_corporativo evento_corporativo_ativo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.evento_corporativo
    ADD CONSTRAINT evento_corporativo_ativo_id_fkey FOREIGN KEY (ativo_id) REFERENCES public.ativo(id) ON DELETE RESTRICT;


--
-- Name: evento_corporativo evento_corporativo_ativo_novo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.evento_corporativo
    ADD CONSTRAINT evento_corporativo_ativo_novo_id_fkey FOREIGN KEY (ativo_novo_id) REFERENCES public.ativo(id) ON DELETE SET NULL;


--
-- Name: historico_preco historico_preco_ativoid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.historico_preco
    ADD CONSTRAINT historico_preco_ativoid_fkey FOREIGN KEY (ativoid) REFERENCES public.ativo(id) ON DELETE CASCADE;


--
-- Name: log_auditoria log_auditoria_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.log_auditoria
    ADD CONSTRAINT log_auditoria_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuario(id) ON DELETE SET NULL;


--
-- Name: movimentacao_caixa movimentacao_caixa_corretora_destino_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.movimentacao_caixa
    ADD CONSTRAINT movimentacao_caixa_corretora_destino_id_fkey FOREIGN KEY (corretora_destino_id) REFERENCES public.corretora(id) ON DELETE SET NULL;


--
-- Name: movimentacao_caixa movimentacao_caixa_corretora_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.movimentacao_caixa
    ADD CONSTRAINT movimentacao_caixa_corretora_id_fkey FOREIGN KEY (corretora_id) REFERENCES public.corretora(id) ON DELETE CASCADE;


--
-- Name: movimentacao_caixa movimentacao_caixa_provento_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.movimentacao_caixa
    ADD CONSTRAINT movimentacao_caixa_provento_id_fkey FOREIGN KEY (provento_id) REFERENCES public.provento(id) ON DELETE SET NULL;


--
-- Name: movimentacao_caixa movimentacao_caixa_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.movimentacao_caixa
    ADD CONSTRAINT movimentacao_caixa_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuario(id) ON DELETE CASCADE;


--
-- Name: portfolio portfolio_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.portfolio
    ADD CONSTRAINT portfolio_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuario(id) ON DELETE CASCADE;


--
-- Name: posicao posicao_ativo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.posicao
    ADD CONSTRAINT posicao_ativo_id_fkey FOREIGN KEY (ativo_id) REFERENCES public.ativo(id) ON DELETE RESTRICT;


--
-- Name: posicao posicao_corretora_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.posicao
    ADD CONSTRAINT posicao_corretora_id_fkey FOREIGN KEY (corretora_id) REFERENCES public.corretora(id) ON DELETE CASCADE;


--
-- Name: posicao posicao_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.posicao
    ADD CONSTRAINT posicao_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuario(id) ON DELETE CASCADE;


--
-- Name: projecoes_renda projecoes_renda_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.projecoes_renda
    ADD CONSTRAINT projecoes_renda_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuario(id);


--
-- Name: provento provento_ativo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.provento
    ADD CONSTRAINT provento_ativo_id_fkey FOREIGN KEY (ativo_id) REFERENCES public.ativo(id) ON DELETE RESTRICT;


--
-- Name: relatorios_performance relatorios_performance_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.relatorios_performance
    ADD CONSTRAINT relatorios_performance_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuario(id);


--
-- Name: transacao transacao_ativo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.transacao
    ADD CONSTRAINT transacao_ativo_id_fkey FOREIGN KEY (ativo_id) REFERENCES public.ativo(id);


--
-- Name: transacao transacao_corretora_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.transacao
    ADD CONSTRAINT transacao_corretora_id_fkey FOREIGN KEY (corretora_id) REFERENCES public.corretora(id);


--
-- Name: transacao transacao_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.transacao
    ADD CONSTRAINT transacao_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuario(id);


--
-- PostgreSQL database dump complete
--

\unrestrict YnvsWSHL3LVi5oKitdQsVovqeAlTbWZqRV5mX5tgxK2hBWKWEOIwWEAkpsDqw0i

