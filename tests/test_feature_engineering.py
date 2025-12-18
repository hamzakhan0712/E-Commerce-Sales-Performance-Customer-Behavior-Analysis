"""
Unit Tests for Feature Engineering Module

Tests all functions in src/feature_engineering.py to ensure feature
creation, RFM segmentation, and aggregations work correctly.

Run tests with:
    pytest tests/test_feature_engineering.py -v
    pytest tests/test_feature_engineering.py --cov=src.feature_engineering

Author: Data Analytics Team
Version: 1.0.0
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from src.feature_engineering import (
    create_total_price,
    extract_date_features,
    create_customer_metrics,
    create_rfm_scores,
    create_customer_segments,
    create_product_metrics,
    create_monthly_revenue,
    create_country_metrics,
    create_invoice_metrics,
    engineer_all_features
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_ecommerce_data():
    """Create sample e-commerce data for testing"""
    np.random.seed(42)
    data = {
        'InvoiceNo': ['INV001', 'INV001', 'INV002', 'INV003', 'INV004', 'INV005'],
        'StockCode': ['A001', 'A002', 'A001', 'A003', 'A001', 'A002'],
        'Description': ['Product A', 'Product B', 'Product A', 'Product C', 'Product A', 'Product B'],
        'Quantity': [2, 1, 3, 1, 5, 2],
        'UnitPrice': [10.0, 20.0, 10.0, 15.0, 10.0, 20.0],
        'InvoiceDate': pd.to_datetime([
            '2010-12-01 10:00:00',
            '2010-12-01 10:00:00',
            '2010-12-05 14:30:00',
            '2010-12-10 09:15:00',
            '2010-12-15 16:45:00',
            '2010-12-20 11:20:00'
        ]),
        'CustomerID': [1001, 1001, 1002, 1001, 1003, 1002],
        'Country': ['UK', 'UK', 'Germany', 'UK', 'France', 'Germany']
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_customer_data():
    """Create sample data focused on customer analysis"""
    data = {
        'InvoiceNo': ['INV001', 'INV002', 'INV003', 'INV004', 'INV005'],
        'CustomerID': [1001, 1001, 1002, 1003, 1001],
        'InvoiceDate': pd.to_datetime([
            '2010-01-01',
            '2010-02-01',
            '2010-01-15',
            '2010-03-01',
            '2010-06-01'
        ]),
        'Quantity': [5, 3, 10, 2, 4],
        'UnitPrice': [10.0, 15.0, 8.0, 20.0, 12.0]
    }
    df = pd.DataFrame(data)
    df['TotalPrice'] = df['Quantity'] * df['UnitPrice']
    return df


# ============================================================================
# TESTS: create_total_price
# ============================================================================

def test_create_total_price_basic(sample_ecommerce_data):
    """Test basic total price calculation"""
    df = create_total_price(sample_ecommerce_data)
    
    # Should have TotalPrice column
    assert 'TotalPrice' in df.columns
    
    # Check calculations
    expected = [20.0, 20.0, 30.0, 15.0, 50.0, 40.0]
    np.testing.assert_array_almost_equal(df['TotalPrice'].values, expected)


def test_create_total_price_with_decimals():
    """Test with decimal quantities and prices"""
    df = pd.DataFrame({
        'Quantity': [1.5, 2.25, 0.5],
        'UnitPrice': [10.99, 5.50, 20.00]
    })
    
    result = create_total_price(df)
    
    expected = [16.485, 12.375, 10.0]
    np.testing.assert_array_almost_equal(result['TotalPrice'].values, expected)


def test_create_total_price_with_zeros():
    """Test handling of zero quantities or prices"""
    df = pd.DataFrame({
        'Quantity': [0, 5, 10],
        'UnitPrice': [10.0, 0.0, 5.0]
    })
    
    result = create_total_price(df)
    
    expected = [0.0, 0.0, 50.0]
    np.testing.assert_array_almost_equal(result['TotalPrice'].values, expected)


# ============================================================================
# TESTS: extract_date_features
# ============================================================================

def test_extract_date_features_all_components(sample_ecommerce_data):
    """Test extraction of all date components"""
    df = extract_date_features(sample_ecommerce_data, date_col='InvoiceDate')
    
    # Should have new date columns
    expected_cols = ['Year', 'Month', 'Day', 'DayOfWeek', 'Hour', 'YearMonth']
    for col in expected_cols:
        assert col in df.columns
    
    # Check first row values
    assert df['Year'].iloc[0] == 2010
    assert df['Month'].iloc[0] == 12
    assert df['Day'].iloc[0] == 1
    assert df['Hour'].iloc[0] == 10
    assert df['YearMonth'].iloc[0] == '2010-12'


def test_extract_date_features_day_of_week():
    """Test day of week extraction"""
    df = pd.DataFrame({
        'Date': pd.to_datetime(['2010-12-01', '2010-12-02', '2010-12-03'])
    })
    
    result = extract_date_features(df, date_col='Date')
    
    # 2010-12-01 is Wednesday (2), 02 is Thursday (3), 03 is Friday (4)
    assert result['DayOfWeek'].iloc[0] == 2
    assert result['DayOfWeek'].iloc[1] == 3
    assert result['DayOfWeek'].iloc[2] == 4


def test_extract_date_features_year_month_format():
    """Test YearMonth string format"""
    df = pd.DataFrame({
        'Date': pd.to_datetime(['2010-01-15', '2010-12-31', '2011-06-01'])
    })
    
    result = extract_date_features(df, date_col='Date')
    
    assert result['YearMonth'].iloc[0] == '2010-01'
    assert result['YearMonth'].iloc[1] == '2010-12'
    assert result['YearMonth'].iloc[2] == '2011-06'


# ============================================================================
# TESTS: create_customer_metrics
# ============================================================================

def test_create_customer_metrics_basic(sample_customer_data):
    """Test basic customer metrics calculation"""
    df = create_customer_metrics(
        sample_customer_data,
        customer_col='CustomerID',
        invoice_col='InvoiceNo',
        date_col='InvoiceDate',
        total_price_col='TotalPrice'
    )
    
    # Should have one row per customer
    assert len(df) == 3  # Customers 1001, 1002, 1003
    
    # Check required columns
    required_cols = [
        'CustomerID', 'CustomerLifetimeValue', 'TotalOrders',
        'AvgBasketValue', 'Recency', 'Tenure', 'IsRepeatCustomer',
        'PurchaseFrequency'
    ]
    for col in required_cols:
        assert col in df.columns


def test_create_customer_metrics_clv_calculation(sample_customer_data):
    """Test CLV (Customer Lifetime Value) calculation"""
    df = create_customer_metrics(sample_customer_data, customer_col='CustomerID')
    
    # Customer 1001: 3 orders (50 + 45 + 48 = 143)
    customer_1001 = df[df['CustomerID'] == 1001].iloc[0]
    assert customer_1001['CustomerLifetimeValue'] == 143.0
    
    # Customer 1002: 1 order (80)
    customer_1002 = df[df['CustomerID'] == 1002].iloc[0]
    assert customer_1002['CustomerLifetimeValue'] == 80.0


def test_create_customer_metrics_repeat_customer(sample_customer_data):
    """Test repeat customer identification"""
    df = create_customer_metrics(sample_customer_data, customer_col='CustomerID')
    
    # Customer 1001 has 3 orders (repeat)
    customer_1001 = df[df['CustomerID'] == 1001].iloc[0]
    assert customer_1001['IsRepeatCustomer'] == 1
    assert customer_1001['TotalOrders'] == 3
    
    # Customer 1002 has 1 order (not repeat)
    customer_1002 = df[df['CustomerID'] == 1002].iloc[0]
    assert customer_1002['IsRepeatCustomer'] == 0
    assert customer_1002['TotalOrders'] == 1


def test_create_customer_metrics_recency(sample_customer_data):
    """Test recency calculation"""
    reference_date = pd.to_datetime('2010-06-30')
    
    df = create_customer_metrics(
        sample_customer_data,
        customer_col='CustomerID',
        reference_date=reference_date
    )
    
    # Customer 1001 last purchase: 2010-06-01 (29 days before reference)
    customer_1001 = df[df['CustomerID'] == 1001].iloc[0]
    assert customer_1001['Recency'] == 29


def test_create_customer_metrics_tenure(sample_customer_data):
    """Test tenure calculation"""
    df = create_customer_metrics(sample_customer_data, customer_col='CustomerID')
    
    # Customer 1001: first 2010-01-01, last 2010-06-01 = 151 days
    customer_1001 = df[df['CustomerID'] == 1001].iloc[0]
    assert customer_1001['Tenure'] == 151


# ============================================================================
# TESTS: create_rfm_scores
# ============================================================================

def test_create_rfm_scores_basic(sample_customer_data):
    """Test RFM score calculation"""
    # First create customer metrics
    customer_df = create_customer_metrics(sample_customer_data, customer_col='CustomerID')
    
    # Then calculate RFM scores
    df = create_rfm_scores(
        customer_df,
        recency_col='Recency',
        frequency_col='TotalOrders',
        monetary_col='CustomerLifetimeValue',
        bins=[0, 0.2, 0.4, 0.6, 0.8, 1.0]
    )
    
    # Should have RFM score columns
    assert 'R_Score' in df.columns
    assert 'F_Score' in df.columns
    assert 'M_Score' in df.columns
    assert 'RFM_Score' in df.columns


def test_create_rfm_scores_range():
    """Test RFM scores are within expected range (1-5)"""
    df = pd.DataFrame({
        'Recency': [1, 10, 50, 100, 200],
        'Frequency': [1, 2, 5, 10, 20],
        'Monetary': [10, 50, 100, 500, 1000]
    })
    
    result = create_rfm_scores(
        df,
        recency_col='Recency',
        frequency_col='Frequency',
        monetary_col='Monetary'
    )
    
    # All scores should be between 1 and 5
    assert result['R_Score'].between(1, 5).all()
    assert result['F_Score'].between(1, 5).all()
    assert result['M_Score'].between(1, 5).all()


def test_create_rfm_scores_recency_inverse():
    """Test that recency is scored inversely (lower is better)"""
    df = pd.DataFrame({
        'Recency': [1, 100],  # 1 day (recent) vs 100 days (old)
        'Frequency': [5, 5],
        'Monetary': [100, 100]
    })
    
    result = create_rfm_scores(df, recency_col='Recency')
    
    # Customer with Recency=1 should have higher R_Score
    assert result.loc[0, 'R_Score'] > result.loc[1, 'R_Score']


def test_create_rfm_scores_combined():
    """Test combined RFM score calculation"""
    df = pd.DataFrame({
        'Recency': [1, 10, 100],
        'Frequency': [10, 5, 1],
        'Monetary': [1000, 500, 50]
    })
    
    result = create_rfm_scores(df, recency_col='Recency')
    
    # First customer should have highest RFM_Score (sum of R+F+M)
    assert result.loc[0, 'RFM_Score'] > result.loc[1, 'RFM_Score']
    assert result.loc[1, 'RFM_Score'] > result.loc[2, 'RFM_Score']


# ============================================================================
# TESTS: create_customer_segments
# ============================================================================

def test_create_customer_segments_basic():
    """Test customer segmentation"""
    df = pd.DataFrame({
        'R_Score': [5, 5, 3, 2, 1],
        'F_Score': [5, 4, 3, 2, 1],
        'M_Score': [5, 4, 3, 2, 1]
    })
    
    segment_rules = {
        'champions': {'r_min': 4, 'f_min': 4, 'm_min': 4},
        'loyal': {'r_min': 4, 'f_min': 3},
        'potential_loyalists': {'r_min': 3, 'm_min': 3},
        'at_risk': {'r_max': 2, 'f_min': 2},
        'lost': {'r_max': 2, 'f_max': 2}
    }
    
    result = create_customer_segments(
        df,
        r_col='R_Score',
        f_col='F_Score',
        m_col='M_Score',
        segment_rules=segment_rules
    )
    
    # Should have CustomerSegment column
    assert 'CustomerSegment' in result.columns
    
    # Check segments
    assert result.loc[0, 'CustomerSegment'] == 'Champions'
    assert result.loc[1, 'CustomerSegment'] == 'Loyal Customers'


def test_create_customer_segments_all_segments():
    """Test that all segment types can be assigned"""
    df = pd.DataFrame({
        'R_Score': [5, 5, 3, 2, 1],
        'F_Score': [5, 4, 3, 2, 1],
        'M_Score': [5, 4, 3, 2, 1]
    })
    
    result = create_customer_segments(df)
    
    # Should have variety of segments
    assert result['CustomerSegment'].nunique() > 1
    
    # No 'Other' segment if rules cover all cases
    segments = result['CustomerSegment'].unique()
    expected_segments = ['Champions', 'Loyal Customers', 'Potential Loyalists', 'At Risk', 'Lost Customers']
    
    for segment in segments:
        assert segment in expected_segments


def test_create_customer_segments_edge_cases():
    """Test edge cases in segmentation"""
    df = pd.DataFrame({
        'R_Score': [5, 1, 3],
        'F_Score': [5, 1, 3],
        'M_Score': [5, 1, 3]
    })
    
    result = create_customer_segments(df)
    
    # All should be classified
    assert not result['CustomerSegment'].isna().any()


# ============================================================================
# TESTS: create_product_metrics
# ============================================================================

def test_create_product_metrics_basic(sample_ecommerce_data):
    """Test product metrics aggregation"""
    df = sample_ecommerce_data.copy()
    df['TotalPrice'] = df['Quantity'] * df['UnitPrice']
    
    result = create_product_metrics(
        df,
        product_col='StockCode',
        quantity_col='Quantity',
        price_col='UnitPrice',
        customer_col='CustomerID',
        invoice_col='InvoiceNo',
        description_col='Description'
    )
    
    # Should have one row per product
    assert len(result) == 3  # Products A001, A002, A003
    
    # Check required columns
    required_cols = [
        'StockCode', 'Description', 'TotalRevenue', 'UnitsSold',
        'OrderCount', 'UniqueCustomers', 'AvgPrice'
    ]
    for col in required_cols:
        assert col in result.columns


def test_create_product_metrics_revenue_calculation(sample_ecommerce_data):
    """Test product revenue calculation"""
    df = sample_ecommerce_data.copy()
    df['TotalPrice'] = df['Quantity'] * df['UnitPrice']
    
    result = create_product_metrics(df, product_col='StockCode')
    
    # Product A001: (2*10) + (3*10) + (5*10) = 100
    product_a001 = result[result['StockCode'] == 'A001'].iloc[0]
    assert product_a001['TotalRevenue'] == 100.0
    assert product_a001['UnitsSold'] == 10  # 2 + 3 + 5


def test_create_product_metrics_unique_customers(sample_ecommerce_data):
    """Test unique customer count per product"""
    df = sample_ecommerce_data.copy()
    df['TotalPrice'] = df['Quantity'] * df['UnitPrice']
    
    result = create_product_metrics(df, product_col='StockCode')
    
    # Product A001 bought by customers 1001, 1002, 1003 = 3 unique
    product_a001 = result[result['StockCode'] == 'A001'].iloc[0]
    assert product_a001['UniqueCustomers'] == 3


# ============================================================================
# TESTS: create_monthly_revenue
# ============================================================================

def test_create_monthly_revenue_basic(sample_ecommerce_data):
    """Test monthly revenue aggregation"""
    df = sample_ecommerce_data.copy()
    df['TotalPrice'] = df['Quantity'] * df['UnitPrice']
    
    result = create_monthly_revenue(
        df,
        date_col='InvoiceDate',
        total_price_col='TotalPrice',
        invoice_col='InvoiceNo',
        customer_col='CustomerID'
    )
    
    # Should have required columns
    required_cols = ['YearMonth', 'Revenue', 'Orders', 'UniqueCustomers']
    for col in required_cols:
        assert col in result.columns
    
    # All transactions in 2010-12
    assert len(result) == 1
    assert result['YearMonth'].iloc[0] == '2010-12'


def test_create_monthly_revenue_multiple_months():
    """Test with data spanning multiple months"""
    df = pd.DataFrame({
        'InvoiceDate': pd.to_datetime([
            '2010-01-15', '2010-01-20', '2010-02-10', '2010-03-05'
        ]),
        'TotalPrice': [100, 150, 200, 300],
        'InvoiceNo': ['INV001', 'INV002', 'INV003', 'INV004'],
        'CustomerID': [1001, 1002, 1001, 1003]
    })
    
    result = create_monthly_revenue(df, date_col='InvoiceDate')
    
    # Should have 3 months
    assert len(result) == 3
    
    # Check January revenue
    jan_revenue = result[result['YearMonth'] == '2010-01']['Revenue'].iloc[0]
    assert jan_revenue == 250.0  # 100 + 150


def test_create_monthly_revenue_mom_growth():
    """Test month-over-month growth calculation"""
    df = pd.DataFrame({
        'InvoiceDate': pd.to_datetime(['2010-01-15', '2010-02-15', '2010-03-15']),
        'TotalPrice': [100, 150, 120],
        'InvoiceNo': ['INV001', 'INV002', 'INV003'],
        'CustomerID': [1001, 1002, 1003]
    })
    
    result = create_monthly_revenue(df, date_col='InvoiceDate')
    
    # Should have MonthOverMonthGrowth column
    assert 'MonthOverMonthGrowth' in result.columns
    
    # February growth: (150-100)/100 * 100 = 50%
    feb_growth = result[result['YearMonth'] == '2010-02']['MonthOverMonthGrowth'].iloc[0]
    assert abs(feb_growth - 50.0) < 0.01


# ============================================================================
# TESTS: create_country_metrics
# ============================================================================

def test_create_country_metrics_basic(sample_ecommerce_data):
    """Test country-level aggregation"""
    df = sample_ecommerce_data.copy()
    df['TotalPrice'] = df['Quantity'] * df['UnitPrice']
    
    result = create_country_metrics(
        df,
        country_col='Country',
        total_price_col='TotalPrice',
        customer_col='CustomerID',
        invoice_col='InvoiceNo'
    )
    
    # Should have one row per country
    assert len(result) == 3  # UK, Germany, France
    
    # Check required columns
    required_cols = ['Country', 'TotalRevenue', 'TotalCustomers', 'TotalOrders', 'RevenuePercentage']
    for col in required_cols:
        assert col in result.columns


def test_create_country_metrics_revenue_percentage(sample_ecommerce_data):
    """Test revenue percentage calculation"""
    df = sample_ecommerce_data.copy()
    df['TotalPrice'] = df['Quantity'] * df['UnitPrice']
    
    result = create_country_metrics(df, country_col='Country')
    
    # Sum of all percentages should be 100%
    total_percentage = result['RevenuePercentage'].sum()
    assert abs(total_percentage - 100.0) < 0.01


def test_create_country_metrics_sorted():
    """Test that results are sorted by revenue descending"""
    df = pd.DataFrame({
        'Country': ['USA', 'UK', 'Germany'],
        'TotalPrice': [500, 1000, 200],
        'CustomerID': [1, 2, 3],
        'InvoiceNo': ['A', 'B', 'C']
    })
    
    result = create_country_metrics(df, country_col='Country')
    
    # UK should be first (highest revenue)
    assert result.iloc[0]['Country'] == 'UK'
    assert result.iloc[1]['Country'] == 'USA'
    assert result.iloc[2]['Country'] == 'Germany'


# ============================================================================
# TESTS: create_invoice_metrics
# ============================================================================

def test_create_invoice_metrics_basic(sample_ecommerce_data):
    """Test invoice-level metrics"""
    df = sample_ecommerce_data.copy()
    df['TotalPrice'] = df['Quantity'] * df['UnitPrice']
    
    result = create_invoice_metrics(
        df,
        invoice_col='InvoiceNo',
        total_price_col='TotalPrice',
        quantity_col='Quantity',
        product_col='StockCode'
    )
    
    # Should have one row per invoice
    assert len(result) == 5  # INV001-INV005
    
    # Check required columns
    required_cols = ['InvoiceNo', 'InvoiceValue', 'TotalItems', 'UniqueProducts']
    for col in required_cols:
        assert col in result.columns


def test_create_invoice_metrics_calculations(sample_ecommerce_data):
    """Test invoice metric calculations"""
    df = sample_ecommerce_data.copy()
    df['TotalPrice'] = df['Quantity'] * df['UnitPrice']
    
    result = create_invoice_metrics(df, invoice_col='InvoiceNo')
    
    # INV001 has 2 items (2 + 1), 2 unique products, value 40 (20+20)
    inv001 = result[result['InvoiceNo'] == 'INV001'].iloc[0]
    assert inv001['TotalItems'] == 3  # Quantity 2 + 1
    assert inv001['UniqueProducts'] == 2  # 2 different products
    assert inv001['InvoiceValue'] == 40.0  # 20 + 20


# ============================================================================
# TESTS: engineer_all_features (Integration Test)
# ============================================================================

def test_engineer_all_features_complete_pipeline(sample_ecommerce_data):
    """Test complete feature engineering pipeline"""
    datasets = engineer_all_features(
        sample_ecommerce_data,
        customer_col='CustomerID',
        invoice_col='InvoiceNo',
        date_col='InvoiceDate',
        product_col='StockCode',
        quantity_col='Quantity',
        price_col='UnitPrice',
        country_col='Country',
        description_col='Description'
    )
    
    # Should return tuple of 6 dataframes
    assert len(datasets) == 6
    
    (customer_df, customer_segments_df, product_df, 
     monthly_df, country_df, invoice_df) = datasets
    
    # Check all dataframes are non-empty
    assert len(customer_df) > 0
    assert len(customer_segments_df) > 0
    assert len(product_df) > 0
    assert len(monthly_df) > 0
    assert len(country_df) > 0
    assert len(invoice_df) > 0


def test_engineer_all_features_customer_count(sample_ecommerce_data):
    """Test that customer counts match"""
    datasets = engineer_all_features(sample_ecommerce_data)
    
    customer_df, customer_segments_df = datasets[0], datasets[1]
    
    # Both should have same number of customers
    assert len(customer_df) == len(customer_segments_df)
    
    # Should match unique customers in data
    expected_customers = sample_ecommerce_data['CustomerID'].nunique()
    assert len(customer_df) == expected_customers


def test_engineer_all_features_with_custom_rfm():
    """Test with custom RFM configuration"""
    df = pd.DataFrame({
        'InvoiceNo': ['INV001', 'INV002'],
        'StockCode': ['A001', 'A002'],
        'Description': ['Product A', 'Product B'],
        'Quantity': [5, 10],
        'UnitPrice': [10.0, 20.0],
        'InvoiceDate': pd.to_datetime(['2010-12-01', '2010-12-05']),
        'CustomerID': [1001, 1002],
        'Country': ['UK', 'Germany']
    })
    
    custom_bins = [0, 0.25, 0.50, 0.75, 1.0]
    custom_rules = {
        'champions': {'r_min': 3, 'f_min': 3, 'm_min': 3}
    }
    
    datasets = engineer_all_features(
        df,
        rfm_bins=custom_bins,
        segment_rules=custom_rules
    )
    
    customer_segments_df = datasets[1]
    
    # Should have RFM scores with custom bins (4 bins = scores 1-4)
    assert customer_segments_df['R_Score'].max() <= 4


# ============================================================================
# EDGE CASES
# ============================================================================

def test_empty_dataframe_handling():
    """Test handling of empty dataframes"""
    df = pd.DataFrame(columns=[
        'InvoiceNo', 'StockCode', 'Description', 'Quantity',
        'UnitPrice', 'InvoiceDate', 'CustomerID', 'Country'
    ])
    
    # Should handle gracefully without errors
    result = create_total_price(df)
    assert len(result) == 0
    assert 'TotalPrice' in result.columns


def test_single_customer_rfm():
    """Test RFM calculation with single customer"""
    df = pd.DataFrame({
        'CustomerID': [1001],
        'Recency': [10],
        'Frequency': [5],
        'Monetary': [100]
    })
    
    result = create_rfm_scores(df, recency_col='Recency')
    
    # Should still calculate scores (will all be same percentile)
    assert 'R_Score' in result.columns
    assert len(result) == 1


def test_missing_descriptions():
    """Test product metrics with missing descriptions"""
    df = pd.DataFrame({
        'StockCode': ['A001', 'A002'],
        'Description': [None, 'Product B'],
        'Quantity': [5, 10],
        'UnitPrice': [10.0, 20.0],
        'TotalPrice': [50.0, 200.0],
        'CustomerID': [1001, 1002],
        'InvoiceNo': ['INV001', 'INV002']
    })
    
    result = create_product_metrics(df, product_col='StockCode')
    
    # Should handle None descriptions
    assert len(result) == 2
    assert result['Description'].isna().sum() <= 1


if __name__ == "__main__":
    pytest.main([__file__, '-v', '--cov=src.feature_engineering', '--cov-report=html'])
