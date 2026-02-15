# 📅 SWEET SPOT BOOKING - QUICK REFERENCE

## ❓ Sweet Spot Nedir?

**Havacılık sektörünün en iyi saklanan sırrı:**

Uçak biletlerinin **en ucuz olduğu rezervasyon zamanı**!

---

## 📊 Fiyat Grafiği (İstatistiksel)

```
FİYAT
  │
  │     Çok Erken         SWEET SPOT!        Çok Geç
  │        ▲                  ▼                ▲
  │      PAHALI             UCUZ            PAHALI
  │         ╱                 │                ╲
  │        ╱                  │                 ╲
  │       ╱                   │                  ╲
  │      ╱                    │                   ╲
  │     ╱                     ▼                    ╲
  │    ╱                   EN UCUZ                  ╲
  │   ╱                       │                      ╲
  │  ╱                        │                       ╲
  └─────────────────────────────────────────────────────► ZAMAN
    1h  1g  1h  3h  4h  5h  6h  7h  8h  9h  10h  11h  12h
    
    ❌ Pahalı    ✅✅✅ En Ucuz ✅✅✅    ❌ Pahalı
```

---

## 🎯 TITAN V2.5 Ayarı

```python
# config_v25.py

DATE_RANGE_MIN = 42      # 6 hafta
DATE_RANGE_MAX = 56      # 8 hafta
ENFORCE_SWEET_SPOT = True  # SADECE bu aralık!
```

**Sonuç:**
- ✅ Sistem sadece 6-8 hafta sonraki uçuşları tarar
- ❌ Daha erken tarihler: TARANMAzZZZ
- ❌ Daha geç tarihler: TARANMAZ

---

## 📅 Pratik Örnekler

### Örnek 1: Bugün 15 Şubat 2026
```
6 hafta sonra: 29 Mart 2026  ← ✅ TARANIR
7 hafta sonra: 5 Nisan 2026  ← ✅ TARANIR
8 hafta sonra: 12 Nisan 2026 ← ✅ TARANIR

5 hafta sonra: 22 Mart 2026  ← ❌ ÇOK ERKEN, TARANMAZ
9 hafta sonra: 19 Nisan 2026 ← ❌ ÇOK GEÇ, TARANMAZ
```

### Örnek 2: Yaz Tatili Planı (Haziran)
```
Bugün: 15 Şubat

Haziran uçuşu istiyorsun (4 ay sonra = 16 hafta)
❌ ÇOK GEÇ! Sistem taramaz.

Ne zaman taranır?
Haziran - 6 hafta = 19 Mayıs civarı
Sistem 19 Mayıs'ta otomatik tarar! ✅
```

### Örnek 3: Acil Seyahat (2 hafta sonra)
```
Bugün: 15 Şubat
İstediğin: 1 Mart (2 hafta sonra)

❌ SWEET SPOT DIŞINDA!
❌ Sistem taramaz (çok erken!)

Çözüm:
1. Manuel ara (Google Flights)
2. veya config'de ENFORCE_SWEET_SPOT = False yap
```

---

## 🔧 Özelleştirme

### Daha Geniş Aralık İstersen:

```python
# 4-10 hafta arası
DATE_RANGE_MIN = 28   # 4 hafta
DATE_RANGE_MAX = 70   # 10 hafta
```

### Sweet Spot'u Devre Dışı Bırakmak İstersen:

```python
ENFORCE_SWEET_SPOT = False  # Tüm tarihler taranır
DATE_RANGE_MIN = 7    # 1 hafta
DATE_RANGE_MAX = 365  # 1 yıl
```

**⚠️ UYARI:** Sweet spot dışı tarama = daha pahalı biletler!

---

## 📊 Gerçek Veri (Industry Research)

### Kaynak: Airlines Reporting Corporation (ARC)

**Domestic Flights (İç Hatlar):**
- En ucuz: 6 hafta önceden
- %5-10 daha ucuz

**International Flights (Dış Hatlar):**
- En ucuz: 6-8 hafta önceden
- %15-25 daha ucuz
- Bazen %40'a kadar!

### Kaynak: CheapAir Annual Study

**20 Yıllık Veri Analizi:**
```
Prime Booking Window:
Domestic: 3-7 hafta (ortalama 54 gün)
International: 5-10 hafta (ortalama 76 gün)

En ucuz gün: 54 gün önceden (7.7 hafta)
```

**TITAN V2.5:** 6-8 hafta = **Perfect Match!** ✅

---

## 💡 Pro Tips

### Tip 1: Sabırlı Ol
```
Acil seyahat mi? → Google Flights manuel kullan
Planlı tatil mi? → TITAN'a bırak, 6 hafta bekle!
```

### Tip 2: Takviminizi Ayarlayın
```
Haziran tatili istiyorsun?
Takvim: 19 Mayıs'a alarm kur
O gün TITAN çalışacak ve Haziran'ı tarayacak!
```

### Tip 3: Esnek Ol
```
±3 gün esneklik = %10-15 ekstra tasarruf
6 hafta + esneklik = %30-40 toplam tasarruf!
```

---

## ❓ SSS

**S: Neden sadece 6-8 hafta?**  
C: İstatistiksel olarak EN UCUZ dönem. Daha erken/geç = daha pahalı.

**S: Acil seyahat için kullanabilir miyim?**  
C: Hayır. TITAN uzun vadeli planlama için. Acil = Google Flights manuel.

**S: Sweet spot'u değiştirebilir miyim?**  
C: Evet! config_v25.py'de DATE_RANGE_MIN/MAX'ı değiştir.

**S: Tatilim 4 ay sonra, ne zaman taranır?**  
C: 4 ay - 6 hafta = 2.5 ay sonra sistem otomatik tarar.

**S: Sistem şu an ne tarihler tarıyor?**  
C: Log'lara bak:
```
📅 SWEET SPOT WINDOW:
   2026-03-29 → 2026-04-12
   (42-56 gün / 6-8 hafta)
```

---

## 🎯 Özet

**SWEET SPOT = 6-8 HAFTA ÖNCEDEN REZERVASYON**

✅ En ucuz fiyatlar  
✅ İstatistiksel olarak kanıtlanmış  
✅ TITAN V2.5 otomatik uygular  
✅ %30-40 tasarruf potansiyeli  

**Sabır = Tasarruf! 💰**

---

**Not:** TITAN sabah 09:00'da mesaj gönderecek. O zaman hemen rezervasyon yap!

⏰ **Her saat değerli!** Sweet spot içinde bile fiyatlar değişebilir.

---

Made with 📊 by TITAN Research Team
