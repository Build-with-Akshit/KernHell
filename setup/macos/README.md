# 🍎 Install KernHell on macOS

Follow these steps for any macOS version (Intel or Apple Silicon).

---

## 🏗️ Step 1: Install Python

We recommend using Homebrew.

1. **Install Homebrew** (if you don't have it):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install Python 3:**
   ```bash
   brew install python
   ```

---

## ⚡ Step 2: Install KernHell

1. **Clone the Repo:**
   ```bash
   git clone https://github.com/your-repo/kernhell.git
   cd kernhell
   ```

2. **Create Virtual Environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Package:**
   ```bash
   pip install --upgrade pip
   pip install -e .
   ```

4. **Install Browsers:**
   ```bash
   playwright install chromium
   ```

---

## 🔑 Step 3: Add API Keys

```bash
# Google Gemini (Best Vision)
kernhell config add-key "YOUR_KEY" --provider google
```

---

## ⚠️ Troubleshooting

**"Externally Managed Environment"**

If you try to install globally without `venv`, macOS will block it. Always use a virtual environment (`venv`).

**"Playwright: OpenSSL Error"**

If you see SSL errors, install certificates:
```bash
/Applications/Python\ 3.10/Install\ Certificates.command
```
