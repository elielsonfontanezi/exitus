--
-- PostgreSQL database dump
--

\restrict uMUXmGwGK02AP5YMODBHaCONJwJGYsr5weuel1YFRUVw08BR3RyoqH4uID61Coa

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

SET default_tablespace = '';

SET default_table_access_method = heap;

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
-- Name: ativo ativo_pkey; Type: CONSTRAINT; Schema: public; Owner: exitus
--

ALTER TABLE ONLY public.ativo
    ADD CONSTRAINT ativo_pkey PRIMARY KEY (id);


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
-- PostgreSQL database dump complete
--

\unrestrict uMUXmGwGK02AP5YMODBHaCONJwJGYsr5weuel1YFRUVw08BR3RyoqH4uID61Coa

