# scraper_engine.py - Hybrid Scraping Engine
import asyncio
import logging
import random
from typing import Dict, Optional
import re

# Primary method imports
try:
    from fast_flights import FlightData, Passengers, create_filter, get_flights
    FAST_FLIGHTS_AVAILABLE = True
except ImportError:
    FAST_FLIGHTS_AVAILABLE = False
    logging.warning("fast-flights not available, will use Playwright only")

# Fallback method imports
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

logger = logging.getLogger(__name__)

class ScraperEngine:
    """
    Hybrid scraping engine with two methods:
    1. fast-flights (primary, fast)
    2. Playwright stealth browser (fallback, bulletproof)
    """
    
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
    
    def _get_random_user_agent(self) -> str:
        """Get random user agent for anti-detection"""
        return random.choice(self.user_agents)
    
    async def _scrape_with_fast_flights(self, origin: str, destination: str, 
                                        departure_date: str, return_date: str) -> Optional[Dict]:
        """
        Primary scraping method using fast-flights library
        """
        if not FAST_FLIGHTS_AVAILABLE:
            return None
        
        try:
            logger.info(f"[FAST-FLIGHTS] Scraping {origin} → {destination}")
            
            # Create flight filter
            filter_criteria = create_filter(
                flight_data=[
                    FlightData(
                        date=departure_date,
                        from_airport=origin,
                        to_airport=destination
                    ),
                    FlightData(
                        date=return_date,
                        from_airport=destination,
                        to_airport=origin
                    )
                ],
                trip='round-trip',
                seat='economy',
                passengers=Passengers(adults=1)
            )
            
            # Get flights
            result = get_flights(filter_criteria)
            
            if result and len(result) > 0:
                # Get cheapest flight
                cheapest = min(result, key=lambda x: x.get('price', float('inf')))
                
                price_str = cheapest.get('price', '0')
                # Extract numeric price
                price = float(re.sub(r'[^\d.]', '', str(price_str)))
                
                return {
                    'price': price,
                    'currency': 'TRY',
                    'airline': cheapest.get('name', 'Unknown'),
                    'method': 'fast-flights'
                }
            
            return None
            
        except Exception as e:
            logger.warning(f"[FAST-FLIGHTS] Failed: {e}")
            return None
    
    async def _scrape_with_playwright(self, origin: str, destination: str,
                                     departure_date: str, return_date: str) -> Optional[Dict]:
        """
        Fallback scraping method using Playwright with stealth
        This is the bulletproof method that WILL get the data
        """
        try:
            logger.info(f"[PLAYWRIGHT] Launching stealth browser for {origin} → {destination}")
            
            async with async_playwright() as p:
                # Launch browser with stealth options
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-gpu'
                    ]
                )
                
                # Create context with random user agent
                context = await browser.new_context(
                    user_agent=self._get_random_user_agent(),
                    viewport={'width': 1920, 'height': 1080},
                    locale='tr-TR'
                )
                
                # Remove webdriver flag
                await context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                """)
                
                page = await context.new_page()
                
                # Build Google Flights URL
                url = (
                    f"https://www.google.com/travel/flights?"
                    f"q=Flights%20to%20{destination}%20from%20{origin}%20on%20{departure_date}%20through%20{return_date}"
                    f"&curr=TRY"
                )
                
                logger.info(f"[PLAYWRIGHT] Navigating to: {url}")
                
                # Navigate with timeout
                await page.goto(url, wait_until='networkidle', timeout=60000)
                
                # Random human-like delay
                await asyncio.sleep(random.uniform(2, 4))
                
                # Try multiple selectors for price extraction
                price = None
                selectors = [
                    'div[role="listitem"] span[aria-label*="₺"]',
                    'div.YMlIz.FpEdX span',
                    'span[data-gs*="price"]',
                    'div[jsname] span:has-text("₺")'
                ]
                
                for selector in selectors:
                    try:
                        elements = await page.query_selector_all(selector)
                        if elements:
                            for element in elements:
                                text = await element.text_content()
                                if text and '₺' in text:
                                    # Extract numeric value
                                    price_match = re.search(r'[\d.,]+', text.replace('.', '').replace(',', '.'))
                                    if price_match:
                                        price = float(price_match.group())
                                        logger.info(f"[PLAYWRIGHT] Found price: {price} TL")
                                        break
                        if price:
                            break
                    except Exception as e:
                        continue
                
                # Screenshot for debugging (optional)
                # await page.screenshot(path=f"debug_{origin}_{destination}.png")
                
                await browser.close()
                
                if price:
                    return {
                        'price': price,
                        'currency': 'TRY',
                        'airline': 'Various',
                        'method': 'playwright'
                    }
                
                logger.warning(f"[PLAYWRIGHT] Could not extract price from page")
                return None
                
        except PlaywrightTimeout:
            logger.error("[PLAYWRIGHT] Page load timeout")
            return None
        except Exception as e:
            logger.error(f"[PLAYWRIGHT] Failed: {e}")
            return None
    
    async def scrape_flight(self, origin: str, destination: str,
                           departure_date: str, return_date: str) -> Optional[Dict]:
        """
        Main scraping method with fallback logic
        1. Try fast-flights first (fast, but may fail)
        2. If fails, use Playwright (slower, but bulletproof)
        """
        # Try primary method first
        result = await self._scrape_with_fast_flights(origin, destination, departure_date, return_date)
        
        if result:
            logger.info(f"✅ Success with primary method: {result['price']} TL")
            return result
        
        # Fallback to Playwright
        logger.info("Primary method failed, using Playwright fallback...")
        result = await self._scrape_with_playwright(origin, destination, departure_date, return_date)
        
        if result:
            logger.info(f"✅ Success with Playwright: {result['price']} TL")
            return result
        
        logger.error("❌ Both scraping methods failed")
        return None
