"""Restart Step 17 fix wave 3, Fix Seat K5 tests.

Charge CH-39 (validate and parse, the claim and citation
reading family), ruled at section 26 of
design/steps/step-17r-record.md, flag ruling (f), and prepared
at design/steps/step-17r-triage3-prep.md. Findings: seat 4 F-1
Low (the parse level governing claim path bypasses the
quarantined heading line) and F-2 Low (a citation token
carrying a combining mark or a zero width character inside or
after its digits is still read in part); seat 6 Finding 1 Low
(the claim Note lists each distinct state once at three or
more copies while stating one for each standing copy); seat 7
S17-ATK3-7-02 Medium (a ghost number named as the subject of
a closure on the entry own Status line, in was form, is read
by no scan), S17-ATK3-7-03 Medium (decision evidence naming a
headed entry with a lower case verb first form takes no claim
Note), and S17-ATK3-7-05 Low (cross entry state claims in the
has closed, got ruled, and bare closed past forms take no
claim Note).

Constructions are the finding papers own constructions,
rebuilt inline from the attack scratch files. Pins stated in
the charge stand as controls in this file: the CH-7 pins whole
(the body line claim in a quarantined segment, the fallback
quarantine forms, the entry heading limb on a valid entry, the
two copy claim Note forms, and the singular same state form),
the CH-20 pins at the heading limb (re-run from their own file
at the cluster close, and the level 2 quarantined heading form
here), and the CH-24 pins whole (the mixed script refusals and
the clean token reports, including the full stop terminator
control).
"""

import unittest

import dqv_harness as h

validate = h.import_module("validate")

ZWSP = "\u200b"
ACUTE = "\u0301"

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


def _quarantined_file(heading_title, extra_line=None, heading_level=3):
    hashes = "#" * heading_level
    data = (
        "# Decision queue\n"
        "\n"
        "### DQ-002: A sample open question\n"
        "\n"
        + _BANKED_BODY_999
        + "\n"
        + hashes + " DQ-00" + ZWSP + "1: " + heading_title + "\n"
        "\n"
        + _BANKED_BODY_999
    )
    if extra_line is not None:
        data += "\n" + extra_line + "\n"
    return data


