# 🪟 Install KernHell on Windows

Follow these steps to set up KernHell 2.0 on Windows 10/11.

---

## 🏗️ Step 1: Install Python

1. Download Python 3.10 or newer from [python.org](https://www.python.org/downloads/).
2. Run the installer.
3. **CRITICAL:** Check the box **"Add Python to PATH"** at the bottom of the first screen.
4. Click "Install Now".

---

## ⚡ Step 2: Automated Install (Recommended)

We have a 1-click script that handles virtual environments and updates.

1. Open PowerShell in the `KernHell` folder.
   *(Shift + Right Click in folder -> "Open PowerShell window here")*
2. Run the update script:
   ```powershell
   .\install_update.ps1
   ```
3. If successful, it will show the version and you are ready!

---

## 🛠️ Step 3: Manual Install (Advanced)

If you prefer doing it manually:

1. **Create a Virtual Environment:**
   ```powershell
   python -m venv venv
   ```

2. **Activate it:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
   *(If you get a permission error, run `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`)*

3. **Install KernHell:**
   ```powershell
   pip install -e .
   ```

4. **Install Browsers:**
   ```powershell
   playwright install chromium
   ```

---

## 🔑 Step 4: Add API Keys

You need at least one AI provider key.

```powershell
# Google Gemini (Recommended)
kernhell config add-key "YOUR_KEY" --provider google
```

## ✅ Verify

Run:
```powershell
kernhell doctor
```
