# scraper_engine.py - Advanced Google Flights Scraper
import asyncio
import logging
import random
from typing import Dict, Optional
import re
from datetime import datetime

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

logger = logging.getLogger(__name__)

class ScraperEngine:
    """
    Advanced Google Flights scraper with human-like behavior
    Bypasses bot detection with realistic patterns
    """
    
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
        ]
        
        self.viewport_sizes = [
            {'width': 1920, 'height': 1080},
            {'width': 1366, 'height': 768},
            {'width': 1536, 'height': 864},
        ]
    
    def _get_random_user_agent(self) -> str:
        return random.choice(self.user_agents)
    
    def _get_random_viewport(self) -> Dict:
        return random.choice(self.viewport_sizes)
    
    async def _human_like_delay(self, min_sec: float = 0.5, max_sec: float = 2.0):
        await asyncio.sleep(random.uniform(min_sec, max_sec))
    
    async def scrape_flight(self, origin: str, destination: str,
                           departure_date: str, return_date: str) -> Optional[Dict]:
        """
        Main scraping method - scrapes Google Flights like a human
        """
        browser = None
        try:
            logger.info(f"🔍 [SCRAPER] {origin} → {destination} ({departure_date} to {return_date})")
            
            async with async_playwright() as p:
                # Launch browser with stealth
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-web-security',
                        '--disable-gpu',
                    ]
                )
                
                # Create context
                viewport = self._get_random_viewport()
                context = await browser.new_context(
                    user_agent=self._get_random_user_agent(),
                    viewport=viewport,
                    locale='tr-TR',
                    timezone_id='Europe/Istanbul',
                )
                
                # Anti-detection script
                await context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5]
                    });
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['tr-TR', 'tr', 'en-US', 'en']
                    });
                    window.chrome = { runtime: {} };
                """)
                
                page = await context.new_page()
                
                # Build URL
                url = (
                    f"https://www.google.com/travel/flights?"
                    f"q=Flights%20to%20{destination}%20from%20{origin}%20"
                    f"on%20{departure_date}%20through%20{return_date}"
                    f"&curr=TRY&hl=tr"
                )
                
                # Navigate
                try:
                    await page.goto(url, wait_until='domcontentloaded', timeout=60000)
                except PlaywrightTimeout:
                    logger.warning("⚠️ Navigation timeout, continuing...")
                
                # Wait for page to load
                await self._human_like_delay(3, 5)
                
                # Wait for results
                try:
                    await page.wait_for_selector(
                        'div[role="listitem"], span[aria-label*="₺"]',
                        timeout=20000
                    )
                except:
                    pass
                
                await self._human_like_delay(2, 3)
                
                # Extract prices - multiple strategies
                prices = []
                
                # Strategy 1: aria-label
                try:
                    elements = await page.query_selector_all('span[aria-label*="₺"], span[aria-label*="TL"]')
                    for elem in elements[:15]:
                        text = await elem.get_attribute('aria-label')
                        if text:
                            nums = re.findall(r'[\d.]+', text.replace(',', ''))
                            for n in nums:
                                try:
                                    price = float(n)
                                    if 1000 < price < 500000:
                                        prices.append(price)
                                except:
                                    pass
                except:
                    pass
                
                # Strategy 2: Text content
                if len(prices) < 3:
                    try:
                        all_text = await page.content()
                        matches = re.findall(r'(\d{1,3}(?:\.\d{3})*)\s*₺', all_text)
                        for match in matches[:20]:
                            try:
                                price = float(match.replace('.', ''))
                                if 1000 < price < 500000:
                                    prices.append(price)
                            except:
                                pass
                    except:
                        pass
                
                await browser.close()
                
                if prices:
                    cheapest = min(prices)
                    logger.info(f"✅ Found {len(prices)} prices, cheapest: {cheapest:,.0f} TL")
                    
                    return {
                        'price': cheapest,
                        'currency': 'TRY',
                        'airline': 'Various',
                        'method': 'google-flights',
                        'url': url
                    }
                else:
                    logger.warning("⚠️ No prices found")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Scraping error: {e}")
            if browser:
                try:
                    await browser.close()
                except:
                    pass
            return None
