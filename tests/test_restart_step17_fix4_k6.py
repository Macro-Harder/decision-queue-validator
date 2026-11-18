"""Restart Step 17 fix wave 4, cluster K6 tests.

Charges CH-53 then CH-63, ruled at section 38 of design/steps/
step-17r-record.md, prepared at design/steps/
step-17r-triage4-prep.md.

CH-53, in the defect repair form, against register item
17R-183 (round 4 attack seat 15, finding F-15-4-1): the
CH-35 defect repair helper _banked_cut_entry_ids keys the
Banked head population removal by display identifier, so
where one identifier stands twice and only the second
entry is cut by an unmatched heading segment, the uncut
twin is also removed and a run the CH-42 form withholds
at exit 4 is released at exit 1 with full findings. The
cure keys the removal on the entry itself, its span, not
on the shared display identifier.

CH-63, the Banked head evidence group limbs of round 4
attack seat 8 (findings F4-8-1 to F4-8-7): a level 4
heading in entry heading form, respelled taught labels,
the census heading shape surface under the class ground
of record section 38 ruling (e), the marker forms of the
heading shape test, the identifier only content line, and
the decider limb F4-8-7 under FLAG 8, its exact
repetition bound form standing as recorded.

Pins that must not break: the corrected CH-35 pin and the
defect repair verification forms (the pin form and its
adjacent cut forms at exit 1 with the Warning released,
the uncut controls withholding), the CH-42 pins whole,
the genuine credit controls (the round 2 quoted prose
control and the genuine short word control, two CJK
characters forming one word, under record section 26
flag (g)), and the D1 decider narrowing pins. The whole
charge stands on the Banked head footing surface beside
F1; no test here decides, drafts, or advances the F1
shape outcome, which stands fenced at carry H-01.
"""

import tempfile
import unittest
from pathlib import Path

import dqv_harness as h

validate = h.import_module("validate")
parse = h.import_module("parse")

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


DUP_FIELDS = ("Question: Which option should we take for DQ-001?\n\n"
              "Options: Option A, Option B\n\n"
              "Cost of deciding late: Work stays blocked while "
              "this waits.\n\n"
              "Blocks: nothing named\n")


def dup_entry():
    return ("### DQ-001: Question DQ-001\n\n"
            "Status: Banked\n\n" + DUP_FIELDS)


CUT_TAIL = ("\x0b##### An unmatched generated heading\n\n"
            "Prose standing under the unmatched heading.\n")


class Ch53DuplicateCutTest(unittest.TestCase):
    """CH-53: the seat 15 construction and its controls,
    in the form the attack paper files them (its c03, c04,
    c05, and c06 cases)."""

    def test_c03_duplicate_second_cut_withholds_at_exit_4(self):
        # The finding form, failing before the cure: two
        # entries headed DQ-001, field lines only, the
        # second cut by an unmatched heading. The uncut
        # twin stays in the population, the footing fails
        # at sum 0 against a population of 1, and the run
        # is withheld in full.
        text = HEAD + dup_entry() + "\n" + dup_entry() + CUT_TAIL
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                code, combined = run_cli_on(self, text, subcommand)
                self.assertEqual(code, 4)
                self.assertIn(
                    "Banked head evidence groups sum to 0 against "
                    "a Banked head population of 1", combined)

    def test_c04_duplicate_neither_cut_withholds_at_exit_4(self):
        text = HEAD + dup_entry() + "\n" + dup_entry()
        code, combined = run_cli_on(self, text)
        self.assertEqual(code, 4)
        self.assertIn(
            "Banked head evidence groups sum to 0 against "
            "a Banked head population of 2", combined)

    def test_c05_single_uncut_withholds_at_exit_4(self):
        text = HEAD + dup_entry()
        code, combined = run_cli_on(self, text)
        self.assertEqual(code, 4)
        self.assertIn(
            "Banked head evidence groups sum to 0 against "
            "a Banked head population of 1", combined)

    def test_c06_single_cut_released_at_exit_1(self):
        # The corrected CH-35 pin form, standing before and
        # after: one entry, field lines only, cut by the
        # unmatched heading, released with its Warning.
        text = HEAD + dup_entry() + CUT_TAIL
        code, combined = run_cli_on(self, text)
        self.assertEqual(code, 1)
        self.assertIn("An unmatched generated heading", combined)
        self.assertIn("Self check: sums agree", combined)

    def test_duplicate_first_cut_second_uncut_withholds(self):
        # The twin form in the other order: the cut stands
        # after the first entry and the second entry stands
        # after the segment, uncut and taking no group, so
        # the run withholds on the second entry alone.
        text = (HEAD + dup_entry() + CUT_TAIL + "\n" + dup_entry())
        code, combined = run_cli_on(self, text)
        self.assertEqual(code, 4)
        self.assertIn(
            "Banked head evidence groups sum to 0 against "
            "a Banked head population of 1", combined)

    def test_cut_set_keys_entries_not_identifiers(self):
        # The helper itself: on the c03 construction it
        # names exactly one entry, the cut second entry,
        # though both entries carry the one identifier.
        text = HEAD + dup_entry() + "\n" + dup_entry() + CUT_TAIL
        model, _output = h.run_pipeline(text.encode("utf-8"))
        entries = h.entries_of(model)
        cut = validate._banked_cut_entry_ids(model, entries)
        self.assertEqual(len(cut), 1)
        self.assertIn(entries[1], list(cut))
        self.assertNotIn(entries[0], list(cut))


