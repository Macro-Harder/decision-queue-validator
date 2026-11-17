"""Restart Step 16 fix wave, Fix seat C tests.

Seat C owns product/README.md. Each test pins one charged README
cure, written before the cure, in the Step 16 record at
design/steps/step-16r-record.md section 6:

F2 promise correction (Auditor 4 ruling b): the file facts line
states the designation the run carries. On every readable file
that designation reads live in this version, on a pinned copy as
on the live file itself, and the digest on the same line is what
identifies the bytes the run actually read.

F1 interim honesty (Auditor 3 section 5): the README states the
three Banked head evidence groups and their precedence, that
labelled field paragraphs count toward none of them, the self
check outcome for a Banked entry whose body carries none of the
three counted elements, and a worked example in a passing form
that does not teach a false reason for passing.

F18-2 (Auditor 18): the fault recovery teaching gives a workable
form: what to record, and how the entry forms that pass are
shaped, for a user whose run takes the self check outcome.

F18-3, F18-4, F18-5 (Auditor 18): the install instruction in an
executable copy and run form with the working directory stated,
the example to file step stated, and the Python version
statement operationalised.

The two closing lines statement (Auditor 3 row 8 and Auditor 15
Finding 2, counted once): refusal and usage outputs carry one
closing line, not two.

A20-1 (Auditor 20 Finding 1): a report must not be redirected
onto the input file own path; the shell empties the target
before the tool runs.

F18-6 README limb (Auditor 18): the tests tree in the shipped
repo explained in one short passage.
"""

import hashlib
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


MINIMAL = (
    "# Decision queue\n\n"
    "### DQ-001: A sample open question\n\n"
    "Status: Banked\n")

LABELLED_ONLY = MINIMAL + (
    "\nQuestion: Which option should we take?\n\n"
    "Options: Option A, Option B\n\n"
    "Cost of deciding late: Work stays blocked.\n\n"
    "Blocks: DQ-002\n")

LABELLED_AND_PARAGRAPH = LABELLED_ONLY + (
    "\nA plain note about this question.\n")

PARAGRAPH_ONLY = MINIMAL + (
    "\nA plain note about this question.\n")

LATER_STATUS = MINIMAL + "\nStatus: Open\n"

DECISION_BLOCK = MINIMAL + (
    "\n#### Decision\n\nDecided: Option A.\n")


def facts_line(output):
    for line in output.splitlines():
        if line.startswith("File:"):
            return line
    raise AssertionError("no File line in output: " + output)


def readme_example_block():
    text = readme_text()
    marker = "A minimal example of a queue file in those forms:"
    start = text.find(marker)
    if start < 0:
        raise AssertionError("the worked example intro is missing")
    fence_open = text.find("```", start)
    fence_close = text.find("```", fence_open + 3)
    if fence_open < 0 or fence_close < 0:
        raise AssertionError("the worked example block is missing")
    return text[fence_open + 3:fence_close].strip("\n") + "\n"


class F2DesignationTest(unittest.TestCase):
    """F2: the designation reads live on every readable file,
    and the README says so without claiming it tells a live
    file from a pinned copy."""

    def test_copy_named_as_pinned_reads_live_with_its_digest(self):
        data = PARAGRAPH_ONLY.encode("utf-8")
        digest = hashlib.sha256(data).hexdigest()[:12]
        code, out, err = run_file("validate", data,
                                  "pinned-copy-of-live.md")
        self.assertEqual(code, 1)
        line = facts_line(out)
        self.assertTrue(line.startswith("File: live, "), line)
        self.assertIn("digest " + digest, line)

    def test_render_on_a_backup_copy_reads_live(self):
        data = PARAGRAPH_ONLY.encode("utf-8")
        code, out, err = run_file("render", data,
                                  "backup-2026-11-13-QUEUE.md")
        self.assertEqual(code, 1)
        self.assertTrue(
            facts_line(out).startswith("File: live, "),
            facts_line(out))

    def test_readme_states_the_designation_as_it_behaves(self):
        text = readme_flat()
        self.assertNotIn(
            "whether the file is the live file or a pinned copy",
            text)
        self.assertIn(
            "In this version the designation reads live on every "
            "readable file", text)
        self.assertIn(
            "does not tell you whether the file you ran is the "
            "live file or a copy of it", text)
        self.assertIn(
            "The digest on the same line identifies the bytes "
            "the run actually read", text)


