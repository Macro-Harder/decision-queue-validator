"""Step 17 (restart) fix wave 12, Fix Seat I tests, test first.

Charges CH-349 and CH-350, Cluster I, the joiner target
list, consolidated in design/steps/step-17r-r12-triage-prep.md
at its Cluster I from the source paper
design/steps/step-17r-r12-seat08-run.md (seat 8 Findings 1
and 2 of round 12, each Low, distinct findings T12-37 and
T12-38). Locus: product/decision_queue_validator/validate.py
only, at the supersession target list reading as cured at
CH-310 and CH-311.

CH-349 (T12-37, Finding 1): a target list on the forms one
step past the CH-310 and CH-311 sets loses the head pointer
its cured sibling forms derive, while its signal stands and
names the head among the missed targets: the charged
semicolon spaced by a space character outside the twelve
CH-310 names (the ogham space mark U+1680, the three per
em space U+2004, the four per em space U+2005, and the
punctuation space U+2008, the three per em space also in
the before only pairing and at a ghost middle); a joiner
outside the CH-310 spaced joiner set at a charged Unicode
spacing (the slash, the equals sign, the ampersand, the
pipe, and the backslash); a CH-311 joiner form at the no
space spacing (the triple backslash, the triple greater
than, the quadruple plus, the double hash, the double
dollar, the triple colon, the double asterisk, and the
double small comma U+FE50); and a CH-311 or CH-270 joiner
form spaced by a Unicode space (the triple backslash at
en spaces, the double hash at no break spaces, and the
double greater than at en spaces). The charge asks the
head exception question be settled for these forms and
does not ask that any middle pointer derive: the signal
only ruling stands.

CH-350 (T12-38, Finding 2): a target list joined by a
quadrupled or quintupled CH-311 joiner (the quadruple
backslash, the quadruple greater than, the quintuple
plus, the quadruple underscore, and the quadruple colon),
by a tripled doubled CH-183 joiner (the triple hash, the
triple asterisk, the triple at sign, and the triple
percent), by a doubled punctuation form outside every
charged signal set (the double hyphen, the double
semicolon, the double question mark, the double tilde,
and the double exclamation mark), or by a single dollar
or hyphen at an en space, derives pointers for its end
targets only (one pointer only on the single joiner
forms) and drops its remaining targets silently with no
signal of any class. The charge is the silence, not the
derivation: signal only, no pointer derives from any list
this charge names past the end readings those lists
already took.

Constructions stand in the attack paper shape: one
claiming entry carrying the statement in both clauses,
headed targets, each entry carrying Status: Ruled, so no
construction in this file is of the F1 shape.

Copyright: J.P. Picard aka Macro-Harder
"""

import unittest

import dqv_harness as h

_HEADER = "# Decision Queue\n\n## Open items\n\n"

# CH-349 limb A: space characters past the twelve CH-310
# names, at the charged semicolon, symmetric pairings.
_CH349_SEMICOLON_SPACES = {
    "ogham": "\u1680;\u1680",
    "three_per_em": " ; ",
    "four_per_em": " ; ",
    "punctuation_space": " ; ",
}

# CH-349 limb B: joiners past the CH-310 spaced joiner
# set, at charged Unicode spacings, symmetric pairings.
_CH349_SPACED_JOINERS = {
    "slash_enspace": " / ",
    "equals_emspace": " = ",
    "ampersand_ideographic": "　&　",
    "pipe_enspace": " | ",
    "backslash_nbsp": " \\ ",
}

# CH-349 limb C: CH-311 joiner forms at the no space
# spacing.
_CH349_CH311_NOSPACE_JOINERS = {
    "triple_backslash": "\\" * 3,
    "triple_greater_than": ">>>",
    "quadruple_plus": "++++",
    "double_hash": "##",
    "double_dollar": "$$",
    "triple_colon": ":::",
    "double_asterisk": "**",
    "double_small_comma": "﹐﹐",
}

# CH-349 limb D: CH-311 and CH-270 joiner forms spaced
# by a Unicode space instead of a plain space.
_CH349_UNICODE_SPACED_MULTI_JOINERS = {
    "triple_backslash_enspace": " " + "\\" * 3 + " ",
    "double_hash_nbsp": " ## ",
    "double_greater_than_enspace": " >> ",
}

