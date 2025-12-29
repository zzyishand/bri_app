"""
Example: Calculate BRI for All Assets

This script demonstrates how to use the BRI calculator to analyze
all assets from the data_fetch_and_process folder.

It calculates BRI indicators for short/mid/long term horizons and
saves results to CSV files for further analysis.
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

from indicator.bri_calculator import BRICalculator
from indicator.bri_config import BRIConfig, get_config


def find_latest_data_file(data_dir: str, asset_pattern: str) -> str:
    """
    Find the latest data file for an asset
    
    Parameters:
    -----------
    data_dir : str
        Directory containing data files
    asset_pattern : str
        Pattern to match asset files (e.g., 'NASDAQ_100')
    
    Returns:
    --------
    str: Path to latest file
    """
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
    """
    Calculate BRI for a single asset
    
    Parameters:
    -----------
    data_path : str
        Path to asset data CSV file
    asset_name : str
        Name of the asset
    output_dir : str
        Directory to save results
    config : BRIConfig, optional
        Configuration to use
    
    Returns:
    --------
    dict: Summary of calculation
    """
    print(f"\n{'='*80}")
    print(f"Calculating BRI for: {asset_name}")
    print(f"{'='*80}")
    
    try:
        # Load data
        print(f"[1/4] Loading data from: {data_path}")
        data = pd.read_csv(data_path, index_col=0, parse_dates=True)
        print(f"      Loaded {len(data)} rows, date range: {data.index[0]} to {data.index[-1]}")
        
        # Create calculator
        print(f"[2/4] Initializing BRI calculator...")
        calculator = BRICalculator(config)
        
        # Calculate BRI
        print(f"[3/4] Calculating BRI indicators...")
        results = calculator.calculate_full_bri(
            data,
            price_column='Close',
            asset_name=asset_name
        )
        
        # Get current status
        status = calculator.get_current_status(results)
        print(f"\n      Current Status:")
        print(f"      - Date: {status['date']}")
        print(f"      - Price: {status['price']:.2f}")
        print(f"      - Composite BRI: {status['composite_bri']:.3f}")
        print(f"      - Risk Level: {status['composite_risk']}")
        print(f"      - Short-term BRI: {status['short_term']['bri']:.3f} ({status['short_term']['risk']})")
        print(f"      - Mid-term BRI: {status['mid_term']['bri']:.3f} ({status['mid_term']['risk']})")
        print(f"      - Long-term BRI: {status['long_term']['bri']:.3f} ({status['long_term']['risk']})")
        
        # Save results
        print(f"[4/4] Saving results...")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = os.path.join(output_dir, f"{asset_name}_BRI_{timestamp}.csv")
        calculator.save_results(results, output_path, include_raw_moments=True)
        
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
        return {
            'asset_name': asset_name,
            'success': False,
            'error': str(e)
        }


def main():
    """
    Main function to calculate BRI for all assets
    """
    print("="*80)
    print("BRI CALCULATOR - BATCH PROCESSING")
    print("="*80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Configuration
    data_dir = '../data_fetch_and_process/raw_data'
    output_dir = 'bri_results'
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    print(f"\nOutput directory: {output_dir}/")
    
    # Define assets to process
    assets = {
        'DOW_JONES': 'DOW_JONES',
        'NASDAQ_100': 'NASDAQ_100',
        'NIKKEI_225': 'NIKKEI_225',
        'HSCEI': 'HSCEI',
        'GOLD': 'GOLD',
        'CRUDE_OIL': 'CRUDE_OIL',
        'BITCOIN': 'BITCOIN',
        'BIOTECH': 'BIOTECH'
    }
    
    # Get configuration
    config_choice = 'default'  # Options: 'default', 'conservative', 'momentum', 'short_term', 'long_term'
    config = get_config(config_choice)
    
    print(f"\nUsing configuration: {config_choice}")
    print(f"  Windows: Short={config.windows.short_term}, Mid={config.windows.mid_term}, Long={config.windows.long_term}")
    print(f"  Weights: Mean={config.weights.mean}, Var={config.weights.variance}, Skew={config.weights.skewness}, Kurt={config.weights.kurtosis}")
    print(f"  Thresholds: Warning={config.thresholds.warning}, Bubble={config.thresholds.bubble}, Extreme={config.thresholds.extreme}")
    
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
            print(f"  Current BRI: {status['composite_bri']:.3f} ({status['composite_risk']})")
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
    summary_path = os.path.join(output_dir, f"calculation_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    with open(summary_path, 'w') as f:
        f.write("BRI CALCULATION SUMMARY\n")
        f.write("="*80 + "\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Configuration: {config_choice}\n")
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
                f.write(f"  Composite BRI: {status['composite_bri']:.3f}\n")
                f.write(f"  Risk Level: {status['composite_risk']}\n")
                f.write(f"  Short-term: {status['short_term']['bri']:.3f} ({status['short_term']['risk']})\n")
                f.write(f"  Mid-term: {status['mid_term']['bri']:.3f} ({status['mid_term']['risk']})\n")
                f.write(f"  Long-term: {status['long_term']['bri']:.3f} ({status['long_term']['risk']})\n")
                f.write(f"  Output: {result['output_path']}\n")
    
    print(f"\n[OK] Summary saved to: {summary_path}")


if __name__ == "__main__":
    main()

