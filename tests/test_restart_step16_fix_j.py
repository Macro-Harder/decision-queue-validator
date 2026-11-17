"""Restart Step 16 fix wave 3, Fix seat J tests.

Seat J owns two faces of one wave 2 regression:

A3-12-1 (High, Auditor 12 of confirmation round 3): a queue
file whose final line has no line feed terminator loses its
last entry. Three byte forms are pinned, each built from the
plain 138 byte base whose validate run exits 1 with its one
entry counted Open: the plain bytes with the final line feed
removed (137 bytes, digest 55f7dfc0df86), the carriage return
form ending in a lone carriage return (144 bytes, digest
80c333155308), and the line feed bytes with a lone carriage
return closing the final line (138 bytes, digest
b9ffba9abdf1). Under the terminator rule stated in parse.py
itself, a final line with no terminator is a line, so each
form reports exactly as the plain form: no unparsed entry,
no rule 12 finding, the entry counted, exit 1.

A3-8-F1 (Medium, Auditor 8 of confirmation round 3): the
cut off Status edge form, a file ending on an entry complete
Status: Open line with no line ending, stands parsed with
its Open state standing and exit 1, as rounds 1 and 2
verified. The exception in the brief Entry shape at section
5.5 and in PIN-05, and in the plan at Item 3, runs where a
determining element is extracted from any element of the
entry, heading or other.

Both cures must hold at once with the wave 2 form they
regressed against: the WV-8 truncation fixture, whose
partial entry is cut off mid sentence in a later paragraph
(its last body line ends mid word with no sentence close),
still takes its pinned unparsed report at exit 4, and the
no element cut off prose form still takes the marker. The
seat F cures also stand pinned here: WV-8 in its report
form, F-15 and F-16 clean at exit 0, the status occurrence
total at 253 on the pin and on WV-2, and the WV-2 finding
set matching the pin outside the exempt reattachment class.
"""

import re
import unittest

import dqv_harness as h


PLAIN = (b"# Decision queue\n\n"
         b"### DQ-001: A sample open question\n\n"
         b"Status: Banked\n\n"
         b"This entry is waiting for a decision and carries a "
         b"plain paragraph.\n")

CUTOFF_STATUS = (b"# Decision queue\n\n"
                 b"### DQ-001: Complete entry first\n\n"
                 b"Status: Open\n\n"
                 b"A plain paragraph of body text for the first "
                 b"entry.\n\n"
                 b"### DQ-002: Cut off entry with status\n\n"
                 b"Status: Open")

CUTOFF_NO_ELEMENT = (b"# Decision queue\n\n"
                     b"### DQ-001: Complete entry first\n\n"
                     b"Status: Open\n\n"
                     b"A plain paragraph of body text for the "
                     b"first entry.\n\n"
                     b"### DQ-002: Cut off entry\n\n"
                     b"Some body text that ends with no line ending")


def _cli(data, subcommand="validate"):
    path = h.temp_input(data, name="fix_j_probe.md")
    return h.run_cli(subcommand, path)


def _rule12(output):
    return [finding for finding in h.findings_of(output)
            if h.finding_rule_number(finding) == 12]


class TerminatorFormsTest(unittest.TestCase):
    """A3-12-1: a missing final line feed terminator alone
    takes no entry. The three probed byte forms report as
    the plain form reports."""

    def _assert_as_plain(self, data):
        model, output = h.run_pipeline(data, name="probe.md")
        self.assertIsNotNone(output)
        entry = h.entry_by_id(model, "DQ-001")
        self.assertFalse(bool(h.get(entry, "unparsed")))
        self.assertEqual(h.unparsed_count(output), 0)
        self.assertEqual(_rule12(output), [])
        self.assertEqual(h.canonical_counts(output).get("Open"), 1)
        result = h.entry_by_id(output, "DQ-001")
        self.assertEqual(h.entry_state(result), "Open")
        for subcommand in ("validate", "render"):
            code, _out, _err = _cli(data, subcommand)
            self.assertEqual(code, 1)

    def test_plain_form_baseline(self):
        self.assertEqual(len(PLAIN), 138)
        self._assert_as_plain(PLAIN)

    def test_final_line_feed_removed(self):
        data = PLAIN[:-1]
        self.assertEqual(len(data), 137)
        self.assertEqual(h.sha256_hex(data)[:12], "55f7dfc0df86")
        self._assert_as_plain(data)

    def test_crlf_form_ending_in_lone_carriage_return(self):
        data = PLAIN.replace(b"\n", b"\r\n")[:-2] + b"\r"
        self.assertEqual(len(data), 144)
        self.assertEqual(h.sha256_hex(data)[:12], "80c333155308")
        self._assert_as_plain(data)

    def test_lone_carriage_return_closing_final_line(self):
        data = PLAIN[:-1] + b"\r"
        self.assertEqual(len(data), 138)
        self.assertEqual(h.sha256_hex(data)[:12], "b9ffba9abdf1")
        self._assert_as_plain(data)


