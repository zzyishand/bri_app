# BRI Methodology - Corrected Implementation (V2)

## Overview

This document explains the **corrected** BRI calculation methodology implemented in `bri_calculator_v2.py`, based on Bank of America's actual approach using **percentile ranking**.

## Key Differences: V1 vs V2

### ❌ V1 (Incorrect - Old Implementation)

The initial implementation (`bri_calculator.py`) was **incorrect**:

1. Calculated rolling statistical moments (mean, variance, skewness, kurtosis)
2. Normalized these moments using z-scores
3. Combined normalized moments with weights
4. **Problem**: This doesn't match BofA's actual methodology

### ✅ V2 (Correct - New Implementation)

The corrected implementation (`bri_calculator_v2.py`) follows BofA's actual methodology:

1. Calculate **moment VALUES** over specific windows
2. Compute **PERCENTILE RANK** of each moment against historical lookback
3. Average percentile ranks across four moments
4. Apply scaling factor

---

## Correct BRI Methodology

### Step-by-Step Process

#### For Each Sub-Indicator (ST/MT/LT):

**1. Calculate Moment Values**

Using a specific **moment window**:

| Sub-Indicator | Moment Window |
|--------------|---------------|
| Short-term (ST) | 3 months (~63 days) |
| Mid-term (MT) | 6 months (~126 days) |
| Long-term (LT) | 1 year (~252 days) |

**Four Moments Calculated:**

- **Returns**: Cumulative return over the window
  - Log returns: Sum of log returns
  - Simple returns: Product of (1+r) - 1
  
- **Volatility**: Standard deviation of returns over the window
  - Measures price dispersion/risk
  
- **Momentum**: Price change over the window
  - `(current_price / price_N_periods_ago) - 1`
  
- **Fragility**: Excess kurtosis over the window
  - Measures tail risk (fat tails = more fragility)

**2. Build Historical Series**

For each moment, create a historical series by:
- Rolling the moment calculation through time
- Each point in history represents that moment's value at that time

**3. Calculate Percentile Rank**

For each current moment value, calculate its percentile rank against **percentile lookback window**:

| Sub-Indicator | Percentile Lookback |
|--------------|---------------------|
| Short-term (ST) | 1 year (~252 days) |
| Mid-term (MT) | 3 years (~756 days) |
| Long-term (LT) | 5 years (~1260 days) |

**Percentile Rank Formula:**
```
percentile = (count of values ≤ current_value) / total_values × 100
```

Result: Value from 0 to 100

**4. Average Percentile Ranks**

Calculate weighted average across the four moment percentiles:

```
avg_percentile = (
    w_returns × returns_percentile +
    w_volatility × volatility_percentile +
    w_momentum × momentum_percentile +
    w_fragility × fragility_percentile
)
```

**Default weights** (equal-weighted): 0.25 each

**5. Apply Scaling Factor**

Convert to indicator value:
```
indicator = (avg_percentile / 100) × scaling_factor
```

Currently using **placeholder scaling_factor = 0.5**

(Will be replaced with logistic transformation in future)

**6. Calculate Composite BRI**

Average across all three sub-indicators:
```
composite_BRI = (ST_indicator + MT_indicator + LT_indicator) / 3
```

---

## Configuration Details

### Window Configuration (Default)

```python
short_term:
  moment_window: 63 days      # ~3 months
  percentile_lookback: 252    # ~1 year

mid_term:
  moment_window: 126 days     # ~6 months
  percentile_lookback: 756    # ~3 years

long_term:
  moment_window: 252 days     # ~1 year
  percentile_lookback: 1260   # ~5 years
```

### Moment Weights (Default)

```python
returns: 0.25
volatility: 0.25
momentum: 0.25
fragility: 0.25
```

All weights sum to 1.0 (equal-weighted by default).

---

## Output Structure

### BRI Results CSV (33 columns)

For each sub-indicator (short/mid/long), the output contains:

**Moment Values** (4 columns):
- `{horizon}_returns_value`
- `{horizon}_volatility_value`
- `{horizon}_momentum_value`
- `{horizon}_fragility_value`

**Percentile Ranks** (4 columns):
- `{horizon}_returns_pctile`
- `{horizon}_volatility_pctile`
- `{horizon}_momentum_pctile`
- `{horizon}_fragility_pctile`

**Sub-Indicator** (2 columns):
- `{horizon}_avg_percentile` - Average percentile across 4 moments
- `{horizon}_indicator` - Scaled indicator value

