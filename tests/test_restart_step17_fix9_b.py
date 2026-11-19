"""Step 17 fix wave 9, Fix Seat B tests.

Charges CH-193, CH-194, CH-195, and CH-196, the guard
programme limbs, ruled TO FIX at section 81 of
design/steps/step-17r-record.md under ruling (a)
(charges numbered consecutively from CH-191 in cluster
order, Cluster A taking CH-191 and CH-192, so Cluster B
takes the next four) and ruling (g) (the guard programme
pattern restated for the Step 18 plan with round 9 guard
members added). Findings: T9-14 (seat 10 A9-10-F3 kind
member and seat 20 F-20-9-2), T9-15 (seat 10 A9-10-F3
prefix members and seat 20 F-20-9-3), T9-16 (seat 10
A9-10-F4 and seat 20 F-20-9-1), and T9-35 (seat 20
F-20-9-4, Low), consolidated in
design/steps/step-17r-r9-triage-prep.md Cluster B.

Each surface width, stated in its own terms. Appendix
kind (CH-193): the kind slot stands as one to seven word
tokens joined by whitespace between its pipes, where
CH-160 read one to six. Total word prefix (CH-194): up
to three word tokens other than the word in standing
before the total word at a non word joint stand as its
prefix, the same terms standing at the grand total form,
at the word sum, and at the word aggregate in its
singular and plural forms, where CH-161 read up to two.
Crosswalk tail (CH-195): the trailing row matter after
the final count stands as at CH-159, with the row noun
standing also at an exclamation, question, pipe, or
equals joint; with a fourth word token standing after
the third at a whitespace joint; with a second word
token standing after the first at a semicolon or colon
joint where that token closes the line; with a third
word token standing after the second at a comma joint
where that token closes the line; with a comma joint
token that does not close the line standing as row
matter where one further word token stands after it at
a whitespace joint and closes the line (at the first
token place and at the second token place alike); with
a first word token that is no row noun standing at a
semicolon joint where it closes the line; and with a
third word token standing after a second token that
ends at a period, where that third token closes the
line and is no ruling form (the g14 member, charged on
its non ruling third word form only). Sums plural
(CH-196): the word sum stands as a total word in its
plural form sums beside its singular, in the plain form
and in the grand form, where CH-161 read the singular
only.

Both directions are pinned in this file. Recognition:
the charged rows denote nothing, and the host entry
stays Open. Confinement: a genuine ruling standing in
the widened forms company still counts, in the forms
the earlier waves charged and in the new bound forms
this cure states at their line closing and non ruling
edges, matter standing past a tally row still denotes
through its label, and quoted genuine ruling lines
still denote. The fix wave 8 K4 pins on these limbs
stand whole, restated in the standing pin class below.

Copyright: J.P. Picard aka Macro-Harder
"""

import unittest

import dqv_harness as h


def _entry(extra_body=""):
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


def _state(extra_body, name="b_case.md"):
    model, output = h.run_pipeline(_entry(extra_body), name)
    result = h.entry_by_id(output, "DQ-001")
    return model, h.entry_state(result)