class Ch63Level4EntryHeadingTest(unittest.TestCase):
    """F4-8-1: a level 4 heading in entry heading form
    takes the unmatched heading treatment, naming it, and
    its body stands in no entry above it."""

    Z03 = (HEAD + entry("An unheaded paragraph stands here.\n")
           + "#### DQ-002: Second entry\n\n"
           + "Status: Banked\n\n" + FIELDS
           + "An unheaded paragraph stands here.\n")

    def test_level4_entry_heading_takes_unmatched_warning(self):
        code, combined = run_cli_on(self, self.Z03)
        self.assertEqual(code, 1)
        self.assertIn("DQ-002: Second entry", combined)
        self.assertIn("matches no recognised heading form",
                      combined)

    def test_absorbed_status_line_no_longer_moves_the_entry(self):
        _model, output = h.run_pipeline(self.Z03.encode("utf-8"))
        self.assertIsNotNone(output)
        self.assertNotIn("DQ-001", group_members(
            output, "later Status line"))
        self.assertIn("DQ-001", group_members(
            output, "unheaded paragraphs"))
        self.assertEqual(sums_agree(output), True)

    def test_genuine_decision_block_forms_stand(self):
        # Pin direction: a level 4 block heading in ruling
        # form inside an entry stays a decision block, and
        # the level 3 and level 2 block forms keep their
        # PIN-06 Warnings with nothing imported (the seat 8
        # Z01 and Z02 forms).
        block_body = ("Ruled by: Captain JP\n\n"
                      "Ruled. The harbour light burns all night.\n\n"
                      "Outcome: Closed.\n\n"
                      "Landed in the harbour log.\n")
        text = HEAD + entry("#### Ruling by Captain JP\n\n"
                            + block_body)
        code, _combined = run_cli_on(self, text)
        self.assertEqual(code, 0)
        for heading in ("### Ruling by Captain JP\n\n",
                        "## Ruling by Captain JP\n\n"):
            with self.subTest(heading=heading):
                text = HEAD + entry(heading + block_body)
                code, combined = run_cli_on(self, text)
                self.assertEqual(code, 1)
                self.assertIn("PIN-06", combined)


