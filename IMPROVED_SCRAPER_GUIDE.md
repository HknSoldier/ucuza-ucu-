# 🎯 İYİLEŞTİRİLMİŞ GOOGLE FLIGHTS SCRAPER KULLANIM KILAVUZU

## ✅ NE DEĞİŞTİ?

### **Önceki Sorun:**
```
ERROR: scraper_engine: Both scraping methods failed
WARNING: Could not extract price from page
```

### **Yeni Çözüm:**
- ✅ **İnsan benzeri davranış**: Rastgele mouse hareketleri, scroll, gecikmeler
- ✅ **Gelişmiş anti-detection**: WebDriver flag kaldırıldı, fingerprint maskelendi
- ✅ **Çoklu strateji**: 3 farklı fiyat çıkarma yöntemi
- ✅ **Daha iyi selector'lar**: Google Flights'ın güncel DOM yapısına uygun
- ✅ **Debug modu**: Screenshot alıyor, ne gördüğünü gösteriyor

---

## 🚀 NASIL ÇALIŞIYOR?

### **1. Otomatik Tarih Üretimi**

Bot her 4 saatte bir çalıştığında:
- ✅ **Tüm yılı** tarar (3-11 ay arası)
- ✅ Her rota için **5 farklı tarih** kombinasyonu dener
- ✅ Rastgele gün ve dönüş tarihleri seçer

**Örnek:**
```
Rota: IST → JFK
Tarih 1: 2026-05-15 → 2026-05-22 (7 gün)
Tarih 2: 2026-08-03 → 2026-08-10 (7 gün)
Tarih 3: 2026-11-20 → 2026-11-27 (7 gün)
Tarih 4: 2026-03-10 → 2026-03-17 (7 gün)
Tarih 5: 2026-09-25 → 2026-10-05 (10 gün)
```

### **2. Çoklu Rota Taraması**

Her çalıştırmada:
- ✅ **RSS feedlerden** trend destinasyonları alır
- ✅ **7 origin** (IST, SAW, ADB, ESB, AYT, TZX, **SOF**)
- ✅ **30+ destination** (JFK, LAX, LHR, CDG, DXB...)
- ✅ Toplamda **~25 rota** taranır

**Örnek Rotalar:**
```
IST → JFK (New York)
IST → LAX (Los Angeles)
SOF → JFK (Sofia hack!)
SAW → LHR (Londra)
ADB → CDG (Paris)
```

### **3. Akıllı Bildirim**

Fiyat bulunca:
- ✅ **Eşik kontrolü**: SOF → JFK için 10,000 TL, IST → JFK için 30,000 TL
- ✅ **Fiyat geçmişi**: Önceki fiyatlarla karşılaştırır
- ✅ **Green Zone**: Ortalama fiyatın %20 altındaysa 🔥
- ✅ **Telegram'a gönder**: Sadece gerçek fırsatları bildirir

---

## 📊 GÜNLÜK TARAMA HESABI

```
Her 4 saatte bir çalışır (günde 6 kez)

Bir tarama:
├─ 25 rota
├─ Her rota için 5 tarih kombinasyonu
├─ Toplam: 125 arama
└─ Süre: ~3-5 dakika

Günlük:
├─ 6 çalışma × 125 arama = 750 arama
├─ Aylık: ~22,500 arama
└─ GitHub Actions: SINIRSIZ (ücretsiz!)
```

---

## 🔍 YENİ SCRAPER ÖZELLİKLERİ

### **1. İnsan Benzeri Davranış**
```python
# Rastgele gecikme
await self._human_like_delay(2, 4)

# Rastgele viewport
viewport = random.choice([
    {'width': 1920, 'height': 1080},
    {'width': 1366, 'height': 768},
])

# Rastgele User-Agent
user_agent = random.choice([
    'Chrome/122.0...',
    'Firefox/123.0...',
    'Safari/17.2...'
])
```

### **2. Gelişmiş Anti-Detection**
```javascript
// WebDriver flag kaldır
Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined
});

// Plugin'leri maskele
Object.defineProperty(navigator, 'plugins', {
    get: () => [1, 2, 3, 4, 5]
});

// Diller
Object.defineProperty(navigator, 'languages', {
    get: () => ['tr-TR', 'tr', 'en-US']
});
```

### **3. Çoklu Fiyat Çıkarma Stratejisi**

**Strateji 1: aria-label**
```python
# Google Flights fiyatları aria-label'da saklar
<span aria-label="25.060 Türk Lirası">₺25.060</span>
```

**Strateji 2: Text content**
```python
# Sayfadaki tüm metni tara
"₺25.060" → 25060 TL
```

**Strateji 3: Regex (son çare)**
```python
# Tüm sayıları + ₺ sembolü
(\d{1,3}(?:\.\d{3})*)\s*₺
```

---

## 🎯 KULLANIM

### **Yerel Test:**
```bash
# 1. Dosyaları güncelle
cd ucuza-ucu
rm scraper_engine.py
# Yeni scraper_engine.py'yi kopyala

# 2. Test et
python main.py

# 3. Logları izle
tail -f titan.log
```

### **GitHub Actions:**
```bash
# 1. Dosyaları push et
git add scraper_engine.py
git commit -m "🚀 Improved: Advanced Google Flights scraper"
git push

# 2. Test çalıştır
GitHub → Actions → Run workflow

# 3. Logları kontrol et
Actions → Run TITAN → Detayları aç
```

---

## 📱 TELEGRAM BİLDİRİMİ ÖRNEĞİ

```
🦅 PROJECT TITAN ALERT 🔥 GREEN ZONE | 📉 PRICE DROP

Route: SOF → JFK
Price: 9,500 TRY
Dates: 2026-06-15 → 2026-06-25
Airline: Turkish Airlines

📊 Analysis:
• Average Price: 15,000 TL
• Threshold: 10,000 TL
• Savings: 36.7%

🔗 View Flights on Google
🏨 Find Hotels

Scanned by google-flights engine
```

---

## 🔧 SORUN GİDERME

### **Hala "Could not extract price" hatası alıyorsan:**

**1. Playwright'ın güncel olduğundan emin ol:**
```bash
playwright install chromium --force
```

**2. Debug screenshot'ları kontrol et:**
```bash
# main.py çalıştırınca debug_*.png dosyaları oluşur
ls -la debug_*.png

# Screenshot'a bak, Google'ın ne gösterdiğini gör
```

**3. URL'yi manuel test et:**
```python
# Log'dan URL'yi kopyala
# Tarayıcıda aç, fiyatlar görünüyor mu?
```

**4. Daha uzun bekleme süresi:**
```python
# scraper_engine.py içinde:
await self._human_like_delay(5, 8)  # 3,5 yerine 5,8
```

---

## ✅ BAŞARI KRİTERLERİ

```
✅ "Found X prices, cheapest: Y TL" log'u
✅ Telegram'a bildirim geldi
✅ titan_state.json oluştu
✅ Fiyat geçmişi kaydediliyor
✅ Her 4 saatte bir otomatik tarama
```

---

## 🎉 SONUÇ

**Artık bot:**
- ✅ **Tüm yılı** tarar (3-11 ay arası)
- ✅ **Google Flights**'tan gerçek fiyatları çeker
- ✅ **İnsan gibi** davranır (bot detection bypass)
- ✅ **En ucuz biletleri** bulur
- ✅ **Telegram**'a bildirir
- ✅ **Sınırsız** çalışır (GitHub Actions ücretsiz)

**İyi avlar! 🦅✈️💰**
