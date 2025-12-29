"""
BRI增量更新服务
检测新数据并智能更新BRI
"""

import sys
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta

# 添加父目录到路径以导入indicator模块
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from database.bri_database import BRIDatabase
from data_fetch_and_process.bri_data_fetcher import fetch_asset_data
from data_sources.fred_fetcher import FREDDataFetcher
from indicator.bri_calculator_v2 import BRICalculatorV2
from indicator.bri_config import get_config


class BRIUpdateService:
    """BRI增量更新服务"""
    
    def __init__(self, db_path='data/bri_data.db'):
        self.db = BRIDatabase(db_path)
        self.config = get_config('default')
        self.calculator = BRICalculatorV2(self.config)
        self.fred_fetcher = FREDDataFetcher()
        
        # 需要的历史天数（用于计算百分位数）
        self.required_history = 1260  # ~5年
        
        # FRED数据源的资产列表
        self.fred_assets = ['IG_SPREAD', 'HY_SPREAD']
    
    def check_for_updates(self, asset_name: str, ticker: str = None):
        """
        检查是否有新数据需要更新
        
        Returns:
        --------
        dict: {
            'has_new_data': bool,
            'last_db_date': date,
            'latest_available_date': date,
            'new_rows': int
        }
        """
        # 获取数据库中的最新日期
        last_db_date = self.db.get_last_date(asset_name, 'price_data')
        
        try:
            # 检查是否为FRED数据源
            if asset_name in self.fred_assets:
                # 使用FRED API快速检查
                recent_data, _ = self.fred_fetcher.fetch_credit_spread(
                    asset_name, 
                    years_back=1  # 只获取最近1年快速检查
                )
            else:
                # 获取Yahoo Finance最新数据（只获取最近几天做快速检查）
                recent_data, _ = fetch_asset_data(
                    asset_name, 
                    ticker, 
                    period='5d',  # 只检查最近5天
                    interval='1d'
                )
            
            if recent_data is None or recent_data.empty:
                return {
                    'has_new_data': False,
                    'error': 'Failed to fetch data'
                }
            
            latest_available_date = recent_data.index[-1]
            
            # 比较日期
            if last_db_date is None:
                # 第一次获取数据
                return {
                    'has_new_data': True,
                    'last_db_date': None,
                    'latest_available_date': latest_available_date,
                    'new_rows': 'First time',
                    'update_type': 'full'
                }
            
            # 检查是否有新数据
            if latest_available_date > last_db_date:
                new_rows = len(recent_data[recent_data.index > last_db_date])
                return {
                    'has_new_data': True,
                    'last_db_date': last_db_date,
                    'latest_available_date': latest_available_date,
                    'new_rows': new_rows,
                    'update_type': 'incremental'
                }
            else:
                return {
                    'has_new_data': False,
                    'last_db_date': last_db_date,
                    'latest_available_date': latest_available_date,
                    'message': 'Already up to date'
                }
                
        except Exception as e:
            return {
                'has_new_data': False,
                'error': str(e)
            }
    
    def update_asset(self, asset_name: str, ticker: str = None, force_full=False):
        """
        更新单个资产的价格和BRI
        
        Returns:
        --------
        dict: 更新结果
        """
        try:
            # 检查是否首次使用（数据库为空）
            last_price_date = self.db.get_last_date(asset_name, 'price_data')
            is_first_time = (last_price_date is None)
            
            # 1. 获取最新价格数据
            print(f"[1/4] Fetching latest price data for {asset_name}...")
            
            # 检查是否为FRED数据源
            if asset_name in self.fred_assets:
                # 使用FRED API获取数据
                print(f"      → Using FRED API for {asset_name}")
                years_back = 10 if (is_first_time or force_full) else 2
                price_data, metadata = self.fred_fetcher.fetch_credit_spread(
                    asset_name, 
                    years_back=years_back
                )
            else:
                # 使用Yahoo Finance获取数据
                # 智能选择下载范围：
                # - 首次使用或强制完整：下载10年历史数据（足够计算BRI）
                # - 增量更新：下载最近2年以确保有足够数据
                # 注意：不使用'max'因为Yahoo Finance在某些资产上会失败
                if is_first_time or force_full:
                    period = '10y'  # 10年数据足够BRI计算（需要5年）
                    print(f"      → Downloading 10 years historical data (is_first_time={is_first_time}, force_full={force_full})")
                else:
                    period = '2y'
                    print(f"      → Downloading recent 2 years data (incremental update)")
                
                print(f"      → Period parameter: {period}")
                
                price_data, metadata = fetch_asset_data(
                    asset_name,
                    ticker,
                    period=period,
                    interval='1d'
                )
            
            if price_data is not None:
                print(f"      → Downloaded {len(price_data)} rows, date range: {price_data.index[0]} to {price_data.index[-1]}")
            
            if price_data is None:
                raise Exception("Failed to fetch price data")
            
            # 2. 保存到数据库
            print(f"[2/4] Saving price data to database...")
            self.db.save_price_data(asset_name, price_data)
            self.db.log_update(
                asset_name, 'price_fetch', 'success',
                len(price_data), f"Fetched {len(price_data)} rows"
            )
            
            # 3. 检查BRI是否需要更新
            last_bri_date = self.db.get_last_date(asset_name, 'bri_results')
            
            if force_full or last_bri_date is None:
                # 完全重新计算
                print(f"[3/4] Calculating BRI (full recalculation)...")
                full_price_data = self.db.get_price_data(asset_name)
                bri_results = self.calculator.calculate_full_bri(
                    full_price_data,
                    price_column='Close',
                    asset_name=asset_name
                )
                new_bri_rows = len(bri_results)
                
            else:
                # 增量更新：只计算新日期
                print(f"[3/4] Calculating BRI (incremental update)...")
                
                # 获取足够的历史数据（用于计算百分位数）
                start_date = last_bri_date - timedelta(days=self.required_history)
                historical_data = self.db.get_price_data(asset_name, start_date=start_date)
                
                # 计算完整BRI
                all_results = self.calculator.calculate_full_bri(
                    historical_data,
                    price_column='Close',
                    asset_name=asset_name
                )
                
                # 只保存新日期的结果
                bri_results = all_results[all_results.index > last_bri_date]
                new_bri_rows = len(bri_results)
            
            # 4. 保存BRI结果
            print(f"[4/4] Saving BRI results to database...")
            if new_bri_rows > 0:
                self.db.save_bri_results(asset_name, bri_results)
                self.db.log_update(
                    asset_name, 'bri_calc', 'success',
                    new_bri_rows, f"Calculated {new_bri_rows} new BRI rows"
                )
            
            return {
                'success': True,
                'asset_name': asset_name,
                'price_rows': len(price_data),
                'new_bri_rows': new_bri_rows,
                'last_date': price_data.index[-1],
                'message': f"Successfully updated {asset_name}"
            }
            
        except Exception as e:
            error_msg = f"Failed to update {asset_name}: {str(e)}"
            self.db.log_update(asset_name, 'update_failed', 'error', 0, error_msg)
            
            return {
                'success': False,
                'asset_name': asset_name,
                'error': str(e)
            }

