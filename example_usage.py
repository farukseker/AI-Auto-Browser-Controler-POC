"""
Example usage of AI-controlled Selenium with runtime monitoring
"""
from orchestrator import AISeleniumOrchestrator


def example_basic_automation():
    """
    Basic example: Google search with HTML report
    """
    
    # Initialize orchestrator
    orchestrator = AISeleniumOrchestrator(
        openrouter_api_key="YOUR_OPENROUTER_API_KEY",
        model="openai/gpt-4-turbo",
        headless=False,  # Set True for production
        auto_retry=True,
        max_retries=2
    )
    
    try:
        # Define task in natural language
        task = """
        Go to google.com and search for "Selenium automation best practices"
        """
        
        # Execute
        success = orchestrator.execute_task(task)
        
        # Generate HTML report
        report_path = orchestrator.generate_report(format='html')
        print(f"\nHTML Report generated: {report_path}")
        
        # Also generate JSON report
        json_report = orchestrator.generate_report(format='json')
        print(f"JSON Report generated: {json_report}")
        
        # Get summary
        summary = orchestrator.get_summary()
        print(f"\nSuccess Rate: {summary['success_rate']}%")
        print(f"Total Duration: {summary['duration']}")
            
    finally:
        orchestrator.cleanup()


def example_form_filling():
    """
    Advanced example: Form automation with text report
    """
    
    orchestrator = AISeleniumOrchestrator(
        openrouter_api_key="YOUR_OPENROUTER_API_KEY",
        headless=False,
        auto_retry=True
    )
    
    try:
        task = """
        Navigate to https://www.example.com/contact
        Fill out the contact form:
        - Name field: John Doe
        - Email field: john@example.com
        - Message: Testing automated form filling
        Then click the submit button
        Wait 3 seconds after submission
        """
        
        success = orchestrator.execute_task(task)
        
        # Generate text report for email/logs
        report_path = orchestrator.generate_report(format='text')
        print(f"\nText report saved: {report_path}")
        
        # Read and print summary
        with open(report_path, 'r') as f:
            print(f.read())
        
    finally:
        orchestrator.cleanup()


def example_with_custom_monitoring():
    """
    Example with custom event listener and detailed reporting
    """
    
    orchestrator = AISeleniumOrchestrator(
        openrouter_api_key="YOUR_OPENROUTER_API_KEY",
        headless=False
    )
    
    # Add custom listener
    def custom_listener(event):
        if event.status == "failed":
            print(f"ALERT: Step {event.step_index} failed!")
            print(f"Screenshot saved: {event.screenshot_path}")
            
    orchestrator.monitor.add_listener(custom_listener)
    
    try:
        task = "Go to github.com and search for selenium projects"
        orchestrator.execute_task(task)
        
        # Generate all report formats
        html_report = orchestrator.generate_report(format='html')
        json_report = orchestrator.generate_report(format='json')
        text_report = orchestrator.generate_report(format='text')
        
        print("\nReports generated:")
        print(f"  HTML: {html_report}")
        print(f"  JSON: {json_report}")
        print(f"  Text: {text_report}")
        
    finally:
        orchestrator.cleanup()


def example_report_only():
    """
    Example: Generate report from existing execution
    """
    
    from reporter import ExecutionReporter
    import json
    
    # Load existing log
    with open('execution_log.json', 'r') as f:
        log_data = json.load(f)
    
    # Create reporter
    reporter = ExecutionReporter(log_data)
    
    # Generate reports
    html_path = reporter.generate_html_report('./reports/report.html')
    json_path = reporter.generate_json_report('./reports/report.json')
    text_path = reporter.generate_text_report('./reports/report.txt')
    
    print(f"Reports generated from existing log:")
    print(f"  HTML: {html_path}")
    print(f"  JSON: {json_path}")
    print(f"  Text: {text_path}")


if __name__ == "__main__":
    # Run basic example with reporting
    print("Running automation with reporting...")
    example_basic_automation()
    
    # Uncomment to run other examples:
    # example_form_filling()
    # example_with_custom_monitoring()
    # example_report_only()
