"""
BRI Configuration Module
Defines default parameters for Bubble Risk Indicator calculations
Based on Bank of America's "Year Ahead 2026: The Bubble Era" methodology
"""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class MomentWindow:
    """Window configuration for moment calculation and percentile lookback"""
    moment_window: int        # Window for calculating moment value
    percentile_lookback: int  # Historical lookback for percentile ranking


@dataclass
class WindowConfig:
    """
    Configuration for rolling window calculations
    
    Based on BofA BRI methodology:
    - Short-term: 3m moments vs 1y percentile lookback
    - Mid-term: 6m moments vs 3y percentile lookback
    - Long-term: 1y moments vs 5y percentile lookback
    """
    short_term: MomentWindow = field(default_factory=lambda: MomentWindow(
        moment_window=63,          # ~3 months
        percentile_lookback=252    # ~1 year
    ))
    mid_term: MomentWindow = field(default_factory=lambda: MomentWindow(
        moment_window=126,         # ~6 months
        percentile_lookback=756    # ~3 years
    ))
    long_term: MomentWindow = field(default_factory=lambda: MomentWindow(
        moment_window=252,         # ~1 year
        percentile_lookback=1260   # ~5 years
    ))


@dataclass
class MomentWeights:
    """
    Weights for combining the four moments into BRI sub-indicators
    
    Four moments used in BRI:
    1. Returns - Recent return performance
    2. Volatility - Price volatility/dispersion
    3. Momentum - Trend strength/persistence  
    4. Fragility - Tail risk/extreme events (kurtosis-based)
    """
    returns: float = 0.25      # Weight for returns moment
    volatility: float = 0.25   # Weight for volatility moment
    momentum: float = 0.25     # Weight for momentum moment
    fragility: float = 0.25    # Weight for fragility moment (tail risk)
    
    def __post_init__(self):
        """Validate weights sum to 1.0"""
        total = self.returns + self.volatility + self.momentum + self.fragility
        if abs(total - 1.0) > 0.001:
            raise ValueError(f"Weights must sum to 1.0, got {total}")


@dataclass
class BubbleThresholds:
    """Thresholds for identifying bubble conditions"""
    warning: float = 1.5      # Warning level (1.5 standard deviations)
    bubble: float = 2.0       # Bubble level (2.0 standard deviations)
    extreme: float = 2.5      # Extreme bubble level (2.5 standard deviations)


@dataclass
class BRIConfig:
    """
    Main BRI Configuration
    
    This configuration follows Bank of America's methodology for the
    Bubble Risk Indicator based on four moments with percentile ranking.
    
    Key methodology:
    1. Calculate moment values over specific windows (e.g., 3m for ST)
    2. Compute percentile rank vs historical lookback (e.g., 1y for ST)
    3. Average percentile ranks across four moments to get sub-indicator
    4. Apply scaling factor to normalize
    
    Users can customize these parameters based on their analysis needs.
    """
    
    # Rolling window configurations for different time horizons
    windows: WindowConfig = field(default_factory=WindowConfig)
    
    # Weights for combining the four moments (returns, vol, momentum, fragility)
    # Default: equal-weighted (0.25 each) as per standard BRI methodology
    weights: MomentWeights = field(default_factory=MomentWeights)
    
    # Bubble detection thresholds (applied to scaled indicators)
    thresholds: BubbleThresholds = field(default_factory=BubbleThresholds)
    
    # Return calculation method
    use_log_returns: bool = True  # True for log returns, False for simple returns
    
    # Minimum number of data points required for calculation
    min_periods_ratio: float = 0.8  # Require 80% of window to have data
    
    # Whether to adjust for outliers before calculating moments
    remove_outliers: bool = False
    outlier_threshold: float = 3.0  # Z-score threshold for outliers
    
    # Scaling factor configuration (dynamic calculation using logistic function)
    use_dynamic_scaling: bool = True  # If False, use static scaling_factor
    scaling_steepness: float = 3.0    # Steepness parameter (k) for logistic function
    scaling_logic_note: str = (
        "Scaling Factor uses logistic transformation: 1 / (1 + exp(-k * normalized_return)). "
        "normalized_return = trailing_return / trailing_volatility. "
        "Higher k (e.g., 5) makes the transition steeper; lower k (e.g., 2) makes it smoother. "
        "Default k=3.0 provides balanced sensitivity."
    )
    
    def get_min_periods(self, window: int) -> int:
        """Calculate minimum required periods for a given window"""
        return int(window * self.min_periods_ratio)
    
    def to_dict(self) -> Dict:
        """Convert configuration to dictionary"""
        return {
            'windows': {
                'short_term': {
                    'moment_window': self.windows.short_term.moment_window,
                    'percentile_lookback': self.windows.short_term.percentile_lookback
                },
                'mid_term': {
                    'moment_window': self.windows.mid_term.moment_window,
                    'percentile_lookback': self.windows.mid_term.percentile_lookback
                },
                'long_term': {
                    'moment_window': self.windows.long_term.moment_window,
                    'percentile_lookback': self.windows.long_term.percentile_lookback
                }
            },
            'weights': {
                'returns': self.weights.returns,
                'volatility': self.weights.volatility,
                'momentum': self.weights.momentum,
                'fragility': self.weights.fragility
            },
            'thresholds': {
                'warning': self.thresholds.warning,
                'bubble': self.thresholds.bubble,
                'extreme': self.thresholds.extreme
            },
            'use_log_returns': self.use_log_returns,
            'min_periods_ratio': self.min_periods_ratio,
            'remove_outliers': self.remove_outliers,
            'use_dynamic_scaling': self.use_dynamic_scaling,
            'scaling_steepness': self.scaling_steepness,
            'outlier_threshold': self.outlier_threshold,
            'scaling_logic_note': self.scaling_logic_note
        }


