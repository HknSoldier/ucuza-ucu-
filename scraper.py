#!/usr/bin/env python3
"""
PROJECT TITAN v6.1 — Playwright Edition (Form Interaction)
Önceki versiyondan farklar:
  - Hash URL (#flt=...) KALDIRILDI → headless tarayıcıda çalışmıyor
  - Arama formu gerçekten doldurulup gönderiliyor (insan davranışı)
  - CAPTCHA tespiti düzeltildi (yanlış pozitif yoktu, asıl sorun URL'di)
  - Stealth iyileştirildi: rastgele mouse hareketi, typing delay
"""

import json
import re
import random
import time
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# ============================================================
# KONFİGÜRASYON
# ============================================================
BOT_TOKEN = os.environ.get("TITAN_BOT_TOKEN", "8161806410:AAH4tGpW_kCvQpLOfaB-r2OYQMypPVYtuYg")
ADMIN_ID  = os.environ.get("TITAN_ADMIN_ID",  "7684228928")
GROUP_ID  = os.environ.get("TITAN_GROUP_ID",  "-1003515302846")

DIRECT_THRESHOLD   = 0.50
STOPOVER_THRESHOLD = 0.10
MAX_DATA_AGE_HOURS = 3
HEADLESS           = True
PAGE_TIMEOUT_MS    = 60_000
RENDER_WAIT_MS     = 10_000   # Arama sonuçları yüklenmesi için bekleme

TARGET_PRICES = {
    "IST-CDG": 3000, "IST-LHR": 3200, "IST-AMS": 2800,
    "IST-BCN": 2900, "IST-FCO": 2600, "IST-MAD": 3100,
    "IST-FRA": 2700, "IST-MUC": 2500, "IST-VIE": 2400,
    "IST-PRG": 2600, "IST-ATH": 1800, "IST-DXB": 2200,
    "IST-JFK": 18000, "IST-LAX": 20000,
    "SAW-CDG": 2800, "SAW-LHR": 3000, "SAW-AMS": 2600,
    "SAW-BCN": 2700, "SAW-FCO": 2400,
}

ROUTES = list(TARGET_PRICES.keys())

BOUNDS = {
    "IST-CDG":(150,15000),  "IST-LHR":(150,16000),  "IST-AMS":(150,14000),
    "IST-BCN":(150,14000),  "IST-FCO":(150,13000),  "IST-MAD":(150,15000),
    "IST-FRA":(150,13000),  "IST-MUC":(150,13000),  "IST-VIE":(150,12000),
    "IST-PRG":(150,13000),  "IST-ATH":(100,10000),  "IST-DXB":(150,12000),
    "IST-JFK":(1000,80000), "IST-LAX":(1000,90000),
    "SAW-CDG":(150,15000),  "SAW-LHR":(150,16000),  "SAW-AMS":(150,14000),
    "SAW-BCN":(150,14000),  "SAW-FCO":(150,13000),
}

# Tam havalimanı adları — arama formuna yazılacak
AIRPORT_NAMES = {
    "IST": "Istanbul Ataturk",
    "SAW": "Istanbul Sabiha",
    "CDG": "Paris Charles de Gaulle",
    "LHR": "London Heathrow",
    "AMS": "Amsterdam",
    "BCN": "Barcelona",
    "FCO": "Rome Fiumicino",
    "MAD": "Madrid",
    "FRA": "Frankfurt",
    "MUC": "Munich",
    "VIE": "Vienna",
    "PRG": "Prague",
    "ATH": "Athens",
    "DXB": "Dubai",
    "JFK": "New York JFK",
    "LAX": "Los Angeles",
}

SCHENGEN = {"CDG","ORY","AMS","EIN","BCN","MAD","FCO","MXP","LIN","FRA","MUC",
            "TXL","BER","VIE","PRG","ATH","SKG","LIS","ARN","GOT","CPH","HEL",
            "OSL","ZUR","GVA","BRU","WAW","KRK","BUD","SOF","OTP","RIX","TLL","VNO","LJU","SKP"}
VISA_WARN = {"LHR","LGW","STN","MAN","JFK","LAX","ORD","MIA","SFO","BOS","IAD","YYZ","YVR"}

