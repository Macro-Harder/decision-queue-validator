"""Step 17 (restart) fix wave 9, Fix Seat J tests, test first.

Charges CH-222 and CH-223, Cluster J, the joiner target
lists, ruled TO FIX at section 81 ruling (a) of
design/steps/step-17r-record.md, charges numbered
consecutively from CH-191 in cluster order per the
proposed charge split as filed in
design/steps/step-17r-r9-triage-prep.md section 3 (one
charge per distinct finding: Cluster A CH-191 and
CH-192, Cluster B CH-193 to CH-196, Cluster C CH-197,
Cluster D CH-198, Cluster E CH-199 to CH-205, Cluster F
CH-206 to CH-212, Cluster G CH-213 and CH-214, Cluster H
CH-215 to CH-218, Cluster I CH-219 to CH-221, so Cluster
J takes CH-222 and CH-223 and Cluster K takes CH-224).
Findings T9-30 and T9-31, seat 9 Findings 1 and 2 of
round 9, at design/steps/step-17r-attack9-9.md, each
Low. Locus: product/decision_queue_validator/validate.py
only, at the supersession target list reading, the
CH-166 and CH-183 cure family of fix wave 8 seat K7.

CH-222 (T9-30, Finding 1): a target list on a CH-183
joiner form with no space on either side of the joiner
(the asterisk, arabic semicolon, double slash, and at
sign forms charged, cases t15 to t18), and a target
list on the charged semicolon form spaced by an en
space (U+2002) or a no break space (U+00A0) on each
side (cases t36 and t37), loses the head pointer its
spaced form derives, while its signal stands and names
the head among the missed targets. The cure is the
head derivation only, at the no space adjacency for
the CH-183 joiner characters and at the two Unicode
space characters for the charged semicolon: no middle
pointer derives from any CH-183 list, in the signal
only posture of CH-183. Pins: the spaced CH-183 forms
stand whole, and the tab spaced semicolon form (case
t38) stands whole.

CH-223 (T9-31, Finding 2): a target list joined by a
doubled charged joiner (double plus, double pipe,
double ampersand), by a semicolon lookalike (the
semicolon with modifier letter colon U+02F8), by a
comma lookalike (the fullwidth comma U+FF0C, the
ideographic comma U+3001), or by an underscore (cases
t29 to t35), derives pointers for its end targets only
and drops the remaining targets silently, with no
signal of any class. The cure is the signal only, in
the CH-183 posture: the missed middles take the not
recognised Note, and no pointer derives from any list
this charge names past the end readings those lists
already took. Pin: the caret list (case t28) stands as
the fix wave 8 K7 pin class holds it, at no signal and
no pointer past its end readings.

Constructions stand in the attack paper shape: one
claiming entry carrying the statement in both clauses,
headed targets, each entry carrying Status: Ruled, so
no construction in this file is of the F1 shape.

Copyright: J.P. Picard aka Macro-Harder
"""

import unittest

import dqv_harness as h

_HEADER = "# Decision Queue\n\n## Open items\n\n"

_CH183_NOSPACE_JOINERS = {
    "arabic_semicolon": "؛",
    "reversed_semicolon": "⁏",
    "vertical_semicolon": "︔",
    "asterisk": "*",
    "at_sign": "@",
    "hash": "#",
    "percent": "%",
    "double_slash": "//",
}

_CH183_SPACED_JOINERS = {
    "arabic_semicolon": " ؛ ",
    "reversed_semicolon": " ⁏ ",
    "vertical_semicolon": " ︔ ",
    "asterisk": " * ",
    "at_sign": " @ ",
    "hash": " # ",
    "percent": " % ",
    "double_slash": " // ",
}

_UNICODE_SPACE_SEMICOLON_JOINERS = {
    "en_space": " ; ",
    "no_break_space": " ; ",
}


def _ruled_entry(number, ruling_line):
    return (
        "### DQ-%03d: Synthetic entry %d\n\n"
        "Status: Ruled\n\n"
        "Ruled by: Captain JP\n\n"
        "Ruling text: \"%s\"\n\n"
        "Ruling outcome: The synthetic outcome stands.\n\n"
        "Where the ruling landed: synthetic record.\n\n"
        % (number, number, ruling_line))


