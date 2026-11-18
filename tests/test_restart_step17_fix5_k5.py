"""Restart Step 17 fix wave 5, Fix Seat K5 tests.

Charges CH-82, CH-83, CH-84, CH-90, and CH-94, ruled at
section 52 of design/steps/step-17r-record.md, rulings (a),
(f), and (k), and prepared at
design/steps/step-17r-triage5-prep.md.

CH-82 (validate and parse, the citation continuation guard
classes and the scans standing outside the guard): seat 4
findings F-1 (the CH-73 guard standing as a category list,
tokens continuing in Co, Nl, No, Cc, and Zs read in part and
manufacturing identifiers, with visible letter, symbol, and
connector punctuation inside forms beside them) and F-2 (the
fallback segment claim scan and the parse bullet claim
standing outside the guard, manufacturing claims from tokens
interrupted by characters inside the guard own classes, and
a validate supersession line scan beside them). The ruled
ground: the guard reads the no visible glyph ground of
ruling (a) together with its standing digit and colon
ground, and the outside scans take the same guard.

CH-83 (validate, the ghost, claim, and evidence scan
widths): seat 7 findings S17-ATK5-7-01 (a ghost number on
the entry own Status line in the remains and stays forms),
S17-ATK5-7-02 (a ghost number on the Status line in past
tense verb first forms), S17-ATK5-7-03 (decision evidence
naming a headed entry with the verb first Ruled and Decided
forms), S17-ATK5-7-05 (cross entry claims in the remains
decided and stays decided forms), and the heading dressed
Status occurrence limb of S17-ATK5-7-06 as its sixth limb.

CH-84 (validate, closing prose derivation crossings, under
ruling (f)): seat 7 finding S17-ATK5-7-04, the decided verb
beside shut and the verdict noun beside sealed, named
crossings only. The two K7 bound guards (the decision noun
beside sealed, the verdict noun beside shut) stand pinned
deriving Open in both directions.

CH-90 (validate, the plain citation suppression keying in
check 8): seat 15 finding F-15-5-1, the suppression reading
its derived state through a display identifier keyed map,
last copy wins, where the governed rule is per entry.

CH-94 (validate, under ruling (k)): the field conflict
reading does not count a field echo standing in the render
append form as a repeated field, seat 20 observation
O-5-20-2, disposition item D-5-1. The CH-59 and CH-72
stated bounds stand: effectively open entries, exact string
comparison, decision block lines skipped.

Constructions are the finding papers own constructions,
rebuilt inline from the attack scratch files. Governing
pins stand as controls in this file: the CH-73 pins whole,
the CH-60 and CH-62 pins and bound guards, the CH-59 and
CH-72 pins, and the terminator bound at record section 26
flag (f).
"""

import unittest

import dqv_harness as h

validate = h.import_module("validate")

PUA = "\ue000"
ROMAN = "\u216b"
SUPER2 = "\u00b2"
FRAC = "\u00bd"
NEL = "\u0085"
NBSP = "\u00a0"
ALPHA = "\u03b1"
COPY = "\u00a9"
TIE = "\u203f"
ALM = "\u061c"
ACUTE = "\u0301"
ZWSP = "\u200b"


def _run(data, name):
    _model, output = h.run_pipeline(data.encode("utf-8"), name)
    if output is None:
        raise AssertionError("pipeline returned a failure for " + name)
    return output


def _statements(output):
    return [h.finding_statement(f) or ""
            for f in h.findings_of(output)]


def _pd_r7(output, number):
    return [f for f in h.findings_of(output)
            if (h.finding_statement(f) or "").startswith(
                "DQ-%03d is cited, but" % number)]


def _claims_about(output, number):
    return [s for s in _statements(output)
            if "records a claim" in s
            and "DQ-%03d" % number in s]


def _state_of(output, identifier):
    entry = h.entry_by_id(output, identifier)
    if entry is None:
        raise AssertionError("no entry %s in output" % identifier)
    return h.entry_state(entry)


