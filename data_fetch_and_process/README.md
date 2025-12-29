# BRI Data Fetch and Process

This folder contains scripts and raw data for the **Bubble Risk Indicator (BRI)** project, replicating Bank of America's framework for diagnosing market bubbles.

## 📁 Folder Structure

```
data_fetch_and_process/
├── bri_data_fetcher.py          # Main data fetching script
├── ASSET_REFERENCE.md           # Detailed asset ticker mappings and notes
├── NEW_ASSETS_SUMMARY.md        # Summary of newly added assets (2025-12-12)
├── README.md                    # This file
└── raw_data/                    # Downloaded historical data
    ├── [Equity Indices] DOW_JONES, NASDAQ_100, NIKKEI_225, HSCEI, DAX, CSI300, CSI500, HSTECH
    ├── [U.S. Sectors] XLF, XLY, XLC, XLI, XLK, XLV, XLE, IXE, BIOTECH
    ├── [Commodities] GOLD, CRUDE_OIL, COPPER
    ├── [Crypto] BITCOIN
    ├── [Tech Giants] MAG7
    └── fetch_summary_*.txt      # Summary report
```

## 📊 Data Successfully Fetched

### ✅ All 22 Assets Retrieved

#### 🌍 Global Equity Indices (8 assets)

| Asset | Original Ticker | Yahoo Ticker | Data Points | Coverage | Start Date |
|-------|----------------|--------------|-------------|----------|------------|
| **Dow Jones** | INDU | ^DJI | 8,547 | 33.9 years | 1992-01-02 |
| **NASDAQ-100** | NDX | ^NDX | 10,129 | 40.2 years | 1985-10-01 |
| **Nikkei 225** | NKY | ^N225 | 14,983 | **60.9 years** | **1965-01-05** |
| **HSCEI** | HSCEI | ^HSCE | 7,996 | 32.4 years | 1993-07-15 |
| **DAX** | DAX | ^GDAXI | 9,599 | 37.9 years | 1987-12-30 |
| **CSI300** | CSI300 | 000300.SS | 1,155 | 4.8 years | 2021-03-11 |
| **CSI500** | CSI500 | ASHS | 2,909 | 11.6 years | 2014-05-21 |
| **Hang Seng Tech** | HSTECH | 3033.HK | 1,301 | 5.3 years | 2020-08-27 |

#### 🏢 U.S. Sector Indices (9 assets)

| Asset | Ticker | Data Points | Coverage | Start Date |
|-------|--------|-------------|----------|------------|
| **Financials (XLF)** | XLF | 6,785 | 27.0 years | 1998-12-22 |
| **Consumer Discretionary (XLY)** | XLY | 6,785 | 27.0 years | 1998-12-22 |
| **Communication Services (XLC)** | XLC | 1,882 | 7.5 years | 2018-06-19 |
| **Industrials (XLI)** | XLI | 6,785 | 27.0 years | 1998-12-22 |
| **Technology (XLK)** | XLK | 6,785 | 27.0 years | 1998-12-22 |
| **Healthcare (XLV)** | XLV | 6,785 | 27.0 years | 1998-12-22 |
| **Energy (XLE)** | XLE | 6,785 | 27.0 years | 1998-12-22 |
| **Energy Index (IXE)** | ^IXE → XLE | 6,785 | 27.0 years | 1998-12-22 |
| **Biotech (IBB)** | IBB | 6,246 | 24.8 years | 2001-02-12 |

#### 🔨 Commodities (3 assets)

| Asset | Original Ticker | Yahoo Ticker | Data Points | Coverage | Start Date |
|-------|----------------|--------------|-------------|----------|------------|
| **Gold** | XAU | GC=F | 6,345 | 25.3 years | 2000-08-30 |
| **Crude Oil** | CO1 | CL=F | 6,354 | 25.3 years | 2000-08-23 |
| **Copper** | HG | HG=F | 6,350 | 25.3 years | 2000-08-30 |

#### 💻 Crypto & Tech Giants (2 assets)

| Asset | Ticker | Data Points | Coverage | Start Date |
|-------|--------|-------------|----------|------------|
| **Bitcoin** | BTC-USD | 4,104 | 11.2 years | 2014-09-17 |
| **Magnificent 7** | MAGS | 672 | 2.7 years | 2023-04-11 |

### 🏆 Longest History
**Nikkei 225** provides the most extensive dataset with **60.9 years** of data going back to **1965**!

### 📝 Key Updates (2025-12-12)
- ➕ Added **9 U.S. sector indices** for cross-sector bubble analysis
- ➕ Added **4 China/Hong Kong indices** (DAX, CSI300, CSI500, HSTECH)
  - Note: CSI500 uses ASHS ETF (Xtrackers Harvest CSI 500 Small Cap)
- ➕ Added **Copper futures** as industrial demand indicator
- ➕ Added **Magnificent 7 ETF** for tech concentration risk
- 📊 Total assets expanded from 8 to **22**

For detailed information on new assets, see: **[NEW_ASSETS_SUMMARY.md](NEW_ASSETS_SUMMARY.md)**

## 🚀 Usage

### To Fetch Fresh Data

```bash
cd data_fetch_and_process
python bri_data_fetcher.py
```

