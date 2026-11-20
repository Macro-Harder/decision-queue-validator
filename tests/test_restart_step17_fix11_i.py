"""Step 17 (restart) fix wave 11, Fix Seat I tests, test first.

Charges CH-310 and CH-311, Cluster I, the joiner target
list, consolidated in design/steps/step-17r-r11-triage-prep.md
at its Cluster I from the source paper
design/steps/step-17r-r11-seat09-run.md (seat 9 Findings 1
and 2 of round 11, each Low, distinct findings T11-38 and
T11-39). Locus: product/decision_queue_validator/validate.py
only, at the supersession target list reading as cured at
CH-269 and CH-270.

CH-310 (T11-38, Finding 1): a target list on the forms one
step past the CH-269 sets loses the head pointer its cured
sibling forms derive, while its signal stands and names the
head among the missed targets: the three remaining CH-223
joiner forms at the no space spacing (the double pipe, the
double ampersand, and the ideographic comma U+3001), a
Unicode space character outside the six CH-269 names at the
charged semicolon (the em quad U+2001, the six per em space
U+2006, the figure space U+2007, the thin space U+2009, the
hair space U+200A, and the mathematical space U+205F, the
thin space also in the before only pairing), a joiner
outside the three CH-269 spaced joiners at a charged Unicode
spacing (the hash, the at sign, the percent, the double
slash, the underscore, and the double plus), and a CH-270
joiner form at the no space spacing (the double backslash,
the triple plus, the double colon, and the small comma
U+FE50). The charge asks the head exception question be
settled for these forms and does not ask that any middle
pointer derive: the signal only ruling stands.

CH-311 (T11-39, Finding 2): a target list joined by a
tripled CH-270 joiner (the triple backslash, the triple
greater than, the triple colon, and the triple underscore),
a quadrupled charged joiner (the quadruple plus), a doubled
CH-183 joiner outside the CH-270 ten (the double hash, the
double asterisk, the double at sign, and the double
percent), a doubled comma lookalike of the CH-270 pair (the
double Arabic comma U+060C, the double small comma U+FE50,
and the double fullwidth comma U+FF0C), or the double dollar,
derives pointers for its end targets only and drops the
remaining targets silently with no signal of any class. The
charge is the silence, not the derivation: signal only, no
pointer derives from any list this charge names past the end
readings those lists already took.

Constructions stand in the attack paper shape: one claiming
entry carrying the statement in both clauses, headed targets,
each entry carrying Status: Ruled, so no construction in
this file is of the F1 shape.

Copyright: J.P. Picard aka Macro-Harder
"""

import unittest

import dqv_harness as h

_HEADER = "# Decision Queue\n\n## Open items\n\n"

# CH-310 limb A: the remaining CH-223 forms, no space.
_CH310_NOSPACE_JOINERS = {
    "double_pipe": "||",
    "double_ampersand": "&&",
    "ideographic_comma": "、",
}

# CH-310 limb B: space characters past the six CH-269
# names, at the charged semicolon, symmetric pairings.
_CH310_SEMICOLON_SPACES = {
    "em_quad": "\u2001;\u2001",
    "six_per_em": " ; ",
    "figure_space": " ; ",
    "thin_space": " ; ",
    "hair_space": " ; ",
    "math_space": " ; ",
}

# CH-310 limb C: joiners past the three CH-269 spaced
# joiners, at charged Unicode spacings.
_CH310_SPACED_JOINERS = {
    "hash_enspace": " # ",
    "at_emspace": " @ ",
    "percent_ideographic": "　%　",
    "double_slash_enspace": " // ",
    "underscore_enspace": " _ ",
    "double_plus_enspace": " ++ ",
    "hash_nbsp": " # ",
}

# CH-310 limb F: CH-270 forms at the no space spacing.
_CH310_CH270_NOSPACE_JOINERS = {
    "double_backslash": "\\" * 2,
    "triple_plus": "+++",
    "double_colon": "::",
    "small_comma": "﹐",
}

# CH-311: the ring further out joiners, spaced forms.
_CH311_TRIPLED_JOINERS = {
    "triple_backslash": " " + "\\" * 3 + " ",
    "triple_greater_than": " >>> ",
    "triple_colon": " ::: ",
    "triple_underscore": " ___ ",
}

_CH311_QUADRUPLED_AND_DOUBLED_JOINERS = {
    "quadruple_plus": " ++++ ",
    "double_hash": " ## ",
    "double_asterisk": " ** ",
    "double_at": " @@ ",
    "double_percent": " %% ",
}

