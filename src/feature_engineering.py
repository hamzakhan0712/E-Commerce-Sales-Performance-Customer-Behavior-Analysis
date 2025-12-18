"""
Feature Engineering Functions for E-Commerce Analysis
Functions for creating customer metrics, RFM segmentation, and aggregations

Author: Hamza Khan
Date: December 18, 2024
"""

import pandas as pd
import numpy as np
from loguru import logger
from typing import Dict, Any, Tuple


def create_total_price(df: pd.DataFrame, quantity_col: str = 'Quantity',
                        price_col: str = 'UnitPrice') -> pd.DataFrame:
    """
    Create TotalPrice column (revenue per transaction)
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe
    quantity_col : str
        Quantity column name
    price_col : str
        Unit price column name
    
    Returns:
    --------
    pd.DataFrame : Dataframe with TotalPrice column
    
    Example:
    --------
    >>> df = create_total_price(df)
    """
    df['TotalPrice'] = df[quantity_col] * df[price_col]
    logger.info(f"✅ Created TotalPrice column")
    return df


def extract_date_features(df: pd.DataFrame, date_col: str = 'InvoiceDate') -> pd.DataFrame:
    """
    Extract date components from datetime column
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe
    date_col : str
        Date column name
    
    Returns:
    --------
    pd.DataFrame : Dataframe with date features
    
    Example:
    --------
    >>> df = extract_date_features(df)
    """
    df[date_col] = pd.to_datetime(df[date_col])
    
    df['Year'] = df[date_col].dt.year
    df['Month'] = df[date_col].dt.month
    df['Day'] = df[date_col].dt.day
    df['DayOfWeek'] = df[date_col].dt.dayofweek  # Monday=0, Sunday=6
    df['Hour'] = df[date_col].dt.hour
    df['YearMonth'] = df[date_col].dt.to_period('M')
    
    logger.info(f"✅ Extracted date features: Year, Month, Day, DayOfWeek, Hour, YearMonth")
    return df


def create_customer_metrics(df: pd.DataFrame, analysis_date: str = None) -> pd.DataFrame:
    """
    Create customer-level aggregated metrics with RFM segmentation
    
    Parameters:
    -----------
    df : pd.DataFrame
        Transaction dataframe
    analysis_date : str
        Reference date for recency calculation (YYYY-MM-DD)
    
    Returns:
    --------
    pd.DataFrame : Customer metrics dataframe
    
    Example:
    --------
    >>> customer_metrics = create_customer_metrics(df, analysis_date='2010-12-09')
    """
    if analysis_date is None:
        analysis_date = df['InvoiceDate'].max()
    else:
        analysis_date = pd.to_datetime(analysis_date)
    
    logger.info(f"📊 Creating customer metrics (Analysis date: {analysis_date.date()})")
    
    # Aggregate by customer
    customer_agg = df.groupby('CustomerID').agg({
        'InvoiceNo': 'nunique',              # Total orders
        'TotalPrice': ['sum', 'mean'],        # CLV and average basket value
        'Quantity': 'sum',                    # Total items purchased
        'InvoiceDate': ['min', 'max']         # First and last purchase
    }).reset_index()
    
    # Flatten column names
    customer_agg.columns = [
        'CustomerID', 'TotalOrders', 'CustomerLifetimeValue',
        'AvgBasketValue', 'TotalItemsPurchased',
        'FirstPurchase', 'LastPurchase'
    ]
    
    # Calculate tenure and recency
    customer_agg['CustomerTenure_Days'] = (
        customer_agg['LastPurchase'] - customer_agg['FirstPurchase']
    ).dt.days
    
    customer_agg['Recency_Days'] = (
        analysis_date - customer_agg['LastPurchase']
    ).dt.days
    
    # Is repeat customer?
    customer_agg['IsRepeatCustomer'] = (customer_agg['TotalOrders'] > 1).astype(int)
    
    # Purchase frequency (orders per month)
    customer_agg['PurchaseFrequency'] = customer_agg['TotalOrders'] / (
        (customer_agg['CustomerTenure_Days'] + 1) / 30
    )
    
    logger.info(f"✅ Created customer metrics for {len(customer_agg):,} customers")
    
    return customer_agg


