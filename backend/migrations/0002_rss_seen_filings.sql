-- ABOUTME: Migration to create rss_seen_filings table
-- ABOUTME: Tracks RSS filings we've already processed for deduplication

CREATE TABLE IF NOT EXISTS rss_seen_filings (
    accession_number TEXT PRIMARY KEY,
    form_type TEXT NOT NULL,
    first_seen TIMESTAMPTZ DEFAULT NOW()
);
