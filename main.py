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

# V2.5 modules
from config_v25 import TitanConfig
from scraper_engine_v25 import ProfessionalFlightScraper
from intel_center_v25 import FlightHackerIntelCenter

# V2.3 modules (still compatible)
# GitHub Actions'da aynı klasörde olacak, path eklemeye gerek yok
try:
    from notifier import TelegramNotifier
    from price_analyzer import PriceAnalyzer
    from visa_checker import VisaChecker
except ImportError:
    # Fallback: eğer başka yerdeyse
    sys.path.append('.')
    from notifier import TelegramNotifier
    from price_analyzer import PriceAnalyzer
    from visa_checker import VisaChecker

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('titan_v25.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProjectTitanV25:
    """
    PROJECT TITAN V2.5 - PROFESSIONAL FLIGHT HACKER
    
    Features:
    - Sweet spot booking (6-8 weeks)
    - Night scanning (02:00-05:00)
    - Morning alerts (09:00+)
    - One-way combinations
    - Alternative airports
    - Baggage cost included
    - Day-of-week pricing
    """
    
    def __init__(self):
        self.config = TitanConfig()
        
        # V2.5 components
        self.scraper = ProfessionalFlightScraper(self.config)
        self.intel = FlightHackerIntelCenter(self.config)
        
        # V2.3 components
        self.notifier = TelegramNotifier(self.config)
        self.price_analyzer = PriceAnalyzer(
            min_sane_price=self.config.MIN_SANE_PRICE,
            max_sane_price=self.config.MAX_SANE_PRICE
        )
        self.visa_checker = VisaChecker()
        
        # State
        self.state_file = Path(self.config.STATE_FILE)
        self.state = self._load_state()
        
        # Alert queue (for night scanning)
        self.alert_queue = []
        
        # Stats
        self.stats = {
            'total_routes': 0,
            'successful_scans': 0,
            'failed_scans': 0,
            'one_way_combos_found': 0,
            'alternative_airports_found': 0,
            'ultra_deals': 0,
            'mistake_fares': 0,
            'total_alerts': 0,
            'queued_alerts': 0,
            'scan_times': []
        }
    
    def _load_state(self) -> Dict:
        """Load state"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self._init_state()
        return self._init_state()
    
    def _init_state(self) -> Dict:
        """Initialize state"""
        return {
            "price_history": {},
            "last_scan": None,
            "total_scans": 0,
            "last_alerts": {},
            "best_deals_found": [],
            "one_way_combos": []  # Track successful combinations
        }
    
    def _save_state(self):
        """Save state"""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
            logger.info("💾 State saved")
        except Exception as e:
            logger.error(f"State save failed: {e}")
    
    def _is_scan_time(self) -> bool:
        """
        RULE 3: Check if current time is in scan window
        Gece 02:00-05:00 tarama zamanı
        """
        now = datetime.now().time()
        scan_start, scan_end = self.config.SCAN_HOURS
        return scan_start <= now <= scan_end
    
    def _is_alert_time(self) -> bool:
        """
        RULE 3: Check if current time is in alert window
        Sabah 09:00'dan sonra mesaj gönder
        """
        now = datetime.now().time()
        alert_start, alert_end = self.config.ALERT_HOURS
        return alert_start <= now <= alert_end
    
    def _queue_alert(self, deal: Dict):
        """
        RULE 3: Queue alert for morning delivery
        Gece bulunan fırsatları sabaha ertele
        """
        self.alert_queue.append(deal)
        self.stats['queued_alerts'] += 1
        logger.info(f"📮 Alert queued for morning delivery (total: {len(self.alert_queue)})")
    
    async def _send_queued_alerts(self):
        """
        RULE 3: Send queued alerts in the morning
        Sabah saat 09:00'dan sonra mesaj gönder
        """
        if not self.alert_queue:
            return
        
        if not self._is_alert_time():
            logger.info(f"⏰ Not yet alert time. {len(self.alert_queue)} alerts queued.")
            return
        
        logger.info(f"📢 Sending {len(self.alert_queue)} queued alerts...")
        
        sent = await self.notifier.send_deals_report(self.alert_queue)
        self.stats['total_alerts'] = sent
        
        # Clear queue
        self.alert_queue = []
        logger.info(f"✅ Queue cleared. {sent} alerts sent.")
    
    async def scan_one_way_combo(self, route: Dict, outbound_date: str, return_date: str) -> Optional[Dict]:
        """
        RULE 4: Scan one-way combination
        Gidiş + Dönüş ayrı ayrı tara, kombinasyonu oluştur
        """
        try:
            logger.info(f"\n🎯 ONE-WAY COMBO SCAN:")
            logger.info(f"   Outbound: {route['origin']} → {route['destination']} ({outbound_date})")
            logger.info(f"   Return: {route['destination']} → {route['origin']} ({return_date})")
            
            # Scan outbound
            outbound = await self.scraper.scrape_one_way_flight(
                route['origin'],
                route['destination'],
                outbound_date
            )
            
            if not outbound:
                logger.warning("❌ Outbound not found")
                return None
            
            await asyncio.sleep(random.uniform(3, 5))
            
            # Scan return
            return_flight = await self.scraper.scrape_one_way_flight(
                route['destination'],
                route['origin'],
                return_date
            )
            
            if not return_flight:
                logger.warning("❌ Return not found")
                return None
            
            # Combine
            combo = await self.scraper.combine_one_way_flights(outbound, return_flight)
            
            if combo:
                self.stats['one_way_combos_found'] += 1
                
                # Save to state
                self.state["one_way_combos"].append({
                    "route": f"{route['origin']}-{route['destination']}",
                    "outbound_price": outbound['price'],
                    "return_price": return_flight['price'],
                    "total_price": combo['price'],
                    "real_price": combo['real_price'],
                    "date": datetime.now().isoformat()
                })
                
                return combo
            
            return None
            
        except Exception as e:
            logger.error(f"❌ One-way combo error: {e}")
            return None
    
    async def scan_route(self, route: Dict) -> Optional[Dict]:
        """
        Main route scanning with V2.5 enhancements
        """
        try:
            start_time = datetime.now()
            
            # Generate sweet spot dates
            dates = self.intel._generate_sweet_spot_dates(count=self.config.DATES_PER_ROUTE)
            
            best_deal = None
            best_price = float('inf')
            
            for dep_date, ret_date in dates:
                logger.info(
                    f"🔍 Scanning: {route['origin']} → {route['destination']} "
                    f"({dep_date} to {ret_date})"
                )
                
                # Check if one-way strategy
                if self.config.SEARCH_STRATEGY == "one_way_combo" and route.get('route_type') == 'one_way':
                    # One-way combo scan
                    result = await self.scan_one_way_combo(route, dep_date, ret_date)
                else:
                    # Traditional round-trip
                    result = await self.scraper.scrape_flight(
                        origin=route['origin'],
                        destination=route['destination'],
                        departure_date=dep_date,
                        return_date=ret_date
                    )
                
                if result and result.get('price'):
                    price = result.get('real_price', result['price'])
                    
                    if not self.price_analyzer.is_sane_price(price):
                        logger.warning(f"⚠️ Anomalous price: {price:,.0f} TL")
                        continue
                    
                    if price < best_price:
                        best_price = price
                        best_deal = {
                            **route,
                            **result,
                            'departure_date': dep_date,
                            'return_date': ret_date
                        }
                        logger.info(f"💎 New best: {price:,.0f} TL")
                
                await asyncio.sleep(random.uniform(
                    self.config.RANDOM_SLEEP_MIN,
                    self.config.RANDOM_SLEEP_MAX
                ))
            
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
    
    async def analyze_deal(self, route: Dict, scrape_result: Dict) -> Dict:
        """Analyze deal with V2.5 enhancements"""
        route_key = f"{route['origin']}-{route['destination']}"
        
        # Use real price if available
        current_price = scrape_result.get('real_price', scrape_result['price'])
        
        # Price history (existing logic from V2.4)
        price_history = self.state["price_history"].get(route_key, [])
        
        # Calculate discount
        meets_threshold = False
        discount_rate = 0
        
        if price_history:
            prices = [h.get("price", h) if isinstance(h, dict) else h for h in price_history]
            if prices:
                avg_price = sum(prices) / len(prices)
                discount_rate = 1 - (current_price / avg_price)
                meets_threshold = discount_rate >= self.config.MIN_DISCOUNT_THRESHOLD
        
        # Ultra deal & mistake fare
        is_ultra_deal = discount_rate >= self.config.ULTRA_DEAL_THRESHOLD
        is_mistake_fare = discount_rate >= self.config.MISTAKE_FARE_THRESHOLD
        
        # Should alert
        should_alert = meets_threshold or is_mistake_fare
        
        # Alert reason
        if is_mistake_fare:
            alert_reason = f"MISTAKE FARE! {discount_rate:.1%} indirim"
        elif is_ultra_deal:
            alert_reason = f"ULTRA DEAL! {discount_rate:.1%} indirim"
        elif meets_threshold:
            alert_reason = f"İyi Fırsat: {discount_rate:.1%} indirim"
        else:
            alert_reason = f"Yetersiz indirim: {discount_rate:.1%}"
        
        # Visa check
        visa_info = self.visa_checker.get_visa_message(route['destination'])
        
        return {
            'should_alert': should_alert,
            'alert_reason': alert_reason,
            'is_mistake_fare': is_mistake_fare,
            'is_ultra_deal': is_ultra_deal,
            'discount_rate': discount_rate,
            'meets_threshold': meets_threshold,
            'visa_info': visa_info,
            'is_direct': scrape_result.get('is_direct', False),
            'confidence': scrape_result.get('confidence', 0.0),
            'baggage_breakdown': scrape_result.get('baggage_breakdown'),
            'is_one_way_combo': scrape_result.get('flight_type') == 'one_way_combo',
            'is_alternative': scrape_result.get('is_alternative', False)
        }
    
    async def run_intelligence_cycle(self):
        """
        Main V2.5 intelligence cycle with night scanning
        """
        try:
            logger.info("\n" + "=" * 70)
            logger.info("🦅 PROJECT TITAN V2.5 - PROFESSIONAL FLIGHT HACKER")
            logger.info("=" * 70)
            
            # Check if scan time (night 02:00-05:00)
            if self.config.QUEUE_NIGHT_ALERTS and not self._is_scan_time():
                logger.info(f"⏰ Not scan time. Current: {datetime.now().strftime('%H:%M')}")
                logger.info(f"   Scan hours: {self.config.SCAN_HOURS[0].strftime('%H:%M')} - {self.config.SCAN_HOURS[1].strftime('%H:%M')}")
                
                # Check if morning - send queued alerts
                if self._is_alert_time() and self.alert_queue:
                    await self._send_queued_alerts()
                
                return
            
            logger.info(f"✅ Scan time! Starting intelligence cycle...")
            
            # ⚠️ SWEET SPOT INFO
            sweet_start = datetime.now() + timedelta(days=self.config.DATE_RANGE_MIN)
            sweet_end = datetime.now() + timedelta(days=self.config.DATE_RANGE_MAX)
            logger.info(f"📅 SWEET SPOT WINDOW:")
            logger.info(f"   {sweet_start.strftime('%Y-%m-%d')} → {sweet_end.strftime('%Y-%m-%d')}")
            logger.info(f"   ({self.config.DATE_RANGE_MIN}-{self.config.DATE_RANGE_MAX} gün / {self.config.DATE_RANGE_MIN//7}-{self.config.DATE_RANGE_MAX//7} hafta)")
            logger.info(f"   ⚠️ SADECE bu aralıktaki uçuşlar taranacak!")
            
            # Get strategic routes
            routes = await self.intel.get_strategic_routes(max_routes=self.config.ROUTES_TO_SCAN)
            self.stats['total_routes'] = len(routes)
            
            deals_found = []
            
            # Scan routes
            for idx, route in enumerate(routes, 1):
                try:
                    logger.info(f"\n--- Route {idx}/{len(routes)} ---")
                    
                    deal = await self.scan_route(route)
                    
                    if deal:
                        analysis = await self.analyze_deal(route, deal)
                        deal['analysis'] = analysis
                        
                        if analysis['should_alert']:
                            # Queue alert if night time, send immediately if day time
                            if self.config.QUEUE_NIGHT_ALERTS and not self._is_alert_time():
                                self._queue_alert(deal)
                            else:
                                deals_found.append(deal)
                            
                            # Stats
                            if analysis['is_mistake_fare']:
                                self.stats['mistake_fares'] += 1
                            if analysis['is_ultra_deal']:
                                self.stats['ultra_deals'] += 1
                            
                            logger.info(
                                f"🔥 DEAL FOUND: {deal['origin']} → {deal['destination']} "
                                f"@ {deal.get('real_price', deal['price']):,.0f} TL "
                                f"[{analysis['alert_reason']}]"
                            )
                    
                    await asyncio.sleep(random.uniform(5, 10))
                    
                except Exception as e:
                    logger.error(f"❌ Route error: {e}")
                    continue
            
            # Send immediate alerts (if day time)
            if deals_found and self._is_alert_time():
                logger.info(f"\n📢 Sending {len(deals_found)} immediate alerts...")
                sent = await self.notifier.send_deals_report(deals_found)
                self.stats['total_alerts'] += sent
            
            # Update state
            self.state["last_scan"] = datetime.now().isoformat()
            self.state["total_scans"] += 1
            self._save_state()
            
            # Performance report
            self._log_performance()
            
            logger.info("\n" + "=" * 70)
            logger.info("✅ V2.5 Intelligence Cycle Complete")
            logger.info("=" * 70)
            
        except Exception as e:
            logger.error(f"❌ Critical error: {e}")
            logger.error(traceback.format_exc())
            await self.notifier.send_error_alert(str(e))
    
    def _log_performance(self):
        """Log V2.5 performance"""
        if self.stats['scan_times']:
            avg_time = sum(self.stats['scan_times']) / len(self.stats['scan_times'])
        else:
            avg_time = 0
        
        success_rate = 0
        if self.stats['total_routes'] > 0:
            success_rate = (self.stats['successful_scans'] / self.stats['total_routes']) * 100
        
        logger.info("\n📊 V2.5 PERFORMANCE METRICS:")
        logger.info(f"   Total Routes: {self.stats['total_routes']}")
        logger.info(f"   Successful: {self.stats['successful_scans']}")
        logger.info(f"   Failed: {self.stats['failed_scans']}")
        logger.info(f"   Success Rate: {success_rate:.1f}%")
        logger.info(f"   Avg Scan Time: {avg_time:.1f}s")
        logger.info(f"   One-Way Combos: {self.stats['one_way_combos_found']}")
        logger.info(f"   Alternative Airports: {self.stats['alternative_airports_found']}")
        logger.info(f"   Ultra Deals: {self.stats['ultra_deals']}")
        logger.info(f"   Mistake Fares: {self.stats['mistake_fares']}")
        logger.info(f"   Alerts Sent: {self.stats['total_alerts']}")
        logger.info(f"   Queued Alerts: {self.stats['queued_alerts']}")
    
    async def run_forever(self):
        """Continuous monitoring with schedule"""
        while True:
            try:
                await self.run_intelligence_cycle()
                
                # Sleep until next scan time
                logger.info(f"😴 Sleeping until next scan time...")
                await asyncio.sleep(1 * 60 * 60)  # 1 hour
                
            except KeyboardInterrupt:
                logger.info("👋 Shutting down...")
                break
            except Exception as e:
                logger.error(f"❌ Unexpected error: {e}")
                await asyncio.sleep(60)

async def main():
    """Entry point"""
    try:
        titan = ProjectTitanV25()
        
        # Single cycle (GitHub Actions)
        await titan.run_intelligence_cycle()
        
        # Continuous (local)
        # await titan.run_forever()
        
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(main())
