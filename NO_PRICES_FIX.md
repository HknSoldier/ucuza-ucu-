# 🔧 "NO PRICES FOUND" SORUNU - ÇÖZÜM

## ❌ SORUN

Log'da sürekli:
```
⚠️ No prices found
```

**Neden:**  
Google Flights'tan fiyatları çıkaramıyor (selector'lar eski/yanlış)

---

## ✅ ÇÖZÜM: YENİ SCRAPER

### **ÖNCEKİ SCRAPER:**
- 2 strateji
- Kısa bekleme süresi (2-3 saniye)
- Basit selector'lar

### **YENİ SCRAPER:**
- **4 farklı strateji** (daha agresif!)
- **Uzun bekleme** (8 saniye + scroll)
- **Screenshot** kaydediyor (debug için)
- **Regex ile tüm sayfa** taranıyor

---

## 🚀 KURULUM (2 DAKİKA)

### **YÖNTEM 1: Dosyayı Değiştir**

1. **Yeni `scraper_engine.py` dosyasını indir** (yukarıda)

2. **GitHub'da değiştir:**
   ```bash
   Repo → scraper_engine.py → Edit (kalem ikonu) → İçeriği sil → Yeni kodu yapıştır → Commit
   ```

3. **VEYA Terminal'de:**
   ```bash
   cd ucuza-ucu
   # Yeni scraper_engine.py dosyasını kopyala
   git add scraper_engine.py
   git commit -m "fix: Ultra improved scraper with 4 strategies"
   git push
   ```

---

## 🔍 YENİ ÖZELLİKLER

### **1. Daha Uzun Bekleme**
```python
# Önceki: 2-3 saniye
await asyncio.sleep(3)

# Yeni: 8 saniye + scroll
await asyncio.sleep(8)
await page.evaluate("window.scrollTo(0, 500)")  # Lazy loading tetikle
```

### **2. 4 Farklı Strateji**

**Strateji 1: ₺ sembolü ile regex**
```python
pattern = r'(\d{1,3}(?:\.\d{3})*)\s*₺'
# Örnek: "25.060 ₺" → 25060
```

**Strateji 2: TL/TRY suffix**
```python
pattern = r'(\d{1,3}(?:\.\d{3})*)\s*(?:TL|TRY)'
# Örnek: "25.060 TL" → 25060
```

**Strateji 3: aria-label attribute**
```python
# Google Flights fiyatları aria-label'da saklar
<span aria-label="25.060 Türk Lirası">
```

**Strateji 4: Tüm div'leri tara**
```python
# Tüm fiyat div'lerini bul
div[jsname], div[data-test-id*="price"], span[data-gs]
```

### **3. Screenshot Debug**
```python
# Her tarama için screenshot kaydet
screenshot_name = f"debug_{origin}_{destination}.png"
await page.screenshot(path=screenshot_name, full_page=True)
```

**Kullanımı:**
```bash
# GitHub Actions artifact'ında göreceksin
Actions → Run → Artifacts → Download
# debug_IST_JFK.png dosyasını aç
# Google'ın ne gösterdiğini gör!
```

---

## 📊 BEKLENEN ÇIKTI

### **Önceki Log:**
```
🔍 [SCRAPER] SOF → BER (2026-07-27 to 2026-07-31)
⚠️ No prices found
```

### **Yeni Log:**
```
🔍 [SCRAPER] SOF → BER (2026-07-27 to 2026-07-31)
📍 Navigating to Google Flights...
⏳ Waiting for prices to load...
📸 Screenshot saved: debug_SOF_BER.png
💰 Found price (₺): 12,450 TL
💰 Found price (TL): 15,300 TL
💰 Found price (aria): 18,900 TL
✅ SUCCESS! Found 8 unique prices, cheapest: 12,450 TL
```

---

## 🎯 TEST

### **Yerel Test:**
```bash
cd ucuza-ucu

# Yeni scraper'ı çalıştır
python main.py

# Log'u izle
tail -f titan.log

# Göreceksin:
# ✅ SUCCESS! Found X prices, cheapest: Y TL
# 📸 Screenshot saved: debug_*.png
```

### **GitHub Actions Test:**
```bash
# Push yap
git push

# Actions otomatik çalışacak
# Veya manuel:
Actions → Run workflow

# Log'da:
✅ SUCCESS! Found prices
```

---

## 🔧 SORUN GİDERME

### **Hala "No prices found":**

**1. Screenshot'ları kontrol et:**
```bash
# GitHub Actions → Artifacts → Download
# debug_*.png dosyalarına bak
# Google Flights açılıyor mu?
# Fiyatlar görünüyor mu?
```

**2. URL'yi manuel test et:**
```bash
# Log'dan URL'yi kopyala:
https://www.google.com/travel/flights?q=Flights%20to%20JFK%20from%20IST...

# Tarayıcıda aç
# Fiyatlar görünüyor mu?
```

**3. Bekleme süresini daha da artır:**
```python
# scraper_engine.py, satır ~75:
await asyncio.sleep(12)  # 8'den 12'ye
```

**4. Headless'ı kapat (yerel test için):**
```python
# scraper_engine.py, satır ~30:
browser = await p.chromium.launch(
    headless=False,  # True yerine False
    ...
)
```

---

## ✅ BAŞARI KRİTERLERİ

```
✅ Log'da: "✅ SUCCESS! Found X prices"
✅ Fiyat: 10,000-50,000 TL aralığında
✅ Screenshot'ta Google Flights görünüyor
✅ Telegram'a bildirim gidiyor
```

---

## 📝 ÖZET

**Yapman gereken:**
1. ✅ Yeni `scraper_engine.py` dosyasını GitHub'a yükle
2. ✅ Actions → Run workflow
3. ✅ Log'u kontrol et: "SUCCESS! Found prices"
4. ✅ Screenshot'ları indir ve kontrol et

**Eğer hala bulamazsa:**
- Screenshot'ları kontrol et
- URL'yi manuel test et
- Bekleme süresini artır (12 saniye)

**Şimdi çalışmalı! 🚀**
