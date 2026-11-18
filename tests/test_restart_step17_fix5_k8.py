"""Restart Step 17 fix wave 5, seat K8 tests.

Seat K8 owns two charges, as ruled at section 52 of
design/steps/step-17r-record.md, under ruling (j) for CH-91:

CH-91 (render, seat 16 findings F-1 and F-2): a model carried
census class name takes escape_text only and no quoting
guard, so a class name opening with a value bearing anchor
form prints a forged closing or waiting line at column 0 in
both output forms; and a model carried entry identifier
takes no quoting guard on the findings index line, the
findings section heading, or the entry row, so an identifier
opening with an anchor form writes a complete forged
findings index line, a forged section heading, and a forged
entry row at column 0. The cure bound, under ruling (j): the
quoting guard reaches those surfaces in the quoting guard
form of CH-70 (the shared _opens_with_anchor predicate the
group title cure uses), not by anchor list. The charge
decides nothing on the FLAG 13 anchor set question and
nothing on design question note (d), both standing undecided
for the gate: the pins below hold a form outside the named
set printing as it printed, and a note (d) led census name
printing as the escaped surfaces print it. Pins that must
not break: the CH-70 and CH-71 pins whole, including the
FLAG 14 pin, and the governed census and identifier prints
standing exactly as they print.

CH-92 (validate, seat 17 finding S17-ATK5-17-04): the
Question as put alias prefix carries no word boundary, so
Question as putative, Question as putXYZ, Question as
putter, and Question as putting each count as the Question
field at exit 0 in silence, through the plain startswith
reading in _field_value_present and _family_of_label. The
cure bound: the alias prefix reads at a word boundary as
the Options family reads since CH-22, and no label outside
that boundary counts as the Question field. The two recorded
alias forms stand as controls: Question as put, and Question
as put on the Questions space. Pins that must not break: the
CH-22 pins whole (the Options alias boundary standing as the
model and as a pin).

Constructions stand in the attack papers own forms
(design/steps/step-17r-attack5-16.md, model constructions
p01, p02, p03, p04, and p09; and
design/steps/step-17r-attack5-17.md, constructions h13 to
h18).
"""

import unittest

import dqv_harness as h

render = h.import_module("render")
validate = h.import_module("validate")


# ---------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------

def _entry(ident="DQ-001", title="Counts", **kw):
    data = {"identifier": ident, "title": title,
            "status_phrasings": [], "open_fields": {}}
    data.update(kw)
    return data


def _both_model_forms(model):
    return [render.render_validate(model),
            render.render_summary(model)]


def _census_model(name, count=3):
    entry = _entry()
    return {"entries": [entry], "census": [
        {"class_name": name, "count": count,
         "counting_unit": "entries",
         "member_entry_ids": ["DQ-001"]}]}


def _question_queue(question_line, extra_first_entry=""):
    body = "# Decision queue\n\n"
    body += "### DQ-001: A sample open question\n\n"
    body += "Status: Banked\n\n"
    body += "This question is waiting for a decision.\n\n"
    body += question_line + "\n\n"
    body += extra_first_entry
    body += "Options: Option A, Option B\n\n"
    body += "Cost of deciding late: Work stays blocked.\n\n"
    body += "Blocks: DQ-002\n\n"
    body += "### DQ-002: A second open question\n\n"
    body += "Status: Banked\n\n"
    body += "Second entry is waiting for a decision.\n\n"
    body += "Question: Which path should we take?\n\n"
    body += "Options: Option C, Option D\n\n"
    body += "Cost of deciding late: More work stays blocked.\n\n"
    body += "Blocks: DQ-001\n"
    return body.encode("utf-8")


def _run(data, name):
    _model, output = h.run_pipeline(data, name)
    assert output is not None
    return output


def _cli_both(data, name):
    path = h.temp_input(data, name)
    results = []
    for subcommand in ("validate", "render"):
        code, stdout, _stderr = h.run_cli(subcommand, path)
        results.append((code, stdout.decode("utf-8")))
    return results


