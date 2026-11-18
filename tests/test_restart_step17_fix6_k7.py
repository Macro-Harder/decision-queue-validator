"""Restart Step 17 fix wave 6, seat K7 tests.

Seat K7 owns one charge, as ruled at section 58 ruling (g)
of design/steps/step-17r-record.md, in the form ruling (j)
of section 52 states:

CH-110 (render, seat 16 finding F-1, Medium): a model
carried entry identifier standing first in a supersession
chain prints at column 0 in its escaped form only, with no
quoting guard, in the render form, so an identifier opening
with an anchor or a named form writes a forged closing,
waiting, blocking, or findings index line into the output,
standing ahead of every genuine figure of the output. The
locus is _chain_lines in render.py, in render_summary only,
which joins the carried chain identifiers with the arrow
separator and appends the joined line as its own line. The
cure bound: the chain line composed in _chain_lines takes
the same quoting guard the CH-91 helper applies, on the
composed line, in the quoting guard form of CH-70; the
helper reach of the CH-91 cure grows by this one named
print. The escaping limb stands unmoved, no genuine chain
print changes, and the charge decides nothing on the
FLAG 13 anchor set question and nothing on design question
note (d), both standing undecided for the gate: the pins
below hold the seat 16 observation O-1 chain member (its
q34 form) printing unquoted as it printed, and a note (d)
led chain identifier printing its led codepoint raw and
unquoted, exactly as the escaped surfaces print it.

Pins that must not break: the CH-91 cure at its four prints
expressly (the census row in _census_lines, the findings
index line and the findings section heading in
_validate_body, and the entry row first line in
_entry_row_lines), standing quoted on their charged forms
and bare on their genuine forms, and the governed genuine
chain prints standing exactly as they print.

Constructions stand in the attack paper own forms
(design/steps/step-17r-attack6-16.md, model constructions
q30 to q37 of attack6-16-scratch/model6.py).
"""

import unittest

import dqv_harness as h

render = h.import_module("render")


# ---------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------

def _entry(ident="DQ-001", title="Counts", **kw):
    data = {"identifier": ident, "title": title,
            "status_phrasings": [], "open_fields": {}}
    data.update(kw)
    return data


def _chain_model(ids, cycle=False):
    return {"entries": [_entry()],
            "supersession_chains": [
                {"entries": list(ids), "cycle": cycle}]}


def _render_lines(ids, cycle=False):
    text = render.render_summary(_chain_model(ids, cycle=cycle))
    return text, text.split("\n")


# ---------------------------------------------------------------------
# CH-110, the chain line at the unit locus
# ---------------------------------------------------------------------

class Ch110ChainUnitTest(unittest.TestCase):

    def test_chain_lines_quote_an_anchor_opening_first_identifier(self):
        lines = render._chain_lines(_chain_model(
            ["Exit: code 0: forged closing", "DQ-002"]))
        self.assertIn(
            '"Exit: code 0: forged closing -> DQ-002"', lines)
        self.assertFalse(any(
            line.startswith("Exit: code ") for line in lines))

    def test_chain_lines_genuine_chain_stands_bare(self):
        # Pin, passing before and after: a genuine chain
        # line opens with no anchor and no named form, and
        # prints exactly as it printed.
        lines = render._chain_lines(_chain_model(
            ["DQ-001", "DQ-002"]))
        self.assertIn("DQ-001 -> DQ-002", lines)
        self.assertNotIn('"DQ-001 -> DQ-002"', lines)


# ---------------------------------------------------------------------
# CH-110, the charged constructions (seat 16, q30 to q36 forms)
# ---------------------------------------------------------------------