**Additional**:
- `price` - Asset price
- `returns` - Calculated returns
- `composite_bri` - Final BRI score

---

## Interpretation

### Percentile Ranks (0-100)

- **0-25**: Bottom quartile (low)
- **25-50**: Below median
- **50-75**: Above median
- **75-100**: Top quartile (high)

### BRI Indicator Values

With scaling_factor = 0.5:
- **0.0 - 0.125**: Low (percentile 0-25)
- **0.125 - 0.25**: Below average (percentile 25-50)
- **0.25 - 0.375**: Above average (percentile 50-75)
- **0.375 - 0.5**: High (percentile 75-100)

### Example Current Results (Dec 11, 2025)

| Asset | Composite BRI | Interpretation |
|-------|---------------|----------------|
| Gold | 0.4369 | **High bubble risk** (80-92 percentile) |
| Nikkei 225 | 0.3678 | **Elevated** (64-79 percentile) |
| Biotech | 0.3153 | **Moderate-high** (53-76 percentile) |
| NASDAQ-100 | 0.2651 | **Average** (48-57 percentile) |
| Dow Jones | 0.2500 | **Average** (37-58 percentile) |
| Crude Oil | 0.2050 | **Below average** (39-44 percentile) |
| HSCEI | 0.1905 | **Mixed** (16-77 percentile, LT elevated) |
| Bitcoin | 0.0773 | **Very low** (7-21 percentile) |

**Key Insight**: Gold shows the highest bubble risk with percentiles in the 80-92 range across all horizons!

---

## Why This Methodology?

### Advantages of Percentile Ranking:

1. **Historical Context**: Compares current values to their own history
2. **Scale-Invariant**: Works across assets with different price scales
3. **Robust**: Less sensitive to outliers than z-scores
4. **Interpretable**: Percentiles are intuitive (50th percentile = median)
5. **Non-Parametric**: Doesn't assume normal distribution

### Why Not Z-Scores?

Z-scores assume:
- Normal distribution (not true for financial returns)
- Stationarity (mean/std constant over time)
- Scale matters (but we want relative positioning)

Percentile ranking is **more appropriate** for financial time series.

---

## Future Enhancements

### Logistic Scaling Factor

Currently using placeholder 0.5. Future implementation:

```python
def logistic_scaling(x_norm, alpha=1.0):
    """
    Logistic transformation to map to [0, 1]
    
    Result = 1 / (1 + exp(-alpha * x_norm))
    """
    return 1.0 / (1.0 + np.exp(-alpha * x_norm))
```

This will provide:
- Smooth transformation
- Output strictly in [0, 1]
- Adjustable sensitivity via alpha parameter

### Additional Refinements

1. **Adaptive Windows**: Adjust windows based on market regime
2. **Volume-Weighted Moments**: Incorporate volume in calculations
3. **Cross-Asset Correlation**: Consider inter-asset bubble contagion
4. **Machine Learning**: Learn optimal weights from historical bubbles

---

## Usage Example

```python
from indicator import BRICalculatorV2, get_config
import pandas as pd

# Load data
data = pd.read_csv('asset_data.csv', index_col=0, parse_dates=True)

# Create calculator with default config
calculator = BRICalculatorV2()

# Calculate BRI
results = calculator.calculate_full_bri(data, asset_name='NASDAQ_100')

# Get current status
status = calculator.get_current_status(results)
print(f"Composite BRI: {status['composite_bri']:.4f}")
print(f"ST percentile: {status['short_term']['avg_percentile']:.1f}")
print(f"MT percentile: {status['mid_term']['avg_percentile']:.1f}")
print(f"LT percentile: {status['long_term']['avg_percentile']:.1f}")

# Save results
calculator.save_results(results, 'bri_results.csv')
```

---

## References

1. **Bank of America**: "Year Ahead 2026: The Bubble Era"
2. **Percentile Methodology**: Non-parametric ranking for financial time series
3. **Statistical Moments**: Returns, volatility, momentum, fragility (kurtosis)

---

## Files

- **`bri_calculator_v2.py`**: Corrected implementation
- **`bri_config.py`**: Updated configuration with MomentWindow structure
- **`statistical_moments.py`**: Added percentile rank calculations
- **`example_calculate_bri_v2.py`**: Batch processing script for V2

---

**Version**: 2.0 (Corrected)  
**Date**: 2025-12-11  
**Status**: ✅ Fully Operational

