# PROJECT TITAN - Configuration
# Although credentials are hardcoded, this file allows easy customization

class TitanConfig:
    """Configuration for PROJECT TITAN"""
    
    # Telegram Credentials (HARDCODED)
    TELEGRAM_BOT_TOKEN = "8161806410:AAH4tGpW_kCvQpLOfaB-r2OYQMypPVYtuYg"
    TELEGRAM_ADMIN_ID = 7684228928
    TELEGRAM_GROUP_ID = -1003515302846
    
    # Scraping Configuration
    SCRAPE_TIMEOUT = 60  # seconds
    MAX_RETRIES = 3
    RANDOM_SLEEP_MIN = 3  # seconds
    RANDOM_SLEEP_MAX = 8  # seconds
    
    # Route Configuration
    ORIGINS = ["IST", "SAW", "ADB", "ESB", "AYT", "TZX", "SOF"]
    
    DESTINATIONS = {
        "USA": ["JFK", "LAX", "ORD", "MIA", "BOS", "SFO", "SEA", "ATL"],
        "Europe": ["LHR", "CDG", "AMS", "FCO", "BCN", "BER", "MAD", "VIE"],
        "Asia": ["DXB", "BKK", "SIN", "HKG", "NRT", "ICN", "PEK"],
        "Oceania": ["SYD", "MEL", "AKL"],
        "Americas": ["GRU", "EZE", "MEX", "YYZ"]
    }
    
    # Price Thresholds (TRY)
    THRESHOLDS = {
        "SOF": {  # Sofia Hub - Super aggressive
            "JFK": 10000,
            "LAX": 12000,
            "ORD": 11000,
            "MIA": 10000,
            "BOS": 10000,
            "SFO": 12000,
            "default": 10000
        },
        "IST": {  # Istanbul - Main hub
            "JFK": 30000,
            "LAX": 35000,
            "ORD": 32000,
            "MIA": 28000,
            "BOS": 30000,
            "SFO": 35000,
            "default": 30000
        },
        "SAW": {  # Sabiha Gokcen
            "JFK": 28000,
            "LAX": 33000,
            "ORD": 30000,
            "MIA": 26000,
            "BOS": 28000,
            "default": 28000
        },
        "default": {
            "default": 30000
        }
    }
    
    # RSS Feeds for Intelligence
    RSS_FEEDS = [
        "https://www.secretflying.com/feed/",
        "https://www.fly4free.com/feed/",
        "https://www.theflightdeal.com/feed/",
        "https://www.goingtotheworld.com/feed/"
    ]
    
    # Date Range (days from now)
    DATE_RANGE_MIN = 90   # 3 months
    DATE_RANGE_MAX = 330  # 11 months
    
    # Trip Length (days)
    TRIP_LENGTH_MIN = 3
    TRIP_LENGTH_MAX = 14
    
    # Green Zone Detection (percentage)
    GREEN_ZONE_THRESHOLD = 0.8  # Price must be <= 80% of average
    PRICE_DROP_THRESHOLD = 0.85  # Alert if price drops below 85% of average
    
    # Sampling
    ROUTES_TO_SCAN = 20  # How many normal priority routes to sample
    DATES_PER_ROUTE = 5  # How many date combinations to try per route
    
    # State Management
    STATE_FILE = "titan_state.json"
    PRICE_HISTORY_SIZE = 10  # Keep last N prices per route
    
    # User Agents for Anti-Detection
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]
