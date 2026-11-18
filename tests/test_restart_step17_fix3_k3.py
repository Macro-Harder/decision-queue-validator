"""Step 17 fix wave 3, Fix Seat K3 tests.

Charges CH-50 and CH-51, ruled at section 26 of
design/steps/step-17r-record.md under flag rulings (c) and (l),
prepared at design/steps/step-17r-triage3-prep.md, findings at
design/steps/step-17r-attack3-20.md (F-20-3-1 to F-20-3-4, all
High).

CH-50: the output reuse guard recognises whatever the
disposition reading denotes, at the disposition reading own
width, neither wider nor narrower. The count row joints beyond
spaces and tabs, the count in the digit forms and word forms
the disposition reading accepts, decoration standing between
the words of a row, and group heading forms beyond the one
exact sentence form (trailing punctuation other than a period,
internal respacing) all take the guard.

CH-51: crosswalk and verbatim appendix tally rows take the
guard on the same terms as the count rows and group headings,
so a reused tally row does not denote a disposition for the
entry it is reused inside.

Both directions are pinned in this file. Recognition: the
charged rows denote nothing, and the host entry stays Open.
Confinement: a genuine ruling standing on the same line as a
guarded row, before it or after it, still counts, in the
widened forms as in the round 2 forms. The standing of seat 20
observation O-3-20-1 is pinned unmoved: quoted genuine ruling
lines still denote for their host entry, on the crosswalk,
appendix, residue, and segment claim surfaces alike.

Copyright: J.P. Picard aka Macro-Harder
"""

import unittest

import dqv_harness as h


def _k3_entry(extra_body=""):
    """The seat 20 control base: one Banked entry, DQ-001."""
    body = h._header_block()
    body += "### DQ-001: A sample open question\n\n"
    body += "Status: Banked\n\n"
    body += "This question is waiting for a decision.\n\n"
    body += "Question: Which option should we take?\n\n"
    body += "Options: Option A, Option B\n\n"
    body += "Cost of deciding late: Work stays blocked.\n\n"
    body += "Blocks: none\n"
    body += extra_body
    return body.encode("utf-8")


def _k3_elements(model, entry_id="DQ-001"):
    entry = h.entry_by_id(model, entry_id)
    if entry is None:
        return []
    return h.as_list(h.get(entry, "status_elements", "elements"))


def _k3_dispositions(model, entry_id="DQ-001"):
    out = []
    for el in _k3_elements(model, entry_id):
        tup = h.get(el, "tuple", "element_tuple", "core_tuple")
        out.append(h.text_of(tuple(tup)[0]) if tup is not None
                   else h.text_of(h.get(el, "disposition")))
    return out


def _k3_state(extra_body, name="k3_case.md"):
    model, output = h.run_pipeline(_k3_entry(extra_body), name)
    result = h.entry_by_id(output, "DQ-001")
    return model, h.entry_state(result)


