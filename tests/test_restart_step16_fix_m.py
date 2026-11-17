"""Restart Step 16 fix wave 4, Fix seat M tests.

Seat M owns finding A20-F1 (Medium) of Auditor 20, confirmation
round 4 (design/steps/step-16r-audit4-20.md, sections 2, 3, 5
and 7): a decided entry whose ruling stands as its own
labelled paragraph opening "Ruled:" takes a rule 5 Error
stating that no ruling text is recorded for the entry in any
form, with the finding's own evidence line quoting that very
paragraph. The same ruling words pass inside a level 4 ruling
block and inside closing prose. The paragraph is the entry's
determining element, it derives the Ruled state, and it
satisfies the outcome presence test; only the ruling text
limb of check 5 does not count this form.

The brief ground, quoted in the seat paper
(design/steps/step-16r-fix4-m.md): PIN-08 at brief section 5.3
states the four presence tests as tests "over all recorded
label forms" and grades "no ruling text in any recorded label
form" as an Error; PIN-01 form 2 at brief section 5.2 lists
the recorded label forms for an unheaded labelled paragraph
and the list includes Ruled and Settled; and the consolidated
restart notes record the compact ruled form at DQ-147 and
DQ-148 as one long "Ruled:" paragraph dropping the Ruling
text line. No brief or plan locus enumerates a narrower set
for the ruling text limb that excludes this form.

Each test below pins the specified behaviour, written before
the cure. The standalone paragraph tests fail before the cure
and pass after it. The guard tests pass before and after: a
decided entry with no ruling text in any form still takes the
Error, the forms that pass today still pass, and the landing
pins of Fix Seats K and L are unaffected.

Copyright: J.P. Picard aka Macro-Harder
"""

import unittest

import dqv_harness as h


AUDITOR_FORM = (
    "# Decision queue\n"
    "\n"
    "### DQ-962: the checker note form\n"
    "\n"
    "Status: Banked\n"
    "\n"
    "Ruled by Captain JP in the roles chat on 2026-11-14.\n"
    "\n"
    "Ruled: the checker note takes the short form.\n"
    "\n"
    "Landed: the checker note in NOTES.md section 2 now "
    "states the agreed form.\n"
    "\n"
    "Status: closed.\n"
).encode("utf-8")


SETTLED_FORM = (
    "# Decision queue\n"
    "\n"
    "### DQ-966: the checker note settlement\n"
    "\n"
    "Status: Banked\n"
    "\n"
    "Settled by the Manager under the grant, recorded in the "
    "roles chat on 2026-11-14.\n"
    "\n"
    "Settled: the checker note takes the short form.\n"
    "\n"
    "Landed: the checker note in NOTES.md section 2 now "
    "states the agreed form.\n"
    "\n"
    "Status: closed.\n"
).encode("utf-8")


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


STANDALONE_LANDED_LABEL = (
    "## DQ-964: the harbour store note. RULED by Captain JP "
    "2026-11-15\n"
    "\n"
    "Origin: the harbour store question in the Clerk note of "
    "2026-11-14. Captain JP ruled in her own words: \"Keep the "
    "store by the harbour gate.\" Ruled: the harbour store "
    "stands by the harbour gate, and the night keeper holds "
    "its key. Status: closed.\n"
    "\n"
    "Landed: the Clerk note.\n"
).encode("utf-8")


def _ruling_text_errors(output, entry_id):
    found = []
    for finding in h.findings_for(output, entry_id=entry_id, rule=5):
        statement = h.finding_statement(finding) or ""
        if "No ruling text" in statement:
            found.append(finding)
    return found


def _landing_warnings(output, entry_id):
    found = []
    for finding in h.findings_for(output, entry_id=entry_id, rule=5):
        statement = h.finding_statement(finding) or ""
        if "No landing record" in statement:
            found.append(finding)
    return found


def _rule5_findings(output, entry_id):
    return h.findings_for(output, entry_id=entry_id, rule=5)


class StandaloneRuledParagraphTest(unittest.TestCase):
    """A20-F1: a standalone labelled paragraph opening with
    the Ruled label, or with the Settled label, is a ruling
    text record in a recorded label form."""

    def test_auditor_form_takes_no_ruling_text_error(self):
        _model, output = h.run_pipeline(AUDITOR_FORM, name="probe.md")
        self.assertEqual(_ruling_text_errors(output, "DQ-962"), [])

    def test_auditor_form_takes_no_rule5_finding(self):
        _model, output = h.run_pipeline(AUDITOR_FORM, name="probe.md")
        self.assertEqual(_rule5_findings(output, "DQ-962"), [])

    def test_settled_label_form_takes_no_ruling_text_error(self):
        _model, output = h.run_pipeline(SETTLED_FORM, name="probe.md")
        self.assertEqual(_ruling_text_errors(output, "DQ-966"), [])
        self.assertEqual(_rule5_findings(output, "DQ-966"), [])

    def test_pin_compact_form_entries_take_no_ruling_text_error(self):
        _model, output = h.cached_pipeline("PIN")
        for entry_id in ("DQ-147", "DQ-148", "DQ-149", "DQ-150",
                         "DQ-151", "DQ-152", "DQ-154", "DQ-155"):
            self.assertEqual(
                _ruling_text_errors(output, entry_id), [], entry_id)


class NoRulingTextGuardTest(unittest.TestCase):
    """The cure must not silence the ruling text test where
    no ruling text stands in any form. Fixture F-12 carries a
    decider, an outcome, and a landing, and no ruling text in
    any recorded label form, singular or plural; its labelled
    paragraphs open with the Ruled by label and the Ruling
    outcome label, neither of which is a ruling text."""

    def test_f12_no_ruling_text_in_any_form_still_errors(self):
        _model, output = h.cached_pipeline("F-12")
        found = _ruling_text_errors(output, "DQ-001")
        self.assertEqual(len(found), 1)
        self.assertEqual(h.finding_severity(found[0]), "Error")

    def test_f11_no_decider_still_errors(self):
        _model, output = h.cached_pipeline("F-11")
        found = []
        for finding in h.findings_for(output, entry_id="DQ-001", rule=5):
            statement = h.finding_statement(finding) or ""
            if "No decider" in statement:
                found.append(finding)
        self.assertEqual(len(found), 1)
        self.assertEqual(h.finding_severity(found[0]), "Error")


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


class LandingPinsUnaffectedTest(unittest.TestCase):
    """The landing pins of Fix Seats K and L stand exactly as
    those seats left them."""

    def test_pin_dq167_takes_no_rule5_finding(self):
        _model, output = h.cached_pipeline("PIN")
        self.assertEqual(_rule5_findings(output, "DQ-167"), [])

    def test_pin_dq153_still_takes_its_landing_warning(self):
        _model, output = h.cached_pipeline("PIN")
        found = _landing_warnings(output, "DQ-153")
        self.assertEqual(len(found), 1)
        self.assertEqual(h.finding_severity(found[0]), "Warning")

    def test_f13_no_landing_in_any_form_still_warns(self):
        _model, output = h.cached_pipeline("F-13")
        found = _landing_warnings(output, "DQ-001")
        self.assertEqual(len(found), 1)
        self.assertEqual(h.finding_severity(found[0]), "Warning")

    def test_standalone_landed_label_paragraph_still_passes(self):
        _model, output = h.run_pipeline(
            STANDALONE_LANDED_LABEL, name="probe.md")
        self.assertEqual(_landing_warnings(output, "DQ-964"), [])


if __name__ == "__main__":
    unittest.main()
