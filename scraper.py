#!/usr/bin/env python3
"""
PROJECT TITAN v5.1 – Google Flights HTTP Scraper
urllib kullanılır, sıkıştırma yok (identity), binary sorun yok.
"""

import asyncio
import json
import re
import random
import urllib.request
import urllib.parse
import gzip
import zlib
from datetime import datetime, timedelta
from pathlib import Path

# ============================================================
# GLOBAL KİMLİK BİLGİLERİ
# ============================================================
BOT_TOKEN = "8161806410:AAH4tGpW_kCvQpLOfaB-r2OYQMypPVYtuYg"
ADMIN_ID  = "7684228928"
GROUP_ID  = "-1003515302846"

# ============================================================
# HEDEF FİYATLAR (TL)
# ============================================================
TARGET_PRICES = {
    "IST-CDG": 3000, "IST-LHR": 3200, "IST-AMS": 2800,
    "IST-BCN": 2900, "IST-FCO": 2600, "IST-MAD": 3100,
    "IST-FRA": 2700, "IST-MUC": 2500, "IST-VIE": 2400,
    "IST-PRG": 2600, "IST-ATH": 1800, "IST-DXB": 2200,
    "IST-JFK": 18000, "IST-LAX": 20000,
    "SAW-CDG": 2800, "SAW-LHR": 3000, "SAW-AMS": 2600,
    "SAW-BCN": 2700, "SAW-FCO": 2400,
}

ALARM_THRESHOLD   = 0.85
MISTAKE_THRESHOLD = 0.50
ROUTES = list(TARGET_PRICES.keys())

# ============================================================
# VİZE
# ============================================================
SCHENGEN = {"CDG","ORY","AMS","EIN","BCN","MAD","FCO","MXP","LIN","FRA","MUC",
            "TXL","BER","VIE","PRG","ATH","SKG","LIS","ARN","GOT","CPH","HEL",
            "OSL","ZUR","GVA","BRU","WAW","KRK","BUD","SOF","OTP","RIX","TLL","VNO","LJU","SKP"}
VISA_WARN = {"LHR","LGW","STN","MAN","JFK","LAX","ORD","MIA","SFO","BOS","IAD","YYZ","YVR"}

def get_visa_status(dest):
    if dest.upper() in SCHENGEN: return "✅ VİZESİZ (Schengen – Yeşil Pasaport)"
    if dest.upper() in VISA_WARN: return "⚠️ VİZE GEREKLİ (UK/ABD/Kanada)"
    return "ℹ️ Vize durumu kontrol edilmeli"

# ============================================================
# TARİHLER
# ============================================================
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
    return f"https://www.google.com/travel/flights?hl=tr&curr=TRY&gl=TR&q={origin}+to+{dest}+{dep}+{ret}"

# ============================================================
# HTTP FETCH — urllib ile, sıkıştırmasız
# ============================================================
UAS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
]

