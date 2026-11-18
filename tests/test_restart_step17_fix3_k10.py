"""Restart Step 17 fix wave 3, Seat K10 tests: shell causes.

One charge stands in this file, in shell.py, written before
its cure:

CH-46 (S17-ATK3-13-01, Low): _os_error_cause states no exact
cause for ENFILE (errno 23, too many open files in system),
so ENFILE falls back to the generic "it could not be read" at
both the stat stage and the open stage of an input read. The
cure states the exact cause for ENFILE in place of the
generic fallback, in the form of the cured EMFILE and EIO
causes of CH-29: ENFILE, too many files are open in the
system. Ruling (n) at section 26 of the step record bounds
the cure expressly: it states the ENFILE cause and no other.
Seat 13 observations O-1 and O-2 (EINVAL, ESTALE, and ENOSPC
standing ungraded, each on a stated ground) are not decided
by this cure and stand as recorded; a control below pins
only that those three errnos still take no named cause on
this surface, which is the cure bound, not a grading of any
of them.

Evidence bound, as the finding paper states it: ENFILE was
injected at the OS boundary, not induced from the kernel,
because inducing it for real means exhausting the file table
of the whole machine. The surface tests here pin the cause
mapping on that same footing, in the attack paper injection
driver form: the OS boundary is patched so the stat call or
the open call raises the chosen errno, and shell.main is
called on a valid control file. The harness fidelity controls
prove the driver on the same footing the paper measured it:
injected EIO at the open call and injected EMFILE at the stat
call take their exact cured causes.
"""

import errno
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import dqv_harness as h

ENFILE_CAUSE = "too many files are open in the system"
EMFILE_CAUSE = "too many files are open"
EIO_CAUSE = "an input/output error occurred"
NOTDIR_CAUSE = "part of its path is not a directory"
GENERIC_CAUSE = "it could not be read"
CLOSING_TAIL = "input not read"