# Default configuration instance
DEFAULT_CONFIG = BRIConfig()


# Alternative configurations for different analysis styles

def create_conservative_config() -> BRIConfig:
    """
    Conservative configuration with emphasis on volatility and tail risk
    More weight on volatility and fragility (tail risk)
    """
    config = BRIConfig()
    config.weights = MomentWeights(
        returns=0.15,
        volatility=0.35,
        momentum=0.15,
        fragility=0.35
    )
    config.thresholds = BubbleThresholds(
        warning=1.0,
        bubble=1.5,
        extreme=2.0
    )
    return config


def create_momentum_focused_config() -> BRIConfig:
    """
    Momentum-focused configuration emphasizing returns and momentum
    """
    config = BRIConfig()
    config.weights = MomentWeights(
        returns=0.35,
        volatility=0.15,
        momentum=0.35,
        fragility=0.15
    )
    return config


def create_short_term_config() -> BRIConfig:
    """
    Short-term trading configuration with smaller windows
    """
    config = BRIConfig()
    config.windows = WindowConfig(
        short_term=MomentWindow(moment_window=21, percentile_lookback=63),    # 1m vs 3m
        mid_term=MomentWindow(moment_window=63, percentile_lookback=252),     # 3m vs 1y
        long_term=MomentWindow(moment_window=126, percentile_lookback=756)    # 6m vs 3y
    )
    return config


def create_long_term_config() -> BRIConfig:
    """
    Long-term investment configuration with larger windows
    """
    config = BRIConfig()
    config.windows = WindowConfig(
        short_term=MomentWindow(moment_window=126, percentile_lookback=756),   # 6m vs 3y
        mid_term=MomentWindow(moment_window=252, percentile_lookback=1260),    # 1y vs 5y
        long_term=MomentWindow(moment_window=756, percentile_lookback=2520)    # 3y vs 10y
    )
    return config


# Configuration presets dictionary
CONFIG_PRESETS = {
    'default': DEFAULT_CONFIG,
    'conservative': create_conservative_config(),
    'momentum': create_momentum_focused_config(),
    'short_term': create_short_term_config(),
    'long_term': create_long_term_config()
}


def get_config(preset: str = 'default') -> BRIConfig:
    """
    Get a configuration preset
    
    Parameters:
    -----------
    preset : str
        Configuration preset name. Options:
        - 'default': Standard BRI configuration (equal weights)
        - 'conservative': Emphasizes volatility and tail risk
        - 'momentum': Emphasizes returns and skewness
        - 'short_term': Shorter rolling windows for trading
        - 'long_term': Longer rolling windows for investment
    
    Returns:
    --------
    BRIConfig: Configuration object
    """
    if preset not in CONFIG_PRESETS:
        raise ValueError(f"Unknown preset: {preset}. Available: {list(CONFIG_PRESETS.keys())}")
    
    return CONFIG_PRESETS[preset]

