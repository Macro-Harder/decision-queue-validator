"""Restart Step 17 fix wave 6, Fix Seat K5 tests.

Charges CH-97, CH-101, CH-102, CH-109, and CH-112, ruled
at section 58 of design/steps/step-17r-record.md and
prepared at design/steps/step-17r-triage6-prep.md.

CH-97 (validate, and the parse segment claim naming scan):
seat 4 findings F-1 (the CH-82 digit following limb stated
as letters, symbols, and connector punctuation only; the
ruling at section 58 states the ground as letters, symbols,
and punctuation whole, classes L, S, and P, standing
between two digits) and F-2 (the ghost verb first scan, the
decision evidence verb claim scan, and the parse side
segment claim naming scan standing outside the continuation
guard entirely, manufacturing or misattributing from tokens
interrupted by ground characters, U+061C Cf and U+E000 Co
named in the paper).

CH-101 (validate, the ghost, claim, and evidence scan
widths, round 6 limbs): seat 7 findings S17-ATK6-7-01 (the
ghost verb first Closed form and the Resolve forms),
S17-ATK6-7-02 (the ghost stands decided form and the left
closed form), S17-ATK6-7-03 (the evidence verb first
Resolved form), S17-ATK6-7-05 (cross entry claims in the
remains parked, is still decided, and stands presented
forms only), and S17-ATK6-7-06 (the heading dressed Status
limb reading the marker in either case).

CH-102 (validate, closing prose derivation crossings,
named crossings only, under ruling (f) of section 52):
seat 7 finding S17-ATK6-7-04, the ruling noun beside
sealed and the settlement noun beside shut. The two bound
guards (the decision noun beside sealed, the verdict noun
beside shut) stand pinned deriving Open in both directions.

CH-109 (validate, the check 8 entry keying): seat 15
findings F-15-6-1 (the framed citation set and its
snapshot), F-15-6-2 (the supersession coverage set), and
F-15-6-3 (the claim scan dedup, seen_claims), under ruling
(c) of section 58: the same entry bound of CH-90 reaches
every set in check 8 that keys by an entry.

CH-112 (validate, the rendered echo exclusion run
reading): seat 20 finding F-20-6-5, under ruling (i) of
section 58: a blank line standing between any two lines of
a rendered run stands as no break in the run. A field line
standing in no rendered run stands as a field statement
exactly as the CH-94 bound states.

Constructions are the finding papers own constructions,
rebuilt inline from the attack scratch files. Governing
pins stand as controls in this file and in the fix wave 5
K5 file re-run whole at the close.
"""

import unittest

import dqv_harness as h

validate = h.import_module("validate")

PUA = "\ue000"
ALM = "\u061c"
ZWSP = "\u200b"
HYPHEN = "\u2010"
MINUS = "\u002d"
EXCL = "\u0021"
QUEST = "\u003f"
MIDDOT = "\u00b7"
LPAREN = "\u0028"
RPAREN = "\u0029"
PI = "\u00ab"
PF = "\u00bb"


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


def _framed_warnings(output, number):
    return [s for s in _statements(output)
            if "DQ-%03d is cited in a citation frame" % number in s]


def _named_entries(output):
    names = set()
    for f in h.findings_of(output):
        for name in getattr(f, "named_entries", None) or []:
            names.add(name)
    return names


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