class Step17Fix9BAppendixKindTest(unittest.TestCase):
    """CH-193, T9-14: the appendix kind slot reads at most
    six word tokens under CH-160, so a kind spelled in
    seven tokens still denotes (attack9-10 case
    g9-kind-seven and attack9-20 case k9_01)."""

    def test_seven_token_kinds_denote_nothing(self):
        rows = (
            "Ruled | one two three four five six seven | 1 "
            "occurrence | entries: DQ-001",
            "Ruled | at the line start position now today | 1 "
            "occurrence | entries: DQ-001",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")

    def test_kind_controls_stay_guarded(self):
        rows = (
            "Ruled | one two three four five six | 1 "
            "occurrence | entries: DQ-001",
            "Ruled | at the line start position | 1 "
            "occurrence | entries: DQ-001",
            "Ruled | at\tthe\tline\tstart | 1 occurrence "
            "| entries: DQ-001",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")


class Step17Fix9BTotalWordPrefixTest(unittest.TestCase):
    """CH-194, T9-15: the total word prefix reading admits
    up to two words under CH-161, so three words standing
    before the total word, the grand total form, the
    aggregates plural, or the word sum still denote
    (attack9-10 cases g9-prefix-three,
    g9-prefix-three-grand, and g9-sum-prefix-three, and
    attack9-20 cases w9_01, w9_02, w9_04, and w9_06)."""

    def test_three_word_prefix_denotes_nothing(self):
        rows = (
            "Ruled: Ruled 1, combined net gross total 1",
            "Ruled: Ruled 1, very truly grand total 1",
            "Ruled: Ruled 1, combined overall net total 1",
            "Ruled: Ruled 1, overall combined grand total 1",
            "Ruled: Ruled 1, combined overall net sum 1",
            "Ruled: Ruled 1, combined net gross sum 1",
            "Ruled: Ruled 1, combined net gross aggregates 1",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")

    def test_prefix_controls_stay_guarded(self):
        rows = (
            "Ruled: Ruled 1, combined net aggregates 1",
            "Ruled: Ruled 1, combined net sum 1",
            "Ruled: Ruled 1 in aggregates",
            "Ruled: Ruled 1, net aggregates 1",
            "Ruled: Ruled 1, combined overall aggregate 1",
            "Ruled: Ruled 1, combined overall aggregates 1",
            "Ruled: Ruled 1, combined net total 1",
            "Ruled: Ruled 1, grand aggregate 1",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")


class Step17Fix9BCrosswalkTailTest(unittest.TestCase):
    """CH-195, T9-16: the crosswalk tail still denotes one
    step past the CH-159 restated bound (attack9-10 cases
    g9-tail-four-tokens, g9-tail-noun-excl, and
    g9-tail-noun-question, and attack9-20 cases g01 to
    g07, g09 to g12, and g14)."""

    def test_fourth_trailing_token_denotes_nothing(self):
        rows = (
            "Ruled: Ruled 1, total 1 entries extra more again",
            "Ruled: Ruled 1, total 1 items counted extra more",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")

    def test_noun_at_fresh_joints_denotes_nothing(self):
        rows = (
            "Ruled: Ruled 1, total 1! entries",
            "Ruled: Ruled 1, total 1? entries",
            "Ruled: Ruled 1, total 1| entries",
            "Ruled: Ruled 1, total 1= entries",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")

    def test_second_token_at_semicolon_colon_joints(self):
        rows = (
            "Ruled: Ruled 1, total 1 entries; extra",
            "Ruled: Ruled 1, total 1 entries: extra",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")

    def test_third_token_at_comma_joint_denotes_nothing(self):
        model, state = _state(
            "\nRuled: Ruled 1, total 1 entries extra, more\n")
        self.assertNotIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Open")

    def test_comma_joint_token_not_closing_denotes_nothing(self):
        rows = (
            "Ruled: Ruled 1, total 1, extra more",
            "Ruled: Ruled 1, total 1 entries, extra more",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")

    def test_non_noun_token_at_semicolon_joint(self):
        model, state = _state(
            "\nRuled: Ruled 1, total 1; extra\n")
        self.assertNotIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Open")

    def test_third_token_after_period_ending_second(self):
        # Case g14, charged on its non ruling third word
        # form only: the word more is no ruling, and the
        # whole line denotes through its label.
        model, state = _state(
            "\nRuled: Ruled 1, total 1 entries extra. more\n")
        self.assertNotIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Open")

    def test_tail_controls_stay_guarded(self):
        rows = (
            "Ruled: Ruled 1, total 1 entries extra more",
            "Ruled: Ruled 1, total 1; entries",
            "Ruled: Ruled 1, total 1 entries/extra",
            "Ruled: Ruled 1, total 1 & entries",
            "Ruled: Ruled 1, total 1,, entries",
            "Ruled: Ruled 1, total 1 entries. extra",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")


class Step17Fix9BSumsPluralTest(unittest.TestCase):
    """CH-196, T9-35 (Low): the word sum stands admitted
    in the singular only under CH-161, so its plural
    still denotes (attack9-20 cases w9_07 and w9_08)."""

    def test_sums_plural_denotes_nothing(self):
        rows = (
            "Ruled: Ruled 1, sums 1",
            "Ruled: Ruled 1, grand sums 1",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")

    def test_sums_controls_stay_guarded(self):
        rows = (
            "Ruled: Ruled 1, aggregates 1",
            "Ruled: Ruled 1 in aggregates",
            "Ruled: Ruled 1, grand sum 1",
            "Ruled: Ruled 1, sum 1",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")


class Step17Fix9BCombinedScaleTest(unittest.TestCase):
    """The scale case g9-combined of seat 10: nine Banked
    head entries, three carrying control rows, two
    carrying guarded forms, and four carrying denoting
    rows of CH-193 to CH-195, reported Canonical Ruled 4
    against a hand truth of Open 9 on the uncured tree."""

    def test_combined_file_stays_open(self):
        rows = (
            "Ruled: Ruled 1, total 1",
            "Ruled | one two three four five six | 1 "
            "occurrence | entries: DQ-001",
            "Canonical Ruled: ;",
            "Ruled | one two three four five six seven | 1 "
            "occurrence | entries: DQ-001",
            "Ruled: Ruled 1, combined overall net total 1",
            "Ruled: Ruled 1, total 1 entries extra more again",
            "Ruled: Ruled 1, total 1! entries",
            "Ruled: Ruled 1, combined overall aggregate 1",
            "Ruled: Ruled 1, combined overall aggregates 1",
        )
        body = h._header_block()
        for index, row in enumerate(rows, start=1):
            body += "### DQ-%03d: Guard case %d\n\n" % (
                index, index)
            body += "Status: Banked\n\n"
            body += "Question: Which option should we "
            body += "take?\n\n"
            body += "Options: Option A, Option B\n\n"
            body += "Cost of deciding late: Work stays "
            body += "blocked.\n\n"
            body += "Blocks: none\n\n"
            body += "A plain context paragraph.\n\n"
            body += row + "\n\n"
        model, output = h.run_pipeline(
            body.encode("utf-8"), "b_combined.md")
        for index in range(1, 10):
            entry_id = "DQ-%03d" % index
            with self.subTest(entry=entry_id):
                result = h.entry_by_id(output, entry_id)
                self.assertEqual(
                    h.entry_state(result), "Open")
                self.assertNotIn(
                    "Ruled", _dispositions(model, entry_id))


class Step17Fix9BConfinementTest(unittest.TestCase):
    """CH-193 to CH-196 under the CH-15 segment awareness
    pin, in both directions: every widening stays confined
    to the row itself, so a genuine ruling standing in the
    widened forms company still counts."""

    def test_seven_token_kind_row_then_ruling_counts(self):
        model, state = _state(
            "\nSettled | at the line start position now "
            "today | 1 occurrence | entries: DQ-001. Ruled "
            "by Captain JP: take Option A.\n")
        self.assertNotIn("Settled", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_three_prefix_row_then_ruling_counts(self):
        model, state = _state(
            "\nSettled: Settled 1, combined net gross "
            "total 1. Ruled by Captain JP: take Option A.\n")
        self.assertNotIn("Settled", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_fourth_token_row_then_ruling_counts(self):
        model, state = _state(
            "\nSettled: Settled 1, total 1 entries extra "
            "more again. Ruled by Captain JP: take "
            "Option A.\n")
        self.assertNotIn("Settled", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_period_joint_edge_still_takes_no_ruling(self):
        model, state = _state(
            "\nSettled: Settled 1, total 1. Ruled by "
            "Captain JP: take Option A.\n")
        self.assertNotIn("Settled", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_ruling_after_period_ending_second_counts(self):
        # The g14 bound edge: a third word standing after
        # a period ending second token is row matter only
        # where it closes the line on its non ruling form,
        # so a genuine ruling standing there counts in
        # full.
        model, state = _state(
            "\nSettled: Settled 1, total 1 entries extra. "
            "Ruled by Captain JP: take Option A.\n")
        self.assertNotIn("Settled", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_comma_joint_ruling_edges_still_count(self):
        model, state = _state(
            "\nRuled: Ruled 1, total 1, Ruled by Captain "
            "JP: take Option A.\n")
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")
        model, state = _state(
            "\nSettled: Settled 1, total 1 entries, Ruled "
            "by Captain JP: take Option A.\n")
        self.assertNotIn("Settled", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_semicolon_joint_ruling_edge_still_counts(self):
        # A ruling standing at the semicolon joint second
        # token place, not closing the line, counts in
        # full on the same line closing bound.
        model, state = _state(
            "\nSettled: Settled 1, total 1 entries; Ruled "
            "by Captain JP: take Option A.\n")
        self.assertNotIn("Settled", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_matter_past_tally_row_still_denotes(self):
        model, state = _state(
            "\nRuled: Ruled 1, total 1 and the panel "
            "accepted the report.\n")
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")


class Step17Fix9BQuotedRulingStandingTest(unittest.TestCase):
    """Observation O-4-20-1 standing, unmoved by this
    cure: quoted genuine ruling lines still denote."""

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

    def test_segment_claim_line_still_denotes(self):
        model, state = _state(
            "\nClaim, reported as a claim: Ruled by "
            "Captain JP: take Option A.\n")
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")


class Step17Fix9BStandingPinTest(unittest.TestCase):
    """The fix wave 8 K4 pins on these limbs, standing as
    recorded before this cure and after it."""

    def test_wave8_tail_forms_stay_guarded(self):
        rows = (
            "Ruled: Ruled 1, total 1 entries extra more",
            "Ruled: Ruled 1, total 1 items counted extra",
            "Ruled: Ruled 1, total 1; entries",
            "Ruled: Ruled 1, total 1: entries",
            "Ruled: Ruled 1, total 1/entries",
            "Ruled: Ruled 1, total 1 entries, extra",
            "Ruled: Ruled 1, total 1, extra",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")

    def test_wave8_kind_forms_stay_guarded(self):
        rows = (
            "Ruled | at the line start position now | 1 "
            "occurrence | entries: DQ-001",
            "Ruled | one two three four five six | 1 "
            "occurrence | entries: DQ-001",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")

    def test_wave8_total_forms_stay_guarded(self):
        rows = (
            "Ruled: Ruled 1, combined net total 1",
            "Ruled: Ruled 1, very grand total 1",
            "Ruled: Ruled 1, grand aggregate 1",
            "Ruled: Ruled 1, aggregates 1",
            "Ruled: Ruled 1 in aggregates",
            "Ruled: Ruled 1, grand sum 1",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")

    def test_wave8_confinement_forms_stay_counting(self):
        cases = (
            "\nSettled: Settled 1, total 1 entries extra "
            "more. Ruled by Captain JP: take Option A.\n",
            "\nSettled: Settled 1, combined net total 1. "
            "Ruled by Captain JP: take Option A.\n",
            "\nSettled | at the line start position now | "
            "1 occurrence | entries: DQ-001. Ruled by "
            "Captain JP: take Option A.\n",
        )
        for body in cases:
            with self.subTest(body=body):
                model, state = _state(body)
                self.assertNotIn(
                    "Settled", _dispositions(model))
                self.assertIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Ruled")


if __name__ == "__main__":
    unittest.main()