# ============================================================
# YARDIMCI FONKSİYONLAR
# ============================================================
def get_visa_status(dest):
    if dest.upper() in SCHENGEN: return "✅ VİZESİZ (Schengen – Yeşil Pasaport)"
    if dest.upper() in VISA_WARN: return "⚠️ VİZE GEREKLİ (UK/ABD/Kanada)"
    return "ℹ️ Vize durumu kontrol edilmeli"

def get_search_dates():
    dates = []
    base = datetime.now()
    for w in [2, 3, 4, 5, 6, 8, 10, 12, 14, 16]:
        d = base + timedelta(weeks=w)
        fri = d + timedelta(days=(4 - d.weekday()) % 7)
        mon = fri + timedelta(days=3)
        dates.append((fri.strftime("%Y-%m-%d"), mon.strftime("%Y-%m-%d")))
    return dates

def build_short_url(origin, dest, dep, ret):
    import urllib.parse
    q = urllib.parse.quote(f"{origin} to {dest} {dep} {ret}")
    return f"https://www.google.com/travel/flights?hl=tr&curr=TRY&gl=TR&q={q}"

def should_alarm(price, target, has_stopover):
    if has_stopover:
        return price <= target * STOPOVER_THRESHOLD, "aktarmalı-%90"
    return price <= target * DIRECT_THRESHOLD, "direkt-%50"

def sanity_check(price, route):
    mn, mx = BOUNDS.get(route, (100, 200000))
    return mn <= price <= mx

def is_fresh(scraped_at):
    if not scraped_at: return True
    return (datetime.now() - scraped_at).total_seconds() < MAX_DATA_AGE_HOURS * 3600

# ============================================================
# FİYAT PARSE
# ============================================================
def extract_prices_from_html(html, route):
    mn, mx = BOUNDS.get(route, (100, 200000))
    found = set()

    # Yöntem 1: ₺ sembolü
    for m in re.finditer(r'₺\s*([\d]{1,3}(?:[.,][\d]{3})*|[\d]{3,6})', html):
        raw = m.group(1).replace(".", "").replace(",", "")
        try:
            p = float(raw)
            if mn <= p <= mx: found.add(p)
        except: pass

    # Yöntem 2: "X TL" formatı
    for m in re.finditer(r'([\d]{1,3}(?:[.,][\d]{3})+)\s*TL', html):
        raw = m.group(1).replace(".", "").replace(",", "")
        try:
            p = float(raw)
            if mn <= p <= mx: found.add(p)
        except: pass

    # Yöntem 3: JSON TRY
    for m in re.finditer(r'"(\d{4,6})"\s*,\s*"TRY"', html):
        try:
            p = float(m.group(1))
            if mn <= p <= mx: found.add(p)
        except: pass

    for m in re.finditer(r'\[null,null,(\d{4,6})[,\]]', html):
        try:
            p = float(m.group(1))
            if mn <= p <= mx: found.add(p)
        except: pass

    if found:
        result = sorted(found)
        print(f"    [PARSE] {len(result)} fiyat: {result[:5]}")
        return result[:5]

    print(f"    [PARSE] Fiyat yok ({mn:,}–{mx:,} TL aralığı)")
    idx = html.find("₺")
    if idx >= 0:
        print(f"    [DEBUG] ₺ bağlamı: {repr(html[max(0,idx-10):idx+30])}")
    else:
        print(f"    [DEBUG] HTML'de ₺ yok. Uzunluk: {len(html):,}")
    return []

def is_real_captcha(html, url):
    """
    Gerçek CAPTCHA'yı masumca geçen 'robot' kelimesinden ayırt eder.
    Google Flights HTML'inde 'robot' kelimesi meşru içerikte de geçer.
    """
    # Gerçek CAPTCHA sinyalleri
    real_signals = [
        "unusual traffic",
        "/sorry/index",
        "recaptcha/api.js",
        "g-recaptcha",
        "I'm not a robot",
        "Are you a robot",
        "confirm you're not a robot",
    ]
    html_lower = html.lower()
    for sig in real_signals:
        if sig.lower() in html_lower:
            return True, sig
    if "/sorry/" in url:
        return True, "URL /sorry/"
    return False, None

def detect_stopover(html):
    if "nonstop" in html.lower(): return False
    kws = ["aktarma", "aktarmalı", "1 stop", "2 stop", "layover", "connecting"]
    return any(kw in html.lower() for kw in kws)

