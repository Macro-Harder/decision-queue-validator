"""Restart Step 16 fix wave 7, Fix seat W tests.

Seat W owns finding A7-8-2 (Low) of Auditor 8, confirmation
round 7 (design/steps/step-16r-audit7-8.md, section 3 item 5
and its findings list), with the listing facts confirmed
first hand by Auditor 14 (design/steps/step-16r-audit7-14.md,
section 3): the entry group listing denies a decider the
rule 5 decider check accepts, where a vertical tab or a
form feed stands between "by" and the decider name. The six
evidenced variants are the Manager phrase, the Captain
phrase and a named Clerk phrase, under each of the two
characters, each with presence decider true and no decider
Error, while render prints "Decider: decider not recorded".

The decider check takes any word boundary after "by": its
body pattern is "(Ruled|Settled|Decided) by" ending at a
word boundary, and a vertical tab and a form feed are each
a word boundary. Fix Seat U widened the listing's decider
steps inside _listing_decider_label in validate.py to one
whitespace character of the class space, tab, carriage
return or line feed at that position (finding A6-8-4), and
neither the vertical tab nor the form feed stands in that
class, so the listing again denies what the check accepts,
one character class further in the same mirror family.

The tests below pin the cured behaviour, written before
the cure. The six variant tests fail before the cure and
pass after it: each evidenced variant prints its decider
label on both subcommands where the listing prints, with
no decider Error, and the named Clerk variants pin the
named phrase step itself in the same forms. The guard
tests pass before and after: the standing mirror forms
Fix Seat U cured (a space, a tab, a line break and a
carriage return after "by") keep printing their labels,
the bounding contrast of a vertical tab before "by" keeps
its grant label, every unaccepted form keeps printing
decider not recorded beside its standing decider Error,
including a sent by form with a vertical tab at the same
position, and DQ-164 on the corpus pin keeps printing no
decider line of either form.

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


VT_MANAGER_FORM = _entry("DQ-1010", (
    "Settled by\vthe Manager in the roles chat.",
))


FF_MANAGER_FORM = _entry("DQ-1011", (
    "Settled by\fthe Manager in the roles chat.",
))


VT_CAPTAIN_FORM = _entry("DQ-1012", (
    "Ruled by\vCaptain JP in the roles chat.",
))


FF_CAPTAIN_FORM = _entry("DQ-1013", (
    "Ruled by\fCaptain JP in the roles chat.",
))


VT_NAMED_FORM = _entry("DQ-1014", (
    "Decided by\vthe Clerk in the roles chat.",
))


FF_NAMED_FORM = _entry("DQ-1015", (
    "Decided by\fthe Clerk in the roles chat.",
))


SPACE_MANAGER_FORM = _entry("DQ-1016", (
    "Settled by the Manager in the roles chat.",
))


TAB_MANAGER_FORM = _entry("DQ-1017", (
    "Settled by\tthe Manager in the roles chat.",
))


LINEBREAK_MANAGER_FORM = _entry("DQ-1018", (
    "Settled by\nthe Manager in the roles chat.",
))


CARRIAGE_RETURN_MANAGER_FORM = _entry("DQ-1019", (
    "Settled by\rthe Manager in the roles chat.",
))


VT_BEFORE_BY_FORM = _entry("DQ-1020", (
    "Settled\vby the Manager in the roles chat.",
))


BARE_LOWERCASE_FORM = _entry("DQ-1021", (
    "This item was settled by the Manager in the roles chat, "
    "and the grant record stands in the chat.",
))


SENT_BY_FORM = _entry("DQ-1022", (
    "The weekly note was sent by the Manager to the roles "
    "chat for filing.",
))


SENT_BY_VT_FORM = _entry("DQ-1023", (
    "The weekly note was sent by\vthe Manager to the roles "
    "chat for filing.",
))


SENT_BY_FF_FORM = _entry("DQ-1024", (
    "The weekly note was sent by\fthe Manager to the roles "
    "chat for filing.",
))


NO_DECIDER_FORM = _entry("DQ-1025", ())


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


class VerticalTabAndFormFeedAfterByFormTest(unittest.TestCase):
    """A7-8-2: a vertical tab or a form feed between "by"
    and the decider name is a form the decider check
    accepts, and the listing prints the decider label for
    it, on both subcommands where the listing prints."""

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

    def test_settled_by_vertical_tab_the_manager_prints_grant(self):
        self._assert_labelled(
            VT_MANAGER_FORM, "DQ-1010",
            "Settled by the Manager under the grant")

    def test_settled_by_form_feed_the_manager_prints_grant(self):
        self._assert_labelled(
            FF_MANAGER_FORM, "DQ-1011",
            "Settled by the Manager under the grant")

    def test_ruled_by_vertical_tab_captain_jp_prints_captain(self):
        self._assert_labelled(
            VT_CAPTAIN_FORM, "DQ-1012", "Ruled by Captain JP")

    def test_ruled_by_form_feed_captain_jp_prints_captain(self):
        self._assert_labelled(
            FF_CAPTAIN_FORM, "DQ-1013", "Ruled by Captain JP")

    def test_decided_by_vertical_tab_named_clerk_prints_phrase(self):
        self._assert_labelled(
            VT_NAMED_FORM, "DQ-1014",
            "the Clerk in the roles chat")

    def test_decided_by_form_feed_named_clerk_prints_phrase(self):
        self._assert_labelled(
            FF_NAMED_FORM, "DQ-1015",
            "the Clerk in the roles chat")


class StandingMirrorFormsGuardTest(unittest.TestCase):
    """The standing mirror forms keep printing their labels:
    the space, tab, line break and carriage return forms
    Fix Seat U cured, and the bounding contrast of a
    vertical tab standing before "by", which an element
    parse extracts, in agreement between listing and check."""

    def _assert_label(self, data, entry_id, label):
        output, blocks = _render_blocks(data)
        block = _block_for(blocks, entry_id)
        self.assertIn("Decider label: " + label, block)
        self.assertEqual(_decider_findings(output, entry_id), [])

    def test_space_after_by_keeps_the_grant_label(self):
        self._assert_label(
            SPACE_MANAGER_FORM, "DQ-1016",
            "Settled by the Manager under the grant")

    def test_tab_after_by_keeps_the_grant_label(self):
        self._assert_label(
            TAB_MANAGER_FORM, "DQ-1017",
            "Settled by the Manager under the grant")

    def test_linebreak_after_by_keeps_the_grant_label(self):
        self._assert_label(
            LINEBREAK_MANAGER_FORM, "DQ-1018",
            "Settled by the Manager under the grant")

    def test_carriage_return_after_by_keeps_the_grant_label(self):
        self._assert_label(
            CARRIAGE_RETURN_MANAGER_FORM, "DQ-1019",
            "Settled by the Manager under the grant")

    def test_vertical_tab_before_by_keeps_the_grant_label(self):
        self._assert_label(
            VT_BEFORE_BY_FORM, "DQ-1020",
            "Settled by the Manager under the grant")


class UnacceptedFormsGuardTest(unittest.TestCase):
    """Every unaccepted form keeps printing decider not
    recorded beside its standing decider Error, including
    the bare Manager body form Fix Seat Q cured: a vertical
    tab or a form feed at the same position creates no
    acceptance where the verb stands in no accepted form."""

    def _assert_not_recorded(self, data, entry_id):
        output, blocks = _render_blocks(data)
        block = _block_for(blocks, entry_id)
        self.assertNotIn("Decider label:", block)
        self.assertIn("Decider: decider not recorded", block)
        self.assertEqual(len(_decider_findings(output, entry_id)), 1)

    def test_bare_manager_lowercase_prose_stays_not_recorded(self):
        self._assert_not_recorded(BARE_LOWERCASE_FORM, "DQ-1021")

    def test_sent_by_the_manager_prose_stays_not_recorded(self):
        self._assert_not_recorded(SENT_BY_FORM, "DQ-1022")

    def test_sent_by_vertical_tab_manager_stays_not_recorded(self):
        self._assert_not_recorded(SENT_BY_VT_FORM, "DQ-1023")

    def test_sent_by_form_feed_manager_stays_not_recorded(self):
        self._assert_not_recorded(SENT_BY_FF_FORM, "DQ-1024")

    def test_no_decider_entry_stays_not_recorded(self):
        self._assert_not_recorded(NO_DECIDER_FORM, "DQ-1025")


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
