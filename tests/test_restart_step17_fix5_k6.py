"""Restart Step 17 fix wave 5, cluster K6 tests.

Charges CH-85, CH-86, and CH-87, ruled at section 52 of
design/steps/step-17r-record.md and prepared at
design/steps/step-17r-triage5-prep.md. Every cure stands in
product/decision_queue_validator/validate.py only.

CH-85 (round 5 attack seat 8, findings F5-8-1 to F5-8-6):
the Banked head evidence groups, round 5 limbs. An entry
identifier alone in a respelled form takes no group credit;
a partial block whose only body is a landed line or an
Origin line takes no group credit, toward the PIN-01
ground; a taught field label in a further respelled form
takes no group credit; a heading shaped line behind a
fresh marker or wrap takes no group credit; a level 4
entry heading in a non exact form takes the orphan
treatment at the census and findings surfaces of
validate, the Arabic Indic digit member at the orphan
reading only under record section 52 ruling (g), the
ASCII digit ground unmoved; and a second decider line in
lower case or with its value on the next line draws the
decider conflict finding.

CH-86 (round 5 attack seat 10, finding A5-10-F1): the
blocking figure no item values, round 5 limbs, 29 fresh
phrase, wrapper, and joiner forms. The D2 blocking
narrowing pin and the O4 corpus bound stand whole.

CH-87 (round 5 attack seat 10, finding A5-10-F2): part
scope remainder verb widths, round 5 limbs. Remainder
statements in fresh verb forms are read in the statement
and in their own paragraph alike, including the bare
remainder stands open asymmetry between the two surfaces.
The CH-66, CH-67, CH-63, and PIN-01, PIN-03 pins whole
stand. No construction in this file builds the F1 shape,
and no banked question is named in any construction.
"""

import tempfile
import unittest
from pathlib import Path

import dqv_harness as h

validate = h.import_module("validate")

HEAD = "# Decision queue\n\n"
FIELDS = ("Question: Which option should we take?\n\n"
          "Options: Option A, Option B\n\n"
          "Cost of deciding late: Work stays blocked.\n\n"
          "Blocks: DQ-002\n\n")
BLOCK = "#### Ruling by Captain JP\n\n"


def entry(body, dq="DQ-001", title="Test entry", status="Banked"):
    text = "### %s: %s\n\n" % (dq, title)
    if status is not None:
        text += "Status: %s\n\n" % status
    return text + FIELDS + body


def banked_block_entry(body_line):
    return HEAD + entry(BLOCK + body_line + "\n")


def banked_plain_entry(body_line):
    return HEAD + entry(body_line + "\n")


def run_cli_on(test_case, text, subcommand="validate"):
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "case.md"
        target.write_bytes(text.encode("utf-8"))
        code, out, err = h.run_cli(subcommand, target)
    combined = (out + err).decode("utf-8", errors="replace")
    return code, combined


def group_members(output, *name_parts):
    group = h.census_class(h.census_of(output), *name_parts)
    if group is None:
        return []
    return h.census_members(group)


def sums_agree(output):
    recon = h.reconciliation_of(output)
    check = h.get(recon, "self_check", "self_check_result")
    return h.get(check, "sums_agree", "ok", "passed", "agrees")


def assert_in_no_group(test_case, output):
    for name in ("level 4 decision block", "unheaded paragraphs",
                 "later Status line"):
        test_case.assertNotIn("DQ-001", group_members(output, name))
    test_case.assertEqual(sums_agree(output), False)


def open_entry(number, blocks_value, label="Blocks"):
    return (
        "### DQ-%03d: Blocks case %d\n"
        "\n"
        "Status: Banked\n"
        "\n"
        "Question: Which option?\n"
        "\n"
        "Options: Option A, Option B\n"
        "\n"
        "Cost of deciding late: Work stays blocked.\n"
        "\n"
        "%s: %s\n"
        "\n"
        "A plain context paragraph.\n"
        % (number, number, label, blocks_value))


def taught_entry(number, title, ruling_paragraphs):
    text = (
        "### DQ-%03d: %s\n"
        "\n"
        "Status: Banked\n"
        "\n"
        "Question: Which option should we take?\n"
        "\n"
        "Options: Option A, Option B\n"
        "\n"
        "Cost of deciding late: Work stays blocked.\n"
        "\n"
        "Blocks: DQ-002\n"
        "\n"
        "A plain context paragraph.\n" % (number, title))
    for paragraph in ruling_paragraphs:
        text += "\n" + paragraph + "\n"
    return text