class ParseClaimQuarantineTest(unittest.TestCase):
    """Seat 4 F-1: the parse level governing claim path stands
    outside the CH-7 quarantine of the unmatched heading line."""

    def test_governing_claim_on_quarantined_heading_takes_no_note(self):
        output = _run(
            _quarantined_file("DQ-777 governs this queue"), "f01.md")
        self.assertEqual(_claim_statements(output), [])

    def test_governing_claim_naming_a_headed_entry_takes_no_note(self):
        output = _run(
            _quarantined_file("DQ-002 governs this queue"), "f02.md")
        self.assertEqual(_claim_statements(output), [])

    def test_citation_on_governing_quarantined_heading_not_reported(self):
        # Recovery correction, second holder: the first holder
        # form counted every statement naming DQ-555, which
        # also counts the PIN-06 Warning naming the quarantined
        # heading as written, a governed pin standing outside
        # CH-39. The charged harm is the citation and claim
        # reporting of the token, asserted here in exact form.
        output = _run(
            _quarantined_file("See DQ-555, which governs this queue"),
            "f20.md")
        self.assertEqual(_claim_statements(output), [])
        named = [s for s in _statements(output)
                 if "DQ-555" in s and ("is cited" in s
                                       or "records a claim" in s)]
        self.assertEqual(named, [])

    def test_body_claim_displaced_by_quarantined_heading_reports_body(self):
        output = _run(
            _quarantined_file(
                "DQ-777 governs this queue",
                extra_line="DQ-555 governs this queue."),
            "f18.md")
        claims = _claim_statements(output)
        self.assertEqual(len(claims), 1)
        self.assertIn("DQ-555 governs this queue", claims[0])
        self.assertNotIn("DQ-777", claims[0])

    def test_render_segment_claims_carry_no_quarantined_heading_claim(self):
        output = _run(
            _quarantined_file("DQ-777 governs this queue"), "f01r.md")
        text = h.render_text(output, "render")
        section = text.split("Segment claims", 1)[-1]
        self.assertNotIn("DQ-777", section)

    def test_render_segment_claims_carry_the_body_claim_only(self):
        # Recovery correction, second holder: the first holder
        # form counted the Segment heading line of the section,
        # which names the quarantined heading as written,
        # outside CH-39. The claim lines themselves are the
        # charged surface, asserted here in exact form.
        output = _run(
            _quarantined_file(
                "DQ-777 governs this queue",
                extra_line="DQ-555 governs this queue."),
            "f18r.md")
        text = h.render_text(output, "render")
        section = text.split("Segment claims", 1)[-1]
        claim_lines = [line for line in section.splitlines()
                       if line.startswith("Claim, reported")
                       or line.startswith("Entries named")]
        joined = "\n".join(claim_lines)
        self.assertIn("DQ-555", joined)
        self.assertNotIn("DQ-777", joined)

    def test_governing_quarantined_heading_at_end_of_file_takes_no_note(self):
        data = (
            "# Decision queue\n"
            "\n"
            "### DQ-002: A sample open question\n"
            "\n"
            + _BANKED_BODY_999
            + "\n### DQ-00" + ZWSP + "1: DQ-777 governs this queue\n"
        )
        output = _run(data, "f24.md")
        self.assertEqual(_claim_statements(output), [])

    def test_governing_quarantined_heading_at_level_2_takes_no_note(self):
        output = _run(
            _quarantined_file("DQ-777 governs this queue",
                              heading_level=2),
            "f25.md")
        self.assertEqual(_claim_statements(output), [])

    def test_body_line_claim_in_quarantined_segment_still_reports(self):
        # Pin, the paper control f03: the same governing sentence
        # on a body line of the quarantined segment is reported.
        output = _run(
            _quarantined_file(
                "A plain title",
                extra_line="DQ-777 governs this queue."),
            "f03.md")
        claims = _claim_statements(output)
        self.assertTrue(claims)
        self.assertIn("DQ-777 governs this queue", claims[0])

    def test_fallback_claim_forms_on_quarantined_heading_take_no_note(self):
        # Pin: the CH-7 quarantine on the fallback path, cases
        # f04 and f05, stands before and after.
        for title in ("DQ-777 is settled", "DQ-777 stands closed"):
            with self.subTest(title=title):
                output = _run(_quarantined_file(title), "f04.md")
                self.assertEqual(_claim_statements(output), [])

    def test_valid_entry_heading_line_stays_a_citation_surface(self):
        # Pin, the CH-7 entry heading limb: a ghost number named
        # in the title of a valid entry heading is reported at
        # its heading line.
        data = (
            "# Decision queue\n"
            "\n"
            "### DQ-002: A sample open question\n"
            "\n"
            + _BANKED_BODY_999
            + "\n### DQ-005: DQ-777 governs this queue\n"
            "\n"
            + _BANKED_BODY_999
        )
        output = _run(data, "f19.md")
        named = [s for s in _statements(output)
                 if "DQ-777 is cited" in s]
        self.assertTrue(named)


