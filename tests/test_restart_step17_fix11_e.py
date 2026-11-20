"""Restart Step 17 fix wave 11, Fix Seat E tests.

Charges CH-295 to CH-301, as determined at record
section 108 of design/steps/step-17r-record.md, on the
round 11 triage preparation paper
design/steps/step-17r-r11-triage-prep.md, Cluster E,
and on round 11 attack seat 8 findings F11-8-1 to
F11-8-7 (design/steps/step-17r-r11-seat08-run.md).
Every cure stands in
product/decision_queue_validator/validate.py only, at
the Cluster E surfaces as cured at CH-249 to CH-255.

CH-295 (F11-8-2, T11-18, Medium): a partial block whose
only body is a Recorded, Origin, Source, Landed, Filed,
or Sources line closed by an exclamation mark or a
question mark states no census content and takes no
group credit, toward PIN-01 form 1.

CH-296 (F11-8-3, T11-19, Medium): a labelled field line
in a further respelled form of a taught label (an en
quad, an em quad, a three per em space, or a four per
em space inside the label, a Cyrillic capital Te at the
head of The question, a Cyrillic capital Be at the head
of Blocks, a Cyrillic capital O at the head of Options,
or a Cyrillic small Es inside Cost of deciding late)
takes no group credit.

CH-297 (F11-8-5, T11-20, Medium): a level 4 entry
heading in a further non exact form (a small em dash,
a two em dash, a double low line, a three em dash, or
a wave dash in place of its hyphen, or a mixed case
prefix with a small em dash) takes the orphan
treatment at the validate surfaces.

CH-298 (F11-8-1, T11-26, Low): an entry identifier
alone inside tortoise shell brackets, double angle
book brackets, single angle book brackets, fullwidth
square brackets, or mathematical angle brackets, or
joined to a second identifier by the word v, contra,
opposing, or beside, or by versus with a full stop,
states no content and takes no group credit.

CH-299 (F11-8-4, T11-27, Low): a heading shaped line
behind a nine or ten letter marker, a white right
pointing triangle, a heavy wide headed rightwards
arrow, a rightwards white arrow, or a two digit and
two letter marker takes no group credit, in group 3
and inside a block.

CH-300 (F11-8-6, T11-28, Low): two decider lines naming
two different deciders draw the conflict finding where
the second line stands behind a nine letter marker, a
black rightwards arrowhead, or a three dimensional
arrowhead, stands behind a letter digit letter marker,
carries an em space or a narrow no break space inside
its verb phrase, or carries a Greek question mark or a
small semicolon after the word by.

CH-301 (F11-8-7, T11-29, Low): a Status line standing
as a level 4 heading with a quadruple asterisk, a
quadruple underscore, a single tilde, a mixed
underscore and asterisk, a mixed asterisk and tilde,
or a quintuple asterisk dressed marker, inside an
entry takes the rule 2 heading signal.

The cured CH-249 to CH-255 forms stand as pins in every
class. No construction in this file builds the F1
shape, and no banked question is named in any
construction. The Ch144FullmatchCostTest class is not
run by this seat in any form.
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


class Ch295RecordLineRound11Test(unittest.TestCase):
    """F11-8-2: the round 11 record lines state no census
    content and take no group credit."""

    BLOCK_FORMS = (
        "Recorded! In the harbour log.",
        "Recorded? In the harbour log.",
        "Origin! The harbour log.",
        "Source! The harbour log.",
        "Landed! In the harbour log.",
        "Filed? In the harbour log.",
        "Sources! The harbour log.",
        "Origin? The harbour log.",
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
            self, banked_block_entry("Recorded! In the "
                                     "harbour log."))
        self.assertEqual(code, 4)
        self.assertIn("Banked head evidence groups sum to 0",
                      combined)

    def test_ch249_and_round9_record_line_pins_stand(self):
        for line in ("Recorded. In the harbour log.",
                     "Origin. The harbour log.",
                     "Source. The harbour log.",
                     "Landed. In the harbour log.",
                     "Filed! In the harbour log.",
                     "Origin, the harbour log.",
                     "Filed; in the harbour log.",
                     "Sources; the harbour log.",
                     "Sources. The harbour log."):
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


class Ch296RespelledLabelRound11Test(unittest.TestCase):
    """F11-8-3: the round 11 label forms take no group
    credit."""

    PLAIN_FORMS = (
        "Question\u2000as put: genuine words stand here in a "
        "repeated line.",
        "Question\u2001as put: genuine words stand here in a "
        "repeated line.",
        "Question\u2004as put: genuine words stand here in a "
        "repeated line.",
        "Question\u2005as put: genuine words stand here in a "
        "repeated line.",
        "\u0422he question: genuine words stand here in a "
        "repeated line.",
        "\u0412locks: genuine words stand here in a "
        "repeated line.",
        "\u041eptions: genuine words stand here in a "
        "repeated line.",
        "Cost of de\u0441iding late: genuine words stand "
        "here in a repeated line.",
    )

    def test_respelled_plain_forms_take_no_group(self):
        for line in self.PLAIN_FORMS:
            with self.subTest(line=repr(line)):
                _model, output = h.run_pipeline(
                    banked_plain_entry(line).encode("utf-8"))
                self.assertIsNotNone(output)
                assert_in_no_group(self, output)

    def test_labelled_test_reads_the_round11_forms(self):
        for line in self.PLAIN_FORMS:
            with self.subTest(line=repr(line)):
                self.assertEqual(
                    validate._is_open_field_labelled_line(line),
                    True)

    def test_ch250_and_taught_label_pins_stand(self):
        for line in ("Question\u2003as put: genuine words stand "
                     "here in a repeated line.",
                     "Question\u2002as put: genuine words stand "
                     "here in a repeated line.",
                     "C\u043est of deciding late: genuine words "
                     "stand here in a repeated line.",
                     "O\u0440tions: genuine words stand here in a "
                     "repeated line.",
                     "Opti\u03bfns: genuine words stand here in a "
                     "repeated line.",
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


class Ch297Level4Round11HeadingTest(unittest.TestCase):
    """F11-8-5: the round 11 non exact heading forms take
    the orphan treatment at the validate surfaces."""

    @staticmethod
    def _construction(heading_line):
        return (HEAD + entry("An unheaded paragraph stands "
                             "here.\n")
                + heading_line + "\n\n"
                + "Status: Banked\n\n" + FIELDS
                + "An unheaded paragraph stands here.\n")

    FORMS = (
        "#### DQ\ufe58002: Second entry",
        "#### DQ\u2e3a002: Second entry",
        "#### DQ\u2017002: Second entry",
        "#### Dq\ufe58002: Second entry",
        "#### DQ\u2e3b002: Second entry",
        "#### DQ\u301c002: Second entry",
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

    def test_ch251_heading_pins_stand(self):
        for heading_line in ("#### DQ\u2011002: Second entry",
                             "#### DQ\u2014002: Second entry",
                             "#### DQ\u2015002: Second entry",
                             "#### Dq\uff0d002: Second entry",
                             "#### DQ\ufe63002: Second entry",
                             "#### DQ\u2014002: Second entry",
                             "#### Dq\u2014002: Second entry"):
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


class Ch298IdentifierRound11Test(unittest.TestCase):
    """F11-8-1: the round 11 identifier forms state no
    content and take no group credit."""

    BLOCK_FORMS = (
        "\u3014DQ-002\u3015",
        "\u300aDQ-002\u300b",
        "\u3008DQ-002\u3009",
        "\uff3bDQ-002\uff3d",
        "\u27e8DQ-002\u27e9",
        "DQ-002 v DQ-003",
        "DQ-002 contra DQ-003",
        "DQ-002 opposing DQ-003",
        "DQ-002 versus. DQ-003",
        "DQ-002 beside DQ-003",
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
            self, banked_block_entry("\u3014DQ-002\u3015"))
        self.assertEqual(code, 4)
        self.assertIn("Banked head evidence groups sum to 0",
                      combined)

    def test_ch252_and_exact_identifier_pins_stand(self):
        for line in ("\u2039DQ-002\u203a",
                     "\u300cDQ-002\u300d",
                     "\u27e6DQ-002\u27e7",
                     "\u3010DQ-002\u3011",
                     "\u00bbDQ-002\u00ab",
                     "DQ-002 vs DQ-003",
                     "DQ-002 vs. DQ-003",
                     "DQ-002 against DQ-003",
                     "DQ-002", "DQ-002 or DQ-003",
                     "DQ-002 versus DQ-003"):
            with self.subTest(line=repr(line)):
                _model, output = h.run_pipeline(
                    banked_block_entry(line).encode("utf-8"))
                self.assertIsNotNone(output)
                assert_in_no_group(self, output)

    def test_identifier_beside_words_keeps_content(self):
        for line in ("DQ-002 is the harbour entry",
                     "DQ-002 v the harbour entry",
                     "DQ-002 contra the harbour entry",
                     "DQ-002 beside the harbour entry",
                     "DQ-002 versus the harbour entry"):
            with self.subTest(line=line):
                self.assertEqual(
                    validate._line_carries_content(line), True)


class Ch299HeadingShapeRound11Test(unittest.TestCase):
    """F11-8-4: the round 11 heading forms take no group
    credit, in group 3 and inside a block."""

    PLAIN_FORMS = (
        "abcdefghi) #### Ruling by Captain JP",
        "\u25b7 #### Ruling by Captain JP",
        "\u2794 #### Ruling by Captain JP",
        "\u21e8 #### Ruling by Captain JP",
        "12ab) #### Ruling by Captain JP",
        "abcdefghij) #### Ruling by Captain JP",
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
        line = "abcdefghi) #### Ruling by Captain JP"
        _model, output = h.run_pipeline(
            banked_block_entry(line).encode("utf-8"))
        self.assertIsNotNone(output)
        assert_in_no_group(self, output)

    def test_genuine_prose_behind_the_same_forms_keeps_credit(self):
        for line in ("abcdefghi) An unheaded paragraph stands "
                     "here.",
                     "\u25b7 An unheaded paragraph stands here.",
                     "\u2794 An unheaded paragraph stands here.",
                     "\u21e8 An unheaded paragraph stands here.",
                     "12ab) An unheaded paragraph stands here."):
            with self.subTest(line=repr(line)):
                self.assertEqual(
                    validate._is_heading_shaped_line(line), False)
                _model, output = h.run_pipeline(
                    banked_plain_entry(line).encode("utf-8"))
                self.assertIsNotNone(output)
                self.assertIn("DQ-001", group_members(
                    output, "unheaded paragraphs"))
                self.assertEqual(sums_agree(output), True)

    def test_ch253_marker_pins_stand(self):
        for line in ("abcdefgh) #### Ruling by Captain JP",
                     "\u25ba #### Ruling by Captain JP",
                     "\u27a4 #### Ruling by Captain JP",
                     "\u27a2 #### Ruling by Captain JP",
                     "12a) #### Ruling by Captain JP"):
            with self.subTest(line=repr(line)):
                self.assertEqual(
                    validate._is_heading_shaped_line(line), True)


class Ch300DeciderRound11Test(unittest.TestCase):
    """F11-8-6: the round 11 second decider forms draw the
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
        "abcdefghi) Ruled by: Sam\n\n",
        "\u27a4 Ruled by: Sam\n\n",
        "\u27a2 Ruled by: Sam\n\n",
        "Ruled\u2003by: Sam\n\n",
        "Ruled\u202fby: Sam\n\n",
        "Ruled by\u037e Sam\n\n",
        "Ruled by\ufe54 Sam\n\n",
        "a1b) Ruled by: Sam\n\n",
    )

    def test_second_decider_round11_forms_take_a_finding(self):
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

    def test_ch254_decider_pins_stand(self):
        for second in ("abcdefgh) Ruled by: Sam\n\n",
                       "\u25ba Ruled by: Sam\n\n",
                       "\u27a1 Ruled by: Sam\n\n",
                       "1a) Ruled by: Sam\n\n",
                       "Ruled\u2007by: Sam\n\n",
                       "Ruled\u2008by: Sam\n\n",
                       "Ruled by; Sam\n\n"):
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


