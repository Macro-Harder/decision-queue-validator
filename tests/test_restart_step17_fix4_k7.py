"""Restart Step 17 fix wave 4, Seat K7 tests.

Charges CH-61 (validate, decided entry presence tests on matter
content, round 4 limbs: S17-ATK4-7-01 and S17-ATK4-7-09) and
CH-62 (validate, closing prose derivation width, round 4 limbs:
S17-ATK4-7-04). Constructions are the finding papers own
constructions, rebuilt inline from the attack scratch files.
The cure stands in decision_queue_validator/validate.py only.

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


def _decided(number, title, tail):
    return (
        "# Decision queue\n"
        "\n"
        "### DQ-%03d: %s\n"
        "\n"
        "Status: RULED, closed\n"
        "\n"
        "Ruled by: Captain JP\n"
        "\n"
        % (number, title)
        + tail
    )


class Ch61LandingFallbackMatterTest(unittest.TestCase):
    """CH-61, limb S17-ATK4-7-01: the two landing fallback limbs
    outside the _field_value_present reading (a body line
    carrying the words Where it landed, and a bullet line
    standing under an empty landing label) test the matter
    standing after the label words and inside the bullet, as
    the cured labelled limb does."""

    def test_f01_where_it_landed_punctuation_takes_landing(self):
        # S17-ATK4-7-01, construction f01, verbatim.
        data = _decided(
            402, "Landing where it landed punct",
            "Ruling text: \"Settle DQ-402 as follows.\"\n"
            "\n"
            "Ruling outcome: DQ-402 is decided and closed.\n"
            "\n"
            "Where it landed: .\n")
        output = _run(data, "f01.md")
        statements = _rule5_statements(output, "DQ-402")
        self.assertEqual(len(statements), 1)
        self.assertIn("No landing record is recorded", statements[0])

    def test_f02_bullet_punctuation_takes_landing(self):
        # S17-ATK4-7-01, construction f02, verbatim.
        data = _decided(
            403, "Landing bullet punct",
            "Ruling text: \"Settle DQ-403 as follows.\"\n"
            "\n"
            "Ruling outcome: DQ-403 is decided and closed.\n"
            "\n"
            "Where the ruling landed:\n"
            "\n"
            "- .\n")
        output = _run(data, "f02.md")
        statements = _rule5_statements(output, "DQ-403")
        self.assertEqual(len(statements), 1)
        self.assertIn("No landing record is recorded", statements[0])

    def test_where_it_landed_punctuation_variants_take_landing(self):
        for index, value in enumerate(("...", "!", "?!", "***")):
            with self.subTest(value=value):
                number = 410 + index
                data = _decided(
                    number, "Landing label variant",
                    "Ruling text: \"Settle DQ-%03d as follows.\"\n"
                    "\n"
                    "Ruling outcome: DQ-%03d is decided and "
                    "closed.\n"
                    "\n"
                    "Where it landed: %s\n"
                    % (number, number, value))
                output = _run(data, "lv%03d.md" % number)
                statements = _rule5_statements(
                    output, "DQ-%03d" % number)
                self.assertEqual(len(statements), 1)
                self.assertIn("No landing record is recorded",
                              statements[0])

    def test_bullet_punctuation_variants_take_landing(self):
        for index, value in enumerate(("...", "?", "()")):
            with self.subTest(value=value):
                number = 420 + index
                data = _decided(
                    number, "Landing bullet variant",
                    "Ruling text: \"Settle DQ-%03d as follows.\"\n"
                    "\n"
                    "Ruling outcome: DQ-%03d is decided and "
                    "closed.\n"
                    "\n"
                    "Where the ruling landed:\n"
                    "\n"
                    "- %s\n" % (number, number, value))
                output = _run(data, "bv%03d.md" % number)
                statements = _rule5_statements(
                    output, "DQ-%03d" % number)
                self.assertEqual(len(statements), 1)
                self.assertIn("No landing record is recorded",
                              statements[0])

    def test_f06_where_it_landed_real_matter_stays_clean(self):
        # Guard, construction f06, verbatim: genuine matter
        # after the label words counts, before and after.
        data = _decided(
            407, "Landing where it landed real",
            "Ruling text: \"Settle DQ-407 as follows.\"\n"
            "\n"
            "Ruling outcome: DQ-407 is decided and closed.\n"
            "\n"
            "Where it landed: records.md, sample rule.\n")
        output = _run(data, "f06.md")
        self.assertEqual(_rule5_statements(output, "DQ-407"), [])

    def test_f03_bullet_real_matter_stays_clean(self):
        # Guard, construction f03, verbatim: a bullet carrying
        # genuine matter counts, before and after.
        data = _decided(
            404, "Landing bullet real",
            "Ruling text: \"Settle DQ-404 as follows.\"\n"
            "\n"
            "Ruling outcome: DQ-404 is decided and closed.\n"
            "\n"
            "Where the ruling landed:\n"
            "\n"
            "- records.md, sample rule.\n")
        output = _run(data, "f03.md")
        self.assertEqual(_rule5_statements(output, "DQ-404"), [])

    def test_bullet_word_character_matter_counts(self):
        # Guard: a bullet whose content carries a word
        # character counts as present, as the cured labelled
        # limb counts a value carrying a word character.
        data = _decided(
            430, "Landing bullet word character",
            "Ruling text: \"Settle DQ-430 as follows.\"\n"
            "\n"
            "Ruling outcome: DQ-430 is decided and closed.\n"
            "\n"
            "Where the ruling landed:\n"
            "\n"
            "- x.\n")
        output = _run(data, "bw430.md")
        self.assertEqual(_rule5_statements(output, "DQ-430"), [])

    def test_where_it_landed_word_character_matter_counts(self):
        # Guard: matter after the label words carrying a word
        # character counts as present.
        data = _decided(
            431, "Landing label word character",
            "Ruling text: \"Settle DQ-431 as follows.\"\n"
            "\n"
            "Ruling outcome: DQ-431 is decided and closed.\n"
            "\n"
            "Where it landed: x.\n")
        output = _run(data, "lw431.md")
        self.assertEqual(_rule5_statements(output, "DQ-431"), [])


class Ch61OutcomeBlockMatterTest(unittest.TestCase):
    """CH-61, limb S17-ATK4-7-09: the outcome limb that counts
    a decision block statement opening with a Ruled, Settled,
    or Closed form tests the matter standing after its opening
    disposition word, as its ruling text twin does."""

    def _block_file(self, number, title, block_body, extra=""):
        return _decided(
            number, title,
            "Ruling text: \"Settle DQ-%03d as follows.\"\n"
            "\n"
            "%s"
            "Where the ruling landed: NOWHERE.md, sample rule.\n"
            "\n"
            "#### Ruling by Captain JP\n"
            "\n"
            "%s\n" % (number, extra, block_body))

    def test_f05_ruled_dot_block_takes_outcome(self):
        # S17-ATK4-7-09, construction f05, verbatim.
        data = self._block_file(406, "Outcome ruled dot block",
                                "Ruled.")
        output = _run(data, "f05.md")
        statements = _rule5_statements(output, "DQ-406")
        self.assertEqual(len(statements), 1)
        self.assertIn("No outcome is recorded", statements[0])

    def test_settled_dot_block_takes_outcome(self):
        data = self._block_file(416, "Outcome settled dot block",
                                "Settled.")
        output = _run(data, "sb416.md")
        statements = _rule5_statements(output, "DQ-416")
        self.assertEqual(len(statements), 1)
        self.assertIn("No outcome is recorded", statements[0])

    def test_closed_dot_block_takes_outcome(self):
        data = self._block_file(417, "Outcome closed dot block",
                                "Closed.")
        output = _run(data, "cb417.md")
        statements = _rule5_statements(output, "DQ-417")
        self.assertEqual(len(statements), 1)
        self.assertIn("No outcome is recorded", statements[0])

    def test_f04_block_punctuation_twin_takes_ruling_text(self):
        # Control, construction f04, verbatim: the ruling text
        # twin already tests matter on its block forms, so a
        # block body of one full stop beside a real outcome
        # line takes the ruling text Error alone, before and
        # after this cure.
        data = _decided(
            405, "Block matter punct",
            "Ruling outcome: DQ-405 is decided and closed.\n"
            "\n"
            "Where the ruling landed: NOWHERE.md, sample rule.\n"
            "\n"
            "#### Ruling by Captain JP\n"
            "\n"
            ".\n")
        output = _run(data, "f04.md")
        statements = _rule5_statements(output, "DQ-405")
        self.assertEqual(len(statements), 1)
        self.assertIn("No ruling text is recorded", statements[0])

    def test_ruled_dot_block_with_matter_counts(self):
        # Guard: a block statement opening with the Ruled form
        # and carrying matter after it counts as an outcome,
        # before and after.
        data = self._block_file(
            418, "Outcome ruled dot matter",
            "Ruled. The second option stands.")
        output = _run(data, "rm418.md")
        self.assertEqual(_rule5_statements(output, "DQ-418"), [])

    def test_ruled_colon_block_with_matter_counts(self):
        # Guard: the colon form with matter after the label
        # counts as an outcome, before and after.
        data = self._block_file(
            419, "Outcome ruled colon matter",
            "Ruled: the second option stands.")
        output = _run(data, "rc419.md")
        self.assertEqual(_rule5_statements(output, "DQ-419"), [])


class Ch62ClosingProseCrossingsTest(unittest.TestCase):
    """CH-62: closing prose in the determining element position
    pairs the noun and closure forms across the charged
    crossings: the decision noun beside shut, the ruling noun
    beside closed, the verdict noun beside closed, and the
    decided verb beside sealed."""

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

    def test_p01_decided_verb_beside_sealed_is_ambiguous(self):
        # S17-ATK4-7-04, construction p01, verbatim.
        state = self._state(
            462,
            "This entry was ruled by Captain JP yesterday and "
            "is now sealed. Nothing remains open on it.",
            "p01.md")
        self.assertEqual(state, "Ambiguous")

    def test_p02_decision_noun_beside_shut_is_ambiguous(self):
        # S17-ATK4-7-04, construction p02, verbatim.
        state = self._state(
            463,
            "Captain JP made the decision and this entry is "
            "now shut. Nothing remains open on it.",
            "p02.md")
        self.assertEqual(state, "Ambiguous")

    def test_p03_ruling_noun_beside_closed_is_ambiguous(self):
        # S17-ATK4-7-04, construction p03, verbatim.
        state = self._state(
            464,
            "A ruling was issued on this entry and it is now "
            "closed. Nothing remains open on it.",
            "p03.md")
        self.assertEqual(state, "Ambiguous")

    def test_p04_verdict_noun_beside_closed_is_ambiguous(self):
        # S17-ATK4-7-04, construction p04, verbatim.
        state = self._state(
            465,
            "The verdict is final and this entry is now "
            "closed. Nothing remains open on it.",
            "p04.md")
        self.assertEqual(state, "Ambiguous")

    def test_crossing_variants_are_ambiguous(self):
        cases = (
            (470, "This entry was settled by Captain JP and "
                  "stands sealed. Nothing remains open on it."),
            (471, "Captain JP recorded the decision; the entry "
                  "is shut. Nothing remains open on it."),
            (472, "The ruling stands recorded and the entry "
                  "stands closed. Nothing remains open on it."),
            (473, "Her verdict was given and this entry is "
                  "now closed. Nothing remains open on it."),
        )
        for number, paragraph in cases:
            with self.subTest(number=number):
                self.assertEqual(
                    self._state(number, paragraph,
                                "cv%03d.md" % number),
                    "Ambiguous")

    def test_p05_ch41_decision_noun_beside_closed_still(self):
        # Guard, construction p05, verbatim: the CH-41 cured
        # paired form stands Ambiguous, before and after.
        state = self._state(
            466,
            "Captain JP made the decision and this entry is "
            "now closed. Nothing remains open on it.",
            "p05.md")
        self.assertEqual(state, "Ambiguous")

    def test_ch41_shut_beside_ruling_noun_still_ambiguous(self):
        # Guard: the CH-41 shut limb stands, before and after.
        state = self._state(
            474,
            "This entry was shut by Captain JP after a ruling. "
            "Nothing remains open on it.",
            "sr474.md")
        self.assertEqual(state, "Ambiguous")

    def test_sealed_without_a_decided_verb_stays_open(self):
        # Guard: sealed standing alone, with no decided verb
        # and no charged noun beside it, stands outside the
        # reading and still derives Open.
        state = self._state(
            475,
            "This entry is now sealed. Nothing remains open "
            "on it.",
            "sa475.md")
        self.assertEqual(state, "Open")

    def test_shut_without_a_noun_stays_open(self):
        # Guard: shut with no ruling, decision, or verdict
        # noun stated stands outside the reading, as the
        # CH-41 bound guard pins for the ruling noun form.
        state = self._state(
            476,
            "This entry is now shut. Nothing remains open "
            "on it.",
            "sh476.md")
        self.assertEqual(state, "Open")

    def test_verdict_noun_without_closure_stays_open(self):
        # Guard: a verdict noun with no closure stated stands
        # outside the reading.
        state = self._state(
            477,
            "The verdict is final. Nothing remains open "
            "on it.",
            "vn477.md")
        self.assertEqual(state, "Open")

    def test_ruling_noun_without_closure_stays_open(self):
        # Guard: a ruling noun with no closure stated stands
        # outside the reading.
        state = self._state(
            478,
            "A ruling was issued on this entry. Nothing "
            "remains open on it.",
            "rn478.md")
        self.assertEqual(state, "Open")

    def test_decision_noun_beside_sealed_stays_open(self):
        # Bound guard: the decision noun beside sealed is not
        # a charged crossing (the charge pairs sealed with the
        # decided verb only), so it stands outside the reading.
        state = self._state(
            479,
            "Captain JP made the decision and this entry is "
            "now sealed. Nothing remains open on it.",
            "ds479.md")
        self.assertEqual(state, "Open")

    def test_verdict_noun_beside_shut_stays_open(self):
        # Bound guard: the verdict noun beside shut is not a
        # charged crossing (the charge pairs the verdict noun
        # with closed only), so it stands outside the reading.
        state = self._state(
            480,
            "The verdict is final and this entry is now shut. "
            "Nothing remains open on it.",
            "vs480.md")
        self.assertEqual(state, "Open")


if __name__ == "__main__":
    unittest.main()
