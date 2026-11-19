"""Step 17 (restart) fix wave 10, Fix Seat I tests, test first.

Charges CH-269 and CH-270, Cluster I, the joiner target
list family of round 10, consolidated in
design/steps/step-17r-r10-triage-prep.md at its
Cluster I and stated from the source paper
design/steps/step-17r-r10-seat09.md (seat 9 Findings 1
and 2 of round 10, each Low). Locus:
product/decision_queue_validator/validate.py only, at
the supersession target list reading, the CH-222 and
CH-223 cure family of fix wave 9 seat J.

CH-269 (T10-46, Finding 1): a target list on a CH-223
joiner form with no space on either side of the joiner
(the underscore, double plus, semicolon with modifier
letter colon U+02F8, and fullwidth comma U+FF0C forms,
cases u38 to u41), and a target list spaced by a
Unicode space character outside the two characters and
the one joiner CH-222 names (cases u14 to u21, u42,
u43), loses the head pointer its cured form derives,
while its signal stands and names the head among the
missed targets. The cure asked is the head derivation
only for these forms: no middle pointer derives from
any CH-223 list, the signal only posture of CH-223
standing as pinned.

CH-270 (T10-47, Finding 2): a target list joined by a
doubled charged joiner outside the three CH-223
doubles (the double backslash, double greater than,
double equals, double Greek question mark U+037E, and
double fullwidth question mark U+FF1F forms), by a
tripled charged joiner (the triple plus), by a
doubled underscore, by a further comma lookalike (the
small comma U+FE50 and the Arabic comma U+060C), or
by a doubled colon (cases u22 to u32), derives
pointers for its end targets only and drops the
remaining targets silently, with no signal of any
class. The cure asked is the signal only, in the
CH-223 posture: the missed middles take the not
recognised Note, and no pointer derives from any list
this charge names past the end readings those lists
already took. The caret form stands outside this
charge expressly, as its fix wave 8 K7 pin holds it.

Constructions stand in the attack paper shape: one
claiming entry carrying the statement in both clauses,
headed targets, each entry carrying Status: Ruled, so
no construction in this file is of the F1 shape.

Copyright: J.P. Picard aka Macro-Harder
"""

import unittest

import dqv_harness as h

_HEADER = "# Decision Queue\n\n## Open items\n\n"

_CH223_NOSPACE_JOINERS = {
    "underscore": "_",
    "double_plus": "++",
    "semicolon_colon": ";˸",
    "fullwidth_comma": "，",
}

_UNICODE_SPACE_SEMICOLON_JOINERS = {
    "enspace_before_only": " ;",
    "nbsp_after_only": "; ",
    "enspace_nbsp_mixed": " ; ",
    "em_space": " ; ",
    "ideographic_space": "　;　",
    "narrow_nbsp": " ; ",
    "en_quad": " ; ",
    "enspace_tab_mixed": " ;\t",
}

_UNICODE_SPACE_OTHER_JOINERS = {
    "plus_enspace": " + ",
    "asterisk_enspace": " * ",
}

_CH270_DOUBLED_JOINERS = {
    "double_backslash": " " + "\\" * 2 + " ",
    "double_greater_than": " >> ",
    "double_equals": " == ",
    "double_greek_question": " ;; ",
    "double_fullwidth_question": " ？？ ",
    "double_underscore": " __ ",
    "double_colon": " :: ",
}

_CH270_COMMA_LOOKALIKE_JOINERS = {
    "small_comma": " ﹐ ",
    "arabic_comma": " ، ",
}

