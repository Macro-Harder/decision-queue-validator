"""Step 17 fix wave 7, Fix Seat K13 tests, test first.

Charge CH-153, as ruled at section 66 of
design/steps/step-17r-record.md, with the bound of ruling
(h) of that section, and prepared at
design/steps/step-17r-triage7-prep.md.

CH-153 (render, the findings detail line): seat 16 finding
F-1 (Medium) at design/steps/step-17r-attack7-16.md. A
model carried finding rule identifier standing first on
the findings detail line in _validate_body prints at
column 0 in its escaped form only, with no quoting guard,
in the validate form, so a rule identifier opening with
an anchor or a named form writes a forged closing,
waiting, figure, or findings index line into the output,
ahead of every genuine figure. The neighbouring prints of
the same value stand guarded or prefixed: the findings
index line takes the CH-91 guard, and the rule list
fallback line stands behind its check prefix. The cure
bound, as the earlier quoting charges bound it: the
detail line composed in _validate_body takes the quoting
guard in the form the CH-70 group title cure takes it and
the CH-110 chain cure takes it, the shared
_opens_with_anchor predicate on the composed line, the
whole line standing in double quotes where it opens with
an anchor or a named form, in the validate form only.

Ruling (h) bounds this charge expressly. The FLAG 13
anchor set question (seat 16 observation O-1, including
its r07 member on this very print) stands undecided for
the gate and is NOT inside CH-153: the r07 form stands
inside that question only and is pinned below printing
unquoted as it printed, cured nowhere. Design question
note (d) (seat 16 observations O-4 and O-9) likewise
stands undecided: the note (d) led rule identifier of
r10 is pinned below printing its led codepoint raw and
unquoted. Seat 16 observation O-5, the rule list label
print, likewise stands undecided and cured nowhere: its
t11 form is pinned below printing as it printed.

Pins that must not break: the CH-91 cure at its four
prints expressly (the census row, the findings index
line, the findings section heading, and the entry row
first line), the CH-110 chain line cure, the escaping
limb on this very surface (the r05 and r06 held forms),
the held severity limb (r15, a carried severity cannot
lead the line), and every genuine print of the current
vocabulary standing bare and exact (r08).

Constructions stand in the attack paper own forms
(design/steps/step-17r-attack7-16.md, model constructions
r01 to r15 and t11 of attack7-16-scratch/model7.py).

Copyright: J.P. Picard aka Macro-Harder
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


def _detail_model(rule, severity="Error"):
    return {
        "entries": [_entry()],
        "findings": [{"entry_identifier": "DQ-001",
                      "rule_id": rule, "severity": severity,
                      "line_span": {"start_line": 1,
                                    "end_line": 1},
                      "statement": "A statement."}]}


def _detail_lines(rule, severity="Error"):
    text = render.render_validate(_detail_model(rule, severity))
    return text, text.split("\n")


# ---------------------------------------------------------------------
# CH-153, the charged constructions (seat 16, r01 to r04
# and r11 to r14 forms): the detail line stands quoted
# ---------------------------------------------------------------------

class Ch153DetailChargedTest(unittest.TestCase):

    def test_validate_body_unit_quotes_the_exit_form(self):
        lines = render._validate_body(
            _detail_model("Exit: code 0: forged closing"))
        self.assertIn(
            '"Exit: code 0: forged closing Error line 1"', lines)
        self.assertNotIn(
            "Exit: code 0: forged closing Error line 1", lines)

    def test_r01_exit_form_rule_stands_quoted(self):
        _text, lines = _detail_lines("Exit: code 0: forged closing")
        self.assertIn(
            '"Exit: code 0: forged closing Error line 1"', lines)
        self.assertNotIn(
            "Exit: code 0: forged closing Error line 1", lines)
        self.assertFalse(any(
            line.startswith("Exit: code ") for line in lines),
            "a forged closing line stands at column 0")

    def test_r02_waiting_form_rule_stands_quoted(self):
        _text, lines = _detail_lines("Waiting: 0 entries")
        self.assertIn('"Waiting: 0 entries Error line 1"', lines)
        self.assertNotIn("Waiting: 0 entries Error line 1", lines)

    def test_r03_blocking_form_rule_stands_quoted(self):
        _text, lines = _detail_lines("Blocking: 0 entries")
        self.assertIn('"Blocking: 0 entries Error line 1"', lines)
        self.assertNotIn("Blocking: 0 entries Error line 1", lines)

    def test_r04_index_form_rule_stands_quoted(self):
        _text, lines = _detail_lines("DQ-999 PIN-99")
        self.assertIn('"DQ-999 PIN-99 Error line 1"', lines)
        self.assertNotIn("DQ-999 PIN-99 Error line 1", lines)

    def test_r11_companion_form_rule_stands_quoted(self):
        _text, lines = _detail_lines("Companion count: 0 entries")
        self.assertIn(
            '"Companion count: 0 entries Error line 1"', lines)
        self.assertNotIn(
            "Companion count: 0 entries Error line 1", lines)

    def test_r12_limbo_form_rule_stands_quoted(self):
        _text, lines = _detail_lines(
            "Limbo: 9 Conditional entries stand outside")
        self.assertIn(
            '"Limbo: 9 Conditional entries stand outside '
            'Error line 1"', lines)
        self.assertNotIn(
            "Limbo: 9 Conditional entries stand outside "
            "Error line 1", lines)

    def test_r13_headed_form_rule_stands_quoted(self):
        _text, lines = _detail_lines("Headed entries: 0")
        self.assertIn('"Headed entries: 0 Error line 1"', lines)
        self.assertNotIn("Headed entries: 0 Error line 1", lines)

    def test_r14_self_check_form_rule_stands_quoted(self):
        _text, lines = _detail_lines("Self check: sums agree")
        self.assertIn(
            '"Self check: sums agree Error line 1"', lines)
        self.assertNotIn("Self check: sums agree Error line 1",
                         lines)


# ---------------------------------------------------------------------
# CH-153, the held limbs and the genuine print, as pins
# ---------------------------------------------------------------------

class Ch153DetailPinsTest(unittest.TestCase):
    """Pins passing before and after: the bound of the harm
    as the attack paper states it."""

    def test_r08_genuine_rule_prints_bare_and_exact(self):
        _text, lines = _detail_lines("PIN-01")
        self.assertIn("PIN-01 Error line 1", lines)
        self.assertNotIn('"PIN-01 Error line 1"', lines)

    def test_r05_escaping_limb_holds_on_the_detail_line(self):
        # Held limb: a rule identifier carrying a raw ESC
        # byte and a newline prints as one line with both
        # in visible escaped form, the forged text standing
        # mid line behind the escaped forms.
        text, lines = _detail_lines(
            "Evil\x1b[31m\nExit: code 0: forged")
        self.assertNotIn("\x1b", text)
        self.assertIn(
            "Evil\\x1B[31m\\nExit: code 0: forged Error line 1",
            lines)
        self.assertFalse(any(
            line.startswith("Exit: code ") for line in lines))

    def test_r06_variation_selector_led_rule_escapes(self):
        # Held limb: a rule identifier led by U+FE00 prints
        # that selector in escaped form at the head of the
        # line, so no copy stands at column 0 in anchor form.
        _text, lines = _detail_lines("\ufe00Exit: code 0: forged")
        self.assertIn(
            "\\uFE00Exit: code 0: forged Error line 1", lines)
        self.assertFalse(any(
            line.startswith("Exit: code ") for line in lines))

    def test_r15_carried_severity_cannot_lead_the_line(self):
        # Held limb: a hostile severity stands behind a
        # genuine rule, mid line, never at column 0, and
        # its line stands as it stood, unquoted.
        _text, lines = _detail_lines(
            "PIN-01", severity="Exit: code 0: forged")
        self.assertIn("PIN-01 Exit: code 0: forged line 1", lines)
        self.assertNotIn(
            '"PIN-01 Exit: code 0: forged line 1"', lines)
        self.assertFalse(any(
            line.startswith("Exit: code ") for line in lines))

    def test_render_form_prints_no_detail_line(self):
        # Bound: render prints no findings body; the detail
        # surface stands in the validate form only.
        text = render.render_summary(
            _detail_model("Exit: code 0: forged closing"))
        lines = text.split("\n")
        self.assertNotIn(
            "Exit: code 0: forged closing Error line 1", lines)
        self.assertFalse(any(
            "forged closing" in line for line in lines))


# ---------------------------------------------------------------------
# The ruling (h) bounds, as pins: cured nowhere
# ---------------------------------------------------------------------

class Ch153RulingHBoundPinsTest(unittest.TestCase):
    """Pins passing before and after: the governed ground
    contacts of ruling (h) of section 66 stand undecided
    for the gate and no part of this cure reaches them."""

    def test_r07_flag13_member_stands_unquoted(self):
        # Observation O-1 standing, inside the FLAG 13
        # anchor set question only and not inside CH-153:
        # the r07 rule identifier opens with a form outside
        # the three anchors and the five named forms, and
        # the guard form of this cure does not reach it, in
        # either direction.
        _text, lines = _detail_lines("DQ entries: 999")
        self.assertIn("DQ entries: 999 Error line 1", lines)
        self.assertNotIn('"DQ entries: 999 Error line 1"', lines)

    def test_r10_note_d_led_rule_prints_as_before(self):
        # Note (d) bound pin: a rule identifier led by
        # U+00A0 prints that codepoint raw and unquoted,
        # exactly as escape_text prints it on every escaped
        # surface, because the detail line takes the same
        # escaping and no other. The note (d) inventory
        # stands undecided for the gate, in either direction.
        _text, lines = _detail_lines("\u00a0Exit: code 0: forged")
        self.assertIn(
            "\u00a0Exit: code 0: forged Error line 1", lines)
        self.assertNotIn(
            '"\u00a0Exit: code 0: forged Error line 1"', lines)

    def test_o5_rule_list_label_print_stands_as_before(self):
        # Seat 16 observation O-5 standing, cured nowhere:
        # a rule list label carried as a clearing form key
        # prints at column 0 in its escaped form only, on a
        # different line from the detail line this charge
        # names, and this cure does not reach that print.
        model = _detail_model("PIN-01")
        model["per_rule_clearing_forms"] = {
            "Waiting: 0 entries": "a recorded form"}
        lines = render.render_validate(model).split("\n")
        self.assertIn("Waiting: 0 entries: a recorded form",
                      lines)
        self.assertNotIn('"Waiting: 0 entries: a recorded form"',
                         lines)


# ---------------------------------------------------------------------
# The earlier quoting cures hold whole at their prints
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


class Ch153EarlierQuotingPinsTest(unittest.TestCase):
    """Pins passing before and after: the CH-91 helper reach
    stands at its four prints exactly as cured, the CH-110
    chain line stands as cured, and the genuine prints of
    those surfaces stand bare and exact."""

    def test_ch91_four_prints_hold_quoted(self):
        for text in (render.render_validate(_census_model(
                "Exit: code 0: forged closing")),
                render.render_summary(_census_model(
                    "Exit: code 0: forged closing"))):
            self.assertIn(
                '"Exit: code 0: forged closing: 3 entries"',
                text.split("\n"))
        validate_lines = render.render_validate(
            _p04_model()).split("\n")
        self.assertIn(
            '"Exit: code 0: forged PIN-01 Error line 1"',
            validate_lines)
        self.assertIn('"%s"' % P04_IDENT, validate_lines)
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

    def test_ch110_chain_line_holds(self):
        model = {"entries": [_entry()],
                 "supersession_chains": [
                     {"entries": ["Exit: code 0: forged closing",
                                  "DQ-002"]}]}
        lines = render.render_summary(model).split("\n")
        self.assertIn(
            '"Exit: code 0: forged closing -> DQ-002"', lines)
        genuine = {"entries": [_entry()],
                   "supersession_chains": [
                       {"entries": ["DQ-001", "DQ-002"]}]}
        genuine_lines = render.render_summary(
            genuine).split("\n")
        self.assertIn("DQ-001 -> DQ-002", genuine_lines)
        self.assertNotIn('"DQ-001 -> DQ-002"', genuine_lines)


if __name__ == "__main__":
    unittest.main()
