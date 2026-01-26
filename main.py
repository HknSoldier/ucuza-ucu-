import os
import time
import requests
import logging
from intelligence import IntelligenceGatherer
from engine import AnalysisEngine

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [SNIPER] - %(message)s')
logger = logging.getLogger(__name__)

# GitHub Secrets'tan okur
TG_TOKEN = os.getenv('TG_TOKEN')
TG_CHAT_ID = os.getenv('TG_CHAT_ID')
SENT_DEALS_FILE = "sent_deals.txt"

def send_telegram_package(deal):
    if not TG_TOKEN or not TG_CHAT_ID:
        logger.error("❌ HATA: TG_CHAT_ID (Grup ID) bulunamadı! Mesaj atılamıyor.")
        return

    est_hotel_price = deal.days * 2000 
    total_est = deal.price_try + est_hotel_price

    msg = f"""
<b>✈️ TATİL PAKETİ FIRSATI!</b>

📍 <b>Rota:</b> {deal.origin} ➔ {deal.destination}
📅 <b>Tarih:</b> {deal.date} - {deal.return_date} ({deal.days} Gece)
🏨 <b>Konaklama:</b> Otel önerileri eklendi.

💰 <b>UÇAK BİLETİ:</b> {deal.price_try:,.0f} TL
🛏️ <b>TAHMİNİ OTEL:</b> {est_hotel_price:,.0f} TL (Ort.)
🏷️ <b>TOPLAM TAHMİNİ:</b> {total_est:,.0f} TL

⚠️ <i>{deal.note}</i>
🎒 <i>Bavul: Fiyat 'Eco Light' olabilir. +20kg bagajı kontrol et.</i>

🔗 <a href="{deal.link}">✈️ UÇAK BİLETİNE GİT</a>
🔗 <a href="{deal.hotel_link}">🏨 OTELLERE BAK (GOOGLE)</a>
    """

    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {"chat_id": TG_CHAT_ID, "text": msg, "parse_mode": "HTML", "disable_web_page_preview": False}

    try:
        requests.post(url, json=payload)
        logger.info(f"✅ Paket gönderildi: {deal.destination}")
    except Exception as e:
        logger.error(f"❌ Mesaj hatası: {e}")

def is_deal_new(deal):
    price_rounded = int(round(deal.price_try, -2))
    deal_sig = f"{deal.origin}-{deal.destination}-{deal.date}-{price_rounded}"
    
    if not os.path.exists(SENT_DEALS_FILE):
        open(SENT_DEALS_FILE, 'w').close()
    
    with open(SENT_DEALS_FILE, 'r') as f:
        if deal_sig in f.read():
            return False
            
    with open(SENT_DEALS_FILE, 'a') as f:
        f.write(deal_sig + "\n")
    return True

def main():
    logger.info("🚀 TATİL PAKETİ MOTORU BAŞLATILIYOR...")
    
    if not TG_CHAT_ID:
        logger.warning("⚠️ UYARI: Chat ID eksik! Sadece tarama yapılacak, mesaj atılmayacak.")

    intel = IntelligenceGatherer()
    engine = AnalysisEngine()
    routes = intel.get_target_routes()
    
    for r in routes:
        logger.info(f"🔎 Taranıyor: {r['origin']} -> {r['dest']}")
        deal = engine.scan_route(r['origin'], r['dest'], r['months'], hard_limit=r.get('hard_limit'))
        
        if deal:
            if is_deal_new(deal):
                logger.info(f"🔥 Fırsat: {deal.destination} - {deal.price_try} TL")
                send_telegram_package(deal)
            else:
                logger.info("♻️ Bu fırsat zaten gönderilmiş.")
        
        time.sleep(3)

if __name__ == "__main__":
    main()
