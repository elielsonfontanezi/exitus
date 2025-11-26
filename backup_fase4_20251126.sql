--
-- PostgreSQL database dump
--

\restrict GKPkJ0HUazHhGWoZucB0W175i385M8gluav75q4QDk791AqK2yfWUeOUdV3G2s9

-- Dumped from database version 15.15 (Debian 15.15-1.pgdg13+1)
-- Dumped by pg_dump version 15.15 (Debian 15.15-1.pgdg13+1)

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
    CONSTRAINT ativo_nome_min_length CHECK ((length((nome)::text) >= 2)),
    CONSTRAINT ativo_preco_positivo CHECK (((preco_atual IS NULL) OR (preco_atual >= (0)::numeric))),
    CONSTRAINT ativo_ticker_min_length CHECK ((length((ticker)::text) >= 1))
);


ALTER TABLE public.ativo OWNER TO exitus;

--
-- Name: TABLE ativo; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON TABLE public.ativo IS 'Tabela de ativos financeiros (ações, FIIs, REITs, bonds, criptomoedas)';


--
-- Name: COLUMN ativo.id; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.ativo.id IS 'Identificador único do ativo';


--
-- Name: COLUMN ativo.ticker; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.ativo.ticker IS 'Código/símbolo do ativo (ex: PETR4, AAPL, BTC)';


--
-- Name: COLUMN ativo.nome; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.ativo.nome IS 'Nome completo do ativo';


--
-- Name: COLUMN ativo.tipo; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.ativo.tipo IS 'Tipo do ativo (ação, FII, REIT, bond, cripto)';


--
-- Name: COLUMN ativo.classe; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.ativo.classe IS 'Classe do ativo (renda variável, fixa, cripto)';


--
-- Name: COLUMN ativo.mercado; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.ativo.mercado IS 'Mercado/país de negociação (BR, US, EUR)';


--
-- Name: COLUMN ativo.moeda; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.ativo.moeda IS 'Moeda de negociação (BRL, USD, EUR)';


--
-- Name: COLUMN ativo.preco_atual; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.ativo.preco_atual IS 'Preço/cotação atual do ativo';


--
-- Name: COLUMN ativo.data_ultima_cotacao; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.ativo.data_ultima_cotacao IS 'Data e hora da última cotação';


--
-- Name: COLUMN ativo.dividend_yield; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.ativo.dividend_yield IS 'Dividend Yield em % (ex: 6.5000 = 6.5%)';


--
-- Name: COLUMN ativo.p_l; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.ativo.p_l IS 'Índice Preço/Lucro';


--
-- Name: COLUMN ativo.p_vp; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.ativo.p_vp IS 'Índice Preço/Valor Patrimonial';


--
-- Name: COLUMN ativo.roe; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.ativo.roe IS 'Return on Equity em %';


--
-- Name: COLUMN ativo.ativo; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.ativo.ativo IS 'Indica se ativo está disponível para negociação';


--
-- Name: COLUMN ativo.deslistado; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.ativo.deslistado IS 'Indica se ativo foi deslistado da bolsa';


--
-- Name: COLUMN ativo.data_deslistagem; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.ativo.data_deslistagem IS 'Data de deslistagem (se aplicável)';


--
-- Name: COLUMN ativo.observacoes; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.ativo.observacoes IS 'Observações e notas sobre o ativo';


--
-- Name: COLUMN ativo.created_at; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.ativo.created_at IS 'Data de criação do registro';


--
-- Name: COLUMN ativo.updated_at; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.ativo.updated_at IS 'Data da última atualização';


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
-- Name: TABLE corretora; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON TABLE public.corretora IS 'Tabela de corretoras e contas de investimento';


--
-- Name: COLUMN corretora.id; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.corretora.id IS 'Identificador único da corretora';


--
-- Name: COLUMN corretora.usuario_id; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.corretora.usuario_id IS 'ID do usuário proprietário';


--
-- Name: COLUMN corretora.nome; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.corretora.nome IS 'Nome da corretora/exchange (ex: XP, Clear, Binance)';


--
-- Name: COLUMN corretora.tipo; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.corretora.tipo IS 'Tipo: corretora tradicional ou exchange cripto';


--
-- Name: COLUMN corretora.pais; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.corretora.pais IS 'Código ISO 3166-1 alpha-2 do país (BR, US, etc.)';


--
-- Name: COLUMN corretora.moeda_padrao; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.corretora.moeda_padrao IS 'Código ISO 4217 da moeda (BRL, USD, EUR)';


--
-- Name: COLUMN corretora.saldo_atual; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.corretora.saldo_atual IS 'Saldo disponível em caixa (na moeda padrão)';


--
-- Name: COLUMN corretora.ativa; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.corretora.ativa IS 'Indica se conta está ativa';


