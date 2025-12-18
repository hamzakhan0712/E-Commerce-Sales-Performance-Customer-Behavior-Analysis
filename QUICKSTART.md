# 🚀 Quick Start Guide

Get up and running with the E-Commerce Analytics Platform in 5 minutes!

---

## ⚡ Prerequisites

- **Python 3.8+** (recommended: 3.10)
- **Git** (for cloning repository)
- **8GB RAM** minimum
- **2GB disk space** for data and outputs

---

## 📥 Step 1: Clone & Setup (2 minutes)

```bash
# Clone repository
git clone https://github.com/hamzakhan0712/E-Commerce-Sales-Performance-Customer-Behavior-Analysis.git
cd E-Commerce-Sales-Performance-Customer-Behavior-Analysis

# Create conda environment (RECOMMENDED)
conda env create -f environment.yml
conda activate ecommerce-analytics

# OR use pip
pip install -r requirements.txt
```

**✅ Verify installation:**
```bash
python -c "import pandas, numpy, matplotlib; print('All packages installed!')"
```

---

## 🎯 Step 2: Run Complete Pipeline (2 minutes)

```bash
# Execute full workflow (load → clean → features → save → report)
python scripts/run_pipeline.py --verbose
```

**Expected Output:**
```
========================================
E-COMMERCE DATA ANALYTICS PIPELINE
========================================
✓ Loaded 541,909 raw records
✓ Cleaned to 504,730 records (93.1% retention)
✓ Engineered 6 feature datasets
✓ Saved 7 files to data/processed/
✓ Generated summary report

Total execution time: 45.23 seconds
========================================
```

**What just happened?**
1. Loaded raw data from `data/data.csv`
2. Cleaned data (removed cancelled orders, missing values, duplicates)
3. Created 6 feature datasets (customer metrics, RFM segments, etc.)
4. Saved results to `data/processed/`
5. Generated summary report in `reports/`

---

## 📊 Step 3: Export Results (1 minute)

```bash
# Export to all formats (CSV, Excel, JSON, Text)
python scripts/export_results.py --format all
```

**Expected Output:**
```
✓ 7 CSV files → exports/csv/
✓ Excel workbook → exports/ecommerce_analysis.xlsx (8 sheets)
✓ 5 JSON files → exports/json/
✓ Summary report → exports/summary_report.txt
```

**Find your exports:**
- **CSV**: `exports/csv/*.csv` (7 files)
- **Excel**: `exports/ecommerce_analysis.xlsx` (1 workbook, 8 sheets)
- **JSON**: `exports/json/*.json` (5 API-ready files)
- **Report**: `exports/summary_report.txt` (human-readable summary)

---

## 🔬 Step 4: Explore Analysis (Optional)

### Option A: View Notebooks
```bash
# Launch Jupyter Lab
jupyter lab

# Open notebooks in this order:
# 01_data_overview.ipynb
# 02_data_cleaning.ipynb
# 03_feature_engineering.ipynb
# 04_exploratory_data_analysis.ipynb
# 05_insights_and_recommendations.ipynb
```

### Option B: View Processed Data
```bash
# Quickly inspect cleaned data
python -c "import pandas as pd; df = pd.read_csv('data/processed/cleaned_data.csv'); print(df.info()); print('\n', df.head())"
```

### Option C: View Summary Report
```bash
# Open the text summary (Windows)
notepad exports/summary_report.txt

# Or Linux/Mac
cat exports/summary_report.txt
```

---

## 🧪 Step 5: Run Tests (Optional but Recommended)

```bash
# Run all tests with coverage report
pytest tests/ -v --cov=src --cov-report=html

# Expected: 55+ tests PASSED, >85% coverage

# View coverage report in browser
# Open: htmlcov/index.html
```

---

## 🎓 What You Get

After following these steps, you have:

