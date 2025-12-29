"""
BRI (Bubble Risk Indicator) Data Fetcher
Fetches historical price and volume data for multiple asset classes
Used for Bank of America's BRI framework analysis

Assets covered:
- Equity Indices: Dow Jones, NASDAQ-100, Nikkei, Hang Seng (HSI), Hang Seng China Enterprises, 
                  Hang Seng Tech, DAX, CSI300, CSI500
- Sector Indices: Financials (XLF), Consumer Discretionary (XLY), Communication Services (XLC), 
                  Industrials (XLI), Technology (XLK), Healthcare (XLV), Energy (XLE, IXE), Biotech (IBB)
- Commodities: Gold, Silver, Crude Oil, Copper
- Currencies: US Dollar Index (DXY), Japanese Yen (JPY), Euro (EUR)
- Cryptocurrencies: Bitcoin
- Mega-cap Tech: Magnificent 7 (MAGS)
"""

import yfinance as yf
import pandas as pd
from datetime import datetime
import os
import warnings
import time
import random
warnings.filterwarnings('ignore')

# BRI Asset Mapping to Yahoo Finance Tickers
BRI_ASSETS = {
    # Equity Indices
    'DOW_JONES': {
        'yahoo_ticker': '^DJI',
        'description': 'Dow Jones Industrial Average',
        'asset_class': 'Equity Index',
        'original_ticker': 'INDU'
    },
    'NASDAQ_100': {
        'yahoo_ticker': '^NDX',
        'description': 'NASDAQ-100 Index',
        'asset_class': 'Equity Index',
        'original_ticker': 'NDX'
    },
    'NIKKEI_225': {
        'yahoo_ticker': '^N225',
        'description': 'Nikkei 225 Index',
        'asset_class': 'Equity Index',
        'original_ticker': 'NKY'
    },
    'HSI': {
        'yahoo_ticker': '^HSI',
        'description': 'Hang Seng Index',
        'asset_class': 'Equity Index',
        'original_ticker': 'HSI'
    },
    
    # Commodities
    'GOLD': {
        'yahoo_ticker': 'GC=F',
        'description': 'Gold Futures (Continuous Contract)',
        'asset_class': 'Commodity',
        'original_ticker': 'XAU',
        'alternative_ticker': 'GOLD'  # SPDR Gold Shares ETF as backup
    },
    'CRUDE_OIL': {
        'yahoo_ticker': 'CL=F',
        'description': 'Crude Oil Futures (Continuous Contract)',
        'asset_class': 'Commodity',
        'original_ticker': 'CO1',
        'alternative_ticker': 'USO'  # United States Oil Fund ETF as backup
    },
    'SILVER': {
        'yahoo_ticker': 'SI=F',
        'description': 'Silver Futures (Continuous Contract)',
        'asset_class': 'Commodity',
        'original_ticker': 'SI',
        'alternative_ticker': 'SLV'  # iShares Silver Trust ETF as backup
    },
    'COPPER': {
        'yahoo_ticker': 'HG=F',
        'description': 'Copper Futures (Continuous Contract)',
        'asset_class': 'Commodity',
        'original_ticker': 'HG',
        'alternative_ticker': 'CPER'  # United States Copper Index Fund as backup
    },
    
    # Cryptocurrency
    'BITCOIN': {
        'yahoo_ticker': 'BTC-USD',
        'description': 'Bitcoin USD',
        'asset_class': 'Cryptocurrency',
        'original_ticker': 'XBTUSD'
    },
    
    # Currencies & FX Indices
    'US_DOLLAR_INDEX': {
        'yahoo_ticker': 'DX-Y.NYB',
        'description': 'US Dollar Index (DXY)',
        'asset_class': 'Currency Index',
        'original_ticker': 'DXY',
        'alternative_ticker': 'UUP'  # Invesco DB USD Index Bullish Fund ETF as backup
    },
    'JPY': {
        'yahoo_ticker': 'JPY=X',
        'description': 'Japanese Yen / US Dollar',
        'asset_class': 'Currency',
        'original_ticker': 'USDJPY'
    },
    'EUR': {
        'yahoo_ticker': 'EUR=X',
        'description': 'Euro / US Dollar',
        'asset_class': 'Currency',
        'original_ticker': 'EURUSD'
    },
    
    # Sector Indices - U.S. SPDR Sector ETFs
    'XLF': {
        'yahoo_ticker': 'XLF',
        'description': 'Financial Select Sector SPDR Fund',
        'asset_class': 'Sector Index',
        'original_ticker': 'XLF'
    },
    'XLY': {
        'yahoo_ticker': 'XLY',
        'description': 'Consumer Discretionary Select Sector SPDR Fund',
        'asset_class': 'Sector Index',
        'original_ticker': 'XLY'
    },
    'XLC': {
        'yahoo_ticker': 'XLC',
        'description': 'Communication Services Select Sector SPDR Fund',
        'asset_class': 'Sector Index',
        'original_ticker': 'XLC'
    },
    'XLI': {
        'yahoo_ticker': 'XLI',
        'description': 'Industrial Select Sector SPDR Fund',
        'asset_class': 'Sector Index',
        'original_ticker': 'XLI'
    },
    'XLK': {
        'yahoo_ticker': 'XLK',
        'description': 'Technology Select Sector SPDR Fund',
        'asset_class': 'Sector Index',
        'original_ticker': 'XLK'
    },
    'XLV': {
        'yahoo_ticker': 'XLV',
        'description': 'Health Care Select Sector SPDR Fund',
        'asset_class': 'Sector Index',
        'original_ticker': 'XLV'
    },
    'XLE': {
        'yahoo_ticker': 'XLE',
        'description': 'Energy Select Sector SPDR Fund',
        'asset_class': 'Sector Index',
        'original_ticker': 'XLE'
    },
    'IXE': {
        'yahoo_ticker': '^IXE',
        'description': 'S&P Global Energy Index',
        'asset_class': 'Sector Index',
        'original_ticker': 'IXE',
        'alternative_ticker': 'XLE'  # Energy Select Sector SPDR as backup
    },
    'BIOTECH': {
        'yahoo_ticker': 'IBB',
        'description': 'iShares Biotechnology ETF',
        'asset_class': 'Sector Index',
        'original_ticker': 'IBB',
        'alternative_ticker': '^SPSIBI'  # S&P Biotech Select Industry Index as backup
    },
    
    # Global Equity Indices
    'DAX': {
        'yahoo_ticker': '^GDAXI',
        'description': 'DAX Performance Index (Germany)',
        'asset_class': 'Equity Index',
        'original_ticker': 'DAX'
    },
    'CSI300': {
        'yahoo_ticker': '000300.SS',
        'description': 'CSI 300 Index (China A-shares)',
        'asset_class': 'Equity Index',
        'original_ticker': 'CSI300'
    },
    'CSI500': {
        'yahoo_ticker': 'ASHS',
        'description': 'Xtrackers Harvest CSI 500 China A-Shares Small Cap ETF',
        'asset_class': 'Equity Index',
        'original_ticker': 'CSI500',
        'note': 'CSI 500 tracks small-cap China A-shares (CSI 1000 not available on Yahoo Finance)'
    },
    'HSTECH': {
        'yahoo_ticker': 'HSTECH.HK',
        'description': 'Hang Seng TECH Index',
        'asset_class': 'Equity Index',
        'original_ticker': 'HSTECH',
        'alternative_ticker': '3033.HK'  # Hang Seng TECH Index ETF as backup
    },
    
    # Mega-cap Technology
    'MAG7': {
        'yahoo_ticker': 'MAGS',
        'description': 'Roundhill Magnificent Seven ETF (Apple, Microsoft, Google, Amazon, Nvidia, Meta, Tesla)',
        'asset_class': 'Thematic Index',
        'original_ticker': 'MAG7',
        'alternative_ticker': 'XLK'  # Tech sector as backup
    },
    
    # Credit Spreads (from FRED API, not Yahoo Finance)
    'IG_SPREAD': {
        'yahoo_ticker': None,  # Not available on Yahoo Finance
        'fred_series_id': 'BAMLC0A0CM',
        'description': 'ICE BofA US Corporate Index Option-Adjusted Spread (Investment Grade)',
        'asset_class': 'Credit Spread',
        'original_ticker': 'IG_SPREAD',
        'data_source': 'FRED',
        'note': 'Data fetched from FRED API, measures spread between IG corporate bonds and Treasury curve'
    },
    'HY_SPREAD': {
        'yahoo_ticker': None,  # Not available on Yahoo Finance
        'fred_series_id': 'BAMLH0A0HYM2',
        'description': 'ICE BofA US High Yield Index Option-Adjusted Spread',
        'asset_class': 'Credit Spread',
        'original_ticker': 'HY_SPREAD',
        'data_source': 'FRED',
        'note': 'Data fetched from FRED API, measures spread between HY corporate bonds and Treasury curve'
    }
}


