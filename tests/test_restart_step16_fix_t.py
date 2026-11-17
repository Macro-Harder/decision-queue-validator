"""Restart Step 16 fix wave 6, Fix seat T tests.

Seat T owns finding A6-8-2 (Low) of Auditor 8, confirmation
round 6 (design/steps/step-16r-audit6-8.md, section 1 item 7
and its findings list): an attribution only or empty
statement classified as a closing prose element satisfies
the ruling text test through the element limb, which
carries no matter condition at all. The evidenced forms are
a tab after the colon with "Captain JP" under both labels,
a tab with a full stop only, a prose paragraph whose only
decided matter is "Ruled: Captain JP", a fenced block
holding "Ruled: Captain JP", a fenced block holding the
bare label, and a blockquote holding "Ruled: Captain JP",
each at exit 0 with the ruling text Error suppressed.

The triage ground, at step record section 21: the form
stands DEFECTIVE under PIN-08 in the element limb: a
statement that records no ruling matter does not record
ruling text in any form, whichever limb classifies it; the
grade rests on the absence of matter, in plain text as much
as in a fence. The cure these tests pin: a closing prose
element satisfying by a labelled statement must meet the
same matter condition the labelled paragraph block applies
after Fix Seats O and S (at least one content token beyond
the label and beyond attribution alone, attribution read
whole across punctuation inside the word).

Each test below pins the specified behaviour, written
before the cure. The empty and attribution only form tests
fail before the cure and pass after it. The guard tests
pass before and after: genuine ruling matter in fenced and
blockquoted form keeps passing, genuine closing prose and
the level 4 block keep passing, fixture F-12 keeps exactly
its one ruling text Error, the eight compact form entries
of the corpus pin keep taking no ruling text Error, and the
pin totals stand.

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

BLOCK_FORM = (
    "# Decision queue\n"
    "\n"
    "### DQ-901: the harbour consequence\n"
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
    "## DQ-902: the harbour store note. RULED by Captain JP "
    "2026-11-15\n"
    "\n"
    "Origin: the harbour store question in the Clerk note of "
    "2026-11-14. Captain JP ruled in her own words: \"Keep the "
    "store by the harbour gate.\" Ruled: the harbour store "
    "stands by the harbour gate, and the night keeper holds "
    "its key. Landed: the harbour store paragraph in the Clerk "
    "note now states the gate form. Status: closed.\n"
).encode("utf-8")


EMPTY_ELEMENT_FORMS = (
    ("DQ-910", "Ruled:\tCaptain JP", None),
    ("DQ-911", "Settled:\tCaptain JP", SETTLED_DECIDER),
    ("DQ-912", "Ruled:\t.", None),
    ("DQ-913", "The meeting ended at noon. Ruled: Captain JP", None),
    ("DQ-914", "```\nRuled: Captain JP\n```", None),
    ("DQ-915", "```\nRuled:\n```", None),
    ("DQ-916", "> Ruled: Captain JP", None),
    ("DQ-917", "```\nRuled: Captain J.P.\n```", None),
    ("DQ-918", "> Ruled: Cap-tain JP", None),
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


class EmptyElementFormTest(unittest.TestCase):
    """A6-8-2: an attribution only or empty statement that
    parse classifies as a closing prose element records no
    ruling text, and the decided entry takes the rule 5
    ruling text Error, in plain, fenced and blockquoted
    form alike."""

    def _assert_empty_form_errors(self, entry_id, paragraph,
                                  decider_sentence):
        data = _decided_entry(
            entry_id, paragraph, decider_sentence=decider_sentence)
        _model, output = h.run_pipeline(data, name="probe.md")
        found = _ruling_text_errors(output, entry_id)
        self.assertEqual(len(found), 1, entry_id)
        self.assertEqual(h.finding_severity(found[0]), "Error")

    def test_tab_ruled_attribution_only_takes_the_error(self):
        self._assert_empty_form_errors(*EMPTY_ELEMENT_FORMS[0])

    def test_tab_settled_attribution_only_takes_the_error(self):
        self._assert_empty_form_errors(*EMPTY_ELEMENT_FORMS[1])

    def test_tab_full_stop_only_takes_the_error(self):
        self._assert_empty_form_errors(*EMPTY_ELEMENT_FORMS[2])

    def test_prose_paragraph_attribution_only_takes_the_error(self):
        self._assert_empty_form_errors(*EMPTY_ELEMENT_FORMS[3])

    def test_fenced_attribution_only_takes_the_error(self):
        self._assert_empty_form_errors(*EMPTY_ELEMENT_FORMS[4])

    def test_fenced_bare_label_takes_the_error(self):
        self._assert_empty_form_errors(*EMPTY_ELEMENT_FORMS[5])

    def test_blockquote_attribution_only_takes_the_error(self):
        self._assert_empty_form_errors(*EMPTY_ELEMENT_FORMS[6])

    def test_fenced_fragmented_attribution_takes_the_error(self):
        self._assert_empty_form_errors(*EMPTY_ELEMENT_FORMS[7])

    def test_blockquote_fragmented_attribution_takes_the_error(self):
        self._assert_empty_form_errors(*EMPTY_ELEMENT_FORMS[8])


class GenuineElementFormGuardTest(unittest.TestCase):
    """The genuine forms keep passing exactly as today:
    genuine ruling matter in fenced and blockquoted form
    stands in the standing ungraded fence territory and is
    not moved by a cure scoped to the absence of matter,
    and genuine matter in the plainer element forms keeps
    passing on the same evidence."""

    def _assert_no_ruling_text_error(self, entry_id, paragraph,
                                     decider_sentence=None):
        data = _decided_entry(
            entry_id, paragraph, decider_sentence=decider_sentence)
        _model, output = h.run_pipeline(data, name="probe.md")
        self.assertEqual(
            _ruling_text_errors(output, entry_id), [], entry_id)

    def test_fenced_genuine_matter_still_passes(self):
        self._assert_no_ruling_text_error(
            "DQ-920",
            "```\nRuled: the checker note takes the short form.\n```")

    def test_blockquote_genuine_matter_still_passes(self):
        self._assert_no_ruling_text_error(
            "DQ-921", "> Ruled: the checker note takes the short form.")

    def test_tab_genuine_matter_still_passes(self):
        self._assert_no_ruling_text_error(
            "DQ-922", "Ruled:\tthe checker note takes the short form.")

    def test_prose_paragraph_genuine_matter_still_passes(self):
        self._assert_no_ruling_text_error(
            "DQ-923",
            "The meeting ended at noon. Ruled: the checker note "
            "takes the short form.")

    def test_fenced_genuine_matter_beside_fragmented_name_passes(self):
        self._assert_no_ruling_text_error(
            "DQ-924",
            "```\nRuled: Captain J.P. ruled that the checker note "
            "takes the short form.\n```")

    def test_tab_gibberish_token_still_passes(self):
        self._assert_no_ruling_text_error(
            "DQ-925", "Ruled:\tCaptain JP xyzzy.")

    def test_blockquote_bare_label_still_takes_the_error(self):
        data = _decided_entry("DQ-926", "> Ruled:")
        _model, output = h.run_pipeline(data, name="probe.md")
        found = _ruling_text_errors(output, "DQ-926")
        self.assertEqual(len(found), 1)
        self.assertEqual(h.finding_severity(found[0]), "Error")


class StandingPositionGuardTest(unittest.TestCase):
    """The positions the earlier seats established still
    hold: the closing prose and level 4 block forms keep
    passing, the labelled fields form of fixture F-02 takes
    no findings, fixture F-12 keeps exactly its one ruling
    text Error, the eight compact form entries keep their
    passes, and the pin totals stand."""

    def test_closing_prose_form_still_passes(self):
        _model, output = h.run_pipeline(
            CLOSING_PROSE_FORM, name="probe.md")
        self.assertEqual(_rule5_findings(output, "DQ-902"), [])

    def test_level4_block_form_still_passes(self):
        _model, output = h.run_pipeline(BLOCK_FORM, name="probe.md")
        self.assertEqual(_rule5_findings(output, "DQ-901"), [])
        self.assertEqual(h.findings_of(output), [])

    def test_labelled_fields_form_f02_still_passes(self):
        _model, output = h.cached_pipeline("F-02")
        self.assertEqual(h.findings_of(output), [])

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


if __name__ == "__main__":
    unittest.main()
