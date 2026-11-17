"""Restart Step 17 fix wave 2 closing, Defect Repair Seat D1 tests.

Defect: on the wave 2 cured tree, 25 Step 16 pins fail on one
shared form: the run returns a rule 5 "no decider is recorded"
finding where the Step 16 pin expects no decider finding. The
moving hunk is the CH-6 decider limb in _check5 in validate.py:
the wave 2 cure replaced the standing body reading, the verb
form (Ruled, Settled, or Decided) followed by "by" ending at a
word boundary, with a same line reading requiring an optional
single colon, whitespace, and a non space character after
"by". That same line reading takes none of the boundary
character forms the Step 16 seats pinned as accepted by the
check: punctuation standing between "by" and the decider name,
punctuation followed by a non breaking space, doubled and
triple separators, punctuation standing directly against the
name, and the line break after "by".

These pins stand in both directions at that one locus. The
Step 16 direction: every bound form below records a decider,
so no rule 5 decider finding stands. The wave 2 direction:
the CH-6 charged form, the bare field line "Ruled by:" with
an empty value, and its Settled and Decided counterparts,
record no decider, so the decider finding stands, and the
full evidence form records every presence item. The verb
anchor guards stand in both directions: a boundary character
after a verb the check does not accept records no decider.

Copyright: J.P. Picard aka Macro-Harder
"""

import unittest

import dqv_harness as h


def _entry(entry_id, extra_paragraphs):
    text = (
        "# Decision queue\n"
        "\n"
        "### %s: the unnamed ruling\n"
        "\n"
        "Status: Banked\n"
        "\n"
        "%s\n"
        "\n"
        "Ruling text: \"The note takes the short form.\"\n"
        "\n"
        "Ruling outcome: The short form stands.\n"
        "\n"
        "Where the ruling landed: NOTES.md section 2.\n"
        "\n"
        "Status: RULED, closed. This item is ruled.\n"
    ) % (entry_id, "\n\n".join(extra_paragraphs))
    return text.encode("utf-8")


def _pipeline(data, name="probe.md"):
    _model, output = h.run_pipeline(data, name=name)
    if output is None:
        raise AssertionError("pipeline returned a failure result")
    return output


def _decider_findings(output, entry_id):
    found = []
    for finding in h.findings_for(output, entry_id=entry_id, rule=5):
        statement = h.finding_statement(finding) or ""
        if "No decider is recorded" in statement:
            found.append(finding)
    return found


def _rule5_statements(output, entry_id):
    return [h.finding_statement(f)
            for f in h.findings_for(output, entry_id=entry_id, rule=5)]


class Step16BoundFormsRecordDeciderTest(unittest.TestCase):
    """The Step 16 bound forms record a decider at the
    _check5 decider limb: no rule 5 decider finding stands
    for any of them."""

    def _assert_recorded(self, data, entry_id):
        output = _pipeline(data)
        self.assertEqual(_decider_findings(output, entry_id), [])

    def test_comma_space_captain_records(self):
        self._assert_recorded(_entry("DQ-3001", (
            "Ruled by, Captain JP in the roles chat.",)), "DQ-3001")

    def test_doubled_colon_space_captain_records(self):
        self._assert_recorded(_entry("DQ-3002", (
            "Ruled by:: Captain JP in the roles chat.",)), "DQ-3002")

    def test_comma_nbsp_captain_records(self):
        self._assert_recorded(_entry("DQ-3003", (
            "Ruled by,\u00a0Captain JP in the roles chat.",)),
            "DQ-3003")

    def test_doubled_colon_nbsp_manager_records(self):
        self._assert_recorded(_entry("DQ-3004", (
            "Settled by::\u00a0the Manager in the roles chat.",)),
            "DQ-3004")

    def test_semicolon_nbsp_clerk_records(self):
        self._assert_recorded(_entry("DQ-3005", (
            "Decided by;\u00a0the Clerk in the roles chat.",)),
            "DQ-3005")

    def test_full_stop_nbsp_captain_records(self):
        self._assert_recorded(_entry("DQ-3006", (
            "Ruled by.\u00a0Captain JP in the roles chat.",)),
            "DQ-3006")

    def test_doubled_comma_space_records(self):
        self._assert_recorded(_entry("DQ-3007", (
            "Ruled by,, Captain JP in the roles chat.",)), "DQ-3007")

    def test_triple_colon_space_records(self):
        self._assert_recorded(_entry("DQ-3008", (
            "Ruled by::: Captain JP in the roles chat.",)), "DQ-3008")

    def test_comma_against_name_records(self):
        self._assert_recorded(_entry("DQ-3009", (
            "Ruled by,Captain JP in the roles chat.",)), "DQ-3009")

    def test_parenthesis_after_by_records(self):
        self._assert_recorded(_entry("DQ-3010", (
            "Ruled by(Captain JP in the roles chat.",)), "DQ-3010")

    def test_linebreak_after_by_records(self):
        self._assert_recorded(_entry("DQ-3011", (
            "Settled by\nthe Manager in the roles chat.",)),
            "DQ-3011")

    def test_hyphen_against_name_records(self):
        self._assert_recorded(_entry("DQ-3012", (
            "Ruled by-Captain JP in the roles chat.",)), "DQ-3012")

    def test_slash_against_name_records(self):
        self._assert_recorded(_entry("DQ-3013", (
            "Ruled by/Captain JP in the roles chat.",)), "DQ-3013")

    def test_en_dash_against_name_records(self):
        self._assert_recorded(_entry("DQ-3014", (
            "Settled by\u2013the Manager in the roles chat.",)),
            "DQ-3014")

    def test_comma_named_clerk_records(self):
        self._assert_recorded(_entry("DQ-3015", (
            "Decided by, the Clerk in the roles chat.",)), "DQ-3015")

    def test_value_wrapped_to_next_line_records(self):
        self._assert_recorded(_entry("DQ-3016", (
            "Ruled by:\nCaptain JP in the roles chat.",)), "DQ-3016")


