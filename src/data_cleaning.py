"""
Data Cleaning Functions for E-Commerce Analysis
Reusable functions for data cleaning, validation, and preprocessing

Author: Hamza Khan
Date: December 18, 2024
"""

import pandas as pd
import numpy as np
from loguru import logger
from typing import Tuple, List, Dict, Any


def remove_cancelled_orders(df: pd.DataFrame, invoice_column: str = 'InvoiceNo',
                             cancelled_prefix: str = 'C') -> pd.DataFrame:
    """
    Remove cancelled orders from dataset
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe
    invoice_column : str
        Name of invoice column
    cancelled_prefix : str
        Prefix indicating cancelled orders
    
    Returns:
    --------
    pd.DataFrame : Dataframe without cancelled orders
    
    Example:
    --------
    >>> df_clean = remove_cancelled_orders(df)
    """
    original_rows = len(df)
    cancelled_mask = df[invoice_column].astype(str).str.startswith(cancelled_prefix)
    cancelled_count = cancelled_mask.sum()
    
    df_clean = df[~cancelled_mask].copy()
    
    logger.info(f"🔍 Cancelled orders removed: {cancelled_count:,} ({cancelled_count/original_rows*100:.2f}%)")
    logger.info(f"✅ Remaining rows: {len(df_clean):,}")
    
    return df_clean


def remove_missing_values(df: pd.DataFrame, columns: List[str],
                          how: str = 'any') -> pd.DataFrame:
    """
    Remove rows with missing values in specified columns
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe
    columns : list
        List of columns to check for missing values
    how : str
        'any' or 'all' (same as pandas dropna)
    
    Returns:
    --------
    pd.DataFrame : Dataframe without missing values
    
    Example:
    --------
    >>> df_clean = remove_missing_values(df, ['Description', 'CustomerID'])
    """
    original_rows = len(df)
    
    df_clean = df.dropna(subset=columns, how=how).copy()
    
    removed = original_rows - len(df_clean)
    logger.info(f"🔍 Rows with missing values removed: {removed:,} ({removed/original_rows*100:.2f}%)")
    logger.info(f"✅ Remaining rows: {len(df_clean):,}")
    
    return df_clean


def remove_invalid_quantities(df: pd.DataFrame, quantity_column: str = 'Quantity',
                               min_quantity: int = 1) -> pd.DataFrame:
    """
    Remove rows with invalid (negative or zero) quantities
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe
    quantity_column : str
        Name of quantity column
    min_quantity : int
        Minimum valid quantity
    
    Returns:
    --------
    pd.DataFrame : Dataframe with valid quantities only
    
    Example:
    --------
    >>> df_clean = remove_invalid_quantities(df, min_quantity=1)
    """
    original_rows = len(df)
    
    negative = (df[quantity_column] < 0).sum()
    zero = (df[quantity_column] == 0).sum()
    
    df_clean = df[df[quantity_column] >= min_quantity].copy()
    
    removed = original_rows - len(df_clean)
    logger.info(f"🔍 Invalid quantities removed: {removed:,}")
    logger.info(f"   • Negative: {negative:,}")
    logger.info(f"   • Zero: {zero:,}")
    logger.info(f"✅ Remaining rows: {len(df_clean):,}")
    
    return df_clean


def remove_invalid_prices(df: pd.DataFrame, price_column: str = 'UnitPrice',
                          min_price: float = 0.01, max_price: float = 100000) -> pd.DataFrame:
    """
    Remove rows with invalid prices
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe
    price_column : str
        Name of price column
    min_price : float
        Minimum valid price
    max_price : float
        Maximum valid price
    
    Returns:
    --------
    pd.DataFrame : Dataframe with valid prices only
    
    Example:
    --------
    >>> df_clean = remove_invalid_prices(df, min_price=0.01)
    """
    original_rows = len(df)
    
    negative = (df[price_column] < 0).sum()
    zero = (df[price_column] == 0).sum()
    too_high = (df[price_column] > max_price).sum()
    
    df_clean = df[
        (df[price_column] >= min_price) & 
        (df[price_column] <= max_price)
    ].copy()
    
    removed = original_rows - len(df_clean)
    logger.info(f"🔍 Invalid prices removed: {removed:,}")
    logger.info(f"   • Negative: {negative:,}")
    logger.info(f"   • Zero: {zero:,}")
    logger.info(f"   • Too high (>${max_price}): {too_high:,}")
    logger.info(f"✅ Remaining rows: {len(df_clean):,}")
    
    return df_clean


