"""Step 17 fix wave 4, Fix Seat K2 tests, test first.

Charges CH-54, CH-55, and CH-56, in that order, as ruled at
section 38 of design/steps/step-17r-record.md, ruling (e)
especially, and prepared at design/steps/step-17r-triage4-prep.md.
The run set ground is stated once for the whole family: the run
characters are read by Unicode class, not by enumerated list.
The class boundary pinned here, named expressly by Unicode
general category, is: format characters (category Cf), control
characters (category Cc), separator characters (categories Zs,
Zl, and Zp), and mark characters (categories Mn, Mc, and Me).
Every character enumerated in ruling (d) and every governed pin
stands as a pin inside that class reading. Characters in the
symbol and letter categories that present as blank (a braille
pattern blank, the hangul fillers, an object replacement
character) stand outside the run class: at the Status leading
and separator surfaces they take the near marker signal rather
than a silent demotion or a silent folded extraction, on the
cure bounds the triage preparation states for CH-55 and CH-56.
The seat 19 combination limb (an outside character defeating
the near marker signal on the same line) is disposed inside
CH-55 in this file. The CH-21 tab forms and the note (f) guard
form stand narrower by governing text and are not moved: the
plain spaces separator guard below passes before and after the
cure, as a guard should.
"""

import unittest

import dqv_harness as h


def _elements(model, entry_id="DQ-001"):
    entry = h.entry_by_id(model, entry_id)
    if entry is None:
        return []
    return h.as_list(h.get(entry, "status_elements", "elements"))


def _kinds(model, entry_id="DQ-001"):
    return [(h.text_of(h.get(el, "kind", "element_kind")) or "")
            for el in _elements(model, entry_id)]


def _dispositions(model, entry_id="DQ-001"):
    out = []
    for el in _elements(model, entry_id):
        tup = h.get(el, "tuple", "element_tuple", "core_tuple")
        out.append(h.text_of(tuple(tup)[0]) if tup is not None
                   else h.text_of(h.get(el, "disposition")))
    return out


def _entry(status_line, first_paragraph=None):
    body = h._header_block()
    body += "### DQ-001: A sample open question\n\n"
    if first_paragraph is not None:
        body += first_paragraph + "\n\n"
    body += status_line
    if not status_line.endswith("\n"):
        body += "\n"
    body += "This question is waiting for a decision.\n\n"
    body += "Question: Which option should we take?\n\n"
    body += "Options: Option A, Option B\n\n"
    body += "Cost of deciding late: Work stays blocked.\n\n"
    body += "Blocks: DQ-002\n"
    return body.encode("utf-8")


def _two_entry_file(prefix):
    body = h._header_block()
    body += "### DQ-001: First question\n\nStatus: Banked\n\n"
    body += "Question: Which option should we take?\n\n"
    body += "Options: Option A, Option B\n\n"
    body += "Cost of deciding late: Work stays blocked.\n\n"
    body += "Blocks: DQ-002\n\n"
    body += "This question is waiting for a decision.\n\n"
    body += prefix + "### DQ-002: Second question\n\n"
    body += "Status: Banked\n\n"
    body += "Question: Which other option should we take?\n\n"
    body += "Options: Option C, Option D\n\n"
    body += "Cost of deciding late: More work stays blocked.\n\n"
    body += "Blocks: DQ-001\n\n"
    body += "This question is also waiting for a decision.\n"
    return body.encode("utf-8")


def _cr_tail_file(tail_parts):
    body = h._header_block()
    body += "### DQ-001: A sample open question"
    for part in tail_parts:
        body += "\r" + part
    body += "\n\nQuestion: Which option should we take?\n\n"
    body += "Options: Option A, Option B\n\n"
    body += "Cost of deciding late: Work stays blocked.\n\n"
    body += "Blocks: DQ-002\n\n"
    body += "This question is waiting for a decision.\n"
    return body.encode("utf-8")


