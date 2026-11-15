"""Restart Slice 3 tests, group TG-S3-01.

Source: plan Item 2, section 2.5, against plan Item 1, section 1.4,
plan Item 3, sections 3.4 and 3.5, plan Item 9, section 9.3, and
brief section 5.2 at PIN-01, PIN-02, PIN-05, and PIN-14. This slice
builds no state: every test here reads parse level facts only, being
element identification, extraction of disposition, scope, and
condition, element ordering, verbatim capture, and the unparsed
marker assignment. No test asserts a canonical state, a count of
states, or a finding.

Fixture set, as the register charges: F-02, F-15, and F-16 at the
capture level; F-17 at the capture level for the Candidate named
lead in form; and the restart pin scoped to the DQ-022 position for
the Supersession lead in form, under the dependence guard at plan
Item 2, section 2.2: no fixture is added by that dependence and no
coverage is claimed for the DQ-022 position. Fixture measurements
are deferred derivation D-13-1 and are asserted nowhere here. The
pin bytes are identified by the brief section 4 digest.
"""

import hashlib
import unittest

import dqv_harness as h

CORPUS_DIR = h.CORPUS_DIR
PIN_DIGEST = "23f6128230632a5de7f133a65a2497ed6fc11753083e17cd1dfd4" \
             "fa1e57c6132"

HEADER = "# Decision queue\n\nSynthetic queue shaped input.\n\n"


def queue_entry(number, title, level=3, body_lines=None):
    marks = "#" * level
    lines = ["%s DQ-%03d: %s" % (marks, number, title), ""]
    lines.extend(body_lines if body_lines is not None else [
        "Status: Banked",
        "",
        "Owner of record: Decision-queue Clerk",
        "",
        "The question: A synthetic question.",
        "",
    ])
    return "\n".join(lines) + "\n"


def parse(data, name="synthetic.md"):
    return h.run_parse(data, name)


def elements_of(entry):
    return h.as_list(h.get(entry, "status_elements",
                           "status_bearing_elements", "elements"))


def element_kind(element):
    return (h.text_of(h.get(element, "kind", "element_kind")) or "")


def element_verbatim(element):
    return h.text_of(h.get(element, "verbatim", "verbatim_value",
                           "verbatim_value_text"))


def element_line(element):
    line = h.get(element, "position_line", "line")
    if line is None:
        start, _end = h.span_of(element)
        return start
    return h.int_of(line)


def element_disposition(element):
    value = h.get(element, "disposition")
    if value is None:
        inner = h.get(element, "tuple", "element_tuple")
        if inner is not None:
            try:
                value = inner[0]
            except (TypeError, IndexError):
                value = h.get(inner, "disposition")
    return h.text_of(value)


def element_scope(element):
    value = h.get(element, "scope")
    if value is None:
        inner = h.get(element, "tuple", "element_tuple")
        if inner is not None:
            try:
                value = inner[1]
            except (TypeError, IndexError):
                value = h.get(inner, "scope")
    return h.text_of(value)


def element_condition(element):
    value = h.get(element, "condition")
    if value is None:
        inner = h.get(element, "tuple", "element_tuple")
        if inner is not None:
            try:
                value = inner[2]
            except (TypeError, IndexError):
                value = h.get(inner, "condition")
    return h.text_of(value)


def element_remainder(element):
    return h.text_of(h.get(element, "remainder_text", "remainder"))


def kinds_of(entry):
    return [element_kind(element).lower() for element in
            elements_of(entry)]


def manifest_entries():
    found = {}
    if not CORPUS_DIR.is_dir():
        return found
    for path in sorted(CORPUS_DIR.iterdir()):
        if not path.is_file() or path.suffix == ".json":
            continue
        if "manifest" not in path.name.lower():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for block in text.split("\n\n"):
            lines = [line for line in block.splitlines() if line.strip()]
            if not lines or not lines[0].startswith("Fixture:"):
                continue
            entry = {}
            for line in lines:
                if ":" in line:
                    label, value = line.split(":", 1)
                    entry[label.strip()] = value.strip()
            if "Fixture" in entry:
                found[entry["Fixture"]] = entry
    return found


