"""
Unit Tests for Data Cleaning Module

Tests all functions in src/data_cleaning.py to ensure data quality
and business rule enforcement work correctly.

Run tests with:
    pytest tests/test_data_cleaning.py -v
    pytest tests/test_data_cleaning.py --cov=src.data_cleaning

Author: Data Analytics Team
Version: 1.0.0
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from src.data_cleaning import (
    remove_cancelled_orders,
    remove_missing_values,
    remove_invalid_quantities,
    remove_invalid_prices,
    remove_duplicates,
    convert_data_types,
    filter_by_date_range,
    handle_outliers,
    clean_ecommerce_data
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_data():
    """Create sample e-commerce data for testing"""
    data = {
        'InvoiceNo': ['536365', '536366', 'C536367', '536368', '536369', '536370'],
        'StockCode': ['85123A', '71053', '84406B', '84029G', '84029E', '22752'],
        'Description': ['WHITE HANGING HEART', 'WHITE METAL LANTERN', 'CREAM CUPID', 
                       'KNITTED UNION FLAG', None, 'RED RETROSPOT PLATE'],
        'Quantity': [6, 8, -1, 6, 0, 5],
        'InvoiceDate': [
            '2010-12-01 08:26:00',
            '2010-12-01 08:28:00',
            '2010-12-01 08:30:00',
            '2010-12-01 08:34:00',
            '2010-12-01 08:35:00',
            '2010-12-01 08:36:00'
        ],
        'UnitPrice': [2.55, 3.39, 2.75, 3.25, 0.0, -1.5],
        'CustomerID': [17850.0, 17850.0, 13047.0, np.nan, 17850.0, 17850.0],
        'Country': ['United Kingdom', 'United Kingdom', 'United Kingdom', 
                   'United Kingdom', 'United Kingdom', 'United Kingdom']
    }
    df = pd.DataFrame(data)
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    return df


@pytest.fixture
def sample_data_with_duplicates():
    """Create sample data with duplicate rows"""
    data = {
        'InvoiceNo': ['536365', '536365', '536366', '536367'],
        'StockCode': ['85123A', '85123A', '71053', '84406B'],
        'Quantity': [6, 6, 8, 5],
        'UnitPrice': [2.55, 2.55, 3.39, 2.75],
        'CustomerID': [17850.0, 17850.0, 17850.0, 13047.0],
        'InvoiceDate': pd.to_datetime(['2010-12-01'] * 4)
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_data_with_outliers():
    """Create sample data with outliers"""
    np.random.seed(42)
    data = {
        'Quantity': list(np.random.normal(10, 2, 95)) + [100, 150, 200, 250, 300],
        'UnitPrice': list(np.random.normal(5, 1, 95)) + [500, 600, 700, 800, 900]
    }
    return pd.DataFrame(data)


# ============================================================================
# TESTS: remove_cancelled_orders
# ============================================================================

def test_remove_cancelled_orders_basic(sample_data):
    """Test removal of cancelled orders with 'C' prefix"""
    df = remove_cancelled_orders(sample_data, invoice_col='InvoiceNo', cancelled_prefix='C')
    
    # Should have 5 rows (1 cancelled removed)
    assert len(df) == 5
    
    # No invoice numbers should start with 'C'
    assert not df['InvoiceNo'].str.startswith('C').any()
    
    # Cancelled invoice 'C536367' should be removed
    assert 'C536367' not in df['InvoiceNo'].values


def test_remove_cancelled_orders_custom_prefix(sample_data):
    """Test removal with custom prefix"""
    # Add custom prefix
    df = sample_data.copy()
    df.loc[0, 'InvoiceNo'] = 'X536365'
    
    result = remove_cancelled_orders(df, invoice_col='InvoiceNo', cancelled_prefix='X')
    
    # Should remove the 'X' prefixed invoice
    assert 'X536365' not in result['InvoiceNo'].values
    assert len(result) == len(df) - 1


def test_remove_cancelled_orders_no_cancelled(sample_data):
    """Test when no cancelled orders exist"""
    # Remove cancelled orders first
    df = sample_data[~sample_data['InvoiceNo'].str.startswith('C')].copy()
    
    result = remove_cancelled_orders(df, invoice_col='InvoiceNo')
    
    # Should return same dataframe
    assert len(result) == len(df)


# ============================================================================
# TESTS: remove_missing_values
# ============================================================================

def test_remove_missing_values_single_column(sample_data):
    """Test removal of rows with missing CustomerID"""
    df = remove_missing_values(sample_data, columns=['CustomerID'])
    
    # Should have 5 rows (1 with NaN CustomerID removed)
    assert len(df) == 5
    
    # No missing values in CustomerID
    assert not df['CustomerID'].isna().any()


def test_remove_missing_values_multiple_columns(sample_data):
    """Test removal with multiple columns"""
    df = remove_missing_values(sample_data, columns=['CustomerID', 'Description'])
    
    # Should remove rows with NaN in either column
    assert len(df) == 4
    
    # No missing values in specified columns
    assert not df['CustomerID'].isna().any()
    assert not df['Description'].isna().any()


def test_remove_missing_values_no_missing():
    """Test when no missing values exist"""
    df = pd.DataFrame({
        'A': [1, 2, 3],
        'B': [4, 5, 6]
    })
    
    result = remove_missing_values(df, columns=['A', 'B'])
    
    # Should return same dataframe
    assert len(result) == len(df)


# ============================================================================
# TESTS: remove_invalid_quantities
# ============================================================================

def test_remove_invalid_quantities_positive_only(sample_data):
    """Test removal of non-positive quantities"""
    df = remove_invalid_quantities(sample_data, quantity_col='Quantity', min_quantity=1)
    
    # Should have 4 rows (2 with Quantity <= 0 removed)
    assert len(df) == 4
    
    # All quantities should be >= 1
    assert (df['Quantity'] >= 1).all()


def test_remove_invalid_quantities_custom_threshold(sample_data):
    """Test with custom minimum quantity"""
    df = remove_invalid_quantities(sample_data, quantity_col='Quantity', min_quantity=5)
    
    # Should have 3 rows (Quantity >= 5)
    assert len(df) == 3
    
    # All quantities should be >= 5
    assert (df['Quantity'] >= 5).all()


def test_remove_invalid_quantities_zero_threshold():
    """Test with zero threshold (allow zero)"""
    df = pd.DataFrame({'Quantity': [-5, 0, 5, 10]})
    
    result = remove_invalid_quantities(df, quantity_col='Quantity', min_quantity=0)
    
    # Should remove only negative values
    assert len(result) == 3
    assert (result['Quantity'] >= 0).all()


# ============================================================================
# TESTS: remove_invalid_prices
# ============================================================================

def test_remove_invalid_prices_positive_only(sample_data):
    """Test removal of non-positive prices"""
    df = remove_invalid_prices(sample_data, price_col='UnitPrice', min_price=0.01)
    
    # Should have 4 rows (2 with invalid prices removed)
    assert len(df) == 4
    
    # All prices should be >= 0.01
    assert (df['UnitPrice'] >= 0.01).all()


def test_remove_invalid_prices_with_max_price(sample_data):
    """Test removal with both min and max price"""
    df = remove_invalid_prices(
        sample_data, 
        price_col='UnitPrice', 
        min_price=2.0, 
        max_price=3.5
    )
    
    # Should have 3 rows (within price range)
    assert len(df) == 3
    
    # All prices should be in range
    assert (df['UnitPrice'] >= 2.0).all()
    assert (df['UnitPrice'] <= 3.5).all()


# ============================================================================
# TESTS: remove_duplicates
# ============================================================================

def test_remove_duplicates_exact(sample_data_with_duplicates):
    """Test removal of exact duplicate rows"""
    df = remove_duplicates(sample_data_with_duplicates)
    
    # Should have 3 unique rows (1 duplicate removed)
    assert len(df) == 3
    
    # No duplicates should remain
    assert not df.duplicated().any()


def test_remove_duplicates_subset():
    """Test removal based on subset of columns"""
    df = pd.DataFrame({
        'A': [1, 1, 2, 3],
        'B': [10, 20, 30, 40],
        'C': [100, 200, 300, 400]
    })
    
    result = remove_duplicates(df, subset=['A'])
    
    # Should have 3 rows (duplicate 'A' value removed)
    assert len(result) == 3
    
    # Column A should have unique values
    assert result['A'].nunique() == len(result)


def test_remove_duplicates_keep_last():
    """Test keeping last occurrence of duplicates"""
    df = pd.DataFrame({
        'A': [1, 1, 2],
        'B': [10, 20, 30]
    })
    
    result = remove_duplicates(df, keep='last')
    
    # Should keep the second occurrence (B=20)
    assert len(result) == 2
    assert 20 in result['B'].values
    assert 10 not in result['B'].values


# ============================================================================
# TESTS: convert_data_types
# ============================================================================

def test_convert_data_types_basic(sample_data):
    """Test data type conversions"""
    # Convert to string first to test conversion
    df = sample_data.copy()
    df['Quantity'] = df['Quantity'].astype(str)
    df['UnitPrice'] = df['UnitPrice'].astype(str)
    
    type_mapping = {
        'Quantity': int,
        'UnitPrice': float,
        'InvoiceDate': 'datetime64[ns]'
    }
    
    result = convert_data_types(df, type_mapping)
    
    # Check data types
    assert result['Quantity'].dtype == int
    assert result['UnitPrice'].dtype == float
    assert pd.api.types.is_datetime64_any_dtype(result['InvoiceDate'])


def test_convert_data_types_handles_errors():
    """Test error handling in type conversion"""
    df = pd.DataFrame({
        'A': ['1', 'invalid', '3'],
        'B': ['1.5', '2.5', 'bad']
    })
    
    type_mapping = {'A': int, 'B': float}
    
    # Should handle errors gracefully (with coerce)
    result = convert_data_types(df, type_mapping)
    
    # Should have NaN for invalid conversions
    assert result['A'].isna().sum() > 0
    assert result['B'].isna().sum() > 0


# ============================================================================
# TESTS: filter_by_date_range
# ============================================================================

def test_filter_by_date_range_basic():
    """Test date range filtering"""
    df = pd.DataFrame({
        'Date': pd.date_range('2010-01-01', periods=10, freq='D'),
        'Value': range(10)
    })
    
    result = filter_by_date_range(
        df, 
        date_col='Date',
        start_date='2010-01-03',
        end_date='2010-01-07'
    )
    
    # Should have 5 rows (days 3-7)
    assert len(result) == 5
    
    # Dates should be within range
    assert result['Date'].min() >= pd.to_datetime('2010-01-03')
    assert result['Date'].max() <= pd.to_datetime('2010-01-07')


def test_filter_by_date_range_start_only():
    """Test filtering with only start date"""
    df = pd.DataFrame({
        'Date': pd.date_range('2010-01-01', periods=10, freq='D'),
        'Value': range(10)
    })
    
    result = filter_by_date_range(df, date_col='Date', start_date='2010-01-06')
    
    # Should have 5 rows (days 6-10)
    assert len(result) == 5
    assert result['Date'].min() >= pd.to_datetime('2010-01-06')


def test_filter_by_date_range_end_only():
    """Test filtering with only end date"""
    df = pd.DataFrame({
        'Date': pd.date_range('2010-01-01', periods=10, freq='D'),
        'Value': range(10)
    })
    
    result = filter_by_date_range(df, date_col='Date', end_date='2010-01-05')
    
    # Should have 5 rows (days 1-5)
    assert len(result) == 5
    assert result['Date'].max() <= pd.to_datetime('2010-01-05')


# ============================================================================
# TESTS: handle_outliers
# ============================================================================

def test_handle_outliers_iqr_remove(sample_data_with_outliers):
    """Test IQR method with removal"""
    df = handle_outliers(
        sample_data_with_outliers,
        columns=['Quantity'],
        method='iqr',
        action='remove'
    )
    
    # Should have removed outliers
    assert len(df) < len(sample_data_with_outliers)
    
    # Max quantity should be less than outlier values
    assert df['Quantity'].max() < 100


def test_handle_outliers_iqr_cap(sample_data_with_outliers):
    """Test IQR method with capping"""
    original_len = len(sample_data_with_outliers)
    
    df = handle_outliers(
        sample_data_with_outliers,
        columns=['Quantity'],
        method='iqr',
        action='cap'
    )
    
    # Should keep all rows
    assert len(df) == original_len
    
    # Outliers should be capped
    q1 = sample_data_with_outliers['Quantity'].quantile(0.25)
    q3 = sample_data_with_outliers['Quantity'].quantile(0.75)
    iqr = q3 - q1
    upper_bound = q3 + 1.5 * iqr
    
    assert df['Quantity'].max() <= upper_bound


def test_handle_outliers_zscore():
    """Test z-score method"""
    np.random.seed(42)
    df = pd.DataFrame({
        'Value': list(np.random.normal(0, 1, 100)) + [10, -10]  # Outliers
    })
    
    result = handle_outliers(
        df,
        columns=['Value'],
        method='zscore',
        threshold=3,
        action='remove'
    )
    
    # Should remove extreme outliers (z-score > 3)
    assert len(result) < len(df)


def test_handle_outliers_keep():
    """Test keeping outliers (no action)"""
    df = sample_data_with_outliers
    original_len = len(df)
    
    result = handle_outliers(
        df,
        columns=['Quantity'],
        method='iqr',
        action='keep'
    )
    
    # Should keep all rows unchanged
    assert len(result) == original_len
    pd.testing.assert_frame_equal(result, df)


# ============================================================================
# TESTS: clean_ecommerce_data (Integration Test)
# ============================================================================

def test_clean_ecommerce_data_full_pipeline(sample_data):
    """Test complete cleaning pipeline"""
    df = clean_ecommerce_data(
        sample_data,
        cancelled_prefix='C',
        min_quantity=1,
        min_unit_price=0.01,
        required_columns=['CustomerID', 'Description'],
        date_column='InvoiceDate',
        handle_outliers_method='keep'
    )
    
    # Should have removed:
    # - 1 cancelled order (C prefix)
    # - 1 missing CustomerID
    # - 1 missing Description  
    # - 2 invalid quantities (<=0)
    # - 2 invalid prices (<=0)
    # Expected: might vary due to overlap, but should be < 6
    
    assert len(df) < len(sample_data)
    
    # All remaining data should be valid
    assert not df['InvoiceNo'].str.startswith('C').any()
    assert not df['CustomerID'].isna().any()
    assert not df['Description'].isna().any()
    assert (df['Quantity'] >= 1).all()
    assert (df['UnitPrice'] >= 0.01).all()


def test_clean_ecommerce_data_preserves_valid_data():
    """Test that valid data is preserved"""
    df = pd.DataFrame({
        'InvoiceNo': ['536365', '536366'],
        'StockCode': ['85123A', '71053'],
        'Description': ['Item 1', 'Item 2'],
        'Quantity': [5, 10],
        'InvoiceDate': pd.date_range('2010-12-01', periods=2),
        'UnitPrice': [2.55, 3.39],
        'CustomerID': [17850.0, 17851.0],
        'Country': ['UK', 'UK']
    })
    
    result = clean_ecommerce_data(
        df,
        cancelled_prefix='C',
        min_quantity=1,
        min_unit_price=0.01,
        required_columns=['CustomerID'],
        date_column='InvoiceDate'
    )
    
    # All valid rows should be preserved
    assert len(result) == 2


def test_clean_ecommerce_data_empty_result():
    """Test when all data is invalid"""
    df = pd.DataFrame({
        'InvoiceNo': ['C001', 'C002'],
        'Quantity': [-1, 0],
        'UnitPrice': [0, -1],
        'CustomerID': [np.nan, np.nan],
        'InvoiceDate': pd.date_range('2010-12-01', periods=2)
    })
    
    result = clean_ecommerce_data(
        df,
        cancelled_prefix='C',
        min_quantity=1,
        min_unit_price=0.01,
        required_columns=['CustomerID']
    )
    
    # Should return empty dataframe
    assert len(result) == 0


# ============================================================================
# EDGE CASES & ERROR HANDLING
# ============================================================================

def test_empty_dataframe_handling():
    """Test handling of empty dataframes"""
    df = pd.DataFrame()
    
    # Should handle gracefully without errors
    result = remove_cancelled_orders(df)
    assert len(result) == 0


def test_missing_column_handling():
    """Test error handling for missing columns"""
    df = pd.DataFrame({'A': [1, 2, 3]})
    
    with pytest.raises(KeyError):
        remove_cancelled_orders(df, invoice_col='NonExistentColumn')


def test_all_nulls_column():
    """Test handling of columns with all null values"""
    df = pd.DataFrame({
        'A': [np.nan, np.nan, np.nan],
        'B': [1, 2, 3]
    })
    
    result = remove_missing_values(df, columns=['A'])
    
    # Should remove all rows
    assert len(result) == 0


# ============================================================================
# PERFORMANCE TESTS (Optional)
# ============================================================================

@pytest.mark.slow
def test_large_dataset_performance():
    """Test performance with large dataset"""
    # Create large dataset (100K rows)
    n_rows = 100000
    df = pd.DataFrame({
        'InvoiceNo': [f'INV{i}' for i in range(n_rows)],
        'Quantity': np.random.randint(1, 100, n_rows),
        'UnitPrice': np.random.uniform(0.5, 50, n_rows),
        'CustomerID': np.random.randint(1000, 5000, n_rows),
        'InvoiceDate': pd.date_range('2010-01-01', periods=n_rows, freq='min')
    })
    
    import time
    start_time = time.time()
    
    result = clean_ecommerce_data(
        df,
        cancelled_prefix='C',
        min_quantity=1,
        min_unit_price=0.01,
        required_columns=['CustomerID']
    )
    
    execution_time = time.time() - start_time
    
    # Should complete in reasonable time (< 5 seconds for 100K rows)
    assert execution_time < 5.0
    assert len(result) > 0


if __name__ == "__main__":
    pytest.main([__file__, '-v', '--cov=src.data_cleaning', '--cov-report=html'])
