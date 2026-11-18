"""Restart Step 17 fix wave 7, cluster K8 tests.

Charges CH-138 to CH-144, ruled at section 66 of
design/steps/step-17r-record.md, with ruling (f) of that
section on the cost charge CH-144. Every cure stands in
product/decision_queue_validator/validate.py only, at the
Banked head census and its content test.

CH-138 (round 7 attack seat 8, finding F7-8-1): an entry
identifier alone in a further respelled form (an exclamation
mark, quotation marks, angle brackets, a wrapper with
trailing punctuation, an ampersand, hyphen, or word joiner)
states no content and takes no group credit.

CH-139 (F7-8-2): a partial block whose only body is a Source
line in another case, a Landed line closed by a comma, a
Recorded line, or an Origins line states no census content
and takes no group credit, toward PIN-01 form 1.

CH-140 (F7-8-3): a labelled field line in a further respelled
form of a taught label (a no break space or an ideographic
space inside the label, a fullwidth letter at its opening, a
small colon or a modifier letter colon at its close) takes
no group credit.

CH-141 (F7-8-4): a heading shaped line behind a five letter
marker, a double angle character, a rightwards arrow, a
digit and letter marker, or a double tilde wrap takes no
group credit, in group 3 and inside a block.

CH-142 (F7-8-5): a level 4 entry heading in a further non
exact form (a mixed case prefix, an underscore, a no break
space after its colon, a colon with no title, a lower case
R number) takes the orphan treatment at the validate
surfaces.

CH-143 (F7-8-6): two decider lines naming two different
deciders draw the conflict finding where the second line
stands behind a numbered or bullet character marker or
nested markers, carries a no break space inside its verb
phrase, or carries a fullwidth colon.

CH-144 (round 7 attack seat 21, finding A7-21-1, High): the
identifier only line fullmatch in _line_carries_content
backtracks catastrophically on a failing match. The cure
stands at that locus; the tests below rest on the
construction behaviour (a failing identifier run line is
read, in bounded time, as the content it carries, and an
identifier only line still states no content), and the cost
figures in the seat paper stand as measurements only, under
ruling (f). No construction in this file builds the F1
shape, and no banked question is named in any construction.
"""

import os
import subprocess
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


class Ch138IdentifierRound7Test(unittest.TestCase):
    """F7-8-1: an entry identifier alone carrying an
    exclamation mark, standing inside quotation marks, angle
    brackets, or stars, carrying a wrapper with trailing
    punctuation, or joined to a second identifier by an
    ampersand, a hyphen, or the word and states no content
    and takes no group credit."""

    BLOCK_FORMS = (
        "DQ-002!",
        '"DQ-002"',
        "<DQ-002>",
        "(DQ-002),",
        "DQ-002 & DQ-003",
        "DQ-002-DQ-003",
        "*DQ-002*",
        "DQ-002 and DQ-003",
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
            self, banked_block_entry("DQ-002!"))
        self.assertEqual(code, 4)
        self.assertIn("Banked head evidence groups sum to 0",
                      combined)

    def test_round6_and_exact_identifier_pins_stand(self):
        # Pins, passing before and after: the exact form and
        # the CH-103 respelled forms take no credit still.
        for line in ("DQ-002", "DQ-002.", "dq-002", "DQ-002,",
                     "(DQ-002)", "DQ_002", "DQ-002;",
                     "DQ-002, DQ-003", "DQ-002/DQ-003"):
            with self.subTest(line=line):
                _model, output = h.run_pipeline(
                    banked_block_entry(line).encode("utf-8"))
                self.assertIsNotNone(output)
                assert_in_no_group(self, output)

    def test_identifier_beside_words_keeps_content(self):
        # Guards, passing before and after: an identifier
        # standing beside genuine words is prose, on the
        # standing joiners and on the fresh joiners alike.
        for line in ("DQ-002 is the harbour entry",
                     "DQ-002 and the harbour entry",
                     "DQ-002 & the harbour entry"):
            with self.subTest(line=line):
                self.assertEqual(
                    validate._line_carries_content(line), True)