class CutOffStatusFormTest(unittest.TestCase):
    """A3-8-F1: a file ending on a complete Status line with
    no line ending stands parsed, its state standing."""

    def test_cutoff_status_entry_parsed_open(self):
        model, output = h.run_pipeline(CUTOFF_STATUS,
                                       name="probe.md")
        self.assertIsNotNone(output)
        entry = h.entry_by_id(model, "DQ-002")
        self.assertFalse(bool(h.get(entry, "unparsed")))
        self.assertEqual(h.unparsed_count(output), 0)
        result = h.entry_by_id(output, "DQ-002")
        self.assertEqual(h.entry_state(result), "Open")
        self.assertEqual(h.canonical_counts(output).get("Open"), 2)

    def test_cutoff_status_exit_one_both_subcommands(self):
        for subcommand in ("validate", "render"):
            code, _out, _err = _cli(CUTOFF_STATUS, subcommand)
            self.assertEqual(code, 1)


class CutOffFormsStillUnparsedTest(unittest.TestCase):
    """The forms the marker exists for still take it: a last
    body line cut off in its own form, mid sentence, takes
    the marker whether or not an earlier element stands."""

    def test_no_element_cutoff_prose_unparsed(self):
        model, output = h.run_pipeline(CUTOFF_NO_ELEMENT,
                                       name="probe.md")
        entry = h.entry_by_id(model, "DQ-002")
        self.assertTrue(bool(h.get(entry, "unparsed")))
        self.assertEqual(h.unparsed_count(output), 1)
        code, _out, _err = _cli(CUTOFF_NO_ELEMENT)
        self.assertEqual(code, 4)

    def test_wv8_truncation_pinned_unparsed_report(self):
        _model, output = h.cached_pipeline("WV-8-truncation")
        whole = h.entry_by_id(output, "DQ-001")
        partial = h.entry_by_id(output, "DQ-002")
        self.assertEqual(h.entry_state(whole), "Open")
        self.assertTrue(h.get(partial, "unparsed", "unparsed_flag"))
        self.assertEqual(h.unparsed_count(output), 1)
        self.assertEqual(h.entry_total(output), 2)
        self.assertEqual(h.canonical_counts(output).get("Open"), 1)
        for finding in h.findings_for(output, entry_id="DQ-002"):
            statement = (h.finding_statement(finding) or "").lower()
            self.assertIn("unparsed", statement)
        recon = h.reconciliation_of(output)
        result = h.get(recon, "self_check_result", "self_check")
        self.assertTrue(h.get(result, "sums_agree"))
        code, out, _err = h.run_cli(
            "validate", h.corpus_path("WV-8-truncation"))
        self.assertEqual(code, 4)
        self.assertNotIn(b"tool inconsistency", out.lower())
        self.assertNotIn(b"summary withheld", out.lower())


class SeatFCuresIntactTest(unittest.TestCase):
    """The wave 2 cures of fix seat F stand after this cure."""

    def test_f15_and_f16_clean(self):
        for fixture_id, states in (
                ("F-15", ["Ruled", "Settled", "Closed as decided",
                          "Open"]),
                ("F-16", ["Ruled", "Settled", "Open"])):
            _model, output = h.cached_pipeline(fixture_id)
            self.assertEqual(h.findings_of(output), [])
            self.assertEqual(
                [h.entry_state(entry)
                 for entry in h.entries_of(output)], states)
            code, _out, _err = h.run_cli(
                "validate", h.corpus_path(fixture_id))
            self.assertEqual(code, 0)

    def test_occurrence_totals_stay_253(self):
        for fixture_id in ("PIN", "WV-2"):
            _model, output = h.cached_pipeline(fixture_id)
            recon = h.reconciliation_of(output)
            by_kind = h.get(recon, "status_occurrences_by_kind",
                            "occurrences_by_kind") or {}
            total = h.get(recon, "status_occurrence_total",
                          "occurrence_total")
            self.assertEqual(total, 253)
            self.assertEqual(by_kind.get("variant"), 2)
            self.assertEqual(by_kind.get("line start"), 233)
            self.assertEqual(by_kind.get("embedded"), 18)

    def test_wv2_finding_set_still_matches(self):
        def keys(output):
            found = []
            for finding in h.findings_of(output):
                entry_id = h.finding_entry_id(finding)
                if entry_id is not None:
                    entry_id = re.sub(r"line \d+", "line N",
                                      str(entry_id))
                found.append((str(h.get(finding, "rule_id")),
                              h.finding_severity(finding),
                              entry_id))
            return sorted(found)
        _m1, pin_output = h.cached_pipeline("PIN")
        _m2, wv2_output = h.cached_pipeline("WV-2")
        pin_keys = [key for key in keys(pin_output)
                    if key[0] != "6"]
        wv2_keys = [key for key in keys(wv2_output)
                    if key[0] != "6"]
        self.assertEqual(wv2_keys, pin_keys)


if __name__ == "__main__":
    unittest.main()
