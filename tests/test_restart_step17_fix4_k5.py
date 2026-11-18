"""Restart Step 17 fix wave 4, Fix Seat K5 tests.

Charges CH-60 and CH-73, ruled at section 38 of
design/steps/step-17r-record.md, rulings (e) and (g) and the
FLAG 5 disposition, and prepared at
design/steps/step-17r-triage4-prep.md.

CH-60 (validate, the claim, ghost, and evidence scan widths):
seat 7 findings S17-ATK4-7-02 (a ghost number named on the
entry own Status line in the has, has been, got, bare past,
stands, and Decides forms is read by no scan), S17-ATK4-7-03
(cross entry state claims in the bare past form outside the
CH-39 adverb set take no claim Note), S17-ATK4-7-05 (decision
evidence naming a headed entry with a past tense verb first
form takes no claim Note), S17-ATK4-7-06 (status claims stated
with the word shut take no claim Note and no ghost Note),
S17-ATK4-7-07 (decision evidence naming a headed entry with
Resolve, or with a Decision on noun form, takes no claim
Note), and S17-ATK4-7-08 (a cross entry state claim carried
in an entry heading title is read by no scan).

CH-73 (validate, the citation token continuation guard):
seat 4 finding F-1 (the CH-39 token continuation guard is an
enumerated list, and citation tokens continuing in characters
outside it are still read in part on the framed, plain,
segment, and entry surfaces, manufacturing DQ-088 and DQ-000
where no such token stands). The ruled ground is class based:
token continuation is admitted by Unicode class, and the
class boundary pinned by this file is stated in the K5 paper.

Constructions are the finding papers own constructions,
rebuilt inline from the attack scratch files. Pins stated in
the charges stand as controls in this file: the CH-39 pins
whole (the listed continuation characters refused whole, the
was form ghost control taking exactly one Note, the bare past
adverb forms, and the ruling reference forms that the
governed corpus pin protects), the CH-7 entry heading limb,
the CH-24 pins, and the legitimate terminator bound at
record section 26 flag (f).
"""

import unittest

import dqv_harness as h

validate = h.import_module("validate")

ZWSP = "\u200b"
ACUTE = "\u0301"
ALM = "\u061c"
SHADDA = "\u0651"
TAG = "\U000e0041"
INTERLINEAR = "\ufff9"
MVS = "\u180e"
NUKTA = "\u093c"
THAI = "\u0e31"
CYR_COMB = "\u2de0"
HEBREW_PT = "\u05b0"
VS_SUPP = "\U000e0100"
ISOLATE = "\u2066"
UNASSIGNED = "\u0378"

_BANKED_BODY_999 = (
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
    "A plain paragraph of context for this entry.\n"
)

_BANKED_BODY = (
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
)


def _run(data, name):
    _model, output = h.run_pipeline(data.encode("utf-8"), name)
    if output is None:
        raise AssertionError("pipeline returned a failure for " + name)
    return output


def _statements(output):
    return [h.finding_statement(f) or ""
            for f in h.findings_of(output)]


def _claim_statements(output):
    return [s for s in _statements(output) if "records a claim" in s]


def _claims_about(output, target_number):
    return [s for s in _claim_statements(output)
            if "about the state of DQ-%03d" % target_number in s]


_DECIDED_SKELETON = (
    "# Decision queue\n"
    "\n"
    "### DQ-%03d: %s\n"
    "\n"
    "Status: %s\n"
    "\n"
    "Ruled by: Captain JP\n"
    "\n"
    "Ruling text: \"Settle DQ-%03d as follows.\"\n"
    "\n"
    "Ruling outcome: DQ-%03d is decided and closed.\n"
    "\n"
    "Where the ruling landed: NOWHERE.md, sample rule.\n"
    "\n"
    "#### Ruling by Captain JP\n"
    "\n"
    "Ruled: DQ-%03d is closed by this ruling. Closed.\n"
)


