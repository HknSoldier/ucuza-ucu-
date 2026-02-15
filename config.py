# PROJECT TITAN V2.5 - PROFESSIONAL FLIGHT HACKER
# 🎯 Industry secrets + One-way combinations + Night scanning

import os
from datetime import time, datetime, timedelta
from typing import Dict, List

class TitanConfig:
    """V2.5: Professional flight hacker with industry insider knowledge"""
    
    # ==================== TELEGRAM CREDENTIALS ====================
    TELEGRAM_BOT_TOKEN = "8161806410:AAH4tGpW_kCvQpLOfaB-r2OYQMypPVYtuYg"
    TELEGRAM_ADMIN_ID = 7684228928
    TELEGRAM_GROUP_ID = -1003515302846
    
    # ==================== V2.5 FLIGHT HACKER RULES ====================
    
    # 🕐 RULE 1: Sweet Spot Booking Window
    # "6-8 hafta önceden en ucuz"
    # ⚠️ KRİTİK: Sadece bu aralıktaki tarihleri tara!
    DATE_RANGE_MIN = 42      # 6 hafta = 42 gün
    DATE_RANGE_MAX = 56      # 8 hafta = 56 gün
    SWEET_SPOT_WINDOW = (42, 56)  # En ucuz booking window
    
    # Sweet spot ENFORCEMENT
    ENFORCE_SWEET_SPOT = True  # True = SADECE 6-8 hafta arası tara
    
    # 🕐 RULE 2: Price Update Days
    # "Salı-Çarşamba sistem fiyat güncellemesi"
    PRICE_UPDATE_DAYS = [1, 2]  # Monday=0, Tuesday=1, Wednesday=2
    PREFER_UPDATE_DAYS = True
    
    # 🕐 RULE 3: Night Scanning + Morning Alert
    # "Gece 02:00-05:00 ara, sabah 09:00'dan önce mesaj gönderme"
    SCAN_HOURS = (time(2, 0), time(5, 0))    # Gece 02:00-05:00 tarama
    ALERT_HOURS = (time(9, 0), time(23, 0))  # Sabah 09:00-23:00 mesaj
    QUEUE_NIGHT_ALERTS = True  # Gece bulunan fırsatları sabaha ertele
    
    # 🎯 RULE 4: One-Way Search Strategy
    # "Gidiş-dönüş yerine tek yön + kombinasyon"
    SEARCH_STRATEGY = "one_way_combo"  # "round_trip" veya "one_way_combo"
    ONE_WAY_ENABLED = True
    COMBINE_ONE_WAYS = True  # Gidiş + Dönüş kombinasyonunu oluştur
    
    # 📅 RULE 5: Day-of-Week Pricing
    # "Cuma akşamı pahalı, Pazar dönüş pahalı, Sabah uçuşları ucuz"
    EXPENSIVE_DEPARTURE_DAYS = [4]  # Friday=4 (Cuma akşamı)
    EXPENSIVE_RETURN_DAYS = [6]     # Sunday=6 (Pazar)
    CHEAP_DEPARTURE_TIMES = (time(6, 0), time(12, 0))  # Sabah 06:00-12:00
    PREFER_MORNING_FLIGHTS = True
    AVOID_FRIDAY_EVENING = True  # Cuma akşamı atla
    AVOID_SUNDAY_RETURN = True   # Pazar dönüş atla
    
    # 🛫 RULE 6: Small Airport Strategy
    # "Küçük havalimanları yüzlerce TL ucuz olabilir"
    CHECK_ALTERNATIVE_AIRPORTS = True
    SMALL_AIRPORTS = {
        # Istanbul alternatif
        "IST": ["SAW"],  # Sabiha Gökçen alternatif
        "SAW": ["IST"],  # Atatürk alternatif
        
        # New York alternatif
        "JFK": ["EWR", "LGA"],  # Newark, LaGuardia
        "EWR": ["JFK", "LGA"],
        "LGA": ["JFK", "EWR"],
        
        # London alternatif
        "LHR": ["LGW", "STN", "LTN"],  # Gatwick, Stansted, Luton
        "LGW": ["LHR", "STN", "LTN"],
        
        # Paris alternatif
        "CDG": ["ORY", "BVA"],  # Orly, Beauvais
        "ORY": ["CDG", "BVA"],
        
        # Milan alternatif
        "MXP": ["LIN", "BGY"],  # Linate, Bergamo
        
        # Barcelona alternatif
        "BCN": ["GRO", "REU"],  # Girona, Reus
        
        # Los Angeles alternatif
        "LAX": ["BUR", "SNA", "ONT"],  # Burbank, Orange County, Ontario
        
        # San Francisco alternatif
        "SFO": ["OAK", "SJC"],  # Oakland, San Jose
        
        # Chicago alternatif
        "ORD": ["MDW"],  # Midway
        
        # Berlin alternatif
        "BER": ["SXF"],  # Schönefeld
        
        # Rome alternatif
        "FCO": ["CIA"],  # Ciampino
    }
    
    # 🎒 RULE 7: Baggage Cost Calculation
    # "Valiz hakkını hesaba kat - standart 20 kg"
    INCLUDE_BAGGAGE_COST = True
    STANDARD_BAGGAGE_WEIGHT = 20  # kg
    
    BAGGAGE_COSTS = {
        "Turkish Airlines": {
            "cabin": 0,      # 8 kg kabin dahil
            "checked_20": 0, # 20 kg bavul dahil (ekonomi)
        },
        "Pegasus": {
            "cabin": 150,    # 8 kg kabin
            "checked_20": 400,  # 20 kg bavul
        },
        "AnadoluJet": {
            "cabin": 120,
            "checked_20": 350,
        },
        "Lufthansa": {
            "cabin": 0,
            "checked_20": 0,  # Dahil (ekonomi)
        },
        "United Airlines": {
            "cabin": 0,
            "checked_20": 0,  # Dahil
        },
        "Emirates": {
            "cabin": 0,
            "checked_20": 0,  # 30 kg dahil!
        },
        "Qatar Airways": {
            "cabin": 0,
            "checked_20": 0,  # 30 kg dahil!
        },
        "Ryanair": {
            "cabin": 200,    # Ek ücret
            "checked_20": 800,  # Çok pahalı!
        },
        "WizzAir": {
            "cabin": 180,
            "checked_20": 700,
        },
        "default": {
            "cabin": 100,
            "checked_20": 300,  # Ortalama
        }
    }
    
    # 🕐 RULE 8: Flexible Time Windows
    # "Esnek zaman dilimlerini tarayarak en ucuz kombinasyonu bul"
    FLEXIBLE_DATES = True
    DATE_FLEXIBILITY_DAYS = 3  # ±3 gün esneklik
    
    # Esnek zaman dilimleri (sabah/öğle/akşam)
    TIME_WINDOWS = {
        "early_morning": (time(0, 0), time(6, 0)),    # 00:00-06:00
        "morning": (time(6, 0), time(12, 0)),         # 06:00-12:00 (EN UCUZ)
        "afternoon": (time(12, 0), time(18, 0)),      # 12:00-18:00
        "evening": (time(18, 0), time(23, 59)),       # 18:00-23:59 (PAHALI)
    }
    
    PREFERRED_TIME_WINDOWS = ["morning", "afternoon"]  # Sabah ve öğle
    AVOID_TIME_WINDOWS = ["evening"]  # Akşam pahalı
    
    # ==================== CORE SETTINGS (V2.4'TEN DEVAM) ====================
    
    # Direkt uçuşlar
    DIRECT_FLIGHTS_ONLY = True
    MAX_STOPS = 0
    
    # Multi-source scraping
    SCRAPING_SOURCES = {
        "google_flights": True,
        "kayak": True,
        "momondo": False,  # Opsiyonel
    }
    
    SOURCE_WEIGHTS = {
        "google_flights": 1.0,
        "kayak": 0.9,
        "momondo": 0.9,
    }
    
    # Ultra-aggressive pricing
    MIN_DISCOUNT_THRESHOLD = 0.30
    ULTRA_DEAL_THRESHOLD = 0.40
    MISTAKE_FARE_THRESHOLD = 0.60
    
    # Tatil günleri
    AVOID_HOLIDAYS = True
    TURKISH_HOLIDAYS = [
        "2026-01-01", "2026-03-21", "2026-03-22", "2026-03-23",
        "2026-05-27", "2026-05-28", "2026-05-29", "2026-05-30",
        "2026-04-23", "2026-05-01", "2026-05-19",
        "2026-08-30", "2026-10-29",
    ]
    
    # Optimal aylar
    OPTIMAL_MONTHS = [3, 4, 5, 9, 10, 11]
    EXPENSIVE_MONTHS = [6, 7, 8, 12, 1]
    AVOID_SUMMER_PEAK = True
    
    # Ghost Protocol
    ACTIVE_HOURS_WEEKDAY = (time(9, 0), time(23, 0))  # Mesaj için
    ACTIVE_HOURS_WEEKEND = (time(11, 0), time(23, 0))
    
    # Anti-spam
    MAX_ALERTS_PER_ROUTE_PER_DAY = 1
    MAX_TOTAL_ALERTS_PER_DAY = 5
    
    # Sampling
    ROUTES_TO_SCAN = 20
    DATES_PER_ROUTE = 8  # Artırıldı (esnek tarih için)
    
    # ==================== HAVAALANLARI ====================
    
    ORIGINS = ["IST", "SAW", "ADB", "ESB", "AYT"]
    
    DESTINATIONS = {
        "USA_DIRECT": {
            "JFK": {"min_weekly_flights": 14, "airlines": ["TK", "UA"]},
            "EWR": {"min_weekly_flights": 7, "airlines": ["TK", "UA"]},
            "IAD": {"min_weekly_flights": 7, "airlines": ["TK", "UA"]},
            "ORD": {"min_weekly_flights": 7, "airlines": ["TK", "UA"]},
            "LAX": {"min_weekly_flights": 7, "airlines": ["TK"]},
            "SFO": {"min_weekly_flights": 7, "airlines": ["TK", "UA"]},
            "MIA": {"min_weekly_flights": 7, "airlines": ["TK"]},
            "BOS": {"min_weekly_flights": 7, "airlines": ["TK"]},
        },
        "EUROPE_DIRECT": {
            "LHR": {"min_weekly_flights": 35, "airlines": ["TK", "BA"]},
            "CDG": {"min_weekly_flights": 21, "airlines": ["TK", "AF"]},
            "AMS": {"min_weekly_flights": 21, "airlines": ["TK", "KL"]},
            "FRA": {"min_weekly_flights": 28, "airlines": ["TK", "LH"]},
            "MUC": {"min_weekly_flights": 21, "airlines": ["TK", "LH"]},
            "FCO": {"min_weekly_flights": 21, "airlines": ["TK", "AZ"]},
            "BCN": {"min_weekly_flights": 14, "airlines": ["TK", "VY"]},
            "MAD": {"min_weekly_flights": 14, "airlines": ["TK", "IB"]},
            "VIE": {"min_weekly_flights": 21, "airlines": ["TK", "OS"]},
            "BER": {"min_weekly_flights": 14, "airlines": ["TK"]},
            "ZRH": {"min_weekly_flights": 14, "airlines": ["TK", "LX"]},
        },
        "ASIA_DIRECT": {
            "DXB": {"min_weekly_flights": 35, "airlines": ["TK", "EK"]},
            "BKK": {"min_weekly_flights": 14, "airlines": ["TK"]},
            "SIN": {"min_weekly_flights": 14, "airlines": ["TK", "SQ"]},
            "HKG": {"min_weekly_flights": 7, "airlines": ["TK", "CX"]},
            "NRT": {"min_weekly_flights": 7, "airlines": ["TK", "NH"]},
            "ICN": {"min_weekly_flights": 7, "airlines": ["TK", "KE"]},
        },
    }
    
    # ==================== FİYAT EŞİKLERİ ====================
    
    THRESHOLDS = {
        "IST": {
            # ABD
            "JFK": 25000, "EWR": 24000, "IAD": 24000, "ORD": 26000,
            "LAX": 28000, "SFO": 28000, "MIA": 26000, "BOS": 25000,
            # Avrupa
            "LHR": 4000, "CDG": 3500, "AMS": 3500, "FRA": 3000,
            "MUC": 3500, "FCO": 3500, "BCN": 3000, "MAD": 3000,
            "VIE": 3000, "BER": 3000, "ZRH": 4000,
            # Asya
            "DXB": 3000, "BKK": 12000, "SIN": 13000,
            "HKG": 15000, "NRT": 16000, "ICN": 14000,
            "default": 15000
        },
        "default": {"default": 15000}
    }
    
    # ==================== SCRAPING ====================
    
    SCRAPE_TIMEOUT = 90
    MAX_RETRIES = 3
    RANDOM_SLEEP_MIN = 3
    RANDOM_SLEEP_MAX = 8
    MAX_REQUESTS_PER_10_SEC = 2
    
    USE_PROXY = True
    MIN_IP_REPUTATION_SCORE = 0.4
    
    TRIP_LENGTH_MIN = 5
    TRIP_LENGTH_MAX = 14
    
    # ==================== REMOTE AIRPORT TRANSPORT ====================
    
    REMOTE_AIRPORT_TRANSPORT = {
        "BVA": 25,   # Paris Beauvais
        "HHN": 20,   # Frankfurt Hahn
        "NYO": 15,   # Stockholm Skavsta
        "CIA": 10,   # Rome Ciampino
        "BGY": 15,   # Milan Bergamo
        "GRO": 20,   # Barcelona Girona
        "STN": 15,   # London Stansted
        "LTN": 20,   # London Luton
    }
    
    # ==================== DURUM & ANOMALİ ====================
    
    STATE_FILE = "titan_state.json"
    PRICE_HISTORY_SIZE = 120
    MIN_SANE_PRICE = 500
    MAX_SANE_PRICE = 500000
    MIN_PRICE_VARIANCE = 2
    MAX_FAILURE_RATE = 0.30
    
    # ==================== RSS ====================
    
    RSS_FEEDS = [
        "https://www.secretflying.com/feed/",
        "https://www.fly4free.com/feed/",
        "https://www.theflightdeal.com/feed/",
        "https://www.goingtotheworld.com/feed/",
        "https://thepointsguy.com/feed/",
    ]
    
    # ==================== USER AGENTS ====================
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15'
    ]
    
    # ==================== HAVAYOLU FILTRELEME ====================
    
    PREFERRED_AIRLINES = [
        "Turkish Airlines", "Lufthansa", "United Airlines",
        "Emirates", "Qatar Airways", "Singapore Airlines",
        "KLM", "Air France", "British Airways",
    ]
    
    BLACKLIST_AIRLINES = ["Ryanair", "WizzAir", "EasyJet"]
    
    # ==================== V2.5 SCRAPING STRATEGY ====================
    
    SOURCE_RETRY_STRATEGY = {
        "google_flights": 3,
        "kayak": 2,
        "momondo": 2,
    }
