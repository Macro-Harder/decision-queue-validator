"""Restart Step 16 fix wave 2, Fix seat F tests.

Seat F owns the corpus disposition for six findings of
Auditor 12, confirmation round 2 (design/steps/
step-16r-audit2-12.md section 4), plus the confirmation only
item A12-F5. Each test pins the specified behaviour, written
before the cure:

A12-F1 (Medium, F-15): a decided entry in the tail single
paragraph form takes no presence finding. The form carries no
line start Status line and no field of any form, and the
evidence forms the four presence tests of PIN-08 test for are
forms that dialect does not carry, so the absence is the
normal condition of the dialect under the PIN-13 class rule,
as Fix seat D held for the open entry field tests on the same
form. F-15 therefore carries no finding, the PIN-11 unmatched
heading word treatment stands in the census with DQ-903
named, and the fixture exits 0.

A12-F2 (Medium, F-16): the same ruling on the same form.
F-16 carries no finding and exits 0.

A12-F3 (Medium, WV-8 truncation): the partial entry takes the
unparsed marker under the trigger rule at brief section 5.5,
because the file ends inside its body with its last body line
cut off with no line ending, and its heading carries no
determining element under PIN-05, so no body element saves
it. The run reports headed 2, unparsed 1, Open 1 for the
surviving whole entry, at exit 4 on the unparsed reason
class, and not in the tool fault form: an unparsed entry
stands in no Banked head census population and no crosswalk
population, because it carries no derived state.

A12-F4 (Low, F-03): manifest side. The post Status addition
paragraph is a span fixed by label reattachment under
testing pin down 6, one Warning for the span, so the product
behaviour stands and the manifest expectation is restated:
one Warning of the label reattachment class on DQ-001 and
exit 1.

A12-F6 (Low, PIN and WV-2): the status occurrence total is
253, variant 2, line start 233, embedded 18, under PIN-14
and derivation D-13-2. A terminal Status sentence in the
landing record form, Status: landed in followed by a list
of places, is no status bearing element under PIN-01 form
4, but its marker standing inside a line is an embedded
occurrence for the appendix count, at DQ-168 and DQ-169.

A12-F7 (Low, WV-2): the finding set by rule and entry
matches the true pin run outside the exempt label
reattachment class. A level 2 entry heading does not end
the section a section introduction heads, in the parse
recognition scan or in the validate section count, and the
section introduction count finding stands on the
introduction unit itself, a file level unit, on both files.

A12-F5 (Low, WV-9): confirmation only, no cure. The fixture
behaviour stands as Auditor 12 recorded it: headed 3, Open
3, no findings of any grade, exit 0. The item stands in the
WV-9 territory whose printing decision is the Manager's.
"""

import re
import unittest

import dqv_harness as h


def _normalise_entry_id(entry_id):
    if entry_id is None:
        return None
    return re.sub(r"line \d+", "line N", str(entry_id))


def _finding_keys(output):
    keys = []
    for finding in h.findings_of(output):
        keys.append((
            str(h.get(finding, "rule_id")),
            h.finding_severity(finding),
            _normalise_entry_id(h.finding_entry_id(finding)),
        ))
    return sorted(keys)


def _occurrence_kinds(output):
    recon = h.reconciliation_of(output)
    by_kind = h.get(recon, "status_occurrences_by_kind",
                    "occurrences_by_kind") or {}
    total = h.get(recon, "status_occurrence_total",
                  "occurrence_total")
    return by_kind, total


def _embedded_count(model, entry_id):
    entry = h.entry_by_id(model, entry_id)
    count = 0
    for element in h.as_list(h.get(entry, "status_elements")):
        if h.get(element, "occurrence_kind") == "embedded":
            count += 1
    for element in h.as_list(
            h.get(entry, "occurrence_only_elements")):
        if h.get(element, "occurrence_kind") == "embedded":
            count += 1
    return count


