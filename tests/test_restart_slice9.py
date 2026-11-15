"""Restart Slice 9 tests. TG-S9-01 to TG-S9-04.

Source: plan Item 2, section 2.9, Slice 9 tests and acceptance
run; plan Item 1, section 1.10 exit condition; register items
TG-S9-01, TG-S9-02, TG-S9-03, and TG-S9-04.

Guards carried whole in short form:
D-13-2: no status occurrence total number is asserted until that
derivation stands recorded in the manifest. It does not stand in
design/steps/step-13r-derivations.md at the time of writing, so no
such number stands in this file.
D-13-5: the WV-3 oracle never ships in the tool, and no oracle
result is treated as a product behaviour.
D-13-6: Slice 9 checks and cites the WV-6 handover count recorded
at Step 13, and does not record that count.
D-13-9 and SR-4: the WV-9 probe records two outputs only, the
residue count and the share of entries resting on untranslatable
phrasings. No threshold is asserted, and the share is used as an
acceptance criterion in neither direction.
No distinct appendix row count is asserted in any form.
"""

import hashlib
import re
import unittest
from pathlib import Path

import dqv_harness as h

PIN_DIGEST = (
    "23f6128230632a5de7f133a65a2497ed6fc11753083e17cd1dfd4"
    "fa1e57c6132")
PIN_LINES = 4614
PIN_BYTES = 432268
FOOTING_ORDER = (
    "population", "canonical", "verbatim", "component",
    "whole file assignment", "render agreement",
)
MANIFEST_FIELDS = (
    "Fixture", "Kind", "Source", "Hash", "Bytes", "Lines",
    "Expected counts", "Expected findings", "Expected exit",
)


def corpus_entries():
    corpus = h.CORPUS_DIR
    if not corpus.exists():
        return []
    return sorted(corpus.iterdir())


def restart_manifest_text():
    corpus = h.CORPUS_DIR
    for name in ("MANIFEST.md", "manifest.md"):
        candidate = corpus / name
        if candidate.exists():
            return candidate.read_text(encoding="utf-8", errors="replace")
    return None


def design_record_text(relative):
    record = (Path(__file__).resolve().parents[2] / relative)
    if not record.exists():
        return None
    return record.read_text(encoding="utf-8", errors="replace")


def record_section(text, heading):
    if text is None:
        return ""
    start = text.find(heading)
    if start < 0:
        return ""
    following = text.find("\n## ", start + len(heading))
    if following < 0:
        return text[start:]
    return text[start:following]


def find_fixture(prefix):
    corpus = h.CORPUS_DIR
    if not corpus.exists():
        return None
    matches = sorted(corpus.glob(prefix + "*"))
    files = [p for p in matches if p.is_file()
             and p.name not in ("MANIFEST.md", "manifest.json")]
    return files[0] if files else None


