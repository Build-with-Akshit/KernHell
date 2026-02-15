# KernHell

**KernHell** is a self-healing CLI tool that automatically fixes broken Playwright scripts using AI.

## 🚀 Installation

Choose your operating system:

### 🪟 Windows (Double-Click Setup)
1. **Download:** Clone repo or copy folder.
2. **Install Python:** Ensure Python 3.10+ is installed and "Add to PATH" is checked.
### 🔑 Setup (One-Time)
KernHell supports multiple AI providers. You need at least one API Key.
Run any of the following commands:

```bash
# 1. Google Gemini (Best Vision - Free Tier Available)
kernhell config add-key <YOUR_GEMINI_KEY> --provider google

# 2. Groq (Fastest Llama 70B - Free Beta)
kernhell config add-key <YOUR_GROQ_KEY> --provider groq

# 3. NVIDIA NIM (Llama 90B Vision - Free Credits)
kernhell config add-key <YOUR_NVIDIA_KEY> --provider nvidia
```

*Tip: You can add multiple keys. KernHell will auto-rotate and smart-select the best one.*

---

## 🛠️ Usage
After installation, the `kernhell` command will be available globally.

### Fix a Script
```bash
kernhell heal path/to/your/script.py
```

### Verify Installation & Models
```bash
## 📚 Command Reference

### Core Commands
| Command | Description |
|---------|-------------|
| `kernhell heal <target>` | **Main Command.** Fixes a file or recursively scans a directory. |
| `kernhell doctor` | **System Check.** Verifies Python, Playwright, and API Keys. |
| `kernhell report` | **Dashboard.** Generates an HTML report of time/money saved. |
| `kernhell version` | Shows installed version. |

### Configuration (API Keys)
| Command | Description |
|---------|-------------|
| `kernhell config add-key <key>` | Add an API Key. Use `--provider <name>` to specify (google, groq, nvidia). |
| `kernhell config list-keys` | View all added keys (masked). |
| `kernhell config remove-key <key>` | Remove a specific key. |
| `kernhell config prune` | **Auto-Cleanup.** Tests all keys and removes dead/invalid ones. |

---

## ⚠️ Troubleshooting
- **"kernhell: command not found" (Linux)**: Ensure `~/.local/bin` is in your PATH. Adding `export PATH=$PATH:~/.local/bin` to your shell config usually fixes this.
- **"Externally Managed Environment" (Linux)**: The `setup.sh` script attempts to handle this automatically, but if it fails, try installing with `pip install . --break-system-packages`.




## 📂 Project Structure

```
kernhell/
├── core/                  # "The Brain" (CLI, Logic, Config)
│   ├── main.py            # Entry Point
│   ├── database.py        # Stats
│   └── config.py          # AI Configuration
├── strategies/            # "The Hands" (Framework Logic)
│   ├── web/               # React / MERN Support
│   ├── python/            # Python Automation Support
│   └── mobile/            # (Future) Flutter / React Native
└── utils/                 # Shared Utilities
```

## 🛠️ Setup Guides

- [Windows Setup](setup/windows/README.md)
- [Linux Setup](setup/linux/README.md)
- [macOS Setup](setup/macos/README.md)