class F15TailPresenceTest(unittest.TestCase):
    """A12-F1: no presence finding stands on a decided entry
    in the tail single paragraph form."""

    def test_f15_states_match_manifest(self):
        _model, output = h.cached_pipeline("F-15")
        entries = h.entries_of(output)
        self.assertEqual(
            [h.entry_state(entry) for entry in entries],
            ["Ruled", "Settled", "Closed as decided", "Open"])

    def test_f15_no_findings_and_pin11_census_note(self):
        _model, output = h.cached_pipeline("F-15")
        self.assertEqual(h.findings_of(output), [])
        census = h.census_of(output)
        note = h.census_class(census, "unmatched", "heading")
        if note is None:
            note = h.census_class(census, "unclassified")
        self.assertIsNotNone(note)
        self.assertIn("DQ-903", h.census_members(note))

    def test_f15_exit_zero(self):
        code, _out, _err = h.run_cli(
            "validate", h.corpus_path("F-15"))
        self.assertEqual(code, 0)
        code, _out, _err = h.run_cli(
            "render", h.corpus_path("F-15"))
        self.assertEqual(code, 0)


class F16TailPresenceTest(unittest.TestCase):
    """A12-F2: no presence finding stands on F-16."""

    def test_f16_states_match_manifest(self):
        _model, output = h.cached_pipeline("F-16")
        entries = h.entries_of(output)
        self.assertEqual(
            [h.entry_state(entry) for entry in entries],
            ["Ruled", "Settled", "Open"])

    def test_f16_no_findings_and_exit_zero(self):
        _model, output = h.cached_pipeline("F-16")
        self.assertEqual(h.findings_of(output), [])
        code, _out, _err = h.run_cli(
            "validate", h.corpus_path("F-16"))
        self.assertEqual(code, 0)
        code, _out, _err = h.run_cli(
            "render", h.corpus_path("F-16"))
        self.assertEqual(code, 0)


class Wv8TruncationTest(unittest.TestCase):
    """A12-F3: the partial entry takes the unparsed marker
    and the run reports it, in the unparsed report form."""

    def test_partial_entry_unparsed_and_whole_entry_open(self):
        _model, output = h.cached_pipeline("WV-8-truncation")
        whole = h.entry_by_id(output, "DQ-001")
        partial = h.entry_by_id(output, "DQ-002")
        self.assertEqual(h.entry_state(whole), "Open")
        self.assertTrue(h.get(partial, "unparsed", "unparsed_flag"))
        self.assertEqual(h.unparsed_count(output), 1)
        self.assertEqual(h.entry_total(output), 2)

    def test_no_tool_fault_and_exit_four(self):
        _model, output = h.cached_pipeline("WV-8-truncation")
        recon = h.reconciliation_of(output)
        result = h.get(recon, "self_check_result", "self_check")
        self.assertTrue(h.get(result, "sums_agree"))
        code, out, _err = h.run_cli(
            "validate", h.corpus_path("WV-8-truncation"))
        self.assertEqual(code, 4)
        self.assertNotIn(b"tool inconsistency", out.lower())
        self.assertNotIn(b"summary withheld", out.lower())
        self.assertIn(b"unparsed", out.lower())

    def test_no_state_asserted_for_partial_entry(self):
        _model, output = h.cached_pipeline("WV-8-truncation")
        counts = h.canonical_counts(output)
        self.assertEqual(counts.get("Open"), 1)
        for finding in h.findings_for(output, entry_id="DQ-002"):
            statement = (h.finding_statement(finding) or "").lower()
            self.assertIn("unparsed", statement)


class F03ManifestRestatementTest(unittest.TestCase):
    """A12-F4: the product behaviour stands, one rule 6
    Warning for the reattached post Status addition span,
    and the manifest records it."""

    def test_f03_product_behaviour_one_reattachment_warning(self):
        _model, output = h.cached_pipeline("F-03")
        findings = h.findings_of(output)
        self.assertEqual(len(findings), 1)
        finding = findings[0]
        self.assertEqual(h.finding_rule_number(finding), 6)
        self.assertEqual(h.finding_severity(finding), "Warning")
        self.assertEqual(h.finding_entry_id(finding), "DQ-001")
        code, _out, _err = h.run_cli(
            "validate", h.corpus_path("F-03"))
        self.assertEqual(code, 1)

    def test_f03_manifest_records_the_warning_and_exit_one(self):
        entry = h.manifest_entry("F-03")
        findings_text = str(entry["expected_findings"]).lower()
        self.assertIn("warning", findings_text)
        self.assertIn("reattachment", findings_text)
        self.assertEqual(h.expected_exit("F-03"), 1)


