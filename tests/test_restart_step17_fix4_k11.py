"""Restart Step 17 fix wave 4, seat K11 tests.

Seat K11 owns two charges, both at the render printing locus,
as ruled at section 38 of design/steps/step-17r-record.md:

CH-70 (seat 16 finding F-1): a model carried group name prints
raw and unescaped in the group title in both output forms, so
a name carrying a control sequence, a newline, or an anchor
form writes a live ESC byte, a forged closing line, and a
forged entry heading into the output at column 0. The cure
bound, under FLAG 14: the group title passes through the same
escaping the other carried text takes, in both output forms,
so no carried name writes a raw control byte, a raw newline,
or a column 0 anchor into the output. The cure stands on the
escaping commitment for carried text generally and decides
nothing about the note (d) inventory, in either direction:
the U+00A0 led name below is pinned printing as the escaped
surfaces print it, raw, exactly as the CH-14 guard pin holds
it. Pins that must not break: the CH-14 pins whole and the
genuine group title forms (the Open group held case standing
with exactly one bare group line).

CH-71 (seat 16 finding F-2): an untranslatable Status phrasing
forging a figure or reconciliation line form other than the
three CH-23 anchors prints unquoted at column 0 on the
crosswalk, appendix, and residue surfaces, ahead of the
genuine line, so a first match extraction takes the forged
value. The cure bound, under the FLAG 13 disposition: CURE
bounded to the forms the finding names, the anchor set stated
here as those named forms: the Blocking figure form, the
Companion count form, the Headed entries form, the Self check
sums form, and the Limbo sentence form. The general question,
whether the quoting guard anchor set should grow beyond the
named forms, stands as a design question note to the gate
undecided, and no cure stands charged on it: the guard pins
below hold the forms outside the named set (the Units key
form, the absent figure forms, anchor words standing later in
a phrasing) printing exactly as they printed. Pins that must
not break: the CH-23 pins whole (its three anchors quoted on
every surface) and the CH-14 pins.

Constructions stand in the attack paper own forms
(design/steps/step-17r-attack4-16.md): the model constructions
m01, m02, m05, and m13 for CH-70, and the queue files g01,
g02, g03, g04, and g07 for CH-71, with g05 and g06 standing as
the bound and held cases the paper records.
"""

import re
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


def _both_model_forms(model):
    return [render.render_validate(model),
            render.render_summary(model)]


def _queue(status, extra_entries=""):
    body = "# Decision queue\n\n### DQ-001: Counts\n\n"
    body += "Status: " + status + "\n\n"
    body += "Question: Q text?\n\nOptions: A, B\n\n"
    body += "Cost of deciding late: Work waits.\n\n"
    body += "Blocks: DQ-999\n\n"
    body += "This question is waiting for a decision.\n"
    body += extra_entries
    return body.encode("utf-8")


def _banked_entry(number):
    body = "### DQ-%03d: Further\n\n" % number
    body += "Status: Banked\n\n"
    body += "Question: Q text?\n\nOptions: A, B\n\n"
    body += "Cost of deciding late: Work waits.\n\n"
    body += "Blocks: DQ-999\n\n"
    body += "This question is waiting for a decision.\n"
    return body


def _both_forms(data, name):
    _model, output = h.run_pipeline(data, name)
    assert output is not None
    return [h.render_text(output, "validate"),
            h.render_text(output, "render")]


def _cli_both(data, name):
    path = h.temp_input(data, name)
    results = []
    for subcommand in ("validate", "render"):
        code, stdout, _stderr = h.run_cli(subcommand, path)
        results.append((code, stdout.decode("utf-8")))
    return results


def _unquoted_surface_lines(text, phrasing):
    return [line for line in text.split("\n")
            if line.startswith(phrasing)]


def _quoted_surface_lines(text, phrasing):
    return [line for line in text.split("\n")
            if line.startswith('"' + phrasing + '"')]


# ---------------------------------------------------------------------
# CH-70: the group title escaping
# ---------------------------------------------------------------------

