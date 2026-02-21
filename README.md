# 🦅 PROJECT TITAN — Autonomous Flight Intel System

> **7/24 çalışan, sıfır bağımlılıklı, Google Flights tabanlı tam otonom uçuş fiyat takip sistemi. Ucuz biletleri Telegram'dan anında bildirir.**

---

## Nasıl Çalışır?

```
GitHub Actions (her 6 saatte bir)
        │
        ▼
   scraper.py
   Google Flights'a HTTP isteği atar
        │
        ▼
   Fiyat parse edilir
   Direkt uçuş kontrolü yapılır
   Sanity check uygulanır
        │
        ▼
   Hedef fiyatın altında mı?
        │
   ┌────┴────┐
  EVET      HAYIR
   │          │
   ▼          ▼
Telegram   flights.json
 Alarmı    güncellenir
   │          │
   └────┬─────┘
        ▼
  GitHub'a commit
  Dashboard yenilenir
```

---

## Özellikler

**Fiyat Takibi**
- 19 rota için önceden tanımlanmış hedef fiyatlar (TL)
- Hedefin %85'i altı → Dip Fiyat Alarmı
- Hedefin %50'si altı → Mistake Fare Alarmı (çok daha agresif eşik)

**Direkt Uçuş Zorunluluğu**
- Aktarmalı uçuşlar varsayılan olarak filtrelenir
- HTML'de aktarma belirtisi tespit edilirse (aktarma, layover, 1 stop vb.) uçuş yalnızca Mistake Fare eşiğini geçiyorsa alarmlanır, aksi hâlde atlanır

**Veri Kalitesi**
- Rota bazlı fiyat aralığı kontrolü (örn. IST-CDG için 1.500–15.000 TL)
- Yalnızca ₺ sembolünün yanındaki sayılar fiyat olarak kabul edilir — yanlış parse riski minimuma indirilmiştir
- 3 saatten eski veri ile alarm gönderilmez

**Spam Koruması**
- Aynı rota için 24 saat içinde en fazla 1 alarm
- Günlük toplam alarm limiti: 3
- 30 günden eski alarm kayıtları otomatik temizlenir

**Sıfır Bağımlılık**
- Playwright yok, Selenium yok, harici kütüphane yok
- Yalnızca Python stdlib: `urllib`, `gzip`, `zlib`, `re`, `json`
- GitHub Actions'ta kurulum adımı gerekmez

**Dashboard**
- GitHub Pages üzerinde canlı dark-mode panel
- Filtreler: Tüm uçuşlar / Hedef altı / Mistake Fare / Rotaya göre
- Her 5 dakikada otomatik yenileme

---

## Dosya Yapısı

```
repo/
├── scraper.py              # Ana motor — Google Flights tarama + Telegram alarmı
├── index.html              # GitHub Pages dashboard
├── requirements.txt        # Boş — dış bağımlılık yok
├── .gitignore
├── flights.json            # ← Otomatik oluşturulur (scraper çıktısı)
├── history.json            # ← Otomatik oluşturulur (spam kontrol state)
└── .github/
    └── workflows/
        └── hunt.yml        # GitHub Actions zamanlayıcı
```

---

## Kurulum

### 1. Repoyu Hazırla

```bash
git clone https://github.com/KULLANICI/REPO.git
cd REPO
cp scraper.py index.html requirements.txt .gitignore ./
mkdir -p .github/workflows
cp hunt.yml .github/workflows/
git add .
git commit -m "🦅 PROJECT TITAN — İlk kurulum"
git push origin main
```

### 2. Actions Yazma İznini Ver

**Settings → Actions → General → Workflow permissions → Read and write permissions → Save**

Bu ayar olmadan workflow `flights.json` ve `history.json`'ı repoya push edemez.

### 3. GitHub Pages'i Aç

**Settings → Pages → Branch: main / Folder: / (root) → Save**

Birkaç dakika sonra dashboard şu adreste yayına girer:
`https://KULLANICI.github.io/REPO`