def state_of(output, entry_id):
    found = h.entry_by_id(output, entry_id)
    if found is None:
        raise AssertionError("no entry %s in the output" % entry_id)
    return h.entry_state(found)


def blocking_of(text):
    _model, output = h.run_pipeline(text.encode("utf-8"))
    if output is None:
        raise AssertionError("pipeline produced no output")
    _waiting, blocking = h.waiting_and_blocking(output)
    return output, h.int_of(blocking)


class Ch85IdentifierRespelledTest(unittest.TestCase):
    """F5-8-1: an entry identifier alone in a respelled
    form states no content and takes no group credit, in
    the block and plain forms alike."""

    BLOCK_FORMS = ("DQ-002.", "dq-002", "DQ002",
                   "DQ-002 DQ-003")
    PLAIN_FORMS = ("DQ 002", "DQ - 002", "DQ-002.", "dq-002")

    def test_respelled_identifier_in_block_takes_no_group(self):
        for line in self.BLOCK_FORMS:
            with self.subTest(line=line):
                _model, output = h.run_pipeline(
                    banked_block_entry(line).encode("utf-8"))
                self.assertIsNotNone(output)
                assert_in_no_group(self, output)

    def test_respelled_identifier_plain_takes_no_group(self):
        for line in self.PLAIN_FORMS:
            with self.subTest(line=line):
                _model, output = h.run_pipeline(
                    banked_plain_entry(line).encode("utf-8"))
                self.assertIsNotNone(output)
                assert_in_no_group(self, output)

    def test_content_test_reads_respelled_identifiers_empty(self):
        for line in self.BLOCK_FORMS + self.PLAIN_FORMS:
            with self.subTest(line=line):
                self.assertEqual(
                    validate._line_carries_content(line), False)

    def test_respelled_identifier_withholds_the_run(self):
        code, combined = run_cli_on(
            self, banked_block_entry("DQ-002."))
        self.assertEqual(code, 4)
        self.assertIn("Banked head evidence groups sum to 0",
                      combined)

    def test_exact_identifier_pin_stands(self):
        # Pin, passing before and after: the exact CH-63
        # form takes no credit, in the block and plain
        # forms alike.
        for builder in (banked_block_entry, banked_plain_entry):
            with self.subTest(builder=builder.__name__):
                _model, output = h.run_pipeline(
                    builder("DQ-002").encode("utf-8"))
                self.assertIsNotNone(output)
                assert_in_no_group(self, output)
        self.assertEqual(validate._line_carries_content("R-7"),
                         False)

    def test_identifier_beside_words_keeps_content(self):
        # Guard, passing before and after: an identifier
        # standing inside genuine prose is prose, and the
        # neighbouring token forms of the CH-63 bound keep
        # their content reading.
        self.assertEqual(
            validate._line_carries_content(
                "DQ-002 is the harbour entry"), True)
        self.assertEqual(validate._line_carries_content("ab1 cd2"),
                         True)
        self.assertEqual(
            validate._line_carries_content("\u4e2d\u6587"), True)


class Ch85PartialBlockNonDispositionTest(unittest.TestCase):
    """F5-8-2: a partial block whose only body is a landed
    line or an Origin line carries no disposition
    statement and takes no group credit, toward PIN-01
    form 1."""

    BLOCK_FORMS = (
        "Landed in the harbour log.",
        "Landed: the harbour log",
        "Origin: Captain JP raised this question in the "
        "meeting.",
        "Origin: the board",
    )

    def test_landed_or_origin_only_block_takes_no_group(self):
        for line in self.BLOCK_FORMS:
            with self.subTest(line=line):
                _model, output = h.run_pipeline(
                    banked_block_entry(line).encode("utf-8"))
                self.assertIsNotNone(output)
                assert_in_no_group(self, output)

    def test_landed_or_origin_only_block_withholds(self):
        code, combined = run_cli_on(
            self, banked_block_entry("Landed in the harbour "
                                     "log."))
        self.assertEqual(code, 4)
        self.assertIn("Banked head evidence groups sum to 0",
                      combined)

    def test_date_only_block_pin_stands(self):
        # Pin, passing before and after: the attack paper
        # control, a date only block body, takes no credit.
        _model, output = h.run_pipeline(
            banked_block_entry("2026-11-17").encode("utf-8"))
        self.assertIsNotNone(output)
        assert_in_no_group(self, output)

    def test_genuine_block_credit_pins_stand(self):
        # Pins, passing before and after: a full ruling
        # block credits group 2, and the genuine short word
        # control of FLAG 6 keeps its group 2 credit.
        block_body = ("Ruled by: Captain JP\n\n"
                      "Ruled. The harbour light burns all "
                      "night.\n\n"
                      "Outcome: Closed.\n\n"
                      "Landed in the harbour log.\n")
        text = HEAD + entry(BLOCK + block_body)
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        self.assertIn("DQ-001", group_members(
            output, "level 4 decision block"))
        self.assertEqual(sums_agree(output), True)
        _model, output = h.run_pipeline(
            banked_block_entry("\u4e2d\u6587").encode("utf-8"))
        self.assertIsNotNone(output)
        self.assertIn("DQ-001", group_members(
            output, "level 4 decision block"))


