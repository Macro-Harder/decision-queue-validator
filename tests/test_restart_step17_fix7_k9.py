"""Step 17 fix wave 7, Fix Seat K9 tests, test first.

Charge CH-145, as ruled at section 66 of
design/steps/step-17r-record.md, with express ruling (e)
of that section, and sourced at round 7 attack seat 9,
design/steps/step-17r-attack7-9.md, Finding 1 (Low).

CH-145 (validate, the joiner silence limb): a target list
joined by a joiner outside the CH-104 charged set, and a
list joined by a semicolon lookalike, derives pointers
for its end targets only, and its remaining targets are
dropped silently with no signal of any class. The eight
charged forms of this seat: the plus, backslash, greater
than, colon, equals, and tilde joiners, and the two
semicolon lookalikes, the Greek question mark U+037E and
the small semicolon U+FE54.

Ruling (e) bounds this charge: it is charged on the
silence only, in the CH-104 form of ruling (h) of record
section 58. The cure is signal only: the near miss
signal extends to the eight forms above, on the same
condition limb as every CH-104 signal (the signal stands
only for a target for which no pointer stands in the
same run from the same entry, in either statement
order), and no pointer derives from any list this
charge names. Derivation from the charged joiner lists
is not charged, the CH-64 joiner set (commas, the word
and, or both) stands unmoved, and no pointer derives
from a list the charge does not name.

The colon form stands in its attack paper posture: its
colon stands inside the clause punctuation the end
readings read by, so the head target of a colon list
takes no pointer either, and the silence this charge
cures covers every target of the list that no pointer
stands for, the lost head among them. No derivation is
charged for it: after the cure the colon list still
derives the one pointer it derived before, and the
signal names the rest.

Constructions stand in the attack paper shape: one
claiming entry, DQ-005, headed targets DQ-001 to
DQ-004, the list standing in both clauses of the
statement, each entry carrying Status: Ruled, so no
construction in this file is of the F1 shape.

Copyright: J.P. Picard aka Macro-Harder
"""

import unittest

import dqv_harness as h

_HEADER = "# Decision Queue\n\n## Open items\n\n"

_JOINERS = {
    "plus": " + ",
    "backslash": " \\ ",
    "gt": " > ",
    "equals": " = ",
    "tilde": " ~ ",
    "greek_question": "; ",
    "small_semicolon": "﹔ ",
}

_COLON_JOINER = ": "


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


def _list_file(claiming_number, statement, headed, extra=None,
               second_claiming=None, second_statement=None):
    total = max([claiming_number] + list(headed)
                + ([second_claiming] if second_claiming else []))
    parts = [_HEADER]
    for i in range(1, total + 1):
        if i == claiming_number:
            entry = _ruled_entry(i, statement)
            if extra is not None:
                entry += extra + "\n\n"
            parts.append(entry)
        elif second_claiming is not None and i == second_claiming:
            parts.append(_ruled_entry(i, second_statement))
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


