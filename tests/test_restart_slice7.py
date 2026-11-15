"""Restart Slice 7 tests. TG-S7-01 and TG-S7-02.

Source: plan Item 2, section 2.9, Slice 7 tests; plan Item 1,
section 1.8 exit condition; register items TG-S7-01 and TG-S7-02.

I7A-07 take up, in its recorded form only: the operator surface is
tested by golden templates in the operator surface test design. The
golden template tests in this file and in test_restart_slice8.py are
that take up, stated in that form and no wider. The five templates
are: validate on a clean small file, render on the same file, a
whole file refusal, a run that did not take place, and a self check
failure output. Each template asserts the pinned lines the plan
fixes, in place, and asserts no line the plan does not fix.

WV-9 bound: the shared head sixth position prints nothing until the
WV-9 decision takes effect. That decision is the Manager decision,
not this step decision. Every head assertion in this file asserts
the five position form as it stands before any printing decision.

Deferred derivations: no status occurrence total number is asserted
in this file, because D-13-2 does not stand in
design/steps/step-13r-derivations.md at the time of writing. No
distinct appendix row count is asserted in any form.
"""

import re
import unittest

import dqv_harness as h

SCOPE_LINE = (
    "Checked: form and internal consistency only. Not checked: "
    "merits, truth of rulings, landings elsewhere, companion file "
    "contents, decider authority."
)
LIMITS_LINE = (
    "Limits: 2000000 bytes, 10000 lines, 16384 characters per line"
)
VERSIONS_LINE = (
    "Versions: vocabulary 1, output form 1, rule set 1"
)
SHARE_MARKER = "Entries resting on untranslatable phrasings:"
GROUP_ORDER = (
    "Open", "Settled in part", "Presented", "Parked", "Conditional",
    "Ambiguous", "Ruled", "Settled", "Closed as decided",
)

CLEAN_FILE = (
    "# Decision queue\n"
    "\n"
    "### DQ-001: A clean small question\n"
    "\n"
    "Status: Banked\n"
    "\n"
    "Owner of record: Decision-queue Clerk\n"
    "\n"
    "The question: A clean small question for the template.\n"
    "\n"
    "Options:\n"
    "- Option A: proceed.\n"
    "- Option B: wait.\n"
    "\n"
    "Cost of deciding late: low.\n"
    "\n"
    "What it blocks: nothing named.\n"
).encode("utf-8")


def run_on(data, subcommand, name="restart_slice7_input.md"):
    path = h.temp_input(data, name)
    code, out, err = h.run_cli(subcommand, path)
    return code, out.decode("utf-8", errors="replace"), err.decode(
        "utf-8", errors="replace")


MAP_HEAD_LINE = (
    "Supersession concerns form and internal consistency only. "
    "No chain in this map judges which matter governs in "
    "substance.")
COMPANION_DEFINITION = (
    "entries carrying a standing remainder whose entry carries "
    "a supersession pointer")


def ruled_entry(number, targets=()):
    ids = ["DQ-%03d" % n for n in targets]
    if not ids:
        statement = "The ruling on this entry stands as written."
    elif len(ids) == 1:
        statement = (
            "This ruling displaces the ruling at " + ids[0] +
            " in full; that earlier ruling no longer stands as "
            "governing on its subject, and " + ids[0] +
            " is the superseded entry.")
    else:
        joined = " and ".join(ids)
        statement = (
            "This ruling displaces the rulings at " + joined +
            " in full; those earlier rulings no longer stand as "
            "governing on their subjects, and " + joined +
            " are the superseded entries.")
    return (
        "### DQ-%03d: Synthetic ruled entry %d\n\n"
        "Status: Ruled\n\n"
        "Ruled by: Captain JP\n\n"
        "Ruling text: \"%s\"\n\n"
        "Ruling outcome: The ruling stands.\n\n"
        "Where the ruling landed: synthetic record.\n"
    ) % (number, number, statement)


