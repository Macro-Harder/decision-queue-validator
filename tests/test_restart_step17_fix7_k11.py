"""Step 17 fix wave 7, Fix Seat K11 tests, test first.

Charges CH-148 and CH-149, as ruled at section 66 of
design/steps/step-17r-record.md, and prepared at
design/steps/step-17r-triage7-prep.md. Both charges stand
in product/decision_queue_validator/validate.py, at the
field conflict and presence readings.

CH-148 (validate, the field conflict reading, the digit
width identity limb): seat 6 Finding 1 (Low) at
design/steps/step-17r-attack7-6.md. The CH-59
contradictory values Warning fires on two blocks field
values that name the same entry in different digit width
forms (DQ-002 beside DQ-02, in either order, under one
label or across the Blocks and What it blocks alias
pair), where the tool own identifier identity on this
surface is the entry number: heading copies in different
width forms take the duplicate Error as one number, a
lone blocks value in a short width reads as its number,
and a claim token in a short width reads as its number.
Cure bound: at the blocks field value comparison in
_check9_field_conflicts, two values that are each a
single entry identifier naming the one entry number
state no contradiction, in any digit widths; every other
comparison stands as CH-59 stands, exact strings, and a
pair naming two different numbers, in any widths, still
contradicts.

CH-149 (validate, the presence reading, the word
boundary limb): seat 17 finding S17-ATK7-17-03 (Low) at
design/steps/step-17r-attack7-17.md. The decided entry
outcome and landing prefixes carry no word boundary in
_field_value_present, whose prefixes read through
_alias_prefix_matches as a plain startswith for every
prefix but the Question as put alias, so a label that
merely opens with those words (Ruling outcomeXYZ,
Ruling outcomes, Form outcomeXYZ, Where the ruling
landedXYZ, Where the ruling landedness, Where the
settlement landedXYZ) counts as the outcome or the
landing record and the decided entry passes in silence.
Cure bound: the outcome and landing prefixes read at
their word boundary in the CH-92 form, the same form the
Question as put alias and the Options alias take: the
prefix standing alone as the whole label, or standing
before a character that is no letter, digit, or
underscore, counts; a continuation of the final word by
a letter, a digit, or an underscore does not. The
recorded boundary continuations stand credited exactly
as before: the corpus forms Ruling outcome for this
entry and Ruling outcome, verifier limb, whose next
characters are a plain space and a comma, and the exact
prefix labels themselves.

Constructions stand in the attack papers own shapes:
the seat 6 two entry Open base of round 7 attack seat 6
(cases t65, u01 to u04, and t64) and the seat 17 decided
base of round 7 attack seat 17 (cases j23 to j29, j37,
and j38).

Copyright: J.P. Picard aka Macro-Harder
"""

import unittest

import dqv_harness as h

validate = h.import_module("validate")

HEAD = "# Decision queue\n\n"


def open_queue(blocks_paragraphs):
    """The seat 6 base: DQ-001 Open carrying the blocks
    paragraphs under test, DQ-002 Open complete."""
    parts = [HEAD,
             "### DQ-001: Alpha question\n\n",
             "Status: Open\n\n",
             "Question: Which option should we take?\n\n",
             "Options: Option A, Option B\n\n",
             "Cost of deciding late: Work stays blocked.\n\n"]
    for paragraph in blocks_paragraphs:
        parts.append(paragraph + "\n\n")
    parts.extend([
        "This entry is waiting for a decision.\n\n",
        "### DQ-002: Beta question\n\n",
        "Status: Open\n\n",
        "Question: Which other option should we take?\n\n",
        "Options: Option C, Option D\n\n",
        "Cost of deciding late: Work stays blocked.\n\n",
        "Blocks: DQ-001\n\n",
        "This second entry is waiting for a decision.\n",
    ])
    return "".join(parts).encode("utf-8")


