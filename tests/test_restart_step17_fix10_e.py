"""Restart Step 17 fix wave 10, Fix Seat E tests.

Charges CH-249 to CH-255, ruled TO FIX at section 83
ruling (a) of design/steps/step-17r-record.md, in the
charge split of design/steps/step-17r-r10-triage-prep.md
section 3, Cluster E. Every cure stands in
product/decision_queue_validator/validate.py only, at the
Banked head census and its content test.

CH-249 (round 10 attack seat 8, finding F10-8-2, T10-19):
a partial block whose only body is a Recorded, Origin,
or Source line closed by a full stop, a Landed line
closed by a full stop, a Filed line closed by an
exclamation mark, or an Origin line closed by a comma,
states no census content and takes no group credit,
toward PIN-01 form 1. The plural Sources line closed by
a semicolon (case X13) stands as a pin.

CH-250 (F10-8-3, T10-20): a labelled field line in a
further respelled form of a taught label (an em space,
an en space, a six per em space, or a medium
mathematical space inside the label, a Cyrillic o or a
Cyrillic er inside a label, or a Cyrillic capital Es at
its head) takes no group credit.

CH-251 (F10-8-5, T10-21): a level 4 entry heading in a
further non exact form (a non breaking hyphen, an em
dash character, a horizontal bar, or a small hyphen
minus in place of its hyphen, or a mixed case prefix
with a fullwidth hyphen or a non breaking hyphen) takes
the orphan treatment at the validate surfaces.

CH-252 (F10-8-1, T10-29): an entry identifier alone
inside single guillemets, corner brackets, double angle
brackets, lenticular brackets, reversed guillemets, or
white square brackets, or joined to a second identifier
by the word vs, by vs with a full stop, or by the word
against, states no content and takes no group credit.

CH-253 (F10-8-4, T10-30): a heading shaped line behind
an eight letter marker, a black rightwards pointer, a
black rightwards arrowhead, or a three dimensional
arrowhead takes no group credit, in group 3 and inside
a block. The two digit and letter marker form (case
X30) stands as a pin.

CH-254 (F10-8-6, T10-31): two decider lines naming two
different deciders draw the conflict finding where the
second line stands behind an eight letter marker, a
black rightwards pointer, or a black rightwards arrow,
stands behind a digit and letter marker, carries a
figure space or a punctuation space inside its verb
phrase, or carries a semicolon after the word by.

CH-255 (F10-8-7, T10-32): a Status line standing as a
level 4 heading with a triple underscore dressed
marker, a tilde dressed marker, or a mixed asterisk and
underscore dressed marker, inside an entry takes the
rule 2 heading signal.

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


class Ch249RecordLineRound10Test(unittest.TestCase):
    """F10-8-2: the round 10 record lines state no census
    content and take no group credit."""

    BLOCK_FORMS = (
        "Recorded. In the harbour log.",
        "Origin. The harbour log.",
        "Source. The harbour log.",
        "Landed. In the harbour log.",
        "Filed! In the harbour log.",
        "Origin, the harbour log.",
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
            self, banked_block_entry("Recorded. In the "
                                     "harbour log."))
        self.assertEqual(code, 4)
        self.assertIn("Banked head evidence groups sum to 0",
                      combined)

    def test_round9_record_line_pins_stand(self):
        for line in ("Filed; in the harbour log.",
                     "Recorded; in the harbour log.",
                     "Filed. In the harbour log.",
                     "Source; the harbour log.",
                     "Origin; the harbour log.",
                     "Sources; the harbour log."):
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


class Ch250RespelledLabelRound10Test(unittest.TestCase):
    """F10-8-3: the round 10 label forms take no group
    credit."""

    PLAIN_FORMS = (
        "Question\u2003as put: genuine words stand here in a "
        "repeated line.",
        "Question\u2002as put: genuine words stand here in a "
        "repeated line.",
        "Question\u2006as put: genuine words stand here in a "
        "repeated line.",
        "Question\u205fas put: genuine words stand here in a "
        "repeated line.",
        "C\u043est of deciding late: genuine words stand "
        "here in a repeated line.",
        "O\u0440tions: genuine words stand here in a "
        "repeated line.",
        "\u0421ost of deciding late: genuine words stand "
        "here in a repeated line.",
        "Questi\u043en: genuine words stand here in a "
        "repeated line.",
    )

    def test_respelled_plain_forms_take_no_group(self):
        for line in self.PLAIN_FORMS:
            with self.subTest(line=repr(line)):
                _model, output = h.run_pipeline(
                    banked_plain_entry(line).encode("utf-8"))
                self.assertIsNotNone(output)
                assert_in_no_group(self, output)

    def test_labelled_test_reads_the_round10_forms(self):
        for line in self.PLAIN_FORMS:
            with self.subTest(line=repr(line)):
                self.assertEqual(
                    validate._is_open_field_labelled_line(line),
                    True)

    def test_round9_and_taught_label_pins_stand(self):
        for line in ("Question\u2007as put: genuine words stand "
                     "here in a repeated line.",
                     "Question\u202fas put: genuine words stand "
                     "here in a repeated line.",
                     "Cost of deciding l\u0430te: genuine words "
                     "stand here in a repeated line.",
                     "\u039fptions: genuine words stand here in "
                     "a repeated line.",
                     "Question\u2008as put: genuine words stand "
                     "here in a repeated line.",
                     "Question: genuine words stand here in a "
                     "repeated line."):
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


class Ch251Level4Round10HeadingTest(unittest.TestCase):
    """F10-8-5: the round 10 non exact heading forms take
    the orphan treatment at the validate surfaces."""

    @staticmethod
    def _construction(heading_line):
        return (HEAD + entry("An unheaded paragraph stands "
                             "here.\n")
                + heading_line + "\n\n"
                + "Status: Banked\n\n" + FIELDS
                + "An unheaded paragraph stands here.\n")

    FORMS = (
        "#### DQ\u2011002: Second entry",
        "#### DQ\u2014002: Second entry",
        "#### DQ\u2015002: Second entry",
        "#### Dq\uff0d002: Second entry",
        "#### DQ\ufe63002: Second entry",
        "#### Dq\u2011002: Second entry",
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

    def test_round9_heading_pins_stand(self):
        for heading_line in ("#### DQ\u2010002: Second entry",
                             "#### DQ\u2212002: Second entry",
                             "#### DQ\u2012002: Second entry",
                             "#### DQ\u00ad002: Second entry",
                             "#### Dq\u2013002: Second entry"):
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


class Ch252IdentifierRound10Test(unittest.TestCase):
    """F10-8-1: the round 10 identifier forms state no
    content and take no group credit."""

    BLOCK_FORMS = (
        "\u2039DQ-002\u203a",
        "\u300cDQ-002\u300d",
        "\u27e6DQ-002\u27e7",
        "\u3010DQ-002\u3011",
        "\u00bbDQ-002\u00ab",
        "DQ-002 vs DQ-003",
        "DQ-002 vs. DQ-003",
        "DQ-002 against DQ-003",
        "\u301aDQ-002\u301b",
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
            self, banked_block_entry("\u2039DQ-002\u203a"))
        self.assertEqual(code, 4)
        self.assertIn("Banked head evidence groups sum to 0",
                      combined)

    def test_round9_and_exact_identifier_pins_stand(self):
        for line in ("\u00abDQ-002\u00bb",
                     "\u201eDQ-002\u201c",
                     "DQ-002 versus DQ-003",
                     "\uff08DQ-002\uff09",
                     "DQ-002", "DQ-002 or DQ-003",
                     "DQ-002 and DQ-003"):
            with self.subTest(line=repr(line)):
                _model, output = h.run_pipeline(
                    banked_block_entry(line).encode("utf-8"))
                self.assertIsNotNone(output)
                assert_in_no_group(self, output)

    def test_identifier_beside_words_keeps_content(self):
        for line in ("DQ-002 is the harbour entry",
                     "DQ-002 vs the harbour entry",
                     "DQ-002 against the harbour entry",
                     "DQ-002 versus the harbour entry"):
            with self.subTest(line=line):
                self.assertEqual(
                    validate._line_carries_content(line), True)


class Ch253HeadingShapeRound10Test(unittest.TestCase):
    """F10-8-4: the round 10 heading forms take no group
    credit, in group 3 and inside a block."""

    PLAIN_FORMS = (
        "abcdefgh) #### Ruling by Captain JP",
        "\u25ba #### Ruling by Captain JP",
        "\u27a4 #### Ruling by Captain JP",
        "\u27a2 #### Ruling by Captain JP",
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
        line = "abcdefgh) #### Ruling by Captain JP"
        _model, output = h.run_pipeline(
            banked_block_entry(line).encode("utf-8"))
        self.assertIsNotNone(output)
        assert_in_no_group(self, output)

    def test_genuine_prose_behind_the_same_forms_keeps_credit(self):
        for line in ("abcdefgh) An unheaded paragraph stands "
                     "here.",
                     "\u25ba An unheaded paragraph stands here.",
                     "\u27a4 An unheaded paragraph stands here.",
                     "\u27a2 An unheaded paragraph stands here."):
            with self.subTest(line=repr(line)):
                self.assertEqual(
                    validate._is_heading_shaped_line(line), False)
                _model, output = h.run_pipeline(
                    banked_plain_entry(line).encode("utf-8"))
                self.assertIsNotNone(output)
                self.assertIn("DQ-001", group_members(
                    output, "unheaded paragraphs"))
                self.assertEqual(sums_agree(output), True)

    def test_round9_marker_pins_stand(self):
        for line in ("abcdefg) #### Ruling by Captain JP",
                     "\u25b6 #### Ruling by Captain JP",
                     "\u27a1 #### Ruling by Captain JP",
                     "12a) #### Ruling by Captain JP"):
            with self.subTest(line=repr(line)):
                self.assertEqual(
                    validate._is_heading_shaped_line(line), True)


class Ch254DeciderRound10Test(unittest.TestCase):
    """F10-8-6: the round 10 second decider forms draw the
    conflict finding. The space before colon bound case
    stands as recorded."""

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
        "abcdefgh) Ruled by: Sam\n\n",
        "\u25ba Ruled by: Sam\n\n",
        "\u27a1 Ruled by: Sam\n\n",
        "1a) Ruled by: Sam\n\n",
        "Ruled\u2007by: Sam\n\n",
        "Ruled\u2008by: Sam\n\n",
        "Ruled by; Sam\n\n",
    )

    def test_second_decider_round10_forms_take_a_finding(self):
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

    def test_round9_decider_pins_stand(self):
        for second in ("abcdefg) Ruled by: Sam\n\n",
                       "\u25b6 Ruled by: Sam\n\n",
                       "Ruled\u200aby: Sam\n\n",
                       "Ruled by\u2236 Sam\n\n",
                       "a1) Ruled by: Sam\n\n",
                       "Ruled\u2009by: Sam\n\n"):
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


def _banked_heading_entry(number, extra):
    return (
        "### DQ-%03d: Banked head, heading status probe\n"
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
        "This question is waiting for a decision.\n"
        "%s" % (number, extra))


class Ch255DressedStatusHeadingRound10Test(unittest.TestCase):
    """F10-8-7: the round 10 dressed Status heading forms
    take the rule 2 heading signal."""

    FORMS = (
        "\n#### ___Status:___ RULED, closed\n",
        "\n#### ~~Status:~~ RULED, closed\n",
        "\n#### **_Status:**_ RULED, closed\n",
    )

    def _heading_hits(self, output):
        return [f for f in h.findings_of(output)
                if "standing as a heading" in
                (h.finding_statement(f) or "")]

    def _run(self, data):
        _model, output = h.run_pipeline(
            data.encode("utf-8"), "fix10-e-heading")
        if output is None:
            raise AssertionError("pipeline returned a failure")
        return output

    def test_heading_round10_forms_take_a_signal(self):
        for extra in self.FORMS:
            with self.subTest(extra=repr(extra)):
                data = ("# Decision queue\n\n"
                        + _banked_heading_entry(962, extra))
                output = self._run(data)
                self.assertEqual(
                    1, len(self._heading_hits(output)))

    def test_heading_forms_cli_exit_one(self):
        for extra in self.FORMS:
            with self.subTest(extra=repr(extra)):
                data = ("# Decision queue\n\n"
                        + _banked_heading_entry(962, extra))
                code, combined = run_cli_on(self, data)
                self.assertEqual(code, 1)
                self.assertIn("standing as a heading inside",
                              combined)

    def test_round9_dress_pins_stand(self):
        for number, extra in (
                (964, "\n#### _Status:_ RULED, closed\n"),
                (963, "\n#### ***Status:*** RULED, closed\n"),
                (965, "\n#### **Status:** RULED, closed\n"),
                (967, "\n#### Status: RULED, closed\n")):
            with self.subTest(extra=repr(extra)):
                data = ("# Decision queue\n\n"
                        + _banked_heading_entry(number, extra))
                output = self._run(data)
                self.assertEqual(
                    1, len(self._heading_hits(output)))

    def test_no_colon_form_stays_outside_the_signal_pin(self):
        data = ("# Decision queue\n\n" + _banked_heading_entry(
            968, "\n#### __Status__ RULED, closed\n"))
        output = self._run(data)
        self.assertEqual([], self._heading_hits(output))


if __name__ == "__main__":
    unittest.main()
