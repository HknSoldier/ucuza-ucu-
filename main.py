# main.py - PROJECT TITAN V2.3 Main Orchestrator
# 🦅 Event-driven Architecture + Self-healing + Advanced Analytics

import asyncio
import logging
import json
import random
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Import modüller
from config import TitanConfig
from scraper_engine import ScraperEngine
from intel_center import IntelCenter
from notifier import TelegramNotifier
from price_analyzer import PriceAnalyzer
from visa_checker import VisaChecker
from ucuzaucak_scraper import UcuzaucakScraper

# Logging yapılandırması
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('titan.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProjectTitanV2:
    """
    PROJECT TITAN V2.3 - Enterprise Flight Intelligence System
    
    Features:
    - Event-driven architecture
    - Ghost Protocol (time-based alerting)
    - Anti-spam protection
    - Self-healing (auto IP rotation)
    - Advanced price analytics
    - Hub arbitrage
    - Visa checking (Green Passport)
    """
    
    def __init__(self):
        self.config = TitanConfig()
        self.scraper = ScraperEngine(self.config)
        self.intel = IntelCenter(self.config)
        self.notifier = TelegramNotifier(self.config)
        self.price_analyzer = PriceAnalyzer(
            min_sane_price=self.config.MIN_SANE_PRICE,
            max_sane_price=self.config.MAX_SANE_PRICE
        )
        self.visa_checker = VisaChecker()
        self.ucuzaucak = UcuzaucakScraper(self.config)
        
        # State management
        self.state_file = Path(self.config.STATE_FILE)
        self.state = self._load_state()
        
        # Historical price cache
        self.historical_data = None  # Geçmiş fiyat verileri
        
        # Performance tracking
        self.stats = {
            'total_routes': 0,
            'successful_scans': 0,
            'failed_scans': 0,
            'bottom_deals': 0,
            'mistake_fares': 0,
            'total_alerts': 0,
            'scan_times': []
        }
    
    def _load_state(self) -> Dict:
        """Persistent state yükle"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"State load failed: {e}")
                return self._init_state()
        return self._init_state()
    
    def _init_state(self) -> Dict:
        """Yeni state başlat"""
        return {
            "price_history": {},  # {route_key: [prices]}
            "last_scan": None,
            "total_scans": 0,
            "last_alerts": {},  # {route_key: timestamp}
        }
    
    def _save_state(self):
        """State kaydet"""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
            logger.info("💾 State saved")
        except Exception as e:
            logger.error(f"State save failed: {e}")
    
    def _generate_smart_dates(self, count: int = 5) -> List[tuple]:
        """
        Akıllı tarih çiftleri üret (3-11 ay arası)
        """
        dates = []
        base_date = datetime.now()
        
        for _ in range(count):
            # 90-330 gün arası rastgele offset
            days_offset = random.randint(
                self.config.DATE_RANGE_MIN,
                self.config.DATE_RANGE_MAX
            )
            departure = base_date + timedelta(days=days_offset)
            
            # 3-14 gün arası trip length
            trip_length = random.randint(
                self.config.TRIP_LENGTH_MIN,
                self.config.TRIP_LENGTH_MAX
            )
            return_date = departure + timedelta(days=trip_length)
            
            dates.append((
                departure.strftime("%Y-%m-%d"),
                return_date.strftime("%Y-%m-%d")
            ))
        
        return dates
    
    def _update_price_history(self, route_key: str, price: float):
        """Fiyat geçmişini güncelle"""
        if route_key not in self.state["price_history"]:
            self.state["price_history"][route_key] = []
        
        history = self.state["price_history"][route_key]
        history.append({
            "price": price,
            "date": datetime.now().isoformat()
        })
        
        # Son 90 günlük geçmişi tut
        if len(history) > self.config.PRICE_HISTORY_SIZE:
            history = history[-self.config.PRICE_HISTORY_SIZE:]
        
        self.state["price_history"][route_key] = history
    
    def _get_price_history(self, route_key: str) -> List[float]:
        """Rota için fiyat geçmişini al"""
        history = self.state["price_history"].get(route_key, [])
        return [h["price"] for h in history]
    
    async def load_historical_data(self, max_pages: int = 3):
        """
        ucuzaucak.net'ten geçmiş fiyat verilerini yükle
        
        Args:
            max_pages: Maksimum kaç sayfa taranacak (default: 3, çok fazla spam yapmamak için)
        """
        try:
            logger.info(f"📊 Loading historical data from ucuzaucak.net (max {max_pages} pages)...")
            
            # Geçmiş verileri çek
            deals = await self.ucuzaucak.scrape_multiple_pages(max_pages=max_pages)
            
            if not deals:
                logger.warning("⚠️ No historical data found from ucuzaucak.net")
                return
            
            # Rotaya göre grupla
            self.historical_data = self.ucuzaucak.aggregate_by_route(deals)
            
            logger.info(f"✅ Historical data loaded: {len(self.historical_data)} unique routes")
            
            # İstatistik logla
            for route_key, stats in list(self.historical_data.items())[:5]:
                logger.info(
                    f"   {route_key}: Min={stats['min']:.0f} TL, "
                    f"Avg={stats['avg']:.0f} TL, Max={stats['max']:.0f} TL "
                    f"({stats['count']} samples)"
                )
            
        except Exception as e:
            logger.error(f"❌ Failed to load historical data: {e}")
            self.historical_data = None
    
    async def analyze_deal(self, route: Dict, scrape_result: Dict) -> Dict:
        """
        Komple deal analizi:
        - Dip fiyat tespiti
        - Mistake fare kontrolü
        - Alarm filter
        - Visa check
        - Gerçek maliyet hesaplama
        - Fiyat elastikiyeti
        """
        route_key = f"{route['origin']}-{route['destination']}"
        current_price = scrape_result['price']
        
        # Fiyat geçmişi
        price_history = self._get_price_history(route_key)
        
        # 1. Dip fiyat analizi
        bottom_analysis = self.price_analyzer.calculate_bottom_price(price_history)
        price_category = self.price_analyzer.categorize_price(current_price, bottom_analysis)
        
        # 2. Alarm filter
        should_alert, alert_reason = self.price_analyzer.should_alert(
            current_price,
            price_history,
            self.config.ALARM_PRICE_MULTIPLIER
        )
        
        # 3. Mistake fare?
        is_mistake_fare = False
        if price_history:
            avg_price = sum(price_history) / len(price_history)
            is_mistake_fare = self.price_analyzer.is_mistake_fare(
                current_price,
                avg_price,
                self.config.MISTAKE_FARE_THRESHOLD
            )
        
        # 4. Visa check
        visa_info = self.visa_checker.get_visa_message(route['destination'])
        
        # 5. Gerçek maliyet
        real_cost = self.price_analyzer.calculate_real_cost(
            current_price,
            scrape_result.get('airline', 'Unknown'),
            route['destination'],
            self.config.BAGGAGE_COSTS,
            self.config.REMOTE_AIRPORT_TRANSPORT
        )
        
        # 6. Fiyat elastikiyeti
        history_with_dates = self.state["price_history"].get(route_key, [])
        elasticity = self.price_analyzer.estimate_price_elasticity(history_with_dates)
        
        # 7. Geçmiş fiyat karşılaştırması (ucuzaucak.net)
        historical_comparison = None
        if self.historical_data:
            historical_comparison = self.ucuzaucak.compare_with_historical(
                current_price,
                route_key,
                self.historical_data
            )
            
            if historical_comparison:
                logger.info(
                    f"📊 Historical comparison for {route_key}: "
                    f"Percentile: {historical_comparison.get('percentile', 0):.0f}%, "
                    f"{historical_comparison.get('recommendation', 'N/A')}"
                )
        
        # Fiyat geçmişini güncelle
        self._update_price_history(route_key, current_price)
        
        return {
            'should_alert': should_alert,
            'alert_reason': alert_reason,
            'is_mistake_fare': is_mistake_fare,
            'bottom_analysis': bottom_analysis,
            'price_category': price_category,
            'visa_info': visa_info,
            'real_cost': real_cost,
            'elasticity': elasticity,
            'historical_comparison': historical_comparison,  # Yeni!
            'is_green_zone': price_category.get('category') == 'bottom',
            'confidence': scrape_result.get('confidence', 0.0)
        }
    
    async def scan_route(self, route: Dict) -> Optional[Dict]:
        """
        Tek rota tarama + multi-date sampling
        """
        try:
            start_time = datetime.now()
            
            # Tarih çiftleri üret
            dates = self._generate_smart_dates(count=5)
            
            best_deal = None
            best_price = float('inf')
            
            for dep_date, ret_date in dates:
                logger.info(
                    f"🔍 Scanning: {route['origin']} → {route['destination']} "
                    f"({dep_date} to {ret_date})"
                )
                
                # Scrape
                result = await self.scraper.scrape_flight(
                    origin=route['origin'],
                    destination=route['destination'],
                    departure_date=dep_date,
                    return_date=ret_date
                )
                
                if result and result.get('price'):
                    price = result['price']
                    
                    # Anomali kontrolü
                    if not self.price_analyzer.is_sane_price(price):
                        logger.warning(f"⚠️ Anomali price: {price:,.0f} TL - skipping")
                        continue
                    
                    if price < best_price:
                        best_price = price
                        best_deal = {
                            **route,
                            **result,
                            'departure_date': dep_date,
                            'return_date': ret_date
                        }
                
                # Random sleep (anti-detection)
                await asyncio.sleep(random.uniform(
                    self.config.RANDOM_SLEEP_MIN,
                    self.config.RANDOM_SLEEP_MAX
                ))
            
            # Performance tracking
            scan_duration = (datetime.now() - start_time).total_seconds()
            self.stats['scan_times'].append(scan_duration)
            
            if best_deal:
                self.stats['successful_scans'] += 1
                return best_deal
            else:
                self.stats['failed_scans'] += 1
                return None
                
        except Exception as e:
            logger.error(f"❌ Route scan error: {e}")
            self.stats['failed_scans'] += 1
            return None
    
    async def run_intelligence_cycle(self):
        """
        Ana istihbarat döngüsü:
        1. RSS intelligence toplama
        2. Stratejik rotalar üretme
        3. Her rotayı tarama
        4. Deal analizi
        5. Alarm gönderme (Ghost Protocol + Anti-Spam)
        """
        try:
            logger.info("=" * 60)
            logger.info("🦅 PROJECT TITAN V2.3 - Intelligence Cycle Starting")
            logger.info("=" * 60)
            
            # ❌ SESSİZ BAŞLANGIÇ: Startup mesajı KALDIRILDI
            # GitHub Actions her 4 saatte çalışır, spam yaratmamak için sessiz başlangıç
            # await self.notifier.send_startup_message()  # DEVRE DIŞI
            
            # 0. Geçmiş fiyat verilerini yükle (ilk cycle'da)
            if self.historical_data is None:
                await self.load_historical_data(max_pages=3)
            
            # 1. Stratejik rotalar al
            routes = await self.intel.get_strategic_routes(max_routes=30)
            self.stats['total_routes'] = len(routes)
            logger.info(f"📋 {len(routes)} routes loaded for scanning")
            
            deals_found = []
            
            # 2. Her rotayı tara
            for idx, route in enumerate(routes, 1):
                try:
                    logger.info(f"\n--- Route {idx}/{len(routes)} ---")
                    
                    # Scrape
                    deal = await self.scan_route(route)
                    
                    if deal:
                        # Analiz
                        analysis = await self.analyze_deal(route, deal)
                        deal['analysis'] = analysis
                        
                        # Alarm gerekli mi?
                        if analysis['should_alert']:
                            deals_found.append(deal)
                            
                            # Stats güncelle
                            if analysis['is_mistake_fare']:
                                self.stats['mistake_fares'] += 1
                            if analysis['is_green_zone']:
                                self.stats['bottom_deals'] += 1
                            
                            logger.info(
                                f"🔥 DEAL FOUND: {deal['origin']} → {deal['destination']} "
                                f"@ {deal['price']:,.0f} TL "
                                f"({analysis['price_category']['emoji']} {analysis['price_category']['action']})"
                            )
                    
                    # Rotalar arası rastgele sleep
                    await asyncio.sleep(random.uniform(5, 10))
                    
                except Exception as e:
                    logger.error(f"❌ Route processing error: {e}")
                    continue
            
            # 3. Alarm gönder (Ghost Protocol + Anti-Spam kontrollü)
            if deals_found:
                logger.info(f"\n📢 Sending {len(deals_found)} deal alerts...")
                sent = await self.notifier.send_deals_report(deals_found)
                self.stats['total_alerts'] = sent
            else:
                logger.info("📭 No significant deals found in this cycle")
            
            # 4. State güncelle
            self.state["last_scan"] = datetime.now().isoformat()
            self.state["total_scans"] += 1
            self._save_state()
            
            # 5. Performance raporu
            self._log_performance()
            
            # 6. Self-healing check
            await self._check_system_health()
            
            logger.info("=" * 60)
            logger.info("✅ Intelligence Cycle Complete")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"❌ Critical error in intelligence cycle: {e}")
            logger.error(traceback.format_exc())
            await self.notifier.send_error_alert(str(e))
    
    def _log_performance(self):
        """Performance metriklerini logla"""
        if self.stats['scan_times']:
            avg_time = sum(self.stats['scan_times']) / len(self.stats['scan_times'])
        else:
            avg_time = 0
        
        success_rate = 0
        if self.stats['total_routes'] > 0:
            success_rate = (self.stats['successful_scans'] / self.stats['total_routes']) * 100
        
        logger.info("\n📊 PERFORMANCE METRICS:")
        logger.info(f"   Total Routes: {self.stats['total_routes']}")
        logger.info(f"   Successful: {self.stats['successful_scans']}")
        logger.info(f"   Failed: {self.stats['failed_scans']}")
        logger.info(f"   Success Rate: {success_rate:.1f}%")
        logger.info(f"   Avg Scan Time: {avg_time:.1f}s")
        logger.info(f"   Bottom Deals: {self.stats['bottom_deals']}")
        logger.info(f"   Mistake Fares: {self.stats['mistake_fares']}")
        logger.info(f"   Alerts Sent: {self.stats['total_alerts']}")
    
    async def _check_system_health(self):
        """
        Self-healing: Sistem sağlığını kontrol et
        Başarı oranı < %70 ise uyar
        """
        if self.stats['total_routes'] == 0:
            return
        
        failure_rate = self.stats['failed_scans'] / self.stats['total_routes']
        
        if failure_rate > self.config.MAX_FAILURE_RATE:
            logger.error(
                f"⚠️ HIGH FAILURE RATE: {failure_rate:.1%} "
                f"(Threshold: {self.config.MAX_FAILURE_RATE:.1%})"
            )
            
            alert_msg = f"""
⚠️ SYSTEM HEALTH WARNING

Failure Rate: {failure_rate:.1%}
Threshold: {self.config.MAX_FAILURE_RATE:.1%}

Action Required:
- Check IP reputation
- Verify proxy settings
- Review rate limits
- Check Google Flights changes

System may need IP rotation or cooldown period.
"""
            await self.notifier.send_error_alert(alert_msg)
    
    async def run_forever(self):
        """
        Sürekli monitoring (local test için)
        Her 4 saatte bir döngü
        """
        while True:
            try:
                await self.run_intelligence_cycle()
                
                # 4 saat bekle
                logger.info(f"😴 Sleeping for 4 hours... Next scan at {(datetime.now() + timedelta(hours=4)).strftime('%H:%M')}")
                await asyncio.sleep(4 * 60 * 60)
                
            except KeyboardInterrupt:
                logger.info("👋 Shutting down gracefully...")
                break
            except Exception as e:
                logger.error(f"❌ Unexpected error: {e}")
                await asyncio.sleep(60)  # 1 dakika bekle, retry

async def main():
    """Entry point"""
    try:
        titan = ProjectTitanV2()
        
        # GitHub Actions için tek cycle
        await titan.run_intelligence_cycle()
        
        # Local test için sürekli monitoring
        # await titan.run_forever()
        
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(main())
