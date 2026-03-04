# BRI Indicator Calculator

This module calculates the **Bubble Risk Indicator (BRI)** based on Bank of America's methodology using four statistical moments.

## 📐 Methodology

### Four Statistical Moments

The BRI framework analyzes return distributions using:

1. **Mean (μ)** - First Moment
   - Measures: Average returns
   - BRI Use: Identifies periods of exceptional returns
   - High values indicate strong momentum (potential bubble)

2. **Variance (σ²)** - Second Moment  
   - Measures: Return volatility/dispersion
   - BRI Use: Detects market instability
   - High values indicate increased risk

3. **Skewness** - Third Moment
   - Measures: Asymmetry in return distribution
   - BRI Use: Identifies one-sided price movements
   - Positive: More extreme upside moves (bubble formation)
   - Negative: More extreme downside moves (crash risk)

4. **Kurtosis** - Fourth Moment
   - Measures: "Fat tails" - extreme events probability
   - BRI Use: Detects tail risk
   - High excess kurtosis: More outliers, higher crash risk

### BRI Calculation Process

1. **Calculate Returns**: Log or simple returns from prices
2. **Rolling Windows**: Apply rolling windows (short/mid/long term)
3. **Compute Moments**: Calculate all four moments for each window
4. **Normalize**: Z-score normalization for comparability
5. **Weight & Combine**: Weighted sum of normalized moments
6. **Classify Risk**: Apply thresholds to identify bubble conditions

### Formula

```
BRI = w₁×Mean_norm + w₂×Variance_norm + w₃×Skewness_norm + w₄×Kurtosis_norm
```

**Default weights** (equal-weighted): w₁ = w₂ = w₃ = w₄ = 0.25

## 📁 Module Structure

```
indicator/
├── __init__.py                  # Package initialization
├── bri_config.py               # Configuration and parameters
├── statistical_moments.py      # Statistical calculations
├── bri_calculator.py           # Main BRI calculator
├── example_calculate_bri.py    # Example batch processing script
└── README.md                   # This file
```

## 🎯 Quick Start

### Basic Usage

```python
import pandas as pd
from indicator import BRICalculator

# Load price data
data = pd.read_csv('asset_data.csv', index_col=0, parse_dates=True)

# Create calculator
calculator = BRICalculator()

# Calculate BRI
results = calculator.calculate_full_bri(
    data, 
    price_column='Close',
    asset_name='NASDAQ_100'
)

# Save results
calculator.save_results(results, 'nasdaq_bri_results.csv')

# Get current status
status = calculator.get_current_status(results)
print(f"Current BRI: {status['composite_bri']:.3f}")
print(f"Risk Level: {status['composite_risk']}")
```

### Custom Configuration

```python
from indicator import BRICalculator, BRIConfig, WindowConfig, MomentWeights

# Create custom configuration
config = BRIConfig()

# Customize windows
config.windows = WindowConfig(
    short_term=21,   # 1 month
    mid_term=63,     # 3 months
    long_term=252    # 1 year
)

# Customize weights (emphasize volatility and tail risk)
config.weights = MomentWeights(
    mean=0.15,
    variance=0.35,
    skewness=0.15,
    kurtosis=0.35
)

# Use configuration
calculator = BRICalculator(config)
results = calculator.calculate_full_bri(data)
```

### Using Presets

```python
from indicator import BRICalculator, get_config

# Available presets: 'default', 'conservative', 'momentum', 'short_term', 'long_term'
config = get_config('conservative')

calculator = BRICalculator(config)
results = calculator.calculate_full_bri(data)
```

## ⚙️ Configuration Parameters

### Windows (Time Horizons)

| Horizon | Default | Description |
|---------|---------|-------------|
| Short-term | 63 days | ~3 months trading |
| Mid-term | 252 days | ~1 year trading |
| Long-term | 756 days | ~3 years trading |

### Moment Weights

| Moment | Default | Range |
|--------|---------|-------|
| Mean | 0.25 | 0.0 - 1.0 |
| Variance | 0.25 | 0.0 - 1.0 |
| Skewness | 0.25 | 0.0 - 1.0 |
| Kurtosis | 0.25 | 0.0 - 1.0 |

**Note**: Weights must sum to 1.0

### Bubble Thresholds

| Level | Default | Description |
|-------|---------|-------------|
| Warning | 1.5 | Early warning (1.5σ above mean) |
| Bubble | 2.0 | Bubble territory (2.0σ above mean) |
| Extreme | 2.5 | Extreme bubble (2.5σ above mean) |

## 📊 Output Format

### CSV Columns

The output CSV contains:

#### Price & Returns
- `price`: Asset price
- `returns`: Calculated returns

#### For Each Horizon (short/mid/long)
- `{horizon}_mean_raw`: Raw mean
- `{horizon}_variance_raw`: Raw variance
- `{horizon}_skewness_raw`: Raw skewness
- `{horizon}_kurtosis_raw`: Raw kurtosis
- `{horizon}_mean_norm`: Normalized mean
- `{horizon}_variance_norm`: Normalized variance
- `{horizon}_skewness_norm`: Normalized skewness
- `{horizon}_kurtosis_norm`: Normalized kurtosis
- `{horizon}_bri`: BRI score for this horizon
- `{horizon}_risk_level`: Risk classification (0-3)

