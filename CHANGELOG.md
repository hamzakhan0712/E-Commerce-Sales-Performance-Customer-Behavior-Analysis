# Changelog

All notable changes to the E-Commerce Sales Performance & Customer Behavior Analysis project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-12-18

### Added
- **Initial Release** of E-Commerce Sales Performance & Customer Behavior Analysis
- Complete data analysis workflow (5 modular notebooks)
  - `01_data_overview.ipynb` - Initial data exploration
  - `02_data_cleaning.ipynb` - Data quality and cleaning
  - `03_feature_engineering.ipynb` - Customer/product/time metrics
  - `04_exploratory_data_analysis.ipynb` - Business-driven EDA
  - `05_insights_and_recommendations.ipynb` - Strategic insights
- **Reusable Python modules** (`src/`)
  - `utils.py` - Helper functions for data loading, logging, config
  - `data_cleaning.py` - Data cleaning and validation functions
  - `feature_engineering.py` - RFM segmentation and metric creation
- **8 engineered datasets**:
  - `cleaned_data.csv` (504,730 rows)
  - `customer_data.csv` (401,604 rows)
  - `customer_metrics.csv` (4,312 customers with RFM segmentation)
  - `product_metrics.csv` (4,581 products)
  - `monthly_revenue.csv` (13 months)
  - `country_metrics.csv` (40 countries)
  - `invoice_metrics.csv` (20,951 orders)
  - `raw_data.csv` (original 525,461 rows)
- **Comprehensive documentation**:
  - `README.md` - Project overview with business context
  - `docs/data_dictionary.md` - Complete column documentation
  - `docs/data_quality_report.md` - Data quality metrics
  - `docs/implementation_plan.md` - Strategic roadmap
- **Configuration management**:
  - `config/config.yaml` - Centralized project configuration
  - `requirements.txt` - Python dependencies
  - `environment.yml` - Conda environment specification
  - `.gitignore` - Version control exclusions
- **Automation scripts**:
  - `scripts/run_pipeline.py` - End-to-end pipeline execution
  - `scripts/export_results.py` - Report generation
- **SQL queries** (`sql/analysis_queries.sql`) - Database-ready analyses
- **Unit tests** (`tests/`) - Data validation and function testing
- **Key findings**:
  - 79.4% repeat purchase rate (world-class retention)
  - Top 34% of customers generate 80% of revenue
  - Q4 seasonality: 26% of annual revenue
  - £5.5M+ addressable revenue opportunities identified
- **10 costed business recommendations** with ROI projections
- **RFM customer segmentation**:
  - Champions (21%)
  - Loyal Customers (23.9%)
  - Potential Loyalists (26.2%)
  - At Risk (16.3%)
  - Lost Customers (12.6%)

### Changed
- N/A (Initial release)

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- N/A

---

## [Unreleased]

### Planned Features
- **Predictive Models**:
  - Customer churn prediction (Random Forest)
  - CLV forecasting (Linear Regression)
  - Demand forecasting for Q4 inventory
- **Interactive Dashboards**:
  - Power BI/Tableau executive dashboard
  - Customer health score monitoring
  - Real-time KPI tracking
- **Advanced Analytics**:
  - Market basket analysis (association rules)
  - Customer journey mapping
  - A/B testing framework
- **API Integration**:
  - REST API for model serving
  - Automated data pipeline (Airflow)
- **Enhanced Documentation**:
  - Video walkthroughs
  - Interactive notebook tutorials
  - Model deployment guide

---

## Version History

### Version Naming Convention
- **Major version** (X.0.0): Breaking changes, major feature additions
- **Minor version** (1.X.0): New features, backward-compatible
- **Patch version** (1.0.X): Bug fixes, documentation updates

### Support Policy
- **Current version (1.0.0)**: Full support, active development
- **Previous versions**: Security fixes only

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on proposing changes.

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

---

**Maintained by:** Hamza Khan  
**Last Updated:** December 18, 2024