class CitationContinuationTest(unittest.TestCase):
    """Seat 4 F-2: a citation token carrying a combining mark
    or a zero width character inside or after its digits is
    still read in part."""

    def test_framed_patterns_refuse_mark_and_format_continuations(self):
        for token in ("DQ-88" + ZWSP + "8",
                      "DQ-888" + ACUTE,
                      "DQ-888" + ZWSP,
                      "DQ-888" + "\u200c",
                      "DQ-888" + "\ufe0f"):
            with self.subTest(token=token):
                for pattern in validate._CITATION_PATTERNS:
                    self.assertIsNone(
                        pattern.search("See the note at " + token
                                       + " for context."),
                        "a framed pattern read a corrupted token")

    def test_plain_token_pattern_refuses_mark_and_format_continuations(self):
        for token in ("DQ-88" + ZWSP + "8",
                      "DQ-888" + ACUTE,
                      "DQ-888" + ZWSP):
            with self.subTest(token=token):
                self.assertIsNone(validate._DQ_TOKEN_RE.search(token))

    def test_inside_zero_width_token_manufactures_no_number_in_segment(self):
        output = _run(
            _quarantined_file(
                "A sample open question",
                extra_line="See the note at DQ-88" + ZWSP
                + "8 for context."),
            "f16.md")
        named = [s for s in _statements(output) if "DQ-088" in s]
        self.assertEqual(named, [])

    def test_inside_zero_width_token_manufactures_no_number_in_entry(self):
        data = (
            "# Decision queue\n"
            "\n"
            "### DQ-001: A sample open question\n"
            "\n"
            + _BANKED_BODY_999
            + "\nSee the note at DQ-88" + ZWSP + "8 for context.\n"
        )
        output = _run(data, "f22.md")
        named = [s for s in _statements(output) if "DQ-088" in s]
        self.assertEqual(named, [])

    def test_trailing_combining_mark_token_is_not_reported_in_segment(self):
        output = _run(
            _quarantined_file(
                "A sample open question",
                extra_line="See the note at DQ-888" + ACUTE
                + " for context."),
            "f14.md")
        named = [s for s in _statements(output) if "DQ-888" in s]
        self.assertEqual(named, [])

    def test_trailing_zero_width_token_is_not_reported_in_segment(self):
        output = _run(
            _quarantined_file(
                "A sample open question",
                extra_line="See the note at DQ-888" + ZWSP
                + " for context."),
            "f15.md")
        named = [s for s in _statements(output) if "DQ-888" in s]
        self.assertEqual(named, [])

    def test_trailing_combining_mark_token_is_not_reported_in_entry(self):
        data = (
            "# Decision queue\n"
            "\n"
            "### DQ-001: A sample open question\n"
            "\n"
            + _BANKED_BODY_999
            + "\nSee DQ-888" + ACUTE + " for the earlier ruling.\n"
        )
        output = _run(data, "f23.md")
        named = [s for s in _statements(output) if "DQ-888" in s]
        self.assertEqual(named, [])

    def test_full_stop_terminated_token_still_reports(self):
        # Pin and bound: a token closed by a full stop is a
        # legitimate terminator and stands outside the charge.
        output = _run(
            _quarantined_file(
                "A sample open question",
                extra_line="See the note at DQ-888. It stands."),
            "f21.md")
        named = [s for s in _statements(output) if "DQ-888" in s]
        self.assertTrue(named)

    def test_clean_ascii_token_still_reports(self):
        # Pin, the CH-24 clean token reports.
        output = _run(
            _quarantined_file(
                "A sample open question",
                extra_line="See the note at DQ-888 for context."),
            "clean.md")
        named = [s for s in _statements(output) if "DQ-888" in s]
        self.assertTrue(named)

    def test_mixed_script_tokens_stay_refused(self):
        # Pin, the CH-24 mixed script refusals, cases f12 and f13.
        for token in ("DQ-888" + "\u0668", "DQ-" + "\u0668" + "88"):
            with self.subTest(token=token):
                output = _run(
                    _quarantined_file(
                        "A sample open question",
                        extra_line="See the note at " + token
                        + " for context."),
                    "f12.md")
                named = [s for s in _statements(output)
                         if "DQ-888" in s]
                self.assertEqual(named, [])


_OPEN_COPY = (
    "### DQ-001: Alpha open copy\n"
    "\n"
    "Status: Open\n"
    "\n"
    "Question: Which option should we take?\n"
    "\n"
    "Options: Option A, Option B\n"
    "\n"
    "Cost of deciding late: Work stays blocked.\n"
    "\n"
    "Blocks: DQ-002\n"
    "\n"
    "This entry is waiting for a decision.\n"
)

_RULED_COPY = (
    "### DQ-001: Alpha ruled copy\n"
    "\n"
    "Status: RULED, closed\n"
    "\n"
    "Ruled by: Captain JP\n"
    "\n"
    "Ruling text: \"Decided.\"\n"
    "\n"
    "Ruling outcome: Decided in full.\n"
    "\n"
    "Where the ruling landed: the scratch file.\n"
)

_CLAIMER = (
    "### DQ-002: Beta question\n"
    "\n"
    "Status: Open\n"
    "\n"
    "Question: Which option should we take?\n"
    "\n"
    "Options: Option A, Option B\n"
    "\n"
    "Cost of deciding late: Work stays blocked.\n"
    "\n"
    "Blocks: DQ-001\n"
    "\n"
    "DQ-001 is still open.\n"
    "\n"
    "This second entry is waiting for a decision.\n"
)


