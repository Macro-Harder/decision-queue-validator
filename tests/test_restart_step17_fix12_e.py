"""Restart Step 17 fix wave 12, Fix Seat E tests.

Charges CH-335 to CH-341, Cluster E (the group credit
family), as proposed at section 3 of
design/steps/step-17r-r12-triage-prep.md, on round 12
attack seat 7 findings F12-7-1 to F12-7-7
(design/steps/step-17r-r12-seat07-run.md). Every cure
stands in product/decision_queue_validator/validate.py
only, at the Cluster E surfaces as cured at CH-295 to
CH-301.

CH-335 (F12-7-2, T12-20, Medium): a partial block whose
only body is a Recorded, Filed, Source, Landed, Origin,
or Sources line closed by a fullwidth exclamation mark,
a fullwidth question mark, a hyphen, a slash, a closing
parenthesis, or an ellipsis states no census content
and takes no group credit, toward PIN-01 form 1.

CH-336 (F12-7-3, T12-21, Medium): a labelled field line
in a further respelled form of a taught label (an ogham
space mark inside the label, a Greek capital Beta at
the head of Blocks, a Greek capital Tau at the head of
The question, a Ukrainian small I inside Cost of
deciding late, or a Cyrillic capital A at the head of
the As of Question as put) takes no group credit.

CH-337 (F12-7-5, T12-22, Medium): a level 4 entry
heading in a further non exact form (a hyphen bullet,
a prolonged sound mark, or a modifier letter hyphen in
place of its hyphen) takes the orphan treatment at the
validate surfaces.

CH-338 (F12-7-1, T12-26, Low): an entry identifier
alone inside white lenticular brackets, mathematical
double angle brackets, parenthesis ornament brackets,
or white tortoise shell brackets, or joined to a second
identifier by with, alongside, facing, or meeting,
states no content and takes no group credit.

CH-339 (F12-7-4, T12-27, Low): a heading shaped line
behind an eleven letter marker, a heavy round tipped
rightwards arrow, a white small right pointing
triangle, a single right pointing angle quotation
mark, or a two letter and one digit marker takes no
group credit, in group 3 and inside a block. Genuine
prose behind the same forms keeps its credit, and the
three digit and two letter marker form stands cured
already, as pins.

CH-340 (F12-7-6, T12-28, Low): two decider lines naming
two different deciders draw the conflict finding where
the second line stands behind a ten letter marker or a
heavy round tipped rightwards arrow, carries an en
quad or a six per em space inside its verb phrase, or
carries a fullwidth semicolon or a modifier letter
colon after the word by.

CH-341 (F12-7-7, T12-29, Low): a Status line standing
as a level 4 heading in a sextuple asterisk, quintuple
underscore, asterisk underscore, double asterisk tilde,
tilde asterisk, or underscore tilde dressed marker
form, inside an entry, takes the rule 2 heading signal.

The cured CH-295 to CH-301 forms stand as pins in every
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


class Ch335RecordLineRound12Test(unittest.TestCase):
    """F12-7-2: the round 12 record line closers state no
    census content and take no group credit."""

    BLOCK_FORMS = (
        "Recorded\uff01 In the harbour log.",
        "Filed\uff1f In the harbour log.",
        "Source- In the harbour log.",
        "Landed/ In the harbour log.",
        "Origin) In the harbour log.",
        "Recorded\u2026 In the harbour log.",
        "Sources- In the harbour log.",
    )

    def test_record_line_only_block_takes_no_group(self):
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

    def test_record_line_only_block_withholds(self):
        code, combined = run_cli_on(
            self, banked_block_entry("Recorded\uff01 In the "
                                     "harbour log."))
        self.assertEqual(code, 4)
        self.assertIn("Banked head evidence groups sum to 0",
                      combined)

    def test_ch295_and_earlier_record_line_pins_stand(self):
        for line in ("Recorded! In the harbour log.",
                     "Filed? In the harbour log.",
                     "Recorded. In the harbour log.",
                     "Origin. The harbour log.",
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


class Ch336RespelledLabelRound12Test(unittest.TestCase):
    """F12-7-3: the round 12 label forms take no group
    credit."""

    PLAIN_FORMS = (
        "Question\u1680as put: genuine words stand here in a "
        "repeated line.",
        "\u0392locks: genuine words stand here in a "
        "repeated line.",
        "\u03a4he question: genuine words stand here in a "
        "repeated line.",
        "Cost of dec\u0456ding late: genuine words stand "
        "here in a repeated line.",
        "Question \u0410s put: genuine words stand here in a "
        "repeated line.",
    )

    def test_respelled_plain_forms_take_no_group(self):
        for line in self.PLAIN_FORMS:
            with self.subTest(line=repr(line)):
                _model, output = h.run_pipeline(
                    banked_plain_entry(line).encode("utf-8"))
                self.assertIsNotNone(output)
                assert_in_no_group(self, output)

    def test_labelled_test_reads_the_round12_forms(self):
        for line in self.PLAIN_FORMS:
            with self.subTest(line=repr(line)):
                self.assertEqual(
                    validate._is_open_field_labelled_line(line),
                    True)

    def test_ch296_and_taught_label_pins_stand(self):
        for line in ("Question\u2000as put: genuine words stand "
                     "here in a repeated line.",
                     "\u0422he question: genuine words stand here "
                     "in a repeated line.",
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


class Ch337Level4Round12HeadingTest(unittest.TestCase):
    """F12-7-5: the round 12 non exact heading forms take
    the orphan treatment at the validate surfaces."""

    @staticmethod
    def _construction(heading_line):
        return (HEAD + entry("An unheaded paragraph stands "
                             "here.\n")
                + heading_line + "\n\n"
                + "Status: Banked\n\n" + FIELDS
                + "An unheaded paragraph stands here.\n")

    FORMS = (
        "#### DQ\u2043002: Second entry",
        "#### DQ\u30fc002: Second entry",
        "#### DQ\u02d7002: Second entry",
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

    def test_ch297_heading_pins_stand(self):
        for heading_line in ("#### DQ\ufe58002: Second entry",
                             "#### DQ\u2e3a002: Second entry",
                             "#### DQ\u2014002: Second entry"):
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


class Ch338IdentifierRound12Test(unittest.TestCase):
    """F12-7-1: the round 12 identifier forms state no
    content and take no group credit."""

    BLOCK_FORMS = (
        "\u3016DQ-002\u3017",
        "\u27eaDQ-002\u27eb",
        "\u2768DQ-002\u2769",
        "\u3018DQ-002\u3019",
        "DQ-002 with DQ-003",
        "DQ-002 alongside DQ-003",
        "DQ-002 facing DQ-003",
        "DQ-002 meeting DQ-003",
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
            self, banked_block_entry("\u3016DQ-002\u3017"))
        self.assertEqual(code, 4)
        self.assertIn("Banked head evidence groups sum to 0",
                      combined)

    def test_ch298_and_exact_identifier_pins_stand(self):
        for line in ("\u3014DQ-002\u3015",
                     "\u300aDQ-002\u300b",
                     "DQ-002 beside DQ-003",
                     "DQ-002 versus. DQ-003",
                     "DQ-002", "DQ-002 or DQ-003"):
            with self.subTest(line=repr(line)):
                _model, output = h.run_pipeline(
                    banked_block_entry(line).encode("utf-8"))
                self.assertIsNotNone(output)
                assert_in_no_group(self, output)

    def test_identifier_beside_words_keeps_content(self):
        for line in ("DQ-002 is the harbour entry",
                     "DQ-002 with the harbour entry",
                     "DQ-002 alongside the harbour entry",
                     "DQ-002 meeting the harbour entry"):
            with self.subTest(line=line):
                self.assertEqual(
                    validate._line_carries_content(line), True)


class Ch339HeadingShapeRound12Test(unittest.TestCase):
    """F12-7-4: the round 12 heading forms take no group
    credit, in group 3 and inside a block."""

    PLAIN_FORMS = (
        "abcdefghijk) #### Ruling by Captain JP",
        "\u279c #### Ruling by Captain JP",
        "\u25b9 #### Ruling by Captain JP",
        "\u203a #### Ruling by Captain JP",
        "ab1) #### Ruling by Captain JP",
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
        line = "\u279c #### Ruling by Captain JP"
        _model, output = h.run_pipeline(
            banked_block_entry(line).encode("utf-8"))
        self.assertIsNotNone(output)
        assert_in_no_group(self, output)

    def test_genuine_prose_behind_the_same_forms_keeps_credit(self):
        for line in ("abcdefghijk) Genuine prose stands here "
                     "as a paragraph.",
                     "\u279c Genuine prose stands here as a "
                     "paragraph."):
            with self.subTest(line=repr(line)):
                self.assertEqual(
                    validate._is_heading_shaped_line(line), False)
                _model, output = h.run_pipeline(
                    banked_plain_entry(line).encode("utf-8"))
                self.assertIsNotNone(output)
                self.assertIn("DQ-001", group_members(
                    output, "unheaded paragraphs"))
                self.assertEqual(sums_agree(output), True)

    def test_ch299_marker_pins_stand(self):
        for line in ("abcdefghij) #### Ruling by Captain JP",
                     "\u25b7 #### Ruling by Captain JP",
                     "12ab) #### Ruling by Captain JP",
                     "123ab) #### Ruling by Captain JP"):
            with self.subTest(line=repr(line)):
                self.assertEqual(
                    validate._is_heading_shaped_line(line), True)


class Ch340DeciderRound12Test(unittest.TestCase):
    """F12-7-6: the round 12 second decider forms draw the
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
        "abcdefghij) Ruled by: Sam\n\n",
        "\u279c Ruled by: Sam\n\n",
        "Ruled\u2000by: Sam\n\n",
        "Ruled\u2006by: Sam\n\n",
        "Ruled by\uff1b Sam\n\n",
        "Ruled by\u02f8 Sam\n\n",
    )

    def test_second_decider_round12_forms_take_a_finding(self):
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

    def test_ch300_decider_pins_stand(self):
        for second in ("abcdefghi) Ruled by: Sam\n\n",
                       "\u27a4 Ruled by: Sam\n\n",
                       "Ruled\u2003by: Sam\n\n",
                       "Ruled by\u037e Sam\n\n"):
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


class Ch341DressedStatusHeadingRound12Test(unittest.TestCase):
    """F12-7-7: the round 12 dressed Status heading forms
    take the rule 2 heading signal."""

    FORMS = (
        "\n#### ******Status:****** RULED, closed\n",
        "\n#### _____Status:_____ RULED, closed\n",
        "\n#### *_Status:*_ RULED, closed\n",
        "\n#### **~Status:**~ RULED, closed\n",
        "\n#### ~*Status:~* RULED, closed\n",
        "\n#### _~Status:_~ RULED, closed\n",
    )

    def _heading_hits(self, output):
        return [f for f in h.findings_of(output)
                if "standing as a heading" in
                (h.finding_statement(f) or "")]

    def _run(self, data):
        _model, output = h.run_pipeline(
            data.encode("utf-8"), "fix12-e-heading")
        if output is None:
            raise AssertionError("pipeline returned a failure")
        return output

    def test_heading_round12_forms_take_a_signal(self):
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

    def test_ch301_dress_pins_stand(self):
        for extra in ("\n#### ****Status:**** RULED, closed\n",
                      "\n#### *****Status:***** RULED, closed\n",
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
