"""Restart Step 16 fix wave 8, Fix seat Y tests.

Seat Y owns finding A8-8-2 (Low) of Auditor 8, confirmation
round 8 (design/steps/step-16r-audit8-8.md, section 6 and
its findings list), triaged at step record section 27
(design/steps/step-16r-record.md): the entry group listing
denies a decider the rule 5 decider check accepts, where a
boundary character that is not a whitespace of the
listing's class stands between "by" and the decider name.

The decider check takes any word boundary after "by": its
body pattern is "(Ruled|Settled|Decided) by" ending at a
word boundary. Fix Seat U widened the listing's decider
steps inside _listing_decider_label in validate.py to one
whitespace character of the class space, tab, carriage
return or line feed at that position (finding A6-8-4), and
Fix Seat W widened the same class to the vertical tab and
the form feed (finding A7-8-2). Every character Auditor 8
evidences in section 6 is a word boundary the check takes
and no character of that widened class: a comma, a
semicolon and a full stop, each followed by a space; a
hyphen, a slash and the en dash character, each standing
directly against the name; a non breaking space standing
as the separator itself; and a doubled colon followed by
a space. In each evidenced form the presence decider
stands true and no decider Error stands, while both
subcommands print "Decider: decider not recorded".

The tests below pin the cured behaviour, written before
the cure. The twelve evidenced variant tests fail before
the cure and pass after it: each prints its decider label
on both subcommands where the listing prints, with no
decider Error. The guard tests pass before and after: the
standing mirror forms Fix Seats U and W cured keep
printing their labels, the doubled space Manager form
keeps the verbatim phrase label Fix Seat Q recorded for
it, and every unaccepted form keeps printing decider not
recorded beside its standing decider Error, including a
bare note carrying "by" with a non breaking space before
"Captain JP" and no verb form the check accepts, which
the check denies and the listing must go on denying.

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


COMMA_CAPTAIN_FORM = _entry("DQ-1030", (
    "Ruled by, Captain JP in the roles chat.",
))


COMMA_MANAGER_FORM = _entry("DQ-1031", (
    "Settled by, the Manager in the roles chat.",
))


COMMA_NAMED_FORM = _entry("DQ-1032", (
    "Decided by, the Clerk in the roles chat.",
))


SEMICOLON_CAPTAIN_FORM = _entry("DQ-1033", (
    "Ruled by; Captain JP in the roles chat.",
))


FULL_STOP_CAPTAIN_FORM = _entry("DQ-1034", (
    "Ruled by. Captain JP in the roles chat.",
))


HYPHEN_CAPTAIN_FORM = _entry("DQ-1035", (
    "Ruled by-Captain JP in the roles chat.",
))


SLASH_CAPTAIN_FORM = _entry("DQ-1036", (
    "Ruled by/Captain JP in the roles chat.",
))


EN_DASH_MANAGER_FORM = _entry("DQ-1037", (
    "Settled by\u2013the Manager in the roles chat.",
))


NBSP_CAPTAIN_FORM = _entry("DQ-1038", (
    "Ruled by\u00a0Captain JP in the roles chat.",
))


NBSP_MANAGER_FORM = _entry("DQ-1039", (
    "Settled by\u00a0the Manager in the roles chat.",
))


NBSP_NAMED_FORM = _entry("DQ-1040", (
    "Decided by\u00a0the Clerk in the roles chat.",
))


DOUBLED_COLON_CAPTAIN_FORM = _entry("DQ-1041", (
    "Ruled by:: Captain JP in the roles chat.",
))


SPACE_MANAGER_FORM = _entry("DQ-1042", (
    "Settled by the Manager in the roles chat.",
))


VT_MANAGER_FORM = _entry("DQ-1043", (
    "Settled by\vthe Manager in the roles chat.",
))


DOUBLED_SPACE_MANAGER_FORM = _entry("DQ-1044", (
    "Settled by  the Manager in the roles chat.",
))


BARE_NBSP_CAPTAIN_FORM = _entry("DQ-1045", (
    "This item was settled by\u00a0Captain JP in the roles "
    "chat, and the grant record stands in the chat.",
))


MENTIONED_COMMA_FORM = _entry("DQ-1046", (
    "Mentioned by, the Manager in the roles chat.",
))


SENT_BY_COMMA_FORM = _entry("DQ-1047", (
    "The weekly note was sent by, the Manager to the roles "
    "chat for filing.",
))


NO_DECIDER_FORM = _entry("DQ-1048", ())


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


class BoundaryCharacterAfterByFormTest(unittest.TestCase):
    """A8-8-2: a boundary character that is not a whitespace
    of the listing's class, standing between "by" and the
    decider name, is a form the decider check accepts, and
    the listing prints the decider label for it, on both
    subcommands where the listing prints."""

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

    def test_ruled_by_comma_captain_jp_prints_captain(self):
        self._assert_labelled(
            COMMA_CAPTAIN_FORM, "DQ-1030", "Ruled by Captain JP")

    def test_settled_by_comma_the_manager_prints_grant(self):
        self._assert_labelled(
            COMMA_MANAGER_FORM, "DQ-1031",
            "Settled by the Manager under the grant")

    def test_decided_by_comma_named_clerk_prints_phrase(self):
        self._assert_labelled(
            COMMA_NAMED_FORM, "DQ-1032",
            "the Clerk in the roles chat")

    def test_ruled_by_semicolon_captain_jp_prints_captain(self):
        self._assert_labelled(
            SEMICOLON_CAPTAIN_FORM, "DQ-1033",
            "Ruled by Captain JP")

    def test_ruled_by_full_stop_captain_jp_prints_captain(self):
        self._assert_labelled(
            FULL_STOP_CAPTAIN_FORM, "DQ-1034",
            "Ruled by Captain JP")

    def test_ruled_by_hyphen_captain_jp_prints_captain(self):
        self._assert_labelled(
            HYPHEN_CAPTAIN_FORM, "DQ-1035", "Ruled by Captain JP")

    def test_ruled_by_slash_captain_jp_prints_captain(self):
        self._assert_labelled(
            SLASH_CAPTAIN_FORM, "DQ-1036", "Ruled by Captain JP")

    def test_settled_by_en_dash_the_manager_prints_grant(self):
        self._assert_labelled(
            EN_DASH_MANAGER_FORM, "DQ-1037",
            "Settled by the Manager under the grant")

    def test_ruled_by_nbsp_captain_jp_prints_captain(self):
        self._assert_labelled(
            NBSP_CAPTAIN_FORM, "DQ-1038", "Ruled by Captain JP")

    def test_settled_by_nbsp_the_manager_prints_grant(self):
        self._assert_labelled(
            NBSP_MANAGER_FORM, "DQ-1039",
            "Settled by the Manager under the grant")

    def test_decided_by_nbsp_named_clerk_prints_phrase(self):
        self._assert_labelled(
            NBSP_NAMED_FORM, "DQ-1040",
            "the Clerk in the roles chat")

    def test_ruled_by_doubled_colon_captain_jp_prints_captain(self):
        self._assert_labelled(
            DOUBLED_COLON_CAPTAIN_FORM, "DQ-1041",
            "Ruled by Captain JP")


class StandingFormsGuardTest(unittest.TestCase):
    """The standing forms keep printing the labels they
    printed before this cure: the space form and the
    vertical tab form Fix Seats U and W cured, and the
    doubled space Manager form, which reaches its label
    through the named phrase step in the verbatim form
    Fix Seat Q recorded for the doubled separator."""

    def _assert_label(self, data, entry_id, label):
        output, blocks = _render_blocks(data)
        block = _block_for(blocks, entry_id)
        self.assertIn("Decider label: " + label, block)
        self.assertEqual(_decider_findings(output, entry_id), [])

    def test_space_after_by_keeps_the_grant_label(self):
        self._assert_label(
            SPACE_MANAGER_FORM, "DQ-1042",
            "Settled by the Manager under the grant")

    def test_vertical_tab_after_by_keeps_the_grant_label(self):
        self._assert_label(
            VT_MANAGER_FORM, "DQ-1043",
            "Settled by the Manager under the grant")

    def test_doubled_space_keeps_the_verbatim_phrase_label(self):
        self._assert_label(
            DOUBLED_SPACE_MANAGER_FORM, "DQ-1044",
            "the Manager in the roles chat")


class UnacceptedFormsGuardTest(unittest.TestCase):
    """Every unaccepted form keeps printing decider not
    recorded beside its standing decider Error: a boundary
    character at this position creates no acceptance where
    the verb stands in no form the check accepts, and a
    bare "by" carrying a non breaking space before
    "Captain JP" with no accepted verb form stands denied
    by the check, whose "by Captain JP" substring test
    takes the plain space only, so the listing denies it
    too."""

    def _assert_not_recorded(self, data, entry_id):
        output, blocks = _render_blocks(data)
        block = _block_for(blocks, entry_id)
        self.assertNotIn("Decider label:", block)
        self.assertIn("Decider: decider not recorded", block)
        self.assertEqual(len(_decider_findings(output, entry_id)), 1)

    def test_bare_nbsp_captain_no_verb_stays_not_recorded(self):
        self._assert_not_recorded(BARE_NBSP_CAPTAIN_FORM, "DQ-1045")

    def test_mentioned_by_comma_manager_stays_not_recorded(self):
        self._assert_not_recorded(MENTIONED_COMMA_FORM, "DQ-1046")

    def test_sent_by_comma_manager_stays_not_recorded(self):
        self._assert_not_recorded(SENT_BY_COMMA_FORM, "DQ-1047")

    def test_no_decider_entry_stays_not_recorded(self):
        self._assert_not_recorded(NO_DECIDER_FORM, "DQ-1048")


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
