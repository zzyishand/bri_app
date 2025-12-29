"""
Custom Ticker Analysis Service
允许用户输入任意Yahoo Finance ticker进行即时BRI分析
"""

import pandas as pd
from datetime import datetime
from typing import Optional, Tuple, Dict
import yfinance as yf

from database.bri_database import BRIDatabase
from data_fetch_and_process.bri_data_fetcher import fetch_asset_data
from indicator.bri_calculator_v2 import BRICalculatorV2
from indicator.bri_config import get_config


class CustomTickerService:
    """自定义Ticker分析服务"""
    
    def __init__(self, db_path='data/bri_data.db'):
        self.db = BRIDatabase(db_path)
        self.config = get_config('default')
        self.calculator = BRICalculatorV2(self.config)
    
    def check_ticker_exists(self, ticker: str) -> Dict:
        """
        检查ticker是否已在数据库中
        
        Returns:
        --------
        dict: {
            'exists': bool,
            'asset_name': str or None,
            'last_date': datetime or None,
            'rows': int
        }
        """
        # 在数据库中查找所有资产，检查是否有匹配的ticker
        all_assets = self.db.get_all_assets()
        
        # 简单匹配：将ticker转换为可能的资产名
        # 例如：BTC-USD -> BITCOIN, ^DJI -> DOW_JONES
        ticker_upper = ticker.upper().replace('-', '_').replace('^', '').replace('=', '_')
        
        for asset in all_assets:
            if ticker_upper in asset or asset in ticker_upper:
                last_date = self.db.get_last_date(asset, 'bri_results')
                price_data = self.db.get_price_data(asset)
                return {
                    'exists': True,
                    'asset_name': asset,
                    'last_date': last_date,
                    'rows': len(price_data) if not price_data.empty else 0
                }
        
        return {
            'exists': False,
            'asset_name': None,
            'last_date': None,
            'rows': 0
        }
    
    def validate_ticker(self, ticker: str) -> Tuple[bool, str, Optional[dict]]:
        """
        验证ticker是否在Yahoo Finance上存在
        
        Returns:
        --------
        tuple: (is_valid, message, info_dict)
        """
        try:
            print(f"Validating ticker: {ticker}")
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # 检查是否有基本信息
            if not info or len(info) < 3:
                return False, f"Ticker '{ticker}' not found on Yahoo Finance", None
            
            # 尝试获取少量历史数据验证
            hist = stock.history(period='5d')
            if hist.empty:
                return False, f"Ticker '{ticker}' has no price data available", None
            
            # 提取有用的信息
            ticker_info = {
                'name': info.get('longName', info.get('shortName', ticker)),
                'type': info.get('quoteType', 'Unknown'),
                'currency': info.get('currency', 'USD'),
                'exchange': info.get('exchange', 'Unknown'),
                'latest_price': hist['Close'].iloc[-1] if not hist.empty else None,
                'latest_date': hist.index[-1] if not hist.empty else None
            }
            
            return True, "Ticker is valid", ticker_info
            
        except Exception as e:
            return False, f"Error validating ticker: {str(e)}", None
    
    def analyze_custom_ticker(self, 
                              ticker: str,
                              custom_name: Optional[str] = None,
                              category: str = 'Custom',
                              years_back: int = 10,
                              save_to_db: bool = False) -> Dict:
        """
        分析自定义ticker并计算BRI
        
        Parameters:
        -----------
        ticker : str
            Yahoo Finance ticker symbol
        custom_name : str, optional
            自定义资产名称
        category : str
            资产类别
        years_back : int
            获取多少年的历史数据
        save_to_db : bool
            是否保存到数据库
        
        Returns:
        --------
        dict: 分析结果
        """
        try:
            # 1. 验证ticker
            print(f"[1/5] Validating ticker {ticker}...")
            is_valid, message, ticker_info = self.validate_ticker(ticker)
            
            if not is_valid:
                return {
                    'success': False,
                    'error': message,
                    'step': 'validation'
                }
            
            print(f"  ✓ Valid ticker: {ticker_info['name']}")
            
            # 2. 获取历史数据
            print(f"[2/5] Fetching {years_back} years of data...")
            asset_name = custom_name or ticker.replace('^', '').replace('-', '_').upper()
            
            price_data, metadata = fetch_asset_data(
                asset_name,
                ticker,
                period=f'{years_back}y',
                interval='1d'
            )
            
            if price_data is None or price_data.empty:
                return {
                    'success': False,
                    'error': 'Failed to fetch price data',
                    'step': 'data_fetch'
                }
            
            print(f"  ✓ Fetched {len(price_data)} rows")
            
            # 3. 计算BRI
            print(f"[3/5] Calculating BRI indicators...")
            bri_results = self.calculator.calculate_full_bri(
                price_data,
                asset_name=asset_name
            )
            
            if bri_results is None or bri_results.empty:
                return {
                    'success': False,
                    'error': 'Failed to calculate BRI',
                    'step': 'bri_calculation'
                }
            
            # 统计有效BRI数据
            valid_bri = bri_results['composite_bri'].notna().sum()
            print(f"  ✓ Calculated BRI: {valid_bri} valid rows")
            
            # 4. 保存到数据库（可选）
            if save_to_db:
                print(f"[4/5] Saving to database...")
                self.db.save_price_data(asset_name, price_data)
                self.db.save_bri_results(asset_name, bri_results)
                self.db.log_update(
                    asset_name,
                    'custom_ticker_analysis',
                    'success',
                    len(bri_results),
                    f"Custom ticker {ticker} analyzed and saved"
                )
                print(f"  ✓ Saved to database as '{asset_name}'")
            else:
                print(f"[4/5] Skipping database save (save_to_db=False)")
            
            # 5. 准备返回结果
            print(f"[5/5] Preparing results...")
            latest_data = bri_results[bri_results['composite_bri'].notna()].iloc[-1]
            
            result = {
                'success': True,
                'ticker': ticker,
                'asset_name': asset_name,
                'ticker_info': ticker_info,
                'category': category,
                'data_info': {
                    'total_rows': len(price_data),
                    'date_range': f"{price_data.index[0].strftime('%Y-%m-%d')} to {price_data.index[-1].strftime('%Y-%m-%d')}",
                    'years_coverage': (price_data.index[-1] - price_data.index[0]).days / 365.25
                },
                'bri_results': bri_results,
                'latest_metrics': {
                    'date': latest_data.name if hasattr(latest_data, 'name') else latest_data.get('Date'),
                    'price': float(latest_data['price']),
                    'returns': float(latest_data['returns']) if pd.notna(latest_data['returns']) else 0.0,
                    'composite_bri': float(latest_data['composite_bri']),
                    'short_indicator': float(latest_data['short_indicator']) if pd.notna(latest_data['short_indicator']) else None,
                    'mid_indicator': float(latest_data['mid_indicator']) if pd.notna(latest_data['mid_indicator']) else None,
                    'long_indicator': float(latest_data['long_indicator']) if pd.notna(latest_data['long_indicator']) else None
                },
                'saved_to_db': save_to_db
            }
            
            print(f"  ✓ Analysis complete!")
            return result
            
        except Exception as e:
            import traceback
            return {
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc(),
                'step': 'unknown'
            }
    
    def get_saved_custom_tickers(self) -> list:
        """获取所有保存的自定义ticker"""
        all_assets = self.db.get_all_assets()
        # 可以根据命名规则或元数据过滤出自定义ticker
        return all_assets


# 测试函数
def test_custom_ticker():
    """测试自定义ticker分析"""
    service = CustomTickerService()
    
    # 测试ticker: TSLA (Tesla)
    print("="*70)
    print("Testing Custom Ticker Analysis: TSLA")
    print("="*70)
    
    result = service.analyze_custom_ticker(
        ticker='TSLA',
        custom_name='TESLA',
        category='Tech Stock',
        years_back=5,
        save_to_db=False
    )
    
    if result['success']:
        print("\n✅ Analysis Successful!")
        print(f"Ticker: {result['ticker']}")
        print(f"Name: {result['ticker_info']['name']}")
        print(f"Latest BRI: {result['latest_metrics']['composite_bri']:.2%}")
        print(f"Latest Price: ${result['latest_metrics']['price']:.2f}")
    else:
        print(f"\n❌ Analysis Failed: {result['error']}")


if __name__ == "__main__":
    test_custom_ticker()

