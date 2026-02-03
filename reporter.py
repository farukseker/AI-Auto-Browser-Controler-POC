"""
Reporting module - Generate execution reports in various formats
"""
import json
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class ExecutionReporter:
    """Generate comprehensive execution reports"""
    
    def __init__(self, monitor_events: List[Dict]):
        self.events = monitor_events
        self.start_time = None
        self.end_time = None
        
        if self.events:
            self.start_time = self.events[0].get('timestamp')
            self.end_time = self.events[-1].get('timestamp')
    
    def generate_summary(self) -> Dict:
        """Generate execution summary statistics"""
        
        total_steps = len([e for e in self.events if e['status'] == 'started'])
        successful_steps = len([e for e in self.events if e['status'] == 'success'])
        failed_steps = len([e for e in self.events if e['status'] == 'failed'])
        
        success_rate = (successful_steps / total_steps * 100) if total_steps > 0 else 0
        
        # Calculate duration
        duration = self._calculate_duration()
        
        # Collect errors
        errors = [
            {
                'step': e['step_index'],
                'action': e['action'],
                'error': e.get('error'),
                'screenshot': e.get('screenshot_path')
            }
            for e in self.events if e['status'] == 'failed'
        ]
        
        # Collect URLs visited
        urls_visited = list(set([
            e['url'] for e in self.events 
            if e.get('url') and e['status'] == 'success'
        ]))
        
        return {
            'execution_id': self._generate_execution_id(),
            'timestamp': self.start_time,
            'duration': duration,
            'total_steps': total_steps,
            'successful_steps': successful_steps,
            'failed_steps': failed_steps,
            'success_rate': round(success_rate, 2),
            'urls_visited': urls_visited,
            'errors': errors,
            'status': 'completed' if failed_steps == 0 else 'failed'
        }
    
    def generate_json_report(self, filepath: str):
        """Generate detailed JSON report"""
        
        report = {
            'summary': self.generate_summary(),
            'detailed_steps': self.events,
            'metadata': {
                'report_generated': datetime.now().isoformat(),
                'format': 'json',
                'version': '1.0'
            }
        }
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def generate_html_report(self, filepath: str):
        """Generate visual HTML report"""
        
        summary = self.generate_summary()
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Selenium Execution Report - {summary['execution_id']}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #f5f5f5;
            padding: 20px;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
        }}
        
        .header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
        }}
        
        .header p {{
            opacity: 0.9;
            font-size: 14px;
        }}
        
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f9fafb;
        }}
        
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        
        .stat-card.success {{
            border-left-color: #10b981;
        }}
        
        .stat-card.failed {{
            border-left-color: #ef4444;
        }}
        
        .stat-card h3 {{
            font-size: 14px;
            color: #6b7280;
            margin-bottom: 8px;
            font-weight: 500;
        }}
        
        .stat-card .value {{
            font-size: 32px;
            font-weight: 700;
            color: #1f2937;
        }}
        
        .stat-card.success .value {{
            color: #10b981;
        }}
        
        .stat-card.failed .value {{
            color: #ef4444;
        }}
        
        .section {{
            padding: 30px;
        }}
        
        .section h2 {{
            font-size: 20px;
            margin-bottom: 20px;
            color: #1f2937;
            border-bottom: 2px solid #e5e7eb;
            padding-bottom: 10px;
        }}
        
        .step {{
            padding: 15px;
            margin-bottom: 10px;
            background: #f9fafb;
            border-radius: 6px;
            border-left: 3px solid #e5e7eb;
        }}
        
        .step.success {{
            border-left-color: #10b981;
            background: #f0fdf4;
        }}
        
        .step.failed {{
            border-left-color: #ef4444;
            background: #fef2f2;
        }}
        
        .step-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }}
        
        .step-title {{
            font-weight: 600;
            color: #1f2937;
        }}
        
        .step-status {{
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
        }}
        
        .step-status.success {{
            background: #d1fae5;
            color: #065f46;
        }}
        
        .step-status.failed {{
            background: #fee2e2;
            color: #991b1b;
        }}
        
        .step-details {{
            font-size: 14px;
            color: #6b7280;
        }}
        
        .step-details p {{
            margin: 4px 0;
        }}
        
        .error-box {{
            background: #fef2f2;
            border: 1px solid #fecaca;
            border-radius: 6px;
            padding: 12px;
            margin-top: 8px;
        }}
        
        .error-text {{
            color: #991b1b;
            font-size: 13px;
            font-family: 'Courier New', monospace;
        }}
        
        .url-list {{
            list-style: none;
        }}
        
        .url-list li {{
            padding: 10px;
            background: #f9fafb;
            margin-bottom: 8px;
            border-radius: 4px;
            font-size: 14px;
            color: #4b5563;
        }}
        
        .url-list li a {{
            color: #667eea;
            text-decoration: none;
        }}
        
        .url-list li a:hover {{
            text-decoration: underline;
        }}
        
        .footer {{
            text-align: center;
            padding: 20px;
            background: #f9fafb;
            color: #6b7280;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Selenium Execution Report</h1>
            <p>Execution ID: {summary['execution_id']}</p>
            <p>Generated: {summary['timestamp']}</p>
        </div>
        
        <div class="summary">
            <div class="stat-card">
                <h3>Total Steps</h3>
                <div class="value">{summary['total_steps']}</div>
            </div>
            
            <div class="stat-card success">
                <h3>Successful</h3>
                <div class="value">{summary['successful_steps']}</div>
            </div>
            
            <div class="stat-card failed">
                <h3>Failed</h3>
                <div class="value">{summary['failed_steps']}</div>
            </div>
            
            <div class="stat-card">
                <h3>Success Rate</h3>
                <div class="value">{summary['success_rate']}%</div>
            </div>
            
            <div class="stat-card">
                <h3>Duration</h3>
                <div class="value">{summary['duration']}</div>
            </div>
            
            <div class="stat-card">
                <h3>Status</h3>
                <div class="value" style="font-size: 20px; text-transform: uppercase;">{summary['status']}</div>
            </div>
        </div>
        
        <div class="section">
            <h2>Execution Steps</h2>
            {self._generate_steps_html()}
        </div>
        
        {self._generate_errors_html(summary['errors'])}
        
        {self._generate_urls_html(summary['urls_visited'])}
        
        <div class="footer">
            <p>AI-Controlled Selenium Automation Report</p>
            <p>Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>"""
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filepath
    
    def generate_text_report(self, filepath: str):
        """Generate simple text report"""
        
        summary = self.generate_summary()
        
        report_lines = [
            "="*70,
            "SELENIUM EXECUTION REPORT",
            "="*70,
            "",
            f"Execution ID: {summary['execution_id']}",
            f"Timestamp: {summary['timestamp']}",
            f"Duration: {summary['duration']}",
            "",
            "SUMMARY",
            "-"*70,
            f"Total Steps:      {summary['total_steps']}",
            f"Successful Steps: {summary['successful_steps']}",
            f"Failed Steps:     {summary['failed_steps']}",
            f"Success Rate:     {summary['success_rate']}%",
            f"Status:           {summary['status'].upper()}",
            "",
            "EXECUTION STEPS",
            "-"*70,
        ]
        
        # Add steps
        for event in self.events:
            if event['status'] == 'started':
                continue
                
            status_symbol = "✓" if event['status'] == 'success' else "✗"
            step_line = f"{status_symbol} Step {event['step_index']}: {event['action']}"
            
            if event.get('selector'):
                step_line += f" ({event['selector']})"
            
            report_lines.append(step_line)
            
            if event['status'] == 'failed' and event.get('error'):
                report_lines.append(f"  Error: {event['error']}")
        
        # Add errors section
        if summary['errors']:
            report_lines.extend([
                "",
                "ERRORS",
                "-"*70,
            ])
            
            for error in summary['errors']:
                report_lines.append(f"Step {error['step']}: {error['action']}")
                report_lines.append(f"  Error: {error['error']}")
                if error.get('screenshot'):
                    report_lines.append(f"  Screenshot: {error['screenshot']}")
                report_lines.append("")
        
        # Add URLs
        if summary['urls_visited']:
            report_lines.extend([
                "URLS VISITED",
                "-"*70,
            ])
            
            for url in summary['urls_visited']:
                report_lines.append(f"  - {url}")
        
        report_lines.extend([
            "",
            "="*70,
            f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "="*70,
        ])
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        return filepath
    
    def _generate_steps_html(self) -> str:
        """Generate HTML for execution steps"""
        
        steps_html = []
        
        for event in self.events:
            if event['status'] == 'started':
                continue
            
            status_class = event['status']
            status_text = event['status'].upper()
            
            step_html = f"""
            <div class="step {status_class}">
                <div class="step-header">
                    <div class="step-title">Step {event['step_index']}: {event['action'].upper()}</div>
                    <div class="step-status {status_class}">{status_text}</div>
                </div>
                <div class="step-details">
            """
            
            if event.get('selector'):
                step_html += f"<p><strong>Selector:</strong> {event['selector']}</p>"
            
            if event.get('url'):
                step_html += f"<p><strong>URL:</strong> {event['url']}</p>"
            
            if event.get('value'):
                step_html += f"<p><strong>Value:</strong> {event['value']}</p>"
            
            if event['status'] == 'failed' and event.get('error'):
                step_html += f"""
                <div class="error-box">
                    <div class="error-text">{event['error']}</div>
                </div>
                """
            
            step_html += """
                </div>
            </div>
            """
            
            steps_html.append(step_html)
        
        return ''.join(steps_html)
    
    def _generate_errors_html(self, errors: List[Dict]) -> str:
        """Generate HTML for errors section"""
        
        if not errors:
            return ""
        
        return f"""
        <div class="section">
            <h2>Errors ({len(errors)})</h2>
            {''.join([f'''
            <div class="step failed">
                <div class="step-header">
                    <div class="step-title">Step {error['step']}: {error['action'].upper()}</div>
                </div>
                <div class="error-box">
                    <div class="error-text">{error['error']}</div>
                    {f'<p style="margin-top: 8px; color: #991b1b;">Screenshot: {error["screenshot"]}</p>' if error.get('screenshot') else ''}
                </div>
            </div>
            ''' for error in errors])}
        </div>
        """
    
    def _generate_urls_html(self, urls: List[str]) -> str:
        """Generate HTML for URLs section"""
        
        if not urls:
            return ""
        
        return f"""
        <div class="section">
            <h2>URLs Visited ({len(urls)})</h2>
            <ul class="url-list">
                {''.join([f'<li><a href="{url}" target="_blank">{url}</a></li>' for url in urls])}
            </ul>
        </div>
        """
    
    def _calculate_duration(self) -> str:
        """Calculate execution duration"""
        
        if not self.start_time or not self.end_time:
            return "N/A"
        
        try:
            start = datetime.fromisoformat(self.start_time)
            end = datetime.fromisoformat(self.end_time)
            duration = end - start
            
            seconds = duration.total_seconds()
            
            if seconds < 60:
                return f"{seconds:.1f}s"
            elif seconds < 3600:
                minutes = seconds / 60
                return f"{minutes:.1f}m"
            else:
                hours = seconds / 3600
                return f"{hours:.1f}h"
        except:
            return "N/A"
    
    def _generate_execution_id(self) -> str:
        """Generate unique execution ID"""
        
        if self.start_time:
            return f"exec_{self.start_time.replace(':', '').replace('-', '').replace('.', '')[:15]}"
        
        return f"exec_{datetime.now().strftime('%Y%m%d%H%M%S')}"
