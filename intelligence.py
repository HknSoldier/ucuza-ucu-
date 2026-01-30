import feedparser
import logging
import random

logger = logging.getLogger(__name__)

class IntelligenceGatherer:
    def __init__(self):
        # 🌍 STRATEJİK ÇIKIŞ ÜSLERİ (Türkiye + Sofya)
        self.HUBS = [
            'IST', 'SAW', # İstanbul (Ana Üs)
            'ADB', # İzmir (Avrupa Bağlantısı)
            'ESB', # Ankara
            'AYT', # Antalya
            'DLM', # Dalaman
            'BJV', # Bodrum
            'TZX', # Trabzon
            'SOF'  # 🇧🇬 SOFYA (Avrupa'ya Gizli Kapı)
        ]
        
        # 🎯 DÜNYA HEDEFLERİ
        self.GLOBAL_TARGETS = [
            'LON', 'PAR', 'AMS', 'BER', 'MUC', 'FRA', 'FCO', 'MXP', 'BCN', 'MAD', # Avrupa
            'NYC', 'LAX', 'MIA', 'JFK', # Amerika
            'BKK', 'HKT', 'DPS', 'TYO', 'NRT', 'SIN', 'KUL', 'MLE', # Asya & Egzotik
            'DXB', 'DOH', 'AUH', 'CAI', 'SSH' # Orta Doğu & Afrika
        ]

        # 📡 SİNYAL KAYNAKLARI
        self.INTEL_SOURCES = [
            'https://www.secretflying.com/euro-deals/feed/',
            'https://www.fly4free.com/flight-deals/europe/feed/'
        ]

    def fetch_external_signals(self):
        """RSS Kaynaklarını tarar ve sıcak bölgeleri tespit eder"""
        priority_destinations = []
        logger.info("📡 Dış İstihbarat (RSS/Reddit) taranıyor...")
        
        for source in self.INTEL_SOURCES:
            try:
                feed = feedparser.parse(source)
                for entry in feed.entries[:15]: 
                    text = (entry.title + " " + entry.description).upper()
                    for dest in self.GLOBAL_TARGETS:
                        if dest in text or self._get_city_name(dest) in text:
                            if dest not in priority_destinations:
                                priority_destinations.append(dest)
                                logger.info(f"🚨 SİNYAL ALINDI: {dest} için kampanya var!")
            except: continue
        return priority_destinations

    def _get_city_name(self, code):
        names = {'LON': 'LONDON', 'PAR': 'PARIS', 'NYC': 'NEW YORK', 'BKK': 'BANGKOK', 'TYO': 'TOKYO'}
        return names.get(code, "UNKNOWN")

    def get_mission_targets(self):
        signals = self.fetch_external_signals()
        targets = list(set(signals)) 
        
        while len(targets) < 25:
            choice = random.choice(self.GLOBAL_TARGETS)
            if choice not in targets: targets.append(choice)
        
        missions = []
        
        # Rastgele 3 merkez seç (Sofya'nın seçilme şansını artırmak için manuel kontrol eklenebilir)
        active_hubs = random.sample(self.HUBS, 3)
        
        # %30 Şansla Sofya'yı zorla listeye sok (Hacker Bonusu)
        if 'SOF' not in active_hubs and random.random() < 0.3:
            active_hubs.pop()
            active_hubs.append('SOF')
            logger.info("🇧🇬 Hacker Rotası Aktif: SOFYA (SOF) listeye eklendi.")
        
        for origin in active_hubs:
            for dest in targets:
                # FİYAT ZEKASI:
                limit = 45000
                
                # 1. Sofya'dan uçuyorsak limit çok düşük olmalı (Zaten ucuz)
                if origin == 'SOF':
                    limit = 12000
                
                # 2. Avrupa hedefliysek limit orta olmalı
                elif dest in ['LON', 'PAR', 'BER', 'AMS', 'FCO']:
                    limit = 15000
                
                missions.append({'origin': origin, 'dest': dest, 'hard_limit': limit})
                
        logger.info(f"⚔️ GÖREV EMRİ: {active_hubs} çıkışlı {len(missions)} rota taranacak.")
        return missions
