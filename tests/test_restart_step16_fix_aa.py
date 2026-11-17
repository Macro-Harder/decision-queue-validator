"""Restart Step 16 fix wave 9, Fix seat AA tests.

Seat AA owns finding A9-8-2 (Low) of Auditor 8,
confirmation round 9 (design/steps/step-16r-audit9-8.md,
section 5 and its findings list), triaged at step record
section 30 (design/steps/step-16r-record.md), register
items 16R-138 and 16R-141: the entry group listing denies
a decider the rule 5 decider check accepts, where a cured
punctuation separator standing between "by" and the
decider name is followed by a non breaking space in place
of a whitespace of the standing class.

Fix Seat Y (design/steps/step-16r-fix8-y.md) took the
non breaking space in its colon branch's whitespace slot
and took the comma, semicolon and full stop branches, and
the doubled colon branch, with one whitespace of the
standing class after the punctuation. The combination,
the punctuation branch's whitespace slot filled by the
non breaking space, stood in no step. Auditor 8 evidences
eight combinations, each with the presence decider true
and no decider Error standing, while both subcommands
print "Decider: decider not recorded": a doubled colon
followed by a non breaking space in the Captain phrase,
the Manager phrase and the named Clerk phrase; a comma
followed by a non breaking space in the Captain phrase
and the Manager phrase; a semicolon followed by a non
breaking space in the Captain phrase and the named Clerk
phrase; and a full stop followed by a non breaking space
in the Captain phrase.

The tests below pin the cured behaviour, written before
the cure. The eight evidenced variant tests fail before
the cure and pass after it: each prints its decider label
on both subcommands where the listing prints, with no
decider Error. The guard tests pass before and after: the
standing forms Fix Seats U, W and Y cured keep printing
their labels; doubled separators generally, a triple
colon, punctuation standing directly against the name
and a parenthesis at this position keep standing denied
by the listing in the form the bound leaves; the heading
step keeps standing not widened; the verb anchor on the
Captain branch keeps holding, so a bare "by" form and a
mentioned by form carrying a new combination stay denied
by both sides; and the corpus pin guards stand.

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


def _heading_entry(entry_id, heading_suffix, body_paragraph):
    text = (
        "# Decision queue\n"
        "\n"
        "### %s: %s\n"
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
    ) % (entry_id, heading_suffix, body_paragraph)
    return text.encode("utf-8")


DOUBLED_COLON_NBSP_CAPTAIN_FORM = _entry("DQ-1050", (
    "Ruled by::\u00a0Captain JP in the roles chat.",
))


DOUBLED_COLON_NBSP_MANAGER_FORM = _entry("DQ-1051", (
    "Settled by::\u00a0the Manager in the roles chat.",
))


DOUBLED_COLON_NBSP_CLERK_FORM = _entry("DQ-1052", (
    "Decided by::\u00a0the Clerk in the roles chat.",
))


COMMA_NBSP_CAPTAIN_FORM = _entry("DQ-1053", (
    "Ruled by,\u00a0Captain JP in the roles chat.",
))


COMMA_NBSP_MANAGER_FORM = _entry("DQ-1054", (
    "Settled by,\u00a0the Manager in the roles chat.",
))


SEMICOLON_NBSP_CAPTAIN_FORM = _entry("DQ-1055", (
    "Ruled by;\u00a0Captain JP in the roles chat.",
))


SEMICOLON_NBSP_CLERK_FORM = _entry("DQ-1056", (
    "Decided by;\u00a0the Clerk in the roles chat.",
))


FULL_STOP_NBSP_CAPTAIN_FORM = _entry("DQ-1057", (
    "Ruled by.\u00a0Captain JP in the roles chat.",
))


SPACE_MANAGER_FORM = _entry("DQ-1060", (
    "Settled by the Manager in the roles chat.",
))


COMMA_SPACE_CAPTAIN_FORM = _entry("DQ-1061", (
    "Ruled by, Captain JP in the roles chat.",
))


DOUBLED_COLON_SPACE_CAPTAIN_FORM = _entry("DQ-1062", (
    "Ruled by:: Captain JP in the roles chat.",
))


SINGLE_COLON_NBSP_MANAGER_FORM = _entry("DQ-1063", (
    "Settled by:\u00a0the Manager in the roles chat.",
))


DOUBLED_COMMA_SPACE_CAPTAIN_FORM = _entry("DQ-1064", (
    "Ruled by,, Captain JP in the roles chat.",
))


TRIPLE_COLON_SPACE_CAPTAIN_FORM = _entry("DQ-1065", (
    "Ruled by::: Captain JP in the roles chat.",
))


COMMA_AGAINST_NAME_CAPTAIN_FORM = _entry("DQ-1066", (
    "Ruled by,Captain JP in the roles chat.",
))


PARENTHESIS_CAPTAIN_FORM = _entry("DQ-1067", (
    "Ruled by(Captain JP in the roles chat.",
))


HEADING_COMMA_NBSP_FORM = _heading_entry(
    "DQ-1068",
    "Ruled by,\u00a0Captain JP",
    "The note stands in the queue in its short form.",
)


MENTIONED_DOUBLED_COLON_NBSP_FORM = _entry("DQ-1069", (
    "Mentioned by::\u00a0the Manager in the roles chat.",
))


BARE_COMMA_NBSP_CAPTAIN_FORM = _entry("DQ-1070", (
    "This item was noted by,\u00a0Captain JP in the roles "
    "chat, and the note stands in the chat.",
))


NO_DECIDER_FORM = _entry("DQ-1071", ())


PIN_LABELLED_ENTRIES = (
    "DQ-002", "DQ-003", "DQ-004", "DQ-005", "DQ-006", "DQ-009",
    "DQ-010", "DQ-011", "DQ-012", "DQ-013", "DQ-015", "DQ-016",
    "DQ-017", "DQ-018", "DQ-019", "DQ-020", "DQ-021", "DQ-027",
    "DQ-028", "DQ-030", "DQ-031", "DQ-033", "DQ-052", "DQ-059",
    "DQ-072", "DQ-073", "DQ-138", "DQ-139", "DQ-140", "DQ-141",
    "DQ-142", "DQ-144", "DQ-145", "DQ-146", "DQ-147", "DQ-148",
    "DQ-149", "DQ-150", "DQ-151", "DQ-152", "DQ-154", "DQ-155",
    "DQ-160", "DQ-168", "DQ-169", "R-7",
)


def _pipeline(data, name="probe.md"):
    _model, output = h.run_pipeline(data, name=name)
    if output is None:
        raise AssertionError("pipeline returned a failure result")
    return output


def _render_blocks(data, name="probe.md"):
    output = _pipeline(data, name=name)
    text = h.render_text(output, "render")
    return output, text.split("\n\n")


def _block_for(blocks, entry_id):
    for block in blocks:
        first_line = block.split("\n", 1)[0]
        if (first_line.startswith(entry_id + ":")
                or first_line.startswith(entry_id + " ")):
            return block
    raise AssertionError("no render block for " + entry_id)


def _decider_findings(output, entry_id):
    found = []
    for finding in h.findings_for(output, entry_id=entry_id, rule=5):
        statement = h.finding_statement(finding) or ""
        if "No decider is recorded" in statement:
            found.append(finding)
    return found


class PunctuationNbspFormTest(unittest.TestCase):
    """A9-8-2: a cured punctuation separator after "by"
    followed by a non breaking space is a form the decider
    check accepts, and the listing prints the decider label
    for it, on both subcommands where the listing prints."""

    def _assert_labelled(self, data, entry_id, label):
        output, blocks = _render_blocks(data)
        block = _block_for(blocks, entry_id)
        self.assertIn("Decider label: " + label, block)
        self.assertNotIn("decider not recorded", block)
        self.assertEqual(_decider_findings(output, entry_id), [])
        for form in ("validate", "render"):
            text = h.render_text(output, form)
            self.assertIn("Decider label: " + label, text, form)
            self.assertNotIn(
                "Decider: decider not recorded", text, form)

    def test_doubled_colon_nbsp_captain_prints_captain(self):
        self._assert_labelled(
            DOUBLED_COLON_NBSP_CAPTAIN_FORM, "DQ-1050",
            "Ruled by Captain JP")

    def test_doubled_colon_nbsp_manager_prints_grant(self):
        self._assert_labelled(
            DOUBLED_COLON_NBSP_MANAGER_FORM, "DQ-1051",
            "Settled by the Manager under the grant")

    def test_doubled_colon_nbsp_clerk_prints_phrase(self):
        self._assert_labelled(
            DOUBLED_COLON_NBSP_CLERK_FORM, "DQ-1052",
            "the Clerk in the roles chat")

    def test_comma_nbsp_captain_prints_captain(self):
        self._assert_labelled(
            COMMA_NBSP_CAPTAIN_FORM, "DQ-1053",
            "Ruled by Captain JP")

    def test_comma_nbsp_manager_prints_grant(self):
        self._assert_labelled(
            COMMA_NBSP_MANAGER_FORM, "DQ-1054",
            "Settled by the Manager under the grant")

    def test_semicolon_nbsp_captain_prints_captain(self):
        self._assert_labelled(
            SEMICOLON_NBSP_CAPTAIN_FORM, "DQ-1055",
            "Ruled by Captain JP")

    def test_semicolon_nbsp_clerk_prints_phrase(self):
        self._assert_labelled(
            SEMICOLON_NBSP_CLERK_FORM, "DQ-1056",
            "the Clerk in the roles chat")

    def test_full_stop_nbsp_captain_prints_captain(self):
        self._assert_labelled(
            FULL_STOP_NBSP_CAPTAIN_FORM, "DQ-1057",
            "Ruled by Captain JP")


class StandingFormsGuardTest(unittest.TestCase):
    """The standing forms keep printing the labels they
    printed before this cure: the space form, the comma
    with a standing class whitespace form and the doubled
    colon with a standing class whitespace form Fix Seat Y
    cured, and the single colon with a non breaking space
    form the colon branch already took."""

    def _assert_label(self, data, entry_id, label):
        output, blocks = _render_blocks(data)
        block = _block_for(blocks, entry_id)
        self.assertIn("Decider label: " + label, block)
        self.assertEqual(_decider_findings(output, entry_id), [])

    def test_space_after_by_keeps_the_grant_label(self):
        self._assert_label(
            SPACE_MANAGER_FORM, "DQ-1060",
            "Settled by the Manager under the grant")

    def test_comma_space_keeps_the_captain_label(self):
        self._assert_label(
            COMMA_SPACE_CAPTAIN_FORM, "DQ-1061",
            "Ruled by Captain JP")

    def test_doubled_colon_space_keeps_the_captain_label(self):
        self._assert_label(
            DOUBLED_COLON_SPACE_CAPTAIN_FORM, "DQ-1062",
            "Ruled by Captain JP")

    def test_single_colon_nbsp_keeps_the_grant_label(self):
        self._assert_label(
            SINGLE_COLON_NBSP_MANAGER_FORM, "DQ-1063",
            "Settled by the Manager under the grant")


class BoundFormsGuardTest(unittest.TestCase):
    """The forms the bound leaves keep standing as they
    stood: doubled separators generally stay denied by
    the listing while the check accepts them, a triple
    colon stays denied the same way, punctuation standing
    directly against the name stays denied the same way,
    and a parenthesis at this position stays denied the
    same way, each beside no decider Error."""

    def _assert_left(self, data, entry_id):
        output, blocks = _render_blocks(data)
        block = _block_for(blocks, entry_id)
        self.assertNotIn("Decider label:", block)
        self.assertIn("Decider: decider not recorded", block)
        self.assertEqual(_decider_findings(output, entry_id), [])

    def test_doubled_comma_space_stays_not_recorded(self):
        self._assert_left(DOUBLED_COMMA_SPACE_CAPTAIN_FORM, "DQ-1064")

    def test_triple_colon_space_stays_not_recorded(self):
        self._assert_left(TRIPLE_COLON_SPACE_CAPTAIN_FORM, "DQ-1065")

    def test_comma_against_name_stays_not_recorded(self):
        self._assert_left(COMMA_AGAINST_NAME_CAPTAIN_FORM, "DQ-1066")

    def test_parenthesis_after_by_stays_not_recorded(self):
        self._assert_left(PARENTHESIS_CAPTAIN_FORM, "DQ-1067")


class DeniedFormsGuardTest(unittest.TestCase):
    """Every form both sides deny keeps printing decider
    not recorded beside its standing decider Error: the
    heading step stands not widened, the verb anchor on
    the Captain branch holds for the new combinations,
    and an entry with no decider anywhere stands denied."""

    def _assert_not_recorded(self, data, entry_id):
        output, blocks = _render_blocks(data)
        block = _block_for(blocks, entry_id)
        self.assertNotIn("Decider label:", block)
        self.assertIn("Decider: decider not recorded", block)
        self.assertEqual(len(_decider_findings(output, entry_id)), 1)

    def test_heading_comma_nbsp_stays_not_recorded(self):
        self._assert_not_recorded(HEADING_COMMA_NBSP_FORM, "DQ-1068")

    def test_mentioned_doubled_colon_nbsp_stays_not_recorded(self):
        self._assert_not_recorded(
            MENTIONED_DOUBLED_COLON_NBSP_FORM, "DQ-1069")

    def test_bare_comma_nbsp_captain_no_verb_stays_not_recorded(self):
        self._assert_not_recorded(BARE_COMMA_NBSP_CAPTAIN_FORM, "DQ-1070")

    def test_no_decider_entry_stays_not_recorded(self):
        self._assert_not_recorded(NO_DECIDER_FORM, "DQ-1071")


class PinGuardTest(unittest.TestCase):
    """The corpus pin guards: no not recorded line stands in
    either output, every one of Fix Seat N's 46 named
    entries still prints a Decider label line, DQ-164 (Open)
    prints no decider line, and the pin totals stand."""

    def test_pin_outputs_carry_no_not_recorded_line(self):
        _model, output = h.cached_pipeline("PIN")
        for form in ("validate", "render"):
            text = h.render_text(output, form)
            self.assertEqual(
                text.count("Decider: decider not recorded"), 0, form)

    def test_pin_named_entries_still_print_a_decider_label(self):
        _model, output = h.cached_pipeline("PIN")
        text = h.render_text(output, "render")
        blocks = text.split("\n\n")
        self.assertEqual(len(PIN_LABELLED_ENTRIES), 46)
        for entry_id in PIN_LABELLED_ENTRIES:
            block = _block_for(blocks, entry_id)
            self.assertIn("Decider label:", block, entry_id)

    def test_pin_open_entry_dq164_prints_no_decider_line(self):
        _model, output = h.cached_pipeline("PIN")
        text = h.render_text(output, "render")
        block = _block_for(text.split("\n\n"), "DQ-164")
        self.assertNotIn("Decider label:", block)
        self.assertNotIn("Decider:", block)

    def test_pin_totals_stand(self):
        _model, output = h.cached_pipeline("PIN")
        counts = {"Error": 0, "Warning": 0, "Note": 0}
        for finding in h.findings_of(output):
            counts[h.finding_severity(finding)] += 1
        self.assertEqual(counts, {"Error": 16, "Warning": 57,
                                  "Note": 13})


if __name__ == "__main__":
    unittest.main()
