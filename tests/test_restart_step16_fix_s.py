"""Restart Step 16 fix wave 6, Fix seat S tests.

Seat S owns finding A6-8-1 (Low) of Auditor 8, confirmation
round 6 (design/steps/step-16r-audit6-8.md, section 1 item 4
and its findings list): in Fix Seat O's labelled paragraph
block, attribution fragmented inside the word earns the
ruling text pass, in the six evidenced forms "Ruled:
Captain J.P.", "Settled: Captain J.P.", "Ruled: Cap-tain
JP", "Ruled: the Man-ager decided.", "Ruled: the Man.ager
decided.", and "Ruled: J.P. Morgan", because the token
reduction splits on punctuation and the fragments of the
attribution names count as content tokens outside the
attribution set (_ATTRIBUTION_TOKENS, beside the decider
line pattern; the condition stands in the block Fix Seat M
built and Fix Seat O conditioned).

The triage ground, at step record section 21: the form
stands DEFECTIVE under PIN-08 as section 18 ruled for the
neighbouring corner: a label carrying only an attribution,
whole or fragmented by punctuation inside the word, records
no ruling text; a name broken by punctuation is the same
attribution in a punctuated spelling.

Each test below pins the specified behaviour, written
before the cure. The six fragmented form tests fail before
the cure and pass after it. The guard tests pass before and
after: the genuine labelled paragraph forms keep passing,
including genuine matter standing beside a fragmented name;
the bound Auditor 1 of round 6 recorded inside Seat O's
stated bound stands unmoved (an unrecorded name alone, a
number alone, and a gibberish token each still pass, as do
the attribution adjunct form and the smuggled content token
form Auditor 8 ruled no finding); fixture F-12 keeps
exactly its one ruling text Error; the eight compact form
entries of the corpus pin keep taking no ruling text Error;
the pin totals stand; and the level 4 block and closing
prose forms keep passing.

Copyright: J.P. Picard aka Macro-Harder
"""

import unittest

import dqv_harness as h


def _decided_entry(entry_id, ruling_paragraph,
                   decider_sentence=None, closing="Status: closed."):
    if decider_sentence is None:
        decider_sentence = (
            "Ruled by Captain JP in the roles chat on 2026-11-14.")
    text = (
        "# Decision queue\n"
        "\n"
        "### %s: the checker note form\n"
        "\n"
        "Status: Banked\n"
        "\n"
        "%s\n"
        "\n"
        "%s\n"
        "\n"
        "Landed: the checker note in NOTES.md section 2 now "
        "states the agreed form.\n"
        "\n"
        "%s\n"
    ) % (entry_id, decider_sentence, ruling_paragraph, closing)
    return text.encode("utf-8")


SETTLED_DECIDER = (
    "Settled by the Manager under the grant, recorded in the "
    "roles chat on 2026-11-14.")

GENUINE_RULED = _decided_entry(
    "DQ-980", "Ruled: the checker note takes the short form.")

GENUINE_SETTLED = _decided_entry(
    "DQ-981", "Settled: the checker note takes the short form.",
    decider_sentence=SETTLED_DECIDER)

BLOCK_FORM = (
    "# Decision queue\n"
    "\n"
    "### DQ-982: the harbour consequence\n"
    "\n"
    "Status: Banked\n"
    "\n"
    "#### Ruling by Captain JP\n"
    "\n"
    "Ruled by: Captain JP\n"
    "\n"
    "Ruling text: \"Count it as a fail.\"\n"
    "\n"
    "Ruling outcome: The outcome stands as recorded.\n"
    "\n"
    "Where the ruling landed: NOTES.md section 2.\n"
    "\n"
    "Status: RULED, closed. This item is ruled.\n"
).encode("utf-8")


CLOSING_PROSE_FORM = (
    "## DQ-983: the harbour store note. RULED by Captain JP "
    "2026-11-15\n"
    "\n"
    "Origin: the harbour store question in the Clerk note of "
    "2026-11-14. Captain JP ruled in her own words: \"Keep the "
    "store by the harbour gate.\" Ruled: the harbour store "
    "stands by the harbour gate, and the night keeper holds "
    "its key. Landed: the harbour store paragraph in the Clerk "
    "note now states the gate form. Status: closed.\n"
).encode("utf-8")


