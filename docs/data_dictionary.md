# 📖 Data Dictionary

> **Comprehensive documentation of all datasets, columns, and business logic**

**Last Updated:** December 18, 2024  
**Project:** E-Commerce Sales Performance & Customer Behavior Analysis  
**Author:** Hamza Khan

---

## 📊 Dataset Overview

| Dataset | Rows | Columns | Description | File Path |
|---------|------|---------|-------------|-----------|
| **Raw Data** | 525,461 | 8 | Original unprocessed transactions | `data/raw_data.csv` |
| **Cleaned Data** | 504,730 | 15 | Cleaned & enriched transactions | `data/cleaned_data.csv` |
| **Customer Data** | 401,604 | 15 | B2C customer transactions only | `data/customer_data.csv` |
| **Customer Metrics** | 4,312 | 17 | Customer-level aggregated metrics with RFM segmentation | `data/customer_metrics.csv` |
| **Product Metrics** | 4,581 | 7 | Product-level performance metrics | `data/product_metrics.csv` |
| **Monthly Revenue** | 13 | 5 | Time-series monthly aggregations | `data/monthly_revenue.csv` |
| **Country Metrics** | 40 | 5 | Geographic revenue distribution | `data/country_metrics.csv` |
| **Invoice Metrics** | 20,951 | 5 | Order-level basket analysis | `data/invoice_metrics.csv` |

---

## 📁 Dataset 1: Raw Data (`raw_data.csv`)

**Description:** Original unprocessed dataset from UCI Machine Learning Repository  
**Source:** UK-based online retail company  
**Date Range:** December 1, 2009 - December 9, 2010  
**Business Context:** Transactional data including both B2C and B2B sales

### Columns

| Column Name | Data Type | Description | Valid Range | Missing Values | Example |
|-------------|-----------|-------------|-------------|----------------|---------|
| **InvoiceNo** | `object` | Unique transaction identifier | 6-digit integer OR 'C' prefix for cancellations | 0 | `536365` |
| **StockCode** | `object` | Product SKU identifier | 5-character alphanumeric | 0 | `85123A` |
| **Description** | `object` | Product name/description | Free text | 2,928 (0.56%) | `WHITE HANGING HEART` |
| **Quantity** | `int64` | Units purchased per transaction | -80,995 to 80,995 | 0 | `6` |
| **InvoiceDate** | `datetime64` | Transaction timestamp | 2009-12-01 to 2010-12-09 | 0 | `2010-12-01 08:26:00` |
| **UnitPrice** | `float64` | Price per unit (GBP £) | 0 to £13,541.33 | 0 | `2.55` |
| **CustomerID** | `float64` | Unique customer identifier | 12,346 to 18,287 | 106,290 (20.2%) | `17850.0` |
| **Country** | `object` | Customer country | 40 unique countries | 0 | `United Kingdom` |

### Data Quality Issues (Raw)
- ❌ **Cancelled Orders:** 10,206 rows (1.94%) with 'C' prefix in InvoiceNo
- ❌ **Missing CustomerID:** 106,290 rows (20.2%) - B2B/guest checkouts
- ❌ **Negative Quantities:** 10,624 rows - returns/cancellations
- ❌ **Negative Prices:** 2 rows - data entry errors
- ❌ **Duplicates:** 400 rows - exact transaction duplicates
- ❌ **Missing Descriptions:** 2,928 rows (0.56%)

---

## 📁 Dataset 2: Cleaned Data (`cleaned_data.csv`)

**Description:** Processed dataset after data cleaning and feature engineering  
**Purpose:** Analysis-ready transactions for EDA and modeling  
**Cleaning Actions:**
- ✅ Removed cancelled orders (InvoiceNo starting with 'C')
- ✅ Removed missing CustomerIDs (focus on B2C)
- ✅ Removed negative quantities and prices
- ✅ Removed exact duplicates
- ✅ Created 7 engineered features

### Columns

#### Original Columns (8)
Same as Raw Data (see above), with quality issues resolved.

