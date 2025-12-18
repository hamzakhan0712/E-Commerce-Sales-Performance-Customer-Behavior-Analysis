-- ============================================================================
-- UK E-commerce Analytics SQL Queries
-- ============================================================================
-- Purpose: Production-ready SQL queries for business intelligence analysis
-- Database: PostgreSQL/MySQL/Snowflake compatible
-- Version: 1.0
-- Author: Data Analytics Team
-- Last Updated: December 2024
-- ============================================================================

-- ============================================================================
-- 1. REVENUE ANALYSIS
-- ============================================================================

-- 1.1 Total Revenue and Key Metrics (Overall Performance)
-- Business Question: What is our total revenue, orders, and average order value?
-- ----------------------------------------------------------------------------
SELECT 
    COUNT(DISTINCT invoice_no) AS total_orders,
    COUNT(DISTINCT customer_id) AS total_customers,
    COUNT(DISTINCT stock_code) AS total_products,
    SUM(quantity * unit_price) AS total_revenue,
    AVG(quantity * unit_price) AS avg_order_value,
    SUM(quantity) AS total_units_sold,
    MIN(invoice_date) AS first_transaction_date,
    MAX(invoice_date) AS last_transaction_date
FROM ecommerce_data
WHERE invoice_no NOT LIKE 'C%'  -- Exclude cancelled orders
    AND customer_id IS NOT NULL
    AND quantity > 0
    AND unit_price > 0;


-- 1.2 Monthly Revenue Trend (Time Series Analysis)
-- Business Question: How has revenue trended month-over-month?
-- ----------------------------------------------------------------------------
WITH monthly_revenue AS (
    SELECT 
        DATE_TRUNC('month', invoice_date) AS month,
        SUM(quantity * unit_price) AS revenue,
        COUNT(DISTINCT invoice_no) AS orders,
        COUNT(DISTINCT customer_id) AS active_customers,
        SUM(quantity) AS units_sold
    FROM ecommerce_data
    WHERE invoice_no NOT LIKE 'C%'
        AND customer_id IS NOT NULL
        AND quantity > 0
        AND unit_price > 0
    GROUP BY DATE_TRUNC('month', invoice_date)
)
SELECT 
    month,
    revenue,
    orders,
    active_customers,
    units_sold,
    LAG(revenue) OVER (ORDER BY month) AS prev_month_revenue,
    ROUND(
        ((revenue - LAG(revenue) OVER (ORDER BY month)) / 
         NULLIF(LAG(revenue) OVER (ORDER BY month), 0) * 100), 2
    ) AS revenue_growth_pct,
    ROUND(revenue / NULLIF(orders, 0), 2) AS avg_order_value
FROM monthly_revenue
ORDER BY month;


-- 1.3 Revenue by Country (Geographic Analysis)
-- Business Question: Which countries generate the most revenue?
-- ----------------------------------------------------------------------------
SELECT 
    country,
    COUNT(DISTINCT customer_id) AS customers,
    COUNT(DISTINCT invoice_no) AS orders,
    SUM(quantity * unit_price) AS total_revenue,
    ROUND(
        SUM(quantity * unit_price) / 
        SUM(SUM(quantity * unit_price)) OVER () * 100, 2
    ) AS revenue_percentage,
    ROUND(AVG(quantity * unit_price), 2) AS avg_transaction_value,
    SUM(quantity) AS total_units_sold
FROM ecommerce_data
WHERE invoice_no NOT LIKE 'C%'
    AND customer_id IS NOT NULL
    AND quantity > 0
    AND unit_price > 0
GROUP BY country
ORDER BY total_revenue DESC
LIMIT 20;


