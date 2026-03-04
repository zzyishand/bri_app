# BRI Asset Reference Guide

This document maps the original asset tickers used in BRI analysis to Yahoo Finance tickers for data fetching.

## Asset Mappings

### Equity Indices

| Original Ticker | Asset Name | Yahoo Finance Ticker | Alternative | Earliest Data |
|----------------|------------|---------------------|-------------|---------------|
| INDU | Dow Jones Industrial Average | ^DJI | - | 1992 |
| NDX | NASDAQ-100 Index | ^NDX | - | 1985 |
| NKY | Nikkei 225 Index | ^N225 | - | 1965 |
| HSCEI | Hang Seng China Enterprises Index | ^HSCE | - | 1993 |
| DAX | DAX Performance Index (Germany) | ^GDAXI | - | 1987 |
| CSI300 | CSI 300 Index (China A-shares) | 000300.SS | - | 2021 |
| CSI500 | CSI 500 Index (China Small-Cap) | ASHS | - | 2014 |
| HSTECH | Hang Seng TECH Index | HSTECH.HK | 3033.HK ETF | 2020 |

### Commodities

| Original Ticker | Asset Name | Yahoo Finance Ticker | Alternative | Earliest Data |
|----------------|------------|---------------------|-------------|---------------|
| XAU | Gold | GC=F (Gold Futures) | GOLD (SPDR Gold ETF) | Varies |
| CO1 | Crude Oil | CL=F (Crude Oil Futures) | USO (US Oil Fund) | Varies |
| HG | Copper | HG=F (Copper Futures) | CPER (US Copper Index Fund) | Varies |

### Cryptocurrencies

| Original Ticker | Asset Name | Yahoo Finance Ticker | Earliest Data |
|----------------|------------|---------------------|---------------|
| XBTUSD | Bitcoin | BTC-USD | 2014 |

### Sector Indices (U.S.)

| Original Ticker | Asset Name | Yahoo Finance Ticker | Alternative | Earliest Data |
|----------------|------------|---------------------|-------------|---------------|
| XLF | Financial Select Sector SPDR | XLF | - | 1998 |
| XLY | Consumer Discretionary Select Sector SPDR | XLY | - | 1998 |
| XLC | Communication Services Select Sector SPDR | XLC | - | 2018 |
| XLI | Industrial Select Sector SPDR | XLI | - | 1998 |
| XLK | Technology Select Sector SPDR | XLK | - | 1998 |
| XLV | Health Care Select Sector SPDR | XLV | - | 1998 |
| XLE | Energy Select Sector SPDR | XLE | - | 1998 |
| IXE | S&P Global Energy Index | ^IXE | XLE | 1998 |
| IBB | iShares Biotechnology ETF | IBB | ^SPSIBI | 2001 |

### Thematic Indices

| Original Ticker | Asset Name | Yahoo Finance Ticker | Alternative | Earliest Data |
|----------------|------------|---------------------|-------------|---------------|
| MAG7 | Magnificent Seven (AAPL, MSFT, GOOGL, AMZN, NVDA, META, TSLA) | MAGS | XLK (Tech Sector) | 2023 |

## Data Columns

All fetched data includes the following columns:

- **Date**: Trading date (index)
- **Open**: Opening price
- **High**: Highest price of the day
- **Low**: Lowest price of the day
- **Close**: Closing price
- **Volume**: Trading volume
- **Dividends**: Dividend payments (if applicable)
- **Stock Splits**: Stock split information (if applicable)

## Notes on Data Availability

### Futures Contracts (GC=F, CL=F)
- **Continuous contracts** may have limited history on Yahoo Finance
- **Alternative ETFs** provide longer historical data:
  - GOLD: Data from 2004 (SPDR Gold Shares launch)
  - USO: Data from 2006 (US Oil Fund launch)
- Futures data may have gaps or missing data points

### Index Data
- Most major indices have data going back to the 1980s-1990s
- HSCEI (Hang Seng China Enterprises): Data from 1994
- Some indices may have data quality issues in early years

