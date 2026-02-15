# intel_center_v25.py - PROFESSIONAL FLIGHT HACKER INTELLIGENCE
# 🎯 Sweet spot booking + One-way combos + Flexible dates

import logging
import feedparser
import random
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta, time as dt_time
import re

logger = logging.getLogger(__name__)

class FlightHackerIntelCenter:
    """
    V2.5: Professional flight hacker with industry insider knowledge
    
    Features:
    - Sweet spot booking window (6-8 weeks)
    - Price update day prioritization (Tue-Wed)
    - Day-of-week pricing strategy
    - One-way combination generation
    - Alternative airport checking
    - Flexible date windows
    """
    
    def __init__(self, config):
        self.config = config
        self.origins = config.ORIGINS
        self.destinations = config.DESTINATIONS
        self.rss_feeds = config.RSS_FEEDS
    
    def _parse_rss_feeds(self) -> Dict[str, int]:
        """Parse RSS feeds for trending destinations"""
        trending = {}
        
        for feed_url in self.rss_feeds:
            try:
                logger.info(f"📡 RSS parsing: {feed_url}")
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:20]:
                    title = entry.get('title', '').upper()
                    summary = entry.get('summary', '').upper()
                    text = f"{title} {summary}"
                    
                    codes = re.findall(r'\b[A-Z]{3}\b', text)
                    
                    for code in codes:
                        if code not in ["IST", "SAW", "ADB", "ESB", "AYT", "TZX"]:
                            trending[code] = trending.get(code, 0) + 1
                
            except Exception as e:
                logger.warning(f"⚠️ RSS parse failed: {feed_url} - {e}")
                continue
        
        trending_sorted = dict(sorted(trending.items(), key=lambda x: x[1], reverse=True))
        logger.info(f"🔥 Trending: {list(trending_sorted.keys())[:10]}")
        
        return trending_sorted
    
    def _is_sweet_spot_date(self, date: datetime) -> bool:
        """
        RULE 1: Check if date is in sweet spot booking window
        6-8 hafta önceden = en ucuz booking window
        """
        days_from_now = (date - datetime.now()).days
        min_days, max_days = self.config.SWEET_SPOT_WINDOW
        return min_days <= days_from_now <= max_days
    
    def _is_price_update_day(self, date: datetime) -> bool:
        """
        RULE 2: Check if day is price update day
        Salı-Çarşamba sistem fiyat güncellemesi yapar
        """
        return date.weekday() in self.config.PRICE_UPDATE_DAYS
    
    def _is_expensive_departure_day(self, date: datetime) -> bool:
        """
        RULE 5: Check if expensive departure day
        Cuma akşamı = pahalı
        """
        return date.weekday() in self.config.EXPENSIVE_DEPARTURE_DAYS
    
    def _is_expensive_return_day(self, date: datetime) -> bool:
        """
        RULE 5: Check if expensive return day
        Pazar = pahalı
        """
        return date.weekday() in self.config.EXPENSIVE_RETURN_DAYS
    
    def _is_holiday(self, date_str: str) -> bool:
        """Check if date is Turkish holiday"""
        return date_str in self.config.TURKISH_HOLIDAYS
    
    def _is_optimal_month(self, date: datetime) -> bool:
        """Check if date is in optimal travel month"""
        return date.month in self.config.OPTIMAL_MONTHS
    
    def _generate_sweet_spot_dates(self, count: int = 8) -> List[Tuple[str, str]]:
        """
        RULE 1 + 2 + 5: Generate dates in sweet spot with optimal days
        
        ⚠️ KRİTİK DEĞİŞİKLİK: SADECE 6-8 hafta arası tarihler!
        
        Strategy:
        - **ZORUNLU:** 6-8 hafta arası (42-56 gün)
        - Salı-Çarşamba öncelikli (price update days)
        - Cuma akşamı atla (expensive)
        - Pazar dönüş atla (expensive)
        - Sabah uçuşları tercih et
        """
        dates = []
        base_date = datetime.now()
        
        # ⚠️ SWEET SPOT ENFORCEMENT: SADECE 42-56 gün arası
        min_days, max_days = self.config.SWEET_SPOT_WINDOW
        
        attempts = 0
        max_attempts = count * 20
        
        while len(dates) < count and attempts < max_attempts:
            attempts += 1
            
            # ⚠️ KRİTİK: Sweet spot window içinde rastgele tarih
            # Bu aralık DISINDAKİ tarihler ASLA taranmaz!
            days_offset = random.randint(min_days, max_days)
            departure = base_date + timedelta(days=days_offset)
            
            # Double check: Sweet spot içinde mi?
            if not (min_days <= days_offset <= max_days):
                continue  # Skip if outside sweet spot
            
            # Tatil mi?
            if self.config.AVOID_HOLIDAYS and self._is_holiday(departure.strftime("%Y-%m-%d")):
                continue
            
            # Cuma akşamı mı?
            if self.config.AVOID_FRIDAY_EVENING and self._is_expensive_departure_day(departure):
                continue
            
            # Trip length
            trip_length = random.randint(
                self.config.TRIP_LENGTH_MIN,
                self.config.TRIP_LENGTH_MAX
            )
            
            return_date = departure + timedelta(days=trip_length)
            
            # Pazar dönüş mü?
            if self.config.AVOID_SUNDAY_RETURN and self._is_expensive_return_day(return_date):
                continue
            
            # Dönüş tatil mi?
            if self.config.AVOID_HOLIDAYS and self._is_holiday(return_date.strftime("%Y-%m-%d")):
                continue
            
            # Scoring
            score = 0
            
            # Sweet spot bonus
            if self._is_sweet_spot_date(departure):
                score += 10
            
            # Price update day bonus
            if self._is_price_update_day(departure):
                score += 5
            
            # Optimal month bonus
            if self._is_optimal_month(departure):
                score += 3
            
            dates.append((
                departure.strftime("%Y-%m-%d"),
                return_date.strftime("%Y-%m-%d"),
                score
            ))
        
        # Sort by score
        dates.sort(key=lambda x: x[2], reverse=True)
        
        return [(d[0], d[1]) for d in dates]
    
    def _generate_flexible_dates(self, target_date: str, flexibility_days: int = 3) -> List[str]:
        """
        RULE 8: Generate flexible date options
        ±3 gün esneklik
        """
        target = datetime.strptime(target_date, "%Y-%m-%d")
        flexible_dates = []
        
        for offset in range(-flexibility_days, flexibility_days + 1):
            date = target + timedelta(days=offset)
            flexible_dates.append(date.strftime("%Y-%m-%d"))
        
        return flexible_dates
    
    def _get_alternative_airports(self, airport: str) -> List[str]:
        """
        RULE 6: Get alternative airports
        Küçük havalimanları yüzlerce TL ucuz olabilir
        """
        return self.config.SMALL_AIRPORTS.get(airport, [])
    
    def _generate_one_way_routes(self) -> List[Dict]:
        """
        RULE 4: Generate one-way routes
        Gidiş ve dönüş ayrı ayrı taranacak
        """
        routes = []
        
        # Get all destinations
        all_destinations = []
        for region, airports in self.destinations.items():
            all_destinations.extend(airports.keys())
        
        for origin in self.origins:
            # Origin alternatives
            origin_alternatives = [origin] + self._get_alternative_airports(origin)
            
            for dest in all_destinations:
                # Destination alternatives
                dest_alternatives = [dest] + self._get_alternative_airports(dest)
                
                # Find airline info
                airline_info = None
                for region, airports in self.destinations.items():
                    if dest in airports:
                        airline_info = airports[dest]
                        break
                
                if not airline_info:
                    continue
                
                min_flights = airline_info.get('min_weekly_flights', 0)
                airlines = airline_info.get('airlines', [])
                
                if min_flights >= 7:
                    # Generate outbound one-way routes
                    for orig_alt in origin_alternatives:
                        for dest_alt in dest_alternatives:
                            routes.append({
                                "origin": orig_alt,
                                "destination": dest_alt,
                                "direction": "outbound",
                                "route_type": "one_way",
                                "is_alternative": (orig_alt != origin or dest_alt != dest),
                                "main_origin": origin,
                                "main_destination": dest,
                                "airlines": airlines,
                                "weekly_flights": min_flights,
                                "is_direct": True,
                                "stops": 0
                            })
                    
                    # Generate return one-way routes
                    for dest_alt in dest_alternatives:
                        for orig_alt in origin_alternatives:
                            routes.append({
                                "origin": dest_alt,
                                "destination": orig_alt,
                                "direction": "return",
                                "route_type": "one_way",
                                "is_alternative": (dest_alt != dest or orig_alt != origin),
                                "main_origin": dest,
                                "main_destination": origin,
                                "airlines": airlines,
                                "weekly_flights": min_flights,
                                "is_direct": True,
                                "stops": 0
                            })
        
        logger.info(f"✈️ Generated {len(routes)} one-way routes (with alternatives)")
        return routes
    
    def _generate_round_trip_routes(self) -> List[Dict]:
        """Generate traditional round-trip routes (backup strategy)"""
        routes = []
        
        all_destinations = []
        for region, airports in self.destinations.items():
            all_destinations.extend(airports.keys())
        
        for origin in self.origins:
            for dest in all_destinations:
                airline_info = None
                for region, airports in self.destinations.items():
                    if dest in airports:
                        airline_info = airports[dest]
                        break
                
                if not airline_info:
                    continue
                
                min_flights = airline_info.get('min_weekly_flights', 0)
                
                if min_flights >= 7:
                    routes.append({
                        "origin": origin,
                        "destination": dest,
                        "route_type": "round_trip",
                        "airlines": airline_info.get('airlines', []),
                        "weekly_flights": min_flights,
                        "is_direct": True,
                        "stops": 0
                    })
        
        return routes
    
    def _prioritize_routes(self, routes: List[Dict], trending: Dict[str, int]) -> List[Dict]:
        """Prioritize routes by multiple factors"""
        for route in routes:
            dest = route.get('main_destination', route.get('destination'))
            
            score = 0
            
            # Trending bonus
            if dest in trending:
                score += trending[dest] * 10
                route['priority'] = 'critical'
            
            # Alternative airport bonus
            if route.get('is_alternative', False):
                score += 5  # Alternatives might be cheaper
            
            # Flight frequency bonus
            score += route.get('weekly_flights', 0)
            
            route['priority_score'] = score
            
            if 'priority' not in route:
                if route.get('weekly_flights', 0) >= 14:
                    route['priority'] = 'high'
                else:
                    route['priority'] = 'medium'
        
        # Sort by score
        routes.sort(key=lambda x: x.get('priority_score', 0), reverse=True)
        
        return routes
    
    async def get_strategic_routes(self, max_routes: int = 20) -> List[Dict]:
        """
        Get strategic routes with V2.5 enhancements
        """
        try:
            # RSS intelligence
            trending = self._parse_rss_feeds()
            
            # Generate routes based on strategy
            if self.config.SEARCH_STRATEGY == "one_way_combo":
                routes = self._generate_one_way_routes()
                logger.info(f"🎯 Strategy: ONE-WAY COMBINATIONS")
            else:
                routes = self._generate_round_trip_routes()
                logger.info(f"🎯 Strategy: ROUND-TRIP")
            
            # Prioritize
            prioritized = self._prioritize_routes(routes, trending)
            
            # Sample
            selected = prioritized[:max_routes]
            
            logger.info(f"📋 Selected {len(selected)} routes:")
            logger.info(f"   - Critical: {len([r for r in selected if r.get('priority')=='critical'])}")
            logger.info(f"   - High: {len([r for r in selected if r.get('priority')=='high'])}")
            logger.info(f"   - Medium: {len([r for r in selected if r.get('priority')=='medium'])}")
            
            # Log top 5
            for i, route in enumerate(selected[:5], 1):
                alt_flag = "ALT" if route.get('is_alternative') else "MAIN"
                direction = route.get('direction', 'round_trip').upper()
                logger.info(
                    f"   {i}. [{alt_flag}] [{direction}] "
                    f"{route['origin']} → {route['destination']} "
                    f"({route['weekly_flights']} weekly)"
                )
            
            return selected
            
        except Exception as e:
            logger.error(f"❌ Intel center error: {e}")
            return self._generate_round_trip_routes()[:max_routes]