class Ch139PartialBlockRound7Test(unittest.TestCase):
    """F7-8-2: a partial block whose only body is a Source
    line in lower or upper case, a Landed line closed by a
    comma after the word, a Recorded line, or an Origins
    line carries no disposition statement and takes no
    group credit, toward PIN-01 form 1."""

    BLOCK_FORMS = (
        "source: the harbour log.",
        "SOURCE: THE HARBOUR LOG.",
        "Landed, in the harbour log.",
        "Recorded in the harbour log.",
        "Origins: Captain JP raised this question in the "
        "meeting.",
    )

    def test_record_line_only_block_takes_no_group(self):
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

    def test_record_line_only_block_withholds(self):
        code, combined = run_cli_on(
            self, banked_block_entry("source: the harbour "
                                     "log."))
        self.assertEqual(code, 4)
        self.assertIn("Banked head evidence groups sum to 0",
                      combined)

    def test_round6_record_line_pins_stand(self):
        # Pins, passing before and after: the CH-103 record
        # line forms take no credit still.
        for line in ("landed in the harbour log.",
                     "origin: Captain JP raised this question "
                     "in the meeting.",
                     "LANDED IN THE HARBOUR LOG.",
                     "Filed in the harbour log.",
                     "Source: the harbour log."):
            with self.subTest(line=line):
                _model, output = h.run_pipeline(
                    banked_block_entry(line).encode("utf-8"))
                self.assertIsNotNone(output)
                assert_in_no_group(self, output)

    def test_genuine_block_credit_pin_stands(self):
        # Pin, passing before and after: a full ruling block
        # credits group 2, and the date only control takes
        # no credit.
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


class Ch140RespelledLabelRound7Test(unittest.TestCase):
    """F7-8-3: a labelled field line in a further respelled
    form of a taught label (a no break space or an
    ideographic space inside the label, a fullwidth letter
    at its opening, a small colon or a modifier letter
    colon at its close) takes no group credit."""

    PLAIN_FORMS = (
        "Question\u00a0as put: genuine words stand here in a "
        "repeated line.",
        "\uff31uestion: genuine words stand here in a "
        "repeated line.",
        "Question\ufe55 genuine words stand here in a "
        "repeated line.",
        "Question as\u3000put: genuine words stand here in a "
        "repeated line.",
        "Cost\ua789 genuine words stand here in a repeated "
        "line.",
    )

    def test_respelled_plain_forms_take_no_group(self):
        for line in self.PLAIN_FORMS:
            with self.subTest(line=repr(line)):
                _model, output = h.run_pipeline(
                    banked_plain_entry(line).encode("utf-8"))
                self.assertIsNotNone(output)
                assert_in_no_group(self, output)

    def test_labelled_test_reads_the_round7_forms(self):
        for line in self.PLAIN_FORMS:
            with self.subTest(line=repr(line)):
                self.assertEqual(
                    validate._is_open_field_labelled_line(line),
                    True)

    def test_taught_and_round6_label_pins_stand(self):
        # Pins, passing before and after: the taught form
        # itself and the CH-103 forms take no group credit.
        for line in ("Question: genuine words stand here in "
                     "a repeated line.",
                     "Question\uff1a genuine words stand here "
                     "in a repeated line.",
                     "Question\u2009: genuine words stand here "
                     "in a repeated line.",
                     "Question_as_put: genuine words stand "
                     "here in a repeated line."):
            with self.subTest(line=repr(line)):
                self.assertEqual(
                    validate._is_open_field_labelled_line(line),
                    True)

    def test_unrelated_labels_stand_outside_the_taught_set(self):
        # Pins, passing before and after: a lower case note
        # label and a snake case label that respells no
        # taught label stand outside the taught set.
        for line in ("note: genuine words stand here in a "
                     "note line.",
                     "question_text: genuine words stand here "
                     "in a repeated line."):
            with self.subTest(line=line):
                self.assertEqual(
                    validate._is_open_field_labelled_line(line),
                    False)


