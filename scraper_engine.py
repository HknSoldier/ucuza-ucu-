# scraper_engine.py - ULTRA IMPROVED Google Flights Scraper
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
    Ultra-improved Google Flights scraper
    Uses multiple strategies to GUARANTEE price extraction
    """
    
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        ]
    
    async def scrape_flight(self, origin: str, destination: str,
                           departure_date: str, return_date: str) -> Optional[Dict]:
        """
        Main scraping method with ULTRA aggressive price extraction
        """
        browser = None
        try:
            logger.info(f"🔍 [SCRAPER] {origin} → {destination} ({departure_date} to {return_date})")
            
            async with async_playwright() as p:
                # Launch browser
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                    ]
                )
                
                # Create context
                context = await browser.new_context(
                    user_agent=random.choice(self.user_agents),
                    viewport={'width': 1920, 'height': 1080},
                    locale='tr-TR',
                )
                
                # Anti-detection
                await context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                """)
                
                page = await context.new_page()
                
                # Build URL
                url = (
                    f"https://www.google.com/travel/flights?"
                    f"q=Flights%20to%20{destination}%20from%20{origin}%20"
                    f"on%20{departure_date}%20through%20{return_date}"
                    f"&curr=TRY"
                )
                
                logger.info(f"📍 Navigating to Google Flights...")
                
                # Navigate
                await page.goto(url, wait_until='networkidle', timeout=60000)
                
                # CRITICAL: Wait longer for prices to load
                logger.info(f"⏳ Waiting for prices to load...")
                await asyncio.sleep(8)  # Longer wait!
                
                # Scroll to trigger lazy loading
                await page.evaluate("window.scrollTo(0, 500)")
                await asyncio.sleep(2)
                await page.evaluate("window.scrollTo(0, 0)")
                await asyncio.sleep(2)
                
                # Take screenshot for debugging
                screenshot_name = f"debug_{origin}_{destination}.png"
                await page.screenshot(path=screenshot_name, full_page=True)
                logger.info(f"📸 Screenshot saved: {screenshot_name}")
                
                # Extract ALL text from page
                page_text = await page.content()
                
                # STRATEGY 1: Find all Turkish Lira prices with regex
                prices = []
                
                # Pattern 1: Numbers before ₺ symbol
                pattern1 = r'(\d{1,3}(?:\.\d{3})*)\s*₺'
                matches1 = re.findall(pattern1, page_text)
                for match in matches1:
                    try:
                        price = float(match.replace('.', ''))
                        if 1000 < price < 500000:  # Reasonable range
                            prices.append(price)
                            logger.info(f"💰 Found price (₺): {price:,.0f} TL")
                    except:
                        pass
                
                # Pattern 2: TL or TRY suffix
                pattern2 = r'(\d{1,3}(?:\.\d{3})*)\s*(?:TL|TRY)'
                matches2 = re.findall(pattern2, page_text, re.IGNORECASE)
                for match in matches2:
                    try:
                        price = float(match.replace('.', ''))
                        if 1000 < price < 500000:
                            prices.append(price)
                            logger.info(f"💰 Found price (TL): {price:,.0f} TL")
                    except:
                        pass
                
                # Pattern 3: aria-label attributes
                aria_elements = await page.query_selector_all('[aria-label]')
                for elem in aria_elements[:50]:
                    aria_label = await elem.get_attribute('aria-label')
                    if aria_label and ('₺' in aria_label or 'lira' in aria_label.lower()):
                        nums = re.findall(r'\d{1,3}(?:\.\d{3})*', aria_label)
                        for num in nums:
                            try:
                                price = float(num.replace('.', ''))
                                if 1000 < price < 500000:
                                    prices.append(price)
                                    logger.info(f"💰 Found price (aria): {price:,.0f} TL")
                            except:
                                pass
                
                # Pattern 4: Look for flight price divs
                price_divs = await page.query_selector_all('div[jsname], div[data-test-id*="price"], span[data-gs]')
                for div in price_divs[:30]:
                    text = await div.text_content()
                    if text:
                        nums = re.findall(r'\d{1,3}(?:\.\d{3})+', text)
                        for num in nums:
                            try:
                                price = float(num.replace('.', ''))
                                if 1000 < price < 500000:
                                    prices.append(price)
                                    logger.info(f"💰 Found price (div): {price:,.0f} TL")
                            except:
                                pass
                
                await browser.close()
                
                # Remove duplicates and sort
                prices = list(set(prices))
                prices.sort()
                
                if prices:
                    cheapest = prices[0]
                    logger.info(f"✅ SUCCESS! Found {len(prices)} unique prices, cheapest: {cheapest:,.0f} TL")
                    logger.info(f"📊 All prices: {[f'{p:,.0f}' for p in prices[:5]]}")
                    
                    return {
                        'price': cheapest,
                        'currency': 'TRY',
                        'airline': 'Various',
                        'method': 'google-flights',
                        'prices_found': len(prices),
                        'url': url
                    }
                else:
                    logger.warning(f"⚠️ No prices found - check screenshot: {screenshot_name}")
                    logger.warning(f"🔗 URL: {url}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Scraping error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            if browser:
                try:
                    await browser.close()
                except:
                    pass
            return None
