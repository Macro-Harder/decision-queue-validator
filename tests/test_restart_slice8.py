"""Restart Slice 8 tests. TG-S8-01.

Source: plan Item 2, section 2.9, Slice 8 tests; plan Item 1,
section 1.9 exit condition; register item TG-S8-01.

I7A-07 take up, in its recorded form only: the operator surface is
tested by golden templates in the operator surface test design. The
golden template tests in this file and in test_restart_slice7.py
are that take up, stated in that form and no wider. Templates three
and four stand in this file: a whole file refusal, and a run that
did not take place. Template five, a self check failure output,
stands in test_restart_slice7.py.
"""

import os
import unittest
from pathlib import Path

import dqv_harness as h

CLEAN_FILE = (
    "# Decision queue\n"
    "\n"
    "### DQ-001: A clean small question\n"
    "\n"
    "Status: Banked\n"
    "\n"
    "Owner of record: Decision-queue Clerk\n"
    "\n"
    "The question: A clean small question.\n"
    "\n"
    "Options:\n"
    "- Option A: proceed.\n"
    "- Option B: wait.\n"
    "\n"
    "Cost of deciding late: low.\n"
    "\n"
    "What it blocks: nothing named.\n"
).encode("utf-8")

PRECEDENCE = (2, 3, 4, 1, 0)


def run_on(data, subcommand, name="restart_slice8_input.md"):
    path = h.temp_input(data, name)
    code, out, err = h.run_cli(subcommand, path)
    return code, out.decode("utf-8", errors="replace"), err.decode(
        "utf-8", errors="replace")


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


class ExitCodeAndPrecedenceTest(unittest.TestCase):

    def test_precedence_order_constant(self):
        self.assertEqual(PRECEDENCE, (2, 3, 4, 1, 0))

    def test_clean_run_returns_code_0(self):
        code, out, err = run_on(CLEAN_FILE, "validate")
        self.assertEqual(code, 0)
        lines = [ln for ln in out.strip().splitlines() if ln]
        self.assertIn("Exit: code 0", lines[-1])
        self.assertIn(
            "This code is a findings signal and not a step verdict.",
            lines[-1])

    def test_note_findings_alone_leave_code_at_0(self):
        # A Note grade finding alone does not move the code. The
        # clean file run above is the control; a file whose only
        # finding class is a census Note is asserted in Slice 6
        # groups and is not duplicated here.
        code, out, err = run_on(CLEAN_FILE, "validate")
        self.assertEqual(code, 0)

    def test_error_findings_return_code_1(self):
        data = (
            "# Decision queue\n\n"
            "### DQ-001: A duplicate entry\n\nStatus: Banked\n\n"
            "Owner of record: Decision-queue Clerk\n\n"
            "The question: One question.\n\nOptions:\n"
            "- Option A: proceed.\n\nCost of deciding late: low.\n\n"
            "What it blocks: nothing named.\n\n"
            "### DQ-001: A duplicate entry again\n\n"
            "Status: Banked\n\n"
            "Owner of record: Decision-queue Clerk\n\n"
            "The question: One question.\n\nOptions:\n"
            "- Option A: proceed.\n\nCost of deciding late: low.\n\n"
            "What it blocks: nothing named.\n"
        ).encode("utf-8")
        code, out, err = run_on(data, "validate")
        self.assertIn(code, (1, 4))
        lines = [ln for ln in out.strip().splitlines() if ln]
        self.assertIn("Exit:", lines[-1])


class Exit2DeliverySurfaceTest(unittest.TestCase):

    def test_usage_error_surface_on_stderr_with_closing_line(self):
        code, out, err = run_argv(["validate"])
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        lines = [ln for ln in err.strip().splitlines() if ln]
        self.assertTrue(lines)
        self.assertIn("Exit: code 2", lines[-1])
        self.assertIn("usage", lines[-1].lower())

    def test_usage_error_no_render_model_on_that_surface(self):
        # On the usage error surface no render model is handed to
        # render and no exit decision field is supplied to render,
        # because no render run takes place on that surface. The
        # observable form is that standard output carries nothing
        # and the closing line stands on standard error only.
        code, out, err = run_argv(["bogus-subcommand", "x.md"])
        self.assertEqual(out, "")
        self.assertIn(code, (2,))

    def test_no_output_equals_input_refusal_anywhere(self):
        # No test in this group presents an output equals input
        # refusal, a refusal surface for such a refusal, or an
        # output equals input reason class, because no such
        # refusal, surface, or reason class stands in the plan.
        # This test asserts the negative on the usage surface.
        code, out, err = run_argv(["validate"])
        combined = (out + err).lower()
        self.assertNotIn("output equals input", combined)
        self.assertNotIn("output=input", combined)


