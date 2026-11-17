"""Restart Step 17 fix wave 2, Seat K6 tests.

Charges CH-6 (validate, decided entry presence tests on value:
S17-ATK2-7-01 merged with S17-ATK2-17-05), CH-7 (validate, the
ghost and claim scans: seat 4 F-1, seat 6 Finding 2 as its own
duplicate keying limb, S17-ATK2-7-04, 05, 06, 07, 08), and CH-8
(validate, closing prose derivation width: S17-ATK2-7-02 merged
with A2-10-F1). Constructions are the finding papers own
constructions, rebuilt inline from the attack scratch files.
The cure stands in decision_queue_validator/validate.py only.
"""

import unittest

import dqv_harness as h


def _run(data, name):
    _model, output = h.run_pipeline(data.encode("utf-8"), name)
    if output is None:
        raise AssertionError("pipeline returned a failure for " + name)
    return output


def _statements(output, entry_id=None):
    return [h.finding_statement(f)
            for f in h.findings_of(output)
            if entry_id is None
            or h.finding_entry_id(f) == entry_id]


def _rule5_statements(output, entry_id):
    return [h.finding_statement(f)
            for f in h.findings_for(output, entry_id=entry_id, rule=5)]


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

_DECIDED_SKELETON = (
    "# Decision queue\n"
    "\n"
    "### DQ-%03d: %s\n"
    "\n"
    "Status: RULED, closed\n"
    "\n"
    "Ruled by: Captain JP\n"
    "\n"
    "Ruling text: \"Settle DQ-%03d as follows.\"\n"
    "\n"
    "Ruling outcome: DQ-%03d is decided and closed.\n"
    "\n"
    "Where the ruling landed: NOWHERE.md, sample rule.\n"
    "\n"
    "%s"
    "\n"
    "Ruled: DQ-%03d is closed by this ruling. Closed.\n"
)


def _decided(number, title, block_heading):
    return _DECIDED_SKELETON % (
        number, title, number, number, block_heading, number)


class Ch6PresenceOnValueTest(unittest.TestCase):
    """CH-6: the decided entry presence tests of _check5 are
    satisfied by the label standing in the body text, where the
    open entry field tests test presence on the value."""

    def test_all_four_empty_evidence_labels_take_presence_findings(self):
        # S17-ATK2-7-01, construction n01.
        data = (
            "# Decision queue\n"
            "\n"
            "### DQ-201: Empty evidence labels\n"
            "\n"
            "Status: RULED, closed\n"
            "\n"
            "Ruled by:\n"
            "\n"
            "Ruling text:\n"
            "\n"
            "Ruling outcome:\n"
            "\n"
            "Where the ruling landed:\n"
        )
        output = _run(data, "n01.md")
        statements = _rule5_statements(output, "DQ-201")
        joined = "\n".join(statements)
        self.assertIn("No decider is recorded", joined)
        self.assertIn("No ruling text is recorded", joined)
        self.assertIn("No outcome is recorded", joined)
        self.assertIn("No landing record is recorded", joined)

    def test_empty_landing_label_alone_takes_the_landing_finding(self):
        # S17-ATK2-17-05, construction d15: a real decider line
        # and a real ruling text value stand beside the bare
        # landing label; the outcome is genuinely absent.
        data = (
            "# Decision queue\n"
            "\n"
            "### DQ-001: A sample decided question\n"
            "\n"
            "Status: Banked\n"
            "\n"
            "This question was waiting for a decision.\n"
            "\n"
            "Ruled by: Captain JP, option A stands.\n"
            "\n"
            "Ruling text: Option A stands.\n"
            "\n"
            "Where the ruling landed:\n"
        )
        output = _run(data, "d15.md")
        statements = _rule5_statements(output, "DQ-001")
        joined = "\n".join(statements)
        self.assertIn("No landing record is recorded", joined)
        self.assertIn("No outcome is recorded", joined)
        self.assertNotIn("No ruling text is recorded", joined)

    def test_empty_labels_beside_a_ruled_paragraph_take_landing(self):
        # S17-ATK2-17-05, construction d11: the ruling text
        # stands in the Ruled paragraph form; the empty Ruling
        # text and landing labels record nothing.
        data = (
            "# Decision queue\n"
            "\n"
            "### DQ-001: A sample decided question\n"
            "\n"
            "Status: Banked\n"
            "\n"
            "This question was waiting for a decision.\n"
            "\n"
            "Ruled: The Manager ruled option A stands.\n"
            "\n"
            "Ruling text:\n"
            "\n"
            "Where the ruling landed:\n"
        )
        output = _run(data, "d11.md")
        statements = _rule5_statements(output, "DQ-001")
        joined = "\n".join(statements)
        self.assertIn("No landing record is recorded", joined)

    def test_full_evidence_values_take_no_presence_finding(self):
        # Guard: the same skeleton with every value filled
        # stands clean on rule 5, before and after the cure.
        data = _decided(202, "Full evidence", "#### Ruling by Captain JP")
        output = _run(data, "full.md")
        self.assertEqual(_rule5_statements(output, "DQ-202"), [])