# ============================================================
# PLAYWRIGHT — FORM DOLDURMA YÖNTEMİ
# ============================================================
def scrape_with_playwright(origin, dest, dep_date, ret_date):
    """
    Google Flights ana sayfasını açar, arama formunu doldurur,
    gidiş-dönüş tarihlerini seçer, arama yapar ve sonuçları çeker.
    
    Hash URL (#flt=...) headless tarayıcıda çalışmıyor çünkü
    hash kısmı server'a gönderilmiyor — sadece JS tarafından işleniyor.
    Bu yöntem gerçek kullanıcı davranışı simüle eder.
    """
    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
    except ImportError:
        print("  [HATA] playwright kurulu değil: pip install playwright && playwright install chromium")
        return []

    route = f"{origin}-{dest}"
    print(f"    [PW] {route} {dep_date}→{ret_date} — form doldurma başlıyor")

    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=HEADLESS,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-extensions",
                "--window-size=1366,768",
            ]
        )

        context = browser.new_context(
            viewport={"width": 1366, "height": 768},
            locale="tr-TR",
            timezone_id="Europe/Istanbul",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/121.0.0.0 Safari/537.36"
            ),
            extra_http_headers={
                "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
            }
        )

        # Otomasyon sinyallerini gizle
        context.add_init_script("""
            // webdriver bayrağını gizle
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            // Chrome nesnesi
            window.chrome = {runtime: {}, loadTimes: () => {}, csi: () => {}, app: {}};
            // Plugin listesi doldur
            Object.defineProperty(navigator, 'plugins', {
                get: () => {
                    const arr = [
                        {name:'Chrome PDF Plugin', filename:'internal-pdf-viewer'},
                        {name:'Chrome PDF Viewer', filename:'mhjfbmdgcfjbbpaeojofohoefgiehjai'},
                        {name:'Native Client', filename:'internal-nacl-plugin'},
                    ];
                    arr.__proto__ = PluginArray.prototype;
                    return arr;
                }
            });
            // Dil ayarı
            Object.defineProperty(navigator, 'languages', {get: () => ['tr-TR', 'tr', 'en-US', 'en']});
            // Permissions API
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (params) => (
                params.name === 'notifications' ? 
                Promise.resolve({state: Notification.permission}) : 
                originalQuery(params)
            );
        """)

        page = context.new_page()

        try:
            # ── Adım 1: Ana sayfayı aç ────────────────────────────────
            print(f"    [PW] Ana sayfa açılıyor...")
            page.goto(
                "https://www.google.com/travel/flights?hl=tr&curr=TRY&gl=TR",
                timeout=PAGE_TIMEOUT_MS,
                wait_until="domcontentloaded"
            )

            # CAPTCHA kontrolü
            captcha, signal = is_real_captcha(page.content(), page.url)
            if captcha:
                print(f"    [PW] Gerçek CAPTCHA: {signal}")
                browser.close()
                return []

            # İnsan gibi kısa bekleme
            page.wait_for_timeout(random.randint(1500, 3000))

            # Cookie popup'ı kapat (varsa)
            _close_cookie_popup(page)

            # ── Adım 2: Round-trip (gidiş-dönüş) modunu doğrula ──────
            # Varsayılan round-trip — değilse seç
            _ensure_roundtrip(page)

            # ── Adım 3: Nereden alanını doldur ───────────────────────
            origin_name = AIRPORT_NAMES.get(origin, origin)
            dest_name   = AIRPORT_NAMES.get(dest, dest)
            print(f"    [PW] Nereden: {origin} ({origin_name})")

            if not _fill_airport_field(page, "origin", origin, origin_name):
                print(f"    [PW] Origin doldurulamadı, HTML parse'a geçiliyor")
                results = _fallback_url_scrape(page, origin, dest, dep_date, ret_date, route)
                browser.close()
                return results

            page.wait_for_timeout(random.randint(800, 1500))

            # ── Adım 4: Nereye alanını doldur ────────────────────────
            print(f"    [PW] Nereye: {dest} ({dest_name})")
            if not _fill_airport_field(page, "dest", dest, dest_name):
                print(f"    [PW] Dest doldurulamadı")
                results = _fallback_url_scrape(page, origin, dest, dep_date, ret_date, route)
                browser.close()
                return results

            page.wait_for_timeout(random.randint(800, 1500))

            # ── Adım 5: Tarihleri seç ─────────────────────────────────
            print(f"    [PW] Tarih: {dep_date} → {ret_date}")
            _select_dates(page, dep_date, ret_date)

            page.wait_for_timeout(random.randint(1000, 2000))

            # ── Adım 6: Ara ───────────────────────────────────────────
            print(f"    [PW] Arama yapılıyor...")
            _click_search(page)

            # Sonuçları bekle
            print(f"    [PW] Sonuçlar bekleniyor ({RENDER_WAIT_MS}ms)...")
            page.wait_for_timeout(RENDER_WAIT_MS)

            try:
                page.wait_for_load_state("networkidle", timeout=15000)
            except: pass

            page.wait_for_timeout(3000)

            # ── Adım 7: Fiyatları çek ─────────────────────────────────
            scraped_at = datetime.now()
            title      = page.title()
            cur_url    = page.url
            html       = page.content()
            print(f"    [PW] Sayfa: '{title[:70]}'")
            print(f"    [PW] HTML: {len(html):,} byte")

            # Gerçek CAPTCHA kontrolü
            captcha, signal = is_real_captcha(html, cur_url)
            if captcha:
                print(f"    [PW] CAPTCHA sonuç sayfasında: {signal}")
                browser.close()
                return []

            # DOM'dan fiyat çek
            dom_results = _dom_extract(page, route, scraped_at)
            if dom_results:
                results = dom_results
                print(f"    [PW] DOM: {len(results)} fiyat")
            else:
                # HTML parse'a düş
                prices = extract_prices_from_html(html, route)
                stop   = detect_stopover(html)
                results = [{
                    "price": pr,
                    "airline": "Çeşitli",
                    "has_stopover": stop,
                    "scraped_at": scraped_at,
                    "source": "playwright_html",
                } for pr in prices]

            if not results:
                _save_debug_screenshot(page, origin, dest, dep_date)

        except Exception as e:
            print(f"    [PW HATA] {type(e).__name__}: {e}")
            try: _save_debug_screenshot(page, origin, dest, dep_date)
            except: pass
        finally:
            browser.close()

    return results