class GhostStatusFormsTest(unittest.TestCase):
    """S17-ATK4-7-02: a ghost number named on the entry own
    Status line in the has, has been, got, bare past, stands,
    and Decides forms is read by no scan. The ghost scan reads
    the Status line forms the prose claim scan reads."""

    def _ghost_notes(self, status_value, name):
        data = _DECIDED_SKELETON % (
            412, "Ghost status probe", status_value, 412, 412, 412)
        output = _run(data, name)
        return [s for s in _statements(output)
                if "DQ-999 is cited" in s]

    def test_has_been_closed_on_status_line_is_reported_once(self):
        notes = self._ghost_notes(
            "RULED, closed. DQ-999 has been closed.", "g01.md")
        self.assertEqual(len(notes), 1)

    def test_has_closed_on_status_line_is_reported_once(self):
        notes = self._ghost_notes(
            "RULED, closed. DQ-999 has closed.", "g08.md")
        self.assertEqual(len(notes), 1)

    def test_got_closed_on_status_line_is_reported_once(self):
        notes = self._ghost_notes(
            "RULED, closed. DQ-999 got closed.", "g02.md")
        self.assertEqual(len(notes), 1)

    def test_bare_past_on_status_line_is_reported_once(self):
        notes = self._ghost_notes(
            "RULED, closed. DQ-999 closed yesterday.", "g04.md")
        self.assertEqual(len(notes), 1)

    def test_stands_closed_on_status_line_is_reported_once(self):
        notes = self._ghost_notes(
            "RULED, closed. DQ-999 stands closed.", "g06.md")
        self.assertEqual(len(notes), 1)

    def test_decides_on_status_line_is_reported_once(self):
        notes = self._ghost_notes(
            "RULED, closed. Decides DQ-999 in full.", "g03.md")
        self.assertEqual(len(notes), 1)

    def test_was_shut_on_status_line_is_reported_once(self):
        # S17-ATK4-7-06, the ghost limb: shut stands beside the
        # closed forms on this surface as on the claim scan.
        notes = self._ghost_notes(
            "RULED, closed. DQ-999 was shut.", "g05.md")
        self.assertEqual(len(notes), 1)

    def test_was_closed_on_status_line_stays_reported_once(self):
        # Pin, the CH-39 cured was form control, case
        # g07-status-was-closed of the round 4 paper: exactly
        # one Note, no second report from any other scan.
        notes = self._ghost_notes(
            "RULED, closed. DQ-999 was closed.", "g07.md")
        self.assertEqual(len(notes), 1)

    def test_is_closed_on_status_line_stays_reported_once(self):
        # Pin, the standing is form of the ghost scan.
        notes = self._ghost_notes(
            "RULED, closed. DQ-999 is closed.", "g09.md")
        self.assertEqual(len(notes), 1)


def _claim_file(claimer_number, claim_sentence, target_number):
    return (
        "# Decision queue\n"
        "\n"
        "### DQ-%03d: Claim probe\n"
        "\n"
        % claimer_number
        + _BANKED_BODY
        + "This question is waiting for a decision. "
        + claim_sentence + "\n"
        "\n"
        "### DQ-%03d: An ordinary banked entry\n"
        "\n"
        % target_number
        + _BANKED_BODY
        + "This question is waiting for a decision.\n"
    )


