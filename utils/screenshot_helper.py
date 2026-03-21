"""
screenshot_helper.py
--------------------
Captures screenshots of the Calculator window and attaches them to
Allure reports for failed (and optionally passing) tests.
"""

from __future__ import annotations

import logging
import time
from io import BytesIO
from pathlib import Path

import allure

logger = logging.getLogger(__name__)

SCREENSHOT_DIR = Path("screenshots")


def capture_and_attach(window, label: str = "screenshot") -> None:
    """
    Take a screenshot of *window* and attach it to the current Allure step.

    Args:
        window: A pywinauto window wrapper (``WindowSpecification``).
        label:  The name shown in the Allure attachment panel.
    """
    SCREENSHOT_DIR.mkdir(exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = SCREENSHOT_DIR / f"{label}_{ts}.png"

    try:
        img = window.capture_as_image()
        img.save(str(path))

        # Attach as PNG to Allure report
        buf = BytesIO()
        img.save(buf, format="PNG")
        allure.attach(
            buf.getvalue(),
            name=label,
            attachment_type=allure.attachment_type.PNG,
        )
        logger.debug("Screenshot attached: %s", path)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Could not capture screenshot: %s", exc)


def attach_text(content: str, label: str = "log") -> None:
    """Attach a plain-text snippet to the Allure report."""
    allure.attach(content, name=label, attachment_type=allure.attachment_type.TEXT)
