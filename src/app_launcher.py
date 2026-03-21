"""
app_launcher.py
---------------
Handles launching, connecting to, and closing the Windows Calculator application
using pywinauto's Application interface.
"""

import time
import logging
from pywinauto import Application, Desktop
from pywinauto.findwindows import ElementNotFoundError

logger = logging.getLogger(__name__)


class CalculatorLauncher:
    """
    Manages the lifecycle of the Windows Calculator application.

    Supports both the modern UWP Calculator (Windows 10/11) and
    the legacy Win32 Calculator for older systems.
    """

    APP_PATH_UWP = "calc.exe"
    WINDOW_TITLE_PATTERN = "Calculator"
    CONNECT_TIMEOUT = 10  # seconds

    def __init__(self, backend: str = "uia"):
        """
        Args:
            backend: 'uia' for UIA/modern apps (recommended),
                     'win32' for legacy Win32 apps.
        """
        self.backend = backend
        self.app: Application | None = None
        self.window = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def launch(self) -> "CalculatorLauncher":
        """Launch Calculator and wait until its window is ready."""
        logger.info("Launching Calculator application …")
        self.app = Application(backend=self.backend).start(
            self.APP_PATH_UWP, wait_for_idle=False
        )
        self._wait_for_window()
        logger.info("Calculator launched successfully.")
        return self

    def connect(self) -> "CalculatorLauncher":
        """Connect to an already-running Calculator instance."""
        logger.info("Connecting to running Calculator instance …")
        self.app = Application(backend=self.backend).connect(
            title_re=self.WINDOW_TITLE_PATTERN
        )
        self._wait_for_window()
        logger.info("Connected to Calculator.")
        return self

    def close(self) -> None:
        """Close the Calculator window gracefully."""
        if self.app:
            try:
                self.app.kill()
                logger.info("Calculator closed.")
            except Exception as exc:  # noqa: BLE001
                logger.warning("Could not close Calculator: %s", exc)
        self.app = None
        self.window = None

    def get_window(self):
        """Return the main Calculator window wrapper."""
        if self.window is None:
            raise RuntimeError("Calculator window is not initialised. Call launch() first.")
        return self.window

    def take_screenshot(self, filepath: str) -> None:
        """Capture a screenshot of the Calculator window."""
        try:
            self.get_window().capture_as_image().save(filepath)
            logger.debug("Screenshot saved to %s", filepath)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Screenshot failed: %s", exc)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _wait_for_window(self) -> None:
        deadline = time.time() + self.CONNECT_TIMEOUT
        while time.time() < deadline:
            try:
                self.window = self.app.window(title_re=self.WINDOW_TITLE_PATTERN)
                self.window.wait("visible", timeout=5)
                self.window.set_focus()
                return
            except (ElementNotFoundError, Exception):  # noqa: BLE001
                time.sleep(0.5)
        raise TimeoutError(
            f"Calculator window not found within {self.CONNECT_TIMEOUT}s."
        )
