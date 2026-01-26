"""
SNIPER ANALYTICS REPORT V2
Patron icin ozel veri analizi ve ozet raporu.
Bu dosya flight_analytics.csv dosyasını okur ve Telegram'a istatistik atar.
"""
import os
import pandas as pd
import requests
import logging

# --- AYARLAR ---
CSV_FILE = "flight_analytics.csv"
TG_TOKEN = os.environ.get("TG_TOKEN")
TG_CHAT_ID = os.environ.get("TG_CHAT_ID")

# Logging (Hata takibi için)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def send_report(msg):
    """
    Oluşturulan raporu Telegram üzerinden kullanıcıya gönderir.
    """
    if not TG_TOKEN or not TG_CHAT_ID:
        logger.error("Telegram Token veya Chat ID bulunamadi!")
        return
        
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {
        "chat_id": TG_CHAT_ID, 
        "text": msg, 
        "parse_mode": "HTML"
    }
    
    try:
        requests.post(url, json=payload)
        logger.info("Rapor Telegram'a basariyla gonderildi.")
    except Exception as e:
        logger.error(f"Telegram gonderme hatasi: {e}")

def main():
    """
    Ana Analiz Fonksiyonu:
    1. CSV dosyasını kontrol et.
    2. Veriyi oku ve temizle.
    3. İstatistikleri hesapla.
    4. Raporu hazırla ve gönder.
    """
    # 1. Dosya Kontrolü
    if not os.path.exists(CSV_FILE):
        send_report("⚠️ <b>Analiz Raporu:</b> Henüz veri dosyası (CSV) oluşmamış. Biraz veri birikmesini bekleyin.")
        return

    try:
        # 2. Veriyi Oku
        df = pd.read_csv(CSV_FILE)
        
        if df.empty:
            send_report("⚠️ <b>Analiz Raporu:</b> Veri dosyası bulundu ama içi boş.")
            return

        # Fiyat sütununu sayıya çevir (Hatalı karakter varsa temizle)
        df['Fiyat (TL)'] = pd.to_numeric(df['Fiyat (TL)'], errors='coerce')
        # Fiyatı olmayan satırları sil
        df.dropna(subset=['Fiyat (TL)'], inplace=True)
        
        if len(df) == 0:
            send_report("⚠️ <b>Analiz Raporu:</b> Geçerli fiyat verisi bulunamadı.")
            return

        # 3. İstatistikleri Hesapla
        total_scan = len(df)
        
        # En düşük fiyatlı satırı bul
        lowest_idx = df['Fiyat (TL)'].idxmin()
        lowest_ever = df.loc[lowest_idx]
        
        # Yeşil alana girenlerin sayısı
        green_zone_count = len(df[df['Yesil Alan'] == 'EVET'])
        
        # Şehirlere göre en ucuz 5 rotayı bul ve sırala
        city_stats = df.groupby('Rota')['Fiyat (TL)'].min().sort_values().head(5)
        
        # Şehir listesini metne dök
        city_report = ""
        for rota, fiyat in city_stats.items():
            city_report += f"✈️ <b>{rota}:</b> {fiyat:,.0f} TL\n"

        # 4. Rapor Metnini Oluştur
        msg = f"""📊 <b>SNIPER GÜNCEL DURUM RAPORU</b>

📅 <b>Toplam Kayıtlı Veri:</b> {total_scan} Adet
🟢 <b>Yakalanan Yeşil Alan:</b> {green_zone_count} Adet

🏆 <b>TARİHİ REKOR (En Ucuz Bilet):</b>
📍 <b>{lowest_ever['Rota']}</b>
💰 <b>{lowest_ever['Fiyat (TL)']:,.0f} TL</b>
🗓 {lowest_ever['Tarih']} ({lowest_ever['Hava Yolu']})

📉 <b>ŞU AN EN UCUZ 5 ROTA (Dip Fiyatlar):</b>
{city_report}

💡 <i>Bu rapor, botun kaydettiği {total_scan} adet verinin analizidir.</i>
"""
        # Gönder
        send_report(msg)

    except Exception as e:
        logger.error(f"Analiz sırasında hata oluştu: {e}")
        send_report(f"⚠️ <b>Kritik Hata:</b> Rapor oluşturulurken bir sorun çıktı:\n{str(e)}")

if __name__ == "__main__":
    main()
