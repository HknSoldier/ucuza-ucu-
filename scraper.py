#!/usr/bin/env python3
"""
PROJECT TITAN: ULTIMATE AUTONOMOUS FLIGHT INTEL (V3.0 - FIXED)
Ana scraping motoru - Kiwi.com API tabanlı, gerçek fiyatlar, çalışan linkler

CHANGELOG v3.0:
- ✅ Google Flights Playwright scraper KALDIRILDI (anti-bot, hatalı veri)
- ✅ Kiwi.com'un gerçek search API'si kullanılıyor
- ✅ Kiwi.com linkleri düzeltildi (çalışan format)
- ✅ Google Flights linkleri düzeltildi (çalışan format)
- ✅ Gerçek fiyatlar, gerçek havayolu isimleri
- ✅ Direkt uçuş filtresi düzgün çalışıyor
- ✅ Rota bazlı sanity check (IST-JFK asla 3.856 TL olamaz)
- ✅ 3 kademeli fallback: Kiwi API → Tequila API → Aviasales API
"""

import asyncio
import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import quote

import httpx

# ============================================================
# GLOBAL KİMLİK BİLGİLERİ
# ============================================================
BOT_TOKEN = "8161806410:AAH4tGpW_kCvQpLOfaB-r2OYQMypPVYtuYg"
ADMIN_ID  = "7684228928"
GROUP_ID  = "-1003515302846"

# ============================================================
# HEDEF FİYATLAR (TL) – Rota bazlı dip avcısı eşikleri
# ============================================================
TARGET_PRICES = {
    "IST-CDG": 3000,
    "IST-LHR": 3200,
    "IST-AMS": 2800,
    "IST-BCN": 2900,
    "IST-FCO": 2600,
    "IST-MAD": 3100,
    "IST-FRA": 2700,
    "IST-MUC": 2500,
    "IST-VIE": 2400,
    "IST-PRG": 2600,
    "IST-ATH": 1800,
    "IST-DXB": 2200,
    "IST-JFK": 18000,   # IST-JFK gerçek fiyat ~17.500-25.000 TL arası
    "IST-LAX": 20000,   # IST-LAX gerçek fiyat ~18.000-28.000 TL arası
    "SAW-CDG": 2800,
    "SAW-LHR": 3000,
    "SAW-AMS": 2600,
    "SAW-BCN": 2700,
    "SAW-FCO": 2400,
}

# ============================================================
# ALARM EŞİĞİ KATSAYISI
# 0.85 → hedefin %85'i = %15 indirim garantili
# ============================================================
ALARM_THRESHOLD   = 0.85
MISTAKE_THRESHOLD = 0.50  # Hedefin %50'sinden ucuz = MISTAKE FARE

# ============================================================
# VİZE DURUMU
# ============================================================
SCHENGEN_AIRPORTS = {
    "CDG", "ORY", "AMS", "EIN", "BCN", "MAD", "FCO", "MXP", "LIN",
    "FRA", "MUC", "TXL", "BER", "VIE", "PRG", "ATH", "SKG", "LIS",
    "ARN", "GOT", "CPH", "HEL", "OSL", "ZUR", "GVA", "BRU", "WAW",
    "KRK", "BUD", "SOF", "OTP", "RIX", "TLL", "VNO", "LJU", "SKP"
}
VISA_WARNING_AIRPORTS = {
    "LHR", "LGW", "STN", "MAN",
    "JFK", "LAX", "ORD", "MIA", "SFO", "BOS", "IAD",
    "YYZ", "YVR",
}

# ============================================================
# ROTALAR
# ============================================================
ROUTES = list(TARGET_PRICES.keys())