class ClaimNoteCopyListTest(unittest.TestCase):
    """Seat 6 Finding 1: at three or more copies with a repeated
    state, the claim Note lists each distinct state once while
    stating one for each standing copy."""

    def _claim_statement(self, copies, name):
        data = "# Decision queue\n\n" + "\n".join(copies) \
            + "\n" + _CLAIMER
        output = _run(data, name)
        for statement in _claim_statements(output):
            if "about the state of DQ-001" in statement:
                return statement
        raise AssertionError("no claim Note stands in " + name)

    def test_three_copies_open_ruled_open_list_each_copy(self):
        statement = self._claim_statement(
            [_OPEN_COPY, _RULED_COPY, _OPEN_COPY], "g13.md")
        self.assertIn(
            "are Open, Ruled and Open, one for each standing copy.",
            statement)

    def test_three_copies_ruled_open_ruled_list_each_copy(self):
        statement = self._claim_statement(
            [_RULED_COPY, _OPEN_COPY, _RULED_COPY], "h01.md")
        self.assertIn(
            "are Ruled, Open and Ruled, one for each standing copy.",
            statement)

    def test_four_copies_list_each_copy(self):
        statement = self._claim_statement(
            [_OPEN_COPY, _RULED_COPY, _OPEN_COPY, _RULED_COPY],
            "h02.md")
        self.assertIn(
            "are Open, Ruled, Open and Ruled, one for each "
            "standing copy.", statement)

    def test_three_copies_open_open_ruled_list_each_copy(self):
        statement = self._claim_statement(
            [_OPEN_COPY, _OPEN_COPY, _RULED_COPY], "h03.md")
        self.assertIn(
            "are Open, Open and Ruled, one for each standing copy.",
            statement)

    def test_two_copies_open_first_form_stands_exact(self):
        # Pin, the CH-7 two copy form the cure is exact on.
        statement = self._claim_statement(
            [_OPEN_COPY, _RULED_COPY], "c03.md")
        self.assertIn(
            "are Open and Ruled, one for each standing copy.",
            statement)

    def test_two_copies_ruled_first_form_stands_exact(self):
        # Pin, the CH-7 two copy form in the other order.
        statement = self._claim_statement(
            [_RULED_COPY, _OPEN_COPY], "c04.md")
        self.assertIn(
            "are Ruled and Open, one for each standing copy.",
            statement)

    def test_same_state_thrice_takes_the_singular_form(self):
        # Pin, the singular same state form, case g14.
        statement = self._claim_statement(
            [_OPEN_COPY, _OPEN_COPY, _OPEN_COPY], "g14.md")
        self.assertIn(
            "The derived state of DQ-001 in this run is Open.",
            statement)


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


class GhostWasFormTest(unittest.TestCase):
    """Seat 7 S17-ATK3-7-02: a ghost number named as the subject
    of a closure on the entry own Status line, in was form, is
    read by no scan."""

    def _ghost_notes(self, status_value, name):
        data = _DECIDED_SKELETON % (
            312, "Ghost probe", status_value, 312, 312, 312)
        output = _run(data, name)
        return [s for s in _statements(output)
                if "DQ-999 is cited" in s]

    def test_was_closed_on_the_status_line_is_reported_once(self):
        notes = self._ghost_notes(
            "RULED, closed. DQ-999 was closed.", "g02.md")
        self.assertEqual(len(notes), 1)

    def test_was_settled_on_the_status_line_is_reported_once(self):
        notes = self._ghost_notes(
            "RULED, closed. DQ-999 was settled.", "g02b.md")
        self.assertEqual(len(notes), 1)

    def test_was_ruled_on_the_status_line_is_reported_once(self):
        notes = self._ghost_notes(
            "RULED, closed. DQ-999 was ruled.", "g02c.md")
        self.assertEqual(len(notes), 1)

    def test_verb_first_forms_on_the_status_line_stay_reported(self):
        # Pins, the cured forms of the round 2 charge: Closes in
        # capital form, settles in lower case, and the question
        # for form each take exactly one Note.
        for status_value in (
                "RULED, closed (closes DQ-999)",
                "RULED, closed (settles DQ-999)",
                "RULED, closed (question for DQ-999)"):
            with self.subTest(status_value=status_value):
                notes = self._ghost_notes(status_value, "g03.md")
                self.assertEqual(len(notes), 1)


