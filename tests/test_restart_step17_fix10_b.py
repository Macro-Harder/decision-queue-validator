"""Step 17 fix wave 10, Fix Seat B tests.

Charges CH-234, CH-235, CH-236, CH-237, and CH-238,
Cluster B, the guard programme limbs, ruled TO FIX at
section 83 of design/steps/step-17r-record.md, adopting
the consolidation of design/steps/step-17r-r10-triage-
prep.md Cluster B. Findings: T10-08 (seat 10 A10-10-F2
and seat 20 F-20-10-2, Medium), T10-09 (seat 10
A10-10-F3 and seat 20 F-20-10-3, Medium), T10-10 (seat
10 A10-10-F4 and seat 20 F-20-10-1, Medium), T10-25
(seat 10 A10-10-F5, Low), and T10-26 (seat 20
F-20-10-4, Low). Source papers:
design/steps/step-17r-r10-seat10.md and
design/steps/step-17r-r10-seat20.md.

Each surface width, stated in its own terms. Appendix
kind (CH-234): the kind slot stands as one to eight
word tokens joined by whitespace between its pipes,
where CH-193 read one to seven. Total word prefix
(CH-235): up to four word tokens other than the word
in standing before the total word at a non word joint
stand as its prefix, the same terms standing at the
word sum in both its forms and at the word aggregate
in its singular and plural forms, and the same four
word terms standing before the word grand at the
grand total form, where CH-194 read up to three.
Crosswalk tail
(CH-236): the trailing row matter after the final
count stands as at CH-195, with a fifth word token
standing after the fourth at a whitespace joint; with
the row noun standing also at an at sign, hash, tilde,
plus, percent, caret, dollar, asterisk, backslash,
opening parenthesis, or double quote joint; with a
second word token standing after the first at a pipe,
exclamation, or question joint where that token closes
the line; with a second word token standing after the
first at a semicolon or colon joint followed by its
one closing whitespace token; with a third word token
standing after the second at a semicolon, colon, or
pipe joint where that token closes the line; with a
fourth word token standing after the third at a comma
joint where it closes the line, or standing after a
period ending third token where it closes the line;
with a first word token that is no row noun standing
at a colon joint where it closes the line, beside the
pipe, exclamation, and question forms; and with a
comma joint token followed by two further word tokens
where the last closes the line, at the first token
place and at the second token place alike. Grand sums
prefix (CH-237): the grand sums form with three words
standing before the word grand, which stands four word
tokens before the word sums and is cured at the
CH-235 prefix limb on those same terms; the one and
two word forms at that point stand guarded in the
controls, as seat 10 records their measured reach.
Summation word (CH-238): the word summation stands as
a total word beside total, sum, and aggregate, where
the CH-194 and CH-196 reading carried no such form;
the totals plural and the subtotals form stand
guarded in the controls, as seat 20 records them.

Both directions are pinned in this file. Recognition:
the charged rows denote nothing, and the host entry
stays Open. Confinement: a genuine ruling standing in
the widened forms company still counts, in the forms
the earlier waves charged and in the new bound forms
this cure states at their line closing and noun edges,
matter standing past a tally row still denotes through
its label, and quoted genuine ruling lines still
denote. The fix wave 9 B pins on these limbs stand
whole, restated in the standing pin class below.

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


class Step17Fix10BAppendixKindTest(unittest.TestCase):
    """CH-234, T10-08: the appendix kind slot reads at
    most seven word tokens under CH-193, so a kind
    spelled in eight tokens still denotes (attack10-10
    case g10-kind-eight and attack10-20 case y01)."""

    def test_eight_token_kinds_denote_nothing(self):
        rows = (
            "Ruled | one two three four five six seven "
            "eight | 1 occurrence | entries: DQ-001",
            "Ruled | at the line start position now today "
            "again | 1 occurrence | entries: DQ-001",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")

    def test_kind_controls_stay_guarded(self):
        rows = (
            "Ruled | one two three four five six seven | 1 "
            "occurrence | entries: DQ-001",
            "Ruled | at the line start position now today | "
            "1 occurrence | entries: DQ-001",
            "Ruled | at the line start position now to-day "
            "| 1 occurrence | entries: DQ-001",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")


class Step17Fix10BTotalWordPrefixTest(unittest.TestCase):
    """CH-235, T10-09: the total word prefix reading
    admits up to three words under CH-194, so four words
    standing before the total word, the grand total
    form, the word sum, the word aggregate, the
    aggregates plural, or the sums plural still denote
    (attack10-10 cases g10-prefix-four,
    g10-prefix-four-grand, g10-sum-prefix-four,
    g10-aggregate-prefix-four,
    g10-aggregates-prefix-four, and
    g10-sums-prefix-four, and attack10-20 cases z01b,
    z02, z03, z04, and z05)."""

    def test_four_word_prefix_denotes_nothing(self):
        rows = (
            "Ruled: Ruled 1, combined overall net gross "
            "total 1",
            "Ruled: Ruled 1, one two three four grand "
            "total 1",
            "Ruled: Ruled 1, combined overall net gross "
            "sum 1",
            "Ruled: Ruled 1, combined overall net gross "
            "aggregate 1",
            "Ruled: Ruled 1, combined overall net gross "
            "aggregates 1",
            "Ruled: Ruled 1, combined overall net gross "
            "sums 1",
            "Ruled: Ruled 1, one two three four total 1",
            "Ruled: Ruled 1, one two three grand total 1",
            "Ruled: Ruled 1, one two three four "
            "aggregates 1",
            "Ruled: Ruled 1, one two three four sum 1",
            "Ruled: Ruled 1, one two three four sums 1",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")

    def test_prefix_controls_stay_guarded(self):
        rows = (
            "Ruled: Ruled 1, combined overall net total 1",
            "Ruled: Ruled 1, combined net gross sums 1",
            "Ruled: Ruled 1, net sums 1",
            "Ruled: Ruled 1 in sums",
            "Ruled: Ruled 1, combined overall net sums 1",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")


class Step17Fix10BCrosswalkTailTest(unittest.TestCase):
    """CH-236, T10-10: the crosswalk tail still denotes
    one step past the CH-195 restated forms
    (attack10-10 cases g10-tail-five-tokens,
    g10-tail-five-noun-first, g10-tail-noun-at,
    g10-tail-noun-hash, g10-tail-noun-tilde,
    g10-tail-noun-plus, g10-tail-noun-percent,
    g10-tail-noun-caret, g10-tail-noun-dollar,
    g10-tail-noun-star, g10-tail-noun-backslash,
    g10-tail-noun-lparen, g10-tail-noun-dquote,
    g10-tail-second-pipe, g10-tail-second-excl,
    g10-tail-second-question, g10-tail-third-semicolon,
    g10-tail-third-colon, g10-tail-third-pipe,
    g10-tail-fourth-comma-close,
    g10-tail-fourth-after-period, g10-tail-nonnoun-pipe,
    g10-tail-nonnoun-excl, and g10-tail-nonnoun-question,
    and attack10-20 cases x01 to x04, x06 to x09, x11
    to x13, x15 to x22, and x24 as grouped at section
    2.5 of the triage preparation)."""

    def test_fifth_trailing_token_denotes_nothing(self):
        rows = (
            "Ruled: Ruled 1, total 1 items counted extra "
            "more again",
            "Ruled: Ruled 1, total 1 entries extra more "
            "again plus",
            "Ruled: Ruled 1, total 1 entries extra more "
            "again fifth",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")

    def test_noun_at_fresh_joints_denotes_nothing(self):
        rows = (
            "Ruled: Ruled 1, total 1@ entries",
            "Ruled: Ruled 1, total 1# entries",
            "Ruled: Ruled 1, total 1~ entries",
            "Ruled: Ruled 1, total 1+ entries",
            "Ruled: Ruled 1, total 1% entries",
            "Ruled: Ruled 1, total 1^ entries",
            "Ruled: Ruled 1, total 1$ entries",
            "Ruled: Ruled 1, total 1* entries",
            "Ruled: Ruled 1, total 1\\ entries",
            "Ruled: Ruled 1, total 1( entries",
            'Ruled: Ruled 1, total 1" entries',
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")

    def test_second_token_at_fresh_joints(self):
        rows = (
            "Ruled: Ruled 1, total 1 entries| extra",
            "Ruled: Ruled 1, total 1 entries! extra",
            "Ruled: Ruled 1, total 1 entries? extra",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")

    def test_third_token_at_fresh_joints(self):
        rows = (
            "Ruled: Ruled 1, total 1 entries extra; more",
            "Ruled: Ruled 1, total 1 entries extra: more",
            "Ruled: Ruled 1, total 1 entries extra| more",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")

    def test_fourth_token_comma_and_period_forms(self):
        rows = (
            "Ruled: Ruled 1, total 1 entries extra more, "
            "again",
            "Ruled: Ruled 1, total 1 entries extra. more "
            "again",
            "Ruled: Ruled 1, total 1 entries extra more. "
            "again",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")

    def test_non_noun_first_token_at_fresh_joints(self):
        rows = (
            "Ruled: Ruled 1, total 1| extra",
            "Ruled: Ruled 1, total 1! extra",
            "Ruled: Ruled 1, total 1? extra",
            "Ruled: Ruled 1, total 1: extra",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")

    def test_comma_joint_token_two_following(self):
        rows = (
            "Ruled: Ruled 1, total 1, extra more again",
            "Ruled: Ruled 1, total 1 entries, extra more "
            "again",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")

    def test_second_token_semicolon_colon_followed(self):
        rows = (
            "Ruled: Ruled 1, total 1 entries; extra more",
            "Ruled: Ruled 1, total 1 entries: extra more",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")

    def test_tail_controls_stay_guarded(self):
        rows = (
            "Ruled: Ruled 1, total 1 items counted extra "
            "more",
            "Ruled: Ruled 1, total 1 & entries",
            "Ruled: Ruled 1, total 1 entries= extra",
            "Ruled: Ruled 1, total 1_ entries",
            "Ruled: Ruled 1, total 1 entries extra/more",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")


class Step17Fix10BGrandSumsPrefixTest(unittest.TestCase):
    """CH-237, T10-25 (Low): the grand sums form with
    three words standing before the word grand denotes,
    where the one and two word forms stand guarded
    (attack10-10 case g10-grand-sums-prefix-three, with
    controls g10-grand-sums-one-prefix,
    g10-grand-sums-two-prefix, g10-grand-sums-control,
    and g10-in-grand-sums)."""

    def test_three_words_before_grand_sums(self):
        model, state = _state(
            "\nRuled: Ruled 1, combined overall net grand "
            "sums 1\n")
        self.assertNotIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Open")

    def test_grand_sums_prefix_controls(self):
        rows = (
            "Ruled: Ruled 1, overall grand sums 1",
            "Ruled: Ruled 1, combined overall grand sums 1",
            "Ruled: Ruled 1, grand sums 1",
            "Ruled: Ruled 1 in grand sums",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")


class Step17Fix10BSummationWordTest(unittest.TestCase):
    """CH-238, T10-26 (Low): the total word reading
    carries total, sum, and aggregate in the forms
    CH-194 and CH-196 name, so the word summation
    standing as the total word still denotes
    (attack10-20 case z09, with controls z07 and z08)."""

    def test_summation_denotes_nothing(self):
        model, state = _state(
            "\nRuled: Ruled 1, summation 1\n")
        self.assertNotIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Open")

    def test_summation_neighbour_controls(self):
        rows = (
            "Ruled: Ruled 1, totals 1",
            "Ruled: Ruled 1, subtotals 1",
            "Ruled: Ruled 1, subtotal 1",
            "Ruled: Ruled 1, sums 1",
            "Ruled: Ruled 1, total 1",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")


class Step17Fix10BCombinedScaleTest(unittest.TestCase):
    """The scale case g10-combined of seat 10: nine
    Banked head entries, five carrying control and
    guarded rows and four carrying denoting rows of
    CH-234 to CH-236, reported Canonical Ruled 4, Open 5
    against a hand truth of Open 9 on the uncured tree."""

    def test_combined_file_stays_open(self):
        rows = (
            "Ruled | one two three four five six seven "
            "eight | 1 occurrence | entries: DQ-001",
            "Ruled: Ruled 1, combined overall net gross "
            "total 1",
            "Ruled: Ruled 1, total 1 items counted extra "
            "more again",
            "Ruled: Ruled 1, overall grand sums 1",
            "Ruled: Ruled 1, total 1@ entries",
            "Ruled | one two three four five six seven | "
            "1 occurrence | entries: DQ-001",
            "Ruled: Ruled 1, sums 1",
            "Ruled: Ruled 1, total 1 items counted extra "
            "more",
            "Ruled: Ruled 1, total 1",
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


class Step17Fix10BConfinementTest(unittest.TestCase):
    """CH-234 to CH-238 under the CH-15 segment awareness
    pin, in both directions: every widening stays
    confined to the row itself, so a genuine ruling
    standing in the widened forms company still
    counts."""

    def test_eight_token_kind_row_then_ruling_counts(self):
        model, state = _state(
            "\nSettled | one two three four five six seven "
            "eight | 1 occurrence | entries: DQ-001. Ruled "
            "by Captain JP: take Option A.\n")
        self.assertNotIn("Settled", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_four_prefix_row_then_ruling_counts(self):
        model, state = _state(
            "\nSettled: Settled 1, one two three four "
            "total 1. Ruled by Captain JP: take Option A.\n")
        self.assertNotIn("Settled", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_fifth_token_row_then_ruling_counts(self):
        model, state = _state(
            "\nSettled: Settled 1, total 1 entries extra "
            "more again fifth. Ruled by Captain JP: take "
            "Option A.\n")
        self.assertNotIn("Settled", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_grand_sums_prefix_row_then_ruling(self):
        model, state = _state(
            "\nSettled: Settled 1, combined overall net "
            "grand sums 1. Ruled by Captain JP: take "
            "Option A.\n")
        self.assertNotIn("Settled", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_summation_row_then_ruling_counts(self):
        model, state = _state(
            "\nSettled: Settled 1, summation 1. Ruled by "
            "Captain JP: take Option A.\n")
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
        model, state = _state(
            "\nSettled: Settled 1, total 1 entries extra. "
            "Ruled by Captain JP: take Option A.\n")
        self.assertNotIn("Settled", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_noun_joint_ruling_edge_still_counts(self):
        model, state = _state(
            "\nSettled: Settled 1, total 1@ Ruled by "
            "Captain JP: take Option A.\n")
        self.assertNotIn("Settled", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_second_token_joint_ruling_edge_counts(self):
        model, state = _state(
            "\nSettled: Settled 1, total 1 entries| Ruled "
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


class Step17Fix10BQuotedRulingStandingTest(unittest.TestCase):
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


class Step17Fix10BStandingPinTest(unittest.TestCase):
    """The fix wave 9 B pins on these limbs, standing as
    recorded before this cure and after it."""

    def test_wave9_tail_forms_stay_guarded(self):
        rows = (
            "Ruled: Ruled 1, total 1 entries extra more "
            "again",
            "Ruled: Ruled 1, total 1! entries",
            "Ruled: Ruled 1, total 1? entries",
            "Ruled: Ruled 1, total 1 entries; extra",
            "Ruled: Ruled 1, total 1 entries: extra",
            "Ruled: Ruled 1, total 1 entries extra, more",
            "Ruled: Ruled 1, total 1, extra more",
            "Ruled: Ruled 1, total 1 entries, extra more",
            "Ruled: Ruled 1, total 1; extra",
            "Ruled: Ruled 1, total 1 entries extra. more",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")

    def test_wave9_kind_forms_stay_guarded(self):
        rows = (
            "Ruled | one two three four five six seven | 1 "
            "occurrence | entries: DQ-001",
            "Ruled | at the line start position now today | "
            "1 occurrence | entries: DQ-001",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")

    def test_wave9_total_forms_stay_guarded(self):
        rows = (
            "Ruled: Ruled 1, combined overall net total 1",
            "Ruled: Ruled 1, very truly grand total 1",
            "Ruled: Ruled 1, combined net gross aggregates "
            "1",
            "Ruled: Ruled 1, sums 1",
            "Ruled: Ruled 1, grand sums 1",
            "Ruled: Ruled 1, grand aggregate 1",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")

    def test_wave9_confinement_forms_stay_counting(self):
        cases = (
            "\nSettled | at the line start position now "
            "today | 1 occurrence | entries: DQ-001. Ruled "
            "by Captain JP: take Option A.\n",
            "\nSettled: Settled 1, combined net gross "
            "total 1. Ruled by Captain JP: take Option A.\n",
            "\nSettled: Settled 1, total 1 entries extra "
            "more again. Ruled by Captain JP: take "
            "Option A.\n",
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