class Ch85RespelledLabelRound5Test(unittest.TestCase):
    """F5-8-3: a labelled field line in a further
    respelled form of a taught label takes no group
    credit, in group 3 and inside a block."""

    PLAIN_FORMS = (
        "Question2: genuine words stand here in a repeated "
        "line.",
        "Cost of deciding late while the harbour works and "
        "the town works both stand waiting through the "
        "whole winter season: genuine words stand here.",
        "Question\u00a0: genuine words stand here in a repeated "
        "line.",
    )
    BLOCK_FORMS = (
        "Question (as put): genuine words stand here in a "
        "repeated line.",
    )

    def test_respelled_plain_forms_take_no_group(self):
        for line in self.PLAIN_FORMS:
            with self.subTest(line=line):
                _model, output = h.run_pipeline(
                    banked_plain_entry(line).encode("utf-8"))
                self.assertIsNotNone(output)
                assert_in_no_group(self, output)

    def test_respelled_block_form_takes_no_group(self):
        for line in self.BLOCK_FORMS:
            with self.subTest(line=line):
                _model, output = h.run_pipeline(
                    banked_block_entry(line).encode("utf-8"))
                self.assertIsNotNone(output)
                assert_in_no_group(self, output)

    def test_labelled_test_reads_the_round5_forms(self):
        for line in self.PLAIN_FORMS + self.BLOCK_FORMS:
            with self.subTest(line=repr(line)):
                self.assertEqual(
                    validate._is_open_field_labelled_line(line),
                    True)

    def test_plural_label_bound_case_stands(self):
        # Bound case of the attack paper, passing before
        # and after: the plural Questions label is no
        # taught label respelling, and its line takes no
        # group credit on the standing capitalised label
        # reading.
        line = ("Questions: genuine words stand here in a "
                "repeated line.")
        self.assertEqual(
            validate._is_open_field_labelled_line(line), False)
        _model, output = h.run_pipeline(
            banked_plain_entry(line).encode("utf-8"))
        self.assertIsNotNone(output)
        assert_in_no_group(self, output)

    def test_unrelated_labels_stand_outside_the_taught_set(self):
        # Pin, passing before and after, from the CH-63
        # bound forms.
        for line in ("note: genuine words stand here in a "
                     "note line.",
                     "question_text: genuine words stand here "
                     "in a repeated line."):
            with self.subTest(line=line):
                self.assertEqual(
                    validate._is_open_field_labelled_line(line),
                    False)


