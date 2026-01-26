import os
import time
import requests
import logging
from intelligence import IntelligenceGatherer
from engine import AnalysisEngine

# LOGLAMA
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [SNIPER] - %(message)s')
logger = logging.getLogger(__name__)

# AYARLAR (GitHub Secrets'tan alır)
TG_TOKEN = os.getenv('TG_TOKEN')
TG_CHAT_ID = os.getenv('TG_CHAT_ID')
SENT_DEALS_FILE = "sent_deals.txt"

def send_telegram_package(deal):
    """
    Telegram'a Tatil Paketi Formatında (Uçak + Otel + Bavul) Mesaj Atar
    """
    if not TG_TOKEN or not TG_CHAT_ID:
        logger.error("❌ Telegram Token veya ID eksik! GitHub Secrets ayarlarını kontrol et.")
        return

    # Tahmini Otel Fiyatı (Ortalama gecelik 2500 TL varsayımı)
    est_hotel_price = deal.days * 2500 
    total_est = deal.price_try + est_hotel_price

    msg = f"""
<b>✈️ TATİL PAKETİ FIRSATI!</b>

📍 <b>Rota:</b> {deal.origin} ➔ {deal.destination}
📅 <b>Tarih:</b> {deal.date} - {deal.return_date} ({deal.days} Gece)
🏨 <b>Konaklama:</b> Otel/Daire önerileri hazır.

💰 <b>UÇAK BİLETİ:</b> {deal.price_try:,.0f} TL
🛏️ <b>TAHMİNİ OTEL:</b> {est_hotel_price:,.0f} TL (Ort.)
🏷️ <b>TOPLAM TAHMİNİ:</b> {total_est:,.0f} TL

⚠️ <i>{deal.note}</i>
🎒 <i>Bavul Uyarısı: Fiyat 'Eco Light' olabilir. +20kg bagaj için linkten kontrol edin.</i>

🔗 <a href="{deal.link}">✈️ UÇAK BİLETİNE GİT</a>
🔗 <a href="{deal.hotel_link}">🏨 OTELLERE BAK (GOOGLE)</a>
    """

    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {
        "chat_id": TG_CHAT_ID,
        "text": msg,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }

    try:
        requests.post(url, json=payload)
        logger.info(f"✅ Paket gönderildi: {deal.destination}")
    except Exception as e:
        logger.error(f"❌ Mesaj hatası: {e}")

def is_deal_new(deal):
    """Aynı paketi tekrar tekrar atmasın diye kontrol eder"""
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
    
    intel = IntelligenceGatherer()
    engine = AnalysisEngine()

    routes = intel.get_target_routes()
    
    for r in routes:
        logger.info(f"🔎 Taranıyor: {r['origin']} -> {r['dest']}")
        
        # Tarama yap
        deal = engine.scan_route(r['origin'], r['dest'], r['months'], hard_limit=r.get('hard_limit'))
        
        if deal:
            if is_deal_new(deal):
                logger.info(f"🔥 Fırsat: {deal.destination} - {deal.price_try} TL")
                send_telegram_package(deal)
            else:
                logger.info("♻️ Bu fırsat zaten gönderilmiş.")
        
        time.sleep(3) # Anti-spam beklemesi

if __name__ == "__main__":
    main()