--
-- Name: COLUMN corretora.observacoes; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.corretora.observacoes IS 'Observações e notas do usuário sobre a conta';


--
-- Name: COLUMN corretora.created_at; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.corretora.created_at IS 'Data de criação do registro';


--
-- Name: COLUMN corretora.updated_at; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.corretora.updated_at IS 'Data da última atualização';


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
-- Name: transacao; Type: TABLE; Schema: public; Owner: exitus
--

CREATE TABLE public.transacao (
    id uuid NOT NULL,
    usuario_id uuid NOT NULL,
    corretora_id uuid NOT NULL,
    ativo_id uuid NOT NULL,
    tipo_operacao public.tipooperacao NOT NULL,
    quantidade numeric(18,8) NOT NULL,
    preco_unitario numeric(18,6) NOT NULL,
    valor_total numeric(18,2) NOT NULL,
    taxas numeric(18,2) NOT NULL,
    impostos numeric(18,2) NOT NULL,
    data_operacao date NOT NULL,
    data_liquidacao date,
    observacoes text,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    CONSTRAINT transacao_data_liquidacao_valida CHECK (((data_liquidacao IS NULL) OR (data_liquidacao >= data_operacao))),
    CONSTRAINT transacao_impostos_positivos CHECK ((impostos >= (0)::numeric)),
    CONSTRAINT transacao_preco_positivo CHECK ((preco_unitario > (0)::numeric)),
    CONSTRAINT transacao_quantidade_positiva CHECK ((quantidade > (0)::numeric)),
    CONSTRAINT transacao_taxas_positivas CHECK ((taxas >= (0)::numeric)),
    CONSTRAINT transacao_valor_total_positivo CHECK ((valor_total > (0)::numeric))
);


ALTER TABLE public.transacao OWNER TO exitus;

--
-- Name: TABLE transacao; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON TABLE public.transacao IS 'Tabela de transações de compra e venda de ativos';


--
-- Name: COLUMN transacao.id; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.transacao.id IS 'Identificador único da transação';


--
-- Name: COLUMN transacao.usuario_id; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.transacao.usuario_id IS 'ID do usuário';


--
-- Name: COLUMN transacao.corretora_id; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.transacao.corretora_id IS 'ID da corretora';


--
-- Name: COLUMN transacao.ativo_id; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.transacao.ativo_id IS 'ID do ativo transacionado';


--
-- Name: COLUMN transacao.tipo_operacao; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.transacao.tipo_operacao IS 'Tipo de operação: COMPRA ou VENDA';


--
-- Name: COLUMN transacao.quantidade; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.transacao.quantidade IS 'Quantidade transacionada (suporta fracionários)';


--
-- Name: COLUMN transacao.preco_unitario; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.transacao.preco_unitario IS 'Preço por unidade';


--
-- Name: COLUMN transacao.valor_total; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.transacao.valor_total IS 'Valor total da operação (quantidade * preço)';


--
-- Name: COLUMN transacao.taxas; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.transacao.taxas IS 'Taxas de corretagem, custódia, emolumentos';


--
-- Name: COLUMN transacao.impostos; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.transacao.impostos IS 'IR retido na fonte, IOF, etc.';


--
-- Name: COLUMN transacao.data_operacao; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.transacao.data_operacao IS 'Data da operação';


--
-- Name: COLUMN transacao.data_liquidacao; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.transacao.data_liquidacao IS 'Data de liquidação (D+2, D+3, etc.)';


--
-- Name: COLUMN transacao.observacoes; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.transacao.observacoes IS 'Observações sobre a transação';


--
-- Name: COLUMN transacao.created_at; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.transacao.created_at IS 'Data de criação do registro';


--
-- Name: COLUMN transacao.updated_at; Type: COMMENT; Schema: public; Owner: exitus
--

COMMENT ON COLUMN public.transacao.updated_at IS 'Data da última atualização';


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
b2542b2f7857
\.


--
-- Data for Name: ativo; Type: TABLE DATA; Schema: public; Owner: exitus
--