def decided_queue(outcome_line, landing_line):
    """The seat 17 decided base (the f00 and j23 shape):
    one entry, Status RULED closed, with its decider,
    ruling text, and the outcome and landing lines under
    test."""
    parts = [HEAD,
             "### DQ-001: A decided sample\n\n",
             "Status: RULED, closed\n\n",
             "Ruled by: Captain JP, option A stands.\n\n",
             "Ruling text: Option A stands.\n\n"]
    if outcome_line is not None:
        parts.append(outcome_line + "\n\n")
    if landing_line is not None:
        parts.append(landing_line + "\n")
    return "".join(parts).encode("utf-8")


OUTCOME_OK = "Ruling outcome: Option A adopted."
LANDING_OK = "Where the ruling landed: DQ-001 record."


def run(data, name="fix7_k11.md"):
    model, output = h.run_pipeline(data, name)
    if output is None or h.is_failure_result(model):
        raise AssertionError("pipeline returned a failure")
    return output


def cli_codes(data):
    path = h.temp_input(data)
    codes = []
    for subcommand in ("validate", "render"):
        code, _out, _err = h.run_cli(subcommand, path)
        codes.append(code)
    return codes


def statements(output, entry_id="DQ-001"):
    return [h.finding_statement(f) or ""
            for f in h.findings_for(output, entry_id=entry_id)]


def conflict_statements(output):
    return [s for s in statements(output)
            if "contradictory values" in s]


def missing_outcome_statements(output):
    return [s for s in statements(output)
            if "No outcome is recorded" in s]


def missing_landing_statements(output):
    return [s for s in statements(output)
            if "No landing record is recorded" in s]


# ---------------------------------------------------------------------
# CH-148: the digit width identity limb of the blocks
# field value comparison
# ---------------------------------------------------------------------

class Ch148WidthIdentityTest(unittest.TestCase):
    """CH-148, seat 6 Finding 1: two blocks values naming
    the one entry number in different digit widths state
    no contradiction."""

    def test_width_pair_same_label_no_conflict(self):
        # Case t65: Blocks DQ-002 then Blocks DQ-02.
        data = open_queue(["Blocks: DQ-002", "Blocks: DQ-02"])
        output = run(data, "fix7_k11_t65.md")
        self.assertEqual(conflict_statements(output), [])
        _waiting, blocking = h.waiting_and_blocking(output)
        self.assertEqual(int(blocking), 2)
        self.assertEqual(cli_codes(data), [0, 0])

    def test_width_pair_reversed_no_conflict(self):
        # Case u02: Blocks DQ-02 then Blocks DQ-002.
        data = open_queue(["Blocks: DQ-02", "Blocks: DQ-002"])
        output = run(data, "fix7_k11_u02.md")
        self.assertEqual(conflict_statements(output), [])
        _waiting, blocking = h.waiting_and_blocking(output)
        self.assertEqual(int(blocking), 2)
        self.assertEqual(cli_codes(data), [0, 0])

    def test_width_alias_pair_no_conflict(self):
        # Case u04: Blocks DQ-002 then What it blocks DQ-02.
        data = open_queue(
            ["Blocks: DQ-002", "What it blocks: DQ-02"])
        output = run(data, "fix7_k11_u04.md")
        self.assertEqual(conflict_statements(output), [])
        _waiting, blocking = h.waiting_and_blocking(output)
        self.assertEqual(int(blocking), 2)
        self.assertEqual(cli_codes(data), [0, 0])

    def test_width_forms_same_number_no_conflict(self):
        # The identity at further widths of the one number:
        # one digit, four digit, and six digit forms of
        # entry number 2 against the three digit form.
        for first, second in (("DQ-002", "DQ-2"),
                              ("DQ-0002", "DQ-02"),
                              ("DQ-002", "DQ-000002")):
            with self.subTest(first=first, second=second):
                data = open_queue(
                    ["Blocks: " + first, "Blocks: " + second])
                output = run(data, "fix7_k11_widths.md")
                self.assertEqual(conflict_statements(output), [])
                self.assertEqual(cli_codes(data), [0, 0])

    def test_width_pair_then_genuine_value_conflicts_on_it(self):
        # The width pair states one value; a third value
        # that names no entry contradicts that one value,
        # and the finding names the third value against the
        # governing first value, not the width twin.
        data = open_queue(
            ["Blocks: DQ-002", "Blocks: DQ-02", "Blocks: none"])
        output = run(data, "fix7_k11_width_third.md")
        conflicts = conflict_statements(output)
        self.assertEqual(len(conflicts), 1)
        self.assertIn('"none"', conflicts[0])
        self.assertIn("stands as \"DQ-002\"", conflicts[0])
        self.assertEqual(cli_codes(data), [1, 1])


