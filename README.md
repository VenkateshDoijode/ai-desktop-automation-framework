# 🧮 Calculator Automation Framework

AI-Enhanced test automation for Windows Calculator using **pywinauto**, **pytest**, **Allure Reports**, and **GitHub Actions**.

---

## 📁 Project Structure

```
calculator_automation/
├── .github/
│   └── workflows/
│       └── automation.yml          # GitHub Actions CI/CD
├── src/
│   ├── __init__.py
│   ├── app_launcher.py             # Calculator app launcher
│   ├── calculator_page.py          # Page Object Model
│   └── ai_enhancer.py              # AI Enhancement (Claude API)
├── tests/
│   ├── __init__.py
│   ├── conftest.py                 # Pytest fixtures & setup
│   ├── test_basic_operations.py    # Basic arithmetic tests
│   ├── test_scientific.py          # Scientific mode tests
│   └── test_ai_enhanced.py        # AI-generated test cases
├── utils/
│   ├── __init__.py
│   ├── logger.py                   # Logging utility
│   └── screenshot_helper.py        # Screenshot capture
├── allure-results/                 # Allure raw results
├── allure-report/                  # Generated HTML report
├── requirements.txt
├── pytest.ini
└── README.md
```

---

## ⚙️ Setup

### 1. Prerequisites
- **Windows OS** (pywinauto requires Windows)
- Python 3.9+
- Java 8+ (for Allure CLI)
- Allure CLI installed

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set AI API Key (optional)
```bash
set ANTHROPIC_API_KEY=your_key_here   # Windows CMD
$env:ANTHROPIC_API_KEY="your_key"     # PowerShell
```

---

## 🚀 Running Tests

### Run all tests with Allure
```bash
pytest tests/ --alluredir=allure-results -v
allure serve allure-results
```

### Run specific test suite
```bash
pytest tests/test_basic_operations.py --alluredir=allure-results -v
pytest tests/test_ai_enhanced.py --alluredir=allure-results -v
```

### Run with markers
```bash
pytest -m "smoke" --alluredir=allure-results -v
pytest -m "regression" --alluredir=allure-results -v
```

---

## 🤖 AI Enhancement Features

The `ai_enhancer.py` module uses Claude API to:
- **Generate test cases** dynamically based on operation descriptions
- **Analyze failures** and suggest root cause fixes
- **Create edge case** inputs for boundary testing
- **Summarize test runs** with intelligent insights

---

## 📊 Allure Report Features

- ✅ Test status (pass/fail/skip)
- 📸 Screenshots on failure
- 📝 Step-by-step execution logs
- 🏷️ Tags: smoke, regression, AI-generated
- 📈 Trend charts across runs
- 🔗 GitHub Actions integration

---

## 🔄 GitHub Actions

The CI pipeline:
1. Sets up Python & Java environment
2. Installs Allure CLI
3. Runs pytest with Allure reporter
4. Publishes Allure report to GitHub Pages
5. Uploads artifacts for download

---

## 📌 Notes

> **pywinauto** requires an actual Windows desktop environment with Calculator installed.  
> In CI/CD (GitHub Actions), a Windows runner (`windows-latest`) is used.
> The AI enhancement gracefully degrades if no API key is provided.
