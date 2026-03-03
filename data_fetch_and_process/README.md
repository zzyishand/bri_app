# BRI Data Fetching and Processing

This directory contains scripts for fetching and processing historical market data for the Bubble Risk Indicator (BRI) project.

## Overview

The BRI replicates Bank of America's bubble detection framework based on four statistical moments:
1. **Returns** (Mean) - Price appreciation
2. **Realized Volatility** (Variance) - Price fluctuation intensity  
3. **Momentum** (Skewness) - Distance from moving average
4. **Fragility** (Kurtosis) - Extreme movements (Vol - MAD)

## Historical Bubble Cases

Based on BofA Global Research (Jan-1926 to Feb-2021):

| Case | Period | Bloomberg Ticker | Yahoo Ticker | Description |
|------|--------|------------------|--------------|-------------|
| 1929 Crash | Oct-1926 to Sep-1929 | INDU | ^DJI | Dow Jones crash |
| Gold 1980 | Jul-1979 to Jan-1980 | XAU | GC=F | Gold bubble |
| Nikkei 1987 | Jan-1986 to Oct-1987 | NKY | ^N225 | Japanese asset bubble |
| Dot-com 2000 | Jan-1995 to Mar-2000 | NDX | ^IXIC | Nasdaq bubble |
| China 2007 | Jun-2006 to Oct-2007 | HSCEI | ^HSCE | H-Share bubble |
| Oil 2008 | Jan-2007 to Jul-2008 | CO1 | CL=F | Oil spike |
| Bitcoin 2017 | Jul-2017 to Dec-2017 | XBTUSD | BTC-USD | Crypto bubble |
| Biotech 2021 | May-2020 to Feb-2021 | SPSIBI | XBI | COVID biotech |

## Scripts

### 1. `data_availability_checker.py`
Checks Yahoo Finance for data availability for all bubble cases.

**Usage:**
```bash
python data_availability_checker.py
```

**Output:**
- Console report with detailed availability info
- `yahoo_finance_availability_summary.csv` - Summary table

### 2. Future Scripts (To be implemented)
- `fetch_yahoo_data.py` - Download data from Yahoo Finance
- `fetch_alternative_sources.py` - Fetch from FRED, Quandl, etc.
- `data_processor.py` - Clean and process raw data
- `calculate_bri_components.py` - Calculate the 4 BRI components

## Data Sources

### Primary: Yahoo Finance (yfinance)
- Free and accessible
- Good coverage for recent data (1990s onwards)
- Limited historical data for very old periods

### Alternative Sources (if needed):
1. **FRED** (Federal Reserve Economic Data) - Macro data
2. **Quandl/Nasdaq Data Link** - Financial datasets
3. **Alpha Vantage** - Stock data API
4. **Historical Providers** - Norgate, CSI Data (paid)

## Setup

1. Create and activate virtual environment:
```bash
cd /Users/a1-6/Desktop/python\ project/BRI
python3 -m venv venv
source venv/bin/activate
```

2. Install requirements:
```bash
pip install -r requirements.txt
```

3. Run availability checker:
```bash
cd data_fetch_and_process
python data_availability_checker.py
```

## Next Steps

1. ✓ Check Yahoo Finance availability
2. Review which cases need alternative data sources
3. Implement data fetchers for available sources
4. Process and validate data quality
5. Calculate BRI components
6. Backtest and validate against BofA results

