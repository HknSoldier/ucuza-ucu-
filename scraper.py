#!/usr/bin/env python3
"""
PROJECT TITAN: ULTIMATE AUTONOMOUS FLIGHT INTEL (V2.3 - ENTERPRISE PROD)
Ana scraping motoru - Playwright tabanlı, anti-bot bypass, Telegram bildirim sistemi
"""

import asyncio
import json
import os
import random
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from playwright.async_api import async_playwright, Page
from playwright_stealth import stealth_async

# ============================================================
# GLOBAL KİMLİK BİLGİLERİ (HARDCODED)
# ============================================================
BOT_TOKEN = "8161806410:AAH4tGpW_kCvQpLOfaB-r2OYQMypPVYtuYg"
ADMIN_ID = "7684228928"
GROUP_ID = "-1003515302846"

# ============================================================
# HEDEF FIYATLAR (TL) – Rota bazlı dip avcısı eşikleri
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
    "IST-JFK": 6500,
    "IST-LAX": 7000,
    "SAW-CDG": 2800,
    "SAW-LHR": 3000,
    "SAW-AMS": 2600,
    "SAW-BCN": 2700,
    "SAW-FCO": 2400,
}

# ============================================================
# VİZE DURUMU – Schengen ve diğer ülkeler için Yeşil Pasaport
# ============================================================
SCHENGEN_AIRPORTS = {
    "CDG", "ORY",   # Fransa
    "AMS", "EIN",   # Hollanda
    "BCN", "MAD",   # İspanya
    "FCO", "MXP", "LIN",  # İtalya
    "FRA", "MUC", "TXL", "BER",  # Almanya
    "VIE",          # Avusturya
    "PRG",          # Çekya
    "ATH", "SKG",   # Yunanistan
    "LIS",          # Portekiz
    "ARN", "GOT",   # İsveç
    "CPH",          # Danimarka
    "HEL",          # Finlandiya
    "OSL",          # Norveç
    "ZUR", "GVA",   # İsviçre
    "BRU",          # Belçika
    "WAW", "KRK",   # Polonya
    "BUD",          # Macaristan
    "SOF",          # Bulgaristan
    "OTP",          # Romanya
    "RIX",          # Letonya
    "TLL",          # Estonya
    "VNO",          # Litvanya
    "LJU",          # Slovenya
    "SKP",          # Kuzey Makedonya
}
VISA_WARNING_AIRPORTS = {
    "LHR", "LGW", "STN", "MAN",  # İngiltere
    "JFK", "LAX", "ORD", "MIA", "SFO", "BOS", "IAD",  # ABD
    "YYZ", "YVR",  # Kanada
}

# ============================================================
# ARANACAK ROTALAR VE TARİH ARALIĞI
# ============================================================
ROUTES = list(TARGET_PRICES.keys())

def get_search_dates():
    """Önümüzdeki 30-90 gün arasında rastgele tarihleri döndür"""
    dates = []
    base = datetime.now()
    # Birkaç hafta sonu tatili senaryosu
    for weeks_ahead in [2, 3, 4, 6, 8, 10, 12]:
        d = base + timedelta(weeks=weeks_ahead)
        # Cuma gidip Pazartesi dön
        friday = d + timedelta(days=(4 - d.weekday()) % 7)
        monday = friday + timedelta(days=3)
        dates.append((friday.strftime("%Y-%m-%d"), monday.strftime("%Y-%m-%d")))
    return dates

# ============================================================
# RANDOM USER-AGENT HAVUZU
# ============================================================
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
]

# ============================================================
# GHOST PROTOCOL – ZAMAN YÖNETİMİ
# ============================================================
def is_active_hour() -> bool:
    now = datetime.now()
    hour = now.hour
    weekday = now.weekday()  # 0=Pazartesi, 6=Pazar
    if weekday < 5:  # Hafta içi
        return 9 <= hour < 20
    else:  # Hafta sonu
        return 11 <= hour < 23

def is_mistake_fare(price: float, target: float) -> bool:
    """Hedef fiyatın %70 veya daha fazlası kadar ucuzsa MISTAKE FARE"""
    return price <= target * 0.30  # %70 indirim = hedefin %30'u

# ============================================================
# HISTORY (ANTİ-SPAM) YÖNETİMİ
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
    HISTORY_FILE.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")

