#!/usr/bin/env python3
"""
Quick test script for Telegram notifications
Supports both environment variables and .env file
"""

import asyncio
import sys
import os

# Try to load .env file for local testing
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✓ Loaded .env file")
except ImportError:
    print("ℹ️  python-dotenv not installed (optional for local testing)")
except:
    pass

from notifier import TelegramNotifier

async def test_notifications():
    """Test all notification types"""
    print("\n" + "="*50)
    print("🦅 PROJECT TITAN - Telegram Bot Tester")
    print("="*50 + "\n")
    
    # Check if credentials are set
    bot_token = os.environ.get("BOT_TOKEN", "")
    admin_id = os.environ.get("ADMIN_ID", "")
    
    if not bot_token or bot_token == "YOUR_BOT_TOKEN_HERE":
        print("❌ ERROR: BOT_TOKEN not set!")
        print("\nFor local testing:")
        print("  1. Copy .env.example to .env")
        print("  2. Fill in your credentials in .env")
        print("  3. Install: pip install python-dotenv")
        print("  4. Run this script again")
        print("\nFor GitHub Actions:")
        print("  Settings → Secrets → Add BOT_TOKEN, ADMIN_ID, GROUP_ID")
        return False
    
    print(f"✓ BOT_TOKEN: {bot_token[:20]}...")
    print(f"✓ ADMIN_ID: {admin_id}")
    print("-" * 50)
    
    notifier = TelegramNotifier()
    
    # Test 1: Startup message
    print("\nTest 1: Sending startup message...")
    success = await notifier.send_startup_message()
    if success:
        print("✅ Startup message sent!")
    else:
        print("❌ Failed to send startup message")
        return False
    
    await asyncio.sleep(2)
    
    # Test 2: Mock deal alert
    print("\nTest 2: Sending mock deal alert...")
    mock_deal = {
        "origin": "SOF",
        "destination": "JFK",
        "price": 9500,
        "currency": "TRY",
        "departure_date": "2026-06-15",
        "return_date": "2026-06-25",
        "airline": "Turkish Airlines",
        "method": "playwright",
        "analysis": {
            "is_green_zone": True,
            "price_drop": True,
            "below_threshold": True,
            "avg_price": 15000,
            "threshold": 10000
        }
    }
    
    await notifier.send_deals_report([mock_deal])
    print("✅ Deal alert sent!")
    
    await asyncio.sleep(2)
    
    # Test 3: Error alert
    print("\nTest 3: Sending mock error alert...")
    await notifier.send_error_alert("Test error: This is a test message")
    print("✅ Error alert sent!")
    
    print("\n" + "=" * 50)
    print("✅ ALL TESTS PASSED!")
    print("Check your Telegram for 3 messages:")
    print("  1. Startup message")
    print("  2. Deal alert (SOF → JFK)")
    print("  3. Error alert")
    print("=" * 50 + "\n")
    
    return True

async def test_single_message():
    """Send a simple test message"""
    print("\n🦅 Sending test message to Telegram...\n")
    
    notifier = TelegramNotifier()
    
    test_message = """
🦅 <b>TITAN TEST MESSAGE</b>

This is a test message from PROJECT TITAN.

If you received this, your bot is configured correctly! ✅

Environment: {env}
"""
    
    env_type = "GitHub Actions" if os.environ.get("GITHUB_ACTIONS") else "Local"
    test_message = test_message.format(env=env_type)
    
    success = await notifier._send_message(notifier.admin_id, test_message)
    
    if success:
        print("✅ Test message sent successfully!")
        print("Check your Telegram now.\n")
        return True
    else:
        print("❌ Failed to send test message")
        print("Check your credentials and internet connection\n")
        return False

def main():
    """Main test function"""
    try:
        print("\nChoose test mode:")
        print("1. Quick test (single message)")
        print("2. Full test (all notification types)")
        print()
        
        choice = input("Enter choice (1 or 2, default=1): ").strip() or "1"
        
        if choice == "1":
            success = asyncio.run(test_single_message())
        elif choice == "2":
            success = asyncio.run(test_notifications())
        else:
            print("Invalid choice!")
            sys.exit(1)
        
        if success:
            print("✅ Bot is working perfectly!\n")
            sys.exit(0)
        else:
            print("❌ Bot test failed!\n")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Test cancelled by user\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error during test: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
