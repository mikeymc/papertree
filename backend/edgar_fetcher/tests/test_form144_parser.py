# ABOUTME: Tests for Form 144 XML parsing
# ABOUTME: Validates extraction of insider intent-to-sell data from SEC EDGAR filings

import pytest
from unittest.mock import Mock, patch
from edgar_fetcher.filings import FilingsMixin


# Real Form 144 XML from DraftKings filing (Erik Bradbury, 2026-03-03)
SAMPLE_FORM144_XML = """<?xml version="1.0" encoding="UTF-8"?>
<edgarSubmission xmlns="http://www.sec.gov/edgar/ownership" xmlns:com="http://www.sec.gov/edgar/common">
  <headerData>
    <submissionType>144</submissionType>
    <filerInfo>
      <filer>
        <filerCredentials>
          <cik>0001824092</cik>
          <ccc>XXXXXXXX</ccc>
        </filerCredentials>
      </filer>
      <liveTestFlag>LIVE</liveTestFlag>
    </filerInfo>
  </headerData>
  <formData>
    <issuerInfo>
      <issuerCik>0001883685</issuerCik>
      <issuerName>DraftKings Inc.</issuerName>
      <secFileNumber>001-41379</secFileNumber>
      <issuerAddress>
        <com:street1>222 BERKELEY STREET</com:street1>
        <com:city>BOSTON</com:city>
        <com:stateOrCountry>MA</com:stateOrCountry>
        <com:zipCode>02116</com:zipCode>
      </issuerAddress>
      <issuerContactPhone>(617) 986-6744</issuerContactPhone>
      <nameOfPersonForWhoseAccountTheSecuritiesAreToBeSold>Bradbury Erik</nameOfPersonForWhoseAccountTheSecuritiesAreToBeSold>
      <relationshipsToIssuer>
        <relationshipToIssuer>Officer</relationshipToIssuer>
      </relationshipsToIssuer>
    </issuerInfo>
    <securitiesInformation>
      <securitiesClassTitle>Class A Common</securitiesClassTitle>
      <brokerOrMarketmakerDetails>
        <name>UBS Financial Services Inc.</name>
        <address>
          <com:street1>11 Madison Avenue</com:street1>
          <com:city>New York</com:city>
          <com:stateOrCountry>NY</com:stateOrCountry>
          <com:zipCode>10010</com:zipCode>
        </address>
      </brokerOrMarketmakerDetails>
      <noOfUnitsSold>2883</noOfUnitsSold>
      <aggregateMarketValue>70787.74</aggregateMarketValue>
      <noOfUnitsOutstanding>492991385</noOfUnitsOutstanding>
      <approxSaleDate>03/03/2026</approxSaleDate>
      <securitiesExchangeName>NASDAQ</securitiesExchangeName>
    </securitiesInformation>
    <securitiesToBeSold>
      <securitiesClassTitle>Class A Common</securitiesClassTitle>
      <acquiredDate>03/02/2026</acquiredDate>
      <natureOfAcquisitionTransaction>Vesting of Restricted Stock Units</natureOfAcquisitionTransaction>
      <nameOfPersonfromWhomAcquired>Issuer</nameOfPersonfromWhomAcquired>
      <isGiftTransaction>N</isGiftTransaction>
      <amountOfSecuritiesAcquired>2883</amountOfSecuritiesAcquired>
      <paymentDate>03/02/2026</paymentDate>
      <natureOfPayment>N/A</natureOfPayment>
    </securitiesToBeSold>
    <remarks>Seller represents that the sale reported was made pursuant to a Rule 10b5-1 trading plan.</remarks>
    <noticeSignature>
      <noticeDate>03/03/2026</noticeDate>
      <planAdoptionDates>
        <planAdoptionDate>11/10/2025</planAdoptionDate>
      </planAdoptionDates>
      <signature>/s/ UBS Financial Services Inc, as attorney-in-fact for Erik Bradbury</signature>
    </noticeSignature>
  </formData>
</edgarSubmission>"""

# Form 144 XML without a 10b5-1 plan
SAMPLE_FORM144_NO_PLAN_XML = """<?xml version="1.0" encoding="UTF-8"?>
<edgarSubmission xmlns="http://www.sec.gov/edgar/ownership" xmlns:com="http://www.sec.gov/edgar/common">
  <headerData>
    <submissionType>144</submissionType>
    <filerInfo>
      <filer>
        <filerCredentials>
          <cik>0000999999</cik>
        </filerCredentials>
      </filer>
    </filerInfo>
  </headerData>
  <formData>
    <issuerInfo>
      <issuerCik>0000320193</issuerCik>
      <issuerName>APPLE INC</issuerName>
      <nameOfPersonForWhoseAccountTheSecuritiesAreToBeSold>Cook Timothy</nameOfPersonForWhoseAccountTheSecuritiesAreToBeSold>
      <relationshipsToIssuer>
        <relationshipToIssuer>Director</relationshipToIssuer>
        <relationshipToIssuer>Officer</relationshipToIssuer>
      </relationshipsToIssuer>
    </issuerInfo>
    <securitiesInformation>
      <securitiesClassTitle>Common Stock</securitiesClassTitle>
      <noOfUnitsSold>50000</noOfUnitsSold>
      <aggregateMarketValue>12500000.00</aggregateMarketValue>
      <approxSaleDate>04/15/2026</approxSaleDate>
    </securitiesInformation>
    <securitiesToBeSold>
      <natureOfAcquisitionTransaction>Open Market Purchase</natureOfAcquisitionTransaction>
    </securitiesToBeSold>
    <noticeSignature>
      <noticeDate>03/01/2026</noticeDate>
    </noticeSignature>
  </formData>
</edgarSubmission>"""


