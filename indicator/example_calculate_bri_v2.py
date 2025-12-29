"""
Example: Calculate BRI for All Assets (Corrected Percentile Rank Method)

This script uses the corrected BRI calculator (V2) that implements:
1. Moment value calculation over specific windows
2. Percentile ranking against historical lookback
3. Weighted average of percentile ranks for sub-indicators
4. Scaling factor application

Based on BofA methodology:
- ST: 3m moments vs 1y percentile lookback
- MT: 6m moments vs 3y percentile lookback
- LT: 1y moments vs 5y percentile lookback

Four moments with intermediate variables:
1. Returns: Cumulative return
2. Volatility: Realized volatility (std dev)
3. Momentum: % distance from moving average price
   - Intermediate: moving_avg_price
4. Fragility: Realized vol - Realized MAD
   - Intermediate: realized_vol, realized_mad

Output includes 42 columns with all intermediate variables.
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime
from pathlib import Path

# Import BRI modules
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from indicator.bri_calculator_v2 import BRICalculatorV2
from indicator.bri_config import BRIConfig, get_config


def find_latest_data_file(data_dir, asset_pattern: str) -> str:
    """Find the latest data file for an asset"""
    data_dir = Path(data_dir)  # Ensure it's a Path object
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory does not exist: {data_dir}")
    
    files = [f for f in os.listdir(data_dir) if f.startswith(asset_pattern) and f.endswith('.csv')]
    
    if not files:
        raise FileNotFoundError(f"No files found for pattern: {asset_pattern}")
    
    # Sort by modification time and get latest
    files_with_time = [(f, os.path.getmtime(os.path.join(data_dir, f))) for f in files]
    latest_file = sorted(files_with_time, key=lambda x: x[1], reverse=True)[0][0]
    
    return os.path.join(data_dir, latest_file)


def calculate_bri_for_asset(data_path: str,
                           asset_name: str,
                           output_dir: str,
                           config: BRIConfig = None) -> dict:
    """Calculate BRI for a single asset using V2 calculator"""
    print(f"\n{'='*80}")
    print(f"Processing: {asset_name}")
    print(f"{'='*80}")
    
    try:
        # Load data
        print(f"[1/4] Loading data from: {data_path}")
        data = pd.read_csv(data_path, index_col=0, parse_dates=True)
        print(f"      Loaded {len(data)} rows, date range: {data.index[0]} to {data.index[-1]}")
        
        # Create calculator
        print(f"[2/4] Initializing BRI Calculator V2 (Percentile Rank Method)...")
        calculator = BRICalculatorV2(config)
        
        # Calculate BRI
        print(f"[3/4] Calculating BRI indicators...")
        results = calculator.calculate_full_bri(
            data,
            price_column='Close',
            asset_name=asset_name
        )
        
        # Get current status
        status = calculator.get_current_status(results)
        latest = results.iloc[-1]
        
        print(f"\n      Current Status:")
        print(f"      - Date: {status['date']}")
        print(f"      - Price: {status['price']:.2f}")
        print(f"      - Composite BRI: {status['composite_bri']:.4f}")
        print(f"      - Short-term: indicator={status['short_term']['indicator']:.4f}, avg_pctile={status['short_term']['avg_percentile']:.1f}")
        print(f"          (MA price: {latest['short_moving_avg_price']:.2f}, Momentum: {latest['short_momentum_value']:.2f}%)")
        print(f"      - Mid-term: indicator={status['mid_term']['indicator']:.4f}, avg_pctile={status['mid_term']['avg_percentile']:.1f}")
        print(f"      - Long-term: indicator={status['long_term']['indicator']:.4f}, avg_pctile={status['long_term']['avg_percentile']:.1f}")
        
        # Save results
        print(f"[4/4] Saving results...")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = os.path.join(output_dir, f"{asset_name}_BRI_v2_{timestamp}.csv")
        calculator.save_results(results, output_path, include_moment_values=True)
        
        print(f"\n[OK] Successfully calculated BRI for {asset_name}")
        
        return {
            'asset_name': asset_name,
            'success': True,
            'output_path': output_path,
            'status': status,
            'data_points': len(results),
            'valid_bri_points': results['composite_bri'].notna().sum()
        }
    
    except Exception as e:
        print(f"\n[ERROR] Failed to calculate BRI for {asset_name}: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'asset_name': asset_name,
            'success': False,
            'error': str(e)
        }


def main():
    """Main function to calculate BRI for all assets"""
    print("="*80)
    print("BRI CALCULATOR V2 - PERCENTILE RANK METHOD")
    print("="*80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Configuration
    # Get script directory and construct paths relative to project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    data_dir = project_root / 'data_fetch_and_process' / 'raw_data'
    output_dir = script_dir / 'bri_results_v2_with_intermediates'
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    print(f"\nOutput directory: {output_dir}/")
    
    # Define assets to process
    assets = {
        # Equity Indices
        'DOW_JONES': 'DOW_JONES',
        'NASDAQ_100': 'NASDAQ_100',
        'NIKKEI_225': 'NIKKEI_225',
        'HSI': 'HSI',
        'HSCEI': 'HSCEI',
        'DAX': 'DAX',
        'CSI300': 'CSI300',
        'CSI500': 'CSI500',
        'HSTECH': 'HSTECH',
        
        # Commodities
        'GOLD': 'GOLD',
        'SILVER': 'SILVER',
        'CRUDE_OIL': 'CRUDE_OIL',
        'COPPER': 'COPPER',
        
        # Currencies
        'US_DOLLAR_INDEX': 'US_DOLLAR_INDEX',
        'JPY': 'JPY',
        'EUR': 'EUR',
        
        # Cryptocurrency
        'BITCOIN': 'BITCOIN',
        
        # Sectors
        'XLF': 'XLF',
        'XLY': 'XLY',
        'XLC': 'XLC',
        'XLI': 'XLI',
        'XLK': 'XLK',
        'XLV': 'XLV',
        'XLE': 'XLE',
        'IXE': 'IXE',
        'BIOTECH': 'BIOTECH',
        
        # Tech Giants
        'MAG7': 'MAG7'
    }
    
    # Get configuration
    config_choice = 'default'
    config = get_config(config_choice)
    
    print(f"\nUsing configuration: {config_choice}")
    print(f"\nWindow Configuration:")
    print(f"  Short-term: moment_window={config.windows.short_term.moment_window} (~3m), percentile_lookback={config.windows.short_term.percentile_lookback} (~1y)")
    print(f"  Mid-term: moment_window={config.windows.mid_term.moment_window} (~6m), percentile_lookback={config.windows.mid_term.percentile_lookback} (~3y)")
    print(f"  Long-term: moment_window={config.windows.long_term.moment_window} (~1y), percentile_lookback={config.windows.long_term.percentile_lookback} (~5y)")
    print(f"\nMoment Weights:")
    print(f"  Returns={config.weights.returns}, Volatility={config.weights.volatility}, Momentum={config.weights.momentum}, Fragility={config.weights.fragility}")
    print(f"\nScaling Configuration:")
    print(f"  Dynamic Scaling: {config.use_dynamic_scaling}")
    print(f"  Steepness (k): {config.scaling_steepness}")
    
    # Process each asset
    results = []
    
    for asset_key, asset_name in assets.items():
        try:
            # Find latest data file
            data_path = find_latest_data_file(data_dir, asset_key)
            
            # Calculate BRI
            result = calculate_bri_for_asset(
                data_path,
                asset_name,
                output_dir,
                config
            )
            results.append(result)
            
        except FileNotFoundError as e:
            print(f"\n[WARNING] Skipping {asset_name}: {str(e)}")
            results.append({
                'asset_name': asset_name,
                'success': False,
                'error': str(e)
            })
    
    # Summary report
    print("\n" + "="*80)
    print("BATCH PROCESSING SUMMARY")
    print("="*80)
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"\nTotal assets processed: {len(results)}")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")
    
    if successful:
        print("\n" + "-"*80)
        print("SUCCESSFUL CALCULATIONS")
        print("-"*80)
        
        for result in successful:
            status = result['status']
            print(f"\n{result['asset_name']}:")
            print(f"  Current BRI: {status['composite_bri']:.4f}")
            print(f"  ST: {status['short_term']['indicator']:.4f} (pctile: {status['short_term']['avg_percentile']:.1f})")
            print(f"  MT: {status['mid_term']['indicator']:.4f} (pctile: {status['mid_term']['avg_percentile']:.1f})")
            print(f"  LT: {status['long_term']['indicator']:.4f} (pctile: {status['long_term']['avg_percentile']:.1f})")
            print(f"  Valid data points: {result['valid_bri_points']}/{result['data_points']}")
            print(f"  Output: {result['output_path']}")
    
    if failed:
        print("\n" + "-"*80)
        print("FAILED CALCULATIONS")
        print("-"*80)
        
        for result in failed:
            print(f"\n{result['asset_name']}: {result.get('error', 'Unknown error')}")
    
    print("\n" + "="*80)
    print("BATCH PROCESSING COMPLETE")
    print("="*80)
    
    # Save summary
    summary_path = os.path.join(output_dir, f"calculation_summary_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    with open(summary_path, 'w') as f:
        f.write("BRI CALCULATION SUMMARY (V2 - Percentile Rank Method)\n")
        f.write("="*80 + "\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Configuration: {config_choice}\n")
        f.write(f"Methodology: Percentile Rank with Historical Lookback\n")
        f.write(f"Total assets: {len(results)}\n")
        f.write(f"Successful: {len(successful)}\n")
        f.write(f"Failed: {len(failed)}\n")
        f.write("="*80 + "\n\n")
        
        if successful:
            f.write("SUCCESSFUL CALCULATIONS:\n")
            f.write("-"*80 + "\n")
            for result in successful:
                status = result['status']
                f.write(f"\n{result['asset_name']}:\n")
                f.write(f"  Date: {status['date']}\n")
                f.write(f"  Price: {status['price']:.2f}\n")
                f.write(f"  Composite BRI: {status['composite_bri']:.4f}\n")
                f.write(f"  Short-term: {status['short_term']['indicator']:.4f} (percentile: {status['short_term']['avg_percentile']:.1f})\n")
                f.write(f"  Mid-term: {status['mid_term']['indicator']:.4f} (percentile: {status['mid_term']['avg_percentile']:.1f})\n")
                f.write(f"  Long-term: {status['long_term']['indicator']:.4f} (percentile: {status['long_term']['avg_percentile']:.1f})\n")
                f.write(f"  Output: {result['output_path']}\n")
    
    print(f"\n[OK] Summary saved to: {summary_path}")


if __name__ == "__main__":
    main()