def fixture_path(fixture_id):
    entry = manifest_entries().get(fixture_id)
    if entry and entry.get("Source"):
        from pathlib import Path
        candidate = CORPUS_DIR / Path(entry["Source"].split()[0]).name
        if candidate.is_file():
            return candidate
    for name in (fixture_id + ".md", fixture_id + ".txt",
                 fixture_id.replace("-", "") + ".md", fixture_id):
        candidate = CORPUS_DIR / name
        if candidate.is_file():
            return candidate
    return None


def require_fixture(testcase, fixture_id):
    path = fixture_path(fixture_id)
    testcase.assertIsNotNone(
        path, "restart fixture " + fixture_id + " does not stand in "
        "the corpus yet; this test depends on the Corpus seat "
        "standing it with its manifest entry under D-13-1")
    return path


def fixture_model(testcase, fixture_id):
    path = require_fixture(testcase, fixture_id)
    data = path.read_bytes()
    model = parse(data, path.name)
    testcase.assertFalse(h.is_failure_result(model),
                         "fixture " + fixture_id + " failed to parse")
    return model, data


def pin_bytes(testcase):
    if CORPUS_DIR.is_dir():
        for path in sorted(CORPUS_DIR.iterdir()):
            if not path.is_file():
                continue
            try:
                data = path.read_bytes()
            except OSError:
                continue
            if hashlib.sha256(data).hexdigest() == PIN_DIGEST:
                return data
    testcase.fail("the restart pin does not stand in the corpus; "
                  "this test depends on the acceptance pin copy "
                  "standing under testing pin down 11, identified by "
                  "the brief section 4 digest")


def single_entry_model(testcase, body_lines, number=1,
                       title="Synthetic entry", level=3):
    data = (HEADER + queue_entry(number, title, level=level,
                                  body_lines=body_lines)).encode()
    model = parse(data)
    testcase.assertFalse(h.is_failure_result(model))
    found = h.entries_of(model)
    testcase.assertEqual(len(found), 1)
    return found[0], data


class DecisionBlockFormTest(unittest.TestCase):

    def test_level_4_decision_block_with_segmentation_rule(self):
        body = [
            "Status: Banked",
            "",
            "#### Decision",
            "",
            "Ruled by: Captain JP",
            "",
            "Ruling text: The intake limb is adopted.",
            "",
            "Status: RULED, closed",
            "",
            "A closing note standing after the contained Status line.",
            "",
        ]
        entry, _data = single_entry_model(self, body)
        elements = elements_of(entry)
        status_lines = [el for el in elements
                        if "status line" in element_kind(el).lower()]
        self.assertTrue(status_lines,
                        "no Status line element stands in the entry")
        contained = [el for el in status_lines
                     if element_verbatim(el) == "RULED, closed"]
        self.assertTrue(contained,
                        "the Status line inside the decision block "
                        "is not its own element at its own line")
        block_elements = [el for el in elements
                          if "decision block" in element_kind(el)
                          .lower()]
        self.assertTrue(block_elements,
                        "the block matter outside the contained "
                        "Status line forms no segment element")
        for element in block_elements:
            self.assertNotEqual(
                element_line(element), element_line(contained[0]),
                "a block segment element spans the contained Status "
                "line as one element")

    def test_segment_with_two_disposition_statements_splits(self):
        body = [
            "#### Decision",
            "",
            "Ruled by: Captain JP. Settled by: the Manager.",
            "",
        ]
        entry, _data = single_entry_model(self, body)
        elements = elements_of(entry)
        self.assertGreaterEqual(
            len(elements), 2,
            "a segment carrying two disposition statements stands "
            "as one element; the segmentation rule splits it at the "
            "second disposition statement")
        dispositions = [(element_disposition(el) or "").lower()
                        for el in elements]
        self.assertTrue(any("rul" in item for item in dispositions))
        self.assertTrue(any("settl" in item for item in dispositions))

    def test_block_with_no_disposition_statement_carries_no_element(self):
        body = [
            "Status: Banked",
            "",
            "#### Background",
            "",
            "Plain narrative about the history of the question, "
            "stating no disposition for this entry.",
            "",
        ]
        entry, _data = single_entry_model(self, body)
        elements = elements_of(entry)
        block_elements = [el for el in elements
                          if "decision block" in element_kind(el)
                          .lower()]
        self.assertEqual(block_elements, [],
                         "a block with no disposition statement and "
                         "no contained Status line carries an element")