def can_send_alarm(route: str, price: float, target: float) -> tuple[bool, str]:
    """
    Alarm gönderilebilir mi?
    Returns: (can_send, reason)
    """
    history = load_history()
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Günlük sayacı sıfırla
    if history.get("daily_date") != today:
        history["daily_count"] = 0
        history["daily_date"] = today
        # 30 günden eski alarmları temizle
        cutoff = (datetime.now() - timedelta(days=30)).isoformat()
        history["alarms"] = [a for a in history.get("alarms", []) if a.get("time", "") > cutoff]
    
    mistake = is_mistake_fare(price, target)
    
    # MISTAKE FARE → aktif saat kuralını bypass et
    if not mistake and not is_active_hour():
        return False, "Aktif saat dışı (MISTAKE FARE değil)"
    
    # Günlük maks 3 alarm
    if history.get("daily_count", 0) >= 3:
        return False, "Günlük maksimum 3 alarm limitine ulaşıldı"
    
    # Aynı rota için 24 saat içinde maks 1 alarm
    cutoff_24h = (datetime.now() - timedelta(hours=24)).isoformat()
    recent_route_alarms = [
        a for a in history.get("alarms", [])
        if a.get("route") == route and a.get("time", "") > cutoff_24h
    ]
    if recent_route_alarms:
        return False, f"{route} için son 24 saatte zaten alarm gönderildi"
    
    return True, "OK"

def record_alarm(route: str):
    history = load_history()
    today = datetime.now().strftime("%Y-%m-%d")
    if history.get("daily_date") != today:
        history["daily_count"] = 0
        history["daily_date"] = today
    history["daily_count"] = history.get("daily_count", 0) + 1
    if "alarms" not in history:
        history["alarms"] = []
    history["alarms"].append({
        "route": route,
        "time": datetime.now().isoformat()
    })
    save_history(history)

# ============================================================
# VİZE DURUM KONTROLÜ
# ============================================================
def get_visa_status(dest_airport: str) -> str:
    code = dest_airport.upper()
    if code in SCHENGEN_AIRPORTS:
        return "✅ VİZESİZ (Schengen – Yeşil Pasaport)"
    elif code in VISA_WARNING_AIRPORTS:
        return "⚠️ VİZE GEREKLİ (UK/ABD/Kanada)"
    else:
        return "ℹ️ Vize durumu kontrol edilmeli"

# ============================================================
# TELEGRAM BİLDİRİM
# ============================================================
async def send_telegram(message: str):
    """Telegram'a mesaj gönder (httpx ile async)"""
    import httpx
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    targets = [ADMIN_ID, GROUP_ID]
    async with httpx.AsyncClient(timeout=30) as client:
        for chat_id in targets:
            try:
                resp = await client.post(url, json={
                    "chat_id": chat_id,
                    "text": message,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": True,
                })
                if resp.status_code != 200:
                    print(f"[TELEGRAM HATA] chat_id={chat_id}: {resp.text}")
                else:
                    print(f"[TELEGRAM OK] chat_id={chat_id}")
            except Exception as e:
                print(f"[TELEGRAM EXCEPTION] {e}")
            await asyncio.sleep(1)

def format_message(
    origin: str, dest: str,
    depart_date: str, return_date: str,
    price: float, airline: str,
    target: float
) -> str:
    savings_pct = round((1 - price / target) * 100)
    visa_status = get_visa_status(dest)
    # Google Flights deep link
    link = f"https://www.google.com/travel/flights?q=Flights+to+{dest}+from+{origin}&tfs=CBwQAhoeEgoyMDI0LTAxLTAxagcIARIDSVNUcgcIARIDQ0RH"
    
    msg = (
        f"🦅 <b>PROJECT TITAN – DİP FİYAT ALARMI</b> 💎\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"✈️ <b>Rota:</b> {origin} ➔ {dest} <i>(Direkt Uçuş)</i>\n"
        f"📅 <b>Tarih:</b> {depart_date} ➔ {return_date}\n"
        f"💰 <b>Fiyat:</b> <b>{price:,.0f} TL</b>\n"
        f"🏷️ <b>Havayolu:</b> {airline}\n"
        f"📊 <b>Analiz:</b> Belirlenen hedefin %{savings_pct} altında!\n"
        f"✅ <b>Vize Durumu:</b> {visa_status}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f'🔗 <a href="{link}">✈️ UÇUŞ LİNKİ</a>\n'
        f"⚡ <b>AKSİYON: HEMEN AL!</b>"
    )
    return msg

# ============================================================
# SANİTY CHECK
# ============================================================
def sanity_check(price: float) -> bool:
    return 100 <= price <= 500_000

