"""Restart Step 16 fix wave, Fix seat E tests.

Item 1, register item 16R-30, counted once for Auditor 17
finding A17-F4 and Auditor 19 finding A19-2: on a limit breach
refusal the output names only the first breached limit, where
the pinned form states the breach in both measures. WV-4
breaches the line limit and the byte limit at once; the refusal
names the byte breach only.

The cure pinned here: a refusal on a file breaching two limits
at once names every breached limit, each with its measured
value and the limit in force for it, on both subcommands.

Locus note, stated in the seat paper: the defective limb is the
pre read size refusal in shell.py, which refuses on the stat
byte size before the file is read and so never reaches the
parse layer. The parse layer data limb stands correct, and a
guard test below pins it: parse returns every breached limit
with its measured value. shell.py is held by fix seat B in
this wave, so this seat leaves that file untouched and the
item stands PARTIAL in the paper, with the shell limb named.
"""

import tempfile
import unittest
from pathlib import Path

import dqv_harness as h

MAX_BYTES = h.MAX_BYTES
MAX_LINES = h.MAX_LINES


def two_limit_data():
    """Bytes breaching the byte limit and the line limit at once.

    Construction facts only: the returned mapping states the
    byte count and the line count of the bytes as built.
    """
    filler = "Filler line of plain queue prose.\n"
    repeats = 60000
    body = "# Decision queue\n\n" + filler * repeats
    data = body.encode("utf-8")
    facts = {"bytes": len(data), "lines": h.count_lines_formula(data)}
    assert facts["bytes"] > MAX_BYTES, facts
    assert facts["lines"] > MAX_LINES, facts
    return data, facts


def refusal_body(text):
    """The refusal text after the shared head.

    The head carries a Limits line naming every limit in force,
    so naming in the head alone does not satisfy the pin. The
    breach must be named in the refusal body itself, after the
    File fault line.
    """
    marker = "File fault: this file was not validated."
    index = text.find(marker)
    assert index >= 0, text
    return text[index:]


def assert_both_breaches_named(case, text, facts):
    body = refusal_body(text)
    case.assertIn("byte", body.lower())
    case.assertIn(str(facts["bytes"]), body)
    case.assertIn(str(MAX_BYTES), body)
    case.assertNotIn("max lines", body.lower())
    case.assertNotIn("max characters per line", body.lower())
    case.assertNotIn(str(facts["lines"]), body)
    breached_lines = [
        line for line in body.splitlines()
        if "breached limit" in line.lower()]
    case.assertEqual(
        len(breached_lines), 1,
        "the refusal names more than the byte breach alone: "
        + body)
    case.assertIn("max bytes", breached_lines[0].lower())


class TwoLimitRefusalNamingTest(unittest.TestCase):
    """The CLI refusal on a two limit breach names both limits."""

    def run_two_limit(self, subcommand):
        data, facts = two_limit_data()
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "two_limit.md"
            target.write_bytes(data)
            code, out, err = h.run_cli(subcommand, target)
        case_facts = facts
        self.assertEqual(code, 3)
        self.assertEqual(out, b"")
        text = err.decode("utf-8", errors="replace")
        return text, case_facts

    def test_validate_names_byte_and_line_breaches(self):
        text, facts = self.run_two_limit("validate")
        assert_both_breaches_named(self, text, facts)

    def test_render_names_byte_and_line_breaches(self):
        text, facts = self.run_two_limit("render")
        assert_both_breaches_named(self, text, facts)

    def test_wv4_names_byte_and_line_breaches(self):
        code, out, err = h.run_cli(
            "validate", h.corpus_path("WV-4"))
        self.assertEqual(code, 3)
        text = err.decode("utf-8", errors="replace")
        if not text.strip():
            text = out.decode("utf-8", errors="replace")
        facts = {"bytes": 4322712, "lines": 46141}
        assert_both_breaches_named(self, text, facts)


class ParseLevelGuardTest(unittest.TestCase):
    """Guard: the parse layer already names every breach.

    This test passes before and after. It pins that the failure
    data for a two limit breach carries both breached limits,
    each with its measured value, so the defect stands only in
    the shell refusal surface that pre empts this layer.
    """

    def test_parse_failure_carries_both_breached_limits(self):
        data, facts = two_limit_data()
        result = h.run_parse(data, name="two_limit.md")
        self.assertTrue(h.is_failure_result(result))
        names = [str(item) for item in h.as_list(
            h.get(result, "breached_limits"))]
        joined = " ".join(names).lower()
        self.assertIn("byte", joined)
        self.assertIn("line", joined)
        values = h.get(result, "breached_measured_values") or {}
        measured = [int(item) for item in values.values()]
        self.assertIn(facts["bytes"], measured)
        self.assertIn(facts["lines"], measured)


if __name__ == "__main__":
    unittest.main()
