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
                "İstanbul": "IST",
                "Ankara": "ANK", 
                "İzmir": "ADB",
                "Antalya": "AYT",
                "Budapeşte": "BUD",
                "Seul": "ICN",
                "Bükreş": "OTP",
                "Hurghada": "HRG",
                "Singapur": "SIN",
                "Berlin": "BER",
                # Daha fazla eklenebilir
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
                
                # Sayfa yapısına göre selector (örnek)
                # Gerçek HTML yapısına göre güncellenmeli
                cards = await page.query_selector_all('div.flight-card, div.deal-card')
                
                if not cards:
                    # Alternatif selector
                    cards = await page.query_selector_all('[class*="flight"], [class*="deal"]')
                
                logger.info(f"Found {len(cards)} cards on page {page_num}")
                
                for card in cards:
                    try:
                        # Rota bilgisi
                        route_elem = await card.query_selector('h3, .route-title, .flight-route')
                        if route_elem:
                            route_text = await route_elem.text_content()
                            route_info = self._parse_route_from_text(route_text)
                            
                            if not route_info:
                                continue
                        else:
                            continue
                        
                        # Fiyat bilgisi
                        price_elem = await card.query_selector('.price, [class*="price"]')
                        if price_elem:
                            price_text = await price_elem.text_content()
                            price = self._parse_price(price_text)
                            
                            if not price or price < 100 or price > 500000:
                                continue
                        else:
                            continue
                        
                        # Tarih bilgisi (varsa)
                        date_elem = await card.query_selector('.date, [class*="date"]')
                        date_info = await date_elem.text_content() if date_elem else "N/A"
                        
                        deal = {
                            **route_info,
                            "price": price,
                            "date_info": date_info.strip(),
                            "source": "ucuzaucak.net",
                            "page": page_num
                        }
                        
                        deals.append(deal)
                        
                    except Exception as e:
                        logger.debug(f"Card parse error: {e}")
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
