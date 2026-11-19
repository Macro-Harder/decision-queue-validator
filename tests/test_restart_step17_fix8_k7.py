"""Step 17 fix wave 8, Fix Seat K7 tests, test first.

Charges CH-166 and CH-183, as ruled at section 77 of
design/steps/step-17r-record.md (ruling (f) for CH-183),
sourced at round 8 attack seat 9,
design/steps/step-17r-attack8-9.md, Findings 1 and 2.

CH-166 (Medium, Finding 1, the no space joiner limb):
a target list on a charged joiner form with no space on
either side of the joiner takes no signal of any class
and loses the head pointer its spaced form derives, and
two constructions verified standing in rounds 6 and 7
stand regressed: q08-semicolon-nospace (round 6, passed
at Q8 with one not recognised Note and pointers on the
head and tail) and r20-fullwidth-ghost-middle (round 7,
passed at R20 with PD-R7 for the ghost middle, one not
recognised Note naming DQ-003, and one pointer). The
charged joiner forms are the semicolon form of CH-93,
the four forms of CH-104 (slash, pipe, ampersand, and
fullwidth semicolon U+FF1B), and the forms of CH-145
(plus, backslash, greater than, equals, and tilde, and
the lookalikes Greek question mark U+037E and small
semicolon U+FE54). The colon form of CH-145 is the
bound of the finding, not a member: at the no space
spacing its signal stands whole on its plain token
reading and its head still derives no pointer, and
both postures stand pinned below.

CH-183 (Low, Finding 2, the uncharged joiner silence
limb): a target list joined by a joiner no charge
named, and a list joined by a further semicolon
lookalike in list position, derives pointers for its
end targets only, and its remaining targets are dropped
silently. Ruled TO FIX at section 77 ruling (f) as a
signal for the named joiner forms, no derivation
charged: the Arabic semicolon U+061B, the reversed
semicolon U+204F, the presentation form vertical
semicolon U+FE14, and the asterisk, at sign, hash,
percent, and double slash forms in list position. The
cure is signal only, in the CH-104 form: no pointer
derives from any list this charge names past the end
readings those lists already took.

Constructions stand in the attack paper shape: one
claiming entry carrying the statement in both clauses,
headed targets, each entry carrying Status: Ruled, so
no construction in this file is of the F1 shape.

Copyright: J.P. Picard aka Macro-Harder
"""

import unittest

import dqv_harness as h

_HEADER = "# Decision Queue\n\n## Open items\n\n"

_NOSPACE_JOINERS = {
    "semicolon": ";",
    "slash": "/",
    "pipe": "|",
    "ampersand": "&",
    "fullwidth_semicolon": "；",
    "plus": "+",
    "backslash": "\\",
    "gt": ">",
    "equals": "=",
    "tilde": "~",
    "greek_question": ";",
    "small_semicolon": "﹔",
}

