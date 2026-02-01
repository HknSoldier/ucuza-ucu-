# scraper_engine.py - FIXED & PRODUCTION READY
import asyncio
import logging
import random
import re
from typing import Dict, Optional
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)

class ScraperEngine:
    """
    Titan Class Scraper - Official Google Flights URL & Smart Selectors
    """
    
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        ]

    async def _handle_cookie_consent(self, page):
        """Çerezleri reddet veya kabul et"""
        try:
            # Google'ın standart butonları
            buttons = [
                "button[aria-label*='Reject all']",
                "button[aria-label*='Tümünü reddet']",
                "button:has-text('Reject all')",
                "button:has-text('Tümünü reddet')",
                "button:has-text('Accept all')",
                "span:has-text('Kabul et')"
            ]
            for selector in buttons:
                if await page.is_visible(selector, timeout=3000):
                    logger.info("🍪 Cookie banner kapatılıyor...")
                    await page.click(selector)
                    await asyncio.sleep(2)
                    return
        except:
            pass

    async def scrape_flight(self, origin: str, destination: str, departure_date: str, return_date: str) -> Optional[Dict]:
        browser = None
        # RESMİ GOOGLE URL'si (En sağlıklısı budur)
        url = (
            f"https://www.google.com/travel/flights?q=Flights+to+{destination}+from+{origin}+on+{departure_date}+through+{return_date}&curr=TRY"
        )

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True, # Actions için True
                    args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
                )
                
                context = await browser.new_context(
                    user_agent=random.choice(self.user_agents),
                    viewport={'width': 1920, 'height': 1080},
                    locale='en-US' # İngilizce zorla ki "TL" parse etmek kolay olsun
                )
                
                page = await context.new_page()
                
                # Bot algılamayı zorlaştır
                await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

                logger.info(f"📍 Navigating to official site: {url}")
                await page.goto(url, timeout=60000, wait_until='domcontentloaded')
                
                # Cookie kapat
                await self._handle_cookie_consent(page)
                
                logger.info("⏳ Waiting for flight results grid...")
                
                # Fiyatların olduğu ana listeyi bekle (Daha uzun süre)
                try:
                    # R15d6c sınıfı genelde uçuş kartlarıdır, aria-label="View flight details" de olabilir
                    await page.wait_for_selector('div[role="main"]', timeout=20000)
                    # Biraz scroll yap ki yüklensin
                    await page.mouse.wheel(0, 800)
                    await asyncio.sleep(5) 
                except:
                    logger.warning("⚠️ Sonuçlar geç yüklendi veya yüklenemedi.")

                # Screenshot al (Hata analizi için şart)
                screenshot_name = f"debug_{origin}_{destination}.png"
                await page.screenshot(path=screenshot_name)
                
                # --- İYİLEŞTİRİLMİŞ FİYAT OKUMA ---
                content = await page.content()
                prices = []

                # 1. Regex ile TRY/TL arama (Sayfadaki metin üzerinden)
                # "TRY 12,345" veya "12,345 TL" formatlarını yakalar
                matches = re.findall(r'(?:TRY|TL)\s?([\d,.]+)|([\d,.]+)\s?(?:TRY|TL)', content)
                
                for m in matches:
                    # Regex grubu hangisi doluysa onu al
                    val_str = m[0] if m[0] else m[1]
                    try:
                        # Virgül ve noktayı temizle
                        clean_price = float(val_str.replace(',', '').replace('.', ''))
                        
                        # FİLTRE: 505 TL gibi saçma rakamları ele (Min 1000 TL)
                        # Uluslararası uçuşlarda 1000 TL altı imkansız
                        if clean_price > 1000: 
                            prices.append(clean_price)
                    except:
                        continue

                # 2. Aria-Label Taraması (Yedek Yöntem)
                elements = await page.query_selector_all('[aria-label*="Turkish Lira"]')
                for el in elements:
                    txt = await el.get_attribute("aria-label")
                    nums = re.findall(r'(\d+[\d,]*)', txt)
                    for n in nums:
                        try:
                            val = float(n.replace(',', ''))
                            if val > 1000: prices.append(val)
                        except: pass

                await browser.close()
                
                # Fiyatları temizle
                prices = sorted(list(set(prices)))
                
                if prices:
                    # En ucuz mantıklı fiyatı al
                    cheapest = prices[0]
                    logger.info(f"✅ SUCCESS! Found valid prices. Cheapest: {cheapest:,.0f} TL")
                    return {
                        'price': cheapest,
                        'currency': 'TRY',
                        'airline': 'Google Flights',
                        'method': 'titan-playwright-v2',
                        'url': url
                    }
                else:
                    logger.warning(f"⚠️ No valid prices found (>1000 TL). Check {screenshot_name}")
                    return None

        except Exception as e:
            logger.error(f"❌ Scraping error: {e}")
            if browser: await browser.close()
            return None