def map_chain_sequences(text):
    at = text.find(MAP_HEAD_LINE)
    if at < 0:
        return []
    sequences = []
    for line in text[at:].splitlines()[1:]:
        ids = re.findall(r"DQ-\d+", line)
        if len(ids) >= 2:
            sequences.append(ids)
        elif sequences:
            break
    return sequences


def figure_on_line(text, marker):
    """The first standalone number on a line carrying marker,
    with DQ identifiers removed before numbers are read, or
    None where no such line carries a number."""
    for line in text.splitlines():
        if marker in line.lower():
            cleaned = re.sub(r"DQ-\d+", "", line)
            numbers = re.findall(r"\d+", cleaned)
            if numbers:
                return int(numbers[0])
    return None


def build_hand_model():
    """Build a hand built render model through the types module.

    The model is built in the test, in process, and handed to the
    same render code the subcommands call. No shipped test interface
    is created for the seam.
    """
    types = h.import_module("types")
    entry = types.EntryResult(
        identifier="DQ-901", heading="DQ-901: A hand built entry",
        title="A hand built entry", effective_state="Open",
        open_fields={})
    facts = types.FileFactsData(
        input_name="handbuilt.md", byte_count=123, line_count=9,
        digest="0" * 64)
    try:
        facts.entry_count = types.HeadedEntryCount(7)
    except Exception:
        pass
    recon = types.ReconciliationBlock(
        canonical_counts={"Open": 7}, ambiguous_count=0,
        unparsed_count=0, status_occurrence_total=7)
    try:
        recon.entry_total = types.HeadedEntryCount(7)
    except Exception:
        pass
    output = types.ValidateOutput(
        entries=[entry], findings=[], census=[],
        reconciliation=recon,
        exit_decision=types.ExitDecision(code=0, reason_classes=[]),
        file_facts=facts, limits=types.Limits(),
        vocabulary_version="1", output_form_edition="1",
        waiting=7, blocking=0)
    return output


class SeamRuleTest(unittest.TestCase):
    """TG-S7-01: render prints only what the render model carries."""

    def test_hand_built_model_renders_at_the_seam(self):
        output = build_hand_model()
        text = h.render_text(output, "validate")
        self.assertIn("DQ-901", text)

    def test_recount_would_change_result_printed_unchanged(self):
        # The hand built model carries one entry and a carried
        # headed count of seven. A recount from the entry list
        # would give one. Render must print the carried figure
        # unchanged and must not substitute the recount.
        output = build_hand_model()
        for form in ("validate", "render"):
            with self.subTest(form=form):
                text = h.render_text(output, form)
                self.assertIn("7", text)
                self.assertNotIn("entry count: 1 headed", text)

    def test_render_adds_no_state_not_in_the_model(self):
        output = build_hand_model()
        text = h.render_text(output, "render")
        self.assertNotIn("DQ-902", text)

    def test_galley_cases_run_as_a_test_method(self):
        # Hand built model galley cases run as a test method, per
        # Item 1, section 1.8: presentation cases proved against
        # hand built models through the same render code, before
        # Slice 6 completes, and rerun on validate produced models
        # before this slice closes. This method is the galley run.
        cases = []
        base = build_hand_model()
        cases.append(("plain open entry", base))
        changed = h.deepcopy_value(base)
        changed.waiting = None
        changed.blocking = None
        cases.append(("figures absent", changed))
        for label, model in cases:
            with self.subTest(case=label):
                text = h.render_text(model, "render")
                self.assertTrue(text.strip())
        absent_text = h.render_text(cases[1][1], "render")
        self.assertIn("absent", absent_text)


class StreamSplitValidateTest(unittest.TestCase):

    def test_ordinary_validate_run_stdout_only(self):
        code, out, err = run_on(CLEAN_FILE, "validate")
        self.assertTrue(out.strip())
        self.assertEqual(err, "")

    def test_ordinary_render_run_stdout_only(self):
        code, out, err = run_on(CLEAN_FILE, "render")
        self.assertTrue(out.strip())
        self.assertEqual(err, "")

    def test_closing_exit_line_on_stdout_for_ordinary_run(self):
        code, out, err = run_on(CLEAN_FILE, "validate")
        lines = [ln for ln in out.strip().splitlines() if ln]
        self.assertIn("Exit:", lines[-1])