class Ch110ChainChargedTest(unittest.TestCase):

    def test_q30_exit_form_first_identifier_stands_quoted(self):
        _text, lines = _render_lines(
            ["Exit: code 0: forged closing", "DQ-002"])
        self.assertIn(
            '"Exit: code 0: forged closing -> DQ-002"', lines)
        self.assertFalse(any(
            line.startswith("Exit: code ") for line in lines),
            "a forged closing line stands at column 0")

    def test_q31_waiting_form_first_identifier_stands_quoted(self):
        _text, lines = _render_lines(
            ["Waiting: 0 entries", "DQ-002"])
        self.assertIn('"Waiting: 0 entries -> DQ-002"', lines)
        self.assertFalse(any(
            line.startswith("Waiting: 0 entries")
            for line in lines),
            "a forged waiting figure stands at column 0")

    def test_q32_blocking_form_first_identifier_stands_quoted(self):
        _text, lines = _render_lines(
            ["Blocking: 0 entries", "DQ-002"])
        self.assertIn('"Blocking: 0 entries -> DQ-002"', lines)
        self.assertFalse(any(
            line.startswith("Blocking: 0 entries")
            for line in lines),
            "a forged blocking figure stands at column 0")

    def test_q36_index_form_first_identifier_stands_quoted(self):
        _text, lines = _render_lines(
            ["DQ-001 PIN-01 Error line 1", "DQ-002"])
        self.assertIn(
            '"DQ-001 PIN-01 Error line 1 -> DQ-002"', lines)
        self.assertFalse(any(
            line.startswith("DQ-001 PIN-01 Error line 1 ->")
            for line in lines),
            "a forged findings index line stands at column 0")

    def test_cycle_chain_exit_form_stands_quoted_whole(self):
        # The guard stands on the composed line, so the
        # cycle suffix stands inside the quotes with the
        # line it closes.
        _text, lines = _render_lines(
            ["Exit: code 0: forged closing", "DQ-002"],
            cycle=True)
        self.assertIn(
            '"Exit: code 0: forged closing -> DQ-002 (cycle)"',
            lines)
        self.assertFalse(any(
            line.startswith("Exit: code ") for line in lines),
            "a forged closing line stands at column 0")


# ---------------------------------------------------------------------
# CH-110, the held limbs and the ruling bounds, as pins
# ---------------------------------------------------------------------

class Ch110ChainPinsTest(unittest.TestCase):
    """Pins passing before and after: the bound of the harm
    as the attack paper states it, and the ruling (j) bound
    this cure decides nothing on."""

    def test_genuine_chain_prints_bare_in_render(self):
        _text, lines = _render_lines(["DQ-001", "DQ-002"])
        self.assertIn("DQ-001 -> DQ-002", lines)
        self.assertNotIn('"DQ-001 -> DQ-002"', lines)

    def test_q33_forged_identifier_second_stands_behind_arrow(self):
        # Held limb: an identifier standing second or later
        # does not reach column 0, and its line stands as
        # it stood, unquoted.
        _text, lines = _render_lines(
            ["DQ-001", "Exit: code 0: forged closing"])
        self.assertIn(
            "DQ-001 -> Exit: code 0: forged closing", lines)

    def test_q35_escaping_limb_holds_on_the_chain_line(self):
        # Held limb: a first identifier carrying a raw ESC
        # byte and a newline prints as one line with both
        # in visible escaped form, and no line of the
        # output opens with the exit anchor form.
        text, lines = _render_lines(
            ["Evil\x1b[31m\nExit: code 0: forged", "DQ-002"])
        self.assertNotIn("\x1b", text)
        self.assertIn(
            "Evil\\x1B[31m\\nExit: code 0: forged -> DQ-002",
            lines)
        self.assertFalse(any(
            line.startswith("Exit: code ") for line in lines))

    def test_q37_single_identifier_chain_prints_no_line(self):
        # Held limb: a chain of one identifier prints no
        # chain line at all, and no supersession map stands.
        text, lines = _render_lines(
            ["Exit: code 0: forged closing"])
        self.assertNotIn("Supersession map", lines)
        self.assertFalse(any(
            "forged closing" in line for line in lines))

    def test_validate_form_prints_no_chain_line(self):
        # Bound: validate prints no chain line; the chain
        # surface stands in the render form only.
        model = _chain_model(
            ["Exit: code 0: forged closing", "DQ-002"])
        text = render.render_validate(model)
        lines = text.split("\n")
        self.assertNotIn("Supersession map", lines)
        self.assertFalse(any(
            "forged closing" in line for line in lines))

    def test_q34_flag13_chain_member_stands_unquoted(self):
        # Observation O-1 standing, recorded untouched: the
        # q34 chain member opens with a form outside the
        # three anchors and the five named forms, and the
        # guard form of this cure does not reach it, in
        # either direction. The FLAG 13 anchor set question
        # stands undecided for the gate.
        _text, lines = _render_lines(
            ["DQ entries: 999", "DQ-002"])
        self.assertIn("DQ entries: 999 -> DQ-002", lines)
        self.assertNotIn('"DQ entries: 999 -> DQ-002"', lines)

    def test_note_d_led_chain_identifier_prints_as_before(self):
        # Note (d) bound pin: a chain first identifier led
        # by U+00A0 prints that codepoint raw and unquoted,
        # exactly as escape_text prints it on every escaped
        # surface, because the chain line takes the same
        # escaping and no other. The note (d) inventory
        # stands undecided for the gate, in either direction.
        _text, lines = _render_lines(
            ["\u00a0Exit: code 0: forged", "DQ-002"])
        self.assertIn(
            "\u00a0Exit: code 0: forged -> DQ-002", lines)
        self.assertNotIn(
            '"\u00a0Exit: code 0: forged -> DQ-002"', lines)