This will:
1. Download latest data for all **22 assets**
2. Save CSV files with timestamps in `raw_data/`
3. Generate a summary report
4. Handle alternative tickers automatically (e.g., IXE → XLE fallback)

### CSV Data Format

Each CSV file contains:
- **Date** (index): Trading date
- **Open**: Opening price
- **High**: Daily high
- **Low**: Daily low
- **Close**: Closing price
- **Volume**: Trading volume
- **Dividends**: Dividend payments (if any)
- **Stock Splits**: Stock splits (if any)

## 📈 BRI Framework Overview

The Bubble Risk Indicator uses **four statistical moments** to analyze market bubbles:

### 1. Mean (μ)
- **Measures**: Average returns
- **BRI Use**: Identify periods of exceptional returns

### 2. Variance (σ²)
- **Measures**: Return volatility
- **BRI Use**: Detect increased market instability

### 3. Skewness
- **Measures**: Asymmetry in return distribution
- **BRI Use**: Identify one-sided price movements (bubble formations)
- **Positive skew**: More extreme upside moves
- **Negative skew**: More extreme downside moves (crash risk)

### 4. Kurtosis
- **Measures**: "Fat tails" - extreme events
- **BRI Use**: Detect probability of extreme price movements
- **High kurtosis**: More outliers, crash risk

## 🔧 Next Steps for BRI Analysis

### Step 1: Data Preprocessing
```python
import pandas as pd

# Load data
df = pd.read_csv('raw_data/DOW_JONES_*.csv', index_col=0, parse_dates=True)

# Calculate returns
df['returns'] = df['Close'].pct_change()
df['log_returns'] = np.log(df['Close'] / df['Close'].shift(1))

# Handle missing values
df = df.fillna(method='ffill')
```

### Step 2: Calculate Rolling Statistics (Window: e.g., 252 days = 1 year)
```python
window = 252

# Mean
df['rolling_mean'] = df['returns'].rolling(window).mean()

# Variance (Volatility)
df['rolling_std'] = df['returns'].rolling(window).std()

# Skewness
df['rolling_skew'] = df['returns'].rolling(window).skew()

# Kurtosis
df['rolling_kurt'] = df['returns'].rolling(window).kurt()
```

### Step 3: Normalize Indicators
```python
from scipy import stats

# Z-score normalization
df['mean_zscore'] = stats.zscore(df['rolling_mean'].dropna())
df['vol_zscore'] = stats.zscore(df['rolling_std'].dropna())
df['skew_zscore'] = stats.zscore(df['rolling_skew'].dropna())
df['kurt_zscore'] = stats.zscore(df['rolling_kurt'].dropna())
```

### Step 4: Construct BRI Composite Score
```python
# Equal-weighted BRI
df['BRI'] = (df['mean_zscore'] + 
             df['vol_zscore'] + 
             df['skew_zscore'] + 
             df['kurt_zscore']) / 4

# Or custom weights based on BofA methodology
weights = {'mean': 0.3, 'vol': 0.3, 'skew': 0.2, 'kurt': 0.2}
df['BRI_weighted'] = (weights['mean'] * df['mean_zscore'] +
                      weights['vol'] * df['vol_zscore'] +
                      weights['skew'] * df['skew_zscore'] +
                      weights['kurt'] * df['kurt_zscore'])
```

### Step 5: Identify Bubble Periods
```python
# Define bubble threshold (e.g., BRI > 2 standard deviations)
bubble_threshold = 2
df['bubble_signal'] = df['BRI'] > bubble_threshold

# Flag bubble periods
bubble_periods = df[df['bubble_signal'] == True]
```

## 📚 Recommended Libraries

```bash
pip install pandas numpy scipy matplotlib seaborn statsmodels
```

- **pandas**: Data manipulation
- **numpy**: Numerical calculations
- **scipy**: Statistical functions (skew, kurtosis)
- **matplotlib/seaborn**: Visualization
- **statsmodels**: Advanced time series analysis

## 🔍 Research References

1. **Bank of America**: "Year Ahead 2026: The Bubble Era"
2. **Statistical Moments**: Mean, Variance, Skewness, Kurtosis
3. **Bubble Detection Literature**: Kindleberger, Shiller, Brunnermeier

## 📊 Visualization Ideas

1. **Time Series**: Plot BRI composite score over time
2. **Heatmap**: Compare BRI across different assets
3. **Scatter Plots**: Skewness vs Kurtosis for different periods
4. **Distribution Analysis**: Return distributions during bubble vs normal periods
5. **Correlation Matrix**: Inter-asset bubble risk correlation

## ⚠️ Important Notes

1. **Survivorship Bias**: Some assets have limited history (Bitcoin: 2014+)
2. **Data Quality**: Futures contracts (Gold, Oil) may have gaps
3. **Time Zones**: Different exchanges, data timestamps vary
4. **Rebalancing**: Re-fetch data periodically for latest information
5. **Alternative Sources**: Consider Bloomberg if Yahoo Finance data is insufficient

## 🔄 Update Data

To refresh all datasets:
```bash
cd data_fetch_and_process
python bri_data_fetcher.py
```

New files will be created with timestamps. Old files are preserved for comparison.

## 📧 Questions?

Refer to `ASSET_REFERENCE.md` for detailed asset information and data source notes.

---

**Ready for BRI Analysis!** 🎯

