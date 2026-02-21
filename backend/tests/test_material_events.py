#!/usr/bin/env python3
"""Tests for material events database methods"""

import pytest
from datetime import datetime
import time

def test_material_events_crud(db):
    """Test saving and retrieving material events"""
    # Test data - simulate an 8-K filing with content_text
    test_symbol = "AAPL"
    test_content = """Item 5.02 Departure of Directors or Certain Officers; Election of Directors

On November 15, 2024, the Board of Directors of Apple Inc. appointed Jane Smith as Chief Financial Officer, effective December 1, 2024. Ms. Smith will succeed John Doe, who announced his retirement.

Ms. Smith, age 45, has served as Senior Vice President of Finance at XYZ Corporation since 2020. Prior to that, she held various leadership positions at ABC Company from 2015 to 2020.

This filing contains forward-looking statements that involve risks and uncertainties. Actual results may differ materially from those projected.

[Content truncated for length]"""

    test_event = {
        'event_type': '8k',
        'headline': 'SEC 8-K Filing - Test Event',
        'description': 'Test material event for Apple Inc.',
        'source': 'SEC',
        'url': 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000320193',
        'filing_date': datetime(2024, 11, 15).date(),
        'datetime': int(datetime(2024, 11, 15).timestamp()),
        'published_date': datetime(2024, 11, 15).isoformat(),
        'sec_accession_number': '0000320193-24-000001',
        'sec_item_codes': ['5.02', '8.01'],
        'content_text': test_content
    }

    # Test 1: Save material event
    db.save_material_event(test_symbol, test_event)
    db.flush()  # Ensure write queue is processed

    # Test 2: Retrieve material events
    events = db.get_material_events(test_symbol)
    assert len(events) > 0, "No events retrieved after saving!"

    # Find our specific test event by accession number
    event = next((e for e in events if e['sec_accession_number'] == test_event['sec_accession_number']), None)
    assert event is not None, f"Test event with accession {test_event['sec_accession_number']} not found!"

    # Verify data matches
    assert event['symbol'] == test_symbol
    assert event['event_type'] == '8k'
    assert event['sec_accession_number'] == test_event['sec_accession_number']
    assert event['sec_item_codes'] == test_event['sec_item_codes']
    assert 'content_text' in event
    assert event['content_text'] == test_content

    # Test 3: Get cache status
    cache_status = db.get_material_events_cache_status(test_symbol)
    assert cache_status is not None
    assert cache_status['event_count'] >= 1

    # Test 4: Test with limit
    limited_events = db.get_material_events(test_symbol, limit=1)
    assert len(limited_events) == 1

    # Test 5: Test upsert (conflict resolution)
    updated_event = test_event.copy()
    updated_event['headline'] = 'SEC 8-K Filing - Updated Test Event'
    updated_event['content_text'] = 'Updated content text with new information'
    db.save_material_event(test_symbol, updated_event)
    db.flush()

    events_after_update = db.get_material_events(test_symbol)
    updated_event_retrieved = next((e for e in events_after_update if e['sec_accession_number'] == test_event['sec_accession_number']), None)
    
    assert updated_event_retrieved is not None
    assert updated_event_retrieved['headline'] == 'SEC 8-K Filing - Updated Test Event'
    assert updated_event_retrieved['content_text'] == 'Updated content text with new information'

    # Test 6: Test with non-existent symbol
    assert len(db.get_material_events("NONEXISTENT")) == 0
    assert db.get_material_events_cache_status("NONEXISTENT") is None