def create_rfm_scores(customer_metrics: pd.DataFrame) -> pd.DataFrame:
    """
    Create RFM scores using percentile ranking
    
    Parameters:
    -----------
    customer_metrics : pd.DataFrame
        Customer metrics dataframe with Recency, Frequency, Monetary columns
    
    Returns:
    --------
    pd.DataFrame : Customer metrics with RFM scores
    
    Example:
    --------
    >>> customer_metrics = create_rfm_scores(customer_metrics)
    """
    logger.info("📊 Creating RFM scores...")
    
    # R_Score: Lower recency is better (more recent purchase)
    customer_metrics['R_Score'] = pd.cut(
        customer_metrics['Recency_Days'].rank(method='first', pct=True),
        bins=[0, 0.2, 0.4, 0.6, 0.8, 1.0],
        labels=[5, 4, 3, 2, 1]
    ).astype(int)
    
    # F_Score: Higher frequency is better (more orders)
    customer_metrics['F_Score'] = pd.cut(
        customer_metrics['TotalOrders'].rank(method='first', pct=True),
        bins=[0, 0.2, 0.4, 0.6, 0.8, 1.0],
        labels=[1, 2, 3, 4, 5]
    ).astype(int)
    
    # M_Score: Higher monetary value is better (more spending)
    customer_metrics['M_Score'] = pd.cut(
        customer_metrics['CustomerLifetimeValue'].rank(method='first', pct=True),
        bins=[0, 0.2, 0.4, 0.6, 0.8, 1.0],
        labels=[1, 2, 3, 4, 5]
    ).astype(int)
    
    # Concatenated RFM score
    customer_metrics['RFM_Score'] = (
        customer_metrics['R_Score'].astype(str) +
        customer_metrics['F_Score'].astype(str) +
        customer_metrics['M_Score'].astype(str)
    )
    
    logger.info("✅ RFM scores created (1-5 scale)")
    
    return customer_metrics


def create_customer_segments(customer_metrics: pd.DataFrame) -> pd.DataFrame:
    """
    Classify customers into business segments based on RFM scores
    
    Parameters:
    -----------
    customer_metrics : pd.DataFrame
        Customer metrics with RFM scores
    
    Returns:
    --------
    pd.DataFrame : Customer metrics with segments
    
    Example:
    --------
    >>> customer_metrics = create_customer_segments(customer_metrics)
    """
    def classify_rfm(row):
        score = row['R_Score'] + row['F_Score'] + row['M_Score']
        if score >= 13:
            return 'Champions'
        elif score >= 10:
            return 'Loyal Customers'
        elif score >= 7:
            return 'Potential Loyalists'
        elif score >= 5:
            return 'At Risk'
        else:
            return 'Lost Customers'
    
    customer_metrics['CustomerSegment'] = customer_metrics.apply(classify_rfm, axis=1)
    
    segment_counts = customer_metrics['CustomerSegment'].value_counts()
    logger.info("✅ Customer segmentation complete:")
    for segment, count in segment_counts.items():
        logger.info(f"   • {segment}: {count:,} ({count/len(customer_metrics)*100:.1f}%)")
    
    return customer_metrics


def create_product_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create product-level performance metrics
    
    Parameters:
    -----------
    df : pd.DataFrame
        Transaction dataframe
    
    Returns:
    --------
    pd.DataFrame : Product metrics dataframe
    
    Example:
    --------
    >>> product_metrics = create_product_metrics(df)
    """
    logger.info("📊 Creating product metrics...")
    
    product_agg = df.groupby(['StockCode', 'Description']).agg({
        'TotalPrice': 'sum',              # Total revenue
        'Quantity': 'sum',                 # Units sold
        'InvoiceNo': 'nunique',           # Order count
        'CustomerID': 'nunique'            # Unique customers
    }).reset_index()
    
    product_agg.columns = [
        'StockCode', 'Description', 'TotalRevenue',
        'UnitsSold', 'OrderCount', 'UniqueCustomers'
    ]
    
    # Average price
    product_agg['AvgPrice'] = product_agg['TotalRevenue'] / product_agg['UnitsSold']
    
    # Sort by revenue
    product_agg = product_agg.sort_values('TotalRevenue', ascending=False).reset_index(drop=True)
    
    logger.info(f"✅ Created metrics for {len(product_agg):,} products")
    
    return product_agg


def create_monthly_revenue(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create monthly revenue aggregations
    
    Parameters:
    -----------
    df : pd.DataFrame
        Transaction dataframe
    
    Returns:
    --------
    pd.DataFrame : Monthly revenue dataframe
    
    Example:
    --------
    >>> monthly_revenue = create_monthly_revenue(df)
    """
    logger.info("📊 Creating monthly revenue metrics...")
    
    monthly_agg = df.groupby(df['InvoiceDate'].dt.to_period('M')).agg({
        'TotalPrice': 'sum',
        'InvoiceNo': 'nunique',
        'CustomerID': 'nunique'
    }).reset_index()
    
    monthly_agg.columns = ['YearMonth', 'MonthlyRevenue', 'MonthlyOrders', 'MonthlyCustomers']
    
    # Calculate month-over-month growth
    monthly_agg['RevenueGrowth_Pct'] = monthly_agg['MonthlyRevenue'].pct_change() * 100
    
    logger.info(f"✅ Created monthly metrics for {len(monthly_agg)} months")
    
    return monthly_agg


