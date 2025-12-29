"""
测试FRED数据获取功能
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bri_app.data_sources.fred_fetcher import FREDDataFetcher


def test_fred_spreads():
    """测试获取FRED信用利差数据"""
    print("="*70)
    print("测试FRED信用利差数据获取")
    print("="*70)
    
    fetcher = FREDDataFetcher()
    
    # 测试IG Spread
    print("\n[1/2] 测试IG Spread (投资级利差)...")
    df_ig, meta_ig = fetcher.fetch_credit_spread('IG_SPREAD', years_back=10)
    if df_ig is not None:
        print(f"\n✅ IG Spread数据获取成功:")
        print(f"   总行数: {len(df_ig)}")
        print(f"   日期范围: {df_ig.index[0]} 到 {df_ig.index[-1]}")
        print(f"\n   最新5行数据:")
        print(df_ig.tail())
    else:
        print("❌ IG Spread数据获取失败")
    
    # 测试HY Spread
    print("\n" + "-"*70)
    print("\n[2/2] 测试HY Spread (高收益利差)...")
    df_hy, meta_hy = fetcher.fetch_credit_spread('HY_SPREAD', years_back=10)
    if df_hy is not None:
        print(f"\n✅ HY Spread数据获取成功:")
        print(f"   总行数: {len(df_hy)}")
        print(f"   日期范围: {df_hy.index[0]} 到 {df_hy.index[-1]}")
        print(f"\n   最新5行数据:")
        print(df_hy.tail())
    else:
        print("❌ HY Spread数据获取失败")
    
    print("\n" + "="*70)
    print("测试完成!")
    print("="*70)


if __name__ == "__main__":
    test_fred_spreads()

