"""Step 17 fix wave 8, Fix Seat K4 tests.

Charges CH-159, CH-160, and CH-161, the validate
disposition guard programme, ruled TO FIX at section 77
of design/steps/step-17r-record.md, standing on the
programme ground of section 52 and ruling (g) of section
77: the guard width is restated once at the next bound
step on each limb the charges name, in the standing
pattern of fix waves 4 to 7. Findings: seat 10 A8-10-F3
(kind and total members) and A8-10-F4 at
design/steps/step-17r-attack8-10.md, and seat 20
F-20-8-1, F-20-8-2, F-20-8-3, and F-20-8-4 at
design/steps/step-17r-attack8-20.md, consolidated as
T8-01, T8-02, and T8-03 in the round 8 triage
preparation. T8-03 stands graded Medium whole under
ruling (a) of section 77.

Each surface width, stated in its own terms. Crosswalk
tail (CH-159): the trailing row matter after the final
count stands as at CH-121 (one word token at a
whitespace joint, or the row noun at the stated joint
run), with the joint run of the noun form taking a
semicolon, a colon, or a slash beside the whitespace,
zero width, comma, period, and hyphen joints; with a
second word token standing after the first at a comma
joint where that token closes the line; with a first
word token that is no row noun standing at a comma
joint where that token closes the line; and with one
further, third, word token standing after the second at
a whitespace joint. Appendix kind (CH-160): the kind
slot stands as one to six word tokens joined by
whitespace between its pipes. Total word (CH-161): the
total word stands as at CH-124, with up to two word
tokens other than the word in standing before it at a
non word joint where they stand (the grand form
included), as the word sum with a prefix word standing
before it on the same terms, or as the word aggregate
or aggregates, each with a prefix word standing before
it on the same terms.

Both directions are pinned in this file. Recognition:
the charged rows denote nothing, and the host entry
stays Open. Confinement: the CH-15 segment awareness
pin and the O-4-20-1 standing stand pinned in both
directions, a genuine ruling standing in the widened
forms company still counts, in the confinement forms
the earlier waves charged and in the comma joint forms
this cure bounds at the line closing edge, matter
standing past a tally row still denotes through its
label, and quoted genuine ruling lines still denote.
The fix wave 7 K3 pins on these limbs stand whole,
restated in the standing pin class below. The wider
readings recorded at seat 10 observations O3, O4, and
O5 and seat 20 observations O-8-20-3 and O-8-20-4 stand
as measured reach under ruling (j) of section 77 and
are not charged here.

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


def _state(extra_body, name="k4_case.md"):
    model, output = h.run_pipeline(_entry(extra_body), name)
    result = h.entry_by_id(output, "DQ-001")
    return model, h.entry_state(result)


class Step17Fix8K4CrosswalkTailTest(unittest.TestCase):
    """CH-159, T8-01 (A8-10-F4 and F-20-8-1): the crosswalk
    tail admits two word tokens of trailing row matter
    under CH-121, the first standing as at CH-107 or as
    the row noun at a joint run of whitespace, the zero
    width characters, a comma, a period, or a hyphen, and
    the second at a whitespace joint, so a third trailing
    token, the row noun at a semicolon, colon, or slash
    joint, the second token at a comma joint, and a non
    noun token at a comma joint still denote on the fix
    wave 7 cured tree (attack8-20 cases t01 to t04, t08,
    and t13, and attack8-10 cases g8-tail-three-tokens
    and g8-tail-noun-semicolon)."""

    def test_third_trailing_token_denotes_nothing(self):
        rows = (
            "Ruled: Ruled 1, total 1 entries extra more",
            "Ruled: Ruled 1, total 1 items counted extra",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")

    def test_noun_at_fresh_joints_denotes_nothing(self):
        rows = (
            "Ruled: Ruled 1, total 1; entries",
            "Ruled: Ruled 1, total 1: entries",
            "Ruled: Ruled 1, total 1/entries",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")

    def test_second_token_at_comma_joint_denotes_nothing(self):
        model, state = _state(
            "\nRuled: Ruled 1, total 1 entries, extra\n")
        self.assertNotIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Open")

    def test_first_token_at_comma_joint_denotes_nothing(self):
        model, state = _state(
            "\nRuled: Ruled 1, total 1, extra\n")
        self.assertNotIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Open")

    def test_tail_controls_stay_guarded(self):
        # The attack8-20 group T controls, guarded on the
        # fix wave 7 cured tree and standing as measured
        # reach under ruling (j) of section 77: joint runs
        # of two marks at the noun joint, the second token
        # at a zero width joint, the noun at a tab joint,
        # the capitalised noun at a comma joint, the noun
        # at an em space and comma joint run, and the
        # second token standing after a period joint, where
        # the span ends at the sentence joint and the word
        # after it stands as new sentence matter.
        rows = (
            "Ruled: Ruled 1, total 1,, entries",
            "Ruled: Ruled 1, total 1,- entries",
            "Ruled: Ruled 1, total 1.. entries",
            "Ruled: Ruled 1, total 1 entries\u200bextra",
            "Ruled: Ruled 1, total 1\tentries",
            "Ruled: Ruled 1, total 1, questions",
            "Ruled: Ruled 1, total 1, Entries",
            "Ruled: Ruled 1, total 1\u2003, entries",
            "Ruled: Ruled 1, total 1 entries. extra",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")


class Step17Fix8K4AppendixKindTest(unittest.TestCase):
    """CH-160, T8-02 (the kind member of A8-10-F3 and
    F-20-8-2): the appendix kind slot reads at most five
    word tokens under CH-123, so a kind spelled in six
    tokens still denotes on the fix wave 7 cured tree
    (attack8-20 case k01 and attack8-10 case
    g8-kind-six)."""

    def test_six_token_kinds_denote_nothing(self):
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

    def test_kind_controls_stay_guarded(self):
        # The attack8-20 group K controls: the five token
        # kind at the cured bound itself, the four token
        # kind at tab joints, and the kind with a zero
        # width space standing inside its first token, the
        # last two standing as measured reach under ruling
        # (j) of section 77.
        rows = (
            "Ruled | at the line start position | 1 "
            "occurrence | entries: DQ-001",
            "Ruled | at\tthe\tline\tstart | 1 occurrence "
            "| entries: DQ-001",
            "Ruled | line\u200bstart | 1 occurrence | "
            "entries: DQ-001",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")


class Step17Fix8K4TotalWordTest(unittest.TestCase):
    """CH-161, T8-03 (the total members of A8-10-F3, and
    F-20-8-3 with F-20-8-4): the total word prefix reading
    admits one word standing before the total word only
    under CH-124, and the word aggregate stands admitted
    as a total word in the singular only, so two prefix
    words, a prefix word standing before the word
    aggregate or the word sum, and the plural of the word
    aggregate still denote on the fix wave 7 cured tree
    (attack8-20 cases w01, w02, w03, w07, w10, and w13,
    and attack8-10 cases g8-two-word-prefix,
    g8-aggregate-prefix, and g8-aggregate-plural)."""

    def test_two_word_prefix_denotes_nothing(self):
        rows = (
            "Ruled: Ruled 1, combined net total 1",
            "Ruled: Ruled 1, very grand total 1",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")

    def test_prefixed_aggregate_and_sum_denote_nothing(self):
        rows = (
            "Ruled: Ruled 1, grand aggregate 1",
            "Ruled: Ruled 1, net aggregate 1",
            "Ruled: Ruled 1, combined aggregate 1",
            "Ruled: Ruled 1, net sum 1",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")

    def test_aggregate_plural_denotes_nothing(self):
        rows = (
            "Ruled: Ruled 1, aggregates 1",
            "Ruled: Ruled 1 in aggregates",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")

    def test_total_controls_stay_guarded(self):
        # The attack8-20 group W controls, guarded on the
        # fix wave 7 cured tree: the in aggregate form,
        # the aggregate form alone, the hyphen compound
        # prefix form, the subtotal sum form, the grand
        # totals plural, and the capitalised grand sum
        # form.
        rows = (
            "Ruled: Ruled 1 in aggregate",
            "Ruled: Ruled 1, aggregate 1",
            "Ruled: Ruled 1, net-total 1",
            "Ruled: Ruled 1, subtotal sum 1",
            "Ruled: Ruled 1, grand totals 1",
            "Ruled: Ruled 1, Grand Sum 1",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")



class Step17Fix8K4ConfinementTest(unittest.TestCase):
    """CH-159 to CH-161 under the CH-15 segment awareness
    pin, in both directions: every widening stays confined
    to the row itself, so a genuine ruling standing in the
    widened forms company still counts, in the confinement
    forms the earlier waves charged (attack8-20 cases f01
    to f03, k05, and w11, in the Settled label form the fix
    wave 7 K3 file charges), at the sentence joint edge,
    and at the comma joint edges this cure bounds at the
    line closing form, and matter standing past a tally
    row still denotes through its label."""

    def test_third_token_row_then_ruling_counts(self):
        model, state = _state(
            "\nSettled: Settled 1, total 1 entries extra "
            "more. Ruled by Captain JP: take Option A.\n")
        self.assertNotIn("Settled", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_two_prefix_row_then_ruling_counts(self):
        model, state = _state(
            "\nSettled: Settled 1, combined net total 1. "
            "Ruled by Captain JP: take Option A.\n")
        self.assertNotIn("Settled", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_six_token_kind_row_then_ruling_counts(self):
        model, state = _state(
            "\nSettled | at the line start position now | "
            "1 occurrence | entries: DQ-001. Ruled by "
            "Captain JP: take Option A.\n")
        self.assertNotIn("Settled", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_prefixed_aggregate_row_then_ruling_counts(self):
        model, state = _state(
            "\nSettled: Settled 1, grand aggregate 1. "
            "Ruled by Captain JP: take Option A.\n")
        self.assertNotIn("Settled", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_period_joint_edge_still_takes_no_ruling(self):
        # The standing confinement edge of the tail limb:
        # a sentence joint standing after the final count
        # takes no trailing token where the word after the
        # joint is no row noun, so the ruling standing
        # after the row counts in full.
        model, state = _state(
            "\nSettled: Settled 1, total 1. Ruled by "
            "Captain JP: take Option A.\n")
        self.assertNotIn("Settled", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_first_token_comma_joint_takes_no_ruling(self):
        # The line closing bound of the comma joint first
        # token form at CH-159: a word standing at a comma
        # joint after the final count is row matter only
        # where it closes the line, so a ruling standing
        # in that place counts in full.
        model, state = _state(
            "\nRuled: Ruled 1, total 1, Ruled by Captain "
            "JP: take Option A.\n")
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_second_token_comma_joint_takes_no_ruling(self):
        # The same bound at the second token: a word
        # standing at a comma joint after the first
        # trailing token is row matter only where it
        # closes the line, so a ruling standing in that
        # place counts and the row word does not.
        model, state = _state(
            "\nSettled: Settled 1, total 1 entries, Ruled "
            "by Captain JP: take Option A.\n")
        self.assertNotIn("Settled", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_matter_past_tally_row_still_denotes(self):
        # The standing CH-51 labelled branch pin, restated:
        # matter standing past a tally row on its line
        # takes its labelled element as before. Three
        # trailing tokens now stand inside the span, and
        # the matter past them still denotes.
        model, state = _state(
            "\nRuled: Ruled 1, total 1 and the panel "
            "accepted the report.\n")
        self.assertIn("Ruled", _dispositions(model))
        self.assertEqual(state, "Ruled")


class Step17Fix8K4QuotedRulingStandingTest(unittest.TestCase):
    """Observation O-4-20-1 standing, unmoved by this
    cure: quoted genuine ruling lines still denote for
    their host entry, on every surface the rounds
    measured, restated whole from the fix wave 7 K3
    file."""

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


class Step17Fix8K4StandingPinTest(unittest.TestCase):
    """The fix wave 7 K3 pins on these limbs, standing as
    recorded before this cure and after it: the CH-121
    noun and second token forms, the CH-123 four and five
    token kinds, and the CH-124 prefixed, aggregate, and
    grand sum forms."""

    def test_wave7_tail_forms_stay_guarded(self):
        rows = (
            "Ruled: Ruled 1, total 1. entries",
            "Ruled: Ruled 1, total 1, entries",
            "Ruled: Ruled 1, total 1-entries",
            "Ruled: Ruled 1, total 1 entries extra",
            "Ruled: Ruled 1, total 1 items counted",
            "Ruled: Ruled 1, total 1 entries",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")

    def test_wave7_kind_forms_stay_guarded(self):
        rows = (
            "Ruled | at the line start | 1 occurrence | "
            "entries: DQ-001",
            "Ruled | very long kind name here | 1 "
            "occurrence | entries: DQ-001",
            "Ruled | at line start | 1 occurrence | "
            "entries: DQ-001",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")

    def test_wave7_total_forms_stay_guarded(self):
        rows = (
            "Ruled: Ruled 1, grand sum 1",
            "Ruled: Ruled 1, combined total 1",
            "Ruled: Ruled 1, net total 1",
            "Ruled: Ruled 1 in aggregate",
            "Ruled: Ruled 1, aggregate 1",
            "Ruled: Ruled 1, grand total 1",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _state("\n" + row + "\n")
                self.assertNotIn("Ruled", _dispositions(model))
                self.assertEqual(state, "Open")

    def test_wave7_confinement_forms_stay_counting(self):
        cases = (
            "\nSettled: Settled 1, total 1 entries extra. "
            "Ruled by Captain JP: take Option A.\n",
            "\nSettled | at the line start | 1 occurrence "
            "| entries: DQ-001. Ruled by Captain JP: take "
            "Option A.\n",
            "\nSettled: Settled 1, grand sum 1. Ruled by "
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