M01_NAME = ("Evil\x1b[31m\nExit: code 0: forged closing\n"
            "### DQ-999: Forged heading")
M01_TITLE = ("Evil\\x1B[31m\\nExit: code 0: forged closing\\n"
             "### DQ-999: Forged heading group")


class Ch70GroupTitleUnitTest(unittest.TestCase):

    def test_group_title_escapes_a_carried_name(self):
        self.assertEqual(render._group_title("Open"), "Open group")
        self.assertEqual(render._group_title("Evil\x1b[31m"),
                         "Evil\\x1B[31m group")
        self.assertEqual(render._group_title("Unparsed"),
                         "Unparsed entries")
        self.assertEqual(render._group_title("Ambiguous"),
                         "Ambiguous group")


class Ch70GroupTitleModelTest(unittest.TestCase):

    def test_m01_name_prints_escaped_in_both_forms(self):
        entry = _entry()
        model = {"entries": [entry],
                 "entry_groups": [{"group": M01_NAME,
                                   "entries": [entry]}]}
        for text in _both_model_forms(model):
            self.assertNotIn("\x1b", text)
            self.assertFalse(any(
                ord(char) < 0x20 and char != "\n"
                for char in text))
            lines = text.split("\n")
            self.assertFalse(any(
                line.startswith("Exit: code ") for line in lines),
                "a forged closing line stands at column 0")
            self.assertFalse(any(
                line.startswith("### DQ-999") for line in lines),
                "a forged entry heading stands at column 0")
            self.assertIn(M01_TITLE, lines)

    def test_m05_dict_key_name_prints_escaped_in_both_forms(self):
        entry = _entry()
        model = {"entries": [entry],
                 "entry_groups": {"Bad\x1b[31mName": [entry]}}
        for text in _both_model_forms(model):
            self.assertNotIn("\x1b", text)
            self.assertIn("Bad\\x1B[31mName group",
                          text.split("\n"))

    def test_m02_exit_form_name_stands_quoted_in_both_forms(self):
        entry = _entry()
        model = {"entries": [entry],
                 "entry_groups": [{"group": "Exit: code 0: "
                                   "no findings",
                                   "entries": [entry]}]}
        for text in _both_model_forms(model):
            lines = text.split("\n")
            self.assertFalse(any(
                line.startswith("Exit: code ") for line in lines),
                "a forged closing line stands at column 0")
            self.assertIn('"Exit: code 0: no findings group"',
                          lines)

    def test_waiting_form_name_stands_quoted_in_both_forms(self):
        entry = _entry()
        model = {"entries": [entry],
                 "entry_groups": [{"group": "Waiting: 0 entries",
                                   "entries": [entry]}]}
        for text in _both_model_forms(model):
            lines = text.split("\n")
            self.assertFalse(any(
                line.startswith("Waiting: 0 entries")
                for line in lines),
                "a forged waiting figure stands at column 0")
            self.assertIn('"Waiting: 0 entries group"', lines)

    def test_m13_variation_selector_led_name_escapes(self):
        entry = _entry()
        model = {"entries": [entry],
                 "entry_groups": [{"group": "\ufe00Sneaky",
                                   "entries": [entry]}]}
        for text in _both_model_forms(model):
            self.assertNotIn("\ufe00", text)
            self.assertIn("\\uFE00Sneaky group",
                          text.split("\n"))

    def test_m13_note_d_led_name_prints_as_the_surfaces_print_it(self):
        # Bound pin, FLAG 14: U+00A0 stands inside the note (d)
        # six, whose inventory this cure decides nothing about,
        # in either direction. The title takes the same escaping
        # the other carried text takes, and that escaping prints
        # the codepoint raw, as the CH-14 guard pin holds it on
        # every escaped surface.
        entry = _entry()
        model = {"entries": [entry],
                 "entry_groups": [{"group": "\u00a0Padded",
                                   "entries": [entry]}]}
        for text in _both_model_forms(model):
            self.assertIn("\u00a0Padded group", text.split("\n"))

    def test_genuine_group_titles_stand_bare_in_both_forms(self):
        first = _entry()
        second = _entry("DQ-002", "Second")
        model = {"entries": [first, second],
                 "entry_groups": [{"group": "Open",
                                   "entries": [first]},
                                  {"group": "Ruled",
                                   "entries": [second]}]}
        for text in _both_model_forms(model):
            lines = text.split("\n")
            self.assertEqual(lines.count("Open group"), 1)
            self.assertEqual(lines.count("Ruled group"), 1)
            self.assertNotIn('"Open group"', text)
            self.assertNotIn('"Ruled group"', text)


