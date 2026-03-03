# Yahoo Finance Data Availability Summary for BRI Project

## Overview
This document summarizes the expected data availability from Yahoo Finance for the 8 historical bubble cases identified by Bank of America Research.

## Data Requirements for BRI Calculation

To calculate the Bubble Risk Indicator, we need the following data fields:
- **Date** (trading date)
- **Open** (opening price)
- **High** (daily high)
- **Low** (daily low)
- **Close** (closing/settlement price) - **PRIMARY REQUIREMENT**
- **Volume** (trading volume)

### Minimum Requirements
- At least **252 trading days** (1 year) of historical data
- **Daily frequency** data
- **Close prices** are essential for all calculations

## Expected Yahoo Finance Coverage

### ✅ STRONG Coverage (Yahoo Finance should have full data)

#### 1. **Nasdaq 2000 Bubble** (^IXIC)
- **Period Needed:** Jan 1995 - Mar 2000
- **Expected Yahoo Coverage:** 1971 - Present
- **Status:** ✅ **EXCELLENT** - Full coverage expected
- **Notes:** Nasdaq Composite has excellent historical data on Yahoo

#### 2. **Bitcoin 2017** (BTC-USD)
- **Period Needed:** Jul 2017 - Dec 2017
- **Expected Yahoo Coverage:** Sep 2014 - Present  
- **Status:** ✅ **EXCELLENT** - Full coverage expected
- **Notes:** Bitcoin data widely available from 2014 onwards

#### 3. **Biotech 2021** (XBI - SPDR S&P Biotech ETF)
- **Period Needed:** May 2020 - Feb 2021
- **Expected Yahoo Coverage:** 2006 - Present (ETF inception Feb 2006)
- **Status:** ✅ **EXCELLENT** - Full coverage expected
- **Notes:** ETF data very reliable on Yahoo

#### 4. **Oil 2008** (CL=F - Crude Oil Futures)
- **Period Needed:** Jan 2007 - Jul 2008
- **Expected Yahoo Coverage:** 1983 - Present
- **Status:** ✅ **GOOD** - Should have coverage
- **Notes:** Futures data can be spotty; may have gaps

#### 5. **China H-Shares 2007** (^HSCE)
- **Period Needed:** Jun 2006 - Oct 2007
- **Expected Yahoo Coverage:** 1999 - Present
- **Status:** ✅ **GOOD** - Should have coverage
- **Notes:** Hong Kong index data generally available

### ⚠️ MODERATE Coverage (Partial or alternative tickers needed)

#### 6. **Nikkei 1987** (^N225)
- **Period Needed:** Jan 1986 - Oct 1987
- **Expected Yahoo Coverage:** 1984 - Present
- **Status:** ⚠️ **MODERATE** - Should have data but quality uncertain
- **Notes:** Yahoo's Nikkei data quality in 1980s may be limited

#### 7. **Gold 1980** (GC=F - Gold Futures)
- **Period Needed:** Jul 1979 - Jan 1980
- **Expected Yahoo Coverage:** 1975 - Present (varies)
- **Status:** ⚠️ **UNCERTAIN** - Futures data spotty for 1970s
- **Alternative:** Consider spot gold price sources (FRED, Quandl)

### ❌ POOR Coverage (Alternative sources required)

#### 8. **Dow Jones 1929** (^DJI)
- **Period Needed:** Oct 1926 - Sep 1929
- **Expected Yahoo Coverage:** 1985 - Present (reconstructed data varies)
- **Status:** ❌ **INSUFFICIENT** - Yahoo typically starts from mid-1980s
- **Alternative Sources Required:**
  - FRED (Federal Reserve Economic Data)
  - Robert Shiller's Historical Stock Data
  - Yale University Historical Data
  - Academic/Research databases

---

## Yahoo Finance Data Characteristics

### Strengths:
✅ **Free and accessible** - No API key required  
✅ **Good coverage** for modern era (1990s onwards)  
✅ **Reliable** for major indices and ETFs  
✅ **Standard OHLCV format** - Easy to process  
✅ **High liquidity assets** well covered  

### Limitations:
❌ **Limited historical data** - Weak for pre-1980 periods  
❌ **Futures data** can have gaps and rollover issues  
❌ **Rate limiting** - Aggressive throttling on rapid requests  
❌ **Data quality** varies significantly by asset type  
❌ **Survivorship bias** - Delisted assets may be missing  

---

## Recommended Data Sources by Case

| Case | Primary Source | Alternative Source(s) | Priority |
|------|----------------|----------------------|----------|
| **Dow 1929** | ❌ Yahoo Insufficient | ✅ FRED, Shiller Data, Academic DBs | **HIGH** |
| **Gold 1980** | ⚠️ Yahoo (uncertain) | ✅ FRED (DFF), Quandl Gold | **MEDIUM** |
| **Nikkei 1987** | ✅ Yahoo ^N225 | Nikkei official source | **LOW** |
| **Nasdaq 2000** | ✅ Yahoo ^IXIC | - | **LOW** |
| **H-Shares 2007** | ✅ Yahoo ^HSCE | - | **LOW** |
| **Oil 2008** | ✅ Yahoo CL=F | EIA, FRED, Quandl | **LOW** |
| **Bitcoin 2017** | ✅ Yahoo BTC-USD | CoinGecko, CoinMarketCap | **LOW** |
| **Biotech 2021** | ✅ Yahoo XBI | - | **LOW** |