class Ch301DressedStatusHeadingRound11Test(unittest.TestCase):
    """F11-8-7: the round 11 dressed Status heading forms
    take the rule 2 heading signal."""

    FORMS = (
        "\n#### ****Status:**** RULED, closed\n",
        "\n#### ____Status:____ RULED, closed\n",
        "\n#### ~Status:~ RULED, closed\n",
        "\n#### _*Status:_* RULED, closed\n",
        "\n#### *~Status:*~ RULED, closed\n",
        "\n#### *****Status:***** RULED, closed\n",
    )

    def _heading_hits(self, output):
        return [f for f in h.findings_of(output)
                if "standing as a heading" in
                (h.finding_statement(f) or "")]

    def _run(self, data):
        _model, output = h.run_pipeline(
            data.encode("utf-8"), "fix11-e-heading")
        if output is None:
            raise AssertionError("pipeline returned a failure")
        return output

    def test_heading_round11_forms_take_a_signal(self):
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

    def test_ch255_dress_pins_stand(self):
        for extra in ("\n#### ___Status:___ RULED, closed\n",
                      "\n#### ~~Status:~~ RULED, closed\n",
                      "\n#### **_Status:**_ RULED, closed\n",
                      "\n#### ***Status:*** RULED, closed\n",
                      "\n#### **Status:** RULED, closed\n",
                      "\n#### Status: RULED, closed\n"):
            with self.subTest(extra=repr(extra)):
                data = ("# Decision queue\n\n"
                        + _banked_heading_entry(962, extra))
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