class Wave2ChargedFormsKeepCuredOutcomeTest(unittest.TestCase):
    """The wave 2 charged constructions at the same locus
    keep their cured outcomes: a bare decider field line
    with an empty value records no decider."""

    def test_all_four_empty_labels_take_presence_findings(self):
        data = (
            "# Decision queue\n"
            "\n"
            "### DQ-3020: Empty evidence labels\n"
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
        ).encode("utf-8")
        output = _pipeline(data, "d1n01.md")
        joined = "\n".join(_rule5_statements(output, "DQ-3020"))
        self.assertIn("No decider is recorded", joined)
        self.assertIn("No ruling text is recorded", joined)
        self.assertIn("No outcome is recorded", joined)
        self.assertIn("No landing record is recorded", joined)

    def test_bare_settled_by_line_records_no_decider(self):
        data = (
            "# Decision queue\n"
            "\n"
            "### DQ-3021: Bare settled label\n"
            "\n"
            "Status: RULED, closed\n"
            "\n"
            "Settled by:\n"
            "\n"
            "Ruling text: \"The note takes the short form.\"\n"
            "\n"
            "Ruling outcome: The short form stands.\n"
            "\n"
            "Where the ruling landed: NOTES.md section 2.\n"
        ).encode("utf-8")
        output = _pipeline(data, "d1bare1.md")
        self.assertEqual(
            len(_decider_findings(output, "DQ-3021")), 1)

    def test_bare_decided_by_line_records_no_decider(self):
        data = (
            "# Decision queue\n"
            "\n"
            "### DQ-3022: Bare decided label\n"
            "\n"
            "Status: RULED, closed\n"
            "\n"
            "Decided by:\n"
            "\n"
            "Ruling text: \"The note takes the short form.\"\n"
            "\n"
            "Ruling outcome: The short form stands.\n"
            "\n"
            "Where the ruling landed: NOTES.md section 2.\n"
        ).encode("utf-8")
        output = _pipeline(data, "d1bare2.md")
        self.assertEqual(
            len(_decider_findings(output, "DQ-3022")), 1)

    def test_full_evidence_values_take_no_presence_finding(self):
        data = (
            "# Decision queue\n"
            "\n"
            "### DQ-3023: Full evidence\n"
            "\n"
            "Status: RULED, closed\n"
            "\n"
            "Ruled by: Captain JP\n"
            "\n"
            "Ruling text: \"The note takes the short form.\"\n"
            "\n"
            "Ruling outcome: The short form stands.\n"
            "\n"
            "Where the ruling landed: NOTES.md section 2.\n"
        ).encode("utf-8")
        output = _pipeline(data, "d1full.md")
        self.assertEqual(_rule5_statements(output, "DQ-3023"), [])


class VerbAnchorGuardTest(unittest.TestCase):
    """A boundary character at this position creates no
    acceptance where the verb stands in no form the check
    accepts, in either direction of the narrowing."""

    def _assert_not_recorded(self, data, entry_id):
        output = _pipeline(data)
        self.assertEqual(
            len(_decider_findings(output, entry_id)), 1)

    def test_mentioned_by_comma_stays_not_recorded(self):
        self._assert_not_recorded(_entry("DQ-3030", (
            "Mentioned by, the Manager in the roles chat.",)),
            "DQ-3030")

    def test_bare_nbsp_captain_no_verb_stays_not_recorded(self):
        self._assert_not_recorded(_entry("DQ-3031", (
            "This item was settled by\u00a0Captain JP in the "
            "roles chat, and the grant record stands in the "
            "chat.",)), "DQ-3031")

    def test_no_decider_entry_stays_not_recorded(self):
        self._assert_not_recorded(_entry("DQ-3032", ()), "DQ-3032")


if __name__ == "__main__":
    unittest.main()
