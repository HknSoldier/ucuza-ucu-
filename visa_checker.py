# visa_checker.py - Visa Requirement Checker
# 🛂 Yeşil Pasaport (Turkish Diplomatic/Service Passport) Visa Rules

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class VisaChecker:
    """
    Yeşil pasaport vize kontrol sistemi
    
    Rules:
    - 🟢 EU/Schengen: Vizesiz giriş
    - 🔴 USA/UK/CA/AU: Vize gerekli
    """
    
    def __init__(self):
        # Vizesiz bölgeler (Yeşil Pasaport ile)
        self.visa_free = {
            # Schengen ülkeleri
            "AMS": "🇳🇱 Hollanda (Schengen - Vizesiz)",
            "BCN": "🇪🇸 İspanya (Schengen - Vizesiz)",
            "BER": "🇩🇪 Almanya (Schengen - Vizesiz)",
            "CDG": "🇫🇷 Fransa (Schengen - Vizesiz)",
            "FCO": "🇮🇹 İtalya (Schengen - Vizesiz)",
            "MAD": "🇪🇸 İspanya (Schengen - Vizesiz)",
            "VIE": "🇦🇹 Avusturya (Schengen - Vizesiz)",
            "ZRH": "🇨🇭 İsviçre (Schengen - Vizesiz)",
            
            # EU üyesi ama Schengen dışı
            "SOF": "🇧🇬 Bulgaristan (EU - Vizesiz)",
            "OTP": "🇷🇴 Romanya (EU - Vizesiz)",
            
            # Diğer vizesiz ülkeler
            "DXB": "🇦🇪 BAE (Vizesiz)",
            "DOH": "🇶🇦 Katar (Vizesiz)",
            "BKK": "🇹🇭 Tayland (Vizesiz)",
            "SIN": "🇸🇬 Singapur (Vizesiz)",
            "HKG": "🇭🇰 Hong Kong (Vizesiz)",
            "ICN": "🇰🇷 Güney Kore (Vizesiz)",
            "NRT": "🇯🇵 Japonya (Vizesiz)",
            "PEK": "🇨🇳 Çin (Vizesiz)",
        }
        
        # Vize gerekli ülkeler
        self.visa_required = {
            # ABD
            "JFK": "🇺🇸 ABD - ⚠️ VİZE GEREKLİ (B1/B2)",
            "LAX": "🇺🇸 ABD - ⚠️ VİZE GEREKLİ (B1/B2)",
            "ORD": "🇺🇸 ABD - ⚠️ VİZE GEREKLİ (B1/B2)",
            "MIA": "🇺🇸 ABD - ⚠️ VİZE GEREKLİ (B1/B2)",
            "BOS": "🇺🇸 ABD - ⚠️ VİZE GEREKLİ (B1/B2)",
            "SFO": "🇺🇸 ABD - ⚠️ VİZE GEREKLİ (B1/B2)",
            "SEA": "🇺🇸 ABD - ⚠️ VİZE GEREKLİ (B1/B2)",
            "ATL": "🇺🇸 ABD - ⚠️ VİZE GEREKLİ (B1/B2)",
            "IAD": "🇺🇸 ABD - ⚠️ VİZE GEREKLİ (B1/B2)",
            
            # İngiltere
            "LHR": "🇬🇧 İngiltere - ⚠️ VİZE GEREKLİ (Standard Visitor)",
            
            # Kanada
            "YYZ": "🇨🇦 Kanada - ⚠️ eTA GEREKLİ",
            "YVR": "🇨🇦 Kanada - ⚠️ eTA GEREKLİ",
            
            # Avustralya
            "SYD": "🇦🇺 Avustralya - ⚠️ eVisitor GEREKLİ",
            "MEL": "🇦🇺 Avustralya - ⚠️ eVisitor GEREKLİ",
            
            # Yeni Zelanda
            "AKL": "🇳🇿 Yeni Zelanda - ⚠️ NZeTA GEREKLİ",
        }
    
    def check_visa_requirement(self, airport_code: str) -> Dict:
        """
        Havalimanı kodu için vize durumu kontrolü
        """
        if airport_code in self.visa_free:
            return {
                "required": False,
                "status": "✅ VİZESİZ",
                "emoji": "🟢",
                "details": self.visa_free[airport_code],
                "warning": None
            }
        
        elif airport_code in self.visa_required:
            return {
                "required": True,
                "status": "⚠️ VİZE GEREKLİ",
                "emoji": "🔴",
                "details": self.visa_required[airport_code],
                "warning": "UÇUŞ ÖNCESİ VİZE BAŞVURUSU YAPILMALIDIR!"
            }
        
        else:
            # Bilinmeyen havalimanı - araştırma gerekli
            return {
                "required": None,
                "status": "❓ BİLİNMİYOR",
                "emoji": "🟡",
                "details": f"{airport_code} - Vize durumu araştırılmalı",
                "warning": "Manuel kontrol gerekli"
            }
    
    def get_visa_message(self, airport_code: str) -> str:
        """
        Telegram mesajına eklenmek üzere vize bilgisi
        """
        visa_info = self.check_visa_requirement(airport_code)
        
        if visa_info["required"] is False:
            return f"{visa_info['emoji']} {visa_info['details']}"
        
        elif visa_info["required"] is True:
            return f"{visa_info['emoji']} {visa_info['details']}\n⚠️ {visa_info['warning']}"
        
        else:
            return f"{visa_info['emoji']} {visa_info['details']}"
    
    def batch_check(self, airport_codes: List[str]) -> Dict[str, Dict]:
        """
        Birden fazla havalimanı için vize kontrolü
        """
        results = {}
        for code in airport_codes:
            results[code] = self.check_visa_requirement(code)
        return results
    
    def requires_visa(self, airport_code: str) -> bool:
        """
        Quick check: Vize gerekli mi?
        """
        return airport_code in self.visa_required
    
    def is_visa_free(self, airport_code: str) -> bool:
        """
        Quick check: Vizesiz mi?
        """
        return airport_code in self.visa_free
