"""Step 17 fix wave 3, Fix Seat K2 tests, test first.

Charges CH-35, CH-37, and CH-38, as ruled at section 26 of
design/steps/step-17r-record.md, ruling (d) especially, and
prepared at design/steps/step-17r-triage3-prep.md. The leading
run set is stated once at ruling (d): the cured CH-13 set
together with every character the three charges name (a no
break space, a zero width space, a vertical tab, a form feed,
U+200C, U+200D, U+2060, U+00AD, U+180E, U+2028, U+0085, and
combining marks as the seat 19 forms carry them), applied at
all three surfaces. The CH-21 tab forms and the note (f)
guard form stand narrower by governing text and are not
moved: the plain spaces separator guard below passes before
and after the cure, as a guard should.
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


NAMED_RUN_CHARS = (
    "\u00a0", "\u200b", "\x0b", "\x0c", "\u200c", "\u200d",
    "\u2060", "\u00ad", "\u180e", "\u2028", "\u0085", "\u0301",
)

OUTSIDE_STATUS_CHARS = (
    "\x0b", "\x0c", "\u200c", "\u200d", "\u2060", "\u00ad",
    "\u180e", "\u2028", "\u0085", "\u0301",
)


class Ch35HeadingPrefixRunTest(unittest.TestCase):
    """CH-35, A3-3-F1: heading recognition reads the heading
    after a leading run of the ruling (d) set."""

    def test_ch35_heading_prefix_named_characters(self):
        for char in NAMED_RUN_CHARS:
            with self.subTest(char=repr(char)):
                model = h.run_parse(
                    _two_entry_file(char), "ch35_heading.md")
                self.assertFalse(h.is_failure_result(model))
                self.assertIsNotNone(
                    h.entry_by_id(model, "DQ-002"))
                self.assertEqual(len(h.entries_of(model)), 2)

    def test_ch35_heading_prefix_mixed_runs(self):
        for prefix in (" \x0b", "\x0b ", "\u00a0\u200c",
                       "\u0301\u200d", "\x0c\u2060"):
            with self.subTest(prefix=repr(prefix)):
                model = h.run_parse(
                    _two_entry_file(prefix), "ch35_mixed.md")
                self.assertFalse(h.is_failure_result(model))
                self.assertIsNotNone(
                    h.entry_by_id(model, "DQ-002"))
                self.assertEqual(len(h.entries_of(model)), 2)

    def test_ch35_unrecognised_prefixed_heading_takes_file_level_warning(self):
        body = h._header_block()
        body += "### DQ-001: A sample open question\n\n"
        body += "Status: Banked\n\n"
        body += "Question: Which option should we take?\n\n"
        body += "Options: Option A, Option B\n\n"
        body += "Cost of deciding late: Work stays blocked.\n\n"
        body += "Blocks: DQ-002\n\n"
        body += "\x0b##### An unmatched generated heading\n\n"
        body += "Prose standing under the unmatched heading.\n"
        model, output = h.run_pipeline(
            body.encode("utf-8"), "ch35_unmatched.md")
        self.assertFalse(h.is_failure_result(model))
        # Corrected by the recovery holder: the first holder
        # pinned rule 5 and the FILE identifier, a form the
        # product does not produce for this finding. The
        # governed form is the PIN-06 unmatched heading
        # Warning, keyed to the file level unit that carries
        # the segment, not to the entry. The pin below asserts
        # that form.
        warnings = [finding for finding in h.findings_of(output)
                    if h.finding_severity(finding) == "Warning"
                    and "matches no recognised heading form" in
                    (h.finding_statement(finding) or "")]
        self.assertTrue(warnings)
        self.assertNotEqual(
            h.finding_entry_id(warnings[0]), "DQ-001")

    def test_ch35_cr_tail_behind_one_space_is_counted(self):
        model = h.run_parse(
            _cr_tail_file([" Status: Banked"]),
            "ch35_cr_space_tail.md")
        self.assertFalse(h.is_failure_result(model))
        self.assertIn("Banked", _dispositions(model))
        self.assertIn("line start Status line", _kinds(model))

    def test_ch35_cr_tail_behind_run_characters_is_counted(self):
        for prefix in ("\u200c", "\x0b", "\u2060"):
            with self.subTest(prefix=repr(prefix)):
                model = h.run_parse(
                    _cr_tail_file([prefix + "Status: Banked"]),
                    "ch35_cr_run_tail.md")
                self.assertFalse(h.is_failure_result(model))
                self.assertIn("Banked", _dispositions(model))
                self.assertIn(
                    "line start Status line", _kinds(model))


class Ch37StatusLeadingRunTest(unittest.TestCase):
    """CH-37, A3-3-F3 with seat 19 F1 and F2: the Status
    marker leading run set, entry and preamble limbs."""

    def test_ch37_entry_status_leading_named_characters(self):
        for char in OUTSIDE_STATUS_CHARS:
            with self.subTest(char=repr(char)):
                model = h.run_parse(
                    _entry(char + "Status: Banked\n"),
                    "ch37_entry.md")
                self.assertFalse(h.is_failure_result(model))
                self.assertIn(
                    "line start Status line", _kinds(model))
                self.assertIn("Banked", _dispositions(model))

    def test_ch37_entry_status_leading_mixed_runs(self):
        for prefix in (" \x0b", "\x0b ", "\x0b\x0b",
                       "\u00a0\x0b", "\u200b\u200c"):
            with self.subTest(prefix=repr(prefix)):
                model = h.run_parse(
                    _entry(prefix + "Status: Banked\n"),
                    "ch37_mixed.md")
                self.assertFalse(h.is_failure_result(model))
                self.assertIn(
                    "line start Status line", _kinds(model))
                self.assertIn("Banked", _dispositions(model))

    def test_ch37_variant_marker_behind_vertical_tab_stays_variant(self):
        model = h.run_parse(
            _entry("\x0bStatus unchanged: Banked\n"),
            "ch37_variant.md")
        self.assertFalse(h.is_failure_result(model))
        self.assertIn("variant phrasing", _kinds(model))

    def test_ch37_vertical_tab_before_tab_separator_takes_near_signal(self):
        model, output = h.run_pipeline(
            _entry("\x0bStatus:\tBanked\n"), "ch37_combo.md")
        self.assertFalse(h.is_failure_result(model))
        self.assertNotIn("Banked", _dispositions(model))
        self.assertTrue(h.findings_for(output, rule=2,
                                       severity="Warning"))

    def test_ch37_preamble_leading_named_characters_take_finding(self):
        for char in ("\x0b", "\x0c", "\u200c", "\u2060",
                     " \x0b"):
            with self.subTest(char=repr(char)):
                _model, output = h.run_pipeline(
                    _preamble_file(char), "ch37_preamble.md")
                self.assertTrue(h.findings_for(
                    output, rule=2, severity="Warning"))

    def test_ch37_preamble_vertical_tab_tab_separator_takes_finding(self):
        _model, output = h.run_pipeline(
            _preamble_file("\x0b", "Status:\tParked"),
            "ch37_preamble_combo.md")
        self.assertTrue(h.findings_for(output, rule=2,
                                       severity="Warning"))


class Ch38SeparatorRunTest(unittest.TestCase):
    """CH-38, S17-ATK3-17-01, S17-ATK3-17-02, and the alias
    limb S17-ATK3-17-03: the Status separator run and the
    embedded separator test."""

    def test_ch38_line_start_separator_beyond_plain_spaces_takes_near(self):
        forms = (
            "Status: \u00a0Banked\n",
            "Status: \x0bBanked\n",
            "Status: \u200bBanked\n",
            "Status: \ufeffBanked\n",
            "Status:  \u00a0Banked\n",
            "Status: \x0cBanked\n",
            "Status: \u200cBanked\n",
            "Status: \u0301Banked\n",
        )
        for form in forms:
            with self.subTest(form=repr(form)):
                model, output = h.run_pipeline(
                    _entry(form), "ch38_sep.md")
                self.assertFalse(h.is_failure_result(model))
                self.assertNotIn("Banked", _dispositions(model))
                self.assertTrue(h.findings_for(
                    output, rule=2, severity="Warning"))

    def test_ch38_plain_spaces_separator_guard_still_extracts(self):
        # Guard, design question note (f) ground, not charged:
        # a run of plain spaces alone still extracts in
        # silence, as pinned. Passes before and after.
        model, output = h.run_pipeline(
            _entry("Status:  Banked\n"), "ch38_guard.md")
        self.assertIn("line start Status line", _kinds(model))
        self.assertIn("Banked", _dispositions(model))
        self.assertEqual(h.findings_for(output, rule=2), [])

    def test_ch38_embedded_separator_forms_take_near(self):
        forms = (
            "Closing prose stands here. Status: \tBanked",
            "Closing prose stands here. Status:\tBanked",
            "Closing prose stands here. Status:\u00a0Banked",
            "Closing prose stands here. Status: \u00a0Banked",
        )
        for form in forms:
            with self.subTest(form=repr(form)):
                model, output = h.run_pipeline(
                    _entry("", first_paragraph=form),
                    "ch38_embedded.md")
                self.assertFalse(h.is_failure_result(model))
                self.assertNotIn("Banked", _dispositions(model))
                self.assertTrue(h.findings_for(
                    output, rule=2, severity="Warning"))

    def test_ch38_embedded_plain_form_still_extracts(self):
        # Guard: the embedded plain form is a designed
        # governing form and extracts with no signal. Passes
        # before and after.
        model, output = h.run_pipeline(
            _entry("", first_paragraph=(
                "Closing prose stands here. Status: Banked")),
            "ch38_embedded_plain.md")
        self.assertIn("tail paragraph element", _kinds(model))
        self.assertIn("Banked", _dispositions(model))
        self.assertEqual(h.findings_for(output, rule=2), [])

    def _alias_alone_file(self, alias_line):
        body = h._header_block()
        body += "### DQ-001: A sample open question\n\n"
        body += "Status: Banked\n\n"
        body += "This question is waiting for a decision.\n\n"
        body += alias_line + "\n\n- Option A\n- Option B\n\n"
        body += "Question: Which option should we take?\n\n"
        body += "Cost of deciding late: Work stays blocked.\n\n"
        body += "Blocks: DQ-002\n"
        return body.encode("utf-8")

    def _missing_options(self, output):
        found = h.findings_for(output, entry_id="DQ-001")
        return [item for item in found
                if "options" in
                (h.finding_statement(item) or "").lower()]

    def test_ch38_options_alias_are_alone_collects_dash_lines(self):
        _model, output = h.run_pipeline(
            self._alias_alone_file("The options are:"),
            "ch38_alias_are.md")
        self.assertEqual(self._missing_options(output), [])

    def test_ch38_options_alias_plain_alone_collects_dash_lines(self):
        _model, output = h.run_pipeline(
            self._alias_alone_file("The options:"),
            "ch38_alias_plain.md")
        self.assertEqual(self._missing_options(output), [])


if __name__ == "__main__":
    unittest.main()