class LabelledParagraphFormTest(unittest.TestCase):

    def test_unheaded_labelled_paragraphs_under_recorded_label_forms(self):
        labels = [
            ("Ruled by: Captain JP", "rul"),
            ("Settled by: the Manager", "settl"),
            ("Ruling text: The intake limb is adopted.", "rul"),
            ("Ruling outcome: The intake limb stands adopted.", "rul"),
            ("Decision: The intake limb stands adopted.", None),
        ]
        for label_line, marker in labels:
            with self.subTest(label=label_line):
                body = ["Status: Banked", "", label_line, ""]
                entry, _data = single_entry_model(self, body)
                labelled = [el for el in elements_of(entry)
                            if "label" in element_kind(el).lower()]
                self.assertTrue(
                    labelled,
                    "no labelled paragraph element stands for the "
                    "recorded label form: " + label_line)
                if marker is not None:
                    dispositions = (
                        (element_disposition(el) or "").lower()
                        for el in labelled)
                    self.assertTrue(
                        any(marker in item for item in dispositions))

    def test_unrecorded_label_form_carries_no_labelled_element(self):
        body = [
            "Status: Banked",
            "",
            "Weather note: This entry is ruled and closed.",
            "",
        ]
        entry, _data = single_entry_model(self, body)
        labelled = [el for el in elements_of(entry)
                    if "label" in element_kind(el).lower()]
        self.assertEqual(labelled, [],
                         "a label form outside the recorded list "
                         "carries a labelled paragraph element")


class BoldLeadInFormTest(unittest.TestCase):

    def test_unrecorded_bold_lead_in_carries_no_element(self):
        body = [
            "Status: Banked",
            "",
            "**Weather summary:** This entry is settled and closed "
            "in the telling of the weather.",
            "",
        ]
        entry, _data = single_entry_model(self, body)
        bold = [el for el in elements_of(entry)
                if "bold" in element_kind(el).lower()]
        self.assertEqual(bold, [],
                         "a bold lead in outside the two recorded "
                         "forms carries an element; the recorded "
                         "forms only are the Candidate named lead in "
                         "and the Supersession lead in")

    def test_f17_candidate_named_lead_in_at_capture_level(self):
        model, _data = fixture_model(self, "F-17")
        first = h.entry_by_id(model, "DQ-001")
        second = h.entry_by_id(model, "DQ-002")
        self.assertIsNotNone(first)
        self.assertIsNotNone(second)
        bold_first = [el for el in elements_of(first)
                      if "bold" in element_kind(el).lower()]
        self.assertTrue(bold_first,
                        "DQ-001 carries no bold lead in paragraph "
                        "element at capture level")
        bold_second = [el for el in elements_of(second)
                       if "bold" in element_kind(el).lower()]
        self.assertEqual(bold_second, [],
                         "the control entry DQ-002 carries a bold "
                         "lead in element")


class TailParagraphFormTest(unittest.TestCase):

    def test_terminal_landing_record_sentence_is_not_an_element(self):
        body = [
            "Origin: Raised in the intake round. The question was "
            "considered in full and the matter rests with the named "
            "decider. Status: landed in the design repo and the "
            "checklist.",
            "",
        ]
        entry, _data = single_entry_model(
            self, body, title="A tail form entry", level=2)
        for element in elements_of(entry):
            verbatim = element_verbatim(element) or ""
            self.assertNotIn(
                "landed in", verbatim,
                "a terminal Status sentence whose value is a "
                "landing record stands as an element; it states no "
                "disposition and is not an element")

    def test_terminal_disposition_sentence_is_an_element(self):
        body = [
            "Origin: Raised in the intake round. The question was "
            "considered in full. Status: BANKED, awaiting Captain JP.",
            "",
        ]
        entry, _data = single_entry_model(
            self, body, title="A tail form entry", level=2)
        tail = [el for el in elements_of(entry)
                if "tail" in element_kind(el).lower()]
        self.assertTrue(tail,
                        "a terminal Status sentence stating a "
                        "remaining open state is not an element "
                        "under the tail single paragraph form")


