"""
BRI Bubble Risk Indicator - 完整应用
包含数据获取、BRI计算和可视化功能
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
from datetime import datetime, timedelta
import sys

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.bri_database import BRIDatabase
from services.bri_update_service import BRIUpdateService
from services.custom_ticker_service import CustomTickerService
from data_fetch_and_process.bri_data_fetcher import BRI_ASSETS

# Page configuration
st.set_page_config(
    page_title="BRI Monitor & Update System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Asset information with Chinese names
ASSET_INFO = {
    'DOW_JONES': {'name_en': 'Dow Jones', 'name_cn': '道琼斯', 'category': 'Global Equity'},
    'NASDAQ_100': {'name_en': 'NASDAQ-100', 'name_cn': '纳斯达克100', 'category': 'Global Equity'},
    'NIKKEI_225': {'name_en': 'Nikkei 225', 'name_cn': '日经225', 'category': 'Global Equity'},
    'HSI': {'name_en': 'Hang Seng', 'name_cn': '恒生指数', 'category': 'Global Equity'},
    'DAX': {'name_en': 'DAX', 'name_cn': '德国DAX', 'category': 'Global Equity'},
    'CSI300': {'name_en': 'CSI 300', 'name_cn': '中证300', 'category': 'Global Equity'},
    'CSI500': {'name_en': 'CSI 500', 'name_cn': '中证500', 'category': 'Global Equity'},
    'HSTECH': {'name_en': 'HSTECH', 'name_cn': '恒生科技', 'category': 'Global Equity'},
    'XLF': {'name_en': 'Financials', 'name_cn': '金融', 'category': 'US Sectors'},
    'XLY': {'name_en': 'Consumer Disc.', 'name_cn': '可选消费', 'category': 'US Sectors'},
    'XLC': {'name_en': 'Communication', 'name_cn': '通信服务', 'category': 'US Sectors'},
    'XLI': {'name_en': 'Industrials', 'name_cn': '工业', 'category': 'US Sectors'},
    'XLK': {'name_en': 'Technology', 'name_cn': '科技', 'category': 'US Sectors'},
    'XLV': {'name_en': 'Healthcare', 'name_cn': '医疗', 'category': 'US Sectors'},
    'XLE': {'name_en': 'Energy', 'name_cn': '能源', 'category': 'US Sectors'},
    'IXE': {'name_en': 'Energy Index', 'name_cn': '能源指数', 'category': 'US Sectors'},
    'BIOTECH': {'name_en': 'Biotech', 'name_cn': '生物科技', 'category': 'US Sectors'},
    'GOLD': {'name_en': 'Gold', 'name_cn': '黄金', 'category': 'Commodity'},
    'SILVER': {'name_en': 'Silver', 'name_cn': '白银', 'category': 'Commodity'},
    'CRUDE_OIL': {'name_en': 'Crude Oil', 'name_cn': '原油', 'category': 'Commodity'},
    'COPPER': {'name_en': 'Copper', 'name_cn': '铜', 'category': 'Commodity'},
    'US_DOLLAR_INDEX': {'name_en': 'USD Index', 'name_cn': '美元指数', 'category': 'Currency'},
    'JPY': {'name_en': 'JPY/USD', 'name_cn': '日元', 'category': 'Currency'},
    'EUR': {'name_en': 'EUR/USD', 'name_cn': '欧元', 'category': 'Currency'},
    'BITCOIN': {'name_en': 'Bitcoin', 'name_cn': '比特币', 'category': 'Crypto'},
    'MAG7': {'name_en': 'Mag 7', 'name_cn': '科技7巨头', 'category': 'Tech Giants'},
    'IG_SPREAD': {'name_en': 'IG Spread', 'name_cn': '投资级利差', 'category': 'Credit'},
    'HY_SPREAD': {'name_en': 'HY Spread', 'name_cn': '高收益利差', 'category': 'Credit'}
}

# Common Assets - Most watched assets (默认显示)
COMMON_ASSETS = [
    'GOLD', 'CRUDE_OIL', 'COPPER',  # Commodities
    'CSI300', 'HSI', 'NASDAQ_100', 'NIKKEI_225', 'DAX', 'DOW_JONES',  # Global Equities
    'US_DOLLAR_INDEX', 'EUR', 'JPY',  # Currencies
    'IG_SPREAD', 'HY_SPREAD'  # Credit Spreads
]

# Category color mapping - 按资产类别分配颜色
CATEGORY_COLORS = {
    'Commodity': '#F39C12',      # Orange - 商品
    'Credit': '#E74C3C',          # Red - 信用利差
    'Currency': '#3498DB',        # Blue - 货币
    'Global Equity': '#9B59B6',   # Purple - 全球股指
    'US Sectors': '#1ABC9C',      # Teal/Green - 美国行业
    'Crypto': '#F1C40F',          # Yellow - 加密货币
    'Tech Giants': '#34495E'      # Dark Gray - 科技巨头
}

def get_category_color(category):
    """
    Get color for asset category
    Returns predefined color or generates consistent color for custom categories
    """
    if category in CATEGORY_COLORS:
        return CATEGORY_COLORS[category]
    
    # 为自定义category生成一致的颜色（基于名称hash）
    # 这样同一个category名称总是得到相同的颜色
    import hashlib
    
    # 预定义的额外颜色池（用于常见自定义category）
    custom_colors = {
        'My Portfolio': '#E67E22',      # 深橙色
        'Watch List': '#16A085',        # 深青色
        'Tech Stocks': '#8E44AD',       # 深紫色
        'Chinese Stocks': '#C0392B',    # 深红色
        'European Stocks': '#2980B9',   # 深蓝色
        'My Holdings': '#27AE60',       # 深绿色
        'Research': '#D35400',          # 烧橤色
        'Comparison': '#7F8C8D',        # 深灰色
    }
    
    # 检查是否是常见的自定义category
    if category in custom_colors:
        return custom_colors[category]
    
    # 为其他自定义category生成一致的颜色
    # 使用hash确保同一名称总是得到相同颜色
    hash_value = int(hashlib.md5(category.encode()).hexdigest()[:6], 16)
    
    # 从备选颜色列表中选择（避免与预定义颜色太接近）
    alternative_colors = [
        '#E8A317', '#D4AC0D', '#BA4A00', '#7D3C98',
        '#1F618D', '#148F77', '#117864', '#B03A2E',
        '#6C3483', '#1A5276', '#17A589', '#D68910'
    ]
    
    color_index = hash_value % len(alternative_colors)
    return alternative_colors[color_index]


# 初始化数据库和服务
@st.cache_resource
def get_database():
    """获取数据库实例"""
    return BRIDatabase('data/bri_data.db')


@st.cache_resource
def get_update_service():
    """获取更新服务实例"""
    return BRIUpdateService('data/bri_data.db')


@st.cache_resource
def get_custom_ticker_service():
    """获取自定义Ticker服务实例"""
    return CustomTickerService('data/bri_data.db')


def load_bri_data_from_db():
    """从数据库加载BRI数据"""
    db = get_database()
    assets = db.get_all_assets()
    
    all_data = {}
    for asset in assets:
        try:
            df = db.get_bri_results(asset)
            if not df.empty:
                # 确保Date列格式正确
                if df.index.name == 'Date':
                    df = df.reset_index()
                elif 'Date' not in df.columns:
                    df['Date'] = df.index
                    df = df.reset_index(drop=True)
                
                # 确保Date列是datetime格式
                df['Date'] = pd.to_datetime(df['Date'])
                df = df.sort_values('Date')
                
                all_data[asset] = df
        except Exception as e:
            st.warning(f"Error loading {asset}: {e}")
            import traceback
            st.error(traceback.format_exc())
    
    return all_data


def get_latest_metrics(all_data):
    """Calculate latest metrics for all assets"""
    metrics = []
    
    for asset_name, df in all_data.items():
        if asset_name not in ASSET_INFO:
            st.sidebar.warning(f"Skipping {asset_name}: Not in ASSET_INFO")
            continue
            
        if len(df) < 2:
            st.sidebar.warning(f"Skipping {asset_name}: Only {len(df)} rows")
            continue
        
        # Debug: show columns
        st.sidebar.text(f"{asset_name} columns: {df.columns.tolist()[:5]}")
        
        # Find the latest row with valid BRI data
        valid_data = df[df['composite_bri'].notna()].copy()
        if len(valid_data) == 0:
            st.sidebar.warning(f"Skipping {asset_name}: No valid composite_bri")
            continue
        
        # Get latest valid data
        latest = valid_data.iloc[-1]
        
        # Calculate metrics
        bri = float(latest['composite_bri']) if pd.notna(latest['composite_bri']) else 0.0
        price = float(latest['price']) if pd.notna(latest['price']) else 0.0
        daily_return = float(latest['returns']) if pd.notna(latest['returns']) else 0.0
        
        # Get sub-indicators
        short_bri = float(latest['short_indicator']) if pd.notna(latest['short_indicator']) else 0.0
        mid_bri = float(latest['mid_indicator']) if pd.notna(latest['mid_indicator']) else 0.0
        long_bri = float(latest['long_indicator']) if pd.notna(latest['long_indicator']) else 0.0
        
        # Skip if all indicators are 0 (but not 0.5 which is a valid value)
        # Relaxed condition to show more data
        if bri == 0.0 and short_bri == 0.0 and mid_bri == 0.0 and long_bri == 0.0:
            st.sidebar.warning(f"Skipping {asset_name}: All indicators are 0")
            continue
        
        # Get date - handle both index and column
        date_val = latest['Date'] if 'Date' in latest else (latest.name if hasattr(latest, 'name') else None)
        
        metrics.append({
            'asset': asset_name,
            'name_en': ASSET_INFO[asset_name]['name_en'],
            'name_cn': ASSET_INFO[asset_name]['name_cn'],
            'category': ASSET_INFO[asset_name]['category'],
            'bri': bri,
            'short_bri': short_bri,
            'mid_bri': mid_bri,
            'long_bri': long_bri,
            'price': price,
            'daily_return': daily_return,
            'date': date_val
        })
    
    return pd.DataFrame(metrics)


def create_bubble_chart(metrics_df):
    """Create interactive bubble chart"""
    if metrics_df.empty:
        st.warning("No data available for bubble chart")
        return None
    
    # Prepare data for bubble chart
    # 优化bubble大小：最小40，最大90，确保文字清晰可见
    # 公式：size = bri * 50 + 40
    # BRI=0时，size=40；BRI=1时，size=90
    metrics_df['size'] = metrics_df['bri'] * 50 + 40
    metrics_df['label'] = metrics_df.apply(
        lambda row: f"{row['name_en']}<br>{row['name_cn']}", axis=1
    )
    metrics_df['hover_text'] = metrics_df.apply(
        lambda row: f"<b>{row['name_en']} / {row['name_cn']}</b><br>" +
                   f"BRI: {row['bri']:.2%}<br>" +
                   f"Daily Return: {row['daily_return']:.2%}<br>" +
                   f"Price: {row['price']:.2f}",
        axis=1
    )
    
    # Create scatter plot with category colors
    fig = go.Figure()
    
    # Track which categories we've added to legend
    categories_added = set()
    
    for _, row in metrics_df.iterrows():
        # Get category color
        category_color = get_category_color(row['category'])
        
        # Only show legend for first occurrence of each category
        show_legend = row['category'] not in categories_added
        if show_legend:
            categories_added.add(row['category'])
        
        # 根据bubble大小动态调整字体大小
        # bubble size范围：40-90
        # 字体大小范围：9-13
        font_size = int(8 + (row['size'] - 40) / 50 * 5)  # 线性映射到9-13
        font_size = max(9, min(13, font_size))  # 确保在范围内
        
        fig.add_trace(go.Scatter(
            x=[row['bri']],
            y=[row['daily_return']],
            mode='markers+text',
            marker=dict(
                size=row['size'],
                color=category_color,
                opacity=0.7,
                line=dict(width=2, color='white')
            ),
            text=row['label'],
            textposition='middle center',
            textfont=dict(size=font_size, color='white', family='Arial Black'),
            hovertext=row['hover_text'],
            hoverinfo='text',
            name=row['category'],  # Show category in legend
            legendgroup=row['category'],  # Group by category
            showlegend=show_legend
        ))
    
    fig.update_layout(
        title={
            'text': 'BRI Bubble Risk Monitor',
            'font': {'size': 24, 'color': '#2c3e50', 'family': 'Arial Black'},
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title='Composite BRI',
        yaxis_title='Daily Return',
        xaxis=dict(tickformat='.0%', gridcolor='lightgray', showgrid=True),
        yaxis=dict(tickformat='.2%', gridcolor='lightgray', showgrid=True),
        plot_bgcolor='white',
        hovermode='closest',
        height=800,  # 增加高度从700到800，给bubble更多空间
        legend=dict(
            title="Asset Category",
            orientation="v",
            yanchor="top",
            y=0.98,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255, 255, 255, 0.9)",
            bordercolor="#2c3e50",
            borderwidth=1
        )
    )
    
    return fig


def create_indicator_plots(asset_data, asset_name):
    """Create BRI indicator plots"""
    if asset_data.empty:
        st.warning(f"No data available for {asset_name}")
        return
    
    # Filter out rows with missing data
    plot_data = asset_data.dropna(subset=['composite_bri', 'short_indicator', 'mid_indicator', 'long_indicator'])
    
    if plot_data.empty:
        st.warning(f"No valid BRI data for {asset_name}")
        return
    
    # 确保使用Date列而不是index
    date_col = plot_data['Date'] if 'Date' in plot_data.columns else plot_data.index
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Short-term BRI
        fig_short = go.Figure()
        fig_short.add_trace(go.Scatter(
            x=date_col,
            y=plot_data['short_indicator'],
            mode='lines',
            line=dict(color='#3498db', width=2),
            fill='tozeroy',
            fillcolor='rgba(52, 152, 219, 0.2)'
        ))
        fig_short.add_hline(y=0.7, line_dash="dash", line_color="red")
        fig_short.add_hline(y=0.5, line_dash="dash", line_color="orange")
        fig_short.update_layout(
            title='Short-term BRI (3-month)',
            yaxis=dict(tickformat='.0%'),
            height=300
        )
        st.plotly_chart(fig_short, use_container_width=True)
        
        # Mid-term BRI
        fig_mid = go.Figure()
        fig_mid.add_trace(go.Scatter(
            x=date_col,
            y=plot_data['mid_indicator'],
            mode='lines',
            line=dict(color='#9b59b6', width=2),
            fill='tozeroy',
            fillcolor='rgba(155, 89, 182, 0.2)'
        ))
        fig_mid.add_hline(y=0.7, line_dash="dash", line_color="red")
        fig_mid.add_hline(y=0.5, line_dash="dash", line_color="orange")
        fig_mid.update_layout(
            title='Mid-term BRI (6-month)',
            yaxis=dict(tickformat='.0%'),
            height=300
        )
        st.plotly_chart(fig_mid, use_container_width=True)
    
    with col2:
        # Long-term BRI
        fig_long = go.Figure()
        fig_long.add_trace(go.Scatter(
            x=date_col,
            y=plot_data['long_indicator'],
            mode='lines',
            line=dict(color='#e74c3c', width=2),
            fill='tozeroy',
            fillcolor='rgba(231, 76, 60, 0.2)'
        ))
        fig_long.add_hline(y=0.7, line_dash="dash", line_color="red")
        fig_long.add_hline(y=0.5, line_dash="dash", line_color="orange")
        fig_long.update_layout(
            title='Long-term BRI (1-year)',
            yaxis=dict(tickformat='.0%'),
            height=300
        )
        st.plotly_chart(fig_long, use_container_width=True)
        
        # Composite BRI
        fig_composite = go.Figure()
        fig_composite.add_trace(go.Scatter(
            x=date_col,
            y=plot_data['composite_bri'],
            mode='lines',
            line=dict(color='#16a085', width=3),
            fill='tozeroy',
            fillcolor='rgba(22, 160, 133, 0.2)'
        ))
        fig_composite.add_hline(y=0.7, line_dash="dash", line_color="red")
        fig_composite.add_hline(y=0.5, line_dash="dash", line_color="orange")
        fig_composite.update_layout(
            title='Composite BRI (Average)',
            yaxis=dict(tickformat='.0%'),
            height=300
        )
        st.plotly_chart(fig_composite, use_container_width=True)


# ==================== 页面定义 ====================

def dashboard_page():
    """Dashboard页面 - 显示BRI数据"""
    st.title("📊 BRI Bubble Risk Indicator Dashboard")
    st.markdown("**Real-time bubble risk monitoring across global assets**")
    st.markdown("---")
    
    # Load data
    with st.spinner("Loading BRI data from database..."):
        all_data = load_bri_data_from_db()
    
    if not all_data:
        st.error("No BRI data found. Please update data first.")
        st.info("Go to '🔄 Data Update' page to fetch and calculate BRI data.")
        
        # Show database status
        db = get_database()
        metadata = db.get_metadata()
        if not metadata.empty:
            st.warning("Database has metadata but no BRI results found:")
            st.dataframe(metadata)
        return
    
    # Get latest metrics
    metrics_df_full = get_latest_metrics(all_data)
    
    if metrics_df_full.empty:
        st.error("No valid metrics data available")
        return
    
    # ===== Controls Section (moved from sidebar) =====
    st.header("🎛️ Controls")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Category filter with "Common Assets" as default
        categories = ['Common Assets', 'All'] + sorted(metrics_df_full['category'].unique().tolist())
        selected_category = st.selectbox(
            "Filter by Category", 
            categories,
            index=0,  # Default to "Common Assets"
            help="Common Assets includes: Gold, Oil, Copper, major indices, USD/EUR/JPY, and credit spreads"
        )
    
    with col2:
        lookback_days = st.slider("Lookback Period (days)", 30, 365*5, 365, 30)
    
    # Apply category filter
    if selected_category == 'Common Assets':
        metrics_df = metrics_df_full[metrics_df_full['asset'].isin(COMMON_ASSETS)]
    elif selected_category != 'All':
        metrics_df = metrics_df_full[metrics_df_full['category'] == selected_category]
    else:
        metrics_df = metrics_df_full
    
    # ===== Summary Statistics (moved from sidebar) =====
    st.markdown("---")
    st.header("📈 Summary Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Assets", len(metrics_df))
    col2.metric("Avg BRI", f"{metrics_df['bri'].mean():.2%}")
    col3.metric("High Risk (>70%)", len(metrics_df[metrics_df['bri'] > 0.7]))
    col4.metric("Elevated Risk (50-70%)", len(metrics_df[(metrics_df['bri'] >= 0.5) & (metrics_df['bri'] <= 0.7)]))
    
    st.markdown("---")
    
    # Bubble chart
    st.header("🔮 BRI Heat Map")
    bubble_fig = create_bubble_chart(metrics_df)
    if bubble_fig:
        st.plotly_chart(bubble_fig, use_container_width=True)
    
    # Asset selection
    st.markdown("---")
    st.header("📊 Detailed Asset Analysis")
    
    metrics_df_sorted = metrics_df.sort_values('bri', ascending=False)
    
    cols = st.columns(5)
    for idx, (_, row) in enumerate(metrics_df_sorted.iterrows()):
        col = cols[idx % 5]
        with col:
            risk_emoji = "🔴" if row['bri'] > 0.7 else "🟡" if row['bri'] > 0.5 else "🟢"
            if st.button(
                f"{risk_emoji} {row['name_en']}\n{row['name_cn']}\n{row['bri']:.1%}",
                key=f"btn_{row['asset']}",
                use_container_width=True
            ):
                st.session_state['selected_asset'] = row['asset']
    
    # Display selected asset details
    if 'selected_asset' in st.session_state:
        selected_asset = st.session_state['selected_asset']
        
        if selected_asset in all_data:
            st.markdown("---")
            asset_info = ASSET_INFO.get(selected_asset, {})
            st.header(f"📈 {asset_info.get('name_en', selected_asset)} / {asset_info.get('name_cn', selected_asset)}")
            
            asset_data = all_data[selected_asset].copy()
            
            # 使用Date列而不是index
            if 'Date' in asset_data.columns:
                max_date = asset_data['Date'].max()
                cutoff_date = max_date - timedelta(days=lookback_days)
                asset_data_filtered = asset_data[asset_data['Date'] >= cutoff_date]
            else:
                cutoff_date = asset_data.index.max() - timedelta(days=lookback_days)
                asset_data_filtered = asset_data[asset_data.index >= cutoff_date]
            
            # Current metrics
            current = metrics_df[metrics_df['asset'] == selected_asset].iloc[0]
            
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Composite BRI", f"{current['bri']:.2%}")
            col2.metric("Short-term", f"{current['short_bri']:.2%}")
            col3.metric("Mid-term", f"{current['mid_bri']:.2%}")
            col4.metric("Long-term", f"{current['long_bri']:.2%}")
            col5.metric("Daily Return", f"{current['daily_return']:.2%}")
            
            create_indicator_plots(asset_data_filtered, selected_asset)


def update_page():
    """Data Update页面 - 更新数据"""
    st.title("🔄 BRI Data Update Center")
    st.markdown("**Fetch latest data and calculate BRI indicators**")
    st.markdown("---")
    
    update_service = get_update_service()
    
    # 1. Quick check
    st.header("1️⃣ Quick Check - All Assets")
    
    if st.button("🔍 Check for Updates", type="primary"):
        with st.spinner("Checking all assets..."):
            check_results = []
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for idx, (asset_key, asset_info) in enumerate(BRI_ASSETS.items()):
                progress = (idx + 1) / len(BRI_ASSETS)
                progress_bar.progress(progress)
                status_text.text(f"Checking {asset_key}... ({idx+1}/{len(BRI_ASSETS)})")
                
                result = update_service.check_for_updates(
                    asset_key,
                    asset_info['yahoo_ticker']
                )
                result['asset'] = asset_key
                check_results.append(result)
            
            status_text.text("✅ Check complete!")
            
            # Display results
            needs_update = [r for r in check_results if r.get('has_new_data')]
            up_to_date = [r for r in check_results if not r.get('has_new_data')]
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Assets", len(check_results))
            col2.metric("Needs Update", len(needs_update), delta=len(needs_update))
            col3.metric("Up to Date", len(up_to_date))
            
            if needs_update:
                st.success(f"Found {len(needs_update)} assets with new data!")
                df_needs_update = pd.DataFrame(needs_update)
                st.dataframe(df_needs_update[[
                    'asset', 'last_db_date', 'latest_available_date', 'new_rows'
                ]], use_container_width=True)
                
                st.session_state['assets_to_update'] = needs_update
            else:
                st.info("All assets are up to date! ✅")
    
    # 2. Execute update
    st.header("2️⃣ Update Assets")
    
    if 'assets_to_update' in st.session_state:
        assets_to_update = st.session_state['assets_to_update']
        
        st.write(f"Ready to update {len(assets_to_update)} assets:")
        selected_assets = st.multiselect(
            "Select assets to update:",
            [a['asset'] for a in assets_to_update],
            default=[a['asset'] for a in assets_to_update]
        )
        
        if st.button("▶️ Start Update", type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            results_container = st.container()
            
            update_results = []
            
            for idx, asset_name in enumerate(selected_assets):
                progress = (idx + 1) / len(selected_assets)
                progress_bar.progress(progress)
                status_text.text(f"Updating {asset_name}... ({idx+1}/{len(selected_assets)})")
                
                asset_info = BRI_ASSETS[asset_name]
                result = update_service.update_asset(
                    asset_name,
                    asset_info['yahoo_ticker']
                )
                update_results.append(result)
                
                with results_container:
                    if result['success']:
                        st.success(f"✅ {asset_name}: Added {result['new_bri_rows']} new BRI rows")
                    else:
                        st.error(f"❌ {asset_name}: {result.get('error', 'Unknown error')}")
            
            status_text.text("✅ Update complete!")
            
            # Clear list
            del st.session_state['assets_to_update']
            
            # Force reload data
            st.cache_data.clear()
    
    # 3. Manual update
    st.header("3️⃣ Manual Update")
    
    selected_asset = st.selectbox(
        "Select Asset:",
        list(BRI_ASSETS.keys())
    )
    
    force_full = st.checkbox("Force full recalculation (重新计算所有历史数据)")
    
    if st.button("🔄 Update Selected Asset"):
        with st.spinner(f"Updating {selected_asset}..."):
            asset_info = BRI_ASSETS[selected_asset]
            result = update_service.update_asset(
                selected_asset,
                asset_info['yahoo_ticker'],
                force_full=force_full
            )
            
            if result['success']:
                st.success(f"✅ Successfully updated {selected_asset}!")
                st.json(result)
            else:
                st.error(f"❌ Failed to update {selected_asset}")
                st.error(result.get('error'))


def custom_ticker_page():
    """Custom Ticker Analysis页面"""
    st.title("🔍 Custom Ticker Analysis")
    st.markdown("**Analyze any Yahoo Finance ticker with BRI indicators**")
    st.markdown("---")
    
    service = get_custom_ticker_service()
    
    # 说明
    with st.expander("ℹ️ How to use", expanded=False):
        st.markdown("""
        ### 使用说明 / Instructions
        
        1. **输入Ticker**: 输入任何Yahoo Finance的ticker symbol（如：TSLA, AAPL, ^GSPC）
        2. **检查状态**: 点击"Check Ticker"查看ticker是否已在数据库中
        3. **分析设置**: 
           - 选择历史数据年限（3-10年）
           - 选择是否保存到数据库
           - 可自定义资产名称和类别
        4. **执行分析**: 点击"Analyze Ticker"开始分析
        5. **查看结果**: 查看BRI指标、图表和风险评估
        
        ### Ticker示例 / Examples
        - **股票 Stocks**: TSLA, AAPL, MSFT, GOOGL
        - **指数 Indices**: ^GSPC (S&P 500), ^IXIC (NASDAQ), ^FTSE (FTSE 100)
        - **商品 Commodities**: GC=F (Gold), CL=F (Crude Oil)
        - **加密货币 Crypto**: BTC-USD, ETH-USD
        - **ETF**: SPY, QQQ, IWM
        """)
    
    st.markdown("---")
    
    # 输入区域
    col1, col2 = st.columns([2, 1])
    
    with col1:
        ticker_input = st.text_input(
            "🎯 Enter Yahoo Finance Ticker",
            placeholder="e.g., TSLA, ^GSPC, BTC-USD",
            help="Enter any valid Yahoo Finance ticker symbol"
        ).strip().upper()
    
    with col2:
        if st.button("🔍 Check Ticker", use_container_width=True):
            if ticker_input:
                with st.spinner("Checking ticker..."):
                    check_result = service.check_ticker_exists(ticker_input)
                    
                    if check_result['exists']:
                        st.success(f"✅ Ticker already in database as '{check_result['asset_name']}'")
                        st.info(f"Last updated: {check_result['last_date']}, {check_result['rows']} rows")
                    else:
                        is_valid, message, info = service.validate_ticker(ticker_input)
                        if is_valid:
                            st.info(f"✅ Valid ticker: {info['name']}")
                            st.write(f"Type: {info['type']}, Exchange: {info['exchange']}")
                        else:
                            st.error(f"❌ {message}")
            else:
                st.warning("Please enter a ticker symbol")
    
    if not ticker_input:
        st.info("👆 Enter a ticker symbol to get started")
        return
    
    st.markdown("---")
    
    # 分析设置
    st.header("⚙️ Analysis Settings")
    
    # 基本设置
    years_back = st.slider(
        "📅 Years of Historical Data",
        min_value=3,
        max_value=10,
        value=5,
        help="How many years of historical data to fetch (more data = more accurate BRI)"
    )
    
    st.markdown("---")
    
    # 数据库保存选项（可选）
    save_to_db = st.checkbox(
        "💾 Save to Database (Optional)",
        value=False,
        help="Save this ticker to database for long-term tracking and Dashboard display"
    )
    
    # 只有选择保存时才显示category和自定义名称
    if save_to_db:
        st.info("ℹ️ **Database Settings** - These settings only matter when saving to database")
        
        col1, col2 = st.columns(2)
        
        with col1:
            custom_name = st.text_input(
                "Custom Name",
                value=ticker_input.replace('^', '').replace('-', '_'),
                help="Custom asset name for database storage (will appear in Dashboard)"
            )
        
        with col2:
            category_option = st.selectbox(
                "Category",
                ['Custom', 'Global Equity', 'US Sectors', 'Commodity', 'Currency', 'Crypto', 'Credit', '➕ Create New...'],
                help="Category for filtering and color coding in Dashboard bubble chart"
            )
            
            # 如果选择创建新category
            if category_option == '➕ Create New...':
                category = st.text_input(
                    "Enter New Category Name",
                    placeholder="e.g., My Portfolio, Watch List, Tech Stocks",
                    help="Create your own category name"
                ).strip()
                if not category:
                    category = 'Custom'  # 默认值
                    st.warning("⚠️ Please enter a category name, using 'Custom' as default")
            else:
                category = category_option
    else:
        # 如果不保存，使用默认值
        custom_name = ticker_input.replace('^', '').replace('-', '_')
        category = 'Custom'
        st.info("ℹ️ **Quick Analysis Mode** - Results will be displayed but not saved to database")
    
    st.markdown("---")
    
    # 分析按钮
    if st.button("🚀 Analyze Ticker", type="primary", use_container_width=True):
        with st.spinner(f"Analyzing {ticker_input}..."):
            # 执行分析
            result = service.analyze_custom_ticker(
                ticker=ticker_input,
                custom_name=custom_name,
                category=category,
                years_back=years_back,
                save_to_db=save_to_db
            )
            
            if result['success']:
                st.success("✅ Analysis Complete!")
                
                # 显示ticker信息
                st.markdown("---")
                st.header("📊 Ticker Information")
                
                info_cols = st.columns(4)
                info_cols[0].metric("Name", result['ticker_info']['name'][:20])
                info_cols[1].metric("Type", result['ticker_info']['type'])
                info_cols[2].metric("Exchange", result['ticker_info']['exchange'])
                info_cols[3].metric("Currency", result['ticker_info']['currency'])
                
                # 数据统计
                st.markdown("---")
                st.header("📈 Data Statistics")
                
                data_cols = st.columns(3)
                data_cols[0].metric("Total Rows", result['data_info']['total_rows'])
                data_cols[1].metric("Date Range", result['data_info']['date_range'])
                data_cols[2].metric("Years Coverage", f"{result['data_info']['years_coverage']:.1f}")
                
                # 最新BRI指标
                st.markdown("---")
                st.header("🎯 Latest BRI Metrics")
                
                metrics = result['latest_metrics']
                metric_cols = st.columns(5)
                
                metric_cols[0].metric(
                    "Price",
                    f"${metrics['price']:.2f}",
                    f"{metrics['returns']:.2%}"
                )
                metric_cols[1].metric(
                    "Composite BRI",
                    f"{metrics['composite_bri']:.1%}",
                    delta_color="inverse"
                )
                metric_cols[2].metric(
                    "Short-term",
                    f"{metrics['short_indicator']:.1%}" if metrics['short_indicator'] else "N/A"
                )
                metric_cols[3].metric(
                    "Mid-term",
                    f"{metrics['mid_indicator']:.1%}" if metrics['mid_indicator'] else "N/A"
                )
                metric_cols[4].metric(
                    "Long-term",
                    f"{metrics['long_indicator']:.1%}" if metrics['long_indicator'] else "N/A"
                )
                
                # 风险评估
                bri_value = metrics['composite_bri']
                if bri_value > 0.7:
                    st.error(f"🔴 HIGH RISK: BRI = {bri_value:.1%} - Bubble risk is elevated!")
                elif bri_value > 0.5:
                    st.warning(f"🟡 MODERATE RISK: BRI = {bri_value:.1%} - Monitor closely")
                else:
                    st.success(f"🟢 LOW RISK: BRI = {bri_value:.1%} - Bubble risk is low")
                
                # BRI图表
                st.markdown("---")
                st.header("📉 BRI Indicators Over Time")
                
                bri_df = result['bri_results']
                create_indicator_plots(bri_df, custom_name or ticker_input)
                
                # 保存状态
                if result['saved_to_db']:
                    st.success(f"💾 Analysis saved to database as '{result['asset_name']}'")
                    st.info("You can now view this asset in the Dashboard!")
                
                # 下载选项
                st.markdown("---")
                st.header("💾 Download Results")
                
                csv = bri_df.to_csv(index=True)
                st.download_button(
                    label="📥 Download BRI Data (CSV)",
                    data=csv,
                    file_name=f"{custom_name or ticker_input}_BRI_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
                
            else:
                st.error(f"❌ Analysis Failed: {result['error']}")
                if 'traceback' in result:
                    with st.expander("Show Error Details"):
                        st.code(result['traceback'])


def history_page():
    """Update History页面 - 更新历史"""
    st.title("📝 Update History Log")
    st.markdown("**View all data update activities**")
    st.markdown("---")
    
    db = get_database()
    history = db.get_update_history(limit=100)
    
    if not history.empty:
        # Statistics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Updates", len(history))
        col2.metric("Success", len(history[history['status'] == 'success']))
        col3.metric("Failed", len(history[history['status'] == 'error']))
        col4.metric("Last Update", history['created_at'].max().strftime('%Y-%m-%d %H:%M'))
        
        # Filter
        selected_asset = st.selectbox(
            "Filter by Asset:",
            ['All'] + history['asset_name'].unique().tolist()
        )
        
        if selected_asset != 'All':
            history = history[history['asset_name'] == selected_asset]
        
        # Display table
        st.dataframe(
            history[['created_at', 'asset_name', 'update_type', 'status', 
                    'rows_affected', 'message']],
            use_container_width=True
        )
    else:
        st.info("No update history yet")


# ==================== 主应用 ====================

def main():
    """Main application"""
    
    # Sidebar navigation
    st.sidebar.title("📊 BRI Application")
    page = st.sidebar.radio(
        "选择页面 / Select Page",
        ["📊 Dashboard", "🔄 Data Update", "🔍 Custom Ticker", "📝 Update History"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 系统信息 / System Info")
    
    db = get_database()
    metadata = db.get_metadata()
    
    if not metadata.empty:
        st.sidebar.metric("Assets in Database", len(metadata))
        latest_update = metadata['updated_at'].max() if 'updated_at' in metadata.columns else 'N/A'
        st.sidebar.text(f"Last Update:\n{latest_update}")
    else:
        st.sidebar.info("No data in database yet")
    
    # Route to pages
    if page == "📊 Dashboard":
        dashboard_page()
    elif page == "🔄 Data Update":
        update_page()
    elif page == "🔍 Custom Ticker":
        custom_ticker_page()
    elif page == "📝 Update History":
        history_page()


if __name__ == "__main__":
    main()