def _banked_entry(number, title, extra=""):
    return (
        "### DQ-%03d: %s\n"
        "\n"
        "Status: Banked\n"
        "\n"
        "Question: Which option should we take?\n"
        "\n"
        "Options: Option A, Option B\n"
        "\n"
        "Cost of deciding late: Work stays blocked.\n"
        "\n"
        "Blocks: DQ-002\n"
        "\n"
        "This question is waiting for a decision.\n"
        "%s" % (number, title, extra))


def _segment_queue(hostile_line):
    """The seat 4 j case skeleton: one headed entry, then a
    heading whose number carries a zero width space, so its
    lines stand in a quarantined segment, then the hostile
    line standing in that segment body."""
    body = (
        "Status: Banked\n"
        "\n"
        "Question: Which option should we take?\n"
        "\n"
        "Options: Option A, Option B\n"
        "\n"
        "Cost of deciding late: Work stays blocked.\n"
        "\n"
        "Blocks: DQ-999\n"
        "\n"
        "A plain paragraph of context for this entry.\n")
    return (
        "# Decision queue\n"
        "\n"
        "### DQ-002: A sample open question\n"
        "\n"
        + body +
        "\n"
        "### DQ-00" + ZWSP + "1: A sample open question\n"
        "\n"
        + body +
        "\n"
        + hostile_line + "\n")


class Ch82GuardClassesTest(unittest.TestCase):
    """CH-82 limb 1: the guard classes, seat 4 F-1."""

    def test_framed_inside_forms_manufacture_nothing(self):
        chars = {
            "private use": PUA, "letter number": ROMAN,
            "other number square": SUPER2,
            "other number fraction": FRAC, "control": NEL,
            "space separator": NBSP, "visible letter": ALPHA,
            "visible symbol": COPY,
            "connector punctuation": TIE,
        }
        for name, char in chars.items():
            with self.subTest(form=name):
                output = _run(_segment_queue(
                    "See the note at DQ-88" + char
                    + "8 for context."), "j01-inside")
                self.assertEqual([], _pd_r7(output, 88))
                self.assertEqual(
                    [], [s for s in _statements(output)
                         if "DQ-088" in s])

    def test_framed_trailing_forms_manufacture_nothing(self):
        chars = {
            "private use": PUA, "letter number": ROMAN,
            "other number square": SUPER2,
            "other number fraction": FRAC, "control": NEL,
            "space separator": NBSP,
        }
        for name, char in chars.items():
            with self.subTest(form=name):
                output = _run(_segment_queue(
                    "See the note at DQ-888" + char
                    + " for context."), "j02-trailing")
                self.assertEqual([], _pd_r7(output, 888))
                self.assertEqual(
                    [], [s for s in _statements(output)
                         if "DQ-888" in s])

    def test_entry_plain_pua_inside_manufactures_nothing(self):
        data = ("# Decision queue\n\n" + _banked_entry(
            1, "A sample open question",
            "\nThe token DQ-88" + PUA + "8 stands as context.\n"))
        output = _run(data, "j03-entry-plain")
        self.assertEqual([], _pd_r7(output, 88))

    def test_blocks_pua_inside_manufactures_nothing(self):
        data = ("# Decision queue\n\n"
                "### DQ-001: A sample open question\n"
                "\n"
                "Status: Banked\n"
                "\n"
                "Question: Which option should we take?\n"
                "\n"
                "Options: Option A, Option B\n"
                "\n"
                "Cost of deciding late: Work stays blocked.\n"
                "\n"
                "Blocks: DQ-00" + PUA + "2\n"
                "\n"
                "A plain paragraph of context for this entry.\n")
        output = _run(data, "j03-blocks")
        self.assertEqual([], _pd_r7(output, 0))
        self.assertEqual(
            [], [s for s in _statements(output) if "DQ-000" in s])

    def test_heading_title_pua_inside_manufactures_nothing(self):
        data = ("# Decision queue\n\n" + _banked_entry(
            5, "A title naming DQ-88" + PUA + "8 in passing"))
        output = _run(data, "j11-heading-title")
        self.assertEqual([], _pd_r7(output, 88))

    def test_supersession_enum_pua_inside_manufactures_nothing(self):
        data = ("# Decision queue\n\n" + _banked_entry(
            1, "A sample open question",
            "\nThis ruling supersedes DQ-777, DQ-88" + PUA
            + "8, and DQ-999.\n"))
        output = _run(data, "j08-super-enum")
        self.assertEqual([], _pd_r7(output, 88))
        self.assertEqual(1, len(_pd_r7(output, 777)))

    def test_named_class_inside_still_refused_pin(self):
        output = _run(_segment_queue(
            "See the note at DQ-88" + ALM + "8 for context."),
            "j01-alm-pin")
        self.assertEqual([], _pd_r7(output, 88))

    def test_clean_framed_token_still_reports_pin(self):
        output = _run(_segment_queue(
            "See the note at DQ-888 for context."), "j09-clean")
        self.assertEqual(1, len(_pd_r7(output, 888)))

    def test_full_stop_terminated_token_still_reports_pin(self):
        output = _run(_segment_queue(
            "See the note at DQ-888."), "terminator-pin")
        self.assertEqual(1, len(_pd_r7(output, 888)))

    def test_blocks_full_stop_token_still_reports_pin(self):
        data = ("# Decision queue\n\n"
                "### DQ-001: A sample open question\n"
                "\n"
                "Status: Banked\n"
                "\n"
                "Question: Which option should we take?\n"
                "\n"
                "Options: Option A, Option B\n"
                "\n"
                "Cost of deciding late: Work stays blocked.\n"
                "\n"
                "Blocks: DQ-00.2\n"
                "\n"
                "A plain paragraph of context for this entry.\n")
        output = _run(data, "h34c-pin")
        named = [s for s in _statements(output) if "DQ-000" in s]
        self.assertTrue(named)


