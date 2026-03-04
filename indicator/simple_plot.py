"""
Simple BRI Visualization using Matplotlib
Creates clean, static PNG charts that are easy to view and debug
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path
import numpy as np


def create_simple_bri_chart(csv_path, output_dir='bri_plots'):
    """
    Create simple, clean BRI charts using matplotlib
    
    Parameters:
    -----------
    csv_path : str
        Path to BRI results CSV
    output_dir : str
        Output directory for PNG files
    """
    # Load data
    print(f"Loading: {csv_path}")
    df = pd.read_csv(csv_path, index_col=0)
    
    # Convert to datetime index (handle timezone)
    df.index = pd.to_datetime(df.index, utc=True)
    
    # Remove timezone for matplotlib compatibility
    df.index = df.index.tz_localize(None)
    
    # Extract asset name
    asset_name = Path(csv_path).stem.split('_BRI')[0]
    
    # Create output directory
    Path(output_dir).mkdir(exist_ok=True)
    
    # Print data statistics
    print(f"\nAsset: {asset_name}")
    print(f"Date range: {df.index[0]} to {df.index[-1]}")
    print(f"Total rows: {len(df)}")
    
    print("\nBRI Statistics:")
    bri_cols = ['short_indicator', 'mid_indicator', 'long_indicator', 'composite_bri']
    for col in bri_cols:
        if col in df.columns:
            valid_data = df[col].dropna()
            print(f"  {col}: min={valid_data.min():.4f}, max={valid_data.max():.4f}, mean={valid_data.mean():.4f}")
    
    # Create figure with 2 subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
    fig.suptitle(f'{asset_name} - BRI Analysis', fontsize=16, fontweight='bold')
    
    # ========== Plot 1: BRI Indicators ==========
    ax1.set_title('BRI Indicators (Range: 0-1)', fontsize=12, pad=10)
    
    # Plot composite BRI
    if 'composite_bri' in df.columns:
        ax1.plot(df.index, df['composite_bri'], 
                label='Composite BRI', color='#1f77b4', linewidth=2.5, alpha=0.9)
    
    # Plot sub-indicators
    if 'short_indicator' in df.columns:
        ax1.plot(df.index, df['short_indicator'], 
                label='Short-term', color='#ff7f0e', linewidth=1.5, alpha=0.7, linestyle='--')
    
    if 'mid_indicator' in df.columns:
        ax1.plot(df.index, df['mid_indicator'], 
                label='Mid-term', color='#2ca02c', linewidth=1.5, alpha=0.7, linestyle='--')
    
    if 'long_indicator' in df.columns:
        ax1.plot(df.index, df['long_indicator'], 
                label='Long-term', color='#d62728', linewidth=1.5, alpha=0.7, linestyle='--')
    
    # Add threshold lines
    ax1.axhline(y=0.5, color='orange', linestyle=':', linewidth=1, alpha=0.5, label='50% level')
    ax1.axhline(y=0.75, color='red', linestyle=':', linewidth=1, alpha=0.5, label='75% level')
    
    # Configure ax1
    ax1.set_ylabel('BRI Value', fontsize=11)
    ax1.set_ylim(-0.05, 1.05)  # Ensure we see 0-1 range
    ax1.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    ax1.legend(loc='upper left', fontsize=9, framealpha=0.9)
    
    # ========== Plot 2: Asset Price ==========
    ax2.set_title('Asset Price', fontsize=12, pad=10)
    
    if 'price' in df.columns:
        ax2.plot(df.index, df['price'], 
                color='#9467bd', linewidth=1.5, alpha=0.8)
        ax2.fill_between(df.index, df['price'], alpha=0.2, color='#9467bd')
    
    ax2.set_ylabel('Price', fontsize=11)
    ax2.set_xlabel('Date', fontsize=11)
    ax2.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    
    # Format x-axis with years
    ax2.xaxis.set_major_locator(mdates.YearLocator())
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax2.xaxis.set_minor_locator(mdates.MonthLocator((1, 7)))
    
    # Rotate dates
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # Tight layout
    plt.tight_layout()
    
    # Save
    output_path = f"{output_dir}/{asset_name}_BRI_simple.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\n[OK] Chart saved: {output_path}")
    
    plt.close()
    
    return output_path


def create_percentile_chart(csv_path, output_dir='bri_plots'):
    """
    Create chart showing percentile ranks
    """
    # Load data
    df = pd.read_csv(csv_path, index_col=0)
    
    # Convert to datetime index (handle timezone)
    df.index = pd.to_datetime(df.index, utc=True)
    df.index = df.index.tz_localize(None)
    
    asset_name = Path(csv_path).stem.split('_BRI')[0]
    
    # Create figure with 3 subplots for each horizon
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 12), sharex=True)
    fig.suptitle(f'{asset_name} - Percentile Rankings (0-100)', fontsize=16, fontweight='bold')
    
    horizons = [
        ('short', ax1, 'Short-term (3m)'),
        ('mid', ax2, 'Mid-term (6m)'),
        ('long', ax3, 'Long-term (1y)')
    ]
    
    colors = {
        'returns': '#1f77b4',
        'volatility': '#ff7f0e',
        'momentum': '#2ca02c',
        'fragility': '#d62728',
        'avg': 'black'
    }
    
    for horizon, ax, title in horizons:
        ax.set_title(title, fontsize=11, pad=10)
        
        # Plot each moment's percentile
        for moment in ['returns', 'volatility', 'momentum', 'fragility']:
            col = f'{horizon}_{moment}_pctile'
            if col in df.columns:
                ax.plot(df.index, df[col], 
                       label=moment.capitalize(), 
                       color=colors[moment],
                       linewidth=1.2, alpha=0.7)
        
        # Plot average
        avg_col = f'{horizon}_avg_percentile'
        if avg_col in df.columns:
            ax.plot(df.index, df[avg_col], 
                   label='Average', 
                   color=colors['avg'],
                   linewidth=2, alpha=0.9)
        
        # Reference lines
        for pct, style in [(25, ':'), (50, '--'), (75, ':')]:
            ax.axhline(y=pct, color='gray', linestyle=style, 
                      linewidth=0.8, alpha=0.4)
        
        ax.set_ylabel('Percentile', fontsize=10)
        ax.set_ylim(-5, 105)
        ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
        ax.legend(loc='upper left', fontsize=8, ncol=5, framealpha=0.9)
    
    # Format x-axis
    ax3.set_xlabel('Date', fontsize=11)
    ax3.xaxis.set_major_locator(mdates.YearLocator())
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    
    # Save
    output_path = f"{output_dir}/{asset_name}_percentiles.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"[OK] Chart saved: {output_path}")
    
    plt.close()
    
    return output_path


def create_bri_price_chart(csv_path, output_dir='bri_plots'):
    """
    Create simplified chart with only Composite BRI and Price
    
    Parameters:
    -----------
    csv_path : str
        Path to BRI results CSV
    output_dir : str
        Output directory for PNG files
    """
    # Load data
    print(f"Loading: {csv_path}")
    df = pd.read_csv(csv_path, index_col=0)
    
    # Convert to datetime index (handle timezone)
    df.index = pd.to_datetime(df.index, utc=True)
    
    # Remove timezone for matplotlib compatibility
    df.index = df.index.tz_localize(None)
    
    # Extract asset name
    asset_name = Path(csv_path).stem.split('_BRI')[0]
    
    # Create output directory
    Path(output_dir).mkdir(exist_ok=True)
    
    # Create figure with 2 subplots (BRI on top, Price on bottom)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
    fig.suptitle(f'{asset_name} - BRI & Price', fontsize=16, fontweight='bold')
    
    # ========== Plot 1: Composite BRI Only ==========
    ax1.set_title('Composite Bubble Risk Indicator', fontsize=12, pad=10)
    
    if 'composite_bri' in df.columns:
        ax1.plot(df.index, df['composite_bri'], 
                label='Composite BRI', color='#1f77b4', linewidth=2.5, alpha=0.9)
    
    # Add threshold lines
    ax1.axhline(y=0.25, color='green', linestyle=':', linewidth=1, alpha=0.5, label='25% (Low)')
    ax1.axhline(y=0.5, color='orange', linestyle=':', linewidth=1, alpha=0.5, label='50% (Moderate)')
    ax1.axhline(y=0.75, color='red', linestyle=':', linewidth=1, alpha=0.5, label='75% (High)')
    
    ax1.set_ylabel('BRI Value', fontsize=11, fontweight='bold')
    ax1.set_ylim(-0.05, 1.05)
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.legend(loc='upper left', fontsize=9, framealpha=0.9)
    
    # Add statistics text
    if 'composite_bri' in df.columns:
        valid_bri = df['composite_bri'].dropna()
        current_bri = valid_bri.iloc[-1]
        mean_bri = valid_bri.mean()
        max_bri = valid_bri.max()
        
        stats_text = f'Current: {current_bri:.3f} | Mean: {mean_bri:.3f} | Max: {max_bri:.3f}'
        ax1.text(0.99, 0.97, stats_text, transform=ax1.transAxes,
                fontsize=9, verticalalignment='top', horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # ========== Plot 2: Price ==========
    ax2.set_title('Asset Price', fontsize=12, pad=10)
    
    if 'price' in df.columns:
        ax2.plot(df.index, df['price'], 
                label='Price', color='#2ca02c', linewidth=2, alpha=0.8)
    
    ax2.set_ylabel('Price', fontsize=11, fontweight='bold')
    ax2.set_xlabel('Date', fontsize=11, fontweight='bold')
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.legend(loc='upper left', fontsize=9, framealpha=0.9)
    
    # Format x-axis
    ax2.xaxis.set_major_locator(mdates.YearLocator())
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax2.xaxis.set_minor_locator(mdates.MonthLocator())
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # Add price statistics
    if 'price' in df.columns:
        valid_price = df['price'].dropna()
        current_price = valid_price.iloc[-1]
        
        stats_text = f'Current: ${current_price:,.2f}'
        ax2.text(0.99, 0.97, stats_text, transform=ax2.transAxes,
                fontsize=9, verticalalignment='top', horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    # Adjust layout
    plt.tight_layout()
    
    # Save
    output_path = Path(output_dir) / f'{asset_name}_BRI_price.png'
    plt.savefig(output_path, dpi=100, bbox_inches='tight')
    plt.close()
    
    print(f"[OK] Chart saved: {output_path}")
    
    return output_path


def batch_plot_all(results_dir='bri_results_v2_with_intermediates', 
                   output_dir='bri_plots'):
    """
    Create simple plots for all BRI results
    """
    print("="*80)
    print("SIMPLE BRI VISUALIZATION")
    print("="*80)
    print(f"Input: {results_dir}/")
    print(f"Output: {output_dir}/")
    print()
    
    csv_files = list(Path(results_dir).glob('*_BRI_*.csv'))
    
    if not csv_files:
        print(f"[ERROR] No CSV files found in {results_dir}/")
        return
    
    print(f"Found {len(csv_files)} assets\n")
    
    for csv_file in csv_files:
        print("-" * 80)
        try:
            # Create BRI + Price simplified chart
            create_bri_price_chart(str(csv_file), output_dir)
            
            # Create detailed BRI chart
            create_simple_bri_chart(str(csv_file), output_dir)
            
            # Create percentile chart
            create_percentile_chart(str(csv_file), output_dir)
            
        except Exception as e:
            print(f"[ERROR] Failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*80)
    print(f"COMPLETE! Charts saved to: {output_dir}/")
    print("="*80)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Single asset
        asset_name = sys.argv[1]
        csv_pattern = f'bri_results_v2_with_intermediates/{asset_name}_BRI_*.csv'
        import glob
        files = glob.glob(csv_pattern)
        if files:
            create_bri_price_chart(files[0])
            create_simple_bri_chart(files[0])
            create_percentile_chart(files[0])
        else:
            print(f"No file found for {asset_name}")
    else:
        # All assets
        batch_plot_all()