class BarePastClaimTest(unittest.TestCase):
    """S17-ATK4-7-03: cross entry state claims in the bare
    past form outside the CH-39 adverb set (a bare past
    sentence closing on its own full stop, on a week phrase,
    or on the in full form) take no claim Note."""

    def test_bare_past_closing_on_full_stop_takes_a_note(self):
        output = _run(
            _claim_file(422, "DQ-423 closed.", 423), "c01.md")
        self.assertTrue(_claims_about(output, 423))

    def test_bare_past_closing_on_last_week_takes_a_note(self):
        output = _run(
            _claim_file(424, "DQ-425 closed last week.", 425),
            "c02.md")
        self.assertTrue(_claims_about(output, 425))

    def test_bare_past_closing_in_full_takes_a_note(self):
        output = _run(
            _claim_file(426, "DQ-427 closed in full.", 427),
            "c03.md")
        self.assertTrue(_claims_about(output, 427))

    def test_bare_past_adverb_form_stays_a_note(self):
        # Pin, the CH-39 charged adverb form.
        output = _run(
            _claim_file(422, "DQ-423 closed yesterday.", 423),
            "c01p.md")
        self.assertTrue(_claims_about(output, 423))

    def test_ruling_references_take_no_note(self):
        # Pin, the governed corpus pin the CH-39 narrowing
        # protects: a bare past verb carrying an object after
        # it is a mention of that ruling, not a state claim
        # (DQ-031 ruled that, DQ-029 settled R-92, fixture R1).
        for sentence in (
                "DQ-423 ruled that the earlier point stands.",
                "DQ-423 settled R-92 in the earlier round."):
            with self.subTest(sentence=sentence):
                output = _run(
                    _claim_file(422, sentence, 423), "c01r.md")
                self.assertEqual(_claims_about(output, 423), [])

    def test_future_progressive_gerund_forms_take_no_note(self):
        # Bound, paper observation O-4: none of these states a
        # present or past decided state, and none is charged.
        for sentence in ("DQ-423 will be ruled and closed.",
                         "DQ-423 is being ruled.",
                         "Closing DQ-423 now."):
            with self.subTest(sentence=sentence):
                output = _run(
                    _claim_file(422, sentence, 423), "c01o.md")
                self.assertEqual(_claims_about(output, 423), [])


def _evidence_file(ruling_text, claimer_number, target_number):
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
        "### DQ-%03d: An ordinary banked entry\n"
        "\n"
        % (claimer_number, ruling_text, target_number)
        + _BANKED_BODY
        + "This question is waiting for a decision.\n"
    )


class EvidenceVerbFormsTest(unittest.TestCase):
    """S17-ATK4-7-05 and S17-ATK4-7-07: decision evidence
    naming a headed entry with a past tense verb first form,
    with Resolve, or with a Decision on noun form, takes no
    claim Note."""

    def test_closed_verb_first_evidence_takes_a_note(self):
        output = _run(
            _evidence_file("Closed DQ-443 in full.", 442, 443),
            "e01.md")
        self.assertTrue(_claims_about(output, 443))

    def test_settled_verb_first_evidence_takes_a_note(self):
        output = _run(
            _evidence_file("Settled DQ-445 as follows.", 444, 445),
            "e02.md")
        self.assertTrue(_claims_about(output, 445))

    def test_resolve_evidence_takes_a_note(self):
        output = _run(
            _evidence_file("Resolve DQ-449 as follows.", 448, 449),
            "e04.md")
        self.assertTrue(_claims_about(output, 449))

    def test_decision_on_evidence_takes_a_note(self):
        output = _run(
            _evidence_file("Decision on DQ-451 as follows.",
                           450, 451),
            "e05.md")
        self.assertTrue(_claims_about(output, 451))

    def test_settle_evidence_stays_a_note(self):
        # Pin, the standing present verb first form.
        output = _run(
            _evidence_file("Settle DQ-443 as follows.", 442, 443),
            "e01p.md")
        self.assertTrue(_claims_about(output, 443))


