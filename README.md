# KernHell

**KernHell** is a self-healing CLI tool that automatically fixes broken Playwright scripts using AI.

## 🚀 Step-by-Step Installation Guide

Follow these steps to install KernHell on any Windows machine.

### Step 1: Install Python (Must Do First!)
Before anything else, you need Python installed correctly.
1. Download Python 3.10+ from [python.org/downloads](https://www.python.org/downloads/).
2. Run the installer.
3. **IMPORTANT:** Check the box **"Add Python to PATH"** at the bottom of the first screen.
4. Click "Install Now".

### Step 2: Get the Project
Open your Command Prompt (cmd) or PowerShell and run these commands to download the code:

```bash
# Clone this repository
git clone https://github.com/YOUR_GITHUB_USERNAME/KernHell.git

# Go into the project folder
cd KernHell
```

*(Replace `YOUR_GITHUB_USERNAME` with your actual username)*

### Step 3: Run the Setup Script
We made this easy. Just run the `setup.bat` file.
You can double-click it in File Explorer, or run:
```bash
setup.bat
```
This script will:
- Install KernHell as a global command on your computer.
- Install all necessary libraries.
- Install browser binaries for Playwright.

### Step 4: Set Your AI Key (Required)
Every user needs their own Google Gemini API Key.
1. Get a free key from [aistudio.google.com](https://aistudio.google.com/).
2. Run this command in your terminal (Command Prompt):

```bash
setx GEMINI_API_KEY "paste_your_key_here"
```
*(After running this, close and reopen your terminal for it to work)*

## ✅ Verify Installation
Open a **new** terminal window and type:
```bash
kernhell --help
```
If you see the help menu, you are ready!

## 🛠️ How to Use
To fix a broken script, just run:
```bash
kernhell heal path/to/your/script.py
```
Example:
```bash
kernhell heal tests/login_test.py
```