#### Engineered Columns (7)

| Column Name | Data Type | Description | Calculation | Valid Range | Example |
|-------------|-----------|-------------|-------------|-------------|---------|
| **TotalPrice** | `float64` | Revenue per transaction line | `Quantity × UnitPrice` | £0.15 to £168,469.60 | `15.30` |
| **Year** | `int64` | Year of transaction | Extracted from `InvoiceDate` | 2009, 2010 | `2010` |
| **Month** | `int64` | Month of transaction | Extracted from `InvoiceDate` | 1-12 | `11` |
| **Day** | `int64` | Day of month | Extracted from `InvoiceDate` | 1-31 | `15` |
| **Hour** | `int64` | Hour of day (24-hour format) | Extracted from `InvoiceDate` | 0-23 | `14` |
| **DayOfWeek** | `int64` | Day of week (0=Monday) | Calculated from `InvoiceDate` | 0-6 | `2` (Wednesday) |
| **YearMonth** | `period[M]` | Year-month aggregation | Formatted as `YYYY-MM` | 2009-12 to 2010-12 | `2010-11` |

### Business Rules
- **TotalPrice Calculation:** Always positive (Quantity > 0 AND UnitPrice > 0)
- **Date Range:** Only transactions from Dec 2009 to Dec 2010
- **CustomerID Requirement:** All rows have valid CustomerID (B2C focus)

---

## 📁 Dataset 3: Customer Data (`customer_data.csv`)

**Description:** Subset of cleaned data containing only B2C customer transactions  
**Purpose:** Customer-specific analysis (excludes B2B/guest checkouts)  
**Difference from Cleaned Data:** Excludes rows without CustomerID

### Columns
Same as Cleaned Data (15 columns). See Dataset 2 above.

### Key Statistics
- **Unique Customers:** 4,312
- **Date Range:** December 1, 2009 - December 9, 2010
- **Countries:** 40
- **Products:** 4,581 unique SKUs

---

## 📁 Dataset 4: Customer Metrics (`customer_metrics.csv`)

**Description:** Customer-level aggregated metrics with RFM segmentation  
**Grain:** 1 row per customer (4,312 customers)  
**Purpose:** Customer lifetime value analysis, segmentation, retention strategies

### Columns

| Column Name | Data Type | Description | Calculation | Valid Range | Example |
|-------------|-----------|-------------|-------------|-------------|---------|
| **CustomerID** | `float64` | Unique customer identifier | From cleaned data | 12,346 to 18,287 | `17850.0` |
| **CustomerLifetimeValue** | `float64` | Total revenue from customer (CLV) | `SUM(TotalPrice)` per customer | £3.75 to £279,489.02 | `1,889.88` |
| **TotalOrders** | `int64` | Number of orders placed | `COUNT(DISTINCT InvoiceNo)` | 1 to 210 | `5` |
| **TotalQuantity** | `int64` | Total items purchased | `SUM(Quantity)` | 1 to 196,175 | `623` |
| **AvgBasketValue** | `float64` | Average order value (AOV) | `CLV / TotalOrders` | £3.75 to £168,469.60 | £377.98 |
| **FirstPurchaseDate** | `datetime64` | Date of first transaction | `MIN(InvoiceDate)` | 2009-12-01 to 2010-12-07 | `2010-03-15` |
| **LastPurchaseDate** | `datetime64` | Date of last transaction | `MAX(InvoiceDate)` | 2009-12-01 to 2010-12-09 | `2010-11-28` |
| **CustomerTenure_Days** | `int64` | Days between first and last purchase | `LastPurchaseDate - FirstPurchaseDate` | 0 to 373 | `258` |
| **Recency_Days** | `int64` | Days since last purchase | `Analysis Date - LastPurchaseDate` | 0 to 374 | `11` |
| **PurchaseFrequency** | `float64` | Orders per month | `TotalOrders / (CustomerTenure_Days / 30)` | 0.13 to 30.0 | `0.93` |
| **IsRepeatCustomer** | `int64` | Repeat purchase indicator | `1 if TotalOrders > 1 else 0` | 0, 1 | `1` |
| **UniqueProductsPurchased** | `int64` | Distinct SKUs purchased | `COUNT(DISTINCT StockCode)` | 1 to 1,807 | `42` |

