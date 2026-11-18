"""Step 17 fix wave 4, Fix Seat K3 tests.

Charge CH-68, ruled at section 38 of
design/steps/step-17r-record.md under ruling (d), with FLAG 2
and the FLAG 11 digit ground restatement. Findings:
F-20-4-1 to F-20-4-4 (all High) at
design/steps/step-17r-attack4-20.md, and A4-10-F3 and
A4-10-F4 (both Medium) at design/steps/step-17r-attack4-10.md,
prepared at design/steps/step-17r-triage4-prep.md.

The guard ground, stated once at the ruling: guard
recognition is a matching matter, recognising whatever the
disposition reading denotes at the disposition reading own
width, on the count, joint, heading, and tally surfaces
alike. Every widening stays segment aware under the CH-15
confinement pin, so a genuine ruling later on the same line
still counts, and no cure suppresses a quoted genuine ruling
line (the O-4-20-1 standing, verified unmoved).

Both directions are pinned in this file. Recognition: the
charged rows and headings denote nothing, and the host entry
stays Open. Confinement: a genuine ruling standing on the
same line as a widened guarded form, after it, still counts.
At the tally surfaces the disposition reading own width
includes its Unicode decimal digit and word count forms;
data readings elsewhere are untouched by this charge.

Copyright: J.P. Picard aka Macro-Harder
"""

import unittest

import dqv_harness as h


def _entry(extra_body=""):
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


def _elements(model, entry_id="DQ-001"):
    entry = h.entry_by_id(model, entry_id)
    if entry is None:
        return []
    return h.as_list(h.get(entry, "status_elements", "elements"))


def _dispositions(model, entry_id="DQ-001"):
    out = []
    for el in _elements(model, entry_id):
        tup = h.get(el, "tuple", "element_tuple", "core_tuple")
        out.append(h.text_of(tuple(tup)[0]) if tup is not None
                   else h.text_of(h.get(el, "disposition")))
    return out


def _state(extra_body, name="k3_case.md"):
    model, output = h.run_pipeline(_entry(extra_body), name)
    result = h.entry_by_id(output, "DQ-001")
    return model, h.entry_state(result)


