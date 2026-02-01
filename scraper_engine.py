# scraper_engine.py - ULTRA IMPROVED & FIXED Google Flights Scraper
import asyncio
import logging
import random
import re
from typing import Dict, Optional
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)

class ScraperEngine:
    """
    Titan Class Scraper - Fixed URL Structure & Cookie Handling
    """
    
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]

    async def _handle_cookie_consent(self, page):
        """
        Google'ın sinir bozucu Cookie banner'ını kapatır.
        """
        try:
            # "Reject all" veya "Accept all" butonlarını ara
            # Farklı diller için (EN, TR, DE) genel butonları dener
            buttons = [
                "button[aria-label*='Reject all']",
                "button[aria-label*='Tümünü reddet']",
                "span:text('Reject all')",
                "span:text('Tümünü reddet')",
                "span:text('Accept all')",
                "span:text('Kabul et')"
            ]
            
            for selector in buttons:
                if await page.is_visible(selector, timeout=2000):
                    logger.info(f"🍪 Cookie banner bulundu ve kapatılıyor: {selector}")
                    await page.click(selector)
                    await asyncio.sleep(1) # Animasyon için bekle
                    return
        except:
            pass # Banner yoksa devam et

    async def scrape_flight(self, origin: str, destination: str, departure_date: str, return_date: str) -> Optional[Dict]:
        """
        Ana scraping fonksiyonu
        """
        browser = None
        # Doğru Google Flights URL Yapısı (Query Parametreleri ile)
        # hl=en (İngilizce), gl=tr (Türkiye Lokasyonu), curr=TRY (Para Birimi)
        url = (
            f"https://www.google.com/travel/flights?hl=en&gl=tr&curr=TRY"
            f"&q=Flights+to+{destination}+from+{origin}+on+{departure_date}+through+{return_date}"
        )

        try:
            async with async_playwright() as p:
                # Browser'ı başlat
                browser = await p.chromium.launch(
                    headless=True, # Debug için False yapabilirsin ama Actions'da True olmalı
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-gpu'
                    ]
                )
                
                # Context oluştur (User Agent hilesi)
                context = await browser.new_context(
                    user_agent=random.choice(self.user_agents),
                    viewport={'width': 1920, 'height': 1080},
                    locale='en-US',
                    timezone_id='Europe/Istanbul'
                )
                
                page = await context.new_page()
                
                # Anti-detection scriptleri
                await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

                logger.info(f"📍 Navigating to: {url}")
                
                # Sayfaya git (Timeout süresi artırıldı)
                await page.goto(url, timeout=60000, wait_until='domcontentloaded')
                
                # Cookie Banner Kontrolü
                await self._handle_cookie_consent(page)
                
                logger.info("⏳ Waiting for prices to load...")
                
                # Fiyat elementinin yüklenmesini bekle (30 saniye)
                # Google Flights'ta fiyatlar genelde aria-label içinde "Turkish Lira" olarak geçer
                try:
                    await page.wait_for_selector('div[role="main"]', state='visible', timeout=15000)
                    # Scroll yaparak lazy-load tetikle
                    await page.mouse.wheel(0, 500)
                    await asyncio.sleep(3) 
                except:
                    logger.warning("⚠️ Main container geç yüklendi.")

                # Screenshot al (Debug için kritik)
                screenshot_name = f"debug_{origin}_{destination}.png"
                await page.screenshot(path=screenshot_name)
                logger.info(f"📸 Screenshot saved: {screenshot_name}")

                # --- FİYAT ÇEKME STRATEJİLERİ ---
                
                content = await page.content()
                prices = []

                # YÖNTEM 1: Regex ile "TL" veya "TRY" geçen sayıları bul (En garantisi)
                # Örnek: "12,345 TL" veya "TRY 12,345"
                matches = re.findall(r'(\d{1,3}(?:,\d{3})*)\s*(?:TL|TRY)', content)
                for m in matches:
                    clean_price = float(m.replace(',', ''))
                    if clean_price > 500: # 500 TL altı hatalı veridir
                        prices.append(clean_price)

                # YÖNTEM 2: Aria-Label taraması (Google erişilebilirlik etiketleri)
                elements = await page.query_selector_all('[aria-label*="Turkish Lira"]')
                for el in elements:
                    text = await el.get_attribute("aria-label")
                    # Text içinden sayıyı sök
                    nums = re.findall(r'(\d{1,3}(?:,\d{3})*)', text)
                    for n in nums:
                        try:
                            val = float(n.replace(',', ''))
                            if val > 500: prices.append(val)
                        except: pass

                await browser.close()
                
                # Fiyatları temizle ve sırala
                prices = sorted(list(set(prices)))
                
                if prices:
                    cheapest = prices[0]
                    logger.info(f"✅ SUCCESS! Found {len(prices)} prices. Cheapest: {cheapest:,.0f} TL")
                    return {
                        'price': cheapest,
                        'currency': 'TRY',
                        'airline': 'Unknown', # Playwright ile havayolu adı çekmek zor ve gereksiz risk
                        'method': 'titan-playwright',
                        'url': url
                    }
                else:
                    logger.warning(f"⚠️ No prices found. Check {screenshot_name}")
                    return None

        except Exception as e:
            logger.error(f"❌ Scraping error: {e}")
            if browser: await browser.close()
            return None
