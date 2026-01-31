# 🔐 GitHub Secrets Kurulum Kılavuzu

Bu kılavuz, bot tokenlerini **güvenli bir şekilde** GitHub'da saklamak için adım adım talimatlar içerir.

## ⚠️ Neden Gerekli?

Repo **public** olduğu için, bot tokenlerini doğrudan kodda tutamayız. Herkes görebilir! 
GitHub Secrets, tokenlerinizi şifreleyerek sadece Actions'ın erişebileceği şekilde saklar.

---

## 📋 Adım 1: GitHub Repo Ayarlarına Git

1. **GitHub'da** bu repoyu aç: `https://github.com/HknSoldier/ucuza-ucu`
2. Üst menüden **Settings** sekmesine tıkla
3. Sol menüden **Secrets and variables** → **Actions** seç

---

## 🔑 Adım 2: Secret'ları Ekle

### Secret 1: BOT_TOKEN

1. **New repository secret** butonuna tıkla
2. **Name:** `BOT_TOKEN` (tam olarak bu şekilde yaz, büyük harflerle)
3. **Secret:** `8161806410:AAH4tGpW_kCvQpLOfaB-r2OYQMypPVYtuYg`
4. **Add secret** butonuna tıkla

✅ İlk secret eklendi!

---

### Secret 2: ADMIN_ID

1. Tekrar **New repository secret** butonuna tıkla
2. **Name:** `ADMIN_ID`
3. **Secret:** `7684228928`
4. **Add secret** butonuna tıkla

✅ İkinci secret eklendi!

---

### Secret 3: GROUP_ID

1. Son kez **New repository secret** butonuna tıkla
2. **Name:** `GROUP_ID`
3. **Secret:** `-1003515302846`
4. **Add secret** butonuna tıkla

✅ Üçüncü secret eklendi!

---

## ✅ Adım 3: Doğrulama

Secrets sayfasında şimdi **3 secret** görmelisin:

```
Repository secrets
BOT_TOKEN         Updated ... seconds ago
ADMIN_ID          Updated ... seconds ago
GROUP_ID          Updated ... seconds ago
```

**Önemli:** Secret'ların değerlerini bir daha göremezsin (güvenlik nedeniyle). 
Ama değerlerini değiştirebilirsin.

---

## 🚀 Adım 4: GitHub Actions'ı Test Et

1. **Actions** sekmesine git
2. "PROJECT TITAN - Flight Sniper" workflow'unu bul
3. **Run workflow** → **Run workflow** butonuna tıkla
4. 2-3 dakika bekle

### Başarılı ise:

- ✅ Workflow yeşil ✓ olacak
- ✅ Telegram'a "🦅 PROJECT TITAN ONLINE" mesajı gelecek

### Başarısız ise:

- ❌ Workflow kırmızı X olacak
- Actions → Failed job → "Run TITAN" step'ini aç → Hata mesajını oku
- Muhtemelen bir secret yanlış yazılmış

---

## 🔧 Sorun Giderme

### Hata: "BOT_TOKEN not set"

**Neden:** Secret adı yanlış yazılmış veya eklenmemiş.

**Çözüm:**
1. Settings → Secrets → Actions → Secret adlarını kontrol et
2. Tam olarak şöyle olmalı: `BOT_TOKEN`, `ADMIN_ID`, `GROUP_ID` (büyük harflerle)
3. Eğer yanlışsa: Secret'a tıkla → Update → Doğru adı yaz

---

### Hata: "Telegram message failed"

**Neden:** Bot token veya chat ID yanlış.

**Çözüm:**
1. Bot token'ı doğrula:
   - Telegram'da @BotFather'a git
   - `/mybots` → Botunu seç → API Token
   - Token'ı kopyala
   - GitHub → Settings → Secrets → BOT_TOKEN → Update → Yeni token'ı yapıştır

2. Admin ID'yi doğrula:
   - Telegram'da @userinfobot'a mesaj at
   - `Your user ID is: 123456789` diyecek
   - GitHub → Settings → Secrets → ADMIN_ID → Update → ID'yi yapıştır

---

### Hata: Secret'ı değiştirdim ama hala çalışmıyor

**Neden:** Actions eski secret'ı cache'lemiş olabilir.

**Çözüm:**
1. Actions → Failed job → **Re-run all jobs** butonuna tıkla
2. Veya yeni bir commit at:
   ```bash
   git commit --allow-empty -m "Trigger workflow with new secrets"
   git push
   ```

---

## 📱 Yerel Test İçin

GitHub Actions'da çalışıyor ama kendi bilgisayarında test etmek istersen:

### 1. `.env` Dosyası Oluştur

```bash
cp .env.example .env
```

### 2. `.env` Dosyasını Düzenle

```env
BOT_TOKEN=8161806410:AAH4tGpW_kCvQpLOfaB-r2OYQMypPVYtuYg
ADMIN_ID=7684228928
GROUP_ID=-1003515302846
```

### 3. python-dotenv Yükle

```bash
pip install python-dotenv
```

### 4. Test Et

```bash
python test_telegram.py
```

---

## 🎯 Özet

**GitHub Actions için:**
- ✅ Settings → Secrets → 3 secret ekle (BOT_TOKEN, ADMIN_ID, GROUP_ID)
- ✅ Actions → Run workflow → Test et

**Yerel test için:**
- ✅ `.env` dosyası oluştur
- ✅ Tokenlerini `.env`'e yaz
- ✅ `python test_telegram.py`

**Güvenlik:**
- ✅ `.env` dosyası git ignore'da (commit edilmez)
- ✅ GitHub Secrets şifreli (kimse göremez)
- ✅ Public repo'da hiç token yok

---

## ✅ Son Kontrol Listesi

- [ ] GitHub'da 3 secret eklendi
- [ ] Secret isimleri doğru (BOT_TOKEN, ADMIN_ID, GROUP_ID)
- [ ] Actions → Run workflow → Yeşil ✓
- [ ] Telegram'a mesaj geldi
- [ ] Yerel test için `.env` oluşturuldu (opsiyonel)

**Hepsi tamam mı?** 🎉 Tebrikler, PROJECT TITAN güvenli şekilde çalışıyor!

---

**Sorun mu var?** TROUBLESHOOTING.md dosyasına bak veya GitHub Actions logs'una bak.
