# PROJECT TITAN 🦅

Otonom, gizli ve sağlam Flight Intelligence System.

## 🔒 Güvenlik Güncellemesi

**Public repo için güvenli!** Bot tokenleri artık GitHub Secrets'ta saklanıyor.

## Özellikler

- **Hibrit Scraping Motoru**: fast-flights (hızlı) + Playwright (hata toleranslı)
- **Anti-Bot Koruması**: Rastgele User-Agent, insan benzeri davranış
- **Akıllı Bildirimler**: Sadece gerçek fırsatları bildirir
- **Hub Mantığı**: Sofia arbitraj desteği
- **RSS İstihbaratı**: Trend olan rotaları önceliklendirir
- **Durum Yönetimi**: Fiyat geçmişini hatırlar
- **🔒 Güvenli**: Tokenler GitHub Secrets'ta

## Hızlı Başlangıç (5 Dakika)

### 1️⃣ GitHub Secrets Ekle

**Çok Önemli!** Repo public olduğu için tokenleri korumamız lazım:

1. **GitHub'da:** Bu repo → **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret** ile şu 3 secret'ı ekle:

| Secret Name | Secret Value |
|-------------|--------------|
| `BOT_TOKEN` | `your_bot_token_here` |
| `ADMIN_ID` | `YOUR_ADMIN_ID` |
| `GROUP_ID` | `YOUR_GROUP_ID` |

### 2️⃣ Actions'ı Etkinleştir

- **Actions** sekmesi → "I understand my workflows, go ahead and enable them"

### 3️⃣ İlk Test

- **Actions** → "PROJECT TITAN - Flight Sniper" → **Run workflow**

✅ **Bitti!** Artık her 4 saatte bir otomatik çalışacak.

---

## Yerel Test (Bilgisayarında)

### Windows

```bash
# 1. Dosyaları indir
git clone https://github.com/HknSoldier/ucuza-ucu.git
cd ucuza-ucu

# 2. Environment dosyasını oluştur
copy .env.example .env
# .env dosyasını aç ve tokenlerini yaz

# 3. Kurulum
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium

# 4. Test
python test_telegram.py

# 5. Çalıştır
python main.py
```

### Mac/Linux

```bash
# 1. Dosyaları indir
git clone https://github.com/HknSoldier/ucuza-ucu.git
cd ucuza-ucu

# 2. Environment dosyasını oluştur
cp .env.example .env
# .env dosyasını düzenle ve tokenlerini yaz

# 3. Hızlı kurulum
chmod +x run.sh
./run.sh

# VEYA manuel:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
python test_telegram.py
python main.py
```

---

## Dosya Yapısı

```
project-titan/
├── main.py              # Ana orkestratör
├── scraper_engine.py    # Hibrit scraping motoru
├── intel_center.py      # RSS & rota üreteci
├── notifier.py          # Telegram (SECURE - env vars)
├── config.py            # Konfigürasyon
├── requirements.txt     # Python bağımlılıkları
├── test_telegram.py     # Telegram test scripti
├── .env.example         # Environment örneği (KOPYALA)
├── .env                 # Senin tokenlerin (GİT IGNORE)
├── run.sh               # Hızlı başlatma scripti
├── .github/
│   └── workflows/
│       └── sniper.yml   # GitHub Actions (SECURE)
├── README.md
├── INSTALL.md
└── TROUBLESHOOTING.md   # Sorun giderme kılavuzu
```

---

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

---

## Sofia Hack 🔥

Sofia (SOF) rotaları için eşikler çok daha düşük:
- **SOF → JFK**: 10,000 TL (IST'den 20,000 TL daha ucuz!)
- **SOF → LAX**: 12,000 TL
- **SOF → ORD**: 11,000 TL

**Strateji:** Türkiye → Sofia ucuz bilet + Sofia → ABD = Büyük tasarruf!

---

## Özelleştirme

`config.py` dosyasını düzenle:
- Eşikler (thresholds)
- Havalimanları (origins, destinations)
- Tarama parametreleri
- RSS feed kaynakları

---

## Test

### Telegram Botunu Test Et

```bash
# Yerel test için önce .env dosyasını oluştur
cp .env.example .env
# .env'i düzenle, tokenlerini yaz

# Sonra test et
python test_telegram.py
```

### Syntax Kontrolü

```bash
python -m py_compile *.py
```

---

## Güvenlik

✅ **GitHub Actions**: Tokenler GitHub Secrets'ta (güvenli!)  
✅ **Yerel Test**: `.env` dosyası git ignore'da (güvenli!)  
✅ **Public Repo**: Kodda hiç token yok (güvenli!)  
✅ **Anti-Detection**: User-Agent rotation, rastgele sleep  
✅ **Hata Toleransı**: Kod asla çökmez  

---

## Sorun mu Var?

1. **TROUBLESHOOTING.md** dosyasını oku (her şey orada!)
2. Telegram test et: `python test_telegram.py`
3. Logları kontrol et: `cat titan.log`
4. GitHub Actions logs: Actions → Failed job → Detayları aç

---

## Yaygın Sorunlar

### ❌ "BOT_TOKEN not set"

**GitHub Actions:**
- Settings → Secrets → BOT_TOKEN, ADMIN_ID, GROUP_ID ekle

**Yerel Test:**
```bash
cp .env.example .env
# .env dosyasını düzenle
pip install python-dotenv
```

### ❌ "Telegram message failed"

```bash
# Test et
python test_telegram.py

# Bot token doğru mu?
# Chat ID doğru mu?
# İnternet bağlantısı var mı?
```

### ❌ GitHub Actions Başarısız

```bash
# Secrets eklendi mi?
Settings → Secrets → Actions → Kontrol et

# Logs'a bak
Actions → Failed job → Her step'i aç → Hata mesajını bul
```

---

## Başarı Kriterleri

✅ GitHub Secrets eklendi (BOT_TOKEN, ADMIN_ID, GROUP_ID)  
✅ `python test_telegram.py` çalışıyor  
✅ Telegram'a test mesajı geldi  
✅ GitHub Actions yeşil ✓  
✅ Her 4 saatte bir otomatik tarama yapıyor  

---

## Lisans

MIT - Özgürce kullan, değiştir, zengin ol! 🚀

---

**Made with 🦅 by TITAN Team**

*Güvenli şekilde uçuş ara, zengin ol! ✈️💰🔒*
