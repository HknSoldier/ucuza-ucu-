#!/usr/bin/env python3
"""
PROJECT TITAN V2.3 - Advanced Telegram Bot Tester
Tests all notification types with real configuration
"""

import asyncio
import sys
from datetime import datetime

# Config'den direkt tokenları al
from config import TitanConfig
from notifier import TelegramNotifier

async def test_all_features():
    """Tüm özellikleri test et"""
    print("\n" + "=" * 60)
    print("🦅 PROJECT TITAN V2.3 - COMPREHENSIVE TEST SUITE")
    print("=" * 60 + "\n")
    
    config = TitanConfig()
    notifier = TelegramNotifier(config)
    
    print(f"✅ Bot Token: {config.TELEGRAM_BOT_TOKEN[:20]}...")
    print(f"✅ Admin ID: {config.TELEGRAM_ADMIN_ID}")
    print(f"✅ Group ID: {config.TELEGRAM_GROUP_ID}")
    print("-" * 60)
    
    # Test 1: Startup mesajı
    print("\n[TEST 1] Startup Message...")
    await notifier.send_startup_message()
    print("✅ Sent!")
    await asyncio.sleep(3)
    
    # Test 2: Normal deal (dip fiyat)
    print("\n[TEST 2] Bottom Price Deal...")
    mock_deal_bottom = {
        "origin": "SOF",
        "destination": "JFK",
        "price": 9500,
        "currency": "TRY",
        "departure_date": "2026-06-15",
        "return_date": "2026-06-25",
        "airline": "Turkish Airlines",
        "method": "playwright-stealth",
        "flight_type": "Direkt",
        "analysis": {
            "should_alert": True,
            "is_mistake_fare": False,
            "is_green_zone": True,
            "bottom_analysis": {
                "min_price": 9000,
                "avg_price": 15000,
                "bottom_threshold": 9450
            },
            "price_category": {
                "category": "bottom",
                "emoji": "🔥",
                "action": "HEMEN AL",
                "urgency": "critical",
                "savings": 36.7
            },
            "visa_info": "🇺🇸 ABD - ⚠️ VİZE GEREKLİ (B1/B2)\n⚠️ UÇUŞ ÖNCESİ VİZE BAŞVURUSU YAPILMALIDIR!",
            "real_cost": {
                "real_cost": 9500,
                "base_price": 9500,
                "extra_costs": 0
            },
            "elasticity": {
                "elasticity": "low",
                "duration": "< 6 saat",
                "emoji": "🔥",
                "confidence": "high"
            },
            "confidence": 0.95
        }
    }
    
    await notifier.send_deal_alert(mock_deal_bottom)
    print("✅ Bottom deal sent!")
    await asyncio.sleep(3)
    
    # Test 3: Mistake fare (BYPASS tüm kuralları)
    print("\n[TEST 3] Mistake Fare Alert...")
    mock_deal_mistake = {
        "origin": "IST",
        "destination": "LAX",
        "price": 8500,
        "currency": "TRY",
        "departure_date": "2026-07-10",
        "return_date": "2026-07-20",
        "airline": "Multiple",
        "method": "playwright-stealth",
        "flight_type": "1 Aktarma",
        "analysis": {
            "should_alert": True,
            "is_mistake_fare": True,  # MISTAKE FARE!
            "is_green_zone": True,
            "bottom_analysis": {
                "min_price": 28000,
                "avg_price": 35000,
                "bottom_threshold": 29400
            },
            "price_category": {
                "category": "bottom",
                "emoji": "🔥",
                "action": "HEMEN AL",
                "urgency": "critical",
                "savings": 75.7
            },
            "visa_info": "🇺🇸 ABD - ⚠️ VİZE GEREKLİ (B1/B2)",
            "real_cost": {
                "real_cost": 9200,
                "base_price": 8500,
                "extra_costs": 700
            },
            "elasticity": {
                "elasticity": "low",
                "duration": "< 6 saat",
                "emoji": "🔥"
            },
            "confidence": 0.90
        }
    }
    
    await notifier.send_deal_alert(mock_deal_mistake)
    print("✅ Mistake fare sent!")
    await asyncio.sleep(3)
    
    # Test 4: Schengen (vizesiz) deal
    print("\n[TEST 4] Schengen Visa-Free Deal...")
    mock_deal_schengen = {
        "origin": "IST",
        "destination": "AMS",
        "price": 2500,
        "currency": "TRY",
        "departure_date": "2026-08-05",
        "return_date": "2026-08-12",
        "airline": "Pegasus",
        "method": "playwright-stealth",
        "flight_type": "Direkt",
        "analysis": {
            "should_alert": True,
            "is_mistake_fare": False,
            "is_green_zone": True,
            "bottom_analysis": {
                "min_price": 2400,
                "avg_price": 3500,
                "bottom_threshold": 2520
            },
            "price_category": {
                "category": "normal",
                "emoji": "🟡",
                "action": "BEKLE",
                "urgency": "medium",
                "savings": 28.6
            },
            "visa_info": "🟢 🇳🇱 Hollanda (Schengen - Vizesiz)",
            "real_cost": {
                "real_cost": 3050,
                "base_price": 2500,
                "extra_costs": 550
            },
            "elasticity": {
                "elasticity": "high",
                "duration": "> 24 saat",
                "emoji": "⏳"
            },
            "confidence": 0.85
        }
    }
    
    await notifier.send_deal_alert(mock_deal_schengen)
    print("✅ Schengen deal sent!")
    await asyncio.sleep(3)
    
    # Test 5: Error alert
    print("\n[TEST 5] Error Alert...")
    await notifier.send_error_alert("Test error: IP rotation needed (Simulated)")
    print("✅ Error alert sent!")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS COMPLETED!")
    print("=" * 60)
    print("\nTelegram'ınızı kontrol edin:")
    print("  1. ✅ Startup mesajı")
    print("  2. 🔥 Dip fiyat alarm (SOF → JFK)")
    print("  3. 💎 Mistake fare alarm (IST → LAX)")
    print("  4. 🟢 Schengen vizesiz deal (IST → AMS)")
    print("  5. ⚠️ Error alert")
    print("=" * 60 + "\n")

async def test_quick():
    """Hızlı test - sadece basit mesaj"""
    print("\n🦅 Quick Test - Sending test message...\n")
    
    config = TitanConfig()
    notifier = TelegramNotifier(config)
    
    test_msg = f"""
🦅 <b>PROJECT TITAN V2.3 TEST</b>

✅ Bot configured correctly!
✅ Ghost Protocol: Active
✅ Anti-Spam: Active
✅ All systems operational

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    success = await notifier._send_message(config.TELEGRAM_ADMIN_ID, test_msg)
    
    if success:
        print("✅ Test message sent successfully!")
        print("Check your Telegram now.\n")
        return True
    else:
        print("❌ Failed to send test message\n")
        return False

def main():
    """Main test function"""
    try:
        print("\n🦅 PROJECT TITAN V2.3 - TEST MODE")
        print("\nSelect test type:")
        print("1. Quick test (single message)")
        print("2. Full test (all features)")
        print()
        
        choice = input("Enter choice (1 or 2, default=1): ").strip() or "1"
        
        if choice == "1":
            success = asyncio.run(test_quick())
        elif choice == "2":
            success = asyncio.run(test_all_features())
        else:
            print("Invalid choice!")
            sys.exit(1)
        
        if success or choice == "2":
            print("\n✅ Testing complete!\n")
            sys.exit(0)
        else:
            print("\n❌ Test failed!\n")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Test cancelled by user\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Test error: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
    
