#!/usr/bin/env python3
"""
PROJECT TITAN v4.0 – Google Flights Playwright Scraper
Tüm fiyat verisi doğrudan Google Flights'tan çekilir.
API key yok, fallback yok, sadece gerçek tarama.
"""

import asyncio
import json
import random
import re
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

from playwright.async_api import async_playwright, TimeoutError as PWTimeout

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
    "IST-JFK": 18000,
    "IST-LAX": 20000,
    "SAW-CDG": 2800,
    "SAW-LHR": 3000,
    "SAW-AMS": 2600,
    "SAW-BCN": 2700,
    "SAW-FCO": 2400,
}

ALARM_THRESHOLD   = 0.85   # Hedefin %85'i altı → alarm
MISTAKE_THRESHOLD = 0.50   # Hedefin %50'si altı → MISTAKE FARE

ROUTES = list(TARGET_PRICES.keys())

# ============================================================
# VİZE DURUMU
# ============================================================
SCHENGEN_AIRPORTS = {
    "CDG","ORY","AMS","EIN","BCN","MAD","FCO","MXP","LIN",
    "FRA","MUC","TXL","BER","VIE","PRG","ATH","SKG","LIS",
    "ARN","GOT","CPH","HEL","OSL","ZUR","GVA","BRU","WAW",
    "KRK","BUD","SOF","OTP","RIX","TLL","VNO","LJU","SKP"
}
VISA_WARNING_AIRPORTS = {
    "LHR","LGW","STN","MAN",
    "JFK","LAX","ORD","MIA","SFO","BOS","IAD",
    "YYZ","YVR",
}

def get_visa_status(dest: str) -> str:
    code = dest.upper()
    if code in SCHENGEN_AIRPORTS:
        return "✅ VİZESİZ (Schengen – Yeşil Pasaport)"
    elif code in VISA_WARNING_AIRPORTS:
        return "⚠️ VİZE GEREKLİ (UK/ABD/Kanada)"
    return "ℹ️ Vize durumu kontrol edilmeli"

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
# GOOGLE FLIGHTS URL
# ============================================================
def build_google_flights_url(origin: str, dest: str, depart_date: str, return_date: str) -> str:
    """
    Google Flights round-trip arama URL'si.
    tfs parametresi: CBwQAhopag0IAxIJL20vMDJwdGpkEgoyMDI2LTA1LTE2cgwIAxIIL20vMDQ2NjUSCjIwMjYtMDUtMTk
    Bunun yerine daha basit query string format kullanıyoruz.
    """
    return (
        f"https://www.google.com/travel/flights"
        f"?hl=tr&curr=TRY"
        f"&q=Flights+from+{origin}+to+{dest}"
        f"+{depart_date}+returning+{return_date}"
    )

def build_google_flights_scrape_url(origin: str, dest: str, depart_date: str, return_date: str) -> str:
    """
    Google Flights direkt URL formatı - tarama için kullanılır.
    /travel/flights/search/ endpoint'i sonuçları daha hızlı yükler.
    """
    dep_fmt = depart_date   # YYYY-MM-DD
    ret_fmt = return_date
    return (
        f"https://www.google.com/travel/flights/search"
        f"?tfs=CBwQAhoqag0IAxIJ"
        f"&hl=tr"
        f"&curr=TRY"
        f"&gl=TR"
        f"&q={origin}+to+{dest}+{dep_fmt}+{ret_fmt}"
        f"&nonstop=1"
    )