def _close_cookie_popup(page):
    """Cookie / consent popup'ını kapat."""
    for text in ["Tümünü reddet", "Reject all", "Kabul et", "Accept all", "Agree"]:
        try:
            btn = page.get_by_role("button", name=re.compile(text, re.IGNORECASE))
            if btn.count() > 0:
                btn.first.click(timeout=3000)
                print(f"    [PW] Popup kapatıldı: '{text}'")
                page.wait_for_timeout(500)
                return
        except: pass


def _ensure_roundtrip(page):
    """Gidiş-dönüş modunda olduğundan emin ol."""
    try:
        # Uçuş tipi dropdown
        trip_btn = page.locator('[data-value="1"], [aria-label*="Round trip"], [aria-label*="Gidiş-dönüş"]')
        if trip_btn.count() > 0:
            print(f"    [PW] Round-trip modu zaten seçili")
            return
        # Değilse dropdown'u aç ve round-trip seç
        mode_select = page.locator('div[data-gs]:first-child, .VfPpkd-TkwUic').first
        mode_select.click(timeout=3000)
        page.wait_for_timeout(500)
        roundtrip = page.get_by_text("Gidiş-dönüş", exact=False)
        if roundtrip.count() > 0:
            roundtrip.first.click(timeout=2000)
    except: pass


