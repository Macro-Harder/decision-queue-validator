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


class ExitThreeHeadFormTest(unittest.TestCase):

    def test_exit3_file_facts_form(self):
        code, out, _err = h.cached_run("S10", "validate")
        self.assertEqual(code, 3)
        text = out.decode("utf-8", errors="replace")
        self.assertIn("S10.md", text)
        self.assertIn("entry count: not parsed", text)
        digest_fragment = h.sha256_hex(h.fixture_bytes("S10"))[:12]
        self.assertIn(digest_fragment, text)

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

    def test_closed_pipe_standard_output_exits_two(self):
        code, err = h.run_cli_closed_pipe("render",
                                          h.corpus_path("S5"))
        self.assertEqual(code, 2)

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