_CH223_SPACED_JOINERS = {
    "underscore": " _ ",
    "double_plus": " ++ ",
    "double_pipe": " || ",
    "double_ampersand": " && ",
    "semicolon_colon": " ;˸ ",
    "fullwidth_comma": " ， ",
    "ideographic_comma": " 、 ",
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


class Ch269Ch223NoSpaceHeadTest(unittest.TestCase):
    """CH-269, the CH-223 limb: a target list on a CH-223
    joiner form with no space on either side of the joiner
    derives the head pointer its spaced form derives, and
    its signal names the middles only. No middle pointer
    derives, the signal only posture standing."""

    def test_ch223_nospace_head_pointer_restored(self):
        for name, joiner in sorted(
                _CH223_NOSPACE_JOINERS.items()):
            with self.subTest(joiner=name):
                text = _list_file(
                    5, _joined_statement([1, 2, 3, 4], joiner),
                    [1, 2, 3, 4])
                output = _run_text(text)
                _assert_list_stands_whole(
                    self, output, ["DQ-002", "DQ-003"])


class Ch269UnicodeSpaceSemicolonHeadTest(unittest.TestCase):
    """CH-269, the Unicode space limb at the charged
    semicolon: a target list spaced by a Unicode space
    character outside the two characters CH-222 names,
    in an asymmetric pair, a mismatched pair, or another
    character of the Zs class on each side, derives the
    head pointer the plain spaced form derives, and its
    signal names the middles only."""

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


class Ch269UnicodeSpaceOtherJoinerHeadTest(unittest.TestCase):
    """CH-269, the Unicode space limb at the other charged
    joiners of its cases: a target list on the plus form
    or the asterisk form spaced by en spaces derives the
    head pointer its plain spaced form derives, and its
    signal names the middles only."""

    def test_unicode_space_other_joiner_head_pointer_restored(self):
        for name, joiner in sorted(
                _UNICODE_SPACE_OTHER_JOINERS.items()):
            with self.subTest(joiner=name):
                text = _list_file(
                    5, _joined_statement([1, 2, 3, 4], joiner),
                    [1, 2, 3, 4])
                output = _run_text(text)
                _assert_list_stands_whole(
                    self, output, ["DQ-002", "DQ-003"])


class Ch270DoubledJoinerSignalTest(unittest.TestCase):
    """CH-270, the doubled joiners: a target list joined
    by a doubled charged joiner outside the three CH-223
    doubles, by a doubled underscore, or by a doubled
    colon takes the not recognised signal for its
    middles, signal only, its end pointers standing as
    they already stood."""

    def test_doubled_joiner_lists_take_the_signal(self):
        for name, joiner in sorted(
                _CH270_DOUBLED_JOINERS.items()):
            with self.subTest(joiner=name):
                text = _list_file(
                    5, _joined_statement([1, 2, 3, 4], joiner),
                    [1, 2, 3, 4])
                output = _run_text(text)
                _assert_list_stands_whole(
                    self, output, ["DQ-002", "DQ-003"])


class Ch270TriplePlusSignalTest(unittest.TestCase):
    """CH-270, the tripled joiner: a target list joined
    by a triple plus takes the not recognised signal for
    its middles, signal only."""

    def test_triple_plus_list_takes_the_signal(self):
        text = _list_file(
            5, _joined_statement([1, 2, 3, 4], " +++ "),
            [1, 2, 3, 4])
        output = _run_text(text)
        _assert_list_stands_whole(
            self, output, ["DQ-002", "DQ-003"])


class Ch270CommaLookalikeSignalTest(unittest.TestCase):
    """CH-270, the further comma lookalikes: a target list
    joined by a small comma U+FE50 or an Arabic comma
    U+060C takes the not recognised signal for its
    middles, signal only."""

    def test_comma_lookalike_lists_take_the_signal(self):
        for name, joiner in sorted(
                _CH270_COMMA_LOOKALIKE_JOINERS.items()):
            with self.subTest(joiner=name):
                text = _list_file(
                    5, _joined_statement([1, 2, 3, 4], joiner),
                    [1, 2, 3, 4])
                output = _run_text(text)
                _assert_list_stands_whole(
                    self, output, ["DQ-002", "DQ-003"])


class ClusterIPinsTest(unittest.TestCase):
    """The governing pins of this surface, passing before
    and after: the caret list at its K7 pin in the spaced
    form and standing as recorded at the no space spacing,
    the spaced CH-223 forms whole in their signal only
    posture, and the colon no space bound."""

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

    def test_caret_nospace_stands_as_recorded(self):
        text = _list_file(
            5, _joined_statement([1, 2, 3, 4], "^"),
            [1, 2, 3, 4])
        output = _run_text(text)
        self.assertEqual(_pointers(output, "DQ-001"), [])
        self.assertEqual(_pointers(output, "DQ-004"), ["DQ-005"])
        self.assertEqual(_pointers(output, "DQ-002"), [])
        self.assertEqual(_pointers(output, "DQ-003"), [])
        self.assertEqual(h.findings_of(output), [])

    def test_spaced_ch223_forms_stand_whole(self):
        for name, joiner in sorted(
                _CH223_SPACED_JOINERS.items()):
            with self.subTest(joiner=name):
                text = _list_file(
                    5, _joined_statement([1, 2, 3, 4], joiner),
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
