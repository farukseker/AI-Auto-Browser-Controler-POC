"""
Main orchestrator - combines AI planning with Selenium execution
"""
from typing import Optional
import json
import os
from datetime import datetime

from runtime_state import RuntimeMonitor, console_listener
from openrouter_planner import OpenRouterPlanner
from selenium_executor import SeleniumExecutor
from reporter import ExecutionReporter


class AISeleniumOrchestrator:
    """
    Main controller that coordinates:
    - AI task planning
    - Selenium execution
    - Runtime monitoring
    - Self-healing on failures
    """
    
    def __init__(
        self, 
        openrouter_api_key: str,
        model: str = "openai/gpt-4-turbo",
        headless: bool = False,
        auto_retry: bool = True,
        max_retries: int = 2
    ):
        # Initialize components
        self.monitor = RuntimeMonitor()
        self.monitor.add_listener(console_listener)
        
        self.planner = OpenRouterPlanner(openrouter_api_key, model)
        self.executor = SeleniumExecutor(self.monitor, headless=headless)
        
        self.auto_retry = auto_retry
        self.max_retries = max_retries
        
    def execute_task(self, user_prompt: str) -> bool:
        """
        Main execution flow:
        1. AI generates task plan
        2. Execute with Selenium
        3. Monitor runtime
        4. Auto-retry on failure (optional)
        """
        
        print("\n" + "="*60)
        print("AI SELENIUM AUTOMATION - STARTING")
        print("="*60)
        print(f"\nTask: {user_prompt}\n")
        
        # Step 1: Get AI plan
        print("Step 1: AI Planning...")
        try:
            plan = self.planner.get_task_plan(user_prompt)
            print(f"Generated plan with {len(plan['steps'])} steps\n")
            self._print_plan(plan)
        except Exception as e:
            print(f"Planning failed: {e}")
            return False
            
        # Step 2: Execute plan
        print("\nStep 2: Executing plan...\n")
        
        retry_count = 0
        while retry_count <= self.max_retries:
            success = self.executor.execute_plan(plan)
            
            if success:
                print("\n" + "="*60)
                print("TASK COMPLETED SUCCESSFULLY")
                print("="*60)
                self._print_summary()
                return True
                
            # Failure handling
            if not self.auto_retry or retry_count >= self.max_retries:
                print("\n" + "="*60)
                print("TASK FAILED")
                print("="*60)
                self._print_summary()
                return False
                
            # Try AI-powered recovery
            print(f"\nRetry {retry_count + 1}/{self.max_retries}: Attempting AI recovery...")
            
            try:
                # Get failed step info
                failed_events = [e for e in self.monitor.events if e.status == "failed"]
                if failed_events:
                    last_failure = failed_events[-1]
                    
                    # Get page context
                    dom_snippet = self.executor.get_page_source()[:1000] if self.executor.driver else None
                    
                    # Ask AI to fix
                    plan = self.planner.refine_plan_with_error(
                        plan,
                        last_failure.step_index,
                        last_failure.error or "Unknown error",
                        dom_snippet
                    )
                    
                    print("AI suggested alternative plan\n")
                    
            except Exception as e:
                print(f"Recovery planning failed: {e}")
                return False
                
            retry_count += 1
            
        return False
        
    def _print_plan(self, plan: dict):
        """Pretty print the execution plan"""
        print("Plan Details:")
        print("-" * 60)
        for i, step in enumerate(plan["steps"]):
            action = step.get("action", "unknown")
            details = []
            
            if "url" in step:
                details.append(f"url={step['url']}")
            if "selector" in step:
                details.append(f"selector={step['selector']}")
            if "value" in step:
                details.append(f"value={step['value'][:20]}...")
            if "seconds" in step:
                details.append(f"seconds={step['seconds']}")
                
            detail_str = ", ".join(details) if details else ""
            print(f"  {i}. {action.upper():<12} {detail_str}")
        print("-" * 60)
        
    def _print_summary(self):
        """Print execution summary"""
        status = self.monitor.get_current_status()
        
        print("\nExecution Summary:")
        print("-" * 60)
        print(f"Total Steps:     {status['total_steps']}")
        print(f"Completed:       {status['completed']}")
        print(f"Failed:          {status['failed']}")
        print(f"Success Rate:    {status['completed']/status['total_steps']*100:.1f}%")
        print("-" * 60)
        
    def get_execution_log(self) -> list:
        """Get full execution log"""
        return self.monitor.get_log()
        
    def save_log(self, filepath: str):
        """Save execution log to file"""
        log = self.get_execution_log()
        with open(filepath, 'w') as f:
            json.dump(log, f, indent=2)
        print(f"\nLog saved to: {filepath}")
    
    def generate_report(self, format: str = 'html', output_dir: str = './reports') -> str:
        """
        Generate execution report
        
        Args:
            format: Report format ('html', 'json', 'text')
            output_dir: Directory to save report
            
        Returns:
            Path to generated report file
        """
        
        os.makedirs(output_dir, exist_ok=True)
        
        reporter = ExecutionReporter(self.get_execution_log())
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == 'html':
            filepath = os.path.join(output_dir, f'report_{timestamp}.html')
            return reporter.generate_html_report(filepath)
        elif format == 'json':
            filepath = os.path.join(output_dir, f'report_{timestamp}.json')
            return reporter.generate_json_report(filepath)
        elif format == 'text':
            filepath = os.path.join(output_dir, f'report_{timestamp}.txt')
            return reporter.generate_text_report(filepath)
        else:
            raise ValueError(f"Unsupported format: {format}. Use 'html', 'json', or 'text'")
    
    def get_summary(self) -> dict:
        """Get execution summary"""
        reporter = ExecutionReporter(self.get_execution_log())
        return reporter.generate_summary()
        
    def cleanup(self):
        """Cleanup resources"""
        self.executor.stop_browser()