#### RFM Segmentation Columns

| Column Name | Data Type | Description | Calculation | Valid Range | Example |
|-------------|-----------|-------------|-------------|-------------|---------|
| **R_Score** | `int64` | Recency score (1=worst, 5=best) | Quintile ranking of `Recency_Days` (inverted) | 1-5 | `5` |
| **F_Score** | `int64` | Frequency score (1=worst, 5=best) | Quintile ranking of `TotalOrders` | 1-5 | `4` |
| **M_Score** | `int64` | Monetary score (1=worst, 5=best) | Quintile ranking of `CustomerLifetimeValue` | 1-5 | `5` |
| **RFM_Score** | `object` | Concatenated RFM scores | `str(R_Score) + str(F_Score) + str(M_Score)` | '111' to '555' | `'545'` |
| **CustomerSegment** | `object` | Business segment classification | See segmentation rules below | 5 categories | `Champions` |

### RFM Segmentation Rules

| Segment | RFM Criteria | Business Definition | Count | % of Base |
|---------|--------------|---------------------|-------|-----------|
| **Champions** | R >= 4, F >= 4, M >= 4 | Recent, frequent, high-spending customers | 906 | 21.0% |
| **Loyal Customers** | R >= 3, F >= 3, M >= 3 (not Champions) | Consistent customers with good engagement | 1,029 | 23.9% |
| **Potential Loyalists** | R >= 3, F = 2-3, M = 2-3 | Recent customers with growth potential | 1,130 | 26.2% |
| **At Risk** | R = 2-3, F >= 2, M >= 2 (not above) | Declining engagement, need reactivation | 703 | 16.3% |
| **Lost Customers** | R = 1, Any F, Any M | Long time since last purchase, likely churned | 544 | 12.6% |

### Business Rules
- **Analysis Date:** December 9, 2010 (last date in dataset)
- **CLV Includes:** All revenue from customer (including returns if applicable)
- **Single Transaction Customers:** TotalOrders = 1 → IsRepeatCustomer = 0

---

## 📁 Dataset 5: Product Metrics (`product_metrics.csv`)

**Description:** Product-level performance metrics  
**Grain:** 1 row per product (4,581 SKUs)  
**Purpose:** Product portfolio optimization, inventory planning, hero product identification

### Columns

| Column Name | Data Type | Description | Calculation | Valid Range | Example |
|-------------|-----------|-------------|-------------|-------------|---------|
| **StockCode** | `object` | Product SKU identifier | From cleaned data | 5-character alphanumeric | `85123A` |
| **Description** | `object` | Product name/description | Most common description for SKU | Free text | `WHITE HANGING HEART` |
| **TotalRevenue** | `float64` | Total revenue from product | `SUM(TotalPrice)` per product | £0.42 to £206,245.48 | `169,913.28` |
| **UnitsSold** | `int64` | Total quantity sold | `SUM(Quantity)` per product | 1 to 56,449 | `13,685` |
| **OrderCount** | `int64` | Number of orders containing product | `COUNT(DISTINCT InvoiceNo)` | 1 to 3,281 | `2,019` |
| **UniqueCustomers** | `int64` | Distinct customers who bought product | `COUNT(DISTINCT CustomerID)` | 1 to 1,275 | `818` |
| **AvgPrice** | `float64` | Average unit price | `TotalRevenue / UnitsSold` | £0.04 to £12,500.00 | `12.42` |

### Business Insights
- **Hero Product:** REGENCY CAKESTAND 3 TIER (£169,913 revenue)
- **Highest Reach:** WHITE HANGING HEART (3,281 orders, 1,275 customers)
- **Price Range:** £0.04 to £12,500 (wide product mix)

---

## 📁 Dataset 6: Monthly Revenue (`monthly_revenue.csv`)

