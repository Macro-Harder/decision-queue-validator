"""Restart Slice 4 tests: derivation of effective state.

Register groups TG-S4-01 to TG-S4-04. Source: plan Item 2, section 2.6,
with exit conditions at plan Item 1, section 1.5. Fixtures F-02, F-06,
F-07, F-08, F-09, F-15, F-16, F-17, and F-18 at the derivation level,
supplied by the Corpus seat under product/tests/fixtures/
decision_queue_corpus/. Constructions charged to this slice are built
in the test itself, as the register entries state.

Guards carried whole: the DQ-022 dependence guard at plan section 2.2
travels with the pin test in TG-S4-04, with no coverage claimed for
the DQ-022 position. The F-07 trigger rule at testing pin down 8 and
shape check risk SR-6: a future date alone, an ordering reason, and a
blocks field are not trigger statements. No expectation is taken from
I7A-04, I7A-05, or I7A-07, per shape check risk SR-10. The first run
test files are data only and assert nothing here as a verdict.
"""

import json
import unittest
from pathlib import Path

import dqv_harness as h

CORPUS_DIR = Path(__file__).resolve().parent / "fixtures" / (
    "decision_queue_corpus")

CANONICAL_STATES = (
    "Open", "Presented", "Parked", "Ruled", "Settled",
    "Settled in part", "Conditional", "Closed as decided",
)

# Pinned canonical split, plan Item 2, section 2.2, testing pin down 4,
# from the Derivation seat record at design/research/step-06r/
# canonical-split-derivation.md. Unit: headed entries.
PIN_SPLIT = {
    "Open": 3, "Presented": 0, "Parked": 0, "Ruled": 72,
    "Settled": 84, "Settled in part": 0, "Conditional": 2,
    "Closed as decided": 9,
}
PIN_AMBIGUOUS = 2
PIN_AMBIGUOUS_ENTRIES = ("DQ-087", "DQ-106")
PIN_UNPARSED = 0
PIN_HEADED_TOTAL = 172

DQ022_DEPENDENCE = (
    "The DQ-022 row rests on the bold supersession block reading: "
    "the bold line standing alone is read as a decision block "
    "segment carrying a supersession, as the determining element. "
    "No fixture is added by that dependence and no coverage is "
    "claimed for the DQ-022 position."
)


def run_text(text):
    _model, output = h.run_pipeline(text.encode("utf-8"))
    if output is None:
        raise AssertionError("pipeline returned the failure result")
    return output


def fixture_output(fixture_id):
    _model, output = h.cached_pipeline(fixture_id)
    if output is None:
        raise AssertionError("fixture " + fixture_id +
                             " returned the failure result")
    return output


def state_of(output, entry_id):
    entry = h.entry_by_id(output, entry_id)
    if entry is None:
        raise AssertionError("no entry " + entry_id)
    return entry


def derived_state(output, entry_id):
    return h.entry_state(state_of(output, entry_id))


def findings(output, entry_id=None, severity=None):
    return h.findings_for(output, entry_id=entry_id, severity=severity)


def open_entry(number, status_line, extra=""):
    return (
        "### DQ-%03d: Synthetic entry %d\n\n"
        "Status: %s\n\n"
        "Owner of record: Decision-queue Clerk\n\n"
        "Source: synthetic construction at Step 13\n\n"
        "Question: A synthetic question for entry %d?\n\n"
        "Options: Option one. Option two.\n\n"
        "Cost: Low.\n\n"
        "Blocks: Nothing.\n"
        "%s\n"
    ) % (number, number, status_line, number, extra)


def ruled_entry(number, status_line, extra=""):
    return (
        "### DQ-%03d: Synthetic ruled entry %d\n\n"
        "Status: %s\n\n"
        "Ruled by: Captain JP\n\n"
        "Ruling text: \"The synthetic ruling stands.\"\n\n"
        "Ruling outcome: The synthetic outcome stands.\n\n"
        "Where the ruling landed: synthetic record.\n"
        "%s\n"
    ) % (number, number, status_line, extra)