class Ch148PinsTest(unittest.TestCase):
    """CH-148 pins, passing before and after: the CH-59
    reading stands whole outside the charged width forms."""

    def test_identical_short_width_pair_no_conflict(self):
        # Control u03: Blocks DQ-02 stated twice in
        # identical strings passes in silence.
        data = open_queue(["Blocks: DQ-02", "Blocks: DQ-02"])
        output = run(data, "fix7_k11_u03.md")
        self.assertEqual(conflict_statements(output), [])
        self.assertEqual(cli_codes(data), [0, 0])

    def test_lone_short_width_value_clean(self):
        # Control u01: the lone value Blocks DQ-02 reads as
        # its number, Blocking 2, at exit 0.
        data = open_queue(["Blocks: DQ-02"])
        output = run(data, "fix7_k11_u01.md")
        self.assertEqual(conflict_statements(output), [])
        _waiting, blocking = h.waiting_and_blocking(output)
        self.assertEqual(int(blocking), 2)
        self.assertEqual(cli_codes(data), [0, 0])

    def test_genuine_blocks_conflict_still_fires(self):
        # The CH-59 charged form stands: DQ-002 beside none
        # takes its one contradictory values Warning.
        data = open_queue(["Blocks: DQ-002", "Blocks: none"])
        output = run(data, "fix7_k11_genuine.md")
        self.assertEqual(len(conflict_statements(output)), 1)
        self.assertEqual(cli_codes(data), [1, 1])

    def test_different_numbers_mixed_widths_still_conflict(self):
        # Two different entry numbers contradict in any
        # widths: DQ-02 names entry 2, DQ-003 names entry 3.
        data = open_queue(["Blocks: DQ-02", "Blocks: DQ-003"])
        output = run(data, "fix7_k11_diff_numbers.md")
        self.assertEqual(len(conflict_statements(output)), 1)
        self.assertEqual(cli_codes(data), [1, 1])

    def test_triple_with_genuine_conflict_one_finding(self):
        # Case t64: DQ-002, none, DQ-002 takes exactly one
        # conflict finding, on the genuine contradiction.
        data = open_queue(
            ["Blocks: DQ-002", "Blocks: none", "Blocks: DQ-002"])
        output = run(data, "fix7_k11_t64.md")
        self.assertEqual(len(conflict_statements(output)), 1)
        _waiting, blocking = h.waiting_and_blocking(output)
        self.assertEqual(int(blocking), 2)
        self.assertEqual(cli_codes(data), [1, 1])


# ---------------------------------------------------------------------
# CH-149: the word boundary limb of the outcome and
# landing presence prefixes
# ---------------------------------------------------------------------

OUTCOME_PREFIXES = ("Ruling outcome", "Form outcome")
LANDING_PREFIXES = ("Where the ruling landed",
                    "Where the settlement landed",
                    "Where the settlement is to land",
                    "Where it landed")


def _field_entry(label, value="Option A adopted."):
    return {"fields": [{"label": label, "value": value}]}


