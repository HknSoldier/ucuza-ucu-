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
├── config.py            # Konfigürasyon dosyası
├── requirements.txt     # Python bağımlılıkları
├── test_telegram.py     # Telegram test scripti
├── run.sh               # Hızlı başlatma scripti
├── .github/
│   └── workflows/
│       └── sniper.yml   # GitHub Actions workflow
├── INSTALL.md           # Detaylı kurulum kılavuzu
└── README.md
```

## Hızlı Başlangıç

### 1. GitHub'a Yükle

```bash
git init
git add .
git commit -m "🦅 PROJECT TITAN initialized"
git remote add origin https://github.com/KULLANICI_ADINIZ/ucuza-ucu.git
git push -u origin main
```

### 2. Actions'ı Etkinleştir

- GitHub repo → **Actions** sekmesi
- "I understand my workflows" → **Enable**

### 3. Manuel Test (Opsiyonel)

- Actions → "PROJECT TITAN - Flight Sniper" → **Run workflow**

### 4. Otomatik Çalışma

Artık her 4 saatte bir otomatik tarama yapacak!

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

## Sofia Hack 🔥

Sofia (SOF) rotaları için eşikler çok daha düşük:
- **SOF → JFK**: 10,000 TL (IST'den 20,000 TL daha ucuz!)
- **SOF → LAX**: 12,000 TL
- **SOF → ORD**: 11,000 TL

Bu sayede Türkiye'den Sofia'ya ucuz bilet alıp oradan ABD'ye giderseniz çok ciddi tasarruf edebilirsiniz!

## Konfigürasyon

### Credentials (Hardcoded)

Bot otomatik çalışır, hiç ayar gerekmez:
- Bot Token: `8161806410:AAH4tGpW_kCvQpLOfaB-r2OYQMypPVYtuYg`
- Admin ID: `7684228928`
- Group ID: `-1003515302846`

### Özelleştirme

`config.py` dosyasını düzenleyerek ayarları değiştirebilirsiniz:
- Eşikler (thresholds)
- Havalimanları (origins, destinations)
- Tarama parametreleri
- RSS feed kaynakları

## Test

Telegram botunu test etmek için:

```bash
python test_telegram.py
```

Bu script 3 test mesajı gönderecek:
1. Startup mesajı
2. Mock deal alert
3. Error alert

## Güvenlik

- ✅ Bot tokenleri kodda hardcoded (güvenli, sadece sen kullanıyorsun)
- ✅ Tüm hata durumları yakalanır - kod asla çökmez
- ✅ Rate limiting için rastgele sleep
- ✅ Anti-detection: User-Agent rotation, rastgele tarihler
- ⚠️ **Public repo yapma!** (Tokenler görünür olur)

## Sorun Giderme

### "ModuleNotFoundError"
```bash
pip install -r requirements.txt
playwright install chromium
```

### "Telegram message failed"
- İnternet bağlantısını kontrol et
- Bot token doğru mu kontrol et
- `test_telegram.py` ile test et

### GitHub Actions Hatası
- Logs: Actions → Son çalışma → "Run TITAN" → Detaylar
- Artifact: Logs'u indir ve `titan.log` dosyasını kontrol et

### Detaylı Kurulum
Daha fazla bilgi için `INSTALL.md` dosyasını okuyun.

## Başarı Kriterleri

✅ `python main.py` hata vermeden çalışıyor  
✅ Telegram'a "ONLINE" mesajı geldi  
✅ Logda "Intelligence Cycle Complete" yazıyor  
✅ `titan_state.json` dosyası oluştu  
✅ GitHub Actions yeşil ✓ gösteriyor  

## Lisans

MIT - Özgürce kullan, değiştir, zengin ol! 🚀

---

**Made with 🦅 by TITAN Team**

*Uçuş aramanın keyfini çıkar! ✈️💰*
