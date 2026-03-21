"""
calculator_page.py
------------------
Page Object Model (POM) for the Windows 10/11 UWP Calculator.

Maps every UI element to a named method so tests stay clean and
changes to the UI only require edits in this one file.
"""

import logging
import time
from typing import Union

import allure

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Button automation-ID maps
# ---------------------------------------------------------------------------
DIGIT_IDS = {
    "0": "num0Button",
    "1": "num1Button",
    "2": "num2Button",
    "3": "num3Button",
    "4": "num4Button",
    "5": "num5Button",
    "6": "num6Button",
    "7": "num7Button",
    "8": "num8Button",
    "9": "num9Button",
}

OPERATOR_IDS = {
    "+": "plusButton",
    "-": "minusButton",
    "*": "multiplyButton",
    "/": "divideButton",
    "%": "percentButton",
    "√": "squareRootButton",
    "x²": "xpower2Button",
    "1/x": "invertButton",
}

SPECIAL_IDS = {
    "=": "equalButton",
    "C": "clearButton",        # Clear all
    "CE": "clearEntryButton",  # Clear entry
    "⌫": "backSpaceButton",    # Backspace
    ".": "decimalSeparatorButton",
    "+/-": "negateButton",
}

MODE_IDS = {
    "Standard": "Standard",
    "Scientific": "Scientific",
    "Programmer": "Programmer",
    "Date Calculation": "Date Calculation",
}


class CalculatorPage:
    """
    Provides high-level interactions with the Calculator window.

    Usage::

        page = CalculatorPage(launcher.get_window())
        result = page.calculate("123 + 456")
        assert result == "579"
    """

    def __init__(self, window):
        self._win = window

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    @allure.step("Switch calculator mode to '{mode}'")
    def switch_mode(self, mode: str) -> "CalculatorPage":
        """Open the hamburger menu and select a mode (Standard / Scientific …)."""
        logger.info("Switching to %s mode", mode)
        self._click_by_auto_id("TogglePaneButton")   # ☰ hamburger
        time.sleep(0.3)
        self._click_by_name(mode)
        time.sleep(0.4)
        return self

    # ------------------------------------------------------------------
    # Input helpers
    # ------------------------------------------------------------------

    @allure.step("Press digit '{digit}'")
    def press_digit(self, digit: str) -> "CalculatorPage":
        auto_id = DIGIT_IDS.get(digit)
        if not auto_id:
            raise ValueError(f"Unknown digit: {digit!r}")
        self._click_by_auto_id(auto_id)
        return self

    @allure.step("Press operator '{operator}'")
    def press_operator(self, operator: str) -> "CalculatorPage":
        auto_id = OPERATOR_IDS.get(operator)
        if not auto_id:
            raise ValueError(f"Unknown operator: {operator!r}")
        self._click_by_auto_id(auto_id)
        return self

    @allure.step("Press '{key}'")
    def press_key(self, key: str) -> "CalculatorPage":
        auto_id = SPECIAL_IDS.get(key)
        if not auto_id:
            raise ValueError(f"Unknown special key: {key!r}")
        self._click_by_auto_id(auto_id)
        return self

    @allure.step("Enter number '{number}'")
    def enter_number(self, number: Union[int, float, str]) -> "CalculatorPage":
        """Type a full number including decimal point and negation."""
        number_str = str(number)
        negative = number_str.startswith("-")
        if negative:
            number_str = number_str[1:]

        for ch in number_str:
            if ch.isdigit():
                self.press_digit(ch)
            elif ch in (".", ","):
                self.press_key(".")
            else:
                logger.warning("Ignoring unexpected character %r while entering number", ch)

        if negative:
            self.press_key("+/-")

        return self

    @allure.step("Press equals")
    def press_equals(self) -> "CalculatorPage":
        self.press_key("=")
        return self

    @allure.step("Clear all (C)")
    def clear(self) -> "CalculatorPage":
        self.press_key("C")
        return self

    @allure.step("Clear entry (CE)")
    def clear_entry(self) -> "CalculatorPage":
        self.press_key("CE")
        return self

    # ------------------------------------------------------------------
    # High-level calculation
    # ------------------------------------------------------------------

    @allure.step("Calculate: {expression}")
    def calculate(self, expression: str) -> str:
        """
        Parse and execute a simple infix expression like "12 + 34".

        Supports: +, -, *, /
        Returns the display result as a string.
        """
        self.clear()
        tokens = expression.split()
        if len(tokens) == 1:
            self.enter_number(tokens[0])
        elif len(tokens) == 3:
            left, op, right = tokens
            self.enter_number(left)
            self.press_operator(op)
            self.enter_number(right)
            self.press_equals()
        else:
            raise ValueError(
                f"Expression must be '<num> <op> <num>' or '<num>', got: {expression!r}"
            )
        return self.get_display()

    # ------------------------------------------------------------------
    # Result reading
    # ------------------------------------------------------------------

    @allure.step("Read display value")
    def get_display(self) -> str:
        """Return the current value shown in the Calculator display."""
        try:
            display = self._win.child_window(auto_id="CalculatorResults")
            text: str = display.window_text()
            # Strip leading "Display is " prefix that UIA sometimes returns
            value = text.replace("Display is ", "").strip()
            logger.info("Display value: %s", value)
            return value
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to read display: %s", exc)
            raise

    def get_expression(self) -> str:
        """Return the expression shown above the main display (if visible)."""
        try:
            expr = self._win.child_window(auto_id="CalculatorExpression")
            return expr.window_text().strip()
        except Exception:  # noqa: BLE001
            return ""

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _click_by_auto_id(self, auto_id: str) -> None:
        btn = self._win.child_window(auto_id=auto_id)
        btn.wait("enabled", timeout=5)
        btn.click_input()
        time.sleep(0.05)

    def _click_by_name(self, name: str) -> None:
        btn = self._win.child_window(title=name, control_type="ListItem")
        btn.wait("visible", timeout=5)
        btn.click_input()
        time.sleep(0.05)