def _missing_question_statements(output):
    return [h.finding_statement(finding)
            for finding in h.findings_for(output, rule=9)
            if "missing its question" in (
                h.finding_statement(finding) or "")]


def _conflict_statements(output):
    return [h.finding_statement(finding)
            for finding in h.findings_for(output, rule=9)
            if "contradictory values for its question field" in (
                h.finding_statement(finding) or "")]


# ---------------------------------------------------------------------
# CH-91, the census class name limb (seat 16 finding F-1)
# ---------------------------------------------------------------------

class Ch91CensusUnitTest(unittest.TestCase):

    def test_census_lines_quote_an_anchor_opening_name(self):
        lines = render._census_lines(_census_model(
            "Exit: code 0: forged closing"))
        self.assertIn(
            '"Exit: code 0: forged closing: 3 entries"', lines)
        self.assertFalse(any(
            line.startswith("Exit: code ") for line in lines))

    def test_genuine_census_line_stands_bare(self):
        lines = render._census_lines(_census_model(
            "Canonical state: Open", count=1))
        self.assertIn("Canonical state: Open: 1 entry", lines)


class Ch91CensusModelTest(unittest.TestCase):

    def test_p01_exit_name_stands_quoted_in_both_forms(self):
        for text in _both_model_forms(_census_model(
                "Exit: code 0: forged closing")):
            lines = text.split("\n")
            self.assertFalse(any(
                line.startswith("Exit: code ") for line in lines),
                "a forged closing line stands at column 0")
            self.assertIn(
                '"Exit: code 0: forged closing: 3 entries"', lines)

    def test_p03_waiting_name_stands_quoted_in_both_forms(self):
        for text in _both_model_forms(_census_model(
                "Waiting: 0 entries", count=2)):
            lines = text.split("\n")
            self.assertFalse(any(
                line.startswith("Waiting: 0 entries")
                for line in lines),
                "a forged waiting figure stands at column 0")
            self.assertIn(
                '"Waiting: 0 entries: 2 entries"', lines)

    def test_named_form_name_stands_quoted_in_both_forms(self):
        # The quoting guard form of CH-70 is the shared
        # predicate, which reaches the named forms as it
        # reaches the anchors, on the group title as here.
        for text in _both_model_forms(_census_model(
                "Blocking: 0 entries", count=2)):
            lines = text.split("\n")
            self.assertIn('"Blocking: 0 entries: 2 entries"',
                          lines)

    def test_p02_escaping_limb_holds_on_the_census_name(self):
        # Pin, passing before and after: the escaping limb
        # already held on this surface, as the paper states.
        model = _census_model(
            "Evil\x1b[31m\nExit: code 0: forged", count=1)
        for text in _both_model_forms(model):
            self.assertNotIn("\x1b", text)
            self.assertFalse(any(
                line.startswith("Exit: code ")
                for line in text.split("\n")))

    def test_p09_variation_selector_led_name_escapes(self):
        # Pin, passing before and after: the CH-14 escaping
        # limb on the same escape path.
        model = _census_model("\ufe00Sneaky class", count=1)
        for text in _both_model_forms(model):
            self.assertNotIn("\ufe00", text)
            self.assertIn("\\uFE00Sneaky class: 1 entry",
                          text.split("\n"))