class Ch97GuardPunctuationTest(unittest.TestCase):
    """CH-97 limb 1: the digit following ground, seat 4 F-1."""

    def test_framed_inside_punctuation_classes_manufacture_nothing(self):
        chars = {
            "Pd hyphen minus": MINUS, "Pd hyphen": HYPHEN,
            "Po exclamation": EXCL, "Po question": QUEST,
            "Po middle dot": MIDDOT, "Ps left parenthesis": LPAREN,
            "Pe right parenthesis": RPAREN,
            "Pi left angle bracket": PI,
            "Pf right angle bracket": PF,
        }
        for name, char in chars.items():
            with self.subTest(form=name):
                output = _run(_segment_queue(
                    "See the note at DQ-88" + char
                    + "8 for context."), "m01-inside")
                self.assertEqual([], _pd_r7(output, 88))
                self.assertEqual(
                    [], [s for s in _statements(output)
                         if "DQ-088" in s])

    def test_framed_first_position_variant_manufactures_nothing(self):
        output = _run(_segment_queue(
            "See the note at DQ-8" + MINUS + "88 for context."),
            "m02-first-inside")
        self.assertEqual([], _pd_r7(output, 8))
        self.assertEqual(
            [], [s for s in _statements(output) if "DQ-008" in s])

    def test_entry_plain_hyphen_inside_manufactures_nothing(self):
        data = ("# Decision queue\n\n" + _banked_entry(
            1, "A sample open question",
            "\nThe token DQ-88" + HYPHEN + "8 stands as context.\n"))
        output = _run(data, "m03-entry-plain")
        self.assertEqual([], _pd_r7(output, 88))

    def test_blocks_hyphen_inside_manufactures_nothing(self):
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
                "Blocks: DQ-00" + HYPHEN + "2\n"
                "\n"
                "A plain paragraph of context for this entry.\n")
        output = _run(data, "m03-blocks")
        self.assertEqual([], _pd_r7(output, 0))
        self.assertEqual(
            [], [s for s in _statements(output) if "DQ-000" in s])

    def test_heading_title_hyphen_inside_manufactures_nothing(self):
        data = ("# Decision queue\n\n" + _banked_entry(
            5, "A title naming DQ-88" + HYPHEN + "8 in passing"))
        output = _run(data, "m11-heading-title")
        self.assertEqual([], _pd_r7(output, 88))

    def test_supersession_hyphen_inside_manufactures_nothing(self):
        data = ("# Decision queue\n\n" + _banked_entry(
            1, "A sample open question",
            "\nThis ruling supersedes DQ-88" + HYPHEN
            + "8 and DQ-777.\n"))
        output = _run(data, "m07-super")
        self.assertEqual([], _pd_r7(output, 88))
        self.assertEqual(1, len(_pd_r7(output, 777)))

    def test_segment_claim_hyphen_inside_manufactures_nothing(self):
        output = _run(_segment_queue(
            "DQ-88" + HYPHEN + "8 was ruled and closed."),
            "m04-segclaim-inside")
        self.assertEqual([], _claims_about(output, 88))

    def test_clean_framed_token_still_reports_pin(self):
        output = _run(_segment_queue(
            "See the note at DQ-888 for context."), "clean-pin")
        self.assertEqual(1, len(_pd_r7(output, 888)))

    def test_trailing_punctuation_token_still_reports_pin(self):
        output = _run(_segment_queue(
            "See the note at DQ-888" + HYPHEN + " for context."),
            "m02-trailing-pin")
        self.assertEqual(1, len(_pd_r7(output, 888)))


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


