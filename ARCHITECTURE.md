# 🏗️ KernHell Architecture & File Structure

## 📁 COMPLETE PROJECT STRUCTURE

```
KernHell/
│
├── kernhell/                      # Main package
│   ├── __init__.py
│   ├── main.py                    # CLI entry point (Typer commands)
│   ├── config.py                  # ConfigManager + API key management
│   ├── healer.py                  # Core self-healing logic
│   ├── scanner.py                 # Playwright error detection + screenshots
│   ├── patcher.py                 # Code modification (comment + add)
│   ├── providers.py               # Multi-AI provider integration
│   ├── analyzer.py                # Project structure analysis
│   ├── generator.py               # Test generation from project map
│   ├── utils.py                   # CacheManager, logging, UI helpers
│   │
│   ├── semantic_db.py            # [NEW] ChromaDB for semantic selectors
│   ├── bug_hunter.py             # [NEW] Log monitoring + auto-fix
│   └── report_generator.py       # [NEW] Enhanced HTML/PDF reports
│
├── .kernhell_cache/              # Temporary storage
│   ├── project_maps/             # Analyzer output
│   ├── screenshots/              # Failure screenshots
│   └── chromadb/                 # Vector embeddings
│
├── project/                      # Example test files
│   └── test_fail.py
│
├── tests/                        # Generated tests output
│
├── setup.py                      # Package installation
├── requirements.txt              # Dependencies
├── README.md                     # Documentation
├── .gitignore
└── kernhell_report.html          # Generated report

```

## 🔄 DATA FLOW ARCHITECTURE

### 1. **Healing Workflow**

```
┌─────────────┐
│ User Input  │  kernhell heal test.py
└──────┬──────┘
       │
       v
┌──────────────────┐
│   Scanner.py     │  Run test with Playwright
│                  │  ├─ Execute test
│                  │  ├─ Detect error
│                  │  └─ Capture screenshot
└──────┬───────────┘
       │
       v
┌──────────────────┐
│   Healer.py      │  Analyze & Generate Fix
│                  │  ├─ Smart Router (choose provider)
│                  │  ├─ Send error + code + screenshot to AI
│                  │  ├─ Check healing memory (past fixes)
│                  │  └─ Get fixed code
└──────┬───────────┘
       │
       v
┌──────────────────┐
│   Patcher.py     │  Apply Fix
│                  │  ├─ Backup original (optional)
│                  │  ├─ Comment out broken line
│                  │  └─ Insert fixed code below
└──────┬───────────┘
       │
       v
┌──────────────────┐
│ Verification     │  Re-run test
│                  │  ├─ Test passes? ✅ Done!
│                  │  └─ Test fails? 🔄 Retry (max 3x)
└──────────────────┘
```

### 2. **Multi-Provider Fallback**

```
┌──────────────┐
│ AI Request   │
└──────┬───────┘
       │
       v
┌──────────────────────┐
│  Smart Router        │  Select best provider
│  (healer.py)         │  ├─ Vision task? → nvidia/google
│                      │  └─ Text only? → groq/cloudflare
└──────┬───────────────┘
       │
       v
┌──────────────────────┐
│ Providers.py         │  Try selected provider
│                      │  ├─ Check quota (QuotaTracker)
│                      │  ├─ Make API call
│                      │  └─ Success? Return
└──────┬───────────────┘
       │ Error?
       v
┌──────────────────────┐
│ Fallback Chain       │  Try alternatives
│                      │  google → groq → nvidia → openrouter → cloudflare
│                      │  Until success or all exhausted
└──────────────────────┘
```

### 3. **Test Generation Workflow**

```
┌──────────────┐
│ User Input   │  kernhell generate ./app --out tests/
└──────┬───────┘
       │
       v
┌──────────────────┐
│  Analyzer.py     │  Scan project
│                  │  ├─ Detect framework (React/Next/Node)
│                  │  ├─ Find routes/pages
│                  │  ├─ Identify components
│                  │  └─ Create source map (JSON)
└──────┬───────────┘
       │
       v
┌──────────────────┐
│  CacheManager    │  Store map
│                  │  └─ .kernhell_cache/project_maps/app_map.json
└──────┬───────────┘
       │
       v
┌──────────────────┐
│  Generator.py    │  Generate tests
│                  │  ├─ Read source map
│                  │  ├─ For each route/page:
│                  │  │   └─ Ask AI to write Playwright test
│                  │  └─ Save to output dir
└──────┬───────────┘
       │
       v
┌──────────────────┐
│  Tests Created   │  tests/test_login.py
│                  │  tests/test_signup.py
│                  │  tests/test_checkout.py
└──────────────────┘
```

