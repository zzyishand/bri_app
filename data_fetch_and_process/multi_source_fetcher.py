"""
Multi-Source Data Fetcher for BRI Project
Fetches historical data from multiple sources with robust error handling and rate limiting
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import warnings
import os
from pathlib import Path

warnings.filterwarnings('ignore')

# Try to import optional data sources
try:
    from fredapi import Fred
    FRED_AVAILABLE = True
except ImportError:
    FRED_AVAILABLE = False
    print("⚠️ fredapi not installed. Install with: pip install fredapi")

try:
    import pandas_datareader as pdr
    DATAREADER_AVAILABLE = True
except ImportError:
    DATAREADER_AVAILABLE = False
    print("⚠️ pandas_datareader not installed. Install with: pip install pandas-datareader")


class MultiSourceDataFetcher:
    """
    Fetches historical financial data from multiple sources
    """
    
    def __init__(self, fred_api_key=None, cache_dir='data/raw'):
        """
        Initialize the fetcher
        
        Parameters:
        -----------
        fred_api_key : str, optional
            FRED API key (get free key from https://fred.stlouisfed.org/docs/api/api_key.html)
        cache_dir : str
            Directory to cache downloaded data
        """
        self.fred_api_key = fred_api_key
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize FRED client if available
        if FRED_AVAILABLE and fred_api_key:
            self.fred = Fred(api_key=fred_api_key)
        else:
            self.fred = None
            
    def fetch_yahoo(self, ticker, start_date=None, end_date=None, max_retries=3):
        """
        Fetch data from Yahoo Finance with retry logic
        
        Parameters:
        -----------
        ticker : str
            Yahoo Finance ticker symbol
        start_date : str or datetime
            Start date for data
        end_date : str or datetime
            End date for data
        max_retries : int
            Maximum number of retry attempts
            
        Returns:
        --------
        pd.DataFrame or None
        """
        print(f"\n  Attempting Yahoo Finance: {ticker}")
        
        for attempt in range(max_retries):
            try:
                # Add delay to avoid rate limiting
                time.sleep(5 + attempt * 5)  # Increasing delay with each retry
                
                asset = yf.Ticker(ticker)
                
                if start_date or end_date:
                    hist = asset.history(start=start_date, end=end_date)
                else:
                    hist = asset.history(period="max")
                
                if not hist.empty:
                    print(f"    ✓ Success! Got {len(hist)} days of data")
                    return hist
                else:
                    print(f"    ✗ No data returned (attempt {attempt + 1}/{max_retries})")
                    
            except Exception as e:
                print(f"    ✗ Error (attempt {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    wait_time = 10 * (attempt + 1)
                    print(f"    Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
        
        return None
    
    def fetch_fred(self, series_id, start_date=None, end_date=None):
        """
        Fetch data from FRED
        
        Parameters:
        -----------
        series_id : str
            FRED series ID
        start_date : str or datetime
            Start date for data
        end_date : str or datetime
            End date for data
            
        Returns:
        --------
        pd.DataFrame or None
        """
        if not self.fred:
            print("    ✗ FRED not available (no API key or library not installed)")
            return None
            
        print(f"\n  Attempting FRED: {series_id}")
        
        try:
            time.sleep(1)  # FRED is more lenient but still be polite
            
            data = self.fred.get_series(
                series_id, 
                observation_start=start_date, 
                observation_end=end_date
            )
            
            if data is not None and not data.empty:
                # Convert to DataFrame with standard columns
                df = pd.DataFrame({
                    'Close': data.values
                }, index=data.index)
                df.index.name = 'Date'
                
                print(f"    ✓ Success! Got {len(df)} days of data")
                return df
            else:
                print(f"    ✗ No data returned")
                
        except Exception as e:
            print(f"    ✗ Error: {str(e)}")
            
        return None
    
    def fetch_with_fallback(self, sources_config):
        """
        Try multiple sources in order until one succeeds
        
        Parameters:
        -----------
        sources_config : list of dict
            List of source configurations, each with:
            - 'source': 'yahoo', 'fred', etc.
            - 'params': dict of parameters for that source
            
        Returns:
        --------
        tuple: (pd.DataFrame or None, str source_used)
        """
        for config in sources_config:
            source_type = config['source']
            params = config['params']
            
            if source_type == 'yahoo':
                data = self.fetch_yahoo(**params)
                if data is not None:
                    return data, 'yahoo'
                    
            elif source_type == 'fred':
                data = self.fetch_fred(**params)
                if data is not None:
                    return data, 'fred'
        
        return None, 'none'
    
    def save_to_cache(self, data, filename):
        """Save data to cache directory"""
        if data is not None:
            filepath = self.cache_dir / filename
            data.to_csv(filepath)
            print(f"  💾 Saved to: {filepath}")
            return filepath
        return None
    
    def load_from_cache(self, filename):
        """Load data from cache if it exists"""
        filepath = self.cache_dir / filename
        if filepath.exists():
            print(f"  📂 Loading from cache: {filepath}")
            return pd.read_csv(filepath, index_col=0, parse_dates=True)
        return None


# Bubble case configurations with multiple source options
BUBBLE_CASES_CONFIG = {
    'Dow_1929': {
        'name': '1929 Stock Market Crash',
        'period': 'Oct-1926 to Sep-1929',
        'start': '1926-10-01',
        'end': '1929-09-30',
        'sources': [
            {
                'source': 'fred',
                'params': {
                    'series_id': 'DJIA',  # FRED has historical Dow data
                    'start_date': '1926-10-01',
                    'end_date': '1929-09-30'
                }
            },
            {
                'source': 'yahoo',
                'params': {
                    'ticker': '^DJI',
                    'start_date': '1926-10-01',
                    'end_date': '1929-09-30'
                }
            }
        ]
    },
    'Gold_1980': {
        'name': 'Gold Bubble',
        'period': 'Jul-1979 to Jan-1980',
        'start': '1979-07-01',
        'end': '1980-01-31',
        'sources': [
            {
                'source': 'fred',
                'params': {
                    'series_id': 'GOLDAMGBD228NLBM',  # London Gold Fixing
                    'start_date': '1979-07-01',
                    'end_date': '1980-01-31'
                }
            },
            {
                'source': 'yahoo',
                'params': {
                    'ticker': 'GC=F',
                    'start_date': '1979-07-01',
                    'end_date': '1980-01-31'
                }
            }
        ]
    },
    'Nikkei_1987': {
        'name': 'Japanese Asset Bubble',
        'period': 'Jan-1986 to Oct-1987',
        'start': '1986-01-01',
        'end': '1987-10-31',
        'sources': [
            {
                'source': 'yahoo',
                'params': {
                    'ticker': '^N225',
                    'start_date': '1986-01-01',
                    'end_date': '1987-10-31'
                }
            }
        ]
    },
    'Nasdaq_2000': {
        'name': 'Dot-com Bubble',
        'period': 'Jan-1995 to Mar-2000',
        'start': '1995-01-01',
        'end': '2000-03-31',
        'sources': [
            {
                'source': 'fred',
                'params': {
                    'series_id': 'NASDAQCOM',  # FRED Nasdaq Composite
                    'start_date': '1995-01-01',
                    'end_date': '2000-03-31'
                }
            },
            {
                'source': 'yahoo',
                'params': {
                    'ticker': '^IXIC',
                    'start_date': '1995-01-01',
                    'end_date': '2000-03-31'
                }
            }
        ]
    },
    'HSCEI_2007': {
        'name': 'China H-Share Bubble',
        'period': 'Jun-2006 to Oct-2007',
        'start': '2006-06-01',
        'end': '2007-10-31',
        'sources': [
            {
                'source': 'yahoo',
                'params': {
                    'ticker': '^HSCE',
                    'start_date': '2006-06-01',
                    'end_date': '2007-10-31'
                }
            }
        ]
    },
    'Oil_2008': {
        'name': 'Oil Price Spike',
        'period': 'Jan-2007 to Jul-2008',
        'start': '2007-01-01',
        'end': '2008-07-31',
        'sources': [
            {
                'source': 'fred',
                'params': {
                    'series_id': 'DCOILWTICO',  # WTI Crude Oil
                    'start_date': '2007-01-01',
                    'end_date': '2008-07-31'
                }
            },
            {
                'source': 'yahoo',
                'params': {
                    'ticker': 'CL=F',
                    'start_date': '2007-01-01',
                    'end_date': '2008-07-31'
                }
            }
        ]
    },
    'Bitcoin_2017': {
        'name': 'Bitcoin 2017 Bubble',
        'period': 'Jul-2017 to Dec-2017',
        'start': '2017-07-01',
        'end': '2017-12-31',
        'sources': [
            {
                'source': 'yahoo',
                'params': {
                    'ticker': 'BTC-USD',
                    'start_date': '2017-07-01',
                    'end_date': '2017-12-31'
                }
            }
        ]
    },
    'Biotech_2021': {
        'name': 'Biotech Bubble during COVID',
        'period': 'May-2020 to Feb-2021',
        'start': '2020-05-01',
        'end': '2021-02-28',
        'sources': [
            {
                'source': 'yahoo',
                'params': {
                    'ticker': 'XBI',
                    'start_date': '2020-05-01',
                    'end_date': '2021-02-28'
                }
            }
        ]
    }
}


def fetch_all_bubble_data(fred_api_key=None, use_cache=True):
    """
    Fetch all bubble case data
    
    Parameters:
    -----------
    fred_api_key : str, optional
        FRED API key (highly recommended)
    use_cache : bool
        Whether to use cached data if available
        
    Returns:
    --------
    dict : Dictionary of case_name -> (DataFrame, metadata)
    """
    print("="*80)
    print("MULTI-SOURCE DATA FETCHER - BRI Project")
    print("="*80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"FRED Available: {FRED_AVAILABLE}")
    print(f"FRED API Key Provided: {fred_api_key is not None}")
    print("="*80)
    
    fetcher = MultiSourceDataFetcher(fred_api_key=fred_api_key)
    results = {}
    
    for case_name, config in BUBBLE_CASES_CONFIG.items():
        print(f"\n{'='*60}")
        print(f"Fetching: {case_name} - {config['name']}")
        print(f"Period: {config['period']}")
        print(f"{'='*60}")
        
        cache_filename = f"{case_name.lower()}_raw.csv"
        
        # Try to load from cache first
        if use_cache:
            cached_data = fetcher.load_from_cache(cache_filename)
            if cached_data is not None:
                results[case_name] = {
                    'data': cached_data,
                    'source': 'cache',
                    'success': True,
                    'metadata': config
                }
                print(f"  ✓ Loaded from cache ({len(cached_data)} days)")
                continue
        
        # Fetch from sources
        data, source = fetcher.fetch_with_fallback(config['sources'])
        
        if data is not None:
            # Save to cache
            fetcher.save_to_cache(data, cache_filename)
            
            results[case_name] = {
                'data': data,
                'source': source,
                'success': True,
                'metadata': config
            }
            print(f"  ✓ Successfully fetched from {source.upper()}")
        else:
            results[case_name] = {
                'data': None,
                'source': 'none',
                'success': False,
                'metadata': config
            }
            print(f"  ✗ Failed to fetch from any source")
        
        # Polite delay between assets
        time.sleep(3)
    
    return results


def generate_summary(results):
    """Generate summary report of fetched data"""
    print("\n" + "="*80)
    print("FETCH SUMMARY REPORT")
    print("="*80)
    
    summary_rows = []
    
    for case_name, result in results.items():
        metadata = result['metadata']
        
        if result['success']:
            data = result['data']
            summary_rows.append({
                'Case': case_name,
                'Period': metadata['period'],
                'Source': result['source'].upper(),
                'Start Date': data.index.min().strftime('%Y-%m-%d'),
                'End Date': data.index.max().strftime('%Y-%m-%d'),
                'Days': len(data),
                'Status': '✓ Success'
            })
        else:
            summary_rows.append({
                'Case': case_name,
                'Period': metadata['period'],
                'Source': 'N/A',
                'Start Date': 'N/A',
                'End Date': 'N/A',
                'Days': 0,
                'Status': '✗ Failed'
            })
    
    df_summary = pd.DataFrame(summary_rows)
    print("\n")
    print(df_summary.to_string(index=False))
    
    success_count = sum(1 for r in results.values() if r['success'])
    print(f"\n{'='*80}")
    print(f"Successfully Fetched: {success_count}/{len(results)} cases")
    print(f"{'='*80}")
    
    # Save summary
    df_summary.to_csv('data_fetch_summary.csv', index=False)
    print("\n✓ Summary saved to: data_fetch_summary.csv")
    
    return df_summary


def main():
    """Main function"""
    print("\n" + "="*80)
    print("INSTRUCTIONS:")
    print("="*80)
    print("For best results, get a FREE FRED API key:")
    print("1. Go to: https://fred.stlouisfed.org/")
    print("2. Create a free account")
    print("3. Get your API key from: https://fredaccount.stlouisfed.org/apikeys")
    print("4. Set environment variable: export FRED_API_KEY='your_key_here'")
    print("="*80)
    
    # Check for FRED API key
    fred_api_key = os.getenv('FRED_API_KEY')
    if fred_api_key:
        print(f"\n✓ FRED API Key found!")
    else:
        print(f"\n⚠️ FRED API Key not found. Will try Yahoo Finance only.")
        print("   Some historical data (especially Dow 1929) may not be available.")
    
    # Fetch all data
    results = fetch_all_bubble_data(fred_api_key=fred_api_key, use_cache=True)
    
    # Generate summary
    summary = generate_summary(results)
    
    print("\n" + "="*80)
    print("NEXT STEPS:")
    print("="*80)
    print("1. Review the data fetch summary above")
    print("2. If some cases failed, consider:")
    print("   - Getting a FRED API key (free)")
    print("   - Trying again later (rate limits may reset)")
    print("   - Using alternative data sources")
    print("3. Process the successfully fetched data")
    print("4. Calculate BRI indicators")
    print("="*80)
    
    return results


if __name__ == "__main__":
    main()