def remove_duplicates(df: pd.DataFrame, subset: List[str] = None) -> pd.DataFrame:
    """
    Remove duplicate rows
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe
    subset : list
        List of columns to check for duplicates (None = all columns)
    
    Returns:
    --------
    pd.DataFrame : Dataframe without duplicates
    
    Example:
    --------
    >>> df_clean = remove_duplicates(df)
    """
    original_rows = len(df)
    duplicates = df.duplicated(subset=subset).sum()
    
    df_clean = df.drop_duplicates(subset=subset).copy()
    
    logger.info(f"🔍 Duplicate rows removed: {duplicates:,} ({duplicates/original_rows*100:.2f}%)")
    logger.info(f"✅ Remaining rows: {len(df_clean):,}")
    
    return df_clean


def convert_data_types(df: pd.DataFrame, type_mappings: Dict[str, str]) -> pd.DataFrame:
    """
    Convert column data types
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe
    type_mappings : dict
        Dictionary mapping column names to desired types
        Example: {'InvoiceDate': 'datetime64', 'CustomerID': 'int64'}
    
    Returns:
    --------
    pd.DataFrame : Dataframe with converted types
    
    Example:
    --------
    >>> df = convert_data_types(df, {'InvoiceDate': 'datetime64'})
    """
    df_clean = df.copy()
    
    for column, dtype in type_mappings.items():
        if column in df_clean.columns:
            try:
                if dtype == 'datetime64':
                    df_clean[column] = pd.to_datetime(df_clean[column])
                else:
                    df_clean[column] = df_clean[column].astype(dtype)
                logger.info(f"✅ {column} converted to {dtype}")
            except Exception as e:
                logger.error(f"❌ Error converting {column} to {dtype}: {e}")
        else:
            logger.warning(f"⚠️  Column not found: {column}")
    
    return df_clean


def standardize_column_names(df: pd.DataFrame, style: str = 'snake_case') -> pd.DataFrame:
    """
    Standardize column names to consistent format
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe
    style : str
        'snake_case', 'camelCase', or 'PascalCase'
    
    Returns:
    --------
    pd.DataFrame : Dataframe with standardized column names
    
    Example:
    --------
    >>> df = standardize_column_names(df, style='snake_case')
    """
    df_clean = df.copy()
    
    if style == 'snake_case':
        df_clean.columns = df_clean.columns.str.replace(' ', '_').str.lower()
    elif style == 'camelCase':
        df_clean.columns = df_clean.columns.str.replace(' ', '')
        df_clean.columns = [col[0].lower() + col[1:] for col in df_clean.columns]
    elif style == 'PascalCase':
        df_clean.columns = df_clean.columns.str.replace(' ', '')
    
    logger.info(f"✅ Column names standardized to {style}")
    
    return df_clean


def filter_by_date_range(df: pd.DataFrame, date_column: str,
                          start_date: str, end_date: str) -> pd.DataFrame:
    """
    Filter dataframe by date range
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe
    date_column : str
        Name of date column
    start_date : str
        Start date (YYYY-MM-DD)
    end_date : str
        End date (YYYY-MM-DD)
    
    Returns:
    --------
    pd.DataFrame : Filtered dataframe
    
    Example:
    --------
    >>> df_filtered = filter_by_date_range(df, 'InvoiceDate', '2009-12-01', '2010-12-09')
    """
    original_rows = len(df)
    
    df[date_column] = pd.to_datetime(df[date_column])
    df_filtered = df[
        (df[date_column] >= start_date) & 
        (df[date_column] <= end_date)
    ].copy()
    
    removed = original_rows - len(df_filtered)
    logger.info(f"🔍 Rows outside date range removed: {removed:,}")
    logger.info(f"✅ Date range: {start_date} to {end_date}")
    logger.info(f"✅ Remaining rows: {len(df_filtered):,}")
    
    return df_filtered