-- 1.4 Daily Revenue with Moving Average (Trend Smoothing)
-- Business Question: What is our daily revenue pattern with smoothed trends?
-- ----------------------------------------------------------------------------
WITH daily_revenue AS (
    SELECT 
        DATE(invoice_date) AS date,
        SUM(quantity * unit_price) AS revenue,
        COUNT(DISTINCT invoice_no) AS orders
    FROM ecommerce_data
    WHERE invoice_no NOT LIKE 'C%'
        AND customer_id IS NOT NULL
        AND quantity > 0
        AND unit_price > 0
    GROUP BY DATE(invoice_date)
)
SELECT 
    date,
    revenue,
    orders,
    AVG(revenue) OVER (
        ORDER BY date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS moving_avg_7day,
    AVG(revenue) OVER (
        ORDER BY date 
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ) AS moving_avg_30day
FROM daily_revenue
ORDER BY date;


-- ============================================================================
-- 2. CUSTOMER ANALYSIS
-- ============================================================================

-- 2.1 Customer Lifetime Value (CLV) and Purchase Metrics
-- Business Question: Who are our most valuable customers?
-- ----------------------------------------------------------------------------
WITH customer_metrics AS (
    SELECT 
        customer_id,
        country,
        MIN(invoice_date) AS first_purchase_date,
        MAX(invoice_date) AS last_purchase_date,
        COUNT(DISTINCT invoice_no) AS total_orders,
        COUNT(DISTINCT DATE(invoice_date)) AS unique_purchase_days,
        SUM(quantity * unit_price) AS total_spent,
        AVG(quantity * unit_price) AS avg_order_value,
        SUM(quantity) AS total_items_purchased,
        COUNT(DISTINCT stock_code) AS unique_products_purchased,
        DATEDIFF(MAX(invoice_date), MIN(invoice_date)) AS customer_tenure_days
    FROM ecommerce_data
    WHERE invoice_no NOT LIKE 'C%'
        AND customer_id IS NOT NULL
        AND quantity > 0
        AND unit_price > 0
    GROUP BY customer_id, country
)
SELECT 
    customer_id,
    country,
    first_purchase_date,
    last_purchase_date,
    total_orders,
    unique_purchase_days,
    ROUND(total_spent, 2) AS customer_lifetime_value,
    ROUND(avg_order_value, 2) AS avg_order_value,
    total_items_purchased,
    unique_products_purchased,
    customer_tenure_days,
    CASE 
        WHEN total_orders = 1 THEN 'One-Time'
        WHEN total_orders BETWEEN 2 AND 5 THEN 'Occasional'
        WHEN total_orders BETWEEN 6 AND 10 THEN 'Regular'
        ELSE 'Frequent'
    END AS customer_type,
    ROUND(
        total_spent / NULLIF(customer_tenure_days, 0) * 30, 2
    ) AS avg_monthly_revenue
FROM customer_metrics
ORDER BY customer_lifetime_value DESC
LIMIT 100;


-- 2.2 RFM Segmentation (Recency, Frequency, Monetary)
-- Business Question: How should we segment customers for targeted marketing?
-- ----------------------------------------------------------------------------
WITH rfm_base AS (
    SELECT 
        customer_id,
        DATEDIFF('2010-12-31', MAX(invoice_date)) AS recency_days,
        COUNT(DISTINCT invoice_no) AS frequency,
        SUM(quantity * unit_price) AS monetary
    FROM ecommerce_data
    WHERE invoice_no NOT LIKE 'C%'
        AND customer_id IS NOT NULL
        AND quantity > 0
        AND unit_price > 0
    GROUP BY customer_id
),
rfm_scores AS (
    SELECT 
        customer_id,
        recency_days,
        frequency,
        monetary,
        NTILE(5) OVER (ORDER BY recency_days ASC) AS r_score,
        NTILE(5) OVER (ORDER BY frequency DESC) AS f_score,
        NTILE(5) OVER (ORDER BY monetary DESC) AS m_score
    FROM rfm_base
)
SELECT 
    customer_id,
    recency_days,
    frequency,
    ROUND(monetary, 2) AS monetary,
    r_score,
    f_score,
    m_score,
    r_score + f_score + m_score AS rfm_total_score,
    CASE 
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
        WHEN r_score >= 4 AND f_score >= 3 THEN 'Loyal Customers'
        WHEN r_score >= 3 AND m_score >= 3 THEN 'Potential Loyalists'
        WHEN r_score <= 2 AND f_score >= 2 THEN 'At Risk'
        WHEN r_score <= 2 AND f_score <= 2 THEN 'Lost Customers'
        ELSE 'Other'
    END AS customer_segment
FROM rfm_scores
ORDER BY rfm_total_score DESC;


-- 2.3 Customer Cohort Analysis (Retention)
-- Business Question: How well are we retaining customers over time?
-- ----------------------------------------------------------------------------
WITH first_purchase AS (
    SELECT 
        customer_id,
        DATE_TRUNC('month', MIN(invoice_date)) AS cohort_month
    FROM ecommerce_data
    WHERE invoice_no NOT LIKE 'C%'
        AND customer_id IS NOT NULL
    GROUP BY customer_id
),
customer_activity AS (
    SELECT 
        f.customer_id,
        f.cohort_month,
        DATE_TRUNC('month', e.invoice_date) AS activity_month,
        EXTRACT(MONTH FROM AGE(
            DATE_TRUNC('month', e.invoice_date), 
            f.cohort_month
        )) AS months_since_first_purchase
    FROM first_purchase f
    JOIN ecommerce_data e ON f.customer_id = e.customer_id
    WHERE e.invoice_no NOT LIKE 'C%'
        AND e.customer_id IS NOT NULL
    GROUP BY f.customer_id, f.cohort_month, DATE_TRUNC('month', e.invoice_date)
)
SELECT 
    cohort_month,
    COUNT(DISTINCT CASE WHEN months_since_first_purchase = 0 THEN customer_id END) AS month_0,
    COUNT(DISTINCT CASE WHEN months_since_first_purchase = 1 THEN customer_id END) AS month_1,
    COUNT(DISTINCT CASE WHEN months_since_first_purchase = 2 THEN customer_id END) AS month_2,
    COUNT(DISTINCT CASE WHEN months_since_first_purchase = 3 THEN customer_id END) AS month_3,
    COUNT(DISTINCT CASE WHEN months_since_first_purchase = 6 THEN customer_id END) AS month_6,
    COUNT(DISTINCT CASE WHEN months_since_first_purchase = 12 THEN customer_id END) AS month_12,
    ROUND(
        COUNT(DISTINCT CASE WHEN months_since_first_purchase = 1 THEN customer_id END)::NUMERIC / 
        NULLIF(COUNT(DISTINCT CASE WHEN months_since_first_purchase = 0 THEN customer_id END), 0) * 100, 2
    ) AS retention_rate_month_1
FROM customer_activity
GROUP BY cohort_month
ORDER BY cohort_month;


-- 2.4 Repeat Customer Analysis
-- Business Question: What percentage of our customers are repeat buyers?
-- ----------------------------------------------------------------------------
WITH customer_order_counts AS (
    SELECT 
        customer_id,
        COUNT(DISTINCT invoice_no) AS order_count,
        SUM(quantity * unit_price) AS total_revenue
    FROM ecommerce_data
    WHERE invoice_no NOT LIKE 'C%'
        AND customer_id IS NOT NULL
        AND quantity > 0
        AND unit_price > 0
    GROUP BY customer_id
)
SELECT 
    COUNT(DISTINCT customer_id) AS total_customers,
    COUNT(DISTINCT CASE WHEN order_count = 1 THEN customer_id END) AS one_time_customers,
    COUNT(DISTINCT CASE WHEN order_count > 1 THEN customer_id END) AS repeat_customers,
    ROUND(
        COUNT(DISTINCT CASE WHEN order_count > 1 THEN customer_id END)::NUMERIC / 
        NULLIF(COUNT(DISTINCT customer_id), 0) * 100, 2
    ) AS repeat_customer_rate,
    ROUND(
        SUM(CASE WHEN order_count = 1 THEN total_revenue END), 2
    ) AS revenue_one_time,
    ROUND(
        SUM(CASE WHEN order_count > 1 THEN total_revenue END), 2
    ) AS revenue_repeat,
    ROUND(
        SUM(CASE WHEN order_count > 1 THEN total_revenue END) / 
        NULLIF(SUM(total_revenue), 0) * 100, 2
    ) AS repeat_revenue_percentage
FROM customer_order_counts;


-- ============================================================================
-- 3. PRODUCT ANALYSIS
-- ============================================================================

-- 3.1 Top Selling Products (Revenue & Volume)
-- Business Question: Which products drive the most revenue and sales?
-- ----------------------------------------------------------------------------
SELECT 
    stock_code,
    description,
    SUM(quantity) AS units_sold,
    COUNT(DISTINCT invoice_no) AS times_ordered,
    COUNT(DISTINCT customer_id) AS unique_customers,
    SUM(quantity * unit_price) AS total_revenue,
    ROUND(AVG(unit_price), 2) AS avg_price,
    ROUND(
        SUM(quantity * unit_price) / 
        SUM(SUM(quantity * unit_price)) OVER () * 100, 2
    ) AS revenue_percentage,
    ROUND(AVG(quantity), 2) AS avg_quantity_per_order
FROM ecommerce_data
WHERE invoice_no NOT LIKE 'C%'
    AND customer_id IS NOT NULL
    AND quantity > 0
    AND unit_price > 0
    AND description IS NOT NULL
GROUP BY stock_code, description
ORDER BY total_revenue DESC
LIMIT 50;


-- 3.2 Product Performance by Month (Seasonality)
-- Business Question: How do product sales vary by season/month?
-- ----------------------------------------------------------------------------
WITH product_monthly_sales AS (
    SELECT 
        stock_code,
        description,
        DATE_TRUNC('month', invoice_date) AS month,
        SUM(quantity) AS units_sold,
        SUM(quantity * unit_price) AS revenue
    FROM ecommerce_data
    WHERE invoice_no NOT LIKE 'C%'
        AND customer_id IS NOT NULL
        AND quantity > 0
        AND unit_price > 0
        AND description IS NOT NULL
    GROUP BY stock_code, description, DATE_TRUNC('month', invoice_date)
)
SELECT 
    stock_code,
    description,
    month,
    units_sold,
    ROUND(revenue, 2) AS revenue,
    LAG(revenue) OVER (PARTITION BY stock_code ORDER BY month) AS prev_month_revenue,
    ROUND(
        (revenue - LAG(revenue) OVER (PARTITION BY stock_code ORDER BY month)) / 
        NULLIF(LAG(revenue) OVER (PARTITION BY stock_code ORDER BY month), 0) * 100, 2
    ) AS mom_growth_pct
FROM product_monthly_sales
WHERE stock_code IN (
    -- Top 10 products by total revenue
    SELECT stock_code
    FROM ecommerce_data
    WHERE invoice_no NOT LIKE 'C%'
        AND customer_id IS NOT NULL
        AND quantity > 0
        AND unit_price > 0
    GROUP BY stock_code
    ORDER BY SUM(quantity * unit_price) DESC
    LIMIT 10
)
ORDER BY stock_code, month;


-- 3.3 Product Basket Analysis (Frequently Bought Together)
-- Business Question: Which products are commonly purchased together?
-- ----------------------------------------------------------------------------
WITH product_pairs AS (
    SELECT 
        e1.stock_code AS product_1,
        e1.description AS description_1,
        e2.stock_code AS product_2,
        e2.description AS description_2,
        COUNT(DISTINCT e1.invoice_no) AS co_occurrence_count
    FROM ecommerce_data e1
    JOIN ecommerce_data e2 
        ON e1.invoice_no = e2.invoice_no 
        AND e1.stock_code < e2.stock_code  -- Avoid duplicates and self-joins
    WHERE e1.invoice_no NOT LIKE 'C%'
        AND e2.invoice_no NOT LIKE 'C%'
        AND e1.customer_id IS NOT NULL
        AND e2.customer_id IS NOT NULL
        AND e1.quantity > 0
        AND e2.quantity > 0
        AND e1.description IS NOT NULL
        AND e2.description IS NOT NULL
    GROUP BY e1.stock_code, e1.description, e2.stock_code, e2.description
    HAVING COUNT(DISTINCT e1.invoice_no) >= 20  -- Minimum support threshold
)
SELECT 
    product_1,
    description_1,
    product_2,
    description_2,
    co_occurrence_count,
    ROUND(
        co_occurrence_count::NUMERIC / 
        (SELECT COUNT(DISTINCT invoice_no) FROM ecommerce_data WHERE invoice_no NOT LIKE 'C%') * 100, 4
    ) AS support_pct
FROM product_pairs
ORDER BY co_occurrence_count DESC
LIMIT 50;


-- 3.4 Low Performing Products (Potential Discontinuation)
-- Business Question: Which products have poor sales and should be reviewed?
-- ----------------------------------------------------------------------------
WITH product_metrics AS (
    SELECT 
        stock_code,
        description,
        SUM(quantity) AS units_sold,
        COUNT(DISTINCT invoice_no) AS times_ordered,
        COUNT(DISTINCT customer_id) AS unique_customers,
        SUM(quantity * unit_price) AS total_revenue,
        MAX(invoice_date) AS last_sold_date
    FROM ecommerce_data
    WHERE invoice_no NOT LIKE 'C%'
        AND customer_id IS NOT NULL
        AND quantity > 0
        AND unit_price > 0
        AND description IS NOT NULL
    GROUP BY stock_code, description
)
SELECT 
    stock_code,
    description,
    units_sold,
    times_ordered,
    unique_customers,
    ROUND(total_revenue, 2) AS total_revenue,
    last_sold_date,
    DATEDIFF('2010-12-31', last_sold_date) AS days_since_last_sale
FROM product_metrics
WHERE units_sold < 50  -- Low volume
    OR total_revenue < 100  -- Low revenue
    OR DATEDIFF('2010-12-31', last_sold_date) > 180  -- Not sold in 6 months
ORDER BY total_revenue ASC, units_sold ASC
LIMIT 100;


-- ============================================================================
-- 4. ORDER ANALYSIS
-- ============================================================================

-- 4.1 Order Size Distribution
-- Business Question: What is the typical order size (items and value)?
-- ----------------------------------------------------------------------------
WITH order_metrics AS (
    SELECT 
        invoice_no,
        customer_id,
        invoice_date,
        SUM(quantity) AS total_items,
        COUNT(DISTINCT stock_code) AS unique_products,
        SUM(quantity * unit_price) AS order_value
    FROM ecommerce_data
    WHERE invoice_no NOT LIKE 'C%'
        AND customer_id IS NOT NULL
        AND quantity > 0
        AND unit_price > 0
    GROUP BY invoice_no, customer_id, invoice_date
)
SELECT 
    CASE 
        WHEN order_value < 10 THEN '0-10'
        WHEN order_value < 50 THEN '10-50'
        WHEN order_value < 100 THEN '50-100'
        WHEN order_value < 250 THEN '100-250'
        WHEN order_value < 500 THEN '250-500'
        WHEN order_value < 1000 THEN '500-1000'
        ELSE '1000+'
    END AS order_value_bucket,
    COUNT(*) AS order_count,
    ROUND(AVG(total_items), 2) AS avg_items_per_order,
    ROUND(AVG(unique_products), 2) AS avg_unique_products,
    ROUND(AVG(order_value), 2) AS avg_order_value,
    ROUND(SUM(order_value), 2) AS total_revenue
FROM order_metrics
GROUP BY order_value_bucket
ORDER BY 
    CASE 
        WHEN order_value_bucket = '0-10' THEN 1
        WHEN order_value_bucket = '10-50' THEN 2
        WHEN order_value_bucket = '50-100' THEN 3
        WHEN order_value_bucket = '100-250' THEN 4
        WHEN order_value_bucket = '250-500' THEN 5
        WHEN order_value_bucket = '500-1000' THEN 6
        ELSE 7
    END;


-- 4.2 Peak Shopping Hours/Days (Temporal Patterns)
-- Business Question: When do customers shop the most?
-- ----------------------------------------------------------------------------
SELECT 
    EXTRACT(HOUR FROM invoice_date) AS hour_of_day,
    EXTRACT(DOW FROM invoice_date) AS day_of_week,  -- 0=Sunday, 6=Saturday
    CASE EXTRACT(DOW FROM invoice_date)
        WHEN 0 THEN 'Sunday'
        WHEN 1 THEN 'Monday'
        WHEN 2 THEN 'Tuesday'
        WHEN 3 THEN 'Wednesday'
        WHEN 4 THEN 'Thursday'
        WHEN 5 THEN 'Friday'
        WHEN 6 THEN 'Saturday'
    END AS day_name,
    COUNT(DISTINCT invoice_no) AS order_count,
    COUNT(DISTINCT customer_id) AS unique_customers,
    ROUND(SUM(quantity * unit_price), 2) AS total_revenue,
    ROUND(AVG(quantity * unit_price), 2) AS avg_transaction_value
FROM ecommerce_data
WHERE invoice_no NOT LIKE 'C%'
    AND customer_id IS NOT NULL
    AND quantity > 0
    AND unit_price > 0
GROUP BY EXTRACT(HOUR FROM invoice_date), 
         EXTRACT(DOW FROM invoice_date),
         day_name
ORDER BY order_count DESC
LIMIT 50;


-- ============================================================================
-- 5. ADVANCED ANALYTICS
-- ============================================================================

-- 5.1 Customer Churn Risk (Customers Who Haven't Purchased Recently)
-- Business Question: Which customers are at risk of churning?
-- ----------------------------------------------------------------------------
WITH customer_last_purchase AS (
    SELECT 
        customer_id,
        MAX(invoice_date) AS last_purchase_date,
        COUNT(DISTINCT invoice_no) AS lifetime_orders,
        SUM(quantity * unit_price) AS lifetime_value
    FROM ecommerce_data
    WHERE invoice_no NOT LIKE 'C%'
        AND customer_id IS NOT NULL
        AND quantity > 0
        AND unit_price > 0
    GROUP BY customer_id
)
SELECT 
    customer_id,
    last_purchase_date,
    DATEDIFF('2010-12-31', last_purchase_date) AS days_since_last_purchase,
    lifetime_orders,
    ROUND(lifetime_value, 2) AS lifetime_value,
    CASE 
        WHEN DATEDIFF('2010-12-31', last_purchase_date) > 180 THEN 'High Risk'
        WHEN DATEDIFF('2010-12-31', last_purchase_date) > 90 THEN 'Medium Risk'
        WHEN DATEDIFF('2010-12-31', last_purchase_date) > 60 THEN 'Low Risk'
        ELSE 'Active'
    END AS churn_risk_category
FROM customer_last_purchase
WHERE DATEDIFF('2010-12-31', last_purchase_date) > 60  -- At least 60 days inactive
ORDER BY lifetime_value DESC, days_since_last_purchase DESC;


-- 5.2 Revenue Concentration (Pareto Analysis - 80/20 Rule)
-- Business Question: What % of revenue comes from top customers/products?
-- ----------------------------------------------------------------------------
WITH customer_revenue_ranked AS (
    SELECT 
        customer_id,
        SUM(quantity * unit_price) AS customer_revenue,
        SUM(SUM(quantity * unit_price)) OVER () AS total_revenue,
        ROW_NUMBER() OVER (ORDER BY SUM(quantity * unit_price) DESC) AS revenue_rank,
        COUNT(*) OVER () AS total_customers
    FROM ecommerce_data
    WHERE invoice_no NOT LIKE 'C%'
        AND customer_id IS NOT NULL
        AND quantity > 0
        AND unit_price > 0
    GROUP BY customer_id
)
SELECT 
    'Top 20% Customers' AS segment,
    COUNT(*) AS customer_count,
    ROUND(SUM(customer_revenue), 2) AS revenue,
    ROUND(SUM(customer_revenue) / MAX(total_revenue) * 100, 2) AS revenue_percentage
FROM customer_revenue_ranked
WHERE revenue_rank <= total_customers * 0.2
UNION ALL
SELECT 
    'Bottom 80% Customers' AS segment,
    COUNT(*) AS customer_count,
    ROUND(SUM(customer_revenue), 2) AS revenue,
    ROUND(SUM(customer_revenue) / MAX(total_revenue) * 100, 2) AS revenue_percentage
FROM customer_revenue_ranked
WHERE revenue_rank > total_customers * 0.2;


-- 5.3 Customer Purchase Frequency Distribution
-- Business Question: How frequently do different customer segments purchase?
-- ----------------------------------------------------------------------------
WITH purchase_intervals AS (
    SELECT 
        customer_id,
        invoice_date,
        LAG(invoice_date) OVER (PARTITION BY customer_id ORDER BY invoice_date) AS prev_purchase_date,
        DATEDIFF(
            invoice_date, 
            LAG(invoice_date) OVER (PARTITION BY customer_id ORDER BY invoice_date)
        ) AS days_between_purchases
    FROM (
        SELECT DISTINCT customer_id, DATE(invoice_date) AS invoice_date
        FROM ecommerce_data
        WHERE invoice_no NOT LIKE 'C%'
            AND customer_id IS NOT NULL
    ) t
)
SELECT 
    CASE 
        WHEN days_between_purchases <= 7 THEN '1 Week or Less'
        WHEN days_between_purchases <= 30 THEN '1-4 Weeks'
        WHEN days_between_purchases <= 90 THEN '1-3 Months'
        WHEN days_between_purchases <= 180 THEN '3-6 Months'
        ELSE '6+ Months'
    END AS purchase_frequency_bucket,
    COUNT(*) AS repeat_purchase_count,
    ROUND(AVG(days_between_purchases), 2) AS avg_days_between_purchases,
    COUNT(DISTINCT customer_id) AS unique_customers
FROM purchase_intervals
WHERE days_between_purchases IS NOT NULL
GROUP BY purchase_frequency_bucket
ORDER BY 
    CASE 
        WHEN purchase_frequency_bucket = '1 Week or Less' THEN 1
        WHEN purchase_frequency_bucket = '1-4 Weeks' THEN 2
        WHEN purchase_frequency_bucket = '1-3 Months' THEN 3
        WHEN purchase_frequency_bucket = '3-6 Months' THEN 4
        ELSE 5
    END;


-- ============================================================================
-- 6. DATA QUALITY QUERIES
-- ============================================================================

-- 6.1 Data Quality Summary
-- Purpose: Check for missing values, duplicates, and anomalies
-- ----------------------------------------------------------------------------
SELECT 
    'Total Records' AS metric,
    COUNT(*) AS value
FROM ecommerce_data
UNION ALL
SELECT 
    'Missing CustomerID',
    COUNT(*)
FROM ecommerce_data
WHERE customer_id IS NULL
UNION ALL
SELECT 
    'Missing Description',
    COUNT(*)
FROM ecommerce_data
WHERE description IS NULL
UNION ALL
SELECT 
    'Cancelled Orders (InvoiceNo starts with C)',
    COUNT(*)
FROM ecommerce_data
WHERE invoice_no LIKE 'C%'
UNION ALL
SELECT 
    'Negative Quantities',
    COUNT(*)
FROM ecommerce_data
WHERE quantity < 0
UNION ALL
SELECT 
    'Zero or Negative Prices',
    COUNT(*)
FROM ecommerce_data
WHERE unit_price <= 0
UNION ALL
SELECT 
    'Duplicate Records',
    COUNT(*) - COUNT(DISTINCT (invoice_no, stock_code, customer_id, invoice_date, quantity, unit_price))
FROM ecommerce_data;


-- ============================================================================
-- END OF SQL QUERIES
-- ============================================================================

-- Notes:
-- 1. Replace 'ecommerce_data' with your actual table name
-- 2. DATE_TRUNC, DATEDIFF, and EXTRACT functions may vary by database
--    - PostgreSQL: DATE_TRUNC, AGE, EXTRACT
--    - MySQL: DATE_FORMAT, DATEDIFF, EXTRACT
--    - Snowflake: DATE_TRUNC, DATEDIFF, EXTRACT
-- 3. Adjust date '2010-12-31' to your dataset's max date for recency calculations
-- 4. Add indexes on customer_id, invoice_no, invoice_date for performance
-- 5. Test queries on a subset before running on full dataset

-- Recommended Indexes:
-- CREATE INDEX idx_customer_id ON ecommerce_data(customer_id);
-- CREATE INDEX idx_invoice_no ON ecommerce_data(invoice_no);
-- CREATE INDEX idx_invoice_date ON ecommerce_data(invoice_date);
-- CREATE INDEX idx_stock_code ON ecommerce_data(stock_code);
-- CREATE INDEX idx_composite ON ecommerce_data(customer_id, invoice_date, invoice_no);