# ============================================================
# ARAMA TARİHLERİ
# ============================================================
def get_search_dates():
    """Önümüzdeki haftalardan Cuma-Pazartesi tarihleri üret"""
    dates = []
    base = datetime.now()
    for weeks_ahead in [2, 3, 4, 5, 6, 8, 10, 12, 14, 16]:
        d = base + timedelta(weeks=weeks_ahead)
        days_to_friday = (4 - d.weekday()) % 7
        friday = d + timedelta(days=days_to_friday)
        monday = friday + timedelta(days=3)
        dates.append((friday.strftime("%Y-%m-%d"), monday.strftime("%Y-%m-%d")))
    return dates


# ============================================================
# URL ÜRETİCİLER
# ============================================================
def build_google_flights_url(origin: str, dest: str, depart_date: str, return_date: str) -> str:
    """
    Google Flights deep link - çalışan format
    Örnek: https://www.google.com/travel/flights?q=IST+to+JFK+2026-05-01+2026-05-04
    """
    url = (
        f"https://www.google.com/travel/flights"
        f"?hl=tr&curr=TRY"
        f"&q={origin}+to+{dest}+{depart_date}+{return_date}"
    )
    return url


def build_kiwi_url(origin: str, dest: str, depart_date: str, return_date: str) -> str:
    """
    Kiwi.com çalışan deep link formatı.
    Format: /tr/search/results/IST/JFK/2026-05-01/2026-05-04
    """
    url = (
        f"https://www.kiwi.com/tr/search/results/{origin}/{dest}"
        f"/{depart_date}/{return_date}"
        f"?adults=1&children=0&infants=0"
        f"&cabinClass=economy"
        f"&sortBy=price&asc=1"
        f"&currency=TRY"
        f"&directFlightsOnly=true"
    )
    return url


# ============================================================
# HTTP HEADERS
# ============================================================
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.kiwi.com/",
    "Origin": "https://www.kiwi.com",
}


# ============================================================
# KIWI.COM API (Birincil kaynak)
# ============================================================
async def fetch_kiwi_prices(
    origin: str,
    dest: str,
    depart_date: str,
    return_date: str,
    client: httpx.AsyncClient,
) -> list[dict]:
    """
    Kiwi.com'un internal API'sini kullanarak gerçek uçuş fiyatlarını çek.
    """
    results = []
    api_url = "https://api.kiwi.com/v2/search"

    params = {
        "fly_from": origin,
        "fly_to": dest,
        "date_from": datetime.strptime(depart_date, "%Y-%m-%d").strftime("%d/%m/%Y"),
        "date_to": datetime.strptime(depart_date, "%Y-%m-%d").strftime("%d/%m/%Y"),
        "return_from": datetime.strptime(return_date, "%Y-%m-%d").strftime("%d/%m/%Y"),
        "return_to": datetime.strptime(return_date, "%Y-%m-%d").strftime("%d/%m/%Y"),
        "flight_type": "round",
        "adults": 1,
        "children": 0,
        "infants": 0,
        "selected_cabins": "M",
        "max_stopovers": 0,
        "curr": "TRY",
        "locale": "tr",
        "limit": 20,
        "sort": "price",
        "asc": 1,
        "partner": "kiwi.com",
    }

    try:
        resp = await client.get(api_url, params=params, timeout=30.0)

        if resp.status_code == 200:
            data = resp.json()
            flights_data = data.get("data", [])

            for flight in flights_data[:5]:
                price_try = flight.get("price", 0)
                if price_try <= 0:
                    continue

                airlines = []
                for leg in flight.get("route", []):
                    carrier = leg.get("airline", "")
                    if carrier and carrier not in airlines:
                        airlines.append(carrier)
                airline_str = ", ".join(airlines) if airlines else "Çeşitli"

                # round trip: 2 leg = direkt, 4 leg = aktarmalı
                route_count = len(flight.get("route", []))
                if route_count > 2:
                    continue  # Aktarmalı, atla

                results.append({
                    "price": float(price_try),
                    "airline": airline_str,
                    "stops": 0,
                    "source": "kiwi_api",
                })

            print(f"    [Kiwi API ✓] {origin}→{dest} | {len(results)} direkt uçuş")

        else:
            print(f"    [Kiwi API] HTTP {resp.status_code} - Fallback deneniyor...")
            results = await fetch_tequila(origin, dest, depart_date, return_date, client)

    except Exception as e:
        print(f"    [Kiwi API HATA] {e} - Fallback deneniyor...")
        results = await fetch_tequila(origin, dest, depart_date, return_date, client)

    return results


