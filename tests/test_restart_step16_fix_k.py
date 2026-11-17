"""Restart Step 16 fix wave 3, Fix seat K tests.

Seat K owns finding A3-7-F1 (Low) of Auditor 7, confirmation
round 3 (design/steps/step-16r-audit3-7.md, section 5): a
decided entry whose landing record stands solely in the
"Landed:" colon label form takes a rule 5 Warning stating
that no landing record is recorded for it in any form. PIN-08
and fixture F-13 state the landing test as no landing record
in any form, and no brief or plan locus enumerates the
accepted landing forms or excludes the colon label form.
Entry DQ-167 on the corpus pin carries its landing solely in
that form, and DQ-168 and DQ-169, which also carry landed in
and landed at sentences, take no such Warning.

Each test below pins the specified behaviour, written before
the cure. The two colon label tests fail before the cure and
pass after it. The guard tests pass before and after: a
decided entry with no landing record in any form still takes
the rule 5 Warning, and the landed in and landed at sentence
forms and the Where the ruling landed label form that pass
today still pass.

Copyright: J.P. Picard aka Macro-Harder
"""

import unittest

import dqv_harness as h


PROBE = (
    "<!-- fix seat K probe: real tail shape, single paragraph "
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


def _landing_warnings(output, entry_id):
    found = []
    for finding in h.findings_for(output, entry_id=entry_id, rule=5):
        statement = h.finding_statement(finding) or ""
        if "No landing record" in statement:
            found.append(finding)
    return found


def _rule5_findings(output, entry_id):
    return h.findings_for(output, entry_id=entry_id, rule=5)


class LandedColonLabelFormTest(unittest.TestCase):
    """A3-7-F1: the Landed colon label form is a landing
    record in its own right."""

    def test_colon_label_only_landing_takes_no_landing_warning(self):
        _model, output = h.run_pipeline(PROBE, name="probe.md")
        self.assertEqual(_landing_warnings(output, "DQ-953"), [])

    def test_colon_label_only_landing_takes_no_rule5_finding(self):
        _model, output = h.run_pipeline(PROBE, name="probe.md")
        self.assertEqual(_rule5_findings(output, "DQ-953"), [])

    def test_pin_dq167_takes_no_landing_warning(self):
        _model, output = h.cached_pipeline("PIN")
        self.assertEqual(_landing_warnings(output, "DQ-167"), [])

    def test_pin_dq167_takes_no_rule5_finding(self):
        _model, output = h.cached_pipeline("PIN")
        self.assertEqual(_rule5_findings(output, "DQ-167"), [])


class LandingGuardTest(unittest.TestCase):
    """The cure must not silence the landing test where no
    landing record stands in any form, and must not disturb
    the forms that pass today."""

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


if __name__ == "__main__":
    unittest.main()
