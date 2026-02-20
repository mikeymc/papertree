# ABOUTME: MarketBeat earnings call transcript scraper using Requests and BeautifulSoup
# ABOUTME: Fetches full transcripts with Q&A content for any stock covered by Quartr

import asyncio
import logging
import re
from datetime import datetime
from typing import Dict, Any, Optional, List
import requests
import cloudscraper
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class TranscriptScraper:
    """
    Scraper for earnings call transcripts from MarketBeat.
    
    MarketBeat provides free transcripts powered by Quartr.
    Uses Requests/BeautifulSoup to parse the content.
    """
    
    BASE_URL = "https://www.marketbeat.com"
    EARNINGS_URL_TEMPLATE = "{base}/stocks/{exchange}/{symbol}/earnings/"
    REQUEST_DELAY = 1.0  # Seconds between requests to avoid rate limiting
    TIMEOUT = 30
    
    def __init__(self):
        """Initialize the transcript scraper."""
        self._last_request_time = 0
        self._session = cloudscraper.create_scraper()
        self._session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Referer': 'https://www.marketbeat.com/',
        })

    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        self._session.close()

    async def restart_browser(self):
        """No-op for compatibility with old playwrigh scraper."""
        logger.info("[TranscriptScraper] Resetting session...")
        self._session.close()
        self._session = cloudscraper.create_scraper()
        self._session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        })

    async def _rate_limit(self):
        """Enforce rate limiting between requests."""
        current_time = asyncio.get_event_loop().time()
        time_since_last = current_time - self._last_request_time
        
        if time_since_last < self.REQUEST_DELAY:
            await asyncio.sleep(self.REQUEST_DELAY - time_since_last)
        
        self._last_request_time = asyncio.get_event_loop().time()
    
    def _get_exchange(self, symbol: str) -> str:
        """
        Determine the exchange for a symbol.
        Default to NASDAQ, but could be extended with a lookup.
        """
        nyse_symbols = {'JPM', 'BAC', 'WMT', 'JNJ', 'PG', 'KO', 'DIS', 'V', 'MA', 'HD'}
        if symbol.upper() in nyse_symbols:
            return 'NYSE'
        return 'NASDAQ'
    
    async def fetch_latest_transcript(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Fetch the most recent earnings call transcript for a symbol.
        """
        return await asyncio.to_thread(self._fetch_sync, symbol)

    def _fetch_sync(self, symbol: str) -> Optional[Dict[str, Any]]:
        try:
            import time
            current_time = time.time()
            time_since_last = current_time - self._last_request_time
            if time_since_last < self.REQUEST_DELAY:
                time.sleep(self.REQUEST_DELAY - time_since_last)
            self._last_request_time = time.time()

            exchange = self._get_exchange(symbol)
            earnings_url = self.EARNINGS_URL_TEMPLATE.format(
                base=self.BASE_URL,
                exchange=exchange,
                symbol=symbol.upper()
            )
            
            logger.info(f"[TranscriptScraper] [{symbol}] Fetching earnings page: {earnings_url}")
            resp = self._session.get(earnings_url, timeout=self.TIMEOUT)
            resp.raise_for_status()
            
            soup = BeautifulSoup(resp.text, 'lxml')
            
            transcript_link = None
            for a in soup.find_all('a', href=True):
                text = a.get_text(strip=True).lower()
                if 'conference call transcript' in text or '#transcript' in a['href']:
                    href = a['href']
                    if href.startswith('/'):
                        transcript_link = self.BASE_URL + href
                    else:
                        transcript_link = href
                    break
                    
            if not transcript_link:
                logger.warning(f"[TranscriptScraper] [{symbol}] No transcript link found")
                return None
                
            logger.info(f"[TranscriptScraper] [{symbol}] Fetching transcript page: {transcript_link}")
            current_time = time.time()
            time_since_last = current_time - self._last_request_time
            if time_since_last < self.REQUEST_DELAY:
                time.sleep(self.REQUEST_DELAY - time_since_last)
            self._last_request_time = time.time()
            
            t_resp = self._session.get(transcript_link, timeout=self.TIMEOUT)
            t_resp.raise_for_status()
            
            t_soup = BeautifulSoup(t_resp.text, 'lxml')
            return self._extract_transcript(t_soup, symbol, transcript_link)
            
        except requests.RequestException as e:
            if resp is not None and resp.status_code in (403, 401):
                logger.error(f"[TranscriptScraper] [{symbol}] Access denied (Cloudflare/Bot detection): {e}")
            else:
                logger.error(f"[TranscriptScraper] [{symbol}] Network error: {e}")
            return None
        except Exception as e:
            logger.error(f"[TranscriptScraper] [{symbol}] ERROR: {e}")
            return None

    def _extract_transcript(self, soup: BeautifulSoup, symbol: str, url: str) -> Dict[str, Any]:
        result = {
            'symbol': symbol.upper(),
            'quarter': None,
            'fiscal_year': None,
            'earnings_date': None,
            'transcript_text': '',
            'has_qa': False,
            'participants': [],
            'source_url': url
        }
        
        try:
            title = soup.title.string if soup.title else ''
            quarter_match = re.search(r'(Q[1-4])\s+(\d{4})', title)
            if quarter_match:
                result['quarter'] = quarter_match.group(1)
                result['fiscal_year'] = int(quarter_match.group(2))
            
            date_match = re.search(r'(\d{4})-(\d{1,2})-(\d{1,2})', url)
            if date_match:
                result['earnings_date'] = f"{date_match.group(1)}-{date_match.group(2).zfill(2)}-{date_match.group(3).zfill(2)}"
            
            # Identify transcript container
            container = soup.find('div', id='transcriptPresentation')
            if container:
                turns = []
                sections = container.find_all('section', class_=re.compile(r'transcript-line-(left|right)'))
                for section in sections:
                    speaker_div = section.find('div', class_='transcript-line-speaker')
                    name, title_str, timestamp = '', '', ''
                    if speaker_div:
                        name_el = speaker_div.find('div', class_='font-weight-bold')
                        if name_el:
                            clone = BeautifulSoup(str(name_el), 'lxml')
                            sec = clone.find(class_='secondary-title')
                            if sec:
                                sec.decompose()
                            name = clone.get_text(strip=True)
                        
                        title_el = speaker_div.find('div', class_='secondary-title')
                        if title_el:
                            title_str = title_el.get_text(strip=True)
                            
                        time_el = speaker_div.find('time')
                        if time_el:
                            timestamp = time_el.get_text(strip=True)
                            
                    content_el = section.find('p')
                    content = content_el.get_text(strip=True) if content_el else ''
                    
                    if name and content:
                        header = f"[{timestamp}] {name}"
                        if title_str:
                            header += f" ({title_str})"
                        turns.append(header + "\n" + content)
                        
                transcript_text = "\n\n".join(turns)
            else:
                fallback_container = soup.find(class_=re.compile(r'transcript-content|TranscriptContent', re.I))
                if fallback_container:
                    transcript_text = fallback_container.get_text(separator='\n\n', strip=True)
                else:
                    main = soup.find('main') or soup.find('article')
                    if main:
                        transcript_text = main.get_text(separator='\n', strip=True)
                    else:
                        transcript_text = soup.body.get_text(separator='\n', strip=True) if soup.body else ''

            result['transcript_text'] = self._clean_transcript_text(transcript_text)
            
            text_lower = result['transcript_text'].lower()
            result['has_qa'] = ('question' in text_lower and 'answer' in text_lower) or 'q&a' in text_lower
            
            participants_match = re.search(r'Participants[\s\S]*?(?=Presentation|Call Participants|$)', transcript_text, re.I)
            if participants_match:
                lines = participants_match.group(0).split('\n')
                participants = []
                for line in lines:
                    line = line.strip()
                    if ' - ' in line or ', ' in line:
                        name = line.split(' - ')[0].split(',')[0].strip()
                        if 2 < len(name) < 50:
                            participants.append(name)
                result['participants'] = participants[:20]
                
        except Exception as e:
            logger.error(f"[TranscriptScraper] Error parsing transcript: {e}")
            
        return result

    def _clean_transcript_text(self, text: str) -> str:
        lines = text.split('\n')
        cleaned_lines = []
        skip_patterns = [
            'sign up', 'sign in', 'subscribe', 'newsletter',
            'advertisement', 'sponsored', 'cookie', 'privacy policy',
            'terms of service', 'contact us', 'about us'
        ]
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            line_lower = line.lower()
            if any(pattern in line_lower for pattern in skip_patterns):
                continue
            
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)

async def fetch_transcript(symbol: str) -> Optional[Dict[str, Any]]:
    async with TranscriptScraper() as scraper:
        return await scraper.fetch_latest_transcript(symbol)

if __name__ == '__main__':
    import sys
    
    async def main():
        symbol = sys.argv[1] if len(sys.argv) > 1 else 'AAPL'
        print(f"Fetching transcript for {symbol}...")
        
        result = await fetch_transcript(symbol)
        
        if result:
            print(f"\nSymbol: {result['symbol']}")
            print(f"Quarter: {result['quarter']} {result['fiscal_year']}")
            print(f"Date: {result['earnings_date']}")
            print(f"Has Q&A: {result['has_qa']}")
            print(f"Participants: {result['participants'][:5]}")
            print(f"Transcript length: {len(result['transcript_text']):,} chars")
            print(f"\nFirst 1000 chars:")
            print(result['transcript_text'][:1000])
        else:
            print("No transcript found")
    
    asyncio.run(main())