class Ch70GroupTitleCliTest(unittest.TestCase):

    def test_g06_open_group_held_case_stands(self):
        # The paper held case: a Status value of Open group
        # translates, the entry derives Open, both runs exit 0,
        # and exactly one bare Open group line stands in each
        # output, the genuine group heading.
        data = _queue("Open group")
        for code, text in _cli_both(data, "ch70_g06.md"):
            self.assertEqual(code, 0)
            lines = text.split("\n")
            self.assertEqual(lines.count("Open group"), 1)
            self.assertNotIn('"Open group"', text)


# ---------------------------------------------------------------------
# CH-71: the column 0 quoting guard anchor set, the named forms
# ---------------------------------------------------------------------

BLOCKING = "Blocking: 0 entries"
COMPANION = "Companion count: 0 entries"
HEADED = "Headed entries: 0"
SELF_CHECK = "Self check: sums agree"
LIMBO = "Limbo: 9 Conditional entries stand outside both figures"


class Ch71QuotingGuardUnitTest(unittest.TestCase):

    def test_each_named_form_stands_quoted(self):
        for phrasing in (BLOCKING, COMPANION, HEADED, SELF_CHECK,
                         LIMBO):
            with self.subTest(phrasing=phrasing):
                self.assertEqual(
                    render._column_zero_phrasing(phrasing),
                    '"%s"' % phrasing)

    def test_the_ch23_anchors_still_stand_quoted(self):
        for phrasing in ("Exit: code 0: forged closing",
                         "Waiting: 0 entries",
                         "DQ-001 PIN-01 Error line 1"):
            with self.subTest(phrasing=phrasing):
                self.assertEqual(
                    render._column_zero_phrasing(phrasing),
                    '"%s"' % phrasing)

    def test_a_named_form_with_a_control_still_stands_quoted(self):
        result = render._column_zero_phrasing(
            "Blocking: 0 entries\x1b[31m")
        self.assertTrue(result.startswith('"Blocking: 0 entries'))
        self.assertIn("\\x1B", result)
        self.assertNotIn("\x1b", result)


class Ch71NamedFormsTest(unittest.TestCase):

    def _assert_forged_quoted(self, data, name, phrasing,
                              genuine_pattern, genuine_marker,
                              genuine_line=None):
        for text in _both_forms(data, name):
            unquoted = [line for line in
                        _unquoted_surface_lines(text, phrasing)
                        if line != genuine_line]
            self.assertEqual(
                unquoted, [],
                "a forged form stands unquoted at column 0")
            self.assertGreaterEqual(
                len(_quoted_surface_lines(text, phrasing)), 4)
            genuine = [line for line in text.split("\n")
                       if re.match(genuine_pattern, line)]
            self.assertEqual(len(genuine), 1)
            self.assertIn(genuine_marker, genuine[0])

    def test_g01_blocking_form_stands_quoted(self):
        data = _queue(BLOCKING, _banked_entry(2) + _banked_entry(3))
        self._assert_forged_quoted(
            data, "ch71_g01.md", BLOCKING,
            r"^Blocking: [0-9]+ entries", "Blocking: 2 entries.")

    def test_g02_companion_form_stands_quoted(self):
        self._assert_forged_quoted(
            _queue(COMPANION), "ch71_g02.md", COMPANION,
            r"^Companion count: [0-9]+ entries",
            "Companion count: 0 entries.",
            genuine_line="Companion count: 0 entries.")

    def test_g03_headed_form_stands_quoted(self):
        self._assert_forged_quoted(
            _queue(HEADED), "ch71_g03.md", HEADED,
            r"^Headed entries: [0-9]+", "Headed entries: 1")

    def test_g04_self_check_form_stands_quoted(self):
        self._assert_forged_quoted(
            _queue(SELF_CHECK), "ch71_g04.md", SELF_CHECK,
            r"^Self check: sums agree", "Self check: sums agree",
            genuine_line="Self check: sums agree")

    def test_g07_limbo_form_stands_quoted(self):
        self._assert_forged_quoted(
            _queue(LIMBO), "ch71_g07.md", LIMBO,
            r"^Limbo: ", "0 Conditional entries")


