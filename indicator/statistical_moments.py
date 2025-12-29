"""
Statistical Moments Calculator
Calculates the four statistical moments for BRI analysis:
1. Mean - Average returns
2. Variance - Volatility/dispersion
3. Skewness - Asymmetry
4. Kurtosis - Fat tails/extreme events
"""

import pandas as pd
import numpy as np
from typing import Optional, Tuple
from scipy import stats


class StatisticalMoments:
    """
    Calculator for the four statistical moments used in BRI
    
    These moments describe the distribution of asset returns:
    - Mean (μ): Central tendency
    - Variance (σ²): Dispersion
    - Skewness: Asymmetry (positive = right tail, negative = left tail)
    - Kurtosis: Tail heaviness (high = more extreme events)
    """
    
    @staticmethod
    def calculate_returns(prices: pd.Series, 
                         method: str = 'log',
                         periods: int = 1) -> pd.Series:
        """
        Calculate returns from price series
        
        Parameters:
        -----------
        prices : pd.Series
            Price series
        method : str
            'log' for log returns, 'simple' for simple returns
        periods : int
            Number of periods for return calculation (default: 1 for daily)
        
        Returns:
        --------
        pd.Series: Returns series
        """
        if method == 'log':
            returns = np.log(prices / prices.shift(periods))
        elif method == 'simple':
            returns = prices.pct_change(periods)
        else:
            raise ValueError(f"Unknown method: {method}. Use 'log' or 'simple'")
        
        return returns
    
    @staticmethod
    def rolling_mean(returns: pd.Series, 
                    window: int, 
                    min_periods: Optional[int] = None) -> pd.Series:
        """
        Calculate rolling mean (average returns)
        
        Parameters:
        -----------
        returns : pd.Series
            Returns series
        window : int
            Rolling window size
        min_periods : int, optional
            Minimum number of observations required
        
        Returns:
        --------
        pd.Series: Rolling mean
        """
        if min_periods is None:
            min_periods = int(window * 0.8)
        
        return returns.rolling(window=window, min_periods=min_periods).mean()
    
    @staticmethod
    def rolling_variance(returns: pd.Series, 
                        window: int, 
                        min_periods: Optional[int] = None) -> pd.Series:
        """
        Calculate rolling variance (volatility squared)
        
        Parameters:
        -----------
        returns : pd.Series
            Returns series
        window : int
            Rolling window size
        min_periods : int, optional
            Minimum number of observations required
        
        Returns:
        --------
        pd.Series: Rolling variance
        """
        if min_periods is None:
            min_periods = int(window * 0.8)
        
        return returns.rolling(window=window, min_periods=min_periods).var()
    
    @staticmethod
    def rolling_std(returns: pd.Series, 
                   window: int, 
                   min_periods: Optional[int] = None) -> pd.Series:
        """
        Calculate rolling standard deviation (volatility)
        
        Parameters:
        -----------
        returns : pd.Series
            Returns series
        window : int
            Rolling window size
        min_periods : int, optional
            Minimum number of observations required
        
        Returns:
        --------
        pd.Series: Rolling standard deviation
        """
        if min_periods is None:
            min_periods = int(window * 0.8)
        
        return returns.rolling(window=window, min_periods=min_periods).std()
    
    @staticmethod
    def rolling_skewness(returns: pd.Series, 
                        window: int, 
                        min_periods: Optional[int] = None) -> pd.Series:
        """
        Calculate rolling skewness (asymmetry)
        
        Skewness interpretation:
        - Positive: Right tail (more extreme positive returns)
        - Negative: Left tail (more extreme negative returns)
        - Zero: Symmetric distribution
        
        Parameters:
        -----------
        returns : pd.Series
            Returns series
        window : int
            Rolling window size
        min_periods : int, optional
            Minimum number of observations required
        
        Returns:
        --------
        pd.Series: Rolling skewness
        """
        if min_periods is None:
            min_periods = int(window * 0.8)
        
        return returns.rolling(window=window, min_periods=min_periods).skew()
    
    @staticmethod
    def rolling_kurtosis(returns: pd.Series, 
                        window: int, 
                        min_periods: Optional[int] = None,
                        excess: bool = True) -> pd.Series:
        """
        Calculate rolling kurtosis (tail heaviness)
        
        Kurtosis interpretation:
        - High excess kurtosis (>0): Fat tails, more extreme events
        - Low excess kurtosis (<0): Thin tails, fewer extreme events
        - Excess kurtosis = 0: Normal distribution tails
        
        Parameters:
        -----------
        returns : pd.Series
            Returns series
        window : int
            Rolling window size
        min_periods : int, optional
            Minimum number of observations required
        excess : bool
            If True, calculate excess kurtosis (subtract 3)
        
        Returns:
        --------
        pd.Series: Rolling kurtosis
        """
        if min_periods is None:
            min_periods = int(window * 0.8)
        
        # pandas.kurt() already returns excess kurtosis by default
        kurt = returns.rolling(window=window, min_periods=min_periods).kurt()
        
        if not excess:
            # Add 3 to get raw kurtosis
            kurt = kurt + 3
        
        return kurt
    
    @staticmethod
    def calculate_all_moments(returns: pd.Series, 
                             window: int, 
                             min_periods: Optional[int] = None) -> pd.DataFrame:
        """
        Calculate all four statistical moments at once
        
        Parameters:
        -----------
        returns : pd.Series
            Returns series
        window : int
            Rolling window size
        min_periods : int, optional
            Minimum number of observations required
        
        Returns:
        --------
        pd.DataFrame: DataFrame with columns for each moment
        """
        if min_periods is None:
            min_periods = int(window * 0.8)
        
        moments_df = pd.DataFrame(index=returns.index)
        
        moments_df['mean'] = StatisticalMoments.rolling_mean(
            returns, window, min_periods
        )
        moments_df['variance'] = StatisticalMoments.rolling_variance(
            returns, window, min_periods
        )
        moments_df['skewness'] = StatisticalMoments.rolling_skewness(
            returns, window, min_periods
        )
        moments_df['kurtosis'] = StatisticalMoments.rolling_kurtosis(
            returns, window, min_periods
        )
        
        return moments_df
    
    @staticmethod
    def remove_outliers(returns: pd.Series, 
                       threshold: float = 3.0) -> pd.Series:
        """
        Remove outliers using z-score method
        
        Parameters:
        -----------
        returns : pd.Series
            Returns series
        threshold : float
            Z-score threshold for outlier detection
        
        Returns:
        --------
        pd.Series: Returns with outliers replaced by NaN
        """
        z_scores = np.abs(stats.zscore(returns.dropna()))
        returns_clean = returns.copy()
        returns_clean[z_scores > threshold] = np.nan
        
        return returns_clean
    
    @staticmethod
    def normalize_zscore(series: pd.Series) -> pd.Series:
        """
        Normalize series using z-score (standard score)
        
        Z-score = (x - mean) / std
        
        Parameters:
        -----------
        series : pd.Series
            Series to normalize
        
        Returns:
        --------
        pd.Series: Normalized series
        """
        return (series - series.mean()) / series.std()
    
    @staticmethod
    def normalize_minmax(series: pd.Series) -> pd.Series:
        """
        Normalize series to [0, 1] range using min-max scaling
        
        Parameters:
        -----------
        series : pd.Series
            Series to normalize
        
        Returns:
        --------
        pd.Series: Normalized series
        """
        return (series - series.min()) / (series.max() - series.min())
    
    @staticmethod
    def normalize_robust(series: pd.Series) -> pd.Series:
        """
        Robust normalization using median and IQR
        Less sensitive to outliers
        
        Parameters:
        -----------
        series : pd.Series
            Series to normalize
        
        Returns:
        --------
        pd.Series: Normalized series
        """
        median = series.median()
        q75, q25 = series.quantile([0.75, 0.25])
        iqr = q75 - q25
        
        if iqr == 0:
            return series - median
        
        return (series - median) / iqr
    
    @staticmethod
    def normalize(series: pd.Series, method: str = 'zscore') -> pd.Series:
        """
        Normalize series using specified method
        
        Parameters:
        -----------
        series : pd.Series
            Series to normalize
        method : str
            Normalization method: 'zscore', 'minmax', or 'robust'
        
        Returns:
        --------
        pd.Series: Normalized series
        """
        if method == 'zscore':
            return StatisticalMoments.normalize_zscore(series)
        elif method == 'minmax':
            return StatisticalMoments.normalize_minmax(series)
        elif method == 'robust':
            return StatisticalMoments.normalize_robust(series)
        else:
            raise ValueError(f"Unknown normalization method: {method}")
    
    @staticmethod
    def calculate_percentile_rank(current_value: float, 
                                  historical_series: pd.Series) -> float:
        """
        Calculate percentile rank of current value within historical series
        
        Percentile rank = (number of values <= current_value) / total_values * 100
        
        Parameters:
        -----------
        current_value : float
            Current moment value
        historical_series : pd.Series
            Historical series of moment values for comparison
        
        Returns:
        --------
        float: Percentile rank (0-100)
        """
        if pd.isna(current_value) or len(historical_series.dropna()) == 0:
            return np.nan
        
        # Remove NaN values
        clean_series = historical_series.dropna()
        
        # Count values less than or equal to current value
        rank = (clean_series <= current_value).sum()
        
        # Calculate percentile (0-100 scale)
        percentile = (rank / len(clean_series)) * 100
        
        return percentile
    
    @staticmethod
    def rolling_percentile_rank(series: pd.Series,
                               value_window: int,
                               lookback_window: int,
                               min_periods: Optional[int] = None) -> pd.Series:
        """
        Calculate rolling percentile rank for a series
        
        For each point:
        1. Get current value (could be already calculated moment)
        2. Look back over lookback_window to get historical distribution
        3. Calculate percentile rank of current value in that distribution
        
        Parameters:
        -----------
        series : pd.Series
            Series of values (e.g., moment values over time)
        value_window : int
            Not used in this version (assumes series already contains moment values)
        lookback_window : int
            Historical lookback window for percentile comparison
        min_periods : int, optional
            Minimum periods required
        
        Returns:
        --------
        pd.Series: Rolling percentile ranks
        """
        if min_periods is None:
            min_periods = int(lookback_window * 0.8)
        
        percentile_ranks = pd.Series(index=series.index, dtype=float)
        
        for i in range(len(series)):
            if i < min_periods:
                percentile_ranks.iloc[i] = np.nan
                continue
            
            # Current value
            current_value = series.iloc[i]
            
            # Historical lookback
            start_idx = max(0, i - lookback_window + 1)
            historical_series = series.iloc[start_idx:i+1]
            
            # Calculate percentile rank
            percentile_ranks.iloc[i] = StatisticalMoments.calculate_percentile_rank(
                current_value, historical_series
            )
        
        return percentile_ranks
    
    @staticmethod
    def calculate_moving_average_price(prices: pd.Series, window: int) -> pd.Series:
        """
        Calculate moving average price
        
        Parameters:
        -----------
        prices : pd.Series
            Price series
        window : int
            Window size
        
        Returns:
        --------
        pd.Series: Moving average price
        """
        return prices.rolling(window=window).mean()
    
    @staticmethod
    def calculate_mean_absolute_deviation(returns: pd.Series, window: int) -> pd.Series:
        """
        Calculate realized mean absolute deviation (MAD)
        
        MAD = mean(|returns - mean(returns)|)
        
        Parameters:
        -----------
        returns : pd.Series
            Returns series
        window : int
            Window size
        
        Returns:
        --------
        pd.Series: Rolling mean absolute deviation
        """
        def mad(x):
            return np.mean(np.abs(x - np.mean(x)))
        
        return returns.rolling(window=window).apply(mad, raw=True)
    
    @staticmethod
    def calculate_price_momentum_from_ma(prices: pd.Series, 
                                        moving_avg: pd.Series) -> pd.Series:
        """
        Calculate price momentum as % distance from moving average
        
        momentum = (current_price - moving_avg) / moving_avg * 100
        
        Parameters:
        -----------
        prices : pd.Series
            Current price series
        moving_avg : pd.Series
            Moving average price series
        
        Returns:
        --------
        pd.Series: Price momentum (%)
        """
        return (prices - moving_avg) / moving_avg * 100
    
    @staticmethod
    def calculate_fragility_convexity(realized_vol: pd.Series,
                                      realized_mad: pd.Series) -> pd.Series:
        """
        Calculate fragility/convexity
        
        fragility = realized_vol - realized_mad
        
        Higher values indicate more fat tails (fragility)
        
        Parameters:
        -----------
        realized_vol : pd.Series
            Realized volatility (standard deviation)
        realized_mad : pd.Series
            Realized mean absolute deviation
        
        Returns:
        --------
        pd.Series: Fragility/convexity measure
        """
        return realized_vol - realized_mad
    
    @staticmethod
    def calculate_moments_summary(returns: pd.Series) -> dict:
        """
        Calculate summary statistics for a returns series
        
        Parameters:
        -----------
        returns : pd.Series
            Returns series
        
        Returns:
        --------
        dict: Summary statistics
        """
        clean_returns = returns.dropna()
        
        return {
            'count': len(clean_returns),
            'mean': clean_returns.mean(),
            'std': clean_returns.std(),
            'variance': clean_returns.var(),
            'skewness': clean_returns.skew(),
            'kurtosis': clean_returns.kurt(),
            'min': clean_returns.min(),
            'max': clean_returns.max(),
            'percentile_25': clean_returns.quantile(0.25),
            'percentile_50': clean_returns.median(),
            'percentile_75': clean_returns.quantile(0.75)
        }