class Ch85HeadingShapeRound5Test(unittest.TestCase):
    """F5-8-4: a heading shaped line behind a fresh marker
    or wrap form takes no group credit, in group 3 and
    inside a block."""

    PLAIN_FORMS = (
        "abc) #### Ruling by Captain JP",
        "\u25e6 #### Ruling by Captain JP",
        "***#### Ruling by Captain JP",
        "_#### Ruling by Captain JP",
    )

    def test_fresh_marker_heading_forms_take_no_group(self):
        for line in self.PLAIN_FORMS:
            with self.subTest(line=repr(line)):
                self.assertEqual(
                    validate._is_heading_shaped_line(line), True)
                _model, output = h.run_pipeline(
                    banked_plain_entry(line).encode("utf-8"))
                self.assertIsNotNone(output)
                assert_in_no_group(self, output)

    def test_fresh_marker_heading_inside_block_takes_no_group(self):
        line = "abc) #### Ruling by Captain JP"
        _model, output = h.run_pipeline(
            banked_block_entry(line).encode("utf-8"))
        self.assertIsNotNone(output)
        assert_in_no_group(self, output)

    def test_genuine_prose_behind_the_same_forms_keeps_credit(self):
        # Pins, passing before and after, on the bound of
        # the family: genuine prose behind the same marker
        # and wrap forms keeps its group 3 credit.
        for line in ("abc) An unheaded paragraph stands here.",
                     "***An unheaded paragraph stands here.",
                     "_An unheaded paragraph stands here."):
            with self.subTest(line=line):
                self.assertEqual(
                    validate._is_heading_shaped_line(line), False)
                _model, output = h.run_pipeline(
                    banked_plain_entry(line).encode("utf-8"))
                self.assertIsNotNone(output)
                self.assertIn("DQ-001", group_members(
                    output, "unheaded paragraphs"))
                self.assertEqual(sums_agree(output), True)


class Ch85Level4NonExactHeadingTest(unittest.TestCase):
    """F5-8-5: a level 4 entry heading in a non exact form
    takes the orphan treatment at the validate surfaces:
    a PIN-06 Warning naming the heading as written, and
    the entry above foots on its own matter only. The
    Arabic Indic digit member is read at the orphan
    reading only; no data reading widens."""

    @staticmethod
    def _construction(heading_line):
        return (HEAD + entry("An unheaded paragraph stands "
                             "here.\n")
                + heading_line + "\n\n"
                + "Status: Banked\n\n" + FIELDS
                + "An unheaded paragraph stands here.\n")

    FORMS = (
        ("#### DQ-\u0660\u0660\u0662: Second entry",
         "DQ-\u0660\u0660\u0662: Second entry"),
        ("#### DQ-002:Second entry", "DQ-002:Second entry"),
        ("#### R-8: Second entry", "R-8: Second entry"),
    )

    def test_non_exact_headings_take_the_orphan_warning(self):
        for heading_line, heading_text in self.FORMS:
            with self.subTest(heading=heading_line):
                code, combined = run_cli_on(
                    self, self._construction(heading_line))
                self.assertEqual(code, 1)
                self.assertIn(heading_text, combined)
                self.assertIn(
                    "matches no recognised heading form",
                    combined)

    def test_absorbed_status_line_no_longer_moves_the_entry(self):
        for heading_line, _text in self.FORMS:
            with self.subTest(heading=heading_line):
                _model, output = h.run_pipeline(
                    self._construction(
                        heading_line).encode("utf-8"))
                self.assertIsNotNone(output)
                self.assertNotIn("DQ-001", group_members(
                    output, "later Status line"))
                self.assertNotIn("DQ-001", group_members(
                    output, "level 4 decision block"))
                self.assertIn("DQ-001", group_members(
                    output, "unheaded paragraphs"))
                self.assertEqual(sums_agree(output), True)

    def test_exact_form_pin_stands(self):
        # Pin, passing before and after: the CH-63 cured
        # exact form keeps its Warning and its group 3
        # footing.
        text = self._construction("#### DQ-002: Second entry")
        code, combined = run_cli_on(self, text)
        self.assertEqual(code, 1)
        self.assertIn("DQ-002: Second entry", combined)
        self.assertIn("matches no recognised heading form",
                      combined)
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        self.assertIn("DQ-001", group_members(
            output, "unheaded paragraphs"))

    def test_genuine_decision_block_heading_stands(self):
        # Pin, passing before and after: a level 4 heading
        # in ruling form inside an entry stays a decision
        # block and takes no orphan Warning.
        block_body = ("Ruled by: Captain JP\n\n"
                      "Ruled. The harbour light burns all "
                      "night.\n\n"
                      "Outcome: Closed.\n\n"
                      "Landed in the harbour log.\n")
        text = HEAD + entry(BLOCK + block_body)
        code, combined = run_cli_on(self, text)
        self.assertEqual(code, 0)
        self.assertNotIn("matches no recognised heading form",
                         combined)


