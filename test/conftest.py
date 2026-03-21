"""
conftest.py
-----------
Session-scoped and function-scoped pytest fixtures for the Calculator
automation framework. Handles app launch, teardown, screenshots on failure,
AI enhancer wiring, and Allure metadata.
"""

from __future__ import annotations

import logging
import os
import sys

import allure
import pytest

# Make src/ and utils/ importable regardless of working directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.ai_enhancer import AIEnhancer
from src.app_launcher import CalculatorLauncher
from src.calculator_page import CalculatorPage
from utils.logger import setup_logging
from utils.screenshot_helper import capture_and_attach

setup_logging(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Session-level fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def ai_enhancer() -> AIEnhancer:
    """Single AI enhancer instance reused across the whole test session."""
    return AIEnhancer()


# ---------------------------------------------------------------------------
# Function-level fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def calculator(request):
    """
    Launch Calculator, yield a :class:`CalculatorPage`, and close the app
    after each test.  On failure, capture a screenshot and attach it to
    the Allure report.
    """
    launcher = CalculatorLauncher(backend="uia")
    page: CalculatorPage | None = None

    try:
        launcher.launch()
        page = CalculatorPage(launcher.get_window())
        logger.info("Test started: %s", request.node.name)
        yield page
    except Exception as exc:
        logger.error("Fixture setup failed: %s", exc)
        pytest.fail(f"Could not launch Calculator: {exc}", pytrace=False)
    finally:
        # Screenshot on failure
        if request.node.rep_call is not None and request.node.rep_call.failed:
            if launcher.window:
                with allure.step("Capture failure screenshot"):
                    capture_and_attach(launcher.get_window(), label="FAILURE")
        launcher.close()


# ---------------------------------------------------------------------------
# Hooks
# ---------------------------------------------------------------------------


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Stash the test result on the item so the fixture can read it."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


# ---------------------------------------------------------------------------
# Allure environment metadata (written once per session)
# ---------------------------------------------------------------------------


def pytest_configure(config):
    import platform
    allure_dir = config.getoption("--alluredir", default="allure-results")
    if allure_dir:
        env_path = os.path.join(allure_dir, "environment.properties")
        os.makedirs(allure_dir, exist_ok=True)
        with open(env_path, "w") as f:
            f.write(f"OS={platform.system()} {platform.release()}\n")
            f.write(f"Python={sys.version.split()[0]}\n")
            f.write(f"Framework=pywinauto + pytest + Allure\n")
            f.write(f"AI_Model=claude-sonnet-4-20250514\n")
