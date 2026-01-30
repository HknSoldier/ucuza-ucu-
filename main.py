import os
import time
import json
import requests
import logging
import traceback # Hata takibi için
from intelligence import IntelligenceGatherer
from engine import AnalysisEngine

# Detaylı Loglama
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# ==========================================
# 🔐 GİZLİ KİMLİK BİLGİLERİ
# ==========================================
TG_TOKEN = "8161806410:AAH4tGpW_kCvQpLOfaB-r2OYQMypPVYtuYg"
ADMIN_ID = "7684228928"
GROUP_ID = "-1003515302846"

HISTORY_FILE = "price_history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f: return json.load(f)
        except: return {}
    return {}

def save_history(history):
    with open(HISTORY_FILE, 'w') as f: json.dump(history, f)

def send_telegram(deal, drop_rate=0):
    if not TG_TOKEN: 
        logger.error("❌ Token yok, mesaj atılamadı.")
        return
    
    recipients = [ADMIN_ID, GROUP_ID]
    
    est_hotel = deal.days * 2000
    total = deal.price_try + est_hotel
    
    title = "🔥 FİYAT DÜŞTÜ!" if drop_rate > 0 else "✈️ TATİL PAKETİ"
    if drop_rate > 0: title += f" (%{drop_rate} İndirim)"

    msg = f"""
<b>{title}</b>

📍 <b>{deal.origin} ➔ {deal.destination}</b>
📅 {deal.date} ({deal.days} Gece)

💰 <b>Uçak:</b> {deal.price_try:,.0f} TL
🏨 <b>Tahmini Otel:</b> {est_hotel:,.0f} TL
🏷️ <b>TOPLAM:</b> {total:,.0f} TL

⚠️ {deal.note}
💡 <i>Sniper V81 - Debug Mode</i>

🔗 <a href="{deal.link}">UÇAK</a> | <a href="{deal.hotel_link}">OTEL</a>
    """
    
    for chat_id in recipients:
        try:
            url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
            payload = {"chat_id": chat_id, "text": msg, "parse_mode": "HTML", "disable_web_page_preview": False}
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                logger.info(f"✅ Mesaj başarıyla gönderildi -> {chat_id}")
            else:
                logger.error(f"❌ Telegram Hatası ({chat_id}): {response.text}")
                
        except Exception as e:
            logger.error(f"❌ Bağlantı hatası ({chat_id}): {e}")

def main():
    logger.info("🛠️ SNIPER V81 - DEBUG MODU BAŞLATILIYOR...")
    
    try:
        logger.info("1. İstihbarat Modülü Yükleniyor...")
        intel = IntelligenceGatherer()
        
        logger.info("2. Motor Modülü Yükleniyor...")
        engine = AnalysisEngine()
        
        logger.info("3. Hafıza Yükleniyor...")
        history = load_history()
        
        logger.info("4. Görevler Alınıyor...")
        missions = intel.get_mission_targets()
        logger.info(f"📋 Toplam {len(missions)} görev alındı.")
        
        if len(missions) == 0:
            logger.warning("⚠️ HİÇ GÖREV YOK! Intelligence.py dosyasını kontrol et.")
        
        for i, m in enumerate(missions):
            origin, dest = m['origin'], m['dest']
            logger.info(f"▶️ [{i+1}/{len(missions)}] Analiz Başlıyor: {origin} -> {dest}")
            
            try:
                deal = engine.scan_route(origin, dest, hard_limit=m['hard_limit'])
                
                if deal:
                    logger.info(f"✅ FIRSAT BULUNDU: {deal.destination} - {deal.price_try} TL")
                    
                    deal_key = f"{origin}-{dest}-{deal.date[:7]}" 
                    old_price = history.get(deal_key, 999999)
                    
                    if deal.price_try < old_price * 0.95: 
                        drop_rate = int((1 - (deal.price_try / old_price)) * 100) if old_price != 999999 else 0
                        
                        logger.info(f"🚀 MESAJ GÖNDERİLİYOR...")
                        send_telegram(deal, drop_rate)
                        history[deal_key] = deal.price_try
                    else:
                        logger.info(f"💤 Fiyat aynı veya yüksek, mesaj atılmadı.")
                else:
                    logger.info("❌ Uygun uçuş bulunamadı (Google boş döndü veya limit aşıldı).")
                    
            except Exception as inner_e:
                logger.error(f"⚠️ Tarama sırasında hata ({origin}->{dest}): {inner_e}")
                # Hata olsa bile devam et, döngüyü kırma
                continue
            
            time.sleep(2)

        logger.info("💾 Hafıza kaydediliyor...")
        save_history(history)
        logger.info("🏁 İŞLEM TAMAMLANDI.")

    except Exception as e:
        logger.error("🔥 KRİTİK SİSTEM HATASI 🔥")
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()