class ShutClaimTest(unittest.TestCase):
    """S17-ATK4-7-06: status claims stated with the word shut
    take no claim Note on the prose and evidence surfaces.
    The claim, ghost, and evidence readings carry shut beside
    the closed forms they already read."""

    def test_was_shut_claim_takes_a_note(self):
        output = _run(
            _claim_file(428, "DQ-429 was shut.", 429), "c04.md")
        self.assertTrue(_claims_about(output, 429))

    def test_is_shut_claim_takes_a_note(self):
        output = _run(
            _claim_file(430, "DQ-431 is shut.", 431), "c05.md")
        self.assertTrue(_claims_about(output, 431))

    def test_has_been_shut_claim_takes_a_note(self):
        output = _run(
            _claim_file(434, "DQ-435 has been shut.", 435),
            "c07.md")
        self.assertTrue(_claims_about(output, 435))

    def test_stands_shut_claim_takes_a_note(self):
        output = _run(
            _claim_file(430, "DQ-431 stands shut.", 431),
            "c05b.md")
        self.assertTrue(_claims_about(output, 431))

    def test_is_shut_evidence_takes_a_note(self):
        output = _run(
            _evidence_file("DQ-447 is shut.", 446, 447), "e03.md")
        self.assertTrue(_claims_about(output, 447))


class HeadingTitleClaimTest(unittest.TestCase):
    """S17-ATK4-7-08: a cross entry state claim carried in an
    entry heading title is read by no scan. The cure reaches
    the claim reading on the heading title only, under FLAG 5:
    no heading line is excluded from any other reading, and
    no heading line is read for every scan."""

    def _heading_file(self, title, claimer_number, target_number):
        return (
            "# Decision queue\n"
            "\n"
            "### DQ-%03d: %s\n"
            "\n"
            % (claimer_number, title)
            + _BANKED_BODY
            + "This question is waiting for a decision.\n"
            "\n"
            "### DQ-%03d: Target banked entry\n"
            "\n"
            % target_number
            + _BANKED_BODY
            + "This question is waiting for a decision.\n"
        )

    def test_claim_in_heading_title_takes_a_note(self):
        output = _run(
            self._heading_file(
                "Claim that DQ-440 was closed", 439, 440),
            "c09.md")
        self.assertTrue(_claims_about(output, 440))

    def test_heading_naming_entry_without_claim_takes_no_note(self):
        # Bound: a heading title that names a headed entry
        # without stating a state claim takes no claim Note.
        output = _run(
            self._heading_file("Notes about DQ-440", 439, 440),
            "c09b.md")
        self.assertEqual(_claims_about(output, 440), [])

    def test_ghost_number_in_heading_title_stays_reported(self):
        # Pin, the CH-7 entry heading limb: the entry heading
        # line stands as a citation surface of the entry, and
        # this cure excludes no heading line from that reading.
        output = _run(
            self._heading_file("Note on DQ-999", 439, 440),
            "c09c.md")
        named = [s for s in _statements(output)
                 if "DQ-999 is cited" in s]
        self.assertTrue(named)


def _quarantined_file(heading_title, extra_line=None):
    data = (
        "# Decision queue\n"
        "\n"
        "### DQ-002: A sample open question\n"
        "\n"
        + _BANKED_BODY_999
        + "\n"
        + "### DQ-00" + ZWSP + "1: " + heading_title + "\n"
        "\n"
        + _BANKED_BODY_999
    )
    if extra_line is not None:
        data += "\n" + extra_line + "\n"
    return data


def _entry_file(extra_line):
    return (
        "# Decision queue\n"
        "\n"
        "### DQ-001: A sample open question\n"
        "\n"
        + _BANKED_BODY_999
        + "\n" + extra_line + "\n"
    )