class StatusOccurrenceTotalTest(unittest.TestCase):
    """A12-F6: the occurrence total is 253, embedded 18, on
    the pin and on its reversal alike."""

    def test_pin_occurrence_total_and_kinds(self):
        _model, output = h.cached_pipeline("PIN")
        by_kind, total = _occurrence_kinds(output)
        self.assertEqual(total, 253)
        self.assertEqual(by_kind.get("variant"), 2)
        self.assertEqual(by_kind.get("line start"), 233)
        self.assertEqual(by_kind.get("embedded"), 18)

    def test_wv2_occurrence_total_and_kinds(self):
        _model, output = h.cached_pipeline("WV-2")
        by_kind, total = _occurrence_kinds(output)
        self.assertEqual(total, 253)
        self.assertEqual(by_kind.get("variant"), 2)
        self.assertEqual(by_kind.get("line start"), 233)
        self.assertEqual(by_kind.get("embedded"), 18)

    def test_landing_record_occurrences_counted_embedded(self):
        model, _output = h.cached_pipeline("PIN")
        self.assertEqual(_embedded_count(model, "DQ-168"), 1)
        self.assertEqual(_embedded_count(model, "DQ-169"), 1)


class Wv2FindingSetTest(unittest.TestCase):
    """A12-F7: outside the exempt label reattachment class,
    the WV-2 finding set by rule, severity, and entry
    matches the true pin run."""

    def test_finding_sets_match_outside_reattachment(self):
        _m1, pin_output = h.cached_pipeline("PIN")
        _m2, wv2_output = h.cached_pipeline("WV-2")
        pin_keys = [key for key in _finding_keys(pin_output)
                    if key[0] != "6"]
        wv2_keys = [key for key in _finding_keys(wv2_output)
                    if key[0] != "6"]
        self.assertEqual(wv2_keys, pin_keys)

    def test_pin06_count_matches(self):
        _m1, pin_output = h.cached_pipeline("PIN")
        _m2, wv2_output = h.cached_pipeline("WV-2")
        pin06_pin = [f for f in h.findings_of(pin_output)
                     if str(h.get(f, "rule_id")) == "PIN-06"]
        pin06_wv2 = [f for f in h.findings_of(wv2_output)
                     if str(h.get(f, "rule_id")) == "PIN-06"]
        self.assertEqual(len(pin06_wv2), len(pin06_pin))
        self.assertEqual(len(pin06_wv2), 4)

    def test_section_introduction_count_statement_matches(self):
        statements = {}
        for fixture_id in ("PIN", "WV-2"):
            _model, output = h.cached_pipeline(fixture_id)
            found = []
            for finding in h.findings_of(output):
                statement = h.finding_statement(finding) or ""
                if "section introduction states" in statement:
                    found.append(statement)
            statements[fixture_id] = found
        self.assertEqual(len(statements["PIN"]), 1)
        self.assertEqual(statements["WV-2"], statements["PIN"])


class Wv9ConfirmationTest(unittest.TestCase):
    """A12-F5: confirmation only. The fixture behaviour
    stands as Auditor 12 recorded it, and no cure stands in
    this seat for it: the WV-9 printing decision is the
    Manager's."""

    def test_wv9_behaviour_stands_as_recorded(self):
        _model, output = h.cached_pipeline("WV-9")
        entries = h.entries_of(output)
        self.assertEqual(len(entries), 3)
        self.assertEqual(
            [h.entry_state(entry) for entry in entries],
            ["Open", "Open", "Open"])
        self.assertEqual(h.findings_of(output), [])
        code, _out, _err = h.run_cli(
            "validate", h.corpus_path("WV-9"))
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
