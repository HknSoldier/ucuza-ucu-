# notifier.py - Telegram Notification System
import logging
import aiohttp
from typing import List, Dict
import traceback

logger = logging.getLogger(__name__)

class TelegramNotifier:
    """
    Telegram notification system
    Sends beautiful HTML-formatted alerts to admin and group
    """
    
    def __init__(self):
        # HARDCODED CREDENTIALS (as requested)
        self.bot_token = "8161806410:AAH4tGpW_kCvQpLOfaB-r2OYQMypPVYtuYg"
        self.admin_id = 7684228928
        self.group_id = -1003515302846
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    async def _send_message(self, chat_id: int, text: str, parse_mode: str = "HTML"):
        """
        Send message to Telegram chat
        """
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": parse_mode,
                "disable_web_page_preview": False
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        logger.info(f"Message sent to {chat_id}")
                        return True
                    else:
                        error = await response.text()
                        logger.error(f"Failed to send message: {error}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False
    
    def _format_deal_message(self, deal: Dict) -> str:
        """
        Format deal as beautiful HTML message
        """
        analysis = deal.get('analysis', {})
        
        # Build badges
        badges = []
        if analysis.get('is_green_zone'):
            badges.append("🔥 GREEN ZONE")
        if analysis.get('price_drop'):
            badges.append("📉 PRICE DROP")
        if analysis.get('below_threshold'):
            badges.append("💎 BELOW THRESHOLD")
        
        badges_str = " | ".join(badges) if badges else "✈️ DEAL"
        
        # Build Google Flights link
        flights_url = (
            f"https://www.google.com/travel/flights?"
            f"q=Flights%20to%20{deal['destination']}%20from%20{deal['origin']}%20"
            f"on%20{deal['departure_date']}%20through%20{deal['return_date']}"
        )
        
        # Build Hotels link
        hotels_url = (
            f"https://www.google.com/travel/hotels?"
            f"q=hotels%20in%20{deal['destination']}"
        )
        
        # Format message
        message = f"""
🦅 <b>PROJECT TITAN ALERT</b> {badges_str}

<b>Route:</b> {deal['origin']} → {deal['destination']}
<b>Price:</b> <code>{deal['price']:,.0f} {deal['currency']}</code>
<b>Dates:</b> {deal['departure_date']} → {deal['return_date']}
<b>Airline:</b> {deal.get('airline', 'N/A')}

📊 <b>Analysis:</b>
- Average Price: {analysis.get('avg_price', 0):,.0f} TL
- Threshold: {analysis.get('threshold', 0):,.0f} TL
- Savings: {((analysis.get('avg_price', 0) - deal['price']) / analysis.get('avg_price', 1) * 100):.1f}%

🔗 <a href="{flights_url}">View Flights on Google</a>
🏨 <a href="{hotels_url}">Find Hotels</a>

<i>Scanned by {deal.get('method', 'hybrid')} engine</i>
"""
        
        return message.strip()
    
    async def send_deals_report(self, deals: List[Dict]):
        """
        Send deals report to both admin and group
        """
        if not deals:
            return
        
        try:
            # Send summary first
            summary = f"""
🦅 <b>TITAN SCAN COMPLETE</b>

Found <b>{len(deals)}</b> significant deal(s)

Sending detailed reports...
"""
            await self._send_message(self.admin_id, summary)
            await self._send_message(self.group_id, summary)
            
            # Send each deal
            for deal in deals:
                message = self._format_deal_message(deal)
                await self._send_message(self.admin_id, message)
                await self._send_message(self.group_id, message)
            
            logger.info(f"Sent {len(deals)} deal alerts")
            
        except Exception as e:
            logger.error(f"Error sending deals report: {e}")
            logger.error(traceback.format_exc())
    
    async def send_error_alert(self, error: str):
        """
        Send error alert to admin
        """
        message = f"""
⚠️ <b>TITAN ERROR ALERT</b>

<code>{error}</code>

Check logs for details.
"""
        await self._send_message(self.admin_id, message)
    
    async def send_startup_message(self):
        """
        Send startup confirmation
        """
        message = """
🦅 <b>PROJECT TITAN ONLINE</b>

Intelligence system initialized.
Monitoring active routes...
"""
        await self._send_message(self.admin_id, message)
```

Şimdi gerekli diğer dosyaları oluşturuyorum:
```
# requirements.txt
aiohttp==3.9.1
feedparser==6.0.10
playwright==1.40.0
pytest-playwright==0.4.3
python-dateutil==2.8.2

# Optional: fast-flights (may break, we have fallback)
fast-flights==1.0.0
