# notifier.py - Advanced Telegram Notification System V2.3
# 🦅 Ghost Protocol + Anti-Spam + Smart Alerting

import logging
import aiohttp
import asyncio
from datetime import datetime, time, timedelta
from typing import List, Dict, Optional
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class TelegramNotifier:
    """
    Gelişmiş Telegram bildirim sistemi:
    - Ghost Protocol (zaman kuralları)
    - Anti-Spam (günlük limit)
    - Mistake fare bypass
    - Profesyonel mesaj formatı
    """
    
    def __init__(self, config):
        self.config = config
        self.bot_token = config.TELEGRAM_BOT_TOKEN
        self.admin_id = config.TELEGRAM_ADMIN_ID
        self.group_id = config.TELEGRAM_GROUP_ID
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        
        # Anti-spam state tracking
        self.state_file = Path("notification_state.json")
        self.state = self._load_state()
    
    def _load_state(self) -> Dict:
        """Anti-spam için state yükle"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"daily_alerts": 0, "route_alerts": {}, "last_reset": datetime.now().isoformat()}
        return {"daily_alerts": 0, "route_alerts": {}, "last_reset": datetime.now().isoformat()}
    
    def _save_state(self):
        """State kaydet"""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"State kaydedilemedi: {e}")
    
    def _reset_daily_limits(self):
        """Günlük limitleri sıfırla"""
        last_reset = datetime.fromisoformat(self.state["last_reset"])
        if datetime.now().date() > last_reset.date():
            logger.info("🔄 Günlük limitler sıfırlanıyor...")
            self.state["daily_alerts"] = 0
            self.state["route_alerts"] = {}
            self.state["last_reset"] = datetime.now().isoformat()
            self._save_state()
    
    def _is_active_hours(self) -> bool:
        """Ghost Protocol: Aktif saatler içinde mi?"""
        now = datetime.now()
        current_time = now.time()
        is_weekend = now.weekday() >= 5  # Cumartesi=5, Pazar=6
        
        if is_weekend:
            start, end = self.config.ACTIVE_HOURS_WEEKEND
        else:
            start, end = self.config.ACTIVE_HOURS_WEEKDAY
        
        return start <= current_time <= end
    
    def _can_send_alert(self, route_key: str, is_mistake_fare: bool = False) -> tuple[bool, str]:
        """
        Anti-spam kontrolü:
        - Günlük max 3 alarm
        - Aynı rota için max 1 alarm/24h
        - Mistake fare ise tüm kuralları bypass et!
        """
        # Mistake fare bypass
        if is_mistake_fare:
            return True, "✅ Mistake Fare - Tüm limitler bypass!"
        
        # Günlük limit kontrolü
        self._reset_daily_limits()
        
        if self.state["daily_alerts"] >= self.config.MAX_TOTAL_ALERTS_PER_DAY:
            return False, f"❌ Günlük limit doldu ({self.state['daily_alerts']}/{self.config.MAX_TOTAL_ALERTS_PER_DAY})"
        
        # Rota bazlı limit
        route_alerts = self.state["route_alerts"].get(route_key, {})
        last_alert_time = route_alerts.get("last_alert")
        
        if last_alert_time:
            last_alert = datetime.fromisoformat(last_alert_time)
            if datetime.now() - last_alert < timedelta(hours=24):
                return False, f"❌ Bu rota için son 24 saatte alarm gönderildi"
        
        return True, "✅ Spam kontrolü geçti"
    
    def _record_alert(self, route_key: str):
        """Alarm gönderimini kaydet"""
        self.state["daily_alerts"] += 1
        self.state["route_alerts"][route_key] = {
            "last_alert": datetime.now().isoformat(),
            "count": self.state["route_alerts"].get(route_key, {}).get("count", 0) + 1
        }
        self._save_state()
    
    async def _send_message(self, chat_id: int, text: str, parse_mode: str = "HTML") -> bool:
        """Telegram mesajı gönder"""
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": parse_mode,
                "disable_web_page_preview": False
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        logger.info(f"✅ Mesaj gönderildi: {chat_id}")
                        return True
                    else:
                        error = await response.text()
                        logger.error(f"❌ Mesaj gönderilemedi: {error}")
                        return False
        except Exception as e:
            logger.error(f"❌ Mesaj hatası: {e}")
            return False
    
    def _format_deal_message(self, deal: Dict) -> str:
        """
        Profesyonel deal mesajı formatla
        
        Format standardı:
        🦅 PROJECT TITAN – DİP FİYAT ALARMI 💎
        ✈️ Rota: IST ➔ JFK (Direkt)
        📅 Tarih: 2026-06-15 ➔ 2026-06-25 (10 Gece)
        💰 Fiyat: 9,500 TL (Gerçek Maliyet: 10,200 TL)
        🏷️ Havayolu: Turkish Airlines
        🎒 Bagaj: Kabin + 1 Bavul Dahil
        
        📊 Analiz:
        • 90 Günlük Ortalama: 15,000 TL | Dip Eşik: 10,500 TL
        • Tasarruf: %36.7
        • ✅ Vize Durumu: Vizesiz (Schengen)
        
        🔗 [UÇUŞ LİNKİ] | [OTEL LİNKİ]
        ⚡ AKSİYON: HEMEN AL
        """
        
        analysis = deal.get('analysis', {})
        price_cat = analysis.get('price_category', {})
        visa_info = deal.get('visa_info', 'Bilinmiyor')
        
        # Tarih formatı
        dep_date = deal.get('departure_date', 'N/A')
        ret_date = deal.get('return_date', 'N/A')
        
        # Gece sayısı hesapla
        try:
            dep = datetime.fromisoformat(dep_date)
            ret = datetime.fromisoformat(ret_date)
            nights = (ret - dep).days
        except:
            nights = "?"
        
        # Badges
        badges = []
        if analysis.get('is_mistake_fare'):
            badges.append("🔥 MISTAKE FARE")
        if price_cat.get('category') == 'bottom':
            badges.append("💎 DİP FİYAT")
        if analysis.get('is_green_zone'):
            badges.append("🟢 YEŞIL BÖLGE")
        
        badges_str = " | ".join(badges) if badges else ""
        
        # Mesaj başlığı
        header = f"🦅 <b>PROJECT TITAN – DİP FİYAT ALARMI</b> {badges_str}\n\n"
        
        # Rota bilgisi
        route_info = (
            f"✈️ <b>Rota:</b> {deal['origin']} ➔ {deal['destination']} "
            f"({deal.get('flight_type', 'Direkt')})\n"
        )
        
        # Tarih bilgisi
        date_info = (
            f"📅 <b>Tarih:</b> {dep_date} ➔ {ret_date} ({nights} Gece)\n"
        )
        
        # Fiyat bilgisi
        real_cost = analysis.get('real_cost', {})
        price_display = f"{deal['price']:,.0f} TL"
        if real_cost.get('real_cost', 0) > deal['price']:
            price_display += f" <i>(Gerçek Maliyet: {real_cost['real_cost']:,.0f} TL)</i>"
        
        price_info = f"💰 <b>Fiyat:</b> {price_display}\n"
        
        # Havayolu ve bagaj
        airline_info = f"🏷️ <b>Havayolu:</b> {deal.get('airline', 'N/A')}\n"
        
        baggage_note = "Kabin + 1 Bavul Dahil" if "Turkish" in deal.get('airline', '') else "Ek bagaj ücretli"
        baggage_info = f"🎒 <b>Bagaj:</b> {baggage_note}\n\n"
        
        # Analiz
        analysis_header = "📊 <b>Analiz:</b>\n"
        
        bottom_analysis = analysis.get('bottom_analysis', {})
        avg_price = bottom_analysis.get('avg_price', 0)
        bottom_threshold = bottom_analysis.get('bottom_threshold', 0)
        savings = price_cat.get('savings', 0)
        
        analysis_content = (
            f"• 90 Günlük Ortalama: {avg_price:,.0f} TL | Dip Eşik: {bottom_threshold:,.0f} TL\n"
            f"• Tasarruf: %{savings:.1f}\n"
        )
        
        # Geçmiş fiyat karşılaştırması (ucuzaucak.net)
        hist_comp = analysis.get('historical_comparison')
        if hist_comp and hist_comp.get('percentile') is not None:
            percentile = hist_comp.get('percentile', 0)
            recommendation = hist_comp.get('recommendation', '')
            hist_min = hist_comp.get('hist_min', 0)
            hist_avg = hist_comp.get('hist_avg', 0)
            
            analysis_content += (
                f"• 📊 Geçmiş Karşılaştırma: En ucuz %{percentile:.0f}'lik dilimde\n"
                f"   (Geçmiş Min: {hist_min:,.0f} TL | Ort: {hist_avg:,.0f} TL)\n"
                f"• {recommendation}\n"
            )
        
        analysis_content += f"• {visa_info}\n\n"
        
        # Linkler
        flights_url = (
            f"https://www.google.com/travel/flights?"
            f"q=Flights%20to%20{deal['destination']}%20from%20{deal['origin']}%20"
            f"on%20{dep_date}%20through%20{ret_date}"
        )
        
        hotels_url = f"https://www.google.com/travel/hotels?q=hotels%20in%20{deal['destination']}"
        
        links = f"🔗 <a href='{flights_url}'>✈️ UÇUŞ LİNKİ</a> | <a href='{hotels_url}'>🏨 OTEL LİNKİ</a>\n"
        
        # Aksiyon
        action_emoji = price_cat.get('emoji', '❓')
        action_text = price_cat.get('action', 'BEKLE')
        action = f"⚡ <b>AKSİYON:</b> {action_emoji} {action_text}\n"
        
        # Elastikiyet tahmini
        elasticity = analysis.get('elasticity', {})
        if elasticity.get('duration'):
            action += f"⏱️ <b>Tahmini Süre:</b> {elasticity['duration']} {elasticity.get('emoji', '')}\n"
        
        # Footer
        footer = f"\n<i>Tarama: {deal.get('method', 'hybrid')} | {datetime.now().strftime('%H:%M:%S')}</i>"
        
        return (
            header + route_info + date_info + price_info + airline_info + 
            baggage_info + analysis_header + analysis_content + links + action + footer
        )
    
    async def send_deal_alert(self, deal: Dict) -> bool:
        """
        Deal alarm gönder (Ghost Protocol + Anti-Spam kontrollü)
        """
        route_key = f"{deal['origin']}-{deal['destination']}"
        is_mistake_fare = deal.get('analysis', {}).get('is_mistake_fare', False)
        
        # Zaman kontrolü (Mistake fare bypass)
        if not is_mistake_fare and not self._is_active_hours():
            logger.info(f"⏰ Aktif saatler dışında, alarm beklemede: {route_key}")
            return False
        
        # Spam kontrolü
        can_send, reason = self._can_send_alert(route_key, is_mistake_fare)
        if not can_send:
            logger.info(f"🚫 Spam koruması: {reason}")
            return False
        
        # Mesaj formatla ve gönder
        try:
            message = self._format_deal_message(deal)
            
            # Admin ve gruba gönder
            success_admin = await self._send_message(self.admin_id, message)
            success_group = await self._send_message(self.group_id, message)
            
            if success_admin or success_group:
                self._record_alert(route_key)
                logger.info(f"✅ Deal alarm gönderildi: {route_key}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Deal alarm hatası: {e}")
            return False
    
    async def send_deals_report(self, deals: List[Dict]) -> bool:
        """Toplu deal raporu gönder"""
        if not deals:
            logger.info("📭 Gönderilecek deal yok")
            return False
        
        sent_count = 0
        for deal in deals:
            success = await self.send_deal_alert(deal)
            if success:
                sent_count += 1
            await asyncio.sleep(2)  # Rate limiting
        
        logger.info(f"📊 {sent_count}/{len(deals)} deal alarm gönderildi")
        return sent_count > 0
    
    async def send_error_alert(self, error: str):
        """Hata bildirimi (sadece admin)"""
        message = f"""
