#!/usr/bin/env python3
"""
PROJECT TITAN v5.4
Alarm kuralları:
- Direkt uçuş: hedefin %50'sinden ucuz olmalı (MISTAKE_THRESHOLD)
- Aktarmalı uçuş: hedefin %10'undan ucuz olmalı (%90 indirim = STOPOVER_THRESHOLD)
- Günlük limit YOK — şarta uyan her uçuş alarm verir
- Aynı rota + aynı fiyat seviyesi 24s içinde tekrar alarm vermez
"""

import json
import re
import random
import urllib.request
import urllib.parse
import gzip
import zlib
import time
from datetime import datetime, timedelta
from pathlib import Path

BOT_TOKEN = "8161806410:AAH4tGpW_kCvQpLOfaB-r2OYQMypPVYtuYg"
ADMIN_ID  = "7684228928"
GROUP_ID  = "-1003515302846"

TARGET_PRICES = {
    "IST-CDG": 3000, "IST-LHR": 3200, "IST-AMS": 2800,
    "IST-BCN": 2900, "IST-FCO": 2600, "IST-MAD": 3100,
    "IST-FRA": 2700, "IST-MUC": 2500, "IST-VIE": 2400,
    "IST-PRG": 2600, "IST-ATH": 1800, "IST-DXB": 2200,
    "IST-JFK": 18000, "IST-LAX": 20000,
    "SAW-CDG": 2800, "SAW-LHR": 3000, "SAW-AMS": 2600,
    "SAW-BCN": 2700, "SAW-FCO": 2400,
}

# ============================================================
# ALARM EŞİKLERİ
# Direkt uçuş  → hedefin %50'si altı (yeşil alanın ortası/dibi)
# Aktarmalı    → hedefin %10'u altı  (%90 indirim — çok istisnai)
# ============================================================
DIRECT_THRESHOLD   = 0.50   # Direkt uçuş alarm eşiği
STOPOVER_THRESHOLD = 0.10   # Aktarmalı uçuş alarm eşiği (%90 indirim)
MAX_DATA_AGE_HOURS = 3      # 3 saatten eski veri → alarm yok

ROUTES = list(TARGET_PRICES.keys())

SCHENGEN = {"CDG","ORY","AMS","EIN","BCN","MAD","FCO","MXP","LIN","FRA","MUC",
            "TXL","BER","VIE","PRG","ATH","SKG","LIS","ARN","GOT","CPH","HEL",
            "OSL","ZUR","GVA","BRU","WAW","KRK","BUD","SOF","OTP","RIX","TLL","VNO","LJU","SKP"}
VISA_WARN = {"LHR","LGW","STN","MAN","JFK","LAX","ORD","MIA","SFO","BOS","IAD","YYZ","YVR"}

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

def build_google_flights_url(origin, dest, dep, ret):
    q = urllib.parse.quote(f"{origin} to {dest} {dep} {ret}")
    return f"https://www.google.com/travel/flights?hl=tr&curr=TRY&gl=TR&q={q}"

# ============================================================
# ALARM MANTIĞI
# ============================================================
def should_alarm(price, target, has_stopover):
    """
    Direkt uçuş : fiyat hedefin %50'sinden ucuz mı?
    Aktarmalı   : fiyat hedefin %10'undan ucuz mı? (%90 indirim)
    """
    if has_stopover:
        return price <= target * STOPOVER_THRESHOLD, "aktarmalı-%90"
    else:
        return price <= target * DIRECT_THRESHOLD, "direkt-%50"

def is_mistake_fare(price, target, has_stopover):
    """Mesaj başlığı için: aktarmalı ise zaten çok istisnai, direkt ise %50 altı."""
    return should_alarm(price, target, has_stopover)[0]

# ============================================================
# HTTP FETCH
# ============================================================
UAS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
]