**Description:** Time-series monthly aggregations  
**Grain:** 1 row per month (13 months)  
**Purpose:** Trend analysis, seasonality detection, forecasting

### Columns

| Column Name | Data Type | Description | Calculation | Valid Range | Example |
|-------------|-----------|-------------|-------------|-------------|---------|
| **YearMonth** | `period[M]` | Year-month identifier | Formatted as `YYYY-MM` | 2009-12 to 2010-12 | `2010-11` |
| **MonthlyRevenue** | `float64` | Total revenue in month | `SUM(TotalPrice)` per month | £551,313 to £1,464,293 | `1,464,293.46` |
| **MonthlyOrders** | `int64` | Number of orders in month | `COUNT(DISTINCT InvoiceNo)` per month | 1,377 to 2,747 | `2,747` |
| **MonthlyCustomers** | `int64` | Active customers in month | `COUNT(DISTINCT CustomerID)` per month | 948 to 1,469 | `1,469` |
| **RevenueGrowth_Pct** | `float64` | Month-over-month revenue growth | `((Current - Previous) / Previous) × 100` | -70.2% to +50.7% | `26.4` |

### Business Rules
- **Incomplete Month:** December 2010 has only 9 days of data (excluded from trend analysis)
- **Growth Calculation:** First month (Dec 2009) has NaN for growth rate

### Key Statistics
- **Peak Month:** November 2010 (£1.46M revenue, 2,747 orders)
- **Low Month:** February 2010 (£551K revenue)
- **Average Monthly Revenue:** £790,059

---

## 📁 Dataset 7: Country Metrics (`country_metrics.csv`)

**Description:** Geographic revenue distribution  
**Grain:** 1 row per country (40 countries)  
**Purpose:** International expansion strategy, market prioritization

### Columns

| Column Name | Data Type | Description | Calculation | Valid Range | Example |
|-------------|-----------|-------------|-------------|-------------|---------|
| **Country** | `object` | Customer country name | From cleaned data | 40 unique values | `United Kingdom` |
| **TotalRevenue** | `float64` | Total revenue from country | `SUM(TotalPrice)` per country | £133 to £8,812,312 | `8,812,312.45` |
| **TotalOrders** | `int64` | Number of orders from country | `COUNT(DISTINCT InvoiceNo)` per country | 1 to 19,290 | `19,290` |
| **UniqueCustomers** | `int64` | Customers from country | `COUNT(DISTINCT CustomerID)` per country | 1 to 3,969 | `3,969` |
| **RevenuePct** | `float64` | Percentage of total revenue | `(TotalRevenue / SUM(TotalRevenue)) × 100` | 0.001% to 85.8% | `85.8` |

### Geographic Insights
- **UK Dominance:** 85.8% of revenue (£8.8M)
- **Top International:** EIRE (£381K), Netherlands (£269K), Germany (£202K)
- **EIRE Anomaly:** 5 customers = £381K (£76K per customer - B2B model)

---

## 📁 Dataset 8: Invoice Metrics (`invoice_metrics.csv`)

**Description:** Order-level basket analysis  
**Grain:** 1 row per invoice (20,951 orders)  
**Purpose:** AOV analysis, basket size optimization, cross-sell opportunities

### Columns

| Column Name | Data Type | Description | Calculation | Valid Range | Example |
|-------------|-----------|-------------|-------------|-------------|---------|
| **InvoiceNo** | `object` | Unique order identifier | From cleaned data | 6-digit integer | `536365` |
| **CustomerID** | `float64` | Customer who placed order | From cleaned data | 12,346 to 18,287 | `17850.0` |
| **InvoiceValue** | `float64` | Total order value (AOV) | `SUM(TotalPrice)` per invoice | £0.42 to £168,469.60 | `300.24` |
| **TotalItems** | `int64` | Total quantity of items | `SUM(Quantity)` per invoice | 1 to 80,995 | `23` |
| **UniqueProducts** | `int64` | Distinct SKUs in order | `COUNT(DISTINCT StockCode)` per invoice | 1 to 420 | `10` |

