-- ABOUTME: Migration to create form144_filings table
-- ABOUTME: Stores parsed Form 144 (Notice of Proposed Sale) filings from SEC EDGAR

CREATE TABLE IF NOT EXISTS form144_filings (
    id SERIAL PRIMARY KEY,
    symbol TEXT NOT NULL REFERENCES stocks(symbol),
    accession_number TEXT NOT NULL,
    filing_date DATE,
    insider_name TEXT,
    insider_cik TEXT,
    relationship TEXT,
    securities_class TEXT,
    shares_to_sell REAL,
    estimated_value REAL,
    approx_sale_date DATE,
    acquisition_nature TEXT,
    is_10b51_plan BOOLEAN DEFAULT false,
    plan_adoption_date DATE,
    filing_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(accession_number, insider_name)
);