class ExtractionTest(unittest.TestCase):

    def test_disposition_form_1_status_value(self):
        entry, _data = single_entry_model(
            self, ["Status: Banked", ""])
        elements = elements_of(entry)
        self.assertEqual(len(elements), 1)
        self.assertIn("bank", (element_disposition(elements[0])
                               or "").lower())

    def test_disposition_form_2_recorded_label(self):
        entry, _data = single_entry_model(
            self, ["Ruled by: Captain JP", "",
                   "Ruling text: The intake limb is adopted.", ""])
        dispositions = [(element_disposition(el) or "").lower()
                        for el in elements_of(entry)]
        self.assertTrue(any("rul" in item for item in dispositions))

    def test_disposition_form_3_unlabelled_prose(self):
        entry, _data = single_entry_model(
            self, ["The Manager settled this entry in full.", ""])
        dispositions = [(element_disposition(el) or "").lower()
                        for el in elements_of(entry)]
        self.assertTrue(any("settl" in item for item in dispositions),
                        "unlabelled prose that settles this entry "
                        "extracts no disposition")

    def test_disposition_form_4_prose_completing_without_a_state_word(self):
        entry, _data = single_entry_model(
            self, ["The Manager has set the outstanding values of "
                   "this entry.", ""])
        dispositions = [(element_disposition(el) or "").lower()
                        for el in elements_of(entry)]
        self.assertTrue(any("settl" in item for item in dispositions),
                        "prose stating that a named actor has set "
                        "the outstanding values extracts no Settled "
                        "disposition")

    def test_disposition_form_4_assessment_prose_closing_form(self):
        entry, _data = single_entry_model(
            self, ["Assessment: The challenge does not hold and the "
                   "item stands as decided. Closed.", ""])
        dispositions = [(element_disposition(el) or "").lower()
                        for el in elements_of(entry)]
        self.assertTrue(any("clos" in item for item in dispositions),
                        "assessment prose in the DQ-148 form that "
                        "closes this entry extracts no Closed as "
                        "decided disposition")

    def test_scope_is_whole_where_no_part_is_named(self):
        entry, _data = single_entry_model(
            self, ["Status: Ruled by Captain JP", ""])
        elements = elements_of(entry)
        self.assertTrue(elements)
        self.assertEqual(element_scope(elements[0]), "Whole")

    def test_scope_part_with_a_named_remainder(self):
        entry, _data = single_entry_model(self, [
            "Status: Ruled in part by Captain JP. The intake limb "
            "only is ruled. What stays banked: the remaining budget "
            "substance of this item stays banked.",
            "",
        ])
        elements = elements_of(entry)
        self.assertTrue(elements)
        element = elements[0]
        self.assertEqual(element_scope(element), "Part")
        remainder = element_remainder(element)
        if remainder is None:
            remainder = h.text_of(h.get(entry, "remainder_texts",
                                        "remainder_text",
                                        "remainders"))
        self.assertTrue(remainder,
                        "a part disposition with a named remainder "
                        "carries no remainder text")

    def test_scope_part_with_no_remainder_named(self):
        entry, _data = single_entry_model(self, [
            "Only the intake limb of this entry is ruled.",
            "",
        ])
        elements = elements_of(entry)
        self.assertTrue(elements)
        element = elements[0]
        self.assertEqual(element_scope(element), "Part")
        remainder = element_remainder(element)
        self.assertFalse(remainder,
                         "a part disposition naming no remainder "
                         "carries remainder text")

    def test_condition_extracted_from_a_conditional_clause(self):
        entry, _data = single_entry_model(self, [
            "Status: RULED, closed, subject to the landings recorded "
            "at DQ-142 standing verified.",
            "",
        ])
        elements = elements_of(entry)
        self.assertTrue(elements)
        condition = element_condition(elements[0])
        self.assertTrue(condition,
                        "a disposition subject to a stated condition "
                        "carries no condition text")
        self.assertIn("verified", condition)

    def test_no_condition_from_landing_record_date_or_reason(self):
        entry, _data = single_entry_model(self, [
            "Status: Ruled by Captain JP",
            "",
            "Where the ruling landed: the design repo, on "
            "2026-11-10, because the intake round had closed.",
            "",
        ])
        for element in elements_of(entry):
            self.assertFalse(
                element_condition(element),
                "a landing record, a date, or a reason stands "
                "extracted as a condition")