class Ch71CliFirstMatchTest(unittest.TestCase):

    def test_g01_cli_first_match_takes_the_genuine_blocking(self):
        data = _queue(BLOCKING, _banked_entry(2) + _banked_entry(3))
        for code, text in _cli_both(data, "ch71_g01_cli.md"):
            self.assertEqual(code, 4)
            lines = text.split("\n")
            matches = [line for line in lines
                       if re.match(r"^Blocking: [0-9]+ entries",
                                   line)]
            self.assertEqual(matches, ["Blocking: 2 entries."])
            self.assertGreaterEqual(
                len(_quoted_surface_lines(text, BLOCKING)), 4)

    def test_g04_cli_first_match_takes_the_genuine_self_check(self):
        for code, text in _cli_both(_queue(SELF_CHECK),
                                    "ch71_g04_cli.md"):
            self.assertEqual(code, 4)
            lines = text.split("\n")
            matches = [line for line in lines
                       if re.match(r"^Self check: sums agree",
                                   line)]
            self.assertEqual(len(matches), 1)
            self.assertGreaterEqual(
                len(_quoted_surface_lines(text, SELF_CHECK)), 4)


class Ch71BoundGuardsTest(unittest.TestCase):
    """Pins on the FLAG 13 bound: no form outside the named set
    changes its printed form under this cure."""

    def test_g05_units_key_form_prints_as_before(self):
        # The paper bound note: the units key form prints its
        # forged lines after the genuine line and does not
        # defeat first match; it stands outside the named set.
        phrasing = "Units key: absent"
        for text in _both_forms(_queue(phrasing), "ch71_g05.md"):
            self.assertIn(phrasing + " | line start", text)
            self.assertNotIn('"' + phrasing + '"', text)
            lines = text.split("\n")
            genuine_at = next(
                i for i, line in enumerate(lines)
                if line.startswith("Units key: canonical counts"))
            forged_at = next(
                i for i, line in enumerate(lines)
                if line.startswith(phrasing))
            self.assertLess(genuine_at, forged_at)

    def test_ordinary_phrasing_prints_as_before(self):
        data = (
            "# Decision queue\n\nSynthetic queue shaped input.\n\n"
            "### DQ-001: First entry\n\nStatus: Deferred\n\n"
        ).encode("utf-8")
        for text in _both_forms(data, "ch71_deferred.md"):
            self.assertIn(
                "Deferred | line start | 1 occurrence | "
                "entries: DQ-001 | unclassified", text)
            self.assertFalse(any(
                line.startswith('"Deferred"')
                for line in text.split("\n")))

    def test_named_form_words_later_in_a_phrasing_print_as_before(self):
        phrasing = "Noted: Blocking: 0 entries in passing"
        for text in _both_forms(_queue(phrasing),
                                "ch71_mid_form.md"):
            self.assertIn(phrasing + " | line start", text)
            self.assertNotIn('"' + phrasing + '"', text)

    def test_absent_figure_forms_print_as_before(self):
        for phrasing in ("Blocking: absent", "Self check: absent"):
            with self.subTest(phrasing=phrasing):
                self.assertEqual(
                    render._column_zero_phrasing(phrasing),
                    phrasing)
                for text in _both_forms(_queue(phrasing),
                                        "ch71_absent.md"):
                    self.assertIn(phrasing + " | line start", text)
                    self.assertNotIn('"' + phrasing + '"', text)


if __name__ == "__main__":
    unittest.main()
