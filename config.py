# PROJECT TITAN V2.3 - Enterprise Configuration
# 🦅 Autonomous Flight Intel System - Production Ready

import os
from datetime import time
from typing import Dict, List

class TitanConfig:
    """Enterprise-grade configuration with Ghost Protocol & Anti-Spam"""
    
    # ==================== TELEGRAM CREDENTIALS ====================
    # Hardcoded bot credentials
    TELEGRAM_BOT_TOKEN = "8161806410:AAH4tGpW_kCvQpLOfaB-r2OYQMypPVYtuYg"
    TELEGRAM_ADMIN_ID = 7684228928
    TELEGRAM_GROUP_ID = -1003515302846
    
    # ==================== GHOST PROTOCOL (ZAMAN KURALLARI) ====================
    # ⚠️ GÜNCELLEME: Sabah fırsatlarını kaçırmamak için 07:00'ye çekildi
    ACTIVE_HOURS_WEEKDAY = (time(7, 0), time(23, 0))   # 07:00 - 23:00
    ACTIVE_HOURS_WEEKEND = (time(11, 0), time(23, 0))  # 11:00 - 23:00
    
    # BYPASS: Mistake fare (%70 indirim) için zaman kuralını yok say
    MISTAKE_FARE_THRESHOLD = 0.30 
    
    # ==================== SAMPLING & PERFORMANCE (TIMEOUT FIX) ====================
    # ⚠️ GÜNCELLEME: GitHub Actions timeout yememek için düşürüldü
    ROUTES_TO_SCAN = 15   # Her döngüde taranacak rota sayısı (Eski: 30)
    DATES_PER_ROUTE = 4   # Her rota için denenecek tarih sayısı (Eski: 5)
    
    # ==================== ALARM FILTER (GERÇEK FIRSATLAR) ====================
    # Sadece gerçek dip fiyatlarda alarm (90 günlük en düşük x 1.05)
    ALARM_PRICE_MULTIPLIER = 1.05 
    
    # ==================== ANTI-SPAM SINIRLAMALARI ====================
    MAX_ALERTS_PER_ROUTE_PER_DAY = 1  # Aynı rota için max 1 alarm/24h
    MAX_TOTAL_ALERTS_PER_DAY = 3      # Toplam max 3 alarm/gün
    
    # ==================== DİP AVCISI ESIKLERI ====================
    PRICE_BOTTOM_MULTIPLIER = 1.05  # Dip fiyat = En düşük × 1.05
    PRICE_NORMAL_MULTIPLIER = 1.0   # Normal = Ortalama
    
    # ==================== STRATEJİK HAVAALANLARI ====================
    # Ana kalkış noktaları (Türkiye + Sofia hub)
    ORIGINS = ["IST", "SAW", "ADB", "ESB", "AYT", "TZX", "SOF"]
    
    # Hedef destinasyonlar
    DESTINATIONS = {
        "USA": ["JFK", "LAX", "ORD", "MIA", "BOS", "SFO", "SEA", "ATL", "IAD"],
        "Europe": ["LHR", "CDG", "AMS", "FCO", "BCN", "BER", "MAD", "VIE", "ZRH"],
        "Asia": ["DXB", "BKK", "SIN", "HKG", "NRT", "ICN", "PEK", "DEL"],
        "Oceania": ["SYD", "MEL", "AKL"],
        "Americas": ["GRU", "EZE", "MEX", "YYZ", "YVR"],
        "Middle_East": ["CAI", "TLV", "AMM", "BEY"]
    }
    
    # Hub arbitraj alternatifleri
    HUB_ALTERNATIVES = {
        "IST": ["SOF", "AUH", "DOH"],  # İstanbul pahalıysa bu hub'lara bak
        "SAW": ["SOF", "SKG", "OTP"],
        "ADB": ["SOF", "ATH", "SKG"]
    }
    
    # ==================== VİZE KONTROL (YEŞİL PASAPORT) ====================
    VISA_FREE_ZONES = ["EU", "Schengen"]  # Yeşil pasaport ile vizesiz
    VISA_REQUIRED = ["USA", "UK", "CA", "AU"]  # Vize gerekli uyarısı
    
    # ==================== SCRAPING AYARLARI ====================
    SCRAPE_TIMEOUT = 60  # saniye
    MAX_RETRIES = 3
    RANDOM_SLEEP_MIN = 2  # saniye
    RANDOM_SLEEP_MAX = 7  # saniye
    MAX_REQUESTS_PER_10_SEC = 3
    
    # ==================== PROXY AYARLARI ====================
    USE_PROXY = True
    MIN_IP_REPUTATION_SCORE = 0.4 
    
    # ==================== TARİH ARALIĞI ====================
    DATE_RANGE_MIN = 90    # 3 ay sonrası
    DATE_RANGE_MAX = 330   # 11 ay sonrası
    TRIP_LENGTH_MIN = 3
    TRIP_LENGTH_MAX = 14
    
    # ==================== FİYAT EŞİKLERİ (ROUTE BAZLI) ====================
    THRESHOLDS = {
        "SOF": {  # Sofia hub - SUPER AGGRESSIVE
            "JFK": 10000, "LAX": 12000, "ORD": 11000,
            "MIA": 10000, "BOS": 10000, "SFO": 12000,
            "default": 10000
        },
        "IST": {  # Istanbul - Main hub
            "JFK": 30000, "LAX": 35000, "ORD": 32000,
            "MIA": 28000, "BOS": 30000, "SFO": 35000,
            "default": 30000
        },
        "SAW": {  # Sabiha Gokcen
            "JFK": 28000, "LAX": 33000, "ORD": 30000,
            "MIA": 26000, "BOS": 28000, "default": 28000
        },
        "default": {"default": 30000}
    }
    
    # ==================== EKSTRA MALİYETLER ====================
    BAGGAGE_COSTS = {
        "Pegasus": {"cabin": 150, "checked": 400},
        "AnadoluJet": {"cabin": 120, "checked": 350},
        "Turkish Airlines": {"cabin": 0, "checked": 0},
        "default": {"cabin": 100, "checked": 300}
    }
    
    REMOTE_AIRPORT_TRANSPORT = {
        "BVA": 25, "HHN": 20, "NYO": 15, "CIA": 10
    }
    
    MIN_SAFE_TRANSFER_TIME = 4  # saat
    
    # ==================== RSS FEEDLER ====================
    RSS_FEEDS = [
        "https://www.secretflying.com/feed/",
        "https://www.fly4free.com/feed/",
        "https://www.theflightdeal.com/feed/",
        "https://www.goingtotheworld.com/feed/"
    ]
    
    # ==================== DURUM & ANOMALİ ====================
    STATE_FILE = "titan_state.json"
    PRICE_HISTORY_SIZE = 90
    MIN_SANE_PRICE = 100
    MAX_SANE_PRICE = 500000
    MIN_PRICE_VARIANCE = 2
    MAX_FAILURE_RATE = 0.30
    
    # ==================== USER AGENTS ====================
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]
    
    # ==================== MİL ARBITRAJ & OPTİMAL ZAMAN ====================
    MILE_PURCHASE_RATE = {
        "TurkishAirlines": 0.02,
        "default": 0.025
    }
    
    OPTIMAL_PURCHASE_WINDOW = {
        "start_day": 1, "start_hour": 15,  # Salı 15:00
        "end_day": 3, "end_hour": 10       # Perşembe 10:00
    }
