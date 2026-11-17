"""Restart Step 16 fix wave 2, Fix seat G tests.

Seat G owns product/README.md. Each test pins one charged README
correction from Auditor 7 of confirmation round 2
(design/steps/step-16r-audit2-7.md), written before the cure, in
the form of Fix seat C's test file
(product/tests/test_restart_step16_fix_c.py):

Row 6 (Low; Auditor 7 Finding 3): the five head lines statement.
The README statement that every output opens with the same five
head lines is broken for exit 2 usage error outputs, which open
with a Call fault line and carry no head lines. The statement is
corrected to its true scope.

Row 7 (the README limb of Auditor 7's Medium, Finding 1): the
file facts line account. The cured designation sentence holds on
completed runs but overclaims on refusal surfaces, which print
File: absent on files the tool read (empty, header only, no
structure, invalid bytes), with the byte limit refusal printing
a byte count only and the invalid bytes refusal printing no
line count. The README account is restated to name the refusal
form as it stands.

Row 27 (Low; Auditor 7 Finding 4): the untranslatable causer
bullet. The bullet's stated exit 4 consequence fails on fixture
WV-9, whose entries carry only untranslatable phrasings, are
held as unknown in the residue list, derive Open under the
designed Shape A exception, and exit 0. The bullet is restated
to state the designed exception truly.

Second holder completion (recovery): the first holder's file
stood landed with the three classes above and all 21 of its
tests passing on the bench. Ruling the landed state first hand
found one gap the landed tests did not pin: the cured refusal
sentence spoke of every refusal output, but two refusal
outputs are decided after the file has been read and parsed,
the gap naming size refusal on either subcommand and the
supersession map size refusal on a render run, and their file
facts line prints in full with the designation live. The
PostParseRefusalFactsTest class below pins that form, written
before the README completion that names it.
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import dqv_harness as h

README_PATH = h.PRODUCT_ROOT / "README.md"


def readme_text():
    return README_PATH.read_text(encoding="utf-8")


def readme_flat():
    """The README text with all whitespace runs collapsed to one
    space, so a phrase stands or falls as written, wherever the
    printed lines wrap."""
    return " ".join(readme_text().split())


def run_file(subcommand, data, name="queue.md"):
    path = h.temp_input(data, name)
    try:
        code, out, err = h.run_cli(subcommand, path)
    finally:
        Path(path).unlink(missing_ok=True)
    return (code, out.decode("utf-8", errors="replace"),
            err.decode("utf-8", errors="replace"))


def run_argv(argv):
    proc = subprocess.run(
        [sys.executable, "-m", h.PACKAGE] + argv,
        cwd=str(h.PRODUCT_ROOT), env=h.cli_env(h.SEED_ONE),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return (proc.returncode,
            proc.stdout.decode("utf-8", errors="replace"),
            proc.stderr.decode("utf-8", errors="replace"))


def facts_line(output):
    for line in output.splitlines():
        if line.startswith("File:"):
            return line
    raise AssertionError("no File line in output: " + output)


PARAGRAPH_ONLY = (
    "# Decision queue\n\n"
    "### DQ-001: A sample open question\n\n"
    "Status: Banked\n\n"
    "A plain note about this question.\n")


class HeadLinesScopeTest(unittest.TestCase):
    """Row 6: usage error outputs open with a Call fault line
    and carry no head lines; the other outputs open with the
    five head lines."""

    def test_usage_error_opens_with_call_fault_and_no_head_lines(self):
        code, out, err = run_argv([])
        self.assertEqual(code, 2)
        lines = [ln for ln in err.splitlines() if ln]
        self.assertTrue(lines[0].startswith("Call fault:"), lines[0])
        self.assertNotIn("Checked:", err)
        self.assertNotIn("File:", err)
        self.assertNotIn("Limits:", err)
        self.assertNotIn("Versions:", err)

    def test_unknown_subcommand_is_also_a_call_fault_opening(self):
        code, out, err = run_argv(["bogus", "queue.md"])
        self.assertEqual(code, 2)
        lines = [ln for ln in err.splitlines() if ln]
        self.assertTrue(lines[0].startswith("Call fault:"), lines[0])
        self.assertNotIn("Checked:", err)

    def test_completed_output_opens_with_the_five_head_lines(self):
        code, out, err = run_file(
            "validate", PARAGRAPH_ONLY.encode("utf-8"))
        self.assertEqual(code, 1)
        lines = out.splitlines()
        self.assertTrue(lines[0].startswith("Checked:"), lines[0])
        self.assertTrue(lines[1].startswith("Input:"), lines[1])
        self.assertTrue(lines[2].startswith("File:"), lines[2])
        self.assertTrue(lines[3].startswith("Limits:"), lines[3])
        self.assertTrue(lines[4].startswith("Versions:"), lines[4])

    def test_refusal_output_carries_the_head_lines(self):
        code, out, err = run_file("validate", b"", "empty.md")
        self.assertEqual(code, 3)
        lines = err.splitlines()
        self.assertTrue(lines[0].startswith("Checked:"), lines[0])
        self.assertTrue(lines[2].startswith("File:"), lines[2])

    def test_input_not_read_output_carries_the_head_lines(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "missing.md"
            code, out, err = h.run_cli("validate", missing)
        err = err.decode("utf-8", errors="replace")
        self.assertEqual(code, 2)
        lines = err.splitlines()
        self.assertTrue(lines[0].startswith("Checked:"), lines[0])
        self.assertTrue(lines[2].startswith("File:"), lines[2])

    def test_readme_scopes_the_head_lines_statement(self):
        text = readme_flat()
        self.assertNotIn(
            "Every output opens with the same five head lines",
            text)
        self.assertIn(
            "Every output except a usage error output opens "
            "with the same five head lines", text)
        self.assertIn(
            "opens with a Call fault line instead and carries "
            "no head lines", text)


class RefusalFactsLineTest(unittest.TestCase):
    """Row 7: on refusal surfaces the file facts line prints
    the designation absent, in full on most refusal forms, in
    reduced form on the byte limit and invalid bytes forms,
    and alone where the input could not be read."""

    def test_completed_run_facts_line_reads_live_in_full(self):
        code, out, err = run_file(
            "validate", PARAGRAPH_ONLY.encode("utf-8"))
        line = facts_line(out)
        self.assertTrue(line.startswith("File: live, "), line)
        self.assertIn("lines", line)
        self.assertIn("bytes", line)
        self.assertIn("digest", line)

    def test_empty_file_refusal_reads_absent_in_full(self):
        code, out, err = run_file("validate", b"", "empty.md")
        self.assertEqual(code, 3)
        line = facts_line(err)
        self.assertTrue(line.startswith("File: absent, "), line)
        self.assertIn("0 lines", line)
        self.assertIn("0 bytes", line)
        self.assertIn("digest", line)

    def test_header_only_refusal_reads_absent_in_full(self):
        code, out, err = run_file(
            "validate", b"# Decision queue\n", "header.md")
        self.assertEqual(code, 3)
        line = facts_line(err)
        self.assertTrue(line.startswith("File: absent, "), line)
        self.assertIn("lines", line)
        self.assertIn("bytes", line)
        self.assertIn("digest", line)

    def test_no_structure_refusal_reads_absent_in_full(self):
        code, out, err = run_file(
            "validate", b"Just some prose.\nMore prose.\n")
        self.assertEqual(code, 3)
        line = facts_line(err)
        self.assertTrue(line.startswith("File: absent, "), line)
        self.assertIn("lines", line)
        self.assertIn("bytes", line)
        self.assertIn("digest", line)

    def test_line_limit_refusal_reads_absent_in_full(self):
        data, facts = h.limit_lines_input()
        code, out, err = run_file("validate", data)
        self.assertEqual(code, 3)
        line = facts_line(err)
        self.assertTrue(line.startswith("File: absent, "), line)
        self.assertIn("lines", line)
        self.assertIn("bytes", line)
        self.assertIn("digest", line)

    def test_invalid_bytes_refusal_prints_no_line_count(self):
        data = b"# Decision queue\n\n\xff\xfe invalid \x80 bytes\n"
        code, out, err = run_file("validate", data)
        self.assertEqual(code, 3)
        line = facts_line(err)
        self.assertTrue(line.startswith("File: absent, "), line)
        self.assertIn("bytes", line)
        self.assertIn("digest", line)
        self.assertNotIn("lines", line)

    def test_byte_limit_refusal_prints_byte_count_only(self):
        data, facts = h.limit_bytes_input()
        code, out, err = run_file("validate", data)
        self.assertEqual(code, 3)
        line = facts_line(err)
        self.assertEqual(
            line, "File: absent, %d bytes" % len(data), line)
        self.assertNotIn("lines", line)
        self.assertNotIn("digest", line)

    def test_input_not_read_facts_line_is_absent_alone(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "missing.md"
            code, out, err = h.run_cli("validate", missing)
        err = err.decode("utf-8", errors="replace")
        self.assertEqual(code, 2)
        self.assertEqual(facts_line(err), "File: absent")

    def test_readme_names_the_refusal_facts_form(self):
        text = readme_flat()
        self.assertIn("the designation reads absent, not live",
                      text)
        self.assertIn(
            "still print the line count, the byte count, and "
            "the digest beside absent", text)

    def test_readme_names_the_two_reduced_refusal_forms(self):
        text = readme_flat()
        self.assertIn(
            "a file refused for invalid bytes prints the byte "
            "count and the digest but no line count", text)
        self.assertIn(
            "a file refused on the byte limit prints the byte "
            "count only, with no line count and no digest", text)
        self.assertIn(
            "the file facts line prints absent alone, with no "
            "counts and no digest", text)


class UntranslatableExceptionTest(unittest.TestCase):
    """Row 27: fixture WV-9, whose entries carry only
    untranslatable phrasings, is held as unknown in the residue
    list, derives Open under the Shape A exception, and exits
    0. The causer bullet states that exception."""

    def test_wv9_exits_zero(self):
        code, out, err = h.run_cli(
            "validate", h.corpus_path("WV-9"))
        self.assertEqual(code, 0)

    def test_wv9_entries_derive_open(self):
        code, out, err = h.run_cli(
            "validate", h.corpus_path("WV-9"))
        out = out.decode("utf-8", errors="replace")
        self.assertEqual(out.count("State: Open"), 3, out)
        self.assertIn("Canonical state: Open: 3 entries", out)

    def test_wv9_phrasings_held_as_unknown_in_residue(self):
        code, out, err = h.run_cli(
            "validate", h.corpus_path("WV-9"))
        out = out.decode("utf-8", errors="replace")
        self.assertIn(
            "Unclassified phrasings, held as unknown:", out)
        self.assertIn(
            "Flummoxed pending the autumn audit", out)
        self.assertIn("Widdershins until the tide turns", out)
        self.assertIn("Pending the purple moon review", out)

    def test_readme_bullet_states_the_shape_a_exception(self):
        text = readme_flat()
        self.assertIn(
            "derives Open under the Shape A exception", text)
        self.assertIn("the entry's only status element", text)
        self.assertIn("carries no decision evidence", text)
        self.assertIn("does not exit 4 on that ground", text)

    def test_readme_bullet_names_the_wv9_outcome(self):
        text = readme_flat()
        self.assertIn("WV-9", text)
        self.assertIn(
            "A file whose entries all take that exception",
            text)


GAP_INPUT = (
    "# Decision queue\n\n"
    "### DQ-1: Entry 1\n\n"
    "Status: Banked\n\n"
    "A plain note.\n\n"
    "### DQ-400000: Entry 400000\n\n"
    "Status: Banked\n\n"
    "A plain note.\n")


class PostParseRefusalFactsTest(unittest.TestCase):
    """Row 7, second holder completion: the gap naming size
    refusal fires on either subcommand after the file has been
    read and parsed, and its file facts line prints in full
    with the designation live. The README account scopes the
    absent form to the refusals of a file the tool could not
    take in as a queue and names the post parse refusal form."""

    def test_gap_refusal_facts_line_reads_live_in_full_validate(self):
        code, out, err = run_file(
            "validate", GAP_INPUT.encode("utf-8"))
        self.assertEqual(code, 3)
        line = facts_line(err)
        self.assertTrue(line.startswith("File: live, "), line)
        self.assertIn("lines", line)
        self.assertIn("bytes", line)
        self.assertIn("digest", line)

    def test_gap_refusal_facts_line_reads_live_in_full_render(self):
        code, out, err = run_file(
            "render", GAP_INPUT.encode("utf-8"))
        self.assertEqual(code, 3)
        line = facts_line(err)
        self.assertTrue(line.startswith("File: live, "), line)
        self.assertIn("lines", line)
        self.assertIn("bytes", line)
        self.assertIn("digest", line)

    def test_readme_scopes_the_absent_form(self):
        text = readme_flat()
        self.assertNotIn(
            "On a refusal output the file facts line takes a "
            "reduced form and the designation reads absent",
            text)
        self.assertIn(
            "On a refusal output for a file the tool could not "
            "take in as a queue, the file facts line takes a "
            "reduced form and the designation reads absent, "
            "not live", text)

    def test_readme_names_the_post_parse_refusal_form(self):
        text = readme_flat()
        self.assertIn("the gap naming size refusal", text)
        self.assertIn("the supersession map size refusal", text)
        self.assertIn(
            "are decided after the file has been read and "
            "parsed", text)
        self.assertIn(
            "their file facts line prints in full, with the "
            "designation live", text)


if __name__ == "__main__":
    unittest.main()