### 4. **Semantic Selector Matching** (NEW)

```
┌──────────────────┐
│ During Test Run  │  page.click("#old-button")
│                  │  ❌ Element not found!
└──────┬───────────┘
       │
       v
┌──────────────────┐
│ Semantic DB      │  Query by meaning
│ (semantic_db.py) │  find_similar("button to submit")
│                  │  └─ Vector search in ChromaDB
└──────┬───────────┘
       │
       v
┌──────────────────┐
│ Alternative      │  Return candidates:
│ Selectors        │  ["#submit-btn", ".purchase-button", "[data-action='buy']"]
└──────┬───────────┘
       │
       v
┌──────────────────┐
│ Healer.py        │  Try each alternative
│                  │  ├─ #submit-btn → Works! ✅
│                  │  └─ Update test with new selector
└──────────────────┘
```

### 5. **Bug Hunter Flow** (NEW)

```
┌──────────────────┐
│ kernhell hunt    │  Monitor ./logs/
│ ./logs/          │
└──────┬───────────┘
       │
       v
┌──────────────────────┐
│ File Watcher         │  Detect log file changes
│ (watchdog library)   │  ├─ server.log modified
│                      │  └─ Read new lines
└──────┬───────────────┘
       │
       v
┌──────────────────────┐
│ Pattern Matching     │  Scan for errors
│                      │  ├─ "ERROR: Out of memory"
│                      │  ├─ "EXCEPTION: Database timeout"
│                      │  └─ "CRASH: Segmentation fault"
└──────┬───────────────┘
       │ Match found!
       v
┌──────────────────────┐
│ AI Analysis          │  Understand error
│ (bug_hunter.py)      │  ├─ Extract context (5 lines before/after)
│                      │  ├─ Send to AI: "What caused this?"
│                      │  └─ AI suggests fix
└──────┬───────────────┘
       │
       v
┌──────────────────────┐
│ Auto-Fix             │  Apply fix if confident
│                      │  ├─ Confidence > 80%? → Apply
│                      │  └─ Else → Just alert
└──────┬───────────────┘
       │
       v
┌──────────────────────┐
│ Alert Developer      │  Send notifications
│                      │  ├─ Slack: "#alerts channel"
│                      │  ├─ WhatsApp: via Twilio
│                      │  └─ Email: via SendGrid
└──────────────────────┘
```

## 🧩 MODULE DEPENDENCIES

```
main.py (CLI)
  ├─ uses → config.py (ConfigManager)
  ├─ uses → healer.py (get_ai_fix)
  ├─ uses → scanner.py (run_test_capture_errors)
  ├─ uses → patcher.py (apply_fix)
  ├─ uses → analyzer.py (analyze_project)
  ├─ uses → generator.py (TestGenerator)
  └─ uses → utils.py (CacheManager, print_banner)

healer.py
  ├─ uses → config.py (get API keys)
  ├─ uses → providers.py (AI functions)
  ├─ uses → semantic_db.py [NEW] (find_similar)
  └─ uses → utils.py (logging)

scanner.py
  ├─ uses → playwright (browser automation)
  └─ uses → utils.py (CacheManager for screenshots)

analyzer.py
  ├─ reads → project files (detect framework)
  └─ uses → utils.py (CacheManager for maps)

generator.py
  ├─ uses → config.py (AI providers)
  ├─ uses → providers.py (generic_call)
  └─ reads → project_map.json

bug_hunter.py [NEW]
  ├─ uses → watchdog (file monitoring)
  ├─ uses → healer.py (AI analysis)
  └─ uses → twilio/slack_sdk (alerts)
```

## 🔑 KEY CLASSES & FUNCTIONS

### config.py
```python
class ConfigManager:
    - get_keys(provider: str) → List[str]
    - add_key(provider: str, key: str)
    - remove_key(key: str)
    - get_key_count() → int
    - select_provider() → str

class QuotaTracker [NEW]:
    - can_use(provider: str) → bool
    - record_usage(provider: str)
    - reset_daily()
```

### healer.py
```python
def get_ai_fix(code: str, error: str, screenshot: Optional[str]) → str:
    """Get fixed code from AI"""

class HealingMemory [NEW]:
    - remember(error, fix, success)
    - recall_similar(error) → Optional[str]
```