#### Composite
- `composite_bri`: Average BRI across all horizons
- `composite_risk_level`: Overall risk classification

### Risk Levels

| Level | Value | Description |
|-------|-------|-------------|
| Normal | 0 | BRI < 1.5 |
| Warning | 1 | 1.5 ≤ BRI < 2.0 |
| Bubble | 2 | 2.0 ≤ BRI < 2.5 |
| Extreme Bubble | 3 | BRI ≥ 2.5 |

## 🚀 Batch Processing

Calculate BRI for all assets at once:

```bash
cd indicator
python example_calculate_bri.py
```

This will:
1. Load all assets from `data_fetch_and_process/raw_data/`
2. Calculate BRI for each asset
3. Save results to `indicator/bri_results/`
4. Generate a summary report

## 📈 Advanced Usage

### Calculate Single Horizon

```python
# Calculate only mid-term BRI
calculator = BRICalculator()
returns = calculator.prepare_data(data)
mid_term_results = calculator.calculate_single_horizon(
    returns, 
    window=252, 
    horizon_name='mid'
)
```

### Custom Normalization

```python
from indicator import BRIConfig

config = BRIConfig()
config.normalization_method = 'robust'  # Options: 'zscore', 'minmax', 'robust'

calculator = BRICalculator(config)
```

### Outlier Removal

```python
config = BRIConfig()
config.remove_outliers = True
config.outlier_threshold = 3.0  # Remove returns > 3 std deviations

calculator = BRICalculator(config)
```

## 🔬 Statistical Methods

### Return Calculation
- **Log returns** (default): `ln(P_t / P_{t-1})`
- **Simple returns**: `(P_t - P_{t-1}) / P_{t-1}`

### Normalization Methods
- **Z-score** (default): `(x - μ) / σ`
- **Min-Max**: `(x - min) / (max - min)`
- **Robust**: `(x - median) / IQR`

### Rolling Statistics
- Uses pandas rolling window functions
- Minimum periods: 80% of window size by default
- Forward-looking: Uses only past data (no lookahead bias)

## 📊 Interpretation Guide

### High BRI Score Indicates:
- ✅ Exceptional returns (high mean)
- ⚠️ Increased volatility (high variance)
- ⚠️ Asymmetric returns (high skewness)
- ⚠️ More extreme events (high kurtosis)

### Bubble Characteristics:
1. **Formation Phase**: Rising mean, increasing skewness
2. **Peak Phase**: High BRI, extreme positive skewness
3. **Crash Phase**: Negative skewness, high kurtosis

### Risk Management:
- **BRI < 1.5**: Normal conditions - full exposure
- **1.5 ≤ BRI < 2.0**: Warning - reduce exposure
- **2.0 ≤ BRI < 2.5**: Bubble - significant risk reduction
- **BRI ≥ 2.5**: Extreme - defensive positioning

## 🔧 Dependencies

```
pandas>=2.0.0
numpy>=1.24.0
scipy>=1.10.0
```

Install with:
```bash
pip install pandas numpy scipy
```

## 📚 Configuration Presets

### 1. Default
- Equal-weighted moments
- Standard windows (63/252/756 days)
- Conservative thresholds

### 2. Conservative
- Emphasizes volatility and tail risk
- Weights: Var=0.35, Kurt=0.35, Mean=0.15, Skew=0.15
- Lower thresholds (Warning=1.0, Bubble=1.5)

### 3. Momentum
- Emphasizes returns and skewness
- Weights: Mean=0.35, Skew=0.35, Var=0.15, Kurt=0.15

### 4. Short-term
- Shorter windows (21/63/252 days)
- For active trading

### 5. Long-term
- Longer windows (252/756/1260 days)
- For strategic investing

## 🎓 References

1. **Bank of America**: "Year Ahead 2026: The Bubble Era"
2. **Statistical Moments**: Pearson, K. (1895). "Contributions to the Mathematical Theory of Evolution"
3. **Bubble Detection**: Kindleberger, C. & Aliber, R. (2011). "Manias, Panics, and Crashes"

## ⚠️ Important Notes

1. **Historical Analysis Only**: BRI is not predictive, use with other indicators
2. **Minimum Data**: Requires sufficient history (>3 years recommended for long-term)
3. **Parameter Sensitivity**: Results depend on configuration choices
4. **Asset-Specific**: Different assets may require different thresholds
5. **No Guarantees**: Past bubbles may not match future patterns

## 🤝 Contributing

To add new features:
1. Extend `BRIConfig` for new parameters
2. Add methods to `StatisticalMoments` for new calculations
3. Update `BRICalculator` for new composite methods

## 📝 License

Part of the BRI Project - For research and educational purposes.