class OrderingTest(unittest.TestCase):

    def test_ordering_by_line_then_position_within_the_line(self):
        data, _facts = h.coincident_input()
        model = parse(data)
        self.assertFalse(h.is_failure_result(model))
        entry = h.entry_by_id(model, "DQ-901")
        self.assertIsNotNone(entry)
        elements = elements_of(entry)
        self.assertGreaterEqual(len(elements), 2,
                                "two status bearing elements on one "
                                "line stand as fewer than two elements")
        first_two = elements[:2]
        self.assertEqual(element_line(first_two[0]),
                         element_line(first_two[1]))
        verbatims = [element_verbatim(el) or "" for el in first_two]
        self.assertIn("Banked", verbatims[0])
        self.assertIn("Ruled", verbatims[1])

    def test_status_line_nested_in_decision_block_orders_at_its_line(self):
        body = [
            "#### Decision",
            "",
            "Ruled by: Captain JP",
            "",
            "Status: RULED, closed",
            "",
            "Ruling text: The intake limb is adopted.",
            "",
        ]
        entry, _data = single_entry_model(self, body)
        elements = elements_of(entry)
        lines = [element_line(el) for el in elements]
        self.assertEqual(lines, sorted(lines),
                         "elements stand out of PIN-02 order")
        contained = [el for el in elements
                     if element_verbatim(el) == "RULED, closed"]
        self.assertTrue(contained)
        heading_line = h.int_of(h.get(entry, "heading_line", "line"))
        expected_line = heading_line + 6
        self.assertEqual(element_line(contained[0]), expected_line,
                         "the nested Status line does not stand at "
                         "its own line")

    def test_reattached_span_elements_order_in_assembled_entry_order(self):
        model, data = fixture_model(self, "F-03")
        found = h.entries_of(model)
        self.assertEqual(len(found), 1)
        entry = found[0]
        elements = elements_of(entry)
        self.assertTrue(elements)
        lines = [element_line(el) for el in elements]
        text = data.decode("utf-8")
        addition_line = None
        for number, line in enumerate(text.splitlines(), start=1):
            if "addition" in line.lower():
                addition_line = number
        self.assertIsNotNone(addition_line)
        in_addition = [el for el in elements
                       if element_line(el) >= addition_line]
        self.assertTrue(in_addition,
                        "the addition paragraph carries no element")
        self.assertEqual(elements[-1], in_addition[-1],
                         "the element from the post Status addition "
                         "does not stand last in assembled entry "
                         "order")
        # Charged expectation from F-03, in the form the audit
        # acceptance of O-A-1 leaves it: the whole element list
        # stands in assembled entry order, so the position lines
        # stand in increasing order across the full span, the
        # opening Banked element stands first, and the closing
        # RULED, closed element stands after it and before the
        # addition element that stands last.
        self.assertEqual(lines, sorted(lines),
                         "the elements of the F-03 entry do not "
                         "stand in assembled entry order across "
                         "the reattached span")
        self.assertEqual(lines, sorted(set(lines)),
                         "two elements of the F-03 entry share "
                         "one position line, so no full order "
                         "stands between them")
        verbatims = [element_verbatim(el) or "" for el in elements]
        self.assertIn("Banked", verbatims[0])
        closing = [index for index, value in enumerate(verbatims)
                   if "RULED, closed" in value]
        self.assertTrue(closing,
                        "the F-03 closing Status element stands "
                        "nowhere in the element list")
        self.assertLess(closing[-1], len(elements) - 1,
                        "the closing Status element does not stand "
                        "before the addition element in assembled "
                        "entry order")

    def test_pin05_heading_borne_elements_order_before_body_elements(self):
        model, _data = fixture_model(self, "F-15")
        for entry in h.entries_of(model):
            elements = elements_of(entry)
            self.assertTrue(elements,
                            "a tail fixture entry carries no element")
            self.assertIn("heading", element_kind(elements[0]).lower(),
                          "the first element of a tail entry is not "
                          "the heading borne element")

    def test_origin_line_carries_no_element_by_itself(self):
        body = [
            "Origin: Raised by the intake round and recorded here "
            "for provenance only.",
            "",
        ]
        entry, _data = single_entry_model(
            self, body, title="A tail form entry", level=2)
        self.assertEqual(elements_of(entry), [],
                         "an Origin line stating no disposition "
                         "carries an element by itself")


