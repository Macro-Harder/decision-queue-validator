"""Step 17 fix wave 11, Fix Seat B tests.

Charges CH-282, CH-283, CH-284, CH-285, and CH-286,
Cluster B, the guard programme, ruled TO FIX at record
section 108, adopting the consolidation of
design/steps/step-17r-r11-triage-prep.md Cluster B.
Findings: T11-09 (seat 10 A11-10-F2 and seat 20
F-20-11-2, Medium), T11-10 (seat 10 A11-10-F3 and
seat 20 F-20-11-3, with seat 20 F-20-11-4's summation
prefix members, Medium), T11-11 (seat 10 A11-10-F4
and seat 20 F-20-11-1, Medium), T11-22 (seat 10
A11-10-F5, Low), and T11-23 (seat 10 A11-10-F6 and
seat 20 F-20-11-4's plural members, Low). Source
papers: design/steps/step-17r-r11-seat10-run.md and
design/steps/step-17r-r11-seat20-run.md.

Each surface width, stated in its own terms. Appendix
kind (CH-282): the kind slot stands as one to ten
word tokens joined by whitespace between its pipes,
where CH-234 read one to eight. Total word prefix
(CH-283): up to six word tokens other than the word
in standing before the total word at a non word joint
stand as its prefix, the same terms standing at the
word sum in both its forms, at the word aggregate in
its singular and plural forms, at the summation word,
and the same six word terms standing before the word
grand at the grand total form, where CH-235 read up
to four. Crosswalk tail (CH-284): the trailing row
matter after the final count stands as at CH-236,
with a sixth and a seventh word token standing after
the fifth at a whitespace joint where the first
trailing token stands as the row noun; with the row noun
standing also at an ampersand, apostrophe, less than,
greater than, backtick, left bracket, right brace,
double angle quotation, euro, pound, section, or
bullet joint; with a second word token standing after
the first at a pipe, exclamation, or question joint
followed by one further closing whitespace token;
with a third word token standing after the second at
an exclamation or question joint where it closes the
line; with a fourth word token standing after the
third at a semicolon, colon, pipe, or question joint
where it closes the line; with a fifth word token
standing after the fourth at a comma or semicolon
joint where it closes the line, or standing after a
period ending fourth token where it closes the line;
with a comma joint token followed by three further
word tokens where the last closes the line; with a
semicolon joint token followed by two further word
tokens where the last closes the line; and with a
first word token that is no row noun standing at an
equals, slash, or hyphen joint where it closes the
line. Grand sums prefix (CH-285): the grand sums form
with four words standing before the word grand, which
stands six word tokens before the word sums at the
restated plain prefix width of CH-283, the word grand
counted among them, where CH-237 read that form at
the plain width of four. Summations word (CH-286):
the word summations stands as a total word beside the
word summation in its plain form, where CH-238
admitted the plain form only.

Both directions are pinned in this file. Recognition:
the charged rows denote nothing, and the host entry
stays Open. Confinement: a genuine ruling standing in
the widened forms company still counts, matter
standing past a tally row still denotes through its
label, and quoted genuine ruling lines still denote.
The guarded widths standing as pins are the eight
token kind, the four word prefixes, the restated
CH-236 tail forms, the grand sums width as restated
at CH-237, and the plain summation form.

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


class Step17Fix11BAppendixKindTest(unittest.TestCase):
    """CH-282, T11-09: the appendix kind slot reads at
    most eight word tokens under CH-234, so a kind
    spelled in nine or ten tokens still denotes
    (attack11-10 case g11-kind-nine and attack11-20
    cases k01 and own_k01)."""

    def test_nine_and_ten_token_kinds_denote_nothing(self):
        _check_open(self, (
            "Ruled | one two three four five six seven "
            "eight nine | 1 occurrence | entries: DQ-001",
            "Ruled | at the line start position now today "
            "again extra | 1 occurrence | entries: DQ-001",
            "Ruled | at the line start position now today "
            "again extra more | 1 occurrence | entries: "
            "DQ-001",
        ))

    def test_kind_pins_stay_guarded(self):
        _check_open(self, (
            "Ruled | one two three four five six seven "
            "eight | 1 occurrence | entries: DQ-001",
            "Ruled | one two three four five six seven | 1 "
            "occurrence | entries: DQ-001",
            "Ruled | at the line start position now today | "
            "1 occurrence | entries: DQ-001",
        ))


class Step17Fix11BTotalWordPrefixTest(unittest.TestCase):
    """CH-283, T11-10: the total word prefix reading
    admits up to four words under CH-235, so five and
    six words standing before the total word, the grand
    total form, the word sum, the word aggregate, the
    aggregates plural, the sums plural, the grand sums
    form, or the summation word still denote
    (attack11-10 cases g11-prefix-five,
    g11-prefix-five-grand, g11-sum-prefix-five,
    g11-aggregate-prefix-five,
    g11-aggregates-prefix-five, g11-sums-prefix-five,
    and g11-summation-prefix-five, and attack11-20
    cases p01 to p07 and own_p01 to own_p06)."""

    def test_five_word_prefix_denotes_nothing(self):
        _check_open(self, (
            "Ruled: Ruled 1, combined overall net gross "
            "alpha total 1",
            "Ruled: Ruled 1, one two three four five "
            "total 1",
            "Ruled: Ruled 1, one two three four five grand "
            "total 1",
            "Ruled: Ruled 1, combined overall net gross "
            "alpha sum 1",
            "Ruled: Ruled 1, combined overall net gross "
            "alpha aggregate 1",
            "Ruled: Ruled 1, combined overall net gross "
            "alpha aggregates 1",
            "Ruled: Ruled 1, combined overall net gross "
            "alpha sums 1",
            "Ruled: Ruled 1, combined overall net gross "
            "alpha summation 1",
            "Ruled: Ruled 1, one two three four grand "
            "sums 1",
        ))

    def test_six_word_prefix_denotes_nothing(self):
        _check_open(self, (
            "Ruled: Ruled 1, one two three four five six "
            "total 1",
            "Ruled: Ruled 1, one two three four five six "
            "grand total 1",
            "Ruled: Ruled 1, one two three four five six "
            "aggregates 1",
            "Ruled: Ruled 1, one two three four five six "
            "sum 1",
            "Ruled: Ruled 1, one two three four five six "
            "sums 1",
            "Ruled: Ruled 1, one two three four five six "
            "summation 1",
        ))

    def test_prefix_pins_stay_guarded(self):
        _check_open(self, (
            "Ruled: Ruled 1, combined overall net gross "
            "total 1",
            "Ruled: Ruled 1, one two three four grand "
            "total 1",
            "Ruled: Ruled 1, combined overall net gross "
            "sums 1",
            "Ruled: Ruled 1, one two three four summation 1",
            "Ruled: Ruled 1, combined overall net total 1",
        ))


class Step17Fix11BCrosswalkTailTest(unittest.TestCase):
    """CH-284, T11-11: the crosswalk tail still denotes
    one step past the CH-236 restated forms
    (attack11-10 cases g11-tail-six-tokens,
    g11-tail-six-noun-first, g11-tail-noun-backtick,
    g11-tail-noun-apos, g11-tail-noun-lt,
    g11-tail-noun-gt, g11-tail-noun-laquo,
    g11-tail-noun-raquo, g11-tail-noun-euro,
    g11-tail-noun-pound, g11-tail-noun-section,
    g11-tail-noun-bullet,
    g11-tail-second-pipe-followed,
    g11-tail-second-excl-followed,
    g11-tail-second-question-followed,
    g11-tail-third-excl, g11-tail-third-question,
    g11-tail-fourth-semicolon, g11-tail-fourth-colon,
    g11-tail-fourth-pipe, g11-tail-fifth-comma,
    g11-tail-fifth-after-period,
    g11-tail-nonnoun-equals, and g11-tail-nonnoun-slash,
    and attack11-20 cases t01 to t08, t13 to t22,
    own_t01, own_t05, and own_t06)."""

    def test_sixth_and_seventh_tokens_denote_nothing(self):
        _check_open(self, (
            "Ruled: Ruled 1, total 1 entries extra more "
            "again plus once",
            "Ruled: Ruled 1, total 1 items counted extra "
            "more again plus",
            "Ruled: Ruled 1, total 1 entries extra more "
            "again fifth sixth",
            "Ruled: Ruled 1, total 1 entries extra more "
            "again fifth sixth seventh",
        ))

    def test_noun_at_fresh_joints_denotes_nothing(self):
        _check_open(self, (
            "Ruled: Ruled 1, total 1` entries",
            "Ruled: Ruled 1, total 1' entries",
            "Ruled: Ruled 1, total 1< entries",
            "Ruled: Ruled 1, total 1> entries",
            "Ruled: Ruled 1, total 1« entries",
            "Ruled: Ruled 1, total 1» entries",
            "Ruled: Ruled 1, total 1€ entries",
            "Ruled: Ruled 1, total 1£ entries",
            "Ruled: Ruled 1, total 1§ entries",
            "Ruled: Ruled 1, total 1• entries",
            "Ruled: Ruled 1, total 1& entries",
            "Ruled: Ruled 1, total 1[ entries",
            "Ruled: Ruled 1, total 1} entries",
        ))

    def test_second_token_followed_denotes_nothing(self):
        _check_open(self, (
            "Ruled: Ruled 1, total 1 entries| extra more",
            "Ruled: Ruled 1, total 1 entries! extra more",
            "Ruled: Ruled 1, total 1 entries? extra more",
        ))

    def test_third_token_at_fresh_joints(self):
        _check_open(self, (
            "Ruled: Ruled 1, total 1 entries extra! more",
            "Ruled: Ruled 1, total 1 entries extra? more",
        ))

    def test_fourth_token_at_fresh_joints(self):
        _check_open(self, (
            "Ruled: Ruled 1, total 1 entries extra more; "
            "again",
            "Ruled: Ruled 1, total 1 entries extra more: "
            "again",
            "Ruled: Ruled 1, total 1 entries extra more| "
            "again",
            "Ruled: Ruled 1, total 1 entries extra more? "
            "again",
        ))

    def test_fifth_token_forms_denote_nothing(self):
        _check_open(self, (
            "Ruled: Ruled 1, total 1 entries extra more "
            "again, plus",
            "Ruled: Ruled 1, total 1 entries extra. more "
            "again plus",
            "Ruled: Ruled 1, total 1 entries extra more "
            "again, fifth",
            "Ruled: Ruled 1, total 1 entries extra more "
            "again. fifth",
            "Ruled: Ruled 1, total 1 entries extra more "
            "again; fifth",
        ))

    def test_comma_and_semicolon_followed_forms(self):
        _check_open(self, (
            "Ruled: Ruled 1, total 1, extra more again "
            "fifth",
            "Ruled: Ruled 1, total 1 entries; extra more "
            "again",
        ))

    def test_non_noun_first_at_fresh_joints(self):
        _check_open(self, (
            "Ruled: Ruled 1, total 1= extra",
            "Ruled: Ruled 1, total 1/ extra",
            "Ruled: Ruled 1, total 1- extra",
        ))

    def test_tail_pins_stay_guarded(self):
        _check_open(self, (
            "Ruled: Ruled 1, total 1 entries extra more "
            "again fifth",
            "Ruled: Ruled 1, total 1@ entries",
            "Ruled: Ruled 1, total 1 entries| extra",
            "Ruled: Ruled 1, total 1 entries extra; more",
            "Ruled: Ruled 1, total 1 items counted extra "
            "more",
            "Ruled: Ruled 1, total 1: extra",
        ))


class Step17Fix11BGrandSumsPrefixTest(unittest.TestCase):
    """CH-285, T11-22 (Low): the grand sums form with
    four words standing before the word grand denotes,
    where the three word form stands cured at CH-237
    (attack11-10 case g11-grand-sums-prefix-four)."""

    def test_four_words_before_grand_sums(self):
        model, state = _state(
            "\nRuled: Ruled 1, combined overall net gross "
            "grand sums 1\n")
        self.assertNotIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Open")

    def test_grand_sums_pins_stay_guarded(self):
        _check_open(self, (
            "Ruled: Ruled 1, combined overall net grand "
            "sums 1",
            "Ruled: Ruled 1, overall grand sums 1",
            "Ruled: Ruled 1, grand sums 1",
            "Ruled: Ruled 1 in grand sums",
        ))


class Step17Fix11BSummationsWordTest(unittest.TestCase):
    """CH-286, T11-23 (Low): the summations plural
    standing as the total word denotes, where the plain
    summation form stands guarded at CH-238
    (attack11-10 case g11-summations and attack11-20
    cases p08 and own_p07)."""

    def test_summations_denotes_nothing(self):
        _check_open(self, (
            "Ruled: Ruled 1, summations 1",
            "Ruled: Ruled 1, one two summations 1",
        ))

    def test_summation_pins_stay_guarded(self):
        _check_open(self, (
            "Ruled: Ruled 1, summation 1",
            "Ruled: Ruled 1, grand summation 1",
            "Ruled: Ruled 1, totals 1",
            "Ruled: Ruled 1, total 1",
        ))


class Step17Fix11BCombinedScaleTest(unittest.TestCase):
    """The scale case g11-combined of seat 10: nine
    Banked head entries, five carrying the denoting
    rows of CH-282 to CH-285 and four carrying control
    and guarded rows, reported Canonical Ruled 5,
    Open 4 against a hand truth of Open 9 on the
    uncured tree."""

    def test_combined_file_stays_open(self):
        rows = (
            "Ruled | one two three four five six seven "
            "eight nine | 1 occurrence | entries: DQ-001",
            "Ruled: Ruled 1, combined overall net gross "
            "alpha total 1",
            "Ruled: Ruled 1, total 1 entries extra more "
            "again plus once",
            "Ruled: Ruled 1, combined overall net gross "
            "grand sums 1",
            "Ruled: Ruled 1, total 1` entries",
            "Ruled | one two three four five six seven "
            "eight | 1 occurrence | entries: DQ-001",
            "Ruled: Ruled 1, summation 1",
            "Ruled: Ruled 1, total 1 entries extra more "
            "again fifth",
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


class Step17Fix11BConfinementTest(unittest.TestCase):
    """CH-282 to CH-286 under the CH-15 segment
    awareness pin, in both directions: every widening
    stays confined to the row itself, so a genuine
    ruling standing in the widened forms company still
    counts."""

    def test_nine_token_kind_row_then_ruling_counts(self):
        model, state = _state(
            "\nSettled | one two three four five six seven "
            "eight nine | 1 occurrence | entries: DQ-001. "
            "Ruled by Captain JP: take Option A.\n")
        self.assertNotIn("Settled", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_five_prefix_row_then_ruling_counts(self):
        model, state = _state(
            "\nSettled: Settled 1, one two three four five "
            "total 1. Ruled by Captain JP: take Option A.\n")
        self.assertNotIn("Settled", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_six_token_tail_row_then_ruling_counts(self):
        model, state = _state(
            "\nSettled: Settled 1, total 1 entries extra "
            "more again plus once. Ruled by Captain JP: "
            "take Option A.\n")
        self.assertNotIn("Settled", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_summations_row_then_ruling_counts(self):
        model, state = _state(
            "\nSettled: Settled 1, summations 1. Ruled by "
            "Captain JP: take Option A.\n")
        self.assertNotIn("Settled", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_grand_sums_four_row_then_ruling_counts(self):
        model, state = _state(
            "\nSettled: Settled 1, combined overall net "
            "gross grand sums 1. Ruled by Captain JP: take "
            "Option A.\n")
        self.assertNotIn("Settled", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_matter_past_tally_row_still_denotes(self):
        model, state = _state(
            "\nRuled: Ruled 1, total 1 and the panel "
            "accepted the report.\n")
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")


class Step17Fix11BQuotedRulingStandingTest(unittest.TestCase):
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
