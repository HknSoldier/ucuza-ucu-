# PROJECT TITAN - Troubleshooting Guide 🔧

## GitHub Actions Sorunları

### ❌ Hata 1: "Billing & Plans" Hatası

**Görünen Mesaj:**
```
The job was not started because recent account payments have failed 
or your spending limit needs to be increased.
```

**Çözüm A: Repo'yu Public Yap (ÜCRETSİZ)**
```bash
# GitHub → ucuza-ucu → Settings → Danger Zone → Change visibility → Make public
```

⚠️ **UYARI:** Public yaparsan bot tokenin görünür olur!

**Çözüm B: Private Kalsın, Secrets Kullan**

1. Bot tokenlerini koddan çıkar, GitHub Secrets'a taşı:
   - Settings → Secrets and variables → Actions → New repository secret
   - İsim: `BOT_TOKEN`, Değer: `your_bot_token_here`
   - İsim: `ADMIN_ID`, Değer: `YOUR_ADMIN_ID`
   - İsim: `GROUP_ID`, Değer: `YOUR_GROUP_ID`

2. `notifier.py` dosyasını güncelle:
```python
import os

class TelegramNotifier:
    def __init__(self):
        # Use secrets from environment (GitHub Actions)
        self.bot_token = os.environ.get("BOT_TOKEN", "your_bot_token_here")
        self.admin_id = int(os.environ.get("ADMIN_ID", "YOUR_ADMIN_ID"))
        self.group_id = int(os.environ.get("GROUP_ID", "YOUR_GROUP_ID"))
        ...
```

3. `sniper.yml` dosyasına env ekle:
```yaml
- name: Run TITAN
  run: python main.py
  env:
    BOT_TOKEN: ${{ secrets.BOT_TOKEN }}
    ADMIN_ID: ${{ secrets.ADMIN_ID }}
    GROUP_ID: ${{ secrets.GROUP_ID }}
```

**Çözüm C: Billing Ayarını Yap**
- GitHub → Settings (profil) → Billing and plans → Set up a spending limit
- Minimum $1 limit koy (aylık 2,000 dakika ücretsiz, sonrası dakika başı $0.008)

---

### ❌ Hata 2: Job 2-5 Saniyede Başarısız Oluyor

**Olası Nedenler:**
1. Python syntax hatası
2. Import hatası (eksik kütüphane)
3. Playwright kurulumu başarısız

**Nasıl Debug Edilir:**

1. **Logları İndir:**
   - Actions → Failed job → "hunt" → Artifacts → Download logs

2. **Hangi Adımda Hata Aldığını Bul:**
   - Her step'i aç (Install dependencies, Run TITAN, vb.)
   - Kırmızı ❌ olan adıma tıkla
   - Hata mesajını kopyala

3. **Yaygın Hatalar ve Çözümleri:**

**Hata:** `ModuleNotFoundError: No module named 'playwright'`
```yaml
# sniper.yml'de bu satırı kontrol et:
- name: Install dependencies
  run: pip install -r requirements.txt
```

**Hata:** `playwright._impl._errors.Error: Executable doesn't exist`
```yaml
# Playwright browsers kurulmamış, şunu ekle:
- name: Install Playwright browsers
  run: |
    playwright install chromium
    playwright install-deps chromium
```

**Hata:** `ImportError: cannot import name 'FlightData' from 'fast_flights'`
```python
# fast-flights kütüphanesi bozuk, requirements.txt'den kaldır
# Zaten Playwright fallback var, sorun yok
```

---

### ❌ Hata 3: "This job failed" (Detay Yok)

**Çözüm:** Daha detaylı log almak için `sniper.yml`'e ekle:

```yaml
- name: Run TITAN
  run: |
    python main.py 2>&1 | tee titan_run.log
  env:
    PYTHONUNBUFFERED: 1
```

---

### ❌ Hata 4: Playwright Timeout

**Görünen Mesaj:**
```
playwright._impl._errors.TimeoutError: Timeout 60000ms exceeded
```

**Çözüm:** Timeout süresini artır:

