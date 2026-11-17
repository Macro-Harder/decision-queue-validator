"""Restart Step 16 fix wave, Fix seat D tests.

Seat D owns the corpus disposition for three fixture findings
at design/steps/step-16r-audit1-17.md, charged at design/steps/
step-16r-record.md section 6. Each test pins the specified
behaviour, written before the cure:

A17-F1 (High, WV-10): a tail form entry whose single paragraph
states banked awaiting the named decider in its closing sentence
carries a Banked element under brief PIN-01 form 4 and the
extraction rule, and derives Open under PIN-03. The whole WV-10
fixture therefore derives Open 172, no Ambiguous entry, no
findings, exit 0.

A17-F2 (Medium, WV-6): the Settlement label on a Settled entry
is a recorded label form of the settlement family, and its
matter is the ruling text of that entry for the PIN-08 ruling
text test, which runs over all recorded label forms. DQ-002
therefore raises no ruling text Error, and WV-6 exits 0 with
no findings.

A17-F3 (Medium, WV-7): the tail entry DQ-502 derives Open
under the whole body governing rule at Q-6 and PIN-11, the
later banked element governing over the heading element, so
no presence finding stands on it; and each unmatched heading
takes a Warning finding with rule identifier PIN-06 under
brief section 5.4, not a finding under check 5.
"""

import unittest

import dqv_harness as h


class Wv10TailBankedTest(unittest.TestCase):
    """A17-F1: stands banked awaiting the named decider is an
    explicit statement of remaining open in the tail form."""

    def test_wv10_entries_all_open(self):
        _model, output = h.cached_pipeline("WV-10")
        entries = h.entries_of(output)
        self.assertEqual(len(entries), 172)
        states = [h.entry_state(entry) for entry in entries]
        self.assertEqual(states, ["Open"] * 172)

    def test_wv10_no_findings_and_exit_zero(self):
        self.assertEqual(h.findings_of(h.cached_pipeline("WV-10")[1]), [])
        code, _out, _err = h.run_cli(
            "validate", h.corpus_path("WV-10"))
        self.assertEqual(code, 0)
        code, _out, _err = h.run_cli(
            "render", h.corpus_path("WV-10"))
        self.assertEqual(code, 0)


class Wv6SettlementTextTest(unittest.TestCase):
    """A17-F2: a Settlement label satisfies the ruling text
    test for a Settled entry."""

    def test_wv6_no_findings(self):
        _model, output = h.cached_pipeline("WV-6")
        self.assertEqual(h.findings_of(output), [])

    def test_wv6_exit_zero(self):
        code, _out, _err = h.run_cli(
            "validate", h.corpus_path("WV-6"))
        self.assertEqual(code, 0)


class Wv7TailAndUnmatchedTest(unittest.TestCase):
    """A17-F3: DQ-502 derives Open, and the two unmatched
    headings carry PIN-06 Warnings."""

    def test_dq502_open_with_no_presence_findings(self):
        _model, output = h.cached_pipeline("WV-7")
        entry = h.entry_by_id(output, "DQ-502")
        self.assertIsNotNone(entry)
        self.assertEqual(h.entry_state(entry), "Open")
        self.assertEqual(h.findings_for(output, entry_id="DQ-502"), [])

    def test_unmatched_headings_carry_pin06(self):
        _model, output = h.cached_pipeline("WV-7")
        pin06 = [finding for finding in h.findings_of(output)
                 if h.get(finding, "rule_id") == "PIN-06"]
        self.assertEqual(len(pin06), 2)
        for finding in pin06:
            self.assertEqual(h.finding_severity(finding), "Warning")

    def test_wv7_findings_are_exactly_the_manifest_set(self):
        _model, output = h.cached_pipeline("WV-7")
        findings = h.findings_of(output)
        self.assertEqual(len(findings), 3)
        errors = [f for f in findings
                  if h.finding_severity(f) == "Error"]
        self.assertEqual(len(errors), 1)
        code, _out, _err = h.run_cli(
            "validate", h.corpus_path("WV-7"))
        self.assertEqual(code, 1)

    def test_wv7_cli_names_pin06(self):
        _code, out, _err = h.run_cli(
            "validate", h.corpus_path("WV-7"))
        self.assertIn(b"PIN-06", out)


if __name__ == "__main__":
    unittest.main()