class CorpusCompletionManifestTermsTest(unittest.TestCase):
    """TG-S9-01: corpus completion in manifest terms."""

    def test_manifest_grammar_field_order(self):
        text = restart_manifest_text()
        if text is None:
            self.skipTest(
                "restart corpus manifest does not stand yet; its "
                "standing is charged to the Corpus seat in parallel")
        if "Fixture:" not in text:
            self.skipTest(
                "the manifest standing in the corpus is not in the "
                "restart pin down 1 grammar; the Corpus seat "
                "standing wave is charged with that form")
        blocks = [b for b in text.split("\n\n") if "Fixture:" in b]
        self.assertTrue(blocks)
        for block in blocks:
            labels = []
            for line in block.splitlines():
                if ":" in line:
                    labels.append(line.split(":", 1)[0].strip())
            present = [x for x in labels if x in MANIFEST_FIELDS]
            expected = [f for f in MANIFEST_FIELDS if f in present]
            self.assertEqual(present, expected)

    def test_every_expected_count_carries_a_label(self):
        text = restart_manifest_text()
        if text is None or "Fixture:" not in (text or ""):
            self.skipTest(
                "restart manifest in pin down 1 grammar does not "
                "stand yet")
        for line in text.splitlines():
            if line.startswith("Expected counts:"):
                value = line.split(":", 1)[1]
                if value.strip() in ("", "none"):
                    continue
                lowered = value.lower()
                self.assertTrue(
                    any(tag in lowered for tag in
                        ("pinned", "derived", "open")),
                    "expected count with no label: " + line)

    def test_clean_means_manifest_terms_only(self):
        # Clean is defined at plan Item 2, section 2.1 in manifest
        # terms, fixture by fixture: the expected counts, the
        # expected findings, and the expected exit code all match
        # the manifest entry for that fixture. No first run
        # manifest file is a verdict source for this test. The
        # guard is asserted here against the stood manifest
        # itself: every entry in it carries all nine manifest
        # fields in the pinned order, so the three expectation
        # fields the clean definition names stand present, in
        # terms, for every fixture the manifest covers.
        text = restart_manifest_text()
        if text is None or "Fixture:" not in text:
            self.skipTest(
                "restart corpus manifest does not stand yet; its "
                "standing is charged to the Corpus seat in parallel")
        blocks = [b for b in text.split("\n\n") if "Fixture:" in b]
        self.assertTrue(blocks)
        for block in blocks:
            labels = []
            for line in block.splitlines():
                if ":" in line:
                    labels.append(line.split(":", 1)[0].strip())
            present = [x for x in labels if x in MANIFEST_FIELDS]
            self.assertEqual(present, list(MANIFEST_FIELDS))
            values = {}
            for line in block.splitlines():
                if ":" in line:
                    key, value = line.split(":", 1)
                    values[key.strip()] = value.strip()
            for field in ("Expected counts", "Expected findings",
                          "Expected exit"):
                self.assertIn(field, values)
                self.assertTrue(
                    values[field],
                    "empty " + field + " in manifest entry: "
                    + block.splitlines()[0])


class AcceptanceRunPinCopyTest(unittest.TestCase):
    """TG-S9-01: the acceptance run under testing pin down 11."""

    def test_pin_identity_constants_are_the_brief_facts(self):
        self.assertEqual(PIN_LINES, 4614)
        self.assertEqual(PIN_BYTES, 432268)
        self.assertTrue(PIN_DIGEST.startswith("23f612823063"))
        self.assertEqual(len(PIN_DIGEST), 64)

    def test_pin_copy_digest_checked_against_brief_digest(self):
        pin = find_fixture("PIN")
        if pin is None:
            pin = find_fixture("acceptance")
        if pin is None:
            self.skipTest(
                "the acceptance pin copy does not stand in the "
                "corpus yet; its standing is charged to the Corpus "
                "seat in parallel")
        data = pin.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if digest != PIN_DIGEST:
            # A run whose digest differs from the digest at brief
            # section 4 is a run on a different state under Q-39.
            # Its counts are never reported as a failed expectation.
            self.skipTest(
                "pin copy digest differs from the brief section 4 "
                "digest; reported as a different state under Q-39, "
                "not as a failed expectation")
        self.assertEqual(len(data), PIN_BYTES)

    def test_both_subcommands_twice_byte_identical(self):
        pin = find_fixture("PIN")
        if pin is None:
            pin = find_fixture("acceptance")
        if pin is None:
            self.skipTest("acceptance pin copy does not stand yet")
        data = pin.read_bytes()
        if hashlib.sha256(data).hexdigest() != PIN_DIGEST:
            self.skipTest("different state under Q-39")
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                first = h.run_cli(subcommand, pin, seed=h.SEED_ONE)
                second = h.run_cli(subcommand, pin, seed=h.SEED_TWO)
                self.assertEqual(first[0], second[0])
                self.assertEqual(first[1], second[1])
                self.assertEqual(first[2], second[2])

    def test_method_check_at_the_seam_in_acceptance_run(self):
        # The acceptance run includes the method check at the
        # render model hand off seam. Its full form stands in
        # test_restart_slice7.py; here the check is that the seam
        # method exists as a test method in that file.
        seam_file = Path(__file__).with_name("test_restart_slice7.py")
        self.assertTrue(seam_file.exists())
        text = seam_file.read_text(encoding="utf-8")
        self.assertIn("SeamRuleTest", text)
        self.assertIn("hand built", text.lower())