def fetch_asset_data(asset_name, ticker_symbol, period='max', interval='1d', max_retries=3, base_delay=5):
    """
    Fetch historical data for a specific asset from Yahoo Finance with retry logic
    
    Parameters:
    -----------
    asset_name : str
        Name of the asset for display purposes
    ticker_symbol : str
        Yahoo Finance ticker symbol
    period : str
        Data period (default: 'max' for all available history)
    interval : str
        Data interval (default: '1d' for daily data)
    max_retries : int
        Maximum number of retry attempts (default: 3)
    base_delay : int
        Base delay in seconds between retries (default: 5)
    
    Returns:
    --------
    tuple: (pandas.DataFrame, dict) - Data and metadata
    """
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                # Exponential backoff with jitter
                delay = base_delay * (2 ** attempt) + random.uniform(0, 2)
                print(f"  [RETRY {attempt}/{max_retries}] Waiting {delay:.1f} seconds before retry...")
                time.sleep(delay)
            
            print(f"Fetching data for {asset_name} ({ticker_symbol})...")
            
            # Create ticker object
            ticker = yf.Ticker(ticker_symbol)
            
            # Fetch historical data
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                print(f"  [WARNING] No data found for {ticker_symbol}")
                return None, None
            
            # Get metadata
            metadata = {
                'asset_name': asset_name,
                'ticker': ticker_symbol,
                'rows': len(data),
                'start_date': data.index[0],
                'end_date': data.index[-1],
                'date_range_years': (data.index[-1] - data.index[0]).days / 365.25
            }
            
            # Display info
            print(f"  [OK] Successfully fetched {metadata['rows']} rows")
            print(f"  [OK] Date range: {metadata['start_date'].strftime('%Y-%m-%d')} to {metadata['end_date'].strftime('%Y-%m-%d')}")
            print(f"  [OK] Coverage: {metadata['date_range_years']:.1f} years")
            
            return data, metadata
        
        except Exception as e:
            error_msg = str(e)
            if "Rate limited" in error_msg or "Too Many Requests" in error_msg:
                print(f"  [WARNING] Rate limited on attempt {attempt + 1}/{max_retries}")
                if attempt == max_retries - 1:
                    print(f"  [ERROR] Failed after {max_retries} attempts: {error_msg}")
                    return None, None
            else:
                print(f"  [ERROR] Error fetching data for {ticker_symbol}: {error_msg}")
                return None, None
    
    return None, None