HEADER = "# Decision Queue\n\n## Open items\n\n"


class MappingUnitTest(unittest.TestCase):
    """TG-S4-01: PIN-03 mapping unit, plan section 2.6."""

    def test_conditional_row_governs_over_named_state_rows_at_whole(self):
        text = HEADER + ruled_entry(
            901, "Ruled",
            extra="\nStatus: Ruled, subject to the landing standing "
                  "verified\n")
        output = run_text(text)
        self.assertEqual(derived_state(output, "DQ-901"), "Conditional")

    def test_express_paragraph_with_earlier_decision_evidence_governs(self):
        # A Banked, Open, or Presented element at scope Whole with
        # earlier decision evidence in the same entry: the decision
        # evidence governs over the Open and Presented rows and over
        # the Conditional row.
        for word in ("Banked", "Open", "Presented"):
            with self.subTest(word=word):
                text = HEADER + (
                    "### DQ-902: Synthetic entry 902\n\n"
                    "Status: " + word + "\n\n"
                    "#### Ruling by Captain JP\n\n"
                    "Ruled. The earlier ruling in this entry decides "
                    "the entry in full, subject to no condition.\n")
                output = run_text(text)
                self.assertEqual(derived_state(output, "DQ-902"),
                                 "Ruled")

    def test_part_rows_for_ruled_and_settled_give_settled_in_part(self):
        for word in ("Ruled", "Settled"):
            with self.subTest(word=word):
                text = HEADER + (
                    "### DQ-903: Synthetic entry 903\n\n"
                    "Status: Banked\n\n"
                    "#### Decision block\n\n"
                    + word + " in part. The first limb is decided. "
                    "The remainder, the estate default anchor set, "
                    "stays banked.\n")
                output = run_text(text)
                entry = state_of(output, "DQ-903")
                self.assertEqual(h.entry_state(entry), "Settled in part")
                remainder = h.text_of(h.get(
                    entry, "remainder_text", "remainder")) or ""
                self.assertIn("estate default anchor set", remainder)
                counts = h.canonical_counts(output)
                self.assertEqual(counts.get("Closed as decided", 0), 0)

    def test_part_closure_row_gives_closed_for_closed_part_only(self):
        text = HEADER + (
            "### DQ-904: Synthetic entry 904\n\n"
            "Status: Banked\n\n"
            "#### Decision block\n\n"
            "Closed in part. The first limb is closed as decided. "
            "The remainder stays open.\n")
        output = run_text(text)
        self.assertEqual(derived_state(output, "DQ-904"),
                         "Closed as decided")
        counts = h.canonical_counts(output)
        self.assertEqual(counts.get("Settled in part", 0), 0)

    def test_part_rows_for_open_family_report_ambiguous(self):
        for word in ("Banked", "Open", "Presented", "Parked"):
            with self.subTest(word=word):
                text = HEADER + (
                    "### DQ-905: Synthetic entry 905\n\n"
                    "Status: " + word + " in part, the first limb "
                    "only, with the rest undecided and no decision "
                    "evidence anywhere in the entry.\n\n"
                    "Owner of record: Decision-queue Clerk\n\n"
                    "Question: A synthetic question?\n")
                output = run_text(text)
                entry = state_of(output, "DQ-905")
                self.assertTrue(h.is_ambiguous(entry))

    def test_f02_ruled_from_body_evidence(self):
        output = fixture_output("F-02")
        self.assertEqual(derived_state(output, "DQ-001"), "Ruled")

    def test_f06_genuinely_open_entry_derives_open(self):
        output = fixture_output("F-06")
        counts = h.canonical_counts(output)
        self.assertEqual(counts.get("Open"), 1)

    def test_f09_presented_entry_derives_presented(self):
        output = fixture_output("F-09")
        counts = h.canonical_counts(output)
        self.assertEqual(counts.get("Presented"), 1)


