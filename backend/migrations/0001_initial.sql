--
-- PostgreSQL database dump
--


-- Dumped from database version 16.11
-- Dumped by pg_dump version 18.2

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
-- search_path reset removed to allow access to public schema
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;


-- Redundant yoyo metadata tables removed to avoid conflict with yoyo's auto-init

--
-- Name: agent_conversations; Type: TABLE; Schema: public; Owner: lynch
--

CREATE TABLE public.agent_conversations (
    id integer NOT NULL,
    user_id integer NOT NULL,
    title text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    last_message_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.agent_conversations OWNER TO lynch;

--
-- Name: agent_conversations_id_seq; Type: SEQUENCE; Schema: public; Owner: lynch
--

CREATE SEQUENCE public.agent_conversations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.agent_conversations_id_seq OWNER TO lynch;

--
-- Name: agent_conversations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lynch
--

ALTER SEQUENCE public.agent_conversations_id_seq OWNED BY public.agent_conversations.id;


--
-- Name: agent_messages; Type: TABLE; Schema: public; Owner: lynch
--

CREATE TABLE public.agent_messages (
    id integer NOT NULL,
    conversation_id integer NOT NULL,
    role text NOT NULL,
    content text NOT NULL,
    tool_calls jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT agent_messages_role_check CHECK ((role = ANY (ARRAY['user'::text, 'assistant'::text])))
);


ALTER TABLE public.agent_messages OWNER TO lynch;

--
-- Name: agent_messages_id_seq; Type: SEQUENCE; Schema: public; Owner: lynch
--

CREATE SEQUENCE public.agent_messages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.agent_messages_id_seq OWNER TO lynch;

--
-- Name: agent_messages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lynch
--

ALTER SEQUENCE public.agent_messages_id_seq OWNED BY public.agent_messages.id;


--
-- Name: alerts; Type: TABLE; Schema: public; Owner: lynch
--

CREATE TABLE public.alerts (
    id integer NOT NULL,
    user_id integer,
    symbol text,
    condition_type text NOT NULL,
    condition_params jsonb NOT NULL,
    frequency text DEFAULT 'daily'::text,
    status text DEFAULT 'active'::text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    last_checked timestamp without time zone,
    triggered_at timestamp without time zone,
    message text,
    condition_description text,
    action_type text,
    action_payload jsonb,
    portfolio_id integer,
    action_note text
);


ALTER TABLE public.alerts OWNER TO lynch;

--
-- Name: alerts_id_seq; Type: SEQUENCE; Schema: public; Owner: lynch
--

CREATE SEQUENCE public.alerts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.alerts_id_seq OWNER TO lynch;

--
-- Name: alerts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lynch
--

ALTER SEQUENCE public.alerts_id_seq OWNED BY public.alerts.id;


--
-- Name: algorithm_configurations; Type: TABLE; Schema: public; Owner: lynch
--

CREATE TABLE public.algorithm_configurations (
    id integer NOT NULL,
    user_id integer,
    name text,
    weight_peg real,
    weight_consistency real,
    weight_debt real,
    weight_ownership real,
    weight_roe real,
    weight_debt_to_earnings real,
    peg_excellent real DEFAULT 1.0,
    peg_good real DEFAULT 1.5,
    peg_fair real DEFAULT 2.0,
    debt_excellent real DEFAULT 0.5,
    debt_good real DEFAULT 1.0,
    debt_moderate real DEFAULT 2.0,
    inst_own_min real DEFAULT 0.20,
    inst_own_max real DEFAULT 0.60,
    revenue_growth_excellent real DEFAULT 15.0,
    revenue_growth_good real DEFAULT 10.0,
    revenue_growth_fair real DEFAULT 5.0,
    income_growth_excellent real DEFAULT 15.0,
    income_growth_good real DEFAULT 10.0,
    income_growth_fair real DEFAULT 5.0,
    roe_excellent real DEFAULT 20.0,
    roe_good real DEFAULT 15.0,
    roe_fair real DEFAULT 10.0,
    debt_to_earnings_excellent real DEFAULT 3.0,
    debt_to_earnings_good real DEFAULT 5.0,
    debt_to_earnings_fair real DEFAULT 8.0,
    correlation_5yr real,
    correlation_10yr real,
    is_active boolean DEFAULT false,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    "character" text DEFAULT 'lynch'::text,
    gross_margin_excellent real DEFAULT 50.0,
    gross_margin_good real DEFAULT 40.0,
    gross_margin_fair real DEFAULT 30.0,
    weight_gross_margin real DEFAULT 0.0
);


ALTER TABLE public.algorithm_configurations OWNER TO lynch;

--
-- Name: algorithm_configurations_id_seq; Type: SEQUENCE; Schema: public; Owner: lynch
--

CREATE SEQUENCE public.algorithm_configurations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.algorithm_configurations_id_seq OWNER TO lynch;

--
-- Name: algorithm_configurations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lynch
--

ALTER SEQUENCE public.algorithm_configurations_id_seq OWNED BY public.algorithm_configurations.id;


--
-- Name: analysis_generation_status; Type: TABLE; Schema: public; Owner: lynch
--

CREATE TABLE public.analysis_generation_status (
    user_id integer NOT NULL,
    symbol text NOT NULL,
    character_id text NOT NULL,
    thesis_status text,
    chart_status text,
    thesis_error text,
    chart_error text,
    started_at timestamp without time zone,
    thesis_completed_at timestamp without time zone,
    chart_completed_at timestamp without time zone
);


ALTER TABLE public.analysis_generation_status OWNER TO lynch;

--
-- Name: analyst_estimates; Type: TABLE; Schema: public; Owner: lynch
--

CREATE TABLE public.analyst_estimates (
    id integer NOT NULL,
    symbol text NOT NULL,
    period text NOT NULL,
    eps_avg real,
    eps_low real,
    eps_high real,
    eps_growth real,
    eps_year_ago real,
    eps_num_analysts integer,
    revenue_avg real,
    revenue_low real,
    revenue_high real,
    revenue_growth real,
    revenue_year_ago real,
    revenue_num_analysts integer,
    last_updated timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    period_end_date date,
    fiscal_quarter integer,
    fiscal_year integer
);


ALTER TABLE public.analyst_estimates OWNER TO lynch;

--
-- Name: analyst_estimates_id_seq; Type: SEQUENCE; Schema: public; Owner: lynch
--

CREATE SEQUENCE public.analyst_estimates_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.analyst_estimates_id_seq OWNER TO lynch;

--
-- Name: analyst_estimates_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lynch
--

ALTER SEQUENCE public.analyst_estimates_id_seq OWNED BY public.analyst_estimates.id;


--
-- Name: analyst_recommendations; Type: TABLE; Schema: public; Owner: lynch
--

CREATE TABLE public.analyst_recommendations (
    id integer NOT NULL,
    symbol text NOT NULL,
    period_month text NOT NULL,
    strong_buy integer,
    buy integer,
    hold integer,
    sell integer,
    strong_sell integer,
    last_updated timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.analyst_recommendations OWNER TO lynch;

--
-- Name: analyst_recommendations_id_seq; Type: SEQUENCE; Schema: public; Owner: lynch
--

CREATE SEQUENCE public.analyst_recommendations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.analyst_recommendations_id_seq OWNER TO lynch;

--
-- Name: analyst_recommendations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lynch
--

ALTER SEQUENCE public.analyst_recommendations_id_seq OWNED BY public.analyst_recommendations.id;


--
-- Name: app_feedback; Type: TABLE; Schema: public; Owner: lynch
--

CREATE TABLE public.app_feedback (
    id integer NOT NULL,
    user_id integer,
    email text,
    feedback_text text,
    screenshot_data text,
    page_url text,
    metadata jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    status text DEFAULT 'new'::text
);


ALTER TABLE public.app_feedback OWNER TO lynch;

--
-- Name: app_feedback_id_seq; Type: SEQUENCE; Schema: public; Owner: lynch
--

CREATE SEQUENCE public.app_feedback_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.app_feedback_id_seq OWNER TO lynch;

--
-- Name: app_feedback_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lynch
--

ALTER SEQUENCE public.app_feedback_id_seq OWNED BY public.app_feedback.id;


--
-- Name: app_settings; Type: TABLE; Schema: public; Owner: lynch
--

CREATE TABLE public.app_settings (
    key text NOT NULL,
    value jsonb,
    description text
);


ALTER TABLE public.app_settings OWNER TO lynch;

--
-- Name: background_jobs; Type: TABLE; Schema: public; Owner: lynch
--

CREATE TABLE public.background_jobs (
    id integer NOT NULL,
    job_type text NOT NULL,
    status text DEFAULT 'pending'::text NOT NULL,
    claimed_by text,
    claimed_at timestamp without time zone,
    claim_expires_at timestamp without time zone,
    params jsonb DEFAULT '{}'::jsonb NOT NULL,
    progress_pct integer DEFAULT 0,
    progress_message text,
    processed_count integer DEFAULT 0,
    total_count integer DEFAULT 0,
    result jsonb,
    error_message text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    started_at timestamp without time zone,
    completed_at timestamp without time zone,
    tier text DEFAULT 'light'::text,
    logs jsonb DEFAULT '[]'::jsonb
);


ALTER TABLE public.background_jobs OWNER TO lynch;

--
-- Name: background_jobs_id_seq; Type: SEQUENCE; Schema: public; Owner: lynch
--

CREATE SEQUENCE public.background_jobs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.background_jobs_id_seq OWNER TO lynch;

--
-- Name: background_jobs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lynch
--

ALTER SEQUENCE public.background_jobs_id_seq OWNED BY public.background_jobs.id;


--
-- Name: backtest_results; Type: TABLE; Schema: public; Owner: lynch
--

CREATE TABLE public.backtest_results (
    id integer NOT NULL,
    symbol text,
    backtest_date date,
    years_back integer,
    start_price real,
    end_price real,
    total_return real,
    historical_score real,
    historical_rating text,
    peg_score real,
    debt_score real,
    ownership_score real,
    consistency_score real,
    peg_ratio real,
    earnings_cagr real,
    revenue_cagr real,
    debt_to_equity real,
    institutional_ownership real,
    roe real,
    debt_to_earnings real,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    gross_margin real
);


ALTER TABLE public.backtest_results OWNER TO lynch;

--
-- Name: backtest_results_id_seq; Type: SEQUENCE; Schema: public; Owner: lynch
--

CREATE SEQUENCE public.backtest_results_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.backtest_results_id_seq OWNER TO lynch;

--
-- Name: backtest_results_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lynch
--

ALTER SEQUENCE public.backtest_results_id_seq OWNED BY public.backtest_results.id;


--
-- Name: benchmark_snapshots; Type: TABLE; Schema: public; Owner: lynch
--

CREATE TABLE public.benchmark_snapshots (
    id integer NOT NULL,
    snapshot_date date NOT NULL,
    spy_price real NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.benchmark_snapshots OWNER TO lynch;

--
-- Name: benchmark_snapshots_id_seq; Type: SEQUENCE; Schema: public; Owner: lynch
--

CREATE SEQUENCE public.benchmark_snapshots_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.benchmark_snapshots_id_seq OWNER TO lynch;

--
-- Name: benchmark_snapshots_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lynch
--

ALTER SEQUENCE public.benchmark_snapshots_id_seq OWNED BY public.benchmark_snapshots.id;


--
-- Name: cache_checks; Type: TABLE; Schema: public; Owner: lynch
--

CREATE TABLE public.cache_checks (
    symbol text NOT NULL,
    cache_type text NOT NULL,
    last_checked date NOT NULL,
    last_data_date date
);


ALTER TABLE public.cache_checks OWNER TO lynch;

--
-- Name: chart_analyses; Type: TABLE; Schema: public; Owner: lynch
--

CREATE TABLE public.chart_analyses (
    symbol text NOT NULL,
    section text NOT NULL,
    analysis_text text,
    generated_at timestamp without time zone,
    model_version text,
    user_id integer NOT NULL,
    id integer NOT NULL,
    character_id text DEFAULT 'lynch'::text NOT NULL
);


ALTER TABLE public.chart_analyses OWNER TO lynch;

--
-- Name: chart_analyses_id_seq; Type: SEQUENCE; Schema: public; Owner: lynch
--

CREATE SEQUENCE public.chart_analyses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.chart_analyses_id_seq OWNER TO lynch;

--
-- Name: chart_analyses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lynch
--

ALTER SEQUENCE public.chart_analyses_id_seq OWNED BY public.chart_analyses.id;


--
-- Name: company_facts; Type: TABLE; Schema: public; Owner: lynch
--

CREATE TABLE public.company_facts (
    cik text NOT NULL,
    entity_name text,
    ticker text,
    facts jsonb NOT NULL,
    last_updated timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.company_facts OWNER TO lynch;

--
-- Name: dcf_recommendations; Type: TABLE; Schema: public; Owner: lynch
--

CREATE TABLE public.dcf_recommendations (
    id integer NOT NULL,
    user_id integer NOT NULL,
    symbol text NOT NULL,
    recommendations_json text NOT NULL,
    generated_at timestamp without time zone,
    model_version text
);


ALTER TABLE public.dcf_recommendations OWNER TO lynch;

--
-- Name: dcf_recommendations_id_seq; Type: SEQUENCE; Schema: public; Owner: lynch
--

CREATE SEQUENCE public.dcf_recommendations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.dcf_recommendations_id_seq OWNER TO lynch;

--
-- Name: dcf_recommendations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lynch
--

ALTER SEQUENCE public.dcf_recommendations_id_seq OWNED BY public.dcf_recommendations.id;


--
-- Name: deliberations; Type: TABLE; Schema: public; Owner: lynch
--

CREATE TABLE public.deliberations (
    user_id integer NOT NULL,
    symbol text NOT NULL,
    deliberation_text text NOT NULL,
    final_verdict text,
    generated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    model_version text,
    CONSTRAINT deliberations_final_verdict_check CHECK ((final_verdict = ANY (ARRAY['BUY'::text, 'WATCH'::text, 'AVOID'::text])))
);


ALTER TABLE public.deliberations OWNER TO lynch;

--
-- Name: dividend_payouts; Type: TABLE; Schema: public; Owner: lynch
--

CREATE TABLE public.dividend_payouts (
    id integer NOT NULL,
    symbol text NOT NULL,
    amount real NOT NULL,
    payment_date date NOT NULL,
    ex_dividend_date date,
    last_updated timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.dividend_payouts OWNER TO lynch;

--
-- Name: dividend_payouts_id_seq; Type: SEQUENCE; Schema: public; Owner: lynch
--

CREATE SEQUENCE public.dividend_payouts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.dividend_payouts_id_seq OWNER TO lynch;

--
-- Name: dividend_payouts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lynch
--

ALTER SEQUENCE public.dividend_payouts_id_seq OWNED BY public.dividend_payouts.id;


--
-- Name: earnings_history; Type: TABLE; Schema: public; Owner: lynch
--

CREATE TABLE public.earnings_history (
    id integer NOT NULL,
    symbol text,
    year integer,
    earnings_per_share real,
    revenue real,
    fiscal_end text,
    debt_to_equity real,
    period text DEFAULT 'annual'::text,
    net_income real,
    dividend_amount real,
    operating_cash_flow real,
    capital_expenditures real,
    free_cash_flow real,
    last_updated timestamp without time zone,
    shareholder_equity real,
    shares_outstanding real,
    cash_and_cash_equivalents real,
    total_debt real
);


ALTER TABLE public.earnings_history OWNER TO lynch;

--
-- Name: earnings_history_id_seq; Type: SEQUENCE; Schema: public; Owner: lynch
--

CREATE SEQUENCE public.earnings_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.earnings_history_id_seq OWNER TO lynch;

--
-- Name: earnings_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lynch
--

ALTER SEQUENCE public.earnings_history_id_seq OWNED BY public.earnings_history.id;


--
-- Name: earnings_transcripts; Type: TABLE; Schema: public; Owner: lynch
--

CREATE TABLE public.earnings_transcripts (
    id integer NOT NULL,
    symbol text NOT NULL,
    quarter text NOT NULL,
    fiscal_year integer,
    earnings_date date,
    transcript_text text,
    summary text,
    has_qa boolean DEFAULT false,
    participants text[],
    source_url text,
    last_updated timestamp without time zone
);


ALTER TABLE public.earnings_transcripts OWNER TO lynch;

--
-- Name: earnings_transcripts_id_seq; Type: SEQUENCE; Schema: public; Owner: lynch
--

CREATE SEQUENCE public.earnings_transcripts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.earnings_transcripts_id_seq OWNER TO lynch;

--
-- Name: earnings_transcripts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lynch
--

ALTER SEQUENCE public.earnings_transcripts_id_seq OWNED BY public.earnings_transcripts.id;


--
-- Name: eps_revisions; Type: TABLE; Schema: public; Owner: lynch
--

CREATE TABLE public.eps_revisions (
    id integer NOT NULL,
    symbol text NOT NULL,
    period text NOT NULL,
    up_7d integer,
    up_30d integer,
    down_7d integer,
    down_30d integer,
    last_updated timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.eps_revisions OWNER TO lynch;

--
-- Name: eps_revisions_id_seq; Type: SEQUENCE; Schema: public; Owner: lynch
--

CREATE SEQUENCE public.eps_revisions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.eps_revisions_id_seq OWNER TO lynch;

--
-- Name: eps_revisions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lynch
--

ALTER SEQUENCE public.eps_revisions_id_seq OWNED BY public.eps_revisions.id;


--
-- Name: eps_trends; Type: TABLE; Schema: public; Owner: lynch
--

CREATE TABLE public.eps_trends (
    id integer NOT NULL,
    symbol text NOT NULL,
    period text NOT NULL,
    current_est real,
    days_7_ago real,
    days_30_ago real,
    days_60_ago real,
    days_90_ago real,
    last_updated timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.eps_trends OWNER TO lynch;

--
-- Name: eps_trends_id_seq; Type: SEQUENCE; Schema: public; Owner: lynch
--

CREATE SEQUENCE public.eps_trends_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.eps_trends_id_seq OWNER TO lynch;

--
-- Name: eps_trends_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lynch
--

ALTER SEQUENCE public.eps_trends_id_seq OWNED BY public.eps_trends.id;


--
-- Name: filing_section_summaries; Type: TABLE; Schema: public; Owner: lynch
--

CREATE TABLE public.filing_section_summaries (
    id integer NOT NULL,
    symbol text NOT NULL,
    section_name text NOT NULL,
    summary text NOT NULL,
    filing_type text NOT NULL,
    filing_date text,
    last_updated timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.filing_section_summaries OWNER TO lynch;

--
-- Name: filing_section_summaries_id_seq; Type: SEQUENCE; Schema: public; Owner: lynch
--

CREATE SEQUENCE public.filing_section_summaries_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.filing_section_summaries_id_seq OWNER TO lynch;

--
-- Name: filing_section_summaries_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lynch
--

ALTER SEQUENCE public.filing_section_summaries_id_seq OWNED BY public.filing_section_summaries.id;


--
-- Name: filing_sections; Type: TABLE; Schema: public; Owner: lynch
--

CREATE TABLE public.filing_sections (
    id integer NOT NULL,
    symbol text,
    section_name text,
    content text,
    filing_type text,
    filing_date text,
    last_updated timestamp without time zone
);


ALTER TABLE public.filing_sections OWNER TO lynch;

--
-- Name: filing_sections_id_seq; Type: SEQUENCE; Schema: public; Owner: lynch
--

CREATE SEQUENCE public.filing_sections_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.filing_sections_id_seq OWNER TO lynch;

--
-- Name: filing_sections_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lynch
--

ALTER SEQUENCE public.filing_sections_id_seq OWNED BY public.filing_sections.id;


--
-- Name: fred_data_cache; Type: TABLE; Schema: public; Owner: lynch
--

CREATE TABLE public.fred_data_cache (
    cache_key text NOT NULL,
    cache_value jsonb NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    expires_at timestamp with time zone
);


ALTER TABLE public.fred_data_cache OWNER TO lynch;

--
-- Name: growth_estimates; Type: TABLE; Schema: public; Owner: lynch
--

CREATE TABLE public.growth_estimates (
    id integer NOT NULL,
    symbol text NOT NULL,
    period text NOT NULL,
    stock_trend real,
    index_trend real,
    last_updated timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.growth_estimates OWNER TO lynch;

--
-- Name: growth_estimates_id_seq; Type: SEQUENCE; Schema: public; Owner: lynch
--

CREATE SEQUENCE public.growth_estimates_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.growth_estimates_id_seq OWNER TO lynch;

--
-- Name: growth_estimates_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lynch
--

ALTER SEQUENCE public.growth_estimates_id_seq OWNED BY public.growth_estimates.id;


--
-- Name: insider_trades; Type: TABLE; Schema: public; Owner: lynch
--

CREATE TABLE public.insider_trades (
    id integer NOT NULL,
    symbol text,
    name text,
    "position" text,
    transaction_date date,
    transaction_type text,
    shares real,
    value real,
    filing_url text,
    transaction_code text,
    is_10b51_plan boolean DEFAULT false,
    direct_indirect text DEFAULT 'D'::text,
    transaction_type_label text,
    price_per_share real,
    is_derivative boolean DEFAULT false,
    accession_number text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    footnotes text[],
    shares_owned_after real,
    ownership_change_pct real
);


ALTER TABLE public.insider_trades OWNER TO lynch;

--
-- Name: insider_trades_id_seq; Type: SEQUENCE; Schema: public; Owner: lynch
--

CREATE SEQUENCE public.insider_trades_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.insider_trades_id_seq OWNER TO lynch;

--
-- Name: insider_trades_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lynch
--

ALTER SEQUENCE public.insider_trades_id_seq OWNED BY public.insider_trades.id;


--
-- Name: investment_strategies; Type: TABLE; Schema: public; Owner: lynch
--

CREATE TABLE public.investment_strategies (
    id integer NOT NULL,
    user_id integer NOT NULL,
    portfolio_id integer NOT NULL,
    name text NOT NULL,
    description text,
    conditions jsonb NOT NULL,
    consensus_mode text DEFAULT 'both_agree'::text NOT NULL,
    consensus_threshold real DEFAULT 70.0,
    position_sizing jsonb DEFAULT '{"method": "equal_weight", "max_position_pct": 5.0}'::jsonb NOT NULL,
    exit_conditions jsonb DEFAULT '{}'::jsonb,
    schedule_cron text DEFAULT '0 9 * * 1-5'::text,
    enabled boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT investment_strategies_consensus_mode_check CHECK ((consensus_mode = ANY (ARRAY['both_agree'::text, 'weighted_confidence'::text, 'veto_power'::text])))
);


ALTER TABLE public.investment_strategies OWNER TO lynch;

--
-- Name: investment_strategies_id_seq; Type: SEQUENCE; Schema: public; Owner: lynch
--

CREATE SEQUENCE public.investment_strategies_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.investment_strategies_id_seq OWNER TO lynch;

--
-- Name: investment_strategies_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lynch
--

ALTER SEQUENCE public.investment_strategies_id_seq OWNED BY public.investment_strategies.id;


--
-- Name: lynch_analyses; Type: TABLE; Schema: public; Owner: lynch
--

CREATE TABLE public.lynch_analyses (
    symbol text NOT NULL,
    analysis_text text,
    generated_at timestamp without time zone,
    model_version text,
    user_id integer NOT NULL,
    id integer NOT NULL,
    character_id text DEFAULT 'lynch'::text NOT NULL
);


ALTER TABLE public.lynch_analyses OWNER TO lynch;

--
-- Name: lynch_analyses_id_seq; Type: SEQUENCE; Schema: public; Owner: lynch
--

CREATE SEQUENCE public.lynch_analyses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.lynch_analyses_id_seq OWNER TO lynch;

--
-- Name: lynch_analyses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lynch
--

ALTER SEQUENCE public.lynch_analyses_id_seq OWNED BY public.lynch_analyses.id;


--
-- Name: material_event_summaries; Type: TABLE; Schema: public; Owner: lynch
--

CREATE TABLE public.material_event_summaries (
    id integer NOT NULL,
    event_id integer NOT NULL,
    summary text NOT NULL,
    model_version text,
    generated_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.material_event_summaries OWNER TO lynch;

--
-- Name: material_event_summaries_id_seq; Type: SEQUENCE; Schema: public; Owner: lynch
--

CREATE SEQUENCE public.material_event_summaries_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.material_event_summaries_id_seq OWNER TO lynch;

--
-- Name: material_event_summaries_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lynch
--

ALTER SEQUENCE public.material_event_summaries_id_seq OWNED BY public.material_event_summaries.id;


--
-- Name: material_events; Type: TABLE; Schema: public; Owner: lynch
--

CREATE TABLE public.material_events (
    id integer NOT NULL,
    symbol text NOT NULL,
    event_type text NOT NULL,
    headline text NOT NULL,
    description text,
    source text DEFAULT 'SEC'::text NOT NULL,
    url text,
    filing_date date,
    datetime integer,
    published_date timestamp without time zone,
    sec_accession_number text,
    sec_item_codes text[],
    content_text text,
    last_updated timestamp without time zone
);


ALTER TABLE public.material_events OWNER TO lynch;

--
-- Name: material_events_id_seq; Type: SEQUENCE; Schema: public; Owner: lynch
--

CREATE SEQUENCE public.material_events_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.material_events_id_seq OWNER TO lynch;

--
-- Name: material_events_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lynch
--

ALTER SEQUENCE public.material_events_id_seq OWNED BY public.material_events.id;


--
-- Name: news_articles; Type: TABLE; Schema: public; Owner: lynch
--

CREATE TABLE public.news_articles (
    id integer NOT NULL,
    symbol text NOT NULL,
    finnhub_id integer,
    headline text,
    summary text,
    source text,
    url text,
    image_url text,
    category text,
    datetime integer,
    published_date timestamp without time zone,
    last_updated timestamp without time zone
);


ALTER TABLE public.news_articles OWNER TO lynch;

--
-- Name: news_articles_id_seq; Type: SEQUENCE; Schema: public; Owner: lynch
--

CREATE SEQUENCE public.news_articles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.news_articles_id_seq OWNER TO lynch;

--
-- Name: news_articles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lynch
--

ALTER SEQUENCE public.news_articles_id_seq OWNED BY public.news_articles.id;


--
-- Name: optimization_runs; Type: TABLE; Schema: public; Owner: lynch
--

CREATE TABLE public.optimization_runs (
    id integer NOT NULL,
    years_back integer,
    iterations integer,
    initial_correlation real,
    final_correlation real,
    improvement real,
    best_config_id integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.optimization_runs OWNER TO lynch;

--
-- Name: optimization_runs_id_seq; Type: SEQUENCE; Schema: public; Owner: lynch
--

CREATE SEQUENCE public.optimization_runs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.optimization_runs_id_seq OWNER TO lynch;

--
-- Name: optimization_runs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lynch
--

ALTER SEQUENCE public.optimization_runs_id_seq OWNED BY public.optimization_runs.id;


--
-- Name: portfolio_transactions; Type: TABLE; Schema: public; Owner: lynch
--

CREATE TABLE public.portfolio_transactions (
    id integer NOT NULL,
    portfolio_id integer NOT NULL,
    symbol text NOT NULL,
    transaction_type text NOT NULL,
    quantity integer NOT NULL,
    price_per_share real NOT NULL,
    total_value real NOT NULL,
    executed_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    note text,
    position_type character varying(20),
    dividend_payment_date date,
    CONSTRAINT portfolio_transactions_position_type_check CHECK (((position_type)::text = ANY ((ARRAY['new'::character varying, 'addition'::character varying, 'exit'::character varying])::text[]))),
    CONSTRAINT portfolio_transactions_quantity_check CHECK ((quantity > 0)),
    CONSTRAINT portfolio_transactions_transaction_type_check CHECK ((transaction_type = ANY (ARRAY['BUY'::text, 'SELL'::text, 'DIVIDEND'::text])))
);


ALTER TABLE public.portfolio_transactions OWNER TO lynch;

--
-- Name: portfolio_transactions_id_seq; Type: SEQUENCE; Schema: public; Owner: lynch
--

CREATE SEQUENCE public.portfolio_transactions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.portfolio_transactions_id_seq OWNER TO lynch;

--
-- Name: portfolio_transactions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lynch
--

ALTER SEQUENCE public.portfolio_transactions_id_seq OWNED BY public.portfolio_transactions.id;


--
-- Name: portfolio_value_snapshots; Type: TABLE; Schema: public; Owner: lynch
--

CREATE TABLE public.portfolio_value_snapshots (
    id integer NOT NULL,
    portfolio_id integer NOT NULL,
    total_value real NOT NULL,
    cash_value real NOT NULL,
    holdings_value real NOT NULL,
    snapshot_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.portfolio_value_snapshots OWNER TO lynch;

--
-- Name: portfolio_value_snapshots_id_seq; Type: SEQUENCE; Schema: public; Owner: lynch
--

CREATE SEQUENCE public.portfolio_value_snapshots_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.portfolio_value_snapshots_id_seq OWNER TO lynch;

--
-- Name: portfolio_value_snapshots_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lynch
--

ALTER SEQUENCE public.portfolio_value_snapshots_id_seq OWNED BY public.portfolio_value_snapshots.id;


--
-- Name: portfolios; Type: TABLE; Schema: public; Owner: lynch
--

CREATE TABLE public.portfolios (
    id integer NOT NULL,
    user_id integer NOT NULL,
    name text NOT NULL,
    initial_cash real DEFAULT 100000.0,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    dividend_preference text DEFAULT 'cash'::text,
    CONSTRAINT portfolios_dividend_preference_check CHECK ((dividend_preference = ANY (ARRAY['cash'::text, 'reinvest'::text])))
);


ALTER TABLE public.portfolios OWNER TO lynch;

--
-- Name: portfolios_id_seq; Type: SEQUENCE; Schema: public; Owner: lynch
--

CREATE SEQUENCE public.portfolios_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.portfolios_id_seq OWNER TO lynch;

--
-- Name: portfolios_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lynch
--

ALTER SEQUENCE public.portfolios_id_seq OWNED BY public.portfolios.id;


--
-- Name: position_entry_tracking; Type: TABLE; Schema: public; Owner: lynch
--

CREATE TABLE public.position_entry_tracking (
    portfolio_id integer NOT NULL,
    symbol character varying(10) NOT NULL,
    first_buy_date date NOT NULL,
    last_evaluated_date date
);


ALTER TABLE public.position_entry_tracking OWNER TO lynch;

--
-- Name: sec_filings; Type: TABLE; Schema: public; Owner: lynch
--

CREATE TABLE public.sec_filings (
    id integer NOT NULL,
    symbol text,
    filing_type text,
    filing_date text,
    document_url text,
    accession_number text,
    last_updated timestamp without time zone
);


ALTER TABLE public.sec_filings OWNER TO lynch;

--
-- Name: sec_filings_id_seq; Type: SEQUENCE; Schema: public; Owner: lynch
--

CREATE SEQUENCE public.sec_filings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sec_filings_id_seq OWNER TO lynch;

--
-- Name: sec_filings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lynch
--

ALTER SEQUENCE public.sec_filings_id_seq OWNED BY public.sec_filings.id;


--
-- Name: sessions; Type: TABLE; Schema: public; Owner: lynch
--

CREATE TABLE public.sessions (
    id integer NOT NULL,
    session_id character varying(255),
    data bytea,
    expiry timestamp without time zone
);


ALTER TABLE public.sessions OWNER TO lynch;

--
-- Name: sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: lynch
--

CREATE SEQUENCE public.sessions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sessions_id_seq OWNER TO lynch;

--
-- Name: sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lynch
--

ALTER SEQUENCE public.sessions_id_seq OWNED BY public.sessions.id;


--
-- Name: social_sentiment; Type: TABLE; Schema: public; Owner: lynch
--

CREATE TABLE public.social_sentiment (
    id text NOT NULL,
    symbol text NOT NULL,
    source text DEFAULT 'reddit'::text,
    subreddit text,
    title text,
    selftext text,
    url text,
    author text,
    score integer DEFAULT 0,
    upvote_ratio real,
    num_comments integer DEFAULT 0,
    sentiment_score real,
    created_utc bigint,
    published_at timestamp without time zone,
    fetched_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    conversation_json jsonb
);


ALTER TABLE public.social_sentiment OWNER TO lynch;

--
-- Name: stock_metrics; Type: TABLE; Schema: public; Owner: lynch
--

CREATE TABLE public.stock_metrics (
    symbol text NOT NULL,
    price real,
    pe_ratio real,
    market_cap real,
    debt_to_equity real,
    institutional_ownership real,
    revenue real,
    dividend_yield real,
    last_updated timestamp without time zone,
    beta real,
    total_debt real,
    interest_expense real,
    effective_tax_rate real,
    forward_pe real,
    forward_peg_ratio real,
    forward_eps real,
    insider_net_buying_6m real,
    analyst_rating text,
    analyst_rating_score real,
    analyst_count integer,
    price_target_high real,
    price_target_low real,
    price_target_mean real,
    short_ratio real,
    short_percent_float real,
    next_earnings_date date,
    gross_margin real,
    price_target_median real,
    earnings_growth real,
    earnings_quarterly_growth real,
    revenue_growth real,
    recommendation_key text,
    last_price_updated timestamp with time zone,
    prev_close real,
    price_change real,
    price_change_pct real
);


ALTER TABLE public.stock_metrics OWNER TO lynch;

--
-- Name: stocks; Type: TABLE; Schema: public; Owner: lynch
--

CREATE TABLE public.stocks (
    symbol text NOT NULL,
    company_name text,
    exchange text,
    sector text,
    country text,
    ipo_year integer,
    last_updated timestamp without time zone
);


ALTER TABLE public.stocks OWNER TO lynch;

--
-- Name: strategy_briefings; Type: TABLE; Schema: public; Owner: lynch
--

CREATE TABLE public.strategy_briefings (
    id integer NOT NULL,
    run_id integer,
    strategy_id integer,
    portfolio_id integer,
    candidates integer,
    qualifiers integer,
    theses_generated integer,
    trades integer,
    portfolio_value real,
    portfolio_return_pct real,
    spy_return_pct real,
    alpha real,
    buys_json text,
    sells_json text,
    holds_json text,
    watchlist_json text,
    executive_summary text,
    generated_at timestamp without time zone,
    universe_size integer DEFAULT 0,
    theses integer DEFAULT 0,
    targets integer DEFAULT 0,
    passed_thesis integer DEFAULT 0,
    passed_deliberation integer DEFAULT 0
);


ALTER TABLE public.strategy_briefings OWNER TO lynch;

--
-- Name: strategy_briefings_id_seq; Type: SEQUENCE; Schema: public; Owner: lynch
--

CREATE SEQUENCE public.strategy_briefings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.strategy_briefings_id_seq OWNER TO lynch;

--
-- Name: strategy_briefings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lynch
--

ALTER SEQUENCE public.strategy_briefings_id_seq OWNED BY public.strategy_briefings.id;


--
-- Name: strategy_decisions; Type: TABLE; Schema: public; Owner: lynch
--

CREATE TABLE public.strategy_decisions (
    id integer NOT NULL,
    run_id integer NOT NULL,
    symbol text NOT NULL,
    lynch_score real,
    lynch_status text,
    buffett_score real,
    buffett_status text,
    consensus_score real,
    consensus_verdict text,
    thesis_verdict text,
    thesis_summary text,
    thesis_full text,
    dcf_fair_value real,
    dcf_upside_pct real,
    final_decision text,
    decision_reasoning text,
    transaction_id integer,
    shares_traded integer,
    trade_price real,
    position_value real,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT strategy_decisions_consensus_verdict_check CHECK ((consensus_verdict = ANY (ARRAY['BUY'::text, 'WATCH'::text, 'AVOID'::text, 'VETO'::text]))),
    CONSTRAINT strategy_decisions_final_decision_check CHECK ((final_decision = ANY (ARRAY['BUY'::text, 'SKIP'::text, 'HOLD'::text, 'SELL'::text]))),
    CONSTRAINT strategy_decisions_thesis_verdict_check CHECK ((thesis_verdict = ANY (ARRAY['BUY'::text, 'WATCH'::text, 'AVOID'::text])))
);


ALTER TABLE public.strategy_decisions OWNER TO lynch;

--
-- Name: strategy_decisions_id_seq; Type: SEQUENCE; Schema: public; Owner: lynch
--

CREATE SEQUENCE public.strategy_decisions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.strategy_decisions_id_seq OWNER TO lynch;

--
-- Name: strategy_decisions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lynch
--

ALTER SEQUENCE public.strategy_decisions_id_seq OWNED BY public.strategy_decisions.id;


--
-- Name: strategy_performance; Type: TABLE; Schema: public; Owner: lynch
--

CREATE TABLE public.strategy_performance (
    id integer NOT NULL,
    strategy_id integer NOT NULL,
    snapshot_date date NOT NULL,
    portfolio_value real NOT NULL,
    portfolio_return_pct real,
    spy_return_pct real,
    alpha real
);


ALTER TABLE public.strategy_performance OWNER TO lynch;

--
-- Name: strategy_performance_id_seq; Type: SEQUENCE; Schema: public; Owner: lynch
--

CREATE SEQUENCE public.strategy_performance_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.strategy_performance_id_seq OWNER TO lynch;

--
-- Name: strategy_performance_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lynch
--

ALTER SEQUENCE public.strategy_performance_id_seq OWNED BY public.strategy_performance.id;


--
-- Name: strategy_runs; Type: TABLE; Schema: public; Owner: lynch
--

CREATE TABLE public.strategy_runs (
    id integer NOT NULL,
    strategy_id integer NOT NULL,
    started_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    completed_at timestamp without time zone,
    status text DEFAULT 'running'::text NOT NULL,
    candidates integer DEFAULT 0,
    qualifiers integer DEFAULT 0,
    trades integer DEFAULT 0,
    spy_price real,
    portfolio_value real,
    error_message text,
    run_log jsonb DEFAULT '[]'::jsonb,
    universe_size integer DEFAULT 0,
    theses integer DEFAULT 0,
    targets integer DEFAULT 0,
    passed_thesis integer DEFAULT 0,
    passed_deliberation integer DEFAULT 0,
    CONSTRAINT strategy_runs_status_check CHECK ((status = ANY (ARRAY['running'::text, 'completed'::text, 'failed'::text, 'cancelled'::text])))
);


ALTER TABLE public.strategy_runs OWNER TO lynch;

--
-- Name: strategy_runs_id_seq; Type: SEQUENCE; Schema: public; Owner: lynch
--

CREATE SEQUENCE public.strategy_runs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.strategy_runs_id_seq OWNER TO lynch;

--
-- Name: strategy_runs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lynch
--

ALTER SEQUENCE public.strategy_runs_id_seq OWNED BY public.strategy_runs.id;


--
-- Name: thesis_refresh_queue; Type: TABLE; Schema: public; Owner: lynch
--

CREATE TABLE public.thesis_refresh_queue (
    id integer NOT NULL,
    symbol text NOT NULL,
    reason text NOT NULL,
    priority integer DEFAULT 0 NOT NULL,
    status text DEFAULT 'PENDING'::text NOT NULL,
    attempts integer DEFAULT 0,
    error_message text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT thesis_refresh_queue_status_check CHECK ((status = ANY (ARRAY['PENDING'::text, 'PROCESSING'::text, 'COMPLETED'::text, 'FAILED'::text])))
);


ALTER TABLE public.thesis_refresh_queue OWNER TO lynch;

--
-- Name: thesis_refresh_queue_id_seq; Type: SEQUENCE; Schema: public; Owner: lynch
--

CREATE SEQUENCE public.thesis_refresh_queue_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.thesis_refresh_queue_id_seq OWNER TO lynch;

--
-- Name: thesis_refresh_queue_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lynch
--

ALTER SEQUENCE public.thesis_refresh_queue_id_seq OWNED BY public.thesis_refresh_queue.id;


--
-- Name: user_events; Type: TABLE; Schema: public; Owner: lynch
--

CREATE TABLE public.user_events (
    id integer NOT NULL,
    user_id integer,
    event_type text,
    path text,
    method text,
    query_params jsonb,
    request_body jsonb,
    ip_address text,
    user_agent text,
    status_code integer,
    duration_ms integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.user_events OWNER TO lynch;

--
-- Name: user_events_id_seq; Type: SEQUENCE; Schema: public; Owner: lynch
--

CREATE SEQUENCE public.user_events_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_events_id_seq OWNER TO lynch;

--
-- Name: user_events_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lynch
--

ALTER SEQUENCE public.user_events_id_seq OWNED BY public.user_events.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: lynch
--

CREATE TABLE public.users (
    id integer NOT NULL,
    google_id text,
    email text NOT NULL,
    name text,
    picture text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    last_login timestamp without time zone,
    active_character text DEFAULT 'lynch'::text,
    theme text DEFAULT 'midnight'::text,
    password_hash text,
    is_verified boolean DEFAULT true,
    verification_token text,
    verification_code character varying(6),
    code_expires_at timestamp without time zone,
    has_completed_onboarding boolean DEFAULT false,
    expertise_level text DEFAULT 'practicing'::text,
    user_type text DEFAULT 'regular'::text,
    email_briefs boolean DEFAULT true,
    subscription_tier text DEFAULT 'free'::text,
    stripe_customer_id text,
    stripe_subscription_id text,
    subscription_expires_at timestamp with time zone
);


ALTER TABLE public.users OWNER TO lynch;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: lynch
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO lynch;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lynch
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: watchlist; Type: TABLE; Schema: public; Owner: lynch
--

CREATE TABLE public.watchlist (
    symbol text NOT NULL,
    added_at timestamp without time zone,
    user_id integer NOT NULL,
    id integer NOT NULL
);


ALTER TABLE public.watchlist OWNER TO lynch;

--
-- Name: watchlist_id_seq; Type: SEQUENCE; Schema: public; Owner: lynch
--

CREATE SEQUENCE public.watchlist_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.watchlist_id_seq OWNER TO lynch;

--
-- Name: watchlist_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lynch
--

ALTER SEQUENCE public.watchlist_id_seq OWNED BY public.watchlist.id;


--
-- Name: weekly_prices; Type: TABLE; Schema: public; Owner: lynch
--

CREATE TABLE public.weekly_prices (
    symbol text NOT NULL,
    week_ending date NOT NULL,
    price real,
    last_updated timestamp without time zone
);


ALTER TABLE public.weekly_prices OWNER TO lynch;

--
-- Name: worker_heartbeats; Type: TABLE; Schema: public; Owner: lynch
--

CREATE TABLE public.worker_heartbeats (
    worker_id text NOT NULL,
    status text NOT NULL,
    tier text,
    last_heartbeat timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.worker_heartbeats OWNER TO lynch;


-- yoyo_lock table removed

--
-- Name: agent_conversations id; Type: DEFAULT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.agent_conversations ALTER COLUMN id SET DEFAULT nextval('public.agent_conversations_id_seq'::regclass);


--
-- Name: agent_messages id; Type: DEFAULT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.agent_messages ALTER COLUMN id SET DEFAULT nextval('public.agent_messages_id_seq'::regclass);


--
-- Name: alerts id; Type: DEFAULT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.alerts ALTER COLUMN id SET DEFAULT nextval('public.alerts_id_seq'::regclass);


--
-- Name: algorithm_configurations id; Type: DEFAULT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.algorithm_configurations ALTER COLUMN id SET DEFAULT nextval('public.algorithm_configurations_id_seq'::regclass);


--
-- Name: analyst_estimates id; Type: DEFAULT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.analyst_estimates ALTER COLUMN id SET DEFAULT nextval('public.analyst_estimates_id_seq'::regclass);


--
-- Name: analyst_recommendations id; Type: DEFAULT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.analyst_recommendations ALTER COLUMN id SET DEFAULT nextval('public.analyst_recommendations_id_seq'::regclass);


--
-- Name: app_feedback id; Type: DEFAULT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.app_feedback ALTER COLUMN id SET DEFAULT nextval('public.app_feedback_id_seq'::regclass);


--
-- Name: background_jobs id; Type: DEFAULT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.background_jobs ALTER COLUMN id SET DEFAULT nextval('public.background_jobs_id_seq'::regclass);


--
-- Name: backtest_results id; Type: DEFAULT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.backtest_results ALTER COLUMN id SET DEFAULT nextval('public.backtest_results_id_seq'::regclass);


--
-- Name: benchmark_snapshots id; Type: DEFAULT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.benchmark_snapshots ALTER COLUMN id SET DEFAULT nextval('public.benchmark_snapshots_id_seq'::regclass);


--
-- Name: chart_analyses id; Type: DEFAULT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.chart_analyses ALTER COLUMN id SET DEFAULT nextval('public.chart_analyses_id_seq'::regclass);


--
-- Name: dcf_recommendations id; Type: DEFAULT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.dcf_recommendations ALTER COLUMN id SET DEFAULT nextval('public.dcf_recommendations_id_seq'::regclass);


--
-- Name: dividend_payouts id; Type: DEFAULT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.dividend_payouts ALTER COLUMN id SET DEFAULT nextval('public.dividend_payouts_id_seq'::regclass);


--
-- Name: earnings_history id; Type: DEFAULT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.earnings_history ALTER COLUMN id SET DEFAULT nextval('public.earnings_history_id_seq'::regclass);


--
-- Name: earnings_transcripts id; Type: DEFAULT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.earnings_transcripts ALTER COLUMN id SET DEFAULT nextval('public.earnings_transcripts_id_seq'::regclass);


--
-- Name: eps_revisions id; Type: DEFAULT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.eps_revisions ALTER COLUMN id SET DEFAULT nextval('public.eps_revisions_id_seq'::regclass);


--
-- Name: eps_trends id; Type: DEFAULT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.eps_trends ALTER COLUMN id SET DEFAULT nextval('public.eps_trends_id_seq'::regclass);


--
-- Name: filing_section_summaries id; Type: DEFAULT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.filing_section_summaries ALTER COLUMN id SET DEFAULT nextval('public.filing_section_summaries_id_seq'::regclass);


--
-- Name: filing_sections id; Type: DEFAULT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.filing_sections ALTER COLUMN id SET DEFAULT nextval('public.filing_sections_id_seq'::regclass);


--
-- Name: growth_estimates id; Type: DEFAULT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.growth_estimates ALTER COLUMN id SET DEFAULT nextval('public.growth_estimates_id_seq'::regclass);


--
-- Name: insider_trades id; Type: DEFAULT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.insider_trades ALTER COLUMN id SET DEFAULT nextval('public.insider_trades_id_seq'::regclass);


--
-- Name: investment_strategies id; Type: DEFAULT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.investment_strategies ALTER COLUMN id SET DEFAULT nextval('public.investment_strategies_id_seq'::regclass);


--
-- Name: lynch_analyses id; Type: DEFAULT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.lynch_analyses ALTER COLUMN id SET DEFAULT nextval('public.lynch_analyses_id_seq'::regclass);


--
-- Name: material_event_summaries id; Type: DEFAULT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.material_event_summaries ALTER COLUMN id SET DEFAULT nextval('public.material_event_summaries_id_seq'::regclass);


--
-- Name: material_events id; Type: DEFAULT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.material_events ALTER COLUMN id SET DEFAULT nextval('public.material_events_id_seq'::regclass);


--
-- Name: news_articles id; Type: DEFAULT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.news_articles ALTER COLUMN id SET DEFAULT nextval('public.news_articles_id_seq'::regclass);


--
-- Name: optimization_runs id; Type: DEFAULT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.optimization_runs ALTER COLUMN id SET DEFAULT nextval('public.optimization_runs_id_seq'::regclass);


--
-- Name: portfolio_transactions id; Type: DEFAULT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.portfolio_transactions ALTER COLUMN id SET DEFAULT nextval('public.portfolio_transactions_id_seq'::regclass);


--
-- Name: portfolio_value_snapshots id; Type: DEFAULT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.portfolio_value_snapshots ALTER COLUMN id SET DEFAULT nextval('public.portfolio_value_snapshots_id_seq'::regclass);


--
-- Name: portfolios id; Type: DEFAULT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.portfolios ALTER COLUMN id SET DEFAULT nextval('public.portfolios_id_seq'::regclass);


--
-- Name: sec_filings id; Type: DEFAULT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.sec_filings ALTER COLUMN id SET DEFAULT nextval('public.sec_filings_id_seq'::regclass);


--
-- Name: sessions id; Type: DEFAULT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.sessions ALTER COLUMN id SET DEFAULT nextval('public.sessions_id_seq'::regclass);


--
-- Name: strategy_briefings id; Type: DEFAULT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.strategy_briefings ALTER COLUMN id SET DEFAULT nextval('public.strategy_briefings_id_seq'::regclass);


--
-- Name: strategy_decisions id; Type: DEFAULT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.strategy_decisions ALTER COLUMN id SET DEFAULT nextval('public.strategy_decisions_id_seq'::regclass);


--
-- Name: strategy_performance id; Type: DEFAULT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.strategy_performance ALTER COLUMN id SET DEFAULT nextval('public.strategy_performance_id_seq'::regclass);


--
-- Name: strategy_runs id; Type: DEFAULT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.strategy_runs ALTER COLUMN id SET DEFAULT nextval('public.strategy_runs_id_seq'::regclass);


--
-- Name: thesis_refresh_queue id; Type: DEFAULT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.thesis_refresh_queue ALTER COLUMN id SET DEFAULT nextval('public.thesis_refresh_queue_id_seq'::regclass);


--
-- Name: user_events id; Type: DEFAULT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.user_events ALTER COLUMN id SET DEFAULT nextval('public.user_events_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: watchlist id; Type: DEFAULT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.watchlist ALTER COLUMN id SET DEFAULT nextval('public.watchlist_id_seq'::regclass);



-- yoyo metadata constraints removed


--
-- Name: agent_conversations agent_conversations_pkey; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.agent_conversations
    ADD CONSTRAINT agent_conversations_pkey PRIMARY KEY (id);


--
-- Name: agent_messages agent_messages_pkey; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.agent_messages
    ADD CONSTRAINT agent_messages_pkey PRIMARY KEY (id);


--
-- Name: alerts alerts_pkey; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.alerts
    ADD CONSTRAINT alerts_pkey PRIMARY KEY (id);


--
-- Name: algorithm_configurations algorithm_configurations_pkey; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.algorithm_configurations
    ADD CONSTRAINT algorithm_configurations_pkey PRIMARY KEY (id);


--
-- Name: analysis_generation_status analysis_generation_status_pkey; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.analysis_generation_status
    ADD CONSTRAINT analysis_generation_status_pkey PRIMARY KEY (user_id, symbol, character_id);


--
-- Name: analyst_estimates analyst_estimates_pkey; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.analyst_estimates
    ADD CONSTRAINT analyst_estimates_pkey PRIMARY KEY (id);


--
-- Name: analyst_estimates analyst_estimates_symbol_period_key; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.analyst_estimates
    ADD CONSTRAINT analyst_estimates_symbol_period_key UNIQUE (symbol, period);


--
-- Name: analyst_recommendations analyst_recommendations_pkey; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.analyst_recommendations
    ADD CONSTRAINT analyst_recommendations_pkey PRIMARY KEY (id);


--
-- Name: analyst_recommendations analyst_recommendations_symbol_period_month_key; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.analyst_recommendations
    ADD CONSTRAINT analyst_recommendations_symbol_period_month_key UNIQUE (symbol, period_month);


--
-- Name: app_feedback app_feedback_pkey; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.app_feedback
    ADD CONSTRAINT app_feedback_pkey PRIMARY KEY (id);


--
-- Name: app_settings app_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.app_settings
    ADD CONSTRAINT app_settings_pkey PRIMARY KEY (key);


--
-- Name: background_jobs background_jobs_pkey; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.background_jobs
    ADD CONSTRAINT background_jobs_pkey PRIMARY KEY (id);


--
-- Name: backtest_results backtest_results_pkey; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.backtest_results
    ADD CONSTRAINT backtest_results_pkey PRIMARY KEY (id);


--
-- Name: backtest_results backtest_results_symbol_years_back_key; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.backtest_results
    ADD CONSTRAINT backtest_results_symbol_years_back_key UNIQUE (symbol, years_back);


--
-- Name: benchmark_snapshots benchmark_snapshots_pkey; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.benchmark_snapshots
    ADD CONSTRAINT benchmark_snapshots_pkey PRIMARY KEY (id);


--
-- Name: benchmark_snapshots benchmark_snapshots_snapshot_date_key; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.benchmark_snapshots
    ADD CONSTRAINT benchmark_snapshots_snapshot_date_key UNIQUE (snapshot_date);


--
-- Name: cache_checks cache_checks_pkey; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.cache_checks
    ADD CONSTRAINT cache_checks_pkey PRIMARY KEY (symbol, cache_type);


--
-- Name: chart_analyses chart_analyses_pkey; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.chart_analyses
    ADD CONSTRAINT chart_analyses_pkey PRIMARY KEY (user_id, symbol, section, character_id);


--
-- Name: company_facts company_facts_pkey; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.company_facts
    ADD CONSTRAINT company_facts_pkey PRIMARY KEY (cik);


--
-- Name: dcf_recommendations dcf_recommendations_pkey; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.dcf_recommendations
    ADD CONSTRAINT dcf_recommendations_pkey PRIMARY KEY (id);


--
-- Name: dcf_recommendations dcf_recommendations_user_symbol_unique; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.dcf_recommendations
    ADD CONSTRAINT dcf_recommendations_user_symbol_unique UNIQUE (user_id, symbol);


--
-- Name: deliberations deliberations_pkey; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.deliberations
    ADD CONSTRAINT deliberations_pkey PRIMARY KEY (user_id, symbol);


--
-- Name: dividend_payouts dividend_payouts_pkey; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.dividend_payouts
    ADD CONSTRAINT dividend_payouts_pkey PRIMARY KEY (id);


--
-- Name: dividend_payouts dividend_payouts_symbol_payment_date_key; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.dividend_payouts
    ADD CONSTRAINT dividend_payouts_symbol_payment_date_key UNIQUE (symbol, payment_date);


--
-- Name: earnings_history earnings_history_pkey; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.earnings_history
    ADD CONSTRAINT earnings_history_pkey PRIMARY KEY (id);


--
-- Name: earnings_history earnings_history_symbol_year_period_key; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.earnings_history
    ADD CONSTRAINT earnings_history_symbol_year_period_key UNIQUE (symbol, year, period);


--
-- Name: earnings_transcripts earnings_transcripts_pkey; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.earnings_transcripts
    ADD CONSTRAINT earnings_transcripts_pkey PRIMARY KEY (id);


--
-- Name: earnings_transcripts earnings_transcripts_symbol_quarter_fiscal_year_key; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.earnings_transcripts
    ADD CONSTRAINT earnings_transcripts_symbol_quarter_fiscal_year_key UNIQUE (symbol, quarter, fiscal_year);


--
-- Name: eps_revisions eps_revisions_pkey; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.eps_revisions
    ADD CONSTRAINT eps_revisions_pkey PRIMARY KEY (id);


--
-- Name: eps_revisions eps_revisions_symbol_period_key; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.eps_revisions
    ADD CONSTRAINT eps_revisions_symbol_period_key UNIQUE (symbol, period);


--
-- Name: eps_trends eps_trends_pkey; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.eps_trends
    ADD CONSTRAINT eps_trends_pkey PRIMARY KEY (id);


--
-- Name: eps_trends eps_trends_symbol_period_key; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.eps_trends
    ADD CONSTRAINT eps_trends_symbol_period_key UNIQUE (symbol, period);


--
-- Name: filing_section_summaries filing_section_summaries_pkey; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.filing_section_summaries
    ADD CONSTRAINT filing_section_summaries_pkey PRIMARY KEY (id);


--
-- Name: filing_section_summaries filing_section_summaries_symbol_section_name_filing_type_key; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.filing_section_summaries
    ADD CONSTRAINT filing_section_summaries_symbol_section_name_filing_type_key UNIQUE (symbol, section_name, filing_type);


--
-- Name: filing_sections filing_sections_pkey; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.filing_sections
    ADD CONSTRAINT filing_sections_pkey PRIMARY KEY (id);


--
-- Name: filing_sections filing_sections_symbol_section_name_filing_type_key; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.filing_sections
    ADD CONSTRAINT filing_sections_symbol_section_name_filing_type_key UNIQUE (symbol, section_name, filing_type);


--
-- Name: fred_data_cache fred_data_cache_pkey; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.fred_data_cache
    ADD CONSTRAINT fred_data_cache_pkey PRIMARY KEY (cache_key);


--
-- Name: growth_estimates growth_estimates_pkey; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.growth_estimates
    ADD CONSTRAINT growth_estimates_pkey PRIMARY KEY (id);


--
-- Name: growth_estimates growth_estimates_symbol_period_key; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.growth_estimates
    ADD CONSTRAINT growth_estimates_symbol_period_key UNIQUE (symbol, period);


--
-- Name: insider_trades insider_trades_pkey; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.insider_trades
    ADD CONSTRAINT insider_trades_pkey PRIMARY KEY (id);


--
-- Name: insider_trades insider_trades_symbol_name_transaction_date_transaction_typ_key; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.insider_trades
    ADD CONSTRAINT insider_trades_symbol_name_transaction_date_transaction_typ_key UNIQUE (symbol, name, transaction_date, transaction_type, shares);


--
-- Name: investment_strategies investment_strategies_pkey; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.investment_strategies
    ADD CONSTRAINT investment_strategies_pkey PRIMARY KEY (id);


--
-- Name: lynch_analyses lynch_analyses_pkey; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.lynch_analyses
    ADD CONSTRAINT lynch_analyses_pkey PRIMARY KEY (user_id, symbol, character_id);


--
-- Name: material_event_summaries material_event_summaries_event_id_key; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.material_event_summaries
    ADD CONSTRAINT material_event_summaries_event_id_key UNIQUE (event_id);


--
-- Name: material_event_summaries material_event_summaries_pkey; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.material_event_summaries
    ADD CONSTRAINT material_event_summaries_pkey PRIMARY KEY (id);


--
-- Name: material_events material_events_pkey; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.material_events
    ADD CONSTRAINT material_events_pkey PRIMARY KEY (id);


--
-- Name: material_events material_events_symbol_sec_accession_number_key; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.material_events
    ADD CONSTRAINT material_events_symbol_sec_accession_number_key UNIQUE (symbol, sec_accession_number);


--
-- Name: news_articles news_articles_pkey; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.news_articles
    ADD CONSTRAINT news_articles_pkey PRIMARY KEY (id);


--
-- Name: news_articles news_articles_symbol_finnhub_id_key; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.news_articles
    ADD CONSTRAINT news_articles_symbol_finnhub_id_key UNIQUE (symbol, finnhub_id);


--
-- Name: optimization_runs optimization_runs_pkey; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.optimization_runs
    ADD CONSTRAINT optimization_runs_pkey PRIMARY KEY (id);


--
-- Name: portfolio_transactions portfolio_transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.portfolio_transactions
    ADD CONSTRAINT portfolio_transactions_pkey PRIMARY KEY (id);


--
-- Name: portfolio_value_snapshots portfolio_value_snapshots_pkey; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.portfolio_value_snapshots
    ADD CONSTRAINT portfolio_value_snapshots_pkey PRIMARY KEY (id);


--
-- Name: portfolios portfolios_pkey; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.portfolios
    ADD CONSTRAINT portfolios_pkey PRIMARY KEY (id);


--
-- Name: position_entry_tracking position_entry_tracking_pkey; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.position_entry_tracking
    ADD CONSTRAINT position_entry_tracking_pkey PRIMARY KEY (portfolio_id, symbol);


--
-- Name: sec_filings sec_filings_pkey; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.sec_filings
    ADD CONSTRAINT sec_filings_pkey PRIMARY KEY (id);


--
-- Name: sec_filings sec_filings_symbol_accession_number_key; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.sec_filings
    ADD CONSTRAINT sec_filings_symbol_accession_number_key UNIQUE (symbol, accession_number);


--
-- Name: sessions sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_pkey PRIMARY KEY (id);


--
-- Name: sessions sessions_session_id_key; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_session_id_key UNIQUE (session_id);


--
-- Name: social_sentiment social_sentiment_pkey; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.social_sentiment
    ADD CONSTRAINT social_sentiment_pkey PRIMARY KEY (id);


--
-- Name: stock_metrics stock_metrics_pkey; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.stock_metrics
    ADD CONSTRAINT stock_metrics_pkey PRIMARY KEY (symbol);


--
-- Name: stocks stocks_pkey; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.stocks
    ADD CONSTRAINT stocks_pkey PRIMARY KEY (symbol);


--
-- Name: strategy_briefings strategy_briefings_pkey; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.strategy_briefings
    ADD CONSTRAINT strategy_briefings_pkey PRIMARY KEY (id);


--
-- Name: strategy_briefings strategy_briefings_run_id_key; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.strategy_briefings
    ADD CONSTRAINT strategy_briefings_run_id_key UNIQUE (run_id);


--
-- Name: strategy_decisions strategy_decisions_pkey; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.strategy_decisions
    ADD CONSTRAINT strategy_decisions_pkey PRIMARY KEY (id);


--
-- Name: strategy_performance strategy_performance_pkey; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.strategy_performance
    ADD CONSTRAINT strategy_performance_pkey PRIMARY KEY (id);


--
-- Name: strategy_performance strategy_performance_strategy_id_snapshot_date_key; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.strategy_performance
    ADD CONSTRAINT strategy_performance_strategy_id_snapshot_date_key UNIQUE (strategy_id, snapshot_date);


--
-- Name: strategy_runs strategy_runs_pkey; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.strategy_runs
    ADD CONSTRAINT strategy_runs_pkey PRIMARY KEY (id);


--
-- Name: thesis_refresh_queue thesis_refresh_queue_pkey; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.thesis_refresh_queue
    ADD CONSTRAINT thesis_refresh_queue_pkey PRIMARY KEY (id);


--
-- Name: thesis_refresh_queue thesis_refresh_queue_symbol_key; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.thesis_refresh_queue
    ADD CONSTRAINT thesis_refresh_queue_symbol_key UNIQUE (symbol);


--
-- Name: user_events user_events_pkey; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.user_events
    ADD CONSTRAINT user_events_pkey PRIMARY KEY (id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_google_id_key; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_google_id_key UNIQUE (google_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: watchlist watchlist_pkey; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.watchlist
    ADD CONSTRAINT watchlist_pkey PRIMARY KEY (id);


--
-- Name: watchlist watchlist_user_symbol_unique; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.watchlist
    ADD CONSTRAINT watchlist_user_symbol_unique UNIQUE (user_id, symbol);


--
-- Name: weekly_prices weekly_prices_pkey; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.weekly_prices
    ADD CONSTRAINT weekly_prices_pkey PRIMARY KEY (symbol, week_ending);


--
-- Name: worker_heartbeats worker_heartbeats_pkey; Type: CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.worker_heartbeats
    ADD CONSTRAINT worker_heartbeats_pkey PRIMARY KEY (worker_id);



-- yoyo_lock constraint removed


--
-- Name: idx_agent_conversations_user; Type: INDEX; Schema: public; Owner: lynch
--

CREATE INDEX idx_agent_conversations_user ON public.agent_conversations USING btree (user_id, last_message_at DESC);


--
-- Name: idx_agent_messages_conversation; Type: INDEX; Schema: public; Owner: lynch
--

CREATE INDEX idx_agent_messages_conversation ON public.agent_messages USING btree (conversation_id, created_at);


--
-- Name: idx_background_jobs_pending; Type: INDEX; Schema: public; Owner: lynch
--

CREATE INDEX idx_background_jobs_pending ON public.background_jobs USING btree (status, created_at) WHERE (status = 'pending'::text);


--
-- Name: idx_benchmark_date; Type: INDEX; Schema: public; Owner: lynch
--

CREATE INDEX idx_benchmark_date ON public.benchmark_snapshots USING btree (snapshot_date);


--
-- Name: idx_briefings_portfolio; Type: INDEX; Schema: public; Owner: lynch
--

CREATE INDEX idx_briefings_portfolio ON public.strategy_briefings USING btree (portfolio_id, generated_at DESC);


--
-- Name: idx_cache_checks_type; Type: INDEX; Schema: public; Owner: lynch
--

CREATE INDEX idx_cache_checks_type ON public.cache_checks USING btree (cache_type, last_checked);


--
-- Name: idx_company_facts_entity_name; Type: INDEX; Schema: public; Owner: lynch
--

CREATE INDEX idx_company_facts_entity_name ON public.company_facts USING btree (entity_name);


--
-- Name: idx_company_facts_facts_gin; Type: INDEX; Schema: public; Owner: lynch
--

CREATE INDEX idx_company_facts_facts_gin ON public.company_facts USING gin (facts);


--
-- Name: idx_company_facts_ticker; Type: INDEX; Schema: public; Owner: lynch
--

CREATE INDEX idx_company_facts_ticker ON public.company_facts USING btree (ticker);


--
-- Name: idx_decisions_run; Type: INDEX; Schema: public; Owner: lynch
--

CREATE INDEX idx_decisions_run ON public.strategy_decisions USING btree (run_id);


--
-- Name: idx_decisions_symbol; Type: INDEX; Schema: public; Owner: lynch
--

CREATE INDEX idx_decisions_symbol ON public.strategy_decisions USING btree (symbol);


--
-- Name: idx_news_articles_symbol_datetime; Type: INDEX; Schema: public; Owner: lynch
--

CREATE INDEX idx_news_articles_symbol_datetime ON public.news_articles USING btree (symbol, datetime DESC);


--
-- Name: idx_perf_strategy; Type: INDEX; Schema: public; Owner: lynch
--

CREATE INDEX idx_perf_strategy ON public.strategy_performance USING btree (strategy_id, snapshot_date);


--
-- Name: idx_portfolio_snapshots_portfolio_time; Type: INDEX; Schema: public; Owner: lynch
--

CREATE INDEX idx_portfolio_snapshots_portfolio_time ON public.portfolio_value_snapshots USING btree (portfolio_id, snapshot_at);


--
-- Name: idx_portfolio_transactions_portfolio; Type: INDEX; Schema: public; Owner: lynch
--

CREATE INDEX idx_portfolio_transactions_portfolio ON public.portfolio_transactions USING btree (portfolio_id);


--
-- Name: idx_portfolios_user; Type: INDEX; Schema: public; Owner: lynch
--

CREATE INDEX idx_portfolios_user ON public.portfolios USING btree (user_id);


--
-- Name: idx_position_entry_tracking_portfolio; Type: INDEX; Schema: public; Owner: lynch
--

CREATE INDEX idx_position_entry_tracking_portfolio ON public.position_entry_tracking USING btree (portfolio_id);


--
-- Name: idx_runs_strategy; Type: INDEX; Schema: public; Owner: lynch
--

CREATE INDEX idx_runs_strategy ON public.strategy_runs USING btree (strategy_id, started_at DESC);


--
-- Name: idx_social_sentiment_score; Type: INDEX; Schema: public; Owner: lynch
--

CREATE INDEX idx_social_sentiment_score ON public.social_sentiment USING btree (score DESC);


--
-- Name: idx_social_sentiment_symbol_date; Type: INDEX; Schema: public; Owner: lynch
--

CREATE INDEX idx_social_sentiment_symbol_date ON public.social_sentiment USING btree (symbol, published_at DESC);


--
-- Name: idx_strategies_enabled; Type: INDEX; Schema: public; Owner: lynch
--

CREATE INDEX idx_strategies_enabled ON public.investment_strategies USING btree (enabled, schedule_cron);


--
-- Name: idx_strategies_user; Type: INDEX; Schema: public; Owner: lynch
--

CREATE INDEX idx_strategies_user ON public.investment_strategies USING btree (user_id);


--
-- Name: idx_thesis_queue_status_priority; Type: INDEX; Schema: public; Owner: lynch
--

CREATE INDEX idx_thesis_queue_status_priority ON public.thesis_refresh_queue USING btree (status, priority DESC);


--
-- Name: idx_user_events_created; Type: INDEX; Schema: public; Owner: lynch
--

CREATE INDEX idx_user_events_created ON public.user_events USING btree (created_at);


--
-- Name: idx_user_events_user; Type: INDEX; Schema: public; Owner: lynch
--

CREATE INDEX idx_user_events_user ON public.user_events USING btree (user_id);


--
-- Name: agent_conversations agent_conversations_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.agent_conversations
    ADD CONSTRAINT agent_conversations_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: agent_messages agent_messages_conversation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.agent_messages
    ADD CONSTRAINT agent_messages_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES public.agent_conversations(id) ON DELETE CASCADE;


--
-- Name: alerts alerts_portfolio_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.alerts
    ADD CONSTRAINT alerts_portfolio_id_fkey FOREIGN KEY (portfolio_id) REFERENCES public.portfolios(id) ON DELETE CASCADE;


--
-- Name: alerts alerts_symbol_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.alerts
    ADD CONSTRAINT alerts_symbol_fkey FOREIGN KEY (symbol) REFERENCES public.stocks(symbol);


--
-- Name: alerts alerts_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.alerts
    ADD CONSTRAINT alerts_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: algorithm_configurations algorithm_configurations_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.algorithm_configurations
    ADD CONSTRAINT algorithm_configurations_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: analysis_generation_status analysis_generation_status_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.analysis_generation_status
    ADD CONSTRAINT analysis_generation_status_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: analyst_estimates analyst_estimates_symbol_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.analyst_estimates
    ADD CONSTRAINT analyst_estimates_symbol_fkey FOREIGN KEY (symbol) REFERENCES public.stocks(symbol);


--
-- Name: analyst_recommendations analyst_recommendations_symbol_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.analyst_recommendations
    ADD CONSTRAINT analyst_recommendations_symbol_fkey FOREIGN KEY (symbol) REFERENCES public.stocks(symbol);


--
-- Name: app_feedback app_feedback_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.app_feedback
    ADD CONSTRAINT app_feedback_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: chart_analyses chart_analyses_symbol_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.chart_analyses
    ADD CONSTRAINT chart_analyses_symbol_fkey FOREIGN KEY (symbol) REFERENCES public.stocks(symbol);


--
-- Name: chart_analyses chart_analyses_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.chart_analyses
    ADD CONSTRAINT chart_analyses_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: dcf_recommendations dcf_recommendations_symbol_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.dcf_recommendations
    ADD CONSTRAINT dcf_recommendations_symbol_fkey FOREIGN KEY (symbol) REFERENCES public.stocks(symbol);


--
-- Name: dcf_recommendations dcf_recommendations_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.dcf_recommendations
    ADD CONSTRAINT dcf_recommendations_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: deliberations deliberations_symbol_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.deliberations
    ADD CONSTRAINT deliberations_symbol_fkey FOREIGN KEY (symbol) REFERENCES public.stocks(symbol);


--
-- Name: deliberations deliberations_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.deliberations
    ADD CONSTRAINT deliberations_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: dividend_payouts dividend_payouts_symbol_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.dividend_payouts
    ADD CONSTRAINT dividend_payouts_symbol_fkey FOREIGN KEY (symbol) REFERENCES public.stocks(symbol);


--
-- Name: earnings_history earnings_history_symbol_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.earnings_history
    ADD CONSTRAINT earnings_history_symbol_fkey FOREIGN KEY (symbol) REFERENCES public.stocks(symbol);


--
-- Name: earnings_transcripts earnings_transcripts_symbol_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.earnings_transcripts
    ADD CONSTRAINT earnings_transcripts_symbol_fkey FOREIGN KEY (symbol) REFERENCES public.stocks(symbol);


--
-- Name: eps_revisions eps_revisions_symbol_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.eps_revisions
    ADD CONSTRAINT eps_revisions_symbol_fkey FOREIGN KEY (symbol) REFERENCES public.stocks(symbol);


--
-- Name: eps_trends eps_trends_symbol_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.eps_trends
    ADD CONSTRAINT eps_trends_symbol_fkey FOREIGN KEY (symbol) REFERENCES public.stocks(symbol);


--
-- Name: filing_section_summaries filing_section_summaries_symbol_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.filing_section_summaries
    ADD CONSTRAINT filing_section_summaries_symbol_fkey FOREIGN KEY (symbol) REFERENCES public.stocks(symbol);


--
-- Name: filing_sections filing_sections_symbol_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.filing_sections
    ADD CONSTRAINT filing_sections_symbol_fkey FOREIGN KEY (symbol) REFERENCES public.stocks(symbol);


--
-- Name: growth_estimates growth_estimates_symbol_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.growth_estimates
    ADD CONSTRAINT growth_estimates_symbol_fkey FOREIGN KEY (symbol) REFERENCES public.stocks(symbol);


--
-- Name: insider_trades insider_trades_symbol_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.insider_trades
    ADD CONSTRAINT insider_trades_symbol_fkey FOREIGN KEY (symbol) REFERENCES public.stocks(symbol);


--
-- Name: investment_strategies investment_strategies_portfolio_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.investment_strategies
    ADD CONSTRAINT investment_strategies_portfolio_id_fkey FOREIGN KEY (portfolio_id) REFERENCES public.portfolios(id) ON DELETE CASCADE;


--
-- Name: investment_strategies investment_strategies_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.investment_strategies
    ADD CONSTRAINT investment_strategies_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: lynch_analyses lynch_analyses_symbol_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.lynch_analyses
    ADD CONSTRAINT lynch_analyses_symbol_fkey FOREIGN KEY (symbol) REFERENCES public.stocks(symbol);


--
-- Name: lynch_analyses lynch_analyses_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.lynch_analyses
    ADD CONSTRAINT lynch_analyses_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: material_event_summaries material_event_summaries_event_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.material_event_summaries
    ADD CONSTRAINT material_event_summaries_event_id_fkey FOREIGN KEY (event_id) REFERENCES public.material_events(id) ON DELETE CASCADE;


--
-- Name: material_events material_events_symbol_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.material_events
    ADD CONSTRAINT material_events_symbol_fkey FOREIGN KEY (symbol) REFERENCES public.stocks(symbol);


--
-- Name: news_articles news_articles_symbol_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.news_articles
    ADD CONSTRAINT news_articles_symbol_fkey FOREIGN KEY (symbol) REFERENCES public.stocks(symbol);


--
-- Name: optimization_runs optimization_runs_best_config_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.optimization_runs
    ADD CONSTRAINT optimization_runs_best_config_id_fkey FOREIGN KEY (best_config_id) REFERENCES public.algorithm_configurations(id);


--
-- Name: portfolio_transactions portfolio_transactions_portfolio_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.portfolio_transactions
    ADD CONSTRAINT portfolio_transactions_portfolio_id_fkey FOREIGN KEY (portfolio_id) REFERENCES public.portfolios(id) ON DELETE CASCADE;


--
-- Name: portfolio_value_snapshots portfolio_value_snapshots_portfolio_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.portfolio_value_snapshots
    ADD CONSTRAINT portfolio_value_snapshots_portfolio_id_fkey FOREIGN KEY (portfolio_id) REFERENCES public.portfolios(id) ON DELETE CASCADE;


--
-- Name: portfolios portfolios_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.portfolios
    ADD CONSTRAINT portfolios_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: position_entry_tracking position_entry_tracking_portfolio_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.position_entry_tracking
    ADD CONSTRAINT position_entry_tracking_portfolio_id_fkey FOREIGN KEY (portfolio_id) REFERENCES public.portfolios(id) ON DELETE CASCADE;


--
-- Name: sec_filings sec_filings_symbol_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.sec_filings
    ADD CONSTRAINT sec_filings_symbol_fkey FOREIGN KEY (symbol) REFERENCES public.stocks(symbol);


--
-- Name: social_sentiment social_sentiment_symbol_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.social_sentiment
    ADD CONSTRAINT social_sentiment_symbol_fkey FOREIGN KEY (symbol) REFERENCES public.stocks(symbol);


--
-- Name: stock_metrics stock_metrics_symbol_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.stock_metrics
    ADD CONSTRAINT stock_metrics_symbol_fkey FOREIGN KEY (symbol) REFERENCES public.stocks(symbol);


--
-- Name: strategy_briefings strategy_briefings_portfolio_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.strategy_briefings
    ADD CONSTRAINT strategy_briefings_portfolio_id_fkey FOREIGN KEY (portfolio_id) REFERENCES public.portfolios(id) ON DELETE CASCADE;


--
-- Name: strategy_briefings strategy_briefings_run_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.strategy_briefings
    ADD CONSTRAINT strategy_briefings_run_id_fkey FOREIGN KEY (run_id) REFERENCES public.strategy_runs(id) ON DELETE CASCADE;


--
-- Name: strategy_briefings strategy_briefings_strategy_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.strategy_briefings
    ADD CONSTRAINT strategy_briefings_strategy_id_fkey FOREIGN KEY (strategy_id) REFERENCES public.investment_strategies(id) ON DELETE CASCADE;


--
-- Name: strategy_decisions strategy_decisions_run_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.strategy_decisions
    ADD CONSTRAINT strategy_decisions_run_id_fkey FOREIGN KEY (run_id) REFERENCES public.strategy_runs(id) ON DELETE CASCADE;


--
-- Name: strategy_decisions strategy_decisions_transaction_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.strategy_decisions
    ADD CONSTRAINT strategy_decisions_transaction_id_fkey FOREIGN KEY (transaction_id) REFERENCES public.portfolio_transactions(id) ON DELETE CASCADE;


--
-- Name: strategy_performance strategy_performance_strategy_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.strategy_performance
    ADD CONSTRAINT strategy_performance_strategy_id_fkey FOREIGN KEY (strategy_id) REFERENCES public.investment_strategies(id) ON DELETE CASCADE;


--
-- Name: strategy_runs strategy_runs_strategy_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.strategy_runs
    ADD CONSTRAINT strategy_runs_strategy_id_fkey FOREIGN KEY (strategy_id) REFERENCES public.investment_strategies(id) ON DELETE CASCADE;


--
-- Name: thesis_refresh_queue thesis_refresh_queue_symbol_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.thesis_refresh_queue
    ADD CONSTRAINT thesis_refresh_queue_symbol_fkey FOREIGN KEY (symbol) REFERENCES public.stocks(symbol) ON DELETE CASCADE;


--
-- Name: user_events user_events_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.user_events
    ADD CONSTRAINT user_events_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: watchlist watchlist_symbol_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.watchlist
    ADD CONSTRAINT watchlist_symbol_fkey FOREIGN KEY (symbol) REFERENCES public.stocks(symbol);


--
-- Name: watchlist watchlist_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.watchlist
    ADD CONSTRAINT watchlist_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: weekly_prices weekly_prices_symbol_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lynch
--

ALTER TABLE ONLY public.weekly_prices
    ADD CONSTRAINT weekly_prices_symbol_fkey FOREIGN KEY (symbol) REFERENCES public.stocks(symbol);


--
-- PostgreSQL database dump complete
--



-- Pre-populate default system user
INSERT INTO users (id, google_id, email, name) VALUES (0, $$system_user$$, $$system@lynch.app$$, $$System$$) ON CONFLICT (id) DO NOTHING;

-- Pre-populate default settings
INSERT INTO app_settings (key, value, description) VALUES ($$us_stocks_only$$, $$true$$, $$Filter to show only US stocks (hides country filters in UI)$$) ON CONFLICT (key) DO NOTHING;
INSERT INTO app_settings (key, value, description) VALUES ($$feature_alerts_enabled$$, $$false$$, $$Toggle for Alerts feature (bell icon and agent tool)$$) ON CONFLICT (key) DO NOTHING;
INSERT INTO app_settings (key, value, description) VALUES ($$feature_dashboard_enabled$$, $$false$$, $$Show Dashboard link in navigation sidebar$$) ON CONFLICT (key) DO NOTHING;
