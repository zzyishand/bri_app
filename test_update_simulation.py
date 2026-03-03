"""
Test script to simulate database with lagged data and run update
Usage: python test_update_simulation.py
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import sqlite3

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.bri_database import BRIDatabase
from services.bri_update_service import BRIUpdateService
from data_fetch_and_process.bri_data_fetcher import BRI_ASSETS


def create_lagged_test_data(db: BRIDatabase, asset_name: str, lag_days: int = 30):
    """
    Create test price data that is lagged by specified days

    Args:
        db: Database instance
        asset_name: Name of the asset
        lag_days: How many days to lag behind (default 30 = 1 month)
    """
    print(f"\n{'='*60}")
    print(f"Creating lagged test data for {asset_name}")
    print(f"Simulating {lag_days} days data lag")
    print(f"{'='*60}")

    # First, clear any existing data for this asset
    print(f"\nClearing existing data for {asset_name}...")
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM price_data WHERE asset_name = ?", (asset_name,))
    cursor.execute("DELETE FROM bri_results WHERE asset_name = ?", (asset_name,))
    conn.commit()
    conn.close()
    print(f"Existing data cleared.")

    # Get today's date and create a date range that ends 'lag_days' ago
    end_date = datetime.now() - timedelta(days=lag_days)
    start_date = end_date - timedelta(days=365)  # 1 year of data

    # Create synthetic price data
    dates = pd.date_range(start=start_date, end=end_date, freq='B')  # Business days

    # Generate realistic-looking price data with random walk
    np.random.seed(42)  # For reproducibility
    returns = np.random.normal(0.0005, 0.01, len(dates))  # Daily returns
    price = 100 * np.exp(np.cumsum(returns))  # Random walk starting at 100

    # Create DataFrame with proper index name
    price_data = pd.DataFrame({
        'Open': price * (1 + np.random.normal(0, 0.005, len(dates))),
        'High': price * (1 + np.abs(np.random.normal(0, 0.01, len(dates)))),
        'Low': price * (1 - np.abs(np.random.normal(0, 0.01, len(dates)))),
        'Close': price,
        'Volume': np.random.randint(1000000, 10000000, len(dates))
    }, index=dates)
    price_data.index.name = 'Date'  # Important: set index name for database

    print(f"Created {len(price_data)} rows")
    print(f"Date range: {price_data.index[0].strftime('%Y-%m-%d')} to {price_data.index[-1].strftime('%Y-%m-%d')}")

    # Save to database
    db.save_price_data(asset_name, price_data)
    db.log_update(asset_name, 'test_lag_setup', 'success', len(price_data),
                  f"Created lagged test data (lag={lag_days} days)")

    # Also calculate initial BRI for the lagged data
    from indicator.bri_calculator_v2 import BRICalculatorV2
    from indicator.bri_config import get_config

    config = get_config('default')
    calculator = BRICalculatorV2(config)

    print(f"\nCalculating initial BRI for lagged data...")
    bri_results = calculator.calculate_full_bri(
        price_data,
        price_column='Close',
        asset_name=asset_name
    )

    if not bri_results.empty:
        db.save_bri_results(asset_name, bri_results)
        db.log_update(asset_name, 'test_bri_setup', 'success', len(bri_results),
                      f"Calculated {len(bri_results)} BRI rows for lagged data")
        print(f"BRI calculated: {len(bri_results)} rows")
        print(f"BRI date range: {bri_results.index[0].strftime('%Y-%m-%d')} to {bri_results.index[-1].strftime('%Y-%m-%d')}")
    else:
        print("WARNING: No BRI results generated!")

    # Show current database status
    print(f"\n--- Current Database Status ---")
    last_price = db.get_last_date(asset_name, 'price_data')
    last_bri = db.get_last_date(asset_name, 'bri_results')
    print(f"Last price date in DB: {last_price}")
    print(f"Last BRI date in DB: {last_bri}")

    return price_data


def run_update_and_observe(asset_name: str, ticker: str):
    """
    Run the update service and observe the procedure
    """
    print(f"\n{'='*60}")
    print(f"RUNNING UPDATE FOR: {asset_name}")
    print(f"{'='*60}")

    # Create update service
    update_service = BRIUpdateService('data/bri_data.db')

    # Step 1: Check for updates
    print(f"\n>>> STEP 1: Checking for updates...")

    # Debug: Let's manually check the database before calling check
    print(f"\n--- Debug: Manual Database Check ---")
    db_check = BRIDatabase('data/bri_data.db')
    manual_last_date = db_check.get_last_date(asset_name, 'price_data')
    print(f"Manual check - Last date in DB: {manual_last_date}")
    print(f"Manual check - Type: {type(manual_last_date)}")

    check_result = update_service.check_for_updates(asset_name, ticker)

    # Debug: Print raw result
    print(f"\n--- Raw Check Result ---")
    print(f"Full result dict: {check_result}")

    print(f"\nCheck Result:")
    print(f"  has_new_data: {check_result.get('has_new_data')}")
    print(f"  last_db_date: {check_result.get('last_db_date')}")
    print(f"  latest_available_date: {check_result.get('latest_available_date')}")
    print(f"  new_rows: {check_result.get('new_rows')}")
    print(f"  update_type: {check_result.get('update_type')}")

    if check_result.get('has_new_data'):
        # Step 2: Run actual update
        print(f"\n>>> STEP 2: Running full update...")
        print(f"\n--- Observing Update Procedure ---\n")

        # Note: Using force_full=True to test full recalculation
        # The incremental update path also works (same timezone fix applies)
        update_result = update_service.update_asset(asset_name, ticker, force_full=True)

        print(f"\n--- Update Result ---")
        print(f"  success: {update_result.get('success')}")
        print(f"  price_rows: {update_result.get('price_rows')}")
        print(f"  new_bri_rows: {update_result.get('new_bri_rows')}")
        print(f"  last_date: {update_result.get('last_date')}")
        print(f"  message: {update_result.get('message')}")

        if not update_result.get('success'):
            print(f"  ERROR: {update_result.get('error')}")

        # Verify final database state
        print(f"\n--- Final Database Status ---")
        db = BRIDatabase('data/bri_data.db')
        final_price_date = db.get_last_date(asset_name, 'price_data')
        final_bri_date = db.get_last_date(asset_name, 'bri_results')
        print(f"Last price date in DB: {final_price_date}")
        print(f"Last BRI date in DB: {final_bri_date}")

        return update_result
    else:
        print(f"\nNo updates needed (already up to date)")
        return None


def main():
    """Main test function"""
    print("="*70)
    print("BRI UPDATE SIMULATION TEST")
    print("Testing update logic with simulated 1-month data lag")
    print("="*70)

    # Select an asset to test
    test_asset = 'DOW_JONES'  # You can change to any asset in BRI_ASSETS
    test_ticker = BRI_ASSETS[test_asset]['yahoo_ticker']

    print(f"\nSelected asset: {test_asset}")
    print(f"Yahoo ticker: {test_ticker}")

    # Create database connection
    db = BRIDatabase('data/bri_data.db')

    # Step 1: Create lagged test data
    create_lagged_test_data(db, test_asset, lag_days=30)

    # Step 2: Run update and observe
    run_update_and_observe(test_asset, test_ticker)

    print(f"\n{'='*70}")
    print("TEST COMPLETE")
    print("="*70)

    print(f"\nTo verify the update worked:")
    print(f"1. Go to the Dashboard page in the app")
    print(f"2. Look at the bubble indicators for {test_asset}")
    print(f"3. Check if the data is now up to date")


if __name__ == "__main__":
    main()
