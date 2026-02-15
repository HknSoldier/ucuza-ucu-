# scraper_engine_v25.py - PROFESSIONAL FLIGHT HACKER SCRAPER
# 🎯 Extends V2.4 with one-way search + baggage calculation

# V2.4 scraper'ı extend ediyoruz
import sys
sys.path.append('/home/claude')

from scraper_engine_v24 import DirectFlightScraper as V24Scraper
import asyncio
import logging
import random
from typing import Dict, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

class ProfessionalFlightScraper(V24Scraper):
    """
    V2.5: Professional flight hacker scraper
    
    New Features:
    - One-way flight search
    - Baggage cost calculation
    - Time window filtering (morning flights preferred)
    - Alternative airport support
    """
    
    def __init__(self, config):
        super().__init__(config)
        self.config = config
    
    def _calculate_real_price_with_baggage(self, base_price: float, airline: str) -> Dict:
        """
        RULE 7: Calculate real price including baggage
        Standart 20 kg valiz maliyeti dahil
        """
        baggage_costs = self.config.BAGGAGE_COSTS.get(
            airline, 
            self.config.BAGGAGE_COSTS["default"]
        )
        
        cabin_cost = baggage_costs.get("cabin", 0)
        checked_cost = baggage_costs.get("checked_20", 0)
        
        real_price = base_price + cabin_cost + checked_cost
        
        return {
            "base_price": base_price,
            "cabin_baggage": cabin_cost,
            "checked_baggage": checked_cost,
            "real_price": real_price,
            "extra_cost": cabin_cost + checked_cost,
            "airline": airline
        }
    
    async def scrape_one_way_flight(self, origin: str, destination: str, 
                                   departure_date: str) -> Optional[Dict]:
        """
        RULE 4: One-way flight search
        Gidiş veya dönüş için tek yön tarama
        """
        await self._wait_for_rate_limit()
        
        browser = None
        
        # One-way URL
        url = (
            f"https://www.google.com/travel/flights?"
            f"q=Flights+to+{destination}+from+{origin}+"
            f"on+{departure_date}"
            f"&curr=TRY&hl=tr&gl=TR"
            f"&type=1"  # type=1 = one-way
        )
        
        try:
            self._record_request()
            
            from playwright.async_api import async_playwright
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-dev-shm-usage']
                )
                
                context = await browser.new_context(
                    user_agent=random.choice(self.user_agents),
                    viewport={'width': 1920, 'height': 1080},
                    locale='tr-TR'
                )
                
                page = await context.new_page()
                
                # Anti-detection
                await page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                """)
                
                logger.info(f"🔍 [Google ONE-WAY] {origin} → {destination} ({departure_date})")
                
                await page.goto(url, timeout=90000, wait_until='domcontentloaded')
                await asyncio.sleep(random.uniform(4, 7))
                
                # Close cookie consent
                try:
                    consent_buttons = ["button[aria-label*='Reject']", "button:has-text('Reject all')"]
                    for selector in consent_buttons:
                        if await page.is_visible(selector, timeout=3000):
                            await page.click(selector)
                            await asyncio.sleep(2)
                            break
                except:
                    pass
                
                # Wait for results
                await page.wait_for_selector('div[role="main"]', timeout=45000)
                await page.mouse.wheel(0, 1500)
                await asyncio.sleep(random.uniform(3, 5))
                
                # Extract direct flights
                page_content = await page.content()
                direct_flights = []
                
                nonstop_elements = await page.query_selector_all('[aria-label*="Nonstop"], [aria-label*="Direct"]')
                
                for elem in nonstop_elements:
                    try:
                        parent = await elem.evaluate_handle("el => el.closest('[role=\"listitem\"]')")
                        if parent:
                            card_text = await parent.text_content()
                            
                            # Price extraction
                            import re
                            price_matches = re.findall(r'(\d{1,3}(?:[.,]\d{3})*)\s*(?:TL|TRY)', card_text)
                            
                            if price_matches:
                                price = float(price_matches[0].replace(',', '').replace('.', ''))
                                
                                if self.config.MIN_SANE_PRICE <= price <= self.config.MAX_SANE_PRICE:
                                    # Airline extraction
                                    airline = "Multiple"
                                    airline_match = re.search(
                                        r'(Turkish Airlines|Lufthansa|United|Emirates|Qatar|KLM|Air France|Pegasus|AnadoluJet)',
                                        card_text
                                    )
                                    if airline_match:
                                        airline = airline_match.group(1)
                                    
                                    direct_flights.append({
                                        "price": price,
                                        "airline": airline,
                                        "stops": 0,
                                        "is_direct": True,
                                        "flight_type": "one_way",
                                        "departure_date": departure_date
                                    })
                    except Exception as e:
                        logger.debug(f"Card extraction error: {e}")
                        continue
                
                await browser.close()
                
                if not direct_flights:
                    logger.warning(f"⚠️ No one-way direct flights: {origin} → {destination}")
                    return None
                
                # Get cheapest
                cheapest = min(direct_flights, key=lambda x: x['price'])
                
                # Calculate real price with baggage
                price_with_baggage = self._calculate_real_price_with_baggage(
                    cheapest['price'],
                    cheapest['airline']
                )
                
                logger.info(
                    f"✅ [ONE-WAY] {cheapest['price']:,.0f} TL "
                    f"(+{price_with_baggage['extra_cost']:.0f} bagaj = {price_with_baggage['real_price']:,.0f} TL) "
                    f"[{cheapest['airline']}]"
                )
                
                return {
                    'price': cheapest['price'],
                    'real_price': price_with_baggage['real_price'],
                    'baggage_breakdown': price_with_baggage,
                    'currency': 'TRY',
                    'airline': cheapest['airline'],
                    'stops': 0,
                    'is_direct': True,
                    'flight_type': 'one_way',
                    'method': 'google_flights_oneway',
                    'confidence': 0.90,
                    'departure_date': departure_date
                }
                
        except Exception as e:
            logger.error(f"❌ [ONE-WAY] Scrape error: {e}")
            if browser:
                await browser.close()
            return None
    
    async def combine_one_way_flights(self, outbound: Dict, return_flight: Dict) -> Dict:
        """
        RULE 4: Combine outbound + return one-way flights
        Gidiş + Dönüş kombinasyonu
        """
        if not outbound or not return_flight:
            return None
        
        combined_price = outbound['price'] + return_flight['price']
        combined_real_price = outbound['real_price'] + return_flight['real_price']
        
        # Check if combination is cheaper than typical round-trip
        logger.info(f"💡 ONE-WAY COMBO: {combined_price:,.0f} TL (Real: {combined_real_price:,.0f} TL)")
        
        return {
            'price': combined_price,
            'real_price': combined_real_price,
            'currency': 'TRY',
            'outbound': outbound,
            'return': return_flight,
            'flight_type': 'one_way_combo',
            'is_direct': True,
            'method': 'one_way_combination',
            'confidence': min(outbound['confidence'], return_flight['confidence']),
            'savings_note': 'One-way combination may be cheaper than round-trip'
        }
    
    async def scrape_with_alternatives(self, route: Dict, departure_date: str, 
                                      return_date: Optional[str] = None) -> List[Dict]:
        """
        RULE 6: Check alternative airports
        Küçük havalimanları kontrolü
        """
        results = []
        
        main_origin = route.get('main_origin', route['origin'])
        main_destination = route.get('main_destination', route['destination'])
        
        # Get alternatives
        origin_alternatives = [main_origin] + self.config.SMALL_AIRPORTS.get(main_origin, [])
        dest_alternatives = [main_destination] + self.config.SMALL_AIRPORTS.get(main_destination, [])
        
        logger.info(f"🔍 Checking alternatives:")
        logger.info(f"   Origins: {origin_alternatives}")
        logger.info(f"   Destinations: {dest_alternatives}")
        
        # Try main route first
        if route.get('route_type') == 'one_way':
            result = await self.scrape_one_way_flight(
                route['origin'],
                route['destination'],
                departure_date
            )
            if result:
                result['is_alternative'] = False
                results.append(result)
        else:
            # Round-trip (use parent class method)
            result = await self.scrape_flight(
                route['origin'],
                route['destination'],
                departure_date,
                return_date
            )
            if result:
                result['is_alternative'] = False
                results.append(result)
        
        # Try alternatives (limit to 2 to avoid spam)
        alt_count = 0
        for orig in origin_alternatives[:2]:
            for dest in dest_alternatives[:2]:
                if orig == route['origin'] and dest == route['destination']:
                    continue  # Skip main route
                
                if alt_count >= 2:
                    break
                
                try:
                    if route.get('route_type') == 'one_way':
                        result = await self.scrape_one_way_flight(orig, dest, departure_date)
                    else:
                        result = await self.scrape_flight(orig, dest, departure_date, return_date)
                    
                    if result:
                        result['is_alternative'] = True
                        result['alternative_airports'] = f"{orig}-{dest}"
                        results.append(result)
                        alt_count += 1
                    
                    await asyncio.sleep(random.uniform(3, 5))
                    
                except Exception as e:
                    logger.debug(f"Alternative search error {orig}-{dest}: {e}")
                    continue
        
        return results
