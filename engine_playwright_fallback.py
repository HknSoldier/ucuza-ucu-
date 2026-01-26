"""
SNIPER V20 - GHOST PROTOCOL
ADVANCED ENGINE: Playwright Fallback Method

This is the ULTIMATE fallback when fast-flights fails.
Uses headless browser automation with anti-detection.

⚠️ WARNING: 
- Slower than fast-flights (adds 30-60s per search)
- Requires more resources
- Higher ban risk (mitigated with delays)
- Only use if fast-flights is not working

To enable: Uncomment playwright in requirements.txt
"""

import asyncio
import random
import logging
from typing import Optional, Dict
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PlaywrightFlightScraper:
    """
    Browser-based Google Flights scraper using Playwright
    HTML-agnostic design: Uses multiple selectors and fallbacks
    """
    
    # Multiple selector strategies (if one breaks, try others)
    PRICE_SELECTORS = [
        'div.YMlIz',  # Primary price container
        '[data-gs*="price"]',  # Data attribute
        'span[aria-label*="price"]',  # Aria label
        'div[class*="price"]',  # Generic class
    ]
    
    AIRLINE_SELECTORS = [
        'div.sSHqwe span',
        '[data-gs*="airline"]',
        'span[aria-label*="airline"]',
    ]
    
    TIME_SELECTORS = [
        'span.eoY5cb',
        '[data-gs*="time"]',
        'span[aria-label*="departure"]',
    ]
    
    def __init__(self):
        self.browser = None
        self.context = None
    
    async def initialize(self):
        """Initialize Playwright browser"""
        try:
            from playwright.async_api import async_playwright
            
            self.playwright = await async_playwright().start()
            
            # Launch with stealth settings
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                ]
            )
            
            # Create context with realistic settings
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='en-US',
                timezone_id='America/New_York',
            )
            
            logger.info("✅ Playwright browser initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Playwright initialization failed: {e}")
            return False
    
    async def close(self):
        """Close browser"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
    
    async def _extract_with_fallback(self, page, selectors: list, attribute: str = 'textContent') -> Optional[str]:
        """Try multiple selectors until one works"""
        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    if attribute == 'textContent':
                        return await element.text_content()
                    else:
                        return await element.get_attribute(attribute)
            except:
                continue
        return None
    
    async def search_flight(self, origin: str, dest: str, date: str, 
                           return_date: Optional[str], currency: str) -> Optional[Dict]:
        """
        Search Google Flights with browser automation
        HTML-AGNOSTIC: Uses multiple selector strategies
        """
        try:
            page = await self.context.new_page()
            
            # Build Google Flights URL
            base = 'https://www.google.com/travel/flights'
            
            if return_date:
                # Round trip
                url = f"{base}?tfs=CBwQAhooEgoyMDI2LTAxLTE1agcIARID{origin}cgcIARID{dest}GgoyMDI2LTAxLTIyagcIARID{dest}cgcIARID{origin}cAE&curr={currency}"
            else:
                # One way
                url = f"{base}?tfs=CBwQAhoeEgoyMDI2LTAxLTE1agcIARID{origin}cgcIARID{dest}QAE&curr={currency}"
            
            logger.info(f"   🌐 Loading Google Flights...")
            
            # Navigate with realistic behavior
            await page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Wait for content to load (with multiple strategies)
            await asyncio.sleep(random.uniform(3, 6))
            
            # Try to wait for flight results
            try:
                await page.wait_for_selector('li.pIav2d', timeout=10000)
            except:
                logger.warning("   ⚠️ Flight results took longer than expected")
            
            # Scroll to simulate human behavior
            await page.evaluate('window.scrollTo(0, 500)')
            await asyncio.sleep(random.uniform(1, 2))
            
            # Extract price with fallback selectors
            price_text = await self._extract_with_fallback(page, self.PRICE_SELECTORS)
            
            if not price_text:
                logger.warning("   ⚠️ Could not extract price")
                await page.close()
                return None
            
            # Clean price text
            price_str = ''.join(c for c in price_text if c.isdigit() or c == '.')
            try:
                price = float(price_str)
            except:
                logger.warning(f"   ⚠️ Could not parse price: {price_text}")
                await page.close()
                return None
            
            # Extract airline
            airline = await self._extract_with_fallback(page, self.AIRLINE_SELECTORS)
            if not airline:
                airline = "Multiple Airlines"
            
            await page.close()
            
            return {
                'price': price,
                'currency': currency,
                'airline': airline.strip(),
                'method': 'playwright-browser'
            }
            
        except Exception as e:
            logger.error(f"   ❌ Playwright search failed: {e}")
            try:
                await page.close()
            except:
                pass
            return None
    
    async def search_with_retry(self, origin: str, dest: str, date: str,
                                return_date: Optional[str], currency: str, 
                                max_retries: int = 2) -> Optional[Dict]:
        """Search with automatic retries"""
        for attempt in range(max_retries):
            result = await self.search_flight(origin, dest, date, return_date, currency)
            if result:
                return result
            
            if attempt < max_retries - 1:
                wait_time = random.uniform(5, 10)
                logger.info(f"   🔄 Retry {attempt + 1}/{max_retries} in {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
        
        return None


# Synchronous wrapper for compatibility with main code
def search_flight_with_playwright(origin: str, dest: str, date: str,
                                  return_date: Optional[str], currency: str) -> Optional[Dict]:
    """
    Synchronous wrapper for Playwright scraper
    Use this in engine.py as METHOD 3
    """
    async def run():
        scraper = PlaywrightFlightScraper()
        if await scraper.initialize():
            result = await scraper.search_with_retry(origin, dest, date, return_date, currency)
            await scraper.close()
            return result
        return None
    
    try:
        return asyncio.run(run())
    except Exception as e:
        logger.error(f"❌ Playwright wrapper failed: {e}")
        return None


# TEST CODE
if __name__ == "__main__":
    # Test single search
    result = search_flight_with_playwright('IST', 'LON', '2026-02-01', '2026-02-08', 'USD')
    
    if result:
        print(f"\n✅ Success!")
        print(f"   Price: {result['price']} {result['currency']}")
        print(f"   Airline: {result['airline']}")
    else:
        print("\n❌ Search failed")
