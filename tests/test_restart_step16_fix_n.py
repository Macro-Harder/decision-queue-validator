"""Restart Step 16 fix wave 4, Fix seat N tests.

Seat N owns two findings of Auditor 20, confirmation round 4
(design/steps/step-16r-audit4-20.md, findings at section 7).

Item 1, A20-F3 (Low): the entry group listing prints
"Decider: decider not recorded" on entries whose decider
stands recorded in the entry's own text in a form the rule 5
decider check itself accepts, and on which no decider finding
fires (Auditor 20's DQ-502, DQ-201, and DQ-204). The listing
takes its value from the determining element alone, while the
decider check reads the whole entry: any element carrying a
decider, the body forms "(Ruled|Settled|Decided) by" and
"by Captain JP", the heading form "by Captain JP", the
assessment cross reference "under DQ-148", and an Origin
field naming Captain JP. The tests below pin the listing to
state the decider recorded in each of those forms, and pin
the guard: an entry with no decider in any accepted form
still prints the not recorded form and still takes the
rule 5 decider Error. The listing tests fail before the cure
and pass after it; the guard tests pass before and after.

Item 2, A20-F2 (Low): a duplicated "# Decision queue" header
in a concatenated file. The plan names the expected surface
for a second header line: plan Item 3, section 3.2, field 7
supplies the header facts from the first occurrence alone,
"however many times the header text stands in the file";
section 3.3 states the invariant that a second or later
queue header stands as a file level unit of kind file
header; and the Slice 2 parse treatment states that such a
unit "takes no finding of any class and no uniqueness check
stands against it". No locus names a printed finding, note,
or segment for a second header. The two tests at the end pin
that standing form: the second header stands as a file
header unit in the model, and it takes no finding. They pass
before and after, because the item is ruled NO DEFECT.

Copyright: J.P. Picard aka Macro-Harder
"""

import unittest

import dqv_harness as h


def _render_blocks(data, name="probe.md"):
    """The render (summary) output split into entry blocks.

    Each entry block of a group listing is separated from the
    next by a blank line, and its first line carries the entry
    heading, so a block is found by its entry identifier.
    """
    _model, output = h.run_pipeline(data, name=name)
    if output is None:
        raise AssertionError("pipeline returned a failure result")
    text = h.render_text(output, "render")
    return output, text.split("\n\n")


def _block_for(blocks, entry_id):
    for block in blocks:
        if entry_id + ":" in block or entry_id + " " in block:
            return block
    raise AssertionError("no render block for " + entry_id)


def _decider_findings(output, entry_id):
    found = []
    for finding in h.findings_for(output, entry_id=entry_id, rule=5):
        statement = h.finding_statement(finding) or ""
        if "No decider is recorded" in statement:
            found.append(finding)
    return found


HEADING_FORM = (
    "# Decision queue\n"
    "\n"
    "## Open items\n"
    "\n"
    "## Ruled Record\n"
    "\n"
    "## DQ-953: the harbour store note. RULED by Captain JP "
    "2026-11-15\n"
    "\n"
    "Origin: the harbour store question in the Clerk note of "
    "2026-11-14. Captain JP ruled in her own words: \"Keep the "
    "store by the harbour gate.\" Ruled: the harbour store "
    "stands by the harbour gate, and the night keeper holds "
    "its key. Landed: the harbour store paragraph in the Clerk "
    "note now states the gate form. Status: closed.\n"
).encode("utf-8")


BLOCK_FORM = (
    "# Decision queue\n"
    "\n"
    "### DQ-961: the harbour consequence\n"
    "\n"
    "Status: Banked\n"
    "\n"
    "#### Ruling by Captain JP\n"
    "\n"
    "Ruled by: Captain JP\n"
    "\n"
    "Ruling text: \"Count it as a fail.\"\n"
    "\n"
    "Ruling outcome: The outcome stands as recorded.\n"
    "\n"
    "Where the ruling landed: NOTES.md section 2.\n"
    "\n"
    "Status: RULED, closed. This item is ruled.\n"
).encode("utf-8")


BODY_PROSE_FORM = (
    "# Decision queue\n"
    "\n"
    "### DQ-962: the checker note form\n"
    "\n"
    "Status: Banked\n"
    "\n"
    "Ruled by Captain JP in the roles chat on 2026-11-14.\n"
    "\n"
    "Ruled: the checker note takes the short form.\n"
    "\n"
    "Landed: the checker note in NOTES.md section 2 now "
    "states the agreed form.\n"
    "\n"
    "Status: closed.\n"
).encode("utf-8")


PLAIN_PARAGRAPH_FORM = (
    "# Decision queue\n"
    "\n"
    "### DQ-963: the harbour cap\n"
    "\n"
    "Status: Banked\n"
    "\n"
    "This item was decided by Captain JP at the roles chat, "
    "and her words stand in the chat record.\n"
    "\n"
    "Ruling outcome: the cap takes the rising form.\n"
    "\n"
    "Where the ruling landed: NOTES.md section 3.\n"
    "\n"
    "Status: RULED, closed. This item is ruled.\n"
).encode("utf-8")


