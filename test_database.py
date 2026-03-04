"""
测试数据库数据
快速检查数据库中是否有数据
"""

import sys
from pathlib import Path

# 添加父目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.bri_database import BRIDatabase

def test_database():
    print("="*60)
    print("测试BRI数据库")
    print("="*60)
    
    db = BRIDatabase('data/bri_data.db')
    
    # 1. 检查所有资产
    print("\n1. 检查资产列表...")
    assets = db.get_all_assets()
    print(f"   找到 {len(assets)} 个资产:")
    for asset in assets:
        print(f"   - {asset}")
    
    if not assets:
        print("\n❌ 数据库中没有BRI结果！")
        print("   请先到 'Data Update' 页面更新数据。")
        return
    
    # 2. 检查第一个资产的数据
    print(f"\n2. 检查第一个资产 ({assets[0]}) 的数据...")
    df = db.get_bri_results(assets[0])
    
    print(f"   数据行数: {len(df)}")
    print(f"   数据列: {df.columns.tolist()}")
    print(f"\n   最后5行数据:")
    print(df.tail())
    
    # 3. 检查关键列
    print(f"\n3. 检查关键列是否存在...")
    required_cols = ['composite_bri', 'short_indicator', 'mid_indicator', 'long_indicator', 'price', 'returns']
    for col in required_cols:
        exists = col in df.columns
        has_data = df[col].notna().sum() if exists else 0
        print(f"   {col}: {'✅' if exists else '❌'} (有效数据: {has_data}行)")
    
    # 4. 检查元数据
    print(f"\n4. 检查元数据...")
    metadata = db.get_metadata()
    if not metadata.empty:
        print(metadata)
    else:
        print("   没有元数据")
    
    print("\n" + "="*60)
    print("测试完成!")
    print("="*60)

if __name__ == "__main__":
    test_database()