class Ch145JoinerSilenceTest(unittest.TestCase):
    """CH-145: a target list joined by one of the eight
    forms this charge names takes the near miss signal for
    every target no pointer stands for, by signal only.
    No pointer derives from any list this charge names."""

    def test_new_joiner_lists_take_the_signal(self):
        for name, joiner in sorted(_JOINERS.items()):
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

    def test_colon_list_signals_every_unread_target(self):
        # The colon form loses its head end reading as well
        # (attack seat 9, Finding 1): only the tail pointer
        # stands, and the signal names the head with the
        # middles. No pointer is derived by the cure.
        text = _list_file(
            5, _joined_statement([1, 2, 3, 4], _COLON_JOINER),
            [1, 2, 3, 4])
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

    def test_new_joiner_ghost_middle_takes_pd_r7(self):
        for name in ("plus", "greek_question"):
            with self.subTest(joiner=name):
                text = _list_file(
                    5,
                    _joined_statement(
                        [1, 999, 2, 3], _JOINERS[name]),
                    [1, 2, 3])
                output = _run_text(text)
                self.assertEqual(
                    _pointers(output, "DQ-001"), ["DQ-005"])
                self.assertEqual(
                    _pointers(output, "DQ-003"), ["DQ-005"])
                self.assertEqual(_pointers(output, "DQ-002"), [])
                self.assertEqual(len(_pd_r7_notes(output)), 1)
                notes = _not_recognised_notes(output)
                self.assertEqual(len(notes), 1)
                self.assertEqual(
                    _named_entries(notes[0]), ["DQ-002"])

    def test_new_joiner_signal_obeys_the_condition_limb(self):
        # The condition limb of ruling (h) governs the new
        # signals too: where the same entry derives one
        # middle by a comma statement, the signal names
        # only the middle no pointer stands for.
        text = _list_file(
            5, _joined_statement([1, 2, 3, 4], _JOINERS["plus"]),
            [1, 2, 3, 4], extra=_comma_statement([3]))
        output = _run_text(text)
        self.assertEqual(_pointers(output, "DQ-003"), ["DQ-005"])
        self.assertEqual(_pointers(output, "DQ-002"), [])
        notes = _not_recognised_notes(output)
        self.assertEqual(len(notes), 1)
        self.assertEqual(_named_entries(notes[0]), ["DQ-002"])

    def test_new_joiner_signal_held_where_comma_derives(self):
        # In either statement order, where the same entry
        # derives both middles by a comma statement, no
        # signal stands for them.
        for first in ("joiner", "comma"):
            with self.subTest(first=first):
                if first == "joiner":
                    text = _list_file(
                        5,
                        _joined_statement(
                            [1, 2, 3, 4], _JOINERS["tilde"]),
                        [1, 2, 3, 4],
                        extra=_comma_statement([2, 3]))
                else:
                    text = _list_file(
                        5, _comma_statement([2, 3]),
                        [1, 2, 3, 4],
                        extra=_joined_statement(
                            [1, 2, 3, 4], _JOINERS["tilde"]))
                output = _run_text(text)
                for target in (1, 2, 3, 4):
                    self.assertEqual(
                        _pointers(output, "DQ-%03d" % target),
                        ["DQ-005"])
                self.assertEqual(_not_recognised_notes(output), [])
                self.assertEqual(_pd_r7_notes(output), [])

    def test_signal_not_suppressed_by_another_entrys_pointer(self):
        # The condition reads on pointers from the same
        # entry: a pointer another entry derives for a
        # middle target does not answer this entry
        # statement, and this entry signal stands.
        text = _list_file(
            5, _joined_statement([1, 2, 3, 4], _JOINERS["plus"]),
            [1, 2, 3, 4],
            second_claiming=6,
            second_statement=_comma_statement([2, 3]))
        output = _run_text(text)
        self.assertEqual(_pointers(output, "DQ-002"), ["DQ-006"])
        self.assertEqual(_pointers(output, "DQ-003"), ["DQ-006"])
        notes = _not_recognised_notes(output)
        self.assertEqual(len(notes), 1)
        self.assertEqual(
            _named_entries(notes[0]), ["DQ-002", "DQ-003"])

    def test_new_joiner_two_target_list_takes_no_signal(self):
        for name in ("plus", "tilde", "greek_question"):
            with self.subTest(joiner=name):
                text = _list_file(
                    5, _joined_statement([1, 2], _JOINERS[name]),
                    [1, 2])
                output = _run_text(text)
                self.assertEqual(
                    _pointers(output, "DQ-001"), ["DQ-005"])
                self.assertEqual(
                    _pointers(output, "DQ-002"), ["DQ-005"])
                self.assertEqual(_not_recognised_notes(output), [])
                self.assertEqual(_pd_r7_notes(output), [])

    def test_colon_two_target_list_signals_the_lost_head(self):
        # A two target colon list loses its head end
        # reading on the same posture as the four target
        # form, so the head takes the signal and the tail
        # keeps its pointer.
        text = _list_file(
            5, _joined_statement([1, 2], _COLON_JOINER), [1, 2])
        output = _run_text(text)
        self.assertEqual(_pointers(output, "DQ-001"), [])
        self.assertEqual(_pointers(output, "DQ-002"), ["DQ-005"])
        notes = _not_recognised_notes(output)
        self.assertEqual(len(notes), 1)
        self.assertEqual(_named_entries(notes[0]), ["DQ-001"])
        self.assertEqual(_pd_r7_notes(output), [])

    def test_new_joiner_self_middle_takes_no_signal(self):
        text = _list_file(
            5, _joined_statement([1, 5, 2, 3], _JOINERS["plus"]),
            [1, 2, 3])
        output = _run_text(text)
        self.assertEqual(_pointers(output, "DQ-001"), ["DQ-005"])
        self.assertEqual(_pointers(output, "DQ-003"), ["DQ-005"])
        self.assertEqual(_pointers(output, "DQ-002"), [])
        notes = _not_recognised_notes(output)
        self.assertEqual(len(notes), 1)
        self.assertEqual(_named_entries(notes[0]), ["DQ-002"])

    def test_new_joiner_duplicate_middle_named_once(self):
        text = _list_file(
            5,
            _joined_statement([1, 2, 2, 3], _JOINERS["tilde"]),
            [1, 2, 3])
        output = _run_text(text)
        self.assertEqual(_pointers(output, "DQ-001"), ["DQ-005"])
        self.assertEqual(_pointers(output, "DQ-003"), ["DQ-005"])
        self.assertEqual(_pointers(output, "DQ-002"), [])
        notes = _not_recognised_notes(output)
        self.assertEqual(len(notes), 1)
        self.assertEqual(_named_entries(notes[0]), ["DQ-002"])

    def test_new_joiner_single_clause_signals_unread(self):
        statement = (
            "This ruling displaces the rulings at "
            "DQ-001 + DQ-002 + DQ-003 in full; those earlier "
            "rulings no longer stand as governing on their "
            "subjects.")
        text = _list_file(5, statement, [1, 2, 3])
        output = _run_text(text)
        self.assertEqual(_pointers(output, "DQ-001"), ["DQ-005"])
        self.assertEqual(_pointers(output, "DQ-002"), [])
        self.assertEqual(_pointers(output, "DQ-003"), [])
        notes = _not_recognised_notes(output)
        self.assertEqual(len(notes), 1)
        self.assertEqual(
            _named_entries(notes[0]), ["DQ-002", "DQ-003"])


class Ch145PinsTest(unittest.TestCase):
    """The standing forms beside CH-145, pinned in both
    directions: the CH-93 and CH-104 signals stand whole,
    the CH-64 comma derivation stands unmoved, and a list
    joined by a joiner no charge names takes no signal
    and derives no pointer past its end readings."""

    def test_semicolon_and_charged_joiner_controls_stand(self):
        for joiner in ("; ", " / ", " | ", " & ", "； "):
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

    def test_uncharged_joiner_takes_no_signal(self):
        # The caret joiner stands named by no charge: its
        # list keeps its standing end readings and its
        # middles take no signal, on the bound of ruling
        # (e) that no pointer and no signal derives from a
        # list the charge does not name.
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
