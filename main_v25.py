# main_v25.py - PROJECT TITAN V2.5 PROFESSIONAL FLIGHT HACKER
# 🎯 Industry secrets + Night scanning + One-way combos

import asyncio
import logging
import json
import random
import traceback
from datetime import datetime, timedelta, time as dt_time
from pathlib import Path
from typing import Dict, List, Optional
import sys

# --- MODÜL İÇE AKTARMA (Hata Yönetimi ile) ---
try:
    # V2.5 Modülleri
    from config_v25 import TitanConfig
    from scraper_engine_v25 import ProfessionalFlightScraper
    from intel_center_v25 import FlightHackerIntelCenter
except ImportError as e:
    print(f"UYARI: V2.5 modülleri tam yüklenemedi! ({e})")
    # Kodun çökmemesi için geçici Config sınıfı
    class TitanConfig:
        STATE_FILE = "titan_state_v25.json"
        SCAN_HOURS = (dt_time(2, 0), dt_time(5, 0))
        ALERT_HOURS = (dt_time(9, 0), dt_time(23, 0))
        QUEUE_NIGHT_ALERTS = True
        MIN_SANE_PRICE = 500
        MAX_SANE_PRICE = 50000
        DATE_RANGE_MIN = 30
        DATE_RANGE_MAX = 90
        ROUTES_TO_SCAN = 5
        RANDOM_SLEEP_MIN = 2
        RANDOM_SLEEP_MAX = 5
        SEARCH_STRATEGY = "standard"
        MIN_DISCOUNT_THRESHOLD = 0.20
        ULTRA_DEAL_THRESHOLD = 0.50
        MISTAKE_FARE_THRESHOLD = 0.70
        DATES_PER_ROUTE = 2

# V2.3 Modülleri (Geriye dönük uyumluluk)
try:
    from notifier import TelegramNotifier
    from price_analyzer import PriceAnalyzer
    from visa_checker import VisaChecker
except ImportError:
    # Eğer modüller yoksa dummy (boş) sınıflar oluştur
    class TelegramNotifier:
        def __init__(self, config): pass
        async def send_deals_report(self, deals): return 0
        async def send_error_alert(self, msg): pass
    
    class PriceAnalyzer:
        def __init__(self, min_sane_price, max_sane_price): pass
        def is_sane_price(self, price): return True
    
    class VisaChecker:
        def get_visa_message(self, dest): return ""

# Logging Ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProjectTitanV25:
    """
    PROJECT TITAN V2.5 - PROFESSIONAL FLIGHT HACKER
    """
    
    def __init__(self):
        self.config = TitanConfig()
        
        # Eğer modüller yüklendiyse başlat
        try:
            # Scraper ve Intel modüllerini sadece import başarılıysa kullan
            if 'ProfessionalFlightScraper' in globals():
                self.scraper = ProfessionalFlightScraper(self.config)
                self.intel = FlightHackerIntelCenter(self.config)
            else:
                logger.warning("Scraper modülü bulunamadı, dummy modda çalışıyor.")
                self.scraper = None
        except Exception as e:
            logger.error(f"Modül başlatma hatası: {e}")
            self.scraper = None

        self.notifier = TelegramNotifier(self.config)
        self.price_analyzer = PriceAnalyzer(
            min_sane_price=self.config.MIN_SANE_PRICE,
            max_sane_price=self.config.MAX_SANE_PRICE
        )
        self.visa_checker = VisaChecker()
        
        # Durum Dosyası (State)
        self.state_file = Path(self.config.STATE_FILE)
        self.state = self._load_state()
        self.alert_queue = []
        
        # İstatistikler
        self.stats = {
            'total_routes': 0, 'successful_scans': 0, 'failed_scans': 0,
            'one_way_combos_found': 0, 'alternative_airports_found': 0,
            'ultra_deals': 0, 'mistake_fares': 0, 'total_alerts': 0,
            'queued_alerts': 0, 'scan_times': []
        }
    
    def _load_state(self) -> Dict:
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self._init_state()
        return self._init_state()
    
    def _init_state(self) -> Dict:
        return {
            "price_history": {},
            "last_scan": None,
            "total_scans": 0,
            "last_alerts": {},
            "best_deals_found": [],
            "one_way_combos": []
        }
    
    def _save_state(self):
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"State save failed: {e}")
    
    async def scan_route(self, route: Dict) -> Optional[Dict]:
        if not self.scraper:
            logger.error("Scraper modülü eksik, tarama yapılamıyor.")
            return None
            
        try:
            # Tarihleri Intel Center'dan al veya default kullan
            dates = []
            if hasattr(self, 'intel') and self.intel:
                dates = self.intel._generate_sweet_spot_dates(count=self.config.DATES_PER_ROUTE)
            else:
                # Fallback tarihler
                d1 = datetime.now() + timedelta(days=30)
                d2 = d1 + timedelta(days=7)
                dates = [(d1.strftime('%Y-%m-%d'), d2.strftime('%Y-%m-%d'))]
            
            best_deal = None
            best_price = float('inf')
            
            for dep_date, ret_date in dates:
                logger.info(f"🔍 Scanning: {route.get('origin', 'IST')} → {route.get('destination', 'ESB')} ({dep_date}-{ret_date})")
                
                # Scraper çağrısı
                result = await self.scraper.scrape_flight(
                    origin=route.get('origin', 'IST'),
                    destination=route.get('destination', 'ESB'),
                    departure_date=dep_date,
                    return_date=ret_date
                )
                
                if result and result.get('price'):
                    price = result.get('real_price', result['price'])
                    if price < best_price:
                        best_price = price
                        best_deal = {**route, **result, 'departure_date': dep_date, 'return_date': ret_date}
                        logger.info(f"💎 New best: {price:,.0f} TL")
                
                await asyncio.sleep(1) 
            
            if best_deal:
                self.stats['successful_scans'] += 1
                return best_deal
            
            self.stats['failed_scans'] += 1
            return None
                
        except Exception as e:
            logger.error(f"❌ Route scan error: {e}")
            self.stats['failed_scans'] += 1
            return None

    async def run_intelligence_cycle(self):
        logger.info("🦅 PROJECT TITAN V2.5 BAŞLATILIYOR...")
        
        # Rotaları al
        routes = []
        if hasattr(self, 'intel') and self.intel:
            routes = await self.intel.get_strategic_routes(max_routes=self.config.ROUTES_TO_SCAN)
        else:
            # Fallback rota
            routes = [{'origin': 'IST', 'destination': 'ADB', 'route_type': 'round_trip'}]
            
        self.stats['total_routes'] = len(routes)
        
        deals_found = []
        
        for route in routes:
            deal = await self.scan_route(route)
            if deal:
                deals_found.append(deal)
        
        if deals_found:
            await self.notifier.send_deals_report(deals_found)
            
        self._save_state()
        logger.info("✅ Döngü tamamlandı.")

async def main():
    try:
        titan = ProjectTitanV25()
        await titan.run_intelligence_cycle()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())