class Ch97OutsideScansTest(unittest.TestCase):
    """CH-97 limb 2: the scans outside the guard, seat 4 F-2."""

    def test_ghost_verb_first_interrupted_manufactures_nothing(self):
        chars = {"arabic letter mark": ALM, "private use": PUA,
                 "hyphen": HYPHEN}
        for name, char in chars.items():
            with self.subTest(form=name):
                output = _run(_ghost_status_entry(
                    502, "Ruled DQ-88" + char + "8 in full."),
                    "m14-ghost-verb")
                self.assertEqual([], _pd_r7(output, 88))
                self.assertEqual(
                    [], [s for s in _statements(output)
                         if "DQ-088" in s])

    def test_ghost_verb_first_clean_still_reports_pin(self):
        output = _run(_ghost_status_entry(
            502, "Ruled DQ-999 in full."), "m14-clean")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_evidence_verb_claim_interrupted_misattributes_nothing(self):
        chars = {"arabic letter mark": ALM, "hyphen": HYPHEN}
        for name, char in chars.items():
            with self.subTest(form=name):
                data = (
                    "# Decision queue\n"
                    "\n"
                    "### DQ-001: Evidence claim probe\n"
                    "\n"
                    "Status: RULED, closed\n"
                    "\n"
                    "Ruled by: Captain JP\n"
                    "\n"
                    "Ruling text: \"Ruled DQ-002" + char
                    + "9 in full.\"\n"
                    "\n"
                    "Ruling outcome: Recorded in full.\n"
                    "\n"
                    "Where the ruling landed: NOWHERE.md, "
                    "sample rule.\n"
                    "\n"
                    "### DQ-002: A sample open question\n"
                    "\n"
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
                    "A plain paragraph of context for this "
                    "entry.\n")
                output = _run(data, "m15-evidence-headed")
                self.assertEqual([], _claims_about(output, 2))

    def test_evidence_verb_claim_clean_still_reports_pin(self):
        data = (
            "# Decision queue\n"
            "\n"
            "### DQ-001: Evidence claim probe\n"
            "\n"
            "Status: RULED, closed\n"
            "\n"
            "Ruled by: Captain JP\n"
            "\n"
            "Ruling text: \"Ruled DQ-002 in full.\"\n"
            "\n"
            "Ruling outcome: Recorded in full.\n"
            "\n"
            "Where the ruling landed: NOWHERE.md, sample rule.\n"
            "\n"
            "### DQ-002: A sample open question\n"
            "\n"
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
        output = _run(data, "m15-clean")
        self.assertEqual(1, len(_claims_about(output, 2)))

    def test_parse_governs_bullet_interrupted_names_nothing(self):
        chars = {"arabic letter mark": ALM, "private use": PUA,
                 "hyphen": HYPHEN}
        for name, char in chars.items():
            with self.subTest(form=name):
                output = _run(_segment_queue(
                    "This note governs the queue.\n"
                    "- DQ-888" + char + " was ruled and closed."),
                    "m16-governs-bullet")
                self.assertNotIn("DQ-888", _named_entries(output))

    def test_parse_governs_prose_interrupted_names_nothing(self):
        output = _run(_segment_queue(
            "This note governs DQ-888" + ALM + " and the queue."),
            "m16-governs-prose")
        self.assertNotIn("DQ-888", _named_entries(output))

    def test_parse_governs_clean_still_names_pin(self):
        output = _run(_segment_queue(
            "This note governs the queue.\n"
            "- DQ-888 was ruled and closed."),
            "m16-clean-governs")
        self.assertIn("DQ-888", _named_entries(output))


class Ch101GhostScanTest(unittest.TestCase):
    """CH-101 ghost limbs: S17-ATK6-7-01 and 02."""

    def test_status_closed_verb_first_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            602, "Closed DQ-999 in full."), "g01")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_resolved_verb_first_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            603, "Resolved DQ-999 in full."), "g02")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_resolves_verb_first_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            604, "Resolves DQ-999 in full."), "g03")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_stands_decided_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            605, "DQ-999 stands decided."), "g04")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_left_closed_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            606, "DQ-999 left closed."), "g05")
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


class Ch101EvidenceVerbFirstTest(unittest.TestCase):
    """CH-101 evidence limb: S17-ATK6-7-03."""

    def test_evidence_resolved_verb_first_takes_claim_note(self):
        output = _run(_evidence_entry(
            622, "Resolved DQ-623 in full.", 623), "e01")
        self.assertEqual(1, len(_claims_about(output, 623)))

    def test_evidence_resolve_present_still_takes_note_pin(self):
        output = _run(_evidence_entry(
            624, "Resolve DQ-625 in full.", 625), "e02")
        self.assertEqual(1, len(_claims_about(output, 625)))


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


class Ch101ClaimPredicateTest(unittest.TestCase):
    """CH-101 claim limb: S17-ATK6-7-05, three forms only."""

    def test_claim_remains_parked_takes_note(self):
        output = _run(_claim_file(
            612, "DQ-613 remains parked.", 613), "c01")
        self.assertEqual(1, len(_claims_about(output, 613)))

    def test_claim_is_still_decided_takes_note(self):
        output = _run(_claim_file(
            614, "DQ-615 is still decided.", 615), "c02")
        self.assertEqual(1, len(_claims_about(output, 615)))

    def test_claim_stands_presented_takes_note(self):
        output = _run(_claim_file(
            616, "DQ-617 stands presented.", 617), "c03")
        self.assertEqual(1, len(_claims_about(output, 617)))


class Ch101HeadingDressedStatusTest(unittest.TestCase):
    """CH-101 heading limb: S17-ATK6-7-06."""

    def test_heading_lowercase_status_line_takes_a_signal(self):
        data = ("# Decision queue\n\n" + _banked_entry(
            642, "Banked head, heading status probe",
            "\n#### status: RULED, closed\n"))
        output = _run(data, "s01-lower")
        hits = [f for f in h.findings_of(output)
                if h.span_of(f)[0] == 17
                and "standing as a heading" in
                (h.finding_statement(f) or "")]
        self.assertEqual(1, len(hits))

    def test_heading_capitalised_status_still_takes_signal_pin(self):
        data = ("# Decision queue\n\n" + _banked_entry(
            643, "Banked head, heading status probe",
            "\n#### Status: RULED, closed\n"))
        output = _run(data, "s01-capital-pin")
        hits = [f for f in h.findings_of(output)
                if h.span_of(f)[0] == 17
                and "standing as a heading" in
                (h.finding_statement(f) or "")]
        self.assertEqual(1, len(hits))


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


