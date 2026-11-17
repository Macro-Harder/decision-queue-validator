"""Restart Step 17 fix wave 2, Seat K12 tests: shell surfaces.

Four charges stand in this file, all in shell.py, each written
before its cure:

CH-26 (S17-ATK2-12-01): the exit 3 refusal surfaces echo the
input name with no length bound. The cure brings _refusal_output
under the _bounded_echo rule at ARGUMENT_ECHO_LIMIT, the rule
Fix C5 charge 2 landed for the usage and not read surfaces. The
completed surface printing the name whole stands outside the
charge under the README promise, and a control here pins it.

CH-27 (S17-ATK2-12-02): a bundled short flag token in the file
position names the valid file as the unexpected argument. The
cure widens _is_flag_token to the bundled form, one dash
carrying two or more ASCII letters and nothing else, while a
dash leading file name keeps its status: a token carrying a
dot, a digit, or any other non letter after the dash, such as
-dashfile.md or -ab.md, stays a file name and validates
directly.

CH-29 (S17-ATK2-13-01 and S17-ATK2-13-02, one charge for two
findings): _os_error_cause states no exact cause for three
exactly nameable errors. The cure states the exact cause for
ENOTDIR in place of the missing cause, and for EMFILE and EIO
in place of the generic fallback. The exact wordings the cure
adopts, in the surface own fragment form, are: ENOTDIR, part
of its path is not a directory; EMFILE, too many files are
open; EIO, an input/output error occurred. No claim stands on
any other unmapped errno, as the finding paper bounds it.

CH-31 (S17-ATK2-14-01): a usage error whose standard error
cannot be delivered loses its closing exit line on every
channel, though standard output stands open. The cure extends
the Fix C6 charge 3 delivery fallback to _usage_error, the one
surface its call sites did not include. Where both channels
fail at once no line can be delivered and the decided code
alone carries the signal; that bound stands uncharged and no
test here charges it.
"""

import errno
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import dqv_harness as h

NOTDIR_CAUSE = "part of its path is not a directory"
EMFILE_CAUSE = "too many files are open"
EIO_CAUSE = "an input/output error occurred"
USAGE_CLOSING = (
    "Exit: code 2: usage error. This code is a findings signal "
    "and not a step verdict.")


