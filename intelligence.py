import feedparser
import logging
import random

logger = logging.getLogger(__name__)

class IntelligenceGatherer:
    def __init__(self):
        # Türkiye'nin Tüm Uluslararası Hub'ları
        self.TR_HUBS = [
            'IST', 'SAW', # İstanbul
            'ADB', # İzmir
            'ESB', # Ankara
            'AYT', # Antalya
            'DLM', # Dalaman
            'BJV', # Bodrum
            'TZX'  # Trabzon
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
        Eğer 'New York' indirimi görürse, listeye NYC'yi öncelikli ekler.
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
        1. Dış sinyalleri (Kampanyaları) al.
        2. Rastgele Türkiye çıkış noktası seç (Cache mantığı).
        3. Rotaları oluştur.
        """
        signals = self.fetch_external_signals()
        
        # Sinyal gelen yerleri %100 listeye al
        targets = list(set(signals))
        
        # Geri kalan boşlukları popüler yerlerle doldur (Toplam 20 hedef olsun)
        while len(targets) < 20:
            choice = random.choice(self.GLOBAL_TARGETS)
            if choice not in targets:
                targets.append(choice)
        
        # Rotaları Oluştur
        missions = []
        
        # Her çalışma döngüsünde Türkiye'den 2 farklı çıkış noktasını tara (Yükü dağıtmak için)
        active_hubs = random.sample(self.TR_HUBS, 2) 
        
        for origin in active_hubs:
            for dest in targets:
                missions.append({
                    'origin': origin,
                    'dest': dest,
                    'hard_limit': 40000 # Üst limit
                })
                
        logger.info(f"⚔️ GÖREV EMRİ: {len(missions)} rota oluşturuldu. Öncelik: {signals}")
        return missions