`scraper_engine.py` içinde:
```python
await page.goto(url, wait_until='networkidle', timeout=120000)  # 60000'den 120000'e çıkar
```

---

## Yerel Test Sorunları

### ❌ Hata: "pip install playwright" Çalışmıyor

**Çözüm:**
```bash
# Python 3.11+ kullandığından emin ol
python --version

# Virtual environment kullan
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

---

### ❌ Hata: "playwright install chromium" Başarısız

**Çözüm:**
```bash
# Manuel kurulum
playwright install chromium --with-deps

# Eğer hala çalışmazsa sistem bağımlılıkları:
# Ubuntu/Debian:
sudo apt-get install libnss3 libnspr4 libdbus-1-3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2

# Mac:
# Genellikle sorun çıkmaz, eğer çıkarsa Homebrew ile:
brew install chromium
```

---

## Telegram Bot Sorunları

### ❌ Mesaj Gelmiyor

**Test Et:**
```bash
python test_telegram.py
```

**Olası Sorunlar:**

1. **Bot token yanlış:**
   - @BotFather'a git
   - `/mybots` → Botunu seç → API Token
   - Kopyala ve `notifier.py`'de güncelle

2. **Chat ID yanlış:**
   - Bot'una `/start` yaz
   - https://api.telegram.org/bot<BOT_TOKEN>/getUpdates adresine git
   - `"chat":{"id":123456789}` kısmını kopyala

3. **Bot banned:**
   - Yeni bot oluştur (@BotFather)
   - Token'ı güncelle

---

## GitHub Actions Debug Komutları

### Manuel Çalıştırma
```bash
# Actions sekmesinden:
Actions → PROJECT TITAN - Flight Sniper → Run workflow → Run workflow
```

### Logları Terminal'de Görme
```bash
# GitHub CLI kullan
gh run list
gh run view <RUN_ID> --log
```

### Artifact İndirme
```bash
gh run download <RUN_ID>
```

---

## Hızlı Testler

### 1. Python Syntax Kontrolü
```bash
python -m py_compile main.py
python -m py_compile scraper_engine.py
python -m py_compile intel_center.py
python -m py_compile notifier.py
```

### 2. Import Testi
```bash
python -c "from main import ProjectTitan; print('OK')"
python -c "from scraper_engine import ScraperEngine; print('OK')"
python -c "from intel_center import IntelCenter; print('OK')"
python -c "from notifier import TelegramNotifier; print('OK')"
```

### 3. Playwright Testi
```bash
python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
```

### 4. Telegram Testi
```bash
python test_telegram.py
```

---

## Logları Okuma

### titan.log Formatı
```
2026-01-30 18:30:00 - __main__ - INFO - 🦅 TITAN Intelligence Cycle Starting...
2026-01-30 18:30:01 - intel_center - INFO - Parsing RSS feed: https://www.secretflying.com/feed/
2026-01-30 18:30:05 - scraper_engine - INFO - [FAST-FLIGHTS] Scraping IST → JFK
2026-01-30 18:30:10 - scraper_engine - WARNING - [FAST-FLIGHTS] Failed: ...
2026-01-30 18:30:11 - scraper_engine - INFO - [PLAYWRIGHT] Launching stealth browser...
```

**Ne Aramalı:**
- ❌ `ERROR` - Kritik hata
- ⚠️ `WARNING` - Uyarı (normal, fallback devreye girer)
- ✅ `INFO` - Normal işlem

---

## Son Çare: Clean Start

Eğer hiçbir şey çalışmıyorsa:

```bash
# 1. Tüm dosyaları sil
rm -rf *

# 2. Repoyu yeniden clone et (veya dosyaları tekrar indir)

# 3. Virtual environment'ı temiz kur
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
playwright install chromium

# 4. Test et
python test_telegram.py
python main.py
```

---

## İletişim

Hala sorun mu var? Log dosyasını paylaş:
```bash
cat titan.log
```

**En yaygın sorun:** Billing hatası → Repo'yu public yap veya billing ayarını yap!