# ============================================================
# FİYAT ÇEKME FONKSİYONU – Google Flights Playwright
# ============================================================
async def scrape_google_flights(
    origin: str,
    dest: str,
    depart_date: str,
    return_date: str,
    page,
) -> list[dict]:
    """
    Google Flights'tan fiyat çek.
    Döndürür: [{"price": float, "airline": str, "stops": int}]
    """
    results = []

    # URL: Google Flights round-trip, direkt uçuş, TRY para birimi
    dep_d = datetime.strptime(depart_date, "%Y-%m-%d")
    ret_d = datetime.strptime(return_date, "%Y-%m-%d")
    dep_str = dep_d.strftime("%Y-%m-%d")
    ret_str = ret_d.strftime("%Y-%m-%d")

    url = (
        f"https://www.google.com/travel/flights"
        f"?hl=tr&curr=TRY&gl=TR"
        f"&q={origin}+to+{dest}+{dep_str}+{ret_str}"
    )

    try:
        print(f"    [GF] Sayfa yükleniyor: {origin}→{dest} {dep_str}")
        await page.goto(url, wait_until="domcontentloaded", timeout=45000)

        # Captcha / reCAPTCHA kontrolü
        content = await page.content()
        if "captcha" in content.lower() or "unusual traffic" in content.lower():
            print(f"    [GF] ⚠️ CAPTCHA tespit edildi, atlanıyor.")
            return []

        # Sayfanın uçuş sonuçlarını yüklemesi için bekle
        # Google Flights'ta uçuş kartları birkaç farklı selector'da olabilir
        selectors_to_try = [
            '[data-gs]',           # Uçuş sonuç kartları
            '.YMlIz',              # Fiyat elementi
            '[jsname="IWWDBc"]',   # Sonuç listesi container
            'div[role="listitem"]', # Liste öğeleri
        ]

        loaded = False
        for sel in selectors_to_try:
            try:
                await page.wait_for_selector(sel, timeout=15000)
                loaded = True
                print(f"    [GF] Sonuçlar yüklendi (selector: {sel})")
                break
            except PWTimeout:
                continue

        if not loaded:
            print(f"    [GF] Sonuç yüklenemedi, sayfa kaydırılıyor...")
            await page.evaluate("window.scrollTo(0, 500)")
            await asyncio.sleep(3)

        # Sayfanın HTML içeriğini al
        html = await page.content()

        # ---- YÖNTEM 1: data-gs attribute'lu kartlardan fiyat çek ----
        prices_found = []

        # TRY fiyatlarını regex ile bul: ₺1.234 veya TRY 1.234 formatı
        # Google Flights Türkçe'de ₺ kullanır
        price_patterns = [
            r'₺\s*([\d.,]+)',
            r'TRY\s*([\d.,]+)',
            r'"price"[^"]*"([\d]+)"',
        ]

        for pattern in price_patterns:
            matches = re.findall(pattern, html)
            for m in matches:
                try:
                    # Türkçe format: 1.234 (nokta = binler ayırıcı)
                    clean = m.replace(".", "").replace(",", ".")
                    price = float(clean)
                    if 500 <= price <= 200000:  # Makul aralık
                        prices_found.append(price)
                except ValueError:
                    continue

        # Airline isimlerini çek
        airline_patterns = [
            r'"carrierName":"([^"]+)"',
            r'aria-label="([A-Za-zÇçĞğİıÖöŞşÜü\s]+) uçuşu',
            r'class="h1fkLb"[^>]*>([^<]+)<',
        ]

        airlines_found = []
        for pattern in airline_patterns:
            matches = re.findall(pattern, html)
            for m in matches:
                name = m.strip()
                if 2 < len(name) < 50 and not any(c.isdigit() for c in name):
                    airlines_found.append(name)

        # Benzersiz fiyatları al, en ucuzdan sırala
        prices_found = sorted(list(set(prices_found)))[:5]

        if prices_found:
            print(f"    [GF ✓] {len(prices_found)} fiyat bulundu: {[f'{p:,.0f}₺' for p in prices_found[:3]]}")
            for i, price in enumerate(prices_found[:3]):
                airline = airlines_found[i] if i < len(airlines_found) else "Çeşitli"
                results.append({
                    "price": price,
                    "airline": airline,
                    "stops": 0,
                    "source": "google_flights",
                })
        else:
            print(f"    [GF] Fiyat bulunamadı, alternatif yöntem deneniyor...")

            # ---- YÖNTEM 2: Playwright evaluate ile DOM'dan veri çek ----
            try:
                flight_data = await page.evaluate("""
                    () => {
                        const results = [];
                        // Fiyat elementlerini bul
                        const priceEls = document.querySelectorAll('[data-gs], .YMlIz, [jsname="IWWDBc"] [class*="price"]');
                        priceEls.forEach(el => {
                            const text = el.innerText || el.textContent || '';
                            // ₺ içeren kısmı bul
                            const match = text.match(/[₺]\s*([\d.,]+)/);
                            if (match) {
                                results.push({
                                    priceText: match[0],
                                    fullText: text.substring(0, 200)
                                });
                            }
                        });
                        return results.slice(0, 10);
                    }
                """)

                for item in flight_data:
                    pt = item.get("priceText", "")
                    m = re.search(r'[\d.,]+', pt)
                    if m:
                        try:
                            price = float(m.group().replace(".", "").replace(",", "."))
                            if 500 <= price <= 200000:
                                results.append({
                                    "price": price,
                                    "airline": "Çeşitli",
                                    "stops": 0,
                                    "source": "google_flights_dom",
                                })
                        except ValueError:
                            pass

                if results:
                    print(f"    [GF DOM ✓] {len(results)} fiyat bulundu")
                else:
                    print(f"    [GF] DOM yöntemi de boş döndü")

            except Exception as e:
                print(f"    [GF DOM HATA] {e}")

    except PWTimeout:
        print(f"    [GF TIMEOUT] {origin}→{dest} {dep_str} zaman aşımı")
    except Exception as e:
        print(f"    [GF HATA] {e}")

    return results


# ============================================================
# SANİTY CHECK
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
    "IST-JFK": (10000, 80000),
    "IST-LAX": (12000, 90000),
    "SAW-CDG": (1500, 15000),
    "SAW-LHR": (1500, 16000),
    "SAW-AMS": (1500, 14000),
    "SAW-BCN": (1500, 14000),
    "SAW-FCO": (1200, 13000),
}
DEFAULT_BOUNDS = (500, 200000)

def sanity_check(price: float, route: str) -> bool:
    min_p, max_p = ROUTE_PRICE_BOUNDS.get(route, DEFAULT_BOUNDS)
    return min_p <= price <= max_p

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