class Ch141HeadingShapeRound7Test(unittest.TestCase):
    """F7-8-4: a heading shaped line behind a five letter
    marker, a double angle character (U+00BB), a rightwards
    arrow (U+2192), a digit and letter marker, or a double
    tilde wrap takes no group credit, in group 3 and inside
    a block."""

    PLAIN_FORMS = (
        "abcde) #### Ruling by Captain JP",
        "\u00bb #### Ruling by Captain JP",
        "\u2192 #### Ruling by Captain JP",
        "1a) #### Ruling by Captain JP",
        "~~#### Ruling by Captain JP",
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
        line = "abcde) #### Ruling by Captain JP"
        _model, output = h.run_pipeline(
            banked_block_entry(line).encode("utf-8"))
        self.assertIsNotNone(output)
        assert_in_no_group(self, output)

    def test_genuine_prose_behind_the_same_forms_keeps_credit(self):
        # Pins, passing before and after, on the bound of
        # the family: genuine prose behind the same marker
        # and wrap forms keeps its group 3 credit.
        for line in ("abcde) An unheaded paragraph stands "
                     "here.",
                     "\u00bb An unheaded paragraph stands here.",
                     "\u2192 An unheaded paragraph stands here.",
                     "1a) An unheaded paragraph stands here.",
                     "~~An unheaded paragraph stands here."):
            with self.subTest(line=repr(line)):
                self.assertEqual(
                    validate._is_heading_shaped_line(line), False)
                _model, output = h.run_pipeline(
                    banked_plain_entry(line).encode("utf-8"))
                self.assertIsNotNone(output)
                self.assertIn("DQ-001", group_members(
                    output, "unheaded paragraphs"))
                self.assertEqual(sums_agree(output), True)

    def test_round6_marker_pins_stand(self):
        # Pins, passing before and after: the CH-103 marker
        # forms are heading shaped still.
        for line in ("abcd) #### Ruling by Captain JP",
                     "\u2023 #### Ruling by Captain JP",
                     "\u00b7 #### Ruling by Captain JP"):
            with self.subTest(line=repr(line)):
                self.assertEqual(
                    validate._is_heading_shaped_line(line), True)


class Ch142Level4Round7HeadingTest(unittest.TestCase):
    """F7-8-5: a level 4 entry heading in a further non
    exact form (a mixed case entry prefix, an underscore in
    place of the hyphen, a no break space after its colon,
    a colon with no title after it, and an R number heading
    in lower case) takes the orphan treatment at the
    validate surfaces: a PIN-06 Warning naming the heading
    as written, and the entry above foots on its own matter
    only, its Status line never imported in silence."""

    @staticmethod
    def _construction(heading_line):
        return (HEAD + entry("An unheaded paragraph stands "
                             "here.\n")
                + heading_line + "\n\n"
                + "Status: Banked\n\n" + FIELDS
                + "An unheaded paragraph stands here.\n")

    FORMS = (
        "#### Dq-002: Second entry",
        "#### DQ_002: Second entry",
        "#### DQ-002:\u00a0Second entry",
        "#### DQ-002:",
        "#### r-7: Second entry",
    )

    def test_non_exact_headings_take_the_orphan_warning(self):
        for heading_line in self.FORMS:
            with self.subTest(heading=repr(heading_line)):
                code, combined = run_cli_on(
                    self, self._construction(heading_line))
                self.assertEqual(code, 1)
                self.assertIn(
                    "matches no recognised heading form",
                    combined)

    def test_absorbed_status_line_no_longer_moves_the_entry(self):
        for heading_line in self.FORMS:
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

    def test_three_spaces_control_stands_cured(self):
        # Control of the attack paper, passing before and
        # after: the three spaces form stands on the cured
        # side of the CH-103 two spaces reading.
        text = self._construction("#### DQ-002:   Second entry")
        code, combined = run_cli_on(self, text)
        self.assertEqual(code, 1)
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


class Ch143DeciderRound7Test(unittest.TestCase):
    """F7-8-6: two decider lines naming two different
    deciders draw the conflict finding where the second
    line stands behind a numbered list marker or a bullet
    character, carries a no break space inside its verb
    phrase, stands behind nested markers, or carries a
    fullwidth colon after the word by. The space before
    colon bound case and the first two names bound stand
    as recorded."""

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
        "1. Ruled by: Sam\n\n",
        "\u2022 Ruled by: Sam\n\n",
        "Ruled\u00a0by: Sam\n\n",
        "> - Ruled by: Sam\n\n",
        "Ruled by\uff1a Sam\n\n",
    )

    def test_second_decider_round7_forms_take_a_finding(self):
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