### 4. İlk Testi Çalıştır

**Actions → 🦅 PROJECT TITAN – Flight Intel Hunter → Run workflow**

---

## Konfigürasyon

### Telegram Kimlik Bilgileri (`scraper.py`)

```python
BOT_TOKEN = "..."        # @BotFather'dan alınan token
ADMIN_ID  = "..."        # Kişisel Telegram ID'n
GROUP_ID  = "-100..."    # Grup ID'si (başında - işareti olmalı)
```

### Hedef Fiyatlar (TL)

```python
TARGET_PRICES = {
    "IST-CDG": 3000,   # İstanbul → Paris
    "IST-LHR": 3200,   # İstanbul → Londra
    "IST-AMS": 2800,   # İstanbul → Amsterdam
    "IST-BCN": 2900,   # İstanbul → Barselona
    "IST-FCO": 2600,   # İstanbul → Roma
    "IST-MAD": 3100,   # İstanbul → Madrid
    "IST-FRA": 2700,   # İstanbul → Frankfurt
    "IST-MUC": 2500,   # İstanbul → Münih
    "IST-VIE": 2400,   # İstanbul → Viyana
    "IST-PRG": 2600,   # İstanbul → Prag
    "IST-ATH": 1800,   # İstanbul → Atina
    "IST-DXB": 2200,   # İstanbul → Dubai
    "IST-JFK": 18000,  # İstanbul → New York
    "IST-LAX": 20000,  # İstanbul → Los Angeles
    "SAW-CDG": 2800,   # Sabiha → Paris
    "SAW-LHR": 3000,   # Sabiha → Londra
    "SAW-AMS": 2600,   # Sabiha → Amsterdam
    "SAW-BCN": 2700,   # Sabiha → Barselona
    "SAW-FCO": 2400,   # Sabiha → Roma
}
```

Yeni rota eklemek için bu sözlüğe eklemen yeterli, `ROUTES` otomatik güncellenir.

### Alarm Eşikleri

```python
ALARM_THRESHOLD   = 0.85   # Hedefin %85'i altı → Dip Fiyat Alarmı
MISTAKE_THRESHOLD = 0.50   # Hedefin %50'si altı → Mistake Fare Alarmı
MAX_DATA_AGE_HOURS = 3     # 3 saatten eski veri → alarm gönderilmez
```

### Zamanlama (`hunt.yml`)

Varsayılan olarak günde 4 kez çalışır (UTC):

| UTC   | Türkiye (UTC+3) |
|-------|-----------------|
| 03:00 | 06:00           |
| 09:00 | 12:00           |
| 15:00 | 18:00           |
| 21:00 | 00:00           |

Değiştirmek için `hunt.yml` içindeki cron satırını düzenle:
```yaml
- cron: '0 3,9,15,21 * * *'
```

---

## Alarm Mantığı

```
Fiyat bulundu
    │
    ├─ Sanity check geçmedi? → Atla
    │
    ├─ Veri 3 saatten eski? → Atla
    │
    ├─ Aktarmalı uçuş?
    │       ├─ Mistake Fare değil → Atla
    │       └─ Mistake Fare → Devam et
    │
    ├─ Günlük 3 alarm doldu? → Atla
    │
    ├─ Aynı rotaya 24s içinde alarm gitti? → Atla
    │
    └─ Telegram'a gönder ✅
```

---

## Telegram Alarm Formatı

**Dip Fiyat Alarmı:**
```
🦅 DİP FİYAT ALARMI 💎
━━━━━━━━━━━━━━━━━━━━━━━━
✈️ Rota: IST ➔ CDG
📅 Gidiş: 2026-04-24
📅 Dönüş: 2026-04-27
💰 Fiyat: 2.450 TL
🎯 Hedef: 3.000 TL
🏷️ Havayolu: Çeşitli
📊 Hedefin %18 altında!
🌍 Vize: ✅ VİZESİZ (Schengen – Yeşil Pasaport)
━━━━━━━━━━━━━━━━━━━━━━━━
🔍 Google Flights'ta Ara
⚡ HEMEN AL!
```

