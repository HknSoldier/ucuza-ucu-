#!/usr/bin/env python3
"""
PROJECT TITAN v6.0 — Playwright Edition
Alarm kuralları:
- Direkt uçuş  : hedefin %50'sinden ucuz   → ALARM
- Aktarmalı    : hedefin %10'undan ucuz    → ALARM (%90 indirim)
- Aynı rota + fiyat bandı (%5) → 24s içinde tekrar alarm yok
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

DIRECT_THRESHOLD   = 0.50   # Direkt: hedefin %50 altı
STOPOVER_THRESHOLD = 0.10   # Aktarmalı: hedefin %10 altı (%90 indirim)
MAX_DATA_AGE_HOURS = 3
HEADLESS           = True   # GitHub Actions'da True olmalı
PAGE_TIMEOUT_MS    = 60_000
WAIT_AFTER_LOAD_MS = 8_000  # JS render için bekleme (ms)

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

# Fiyat aralığı: alarm eşiğini kapsayacak kadar geniş
BOUNDS = {
    "IST-CDG":(150,15000),  "IST-LHR":(150,16000),  "IST-AMS":(150,14000),
    "IST-BCN":(150,14000),  "IST-FCO":(150,13000),  "IST-MAD":(150,15000),
    "IST-FRA":(150,13000),  "IST-MUC":(150,13000),  "IST-VIE":(150,12000),
    "IST-PRG":(150,13000),  "IST-ATH":(100,10000),  "IST-DXB":(150,12000),
    "IST-JFK":(1000,80000), "IST-LAX":(1000,90000),
    "SAW-CDG":(150,15000),  "SAW-LHR":(150,16000),  "SAW-AMS":(150,14000),
    "SAW-BCN":(150,14000),  "SAW-FCO":(150,13000),
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
    """Önümüzdeki haftalara ait Cuma-Pazartesi tarifleri üretir."""
    dates = []
    base = datetime.now()
    for w in [2, 3, 4, 5, 6, 8, 10, 12, 14, 16]:
        d = base + timedelta(weeks=w)
        fri = d + timedelta(days=(4 - d.weekday()) % 7)
        mon = fri + timedelta(days=3)
        dates.append((fri.strftime("%Y-%m-%d"), mon.strftime("%Y-%m-%d")))
    return dates

def build_short_url(origin, dest, dep, ret):
    """Dashboard ve Telegram için Google Flights linki."""
    import urllib.parse
    q = urllib.parse.quote(f"{origin} to {dest} {dep} {ret}")
    return f"https://www.google.com/travel/flights?hl=tr&curr=TRY&gl=TR&q={q}"

def build_flights_url(origin, dest, dep, ret, nonstop=True):
    """
    Google Flights hash URL — fiyatların direkt görünmesi için en iyi format.
    #flt= parametresi sayfayı doğru sonuçlara yönlendirir.
    """
    base = f"https://www.google.com/travel/flights?hl=tr&curr=TRY&gl=TR"
    # Nonstop filtresi: sd:1 = stops direct only
    stops = ";sd:1" if nonstop else ""
    hash_part = f"flt={origin}.{dest}.{dep}*{dest}.{origin}.{ret};c:TRY;e:1{stops};t:f"
    return f"{base}#{hash_part}"

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
    """HTML string'inden TL fiyatlarını çıkarır."""
    mn, mx = BOUNDS.get(route, (100, 200000))
    found = set()

    # Yöntem 1: ₺ sembolü yanındaki sayılar
    for m in re.finditer(r'₺\s*([\d]{1,3}(?:[.,][\d]{3})*|[\d]{3,6})', html):
        raw = m.group(1).replace(".", "").replace(",", "")
        try:
            price = float(raw)
            if mn <= price <= mx:
                found.add(price)
        except ValueError:
            pass

    # Yöntem 2: "TL" kelimesinin önündeki sayılar
    for m in re.finditer(r'([\d]{1,3}(?:[.,][\d]{3})+)\s*TL', html):
        raw = m.group(1).replace(".", "").replace(",", "")
        try:
            price = float(raw)
            if mn <= price <= mx:
                found.add(price)
        except ValueError:
            pass

    # Yöntem 3: JSON TRY fiyatları
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

    print(f"    [PARSE] Fiyat bulunamadı ({mn:,}–{mx:,} TL)")
    tl_idx = html.find("₺")
    if tl_idx >= 0:
        print(f"    [DEBUG] ₺ bağlamı: {repr(html[max(0,tl_idx-10):tl_idx+30])}")
    else:
        print(f"    [DEBUG] HTML'de ₺ yok. Uzunluk: {len(html):,} byte")
    return []

