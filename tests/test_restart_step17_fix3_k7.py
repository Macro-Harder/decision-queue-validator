"""Restart Step 17 fix wave 3, Seat K7 tests.

Charges CH-40 (validate, decided entry presence tests on value
content: S17-ATK3-7-01) and CH-41 (validate, closing prose
derivation width, round 3 limbs: S17-ATK3-7-04). Constructions
are the finding papers own constructions, rebuilt inline from
the attack scratch files. The cure stands in
decision_queue_validator/validate.py only.

Copyright: J.P. Picard aka Macro-Harder
"""

import unittest

import dqv_harness as h


def _run(data, name):
    _model, output = h.run_pipeline(data.encode("utf-8"), name)
    if output is None:
        raise AssertionError("pipeline returned a failure for " + name)
    return output


def _rule5_statements(output, entry_id):
    return [h.finding_statement(f)
            for f in h.findings_for(output, entry_id=entry_id, rule=5)]


_BANKED_BODY = (
    "Status: Banked\n"
    "\n"
    "Question: Which option should we take?\n"
    "\n"
    "Options: Option A, Option B\n"
    "\n"
    "Cost of deciding late: Work stays blocked.\n"
    "\n"
    "Blocks: DQ-002\n"
    "\n"
)


def _decided_with_values(number, ruling_text, outcome, landing,
                         decider="Captain JP"):
    return (
        "# Decision queue\n"
        "\n"
        "### DQ-%03d: Evidence values\n"
        "\n"
        "Status: RULED, closed\n"
        "\n"
        "Ruled by: %s\n"
        "\n"
        "Ruling text: %s\n"
        "\n"
        "Ruling outcome: %s\n"
        "\n"
        "Where the ruling landed: %s\n"
        % (number, decider, ruling_text, outcome, landing)
    )


class Ch40PunctuationOnlyValuesTest(unittest.TestCase):
    """CH-40: a value of punctuation only, carrying no word
    character, stands as no value on the ruling text, outcome,
    and landing limbs read through _field_value_present, as a
    whitespace only value already does."""

    def test_a02_single_full_stop_values_take_all_four_findings(self):
        # S17-ATK3-7-01, construction a02: every evidence value
        # is one full stop. The decider finding already stood;
        # the other three limbs must join it.
        data = _decided_with_values(302, ".", ".", ".", decider=".")
        output = _run(data, "a02.md")
        joined = "\n".join(_rule5_statements(output, "DQ-302"))
        self.assertIn("No decider is recorded", joined)
        self.assertIn("No ruling text is recorded", joined)
        self.assertIn("No outcome is recorded", joined)
        self.assertIn("No landing record is recorded", joined)

    def test_punctuation_only_variants_take_the_three_findings(self):
        variants = (".", "...", "!", "?", "?!", ",;:", "()", "***")
        for index, value in enumerate(variants):
            with self.subTest(value=value):
                number = 310 + index
                data = _decided_with_values(
                    number, value, value, value)
                output = _run(data, "pv%03d.md" % number)
                joined = "\n".join(
                    _rule5_statements(output, "DQ-%03d" % number))
                self.assertIn("No ruling text is recorded", joined)
                self.assertIn("No outcome is recorded", joined)
                self.assertIn("No landing record is recorded", joined)
                self.assertNotIn("No decider is recorded", joined)

    def test_each_limb_alone_with_a_punctuation_only_value(self):
        # One limb at a time carries the punctuation only value
        # while the other two carry real matter.
        cases = (
            (320, ".", "The short form stands.",
             "NOTES.md section 2.", "No ruling text is recorded"),
            (321, "The note takes the short form.", ".",
             "NOTES.md section 2.", "No outcome is recorded"),
            (322, "The note takes the short form.",
             "The short form stands.", ".",
             "No landing record is recorded"),
        )
        for number, text, outcome, landing, expected in cases:
            with self.subTest(number=number):
                data = _decided_with_values(
                    number, text, outcome, landing)
                output = _run(data, "one%03d.md" % number)
                joined = "\n".join(
                    _rule5_statements(output, "DQ-%03d" % number))
                self.assertIn(expected, joined)
                self.assertEqual(
                    len(_rule5_statements(output, "DQ-%03d" % number)),
                    1)

    def test_word_character_values_still_count_as_present(self):
        # Guard: a value carrying a word character, a letter or
        # a digit, counts as present, before and after the cure.
        for index, value in enumerate(("A", "1", "x.")):
            with self.subTest(value=value):
                number = 330 + index
                data = _decided_with_values(
                    number, value, value, value)
                output = _run(data, "wv%03d.md" % number)
                self.assertEqual(
                    _rule5_statements(output, "DQ-%03d" % number), [])

    def test_full_evidence_values_take_no_presence_finding(self):
        # Guard, the CH-6 full evidence form.
        data = _decided_with_values(
            340, '"Settle DQ-340 as follows."',
            "DQ-340 is decided and closed.",
            "NOWHERE.md, sample rule.")
        output = _run(data, "full.md")
        self.assertEqual(_rule5_statements(output, "DQ-340"), [])

    def test_whitespace_only_values_still_take_all_four(self):
        # Control, construction a01: the whitespace forms stood
        # cured before this charge and stand cured after it.
        data = _decided_with_values(
            341, "  ", "  ", "  ", decider="  ")
        output = _run(data, "a01.md")
        joined = "\n".join(_rule5_statements(output, "DQ-341"))
        self.assertIn("No decider is recorded", joined)
        self.assertIn("No ruling text is recorded", joined)
        self.assertIn("No outcome is recorded", joined)
        self.assertIn("No landing record is recorded", joined)

    def test_decider_punctuation_only_beside_full_evidence(self):
        # Guard for ruling (i) and the D1 narrowed form,
        # construction a07: the decider limb stands untouched by
        # this charge, so a punctuation only decider value beside
        # full real evidence takes the decider finding alone,
        # exactly as it did before the cure.
        data = _decided_with_values(
            342, '"The note takes the short form."',
            "The short form stands.", "NOTES.md section 2.",
            decider=".")
        output = _run(data, "a07.md")
        statements = _rule5_statements(output, "DQ-342")
        self.assertEqual(len(statements), 1)
        self.assertIn("No decider is recorded", statements[0])


