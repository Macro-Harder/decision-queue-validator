"""Restart Step 17 fix wave 2, seat K3 tests.

Seat K3 owns two charges, both in parse.py:

CH-13 (A2-3-F5 merged with seat 19 F1 and F2): the M8 cure
reads a Status marker after exactly one leading character.
Neighbouring leading forms (two byte order marks, a mark and
a space, a space and a mark, a mark and a tab, two and three
spaces, one tab, a no break space, a zero width space) demote
the line silently to kind embedded, and two leading spaces
before a preamble Status line escape the rule 2 preamble
finding. The marker is to be read after a leading run of
space, tab, and invisible space or format characters.

CH-21 (S17-ATK2-17-01 and S17-ATK2-17-02): a mixed space and
tab separator after the Status colon extracts silently, and
neighbouring damaged Status forms (an empty value with
spaces or a tab, the plain empty form on a second entry, a
tab before the colon, a two edit typo in the label) reach
Ambiguous at exit 4 with no finding at all. Each is to take
the near marker signal. The design question note (f) forms
are not charged: two plain spaces after the colon stand as
they stood, extracting with no signal, pinned by a guard
test below that passes before and after the cure.
"""

import unittest

import dqv_harness as h


def _entry(status_line, extra_body=""):
    body = h._header_block()
    body += "### DQ-001: A sample open question\n\n"
    body += status_line
    body += "\nThis question is waiting for a decision.\n\n"
    body += "Question: Which option should we take?\n\n"
    body += "Options: Option A, Option B\n\n"
    body += "Cost of deciding late: Work stays blocked.\n\n"
    body += "Blocks: DQ-002\n"
    body += extra_body
    return body.encode("utf-8")


def _two_entry(second_status_line):
    body = h._header_block()
    body += "### DQ-001: A sample open question\n\n"
    body += "Status: Banked\n\n"
    body += "This question is waiting for a decision.\n\n"
    body += "Question: Which option should we take?\n\n"
    body += "Options: Option A, Option B\n\n"
    body += "Cost of deciding late: Work stays blocked.\n\n"
    body += "Blocks: DQ-002\n\n"
    body += "### DQ-002: A second open question\n\n"
    body += second_status_line
    body += "\nThis question is waiting for a decision.\n\n"
    body += "Question: Which option should we take?\n\n"
    body += "Options: Option A, Option B\n\n"
    body += "Cost of deciding late: Work stays blocked.\n\n"
    body += "Blocks: DQ-001\n"
    return body.encode("utf-8")


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


class Ch13LeadingRunTest(unittest.TestCase):
    """CH-13: a leading run before the Status marker does not
    reclassify the occurrence."""

    PREFIXES = (
        "\ufeff\ufeff",
        "\ufeff ",
        " \ufeff",
        "\ufeff\t",
        "  ",
        "   ",
        "\t",
        "\u00a0",
        "\u200b",
    )

    def test_leading_run_before_status_stays_line_start(self):
        for prefix in self.PREFIXES:
            with self.subTest(prefix=repr(prefix)):
                model = h.run_parse(
                    _entry(prefix + "Status: Banked\n"),
                    "leading_run.md")
                self.assertFalse(h.is_failure_result(model))
                self.assertIn("line start Status line", _kinds(model))
                self.assertIn("Banked", _dispositions(model))

    def test_leading_run_before_variant_stays_variant(self):
        model = h.run_parse(
            _entry("\ufeff\ufeffStatus unchanged: Banked\n"),
            "leading_run_variant.md")
        self.assertFalse(h.is_failure_result(model))
        self.assertIn("variant phrasing", _kinds(model))

    def test_two_leading_spaces_before_preamble_status_take_a_finding(self):
        body = "# Decision queue\n\n  Status: Parked\n\n"
        body += "Generated queue shaped input.\n\n"
        body += "### DQ-001: A sample open question\n\n"
        body += "This question is waiting for a decision.\n\n"
        body += "Question: Which option should we take?\n\n"
        body += "Options: Option A, Option B\n\n"
        body += "Cost of deciding late: Work stays blocked.\n\n"
        body += "Blocks: DQ-002\n"
        _model, output = h.run_pipeline(body.encode("utf-8"),
                                        "preamble_two_spaces.md")
        self.assertTrue(h.findings_for(output, rule=2,
                                       severity="Warning"))


class Ch21SeparatorTest(unittest.TestCase):
    """CH-21, S17-ATK2-17-01: a separator run carrying a tab
    after the Status colon takes the near marker signal and
    extracts no element."""

    def test_space_then_tab_separator_takes_a_signal(self):
        _model, output = h.run_pipeline(
            _entry("Status: \tBanked\n"), "space_tab_sep.md")
        self.assertTrue(h.findings_for(output, rule=2,
                                       severity="Warning"))

    def test_spaces_then_tab_separator_takes_a_signal(self):
        _model, output = h.run_pipeline(
            _entry("Status:  \tBanked\n"), "spaces_tab_sep.md")
        self.assertTrue(h.findings_for(output, rule=2,
                                       severity="Warning"))

    def test_two_plain_spaces_separator_still_extracts_in_silence(self):
        # Guard, design question note (f) ground, not charged:
        # two plain spaces after the colon stand as they stood.
        model, output = h.run_pipeline(
            _entry("Status:  Banked\n"), "two_spaces_sep.md")
        self.assertIn("line start Status line", _kinds(model))
        self.assertEqual(h.findings_for(output, rule=2), [])


class Ch21NearMarkerSilenceTest(unittest.TestCase):
    """CH-21, S17-ATK2-17-02: neighbouring damaged Status
    forms take a finding instead of a silent Ambiguous."""

    def test_empty_value_with_spaces_takes_a_finding(self):
        _model, output = h.run_pipeline(
            _entry("Status:    \n"), "empty_spaces.md")
        self.assertTrue(h.findings_for(output, rule=2,
                                       severity="Warning"))

    def test_empty_value_with_a_tab_takes_a_finding(self):
        _model, output = h.run_pipeline(
            _entry("Status: \t\n"), "empty_tab.md")
        self.assertTrue(h.findings_for(output, rule=2,
                                       severity="Warning"))

    def test_plain_empty_value_on_second_entry_takes_a_finding(self):
        _model, output = h.run_pipeline(
            _two_entry("Status:\n"), "empty_second.md")
        self.assertTrue(h.findings_for(output, rule=2,
                                       severity="Warning"))

    def test_tab_before_the_colon_takes_a_finding(self):
        _model, output = h.run_pipeline(
            _entry("Status\t: Banked\n"), "tab_before_colon.md")
        self.assertTrue(h.findings_for(output, rule=2,
                                       severity="Warning"))

    def test_two_edit_typo_in_the_label_takes_a_finding(self):
        _model, output = h.run_pipeline(
            _entry("Statzz: Banked\n"), "two_edit_typo.md")
        self.assertTrue(h.findings_for(output, rule=2,
                                       severity="Warning"))


if __name__ == "__main__":
    unittest.main()
