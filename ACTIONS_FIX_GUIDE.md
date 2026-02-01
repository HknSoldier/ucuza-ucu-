# 🔧 ACTIONS ÇALIŞMIYOR - HIZLI ÇÖZÜM

## ❌ SORUN

Actions sekmesinde "PROJECT TITAN - Flight Sniper" workflow'u göz görünmüyor veya çalıştırılamıyor.

---

## ✅ ÇÖZÜM (3 ADIM)

### **ADIM 1: Dosya Yapısını Kontrol Et**

Terminal'de:
```bash
cd ucuza-ucu

# .github/workflows klasörü var mı?
ls -la .github/workflows/

# Çıktı şöyle olmalı:
# sniper.yml
# test.yml
```

**Eğer klasör yoksa:**
```bash
mkdir -p .github/workflows
# sniper.yml ve test.yml dosyalarını buraya kopyala
```

---

### **ADIM 2: Dosyaları GitHub'a Yükle**

```bash
# Tüm dosyaları ekle
git add .

# Commit
git commit -m "fix: Add GitHub Actions workflows"

# Push
git push
```

**VEYA GitHub Web Arayüzünde:**
1. Repo'da → **Add file** → **Create new file**
2. Dosya adı: `.github/workflows/sniper.yml`
3. İçeriği yapıştır (aşağıda)
4. **Commit changes**

---

### **ADIM 3: Actions'ı Etkinleştir**

1. GitHub repo → **Actions** sekmesi
2. Yeşil buton: **"I understand my workflows, go ahead and enable them"**
3. Tıkla!

---

## 📁 WORKFLOW DOSYASI (KOPYALA-YAPIŞTIR)

Eğer sniper.yml eksikse, bu içeriği kullan:

```yaml
name: PROJECT TITAN - Flight Sniper

on:
  schedule:
    - cron: '0 */4 * * *'
  workflow_dispatch:
  push:
    branches:
      - main

jobs:
  hunt:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
        cache: 'pip'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Install Playwright browsers
      run: |
        playwright install chromium
        playwright install-deps chromium
    
    - name: Verify installation
      run: |
        python --version
        pip list | grep -E "playwright|aiohttp|feedparser"
        python -c "import playwright; print('✓ Playwright OK')"
    
    - name: Run TITAN
      run: |
        python main.py
      env:
        BOT_TOKEN: ${{ secrets.BOT_TOKEN }}
        ADMIN_ID: ${{ secrets.ADMIN_ID }}
        GROUP_ID: ${{ secrets.GROUP_ID }}
        PYTHONUNBUFFERED: 1
    
    - name: Upload logs
      if: always()
      uses: actions/upload-artifact@v4
      with:
        name: titan-logs-${{ github.run_number }}
        path: |
          titan.log
          titan_state.json
        retention-days: 7
        if-no-files-found: warn
```

---

## 🎯 HIZLI TEST

En basit yöntem: **Test workflow'unu kullan**

1. **Dosya oluştur:** `.github/workflows/test.yml`

```yaml
name: TEST - TITAN Status Check

on:
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout
      uses: actions/checkout@v4
    
    - name: Check files
      run: |
        echo "✓ Files in repo:"
        ls -la
        echo ""
        echo "✓ Python files:"
        ls *.py
    
    - name: Done
      run: echo "✅ TEST COMPLETE"
```

2. **GitHub'a yükle**
3. **Actions → TEST - TITAN Status Check → Run workflow**

Eğer bu çalışırsa, ana workflow da çalışacak!

---

## 🔍 SORUN GİDERME

### **Workflow görünmüyor:**
```bash
# 1. Dosya yolunu kontrol et
cat .github/workflows/sniper.yml
# Hata alırsan dosya yok demektir!

# 2. Dosyayı oluştur
mkdir -p .github/workflows
# sniper.yml içeriğini yapıştır

# 3. Push et
git add .github/workflows/
git commit -m "add: GitHub Actions workflows"
git push
```

### **"Enable workflows" butonu yok:**
- Actions zaten aktif demektir
- Workflow'lar listede görünmeli

### **Workflow çalışmıyor:**
```bash
# GitHub Secrets kontrol et
Settings → Secrets → Actions

# Şunlar olmalı:
BOT_TOKEN
ADMIN_ID  
GROUP_ID
```

---

## ✅ BAŞARI KONTROLÜ

Actions sekmesinde göreceksin:

```
All workflows
├─ PROJECT TITAN - Flight Sniper  ← Ana workflow
└─ TEST - TITAN Status Check      ← Test workflow

Her birinde:
└─ [Run workflow] butonu olmalı
```

**Run workflow'a** tıklayınca:
```
1. Yeşil "Running" işareti
2. 2-3 dakika sonra yeşil ✓ veya kırmızı ✗
3. Logları görebilirsin
```

---

## 🚀 SONUÇ

**Problem:** Workflow dosyası yok veya yanlış yerde  
**Çözüm:** `.github/workflows/sniper.yml` oluştur ve push et  
**Test:** Actions → Run workflow → Logları kontrol et  

**Şimdi yapman gereken:**
1. ✅ `.github/workflows/` klasörünü oluştur
2. ✅ `sniper.yml` dosyasını ekle
3. ✅ GitHub'a push et
4. ✅ Actions → Enable workflows
5. ✅ Run workflow → Test et
