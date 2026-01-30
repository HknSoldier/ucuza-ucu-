# PROJECT TITAN 🦅

Otonom, gizli ve sağlam Flight Intelligence System.

## Özellikler

- **Hibrit Scraping Motoru**: fast-flights (hızlı) + Playwright (hata toleranslı)
- **Anti-Bot Koruması**: Rastgele User-Agent, insan benzeri davranış
- **Akıllı Bildirimler**: Sadece gerçek fırsatları bildirir
- **Hub Mantığı**: Sofia arbitraj desteği
- **RSS İstihbaratı**: Trend olan rotaları önceliklendirir
- **Durum Yönetimi**: Fiyat geçmişini hatırlar

## Kurulum

### Yerel Test
```bash
# Bağımlılıkları yükle
pip install -r requirements.txt

# Playwright tarayıcılarını yükle
playwright install chromium

# Çalıştır
python main.py
```

### GitHub Actions

1. Bu repoyu GitHub'a push edin
2. Actions sekmesinde "PROJECT TITAN - Flight Sniper" workflow'unu etkinleştirin
3. Otomatik olarak 4 saatte bir çalışacak

## Dosya Yapısı
```
project-titan/
├── main.py              # Ana orkestratör
├── scraper_engine.py    # Hibrit scraping motoru
├── intel_center.py      # RSS & rota üreteci
├── notifier.py          # Telegram bildirimleri
├── requirements.txt     # Python bağımlılıkları
├── .github/
│   └── workflows/
│       └── sniper.yml   # GitHub Actions workflow
└── README.md
```

## Nasıl Çalışır?

1. **Intel Toplama**: RSS feedlerinden trend destinasyonları çeker
2. **Rota Üretimi**: Stratejik hub'lardan (IST, SAW, SOF vb.) rotalar oluşturur
3. **Akıllı Tarama**: Rastgele tarihler seçer (3-11 ay arası)
4. **Hibrit Scraping**:
   - Önce fast-flights dener (hızlı)
   - Başarısız olursa Playwright açar (garantili)
5. **Deal Analizi**:
   - Fiyat geçmişi ile karşılaştırır
   - Green Zone algılar (%20 altı)
   - Sofia hack eşiklerini uygular
6. **Akıllı Bildirim**: Sadece gerçek fırsatları Telegram'a gönderir

## Sofia Hack

Sofia (SOF) rotaları için eşikler çok daha düşük:
- SOF → JFK: 10,000 TL (IST'den 20,000 TL daha ucuz!)
- SOF → LAX: 12,000 TL

## Konfigürasyon

**Credentials hardcoded** - hiç ayar gerekmez:
- Bot Token: `8161806410:AAH4tGpW_kCvQpLOfaB-r2OYQMypPVYtuYg`
- Admin ID: `7684228928`
- Group ID: `-1003515302846`

## Güvenlik

- Tüm hata durumları yakalanır - kod asla çökmez
- Rate limiting için rastgele sleep
- Anti-detection: User-Agent rotation, rastgele tarihler
- State persistence: JSON dosyasında fiyat geçmişi

## Lisans

MIT - Özgürce kullan, değiştir, zengin ol! 🚀
