"""
test_scientific.py
------------------
Tests for Calculator scientific-mode operations: square root, power, reciprocal.
"""

import allure
import pytest


@allure.epic("Calculator Automation")
@allure.feature("Scientific Mode")
@pytest.mark.scientific
class TestScientificMode:

    @pytest.fixture(autouse=True)
    def switch_to_scientific(self, calculator):
        """Switch to Scientific mode before every test in this class."""
        calculator.switch_mode("Scientific")
        yield
        # Return to Standard after each test to keep state clean
        calculator.switch_mode("Standard")

    # ------------------------------------------------------------------
    # Square root
    # ------------------------------------------------------------------

    @allure.story("Square Root")
    @allure.title("Square root of a perfect square")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_sqrt_perfect_square(self, calculator):
        calculator.clear()
        calculator.enter_number(144)
        calculator.press_operator("√")
        result = calculator.get_display()
        assert result == "12", f"√144 should be 12, got {result}"

    @allure.story("Square Root")
    @allure.title("Square root of zero")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.edge_case
    def test_sqrt_zero(self, calculator):
        calculator.clear()
        calculator.enter_number(0)
        calculator.press_operator("√")
        assert calculator.get_display() == "0"

    @allure.story("Square Root")
    @allure.title("Square root of negative number shows error")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.edge_case
    def test_sqrt_negative(self, calculator):
        calculator.clear()
        calculator.enter_number(-1)
        calculator.press_operator("√")
        result = calculator.get_display()
        assert "Invalid input" in result or "error" in result.lower(), \
            f"Expected error for √(-1), got {result}"

    # ------------------------------------------------------------------
    # Power (x²)
    # ------------------------------------------------------------------

    @allure.story("Power")
    @allure.title("Square of a positive integer")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_square(self, calculator):
        calculator.clear()
        calculator.enter_number(9)
        calculator.press_operator("x²")
        result = calculator.get_display()
        assert result == "81", f"9² should be 81, got {result}"

    @allure.story("Power")
    @allure.title("Square of zero")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.edge_case
    def test_square_zero(self, calculator):
        calculator.clear()
        calculator.enter_number(0)
        calculator.press_operator("x²")
        assert calculator.get_display() == "0"

    # ------------------------------------------------------------------
    # Reciprocal (1/x)
    # ------------------------------------------------------------------

    @allure.story("Reciprocal")
    @allure.title("Reciprocal of 2 is 0.5")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_reciprocal(self, calculator):
        calculator.clear()
        calculator.enter_number(2)
        calculator.press_operator("1/x")
        result = calculator.get_display()
        assert result == "0.5", f"1/2 should be 0.5, got {result}"

    @allure.story("Reciprocal")
    @allure.title("Reciprocal of zero shows error")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.edge_case
    def test_reciprocal_zero(self, calculator):
        calculator.clear()
        calculator.enter_number(0)
        calculator.press_operator("1/x")
        result = calculator.get_display()
        assert "Cannot divide by zero" in result or "∞" in result, \
            f"Expected division by zero message, got {result}"
