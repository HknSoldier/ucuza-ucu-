import os, time, random, requests, logging, csv
from datetime import datetime
from intelligence import IntelligenceGatherer
from engine import AnalysisEngine, HotelEngine

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# CSV DOSYASI ADI
ANALYTICS_FILE = "flight_analytics.csv"

CITY_MAP = {
    'AUH': 'Abu Dhabi', 'DOH': 'Doha', 
    'FRA': 'Frankfurt', 'MUC': 'Munich', 'BER': 'Berlin', 'CGN': 'Cologne', 'DUS': 'Dusseldorf', 'HAM': 'Hamburg',
    'CDG': 'Paris', 'LYS': 'Lyon', 'NCE': 'Nice', 'PAR': 'Paris',
    'FCO': 'Rome', 'MXP': 'Milan', 'VCE': 'Venice', 'NAP': 'Naples', 'MIL': 'Milan', 'ROM': 'Rome',
    'BCN': 'Barcelona', 'MAD': 'Madrid', 'AGP': 'Malaga', 'LIS': 'Lisbon', 'OPO': 'Porto',
    'AMS': 'Amsterdam', 'BRU': 'Brussels', 'VIE': 'Vienna', 'PRG': 'Prague', 'BUD': 'Budapest',
    'ZRH': 'Zurich', 'GVA': 'Geneva',
    'CPH': 'Copenhagen', 'ARN': 'Stockholm', 'OSL': 'Oslo',
    'ATH': 'Athens', 'SKG': 'Thessaloniki', 'IST': 'Istanbul', 'ADB': 'Izmir', # <-- IZMIR EKLENDI
    'BEG': 'Belgrade', 'SJJ': 'Sarajevo', 'TIA': 'Tirana', 'SKP': 'Skopje', 'TGD': 'Podgorica',
    'PRN': 'Pristina', 'TBS': 'Tbilisi', 'GYD': 'Baku', 'SOF': 'Sofia',
    'BKK': 'Bangkok', 'HKT': 'Phuket', 'SIN': 'Singapore', 'ICN': 'Seoul', 'TYO': 'Tokyo',
    'DPS': 'Bali', 'KUL': 'Kuala Lumpur', 'MLE': 'Male',
    'GRU': 'Sao Paulo', 'GIG': 'Rio de Janeiro', 'EZE': 'Buenos Aires', 'BOG': 'Bogota',
    'CCS': 'Caracas', 'HAV': 'Havana', 'CUN': 'Cancun',
    'CMN': 'Casablanca', 'RAK': 'Marrakech', 'CAI': 'Cairo', 'HRG': 'Hurghada', 'SSH': 'Sharm El Sheikh',
    'JNB': 'Johannesburg', 'CPT': 'Cape Town', 'LON': 'London', 'STN': 'London'
}

def is_deal_new(deal):
    DB_FILE = "sent_deals.txt"
    deal_id = f"{deal.origin}-{deal.destination}-{deal.date}-{deal.price_try:.0f}"
    if not os.path.exists(DB_FILE): return True
    with open(DB_FILE, "r") as f: sent_deals = f.read().splitlines()
    return deal_id not in sent_deals

def save_deal(deal):
    DB_FILE = "sent_deals.txt"
    deal_id = f"{deal.origin}-{deal.destination}-{deal.date}-{deal.price_try:.0f}"
    with open(DB_FILE, "a") as f: f.write(deal_id + "\n")

