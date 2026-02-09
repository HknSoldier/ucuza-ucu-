# price_analyzer.py - Advanced Price Analysis Engine
# 🦅 Dip Fiyat Tespiti + Fiyat Elastikiyeti Tahmini

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import statistics

logger = logging.getLogger(__name__)

class PriceAnalyzer:
    """
    Gelişmiş fiyat analiz motoru:
    - Dip fiyat tespiti (PRICE BOTTOM)
    - Fiyat elastikiyeti (Kaç saat dayanır?)
    - Anomali algılama
    - Multi-kaynak doğrulama
    """
    
    def __init__(self, min_sane_price: float = 100, max_sane_price: float = 500000):
        self.min_sane_price = min_sane_price
        self.max_sane_price = max_sane_price
    
    def is_sane_price(self, price: float) -> bool:
        """
        Fiyat mantıklı mı? (Anomali algılama)
        100 TL altı veya 500K TL üstü = hatalı
        """
        return self.min_sane_price <= price <= self.max_sane_price
    
    def validate_with_sources(self, prices: List[float], min_sources: int = 2) -> Optional[float]:
        """
        Multi-kaynak doğrulama
        En az 2 farklı kaynaktan benzer fiyat alınmalı
        """
        if len(prices) < min_sources:
            logger.warning(f"Yetersiz kaynak: {len(prices)} < {min_sources}")
            return None
        
        # Varyans kontrolü: fiyatlar birbirine yakın mı?
        try:
            avg = statistics.mean(prices)
            std_dev = statistics.stdev(prices)
            
            # %20'den fazla sapma varsa güvenme
            if std_dev / avg > 0.20:
                logger.warning(f"Yüksek varyans: std={std_dev:.0f}, avg={avg:.0f}")
                return None
            
            return avg
            
        except statistics.StatisticsError:
            return None
    
    def calculate_bottom_price(self, price_history: List[float]) -> Dict:
        """
        Dip fiyat analizi:
        - 🔥 DİP: Fiyat ≤ (En düşük × 1.05)
        - 🟡 NORMAL: Fiyat ≤ Ortalama
        - 🔴 PAHALI: Fiyat > Ortalama
        """
        if not price_history:
            return {
                "status": "unknown",
                "message": "Fiyat geçmişi yok"
            }
        
        min_price = min(price_history)
        avg_price = statistics.mean(price_history)
        bottom_threshold = min_price * 1.05
        
        return {
            "min_price": min_price,
            "avg_price": avg_price,
            "bottom_threshold": bottom_threshold,
            "history_size": len(price_history)
        }
    
    def categorize_price(self, current_price: float, bottom_analysis: Dict) -> Dict:
        """
        Fiyatı kategorize et ve aksiyona dönüştür
        """
        if not bottom_analysis or "bottom_threshold" not in bottom_analysis:
            return {
                "category": "unknown",
                "emoji": "❓",
                "action": "VERİ YETERSİZ",
                "urgency": "low"
            }
        
        bottom = bottom_analysis["bottom_threshold"]
        avg = bottom_analysis["avg_price"]
        
        if current_price <= bottom:
            return {
                "category": "bottom",
                "emoji": "🔥",
                "action": "HEMEN AL",
                "urgency": "critical",
                "savings": ((avg - current_price) / avg) * 100
            }
        elif current_price <= avg:
            return {
                "category": "normal",
                "emoji": "🟡",
                "action": "BEKLE",
                "urgency": "medium",
                "savings": ((avg - current_price) / avg) * 100
            }
        else:
            return {
                "category": "expensive",
                "emoji": "🔴",
                "action": "ALMA",
                "urgency": "skip",
                "overprice": ((current_price - avg) / avg) * 100
            }
    
    def estimate_price_elasticity(self, price_history: List[Dict]) -> Dict:
        """
        Fiyat elastikiyeti tahmini: Bu fiyat ne kadar dayanır?
        
        price_history format: [{"price": 10000, "date": "2026-01-01"}, ...]
        """
        if len(price_history) < 7:  # En az 7 günlük veri gerekli
            return {
                "elasticity": "unknown",
                "duration": None,
                "confidence": "low",
                "message": "Yetersiz veri"
            }
        
        # Son 7 günde fiyat ne kadar stabil kaldı?
        recent_prices = sorted(price_history, key=lambda x: x["date"], reverse=True)[:7]
        prices = [p["price"] for p in recent_prices]
        
        min_recent = min(prices)
        max_recent = max(prices)
        volatility = (max_recent - min_recent) / min_recent
        
        # Volatilite bazlı tahmin
        if volatility < 0.05:  # %5'ten az dalgalanma
            return {
                "elasticity": "high",
                "duration": "> 24 saat",
                "emoji": "⏳",
                "confidence": "high",
                "message": "Fiyat stabil, acele etme"
            }
        elif volatility < 0.15:  # %15'ten az
            return {
                "elasticity": "medium",
                "duration": "6-24 saat",
                "emoji": "⚡",
                "confidence": "medium",
                "message": "Fiyat orta stabil, yakından takip et"
            }
        else:  # Yüksek volatilite
            return {
                "elasticity": "low",
                "duration": "< 6 saat",
                "emoji": "🔥",
                "confidence": "high",
                "message": "Fiyat çok hareketli, HEMEN AL!"
            }
    
    def should_alert(self, current_price: float, price_history: List[float], 
                     alarm_multiplier: float = 1.05) -> Tuple[bool, str]:
        """
        Alarm filter: Sadece gerçek fırsatlarda alarm ver
        
        Kural: current_price ≤ (90 günlük en düşük × 1.05)
        """
        if not price_history:
            return False, "Fiyat geçmişi yok, alarm yok"
        
        # 90 günlük en düşük fiyat
        min_90day = min(price_history)
        alarm_threshold = min_90day * alarm_multiplier
        
        if current_price <= alarm_threshold:
            savings = ((min_90day - current_price) / min_90day) * 100
            return True, f"✅ ALARM: Fiyat dip seviyede! ({savings:.1f}% altında)"
        else:
            return False, f"❌ Alarm yok: Fiyat yüksek ({current_price:.0f} > {alarm_threshold:.0f} TL)"
    
    def is_mistake_fare(self, current_price: float, avg_price: float, 
                        threshold: float = 0.30) -> bool:
        """
        Mistake fare (Hata bilet) algılama
        %70+ düşüş = Mistake fare = Zaman kuralını bypass et!
        """
        if avg_price == 0:
            return False
        
        discount = 1 - (current_price / avg_price)
        return discount >= (1 - threshold)  # %70+ indirim
    
    def calculate_real_cost(self, base_price: float, airline: str, 
                           destination_airport: str, 
                           baggage_costs: Dict, 
                           remote_airport_costs: Dict) -> Dict:
        """
        Gerçek maliyet hesaplama:
        - Bagaj ücreti ekle (low-cost için)
        - Uzak havalimanı ulaşım maliyeti ekle
        """
        real_cost = base_price
        breakdown = {"base": base_price}
        
        # Bagaj maliyeti
        if airline in baggage_costs:
            baggage = baggage_costs[airline]
            real_cost += baggage.get("cabin", 0) + baggage.get("checked", 0)
            breakdown["baggage"] = baggage.get("cabin", 0) + baggage.get("checked", 0)
        
        # Uzak havalimanı ulaşım
        if destination_airport in remote_airport_costs:
            transport = remote_airport_costs[destination_airport]
            real_cost += transport
            breakdown["transport"] = transport
        
        return {
            "real_cost": real_cost,
            "base_price": base_price,
            "extra_costs": real_cost - base_price,
            "breakdown": breakdown
        }
    
    def compare_with_miles(self, cash_price: float, miles_needed: int, 
                          mile_rate: float = 0.02) -> Dict:
        """
        Mil arbitrajı: Nakit vs Mil kullanımı karşılaştırması
        
        mile_rate: 1 mil satın alma maliyeti (TL cinsinden)
        """
        mile_purchase_cost = miles_needed * mile_rate
        
        if cash_price < mile_purchase_cost:
            return {
                "decision": "NAKİT ÖDE",
                "savings": mile_purchase_cost - cash_price,
                "recommendation": f"Nakit öde, {mile_purchase_cost - cash_price:.0f} TL tasarruf"
            }
        elif cash_price < (miles_needed * mile_rate * 0.8):  # %20 fark
            return {
                "decision": "MİL KULLAN",
                "savings": cash_price - (miles_needed * 0),  # Mil kullanımı ücretsiz
                "recommendation": f"Millerini kullan, {cash_price:.0f} TL tasarruf"
            }
        else:
            return {
                "decision": "MİL SATIN AL",
                "cost": mile_purchase_cost,
                "recommendation": f"Mil satın al ({mile_purchase_cost:.0f} TL), nakit ödemeden {cash_price - mile_purchase_cost:.0f} TL ucuz"
            }