class CaptureTest(unittest.TestCase):

    def test_pin14_every_occurrence_captured_once(self):
        body = [
            "Status: Banked",
            "",
            "Status: Ruled by Captain JP",
            "",
            "A paragraph closing in prose. Status: BANKED, awaiting "
            "Captain JP.",
            "",
            "Status unchanged: Banked.",
            "",
        ]
        entry, _data = single_entry_model(self, body)
        elements = elements_of(entry)
        self.assertEqual(len(elements), 4,
                         "four status occurrences stand captured as "
                         "%d elements" % len(elements))
        verbatims = [element_verbatim(el) for el in elements]
        self.assertEqual(len(set(verbatims)), 4)

    def test_pin14_near_duplicates_kept_distinct(self):
        body = [
            "Status: SETTLED, closed. Settled by a decision of the "
            "Manager under the grant.",
            "",
            "Status: SETTLED, closed. Settled by a pick of the "
            "Manager under the grant.",
            "",
        ]
        entry, _data = single_entry_model(self, body)
        verbatims = [element_verbatim(el) for el in elements_of(entry)
                     if element_verbatim(el)]
        self.assertEqual(len(verbatims), 2)
        self.assertNotEqual(verbatims[0], verbatims[1],
                            "near duplicate values are merged into "
                            "one capture")

    def test_f02_capture_level_inventory(self):
        model, data = fixture_model(self, "F-02")
        found = h.entries_of(model)
        self.assertEqual(len(found), 1)
        entry = found[0]
        text = data.decode("utf-8")
        self.assertFalse(any(line.startswith("Status:")
                             for line in text.splitlines()),
                         "the F-02 fixture carries a line beginning "
                         "with the Status marker, against its "
                         "specification")
        elements = elements_of(entry)
        self.assertTrue(elements,
                        "an entry with no Status line carries no "
                        "element at capture level, though its body "
                        "carries recorded label forms")
        for element in elements:
            self.assertNotIn("line start",
                             element_kind(element).lower())

    def test_f15_capture_level_inventory(self):
        model, _data = fixture_model(self, "F-15")
        found = h.entries_of(model)
        self.assertEqual(len(found), 4)
        for entry in found:
            for element in elements_of(entry):
                self.assertNotIn("line start",
                                 element_kind(element).lower(),
                                 "a tail fixture entry carries a "
                                 "line start Status element")
        third = found[2]
        heading_elements = [el for el in elements_of(third)
                            if "heading" in element_kind(el).lower()]
        self.assertTrue(heading_elements)
        self.assertIn("ORDERED",
                      element_verbatim(heading_elements[0]) or "")

    def test_f16_capture_level_inventory(self):
        model, _data = fixture_model(self, "F-16")
        found = h.entries_of(model)
        self.assertEqual(len(found), 3)
        tail_count = 0
        for entry in found:
            tail = [el for el in elements_of(entry)
                    if "tail" in element_kind(el).lower()]
            tail_count += len(tail)
            self.assertTrue(tail,
                            "a tail fixture entry carries no tail "
                            "paragraph element")
        self.assertEqual(tail_count, 3,
                         "the three embedded Status occurrences of "
                         "F-16 stand captured as %d tail elements"
                         % tail_count)

    def test_pin_dq022_supersession_lead_in_at_capture_level(self):
        data = pin_bytes(self)
        model = parse(data, "pin.md")
        self.assertFalse(h.is_failure_result(model))
        entry = h.entry_by_id(model, "DQ-022")
        self.assertIsNotNone(entry)
        matched = []
        for element in elements_of(entry):
            verbatim = element_verbatim(element) or ""
            statement = h.text_of(h.get(element, "statement")) or ""
            if "Supersession:" in verbatim or \
                    "Supersession:" in statement:
                matched.append(element)
        self.assertTrue(matched,
                        "no element at the DQ-022 position carries "
                        "the Supersession lead in form at capture "
                        "level; this test claims capture at that "
                        "position only, under the dependence guard "
                        "at plan Item 2, section 2.2, and no "
                        "coverage for the DQ-022 position")


