"""
Create BRI Visualizations

This script creates interactive HTML dashboards for BRI results.
You can choose time resolution and which assets to visualize.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from indicator.bri_visualizer import BRIVisualizer, batch_visualize


def main():
    """
    Create visualizations for all BRI results
    """
    print("="*80)
    print("BRI VISUALIZATION GENERATOR")
    print("="*80)
    
    # Configuration
    results_dir = 'bri_results_v2_with_intermediates'  # Use results with intermediate variables
    output_dir = 'bri_visualizations'
    
    # X-axis tick format options:
    # 'D' = Daily ticks
    # 'W' = Weekly ticks
    # 'M' = Monthly ticks
    # 'Y' = Yearly ticks (default, best for long time series)
    tick_format = 'Y'  # Yearly by default
    
    print(f"\nInput directory: {results_dir}")
    print(f"Output directory: {output_dir}")
    print(f"X-axis tick format: {tick_format} (uses all daily data)")
    
    # Batch process all assets
    html_files = batch_visualize(results_dir, output_dir, tick_format)
    
    print("\n" + "="*80)
    print("VISUALIZATION COMPLETE")
    print("="*80)
    print(f"\nCreated {len(html_files)} interactive dashboards")
    print(f"\nTo view:")
    print(f"1. Navigate to: {output_dir}/")
    print(f"2. Open any HTML file in your browser")
    print(f"3. Use mouse to zoom, pan, and interact with charts")
    print("\nFeatures:")
    print("  - All daily data points preserved")
    print("  - Zoom: Click and drag on chart")
    print("  - Pan: Hold shift and drag")
    print("  - Reset: Double-click on chart")
    print("  - Range slider: Drag to change time range")
    print("  - Legend: Click to toggle series on/off")
    print(f"\nNote: Charts use all daily data points, X-axis shows {tick_format.upper()} ticks")
    
    if html_files:
        print(f"\nFirst dashboard: {html_files[0]}")


def create_single_asset(asset_name: str = 'NASDAQ_100', tick_format: str = 'Y'):
    """
    Create visualization for a single asset
    
    Parameters:
    -----------
    asset_name : str
        Asset name (e.g., 'NASDAQ_100', 'BITCOIN')
    tick_format : str
        X-axis tick format: 'D', 'W', 'M', 'Y' (default: 'Y')
    """
    import pandas as pd
    from glob import glob
    
    print(f"\nCreating visualization for {asset_name}...")
    print(f"Using all daily data, X-axis ticks: {tick_format.upper()}")
    
    # Find the CSV file
    pattern = f'bri_results_v2_with_intermediates/{asset_name}_BRI_*.csv'
    files = glob(pattern)
    
    if not files:
        print(f"[ERROR] No results found for {asset_name}")
        print(f"  Searched: {pattern}")
        return
    
    csv_file = files[0]
    print(f"  Loading: {csv_file}")
    
    # Create visualizer
    visualizer = BRIVisualizer()
    
    # Create dashboard
    html_path = visualizer.visualize_from_csv(
        csv_file,
        asset_name=asset_name,
        tick_format=tick_format,
        output_dir='bri_visualizations'
    )
    
    print(f"\n[OK] Dashboard created: {html_path}")
    print(f"  Open in browser to view interactive charts")
    print(f"  Note: Chart shows all daily data points with {tick_format.upper()} tick labels")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Create BRI visualizations (uses all daily data, only changes x-axis tick labels)'
    )
    parser.add_argument('--asset', type=str, help='Single asset to visualize')
    parser.add_argument('--ticks', type=str, default='Y', 
                       choices=['D', 'W', 'M', 'Y'],
                       help='X-axis tick format: D=daily, W=weekly, M=monthly, Y=yearly (default)')
    parser.add_argument('--all', action='store_true',
                       help='Create dashboards for all assets')
    
    args = parser.parse_args()
    
    if args.asset:
        create_single_asset(args.asset, args.ticks)
    else:
        # Default: create all
        main()