def fetch_url(url):
    req = urllib.request.Request(url)
    req.add_header("User-Agent", random.choice(UAS))
    req.add_header("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
    req.add_header("Accept-Language", "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7")
    req.add_header("Accept-Encoding", "gzip, deflate")
    req.add_header("Cache-Control", "no-cache")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read()
            encoding = resp.headers.get("Content-Encoding", "")
            final_url = resp.url
            print(f"    [GF] HTTP {resp.status} | {len(raw):,} byte | {final_url[:70]}")
            if encoding == "gzip":
                raw = gzip.decompress(raw)
            elif encoding == "deflate":
                try: raw = zlib.decompress(raw)
                except: raw = zlib.decompress(raw, -15)
            return raw.decode("utf-8", errors="replace"), final_url
    except Exception as e:
        print(f"    [GF HATA] {e}")
        return None, None

def has_stopover(html):
    keywords = ["aktarma","aktarmalı","bağlantı","stopover","layover",
                "connecting","1 stop","2 stop","1 durak","2 durak"]
    lower = html.lower()
    return any(kw in lower for kw in keywords)

# ============================================================
# SANİTY CHECK
# ============================================================
BOUNDS = {
    "IST-CDG":(200,15000), "IST-LHR":(200,16000), "IST-AMS":(200,14000),
    "IST-BCN":(200,14000), "IST-FCO":(200,13000), "IST-MAD":(200,15000),
    "IST-FRA":(200,13000), "IST-MUC":(200,13000), "IST-VIE":(200,12000),
    "IST-PRG":(200,13000), "IST-ATH":(100,10000),  "IST-DXB":(200,12000),
    "IST-JFK":(1000,80000),"IST-LAX":(1000,90000),
    "SAW-CDG":(200,15000), "SAW-LHR":(200,16000), "SAW-AMS":(200,14000),
    "SAW-BCN":(200,14000), "SAW-FCO":(200,13000),
}

def sanity_check(price, route):
    mn, mx = BOUNDS.get(route, (500, 200000))
    return mn <= price <= mx

def is_fresh(scraped_at):
    if not scraped_at: return True
    return (datetime.now() - scraped_at).total_seconds() < MAX_DATA_AGE_HOURS * 3600

# ============================================================
# FİYAT PARSE
# ============================================================
def extract_prices(html, route):
    mn, mx = BOUNDS.get(route, (500, 200000))
    found = []

    # Yöntem 1: ₺ sembolü yanındaki sayılar — en güvenilir
    for m in re.finditer(r'₺\s*([\d]{1,3}(?:[.,][\d]{3})*|[\d]+)', html):
        raw = m.group(1).replace(".", "").replace(",", "")
        try:
            price = float(raw)
            if mn <= price <= mx:
                found.append(price)
        except ValueError:
            pass

    if found:
        found = sorted(set(found))
        print(f"    [PARSE] ₺ yöntemi: {found[:5]}")
        return found[:3]

    # Yöntem 2: JSON TRY formatı
    json_prices = []
    for m in re.finditer(r'"(\d{4,6})"\s*,\s*"TRY"', html):
        try:
            p = float(m.group(1))
            if mn <= p <= mx: json_prices.append(p)
        except: pass

    for m in re.finditer(r'\[null,null,(\d{4,6})[,\]]', html):
        try:
            p = float(m.group(1))
            if mn <= p <= mx: json_prices.append(p)
        except: pass

    if json_prices:
        json_prices = sorted(set(json_prices))
        print(f"    [PARSE] JSON yöntemi: {json_prices[:5]}")
        return json_prices[:3]

    print(f"    [PARSE] Fiyat bulunamadı ({mn}-{mx} TL aralığı)")
    tl_idx = html.find("₺")
    if tl_idx >= 0:
        print(f"    [DEBUG] ₺ bağlamı: {repr(html[max(0,tl_idx-5):tl_idx+25])}")
    else:
        pattern = r'\b\d{4,5}\b'
        print(f"    [DEBUG] 4-5 haneli sayılar: {re.findall(pattern, html)[:8]}")
    return []

def fetch_google_flights_sync(origin, dest, dep_date, ret_date):
    # Önce direkt (nonstop=1&stops=0) dene
    url = (f"https://www.google.com/travel/flights"
           f"?hl=tr&curr=TRY&gl=TR"
           f"&q={origin}+to+{dest}+{dep_date}+{ret_date}"
           f"&nonstop=1&stops=0")
    route = f"{origin}-{dest}"
    print(f"    [GF] {route} {dep_date} → direkt sorgu...")

    html, resp_url = fetch_url(url)
    if not html:
        return []
    if resp_url and "/sorry/" in resp_url:
        print(f"    [GF] CAPTCHA redirect"); return []
    if "detected unusual traffic" in html.lower():
        print(f"    [GF] Unusual traffic"); return []

    page_stopover = has_stopover(html)
    if page_stopover:
        print(f"    [GF] ⚠️ Direkt sorguda aktarma belirtisi var")

    prices = extract_prices(html, route)
    if not prices:
        return []

    scraped_at = datetime.now()
    return [{
        "price": p,
        "airline": "Çeşitli",
        "stops": 1 if page_stopover else 0,
        "source": "google_flights",
        "scraped_at": scraped_at,
        "has_stopover": page_stopover,
    } for p in prices]

# ============================================================
# HISTORY — günlük limit YOK
# Sadece aynı rota+fiyat_seviyesi 24s içinde tekrar alarm vermez
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
    # 30 günden eski kayıtları temizle
    cutoff30 = (datetime.now() - timedelta(days=30)).isoformat()
    h["alarms"] = [a for a in h.get("alarms", []) if a.get("time", "") > cutoff30]

    # Aynı rota için 24s içinde aynı fiyat bandında alarm gitti mi?
    # Fiyat bandı: %5 tolerans (örn. 1500 TL ile 1520 TL aynı band)
    cutoff24 = (datetime.now() - timedelta(hours=24)).isoformat()
    band_low  = price * 0.95
    band_high = price * 1.05
    recent = [
        a for a in h.get("alarms", [])
        if a.get("route") == route
        and a.get("time", "") > cutoff24
        and band_low <= a.get("price", 0) <= band_high
    ]
    if recent:
        return False, f"{route} aynı fiyat bandında 24s içinde alarm gönderildi"
    return True, "OK"

def record_alarm(route, price):
    h = load_history()
    h.setdefault("alarms", []).append({
        "route": route,
        "price": price,
        "time": datetime.now().isoformat(),
    })
    save_history(h)

# ============================================================
# TELEGRAM
# ============================================================
def send_telegram_sync(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    for cid in [ADMIN_ID, GROUP_ID]:
        try:
            data = json.dumps({
                "chat_id": cid, "text": msg,
                "parse_mode": "HTML",
                "disable_web_page_preview": False,
            }).encode()
            req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=15) as r:
                print(f"  [Telegram ✓] {cid}" if r.status == 200 else f"  [Telegram HATA] {r.status}")
        except Exception as e:
            print(f"  [Telegram ERR] {e}")

def format_message(origin, dest, dep, ret, price, airline, target, has_stop):
    pct = round((1 - price / target) * 100)
    link = build_google_flights_url(origin, dest, dep, ret)
    ucus_turu = "🔄 Aktarmalı" if has_stop else "✈️ Direkt"

    if has_stop:
        header = "🚨 <b>AKTARMALI – EXTREME FARE ALARMI</b> ⚡"
        note   = f"⚡ Aktarmalı ama hedefin <b>%{pct} altında!</b> — İstisnai fiyat."
    else:
        header = "🦅 <b>DİP FİYAT ALARMI</b> 💎"
        note   = f"📊 Direkt uçuş, hedefin <b>%{pct} altında!</b>"

    return (
        f"{header}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{ucus_turu} <b>Rota:</b> {origin} ➔ {dest}\n"
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
    print(f"PROJECT TITAN v5.4 – {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Direkt alarm eşiği  : hedefin %{round(DIRECT_THRESHOLD*100)}'i altı")
    print(f"Aktarmalı alarm eşiği: hedefin %{round(STOPOVER_THRESHOLD*100)}'i altı (%90 indirim)")
    print(f"Günlük limit        : YOK")
    print(f"{'='*60}\n")

    all_flights = []
    search_dates = get_search_dates()

    for route in ROUTES:
        origin, dest = route.split("-")
        target = TARGET_PRICES[route]
        print(f"\n[ROTA] {route} | Hedef: {target:,} TL")
        print(f"         Direkt eşik: {target*DIRECT_THRESHOLD:,.0f} TL | Aktarmalı eşik: {target*STOPOVER_THRESHOLD:,.0f} TL")

        for dep, ret in random.sample(search_dates, min(2, len(search_dates))):
            print(f"  [Tarih] {dep} → {ret}")
            flights = fetch_google_flights_sync(origin, dest, dep, ret)
            glink   = build_google_flights_url(origin, dest, dep, ret)

            if not flights:
                print(f"  [!] Veri yok")
                all_flights.append({
                    "route": route, "origin": origin, "dest": dest,
                    "depart_date": dep, "return_date": ret, "price": None,
                    "airline": "Veri yok", "target": target,
                    "alarm_threshold": round(target * DIRECT_THRESHOLD),
                    "savings_pct": None, "is_below_target": False, "is_mistake_fare": False,
                    "google_link": glink,
                    "scraped_at": datetime.now().isoformat(), "data_source": "no_results"
                })
                time.sleep(random.uniform(3, 7))
                continue

            for f in flights:
                price      = f["price"]
                airline    = f["airline"]
                scraped_at = f.get("scraped_at")
                stop       = f.get("has_stopover", False)

                if not sanity_check(price, route):
                    print(f"  [!] Sanity FAIL: {price:,.0f} TL"); continue

                alarm_ok, alarm_type = should_alarm(price, target, stop)
                pct = round((1 - price / target) * 100)
                stop_label = "🔄aktarmalı" if stop else "✈️direkt"
                alarm_label = f"🚨{alarm_type}" if alarm_ok else ""
                print(f"  [✓] {price:,.0f} TL | {stop_label} | -%{pct} {alarm_label}")

                all_flights.append({
                    "route": route, "origin": origin, "dest": dest,
                    "depart_date": dep, "return_date": ret, "price": price,
                    "airline": airline, "target": target,
                    "alarm_threshold": round(target * DIRECT_THRESHOLD),
                    "savings_pct": pct,
                    "is_below_target": alarm_ok,
                    "is_mistake_fare": stop,   # aktarmalıysa farklı gösterim
                    "has_stopover": stop,
                    "google_link": glink,
                    "scraped_at": scraped_at.isoformat() if scraped_at else datetime.now().isoformat(),
                    "data_source": f.get("source", "google_flights")
                })

                if alarm_ok:
                    if not is_fresh(scraped_at):
                        print(f"  [⏸] Veri {MAX_DATA_AGE_HOURS}s'den eski"); continue
                    ok, reason = can_send_alarm(route, price, target)
                    if ok:
                        print(f"  [🔔] Telegram gönderiliyor...")
                        send_telegram_sync(
                            format_message(origin, dest, dep, ret, price, airline, target, stop)
                        )
                        record_alarm(route, price)
                    else:
                        print(f"  [⏸] {reason}")

            time.sleep(random.uniform(4, 9))

    valid   = [f for f in all_flights if f.get("price") is not None]
    no_data = [f for f in all_flights if f.get("price") is None]

    output = {
        "last_updated": datetime.now().isoformat(),
        "total_found": len(valid),
        "below_target": sum(1 for f in valid if f.get("is_below_target")),
        "direct_threshold_pct": round((1 - DIRECT_THRESHOLD) * 100),
        "stopover_threshold_pct": round((1 - STOPOVER_THRESHOLD) * 100),
        "data_source": "google_flights_urllib",
        "flights": sorted(valid, key=lambda x: x["price"]) + no_data,
    }
    Path("flights.json").write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n{'='*60}")
    print(f"[✓] {len(valid)} geçerli uçuş | {output['below_target']} alarm eşiği altı")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    run_scraper()