class Ch63RespelledLabelTest(unittest.TestCase):
    """F4-8-2: a labelled field line in a respelled form
    of a taught label takes no group credit, in group 3
    and inside a block."""

    PLAIN_FORMS = (
        "Question 2: genuine words stand here in a repeated line.",
        "Cost of deciding late if we keep waiting much longer: "
        "genuine words stand here.",
        "Question-as-put: genuine words stand here in a "
        "repeated line.",
    )
    BLOCK_FORMS = (
        "Question\t: genuine words stand here in a repeated line.",
        "Question 2: genuine words stand here in a repeated line.",
    )

    def test_respelled_plain_forms_take_no_group(self):
        for line in self.PLAIN_FORMS:
            with self.subTest(line=line):
                _model, output = h.run_pipeline(
                    banked_plain_entry(line).encode("utf-8"))
                self.assertIsNotNone(output)
                assert_in_no_group(self, output)

    def test_respelled_block_forms_take_no_group(self):
        for line in self.BLOCK_FORMS:
            with self.subTest(line=repr(line)):
                _model, output = h.run_pipeline(
                    banked_block_entry(line).encode("utf-8"))
                self.assertIsNotNone(output)
                assert_in_no_group(self, output)

    def test_respelled_label_withholds_the_run(self):
        code, combined = run_cli_on(
            self, banked_plain_entry(self.PLAIN_FORMS[0]))
        self.assertEqual(code, 4)
        self.assertIn("Banked head evidence groups sum to 0",
                      combined)

    def test_labelled_test_reads_the_respelled_forms(self):
        for line in self.PLAIN_FORMS + self.BLOCK_FORMS:
            with self.subTest(line=repr(line)):
                self.assertEqual(
                    validate._is_open_field_labelled_line(line),
                    True)

    def test_unrelated_labels_stand_outside_the_taught_set(self):
        # The bound forms of the seat 8 paper, observation
        # 2, charged nowhere and standing after the cure:
        # a lower case note label and a snake case label
        # are no respelling of a taught label.
        for line in ("note: genuine words stand here in a "
                     "note line.",
                     "question_text: genuine words stand here "
                     "in a repeated line."):
            with self.subTest(line=line):
                self.assertEqual(
                    validate._is_open_field_labelled_line(line),
                    False)


class Ch63HeadingShapeClassTest(unittest.TestCase):
    """F4-8-3 and F4-8-4: the census heading shape surface
    under the class ground of record section 38 ruling
    (e). Run characters are read by Unicode class, the
    format, separator, and control classes and the mark
    classes, not by enumerated list."""

    X08 = (HEAD + entry("")
           + "\u061c##### An unmatched generated heading\n\n"
           + "Prose standing under the unmatched heading.\n")

    def test_alm_prefixed_unmatched_heading_cuts_and_warns(self):
        code, combined = run_cli_on(self, self.X08)
        self.assertEqual(code, 1)
        self.assertIn("An unmatched generated heading", combined)
        self.assertIn("Self check: sums agree", combined)

    def test_heading_recognition_reads_the_mark_by_class(self):
        info = parse._heading_info(
            "\u061c##### An unmatched generated heading")
        self.assertIsNotNone(info)
        self.assertEqual(info[0], 5)

    def test_heading_shape_behind_class_characters(self):
        for line in ("\u061c#### Ruling by Captain JP",
                     "\ufe0f#### Ruling by Captain JP",
                     "\u0301#### Ruling by Captain JP",
                     "\u2029#### Ruling by Captain JP",
                     "\x00#### Ruling by Captain JP"):
            with self.subTest(line=repr(line)):
                self.assertEqual(
                    validate._is_heading_shaped_line(line), True)
                _model, output = h.run_pipeline(
                    banked_plain_entry(line).encode("utf-8"))
                self.assertIsNotNone(output)
                assert_in_no_group(self, output)


class Ch63HeadingMarkerTest(unittest.TestCase):
    """F4-8-5: a heading shaped line behind an underscore
    bold opening or a two letter marker takes no group
    credit, and genuine prose behind the same forms keeps
    its credit."""

    def test_marker_heading_forms_take_no_group(self):
        for line in ("__#### Ruling by Captain JP",
                     "ab) #### Ruling by Captain JP"):
            with self.subTest(line=line):
                self.assertEqual(
                    validate._is_heading_shaped_line(line), True)
                _model, output = h.run_pipeline(
                    banked_plain_entry(line).encode("utf-8"))
                self.assertIsNotNone(output)
                assert_in_no_group(self, output)

    def test_genuine_prose_behind_the_same_forms_keeps_credit(self):
        # The seat 8 fresh controls Y16 and Y17, standing
        # as pins: a marked or emphasised paragraph is a
        # paragraph.
        for line in ("ab) An unheaded paragraph stands here.",
                     "__An unheaded paragraph stands here."):
            with self.subTest(line=line):
                self.assertEqual(
                    validate._is_heading_shaped_line(line), False)
                _model, output = h.run_pipeline(
                    banked_plain_entry(line).encode("utf-8"))
                self.assertIsNotNone(output)
                self.assertIn("DQ-001", group_members(
                    output, "unheaded paragraphs"))
                self.assertEqual(sums_agree(output), True)