class Ch85DeciderRound5Test(unittest.TestCase):
    """F5-8-6: two decider lines naming two different
    deciders draw the conflict finding where the second
    line stands in lower case or with its value on the
    next line. The space before colon bound case and the
    first two names bound stand as recorded."""

    RULED_TAIL = ("Ruled. The harbour light burns all "
                  "night.\n\n"
                  "Outcome: Closed.\n\n"
                  "Landed in the harbour log.\n")

    def _conflict_findings(self, output):
        found = []
        for finding in h.findings_of(output):
            statement = h.finding_statement(finding) or ""
            if "decider" in statement.lower() and \
                    "two" in statement.lower():
                found.append(finding)
        return found

    def _run(self, second_lines):
        body = (BLOCK + "Ruled by: Captain JP\n\n"
                + second_lines + self.RULED_TAIL)
        return HEAD + entry(body)

    def test_second_decider_in_lower_case_takes_a_finding(self):
        text = self._run("ruled by: sam\n\n")
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        conflicts = self._conflict_findings(output)
        self.assertEqual(len(conflicts), 1)
        statement = h.finding_statement(conflicts[0])
        self.assertIn("Captain JP", statement)
        self.assertIn("sam", statement.lower())
        code, _combined = run_cli_on(self, text)
        self.assertEqual(code, 1)

    def test_second_decider_value_on_next_line_takes_a_finding(self):
        text = self._run("Ruled by:\nSam\n\n")
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        conflicts = self._conflict_findings(output)
        self.assertEqual(len(conflicts), 1)
        statement = h.finding_statement(conflicts[0])
        self.assertIn("Captain JP", statement)
        self.assertIn("Sam", statement)
        code, _combined = run_cli_on(self, text)
        self.assertEqual(code, 1)

    def test_exact_form_conflict_pin_stands(self):
        # Pin, passing before and after: the CH-63 cured
        # exact form takes its one conflict finding.
        text = self._run("Ruled by: Sam\n\n")
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        conflicts = self._conflict_findings(output)
        self.assertEqual(len(conflicts), 1)
        statement = h.finding_statement(conflicts[0])
        self.assertIn("Captain JP", statement)
        self.assertIn("Sam", statement)

    def test_exact_repetition_pin_stands(self):
        # Pin, passing before and after: the same decider
        # line doubled word for word takes no finding.
        text = self._run("Ruled by: Captain JP\n\n")
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        self.assertEqual(self._conflict_findings(output), [])
        code, _combined = run_cli_on(self, text)
        self.assertEqual(code, 0)

    def test_space_before_colon_bound_case_takes_no_conflict(self):
        # Bound case of the attack paper, observation 1,
        # passing before and after on this limb: the space
        # before colon form is no decider line of the
        # colon form, and draws no conflict finding.
        text = self._run("Ruled by : Sam\n\n")
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        self.assertEqual(self._conflict_findings(output), [])

    def test_three_deciders_name_the_first_two_only(self):
        # Bound of the CH-63 limb, passing before and
        # after: at most the first two distinct names are
        # named.
        text = self._run("Ruled by: Sam\n\nRuled by: Alex\n\n")
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        conflicts = self._conflict_findings(output)
        self.assertEqual(len(conflicts), 1)
        statement = h.finding_statement(conflicts[0])
        self.assertIn("Captain JP", statement)
        self.assertIn("Sam", statement)
        self.assertNotIn("Alex", statement)