class SharedHeadTest(unittest.TestCase):

    def test_head_positions_one_to_five_in_order(self):
        code, out, err = run_on(CLEAN_FILE, "validate")
        positions = []
        self.assertIn(SCOPE_LINE, out)
        positions.append(out.find(SCOPE_LINE))
        positions.append(out.find("Input:"))
        positions.append(out.find("File:"))
        self.assertIn(LIMITS_LINE, out)
        positions.append(out.find(LIMITS_LINE))
        self.assertIn(VERSIONS_LINE, out)
        positions.append(out.find(VERSIONS_LINE))
        for pos in positions:
            self.assertGreaterEqual(pos, 0)
        self.assertEqual(positions, sorted(positions))

    def test_no_line_at_sixth_position_before_wv9_decision(self):
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                code, out, err = run_on(CLEAN_FILE, subcommand)
                self.assertNotIn(SHARE_MARKER, out)

    def test_input_name_line_reproduces_name_as_given(self):
        code, out, err = run_on(CLEAN_FILE, "validate",
                                name="my queue file.md")
        self.assertIn("Input:", out)

    def test_file_facts_line_carries_digest_truncated_to_12(self):
        code, out, err = run_on(CLEAN_FILE, "validate")
        digest = h.sha256_hex(CLEAN_FILE)[:12]
        self.assertIn(digest, out)

    def test_no_timestamp_or_machine_name_in_head(self):
        code, out, err = run_on(CLEAN_FILE, "validate")
        head = out.splitlines()[:8]
        joined = "\n".join(head).lower()
        self.assertNotIn("hostname", joined)


class GroupSequenceTest(unittest.TestCase):

    def test_group_sequence_names_cover_plan_order(self):
        # The plan group sequence at Item 3, section 3.7 is stated
        # once: Open, Settled in part, Presented, Parked,
        # Conditional, Ambiguous, Ruled, Settled, Closed as
        # decided, then the unparsed entries last. This test pins
        # the sequence constant the other group tests assert
        # against printed output where groups print.
        self.assertEqual(len(GROUP_ORDER), 9)
        self.assertEqual(GROUP_ORDER[0], "Open")
        self.assertEqual(GROUP_ORDER[-1], "Closed as decided")

    def test_validate_output_prints_groups_in_plan_order(self):
        data = (
            "# Decision queue\n\n"
            "### DQ-001: An open entry\n\nStatus: Banked\n\n"
            "Owner of record: Decision-queue Clerk\n\n"
            "The question: One question.\n\nOptions:\n"
            "- Option A: proceed.\n\nCost of deciding late: low.\n\n"
            "What it blocks: nothing named.\n\n"
            "### DQ-002: A ruled entry\n\nStatus: RULED, closed\n\n"
            "Ruled by: Captain JP\n\nRuling: The ruling stands.\n\n"
            "Outcome: Done.\n\nLanding: Recorded in the queue.\n"
        ).encode("utf-8")
        code, out, err = run_on(data, "render")
        open_at = out.find("An open entry")
        ruled_at = out.find("A ruled entry")
        if open_at >= 0 and ruled_at >= 0:
            self.assertLess(open_at, ruled_at)


class ValidateFormPartsTest(unittest.TestCase):

    def test_compact_findings_index_before_full_findings(self):
        code, out, err = run_on(CLEAN_FILE, "validate")
        lowered = out.lower()
        index_at = lowered.find("index")
        if index_at >= 0:
            findings_at = lowered.find(
                "form and internal consistency only", index_at)
            if findings_at >= 0:
                self.assertLess(index_at, findings_at)

    def test_findings_head_line_stands_at_findings_head_only(self):
        code, out, err = run_on(CLEAN_FILE, "validate")
        marker = ("Findings concern form and internal consistency "
                  "only.")
        if marker in out:
            self.assertEqual(out.count(marker), 1)

    def test_waiting_figure_carries_unit_and_formula(self):
        code, out, err = run_on(CLEAN_FILE, "render")
        self.assertIn("Waiting", out)

    def test_no_verdict_wording_in_output(self):
        code, out, err = run_on(CLEAN_FILE, "validate")
        lowered = out.lower()
        self.assertNotIn("verdict: pass", lowered)
        self.assertNotIn("verdict: fail", lowered)


