"""Restart Step 17 fix wave 1, seat C8 tests.

Seat C8 owns the resource limits cluster. This file pins
charge two only, written before the cure:

A21-2 (High): one very long DQ number stalls the run on the
gap naming size computation. The computation stands in both
validate.py _gap_naming_size and shell.py _gap_naming_size.
The refusal answer is correct in every completed run and no
limit value changes; the charge is the cost of reaching the
answer only, for a heading line inside the per line limit of
16,384 characters. The cost is pinned by a stated timing
bound of 5 seconds for a 16,000 digit number, the seat 21
paper construction, which the uncured computation does not
meet (killed by a 30 second timeout in the paper runs).

Correctness is pinned two ways. Small and medium number sets
are checked against a brute force enumeration of the missing
values, which passes before and after the cure. The long
number case is checked against a closed form sum, itself
checked against the brute force enumeration at small digit
counts in this file.
"""

import sys
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace

import dqv_harness as h

validate = h.import_module("validate")
shell = h.import_module("shell")

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(20000)

DIGITS = 16000
COST_BOUND_SECONDS = 5.0


def brute_gap_naming_size(numbers):
    """The gap naming size by direct enumeration: the decimal
    digits of each missing value plus one separator character
    for each value after the first."""
    values = sorted(set(numbers))
    if len(values) < 2:
        return 0
    present = set(values)
    missing = [number for number in range(values[0] + 1, values[-1])
               if number not in present]
    if not missing:
        return 0
    return sum(len(str(number)) for number in missing) + \
        (len(missing) - 1)


def closed_form_all_nines(digit_count):
    """The gap naming size for the present set {1, 10**D - 1},
    by the closed form for the sum of digit lengths.

    The sum of the digit lengths of 1 to 10**D - 1 is
    9 * T, where T = sum_{k=1}^{D} k * 10**(k - 1) stands in
    closed form as (1 - (D + 1) * 10**D + D * 10**(D + 1))
    divided by 81. The missing set is 2 to 10**D - 2, so the
    digit lengths of the two present values (1 and 10**D - 1)
    come off that sum, and the separator count is the missing
    count less one.
    """
    total = 9 * ((1 - (digit_count + 1) * 10 ** digit_count
                  + digit_count * 10 ** (digit_count + 1)) // 81)
    digit_total = total - 1 - digit_count
    missing_total = 10 ** digit_count - 3
    return digit_total + (missing_total - 1)


def shell_output_for(numbers):
    entries = [SimpleNamespace(identifier="DQ-%d" % number)
               for number in numbers]
    return SimpleNamespace(entries=entries)


class GapNamingSizeCorrectnessGuardTest(unittest.TestCase):
    """The size values themselves must not move under the
    cure. These cases pass before and after it."""

    CASES = (
        [3, 25],
        [1, 2],
        [5, 5, 9],
        [1, 1000],
        [10, 99, 100, 10000],
        [7],
        [4, 5, 6],
        [2, 3, 100000],
    )

    def test_validate_size_matches_brute_force(self):
        for numbers in self.CASES:
            with self.subTest(numbers=numbers):
                self.assertEqual(
                    validate._gap_naming_size(numbers),
                    brute_gap_naming_size(numbers))

    def test_shell_size_matches_brute_force(self):
        for numbers in self.CASES:
            with self.subTest(numbers=numbers):
                self.assertEqual(
                    shell._gap_naming_size(
                        shell_output_for(numbers)),
                    brute_gap_naming_size(numbers))

    def test_closed_form_matches_brute_force_at_small_counts(self):
        for digit_count in (1, 2, 3):
            with self.subTest(digit_count=digit_count):
                numbers = [1, 10 ** digit_count - 1]
                self.assertEqual(
                    closed_form_all_nines(digit_count),
                    brute_gap_naming_size(numbers))


class GapNamingSizeLongNumberCostTest(unittest.TestCase):
    """A21-2: the cost of the computation for a very long DQ
    number, in each of the two copies the charge names."""

    def test_validate_copy_cost_and_value_at_16000_digits(self):
        high = 10 ** DIGITS - 1
        start = time.perf_counter()
        size = validate._gap_naming_size([1, high])
        elapsed = time.perf_counter() - start
        self.assertLess(
            elapsed, COST_BOUND_SECONDS,
            "the validate gap naming computation took %.2f "
            "seconds for a %d digit number, over the stated "
            "bound of %.1f seconds" % (elapsed, DIGITS,
                                       COST_BOUND_SECONDS))
        self.assertEqual(size, closed_form_all_nines(DIGITS))
        self.assertGreater(size, 2000000)

    def test_shell_copy_cost_and_value_at_16000_digits(self):
        entries = [
            SimpleNamespace(identifier="DQ-001"),
            SimpleNamespace(identifier="DQ-" + "9" * DIGITS),
        ]
        output = SimpleNamespace(entries=entries)
        start = time.perf_counter()
        size = shell._gap_naming_size(output)
        elapsed = time.perf_counter() - start
        self.assertLess(
            elapsed, COST_BOUND_SECONDS,
            "the shell gap naming computation took %.2f "
            "seconds for a %d digit number, over the stated "
            "bound of %.1f seconds" % (elapsed, DIGITS,
                                       COST_BOUND_SECONDS))
        self.assertEqual(size, closed_form_all_nines(DIGITS))
        self.assertGreater(size, 2000000)


class GapNamingLongNumberCliTest(unittest.TestCase):
    """A21-2 at the run surface, in the seat 21 paper
    construction: a queue header, DQ-001, and a second entry
    whose heading number is the digit 9 repeated 16,000 times.
    The run takes the gap naming size refusal at exit 3, and
    reaching it must fit inside the run timeout."""

    def test_long_number_run_refuses_within_the_timeout(self):
        text = (
            "# Decision queue\n\n"
            "### DQ-001: A\n\n"
            "Status: Banked\n\n"
            "Prose paragraph.\n\n"
            "### DQ-" + "9" * DIGITS + ": B\n\n"
            "Status: Banked\n\n"
            "Prose paragraph.\n")
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "huge.md"
            target.write_bytes(text.encode("utf-8"))
            start = time.perf_counter()
            code, out, err = h.run_cli_with_timeout(
                "validate", target, timeout=30)
            elapsed = time.perf_counter() - start
        self.assertEqual(code, 3)
        combined = (out + err).decode("utf-8", errors="replace")
        self.assertIn("Gap naming size limit", combined)
        self.assertNotIn("Traceback", combined)
        self.assertLess(elapsed, 30.0)


if __name__ == "__main__":
    unittest.main()
