"""Slice 5, shell and run conditions group.

Argument handling, the exit 2 branches before any parse, the output
equals input refusal in its own form, the exit 3 file facts form, the
write mechanism for a named output file, delivery failure, the input
left byte identical after every run, and the determinism discipline:
every fixture under both subcommands where the subcommand applies,
each run made twice as two separate processes under the two recorded
hash seed values, compared only within the same subcommand. For exit
2 runs and file level exit 3 runs the comparison covers the shell
composed head text and the exit code only.
"""

import ast
import os
import resource
import tempfile
import unittest
from pathlib import Path

import dqv_harness as h


class EntryDelegationTest(unittest.TestCase):

    def test_entry_module_only_delegates_to_shell(self):
        source = h.module_source("__main__")
        tree = ast.parse(source)
        imported = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported.append(node.module or "")
        joined = " ".join(imported)
        self.assertIn("shell", joined)
        for banned in ("argparse", "parse", "validate", "render"):
            self.assertNotIn(banned, joined)
        self.assertNotIn("open(", source)
        self.assertNotIn("OUTPUT_FORM_EDITION", source)
        self.assertNotIn("output_form_edition", source)
        self.assertIn("shell", source)
        self.assertIn("main", source)

    def test_shell_exposes_a_main_entry(self):
        shell = h.import_module("shell")
        self.assertTrue(callable(getattr(shell, "main", None)))