ORIGIN_FORM = (
    "# Decision queue\n"
    "\n"
    "### DQ-964: the pool division\n"
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


NO_DECIDER_FORM = (
    "# Decision queue\n"
    "\n"
    "### DQ-965: the unnamed ruling\n"
    "\n"
    "Status: Banked\n"
    "\n"
    "Ruling text: \"The note takes the short form.\"\n"
    "\n"
    "Ruling outcome: The short form stands.\n"
    "\n"
    "Where the ruling landed: NOTES.md section 2.\n"
    "\n"
    "Status: RULED, closed. This item is ruled.\n"
).encode("utf-8")


class DeciderListingProseFormsTest(unittest.TestCase):
    """A20-F3: the group listing states the decider the entry
    records, in every form the decider check accepts."""

    def _assert_listed(self, data, entry_id):
        output, blocks = _render_blocks(data)
        self.assertEqual(_decider_findings(output, entry_id), [])
        block = _block_for(blocks, entry_id)
        self.assertIn("Decider label: Ruled by Captain JP", block)
        self.assertNotIn("decider not recorded", block)

    def test_heading_recorded_decider_is_listed(self):
        self._assert_listed(HEADING_FORM, "DQ-953")

    def test_decider_on_a_non_determining_element_is_listed(self):
        self._assert_listed(BLOCK_FORM, "DQ-961")

    def test_body_prose_decider_sentence_is_listed(self):
        self._assert_listed(BODY_PROSE_FORM, "DQ-962")

    def test_plain_paragraph_by_captain_jp_is_listed(self):
        self._assert_listed(PLAIN_PARAGRAPH_FORM, "DQ-963")

    def test_origin_field_decider_is_listed(self):
        self._assert_listed(ORIGIN_FORM, "DQ-964")

    def test_pin_entries_with_prose_deciders_are_listed(self):
        _model, output = h.cached_pipeline("PIN")
        text = h.render_text(output, "render")
        blocks = text.split("\n\n")
        for entry_id in ("DQ-052", "DQ-154", "DQ-160", "DQ-168"):
            block = _block_for(blocks, entry_id)
            self.assertIn(
                "Decider label: Ruled by Captain JP", block,
                entry_id)
            self.assertNotIn("decider not recorded", block,
                             entry_id)

    def test_pin_listing_carries_no_not_recorded_line(self):
        _model, output = h.cached_pipeline("PIN")
        text = h.render_text(output, "render")
        self.assertEqual(text.count("Decider: decider not recorded"), 0)


class DeciderListingGuardTest(unittest.TestCase):
    """The not recorded form stands where no decider stands
    in any accepted form."""

    def test_synthetic_no_decider_entry_keeps_not_recorded(self):
        output, blocks = _render_blocks(NO_DECIDER_FORM)
        block = _block_for(blocks, "DQ-965")
        self.assertIn("Decider: decider not recorded", block)
        self.assertEqual(len(_decider_findings(output, "DQ-965")), 1)

    def test_f11_no_decider_fixture_keeps_not_recorded(self):
        _model, output = h.cached_pipeline("F-11")
        text = h.render_text(output, "render")
        self.assertIn("Decider: decider not recorded", text)
        self.assertEqual(len(_decider_findings(output, "DQ-001")), 1)

    def test_pin_open_entry_carries_no_decider_label_line(self):
        # DQ-164 derives Open: its determining element is a tail
        # paragraph awaiting Captain JP, and no decider line of
        # either form stands in its listing, before or after.
        # The listing label fallback is scoped to decided
        # entries, the same scope as the not recorded annotation.
        _model, output = h.cached_pipeline("PIN")
        text = h.render_text(output, "render")
        block = _block_for(text.split("\n\n"), "DQ-164")
        self.assertNotIn("Decider label:", block)
        self.assertNotIn("Decider:", block)

    def test_f12_recorded_decider_is_listed(self):
        _model, output = h.cached_pipeline("F-12")
        text = h.render_text(output, "render")
        self.assertIn("Decider label: Ruled by Captain JP", text)
        self.assertNotIn("Decider: decider not recorded", text)


CONCAT_FORM = (
    "# Decision queue\n"
    "\n"
    "### DQ-301: the first part entry\n"
    "\n"
    "Status: Open\n"
    "\n"
    "The question: Which form stands?\n"
    "\n"
    "Options: the short form or the long form\n"
    "\n"
    "Cost of deciding late: low\n"
    "\n"
    "What it blocks: DQ-302\n"
    "\n"
    "# Decision queue\n"
    "\n"
    "### DQ-302: the second part entry\n"
    "\n"
    "Status: Open\n"
).encode("utf-8")


class DuplicatedQueueHeaderStandingFormTest(unittest.TestCase):
    """A20-F2 standing form: a second queue header stands as
    a file header unit and takes no finding."""

    def test_second_header_stands_as_a_file_header_unit(self):
        model, output = h.run_pipeline(CONCAT_FORM, name="concat.md")
        if output is None:
            self.fail("concatenated file took a failure result")
        units = h.as_list(h.get(model, "units"))
        headers = [unit for unit in units
                   if h.text_of(h.get(unit, "kind")) == "file header"]
        self.assertEqual(len(headers), 2)
        entries = [h.entry_identifier(entry)
                   for entry in h.entries_of(model)]
        self.assertEqual(entries, ["DQ-301", "DQ-302"])

    def test_second_header_takes_no_finding(self):
        _model, output = h.run_pipeline(CONCAT_FORM, name="concat.md")
        findings = h.findings_of(output)
        self.assertEqual(len(findings), 4)
        for finding in findings:
            self.assertEqual(h.finding_entry_id(finding), "DQ-302")
            self.assertEqual(h.finding_rule_number(finding), 9)


if __name__ == "__main__":
    unittest.main()
