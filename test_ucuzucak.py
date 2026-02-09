#!/usr/bin/env python3
"""
Quick Test Script - PROJECT TITAN V2.3
Tests key features without full cycle
"""

import asyncio
import sys

from config import TitanConfig
from ucuzaucak_scraper import UcuzaucakScraper

async def test_ucuzaucak():
    """Test ucuzaucak.net scraper"""
    print("\n" + "=" * 60)
    print("📊 TESTING ucuzaucak.net SCRAPER")
    print("=" * 60 + "\n")
    
    config = TitanConfig()
    scraper = UcuzaucakScraper(config)
    
    # Test single page
    print("Testing page 1...")
    deals = await scraper.scrape_page(page_num=1)
    
    if deals:
        print(f"✅ Found {len(deals)} deals on page 1\n")
        
        # Show first 3
        for i, deal in enumerate(deals[:3], 1):
            print(f"{i}. {deal['origin']} → {deal['destination']}: {deal['price']:,.0f} TL")
        
        # Aggregate by route
        print("\n" + "-" * 60)
        print("Aggregating by route...")
        stats = scraper.aggregate_by_route(deals)
        
        print(f"\n✅ Found {len(stats)} unique routes\n")
        
        for route_key, data in list(stats.items())[:5]:
            print(f"{route_key}:")
            print(f"  Min: {data['min']:,.0f} TL")
            print(f"  Avg: {data['avg']:,.0f} TL")
            print(f"  Max: {data['max']:,.0f} TL")
            print(f"  Samples: {data['count']}")
            print()
        
        # Test comparison
        if stats:
            first_route = list(stats.keys())[0]
            test_price = stats[first_route]['avg'] * 0.8  # %20 ucuz
            
            print("-" * 60)
            print(f"Testing price comparison for {first_route}")
            print(f"Test price: {test_price:,.0f} TL")
            
            comparison = scraper.compare_with_historical(test_price, first_route, stats)
            
            print(f"\nPercentile: {comparison.get('percentile', 0):.0f}%")
            print(f"Recommendation: {comparison.get('recommendation', 'N/A')}")
            print(f"Is Good Deal: {comparison.get('is_good_deal', False)}")
        
        print("\n" + "=" * 60)
        print("✅ ucuzaucak.net scraper test PASSED!")
        print("=" * 60 + "\n")
        
        return True
    else:
        print("❌ No deals found!")
        return False

async def main():
    """Main test function"""
    try:
        success = await test_ucuzaucak()
        
        if success:
            print("\n✅ All tests passed!\n")
            sys.exit(0)
        else:
            print("\n❌ Tests failed!\n")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Test error: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
