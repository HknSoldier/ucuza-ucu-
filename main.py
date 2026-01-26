import os
import time
import requests
import logging
import random
from intelligence import IntelligenceGatherer
from engine import AnalysisEngine
from state_manager import StateManager

# LOGLAMA
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [SNIPER] - %(message)s')
logger = logging.getLogger(__name__)

# AYARLAR
TG_TOKEN = os.getenv('TG_TOKEN')
TG_CHAT_ID = os.getenv('TG_CHAT_ID')

def send_telegram_package(deal):
    if not TG_TOKEN or not TG_CHAT_ID: return

    est_hotel_price = deal.days * 2500 
    total_est = deal.price_try + est_hotel_price

    msg = f"""
<b>🌍 DÜNYA TURU FIRSATI!</b>

📍 <b>{deal.origin} ➔ {deal.destination}</b>
📅 {deal.date} | {deal.days} Gece
💰 <b>Bilet:</b> {deal.price_try:,.0f} TL
🏨 <b>Otel (Ort):</b> {est_hotel_price:,.0f} TL
🏷️ <b>Toplam:</b> {total_est:,.0f} TL

⚠️ {deal.note}
🎒 <i>Bavul: Eco Light olabilir.</i>

🔗 <a href="{deal.link}">UÇAK</a> | <a href="{deal.hotel_link}">OTEL</a>
    """
    try:
        requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", 
                     json={"chat_id": TG_CHAT_ID, "text": msg, "parse_mode": "HTML", "disable_web_page_preview": False})
        logger.info(f"✅ Mesaj atıldı: {deal.destination}")
    except: pass

def main():
    logger.info("🕷️ SİBER ÖRÜMCEK (WORLDWIDE) BAŞLATILIYOR...")
    
    if not TG_CHAT_ID: logger.warning("⚠️ Chat ID yok!")

    # Modülleri Yükle
    intel = IntelligenceGatherer()
    engine = AnalysisEngine()
    memory = StateManager()

    # Tüm Rotaları Oluştur (Yaklaşık 500+ Rota)
    all_routes = intel.get_all_combinations()
    total_routes = len(all_routes)
    
    # Kaldığımız yeri hatırla
    start_index = memory.get_start_index()
    
    # Eğer liste bitmişse başa dön
    if start_index >= total_routes:
        memory.reset_state()
        start_index = 0
    
    # Bu oturumda taranacak miktar (Google'a yakalanmamak için posta posta)
    BATCH_SIZE = 40 
    end_index = min(start_index + BATCH_SIZE, total_routes)
    
    logger.info(f"📂 Hafıza: {start_index}. sıradan devam ediliyor.")
    logger.info(f"🎯 Hedef: {start_index} ile {end_index} arası taranacak (Toplam: {total_routes})")

    # Taramayı Başlat
    current_batch = all_routes[start_index:end_index]
    
    for i, r in enumerate(current_batch):
        real_index = start_index + i
        logger.info(f"🔎 [{real_index}/{total_routes}] Taranıyor: {r['origin']} -> {r['dest']}")
        
        deal = engine.scan_route(r['origin'], r['dest'], r['months'], hard_limit=r.get('hard_limit'))
        
        if deal:
            logger.info(f"🔥 FIRSAT: {deal.destination} - {deal.price_try} TL")
            send_telegram_package(deal)
        
        # Hafızayı Güncelle (Her taramada kaydet ki çökse bile unutmasın)
        memory.update_state(real_index + 1, 1)
        
        # YAKALANMAMAK İÇİN BEKLEME (Anti-Detection)
        # 8 ile 15 saniye arası rastgele bekle
        sleep_time = random.uniform(8, 15)
        logger.info(f"💤 Gizleniyor... ({sleep_time:.1f}s)")
        time.sleep(sleep_time)

    logger.info("🏁 Bu posta bitti. Dinlenmeye geçiliyor...")

if __name__ == "__main__":
    main()