class Ch7SegmentClaimQuarantineTest(unittest.TestCase):
    """CH-7, seat 4 F-1: the supplementary cure quarantines the
    heading line of an unmatched segment for citations but not
    for claims; the claim scan manufactures a claim about
    DQ-000 from the quarantined heading line."""

    _HEAD = (
        "# Decision queue\n"
        "\n"
        "### DQ-002: A sample open question\n"
        "\n"
        + _BANKED_BODY.replace("Blocks: DQ-002", "Blocks: DQ-999")
        + "A plain paragraph of context for this entry.\n"
        "\n"
        "### DQ-00\u200b1: %s\n"
        "\n"
        + _BANKED_BODY.replace("Blocks: DQ-002", "Blocks: DQ-999")
        + "A plain paragraph of context for this entry.\n"
    )

    def test_quarantined_heading_claim_names_no_dq000(self):
        output = _run(self._HEAD % "DQ-777 was ruled and closed",
                      "e7b.md")
        for statement in _statements(output):
            self.assertNotIn("DQ-000", statement)

    def test_quarantined_heading_claim_names_no_dq000_render(self):
        output = _run(self._HEAD % "DQ-002 was ruled and closed",
                      "e7c.md")
        text = h.render_text(output, "render")
        self.assertNotIn("DQ-000", text)

    def test_body_line_claim_in_quarantined_segment_still_reports(self):
        # Guard, the paper control e8: the same claim sentence
        # on a body line of the segment is reported, naming
        # DQ-777, before and after the cure.
        data = self._HEAD % "A plain title"
        data = data.replace(
            "A plain paragraph of context for this entry.\n",
            "A plain paragraph of context for this entry.\n", 1)
        data += ""
        body_claim = (
            "# Decision queue\n"
            "\n"
            "### DQ-002: A sample open question\n"
            "\n"
            + _BANKED_BODY.replace("Blocks: DQ-002", "Blocks: DQ-999")
            + "A plain paragraph of context for this entry.\n"
            "\n"
            "### DQ-00\u200b1: A plain title\n"
            "\n"
            + _BANKED_BODY.replace("Blocks: DQ-002", "Blocks: DQ-999")
            + "DQ-777 was ruled and closed.\n"
        )
        output = _run(body_claim, "e8.md")
        joined = "\n".join(_statements(output))
        self.assertIn("about DQ-777", joined)


