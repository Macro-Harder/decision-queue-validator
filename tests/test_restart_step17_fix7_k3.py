"""Step 17 fix wave 7, Fix Seat K3 tests.

Charges CH-121 to CH-124, the parse disposition guard
programme, ruled at section 66 of
design/steps/step-17r-record.md under ruling (c) whole,
standing on the programme ground of section 52: the
disposition reading recognises its forms at the reading
own width, and the guard width is restated once at that
width on each surface the charge names. Findings: seat
20 F-20-7-1, F-20-7-2, F-20-7-3 (all Medium) and
F-20-7-4 (Low) at design/steps/step-17r-attack7-20.md,
and the members of seat 10 A7-10-F3 and A7-10-F4 at
design/steps/step-17r-attack7-10.md that ride across
these charges (the clause mark members at CH-122, the
kind members at CH-123, and the trailing token, prefixed,
and aggregate members at CH-121 and CH-124), prepared at
design/steps/step-17r-triage7-prep.md.

Each surface width, stated in its own terms. Crosswalk
tail (CH-121): the trailing row matter after the final
count stands as one word token at a whitespace joint, as
at CH-107, or as the row noun (entries, entry, items,
questions, or cases, a trailing underscore standing as
row matter) at a joint run of whitespace, the zero width
characters, a comma, a period, or a hyphen, and in either
form one further word token stands after it at a
whitespace joint. Clause mark (CH-122): a tally count
stands as the CH-68 count phrase or as one or more count
region tokens joined by whitespace, the zero width
characters, or one semicolon standing between two count
tokens with whitespace or none around it; and the wide
count region takes a span where the whole region is one
clause breaking mark standing alone. Appendix
kind (CH-123): the kind slot stands as one to five word
tokens joined by whitespace between its pipes. Total
word (CH-124): the total word stands as the word total
in either case, its plural, and its prefixed subtotal
form, with one word token other than the word in
standing before the total word at a non word joint
where one stands (the grand form included), as the
word sum, as the two word form grand sum, or as the
word aggregate.

Both directions are pinned in this file. Recognition:
the charged rows denote nothing, and the host entry
stays Open. Confinement: the CH-15 segment awareness
pin and the O-4-20-1 standing stand pinned in both
directions, a genuine ruling standing after a widened
guarded form still counts, matter standing past a tally
row still denotes through its label, and quoted genuine
ruling lines still denote. The K3 pins on their listed
forms stand whole, restated in the control classes
below.

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


class Step17Fix7K3CrosswalkTailTest(unittest.TestCase):
    """CH-121, F-20-7-1, and the trailing token member of
    A7-10-F4: the crosswalk tail takes its trailing row
    matter at one whitespace joint only and at one token
    only, so the row noun standing at a comma, period, or
    hyphen joint, and a second token standing past the
    admitted noun, still denote on the cured CH-107 tree
    (attack7-20 cases b04, b05, b06, and b13, and
    attack7-10 case g7-tally-forms DQ-009)."""

    def test_noun_at_punctuation_joints_denotes_nothing(self):
        rows = (
            "Ruled: Ruled 1, total 1. entries",
            "Ruled: Ruled 1, total 1, entries",
            "Ruled: Ruled 1, total 1-entries",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")

    def test_second_token_past_noun_denotes_nothing(self):
        rows = (
            "Ruled: Ruled 1, total 1 entries extra",
            "Ruled: Ruled 1, total 1 items counted",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")

    def test_one_token_at_whitespace_joint_stays_guarded(self):
        # The CH-107 admitted form, guarded before this
        # cure and after it: one word token standing after
        # the final count at a whitespace joint.
        rows = (
            "Ruled: Ruled 1, total 1 entries",
            "Ruled: Ruled 1, total 1 items",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")


class Step17Fix7K3ClauseMarkTest(unittest.TestCase):
    """CH-122, F-20-7-2, and A7-10-F3: the tally count
    tokens stand joined by whitespace and the zero width
    characters only, so a semicolon standing inside a
    several word tally count still denotes (attack7-20
    case b03); and the wide count reading takes its span
    from a count region token or a noun, so a canonical
    count row whose whole count region is one clause
    breaking mark still denotes (attack7-10 case
    g7b-count-empty DQ-003 and DQ-004)."""

    def test_tally_count_clause_mark_inside_denotes_nothing(self):
        rows = (
            "Ruled: Ruled a; dozen, total 1",
            "Ruled: Ruled a dozen; more, total 1",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")

    def test_appendix_count_clause_mark_inside_stays_guarded(self):
        # The appendix twin of the tally clause form,
        # measured on the uncured tree: it stands guarded
        # in both trees, because the appendix pattern takes
        # the joint before its occurrence token at
        # _GUARD_JOINT_OPT, which already takes the mark.
        # It stands here as a control, not as a fail before
        # member of the charge.
        model, state = _state(
            "\nRuled | line start | a; dozen occurrences | "
            "entries: DQ-001\n")
        self.assertNotIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Open")

    def test_whole_region_clause_mark_denotes_nothing(self):
        rows = (
            ("Canonical Ruled: ;", "Ruled"),
            ("Canonical Ruled: !", "Ruled"),
            ("Canonical Settled: ?", "Settled"),
        )
        for row, word in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn(word, _dispositions(model))
                self.assertEqual(state, "Open")

    def test_clause_controls_stay_as_recorded(self):
        # The guarded and neutral side of the A7-10-F3
        # family, recorded at the paper observation O5
        # and at case g7b-count-empty DQ-005 so the
        # finding is not read wider than its evidence:
        # the empty row carries no count region at all
        # and denotes nothing in either tree, and the
        # doubled mark standing at the final joint before
        # the noun stands guarded in either tree.
        rows = (
            ("Canonical Ruled:", "Ruled"),
            ("Canonical Ruled: circa thirty;; entries",
             "Ruled"),
        )
        for row, word in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn(word, _dispositions(model))
                self.assertEqual(state, "Open")


class Step17Fix7K3AppendixKindTest(unittest.TestCase):
    """CH-123, F-20-7-3, and the kind members of
    A7-10-F4: the appendix kind slot reads at most three
    word tokens under CH-107, so a kind spelled in four
    or five tokens still denotes (attack7-20 cases b08
    and b11, attack7-10 case g7b-tally-more DQ-002, and
    case g7-tally-forms DQ-007)."""

    def test_four_token_kinds_denote_nothing(self):
        rows = (
            "Ruled | at the line start | 1 occurrence | "
            "entries: DQ-001",
            "Ruled | at line start position | 1 occurrence "
            "| entries: DQ-001",
            "Ruled | a kind name here | 1 occurrence | "
            "entries: DQ-001",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")

    def test_five_token_kind_denotes_nothing(self):
        model, state = _state(
            "\nRuled | very long kind name here | 1 "
            "occurrence | entries: DQ-001\n")
        self.assertNotIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Open")

    def test_kind_controls_stay_guarded(self):
        # The CH-107 forms and the attack7-20 controls
        # b09 and b10, guarded before this cure and after
        # it: the three token kind, the slash joined kind
        # standing as one token, and the underscore joined
        # two token kind.
        rows = (
            "Ruled | at line start | 1 occurrence | "
            "entries: DQ-001",
            "Ruled | line/start | 1 occurrence | entries: "
            "DQ-001",
            "Ruled | line_start position | 1 occurrence | "
            "entries: DQ-001",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")


class Step17Fix7K3TotalWordTest(unittest.TestCase):
    """CH-124, F-20-7-4, and the prefixed and aggregate
    members of A7-10-F4: the total word admits grand
    before total and admits sum alone under CH-107, so
    the combined grand sum form, a total word carrying
    another leading word, and the aggregate forms still
    denote (attack7-20 case b07, and attack7-10 case
    g7-tally-forms DQ-003 to DQ-006 and DQ-010)."""

    def test_grand_sum_row_denotes_nothing(self):
        model, state = _state(
            "\nRuled: Ruled 1, grand sum 1\n")
        self.assertNotIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Open")

    def test_prefixed_total_rows_denote_nothing(self):
        rows = (
            "Ruled: Ruled 1, combined total 1",
            "Ruled: Ruled 1, net total 1",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")

    def test_aggregate_rows_denote_nothing(self):
        rows = (
            "Ruled: Ruled 1 in aggregate",
            "Ruled: Ruled 1, aggregate 1",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")

    def test_total_controls_stay_guarded(self):
        # The guarded side of the A7-10-F4 family at the
        # paper observation O6 and the attack7-20 control
        # b14, guarded before this cure and after it: the
        # sum total row, whose span the tally count
        # reading completes over the words total 1, the
        # in sum row, and the grand total row.
        rows = (
            "Ruled: Ruled 1, sum total 1",
            "Ruled: Ruled 1 in sum",
            "Ruled: Ruled 1, grand total 1",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")


class Step17Fix7K3ConfinementTest(unittest.TestCase):
    """CH-121 to CH-124 under the CH-15 segment awareness
    pin, in both directions: every widening stays
    confined to the row itself, so a genuine ruling
    standing on the same line as a widened guarded form,
    after it, still counts, the sentence joint after a
    final count still takes no trailing token where the
    next word is no row noun, and matter standing past a
    tally row still denotes through its label."""

    def test_second_token_row_then_ruling_counts(self):
        model, state = _state(
            "\nSettled: Settled 1, total 1 entries extra. "
            "Ruled by Captain JP: take Option A.\n")
        self.assertNotIn("Settled", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_period_joint_edge_still_takes_no_ruling(self):
        # The confinement edge of the CH-121 limb in its
        # standing form: a sentence joint standing after
        # the final count takes no trailing token where
        # the word after the joint is no row noun, so the
        # ruling standing after the row counts in full.
        model, state = _state(
            "\nSettled: Settled 1, total 1. Ruled by "
            "Captain JP: take Option A.\n")
        self.assertNotIn("Settled", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_clause_mark_row_then_ruling_counts(self):
        model, state = _state(
            "\nCanonical Settled: ; Ruled by Captain JP: "
            "take Option A.\n")
        self.assertNotIn("Settled", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_tally_clause_row_then_ruling_counts(self):
        model, state = _state(
            "\nSettled: Settled a; dozen, total 1. Ruled "
            "by Captain JP: take Option A.\n")
        self.assertNotIn("Settled", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_four_token_kind_row_then_ruling_counts(self):
        model, state = _state(
            "\nSettled | at the line start | 1 occurrence "
            "| entries: DQ-001. Ruled by Captain JP: take "
            "Option A.\n")
        self.assertNotIn("Settled", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_grand_sum_row_then_ruling_counts(self):
        model, state = _state(
            "\nSettled: Settled 1, grand sum 1. Ruled by "
            "Captain JP: take Option A.\n")
        self.assertNotIn("Settled", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_matter_past_tally_row_still_denotes(self):
        # The standing CH-51 labelled branch pin, restated:
        # matter standing past a tally row on its line
        # takes its labelled element as before.
        model, state = _state(
            "\nRuled: Ruled 1, total 1 and the panel "
            "accepted the report.\n")
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")


class Step17Fix7K3QuotedRulingStandingTest(unittest.TestCase):
    """Observation O-4-20-1 standing, unmoved by this
    cure: quoted genuine ruling lines still denote for
    their host entry, on every surface the rounds
    measured."""

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


class Step17Fix7K3StandingControlTest(unittest.TestCase):
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
        model, state = _state(
            "\nCanonical Closed as decided: circa forty "
            "entries\n")
        self.assertNotIn("Closed", _dispositions(model))
        self.assertEqual(state, "Open")


if __name__ == "__main__":
    unittest.main()