class Ch102ClosingProseCrossingsTest(unittest.TestCase):
    """CH-102: S17-ATK6-7-04, named crossings only."""

    def test_ruling_noun_beside_sealed_derives_ambiguous(self):
        output = _run(_prose_file(
            632, "The ruling is final and this entry is now "
                 "sealed."), "p01")
        self.assertEqual("Ambiguous", _state_of(output, "DQ-632"))

    def test_settlement_noun_beside_shut_derives_ambiguous(self):
        output = _run(_prose_file(
            633, "The settlement is final and this entry is now "
                 "shut."), "p02")
        self.assertEqual("Ambiguous", _state_of(output, "DQ-633"))

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


def _banked_copy(number, paragraph):
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
        "%s\n" % (number, number, number, paragraph))


def _ruled_copy_superseding():
    return (
        "### DQ-001: Ruled question DQ-001\n"
        "\n"
        "Status: Ruled\n"
        "\n"
        "Ruled by: Captain JP, 2026-11-17\n"
        "\n"
        "Ruling: Option A stands.\n"
        "\n"
        "Outcome: The option is settled.\n"
        "\n"
        "Landed: Recorded in the queue.\n"
        "\n"
        "This ruling supersedes DQ-999.\n")


_FRAMED_PARA = "The earlier call stands, see DQ-999."
_PLAIN_PARA = "DQ-999 is decided."


class Ch109FramedSetTest(unittest.TestCase):
    """CH-109 framed limb: F-15-6-1."""

    def test_framed_first_plain_second_reports_each(self):
        data = ("# Decision queue\n\n"
                + _banked_copy(1, _FRAMED_PARA)
                + _banked_copy(1, _PLAIN_PARA))
        output = _run(data, "f01")
        self.assertEqual(1, len(_framed_warnings(output, 999)))
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_plain_first_framed_second_reports_each(self):
        data = ("# Decision queue\n\n"
                + _banked_copy(1, _PLAIN_PARA)
                + _banked_copy(1, _FRAMED_PARA))
        output = _run(data, "f02")
        self.assertEqual(1, len(_framed_warnings(output, 999)))
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_two_copies_framed_reports_each(self):
        data = ("# Decision queue\n\n"
                + _banked_copy(1, _FRAMED_PARA)
                + _banked_copy(1, _FRAMED_PARA))
        output = _run(data, "f06")
        self.assertEqual(2, len(_framed_warnings(output, 999)))

    def test_distinct_identifiers_still_report_each_pin(self):
        data = ("# Decision queue\n\n"
                + _banked_copy(1, _FRAMED_PARA)
                + _banked_copy(2, _PLAIN_PARA))
        output = _run(data, "f03")
        self.assertEqual(1, len(_framed_warnings(output, 999)))
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_one_entry_framed_and_plain_suppression_pin(self):
        entry = (
            "### DQ-001: Question DQ-001\n"
            "\n"
            "Status: Banked\n"
            "\n"
            "Question: Which option should we take for DQ-001?\n"
            "\n"
            "Options: Option A, Option B\n"
            "\n"
            "Cost of deciding late: Work stays blocked while "
            "this waits.\n"
            "\n"
            "Blocks: nothing named\n"
            "\n"
            + _FRAMED_PARA + "\n"
            "\n"
            + _PLAIN_PARA + "\n")
        output = _run("# Decision queue\n\n" + entry, "f05")
        self.assertEqual(1, len(_framed_warnings(output, 999)))
        self.assertEqual(0, len(_pd_r7(output, 999)))


