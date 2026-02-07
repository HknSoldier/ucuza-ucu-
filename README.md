# 🦅 PROJECT TITAN V2.3 - Enterprise Flight Intelligence System

**Otonom, akıllı ve profesyonel uçuş istihbarat sistemi.**

## ✨ Yeni Özellikler (V2.3)

### 🕒 Ghost Protocol
- **Aktif Saatler:** Hafta içi 09:00-20:00, Hafta sonu 11:00-23:00
- **Mistake Fare Bypass:** %70+ indirim varsa ANINDA bildir (7/24)

### 🛡️ Anti-Spam Koruması
- Max 1 alarm / rota / 24 saat
- Max 3 alarm / gün
- Gerçek fırsatlar için akıllı filtreleme

### 💎 Dip Avcısı (Price Bottom)
- **🔥 DİP:** Fiyat ≤ (En düşük × 1.05) → HEMEN AL
- **🟡 NORMAL:** Fiyat ≤ Ortalama → BEKLE
- **🔴 PAHALI:** Fiyat > Ortalama → ALMA

### 🛂 Yeşil Pasaport Vize Kontrolü
- ✅ Schengen/EU: Vizesiz
- ⚠️ ABD/UK/CA/AU: Vize gerekli uyarısı

### 🔄 Hub Arbitrajı
- Istanbul pahalıysa Sofia/Abu Dhabi alternatifi
- Positioning flight + hub flight = Büyük tasarruf

### 📊 Gelişmiş Analitik
- 90 günlük fiyat geçmişi
- Fiyat elastikiyeti tahmini ("Kaç saat dayanır?")
- Gerçek maliyet hesaplama (bagaj + ulaşım)
- Multi-source validation

### 🛡️ Self-Healing
- Başarı oranı izleme
- Otomatik IP rotation önerisi
- Sistem sağlığı raporları

---

## 🚀 Hızlı Başlangıç

### ✅ Ön Koşullar

