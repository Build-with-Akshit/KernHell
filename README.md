# 🔥 KernHell

> *"The Heart of Your System Where Innovation Meets Precision"*

AI-Powered Autonomous Self-Healing Testing Engine & CLI tool for Playwright.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ⚡ The Problem

Modern frontend engineering moves fast. When developers refactor classes, IDs, or DOM wrappers (e.g., `#buy-now` becomes `#purchase-btn`), automated Playwright and Selenium test suites fail even though the business functionality works seamlessly. QA teams waste 30–40% of their time manually maintaining broken selectors.

**KernHell autonomously resolves broken selectors in real-time.**

---

## 🚀 Key Features

- **Failure Interception & Context Capture (`Scanner`)**: Intercepts Playwright selector timeouts and crashes, capturing the error stack trace, line number, broken selector, and live DOM snapshot (`page.content()`).
- **High-Speed Semantic DOM Pruning (`DOMPruner`)**: Strips scripts, styles, SVGs, base64 data, and non-semantic wrappers using `selectolax` to slash token usage by 80–90% while keeping semantic landmarks and accessibility roles.
- **Strict Anti-Hallucination Guardrails**: Distinguishes between renamed selectors (`RENAME`) and genuine missing features (`MISSING`) to prevent false-positive heals.
- **Rich Terminal UX**: Beautiful status panels, syntax-highlighted failure code, pruning compression statistics, and summary reports.
- **Extensible Architecture**: Engineered for AI diagnosis (`Analyzer`), AST surgical code patching (`Patcher`), and semantic vector caching (`ChromaDB`).

---

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/kernhell/kernhell.git
cd kernhell

# Install in editable mode
pip install -e ".[dev]"
```

---

## 🛠️ CLI Usage

### 1. Scan a Test File for Failures (Dry Run / Detection)

```bash
kernhell scan tests/fixtures/sample_test.py
```

### 2. Autonomously Heal a Test File

```bash
kernhell heal tests/fixtures/sample_test.py --dry-run
```

### 3. Check Version

```bash
kernhell --version
```

---

## 🧪 Running Tests

```bash
pytest
```

---

## 🗺️ Execution Roadmap

- [x] **Weekend 1: Foundation (Scanner, Pruner, Core Models & CLI)**
- [ ] **Weekend 2: AI Brain (Analyzer, Healer & AST CST Surgeon)**
- [ ] **Weekend 3: Semantic Memory (ChromaDB Vector Cache & JS Support)**
- [ ] **Weekend 4: Mission Control Dashboard (Next.js & Production Release)**

---

## 📄 License

MIT &copy; 2026 KernHell Systems
