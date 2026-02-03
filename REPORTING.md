# Reporting Quick Reference

## Generate Reports During Execution

### Automatic (Recommended)
Reports are automatically generated when using `main.py`:

```bash
python main.py
# After task completes, HTML report is generated
```

### Programmatic
```python
from orchestrator import AISeleniumOrchestrator

orchestrator = AISeleniumOrchestrator(openrouter_api_key="YOUR_KEY")
orchestrator.execute_task("Your task here")

# Generate HTML report
html_path = orchestrator.generate_report(format='html')

# Generate JSON report
json_path = orchestrator.generate_report(format='json')

# Generate text report
text_path = orchestrator.generate_report(format='text')

orchestrator.cleanup()
```

## Generate Reports from Existing Logs

### Command Line
```bash
# Single format
python generate_report.py logs/execution_20240203_143022.json

# Multiple formats
python generate_report.py logs/execution_20240203_143022.json --format html json text

# All formats
python generate_report.py logs/execution_20240203_143022.json --format all

# Custom output directory
python generate_report.py logs/execution_20240203_143022.json --output ./my_reports
```

### Python Script
```python
from reporter import ExecutionReporter
import json

# Load log
with open('execution_log.json', 'r') as f:
    log_data = json.load(f)

# Create reporter
reporter = ExecutionReporter(log_data)

# Generate reports
reporter.generate_html_report('./reports/report.html')
reporter.generate_json_report('./reports/report.json')
reporter.generate_text_report('./reports/report.txt')

# Get summary
summary = reporter.generate_summary()
print(f"Success Rate: {summary['success_rate']}%")
```

## Report Formats Comparison

| Format | Best For | Features |
|--------|----------|----------|
| **HTML** | Sharing, Visualization | Interactive, color-coded, charts |
| **JSON** | Integration, Analysis | Structured, machine-readable |
| **Text** | Logs, Email | Simple, readable, portable |

## What's Included in Reports

✓ Execution summary (steps, success rate, duration)
✓ Step-by-step execution details
✓ Error messages and stack traces
✓ Screenshot paths for failed steps
✓ All URLs visited during execution
✓ Timestamps for each step
✓ Execution status (completed/failed)

## Get Summary Only

```python
# Get summary without generating full report
summary = orchestrator.get_summary()

print(f"Execution ID: {summary['execution_id']}")
print(f"Status: {summary['status']}")
print(f"Total Steps: {summary['total_steps']}")
print(f"Successful: {summary['successful_steps']}")
print(f"Failed: {summary['failed_steps']}")
print(f"Success Rate: {summary['success_rate']}%")
print(f"Duration: {summary['duration']}")
print(f"URLs Visited: {summary['urls_visited']}")
print(f"Errors: {summary['errors']}")
```

## Custom Report Directory

```python
# Set custom directory for all reports
orchestrator.generate_report(
    format='html',
    output_dir='./custom_reports'
)
```

## Batch Report Generation

```python
import os
from reporter import ExecutionReporter
import json

# Process all logs in directory
log_dir = './logs'
report_dir = './reports'

for log_file in os.listdir(log_dir):
    if log_file.endswith('.json'):
        with open(f"{log_dir}/{log_file}", 'r') as f:
            log_data = json.load(f)
        
        reporter = ExecutionReporter(log_data)
        
        # Generate HTML report with same name
        report_name = log_file.replace('.json', '.html')
        reporter.generate_html_report(f"{report_dir}/{report_name}")
        
        print(f"Generated report for {log_file}")
```

## Report File Naming

Default naming pattern:
- HTML: `report_YYYYMMDD_HHMMSS.html`
- JSON: `report_YYYYMMDD_HHMMSS.json`
- Text: `report_YYYYMMDD_HHMMSS.txt`

## Troubleshooting

**Reports not generating?**
- Check `reports` directory exists
- Verify execution completed (has events)
- Check file permissions

**Empty reports?**
- Ensure task was executed before generating report
- Verify log data is not empty

**Missing screenshots in report?**
- Screenshots only captured on errors
- Check `screenshots` directory for files
- Verify screenshot path in events

## Tips

1. **Always generate reports** - They're invaluable for debugging
2. **Use HTML for humans** - Best for sharing and reviewing
3. **Use JSON for machines** - Best for integration and analysis
4. **Keep logs organized** - Use timestamp-based naming
5. **Archive old reports** - Move completed reports to archive directory
