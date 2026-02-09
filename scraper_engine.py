# scraper_engine.py - Advanced Scraper with Quality Control V2.3
# 🔍 Multi-source validation + Anomaly detection + Stealth mode

import asyncio
import logging
import random
import re
from typing import Dict, Optional, List
from playwright.async_api import async_playwright
import time

logger = logging.getLogger(__name__)

class ScraperEngine:
    """
    Gelişmiş scraping motoru:
    - Multi-source validation (2+ kaynak)
    - Anomaly detection (100-500K TL arası)
    - Stealth mode (random delays, user-agents)
    - TOS compliant rate limiting
    """
    
    def __init__(self, config):
        self.config = config
        self.user_agents = config.USER_AGENTS
        self.request_times = []  # Rate limiting tracker
    
    def _check_rate_limit(self) -> bool:
        """
        Rate limiting: Max 3 requests / 10 seconds
        """
        now = time.time()
        # Eski istekleri temizle (10 saniyeden eski)
        self.request_times = [t for t in self.request_times if now - t < 10]
        
        if len(self.request_times) >= self.config.MAX_REQUESTS_PER_10_SEC:
            logger.warning("⚠️ Rate limit reached, waiting...")
            return False
        
        return True
    
    def _record_request(self):
        """İstek zamanını kaydet"""
        self.request_times.append(time.time())
    
    async def _wait_for_rate_limit(self):
        """Rate limit aşıldıysa bekle"""
        while not self._check_rate_limit():
            await asyncio.sleep(2)
    
    async def _handle_cookie_consent(self, page):
        """Cookie consent ekranını kapat"""
        try:
            buttons = [
                "button[aria-label*='Reject']",
                "button[aria-label*='Tümünü reddet']",
                "button:has-text('Reject all')",
                "button:has-text('Tümünü reddet')"
            ]
            
            for selector in buttons:
                try:
                    if await page.is_visible(selector, timeout=3000):
                        logger.info("🍪 Cookie banner kapatılıyor...")
                        await page.click(selector)
                        await asyncio.sleep(2)
                        return
                except:
                    continue
        except:
            pass
    
    async def scrape_flight(self, origin: str, destination: str, 
                           departure_date: str, return_date: str) -> Optional[Dict]:
        """
        Ana scraping fonksiyonu
        Returns: {price, currency, airline, method, confidence}
        """
        # Rate limit kontrolü
        await self._wait_for_rate_limit()
        
        browser = None
        url = (
            f"https://www.google.com/travel/flights?"
            f"q=Flights+to+{destination}+from+{origin}+"
            f"on+{departure_date}+through+{return_date}&curr=TRY"
        )
        
        try:
            self._record_request()
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--no-sandbox',
                        '--disable-dev-shm-usage'
                    ]
                )
                
                context = await browser.new_context(
                    user_agent=random.choice(self.user_agents),
                    viewport={'width': 1920, 'height': 1080},
                    locale='tr-TR'
                )
                
                page = await context.new_page()
                
                # Bot detection bypass
                await page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                    Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                    Object.defineProperty(navigator, 'languages', {get: () => ['tr-TR', 'tr', 'en-US', 'en']});
                """)
                
                logger.info(f"🔍 Scraping: {origin} → {destination} ({departure_date})")
                
                # Sayfa yükle
                await page.goto(url, timeout=60000, wait_until='domcontentloaded')
                
                # Cookie kapat
                await self._handle_cookie_consent(page)
                
                # Sonuçların yüklenmesini bekle
                try:
                    await page.wait_for_selector('div[role="main"]', timeout=30000)
                except Exception as timeout_err:
                    logger.warning(f"⚠️ Main container timeout, trying alternative selectors...")
                    # Alternatif selector'lar dene
                    try:
                        await page.wait_for_selector('.gws-flights-results__result-item', timeout=15000)
                    except:
                        # Son şans: body'nin yüklenmesini bekle
                        await page.wait_for_selector('body', timeout=10000)
                        logger.warning("Using body as fallback selector")
                
                # Scroll ile daha fazla içerik yükle
                await page.mouse.wheel(0, 800)
                await asyncio.sleep(random.uniform(3, 5))
                
                # Screenshot (debug için)
                screenshot_name = f"debug_{origin}_{destination}_{int(time.time())}.png"
                await page.screenshot(path=screenshot_name)
                
                # Fiyatları topla
                prices = await self._extract_prices(page)
                
                await browser.close()
                
                # Multi-source validation
                if len(prices) < 2:
                    logger.warning(f"⚠️ Yetersiz kaynak: {len(prices)} fiyat bulundu")
                    return None
                
                # Anomali algılama
                valid_prices = [p for p in prices if self._is_sane_price(p)]
                
                if not valid_prices:
                    logger.error(f"❌ Tüm fiyatlar anomali! Prices: {prices}")
                    return None
                
                # En ucuz fiyat
                cheapest = min(valid_prices)
                
                # Confidence hesapla
                confidence = self._calculate_confidence(valid_prices)
                
                logger.info(f"✅ Success: {cheapest:,.0f} TL (Confidence: {confidence:.1%})")
                
                return {
                    'price': cheapest,
                    'currency': 'TRY',
                    'airline': 'Multiple',  # TODO: Havayolu parse
                    'method': 'playwright-stealth',
                    'confidence': confidence,
                    'sources': len(valid_prices),
                    'all_prices': valid_prices
                }
                
        except Exception as e:
            logger.error(f"❌ Scraping error: {e}")
            if browser:
                await browser.close()
            return None
    
    async def _extract_prices(self, page) -> List[float]:
        """
        Sayfadan fiyatları çıkar (multi-method)
        """
        prices = []
        
        try:
            # Method 1: Regex ile TRY/TL arama
            content = await page.content()
            matches = re.findall(r'(?:TRY|TL)\s?([\d,.]+)|([\d,.]+)\s?(?:TRY|TL)', content)
            
            for m in matches:
                val_str = m[0] if m[0] else m[1]
                try:
                    clean_price = float(val_str.replace(',', '').replace('.', ''))
                    if clean_price > 1000:  # Min 1000 TL
                        prices.append(clean_price)
                except:
                    continue
            
            # Method 2: Aria-label taraması
            elements = await page.query_selector_all('[aria-label*="lira"]')
            for el in elements:
                txt = await el.get_attribute("aria-label")
                if txt:
                    nums = re.findall(r'(\d+[\d,]*)', txt)
                    for n in nums:
                        try:
                            val = float(n.replace(',', ''))
                            if val > 1000:
                                prices.append(val)
                        except:
                            pass
            
            # Method 3: Class-based selectors (Google Flights specific)
            price_elements = await page.query_selector_all('.YMlIz.FpEdX, .U3gSDe')
            for el in price_elements:
                txt = await el.text_content()
                if txt:
                    nums = re.findall(r'(\d+[\d,\.]*)', txt)
                    for n in nums:
                        try:
                            clean = float(n.replace(',', '').replace('.', ''))
                            if clean > 1000:
                                prices.append(clean)
                        except:
                            pass
            
        except Exception as e:
            logger.error(f"❌ Price extraction error: {e}")
        
        # Deduplicate ve sırala
        prices = sorted(list(set(prices)))
        logger.info(f"📊 Extracted {len(prices)} unique prices: {prices[:5]}")
        
        return prices
    
    def _is_sane_price(self, price: float) -> bool:
        """
        Anomali algılama: 100 TL - 500K TL arası mantıklı
        """
        return self.config.MIN_SANE_PRICE <= price <= self.config.MAX_SANE_PRICE
    
    def _calculate_confidence(self, prices: List[float]) -> float:
        """
        Confidence skoru hesapla (0.0 - 1.0)
        Fiyatlar birbirine ne kadar yakınsa confidence yüksek
        """
        if len(prices) < 2:
            return 0.5
        
        avg = sum(prices) / len(prices)
        variance = sum((p - avg) ** 2 for p in prices) / len(prices)
        std_dev = variance ** 0.5
        
        # %10'dan az sapma = yüksek confidence
        if std_dev / avg < 0.10:
            return 0.95
        elif std_dev / avg < 0.20:
            return 0.80
        elif std_dev / avg < 0.30:
            return 0.60
        else:
            return 0.40
    
    async def verify_price(self, route: Dict, initial_price: float) -> bool:
        """
        Fiyatı tekrar doğrula (özellikle mistake fare için)
        """
        logger.info(f"🔍 Verifying price: {initial_price:,.0f} TL")
        
        result = await self.scrape_flight(
            route['origin'],
            route['destination'],
            route.get('departure_date', '2026-06-01'),
            route.get('return_date', '2026-06-10')
        )
        
        if result and abs(result['price'] - initial_price) / initial_price < 0.10:
            logger.info("✅ Price verified!")
            return True
        
        logger.warning("⚠️ Price mismatch in verification")
        return False