FRAGMENTED_FORMS = (
    ("DQ-984", "Ruled: Captain J.P.", None),
    ("DQ-985", "Settled: Captain J.P.", SETTLED_DECIDER),
    ("DQ-986", "Ruled: Cap-tain JP", None),
    ("DQ-987", "Ruled: the Man-ager decided.", None),
    ("DQ-988", "Ruled: the Man.ager decided.", None),
    ("DQ-989", "Ruled: J.P. Morgan", None),
)


def _ruling_text_errors(output, entry_id):
    found = []
    for finding in h.findings_for(output, entry_id=entry_id, rule=5):
        statement = h.finding_statement(finding) or ""
        if "No ruling text" in statement:
            found.append(finding)
    return found


def _rule5_findings(output, entry_id):
    return h.findings_for(output, entry_id=entry_id, rule=5)


class FragmentedAttributionTest(unittest.TestCase):
    """A6-8-1: a "Ruled:" or "Settled:" labelled paragraph
    whose only matter under the label is the decider
    attribution with its own name fragmented by punctuation
    inside the word records no ruling text, and the decided
    entry takes the rule 5 ruling text Error."""

    def _assert_fragmented_form_errors(self, entry_id, paragraph,
                                       decider_sentence):
        data = _decided_entry(
            entry_id, paragraph, decider_sentence=decider_sentence)
        _model, output = h.run_pipeline(data, name="probe.md")
        found = _ruling_text_errors(output, entry_id)
        self.assertEqual(len(found), 1, entry_id)
        self.assertEqual(h.finding_severity(found[0]), "Error")

    def test_ruled_captain_initials_takes_the_error(self):
        self._assert_fragmented_form_errors(*FRAGMENTED_FORMS[0])

    def test_settled_captain_initials_takes_the_error(self):
        self._assert_fragmented_form_errors(*FRAGMENTED_FORMS[1])

    def test_ruled_hyphenated_captain_takes_the_error(self):
        self._assert_fragmented_form_errors(*FRAGMENTED_FORMS[2])

    def test_ruled_hyphenated_manager_takes_the_error(self):
        self._assert_fragmented_form_errors(*FRAGMENTED_FORMS[3])

    def test_ruled_pointed_manager_takes_the_error(self):
        self._assert_fragmented_form_errors(*FRAGMENTED_FORMS[4])

    def test_ruled_initials_name_alone_takes_the_error(self):
        self._assert_fragmented_form_errors(*FRAGMENTED_FORMS[5])


class GenuineFormGuardTest(unittest.TestCase):
    """The genuine forms keep passing: a "Ruled:" paragraph
    and a "Settled:" paragraph carrying real ruling matter
    satisfy the test, and genuine matter standing beside a
    fragmented name is not silenced by the fragmented name."""

    def test_ruled_paragraph_with_matter_takes_no_ruling_text_error(self):
        _model, output = h.run_pipeline(GENUINE_RULED, name="probe.md")
        self.assertEqual(_ruling_text_errors(output, "DQ-980"), [])
        self.assertEqual(_rule5_findings(output, "DQ-980"), [])

    def test_settled_paragraph_with_matter_takes_no_ruling_text_error(self):
        _model, output = h.run_pipeline(GENUINE_SETTLED, name="probe.md")
        self.assertEqual(_ruling_text_errors(output, "DQ-981"), [])
        self.assertEqual(_rule5_findings(output, "DQ-981"), [])

    def test_genuine_matter_beside_fragmented_name_still_passes(self):
        data = _decided_entry(
            "DQ-990",
            "Ruled: Captain J.P. ruled that the checker note "
            "takes the short form.")
        _model, output = h.run_pipeline(data, name="probe.md")
        self.assertEqual(_ruling_text_errors(output, "DQ-990"), [])

    def test_genuine_matter_after_initials_name_still_passes(self):
        data = _decided_entry(
            "DQ-991",
            "Ruled: J.P. Morgan takes the harbour.")
        _model, output = h.run_pipeline(data, name="probe.md")
        self.assertEqual(_ruling_text_errors(output, "DQ-991"), [])