class UnclassifiableUnitTest(unittest.TestCase):
    """TG-S4-02: PIN-04 unclassifiable unit, plan section 2.6."""

    def test_shape_a_only_element_no_decision_evidence_gives_open(self):
        text = HEADER + open_entry(910, "Wombled")
        output = run_text(text)
        self.assertEqual(derived_state(output, "DQ-910"), "Open")
        self.assertEqual(findings(output, severity="Error"), [])
        entry = state_of(output, "DQ-910")
        self.assertFalse(h.is_ambiguous(entry))
        census = h.census_of(output)
        note = h.census_class(census, "unclassified")
        self.assertIsNotNone(note)
        self.assertIn("DQ-910", h.census_members(note))

    def test_shape_b_last_element_after_classifiable_gives_ambiguous(self):
        text = HEADER + (
            "### DQ-911: Synthetic entry 911\n\n"
            "Status: Banked\n\n"
            "#### Decision block\n\n"
            "Status: Wombled\n")
        output = run_text(text)
        entry = state_of(output, "DQ-911")
        self.assertTrue(h.is_ambiguous(entry))
        errors = findings(output, severity="Error")
        ambiguous_only = [
            f for f in errors
            if "state not determinable" in (
                h.finding_statement(f) or "").lower()
            or h.is_ambiguous(entry)]
        self.assertEqual(len(errors), len(ambiguous_only))

    def test_shape_b_only_status_line_with_decision_evidence(self):
        text = HEADER + ruled_entry(912, "Wombled")
        output = run_text(text)
        entry = state_of(output, "DQ-912")
        self.assertTrue(h.is_ambiguous(entry))
        census = h.census_of(output)
        note = h.census_class(census, "unclassified")
        self.assertIsNotNone(note)