def try_alternative_ticker(asset_name, asset_info):
    """
    Try to fetch data using alternative ticker if primary fails
    
    Parameters:
    -----------
    asset_name : str
        Name of the asset
    asset_info : dict
        Asset information dictionary
    
    Returns:
    --------
    tuple: (pandas.DataFrame, dict, str) - Data, metadata, and ticker used
    """
    data, metadata = fetch_asset_data(asset_name, asset_info['yahoo_ticker'])
    ticker_used = asset_info['yahoo_ticker']
    
    # If primary ticker fails and alternative exists, try alternative
    if data is None and 'alternative_ticker' in asset_info:
        print(f"  → Trying alternative ticker: {asset_info['alternative_ticker']}")
        data, metadata = fetch_asset_data(asset_name, asset_info['alternative_ticker'])
        if data is not None:
            ticker_used = asset_info['alternative_ticker']
    
    return data, metadata, ticker_used


def save_asset_data(data, asset_name, ticker, output_dir='raw_data'):
    """
    Save asset data to CSV file
    
    Parameters:
    -----------
    data : pandas.DataFrame
        The data to save
    asset_name : str
        Name of the asset
    ticker : str
        Ticker symbol used
    output_dir : str
        Directory to save files
    
    Returns:
    --------
    str: Path to saved file
    """
    try:
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{asset_name}_{timestamp}.csv"
        filepath = os.path.join(output_dir, filename)
        
        # Save to CSV
        data.to_csv(filepath)
        file_size = os.path.getsize(filepath)
        print(f"  [OK] Saved to: {filepath} ({file_size:,} bytes)")
        
        return filepath
    
    except Exception as e:
        print(f"  [ERROR] Error saving data: {str(e)}")
        return None


