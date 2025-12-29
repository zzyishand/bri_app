"""
SQLite数据库管理器
管理价格数据、BRI结果和更新日志
"""

import sqlite3
import pandas as pd
from datetime import datetime
from pathlib import Path
import json


class BRIDatabase:
    """BRI SQLite数据库管理器"""
    
    def __init__(self, db_path='data/bri_data.db'):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """初始化数据库表结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 1. 价格数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_data (
                asset_name TEXT NOT NULL,
                date DATE NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL NOT NULL,
                volume INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (asset_name, date)
            )
        ''')
        
        # 2. BRI结果表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bri_results (
                asset_name TEXT NOT NULL,
                date DATE NOT NULL,
                price REAL,
                returns REAL,
                composite_bri REAL,
                short_indicator REAL,
                mid_indicator REAL,
                long_indicator REAL,
                short_avg_percentile REAL,
                mid_avg_percentile REAL,
                long_avg_percentile REAL,
                full_data TEXT,
                calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (asset_name, date)
            )
        ''')
        
        # 3. 更新日志表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS update_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_name TEXT NOT NULL,
                update_type TEXT,
                status TEXT,
                rows_affected INTEGER,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 4. 元数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metadata (
                asset_name TEXT PRIMARY KEY,
                last_price_date DATE,
                last_bri_date DATE,
                total_records INTEGER,
                config_version TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_price_data(self, asset_name: str, df: pd.DataFrame):
        """保存价格数据（支持增量插入）"""
        conn = sqlite3.connect(self.db_path)
        
        # 准备数据
        df_save = df.reset_index()
        if 'Date' in df_save.columns:
            df_save = df_save.rename(columns={'Date': 'date'})
        elif df_save.index.name == 'Date':
            df_save = df_save.reset_index().rename(columns={'Date': 'date'})
        
        df_save['asset_name'] = asset_name
        df_save['date'] = pd.to_datetime(df_save['date']).dt.date
        
        # 准备列名映射
        column_mapping = {
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        }
        df_save = df_save.rename(columns=column_mapping)
        
        # 选择需要的列
        columns_to_save = ['asset_name', 'date', 'open', 'high', 'low', 'close', 'volume']
        existing_columns = [col for col in columns_to_save if col in df_save.columns]
        
        try:
            # 使用 INSERT OR REPLACE 来处理重复
            for _, row in df_save[existing_columns].iterrows():
                cursor = conn.cursor()
                placeholders = ', '.join(['?'] * len(existing_columns))
                columns_str = ', '.join(existing_columns)
                cursor.execute(
                    f"INSERT OR REPLACE INTO price_data ({columns_str}) VALUES ({placeholders})",
                    tuple(row[col] for col in existing_columns)
                )
            
            conn.commit()
            
            # 更新元数据
            self._update_metadata(conn, asset_name, 'price')
            
        finally:
            conn.close()
    
    def get_price_data(self, asset_name: str, start_date=None, end_date=None):
        """读取价格数据"""
        conn = sqlite3.connect(self.db_path)
        
        query = "SELECT date, open, high, low, close, volume FROM price_data WHERE asset_name = ?"
        params = [asset_name]
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        
        query += " ORDER BY date"
        
        df = pd.read_sql_query(query, conn, params=params, parse_dates=['date'])
        df = df.set_index('date')
        
        # 重命名列以匹配yfinance格式
        df = df.rename(columns={
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'volume': 'Volume'
        })
        
        conn.close()
        return df
    
    def get_last_date(self, asset_name: str, table='price_data'):
        """获取最新日期"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            f"SELECT MAX(date) FROM {table} WHERE asset_name = ?",
            (asset_name,)
        )
        result = cursor.fetchone()[0]
        conn.close()
        
        return pd.to_datetime(result) if result else None
    
    def save_bri_results(self, asset_name: str, df: pd.DataFrame):
        """保存BRI结果"""
        conn = sqlite3.connect(self.db_path)
        
        # 准备数据 - 保持原始的index（Date）
        df_save = df.copy()
        
        # 如果index是DatetimeIndex，重置为列
        if isinstance(df_save.index, pd.DatetimeIndex):
            df_save = df_save.reset_index()
            if 'index' in df_save.columns:
                df_save = df_save.rename(columns={'index': 'Date'})
        elif df_save.index.name:
            df_save = df_save.reset_index()
            
        df_save['asset_name'] = asset_name
        
        # 将完整数据存为JSON
        df_save['full_data'] = df_save.apply(lambda row: json.dumps(row.to_dict(), default=str), axis=1)
        
        try:
            for _, row in df_save.iterrows():
                cursor = conn.cursor()
                
                # 提取日期 - 兼容多种格式
                if 'Date' in row:
                    date_val = pd.to_datetime(row['Date']).date()
                elif 'date' in row:
                    date_val = pd.to_datetime(row['date']).date()
                else:
                    date_val = pd.to_datetime(row.iloc[0]).date()
                
                # 提取数值 - 保持原始值，不转换成0
                def get_float(key):
                    val = row.get(key)
                    if pd.isna(val):
                        return None
                    try:
                        return float(val)
                    except:
                        return None
                
                cursor.execute('''
                    INSERT OR REPLACE INTO bri_results 
                    (asset_name, date, price, returns, composite_bri, 
                     short_indicator, mid_indicator, long_indicator,
                     short_avg_percentile, mid_avg_percentile, long_avg_percentile, full_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    asset_name,
                    date_val,
                    get_float('price'),
                    get_float('returns'),
                    get_float('composite_bri'),
                    get_float('short_indicator'),
                    get_float('mid_indicator'),
                    get_float('long_indicator'),
                    get_float('short_avg_percentile'),
                    get_float('mid_avg_percentile'),
                    get_float('long_avg_percentile'),
                    row['full_data']
                ))
            
            conn.commit()
            self._update_metadata(conn, asset_name, 'bri')
            
        finally:
            conn.close()
    
    def get_bri_results(self, asset_name: str, start_date=None):
        """读取BRI结果"""
        conn = sqlite3.connect(self.db_path)
        
        query = "SELECT * FROM bri_results WHERE asset_name = ?"
        params = [asset_name]
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        
        query += " ORDER BY date"
        
        df = pd.read_sql_query(query, conn, params=params, parse_dates=['date'])
        
        conn.close()
        
        if df.empty:
            return df
        
        # 重命名date列为Date，并设置为索引
        df = df.rename(columns={'date': 'Date'})
        # 不要设置为index，保持Date作为列
        # df = df.set_index('Date')
        
        return df
    
    def get_all_assets(self):
        """获取所有资产列表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT asset_name FROM bri_results ORDER BY asset_name")
        assets = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return assets
    
    def log_update(self, asset_name: str, update_type: str, 
                   status: str, rows: int, message: str):
        """记录更新日志"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO update_log (asset_name, update_type, status, rows_affected, message)
            VALUES (?, ?, ?, ?, ?)
        ''', (asset_name, update_type, status, rows, message))
        
        conn.commit()
        conn.close()
    
    def get_update_history(self, limit=50):
        """获取更新历史"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query(
            f"SELECT * FROM update_log ORDER BY created_at DESC LIMIT {limit}",
            conn,
            parse_dates=['created_at']
        )
        conn.close()
        return df
    
    def _update_metadata(self, conn, asset_name: str, update_type: str):
        """更新元数据"""
        cursor = conn.cursor()
        
        if update_type == 'price':
            cursor.execute('''
                INSERT OR REPLACE INTO metadata (asset_name, last_price_date, updated_at)
                VALUES (
                    ?,
                    (SELECT MAX(date) FROM price_data WHERE asset_name = ?),
                    CURRENT_TIMESTAMP
                )
            ''', (asset_name, asset_name))
        
        elif update_type == 'bri':
            cursor.execute('''
                INSERT OR REPLACE INTO metadata (asset_name, last_bri_date, updated_at)
                VALUES (
                    ?,
                    (SELECT MAX(date) FROM bri_results WHERE asset_name = ?),
                    CURRENT_TIMESTAMP
                )
            ''', (asset_name, asset_name))
        
        conn.commit()
    
    def get_metadata(self, asset_name: str = None):
        """获取元数据"""
        conn = sqlite3.connect(self.db_path)
        
        if asset_name:
            query = "SELECT * FROM metadata WHERE asset_name = ?"
            df = pd.read_sql_query(query, conn, params=[asset_name])
        else:
            query = "SELECT * FROM metadata ORDER BY asset_name"
            df = pd.read_sql_query(query, conn)
        
        conn.close()
        return df