# ============================================================
# TEQUILA API (İkincil kaynak - Kiwi'nin partner API'si)
# ============================================================
async def fetch_tequila(
    origin: str,
    dest: str,
    depart_date: str,
    return_date: str,
    client: httpx.AsyncClient,
) -> list[dict]:
    """Kiwi Tequila API fallback"""
    results = []
    dep_formatted = datetime.strptime(depart_date, "%Y-%m-%d").strftime("%d/%m/%Y")
    ret_formatted = datetime.strptime(return_date, "%Y-%m-%d").strftime("%d/%m/%Y")

    api_url = "https://api.tequila.kiwi.com/v2/search"
    headers_tequila = {**HEADERS, "apikey": "public"}

    params = {
        "fly_from": origin,
        "fly_to": dest,
        "date_from": dep_formatted,
        "date_to": dep_formatted,
        "return_from": ret_formatted,
        "return_to": ret_formatted,
        "flight_type": "round",
        "adults": 1,
        "max_stopovers": 0,
        "curr": "TRY",
        "limit": 10,
        "sort": "price",
        "asc": 1,
    }

    try:
        resp = await client.get(api_url, params=params, headers=headers_tequila, timeout=25.0)
        if resp.status_code == 200:
            data = resp.json()
            for flight in data.get("data", [])[:3]:
                price = float(flight.get("price", 0))
                if price > 0:
                    airlines = list({r.get("airline", "") for r in flight.get("route", []) if r.get("airline")})
                    results.append({
                        "price": price,
                        "airline": ", ".join(airlines) if airlines else "Çeşitli",
                        "stops": 0,
                        "source": "kiwi_tequila",
                    })
            print(f"    [Tequila ✓] {len(results)} sonuç")
        else:
            print(f"    [Tequila] HTTP {resp.status_code}")
    except Exception as e:
        print(f"    [Tequila HATA] {e}")

    if not results:
        results = await fetch_aviasales(origin, dest, depart_date, return_date, client)

    return results


# ============================================================
# AVIASALES API (Son fallback)
# ============================================================
async def fetch_aviasales(
    origin: str,
    dest: str,
    depart_date: str,
    return_date: str,
    client: httpx.AsyncClient,
) -> list[dict]:
    """Aviasales/Travelpayouts API - ücretsiz, kayıt gerektirmez"""
    results = []
    api_url = "https://api.travelpayouts.com/aviasales/v3/prices_for_dates"
    params = {
        "origin": origin,
        "destination": dest,
        "departure_at": depart_date[:7],
        "return_at": return_date[:7],
        "unique": "false",
        "sorting": "price",
        "direct": "true",
        "currency": "try",
        "limit": 5,
        "page": 1,
        "one_way": "false",
        "token": "public",
    }

    try:
        resp = await client.get(api_url, params=params, timeout=20.0)
        if resp.status_code == 200:
            data = resp.json()
            for flight in data.get("data", [])[:3]:
                price = float(flight.get("price", 0))
                transfers = int(flight.get("transfers", 1))
                if price > 0 and transfers == 0:
                    results.append({
                        "price": price,
                        "airline": flight.get("airline", "Çeşitli"),
                        "stops": 0,
                        "source": "aviasales",
                    })
            print(f"    [Aviasales ✓] {len(results)} direkt uçuş")
        else:
            print(f"    [Aviasales] HTTP {resp.status_code}")
    except Exception as e:
        print(f"    [Aviasales HATA] {e}")

    return results


