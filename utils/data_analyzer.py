"""
Data Analysis Utilities
Common operations for data processing and analysis
"""

import pandas as pd
import numpy as np
from typing import Any, Dict, List, Optional, Union
import logging

logger = logging.getLogger(__name__)


def calculate_sum(df: pd.DataFrame, column_name: str, filter_condition: Optional[pd.Series] = None) -> float:
    """
    Calculate sum of a numeric column
    
    Args:
        df: Input DataFrame
        column_name: Name of column to sum
        filter_condition: Optional boolean Series for filtering
        
    Returns:
        Sum as float
    """
    try:
        if filter_condition is not None:
            filtered_df = df[filter_condition]
        else:
            filtered_df = df
        
        result = filtered_df[column_name].sum()
        logger.info(f"Sum of {column_name}: {result}")
        return float(result)
        
    except Exception as e:
        logger.error(f"Error calculating sum: {e}")
        raise


def count_rows(df: pd.DataFrame, filter_condition: Optional[pd.Series] = None) -> int:
    """
    Count rows in DataFrame with optional filter
    
    Args:
        df: Input DataFrame
        filter_condition: Optional boolean Series for filtering
        
    Returns:
        Count as integer
    """
    try:
        if filter_condition is not None:
            result = df[filter_condition].shape[0]
        else:
            result = df.shape[0]
        
        logger.info(f"Row count: {result}")
        return int(result)
        
    except Exception as e:
        logger.error(f"Error counting rows: {e}")
        raise


def aggregate_stats(df: pd.DataFrame, group_by: Union[str, List[str]], 
                    agg_func: Union[str, Dict[str, str]]) -> Dict[str, Any]:
    """
    Group by columns and apply aggregation functions
    
    Args:
        df: Input DataFrame
        group_by: Column(s) to group by
        agg_func: Aggregation function(s) - 'sum', 'mean', 'count', etc.
                  Can be a dict mapping column names to functions
        
    Returns:
        Dictionary with aggregated results
    """
    try:
        grouped = df.groupby(group_by)
        
        if isinstance(agg_func, str):
            result = grouped.agg(agg_func)
        else:
            result = grouped.agg(agg_func)
        
        # Convert to JSON-serializable format
        result_dict = result.to_dict()
        
        logger.info(f"Aggregation completed: {len(result)} groups")
        return result_dict
        
    except Exception as e:
        logger.error(f"Error in aggregation: {e}")
        raise


def find_max_min(df: pd.DataFrame, column_name: str) -> Dict[str, Any]:
    """
    Find maximum and minimum values in a column
    
    Args:
        df: Input DataFrame
        column_name: Name of column
        
    Returns:
        Dictionary with 'max' and 'min' values
    """
    try:
        max_val = df[column_name].max()
        min_val = df[column_name].min()
        
        # Find rows with max and min values
        max_row = df[df[column_name] == max_val].iloc[0].to_dict()
        min_row = df[df[column_name] == min_val].iloc[0].to_dict()
        
        result = {
            "max": float(max_val) if pd.api.types.is_numeric_dtype(df[column_name]) else str(max_val),
            "min": float(min_val) if pd.api.types.is_numeric_dtype(df[column_name]) else str(min_val),
            "max_row": max_row,
            "min_row": min_row
        }
        
        logger.info(f"Max: {max_val}, Min: {min_val}")
        return result
        
    except Exception as e:
        logger.error(f"Error finding max/min: {e}")
        raise


def calculate_mean(df: pd.DataFrame, column_name: str, filter_condition: Optional[pd.Series] = None) -> float:
    """
    Calculate mean of a numeric column
    
    Args:
        df: Input DataFrame
        column_name: Name of column
        filter_condition: Optional boolean Series for filtering
        
    Returns:
        Mean as float
    """
    try:
        if filter_condition is not None:
            filtered_df = df[filter_condition]
        else:
            filtered_df = df
        
        result = filtered_df[column_name].mean()
        logger.info(f"Mean of {column_name}: {result}")
        return float(result)
        
    except Exception as e:
        logger.error(f"Error calculating mean: {e}")
        raise


def calculate_median(df: pd.DataFrame, column_name: str) -> float:
    """
    Calculate median of a numeric column
    
    Args:
        df: Input DataFrame
        column_name: Name of column
        
    Returns:
        Median as float
    """
    try:
        result = df[column_name].median()
        logger.info(f"Median of {column_name}: {result}")
        return float(result)
        
    except Exception as e:
        logger.error(f"Error calculating median: {e}")
        raise


def calculate_std(df: pd.DataFrame, column_name: str) -> float:
    """
    Calculate standard deviation of a numeric column
    
    Args:
        df: Input DataFrame
        column_name: Name of column
        
    Returns:
        Standard deviation as float
    """
    try:
        result = df[column_name].std()
        logger.info(f"Std dev of {column_name}: {result}")
        return float(result)
        
    except Exception as e:
        logger.error(f"Error calculating std: {e}")
        raise


def value_counts(df: pd.DataFrame, column_name: str) -> Dict[str, int]:
    """
    Count unique values in a column
    
    Args:
        df: Input DataFrame
        column_name: Name of column
        
    Returns:
        Dictionary mapping values to counts
    """
    try:
        counts = df[column_name].value_counts().to_dict()
        # Convert keys to strings for JSON serialization
        result = {str(k): int(v) for k, v in counts.items()}
        
        logger.info(f"Value counts for {column_name}: {len(result)} unique values")
        return result
        
    except Exception as e:
        logger.error(f"Error calculating value counts: {e}")
        raise


def filter_dataframe(df: pd.DataFrame, conditions: Dict[str, Any]) -> pd.DataFrame:
    """
    Filter DataFrame based on multiple conditions
    
    Args:
        df: Input DataFrame
        conditions: Dictionary of column: value pairs for filtering
        
    Returns:
        Filtered DataFrame
    """
    try:
        filtered = df.copy()
        
        for column, value in conditions.items():
            if isinstance(value, (list, tuple)):
                # Filter for values in list
                filtered = filtered[filtered[column].isin(value)]
            else:
                # Exact match
                filtered = filtered[filtered[column] == value]
        
        logger.info(f"Filtered DataFrame: {filtered.shape[0]} rows remaining")
        return filtered
        
    except Exception as e:
        logger.error(f"Error filtering DataFrame: {e}")
        raise


def get_column_unique_values(df: pd.DataFrame, column_name: str) -> List[Any]:
    """
    Get unique values in a column
    
    Args:
        df: Input DataFrame
        column_name: Name of column
        
    Returns:
        List of unique values
    """
    try:
        unique_vals = df[column_name].unique().tolist()
        logger.info(f"Unique values in {column_name}: {len(unique_vals)}")
        return unique_vals
        
    except Exception as e:
        logger.error(f"Error getting unique values: {e}")
        raise