class Ch86BlockingRound5Test(unittest.TestCase):
    """CH-86, A5-10-F1: the blocking figure no item
    values, round 5 limbs."""

    FRESH_NO_ITEM_VALUES = (
        "nothing blocked",
        "no outstanding items",
        "zero blockers",
        "0 blockers",
        "unblocked",
        "clear",
        "blocks no entry",
        "does not block any entry",
        "no entry blocked",
        "nought",
        "zip",
        "none recorded",
        "nothing recorded",
        "no blocks recorded",
        "not blocking",
        "non-blocking",
        "[none]",
        "{none}",
        '"none"',
        "*none*",
        "none | nothing",
        "none \\ nothing",
        "none ~ nothing",
        "none at present",
        "nothing outstanding",
        "no pending entries",
        "nothing hinders",
        "free",
        "vacant",
    )

    def test_a5_10_f1_each_fresh_no_item_value_does_not_count(self):
        for value in self.FRESH_NO_ITEM_VALUES:
            with self.subTest(value=value):
                text = ("# Decision queue\n\n"
                        + open_entry(1, value))
                _output, blocking = blocking_of(text)
                self.assertEqual(blocking, 0)

    def test_a5_10_f1_combined_figure(self):
        values = (
            "nothing blocked",
            "zero blockers",
            "none | nothing",
            "[none]",
            "none recorded",
            "DQ-002",
            "none",
            "nothing at all",
        )
        text = "# Decision queue\n\n" + "\n".join(
            open_entry(number, value)
            for number, value in enumerate(values, start=1))
        output, blocking = blocking_of(text)
        self.assertEqual(blocking, 1)
        listed = h.as_list(h.get(output, "blocking_list"))
        listed_ids = [h.text_of(h.get(
            item, "entry_id", "identifier")) for item in listed]
        self.assertEqual(listed_ids, ["DQ-006"])

    def test_a5_10_f1_same_edge_under_what_it_blocks_label(self):
        text = ("# Decision queue\n\n"
                + open_entry(1, "DQ-002")
                + "\n"
                + open_entry(2, "nothing blocked",
                             label="What it blocks"))
        _output, blocking = blocking_of(text)
        self.assertEqual(blocking, 1)

    def test_ch66_and_ch43_pins_whole_stand(self):
        # Pins, passing before and after: the CH-66 and
        # CH-43 charged forms keep their cured outcome.
        for value in ("no blockers", "blocks nothing",
                      "none whatsoever", "zero items", "0",
                      "(none)", "none/nothing", "n.a.",
                      "nothing at all", "none at all",
                      "nothing whatsoever", "n/a",
                      "not applicable", "no entries", "nil",
                      "empty", "Nothing.."):
            with self.subTest(value=value):
                text = ("# Decision queue\n\n"
                        + open_entry(1, value))
                _output, blocking = blocking_of(text)
                self.assertEqual(blocking, 0)

    def test_d2_part_exactly_nothing_dot_still_names_an_item(self):
        # Pin under the D2 blocking narrowing pin,
        # passing before and after.
        for value in ("Nothing.", "nothing.",
                      "nothing. and none", "none, nothing."):
            with self.subTest(value=value):
                text = ("# Decision queue\n\n"
                        + open_entry(1, value))
                _output, blocking = blocking_of(text)
                self.assertEqual(blocking, 1)

    def test_o4_corpus_form_nothing_named_keeps_standing_treatment(self):
        # Pin under the O4 corpus bound, passing before
        # and after.
        text = ("# Decision queue\n\n"
                + open_entry(1, "nothing named."))
        _output, blocking = blocking_of(text)
        self.assertEqual(blocking, 1)

    def test_real_reference_beside_no_item_part_still_counts(self):
        # Guard, passing before and after, on the standing
        # joiners and on the fresh joiners alike.
        for value in ("DQ-002, none", "none/DQ-002",
                      "none | DQ-002", "DQ-002 ~ none"):
            with self.subTest(value=value):
                text = ("# Decision queue\n\n"
                        + open_entry(1, value))
                _output, blocking = blocking_of(text)
                self.assertEqual(blocking, 1)