class Ch82OutsideScansTest(unittest.TestCase):
    """CH-82 limb 2: the scans outside the guard, seat 4 F-2."""

    def test_segment_claim_inside_forms_manufacture_nothing(self):
        chars = {"arabic letter mark": ALM,
                 "combining acute": ACUTE, "private use": PUA}
        for name, char in chars.items():
            with self.subTest(form=name):
                output = _run(_segment_queue(
                    "DQ-88" + char + "8 was ruled and closed."),
                    "j04-segclaim-inside")
                self.assertEqual([], _claims_about(output, 88))

    def test_segment_claim_trailing_forms_manufacture_nothing(self):
        chars = {"arabic letter mark": ALM,
                 "combining acute": ACUTE}
        for name, char in chars.items():
            with self.subTest(form=name):
                output = _run(_segment_queue(
                    "DQ-888" + char + " was ruled and closed."),
                    "j05-segclaim-trailing")
                self.assertEqual([], _claims_about(output, 888))

    def test_segment_claim_headed_form_manufactures_nothing(self):
        output = _run(_segment_queue(
            "DQ-002" + ALM + " was ruled and closed."),
            "j06-segclaim-headed")
        self.assertEqual([], _claims_about(output, 2))

    def test_bullet_claim_trailing_forms_manufacture_nothing(self):
        chars = {"arabic letter mark": ALM, "private use": PUA}
        for name, char in chars.items():
            with self.subTest(form=name):
                output = _run(_segment_queue(
                    "- DQ-888" + char + " was ruled and closed."),
                    "j09-bullet-trailing")
                self.assertEqual([], _claims_about(output, 888))

    def test_supersession_line_alm_inside_manufactures_nothing(self):
        data = ("# Decision queue\n\n" + _banked_entry(
            1, "A sample open question",
            "\nThis ruling supersedes DQ-88" + ALM
            + "8 and DQ-777.\n"))
        output = _run(data, "j07-super")
        self.assertEqual([], _pd_r7(output, 88))
        self.assertEqual(1, len(_pd_r7(output, 777)))

    def test_clean_bullet_claim_still_stands_pin(self):
        output = _run(_segment_queue(
            "- DQ-888 was ruled and closed."), "j09-clean-bullet")
        self.assertEqual(1, len(_claims_about(output, 888)))

    def test_roman_segment_claim_takes_no_claim_pin(self):
        output = _run(_segment_queue(
            "DQ-88" + ROMAN + "8 was ruled and closed."),
            "j04-roman-pin")
        self.assertEqual([], _claims_about(output, 88))


