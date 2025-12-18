"""
Utility Functions for E-Commerce Analysis
Helper functions for data loading, configuration, logging, and common operations

Author: Hamza Khan
Date: December 18, 2024
"""

import pandas as pd
import yaml
from pathlib import Path
from loguru import logger
from typing import Dict, Any, List, Union
import sys


def load_config(config_path: str = "config/config.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file
    
    Parameters:
    -----------
    config_path : str
        Path to configuration file
    
    Returns:
    --------
    dict : Configuration dictionary
    
    Example:
    --------
    >>> config = load_config()
    >>> data_path = config['paths']['data']['raw']
    """
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        logger.info(f"✅ Configuration loaded from {config_path}")
        return config
    except FileNotFoundError:
        logger.error(f"❌ Configuration file not found: {config_path}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"❌ Error parsing YAML: {e}")
        raise


def setup_logging(log_file: str = "logs/analysis.log", level: str = "INFO") -> None:
    """
    Configure logging for the project
    
    Parameters:
    -----------
    log_file : str
        Path to log file
    level : str
        Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Remove default logger
    logger.remove()
    
    # Add console logger
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level=level,
        colorize=True
    )
    
    # Add file logger
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
        level=level,
        rotation="10 MB",
        retention="30 days"
    )
    
    logger.info(f"✅ Logging configured: {log_file}")


def load_data(file_path: str, **kwargs) -> pd.DataFrame:
    """
    Load data from CSV file with error handling
    
    Parameters:
    -----------
    file_path : str
        Path to CSV file
    **kwargs : Additional arguments for pd.read_csv
    
    Returns:
    --------
    pd.DataFrame : Loaded dataframe
    
    Example:
    --------
    >>> df = load_data('data/raw_data.csv', encoding='latin1')
    """
    try:
        df = pd.read_csv(file_path, **kwargs)
        logger.info(f"✅ Data loaded: {file_path} ({df.shape[0]:,} rows × {df.shape[1]} columns)")
        return df
    except FileNotFoundError:
        logger.error(f"❌ File not found: {file_path}")
        raise
    except Exception as e:
        logger.error(f"❌ Error loading data: {e}")
        raise


def save_data(df: pd.DataFrame, file_path: str, **kwargs) -> None:
    """
    Save dataframe to CSV with logging
    
    Parameters:
    -----------
    df : pd.DataFrame
        Dataframe to save
    file_path : str
        Output file path
    **kwargs : Additional arguments for df.to_csv
    """
    try:
        # Create directory if it doesn't exist
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        df.to_csv(file_path, index=False, **kwargs)
        logger.info(f"✅ Data saved: {file_path} ({df.shape[0]:,} rows × {df.shape[1]} columns)")
    except Exception as e:
        logger.error(f"❌ Error saving data: {e}")
        raise


def print_dataframe_info(df: pd.DataFrame, name: str = "DataFrame") -> None:
    """
    Print comprehensive dataframe information
    
    Parameters:
    -----------
    df : pd.DataFrame
        Dataframe to analyze
    name : str
        Name of the dataframe for logging
    """
    logger.info(f"\n{'='*80}")
    logger.info(f"{name.upper()} INFORMATION")
    logger.info(f"{'='*80}")
    logger.info(f"Shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
    logger.info(f"Memory Usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    logger.info(f"\nData Types:\n{df.dtypes.value_counts()}")
    
    # Missing values
    missing = df.isnull().sum()
    if missing.sum() > 0:
        missing_df = pd.DataFrame({
            'Column': missing[missing > 0].index,
            'Missing': missing[missing > 0].values,
            'Percentage': (missing[missing > 0] / len(df) * 100).round(2)
        })
        logger.info(f"\n⚠️  Missing Values:\n{missing_df.to_string(index=False)}")
    else:
        logger.info("\n✅ No missing values")
    
    logger.info(f"{'='*80}\n")


def get_data_quality_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate comprehensive data quality metrics
    
    Parameters:
    -----------
    df : pd.DataFrame
        Dataframe to analyze
    
    Returns:
    --------
    dict : Data quality metrics
    """
    metrics = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'memory_mb': df.memory_usage(deep=True).sum() / 1024**2,
        'missing_values': df.isnull().sum().sum(),
        'missing_percentage': (df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100),
        'duplicates': df.duplicated().sum(),
        'duplicate_percentage': (df.duplicated().sum() / len(df) * 100),
        'numeric_columns': len(df.select_dtypes(include=['number']).columns),
        'categorical_columns': len(df.select_dtypes(include=['object']).columns),
        'datetime_columns': len(df.select_dtypes(include=['datetime']).columns),
    }
    
    return metrics


def format_currency(value: float, currency: str = "£") -> str:
    """
    Format number as currency
    
    Parameters:
    -----------
    value : float
        Numeric value
    currency : str
        Currency symbol
    
    Returns:
    --------
    str : Formatted currency string
    
    Example:
    --------
    >>> format_currency(1234.56)
    '£1,234.56'
    """
    return f"{currency}{value:,.2f}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Format number as percentage
    
    Parameters:
    -----------
    value : float
        Numeric value (0.25 = 25%)
    decimals : int
        Number of decimal places
    
    Returns:
    --------
    str : Formatted percentage string
    
    Example:
    --------
    >>> format_percentage(0.7944)
    '79.4%'
    """
    return f"{value * 100:.{decimals}f}%"


def validate_date_range(df: pd.DataFrame, date_column: str, 
                         start_date: str, end_date: str) -> bool:
    """
    Validate if dataframe date range matches expected range
    
    Parameters:
    -----------
    df : pd.DataFrame
        Dataframe with date column
    date_column : str
        Name of date column
    start_date : str
        Expected start date (YYYY-MM-DD)
    end_date : str
        Expected end date (YYYY-MM-DD)
    
    Returns:
    --------
    bool : True if range matches
    """
    df[date_column] = pd.to_datetime(df[date_column])
    actual_start = df[date_column].min()
    actual_end = df[date_column].max()
    
    expected_start = pd.to_datetime(start_date)
    expected_end = pd.to_datetime(end_date)
    
    if actual_start.date() == expected_start.date() and actual_end.date() == expected_end.date():
        logger.info(f"✅ Date range validated: {actual_start.date()} to {actual_end.date()}")
        return True
    else:
        logger.warning(f"⚠️  Date range mismatch:")
        logger.warning(f"   Expected: {expected_start.date()} to {expected_end.date()}")
        logger.warning(f"   Actual:   {actual_start.date()} to {actual_end.date()}")
        return False


def create_directory_structure(base_path: str = ".") -> None:
    """
    Create project directory structure if it doesn't exist
    
    Parameters:
    -----------
    base_path : str
        Base project path
    """
    directories = [
        "data",
        "notebooks",
        "src",
        "tests",
        "sql",
        "scripts",
        "docs",
        "docs/charts",
        "docs/reports",
        "models",
        "config",
        "logs"
    ]
    
    for directory in directories:
        path = Path(base_path) / directory
        path.mkdir(parents=True, exist_ok=True)
    
    logger.info("✅ Directory structure created")


if __name__ == "__main__":
    # Example usage
    setup_logging()
    config = load_config()
    print(f"Project: {config['project']['name']}")
    print(f"Version: {config['project']['version']}")