class ClaimVerbCaseTest(unittest.TestCase):
    """Seat 7 S17-ATK3-7-03: decision evidence naming a headed
    entry with a lower case verb first form takes no claim
    Note."""

    def _evidence_file(self, ruling_text, claimer_number,
                       target_number):
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

    def test_lower_case_settle_in_ruling_text_takes_a_claim_note(self):
        output = _run(
            self._evidence_file("settle DQ-332 as follows.", 331, 332),
            "c06.md")
        claims = [s for s in _claim_statements(output)
                  if "about the state of DQ-332" in s]
        self.assertTrue(claims)

    def test_lower_case_decide_in_ruling_text_takes_a_claim_note(self):
        output = _run(
            self._evidence_file("decide DQ-334 as follows.", 333, 334),
            "c06b.md")
        claims = [s for s in _claim_statements(output)
                  if "about the state of DQ-334" in s]
        self.assertTrue(claims)

    def test_capitalised_settle_in_ruling_text_still_takes_a_note(self):
        # Pin, the cured capitalised form of round 2.
        output = _run(
            self._evidence_file("Settle DQ-332 as follows.", 331, 332),
            "n29.md")
        claims = [s for s in _claim_statements(output)
                  if "about the state of DQ-332" in s]
        self.assertTrue(claims)

    def test_was_decided_evidence_form_still_takes_a_note(self):
        # Pin, case c07 of the round 3 paper.
        output = _run(
            self._evidence_file("DQ-332 was decided.", 331, 332),
            "c07.md")
        claims = [s for s in _claim_statements(output)
                  if "about the state of DQ-332" in s]
        self.assertTrue(claims)

    def test_has_been_decided_evidence_form_still_takes_a_note(self):
        # Pin, case c08 of the round 3 paper.
        output = _run(
            self._evidence_file("DQ-332 has been decided.", 331, 332),
            "c08.md")
        claims = [s for s in _claim_statements(output)
                  if "about the state of DQ-332" in s]
        self.assertTrue(claims)


class ClaimTenseFormsTest(unittest.TestCase):
    """Seat 7 S17-ATK3-7-05: cross entry state claims in the
    has closed, got ruled, and bare closed past forms take no
    claim Note."""

    def _claim_file(self, claimer_number, claim_sentence,
                    target_number):
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

    def _claims_about(self, data, name, target_number):
        output = _run(data, name)
        return [s for s in _claim_statements(output)
                if "about the state of DQ-%03d" % target_number in s]

    def test_has_closed_takes_a_claim_note(self):
        claims = self._claims_about(
            self._claim_file(323, "DQ-324 has closed.", 324),
            "c02.md", 324)
        self.assertTrue(claims)

    def test_has_ruled_takes_a_claim_note(self):
        claims = self._claims_about(
            self._claim_file(323, "DQ-324 has ruled.", 324),
            "c02b.md", 324)
        self.assertTrue(claims)

    def test_got_ruled_takes_a_claim_note(self):
        claims = self._claims_about(
            self._claim_file(325, "DQ-326 got ruled and closed.", 326),
            "c03.md", 326)
        self.assertTrue(claims)

    def test_got_closed_takes_a_claim_note(self):
        claims = self._claims_about(
            self._claim_file(325, "DQ-326 got closed.", 326),
            "c03b.md", 326)
        self.assertTrue(claims)

    def test_bare_closed_past_takes_a_claim_note(self):
        claims = self._claims_about(
            self._claim_file(337, "DQ-338 closed yesterday.", 338),
            "c09.md", 338)
        self.assertTrue(claims)

    def test_bare_ruled_past_takes_a_claim_note(self):
        claims = self._claims_about(
            self._claim_file(337, "DQ-338 ruled yesterday.", 338),
            "c09b.md", 338)
        self.assertTrue(claims)

    def test_was_settled_form_still_takes_a_claim_note(self):
        # Pin, case c04 of the round 3 paper.
        claims = self._claims_about(
            self._claim_file(323, "DQ-324 was settled.", 324),
            "c04.md", 324)
        self.assertTrue(claims)

    def test_future_progressive_and_gerund_forms_take_no_note(self):
        # Bound, paper observation O-4: none of these states a
        # present or past decided state, and none is charged.
        for sentence in ("DQ-324 will be ruled and closed.",
                         "DQ-324 is being ruled.",
                         "Closing DQ-324 now."):
            with self.subTest(sentence=sentence):
                claims = self._claims_about(
                    self._claim_file(323, sentence, 324),
                    "o4.md", 324)
                self.assertEqual(claims, [])


if __name__ == "__main__":
    unittest.main()
