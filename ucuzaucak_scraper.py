# ucuzaucak_scraper.py - Historical Price Data from ucuzaucak.net
# 📊 90 sayfa geçmiş fiyat verisi toplama motoru

import asyncio
import logging
import re
from typing import Dict, List, Optional
from playwright.async_api import async_playwright
import random

logger = logging.getLogger(__name__)

class UcuzaucakScraper:
    """
    ucuzaucak.net sitesinden geçmiş fiyat verileri toplama
    
    Site: https://ucuzaucak.net/ucak-biletleri/
    90+ sayfa fiyat verisi mevcut
    
    Kullanım:
    - Geçmiş fiyatları analiz et
    - Mevcut fiyatı geçmiş ile karşılaştır
    - Trend analizi yap
    """
    
    def __init__(self, config):
        self.config = config
        self.base_url = "https://ucuzaucak.net/ucak-biletleri"
        self.user_agents = config.USER_AGENTS
        self.cache = {}  # Route-based cache
    
    def _parse_route_from_text(self, text: str) -> Optional[Dict]:
        """
        Metin içinden rota bilgisi çıkar
        
        Örnek: "Ankara - Budapeşte (Aktarmasız)"
        Returns: {origin: "ANK", destination: "BUD", type: "direct"}
        """
        try:
            # Şehir isimlerini havalimanı kodlarına çevir
            city_to_code = {
                # Türkiye
                "İstanbul": "IST",
                "Ankara": "ESB", 
                "İzmir": "ADB",
                "Antalya": "AYT",
                "Trabzon": "TZX",
                "Dalaman": "DLM",
                "Bodrum": "BJV",
                
                # Avrupa
                "Budapeşte": "BUD",
                "Seul": "ICN",
                "Bükreş": "OTP",
                "Sofya": "SOF",
                "Berlin": "BER",
                "Paris": "CDG",
                "Londra": "LHR",
                "Amsterdam": "AMS",
                "Roma": "FCO",
                "Barselona": "BCN",
                "Madrid": "MAD",
                "Viyana": "VIE",
                "Prag": "PRG",
                "Varşova": "WAW",
                
                # Asya/Ortadoğu
                "Singapur": "SIN",
                "Dubai": "DXB",
                "Abu Dhabi": "AUH",
                "Doha": "DOH",
                "Bangkok": "BKK",
                "Tokyo": "NRT",
                "Seul": "ICN",
                
                # Afrika
                "Hurghada": "HRG",
                "Sharm El Sheikh": "SSH",
                "Kahire": "CAI",
                
                # Amerika
                "New York": "JFK",
                "Los Angeles": "LAX",
                "Miami": "MIA",
                "Boston": "BOS",
                "San Francisco": "SFO",
                "Chicago": "ORD",
                "Seattle": "SEA",
                
                # Diğer
                "Melbourne": "MEL",
                "Sidney": "SYD",
            }
            
            # Regex ile şehir isimlerini çıkar
            parts = text.split("-")
            if len(parts) >= 2:
                origin_city = parts[0].strip()
                dest_city = parts[1].split("(")[0].strip()
                
                origin = city_to_code.get(origin_city, origin_city[:3].upper())
                destination = city_to_code.get(dest_city, dest_city[:3].upper())
                
                return {
                    "origin": origin,
                    "destination": destination,
                    "route_key": f"{origin}-{destination}"
                }
        except Exception as e:
            logger.error(f"Route parse error: {e}")
        
        return None
    
    def _parse_price(self, price_text: str) -> Optional[float]:
        """
        Fiyat metninden sayısal değer çıkar
        
        Örnek: "3.160 TL" → 3160.0
        """
        try:
            # Sadece rakamları al
            clean = re.sub(r'[^\d]', '', price_text)
            if clean:
                return float(clean)
        except:
            pass
        return None
    
    async def scrape_page(self, page_num: int = 1) -> List[Dict]:
        """
        Tek sayfa fiyat verisi çek
        
        Returns: [{route, price, date_info, ...}]
        """
        browser = None
        url = f"{self.base_url}?page={page_num}"
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-dev-shm-usage']
                )
                
                context = await browser.new_context(
                    user_agent=random.choice(self.user_agents),
                    viewport={'width': 1920, 'height': 1080}
                )
                
                page = await context.new_page()
                
                logger.info(f"📊 ucuzaucak.net scraping: Page {page_num}")
                
                await page.goto(url, timeout=30000, wait_until='domcontentloaded')
                await asyncio.sleep(random.uniform(2, 4))
                
                # Fiyat kartlarını bul
                deals = []
                
                # ucuzaucak.net için özel selector'lar
                # Site yapısına göre güncellendi
                
                # Önce ana container'ı bul
                main_container = await page.query_selector('main, .main-content, #content')
                
                if not main_container:
                    logger.warning("Main container not found, trying body")
                    main_container = await page.query_selector('body')
                
                # Kart selector'ları (birden fazla alternatif)
                card_selectors = [
                    'article',  # Genelde article tag kullanılır
                    '.deal-card',
                    '.flight-card',
                    '[class*="card"]',
                    'div[class*="flight"]',
                    'div[class*="deal"]'
                ]
                
                cards = []
                for selector in card_selectors:
                    if main_container:
                        cards = await main_container.query_selector_all(selector)
                    else:
                        cards = await page.query_selector_all(selector)
                    
                    if len(cards) > 0:
                        logger.info(f"Using selector: {selector}")
                        break
                
                logger.info(f"Found {len(cards)} cards on page {page_num}")
                
                for idx, card in enumerate(cards):
                    try:
                        # Rota bilgisi - birden fazla selector dene
                        route_text = None
                        route_selectors = ['h3', 'h2', '.title', '.route', '[class*="title"]', 'a']
                        
                        for selector in route_selectors:
                            route_elem = await card.query_selector(selector)
                            if route_elem:
                                route_text = await route_elem.text_content()
                                if route_text and len(route_text.strip()) > 5:
                                    break
                        
                        if not route_text:
                            logger.debug(f"Card {idx}: No route text found")
                            continue
                        
                        route_info = self._parse_route_from_text(route_text)
                        if not route_info:
                            logger.debug(f"Card {idx}: Could not parse route from '{route_text}'")
                            continue
                        
                        # Fiyat bilgisi - geniş arama
                        price = None
                        
                        # Önce card içindeki tüm metni al
                        card_text = await card.text_content()
                        
                        # Regex ile TL/TRY içeren sayıları bul
                        price_matches = re.findall(r'(\d{1,3}(?:[.,]\d{3})*)\s*(?:TL|TRY)', card_text)
                        
                        if price_matches:
                            # İlk bulunan fiyatı kullan
                            price_text = price_matches[0]
                            price = self._parse_price(price_text)
                        
                        if not price:
                            # Alternatif: price class'ına bak
                            price_selectors = ['.price', '[class*="price"]', 'span', 'strong']
                            for selector in price_selectors:
                                price_elem = await card.query_selector(selector)
                                if price_elem:
                                    price_text = await price_elem.text_content()
                                    price = self._parse_price(price_text)
                                    if price and price > 100:
                                        break
                        
                        if not price or price < 100 or price > 500000:
                            logger.debug(f"Card {idx}: Invalid price: {price}")
                            continue
                        
                        # Tarih bilgisi (varsa)
                        date_info = "N/A"
                        date_selectors = ['.date', '[class*="date"]', 'time', 'span']
                        for selector in date_selectors:
                            date_elem = await card.query_selector(selector)
                            if date_elem:
                                date_text = await date_elem.text_content()
                                if date_text and len(date_text.strip()) > 3:
                                    date_info = date_text.strip()
                                    break
                        
                        deal = {
                            **route_info,
                            "price": price,
                            "date_info": date_info,
                            "source": "ucuzaucak.net",
                            "page": page_num
                        }
                        
                        deals.append(deal)
                        logger.debug(f"✅ Card {idx}: {route_info['route_key']} @ {price:,.0f} TL")
                        
                    except Exception as e:
                        logger.debug(f"Card {idx} parse error: {e}")
                        continue
                
                await browser.close()
                
                logger.info(f"✅ Scraped {len(deals)} deals from page {page_num}")
                return deals
                
        except Exception as e:
            logger.error(f"❌ ucuzaucak.net scrape error (page {page_num}): {e}")
            if browser:
                await browser.close()
            return []
    
    async def scrape_multiple_pages(self, max_pages: int = 5) -> List[Dict]:
        """
        Birden fazla sayfa tarama
        
        Args:
            max_pages: Maksimum kaç sayfa taranacak (default: 5)
        
        Returns: Tüm deal'lerin listesi
        """
        all_deals = []
        
        for page_num in range(1, max_pages + 1):
            try:
                deals = await self.scrape_page(page_num)
                all_deals.extend(deals)
                
                # Sayfalar arası bekleme (anti-detection)
                await asyncio.sleep(random.uniform(3, 6))
                
            except Exception as e:
                logger.error(f"Error scraping page {page_num}: {e}")
                continue
        
        logger.info(f"📊 Total deals scraped: {len(all_deals)} from {max_pages} pages")
        return all_deals
    
    def aggregate_by_route(self, deals: List[Dict]) -> Dict[str, Dict]:
        """
        Rotaya göre fiyatları grupla ve istatistik çıkar
        
        Returns: {
            "IST-BUD": {
                "prices": [3160, 3500, 3200],
                "min": 3160,
                "max": 3500,
                "avg": 3286,
                "count": 3
            }
        }
        """
        route_stats = {}
        
        for deal in deals:
            route_key = deal.get("route_key")
            price = deal.get("price")
            
            if not route_key or not price:
                continue
            
            if route_key not in route_stats:
                route_stats[route_key] = {
                    "prices": [],
                    "origin": deal.get("origin"),
                    "destination": deal.get("destination")
                }
            
            route_stats[route_key]["prices"].append(price)
        
        # İstatistik hesapla
        for route_key, data in route_stats.items():
            prices = data["prices"]
            data["min"] = min(prices)
            data["max"] = max(prices)
            data["avg"] = sum(prices) / len(prices)
            data["count"] = len(prices)
            data["median"] = sorted(prices)[len(prices) // 2]
        
        return route_stats
    
    def compare_with_historical(self, current_price: float, route_key: str, 
                               historical_stats: Dict) -> Dict:
        """
        Mevcut fiyatı geçmiş verilerle karşılaştır
        
        Returns: {
            "is_good_deal": bool,
            "percentile": float,  # 0-100 arası (0 = en ucuz, 100 = en pahalı)
            "vs_min": float,  # Min fiyata göre fark (%)
            "vs_avg": float,  # Ortalamaya göre fark (%)
            "recommendation": str
        }
        """
        if route_key not in historical_stats:
            return {
                "is_good_deal": None,
                "percentile": None,
                "recommendation": "Geçmiş veri yok, karşılaştırma yapılamıyor"
            }
        
        stats = historical_stats[route_key]
        hist_min = stats["min"]
        hist_max = stats["max"]
        hist_avg = stats["avg"]
        
        # Percentile hesapla
        prices = sorted(stats["prices"])
        rank = sum(1 for p in prices if p <= current_price)
        percentile = (rank / len(prices)) * 100
        
        # Karşılaştırmalar
        vs_min = ((current_price - hist_min) / hist_min) * 100
        vs_avg = ((current_price - hist_avg) / hist_avg) * 100
        
        # Karar
        if percentile <= 10:
            recommendation = "🔥 MÜKEMMEL FİYAT - Geçmişte en ucuz %10'luk dilimde!"
            is_good_deal = True
        elif percentile <= 25:
            recommendation = "💎 ÇOK İYİ FİYAT - Geçmişte en ucuz %25'lik dilimde!"
            is_good_deal = True
        elif percentile <= 50:
            recommendation = "🟡 ORTALAMA FİYAT - Beklersen daha ucuz bulabilirsin"
            is_good_deal = False
        else:
            recommendation = "🔴 PAHALI - Geçmişte çok daha ucuz olmuş, BEKLEME!"
            is_good_deal = False
        
        return {
            "is_good_deal": is_good_deal,
            "percentile": percentile,
            "vs_min": vs_min,
            "vs_avg": vs_avg,
            "hist_min": hist_min,
            "hist_avg": hist_avg,
            "hist_max": hist_max,
            "recommendation": recommendation
        }