# ============================================================
# GOOGLE FLIGHTS SCRAPER (PLAYWRIGHT)
# ============================================================
async def jitter(min_s=2, max_s=7):
    """İnsan simülasyonu için rastgele bekleme"""
    await asyncio.sleep(random.uniform(min_s, max_s))

async def scrape_google_flights(
    page: Page,
    origin: str,
    dest: str,
    depart_date: str,
    return_date: str,
) -> list[dict]:
    """
    Google Flights'tan direkt uçuş verisi çek.
    Returns: list of {price, airline, stops}
    """
    results = []
    
    # Google Flights URL formatı
    # tfs parametresi: CBwQAhoe = round trip, Sadece direkt uçuşlar için nonstop=1
    url = (
        f"https://www.google.com/travel/flights/search"
        f"?tfs=CBwQAhoeEgoyMDI0LTAxLTAxagcIARID{origin}cgcIARID{dest}"
        f"&tfu=EgQIBBAB"  # direkt uçuş filtresi
        f"&curr=TRY"
        f"&hl=tr"
    )
    
    # Daha güvenilir URL formatı
    url = (
        f"https://www.google.com/travel/flights?q=Direkt+ucucler+{origin}+to+{dest}"
        f"+on+{depart_date}+returning+{return_date}&curr=TRY&hl=tr"
    )
    
    try:
        print(f"  [+] Google Flights: {origin}→{dest} | {depart_date}→{return_date}")
        await page.goto(url, wait_until="networkidle", timeout=45000)
        await jitter(3, 6)
        
        # Sayfanın yüklendiğini doğrula
        await page.wait_for_selector("body", timeout=15000)
        await jitter(2, 4)
        
        # Fiyat elementlerini ara – Google Flights'ın class yapısı değişken
        # Birden fazla selector dene
        selectors_to_try = [
            '[data-gs]',
            '.YMlIz',
            '[class*="price"]',
            '.pIav2d',
        ]
        
        price_elements = []
        for sel in selectors_to_try:
            try:
                elements = await page.query_selector_all(sel)
                if elements:
                    price_elements = elements
                    print(f"    [>] Selector '{sel}' ile {len(elements)} eleman bulundu")
                    break
            except Exception:
                continue
        
        # Uçuş kartlarını parse et
        # Google Flights sonuçlarını JSON olarak çek (data-gs attribute)
        flight_data_raw = await page.evaluate("""
            () => {
                const results = [];
                // Uçuş listesi elemanlarını bul
                const listItems = document.querySelectorAll('li[data-gs], li.Rk10dc, div[class*="flight-result"]');
                
                listItems.forEach(item => {
                    try {
                        const priceEl = item.querySelector('[data-gs], .YMlIz, .U3gSDe, [aria-label*="TL"], [aria-label*="₺"]');
                        const airlineEl = item.querySelector('.sSHqwe, .Xsgmwe, [class*="airline"]');
                        const stopsEl = item.querySelector('.EfT7Ae, .ogfYpf, [class*="stop"]');
                        
                        let priceText = '';
                        let airline = 'Bilinmiyor';
                        let stopsText = '';
                        
                        if (priceEl) priceText = priceEl.innerText || priceEl.textContent || '';
                        if (airlineEl) airline = airlineEl.innerText || airlineEl.textContent || 'Bilinmiyor';
                        if (stopsEl) stopsText = stopsEl.innerText || stopsEl.textContent || '';
                        
                        if (priceText) {
                            results.push({
                                price_text: priceText.trim(),
                                airline: airline.trim(),
                                stops_text: stopsText.trim()
                            });
                        }
                    } catch(e) {}
                });
                
                // Alternatif: aria-label üzerinden tüm fiyatları bul
                if (results.length === 0) {
                    const priceEls = document.querySelectorAll('[aria-label]');
                    priceEls.forEach(el => {
                        const label = el.getAttribute('aria-label') || '';
                        if (label.includes('TL') || label.includes('₺')) {
                            results.push({
                                price_text: label,
                                airline: 'Çeşitli',
                                stops_text: label.includes('aktarma') ? '1+ aktarma' : 'direkt'
                            });
                        }
                    });
                }
                
                return results;
            }
        """)
        
        print(f"    [>] Ham veri: {len(flight_data_raw)} kayıt")
        
        for item in flight_data_raw:
            price_text = item.get("price_text", "")
            airline = item.get("airline", "Bilinmiyor")
            stops_text = item.get("stops_text", "").lower()
            
            # Fiyatı parse et
            price = parse_price_tl(price_text)
            if price is None:
                continue
            
            # Sanity check
            if not sanity_check(price):
                print(f"    [!] Sanity check başarısız: {price} TL")
                continue
            
            # SADECE DİREKT UÇUŞLAR (stops=0)
            if "aktarma" in stops_text or "durak" in stops_text or "stop" in stops_text:
                continue
            
            results.append({
                "price": price,
                "airline": airline.split("\n")[0].strip()[:50],
                "stops": 0,
            })
        
    except Exception as e:
        print(f"    [HATA] Scraping başarısız: {e}")
    
    return results