COPY public.ativo (id, ticker, nome, tipo, classe, mercado, moeda, preco_atual, data_ultima_cotacao, dividend_yield, p_l, p_vp, roe, ativo, deslistado, data_deslistagem, observacoes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: corretora; Type: TABLE DATA; Schema: public; Owner: exitus
--

COPY public.corretora (id, usuario_id, nome, tipo, pais, moeda_padrao, saldo_atual, ativa, observacoes, created_at, updated_at) FROM stdin;
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
\.


--
-- Data for Name: fonte_dados; Type: TABLE DATA; Schema: public; Owner: exitus
--

COPY public.fonte_dados (id, nome, tipo_fonte, url_base, requer_autenticacao, rate_limit, ativa, prioridade, ultima_consulta, total_consultas, total_erros, observacoes, created_at, updated_at) FROM stdin;
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
\.


--
-- Data for Name: posicao; Type: TABLE DATA; Schema: public; Owner: exitus
--

COPY public.posicao (id, usuario_id, corretora_id, ativo_id, quantidade, preco_medio, custo_total, taxas_acumuladas, impostos_acumulados, valor_atual, lucro_prejuizo_realizado, lucro_prejuizo_nao_realizado, data_primeira_compra, data_ultima_atualizacao, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: provento; Type: TABLE DATA; Schema: public; Owner: exitus
--

COPY public.provento (id, ativo_id, tipo_provento, valor_por_acao, quantidade_ativos, valor_bruto, imposto_retido, valor_liquido, data_com, data_pagamento, observacoes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: regra_fiscal; Type: TABLE DATA; Schema: public; Owner: exitus
--

COPY public.regra_fiscal (id, pais, tipo_ativo, tipo_operacao, aliquota_ir, valor_isencao, incide_sobre, descricao, vigencia_inicio, vigencia_fim, ativa, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: transacao; Type: TABLE DATA; Schema: public; Owner: exitus
--

COPY public.transacao (id, usuario_id, corretora_id, ativo_id, tipo_operacao, quantidade, preco_unitario, valor_total, taxas, impostos, data_operacao, data_liquidacao, observacoes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: usuario; Type: TABLE DATA; Schema: public; Owner: exitus
--

COPY public.usuario (id, username, email, password_hash, nome_completo, ativo, role, created_at, updated_at) FROM stdin;
\.


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: ativo ativo_pkey; Type: CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.ativo
    ADD CONSTRAINT ativo_pkey PRIMARY KEY (id);


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
-- Name: posicao posicao_pkey; Type: CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.posicao
    ADD CONSTRAINT posicao_pkey PRIMARY KEY (id);


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
-- Name: transacao transacao_pkey; Type: CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.transacao
    ADD CONSTRAINT transacao_pkey PRIMARY KEY (id);


--
-- Name: ativo unique_ativo_ticker_mercado; Type: CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.ativo
    ADD CONSTRAINT unique_ativo_ticker_mercado UNIQUE (ticker, mercado);


--
-- Name: corretora unique_corretora_usuario_nome_pais; Type: CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.corretora
    ADD CONSTRAINT unique_corretora_usuario_nome_pais UNIQUE (usuario_id, nome, pais);


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
-- Name: usuario usuario_pkey; Type: CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_pkey PRIMARY KEY (id);


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
-- Name: ix_transacao_ativo_id; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_transacao_ativo_id ON public.transacao USING btree (ativo_id);


--
-- Name: ix_transacao_corretora_id; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_transacao_corretora_id ON public.transacao USING btree (corretora_id);


--
-- Name: ix_transacao_data_liquidacao; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_transacao_data_liquidacao ON public.transacao USING btree (data_liquidacao);


--
-- Name: ix_transacao_data_operacao; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_transacao_data_operacao ON public.transacao USING btree (data_operacao);


--
-- Name: ix_transacao_tipo_operacao; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_transacao_tipo_operacao ON public.transacao USING btree (tipo_operacao);


--
-- Name: ix_transacao_usuario_id; Type: INDEX; Schema: public; Owner: exitus
--

CREATE INDEX ix_transacao_usuario_id ON public.transacao USING btree (usuario_id);


--
-- Name: ix_usuario_email; Type: INDEX; Schema: public; Owner: exitus
--

CREATE UNIQUE INDEX ix_usuario_email ON public.usuario USING btree (email);


--
-- Name: ix_usuario_username; Type: INDEX; Schema: public; Owner: exitus
--

CREATE UNIQUE INDEX ix_usuario_username ON public.usuario USING btree (username);


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
-- Name: provento provento_ativo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.provento
    ADD CONSTRAINT provento_ativo_id_fkey FOREIGN KEY (ativo_id) REFERENCES public.ativo(id) ON DELETE RESTRICT;


--
-- Name: transacao transacao_ativo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.transacao
    ADD CONSTRAINT transacao_ativo_id_fkey FOREIGN KEY (ativo_id) REFERENCES public.ativo(id) ON DELETE RESTRICT;


--
-- Name: transacao transacao_corretora_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.transacao
    ADD CONSTRAINT transacao_corretora_id_fkey FOREIGN KEY (corretora_id) REFERENCES public.corretora(id) ON DELETE CASCADE;


--
-- Name: transacao transacao_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.transacao
    ADD CONSTRAINT transacao_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuario(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict GKPkJ0HUazHhGWoZucB0W175i385M8gluav75q4QDk791AqK2yfWUeOUdV3G2s9

