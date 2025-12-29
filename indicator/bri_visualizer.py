"""
BRI Visualizer - Interactive Visualization for Bubble Risk Indicator

Creates interactive HTML charts using plotly to visualize:
- Composite BRI over time
- Three sub-indicators (ST/MT/LT)
- Price overlay
- Adjustable time resolution (daily/weekly/monthly/yearly)
"""

import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class BRIVisualizer:
    """
    Interactive visualizer for BRI results
    
    Creates HTML charts with:
    - Zoom/pan capabilities
    - Time resolution selection
    - Multiple sub-indicators
    - Price overlay
    """
    
    def __init__(self):
        """Initialize visualizer with default settings"""
        self.colors = {
            'composite': '#1f77b4',  # Blue
            'short': '#ff7f0e',      # Orange
            'mid': '#2ca02c',        # Green
            'long': '#d62728',       # Red
            'price': '#9467bd',      # Purple
            'warning': '#ffbb00',    # Yellow
            'bubble': '#ff4444',     # Bright red
        }
        
        self.threshold_lines = {
            'warning': 1.5,
            'bubble': 2.0,
            'extreme': 2.5
        }
    
    def create_bri_chart(self,
                        bri_data: pd.DataFrame,
                        asset_name: str,
                        tick_format: str = 'Y',
                        show_price: bool = True,
                        show_thresholds: bool = True) -> go.Figure:
        """
        Create interactive BRI chart
        
        Parameters:
        -----------
        bri_data : pd.DataFrame
            BRI results from calculator (uses all daily data)
        asset_name : str
            Name of the asset
        tick_format : str
            X-axis tick format: 'D'=daily, 'W'=weekly, 'M'=monthly, 'Y'=yearly
        show_price : bool
            Whether to show price overlay
        show_thresholds : bool
            Whether to show threshold lines
        
        Returns:
        --------
        go.Figure: Plotly figure object
        """
        # Use all data (no resampling), just adjust display
        data = bri_data.copy()
        
        # Ensure datetime index
        if not isinstance(data.index, pd.DatetimeIndex):
            data.index = pd.to_datetime(data.index, utc=True)
        if data.index.tz is not None:
            data.index = data.index.tz_localize(None)
        
        # Create figure with secondary y-axis for price
        if show_price and 'price' in data.columns:
            fig = make_subplots(
                rows=2, cols=1,
                row_heights=[0.7, 0.3],
                subplot_titles=(
                    f'{asset_name} - BRI and Sub-Indicators',
                    f'{asset_name} - Price'
                ),
                vertical_spacing=0.1,
                specs=[[{"secondary_y": False}],
                       [{"secondary_y": False}]]
            )
        else:
            fig = go.Figure()
        
        # Add composite BRI
        if 'composite_bri' in data.columns:
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['composite_bri'],
                    name='Composite BRI',
                    line=dict(color=self.colors['composite'], width=3),
                    hovertemplate='%{x}<br>Composite BRI: %{y:.4f}<extra></extra>'
                ),
                row=1, col=1
            )
        
        # Add sub-indicators
        if 'short_indicator' in data.columns:
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['short_indicator'],
                    name='Short-term',
                    line=dict(color=self.colors['short'], width=2, dash='dot'),
                    hovertemplate='%{x}<br>ST: %{y:.4f}<extra></extra>'
                ),
                row=1, col=1
            )
        
        if 'mid_indicator' in data.columns:
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['mid_indicator'],
                    name='Mid-term',
                    line=dict(color=self.colors['mid'], width=2, dash='dash'),
                    hovertemplate='%{x}<br>MT: %{y:.4f}<extra></extra>'
                ),
                row=1, col=1
            )
        
        if 'long_indicator' in data.columns:
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['long_indicator'],
                    name='Long-term',
                    line=dict(color=self.colors['long'], width=2, dash='dashdot'),
                    hovertemplate='%{x}<br>LT: %{y:.4f}<extra></extra>'
                ),
                row=1, col=1
            )
        
        # Add threshold lines
        if show_thresholds:
            for threshold_name, threshold_value in self.threshold_lines.items():
                color = self.colors.get(threshold_name, '#888888')
                fig.add_hline(
                    y=threshold_value,
                    line_dash="dash",
                    line_color=color,
                    opacity=0.5,
                    annotation_text=threshold_name.capitalize(),
                    annotation_position="right",
                    row=1, col=1
                )
        
        # Add price subplot
        if show_price and 'price' in data.columns:
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['price'],
                    name='Price',
                    line=dict(color=self.colors['price'], width=2),
                    hovertemplate='%{x}<br>Price: %{y:.2f}<extra></extra>',
                    fill='tozeroy',
                    fillcolor='rgba(148, 103, 189, 0.1)'
                ),
                row=2, col=1
            )
        
        # Configure x-axis tick format
        dtick_settings = {
            'D': 'D1',      # Every day
            'W': 'D7',      # Every week
            'M': 'M1',      # Every month
            'Y': 'M12'      # Every year
        }
        
        tick_format_str = {
            'D': '%Y-%m-%d',
            'W': '%Y-%m-%d',
            'M': '%Y-%m',
            'Y': '%Y'
        }
        
        # Update layout
        fig.update_layout(
            title=f'{asset_name} - Bubble Risk Indicator (Daily Data, {tick_format.upper()} Ticks)',
            xaxis_title='Date',
            yaxis_title='BRI Value',
            hovermode='x unified',
            template='plotly_white',
            height=800 if show_price else 600,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            # Enable range slider with custom tick format
            xaxis=dict(
                rangeslider=dict(visible=True),
                type='date',
                dtick=dtick_settings.get(tick_format, 'M12'),
                tickformat=tick_format_str.get(tick_format, '%Y')
            )
        )
        
        if show_price:
            fig.update_yaxes(title_text="BRI Value", row=1, col=1)
            fig.update_yaxes(title_text="Price", row=2, col=1)
        
        return fig
    
    def create_percentile_chart(self,
                               bri_data: pd.DataFrame,
                               asset_name: str,
                               horizon: str = 'short',
                               tick_format: str = 'Y') -> go.Figure:
        """
        Create chart showing percentile ranks for all four moments
        
        Parameters:
        -----------
        bri_data : pd.DataFrame
            BRI results from calculator (uses all daily data)
        asset_name : str
            Name of the asset
        horizon : str
            Which horizon to show: 'short', 'mid', or 'long'
        tick_format : str
            X-axis tick format: 'D', 'W', 'M', 'Y'
        
        Returns:
        --------
        go.Figure: Plotly figure object
        """
        # Use all data
        data = bri_data.copy()
        
        # Ensure datetime index
        if not isinstance(data.index, pd.DatetimeIndex):
            data.index = pd.to_datetime(data.index, utc=True)
        if data.index.tz is not None:
            data.index = data.index.tz_localize(None)
        
        fig = go.Figure()
        
        # Add each moment's percentile
        moments = ['returns', 'volatility', 'momentum', 'fragility']
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
        
        for moment, color in zip(moments, colors):
            col_name = f'{horizon}_{moment}_pctile'
            if col_name in data.columns:
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=data[col_name],
                        name=moment.capitalize(),
                        line=dict(color=color, width=2),
                        hovertemplate=f'%{{x}}<br>{moment}: %{{y:.1f}} pctile<extra></extra>'
                    )
                )
        
        # Add average percentile
        avg_col = f'{horizon}_avg_percentile'
        if avg_col in data.columns:
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data[avg_col],
                    name='Average',
                    line=dict(color='black', width=3),
                    hovertemplate='%{x}<br>Avg: %{y:.1f} pctile<extra></extra>'
                )
            )
        
        # Add reference lines
        for pctile, label in [(25, '25th'), (50, '50th (median)'), (75, '75th')]:
            fig.add_hline(
                y=pctile,
                line_dash="dash",
                line_color='gray',
                opacity=0.3,
                annotation_text=label,
                annotation_position="right"
            )
        
        # Configure x-axis tick format
        dtick_settings = {
            'D': 'D1',
            'W': 'D7',
            'M': 'M1',
            'Y': 'M12'
        }
        
        tick_format_str = {
            'D': '%Y-%m-%d',
            'W': '%Y-%m-%d',
            'M': '%Y-%m',
            'Y': '%Y'
        }
        
        fig.update_layout(
            title=f'{asset_name} - {horizon.capitalize()}-term Percentile Ranks (Daily Data, {tick_format.upper()} Ticks)',
            xaxis_title='Date',
            yaxis_title='Percentile Rank (0-100)',
            hovermode='x unified',
            template='plotly_white',
            height=600,
            yaxis=dict(range=[0, 100]),
            xaxis=dict(
                rangeslider=dict(visible=True),
                type='date',
                dtick=dtick_settings.get(tick_format, 'M12'),
                tickformat=tick_format_str.get(tick_format, '%Y')
            )
        )
        
        return fig
    
    def create_dashboard(self,
                        bri_data: pd.DataFrame,
                        asset_name: str,
                        tick_format: str = 'Y',
                        output_path: Optional[str] = None) -> str:
        """
        Create comprehensive dashboard with multiple views
        
        Parameters:
        -----------
        bri_data : pd.DataFrame
            BRI results from calculator (all daily data)
        asset_name : str
            Name of the asset
        tick_format : str
            X-axis tick format: 'D'=daily, 'W'=weekly, 'M'=monthly, 'Y'=yearly (default)
        output_path : str, optional
            Path to save HTML file
        
        Returns:
        --------
        str: Path to saved HTML file
        """
        # Create main BRI chart (uses all daily data)
        fig_main = self.create_bri_chart(bri_data, asset_name, tick_format)
        
        # Create percentile charts for each horizon (uses all daily data)
        fig_st = self.create_percentile_chart(bri_data, asset_name, 'short', tick_format)
        fig_mt = self.create_percentile_chart(bri_data, asset_name, 'mid', tick_format)
        fig_lt = self.create_percentile_chart(bri_data, asset_name, 'long', tick_format)
        
        # Save to HTML
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f'bri_dashboard_{asset_name}_{timestamp}.html'
        
        # Create HTML with all charts
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{asset_name} BRI Dashboard</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: #f5f5f5;
                }}
                .header {{
                    text-align: center;
                    padding: 20px;
                    background-color: white;
                    border-radius: 10px;
                    margin-bottom: 20px;
                }}
                .chart-container {{
                    background-color: white;
                    padding: 20px;
                    margin-bottom: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .controls {{
                    text-align: center;
                    padding: 10px;
                    margin-bottom: 20px;
                }}
                button {{
                    padding: 10px 20px;
                    margin: 5px;
                    font-size: 14px;
                    cursor: pointer;
                    border: none;
                    border-radius: 5px;
                    background-color: #1f77b4;
                    color: white;
                }}
                button:hover {{
                    background-color: #1562a6;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{asset_name} - Bubble Risk Indicator Dashboard</h1>
                <p>Interactive visualization of BRI and sub-indicators (Daily Data)</p>
                <p><strong>X-axis Ticks:</strong> {tick_format.upper()} | <strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="chart-container">
                <h2>BRI Overview</h2>
                {fig_main.to_html(include_plotlyjs=False, div_id='main_chart')}
            </div>
            
            <div class="chart-container">
                <h2>Short-term Percentile Ranks</h2>
                {fig_st.to_html(include_plotlyjs=False, div_id='st_chart')}
            </div>
            
            <div class="chart-container">
                <h2>Mid-term Percentile Ranks</h2>
                {fig_mt.to_html(include_plotlyjs=False, div_id='mt_chart')}
            </div>
            
            <div class="chart-container">
                <h2>Long-term Percentile Ranks</h2>
                {fig_lt.to_html(include_plotlyjs=False, div_id='lt_chart')}
            </div>
            
            <div class="header">
                <p><em>Use mouse to zoom, double-click to reset. Drag range slider to navigate time periods.</em></p>
            </div>
        </body>
        </html>
        """
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"[OK] Dashboard saved to: {output_path}")
        return output_path
    
    def visualize_from_csv(self,
                          csv_path: str,
                          asset_name: Optional[str] = None,
                          tick_format: str = 'Y',
                          output_dir: Optional[str] = None) -> str:
        """
        Create visualization directly from CSV file
        
        Parameters:
        -----------
        csv_path : str
            Path to BRI results CSV
        asset_name : str, optional
            Asset name (extracted from filename if not provided)
        tick_format : str
            X-axis tick format: 'D', 'W', 'M', 'Y' (default: 'Y')
        output_dir : str, optional
            Output directory for HTML
        
        Returns:
        --------
        str: Path to saved HTML file
        """
        # Load data
        data = pd.read_csv(csv_path, index_col=0, parse_dates=True)
        
        # Extract asset name from filename if not provided
        if asset_name is None:
            asset_name = Path(csv_path).stem.split('_BRI')[0]
        
        # Determine output path
        if output_dir:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f'{output_dir}/{asset_name}_dashboard_{timestamp}.html'
        else:
            output_path = None
        
        # Create dashboard (uses all daily data, only adjusts x-axis ticks)
        return self.create_dashboard(data, asset_name, tick_format, output_path)


def batch_visualize(results_dir: str,
                   output_dir: str = 'bri_visualizations',
                   tick_format: str = 'Y') -> List[str]:
    """
    Create visualizations for all BRI results in a directory
    
    Parameters:
    -----------
    results_dir : str
        Directory containing BRI CSV files
    output_dir : str
        Directory to save HTML dashboards
    tick_format : str
        X-axis tick format: 'D'=daily, 'W'=weekly, 'M'=monthly, 'Y'=yearly (default)
    
    Returns:
    --------
    List[str]: Paths to created HTML files
    """
    from pathlib import Path
    
    visualizer = BRIVisualizer()
    html_files = []
    
    # Find all CSV files
    csv_files = list(Path(results_dir).glob('*_BRI_*.csv'))
    
    print(f"\nCreating visualizations for {len(csv_files)} assets...")
    print(f"Using all daily data, X-axis ticks: {tick_format.upper()}")
    
    for csv_file in csv_files:
        try:
            print(f"\nProcessing: {csv_file.name}")
            html_path = visualizer.visualize_from_csv(
                str(csv_file),
                tick_format=tick_format,
                output_dir=output_dir
            )
            html_files.append(html_path)
        except Exception as e:
            print(f"[ERROR] Failed to visualize {csv_file.name}: {str(e)}")
    
    print(f"\n[OK] Created {len(html_files)} dashboards in {output_dir}/")
    return html_files

