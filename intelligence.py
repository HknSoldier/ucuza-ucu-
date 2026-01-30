import feedparser
import logging
import random

logger = logging.getLogger(__name__)

class IntelligenceGatherer:
    def __init__(self):
        # Çıkış Noktaları (Sofya Eklendi)
        self.TR_HUBS = [
            'IST', 'SAW', 'ADB', 'ESB', 'AYT', 'DLM', 'BJV', 'TZX', 
            'SOF' # 🇧🇬 Sofya Kapısı
        ]
        
        # Dünya Hedefleri
        self.GLOBAL_TARGETS = [
            'LON', 'PAR', 'AMS', 'BER', 'MUC', 'FRA', 'FCO', 'MXP', 'BCN', 'MAD',
            'NYC', 'LAX', 'MIA', 'JFK',
            'BKK', 'HKT', 'DPS', 'TYO', 'NRT', 'SIN', 'KUL', 'MLE',
            'DXB', 'DOH', 'AUH', 'CAI', 'SSH'
        ]

        self.INTEL_SOURCES = [
            'https://www.secretflying.com/euro-deals/feed/',
            'https://www.fly4free.com/flight-deals/europe/feed/'
        ]

    def fetch_external_signals(self):
        priority = []
        try:
            for source in self.INTEL_SOURCES:
                feed = feedparser.parse(source)
                for entry in feed.entries[:10]:
                    text = (entry.title + " " + entry.description).upper()
                    for dest in self.GLOBAL_TARGETS:
                        if dest in text: priority.append(dest)
        except: pass
        return list(set(priority))

    def get_mission_targets(self):
        signals = self.fetch_external_signals()
        targets = list(set(signals))
        
        while len(targets) < 25:
            choice = random.choice(self.GLOBAL_TARGETS)
            if choice not in targets: targets.append(choice)
        
        missions = []
        active_hubs = random.sample(self.TR_HUBS, 3) # 3 Farklı şehirden tara
        
        # Sofya Torpili
        if 'SOF' not in active_hubs and random.random() < 0.3:
            active_hubs.pop()
            active_hubs.append('SOF')

        for origin in active_hubs:
            for dest in targets:
                limit = 45000
                if origin == 'SOF': limit = 12000 # Sofya limiti
                elif dest in ['LON', 'PAR', 'BER']: limit = 15000
                
                missions.append({'origin': origin, 'dest': dest, 'hard_limit': limit})
        return missions