def _run_argv(argv, cwd=None):
    proc = subprocess.run(
        [sys.executable, "-m", h.PACKAGE] + argv,
        cwd=str(cwd or h.PRODUCT_ROOT), env=h.cli_env(h.SEED_ONE),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return (proc.returncode, proc.stdout,
            proc.stderr.decode("utf-8", errors="replace"))


def _run_argv_stderr_dev_full(argv):
    with open("/dev/full", "wb") as full:
        proc = subprocess.run(
            [sys.executable, "-m", h.PACKAGE] + argv,
            cwd=str(h.PRODUCT_ROOT), env=h.cli_env(h.SEED_ONE),
            stdout=subprocess.PIPE, stderr=full)
    return proc.returncode, proc.stdout


def _run_argv_stdout_dev_full(argv):
    with open("/dev/full", "wb") as full:
        proc = subprocess.run(
            [sys.executable, "-m", h.PACKAGE] + argv,
            cwd=str(h.PRODUCT_ROOT), env=h.cli_env(h.SEED_ONE),
            stdout=full, stderr=subprocess.PIPE)
    return (proc.returncode,
            proc.stderr.decode("utf-8", errors="replace"))


def _long_path(directory, name):
    """One real file addressed by a long supplied path, in the
    attack paper form: the directory path followed by 200
    repetitions of the segment /. and then the file name."""
    return str(directory) + ("/." * 200) + "/" + name


def _input_line(text):
    for line in text.splitlines():
        if line.startswith("Input: "):
            return line
    raise AssertionError("no Input head line in: " + text[:200])


class Step17FixK12RefusalEchoBoundTest(unittest.TestCase):
    """CH-26: the refusal output echo bound."""

    def _refusal_run(self, subcommand, data, name):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / name
            target.write_bytes(data)
            long_path = _long_path(tmp, name)
            code, out, err = _run_argv([subcommand, long_path])
        return code, out, err, long_path

    def _assert_bounded(self, code, out, err, long_path):
        self.assertEqual(code, 3)
        self.assertEqual(out, b"")
        self.assertNotIn(long_path, err)
        note = "[truncated: %d characters in full]" % len(long_path)
        self.assertIn(note, err)
        line = _input_line(err)
        self.assertEqual(
            len(line), len("Input: ") + 120 + len(" " + note))

    def test_parse_level_refusal_echo_is_bounded(self):
        data = b"Some prose with no queue structure at all.\n"
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                code, out, err, long_path = self._refusal_run(
                    subcommand, data, "nostruct.md")
                self._assert_bounded(code, out, err, long_path)

    def test_pre_read_byte_refusal_echo_is_bounded(self):
        data = b"x" * 2000001
        code, out, err, long_path = self._refusal_run(
            "validate", data, "big.md")
        self._assert_bounded(code, out, err, long_path)

    def test_missing_file_by_long_path_control_stays_bounded(self):
        # Control, passing before and after: the not read surface
        # already carries the bound, on the same long path form.
        with tempfile.TemporaryDirectory() as tmp:
            long_path = _long_path(tmp, "missing.md")
            code, out, err = _run_argv(["validate", long_path])
        self.assertEqual(code, 2)
        self.assertEqual(out, b"")
        self.assertNotIn(long_path, err)
        self.assertIn(
            "[truncated: %d characters in full]" % len(long_path),
            err)

    def test_completed_run_by_long_path_prints_name_whole(self):
        # Scope control, passing before and after: the completed
        # surface prints the name whole under the README promise
        # and stands outside this charge.
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "valid.md"
            target.write_bytes(h.fixture_bytes("S5"))
            long_path = _long_path(tmp, "valid.md")
            code, out, err = _run_argv(["validate", long_path])
        self.assertEqual(code, 0)
        text = out.decode("utf-8", errors="replace")
        self.assertIn(long_path, text)
        self.assertNotIn("[truncated", text)


class Step17FixK12FlagTokenFormTest(unittest.TestCase):
    """CH-27: the flag token form in arity naming."""

    def test_bundled_short_flag_names_the_flag(self):
        control = str(h.corpus_path("S5"))
        code, out, err = _run_argv(["validate", "-ab", control])
        self.assertEqual(code, 2)
        self.assertEqual(out, b"")
        self.assertIn("unexpected argument: -ab", err)
        self.assertNotIn(control, err)

    def test_bundled_three_letter_flag_names_the_flag(self):
        control = str(h.corpus_path("S5"))
        code, out, err = _run_argv(["validate", "-xyz", control])
        self.assertEqual(code, 2)
        self.assertEqual(out, b"")
        self.assertIn("unexpected argument: -xyz", err)
        self.assertNotIn(control, err)

    def test_is_flag_token_bundled_form_unit(self):
        shell = h.import_module("shell")
        for token in ("-ab", "-abc", "-Ab", "-x", "--help", "--"):
            self.assertTrue(
                shell._is_flag_token(token),
                "expected a flag token: " + token)
        for token in ("-dashfile.md", "-ab.md", "-a1", "-",
                      "file.md", ""):
            self.assertFalse(
                shell._is_flag_token(token),
                "expected a file name token: " + token)

    def test_dotted_dash_token_still_names_the_token_after_it(self):
        # Control, passing before and after: a dash token
        # carrying a dot is a file name, so the arity branch
        # names the token after it, as in the two file case.
        control = str(h.corpus_path("S5"))
        code, out, err = _run_argv(["validate", "-ab.md", control])
        self.assertEqual(code, 2)
        self.assertIn("unexpected argument: " + control, err)
        self.assertNotIn("unexpected argument: -ab.md", err)

    def test_two_files_still_name_the_second_file(self):
        code, out, err = _run_argv(
            ["validate", "first.md", "second.md"])
        self.assertEqual(code, 2)
        self.assertIn("unexpected argument: second.md", err)

    def test_dash_leading_file_validates_directly(self):
        # Control, passing before and after: a dash leading file
        # name validates directly with no separator.
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "-dashfile.md"
            target.write_bytes(h.fixture_bytes("S5"))
            code, out, err = _run_argv(
                ["validate", "-dashfile.md"], cwd=tmp)
        self.assertEqual(code, 0)

    def test_dash_leading_file_arity_names_the_extra_token(self):
        # Control, passing before and after: with a dash leading
        # file in the file position, the extra token is named.
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "-dashfile.md"
            target.write_bytes(h.fixture_bytes("S5"))
            code, out, err = _run_argv(
                ["validate", "-dashfile.md", "extra.md"], cwd=tmp)
        self.assertEqual(code, 2)
        self.assertIn("unexpected argument: extra.md", err)


class Step17FixK12OsErrorCauseTest(unittest.TestCase):
    """CH-29: the operating system error cause mapping."""

    def test_enotdir_cause_unit(self):
        shell = h.import_module("shell")
        cause = shell._os_error_cause(
            NotADirectoryError(errno.ENOTDIR, "not a directory"))
        self.assertEqual(cause, NOTDIR_CAUSE)
        plain = OSError("not a directory")
        plain.errno = errno.ENOTDIR
        self.assertEqual(shell._os_error_cause(plain), NOTDIR_CAUSE)

    def test_emfile_cause_unit(self):
        shell = h.import_module("shell")
        cause = shell._os_error_cause(
            OSError(errno.EMFILE, "too many open files"))
        self.assertEqual(cause, EMFILE_CAUSE)

    def test_eio_cause_unit(self):
        shell = h.import_module("shell")
        cause = shell._os_error_cause(
            OSError(errno.EIO, "input/output error"))
        self.assertEqual(cause, EIO_CAUSE)

    def test_cause_controls_unit(self):
        # Controls, passing before and after: the plain missing
        # cause and the cured loop cause stand, and an errno the
        # surface cannot state exactly still falls back.
        shell = h.import_module("shell")
        self.assertEqual(
            shell._os_error_cause(
                OSError(errno.ENOENT, "no such file")),
            "it is missing")
        self.assertEqual(
            shell._os_error_cause(
                OSError(errno.ELOOP, "too many levels of links")),
            "it is a symlink loop")
        self.assertIsNone(
            shell._os_error_cause(
                OSError(errno.EINVAL, "invalid argument")))

    def test_path_through_regular_file_names_notdir_cause(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "valid.md"
            target.write_bytes(h.fixture_bytes("S5"))
            forms = (str(target) + "/child", str(target) + "/")
            results = []
            for form in forms:
                for subcommand in ("validate", "render"):
                    results.append((subcommand, form) +
                                   _run_argv([subcommand, form]))
        for subcommand, form, code, out, err in results:
            with self.subTest(subcommand=subcommand, form=form):
                self.assertEqual(code, 2)
                self.assertIn("Input not read: " + NOTDIR_CAUSE, err)
                self.assertNotIn("it is missing", err)

    def test_plain_missing_control_still_names_missing(self):
        # Control, passing before and after.
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "no_such_input.md"
            code, out, err = _run_argv(["validate", str(missing)])
        self.assertEqual(code, 2)
        self.assertIn("Input not read: it is missing", err)

    @unittest.skipUnless(os.path.exists("/proc/self/mem"),
                         "the EIO construction needs /proc/self/mem")
    def test_eio_run_names_the_cause(self):
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                code, out, err = _run_argv(
                    [subcommand, "/proc/self/mem"])
                self.assertEqual(code, 2)
                self.assertIn("Input not read: " + EIO_CAUSE, err)
                self.assertNotIn("it could not be read", err)

    def test_emfile_run_names_the_cause(self):
        # The attack paper driver form, restated: the package is
        # imported first, then the process soft descriptor limit
        # is lowered to the count of its standard descriptors, so
        # the shell open of the control file meets EMFILE. The
        # stat before it takes no descriptor and succeeds.
        driver = (
            "import resource, sys\n"
            "from decision_queue_validator import shell\n"
            "control = sys.argv[1]\n"
            "soft, hard = resource.getrlimit("
            "resource.RLIMIT_NOFILE)\n"
            "resource.setrlimit(resource.RLIMIT_NOFILE, (3, hard))\n"
            "code = shell.main(['validate', control])\n"
            "sys.stdout.write('MAIN_RETURNED %d\\n' % code)\n"
            "sys.stdout.flush()\n")
        proc = subprocess.run(
            [sys.executable, "-c", driver, str(h.corpus_path("S5"))],
            cwd=str(h.PRODUCT_ROOT), env=h.cli_env(h.SEED_ONE),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(proc.returncode, 0)
        self.assertIn(b"MAIN_RETURNED 2", proc.stdout)
        err = proc.stderr.decode("utf-8", errors="replace")
        self.assertIn("Input not read: " + EMFILE_CAUSE, err)
        self.assertNotIn("it could not be read", err)
        self.assertNotIn("Traceback", err)


class Step17FixK12UsageDeliveryFallbackTest(unittest.TestCase):
    """CH-31: the usage error closing line delivery fallback."""

    def _assert_fallback(self, argv):
        code, out = _run_argv_stderr_dev_full(argv)
        self.assertEqual(code, 2)
        text = out.decode("utf-8", errors="replace")
        self.assertEqual(text, USAGE_CLOSING + "\n")

    def test_no_arguments_closing_line_falls_back(self):
        self._assert_fallback([])

    def test_unknown_subcommand_closing_line_falls_back(self):
        self._assert_fallback(["bogus"])

    def test_validate_no_file_closing_line_falls_back(self):
        self._assert_fallback(["validate"])

    def test_validate_extra_argument_closing_line_falls_back(self):
        self._assert_fallback(
            ["validate", str(h.corpus_path("S5")), "extra.md"])

    def test_closed_stderr_descriptor_closing_line_falls_back(self):
        code, out, err = h.run_cli_closed_descriptor([], 2)
        self.assertEqual(code, 2)
        self.assertIn(USAGE_CLOSING.encode("utf-8"), out)
        self.assertNotIn(b"Traceback", err)

    def test_working_stderr_control_surface_whole_stdout_empty(self):
        # Control, passing before and after: with a working
        # standard error the usage surface stands whole on it
        # and standard output carries nothing.
        code, out, err = _run_argv([])
        self.assertEqual(code, 2)
        self.assertEqual(out, b"")
        self.assertIn("Call fault: usage error.", err)
        self.assertIn(USAGE_CLOSING, err)

    def test_stdout_full_control_surface_intact_on_stderr(self):
        # Control, passing before and after, in the paper form:
        # standard output to /dev/full with standard error
        # working leaves the usage surface intact on stderr.
        code, err = _run_argv_stdout_dev_full([])
        self.assertEqual(code, 2)
        self.assertIn(USAGE_CLOSING, err)


if __name__ == "__main__":
    unittest.main()
