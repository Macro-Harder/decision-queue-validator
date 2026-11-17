"""Restart Step 16 fix wave 6, Fix seat R tests.

Seat R owns the merged construction of finding A6-2-1 (Low)
of Auditor 2, confirmation round 6
(design/steps/step-16r-audit6-2.md, section 2 case E5 and
section 6), and finding A6-8-3 (Low) of Auditor 8,
confirmation round 6 (design/steps/step-16r-audit6-8.md,
section 2 item 4 and its findings list): within the landing
paragraph, a sentence that is not a ruling segment and not
the Landed segment, standing before the Landed segment and
outside the ruling segment run, supplies the only shared
content tokens and earns the landing pass. Fix Seat P's
cure (design/steps/step-16r-fix5-p.md) excluded the Landed
segment and every segment after it in its paragraph; the
segments before the Landed segment in that paragraph kept
supplying under Seat L's rules, and the two round 6 seats
showed a plain prose sentence in that before position
supplying the stated matter alone.

Each test below pins the specified behaviour, written
before the cure. The before position tests fail before the
cure and pass after it: the Auditor 2 probe shape and
Auditor 8's three variants, in each of which the stated
matter stands nowhere in the entry outside the landing
paragraph, must take the rule 5 landing Warning. The guard
tests pass before and after: the DQ-167 shape, whose Ruled
segment stands before the Landed segment in the same
paragraph, still passes; a ruling segment in another
paragraph, before or after the landing paragraph, still
supplies; a genuine ruling restated in its own paragraph
still supplies; the unrelated matter with no repetition
still warns; DQ-167 on the corpus pin still takes no rule
5 finding, DQ-153 still takes its one landing Warning, and
fixture F-13 still warns exactly once.

Copyright: J.P. Picard aka Macro-Harder
"""

import unittest

import dqv_harness as h


RULING_PARA = (
    "Origin: the harbour store question in the Clerk note of "
    "2026-11-14. Captain JP ruled in her own words: \"Keep the "
    "store by the harbour gate.\" Ruled: the harbour store "
    "stands by the harbour gate, and the night keeper holds "
    "its key."
)


def _entry(entry_id, paragraphs):
    text = (
        "## %s: the harbour store note. RULED by Captain JP "
        "2026-11-15\n"
        "\n"
        "%s\n"
    ) % (entry_id, "\n\n".join(paragraphs))
    return text.encode("utf-8")


AUDITOR2_PROBE = _entry("DQ-960", (
    RULING_PARA,
    "The filing was checked in the Clerk note on 2026-11-15. "
    "The weather forecast is sunny. Landed: the harbour store "
    "paragraph in the Clerk note now states the weather "
    "forecast.",
    "Status: closed.",
))


AUDITOR8_VARIANT_A = _entry("DQ-961", (
    RULING_PARA,
    "The weather forecast is sunny. Landed: the harbour store "
    "paragraph in the Clerk note now states the weather "
    "forecast.",
    "Status: closed.",
))


AUDITOR8_VARIANT_B = _entry("DQ-962", (
    RULING_PARA,
    "The filing note was entered in the Clerk note on "
    "2026-11-15. The weather forecast is sunny. Landed: the "
    "harbour store paragraph in the Clerk note now states "
    "the weather forecast.",
    "Status: closed.",
))


AUDITOR8_VARIANT_C = _entry("DQ-963", (
    "Ruled by Captain JP in the roles chat on 2026-11-14.",
    "Ruling text: the checker note takes the short form.",
    "Ruling outcome: The outcome stands as recorded.",
    "The weather forecast is sunny. Landed: the harbour store "
    "paragraph in the Clerk note now states the weather "
    "forecast.",
    "Status: closed.",
))


