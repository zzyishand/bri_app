"""
BRI Calculator V2 - Corrected Percentile Rank Methodology

This version implements the correct BRI calculation based on:
1. Calculate moment VALUES over specific windows (e.g., 3m for ST)
2. Compute PERCENTILE RANK against historical lookback (e.g., 1y for ST)  
3. Average percentile ranks across four moments to get sub-indicator
4. Apply scaling factor

Four moments:
- Returns: Recent return performance
- Volatility: Price dispersion/risk
- Momentum: Trend strength
- Fragility: Tail risk (kurtosis-based)
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Tuple
from datetime import datetime
import warnings

from .bri_config import BRIConfig, DEFAULT_CONFIG, MomentWindow
from .statistical_moments import StatisticalMoments


class BRICalculatorV2:
    """
    Bubble Risk Indicator Calculator - Percentile Rank Method
    
    Methodology:
    1. For each sub-indicator (ST/MT/LT):
       a. Calculate moment value using moment_window
       b. Build historical series of that moment
       c. Compute percentile rank vs percentile_lookback window
       d. Repeat for all 4 moments
       e. Average percentile ranks to get sub-indicator
    2. Apply scaling factor (placeholder: 0.5)
    """
    
    def __init__(self, config: Optional[BRIConfig] = None):
        """
        Initialize BRI Calculator
        
        Parameters:
        -----------
        config : BRIConfig, optional
            Configuration object. If None, uses default configuration
        """
        self.config = config if config is not None else DEFAULT_CONFIG
        self.moments_calculator = StatisticalMoments()
        
    def prepare_data(self, 
                     price_data: pd.DataFrame,
                     price_column: str = 'Close') -> Tuple[pd.Series, pd.Series]:
        """
        Prepare price data and calculate returns
        
        Parameters:
        -----------
        price_data : pd.DataFrame
            DataFrame with price data
        price_column : str
            Name of the price column to use
        
        Returns:
        --------
        tuple: (prices, returns)
        """
        if price_column not in price_data.columns:
            raise ValueError(f"Column '{price_column}' not found in data")
        
        prices = price_data[price_column]
        
        # Calculate returns
        method = 'log' if self.config.use_log_returns else 'simple'
        returns = self.moments_calculator.calculate_returns(prices, method=method)
        
        # Remove outliers if configured
        if self.config.remove_outliers:
            returns = self.moments_calculator.remove_outliers(
                returns, 
                threshold=self.config.outlier_threshold
            )
        
        return prices, returns
    
    def calculate_returns_moment(self, returns: pd.Series, window: int) -> pd.Series:
        """
        Calculate returns moment (cumulative return over window)
        
        Parameters:
        -----------
        returns : pd.Series
            Returns series
        window : int
            Window size
        
        Returns:
        --------
        pd.Series: Rolling cumulative returns
        """
        # Sum of log returns = cumulative return
        if self.config.use_log_returns:
            return returns.rolling(window=window).sum()
        else:
            # For simple returns: (1+r1)*(1+r2)*...*(1+rn) - 1
            return (1 + returns).rolling(window=window).apply(lambda x: x.prod(), raw=True) - 1
    
    def calculate_volatility_moment(self, returns: pd.Series, window: int) -> pd.Series:
        """
        Calculate volatility moment (ANNUALIZED standard deviation of returns)
        
        The volatility is annualized by multiplying daily volatility by sqrt(252),
        where 252 is the typical number of trading days per year.
        
        This ensures volatility values are comparable to market standards
        (e.g., 15%-80% for NASDAQ as shown in BofA exhibits).
        
        Parameters:
        -----------
        returns : pd.Series
            Daily returns series
        window : int
            Window size (in days)
        
        Returns:
        --------
        pd.Series: Rolling volatility (annualized)
        """
        # Calculate daily volatility
        daily_vol = returns.rolling(window=window).std()
        
        # Annualize: multiply by sqrt(252 trading days per year)
        annualized_vol = daily_vol * np.sqrt(252)
        
        return annualized_vol
    
    def calculate_momentum_moment(self, 
                                 prices: pd.Series, 
                                 window: int) -> Tuple[pd.Series, pd.Series]:
        """
        Calculate momentum moment as % distance from moving average
        
        momentum = (current_price - MA_price) / MA_price * 100
        
        Parameters:
        -----------
        prices : pd.Series
            Price series
        window : int
            Window size
        
        Returns:
        --------
        tuple: (momentum values, moving average prices)
        """
        # Calculate moving average price
        moving_avg = self.moments_calculator.calculate_moving_average_price(
            prices, window
        )
        
        # Calculate momentum as % distance from MA
        momentum = self.moments_calculator.calculate_price_momentum_from_ma(
            prices, moving_avg
        )
        
        return momentum, moving_avg
    
    def calculate_fragility_moment(self, 
                                  returns: pd.Series, 
                                  window: int) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate fragility/convexity moment
        
        fragility = realized_vol - realized_MAD
        
        Higher values indicate more fat tails (fragility/convexity)
        
        Parameters:
        -----------
        returns : pd.Series
            Returns series
        window : int
            Window size
        
        Returns:
        --------
        tuple: (fragility values, realized_vol, realized_MAD)
        """
        # Calculate realized volatility (standard deviation)
        realized_vol = self.calculate_volatility_moment(returns, window)
        
        # Calculate realized mean absolute deviation
        realized_mad = self.moments_calculator.calculate_mean_absolute_deviation(
            returns, window
        )
        
        # Calculate fragility/convexity
        fragility = self.moments_calculator.calculate_fragility_convexity(
            realized_vol, realized_mad
        )
        
        return fragility, realized_vol, realized_mad
    
    def calculate_moment_percentile_series(self,
                                          moment_series: pd.Series,
                                          percentile_lookback: int) -> pd.Series:
        """
        Calculate percentile rank series for a moment
        
        For each point, calculate percentile rank against historical lookback
        
        Parameters:
        -----------
        moment_series : pd.Series
            Series of moment values
        percentile_lookback : int
            Historical lookback window for percentile ranking
        
        Returns:
        --------
        pd.Series: Percentile ranks (0-100)
        """
        min_periods = int(percentile_lookback * self.config.min_periods_ratio)
        
        percentile_ranks = pd.Series(index=moment_series.index, dtype=float)
        
        for i in range(len(moment_series)):
            if i < min_periods:
                percentile_ranks.iloc[i] = np.nan
                continue
            
            # Current moment value
            current_value = moment_series.iloc[i]
            
            if pd.isna(current_value):
                percentile_ranks.iloc[i] = np.nan
                continue
            
            # Historical lookback
            start_idx = max(0, i - percentile_lookback + 1)
            historical_series = moment_series.iloc[start_idx:i+1]
            
            # Calculate percentile rank
            percentile_ranks.iloc[i] = self.moments_calculator.calculate_percentile_rank(
                current_value, historical_series
            )
        
        return percentile_ranks
    
    def calculate_sub_indicator(self,
                               prices: pd.Series,
                               returns: pd.Series,
                               moment_window: int,
                               percentile_lookback: int,
                               horizon_name: str) -> pd.DataFrame:
        """
        Calculate BRI sub-indicator for one time horizon
        
        Process:
        1. Calculate 4 moment values over moment_window
        2. Calculate percentile rank of each moment vs percentile_lookback
        3. Average the 4 percentile ranks
        4. Apply scaling factor
        
        Parameters:
        -----------
        prices : pd.Series
            Price series
        returns : pd.Series
            Returns series
        moment_window : int
            Window for calculating moment values
        percentile_lookback : int
            Historical lookback for percentile ranking
        horizon_name : str
            Name of horizon (e.g., 'short', 'mid', 'long')
        
        Returns:
        --------
        pd.DataFrame: Sub-indicator results
        """
        result = pd.DataFrame(index=returns.index)
        
        # 1. Calculate moment values with intermediate variables
        print(f"    Calculating moment values (window={moment_window})...")
        
        # Returns moment
        returns_moment = self.calculate_returns_moment(returns, moment_window)
        
        # Volatility moment
        volatility_moment = self.calculate_volatility_moment(returns, moment_window)
        
        # Momentum moment (with moving average)
        momentum_moment, moving_avg_price = self.calculate_momentum_moment(
            prices, moment_window
        )
        
        # Fragility moment (with realized vol and MAD)
        fragility_moment, realized_vol, realized_mad = self.calculate_fragility_moment(
            returns, moment_window
        )
        
        # Store moment values
        result[f'{horizon_name}_returns_value'] = returns_moment
        result[f'{horizon_name}_volatility_value'] = volatility_moment
        result[f'{horizon_name}_momentum_value'] = momentum_moment
        result[f'{horizon_name}_fragility_value'] = fragility_moment
        
        # Store intermediate variables (important for understanding calculations)
        result[f'{horizon_name}_moving_avg_price'] = moving_avg_price
        result[f'{horizon_name}_realized_vol'] = realized_vol
        result[f'{horizon_name}_realized_mad'] = realized_mad
        
        # 2. Calculate percentile ranks for each moment
        print(f"    Calculating percentile ranks (lookback={percentile_lookback})...")
        returns_pctile = self.calculate_moment_percentile_series(
            returns_moment, percentile_lookback
        )
        volatility_pctile = self.calculate_moment_percentile_series(
            volatility_moment, percentile_lookback
        )
        momentum_pctile = self.calculate_moment_percentile_series(
            momentum_moment, percentile_lookback
        )
        fragility_pctile = self.calculate_moment_percentile_series(
            fragility_moment, percentile_lookback
        )
        
        # Store percentile ranks
        result[f'{horizon_name}_returns_pctile'] = returns_pctile
        result[f'{horizon_name}_volatility_pctile'] = volatility_pctile
        result[f'{horizon_name}_momentum_pctile'] = momentum_pctile
        result[f'{horizon_name}_fragility_pctile'] = fragility_pctile
        
        # 3. Calculate weighted average of percentile ranks
        weights = self.config.weights
        avg_percentile = (
            weights.returns * returns_pctile +
            weights.volatility * volatility_pctile +
            weights.momentum * momentum_pctile +
            weights.fragility * fragility_pctile
        )
        
        result[f'{horizon_name}_avg_percentile'] = avg_percentile
        
        # 4. Calculate dynamic scaling factor
        print(f"    Calculating scaling factor...")
        
        if self.config.use_dynamic_scaling:
            # Use logistic transformation: scaling = 1 / (1 + exp(-k * normalized_return))
            # normalized_return = trailing_return / trailing_volatility
            
            # Normalize returns by volatility (Sharpe-like ratio)
            normalized_return = np.where(
                volatility_moment > 0,
                returns_moment / volatility_moment,
                0
            )
            
            # Apply logistic transformation
            # Higher positive returns → scaling approaches 1 (detect bubble)
            # Negative returns → scaling approaches 0 (ignore downtrends)
            k = self.config.scaling_steepness
            scaling_factor = 1.0 / (1.0 + np.exp(-k * normalized_return))
            
            result[f'{horizon_name}_scaling_factor'] = scaling_factor
        else:
            # Use static scaling factor (legacy behavior)
            scaling_factor = 0.5
            result[f'{horizon_name}_scaling_factor'] = scaling_factor
        
        # 5. Apply scaling factor to average percentile
        # Convert percentile (0-100) to [0,1], then scale
        indicator = (avg_percentile / 100.0) * scaling_factor
        result[f'{horizon_name}_indicator'] = indicator
        
        return result
    
    def calculate_full_bri(self,
                          price_data: pd.DataFrame,
                          price_column: str = 'Close',
                          asset_name: Optional[str] = None) -> pd.DataFrame:
        """
        Calculate complete BRI analysis using percentile rank methodology
        
        Parameters:
        -----------
        price_data : pd.DataFrame
            DataFrame with price data
        price_column : str
            Name of the price column to use
        asset_name : str, optional
            Name of the asset (for metadata)
        
        Returns:
        --------
        pd.DataFrame: Complete BRI analysis results
        """
        print(f"\n  Calculating BRI for {asset_name or 'asset'}...")
        
        # Prepare data
        prices, returns = self.prepare_data(price_data, price_column)
        
        results = pd.DataFrame(index=returns.index)
        results['price'] = prices
        results['returns'] = returns
        
        # Calculate each sub-indicator
        for horizon_name, moment_window_config in [
            ('short', self.config.windows.short_term),
            ('mid', self.config.windows.mid_term),
            ('long', self.config.windows.long_term)
        ]:
            print(f"  [{horizon_name.upper()}] moment_window={moment_window_config.moment_window}, percentile_lookback={moment_window_config.percentile_lookback}")
            
            sub_indicator_results = self.calculate_sub_indicator(
                prices,
                returns,
                moment_window_config.moment_window,
                moment_window_config.percentile_lookback,
                horizon_name
            )
            
            results = pd.concat([results, sub_indicator_results], axis=1)
        
        # Calculate composite BRI (average of three sub-indicators)
        results['composite_bri'] = (
            results['short_indicator'] +
            results['mid_indicator'] +
            results['long_indicator']
        ) / 3.0
        
        # Add metadata
        if asset_name:
            results.attrs['asset_name'] = asset_name
        results.attrs['config'] = self.config.to_dict()
        results.attrs['calculation_date'] = datetime.now().isoformat()
        results.attrs['methodology'] = 'percentile_rank'
        
        return results
    
    def get_current_status(self, bri_results: pd.DataFrame) -> Dict:
        """
        Get current bubble risk status summary
        
        Parameters:
        -----------
        bri_results : pd.DataFrame
            Results from calculate_full_bri
        
        Returns:
        --------
        dict: Current status summary
        """
        latest = bri_results.iloc[-1]
        
        status = {
            'date': bri_results.index[-1],
            'price': latest['price'],
            'composite_bri': latest['composite_bri'],
            'short_term': {
                'indicator': latest['short_indicator'],
                'avg_percentile': latest['short_avg_percentile']
            },
            'mid_term': {
                'indicator': latest['mid_indicator'],
                'avg_percentile': latest['mid_avg_percentile']
            },
            'long_term': {
                'indicator': latest['long_indicator'],
                'avg_percentile': latest['long_avg_percentile']
            }
        }
        
        return status
    
    def save_results(self,
                    bri_results: pd.DataFrame,
                    output_path: str,
                    include_moment_values: bool = True) -> None:
        """
        Save BRI results to CSV file
        
        Parameters:
        -----------
        bri_results : pd.DataFrame
            Results from calculate_full_bri
        output_path : str
            Path to save CSV file
        include_moment_values : bool
            Whether to include raw moment value columns
        """
        # Select columns to save
        if not include_moment_values:
            # Only save percentiles and indicators
            cols_to_save = ['price', 'returns']
            
            for horizon in ['short', 'mid', 'long']:
                cols_to_save.extend([
                    f'{horizon}_returns_pctile',
                    f'{horizon}_volatility_pctile',
                    f'{horizon}_momentum_pctile',
                    f'{horizon}_fragility_pctile',
                    f'{horizon}_avg_percentile',
                    f'{horizon}_indicator'
                ])
            
            cols_to_save.append('composite_bri')
            
            # Filter to existing columns
            cols_to_save = [col for col in cols_to_save if col in bri_results.columns]
            results_to_save = bri_results[cols_to_save]
        else:
            results_to_save = bri_results
        
        # Save to CSV
        results_to_save.to_csv(output_path)
        print(f"  [OK] BRI results saved to: {output_path}")
        print(f"  [OK] Rows: {len(results_to_save)}, Columns: {len(results_to_save.columns)}")

