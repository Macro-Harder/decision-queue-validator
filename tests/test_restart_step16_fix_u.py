"""Restart Step 16 fix wave 6, Fix seat U tests.

Seat U owns finding A6-8-4 (Low) of Auditor 8, confirmation
round 6 (design/steps/step-16r-audit6-8.md, section 3 item 3
and its findings list): the entry group listing denies a
decider the rule 5 decider check accepts, where a tab or a
line break stands between "by" and the decider name. The
evidenced forms are "Settled by" tab "the Manager", "Ruled
by" tab "Captain JP", and "Settled by" line break "the
Manager", each at exit 0 on both subcommands with presence
decider true and no decider Error, while render prints
"Decider: decider not recorded".

The decider check takes any word boundary after "by": its
body pattern is "(Ruled|Settled|Decided) by" ending at a
word boundary, and a tab and a line break are each a
boundary. The listing's decider steps inside
_listing_decider_label in validate.py each require a
literal space at that position: the "by Captain JP" step,
the Manager shim condition built by Fix Seat Q, and the
named phrase step built by Fix Seat N. Fix Seat N built the
listing to mirror the decider check's accepted forms, and
Fix Seat Q kept that mirror in the over claim direction;
this finding is the same mirror family in the under claim
direction, at the one whitespace position.

The tests below pin the cured behaviour, written before
the cure. The whitespace form tests fail before the cure
and pass after it: each evidenced form prints its decider
label on both subcommands where the listing prints, with
no decider Error, and the named phrase isolation form pins
the named phrase step itself in the same whitespace form.
The guard tests pass before and after: every accepted
decider form keeps printing its label in its recorded
label text (the recorded grant forms, the Origin forms,
the named phrase forms, the pass 2 form and the DQ-141
and DQ-148 forms), every unaccepted form keeps printing
decider not recorded beside its standing decider Error,
including the bare Manager body form Fix Seat Q cured,
and DQ-164 on the corpus pin keeps printing no decider
line of either form.

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


TAB_MANAGER_FORM = _entry("DQ-983", (
    "Settled by\tthe Manager in the roles chat.",
))


TAB_CAPTAIN_FORM = _entry("DQ-984", (
    "Ruled by\tCaptain JP in the roles chat.",
))


LINEBREAK_MANAGER_FORM = _entry("DQ-985", (
    "Settled by\nthe Manager in the roles chat.",
))


TAB_NAMED_FORM = _entry("DQ-986", (
    "Decided by\tthe Clerk in the roles chat.",
))


GRANT_PARAGRAPH_FORM = _entry("DQ-987", (
    "Settled by the Manager under the grant, recorded in the "
    "roles chat on 2026-11-14.",
))


PASS2_GRANT_FORM = _entry("DQ-988", (
    "Settled by: The Manager under the pass 2 grant",
))


CROSS_REFERENCE_FORM = _entry("DQ-989", (
    "This item stands decided by assessment under DQ-148.",
))


NAMED_DECIDER_FORM = _entry("DQ-990", (
    "Ruled by the Clerk in the roles chat on 2026-11-14.",
))


LOWERCASE_CAPTAIN_FORM = _entry("DQ-991", (
    "The item was ruled by Captain JP in the roles chat, "
    "in her own words.",
))


ORIGIN_FORM = (
    "# Decision queue\n"
    "\n"
    "### DQ-992: the pool division\n"
    "\n"
    "Origin: Captain JP, build-flow roles chat, 2026-11-11, "
    "in her words: \"The builders only take from the "
    "builder pool.\"\n"
    "\n"
    "Ruled: yes. A team seats only from its own family pool.\n"
    "\n"
    "Landed in NOTES.md section 2.\n"
    "\n"
    "Status: closed.\n"
).encode("utf-8")


TAB_AFTER_THE_FORM = _entry("DQ-993", (
    "Ruled by the\tManager in the roles chat.",
))


TAB_BEFORE_BY_FORM = _entry("DQ-994", (
    "Settled\tby the Manager in the roles chat.",
))


DQ141_SUBFORM_FORM = _entry("DQ-999", (
    "This item was Decided by the Manager in the roles chat, "
    "and the record stands in the chat.",
    "A fill in under DQ-141 is recorded in the filing note.",
))


BARE_LOWERCASE_FORM = _entry("DQ-995", (
    "This item was settled by the Manager in the roles chat, "
    "and the grant record stands in the chat.",
))


SENT_BY_FORM = _entry("DQ-996", (
    "The weekly note was sent by the Manager to the roles "
    "chat for filing.",
))


SENT_BY_TAB_FORM = _entry("DQ-997", (
    "The weekly note was sent by\tthe Manager to the roles "
    "chat for filing.",
))


NO_DECIDER_FORM = _entry("DQ-998", ())


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


class WhitespaceAfterByFormTest(unittest.TestCase):
    """A6-8-4: a tab or a line break between "by" and the
    decider name is a form the decider check accepts, and
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

    def test_settled_by_tab_the_manager_prints_the_grant_label(self):
        self._assert_labelled(
            TAB_MANAGER_FORM, "DQ-983",
            "Settled by the Manager under the grant")

    def test_ruled_by_tab_captain_jp_prints_the_captain_label(self):
        self._assert_labelled(
            TAB_CAPTAIN_FORM, "DQ-984", "Ruled by Captain JP")

    def test_settled_by_linebreak_the_manager_prints_the_label(self):
        self._assert_labelled(
            LINEBREAK_MANAGER_FORM, "DQ-985",
            "Settled by the Manager under the grant")

    def test_decided_by_tab_a_named_decider_prints_its_phrase(self):
        self._assert_labelled(
            TAB_NAMED_FORM, "DQ-986",
            "the Clerk in the roles chat")