class Ch7DuplicateKeyingTest(unittest.TestCase):
    """CH-7, seat 6 Finding 2, its own limb: where a duplicated
    number carries two states, the stale claim Note states one
    derived state for the number, chosen by file order."""

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
        "Ruling text: \"Alpha is decided.\"\n"
        "\n"
        "Ruling outcome: Alpha is decided in full.\n"
        "\n"
        "Where the ruling landed: the scratch file, alpha section.\n"
    )
    _CLAIMER = (
        "### DQ-002: Beta question\n"
        "\n"
        "Status: Open\n"
        "\n"
        "Question: Which other option should we take?\n"
        "\n"
        "Options: Option C, Option D\n"
        "\n"
        "Cost of deciding late: Other work stays blocked.\n"
        "\n"
        "Blocks: DQ-001\n"
        "\n"
        "DQ-001 is still open.\n"
        "\n"
        "This second entry is waiting for a decision.\n"
    )

    def _claim_statement(self, first, second, name):
        data = ("# Decision queue\n\n" + first + "\n" + second
                + "\n" + self._CLAIMER)
        output = _run(data, name)
        for statement in _statements(output, "DQ-002"):
            if "records a claim about the state of DQ-001" in statement:
                return statement
        raise AssertionError("no claim Note stands in " + name)

    def test_open_first_order_states_both_copy_states(self):
        statement = self._claim_statement(
            self._OPEN_COPY, self._RULED_COPY, "c03.md")
        self.assertNotIn(
            "The derived state of DQ-001 in this run is Ruled.",
            statement)
        self.assertIn("Open", statement)
        self.assertIn("Ruled", statement)

    def test_ruled_first_order_states_both_copy_states(self):
        statement = self._claim_statement(
            self._RULED_COPY, self._OPEN_COPY, "c04.md")
        self.assertNotIn(
            "The derived state of DQ-001 in this run is Open.",
            statement)
        self.assertIn("Open", statement)
        self.assertIn("Ruled", statement)


class Ch7GhostScanTest(unittest.TestCase):
    """CH-7, S17-ATK2-7-04, 05, 06: ghost numbers on the entry
    own Status line in verb form, in a decision block heading,
    and in an entry heading title are read by no scan."""

    def test_ghost_in_verb_form_on_the_status_line_is_reported(self):
        data = _decided(202, "Ghost on the status line",
                        "#### Ruling by Captain JP")
        data = data.replace(
            "Status: RULED, closed\n",
            "Status: RULED, closed (closes DQ-999)\n", 1)
        data = data.replace("Settle DQ-202 as follows.",
                            "Settle DQ-202 as follows.")
        output = _run(data, "n02.md")
        joined = "\n".join(_statements(output))
        self.assertIn("DQ-999 is cited", joined)

    def test_ghost_in_a_decision_block_heading_is_reported(self):
        data = _decided(
            204, "Ghost in the block heading",
            "#### Ruling by Captain JP: DQ-999 is closed")
        output = _run(data, "n04.md")
        joined = "\n".join(_statements(output))
        self.assertIn("DQ-999 is cited", joined)

    def test_ghost_in_an_entry_heading_title_is_reported(self):
        data = _decided(203, "Ruling that closes DQ-999",
                        "#### Ruling by Captain JP")
        output = _run(data, "n03.md")
        joined = "\n".join(_statements(output))
        self.assertIn("DQ-999 is cited", joined)

    def test_ghost_in_a_block_body_sentence_stays_exactly_once(self):
        # Guard, the round 1 case F form: a ghost named as the
        # subject of the entry own ruling in a body sentence
        # takes exactly one PD-R7 Note, before and after.
        data = _decided(205, "Ghost in the body",
                        "#### Ruling by Captain JP")
        data = data.replace(
            "Ruling outcome: DQ-205 is decided and closed.",
            "Ruling outcome: DQ-999 is closed.")
        output = _run(data, "caseF.md")
        notes = [s for s in _statements(output)
                 if "DQ-999 is cited" in s]
        self.assertEqual(len(notes), 1)


