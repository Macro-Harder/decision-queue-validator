"""Step 17 fix wave 12, Fix Seat B tests.

Charges CH-322, CH-323, CH-324, CH-325, and CH-326,
Cluster B, the guard programme, as written at section
3 of design/steps/step-17r-r12-triage-prep.md, on the
round 12 paper of seat 09
(design/steps/step-17r-r12-seat09-run.md, findings
A12-09-F2 to A12-09-F6). Findings: T12-10 (seat 09
A12-09-F2, Medium), T12-11 (seat 09 A12-09-F3,
Medium), T12-12 (seat 09 A12-09-F4, Medium), T12-23
(seat 09 A12-09-F5, Low), and T12-24 (seat 09
A12-09-F6, Low).

Each surface width, stated in its own terms. Appendix
kind (CH-322): the kind slot stands as one to twelve
word tokens joined by whitespace between its pipes,
where CH-282 read one to ten. Total word prefix
(CH-323): up to seven word tokens other than the word
in standing before the total word at a non word joint
stand as its prefix, the same terms standing at the
word sum in both its forms, at the word aggregate in
its singular and plural forms, at the summation and
summations words, and the same seven word terms
standing before the word grand at the grand total
form, where CH-283 read up to six. Crosswalk tail
(CH-324): the trailing row matter after the final
count stands as at CH-284, with an eighth word token
standing after the seventh at a whitespace joint
where the first trailing token stands as the row
noun; with a sixth word token standing after a
period ending fifth token where it closes the line;
with a third word token standing after the second at
an exclamation joint itself followed by one further
word token at a whitespace joint closing the line;
with a fourth word token standing after the third at
an exclamation joint where it closes the line; with
a fifth word token standing after the fourth at a
colon, pipe, or exclamation joint where it closes
the line; with a sixth word token standing on the
after period chain, where the third token stands
after a period ending second token and three further
word tokens stand after it at whitespace joints and
the last closes the line; and with a first word
token that is no row noun standing at a tilde,
backtick, apostrophe, or caret joint where it closes
the line. Grand sums prefix (CH-325): the grand sums
form stands read at eight word tokens before the
word sums, the word grand counted among them, on a
grand alternative carrying up to seven word tokens
before the word grand itself, where CH-285 read
that form at the plain prefix width of six. Total
word set (CH-326): the words tally, aggregations,
and summarizations stand as total words beside the
words admitted at CH-283 and CH-286, in the plain
form and at the restated prefix width alike, where
no governing text admitted them before.

Both directions are pinned in this file. Recognition:
the charged rows denote nothing, and the host entry
stays Open. Confinement: a genuine ruling standing in
the widened forms company still counts, matter
standing past a tally row still denotes through its
label, and quoted genuine ruling lines still denote.
The guarded widths standing as pins are the ten token
kind, the six word prefixes, the restated CH-284 tail
forms, the grand sums width as restated at CH-285,
and the total, summation, summations, and aggregates
forms.

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


def _check_open(test, rows):
    for row in rows:
        with test.subTest(row=row):
            model, state = _state("\n" + row + "\n")
            test.assertNotIn("Ruled", _dispositions(model))
            test.assertEqual(state, "Open")


class Step17Fix12BAppendixKindTest(unittest.TestCase):
    """CH-322, T12-10: the appendix kind slot reads at
    most ten word tokens under CH-282, so a kind
    spelled in eleven or twelve tokens still denotes
    (attack12-09 cases g12-kind-eleven and
    g12-kind-twelve)."""

    def test_eleven_and_twelve_token_kinds(self):
        _check_open(self, (
            "Ruled | one two three four five six seven "
            "eight nine ten eleven | 1 occurrence | "
            "entries: DQ-001",
            "Ruled | one two three four five six seven "
            "eight nine ten eleven twelve | 1 occurrence "
            "| entries: DQ-001",
        ))

    def test_kind_pins_stay_guarded(self):
        _check_open(self, (
            "Ruled | one two three four five six seven "
            "eight nine ten | 1 occurrence | entries: "
            "DQ-001",
            "Ruled | one two three four five six seven "
            "eight nine | 1 occurrence | entries: DQ-001",
            "Ruled | one two three four five six seven "
            "eight | 1 occurrence | entries: DQ-001",
        ))


class Step17Fix12BTotalWordPrefixTest(unittest.TestCase):
    """CH-323, T12-11: the total word prefix reading
    admits up to six words under CH-283, so seven words
    standing before the total word, the grand total
    form, the word sum, the word aggregate, the
    aggregates plural, the sums plural, the summation
    word, or the summations word still denote
    (attack12-09 cases g12-prefix-seven,
    g12-prefix-seven-grand, g12-sum-prefix-seven,
    g12-aggregate-prefix-seven,
    g12-aggregates-prefix-seven, g12-sums-prefix-seven,
    g12-summation-prefix-seven, and
    g12-summations-prefix-seven)."""

    def test_seven_word_prefix_denotes_nothing(self):
        _check_open(self, (
            "Ruled: Ruled 1, one two three four five six "
            "seven total 1",
            "Ruled: Ruled 1, one two three four five six "
            "seven grand total 1",
            "Ruled: Ruled 1, one two three four five six "
            "seven sum 1",
            "Ruled: Ruled 1, one two three four five six "
            "seven aggregate 1",
            "Ruled: Ruled 1, one two three four five six "
            "seven aggregates 1",
            "Ruled: Ruled 1, one two three four five six "
            "seven sums 1",
            "Ruled: Ruled 1, one two three four five six "
            "seven summation 1",
            "Ruled: Ruled 1, one two three four five six "
            "seven summations 1",
        ))

    def test_prefix_pins_stay_guarded(self):
        _check_open(self, (
            "Ruled: Ruled 1, one two three four five six "
            "total 1",
            "Ruled: Ruled 1, one two three four five six "
            "grand total 1",
            "Ruled: Ruled 1, one two three four five six "
            "sums 1",
            "Ruled: Ruled 1, one two three four five "
            "summation 1",
        ))


class Step17Fix12BCrosswalkTailTest(unittest.TestCase):
    """CH-324, T12-12: the crosswalk tail still denotes
    one step past the CH-284 restated forms
    (attack12-09 cases g12-tail-eight-nounfirst,
    g12-tail-sixth-after-period,
    g12-tail-third-excl-followed, g12-tail-fourth-excl,
    g12-tail-fifth-colon, g12-tail-fifth-pipe,
    g12-tail-fifth-excl, g12-tail-afterperiod-six,
    g12-tail-nonnoun-tilde, g12-tail-nonnoun-backtick,
    g12-tail-nonnoun-apos, and
    g12-tail-nonnoun-caret)."""

    def test_eighth_token_noun_first_denotes_nothing(self):
        _check_open(self, (
            "Ruled: Ruled 1, total 1 entries extra more "
            "again plus once twice thrice",
        ))

    def test_sixth_after_period_denotes_nothing(self):
        _check_open(self, (
            "Ruled: Ruled 1, total 1 entries extra more "
            "again plus. once",
        ))

    def test_third_excl_followed_denotes_nothing(self):
        _check_open(self, (
            "Ruled: Ruled 1, total 1 entries extra! more "
            "again",
        ))

    def test_fourth_excl_denotes_nothing(self):
        _check_open(self, (
            "Ruled: Ruled 1, total 1 entries extra more! "
            "again",
        ))

    def test_fifth_at_fresh_joints_denote_nothing(self):
        _check_open(self, (
            "Ruled: Ruled 1, total 1 entries extra more "
            "again: plus",
            "Ruled: Ruled 1, total 1 entries extra more "
            "again| plus",
            "Ruled: Ruled 1, total 1 entries extra more "
            "again! plus",
        ))

    def test_afterperiod_six_denotes_nothing(self):
        _check_open(self, (
            "Ruled: Ruled 1, total 1 entries extra. more "
            "again plus once",
        ))

    def test_non_noun_first_at_fresh_joints(self):
        _check_open(self, (
            "Ruled: Ruled 1, total 1~ extra",
            "Ruled: Ruled 1, total 1` extra",
            "Ruled: Ruled 1, total 1' extra",
            "Ruled: Ruled 1, total 1^ extra",
        ))

    def test_tail_pins_stay_guarded(self):
        _check_open(self, (
            "Ruled: Ruled 1, total 1 entries extra more "
            "again plus once twice",
            "Ruled: Ruled 1, total 1 entries extra more "
            "again fifth",
            "Ruled: Ruled 1, total 1 entries| extra",
            "Ruled: Ruled 1, total 1 entries extra; more",
            "Ruled: Ruled 1, total 1 entries extra! more",
            "Ruled: Ruled 1, total 1: extra",
        ))


class Step17Fix12BGrandSumsPrefixTest(unittest.TestCase):
    """CH-325, T12-23 (Low): the grand sums form with
    seven or eight tokens standing before the word
    sums denotes, where the form stands read at the
    plain prefix width of six under CH-285
    (attack12-09 cases g12-grand-sums-seven-tokens and
    g12-grand-sums-eight-tokens)."""

    def test_seven_and_eight_tokens_before_sums(self):
        _check_open(self, (
            "Ruled: Ruled 1, one two three four five six "
            "grand sums 1",
            "Ruled: Ruled 1, one two three four five six "
            "seven grand sums 1",
        ))

    def test_grand_sums_pins_stay_guarded(self):
        _check_open(self, (
            "Ruled: Ruled 1, one two three four five "
            "grand sums 1",
            "Ruled: Ruled 1, combined overall net gross "
            "grand sums 1",
            "Ruled: Ruled 1, grand sums 1",
            "Ruled: Ruled 1 in grand sums",
        ))


class Step17Fix12BTotalWordSetTest(unittest.TestCase):
    """CH-326, T12-24 (Low): the words tally,
    aggregations, and summarizations standing as the
    total word denote, where the plain total form is
    guarded (attack12-09 cases g12-tally-word,
    g12-aggregations-word, and
    g12-summarizations-word)."""

    def test_neighbour_words_denote_nothing(self):
        _check_open(self, (
            "Ruled: Ruled 1, tally 1",
            "Ruled: Ruled 1, aggregations 1",
            "Ruled: Ruled 1, summarizations 1",
        ))

    def test_total_word_pins_stay_guarded(self):
        _check_open(self, (
            "Ruled: Ruled 1, total 1",
            "Ruled: Ruled 1, summation 1",
            "Ruled: Ruled 1, summations 1",
            "Ruled: Ruled 1, aggregates 1",
            "Ruled: Ruled 1, grand total 1",
        ))


class Step17Fix12BCombinedScaleTest(unittest.TestCase):
    """The scale case g12-combined of seat 09: nine
    Banked head entries, five carrying the denoting
    rows of CH-322 to CH-325 and four carrying control
    and guarded rows, reported Canonical Ruled 5,
    Open 4 against a hand truth of Open 9 on the
    uncured tree."""

    def test_combined_file_stays_open(self):
        rows = (
            "Ruled | one two three four five six seven "
            "eight nine ten eleven | 1 occurrence | "
            "entries: DQ-001",
            "Ruled: Ruled 1, one two three four five six "
            "seven total 1",
            "Ruled: Ruled 1, total 1 entries extra more "
            "again plus once twice thrice",
            "Ruled: Ruled 1, one two three four five six "
            "grand sums 1",
            "Ruled: Ruled 1, total 1~ extra",
            "Ruled | one two three four five six seven "
            "eight nine ten | 1 occurrence | entries: "
            "DQ-001",
            "Ruled: Ruled 1, one two three four five six "
            "total 1",
            "Ruled: Ruled 1, total 1 entries extra more "
            "again plus once twice",
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


class Step17Fix12BConfinementTest(unittest.TestCase):
    """CH-322 to CH-326 under the CH-15 segment
    awareness pin, in both directions: every widening
    stays confined to the row itself, so a genuine
    ruling standing in the widened forms company still
    counts."""

    def test_twelve_token_kind_row_then_ruling(self):
        model, state = _state(
            "\nSettled | one two three four five six "
            "seven eight nine ten eleven twelve | 1 "
            "occurrence | entries: DQ-001. Ruled by "
            "Captain JP: take Option A.\n")
        self.assertNotIn("Settled", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_seven_prefix_row_then_ruling_counts(self):
        model, state = _state(
            "\nSettled: Settled 1, one two three four "
            "five six seven total 1. Ruled by Captain "
            "JP: take Option A.\n")
        self.assertNotIn("Settled", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_eight_token_tail_row_then_ruling(self):
        model, state = _state(
            "\nSettled: Settled 1, total 1 entries extra "
            "more again plus once twice thrice. Ruled by "
            "Captain JP: take Option A.\n")
        self.assertNotIn("Settled", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_grand_sums_eight_row_then_ruling(self):
        model, state = _state(
            "\nSettled: Settled 1, one two three four "
            "five six seven grand sums 1. Ruled by "
            "Captain JP: take Option A.\n")
        self.assertNotIn("Settled", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_tally_row_then_ruling_counts(self):
        model, state = _state(
            "\nSettled: Settled 1, tally 1. Ruled by "
            "Captain JP: take Option A.\n")
        self.assertNotIn("Settled", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_matter_past_tally_row_still_denotes(self):
        model, state = _state(
            "\nRuled: Ruled 1, total 1 and the panel "
            "accepted the report.\n")
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")


class Step17Fix12BQuotedRulingStandingTest(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