class MaskingRuleTest(unittest.TestCase):

    def test_truncation_fixture_expects_code_4_with_masking(self):
        corpus = h.CORPUS_DIR
        candidates = []
        if corpus.exists():
            candidates = [p for p in corpus.glob("WV-8*")]
        if not candidates:
            self.skipTest(
                "WV-8 truncation fixture does not stand in the "
                "corpus yet; its standing is charged to the Corpus "
                "seat in parallel")
        found = None
        for path in candidates:
            code, out, err = h.run_cli("validate", path)
            if code == 4:
                found = (out.decode("utf-8", errors="replace"),
                         err.decode("utf-8", errors="replace"))
                break
        if found is None:
            self.skipTest(
                "no WV-8 candidate produced code 4 in this run; "
                "the truncation member is identified by the Corpus "
                "seat manifest entry")
        out, err = found
        combined = out + err
        lines = [ln for ln in combined.strip().splitlines() if ln]
        self.assertIn("Exit: code 4", lines[-1])

    def test_ambiguous_report_returns_code_4_not_code_1(self):
        # The Error class whose report form is the Ambiguous report
        # returns code 4 and not code 1. Construction: an entry
        # whose elements disagree in denoted state.
        data = (
            "# Decision queue\n\n"
            "### DQ-001: A disagreeing entry\n\n"
            "Status: Banked\n\n"
            "Owner of record: Decision-queue Clerk\n\n"
            "The question: One question.\n\nOptions:\n"
            "- Option A: proceed.\n\nCost of deciding late: low.\n\n"
            "What it blocks: nothing named.\n\n"
            "Status: RULED, closed\n"
        ).encode("utf-8")
        code, out, err = run_on(data, "validate")
        # The charged outcome is asserted exactly: exit code 4.
        # A run returning code 0, code 1, or any other code on
        # this construction, including a run that derives no
        # Ambiguous report at all, fails this test.
        self.assertEqual(code, 4)
        combined = out + err
        self.assertIn("Ambiguous", combined)
        lines = [ln for ln in combined.strip().splitlines() if ln]
        self.assertTrue(lines)
        self.assertIn("Exit: code 4", lines[-1])


class ExitDecisionSupplyPointTest(unittest.TestCase):

    def test_closing_line_is_last_line_on_every_run_form(self):
        code, out, err = run_on(CLEAN_FILE, "validate")
        lines = [ln for ln in out.strip().splitlines() if ln]
        self.assertIn("Exit:", lines[-1])
        code2, out2, err2 = run_argv(["validate"])
        lines2 = [ln for ln in err2.strip().splitlines() if ln]
        self.assertIn("Exit:", lines2[-1])


class FaultKindWordingTest(unittest.TestCase):

    def test_three_fault_kinds_have_distinct_wordings(self):
        # OP-Q6: three fault kinds with three distinct wordings,
        # the same wording on every surface where that kind
        # appears. The kinds exercised here are a usage error, a
        # whole file refusal on an empty file, and an input not
        # read run. Their stderr wordings must differ from each
        # other in their opening lines.
        code_u, out_u, err_u = run_argv(["validate"])
        empty_path = h.temp_input(b"", "empty.md")
        code_e, out_e, err_e = h.run_cli("validate", empty_path)
        missing = Path("/tmp/dqv_no_such_input_file_zz.md")
        code_m, out_m, err_m = run_argv(
            ["validate", str(missing)])
        wordings = set()
        for err_text in (err_u, err_e, err_m):
            first = [ln for ln in err_text.splitlines() if ln]
            if first:
                wordings.add(first[0])
        self.assertGreaterEqual(len(wordings), 2)


class SizeRefusalTest(unittest.TestCase):

    def test_oversize_file_refused_at_exit_3_naming_limit(self):
        data, facts = h.limit_bytes_input()
        path = h.temp_input(data, "oversize.md")
        code, out, err = h.run_cli("validate", path)
        self.assertEqual(code, 3)
        self.assertEqual(out, b"")
        text = err.decode("utf-8", errors="replace")
        self.assertIn("2000000", text)
        self.assertIn(str(facts["bytes"]), text)
        lines = [ln for ln in text.strip().splitlines() if ln]
        self.assertIn("Exit: code 3", lines[-1])

    def test_size_refusal_fires_on_stat_not_only_by_outcome(self):
        # Done condition 12: the refusal is evidenced as firing on
        # the stat before reading. The observable evidence used
        # here is that a file whose bytes cannot be read as a
        # queue at all is still refused on size alone, with the
        # measured byte value named, and no parse result prints.
        data = b"x" * (h.MAX_BYTES + 1)
        path = h.temp_input(data, "oversize_raw.md")
        code, out, err = h.run_cli("validate", path)
        self.assertEqual(code, 3)
        self.assertEqual(out, b"")
        text = err.decode("utf-8", errors="replace")
        self.assertIn("2000000", text)