class Ch7CrossEntryClaimTest(unittest.TestCase):
    """CH-7, S17-ATK2-7-07 and 08: decision evidence naming a
    headed entry as the subject of the ruling, and cross entry
    state claims in past tense forms, take no finding."""

    def test_evidence_naming_a_headed_entry_takes_a_claim_note(self):
        data = _decided(237, "Ruling text names a real entry",
                        "#### Ruling by Captain JP")
        data = data.replace("Settle DQ-237 as follows.",
                            "Settle DQ-238 as follows.")
        data = data.replace("DQ-237 is decided and closed.",
                            "DQ-238 is decided in full.")
        data += (
            "\n### DQ-238: An ordinary banked entry\n"
            "\n"
            + _BANKED_BODY
            + "This question is waiting for a decision.\n"
        )
        output = _run(data, "n29.md")
        joined = "\n".join(_statements(output))
        self.assertIn(
            "records a claim about the state of DQ-238", joined)

    def _claim_file(self, number, claimer_title, claim, target):
        return (
            "# Decision queue\n"
            "\n"
            "### DQ-%03d: %s\n"
            "\n"
            % (number, claimer_title)
            + _BANKED_BODY
            + "This question is waiting for a decision. %s\n"
            % claim
            + "\n### DQ-%03d: An ordinary banked entry\n"
            "\n"
            % target
            + _BANKED_BODY
            + "This question is waiting for a decision.\n"
        )

    def test_was_form_claim_takes_a_claim_note(self):
        data = self._claim_file(
            208, "Claims another entry was closed",
            "DQ-209 was ruled and closed yesterday.", 209)
        output = _run(data, "n07.md")
        joined = "\n".join(_statements(output))
        self.assertIn(
            "records a claim about the state of DQ-209", joined)

    def test_has_been_form_claim_takes_a_claim_note(self):
        data = self._claim_file(
            210, "Claims another entry has been closed",
            "DQ-211 has been ruled and closed.", 211)
        output = _run(data, "n08.md")
        joined = "\n".join(_statements(output))
        self.assertIn(
            "records a claim about the state of DQ-211", joined)


class Ch8ClosingProseWidthTest(unittest.TestCase):
    """CH-8, S17-ATK2-7-02: the closing prose cure reads two
    fixed phrases only; neighbouring plain words stating the
    same contradiction still derive Open."""

    def _prose_file(self, number, paragraph):
        return (
            "# Decision queue\n"
            "\n"
            "### DQ-%03d: Banked head, closed body\n"
            "\n"
            % number
            + _BANKED_BODY
            + "This question is waiting for a decision.\n"
            "\n"
            + paragraph + "\n"
        )

    def test_neighbouring_closing_prose_phrasings_do_not_derive_open(self):
        cases = (
            (212, "This entry was decided by Captain JP yesterday "
                  "and is now closed. Nothing remains open on it."),
            (213, "This entry was ruled by Captain JP yesterday "
                  "and closed in full. Nothing remains open on it."),
            (214, "This entry has been ruled by Captain JP and "
                  "has now been closed. Nothing remains open on it."),
            (215, "This entry was ruled yesterday and is now "
                  "closed. Nothing remains open on it."),
        )
        for number, paragraph in cases:
            with self.subTest(number=number):
                output = _run(
                    self._prose_file(number, paragraph),
                    "n%03d.md" % number)
                entry = h.entry_by_id(output, "DQ-%03d" % number)
                self.assertEqual(h.entry_state(entry), "Ambiguous")


class Ch8BareClosingSentenceTest(unittest.TestCase):
    """CH-8, A2-10-F1: a closing sentence in the form It is
    closed. overrides a RULED tail heading, at the edge of the
    bare closing sentence cure."""

    _TAIL = (
        "# Decision queue\n"
        "\n"
        "## DQ-001: the harbour light rota. "
        "RULED by Captain JP 2026-11-15\n"
        "\n"
        "The harbour light rota was drawn up by the Clerk from "
        "the winter watch list, and the rota names the keeper "
        "for each night of the week in a single table at the "
        "end of the note. %s\n"
    )

    def test_it_is_closed_confirms_the_ruled_heading(self):
        output = _run(self._TAIL % "It is closed.", "f1g.md")
        entry = h.entry_by_id(output, "DQ-001")
        self.assertEqual(h.entry_state(entry), "Ruled")

    def test_bare_closed_still_confirms_the_ruled_heading(self):
        # Guard: the cured form itself, before and after.
        output = _run(self._TAIL % "Closed.", "f1guard.md")
        entry = h.entry_by_id(output, "DQ-001")
        self.assertEqual(h.entry_state(entry), "Ruled")


if __name__ == "__main__":
    unittest.main()