✅ **Cleaned dataset** (504K rows, 99.35% revenue retention)  
✅ **6 feature datasets** (customers, products, monthly, countries, etc.)  
✅ **RFM customer segments** (Champions, Loyal, At Risk, Lost, etc.)  
✅ **Business insights** (£10.3M revenue, 79.4% repeat rate)  
✅ **Export formats** (CSV, Excel, JSON, Text)  
✅ **Visualizations** (20+ charts in notebooks)  
✅ **SQL queries** (30+ production-ready queries)  
✅ **Test coverage** (55+ tests, 85%+ coverage)

---

## 📚 Next Steps

### Learn More
- **[README.md](README.md)** - Complete project documentation
- **[docs/data_dictionary.md](docs/data_dictionary.md)** - Dataset documentation
- **[docs/data_quality_report.md](docs/data_quality_report.md)** - Quality assessment
- **[docs/implementation_plan.md](docs/implementation_plan.md)** - Deployment roadmap

### Customize
- **[config/config.yaml](config/config.yaml)** - Change parameters
- **[src/](src/)** - Modify data processing logic
- **[sql/analysis_queries.sql](sql/analysis_queries.sql)** - Add custom queries

### Extend
- Add predictive models (churn, CLV forecasting)
- Create interactive dashboards (Tableau, Power BI)
- Deploy to cloud (AWS, Azure, GCP)
- Integrate with CRM/marketing platforms

---

## 🆘 Troubleshooting

### Issue: "No module named 'src'"
**Solution:** Run from project root directory:
```bash
cd E-Commerce-Sales-Performance-Customer-Behavior-Analysis
python scripts/run_pipeline.py
```

### Issue: "FileNotFoundError: data/data.csv"
**Solution:** Ensure raw data file exists:
```bash
# Check if file exists
ls -lh data/data.csv  # Linux/Mac
dir data\data.csv     # Windows

# If missing, download from project repository
```

### Issue: "ModuleNotFoundError: No module named 'pandas'"
**Solution:** Install dependencies:
```bash
pip install -r requirements.txt
# OR
conda env create -f environment.yml
```

### Issue: "Memory Error"
**Solution:** Process data in chunks (modify config.yaml):
```yaml
data_processing:
  chunk_size: 50000  # Process 50K rows at a time
```

### Issue: Tests failing
**Solution:** Check Python version and dependencies:
```bash
python --version  # Should be 3.8+
pip list | grep pandas  # Check installed versions
pytest tests/ -v  # Run tests with verbose output
```

---

## 💡 Pro Tips

### 1. Use Verbose Mode
```bash
python scripts/run_pipeline.py --verbose
# Shows progress bars and detailed logging
```

### 2. Run Specific Steps
```bash
# Only run cleaning and features (skip loading raw data)
python scripts/run_pipeline.py --steps clean,features
```

### 3. Check Logs
```bash
# View pipeline execution logs
cat logs/pipeline.log

# View export logs
cat logs/export.log
```

### 4. Dry Run (Validate Without Executing)
```bash
python scripts/run_pipeline.py --dry-run
# Validates configuration without processing data
```

### 5. Export Specific Format
```bash
# Only export CSV files
python scripts/export_results.py --format csv

# Only export Excel
python scripts/export_results.py --format excel --output reports/my_analysis.xlsx
```

---

## 🎯 Success Checklist

After completing this guide, you should be able to:

- [x] Run the complete pipeline in one command
- [x] Export results to multiple formats
- [x] View processed datasets
- [x] Open and run Jupyter notebooks
- [x] Run unit tests successfully
- [x] Understand project structure
- [x] Read documentation
- [x] Troubleshoot common issues

---

## 📞 Need Help?

1. **Read the docs**: Start with [README.md](README.md)
2. **Check examples**: Review notebooks for usage patterns
3. **Run tests**: `pytest tests/ -v` to verify setup
4. **Review code**: All modules have docstrings with examples
5. **Open an issue**: GitHub repository for bug reports

---

## 🎉 You're Ready!

You now have a **production-ready e-commerce analytics platform** running on your machine!

**What's next?**
- Explore the 5 Jupyter notebooks
- Customize SQL queries for your needs
- Add your own analysis and visualizations
- Deploy to production (see implementation_plan.md)
- Share insights with stakeholders

---

**Happy Analyzing! 📊🚀**