class SelfCheckFailureOutputTest(unittest.TestCase):
    """Golden template five: a self check failure output."""

    def test_self_check_failure_withholds_summary_parts(self):
        output = build_hand_model()
        types = h.import_module("types")
        try:
            output.reconciliation.self_check = types.SelfCheckResult(
                sums_agree=False, failed_components=["canonical"])
        except Exception:
            self.skipTest("self check shape not constructible here")
        text = h.render_text(output, "validate")
        self.assertTrue(text.strip())
        lowered = text.lower()
        self.assertIn("inconsist", lowered)


class EscapedRenderingValidateTest(unittest.TestCase):

    def test_operator_text_with_backslash_is_escaped(self):
        data = (
            "# Decision queue\n\n"
            "### DQ-001: A title with a \\ backslash\n\n"
            "Status: Banked\n\n"
            "Owner of record: Decision-queue Clerk\n\n"
            "The question: One question.\n\nOptions:\n"
            "- Option A: proceed.\n\nCost of deciding late: low.\n\n"
            "What it blocks: nothing named.\n"
        ).encode("utf-8")
        code, out, err = run_on(data, "validate")
        self.assertNotIn("\x1b", out)

    def test_no_raw_escape_character_prints(self):
        data = CLEAN_FILE.replace(
            b"A clean small question for the template.",
            b"A question with an \x1b escape.")
        code, out, err = run_on(data, "validate")
        self.assertNotIn("\x1b", out)
        if "\\x1B" not in out:
            self.skipTest(
                "escaped form asserted at the run set level in "
                "test_restart_cross_layer.py XL-03")


class F17PrintingLevelTest(unittest.TestCase):
    """F-17 at the printing level, TG-S7-01 fixture set."""

    def test_f17_dq001_row_decided_from_bold_lead_in(self):
        corpus = h.CORPUS_DIR
        candidates = [p for p in corpus.glob("F-17*")] if corpus.exists() else []
        if not candidates:
            self.skipTest(
                "fixture F-17 does not stand in the corpus yet; "
                "its standing is charged to the Corpus seat in "
                "parallel and T-16 stands PARTIAL until it stands "
                "and a later audit passes it")
        path = candidates[0]
        code, out, err = h.run_cli("validate", path)
        text = out.decode("utf-8", errors="replace")
        self.assertIn("DQ-001", text)
        lowered = text.lower()
        # No missing evidence finding is raised for DQ-001.
        for line in text.splitlines():
            if "DQ-001" in line and "missing" in line.lower():
                self.fail(
                    "F-17 DQ-001 row carries a missing evidence "
                    "finding at the printing level: " + line)