---

## Alternative Data Sources

### 1. **FRED (Federal Reserve Economic Data)**
- **Coverage:** Excellent macro & commodity data
- **Cost:** Free (API key required)
- **Best For:** Gold, Oil, Dow Jones historical, Interest Rates
- **API:** `fredapi` Python library
- **URL:** https://fred.stlouisfed.org/

**Recommended FRED Series:**
- `DJIA` - Dow Jones Industrial Average (1896-present)
- `GOLDAMGBD228NLBM` - Gold Fixing Price (1968-present)
- `DCOILWTICO` - Crude Oil WTI (1986-present)

### 2. **Quandl / Nasdaq Data Link**
- **Coverage:** Financial, commodity, crypto data
- **Cost:** Free tier available (limited calls)
- **Best For:** Historical commodity prices, alternative datasets
- **API:** `quandl` Python library
- **URL:** https://data.nasdaq.com/

### 3. **Alpha Vantage**
- **Coverage:** Stocks, forex, crypto, technical indicators
- **Cost:** Free tier (5 calls/min, 500/day)
- **Best For:** Stock indices, technical analysis
- **API:** `alpha_vantage` Python library
- **URL:** https://www.alphavantage.co/

### 4. **CoinGecko / CoinMarketCap**
- **Coverage:** Cryptocurrency historical data
- **Cost:** Free APIs available
- **Best For:** Bitcoin and crypto data
- **API:** `pycoingecko` library

### 5. **Robert Shiller's Data**
- **Coverage:** US stock market data back to 1871
- **Cost:** Free (publicly available)
- **Best For:** Dow Jones 1929 bubble
- **URL:** http://www.econ.yale.edu/~shiller/data.htm

---

## Recommended Next Steps

### Phase 1: Test Yahoo Finance (Despite Rate Limits)
1. ✅ Create rate-limit-friendly fetcher with longer delays (5-10 seconds)
2. ✅ Test each ticker individually 
3. ✅ Document actual availability vs expected

### Phase 2: Implement Alternative Sources
Priority order based on gap analysis:
1. **HIGH Priority:** FRED for Dow 1929 data
2. **MEDIUM Priority:** FRED/Quandl for Gold 1980 validation
3. **LOW Priority:** Backup sources for other cases

### Phase 3: Data Validation
1. Cross-check overlapping periods from multiple sources
2. Identify and handle missing data
3. Verify data quality (outliers, gaps, errors)

### Phase 4: Data Processing Pipeline
1. Standardize all data to common format
2. Calculate required BRI components:
   - Returns (% change)
   - Realized Volatility (rolling std dev)
   - Momentum (distance from MA)
   - Fragility (Vol - MAD)
3. Generate bubble signals

---

## Data Fetching Strategy

### Immediate Actions:
```bash
# 1. Try Yahoo Finance with longer delays
python data_availability_checker.py  # Already created

# 2. Create FRED data fetcher (for Dow 1929)
python fetch_fred_data.py  # TO CREATE

# 3. Create robust Yahoo fetcher with retry logic
python fetch_yahoo_robust.py  # TO CREATE

# 4. Create data consolidation script
python consolidate_data.py  # TO CREATE
```

### Rate Limiting Strategy:
- **Delay between requests:** 5-10 seconds
- **Retry logic:** 3 attempts with exponential backoff
- **Cache results:** Save successful fetches immediately
- **Checkpoint progress:** Resume from where we left off

---

## Expected File Structure

```
data_fetch_and_process/
├── data/
│   ├── raw/
│   │   ├── yahoo_finance/
│   │   │   ├── dow_1929.csv
│   │   │   ├── nasdaq_2000.csv
│   │   │   ├── bitcoin_2017.csv
│   │   │   └── ...
│   │   ├── fred/
│   │   │   ├── djia_historical.csv
│   │   │   ├── gold_prices.csv
│   │   │   └── ...
│   │   └── other_sources/
│   ├── processed/
│   │   ├── dow_1929_processed.csv
│   │   └── ...
│   └── final/
│       └── all_bubbles_data.csv
├── fetch_yahoo_robust.py
├── fetch_fred_data.py
├── data_processor.py
└── calculate_bri.py
```

---

## Summary

**Yahoo Finance Coverage: 6/8 cases likely have sufficient data**

✅ **Can proceed with Yahoo:** Nasdaq 2000, Bitcoin 2017, Biotech 2021, Oil 2008, H-Shares 2007, Nikkei 1987  
⚠️ **Need alternatives:** Gold 1980 (maybe), Dow 1929 (definitely)

**Recommended approach:** 
1. Start with robust Yahoo fetcher for the 6 good cases
2. Simultaneously set up FRED for Dow 1929
3. Validate Gold 1980 data quality and supplement if needed

**Timeline estimate:**
- Yahoo data fetching: 1-2 hours (including rate limit delays)
- FRED integration: 30 minutes - 1 hour
- Data processing & validation: 2-3 hours
- **Total:** Half a day to have clean, validated data for all 8 cases