class TokenContinuationClassTest(unittest.TestCase):
    """Seat 4 F-1, CH-73: the token continuation guard is an
    enumerated list, and a citation token continuing in a
    character outside the list is still read in part on the
    framed, plain, segment, and entry surfaces. The ruled
    ground is class based: a token continuing in a character
    of the governed classes is refused whole."""

    def _segment_named(self, token_text, name):
        output = _run(
            _quarantined_file(
                "A sample open question",
                extra_line="See the note at " + token_text
                + " for context."),
            name)
        return _statements(output)

    def test_inside_classes_refused_on_framed_segment_surface(self):
        for mark in (ALM, SHADDA, TAG, INTERLINEAR, MVS, NUKTA,
                     THAI, CYR_COMB):
            with self.subTest(mark="U+%04X" % ord(mark)):
                named = [s for s in self._segment_named(
                    "DQ-88" + mark + "8", "h-in.md")
                    if "DQ-088" in s]
                self.assertEqual(named, [])

    def test_trailing_classes_refused_on_framed_segment_surface(self):
        for mark in (ALM, HEBREW_PT, VS_SUPP):
            with self.subTest(mark="U+%04X" % ord(mark)):
                named = [s for s in self._segment_named(
                    "DQ-888" + mark, "h-tr.md") if "DQ-888" in s]
                self.assertEqual(named, [])

    def test_mark_stack_trailing_refused_on_framed_segment(self):
        named = [s for s in self._segment_named(
            "DQ-888" + SHADDA * 200, "h35.md") if "DQ-888" in s]
        self.assertEqual(named, [])

    def test_inside_class_refused_on_plain_segment_surface(self):
        output = _run(
            _quarantined_file(
                "A sample open question",
                extra_line="The token DQ-88" + ALM
                + "8 stands as context."),
            "h10.md")
        named = [s for s in _statements(output) if "DQ-088" in s]
        self.assertEqual(named, [])

    def test_inside_class_refused_on_framed_entry_surface(self):
        output = _run(
            _entry_file("See the note at DQ-88" + ISOLATE
                        + "8 for context."),
            "h05.md")
        named = [s for s in _statements(output) if "DQ-088" in s]
        self.assertEqual(named, [])

    def test_inside_class_refused_on_plain_entry_surface(self):
        output = _run(
            _entry_file("The token DQ-88" + ALM
                        + "8 stands as context."),
            "h14.md")
        named = [s for s in _statements(output) if "DQ-088" in s]
        self.assertEqual(named, [])

    def test_unassigned_inside_blocks_token_manufactures_no_number(self):
        data = (
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
            "Blocks: DQ-00" + UNASSIGNED + "2\n"
            "\n"
            "A plain paragraph of context for this entry.\n"
        )
        output = _run(data, "h34.md")
        named = [s for s in _statements(output) if "DQ-000" in s]
        self.assertEqual(named, [])

    def test_listed_characters_stay_refused_whole(self):
        # Pin, the CH-39 pins whole: every character the CH-39
        # list names stands as a pin inside the class reading
        # (cases h15, h16, h17, and h31 of the round 4 paper).
        for mark in (ACUTE, "\u202e", "\u00ad", "\ufeff"):
            with self.subTest(mark="U+%04X" % ord(mark)):
                named = [s for s in self._segment_named(
                    "DQ-88" + mark + "8", "h-pin.md")
                    if "DQ-088" in s]
                self.assertEqual(named, [])

    def test_full_stop_terminated_token_still_reports(self):
        # Pin and bound, record section 26 flag (f): a token
        # closed by a full stop is a legitimate terminator and
        # stands outside the charge (case h34c form, framed).
        named = [s for s in self._segment_named("DQ-888.", "f21.md")
                 if "DQ-888" in s]
        self.assertTrue(named)

    def test_clean_ascii_token_still_reports(self):
        # Pin, the CH-24 clean token reports.
        named = [s for s in self._segment_named("DQ-888", "clean.md")
                 if "DQ-888" in s]
        self.assertTrue(named)

    def test_full_stop_blocks_token_still_takes_its_note(self):
        # Control, case h34c of the round 4 paper, not charged:
        # a Blocks token carrying a visible full stop inside it
        # takes the same DQ-000 Note, on the terminator bound.
        data = (
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
            "Blocks: DQ-00.2\n"
            "\n"
            "A plain paragraph of context for this entry.\n"
        )
        output = _run(data, "h34c.md")
        named = [s for s in _statements(output) if "DQ-000" in s]
        self.assertTrue(named)


if __name__ == "__main__":
    unittest.main()
