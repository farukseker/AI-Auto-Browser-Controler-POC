"""
Selenium executor with runtime monitoring and AI control
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import datetime
import time
import os
from typing import Dict, Optional

from runtime_state import RuntimeMonitor, StepEvent


class SeleniumExecutor:
    """Execute AI-generated Selenium tasks with monitoring"""
    
    def __init__(self, monitor: RuntimeMonitor, headless: bool = False, screenshot_dir: str = "./screenshots"):
        self.monitor = monitor
        self.driver: Optional[webdriver.Chrome] = None
        self.headless = headless
        self.screenshot_dir = screenshot_dir
        self.timeout = 10
        
        # Create screenshot directory
        os.makedirs(screenshot_dir, exist_ok=True)
        
    def start_browser(self):
        """Initialize browser"""
        options = webdriver.ChromeOptions()
        
        if self.headless:
            options.add_argument("--headless")
            
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        
        self.driver = webdriver.Chrome(options=options)
        
    def stop_browser(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            
    def execute_plan(self, plan: Dict) -> bool:
        """
        Execute complete task plan with monitoring
        Returns True if all steps succeeded
        """
        
        if not self.driver:
            self.start_browser()
            
        steps = plan.get("steps", [])
        
        for i, step in enumerate(steps):
            success = self._execute_step(i, step)
            
            if not success:
                # Take error screenshot
                screenshot_path = self._save_screenshot(f"error_step_{i}")
                
                self.monitor.emit(StepEvent(
                    step_index=i,
                    action=step.get("action", "unknown"),
                    status="failed",
                    timestamp=datetime.now().isoformat(),
                    selector=step.get("selector"),
                    url=self.driver.current_url if self.driver else None,
                    error="Step execution failed",
                    screenshot_path=screenshot_path
                ))
                
                return False
                
        return True
        
    def _execute_step(self, step_index: int, step: Dict) -> bool:
        """Execute single step with monitoring"""
        
        action = step.get("action")
        
        # Emit started event
        self.monitor.emit(StepEvent(
            step_index=step_index,
            action=action,
            status="started",
            timestamp=datetime.now().isoformat(),
            selector=step.get("selector"),
            url=self.driver.current_url if self.driver else None,
            value=step.get("value")
        ))
        
        try:
            # Execute action
            if action == "open":
                self._action_open(step["url"])
                
            elif action == "type":
                self._action_type(step["selector"], step["value"])
                
            elif action == "click":
                self._action_click(step["selector"])
                
            elif action == "wait":
                self._action_wait(step["seconds"])
                
            elif action == "screenshot":
                screenshot_path = self._save_screenshot(f"step_{step_index}")
                step["screenshot_path"] = screenshot_path
                
            else:
                raise ValueError(f"Unknown action: {action}")
                
            # Emit success event
            self.monitor.emit(StepEvent(
                step_index=step_index,
                action=action,
                status="success",
                timestamp=datetime.now().isoformat(),
                selector=step.get("selector"),
                url=self.driver.current_url,
                screenshot_path=step.get("screenshot_path")
            ))
            
            return True
            
        except Exception as e:
            # Emit failure event
            screenshot_path = self._save_screenshot(f"error_step_{step_index}")
            
            self.monitor.emit(StepEvent(
                step_index=step_index,
                action=action,
                status="failed",
                timestamp=datetime.now().isoformat(),
                selector=step.get("selector"),
                url=self.driver.current_url if self.driver else None,
                error=str(e),
                screenshot_path=screenshot_path
            ))
            
            return False
            
    def _action_open(self, url: str):
        """Navigate to URL"""
        self.driver.get(url)
        time.sleep(1)  # Brief pause for page load start
        
    def _action_type(self, selector: str, value: str):
        """Type text into element"""
        element = WebDriverWait(self.driver, self.timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )
        element.clear()
        element.send_keys(value)
        
    def _action_click(self, selector: str):
        """Click element"""
        element = WebDriverWait(self.driver, self.timeout).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
        )
        element.click()
        
    def _action_wait(self, seconds: int):
        """Wait for specified seconds"""
        time.sleep(seconds)
        
    def _save_screenshot(self, name: str) -> str:
        """Save screenshot and return path"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        filepath = os.path.join(self.screenshot_dir, filename)
        
        if self.driver:
            self.driver.save_screenshot(filepath)
            
        return filepath
        
    def get_page_source(self) -> str:
        """Get current page HTML"""
        if self.driver:
            return self.driver.page_source
        return ""
        
    def get_current_url(self) -> str:
        """Get current URL"""
        if self.driver:
            return self.driver.current_url
        return ""
