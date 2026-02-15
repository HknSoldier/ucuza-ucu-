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
    print(f"KRİTİK HATA: V2.5 modülleri bulunamadı! ({e})")
    print("Lütfen config_v25.py, scraper_engine_v25.py ve intel_center_v25.py dosyalarının repoda olduğundan emin olun.")
    # Kodun çökmemesi için geçici dummy sınıflar (Sadece dosya kontrolü aşaması için)
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
    # Eğer modüller yoksa dummy (boş) sınıflar oluştur ki kod hata vermesin
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
        
        # Eğer modüller yüklendiyse başlat, yoksa hata verme
        try:
            self.scraper = ProfessionalFlightScraper(self.config)
            self.intel = FlightHackerIntelCenter(self.config)
        except NameError:
            logger.error("V2.5 Modülleri eksik, bot başlatılamıyor.")
            return

        self.notifier = TelegramNotifier(self.config)
        self.price_analyzer = PriceAnalyzer(
            min_sane_price=self.config.MIN_SANE_PRICE,
            max_sane_price=self.config.MAX_SANE_PRICE
        )
        self.visa_checker = VisaChecker()
        
        # Durum Dosyası (State)
        self.state_file = Path(self.config.STATE_FILE)
        self.state = self._load_state()
        
        # Gece taraması için kuyruk
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
    
    def _is_scan_time(self) -> bool:
        # Şimdilik her zaman True döndür ki test ederken çalışsın
        return True 
        # Gerçek modda şunu kullan:
        # now = datetime.now().time()
        # return self.config.SCAN_HOURS[0] <= now <= self.config.SCAN_HOURS[1]
    
    def _is_alert_time(self) -> bool:
        return True # Test için her zaman açık

    def _queue_alert(self, deal: Dict):
        self.alert_queue.append(deal)
        logger.info(f"📮 Alert queued (total: {len(self.alert_queue)})")
    
    async def _send_queued_alerts(self):
        if not self.alert_queue: return
        logger.info(f"📢 Sending {len(self.alert_queue)} queued alerts...")
        sent = await self.notifier.send_deals_report(self.alert_queue)
        self.stats['total_alerts'] = sent
        self.alert_queue = []

    async def scan_route(self, route: Dict) -> Optional[Dict]:
        try:
            start_time = datetime.now()
            
            # Tarihleri Intel Center'dan al
            dates = self.intel._generate_sweet_spot_dates(count=self.config.DATES_PER_ROUTE)
            
            best_deal = None
            best_price = float('inf')
            
            for dep_date, ret_date in dates:
                logger.info(f"🔍 Scanning: {route['origin']} → {route['destination']} ({dep_date}-{ret_date})")
                
                # Scraper çağrısı
                result = await self.scraper.scrape_flight(
                    origin=route['origin'],
                    destination=route['destination'],
                    departure_date=dep_date,
                    return_date=ret_date
                )
                
                if result and result.get('price'):
                    price = result.get('real_price', result['price'])
                    if price < best_price:
                        best_price = price
                        best_deal = {**route, **result, 'departure_date': dep_date, 'return_date': ret_date}
                        logger.info(f"💎 New best: {price:,.0f} TL")
                
                await asyncio.sleep(1) # Hızlı tarama için kısa bekleme
            
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
        routes = await self.intel.get_strategic_routes(max_routes=self.config.ROUTES_TO_SCAN)
        self.stats['total_routes'] = len(routes)
        
        deals_found = []
        
        for route in routes:
            deal = await self.scan_route(route)
            if deal:
                deals_found.append(deal)
                logger.info(f"🔥 FIRSAT: {deal['origin']}-{deal['destination']} = {deal['price']} TL")
        
        if deals_found:
            await self.notifier.send_deals_report(deals_found)
            
        self._save_state()
        logger.info("✅ Döngü tamamlandı.")

async def main():
    try:
        titan = ProjectTitanV25()
        if hasattr(titan, 'scraper'): # Başarılı başlatıldıysa
            await titan.run_intelligence_cycle()
        else:
            logger.error("Bot başlatılamadı, eksik dosyaları kontrol edin.")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
