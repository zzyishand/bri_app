"""
BRI (Bubble Risk Indicator) Package

This package provides tools for calculating the Bubble Risk Indicator
based on Bank of America's methodology using four statistical moments.

Main Components:
- BRICalculator: Main calculator class
- BRIConfig: Configuration and parameter management
- StatisticalMoments: Statistical calculations

Example Usage:
--------------
```python
from indicator import BRICalculator, get_config
import pandas as pd

# Load price data
data = pd.read_csv('price_data.csv', index_col=0, parse_dates=True)

# Create calculator with default config
calculator = BRICalculator()

# Calculate BRI
results = calculator.calculate_full_bri(data, price_column='Close', asset_name='NASDAQ')

# Save results
calculator.save_results(results, 'bri_results.csv')

# Get current status
status = calculator.get_current_status(results)
print(status)
```
"""

from .bri_config import (
    BRIConfig,
    WindowConfig,
    MomentWeights,
    BubbleThresholds,
    DEFAULT_CONFIG,
    CONFIG_PRESETS,
    get_config,
    create_conservative_config,
    create_momentum_focused_config,
    create_short_term_config,
    create_long_term_config
)

from .statistical_moments import StatisticalMoments

from .bri_calculator import BRICalculator
from .bri_calculator_v2 import BRICalculatorV2

__version__ = '1.0.0'
__author__ = 'BRI Project'

__all__ = [
    # Main calculator
    'BRICalculator',
    
    # Configuration
    'BRIConfig',
    'WindowConfig',
    'MomentWeights',
    'BubbleThresholds',
    'DEFAULT_CONFIG',
    'CONFIG_PRESETS',
    'get_config',
    'create_conservative_config',
    'create_momentum_focused_config',
    'create_short_term_config',
    'create_long_term_config',
    
    # Statistical tools
    'StatisticalMoments',
]