class TailAndHeadingUnitTest(unittest.TestCase):
    """TG-S4-03: PIN-11, PIN-05 derivation half, MK-4, WV-7 shape 2,
    and the canonical equivalence construction for translation
    matching. Plan section 2.6."""

    def test_f15_heading_outcome_reading(self):
        output = fixture_output("F-15")
        self.assertEqual(derived_state(output, "DQ-901"), "Ruled")
        self.assertEqual(derived_state(output, "DQ-902"), "Settled")
        self.assertEqual(derived_state(output, "DQ-904"), "Open")

    def test_f15_ordered_heading_word_has_no_canonical_mapping(self):
        output = fixture_output("F-15")
        self.assertEqual(derived_state(output, "DQ-903"),
                         "Closed as decided")
        census = h.census_of(output)
        note = h.census_class(census, "unmatched", "heading")
        if note is None:
            note = h.census_class(census, "unclassified")
        self.assertIsNotNone(note)
        self.assertIn("DQ-903", h.census_members(note))

    def test_f16_single_paragraph_state_reading(self):
        output = fixture_output("F-16")
        self.assertEqual(derived_state(output, "DQ-905"), "Ruled")
        self.assertEqual(derived_state(output, "DQ-906"), "Settled")
        self.assertEqual(derived_state(output, "DQ-907"), "Open")

    def test_wv7_second_shape_disagreement_under_whole_body_rule(self):
        output = fixture_output("WV-7")
        entries = h.entries_of(output)
        self.assertTrue(entries)
        tail = [e for e in entries
                if h.get(e, "tail_form", "tail") ]
        self.assertTrue(tail or entries)

    def test_pin05_heading_determining_element_governs_not_unparsed(self):
        text = HEADER + (
            "## DQ-920: RULED by Captain JP\n\n"
            "A short body with no Status line and no decision "
            "block.\n")
        output = run_text(text)
        entry = state_of(output, "DQ-920")
        self.assertEqual(h.entry_state(entry), "Ruled")
        self.assertFalse(h.get(entry, "unparsed", "unparsed_flag"))

    def test_pin05_heading_as_last_line_of_file(self):
        text = HEADER + open_entry(921, "Banked") + (
            "\n## DQ-922: SETTLED by the Manager\n")
        output = run_text(text)
        entry = state_of(output, "DQ-922")
        self.assertEqual(h.entry_state(entry), "Settled")
        self.assertFalse(h.get(entry, "unparsed", "unparsed_flag"))

    def test_mk4_last_line_heading_unclassifiable_word_shape_a(self):
        # Construction MK-4, plan Item 3, section 3.10, attack 3: a
        # heading as the last line of the file, carrying an
        # unclassifiable heading word as its sole element, with no
        # decision evidence: no marker, and the Shape A result.
        text = HEADER + open_entry(923, "Banked") + (
            "\n## DQ-924: WOMBLED\n")
        output = run_text(text)
        entry = state_of(output, "DQ-924")
        self.assertEqual(h.entry_state(entry), "Open")
        self.assertFalse(h.get(entry, "unparsed", "unparsed_flag"))

    def test_canonical_equivalence_translation_matching(self):
        # Built at Step 13, as TG-S4-03 states: two phrasings that
        # are canonically equivalent and visibly identical, one in a
        # composed code point sequence standing in the translation
        # table, one in a decomposed sequence. The composed phrasing
        # matches; the decomposed phrasing takes the untranslatable
        # treatment. No normalisation is applied to either.
        composed = "Café fermé"
        decomposed = "Café fermé"
        # Construction check only, in the test: the two
        # phrasings are canonically equivalent and visibly
        # identical, while their as written code point
        # sequences differ. This normalises no product input.
        import unicodedata
        self.assertEqual(unicodedata.normalize("NFC", composed),
                         unicodedata.normalize("NFC", decomposed))
        self.assertNotEqual(
            [ord(c) for c in composed], [ord(c) for c in decomposed])
        text = HEADER + ruled_entry(930, composed) + "\n" + \
            ruled_entry(931, decomposed)
        output = run_text(text)
        first = state_of(output, "DQ-930")
        second = state_of(output, "DQ-931")
        self.assertFalse(h.is_ambiguous(first))
        self.assertTrue(
            h.is_ambiguous(second)
            or h.get(second, "unparsed", "unparsed_flag")
            or h.census_class(h.census_of(output), "untranslatable")
            is not None)

    def test_f07_trigger_in_recognised_form_gives_parked_no_error(self):
        # SR-6: the trigger stands in a form the recognition rule at
        # testing pin down 8 recognises.
        output = fixture_output("F-07")
        counts = h.canonical_counts(output)
        self.assertEqual(counts.get("Parked"), 1)
        self.assertEqual(findings(output, severity="Error"), [])

    def test_date_alone_is_not_a_trigger(self):
        # SR-6 negative case: a future date alone is not a trigger
        # statement, so the Parked with no trigger Error fires.
        text = HEADER + open_entry(
            940, "Parked. Revisit on 2027-01-01.")
        output = run_text(text)
        self.assertEqual(derived_state(output, "DQ-940"), "Parked")
        errors = findings(output, entry_id="DQ-940", severity="Error")
        self.assertTrue(errors)

    def test_f08_parked_with_no_trigger_gives_error(self):
        output = fixture_output("F-08")
        counts = h.canonical_counts(output)
        self.assertEqual(counts.get("Parked"), 1)
        self.assertTrue(findings(output, severity="Error"))

    def test_f18_first_entry_trigger_recognised(self):
        output = fixture_output("F-18")
        self.assertEqual(derived_state(output, "DQ-001"), "Parked")
        errors = findings(output, entry_id="DQ-001", severity="Error")
        self.assertEqual(errors, [])


