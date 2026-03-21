"""
run_smoke.py
------------
Standalone script to execute smoke tests and print a quick pass/fail
summary without needing to remember pytest flags.

Usage:
    python run_smoke.py                     # run smoke suite
    python run_smoke.py --serve             # run + open Allure in browser
    python run_smoke.py --suite regression  # run a different marker
"""

import argparse
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Calculator Automation runner")
    parser.add_argument(
        "--suite",
        default="smoke",
        choices=["smoke", "regression", "scientific", "ai_generated", "edge_case", "all"],
        help="Which marker suite to run (default: smoke)",
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Open Allure report in browser after run",
    )
    parser.add_argument(
        "--results-dir",
        default="allure-results",
        help="Directory to store Allure raw results",
    )
    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    results_dir.mkdir(exist_ok=True)

    # ── Build pytest command ─────────────────────────────────────────────────
    cmd = [
        sys.executable, "-m", "pytest", "tests/",
        f"--alluredir={results_dir}",
        "-v", "--tb=short",
    ]

    if args.suite != "all":
        cmd += ["-m", args.suite]

    print(f"\n{'─'*60}")
    print(f"  Suite  : {args.suite}")
    print(f"  Results: {results_dir}")
    print(f"{'─'*60}\n")

    # ── Run tests ────────────────────────────────────────────────────────────
    result = subprocess.run(cmd)

    # ── Optional: serve Allure ───────────────────────────────────────────────
    if args.serve:
        subprocess.run(["allure", "serve", str(results_dir)])

    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