def create_country_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create country-level revenue metrics
    
    Parameters:
    -----------
    df : pd.DataFrame
        Transaction dataframe
    
    Returns:
    --------
    pd.DataFrame : Country metrics dataframe
    
    Example:
    --------
    >>> country_metrics = create_country_metrics(df)
    """
    logger.info("📊 Creating country metrics...")
    
    country_agg = df.groupby('Country').agg({
        'TotalPrice': 'sum',
        'InvoiceNo': 'nunique',
        'CustomerID': 'nunique'
    }).reset_index()
    
    country_agg.columns = ['Country', 'TotalRevenue', 'TotalOrders', 'UniqueCustomers']
    
    # Calculate revenue percentage
    total_revenue = country_agg['TotalRevenue'].sum()
    country_agg['RevenuePct'] = (country_agg['TotalRevenue'] / total_revenue * 100).round(2)
    
    # Sort by revenue
    country_agg = country_agg.sort_values('TotalRevenue', ascending=False).reset_index(drop=True)
    
    logger.info(f"✅ Created metrics for {len(country_agg)} countries")
    
    return country_agg


def create_invoice_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create invoice-level basket metrics
    
    Parameters:
    -----------
    df : pd.DataFrame
        Transaction dataframe
    
    Returns:
    --------
    pd.DataFrame : Invoice metrics dataframe
    
    Example:
    --------
    >>> invoice_metrics = create_invoice_metrics(df)
    """
    logger.info("📊 Creating invoice metrics...")
    
    invoice_agg = df.groupby('InvoiceNo').agg({
        'TotalPrice': 'sum',
        'Quantity': 'sum',
        'StockCode': 'nunique',
        'CustomerID': 'first',
        'Country': 'first',
        'InvoiceDate': 'first'
    }).reset_index()
    
    invoice_agg.columns = [
        'InvoiceNo', 'InvoiceValue', 'TotalItems', 'UniqueProducts',
        'CustomerID', 'Country', 'InvoiceDate'
    ]
    
    logger.info(f"✅ Created metrics for {len(invoice_agg):,} invoices")
    
    return invoice_agg


def engineer_all_features(df: pd.DataFrame, config: Dict[str, Any] = None) -> Tuple:
    """
    Complete feature engineering pipeline
    
    Parameters:
    -----------
    df : pd.DataFrame
        Cleaned transaction dataframe
    config : dict
        Configuration dictionary
    
    Returns:
    --------
    tuple : (df_clean, customer_metrics, product_metrics, monthly_revenue, 
             country_metrics, invoice_metrics)
    
    Example:
    --------
    >>> results = engineer_all_features(df_clean)
    >>> df_clean, customer_metrics, product_metrics, monthly_revenue, country_metrics, invoice_metrics = results
    """
    logger.info("\n" + "="*80)
    logger.info("STARTING FEATURE ENGINEERING PIPELINE")
    logger.info("="*80 + "\n")
    
    # Create TotalPrice
    df = create_total_price(df)
    
    # Extract date features
    df = extract_date_features(df)
    
    # Create aggregated datasets
    customer_metrics = create_customer_metrics(df)
    customer_metrics = create_rfm_scores(customer_metrics)
    customer_metrics = create_customer_segments(customer_metrics)
    
    product_metrics = create_product_metrics(df)
    monthly_revenue = create_monthly_revenue(df)
    country_metrics = create_country_metrics(df)
    invoice_metrics = create_invoice_metrics(df)
    
    logger.info("\n" + "="*80)
    logger.info("FEATURE ENGINEERING COMPLETE")
    logger.info("="*80)
    logger.info(f"📊 Cleaned Data: {len(df):,} rows × {len(df.columns)} columns")
    logger.info(f"📊 Customer Metrics: {len(customer_metrics):,} customers")
    logger.info(f"📊 Product Metrics: {len(product_metrics):,} products")
    logger.info(f"📊 Monthly Revenue: {len(monthly_revenue)} months")
    logger.info(f"📊 Country Metrics: {len(country_metrics)} countries")
    logger.info(f"📊 Invoice Metrics: {len(invoice_metrics):,} invoices")
    logger.info("="*80 + "\n")
    
    return df, customer_metrics, product_metrics, monthly_revenue, country_metrics, invoice_metrics


if __name__ == "__main__":
    # Example usage
    from utils import load_config, setup_logging, load_data, save_data
    
    setup_logging()
    config = load_config()
    
    # Load cleaned data
    df_clean = load_data(config['paths']['data']['cleaned'])
    
    # Engineer features
    results = engineer_all_features(df_clean, config)
    df_clean, customer_metrics, product_metrics, monthly_revenue, country_metrics, invoice_metrics = results
    
    # Save all datasets
    save_data(df_clean, config['paths']['data']['cleaned'])
    save_data(customer_metrics, config['paths']['data']['customer_metrics'])
    save_data(product_metrics, config['paths']['data']['product_metrics'])
    save_data(monthly_revenue, config['paths']['data']['monthly_revenue'])
    save_data(country_metrics, config['paths']['data']['country_metrics'])
    save_data(invoice_metrics, config['paths']['data']['invoice_metrics'])
