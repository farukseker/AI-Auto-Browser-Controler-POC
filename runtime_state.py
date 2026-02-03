"""
Runtime state management and event system for AI-controlled Selenium
"""
from dataclasses import dataclass, asdict
from typing import Optional, List, Callable
from datetime import datetime
import json


@dataclass
class StepEvent:
    """Single step execution event"""
    step_index: int
    action: str
    status: str  # started, success, failed
    timestamp: str
    selector: Optional[str] = None
    url: Optional[str] = None
    value: Optional[str] = None
    error: Optional[str] = None
    screenshot_path: Optional[str] = None
    
    def to_dict(self):
        return asdict(self)
    
    def to_json(self):
        return json.dumps(self.to_dict(), indent=2)


class RuntimeMonitor:
    """Monitors and tracks execution in real-time"""
    
    def __init__(self):
        self.events: List[StepEvent] = []
        self.listeners: List[Callable] = []
        self.current_step: Optional[int] = None
        
    def add_listener(self, callback: Callable):
        """Add a callback function to be called on each event"""
        self.listeners.append(callback)
        
    def emit(self, event: StepEvent):
        """Emit an event to all listeners"""
        self.events.append(event)
        self.current_step = event.step_index
        
        # Call all listeners
        for listener in self.listeners:
            try:
                listener(event)
            except Exception as e:
                print(f"Listener error: {e}")
                
    def get_current_status(self):
        """Get current execution status"""
        if not self.events:
            return {"status": "not_started", "total_steps": 0}
            
        total_steps = max(e.step_index for e in self.events) + 1
        completed = len([e for e in self.events if e.status == "success"])
        failed = len([e for e in self.events if e.status == "failed"])
        
        return {
            "status": "running" if self.current_step is not None else "stopped",
            "total_steps": total_steps,
            "completed": completed,
            "failed": failed,
            "current_step": self.current_step
        }
        
    def get_log(self):
        """Get full execution log"""
        return [e.to_dict() for e in self.events]


# Default console listener
def console_listener(event: StepEvent):
    """Print events to console with color coding"""
    status_symbol = {
        "started": "⏳",
        "success": "✓",
        "failed": "✗"
    }
    
    symbol = status_symbol.get(event.status, "•")
    timestamp = event.timestamp.split("T")[1].split(".")[0]
    
    msg = f"[{timestamp}] {symbol} Step {event.step_index}: {event.action}"
    
    if event.selector:
        msg += f" ({event.selector})"
    
    if event.status == "failed" and event.error:
        msg += f"\n  Error: {event.error}"
        
    print(msg)