def handle_outliers(df: pd.DataFrame, column: str, method: str = 'iqr',
                     threshold: float = 1.5, action: str = 'keep') -> pd.DataFrame:
    """
    Handle outliers in numeric column
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe
    column : str
        Column name to check for outliers
    method : str
        'iqr' (Interquartile Range) or 'zscore' (Z-score)
    threshold : float
        Threshold for outlier detection (1.5 for IQR, 3 for Z-score)
    action : str
        'keep', 'remove', or 'cap' (cap to threshold)
    
    Returns:
    --------
    pd.DataFrame : Dataframe with outliers handled
    
    Example:
    --------
    >>> df_clean = handle_outliers(df, 'UnitPrice', method='iqr', action='keep')
    """
    original_rows = len(df)
    df_clean = df.copy()
    
    if method == 'iqr':
        Q1 = df_clean[column].quantile(0.25)
        Q3 = df_clean[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        
        outliers = ((df_clean[column] < lower_bound) | (df_clean[column] > upper_bound)).sum()
        
        if action == 'remove':
            df_clean = df_clean[
                (df_clean[column] >= lower_bound) & 
                (df_clean[column] <= upper_bound)
            ]
        elif action == 'cap':
            df_clean[column] = df_clean[column].clip(lower_bound, upper_bound)
    
    elif method == 'zscore':
        from scipy import stats
        z_scores = np.abs(stats.zscore(df_clean[column].dropna()))
        outliers = (z_scores > threshold).sum()
        
        if action == 'remove':
            df_clean = df_clean[z_scores <= threshold]
        elif action == 'cap':
            # Cap at threshold z-score
            mean = df_clean[column].mean()
            std = df_clean[column].std()
            lower_bound = mean - threshold * std
            upper_bound = mean + threshold * std
            df_clean[column] = df_clean[column].clip(lower_bound, upper_bound)
    
    removed = original_rows - len(df_clean)
    
    logger.info(f"🔍 Outliers detected in {column}: {outliers:,}")
    logger.info(f"   Action: {action}")
    if action == 'remove':
        logger.info(f"   Rows removed: {removed:,}")
    logger.info(f"✅ Remaining rows: {len(df_clean):,}")
    
    return df_clean


def clean_ecommerce_data(df: pd.DataFrame, config: Dict[str, Any] = None) -> pd.DataFrame:
    """
    Complete data cleaning pipeline for e-commerce data
    
    Parameters:
    -----------
    df : pd.DataFrame
        Raw e-commerce dataframe
    config : dict
        Configuration dictionary (optional)
    
    Returns:
    --------
    pd.DataFrame : Cleaned dataframe
    
    Example:
    --------
    >>> df_clean = clean_ecommerce_data(df_raw)
    """
    logger.info("\n" + "="*80)
    logger.info("STARTING DATA CLEANING PIPELINE")
    logger.info("="*80)
    logger.info(f"Initial dataset: {len(df):,} rows × {len(df.columns)} columns\n")
    
    df_clean = df.copy()
    
    # Step 1: Remove cancelled orders
    df_clean = remove_cancelled_orders(df_clean)
    
    # Step 2: Convert data types
    df_clean = convert_data_types(df_clean, {'InvoiceDate': 'datetime64'})
    
    # Step 3: Remove missing descriptions
    df_clean = remove_missing_values(df_clean, ['Description'])
    
    # Step 4: Remove invalid quantities
    df_clean = remove_invalid_quantities(df_clean)
    
    # Step 5: Remove invalid prices
    df_clean = remove_invalid_prices(df_clean)
    
    # Step 6: Remove duplicates
    df_clean = remove_duplicates(df_clean)
    
    # Summary
    original_rows = len(df)
    final_rows = len(df_clean)
    removed = original_rows - final_rows
    retention_rate = (final_rows / original_rows) * 100
    
    logger.info("\n" + "="*80)
    logger.info("DATA CLEANING SUMMARY")
    logger.info("="*80)
    logger.info(f"📊 Original dataset: {original_rows:,} rows")
    logger.info(f"📊 Cleaned dataset: {final_rows:,} rows")
    logger.info(f"📊 Rows removed: {removed:,} ({(removed/original_rows)*100:.2f}%)")
    logger.info(f"📊 Data retention rate: {retention_rate:.2f}%")
    logger.info("="*80 + "\n")
    
    return df_clean


if __name__ == "__main__":
    # Example usage
    from utils import load_config, setup_logging, load_data
    
    setup_logging()
    config = load_config()
    
    # Load raw data
    df_raw = load_data(config['paths']['data']['raw'], encoding='latin1')
    
    # Clean data
    df_clean = clean_ecommerce_data(df_raw, config)
    
    # Save cleaned data
    from utils import save_data
    save_data(df_clean, config['paths']['data']['cleaned'])