class Ch109CoverageSetTest(unittest.TestCase):
    """CH-109 coverage limb: F-15-6-2."""

    def test_superseding_first_plain_second_reports_each(self):
        data = ("# Decision queue\n\n" + _ruled_copy_superseding()
                + _banked_copy(1, _PLAIN_PARA))
        output = _run(data, "p01")
        self.assertEqual(2, len(_pd_r7(output, 999)))

    def test_plain_first_superseding_second_reports_each(self):
        data = ("# Decision queue\n\n"
                + _banked_copy(1, _PLAIN_PARA)
                + _ruled_copy_superseding())
        output = _run(data, "p02")
        self.assertEqual(2, len(_pd_r7(output, 999)))

    def test_superseding_then_framed_twin_reports_each(self):
        data = ("# Decision queue\n\n" + _ruled_copy_superseding()
                + _banked_copy(1, _FRAMED_PARA))
        output = _run(data, "p05")
        self.assertEqual(1, len(_pd_r7(output, 999)))
        self.assertEqual(1, len(_framed_warnings(output, 999)))

    def test_superseding_then_heading_twin_reports_each(self):
        twin = (
            "### DQ-001: Question about DQ-999\n"
            "\n"
            "Status: Banked\n"
            "\n"
            "Question: Which option should we take for DQ-001?\n"
            "\n"
            "Options: Option A, Option B\n"
            "\n"
            "Cost of deciding late: Work stays blocked while "
            "this waits.\n"
            "\n"
            "Blocks: nothing named\n"
            "\n"
            "A plain context paragraph.\n")
        data = ("# Decision queue\n\n" + _ruled_copy_superseding()
                + twin)
        output = _run(data, "p06")
        self.assertEqual(2, len(_pd_r7(output, 999)))

    def test_distinct_identifiers_still_report_each_pin(self):
        data = ("# Decision queue\n\n" + _ruled_copy_superseding()
                + _banked_copy(2, _PLAIN_PARA))
        output = _run(data, "p03")
        self.assertEqual(2, len(_pd_r7(output, 999)))


def _claim_target_entry():
    return (
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


def _claiming_copy(number, claim_paragraphs):
    body = "\n\n".join(claim_paragraphs)
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
        "%s\n" % (number, number, number, body))


class Ch109ClaimDedupTest(unittest.TestCase):
    """CH-109 claim dedup limb: F-15-6-3."""

    def test_two_claiming_copies_take_two_notes(self):
        data = ("# Decision queue\n\n" + _claim_target_entry()
                + _claiming_copy(10, ["DQ-001 is Ruled."])
                + _claiming_copy(10, ["DQ-001 is Ruled."]))
        output = _run(data, "c01")
        self.assertEqual(2, len(_claims_about(output, 1)))

    def test_distinct_claiming_still_take_two_notes_pin(self):
        data = ("# Decision queue\n\n" + _claim_target_entry()
                + _claiming_copy(10, ["DQ-001 is Ruled."])
                + _claiming_copy(11, ["DQ-001 is Ruled."]))
        output = _run(data, "c02")
        self.assertEqual(2, len(_claims_about(output, 1)))

    def test_within_entry_dedup_still_takes_one_note_pin(self):
        data = ("# Decision queue\n\n" + _claim_target_entry()
                + _claiming_copy(
                    10, ["DQ-001 is Ruled.", "DQ-001 is Ruled."]))
        output = _run(data, "c01-within-pin")
        self.assertEqual(1, len(_claims_about(output, 1)))


def _conflict_statements(output):
    return [s for s in _statements(output)
            if "two contradictory values" in s]


def _append_base():
    return (
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


def _append_block():
    return (
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


class Ch112RenderEchoRunTest(unittest.TestCase):
    """CH-112: F-20-6-5, the blank line inside a rendered run."""

    def test_double_spaced_append_takes_no_field_conflict(self):
        appended = "\n\n".join(
            _append_block().rstrip("\n").split("\n")) + "\n"
        output = _run(_append_base() + appended, "app-blank-inside")
        self.assertEqual([], _conflict_statements(output))

    def test_partly_blanked_append_takes_no_field_conflict(self):
        lines = _append_block().rstrip("\n").split("\n")
        out_lines = []
        for index, line in enumerate(lines):
            out_lines.append(line)
            if index in (2, 5, 9, 14):
                out_lines.append("")
        appended = "\n".join(out_lines) + "\n"
        output = _run(_append_base() + appended, "app-part-blank")
        self.assertEqual([], _conflict_statements(output))

    def test_consecutive_append_still_takes_no_conflict_pin(self):
        output = _run(_append_base() + _append_block(), "app-render")
        self.assertEqual([], _conflict_statements(output))

    def test_sweep_line_standing_alone_still_conflicts_pin(self):
        data = ("# Decision queue\n\n" + _banked_entry(
            1, "A sample open question",
            "\nQuestion: Which other option should we take?\n"))
        output = _run(data, "sweep-line-pin")
        self.assertEqual(1, len(_conflict_statements(output)))


if __name__ == "__main__":
    unittest.main()
