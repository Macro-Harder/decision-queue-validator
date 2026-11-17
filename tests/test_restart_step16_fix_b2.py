"""Restart Step 16 fix wave, Fix seat B second holder tests.

Register item 16R-30: the shell pre read stat refusal must name
every breached limit with its measured value and its limit in
force, in the form the parse layer uses.

Seat E pin in test_restart_step16_fix_e.py covers the byte and
line co-breach. This file adds the two cases that pin does not
cover: a byte and per line co-breach met at the shell refusal,
and a byte only breach, where the refusal must name the byte
limit alone and invent no other breach.
"""

import tempfile
import unittest
from pathlib import Path

import dqv_harness as h

MAX_BYTES = h.MAX_BYTES
MAX_LINES = h.MAX_LINES
MAX_CHARS = h.MAX_CHARS_PER_LINE


def refusal_body(text):
    marker = "File fault: this file was not validated."
    index = text.find(marker)
    assert index >= 0, text
    return text[index:]


def breached_lines(body):
    return [
        line for line in body.splitlines()
        if "breached limit" in line.lower()]


def run_refusal(case, data):
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "input.md"
        target.write_bytes(data)
        code, out, err = h.run_cli("validate", target)
    case.assertEqual(code, 3)
    case.assertEqual(out, b"")
    return refusal_body(err.decode("utf-8", errors="replace"))


class ByteAndPerLineShellRefusalTest(unittest.TestCase):

    def test_byte_and_per_line_breaches_both_named(self):
        data = b"x" * 2000052 + b"\n"
        body = run_refusal(self, data)
        self.assertIn(
            "Breached limit: max bytes, measured value 2000053.",
            body)
        self.assertIn(str(MAX_BYTES), body)
        self.assertIn(
            "Breached limit: max characters per line, "
            "measured value 2000052.", body)
        self.assertIn(str(MAX_CHARS), body)
        self.assertGreaterEqual(len(breached_lines(body)), 2)


class ByteOnlyShellRefusalTest(unittest.TestCase):

    def test_byte_only_breach_names_no_other_limit(self):
        line = "x" * 1000 + "\n"
        data = ("# Decision queue\n\n" + line * 2100).encode("utf-8")
        assert len(data) > MAX_BYTES
        assert h.count_lines_formula(data) <= MAX_LINES
        body = run_refusal(self, data)
        lines = breached_lines(body)
        self.assertEqual(len(lines), 1, body)
        self.assertIn("max bytes", lines[0])
        self.assertIn(str(len(data)), lines[0])
        self.assertIn(str(MAX_BYTES), lines[0])


if __name__ == "__main__":
    unittest.main()
