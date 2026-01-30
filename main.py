import os
import time
import json
import requests
import logging
from intelligence import IntelligenceGatherer
from engine import AnalysisEngine

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# ==========================================
# 🔐 GİZLİ KİMLİK BİLGİLERİ (HARDCODED)
# ==========================================
TG_TOKEN = "8161806410:AAH4tGpW_kCvQpLOfaB-r2OYQMypPVYtuYg"
ADMIN_ID = "7684228928"       # Patron (Sen)
GROUP_ID = "-1003515302846"   # Grup

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
    if not TG_TOKEN: return
    
    # Mesajı alacak kişiler listesi (Sen + Grup)
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
💡 <i>Otonom İstihbarat Raporu</i>

🔗 <a href="{deal.link}">UÇAK</a> | <a href="{deal.hotel_link}">OTEL</a>
    """
    
    for chat_id in recipients:
        try:
            requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", 
                         json={"chat_id": chat_id, "text": msg, "parse_mode": "HTML", "disable_web_page_preview": False})
            logger.info(f"✅ Mesaj gönderildi -> {chat_id}")
        except Exception as e:
            logger.error(f"❌ Gönderim hatası ({chat_id}): {e}")

def main():
    logger.info("🧠 SNIPER V80 - HARDCODED MODE BAŞLATILIYOR...")
    
    intel = IntelligenceGatherer()
    engine = AnalysisEngine()
    history = load_history()
    
    # Görevleri Al
    missions = intel.get_mission_targets()
    
    for m in missions:
        origin, dest = m['origin'], m['dest']
        logger.info(f"🔎 Analiz: {origin} -> {dest}")
        
        deal = engine.scan_route(origin, dest, hard_limit=m['hard_limit'])
        
        if deal:
            deal_key = f"{origin}-{dest}-{deal.date[:7]}" 
            old_price = history.get(deal_key, 999999)
            
            # İndirim veya Yeni Fırsat Kontrolü
            if deal.price_try < old_price * 0.95: 
                drop_rate = int((1 - (deal.price_try / old_price)) * 100) if old_price != 999999 else 0
                
                logger.info(f"🚨 SİNYAL: {deal.destination} {deal.price_try} TL")
                send_telegram(deal, drop_rate)
                
                history[deal_key] = deal.price_try
            else:
                logger.info(f"💤 Değişim Yok: {deal.destination}")
        
        time.sleep(2)

    save_history(history)

if __name__ == "__main__":
    main()
