# 🦅 PROJECT TITAN — Ultimate Autonomous Flight Intel v2.3

> **7/24 çalışan, kendi kendini onaran, anti-bot sistemlerini aşan ve sadece en kârlı uçuş biletlerini Telegram'dan bildiren tam otonom uçuş istihbarat sistemi.**

---

## 📋 İçindekiler

- [Sistem Mimarisi](#-sistem-mimarisi)
- [Özellikler](#-özellikler)
- [Dosya Yapısı](#-dosya-yapısı)
- [Kurulum Rehberi](#-kurulum-rehberi)
- [Konfigürasyon](#-konfigürasyon)
- [Ghost Protocol — Spam Koruması](#-ghost-protocol--spam-koruması)
- [Anti-Bot Bypass Sistemi](#-anti-bot-bypass-sistemi)
- [Telegram Mesaj Formatı](#-telegram-mesaj-formatı)
- [GitHub Actions Workflow](#-github-actions-workflow)
- [Dashboard (index.html)](#-dashboard-indexhtml)
- [Güvenlik Notları](#-güvenlik-notları)
- [Sorun Giderme](#-sorun-giderme)
- [Katkı ve Geliştirme](#-katkı-ve-geliştirme)

---

## 🏗 Sistem Mimarisi

```
┌─────────────────────────────────────────────────────────────────┐
│                    GITHUB ACTIONS (Ubuntu)                       │
│                    Her 6 saatte bir tetiklenir                   │
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐  │
│  │  hunt.yml    │───▶│  scraper.py  │───▶│  flights.json    │  │
│  │  Scheduler   │    │  Ana Motor   │    │  history.json    │  │
│  └──────────────┘    └──────┬───────┘    └────────┬─────────┘  │
│                             │                     │             │
│                    ┌────────▼────────┐            │             │
│                    │  Playwright +   │            │             │
│                    │  Stealth Layer  │            │             │
│                    └────────┬────────┘            │             │
│                             │                     │             │
│                    ┌────────▼────────┐    ┌───────▼──────────┐ │
│                    │ Google Flights  │    │  GitHub Pages    │ │
│                    │   (Scraping)    │    │  index.html      │ │
│                    └────────┬────────┘    │  Dashboard       │ │
│                             │             └──────────────────┘ │
│                    ┌────────▼────────┐                         │
│                    │ Ghost Protocol  │                         │
│                    │ Spam Filter     │                         │
│                    └────────┬────────┘                         │
│                             │                                   │
│                    ┌────────▼────────┐                         │
│                    │   Telegram Bot  │                         │
│                    │  Admin + Grup   │                         │
│                    └─────────────────┘                         │
└─────────────────────────────────────────────────────────────────┘
```

**Veri akışı:**
1. GitHub Actions her 6 saatte `scraper.py`'yi başlatır
2. Playwright + Stealth, Google Flights'ı insan gibi tarar
3. Veriler filtrelenir (direkt uçuş, sanity check, hedef fiyat karşılaştırması)
4. Ghost Protocol spam kontrolünü yapar
5. Uygunsa Telegram'a alarm gönderilir
6. Tüm sonuçlar `flights.json`'a yazılır ve repoya commit edilir
7. GitHub Pages, `index.html` aracılığıyla dashboard'u sunar

---

## ✨ Özellikler

### 🎯 Dip Avcısı (Price Hunter)
- 19 rota için önceden tanımlanmış hedef fiyatlar
- Hedef altı her uçuşta otomatik alarm
- **Mistake Fare** tespiti: Hedefin %70 altı → anında bildirim (saat kısıtı yok)

### ✈️ Sadece Direkt Uçuşlar
- `stops=0` kuralı mutlak — aktarmalı uçuşlar sistem tarafından kesinlikle işlenmez

### 🧠 Sanity Check (Veri Kalitesi)
- 100 TL altı → vergi hatası, atılır
- 500.000 TL üstü → hatalı veri, atılır

### 📱 Telegram Entegrasyonu
- Admin'e özel mesaj
- Grup kanalına bildirim
- Türkçe, emojili, düzenli format
- Vize durumu (Schengen / UK-ABD) otomatik tespiti

### 🌐 Canlı Dashboard
- GitHub Pages üzerinde dark-mode panel
- Filtreleme: Tüm uçuşlar / Hedef altı / Mistake Fare / Rotaya göre
- Sıralama: Fiyat, indirim oranı, tarih
- 5 dakikada bir otomatik yenileme

---

## 📁 Dosya Yapısı

```
repo/
│
├── scraper.py                  # Ana scraping + Telegram motoru
├── index.html                  # GitHub Pages dashboard
├── requirements.txt            # Python bağımlılıkları
├── .gitignore                  # Git dışı bırakılan dosyalar
│
├── flights.json                # ← Otomatik oluşturulur (scraper çıktısı)
├── history.json                # ← Otomatik oluşturulur (spam kontrol state)
│
└── .github/
    └── workflows/
        └── hunt.yml            # GitHub Actions zamanlayıcı + iş akışı
```

> `flights.json` ve `history.json` dosyaları GitHub Actions tarafından otomatik olarak oluşturulur ve her çalışmada repoya commit edilir. Bunları manuel oluşturman gerekmez.

---

## 🚀 Kurulum Rehberi

### Adım 1 — Repoyu Hazırla

```bash
# GitHub'da yeni bir repo oluştur (Public veya Private)
git clone https://github.com/KULLANICI_ADIN/REPO_ADIN.git
cd REPO_ADIN

# Proje dosyalarını kopyala
cp scraper.py index.html requirements.txt .gitignore ./
mkdir -p .github/workflows
cp hunt.yml .github/workflows/

git add .
git commit -m "🦅 PROJECT TITAN v2.3 — İlk kurulum"
git push origin main
```

### Adım 2 — GitHub Pages'i Aktifleştir

1. Repo sayfasında **Settings** sekmesine gir
2. Sol menüden **Pages** seç
3. **Branch** → `main` | **Folder** → `/ (root)` seç
4. **Save** butonuna bas
5. Birkaç dakika sonra `https://KULLANICI_ADIN.github.io/REPO_ADIN` adresinde dashboard erişilebilir olur

### Adım 3 — Actions İzinlerini Ver

1. **Settings** → **Actions** → **General**
2. **Workflow permissions** bölümünde **Read and write permissions** seç
3. **Save** et

> Bu ayar olmadan workflow, `flights.json` ve `history.json`'ı repoya push edemez.

### Adım 4 — İlk Manuel Testi Yap

1. Repo sayfasında **Actions** sekmesine git
2. **🦅 PROJECT TITAN – Flight Intel Hunter** workflow'unu seç
3. **Run workflow** → **Run workflow** butonuna bas
4. Logları takip et; `scraper.py` çalışıp çalışmadığını kontrol et

### Adım 5 — Otomatik Zamanlama

`hunt.yml` dosyası aşağıdaki saatlerde otomatik tetiklenir (UTC):

| UTC   | Türkiye (UTC+3) |
|-------|-----------------|
| 03:00 | 06:00           |
| 09:00 | 12:00           |
| 15:00 | 18:00           |
| 21:00 | 00:00           |

Değiştirmek istersen `hunt.yml` içindeki cron satırını düzenle:
```yaml
- cron: '0 3,9,15,21 * * *'
```

---

## ⚙️ Konfigürasyon

### `scraper.py` İçindeki Ayarlar

#### Telegram Kimlik Bilgileri
```python
BOT_TOKEN = "8161806410:AAH4tGpW_kCvQpLOfaB-r2OYQMypPVYtuYg"
ADMIN_ID   = "7684228928"
GROUP_ID   = "-1003515302846"
```

#### Hedef Fiyatlar (TL)
```python
TARGET_PRICES = {
    "IST-CDG": 3000,   # İstanbul → Paris
    "IST-LHR": 3200,   # İstanbul → Londra
    "IST-AMS": 2800,   # İstanbul → Amsterdam
    "IST-BCN": 2900,   # İstanbul → Barselona
    "IST-FCO": 2600,   # İstanbul → Roma
    # ... devamı scraper.py içinde
}
```

Yeni rota eklemek için:
```python
TARGET_PRICES["ESB-CDG"] = 2500   # Ankara → Paris için hedef fiyat
```
Aynı zamanda `ROUTES` listesini de güncelle:
```python
ROUTES = list(TARGET_PRICES.keys())
```

#### Sanity Check Eşikleri
```python
def sanity_check(price: float) -> bool:
    return 100 <= price <= 500_000
```
Değiştirmek istersen bu aralığı ihtiyacına göre ayarla.

---

## 👻 Ghost Protocol — Spam Koruması

### Aktif Saatler

| Gün       | Saat Aralığı |
|-----------|--------------|
| Hafta içi | 09:00–20:00  |
| Hafta sonu| 11:00–23:00  |

Bu saatler dışında Telegram'a mesaj **gönderilmez**.

### Mistake Fare İstisnası

Eğer bulunan fiyat, belirlenen hedefin **%70 veya daha fazlası kadar altındaysa** (yani hedefin %30'u veya daha azındaysa), saat kısıtı tamamen bypass edilir ve alarm **anında** iletilir.

```python
def is_mistake_fare(price: float, target: float) -> bool:
    return price <= target * 0.30
```

Örnek: IST-CDG hedef 3000 TL → 900 TL veya altı = Mistake Fare → Gece yarısı bile alarm gelir.

### Anti-Spam Kuralları

| Kural                          | Limit              |
|--------------------------------|--------------------|
| Aynı rota için alarm aralığı   | 24 saat içinde max 1 |
| Günlük toplam alarm             | Max 3              |

Bu kurallar `history.json` dosyası üzerinden takip edilir:

```json
{
  "alarms": [
    { "route": "IST-CDG", "time": "2024-03-15T14:32:00" },
    { "route": "IST-LHR", "time": "2024-03-15T16:45:00" }
  ],
  "daily_count": 2,
  "daily_date": "2024-03-15"
}
```

---

## 🛡️ Anti-Bot Bypass Sistemi

### Playwright + Stealth

- `playwright-stealth` kütüphanesi, Chromium'un otomasyon izlerini gizler
- Her request için **yeni browser context** açılır
- `AutomationControlled` flag'i kapatılır

### İnsan Simülasyonu (Jitter)

```python
async def jitter(min_s=2, max_s=7):
    await asyncio.sleep(random.uniform(min_s, max_s))
```

Tıklamalar ve sayfa yüklemeleri arasına 2–7 saniyelik rastgele beklemeler eklenir.

### Rastgele User-Agent

Her istek, aşağıdaki havuzdan rastgele seçilen bir User-Agent ile yapılır:
- Chrome 121 (Windows)
- Chrome 120 (Windows)
- Chrome 121 (macOS)
- Safari 17.2 (macOS)
- Firefox 122 (Windows)
- Chrome 121 (Linux)
- Edge 119 (Windows)

### Rastgele Viewport

```python
viewport={"width": random.randint(1280, 1920), "height": random.randint(800, 1080)}
```

### Locale & Timezone

```python
locale="tr-TR"
timezone_id="Europe/Istanbul"
```

---

## 📱 Telegram Mesaj Formatı

```
🦅 PROJECT TITAN – DİP FİYAT ALARMI 💎
━━━━━━━━━━━━━━━━━━━━━━━━
✈️ Rota: IST ➔ CDG (Direkt Uçuş)
📅 Tarih: 2024-04-05 ➔ 2024-04-08
💰 Fiyat: 1.850 TL
🏷️ Havayolu: Pegasus Airlines
📊 Analiz: Belirlenen hedefin %38 altında!
✅ Vize Durumu: ✅ VİZESİZ (Schengen – Yeşil Pasaport)
━━━━━━━━━━━━━━━━━━━━━━━━
🔗 ✈️ UÇUŞ LİNKİ
⚡ AKSİYON: HEMEN AL!
```

### Vize Durumu Tespiti

| Havalimanı Kodu | Durum |
|-----------------|-------|
| CDG, AMS, BCN, FCO, FRA, VIE, PRG, ATH... (Schengen) | ✅ VİZESİZ |
| LHR, LGW, JFK, LAX, ORD, YYZ... (UK/ABD/Kanada) | ⚠️ VİZE GEREKLİ |
| Diğerleri | ℹ️ Kontrol edilmeli |

---

## ⚙️ GitHub Actions Workflow

`hunt.yml` dosyası şu adımları sırayla çalıştırır:

```
1. 📥 Repo Checkout
2. 🐍 Python 3.11 Kurulumu (pip cache ile hızlandırılmış)
3. 📦 requirements.txt bağımlılıkları
4. 🎭 Playwright Chromium browser kurulumu
5. 🔧 Sistem bağımlılıkları (libnss3, libatk vb.)
6. 📂 State dosyası kontrolü (history.json, flights.json)
7. 🚀 scraper.py çalıştır
8. 📊 Sonuç özeti logla
9. 💾 flights.json + history.json → Git commit + push
10. 🚨 Hata varsa Telegram'a bildir
```

**Önemli:** `continue-on-error: true` ayarı sayesinde scraper çökse bile commit adımı çalışır ve sistemin state'i korunur.

---

## 🌐 Dashboard (index.html)

GitHub Pages üzerinden erişilen canlı panel:

**URL:** `https://KULLANICI_ADIN.github.io/REPO_ADIN`

### Özellikler

- **Dark mode** — Industrial Cyber teması
- **Canlı istatistikler** — Toplam uçuş / Hedef altı / Mistake Fare / En ucuz fiyat
- **Filtreler** — Tüm uçuşlar, Hedef altı, Mistake Fare, Rota bazlı
- **Sıralama** — Fiyat (artan/azalan), İndirim oranı, Tarih
- **Vize durumu** — Her kartta Schengen/UK-ABD göstergesi
- **Otomatik yenileme** — Her 5 dakikada `flights.json`'ı tekrar çeker
- **Responsive** — Mobil uyumlu

### Veri Akışı

```
flights.json (GitHub'da)
        ↓
    fetch() API
        ↓
   index.html render
        ↓
 Kullanıcı Tarayıcısı
```

---

## 🔐 Güvenlik Notları

### ⚠️ Bot Token Güvenliği

Mevcut kurulumda Bot Token `scraper.py` içine hardcoded yazılmıştır. Reponun **Public** olması durumunda token ifşa olabilir.

**Daha güvenli alternatif — GitHub Secrets kullanımı:**

1. Repo → **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret** ekle:
   - `TITAN_BOT_TOKEN`
   - `TITAN_ADMIN_ID`
   - `TITAN_GROUP_ID`
3. `scraper.py`'de şöyle oku:
   ```python
   import os
   BOT_TOKEN = os.environ["TITAN_BOT_TOKEN"]
   ADMIN_ID  = os.environ["TITAN_ADMIN_ID"]
   GROUP_ID  = os.environ["TITAN_GROUP_ID"]
   ```
4. `hunt.yml`'de env bloğuna ekle:
   ```yaml
   env:
     TITAN_BOT_TOKEN: ${{ secrets.TITAN_BOT_TOKEN }}
     TITAN_ADMIN_ID:  ${{ secrets.TITAN_ADMIN_ID }}
     TITAN_GROUP_ID:  ${{ secrets.TITAN_GROUP_ID }}
   ```

### Telegram Bot Oluşturma (Sıfırdan Başlıyorsan)

1. Telegram'da **@BotFather**'a mesaj at
2. `/newbot` komutunu gönder
3. Bot adı ve kullanıcı adı belirle
4. Verilen token'ı kopyala
5. Botu grubuna admin olarak ekle
6. Grup ID'sini öğrenmek için: `https://api.telegram.org/bot<TOKEN>/getUpdates` adresine git ve gruba bir mesaj at

---

## 🔧 Sorun Giderme

### Workflow çalışıyor ama uçuş bulunamıyor

Google Flights'ın arayüzü zaman zaman CSS selector değiştirir. `scraper.py` içindeki `flight_data_raw = await page.evaluate(...)` bloğundaki selector'ları güncellemeyi dene. Sayfanın kaynak kodunu inceleleyerek güncel class isimlerini bul.

### Playwright kurulum hatası

```bash
# Lokal test için:
pip install playwright playwright-stealth httpx
playwright install chromium
playwright install-deps chromium
```

### `history.json` bozuldu / sıfırlamak istiyorum

```bash
echo '{"alarms":[],"daily_count":0,"daily_date":""}' > history.json
git add history.json && git commit -m "history sıfırlandı" && git push
```

### GitHub Actions push hatası

Settings → Actions → General → **Workflow permissions** → **Read and write permissions** seçili olmalı.

### Telegram'a mesaj gitmiyor

1. Bot token'ın geçerli olduğunu doğrula: `https://api.telegram.org/bot<TOKEN>/getMe`
2. Botu gruba admin olarak eklediğini kontrol et
3. Grup ID'sinin başında `-` işareti olduğundan emin ol (örn: `-1003515302846`)

### Aktif saat dışında test etmek istiyorum

`scraper.py`'deki `is_active_hour()` fonksiyonunu geçici olarak `return True` yapabilirsin.

---

## 📊 `flights.json` Yapısı

```json
{
  "last_updated": "2024-03-15T14:32:00.123456",
  "total_found": 47,
  "below_target": 3,
  "flights": [
    {
      "route": "IST-CDG",
      "origin": "IST",
      "dest": "CDG",
      "depart_date": "2024-04-05",
      "return_date": "2024-04-08",
      "price": 1850.0,
      "airline": "Pegasus Airlines",
      "target": 3000,
      "savings_pct": 38,
      "is_below_target": true,
      "is_mistake_fare": false,
      "scraped_at": "2024-03-15T14:32:00.123456"
    }
  ]
}
```

---

## 🛠️ Katkı ve Geliştirme

### Yeni Rota Eklemek

`scraper.py` içindeki `TARGET_PRICES` sözlüğüne ekle:
```python
"ADB-CDG": 2800,   # İzmir → Paris
"AYT-LHR": 3000,   # Antalya → Londra
```

### Yeni Havayolu Kaynağı Eklemek

`run_scraper()` fonksiyonunda `scrape_google_flights()` yanına Skyscanner veya Kayak için yeni bir async fonksiyon eklenebilir.

### Hafıza Temizleme Aralığını Değiştirmek

`can_send_alarm()` içindeki `timedelta(days=30)` değerini değiştir.

---

## 📜 Lisans

Bu proje kişisel kullanım amaçlıdır. Ticari kullanım, toplu veri kazıma veya ilgili platformların hizmet şartlarını ihlal edecek şekilde kullanım kullanıcının sorumluluğundadır.

---

<div align="center">

**🦅 PROJECT TITAN v2.3 ENTERPRISE**

*Bilgisayarın kapalıyken bile sistem senin için çalışıyor.*

</div>
