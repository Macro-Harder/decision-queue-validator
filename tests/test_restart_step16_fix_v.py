"""Restart Step 16 fix wave 7, Fix seat V tests.

Seat V owns the merged findings A7-2-1 (Auditor 2,
confirmation round 7, design/steps/step-16r-audit7-2.md,
section 3) and A7-8-1 (Auditor 8, confirmation round 7,
design/steps/step-16r-audit7-8.md, section 2 and its
findings list), triaged at step record section 24: name
only matter in neighbouring spellings still satisfies the
matter condition Fix Seat S built in the helper
_labelled_matter_tokens, because the residue lives in the
helper's three exact conditions (a break inside one word
only; a surname only where exactly one further word
stands; that word only where capitalised). The forms
Auditor 2 evidences are a lowercase surname in "Ruled:
J.P. morgan", two capitalised name words in "J.P. Morgan
Stanley" and "J.P. Mary Morgan", spaced initials in
"Captain J. P." and "J. P. Morgan", and the attribution
word split by a space in "Cap tain JP". The further
spellings Auditor 8 evidences are space splits of the
grant names, a surname split by a space in "J.P. Mor
gan", initials separated by a comma, spaced slash and
hyphen forms, two lowercase name words, and "Cap tain
J.P.". Both limbs call the one helper, and Auditor 8
evidenced the family agreeing across the labelled
paragraph block and the element limb form by form.

The triage ground, at step record section 24, on PIN-08
as ruled at section 21: a label carrying only an
attribution records no ruling text, and the attribution
restated as name only matter, in any spelling the helper
does not yet read as attribution, is the same attribution
and not ruling matter.

Each test below pins the specified behaviour, written
before the cure. The name only form tests fail before the
cure and pass after it, in the labelled paragraph block
and in the element limb alike. The guard tests pass
before and after: genuine ruling matter in every standing
form keeps passing, including genuine matter standing
beside a name in these spellings; the stated bounds the
earlier seats recorded stand unmoved (an unrecorded name
alone, a number alone, a gibberish token, one thin
lowercase word beside fragmented initials, and a
hyphenated genuine word each still pass); fixture F-12
keeps exactly its one ruling text Error; the eight
compact form entries of the corpus pin keep taking no
ruling text Error; and the pin totals stand.

Copyright: J.P. Picard aka Macro-Harder
"""

import unittest

import dqv_harness as h


def _decided_entry(entry_id, ruling_paragraph,
                   decider_sentence=None, closing="Status: closed."):
    if decider_sentence is None:
        decider_sentence = (
            "Ruled by Captain JP in the roles chat on 2026-11-14.")
    text = (
        "# Decision queue\n"
        "\n"
        "### %s: the checker note form\n"
        "\n"
        "Status: Banked\n"
        "\n"
        "%s\n"
        "\n"
        "%s\n"
        "\n"
        "Landed: the checker note in NOTES.md section 2 now "
        "states the agreed form.\n"
        "\n"
        "%s\n"
    ) % (entry_id, decider_sentence, ruling_paragraph, closing)
    return text.encode("utf-8")


SETTLED_DECIDER = (
    "Settled by the Manager under the grant, recorded in the "
    "roles chat on 2026-11-14.")

GENUINE_RULED = _decided_entry(
    "DQ-700", "Ruled: the checker note takes the short form.")

GENUINE_SETTLED = _decided_entry(
    "DQ-701", "Settled: the checker note takes the short form.",
    decider_sentence=SETTLED_DECIDER)