class Ch149PrefixUnitTest(unittest.TestCase):
    """CH-149 at the presence helper itself: the outcome
    and landing prefixes read at their word boundary."""

    def test_outcome_prefixes_refuse_continued_words(self):
        for label in ("Ruling outcomeXYZ", "Ruling outcomes",
                      "Form outcomeXYZ"):
            with self.subTest(label=label):
                self.assertFalse(validate._field_value_present(
                    _field_entry(label),
                    ("Decision", "Outcome",
                     "Outcome of this decision"),
                    prefixes=OUTCOME_PREFIXES,
                    require_word_character=True))

    def test_landing_prefixes_refuse_continued_words(self):
        for label in ("Where the ruling landedXYZ",
                      "Where the ruling landedness",
                      "Where the settlement landedXYZ",
                      "Where the settlement is to landXYZ",
                      "Where it landedXYZ"):
            with self.subTest(label=label):
                self.assertFalse(validate._field_value_present(
                    _field_entry(label, "DQ-001 record."),
                    ("Landing", "Landing record", "Lands",
                     "Landed"),
                    prefixes=LANDING_PREFIXES,
                    require_word_character=True))

    def test_underscore_continuation_refused(self):
        # An underscore continues the final word, as at the
        # Question and Options alias boundaries.
        self.assertFalse(validate._field_value_present(
            _field_entry("Ruling outcome_extra"),
            ("Decision", "Outcome"), prefixes=OUTCOME_PREFIXES,
            require_word_character=True))

    def test_exact_prefix_labels_credited(self):
        # Controls, passing before and after: each prefix
        # standing as the whole label counts as before.
        for prefix in OUTCOME_PREFIXES:
            with self.subTest(prefix=prefix):
                self.assertTrue(validate._field_value_present(
                    _field_entry(prefix),
                    ("Decision", "Outcome"),
                    prefixes=OUTCOME_PREFIXES,
                    require_word_character=True))
        for prefix in LANDING_PREFIXES:
            with self.subTest(prefix=prefix):
                self.assertTrue(validate._field_value_present(
                    _field_entry(prefix, "DQ-001 record."),
                    ("Landing", "Landing record"),
                    prefixes=LANDING_PREFIXES,
                    require_word_character=True))

    def test_boundary_continuations_credited(self):
        # Controls, passing before and after: the recorded
        # boundary continuations of the corpus stand
        # credited, the next character a plain space or a
        # comma, and a hyphen continuation stands at the
        # boundary as it does at the Question alias.
        for label in ("Ruling outcome for this entry",
                      "Ruling outcome, verifier limb"):
            with self.subTest(label=label):
                self.assertTrue(validate._field_value_present(
                    _field_entry(label),
                    ("Decision", "Outcome"),
                    prefixes=OUTCOME_PREFIXES,
                    require_word_character=True))
        self.assertTrue(validate._field_value_present(
            _field_entry("Where the ruling landed - the record",
                         "DQ-001 record."),
            ("Landing", "Landing record"),
            prefixes=LANDING_PREFIXES,
            require_word_character=True))

    def test_question_alias_boundary_unchanged(self):
        # The CH-92 pins stand whole under this cure: the
        # charged continuations refused, the recorded forms
        # credited, exactly as fix wave 5 left them.
        self.assertFalse(validate._field_value_present(
            _field_entry("Question as putative",
                         "Which option should we take?"),
            validate._QUESTION_LABELS,
            prefixes=("Question as put",)))
        for label in ("Question as put",
                      "Question as put on the Questions space"):
            with self.subTest(label=label):
                self.assertTrue(validate._field_value_present(
                    _field_entry(
                        label, "Which option should we take?"),
                    validate._QUESTION_LABELS,
                    prefixes=("Question as put",)))