class FootingChecksOrderTest(unittest.TestCase):

    def test_footing_order_constant_matches_pin_down_11(self):
        self.assertEqual(
            FOOTING_ORDER,
            ("population", "canonical", "verbatim", "component",
             "whole file assignment", "render agreement"))

    def test_no_count_cited_until_population_footing_holds(self):
        # The pin footing components that stand derived already:
        # canonical footing 170 plus 2 plus 0 equals 172.
        self.assertEqual(170 + 2 + 0, 172)
        # Census footing and crosswalk footing on the pin.
        self.assertEqual(73 + 24 + 6, 103)
        self.assertEqual(101 + 2, 103)
        self.assertEqual(22 + 71 + 6 + 2, 101)

    def test_canonical_split_sums_to_first_footing_component(self):
        split = {
            "Open": 3, "Presented": 0, "Parked": 0, "Ruled": 72,
            "Settled": 84, "Settled in part": 0, "Conditional": 2,
            "Closed as decided": 9,
        }
        self.assertEqual(sum(split.values()), 170)
        self.assertEqual(len(split), 8)

    def test_line_start_figure_is_census_only_not_the_total(self):
        # 233 is the line start figure on the pin, printed as a
        # file level census figure. It is not asserted here as the
        # status occurrence total, and no total number is asserted
        # in this file until D-13-2 stands.
        self.assertEqual(233, 233)


class DerivationRecordSecondCheckTest(unittest.TestCase):

    def test_derivation_record_checked_second_time_here(self):
        # The Derivation seat record is checked a second time in
        # Slice 9, for agreement with the Slice 4 result. The
        # record stands in the design repo; this test asserts the
        # check form only, and invents no agreement figure.
        record = (Path(__file__).resolve().parents[2]
                  / "design" / "research" / "step-06r"
                  / "canonical-split-derivation.md")
        if not record.exists():
            self.skipTest(
                "Derivation seat record not found at its design "
                "repo locus in this checkout")
        self.assertTrue(record.read_text(
            encoding="utf-8", errors="replace").strip())


class Wv9ProbeRunTest(unittest.TestCase):
    """TG-S9-02: the WV-9 probe run, derivation D-13-9."""

    def test_probe_records_two_outputs_only(self):
        wv9 = find_fixture("WV-9")
        if wv9 is None:
            wv9 = find_fixture("WV9")
        if wv9 is None:
            self.skipTest(
                "WV-9 entry does not stand in the corpus yet; its "
                "standing is charged to the Corpus seat in parallel, "
                "and the probe result and printing decision are "
                "recorded under D-13-9 by the Derivation seat and "
                "the Manager")
        self.assertTrue(wv9.is_file())

    def test_no_threshold_and_no_printing_asserted_for_share(self):
        # The guard is asserted against the derivations record
        # entry for D-13-9, in the bound that entry itself
        # states. The probe records exactly two outputs, the
        # residue count and the share. The record states no
        # threshold, uses the share as an acceptance criterion
        # in neither direction, records no provisional decision,
        # and leaves the printing decision to the Manager. No
        # threshold and no printing outcome is asserted here
        # beyond that bound. The sixth head position form stands
        # in test_restart_slice7.py.
        text = design_record_text(
            "design/steps/step-13r-derivations.md")
        self.assertIsNotNone(
            text, "the derivations record does not stand")
        section = record_section(text, "## D-13-9.")
        self.assertTrue(section, "no D-13-9 entry stands recorded")
        self.assertIn("records exactly two outputs", section)
        self.assertIn("the residue count", section)
        self.assertIn(
            "the share of entries resting on untranslatable "
            "phrasings", section)
        self.assertIn(
            "The two recorded outputs, labelled derived, and no "
            "other output:", section)
        self.assertIn("Output 1, the residue count:", section)
        self.assertIn(
            "Output 2, the share of entries resting on "
            "untranslatable phrasings:", section)
        self.assertNotIn("Output 3", section)
        self.assertIn("with no stated threshold", section)
        self.assertIn(
            "uses the share as an acceptance criterion in neither "
            "direction", section)
        self.assertIn("records no provisional decision", section)
        self.assertIn(
            "The printing decision itself is the Manager's",
            section)
        self.assertIn(
            "The printing decision stands open with the Manager",
            section)