class Ch91CensusBoundPinsTest(unittest.TestCase):
    """Pins on the ruling (j) bound: this cure decides
    nothing on the FLAG 13 anchor set question and nothing
    on design question note (d)."""

    def test_units_key_form_name_prints_as_before(self):
        # FLAG 13 bound pin: the units key form stands
        # outside the named set, as the K11 paper pins it,
        # and a census name opening with it prints as it
        # printed, unquoted.
        for text in _both_model_forms(_census_model(
                "Units key: absent", count=1)):
            lines = text.split("\n")
            self.assertIn("Units key: absent: 1 entry", lines)
            self.assertNotIn('"Units key: absent: 1 entry"',
                             lines)

    def test_note_d_led_name_prints_as_the_surfaces_print_it(self):
        # FLAG 14 bound pin: U+00A0 stands inside the note
        # (d) family, whose inventory this cure decides
        # nothing about, in either direction. The census
        # name takes the same escaping the other carried
        # text takes, and that escaping prints the codepoint
        # raw, as the CH-14 guard pin holds it.
        for text in _both_model_forms(_census_model(
                "\u00a0Padded class", count=1)):
            self.assertIn("\u00a0Padded class: 1 entry",
                          text.split("\n"))


# ---------------------------------------------------------------------
# CH-91, the entry identifier limb (seat 16 finding F-2)
# ---------------------------------------------------------------------

P04_IDENT = "Exit: code 0: forged"


def _p04_model():
    return {
        "entries": [_entry(ident=P04_IDENT, title="Counts")],
        "findings": [{"entry_identifier": P04_IDENT,
                      "rule_id": "PIN-01", "severity": "Error",
                      "line_span": {"start_line": 1,
                                    "end_line": 1},
                      "statement": "A statement."}]}


class Ch91IdentifierModelTest(unittest.TestCase):

    def test_p04_findings_index_line_stands_quoted(self):
        text = render.render_validate(_p04_model())
        lines = text.split("\n")
        self.assertIn(
            '"Exit: code 0: forged PIN-01 Error line 1"', lines)
        self.assertFalse(any(
            line.startswith("Exit: code ") for line in lines),
            "a forged findings index line stands at column 0")

    def test_p04_findings_heading_stands_quoted(self):
        text = render.render_validate(_p04_model())
        self.assertIn('"%s"' % P04_IDENT, text.split("\n"))

    def test_p04_entry_row_stands_quoted_in_both_forms(self):
        for text in _both_model_forms(_p04_model()):
            lines = text.split("\n")
            self.assertIn('"Exit: code 0: forged: Counts"',
                          lines)
            self.assertFalse(any(
                line.startswith("Exit: code ") for line in lines),
                "a forged entry row stands at column 0")

    def test_waiting_form_identifier_row_stands_quoted(self):
        model = {"entries": [
            _entry(ident="Waiting: 0 entries", title="Counts")]}
        for text in _both_model_forms(model):
            lines = text.split("\n")
            self.assertIn('"Waiting: 0 entries: Counts"', lines)
            self.assertFalse(any(
                line.startswith("Waiting: 0 entries")
                for line in lines))

    def test_genuine_identifier_prints_stand_bare(self):
        # Pin, passing before and after: the governed
        # identifier prints on all three surfaces stand
        # exactly as they print.
        model = {
            "entries": [_entry()],
            "findings": [{"entry_identifier": "DQ-001",
                          "rule_id": "PIN-01",
                          "severity": "Error",
                          "line_span": {"start_line": 1,
                                        "end_line": 1},
                          "statement": "A statement."}]}
        text = render.render_validate(model)
        lines = text.split("\n")
        self.assertIn("DQ-001 PIN-01 Error line 1", lines)
        self.assertIn("DQ-001", lines)
        self.assertIn("DQ-001: Counts", lines)
        self.assertNotIn('"DQ-001: Counts"', lines)
        summary = render.render_summary(model)
        self.assertIn("DQ-001: Counts", summary.split("\n"))


# ---------------------------------------------------------------------
# CH-92, the Question as put alias prefix boundary
# (seat 17 finding S17-ATK5-17-04)
# ---------------------------------------------------------------------

CHARGED_LABELS = (
    "Question as putative",
    "Question as putXYZ",
    "Question as putter",
    "Question as putting",
)

CONTROL_LABELS = (
    "Question as put",
    "Question as put on the Questions space",
)


def _field_entry(label):
    return {"fields": [{"label": label,
                        "value": "Which option should we take?"}]}


