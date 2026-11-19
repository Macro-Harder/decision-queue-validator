"""Step 17 fix wave 8, Fix Seat K2 tests, test first.

Charge CH-155 (T8-05, seat 18 finding F8-18-1, High), as
ruled at section 77 of design/steps/step-17r-record.md:
a per line cost quadratic in line length on the cured
tree, cost only, no exit or report change anywhere. The
finding paper is design/steps/step-17r-attack8-18.md. Its
measured law: one line costs 0.12 seconds at 4,000
characters, 0.48 at 8,000, and 1.91 at 16,000; at a fixed
500,000 bytes, 4.08 seconds at line length 1,000, 15.22
at 4,000, and 58.66 at 16,000; the byte bound cases went
from 1.64 seconds per subcommand on the round 7 tree to
about 250 seconds.

Locus narrowing, this seat, first hand on the bench: the
whole cost stands in scan_line_occurrences in parse.py
(1.95 of 1.97 seconds of profile tottime on the single
line form, 57.97 of 58.33 on the 500,000 byte form), and
inside it in the one scan that reads the line for a
damaged Status label standing behind other matter: the
finditer of the pattern ([^\\s:]+): over the line. Read
alone on a colon free run of x characters the pattern
costs 0.008 seconds at 1,000 characters, 0.120 at 4,000,
0.466 at 8,000, and 1.864 at 16,000, the finding law to
the digit, because at every position of a whitespace
free, colon free run the engine scans the rest of the
run looking for the colon the run does not carry and
then advances one position and scans again. Every other
per line reading this seat timed on the same line stands
at 0.007 seconds or below at 16,000 characters
(_find_disposition, _guarded_output_spans,
_sentence_spans, _guarded_dq_tokens, escape_text, and
_surrogate_safe among them). The cure stands at that
scan only: the line is read once for its whitespace
separated runs, and a run takes the damaged label reading
only where the character standing immediately after the
run is a colon, which is exactly the set of tokens the
standing pattern matches, at the same positions, under
the same start of line exclusion, with the same two
damage readings (_is_charged_label_damage of CH-111 and
_is_label_interior_damage of CH-128) applied to the same
token text.

The verdict of this file rests on behaviour and on the
governed pins, never on a cost figure alone, under
ruling (f) of section 66 carried at section 77 ruling
(e): the bounded tests assert that the charged readings
complete inside a stated bound and return the behaviour
the line carries, and the pin tests assert the behaviour
of the scan and of the stated limits standing before and
after. Cost figures stand as measurements in the seat
paper only.

Copyright: J.P. Picard aka Macro-Harder
"""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

import dqv_harness as h
from decision_queue_validator import parse as parse_module

_HDR = "# Decision queue\n\n"


def _banked(num, blocks="DQ-999"):
    return ("### DQ-%d: Sample question\n\nStatus: Banked\n\n"
            "This question is waiting for a decision.\n\n"
            "Question: Which option should we take?\n\n"
            "Options: Option A, Option B\n\n"
            "Cost of deciding late: Work stays blocked.\n\n"
            "Blocks: %s\n" % (num, blocks))


def _single_line_file(linelen):
    # The probe9 single line form of the finding paper.
    return _HDR + _banked(1) + "\n" + "x" * linelen + "\n"


def _pad_bytes(total, linelen):
    # The probe9 bytes form of the finding paper: one
    # Banked entry padded with filler lines of one length
    # to an exact byte total.
    base = _HDR + _banked(1) + "\n"
    filler = "x" * linelen + "\n"
    body = base
    while len(body.encode()) + len(filler) <= total:
        body += filler
    rem = total - len(body.encode())
    if rem == 1:
        body += "\n"
    elif rem > 1:
        body += "y" * (rem - 1) + "\n"
    assert len(body.encode()) == total
    return body


def _scan_within_bound(line, bound_seconds=1):
    """The marker scan of one line, taken in a child
    process under a time bound, in the CH-144 test form.
    Returns (completed, near_count): completed is False
    where the scan did not finish inside the bound, the
    behaviour charged at CH-155. The subprocess carries
    its own timeout, as every runner of this seat does."""
    driver = (
        "import sys\n"
        "from decision_queue_validator import parse\n"
        "builder = parse._EntryBuilder(object(), {})\n"
        "builder.scan_line_occurrences(7, sys.argv[1])\n"
        "print(len(builder.near))\n")
    env = dict(os.environ)
    env["PYTHONPATH"] = str(h.PRODUCT_ROOT)
    try:
        proc = subprocess.run(
            [os.sys.executable, "-c", driver, line],
            cwd=str(h.PRODUCT_ROOT), env=env,
            capture_output=True, text=True,
            timeout=bound_seconds)
    except subprocess.TimeoutExpired:
        return False, None
    return True, int(proc.stdout.strip())


class Ch155BoundedCompletionTest(unittest.TestCase):
    """The charged constructions, read inside a bound:
    failing before the cure on the bound, standing after
    it on their behaviour."""

    def test_scan_of_long_colon_free_line_completes(self):
        completed, near = _scan_within_bound("x" * 16000)
        self.assertTrue(completed)
        self.assertEqual(near, 0)

    def test_scan_of_long_run_then_damaged_token_completes(self):
        line = "See " + "x" * 12000 + " Statu5: Banked"
        completed, near = _scan_within_bound(line)
        self.assertTrue(completed)
        self.assertEqual(near, 1)

    def test_bytes_form_500000_long_lines_completes(self):
        # The finding form at a fixed 500,000 bytes with
        # lines of 16,000 characters: 58.66 seconds
        # measured on the precure tree, against a bound
        # of 20 seconds on the command line run.
        text = _pad_bytes(500000, 16000)
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "bytes500k.md"
            target.write_bytes(text.encode("utf-8"))
            try:
                code, out, err = h.run_cli_with_timeout(
                    "validate", target, timeout=20)
            except subprocess.TimeoutExpired:
                self.fail("the validate run did not complete "
                          "inside 20 seconds on the 500,000 "
                          "byte long line construction")
        combined = (out + err).decode("utf-8", errors="replace")
        self.assertEqual(code, 0)
        self.assertIn("DQ-1", combined)


