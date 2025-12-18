#!/usr/bin/env python3
"""
Export Results Script for E-commerce Analytics

This script exports analysis results to various formats:
- CSV files for data sharing
- Excel workbooks with multiple sheets
- Summary statistics reports
- JSON for API integrations

Usage:
    python export_results.py --format csv
    python export_results.py --format excel --output reports/analysis.xlsx
    python export_results.py --format all --include-charts
    
Author: Data Analytics Team
Version: 1.0.0
Last Updated: December 2024
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd
from loguru import logger

try:
    from src.utils import (
        load_config,
        setup_logging,
        load_data,
        format_currency,
        format_percentage
    )
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)


class ResultsExporter:
    """Export analysis results to various formats"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize results exporter
        
        Args:
            config_path: Path to configuration file
        """
        self.config = load_config(config_path)
        
        # Setup logging
        log_config = self.config.get("logging", {})
        setup_logging(
            log_file=log_config.get("file", "logs/export.log"),
            level=log_config.get("level", "INFO")
        )
        
        logger.info("=" * 80)
        logger.info("RESULTS EXPORT UTILITY")
        logger.info("=" * 80)
        logger.info(f"Export started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Load all datasets
        self._load_datasets()
    
    def _load_datasets(self):
        """Load all processed datasets"""
        logger.info("Loading processed datasets...")
        
        processed_dir = Path(self.config['file_paths']['processed_dir'])
        
        try:
            self.cleaned_data = load_data(str(processed_dir / "cleaned_data.csv"))
            self.customer_metrics = load_data(str(processed_dir / "customer_metrics.csv"))
            self.customer_segments = load_data(str(processed_dir / "customer_segments.csv"))
            self.product_metrics = load_data(str(processed_dir / "product_metrics.csv"))
            self.monthly_revenue = load_data(str(processed_dir / "monthly_revenue.csv"))
            self.country_metrics = load_data(str(processed_dir / "country_metrics.csv"))
            self.invoice_metrics = load_data(str(processed_dir / "invoice_metrics.csv"))
            
            logger.info("✓ All datasets loaded successfully")
            
        except FileNotFoundError as e:
            logger.error(f"Dataset not found: {e}")
            logger.error("Please run the pipeline first: python scripts/run_pipeline.py")
            sys.exit(1)
    
    def export_csv(self, output_dir: str = "exports/csv"):
        """
        Export all datasets to CSV files
        
        Args:
            output_dir: Output directory for CSV files
        """
        logger.info(f"\nExporting to CSV format...")
        logger.info(f"Output directory: {output_dir}")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        datasets = {
            'cleaned_data': self.cleaned_data,
            'customer_metrics': self.customer_metrics,
            'customer_segments': self.customer_segments,
            'product_metrics': self.product_metrics,
            'monthly_revenue': self.monthly_revenue,
            'country_metrics': self.country_metrics,
            'invoice_metrics': self.invoice_metrics
        }
        
        for name, df in datasets.items():
            file_path = output_path / f"{name}.csv"
            df.to_csv(file_path, index=False)
            logger.info(f"  ✓ Exported {name}.csv ({len(df):,} records)")
        
        logger.info(f"✓ CSV export complete - {len(datasets)} files created")
    
    def export_excel(self, output_file: str = "exports/ecommerce_analysis.xlsx"):
        """
        Export all datasets to a single Excel workbook with multiple sheets
        
        Args:
            output_file: Output Excel file path
        """
        logger.info(f"\nExporting to Excel format...")
        logger.info(f"Output file: {output_file}")
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Export each dataset to a separate sheet
            self.cleaned_data.to_excel(writer, sheet_name='Cleaned Data', index=False)
            logger.info(f"  ✓ Sheet 'Cleaned Data' ({len(self.cleaned_data):,} records)")
            
            self.customer_metrics.to_excel(writer, sheet_name='Customer Metrics', index=False)
            logger.info(f"  ✓ Sheet 'Customer Metrics' ({len(self.customer_metrics):,} records)")
            
            self.customer_segments.to_excel(writer, sheet_name='Customer Segments', index=False)
            logger.info(f"  ✓ Sheet 'Customer Segments' ({len(self.customer_segments):,} records)")
            
            self.product_metrics.to_excel(writer, sheet_name='Product Metrics', index=False)
            logger.info(f"  ✓ Sheet 'Product Metrics' ({len(self.product_metrics):,} records)")
            
            self.monthly_revenue.to_excel(writer, sheet_name='Monthly Revenue', index=False)
            logger.info(f"  ✓ Sheet 'Monthly Revenue' ({len(self.monthly_revenue):,} records)")
            
            self.country_metrics.to_excel(writer, sheet_name='Country Metrics', index=False)
            logger.info(f"  ✓ Sheet 'Country Metrics' ({len(self.country_metrics):,} records)")
            
            self.invoice_metrics.to_excel(writer, sheet_name='Invoice Metrics', index=False)
            logger.info(f"  ✓ Sheet 'Invoice Metrics' ({len(self.invoice_metrics):,} records)")
            
            # Add summary sheet
            summary_df = self._create_summary_dataframe()
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            logger.info(f"  ✓ Sheet 'Summary' (Key metrics)")
        
        logger.info(f"✓ Excel export complete - {output_file}")
    
    def export_json(self, output_dir: str = "exports/json"):
        """
        Export summary statistics and key metrics to JSON format
        
        Args:
            output_dir: Output directory for JSON files
        """
        logger.info(f"\nExporting to JSON format...")
        logger.info(f"Output directory: {output_dir}")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Overall summary
        summary = self._create_summary_dict()
        with open(output_path / "summary.json", 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        logger.info(f"  ✓ Exported summary.json")
        
        # Customer segments
        segments = self.customer_segments['CustomerSegment'].value_counts().to_dict()
        with open(output_path / "customer_segments.json", 'w') as f:
            json.dump(segments, f, indent=2)
        logger.info(f"  ✓ Exported customer_segments.json")
        
        # Top products
        top_products = (
            self.product_metrics
            .nlargest(20, 'TotalRevenue')[['StockCode', 'Description', 'TotalRevenue', 'UnitsSold']]
            .to_dict('records')
        )
        with open(output_path / "top_products.json", 'w') as f:
            json.dump(top_products, f, indent=2, default=str)
        logger.info(f"  ✓ Exported top_products.json")
        
        # Monthly trends
        monthly_trends = (
            self.monthly_revenue[['YearMonth', 'Revenue', 'Orders', 'UniqueCustomers']]
            .to_dict('records')
        )
        with open(output_path / "monthly_trends.json", 'w') as f:
            json.dump(monthly_trends, f, indent=2, default=str)
        logger.info(f"  ✓ Exported monthly_trends.json")
        
        # Country performance
        country_performance = (
            self.country_metrics
            .nlargest(10, 'TotalRevenue')[['Country', 'TotalRevenue', 'TotalCustomers', 'TotalOrders']]
            .to_dict('records')
        )
        with open(output_path / "country_performance.json", 'w') as f:
            json.dump(country_performance, f, indent=2, default=str)
        logger.info(f"  ✓ Exported country_performance.json")
        
        logger.info(f"✓ JSON export complete - 5 files created")
    
    def export_summary_report(self, output_file: str = "exports/summary_report.txt"):
        """
        Export a human-readable text summary report
        
        Args:
            output_file: Output text file path
        """
        logger.info(f"\nGenerating summary report...")
        logger.info(f"Output file: {output_file}")
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Calculate metrics
        total_revenue = self.cleaned_data['TotalPrice'].sum()
        total_orders = self.cleaned_data['InvoiceNo'].nunique()
        total_customers = self.cleaned_data['CustomerID'].nunique()
        total_products = self.cleaned_data['StockCode'].nunique()
        avg_order_value = total_revenue / total_orders
        
        # Segment distribution
        segment_counts = self.customer_segments['CustomerSegment'].value_counts()
        
        # Top products
        top_5_products = self.product_metrics.nlargest(5, 'TotalRevenue')
        
        # Top countries
        top_5_countries = self.country_metrics.nlargest(5, 'TotalRevenue')
        
        # Create report
        report = f"""
{'=' * 80}
E-COMMERCE ANALYTICS SUMMARY REPORT
{'=' * 80}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Data Period: December 2009 - December 2010

