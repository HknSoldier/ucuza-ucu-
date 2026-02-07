# intel_center.py - Advanced Intelligence & Route Generation V2.3
# 🛰️ Hub Arbitrage + Hidden City + Multi-source RSS

import logging
import feedparser
import random
from typing import List, Dict, Optional, Tuple
import re

logger = logging.getLogger(__name__)

class IntelCenter:
    """
    Gelişmiş istihbarat merkezi:
    - RSS feed analizi
    - Hub arbitraj stratejisi
    - Hidden city routing
    - Alternativ havalimanı önerileri
    """
    
    def __init__(self, config):
        self.config = config
        self.origins = config.ORIGINS
        self.destinations = config.DESTINATIONS
        self.hub_alternatives = config.HUB_ALTERNATIVES
        self.rss_feeds = config.RSS_FEEDS
    
    def _parse_rss_feeds(self) -> Dict[str, int]:
        """
        RSS feedlerden trending destinasyonları çek
        Returns: {airport_code: popularity_score}
        """
        trending = {}
        
        for feed_url in self.rss_feeds:
            try:
                logger.info(f"📡 RSS parsing: {feed_url}")
                feed = feedparser.parse(feed_url, timeout=10)
                
                for entry in feed.entries[:15]:  # Top 15
                    title = entry.get('title', '').upper()
                    summary = entry.get('summary', '').upper()
                    text = f"{title} {summary}"
                    
                    # 3 harfli havalimanı kodlarını çıkar
                    codes = re.findall(r'\b[A-Z]{3}\b', text)
                    
                    for code in codes:
                        # İstanbul/Türkiye kodlarını filtrele (bunlar origin)
                        if code not in ["IST", "SAW", "ADB", "ESB", "AYT", "TZX", "TUR", "TRY"]:
                            trending[code] = trending.get(code, 0) + 1
                
                logger.info(f"✅ RSS parsed: {len(feed.entries)} entries")
                
            except Exception as e:
                logger.warning(f"⚠️ RSS parse failed: {feed_url} - {e}")
                continue
        
        # Popülerliğe göre sırala
        trending_sorted = dict(sorted(trending.items(), key=lambda x: x[1], reverse=True))
        logger.info(f"🔥 Trending destinations: {list(trending_sorted.keys())[:10]}")
        
        return trending_sorted
    
    def _generate_direct_routes(self) -> List[Dict]:
        """
        Direkt rotalar (gidiş-dönüş, non-stop)
        En yüksek öncelik!
        """
        routes = []
        
        # Tüm destinasyonları topla
        all_destinations = []
        for region, airports in self.destinations.items():
            all_destinations.extend(airports)
        
        for origin in self.origins:
            for dest in all_destinations:
                routes.append({
                    "origin": origin,
                    "destination": dest,
                    "route_type": "direct",
                    "priority": "high",
                    "flight_type": "Direkt"
                })
        
        return routes
    
    def _generate_hub_arbitrage_routes(self, expensive_origin: str = "IST") -> List[Dict]:
        """
        Hub arbitraj rotaları:
        Istanbul pahalıysa, SOF/AUH/DOH üzerinden git
        
        Example:
        - IST → JFK: 30,000 TL
        - IST → SOF: 1,500 TL + SOF → JFK: 10,000 TL = 11,500 TL (Tasarruf!)
        """
        hub_routes = []
        
        if expensive_origin not in self.hub_alternatives:
            return hub_routes
        
        alternative_hubs = self.hub_alternatives[expensive_origin]
        
        # Her hub için rotalar oluştur
        for hub in alternative_hubs:
            # Hub'a positioning flight
            positioning = {
                "origin": expensive_origin,
                "destination": hub,
                "route_type": "positioning",
                "priority": "medium",
                "flight_type": f"Positioning ({expensive_origin}→{hub})"
            }
            hub_routes.append(positioning)
            
            # Hub'dan final destinations
            all_destinations = []
            for region, airports in self.destinations.items():
                all_destinations.extend(airports)
            
            for dest in all_destinations:
                main_route = {
                    "origin": hub,
                    "destination": dest,
                    "route_type": "hub_arbitrage",
                    "positioning_from": expensive_origin,
                    "priority": "high",
                    "flight_type": f"Hub Arbitrage ({expensive_origin}→{hub}→{dest})"
                }
                hub_routes.append(main_route)
        
        logger.info(f"🔄 Hub arbitrage routes generated: {len(hub_routes)}")
        return hub_routes
    
    def _generate_hidden_city_routes(self) -> List[Dict]:
        """
        Hidden city routing:
        Varış noktasında inmek daha ucuz olabilir!
        
        Example:
        - IST → LAX direkt: 35,000 TL
        - IST → SFO (LAX stopover): 25,000 TL → LAX'ta in!
        
        ⚠️ Risk: Bagaj ve dönüş bileti geçersiz olabilir
        """
        hidden_routes = []
        
        # Büyük hub'lar (stopover olabilecekler)
        potential_hidden_cities = ["LAX", "SFO", "JFK", "ORD", "DXB", "LHR", "CDG"]
        
        for origin in self.origins:
            for hidden in potential_hidden_cities:
                # Hidden city'den devam eden rotalar
                for final_dest in potential_hidden_cities:
                    if hidden != final_dest:
                        route = {
                            "origin": origin,
                            "destination": final_dest,
                            "hidden_city": hidden,
                            "route_type": "hidden_city",
                            "priority": "low",  # Riskli, düşük öncelik
                            "flight_type": f"Hidden City ({hidden})",
                            "warning": "⚠️ Bagaj riski! Sadece el bagajı tavsiye edilir."
                        }
                        hidden_routes.append(route)
        
        logger.info(f"🕵️ Hidden city routes generated: {len(hidden_routes)}")
        return hidden_routes
    
    def _generate_alternative_airports(self, destination: str, radius_km: int = 160) -> List[str]:
        """
        Alternatif havalimanları (160km çevre)
        
        Example:
        - NYC: JFK, EWR, LGA
        - Paris: CDG, ORY, BVA
        - London: LHR, LGW, STN, LTN
        """
        alternatives = {
            "JFK": ["EWR", "LGA"],  # New York area
            "LAX": ["SNA", "BUR", "ONT"],  # LA area
            "LHR": ["LGW", "STN", "LTN"],  # London area
            "CDG": ["ORY", "BVA"],  # Paris area
            "FCO": ["CIA"],  # Rome area
            "BER": ["SXF"],  # Berlin area
            "SFO": ["OAK", "SJC"],  # San Francisco area
            "ORD": ["MDW"],  # Chicago area
        }
        
        return alternatives.get(destination, [])
    
    def _prioritize_by_rss(self, routes: List[Dict], trending: Dict[str, int]) -> List[Dict]:
        """
        RSS trendlerine göre rotaları önceliklendir
        """
        for route in routes:
            dest = route['destination']
            if dest in trending:
                route['priority'] = 'critical'  # En yüksek öncelik
                route['trending_score'] = trending[dest]
            elif route.get('priority') == 'high':
                route['trending_score'] = 0
        
        # Sıralama: critical > high > medium > low
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        routes.sort(key=lambda x: (
            priority_order.get(x.get('priority', 'low'), 4),
            -x.get('trending_score', 0)
        ))
        
        return routes
    
    async def get_strategic_routes(self, max_routes: int = 50) -> List[Dict]:
        """
        Stratejik rota listesi üret:
        1. RSS trendlerini parse et
        2. Direkt rotalar (en yüksek öncelik)
        3. Hub arbitraj rotaları
        4. Hidden city rotaları (düşük öncelik)
        5. RSS'e göre önceliklendir
        6. Sample al (max_routes kadar)
        """
        try:
            # 1. RSS intelligence
            trending = self._parse_rss_feeds()
            
            # 2. Direkt rotalar (mutlak öncelik)
            direct_routes = self._generate_direct_routes()
            
            # 3. Hub arbitraj
            hub_routes = self._generate_hub_arbitrage_routes("IST")
            
            # 4. Hidden city (riskli, düşük öncelik)
            # hidden_routes = self._generate_hidden_city_routes()  # Şimdilik devre dışı
            
            # Tüm rotaları birleştir
            all_routes = direct_routes + hub_routes  # + hidden_routes
            
            # 5. RSS'e göre önceliklendir
            prioritized = self._prioritize_by_rss(all_routes, trending)
            
            # 6. Sample al
            # Critical routes: hepsini al
            # High routes: rastgele sample
            critical = [r for r in prioritized if r.get('priority') == 'critical']
            high = [r for r in prioritized if r.get('priority') == 'high']
            medium = [r for r in prioritized if r.get('priority') == 'medium']
            
            # Smart sampling
            selected = critical  # Tüm critical rotalar
            remaining = max_routes - len(selected)
            
            if remaining > 0:
                selected += random.sample(high, min(remaining, len(high)))
            
            remaining = max_routes - len(selected)
            if remaining > 0:
                selected += random.sample(medium, min(remaining, len(medium)))
            
            logger.info(f"🎯 Strategic routes: {len(selected)} routes selected")
            logger.info(f"   - Critical: {len(critical)}")
            logger.info(f"   - High: {len([r for r in selected if r.get('priority')=='high'])}")
            logger.info(f"   - Medium: {len([r for r in selected if r.get('priority')=='medium'])}")
            
            return selected[:max_routes]
            
        except Exception as e:
            logger.error(f"❌ Intel center error: {e}")
            # Fallback: basit rotalar
            return self._generate_direct_routes()[:max_routes]
    
    def calculate_hub_arbitrage_savings(self, direct_price: float, 
                                       positioning_price: float, 
                                       hub_price: float) -> Dict:
        """
        Hub arbitraj tasarruf hesaplama
        """
        total_hub_cost = positioning_price + hub_price
        savings = direct_price - total_hub_cost
        savings_percent = (savings / direct_price) * 100 if direct_price > 0 else 0
        
        return {
            "direct_price": direct_price,
            "hub_total": total_hub_cost,
            "savings": savings,
            "savings_percent": savings_percent,
            "recommendation": "HUB KULLAN" if savings > 0 else "DİREKT GİT"
        }