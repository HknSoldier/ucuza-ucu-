# main.py - The Orchestrator
import asyncio
import logging
import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import traceback

from scraper_engine import ScraperEngine
from intel_center import IntelCenter
from notifier import TelegramNotifier

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('titan.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProjectTitan:
    """
    PROJECT TITAN - Autonomous Flight Intelligence System
    Hybrid scraping engine with state persistence and smart alerting
    """
    
    def __init__(self):
        self.scraper = ScraperEngine()
        self.intel = IntelCenter()
        self.notifier = TelegramNotifier()
        self.state_file = Path("titan_state.json")
        self.state = self._load_state()
        
    def _load_state(self) -> Dict:
        """Load persistent state from JSON file"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load state: {e}")
                return {"price_history": {}, "last_scan": None}
        return {"price_history": {}, "last_scan": None}
    
    def _save_state(self):
        """Persist state to JSON file"""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
    
    def _generate_smart_dates(self) -> List[tuple]:
        """
        Generate random date pairs within 3-11 months to avoid detection
        Returns list of (departure_date, return_date) tuples
        """
        dates = []
        base_date = datetime.now()
        
        # Generate 5 random date pairs
        for _ in range(5):
            # Random offset between 90-330 days (3-11 months)
            days_offset = random.randint(90, 330)
            departure = base_date + timedelta(days=days_offset)
            
            # Random trip length 3-14 days
            trip_length = random.randint(3, 14)
            return_date = departure + timedelta(days=trip_length)
            
            dates.append((
                departure.strftime("%Y-%m-%d"),
                return_date.strftime("%Y-%m-%d")
            ))
            
        return dates
    
    def _calculate_threshold(self, origin: str, destination: str) -> int:
        """
        Smart threshold calculation
        Sofia hack: Much lower threshold for SOF
        """
        thresholds = {
            # Sofia arbitrage - super low threshold
            "SOF": {
                "JFK": 10000, "LAX": 12000, "ORD": 11000,
                "MIA": 10000, "BOS": 10000, "default": 10000
            },
            # Turkish airports - normal thresholds
            "IST": {
                "JFK": 30000, "LAX": 35000, "ORD": 32000,
                "MIA": 28000, "BOS": 30000, "default": 30000
            },
            "SAW": {
                "JFK": 28000, "LAX": 33000, "ORD": 30000,
                "MIA": 26000, "BOS": 28000, "default": 28000
            },
            "ADB": {"default": 32000},
            "ESB": {"default": 30000},
            "AYT": {"default": 35000},
            "TZX": {"default": 33000}
        }
        
        origin_thresholds = thresholds.get(origin, {"default": 30000})
        return origin_thresholds.get(destination, origin_thresholds["default"])
    
    def _is_green_zone(self, price: float, avg_price: float) -> bool:
        """
        Detect if price is in the lower 20% (green zone)
        """
        if avg_price == 0:
            return False
        return price <= (avg_price * 0.8)
    
    def _analyze_deal(self, route: Dict, price: float) -> Dict:
        """
        Analyze if a deal is worth alerting
        Returns analysis dict with decision
        """
        route_key = f"{route['origin']}-{route['destination']}"
        history = self.state["price_history"].get(route_key, [])
        
        # Calculate average price from history
        avg_price = sum(history) / len(history) if history else price
        
        # Get threshold for this route
        threshold = self._calculate_threshold(route['origin'], route['destination'])
        
        # Check conditions
        is_below_threshold = price < threshold
        is_price_drop = price < (avg_price * 0.85) if history else False
        is_green = self._is_green_zone(price, avg_price)
        
        # Update history
        history.append(price)
        if len(history) > 10:  # Keep last 10 prices
            history = history[-10:]
        self.state["price_history"][route_key] = history
        
        return {
            "alert": is_below_threshold or is_price_drop or is_green,
            "price": price,
            "avg_price": avg_price,
            "threshold": threshold,
            "is_green_zone": is_green,
            "price_drop": is_price_drop,
            "below_threshold": is_below_threshold
        }
    
    async def scan_route(self, route: Dict) -> Optional[Dict]:
        """
        Scan a single route with all date combinations
        Returns best deal if found
        """
        try:
            dates = self._generate_smart_dates()
            best_deal = None
            best_price = float('inf')
            
            for dep_date, ret_date in dates:
                logger.info(f"Scanning {route['origin']} → {route['destination']} ({dep_date} to {ret_date})")
                
                # Try scraping with retry logic
                result = await self.scraper.scrape_flight(
                    origin=route['origin'],
                    destination=route['destination'],
                    departure_date=dep_date,
                    return_date=ret_date
                )
                
                if result and result.get('price'):
                    price = result['price']
                    if price < best_price:
                        best_price = price
                        best_deal = {
                            **route,
                            **result,
                            'departure_date': dep_date,
                            'return_date': ret_date
                        }
                
                # Random sleep to avoid detection
                await asyncio.sleep(random.uniform(3, 8))
            
            return best_deal
            
        except Exception as e:
            logger.error(f"Error scanning route {route}: {e}")
            logger.error(traceback.format_exc())
            return None
    
    async def run_intelligence_cycle(self):
        """
        Main intelligence cycle
        1. Get routes from Intel Center
        2. Scan each route
        3. Analyze deals
        4. Send notifications
        """
        try:
            logger.info("🦅 TITAN Intelligence Cycle Starting...")
            
            # Get routes from intel center
            routes = await self.intel.get_priority_routes()
            logger.info(f"Loaded {len(routes)} routes for scanning")
            
            deals_found = []
            
            # Scan each route
            for route in routes:
                try:
                    deal = await self.scan_route(route)
                    
                    if deal:
                        # Analyze the deal
                        analysis = self._analyze_deal(route, deal['price'])
                        
                        if analysis['alert']:
                            deal['analysis'] = analysis
                            deals_found.append(deal)
                            logger.info(f"🔥 DEAL FOUND: {deal['origin']} → {deal['destination']} @ {deal['price']} TL")
                    
                    # Random sleep between routes
                    await asyncio.sleep(random.uniform(5, 12))
                    
                except Exception as e:
                    logger.error(f"Error processing route {route}: {e}")
                    continue
            
            # Send notifications for deals
            if deals_found:
                await self.notifier.send_deals_report(deals_found)
            else:
                logger.info("No significant deals found in this cycle")
            
            # Update state
            self.state["last_scan"] = datetime.now().isoformat()
            self._save_state()
            
            logger.info("✅ Intelligence Cycle Complete")
            
        except Exception as e:
            logger.error(f"Critical error in intelligence cycle: {e}")
            logger.error(traceback.format_exc())
            await self.notifier.send_error_alert(str(e))
    
    async def run_forever(self):
        """
        Run continuous monitoring (for local testing)
        """
        while True:
            try:
                await self.run_intelligence_cycle()
                # Sleep 4 hours
                await asyncio.sleep(4 * 60 * 60)
            except KeyboardInterrupt:
                logger.info("Shutting down gracefully...")
                break
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry

async def main():
    """Entry point"""
    titan = ProjectTitan()
    
    # Run single cycle (for GitHub Actions)
    await titan.run_intelligence_cycle()
    
    # Uncomment below for continuous monitoring
    # await titan.run_forever()

if __name__ == "__main__":
    asyncio.run(main())