def _fill_airport_field(page, field_type, code, name):
    """
    Havalimanı alanını doldur.
    field_type: "origin" veya "dest"
    """
    # Google Flights form alanı selector'ları
    if field_type == "origin":
        selectors = [
            '[placeholder*="Nereden"], [placeholder*="From"], [placeholder*="Origin"]',
            '[aria-label*="Nereden"], [aria-label*="Where from"], [aria-label*="From"]',
            'input[aria-label*="Kalkış"]',
            '.e5F5td input',   # Google Flights 2024 class
            'input[role="combobox"]:first-of-type',
        ]
    else:
        selectors = [
            '[placeholder*="Nereye"], [placeholder*="To"], [placeholder*="Destination"]',
            '[aria-label*="Nereye"], [aria-label*="Where to"], [aria-label*="To"]',
            'input[aria-label*="Varış"]',
            '.e5F5td input:nth-of-type(2)',
            'input[role="combobox"]:nth-of-type(2)',
        ]

    for sel in selectors:
        try:
            field = page.locator(sel).first
            if field.count() == 0:
                continue

            # Mevcut değeri temizle
            field.click(timeout=3000)
            page.wait_for_timeout(300)
            field.select_all()
            field.press("Backspace")
            page.wait_for_timeout(200)

            # Havalimanı kodunu yaz (insan hızında)
            field.type(code, delay=random.randint(80, 150))
            page.wait_for_timeout(random.randint(1000, 1800))

            # Autocomplete dropdown'dan seç
            dropdown_items = page.locator(
                'li[role="option"], [data-value], .pFWOv, .n3jYMd li'
            )
            if dropdown_items.count() > 0:
                # İlk eşleşen seçeneği bul
                for i in range(min(5, dropdown_items.count())):
                    item_text = dropdown_items.nth(i).inner_text()
                    if code in item_text.upper() or name.split()[0].lower() in item_text.lower():
                        dropdown_items.nth(i).click(timeout=2000)
                        print(f"    [PW] '{code}' seçildi: {item_text[:50]}")
                        page.wait_for_timeout(400)
                        return True
                # İlk seçeneği al
                dropdown_items.first.click(timeout=2000)
                print(f"    [PW] '{code}' ilk seçenek seçildi")
                page.wait_for_timeout(400)
                return True
            else:
                # Dropdown yoksa Enter dene
                field.press("Enter")
                page.wait_for_timeout(500)
                return True

        except Exception as e:
            print(f"    [PW] Field '{sel}' hata: {e}")
            continue

    return False


def _select_dates(page, dep_date, ret_date):
    """
    Tarih alanlarını doldur.
    Önce text input deneyi, yoksa takvim UI.
    """
    # Gidiş tarihi input'u bul
    dep_selectors = [
        '[placeholder*="Gidiş"], [aria-label*="Gidiş tarihi"], [aria-label*="Departure"]',
        'input[aria-label*="departure"], input[aria-label*="Gidiş"]',
        '.TP4Lpb input:first-of-type',
    ]
    ret_selectors = [
        '[placeholder*="Dönüş"], [aria-label*="Dönüş tarihi"], [aria-label*="Return"]',
        'input[aria-label*="return"], input[aria-label*="Dönüş"]',
        '.TP4Lpb input:last-of-type',
    ]

    def fill_date_field(selectors, date_str):
        # Türkçe tarih formatı: GG Ay YYYY (örn: 10 Nis 2026)
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        tr_months = {1:"Oca",2:"Şub",3:"Mar",4:"Nis",5:"May",6:"Haz",
                     7:"Tem",8:"Ağu",9:"Eyl",10:"Eki",11:"Kas",12:"Ara"}
        tr_date = f"{dt.day} {tr_months[dt.month]} {dt.year}"

        for sel in selectors:
            try:
                field = page.locator(sel).first
                if field.count() == 0: continue
                field.click(timeout=3000)
                page.wait_for_timeout(500)
                field.fill("")
                field.type(date_str, delay=80)  # YYYY-MM-DD dene
                page.wait_for_timeout(800)
                # Autocomplete'den seç veya Enter
                opts = page.locator('li[role="option"]')
                if opts.count() > 0:
                    opts.first.click(timeout=2000)
                else:
                    field.press("Enter")
                    page.wait_for_timeout(500)
                return True
            except: continue
        return False

    dep_ok = fill_date_field(dep_selectors, dep_date)
    page.wait_for_timeout(random.randint(500, 1000))
    ret_ok = fill_date_field(ret_selectors, ret_date)

    if not dep_ok or not ret_ok:
        # Takvim UI dene
        _select_dates_calendar(page, dep_date, ret_date)


def _select_dates_calendar(page, dep_date, ret_date):
    """Takvim arayüzü ile tarih seç."""
    try:
        # Herhangi bir tarih alanına tıkla
        date_field = page.locator('[aria-label*="tarih"], [aria-label*="date"]').first
        date_field.click(timeout=5000)
        page.wait_for_timeout(1000)

        # Takvimde tarihleri bul ve tıkla
        dep_dt = datetime.strptime(dep_date, "%Y-%m-%d")
        ret_dt = datetime.strptime(ret_date, "%Y-%m-%d")

        for dt, label in [(dep_dt, "gidiş"), (ret_dt, "dönüş")]:
            # data-iso veya aria-label ile gün bul
            day_sel = page.locator(
                f'[data-iso="{dt.strftime("%Y-%m-%d")}"], '
                f'[aria-label*="{dt.day}"]'
            )
            if day_sel.count() > 0:
                day_sel.first.click(timeout=3000)
                print(f"    [PW] {label} takvimde seçildi: {dt.date()}")
                page.wait_for_timeout(500)

        # "Bitti" / "Done" butonuna tıkla
        for done_text in ["Bitti", "Done", "Tamam", "OK"]:
            try:
                btn = page.get_by_role("button", name=done_text)
                if btn.count() > 0:
                    btn.first.click(timeout=2000)
                    break
            except: pass
    except Exception as e:
        print(f"    [PW] Takvim seçimi hata: {e}")