**Mistake Fare Alarmı:**
```
🚨 MISTAKE FARE ALARMI ⚡
━━━━━━━━━━━━━━━━━━━━━━━━
✈️ Rota: IST ➔ LHR
📅 Gidiş: 2026-05-02
📅 Dönüş: 2026-05-05
💰 Fiyat: 1.400 TL
🎯 Hedef: 3.200 TL
🏷️ Havayolu: Çeşitli
⚡ MISTAKE FARE! Hedefin %56 altında!
🌍 Vize: ⚠️ VİZE GEREKLİ (UK/ABD/Kanada)
━━━━━━━━━━━━━━━━━━━━━━━━
🔍 Google Flights'ta Ara
⚡ HEMEN AL!
```

---

## `flights.json` Yapısı

```json
{
  "last_updated": "2026-02-21T18:00:00",
  "total_found": 34,
  "below_target": 2,
  "alarm_threshold_pct": 15,
  "data_source": "google_flights_urllib",
  "flights": [
    {
      "route": "IST-CDG",
      "origin": "IST",
      "dest": "CDG",
      "depart_date": "2026-04-24",
      "return_date": "2026-04-27",
      "price": 2450.0,
      "airline": "Çeşitli",
      "target": 3000,
      "alarm_threshold": 2550,
      "savings_pct": 18,
      "is_below_target": true,
      "is_mistake_fare": false,
      "google_link": "https://www.google.com/travel/flights?...",
      "scraped_at": "2026-02-21T18:00:00",
      "data_source": "google_flights"
    }
  ]
}
```

---

## Sorun Giderme

**Uçuş bulunamıyor (veri yok)**
Google Flights'ın HTML yapısı değişmiş olabilir. `scraper.py` içindeki `extract_prices()` fonksiyonundaki regex pattern'larını güncelle. Log'da `[DEBUG]` satırlarına bak — ₺ sembolünün HTML'de hangi formatta geçtiğini gösterir.

**Alarm gelmiyor**
`history.json` dosyasını kontrol et. Günlük limit (3) dolmuş olabilir. Sıfırlamak için:
```bash
echo '{"alarms":[],"daily_count":0,"daily_date":""}' > history.json
git add history.json && git commit -m "history sıfırlandı" && git push
```

**Workflow push hatası**
Settings → Actions → General → Workflow permissions → **Read and write permissions** seçili olmalı.

**Telegram'a mesaj gitmiyor**
Bot token'ı doğrula: `https://api.telegram.org/bot<TOKEN>/getMe`
Botu gruba admin olarak eklediğini ve grup ID'sinin başında `-` olduğunu kontrol et.

---

## Güvenlik Notu

`BOT_TOKEN`, `ADMIN_ID` ve `GROUP_ID` şu an `scraper.py` içinde doğrudan yazılıdır. Repo **Public** ise bunları GitHub Secrets'a taşıman önerilir:

**Settings → Secrets and variables → Actions → New repository secret**

```python
# scraper.py içinde:
import os
BOT_TOKEN = os.environ["TITAN_BOT_TOKEN"]
ADMIN_ID  = os.environ["TITAN_ADMIN_ID"]
GROUP_ID  = os.environ["TITAN_GROUP_ID"]
```

```yaml
# hunt.yml içinde:
env:
  TITAN_BOT_TOKEN: ${{ secrets.TITAN_BOT_TOKEN }}
  TITAN_ADMIN_ID:  ${{ secrets.TITAN_ADMIN_ID }}
  TITAN_GROUP_ID:  ${{ secrets.TITAN_GROUP_ID }}
```

---

<div align="center">

**🦅 PROJECT TITAN v5.3**

*Bilgisayarın kapalıyken bile sistem senin için çalışıyor.*

</div>