**Bot Kimlik Bilgileri:**
- Bot Token: Hazır (config.py'de)
- Admin ID: Hazır (config.py'de)
- Grup ID: Hazır (config.py'de)

**NOT:** Tokenler artık `config.py` içinde hardcoded! GitHub Secrets'a gerek yok.

### 📦 Kurulum (3 Adım)

#### 1️⃣ Dosyaları İndir

```bash
git clone https://github.com/YOUR_USERNAME/PROJECT-TITAN-V2.git
cd PROJECT-TITAN-V2
```

#### 2️⃣ Python Bağımlılıklarını Kur

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

#### 3️⃣ Test Et

```bash
python test_telegram.py
```

Telegram'ınızı kontrol edin - test mesajı geldi mi? ✅

---

## ▶️ Çalıştırma

### Tek Seferlik Test
```bash
python main.py
```

### Sürekli Monitoring (Her 4 Saatte Bir)
`main.py` dosyasındaki son satırı değiştir:
```python
# await titan.run_intelligence_cycle()  # Bunu kapat
await titan.run_forever()  # Bunu aç
```

### GitHub Actions ile Otomatik (Önerilen)
1. **Actions** sekmesi → "I understand my workflows, go ahead and enable them"
2. **Actions** → "PROJECT TITAN V2.3" → **Run workflow**
3. ✅ Her 4 saatte bir otomatik çalışacak!

---

## 📁 Dosya Yapısı

```
PROJECT-TITAN-V2/
├── config.py               # Ana yapılandırma (tokenler burada!)
├── main.py                 # Orkestratör
├── scraper_engine.py       # Gelişmiş scraping motoru
├── intel_center.py         # RSS + rota üreteci + hub arbitraj
├── notifier.py             # Telegram (Ghost Protocol + Anti-Spam)
├── price_analyzer.py       # 🆕 Dip fiyat + elastikiyet analizi
├── visa_checker.py         # 🆕 Yeşil pasaport vize kontrolü
├── requirements.txt        # Python bağımlılıkları
├── test_telegram.py        # Test scripti
├── sniper.yml              # GitHub Actions workflow
└── README.md
```

---

## 🎯 Nasıl Çalışır?

### 1️⃣ RSS Intelligence
- Trend olan destinasyonları tespit et (Secret Flying, Fly4Free, vb.)
- Bu destinasyonlara öncelik ver

### 2️⃣ Rota Üretimi
- **Direkt rotalar:** En yüksek öncelik (gidiş-dönüş, non-stop)
- **Hub arbitraj:** Istanbul pahalıysa SOF/AUH/DOH alternatifleri
- **Hidden city:** (Şimdilik devre dışı - riskli)

### 3️⃣ Akıllı Tarama
- Rastgele tarihler (3-11 ay arası)
- Multi-date sampling (5 tarih kombinasyonu)
- Anti-detection (random delays, user-agent rotation)

### 4️⃣ Gelişmiş Analiz
- ✅ Anomali kontrolü (100 TL - 500K TL arası)
- ✅ Multi-source validation (2+ kaynak)
- ✅ Dip fiyat tespiti (En düşük × 1.05)
- ✅ Mistake fare algılama (%70+ indirim)
- ✅ Vize kontrolü (Yeşil Pasaport)
- ✅ Gerçek maliyet (bagaj + ulaşım)
- ✅ Fiyat elastikiyeti ("6 saat dayanır")

### 5️⃣ Akıllı Bildirim
- **Ghost Protocol:** Sadece aktif saatlerde bildir (Mistake fare bypass)
- **Anti-Spam:** Max 1 alarm/rota/24h, max 3 alarm/gün
- **Alarm Filter:** Sadece gerçek dip fiyatlarda alarm

---

## 🔥 Sofia Hub Hack

Sofia (SOF) üzerinden ABD'ye uçmak çok daha ucuz!

**Örnek:**
- ❌ **IST → JFK:** 30,000 TL
- ✅ **IST → SOF + SOF → JFK:** 1,500 + 10,000 = 11,500 TL

**Tasarruf:** 18,500 TL (% 62!)

---

## 📊 Telegram Mesaj Formatı

```
🦅 PROJECT TITAN – DİP FİYAT ALARMI 💎 | 🔥 MISTAKE FARE

✈️ Rota: SOF ➔ JFK (Direkt)
📅 Tarih: 2026-06-15 ➔ 2026-06-25 (10 Gece)
💰 Fiyat: 9,500 TL (Gerçek Maliyet: 10,200 TL)
🏷️ Havayolu: Turkish Airlines
🎒 Bagaj: Kabin + 1 Bavul Dahil

📊 Analiz:
• 90 Günlük Ortalama: 15,000 TL | Dip Eşik: 10,500 TL
• Tasarruf: %36.7
• ✅ Vize Durumu: VİZE GEREKLİ (B1/B2)

🔗 [✈️ UÇUŞ LİNKİ] | [🏨 OTEL LİNKİ]
⚡ AKSİYON: 🔥 HEMEN AL
⏱️ Tahmini Süre: < 6 saat 🔥
```

---

## ⚙️ Özelleştirme

`config.py` dosyasını düzenleyerek:
- Fiyat eşiklerini değiştir
- Havalimanları ekle/çıkar
- Aktif saatleri ayarla
- Anti-spam limitlerini değiştir
- RSS feedleri güncelle

---

## 🛠️ Sorun Giderme

### ❌ "No module named 'config'"
```bash
# Doğru dizinde olduğunuzdan emin olun
pwd  # PROJECT-TITAN-V2 görünmeli
ls   # config.py görünmeli
```

### ❌ Telegram mesaj gelmiyor
```bash
# Test et
python test_telegram.py

# config.py'deki tokenları kontrol et
# Admin ID doğru mu?
# Bot grup/kanala admin olarak eklendi mi?
```

### ❌ "Playwright browsers not found"
```bash
playwright install chromium
playwright install-deps chromium
```

### ❌ GitHub Actions başarısız
```bash
# Actions → Failed job → Logları incele
# En yaygın hata: Playwright timeout
# Çözüm: workflow timeout'u arttır (45 min)
```

---

## 📈 Performance Metrikleri

Her cycle sonunda sistem otomatik rapor oluşturur:
- Total Routes
- Success Rate
- Avg Scan Time
- Bottom Deals
- Mistake Fares
- Alerts Sent

---

## 🔒 Güvenlik

✅ **Tokenler:** config.py'de (private repo ise güvenli)  
✅ **Rate Limiting:** Max 3 istek / 10 saniye  
✅ **Robots.txt Uyumlu:** TOS compliant  
✅ **Anti-Detection:** User-agent rotation, random delays  
✅ **Self-Healing:** Otomatik IP rotation önerisi  

---

## 🤝 Katkıda Bulunma

Pull request'ler memnuniyetle karşılanır!

**İyileştirme Fikirleri:**
- Daha fazla RSS feed kaynağı
- Alternatif scraping motorları (Kayak, Skyscanner)
- Machine learning fiyat tahmini
- WhatsApp/Discord entegrasyonu

---

## 📄 Lisans

MIT - Özgürce kullan, değiştir, zengin ol! 🚀

---

## 🙏 Teşekkürler

- **Google Flights** - Veri kaynağı
- **Secret Flying** - RSS intelligence
- **Playwright** - Scraping engine
- **Telegram** - Notification platform

---

**Made with 🦅 by TITAN Team**

*Akıllıca uç, ucuza uç! ✈️💎*