BLOCK_FORM = (
    "# Decision queue\n"
    "\n"
    "### DQ-702: the harbour consequence\n"
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


CLOSING_PROSE_FORM = (
    "## DQ-703: the harbour store note. RULED by Captain JP "
    "2026-11-15\n"
    "\n"
    "Origin: the harbour store question in the Clerk note of "
    "2026-11-14. Captain JP ruled in her own words: \"Keep the "
    "store by the harbour gate.\" Ruled: the harbour store "
    "stands by the harbour gate, and the night keeper holds "
    "its key. Landed: the harbour store paragraph in the Clerk "
    "note now states the gate form. Status: closed.\n"
).encode("utf-8")


LABELLED_NAME_ONLY_FORMS = (
    ("DQ-710", "Ruled: J.P. morgan", None),
    ("DQ-711", "Ruled: J.P. Morgan Stanley", None),
    ("DQ-712", "Ruled: J.P. Mary Morgan", None),
    ("DQ-713", "Ruled: Captain J. P.", None),
    ("DQ-714", "Ruled: J. P. Morgan", None),
    ("DQ-715", "Ruled: Cap tain JP", None),
    ("DQ-716", "Settled: Captain J. P.", SETTLED_DECIDER),
    ("DQ-717", "Settled: J. P. Morgan", SETTLED_DECIDER),
    ("DQ-718", "Settled: J. P.", SETTLED_DECIDER),
    ("DQ-719", "Ruled: the Man ager decided.", None),
    ("DQ-720", "Ruled: Gra nt", None),
    ("DQ-721", "Settled: Cap tain JP", SETTLED_DECIDER),
    ("DQ-722", "Ruled: J.P. Mor gan", None),
    ("DQ-723", "Ruled: J, P Morgan", None),
    ("DQ-724", "Ruled: J / P Morgan", None),
    ("DQ-725", "Ruled: J - P Morgan", None),
    ("DQ-726", "Ruled: J . P . Morgan", None),
    ("DQ-727", "Ruled: Captain J P", None),
    ("DQ-728", "Ruled: J.P. morgan stanley", None),
    ("DQ-729", "Ruled: Captain J. P. Morgan", None),
    ("DQ-730", "Ruled: Cap tain J.P.", None),
)


ELEMENT_NAME_ONLY_FORMS = (
    ("DQ-740", "Ruled:\tJ.P. morgan", None),
    ("DQ-741", "Ruled:\tJ.P. Morgan Stanley", None),
    ("DQ-742", "Ruled:\tCaptain J. P.", None),
    ("DQ-743", "Ruled:\tJ. P. Morgan", None),
    ("DQ-744", "Ruled:\tCap tain JP", None),
    ("DQ-745", "Settled:\tCaptain J. P.", SETTLED_DECIDER),
    ("DQ-746", "Settled:\tJ. P. Morgan", SETTLED_DECIDER),
    ("DQ-747", "Ruled:\tthe Man ager decided.", None),
    ("DQ-748", "Ruled:\tJ.P. Mor gan", None),
    ("DQ-749", "Ruled:\tJ, P Morgan", None),
    ("DQ-750", "```\nRuled: Cap tain JP\n```", None),
    ("DQ-751", "```\nRuled: J.P. morgan\n```", None),
    ("DQ-752", "```\nRuled: J. P. Morgan\n```", None),
    ("DQ-753", "```\nSettled: J. P. Morgan\n```", SETTLED_DECIDER),
    ("DQ-754", "```\nRuled: J.P. Morgan Stanley\n```", None),
    ("DQ-755", "```\nRuled: J / P Morgan\n```", None),
    ("DQ-756", "```\nRuled: Gra nt\n```", None),
    ("DQ-757", "> Ruled: Cap tain JP", None),
    ("DQ-758", "> Ruled: J. P. Morgan", None),
    ("DQ-759", "The meeting ended at noon. Ruled: Cap tain JP", None),
    ("DQ-760", "The meeting ended at noon. Ruled: J.P. morgan", None),
    ("DQ-761", "The meeting ended at noon. Settled: J. P. Morgan",
     SETTLED_DECIDER),
)


def _ruling_text_errors(output, entry_id):
    found = []
    for finding in h.findings_for(output, entry_id=entry_id, rule=5):
        statement = h.finding_statement(finding) or ""
        if "No ruling text" in statement:
            found.append(finding)
    return found


def _rule5_findings(output, entry_id):
    return h.findings_for(output, entry_id=entry_id, rule=5)


class LabelledNameOnlyFormTest(unittest.TestCase):
    """A7-2-1 and A7-8-1 in the labelled paragraph block: a
    "Ruled:" or "Settled:" labelled paragraph whose only
    matter is the decider attribution with its name in a
    neighbouring spelling records no ruling text, and the
    decided entry takes the rule 5 ruling text Error."""

    def _assert_name_only_form_errors(self, entry_id, paragraph,
                                      decider_sentence):
        data = _decided_entry(
            entry_id, paragraph, decider_sentence=decider_sentence)
        _model, output = h.run_pipeline(data, name="probe.md")
        found = _ruling_text_errors(output, entry_id)
        self.assertEqual(len(found), 1, entry_id)
        self.assertEqual(h.finding_severity(found[0]), "Error")

    def test_lowercase_surname_takes_the_error(self):
        self._assert_name_only_form_errors(*LABELLED_NAME_ONLY_FORMS[0])

    def test_two_capitalised_name_words_takes_the_error(self):
        self._assert_name_only_form_errors(*LABELLED_NAME_ONLY_FORMS[1])

    def test_two_capitalised_name_words_first_name_takes_the_error(self):
        self._assert_name_only_form_errors(*LABELLED_NAME_ONLY_FORMS[2])

    def test_spaced_initials_after_captain_takes_the_error(self):
        self._assert_name_only_form_errors(*LABELLED_NAME_ONLY_FORMS[3])

    def test_spaced_initials_with_surname_takes_the_error(self):
        self._assert_name_only_form_errors(*LABELLED_NAME_ONLY_FORMS[4])

    def test_space_split_captain_takes_the_error(self):
        self._assert_name_only_form_errors(*LABELLED_NAME_ONLY_FORMS[5])

    def test_settled_spaced_initials_after_captain_takes_the_error(self):
        self._assert_name_only_form_errors(*LABELLED_NAME_ONLY_FORMS[6])

    def test_settled_spaced_initials_with_surname_takes_the_error(self):
        self._assert_name_only_form_errors(*LABELLED_NAME_ONLY_FORMS[7])

    def test_settled_spaced_initials_alone_takes_the_error(self):
        self._assert_name_only_form_errors(*LABELLED_NAME_ONLY_FORMS[8])

    def test_space_split_manager_takes_the_error(self):
        self._assert_name_only_form_errors(*LABELLED_NAME_ONLY_FORMS[9])

    def test_space_split_grant_takes_the_error(self):
        self._assert_name_only_form_errors(*LABELLED_NAME_ONLY_FORMS[10])

    def test_settled_space_split_captain_takes_the_error(self):
        self._assert_name_only_form_errors(*LABELLED_NAME_ONLY_FORMS[11])

    def test_space_split_surname_takes_the_error(self):
        self._assert_name_only_form_errors(*LABELLED_NAME_ONLY_FORMS[12])

    def test_comma_separated_initials_takes_the_error(self):
        self._assert_name_only_form_errors(*LABELLED_NAME_ONLY_FORMS[13])

    def test_spaced_slash_initials_takes_the_error(self):
        self._assert_name_only_form_errors(*LABELLED_NAME_ONLY_FORMS[14])

    def test_spaced_hyphen_initials_takes_the_error(self):
        self._assert_name_only_form_errors(*LABELLED_NAME_ONLY_FORMS[15])

    def test_spaced_points_initials_takes_the_error(self):
        self._assert_name_only_form_errors(*LABELLED_NAME_ONLY_FORMS[16])

    def test_unpunctuated_initials_takes_the_error(self):
        self._assert_name_only_form_errors(*LABELLED_NAME_ONLY_FORMS[17])

    def test_two_lowercase_name_words_takes_the_error(self):
        self._assert_name_only_form_errors(*LABELLED_NAME_ONLY_FORMS[18])

    def test_spaced_initials_captain_with_surname_takes_the_error(self):
        self._assert_name_only_form_errors(*LABELLED_NAME_ONLY_FORMS[19])

    def test_space_split_captain_beside_initials_takes_the_error(self):
        self._assert_name_only_form_errors(*LABELLED_NAME_ONLY_FORMS[20])


class ElementNameOnlyFormTest(unittest.TestCase):
    """A7-8-1 in the element limb: the same name only
    matters, in the tab, fenced, blockquoted and prose
    spellings parse classifies as a closing prose element,
    record no ruling text through that limb either, the two
    limbs agreeing form by form because both call the one
    helper."""

    def _assert_name_only_form_errors(self, entry_id, paragraph,
                                      decider_sentence):
        data = _decided_entry(
            entry_id, paragraph, decider_sentence=decider_sentence)
        _model, output = h.run_pipeline(data, name="probe.md")
        found = _ruling_text_errors(output, entry_id)
        self.assertEqual(len(found), 1, entry_id)
        self.assertEqual(h.finding_severity(found[0]), "Error")

    def test_tab_lowercase_surname_takes_the_error(self):
        self._assert_name_only_form_errors(*ELEMENT_NAME_ONLY_FORMS[0])

    def test_tab_two_capitalised_name_words_takes_the_error(self):
        self._assert_name_only_form_errors(*ELEMENT_NAME_ONLY_FORMS[1])

    def test_tab_spaced_initials_after_captain_takes_the_error(self):
        self._assert_name_only_form_errors(*ELEMENT_NAME_ONLY_FORMS[2])

    def test_tab_spaced_initials_with_surname_takes_the_error(self):
        self._assert_name_only_form_errors(*ELEMENT_NAME_ONLY_FORMS[3])

    def test_tab_space_split_captain_takes_the_error(self):
        self._assert_name_only_form_errors(*ELEMENT_NAME_ONLY_FORMS[4])

    def test_tab_settled_spaced_initials_captain_takes_the_error(self):
        self._assert_name_only_form_errors(*ELEMENT_NAME_ONLY_FORMS[5])

    def test_tab_settled_spaced_initials_surname_takes_the_error(self):
        self._assert_name_only_form_errors(*ELEMENT_NAME_ONLY_FORMS[6])

    def test_tab_space_split_manager_takes_the_error(self):
        self._assert_name_only_form_errors(*ELEMENT_NAME_ONLY_FORMS[7])

    def test_tab_space_split_surname_takes_the_error(self):
        self._assert_name_only_form_errors(*ELEMENT_NAME_ONLY_FORMS[8])

    def test_tab_comma_separated_initials_takes_the_error(self):
        self._assert_name_only_form_errors(*ELEMENT_NAME_ONLY_FORMS[9])

    def test_fenced_space_split_captain_takes_the_error(self):
        self._assert_name_only_form_errors(*ELEMENT_NAME_ONLY_FORMS[10])

    def test_fenced_lowercase_surname_takes_the_error(self):
        self._assert_name_only_form_errors(*ELEMENT_NAME_ONLY_FORMS[11])

    def test_fenced_spaced_initials_takes_the_error(self):
        self._assert_name_only_form_errors(*ELEMENT_NAME_ONLY_FORMS[12])

    def test_fenced_settled_spaced_initials_takes_the_error(self):
        self._assert_name_only_form_errors(*ELEMENT_NAME_ONLY_FORMS[13])

    def test_fenced_two_capitalised_name_words_takes_the_error(self):
        self._assert_name_only_form_errors(*ELEMENT_NAME_ONLY_FORMS[14])

    def test_fenced_spaced_slash_initials_takes_the_error(self):
        self._assert_name_only_form_errors(*ELEMENT_NAME_ONLY_FORMS[15])

    def test_fenced_space_split_grant_takes_the_error(self):
        self._assert_name_only_form_errors(*ELEMENT_NAME_ONLY_FORMS[16])

    def test_blockquote_space_split_captain_takes_the_error(self):
        self._assert_name_only_form_errors(*ELEMENT_NAME_ONLY_FORMS[17])

    def test_blockquote_spaced_initials_takes_the_error(self):
        self._assert_name_only_form_errors(*ELEMENT_NAME_ONLY_FORMS[18])

    def test_prose_space_split_captain_takes_the_error(self):
        self._assert_name_only_form_errors(*ELEMENT_NAME_ONLY_FORMS[19])

    def test_prose_lowercase_surname_takes_the_error(self):
        self._assert_name_only_form_errors(*ELEMENT_NAME_ONLY_FORMS[20])

    def test_prose_settled_spaced_initials_takes_the_error(self):
        self._assert_name_only_form_errors(*ELEMENT_NAME_ONLY_FORMS[21])


class GenuineFormGuardTest(unittest.TestCase):
    """The genuine forms keep passing: labelled paragraphs
    and closing prose elements carrying real ruling matter
    satisfy the test, and genuine matter standing beside a
    name in the neighbouring spellings is not silenced by
    the name beside it."""

    def _assert_no_ruling_text_error(self, entry_id, paragraph,
                                     decider_sentence=None):
        data = _decided_entry(
            entry_id, paragraph, decider_sentence=decider_sentence)
        _model, output = h.run_pipeline(data, name="probe.md")
        self.assertEqual(
            _ruling_text_errors(output, entry_id), [], entry_id)

    def test_ruled_paragraph_with_matter_takes_no_error(self):
        _model, output = h.run_pipeline(GENUINE_RULED, name="probe.md")
        self.assertEqual(_ruling_text_errors(output, "DQ-700"), [])
        self.assertEqual(_rule5_findings(output, "DQ-700"), [])

    def test_settled_paragraph_with_matter_takes_no_error(self):
        _model, output = h.run_pipeline(GENUINE_SETTLED, name="probe.md")
        self.assertEqual(_ruling_text_errors(output, "DQ-701"), [])
        self.assertEqual(_rule5_findings(output, "DQ-701"), [])

    def test_genuine_matter_after_lowercase_surname_still_passes(self):
        self._assert_no_ruling_text_error(
            "DQ-770", "Ruled: J.P. morgan takes the harbour.")

    def test_genuine_matter_after_spaced_initials_still_passes(self):
        self._assert_no_ruling_text_error(
            "DQ-771",
            "Ruled: Captain J. P. ruled that the checker note "
            "takes the short form.")

    def test_genuine_matter_after_space_split_name_still_passes(self):
        self._assert_no_ruling_text_error(
            "DQ-772", "Ruled: Cap tain JP takes the harbour.")

    def test_genuine_lowercase_words_beside_initials_still_pass(self):
        self._assert_no_ruling_text_error(
            "DQ-773", "Ruled: J.P. checker note")

    def test_fenced_genuine_matter_still_passes(self):
        self._assert_no_ruling_text_error(
            "DQ-774",
            "```\nRuled: the checker note takes the short form.\n```")

    def test_blockquote_genuine_matter_still_passes(self):
        self._assert_no_ruling_text_error(
            "DQ-775", "> Ruled: the checker note takes the short form.")

    def test_tab_genuine_matter_still_passes(self):
        self._assert_no_ruling_text_error(
            "DQ-776", "Ruled:\tthe checker note takes the short form.")

    def test_prose_paragraph_genuine_matter_still_passes(self):
        self._assert_no_ruling_text_error(
            "DQ-777",
            "The meeting ended at noon. Ruled: the checker note "
            "takes the short form.")


class StatedBoundGuardTest(unittest.TestCase):
    """The bounds the earlier seats stated stand unmoved:
    an unrecorded name alone, a number alone, and a
    gibberish token still pass, as do the attribution
    adjunct and smuggled content token forms; one thin
    lowercase word beside fragmented initials still passes,
    as Auditor 2 of round 7 ruled inside the bound at its
    case E6, and a hyphenated genuine word still passes on
    its runs, as Fix Seat S stated at its second edge."""

    def _assert_no_ruling_text_error(self, entry_id, paragraph,
                                     decider_sentence=None):
        data = _decided_entry(
            entry_id, paragraph, decider_sentence=decider_sentence)
        _model, output = h.run_pipeline(data, name="probe.md")
        self.assertEqual(
            _ruling_text_errors(output, entry_id), [], entry_id)

    def test_unrecorded_name_alone_still_passes(self):
        self._assert_no_ruling_text_error("DQ-780", "Ruled: Alice")

    def test_unrecorded_two_word_name_alone_still_passes(self):
        self._assert_no_ruling_text_error(
            "DQ-781", "Ruled: Morgan Stanley")

    def test_number_alone_still_passes(self):
        self._assert_no_ruling_text_error("DQ-782", "Ruled: 42.")

    def test_gibberish_token_still_passes(self):
        self._assert_no_ruling_text_error(
            "DQ-783", "Ruled: Captain JP xyzzy.")

    def test_attribution_adjunct_form_still_passes(self):
        self._assert_no_ruling_text_error(
            "DQ-784", "Ruled: Captain JP in the roles chat.")

    def test_smuggled_content_token_form_still_passes(self):
        self._assert_no_ruling_text_error(
            "DQ-785",
            "Ruled: Captain JP, the Manager under the grant, "
            "ruled settled decided closed, harbour.")

    def test_one_thin_lowercase_word_beside_initials_still_passes(self):
        self._assert_no_ruling_text_error(
            "DQ-786", "Ruled: J.P. harbour")

    def test_hyphenated_genuine_word_still_passes(self):
        self._assert_no_ruling_text_error("DQ-787", "Ruled: har-bour.")


class StandingPositionGuardTest(unittest.TestCase):
    """The positions the earlier seats established still
    hold: a whole attribution separated by punctuation and
    a sole capitalised surname beside fragmented initials
    still take the Error, fixture F-12 keeps exactly its
    one ruling text Error, the eight compact form entries
    keep their passes, the pin totals stand, and the level
    4 block and closing prose forms keep passing."""

    def _assert_one_ruling_text_error(self, entry_id, paragraph,
                                      decider_sentence=None):
        data = _decided_entry(
            entry_id, paragraph, decider_sentence=decider_sentence)
        _model, output = h.run_pipeline(data, name="probe.md")
        found = _ruling_text_errors(output, entry_id)
        self.assertEqual(len(found), 1, entry_id)
        self.assertEqual(h.finding_severity(found[0]), "Error")

    def test_separated_whole_attribution_still_takes_the_error(self):
        self._assert_one_ruling_text_error(
            "DQ-790",
            "Ruled: Captain, JP, Manager, under, the, grant.")

    def test_sole_capitalised_surname_still_takes_the_error(self):
        self._assert_one_ruling_text_error(
            "DQ-791", "Ruled: J.P. Harbour")

    def test_f12_keeps_exactly_one_ruling_text_error(self):
        _model, output = h.cached_pipeline("F-12")
        found = _ruling_text_errors(output, "DQ-001")
        self.assertEqual(len(found), 1)
        self.assertEqual(h.finding_severity(found[0]), "Error")
        self.assertEqual(len(_rule5_findings(output, "DQ-001")), 1)

    def test_pin_compact_form_entries_take_no_ruling_text_error(self):
        _model, output = h.cached_pipeline("PIN")
        for entry_id in ("DQ-147", "DQ-148", "DQ-149", "DQ-150",
                         "DQ-151", "DQ-152", "DQ-154", "DQ-155"):
            self.assertEqual(
                _ruling_text_errors(output, entry_id), [], entry_id)

    def test_pin_totals_stand(self):
        _model, output = h.cached_pipeline("PIN")
        counts = {"Error": 0, "Warning": 0, "Note": 0}
        for finding in h.findings_of(output):
            counts[h.finding_severity(finding)] += 1
        self.assertEqual(
            counts, {"Error": 16, "Warning": 57, "Note": 13})

    def test_level4_block_form_still_passes(self):
        _model, output = h.run_pipeline(BLOCK_FORM, name="probe.md")
        self.assertEqual(_rule5_findings(output, "DQ-702"), [])
        self.assertEqual(h.findings_of(output), [])

    def test_closing_prose_form_still_passes(self):
        _model, output = h.run_pipeline(
            CLOSING_PROSE_FORM, name="probe.md")
        self.assertEqual(_rule5_findings(output, "DQ-703"), [])


if __name__ == "__main__":
    unittest.main()
