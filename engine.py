import time, random, logging
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
    def scan_route(self, origin, dest, months, hard_limit=None):
        today = datetime.now()
        for month in months:
            year = today.year + (1 if month < today.month else 0)
            stay_days = random.choice([5, 6, 7, 8]) 
            start_day = random.randint(10, 25)
            
            try:
                dep_date = datetime(year, month, start_day).strftime('%Y-%m-%d')
                ret_date = (datetime(year, month, start_day) + timedelta(days=stay_days)).strftime('%Y-%m-%d')
            except: continue

            try:
                result = get_flights(
                    flight_data=[FlightData(date=dep_date, from_airport=origin, to_airport=dest),
                                 FlightData(date=ret_date, from_airport=dest, to_airport=origin)],
                    trip="round-trip", seat="economy", passengers=Passengers(adults=1),
                    fetch_mode="fallback", currency="TRY"
                )

                if result and result.flights:
                    best = result.flights[0]
                    price = best.price

                    if hard_limit is None or price <= hard_limit:
                        h_link = f"https://www.google.com/travel/hotels?q=hotels+in+{dest}&checkin={dep_date}&checkout={ret_date}"
                        f_link = f"https://www.google.com/travel/flights?q=Flights%20to%20{dest}%20from%20{origin}%20on%20{dep_date}%20through%20{ret_date}"

                        return FlightDeal(
                            origin=origin, destination=dest, date=dep_date, return_date=ret_date,
                            price_try=price, airline=best.airline, days=stay_days,
                            note="Fiyat Limiti Altında Fırsat!", is_green=True, link=f_link, hotel_link=h_link
                        )
                time.sleep(random.uniform(2, 4))
            except Exception as e:
                logger.error(f"Hata: {e}")
                continue
        return None