def save_to_analytics(deal):
    file_exists = os.path.isfile(ANALYTICS_FILE)
    with open(ANALYTICS_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Tarih', 'Saat', 'Rota', 'Hava Yolu', 'Gidis', 'Donus', 'Fiyat (TL)', 'Yesil Alan', 'Not'])
        
        now = datetime.now()
        writer.writerow([
            now.strftime("%Y-%m-%d"), 
            now.strftime("%H:%M"), 
            f"{deal.origin}-{deal.destination}", 
            deal.airline, 
            deal.date, 
            deal.return_date, 
            f"{deal.price_try:.0f}", 
            "EVET" if deal.is_green else "HAYIR", 
            deal.note
        ])

def get_hotel_with_failover(hotel_engine, destination_code, check_in, check_out):
    city_name = CITY_MAP.get(destination_code, destination_code)
    for i in range(1, 4):
        key = os.environ.get(f'SERPAPI_KEY_{i}')
        if not key: continue
        hotel_engine.api_key = key
        hotel = hotel_engine.get_best_hotel(city_name, check_in, check_out)
        if hotel: return hotel
    return None

def send_telegram(token, chat_id, deal, hotel, hack_note):
    flags = {
        'IST': '🇹🇷', 'ADB': '🇹🇷', 'SOF': '🇧🇬', 'LON': '🇬🇧', 'AUH': '🇦🇪', 'DOH': '🇶🇦',
        'FRA': '🇩🇪', 'MUC': '🇩🇪', 'BER': '🇩🇪', 'CGN': '🇩🇪', 'DUS': '🇩🇪', 'HAM': '🇩🇪',
        'CDG': '🇫🇷', 'LYS': '🇫🇷', 'NCE': '🇫🇷', 'PAR': '🇫🇷',
        'FCO': '🇮🇹', 'MXP': '🇮🇹', 'VCE': '🇮🇹', 'NAP': '🇮🇹', 'MIL': '🇮🇹', 'ROM': '🇮🇹',
        'BCN': '🇪🇸', 'MAD': '🇪🇸', 'AGP': '🇪🇸', 'LIS': '🇵🇹', 'OPO': '🇵🇹',
        'AMS': '🇳🇱', 'BRU': '🇧🇪', 'VIE': '🇦🇹', 'PRG': '🇨🇿', 'BUD': '🇭🇺', 'ZRH': '🇨🇭', 'GVA': '🇨🇭',
        'CPH': '🇩🇰', 'ARN': '🇸🇪', 'OSL': '🇳🇴', 'ATH': '🇬🇷', 'SKG': '🇬🇷', 'GYD': '🇦🇿',
        'BEG': '🇷🇸', 'SJJ': '🇧🇦', 'TIA': '🇦🇱', 'SKP': '🇲🇰', 'TGD': '🇲🇪', 'PRN': '🇽🇰', 'TBS': '🇬🇪',
        'BKK': '🇹🇭', 'HKT': '🇹🇭', 'SIN': '🇸🇬', 'ICN': '🇰🇷', 'TYO': '🇯🇵', 'DPS': '🇮🇩', 'KUL': '🇲🇾', 'MLE': '🇲🇻',
        'GRU': '🇧🇷', 'GIG': '🇧🇷', 'EZE': '🇦🇷', 'BOG': '🇨🇴', 'CCS': '🇻🇪', 'HAV': '🇨🇺', 'CUN': '🇲🇽',
        'CMN': '🇲🇦', 'RAK': '🇲🇦', 'CAI': '🇪🇬', 'HRG': '🇪🇬', 'SSH': '🇪🇬', 'JNB': '🇿🇦', 'CPT': '🇿🇦'
    }
    
    flag_origin = flags.get(deal.origin, '✈️')
    flag_dest = flags.get(deal.destination, '✈️')
    city = CITY_MAP.get(deal.destination, deal.destination)
    
    hotel_info = "🏨 Uygun otel bulunamadı."
    # DÜZELTME: Eğer otel bulunduysa, SerpApi'den gelen gerçek linki kullan.
    # Bulunamazsa manuel link oluştur.
    h_link = f"https://www.google.com/travel/hotels?q={city}+hotels&check_in_date={deal.date}&check_out_date={deal.return_date}"
    
    if hotel:
        hotel_info = f"🏨 <b>{hotel['name']}</b>\n💰 {hotel['price']:,.0f} TL | ⭐ {hotel['rating']}/5\n✅ Ücretsiz İptal & Özel Fırsat"
        if 'link' in hotel and hotel['link']:
            h_link = hotel['link'] # <-- İŞTE BU: Gerçek link

    price_txt = f"{deal.native_price:,.0f} {deal.native_currency}"
    if deal.native_currency != "TL": price_txt += f" (~{deal.price_try:,.0f} TL)"

    msg = f"""🎯 <b>SNIPER GLOBAL FIRSATI!</b>

{flag_origin} <b>{deal.origin}</b> ➡️ {flag_dest} <b>{deal.destination}</b>
ℹ️ <b>{hack_note}</b>
🟢 <b>DURUM: GERÇEK DÜŞÜK FİYAT DOĞRULANDI ✅</b>

📅 <b>Tarih:</b> {deal.date} / {deal.return_date} ({deal.days} Gün)
✈️ <b>Havayolu:</b> {deal.airline}
💰 <b>FİYAT: {price_txt}</b>

-------------------------------
{hotel_info}
-------------------------------

🔗 <a href="{deal.link}">UÇUŞU GÖR</a> | <a href="{h_link}">OTEL ARA/GÖR</a>

📊 <i>{deal.note}</i>
"""
    requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id": chat_id, "text": msg, "parse_mode": "HTML", "disable_web_page_preview": True})
    save_deal(deal)

def main():
    tg_token = os.environ.get('TG_TOKEN'); tg_chat_id = os.environ.get('TG_CHAT_ID')
    intel = IntelligenceGatherer(); engine = AnalysisEngine(); hotel_engine = HotelEngine(None)
    
    current_hour = datetime.now().hour
    SILENT_MODE = 2 <= current_hour <= 6 
    
    if SILENT_MODE:
        print(f"🌙 GECE BEKÇİSİ MODU AKTİF (Saat: {current_hour}). Mesaj atılmayacak, sadece kaydedilecek.")

    routes = intel.get_target_routes()
    for r in routes:
        deal = engine.scan_route(r['origin'], r['dest'], r['months'], r['hard_limit'])
        if deal:
            save_to_analytics(deal)
            
            if deal.is_green and is_deal_new(deal):
                if not SILENT_MODE:
                    hotel = get_hotel_with_failover(hotel_engine, r['dest'], deal.date, deal.return_date)
                    send_telegram(tg_token, tg_chat_id, deal, hotel, r['hack_note'])
                else:
                    print(f"🌙 Gece Fırsatı Yakalandı (Sessiz): {deal.destination} - {deal.price_try} TL")
            
            time.sleep(random.uniform(20, 30))

if __name__ == "__main__":
    main()