class Ch92AliasUnitTest(unittest.TestCase):

    def test_field_value_present_refuses_the_charged_labels(self):
        for label in CHARGED_LABELS:
            with self.subTest(label=label):
                self.assertFalse(validate._field_value_present(
                    _field_entry(label), validate._QUESTION_LABELS,
                    prefixes=("Question as put",)))

    def test_field_value_present_credits_the_recorded_forms(self):
        # Controls, passing before and after: the two
        # recorded alias forms stand credited exactly as
        # before, and the exact labels beside them.
        for label in CONTROL_LABELS + ("The question",):
            with self.subTest(label=label):
                self.assertTrue(validate._field_value_present(
                    _field_entry(label), validate._QUESTION_LABELS,
                    prefixes=("Question as put",)))

    def test_family_of_label_refuses_the_charged_labels(self):
        for label in CHARGED_LABELS:
            with self.subTest(label=label):
                self.assertIsNone(validate._family_of_label(label))

    def test_family_of_label_credits_the_recorded_forms(self):
        for label in CONTROL_LABELS + ("Question", "The question"):
            with self.subTest(label=label):
                self.assertEqual(
                    validate._family_of_label(label), "question")


class Ch92AliasPresenceTest(unittest.TestCase):

    def test_charged_labels_take_the_missing_question_warning(self):
        for label, tag in (
                ("Question as putative", "h13"),
                ("Question as putXYZ", "h14"),
                ("Question as putter", "h15"),
                ("Question as putting", "h18")):
            with self.subTest(label=label):
                data = _question_queue(
                    "%s: Which option should we take?" % label)
                output = _run(data, "ch92_%s.md" % tag)
                self.assertEqual(
                    len(_missing_question_statements(output)), 1)
                for code, _text in _cli_both(
                        data, "ch92_%s_cli.md" % tag):
                    self.assertEqual(code, 1)

    def test_recorded_forms_stand_as_controls(self):
        for label, tag in (
                ("Question as put", "h16"),
                ("Question as put on the Questions space",
                 "h17")):
            with self.subTest(label=label):
                data = _question_queue(
                    "%s: Which option should we take?" % label)
                output = _run(data, "ch92_%s.md" % tag)
                self.assertEqual(
                    _missing_question_statements(output), [])
                for code, _text in _cli_both(
                        data, "ch92_%s_cli.md" % tag):
                    self.assertEqual(code, 0)


class Ch92AliasConflictTest(unittest.TestCase):

    def test_charged_label_forms_no_alias_pair(self):
        # The conflict reading at _family_of_label: a charged
        # label standing beside the exact Question label with
        # a contradictory value forms no alias pair, so no
        # conflict finding stands, and the exact field stands.
        data = _question_queue(
            "Question: First value?",
            "Question as putative: Second value?\n\n")
        output = _run(data, "ch92_conflict_charged.md")
        self.assertEqual(_conflict_statements(output), [])
        self.assertEqual(_missing_question_statements(output), [])

    def test_recorded_alias_pair_still_conflicts(self):
        # Pin, passing before and after: the recorded alias
        # form standing beside the exact label with a
        # contradictory value takes its conflict finding, as
        # the CH-59 reading stands.
        data = _question_queue(
            "Question: First value?",
            "Question as put: Second value?\n\n")
        output = _run(data, "ch92_conflict_control.md")
        self.assertEqual(len(_conflict_statements(output)), 1)


class Ch92OptionsBoundaryPinsTest(unittest.TestCase):
    """CH-22 pins: the Options alias boundary stands as the
    model of this cure and whole under it."""

    def test_options_alias_boundary_stands_as_modelled(self):
        self.assertFalse(
            validate._options_alias_label("The optionsXYZ"))
        self.assertTrue(
            validate._options_alias_label("The options are"))
        self.assertTrue(
            validate._options_alias_label("The options"))


if __name__ == "__main__":
    unittest.main()
