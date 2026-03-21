"""
ai_enhancer.py
--------------
AI-powered test enhancement layer that uses the Anthropic Claude API to:

  1. Generate test-case data (inputs + expected outputs) from natural language.
  2. Analyse test failures and suggest probable root causes.
  3. Produce edge-case inputs for boundary testing.
  4. Summarise a completed test run in plain English.

The module gracefully degrades: when no API key is present every method
returns a sensible stub result so the rest of the framework keeps working.
"""

from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Optional Anthropic import
# ---------------------------------------------------------------------------
try:
    import anthropic  # type: ignore

    _ANTHROPIC_AVAILABLE = True
except ImportError:
    _ANTHROPIC_AVAILABLE = False
    logger.warning("anthropic package not installed – AI enhancement disabled.")

_MODEL = "claude-sonnet-4-20250514"
_MAX_TOKENS = 1024


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class TestCase:
    """A single AI-generated test case."""

    description: str
    expression: str          # e.g. "15 + 27"
    expected: str            # e.g. "42"
    tags: list[str] = field(default_factory=list)


@dataclass
class FailureAnalysis:
    """Root-cause analysis produced by AI for a failed assertion."""

    probable_cause: str
    suggested_fix: str
    confidence: str          # "high" | "medium" | "low"


@dataclass
class RunSummary:
    """Plain-English summary of the full test run."""

    headline: str
    details: str
    recommendations: list[str]


# ---------------------------------------------------------------------------
# Core enhancer
# ---------------------------------------------------------------------------


