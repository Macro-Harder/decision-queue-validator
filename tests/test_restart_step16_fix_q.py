"""Restart Step 16 fix wave 5, Fix seat Q tests.

Seat Q owns finding A5-8-3 (Low) of Auditor 8, confirmation
round 5 (design/steps/step-16r-audit5-8.md, section 3 item 2
and its findings list): the entry group listing prints
"Decider label: Settled by the Manager under the grant" on
entries whose only Manager matter is a bare "by the Manager"
mention in body prose, a form the rule 5 decider check does
not accept, so the check fires the decider Error on the same
entry the listing claims a Manager decider for. Fix Seat N's
cure (design/steps/step-16r-fix4-n.md) built the listing
label to mirror the decider check's accepted forms; the bare
body mention is one form further than the check goes.

The decider check accepts a decider from the DQ-148 cross
reference in the body, from any element carrying a decider,
from the body forms "(Ruled|Settled|Decided) by" and
"by Captain JP", from the heading form "by Captain JP", and
from an Origin field naming Captain JP. It accepts no
decider from a bare "by the Manager" mention: not from a
lowercase "settled by the Manager" prose sentence, and not
from a sentence stating no decision at all, such as a note
sent by the Manager for filing.

The tests below pin the cured behaviour, written before the
cure. The bare form tests fail before the cure and pass
after it. The guard tests pass before and after: the
recorded grant form paragraph, the Manager pass 2 grant
form, the "(Ruled|Settled|Decided) by the Manager" prose
forms, the DQ-148 cross reference form, a named decider in
a "Ruled by" phrase, and the lowercase Captain JP prose
sentence each keep printing their label with no decider
Error, and the corpus pin guards hold.

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


SETTLED_LOWERCASE_FORM = _entry("DQ-975", (
    "This item was settled by the Manager in the roles chat, "
    "and the grant record stands in the chat.",
))


SENT_BY_FORM = _entry("DQ-976", (
    "The weekly note was sent by the Manager to the roles "
    "chat for filing.",
))


SETTLED_CAPS_FORM = _entry("DQ-977", (
    "This item was SETTLED by The Manager in the roles chat.",
))


GRANT_PARAGRAPH_FORM = _entry("DQ-966", (
    "Settled by the Manager under the grant, recorded in the "
    "roles chat on 2026-11-14.",
))


PASS2_GRANT_FORM = _entry("DQ-971", (
    "Settled by: The Manager under the pass 2 grant",
))


CROSS_REFERENCE_FORM = _entry("DQ-970", (
    "This item stands decided by assessment under DQ-148.",
))


NAMED_DECIDER_FORM = _entry("DQ-972", (
    "Ruled by the Clerk in the roles chat on 2026-11-14.",
))


LOWERCASE_CAPTAIN_FORM = _entry("DQ-973", (
    "The item was ruled by Captain JP in the roles chat, "
    "in her own words.",
))


SETTLED_BY_MANAGER_FORM = _entry("DQ-974", (
    "Settled by the Manager under the grant, in the roles "
    "chat.",
))


DECIDED_BY_MANAGER_FORM = _entry("DQ-979", (
    "Decided by the Manager in the roles chat.",
))


RULED_BY_MANAGER_FORM = _entry("DQ-980", (
    "Ruled by the Manager in the roles chat.",
))


ORIGIN_PLUS_BARE_FORM = (
    "# Decision queue\n"
    "\n"
    "### DQ-981: the pool division\n"
    "\n"
    "Origin: Captain JP, build-flow roles chat, 2026-11-11, "
    "in her words: \"The builders only take from the "
    "builder pool.\"\n"
    "\n"
    "The weekly note was sent by the Manager to the roles "
    "chat for filing.\n"
    "\n"
    "Ruled: yes. A team seats only from its own family pool.\n"
    "\n"
    "Landed in NOTES.md section 2.\n"
    "\n"
    "Status: closed.\n"
).encode("utf-8")


HEADING_PLUS_BARE_FORM = (
    "# Decision queue\n"
    "\n"
    "## Open items\n"
    "\n"
    "## Ruled Record\n"
    "\n"
    "## DQ-982: the harbour store note. RULED by Captain JP "
    "2026-11-15\n"
    "\n"
    "The weekly note was sent by the Manager to the roles "
    "chat for filing.\n"
    "\n"
    "Origin: the harbour store question in the Clerk note of "
    "2026-11-14. Captain JP ruled in her own words: \"Keep the "
    "store by the harbour gate.\" Ruled: the harbour store "
    "stands by the harbour gate, and the night keeper holds "
    "its key. Landed: the harbour store paragraph in the Clerk "
    "note now states the gate form. Status: closed.\n"
).encode("utf-8")


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


def _render_blocks(data, name="probe.md"):
    _model, output = h.run_pipeline(data, name=name)
    if output is None:
        raise AssertionError("pipeline returned a failure result")
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


class BareManagerBodyFormTest(unittest.TestCase):
    """A5-8-3: a bare "by the Manager" body mention earns no
    listing label, because the decider check accepts no
    decider from it."""

    def _assert_not_recorded(self, data, entry_id):
        output, blocks = _render_blocks(data)
        block = _block_for(blocks, entry_id)
        self.assertNotIn("Decider label:", block)
        self.assertNotIn("Settled by the Manager", block)
        self.assertIn("Decider: decider not recorded", block)
        self.assertEqual(len(_decider_findings(output, entry_id)), 1)

    def test_settled_lowercase_prose_prints_no_manager_label(self):
        self._assert_not_recorded(SETTLED_LOWERCASE_FORM, "DQ-975")

    def test_sent_by_prose_prints_no_manager_label(self):
        self._assert_not_recorded(SENT_BY_FORM, "DQ-976")

    def test_bare_manager_beside_origin_decider_lists_that_decider(self):
        output, blocks = _render_blocks(ORIGIN_PLUS_BARE_FORM)
        block = _block_for(blocks, "DQ-981")
        self.assertIn("Decider label: Ruled by Captain JP", block)
        self.assertNotIn("Settled by the Manager", block)
        self.assertEqual(_decider_findings(output, "DQ-981"), [])


class AcceptedManagerFormsTest(unittest.TestCase):
    """The Manager forms the decider check accepts keep
    printing the Manager label, with no decider Error."""

    def _assert_manager_label(self, data, entry_id, label):
        output, blocks = _render_blocks(data)
        block = _block_for(blocks, entry_id)
        self.assertIn("Decider label: " + label, block)
        self.assertEqual(_decider_findings(output, entry_id), [])

    def test_recorded_grant_form_paragraph_keeps_its_label(self):
        self._assert_manager_label(
            GRANT_PARAGRAPH_FORM, "DQ-966",
            "Settled by the Manager under the grant")

    def test_manager_pass2_grant_form_keeps_its_label(self):
        self._assert_manager_label(
            PASS2_GRANT_FORM, "DQ-971", "under the pass 2 grant")

    def test_settled_by_the_manager_prose_keeps_its_label(self):
        self._assert_manager_label(
            SETTLED_BY_MANAGER_FORM, "DQ-974",
            "Settled by the Manager under the grant")

    def test_decided_by_the_manager_prose_keeps_its_label(self):
        self._assert_manager_label(
            DECIDED_BY_MANAGER_FORM, "DQ-979",
            "Settled by the Manager under the grant")

    def test_ruled_by_the_manager_prose_keeps_its_label(self):
        self._assert_manager_label(
            RULED_BY_MANAGER_FORM, "DQ-980",
            "Settled by the Manager under the grant")

    def test_settled_caps_form_keeps_its_label(self):
        self._assert_manager_label(
            SETTLED_CAPS_FORM, "DQ-977",
            "Settled by the Manager under the grant")


class AcceptedDeciderFormsTest(unittest.TestCase):
    """Every other accepted decider form from Fix Seat N's
    paper, as round 5 Auditor 3 evidenced, keeps printing
    its label."""

    def _assert_label(self, data, entry_id, label):
        output, blocks = _render_blocks(data)
        block = _block_for(blocks, entry_id)
        self.assertIn("Decider label: " + label, block)
        self.assertEqual(_decider_findings(output, entry_id), [])

    def test_dq148_cross_reference_form_keeps_its_label(self):
        self._assert_label(
            CROSS_REFERENCE_FORM, "DQ-970",
            "decided by assessment under DQ-148")

    def test_named_decider_in_ruled_by_phrase_keeps_its_label(self):
        self._assert_label(
            NAMED_DECIDER_FORM, "DQ-972",
            "the Clerk in the roles chat on 2026-11-14")

    def test_lowercase_ruled_by_captain_jp_keeps_its_label(self):
        self._assert_label(
            LOWERCASE_CAPTAIN_FORM, "DQ-973", "Ruled by Captain JP")

    def test_bare_manager_beside_heading_decider_keeps_heading_label(self):
        self._assert_label(
            HEADING_PLUS_BARE_FORM, "DQ-982", "Ruled by Captain JP")


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
