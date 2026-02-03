#!/usr/bin/env python3
"""
AI-Controlled Selenium - Main Demo Script
Run browser automation tasks using natural language commands
"""
import sys
import argparse
from datetime import datetime

from orchestrator import AISeleniumOrchestrator
from config import Config


def run_interactive_mode():
    """Interactive mode - type tasks and see them execute"""
    
    print("\n" + "="*70)
    print(" AI SELENIUM AUTOMATION - INTERACTIVE MODE")
    print("="*70)
    print("\nType your automation tasks in natural language.")
    print("Type 'quit' or 'exit' to stop.\n")
    
    if not Config.validate():
        return
        
    Config.print_config()
    
    orchestrator = AISeleniumOrchestrator(
        openrouter_api_key=Config.OPENROUTER_API_KEY,
        model=Config.OPENROUTER_MODEL,
        headless=Config.HEADLESS,
        auto_retry=Config.AUTO_RETRY,
        max_retries=Config.MAX_RETRIES
    )
    
    try:
        while True:
            try:
                task = input("\nTask: ").strip()
                
                if task.lower() in ['quit', 'exit', 'q']:
                    print("\nExiting...")
                    break
                    
                if not task:
                    continue
                    
                # Execute task
                success = orchestrator.execute_task(task)
                
                # Generate reports
                try:
                    html_report = orchestrator.generate_report(format='html')
                    print(f"\n📊 HTML Report: {html_report}")
                except Exception as e:
                    print(f"Report generation failed: {e}")
                
                # Save log if configured
                if Config.SAVE_LOGS:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    log_file = f"{Config.LOG_DIR}/execution_{timestamp}.json"
                    orchestrator.save_log(log_file)
                    
            except KeyboardInterrupt:
                print("\n\nInterrupted by user")
                break
            except Exception as e:
                print(f"\nError: {e}")
                
    finally:
        orchestrator.cleanup()
        print("\nCleanup complete")


def run_single_task(task: str, save_log: bool = True, generate_reports: bool = True):
    """Execute a single task"""
    
    if not Config.validate():
        return False
        
    orchestrator = AISeleniumOrchestrator(
        openrouter_api_key=Config.OPENROUTER_API_KEY,
        model=Config.OPENROUTER_MODEL,
        headless=Config.HEADLESS,
        auto_retry=Config.AUTO_RETRY,
        max_retries=Config.MAX_RETRIES
    )
    
    try:
        success = orchestrator.execute_task(task)
        
        # Generate reports
        if generate_reports:
            html_report = orchestrator.generate_report(format='html')
            print(f"\n📊 HTML Report: {html_report}")
            
            json_report = orchestrator.generate_report(format='json')
            print(f"📊 JSON Report: {json_report}")
            
            summary = orchestrator.get_summary()
            print(f"\n📈 Success Rate: {summary['success_rate']}%")
            print(f"⏱️  Duration: {summary['duration']}")
        
        if save_log and Config.SAVE_LOGS:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = f"{Config.LOG_DIR}/execution_{timestamp}.json"
            orchestrator.save_log(log_file)
            
        return success
        
    finally:
        orchestrator.cleanup()


def run_demo_tasks():
    """Run predefined demo tasks"""
    
    print("\n" + "="*70)
    print(" AI SELENIUM AUTOMATION - DEMO MODE")
    print("="*70)
    
    demos = [
        {
            "name": "Google Search",
            "task": "Go to google.com and search for 'Selenium automation'"
        },
        {
            "name": "GitHub Navigation",
            "task": "Navigate to github.com and search for 'AI automation tools'"
        },
        {
            "name": "Weather Check",
            "task": "Go to weather.com and check the current weather"
        }
    ]
    
    print("\nAvailable demos:")
    for i, demo in enumerate(demos, 1):
        print(f"{i}. {demo['name']}")
        print(f"   Task: {demo['task']}\n")
        
    try:
        choice = int(input("Select demo (1-3): "))
        if 1 <= choice <= len(demos):
            demo = demos[choice - 1]
            print(f"\nRunning: {demo['name']}")
            run_single_task(demo['task'])
        else:
            print("Invalid choice")
    except ValueError:
        print("Invalid input")


def main():
    """Main entry point with CLI argument parsing"""
    
    parser = argparse.ArgumentParser(
        description="AI-Controlled Selenium Automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                           # Interactive mode
  python main.py --demo                    # Run demo tasks
  python main.py --task "Go to google.com" # Single task
  python main.py --config                  # Show configuration
        """
    )
    
    parser.add_argument(
        '--task',
        type=str,
        help='Execute a single task'
    )
    
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Run demo tasks'
    )
    
    parser.add_argument(
        '--config',
        action='store_true',
        help='Show current configuration'
    )
    
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run in headless mode'
    )
    
    parser.add_argument(
        '--report-format',
        type=str,
        choices=['html', 'json', 'text', 'all'],
        default='html',
        help='Report format (default: html)'
    )
    
    args = parser.parse_args()
    
    # Override config with CLI args
    if args.headless:
        Config.HEADLESS = True
    
    # Handle different modes
    if args.config:
        Config.print_config()
        return
        
    if args.demo:
        run_demo_tasks()
        return
        
    if args.task:
        run_single_task(args.task)
        return
        
    # Default: interactive mode
    run_interactive_mode()


if __name__ == "__main__":
    main()
