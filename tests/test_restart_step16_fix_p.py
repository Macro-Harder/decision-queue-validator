"""Restart Step 16 fix wave 5, Fix seat P tests.

Seat P owns finding A5-8-1 (Low) of Auditor 8, confirmation
round 5 (design/steps/step-16r-audit5-8.md, section 1 item 8
and its findings list): a Landed sentence stating an
unrelated matter (the weather forecast form) passes the
landing limb of check 5 where the same paragraph carries a
trailing sentence repeating that matter, because sentence
segmentation makes the trailing sentence a segment of its
own whose tokens enter the ruling text token set. Fix Seat
L's cure (design/steps/step-16r-fix4-l.md, section 2) states
its rationale as: a Landed segment never counts toward its
own ruling text, so a matter named only inside the landing
claim itself earns nothing. The step record triage at
section 18 reads that rationale at paragraph granularity: a
paragraph that carries the landing claim is the landing
claim for this purpose, in all its sentences after the
landing sentence, and a matter named only there earns
nothing.

Each test below pins the specified behaviour, written before
the cure. The trailing repetition tests fail before the cure
and pass after it. The guard tests pass before and after:
a genuine ruling standing in its own paragraph, before or
after the landing paragraph, still earns the pass; the
genuine ruling segment standing before the Landed segment
in the same paragraph (the DQ-167 shape) still earns the
pass; the unrelated matter with no repetition still warns;
DQ-167 on the corpus pin still takes no rule 5 finding, and
DQ-153 still takes exactly its one landing Warning.

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


WEATHER_TRAILING_MULTI = _entry("DQ-953", (
    RULING_PARA,
    "The filing was checked in the Clerk note on 2026-11-15. "
    "Landed: the harbour store paragraph in the Clerk note "
    "now states the weather forecast. The weather forecast "
    "is sunny.",
    "Status: closed.",
))


WEATHER_TRAILING_TAIL = (
    "## DQ-954: the harbour store note. RULED by Captain JP "
    "2026-11-15\n"
    "\n"
    "Origin: the harbour store question in the Clerk note of "
    "2026-11-14. Captain JP ruled in her own words: \"Keep the "
    "store by the harbour gate.\" Ruled: the harbour store "
    "stands by the harbour gate, and the night keeper holds "
    "its key. Landed: the harbour store paragraph in the Clerk "
    "note now states the weather forecast. The weather "
    "forecast is sunny. Status: closed.\n"
).encode("utf-8")


GENUINE_RESTATE_TRAILING = _entry("DQ-955", (
    "Ruled by Captain JP in the roles chat on 2026-11-14.",
    "Ruling text: the checker note takes the short form.",
    "Ruling outcome: The outcome stands as recorded.",
    "The filing was checked in the Clerk note on 2026-11-15. "
    "Landed: the harbour store paragraph in the Clerk note "
    "now states the gate form. The gate form is the harbour "
    "store standing by the harbour gate.",
    "Status: closed.",
))


GENUINE_RULING_BEFORE = _entry("DQ-956", (
    RULING_PARA,
    "The filing was checked in the Clerk note on 2026-11-15. "
    "Landed: the harbour store paragraph in the Clerk note "
    "now states the gate form.",
    "Status: closed.",
))


GENUINE_RULING_AFTER = _entry("DQ-957", (
    "The filing was checked in the Clerk note on 2026-11-15. "
    "Landed: the harbour store paragraph in the Clerk note "
    "now states the gate form.",
    RULING_PARA,
    "Status: closed.",
))


GENUINE_TAIL = (
    "## DQ-958: the harbour store note. RULED by Captain JP "
    "2026-11-15\n"
    "\n"
    "Origin: the harbour store question in the Clerk note of "
    "2026-11-14. Captain JP ruled in her own words: \"Keep the "
    "store by the harbour gate.\" Ruled: the harbour store "
    "stands by the harbour gate, and the night keeper holds "
    "its key. Landed: the harbour store paragraph in the Clerk "
    "note now states the gate form. Status: closed.\n"
).encode("utf-8")


UNRELATED_NO_REPETITION = _entry("DQ-959", (
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


class WeatherTrailingRepetitionTest(unittest.TestCase):
    """A5-8-1: a trailing sentence inside the landing
    paragraph, repeating the unrelated matter the Landed
    sentence states, earns the landing pass before the cure
    and must earn nothing after it."""

    def test_weather_trailing_in_own_paragraph_warns(self):
        _model, output = h.run_pipeline(
            WEATHER_TRAILING_MULTI, name="probe.md")
        found = _landing_warnings(output, "DQ-953")
        self.assertEqual(len(found), 1)
        self.assertEqual(h.finding_severity(found[0]), "Warning")

    def test_weather_trailing_in_own_paragraph_no_other_rule5(self):
        _model, output = h.run_pipeline(
            WEATHER_TRAILING_MULTI, name="probe.md")
        self.assertEqual(
            len(_rule5_findings(output, "DQ-953")),
            len(_landing_warnings(output, "DQ-953")))

    def test_weather_trailing_in_tail_paragraph_warns(self):
        _model, output = h.run_pipeline(
            WEATHER_TRAILING_TAIL, name="probe.md")
        found = _landing_warnings(output, "DQ-954")
        self.assertEqual(len(found), 1)
        self.assertEqual(h.finding_severity(found[0]), "Warning")


class GenuineRestateTrailingTest(unittest.TestCase):
    """The same paragraph form with a genuine ruling restated
    in a trailing sentence of the landing paragraph also
    warns after the cure: the paragraph no longer supplies
    its own corroboration, as the triage ruling states. The
    entry's ruling text stands in a labelled field whose
    words share no content token with the stated matter, so
    the trailing sentence is the only supply of that token
    before the cure."""

    def test_genuine_restated_only_in_trailing_sentence_warns(self):
        _model, output = h.run_pipeline(
            GENUINE_RESTATE_TRAILING, name="probe.md")
        found = _landing_warnings(output, "DQ-955")
        self.assertEqual(len(found), 1)
        self.assertEqual(h.finding_severity(found[0]), "Warning")


class GenuineOutsideLandingParagraphTest(unittest.TestCase):
    """A genuine ruling standing outside the landing
    paragraph, or in the ruling segment before the Landed
    segment of the same paragraph, still earns the pass."""

    def test_ruling_paragraph_before_landing_paragraph_passes(self):
        _model, output = h.run_pipeline(
            GENUINE_RULING_BEFORE, name="probe.md")
        self.assertEqual(_landing_warnings(output, "DQ-956"), [])
        self.assertEqual(_rule5_findings(output, "DQ-956"), [])

    def test_ruling_paragraph_after_landing_paragraph_passes(self):
        _model, output = h.run_pipeline(
            GENUINE_RULING_AFTER, name="probe.md")
        self.assertEqual(_landing_warnings(output, "DQ-957"), [])
        self.assertEqual(_rule5_findings(output, "DQ-957"), [])

    def test_genuine_tail_form_ruling_segment_still_passes(self):
        _model, output = h.run_pipeline(GENUINE_TAIL, name="probe.md")
        self.assertEqual(_landing_warnings(output, "DQ-958"), [])
        self.assertEqual(_rule5_findings(output, "DQ-958"), [])

    def test_pin_dq167_takes_no_landing_warning(self):
        _model, output = h.cached_pipeline("PIN")
        self.assertEqual(_landing_warnings(output, "DQ-167"), [])

    def test_pin_dq167_takes_no_rule5_finding(self):
        _model, output = h.cached_pipeline("PIN")
        self.assertEqual(_rule5_findings(output, "DQ-167"), [])


class UnrelatedAndPinGuardTest(unittest.TestCase):
    """Seat L's position stands: the unrelated matter with
    no repetition warns, and the pin guards hold."""

    def test_unrelated_matter_no_repetition_still_warns(self):
        _model, output = h.run_pipeline(
            UNRELATED_NO_REPETITION, name="probe.md")
        found = _landing_warnings(output, "DQ-959")
        self.assertEqual(len(found), 1)
        self.assertEqual(h.finding_severity(found[0]), "Warning")

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


if __name__ == "__main__":
    unittest.main()