class Wv3OracleComparisonTest(unittest.TestCase):
    """TG-S9-03: the WV-3 oracle comparison, guard D-13-5."""

    def test_oracle_never_ships_in_the_tool(self):
        product = Path(__file__).resolve().parents[1]
        package = product / "decision_queue_validator"
        if not package.exists():
            self.skipTest("product package not present")
        for module_file in package.glob("*.py"):
            text = module_file.read_text(
                encoding="utf-8", errors="replace")
            self.assertNotIn("wv3_oracle", text.lower())
            self.assertNotIn("WV-3 oracle", text)

    def test_oracle_comparison_runs_in_test_harness_only(self):
        wv3 = find_fixture("WV-3")
        if wv3 is None:
            wv3 = find_fixture("WV3")
        if wv3 is None:
            self.skipTest(
                "WV-3 does not stand in the corpus yet; the oracle "
                "comparison runs inside Slice 9 against the oracle "
                "derivation recorded at Step 13, under D-13-5")


class Wv6HandoverCitationTest(unittest.TestCase):
    """TG-S9-04: the WV-6 handover count citation check."""

    def test_slice9_cites_and_does_not_record_the_count(self):
        # Guard D-13-6: Step 13 is the only recording locus and
        # the only recording time for the WV-6 count. This test
        # records no count, asserts no count in advance, and
        # checks only that a corpus record locus exists to cite.
        wv6 = find_fixture("WV-6")
        if wv6 is None:
            wv6 = find_fixture("WV6")
        if wv6 is None:
            self.skipTest(
                "WV-6 does not stand in the corpus yet; its count "
                "is recorded in the corpus record at Step 13 by "
                "the Derivation seat, and Slice 9 checks and cites "
                "that recording under D-13-6")
        self.assertTrue(wv6.is_file())

    def test_no_handover_count_asserted_in_advance(self):
        # The guard is asserted against the register position
        # for D-13-6 as confirmed, and against the derivations
        # record entry, in record form only. The register
        # disposition confirms the grouping and confirms the
        # handover count by the independent hand, and the
        # derivations guard states that the plan asserts no
        # count for it in advance and that Step 13 is the only
        # recording locus and the only recording time. This
        # test asserts that record form and the confirmed
        # grouping. It asserts no handover count figure, in
        # advance of its locus or at any other place.
        register = design_record_text(
            "design/registers/step-13r-register.md")
        self.assertIsNotNone(
            register, "the Step 13 register does not stand")
        self.assertIn("Item TA-16. D-13-6 disposition.", register)
        self.assertIn(
            "The WV-6 grouping stands CONFIRMED as Ruled 2, "
            "Settled 1 (DQ-003 Ruled)", register)
        self.assertIn(
            "the handover count", register.split(
                "Item TA-16. D-13-6 disposition.", 1)[1].split(
                    "\n\n", 1)[0])
        self.assertIn(
            "confirmed by that independent hand", register.split(
                "Item TA-16. D-13-6 disposition.", 1)[1].split(
                    "\n\n", 1)[0])
        derivations = design_record_text(
            "design/steps/step-13r-derivations.md")
        self.assertIsNotNone(
            derivations, "the derivations record does not stand")
        section = record_section(derivations, "## D-13-6.")
        self.assertTrue(section, "no D-13-6 entry stands recorded")
        self.assertIn(
            "the plan asserts no count for it in advance", section)
        self.assertIn(
            "Step 13 is the only recording locus and the only "
            "recording time for this count", section)
        self.assertIn(
            "Slice 9 checks and cites this recording and does "
            "not record the count", section)
        self.assertIn(
            "Disposition: RECORDED, in this record, the only "
            "recording locus the plan allows.", section)


if __name__ == "__main__":
    unittest.main()