class Ch41ClosingProseNounFormsTest(unittest.TestCase):
    """CH-41: closing prose in the determining element position
    stating a decision by noun form, or closure by shut with a
    ruling noun, is read as the status bearing element it is."""

    def _prose_file(self, number, paragraph):
        return (
            "# Decision queue\n"
            "\n"
            "### DQ-%03d: Banked head, prose probe\n"
            "\n"
            % number
            + _BANKED_BODY
            + "This question is waiting for a decision.\n"
            "\n"
            + paragraph + "\n"
        )

    def _state(self, number, paragraph, name):
        output = _run(self._prose_file(number, paragraph), name)
        entry = h.entry_by_id(output, "DQ-%03d" % number)
        return h.entry_state(entry)

    def test_p02_decision_noun_form_is_ambiguous(self):
        # S17-ATK3-7-04, construction p02.
        state = self._state(
            372,
            "Captain JP made the decision and this entry is now "
            "closed. Nothing remains open on it.",
            "p02.md")
        self.assertEqual(state, "Ambiguous")

    def test_p03_shut_with_a_ruling_noun_is_ambiguous(self):
        # S17-ATK3-7-04, construction p03.
        state = self._state(
            373,
            "This entry was shut by Captain JP after a ruling. "
            "Nothing remains open on it.",
            "p03.md")
        self.assertEqual(state, "Ambiguous")

    def test_decision_noun_variants_are_ambiguous(self):
        cases = (
            (374, "Captain JP made a decision and this entry is "
                  "now closed. Nothing remains open on it."),
            (375, "The decision was made by Captain JP and this "
                  "entry stands closed. Nothing remains open on it."),
        )
        for number, paragraph in cases:
            with self.subTest(number=number):
                self.assertEqual(
                    self._state(number, paragraph,
                                "dn%03d.md" % number),
                    "Ambiguous")

    def test_shut_with_a_ruling_noun_variants_are_ambiguous(self):
        cases = (
            (376, "This entry was shut by Captain JP under a "
                  "ruling. Nothing remains open on it."),
            (377, "This entry is shut after a ruling by Captain "
                  "JP. Nothing remains open on it."),
        )
        for number, paragraph in cases:
            with self.subTest(number=number):
                self.assertEqual(
                    self._state(number, paragraph,
                                "sh%03d.md" % number),
                    "Ambiguous")

    def test_ch8_cured_verb_forms_still_ambiguous(self):
        # Guard: the CH-8 pins whole, in two of their forms.
        cases = (
            (378, "This entry was decided by Captain JP yesterday "
                  "and is now closed. Nothing remains open on it."),
            (379, "This entry has been ruled by Captain JP and "
                  "has now been closed. Nothing remains open on it."),
        )
        for number, paragraph in cases:
            with self.subTest(number=number):
                self.assertEqual(
                    self._state(number, paragraph,
                                "ch8%03d.md" % number),
                    "Ambiguous")

    def test_decision_noun_without_closure_stays_open(self):
        # Bound guard: a decision noun with no closure word
        # stated stands outside the charge bound.
        state = self._state(
            380,
            "This entry awaits a decision from Captain JP. "
            "Nothing remains decided on it.",
            "guard1.md")
        self.assertEqual(state, "Open")

    def test_shut_without_a_ruling_noun_stays_open(self):
        # Bound guard: closure by shut with no ruling noun
        # stated stands outside the charge bound.
        state = self._state(
            381,
            "This entry was shut by Captain JP for the winter "
            "break. Nothing remains open on it.",
            "guard2.md")
        self.assertEqual(state, "Open")

    def test_no_longer_open_form_stays_open(self):
        # Bound guard, attack paper observation O-5: this
        # paragraph is not named as the determining element, and
        # the charge does not reach it.
        state = self._state(
            382,
            "This entry is no longer open following a ruling by "
            "Captain JP.",
            "p07.md")
        self.assertEqual(state, "Open")


class Ch41Pin11ConcordanceGuardTest(unittest.TestCase):
    """The PIN-11 concordance pins and the A2-10-F1 pronoun
    form, which CH-41 must not break."""

    _TAIL = (
        "# Decision queue\n"
        "\n"
        "## DQ-001: the harbour light rota. "
        "RULED by Captain JP 2026-11-15\n"
        "\n"
        "The harbour light rota was drawn up by the Clerk from "
        "the winter watch list, and the rota names the keeper "
        "for each night of the week in a single table at the "
        "end of the note. %s\n"
    )

    def test_it_is_closed_confirms_the_ruled_heading(self):
        output = _run(self._TAIL % "It is closed.", "f1g.md")
        entry = h.entry_by_id(output, "DQ-001")
        self.assertEqual(h.entry_state(entry), "Ruled")

    def test_bare_closed_still_confirms_the_ruled_heading(self):
        output = _run(self._TAIL % "Closed.", "f1guard.md")
        entry = h.entry_by_id(output, "DQ-001")
        self.assertEqual(h.entry_state(entry), "Ruled")


if __name__ == "__main__":
    unittest.main()