class F1BankedEvidenceGroupsTest(unittest.TestCase):
    """F1 designed behaviour: a Banked head entry whose body
    carries none of the three counted elements takes the self
    check failure outcome, with the whole report withheld."""

    def test_status_line_only_banked_entry_takes_tool_fault(self):
        code, out, err = run_file("validate",
                                  MINIMAL.encode("utf-8"))
        self.assertEqual(code, 4)
        self.assertIn("Tool fault: the tool own counts do not "
                      "sum", out)
        self.assertIn("The summary is withheld in full.", out)
        self.assertIn("Banked head evidence groups sum to 0 "
                      "against a Banked head population of 1",
                      out)

    def test_labelled_fields_only_still_takes_tool_fault(self):
        code, out, err = run_file("validate",
                                  LABELLED_ONLY.encode("utf-8"))
        self.assertEqual(code, 4)
        self.assertIn("Tool fault: the tool own counts do not "
                      "sum", out)

    def test_unheaded_paragraph_is_a_counted_element(self):
        code, out, err = run_file("validate",
                                  PARAGRAPH_ONLY.encode("utf-8"))
        self.assertEqual(code, 1)
        self.assertIn("Banked head evidence group: unheaded "
                      "paragraphs only", out)
        self.assertIn("Warning", out)

    def test_labelled_fields_with_counted_element_clear(self):
        code, out, err = run_file(
            "validate", LABELLED_AND_PARAGRAPH.encode("utf-8"))
        self.assertEqual(code, 0)

    def test_later_status_line_is_a_counted_element(self):
        code, out, err = run_file("validate",
                                  LATER_STATUS.encode("utf-8"))
        self.assertNotIn("Tool fault", out)
        self.assertIn("Banked head evidence group: later Status "
                      "line in the body", out)

    def test_decision_block_is_a_counted_element(self):
        code, out, err = run_file("validate",
                                  DECISION_BLOCK.encode("utf-8"))
        self.assertNotIn("Tool fault", out)
        self.assertIn("Banked head evidence group: level 4 "
                      "decision block only", out)

    def test_readme_states_the_five_honesty_points(self):
        text = readme_flat()
        self.assertIn(
            "counted in the census in exactly three evidence "
            "groups", text)
        self.assertIn(
            "a later Status line in the body", text)
        self.assertIn("a level 4 decision block", text)
        self.assertIn("unheaded paragraphs in the body", text)
        self.assertIn(
            "Labelled field paragraphs count toward none of "
            "the three groups", text)
        self.assertIn(
            "is counted in no group", text)
        self.assertIn(
            "the evidence groups fail to foot to the Banked "
            "head population", text)
        self.assertIn(
            "the run is withheld in full as a tool "
            "inconsistency at exit 4", text)
        self.assertIn(
            "no findings are reported for any entry in the "
            "file", text)
        self.assertIn(
            "a Banked entry must carry at least one of the "
            "three counted elements", text)


class F1WorkedExampleTest(unittest.TestCase):
    """F1 and F18-4: the worked example, saved to a file as the
    README states, runs in a passing form, and the README says
    why the counted element in it is there."""

    def test_readme_example_as_written_completes(self):
        example = readme_example_block()
        code, out, err = run_file("validate",
                                  example.encode("utf-8"),
                                  "QUEUE.md")
        self.assertEqual(code, 1, out)
        self.assertNotIn("Tool fault", out)
        self.assertIn("DQ-001", out)

    def test_readme_example_reports_the_promised_warnings(self):
        text = readme_flat()
        self.assertIn(
            "reports Warning findings for DQ-001", text)
        example = readme_example_block()
        code, out, err = run_file("validate",
                                  example.encode("utf-8"),
                                  "QUEUE.md")
        self.assertIn("Warning", out)

    def test_readme_says_why_the_example_paragraph_is_there(self):
        text = readme_flat()
        self.assertIn(
            "The plain paragraph in the example is one of the "
            "three counted elements", text)

    def test_example_to_file_step_is_stated(self):
        text = readme_flat()
        self.assertIn(
            "Save the example below to a file named QUEUE.md",
            text)


class F18RecoveryTest(unittest.TestCase):
    """F18-2: the recovery teaching for the self check outcome
    names what to record and how the passing entry forms are
    shaped."""

    def test_readme_recovery_names_the_check_and_the_fix(self):
        text = readme_flat()
        self.assertIn(
            "If a run is withheld as a tool fault", text)
        self.assertIn(
            "report the run as a tool fault", text)
        self.assertIn(
            "check each Banked entry in the file for one of "
            "the three counted elements", text)
        self.assertIn(
            "Adding labelled fields alone does not change "
            "this outcome", text)

    def test_readme_recovery_gives_the_field_record_form(self):
        text = readme_flat()
        self.assertIn("Question:", text)
        self.assertIn("Options:", text)
        self.assertIn("Cost of deciding late:", text)
        self.assertIn("Blocks:", text)
        self.assertIn(
            "each as its own labelled paragraph", text)
        self.assertIn(
            "Recording those four fields in that form, on an "
            "entry that also carries a counted element, clears "
            "the warnings", text)

    def test_recovery_form_as_taught_passes(self):
        code, out, err = run_file(
            "validate", LABELLED_AND_PARAGRAPH.encode("utf-8"))
        self.assertEqual(code, 0)
        self.assertNotIn("Tool fault", out)


