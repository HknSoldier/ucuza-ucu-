"""
SNIPER V46 - HYBRID ENGINE (ALL-IN-ONE)
Layer 2: Combined Scanning + Proper Link Fix + Strict Green Zone
"""
import time, random, statistics, calendar, requests, logging
from datetime import datetime, timedelta
from fast_flights import FlightData, Passengers, get_flights
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class FlightDeal:
    origin: str; destination: str; date: str; return_date: str
    native_price: float; native_currency: str; price_try: float
    airline: str; days: int; note: str; is_green: bool; link: str

class AnalysisEngine:
    def __init__(self):
        self.CURRENCY_MAP = {"USD": 45.0, "EUR": 48.0, "GBP": 56.0}

    def scan_route(self, origin, dest, months, hard_limit=None):
        all_deals = []
        today = datetime.now()
        
        HOLIDAYS_2026 = [
            '2026-03-20', '2026-04-23', '2026-05-01', '2026-05-19', 
            '2026-05-27', '2026-07-15', '2026-08-30', '2026-10-29'
        ]

        for month in months:
            year = today.year + (1 if month < today.month else 0)
            cal = calendar.monthcalendar(year, month)
            
            # --- HİBRİT TARAMA ---
            candidate_days = []
            
            # 1. EN UCUZ GÜNLER
            cheap_days = [week[i] for week in cal for i in [1, 2] if week[i] != 0]
            candidate_days.extend(cheap_days)
            
            # 2. HAFTA SONU
            fridays = [week[4] for week in cal if week[4] != 0]
            candidate_days.extend(fridays)
            
            # 3. RESMİ TATİLLER
            for h_date in HOLIDAYS_2026:
                h_obj = datetime.strptime(h_date, '%Y-%m-%d')
                if h_obj.month == month and h_obj.year == year:
                    candidate_days.append(h_obj.day)
            
            candidate_days = sorted(list(set(candidate_days)))
            
            if not candidate_days: continue
            
            # 5 Rastgele Gün Seçimi
            for day in random.sample(candidate_days, min(len(candidate_days), 5)):
                d_out = datetime(year, month, day)
                if (d_out - today).days > 330: continue
                
                stay = random.randint(3, 14) 
                d_in = d_out + timedelta(days=stay)
                
                time.sleep(random.uniform(5.0, 7.0))
                try:
                    result = get_flights(
                        flight_data=[FlightData(date=d_out.strftime('%Y-%m-%d'), from_airport=origin, to_airport=dest)],
                        trip="round-trip", seat="economy", passengers=Passengers(adults=1)
                    )
                    if result.flights:
                        f = result.flights[0]
                        raw = str(f.price); val = float(''.join(c for c in raw if c.isdigit() or c == '.'))
                        curr = "TL"; try_val = val
                        if "$" in raw or "USD" in raw: curr = "$"; try_val = val * self.CURRENCY_MAP["USD"]
                        elif "€" in raw or "EUR" in raw: curr = "€"; try_val = val * self.CURRENCY_MAP["EUR"]
                        elif "£" in raw or "GBP" in raw: curr = "£"; try_val = val * self.CURRENCY_MAP["GBP"]
                        
                        if try_val > 500:
                            all_deals.append({
                                'native_price': val, 'native_currency': curr, 'price_try': try_val, 
                                'airline': f.name, 'out': d_out.strftime('%Y-%m-%d'), 'in': d_in.strftime('%Y-%m-%d'), 
                                'stay': stay,
                                'day_type': "HAFTA SONU" if d_out.weekday() == 4 else ("UCUZ GÜN" if d_out.weekday() in [1,2] else "TATİL")
                            })
                except: continue

        if len(all_deals) < 3: return None

        # --- YEŞİL BÖLGE HESABI (DAHA SIKI) ---
        prices = [d['price_try'] for d in all_deals]
        min_p = min(prices); avg_p = statistics.mean(prices)
        
        # Matematiksel Yeşil: Ortalama fiyattan en az %20 daha ucuz olmalı (Eskisi %15 idi)
        # Ayrıca Hard Limit varsa onu da geçmemeli
        green_threshold = avg_p * 0.80
        is_green = min_p <= green_threshold
        
        if hard_limit and min_p > hard_limit:
            is_green = False # Limit aşılmışsa asla yeşil olamaz
            
        best = next(d for d in all_deals if d['price_try'] == min_p)
        
        # LİNK DÜZELTMESİ: Standart Google Flights Linki
        # "tfs" parametresi olmadan, temiz arama linki
        clean_link = f"https://www.google.com/travel/flights?q=Flights%20to%20{dest}%20from%20{origin}%20on%20{best['out']}%20through%20{best['in']}"
        
        return FlightDeal(
            origin=origin, destination=dest, date=best['out'], return_date=best['in'],
            native_price=best['native_price'], native_currency=best['native_currency'], price_try=best['price_try'],
            airline=best['airline'], days=best['stay'], is_green=is_green,
            note=f"📊 TİP: {best['day_type']} | Ort: {avg_p:,.0f} TL | Dip: {min_p:,.0f} TL",
            link=clean_link
        )

class HotelEngine:
    def __init__(self, api_key):
        self.api_key = api_key
    
    def get_best_hotel(self, city_name, check_in, check_out):
        params = {
            "engine": "google_hotels", "q": f"{city_name} hotels",
            "check_in_date": check_in, "check_out_date": check_out,
            "currency": "TRY", "gl": "tr", "hl": "tr", "api_key": self.api_key,
            "free_cancellation": "1", "special_offers": "1"
        }
        try:
            response = requests.get("https://serpapi.com/search.json", params=params)
            hotels = response.json().get('properties', [])
            if not hotels: return None
            valid = []
            for h in hotels:
                p = float(''.join(c for c in h.get('total_rate', {}).get('lowest', "0") if c.isdigit()))
                r = h.get('overall_rating', 0)
                if p > 0: valid.append({'name': h.get('name'), 'price': p, 'rating': r, 'link': h.get('link')})
            return sorted(valid, key=lambda x: x['price'])[0] if valid else None
        except: return None