def parse_price_tl(text: str) -> Optional[float]:
    """Metin içindeki TL fiyatını çıkar"""
    import re
    text = text.replace("\xa0", " ").replace("₺", "").replace("TL", "")
    # Sayıyı bul: nokta binlik ayraç, virgül ondalık
    patterns = [
        r"(\d{1,3}(?:\.\d{3})*(?:,\d+)?)",  # 1.234,56
        r"(\d+)",  # Salt sayı
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            num_str = match.group(1).replace(".", "").replace(",", ".")
            try:
                return float(num_str)
            except ValueError:
                continue
    return None

# ============================================================
# ANA MOTOR
# ============================================================
async def run_scraper():
    print(f"\n{'='*60}")
    print(f"PROJECT TITAN v2.3 – {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    all_flights = []
    search_dates = get_search_dates()
    
    async with async_playwright() as p:
        # Chromium başlat
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--disable-accelerated-2d-canvas",
                "--no-first-run",
                "--no-zygote",
                "--disable-gpu",
            ]
        )
        
        for route in ROUTES:
            origin, dest = route.split("-")
            target_price = TARGET_PRICES.get(route, 5000)
            
            print(f"\n[ROTA] {route} | Hedef: {target_price:,} TL")
            
            # Her rota için birkaç tarih kombinasyonu dene
            dates_to_check = random.sample(search_dates, min(2, len(search_dates)))
            
            for depart_date, return_date in dates_to_check:
                # Yeni context her request için
                context = await browser.new_context(
                    user_agent=random.choice(USER_AGENTS),
                    viewport={"width": random.randint(1280, 1920), "height": random.randint(800, 1080)},
                    locale="tr-TR",
                    timezone_id="Europe/Istanbul",
                )
                page = await context.new_page()
                
                # Playwright Stealth uygula
                try:
                    await stealth_async(page)
                except Exception as e:
                    print(f"  [!] Stealth uygulanamadı: {e}")
                
                flights = await scrape_google_flights(page, origin, dest, depart_date, return_date)
                await context.close()
                
                for flight in flights:
                    price = flight["price"]
                    airline = flight["airline"]
                    
                    flight_record = {
                        "route": route,
                        "origin": origin,
                        "dest": dest,
                        "depart_date": depart_date,
                        "return_date": return_date,
                        "price": price,
                        "airline": airline,
                        "target": target_price,
                        "savings_pct": round((1 - price / target_price) * 100),
                        "is_below_target": price < target_price,
                        "is_mistake_fare": is_mistake_fare(price, target_price),
                        "scraped_at": datetime.now().isoformat(),
                    }
                    all_flights.append(flight_record)
                    
                    print(f"  [✓] {origin}→{dest}: {price:,.0f} TL | {airline}")
                    
                    # Hedef fiyatın altında mı?
                    if price < target_price:
                        can_send, reason = can_send_alarm(route, price, target_price)
                        
                        if can_send:
                            print(f"  [🔔 ALARM] Hedef altında! Telegram'a gönderiliyor...")
                            msg = format_message(
                                origin, dest,
                                depart_date, return_date,
                                price, airline, target_price
                            )
                            await send_telegram(msg)
                            record_alarm(route)
                        else:
                            print(f"  [⏸] Alarm engellendi: {reason}")
                
                # Rotalar arası jitter
                await jitter(3, 7)
        
        await browser.close()
    
    # Sonuçları flights.json'a yaz
    flights_path = Path("flights.json")
    output = {
        "last_updated": datetime.now().isoformat(),
        "total_found": len(all_flights),
        "below_target": sum(1 for f in all_flights if f.get("is_below_target")),
        "flights": sorted(all_flights, key=lambda x: x["price"]),
    }
    flights_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[✓] {len(all_flights)} uçuş flights.json'a kaydedildi.")
    print(f"[✓] {output['below_target']} uçuş hedef fiyat altında.")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    asyncio.run(run_scraper())