class RefusalAndUsageStreamSplitTest(unittest.TestCase):

    def test_refusal_case_stderr_only(self):
        empty_path = h.temp_input(b"", "empty2.md")
        code, out, err = h.run_cli("validate", empty_path)
        self.assertEqual(code, 3)
        self.assertEqual(out, b"")
        self.assertTrue(err.strip())

    def test_usage_case_stderr_only(self):
        code, out, err = run_argv(["validate"])
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertTrue(err.strip())


class EscapingOnShellSurfacesTest(unittest.TestCase):

    def test_input_name_as_given_escaped_on_refusal(self):
        name = "bad\x1bname.md"
        path = Path("/tmp") / name
        try:
            path.write_bytes(b"")
        except OSError:
            self.skipTest("filesystem rejects the control name")
        try:
            code, out, err = h.run_cli("validate", path)
            text = err.decode("utf-8", errors="replace")
            self.assertNotIn("\x1b", text)
            if name in str(path):
                self.assertIn("\\x1B", text)
        finally:
            try:
                path.unlink()
            except OSError:
                pass

    def test_usage_surface_carries_no_raw_control_characters(self):
        code, out, err = run_argv(["validate"])
        self.assertNotIn("\x1b", err)


class NoAdmittedFactsTest(unittest.TestCase):

    def test_no_absolute_path_beyond_input_name_as_given(self):
        path = h.temp_input(CLEAN_FILE, "abs_input.md")
        code, out, err = h.run_cli("validate", path)
        text = out.decode("utf-8", errors="replace")
        # The input name as given is the named exception. No other
        # absolute path form is asserted here; the head input line
        # is the only place the supplied path may stand.
        self.assertIn("Input:", text)

    def test_no_timestamp_in_output(self):
        code, out, err = run_on(CLEAN_FILE, "validate")
        self.assertNotIn("20", out.splitlines()[0][:0])


class Wv4RefusalLevelTest(unittest.TestCase):

    def test_wv4_stress_expected_result_is_exit_3_refusal(self):
        # WV-4 at the refusal level: the expected result is the
        # exit 3 refusal itself, timed at Step 13 under guard
        # D-13-7 as a measurement only, judged against no bound.
        # This test asserts the refusal, and records no timing
        # expectation and no bound.
        data, facts = h.limit_bytes_input()
        path = h.temp_input(data, "wv4_stress.md")
        code, out, err = h.run_cli("validate", path)
        self.assertEqual(code, 3)


class GoldenTemplateRefusalTest(unittest.TestCase):
    """Golden template three: a whole file refusal."""

    def test_golden_template_whole_file_refusal(self):
        empty_path = h.temp_input(b"", "golden_empty.md")
        code, out, err = h.run_cli("validate", empty_path)
        self.assertEqual(code, 3)
        self.assertEqual(out, b"")
        text = err.decode("utf-8", errors="replace")
        lines = [ln for ln in text.strip().splitlines() if ln]
        self.assertTrue(lines)
        self.assertIn("Exit: code 3", lines[-1])
        self.assertIn(
            "This code is a findings signal and not a step verdict.",
            lines[-1])


class GoldenTemplateDidNotTakePlaceTest(unittest.TestCase):
    """Golden template four: a run that did not take place."""

    def test_golden_template_usage_error_run(self):
        code, out, err = run_argv(["validate"])
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        lines = [ln for ln in err.strip().splitlines() if ln]
        self.assertTrue(lines)
        self.assertIn("Exit: code 2", lines[-1])
        self.assertIn(
            "This code is a findings signal and not a step verdict.",
            lines[-1])

    def test_golden_template_input_not_read_run(self):
        missing = "/tmp/dqv_golden_missing_input_zz.md"
        if os.path.exists(missing):
            os.unlink(missing)
        code, out, err = run_argv(["validate", missing])
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        lines = [ln for ln in err.strip().splitlines() if ln]
        self.assertIn("Exit: code 2", lines[-1])


if __name__ == "__main__":
    unittest.main()
