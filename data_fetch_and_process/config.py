"""
Configuration file for BRI data fetching and processing
"""

from datetime import datetime

# Project paths
DATA_DIR = "data"
RAW_DATA_DIR = f"{DATA_DIR}/raw"
PROCESSED_DATA_DIR = f"{DATA_DIR}/processed"
OUTPUT_DIR = "output"

# Historical bubble periods from BofA Research
BUBBLE_PERIODS = {
    'Dow_1929': {
        'start': '1926-10-01',
        'end': '1929-09-30',
        'peak': '1929-09-03'
    },
    'Gold_1980': {
        'start': '1979-07-01',
        'end': '1980-01-31',
        'peak': '1980-01-21'
    },
    'Nikkei_1987': {
        'start': '1986-01-01',
        'end': '1987-10-31',
        'peak': '1989-12-29'  # Actual peak
    },
    'Nasdaq_2000': {
        'start': '1995-01-01',
        'end': '2000-03-31',
        'peak': '2000-03-10'
    },
    'HSCEI_2007': {
        'start': '2006-06-01',
        'end': '2007-10-31',
        'peak': '2007-10-30'
    },
    'Oil_2008': {
        'start': '2007-01-01',
        'end': '2008-07-31',
        'peak': '2008-07-11'
    },
    'Bitcoin_2017': {
        'start': '2017-07-01',
        'end': '2017-12-31',
        'peak': '2017-12-17'
    },
    'Biotech_2021': {
        'start': '2020-05-01',
        'end': '2021-02-28',
        'peak': '2021-02-08'
    }
}

# BRI calculation parameters
BRI_PARAMS = {
    'lookback_days': 252,  # 1 year of trading days
    'momentum_ma_days': [20, 50, 200],  # Moving average windows
    'vol_window': 30,  # Realized volatility window
    'percentile_threshold': 90,  # Bubble threshold (90th percentile)
}

# Data quality thresholds
DATA_QUALITY = {
    'min_data_points': 252,  # Minimum required data points
    'max_missing_pct': 5,  # Maximum % of missing data allowed
    'outlier_threshold': 5,  # Standard deviations for outlier detection
}

# API keys (to be set via environment variables)
API_KEYS = {
    'alpha_vantage': None,  # Set via env: ALPHA_VANTAGE_API_KEY
    'quandl': None,  # Set via env: QUANDL_API_KEY
    'fred': None,  # Set via env: FRED_API_KEY
}