def _ghost_status_entry(number, status_value):
    return (
        "# Decision queue\n"
        "\n"
        "### DQ-%03d: Ghost status probe\n"
        "\n"
        "Status: RULED, closed. %s\n"
        "\n"
        "Ruled by: Captain JP\n"
        "\n"
        "Ruling text: \"Settle DQ-%03d as follows.\"\n"
        "\n"
        "Ruling outcome: DQ-%03d is decided and closed.\n"
        "\n"
        "Where the ruling landed: NOWHERE.md, sample rule.\n"
        % (number, status_value, number, number))


class Ch83GhostStatusTest(unittest.TestCase):
    """CH-83 ghost limbs: S17-ATK5-7-01 and 02."""

    def test_status_remains_closed_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            502, "DQ-999 remains closed."), "g01")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_stays_closed_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            503, "DQ-999 stays closed."), "g02")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_ruled_verb_first_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            504, "Ruled DQ-999 in full."), "g03")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_decided_verb_first_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            505, "Decided DQ-999 in full."), "g04")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_settled_verb_first_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            506, "Settled DQ-999 in full."), "g05")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_stands_closed_still_takes_ghost_note_pin(self):
        output = _run(_ghost_status_entry(
            507, "DQ-999 stands closed."), "g06")
        self.assertEqual(1, len(_pd_r7(output, 999)))


def _evidence_entry(number, ruling_text, target_number):
    return (
        "# Decision queue\n"
        "\n"
        "### DQ-%03d: Evidence claim probe\n"
        "\n"
        "Status: RULED, closed\n"
        "\n"
        "Ruled by: Captain JP\n"
        "\n"
        "Ruling text: \"%s\"\n"
        "\n"
        "Ruling outcome: Recorded in full.\n"
        "\n"
        "Where the ruling landed: NOWHERE.md, sample rule.\n"
        "\n"
        % (number, ruling_text)
        + _banked_entry(target_number, "An ordinary banked entry"))


class Ch83EvidenceVerbFirstTest(unittest.TestCase):
    """CH-83 evidence limb: S17-ATK5-7-03."""

    def test_evidence_ruled_verb_first_takes_claim_note(self):
        output = _run(_evidence_entry(
            522, "Ruled DQ-523 in full.", 523), "e01")
        self.assertEqual(1, len(_claims_about(output, 523)))

    def test_evidence_decided_verb_first_takes_claim_note(self):
        output = _run(_evidence_entry(
            524, "Decided DQ-525 as follows.", 525), "e02")
        self.assertEqual(1, len(_claims_about(output, 525)))

    def test_evidence_closed_verb_first_still_takes_note_pin(self):
        output = _run(_evidence_entry(
            526, "Closed DQ-527 in full.", 527), "e03")
        self.assertEqual(1, len(_claims_about(output, 527)))


def _claim_file(number, claim_sentence, target_number):
    host = (
        "### DQ-%03d: Claim probe\n"
        "\n"
        "Status: Banked\n"
        "\n"
        "Question: Which option should we take?\n"
        "\n"
        "Options: Option A, Option B\n"
        "\n"
        "Cost of deciding late: Work stays blocked.\n"
        "\n"
        "Blocks: DQ-002\n"
        "\n"
        "This question is waiting for a decision. %s\n"
        % (number, claim_sentence))
    return ("# Decision queue\n\n" + host + "\n"
            + _banked_entry(target_number,
                            "An ordinary banked entry"))


class Ch83ClaimPredicateTest(unittest.TestCase):
    """CH-83 claim limb: S17-ATK5-7-05."""

    def test_claim_remains_decided_takes_note(self):
        output = _run(_claim_file(
            512, "DQ-513 remains decided.", 513), "c01")
        self.assertEqual(1, len(_claims_about(output, 513)))

    def test_claim_stays_decided_takes_note(self):
        output = _run(_claim_file(
            514, "DQ-515 stays decided.", 515), "c02")
        self.assertEqual(1, len(_claims_about(output, 515)))

    def test_claim_remains_closed_still_takes_note_pin(self):
        output = _run(_claim_file(
            516, "DQ-517 remains closed.", 517), "c03")
        self.assertEqual(1, len(_claims_about(output, 517)))