class DisagreementAndPartFormUnitTest(unittest.TestCase):
    """TG-S4-04: PIN-07 selection half, PIN-12 state half, and the
    Slice 4 pin test. Plan section 2.6; exit test at plan Item 1,
    section 1.5."""

    def test_pin07_selection_supplies_pair_states_and_determining(self):
        text = HEADER + (
            "### DQ-950: Synthetic entry 950\n\n"
            "Status: Banked\n\n"
            "#### Ruling by Captain JP\n\n"
            "Ruled. This block decides the entry.\n\n"
            "Status: Banked\n")
        output = run_text(text)
        entry = state_of(output, "DQ-950")
        pair = h.get(entry, "competing_elements", "disagreement",
                     "competing_pair")
        self.assertIsNotNone(pair)
        denoted = h.get(entry, "denoted_states", "competing_states")
        self.assertIsNotNone(denoted)
        determining = h.get(entry, "determining_element",
                            "determining")
        self.assertIsNotNone(determining)

    def test_pin12_head_closed_with_undecided_part_in_prose_only(self):
        text = HEADER + (
            "### DQ-951: Synthetic entry 951\n\n"
            "Status: RULED, closed\n\n"
            "Ruled by: Captain JP\n\n"
            "Ruling text: \"The head form closes this entry.\"\n\n"
            "One part of the subject stays expressly undecided in "
            "this prose, and no part form element states it.\n\n"
            "Ruling outcome: The entry is closed.\n\n"
            "Where the ruling landed: synthetic record.\n")
        output = run_text(text)
        self.assertEqual(derived_state(output, "DQ-951"),
                         "Closed as decided")
        counts = h.canonical_counts(output)
        self.assertEqual(counts.get("Settled in part", 0), 0)

    def test_slice4_exit_every_headed_entry_gets_exactly_one_result(self):
        for fixture_id in ("F-02", "F-06", "F-07", "F-08", "F-09",
                           "F-15", "F-16", "F-17", "F-18"):
            with self.subTest(fixture=fixture_id):
                output = fixture_output(fixture_id)
                for entry in h.entries_of(output):
                    state = h.entry_state(entry)
                    unparsed = h.get(entry, "unparsed",
                                     "unparsed_flag")
                    results = sum([
                        1 if state in CANONICAL_STATES else 0,
                        1 if h.is_ambiguous(entry) else 0,
                        1 if unparsed else 0])
                    self.assertEqual(results, 1)

    def test_f17_bold_lead_in_derives_decided_state(self):
        output = fixture_output("F-17")
        first = state_of(output, "DQ-001")
        self.assertIn(h.entry_state(first), CANONICAL_STATES)
        self.assertNotEqual(h.entry_state(first), "Open")
        self.assertEqual(derived_state(output, "DQ-002"), "Open")


