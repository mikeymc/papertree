# ABOUTME: Tests for SEC RSS client
# ABOUTME: Validates RSS feed parsing and CIK-to-ticker mapping

import pytest
from unittest.mock import Mock, patch, MagicMock
from sec.sec_rss_client import SECRSSClient


class TestSECRSSClient:
    """Tests for SECRSSClient"""

    @pytest.fixture
    def client(self):
        """Create test SEC RSS client"""
        return SECRSSClient("Test User Agent test@example.com")

    @pytest.fixture
    def sample_rss_response(self):
        """Sample RSS feed XML response"""
        return """<?xml version="1.0" encoding="ISO-8859-1" ?>
                      <feed xmlns="http://www.w3.org/2005/Atom">
                      <title>Latest Filings</title>
                      <entry>
                      <title>8-K - APPLE INC (0000320193) (Filer)</title>
                      <updated>2024-01-28T17:30:59-05:00</updated>
                      </entry>
                      <entry>
                      <title>8-K - MICROSOFT CORP (0000789019) (Filer)</title>
                      <updated>2024-01-28T17:29:54-05:00</updated>
                      </entry>
                      <entry>
                      <title>8-K - ALPHABET INC (0001652044) (Filer)</title>
                      <updated>2024-01-28T17:28:57-05:00</updated>
                      </entry>
                </feed>"""
                
    @pytest.fixture
    def sample_cik_mapping(self):
        """Sample CIK-to-ticker mapping"""
        return {
            "0": {
                "cik_str": 320193,
                "ticker": "AAPL",
                "title": "Apple Inc."
            },
            "1": {
                "cik_str": 789019,
                "ticker": "MSFT",
                "title": "Microsoft Corp"
            },
            "2": {
                "cik_str": 1652044,
                "ticker": "GOOGL",
                "title": "Alphabet Inc."
            }
        }

    def test_client_initializes_with_agent_and_headers(self, client):
        """Test client initializes correctly"""
        assert client.user_agent == "Test User Agent test@example.com"
        assert client.headers == {'User-Agent': "Test User Agent test@example.com"}
        assert client._cik_to_ticker_cache is None

    def test_form_type_mappings(self, client):
        """Test that form types are correctly mapped"""
        assert SECRSSClient.FORM_TYPE_MAPPING['8-K'] == '8-K'
        assert SECRSSClient.FORM_TYPE_MAPPING['10-K'] == '10-K'
        assert SECRSSClient.FORM_TYPE_MAPPING['10-Q'] == '10-Q'
        assert SECRSSClient.FORM_TYPE_MAPPING['FORM4'] == '4'

    @patch('sec.sec_rss_client.requests.get')
    def test_makes_request_to_right_url_with_headers_and_timeout(self, mock_get, client, sample_rss_response, test_db):
        rss_mock = Mock()
        rss_mock.content = sample_rss_response.encode('utf-8')
        rss_mock.raise_for_status = Mock()

        mock_get.side_effect = rss_mock

        client.get_tickers_with_new_filings_paginated('8-K', None, test_db)

        RSS_BASE_URL = "https://www.sec.gov/cgi-bin/browse-edgar"
        rss_form_type = "8-K"
        start = 0
        batch_size = 100
        url = f"{RSS_BASE_URL}?action=getcurrent&type={rss_form_type}&start={start}&count={batch_size}&output=atom"
        mock_get.assert_called_with(url, client.headers, 10)

    @patch('sec.sec_rss_client.requests.get')
    def test_rss_fetch_when_error_returns_empty_set(self, mock_get, client, test_db):
        """Test handling of RSS fetch errors"""
        mock_get.side_effect = Exception("Network error")

        result = client.get_tickers_with_new_filings_paginated('8-K', None, test_db)
        assert result == set()

    @pytest.fixture
    def sample_rss_with_ids(self):
        """Sample RSS response with accession numbers in ID tags"""
        return """<?xml version="1.0" encoding="ISO-8859-1" ?>
<feed xmlns="http://www.w3.org/2005/Atom">
<title>Latest Filings</title>
<entry>
<title>8-K - APPLE INC (0000320193) (Filer)</title>
<id>urn:tag:sec.gov,2008:accession-number=0001234567-26-001111</id>
</entry>
<entry>
<title>8-K - MICROSOFT CORP (0000789019) (Filer)</title>
<id>urn:tag:sec.gov,2008:accession-number=0001234567-26-002222</id>
</entry>
<entry>
<title>8-K - ALPHABET INC (0001652044) (Filer)</title>
<id>urn:tag:sec.gov,2008:accession-number=0001234567-26-003333</id>
</entry>
</feed>"""

    @patch('sec.sec_rss_client.requests.get')
    def test_paginated_single_page(self, mock_get, client, sample_rss_with_ids, sample_cik_mapping):
        """Test pagination with single page (all new filings)"""
        # Page 1 RSS response
        rss_mock = Mock()
        rss_mock.content = sample_rss_with_ids.encode('utf-8')
        rss_mock.raise_for_status = Mock()

        # Page 2 - empty (end of feed)
        empty_rss = """<?xml version="1.0" encoding="ISO-8859-1" ?>
<feed xmlns="http://www.w3.org/2005/Atom">
</feed>"""
        rss_mock2 = Mock()
        rss_mock2.content = empty_rss.encode('utf-8')
        rss_mock2.raise_for_status = Mock()

        # Mock CIK mapping
        mapping_mock = Mock()
        mapping_mock.json.return_value = sample_cik_mapping
        mapping_mock.raise_for_status = Mock()

        # Mock database (no filings exist)
        mock_db = Mock()
        mock_db.filing_exists.return_value = False

        mock_get.side_effect = [rss_mock, rss_mock2, mapping_mock]

        # Execute
        known_tickers = {'AAPL', 'MSFT', 'GOOGL'}
        result = client.get_tickers_with_new_filings_paginated('8-K', known_tickers=known_tickers, db=mock_db)

        # Verify
        assert result == {'AAPL', 'MSFT', 'GOOGL'}
        assert mock_db.filing_exists.call_count == 3  # Checked all 3 filings

    @patch('sec.sec_rss_client.requests.get')
    def test_paginated_stop_on_known_filing(self, mock_get, client, sample_cik_mapping):
        """Test pagination stops when hitting a known filing"""
        # Page 1: 2 new filings
        page1_rss = """<?xml version="1.0" encoding="ISO-8859-1" ?>
<feed xmlns="http://www.w3.org/2005/Atom">
<entry>
<title>8-K - APPLE INC (0000320193) (Filer)</title>
<id>urn:tag:sec.gov,2008:accession-number=0001234567-26-001111</id>
</entry>
<entry>
<title>8-K - MICROSOFT CORP (0000789019) (Filer)</title>
<id>urn:tag:sec.gov,2008:accession-number=0001234567-26-002222</id>
</entry>
<entry>
<title>8-K - ALPHABET INC (0001652044) (Filer)</title>
<id>urn:tag:sec.gov,2008:accession-number=0001234567-26-003333</id>
</entry>
</feed>"""

        # Mock RSS response
        rss_mock = Mock()
        rss_mock.content = page1_rss.encode('utf-8')
        rss_mock.raise_for_status = Mock()

        # Mock CIK mapping
        mapping_mock = Mock()
        mapping_mock.json.return_value = sample_cik_mapping
        mapping_mock.raise_for_status = Mock()

        # Mock database - third filing exists
        mock_db = Mock()
        def filing_exists_side_effect(acc_num, form_type, ticker=None):
            return acc_num == '0001234567-26-003333'  # Third filing exists
        mock_db.filing_exists.side_effect = filing_exists_side_effect

        mock_get.side_effect = [rss_mock, mapping_mock]

        # Execute
        known_tickers = {'AAPL', 'MSFT', 'GOOGL'}
        result = client.get_tickers_with_new_filings_paginated('8-K', known_tickers=known_tickers, db=mock_db)

        # Verify - should only return first 2 tickers (stopped on 3rd)
        assert result == {'AAPL', 'MSFT'}
        assert 'GOOGL' not in result
        assert mock_db.filing_exists.call_count == 3  # Checked until hitting known

    @patch('sec.sec_rss_client.requests.get')
    def test_paginated_multiple_pages(self, mock_get, client, sample_cik_mapping):
        """Test pagination across multiple pages"""
        # Page 1
        page1_rss = """<?xml version="1.0" encoding="ISO-8859-1" ?>
<feed xmlns="http://www.w3.org/2005/Atom">
<entry>
<title>8-K - APPLE INC (0000320193) (Filer)</title>
<id>urn:tag:sec.gov,2008:accession-number=0001111111-26-000001</id>
</entry>
</feed>"""

        # Page 2
        page2_rss = """<?xml version="1.0" encoding="ISO-8859-1" ?>
<feed xmlns="http://www.w3.org/2005/Atom">
<entry>
<title>8-K - MICROSOFT CORP (0000789019) (Filer)</title>
<id>urn:tag:sec.gov,2008:accession-number=0002222222-26-000002</id>
</entry>
</feed>"""

        # Page 3 - empty (end of feed)
        page3_rss = """<?xml version="1.0" encoding="ISO-8859-1" ?>
<feed xmlns="http://www.w3.org/2005/Atom">
</feed>"""

        # Mock responses
        rss_mock1 = Mock()
        rss_mock1.content = page1_rss.encode('utf-8')
        rss_mock1.raise_for_status = Mock()

        rss_mock2 = Mock()
        rss_mock2.content = page2_rss.encode('utf-8')
        rss_mock2.raise_for_status = Mock()

        rss_mock3 = Mock()
        rss_mock3.content = page3_rss.encode('utf-8')
        rss_mock3.raise_for_status = Mock()

        mapping_mock = Mock()
        mapping_mock.json.return_value = sample_cik_mapping
        mapping_mock.raise_for_status = Mock()

        # Mock database (no filings exist)
        mock_db = Mock()
        mock_db.filing_exists.return_value = False

        mock_get.side_effect = [rss_mock1, rss_mock2, rss_mock3, mapping_mock]

        # Execute
        known_tickers = {'AAPL', 'MSFT'}
        result = client.get_tickers_with_new_filings_paginated('8-K', known_tickers=known_tickers, db=mock_db)

        # Verify - should get both tickers from 2 pages
        assert result == {'AAPL', 'MSFT'}
        assert mock_db.filing_exists.call_count == 2

    @patch('sec.sec_rss_client.requests.get')
    def test_paginated_unknown_form_type(self, mock_get, client):
        """Test pagination with unknown form type"""
        mock_db = Mock()
        result = client.get_tickers_with_new_filings_paginated('UNKNOWN-FORM', known_tickers=set(), db=mock_db)
        assert result == set()
        mock_get.assert_not_called()

    @patch('sec.sec_rss_client.requests.get')
    def test_paginated_error_handling(self, mock_get, client):
        """Test pagination handles errors gracefully"""
        mock_get.side_effect = Exception("Network error")
        mock_db = Mock()

        result = client.get_tickers_with_new_filings_paginated('8-K', known_tickers=set(), db=mock_db)
        assert result == set()

    def test_form144_in_form_type_mapping(self, client):
        """Test that FORM144 is mapped to '144' for RSS feed"""
        assert SECRSSClient.FORM_TYPE_MAPPING['FORM144'] == '144'

    @pytest.fixture
    def form144_rss_with_both_entries(self):
        """Form 144 RSS XML with paired Reporting and Subject entries"""
        return """<?xml version="1.0" encoding="ISO-8859-1" ?>
<feed xmlns="http://www.w3.org/2005/Atom">
<title>Latest Filings</title>
<entry>
<title>144 - John Smith (0000111111) (Reporting)</title>
<id>urn:tag:sec.gov,2008:accession-number=0001234567-26-144001</id>
</entry>
<entry>
<title>144 - APPLE INC (0000320193) (Subject)</title>
<id>urn:tag:sec.gov,2008:accession-number=0001234567-26-144001</id>
</entry>
<entry>
<title>144 - Jane Doe (0000222222) (Reporting)</title>
<id>urn:tag:sec.gov,2008:accession-number=0001234567-26-144002</id>
</entry>
<entry>
<title>144 - MICROSOFT CORP (0000789019) (Subject)</title>
<id>urn:tag:sec.gov,2008:accession-number=0001234567-26-144002</id>
</entry>
</feed>"""

    @patch('sec.sec_rss_client.requests.get')
    def test_form144_only_collects_subject_ciks(self, mock_get, client, form144_rss_with_both_entries, sample_cik_mapping):
        """Test that Form 144 processing only collects CIKs from Subject entries"""
        rss_mock = Mock()
        rss_mock.content = form144_rss_with_both_entries.encode('utf-8')
        rss_mock.raise_for_status = Mock()

        empty_rss = """<?xml version="1.0" encoding="ISO-8859-1" ?>
<feed xmlns="http://www.w3.org/2005/Atom">
</feed>"""
        rss_mock2 = Mock()
        rss_mock2.content = empty_rss.encode('utf-8')
        rss_mock2.raise_for_status = Mock()

        mapping_mock = Mock()
        mapping_mock.json.return_value = sample_cik_mapping
        mapping_mock.raise_for_status = Mock()

        mock_db = Mock()
        mock_db.filing_exists.return_value = False

        mock_get.side_effect = [rss_mock, rss_mock2, mapping_mock]

        known_tickers = {'AAPL', 'MSFT'}
        result = client.get_tickers_with_new_filings_paginated('FORM144', known_tickers=known_tickers, db=mock_db)

        # Should map company CIKs (Subject) to tickers
        assert result == {'AAPL', 'MSFT'}

    @patch('sec.sec_rss_client.requests.get')
    def test_form144_skips_reporting_entries(self, mock_get, client, form144_rss_with_both_entries, sample_cik_mapping):
        """Test that insider (Reporting) CIKs are NOT added to results"""
        rss_mock = Mock()
        rss_mock.content = form144_rss_with_both_entries.encode('utf-8')
        rss_mock.raise_for_status = Mock()

        empty_rss = """<?xml version="1.0" encoding="ISO-8859-1" ?>
<feed xmlns="http://www.w3.org/2005/Atom">
</feed>"""
        rss_mock2 = Mock()
        rss_mock2.content = empty_rss.encode('utf-8')
        rss_mock2.raise_for_status = Mock()

        # Add insider CIKs to mapping to prove they'd match if not filtered
        cik_mapping = dict(sample_cik_mapping)
        cik_mapping["99"] = {"cik_str": 111111, "ticker": "INSIDER1", "title": "John Smith"}
        cik_mapping["100"] = {"cik_str": 222222, "ticker": "INSIDER2", "title": "Jane Doe"}

        mapping_mock = Mock()
        mapping_mock.json.return_value = cik_mapping
        mapping_mock.raise_for_status = Mock()

        mock_db = Mock()
        mock_db.filing_exists.return_value = False

        mock_get.side_effect = [rss_mock, rss_mock2, mapping_mock]

        # Include insider "tickers" in known set to prove filtering works
        known_tickers = {'AAPL', 'MSFT', 'INSIDER1', 'INSIDER2'}
        result = client.get_tickers_with_new_filings_paginated('FORM144', known_tickers=known_tickers, db=mock_db)

        # Insider CIKs should NOT appear in results
        assert 'INSIDER1' not in result
        assert 'INSIDER2' not in result
        # Only company (Subject) CIKs should appear
        assert result == {'AAPL', 'MSFT'}
