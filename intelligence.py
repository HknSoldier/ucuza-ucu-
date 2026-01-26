class IntelligenceGatherer:
    def __init__(self):
        self.HACK_ROUTES = [
            ('IST', 'BKK', [2, 3, 4, 11], '🇹🇭 TAYLAND', 26000),
            ('IST', 'HKT', [2, 3, 4, 11], '🇹🇭 PHUKET', 28000),
            ('IST', 'MLE', [2, 3, 4], '🇲🇻 MALDİVLER', 27000),
            ('IST', 'FCO', [3, 4, 5], '🇮🇹 ROMA', 7000),
            ('IST', 'BCN', [4, 5, 6], '🇪🇸 BARSELONA', 9000),
            ('IST', 'AMS', [4, 5, 6], '🇳🇱 AMSTERDAM', 8500),
            ('IST', 'LHR', [3, 4, 5], '🇬🇧 LONDRA', 7000),
            ('IST', 'BEG', [3, 4, 5], '🇷🇸 BELGRAD (Vizesiz)', 5000),
            ('IST', 'TGD', [4, 5, 6], '🇲🇪 KARADAĞ (Vizesiz)', 6000),
            ('IST', 'SSH', [3, 4, 5], '🇪🇬 ŞARM EL ŞEYH (Vizesiz)', 7000),
        ]

    def get_target_routes(self):
        targets = []
        for r in self.HACK_ROUTES:
            targets.append({'origin': r[0], 'dest': r[1], 'months': r[2], 'note': r[3], 'hard_limit': r[4]})
        return targets