class F18InstallTest(unittest.TestCase):
    """F18-3 and F18-5: the install instruction in executable
    form, the working directory stated, and the Python version
    check stated."""

    def test_readme_install_gives_a_copy_and_run_form(self):
        text = readme_flat()
        self.assertIn("cp -r decision_queue_validator", text)
        self.assertIn(
            "the directory that holds the package must be your "
            "current working directory", text)

    def test_readme_states_the_python_version_check(self):
        text = readme_flat()
        self.assertIn("python3 --version", text)
        self.assertIn("Python 3.11 or later", text)

    def test_module_runs_from_the_package_directory(self):
        data = PARAGRAPH_ONLY.encode("utf-8")
        code, out, err = run_file("validate", data)
        self.assertEqual(code, 1)

    def test_module_does_not_run_from_another_directory(self):
        env = dict(__import__("os").environ)
        env.pop("PYTHONPATH", None)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "QUEUE.md"
            target.write_bytes(PARAGRAPH_ONLY.encode("utf-8"))
            proc = subprocess.run(
                [sys.executable, "-m", h.PACKAGE, "validate",
                 str(target)],
                cwd=tmp, env=env,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(proc.returncode, 1)
        self.assertIn(
            b"No module named decision_queue_validator",
            proc.stderr)


class ClosingLinesTest(unittest.TestCase):
    """The closing lines statement, corrected: completed outputs
    end with two lines; refusal and usage outputs carry one
    closing line."""

    def test_completed_output_ends_with_two_lines(self):
        code, out, err = run_file(
            "validate", PARAGRAPH_ONLY.encode("utf-8"))
        lines = [ln for ln in out.strip().splitlines() if ln]
        self.assertTrue(lines[-2].startswith(
            "For the other view, run the render subcommand"),
            lines[-2])
        self.assertTrue(lines[-1].startswith("Exit: code 1"),
                        lines[-1])

    def test_refusal_output_carries_one_closing_line(self):
        code, out, err = run_file(
            "validate", b"# Decision queue\n", "header.md")
        self.assertEqual(code, 3)
        self.assertNotIn("For the other view", err)
        lines = [ln for ln in err.strip().splitlines() if ln]
        self.assertTrue(lines[-1].startswith("Exit: code 3"),
                        lines[-1])

    def test_usage_output_carries_one_closing_line(self):
        proc = subprocess.run(
            [sys.executable, "-m", h.PACKAGE],
            cwd=str(h.PRODUCT_ROOT), env=h.cli_env(h.SEED_ONE),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        err = proc.stderr.decode("utf-8", errors="replace")
        self.assertEqual(proc.returncode, 2)
        self.assertNotIn("For the other view", err)
        lines = [ln for ln in err.strip().splitlines() if ln]
        self.assertTrue(lines[-1].startswith("Exit: code 2"),
                        lines[-1])

    def test_readme_states_one_closing_line_for_those_forms(self):
        text = readme_flat()
        self.assertNotIn("Every output ends with two lines",
                         text)
        self.assertIn(
            "Refusal outputs and usage outputs carry one "
            "closing line", text)


class SelfRedirectTest(unittest.TestCase):
    """A20-1: the README warns against redirecting a report
    onto the input file own path."""

    def test_readme_carries_the_self_redirect_note(self):
        text = readme_flat()
        self.assertIn(
            "Do not redirect a report onto the input file own "
            "path", text)
        self.assertIn(
            "the shell empties the target file before the tool "
            "runs", text)

    def test_self_redirect_empties_the_input_before_the_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "self-redirect.md"
            target.write_bytes(PARAGRAPH_ONLY.encode("utf-8"))
            self.assertEqual(
                target.stat().st_nlink, 1)
            proc = subprocess.run(
                "%s -m %s validate %s > %s" % (
                    sys.executable, h.PACKAGE, target, target),
                shell=True, cwd=str(h.PRODUCT_ROOT),
                env=h.cli_env(h.SEED_ONE),
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.assertEqual(proc.returncode, 3)
            self.assertEqual(target.read_bytes(), b"")
            self.assertIn(b"empty file", proc.stderr)


class TestsTreeTest(unittest.TestCase):
    """F18-6 README limb: the tests tree explained."""

    def test_readme_explains_the_tests_tree(self):
        text = readme_flat()
        self.assertIn("The tests directory", text)
        self.assertIn(
            "You do not need the tests to run the tool", text)


if __name__ == "__main__":
    unittest.main()
