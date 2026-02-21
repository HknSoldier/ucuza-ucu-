# 🦅 PROJECT TITAN — Autonomous Flight Intel System

> **7/24 çalışan, sıfır bağımlılıklı, Google Flights tabanlı otonom uçuş fiyat takip sistemi.**
> Sadece gerçekten ucuz biletleri — hedefin yarısı fiyatına ya da daha ucuza — Telegram'dan bildirir.

---

## Alarm Mantığı

Çoğu sistem her indirimde alarm verir. TITAN vermez.

| Uçuş Türü | Alarm Eşiği | Örnek (IST-CDG hedef 3.000 TL) |
|---|---|---|
| ✈️ Direkt | Hedefin **%50'si altı** | 1.500 TL ve altı |
| 🔄 Aktarmalı | Hedefin **%10'u altı** (%90 indirim) | 300 TL ve altı |

**Örnek karşılaştırma:**

| Fiyat | Direkt mi? | Alarm? | Neden? |
|---|---|---|---|
| 2.550 TL | ✅ | ❌ | Hedefin %85'i — yeterince ucuz değil |
| 1.754 TL | ✅ | ❌ | Hedefin %58'i — hâlâ eşiğin üstünde |
| 1.499 TL | ✅ | ✅ | Hedefin %50'nin altı — **ALARM** |
| 900 TL | ✅ | ✅ | Hedefin %30'u — **ALARM** |
| 1.754 TL | 🔄 | ❌ | Aktarmalı, %90 indirimi yok |
| 280 TL | 🔄 | ✅ | Aktarmalı ama %90+ indirim — **ALARM** |

**Günlük limit yok.** Şarta uyan her uçuş alarm verir.
Tek kural: aynı rota + aynı fiyat bandında 24 saat içinde tekrar alarm gelmez.

---

## Nasıl Çalışır?

```
GitHub Actions (günde 4 kez)
        │
        ▼
   scraper.py çalışır
   Google Flights'a HTTP GET atar
        │
        ▼
   HTML parse → ₺ fiyatları çekilir
   Direkt uçuş kontrolü yapılır
   Sanity check (rota bazlı fiyat aralığı)
        │
        ▼
   Direkt: fiyat < hedef × 0.50 ?
   Aktarmalı: fiyat < hedef × 0.10 ?
        │
   ┌────┴────┐
  EVET      HAYIR
   │          │
   ▼          ▼
Telegram    flights.json
 Alarmı     güncellenir
   │          │
   └────┬─────┘
        ▼
  GitHub commit → Dashboard yenilenir
```

---

## Özellikler

- **Sıfır bağımlılık** — Playwright yok, Selenium yok, harici kütüphane yok. Sadece Python stdlib.
- **Direkt uçuş öncelikli** — `nonstop=1&stops=0` parametreleriyle Google'a direkt uçuş isteği gönderilir. Aktarmalı uçuşlar çok daha sıkı eşikle değerlendirilir.
- **Akıllı spam koruması** — Günlük limit yok ama aynı fiyat bandında 24s içinde tekrar alarm gelmez.
- **Veri yaşı kontrolü** — 3 saatten eski veri ile alarm gönderilmez.
- **Rota bazlı sanity check** — Her rota için gerçekçi fiyat aralığı tanımlı, saçma fiyatlar filtrelenir.
- **URL encode edilmiş linkler** — Telegram'da her cihazda doğru açılan Google Flights linkleri.
- **Canlı dashboard** — GitHub Pages üzerinde dark-mode panel, 5 dakikada bir yenilenir.

---

## Dosya Yapısı

```
repo/
├── scraper.py              # Ana motor
├── index.html              # GitHub Pages dashboard
├── requirements.txt        # Boş — dış bağımlılık yok
├── .gitignore
├── flights.json            # ← Otomatik (scraper çıktısı)
├── history.json            # ← Otomatik (spam kontrol)
└── .github/
    └── workflows/
        └── hunt.yml        # GitHub Actions
```

---

## Kurulum

### 1. Repoyu Hazırla

```bash
git clone https://github.com/KULLANICI/REPO.git
cd REPO
mkdir -p .github/workflows
cp hunt.yml .github/workflows/
git add .
git commit -m "🦅 PROJECT TITAN — Kurulum"
git push origin main
```

### 2. Actions Yazma İznini Ver

**Settings → Actions → General → Workflow permissions → Read and write permissions → Save**

### 3. GitHub Pages'i Aç

**Settings → Pages → Branch: main / Folder: / (root) → Save**

`https://KULLANICI.github.io/REPO` adresinde dashboard yayına girer.

### 4. İlk Testi Çalıştır

**Actions → 🦅 PROJECT TITAN → Run workflow**

---

## Konfigürasyon (`scraper.py`)

### Alarm Eşikleri

```python
DIRECT_THRESHOLD   = 0.50   # Direkt uçuş: hedefin %50'si altı
STOPOVER_THRESHOLD = 0.10   # Aktarmalı: hedefin %10'u altı (%90 indirim)
MAX_DATA_AGE_HOURS = 3      # 3 saatten eski veri → alarm yok
```

### Hedef Fiyatlar (TL)

