"""
测试BRI计算 - 检查计算结果是否正确
"""

import sys
from pathlib import Path
import pandas as pd

# 添加父目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.bri_database import BRIDatabase
from data_fetch_and_process.bri_data_fetcher import fetch_asset_data
from indicator.bri_calculator_v2 import BRICalculatorV2
from indicator.bri_config import get_config

def test_bri_calculation():
    print("="*70)
    print("测试BRI计算流程")
    print("="*70)
    
    # 1. 获取数据
    print("\n1. 获取BITCOIN数据...")
    price_data, metadata = fetch_asset_data(
        'BITCOIN',
        'BTC-USD',
        period='max',
        interval='1d'
    )
    
    print(f"   数据行数: {len(price_data)}")
    print(f"   日期范围: {price_data.index[0]} 到 {price_data.index[-1]}")
    print(f"   历史长度: {(price_data.index[-1] - price_data.index[0]).days} 天")
    
    # 2. 计算BRI
    print("\n2. 计算BRI...")
    config = get_config('default')
    calculator = BRICalculatorV2(config)
    
    results = calculator.calculate_full_bri(
        price_data,
        price_column='Close',
        asset_name='BITCOIN'
    )
    
    print(f"   结果行数: {len(results)}")
    print(f"   结果列数: {len(results.columns)}")
    
    # 3. 检查结果
    print("\n3. 检查计算结果...")
    
    # 检查关键列的有效数据
    key_cols = ['composite_bri', 'short_indicator', 'mid_indicator', 'long_indicator']
    for col in key_cols:
        if col in results.columns:
            valid_count = results[col].notna().sum()
            total_count = len(results)
            pct = valid_count / total_count * 100 if total_count > 0 else 0
            print(f"   {col}: {valid_count}/{total_count} ({pct:.1f}%)")
            
            # 显示统计
            if valid_count > 0:
                print(f"      → 最小值: {results[col].min():.4f}")
                print(f"      → 最大值: {results[col].max():.4f}")
                print(f"      → 平均值: {results[col].mean():.4f}")
        else:
            print(f"   {col}: ❌ 列不存在")
    
    # 4. 显示最后几行
    print("\n4. 最后5行数据:")
    display_cols = ['price', 'composite_bri', 'short_indicator', 'mid_indicator', 'long_indicator']
    existing_cols = [col for col in display_cols if col in results.columns]
    print(results[existing_cols].tail())
    
    # 5. 检查是否保存到数据库时出问题
    print("\n5. 测试保存到数据库...")
    db = BRIDatabase('data/test_bri.db')
    db.save_bri_results('BITCOIN_TEST', results)
    
    # 读取回来
    loaded = db.get_bri_results('BITCOIN_TEST')
    print(f"   保存前行数: {len(results)}")
    print(f"   读取后行数: {len(loaded)}")
    
    # 检查保存后的数据
    for col in key_cols:
        if col in loaded.columns:
            valid_count = loaded[col].notna().sum()
            print(f"   {col} (保存后): {valid_count} 行有效")
    
    print("\n" + "="*70)
    print("测试完成!")
    print("="*70)

if __name__ == "__main__":
    test_bri_calculation()