def can_send_alarm(route: str, price: float, target: float) -> tuple:
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
# TELEGRAM
# ============================================================
def send_telegram_sync(message: str):
    """Senkron Telegram gönderici (requests yerine urllib)"""
    targets = [ADMIN_ID, GROUP_ID]
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    for chat_id in targets:
        try:
            data = json.dumps({
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML",
                "disable_web_page_preview": False,
            }).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                if resp.status == 200:
                    print(f"  [Telegram ✓] chat_id={chat_id}")
                else:
                    print(f"  [Telegram HATA] HTTP {resp.status}")
        except Exception as e:
            print(f"  [Telegram EXCEPTION] {e}")

def format_message(
    origin, dest, depart_date, return_date,
    price, airline, target
) -> str:
    savings_pct = round((1 - price / target) * 100)
    visa_status = get_visa_status(dest)
    mistake = is_mistake_fare(price, target)

    google_link = (
        f"https://www.google.com/travel/flights"
        f"?hl=tr&curr=TRY&gl=TR"
        f"&q={origin}+to+{dest}+{depart_date}+{return_date}"
    )

    if mistake:
        header = "🚨 <b>PROJECT TITAN – MISTAKE FARE ALARMI</b> ⚡"
        note = f"⚡ <b>MISTAKE FARE!</b> Hedefin %{savings_pct} altında – anında al!"
    else:
        header = "🦅 <b>PROJECT TITAN – DİP FİYAT ALARMI</b> 💎"
        note = (
            f"📊 <b>Analiz:</b> Belirlenen hedefin <b>%{savings_pct} altında!</b>\n"
            f"✅ Alarm eşiği: Hedefin %{round((1-ALARM_THRESHOLD)*100)}'den fazla indirimli"
        )

    return (
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
        f"⚡ <b>AKSİYON: HEMEN AL!</b>"
    )

# ============================================================
# ANA MOTOR
# ============================================================
async def run_scraper():
    print(f"\n{'='*60}")
    print(f"PROJECT TITAN v4.0 – {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Motor: Google Flights (Playwright)")
    print(f"Alarm Eşiği: Hedefin %{round(ALARM_THRESHOLD*100)}'inden ucuz")
    print(f"Mistake Fare: Hedefin %{round(MISTAKE_THRESHOLD*100)}'inden ucuz")
    print(f"{'='*60}\n")

    all_flights = []
    search_dates = get_search_dates()

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--no-first-run",
                "--no-zygote",
                "--single-process",
                "--disable-extensions",
                "--disable-blink-features=AutomationControlled",
            ],
        )

        context = await browser.new_context(
            locale="tr-TR",
            timezone_id="Europe/Istanbul",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/121.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
            extra_http_headers={
                "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
            },
        )

        # Otomasyon tespitini engelle
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]});
            Object.defineProperty(navigator, 'languages', {get: () => ['tr-TR', 'tr', 'en']});
            window.chrome = {runtime: {}};
        """)

        page = await context.new_page()

        for route in ROUTES:
            origin, dest = route.split("-")
            target_price = TARGET_PRICES[route]
            alarm_price = target_price * ALARM_THRESHOLD

            print(f"\n[ROTA] {route} | Hedef: {target_price:,} TL | Eşik: {alarm_price:,.0f} TL")

            dates_to_check = random.sample(search_dates, min(2, len(search_dates)))

            for depart_date, return_date in dates_to_check:
                print(f"  [Tarih] {depart_date} → {return_date}")

                flights = await scrape_google_flights(
                    origin, dest, depart_date, return_date, page
                )

                google_link = (
                    f"https://www.google.com/travel/flights"
                    f"?hl=tr&curr=TRY&gl=TR"
                    f"&q={origin}+to+{dest}+{depart_date}+{return_date}"
                )

                if not flights:
                    print(f"  [!] {route} için {depart_date} tarihinde veri yok")
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
                        "google_link": google_link,
                        "scraped_at": datetime.now().isoformat(),
                        "data_source": "no_results",
                    })
                    await asyncio.sleep(random.uniform(3, 6))
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
                        "google_link": google_link,
                        "scraped_at": datetime.now().isoformat(),
                        "data_source": flight.get("source", "google_flights"),
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
                            send_telegram_sync(msg)
                            record_alarm(route)
                        else:
                            print(f"  [⏸] Alarm engellendi: {reason}")

                # Rotalar arası bekleme (anti-bot)
                await asyncio.sleep(random.uniform(4, 8))

        await browser.close()

    # ============================================================
    # SONUÇLARI flights.json'A YAZ
    # ============================================================
    valid_flights   = [f for f in all_flights if f.get("price") is not None]
    no_data_flights = [f for f in all_flights if f.get("price") is None]
    sorted_flights  = sorted(valid_flights, key=lambda x: x["price"]) + no_data_flights

    output = {
        "last_updated": datetime.now().isoformat(),
        "total_found": len(valid_flights),
        "below_target": sum(1 for f in valid_flights if f.get("is_below_target")),
        "alarm_threshold_pct": round((1 - ALARM_THRESHOLD) * 100),
        "data_source": "google_flights_playwright",
        "flights": sorted_flights,
    }

    Path("flights.json").write_text(
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
