# KernHell 2.0 ⚡

**The Zero-Cost Self-Healing QA Agent.**  
KernHell automatically fixes broken Playwright scripts using AI, monitors your logs for bugs, and generates premium reports—all running locally on your machine.

---

## 🚀 Features at a Glance

| Feature | Command | Description |
| :--- | :--- | :--- |
| **Auto-Heal** | `kernhell heal <file>` | Automatically detects errors, patches code, and verifies fixes. |
| **Watch Mode** | `kernhell watch <dir>` | Runs in background. Auto-heals tests the moment you save them. |
| **Bug Hunter** | `kernhell hunt <logs>` | Monitors server logs. AI analyzes errors & sends Slack/WhatsApp alerts. |
| **Dashboard** | `kernhell report` | Generates a beautiful HTML report of time & money saved. |
| **Semantic AI** | (Internal) | Uses Vector DB to find selectors even if IDs/Classes change completely. |

---

## 📦 Installation

### Prerequisites
- Python 3.10+
- [Add to PATH] checked during Python installation.

### 1-Click Install
```bash
git clone https://github.com/your-repo/kernhell.git
cd kernhell
pip install -e .
playwright install chromium
```

---

## 🔑 Setup (API Keys)

KernHell works with **Google Gemini (Free)**, **Groq (Free Beta)**, **OpenRouter**, and **NVIDIA**.
You need at least one key.

```bash
# Recommended: Google Gemini 2.0 Flash (Fast & Vision Capable)
kernhell config add-key "YOUR_GOOGLE_KEY" --provider google

# Fallback: Groq (Llama 3 70B)
kernhell config add-key "YOUR_GROQ_KEY" --provider groq
```

*KernHell automatically rotates keys and fails over to the next provider if one goes down.*

---

## 🛠️ User Guide

### 1. Fix a Broken Test (`heal`)
The core feature. If a test fails due to a changed selector (e.g., `#submit` -> `.btn-primary`), KernHell fixes it instantly.

```bash
# Fix a single file
kernhell heal tests/login_test.py

# Fix an entire folder recursively
kernhell heal tests/
```

### 2. Developer Mode (`watch`)
Don't run tests manually. Just save your file, and KernHell handles the rest.

```bash
kernhell watch tests/
```
*Now, whenever you save a file in `tests/`, KernHell runs it. If it fails, it patches it automatically.*

### 3. Log Monitoring (`hunt`)
Turn your terminal into a 24/7 SRE agent.

```bash
# Monitor logs and send Slack alerts
kernhell hunt ./server_logs --slack

# Monitor logs and send WhatsApp alerts
kernhell hunt ./server_logs --whatsapp
```
*Requires SLACK_BOT_TOKEN or TWILIO credentials in environment variables.*

### 4. Mission Control (`report`)
Show your boss how much time you saved.

```bash
kernhell report
```
*Opens a premium dark-mode dashboard with charts and success metrics.*

---

## 🛠️ Advanced Configuration

### Environment Variables for Alerts
To use the `hunt` command with alerts, set these variables:

**Slack:**
- `SLACK_BOT_TOKEN`: Your Bot User OAuth Token
- `SLACK_CHANNEL`: Channel ID (e.g., #alerts)

**WhatsApp (Twilio):**
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `ALERT_PHONE`: Your phone number
- `TWILIO_WHATSAPP_NUMBER`: Specific formatting necessary

---

## 🏗️ Architecture

KernHell uses a **Multi-Agent Architecture**:
- **Scanner**: Runs tests & captures screenshots.
- **Doctor**: Diagnoses the error type.
- **Healer**: The AI brain. Uses semantic search + vision to generate patches.
- **Surgeon**: AST-based code rewriting (safe & precise).

---

## License
MIT License. Open Source & Forever Free.