def detect_stopover(html):
    """Sayfada aktarma ifadesi var mı?"""
    if "nonstop" in html.lower(): return False
    kws = ["aktarma", "aktarmalı", "1 stop", "2 stop", "layover", "connecting"]
    return any(kw in html.lower() for kw in kws)

# ============================================================
# PLAYWRIGHT SCRAPER
# ============================================================
def scrape_with_playwright(origin, dest, dep_date, ret_date):
    """
    Playwright Chromium ile Google Flights açar, JS render bekler, fiyat çeker.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("  [HATA] Playwright kurulu değil!")
        print("  Çözüm: pip install playwright && playwright install chromium")
        return []

    route = f"{origin}-{dest}"
    url   = build_flights_url(origin, dest, dep_date, ret_date, nonstop=True)

    print(f"    [PW] {route} {dep_date}→{ret_date}")
    print(f"    [PW] {url[:100]}")

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
            }
        )

        # Otomasyon tespitini engelle
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            Object.defineProperty(navigator, 'languages', {get: () => ['tr-TR', 'tr', 'en-US']});
            window.chrome = {runtime: {}};
        """)

        page = context.new_page()

        try:
            page.goto(url, timeout=PAGE_TIMEOUT_MS, wait_until="domcontentloaded")

            # CAPTCHA / blok kontrolü
            cur_url = page.url
            if "/sorry/" in cur_url or "unusual traffic" in cur_url:
                print(f"    [PW] CAPTCHA — atlanıyor")
                browser.close()
                return []

            # Cookie popup'ı kapat
            for btn_text in ["Tümünü reddet", "Reject all", "Accept all", "Tümünü kabul et"]:
                try:
                    btn = page.get_by_role("button", name=btn_text)
                    if btn.count() > 0:
                        btn.first.click(timeout=3000)
                        print(f"    [PW] '{btn_text}' tıklandı")
                        break
                except: pass

            # Network isteklerinin bitmesini bekle
            try:
                page.wait_for_load_state("networkidle", timeout=20000)
            except:
                pass

            # JS render için ekstra bekleme
            print(f"    [PW] Render bekleniyor ({WAIT_AFTER_LOAD_MS}ms)...")
            page.wait_for_timeout(WAIT_AFTER_LOAD_MS)

            # Fiyat elementlerini bekle — birden fazla selector dene
            fiyat_yüklendi = False
            for sel in [
                '[data-gs]',
                '.YMlIz',
                '.FpEdX',
                'div[aria-label*="TL"]',
                'span[aria-label*="TL"]',
                '[class*="price"]',
            ]:
                try:
                    page.wait_for_selector(sel, timeout=8000)
                    print(f"    [PW] Selector bulundu: {sel}")
                    fiyat_yüklendi = True
                    break
                except: pass

            if not fiyat_yüklendi:
                print(f"    [PW] Fiyat selector'ı bulunamadı — devam ediliyor")

            # Biraz daha bekle
            page.wait_for_timeout(3000)

            scraped_at = datetime.now()
            title      = page.title()
            print(f"    [PW] Sayfa: '{title[:60]}'")

            # HTML al
            html = page.content()
            print(f"    [PW] HTML: {len(html):,} byte")

            # CAPTCHA HTML kontrolü
            if "captcha" in html.lower() or "i'm not a robot" in html.lower():
                print(f"    [PW] CAPTCHA HTML'de tespit edildi")
                browser.close()
                return []

            # 1. Önce DOM'dan direkt çek (daha doğru)
            dom_results = _dom_extract(page, route, scraped_at)

            if dom_results:
                results = dom_results
                print(f"    [PW] DOM: {len(results)} sonuç")
            else:
                # 2. HTML parse'a düş
                print(f"    [PW] DOM boş, HTML parse deneniyor...")
                prices = extract_prices_from_html(html, route)
                stop   = detect_stopover(html)
                for pr in prices:
                    results.append({
                        "price": pr,
                        "airline": "Çeşitli",
                        "has_stopover": stop,
                        "scraped_at": scraped_at,
                        "source": "playwright_html",
                    })

            # Sonuç yoksa screenshot al (debug)
            if not results:
                try:
                    ss = f"/tmp/debug_{origin}{dest}_{dep_date}.png"
                    page.screenshot(path=ss)
                    print(f"    [PW] Screenshot: {ss}")
                except: pass

        except Exception as e:
            print(f"    [PW HATA] {type(e).__name__}: {e}")
        finally:
            browser.close()

    return results