# CH-350 limb A: one ring past the CH-311 thirteen,
# spaced forms.
_CH350_RING_JOINERS = {
    "quadruple_backslash": " " + "\\" * 4 + " ",
    "quadruple_greater_than": " >>>> ",
    "quintuple_plus": " +++++ ",
    "triple_hash": " ### ",
    "triple_asterisk": " *** ",
    "triple_at": " @@@ ",
    "triple_percent": " %%% ",
    "quadruple_underscore": " ____ ",
    "quadruple_colon": " :::: ",
}

# CH-350 limb B: doubled punctuation forms outside every
# charged signal set, spaced forms.
_CH350_DOUBLED_JOINERS = {
    "double_hyphen": " -- ",
    "double_semicolon": " ;; ",
    "double_question": " ?? ",
    "double_tilde": " ~~ ",
    "double_exclamation": " !! ",
}

# CH-350 limb C: single joiners at an en space.
_CH350_SINGLE_JOINERS = {
    "dollar_enspace": " $ ",
    "hyphen_enspace": " - ",
}

# Pins: the cured CH-310 forms of fix wave 11.
_PIN_CH310_NOSPACE = {
    "double_pipe": "||",
    "double_ampersand": "&&",
    "ideographic_comma": "、",
    "double_backslash": "\\" * 2,
    "triple_plus": "+++",
    "double_colon": "::",
    "small_comma": "﹐",
}

_PIN_CH310_SEMICOLON_SPACES = {
    "em_quad": " ; ",
    "thin_space": " ; ",
    "math_space": " ; ",
}

_PIN_CH310_SPACED = {
    "hash_enspace": " # ",
    "percent_ideographic": "　%　",
    "double_plus_mathspace": " ++ ",
}

# Pins: the cured CH-311 forms of fix wave 11, spaced.
_PIN_CH311_SPACED = {
    "triple_backslash": " " + "\\" * 3 + " ",
    "triple_greater_than": " >>> ",
    "quadruple_plus": " ++++ ",
    "double_hash": " ## ",
    "double_dollar": " $$ ",
}