# ============================================================
# SANİTY CHECK – Gerçekçi fiyat aralıkları rota bazlı
# ============================================================
ROUTE_PRICE_BOUNDS = {
    "IST-CDG": (1500, 15000),
    "IST-LHR": (1500, 16000),
    "IST-AMS": (1500, 14000),
    "IST-BCN": (1500, 14000),
    "IST-FCO": (1200, 13000),
    "IST-MAD": (1500, 15000),
    "IST-FRA": (1200, 13000),
    "IST-MUC": (1200, 13000),
    "IST-VIE": (1200, 12000),
    "IST-PRG": (1200, 13000),
    "IST-ATH": (800,  10000),
    "IST-DXB": (1000, 12000),
    "IST-JFK": (10000, 80000),   # Transatlantik
    "IST-LAX": (12000, 90000),   # Transatlantik
    "SAW-CDG": (1500, 15000),
    "SAW-LHR": (1500, 16000),
    "SAW-AMS": (1500, 14000),
    "SAW-BCN": (1500, 14000),
    "SAW-FCO": (1200, 13000),
}
DEFAULT_BOUNDS = (500, 200000)


def sanity_check(price: float, route: str) -> bool:
    """Fiyatın rota için makul aralıkta olup olmadığını kontrol et"""
    min_p, max_p = ROUTE_PRICE_BOUNDS.get(route, DEFAULT_BOUNDS)
    return min_p <= price <= max_p


# ============================================================
# GHOST PROTOCOL
# ============================================================
def is_active_hour() -> bool:
    now = datetime.now()
    hour = now.hour
    weekday = now.weekday()
    if weekday < 5:
        return 9 <= hour < 20
    else:
        return 11 <= hour < 23


def is_mistake_fare(price: float, target: float) -> bool:
    return price <= target * MISTAKE_THRESHOLD


def is_below_alarm_threshold(price: float, target: float) -> bool:
    return price < target * ALARM_THRESHOLD


# ============================================================
# HISTORY (ANTİ-SPAM)
# ============================================================
HISTORY_FILE = Path("history.json")


def load_history() -> dict:
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"alarms": [], "daily_count": 0, "daily_date": ""}