def _preamble_file(prefix, status_line="Status: Parked"):
    body = "# Decision queue\n\n"
    body += prefix + status_line + "\n\n"
    body += "Generated queue shaped input.\n\n"
    body += "### DQ-001: A sample open question\n\n"
    body += "Status: Banked\n\n"
    body += "This question is waiting for a decision.\n\n"
    body += "Question: Which option should we take?\n\n"
    body += "Options: Option A, Option B\n\n"
    body += "Cost of deciding late: Work stays blocked.\n\n"
    body += "Blocks: DQ-002\n"
    return body.encode("utf-8")


# Class representatives outside the ruling (d) enumerated set:
# format characters (Cf), a paragraph separator (Zp), and
# control characters (Cc), as the round 4 papers name them.
CLASS_RUN_CHARS = (
    "\u2029", "\u200e", "\u0000", "\u2061", "\u0086",
    "\u061c", "\u200f", "\u202e", "\u2066", "\u2069",
    "\ufff9", "\u0007", "\u001b", "\u007f", "\u0082",
)

# Blank presenting characters outside the run class: symbol
# and letter categories whose glyph is blank, as seat 17 names
# them (a braille pattern blank, So; hangul fillers, Lo; an
# object replacement character, So).
BLANK_PRESENTING_CHARS = (
    "\u2800", "\u3164", "\u115f", "\ufffc",
)


class Ch54HeadingClassRunTest(unittest.TestCase):
    """CH-54, A4-3-F1 (High): heading recognition reads the
    heading after a leading run read by Unicode class."""

    def test_ch54_heading_prefix_class_characters(self):
        for char in CLASS_RUN_CHARS:
            with self.subTest(char=repr(char)):
                model = h.run_parse(
                    _two_entry_file(char), "ch54_heading.md")
                self.assertFalse(h.is_failure_result(model))
                self.assertIsNotNone(
                    h.entry_by_id(model, "DQ-002"))
                self.assertEqual(len(h.entries_of(model)), 2)

    def test_ch54_heading_prefix_sandwich_run(self):
        model = h.run_parse(
            _two_entry_file("\ufeff\u2029\ufeff"),
            "ch54_sandwich.md")
        self.assertFalse(h.is_failure_result(model))
        self.assertIsNotNone(h.entry_by_id(model, "DQ-002"))
        self.assertEqual(len(h.entries_of(model)), 2)

    def test_ch54_heading_prefix_mixed_class_runs(self):
        for prefix in (" \u200e", "\u200e ", "\u0000\u2029",
                       "\u061c\x0b", " \u0000"):
            with self.subTest(prefix=repr(prefix)):
                model = h.run_parse(
                    _two_entry_file(prefix), "ch54_mixed.md")
                self.assertFalse(h.is_failure_result(model))
                self.assertIsNotNone(
                    h.entry_by_id(model, "DQ-002"))
                self.assertEqual(len(h.entries_of(model)), 2)

    def test_ch54_heading_prefix_ruling_d_pins_inside_class(self):
        # Pins inside the class reading: characters enumerated
        # in ruling (d) keep their cured heading reading.
        for char in ("\u00a0", "\u200b", "\x0b", "\x0c",
                     "\u200c", "\u2060", "\u2028", "\u0085",
                     "\u0301"):
            with self.subTest(char=repr(char)):
                model = h.run_parse(
                    _two_entry_file(char), "ch54_pin.md")
                self.assertFalse(h.is_failure_result(model))
                self.assertIsNotNone(
                    h.entry_by_id(model, "DQ-002"))
                self.assertEqual(len(h.entries_of(model)), 2)