class ExitTwoBranchesTest(unittest.TestCase):

    def test_usage_error_exits_two(self):
        code, _out, _err = h.run_cli("bogus", h.corpus_path("S5"))
        self.assertEqual(code, 2)
        code, _out, _err = h.run_cli(None, None)
        self.assertEqual(code, 2)

    def test_usage_error_closed_stderr_unknown_exits_two(self):
        code, out, err = h.run_cli_closed_descriptor(
            ["bogus", "x.md"], 2)
        self.assertEqual(code, 2)
        self.assertNotIn(b"Traceback", err)
        self.assertNotIn(b"AttributeError", err)

    def test_usage_error_closed_stderr_no_arguments_exits_two(self):
        code, out, err = h.run_cli_closed_descriptor([], 2)
        self.assertEqual(code, 2)
        self.assertNotIn(b"Traceback", err)
        self.assertNotIn(b"AttributeError", err)

    def test_usage_error_with_none_stderr_in_process_returns_two(self):
        import sys as _sys
        shell = h.import_module("shell")
        saved = _sys.stderr
        _sys.stderr = None
        try:
            code = shell.main(["bogus", "x.md"])
        finally:
            _sys.stderr = saved
        self.assertEqual(code, 2)

    def test_usage_error_stderr_flush_failure_exits_two(self):
        # Standard error is a regular file in a scratch directory,
        # and its writes are made to fail at flush time by a file
        # size limit of zero set on this test process for the run
        # only, the same mechanism the standard output flush test
        # uses, now aimed at the standard error channel. The limit
        # is restored before any assertion runs. The assertion is
        # on the finished process return code, because the defect
        # lives past the return of the usage writer, at interpreter
        # shutdown.
        with tempfile.TemporaryDirectory() as tmp:
            stderr_path = Path(tmp) / "stderr.txt"
            soft, hard = resource.getrlimit(resource.RLIMIT_FSIZE)
            resource.setrlimit(resource.RLIMIT_FSIZE, (0, hard))
            try:
                code, out = h.run_cli_stderr_redirect(
                    ["bogus", "x.md"], stderr_path)
            finally:
                resource.setrlimit(resource.RLIMIT_FSIZE, (soft, hard))
            self.assertEqual(code, 2)
            self.assertEqual(out, b"")
            self.assertNotIn(
                "Exception ignored",
                stderr_path.read_bytes().decode(
                    "utf-8", errors="replace"))

    def test_missing_input_exits_two_with_input_not_read_form(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "no_such_input.md"
            code, out, _err = h.run_cli("validate", missing)
            self.assertEqual(code, 2)
            text = out.decode("utf-8", errors="replace")
            self.assertIn("input not read", text)
            self.assertIn("no_such_input.md", text)
            self.assertNotIn("entry count:", text.replace(
                "entry count: not parsed", ""))

    def test_missing_input_limits_line_prints_the_unit_form(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "no_such_input.md"
            code, out, _err = h.run_cli("validate", missing)
            self.assertEqual(code, 2)
            text = out.decode("utf-8", errors="replace")
            self.assertIn(
                "Limits in force: 2,000,000 bytes per file; "
                "10,000 lines per file; 16,384 characters per "
                "line; vocabulary version 1; output form "
                "edition 1", text)

    def test_unreadable_input_exits_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = h.make_unreadable_input(tmp)
            code, _out, _err = h.run_cli("validate", target)
            self.assertEqual(code, 2)

    def test_directory_named_as_input_exits_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, out, _err = h.run_cli("validate", tmp)
            self.assertEqual(code, 2)
            text = out.decode("utf-8", errors="replace")
            self.assertIn("input not read", text)

    def test_non_regular_file_input_exits_two_before_any_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            fifo = Path(tmp) / "input_fifo"
            os.mkfifo(fifo)
            code, out, _err = h.run_cli("validate", fifo)
            self.assertEqual(code, 2)
            text = out.decode("utf-8", errors="replace")
            self.assertIn("input not read", text)
            self.assertNotIn("bytes", text.lower().replace(
                "0 bytes", ""))


class UnknownSubcommandOrderingTest(unittest.TestCase):
    """An unknown first token is named as what it is.

    The subcommand is recognised before the arity of the whole
    command is judged: a user who typed a wrong subcommand word is
    told that, and a user who typed a known subcommand with no
    input, or nothing at all, keeps the present report.
    """

    def _run_argv(self, argv):
        import subprocess
        import sys as _sys
        proc = subprocess.run(
            [_sys.executable, "-m", h.PACKAGE] + argv,
            cwd=str(h.PRODUCT_ROOT), env=h.cli_env(h.SEED_ONE),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return proc.returncode, proc.stdout, proc.stderr

    def test_lone_unknown_token_reports_unknown_subcommand(self):
        code, out, err = self._run_argv(["bogus"])
        self.assertEqual(code, 2)
        self.assertEqual(out, b"")
        message = err.decode("utf-8", errors="replace")
        self.assertIn("unknown subcommand: bogus", message)
        self.assertNotIn("are required", message)

    def test_known_subcommand_with_no_input_keeps_its_report(self):
        code, out, err = self._run_argv(["validate"])
        self.assertEqual(code, 2)
        message = err.decode("utf-8", errors="replace")
        self.assertIn("a subcommand and an input file are "
                      "required", message)

    def test_no_arguments_at_all_keeps_its_report(self):
        code, out, err = self._run_argv([])
        self.assertEqual(code, 2)
        message = err.decode("utf-8", errors="replace")
        self.assertIn("a subcommand and an input file are "
                      "required", message)


class HelpFormTest(unittest.TestCase):
    """Step 19 R-17 and the R-19 wording limb: a help request is
    answered as help.

    A first operator whose first act is to ask for help, with
    --help or -h, is answered with the usage text on standard
    output and exit 0. The request is never answered with the
    unknown subcommand error: that wording misdescribes a help
    request as a malformed invocation.
    """

    def _run_argv(self, argv):
        import subprocess
        import sys as _sys
        proc = subprocess.run(
            [_sys.executable, "-m", h.PACKAGE] + argv,
            cwd=str(h.PRODUCT_ROOT), env=h.cli_env(h.SEED_ONE),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return proc.returncode, proc.stdout, proc.stderr

    def test_help_long_form_prints_usage_to_stdout_and_exits_zero(self):
        code, out, err = self._run_argv(["--help"])
        self.assertEqual(code, 0)
        text = out.decode("utf-8", errors="replace")
        self.assertIn("usage:", text)
        self.assertIn("validate", text)
        self.assertIn("render", text)
        self.assertEqual(err, b"")
        self.assertNotIn("unknown subcommand", text)

    def test_help_short_form_prints_usage_to_stdout_and_exits_zero(self):
        code, out, err = self._run_argv(["-h"])
        self.assertEqual(code, 0)
        text = out.decode("utf-8", errors="replace")
        self.assertIn("usage:", text)
        self.assertEqual(err, b"")
        self.assertNotIn("unknown subcommand", text)


class OutputEqualsInputRefusalTest(unittest.TestCase):

    def _assert_refusal_form(self, code, out, input_path):
        self.assertEqual(code, 2)
        text = out.decode("utf-8", errors="replace")
        self.assertIn(str(input_path), text)
        self.assertIn("same file as the input file", text)
        self.assertNotIn("not parsed", text)
        digest_fragment = None
        with open(input_path, "rb") as handle:
            digest_fragment = h.sha256_hex(handle.read())[:12]
        self.assertNotIn(digest_fragment, text)

    def test_same_path_refused(self):
        target = h.corpus_path("S5")
        before = h.fixture_bytes("S5")
        code, out, _err = h.run_cli("validate", target,
                                    output_path=target)
        self._assert_refusal_form(code, out, target)
        self.assertEqual(h.fixture_bytes("S5"), before)

    def test_link_to_input_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "input.md"
            source.write_bytes(h.fixture_bytes("S5"))
            link = Path(tmp) / "output_link.md"
            os.symlink(source, link)
            before = source.read_bytes()
            code, out, _err = h.run_cli("validate", source,
                                        output_path=link)
            self._assert_refusal_form(code, out, source)
            self.assertEqual(source.read_bytes(), before)

    def test_hard_link_to_input_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "input.md"
            source.write_bytes(h.fixture_bytes("S5"))
            hard = Path(tmp) / "output_hard.md"
            os.link(source, hard)
            before = source.read_bytes()
            code, out, _err = h.run_cli("validate", source,
                                        output_path=hard)
            self._assert_refusal_form(code, out, source)
            self.assertEqual(source.read_bytes(), before)


class NotReadOutputDeliveryTest(unittest.TestCase):
    """The not read report honours a named --output file.

    The README's --output promise is unqualified, and the not read
    form is a composed output like the file level form, which does
    honour the flag. The refusal form is outside this class: its
    named output is the input file itself, and it stays on standard
    output as designed.
    """

    def test_missing_input_with_output_writes_the_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "no_such_input.md"
            named = Path(tmp) / "report.txt"
            code, out, err = h.run_cli("validate", missing,
                                       output_path=named)
            self.assertEqual(code, 2)
            self.assertEqual(out, b"")
            self.assertEqual(err, b"")
            self.assertTrue(named.exists())
            text = named.read_bytes().decode("utf-8",
                                             errors="replace")
            self.assertIn("input not read", text)
            self.assertIn("no_such_input.md", text)

    def test_directory_input_with_output_writes_the_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            named = Path(tmp) / "report.txt"
            code, out, err = h.run_cli("validate", tmp,
                                       output_path=named)
            self.assertEqual(code, 2)
            self.assertEqual(out, b"")
            self.assertEqual(err, b"")
            self.assertTrue(named.exists())
            text = named.read_bytes().decode("utf-8",
                                             errors="replace")
            self.assertIn("input not read", text)

    def test_missing_input_with_output_in_a_missing_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "no_such_input.md"
            named = Path(tmp) / "no_such_dir" / "report.txt"
            code, out, err = h.run_cli("validate", missing,
                                       output_path=named)
            self.assertEqual(code, 2)
            self.assertEqual(out, b"")
            self.assertTrue(err)
            self.assertFalse(named.exists())
            self.assertEqual(sorted(os.listdir(tmp)), [])


class ExitThreeHeadFormTest(unittest.TestCase):

    def test_exit3_file_facts_form(self):
        code, out, _err = h.cached_run("S10", "validate")
        self.assertEqual(code, 3)
        text = out.decode("utf-8", errors="replace")
        self.assertIn("S10.md", text)
        self.assertIn("entry count: not parsed", text)
        digest_fragment = h.sha256_hex(h.fixture_bytes("S10"))[:12]
        self.assertIn(digest_fragment, text)

    def test_no_structure_sentence_names_what_was_looked_for(self):
        # Brief section 6.2: the file level result states what
        # recognisable queue structure is missing, in words the user
        # holds, and never the "measured header form" wording.
        # S10's first heading is a level 1 heading. Under the
        # Step 19 R-02 cure the file header test is level and first
        # position only (brief section 5.3, its text not tested), so
        # S10 now stands as a header only file and its sentence
        # states that a queue header is present; the earlier form
        # of this test expected the "no queue header" sentence on
        # S10, which rested on the text tested reading the cure
        # removes. S10's pinned expectations stand preserved: exit
        # 3 and no entry report. The tension between the brief's
        # S10 prose and its own header test is recorded in the
        # Step 19 fix register.
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                code, out, _err = h.cached_run("S10", subcommand)
                self.assertEqual(code, 3)
                text = out.decode("utf-8", errors="replace")
                self.assertIn(
                    "Missing structure: a queue header is present "
                    "but no entry heading", text)
                self.assertNotIn("no queue header", text)
                self.assertNotIn("measured header form", text)

    def test_prose_file_missing_structure_sentence_is_plain(self):
        # This construction holds a first H1 and prose only. Under
        # the Step 19 R-02 cure it is a header only file: brief
        # section 5.3 tests the file header by level and first
        # position only, its text not tested, so the statement must
        # not say no queue header is present about a file holding
        # an H1. The earlier form of this test expected the "no
        # queue header" sentence on this shape; that expectation
        # encoded the R-02 defect and stands corrected here. The
        # plain words requirement stands: no "measured header
        # form" wording may appear.
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "prose.md"
            target.write_bytes(
                b"# Notes on a rota\n\nSome prose about the rota, "
                b"with no queue forms in it.\n")
            code, out, _err = h.run_cli("validate", target)
            self.assertEqual(code, 3)
            text = out.decode("utf-8", errors="replace")
            self.assertIn(
                "Missing structure: a queue header is present but "
                "no entry heading", text)
            self.assertNotIn("no queue header", text)
            self.assertNotIn("measured header form", text)

    def test_byte_breach_head_omits_the_line_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            data, _facts = h.limit_bytes_input()
            target = Path(tmp) / "big.md"
            target.write_bytes(data)
            code, out, _err = h.run_cli("validate", target)
            self.assertEqual(code, 3)
            text = out.decode("utf-8", errors="replace")
            self.assertIn("entry count: not parsed", text)

    def test_limit_breach_names_the_limit_and_its_measured_value(self):
        with tempfile.TemporaryDirectory() as tmp:
            data, facts = h.limit_lines_input()
            target = Path(tmp) / "many_lines.md"
            target.write_bytes(data)
            code, out, _err = h.run_cli("validate", target)
            self.assertEqual(code, 3)
            text = out.decode("utf-8", errors="replace")
            self.assertIn("10001", text.replace("10,001", "10001"))
            self.assertIn("10000", text.replace("10,000", "10000"))


class CoOccurringBreachMeasuredValuesTest(unittest.TestCase):
    """Step 19 R-12: every breached limit named carries its value.

    Brief section 5.3: a breach result names the breached limit
    and its measured value. Where two breaches co-occur, the
    second breach is not named bare.
    """

    def test_byte_and_per_line_breaches_each_carry_a_measured_value(self):
        data = b"x" * 2000052 + b"\n"
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "big.md"
            target.write_bytes(data)
            code, out, _err = h.run_cli("validate", target)
            self.assertEqual(code, 3)
            text = out.decode("utf-8", errors="replace")
            self.assertIn(
                "Breached limit: max bytes "
                "(measured value 2000053)", text)
            self.assertIn(
                "Breached limit: max characters per line "
                "(measured value 2000052)", text)

    def test_byte_and_line_breaches_each_carry_a_measured_value(self):
        lines = ["# Decision queue", ""]
        while len(lines) < 10001:
            lines.append("A valid queue shaped prose line.")
        filler = "Filler line of plain queue prose.\n"
        repeats = (2000000 // len(filler)) + 2
        data = ("\n".join(lines) + "\n" + filler * repeats).encode(
            "utf-8")
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "big.md"
            target.write_bytes(data)
            code, out, _err = h.run_cli("validate", target)
            self.assertEqual(code, 3)
            text = out.decode("utf-8", errors="replace")
            self.assertIn(
                "Breached limit: max bytes (measured value %d)"
                % len(data), text)
            line_count = h.count_lines_formula(data)
            self.assertIn(
                "Breached limit: max lines (measured value %d)"
                % line_count, text)


class ReadmeCacheStatementTest(unittest.TestCase):
    """Step 19 R-18: the README states the truth about the cache.

    The tool itself writes no log file and no run record. In a
    default environment, though, one run leaves the interpreter
    bytecode cache, decision_queue_validator/__pycache__
    holding .pyc files, inside the tool own directory; a run
    under PYTHONDONTWRITEBYTECODE=1 leaves no cache. The README
    sentence must state both halves, not claim no cache at all.
    """

    def _readme(self):
        with open(h.PRODUCT_ROOT / "README.md", "r",
                  encoding="utf-8") as handle:
            return handle.read()

    def test_readme_states_the_cache_truth_in_both_environments(self):
        text = self._readme()
        self.assertNotIn(
            "no log file, no cache, and no run record", text)
        self.assertIn("__pycache__", text)
        self.assertIn("PYTHONDONTWRITEBYTECODE=1", text)
        self.assertIn("no log file", text)
        self.assertIn("no run record", text)


class WriteMechanismTest(unittest.TestCase):

    def test_named_output_file_receives_the_composed_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            named = Path(tmp) / "out.txt"
            code, out, _err = h.run_cli("render",
                                        h.corpus_path("S5"),
                                        output_path=named)
            self.assertEqual(code, 0)
            self.assertTrue(named.exists())
            if not named.exists():
                return
            code2, stdout_bytes, _err2 = h.cached_run("S5", "render")
            self.assertEqual(named.read_bytes(), stdout_bytes)

    def test_rerun_replaces_a_named_output_with_identical_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            named = Path(tmp) / "out.txt"
            code, _out, _err = h.run_cli("validate",
                                         h.corpus_path("S5"),
                                         output_path=named)
            self.assertEqual(code, 0)
            self.assertTrue(named.exists())
            first = named.read_bytes()
            h.run_cli("validate", h.corpus_path("S5"),
                      output_path=named)
            self.assertEqual(named.read_bytes(), first)

    def test_output_path_that_is_a_directory_exits_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            named = Path(tmp) / "a_directory"
            named.mkdir()
            code, _out, err = h.run_cli("validate",
                                        h.corpus_path("S5"),
                                        output_path=named)
            self.assertEqual(code, 2)
            self.assertTrue(err)
            self.assertEqual(sorted(os.listdir(tmp)), ["a_directory"])

    def test_failed_write_leaves_a_preexisting_output_untouched(self):
        # The named output of the run is the preexisting file itself.
        # The write to it is made to fail by a file size limit of
        # zero set on this test process for the run only: the run
        # inherits the limit, so every write it attempts to the named
        # output or to the temporary file of the write mechanism
        # fails for any account, where a permission based failure
        # would not bind an account that bypasses permission bits.
        # The limit is restored before any assertion runs.
        with tempfile.TemporaryDirectory() as tmp:
            named = Path(tmp) / "out.txt"
            named.write_bytes(b"previous content\n")
            soft, hard = resource.getrlimit(resource.RLIMIT_FSIZE)
            resource.setrlimit(resource.RLIMIT_FSIZE, (0, hard))
            try:
                code, _out, err = h.run_cli("validate",
                                            h.corpus_path("S5"),
                                            output_path=named)
            finally:
                resource.setrlimit(resource.RLIMIT_FSIZE, (soft, hard))
            self.assertEqual(code, 2)
            self.assertTrue(err)
            self.assertEqual(named.read_bytes(), b"previous content\n")
            self.assertEqual(sorted(os.listdir(tmp)), ["out.txt"])

    def test_failed_write_message_names_the_target_in_plain_words(self):
        # Brief section 6.2: a failed write to a named output file is
        # reported on the standard error channel, naming the output
        # path and the failure. The temporary file of the write
        # mechanism is an internal name, and the raw errno bracket is
        # not a plain word failure, so neither stands in the message.
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "no_such_dir" / "out.txt"
            code, out, err = h.run_cli("render",
                                       h.corpus_path("R5"),
                                       output_path=target)
            self.assertEqual(code, 2)
            self.assertEqual(out, b"")
            message = err.decode("utf-8", errors="replace")
            self.assertIn(str(target), message)
            self.assertIn("No such file or directory", message)
            self.assertNotIn(".dqv-output-", message)
            self.assertNotIn("Errno", message)
            self.assertFalse(target.exists())

    def test_failed_write_to_a_directory_target_names_it_plainly(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "a_directory"
            target.mkdir()
            code, out, err = h.run_cli("validate",
                                       h.corpus_path("S5"),
                                       output_path=target)
            self.assertEqual(code, 2)
            self.assertEqual(out, b"")
            message = err.decode("utf-8", errors="replace")
            self.assertIn(str(target), message)
            self.assertIn("Is a directory", message)
            self.assertNotIn(".dqv-output-", message)
            self.assertNotIn("Errno", message)
            self.assertEqual(sorted(os.listdir(tmp)), ["a_directory"])

    def test_closed_pipe_standard_output_exits_two(self):
        code, err = h.run_cli_closed_pipe("render",
                                          h.corpus_path("S5"))
        self.assertEqual(code, 2)

    def test_closed_descriptor_standard_output_validate_exits_two(self):
        code, out, err = h.run_cli_closed_descriptor(
            ["validate", str(h.corpus_path("S5"))], 1)
        self.assertEqual(code, 2)
        self.assertEqual(out, b"")
        message = err.decode("utf-8", errors="replace")
        self.assertNotIn("Traceback", message)
        self.assertNotIn("AttributeError", message)
        self.assertIn(
            "error: standard output was closed before the output "
            "was delivered", message)

    def test_closed_descriptor_standard_output_render_exits_two(self):
        code, out, err = h.run_cli_closed_descriptor(
            ["render", str(h.corpus_path("S5"))], 1)
        self.assertEqual(code, 2)
        message = err.decode("utf-8", errors="replace")
        self.assertNotIn("Traceback", message)
        self.assertNotIn("AttributeError", message)
        self.assertIn(
            "error: standard output was closed before the output "
            "was delivered", message)

    def test_closed_descriptor_standard_output_file_level_exits_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "invalid.bin"
            target.write_bytes(b"\xff\xfe\x80\x00\x01 not valid text")
            code, out, err = h.run_cli_closed_descriptor(
                ["validate", str(target)], 1)
            self.assertEqual(code, 2)
            message = err.decode("utf-8", errors="replace")
            self.assertNotIn("Traceback", message)
            self.assertNotIn("AttributeError", message)
            self.assertIn(
                "error: standard output was closed before the "
                "output was delivered", message)

    def test_closed_descriptor_stdout_not_read_exits_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "no_such_input.md"
            code, out, err = h.run_cli_closed_descriptor(
                ["validate", str(missing)], 1)
            self.assertEqual(code, 2)
            message = err.decode("utf-8", errors="replace")
            self.assertNotIn("Traceback", message)
            self.assertNotIn("AttributeError", message)
            self.assertIn(
                "error: standard output was closed before the "
                "output was delivered", message)

    def test_named_output_failure_closed_stderr_exits_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "a_directory"
            target.mkdir()
            code, out, err = h.run_cli_closed_descriptor(
                ["validate", str(h.corpus_path("S5")),
                 "--output", str(target)], 2)
            self.assertEqual(code, 2)
            self.assertNotIn(b"Traceback", err)
            self.assertNotIn(b"AttributeError", err)
            self.assertTrue(target.is_dir())

    def test_clean_run_closed_stderr_is_unaffected(self):
        code, out, err = h.run_cli_closed_descriptor(
            ["validate", str(h.corpus_path("S5"))], 2)
        self.assertEqual(code, 0)
        text = out.decode("utf-8", errors="replace")
        self.assertIn("exit 0", text)

    def test_named_output_that_is_a_fifo_exits_two_and_is_preserved(self):
        import stat as _stat
        with tempfile.TemporaryDirectory() as tmp:
            fifo = Path(tmp) / "out_fifo"
            os.mkfifo(fifo)
            before = h.fixture_bytes("S5")
            code, out, err = h.run_cli_with_timeout(
                "validate", h.corpus_path("S5"), output_path=fifo)
            self.assertEqual(code, 2)
            self.assertEqual(out, b"")
            message = err.decode("utf-8", errors="replace")
            self.assertIn(str(fifo), message)
            self.assertTrue(_stat.S_ISFIFO(os.stat(fifo).st_mode))
            self.assertEqual(h.fixture_bytes("S5"), before)
            self.assertEqual(sorted(os.listdir(tmp)), ["out_fifo"])

    def test_named_output_link_to_a_fifo_exits_two_and_is_preserved(self):
        import stat as _stat
        with tempfile.TemporaryDirectory() as tmp:
            fifo = Path(tmp) / "real_fifo"
            os.mkfifo(fifo)
            link = Path(tmp) / "out_link"
            os.symlink(fifo, link)
            code, out, err = h.run_cli_with_timeout(
                "validate", h.corpus_path("S5"), output_path=link)
            self.assertEqual(code, 2)
            message = err.decode("utf-8", errors="replace")
            self.assertIn(str(link), message)
            self.assertTrue(_stat.S_ISFIFO(os.stat(fifo).st_mode))
            self.assertTrue(os.path.islink(link))

    def test_named_output_link_to_third_file_still_replaces_the_link(self):
        # The A-06 guard: a symbolic link named as output, resolving
        # to a separate regular file, still delivers by replacing
        # the link name whole, and the third file is untouched.
        import stat as _stat
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "input.md"
            source.write_bytes(h.fixture_bytes("S5"))
            third = Path(tmp) / "third.md"
            third.write_bytes(b"THIRD PARTY CONTENT\n")
            link = Path(tmp) / "out_link.md"
            os.symlink(third, link)
            code, out, _err = h.run_cli_with_timeout(
                "validate", source, output_path=link)
            self.assertEqual(code, 0)
            self.assertEqual(out, b"")
            self.assertEqual(third.read_bytes(),
                             b"THIRD PARTY CONTENT\n")
            self.assertFalse(os.path.islink(link))
            self.assertTrue(_stat.S_ISREG(os.stat(link).st_mode))
            text = link.read_bytes().decode("utf-8",
                                             errors="replace")
            self.assertIn("exit 0", text)
            self.assertEqual(source.read_bytes(),
                             h.fixture_bytes("S5"))

    def test_stdout_flush_failure_exits_two_without_shutdown_noise(self):
        # Standard output is a regular file in a scratch directory,
        # and its writes are made to fail by a file size limit of
        # zero set on this test process for the run only, the same
        # mechanism test_failed_write_leaves_a_preexisting_output_
        # untouched uses, now aimed at standard output. The limit is
        # restored before any assertion runs. The assertions are on
        # the finished process return code and on the standard error
        # bytes, because the defect lives past the return of the
        # delivery function, at interpreter shutdown.
        with tempfile.TemporaryDirectory() as tmp:
            stdout_path = Path(tmp) / "stdout.txt"
            soft, hard = resource.getrlimit(resource.RLIMIT_FSIZE)
            resource.setrlimit(resource.RLIMIT_FSIZE, (0, hard))
            try:
                code, err = h.run_cli_stdout_redirect(
                    "validate", h.corpus_path("S5"), stdout_path)
            finally:
                resource.setrlimit(resource.RLIMIT_FSIZE, (soft, hard))
            self.assertEqual(code, 2)
            message = err.decode("utf-8", errors="replace")
            self.assertIn(
                "error: standard output was closed before the "
                "output was delivered", message)
            self.assertNotIn("Exception ignored", message)

    def test_named_output_failure_stderr_flush_failure_exits_two(self):
        # A named output failure is reported on standard error, and
        # that report is made to fail at flush time by the file size
        # limit form used above, aimed at the standard error file.
        # The named output names a directory, so the run creates
        # nothing and the limit binds only the report channel.
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "a_directory"
            target.mkdir()
            stderr_path = Path(tmp) / "stderr.txt"
            soft, hard = resource.getrlimit(resource.RLIMIT_FSIZE)
            resource.setrlimit(resource.RLIMIT_FSIZE, (0, hard))
            try:
                code, out = h.run_cli_stderr_redirect(
                    ["validate", str(h.corpus_path("S5")),
                     "--output", str(target)], stderr_path)
            finally:
                resource.setrlimit(resource.RLIMIT_FSIZE, (soft, hard))
            self.assertEqual(code, 2)
            self.assertEqual(out, b"")
            self.assertTrue(target.is_dir())
            self.assertNotIn(
                "Exception ignored",
                stderr_path.read_bytes().decode(
                    "utf-8", errors="replace"))

    def test_stdout_failure_stderr_flush_failure_exits_two(self):
        # The standard output delivery failure form of the existing
        # flush test, with the delivery report on standard error
        # also redirected to a regular file, so the report write
        # fails at flush time under the same limit. Both channels
        # fail; the promised exit code is still 2.
        with tempfile.TemporaryDirectory() as tmp:
            stdout_path = Path(tmp) / "stdout.txt"
            stderr_path = Path(tmp) / "stderr.txt"
            soft, hard = resource.getrlimit(resource.RLIMIT_FSIZE)
            resource.setrlimit(resource.RLIMIT_FSIZE, (0, hard))
            try:
                code, _out = h.run_cli_stderr_redirect(
                    ["validate", str(h.corpus_path("S5"))],
                    stderr_path, stdout_path=stdout_path)
            finally:
                resource.setrlimit(resource.RLIMIT_FSIZE, (soft, hard))
            self.assertEqual(code, 2)
            self.assertNotIn(
                "Exception ignored",
                stderr_path.read_bytes().decode(
                    "utf-8", errors="replace"))

    def test_report_stderr_with_none_stderr_in_process_survives(self):
        import sys as _sys
        shell = h.import_module("shell")
        saved = _sys.stderr
        _sys.stderr = None
        try:
            shell._report_stderr("error: a delivery failure")
        finally:
            _sys.stderr = saved

    def test_closed_descriptor_stdout_refusal_exits_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "input.md"
            source.write_bytes(h.fixture_bytes("S5"))
            code, out, err = h.run_cli_closed_descriptor(
                ["validate", str(source), "--output", str(source)], 1)
            self.assertEqual(code, 2)
            message = err.decode("utf-8", errors="replace")
            self.assertNotIn("Traceback", message)
            self.assertNotIn("AttributeError", message)
            self.assertIn(
                "error: standard output was closed before the "
                "output was delivered", message)
            self.assertEqual(source.read_bytes(),
                             h.fixture_bytes("S5"))

    def test_input_is_byte_identical_after_runs(self):
        for fixture_id in ("S5", "R5", "S13"):
            with self.subTest(fixture=fixture_id):
                before = h.fixture_bytes(fixture_id)
                h.run_cli("validate", h.corpus_path(fixture_id),
                          seed=h.SEED_ONE)
                h.run_cli("render", h.corpus_path(fixture_id),
                          seed=h.SEED_TWO)
                self.assertEqual(h.fixture_bytes(fixture_id), before)

    def test_no_run_record_or_state_files_are_created(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "input.md"
            target.write_bytes(h.fixture_bytes("S5"))
            h.run_cli("validate", target, cwd=tmp)
            names = sorted(os.listdir(tmp))
            self.assertEqual(names, ["input.md"])


class ScaleDoubleRunTest(unittest.TestCase):

    def test_doubled_input_runs_and_its_construction_facts_stand(self):
        data, facts = h.doubled_input()
        self.assertEqual(facts["bytes"], len(data))
        self.assertEqual(facts["lines"], h.count_lines_formula(data))
        self.assertGreater(facts["bytes"], 0)
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "doubled.md"
            target.write_bytes(data)
            for subcommand in ("validate", "render"):
                with self.subTest(subcommand=subcommand):
                    code, out, _err = h.run_cli(subcommand, target)
                    self.assertIn(code, (0, 1, 2, 3, 4))
                    self.assertGreater(len(out), 0)
            self.assertEqual(target.read_bytes(), data)


class DeterminismTest(unittest.TestCase):
    """Seed values 4241 and 9176, as recorded for this suite."""

    def test_every_fixture_is_deterministic_per_subcommand(self):
        for fixture_id in h.FIXTURE_IDS:
            expected = h.expected_exit(fixture_id)
            file_level = expected == 3
            for subcommand in ("validate", "render"):
                with self.subTest(fixture=fixture_id,
                                  subcommand=subcommand):
                    code_one, out_one, _e1 = h.run_cli(
                        subcommand, h.corpus_path(fixture_id),
                        seed=h.SEED_ONE)
                    code_two, out_two, _e2 = h.run_cli(
                        subcommand, h.corpus_path(fixture_id),
                        seed=h.SEED_TWO)
                    self.assertEqual(code_one, code_two)
                    self.assertEqual(code_one, expected)
                    if file_level:
                        head_one = out_one.split(b"\n\n", 1)[0]
                        head_two = out_two.split(b"\n\n", 1)[0]
                        self.assertEqual(head_one, head_two)
                    else:
                        self.assertEqual(out_one, out_two)

    def test_exit2_runs_are_deterministic_on_head_and_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "missing.md"
            code_one, out_one, _e1 = h.run_cli("validate", missing,
                                               seed=h.SEED_ONE)
            code_two, out_two, _e2 = h.run_cli("validate", missing,
                                               seed=h.SEED_TWO)
            self.assertEqual(code_one, 2)
            self.assertEqual(code_one, code_two)
            self.assertEqual(out_one, out_two)


if __name__ == "__main__":
    unittest.main()