class Step17Fix4K3CountWordTest(unittest.TestCase):
    """CH-68, F-20-4-1 and A4-10-F3: the count limb stops at
    twenty and at decimal digits; counts written past that
    width still denote on the uncured tree."""

    def test_count_words_past_twenty_denote_nothing(self):
        rows = (
            ("Canonical Ruled: thirty entries", "Ruled"),
            ("Canonical Ruled: forty entries", "Ruled"),
            ("Canonical Ruled: sixty entries", "Ruled"),
            ("Canonical state: Ruled: thirty entries", "Ruled"),
            ("Canonical Settled: thirty entries", "Settled"),
        )
        for row, word in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn(word, _dispositions(model))
                self.assertEqual(state, "Open")

    def test_count_forms_past_decimal_digits_denote_nothing(self):
        rows = (
            "Canonical Ruled: no entries",
            "Canonical Ruled: XII entries",
            "Canonical Ruled: \u00b2 entries",
            "Canonical Ruled: about 0 entries",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")

    def test_prefix_bound_controls_stay_guarded(self):
        # The O-4-20-2 prefix bound, standing guarded before
        # this cure and after it: a multi word count beginning
        # with a word inside the old bound takes the guard.
        rows = (
            "Canonical Ruled: twenty five entries",
            "Canonical Ruled: twenty-one entries",
            "Canonical Ruled: one hundred entries",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")


class Step17Fix4K3JointPunctuationTest(unittest.TestCase):
    """CH-68, F-20-4-2: sentence punctuation at a count row
    joint defeats the guard on the uncured tree."""

    def test_sentence_punctuation_joints_denote_nothing(self):
        rows = (
            "Canonical. Ruled: 0 entries",
            "Canonical: Ruled: 0 entries",
            "Canonical; Ruled: 0 entries",
            "Canonical? Ruled: 0 entries",
            "Canonical! Ruled: 0 entries",
            "Canonical state. Ruled: 0 entries",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")


class Step17Fix4K3GroupHeadingTest(unittest.TestCase):
    """CH-68, F-20-4-3: group headings with trailing matter
    or a zero width joint still denote on the uncured tree,
    including the exit 4 Settled in part variant."""

    def test_headings_with_trailing_matter_denote_nothing(self):
        cases = (
            ("Ruled group)", "Ruled"),
            ('Ruled group"', "Ruled"),
            ("Ruled group]", "Ruled"),
            ("Ruled group entries", "Ruled"),
            ("Ruled group (decided)", "Ruled"),
            ("Ruled group\u2026", "Ruled"),
            ("Ruled group/", "Ruled"),
            ("Closed as decided group)", "Closed"),
        )
        for heading, word in cases:
            with self.subTest(heading=heading):
                model, state = _state("\n" + heading + "\n")
                self.assertNotIn(word, _dispositions(model))
                self.assertEqual(state, "Open")

    def test_headings_with_zero_width_joint_denote_nothing(self):
        model, state = _state("\nRuled\u200bgroup\n")
        self.assertNotIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Open")

    def test_settled_in_part_zero_width_joint_stays_open(self):
        model, state = _state("\nSettled in part\u200bgroup\n")
        self.assertNotIn("Settled", _dispositions(model))
        self.assertEqual(state, "Open")

    def test_heading_controls_stay_as_recorded(self):
        cases = (
            ("Ruled group-", "Ruled"),
            ("Ruled group*", "Ruled"),
            ("Settled in part\u00a0group", "Settled"),
            ("(Ruled group)", "Ruled"),
        )
        for heading, word in cases:
            with self.subTest(heading=heading):
                model, state = _state("\n" + heading + "\n")
                self.assertNotIn(word, _dispositions(model))
                self.assertEqual(state, "Open")


class Step17Fix4K3TallySurfaceTest(unittest.TestCase):
    """CH-68, F-20-4-4 and A4-10-F4: the crosswalk and
    verbatim appendix tally patterns read their tails
    literally on the uncured tree; respaced and re-encoded
    tally rows still denote."""

    def test_crosswalk_respaced_rows_denote_nothing(self):
        cases = (
            ("Ruled: Ruled 1,  total 1", "Ruled"),
            ("Ruled: Ruled 1,\ttotal 1", "Ruled"),
            ("Ruled: Ruled 1,\u00a0total 1", "Ruled"),
            ("Ruled: Ruled 1, Total 1", "Ruled"),
            ("Ruled: Ruled 1 total 1", "Ruled"),
            ("Settled: Settled 1,  total 1", "Settled"),
        )
        for row, word in cases:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn(word, _dispositions(model))
                self.assertEqual(state, "Open")

    def test_crosswalk_reencoded_rows_denote_nothing(self):
        cases = (
            "Ruled: Ruled \u0661, total \u0661",
            "Ruled: Ruled one, total one",
        )
        for row in cases:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")

    def test_appendix_respaced_rows_denote_nothing(self):
        cases = (
            ("Ruled |\u00a0line start | 1 occurrence | "
             "entries: DQ-001", "Ruled"),
            ("Ruled | line  start | 1 occurrence | "
             "entries: DQ-001", "Ruled"),
            ("Ruled | line\u00a0start | 1 occurrence | "
             "entries: DQ-001", "Ruled"),
            ("Ruled | line\tstart | 1 occurrence | "
             "entries: DQ-001", "Ruled"),
            ("Ruled | Line start | 1 occurrence | "
             "entries: DQ-001", "Ruled"),
            ("Settled |\u00a0line start | 1 occurrence | "
             "entries: DQ-001", "Settled"),
        )
        for row, word in cases:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn(word, _dispositions(model))
                self.assertEqual(state, "Open")

    def test_appendix_reencoded_rows_denote_nothing(self):
        cases = (
            "Ruled | line start | \u0661 occurrence | "
            "entries: DQ-001",
            "Ruled | line start | one occurrence | "
            "entries: DQ-001",
        )
        for row in cases:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")

    def test_crosswalk_trailing_period_row_denote_nothing(self):
        # The second mechanism of F-20-4-4: the guard pattern
        # matches this row as a prefix, and the labelled
        # paragraph branch wholly row test must read the row
        # at the same width, trailing period included.
        model, state = _state("\nRuled: Ruled 1, total 1.\n")
        self.assertNotIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Open")

    def test_tally_controls_stay_as_recorded(self):
        cases = (
            ("Ruled:  Ruled 1, total 1", "Ruled"),
            ("Ruled | line start | 1 occurrence | "
             "entries: DQ-001", "Ruled"),
            ("Ruled | line start | 1 occurrence | "
             "entries: DQ-002", "Ruled"),
            ("Awaiting decision: Ruled 1, total 1", "Ruled"),
            ("Pending: Ruled 1, total 1", "Ruled"),
        )
        for row, word in cases:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn(word, _dispositions(model))
                self.assertEqual(state, "Open")


class Step17Fix4K3ConfinementTest(unittest.TestCase):
    """CH-68 under FLAG 2: every widening stays segment aware
    under the CH-15 confinement pin, so a genuine ruling
    later on the same line as a widened guarded form still
    counts, and the widened form itself denotes nothing."""

    def test_widened_count_row_then_ruling_counts(self):
        model, state = _state(
            "\nCanonical Settled: thirty entries. Ruled by "
            "Captain JP: take Option A.\n")
        self.assertNotIn("Settled", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_punctuated_joint_row_then_ruling_counts(self):
        model, state = _state(
            "\nCanonical. Settled: 0 entries. Ruled by "
            "Captain JP: take Option A.\n")
        self.assertNotIn("Settled", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_respaced_crosswalk_then_ruling_counts(self):
        model, state = _state(
            "\nSettled: Settled 1,  total 1. Ruled by "
            "Captain JP: take Option A.\n")
        self.assertNotIn("Settled", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_reencoded_appendix_then_ruling_counts(self):
        model, state = _state(
            "\nSettled | line start | \u0661 occurrence | "
            "entries: DQ-001. Ruled by Captain JP: take "
            "Option A.\n")
        self.assertNotIn("Settled", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_heading_trailing_matter_then_ruling_counts(self):
        model, state = _state(
            "\nSettled group (decided). Ruled by Captain JP: "
            "take Option A.\n")
        self.assertNotIn("Settled", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_heading_and_ruling_one_sentence_counts(self):
        model, state = _state(
            "\nRuled group and Ruled by Captain JP: take "
            "Option A.\n")
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")


class Step17Fix4K3QuotedRulingStandingTest(unittest.TestCase):
    """Observation O-4-20-1 standing, unmoved by this cure:
    quoted genuine ruling lines still denote for their host
    entry, on every surface the rounds measured."""

    def test_crosswalk_quoted_ruling_still_denotes(self):
        model, state = _state(
            "\nRuled: take Option A: Ruled 1, total 1\n")
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_appendix_quoted_ruling_still_denotes(self):
        model, state = _state(
            "\nRuled: take Option A | line start | 1 "
            "occurrence | entries: DQ-001\n")
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_appendix_decider_label_still_denotes(self):
        model, state = _state(
            "\nRuled by Captain JP | line start | 1 "
            "occurrence | entries: DQ-001\n")
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_appendix_pending_phrasing_still_denotes(self):
        model, state = _state(
            "\nPending Ruled: take Option A | line start | 1 "
            "occurrence | entries: DQ-001 | unclassified\n")
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_residue_quoted_ruling_still_denotes(self):
        model, state = _state(
            "\nPending Ruled: take Option A | DQ-001 | "
            "line 5\n")
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_segment_claim_line_still_denotes(self):
        model, state = _state(
            "\nClaim, reported as a claim: Ruled by "
            "Captain JP: take Option A.\n")
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")


class Step17Fix4K3FamilyEdgeControlTest(unittest.TestCase):
    """Family edges denoting nothing before this cure and
    nothing after it: the widening goes no wider than the
    disposition reading."""

    def test_edge_forms_stay_open(self):
        rows = (
            "Canonical Ruled&#58; 0 entries",
            "Canonical rULED: 0 entries",
            "Canonical _Ruled: 0 entries_",
            '"Ruled group"',
            "Copied; Ruled group",
            "Canonical Ruled: 0 entries; Canonical Settled: "
            "0 entries",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertNotIn("Settled", _dispositions(model))
                self.assertEqual(state, "Open")


if __name__ == "__main__":
    unittest.main()
