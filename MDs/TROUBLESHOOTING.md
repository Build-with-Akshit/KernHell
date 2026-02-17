# KernHell Troubleshooting Guide

If you encounter issues like "Command not found", "v0.1 version", or "API Errors", follow these solutions.

---

## 🛑 Problem: "No such command 'watch'" or "v0.1"
**Symptom:** You run `kernhell watch` and get an error, or the version shows `v0.1`.
**Cause:** Your terminal is using an old or cached installation of KernHell.

### ✅ Solution 1: Use the Helper Script (Recommended)
We included a "1-Click Fix" script.

1. Open PowerShell in the project folder.
2. Run this command:
   ```powershell
   .\install_update.ps1
   ```
3. Type `A` if asked to confirm execution policy.

This script will:
- Clean old installations
- Reinstall dependencies
- Force update KernHell to v2.0

### ✅ Solution 2: Manual Clean Install
If you prefer manual steps:

1. **Activate Virtual Environment:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

2. **Force Uninstall:**
   ```powershell
   pip uninstall kernhell -y
   ```

3. **Reinstall in Editable Mode (CRITICAL STEP):**
   ```powershell
   pip install -e .
   ```

4. **Verify:**
   ```powershell
   kernhell --help
   # Should list 'watch', 'heal', 'hunt'
   ```

---

## 🛑 Problem: "API Key Error / 429 Quota Exceeded"
**Symptom:** `kernhell heal` says "Quota exceeded" or "Invalid API Key".
**Cause:** Free tier limits reached or key not saved.

### ✅ Solution: Add Backup Providers
KernHell automatically switches providers if one fails. Add multiple keys:

```bash
# Primary (Google)
kernhell config add-key "AIza..." --provider google

# Backup 1 (Groq - Free)
kernhell config add-key "gsk_..." --provider groq

# Backup 2 (NVIDIA - Free Credits)
kernhell config add-key "nvapi-..." --provider nvidia
```

To verify keys are saved:
```bash
Get-Content ~/.kernhell/keys.json
```

---

## 🛑 Problem: "Playwright Browser Not Found"
**Symptom:** `Target closed` or `Executable not found`.
**Cause:** Browsers not installed or path issue.

### ✅ Solution: Reinstall Browsers
```bash
playwright install chromium
```

---

## 🛑 Problem: "Screenshot Optimization Failed"
**Symptom:** Logs show warning about PIL/Image.
**Cause:** Missing `Pillow` library.

### ✅ Solution: Install Requirements
```bash
pip install -r requirements.txt
```
