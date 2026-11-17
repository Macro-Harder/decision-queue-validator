"""Restart Step 16 fix wave 4, Fix seat L tests.

Seat L owns finding A4-8-1 (Low) of Auditor 8, confirmation
round 4 (design/steps/step-16r-audit4-8.md, section 3): a
"Landed:" sentence naming a place in an in phrase but stating
an unrelated matter ("now states the weather forecast")
passes the landing limb of check 5 and suppresses the rule 5
landing Warning. Fix Seat K's paper
(design/steps/step-16r-fix3-k.md, section 4) specifies the
accepted construction as stating that the named place now
states the ruled matter; the code as cured by Seat K tests
only the label, an in word, and the words "now states".

Each test below pins the specified behaviour, written before
the cure. The unrelated matter tests fail before the cure and
pass after it. The genuine construction tests and the guard
tests pass before and after: DQ-167 on the corpus pin still
takes no landing Warning, DQ-153 still takes its Warning,
fixture F-13 still warns, DQ-168 and DQ-169 still pass, the
F-02 label form still passes, and a standalone "Landed:"
label paragraph still passes.

Copyright: J.P. Picard aka Macro-Harder
"""

import unittest

import dqv_harness as h


GENUINE = (
    "<!-- fix seat L probe: real tail shape, single paragraph "
    "opening with the Origin label, ruling and landing inside "
    "the paragraph -->\n"
    "\n"
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


UNRELATED = (
    "<!-- fix seat L probe: the genuine construction varied "
    "only in the matter the named place is stated to state -->\n"
    "\n"
    "## DQ-953: the harbour store note. RULED by Captain JP "
    "2026-11-15\n"
    "\n"
    "Origin: the harbour store question in the Clerk note of "
    "2026-11-14. Captain JP ruled in her own words: \"Keep the "
    "store by the harbour gate.\" Ruled: the harbour store "
    "stands by the harbour gate, and the night keeper holds "
    "its key. Landed: the harbour store paragraph in the Clerk "
    "note now states the weather forecast. Status: closed.\n"
).encode("utf-8")


STANDALONE_LABEL = (
    "<!-- fix seat L probe: a standalone Landed label "
    "paragraph standing after the tail paragraph -->\n"
    "\n"
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


def _landing_warnings(output, entry_id):
    found = []
    for finding in h.findings_for(output, entry_id=entry_id, rule=5):
        statement = h.finding_statement(finding) or ""
        if "No landing record" in statement:
            found.append(finding)
    return found


def _rule5_findings(output, entry_id):
    return h.findings_for(output, entry_id=entry_id, rule=5)


class UnrelatedMatterTest(unittest.TestCase):
    """A4-8-1: a Landed sentence stating a matter unrelated
    to the entry's ruling is no landing record."""

    def test_unrelated_matter_takes_the_landing_warning(self):
        _model, output = h.run_pipeline(UNRELATED, name="probe.md")
        found = _landing_warnings(output, "DQ-953")
        self.assertEqual(len(found), 1)
        self.assertEqual(h.finding_severity(found[0]), "Warning")

    def test_unrelated_matter_takes_no_other_rule5_finding(self):
        _model, output = h.run_pipeline(UNRELATED, name="probe.md")
        self.assertEqual(
            len(_rule5_findings(output, "DQ-953")),
            len(_landing_warnings(output, "DQ-953")))


class GenuineConstructionTest(unittest.TestCase):
    """The genuine construction, on the synthetic probe and
    on the corpus pin, still satisfies the landing test."""

    def test_synthetic_genuine_form_takes_no_landing_warning(self):
        _model, output = h.run_pipeline(GENUINE, name="probe.md")
        self.assertEqual(_landing_warnings(output, "DQ-953"), [])
        self.assertEqual(_rule5_findings(output, "DQ-953"), [])

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


class LandingGuardTest(unittest.TestCase):
    """The guards of the Fix Seat K file still hold."""

    def test_f13_no_landing_in_any_form_still_warns(self):
        _model, output = h.cached_pipeline("F-13")
        found = _landing_warnings(output, "DQ-001")
        self.assertEqual(len(found), 1)
        self.assertEqual(h.finding_severity(found[0]), "Warning")

    def test_pin_landed_in_and_at_forms_still_pass(self):
        _model, output = h.cached_pipeline("PIN")
        self.assertEqual(_landing_warnings(output, "DQ-168"), [])
        self.assertEqual(_landing_warnings(output, "DQ-169"), [])

    def test_where_the_ruling_landed_label_still_passes(self):
        _model, output = h.cached_pipeline("F-02")
        self.assertEqual(h.findings_of(output), [])

    def test_standalone_landed_label_paragraph_still_passes(self):
        _model, output = h.run_pipeline(
            STANDALONE_LABEL, name="probe.md")
        self.assertEqual(_landing_warnings(output, "DQ-964"), [])


if __name__ == "__main__":
    unittest.main()
