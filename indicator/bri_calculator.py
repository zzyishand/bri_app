"""
BRI Calculator
Main module for calculating the Bubble Risk Indicator
Combines statistical moments across multiple time horizons
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, List, Tuple
from datetime import datetime
import warnings

from .bri_config import BRIConfig, DEFAULT_CONFIG
from .statistical_moments import StatisticalMoments


class BRICalculator:
    """
    Bubble Risk Indicator Calculator
    
    Calculates BRI scores based on four statistical moments:
    - Mean: Average returns indicator
    - Variance: Volatility/risk measure
    - Skewness: Distribution asymmetry
    - Kurtosis: Tail risk/extreme events
    
    Supports multiple time horizons (short/mid/long term)
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
                     price_column: str = 'Close') -> pd.Series:
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
        pd.Series: Returns series
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
        
        return returns
    
    def calculate_moments_single_window(self,
                                       returns: pd.Series,
                                       window: int) -> pd.DataFrame:
        """
        Calculate all four statistical moments for a single window
        
        Parameters:
        -----------
        returns : pd.Series
            Returns series
        window : int
            Rolling window size
        
        Returns:
        --------
        pd.DataFrame: DataFrame with normalized moments
        """
        min_periods = self.config.get_min_periods(window)
        
        # Calculate raw moments
        moments = self.moments_calculator.calculate_all_moments(
            returns, window, min_periods
        )
        
        # Normalize each moment
        normalized_moments = pd.DataFrame(index=moments.index)
        
        for col in moments.columns:
            normalized_moments[f'{col}_raw'] = moments[col]
            normalized_moments[f'{col}_norm'] = self.moments_calculator.normalize(
                moments[col],
                method=self.config.normalization_method
            )
        
        return normalized_moments
    
    def calculate_bri_score(self, normalized_moments: pd.DataFrame) -> pd.Series:
        """
        Calculate BRI composite score from normalized moments
        
        Parameters:
        -----------
        normalized_moments : pd.DataFrame
            DataFrame with normalized statistical moments
        
        Returns:
        --------
        pd.Series: BRI composite score
        """
        weights = self.config.weights
        
        # Extract normalized moments
        mean_norm = normalized_moments['mean_norm']
        var_norm = normalized_moments['variance_norm']
        skew_norm = normalized_moments['skewness_norm']
        kurt_norm = normalized_moments['kurtosis_norm']
        
        # Calculate weighted composite score
        bri_score = (
            weights.mean * mean_norm +
            weights.variance * var_norm +
            weights.skewness * skew_norm +
            weights.kurtosis * kurt_norm
        )
        
        return bri_score
    
    def classify_bubble_risk(self, bri_score: pd.Series) -> pd.Series:
        """
        Classify bubble risk level based on BRI score
        
        Parameters:
        -----------
        bri_score : pd.Series
            BRI score series
        
        Returns:
        --------
        pd.Series: Risk classification (0-3)
            0: Normal
            1: Warning
            2: Bubble
            3: Extreme Bubble
        """
        thresholds = self.config.thresholds
        
        risk_level = pd.Series(0, index=bri_score.index)
        risk_level[bri_score >= thresholds.warning] = 1
        risk_level[bri_score >= thresholds.bubble] = 2
        risk_level[bri_score >= thresholds.extreme] = 3
        
        return risk_level
    
    def calculate_single_horizon(self,
                                returns: pd.Series,
                                window: int,
                                horizon_name: str) -> pd.DataFrame:
        """
        Calculate BRI for a single time horizon
        
        Parameters:
        -----------
        returns : pd.Series
            Returns series
        window : int
            Rolling window size
        horizon_name : str
            Name of the time horizon (e.g., 'short', 'mid', 'long')
        
        Returns:
        --------
        pd.DataFrame: Complete BRI analysis for this horizon
        """
        # Calculate moments
        moments = self.calculate_moments_single_window(returns, window)
        
        # Calculate BRI score
        bri_score = self.calculate_bri_score(moments)
        
        # Classify risk
        risk_level = self.classify_bubble_risk(bri_score)
        
        # Combine results
        result = pd.DataFrame(index=returns.index)
        
        # Add moments with horizon prefix
        for col in ['mean_raw', 'variance_raw', 'skewness_raw', 'kurtosis_raw']:
            result[f'{horizon_name}_{col}'] = moments[col]
        
        for col in ['mean_norm', 'variance_norm', 'skewness_norm', 'kurtosis_norm']:
            result[f'{horizon_name}_{col}'] = moments[col]
        
        # Add BRI score and risk level
        result[f'{horizon_name}_bri'] = bri_score
        result[f'{horizon_name}_risk_level'] = risk_level
        
        return result
    
    def calculate_multi_horizon(self, returns: pd.Series) -> pd.DataFrame:
        """
        Calculate BRI for all time horizons (short/mid/long)
        
        Parameters:
        -----------
        returns : pd.Series
            Returns series
        
        Returns:
        --------
        pd.DataFrame: Complete BRI analysis for all horizons
        """
        results = pd.DataFrame(index=returns.index)
        
        # Short-term horizon
        short_results = self.calculate_single_horizon(
            returns,
            self.config.windows.short_term,
            'short'
        )
        results = pd.concat([results, short_results], axis=1)
        
        # Mid-term horizon
        mid_results = self.calculate_single_horizon(
            returns,
            self.config.windows.mid_term,
            'mid'
        )
        results = pd.concat([results, mid_results], axis=1)
        
        # Long-term horizon
        long_results = self.calculate_single_horizon(
            returns,
            self.config.windows.long_term,
            'long'
        )
        results = pd.concat([results, long_results], axis=1)
        
        return results
    
    def calculate_composite_bri(self, multi_horizon_results: pd.DataFrame) -> pd.Series:
        """
        Calculate composite BRI by averaging across all time horizons
        
        Parameters:
        -----------
        multi_horizon_results : pd.DataFrame
            Results from calculate_multi_horizon
        
        Returns:
        --------
        pd.Series: Composite BRI score
        """
        # Average BRI scores across horizons
        composite_bri = (
            multi_horizon_results['short_bri'] +
            multi_horizon_results['mid_bri'] +
            multi_horizon_results['long_bri']
        ) / 3
        
        return composite_bri
    
    def calculate_full_bri(self, 
                          price_data: pd.DataFrame,
                          price_column: str = 'Close',
                          asset_name: Optional[str] = None) -> pd.DataFrame:
        """
        Calculate complete BRI analysis
        
        This is the main method that performs all calculations:
        1. Prepare returns
        2. Calculate moments for all horizons
        3. Calculate BRI scores
        4. Classify risk levels
        5. Calculate composite BRI
        
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
        # Prepare data
        returns = self.prepare_data(price_data, price_column)
        
        # Calculate multi-horizon BRI
        results = self.calculate_multi_horizon(returns)
        
        # Add composite BRI
        results['composite_bri'] = self.calculate_composite_bri(results)
        results['composite_risk_level'] = self.classify_bubble_risk(results['composite_bri'])
        
        # Add returns and prices for reference
        results['price'] = price_data[price_column]
        results['returns'] = returns
        
        # Add metadata
        if asset_name:
            results.attrs['asset_name'] = asset_name
        results.attrs['config'] = self.config.to_dict()
        results.attrs['calculation_date'] = datetime.now().isoformat()
        
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
        
        risk_labels = {
            0: 'Normal',
            1: 'Warning',
            2: 'Bubble',
            3: 'Extreme Bubble'
        }
        
        status = {
            'date': bri_results.index[-1],
            'price': latest['price'],
            'composite_bri': latest['composite_bri'],
            'composite_risk': risk_labels.get(int(latest['composite_risk_level']), 'Unknown'),
            'short_term': {
                'bri': latest['short_bri'],
                'risk': risk_labels.get(int(latest['short_risk_level']), 'Unknown')
            },
            'mid_term': {
                'bri': latest['mid_bri'],
                'risk': risk_labels.get(int(latest['mid_risk_level']), 'Unknown')
            },
            'long_term': {
                'bri': latest['long_bri'],
                'risk': risk_labels.get(int(latest['long_risk_level']), 'Unknown')
            }
        }
        
        return status
    
    def save_results(self,
                    bri_results: pd.DataFrame,
                    output_path: str,
                    include_raw_moments: bool = True) -> None:
        """
        Save BRI results to CSV file
        
        Parameters:
        -----------
        bri_results : pd.DataFrame
            Results from calculate_full_bri
        output_path : str
            Path to save CSV file
        include_raw_moments : bool
            Whether to include raw moment columns
        """
        # Select columns to save
        if include_raw_moments:
            results_to_save = bri_results
        else:
            # Only save normalized moments, BRI scores, and risk levels
            cols_to_save = ['price', 'returns']
            
            # Add normalized moments and BRI for each horizon
            for horizon in ['short', 'mid', 'long']:
                cols_to_save.extend([
                    f'{horizon}_mean_norm',
                    f'{horizon}_variance_norm',
                    f'{horizon}_skewness_norm',
                    f'{horizon}_kurtosis_norm',
                    f'{horizon}_bri',
                    f'{horizon}_risk_level'
                ])
            
            # Add composite
            cols_to_save.extend(['composite_bri', 'composite_risk_level'])
            
            # Filter to existing columns
            cols_to_save = [col for col in cols_to_save if col in bri_results.columns]
            results_to_save = bri_results[cols_to_save]
        
        # Save to CSV
        results_to_save.to_csv(output_path)
        print(f"[OK] BRI results saved to: {output_path}")
        print(f"[OK] Rows: {len(results_to_save)}, Columns: {len(results_to_save.columns)}")

