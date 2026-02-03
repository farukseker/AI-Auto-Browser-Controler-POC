# Troubleshooting Guide

## Common Issues and Solutions

### 1. Chrome/ChromeDriver Issues

#### Error: "chromedriver not found"
**Solution:**
```bash
pip install webdriver-manager
```
This automatically manages ChromeDriver versions.

#### Error: "Chrome version mismatch"
**Solution:**
Update Chrome and reinstall webdriver-manager:
```bash
# Linux
sudo apt-get update
sudo apt-get upgrade google-chrome-stable

# macOS
brew upgrade google-chrome

# Then
pip install --upgrade webdriver-manager
```

### 2. OpenRouter API Issues

#### Error: "Invalid API key"
**Check:**
- API key is set correctly in .env or code
- No extra spaces in the key
- Key has valid credits

**Verify:**
```python
import os
print(os.getenv("OPENROUTER_API_KEY"))
```

#### Error: "Rate limit exceeded"
**Solution:**
- Wait before retrying
- Upgrade OpenRouter plan
- Use a different model

### 3. Execution Failures

#### Error: "Element not found"
**Possible causes:**
1. Page not fully loaded
2. Selector is incorrect
3. Element is in iframe
4. Dynamic content loaded after page load

**Solutions:**
- Add wait steps in task description
- Enable auto_retry for AI to fix selector
- Use more specific selectors
- Check if element is in iframe

**Example fix:**
```python
# Bad task
"Click the submit button"

# Better task
"Wait 3 seconds, then click the submit button with id 'submit-btn'"
```

#### Error: "Timeout waiting for element"
**Solution:**
Increase timeout in config:
```python
Config.TIMEOUT = 20  # Increase from 10 to 20 seconds
```

### 4. AI Planning Issues

#### AI generates invalid JSON
**Check:**
- Model supports JSON output
- System prompt is clear
- Response isn't truncated

**Fix:**
```python
orchestrator = AISeleniumOrchestrator(
    openrouter_api_key="YOUR_KEY",
    model="openai/gpt-4-turbo"  # Use more capable model
)
```

#### AI misunderstands task
**Make prompt more specific:**

Bad:
```
"Login to the site"
```

Good:
```
"Go to https://example.com/login
Type 'user@example.com' in the field with id 'email'
Type 'password123' in the field with id 'password'
Click the button with text 'Sign In'"
```

### 5. Permission Issues

#### Error: "Permission denied" on screenshots
**Solution:**
```bash
mkdir -p screenshots
chmod 755 screenshots
```

#### Error: "Cannot write log file"
**Solution:**
```bash
mkdir -p logs
chmod 755 logs
```

### 6. Runtime Monitoring

#### Events not showing
**Check:**
- Listener is added before execution
- No exceptions in listener code

**Debug:**
```python
def debug_listener(event):
    print(f"DEBUG: {event.to_json()}")
    
orchestrator.monitor.add_listener(debug_listener)
```

### 7. Memory Issues

#### Browser using too much memory
**Solution:**
Run in headless mode:
```python
Config.HEADLESS = True
```

Or close browser between tasks:
```python
orchestrator.cleanup()  # After each task
```

### 8. Network Issues

#### Error: "DNS resolution failed"
**Check:**
- Internet connection
- URL is correct
- No firewall blocking

**Test:**
```bash
curl -I https://example.com
```

### 9. Import Errors

#### Error: "No module named 'selenium'"
**Solution:**
```bash
pip install -r requirements.txt
```

Or activate virtual environment:
```bash
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 10. Performance Issues

#### Execution is slow
**Optimizations:**
1. Use headless mode
2. Reduce wait times
3. Disable images/CSS:
```python
options = webdriver.ChromeOptions()
prefs = {"profile.managed_default_content_settings.images": 2}
options.add_experimental_option("prefs", prefs)
```

## Debug Mode

Enable verbose logging:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
```

## Getting Help

1. Check logs in `./logs/` directory
2. Review screenshots in `./screenshots/` directory
3. Enable debug listener:
```python
orchestrator.monitor.add_listener(lambda e: print(e.to_json()))
```

## System Requirements Check

Run this diagnostic:

```python
import sys
import selenium
import requests

print(f"Python: {sys.version}")
print(f"Selenium: {selenium.__version__}")
print(f"Requests: {requests.__version__}")

from selenium import webdriver
driver = webdriver.Chrome()
print(f"Chrome: {driver.capabilities['browserVersion']}")
driver.quit()
print("✓ All systems operational")
```

## Still Having Issues?

1. Check README.md for detailed documentation
2. Review example_usage.py for working examples
3. Ensure all dependencies are installed
4. Verify Chrome/ChromeDriver compatibility
5. Test with simple task first: "Go to google.com"