class StatedBoundGuardTest(unittest.TestCase):
    """The bound Auditor 1 of round 6 recorded inside Seat
    O's stated bound stands unmoved by this cure: the test
    still judges presence of a non attribution content token,
    so an unrecorded name alone, a number alone, and a
    gibberish token each still pass, and the attribution
    adjunct and smuggled token forms Auditor 8 ruled no
    finding still pass."""

    def _assert_no_ruling_text_error(self, entry_id, paragraph,
                                     decider_sentence=None):
        data = _decided_entry(
            entry_id, paragraph, decider_sentence=decider_sentence)
        _model, output = h.run_pipeline(data, name="probe.md")
        self.assertEqual(
            _ruling_text_errors(output, entry_id), [], entry_id)

    def test_unrecorded_name_alone_still_passes(self):
        self._assert_no_ruling_text_error("DQ-992", "Ruled: Alice")

    def test_number_alone_still_passes(self):
        self._assert_no_ruling_text_error("DQ-993", "Ruled: 42.")

    def test_gibberish_token_still_passes(self):
        self._assert_no_ruling_text_error(
            "DQ-994", "Ruled: Captain JP xyzzy.")

    def test_attribution_adjunct_form_still_passes(self):
        self._assert_no_ruling_text_error(
            "DQ-995", "Ruled: Captain JP in the roles chat.")

    def test_smuggled_content_token_form_still_passes(self):
        self._assert_no_ruling_text_error(
            "DQ-996",
            "Ruled: Captain JP, the Manager under the grant, "
            "ruled settled decided closed, harbour.")


class StandingPositionGuardTest(unittest.TestCase):
    """The positions the earlier seats established still
    hold: a whole attribution separated by punctuation still
    takes the Error, fixture F-12 keeps exactly its one
    ruling text Error, the eight compact form entries keep
    their passes, the pin totals stand, and the level 4
    block and closing prose forms keep passing."""

    def test_separated_whole_attribution_still_takes_the_error(self):
        data = _decided_entry(
            "DQ-997",
            "Ruled: Captain, JP, Manager, under, the, grant.")
        _model, output = h.run_pipeline(data, name="probe.md")
        found = _ruling_text_errors(output, "DQ-997")
        self.assertEqual(len(found), 1)
        self.assertEqual(h.finding_severity(found[0]), "Error")

    def test_f12_keeps_exactly_one_ruling_text_error(self):
        _model, output = h.cached_pipeline("F-12")
        found = _ruling_text_errors(output, "DQ-001")
        self.assertEqual(len(found), 1)
        self.assertEqual(h.finding_severity(found[0]), "Error")
        self.assertEqual(len(_rule5_findings(output, "DQ-001")), 1)

    def test_pin_compact_form_entries_take_no_ruling_text_error(self):
        _model, output = h.cached_pipeline("PIN")
        for entry_id in ("DQ-147", "DQ-148", "DQ-149", "DQ-150",
                         "DQ-151", "DQ-152", "DQ-154", "DQ-155"):
            self.assertEqual(
                _ruling_text_errors(output, entry_id), [], entry_id)

    def test_pin_totals_stand(self):
        _model, output = h.cached_pipeline("PIN")
        counts = {"Error": 0, "Warning": 0, "Note": 0}
        for finding in h.findings_of(output):
            counts[h.finding_severity(finding)] += 1
        self.assertEqual(
            counts, {"Error": 16, "Warning": 57, "Note": 13})

    def test_level4_block_form_still_passes(self):
        _model, output = h.run_pipeline(BLOCK_FORM, name="probe.md")
        self.assertEqual(_rule5_findings(output, "DQ-982"), [])
        self.assertEqual(h.findings_of(output), [])

    def test_closing_prose_form_still_passes(self):
        _model, output = h.run_pipeline(
            CLOSING_PROSE_FORM, name="probe.md")
        self.assertEqual(_rule5_findings(output, "DQ-983"), [])


if __name__ == "__main__":
    unittest.main()
