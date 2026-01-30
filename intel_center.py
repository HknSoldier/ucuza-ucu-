# intel_center.py - Intelligence & Route Generation
import logging
import feedparser
from typing import List, Dict
import random

logger = logging.getLogger(__name__)

class IntelCenter:
    """
    Intelligence gathering center
    - Parses RSS feeds for trending deals
    - Generates strategic routes with hub logic
    """
    
    def __init__(self):
        self.rss_feeds = [
            "https://www.secretflying.com/feed/",
            "https://www.fly4free.com/feed/",
            "https://www.theflightdeal.com/feed/"
        ]
        
        # Strategic origins (Turkish airports + Sofia hub)
        self.origins = ["IST", "SAW", "ADB", "ESB", "AYT", "TZX", "SOF"]
        
        # High-value destinations
        self.destinations = {
            "USA": ["JFK", "LAX", "ORD", "MIA", "BOS", "SFO", "SEA"],
            "Europe": ["LHR", "CDG", "AMS", "FCO", "BCN", "BER"],
            "Asia": ["DXB", "BKK", "SIN", "HKG", "NRT"],
            "Oceania": ["SYD", "MEL"]
        }
    
    def _parse_rss_feeds(self) -> List[str]:
        """
        Parse RSS feeds and extract trending destinations
        """
        trending = set()
        
        for feed_url in self.rss_feeds:
            try:
                logger.info(f"Parsing RSS feed: {feed_url}")
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:10]:  # Top 10 entries
                    title = entry.get('title', '').upper()
                    # Extract airport codes (3 letters)
                    import re
                    codes = re.findall(r'\b[A-Z]{3}\b', title)
                    trending.update(codes)
                    
            except Exception as e:
                logger.warning(f"Failed to parse {feed_url}: {e}")
                continue
        
        logger.info(f"Trending destinations from RSS: {trending}")
        return list(trending)
    
    def _generate_base_routes(self) -> List[Dict]:
        """
        Generate base route matrix
        """
        routes = []
        
        # Combine all destinations
        all_destinations = []
        for region, airports in self.destinations.items():
            all_destinations.extend(airports)
        
        # Generate routes from each origin to each destination
        for origin in self.origins:
            for dest in all_destinations:
                routes.append({
                    "origin": origin,
                    "destination": dest,
                    "priority": "normal"
                })
        
        return routes
    
    def _prioritize_routes(self, routes: List[Dict], trending: List[str]) -> List[Dict]:
        """
        Prioritize routes based on RSS intel
        """
        for route in routes:
            if route['destination'] in trending:
                route['priority'] = "high"
        
        # Sort by priority
        routes.sort(key=lambda x: 0 if x['priority'] == "high" else 1)
        
        return routes
    
    async def get_priority_routes(self) -> List[Dict]:
        """
        Get prioritized list of routes to scan
        Combines RSS intelligence with strategic hub logic
        """
        try:
            # Parse RSS feeds for trending destinations
            trending = self._parse_rss_feeds()
            
            # Generate base routes
            routes = self._generate_base_routes()
            
            # Prioritize based on RSS intel
            routes = self._prioritize_routes(routes, trending)
            
            # Sample routes (don't scan all at once to avoid detection)
            # High priority: all
            # Normal priority: random sample
            high_priority = [r for r in routes if r['priority'] == "high"]
            normal_priority = [r for r in routes if r['priority'] == "normal"]
            
            # Take all high priority + 20 random normal priority
            sampled = high_priority + random.sample(
                normal_priority, 
                min(20, len(normal_priority))
            )
            
            logger.info(f"Generated {len(sampled)} routes for scanning ({len(high_priority)} high priority)")
            
            return sampled
            
        except Exception as e:
            logger.error(f"Error in intel center: {e}")
            # Return basic routes as fallback
            return self._generate_base_routes()[:20]
