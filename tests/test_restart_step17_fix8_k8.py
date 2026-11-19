"""Restart Step 17 fix wave 8, cluster K8 tests.

Charges CH-170 to CH-172 and CH-180 to CH-182, ruled TO
FIX at section 77 of design/steps/step-17r-record.md.
Every cure stands in
product/decision_queue_validator/validate.py only, at the
Banked head census and its content test.

CH-180 (round 8 attack seat 8, finding F8-8-1, T8-27): an
entry identifier alone carrying a question mark, standing
inside a tilde, backtick, curly quote, or underscore
wrapper, carrying two punctuation marks after a closing
wrapper, or joined to a second identifier by the word or
or a plus sign states no content and takes no group credit.

CH-170 (F8-8-2, T8-17): a partial block whose only body is
a Filed or Recorded line closed by a comma, a Source line
closed by a comma or in its plural form, or a Landed line
closed by a semicolon states no census content and takes
no group credit, toward PIN-01 form 1.

CH-171 (F8-8-3, T8-18): a labelled field line in a further
respelled form of a taught label (a thin space or a hair
space inside the label, a Greek omicron or a Cyrillic ie
inside the label, or a ratio sign at its close) takes no
group credit.

CH-181 (F8-8-4, T8-28): a heading shaped line behind a six
letter marker, a small triangular bullet, a double
rightwards arrow, a letter and digit marker, or a backtick
wrap takes no group credit, in group 3 and inside a block.

CH-172 (F8-8-5, T8-19): a level 4 entry heading in a
further non exact form (an en dash or a fullwidth hyphen
in place of its hyphen, an ideographic space after its
colon, an R number heading with no hyphen, or a mixed case
prefix with an underscore) takes the orphan treatment at
the validate surfaces.

CH-182 (F8-8-6, T8-29): two decider lines naming two
different deciders draw the conflict finding where the
second line stands behind a six letter marker or a small
triangular bullet, carries an ideographic space inside
its verb phrase, or carries a small colon or a modifier
letter colon after the word by.

No construction in this file builds the F1 shape, and no
banked question is named in any construction. The
Ch144FullmatchCostTest class is not run by this seat in
any form.
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


class Ch180IdentifierRound8Test(unittest.TestCase):
    """F8-8-1: the round 8 identifier forms state no
    content and take no group credit."""

    BLOCK_FORMS = (
        "DQ-002?",
        "(DQ-002)!!",
        "~DQ-002~",
        "`DQ-002`",
        "DQ-002 or DQ-003",
        "DQ-002 + DQ-003",
        "\u201cDQ-002\u201d",
        "_DQ-002_",
    )

    def test_identifier_forms_in_block_take_no_group(self):
        for line in self.BLOCK_FORMS:
            with self.subTest(line=repr(line)):
                _model, output = h.run_pipeline(
                    banked_block_entry(line).encode("utf-8"))
                self.assertIsNotNone(output)
                assert_in_no_group(self, output)

    def test_content_test_reads_the_forms_empty(self):
        for line in self.BLOCK_FORMS:
            with self.subTest(line=repr(line)):
                self.assertEqual(
                    validate._line_carries_content(line), False)

    def test_identifier_form_withholds_the_run(self):
        code, combined = run_cli_on(
            self, banked_block_entry("DQ-002?"))
        self.assertEqual(code, 4)
        self.assertIn("Banked head evidence groups sum to 0",
                      combined)

    def test_round7_and_exact_identifier_pins_stand(self):
        for line in ("DQ-002", "DQ-002!", '"DQ-002"',
                     "<DQ-002>", "(DQ-002),", "DQ-002 & DQ-003",
                     "DQ-002-DQ-003", "*DQ-002*",
                     "DQ-002 and DQ-003"):
            with self.subTest(line=line):
                _model, output = h.run_pipeline(
                    banked_block_entry(line).encode("utf-8"))
                self.assertIsNotNone(output)
                assert_in_no_group(self, output)

    def test_identifier_beside_words_keeps_content(self):
        for line in ("DQ-002 is the harbour entry",
                     "DQ-002 or the harbour entry",
                     "DQ-002 + the harbour entry",
                     "DQ-002 and the harbour entry"):
            with self.subTest(line=line):
                self.assertEqual(
                    validate._line_carries_content(line), True)


class Ch170PartialBlockRound8Test(unittest.TestCase):
    """F8-8-2: the round 8 record lines state no census
    content and take no group credit."""

    BLOCK_FORMS = (
        "Filed, in the harbour log.",
        "Recorded, in the harbour log.",
        "Source, the harbour log.",
        "Sources: the harbour log.",
        "Landed; in the harbour log.",
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
            self, banked_block_entry("Filed, in the harbour "
                                     "log."))
        self.assertEqual(code, 4)
        self.assertIn("Banked head evidence groups sum to 0",
                      combined)

    def test_round7_record_line_pins_stand(self):
        for line in ("source: the harbour log.",
                     "Landed, in the harbour log.",
                     "Recorded in the harbour log.",
                     "Origins: Captain JP raised this question "
                     "in the meeting.",
                     "Filed in the harbour log.",
                     "Source: the harbour log."):
            with self.subTest(line=line):
                _model, output = h.run_pipeline(
                    banked_block_entry(line).encode("utf-8"))
                self.assertIsNotNone(output)
                assert_in_no_group(self, output)

    def test_genuine_block_credit_pin_stands(self):
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


class Ch171RespelledLabelRound8Test(unittest.TestCase):
    """F8-8-3: the round 8 label forms take no group
    credit."""

    PLAIN_FORMS = (
        "Question\u2009as put: genuine words stand here in a "
        "repeated line.",
        "Cost\u200aof deciding late: genuine words stand "
        "here in a repeated line.",
        "Questi\u03bfn: genuine words stand here in a "
        "repeated line.",
        "Qu\u0435stion: genuine words stand here in a "
        "repeated line.",
        "Question\u2236 genuine words stand here in a "
        "repeated line.",
    )

    def test_respelled_plain_forms_take_no_group(self):
        for line in self.PLAIN_FORMS:
            with self.subTest(line=repr(line)):
                _model, output = h.run_pipeline(
                    banked_plain_entry(line).encode("utf-8"))
                self.assertIsNotNone(output)
                assert_in_no_group(self, output)

    def test_labelled_test_reads_the_round8_forms(self):
        for line in self.PLAIN_FORMS:
            with self.subTest(line=repr(line)):
                self.assertEqual(
                    validate._is_open_field_labelled_line(line),
                    True)

    def test_taught_and_round7_label_pins_stand(self):
        for line in ("Question: genuine words stand here in "
                     "a repeated line.",
                     "Question\u00a0as put: genuine words stand "
                     "here in a repeated line.",
                     "\uff31uestion: genuine words stand here "
                     "in a repeated line.",
                     "Question\ufe55 genuine words stand here "
                     "in a repeated line.",
                     "Question as\u3000put: genuine words stand "
                     "here in a repeated line."):
            with self.subTest(line=repr(line)):
                self.assertEqual(
                    validate._is_open_field_labelled_line(line),
                    True)

    def test_unrelated_labels_stand_outside_the_taught_set(self):
        for line in ("note: genuine words stand here in a "
                     "note line.",
                     "question_text: genuine words stand here "
                     "in a repeated line."):
            with self.subTest(line=line):
                self.assertEqual(
                    validate._is_open_field_labelled_line(line),
                    False)


class Ch181HeadingShapeRound8Test(unittest.TestCase):
    """F8-8-4: the round 8 heading forms take no group
    credit, in group 3 and inside a block."""

    PLAIN_FORMS = (
        "abcdef) #### Ruling by Captain JP",
        "\u25b8 #### Ruling by Captain JP",
        "\u21d2 #### Ruling by Captain JP",
        "a1) #### Ruling by Captain JP",
        "`#### Ruling by Captain JP",
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
        line = "abcdef) #### Ruling by Captain JP"
        _model, output = h.run_pipeline(
            banked_block_entry(line).encode("utf-8"))
        self.assertIsNotNone(output)
        assert_in_no_group(self, output)

    def test_genuine_prose_behind_the_same_forms_keeps_credit(self):
        for line in ("abcdef) An unheaded paragraph stands "
                     "here.",
                     "\u25b8 An unheaded paragraph stands here.",
                     "\u21d2 An unheaded paragraph stands here.",
                     "a1) An unheaded paragraph stands here.",
                     "`An unheaded paragraph stands here.`"):
            with self.subTest(line=repr(line)):
                self.assertEqual(
                    validate._is_heading_shaped_line(line), False)
                _model, output = h.run_pipeline(
                    banked_plain_entry(line).encode("utf-8"))
                self.assertIsNotNone(output)
                self.assertIn("DQ-001", group_members(
                    output, "unheaded paragraphs"))
                self.assertEqual(sums_agree(output), True)

    def test_round7_marker_pins_stand(self):
        for line in ("abcde) #### Ruling by Captain JP",
                     "\u00bb #### Ruling by Captain JP",
                     "\u2192 #### Ruling by Captain JP",
                     "1a) #### Ruling by Captain JP",
                     "~~#### Ruling by Captain JP"):
            with self.subTest(line=repr(line)):
                self.assertEqual(
                    validate._is_heading_shaped_line(line), True)


class Ch172Level4Round8HeadingTest(unittest.TestCase):
    """F8-8-5: the round 8 non exact heading forms take the
    orphan treatment at the validate surfaces."""

    @staticmethod
    def _construction(heading_line):
        return (HEAD + entry("An unheaded paragraph stands "
                             "here.\n")
                + heading_line + "\n\n"
                + "Status: Banked\n\n" + FIELDS
                + "An unheaded paragraph stands here.\n")

    FORMS = (
        "#### DQ\u2013002: Second entry",
        "#### DQ\uff0d002: Second entry",
        "#### DQ-002:\u3000Second entry",
        "#### R7: Second entry",
        "#### Dq_002: Second entry",
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

    def test_round7_heading_pins_stand(self):
        for heading_line in ("#### Dq-002: Second entry",
                             "#### DQ_002: Second entry",
                             "#### DQ-002:\u00a0Second entry",
                             "#### DQ-002:",
                             "#### r-7: Second entry",
                             "#### DQ-002: Second entry",
                             "#### DQ-002:   Second entry"):
            with self.subTest(heading=repr(heading_line)):
                code, combined = run_cli_on(
                    self, self._construction(heading_line))
                self.assertEqual(code, 1)
                self.assertIn(
                    "matches no recognised heading form",
                    combined)

    def test_genuine_decision_block_heading_stands(self):
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


class Ch182DeciderRound8Test(unittest.TestCase):
    """F8-8-6: the round 8 second decider forms draw the
    conflict finding. The space before colon bound case and
    the first two names bound stand as recorded."""

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
        "abcdef) Ruled by: Sam\n\n",
        "\u25b8 Ruled by: Sam\n\n",
        "Ruled\u3000by: Sam\n\n",
        "Ruled by\ufe55 Sam\n\n",
        "Ruled by\ua789 Sam\n\n",
    )

    def test_second_decider_round8_forms_take_a_finding(self):
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

    def test_round7_decider_pins_stand(self):
        for second in ("Ruled by: Sam\n\n",
                       "1. Ruled by: Sam\n\n",
                       "\u2022 Ruled by: Sam\n\n",
                       "Ruled\u00a0by: Sam\n\n",
                       "> - Ruled by: Sam\n\n",
                       "Ruled by\uff1a Sam\n\n"):
            with self.subTest(second=repr(second)):
                text = self._run(second)
                _model, output = h.run_pipeline(
                    text.encode("utf-8"))
                self.assertIsNotNone(output)
                self.assertEqual(
                    len(self._conflict_findings(output)), 1)

    def test_exact_repetition_pin_stands(self):
        text = self._run("Ruled by: Captain JP\n\n")
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        self.assertEqual(self._conflict_findings(output), [])
        code, _combined = run_cli_on(self, text)
        self.assertEqual(code, 0)

    def test_space_before_colon_bound_case_takes_no_conflict(self):
        text = self._run("Ruled by : Sam\n\n")
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        self.assertEqual(self._conflict_findings(output), [])

    def test_three_deciders_name_the_first_two_only(self):
        text = self._run("Ruled by: Sam\n\nRuled by: Alex\n\n")
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        conflicts = self._conflict_findings(output)
        self.assertEqual(len(conflicts), 1)
        statement = h.finding_statement(conflicts[0])
        self.assertIn("Captain JP", statement)
        self.assertIn("Sam", statement)
        self.assertNotIn("Alex", statement)


if __name__ == "__main__":
    unittest.main()