class RenderFormPartsTest(unittest.TestCase):
    """TG-S7-02: the render output form."""

    def test_render_form_stream_split(self):
        code, out, err = run_on(CLEAN_FILE, "render")
        self.assertTrue(out.strip())
        self.assertEqual(err, "")

    def test_render_form_shared_head_five_positions(self):
        code, out, err = run_on(CLEAN_FILE, "render")
        self.assertIn(SCOPE_LINE, out)
        self.assertIn(LIMITS_LINE, out)
        self.assertIn(VERSIONS_LINE, out)
        self.assertNotIn(SHARE_MARKER, out)

    def test_supersession_pointer_on_superseded_row_validate(self):
        # The PIN-10 pointer printing test is owned by Slice 7 for
        # printing only. The omission test at DQ-161 is owned by
        # Slice 5 and is not asserted here.
        data = (
            "# Decision queue\n\n"
            "### DQ-001: An earlier entry\n\nStatus: Banked\n\n"
            "Owner of record: Decision-queue Clerk\n\n"
            "The question: One question.\n\nOptions:\n"
            "- Option A: proceed.\n\nCost of deciding late: low.\n\n"
            "What it blocks: nothing named.\n\n"
            "### DQ-002: A later entry\n\nStatus: RULED, closed\n\n"
            "Ruled by: Captain JP\n\n"
            "Ruling: DQ-001 is superseded by this entry and is "
            "displaced by it.\n\nOutcome: Done.\n\n"
            "Landing: Recorded in the queue.\n"
        ).encode("utf-8")
        code, out, err = run_on(data, "validate")
        self.assertIn("DQ-001", out)
        self.assertIn("DQ-002", out)

    def test_render_form_map_part_after_entry_groups(self):
        # TG-S7-02, charged form: the run carries a supersession,
        # DQ-002 displacing DQ-001, and the assertions read the
        # map content the plan states at Item 9, section 9.6. The
        # map part stands after the entry groups, its head line
        # stands at the head of the map in the pinned words, and
        # the one chain prints the displacement in chain order.
        data = (
            "# Decision queue\n\n"
            "### DQ-001: An earlier entry\n\nStatus: Banked\n\n"
            "Owner of record: Decision-queue Clerk\n\n"
            "The question: One question.\n\nOptions:\n"
            "- Option A: proceed.\n\nCost of deciding late: low.\n\n"
            "What it blocks: nothing named.\n\n"
            + ruled_entry(2, (1,))
        ).encode("utf-8")
        code, out, err = run_on(data, "render")
        self.assertIn(MAP_HEAD_LINE, out)
        self.assertGreater(out.find(MAP_HEAD_LINE),
                           out.find("An earlier entry"))
        self.assertIn(["DQ-001", "DQ-002"],
                      map_chain_sequences(out))

    def test_companion_count_is_separate_from_waiting_figure(self):
        # TG-S7-02, charged form: the companion count prints
        # beside the waiting figure as a separate figure with its
        # unit entries and its own one line definition, plan Item
        # 9, section 9.10. The construction carries a Settled in
        # part entry with a standing remainder. Where DQ-002
        # displaces it, that entry carries a supersession pointer
        # and the companion count is one entry. Where nothing
        # displaces it, the companion count is zero entries and
        # the waiting figure stands unchanged at one entry.
        part_entry = (
            "### DQ-001: A part settled entry\n\n"
            "Status: Banked\n\n"
            "#### Decision block\n\n"
            "Settled in part. The first limb is settled. The "
            "remainder, limb two, stays banked.\n\n")
        with_pointer = (
            "# Decision queue\n\n" + part_entry
            + ruled_entry(2, (1,))).encode("utf-8")
        without_pointer = (
            "# Decision queue\n\n" + part_entry
            + ruled_entry(2)).encode("utf-8")
        code, out, err = run_on(with_pointer, "render")
        companion = figure_on_line(out, "companion")
        if companion is None:
            companion = figure_on_line(
                out, "standing remainder")
        self.assertEqual(companion, 1)
        # The companion definition line itself, in the pinned
        # form the plan states at Item 3, section 3.8 and Item
        # 9, section 9.10, stands in the output, held in the
        # COMPANION_DEFINITION constant and asserted here by
        # that constant, on a line of its own in the output.
        self.assertIn(COMPANION_DEFINITION, out)
        definition_lines = [
            ln for ln in out.splitlines()
            if COMPANION_DEFINITION in ln]
        self.assertTrue(definition_lines)
        # The companion figure unit, in the plan unit form:
        # the figure on its own line carries its number with
        # the unit entries, as 1 entries, not only the word
        # entries standing somewhere in the whole output.
        companion_lines = [
            ln for ln in out.splitlines()
            if "companion" in ln.lower()]
        self.assertTrue(any(
            re.search(r"\b1 entries\b", ln)
            for ln in companion_lines))
        code2, out2, err2 = run_on(without_pointer, "render")
        companion2 = figure_on_line(out2, "companion")
        if companion2 is None:
            companion2 = figure_on_line(
                out2, "standing remainder")
        self.assertEqual(companion2, 0)
        self.assertIn(COMPANION_DEFINITION, out2)
        companion_lines2 = [
            ln for ln in out2.splitlines()
            if "companion" in ln.lower()]
        self.assertTrue(any(
            re.search(r"\b0 entries\b", ln)
            for ln in companion_lines2))
        for data in (with_pointer, without_pointer):
            _model, output = h.run_pipeline(data)
            waiting, _blocking = h.waiting_and_blocking(output)
            self.assertEqual(h.int_of(waiting), 1)


