# 🔥 KernHell

> *"The Heart of Your System Where Innovation Meets Precision"*

**AI-Powered Autonomous Self-Healing Testing Engine & CLI tool for Playwright.**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![Next.js 14](https://img.shields.io/badge/dashboard-Next.js%2014-black.svg)](https://nextjs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI/CD Status](https://img.shields.io/badge/tests-79%20passed%20(100%25)-brightgreen.svg)](https://github.com/riteshkumar072/KernHell)
[![TypeScript & Python](https://img.shields.io/badge/playwright-Python%20%7C%20TypeScript-blue.svg)](https://playwright.dev/)

---

## ⚡ The Problem

Modern frontend engineering moves fast. When developers refactor classes, IDs, or DOM wrappers (e.g., `#buy-now` becomes `#purchase-btn`), automated Playwright and Selenium test suites fail even though the business functionality works seamlessly. QA teams waste 30–40% of their time manually maintaining broken selectors.

**KernHell autonomously resolves broken selectors in real-time across both Python and TypeScript/JavaScript test suites, preserving 100% of your code formatting, comments, and QA sanity.**

---

## 🏛️ Autonomous 6-Stage Healing Architecture

```mermaid
flowchart TD
    A[Playwright Locator Timeout] -->|1. Intercept| B(Scanner & Live DOM Capture)
    B -->|2. Prune| C(Selectolax Lexbor HTML5 Pruner)
    C -->|85% Token Reduction| D{3. Dense Vector Cache}
    D -->|Cache Hit <5ms| G[Strict DOM Verification]
    D -->|Cache Miss| E[4. AI Brain: LiteLLM Gateway]
    E -->|Intent Diagnosis| F{RENAME vs MISSING?}
    F -->|MISSING: Real Bug| H[Anti-Hallucination Guardrail: Abort Healing]
    F -->|RENAME: Safe Refactor| G
    G -->|5. Verify Unambiguous Element| I[Selector Fix: role / data-testid / text]
    I -->|Store Embedding| D
    I -->|6. Surgical Patch| J[Surgical CST & Line Patcher]
    J -->|Preserve Comments & Formatting| K[Automatic Verification Runner]
    K -->|Pass| L[Commit Fix & Log Run]
    K -->|Fail| M[Immediate Rollback from .kernhell.bak]
```

---

## 🚀 Key Features

- **Multi-Language Playwright Support**: Seamlessly heals both **Python (`pytest-playwright`)** and **TypeScript / JavaScript (`@playwright/test`)** test suites with zero configuration.
- **Failure Interception & Live DOM Capture (`Scanner`)**: Intercepts Playwright selector timeouts and crashes, capturing the error stack trace, line number, broken selector, and live DOM snapshot (`page.content()`).
- **High-Speed Semantic DOM Pruning (`DOMPruner`)**: Strips scripts, styles, SVGs, base64 data, and non-semantic wrappers using `selectolax` to slash token usage by 80–90% while keeping semantic landmarks and accessibility roles.
- **Semantic Vector Memory (`Vector Cache`)**: 384-dimensional dense cosine index matching broken selectors against historical fixes. Resolves recurring failures in **<5ms** with zero LLM API cost.
- **Strict Anti-Hallucination Guardrails**: Distinguishes between renamed selectors (`RENAME`) and genuine missing features (`MISSING`) to prevent false-positive heals on actual product regressions.
- **Surgical Code Patching (`Patcher`)**: Surgically transforms only the target locator expression in the AST / file without reformatting unrelated code or stripping inline comments (supports Python LibCST & TypeScript line targeting).
- **Automated Verification & Zero-Risk Rollback (`Verifier`)**: Re-runs the patched test in a sandbox (via `pytest` or `npx playwright test`); if it fails, immediately restores the code from `.kernhell.bak`.
- **Mission Control Dashboard (`Next.js App Router`)**: High-tech, dark-mode glassmorphic web dashboard providing live stats, real-time healing stream, semantic memory inspector, and interactive simulation playground.

---

## 📦 Installation

### Quick Install (from PyPI)

```bash
pip install kernhell
```

That's it! Now run `kernhell --help` to get started.

### With Optional Dependencies

```bash
# Install with dashboard support
pip install kernhell[dashboard]

# Install everything (dev + dashboard)
pip install kernhell[all]
```

### 🔧 Developer Setup (Contributing)

```bash
# Clone the repository
git clone https://github.com/riteshkumar072/KernHell.git
cd KernHell

# Install in editable mode with all dev dependencies
pip install -e ".[all]"

# Install Mission Control dashboard dependencies
cd dashboard
npm install
cd ..
```

---

## 🛠️ CLI Usage

```text
Usage: kernhell [OPTIONS] COMMAND [ARGS]...

┌─ Commands ──────────────────────────────────────────────────────────────────┐
│ setup       Interactive setup wizard to configure your AI / LLM provider &  │
│             API keys.                                                       │
│ init        Alias for 'setup' command.                                      │
│ switch-llm  Interactively switch the active AI / LLM provider.              │
│ llm         Inspect, set, and switch AI / LLM providers (Gemini, OpenAI,    │
│             Claude, Groq, Ollama, Offline).                                 │
│ scan        Scan a test file to detect broken selectors and capture DOM     │
│             snapshots.                                                      │
│ heal        Autonomously heal broken Playwright selectors in a test file.   │
│ dashboard   Launch the KernHell Mission Control Dashboard and REST API.     │
│ ui          Alias for 'dashboard' command.                                  │
│ cache       Inspect, query, and manage KernHell's Semantic Vector Cache.    │
│ config      View and configure KernHell engine parameters.                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🤖 Supported AI Providers & LLM Management

KernHell gives you full freedom to choose whichever AI engine you prefer, or run **100% Offline with zero API keys**.

| Provider | Default Model | Speed | Cost | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Google Gemini** | `gemini-3.5-flash` | Ultra-fast | Free Tier | **Recommended**. Exceptional accuracy and zero setup cost. |
| **OpenAI** | `gpt-4o-mini` / `gpt-4o` | Fast | Paid API | Industry standard accuracy for complex selectors. |
| **Anthropic Claude** | `claude-3-5-sonnet` | Fast | Paid API | Deep reasoning for ambiguous multi-level DOM layouts. |
| **Groq Cloud** | `llama-3.3-70b` | Lightning (~500 T/s) | Free Tier | Ultra-low latency inference for high-speed CI/CD. |
| **Ollama (Local)** | `llama3.2` / `qwen` | Local Hardware | Free (Offline) | 100% private, runs entirely on your local machine (`http://localhost:11434`). |
| **Free Offline Mode** | *Built-in heuristic* | Instant (<5ms) | Free (No API) | Uses Selectolax HTML DOM parser + 384-d Vector Cache. Zero API key needed. |

### First-Run Automatic Onboarding
When running KernHell for the first time in an interactive terminal, if no API key is detected, KernHell automatically asks:
```text
⚡ Welcome to KernHell! No AI / LLM provider has been configured yet.
Would you like to select an LLM provider now (Gemini / OpenAI / Claude / Groq / Ollama / Free Offline)? [Y/n]:
```
Pressing `Enter` opens the interactive setup wizard immediately.

---

### Managing and Switching LLMs

```bash
# 1. View currently active LLM provider, model, and API key status
kernhell llm show
# or simply:
kernhell llm

# 2. Interactively switch to another provider anytime
kernhell llm switch
# or:
kernhell switch-llm
# or:
kernhell setup

# 3. Directly switch LLM provider via CLI flags
kernhell llm set gemini --key "AIzaSy..."
kernhell llm set groq --key "gsk_..."
kernhell llm set openai --model "gpt-4o" --key "sk-..."
kernhell llm set anthropic --key "sk-ant-..."
kernhell llm set ollama --model "llama3.2" --api-base "http://localhost:11434"
kernhell llm set offline    # Switch to 100% free offline heuristic mode
```

---

### 1. Scan a Test File for Broken Selectors

```bash
kernhell scan tests/test_checkout.py
```

### 2. Autonomously Heal a Test File or Suite

```bash
# Preview changes without modifying code (dry run)
kernhell heal tests/test_checkout.py --dry-run

# Surgically patch and verify fix with automatic backup
kernhell heal tests/test_checkout.py

# Batch heal all test files in a folder (Python & TypeScript)
kernhell heal tests/

# Export machine-readable report for CI/CD pipelines
kernhell heal tests/ --output json
```

### 3. Launch the Mission Control Dashboard

```bash
# Start FastAPI REST API and open dashboard in browser
kernhell dashboard

# Or run Next.js frontend directly:
cd dashboard
npm run dev
```

Visit **`http://localhost:3000`** to view the live dashboard and interactive playground.

### 4. Semantic Vector Memory & Cache

```bash
# List all verified cached selector mappings
kernhell cache list

# View cache hit/miss ratio and efficiency metrics
kernhell cache stats

# Purge semantic memory
kernhell cache clear
```

### 5. Engine Configuration

```bash
# Display active settings
kernhell config show

# Run the interactive configuration wizard
kernhell config init
```

---

## 🖥️ Mission Control Dashboard

The dashboard provides a production-grade operations center:

- **Overview (`/`)**: Real-time healing metrics (autonomous fixes, cache efficiency, real bugs guarded, dollar savings), live 6-stage pipeline status, and recent activity stream.
- **Interactive Playground (`/playground`)**: Test healer sandbox with pre-configured refactor scenarios and out-of-stock guardrail alerts.
- **Semantic Memory Explorer (`/cache`)**: Searchable browser for 384-dimensional dense vector embeddings with hit counts and verification badges.
- **Run History & Diffs (`/history`)**: Audit trail with side-by-side syntax-highlighted unified diffs of AST code patches.

---

## 🧪 Running the Test Suite

```bash
# Run all 59 unit and integration tests
python -m pytest -v

# Run with test coverage
python -m pytest tests/unit -v --cov=src/kernhell
```
---



## 📄 License

MIT &copy; 2026 Ritesh Kumar • KernHell Systems
