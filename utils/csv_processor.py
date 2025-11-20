"""
CSV and Excel Processing Utilities
Handles loading and cleaning CSV/Excel files
"""

import pandas as pd
import requests
from io import StringIO, BytesIO
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


def load_csv(url: str, **kwargs) -> pd.DataFrame:
    """
    Load CSV file from URL directly into pandas DataFrame
    
    Args:
        url: URL to CSV file
        **kwargs: Additional arguments to pass to pd.read_csv
        
    Returns:
        pandas DataFrame
    """
    try:
        logger.info(f"Loading CSV from {url}")
        
        # Download CSV content
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Parse CSV
        csv_content = StringIO(response.text)
        df = pd.read_csv(csv_content, **kwargs)
        
        logger.info(f"CSV loaded: {df.shape[0]} rows, {df.shape[1]} columns")
        return df
        
    except Exception as e:
        logger.error(f"Error loading CSV: {e}")
        raise


def load_excel(url: str, sheet_name: Optional[str] = None, **kwargs) -> pd.DataFrame:
    """
    Load Excel file from URL into pandas DataFrame
    
    Args:
        url: URL to Excel file
        sheet_name: Sheet name to load (default: first sheet)
        **kwargs: Additional arguments to pass to pd.read_excel
        
    Returns:
        pandas DataFrame
    """
    try:
        logger.info(f"Loading Excel from {url}")
        
        # Download Excel file
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Parse Excel
        excel_content = BytesIO(response.content)
        
        if sheet_name:
            df = pd.read_excel(excel_content, sheet_name=sheet_name, **kwargs)
        else:
            df = pd.read_excel(excel_content, **kwargs)
        
        logger.info(f"Excel loaded: {df.shape[0]} rows, {df.shape[1]} columns")
        return df
        
    except Exception as e:
        logger.error(f"Error loading Excel: {e}")
        raise


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean DataFrame by removing NaN values and converting types
    
    Args:
        df: Input DataFrame
        
    Returns:
        Cleaned DataFrame
    """
    try:
        logger.info("Cleaning DataFrame")
        
        # Create a copy to avoid modifying original
        df_clean = df.copy()
        
        # Strip whitespace from string columns
        for col in df_clean.select_dtypes(include=['object']).columns:
            df_clean[col] = df_clean[col].str.strip() if df_clean[col].dtype == 'object' else df_clean[col]
        
        # Convert numeric strings to numbers
        for col in df_clean.columns:
            try:
                # Try to convert to numeric
                df_clean[col] = pd.to_numeric(df_clean[col], errors='ignore')
            except:
                pass
        
        # Log cleaning results
        logger.info(f"Cleaned DataFrame: {df_clean.shape[0]} rows, {df_clean.shape[1]} columns")
        
        return df_clean
        
    except Exception as e:
        logger.error(f"Error cleaning data: {e}")
        return df


def load_data_from_url(url: str) -> pd.DataFrame:
    """
    Auto-detect file type and load data from URL
    
    Args:
        url: URL to data file
        
    Returns:
        pandas DataFrame
    """
    try:
        url_lower = url.lower()
        
        if url_lower.endswith('.csv'):
            return load_csv(url)
        elif url_lower.endswith(('.xlsx', '.xls')):
            return load_excel(url)
        else:
            # Try CSV first, then Excel
            try:
                return load_csv(url)
            except:
                return load_excel(url)
                
    except Exception as e:
        logger.error(f"Error loading data from URL: {e}")
        raise


def describe_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Get summary statistics for DataFrame
    
    Args:
        df: Input DataFrame
        
    Returns:
        Dictionary with summary statistics
    """
    try:
        return {
            "shape": df.shape,
            "columns": list(df.columns),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "null_counts": df.isnull().sum().to_dict(),
            "numeric_summary": df.describe().to_dict() if len(df.select_dtypes(include='number').columns) > 0 else {}
        }
    except Exception as e:
        logger.error(f"Error describing DataFrame: {e}")
        return {}
