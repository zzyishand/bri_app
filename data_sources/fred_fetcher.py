"""
FRED (Federal Reserve Economic Data) Data Fetcher
Fetches credit spread data from FRED API
"""

import pandas as pd
import requests
from datetime import datetime, timedelta
from typing import Optional, Tuple


class FREDDataFetcher:
    """FRED API数据获取器"""
    
    # FRED API配置
    FRED_API_KEY = '1d0565998ba35f78c5b572fa1f865a84'
    FRED_API_URL = 'https://api.stlouisfed.org/fred/series/observations'
    
    # 信用利差系列
    FRED_SERIES = {
        'IG_SPREAD': {
            'series_id': 'BAMLC0A0CM',
            'name': 'ICE BofA US Corporate Index OAS',
            'description': 'Investment Grade Corporate Bond Spread',
            'category': 'Credit Spread'
        },
        'HY_SPREAD': {
            'series_id': 'BAMLH0A0HYM2',
            'name': 'ICE BofA US High Yield Index OAS',
            'description': 'High Yield Corporate Bond Spread',
            'category': 'Credit Spread'
        }
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化FRED数据获取器
        
        Parameters:
        -----------
        api_key : str, optional
            FRED API密钥，如果不提供则使用默认密钥
        """
        self.api_key = api_key or self.FRED_API_KEY
    
    def fetch_series(self, 
                    series_id: str,
                    start_date: Optional[str] = None,
                    end_date: Optional[str] = None) -> Tuple[Optional[pd.DataFrame], Optional[dict]]:
        """
        从FRED API获取数据系列
        
        Parameters:
        -----------
        series_id : str
            FRED系列ID（如 'BAMLC0A0CM'）
        start_date : str, optional
            开始日期 (YYYY-MM-DD格式)
        end_date : str, optional
            结束日期 (YYYY-MM-DD格式)
        
        Returns:
        --------
        tuple: (DataFrame, metadata dict)
        """
        try:
            # 构建API请求参数
            params = {
                'series_id': series_id,
                'api_key': self.api_key,
                'file_type': 'json'
            }
            
            # 添加日期范围
            if start_date:
                params['observation_start'] = start_date
            if end_date:
                params['observation_end'] = end_date
            
            print(f"Fetching FRED data for {series_id}...")
            
            # 发送API请求
            response = requests.get(self.FRED_API_URL, params=params, timeout=30)
            response.raise_for_status()
            
            # 解析JSON响应
            data = response.json()
            
            if 'observations' not in data:
                print(f"  [WARNING] No observations found for {series_id}")
                return None, None
            
            # 转换为DataFrame
            observations = data['observations']
            df = pd.DataFrame(observations)
            
            # 处理数据
            df['date'] = pd.to_datetime(df['date'])
            df['value'] = pd.to_numeric(df['value'], errors='coerce')
            
            # 过滤掉 '.' 值（缺失数据）
            df = df[df['value'].notna()].copy()
            
            # 设置日期为索引
            df = df.set_index('date')
            
            # 重命名value列为Close（与yfinance格式一致）
            df = df.rename(columns={'value': 'Close'})
            
            # 只保留Close列
            df = df[['Close']]
            
            # 元数据
            metadata = {
                'series_id': series_id,
                'rows': len(df),
                'start_date': df.index[0] if not df.empty else None,
                'end_date': df.index[-1] if not df.empty else None,
                'date_range_years': (df.index[-1] - df.index[0]).days / 365.25 if not df.empty else 0
            }
            
            # 显示信息
            print(f"  [OK] Successfully fetched {metadata['rows']} rows")
            if not df.empty:
                print(f"  [OK] Date range: {metadata['start_date'].strftime('%Y-%m-%d')} to {metadata['end_date'].strftime('%Y-%m-%d')}")
                print(f"  [OK] Coverage: {metadata['date_range_years']:.1f} years")
            
            return df, metadata
        
        except requests.exceptions.RequestException as e:
            print(f"  [ERROR] Request error for {series_id}: {str(e)}")
            return None, None
        except Exception as e:
            print(f"  [ERROR] Error fetching {series_id}: {str(e)}")
            return None, None
    
    def fetch_credit_spread(self, 
                          spread_type: str,
                          years_back: int = 10) -> Tuple[Optional[pd.DataFrame], Optional[dict]]:
        """
        获取信用利差数据
        
        Parameters:
        -----------
        spread_type : str
            利差类型：'IG_SPREAD' 或 'HY_SPREAD'
        years_back : int
            获取多少年的历史数据
        
        Returns:
        --------
        tuple: (DataFrame, metadata dict)
        """
        if spread_type not in self.FRED_SERIES:
            print(f"  [ERROR] Unknown spread type: {spread_type}")
            print(f"  [INFO] Available types: {list(self.FRED_SERIES.keys())}")
            return None, None
        
        series_info = self.FRED_SERIES[spread_type]
        series_id = series_info['series_id']
        
        # 计算开始日期
        start_date = (datetime.now() - timedelta(days=years_back*365)).strftime('%Y-%m-%d')
        
        print(f"\nFetching {series_info['name']}...")
        print(f"  Series ID: {series_id}")
        print(f"  Description: {series_info['description']}")
        
        return self.fetch_series(series_id, start_date=start_date)
    
    @classmethod
    def get_all_spreads(cls, years_back: int = 10) -> dict:
        """
        获取所有信用利差数据
        
        Parameters:
        -----------
        years_back : int
            获取多少年的历史数据
        
        Returns:
        --------
        dict: {spread_type: (DataFrame, metadata)}
        """
        fetcher = cls()
        results = {}
        
        for spread_type in cls.FRED_SERIES.keys():
            df, metadata = fetcher.fetch_credit_spread(spread_type, years_back)
            if df is not None:
                results[spread_type] = (df, metadata)
        
        return results


# 测试函数
def test_fred_fetcher():
    """测试FRED数据获取"""
    print("="*70)
    print("测试FRED数据获取")
    print("="*70)
    
    fetcher = FREDDataFetcher()
    
    # 测试IG Spread
    df_ig, meta_ig = fetcher.fetch_credit_spread('IG_SPREAD', years_back=10)
    if df_ig is not None:
        print(f"\nIG Spread数据:")
        print(df_ig.tail())
    
    # 测试HY Spread
    df_hy, meta_hy = fetcher.fetch_credit_spread('HY_SPREAD', years_back=10)
    if df_hy is not None:
        print(f"\nHY Spread数据:")
        print(df_hy.tail())
    
    print("\n" + "="*70)
    print("测试完成!")
    print("="*70)


if __name__ == "__main__":
    test_fred_fetcher()