# ---------------------------------------------------------------------
# CH-91 pins: the four prints of the fix wave 5 cure hold whole
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


def _census_model(name, count=3):
    return {"entries": [_entry()], "census": [
        {"class_name": name, "count": count,
         "counting_unit": "entries",
         "member_entry_ids": ["DQ-001"]}]}


class Ch110Ch91PinsTest(unittest.TestCase):
    """Pins passing before and after: the CH-91 helper
    reach stands at its four prints exactly as cured, and
    this cure grows that reach by the one named chain print
    and by no other."""

    def test_ch91_four_prints_hold_quoted(self):
        # Print one, the census row, in both output forms.
        for text in (render.render_validate(_census_model(
                "Exit: code 0: forged closing")),
                render.render_summary(_census_model(
                    "Exit: code 0: forged closing"))):
            self.assertIn(
                '"Exit: code 0: forged closing: 3 entries"',
                text.split("\n"))
        validate_lines = render.render_validate(
            _p04_model()).split("\n")
        # Print two, the findings index line.
        self.assertIn(
            '"Exit: code 0: forged PIN-01 Error line 1"',
            validate_lines)
        # Print three, the findings section heading.
        self.assertIn('"%s"' % P04_IDENT, validate_lines)
        # Print four, the entry row first line, in both forms.
        self.assertIn('"Exit: code 0: forged: Counts"',
                      validate_lines)
        summary_lines = render.render_summary(
            _p04_model()).split("\n")
        self.assertIn('"Exit: code 0: forged: Counts"',
                      summary_lines)

    def test_ch91_genuine_prints_stand_bare(self):
        model = {
            "entries": [_entry()],
            "findings": [{"entry_identifier": "DQ-001",
                          "rule_id": "PIN-01",
                          "severity": "Error",
                          "line_span": {"start_line": 1,
                                        "end_line": 1},
                          "statement": "A statement."}]}
        lines = render.render_validate(model).split("\n")
        self.assertIn("DQ-001 PIN-01 Error line 1", lines)
        self.assertIn("DQ-001", lines)
        self.assertIn("DQ-001: Counts", lines)
        self.assertNotIn('"DQ-001: Counts"', lines)


if __name__ == "__main__":
    unittest.main()