def generate_summary_report(results, output_dir='raw_data'):
    """
    Generate a summary report of all fetched data
    
    Parameters:
    -----------
    results : list
        List of dictionaries containing fetch results
    output_dir : str
        Directory to save the report
    """
    try:
        report_path = os.path.join(output_dir, f'fetch_summary_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt')
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("BRI DATA FETCH SUMMARY REPORT\n")
            f.write("="*80 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*80 + "\n\n")
            
            # Successful fetches
            successful = [r for r in results if r['success']]
            failed = [r for r in results if not r['success']]
            
            f.write(f"Total Assets Processed: {len(results)}\n")
            f.write(f"Successfully Fetched: {len(successful)}\n")
            f.write(f"Failed: {len(failed)}\n\n")
            
            # Detailed results for successful fetches
            if successful:
                f.write("-"*80 + "\n")
                f.write("SUCCESSFULLY FETCHED ASSETS\n")
                f.write("-"*80 + "\n\n")
                
                for result in successful:
                    meta = result['metadata']
                    f.write(f"Asset: {result['asset_name']}\n")
                    f.write(f"  Original Ticker: {result['original_ticker']}\n")
                    f.write(f"  Yahoo Ticker: {result['ticker_used']}\n")
                    f.write(f"  Asset Class: {result['asset_class']}\n")
                    f.write(f"  Description: {result['description']}\n")
                    f.write(f"  Data Points: {meta['rows']:,}\n")
                    f.write(f"  Start Date: {meta['start_date'].strftime('%Y-%m-%d')}\n")
                    f.write(f"  End Date: {meta['end_date'].strftime('%Y-%m-%d')}\n")
                    f.write(f"  Coverage: {meta['date_range_years']:.1f} years\n")
                    f.write(f"  File: {result['file_path']}\n")
                    f.write("\n")
            
            # Failed fetches
            if failed:
                f.write("-"*80 + "\n")
                f.write("FAILED FETCHES\n")
                f.write("-"*80 + "\n\n")
                
                for result in failed:
                    f.write(f"Asset: {result['asset_name']}\n")
                    f.write(f"  Original Ticker: {result['original_ticker']}\n")
                    f.write(f"  Attempted Yahoo Ticker: {result['ticker_attempted']}\n")
                    f.write(f"  Asset Class: {result['asset_class']}\n")
                    f.write("\n")
            
            f.write("="*80 + "\n")
            f.write("END OF REPORT\n")
            f.write("="*80 + "\n")
        
        print(f"\n[OK] Summary report saved to: {report_path}")
        return report_path
    
    except Exception as e:
        print(f"\n[ERROR] Error generating summary report: {str(e)}")
        return None


def main():
    """
    Main function to fetch all BRI assets
    """
    print("="*80)
    print("BRI (BUBBLE RISK INDICATOR) DATA FETCHER")
    print("="*80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total assets to fetch: {len(BRI_ASSETS)}")
    print("="*80)
    print()
    
    # Results tracking
    results = []
    output_dir = 'raw_data'
    
    # Fetch data for each asset
    for idx, (asset_name, asset_info) in enumerate(BRI_ASSETS.items(), 1):
        print(f"\n{'='*80}")
        print(f"Processing: {asset_name} ({idx}/{len(BRI_ASSETS)})")
        print(f"Description: {asset_info['description']}")
        print(f"Asset Class: {asset_info['asset_class']}")
        print(f"Original Ticker: {asset_info['original_ticker']}")
        print(f"{'='*80}\n")
        
        # Try to fetch data (with alternative ticker if needed)
        data, metadata, ticker_used = try_alternative_ticker(asset_name, asset_info)
        
        # Add delay between requests to avoid rate limiting
        if idx < len(BRI_ASSETS):  # Don't delay after the last one
            delay = random.uniform(3, 6)  # Random delay between 3-6 seconds
            print(f"  [INFO] Waiting {delay:.1f} seconds before next request...")
            time.sleep(delay)
        
        if data is not None:
            # Save data
            file_path = save_asset_data(data, asset_name, ticker_used, output_dir)
            
            # Record successful result
            results.append({
                'asset_name': asset_name,
                'original_ticker': asset_info['original_ticker'],
                'ticker_used': ticker_used,
                'asset_class': asset_info['asset_class'],
                'description': asset_info['description'],
                'success': True,
                'metadata': metadata,
                'file_path': file_path
            })
        else:
            # Record failed result
            results.append({
                'asset_name': asset_name,
                'original_ticker': asset_info['original_ticker'],
                'ticker_attempted': asset_info['yahoo_ticker'],
                'asset_class': asset_info['asset_class'],
                'description': asset_info['description'],
                'success': False
            })
    
    # Generate summary report
    print("\n" + "="*80)
    print("GENERATING SUMMARY REPORT")
    print("="*80)
    generate_summary_report(results, output_dir)
    
    # Final summary
    print("\n" + "="*80)
    print("DATA FETCH COMPLETE!")
    print("="*80)
    successful = sum(1 for r in results if r['success'])
    print(f"[OK] Successfully fetched: {successful}/{len(results)} assets")
    print(f"[OK] Data saved in: {output_dir}/")
    print("="*80)


if __name__ == "__main__":
    main()