GENUINE_TAIL = (
    "## DQ-964: the harbour store note. RULED by Captain JP "
    "2026-11-15\n"
    "\n"
    "Origin: the harbour store question in the Clerk note of "
    "2026-11-14. Captain JP ruled in her own words: \"Keep the "
    "store by the harbour gate.\" Ruled: the harbour store "
    "stands by the harbour gate, and the night keeper holds "
    "its key. Landed: the harbour store paragraph in the Clerk "
    "note now states the gate form. Status: closed.\n"
).encode("utf-8")


GENUINE_RULING_BEFORE = _entry("DQ-965", (
    RULING_PARA,
    "The filing was checked in the Clerk note on 2026-11-15. "
    "Landed: the harbour store paragraph in the Clerk note "
    "now states the gate form.",
    "Status: closed.",
))


GENUINE_RULING_AFTER = _entry("DQ-966", (
    "The filing was checked in the Clerk note on 2026-11-15. "
    "Landed: the harbour store paragraph in the Clerk note "
    "now states the gate form.",
    RULING_PARA,
    "Status: closed.",
))


GENUINE_RESTATE_OWN_PARA_AFTER = _entry("DQ-967", (
    "Ruled by Captain JP in the roles chat on 2026-11-14.",
    "Ruling text: the checker note takes the short form.",
    "Ruling outcome: The outcome stands as recorded.",
    "The filing was checked in the Clerk note on 2026-11-15. "
    "Landed: the harbour store paragraph in the Clerk note "
    "now states the gate form.",
    "The gate form is the harbour store standing by the "
    "harbour gate.",
    "Status: closed.",
))


GENUINE_RESTATE_OWN_PARA_BEFORE = _entry("DQ-968", (
    "Ruled by Captain JP in the roles chat on 2026-11-14.",
    "Ruling text: the checker note takes the short form.",
    "Ruling outcome: The outcome stands as recorded.",
    "The gate form is the harbour store standing by the "
    "harbour gate.",
    "The filing was checked in the Clerk note on 2026-11-15. "
    "Landed: the harbour store paragraph in the Clerk note "
    "now states the gate form.",
    "Status: closed.",
))


UNRELATED_NO_REPETITION = _entry("DQ-969", (
    RULING_PARA,
    "The filing was checked in the Clerk note on 2026-11-15. "
    "Landed: the harbour store paragraph in the Clerk note "
    "now states the weather forecast.",
    "Status: closed.",
))


def _landing_warnings(output, entry_id):
    found = []
    for finding in h.findings_for(output, entry_id=entry_id, rule=5):
        statement = h.finding_statement(finding) or ""
        if "No landing record" in statement:
            found.append(finding)
    return found


def _rule5_findings(output, entry_id):
    return h.findings_for(output, entry_id=entry_id, rule=5)


class BeforeLandedRepetitionTest(unittest.TestCase):
    """A6-2-1 and A6-8-3: a plain prose sentence standing
    before the Landed segment in the landing paragraph,
    repeating the unrelated matter the Landed sentence
    states, earns the landing pass before the cure and must
    earn nothing after it. In every construction the stated
    matter stands nowhere in the entry outside the landing
    paragraph."""

    def test_auditor2_probe_shape_warns(self):
        _model, output = h.run_pipeline(
            AUDITOR2_PROBE, name="probe.md")
        found = _landing_warnings(output, "DQ-960")
        self.assertEqual(len(found), 1)
        self.assertEqual(h.finding_severity(found[0]), "Warning")

    def test_auditor8_variant_a_warns(self):
        _model, output = h.run_pipeline(
            AUDITOR8_VARIANT_A, name="probe.md")
        found = _landing_warnings(output, "DQ-961")
        self.assertEqual(len(found), 1)
        self.assertEqual(h.finding_severity(found[0]), "Warning")

    def test_auditor8_variant_b_warns(self):
        _model, output = h.run_pipeline(
            AUDITOR8_VARIANT_B, name="probe.md")
        found = _landing_warnings(output, "DQ-962")
        self.assertEqual(len(found), 1)
        self.assertEqual(h.finding_severity(found[0]), "Warning")

    def test_auditor8_variant_c_warns(self):
        _model, output = h.run_pipeline(
            AUDITOR8_VARIANT_C, name="probe.md")
        found = _landing_warnings(output, "DQ-963")
        self.assertEqual(len(found), 1)
        self.assertEqual(h.finding_severity(found[0]), "Warning")

    def test_auditor8_variant_c_no_other_rule5(self):
        _model, output = h.run_pipeline(
            AUDITOR8_VARIANT_C, name="probe.md")
        self.assertEqual(
            len(_rule5_findings(output, "DQ-963")),
            len(_landing_warnings(output, "DQ-963")))