def _dom_extract(page, route, scraped_at):
    """Playwright page üzerinden DOM sorgulama."""
    mn, mx = BOUNDS.get(route, (100, 200000))
    results = []

    # Google Flights DOM selector'ları (öncelik sırasıyla)
    selectors = [
        # 2024+ Google Flights fiyat container
        '[data-gs]',
        # Fiyat span'ları
        '.YMlIz',
        '.FpEdX',
        '.gDs2Hf',
        # Genel
        '[aria-label*="Türk lirası"]',
        '[aria-label*="TL"]',
        'div[role="listitem"]',
    ]

    for sel in selectors:
        try:
            elems = page.locator(sel).all()
            if not elems:
                continue
            print(f"    [DOM] '{sel}' → {len(elems)} element")

            for elem in elems[:30]:
                try:
                    text = elem.inner_text().strip()
                    if not text:
                        text = elem.get_attribute("aria-label") or ""
                    if not text:
                        continue

                    # Türkçe TL formatı: ₺1.450 veya 1.450 TL veya 1450
                    for pat in [
                        r'₺\s*([\d]{1,3}(?:[.,][\d]{3})+)',
                        r'₺\s*(\d{4,6})',
                        r'([\d]{1,3}(?:[.,][\d]{3})+)\s*TL',
                        r'([\d]{1,3}(?:[.,][\d]{3})+)\s*₺',
                    ]:
                        m = re.search(pat, text)
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

            if results:
                # Duplicate temizle
                seen = set()
                unique = []
                for r in results:
                    if r["price"] not in seen:
                        seen.add(r["price"])
                        unique.append(r)
                return sorted(unique, key=lambda x: x["price"])

        except Exception as e:
            print(f"    [DOM] '{sel}' hata: {e}")
            continue

    return []

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
    print(f"PROJECT TITAN v6.0 (Playwright) — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Direkt eşik   : hedefin %{round(DIRECT_THRESHOLD*100)}'i altı")
    print(f"Aktarmalı eşik: hedefin %{round(STOPOVER_THRESHOLD*100)}'i altı (%90 indirim)")
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
                        print(f"  [⏸] Veri eski, alarm yok")
                        continue
                    ok, reason = can_send_alarm(route, price, target)
                    if ok:
                        print(f"  [🔔] ALARM! Telegram...")
                        send_telegram(format_message(origin, dest, dep, ret, price, airline, target, stop))
                        record_alarm(route, price)
                        alarms_sent += 1
                    else:
                        print(f"  [⏸] {reason}")

            sleep_s = random.uniform(8, 15)
            print(f"  [⏳] {sleep_s:.1f}s bekleniyor (rate limit)...")
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