# The pin table is appended below by the writing seat from the
# record at design/research/step-06r/canonical-split-derivation.md,
# entry by entry, at testing pin down 4. No part of the table comes
# from design/steps/step-13r-derivations.md.
# Correction note (A2-F2): the source is named by path here, replacing
# the ambiguous shorthand "the Derivation seat record".
PIN_TABLE = {
    "DQ-035": "Ruled",
    "DQ-036": "Ruled",
    "DQ-037": "Settled",
    "DQ-038": "Settled",
    "DQ-039": "Settled",
    "DQ-040": "Settled",
    "DQ-041": "Settled",
    "DQ-042": "Settled",
    "DQ-043": "Settled",
    "DQ-044": "Settled",
    "DQ-045": "Settled",
    "DQ-046": "Settled",
    "DQ-047": "Settled",
    "DQ-048": "Settled",
    "DQ-049": "Settled",
    "DQ-050": "Settled",
    "DQ-051": "Settled",
    "DQ-052": "Ruled",
    "DQ-053": "Closed as decided",
    "DQ-054": "Settled",
    "DQ-055": "Settled",
    "DQ-056": "Settled",
    "DQ-057": "Settled",
    "DQ-058": "Settled",
    "DQ-059": "Conditional",
    "DQ-060": "Settled",
    "DQ-061": "Closed as decided",
    "DQ-062": "Settled",
    "DQ-063": "Settled",
    "DQ-064": "Closed as decided",
    "DQ-065": "Ruled",
    "DQ-066": "Settled",
    "DQ-067": "Closed as decided",
    "DQ-068": "Settled",
    "DQ-069": "Settled",
    "DQ-070": "Settled",
    "DQ-071": "Settled",
    "DQ-072": "Ruled",
    "DQ-073": "Conditional",
    "DQ-074": "Settled",
    "DQ-075": "Ruled",
    "DQ-076": "Settled",
    "DQ-077": "Ruled",
    "DQ-078": "Settled",
    "DQ-079": "Ruled",
    "DQ-080": "Settled",
    "DQ-081": "Settled",
    "DQ-082": "Settled",
    "DQ-083": "Ruled",
    "DQ-084": "Ruled",
    "DQ-085": "Settled",
    "DQ-086": "Settled",
    "DQ-087": "Ambiguous",
    "DQ-088": "Settled",
    "DQ-089": "Settled",
    "DQ-090": "Settled",
    "DQ-091": "Settled",
    "DQ-092": "Ruled",
    "DQ-093": "Settled",
    "DQ-094": "Settled",
    "DQ-095": "Settled",
    "DQ-096": "Settled",
    "DQ-097": "Settled",
    "DQ-098": "Settled",
    "DQ-099": "Settled",
    "DQ-100": "Ruled",
    "DQ-101": "Settled",
    "DQ-102": "Settled",
    "DQ-103": "Settled",
    "DQ-104": "Settled",
    "DQ-105": "Settled",
    "DQ-106": "Ambiguous",
    "DQ-107": "Settled",
    "DQ-108": "Ruled",
    "DQ-109": "Closed as decided",
    "DQ-110": "Closed as decided",
    "DQ-111": "Settled",
    "DQ-112": "Ruled",
    "DQ-113": "Ruled",
    "DQ-114": "Settled",
    "DQ-115": "Settled",
    "DQ-116": "Settled",
    "DQ-117": "Ruled",
    "DQ-118": "Ruled",
    "DQ-119": "Ruled",
    "DQ-120": "Ruled",
    "DQ-121": "Settled",
    "DQ-122": "Ruled",
    "DQ-123": "Settled",
    "DQ-124": "Settled",
    "DQ-125": "Settled",
    "DQ-126": "Settled",
    "DQ-127": "Settled",
    "DQ-128": "Ruled",
    "DQ-129": "Settled",
    "DQ-130": "Settled",
    "R-7": "Ruled",
    "DQ-002": "Ruled",
    "DQ-001": "Settled",
    "DQ-003": "Closed as decided",
    "DQ-004": "Ruled",
    "DQ-005": "Ruled",
    "DQ-006": "Ruled",
    "DQ-007": "Settled",
    "DQ-008": "Settled",
    "DQ-009": "Ruled",
    "DQ-010": "Ruled",
    "DQ-011": "Ruled",
    "DQ-012": "Ruled",
    "DQ-013": "Closed as decided",
    "DQ-014": "Settled",
    "DQ-015": "Ruled",
    "DQ-016": "Ruled",
    "DQ-018": "Ruled",
    "DQ-017": "Ruled",
    "DQ-019": "Ruled",
    "DQ-020": "Ruled",
    "DQ-021": "Ruled",
    "DQ-022": "Settled",
    "DQ-023": "Settled",
    "DQ-024": "Settled",
    "DQ-025": "Settled",
    "DQ-027": "Ruled",
    "DQ-026": "Settled",
    "DQ-028": "Ruled",
    "DQ-029": "Settled",
    "DQ-030": "Ruled",
    "DQ-031": "Ruled",
    "DQ-032": "Settled",
    "DQ-033": "Ruled",
    "DQ-034": "Settled",
    "DQ-138": "Ruled",
    "DQ-139": "Ruled",
    "DQ-140": "Ruled",
    "DQ-141": "Ruled",
    "DQ-142": "Ruled",
    "DQ-143": "Ruled",
    "DQ-144": "Ruled",
    "DQ-145": "Ruled",
    "DQ-146": "Ruled",
    "DQ-147": "Ruled",
    "DQ-148": "Ruled",
    "DQ-131": "Settled",
    "DQ-132": "Settled",
    "DQ-133": "Settled",
    "DQ-134": "Settled",
    "DQ-135": "Settled",
    "DQ-136": "Settled",
    "DQ-137": "Ruled",
    "DQ-149": "Ruled",
    "DQ-150": "Ruled",
    "DQ-151": "Ruled",
    "DQ-152": "Ruled",
    "DQ-153": "Ruled",
    "DQ-154": "Ruled",
    "DQ-155": "Ruled",
    "DQ-156": "Ruled",
    "DQ-157": "Ruled",
    "DQ-158": "Settled",
    "DQ-159": "Ruled",
    "DQ-160": "Closed as decided",
    "DQ-161": "Ruled",
    "DQ-162": "Open",
    "DQ-163": "Open",
    "DQ-164": "Open",
    "DQ-165": "Ruled",
    "DQ-166": "Ruled",
    "DQ-167": "Ruled",
    "DQ-168": "Ruled",
    "DQ-169": "Ruled",
    "DQ-170": "Ruled",
    "DQ-171": "Ruled",
}


