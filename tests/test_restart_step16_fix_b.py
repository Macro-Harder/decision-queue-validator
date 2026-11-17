"""Restart Step 16 fix wave, Fix seat B tests.

Seat B owns shell.py. The items pinned here stand in the Step 16
record at design/steps/step-16r-record.md section 6:

Item 1, F3 in the narrowed form of Auditor 5 (design/steps/
step-16r-audit1-5.md section 6, Cure A): the top level --help and
-h special case stands removed, so both forms take the specified
usage error surface, as --version already does: standard error
only, the call fault wording, the closing line last, exit 2.

Item 2, A16-F1 (Auditor 16, design/steps/step-16r-audit1-16.md
Finding 1): the input not read surface names the exact cause
where the code knows it, one cause per path, instead of the
identical four way disjunction.

Item 3, A16-F2 shell loci (the same paper, Finding 2): the
missing argument message names what is actually missing in each
case. The bare invocation lacks both a subcommand and an input
file; an invocation carrying a subcommand and no file lacks the
input file only.
"""

import io
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

import dqv_harness as h

DISJUNCTION = (
    "missing, unreadable, a directory, or not a regular file")


def run_argv(argv):
    import subprocess
    import sys
    proc = subprocess.run(
        [sys.executable, "-m", h.PACKAGE] + argv,
        cwd=str(h.PRODUCT_ROOT), env=h.cli_env(h.SEED_ONE),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return (proc.returncode,
            proc.stdout.decode("utf-8", errors="replace"),
            proc.stderr.decode("utf-8", errors="replace"))


def run_main_in_process(argv):
    from decision_queue_validator import shell
    out = io.StringIO()
    err = io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = shell.main(argv)
    return code, out.getvalue(), err.getvalue()


def cause_line(err_text):
    for line in err_text.splitlines():
        if line.startswith("Input not read:"):
            return line
    raise AssertionError("no Input not read line in: " + err_text)


class HelpSurfaceTest(unittest.TestCase):
    """F3 cure: --help and -h take the usage error surface."""

    def check_usage_error_surface(self, argv, token):
        code, out, err = run_argv(argv)
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertIn(
            "Call fault: usage error. No run took place and no "
            "file was read as a queue.", err)
        self.assertIn("Usage error: unknown subcommand: " + token,
                      err)
        self.assertIn(
            "Usage: python3 -m decision_queue_validator "
            "{validate|render} INPUT", err)
        lines = [ln for ln in err.strip().splitlines() if ln]
        self.assertTrue(lines)
        self.assertIn("Exit: code 2: usage error.", lines[-1])
        self.assertIn(
            "This code is a findings signal and not a step "
            "verdict.", lines[-1])

    def test_help_long_form_takes_usage_error_surface(self):
        self.check_usage_error_surface(["--help"], "--help")

    def test_help_short_form_takes_usage_error_surface(self):
        self.check_usage_error_surface(["-h"], "-h")

    def test_help_with_trailing_argument_takes_usage_error(self):
        self.check_usage_error_surface(
            ["--help", "validate"], "--help")


class InputNotReadCauseTest(unittest.TestCase):
    """A16-F1: the surface names the exact cause it knows."""

    def test_missing_file_names_missing_cause(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = str(Path(tmp) / "no_such_input.md")
            code, out, err = run_argv(["validate", missing])
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        line = cause_line(err)
        self.assertEqual(
            line, "Input not read: %s: it is missing" % missing)
        self.assertNotIn(DISJUNCTION, err)
        self.assertNotIn("unreadable", line)

    def test_directory_names_directory_cause(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, out, err = run_argv(["validate", tmp])
            self.assertEqual(code, 2)
            self.assertEqual(out, "")
            line = cause_line(err)
            self.assertEqual(
                line,
                "Input not read: %s: it is a directory" % tmp)
            self.assertNotIn(DISJUNCTION, err)

    def test_not_regular_file_names_not_regular_cause(self):
        with tempfile.TemporaryDirectory() as tmp:
            fifo = Path(tmp) / "input_fifo"
            os.mkfifo(fifo)
            code, out, err = run_argv(["validate", str(fifo)])
            self.assertEqual(code, 2)
            self.assertEqual(out, "")
            line = cause_line(err)
            self.assertEqual(
                line,
                "Input not read: %s: it is not a regular file"
                % fifo)
            self.assertNotIn(DISJUNCTION, err)

    def test_unreadable_file_names_unreadable_cause(self):
        path = h.temp_input(b"# Decision queue\n",
                            "unreadable_input.md")
        with mock.patch(
                "builtins.open",
                side_effect=PermissionError(
                    13, "Permission denied")):
            code, out, err = run_main_in_process(
                ["validate", str(path)])
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        line = cause_line(err)
        self.assertEqual(
            line,
            "Input not read: %s: it is unreadable" % path)
        self.assertNotIn(DISJUNCTION, err)
        self.assertNotIn("missing", line)

    def test_unreadable_stat_names_unreadable_cause(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = str(Path(tmp) / "guarded_input.md")
            with mock.patch(
                    "os.stat",
                    side_effect=PermissionError(
                        13, "Permission denied")):
                code, out, err = run_main_in_process(
                    ["validate", target])
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        line = cause_line(err)
        self.assertEqual(
            line,
            "Input not read: %s: it is unreadable" % target)
        self.assertNotIn(DISJUNCTION, err)


class MissingArgumentMessageTest(unittest.TestCase):
    """A16-F2 shell loci: the message names what is missing."""

    def test_bare_invocation_names_both_missing(self):
        code, out, err = run_argv([])
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertIn(
            "Usage error: a subcommand and an input file are "
            "required", err)

    def test_validate_with_no_file_names_input_file_only(self):
        code, out, err = run_argv(["validate"])
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertIn("Usage error: an input file is required",
                      err)
        self.assertNotIn(
            "a subcommand and an input file are required", err)

    def test_render_with_no_file_names_input_file_only(self):
        code, out, err = run_argv(["render"])
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertIn("Usage error: an input file is required",
                      err)
        self.assertNotIn(
            "a subcommand and an input file are required", err)


if __name__ == "__main__":
    unittest.main()