class Ch63IdentifierOnlyContentTest(unittest.TestCase):
    """F4-8-6: a line carrying only an entry identifier
    states no content for the census, in the block and
    plain forms alike."""

    def test_identifier_only_forms_take_no_group(self):
        for builder in (banked_block_entry, banked_plain_entry):
            with self.subTest(builder=builder.__name__):
                _model, output = h.run_pipeline(
                    builder("DQ-002").encode("utf-8"))
                self.assertIsNotNone(output)
                assert_in_no_group(self, output)

    def test_content_test_reads_the_identifier_form_empty(self):
        self.assertEqual(validate._line_carries_content("DQ-002"),
                         False)
        self.assertEqual(validate._line_carries_content("R-7"),
                         False)

    def test_neighbouring_token_forms_keep_content(self):
        # The stated bound of the content test, seat 8
        # observation 3, charged nowhere: two alphanumeric
        # tokens pass the content test as the cure states
        # it, and the genuine short word control stands.
        self.assertEqual(validate._line_carries_content("ab1 cd2"),
                         True)
        self.assertEqual(
            validate._line_carries_content("\u4e2d\u6587"), True)


class Ch63DeciderConflictTest(unittest.TestCase):
    """F4-8-7, the decider limb under FLAG 8: two decider
    lines naming two different deciders in one block take
    a finding naming the conflict of form, and no
    authority judgement stands in it. The exact repetition
    bound form stands as recorded."""

    Z04_BODY = (BLOCK + "Ruled by: Captain JP\n\n"
                "Ruled by: Sam\n\n"
                "Ruled. The harbour light burns all night.\n\n"
                "Outcome: Closed.\n\n"
                "Landed in the harbour log.\n")
    Z05_BODY = (BLOCK + "Ruled by: Captain JP\n\n"
                "Ruled by: Captain JP\n\n"
                "Ruled. The harbour light burns all night.\n\n"
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

    def test_two_different_deciders_take_a_finding(self):
        text = HEAD + entry(self.Z04_BODY)
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        conflicts = self._conflict_findings(output)
        self.assertEqual(len(conflicts), 1)
        statement = h.finding_statement(conflicts[0])
        self.assertIn("Sam", statement)
        self.assertIn("Captain JP", statement)

    def test_conflict_finding_moves_the_exit(self):
        code, _combined = run_cli_on(
            self, HEAD + entry(self.Z04_BODY))
        self.assertEqual(code, 1)

    def test_exact_repetition_takes_no_conflict_finding(self):
        # The bound form of the finding, seat 8 observation
        # 4: the same decider line doubled word for word
        # adds no conflict and no second name.
        text = HEAD + entry(self.Z05_BODY)
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        self.assertEqual(self._conflict_findings(output), [])
        code, _combined = run_cli_on(self, text)
        self.assertEqual(code, 0)


class Ch63GenuineCreditPinsTest(unittest.TestCase):
    """FLAG 6 pins: the genuine credit controls stand.
    Every test in this class passes before and after."""

    def test_quoted_genuine_paragraph_keeps_group_3_credit(self):
        text = banked_plain_entry(
            "> An unheaded paragraph stands here.")
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        self.assertIn("DQ-001", group_members(
            output, "unheaded paragraphs"))
        self.assertEqual(sums_agree(output), True)

    def test_two_cjk_characters_forming_one_word_keep_group_2(self):
        text = banked_block_entry("\u4e2d\u6587")
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        self.assertIn("DQ-001", group_members(
            output, "level 4 decision block"))
        self.assertEqual(sums_agree(output), True)


if __name__ == "__main__":
    unittest.main()