class TestParseForm144Filing:
    """Tests for _parse_form144_filing()"""

    @pytest.fixture
    def parser(self):
        """Create a minimal FilingsMixin instance for testing the parser"""
        instance = FilingsMixin.__new__(FilingsMixin)
        instance.headers = {'User-Agent': 'Test'}
        return instance

    def test_extracts_insider_name(self, parser):
        filing = {'filing_date': '2026-03-03', 'accession_number': '0001969223-26-000271',
                  'url': 'https://example.com/doc.xml', 'insider_cik': '0001824092'}
        result = parser._parse_form144_filing('DKNG', filing, SAMPLE_FORM144_XML)

        assert result['insider_name'] == 'Bradbury Erik'

    def test_extracts_insider_cik(self, parser):
        filing = {'filing_date': '2026-03-03', 'accession_number': '0001969223-26-000271',
                  'url': 'https://example.com/doc.xml', 'insider_cik': '0001824092'}
        result = parser._parse_form144_filing('DKNG', filing, SAMPLE_FORM144_XML)

        assert result['insider_cik'] == '0001824092'

    def test_extracts_relationship(self, parser):
        filing = {'filing_date': '2026-03-03', 'accession_number': '0001969223-26-000271',
                  'url': 'https://example.com/doc.xml', 'insider_cik': '0001824092'}
        result = parser._parse_form144_filing('DKNG', filing, SAMPLE_FORM144_XML)

        assert result['relationship'] == 'Officer'

    def test_extracts_multiple_relationships(self, parser):
        filing = {'filing_date': '2026-03-01', 'accession_number': '0000000000-26-000001',
                  'url': 'https://example.com/doc.xml', 'insider_cik': '0000999999'}
        result = parser._parse_form144_filing('AAPL', filing, SAMPLE_FORM144_NO_PLAN_XML)

        assert result['relationship'] == 'Director, Officer'

    def test_extracts_securities_info(self, parser):
        filing = {'filing_date': '2026-03-03', 'accession_number': '0001969223-26-000271',
                  'url': 'https://example.com/doc.xml', 'insider_cik': '0001824092'}
        result = parser._parse_form144_filing('DKNG', filing, SAMPLE_FORM144_XML)

        assert result['securities_class'] == 'Class A Common'
        assert result['shares_to_sell'] == 2883.0
        assert result['estimated_value'] == 70787.74

    def test_extracts_approx_sale_date(self, parser):
        filing = {'filing_date': '2026-03-03', 'accession_number': '0001969223-26-000271',
                  'url': 'https://example.com/doc.xml', 'insider_cik': '0001824092'}
        result = parser._parse_form144_filing('DKNG', filing, SAMPLE_FORM144_XML)

        assert result['approx_sale_date'] == '2026-03-03'

    def test_extracts_acquisition_nature(self, parser):
        filing = {'filing_date': '2026-03-03', 'accession_number': '0001969223-26-000271',
                  'url': 'https://example.com/doc.xml', 'insider_cik': '0001824092'}
        result = parser._parse_form144_filing('DKNG', filing, SAMPLE_FORM144_XML)

        assert result['acquisition_nature'] == 'Vesting of Restricted Stock Units'

    def test_detects_10b51_plan(self, parser):
        filing = {'filing_date': '2026-03-03', 'accession_number': '0001969223-26-000271',
                  'url': 'https://example.com/doc.xml', 'insider_cik': '0001824092'}
        result = parser._parse_form144_filing('DKNG', filing, SAMPLE_FORM144_XML)

        assert result['is_10b51_plan'] is True
        assert result['plan_adoption_date'] == '2025-11-10'

    def test_no_plan_when_absent(self, parser):
        filing = {'filing_date': '2026-03-01', 'accession_number': '0000000000-26-000001',
                  'url': 'https://example.com/doc.xml', 'insider_cik': '0000999999'}
        result = parser._parse_form144_filing('AAPL', filing, SAMPLE_FORM144_NO_PLAN_XML)

        assert result['is_10b51_plan'] is False
        assert result['plan_adoption_date'] is None

    def test_passes_through_filing_metadata(self, parser):
        filing = {'filing_date': '2026-03-03', 'accession_number': '0001969223-26-000271',
                  'url': 'https://example.com/doc.xml', 'insider_cik': '0001824092'}
        result = parser._parse_form144_filing('DKNG', filing, SAMPLE_FORM144_XML)

        assert result['accession_number'] == '0001969223-26-000271'
        assert result['filing_date'] == '2026-03-03'
        assert result['filing_url'] == 'https://example.com/doc.xml'
