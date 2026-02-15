
# KernHell Setup Guide for Windows

## Prerequisites
1.  **Python 3.10+**: [Download Here](https://www.python.org/downloads/)
    *   Ensure "Add Python to PATH" is checked during installation.
2.  **Node.js (Optional)**: For React/Web projects. [Download Here](https://nodejs.org/)
3.  **Git**: [Download Here](https://git-scm.com/)

## Installation

1.  **Clone the Repository**
    ```powershell
    git clone https://github.com/yourusername/kernhell.git
    cd kernhell
    ```

2.  **Create a Virtual Environment**
    ```powershell
    python -m venv venv
    .\venv\Scripts\Activate
    ```

3.  **Install KernHell**
    ```powershell
    pip install .
    ```

4.  **Install Playwright Browsers**
    ```powershell
    playwright install chromium
    ```

## Verification
Run the doctor command to check your setup:
```powershell
kernhell doctor
```