class Ch149PresencePipelineTest(unittest.TestCase):
    """CH-149 on the decided base: a continued word label
    standing as the only outcome or landing line takes
    its missing evidence statement at exit 1."""

    def test_outcome_gibberish_label_takes_missing_outcome(self):
        # Case j24.
        data = decided_queue(
            "Ruling outcomeXYZ: Option A adopted.", LANDING_OK)
        output = run(data, "fix7_k11_j24.md")
        self.assertEqual(len(missing_outcome_statements(output)), 1)
        self.assertEqual(missing_landing_statements(output), [])
        self.assertEqual(cli_codes(data), [1, 1])

    def test_outcome_plural_label_takes_missing_outcome(self):
        # Case j25.
        data = decided_queue(
            "Ruling outcomes: Option A adopted.", LANDING_OK)
        output = run(data, "fix7_k11_j25.md")
        self.assertEqual(len(missing_outcome_statements(output)), 1)
        self.assertEqual(cli_codes(data), [1, 1])

    def test_form_outcome_gibberish_takes_missing_outcome(self):
        # Case j26.
        data = decided_queue(
            "Form outcomeXYZ: Option A adopted.", LANDING_OK)
        output = run(data, "fix7_k11_j26.md")
        self.assertEqual(len(missing_outcome_statements(output)), 1)
        self.assertEqual(cli_codes(data), [1, 1])

    def test_landing_gibberish_label_takes_missing_landing(self):
        # Case j27.
        data = decided_queue(
            OUTCOME_OK,
            "Where the ruling landedXYZ: DQ-001 record.")
        output = run(data, "fix7_k11_j27.md")
        self.assertEqual(len(missing_landing_statements(output)), 1)
        self.assertEqual(missing_outcome_statements(output), [])
        self.assertEqual(cli_codes(data), [1, 1])

    def test_landing_continued_word_takes_missing_landing(self):
        # Case j28.
        data = decided_queue(
            OUTCOME_OK,
            "Where the ruling landedness: DQ-001 record.")
        output = run(data, "fix7_k11_j28.md")
        self.assertEqual(len(missing_landing_statements(output)), 1)
        self.assertEqual(cli_codes(data), [1, 1])

    def test_settlement_landing_gibberish_takes_missing(self):
        # Case j29.
        data = decided_queue(
            OUTCOME_OK,
            "Where the settlement landedXYZ: DQ-001 record.")
        output = run(data, "fix7_k11_j29.md")
        self.assertEqual(len(missing_landing_statements(output)), 1)
        self.assertEqual(cli_codes(data), [1, 1])

    def test_decided_control_clean(self):
        # Control j23, passing before and after: the exact
        # labels stand present and the entry is clean.
        data = decided_queue(OUTCOME_OK, LANDING_OK)
        output = run(data, "fix7_k11_j23.md")
        self.assertEqual(h.findings_of(output), [])
        self.assertEqual(cli_codes(data), [0, 0])

    def test_outcome_boundary_continuation_stands_present(self):
        # Pin, passing before and after: the corpus form
        # Ruling outcome for this entry counts as the
        # outcome record under the boundary reading.
        data = decided_queue(
            "Ruling outcome for this entry: Option A adopted.",
            LANDING_OK)
        output = run(data, "fix7_k11_outcome_cont.md")
        self.assertEqual(missing_outcome_statements(output), [])
        self.assertEqual(cli_codes(data), [0, 0])

    def test_broken_outcome_prefix_takes_missing_outcome(self):
        # Contrast j37, passing before and after: the
        # prefix itself cut short records no outcome.
        data = decided_queue(
            "Ruling outcom: Option A adopted.", LANDING_OK)
        output = run(data, "fix7_k11_j37.md")
        self.assertEqual(len(missing_outcome_statements(output)), 1)
        self.assertEqual(cli_codes(data), [1, 1])

    def test_broken_landing_prefix_takes_missing_landing(self):
        # Contrast j38, passing before and after: the
        # prefix itself cut short records no landing.
        data = decided_queue(
            OUTCOME_OK, "Where the ruling lande: DQ-001 record.")
        output = run(data, "fix7_k11_j38.md")
        self.assertEqual(len(missing_landing_statements(output)), 1)
        self.assertEqual(cli_codes(data), [1, 1])


if __name__ == "__main__":
    unittest.main()