### scanner.py
```python
def run_test_capture_errors(file_path: str) → dict:
    """Run test, return errors + screenshot"""

def optimize_screenshot(image_path: Path) → str [NEW]:
    """Compress & resize screenshot"""
```

### patcher.py
```python
def apply_fix(file_path: str, old_code: str, new_code: str):
    """Comment old, insert new"""
```

### providers.py
```python
def google_generate_fix(...) → str
def groq_generate_fix(...) → str
def nvidia_generate_fix(...) → str
def openrouter_generate_fix(...) → str
def cloudflare_generate_fix(...) → str
def generic_call(prompt: str, provider: str) → str
```

### semantic_db.py [NEW]
```python
class SemanticSelector:
    - store_element(selector: str, context: dict)
    - find_similar(query: str) → List[str]
```

### bug_hunter.py [NEW]
```python
class LogMonitor:
    - on_modified(event)
    - handle_error(log_line: str)

def send_slack_alert(message: str)
def send_whatsapp_alert(message: str)
```

## 🎨 UI/UX Flow

### Terminal Output Examples

#### 1. Healing in Action
```
$ kernhell heal tests/test_login.py

🔥 KernHell v1.0.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 Analyzing: tests/test_login.py
⚡ Running test... FAILED
📸 Screenshot captured
🤖 Asking AI for fix...
   ├─ Provider: google/gemini-2.0-flash-exp (vision)
   └─ Processing...

✅ Fix Generated!
   Error: TimeoutError: Timeout 30000ms exceeded
   Fix: Changed selector from #login to button[data-testid="login-btn"]

📝 Applying patch...
   ├─ Original line commented
   └─ Fixed code inserted

🔄 Verifying fix...
   ├─ Running test again...
   └─ ✅ PASSED!

💾 Saved to healing history
⏱️  Total time: 12.3s
```

#### 2. Bug Hunter Alert
```
$ kernhell hunt ./logs --patterns error,crash

🔍 Bug Hunter Started
👀 Watching: ./logs/

[12:34:56] 🚨 ERROR DETECTED!
File: server.log
Error: Out of memory (heap size exceeded)

🤖 AI Analysis:
   Cause: Memory leak in /api/upload endpoint
   Suggested Fix: Add stream processing for large files

🔧 Auto-fix applied: routes/upload.js
   ├─ Changed: fs.readFile() → fs.createReadStream()
   └─ Added: buffer size limit

📲 Alerts sent:
   ✅ Slack: #dev-alerts
   ✅ WhatsApp: +91-XXXXXXXXXX
```

#### 3. Watch Mode
```
$ kernhell watch ./app/tests

👀 Watch Mode Active
Monitoring: ./app/tests

[12:45:00] 📝 Change detected: test_cart.py
[12:45:02] 🔄 Auto-healing...
[12:45:08] ✅ Fixed!

[12:46:15] 📝 Change detected: test_payment.py
[12:46:17] 🔄 Auto-healing...
[12:46:22] ✅ Fixed!

Press Ctrl+C to stop...
```

## 📊 CONFIG FILE STRUCTURE

### .kernhell_config.json
```json
{
  "providers": {
    "google": {
      "keys": ["AIzaSyXXXXXXXXX", "AIzaSyYYYYYYYYY"],
      "current_key_index": 0,
      "quota_used_today": 23,
      "quota_limit": 50
    },
    "groq": {
      "keys": ["gsk_XXXXXXXXXX"],
      "current_key_index": 0,
      "quota_used_today": 145,
      "quota_limit": 14400
    }
  },
  "preferences": {
    "default_provider": "google",
    "fallback_chain": ["google", "groq", "nvidia", "openrouter"],
    "auto_retry": true,
    "max_retries": 3
  },
  "healing_history": [
    {
      "timestamp": "2026-02-15T10:30:00",
      "file": "test_login.py",
      "error_hash": "a3f2e1c9...",
      "fix_applied": true,
      "provider_used": "google"
    }
  ]
}
```

## 🎯 TESTING CHECKLIST

### Unit Tests
- [ ] config.py → Add/remove keys
- [ ] healer.py → AI response parsing
- [ ] patcher.py → Code modification
- [ ] scanner.py → Error detection

### Integration Tests
- [ ] Full healing workflow on sample project
- [ ] Multi-provider fallback
- [ ] Semantic selector matching

### E2E Tests
- [ ] Test on SIH project
- [ ] Generate tests from scratch
- [ ] Bug Hunter on real logs

---

This architecture is **modular**, **extensible**, and **production-ready**!
Each component can be developed/tested independently, then integrated smoothly.