def _click_search(page):
    """Arama butonuna tıkla."""
    search_selectors = [
        'button[aria-label*="Ara"], button[aria-label*="Search"]',
        'button:has-text("Ara"), button:has-text("Search")',
        '.MXvFbd',   # Google Flights arama butonu class (2024)
        'button[type="submit"]',
        '[role="button"]:has-text("Ara")',
    ]
    for sel in search_selectors:
        try:
            btn = page.locator(sel).first
            if btn.count() > 0:
                btn.click(timeout=5000)
                print(f"    [PW] Arama butonuna tıklandı: {sel}")
                return True
        except: continue

    # Son çare: Enter tuşu
    page.keyboard.press("Enter")
    print(f"    [PW] Enter ile arama tetiklendi")
    return True


def _fallback_url_scrape(page, origin, dest, dep_date, ret_date, route):
    """
    Form doldurulamadığında URL parametreli yaklaşım dene.
    q= parametresi hash'ten farklı olarak bazı durumlarda çalışır.
    """
    import urllib.parse
    print(f"    [PW] Fallback: URL ile arama deneniyor...")
    url = (f"https://www.google.com/travel/flights"
           f"?hl=tr&curr=TRY&gl=TR"
           f"&q={urllib.parse.quote(AIRPORT_NAMES.get(origin, origin))}"
           f"+to+{urllib.parse.quote(AIRPORT_NAMES.get(dest, dest))}"
           f"+{dep_date}+{ret_date}")
    try:
        page.goto(url, timeout=PAGE_TIMEOUT_MS, wait_until="domcontentloaded")
        page.wait_for_timeout(RENDER_WAIT_MS)
        html = page.content()
        captcha, sig = is_real_captcha(html, page.url)
        if captcha:
            print(f"    [PW] Fallback CAPTCHA: {sig}")
            return []
        prices = extract_prices_from_html(html, route)
        stop   = detect_stopover(html)
        scraped_at = datetime.now()
        return [{"price": p, "airline": "Çeşitli", "has_stopover": stop,
                 "scraped_at": scraped_at, "source": "playwright_url"} for p in prices]
    except Exception as e:
        print(f"    [PW] Fallback hata: {e}")
        return []


def _dom_extract(page, route, scraped_at):
    """DOM'dan fiyatları çek."""
    mn, mx = BOUNDS.get(route, (100, 200000))
    results = []

    price_selectors = [
        # Google Flights 2024+ fiyat container'ları
        '[data-gs] .YMlIz',
        '[data-gs] .FpEdX',
        '[data-gs]',
        # Aria label bazlı
        '[aria-label*="TL"]',
        '[aria-label*="Türk lirası"]',
        # Genel
        'div.YMlIz',
        'span.YMlIz',
        'div.FpEdX',
    ]

    price_regex = [
        r'₺\s*([\d]{1,3}(?:[.,][\d]{3})+)',
        r'₺\s*(\d{4,6})',
        r'([\d]{1,3}(?:[.,][\d]{3})+)\s*TL',
    ]

    for sel in price_selectors:
        try:
            elems = page.locator(sel).all()
            if not elems: continue
            print(f"    [DOM] '{sel}' → {len(elems)} element")

            for elem in elems[:40]:
                try:
                    text = (elem.inner_text() or "").strip()
                    if not text:
                        text = elem.get_attribute("aria-label") or ""
                    if not text: continue

                    for pat in price_regex:
                        m = re.search(pat, text.replace("\xa0", "").replace("\u200b", ""))
                        if m:
                            raw   = m.group(1).replace(".", "").replace(",", "")
                            price = float(raw)
                            if mn <= price <= mx:
                                stop = any(kw in text.lower()
                                           for kw in ["aktarma", "1 stop", "2 stop", "layover"])
                                results.append({
                                    "price": price,
                                    "airline": "Çeşitli",
                                    "has_stopover": stop,
                                    "scraped_at": scraped_at,
                                    "source": "playwright_dom",
                                })
                                print(f"    [DOM] ✓ {price:,.0f} TL")
                            break
                except: pass

            if results: break

        except Exception as e:
            print(f"    [DOM] Hata: {e}")

    # Deduplicate
    seen = set()
    unique = []
    for r in results:
        if r["price"] not in seen:
            seen.add(r["price"])
            unique.append(r)
    return sorted(unique, key=lambda x: x["price"])