class AcceptedDeciderFormsGuardTest(unittest.TestCase):
    """Every accepted decider form keeps printing its label
    in its recorded label text, with no decider Error."""

    def _assert_label(self, data, entry_id, label):
        output, blocks = _render_blocks(data)
        block = _block_for(blocks, entry_id)
        self.assertIn("Decider label: " + label, block)
        self.assertEqual(_decider_findings(output, entry_id), [])

    def test_recorded_grant_form_paragraph_keeps_its_label(self):
        self._assert_label(
            GRANT_PARAGRAPH_FORM, "DQ-987",
            "Settled by the Manager under the grant")

    def test_manager_pass2_grant_form_keeps_its_label(self):
        self._assert_label(
            PASS2_GRANT_FORM, "DQ-988", "under the pass 2 grant")

    def test_dq148_cross_reference_form_keeps_its_label(self):
        self._assert_label(
            CROSS_REFERENCE_FORM, "DQ-989",
            "decided by assessment under DQ-148")

    def test_dq141_subform_beside_manager_phrase_keeps_its_label(self):
        self._assert_label(
            DQ141_SUBFORM_FORM, "DQ-999", "fill in under DQ-141")

    def test_named_decider_in_ruled_by_phrase_keeps_its_label(self):
        self._assert_label(
            NAMED_DECIDER_FORM, "DQ-990",
            "the Clerk in the roles chat on 2026-11-14")

    def test_lowercase_ruled_by_captain_jp_keeps_its_label(self):
        self._assert_label(
            LOWERCASE_CAPTAIN_FORM, "DQ-991", "Ruled by Captain JP")

    def test_origin_field_decider_keeps_its_label(self):
        self._assert_label(ORIGIN_FORM, "DQ-992", "Ruled by Captain JP")

    def test_tab_between_the_and_manager_keeps_its_phrase_label(self):
        # The named phrase step prints the verbatim phrase with
        # the tab standing in it, and the escaped printing rule
        # renders that tab as the two character escape sequence.
        self._assert_label(
            TAB_AFTER_THE_FORM, "DQ-993",
            "the\\tManager in the roles chat")

    def test_tab_between_verb_and_by_keeps_the_grant_label(self):
        self._assert_label(
            TAB_BEFORE_BY_FORM, "DQ-994",
            "Settled by the Manager under the grant")


class UnacceptedFormsGuardTest(unittest.TestCase):
    """Every unaccepted form keeps printing decider not
    recorded beside its standing decider Error, including
    the bare Manager body form Fix Seat Q cured: a tab at
    the same position creates no acceptance where the verb
    stands in no accepted form."""

    def _assert_not_recorded(self, data, entry_id):
        output, blocks = _render_blocks(data)
        block = _block_for(blocks, entry_id)
        self.assertNotIn("Decider label:", block)
        self.assertIn("Decider: decider not recorded", block)
        self.assertEqual(len(_decider_findings(output, entry_id)), 1)

    def test_bare_manager_lowercase_prose_stays_not_recorded(self):
        self._assert_not_recorded(BARE_LOWERCASE_FORM, "DQ-995")

    def test_sent_by_the_manager_prose_stays_not_recorded(self):
        self._assert_not_recorded(SENT_BY_FORM, "DQ-996")

    def test_sent_by_tab_the_manager_stays_not_recorded(self):
        self._assert_not_recorded(SENT_BY_TAB_FORM, "DQ-997")

    def test_no_decider_entry_stays_not_recorded(self):
        self._assert_not_recorded(NO_DECIDER_FORM, "DQ-998")


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