class Ch83HeadingDressedStatusTest(unittest.TestCase):
    """CH-83 sixth limb: S17-ATK5-7-06, on its own locus."""

    def test_heading_dressed_status_line_takes_a_signal(self):
        data = ("# Decision queue\n\n" + _banked_entry(
            542, "Banked head, heading status probe",
            "\n#### Status: RULED, closed\n"))
        output = _run(data, "s01")
        hits = [f for f in h.findings_of(output)
                if h.span_of(f)[0] == 17
                and "Status" in (h.finding_evidence_text(f)
                                 + (h.finding_statement(f) or ""))]
        self.assertEqual(1, len(hits))

    def test_plain_level4_heading_takes_no_such_signal_pin(self):
        data = ("# Decision queue\n\n" + _banked_entry(
            543, "Banked head, heading probe",
            "\n#### Notes on the ruling\n"))
        output = _run(data, "s01-pin")
        hits = [f for f in h.findings_of(output)
                if "standing as a heading" in
                (h.finding_statement(f) or "")]
        self.assertEqual([], hits)


def _prose_file(number, closing_sentence):
    return (
        "# Decision queue\n"
        "\n"
        "### DQ-%03d: Banked head, prose probe\n"
        "\n"
        "Status: Banked\n"
        "\n"
        "Question: Which option should we take?\n"
        "\n"
        "Options: Option A, Option B\n"
        "\n"
        "Cost of deciding late: Work stays blocked.\n"
        "\n"
        "Blocks: DQ-002\n"
        "\n"
        "This question is waiting for a decision.\n"
        "\n"
        "%s Nothing remains open on it.\n"
        % (number, closing_sentence))


class Ch84ClosingProseCrossingsTest(unittest.TestCase):
    """CH-84: S17-ATK5-7-04, named crossings only."""

    def test_decided_verb_beside_shut_derives_ambiguous(self):
        output = _run(_prose_file(
            532, "This entry was ruled by Captain JP yesterday "
                 "and is now shut."), "p01")
        self.assertEqual("Ambiguous", _state_of(output, "DQ-532"))

    def test_verdict_noun_beside_sealed_derives_ambiguous(self):
        output = _run(_prose_file(
            533, "The verdict is final and this entry is now "
                 "sealed."), "p02")
        self.assertEqual("Ambiguous", _state_of(output, "DQ-533"))

    def test_decision_closed_still_derives_ambiguous_pin(self):
        output = _run(_prose_file(
            534, "The decision was recorded yesterday and this "
                 "entry is now closed."), "p03")
        self.assertEqual("Ambiguous", _state_of(output, "DQ-534"))

    def test_decision_noun_beside_sealed_still_open_guard(self):
        output = _run(_prose_file(
            535, "The decision is final and this entry is now "
                 "sealed."), "guard-decision-sealed")
        self.assertEqual("Open", _state_of(output, "DQ-535"))

    def test_verdict_noun_beside_shut_still_open_guard(self):
        output = _run(_prose_file(
            536, "The verdict is final and this entry is now "
                 "shut."), "guard-verdict-shut")
        self.assertEqual("Open", _state_of(output, "DQ-536"))


_RULed_ENTRY_001 = (
    "### DQ-001: Ruled question DQ-001\n"
    "\n"
    "Status: Ruled\n"
    "\n"
    "Ruled by: Captain JP, 2026-11-17\n"
    "\n"
    "Ruling text: DQ-999 is decided.\n"
    "\n"
    "Ruling: Option A stands.\n"
    "\n"
    "Outcome: The option is settled.\n"
    "\n"
    "Landed: Recorded in the queue.\n")


def _open_entry(number):
    return (
        "### DQ-%03d: Question DQ-%03d\n"
        "\n"
        "Status: Banked\n"
        "\n"
        "Question: Which option should we take for DQ-%03d?\n"
        "\n"
        "Options: Option A, Option B\n"
        "\n"
        "Cost of deciding late: Work stays blocked while this "
        "waits.\n"
        "\n"
        "Blocks: nothing named\n"
        "\n"
        "DQ-999 is decided.\n" % (number, number, number))


