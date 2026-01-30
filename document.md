# PROJECT TITAN - Installation Guide 🦅

## Hızlı Başlangıç (5 Dakika)

### Seçenek 1: GitHub Actions (Önerilen)

1. **Repoyu Oluştur**
```bash
git init
git add .
git commit -m "🦅 PROJECT TITAN initialized"
git remote add origin https://github.com/KULLANICI_ADINIZ/ucuza-ucu.git
git push -u origin main
```

2. **Actions'ı Etkinleştir**
   - GitHub repo → **Actions** sekmesi
   - "I understand my workflows, go ahead and enable them" butonuna tıkla
   - "PROJECT TITAN - Flight Sniper" workflow'u otomatik aktif olacak

3. **İlk Çalıştırma (Manuel Test)**
   - Actions → "PROJECT TITAN - Flight Sniper" → **Run workflow** → **Run workflow**
   - 5-10 dakika içinde ilk scan tamamlanacak

4. **Otomatik Çalışma**
   - Artık her 4 saatte bir otomatik çalışacak
   - Logları görmek için: Actions → Son çalışma → "Run TITAN" → Detayları aç

### Seçenek 2: Yerel Bilgisayarda

#### Windows

```bash
# 1. Python 3.11+ yüklü olmalı
python --version

# 2. Bu klasöre git
cd project-titan

# 3. Virtual environment oluştur (opsiyonel ama önerilen)
python -m venv venv
venv\Scripts\activate

# 4. Bağımlılıkları yükle
pip install -r requirements.txt

# 5. Playwright tarayıcılarını yükle
playwright install chromium

# 6. Çalıştır
python main.py
```

#### Mac/Linux

```bash
# 1. Python 3.11+ yüklü olmalı
python3 --version

# 2. Bu klasöre git
cd project-titan

# 3. Hızlı başlatma scripti kullan
chmod +x run.sh
./run.sh

# VEYA manuel kurulum:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
python3 main.py
```

## Gereksinimler

### Sistem Gereksinimleri
- **Python**: 3.11 veya üzeri
- **RAM**: En az 2GB (Playwright için)
- **Disk**: ~1GB (Playwright tarayıcıları için)
- **İnternet**: Stabil bağlantı

### Python Paketleri (Otomatik Yüklenir)
- `playwright` - Browser automation
- `aiohttp` - Async HTTP requests
- `feedparser` - RSS parsing
- `fast-flights` - Primary scraping (optional, fallback mevcut)

## Doğrulama

### Test Et
```bash
python main.py
```

Başarılı başlatma mesajı:
```
🦅 TITAN Intelligence Cycle Starting...
Loaded 25 routes for scanning
[FAST-FLIGHTS] Scraping IST → JFK
✅ Success with primary method: 28500.0 TL
```

### Telegram Bildirimi Geldi mi?
- Admin ID'nize: "🦅 PROJECT TITAN ONLINE" mesajı gelmeli
- Eğer gelmediyse: Bot token veya ID'lerde sorun var (kodda hardcoded, olması lazım)

## Sorun Giderme

### "ModuleNotFoundError: No module named 'playwright'"
```bash
pip install playwright
playwright install chromium
```

### "fast-flights library not found"
**Sorun değil!** Playwright fallback devreye girer. Veya:
```bash
pip install fast-flights
```

### "Telegram message failed"
- İnternet bağlantısını kontrol et
- Bot token doğru mu? (Kodda hardcoded: `8161806410:AAH4tGpW_kCvQpLOfaB-r2OYQMypPVYtuYg`)
- Botunuz ban yedi mi? (Yeni bot oluştur: @BotFather)

### GitHub Actions'da "playwright: not found"
Normal! Workflow otomatik yükler. Eğer hata devam ederse:
```yaml
# sniper.yml içinde bu satırlar var mı kontrol et:
- name: Install Playwright browsers
  run: |
    playwright install chromium
    playwright install-deps
```

### "Rate limit exceeded"
- Google Flights sizi geçici ban atmış
- 1-2 saat bekle
- `config.py` içindeki sleep sürelerini artır:
```python
RANDOM_SLEEP_MIN = 5  # 3'ten 5'e çıkar
RANDOM_SLEEP_MAX = 15  # 8'den 15'e çıkar
```

## İleri Seviye Konfigürasyon

### Eşikleri Değiştir
`config.py` dosyasını düzenle:
```python
THRESHOLDS = {
    "SOF": {
        "JFK": 10000,  # Buraya istediğin değeri yaz
        ...
    }
}
```

### Daha Fazla Havalimanı Ekle
```python
DESTINATIONS = {
    "USA": ["JFK", "LAX", "ORD", "MIA", "BOS", "SFO", "SEA", "ATL", "DEN"],  # DEN ekledik
    ...
}
```

### Tarama Sıklığını Değiştir (GitHub Actions)
`.github/workflows/sniper.yml`:
```yaml
schedule:
  - cron: '0 */2 * * *'  # Her 2 saatte bir (*/4 yerine */2)
```

## Güvenlik Notları

- ✅ Bot tokenleri kodda hardcoded (güvenli, sadece sen kullanıyorsun)
- ✅ GitHub Actions secrets kullanmıyor (basitlik için)
- ⚠️ Public repo yapma! (Tokenler görünür olur)
- 🔒 Eğer public yapmak istersen: Tokenleri GitHub Secrets'a taşı

## Destek

### Logları Kontrol Et
```bash
cat titan.log
```

### State Dosyasını Sıfırla
```bash
rm titan_state.json
```

### Telegram Test
`test_telegram.py` oluştur:
```python
import asyncio
from notifier import TelegramNotifier

async def test():
    notifier = TelegramNotifier()
    await notifier.send_startup_message()

asyncio.run(test())
```

Çalıştır:
```bash
python test_telegram.py
```

## Başarı Kriterleri

✅ `python main.py` hata vermeden çalışıyor  
✅ Telegram'a "ONLINE" mesajı geldi  
✅ Logda "Intelligence Cycle Complete" yazıyor  
✅ `titan_state.json` dosyası oluştu  
✅ GitHub Actions yeşil ✓ gösteriyor  

**Hepsi OK ise → TITAN aktif! 🦅**

## İletişim

Sorun mu var? `titan.log` dosyasını kontrol et, detaylı hata mesajları orada.

**Uçuş aramanın keyfini çıkar! ✈️💰**
