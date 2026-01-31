# 🔐 GitHub Secrets Kurulum Kılavuzu

Bu kılavuz, bot tokenlerini **güvenli bir şekilde** GitHub'da saklamak için adım adım talimatlar içerir.

## ⚠️ Neden Gerekli?

Repo **public** olduğu için, bot tokenlerini doğrudan kodda tutamayız. Herkes görebilir! 
GitHub Secrets, tokenlerinizi şifreleyerek sadece Actions'ın erişebileceği şekilde saklar.

---

## 📋 Adım 1: Telegram Bot Bilgilerini Al

### 1.1: Bot Token Al

1. Telegram'da **@BotFather** ara ve başlat
2. `/newbot` komutunu gönder
3. Bot için bir isim seç (örn: "Flight Sniper Bot")
4. Bot için bir kullanıcı adı seç (örn: "MyFlightSniperBot")
5. BotFather sana bir **token** verecek:
   ```
   1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   ```
6. Bu token'ı **kopyala ve güvenli bir yere kaydet**

### 1.2: Admin ID Al

1. Telegram'da **@userinfobot** ara ve başlat
2. Bot sana user ID'ni verecek:
   ```
   Your user ID is: 123456789
   ```
3. Bu sayıyı **kopyala**

### 1.3: Group ID Al (Opsiyonel)

Eğer gruba da bildirim göndermek istiyorsan:

1. Bir Telegram grubu oluştur
2. Botunu gruba ekle (admin yap)
3. Tarayıcıda şu URL'i aç (BOT_TOKEN yerine kendi tokenini yaz):
   ```
   https://api.telegram.org/bot<BOT_TOKEN>/getUpdates
   ```
4. JSON'da şunu ara:
   ```json
   "chat":{"id":-1001234567890, ...}
   ```
5. Negatif sayıyı **kopyala** (örn: -1001234567890)

**Sadece kendine bildirim istiyorsan:** Group ID'yi ADMIN_ID ile aynı yap.

---

## 📋 Adım 2: GitHub Secrets Ekle

1. **GitHub'da** bu repoyu aç
2. Üst menüden **Settings** sekmesine tıkla
3. Sol menüden **Secrets and variables** → **Actions** seç
4. **New repository secret** butonuna tıkla

### Secret 1: BOT_TOKEN

- **Name:** `BOT_TOKEN` (tam olarak bu şekilde, büyük harflerle)
- **Secret:** (BotFather'dan aldığın token)
- **Add secret** → Tıkla

### Secret 2: ADMIN_ID

- **Name:** `ADMIN_ID`
- **Secret:** (userinfobot'tan aldığın ID)
- **Add secret** → Tıkla

### Secret 3: GROUP_ID

- **Name:** `GROUP_ID`
- **Secret:** (getUpdates'ten aldığın group ID, veya sadece kendine göndermek için ADMIN_ID'yi tekrar yaz)
- **Add secret** → Tıkla

---

## ✅ Adım 3: Doğrulama

Secrets sayfasında şimdi **3 secret** görmelisin:

```
Repository secrets
BOT_TOKEN         Updated ... seconds ago
ADMIN_ID          Updated ... seconds ago
GROUP_ID          Updated ... seconds ago
```

---

## 🚀 Adım 4: Test Et

1. **Actions** sekmesine git
2. "PROJECT TITAN - Flight Sniper" workflow'unu bul
3. **Run workflow** → **Run workflow** butonuna tıkla
4. 2-3 dakika bekle

### Başarılı ise:

- ✅ Workflow yeşil ✓ olacak
- ✅ Telegram'a "🦅 PROJECT TITAN ONLINE" mesajı gelecek

### Başarısız ise:

- ❌ Actions → Failed job → "Run TITAN" step'ini aç
- Hata mesajını oku
- Muhtemelen bir secret yanlış

---

## 🔧 Sorun Giderme

### "BOT_TOKEN not set"

**Çözüm:** Secret adı tam olarak `BOT_TOKEN` olmalı (büyük harflerle, alt çizgi ile)

### "Telegram message failed"

**Çözüm:** 
- Bot token'ı kontrol et (@BotFather → /mybots → API Token)
- Admin ID'yi kontrol et (@userinfobot)
- Botu gruba ekle ve admin yap

### Secret'ı değiştirdim ama hala çalışmıyor

**Çözüm:** Actions → Failed job → **Re-run all jobs**

---

## 📱 Yerel Test İçin

Kendi bilgisayarında test etmek için:

```bash
# .env dosyası oluştur
cp .env.example .env

# .env dosyasını düzenle, tokenlerini yaz
nano .env  # veya notepad .env

# Test et
pip install python-dotenv
python test_telegram.py
```

---

## 🎯 Özet

1. ✅ @BotFather → Bot oluştur → Token al
2. ✅ @userinfobot → User ID al
3. ✅ GitHub → Settings → Secrets → 3 secret ekle
4. ✅ Actions → Run workflow → Test et

**Tokenlerini kimseyle paylaşma!** 🔒
