
# KernHell Setup Guide for macOS

## Prerequisites
1.  **Homebrew** (Recommended):
    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    ```
2.  **Python 3.10+**:
    ```bash
    brew install python
    ```

## Installation

1.  **Clone Repo**
    ```bash
    git clone https://github.com/yourusername/kernhell.git
    cd kernhell
    ```

2.  **Virtual Environment**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install KernHell**
    ```bash
    pip install .
    ```

4.  **Install Browsers**
    ```bash
    playwright install chromium
    ```
