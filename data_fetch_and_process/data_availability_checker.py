"""
Data Availability Checker for BRI (Bubble Risk Indicator) Project
Checks Yahoo Finance for historical data availability for bubble case studies
"""

import yfinance as yf
from datetime import datetime
import pandas as pd
import time
import warnings
warnings.filterwarnings('ignore')


# Historical bubble periods from BofA Research
BUBBLE_CASES = {
    'Dow_1929': {
        'ticker': '^DJI',  # Yahoo Finance ticker for Dow Jones
        'bloomberg': 'INDU',
        'period': 'Oct-1926 to Sep-1929',
        'description': '1929 Stock Market Crash'
    },
    'Gold_1980': {
        'ticker': 'GC=F',  # Gold Futures
        'bloomberg': 'XAU',
        'period': 'Jul-1979 to Jan-1980',
        'description': 'Gold Bubble'
    },
    'Nikkei_1987': {
        'ticker': '^N225',  # Nikkei 225
        'bloomberg': 'NKY',
        'period': 'Jan-1986 to Oct-1987',
        'description': 'Japanese Asset Bubble'
    },
    'Nasdaq_2000': {
        'ticker': '^IXIC',  # Nasdaq Composite
        'bloomberg': 'NDX',
        'period': 'Jan-1995 to Mar-2000',
        'description': 'Dot-com Bubble'
    },
    'HSCEI_2007': {
        'ticker': '^HSCE',  # Hang Seng China Enterprises Index
        'bloomberg': 'HSCEI',
        'period': 'Jun-2006 to Oct-2007',
        'description': 'China H-Share Bubble'
    },
    'Oil_2008': {
        'ticker': 'CL=F',  # Crude Oil Futures
        'bloomberg': 'CO1',
        'period': 'Jan-2007 to Jul-2008',
        'description': 'Oil Price Spike'
    },
    'Bitcoin_2017': {
        'ticker': 'BTC-USD',  # Bitcoin USD
        'bloomberg': 'XBTUSD',
        'period': 'Jul-2017 to Dec-2017',
        'description': 'Bitcoin 2017 Bubble'
    },
    'Biotech_2021': {
        'ticker': 'XBI',  # SPDR S&P Biotech ETF (proxy for SPSIBI)
        'bloomberg': 'SPSIBI',
        'period': 'May-2020 to Feb-2021',
        'description': 'Biotech Bubble during COVID'
    }
}


def check_ticker_availability(ticker, name):
    """
    Check data availability for a given ticker on Yahoo Finance
    
    Parameters:
    -----------
    ticker : str
        Yahoo Finance ticker symbol
    name : str
        Name/identifier for the asset
        
    Returns:
    --------
    dict : Information about data availability
    """
    try:
        print(f"\n{'='*60}")
        print(f"Checking: {name} ({ticker})")
        print(f"{'='*60}")
        
        # Add delay to avoid rate limiting
        time.sleep(2)
        
        # Fetch maximum available history
        asset = yf.Ticker(ticker)
        hist = asset.history(period="max")
        
        if hist.empty:
            return {
                'name': name,
                'ticker': ticker,
                'available': False,
                'error': 'No data available'
            }
        
        # Get info about available data
        start_date = hist.index.min()
        end_date = hist.index.max()
        total_days = len(hist)
        
        # Get available columns
        columns = list(hist.columns)
        
        print(f"✓ Data Available!")
        print(f"  Start Date: {start_date.strftime('%Y-%m-%d')}")
        print(f"  End Date: {end_date.strftime('%Y-%m-%d')}")
        print(f"  Total Trading Days: {total_days:,}")
        print(f"  Available Columns: {', '.join(columns)}")
        
        # Calculate basic statistics for the full period
        if 'Close' in columns:
            returns = hist['Close'].pct_change()
            volatility = returns.std() * (252 ** 0.5)  # Annualized
            
            print(f"\n  Summary Statistics (Full Period):")
            print(f"    Start Price: ${hist['Close'].iloc[0]:.2f}")
            print(f"    End Price: ${hist['Close'].iloc[-1]:.2f}")
            print(f"    Total Return: {((hist['Close'].iloc[-1] / hist['Close'].iloc[0]) - 1) * 100:.2f}%")
            print(f"    Annualized Volatility: {volatility * 100:.2f}%")
        
        return {
            'name': name,
            'ticker': ticker,
            'available': True,
            'start_date': start_date,
            'end_date': end_date,
            'total_days': total_days,
            'columns': columns,
            'sample_data': hist.head(3)
        }
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return {
            'name': name,
            'ticker': ticker,
            'available': False,
            'error': str(e)
        }


def generate_summary_report(results):
    """Generate a summary report of data availability"""
    
    print("\n" + "="*80)
    print("SUMMARY REPORT: Yahoo Finance Data Availability for BRI Project")
    print("="*80)
    
    summary_data = []
    
    for case_name, case_info in BUBBLE_CASES.items():
        result = results.get(case_name, {})
        
        if result.get('available'):
            summary_data.append({
                'Case': case_name,
                'Yahoo Ticker': case_info['ticker'],
                'Bloomberg': case_info['bloomberg'],
                'Target Period': case_info['period'],
                'Available From': result['start_date'].strftime('%Y-%m-%d'),
                'Available To': result['end_date'].strftime('%Y-%m-%d'),
                'Days': result['total_days'],
                'Status': '✓ Available'
            })
        else:
            summary_data.append({
                'Case': case_name,
                'Yahoo Ticker': case_info['ticker'],
                'Bloomberg': case_info['bloomberg'],
                'Target Period': case_info['period'],
                'Available From': 'N/A',
                'Available To': 'N/A',
                'Days': 0,
                'Status': f"✗ {result.get('error', 'Unknown error')}"
            })
    
    df_summary = pd.DataFrame(summary_data)
    print("\n")
    print(df_summary.to_string(index=False))
    
    # Additional insights
    available_count = sum(1 for r in results.values() if r.get('available'))
    print(f"\n{'='*80}")
    print(f"Available: {available_count}/{len(BUBBLE_CASES)} cases")
    print(f"{'='*80}")
    
    # Save to CSV
    df_summary.to_csv('yahoo_finance_availability_summary.csv', index=False)
    print("\n✓ Summary saved to: yahoo_finance_availability_summary.csv")
    
    return df_summary


def main():
    """Main function to check all bubble cases"""
    
    print("="*80)
    print("BRI PROJECT - Yahoo Finance Data Availability Check")
    print("="*80)
    print(f"Checking {len(BUBBLE_CASES)} historical bubble cases...")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # Check each bubble case
    for case_name, case_info in BUBBLE_CASES.items():
        result = check_ticker_availability(case_info['ticker'], case_name)
        results[case_name] = result
    
    # Generate summary report
    summary_df = generate_summary_report(results)
    
    print("\n" + "="*80)
    print("NEXT STEPS:")
    print("="*80)
    print("1. Review the availability summary above")
    print("2. For cases with missing data, consider alternative sources:")
    print("   - FRED (Federal Reserve Economic Data)")
    print("   - Quandl/Nasdaq Data Link")
    print("   - Alpha Vantage")
    print("   - Historical data providers (e.g., Norgate, CSI)")
    print("3. Decide whether to proceed with available data or fetch additional sources")
    print("="*80)
    
    return results


if __name__ == "__main__":
    main()