class Ch90SuppressionKeyingTest(unittest.TestCase):
    """CH-90: F-15-5-1, per entry suppression and dedup."""

    def test_ruled_first_open_second_reports_each_citation(self):
        data = ("# Decision queue\n\n" + _RULed_ENTRY_001 + "\n"
                + _open_entry(1))
        output = _run(data, "s03")
        notes = _pd_r7(output, 999)
        self.assertEqual([9, 29], sorted(
            h.span_of(f)[0] for f in notes))

    def test_open_first_ruled_second_reports_each_citation(self):
        data = ("# Decision queue\n\n" + _open_entry(1) + "\n"
                + _RULed_ENTRY_001)
        output = _run(data, "s04")
        notes = _pd_r7(output, 999)
        self.assertEqual([15, 23], sorted(
            h.span_of(f)[0] for f in notes))

    def test_distinct_identifiers_still_report_each_pin(self):
        data = ("# Decision queue\n\n" + _RULed_ENTRY_001 + "\n"
                + _open_entry(2))
        output = _run(data, "s05")
        notes = _pd_r7(output, 999)
        self.assertEqual([9, 29], sorted(
            h.span_of(f)[0] for f in notes))

    def test_ruled_alone_reports_once_pin(self):
        data = "# Decision queue\n\n" + _RULed_ENTRY_001
        output = _run(data, "s01")
        notes = _pd_r7(output, 999)
        self.assertEqual([9], [h.span_of(f)[0] for f in notes])

    def test_open_alone_reports_once_pin(self):
        data = "# Decision queue\n\n" + _open_entry(1)
        output = _run(data, "s02")
        notes = _pd_r7(output, 999)
        self.assertEqual([15], [h.span_of(f)[0] for f in notes])


def _conflict_statements(output):
    return [s for s in _statements(output)
            if "two contradictory values" in s]


class Ch94RenderEchoTest(unittest.TestCase):
    """CH-94: D-5-1, the rendered echo exclusion."""

    def test_render_append_echo_takes_no_field_conflict(self):
        base = (
            "# Decision queue\n"
            "\n"
            "### DQ-001: A sample open question\n"
            "\n"
            "Status: Banked\n"
            "\n"
            "Question: Which option should we take?\n"
            "\n"
            "Options: Option A, Option B\n"
            "\n"
            "Cost of deciding late: Work stays blocked.\n"
            "\n"
            "Blocks: DQ-002\n"
            "\n"
            "A plain paragraph of context for this entry.\n"
            "\n"
            "### DQ-002: A second open question\n"
            "\n"
            "Status: Banked\n"
            "\n"
            "Question: Should we proceed?\n"
            "\n"
            "Options: Yes, No\n"
            "\n"
            "Cost of deciding late: More delay.\n"
            "\n"
            "Blocks: none\n")
        appended = (
            "Open group\n"
            "\n"
            "DQ-001: A sample open question\n"
            "Date: no date recorded\n"
            "Status as written: Banked\n"
            "State: Open\n"
            "Determining element: line start Status line at "
            "line 5: Banked\n"
            "Question: Which option should we take?\n"
            "Options: Option A, Option B\n"
            "Cost of deciding late: Work stays blocked.\n"
            "\n"
            "DQ-002: A second open question\n"
            "Date: no date recorded\n"
            "Status as written: Banked\n"
            "State: Open\n"
            "Determining element: line start Status line at "
            "line 19: Banked\n"
            "Question: Should we proceed?\n"
            "Options: Yes, No\n"
            "Cost of deciding late: More delay.\n")
        output = _run(base + appended, "app-render")
        self.assertEqual([], _conflict_statements(output))

    def test_genuine_repeated_field_still_conflicts_pin(self):
        data = ("# Decision queue\n\n" + _banked_entry(
            1, "A sample open question",
            "\nQuestion: A different question entirely?\n"))
        output = _run(data, "genuine-repeat")
        self.assertEqual(1, len(_conflict_statements(output)))

    def test_identical_repeat_takes_no_conflict_pin(self):
        data = ("# Decision queue\n\n" + _banked_entry(
            1, "A sample open question",
            "\nQuestion: Which option should we take?\n"))
        output = _run(data, "identical-repeat")
        self.assertEqual([], _conflict_statements(output))


if __name__ == "__main__":
    unittest.main()
