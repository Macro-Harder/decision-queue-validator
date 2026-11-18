"""Step 17 fix wave 6, Fix Seat K3 tests.

Charge CH-107, the parse disposition guard programme,
ruled at section 58 of design/steps/step-17r-record.md
under ruling (b): option (i) stands ruled with the surface
discipline of option (iii) inside it. Ruling (c) of
section 52 stands as the programme ground, and the width
is restated once at the disposition reading own width on
each surface that ruling names (count, state, crosswalk,
and the appendix kind at the charged limb), the K3 stated
bounds standing superseded at the charged limbs in the
open by this ruling, as ruling (c) superseded the
vocabulary bound. Findings: seat 20 F-20-6-1, F-20-6-2,
F-20-6-3 (all High) and F-20-6-4 at
design/steps/step-17r-attack6-20.md, and seat 10
A6-10-F3 and A6-10-F4 at
design/steps/step-17r-attack6-10.md, prepared at
design/steps/step-17r-triage6-prep.md headed question 2.

Each surface width, stated in its own terms. Count: the
wide region joints take any whitespace character and the
zero width characters, a clause breaking mark standing
between the count and its noun is region matter, the row
noun stands as entries, entry, items, questions, or cases
(a trailing underscore on the noun standing as row
matter), and a single count token standing alone at the
end of the row takes its span. Tally count: a tally count
stands as the CH-68 count phrase or as one or more count
region tokens joined by whitespace. Crosswalk tail: the
total word stands as total, totals, subtotal, grand
total, or sum, and a single word token standing after the
final count at a whitespace joint is row matter. Appendix
kind: the kind slot stands as one to three word tokens
joined by whitespace between its pipes, the underscore
standing inside a kind token as before.

Both directions are pinned in this file. Recognition: the
charged rows denote nothing, and the host entry stays
Open. Confinement: the CH-15 segment awareness pin and
the O-4-20-1 standing stand pinned in both directions, a
genuine ruling standing after a widened guarded form
still counts, and quoted genuine ruling lines still
denote. The K3 pins on their listed forms stand whole,
restated in the control class below.

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


class Step17Fix6K3CountJointWidthTest(unittest.TestCase):
    """CH-107, F-20-6-1 at the joints: the wide count
    region joins its tokens by space, tab, or no break
    space only, while a tally copied through rich text or
    a wide layout takes the other whitespace forms of the
    same class, and those rows still denote on the
    uncured tree (attack6-20 cases a01 to a04, a18)."""

    def test_wide_whitespace_joints_denote_nothing(self):
        rows = (
            ("Canonical Ruled: dozen\u2003entries", "Ruled"),
            ("Canonical Ruled: dozen\u2009entries", "Ruled"),
            ("Canonical Ruled: dozen\u202fentries", "Ruled"),
            ("Canonical Ruled: dozen\u3000entries", "Ruled"),
        )
        for row, word in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn(word, _dispositions(model))
                self.assertEqual(state, "Open")

    def test_census_twin_em_space_joint_denotes_nothing(self):
        model, state = _state(
            "\nCanonical state: Ruled: dozen\u2003entries\n")
        self.assertNotIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Open")

    def test_zero_width_space_inside_noun_denotes_nothing(self):
        # Case a05: the zero width space standing inside
        # the would be noun, as one token on the uncured
        # tree, so no entries noun stands in the region.
        model, state = _state(
            "\nCanonical Ruled: dozen\u200bentries\n")
        self.assertNotIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Open")


class Step17Fix6K3CountClauseMarkTest(unittest.TestCase):
    """CH-107, F-20-6-1 at the clause marks, and the
    A6-10-F3 clause limb: a clause breaking mark standing
    between the count and its noun ends the wide region
    before the noun stands on the uncured tree, and the
    row denotes (attack6-20 cases a06 to a09, a19, and
    attack6-10 case g6-count-words DQ-010)."""

    def test_clause_marks_before_noun_denote_nothing(self):
        rows = (
            ("Canonical Ruled: dozen; entries", "Ruled"),
            ("Canonical Ruled: dozen: entries", "Ruled"),
            ("Canonical Ruled: dozen! entries", "Ruled"),
            ("Canonical Ruled: dozen? entries", "Ruled"),
            ("Canonical Settled: dozen; entries", "Settled"),
        )
        for row, word in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn(word, _dispositions(model))
                self.assertEqual(state, "Open")

    def test_seat10_clause_cut_row_denotes_nothing(self):
        model, state = _state(
            "\nCanonical Ruled: circa thirty; entries\n")
        self.assertNotIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Open")


class Step17Fix6K3CountNounTest(unittest.TestCase):
    """CH-107, F-20-6-1 at the noun, and A6-10-F3: the
    wide reading requires the plural word entries with a
    word boundary after it, and a row ending at another
    noun, at the singular, at a word joined noun, or at
    no noun at all takes no wide span on the uncured tree
    (attack6-20 cases a10 to a12, and attack6-10 case
    g6-count-words DQ-003 to DQ-008, DQ-011, DQ-013)."""

    def test_missing_and_respelled_noun_denote_nothing(self):
        rows = (
            "Canonical Ruled: dozen",
            "Canonical Ruled: dozen entry",
            "Canonical Ruled: dozen entries_",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")

    def test_seat10_other_nouns_denote_nothing(self):
        rows = (
            "Canonical Ruled: circa thirty items",
            "Canonical Ruled: over thirty items",
            "Canonical Ruled: some thirty cases",
            "Canonical Ruled: exactly thirty items",
            "Canonical Ruled: circa thirty questions",
            "Canonical Ruled: a dozen items",
            "Canonical Ruled: nil cases",
            "Canonical Ruled: dozen questions",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")

    def test_seat10_noun_controls_stay_guarded(self):
        # The guarded side of the A6-10-F3 family, recorded
        # at the paper observations O4 and O5 so the
        # finding is not read wider than its evidence:
        # these rows leave their host Open in both trees.
        rows = (
            "Canonical Ruled: thirty items",
            "Canonical Closed as decided: circa forty items",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertNotIn("Closed", _dispositions(model))
                self.assertEqual(state, "Open")


class Step17Fix6K3TallyCountWidthTest(unittest.TestCase):
    """CH-107, F-20-6-2, and the tally count limb of
    A6-10-F4: the tally count reading admits the CH-68
    count phrase or one count region token, so crosswalk
    counts spelled in several words outside the phrase
    still denote on the uncured tree (attack6-20 cases
    b01 to b03, and attack6-10 case g6-tally-forms DQ-005
    and DQ-009)."""

    def test_crosswalk_several_word_counts_denote_nothing(self):
        rows = (
            "Ruled: Ruled a dozen, total 1",
            "Ruled: Ruled 1, total a dozen",
            "Ruled: Ruled more than one, total 1",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")

    def test_seat10_dozen_word_counts_denote_nothing(self):
        rows = (
            "Ruled: Ruled two dozen, total two dozen",
            "Ruled: Ruled one dozen, total one dozen",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")

    def test_appendix_several_word_count_control(self):
        # Attack6-20 controls b04 and b05, guarded on the
        # uncured tree and after it: the appendix pattern
        # takes its count as one token and its occurrence
        # word as the next token, so a two word count
        # stands covered at that surface.
        rows = (
            "Ruled | line start | a dozen occurrences | "
            "entries: DQ-001",
            "Ruled | line start | more than one occurrences "
            "| entries: DQ-001",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")


class Step17Fix6K3CrosswalkTailTest(unittest.TestCase):
    """CH-107, F-20-6-3, and the total word limb of
    A6-10-F4: the crosswalk tail reads its total word
    directly at the joint after the first count and takes
    no final noun other than entries, so a word standing
    before the total word, a fresh total word, and a row
    closed by another noun still denote on the uncured
    tree (attack6-20 cases b11 and b12, and attack6-10
    case g6-tally-forms DQ-003 and DQ-004)."""

    def test_grand_total_row_denotes_nothing(self):
        model, state = _state(
            "\nRuled: Ruled 1, grand total 1\n")
        self.assertNotIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Open")

    def test_sum_total_row_denotes_nothing(self):
        model, state = _state("\nRuled: Ruled 1, sum 1\n")
        self.assertNotIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Open")

    def test_final_items_noun_row_denotes_nothing(self):
        model, state = _state(
            "\nRuled: Ruled 1, total 1 items\n")
        self.assertNotIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Open")


class Step17Fix6K3AppendixKindTest(unittest.TestCase):
    """CH-107, F-20-6-4, and the kind limb of A6-10-F4:
    the appendix occurrence kind forms stand at the
    CH-68 width, so a word joined kind, a kind with a
    leading word, and a kind outside the three stated
    kinds still denote on the uncured tree (attack6-20
    cases b08 and b10, and attack6-10 case g6-tally-forms
    DQ-006)."""

    def test_word_joined_kind_denotes_nothing(self):
        model, state = _state(
            "\nRuled | line_start | 1 occurrence | "
            "entries: DQ-001\n")
        self.assertNotIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Open")

    def test_leading_word_kind_denotes_nothing(self):
        model, state = _state(
            "\nRuled | at line start | 1 occurrence | "
            "entries: DQ-001\n")
        self.assertNotIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Open")

    def test_fresh_kind_word_denotes_nothing(self):
        model, state = _state(
            "\nRuled | heading | 1 occurrence | "
            "entries: DQ-001\n")
        self.assertNotIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Open")


class Step17Fix6K3ConfinementTest(unittest.TestCase):
    """CH-107 under the CH-15 segment awareness pin, in
    both directions: every widening stays confined to
    the row itself, so a genuine ruling standing on the
    same line as a widened guarded form, after it, still
    counts, and matter standing past a tally row still
    denotes through its label."""

    def test_em_space_count_row_then_ruling_counts(self):
        model, state = _state(
            "\nCanonical Settled: dozen\u2003entries. Ruled "
            "by Captain JP: take Option A.\n")
        self.assertNotIn("Settled", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_clause_mark_count_row_then_ruling_counts(self):
        # Attack6-20 case e01 stands in this family: the
        # row closed by its noun and a semicolon, then the
        # ruling, the ruling counting in full.
        model, state = _state(
            "\nCanonical Ruled: dozen entries; Ruled by "
            "Captain JP: take Option A.\n")
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_no_noun_count_row_then_ruling_counts(self):
        model, state = _state(
            "\nCanonical Settled: dozen. Ruled by Captain "
            "JP: take Option A.\n")
        self.assertNotIn("Settled", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_several_word_tally_then_ruling_counts(self):
        model, state = _state(
            "\nSettled: Settled a dozen, total 1. Ruled by "
            "Captain JP: take Option A.\n")
        self.assertNotIn("Settled", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_grand_total_row_then_ruling_counts(self):
        model, state = _state(
            "\nSettled: Settled 1, grand total 1. Ruled by "
            "Captain JP: take Option A.\n")
        self.assertNotIn("Settled", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_word_joined_kind_row_then_ruling_counts(self):
        model, state = _state(
            "\nSettled | line_start | 1 occurrence | "
            "entries: DQ-001. Ruled by Captain JP: take "
            "Option A.\n")
        self.assertNotIn("Settled", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_matter_past_tally_row_still_denotes(self):
        # The standing CH-51 labelled branch pin, restated:
        # matter standing past a tally row on its line takes
        # its labelled element as before (attack6-20 case
        # e08 stands in this family).
        model, state = _state(
            "\nRuled: Ruled 1, total 1 and the panel "
            "accepted the report.\n")
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")


class Step17Fix6K3QuotedRulingStandingTest(unittest.TestCase):
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


class Step17Fix6K3StandingControlTest(unittest.TestCase):
    """The K3 pins on their listed forms, the CH-68 pins,
    the state joint bound, and the attack round controls,
    standing as recorded before this cure and after it."""

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

    def test_count_region_controls_stay_guarded(self):
        # Attack6-20 Group A controls a15, a16, a20, and
        # a21, guarded on the uncured tree and after it.
        rows = (
            "Canonical Ruled: dozen entries.",
            "Canonical Ruled: more\u00a0than\u00a0thirty "
            "entries",
            "Canonical Ruled: dozen, entries",
            "Canonical Ruled: dozen. entries",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")

    def test_state_word_character_joint_bound_stays(self):
        # Attack6-20 Group C, standing in both directions:
        # a word character at a multiword state joint, an
        # underscore included, leaves no boundary for
        # either reading, so these rows denote nothing on
        # the uncured tree and after the cure.
        rows = (
            "Canonical Settled_in_part: 0 entries",
            "Settled_in_part: Settled in part 1, total 1",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Settled", _dispositions(model))
                self.assertEqual(state, "Open")

    def test_closed_as_decided_circa_row_stays_open(self):
        # The seat 10 observation O4 bound in its entries
        # form, standing from fix wave 5: this row leaves
        # its host Open in both trees.
        model, state = _state(
            "\nCanonical Closed as decided: circa forty "
            "entries\n")
        self.assertNotIn("Closed", _dispositions(model))
        self.assertEqual(state, "Open")


if __name__ == "__main__":
    unittest.main()