def _inject_driver(stage, err, subcommand, path):
    """The attack seat 13 injection driver form, restated.

    A fresh process imports the package, patches the OS
    boundary so the call named by stage raises OSError with
    the chosen errno for the control path alone, and calls
    shell.main on the control. Returns (returncode, stdout,
    stderr) of the driver process; the shell surface stands
    on the driver standard error, and the driver confirms the
    code shell.main returned on its standard output.
    """
    driver = (
        "import builtins, os, sys\n"
        "from decision_queue_validator import shell\n"
        "stage, err, subcommand, path = (\n"
        "    sys.argv[1], int(sys.argv[2]), sys.argv[3],\n"
        "    sys.argv[4])\n"
        "if stage == 'stat':\n"
        "    real_stat = os.stat\n"
        "    def fake_stat(p, *a, **k):\n"
        "        if p == path:\n"
        "            raise OSError(err, os.strerror(err))\n"
        "        return real_stat(p, *a, **k)\n"
        "    shell.os.stat = fake_stat\n"
        "else:\n"
        "    real_open = builtins.open\n"
        "    def fake_open(p, *a, **k):\n"
        "        if p == path:\n"
        "            raise OSError(err, os.strerror(err))\n"
        "        return real_open(p, *a, **k)\n"
        "    builtins.open = fake_open\n"
        "code = shell.main([subcommand, path])\n"
        "sys.stdout.write('MAIN_RETURNED %d\\n' % code)\n"
        "sys.stdout.flush()\n")
    proc = subprocess.run(
        [sys.executable, "-c", driver, stage, str(err),
         subcommand, str(path)],
        cwd=str(h.PRODUCT_ROOT), env=h.cli_env(h.SEED_ONE),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return (proc.returncode,
            proc.stdout.decode("utf-8", errors="replace"),
            proc.stderr.decode("utf-8", errors="replace"))


def _control_path(directory):
    target = Path(directory) / "valid.md"
    target.write_bytes(h.fixture_bytes("S5"))
    return str(target)


class Step17Fix3K10EnfileCauseUnitTest(unittest.TestCase):
    """CH-46: the ENFILE cause at the _os_error_cause unit."""

    def test_enfile_cause_unit(self):
        shell = h.import_module("shell")
        cause = shell._os_error_cause(
            OSError(errno.ENFILE, "too many open files in system"))
        self.assertEqual(cause, ENFILE_CAUSE)

    def test_enfile_cause_plain_errno_form(self):
        shell = h.import_module("shell")
        plain = OSError("too many open files in system")
        plain.errno = errno.ENFILE
        self.assertEqual(shell._os_error_cause(plain), ENFILE_CAUSE)

    def test_cured_sibling_causes_stand_unit(self):
        # Controls, passing before and after: the CH-29 limbs
        # in the same function stand exactly as cured.
        shell = h.import_module("shell")
        self.assertEqual(
            shell._os_error_cause(
                OSError(errno.EMFILE, "too many open files")),
            EMFILE_CAUSE)
        self.assertEqual(
            shell._os_error_cause(
                OSError(errno.EIO, "input/output error")),
            EIO_CAUSE)
        self.assertEqual(
            shell._os_error_cause(
                NotADirectoryError(errno.ENOTDIR,
                                   "not a directory")),
            NOTDIR_CAUSE)

    def test_no_other_errno_named_unit(self):
        # Ruling (n) bound control, passing before and after:
        # the cure states the ENFILE cause and no other, so the
        # errnos seat 13 recorded ungraded at O-1 and O-2
        # (EINVAL, ESTALE, ENOSPC) still take no named cause.
        # This pins the cure bound only; it grades none of them.
        shell = h.import_module("shell")
        for err in (errno.EINVAL, errno.ESTALE, errno.ENOSPC):
            with self.subTest(errno=err):
                self.assertIsNone(
                    shell._os_error_cause(
                        OSError(err, "recorded ungraded")))


class Step17Fix3K10EnfileSurfaceTest(unittest.TestCase):
    """CH-46: ENFILE injected at the OS boundary, both stages."""

    def _assert_enfile_surface(self, stage, subcommand):
        with tempfile.TemporaryDirectory() as tmp:
            control = _control_path(tmp)
            returned, out, err = _inject_driver(
                stage, errno.ENFILE, subcommand, control)
        self.assertEqual(returned, 0)
        self.assertIn("MAIN_RETURNED 2", out)
        self.assertIn("Input not read: " + ENFILE_CAUSE, err)
        self.assertNotIn(GENERIC_CAUSE, err)
        self.assertIn("Exit: code 2", err)
        self.assertNotIn("Traceback", err)

    def test_enfile_at_stat_validate(self):
        self._assert_enfile_surface("stat", "validate")

    def test_enfile_at_stat_render(self):
        self._assert_enfile_surface("stat", "render")

    def test_enfile_at_open_validate(self):
        self._assert_enfile_surface("open", "validate")

    def test_enfile_at_open_render(self):
        self._assert_enfile_surface("open", "render")

    def test_driver_fidelity_controls(self):
        # Controls, passing before and after, on the paper
        # measured footing: the same driver delivers errnos to
        # the surface faithfully, injected EMFILE at the stat
        # call and injected EIO at the open call each taking
        # its exact cured cause.
        with tempfile.TemporaryDirectory() as tmp:
            control = _control_path(tmp)
            cases = (
                ("stat", errno.EMFILE, EMFILE_CAUSE),
                ("open", errno.EIO, EIO_CAUSE),
            )
            results = []
            for stage, err, cause in cases:
                for subcommand in ("validate", "render"):
                    results.append(
                        (stage, err, cause, subcommand) +
                        _inject_driver(stage, err, subcommand,
                                       control))
        for stage, err, cause, subcommand, returned, out, serr \
                in results:
            with self.subTest(stage=stage, errno=err,
                              subcommand=subcommand):
                self.assertEqual(returned, 0)
                self.assertIn("MAIN_RETURNED 2", out)
                self.assertIn("Input not read: " + cause, serr)
                self.assertNotIn(GENERIC_CAUSE, serr)


if __name__ == "__main__":
    unittest.main()