def _joined_statement(targets, joiner):
    names = joiner.join("DQ-%03d" % t for t in targets)
    return (
        "This ruling displaces the rulings at %s in full; "
        "those earlier rulings no longer stand as governing "
        "on their subjects, and %s are the superseded entries."
        % (names, names))


def _list_file(claiming_number, statement, headed):
    total = max([claiming_number] + list(headed))
    parts = [_HEADER]
    for i in range(1, total + 1):
        if i == claiming_number:
            parts.append(_ruled_entry(i, statement))
        else:
            parts.append(_ruled_entry(
                i, "The harbour ruling stands."))
    return "".join(parts)


def _run_text(text):
    _model, output = h.run_pipeline(text.encode("utf-8"))
    if output is None:
        raise AssertionError("pipeline returned the failure result")
    return output


def _by_rule(output, rule_text):
    return [f for f in h.findings_of(output)
            if (h.text_of(h.get(f, "rule_id", "rule")) or "")
            == rule_text]


def _not_recognised_notes(output):
    return [f for f in _by_rule(output, "PIN-10")
            if h.finding_severity(f) == "Note"
            and "not recognised" in (h.finding_statement(f) or "")]


def _named_entries(finding):
    return [h.text_of(x) for x in h.as_list(
        h.get(finding, "named_entries", "named_entry_ids"))]


def _pointers(output, entry_id):
    entry = h.entry_by_id(output, entry_id)
    if entry is None:
        raise AssertionError("no entry " + entry_id)
    return [h.text_of(p) for p in h.as_list(
        h.get(entry, "supersession_pointers"))]


def _assert_list_stands_whole(case, output, note_named):
    case.assertEqual(_pointers(output, "DQ-001"), ["DQ-005"])
    case.assertEqual(_pointers(output, "DQ-004"), ["DQ-005"])
    case.assertEqual(_pointers(output, "DQ-002"), [])
    case.assertEqual(_pointers(output, "DQ-003"), [])
    notes = _not_recognised_notes(output)
    case.assertEqual(len(notes), 1)
    case.assertEqual(_named_entries(notes[0]), note_named)


class Ch222Ch183NoSpaceHeadTest(unittest.TestCase):
    """CH-222, the CH-183 limb: a target list on a CH-183
    joiner form with no space on either side of the joiner
    derives the head pointer its spaced form derives, and
    its signal names the middles only, as the spaced form
    states it. No middle pointer derives."""

    def test_ch183_nospace_head_pointer_restored(self):
        for name, joiner in sorted(
                _CH183_NOSPACE_JOINERS.items()):
            with self.subTest(joiner=name):
                text = _list_file(
                    5, _joined_statement([1, 2, 3, 4], joiner),
                    [1, 2, 3, 4])
                output = _run_text(text)
                _assert_list_stands_whole(
                    self, output, ["DQ-002", "DQ-003"])


class Ch222UnicodeSpaceSemicolonTest(unittest.TestCase):
    """CH-222, the Unicode space limb: a target list on
    the charged semicolon form spaced by an en space or
    a no break space on each side derives the head
    pointer the tab spaced and plain spaced forms
    derive, and its signal names the middles only."""

    def test_unicode_space_semicolon_head_pointer_restored(self):
        for name, joiner in sorted(
                _UNICODE_SPACE_SEMICOLON_JOINERS.items()):
            with self.subTest(joiner=name):
                text = _list_file(
                    5, _joined_statement([1, 2, 3, 4], joiner),
                    [1, 2, 3, 4])
                output = _run_text(text)
                _assert_list_stands_whole(
                    self, output, ["DQ-002", "DQ-003"])


class Ch223DoubledJoinerSignalTest(unittest.TestCase):
    """CH-223, the doubled joiners: a target list joined
    by a doubled charged joiner takes the not recognised
    signal for its middles, signal only, its end pointers
    standing as they already stood."""

    def test_doubled_joiner_lists_take_the_signal(self):
        for name, joiner in sorted({
                "double_plus": " ++ ",
                "double_pipe": " || ",
                "double_ampersand": " && "}.items()):
            with self.subTest(joiner=name):
                text = _list_file(
                    5, _joined_statement([1, 2, 3, 4], joiner),
                    [1, 2, 3, 4])
                output = _run_text(text)
                _assert_list_stands_whole(
                    self, output, ["DQ-002", "DQ-003"])