{'─' * 80}
EXECUTIVE SUMMARY
{'─' * 80}
Total Revenue:              {format_currency(total_revenue)}
Total Orders:               {total_orders:,}
Total Customers:            {total_customers:,}
Total Products:             {total_products:,}
Average Order Value:        {format_currency(avg_order_value)}

{'─' * 80}
CUSTOMER SEGMENTS
{'─' * 80}
"""
        
        for segment, count in segment_counts.items():
            pct = count / len(self.customer_segments) * 100
            report += f"{segment:<30} {count:>8,} ({pct:>5.1f}%)\n"
        
        report += f"\n{'─' * 80}\n"
        report += "TOP 5 PRODUCTS BY REVENUE\n"
        report += f"{'─' * 80}\n"
        
        for idx, row in top_5_products.iterrows():
            report += f"\n{row['Description'][:50]}\n"
            report += f"  Stock Code: {row['StockCode']}\n"
            report += f"  Revenue:    {format_currency(row['TotalRevenue'])}\n"
            report += f"  Units Sold: {row['UnitsSold']:,}\n"
        
        report += f"\n{'─' * 80}\n"
        report += "TOP 5 COUNTRIES BY REVENUE\n"
        report += f"{'─' * 80}\n"
        
        for idx, row in top_5_countries.iterrows():
            report += f"\n{row['Country']}\n"
            report += f"  Revenue:   {format_currency(row['TotalRevenue'])}\n"
            report += f"  Customers: {row['TotalCustomers']:,}\n"
            report += f"  Orders:    {row['TotalOrders']:,}\n"
        
        report += f"\n{'─' * 80}\n"
        report += "MONTHLY REVENUE TREND\n"
        report += f"{'─' * 80}\n"
        
        for idx, row in self.monthly_revenue.iterrows():
            growth = row.get('MonthOverMonthGrowth', 0)
            growth_str = f"+{growth:.1f}%" if growth > 0 else f"{growth:.1f}%"
            report += f"{row['YearMonth']}    {format_currency(row['Revenue']):>15}    {growth_str:>8}\n"
        
        report += f"\n{'=' * 80}\n"
        report += "END OF REPORT\n"
        report += f"{'=' * 80}\n"
        
        # Save report
        with open(output_path, 'w') as f:
            f.write(report)
        
        logger.info(f"✓ Summary report created - {output_file}")
        
        # Also print to console
        print(report)
    
    def _create_summary_dataframe(self) -> pd.DataFrame:
        """Create a summary dataframe with key metrics"""
        total_revenue = self.cleaned_data['TotalPrice'].sum()
        total_orders = self.cleaned_data['InvoiceNo'].nunique()
        total_customers = self.cleaned_data['CustomerID'].nunique()
        total_products = self.cleaned_data['StockCode'].nunique()
        avg_order_value = total_revenue / total_orders
        
        summary_data = {
            'Metric': [
                'Total Revenue',
                'Total Orders',
                'Total Customers',
                'Total Products',
                'Average Order Value',
                'Repeat Customer Rate',
                'Total Countries',
                'Data Period Start',
                'Data Period End',
                'Total Transactions'
            ],
            'Value': [
                format_currency(total_revenue),
                f"{total_orders:,}",
                f"{total_customers:,}",
                f"{total_products:,}",
                format_currency(avg_order_value),
                format_percentage(
                    (self.customer_metrics['TotalOrders'] > 1).sum() / len(self.customer_metrics)
                ),
                f"{self.cleaned_data['Country'].nunique():,}",
                self.cleaned_data['InvoiceDate'].min().strftime('%Y-%m-%d'),
                self.cleaned_data['InvoiceDate'].max().strftime('%Y-%m-%d'),
                f"{len(self.cleaned_data):,}"
            ]
        }
        
        return pd.DataFrame(summary_data)
    
    def _create_summary_dict(self) -> Dict:
        """Create a summary dictionary with key metrics"""
        total_revenue = float(self.cleaned_data['TotalPrice'].sum())
        total_orders = int(self.cleaned_data['InvoiceNo'].nunique())
        total_customers = int(self.cleaned_data['CustomerID'].nunique())
        total_products = int(self.cleaned_data['StockCode'].nunique())
        
        summary = {
            'generated_at': datetime.now().isoformat(),
            'data_period': {
                'start': self.cleaned_data['InvoiceDate'].min().strftime('%Y-%m-%d'),
                'end': self.cleaned_data['InvoiceDate'].max().strftime('%Y-%m-%d')
            },
            'overall_metrics': {
                'total_revenue': round(total_revenue, 2),
                'total_orders': total_orders,
                'total_customers': total_customers,
                'total_products': total_products,
                'average_order_value': round(total_revenue / total_orders, 2),
                'total_transactions': len(self.cleaned_data)
            },
            'customer_metrics': {
                'repeat_customer_rate': round(
                    (self.customer_metrics['TotalOrders'] > 1).sum() / len(self.customer_metrics) * 100, 2
                ),
                'average_clv': round(self.customer_metrics['CustomerLifetimeValue'].mean(), 2),
                'average_orders_per_customer': round(self.customer_metrics['TotalOrders'].mean(), 2)
            },
            'geographic_metrics': {
                'total_countries': int(self.cleaned_data['Country'].nunique()),
                'top_country': self.country_metrics.nlargest(1, 'TotalRevenue')['Country'].iloc[0],
                'top_country_revenue': round(
                    float(self.country_metrics.nlargest(1, 'TotalRevenue')['TotalRevenue'].iloc[0]), 2
                )
            },
            'segment_distribution': self.customer_segments['CustomerSegment'].value_counts().to_dict()
        }
        
        return summary
    
    def export_all(self, output_base_dir: str = "exports"):
        """
        Export to all formats
        
        Args:
            output_base_dir: Base output directory
        """
        logger.info("\n" + "=" * 80)
        logger.info("EXPORTING TO ALL FORMATS")
        logger.info("=" * 80)
        
        base_path = Path(output_base_dir)
        
        # Export to all formats
        self.export_csv(str(base_path / "csv"))
        self.export_excel(str(base_path / "ecommerce_analysis.xlsx"))
        self.export_json(str(base_path / "json"))
        self.export_summary_report(str(base_path / "summary_report.txt"))
        
        logger.info("\n" + "=" * 80)
        logger.info("ALL EXPORTS COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)
        logger.info(f"Output location: {base_path}")


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Export E-commerce Analytics Results",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Export to CSV
  python export_results.py --format csv
  
  # Export to Excel
  python export_results.py --format excel --output reports/analysis.xlsx
  
  # Export to JSON
  python export_results.py --format json
  
  # Export summary report
  python export_results.py --format summary
  
  # Export to all formats
  python export_results.py --format all
        """
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config/config.yaml',
        help='Path to configuration file (default: config/config.yaml)'
    )
    
    parser.add_argument(
        '--format',
        type=str,
        choices=['csv', 'excel', 'json', 'summary', 'all'],
        default='all',
        help='Export format (default: all)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Output file/directory path (format-specific)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='exports',
        help='Base output directory (default: exports)'
    )
    
    return parser.parse_args()


def main():
    """Main entry point for export script"""
    args = parse_arguments()
    
    try:
        # Initialize exporter
        exporter = ResultsExporter(config_path=args.config)
        
        # Export based on format
        if args.format == 'csv':
            output = args.output or f"{args.output_dir}/csv"
            exporter.export_csv(output)
            
        elif args.format == 'excel':
            output = args.output or f"{args.output_dir}/ecommerce_analysis.xlsx"
            exporter.export_excel(output)
            
        elif args.format == 'json':
            output = args.output or f"{args.output_dir}/json"
            exporter.export_json(output)
            
        elif args.format == 'summary':
            output = args.output or f"{args.output_dir}/summary_report.txt"
            exporter.export_summary_report(output)
            
        elif args.format == 'all':
            exporter.export_all(args.output_dir)
        
        logger.info("\n✓ Export completed successfully")
        return 0
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        logger.error("Please run the pipeline first: python scripts/run_pipeline.py")
        return 1
        
    except Exception as e:
        logger.error(f"Export failed with error: {e}")
        logger.exception("Full traceback:")
        return 1


if __name__ == "__main__":
    sys.exit(main())
