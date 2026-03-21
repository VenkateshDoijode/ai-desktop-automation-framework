"""
test_data.py
------------
Static parametrized test data sets for use with @pytest.mark.parametrize.

Keeps test functions clean — all data lives here and can be imported
by any test module.
"""

# ── Addition ─────────────────────────────────────────────────────────────────
ADDITION_DATA = [
    # (left, right, expected, description)
    (0,       0,         "0",           "zero plus zero"),
    (1,       1,         "2",           "one plus one"),
    (10,      90,        "100",         "tens summing to hundred"),
    (999,     1,         "1,000",       "crossing the thousand boundary"),
    (-5,      5,         "0",           "negative cancels positive"),
    (-10,     -20,       "-30",         "both operands negative"),
    (1234,    5678,      "6,912",       "four-digit addition"),
    (0,       1000000,   "1,000,000",   "zero plus million"),
]

# ── Subtraction ───────────────────────────────────────────────────────────────
SUBTRACTION_DATA = [
    (10,  3,    "7",    "basic positive subtraction"),
    (0,   0,    "0",    "zero minus zero"),
    (5,   10,   "-5",   "result is negative"),
    (100, 100,  "0",    "equal operands give zero"),
    (-5,  -3,   "-2",   "negative minus negative"),
    (1000, 1,   "999",  "crossing a round number"),
]

# ── Multiplication ────────────────────────────────────────────────────────────
MULTIPLICATION_DATA = [
    (0,    5,    "0",      "anything times zero"),
    (1,    99,   "99",     "identity element"),
    (6,    7,    "42",     "classic six times seven"),
    (-3,   4,    "-12",    "negative times positive"),
    (-3,   -4,   "12",     "negative times negative"),
    (12,   12,   "144",    "square of twelve"),
    (100,  100,  "10,000", "two hundreds"),
]

# ── Division ──────────────────────────────────────────────────────────────────
DIVISION_DATA = [
    (10,   2,    "5",       "even division"),
    (0,    5,    "0",       "zero dividend"),
    (1,    4,    "0.25",    "quarter"),
    (9,    3,    "3",       "perfect thirds"),
    (100,  10,   "10",      "round quotient"),
    (-10,  2,    "-5",      "negative dividend"),
]

# ── Edge cases ────────────────────────────────────────────────────────────────
EDGE_CASE_EXPRESSIONS = [
    # expression, expected_fragment, description
    ("5 / 0",    "Cannot divide by zero",  "division by zero"),
    ("0 / 0",    "Result is undefined",    "zero over zero"),
    ("9999999 + 1", "10,000,000",          "large number addition"),
]
