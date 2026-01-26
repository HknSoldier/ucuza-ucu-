"""
SNIPER INTELLIGENCE - WORLDWIDE TARGETS
"""
class IntelligenceGatherer:
    def __init__(self):
        # Merkez Üslerimiz
        self.HUBS = ['IST', 'SAW', 'ADB', 'ESB', 'AYT']
        
        # Hedef Bölgeler (Popüler Havalimanları)
        self.TARGETS = [
            # AVRUPA
            'LHR', 'LGW', 'CDG', 'AMS', 'FRA', 'MUC', 'BER', 'FCO', 'MXP', 'MAD', 
            'BCN', 'LIS', 'OPO', 'VIE', 'PRG', 'BUD', 'ATH', 'WAW', 'ZRH', 'GVA',
            'OSL', 'ARN', 'CPH', 'DUB', 'BRU', 'BEG', 'TGD', 'SJJ', 'TIA', 'SKP',
            
            # ASYA & ORTA DOĞU
            'DXB', 'AUH', 'DOH', 'JED', 'RUH', 'KWI', 'BAH', 'MCT', 'BKK', 'HKT',
            'SIN', 'KUL', 'CGK', 'DPS', 'HAN', 'SGN', 'TYO', 'NRT', 'KIX', 'ICN',
            'PEK', 'PVG', 'HKG', 'BOM', 'DEL', 'MLE', 'CMB',
            
            # AMERİKA
            'JFK', 'EWR', 'LAX', 'MIA', 'ORD', 'SFO', 'IAD', 'BOS', 'YYZ', 'YUL',
            'GRU', 'GIG', 'BOG', 'EZE', 'MEX', 'CUN',
            
            # AFRİKA
            'CAI', 'SSH', 'HRG', 'CMN', 'RAK', 'TUN', 'JNB', 'CPT', 'NBO', 'ZNZ'
        ]
        
        # Aylar: Önümüzdeki 6 ay
        self.MONTHS = [2, 3, 4, 5, 6, 7]

    def get_all_combinations(self):
        """Tüm kombinasyonları üretir"""
        routes = []
        for origin in self.HUBS:
            for dest in self.TARGETS:
                # Aynı şehre uçuş arama
                if origin == dest: continue
                
                # Fiyat Limiti (Bölgeye göre dinamik limit)
                limit = 35000 # Varsayılan yüksek limit
                
                # Avrupa ise limit düşük
                if dest in ['LHR', 'CDG', 'BER', 'AMS']: limit = 10000
                # Asya ise orta
                if dest in ['BKK', 'TYO', 'SIN']: limit = 30000
                
                routes.append({
                    'origin': origin,
                    'dest': dest,
                    'months': self.MONTHS,
                    'hard_limit': limit
                })
        return routes
