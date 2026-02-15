# KernHell

**KernHell** is a self-healing CLI tool that automatically fixes broken Playwright scripts using AI.

## 🚀 Installation

Choose your operating system:

### 🪟 Windows (Double-Click Setup)
1. **Download:** Clone repo or copy folder.
2. **Install Python:** Ensure Python 3.10+ is installed and "Add to PATH" is checked.
3. **Run Setup:** Double-click `setup.bat`.
4. **Set API Key:**
   ```cmd
   setx GEMINI_API_KEY "your_key_here"
   ```
   *(Restart terminal after setting key)*

### 🐧 Linux / macOS (Shell Script)
1. **Download:** Clone repo or copy folder.
2. **Make Executable:**
   ```bash
   chmod +x setup.sh
   ```
3. **Run Setup:**
   ```bash
   ./setup.sh
   ```
   *(If permission denied, run: `sudo ./setup.sh`)*
   
4. **Set API Key:**
   Add this to your `~/.bashrc` or `~/.zshrc`:
   ```bash
   export GEMINI_API_KEY="your_key_here"
   ```
   Then run: `source ~/.bashrc`

---

## 🛠️ Usage
After installation, the `kernhell` command will be available globally.

### Fix a Script
```bash
kernhell heal path/to/your/script.py
```

### Verify Installation & Models
```bash
kernhell --help
python3 check_models.py
```

---

## ⚠️ Troubleshooting
- **"kernhell: command not found" (Linux)**: Ensure `~/.local/bin` is in your PATH. Adding `export PATH=$PATH:~/.local/bin` to your shell config usually fixes this.
- **"Externally Managed Environment" (Linux)**: The `setup.sh` script attempts to handle this automatically, but if it fails, try installing with `pip install . --break-system-packages`.
