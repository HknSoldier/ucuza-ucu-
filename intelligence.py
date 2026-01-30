import feedparser
import logging
import random

logger = logging.getLogger(__name__)

class IntelligenceGatherer:
    def __init__(self):
        # STRATEJİK ÇIKIŞ ÜSLERİ (Türkiye + Sofya Kapısı)
        self.STRATEGIC_HUBS = [
            'IST', 'SAW', # İstanbul (Ana Üs)
            'ADB', # İzmir (Avrupa Bağlantısı)
            'ESB', # Ankara
            'AYT', # Antalya (Turistik)
            'DLM', # Dalaman
            'BJV', # Bodrum
            'TZX', # Trabzon (Doğu Kapısı)
            'SOF'  # 🇧🇬 SOFYA (AVRUPA ARKA KAPISI - HACKER ROTASI)
        ]
        
        # Dünya Geneli Hedefler (Popüler)
        self.GLOBAL_TARGETS = [
            'LON', 'PAR', 'AMS', 'BER', 'MUC', 'FRA', 'FCO', 'MXP', 'BCN', 'MAD', # Avrupa
            'NYC', 'LAX', 'MIA', 'TOR', # Amerika
            'BKK', 'HKT', 'DPS', 'TYO', 'SEL', 'SIN', 'KUL', 'MLE', # Asya & Egzotik
            'DXB', 'DOH', 'AUH', 'CAI', 'SSH' # Orta Doğu & Afrika
        ]

        # Kampanya Kaynakları (Reddit & Deal Siteleri RSS)
        self.INTEL_SOURCES = [
            'https://www.secretflying.com/euro-deals/feed/',
            'https://www.fly4free.com/flight-deals/europe/feed/'
        ]

    def fetch_external_signals(self):
        """
        İnternetteki kampanya sinyallerini (RSS) tarar.
        """
        priority_destinations = []
        logger.info("📡 Dış İstihbarat (RSS/Reddit) taranıyor...")
        
        for source in self.INTEL_SOURCES:
            try:
                feed = feedparser.parse(source)
                for entry in feed.entries[:10]: # Son 10 habere bak
                    text = (entry.title + " " + entry.description).upper()
                    
                    # Eğer haberde hedef şehirlerimizden biri geçiyorsa
                    for dest in self.GLOBAL_TARGETS:
                        if dest in text or self._get_city_name(dest) in text:
                            if dest not in priority_destinations:
                                priority_destinations.append(dest)
                                logger.info(f"🚨 SİNYAL ALINDI: {dest} için kampanya var!")
            except:
                continue
                
        return priority_destinations

    def _get_city_name(self, code):
        names = {'LON': 'LONDON', 'PAR': 'PARIS', 'NYC': 'NEW YORK', 'BKK': 'BANGKOK', 'TYO': 'TOKYO'}
        return names.get(code, "UNKNOWN")

    def get_mission_targets(self):
        """
        Görev emrini oluşturur.
        Sofya dahil tüm üslerden rastgele 2 tanesini seçip tarama yapar.
        """
        signals = self.fetch_external_signals()
        
        # Sinyal gelen yerleri %100 listeye al
        targets = list(set(signals))
        
        # Geri kalan boşlukları popüler yerlerle doldur
        while len(targets) < 20:
            choice = random.choice(self.GLOBAL_TARGETS)
            if choice not in targets:
                targets.append(choice)
        
        # Rotaları Oluştur
        missions = []
        
        # Rastgele 2 veya 3 farklı çıkış noktasını seç (Örn: Bir turda IST ve SOF, diğerinde ADB ve SAW)
        # Bu sayede her çalışmada farklı kombinasyonlar denenir.
        active_hubs = random.sample(self.STRATEGIC_HUBS, 3) 
        
        # Eğer Sofya seçilmediyse, %30 şansla zorla ekle (Hacker Bonusu)
        if 'SOF' not in active_hubs and random.random() < 0.3:
            active_hubs.pop()
            active_hubs.append('SOF')
        
        logger.info(f"🏰 AKTİF ÜSLER: {active_hubs} (Bu turda buradan kalkış yapılacak)")

        for origin in active_hubs:
            for dest in targets:
                # Fiyat Limitleri: Sofya çıkışlı ise limit daha düşük olmalı (Daha ucuz olduğu için)
                limit = 40000
                if origin == 'SOF':
                    limit = 15000 # Sofya'dan 15k üstü pahalıdır
                
                missions.append({
                    'origin': origin,
                    'dest': dest,
                    'hard_limit': limit 
                })
                
        logger.info(f"⚔️ GÖREV EMRİ: {len(missions)} rota oluşturuldu.")
        return missions
