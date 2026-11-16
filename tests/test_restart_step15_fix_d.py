"""Restart Step 15 fix wave 2, Fix seat D tests.

Each test pins the differing form of one charged item in the
derivation layer, validate.py, as confirmation round 2 states
it: fresh finding CF-1 (the DQ entry count and the unnumbered
entry count testing identifier presence alone, so the named
unnumbered entry in the D-06 form counts as a DQ entry), the
validate limb of the A1-F6 residue (the unclassified flag
attached dynamically on every built verbatim appendix row,
outside the declared shape), and the WV-1 component footing
verification charged to this seat. Items: CF-1, completing the
standing parts of NF-2 and D-20 on the same root; the A1-F6
validate limb; the WV-1 verification.
"""

import unittest
from pathlib import Path

import dqv_harness as h

HEADER = "# Decision Queue\n\n## Open items\n\n"
CORPUS_DIR = Path(__file__).resolve().parent / "fixtures" / (
    "decision_queue_corpus")
R7_HEADING_TEXT = "R-7 closure conflict"


def run_text(text):
    model, output = h.run_pipeline(text.encode("utf-8"))
    if output is None:
        raise AssertionError("pipeline returned the failure result")
    return model, output


def run_fixture(fixture_id):
    data = (CORPUS_DIR / (fixture_id + ".md")).read_bytes()
    model, output = h.run_pipeline(data, name=fixture_id + ".md")
    if output is None:
        raise AssertionError("pipeline returned the failure result")
    return model, output


def open_entry(number, status_line="Banked"):
    return (
        "### DQ-%03d: Synthetic entry %d\n\n"
        "Status: %s\n\n"
        "A plain paragraph stands in this entry.\n\n"
        "Owner of record: Decision-queue Clerk\n\n"
        "Question: A synthetic question for entry %d?\n\n"
        "Options: Option one. Option two.\n\n"
        "Cost: Low.\n\n"
        "Blocks: Nothing.\n"
    ) % (number, number, status_line, number)


def r7_entry():
    return (
        "## Ruled record\n\n"
        "### R-7 closure conflict\n\n"
        "Status: RULED, closed\n\n"
        "Ruled by: Captain JP\n\n"
        "Ruling text: \"The synthetic ruling stands.\"\n")


def component_holds(recon, wanted):
    components = h.as_list(h.get(recon, "components",
                                 "component_results"))
    for component in components:
        if str(h.get(component, "name", "component")) == wanted:
            return bool(h.get(component, "holds"))
    raise AssertionError("no component named " + wanted)


def failed_texts(recon):
    check = h.get(recon, "self_check", "self_check_result")
    return [str(x) for x in h.as_list(
        h.get(check, "failed_components", "failures"))]


class Cf1NamedUnnumberedCountingTest(unittest.TestCase):
    """CF-1: the counts distinguish a DQ numbered entry, whose
    identifier is a DQNumber, from a named unnumbered entry,
    whose identifier is the literal heading text in the D-06
    form. Identifier presence alone distinguishes neither."""

    def test_identifier_forms_stand_distinguished_on_the_model(self):
        model, output = run_text(
            HEADER + open_entry(1) + "\n" + r7_entry())
        dq_type = h.find_type("DQNumber")
        self.assertIsNotNone(dq_type)
        forms = []
        for entry in h.as_list(h.get(model, "entries")):
            identifier = h.get(entry, "identifier")
            forms.append((identifier, isinstance(identifier, dq_type)))
        numbered = [f for f in forms if f[1]]
        named = [f for f in forms if not f[1]]
        self.assertEqual(len(numbered), 1)
        self.assertEqual(len(named), 1)
        self.assertEqual(str(named[0][0]), R7_HEADING_TEXT)

    def test_synthetic_r7_construction_counts(self):
        # Two headed entries carry the one DQ number, so a
        # duplicate number finding stands to be read back: the
        # findings list standing non empty proves it was not
        # withheld by a false population footing failure.
        model, output = run_text(
            HEADER + open_entry(1) + "\n" + open_entry(1) + "\n"
            + r7_entry())
        recon = h.reconciliation_of(output)
        self.assertEqual(h.int_of(h.get(recon, "entry_total")), 3)
        self.assertEqual(h.get(recon, "dq_entry_count"), 2)
        self.assertEqual(h.get(recon, "unnumbered_entry_count"), 1)
        self.assertTrue(component_holds(recon, "population footing"))
        check = h.get(recon, "self_check", "self_check_result")
        self.assertTrue(h.get(check, "sums_agree"))
        duplicates = [f for f in h.findings_of(output)
                      if h.finding_rule_number(f) == 1
                      and h.finding_severity(f) == "Error"]
        self.assertTrue(duplicates)

    def test_pin_counts_stand_at_the_ledger_figures(self):
        # The pin carries 171 DQ numbered entries and the one
        # named unnumbered entry in the R-7 form, 172 headed
        # entries in all. The DQ total stands against the File
        # number ledger at 171, the unnumbered count at 1,
        # population footing passes, and the findings list is
        # not withheld.
        model, output = run_fixture("PIN")
        recon = h.reconciliation_of(output)
        self.assertEqual(h.int_of(h.get(recon, "entry_total")), 172)
        self.assertEqual(h.get(recon, "dq_entry_count"), 171)
        self.assertEqual(h.get(recon, "unnumbered_entry_count"), 1)
        self.assertTrue(component_holds(recon, "population footing"))
        check = h.get(recon, "self_check", "self_check_result")
        self.assertTrue(h.get(check, "sums_agree"))
        self.assertTrue(h.findings_of(output))


class A1F6ValidateLimbTest(unittest.TestCase):
    """A1-F6, validate limb: no built verbatim appendix row
    carries the unclassified flag as a dynamically attached
    attribute. The declared VerbatimAppendixRow shape carries
    no such field, so no built row carries the attribute at
    all, for a phrasing inside the vocabulary mapping or for
    one outside it."""

    def test_built_rows_carry_no_unclassified_attribute(self):
        model, output = run_text(
            HEADER + open_entry(1, "Wombled") + "\n" + open_entry(2))
        rows = h.as_list(h.get(output, "verbatim_appendix_rows",
                               "verbatim_appendix"))
        self.assertTrue(rows)
        phrasings = [str(h.get(row, "phrasing")) for row in rows]
        self.assertIn("Wombled", phrasings)
        self.assertIn("Banked", phrasings)
        for row in rows:
            self.assertFalse(
                hasattr(row, "unclassified"),
                "row for %r carries the undeclared attribute"
                % (h.get(row, "phrasing"),))


class Wv1ComponentFootingVerificationTest(unittest.TestCase):
    """WV-1 verification, as charged: after the CF-1 cure the
    WV-1 population footing position and the WV-1 component
    footing position stand read separately, so the paper can
    rule whether the one cure carries the other."""

    def test_wv1_population_and_component_positions(self):
        model, output = run_fixture("WV-1")
        recon = h.reconciliation_of(output)
        self.assertEqual(h.get(recon, "dq_entry_count"), 171)
        self.assertEqual(h.get(recon, "unnumbered_entry_count"), 1)
        self.assertTrue(component_holds(recon, "population footing"))
        self.assertFalse(component_holds(recon, "component footing"))
        banked = [text for text in failed_texts(recon)
                  if "Banked head evidence groups" in text]
        self.assertEqual(len(banked), 1)
        self.assertIn("sum to 151", banked[0])
        self.assertIn("population of 153", banked[0])


if __name__ == "__main__":
    unittest.main()
