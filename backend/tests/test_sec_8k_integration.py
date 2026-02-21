#!/usr/bin/env python3
"""Integration tests for SEC 8-K client"""

import pytest
from sec_8k_client import SEC8KClient
import time

@pytest.mark.integration
def test_sec_8k_integration(db):
    """Test fetching real 8-K filings for AAPL and saving to database"""
    # Initialize client
    user_agent = "Lynch Stock Screener test@example.com"
    client = SEC8KClient(user_agent)

    # Test with AAPL
    test_symbol = "AAPL"
    # Use a shorter window for testing to be faster, but AAPL files often
    filings = client.fetch_recent_8ks(test_symbol, days_back=90)
    
    if not filings:
        # Fallback to year if necessary
        filings = client.fetch_recent_8ks(test_symbol, days_back=365)

    assert len(filings) > 0, f"No 8-K filings found for {test_symbol} in last year"

    filing = filings[0]
    
    # Verify required fields
    required_fields = ['event_type', 'headline', 'source', 'filing_date',
                      'datetime', 'published_date', 'sec_accession_number',
                      'sec_item_codes', 'content_text']

    for field in required_fields:
        assert field in filing, f"Missing required field: {field}"
        if field != 'content_text':
            assert filing[field] is not None, f"Field {field} is None"

    # Verify content_text extraction quality
    if filing['content_text']:
        content_len = len(filing['content_text'])
        assert content_len > 100, "Content text too short - extraction may have failed"
        assert content_len <= 505000, "Content text too long - truncation may have failed"
        # Check for exhibit content (press release) or item markers (8-K body fallback)
        assert "Exhibit" in filing['content_text'] or "Item" in filing['content_text'] or content_len > 1000, "Content may not have extracted properly"

    # Test database integration
    for f in filings:
        db.save_material_event(test_symbol, f)

    db.flush()
    # Wait for batch commit if necessary, but flush() should handle it in theory
    # although writer loop has its own logic. db.flush() is blocking.

    saved_events = db.get_material_events(test_symbol)
    assert len(saved_events) >= len(filings)

    event = next((e for e in saved_events if e['sec_accession_number'] == filing['sec_accession_number']), None)
    assert event is not None
    assert event['symbol'] == test_symbol
    assert event['sec_accession_number'] == filing['sec_accession_number']