class Ch87RemainderRound5Test(unittest.TestCase):
    """CH-87, A5-10-F2: part scope remainder verb widths,
    round 5 limbs, in the statement and in the own
    paragraph shapes alike."""

    STATEMENT_FORMS = (
        (2, "Remainder bare stands open",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The remainder stands open."),
        (3, "Remainder bare still stands open",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The remainder still stands open."),
        (5, "Remainder remains outstanding",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The remainder remains outstanding."),
        (6, "Rest is outstanding",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The rest is outstanding."),
        (9, "Rest is still unresolved",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The rest is still unresolved."),
        (10, "Remainder named is still unresolved",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The remainder, the second part, "
         "is still unresolved."),
        (11, "Remainder is yet to be decided",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The remainder is yet to be "
         "decided."),
        (12, "Rest remains to be decided",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The rest remains to be decided."),
        (13, "Remainder is left open",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The remainder is left open."),
        (14, "Rest continues to stand open",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The rest continues to stand open."),
        (15, "Remainder awaits decision",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The remainder awaits decision."),
        (16, "Settled rest remains outstanding",
         "Settled by Captain JP: the first part is settled, "
         "take Option A. The rest remains outstanding."),
    )

    def test_a5_10_f2_statement_forms_derive_settled_in_part(self):
        for number, title, paragraph in self.STATEMENT_FORMS:
            with self.subTest(title=title):
                text = ("# Decision queue\n\n" + taught_entry(
                    number, title, [paragraph]))
                _model, output = h.run_pipeline(
                    text.encode("utf-8"))
                self.assertIsNotNone(output)
                entry_id = "DQ-%03d" % number
                self.assertEqual(state_of(output, entry_id),
                                 "Settled in part")
                found = h.entry_by_id(output, entry_id)
                remainder = h.get(found, "remainder_text",
                                  "remainder")
                self.assertTrue(remainder)

    def test_a5_10_f2_statement_combined_figures(self):
        sentences = (
            (1, "Control rest stands open named",
             "Ruled by Captain JP: the first part is ruled, "
             "take Option A. The rest, the second part, "
             "stands open."),
            (4, "Rest bare stands open",
             "Ruled by Captain JP: the first part is ruled, "
             "take Option A. The rest stands open."),
            (7, "Remainder stands undecided named",
             "Ruled by Captain JP: the first part is ruled, "
             "take Option A. The remainder, the second part, "
             "stands undecided."),
            (8, "Remainder bare stays undecided",
             "Ruled by Captain JP: the first part is ruled, "
             "take Option A. The remainder stays undecided."),
        )
        parts = ["# Decision queue\n\n"]
        for number, title, paragraph in sentences:
            parts.append(taught_entry(number, title, [paragraph]))
        for number, title, paragraph in self.STATEMENT_FORMS:
            parts.append(taught_entry(number, title, [paragraph]))
        text = "\n".join(parts)
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        counts = h.canonical_counts(output)
        self.assertEqual(counts.get("Settled in part"), 16)
        self.assertEqual(h.ambiguous_count(output), 0)
        waiting, _blocking = h.waiting_and_blocking(output)
        self.assertEqual(h.int_of(waiting), 16)

    def test_a5_10_f2_own_paragraph_forms_derive_settled_in_part(self):
        parts = ["# Decision queue\n\n"]
        parts.append(taught_entry(
            1, "Control remainder stands open",
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A.",
             "The remainder, the second part, still stands "
             "open."]))
        parts.append(taught_entry(
            2, "Remainder remains outstanding para",
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A.",
             "The remainder remains outstanding."]))
        parts.append(taught_entry(
            3, "Rest is outstanding para",
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A.",
             "The rest is outstanding."]))
        parts.append(taught_entry(
            4, "Remainder stands undecided para",
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A.",
             "The remainder, the second part, stands "
             "undecided."]))
        parts.append(taught_entry(
            5, "Rest is still unresolved para",
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A.",
             "The rest is still unresolved."]))
        parts.append(taught_entry(
            6, "Remainder bare stands open para",
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A.",
             "The remainder stands open."]))
        text = "\n".join(parts)
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        counts = h.canonical_counts(output)
        self.assertEqual(counts.get("Settled in part"), 6)
        self.assertEqual(h.ambiguous_count(output), 0)
        waiting, _blocking = h.waiting_and_blocking(output)
        self.assertEqual(h.int_of(waiting), 6)

    def test_ch67_cured_forms_still_derive_settled_in_part(self):
        # Pin, passing before and after: the CH-67 pins
        # whole, in the statement and own paragraph shapes.
        forms = (
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A. The rest is open."],
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A. The remainder remains pending."],
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A. The rest, the second part, "
             "remains unresolved."],
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A.",
             "The rest remains unresolved."],
        )
        for paragraphs in forms:
            with self.subTest(paragraphs=paragraphs):
                text = ("# Decision queue\n\n" + taught_entry(
                    1, "Cured form", paragraphs))
                _model, output = h.run_pipeline(
                    text.encode("utf-8"))
                self.assertIsNotNone(output)
                self.assertEqual(state_of(output, "DQ-001"),
                                 "Settled in part")

    def test_pin03_part_act_with_no_remainder_is_ambiguous(self):
        # PIN-03 pin, passing before and after.
        text = ("# Decision queue\n\n" + taught_entry(
            1, "Part no remainder",
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A."]))
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        self.assertEqual(state_of(output, "DQ-001"), "Ambiguous")
        self.assertEqual(h.ambiguous_count(output), 1)

    def test_whole_ruling_still_derives_ruled(self):
        # Guard, passing before and after.
        text = ("# Decision queue\n\n" + taught_entry(
            1, "Whole ruling entry",
            ["Ruled by Captain JP: this entry is ruled, "
             "take Option A."]))
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        self.assertEqual(state_of(output, "DQ-001"), "Ruled")


if __name__ == "__main__":
    unittest.main()