class Ch155BehaviourPinsTest(unittest.TestCase):
    """Behaviour of the charged forms and of the stated
    limits, standing before and after the cure."""

    def test_single_long_line_entry_stands_as_before(self):
        # The standing behaviour of the probe9 form on the
        # precure tree, recorded first hand by this seat:
        # the run completes, and the entry derives Open, the
        # filler paragraph standing as its body. The cure
        # is cost only, so the same standing is asserted
        # after it.
        for linelen in (4000, 8000):
            with self.subTest(linelen=linelen):
                model, output = h.run_pipeline(
                    _single_line_file(linelen).encode("utf-8"))
                self.assertFalse(h.is_failure_result(model))
                self.assertIsNotNone(output)
                entry = h.entry_by_id(output, "DQ-1")
                self.assertEqual(h.entry_state(entry), "Open")

    def test_byte_bound_stands_at_its_bound(self):
        model, output = h.run_pipeline(
            _pad_bytes(2000000, 1000).encode("utf-8"))
        self.assertFalse(h.is_failure_result(model))
        self.assertIsNotNone(output)
        model, output = h.run_pipeline(
            _pad_bytes(2000001, 1000).encode("utf-8"))
        self.assertTrue(h.is_failure_result(model))

    def test_per_line_bound_stands_at_its_bound(self):
        model, output = h.run_pipeline(
            _single_line_file(16384).encode("utf-8"))
        self.assertFalse(h.is_failure_result(model))
        self.assertIsNotNone(output)
        model, output = h.run_pipeline(
            _single_line_file(16385).encode("utf-8"))
        self.assertTrue(h.is_failure_result(model))


def _embedded_body(marker_line):
    # The embedded body form of the fix wave 7 seat K5
    # pins: the entry carries no head Status line and its
    # only marker stands in the closing prose of its first
    # paragraph.
    body = "# Decision queue\n\n"
    body += "### DQ-001: A sample open question\n\n"
    body += "Some closing text. " + marker_line + "\n\n"
    body += "Question: Which option should we take?\n\n"
    body += "Options: Option A, Option B\n\n"
    body += "Cost of deciding late: Work stays blocked.\n\n"
    body += "Blocks: DQ-002\n\n"
    body += "### DQ-002: A second open question\n\n"
    body += "Status: Banked\n\n"
    body += "Second entry is waiting for a decision.\n\n"
    body += "Question: Which path should we take?\n\n"
    body += "Options: Option C, Option D\n\n"
    body += "Cost of deciding late: More work stays blocked.\n\n"
    body += "Blocks: DQ-001\n"
    return body


class Ch155TokenScanPinsTest(unittest.TestCase):
    """The governed pins of the scan the cure rewrites:
    the CH-111 and CH-128 embedded damaged label readings,
    standing before and after in their pipeline form, and
    the scan level bounds of the same reading."""

    def _assert_embedded_near_marker(self, marker_line, name):
        _model, output = h.run_pipeline(
            _embedded_body(marker_line).encode("utf-8"), name)
        self.assertIsNotNone(output)
        entry = h.entry_by_id(output, "DQ-001")
        self.assertEqual(h.entry_state(entry), "Ambiguous")
        self.assertEqual(h.entry_sub_label(entry), "No element")
        self.assertEqual(
            len(h.findings_for(output, entry_id="DQ-001", rule=2)),
            1)
        recon = h.reconciliation_of(output)
        self.assertEqual(h.int_of(h.get(
            recon, "status_occurrence_total", "occurrence_total")), 1)

    def test_embedded_charged_digit_form_still_warns(self):
        self._assert_embedded_near_marker(
            "Statu5: Banked", "k2_embedded_digit.md")

    def test_embedded_interior_dot_form_still_warns(self):
        self._assert_embedded_near_marker(
            "Stat.us: Banked", "k2_embedded_dot.md")

    def test_embedded_interior_letter_form_still_warns(self):
        self._assert_embedded_near_marker(
            "St\u0430tus: Banked", "k2_embedded_cyrillic.md")

    def test_scan_level_token_bounds(self):
        cases = (
            # A damaged token behind other matter warns.
            ("See Statu5: now", 1),
            # Two damaged tokens on one line warn twice.
            ("See Statu5: and St4tus: now", 2),
            # A damaged token standing after a colon on the
            # same line still warns.
            ("See a: Statu5: now", 1),
            # No colon after the token: no reading stands.
            ("See Statu5 now", 0),
            # A plain long token before a colon is no label.
            ("See " + "x" * 300 + ": now", 0),
            # A colon free long line carries no token.
            ("x" * 300, 0),
        )
        for line, expected in cases:
            with self.subTest(line=line[:24]):
                builder = parse_module._EntryBuilder(object(), {})
                builder.scan_line_occurrences(7, line)
                self.assertEqual(len(builder.near), expected)


if __name__ == "__main__":
    unittest.main()