class Ch223SemicolonLookalikeSignalTest(unittest.TestCase):
    """CH-223, the semicolon lookalike: a target list
    joined by a semicolon with modifier letter colon
    U+02F8 takes the not recognised signal for its
    middles, signal only."""

    def test_semicolon_colon_list_takes_the_signal(self):
        text = _list_file(
            5, _joined_statement([1, 2, 3, 4], " ;˸ "),
            [1, 2, 3, 4])
        output = _run_text(text)
        _assert_list_stands_whole(
            self, output, ["DQ-002", "DQ-003"])


class Ch223CommaLookalikeSignalTest(unittest.TestCase):
    """CH-223, the comma lookalikes: a target list joined
    by a fullwidth comma or an ideographic comma takes
    the not recognised signal for its middles, signal
    only."""

    def test_comma_lookalike_lists_take_the_signal(self):
        for name, joiner in sorted({
                "fullwidth_comma": " ， ",
                "ideographic_comma": " 、 "}.items()):
            with self.subTest(joiner=name):
                text = _list_file(
                    5, _joined_statement([1, 2, 3, 4], joiner),
                    [1, 2, 3, 4])
                output = _run_text(text)
                _assert_list_stands_whole(
                    self, output, ["DQ-002", "DQ-003"])


class Ch223UnderscoreSignalTest(unittest.TestCase):
    """CH-223, the underscore companion: a target list
    joined by an underscore takes the not recognised
    signal for its middles, signal only."""

    def test_underscore_list_takes_the_signal(self):
        text = _list_file(
            5, _joined_statement([1, 2, 3, 4], " _ "),
            [1, 2, 3, 4])
        output = _run_text(text)
        _assert_list_stands_whole(
            self, output, ["DQ-002", "DQ-003"])


class ClusterJPinsTest(unittest.TestCase):
    """The governing pins of this surface, passing before
    and after: the caret list at its K7 pin, the spaced
    CH-183 forms whole, the tab spaced semicolon form
    whole, and the colon no space bound."""

    def test_caret_list_takes_no_signal(self):
        text = _list_file(
            5, _joined_statement([1, 2, 3, 4], " ^ "),
            [1, 2, 3, 4])
        output = _run_text(text)
        self.assertEqual(_pointers(output, "DQ-001"), ["DQ-005"])
        self.assertEqual(_pointers(output, "DQ-004"), ["DQ-005"])
        self.assertEqual(_pointers(output, "DQ-002"), [])
        self.assertEqual(_pointers(output, "DQ-003"), [])
        self.assertEqual(h.findings_of(output), [])

    def test_spaced_ch183_forms_stand_whole(self):
        for name, joiner in sorted(
                _CH183_SPACED_JOINERS.items()):
            with self.subTest(joiner=name):
                text = _list_file(
                    5, _joined_statement([1, 2, 3, 4], joiner),
                    [1, 2, 3, 4])
                output = _run_text(text)
                _assert_list_stands_whole(
                    self, output, ["DQ-002", "DQ-003"])

    def test_tab_semicolon_stands_whole(self):
        text = _list_file(
            5, _joined_statement([1, 2, 3, 4], "\t;\t"),
            [1, 2, 3, 4])
        output = _run_text(text)
        _assert_list_stands_whole(
            self, output, ["DQ-002", "DQ-003"])

    def test_colon_nospace_bound_stands(self):
        text = _list_file(
            5, _joined_statement([1, 2, 3, 4], ":"),
            [1, 2, 3, 4])
        output = _run_text(text)
        self.assertEqual(_pointers(output, "DQ-001"), [])
        self.assertEqual(
            _pointers(output, "DQ-004"), ["DQ-005"])
        self.assertEqual(_pointers(output, "DQ-002"), [])
        self.assertEqual(_pointers(output, "DQ-003"), [])
        notes = _not_recognised_notes(output)
        self.assertEqual(len(notes), 1)
        self.assertEqual(
            _named_entries(notes[0]),
            ["DQ-001", "DQ-002", "DQ-003"])


if __name__ == "__main__":
    unittest.main()
