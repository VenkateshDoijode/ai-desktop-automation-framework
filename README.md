<div align="center">

# 🧮 Calculator Automation Framework

### AI-Enhanced Windows Desktop Test Automation

**pywinauto · pytest · Allure Reports · Claude AI · GitHub Actions**

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=flat-square&logo=python)
![pywinauto](https://img.shields.io/badge/pywinauto-0.6.8-green?style=flat-square)
![pytest](https://img.shields.io/badge/pytest-8.3-orange?style=flat-square&logo=pytest)
![Allure](https://img.shields.io/badge/Allure-2.27-purple?style=flat-square)
![Claude](https://img.shields.io/badge/Claude-Sonnet_4-black?style=flat-square)
![CI](https://img.shields.io/badge/CI-GitHub_Actions-blue?style=flat-square&logo=github-actions)
![OS](https://img.shields.io/badge/OS-Windows_10%2F11-0078D4?style=flat-square&logo=windows)

</div>

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Project Structure](#project-structure)
4. [Layer Descriptions](#layer-descriptions)
5. [AI Enhancement](#ai-enhancement)
6. [Test Design](#test-design)
7. [Reporting](#reporting)
8. [CI/CD Pipeline](#cicd-pipeline)
9. [Setup & Usage](#setup--usage)
10. [pywinauto vs WinAppDriver](#pywinauto-vs-winappdriver)
11. [Decision Guide](#decision-guide)
12. [Troubleshooting](#troubleshooting)

---

## Overview

This framework automates the **Windows Calculator** application using a layered, production-grade architecture. It combines the low-level UI accessibility power of **pywinauto** with **AI-generated test cases** from Anthropic's Claude API, structured reporting via **Allure**, and full **CI/CD** integration through GitHub Actions.

The framework demonstrates:

- Clean separation of concerns through a Page Object Model (POM)
- Intelligent test generation and failure analysis using a live LLM
- Rich, stakeholder-ready HTML reports with screenshots and step tracing
- Fully automated execution on a real Windows GitHub Actions runner
- Graceful degradation when optional services (AI key) are unavailable

---

## Architecture

The framework is organized into five logical tiers that each have a single responsibility. Data flows strictly downward — tests call the POM, the POM calls the launcher, and the launcher interacts with the Windows accessibility tree.

```
┌─────────────────────────────────────────────────────────────────┐
│                    CONTINUOUS INTEGRATION                       │
│              GitHub Actions  ·  windows-latest runner           │
│        push / pull_request / schedule (nightly) / manual        │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                       TEST LAYER                                │
│   test_basic_operations · test_scientific · test_ai_enhanced    │
│           test_parametrized  ·  conftest fixtures               │
│                                                                 │
│   Markers:  @smoke  @regression  @scientific  @edge_case        │
│             @ai_generated                                       │
└────────────┬──────────────────┬───────────────────┬────────────┘
             │                  │                   │
┌────────────▼──────┐  ┌────────▼────────┐  ┌──────▼──────────────┐
│  CalculatorPage   │  │CalculatorLauncher│  │    AIEnhancer       │
│  (Page Object)    │  │ (App Lifecycle)  │  │  (Claude API)       │
│                   │  │                  │  │                     │
│ press_digit()     │  │ launch()         │  │ generate_test_cases │
│ press_operator()  │  │ connect()        │  │ analyse_failure()   │
│ calculate()       │  │ close()          │  │ generate_edge_cases │
│ get_display()     │  │ get_window()     │  │ summarise_run()     │
│ switch_mode()     │  │ take_screenshot()│  │                     │
└────────────┬──────┘  └────────┬─────────┘  └──────┬─────────────┘
             │                  │                    │
┌────────────▼──────────────────▼──────┐  ┌─────────▼──────────────┐
│       pywinauto (UIA backend)        │  │  Anthropic REST API     │
│                                      │  │  claude-sonnet-4        │
│  Application()  ·  child_window()    │  │  /v1/messages endpoint  │
│  click_input()  ·  window_text()     │  │                         │
│  wait()  ·  capture_as_image()       │  │  JSON ←→ TestCase       │
└────────────┬─────────────────────────┘  └────────────────────────┘
             │
┌────────────▼──────────────────────────────────────────────────────┐
│               Windows Accessibility Tree (UIA)                    │
│         Windows 10 / 11  ·  calc.exe  ·  UWP Calculator          │
│  AutomationId: num0Button … equalButton … CalculatorResults …     │
└───────────────────────────────────────────────────────────────────┘
             │
┌────────────▼──────────────────────────────────────────────────────┐
│                         UTILITIES                                 │
│    logger.py (colorlog + rotating file)                           │
│    screenshot_helper.py (capture → Allure attach)                 │
│    allure-results/categories.json (defect classification)         │
└───────────────────────────────────────────────────────────────────┘
             │
┌────────────▼──────────────────────────────────────────────────────┐
│                         REPORTING                                 │
│    Allure HTML Report  ·  GitHub Pages  ·  CI Job Summary         │
│    Steps · Screenshots · Trends · Environment Properties          │
└───────────────────────────────────────────────────────────────────┘
```

### Key Design Principles

**Single Direction Data Flow.** Tests never touch `pywinauto` directly. Every UI interaction is mediated through `CalculatorPage`. A Calculator UI change (e.g. a button's `AutomationId` is renamed) only ever requires a change in one file.

**Fail-Fast Fixture.** The `calculator` pytest fixture launches the app, yields the page object, and unconditionally closes the app in its `finally` block. If launch fails, the test is marked `FAILED` immediately with a clean error — no orphaned Calculator processes accumulate.

**Graceful AI Degradation.** If `ANTHROPIC_API_KEY` is not set or the `anthropic` package is missing, every `AIEnhancer` method silently returns a pre-built stub result. The entire test suite runs without the AI layer — CI never breaks due to a missing API key.

**Allure as the Single Source of Truth.** Every meaningful action (digit press, operator press, mode switch, display read) is wrapped in `@allure.step`. Failures are enriched with screenshots, actual vs expected values, and an optional AI-generated root-cause analysis — all accessible in one HTML report.

---

## Project Structure

```
calculator_automation/
│
├── .github/
│   └── workflows/
│       └── automation.yml          # Full CI/CD pipeline definition
│
├── src/                            # Core automation library
│   ├── __init__.py
│   ├── app_launcher.py             # Calculator app lifecycle manager
│   ├── calculator_page.py          # Page Object Model (all UI interactions)
│   └── ai_enhancer.py              # Claude API integration layer
│
├── tests/                          # Test suite
│   ├── __init__.py
│   ├── conftest.py                 # Session/function fixtures, hooks, env metadata
│   ├── test_basic_operations.py    # Addition, subtraction, multiplication, division
│   ├── test_scientific.py          # Scientific mode: sqrt, square, reciprocal
│   ├── test_ai_enhanced.py         # AI-generated cases, failure analysis, run summary
│   ├── test_parametrized.py        # Data-driven tests via pytest.mark.parametrize
│   └── test_data.py                # Static test datasets (inputs + expected outputs)
│
├── utils/                          # Cross-cutting utilities
│   ├── __init__.py
│   ├── logger.py                   # Colorised console + rotating file logger
│   └── screenshot_helper.py        # Window capture → Allure attachment
│
├── allure-results/                 # Raw Allure JSON output (gitignored except categories)
│   └── categories.json             # Defect classification rules
│
├── allure-report/                  # Generated HTML report (gitignored)
├── screenshots/                    # Failure screenshots (gitignored)
├── logs/                           # Rotating log files (gitignored)
│
├── .env.example                    # Environment variable template
├── .gitignore
├── Makefile                        # Convenience targets (make smoke, make serve …)
├── pytest.ini                      # pytest configuration and marker definitions
├── requirements.txt                # Pinned Python dependencies
├── run_smoke.py                    # CLI runner script with argparse
└── README.md
```

---

## Layer Descriptions

### `src/app_launcher.py` — Application Lifecycle

`CalculatorLauncher` manages the Calculator process from launch to teardown. It supports two access modes:

- `launch()` spawns a fresh `calc.exe` process and waits for the window to appear
- `connect()` attaches to an already-running Calculator instance by window title

Internally it polls for the window with a configurable timeout (default 10 s), sets focus, and exposes the window handle via `get_window()`. The `backend="uia"` parameter selects the **UI Automation** accessibility layer, which is the correct choice for modern UWP apps on Windows 10/11.

```python
launcher = CalculatorLauncher(backend="uia")
launcher.launch()
window = launcher.get_window()
launcher.close()
```

### `src/calculator_page.py` — Page Object Model

`CalculatorPage` is the single interface for every UI interaction. It maps Calculator controls to their **AutomationId** strings and exposes typed Python methods. No test file ever calls `child_window()` directly.

| Method group | Methods |
|---|---|
| Digit input | `press_digit(d)`, `enter_number(n)` |
| Operators | `press_operator(op)` — supports `+`, `-`, `*`, `/`, `√`, `x²`, `1/x`, `%` |
| Control keys | `press_key(key)` — `=`, `C`, `CE`, `⌫`, `.`, `+/-` |
| Navigation | `switch_mode(mode)` — Standard, Scientific, Programmer, Date Calculation |
| Reading | `get_display()`, `get_expression()` |
| High-level | `calculate(expression)` — parses `"12 + 34"` and returns the display result |

Every method is decorated with `@allure.step`, so the Allure report shows a human-readable step trace for every test without extra boilerplate in the test files themselves.

### `src/ai_enhancer.py` — Claude API Integration

`AIEnhancer` wraps the Anthropic messages API and exposes four domain-specific capabilities:

`generate_test_cases(operation, count)` sends a prompt asking Claude for `count` arithmetic test cases for a described operation. Returns a list of `TestCase` dataclasses with `expression`, `expected`, `description`, and `tags` fields. The prompt enforces raw JSON output so no markdown stripping is needed.

`analyse_failure(test_name, expression, expected, actual, error_message)` given a failing test's context, asks Claude for a `probable_cause`, `suggested_fix`, and `confidence` level. The result is attached to the Allure report so engineers reviewing failures see AI-generated root-cause analysis alongside the screenshot.

`generate_edge_cases(operation)` specifically requests boundary inputs: zero, very large numbers, negative numbers, decimals, divide-by-zero, and overflow scenarios.

`summarise_run(stats)` accepts a dict of run metrics and returns a plain-English `RunSummary` with a headline, details paragraph, and up to three recommendations.

All four methods catch API exceptions and return sensible stub values if the key is absent or the network is unavailable.

### `tests/conftest.py` — Fixtures and Hooks

Two fixtures drive the entire test lifecycle.

`ai_enhancer` (session scope) creates a single `AIEnhancer` instance shared across all tests, avoiding repeated API client initialization.

`calculator` (function scope) launches Calculator, yields `CalculatorPage`, captures a failure screenshot attached to Allure in the `finally` block, and closes the app. The `pytest_runtest_makereport` hook stashes the call-phase result on the item so the fixture can inspect `request.node.rep_call.failed`.

`pytest_configure` writes an `environment.properties` file into the Allure results directory at session start, populating the Allure Environment panel with OS version, Python version, framework name, and AI model.

### `utils/logger.py` — Structured Logging

Configures the root logger once per session with two handlers:

- **Console handler** — colorised output via `colorlog` (green INFO, yellow WARNING, red ERROR). Falls back to plain formatting if `colorlog` is not installed.
- **File handler** — rotating `logs/automation.log`, 5 MB per file, 3 backups, DEBUG level, includes filename and line number.

`pywinauto` and `comtypes` are pinned to WARNING to suppress verbose COM/UIA noise.

### `utils/screenshot_helper.py` — Allure Attachments

`capture_and_attach(window, label)` calls pywinauto's `capture_as_image()`, saves to `screenshots/`, converts to PNG bytes, and attaches to the current Allure report step. `attach_text(content, label)` attaches plain-text snippets — used by the AI enhancer to embed generated test data and analysis output.

---

## AI Enhancement

### How It Works

```
Test Request
     │
     ▼
AIEnhancer.generate_test_cases("addition of two integers", count=5)
     │
     ▼
POST https://api.anthropic.com/v1/messages
{
  "model": "claude-sonnet-4-20250514",
  "messages": [{ "role": "user", "content": "<structured prompt>" }]
}
     │
     ▼
Response JSON:
[
  { "description": "Simple case", "expression": "5 + 3",  "expected": "8",  "tags": ["smoke"] },
  { "description": "Zero addend", "expression": "0 + 99", "expected": "99", "tags": ["edge_case"] },
  ...
]
     │
     ▼
List[TestCase] → each case executed against live Calculator UI
```

### Prompt Engineering

All prompts use a strict constraint: "Return ONLY a valid JSON array / object. No markdown, no explanation." This eliminates the need to strip code fences and makes JSON parsing reliable. A `try/except` around `json.loads()` and a regex to strip occasional fences provides a safety net.

### AI-Powered Failure Analysis

When a test fails, the AI enhancer produces a structured failure report:

```python
analysis = ai_enhancer.analyse_failure(
    test_name     = "test_multiply_negatives",
    expression    = "-3 * -4",
    expected      = "999",        # intentionally wrong
    actual        = "12",
    error_message = "AssertionError: expected 999, got 12"
)
# analysis.probable_cause  → "The expected value 999 is incorrect..."
# analysis.suggested_fix   → "Change expected to '12'..."
# analysis.confidence      → "high"
```

The result is attached to the Allure report as a plain-text attachment, giving engineers actionable guidance alongside the failure screenshot.

---

## Test Design

### Marker Taxonomy

| Marker | Intent | When to run |
|---|---|---|
| `@smoke` | Fast sanity — does the app open and can we add two numbers? | Every commit |
| `@regression` | Full behavioural coverage of all supported operations | Before merge to main |
| `@scientific` | Scientific mode only — sqrt, square, reciprocal | On scientific-mode changes |
| `@edge_case` | Boundary values, divide-by-zero, overflow | Nightly + regression |
| `@ai_generated` | Cases produced by Claude — non-deterministic data | Nightly / exploratory |

### Test Count Summary

| File | Tests | Markers |
|---|---|---|
| `test_basic_operations.py` | 17 | smoke, regression, edge_case |
| `test_scientific.py` | 7 | scientific, regression, edge_case |
| `test_ai_enhanced.py` | 5 | ai_generated, regression |
| `test_parametrized.py` | 37 (parametrized) | regression, edge_case |
| **Total** | **66+** | |

### Page Object Pattern

Tests are intentionally thin. All UI coordination lives in `CalculatorPage`:

```python
# Test file — describes intent only
def test_add_large_numbers(self, calculator):
    result = calculator.calculate("999999 + 1")
    assert result == "1,000,000"

# CalculatorPage — owns the mechanism
def calculate(self, expression: str) -> str:
    self.clear()
    left, op, right = expression.split()
    self.enter_number(left)
    self.press_operator(op)
    self.enter_number(right)
    self.press_equals()
    return self.get_display()
```

---

## Reporting

### Allure Report Structure

```
Allure Report
├── Overview          — pass/fail/skip counts, severity breakdown
├── Suites            — tests grouped by Epic → Feature → Story
├── Graphs            — status distribution, severity, duration trends
├── Timeline          — wall-clock execution across workers
├── Behaviors         — BDD-style grouping by Epic / Feature / Story
├── Packages          — file-level grouping
└── Environment       — OS, Python version, AI model, framework name
```

### Allure Annotations Used

| Annotation | Applied at | Purpose |
|---|---|---|
| `@allure.epic` | class | Top-level grouping |
| `@allure.feature` | class | Feature area |
| `@allure.story` | method | User story |
| `@allure.title` | method | Human-readable test name |
| `@allure.severity` | method | BLOCKER / CRITICAL / NORMAL / MINOR |
| `@allure.step` | POM methods | Step-level trace in report |
| `allure.attach` | fixtures/utils | Screenshots, AI analysis text |

### Defect Categories

`allure-results/categories.json` classifies failures automatically:

- **Product Defects** — `AssertionError` (the app returned the wrong value)
- **UI Automation Issues** — `ElementNotFoundError`, `TimeoutError`
- **AI Enhancement Failures** — `APIError`, `anthropic` errors
- **Test Infrastructure Issues** — `RuntimeError`, `ConnectionError`
- **Skipped Tests** — any test with skipped status

---

## CI/CD Pipeline

```
Trigger (push / PR / schedule / manual)
         │
         ▼
┌─────────────────────────────────────┐
│  Job: run-tests  (windows-latest)   │
│                                     │
│  1.  Checkout repository            │
│  2.  Set up Python 3.11             │
│  3.  pip install -r requirements    │
│  4.  Set up Java 17 (Allure CLI)    │
│  5.  Install Allure CLI 2.27        │
│  6.  Create result directories      │
│  7.  Restore Allure history (cache) │
│  8.  Resolve marker from input      │
│  9.  pytest --alluredir=...         │ ← continue-on-error: true
│  10. allure generate                │
│  11. Upload allure-results artifact │
│  12. Upload allure-report artifact  │
│  13. Upload screenshots (on fail)   │
│  14. Upload logs                    │
│  15. Deploy to GitHub Pages         │ ← main branch only
│  16. Write job summary              │
└─────────────────────────────────────┘
```

Allure history is restored from GitHub Actions cache before each run so the report shows trend graphs across runs. The report is published to `gh-pages` and accessible at `https://<owner>.github.io/<repo>/allure-report`.

---

## Setup & Usage

### Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Windows | 10 / 11 | UWP Calculator must be installed |
| Python | 3.9+ | Tested on 3.11 |
| Java | 17+ | Required by Allure CLI only |
| Allure CLI | 2.27 | `choco install allure` or manual install |

### Installation

```bash
# Clone
git clone https://github.com/your-org/calculator-automation.git
cd calculator-automation

# Optional virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set API key (optional — framework works without it)
set ANTHROPIC_API_KEY=sk-ant-your-key-here        # CMD
$env:ANTHROPIC_API_KEY = "sk-ant-your-key-here"   # PowerShell
```

### Running Tests

```bash
make test          # Run all tests and generate Allure report
make smoke         # Fast smoke suite (~30 s)
make regression    # Full regression suite
make ai            # AI-enhanced tests only
make serve         # Generate report + open in browser
make clean         # Remove artifacts

# Direct pytest
pytest tests/ -m "smoke or edge_case" --alluredir=allure-results -v

# CLI runner script
python run_smoke.py --suite regression --serve
```

### Makefile Targets

| Target | Description |
|---|---|
| `make install` | Install Python dependencies |
| `make test` | Run all tests + build Allure report |
| `make smoke` | Smoke suite only |
| `make regression` | Regression suite |
| `make scientific` | Scientific mode tests |
| `make ai` | AI-generated tests |
| `make edge` | Edge/boundary tests |
| `make report` | Generate HTML from existing results |
| `make serve` | Generate + open in browser |
| `make clean` | Remove all generated artifacts |

---

## pywinauto vs WinAppDriver

This is the most consequential architectural decision in a Windows desktop automation project. Understanding the trade-offs determines which tool fits your context.

### What They Are

**pywinauto** is a pure Python library that communicates directly with Windows accessibility APIs — either the legacy **Win32** layer (`backend="win32"`) or the modern **UI Automation** framework (`backend="uia"`). Your Python script talks directly to the Windows kernel accessibility subsystem with no intermediary service.

**WinAppDriver (Windows Application Driver)** is Microsoft's implementation of the WebDriver protocol for desktop applications. It is a local HTTP server (`WinAppDriver.exe`) that accepts WebDriver/Appium JSON Wire Protocol commands over `http://127.0.0.1:4723` and translates them into UIA calls.

```
pywinauto:
  Python Script ──► pywinauto ──► Windows UIA/Win32 API ──► Application

WinAppDriver:
  Python Script ──► Appium Client ──► HTTP ──► WinAppDriver.exe ──► Windows UIA ──► Application
```

### Feature-by-Feature Comparison

| Dimension | pywinauto | WinAppDriver |
|---|---|---|
| **Protocol** | Native Python API | WebDriver / W3C Protocol over HTTP |
| **Language support** | Python only | Any WebDriver-compatible language |
| **Infrastructure required** | Zero — no external service | WinAppDriver.exe must be running; Windows SDK |
| **Installation** | `pip install pywinauto` | Install WinAppDriver + Appium Python client |
| **App support** | Win32, WinForms, WPF, UWP, Qt, MFC | UWP, Win32, WinForms, WPF (via UIA) |
| **Element location** | AutomationId, title, class, control type, regex | id, name, class name, XPath, accessibility id |
| **XPath support** | No | Yes (full XPath 1.0 on the UIA tree) |
| **Screenshot** | `window.capture_as_image()` — window-level | `driver.get_screenshot_as_png()` — full screen |
| **Speed** | Fast — direct API calls, ~20–80 ms per action | Slower — HTTP round-trip per command, ~5–20 ms overhead each |
| **Parallel execution** | Via pytest-xdist (process-level) | Via Appium Grid / Selenium Grid |
| **Mobile integration** | No | Yes — Appium unifies mobile + desktop |
| **Active maintenance** | Community, slower releases | Microsoft-archived 2022, still widely used |
| **CI/CD friction** | Low — just pip install | Medium — must start WinAppDriver.exe in CI |
| **Learning curve** | Low for Python developers | Medium — requires WebDriver/Appium knowledge |
| **Debugging** | Python debugger works natively | Remote debugging via Appium Inspector |
| **Spy tool** | `pywinauto-recorder`, `inspect.exe` | Appium Desktop / WinAppDriver UI Recorder |
| **Licence** | BSD | Apache 2.0 (Microsoft) |

### Performance

pywinauto makes direct Windows API calls in-process. A typical `click_input()` → `window_text()` round-trip is 20–80 ms depending on element complexity.

WinAppDriver adds an HTTP round-trip for every single command — typically 5–20 ms of overhead per call. This compounds: a test that presses 15 buttons has 15 round-trips. A suite taking 45 seconds in pywinauto may take 70–90 seconds with WinAppDriver purely due to protocol overhead.

### Element Location

pywinauto uses a named-parameter model that maps directly to the UIA property set:

```python
# pywinauto — direct, readable
button = window.child_window(auto_id="num5Button", control_type="Button")
result = window.child_window(auto_id="CalculatorResults")
```

WinAppDriver uses WebDriver locator strategies, with `accessibility id` mapping to UIA AutomationId:

```python
# WinAppDriver (Appium Python client) — same element, more ceremony
button = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "num5Button")
result = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "CalculatorResults")
```

XPath is WinAppDriver's advantage for elements lacking a stable AutomationId:

```python
# WinAppDriver XPath — powerful but brittle
button = driver.find_element(AppiumBy.XPATH, '//Button[@Name="Five"]')
```

pywinauto has no XPath. It compensates with regex matching on titles and a rich set of child-finding predicates, but for deeply nested elements with no AutomationId it can require more discovery work.

### Code Side-by-Side

The same test — open Calculator, compute 5 + 3, read result — in both frameworks:

```python
# ── pywinauto ────────────────────────────────────────────────────────────────
from pywinauto import Application

app = Application(backend="uia").start("calc.exe")
win = app.window(title_re="Calculator")
win.child_window(auto_id="num5Button").click_input()
win.child_window(auto_id="plusButton").click_input()
win.child_window(auto_id="num3Button").click_input()
win.child_window(auto_id="equalButton").click_input()
result = win.child_window(auto_id="CalculatorResults").window_text()
print(result)   # "Display is 8"
app.kill()


# ── WinAppDriver ─────────────────────────────────────────────────────────────
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy

caps = {
    "app": "Microsoft.WindowsCalculator_8wekyb3d8bbwe!App",
    "platformName": "Windows",
    "deviceName": "WindowsPC",
}
driver = webdriver.Remote("http://127.0.0.1:4723", caps)
driver.find_element(AppiumBy.ACCESSIBILITY_ID, "num5Button").click()
driver.find_element(AppiumBy.ACCESSIBILITY_ID, "plusButton").click()
driver.find_element(AppiumBy.ACCESSIBILITY_ID, "num3Button").click()
driver.find_element(AppiumBy.ACCESSIBILITY_ID, "equalButton").click()
result = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "CalculatorResults").text
print(result)   # "Display is 8"
driver.quit()
```

The code volume is similar, but WinAppDriver requires `WinAppDriver.exe` to already be running and the UWP package ID to be known upfront. pywinauto just needs `calc.exe`.

### CI Setup Difference

```yaml
# WinAppDriver — additional CI step required
- name: Start WinAppDriver
  run: |
    Start-Process "C:\Program Files\Windows Application Driver\WinAppDriver.exe"
    Start-Sleep -s 5
  shell: pwsh

# pywinauto — nothing extra needed beyond pip install
```

### Cross-Team and Multi-Language Scenarios

If your organisation writes automation in multiple languages — Java for backend API tests, Python for scripting, C# for unit tests — WinAppDriver's WebDriver protocol means any team can write Windows desktop tests using the same Appium client they use for Android/iOS automation. The investment in Appium knowledge transfers.

pywinauto is Python-only. If your wider automation ecosystem is already Python (pytest, requests, Playwright for web), pywinauto fits naturally and adds zero new concepts.

---

## Decision Guide

**Choose pywinauto (this framework's approach) when:**

- Your team writes automation exclusively in Python
- You need the lowest possible setup friction in CI/CD
- Speed matters and you want to minimise latency per test action
- The application is a standard Windows desktop app (Win32, WPF, UWP, WinForms)
- You do not need to share tests with a non-Python team

**Consider WinAppDriver when:**

- Your team already uses Appium for mobile automation and wants a unified driver model
- You need to write desktop automation in Java, C#, or JavaScript
- Your application requires XPath to locate elements with no stable AutomationId
- You need to run tests against a remote Windows machine via Appium Grid
- You are integrating desktop tests into a Selenium Grid infrastructure

---

## Troubleshooting

**Calculator window not found**

```
TimeoutError: Calculator window not found within 10s
```

The UWP Calculator may take longer on first launch after a cold start. Increase the timeout:

```python
launcher = CalculatorLauncher(backend="uia")
launcher.CONNECT_TIMEOUT = 20
```

**AutomationId not found**

```
ElementNotFoundError: child_window(auto_id="num5Button") not found
```

Microsoft occasionally changes AutomationIds between Windows builds. Run `inspect.exe` (Windows SDK) or `pywinauto-recorder` to find the current AutomationId and update `DIGIT_IDS` / `OPERATOR_IDS` in `calculator_page.py`.

**AI features not working**

```
AI enhancer running in stub mode (no API key / package)
```

Set `ANTHROPIC_API_KEY` in your environment (see `.env.example`). Stub mode is intentional — all tests pass without an API key.

**Allure report not generating**

Ensure Java 17+ is installed and `allure` is on your PATH:

```bash
java -version
allure --version
# Install via Chocolatey:
choco install allure
```

**pywinauto COM errors on import**

```
ImportError: ... comtypes
```

Run `pip install pywinauto --upgrade`. If the issue persists: `pip install comtypes`.

---

## Contributing

1. Fork the repository and create a feature branch
2. Add or modify tests — ensure existing tests still pass with `make smoke`
3. Update `test_data.py` if adding new parametrized data sets
4. Run `make regression` before opening a pull request
5. The CI pipeline runs automatically on PR — the Allure report is uploaded as an artifact for review

---

<div align="center">

Built with pywinauto · pytest · Allure · Claude AI · GitHub Actions

</div>