class Ch54CrTailClassRunTest(unittest.TestCase):
    """CH-54, A4-3-F2 (Medium): the carriage return tail
    selection reads its parts under the same class run."""

    def test_ch54_cr_tail_behind_class_characters_is_counted(self):
        for char in ("\u2029", "\u200e", "\u0000"):
            with self.subTest(char=repr(char)):
                model = h.run_parse(
                    _cr_tail_file([char + "Status: Banked"]),
                    "ch54_cr_tail.md")
                self.assertFalse(h.is_failure_result(model))
                self.assertIn("Banked", _dispositions(model))
                self.assertIn(
                    "line start Status line", _kinds(model))

    def test_ch54_cr_tail_second_part_behind_class_character(self):
        model = h.run_parse(
            _cr_tail_file(["Status: Banked",
                           "\u2029Status: Ruled"]),
            "ch54_cr_two_tails.md")
        self.assertFalse(h.is_failure_result(model))
        self.assertIn("Banked", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        # Both occurrences stand counted: the first as the
        # line start Status line and the second as a later
        # Status line, the standing kind for a second line
        # start occurrence, as the CH-36 three marked tails
        # form stands. An earlier form of this pin counted
        # two line start kinds and was corrected on that
        # evidence, in the open in the cluster paper.
        kinds = _kinds(model)
        self.assertEqual(
            kinds.count("line start Status line")
            + kinds.count("later Status line"), 2)


class Ch54StatusLeadingClassRunTest(unittest.TestCase):
    """CH-54, A4-3-F3 (Low): a class character before an entry
    Status line no longer reclassifies it."""

    def test_ch54_status_leading_class_characters(self):
        for char in ("\u2029", "\u200e", "\u0000", "\u061c",
                     "\u0086"):
            with self.subTest(char=repr(char)):
                model = h.run_parse(
                    _entry(char + "Status: Banked\n"),
                    "ch54_status.md")
                self.assertFalse(h.is_failure_result(model))
                self.assertIn(
                    "line start Status line", _kinds(model))
                self.assertIn("Banked", _dispositions(model))

    def test_ch54_variant_marker_behind_class_character(self):
        model = h.run_parse(
            _entry("\u200eStatus unchanged: Banked\n"),
            "ch54_variant.md")
        self.assertFalse(h.is_failure_result(model))
        self.assertIn("variant phrasing", _kinds(model))


class Ch55StatusLeadingRunTest(unittest.TestCase):
    """CH-55: seat 19 F1 (sixteen entry demotion forms) and
    seat 17 S17-ATK4-17-02 (blank presenting leading forms)."""

    def test_ch55_entry_status_leading_class_characters(self):
        for char in CLASS_RUN_CHARS:
            with self.subTest(char=repr(char)):
                model = h.run_parse(
                    _entry(char + "Status: Banked\n"),
                    "ch55_entry.md")
                self.assertFalse(h.is_failure_result(model))
                self.assertIn(
                    "line start Status line", _kinds(model))
                self.assertIn("Banked", _dispositions(model))

    def test_ch55_entry_status_leading_class_combinations(self):
        for prefix in ("\u200e ", " \u200e", "\u200e\x0b"):
            with self.subTest(prefix=repr(prefix)):
                model = h.run_parse(
                    _entry(prefix + "Status: Banked\n"),
                    "ch55_combo_run.md")
                self.assertFalse(h.is_failure_result(model))
                self.assertIn(
                    "line start Status line", _kinds(model))
                self.assertIn("Banked", _dispositions(model))

    def test_ch55_mark_category_controls_stay_line_start(self):
        # Pins inside the class reading: the mark category limb
        # of the earlier cure holds on its whole class.
        for char in ("\u034f", "\ufe0f"):
            with self.subTest(char=repr(char)):
                model = h.run_parse(
                    _entry(char + "Status: Banked\n"),
                    "ch55_mark_pin.md")
                self.assertFalse(h.is_failure_result(model))
                self.assertIn(
                    "line start Status line", _kinds(model))

    def test_ch55_blank_presenting_leading_takes_signal(self):
        # Seat 17 S17-ATK4-17-02: characters outside the run
        # class that present as blank take the near marker
        # signal instead of a silent demotion to embedded.
        forms = [char + "Status: Banked\n"
                 for char in BLANK_PRESENTING_CHARS[:3]]
        forms += [" \u2800Status: Banked\n",
                  "\u200b\u2800Status: Banked\n"]
        for form in forms:
            with self.subTest(form=repr(form)):
                model, output = h.run_pipeline(
                    _entry(form), "ch55_blank_lead.md")
                self.assertFalse(h.is_failure_result(model))
                self.assertNotIn(
                    "line start Status line", _kinds(model))
                self.assertTrue(h.findings_for(
                    output, rule=2, severity="Warning"))


class Ch55CombinationLimbTest(unittest.TestCase):
    """CH-55, combination limb: the seat 19 forms where an
    outside character defeats the near marker signal on the
    same line, disposed inside CH-55 in this file."""

    def test_ch55_class_character_before_no_space_separator(self):
        model, output = h.run_pipeline(
            _entry("\u200eStatus:Banked\n"), "ch55_nospace.md")
        self.assertFalse(h.is_failure_result(model))
        self.assertNotIn("Banked", _dispositions(model))
        self.assertTrue(h.findings_for(
            output, rule=2, severity="Warning"))

    def test_ch55_class_character_before_empty_value(self):
        model, output = h.run_pipeline(
            _entry("\u200eStatus:\n"), "ch55_empty.md")
        self.assertFalse(h.is_failure_result(model))
        self.assertNotIn("Banked", _dispositions(model))
        self.assertTrue(h.findings_for(
            output, rule=2, severity="Warning"))

    def test_ch55_class_character_before_tab_separator_pin(self):
        # Bounding pin from seat 19: the tab separator form
        # behind an outside character already took the near
        # marker signal through the embedded separator limb,
        # and keeps it.
        model, output = h.run_pipeline(
            _entry("\u200eStatus:\tBanked\n"), "ch55_tab.md")
        self.assertFalse(h.is_failure_result(model))
        self.assertNotIn("Banked", _dispositions(model))
        self.assertTrue(h.findings_for(
            output, rule=2, severity="Warning"))


class Ch55PreambleRunTest(unittest.TestCase):
    """CH-55: seat 19 F2 (six preamble escape forms)."""

    def test_ch55_preamble_leading_class_characters(self):
        for char in ("\u200e", "\u200f", "\u2029", "\u0000",
                     "\u202e"):
            with self.subTest(char=repr(char)):
                _model, output = h.run_pipeline(
                    _preamble_file(char), "ch55_preamble.md")
                self.assertTrue(h.findings_for(
                    output, rule=2, severity="Warning"))

    def test_ch55_preamble_class_character_tab_separator(self):
        _model, output = h.run_pipeline(
            _preamble_file("\u200e", "Status:\tParked"),
            "ch55_preamble_tab.md")
        self.assertTrue(h.findings_for(
            output, rule=2, severity="Warning"))

    def test_ch55_preamble_blank_presenting_takes_finding(self):
        _model, output = h.run_pipeline(
            _preamble_file("\u2800"), "ch55_preamble_blank.md")
        self.assertTrue(h.findings_for(
            output, rule=2, severity="Warning"))


class Ch56SeparatorRunClassTest(unittest.TestCase):
    """CH-56: seat 17 S17-ATK4-17-01, separator characters
    outside the cured run class folded into the Status value."""

    def test_ch56_line_start_separator_blank_presenting_takes_near(self):
        forms = (
            "Status: \u2800Banked\n",
            "Status: \u3164Banked\n",
            "Status:  \u2800Banked\n",
            "Status: \ufffcBanked\n",
            "Status: \u115fBanked\n",
        )
        for form in forms:
            with self.subTest(form=repr(form)):
                model, output = h.run_pipeline(
                    _entry(form), "ch56_sep_blank.md")
                self.assertFalse(h.is_failure_result(model))
                self.assertNotIn("Banked", _dispositions(model))
                self.assertTrue(h.findings_for(
                    output, rule=2, severity="Warning"))

    def test_ch56_line_start_separator_control_behind_space(self):
        # The separator run read by class: a control character
        # (category Cc) behind a leading plain space stands in
        # the run and takes the near marker report, where the
        # earlier run class let it fold into the value.
        model, output = h.run_pipeline(
            _entry("Status: \u0000Banked\n"), "ch56_sep_cc.md")
        self.assertFalse(h.is_failure_result(model))
        self.assertNotIn("Banked", _dispositions(model))
        self.assertTrue(h.findings_for(
            output, rule=2, severity="Warning"))

    def test_ch56_embedded_separator_blank_presenting_takes_near(self):
        forms = (
            "Closing prose stands here. Status: \u2800Banked",
            "Closing prose stands here. Status:\u2800Banked",
            "Closing prose stands here. Status: \u3164Banked",
        )
        for form in forms:
            with self.subTest(form=repr(form)):
                model, output = h.run_pipeline(
                    _entry("", first_paragraph=form),
                    "ch56_embedded.md")
                self.assertFalse(h.is_failure_result(model))
                self.assertNotIn("Banked", _dispositions(model))
                self.assertTrue(h.findings_for(
                    output, rule=2, severity="Warning"))

    def test_ch56_plain_spaces_separator_guard_still_extracts(self):
        # Guard, design question note (f) ground, not charged:
        # a run of plain spaces alone still extracts in
        # silence, as pinned. Passes before and after.
        model, output = h.run_pipeline(
            _entry("Status:  Banked\n"), "ch56_guard.md")
        self.assertIn("line start Status line", _kinds(model))
        self.assertIn("Banked", _dispositions(model))
        self.assertEqual(h.findings_for(output, rule=2), [])

    def test_ch56_embedded_plain_form_still_extracts(self):
        # Guard: the embedded plain form is a designed
        # governing form and extracts with no signal. Passes
        # before and after.
        model, output = h.run_pipeline(
            _entry("", first_paragraph=(
                "Closing prose stands here. Status: Banked")),
            "ch56_embedded_plain.md")
        self.assertIn("tail paragraph element", _kinds(model))
        self.assertIn("Banked", _dispositions(model))
        self.assertEqual(h.findings_for(output, rule=2), [])


class Ch56NearMarkerLabelTest(unittest.TestCase):
    """CH-56: seat 17 S17-ATK4-17-03, an invisible character
    inside the Status label or before its colon."""

    def test_ch56_invisible_inside_label_takes_near(self):
        forms = (
            "Stat\u200bus: Banked\n",
            "Sta\u200btus: Banked\n",
            "Status\u200b: Banked\n",
            "Status\u00a0: Banked\n",
            "Status\u2029: Banked\n",
        )
        for form in forms:
            with self.subTest(form=repr(form)):
                model, output = h.run_pipeline(
                    _entry(form), "ch56_label.md")
                self.assertFalse(h.is_failure_result(model))
                self.assertNotIn(
                    "line start Status line", _kinds(model))
                self.assertNotIn("Banked", _dispositions(model))
                self.assertTrue(h.findings_for(
                    output, rule=2, severity="Warning"))

    def test_ch56_near_marker_pins_hold(self):
        # Pins: the transposition form and the space before
        # the colon form keep their near marker Warning.
        for form in ("Stauts: Banked\n", "Status : Banked\n"):
            with self.subTest(form=repr(form)):
                model, output = h.run_pipeline(
                    _entry(form), "ch56_near_pin.md")
                self.assertFalse(h.is_failure_result(model))
                self.assertNotIn("Banked", _dispositions(model))
                self.assertTrue(h.findings_for(
                    output, rule=2, severity="Warning"))


if __name__ == "__main__":
    unittest.main()
