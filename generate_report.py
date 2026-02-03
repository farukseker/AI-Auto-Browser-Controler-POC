#!/usr/bin/env python3
"""
Standalone report generator - Generate reports from execution logs
"""
import argparse
import json
import sys
from pathlib import Path

from reporter import ExecutionReporter


def generate_reports_from_log(log_file: str, output_dir: str = './reports', formats: list = None):
    """
    Generate reports from an existing execution log file
    
    Args:
        log_file: Path to JSON log file
        output_dir: Directory to save reports
        formats: List of formats to generate ('html', 'json', 'text')
    """
    
    if formats is None:
        formats = ['html']
    
    # Load log file
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            log_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Log file not found: {log_file}")
        return False
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in log file: {log_file}")
        return False
    
    # Create reporter
    reporter = ExecutionReporter(log_data)
    
    # Generate reports
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    generated_reports = []
    
    try:
        if 'html' in formats:
            html_path = reporter.generate_html_report(f"{output_dir}/report.html")
            generated_reports.append(('HTML', html_path))
            print(f"✓ HTML report generated: {html_path}")
        
        if 'json' in formats:
            json_path = reporter.generate_json_report(f"{output_dir}/report.json")
            generated_reports.append(('JSON', json_path))
            print(f"✓ JSON report generated: {json_path}")
        
        if 'text' in formats:
            text_path = reporter.generate_text_report(f"{output_dir}/report.txt")
            generated_reports.append(('Text', text_path))
            print(f"✓ Text report generated: {text_path}")
        
        # Print summary
        summary = reporter.generate_summary()
        print("\n" + "="*60)
        print("EXECUTION SUMMARY")
        print("="*60)
        print(f"Execution ID:    {summary['execution_id']}")
        print(f"Status:          {summary['status'].upper()}")
        print(f"Total Steps:     {summary['total_steps']}")
        print(f"Successful:      {summary['successful_steps']}")
        print(f"Failed:          {summary['failed_steps']}")
        print(f"Success Rate:    {summary['success_rate']}%")
        print(f"Duration:        {summary['duration']}")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"Error generating reports: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Generate reports from Selenium execution logs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate HTML report
  python generate_report.py execution_log.json
  
  # Generate all formats
  python generate_report.py execution_log.json --format all
  
  # Generate specific formats
  python generate_report.py execution_log.json --format html json
  
  # Custom output directory
  python generate_report.py execution_log.json --output ./my_reports
        """
    )
    
    parser.add_argument(
        'log_file',
        help='Path to execution log JSON file'
    )
    
    parser.add_argument(
        '--format',
        nargs='+',
        choices=['html', 'json', 'text', 'all'],
        default=['html'],
        help='Report format(s) to generate (default: html)'
    )
    
    parser.add_argument(
        '--output',
        default='./reports',
        help='Output directory for reports (default: ./reports)'
    )
    
    args = parser.parse_args()
    
    # Handle 'all' format
    if 'all' in args.format:
        formats = ['html', 'json', 'text']
    else:
        formats = args.format
    
    # Generate reports
    success = generate_reports_from_log(args.log_file, args.output, formats)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
