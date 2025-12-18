#!/usr/bin/env python3
"""
E-commerce Data Analytics Pipeline Automation Script

This script orchestrates the complete end-to-end data analytics workflow:
1. Load configuration
2. Read raw data
3. Clean and validate data
4. Engineer features and create derived datasets
5. Save all outputs
6. Generate summary report

Usage:
    python run_pipeline.py --config config/config.yaml
    python run_pipeline.py --input data/raw_data.csv --output data/
    python run_pipeline.py --steps cleaning,features --verbose
    
Author: Data Analytics Team
Version: 1.0.0
Last Updated: December 2024
"""

import argparse
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd
from loguru import logger
from tqdm import tqdm

# Import custom modules
try:
    from src.utils import (
        load_config,
        setup_logging,
        load_data,
        save_data,
        print_dataframe_info,
        get_data_quality_metrics,
        format_currency,
        format_percentage
    )
    from src.data_cleaning import clean_ecommerce_data
    from src.feature_engineering import engineer_all_features
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)


class PipelineRunner:
    """Orchestrates the complete data analytics pipeline"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize pipeline runner
        
        Args:
            config_path: Path to configuration file
        """
        self.config = load_config(config_path)
        self.start_time = time.time()
        self.metrics = {}
        
        # Setup logging
        log_config = self.config.get("logging", {})
        setup_logging(
            log_file=log_config.get("file", "logs/pipeline.log"),
            level=log_config.get("level", "INFO")
        )
        
        logger.info("=" * 80)
        logger.info("E-COMMERCE DATA ANALYTICS PIPELINE")
        logger.info("=" * 80)
        logger.info(f"Pipeline started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Configuration loaded from: {config_path}")
        
    def run(self, steps: Optional[List[str]] = None, verbose: bool = False) -> Dict:
        """
        Run the complete pipeline or specific steps
        
        Args:
            steps: List of steps to run (None = all steps)
                   Options: ['load', 'clean', 'features', 'save', 'report']
            verbose: Enable verbose output
            
        Returns:
            Dictionary with pipeline execution metrics
        """
        all_steps = ['load', 'clean', 'features', 'save', 'report']
        steps_to_run = steps if steps else all_steps
        
        logger.info(f"Steps to execute: {', '.join(steps_to_run)}")
        logger.info("-" * 80)
        
        # Step 1: Load Data
        if 'load' in steps_to_run:
            self.raw_data = self._load_data_step(verbose)
        
        # Step 2: Clean Data
        if 'clean' in steps_to_run:
            self.cleaned_data = self._clean_data_step(verbose)
        
        # Step 3: Engineer Features
        if 'features' in steps_to_run:
            self.feature_datasets = self._feature_engineering_step(verbose)
        
        # Step 4: Save Results
        if 'save' in steps_to_run:
            self._save_results_step(verbose)
        
        # Step 5: Generate Report
        if 'report' in steps_to_run:
            self._generate_report_step(verbose)
        
        # Calculate total execution time
        self.metrics['total_execution_time'] = time.time() - self.start_time
        
        logger.info("=" * 80)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY!")
        logger.info(f"Total execution time: {self.metrics['total_execution_time']:.2f} seconds")
        logger.info("=" * 80)
        
        return self.metrics
    
    def _load_data_step(self, verbose: bool) -> pd.DataFrame:
        """Load raw data from CSV"""
        logger.info("STEP 1: Loading Raw Data")
        logger.info("-" * 80)
        
        file_path = self.config['file_paths']['raw_data']
        logger.info(f"Reading data from: {file_path}")
        
        with tqdm(total=1, desc="Loading data", disable=not verbose) as pbar:
            df = load_data(file_path)
            pbar.update(1)
        
        logger.info(f"✓ Successfully loaded {len(df):,} records")
        
        if verbose:
            print_dataframe_info(df, "Raw Data")
        
        self.metrics['raw_records'] = len(df)
        self.metrics['raw_columns'] = len(df.columns)
        
        return df
    
    def _clean_data_step(self, verbose: bool) -> pd.DataFrame:
        """Clean and validate data"""
        logger.info("\nSTEP 2: Cleaning Data")
        logger.info("-" * 80)
        
        # Get cleaning parameters from config
        cleaning_params = self.config.get('data_cleaning', {})
        business_rules = self.config.get('business_rules', {})
        
        logger.info("Applying data cleaning pipeline...")
        logger.info(f"  - Removing cancelled orders (prefix: {business_rules.get('cancelled_invoice_prefix')})")
        logger.info(f"  - Enforcing minimum quantity: {business_rules.get('min_quantity')}")
        logger.info(f"  - Enforcing minimum unit price: {business_rules.get('min_unit_price')}")
        
        with tqdm(total=1, desc="Cleaning data", disable=not verbose) as pbar:
            df_cleaned = clean_ecommerce_data(
                df=self.raw_data,
                cancelled_prefix=business_rules.get('cancelled_invoice_prefix', 'C'),
                min_quantity=business_rules.get('min_quantity', 1),
                min_unit_price=business_rules.get('min_unit_price', 0.01),
                required_columns=cleaning_params.get('required_columns', []),
                date_column=cleaning_params.get('date_column', 'InvoiceDate'),
                handle_outliers_method=cleaning_params.get('outlier_method', 'keep')
            )
            pbar.update(1)
        
        records_removed = len(self.raw_data) - len(df_cleaned)
        retention_rate = len(df_cleaned) / len(self.raw_data) * 100
        
        logger.info(f"✓ Data cleaning complete")
        logger.info(f"  Records removed: {records_removed:,} ({100 - retention_rate:.2f}%)")
        logger.info(f"  Records retained: {len(df_cleaned):,} ({retention_rate:.2f}%)")
        
        # Data quality metrics
        quality_metrics = get_data_quality_metrics(df_cleaned)
        logger.info(f"  Data quality score: {quality_metrics['completeness_score']:.2f}%")
        
        if verbose:
            print_dataframe_info(df_cleaned, "Cleaned Data")
        
        self.metrics['cleaned_records'] = len(df_cleaned)
        self.metrics['records_removed'] = records_removed
        self.metrics['retention_rate'] = retention_rate
        self.metrics['data_quality_score'] = quality_metrics['completeness_score']
        
        return df_cleaned
    
    def _feature_engineering_step(self, verbose: bool) -> Dict[str, pd.DataFrame]:
        """Engineer features and create derived datasets"""
        logger.info("\nSTEP 3: Engineering Features")
        logger.info("-" * 80)
        
        # Get feature engineering parameters
        rfm_config = self.config.get('rfm', {})
        
        logger.info("Creating derived datasets:")
        logger.info("  1. Customer Metrics (CLV, Recency, Frequency)")
        logger.info("  2. Customer Segments (RFM Analysis)")
        logger.info("  3. Product Metrics (Revenue, Units Sold)")
        logger.info("  4. Monthly Revenue (Time Series)")
        logger.info("  5. Country Metrics (Geographic Analysis)")
        logger.info("  6. Invoice Metrics (Order-level Data)")
        
        with tqdm(total=1, desc="Feature engineering", disable=not verbose) as pbar:
            datasets = engineer_all_features(
                df=self.cleaned_data,
                customer_col='CustomerID',
                invoice_col='InvoiceNo',
                date_col='InvoiceDate',
                product_col='StockCode',
                quantity_col='Quantity',
                price_col='UnitPrice',
                country_col='Country',
                description_col='Description',
                rfm_bins=rfm_config.get('r_bins', [0, 0.2, 0.4, 0.6, 0.8, 1.0]),
                segment_rules=rfm_config.get('segments', {})
            )
            pbar.update(1)
        
        # Unpack datasets
        (customer_df, customer_segments_df, product_df, 
         monthly_df, country_df, invoice_df) = datasets
        
        logger.info(f"✓ Feature engineering complete")
        logger.info(f"  Customer records: {len(customer_df):,}")
        logger.info(f"  Product records: {len(product_df):,}")
        logger.info(f"  Monthly records: {len(monthly_df):,}")
        logger.info(f"  Country records: {len(country_df):,}")
        logger.info(f"  Invoice records: {len(invoice_df):,}")
        
        # Segment distribution
        if 'CustomerSegment' in customer_segments_df.columns:
            segment_counts = customer_segments_df['CustomerSegment'].value_counts()
            logger.info("\n  Customer Segment Distribution:")
            for segment, count in segment_counts.items():
                pct = count / len(customer_segments_df) * 100
                logger.info(f"    {segment}: {count:,} ({pct:.1f}%)")
        
        if verbose:
            print("\n" + "=" * 80)
            print("FEATURE DATASETS SUMMARY")
            print("=" * 80)
            for name, df in [
                ("Customer Metrics", customer_df),
                ("Customer Segments", customer_segments_df),
                ("Product Metrics", product_df),
                ("Monthly Revenue", monthly_df),
                ("Country Metrics", country_df),
                ("Invoice Metrics", invoice_df)
            ]:
                print(f"\n{name}:")
                print(f"  Shape: {df.shape}")
                print(f"  Columns: {', '.join(df.columns.tolist()[:5])}...")
        
        self.metrics['customer_count'] = len(customer_df)
        self.metrics['product_count'] = len(product_df)
        self.metrics['monthly_periods'] = len(monthly_df)
        self.metrics['country_count'] = len(country_df)
        
        return {
            'customer_metrics': customer_df,
            'customer_segments': customer_segments_df,
            'product_metrics': product_df,
            'monthly_revenue': monthly_df,
            'country_metrics': country_df,
            'invoice_metrics': invoice_df
        }
    
    def _save_results_step(self, verbose: bool):
        """Save all processed datasets"""
        logger.info("\nSTEP 4: Saving Results")
        logger.info("-" * 80)
        
        output_dir = Path(self.config['file_paths']['processed_dir'])
        output_dir.mkdir(parents=True, exist_ok=True)
        
        datasets_to_save = [
            (self.cleaned_data, 'cleaned_data'),
            (self.feature_datasets['customer_metrics'], 'customer_metrics'),
            (self.feature_datasets['customer_segments'], 'customer_segments'),
            (self.feature_datasets['product_metrics'], 'product_metrics'),
            (self.feature_datasets['monthly_revenue'], 'monthly_revenue'),
            (self.feature_datasets['country_metrics'], 'country_metrics'),
            (self.feature_datasets['invoice_metrics'], 'invoice_metrics')
        ]
        
        logger.info(f"Saving {len(datasets_to_save)} datasets to: {output_dir}")
        
        with tqdm(total=len(datasets_to_save), desc="Saving files", disable=not verbose) as pbar:
            for df, name in datasets_to_save:
                file_path = output_dir / f"{name}.csv"
                save_data(df, str(file_path))
                logger.info(f"  ✓ Saved {name}.csv ({len(df):,} records)")
                pbar.update(1)
        
        logger.info(f"✓ All datasets saved successfully")
        
        self.metrics['files_saved'] = len(datasets_to_save)
        self.metrics['output_directory'] = str(output_dir)
    
    def _generate_report_step(self, verbose: bool):
        """Generate pipeline execution summary report"""
        logger.info("\nSTEP 5: Generating Summary Report")
        logger.info("-" * 80)
        
        # Calculate business metrics
        total_revenue = (self.cleaned_data['Quantity'] * self.cleaned_data['UnitPrice']).sum()
        avg_order_value = total_revenue / self.cleaned_data['InvoiceNo'].nunique()
        
        # Create report
        report = f"""
{'=' * 80}
E-COMMERCE DATA ANALYTICS PIPELINE - EXECUTION REPORT
{'=' * 80}
Execution Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Pipeline Version: 1.0.0

{'─' * 80}
1. DATA PROCESSING METRICS
{'─' * 80}
Raw Records:              {self.metrics['raw_records']:>15,}
Cleaned Records:          {self.metrics['cleaned_records']:>15,}
Records Removed:          {self.metrics['records_removed']:>15,}
Retention Rate:           {self.metrics['retention_rate']:>14.2f}%
Data Quality Score:       {self.metrics['data_quality_score']:>14.2f}%

{'─' * 80}
2. FEATURE ENGINEERING METRICS
{'─' * 80}
Total Customers:          {self.metrics['customer_count']:>15,}
Total Products:           {self.metrics['product_count']:>15,}
Monthly Periods:          {self.metrics['monthly_periods']:>15,}
Countries:                {self.metrics['country_count']:>15,}
Files Saved:              {self.metrics['files_saved']:>15,}

{'─' * 80}
3. BUSINESS METRICS
{'─' * 80}
Total Revenue:            {format_currency(total_revenue):>15}
Average Order Value:      {format_currency(avg_order_value):>15}
Total Orders:             {self.cleaned_data['InvoiceNo'].nunique():>15,}
Unique Customers:         {self.cleaned_data['CustomerID'].nunique():>15,}
Unique Products:          {self.cleaned_data['StockCode'].nunique():>15,}

{'─' * 80}
4. PERFORMANCE METRICS
{'─' * 80}
Total Execution Time:     {self.metrics['total_execution_time']:>14.2f}s
Output Directory:         {self.metrics['output_directory']}

{'─' * 80}
5. CUSTOMER SEGMENT DISTRIBUTION
{'─' * 80}
"""
        
        # Add segment distribution
        if 'CustomerSegment' in self.feature_datasets['customer_segments'].columns:
            segment_counts = self.feature_datasets['customer_segments']['CustomerSegment'].value_counts()
            for segment, count in segment_counts.items():
                pct = count / len(self.feature_datasets['customer_segments']) * 100
                report += f"{segment:<25} {count:>10,} ({pct:>5.1f}%)\n"
        
        report += f"\n{'=' * 80}\n"
        report += "PIPELINE COMPLETED SUCCESSFULLY\n"
        report += f"{'=' * 80}\n"
        
        # Print report
        print(report)
        
        # Save report to file
        report_dir = Path("reports")
        report_dir.mkdir(exist_ok=True)
        report_file = report_dir / f"pipeline_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(report_file, 'w') as f:
            f.write(report)
        
        logger.info(f"✓ Report saved to: {report_file}")
        
        self.metrics['report_file'] = str(report_file)


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="E-commerce Data Analytics Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full pipeline with default config
  python run_pipeline.py
  
  # Run specific steps
  python run_pipeline.py --steps clean,features
  
  # Use custom config file
  python run_pipeline.py --config custom_config.yaml
  
  # Verbose output
  python run_pipeline.py --verbose
  
  # Dry run (check without executing)
  python run_pipeline.py --dry-run
        """
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config/config.yaml',
        help='Path to configuration file (default: config/config.yaml)'
    )
    
    parser.add_argument(
        '--steps',
        type=str,
        help='Comma-separated list of steps to run (load,clean,features,save,report). Default: all'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output with progress bars and detailed info'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Validate configuration without executing pipeline'
    )
    
    return parser.parse_args()


def main():
    """Main entry point for pipeline execution"""
    args = parse_arguments()
    
    try:
        # Initialize pipeline
        pipeline = PipelineRunner(config_path=args.config)
        
        # Dry run - just validate config
        if args.dry_run:
            logger.info("DRY RUN MODE - Configuration validated successfully")
            logger.info("Pipeline would execute the following steps:")
            steps = args.steps.split(',') if args.steps else ['all']
            for step in steps:
                logger.info(f"  - {step}")
            return 0
        
        # Parse steps
        steps = args.steps.split(',') if args.steps else None
        
        # Run pipeline
        metrics = pipeline.run(steps=steps, verbose=args.verbose)
        
        # Success
        return 0
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        logger.error("Please check that all required files exist and paths are correct")
        return 1
        
    except KeyError as e:
        logger.error(f"Configuration error - missing key: {e}")
        logger.error("Please check your config.yaml file")
        return 1
        
    except Exception as e:
        logger.error(f"Pipeline failed with error: {e}")
        logger.exception("Full traceback:")
        return 1


if __name__ == "__main__":
    sys.exit(main())
