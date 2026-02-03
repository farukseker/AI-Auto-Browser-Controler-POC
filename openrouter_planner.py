"""
OpenRouter integration for AI-driven Selenium task planning
"""
import requests
import json
from typing import Dict, List, Optional


class OpenRouterPlanner:
    """AI task planner using OpenRouter"""
    
    def __init__(self, api_key: str, model: str = "openai/gpt-4-turbo"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        
    def get_task_plan(self, user_prompt: str) -> Dict:
        """
        Convert user prompt to structured Selenium task plan
        
        Returns JSON format:
        {
            "steps": [
                {"action": "open", "url": "..."},
                {"action": "type", "selector": "...", "value": "..."},
                {"action": "click", "selector": "..."},
                {"action": "wait", "seconds": 3}
            ]
        }
        """
        
        system_prompt = """You are a browser automation planner.
Your job is to convert user instructions into structured Selenium commands.

RULES:
1. Return ONLY valid JSON
2. No explanations or markdown
3. Use only these actions: open, type, click, wait, screenshot
4. Selectors must be CSS selectors
5. Be specific and safe

Example output:
{
  "steps": [
    {"action": "open", "url": "https://example.com"},
    {"action": "type", "selector": "#username", "value": "user123"},
    {"action": "click", "selector": "button[type='submit']"},
    {"action": "wait", "seconds": 2}
  ]
}"""

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 2000
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                data=json.dumps(payload),
                timeout=30
            )
            
            response.raise_for_status()
            
            content = response.json()["choices"][0]["message"]["content"]
            
            # Clean up markdown if present
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            plan = json.loads(content)
            
            # Validate plan structure
            if "steps" not in plan:
                raise ValueError("Plan must contain 'steps' key")
                
            # Validate each step
            for step in plan["steps"]:
                if "action" not in step:
                    raise ValueError("Each step must have 'action' key")
                    
                action = step["action"]
                if action not in ["open", "type", "click", "wait", "screenshot"]:
                    raise ValueError(f"Invalid action: {action}")
                    
                # Validate required fields per action
                if action == "open" and "url" not in step:
                    raise ValueError("'open' action requires 'url'")
                if action == "type" and ("selector" not in step or "value" not in step):
                    raise ValueError("'type' action requires 'selector' and 'value'")
                if action == "click" and "selector" not in step:
                    raise ValueError("'click' action requires 'selector'")
                if action == "wait" and "seconds" not in step:
                    raise ValueError("'wait' action requires 'seconds'")
                    
            return plan
            
        except requests.RequestException as e:
            raise Exception(f"OpenRouter API error: {str(e)}")
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON from AI: {str(e)}")
        except Exception as e:
            raise Exception(f"Planning error: {str(e)}")
            
    def refine_plan_with_error(self, original_plan: Dict, error_step: int, error_msg: str, dom_snippet: Optional[str] = None) -> Dict:
        """
        AI attempts to fix failed step by generating alternative selector or approach
        """
        
        context = f"""Original plan failed at step {error_step}.
Error: {error_msg}

Original step: {json.dumps(original_plan['steps'][error_step])}

{f"DOM context: {dom_snippet[:500]}" if dom_snippet else ""}

Suggest an alternative approach or selector. Return complete plan with the fix."""

        return self.get_task_plan(context)