```python
TARGET_PRICES = {
    "IST-CDG": 3000,   # İstanbul → Paris      alarm < 1.500 TL
    "IST-LHR": 3200,   # İstanbul → Londra     alarm < 1.600 TL
    "IST-AMS": 2800,   # İstanbul → Amsterdam  alarm < 1.400 TL
    "IST-BCN": 2900,   # İstanbul → Barselona  alarm < 1.450 TL
    "IST-FCO": 2600,   # İstanbul → Roma       alarm < 1.300 TL
    "IST-MAD": 3100,   # İstanbul → Madrid     alarm < 1.550 TL
    "IST-FRA": 2700,   # İstanbul → Frankfurt  alarm < 1.350 TL
    "IST-MUC": 2500,   # İstanbul → Münih      alarm < 1.250 TL
    "IST-VIE": 2400,   # İstanbul → Viyana     alarm < 1.200 TL
    "IST-PRG": 2600,   # İstanbul → Prag       alarm < 1.300 TL
    "IST-ATH": 1800,   # İstanbul → Atina      alarm <   900 TL
    "IST-DXB": 2200,   # İstanbul → Dubai      alarm < 1.100 TL
    "IST-JFK": 18000,  # İstanbul → New York   alarm < 9.000 TL
    "IST-LAX": 20000,  # İstanbul → L.A.       alarm < 10.000 TL
    "SAW-CDG": 2800,   # Sabiha → Paris        alarm < 1.400 TL
    "SAW-LHR": 3000,   # Sabiha → Londra       alarm < 1.500 TL
    "SAW-AMS": 2600,   # Sabiha → Amsterdam    alarm < 1.300 TL
    "SAW-BCN": 2700,   # Sabiha → Barselona    alarm < 1.350 TL
    "SAW-FCO": 2400,   # Sabiha → Roma         alarm < 1.200 TL
}
```

### Zamanlama (`hunt.yml`)

| UTC   | Türkiye |
|-------|---------|
| 03:00 | 06:00   |
| 09:00 | 12:00   |
| 15:00 | 18:00   |
| 21:00 | 00:00   |

---

## Telegram Alarm Formatı

**Direkt uçuş:**
```
🦅 DİP FİYAT ALARMI 💎
━━━━━━━━━━━━━━━━━━━━━━━━
✈️ Direkt  Rota: IST ➔ CDG
📅 Gidiş: 2026-04-24
📅 Dönüş: 2026-04-27
💰 Fiyat: 1.400 TL
🎯 Hedef: 3.000 TL
🏷️ Havayolu: Çeşitli
📊 Direkt uçuş, hedefin %53 altında!
🌍 Vize: ✅ VİZESİZ (Schengen – Yeşil Pasaport)
━━━━━━━━━━━━━━━━━━━━━━━━
🔍 Google Flights'ta Ara
⚡ HEMEN AL!
```

**Aktarmalı (çok istisnai):**
```
🚨 AKTARMALI – EXTREME FARE ALARMI ⚡
━━━━━━━━━━━━━━━━━━━━━━━━
🔄 Aktarmalı  Rota: IST ➔ JFK
💰 Fiyat: 1.200 TL
🎯 Hedef: 18.000 TL
⚡ Aktarmalı ama hedefin %93 altında! — İstisnai fiyat.
━━━━━━━━━━━━━━━━━━━━━━━━
🔍 Google Flights'ta Ara
⚡ HEMEN AL!
```

---

## `flights.json` Yapısı

```json
{
  "last_updated": "2026-02-22T06:00:00",
  "total_found": 34,
  "below_target": 1,
  "direct_threshold_pct": 50,
  "stopover_threshold_pct": 90,
  "data_source": "google_flights_urllib",
  "flights": [
    {
      "route": "IST-CDG",
      "depart_date": "2026-04-24",
      "return_date": "2026-04-27",
      "price": 1400.0,
      "target": 3000,
      "savings_pct": 53,
      "is_below_target": true,
      "has_stopover": false,
      "google_link": "https://www.google.com/travel/flights?..."
    }
  ]
}
```

---

## Sorun Giderme

**Alarm gelmiyor**
`history.json`'u sıfırla:
```bash
echo '{"alarms":[]}' > history.json
git add history.json && git commit -m "history sıfırlandı" && git push
```

**Fiyat parse edilemiyor**
Log'daki `[DEBUG]` satırına bak. `₺` sembolü HTML'de farklı formatta geliyorsa `extract_prices()` içindeki regex güncellemesi gerekebilir.

**Workflow push hatası**
Settings → Actions → General → **Read and write permissions** seçili olmalı.

**Telegram'a mesaj gitmiyor**
`https://api.telegram.org/bot<TOKEN>/getMe` ile token'ı doğrula. Botu gruba admin olarak ekle, grup ID'sinin başında `-` olduğunu kontrol et.

---

## Güvenlik

`BOT_TOKEN`, `ADMIN_ID`, `GROUP_ID` şu an kodun içinde. Repo **Public** ise GitHub Secrets'a taşı:

**Settings → Secrets and variables → Actions → New repository secret**

```python
# scraper.py
import os
BOT_TOKEN = os.environ["TITAN_BOT_TOKEN"]
ADMIN_ID  = os.environ["TITAN_ADMIN_ID"]
GROUP_ID  = os.environ["TITAN_GROUP_ID"]
```

```yaml
# hunt.yml
env:
  TITAN_BOT_TOKEN: ${{ secrets.TITAN_BOT_TOKEN }}
  TITAN_ADMIN_ID:  ${{ secrets.TITAN_ADMIN_ID }}
  TITAN_GROUP_ID:  ${{ secrets.TITAN_GROUP_ID }}
```

---

<div align="center">

**🦅 PROJECT TITAN v5.4**

*Bilgisayarın kapalıyken bile sistem senin için çalışıyor.*

</div>
