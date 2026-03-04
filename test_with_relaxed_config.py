"""
使用宽松配置测试BRI计算
"""

import sys
from pathlib import Path
import pandas as pd

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from data_fetch_and_process.bri_data_fetcher import fetch_asset_data
from indicator.bri_calculator_v2 import BRICalculatorV2
from indicator.bri_config import BRIConfig, MomentWindow, MomentWeights

def test_with_custom_config():
    print("="*70)
    print("使用宽松配置测试BRI计算")
    print("="*70)
    
    # 1. 获取数据
    print("\n1. 获取DOW_JONES数据...")
    price_data, _ = fetch_asset_data('DOW_JONES', '^DJI', period='max')
    
    print(f"   数据行数: {len(price_data)}")
    print(f"   日期范围: {price_data.index[0]} 到 {price_data.index[-1]}")
    days = (price_data.index[-1] - price_data.index[0]).days
    print(f"   历史长度: {days} 天 ({days/365:.1f} 年)")
    
    # 2. 使用宽松配置
    print("\n2. 创建宽松配置（min_periods_ratio=0.3）...")
    
    config = BRIConfig(
        windows={
            'short_term': MomentWindow(moment_window=63, percentile_lookback=252),   # 3月 vs 1年
            'mid_term': MomentWindow(moment_window=126, percentile_lookback=756),    # 6月 vs 3年
            'long_term': MomentWindow(moment_window=252, percentile_lookback=1260)   # 1年 vs 5年
        },
        weights=MomentWeights(
            returns=0.25,
            volatility=0.25,
            momentum=0.25,
            fragility=0.25
        ),
        min_periods_ratio=0.3,  # 降低到30%！（默认可能是50-80%）
        use_log_returns=True,
        remove_outliers=False,
        use_dynamic_scaling=True,
        scaling_steepness=2.0
    )
    
    print(f"   短期需要最少: {252 * 0.3:.0f} 天")
    print(f"   中期需要最少: {756 * 0.3:.0f} 天")
    print(f"   长期需要最少: {1260 * 0.3:.0f} 天")
    
    # 3. 计算BRI
    print("\n3. 计算BRI...")
    calculator = BRICalculatorV2(config)
    
    results = calculator.calculate_full_bri(
        price_data,
        price_column='Close',
        asset_name='DOW_JONES'
    )
    
    # 4. 检查结果
    print("\n4. 检查计算结果...")
    
    key_cols = ['composite_bri', 'short_indicator', 'mid_indicator', 'long_indicator']
    for col in key_cols:
        if col in results.columns:
            valid_count = results[col].notna().sum()
            total_count = len(results)
            pct = valid_count / total_count * 100
            print(f"   {col}: {valid_count}/{total_count} ({pct:.1f}%)")
            
            if valid_count > 0:
                print(f"      → 最小值: {results[col].min():.4f}")
                print(f"      → 最大值: {results[col].max():.4f}")
                print(f"      → 最新值: {results[col].iloc[-1]:.4f}")
    
    # 5. 显示最后几行
    print("\n5. 最后5行数据:")
    display_cols = ['price', 'composite_bri', 'short_indicator', 'mid_indicator', 'long_indicator']
    existing_cols = [col for col in display_cols if col in results.columns]
    print(results[existing_cols].tail())
    
    print("\n" + "="*70)
    print("如果现在有更多有效数据，说明min_periods_ratio设置太高！")
    print("="*70)

if __name__ == "__main__":
    test_with_custom_config()

