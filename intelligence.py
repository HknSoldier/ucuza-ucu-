"""
SNIPER INTELLIGENCE - GLOBAL HOLIDAY ROUTES
"""
class IntelligenceGatherer:
    def __init__(self):
        # Format: (Kalkış, Varış, [Aylar], Not, Maksimum Fiyat Limiti TL)
        self.HACK_ROUTES = [
            # --- UZAK DOĞU & EGZOTİK ---
            ('IST', 'BKK', [2, 3, 4, 11], '🇹🇭 TAYLAND', 26000),
            ('IST', 'HKT', [2, 3, 4, 11], '🇹🇭 PHUKET', 28000),
            ('IST', 'DPS', [3, 4, 5], '🇮🇩 BALİ', 30000),
            ('IST', 'MLE', [2, 3, 4], '🇲🇻 MALDİVLER', 27000),
            ('IST', 'NRT', [4, 5, 10], '🇯🇵 TOKYO', 32000),
            
            # --- AVRUPA POPÜLER ---
            ('IST', 'FCO', [3, 4, 5], '🇮🇹 ROMA', 7000),
            ('IST', 'MXP', [3, 4, 5], '🇮🇹 MİLANO', 6500),
            ('IST', 'CDG', [3, 4, 5], '🇫🇷 PARİS', 8000),
            ('IST', 'BCN', [4, 5, 6], '🇪🇸 BARSELONA', 9000),
            ('IST', 'AMS', [4, 5, 6], '🇳🇱 AMSTERDAM', 8500),
            ('IST', 'LHR', [3, 4, 5], '🇬🇧 LONDRA', 7000),
            
            # --- VİZESİZ / YAKIN ---
            ('IST', 'BEG', [3, 4, 5], '🇷🇸 BELGRAD', 5000),
            ('IST', 'TGD', [4, 5, 6], '🇲🇪 KARADAĞ', 6000),
            ('IST', 'SSH', [3, 4, 5], '🇪🇬 ŞARM EL ŞEYH', 7000),
            ('IST', 'DXB', [2, 3], '🇦🇪 DUBAİ', 10000),
            
            # --- İZMİR ÇIKIŞLI ---
            ('ADB', 'BER', [4, 5, 6], '🇩🇪 BERLİN (İzmir)', 6000),
            ('ADB', 'AMS', [4, 5, 6], '🇳🇱 AMSTERDAM (İzmir)', 7000),
        ]

    def get_target_routes(self):
        targets = []
        for r in self.HACK_ROUTES:
            targets.append({
                'origin': r[0], 'dest': r[1], 'months': r[2], 
                'note': r[3], 'hard_limit': r[4]
            })
        return targets
