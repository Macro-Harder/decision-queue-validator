"""Restart Step 16 fix wave 5, Fix seat O tests.

Seat O owns the merged finding A5-2-F1 (Auditor 2, confirmation
round 5, design/steps/step-16r-audit5-2.md) and A5-8-2
(Auditor 8, confirmation round 5,
design/steps/step-16r-audit5-8.md, section 2 item 2): a
labelled paragraph opening "Ruled:" or "Settled:" that carries
no ruling matter at all satisfies the ruling text test that
Fix Seat M added in fix wave 4, and suppresses the rule 5
ruling text Error, though no ruling text stands in any form.
The evidenced empty forms are the bare label ("Ruled:" and
"Settled:" standing alone), the label with a decider name only
("Ruled: Captain JP", "Ruled: by Captain JP",
"Settled: Captain JP"), the label with punctuation only
("Ruled: ."), and the label with function and generic words
only ("Ruled: the form.").

The triage ground, at step record section 18: PIN-08 states
the presence tests over ruling text recorded in any form, and
a label with nothing under it records no ruling text, as
fixture F-12 already pins for the "Ruled by:" and
"Ruling outcome:" labels. The cure these tests pin: a
"Ruled:" or "Settled:" labelled paragraph satisfies the
ruling text test only where ruling matter stands under the
label beyond the label itself and beyond a decider
attribution alone.

Each test below pins the specified behaviour, written before
the cure. The empty form tests fail before the cure and pass
after it. The guard tests pass before and after: the genuine
labelled paragraph forms keep passing, the forms that passed
before still pass, fixture F-12 keeps exactly its one Error,
the eight compact form entries of the corpus pin keep taking
no ruling text Error, the pin totals stand, and a "Ruled:"
paragraph on a non-decided entry keeps deriving Ambiguous
with no presence pass recorded.

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
    "DQ-962", "Ruled: the checker note takes the short form.")

GENUINE_SETTLED = _decided_entry(
    "DQ-966", "Settled: the checker note takes the short form.",
    decider_sentence=SETTLED_DECIDER)

BLOCK_FORM = (
    "# Decision queue\n"
    "\n"
    "### DQ-961: the harbour consequence\n"
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
    "## DQ-953: the harbour store note. RULED by Captain JP "
    "2026-11-15\n"
    "\n"
    "Origin: the harbour store question in the Clerk note of "
    "2026-11-14. Captain JP ruled in her own words: \"Keep the "
    "store by the harbour gate.\" Ruled: the harbour store "
    "stands by the harbour gate, and the night keeper holds "
    "its key. Landed: the harbour store paragraph in the Clerk "
    "note now states the gate form. Status: closed.\n"
).encode("utf-8")


NON_DECIDED_FORM = _decided_entry(
    "DQ-971", "Ruled: the checker note takes the short form.",
    closing="Status: Banked")


EMPTY_FORMS = (
    ("DQ-990", "Ruled:", None),
    ("DQ-981", "Ruled: Captain JP", None),
    ("DQ-982", "Ruled: by Captain JP", None),
    ("DQ-991", "Settled: Captain JP", SETTLED_DECIDER),
    ("DQ-992", "Ruled: .", None),
    ("DQ-993", "Ruled: the form.", None),
    ("DQ-994", "Settled:", SETTLED_DECIDER),
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


class EmptyLabelledParagraphTest(unittest.TestCase):
    """A5-2-F1 and A5-8-2: a "Ruled:" or "Settled:" labelled
    paragraph carrying no ruling matter at all, or a decider
    attribution alone, records no ruling text, and the decided
    entry takes the rule 5 ruling text Error."""

    def _assert_empty_form_errors(self, entry_id, paragraph,
                                  decider_sentence):
        data = _decided_entry(
            entry_id, paragraph, decider_sentence=decider_sentence)
        _model, output = h.run_pipeline(data, name="probe.md")
        found = _ruling_text_errors(output, entry_id)
        self.assertEqual(len(found), 1, entry_id)
        self.assertEqual(h.finding_severity(found[0]), "Error")

    def test_bare_ruled_label_takes_the_error(self):
        self._assert_empty_form_errors(*EMPTY_FORMS[0])

    def test_ruled_label_with_decider_name_only_takes_the_error(self):
        self._assert_empty_form_errors(*EMPTY_FORMS[1])

    def test_ruled_label_with_by_decider_only_takes_the_error(self):
        self._assert_empty_form_errors(*EMPTY_FORMS[2])

    def test_settled_label_with_decider_name_only_takes_the_error(self):
        self._assert_empty_form_errors(*EMPTY_FORMS[3])

    def test_ruled_label_with_punctuation_only_takes_the_error(self):
        self._assert_empty_form_errors(*EMPTY_FORMS[4])

    def test_ruled_label_with_generic_words_only_takes_the_error(self):
        self._assert_empty_form_errors(*EMPTY_FORMS[5])

    def test_bare_settled_label_takes_the_error(self):
        self._assert_empty_form_errors(*EMPTY_FORMS[6])


class GenuineLabelledParagraphTest(unittest.TestCase):
    """The genuine forms keep passing: a "Ruled:" paragraph
    and a "Settled:" paragraph carrying real ruling matter
    satisfy the test, as Fix Seat M pinned."""

    def test_ruled_paragraph_with_matter_takes_no_ruling_text_error(self):
        _model, output = h.run_pipeline(GENUINE_RULED, name="probe.md")
        self.assertEqual(_ruling_text_errors(output, "DQ-962"), [])
        self.assertEqual(_rule5_findings(output, "DQ-962"), [])

    def test_settled_paragraph_with_matter_takes_no_ruling_text_error(self):
        _model, output = h.run_pipeline(GENUINE_SETTLED, name="probe.md")
        self.assertEqual(_ruling_text_errors(output, "DQ-966"), [])
        self.assertEqual(_rule5_findings(output, "DQ-966"), [])


class PassingFormsGuardTest(unittest.TestCase):
    """The forms that pass today still pass: the level 4
    ruling block, the closing prose form, and the labelled
    fields form of fixture F-02."""

    def test_level4_block_form_still_passes(self):
        _model, output = h.run_pipeline(BLOCK_FORM, name="probe.md")
        self.assertEqual(_rule5_findings(output, "DQ-961"), [])
        self.assertEqual(h.findings_of(output), [])

    def test_closing_prose_form_still_passes(self):
        _model, output = h.run_pipeline(
            CLOSING_PROSE_FORM, name="probe.md")
        self.assertEqual(_rule5_findings(output, "DQ-953"), [])

    def test_labelled_fields_form_f02_still_passes(self):
        _model, output = h.cached_pipeline("F-02")
        self.assertEqual(h.findings_of(output), [])


class NoRulingTextGuardTest(unittest.TestCase):
    """Fixture F-12, whose labelled paragraphs open with the
    "Ruled by:" and "Ruling outcome:" labels, keeps taking
    exactly its one ruling text Error."""

    def test_f12_keeps_exactly_one_ruling_text_error(self):
        _model, output = h.cached_pipeline("F-12")
        found = _ruling_text_errors(output, "DQ-001")
        self.assertEqual(len(found), 1)
        self.assertEqual(h.finding_severity(found[0]), "Error")
        self.assertEqual(len(_rule5_findings(output, "DQ-001")), 1)


class PinGuardTest(unittest.TestCase):
    """The corpus pin guards: the eight compact form entries
    still take no ruling text Error, and the pin totals stand
    at Error 16, Warning 57, Note 13."""

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


class NonDecidedGuardTest(unittest.TestCase):
    """Auditor 2's DQ-971 position: a "Ruled:" paragraph on an
    entry that does not stand decided satisfies nothing. The
    entry derives Ambiguous, the presence tests do not run,
    and no ruling text pass is recorded."""

    def test_ruled_paragraph_on_banked_entry_derives_ambiguous(self):
        _model, output = h.run_pipeline(
            NON_DECIDED_FORM, name="probe.md")
        entry = h.entry_by_id(output, "DQ-971")
        self.assertIsNotNone(entry)
        self.assertEqual(h.entry_state(entry), "Ambiguous")
        self.assertEqual(_rule5_findings(output, "DQ-971"), [])
        presence = h.get(entry, "presence_results")
        if isinstance(presence, dict):
            self.assertFalse(presence.get("ruling_text"))
        else:
            self.assertIsNone(presence)


if __name__ == "__main__":
    unittest.main()