_CH183_JOINERS = {
    "arabic_semicolon": " ؛ ",
    "reversed_semicolon": " ⁏ ",
    "vertical_semicolon": " \ufe14 ",
    "asterisk": " * ",
    "at_sign": " @ ",
    "hash": " # ",
    "percent": " % ",
    "double_slash": " // ",
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


def _and_join(names):
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + " and " + names[-1]


def _comma_statement(targets):
    names = ["DQ-%03d" % t for t in targets]
    joined = _and_join(names)
    if len(names) == 1:
        return (
            "This ruling displaces the ruling at %s in full; "
            "that earlier ruling no longer stands as governing "
            "on its subject, and %s is the superseded entry."
            % (joined, joined))
    return (
        "This ruling displaces the rulings at %s in full; "
        "those earlier rulings no longer stand as governing "
        "on their subjects, and %s are the superseded entries."
        % (joined, joined))


def _joined_statement(targets, joiner):
    names = joiner.join("DQ-%03d" % t for t in targets)
    return (
        "This ruling displaces the rulings at %s in full; "
        "those earlier rulings no longer stand as governing "
        "on their subjects, and %s are the superseded entries."
        % (names, names))


def _list_file(claiming_number, statement, headed, extra=None):
    total = max([claiming_number] + list(headed))
    parts = [_HEADER]
    for i in range(1, total + 1):
        if i == claiming_number:
            entry = _ruled_entry(i, statement)
            if extra is not None:
                entry += extra + "\n\n"
            parts.append(entry)
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


def _pd_r7_notes(output):
    return _by_rule(output, "PD-R7")


def _named_entries(finding):
    return [h.text_of(x) for x in h.as_list(
        h.get(finding, "named_entries", "named_entry_ids"))]


def _pointers(output, entry_id):
    entry = h.entry_by_id(output, entry_id)
    if entry is None:
        raise AssertionError("no entry " + entry_id)
    return [h.text_of(p) for p in h.as_list(
        h.get(entry, "supersession_pointers"))]


class Ch166NoSpaceJoinerTest(unittest.TestCase):
    """CH-166: a charged joiner list with no space on
    either side of the joiner stands whole, as its spaced
    form does: pointers on the head and tail, and the
    near miss signal naming every middle target no
    pointer stands for."""

    def test_nospace_joiner_lists_stand_whole(self):
        for name, joiner in sorted(_NOSPACE_JOINERS.items()):
            with self.subTest(joiner=name):
                text = _list_file(
                    5, _joined_statement([1, 2, 3, 4], joiner),
                    [1, 2, 3, 4])
                output = _run_text(text)
                self.assertEqual(
                    _pointers(output, "DQ-001"), ["DQ-005"])
                self.assertEqual(
                    _pointers(output, "DQ-004"), ["DQ-005"])
                self.assertEqual(_pointers(output, "DQ-002"), [])
                self.assertEqual(_pointers(output, "DQ-003"), [])
                notes = _not_recognised_notes(output)
                self.assertEqual(len(notes), 1)
                self.assertEqual(
                    _named_entries(notes[0]), ["DQ-002", "DQ-003"])
                self.assertEqual(_pd_r7_notes(output), [])

    def test_q08_semicolon_nospace_restored_by_name(self):
        # The round 6 construction q08-semicolon-nospace,
        # passed at Q8 in its round and verified standing
        # in round 7, regressed by the cure defect this
        # charge cures: restored expressly here.
        text = _list_file(
            5, _joined_statement([1, 2, 3, 4], ";"), [1, 2, 3, 4])
        output = _run_text(text)
        self.assertEqual(_pointers(output, "DQ-001"), ["DQ-005"])
        self.assertEqual(_pointers(output, "DQ-004"), ["DQ-005"])
        notes = _not_recognised_notes(output)
        self.assertEqual(len(notes), 1)
        self.assertEqual(
            _named_entries(notes[0]), ["DQ-002", "DQ-003"])
        self.assertEqual(_pd_r7_notes(output), [])

    def test_r20_fullwidth_ghost_middle_restored_by_name(self):
        # The round 7 construction
        # r20-fullwidth-ghost-middle, passed at R20 in its
        # round (PD-R7: 1 for DQ-999, PIN-10: 1 naming
        # DQ-003, one pointer), regressed on the same
        # defect: restored expressly here. The stating
        # entry is DQ-004, the tail target itself, so the
        # one pointer stands on the head, DQ-001.
        text = _list_file(
            4,
            _joined_statement([1, 999, 3, 4], "；"),
            [1, 3])
        output = _run_text(text)
        self.assertEqual(_pointers(output, "DQ-001"), ["DQ-004"])
        self.assertEqual(_pointers(output, "DQ-003"), [])
        self.assertEqual(len(_pd_r7_notes(output)), 1)
        notes = _not_recognised_notes(output)
        self.assertEqual(len(notes), 1)
        self.assertEqual(_named_entries(notes[0]), ["DQ-003"])

    def test_nospace_semicolon_ghost_middle_takes_pd_r7(self):
        # Attack round 8 case s38 on the same form.
        text = _list_file(
            5, _joined_statement([1, 999, 3, 4], ";"), [1, 3, 4])
        output = _run_text(text)
        self.assertEqual(_pointers(output, "DQ-001"), ["DQ-005"])
        self.assertEqual(_pointers(output, "DQ-004"), ["DQ-005"])
        self.assertEqual(_pointers(output, "DQ-003"), [])
        self.assertEqual(len(_pd_r7_notes(output)), 1)
        notes = _not_recognised_notes(output)
        self.assertEqual(len(notes), 1)
        self.assertEqual(_named_entries(notes[0]), ["DQ-003"])

    def test_nospace_signal_obeys_the_condition_limb(self):
        text = _list_file(
            5, _joined_statement([1, 2, 3, 4], "+"),
            [1, 2, 3, 4], extra=_comma_statement([3]))
        output = _run_text(text)
        self.assertEqual(_pointers(output, "DQ-001"), ["DQ-005"])
        self.assertEqual(_pointers(output, "DQ-003"), ["DQ-005"])
        self.assertEqual(_pointers(output, "DQ-002"), [])
        notes = _not_recognised_notes(output)
        self.assertEqual(len(notes), 1)
        self.assertEqual(_named_entries(notes[0]), ["DQ-002"])

    def test_nospace_two_target_list_takes_no_signal(self):
        text = _list_file(
            5, _joined_statement([1, 2], ";"), [1, 2])
        output = _run_text(text)
        self.assertEqual(_pointers(output, "DQ-001"), ["DQ-005"])
        self.assertEqual(_pointers(output, "DQ-002"), ["DQ-005"])
        self.assertEqual(_not_recognised_notes(output), [])
        self.assertEqual(_pd_r7_notes(output), [])


class Ch183UnchargedJoinerSignalTest(unittest.TestCase):
    """CH-183: a target list on one of the eight named
    joiner forms takes the near miss signal for its
    middle targets, signal only, with its standing end
    pointers unmoved and no middle pointer derived."""

    def test_named_joiner_lists_take_the_signal(self):
        for name, joiner in sorted(_CH183_JOINERS.items()):
            with self.subTest(joiner=name):
                text = _list_file(
                    5, _joined_statement([1, 2, 3, 4], joiner),
                    [1, 2, 3, 4])
                output = _run_text(text)
                self.assertEqual(
                    _pointers(output, "DQ-001"), ["DQ-005"])
                self.assertEqual(
                    _pointers(output, "DQ-004"), ["DQ-005"])
                self.assertEqual(_pointers(output, "DQ-002"), [])
                self.assertEqual(_pointers(output, "DQ-003"), [])
                notes = _not_recognised_notes(output)
                self.assertEqual(len(notes), 1)
                self.assertEqual(
                    _named_entries(notes[0]), ["DQ-002", "DQ-003"])
                self.assertEqual(_pd_r7_notes(output), [])

    def test_named_joiner_ghost_middle_takes_pd_r7(self):
        text = _list_file(
            5,
            _joined_statement(
                [1, 999, 3, 4], _CH183_JOINERS["arabic_semicolon"]),
            [1, 3, 4])
        output = _run_text(text)
        self.assertEqual(_pointers(output, "DQ-001"), ["DQ-005"])
        self.assertEqual(_pointers(output, "DQ-004"), ["DQ-005"])
        self.assertEqual(_pointers(output, "DQ-003"), [])
        self.assertEqual(len(_pd_r7_notes(output)), 1)
        notes = _not_recognised_notes(output)
        self.assertEqual(len(notes), 1)
        self.assertEqual(_named_entries(notes[0]), ["DQ-003"])

    def test_named_joiner_signal_obeys_the_condition_limb(self):
        text = _list_file(
            5,
            _joined_statement(
                [1, 2, 3, 4], _CH183_JOINERS["asterisk"]),
            [1, 2, 3, 4], extra=_comma_statement([3]))
        output = _run_text(text)
        self.assertEqual(_pointers(output, "DQ-003"), ["DQ-005"])
        self.assertEqual(_pointers(output, "DQ-002"), [])
        notes = _not_recognised_notes(output)
        self.assertEqual(len(notes), 1)
        self.assertEqual(_named_entries(notes[0]), ["DQ-002"])


class Ch166Ch183PinsTest(unittest.TestCase):
    """The governing pins of this surface, held in both
    directions: the colon bound of Finding 1, the spaced
    CH-93, CH-104, and CH-145 forms whole, the CH-64
    comma derivation unmoved, and a joiner no charge
    names still taking no signal."""

    def test_colon_nospace_bound_stands(self):
        # Attack round 8 case s35: the colon limb reads
        # its list on the plain token form, so at the no
        # space spacing its signal stands whole and its
        # head still derives no pointer.
        text = _list_file(
            5, _joined_statement([1, 2, 3, 4], ":"), [1, 2, 3, 4])
        output = _run_text(text)
        self.assertEqual(_pointers(output, "DQ-001"), [])
        self.assertEqual(_pointers(output, "DQ-002"), [])
        self.assertEqual(_pointers(output, "DQ-003"), [])
        self.assertEqual(_pointers(output, "DQ-004"), ["DQ-005"])
        notes = _not_recognised_notes(output)
        self.assertEqual(len(notes), 1)
        self.assertEqual(
            _named_entries(notes[0]),
            ["DQ-001", "DQ-002", "DQ-003"])
        self.assertEqual(_pd_r7_notes(output), [])

    def test_spaced_charged_forms_stand_whole(self):
        for joiner in ("; ", " / ", " & ", "； ", " + ", " ~ "):
            with self.subTest(joiner=repr(joiner)):
                text = _list_file(
                    5, _joined_statement([1, 2, 3, 4], joiner),
                    [1, 2, 3, 4])
                output = _run_text(text)
                self.assertEqual(
                    _pointers(output, "DQ-001"), ["DQ-005"])
                self.assertEqual(
                    _pointers(output, "DQ-004"), ["DQ-005"])
                self.assertEqual(_pointers(output, "DQ-002"), [])
                self.assertEqual(_pointers(output, "DQ-003"), [])
                notes = _not_recognised_notes(output)
                self.assertEqual(len(notes), 1)
                self.assertEqual(
                    _named_entries(notes[0]), ["DQ-002", "DQ-003"])
                self.assertEqual(_pd_r7_notes(output), [])

    def test_comma_list_derives_whole_and_takes_no_signal(self):
        text = _list_file(
            5, _comma_statement([1, 2, 3, 4]), [1, 2, 3, 4])
        output = _run_text(text)
        for target in (1, 2, 3, 4):
            self.assertEqual(
                _pointers(output, "DQ-%03d" % target), ["DQ-005"])
        self.assertEqual(_not_recognised_notes(output), [])
        self.assertEqual(_pd_r7_notes(output), [])

    def test_uncharged_caret_joiner_takes_no_signal(self):
        text = _list_file(
            5, _joined_statement([1, 2, 3, 4], " ^ "),
            [1, 2, 3, 4])
        output = _run_text(text)
        self.assertEqual(_pointers(output, "DQ-001"), ["DQ-005"])
        self.assertEqual(_pointers(output, "DQ-004"), ["DQ-005"])
        self.assertEqual(_pointers(output, "DQ-002"), [])
        self.assertEqual(_pointers(output, "DQ-003"), [])
        self.assertEqual(_not_recognised_notes(output), [])
        self.assertEqual(_pd_r7_notes(output), [])


if __name__ == "__main__":
    unittest.main()
