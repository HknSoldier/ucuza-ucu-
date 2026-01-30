import time
import random
import logging
from datetime import datetime, timedelta
from fast_flights import FlightData, Passengers, get_flights
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class FlightDeal:
    origin: str; destination: str; date: str; return_date: str
    price_try: float; airline: str; days: int; note: str
    is_green: bool; link: str; hotel_link: str

class AnalysisEngine:
    def scan_route(self, origin, dest, hard_limit=None):
        today = datetime.now()
        
        # STRATEJİ: Önümüzdeki 365 gün içinden rastgele 4 farklı dönem seçip dene.
        # Böylece tüm yılı "örnekleme" yöntemiyle taramış oluruz.
        attempt_dates = []
        for _ in range(4):
            days_future = random.randint(14, 300) # En erken 2 hafta, en geç 10 ay sonrasına bak
            attempt_dates.append(today + timedelta(days=days_future))

        for date_obj in attempt_dates:
            # Tatil Süresi: 3 ile 14 gün arası
            stay_days = random.randint(3, 14)
            
            dep_date = date_obj.strftime('%Y-%m-%d')
            ret_date = (date_obj + timedelta(days=stay_days)).strftime('%Y-%m-%d')

            try:
                # Fast-flights (Fallback modu)
                result = get_flights(
                    flight_data=[FlightData(date=dep_date, from_airport=origin, to_airport=dest),
                                 FlightData(date=ret_date, from_airport=dest, to_airport=origin)],
                    trip="round-trip", seat="economy", passengers=Passengers(adults=1),
                    fetch_mode="fallback", currency="TRY"
                )

                if result and result.flights:
                    # Sadece En Ucuz (Yeşil) olanı al
                    best = result.flights[0] 
                    price = best.price
                    
                    # Eğer Google "Bu fiyat düşük" veya "Tipik" diyorsa
                    # (Fast-flights bazen bu veriyi vermez, fiyata göre biz karar verelim)
                    
                    if hard_limit and price > hard_limit:
                        continue # Pahalıysa geç
                    
                    # Hack: Eğer aktarma süresi 14-24 saat ise "Bedava Otel" ihtimali var
                    note = "Yeşil Bölge Fırsatı"
                    if "DOH" in str(best) or "IST" in str(best) or "AUH" in str(best):
                        note += " | 🏨 Stopover (Bedava Otel) ihtimalini kontrol et!"

                    # Linkler
                    h_link = f"https://www.google.com/travel/hotels?q=hotels+in+{dest}&checkin={dep_date}&checkout={ret_date}"
                    f_link = f"https://www.google.com/travel/flights?q=Flights%20to%20{dest}%20from%20{origin}%20on%20{dep_date}%20through%20{ret_date}"
                    
                    return FlightDeal(
                        origin=origin, destination=dest, date=dep_date, return_date=ret_date,
                        price_try=price, airline=best.airline, days=stay_days,
                        note=note, is_green=True, link=f_link, hotel_link=h_link
                    )
                
                # Anti-ban: Kısa bekleme
                time.sleep(random.uniform(1.5, 3.5))

            except:
                continue
        
        return None