_CH311_DOUBLED_LOOKALIKE_JOINERS = {
    "double_arabic_comma": " ،، ",
    "double_small_comma": " ﹐﹐ ",
    "double_fullwidth_comma": " ，， ",
    "double_dollar": " $$ ",
}

# Pins: the cured CH-269 forms of fix wave 10.
_PIN_CH269_NOSPACE = {
    "underscore": "_",
    "double_plus": "++",
    "semicolon_colon": ";˸",
    "fullwidth_comma": "，",
}

_PIN_CH269_SEMICOLON_SPACES = {
    "em_space": " ; ",
    "ideographic_space": "　;　",
    "en_quad": " ; ",
}

_PIN_CH269_OTHER = {
    "plus_enspace": " + ",
    "asterisk_enspace": " * ",
}

# Pins: the cured CH-270 forms of fix wave 10, spaced.
_PIN_CH270_SPACED = {
    "double_backslash": " " + "\\" * 2 + " ",
    "double_greater_than": " >> ",
    "triple_plus": " +++ ",
    "double_colon": " :: ",
    "small_comma": " ﹐ ",
}

# Pins: controls inside the CH-269 bounds at new pairings
# (seat 9 round 11 section 2D, passing on the standing tree).
_PIN_INSIDE_BOUNDS = {
    "plus_ideographic": "　+　",
    "asterisk_nbsp": " * ",
    "semicolon_tab_ensp": "\t; ",
    "plus_narrow_nbsp_before_only": " +",
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
    names = joiner.join("DQ-%03d" % t if t < 900 else "DQ-999"
                        for t in targets)
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


def _assert_signal_only(case, joiner):
    text = _list_file(
        5, _joined_statement([1, 2, 3, 4], joiner), [1, 2, 3, 4])
    output = _run_text(text)
    _assert_list_stands_whole(case, output, ["DQ-002", "DQ-003"])


class Ch310RemainingCh223NoSpaceHeadTest(unittest.TestCase):
    """CH-310 limb A: the three remaining CH-223 joiner
    forms at the no space spacing derive the head pointer
    their cured sibling forms derive, signal naming the
    middles only, no middle pointer deriving."""

    def test_remaining_ch223_nospace_head_restored(self):
        for name, joiner in sorted(
                _CH310_NOSPACE_JOINERS.items()):
            with self.subTest(joiner=name):
                _assert_signal_only(self, joiner)


class Ch310RemainingCh223PositionsTest(unittest.TestCase):
    """CH-310 limb A at new positions: the double pipe form
    with a ghost middle, and the double ampersand form at
    eight targets, derive the head pointer."""

    def test_double_pipe_nospace_ghost_head_restored(self):
        text = _list_file(
            5, _joined_statement([1, 999, 3, 4], "||"),
            [1, 3, 4])
        output = _run_text(text)
        self.assertEqual(_pointers(output, "DQ-001"), ["DQ-005"])
        self.assertEqual(_pointers(output, "DQ-004"), ["DQ-005"])
        self.assertEqual(_pointers(output, "DQ-003"), [])
        notes = _not_recognised_notes(output)
        self.assertEqual(len(notes), 1)
        self.assertEqual(_named_entries(notes[0]), ["DQ-003"])
        ghosts = [f for f in _by_rule(output, "PD-R7")]
        self.assertEqual(len(ghosts), 1)

    def test_double_ampersand_nospace_eight_head_restored(self):
        text = _list_file(
            9, _joined_statement([1, 2, 3, 4, 5, 6, 7, 8], "&&"),
            [1, 2, 3, 4, 5, 6, 7, 8])
        output = _run_text(text)
        self.assertEqual(_pointers(output, "DQ-001"), ["DQ-009"])
        self.assertEqual(_pointers(output, "DQ-008"), ["DQ-009"])
        for mid in ("DQ-002", "DQ-003", "DQ-004", "DQ-005",
                    "DQ-006", "DQ-007"):
            self.assertEqual(_pointers(output, mid), [])
        notes = _not_recognised_notes(output)
        self.assertEqual(len(notes), 1)
        self.assertEqual(
            _named_entries(notes[0]),
            ["DQ-002", "DQ-003", "DQ-004", "DQ-005",
             "DQ-006", "DQ-007"])


class Ch310UnicodeSpaceSemicolonHeadTest(unittest.TestCase):
    """CH-310 limb B: the charged semicolon spaced by a
    space character past the six CH-269 names derives the
    head pointer, signal naming the middles only."""

    def test_further_space_semicolon_head_restored(self):
        for name, joiner in sorted(
                _CH310_SEMICOLON_SPACES.items()):
            with self.subTest(joiner=name):
                _assert_signal_only(self, joiner)

    def test_thin_space_before_only_head_restored(self):
        _assert_signal_only(self, " ;")


class Ch310SpacedJoinerHeadTest(unittest.TestCase):
    """CH-310 limb C: a joiner past the three CH-269 spaced
    joiners at a charged Unicode spacing derives the head
    pointer, signal naming the middles only."""

    def test_further_spaced_joiner_head_restored(self):
        for name, joiner in sorted(
                _CH310_SPACED_JOINERS.items()):
            with self.subTest(joiner=name):
                _assert_signal_only(self, joiner)


class Ch310Ch270NoSpaceHeadTest(unittest.TestCase):
    """CH-310 limb F: a CH-270 joiner form at the no space
    spacing derives the head pointer, its signal standing
    and naming the middles only, no middle pointer
    deriving under the signal only ruling."""

    def test_ch270_nospace_head_restored(self):
        for name, joiner in sorted(
                _CH310_CH270_NOSPACE_JOINERS.items()):
            with self.subTest(joiner=name):
                _assert_signal_only(self, joiner)


class Ch311TripledJoinerSignalTest(unittest.TestCase):
    """CH-311: a target list joined by a tripled CH-270
    joiner takes the not recognised signal for its
    middles, signal only, end pointers standing."""

    def test_tripled_joiner_lists_take_the_signal(self):
        for name, joiner in sorted(
                _CH311_TRIPLED_JOINERS.items()):
            with self.subTest(joiner=name):
                _assert_signal_only(self, joiner)


class Ch311QuadrupledAndDoubledJoinerSignalTest(unittest.TestCase):
    """CH-311: a target list joined by a quadrupled charged
    joiner or a doubled CH-183 joiner outside the CH-270
    ten takes the signal for its middles, signal only."""

    def test_quadrupled_and_doubled_lists_take_the_signal(self):
        for name, joiner in sorted(
                _CH311_QUADRUPLED_AND_DOUBLED_JOINERS.items()):
            with self.subTest(joiner=name):
                _assert_signal_only(self, joiner)


class Ch311DoubledLookalikeSignalTest(unittest.TestCase):
    """CH-311: a target list joined by a doubled comma
    lookalike of the CH-270 pair, or the double dollar,
    takes the signal for its middles, signal only."""

    def test_doubled_lookalike_lists_take_the_signal(self):
        for name, joiner in sorted(
                _CH311_DOUBLED_LOOKALIKE_JOINERS.items()):
            with self.subTest(joiner=name):
                _assert_signal_only(self, joiner)


class ClusterIPinsTest(unittest.TestCase):
    """The governing pins of this surface, passing before
    and after: the cured CH-269 and CH-270 forms whole, the
    signal only ruling in its own terms (no middle pointer
    derives from any signal list), the controls inside the
    CH-269 bounds at new pairings, the caret pin at both
    spacings, and the colon no space bound."""

    def test_cured_ch269_forms_stand(self):
        for group in (_PIN_CH269_NOSPACE,
                      _PIN_CH269_SEMICOLON_SPACES, _PIN_CH269_OTHER):
            for name, joiner in sorted(group.items()):
                with self.subTest(joiner=name):
                    _assert_signal_only(self, joiner)

    def test_cured_ch270_forms_stand(self):
        for name, joiner in sorted(_PIN_CH270_SPACED.items()):
            with self.subTest(joiner=name):
                _assert_signal_only(self, joiner)

    def test_signal_only_no_middle_pointer_derives(self):
        for joiner in (" || ", " && ", " " + "\\" * 2 + " ",
                       " >> ", ";"):
            text = _list_file(
                5, _joined_statement([1, 2, 3, 4], joiner),
                [1, 2, 3, 4])
            output = _run_text(text)
            self.assertEqual(_pointers(output, "DQ-002"), [])
            self.assertEqual(_pointers(output, "DQ-003"), [])

    def test_controls_inside_ch269_bounds_stand(self):
        for name, joiner in sorted(_PIN_INSIDE_BOUNDS.items()):
            with self.subTest(joiner=name):
                _assert_signal_only(self, joiner)

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
