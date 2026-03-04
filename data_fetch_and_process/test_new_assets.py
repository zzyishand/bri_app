"""
Quick Test Script for New BRI Assets
Tests if all newly added assets can be fetched from Yahoo Finance
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# New assets to test
NEW_ASSETS = {
    # U.S. Sector Indices
    'XLF': 'XLF',
    'XLY': 'XLY',
    'XLC': 'XLC',
    'XLI': 'XLI',
    'XLK': 'XLK',
    'XLV': 'XLV',
    'XLE': 'XLE',
    
    # Global Indices
    'DAX': '^GDAXI',
    'CSI300': '000300.SS',
    'CSI1000': '000852.SS',
    'HSTECH': '^HSTECH',
    
    # Thematic
    'MAG7': 'MAGS',
    
    # Commodities
    'COPPER': 'HG=F'
}

def test_ticker(name, ticker):
    """Test if a ticker can be fetched"""
    try:
        print(f"\nTesting {name} ({ticker})...")
        
        # Try to fetch last 30 days of data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        data = yf.download(ticker, start=start_date, end=end_date, progress=False)
        
        if data.empty:
            print(f"  [FAIL] No data returned for {ticker}")
            return False
        else:
            print(f"  [OK] Fetched {len(data)} rows")
            print(f"      Latest date: {data.index[-1].strftime('%Y-%m-%d')}")
            print(f"      Latest close: {data['Close'].iloc[-1]:.2f}")
            return True
            
    except Exception as e:
        print(f"  [ERROR] {str(e)}")
        return False

def main():
    print("="*80)
    print("TESTING NEW BRI ASSETS")
    print("="*80)
    print(f"Testing {len(NEW_ASSETS)} new assets...")
    print("="*80)
    
    results = {}
    
    for name, ticker in NEW_ASSETS.items():
        success = test_ticker(name, ticker)
        results[name] = success
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    successful = [name for name, success in results.items() if success]
    failed = [name for name, success in results.items() if not success]
    
    print(f"\n[SUCCESS] {len(successful)}/{len(NEW_ASSETS)}")
    if successful:
        for name in successful:
            print(f"  - {name} ({NEW_ASSETS[name]})")
    
    if failed:
        print(f"\n[FAILED] {len(failed)}/{len(NEW_ASSETS)}")
        for name in failed:
            print(f"  - {name} ({NEW_ASSETS[name]})")
    
    print("\n" + "="*80)
    
    # Test with alternative tickers if any failed
    if failed:
        print("\nSuggested alternatives for failed tickers:")
        alternatives = {
            'MAGS': 'XLK or individual stocks',
            '000300.SS': 'Try ASHR (China A-shares ETF)',
            '000852.SS': 'Try FXI (China Large-Cap ETF)',
            '^HSTECH': 'Try KTEC (KraneShares Hang Seng Tech ETF)'
        }
        for name in failed:
            ticker = NEW_ASSETS[name]
            if ticker in alternatives:
                print(f"  {name}: {alternatives[ticker]}")

if __name__ == "__main__":
    main()