### Cryptocurrency (Bitcoin)
- Yahoo Finance BTC-USD data starts around **2014**
- Earlier Bitcoin price data may require alternative sources
- High volatility and 24/7 trading may affect daily OHLC calculations

### Biotech Index
- ^SPSIBI availability varies
- IBB (iShares Biotechnology ETF) as alternative from 2001

### U.S. Sector Indices (SPDR ETFs)
- **XLF, XLY, XLI, XLK, XLV, XLE**: Launched December 1998
- **XLC**: Launched June 2018 (newly created Communication Services sector)
- These ETFs track their respective S&P 500 sector indices
- Highly liquid with deep history for bubble analysis

### Global Indices
- **DAX (^GDAXI)**: German blue-chip index, data from 1987
- **CSI300 (000300.SS)**: China A-share index, data from 2021 (limited availability)
- **CSI500 (ASHS)**: Xtrackers Harvest CSI 500 China A-Shares Small Cap ETF, data from 2014
  - Tracks CSI 500 Index (China small-cap A-shares)
  - Note: CSI 1000 not available on Yahoo Finance
- **HSTECH (3033.HK)**: Hang Seng Tech Index ETF, data from 2020
- Note: Chinese indices direct access on Yahoo Finance is limited; ETFs used as proxies

### Magnificent 7 (MAG7)
- **MAGS ETF**: Launched 2023, tracks the "Magnificent Seven" mega-cap tech stocks
- Represents: Apple, Microsoft, Alphabet, Amazon, Nvidia, Meta, Tesla
- For historical analysis pre-2023, consider using XLK or individual stock data
- Alternative: Create custom index from individual stocks

### Copper Futures
- **HG=F**: COMEX Copper continuous contract
- Alternative: CPER (United States Copper Index Fund)
- Important industrial demand indicator and economic barometer

## Data Quality Considerations

1. **Missing Data**: Some assets may have gaps in historical data
2. **Corporate Actions**: Stock splits and dividends are recorded
3. **Timezone**: Timestamps reflect the exchange's timezone
4. **Futures Rollover**: Continuous futures contracts may show price jumps during rollovers
5. **Adjusted vs Unadjusted**: Yahoo Finance typically provides adjusted closing prices

## Usage for BRI Analysis

The Bubble Risk Indicator (BRI) framework analyzes market bubbles using statistical moments:

1. **Mean**: Average returns
2. **Variance**: Return volatility
3. **Skewness**: Asymmetry of return distribution
4. **Kurtosis**: "Fat tails" in return distribution

### Required Calculations from Raw Data

- **Returns**: `(Close_t - Close_(t-1)) / Close_(t-1)`
- **Log Returns**: `ln(Close_t / Close_(t-1))`
- **Volatility**: Rolling standard deviation of returns
- **Volume Patterns**: Abnormal volume spikes

## Recommended Data Processing Steps

1. **Load raw CSV data**
2. **Handle missing values** (forward fill, interpolation)
3. **Calculate returns** (simple and log returns)
4. **Compute rolling statistics** (mean, std, skewness, kurtosis)
5. **Normalize across assets** for cross-asset comparison
6. **Detect anomalies** and outliers

## Alternative Data Sources

If Yahoo Finance data is insufficient:

- **Bloomberg Terminal**: INDU, XAU, NKY, CO1 (original tickers)
- **Quandl/Nasdaq Data Link**: Commodity futures, Bitcoin
- **CoinGecko/CoinMarketCap API**: Cryptocurrency historical data
- **FRED (Federal Reserve)**: Economic indices
- **Alpha Vantage**: Extended historical data for some assets

## File Naming Convention

Fetched data files follow the pattern:
```
{ASSET_NAME}_{YYYYMMDD_HHMMSS}.csv
```

Example:
```
DOW_JONES_20251211_105030.csv
BITCOIN_20251211_105035.csv
```

## Contact & Updates

This mapping is based on Yahoo Finance availability as of December 2025.
Ticker symbols and data availability may change over time.
Always verify data quality before using in production analysis.