### Key Statistics
- **Mean AOV:** £490.28 (median: £300.24)
- **Mean Basket Size:** 24.2 items (median: 23)
- **Mean Product Diversity:** 11.8 unique products (median: 10)

---

## 🔑 Key Business Definitions

### Customer Lifetime Value (CLV)
**Formula:** `SUM(TotalPrice)` for all transactions by customer  
**Business Meaning:** Total historical revenue generated by customer  
**Use Case:** Customer segmentation, retention prioritization  
**Limitation:** Does not predict future value (historical only)

### Average Order Value (AOV)
**Formula:** `Total Revenue / Total Orders`  
**Business Meaning:** Typical transaction size  
**Use Case:** Pricing strategy, upsell/cross-sell optimization  
**Industry Benchmark:** £300-£500 for UK e-commerce

### Repeat Purchase Rate
**Formula:** `(Customers with >1 order / Total Customers) × 100`  
**Business Meaning:** Percentage of customers who return  
**Use Case:** Retention effectiveness measurement  
**Industry Benchmark:** 30-40% (this dataset: 79.4%)

### RFM Analysis
**Recency (R):** How recently customer purchased (lower days = better)  
**Frequency (F):** How often customer purchases (higher orders = better)  
**Monetary (M):** How much customer spends (higher CLV = better)  
**Scoring:** Each dimension scored 1-5 (quintiles), concatenated into 3-digit score

---

## 📊 Data Lineage

```
raw_data.csv (525,461 rows)
    │
    ├─► Data Cleaning (96% retention)
    │   ├─ Remove cancelled orders (-10,206)
    │   ├─ Remove missing CustomerIDs (-106,290)
    │   ├─ Remove negative values (-6,835)
    │   └─ Remove duplicates (-400)
    │
    ├─► cleaned_data.csv (504,730 rows)
    │   │
    │   ├─► Feature Engineering
    │   │   ├─ TotalPrice = Quantity × UnitPrice
    │   │   └─ Date components (Year, Month, Day, Hour, YearMonth)
    │   │
    │   └─► customer_data.csv (401,604 rows)
    │       │
    │       ├─► Aggregation by CustomerID
    │       │   └─► customer_metrics.csv (4,312 rows)
    │       │       └─ RFM Segmentation Applied
    │       │
    │       ├─► Aggregation by StockCode
    │       │   └─► product_metrics.csv (4,581 rows)
    │       │
    │       ├─► Aggregation by YearMonth
    │       │   └─► monthly_revenue.csv (13 rows)
    │       │
    │       ├─► Aggregation by Country
    │       │   └─► country_metrics.csv (40 rows)
    │       │
    │       └─► Aggregation by InvoiceNo
    │           └─► invoice_metrics.csv (20,951 rows)
```

---

## ⚠️ Data Quality Notes

### Known Limitations
1. **December 2010 Incomplete:** Only 9 days of data (Dec 1-9) → excluded from trend analysis
2. **Missing CustomerIDs:** 20% of raw transactions (B2B/guest checkouts) excluded from customer analysis
3. **Single Year Data:** Seasonality patterns need multi-year validation
4. **No Returns Data:** Cannot separate genuine returns from data errors
5. **Price Outliers:** Some £10,000+ transactions (wholesale orders) skew averages

### Data Quality Metrics
- **Completeness:** 96% of raw data retained after cleaning
- **Validity:** 100% of cleaned data passes business rules
- **Consistency:** No conflicting values in cleaned datasets
- **Accuracy:** Manual spot-checks performed on top 100 customers

---

## 📧 Contacts

**Data Owner:** Hamza Khan  
**Last Updated:** December 18, 2024  
**Version:** 1.0.0  
**Questions?** Open an issue on [GitHub](https://github.com/hamzakhan0712/E-Commerce-Sales-Performance-Customer-Behavior-Analysis)

---

**This data dictionary is a living document. Updates will be versioned and tracked in CHANGELOG.md.**