class UnparsedMarkerTest(unittest.TestCase):

    def _marker(self, entry):
        value = h.get(entry, "unparsed_marker", "unparsed",
                      "unparsed_flag", "marker")
        return bool(value)

    def test_marker_on_truncated_body_with_no_determining_element(self):
        text = HEADER + "### DQ-001: A cut off entry\n\n" \
               "Plain prose with no disposition in it, cut of"
        model = parse(text.encode())
        self.assertFalse(h.is_failure_result(model))
        found = h.entries_of(model)
        self.assertEqual(len(found), 1)
        self.assertTrue(self._marker(found[0]),
                        "an entry whose last body line is cut off "
                        "at end of file, with no determining element "
                        "extracted, takes no unparsed marker")

    def test_marker_on_heading_only_final_entry_with_no_element(self):
        text = HEADER + queue_entry(1, "A complete entry") \
            + "### DQ-002: A plain heading with no outcome word"
        model = parse(text.encode())
        self.assertFalse(h.is_failure_result(model))
        entry = h.entry_by_id(model, "DQ-002")
        self.assertIsNotNone(entry)
        self.assertTrue(self._marker(entry),
                        "a heading only final entry from which no "
                        "determining element can be extracted takes "
                        "no unparsed marker")

    def test_pin05_exception_classifiable_heading_word_takes_no_marker(self):
        text = HEADER + queue_entry(1, "A complete entry") \
            + "## DQ-002: RULED"
        model = parse(text.encode())
        self.assertFalse(h.is_failure_result(model))
        entry = h.entry_by_id(model, "DQ-002")
        self.assertIsNotNone(entry)
        self.assertFalse(self._marker(entry),
                         "a heading only final entry whose heading "
                         "extracts a determining element takes the "
                         "unparsed marker, against the PIN-05 "
                         "exception")

    def test_pin05_exception_unclassifiable_heading_word_takes_no_marker(self):
        text = HEADER + queue_entry(1, "A complete entry") \
            + "## DQ-002: ORDERED"
        model = parse(text.encode())
        self.assertFalse(h.is_failure_result(model))
        entry = h.entry_by_id(model, "DQ-002")
        self.assertIsNotNone(entry)
        self.assertFalse(self._marker(entry),
                         "construction MK-4: a heading that is the "
                         "last line of the file, carrying an "
                         "unclassifiable heading word as its sole "
                         "element and no decision evidence, takes a "
                         "marker; the PIN-05 exception in its "
                         "extraction sense bars the assignment")


class ExitConditionTest(unittest.TestCase):

    def test_complete_element_inventory_in_order_on_open_fixtures(self):
        for fixture_id in ("F-02", "F-15", "F-16", "F-17"):
            with self.subTest(fixture=fixture_id):
                model, _data = fixture_model(self, fixture_id)
                for entry in h.entries_of(model):
                    elements = elements_of(entry)
                    self.assertTrue(
                        elements,
                        fixture_id + " entry "
                        + str(h.entry_identifier(entry))
                        + " carries an empty element inventory")
                    lines = [element_line(el) for el in elements]
                    self.assertEqual(lines, sorted(lines),
                                     "the inventory stands out of "
                                     "element order")
                    for element in elements:
                        self.assertTrue(element_kind(element),
                                        "an element carries no kind")
                        self.assertGreaterEqual(element_line(element),
                                                1)


if __name__ == "__main__":
    unittest.main()