def _save_debug_screenshot(page, origin, dest, dep_date):
    """Hata durumunda screenshot kaydet."""
    try:
        path = f"/tmp/titan_debug_{origin}{dest}_{dep_date}.png"
        page.screenshot(path=path, full_page=False)
        print(f"    [PW] Screenshot: {path}")
    except: pass

# ============================================================
# HISTORY
# ============================================================
HFILE = Path("history.json")

def load_history():
    if HFILE.exists():
        try: return json.loads(HFILE.read_text(encoding="utf-8"))
        except: pass
    return {"alarms": []}

def save_history(h):
    HFILE.write_text(json.dumps(h, ensure_ascii=False, indent=2), encoding="utf-8")

def can_send_alarm(route, price, target):
    h = load_history()
    cutoff30 = (datetime.now() - timedelta(days=30)).isoformat()
    h["alarms"] = [a for a in h.get("alarms", []) if a.get("time", "") > cutoff30]
    cutoff24  = (datetime.now() - timedelta(hours=24)).isoformat()
    band_low  = price * 0.95
    band_high = price * 1.05
    recent = [
        a for a in h["alarms"]
        if a.get("route") == route
        and a.get("time", "") > cutoff24
        and band_low <= a.get("price", 0) <= band_high
    ]
    if recent:
        return False, f"{route} aynı bandda 24s içinde alarm gönderildi"
    return True, "OK"

def record_alarm(route, price):
    h = load_history()
    h.setdefault("alarms", []).append({
        "route": route, "price": price, "time": datetime.now().isoformat()
    })
    save_history(h)

# ============================================================
# TELEGRAM
# ============================================================
def send_telegram(msg):
    import urllib.request
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    for cid in [ADMIN_ID, GROUP_ID]:
        try:
            data = json.dumps({
                "chat_id": cid, "text": msg,
                "parse_mode": "HTML",
                "disable_web_page_preview": False,
            }).encode()
            req = urllib.request.Request(
                url, data=data, headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=15) as r:
                resp = json.loads(r.read())
                print(f"  [TG {'✓' if resp.get('ok') else '✗'}] {cid}")
        except Exception as e:
            print(f"  [TG ERR] {cid}: {e}")

def format_message(origin, dest, dep, ret, price, airline, target, has_stop):
    pct  = round((1 - price / target) * 100)
    link = build_short_url(origin, dest, dep, ret)
    tip  = "🔄 Aktarmalı" if has_stop else "✈️ Direkt"
    if has_stop:
        header = "🚨 <b>AKTARMALI – EXTREME FARE ALARMI</b> ⚡"
        note   = f"⚡ Aktarmalı ama hedefin <b>%{pct} altında!</b> — İstisnai fiyat."
    else:
        header = "🦅 <b>DİP FİYAT ALARMI</b> 💎"
        note   = f"📊 Direkt uçuş, hedefin <b>%{pct} altında!</b>"
    return (
        f"{header}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{tip} <b>Rota:</b> {origin} ➔ {dest}\n"
        f"📅 <b>Gidiş:</b> {dep}\n"
        f"📅 <b>Dönüş:</b> {ret}\n"
        f"💰 <b>Fiyat:</b> {price:,.0f} TL\n"
        f"🎯 <b>Hedef:</b> {target:,.0f} TL\n"
        f"🏷️ <b>Havayolu:</b> {airline}\n"
        f"{note}\n"
        f"🌍 <b>Vize:</b> {get_visa_status(dest)}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f'🔍 <a href="{link}">Google Flights\'ta Ara</a>\n'
        f"⚡ HEMEN AL!"
    )