class Step17Fix3K3JointAndCountTest(unittest.TestCase):
    """CH-50, F-20-3-1: joints and counts at the disposition
    reading own width."""

    def test_f20_3_1_wide_joint_rows_denote_no_disposition(self):
        rows = (
            "Canonical Ruled: 0 entries",
            "Canonical Ruled: 0 entries",
            "Canonical\u200bRuled: 0 entries",
            "Canonical\x0bRuled: 0 entries",
            "Canonical state: Ruled: 0 entries",
            "Canonical state: Ruled: 0 entries",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _k3_state("\n" + row + "\n")
                self.assertNotIn("Ruled", _k3_dispositions(model))
                self.assertNotIn("Settled", _k3_dispositions(model))
                self.assertEqual(state, "Open")

    def test_f20_3_1_count_forms_denote_no_disposition(self):
        rows = (
            "Canonical Ruled: ٠ entries",
            "Canonical Ruled: ０ entries",
            "Canonical Ruled: zero entries",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _k3_state("\n" + row + "\n")
                self.assertNotIn("Ruled", _k3_dispositions(model))
                self.assertEqual(state, "Open")


class Step17Fix3K3SplitDecorationTest(unittest.TestCase):
    """CH-50, F-20-3-2: decoration between the words of a row."""

    def test_f20_3_2_split_decoration_rows_denote_nothing(self):
        rows = (
            "Canonical **Ruled: 0 entries**",
            "*Canonical* Ruled: 0 entries",
            "`Canonical` Ruled: 0 entries",
            "[Canonical] Ruled: 0 entries",
            "Canonical **state: Ruled: 0 entries**",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _k3_state("\n" + row + "\n")
                self.assertNotIn("Ruled", _k3_dispositions(model))
                self.assertNotIn("Settled", _k3_dispositions(model))
                self.assertEqual(state, "Open")


class Step17Fix3K3GroupHeadingFormTest(unittest.TestCase):
    """CH-50, F-20-3-3: group headings beyond the one exact
    sentence form."""

    def test_f20_3_3_punctuated_headings_denote_nothing(self):
        cases = (
            ("Ruled group!", "Ruled"),
            ("Ruled group:", "Ruled"),
            ("Ruled group,", "Ruled"),
            ("Settled group!", "Settled"),
            ("Closed as decided group!", "Closed"),
            ("Parked group:", "Parked"),
        )
        for heading, word in cases:
            with self.subTest(heading=heading):
                model, state = _k3_state("\n" + heading + "\n")
                self.assertNotIn(word, _k3_dispositions(model))
                self.assertEqual(state, "Open")

    def test_f20_3_3_respaced_headings_denote_nothing(self):
        cases = (
            ("Ruled  group", "Ruled"),
            ("Ruled\tgroup", "Ruled"),
            ("Ruled group", "Ruled"),
        )
        for heading, word in cases:
            with self.subTest(heading=heading):
                model, state = _k3_state("\n" + heading + "\n")
                self.assertNotIn(word, _k3_dispositions(model))
                self.assertEqual(state, "Open")

    def test_f20_3_3_respaced_settled_in_part_stays_open(self):
        model, state = _k3_state("\nSettled in part  group\n")
        self.assertNotIn("Settled", _k3_dispositions(model))
        self.assertEqual(state, "Open")


class Step17Fix3K3TallySurfaceTest(unittest.TestCase):
    """CH-51, F-20-3-4: crosswalk and verbatim appendix tally
    rows take the guard."""

    def test_f20_3_4_crosswalk_rows_denote_no_disposition(self):
        cases = (
            ("Ruled: Ruled 1, total 1", "Ruled"),
            ("Settled: Settled 1, total 1", "Settled"),
        )
        for row, word in cases:
            with self.subTest(row=row):
                model, state = _k3_state("\n" + row + "\n")
                self.assertNotIn(word, _k3_dispositions(model))
                self.assertEqual(state, "Open")

    def test_f20_3_4_appendix_rows_denote_no_disposition(self):
        cases = (
            ("Ruled | line start | 1 occurrence | entries: DQ-001",
             "Ruled"),
            ("Settled | line start | 1 occurrence | entries: DQ-001",
             "Settled"),
        )
        for row, word in cases:
            with self.subTest(row=row):
                model, state = _k3_state("\n" + row + "\n")
                self.assertNotIn(word, _k3_dispositions(model))
                self.assertEqual(state, "Open")


class Step17Fix3K3ConfinementTest(unittest.TestCase):
    """Both charges, confinement direction: the widened guard
    stays segment aware under the CH-15 confinement pin, so a
    genuine ruling on the same line as a guarded row counts."""

    def test_confinement_ruling_before_row_counts(self):
        model, state = _k3_state(
            "\nRuled by Captain JP: take Option A. Canonical "
            "Ruled: 0 entries\n")
        self.assertIn("Ruled", _k3_dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_confinement_ruling_after_row_comma_counts(self):
        model, state = _k3_state(
            "\nCanonical Ruled: 0 entries, Ruled by Captain JP: "
            "take Option A.\n")
        self.assertIn("Ruled", _k3_dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_confinement_ruling_after_row_no_break_counts(self):
        model, state = _k3_state(
            "\nCanonical Ruled: 0 entries Ruled by Captain JP: "
            "take Option A.\n")
        self.assertIn("Ruled", _k3_dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_confinement_cross_state_ruling_counts(self):
        model, state = _k3_state(
            "\nCanonical Settled: 0 entries. Ruled by Captain JP: "
            "take Option A.\n")
        self.assertNotIn("Settled", _k3_dispositions(model))
        self.assertIn("Ruled", _k3_dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_confinement_ruled_the_entry_after_row_counts(self):
        model, state = _k3_state(
            "\nCanonical Ruled: 0 entries is wrong; Captain JP "
            "ruled the entry, take Option A.\n")
        self.assertIn("Ruled", _k3_dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_confinement_two_rows_then_ruling_counts(self):
        model, state = _k3_state(
            "\nCanonical Ruled: 0 entries. Canonical Settled: 0 "
            "entries. Ruled by Captain JP: take Option A.\n")
        self.assertNotIn("Settled", _k3_dispositions(model))
        self.assertIn("Ruled", _k3_dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_confinement_row_inside_ruling_sentence_counts(self):
        model, state = _k3_state(
            "\nCaptain JP ruled the entry, noting Canonical "
            "Ruled: 0 entries in the report.\n")
        self.assertIn("Ruled", _k3_dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_confinement_heading_and_ruling_one_sentence(self):
        model, state = _k3_state(
            "\nRuled group and Ruled by Captain JP: take "
            "Option A.\n")
        self.assertIn("Ruled", _k3_dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_confinement_heading_sentence_then_ruling(self):
        model, state = _k3_state(
            "\nRuled group. Ruled by Captain JP: take Option A.\n")
        self.assertIn("Ruled", _k3_dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_confinement_widened_row_then_ruling_counts(self):
        model, state = _k3_state(
            "\nCanonical Ruled: 0 entries. Ruled by Captain JP: "
            "take Option A.\n")
        self.assertIn("Ruled", _k3_dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_confinement_tally_row_then_ruling_counts(self):
        model, state = _k3_state(
            "\nRuled: Ruled 1, total 1. Ruled by Captain JP: "
            "take Option A.\n")
        self.assertIn("Ruled", _k3_dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_confinement_appendix_row_then_ruling_counts(self):
        model, state = _k3_state(
            "\nRuled | line start | 1 occurrence | entries: "
            "DQ-001. Ruled by Captain JP: take Option A.\n")
        self.assertIn("Ruled", _k3_dispositions(model))
        self.assertEqual(state, "Ruled")


class Step17Fix3K3QuotedRulingStandingTest(unittest.TestCase):
    """Observation O-3-20-1 standing, unmoved by this cure:
    quoted genuine ruling lines still denote for their host
    entry, on every surface the round measured."""

    def test_o3_20_1_crosswalk_quoted_ruling_still_denotes(self):
        model, state = _k3_state(
            "\nRuled: take Option A: Ruled 1, total 1\n")
        self.assertIn("Ruled", _k3_dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_o3_20_1_appendix_quoted_ruling_still_denotes(self):
        model, state = _k3_state(
            "\nRuled: take Option A | line start | 1 occurrence "
            "| entries: DQ-001\n")
        self.assertIn("Ruled", _k3_dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_o3_20_1_appendix_decider_label_still_denotes(self):
        model, state = _k3_state(
            "\nRuled by Captain JP | line start | 1 occurrence "
            "| entries: DQ-001\n")
        self.assertIn("Ruled", _k3_dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_o3_20_1_appendix_pending_phrasing_still_denotes(self):
        model, state = _k3_state(
            "\nPending Ruled: take Option A | line start | 1 "
            "occurrence | entries: DQ-001 | unclassified\n")
        self.assertIn("Ruled", _k3_dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_o3_20_1_residue_quoted_ruling_still_denotes(self):
        model, state = _k3_state(
            "\nPending Ruled: take Option A | DQ-001 | line 5\n")
        self.assertIn("Ruled", _k3_dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_o3_20_1_segment_claim_line_still_denotes(self):
        model, state = _k3_state(
            "\nClaim, reported as a claim: Ruled by Captain JP: "
            "take Option A.\n")
        self.assertIn("Ruled", _k3_dispositions(model))
        self.assertEqual(state, "Ruled")


class Step17Fix3K3FamilyEdgeControlTest(unittest.TestCase):
    """Family edges from the attack paper, denoting nothing
    before this cure and nothing after it: the guard widening
    goes no wider than the disposition reading."""

    def test_edge_entity_colon_row_stays_open(self):
        model, state = _k3_state(
            "\nCanonical Ruled&#58; 0 entries\n")
        self.assertEqual(state, "Open")

    def test_edge_mixed_case_state_row_stays_open(self):
        model, state = _k3_state("\nCanonical rULED: 0 entries\n")
        self.assertEqual(state, "Open")

    def test_edge_underscore_state_row_stays_open(self):
        model, state = _k3_state(
            "\nCanonical _Ruled: 0 entries_\n")
        self.assertEqual(state, "Open")

    def test_edge_quoted_heading_stays_open(self):
        model, state = _k3_state("\n\"Ruled group\"\n")
        self.assertEqual(state, "Open")

    def test_edge_prefixed_heading_stays_open(self):
        model, state = _k3_state("\nCopied; Ruled group\n")
        self.assertEqual(state, "Open")

    def test_edge_two_rows_semicolon_stay_open(self):
        model, state = _k3_state(
            "\nCanonical Ruled: 0 entries; Canonical Settled: 0 "
            "entries\n")
        self.assertNotIn("Ruled", _k3_dispositions(model))
        self.assertNotIn("Settled", _k3_dispositions(model))
        self.assertEqual(state, "Open")


class Step17Fix3K3LabelledBranchStandingTest(unittest.TestCase):
    """CH-51, second holder pins: the crosswalk cure at the
    labelled paragraph branch suppresses only a first line that
    is wholly a tally row. Labelled decision matter standing in
    its own form still denotes, and matter standing past a tally
    row on its line still denotes through the label."""

    def test_ruling_text_label_still_denotes(self):
        model, state = _k3_state(
            "\nRuling text: the panel accepted the report as "
            "written.\n")
        self.assertIn("Ruled", _k3_dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_matter_past_tally_row_still_denotes(self):
        model, state = _k3_state(
            "\nRuled: Ruled 1, total 1 and the panel accepted "
            "the report.\n")
        self.assertIn("Ruled", _k3_dispositions(model))
        self.assertEqual(state, "Ruled")


if __name__ == "__main__":
    unittest.main()