class AIEnhancer:
    """
    Wraps the Anthropic API and exposes domain-specific helpers for
    calculator test automation.
    """

    def __init__(self, api_key: str | None = None) -> None:
        self._key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
        self._client = None
        if _ANTHROPIC_AVAILABLE and self._key:
            self._client = anthropic.Anthropic(api_key=self._key)
            logger.info("AI enhancer initialised with Claude (%s).", _MODEL)
        else:
            logger.info("AI enhancer running in stub mode (no API key / package).")

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def generate_test_cases(
        self,
        operation: str,
        count: int = 5,
    ) -> list[TestCase]:
        """
        Return *count* test cases for a described calculator operation.

        Args:
            operation: Natural-language description, e.g. "addition of two integers".
            count:     How many test cases to produce.

        Returns:
            List of :class:`TestCase` objects.
        """
        if not self._client:
            return self._stub_test_cases(operation, count)

        prompt = (
            f"You are a QA engineer writing test data for a calculator app.\n"
            f"Generate exactly {count} test cases for: {operation}.\n\n"
            f"Return ONLY a valid JSON array.  Each element must have:\n"
            f'  "description": short label\n'
            f'  "expression":  "<left> <op> <right>" e.g. "15 + 27"\n'
            f'  "expected":    string result e.g. "42"\n'
            f'  "tags":        array of strings from [smoke, regression, edge_case]\n\n'
            f"No markdown, no explanation – raw JSON only."
        )

        raw = self._chat(prompt)
        return self._parse_test_cases(raw)

    def analyse_failure(
        self,
        test_name: str,
        expression: str,
        expected: str,
        actual: str,
        error_message: str = "",
    ) -> FailureAnalysis:
        """
        Ask Claude why a test failed and how to fix it.
        """
        if not self._client:
            return FailureAnalysis(
                probable_cause="AI analysis unavailable (no API key).",
                suggested_fix="Review the expression manually.",
                confidence="low",
            )

        prompt = (
            f"A calculator UI automation test failed.\n\n"
            f"Test name    : {test_name}\n"
            f"Expression   : {expression}\n"
            f"Expected     : {expected}\n"
            f"Actual output: {actual}\n"
            f"Error message: {error_message or 'none'}\n\n"
            f"Return ONLY a JSON object with keys:\n"
            f'  "probable_cause" (string)\n'
            f'  "suggested_fix"  (string)\n'
            f'  "confidence"     ("high"|"medium"|"low")\n\n'
            f"No markdown, no explanation – raw JSON only."
        )

        raw = self._chat(prompt)
        return self._parse_failure_analysis(raw)

    def generate_edge_cases(self, operation: str) -> list[TestCase]:
        """Generate boundary / edge-case test data for an operation."""
        if not self._client:
            return self._stub_edge_cases(operation)

        prompt = (
            f"Generate 6 edge-case test cases for the calculator operation: {operation}.\n"
            f"Include: zero, very large numbers, negative numbers, decimals, "
            f"divide-by-zero (expected='Cannot divide by zero' or similar), overflow.\n\n"
            f"Return ONLY a JSON array with fields: description, expression, expected, tags.\n"
            f"No markdown."
        )

        raw = self._chat(prompt)
        return self._parse_test_cases(raw)

    def summarise_run(self, stats: dict[str, Any]) -> RunSummary:
        """
        Produce a readable summary of a completed test run.

        Args:
            stats: Dict with keys: total, passed, failed, skipped, duration_s.
        """
        if not self._client:
            passed = stats.get("passed", 0)
            total = stats.get("total", 0)
            return RunSummary(
                headline=f"{passed}/{total} tests passed.",
                details="AI summary unavailable.",
                recommendations=[],
            )

        prompt = (
            f"Summarise this test run for a calculator automation suite:\n"
            f"{json.dumps(stats, indent=2)}\n\n"
            f"Return ONLY a JSON object:\n"
            f'  "headline"        (one sentence)\n'
            f'  "details"         (2-3 sentences)\n'
            f'  "recommendations" (array of actionable strings, max 3)\n\n'
            f"No markdown."
        )

        raw = self._chat(prompt)
        return self._parse_run_summary(raw)

    # ------------------------------------------------------------------
    # Private: API call
    # ------------------------------------------------------------------

    def _chat(self, user_message: str) -> str:
        """Send a single-turn message and return the text response."""
        try:
            msg = self._client.messages.create(
                model=_MODEL,
                max_tokens=_MAX_TOKENS,
                messages=[{"role": "user", "content": user_message}],
            )
            return msg.content[0].text.strip()
        except Exception as exc:  # noqa: BLE001
            logger.error("Anthropic API error: %s", exc)
            return "{}"

    # ------------------------------------------------------------------
    # Private: parsers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_json(raw: str) -> Any:
        """Strip optional markdown fences and parse JSON."""
        cleaned = re.sub(r"```(?:json)?|```", "", raw).strip()
        return json.loads(cleaned)

    def _parse_test_cases(self, raw: str) -> list[TestCase]:
        try:
            data = self._extract_json(raw)
            if isinstance(data, list):
                return [
                    TestCase(
                        description=item.get("description", ""),
                        expression=item.get("expression", ""),
                        expected=str(item.get("expected", "")),
                        tags=item.get("tags", []),
                    )
                    for item in data
                ]
        except Exception as exc:  # noqa: BLE001
            logger.warning("Could not parse AI test cases: %s", exc)
        return []

    def _parse_failure_analysis(self, raw: str) -> FailureAnalysis:
        try:
            data = self._extract_json(raw)
            return FailureAnalysis(
                probable_cause=data.get("probable_cause", "Unknown"),
                suggested_fix=data.get("suggested_fix", "N/A"),
                confidence=data.get("confidence", "low"),
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Could not parse AI failure analysis: %s", exc)
            return FailureAnalysis("Parse error", "Check logs", "low")

    def _parse_run_summary(self, raw: str) -> RunSummary:
        try:
            data = self._extract_json(raw)
            return RunSummary(
                headline=data.get("headline", ""),
                details=data.get("details", ""),
                recommendations=data.get("recommendations", []),
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Could not parse AI run summary: %s", exc)
            return RunSummary("Parse error", "", [])

    # ------------------------------------------------------------------
    # Stubs (no-API-key fallback)
    # ------------------------------------------------------------------

    @staticmethod
    def _stub_test_cases(operation: str, count: int) -> list[TestCase]:
        stubs = [
            TestCase("Simple case", "5 + 3", "8", ["smoke"]),
            TestCase("Larger numbers", "100 + 200", "300", ["regression"]),
            TestCase("Zero operand", "0 + 99", "99", ["edge_case"]),
            TestCase("Negative result", "10 - 20", "-10", ["regression"]),
            TestCase("Equal operands", "7 + 7", "14", ["smoke"]),
        ]
        return stubs[:count]

    @staticmethod
    def _stub_edge_cases(operation: str) -> list[TestCase]:
        return [
            TestCase("Zero", "0 + 0", "0", ["edge_case"]),
            TestCase("Negative", "-5 + 3", "-2", ["edge_case"]),
            TestCase("Large", "999999 + 1", "1000000", ["edge_case"]),
        ]
