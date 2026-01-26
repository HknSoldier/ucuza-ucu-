"""
SNIPER V46 - INTELLIGENCE (IZMIR ADDED)
Layer 1: Global Routes + Holidays + Hard Limits + IZMIR
"""
from datetime import datetime

class IntelligenceGatherer:
    def __init__(self):
        # 2026 Bayram ve Tatil Günleri
        self.HOLIDAY_TARGETS = [
            '2026-03-20', '2026-04-23', '2026-05-01', '2026-05-19', 
            '2026-05-27', '2026-07-15', '2026-08-30', '2026-10-29'
        ]

        self.HACK_ROUTES = [
            # ==========================================
            # 💎 ÖZEL HACK ROTALARI
            # ==========================================
            ('IST', 'AUH', [2, 3, 4, 10, 11], '🇦🇪 ABU DHABI: Stopover (Bedava Otel) Fırsatı.', 15000),
            ('IST', 'DOH', [2, 3, 4, 11], '🇶🇦 KATAR: Aktarma ve lüks mola.', 16000),
            
            # ==========================================
            # 🏖️ İZMİR (ADB) ÇIKIŞLI ROTALAR (YENİ EKLENDİ)
            # ==========================================
            ('ADB', 'BER', [3, 4, 5, 9, 10], '🇩🇪 İZMİR-BERLİN: Direkt uçuş fırsatı.', 6500),
            ('ADB', 'DUS', [2, 3, 4, 9, 10], '🇩🇪 İZMİR-DÜSSELDORF: Gurbetçi rotası.', 6800),
            ('ADB', 'CGN', [3, 4, 5, 9, 10], '🇩🇪 İZMİR-KÖLN: Ucuz aktarma.', 6500),
            ('ADB', 'MUC', [3, 4, 9, 10], '🇩🇪 İZMİR-MÜNİH: Bavyera.', 7200),
            ('ADB', 'FRA', [2, 3, 4, 9, 10], '🇩🇪 İZMİR-FRANKFURT: Ana hub.', 7500),
            ('ADB', 'STN', [3, 4, 5, 9, 10], '🇬🇧 İZMİR-LONDRA: Stansted ucuz uçuş.', 6000),
            ('ADB', 'AMS', [2, 3, 4, 11], '🇳🇱 İZMİR-AMSTERDAM: Direkt/Aktarmalı.', 8500),
            ('ADB', 'CDG', [3, 4, 5, 9, 10], '🇫🇷 İZMİR-PARİS: Romantik.', 8800),
            ('ADB', 'ATH', [4, 5, 9, 10], '🇬🇷 İZMİR-ATİNA: Ege komşusu.', 4500),
            ('ADB', 'BCN', [4, 5, 6, 9, 10], '🇪🇸 İZMİR-BARSELONA: Aktarmalı fırsat.', 8500),

            # ==========================================
            # 🇪🇺 AVRUPA (İSTANBUL DEVAM)
            # ==========================================
            ('IST', 'CGN', [3, 4, 5, 9, 10], '🇩🇪 KÖLN: Fuar ve bahar fırsatı.', 6500),
            ('IST', 'FRA', [2, 3, 4, 9, 10], '🇩🇪 FRANKFURT: Finans merkezi.', 7500),
            ('IST', 'MUC', [3, 4, 9, 10], '🇩🇪 MÜNİH: Bavyera turu.', 8000),
            ('IST', 'BER', [2, 3, 5, 9, 11], '🇩🇪 BERLİN: Sanat ve gece hayatı.', 7200),
            ('IST', 'DUS', [2, 3, 10, 11], '🇩🇪 DÜSSELDORF: İş ve alışveriş.', 7500),
            ('IST', 'HAM', [4, 5, 8, 9], '🇩🇪 HAMBURG: Liman şehri.', 7800),
            ('IST', 'CDG', [3, 4, 5, 9, 10], '🇫🇷 PARİS: Romantik sezon.', 8500),
            ('IST', 'LYS', [4, 5, 9], '🇫🇷 LYON: Gastronomi başkenti.', 8000),
            ('IST', 'NCE', [5, 6, 9], '🇫🇷 NICE: Cote d\'Azur tatili.', 9000),
            ('IST', 'FCO', [3, 4, 5, 9, 10], '🇮🇹 ROMA: Tarih ve makarna.', 7500),
            ('IST', 'MXP', [2, 3, 9, 11], '🇮🇹 MİLANO: Moda haftası.', 7200),
            ('IST', 'VCE', [3, 4, 9, 10], '🇮🇹 VENEDİK: Kanallar turu.', 8000),
            ('IST', 'NAP', [4, 5, 9], '🇮🇹 NAPOLİ: Amalfi kıyıları.', 7800),
            ('IST', 'BCN', [4, 5, 6, 9, 10], '🇪🇸 BARSELONA: Gaudi ve deniz.', 8500),
            ('IST', 'MAD', [3, 4, 5, 10], '🇪🇸 MADRİD: Başkent turu.', 8200),
            ('IST', 'AGP', [5, 6, 9], '🇪🇸 MALAGA: Endülüs güneşi.', 9000),
            ('IST', 'LIS', [3, 4, 5, 10], '🇵🇹 LİZBON: Okyanus manzarası.', 9500),
            ('IST', 'OPO', [4, 5, 9], '🇵🇹 PORTO: Şarap tadımı.', 9200),
            ('IST', 'AMS', [2, 3, 4, 11], '🇳🇱 AMSTERDAM: Özgürlükler şehri.', 8500),
            ('IST', 'BRU', [3, 4, 5, 10], '🇧🇪 BRÜKSEL: Çikolata ve tarih.', 7500),
            ('IST', 'VIE', [2, 3, 11], '🇦🇹 VİYANA: Klasik müzik.', 6500),
            ('IST', 'PRG', [3, 4, 5, 10], '🇨🇿 PRAG: Masal şehri.', 7000),
            ('IST', 'BUD', [2, 3, 11], '🇭🇺 BUDAPEŞTE: Tuna nehri.', 5500),
            ('IST', 'ZRH', [2, 3, 10], '🇨🇭 ZÜRİH: Lüks ve doğa.', 9000),
            ('IST', 'GVA', [3, 4, 9], '🇨🇭 CENEVRE: Göl kenarı.', 8800),
            ('IST', 'CPH', [5, 6, 7, 8], '🇩🇰 KOPENHAG: İskandinav tarzı.', 8500),
            ('IST', 'ARN', [5, 6, 7, 8], '🇸🇪 STOKHOLM: Adalar şehri.', 8200),
            ('IST', 'OSL', [5, 6, 7, 8], '🇳🇴 OSLO: Fiyort başlangıcı.', 9000),
            ('IST', 'ATH', [4, 5, 9, 10], '🇬🇷 ATİNA: Akropolis turu.', 5200),
            ('IST', 'SKG', [4, 5, 9], '🇬🇷 SELANİK: Atatürk evi.', 4500),

            # ==========================================
            # 🔓 VİZESİZ BALKANLAR (İSTANBUL DEVAM)
            # ==========================================
            ('IST', 'BEG', [2, 3, 4, 9, 10], '🇷🇸 BELGRAD: Vizesiz gece hayatı.', 6000),
            ('IST', 'SJJ', [3, 4, 5, 9, 10], '🇧🇦 SARAYBOSNA: Tarih ve lezzet.', 5400),
            ('IST', 'TIA', [4, 5, 9, 10], '🇦🇱 TİRAN: Adriyatik kıyıları.', 4200),
            ('IST', 'SKP', [2, 3, 11], '🇲🇰 ÜSKÜP: Heykeller şehri.', 3800),
            ('IST', 'TGD', [5, 6, 7, 8, 9], '🇲🇪 PODGORICA: Karadağ sahilleri.', 6000),
            ('IST', 'PRN', [3, 4, 10], '🇽🇰 PRİŞTİNE: Genç başkent.', 4200),
            ('IST', 'TBS', [3, 4, 5, 10], '🇬🇪 TİFLİS: Pasaportsuz giriş.', 3500),
            ('IST', 'GYD', [3, 4, 5, 9], '🇦🇿 BAKÜ: Hazar kıyısı.', 4000),

            # ==========================================
            # 🌏 UZAK ROTALAR (İSTANBUL DEVAM)
            # ==========================================
            ('IST', 'BKK', [1, 2, 5, 6, 9, 10, 11, 12], '🇹🇭 BANGKOK: Uzak doğu macerası.', 18000),
            ('IST', 'HKT', [1, 2, 5, 6, 11, 12], '🇹🇭 PHUKET: Deniz kum güneş.', 20000),
            ('IST', 'SIN', [2, 3, 4, 11], '🇸🇬 SİNGAPUR: Modern şehir.', 23000),
            ('IST', 'ICN', [4, 5, 9, 10], '🇰🇷 SEUL: Teknoloji ve kültür.', 22000),
            ('IST', 'TYO', [3, 4, 10, 11], '🇯🇵 TOKYO: Japonya rüyası.', 21000),
            ('IST', 'DPS', [2, 3, 5, 6, 11], '🇮🇩 BALİ: Tropik cennet.', 25000),
            ('IST', 'KUL', [2, 3, 11], '🇲🇾 KUALA LUMPUR: İkiz kuleler.', 21000),
            ('IST', 'MLE', [1, 2, 5, 6, 11], '🇲🇻 MALDİVLER: Balayı rotası.', 22000),
            ('IST', 'GRU', [2, 3, 11], '🇧🇷 SAO PAULO: Latin Amerika.', 30000),
            ('IST', 'GIG', [2, 3, 11], '🇧🇷 RIO DE JANEIRO: Karnaval şehri.', 32000),
            ('IST', 'EZE', [2, 3, 11], '🇦🇷 BUENOS AIRES: Tango ve et.', 35000),
            ('IST', 'BOG', [3, 4, 10], '🇨🇴 BOGOTA: Andes dağları.', 28000),
            ('IST', 'CCS', [3, 4, 10], '🇻🇪 KARAKAS: Tropik.', 29000),
            ('IST', 'HAV', [2, 3, 11], '🇨🇺 HAVANA: Nostalji.', 33000),
            ('IST', 'CUN', [1, 2, 5, 6, 9, 10, 11], '🇲🇽 CANCUN: Karayip denizi.', 30000),

            # ==========================================
            # 🌍 AFRİKA & SOFYA (İSTANBUL DEVAM)
            # ==========================================
            ('IST', 'CMN', [1, 2, 3, 10, 11], '🇲🇦 KAZABLANKA: Egzotik.', 12500),
            ('IST', 'RAK', [1, 2, 3, 10, 11], '🇲🇦 MARAKEŞ: Kızıl şehir.', 13000),
            ('IST', 'CAI', [2, 3, 10, 11], '🇪🇬 KAHİRE: Piramitler.', 7000),
            ('IST', 'HRG', [3, 4, 9, 10, 11], '🇪🇬 HURGHADA: Kızıldeniz.', 8000),
            ('IST', 'SSH', [3, 4, 9, 10, 11], '🇪🇬 ŞARM EL-ŞEYH: Dalış.', 7500),
            ('IST', 'JNB', [4, 5, 9], '🇿🇦 JOHANNESBURG: Safari.', 24000),
            ('IST', 'CPT', [4, 5, 9], '🇿🇦 CAPE TOWN: Masa dağı.', 26000),
            
            # Sofya Çıkış (Aynen Korundu)
            ('SOF', 'LON', [4, 5, 6, 9, 10, 11], '🇬🇧 HACK: Londra Sofya çıkış.', 3500),
            ('SOF', 'MIL', [4, 5, 6, 9, 10], '🇮🇹 HACK: Milano Sofya çıkış.', 2750),
            ('SOF', 'BCN', [5, 6, 7, 8, 9], '🇪🇸 HACK: Barselona Sofya çıkış.', 3500)
        ]

    def get_target_routes(self):
        targets = []
        current_month = datetime.now().month
        lookahead_window = [(current_month + i - 1) % 12 + 1 for i in range(8)]
        
        for origin, dest, months, hack, hard_limit in self.HACK_ROUTES:
            valid_months = [m for m in months if m in lookahead_window]
            if valid_months:
                targets.append({
                    'origin': origin, 'dest': dest, 
                    'months': valid_months,
                    'hack_note': hack,
                    'hard_limit': hard_limit,
                    'holidays': self.HOLIDAY_TARGETS
                })
        return targets
