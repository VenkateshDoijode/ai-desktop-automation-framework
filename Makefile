# ============================================================
# Makefile — Calculator Automation Framework
# Usage: make <target>
# ============================================================

PYTHON     := python
PYTEST     := pytest
ALLURE     := allure
RESULTS    := allure-results
REPORT     := allure-report
TESTS      := tests/

.PHONY: help install test smoke regression scientific ai clean report serve open-report

# ── Default target ──────────────────────────────────────────
help:
	@echo ""
	@echo "  Calculator Automation Framework — available targets"
	@echo "  ────────────────────────────────────────────────────"
	@echo "  install        Install all Python dependencies"
	@echo "  test           Run ALL tests + generate Allure report"
	@echo "  smoke          Run @smoke tests only"
	@echo "  regression     Run @regression tests only"
	@echo "  scientific     Run @scientific tests only"
	@echo "  ai             Run @ai_generated tests only"
	@echo "  edge           Run @edge_case tests only"
	@echo "  report         Generate Allure HTML report"
	@echo "  serve          Generate + serve Allure report in browser"
	@echo "  clean          Remove results, report, screenshots, logs"
	@echo ""

# ── Setup ───────────────────────────────────────────────────
install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt
	@echo "✓ Dependencies installed."

# ── Test targets ────────────────────────────────────────────
test:
	$(PYTEST) $(TESTS) --alluredir=$(RESULTS) -v
	$(MAKE) report

smoke:
	$(PYTEST) $(TESTS) -m smoke --alluredir=$(RESULTS) -v

regression:
	$(PYTEST) $(TESTS) -m regression --alluredir=$(RESULTS) -v

scientific:
	$(PYTEST) $(TESTS) -m scientific --alluredir=$(RESULTS) -v

ai:
	$(PYTEST) $(TESTS) -m ai_generated --alluredir=$(RESULTS) -v

edge:
	$(PYTEST) $(TESTS) -m edge_case --alluredir=$(RESULTS) -v

# ── Reporting ────────────────────────────────────────────────
report:
	@echo "Generating Allure report…"
	$(ALLURE) generate $(RESULTS) --clean --output $(REPORT)
	@echo "✓ Report at: $(REPORT)/index.html"

serve:
	$(ALLURE) serve $(RESULTS)

open-report:
	start $(REPORT)/index.html

# ── Cleanup ──────────────────────────────────────────────────
clean:
	@if exist $(RESULTS) rmdir /S /Q $(RESULTS)
	@if exist $(REPORT)  rmdir /S /Q $(REPORT)
	@if exist screenshots rmdir /S /Q screenshots
	@if exist logs        rmdir /S /Q logs
	@if exist __pycache__ rmdir /S /Q __pycache__
	@echo "✓ Cleaned."