⚠️ <b>TITAN HATA BİLDİRİMİ</b>

<code>{error}</code>

Logları kontrol edin.
"""
        await self._send_message(self.admin_id, message)
    
    async def send_startup_message(self):
        """Başlangıç mesajı"""
        message = f"""
🦅 <b>PROJECT TITAN V2.3 ONLINE</b>

✅ Ghost Protocol: Aktif
✅ Anti-Spam: Aktif
✅ Visa Checker: Aktif
✅ Price Analyzer: Aktif

Sistem hazır. Rota taraması başlatılıyor...
"""
        await self._send_message(self.admin_id, message)
    
    async def send_daily_summary(self, stats: Dict):
        """Günlük özet rapor"""
        message = f"""
📊 <b>TITAN GÜNLÜK RAPOR</b>

📅 Tarih: {datetime.now().strftime('%Y-%m-%d')}

🔍 <b>Tarama:</b>
• Toplam Rota: {stats.get('total_routes', 0)}
• Başarılı: {stats.get('successful_scans', 0)}
• Başarısız: {stats.get('failed_scans', 0)}

💎 <b>Fırsatlar:</b>
• Dip Fiyat: {stats.get('bottom_deals', 0)}
• Mistake Fare: {stats.get('mistake_fares', 0)}
• Toplam Alarm: {stats.get('total_alerts', 0)}

⏱️ <b>Performans:</b>
• Ortalama Süre: {stats.get('avg_duration', 0):.1f}s
• Başarı Oranı: {stats.get('success_rate', 0):.1f}%
"""
        await self._send_message(self.admin_id, message)