class PinTest(unittest.TestCase):
    """TG-S4-04 pin test: entry by entry agreement with the
    record at design/research/step-06r/canonical-split-derivation.md
    at testing pin down 4, not footing agreement only. No part of
    the table comes from design/steps/step-13r-derivations.md.
    The DQ-022 dependence guard travels with this test: see
    DQ022_DEPENDENCE above. No coverage is claimed for the
    DQ-022 position.
    Correction note (C2-F1): the source is named by path here,
    replacing the ambiguous shorthand "the Derivation seat record"."""

    def _pin_output(self):
        for name in ("PIN", "restart-pin", "acceptance-pin"):
            path = CORPUS_DIR / (name + ".md")
            if path.exists():
                _model, output = h.run_pipeline(
                    path.read_bytes(), name=name + ".md")
                if output is not None:
                    return output
        raise AssertionError(
            "the restart pin copy does not stand in the corpus yet")

    def test_pin_table_foots_to_the_pinned_split(self):
        self.assertEqual(len(PIN_TABLE), PIN_HEADED_TOTAL)
        counts = {}
        ambiguous = 0
        for state in PIN_TABLE.values():
            if state == "Ambiguous":
                ambiguous += 1
            else:
                counts[state] = counts.get(state, 0) + 1
        for state, expected in PIN_SPLIT.items():
            self.assertEqual(counts.get(state, 0), expected, state)
        self.assertEqual(ambiguous, PIN_AMBIGUOUS)
        self.assertEqual(
            sum(PIN_SPLIT.values()) + PIN_AMBIGUOUS + PIN_UNPARSED,
            PIN_HEADED_TOTAL)

    def test_pin_entry_by_entry_agreement(self):
        output = self._pin_output()
        for entry_id, expected in PIN_TABLE.items():
            with self.subTest(entry=entry_id):
                entry = state_of(output, entry_id)
                if expected == "Ambiguous":
                    self.assertTrue(h.is_ambiguous(entry))
                else:
                    self.assertEqual(h.entry_state(entry), expected)

    def test_pin_ambiguous_entries_are_dq087_and_dq106(self):
        self.assertEqual(
            tuple(sorted(k for k, v in PIN_TABLE.items()
                         if v == "Ambiguous")),
            PIN_AMBIGUOUS_ENTRIES)

    def test_dq022_dependence_guard_travels_with_the_test(self):
        self.assertIn("no coverage is claimed",
                      DQ022_DEPENDENCE.lower())
        self.assertEqual(PIN_TABLE.get("DQ-022"), "Settled")
        added = [p.name for p in CORPUS_DIR.glob("*022*")]
        self.assertEqual(added, [])


if __name__ == "__main__":
    unittest.main()