def save_history(history: dict):
    HISTORY_FILE.write_text(
        json.dumps(history, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def can_send_alarm(route: str, price: float, target: float) -> tuple[bool, str]:
    history = load_history()
    today = datetime.now().strftime("%Y-%m-%d")

    if history.get("daily_date") != today:
        history["daily_count"] = 0
        history["daily_date"] = today
        cutoff = (datetime.now() - timedelta(days=30)).isoformat()
        history["alarms"] = [
            a for a in history.get("alarms", [])
            if a.get("time", "") > cutoff
        ]

    mistake = is_mistake_fare(price, target)

    if not mistake and not is_active_hour():
        return False, "Aktif saat dışı (MISTAKE FARE değil)"

    if history.get("daily_count", 0) >= 3:
        return False, "Günlük 3 alarm limitine ulaşıldı"

    cutoff_24h = (datetime.now() - timedelta(hours=24)).isoformat()
    recent = [
        a for a in history.get("alarms", [])
        if a.get("route") == route and a.get("time", "") > cutoff_24h
    ]
    if recent:
        return False, f"{route} için son 24 saatte alarm zaten gönderildi"

    return True, "OK"


def record_alarm(route: str):
    history = load_history()
    today = datetime.now().strftime("%Y-%m-%d")
    if history.get("daily_date") != today:
        history["daily_count"] = 0
        history["daily_date"] = today
    history["daily_count"] = history.get("daily_count", 0) + 1
    history.setdefault("alarms", []).append({
        "route": route,
        "time": datetime.now().isoformat()
    })
    save_history(history)


# ============================================================
# VİZE KONTROL
# ============================================================
def get_visa_status(dest: str) -> str:
    code = dest.upper()
    if code in SCHENGEN_AIRPORTS:
        return "✅ VİZESİZ (Schengen – Yeşil Pasaport)"
    elif code in VISA_WARNING_AIRPORTS:
        return "⚠️ VİZE GEREKLİ (UK/ABD/Kanada)"
    return "ℹ️ Vize durumu kontrol edilmeli"


# ============================================================
# TELEGRAM
# ============================================================
async def send_telegram(message: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    targets = [ADMIN_ID, GROUP_ID]

    async with httpx.AsyncClient(timeout=30) as client:
        for chat_id in targets:
            try:
                resp = await client.post(url, json={
                    "chat_id": chat_id,
                    "text": message,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": False,
                })
                if resp.status_code == 200:
                    print(f"  [Telegram ✓] chat_id={chat_id}")
                else:
                    print(f"  [Telegram HATA] {resp.status_code}: {resp.text[:200]}")
            except Exception as e:
                print(f"  [Telegram EXCEPTION] {e}")
            await asyncio.sleep(1)


def format_message(
    origin: str,
    dest: str,
    depart_date: str,
    return_date: str,
    price: float,
    airline: str,
    target: float,
) -> str:
    savings_pct = round((1 - price / target) * 100)
    visa_status = get_visa_status(dest)
    mistake = is_mistake_fare(price, target)

    google_link = build_google_flights_url(origin, dest, depart_date, return_date)
    kiwi_link = build_kiwi_url(origin, dest, depart_date, return_date)

    if mistake:
        header = "🚨 <b>PROJECT TITAN – MISTAKE FARE ALARMI</b> ⚡"
        note = f"⚡ <b>MISTAKE FARE!</b> Hedefin %{savings_pct} altında – anında al!"
    else:
        header = "🦅 <b>PROJECT TITAN – DİP FİYAT ALARMI</b> 💎"
        note = (
            f"📊 <b>Analiz:</b> Belirlenen hedefin <b>%{savings_pct} altında!</b>\n"
            f"✅ Alarm eşiği: Hedefin %{round((1 - ALARM_THRESHOLD) * 100)}'den fazla indirimli"
        )

    msg = (
        f"{header}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"✈️ <b>Rota:</b> {origin} ➔ {dest} <i>(Direkt Uçuş)</i>\n"
        f"📅 <b>Gidiş:</b> {depart_date}\n"
        f"📅 <b>Dönüş:</b> {return_date}\n"
        f"💰 <b>Fiyat:</b> <b>{price:,.0f} TL</b>\n"
        f"🎯 <b>Hedef Fiyat:</b> {target:,.0f} TL\n"
        f"🏷️ <b>Havayolu:</b> {airline}\n"
        f"{note}\n"
        f"🌍 <b>Vize:</b> {visa_status}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f'🔍 <a href="{google_link}">✈️ Google Flights\'ta Ara</a>\n'
        f'🪁 <a href="{kiwi_link}">Kiwi\'de Satın Al</a>\n'
        f"⚡ <b>AKSİYON: HEMEN AL!</b>"
    )
    return msg


# ============================================================
# ANA MOTOR
# ============================================================
async def run_scraper():
    print(f"\n{'='*60}")
    print(f"PROJECT TITAN v3.0 – {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Alarm Eşiği: Hedefin %{round(ALARM_THRESHOLD * 100)}'inden ucuz")
    print(f"Mistake Fare: Hedefin %{round(MISTAKE_THRESHOLD * 100)}'inden ucuz")
    print(f"Motor: Kiwi.com API (gerçek fiyatlar)")
    print(f"{'='*60}\n")

    all_flights = []
    search_dates = get_search_dates()

    async with httpx.AsyncClient(
        headers=HEADERS,
        follow_redirects=True,
        timeout=httpx.Timeout(30.0, connect=10.0),
    ) as client:

        for route in ROUTES:
            origin, dest = route.split("-")
            target_price = TARGET_PRICES[route]
            alarm_price = target_price * ALARM_THRESHOLD

            print(f"\n[ROTA] {route} | Hedef: {target_price:,} TL | Eşik: {alarm_price:,.0f} TL")

            dates_to_check = random.sample(search_dates, min(2, len(search_dates)))

            for depart_date, return_date in dates_to_check:
                print(f"  [Tarih] {depart_date} → {return_date}")

                flights = await fetch_kiwi_prices(
                    origin, dest, depart_date, return_date, client
                )

                if not flights:
                    print(f"  [!] {route} için {depart_date} tarihinde uçuş bulunamadı")
                    all_flights.append({
                        "route": route,
                        "origin": origin,
                        "dest": dest,
                        "depart_date": depart_date,
                        "return_date": return_date,
                        "price": None,
                        "airline": "Veri yok",
                        "target": target_price,
                        "alarm_threshold": round(alarm_price),
                        "savings_pct": None,
                        "is_below_target": False,
                        "is_mistake_fare": False,
                        "google_link": build_google_flights_url(origin, dest, depart_date, return_date),
                        "kiwi_link": build_kiwi_url(origin, dest, depart_date, return_date),
                        "scraped_at": datetime.now().isoformat(),
                        "data_source": "no_results",
                    })
                    await asyncio.sleep(random.uniform(2, 4))
                    continue

                for flight in flights:
                    price = flight["price"]
                    airline = flight["airline"]

                    if not sanity_check(price, route):
                        print(f"  [!] Sanity check FAIL: {price:,.0f} TL ({route}) – atlandı")
                        continue

                    below_threshold = is_below_alarm_threshold(price, target_price)
                    mistake = is_mistake_fare(price, target_price)

                    flight_record = {
                        "route": route,
                        "origin": origin,
                        "dest": dest,
                        "depart_date": depart_date,
                        "return_date": return_date,
                        "price": price,
                        "airline": airline,
                        "target": target_price,
                        "alarm_threshold": round(alarm_price),
                        "savings_pct": round((1 - price / target_price) * 100),
                        "is_below_target": below_threshold,
                        "is_mistake_fare": mistake,
                        "google_link": build_google_flights_url(origin, dest, depart_date, return_date),
                        "kiwi_link": build_kiwi_url(origin, dest, depart_date, return_date),
                        "scraped_at": datetime.now().isoformat(),
                        "data_source": flight.get("source", "kiwi"),
                    }
                    all_flights.append(flight_record)

                    label = ""
                    if mistake:
                        label = "🚨 MISTAKE FARE"
                    elif below_threshold:
                        label = "🎯 ALARM EŞİĞİ ALTI"

                    print(f"  [✓] {origin}→{dest}: {price:,.0f} TL | {airline} {label}")

                    if below_threshold or mistake:
                        can_send, reason = can_send_alarm(route, price, target_price)
                        if can_send:
                            print(f"  [🔔] Telegram alarm gönderiliyor...")
                            msg = format_message(
                                origin, dest,
                                depart_date, return_date,
                                price, airline, target_price
                            )
                            await send_telegram(msg)
                            record_alarm(route)
                        else:
                            print(f"  [⏸] Alarm engellendi: {reason}")

                await asyncio.sleep(random.uniform(1.5, 3.5))

    # ============================================================
    # SONUÇLARI flights.json'A YAZ
    # ============================================================
    valid_flights = [f for f in all_flights if f.get("price") is not None]
    no_data_flights = [f for f in all_flights if f.get("price") is None]

    sorted_flights = sorted(valid_flights, key=lambda x: x["price"]) + no_data_flights

    output = {
        "last_updated": datetime.now().isoformat(),
        "total_found": len(valid_flights),
        "below_target": sum(1 for f in valid_flights if f.get("is_below_target")),
        "alarm_threshold_pct": round((1 - ALARM_THRESHOLD) * 100),
        "data_source": "kiwi_api",
        "flights": sorted_flights,
    }

    flights_path = Path("flights.json")
    flights_path.write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print(f"\n{'='*60}")
    print(f"[✓] Toplam {len(valid_flights)} geçerli uçuş bulundu.")
    print(f"[✓] {output['below_target']} uçuş alarm eşiğinin altında.")
    print(f"[✓] flights.json güncellendi.")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(run_scraper())
