"""
Test script for intermediate variables in BRI calculation
"""

import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from indicator.bri_calculator_v2 import BRICalculatorV2

# Load a small sample
print("Loading Bitcoin data...")
data = pd.read_csv('../data_fetch_and_process/raw_data/BITCOIN_20251211_105531.csv', 
                   index_col=0, parse_dates=True)

# Use only recent data for faster testing
data_sample = data.tail(1500)

print(f"Data sample: {len(data_sample)} rows")
print(f"Date range: {data_sample.index[0]} to {data_sample.index[-1]}")

# Create calculator
print("\nInitializing calculator...")
calculator = BRICalculatorV2()

# Calculate BRI
print("Calculating BRI with intermediate variables...\n")
results = calculator.calculate_full_bri(
    data_sample,
    price_column='Close',
    asset_name='BITCOIN_TEST'
)

# Check columns
print("\n" + "="*80)
print("RESULTS ANALYSIS")
print("="*80)

print(f"\nTotal columns: {len(results.columns)}")

print("\nShort-term columns:")
short_cols = [col for col in results.columns if col.startswith('short_')]
for col in short_cols:
    print(f"  - {col}")

print(f"\nTotal short-term columns: {len(short_cols)}")

print("\nChecking intermediate variables:")
intermediate_vars = ['moving_avg_price', 'realized_vol', 'realized_mad']
for horizon in ['short', 'mid', 'long']:
    print(f"\n{horizon.upper()} horizon:")
    for var in intermediate_vars:
        col_name = f'{horizon}_{var}'
        if col_name in results.columns:
            print(f"  [OK] {col_name}: {results[col_name].notna().sum()} valid values")
        else:
            print(f"  [MISSING] {col_name}")

# Show sample data
print("\n" + "="*80)
print("SAMPLE DATA (Last 5 rows)")
print("="*80)

sample_cols = [
    'price',
    'short_moving_avg_price',
    'short_momentum_value',
    'short_realized_vol',
    'short_realized_mad',
    'short_fragility_value',
    'short_avg_percentile',
    'composite_bri'
]

print(results[sample_cols].tail().to_string())

# Verify calculations
print("\n" + "="*80)
print("CALCULATION VERIFICATION")
print("="*80)

last_row = results.iloc[-1]
print(f"\nLast row analysis:")
print(f"  Current price: {last_row['price']:.2f}")
print(f"  Short MA price: {last_row['short_moving_avg_price']:.2f}")
print(f"  Short momentum: {last_row['short_momentum_value']:.2f}%")
print(f"  Calculated momentum check: {(last_row['price'] - last_row['short_moving_avg_price']) / last_row['short_moving_avg_price'] * 100:.2f}%")

print(f"\n  Short realized vol: {last_row['short_realized_vol']:.6f}")
print(f"  Short realized MAD: {last_row['short_realized_mad']:.6f}")
print(f"  Short fragility: {last_row['short_fragility_value']:.6f}")
print(f"  Calculated fragility check: {last_row['short_realized_vol'] - last_row['short_realized_mad']:.6f}")

print("\n[OK] Test completed successfully!")

