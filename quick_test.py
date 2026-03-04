"""
Quick test to verify:
1. COMMON_ASSETS list
2. CATEGORY_COLORS mapping
3. FRED data fetcher
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("="*70)
print("BRI APP - Quick Configuration Test")
print("="*70)

# Test 1: Common Assets
print("\n[Test 1] Common Assets List")
print("-"*70)
from bri_app.app import COMMON_ASSETS, ASSET_INFO, CATEGORY_COLORS

print(f"Total Common Assets: {len(COMMON_ASSETS)}")
print("\nCommon Assets with Categories:")
for asset in COMMON_ASSETS:
    if asset in ASSET_INFO:
        info = ASSET_INFO[asset]
        print(f"  {asset:20s} -> {info['name_en']:20s} ({info['category']})")
    else:
        print(f"  {asset:20s} -> [NOT FOUND IN ASSET_INFO]")

# Test 2: Category Colors
print("\n[Test 2] Category Color Mapping")
print("-"*70)
for category, color in CATEGORY_COLORS.items():
    print(f"  {category:20s} -> {color}")

# Test 3: Verify all categories in ASSET_INFO have colors
print("\n[Test 3] Category Coverage Check")
print("-"*70)
all_categories = set(info['category'] for info in ASSET_INFO.values())
print(f"Unique categories in ASSET_INFO: {len(all_categories)}")
for cat in sorted(all_categories):
    has_color = cat in CATEGORY_COLORS
    status = "✅" if has_color else "❌"
    print(f"  {status} {cat}")

# Test 4: FRED fetcher availability
print("\n[Test 4] FRED Data Fetcher")
print("-"*70)
try:
    from bri_app.data_sources.fred_fetcher import FREDDataFetcher
    fetcher = FREDDataFetcher()
    print(f"✅ FREDDataFetcher loaded successfully")
    print(f"   API Key: {fetcher.api_key[:10]}...")
    print(f"   Available series: {list(fetcher.FRED_SERIES.keys())}")
except Exception as e:
    print(f"❌ Error loading FREDDataFetcher: {e}")

print("\n" + "="*70)
print("Test Complete!")
print("="*70)

