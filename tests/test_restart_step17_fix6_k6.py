"""Restart Step 17 fix wave 6, cluster K6 tests.

Charges CH-103, CH-105, and CH-106, ruled at section 58 of
design/steps/step-17r-record.md and prepared at
design/steps/step-17r-triage6-prep.md. Every cure stands in
product/decision_queue_validator/validate.py only.

CH-103 (round 6 attack seat 8, findings F6-8-1 to F6-8-6):
the Banked head evidence groups and the decider conflict
limb, round 6 limbs. An entry identifier alone in a further
respelled form takes no group credit; a partial block whose
only body is a case respelled landed or Origin line, or a
Filed or Source record line, takes no group credit; a
taught field label respelled by a fullwidth colon, a thin
space, underscores, or a zero width space takes no group
credit; a heading shaped line behind a four letter marker,
a triangular bullet, or a middle dot takes no group credit;
a level 4 entry heading in a further non exact form takes
the orphan treatment at the census and findings surfaces of
validate; and a second decider line behind a bullet or
blockquote marker, with a respaced verb phrase, or with its
value after a blank line draws the decider conflict
finding. The Devanagari digit control of the attack paper
stands cured at the orphan reading only, as an observation
pin, and the digit ground stands unmoved.

CH-105 (round 6 attack seat 10, finding A6-10-F1): the
blocking figure no item values, round 6 limbs, 26 fresh
phrase, wrapper, and joiner forms. The D2 blocking
narrowing pin and the O4 corpus bound stand whole, and the
no space ampersand form stands at its measured standing,
outside the charge.

CH-106 (round 6 attack seat 10, finding A6-10-F2): part
scope remainder verb widths, round 6 limbs. Remainder
statements in fresh verb forms are read in the statement
and in their own paragraph alike. The CH-85, CH-86, and
CH-87 pins whole stand. No construction in this file
builds the F1 shape, and no banked question is named in
any construction.
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


class Ch103IdentifierRound6Test(unittest.TestCase):
    """F6-8-1: an entry identifier alone carrying trailing
    punctuation, a wrapper, an underscore, or a punctuation
    joined second identifier states no content and takes no
    group credit."""

    BLOCK_FORMS = (
        "DQ-002,",
        "(DQ-002)",
        "DQ_002",
        "DQ-002;",
        "DQ-002, DQ-003",
        "DQ-002/DQ-003",
    )

    def test_identifier_forms_in_block_take_no_group(self):
        for line in self.BLOCK_FORMS:
            with self.subTest(line=line):
                _model, output = h.run_pipeline(
                    banked_block_entry(line).encode("utf-8"))
                self.assertIsNotNone(output)
                assert_in_no_group(self, output)

    def test_content_test_reads_the_forms_empty(self):
        for line in self.BLOCK_FORMS:
            with self.subTest(line=line):
                self.assertEqual(
                    validate._line_carries_content(line), False)

    def test_identifier_form_withholds_the_run(self):
        code, combined = run_cli_on(
            self, banked_block_entry("DQ-002,"))
        self.assertEqual(code, 4)
        self.assertIn("Banked head evidence groups sum to 0",
                      combined)

    def test_exact_identifier_pin_stands(self):
        # Pin, passing before and after: the exact form and
        # the round 5 respelled forms take no credit still.
        for line in ("DQ-002", "DQ-002.", "dq-002"):
            with self.subTest(line=line):
                _model, output = h.run_pipeline(
                    banked_block_entry(line).encode("utf-8"))
                self.assertIsNotNone(output)
                assert_in_no_group(self, output)

    def test_identifier_beside_words_keeps_content(self):
        # Guard, passing before and after: an identifier
        # standing inside genuine prose is prose.
        self.assertEqual(
            validate._line_carries_content(
                "DQ-002 is the harbour entry"), True)
        self.assertEqual(validate._line_carries_content("ab1 cd2"),
                         True)


class Ch103PartialBlockRound6Test(unittest.TestCase):
    """F6-8-2: a partial block whose only body is a landed
    or Origin line in a case respelled form, or a Filed or
    Source record line, carries no disposition statement
    and takes no group credit, toward PIN-01 form 1."""

    BLOCK_FORMS = (
        "landed in the harbour log.",
        "origin: Captain JP raised this question in the "
        "meeting.",
        "LANDED IN THE HARBOUR LOG.",
        "Filed in the harbour log.",
        "Source: the harbour log.",
    )

    def test_record_line_only_block_takes_no_group(self):
        for line in self.BLOCK_FORMS:
            with self.subTest(line=line):
                _model, output = h.run_pipeline(
                    banked_block_entry(line).encode("utf-8"))
                self.assertIsNotNone(output)
                assert_in_no_group(self, output)

    def test_record_line_only_block_withholds(self):
        code, combined = run_cli_on(
            self, banked_block_entry("landed in the harbour "
                                     "log."))
        self.assertEqual(code, 4)
        self.assertIn("Banked head evidence groups sum to 0",
                      combined)

    def test_genuine_block_credit_pins_stand(self):
        # Pins, passing before and after: a full ruling
        # block credits group 2, and the date only control
        # takes no credit.
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
            banked_block_entry("2026-11-17").encode("utf-8"))
        self.assertIsNotNone(output)
        assert_in_no_group(self, output)


class Ch103RespelledLabelRound6Test(unittest.TestCase):
    """F6-8-3: a labelled field line in a further respelled
    form of a taught label (a fullwidth colon, a thin space
    before the colon, underscores in place of the label
    spaces, a zero width space inside the word) takes no
    group credit."""

    PLAIN_FORMS = (
        "Question\uff1a genuine words stand here in a repeated "
        "line.",
        "Question\u2009: genuine words stand here in a repeated "
        "line.",
        "Question_as_put: genuine words stand here in a "
        "repeated line.",
        "Ques\u200btion: genuine words stand here in a repeated "
        "line.",
    )

    def test_respelled_plain_forms_take_no_group(self):
        for line in self.PLAIN_FORMS:
            with self.subTest(line=repr(line)):
                _model, output = h.run_pipeline(
                    banked_plain_entry(line).encode("utf-8"))
                self.assertIsNotNone(output)
                assert_in_no_group(self, output)

    def test_labelled_test_reads_the_round6_forms(self):
        for line in self.PLAIN_FORMS:
            with self.subTest(line=repr(line)):
                self.assertEqual(
                    validate._is_open_field_labelled_line(line),
                    True)

    def test_taught_label_pin_stands(self):
        # Pin, passing before and after: the taught form
        # itself takes no group credit.
        line = ("Question: genuine words stand here in a "
                "repeated line.")
        self.assertEqual(
            validate._is_open_field_labelled_line(line), True)
        _model, output = h.run_pipeline(
            banked_plain_entry(line).encode("utf-8"))
        self.assertIsNotNone(output)
        assert_in_no_group(self, output)

    def test_unrelated_labels_stand_outside_the_taught_set(self):
        # Pins, passing before and after: a lower case note
        # label and a snake case label that respells no
        # taught label stand outside the taught set, the
        # snake case pin standing beside the underscore
        # cure of this round.
        for line in ("note: genuine words stand here in a "
                     "note line.",
                     "question_text: genuine words stand here "
                     "in a repeated line."):
            with self.subTest(line=line):
                self.assertEqual(
                    validate._is_open_field_labelled_line(line),
                    False)


class Ch103HeadingShapeRound6Test(unittest.TestCase):
    """F6-8-4: a heading shaped line behind a four letter
    marker, a triangular bullet (U+2023), or a middle dot
    (U+00B7) takes no group credit, in group 3 and inside
    a block."""

    PLAIN_FORMS = (
        "abcd) #### Ruling by Captain JP",
        "\u2023 #### Ruling by Captain JP",
        "\u00b7 #### Ruling by Captain JP",
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
        line = "abcd) #### Ruling by Captain JP"
        _model, output = h.run_pipeline(
            banked_block_entry(line).encode("utf-8"))
        self.assertIsNotNone(output)
        assert_in_no_group(self, output)

    def test_genuine_prose_behind_the_same_forms_keeps_credit(self):
        # Pins, passing before and after, on the bound of
        # the family: genuine prose behind the same marker
        # forms keeps its group 3 credit.
        for line in ("abcd) An unheaded paragraph stands here.",
                     "\u2023 An unheaded paragraph stands here.",
                     "\u00b7 An unheaded paragraph stands here."):
            with self.subTest(line=repr(line)):
                self.assertEqual(
                    validate._is_heading_shaped_line(line), False)
                _model, output = h.run_pipeline(
                    banked_plain_entry(line).encode("utf-8"))
                self.assertIsNotNone(output)
                self.assertIn("DQ-001", group_members(
                    output, "unheaded paragraphs"))
                self.assertEqual(sums_agree(output), True)


class Ch103Level4Round6HeadingTest(unittest.TestCase):
    """F6-8-5: a level 4 entry heading in a further non
    exact form (a space before the colon, two spaces after
    it, a lower case entry prefix, a fullwidth colon, a tab
    after the colon, and no colon at all) takes the orphan
    treatment at the validate surfaces: a PIN-06 Warning
    naming the heading as written, and the entry above
    foots on its own matter only, its Status line never
    imported in silence."""

    @staticmethod
    def _construction(heading_line):
        return (HEAD + entry("An unheaded paragraph stands "
                             "here.\n")
                + heading_line + "\n\n"
                + "Status: Banked\n\n" + FIELDS
                + "An unheaded paragraph stands here.\n")

    FORMS = (
        ("#### DQ-002 : Second entry", "DQ-002 : Second entry"),
        ("#### DQ-002:  Second entry", "DQ-002:  Second entry"),
        ("#### dq-002: Second entry", "dq-002: Second entry"),
        ("#### DQ-002\uff1a Second entry",
         "DQ-002\uff1a Second entry"),
        ("#### DQ-002:\tSecond entry", "DQ-002:"),
        ("#### DQ-002 Second entry", "DQ-002 Second entry"),
    )

    def test_non_exact_headings_take_the_orphan_warning(self):
        for heading_line, heading_text in self.FORMS:
            with self.subTest(heading=repr(heading_line)):
                code, combined = run_cli_on(
                    self, self._construction(heading_line))
                self.assertEqual(code, 1)
                self.assertIn(heading_text, combined)
                self.assertIn(
                    "matches no recognised heading form",
                    combined)

    def test_absorbed_status_line_no_longer_moves_the_entry(self):
        for heading_line, _text in self.FORMS:
            with self.subTest(heading=repr(heading_line)):
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
        # Pin, passing before and after: the cured exact
        # form keeps its Warning and its group 3 footing.
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

    def test_devanagari_digit_control_stands_cured(self):
        # Observation pin of the attack paper, passing
        # before and after: the Devanagari digit heading
        # stands cured at the orphan reading only, and no
        # number is read from it as data.
        text = self._construction(
            "#### DQ-\u0966\u0966\u0968: Second entry")
        code, combined = run_cli_on(self, text)
        self.assertEqual(code, 1)
        self.assertIn("matches no recognised heading form",
                      combined)
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        self.assertIn("DQ-001", group_members(
            output, "unheaded paragraphs"))

    def test_r_number_other_title_pin_stands(self):
        # Pin, passing before and after: the R number
        # heading with a second entry title keeps its
        # Warning and group 3 footing.
        text = self._construction("#### R-7: Second entry")
        code, combined = run_cli_on(self, text)
        self.assertEqual(code, 1)
        self.assertIn("matches no recognised heading form",
                      combined)

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


class Ch103DeciderRound6Test(unittest.TestCase):
    """F6-8-6: two decider lines naming two different
    deciders draw the conflict finding where the second
    line stands behind a bullet or blockquote marker,
    carries a respaced verb phrase, or carries its value
    after a blank line. The space before colon bound case
    and the first two names bound stand as recorded."""

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

    SECOND_FORMS = (
        "- Ruled by: Sam\n\n",
        "Ruled  by: Sam\n\n",
        "Ruled by:\n\nSam\n\n",
        "Ruled\tby: Sam\n\n",
        "> Ruled by: Sam\n\n",
    )

    def test_second_decider_round6_forms_take_a_finding(self):
        for second in self.SECOND_FORMS:
            with self.subTest(second=repr(second)):
                text = self._run(second)
                _model, output = h.run_pipeline(
                    text.encode("utf-8"))
                self.assertIsNotNone(output)
                conflicts = self._conflict_findings(output)
                self.assertEqual(len(conflicts), 1)
                statement = h.finding_statement(conflicts[0])
                self.assertIn("Captain JP", statement)
                self.assertIn("Sam", statement)
                self.assertIn("DQ-001", group_members(
                    output, "level 4 decision block"))
                code, _combined = run_cli_on(self, text)
                self.assertEqual(code, 1)

    def test_exact_form_conflict_pin_stands(self):
        # Pin, passing before and after: the cured exact
        # form takes its one conflict finding.
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
        # Bound case of the family, passing before and
        # after: the space before colon form is no decider
        # line of the colon form, and draws no conflict
        # finding.
        text = self._run("Ruled by : Sam\n\n")
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        self.assertEqual(self._conflict_findings(output), [])

    def test_three_deciders_name_the_first_two_only(self):
        # Bound of the limb, passing before and after: at
        # most the first two distinct names are named.
        text = self._run("Ruled by: Sam\n\nRuled by: Alex\n\n")
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        conflicts = self._conflict_findings(output)
        self.assertEqual(len(conflicts), 1)
        statement = h.finding_statement(conflicts[0])
        self.assertIn("Captain JP", statement)
        self.assertIn("Sam", statement)
        self.assertNotIn("Alex", statement)


class Ch105BlockingRound6Test(unittest.TestCase):
    """CH-105, A6-10-F1: the blocking figure no item
    values, round 6 limbs."""

    FRESH_NO_ITEM_VALUES = (
        "zilch",
        "nada",
        "no blockage",
        "unobstructed",
        "nothing obstructs",
        "no obstruction",
        "nothing is blocked",
        "zero entries blocked",
        "no item blocks",
        "does not block",
        "all clear",
        "no impediments",
        "nothing impedes",
        "free of blockers",
        "blocked by none",
        "no entries blocked",
        "no blocking entries",
        "nothing blocks anything",
        "0 entries",
        "zero entries",
        "_none_",
        "<none>",
        "none - nothing",
        "none = nothing",
        "none @ nothing",
        "none # nothing",
    )

    def test_a6_10_f1_each_fresh_no_item_value_does_not_count(self):
        for value in self.FRESH_NO_ITEM_VALUES:
            with self.subTest(value=value):
                text = ("# Decision queue\n\n"
                        + open_entry(1, value))
                _output, blocking = blocking_of(text)
                self.assertEqual(blocking, 0)

    def test_a6_10_f1_combined_figure(self):
        values = (
            "zilch",
            "no blockage",
            "_none_",
            "none&nothing",
            "0 entries",
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

    def test_a6_10_f1_same_edge_under_what_it_blocks_label(self):
        text = ("# Decision queue\n\n"
                + open_entry(1, "DQ-002")
                + "\n"
                + open_entry(2, "zilch",
                             label="What it blocks"))
        _output, blocking = blocking_of(text)
        self.assertEqual(blocking, 1)

    def test_no_space_ampersand_standing_unchanged(self):
        # Observation O3 of the attack paper, passing before
        # and after, excluded from the charge and from the
        # scale figure: the no space ampersand value stands
        # excluded on this tree.
        text = ("# Decision queue\n\n"
                + open_entry(1, "none&nothing"))
        _output, blocking = blocking_of(text)
        self.assertEqual(blocking, 0)

    def test_ch86_and_ch66_pins_whole_stand(self):
        # Pins, passing before and after: the CH-86 and
        # CH-66 charged forms keep their cured outcome.
        for value in ("nothing blocked", "zero blockers",
                      "none | nothing", "[none]",
                      "none recorded", "no blockers",
                      "blocks nothing", "none whatsoever",
                      "zero items", "0", "(none)",
                      "none/nothing", "n.a.", "nothing at all",
                      "none at all", "nothing whatsoever",
                      "n/a", "not applicable", "no entries",
                      "nil", "empty", "Nothing.."):
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
                      "none | DQ-002", "DQ-002 ~ none",
                      "DQ-002 - none", "none = DQ-002"):
            with self.subTest(value=value):
                text = ("# Decision queue\n\n"
                        + open_entry(1, value))
                _output, blocking = blocking_of(text)
                self.assertEqual(blocking, 1)


class Ch106RemainderRound6Test(unittest.TestCase):
    """CH-106, A6-10-F2: part scope remainder verb widths,
    round 6 limbs, in the statement and in the own
    paragraph shapes alike."""

    STATEMENT_FORMS = (
        (2, "Rest bare is pending",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The rest is pending."),
        (3, "Remainder named is pending",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The remainder, the second part, "
         "is pending."),
        (4, "Remainder bare is undecided",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The remainder is undecided."),
        (5, "Rest named is undecided",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The rest, the second part, "
         "is undecided."),
        (6, "Remainder stands pending",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The remainder stands pending."),
        (7, "Rest stays outstanding",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The rest stays outstanding."),
        (8, "Remainder named is still outstanding",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The remainder, the second part, "
         "is still outstanding."),
        (9, "Remainder bare remains undecided",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The remainder remains undecided."),
        (10, "Rest is not yet decided",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The rest is not yet decided."),
        (11, "Remainder awaits a decision",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The remainder awaits a decision."),
        (12, "Rest named is awaiting decision",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The rest, the second part, "
         "is awaiting decision."),
        (13, "Remainder has yet to be decided",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The remainder has yet to be "
         "decided."),
        (14, "Rest is left undecided",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The rest is left undecided."),
        (15, "Remainder named stands unresolved",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The remainder, the second part, "
         "stands unresolved."),
        (16, "Rest is held open",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The rest is held open."),
        (17, "Remainder continues to remain open",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The remainder continues to remain "
         "open."),
        (18, "Settled rest is pending mirror",
         "Settled by Captain JP: the first part is settled, "
         "take Option A. The rest is pending."),
    )

    def test_a6_10_f2_statement_forms_derive_settled_in_part(self):
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

    def test_a6_10_f2_statement_combined_figures(self):
        parts = ["# Decision queue\n\n"]
        parts.append(taught_entry(
            1, "Control rest stands open named",
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A. The rest, the second part, "
             "stands open."]))
        for number, title, paragraph in self.STATEMENT_FORMS:
            parts.append(taught_entry(number, title, [paragraph]))
        text = "\n".join(parts)
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        counts = h.canonical_counts(output)
        self.assertEqual(counts.get("Settled in part"), 18)
        self.assertEqual(h.ambiguous_count(output), 0)
        waiting, _blocking = h.waiting_and_blocking(output)
        self.assertEqual(h.int_of(waiting), 18)

    def test_a6_10_f2_own_paragraph_forms_derive_settled_in_part(self):
        parts = ["# Decision queue\n\n"]
        parts.append(taught_entry(
            1, "Control remainder stands open",
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A.",
             "The remainder, the second part, still stands "
             "open."]))
        parts.append(taught_entry(
            2, "Rest is pending para",
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A.",
             "The rest is pending."]))
        parts.append(taught_entry(
            3, "Remainder is undecided para",
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A.",
             "The remainder is undecided."]))
        parts.append(taught_entry(
            4, "Remainder awaits a decision para",
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A.",
             "The remainder awaits a decision."]))
        parts.append(taught_entry(
            5, "Remainder named stands unresolved para",
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A.",
             "The remainder, the second part, stands "
             "unresolved."]))
        parts.append(taught_entry(
            6, "Rest stays outstanding para",
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A.",
             "The rest stays outstanding."]))
        text = "\n".join(parts)
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        counts = h.canonical_counts(output)
        self.assertEqual(counts.get("Settled in part"), 6)
        self.assertEqual(h.ambiguous_count(output), 0)
        waiting, _blocking = h.waiting_and_blocking(output)
        self.assertEqual(h.int_of(waiting), 6)

    def test_ch87_cured_forms_still_derive_settled_in_part(self):
        # Pin, passing before and after: the CH-87 pins
        # whole, in the statement and own paragraph shapes.
        forms = (
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A. The remainder awaits decision."],
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A. The remainder stands undecided."],
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A.",
             "The rest is still unresolved."],
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
