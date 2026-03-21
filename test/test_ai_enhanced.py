"""
test_ai_enhanced.py
-------------------
Tests that use the AIEnhancer to dynamically generate test cases and
perform intelligent failure analysis. Each test asks Claude for data,
then executes the result against the live Calculator UI.
"""

from __future__ import annotations

import allure
import pytest

from src.ai_enhancer import AIEnhancer, TestCase
from utils.screenshot_helper import attach_text


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _run_test_case(calculator, tc: TestCase) -> None:
    """Execute a single AI-generated TestCase and assert the result."""
    with allure.step(f"AI test: {tc.description}"):
        attach_text(
            f"Expression : {tc.expression}\nExpected   : {tc.expected}",
            label="AI Test Input",
        )
        actual = calculator.calculate(tc.expression)
        attach_text(actual, label="Actual Result")
        assert actual == tc.expected, (
            f"[{tc.description}] {tc.expression} → expected {tc.expected!r}, got {actual!r}"
        )


# ---------------------------------------------------------------------------
# Test classes
# ---------------------------------------------------------------------------


@allure.epic("Calculator Automation")
@allure.feature("AI-Enhanced Testing")
@pytest.mark.ai_generated
class TestAIGeneratedCases:

    @allure.story("Dynamic Test Generation")
    @allure.title("AI-generated addition test cases")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_ai_addition(self, calculator, ai_enhancer: AIEnhancer):
        cases = ai_enhancer.generate_test_cases("integer addition", count=5)
        allure.attach(
            "\n".join(f"{tc.expression} = {tc.expected}" for tc in cases),
            name="AI Generated Cases",
            attachment_type=allure.attachment_type.TEXT,
        )
        assert cases, "AI enhancer returned no test cases"
        for tc in cases:
            _run_test_case(calculator, tc)

    @allure.story("Dynamic Test Generation")
    @allure.title("AI-generated subtraction test cases")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_ai_subtraction(self, calculator, ai_enhancer: AIEnhancer):
        cases = ai_enhancer.generate_test_cases("integer subtraction", count=5)
        assert cases
        for tc in cases:
            _run_test_case(calculator, tc)

    @allure.story("Dynamic Test Generation")
    @allure.title("AI-generated multiplication test cases")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_ai_multiplication(self, calculator, ai_enhancer: AIEnhancer):
        cases = ai_enhancer.generate_test_cases("integer multiplication", count=5)
        assert cases
        for tc in cases:
            _run_test_case(calculator, tc)

    @allure.story("Edge Cases")
    @allure.title("AI-generated edge cases for division")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.edge_case
    def test_ai_division_edge_cases(self, calculator, ai_enhancer: AIEnhancer):
        cases = ai_enhancer.generate_edge_cases("division")
        assert cases
        for tc in cases:
            with allure.step(f"{tc.description}: {tc.expression}"):
                actual = calculator.calculate(tc.expression)
                # Edge cases may have flexible expected values
                if tc.expected:
                    assert actual == tc.expected or any(
                        keyword in actual.lower()
                        for keyword in ["error", "cannot", "infinity", "∞"]
                    ), f"Unexpected result for {tc.expression}: {actual}"


@allure.epic("Calculator Automation")
@allure.feature("AI Failure Analysis")
@pytest.mark.ai_generated
class TestAIFailureAnalysis:

    @allure.story("Failure Analysis")
    @allure.title("AI analyses an intentionally wrong expected value")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.regression
    def test_ai_failure_analysis(self, calculator, ai_enhancer: AIEnhancer):
        """
        Intentionally supply a wrong expected value, catch the AssertionError,
        ask the AI for analysis, and attach it to the report.
        The test itself is considered PASSED if AI produces a valid analysis.
        """
        expression = "8 * 7"
        wrong_expected = "999"

        actual = calculator.calculate(expression)
        error_msg = f"Expected {wrong_expected}, got {actual}"

        analysis = ai_enhancer.analyse_failure(
            test_name="test_ai_failure_analysis",
            expression=expression,
            expected=wrong_expected,
            actual=actual,
            error_message=error_msg,
        )

        allure.attach(
            (
                f"Probable cause : {analysis.probable_cause}\n"
                f"Suggested fix  : {analysis.suggested_fix}\n"
                f"Confidence     : {analysis.confidence}"
            ),
            name="AI Failure Analysis",
            attachment_type=allure.attachment_type.TEXT,
        )

        # Validate the analysis object is well-formed
        assert analysis.probable_cause, "AI should return a probable cause"
        assert analysis.suggested_fix, "AI should suggest a fix"
        assert analysis.confidence in ("high", "medium", "low")


@allure.epic("Calculator Automation")
@allure.feature("AI Run Summary")
@pytest.mark.ai_generated
class TestAIRunSummary:

    @allure.story("Run Summary")
    @allure.title("AI produces a meaningful test-run summary")
    @allure.severity(allure.severity_level.MINOR)
    def test_ai_run_summary(self, calculator, ai_enhancer: AIEnhancer):
        stats = {
            "total": 20,
            "passed": 17,
            "failed": 2,
            "skipped": 1,
            "duration_s": 45.3,
            "suite": "Calculator Standard Mode",
        }

        summary = ai_enhancer.summarise_run(stats)

        allure.attach(
            (
                f"Headline       : {summary.headline}\n"
                f"Details        : {summary.details}\n"
                f"Recommendations:\n"
                + "\n".join(f"  • {r}" for r in summary.recommendations)
            ),
            name="AI Run Summary",
            attachment_type=allure.attachment_type.TEXT,
        )

        assert summary.headline, "AI summary headline must not be empty"