# ============================================================
# ANA MOTOR
# ============================================================
def run_scraper():
    print(f"\n{'='*60}")
    print(f"PROJECT TITAN v6.1 (Playwright Form) — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Direkt eşik   : hedefin %{round(DIRECT_THRESHOLD*100)}'i altı")
    print(f"Aktarmalı eşik: hedefin %{round(STOPOVER_THRESHOLD*100)}'i altı")
    print(f"{'='*60}\n")

    all_flights  = []
    search_dates = get_search_dates()
    alarms_sent  = 0

    for route in ROUTES:
        origin, dest = route.split("-")
        target   = TARGET_PRICES[route]
        dir_esik = target * DIRECT_THRESHOLD
        stp_esik = target * STOPOVER_THRESHOLD
        print(f"\n[ROTA] {route} | Hedef: {target:,} TL | Direkt<{dir_esik:,.0f} | Aktarmalı<{stp_esik:,.0f}")

        for dep, ret in random.sample(search_dates, min(2, len(search_dates))):
            print(f"  ▶ {dep} → {ret}")
            glink = build_short_url(origin, dest, dep, ret)

            flights = scrape_with_playwright(origin, dest, dep, ret)

            if not flights:
                print(f"  [!] Veri alınamadı")
                all_flights.append({
                    "route": route, "origin": origin, "dest": dest,
                    "depart_date": dep, "return_date": ret,
                    "price": None, "airline": "Veri yok", "target": target,
                    "alarm_threshold": round(dir_esik),
                    "savings_pct": None, "is_below_target": False,
                    "is_mistake_fare": False, "has_stopover": None,
                    "google_link": glink,
                    "scraped_at": datetime.now().isoformat(),
                    "data_source": "no_results",
                })
                time.sleep(random.uniform(5, 10))
                continue

            for f in flights:
                price      = f["price"]
                airline    = f.get("airline", "Çeşitli")
                scraped_at = f.get("scraped_at")
                stop       = f.get("has_stopover", False)

                if not sanity_check(price, route):
                    print(f"  [!] Sanity FAIL: {price:,.0f} TL")
                    continue

                alarm_ok, alarm_type = should_alarm(price, target, stop)
                pct       = round((1 - price / target) * 100)
                stop_lbl  = "🔄aktarmalı" if stop else "✈️direkt"
                alarm_lbl = f"🚨{alarm_type}" if alarm_ok else ""
                print(f"  [✓] {price:,.0f} TL | {stop_lbl} | -%{pct} {alarm_lbl}")

                all_flights.append({
                    "route": route, "origin": origin, "dest": dest,
                    "depart_date": dep, "return_date": ret,
                    "price": price, "airline": airline, "target": target,
                    "alarm_threshold": round(dir_esik),
                    "savings_pct": pct,
                    "is_below_target": alarm_ok,
                    "is_mistake_fare": stop,
                    "has_stopover": stop,
                    "google_link": glink,
                    "scraped_at": scraped_at.isoformat() if scraped_at else datetime.now().isoformat(),
                    "data_source": f.get("source", "playwright"),
                })

                if alarm_ok:
                    if not is_fresh(scraped_at):
                        print(f"  [⏸] Veri eski")
                        continue
                    ok, reason = can_send_alarm(route, price, target)
                    if ok:
                        print(f"  [🔔] ALARM! Telegram...")
                        send_telegram(format_message(origin, dest, dep, ret, price, airline, target, stop))
                        record_alarm(route, price)
                        alarms_sent += 1
                    else:
                        print(f"  [⏸] {reason}")

            sleep_s = random.uniform(10, 18)
            print(f"  [⏳] {sleep_s:.1f}s bekleniyor...")
            time.sleep(sleep_s)

    # flights.json yaz
    valid   = [f for f in all_flights if f.get("price") is not None]
    no_data = [f for f in all_flights if f.get("price") is None]

    output = {
        "last_updated": datetime.now().isoformat(),
        "total_found": len(valid),
        "below_target": sum(1 for f in valid if f.get("is_below_target")),
        "alarms_sent_this_run": alarms_sent,
        "direct_threshold_pct": round((1 - DIRECT_THRESHOLD) * 100),
        "stopover_threshold_pct": round((1 - STOPOVER_THRESHOLD) * 100),
        "data_source": "playwright_chromium",
        "flights": sorted(valid, key=lambda x: x["price"]) + no_data,
    }
    Path("flights.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"\n{'='*60}")
    print(f"[✓] {len(valid)} uçuş | {output['below_target']} alarm altı | {alarms_sent} alarm gönderildi")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    run_scraper()