def _content_within_bound(line, bound_seconds=20):
    """The content reading of a line, taken in a child
    process under a time bound, so a reading that does not
    finish is killed at the bound. Returns (completed,
    result): completed is False where the reading did not
    finish inside the bound, the failing match behaviour
    charged at CH-144. The bound is a behaviour bound of
    the test, not a cost verdict: ruling (f) of section
    66."""
    driver = (
        "import sys\n"
        "from decision_queue_validator import validate\n"
        "print(validate._line_carries_content(sys.argv[1]))\n")
    env = dict(os.environ)
    env["PYTHONPATH"] = str(h.PRODUCT_ROOT)
    try:
        proc = subprocess.run(
            [os.sys.executable, "-c", driver, line],
            cwd=str(h.PRODUCT_ROOT), env=env,
            capture_output=True, text=True,
            timeout=bound_seconds)
    except subprocess.TimeoutExpired:
        return False, None
    return True, proc.stdout.strip() == "True"


def _identifier_run(count):
    return ", ".join("DQ-%03d" % number
                     for number in range(1, count + 1))


class Ch144FullmatchCostTest(unittest.TestCase):
    """A7-21-1: the identifier only line reading on a
    failing match. A governed list first statement line,
    a run of identifiers closing in words, is read as the
    content it carries and the reading completes; an
    identifier only line of the same run still states no
    content. The verdict rests on this behaviour and on
    the governed pins; cost figures stand as measurements
    in the seat paper only, under ruling (f)."""

    def test_failing_run_of_30_identifiers_reads_as_content(self):
        line = (_identifier_run(30)
                + " are the superseded entries.")
        completed, result = _content_within_bound(line)
        self.assertTrue(completed)
        self.assertEqual(result, True)

    def test_failing_run_of_100_identifiers_reads_as_content(self):
        line = (_identifier_run(100)
                + " are the superseded entries.")
        completed, result = _content_within_bound(line)
        self.assertTrue(completed)
        self.assertEqual(result, True)

    def test_failing_run_closed_by_a_separator_reads_as_content(self):
        line = _identifier_run(50) + ", and the rest follows."
        completed, result = _content_within_bound(line)
        self.assertTrue(completed)
        self.assertEqual(result, True)

    def test_identifier_only_long_list_still_states_no_content(self):
        # Pin in behaviour, passing before and after on its
        # matching form: an identifier only list completes
        # and states no content at either size.
        for count in (30, 100):
            with self.subTest(count=count):
                completed, result = _content_within_bound(
                    _identifier_run(count))
                self.assertTrue(completed)
                self.assertEqual(result, False)

    def test_list_first_statement_file_completes(self):
        # The governed construction end to end: one Banked
        # head entry whose only body line is a list first
        # statement naming 30 targets and closing in words.
        # The run completes inside the harness timeout, the
        # entry foots in group 3 on the content the line
        # carries, and the census sums agree.
        text = banked_plain_entry(
            _identifier_run(30) + " are the superseded "
            "entries.")
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "case.md"
            target.write_bytes(text.encode("utf-8"))
            try:
                code, out, err = h.run_cli_with_timeout(
                    "validate", target, timeout=30)
            except subprocess.TimeoutExpired:
                self.fail("the validate run did not complete "
                          "inside 30 seconds on the list first "
                          "statement construction")
        combined = (out + err).decode("utf-8", errors="replace")
        self.assertEqual(code, 0)
        self.assertIn("unheaded paragraphs only: 1 entry",
                      combined)
        self.assertIn("DQ-001", combined)


if __name__ == "__main__":
    unittest.main()