# Pins: the cured CH-269 forms of fix wave 10.
_PIN_CH269 = {
    "underscore_nospace": "_",
    "plus_enspace": " + ",
    "em_space_semicolon": " ; ",
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


def _assert_head_restored(case, joiner):
    text = _list_file(
        5, _joined_statement([1, 2, 3, 4], joiner), [1, 2, 3, 4])
    output = _run_text(text)
    _assert_list_stands_whole(case, output, ["DQ-002", "DQ-003"])


def _assert_signal_only(case, joiner):
    _assert_head_restored(case, joiner)


class Ch349FurtherSpaceSemicolonHeadTest(unittest.TestCase):
    """CH-349 limb A: the charged semicolon spaced by a
    space character past the twelve CH-310 names derives
    the head pointer, signal naming the middles only."""

    def test_further_space_semicolon_head_restored(self):
        for name, joiner in sorted(
                _CH349_SEMICOLON_SPACES.items()):
            with self.subTest(joiner=name):
                _assert_head_restored(self, joiner)

    def test_three_per_em_before_only_head_restored(self):
        _assert_head_restored(self, " ;")


class Ch349SpacedJoinerHeadTest(unittest.TestCase):
    """CH-349 limb B: a joiner past the CH-310 spaced
    joiner set at a charged Unicode spacing derives the
    head pointer, signal naming the middles only."""

    def test_further_spaced_joiner_head_restored(self):
        for name, joiner in sorted(
                _CH349_SPACED_JOINERS.items()):
            with self.subTest(joiner=name):
                _assert_head_restored(self, joiner)


class Ch349Ch311NoSpaceHeadTest(unittest.TestCase):
    """CH-349 limb C: a CH-311 joiner form at the no space
    spacing derives the head pointer, its signal standing
    and naming the middles only, no middle pointer
    deriving under the signal only ruling."""

    def test_ch311_nospace_head_restored(self):
        for name, joiner in sorted(
                _CH349_CH311_NOSPACE_JOINERS.items()):
            with self.subTest(joiner=name):
                _assert_head_restored(self, joiner)


class Ch349UnicodeSpacedMultiJoinerHeadTest(unittest.TestCase):
    """CH-349 limb D: a CH-311 or CH-270 joiner form
    spaced by a Unicode space derives the head pointer,
    signal naming the middles only."""

    def test_unicode_spaced_multi_joiner_head_restored(self):
        for name, joiner in sorted(
                _CH349_UNICODE_SPACED_MULTI_JOINERS.items()):
            with self.subTest(joiner=name):
                _assert_head_restored(self, joiner)


class Ch349PositionsTest(unittest.TestCase):
    """CH-349 limb A at a new position: the three per em
    spaced semicolon form with a ghost middle derives the
    head pointer, the ghost standing beside it."""

    def test_three_per_em_ghost_head_restored(self):
        text = _list_file(
            5, _joined_statement([1, 999, 3, 4], " ; "),
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


class Ch350RingJoinerSignalTest(unittest.TestCase):
    """CH-350 limb A: a target list joined by a quadrupled
    or quintupled CH-311 joiner, or a tripled doubled
    CH-183 joiner, takes the not recognised signal for
    its middles, signal only, end pointers standing."""

    def test_ring_joiner_lists_take_the_signal(self):
        for name, joiner in sorted(_CH350_RING_JOINERS.items()):
            with self.subTest(joiner=name):
                _assert_signal_only(self, joiner)


class Ch350DoubledPunctuationSignalTest(unittest.TestCase):
    """CH-350 limb B: a target list joined by a doubled
    punctuation form outside every charged signal set
    takes the signal for its middles, signal only."""

    def test_doubled_punctuation_lists_take_the_signal(self):
        for name, joiner in sorted(
                _CH350_DOUBLED_JOINERS.items()):
            with self.subTest(joiner=name):
                _assert_signal_only(self, joiner)


class Ch350SingleJoinerSignalTest(unittest.TestCase):
    """CH-350 limb C: a target list joined by a single
    dollar or hyphen at an en space takes the signal for
    the targets no pointer stands for, its head among
    them, signal only: the one end pointer stands and no
    further pointer derives."""

    def test_single_joiner_lists_take_the_signal(self):
        for name, joiner in sorted(
                _CH350_SINGLE_JOINERS.items()):
            with self.subTest(joiner=name):
                text = _list_file(
                    5, _joined_statement([1, 2, 3, 4], joiner),
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

    def test_single_dollar_enspace_eight_takes_the_signal(self):
        text = _list_file(
            9, _joined_statement(
                [1, 2, 3, 4, 5, 6, 7, 8], " $ "),
            [1, 2, 3, 4, 5, 6, 7, 8])
        output = _run_text(text)
        self.assertEqual(_pointers(output, "DQ-001"), [])
        self.assertEqual(_pointers(output, "DQ-008"), ["DQ-009"])
        for mid in ("DQ-002", "DQ-003", "DQ-004", "DQ-005",
                    "DQ-006", "DQ-007"):
            self.assertEqual(_pointers(output, mid), [])
        notes = _not_recognised_notes(output)
        self.assertEqual(len(notes), 1)
        self.assertEqual(
            _named_entries(notes[0]),
            ["DQ-001", "DQ-002", "DQ-003", "DQ-004",
             "DQ-005", "DQ-006", "DQ-007"])


class ClusterIPinsTest(unittest.TestCase):
    """The governing pins of this surface, passing before
    and after: the cured CH-269, CH-270, CH-310, and
    CH-311 forms whole, the signal only ruling in its own
    terms (no middle pointer derives from any signal
    list), the caret pin at both spacings, and the colon
    no space bound."""

    def test_cured_ch269_forms_stand(self):
        for name, joiner in sorted(_PIN_CH269.items()):
            with self.subTest(joiner=name):
                _assert_signal_only(self, joiner)

    def test_cured_ch310_forms_stand(self):
        for group in (_PIN_CH310_NOSPACE,
                      _PIN_CH310_SEMICOLON_SPACES, _PIN_CH310_SPACED):
            for name, joiner in sorted(group.items()):
                with self.subTest(joiner=name):
                    _assert_signal_only(self, joiner)

    def test_cured_ch311_forms_stand(self):
        for name, joiner in sorted(_PIN_CH311_SPACED.items()):
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
