"""
应用配置文件
"""

from pathlib import Path

# 数据库配置
DB_PATH = Path(__file__).parent / 'data' / 'bri_data.db'

# 数据源配置
DATA_SOURCE = 'yahoo_finance'
DEFAULT_PERIOD = 'max'  # 默认获取所有历史数据
DEFAULT_INTERVAL = '1d'  # 日线数据

# BRI计算配置
BRI_CONFIG = 'default'  # 使用默认配置

# 历史数据窗口（用于增量更新）
REQUIRED_HISTORY_DAYS = 1260  # ~5年，用于计算百分位数

# UI配置
APP_TITLE = "BRI Bubble Risk Indicator"
APP_ICON = "📊"
DEFAULT_LOOKBACK_DAYS = 365  # 默认回看期