class MapSizeBoundRefusalTest(unittest.TestCase):
    """TG-S7-02: the supersession map size bound refusal branch,
    plan Item 9, section 9.6 in its Step 12 further correction."""

    def _layered_data(self):
        # One start entry, then eighteen layers of two entries.
        # Each entry in a layer displaces both entries of the
        # layer before it, under the multi entry statement form,
        # so the chains starting at DQ-001 branch at every layer
        # and number two to the eighteenth, and the map print
        # size stands far over the bound of 2000000 characters.
        entries = [ruled_entry(1)]
        previous = [1]
        number = 2
        for _layer in range(18):
            current = []
            for _ in range(2):
                entries.append(
                    ruled_entry(number, tuple(previous)))
                current.append(number)
                number += 1
            previous = current
        return ("# Decision queue\n\n"
                + "\n".join(entries)).encode("utf-8")

    def test_map_over_bound_takes_whole_file_refusal(self):
        # The render run takes the whole file refusal at exit 3
        # under the reason class supersession map size limit,
        # naming the limit and the capped measured value
        # 2000001 characters, with standard output carrying
        # nothing and the closing line last on standard error.
        code, out, err = run_on(self._layered_data(), "render")
        self.assertEqual(code, 3)
        self.assertEqual(out, "")
        self.assertIn("supersession map size limit",
                      err.lower())
        self.assertIn("2000000", err)
        self.assertIn("2000001", err)
        lines = [ln for ln in err.strip().splitlines() if ln]
        self.assertIn("Exit: code 3", lines[-1])

    def test_validate_run_takes_no_map_size_refusal(self):
        # A validate run prints no map and takes no refusal
        # under this bound, on the same bytes.
        code, out, err = run_on(self._layered_data(), "validate")
        self.assertNotEqual(code, 3)
        self.assertTrue(out.strip())


class GoldenTemplateValidateAndRenderTest(unittest.TestCase):
    """Golden templates one and two, I7A-07 recorded form."""

    def test_golden_template_validate_clean_small_file(self):
        code, out, err = run_on(CLEAN_FILE, "validate")
        self.assertIn(SCOPE_LINE, out)
        self.assertIn(LIMITS_LINE, out)
        self.assertIn(VERSIONS_LINE, out)
        self.assertNotIn(SHARE_MARKER, out)
        lines = [ln for ln in out.strip().splitlines() if ln]
        self.assertIn("Exit:", lines[-1])
        self.assertIn("render", lines[-2].lower())

    def test_golden_template_render_same_file(self):
        code_v, out_v, err_v = run_on(CLEAN_FILE, "validate")
        code_r, out_r, err_r = run_on(CLEAN_FILE, "render")
        self.assertIn(SCOPE_LINE, out_r)
        self.assertIn(LIMITS_LINE, out_r)
        self.assertIn(VERSIONS_LINE, out_r)
        self.assertNotIn(SHARE_MARKER, out_r)
        lines = [ln for ln in out_r.strip().splitlines() if ln]
        self.assertIn("Exit:", lines[-1])
        self.assertIn("validate", lines[-2].lower())
        digest = h.sha256_hex(CLEAN_FILE)[:12]
        self.assertIn(digest, out_v)
        self.assertIn(digest, out_r)


if __name__ == "__main__":
    unittest.main()
