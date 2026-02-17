# 🐧 Install KernHell on Linux

Follow these steps for Ubuntu/Debian/Fedora.

---

## 🏗️ Step 1: Install Prerequisites

You need Python 3.10+ and `venv` support.

### Ubuntu / Debian:
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv git
```

### Fedora:
```bash
sudo dnf install python3 python3-pip git
```

---

## ⚡ Step 2: Install KernHell

1. **Clone the Repo:**
   ```bash
   git clone https://github.com/your-repo/kernhell.git
   cd kernhell
   ```

2. **Create Virtual Environment (Recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Package:**
   ```bash
   pip install -e .
   ```

4. **Install Browsers:**
   ```bash
   playwright install chromium
   playwright install-deps
   ```

---

## 🔑 Step 3: Add API Keys

```bash
# Google Gemini (Best Vision)
kernhell config add-key "YOUR_KEY" --provider google
```

---

## ⚠️ Troubleshooting

**"kernhell: command not found"**

If you installed WITHOUT a virtual environment (using `--user`), the binary is in `~/.local/bin`. Ensure this is in your PATH.

Add to `~/.bashrc` or `~/.zshrc`:
```bash
export PATH=$PATH:~/.local/bin
```
Then run `source ~/.bashrc`.
