import os
import time
import json
import requests
import logging
from intelligence import IntelligenceGatherer
from engine import AnalysisEngine

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

TG_TOKEN = os.getenv('TG_TOKEN')
TG_CHAT_ID = os.getenv('TG_CHAT_ID')
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
    if not TG_TOKEN or not TG_CHAT_ID: return
    
    est_hotel = deal.days * 2000
    total = deal.price_try + est_hotel
    
    # İndirim varsa başlığa ekle
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
💡 <i>En uygun ay/dönem taranarak bulundu.</i>

🔗 <a href="{deal.link}">UÇAK</a> | <a href="{deal.hotel_link}">OTEL</a>
    """
    try:
        requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", 
                     json={"chat_id": TG_CHAT_ID, "text": msg, "parse_mode": "HTML", "disable_web_page_preview": False})
    except: pass

def main():
    logger.info("🧠 SNIPER V70 - OTONOM MOD BAŞLATILIYOR...")
    
    intel = IntelligenceGatherer()
    engine = AnalysisEngine()
    history = load_history()
    
    # Görevleri Al (Reddit sinyalleri + Türkiye Hub'ları)
    missions = intel.get_mission_targets()
    
    for m in missions:
        origin, dest = m['origin'], m['dest']
        logger.info(f"🔎 Analiz: {origin} -> {dest}")
        
        deal = engine.scan_route(origin, dest, hard_limit=m['hard_limit'])
        
        if deal:
            # BENZERSİZ KEY: Rota + Ay (Örn: IST-LON-2024-05)
            # Böylece aynı ay için tekrar tekrar mesaj atmaz, sadece ucuzlarsa atar.
            deal_key = f"{origin}-{dest}-{deal.date[:7]}" 
            
            old_price = history.get(deal_key, 999999)
            
            # Sinyal Mantığı:
            # 1. İlk defa bulduysak -> GÖNDER
            # 2. Eski fiyattan %5 daha ucuzsa -> GÖNDER
            # 3. Eski fiyatla aynıysa -> SUS (Hafızada tut)
            
            if deal.price_try < old_price * 0.95: # %5'ten fazla indirim
                drop_rate = int((1 - (deal.price_try / old_price)) * 100) if old_price != 999999 else 0
                
                logger.info(f"🚨 SİNYAL: {deal.destination} {deal.price_try} TL (Eski: {old_price})")
                send_telegram(deal, drop_rate)
                
                # Hafızayı Güncelle
                history[deal_key] = deal.price_try
            else:
                logger.info(f"💤 Değişim Yok: {deal.destination} (Güncel: {deal.price_try}, Kayıtlı: {old_price})")
        
        time.sleep(2) # Kısa mola

    save_history(history)

if __name__ == "__main__":
    main()