def fetch_url(url):
    """Senkron urllib fetch — sıkıştırmasız, güvenli decode."""
    req = urllib.request.Request(url)
    req.add_header("User-Agent", random.choice(UAS))
    req.add_header("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
    req.add_header("Accept-Language", "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7")
    # Sıkıştırma KAPALIYKEN gzip istiyoruz — urllib bunu otomatik açar
    req.add_header("Accept-Encoding", "gzip, deflate")
    req.add_header("Cache-Control", "no-cache")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read()
            encoding = resp.headers.get("Content-Encoding", "")
            print(f"    [GF] HTTP {resp.status} | encoding={encoding} | {len(raw):,} byte")

            # Manuel decompress
            if encoding == "gzip":
                raw = gzip.decompress(raw)
            elif encoding == "deflate":
                raw = zlib.decompress(raw)
            # br (brotli) — stdlib yok, skip

            html = raw.decode("utf-8", errors="replace")
            return html
    except Exception as e:
        print(f"    [GF HATA] {e}")
        return None


def fetch_google_flights_sync(origin, dest, dep_date, ret_date):
    """Google Flights'tan fiyat çek — senkron."""
    url = f"https://www.google.com/travel/flights?hl=tr&curr=TRY&gl=TR&q={origin}+to+{dest}+{dep_date}+{ret_date}&nonstop=1"
    print(f"    [GF] {origin}->{dest} {dep_date} sorgulanıyor...")

    html = fetch_url(url)
    if not html:
        return []

    print(f"    [GF] HTML başlangıcı: {repr(html[:80])}")

    if any(x in html.lower() for x in ["captcha", "unusual traffic", "/sorry/"]):
        print(f"    [GF] ⚠️ Bot tespiti")
        return []

    prices = extract_prices(html)
    if prices:
        print(f"    [GF ✓] Fiyatlar: {[f'{p:,.0f}₺' for p in prices[:5]]}")
        return [{"price": p, "airline": "Çeşitli", "stops": 0, "source": "google_flights"} for p in prices[:3]]
    else:
        print(f"    [GF] Fiyat bulunamadı")
        # Daha fazla debug bilgisi
        idx = html.find("₺")
        if idx >= 0:
            print(f"    [GF DEBUG] ₺ bulundu: {repr(html[idx-5:idx+20])}")
        else:
            print(f"    [GF DEBUG] ₺ sembolü hiç yok. İlk 200: {repr(html[:200])}")
        return []


def extract_prices(html):
    """Google Flights HTML'inden TRY fiyatlarını çıkar."""
    found = set()

    # 1) ₺ sembolü
    for m in re.finditer(r'₺\s*([\d.,]+)', html):
        try:
            price = float(m.group(1).replace(".", "").replace(",", ""))
            if 500 <= price <= 200000:
                found.add(price)
        except ValueError:
            pass

    # 2) "SAYI","TRY" formatı
    for m in re.finditer(r'"(\d{4,6})"\s*,\s*"TRY"', html):
        try: found.add(float(m.group(1)))
        except: pass

    # 3) "TRY",SAYI
    for m in re.finditer(r'"TRY"\s*,\s*(\d{4,6})\b', html):
        try: found.add(float(m.group(1)))
        except: pass

    # 4) [null,null,SAYI
    for m in re.finditer(r'\[null,null,(\d{4,6}),', html):
        try: found.add(float(m.group(1)))
        except: pass

    # 5) data-price veya itemprop
    for m in re.finditer(r'(?:data-price|content)="(\d{3,6})"', html):
        try:
            p = float(m.group(1))
            if 800 <= p <= 100000:
                found.add(p)
        except: pass

    return sorted(found)

# ============================================================
# SANİTY CHECK
# ============================================================
BOUNDS = {
    "IST-CDG":(1500,15000), "IST-LHR":(1500,16000), "IST-AMS":(1500,14000),
    "IST-BCN":(1500,14000), "IST-FCO":(1200,13000), "IST-MAD":(1500,15000),
    "IST-FRA":(1200,13000), "IST-MUC":(1200,13000), "IST-VIE":(1200,12000),
    "IST-PRG":(1200,13000), "IST-ATH":(800,10000),  "IST-DXB":(1000,12000),
    "IST-JFK":(10000,80000),"IST-LAX":(12000,90000),
    "SAW-CDG":(1500,15000), "SAW-LHR":(1500,16000), "SAW-AMS":(1500,14000),
    "SAW-BCN":(1500,14000), "SAW-FCO":(1200,13000),
}
def sanity_check(price, route):
    mn, mx = BOUNDS.get(route, (500, 200000))
    return mn <= price <= mx

def is_mistake_fare(p, t): return p <= t * MISTAKE_THRESHOLD
def is_below_alarm(p, t):  return p < t * ALARM_THRESHOLD

# ============================================================
# HISTORY
# ============================================================
HFILE = Path("history.json")

def load_history():
    if HFILE.exists():
        try: return json.loads(HFILE.read_text(encoding="utf-8"))
        except: pass
    return {"alarms": [], "daily_count": 0, "daily_date": ""}

def save_history(h):
    HFILE.write_text(json.dumps(h, ensure_ascii=False, indent=2), encoding="utf-8")

def can_send_alarm(route, price, target):
    h = load_history()
    today = datetime.now().strftime("%Y-%m-%d")
    if h.get("daily_date") != today:
        h["daily_count"] = 0; h["daily_date"] = today
        cutoff = (datetime.now() - timedelta(days=30)).isoformat()
        h["alarms"] = [a for a in h.get("alarms",[]) if a.get("time","") > cutoff]
    if h.get("daily_count", 0) >= 3: return False, "Günlük 3 limit"
    cutoff24 = (datetime.now() - timedelta(hours=24)).isoformat()
    if any(a.get("route")==route and a.get("time","")>cutoff24 for a in h.get("alarms",[])):
        return False, f"{route} 24s içinde alarm gönderildi"
    return True, "OK"

def record_alarm(route):
    h = load_history()
    today = datetime.now().strftime("%Y-%m-%d")
    if h.get("daily_date") != today: h["daily_count"]=0; h["daily_date"]=today
    h["daily_count"] = h.get("daily_count",0) + 1
    h.setdefault("alarms",[]).append({"route":route,"time":datetime.now().isoformat()})
    save_history(h)

# ============================================================
# TELEGRAM
# ============================================================
def send_telegram_sync(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    for cid in [ADMIN_ID, GROUP_ID]:
        try:
            data = json.dumps({"chat_id":cid,"text":msg,"parse_mode":"HTML","disable_web_page_preview":False}).encode()
            req = urllib.request.Request(url, data=data, headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req, timeout=15) as r:
                print(f"  [Telegram ✓] {cid}" if r.status==200 else f"  [Telegram HATA] {r.status}")
        except Exception as e:
            print(f"  [Telegram ERR] {e}")

def format_message(origin, dest, dep, ret, price, airline, target):
    pct = round((1 - price/target)*100)
    mistake = is_mistake_fare(price, target)
    link = build_google_flights_url(origin, dest, dep, ret)
    header = "🚨 <b>MISTAKE FARE ALARMI</b> ⚡" if mistake else "🦅 <b>DİP FİYAT ALARMI</b> 💎"
    note = f"⚡ MISTAKE FARE! Hedefin %{pct} altında!" if mistake else f"📊 Hedefin %{pct} altında!"
    return (f"{header}\n━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"✈️ <b>Rota:</b> {origin} ➔ {dest}\n📅 <b>Gidiş:</b> {dep}\n📅 <b>Dönüş:</b> {ret}\n"
            f"💰 <b>Fiyat:</b> {price:,.0f} TL\n🎯 <b>Hedef:</b> {target:,.0f} TL\n"
            f"🏷️ <b>Havayolu:</b> {airline}\n{note}\n"
            f"🌍 <b>Vize:</b> {get_visa_status(dest)}\n━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f'🔍 <a href="{link}">Google Flights\'ta Ara</a>\n⚡ HEMEN AL!')

# ============================================================
# ANA MOTOR
# ============================================================
def run_scraper():
    print(f"\n{'='*60}")
    print(f"PROJECT TITAN v5.1 – {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Motor: Google Flights urllib (sıkıştırmasız, güvenli)")
    print(f"{'='*60}\n")

    all_flights = []
    search_dates = get_search_dates()

    for route in ROUTES:
        origin, dest = route.split("-")
        target = TARGET_PRICES[route]
        alarm_p = target * ALARM_THRESHOLD
        print(f"\n[ROTA] {route} | Hedef: {target:,} TL | Eşik: {alarm_p:,.0f} TL")

        for dep, ret in random.sample(search_dates, min(2, len(search_dates))):
            print(f"  [Tarih] {dep} → {ret}")
            flights = fetch_google_flights_sync(origin, dest, dep, ret)
            glink = build_google_flights_url(origin, dest, dep, ret)

            if not flights:
                print(f"  [!] Veri yok")
                all_flights.append({
                    "route":route,"origin":origin,"dest":dest,
                    "depart_date":dep,"return_date":ret,"price":None,
                    "airline":"Veri yok","target":target,"alarm_threshold":round(alarm_p),
                    "savings_pct":None,"is_below_target":False,"is_mistake_fare":False,
                    "google_link":glink,"scraped_at":datetime.now().isoformat(),"data_source":"no_results"
                })
                import time; time.sleep(random.uniform(3,7))
                continue

            for f in flights:
                price, airline = f["price"], f["airline"]
                if not sanity_check(price, route):
                    print(f"  [!] Sanity FAIL: {price:,.0f} TL")
                    continue
                below = is_below_alarm(price, target)
                mistake = is_mistake_fare(price, target)
                label = "🚨 MISTAKE" if mistake else ("🎯 ALARM" if below else "")
                print(f"  [✓] {price:,.0f} TL | {airline} {label}")
                all_flights.append({
                    "route":route,"origin":origin,"dest":dest,
                    "depart_date":dep,"return_date":ret,"price":price,
                    "airline":airline,"target":target,"alarm_threshold":round(alarm_p),
                    "savings_pct":round((1-price/target)*100),
                    "is_below_target":below,"is_mistake_fare":mistake,
                    "google_link":glink,"scraped_at":datetime.now().isoformat(),
                    "data_source":f.get("source","google_flights")
                })
                if below or mistake:
                    ok, reason = can_send_alarm(route, price, target)
                    if ok:
                        print(f"  [🔔] Telegram gönderiliyor...")
                        send_telegram_sync(format_message(origin,dest,dep,ret,price,airline,target))
                        record_alarm(route)
                    else:
                        print(f"  [⏸] {reason}")

            import time; time.sleep(random.uniform(4, 9))

    valid = [f for f in all_flights if f.get("price") is not None]
    no_data = [f for f in all_flights if f.get("price") is None]

    output = {
        "last_updated": datetime.now().isoformat(),
        "total_found": len(valid),
        "below_target": sum(1 for f in valid if f.get("is_below_target")),
        "alarm_threshold_pct": round((1-ALARM_THRESHOLD)*100),
        "data_source": "google_flights_urllib",
        "flights": sorted(valid, key=lambda x: x["price"]) + no_data,
    }
    Path("flights.json").write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n{'='*60}")
    print(f"[✓] {len(valid)} geçerli uçuş | {output['below_target']} alarm eşiği altı")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    run_scraper()
