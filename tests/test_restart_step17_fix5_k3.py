"""Step 17 fix wave 5, Fix Seat K3 tests.

Charge CH-88, ruled at section 52 of
design/steps/step-17r-record.md under ruling (c): ruling (d)
of section 38 stands as the programme ground, the
disposition reading recognises its forms at the reading's
own width at the count, state, and crosswalk surfaces
alike, and the K3 enumerated count vocabulary bound stands
superseded at the count limb in the open by that ruling.
Findings: F-20-5-1, F-20-5-2, and F-20-5-3 (all High) at
design/steps/step-17r-attack5-20.md, and A5-10-F3 and
A5-10-F4 (both Medium) at
design/steps/step-17r-attack5-10.md, prepared at
design/steps/step-17r-triage5-prep.md.

Both directions are pinned in this file. Recognition: the
charged rows denote nothing, and the host entry stays Open.
Confinement: a genuine ruling standing on the same line as
a widened guarded form, after it, still counts, and no cure
suppresses a quoted genuine ruling line (the O-4-20-1
standing, verified unmoved). The K3 pins on their listed
forms and the CH-68 pins stand whole, restated in the
control class below.

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


class Step17Fix5K3CountWidthTest(unittest.TestCase):
    """CH-88, F-20-5-1 and A5-10-F3, the count limb: the
    CH-68 count phrase vocabulary stops short of the
    disposition reading width, so count rows whose counts
    stand outside the vocabulary still denote on the
    uncured tree. Under ruling (c) the vocabulary bound
    stands superseded at this limb in the open."""

    def test_unlisted_approximators_denote_nothing(self):
        rows = (
            ("Canonical Ruled: over 0 entries", "Ruled"),
            ("Canonical Ruled: exactly 0 entries", "Ruled"),
            ("Canonical Ruled: circa thirty entries", "Ruled"),
            ("Canonical Ruled: over thirty entries", "Ruled"),
            ("Canonical Ruled: more than thirty entries",
             "Ruled"),
            ("Canonical Ruled: at least thirty entries",
             "Ruled"),
            ("Canonical Ruled: some thirty entries", "Ruled"),
            ("Canonical Ruled: approx. thirty entries",
             "Ruled"),
            ("Canonical Ruled: approx. 0 entries", "Ruled"),
            ("Canonical Ruled: about-0 entries", "Ruled"),
            ("Canonical state: Ruled: over 0 entries", "Ruled"),
        )
        for row, word in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn(word, _dispositions(model))
                self.assertEqual(state, "Open")

    def test_count_words_outside_vocabulary_denote_nothing(self):
        rows = (
            ("Canonical Ruled: several entries", "Ruled"),
            ("Canonical Ruled: trillion entries", "Ruled"),
            ("Canonical Ruled: dozen entries", "Ruled"),
            ("Canonical Ruled: none entries", "Ruled"),
            ("Canonical Ruled: zillion entries", "Ruled"),
            ("Canonical Ruled: pair entries", "Ruled"),
            ("Canonical Ruled: a dozen entries", "Ruled"),
            ("Canonical Ruled: nil entries", "Ruled"),
            ("Canonical Ruled: nought entries", "Ruled"),
            ("Canonical Settled: dozen entries", "Settled"),
        )
        for row, word in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn(word, _dispositions(model))
                self.assertEqual(state, "Open")

    def test_numeric_forms_outside_ranges_denote_nothing(self):
        rows = (
            "Canonical Ruled: \u2153 entries",
            "Canonical Ruled: \u24ea entries",
            "Canonical Ruled: \u3007 entries",
            "Canonical Ruled: 1_000 entries",
            "Canonical Ruled: 0x0 entries",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")


class Step17Fix5K3TallyCountWidthTest(unittest.TestCase):
    """CH-88, F-20-5-1 at the tally limbs and A5-10-F4:
    tally rows whose counts or tally words stand in fresh
    stated forms still denote on the uncured tree, where
    their printed forms are guarded."""

    def test_tally_dozen_counts_denote_nothing(self):
        cases = (
            ("Ruled: Ruled dozen, total dozen", "Ruled"),
            ("Ruled | variant | dozen occurrences | "
             "entries: DQ-001", "Ruled"),
        )
        for row, word in cases:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn(word, _dispositions(model))
                self.assertEqual(state, "Open")

    def test_appendix_fresh_occurrence_words_denote_nothing(self):
        rows = (
            "Ruled | line start | 1 time | entries: DQ-001",
            "Ruled | line start | one time | entries: DQ-001",
            "Ruled | line start | 1 hit | entries: DQ-001",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")

    def test_crosswalk_in_total_rows_denote_nothing(self):
        rows = (
            "Ruled: Ruled 1 in total",
            "Ruled: Ruled one in total",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")


class Step17Fix5K3StateJointWidthTest(unittest.TestCase):
    """CH-88, F-20-5-2: the tally state pattern reads the
    multiword states at single literal spaces only, while
    the heading pattern in the same programme reads them
    at any non word joint; respaced multiword tally
    phrasings still denote on the uncured tree, the
    respaced Settled in part crosswalk row driving its
    entry Ambiguous at exit 4."""

    def test_respaced_multiword_tally_rows_denote_nothing(self):
        cases = (
            ("Settled  in  part: Settled in part 1, total 1",
             "Settled"),
            ("Closed  as  decided: Closed as decided 1, "
             "total 1", "Closed"),
            ("Settled  in  part | line start | 1 occurrence "
             "| entries: DQ-001", "Settled"),
            ("Closed  as  decided | line start | 1 "
             "occurrence | entries: DQ-001", "Closed"),
            ("Ruled: Settled  in  part 1, total 1", "Ruled"),
        )
        for row, word in cases:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn(word, _dispositions(model))
                self.assertEqual(state, "Open")


class Step17Fix5K3CrosswalkTailTest(unittest.TestCase):
    """CH-88, F-20-5-3: the crosswalk tail reads literally
    at three points on the uncured tree: a trailing word
    past the wholly row test, a space before the first
    colon, and a respelled total word."""

    def test_trailing_word_row_denotes_nothing(self):
        model, state = _state(
            "\nRuled: Ruled 1, total 1 entries\n")
        self.assertNotIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Open")

    def test_space_before_colon_row_denotes_nothing(self):
        model, state = _state("\nRuled : Ruled 1, total 1\n")
        self.assertNotIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Open")

    def test_respelled_total_rows_denote_nothing(self):
        rows = (
            "Ruled: Ruled 1, totals 1",
            "Ruled: Ruled 1, subtotal 1",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")


class Step17Fix5K3CombinationTest(unittest.TestCase):
    """CH-88, F-20-5-1 in combination: an escaping form
    standing with a guarded form, a heading, a comment
    segment, or in a table cell still denotes on the
    uncured tree."""

    def test_combination_rows_denote_nothing(self):
        cases = (
            ("| note | Canonical Ruled: dozen entries |",
             "Ruled"),
            ("Canonical Settled: 0 entries. Canonical Ruled: "
             "dozen entries", "Ruled"),
            ("Ruled group. Canonical Ruled: dozen entries",
             "Ruled"),
            ("Canonical Ruled: 0 entries. Ruled: Ruled "
             "dozen, total dozen", "Ruled"),
            ("<!-- note --> Canonical Ruled: dozen entries",
             "Ruled"),
            ("Copied from the report. Canonical state: "
             "Ruled: dozen entries", "Ruled"),
            ("Ruled group. Ruled: Ruled dozen, total dozen",
             "Ruled"),
        )
        for row, word in cases:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn(word, _dispositions(model))
                self.assertNotIn("Settled", _dispositions(model))
                self.assertEqual(state, "Open")


class Step17Fix5K3ConfinementTest(unittest.TestCase):
    """CH-88 under the CH-15 confinement pin: every
    widening stays segment aware, so a genuine ruling
    standing on the same line as a widened guarded form,
    after it, still counts, and matter standing past a
    tally row still denotes through its label."""

    def test_wide_count_row_then_ruling_counts(self):
        model, state = _state(
            "\nCanonical Settled: dozen entries. Ruled by "
            "Captain JP: take Option A.\n")
        self.assertNotIn("Settled", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_wide_count_row_comma_then_ruling_counts(self):
        model, state = _state(
            "\nCanonical Settled: dozen entries, Ruled by "
            "Captain JP: take Option A.\n")
        self.assertNotIn("Settled", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_respaced_crosswalk_then_ruling_counts(self):
        model, state = _state(
            "\nRuled: Settled  in  part 1, total 1. Ruled "
            "by Captain JP: take Option A.\n")
        self.assertNotIn("Settled", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_dozen_appendix_then_ruling_counts(self):
        model, state = _state(
            "\nSettled | variant | dozen occurrences | "
            "entries: DQ-001. Ruled by Captain JP: take "
            "Option A.\n")
        self.assertNotIn("Settled", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_in_total_crosswalk_then_ruling_counts(self):
        model, state = _state(
            "\nSettled: Settled one in total. Ruled by "
            "Captain JP: take Option A.\n")
        self.assertNotIn("Settled", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_matter_past_tally_row_still_denotes(self):
        # The standing CH-51 labelled branch pin, restated:
        # matter standing past a tally row on its line takes
        # its labelled element as before.
        model, state = _state(
            "\nRuled: Ruled 1, total 1 and the panel "
            "accepted the report.\n")
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")


class Step17Fix5K3QuotedRulingStandingTest(unittest.TestCase):
    """Observation O-4-20-1 standing, unmoved by this cure:
    quoted genuine ruling lines still denote for their
    host entry, on every surface the rounds measured."""

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
            "\nPending Ruled: take Option A | line start | "
            "1 occurrence | entries: DQ-001 | unclassified\n")
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


class Step17Fix5K3StandingControlTest(unittest.TestCase):
    """The K3 pins on their listed forms, the CH-68 pins,
    and the attack round controls, standing guarded before
    this cure and after it."""

    def test_listed_forms_stay_guarded(self):
        cases = (
            ("Canonical Ruled: thirty entries", "Ruled"),
            ("Canonical Ruled: about thirty entries", "Ruled"),
            ("Canonical Ruled: two dozen entries", "Ruled"),
            ("Canonical Ruled: (0) entries", "Ruled"),
            ("Canonical Ruled: 0.5 entries", "Ruled"),
            ("Ruled: Ruled 1, total 1", "Ruled"),
            ("Ruled: Ruled 1, total 1.", "Ruled"),
            ("Ruled | line start | 1 occurrence | entries: "
             "DQ-001", "Ruled"),
            ("Ruled | embedded | 1 occurrence | entries: "
             "DQ-001", "Ruled"),
            ("Canonical state: Settled  in  part: 0 entries",
             "Settled"),
        )
        for row, word in cases:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn(word, _dispositions(model))
                self.assertEqual(state, "Open")

    def test_closed_as_decided_circa_row_stays_open(self):
        # The seat 10 observation O4 bound, measured on the
        # uncured tree and standing after the cure: this
        # row leaves its host Open in both trees, recorded
        # so the count finding is not read wider than its
        # evidence at the Closed as decided surface.
        model, state = _state(
            "\nCanonical Closed as decided: circa forty "
            "entries\n")
        self.assertNotIn("Closed", _dispositions(model))
        self.assertEqual(state, "Open")


if __name__ == "__main__":
    unittest.main()