class GenuineSupplyGuardTest(unittest.TestCase):
    """A genuine ruling standing in a ruling segment, in the
    landing paragraph itself or in a paragraph of its own,
    still earns the pass, and the pin guards hold."""

    def test_dq167_shape_ruling_segment_still_passes(self):
        _model, output = h.run_pipeline(GENUINE_TAIL, name="probe.md")
        self.assertEqual(_landing_warnings(output, "DQ-964"), [])
        self.assertEqual(_rule5_findings(output, "DQ-964"), [])

    def test_ruling_segment_in_paragraph_before_supplies(self):
        _model, output = h.run_pipeline(
            GENUINE_RULING_BEFORE, name="probe.md")
        self.assertEqual(_landing_warnings(output, "DQ-965"), [])
        self.assertEqual(_rule5_findings(output, "DQ-965"), [])

    def test_ruling_segment_in_paragraph_after_supplies(self):
        _model, output = h.run_pipeline(
            GENUINE_RULING_AFTER, name="probe.md")
        self.assertEqual(_landing_warnings(output, "DQ-966"), [])
        self.assertEqual(_rule5_findings(output, "DQ-966"), [])

    def test_genuine_restated_in_own_paragraph_after_supplies(self):
        _model, output = h.run_pipeline(
            GENUINE_RESTATE_OWN_PARA_AFTER, name="probe.md")
        self.assertEqual(_landing_warnings(output, "DQ-967"), [])
        self.assertEqual(_rule5_findings(output, "DQ-967"), [])

    def test_genuine_restated_in_own_paragraph_before_supplies(self):
        _model, output = h.run_pipeline(
            GENUINE_RESTATE_OWN_PARA_BEFORE, name="probe.md")
        self.assertEqual(_landing_warnings(output, "DQ-968"), [])
        self.assertEqual(_rule5_findings(output, "DQ-968"), [])

    def test_pin_dq167_takes_no_landing_warning(self):
        _model, output = h.cached_pipeline("PIN")
        self.assertEqual(_landing_warnings(output, "DQ-167"), [])

    def test_pin_dq167_takes_no_rule5_finding(self):
        _model, output = h.cached_pipeline("PIN")
        self.assertEqual(_rule5_findings(output, "DQ-167"), [])

    def test_pin_dq153_still_takes_its_landing_warning(self):
        _model, output = h.cached_pipeline("PIN")
        found = _landing_warnings(output, "DQ-153")
        self.assertEqual(len(found), 1)
        self.assertEqual(h.finding_severity(found[0]), "Warning")


class StandingWarningGuardTest(unittest.TestCase):
    """The positions the earlier seats established still
    hold: the unrelated matter with no repetition warns, and
    an entry with no landing record in any form warns."""

    def test_unrelated_matter_no_repetition_still_warns(self):
        _model, output = h.run_pipeline(
            UNRELATED_NO_REPETITION, name="probe.md")
        found = _landing_warnings(output, "DQ-969")
        self.assertEqual(len(found), 1)
        self.assertEqual(h.finding_severity(found[0]), "Warning")

    def test_f13_no_landing_in_any_form_still_warns(self):
        _model, output = h.cached_pipeline("F-13")
        found = _landing_warnings(output, "DQ-001")
        self.assertEqual(len(found), 1)
        self.assertEqual(h.finding_severity(found[0]), "Warning")


if __name__ == "__main__":
    unittest.main()
