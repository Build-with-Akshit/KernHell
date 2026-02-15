
# KernHell Setup Guide for Linux (Ubuntu/Debian)

## Prerequisites
1.  **Python 3.10+**:
    ```bash
    sudo apt update
    sudo apt install python3 python3-pip python3-venv git
    ```
2.  **Node.js (Optional)**:
    ```bash
    # Via NVM/NodeSource recommended
    curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
    sudo apt-get install -y nodejs
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
    sudo playright install-deps
    ```

## "Externally Managed Environment" Error?
If you see this error, ensure you are inside the `venv` active shell.
Do NOT use `sudo pip install`.
