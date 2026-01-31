# 🔧 HIZLI DÜZELTme TALİMATLARI

## ❌ Hata: "ModuleNotFoundError: No module named 'intel_center'"

Bu hata, dosyaların GitHub'a tam yüklenmediği anlamına geliyor.

---

## ✅ ÇÖZÜM: Tüm Dosyaları Tekrar Yükle

### ADIM 1: ZIP'i İndir ve Çıkart

`project-titan-complete.zip` dosyasını indir ve çıkart.

### ADIM 2: Eski Dosyaları Sil

```bash
cd ucuza-ucu
rm -rf *
rm -rf .github
```

### ADIM 3: Yeni Dosyaları Yükle

```bash
# ZIP'i çıkart
unzip project-titan-complete.zip

# Dosyaları kontrol et
ls -la
# Görmelisin: main.py, scraper_engine.py, intel_center.py, notifier.py, vb.

# .github klasörünü kontrol et
ls -la .github/workflows/
# Görmelisin: sniper.yml
```

### ADIM 4: GitHub'a Push Et

```bash
git add .
git commit -m "🔧 Fix: Complete file upload with all modules"
git push
```

---

## ✅ ADIM 5: GitHub Secrets'ı Kontrol Et

**ÖNEMLİ:** Tokenlerinizi GitHub Secrets'a eklemediniz!

Settings → Secrets → Actions → Bu 3 secret olmalı:

- `BOT_TOKEN` (kendi bot tokeniniz)
- `ADMIN_ID` (kendi user ID'niz)
- `GROUP_ID` (kendi group ID'niz)

**Nasıl alınır:** `SETUP_SECRETS.md` dosyasına bakın.

---

## ✅ ADIM 6: Test Et

```bash
# Actions sekmesi → "PROJECT TITAN - Flight Sniper" → Run workflow

# 2-3 dakika bekle

# Başarılı ise:
# ✅ Workflow yeşil ✓
# ✅ Telegram'a mesaj gelecek
```

---

## 🎯 DOSYA LİSTESİ (Hepsi Olmalı!)

```
ucuza-ucu/
├── main.py                    ✓
├── scraper_engine.py          ✓
├── intel_center.py            ✓
├── notifier.py                ✓
├── config.py                  ✓
├── test_telegram.py           ✓
├── requirements.txt           ✓
├── run.sh                     ✓
├── .env.example               ✓
├── .gitignore                 ✓
├── README.md                  ✓
├── INSTALL.md                 ✓
├── SETUP_SECRETS.md           ✓
├── TROUBLESHOOTING.md         ✓
└── .github/
    └── workflows/
        └── sniper.yml         ✓
```

---

## 🚨 YAYGIN HATALAR

### "ModuleNotFoundError: No module named 'intel_center'"

**Çözüm:** ZIP'ten tüm dosyaları tekrar yükle

### "BOT_TOKEN not set"

**Çözüm:** GitHub Secrets ekle (SETUP_SECRETS.md'ye bak)

### "Telegram message failed"

**Çözüm:** Bot token ve ID'leri kontrol et

---

## ✅ SON KONTROL

```bash
# Tüm Python dosyaları var mı?
ls -la *.py

# Workflow dosyası var mı?
ls -la .github/workflows/sniper.yml

# GitHub Secrets eklendi mi?
Settings → Secrets → 3 secret kontrol et
```

---

## 🎉 BAŞARILI OLUNCA

```
✅ GitHub'da 14 dosya var
✅ GitHub Secrets'ta 3 secret var
✅ Actions → Run workflow → Yeşil ✓
✅ Telegram'a mesaj geldi
```
