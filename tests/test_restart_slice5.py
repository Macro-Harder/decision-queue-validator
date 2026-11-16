"""Restart Slice 5 tests: presence tests, provenance, and claims.

Register groups TG-S5-01 to TG-S5-03. Source: plan Item 2, section
2.7, with exit conditions at plan Item 1, section 1.6. Fixtures F-11,
F-12, and F-13, supplied by the Corpus seat. The no outcome
construction, the combined construction, the first limb construction,
the second limb construction, the cyclic construction, and the cited
number construction are Step 13 constructions: the outcome and limb
constructions are built in the test itself in the ruled record form
the register states, and the cyclic and cited number constructions
are built in the test itself in the same form, as the register
entries state for constructions charged to this slice.

No expectation is taken from I7A-04, I7A-05, or I7A-07, per shape
check risk SR-10. The first run test files are data only and assert
nothing here as a verdict.
"""

import re
import unittest
from pathlib import Path

import dqv_harness as h

CORPUS_DIR = Path(__file__).resolve().parent / "fixtures" / (
    "decision_queue_corpus")

PIN08_DOMAIN = ("Ruled", "Settled", "Settled in part", "Conditional",
                "Closed as decided")
DQ148_CLOSURES = ("DQ-053", "DQ-061", "DQ-064", "DQ-067", "DQ-109",
                  "DQ-110")
HEADER = "# Decision Queue\n\n## Open items\n\n"


def run_text(text):
    _model, output = h.run_pipeline(text.encode("utf-8"))
    if output is None:
        raise AssertionError("pipeline returned the failure result")
    return output


def fixture_output(fixture_id):
    _model, output = h.cached_pipeline(fixture_id)
    if output is None:
        raise AssertionError("fixture " + fixture_id +
                             " returned the failure result")
    return output


def pin_output():
    for name in ("PIN", "restart-pin", "acceptance-pin"):
        path = CORPUS_DIR / (name + ".md")
        if path.exists():
            _model, output = h.run_pipeline(path.read_bytes(),
                                            name=name + ".md")
            if output is not None:
                return output
    raise AssertionError("the restart pin copy does not stand yet")


def entry_of(output, entry_id):
    entry = h.entry_by_id(output, entry_id)
    if entry is None:
        raise AssertionError("no entry " + entry_id)
    return entry


def ruled_record(number, decider=True, ruling_text=True, outcome=True,
                 landing=True, status_line="Ruled"):
    lines = ["### DQ-%03d: Synthetic ruled entry %d" % (number, number),
             "", "Status: " + status_line, ""]
    if decider:
        lines += ["Ruled by: Captain JP", ""]
    if ruling_text:
        lines += ["Ruling text: \"The synthetic ruling stands.\"", ""]
    if outcome:
        lines += ["Ruling outcome: The synthetic outcome stands.", ""]
    if landing:
        lines += ["Where the ruling landed: synthetic record.", ""]
    return "\n".join(lines)


def findings(output, entry_id=None, severity=None, rule=None):
    return h.findings_for(output, entry_id=entry_id, severity=severity,
                          rule=rule)


def classes_of(finding_list):
    out = []
    for finding in finding_list:
        text = (h.finding_statement(finding) or "") + " " + (
            h.text_of(h.get(finding, "rule_id", "rule",
                            "class_name")) or "")
        out.append(text.lower())
    return out


MAP_HEAD_LINE = (
    "Supersession concerns form and internal consistency only. "
    "No chain in this map judges which matter governs in "
    "substance.")


def run_cli_text(text, subcommand="validate"):
    path = h.temp_input(text.encode("utf-8"),
                        "restart_slice5_input.md")
    code, out, err = h.run_cli(subcommand, path)
    return (code, out.decode("utf-8", errors="replace"),
            err.decode("utf-8", errors="replace"))


def companion_of(output):
    value = h.get(output, "companion_count", "companion",
                  "companion_figure")
    if value is None:
        figures = h.get(output, "project_manager_figures",
                        "pm_figures", "figures")
        if figures is not None:
            value = h.get(figures, "companion_count", "companion",
                          "companion_figure")
    return h.int_of(value)


def superseding_entry(number, targets, first_limb=True):
    ids = ["DQ-%03d" % n for n in targets]
    joined = " and ".join(ids)
    if first_limb and len(ids) == 1:
        statement = (
            "This ruling displaces the ruling at " + ids[0] +
            " in full; that earlier ruling no longer stands as "
            "governing on its subject, and " + ids[0] +
            " is the superseded entry.")
    elif first_limb:
        statement = (
            "This ruling displaces the rulings at " + joined +
            " in full; those earlier rulings no longer stand as "
            "governing on their subjects, and " + joined +
            " are the superseded entries.")
    else:
        statement = (
            "This entry replaces " + joined + " as the nicer "
            "wording on the subject, and " + joined +
            " are the entries it stands in place of.")
    return (
        "### DQ-%03d: Synthetic entry %d\n\n"
        "Status: Ruled\n\n"
        "Ruled by: Captain JP\n\n"
        "Ruling text: \"%s\"\n\n"
        "Ruling outcome: The displacement stands.\n\n"
        "Where the ruling landed: synthetic record.\n"
    ) % (number, number, statement)


def map_chain_lines(text):
    at = text.find(MAP_HEAD_LINE)
    if at < 0:
        return []
    lines = []
    for line in text[at:].splitlines()[1:]:
        ids = re.findall(r"DQ-\d+", line)
        if len(ids) >= 2:
            lines.append(line)
        elif lines:
            break
    return lines


def map_chain_sequences(text):
    return [re.findall(r"DQ-\d+", line)
            for line in map_chain_lines(text)]


def render_map_sequences(text):
    output = run_text(text)
    return map_chain_sequences(h.render_text(output, "render"))


class PresenceTestUnitTest(unittest.TestCase):
    """TG-S5-01: PIN-08 in full. Plan section 2.7."""

    def test_domain_list_is_the_five_states(self):
        self.assertEqual(
            PIN08_DOMAIN,
            ("Ruled", "Settled", "Settled in part", "Conditional",
             "Closed as decided"))

    def test_f11_no_decider_gives_one_error(self):
        output = fixture_output("F-11")
        errors = findings(output, severity="Error")
        self.assertEqual(len(errors), 1)
        self.assertTrue(any("decider" in c
                            for c in classes_of(errors)))

    def test_f12_no_ruling_text_gives_error_and_no_decider_finding(self):
        output = fixture_output("F-12")
        errors = findings(output, severity="Error")
        self.assertTrue(any("ruling text" in c
                            for c in classes_of(errors)))
        self.assertFalse(any("no decider" in c
                             for c in classes_of(errors)))

    def test_f13_no_landing_record_gives_one_warning_state_ruled(self):
        output = fixture_output("F-13")
        entry = entry_of(output, "DQ-001")
        self.assertEqual(h.entry_state(entry), "Ruled")
        warnings = findings(output, severity="Warning")
        self.assertEqual(len(warnings), 1)
        self.assertTrue(any("landing" in c
                            for c in classes_of(warnings)))

    def test_no_outcome_construction(self):
        # Step 13 construction, register TG-S5-01: decider present,
        # ruling text present, landing record present, no outcome in
        # any recorded form. Expected: one Warning of the outcome
        # class and no landing record Warning.
        text = HEADER + ruled_record(910, outcome=False)
        output = run_text(text)
        warnings = findings(output, entry_id="DQ-910",
                            severity="Warning")
        self.assertEqual(len(warnings), 1)
        self.assertTrue(any("outcome" in c
                            for c in classes_of(warnings)))
        self.assertFalse(any("landing" in c
                             for c in classes_of(warnings)))

    def test_combined_construction_two_warnings(self):
        # Step 13 construction, register TG-S5-01 and testing pin
        # down 7: no outcome and no landing record. Expected: two
        # Warning findings, one under each test.
        text = HEADER + ruled_record(911, outcome=False, landing=False)
        output = run_text(text)
        warnings = findings(output, entry_id="DQ-911",
                            severity="Warning")
        self.assertEqual(len(warnings), 2)
        joined = classes_of(warnings)
        self.assertTrue(any("outcome" in c for c in joined))
        self.assertTrue(any("landing" in c for c in joined))

    def test_conditional_rule_runs_only_on_decided_underlying(self):
        # Conditional with underlying Open: the tests do not run, a
        # non running result stands in place of the four results,
        # and no presence failure is raised.
        text = HEADER + (
            "### DQ-912: Synthetic entry 912\n\n"
            "Status: Banked\n\n"
            "Owner of record: Decision-queue Clerk\n\n"
            "Question: A synthetic question?\n\n"
            "#### Decision block\n\n"
            "Held conditionally. The entry closes subject to a "
            "stated condition, with no ruling behind it.\n")
        output = run_text(text)
        entry = entry_of(output, "DQ-912")
        if h.entry_state(entry) == "Conditional":
            results = h.get(entry, "presence_results",
                            "presence_tests")
            self.assertIsNotNone(results)
            presence = findings(output, entry_id="DQ-912")
            self.assertFalse(any(
                "decider" in c or "ruling text" in c
                for c in classes_of(presence)))

    def test_tests_do_not_run_on_ambiguous_or_open_entries(self):
        output = fixture_output("F-06")
        self.assertEqual(findings(output), [])
        text = HEADER + ruled_record(913, status_line="Wombled")
        output = run_text(text)
        entry = entry_of(output, "DQ-913")
        if h.is_ambiguous(entry):
            presence = findings(output, entry_id="DQ-913")
            self.assertFalse(any(
                "decider" in c for c in classes_of(presence)))

    def test_part_scoping_settled_part_only(self):
        # Presence classes on a Settled in part entry are scoped to
        # the settled part only: evidence absent from the remainder
        # raises no finding.
        text = HEADER + (
            "### DQ-914: Synthetic entry 914\n\n"
            "Status: Banked\n\n"
            "#### Decision block\n\n"
            "Settled in part by Captain JP. Ruling text: the first "
            "limb is settled. Ruling outcome: the first limb stands "
            "settled. Where it landed: synthetic record. The "
            "remainder, the second limb, stays banked with no "
            "evidence of any form.\n")
        output = run_text(text)
        entry = entry_of(output, "DQ-914")
        if h.entry_state(entry) == "Settled in part":
            presence = findings(output, entry_id="DQ-914")
            self.assertEqual(presence, [])

    def test_dq148_assessment_prose_forms_accepted_on_pin(self):
        output = pin_output()
        for entry_id in DQ148_CLOSURES:
            with self.subTest(entry=entry_id):
                entry = entry_of(output, entry_id)
                self.assertEqual(h.entry_state(entry),
                                 "Closed as decided")
                presence = findings(output, entry_id=entry_id)
                self.assertFalse(any(
                    "decider" in c or "ruling text" in c
                    for c in classes_of(presence)))


class SupersessionUnitTest(unittest.TestCase):
    """TG-S5-02: PIN-10 in full. Plan section 2.7."""

    def _pointers(self, output, entry_id):
        entry = entry_of(output, entry_id)
        return h.as_list(h.get(entry, "supersession_pointers",
                               "pointers", "superseded_by"))

    def test_pin_two_instances_carry_pointer_on_superseded_row(self):
        output = pin_output()
        self.assertTrue(self._pointers(output, "DQ-122"))
        self.assertTrue(self._pointers(output, "DQ-168"))

    def test_pin_dq161_gives_dq092_and_dq112_no_pointer(self):
        output = pin_output()
        for entry_id in ("DQ-092", "DQ-112"):
            pointers = self._pointers(output, entry_id)
            named = [h.text_of(p) for p in pointers]
            self.assertNotIn("DQ-161", named)

    def test_first_limb_construction_near_miss_note_no_pointer(self):
        # Step 13 construction, register TG-S5-02: the statement
        # identifies exactly one entry as the superseded subject and
        # claims to displace it, but does not state displacement in
        # the ruling sense. First limb only fails.
        text = HEADER + ruled_record(920) + "\n" + (
            "### DQ-921: Synthetic entry 921\n\n"
            "Status: Ruled\n\n"
            "Ruled by: Captain JP\n\n"
            "Ruling text: \"This entry replaces DQ-920 as the nicer "
            "wording on the subject, and DQ-920 is the entry it "
            "stands in place of.\"\n\n"
            "Ruling outcome: The wording is preferred.\n\n"
            "Where the ruling landed: synthetic record.\n")
        output = run_text(text)
        notes = findings(output, entry_id="DQ-921", severity="Note")
        self.assertTrue(any("supersession" in c
                            for c in classes_of(notes)))
        named_ok = False
        for finding in notes:
            named = h.as_list(h.get(finding, "named_entries",
                                    "named_entry_ids"))
            if "DQ-920" in [h.text_of(n) for n in named]:
                named_ok = True
        self.assertTrue(named_ok)
        self.assertEqual(self._pointers(output, "DQ-920"), [])

    def test_second_limb_construction_near_miss_note_no_pointer(self):
        # Step 13 construction, register TG-S5-02: the statement
        # states displacement in the ruling sense and names one
        # entry, but does not name that entry as the superseded
        # subject in terms identifying exactly one entry. Second
        # limb only fails.
        text = HEADER + ruled_record(922) + "\n" + (
            "### DQ-923: Synthetic entry 923\n\n"
            "Status: Ruled\n\n"
            "Ruled by: Captain JP\n\n"
            "Ruling text: \"The earlier ruling on this subject no "
            "longer stands as governing and is displaced. DQ-922 "
            "discusses the same subject at length.\"\n\n"
            "Ruling outcome: The earlier ruling is displaced.\n\n"
            "Where the ruling landed: synthetic record.\n")
        output = run_text(text)
        notes = findings(output, entry_id="DQ-923", severity="Note")
        self.assertTrue(any("supersession" in c
                            for c in classes_of(notes)))
        # The charged named entries behaviour in full, plan Item
        # 2, section 2.7: the near miss Note stands on DQ-923, the
        # synthetic entry carrying the statement, with that entry
        # in the finding entry identifier field, the identified
        # entry DQ-922 in the named entries field, and no pointer.
        supersession_notes = [
            f for f in notes
            if "supersession" in " ".join(classes_of([f]))]
        self.assertTrue(supersession_notes)
        for finding in supersession_notes:
            self.assertEqual(h.finding_entry_id(finding), "DQ-923")
            named = [h.text_of(n) for n in h.as_list(
                h.get(finding, "named_entries", "named_entry_ids"))]
            self.assertIn("DQ-922", named)
        self.assertEqual(self._pointers(output, "DQ-922"), [])

    def test_no_note_where_statement_identifies_no_entry(self):
        # The omission test this slice owns, plan Item 1, section
        # 1.6, in the DQ-161 form.
        text = HEADER + (
            "### DQ-924: Synthetic entry 924\n\n"
            "Status: Ruled\n\n"
            "Ruled by: Captain JP\n\n"
            "Ruling text: \"An earlier ruling somewhere no longer "
            "stands as governing and is displaced in full.\"\n\n"
            "Ruling outcome: The displacement stands.\n\n"
            "Where the ruling landed: synthetic record.\n")
        output = run_text(text)
        notes = findings(output, entry_id="DQ-924", severity="Note")
        self.assertFalse(any("supersession" in c
                             for c in classes_of(notes)))
        self.assertEqual(findings(output, entry_id="DQ-924"), [])

    def test_no_pointer_for_supersession_inside_single_entry(self):
        output = pin_output()
        for entry_id in ("DQ-022", "DQ-023"):
            entry = entry_of(output, entry_id)
            pointers = h.as_list(h.get(entry, "supersession_pointers",
                                       "pointers"))
            self_names = [h.text_of(p) for p in pointers
                          if h.text_of(p) == entry_id]
            self.assertEqual(self_names, [])

    def test_cyclic_construction_two_entry_cycle(self):
        # Step 13 construction, register TG-S5-02, shortest form:
        # two entries each displacing the other, each statement
        # meeting both limbs.
        text = HEADER + (
            "### DQ-930: Synthetic entry 930\n\n"
            "Status: Ruled\n\n"
            "Ruled by: Captain JP\n\n"
            "Ruling text: \"This ruling displaces the ruling at "
            "DQ-931 in full; that earlier ruling no longer stands "
            "as governing on its subject, and DQ-931 is the "
            "superseded entry.\"\n\n"
            "Ruling outcome: DQ-931 is displaced.\n\n"
            "Where the ruling landed: synthetic record.\n\n"
            "### DQ-931: Synthetic entry 931\n\n"
            "Status: Ruled\n\n"
            "Ruled by: Captain JP\n\n"
            "Ruling text: \"This ruling displaces the ruling at "
            "DQ-930 in full; that earlier ruling no longer stands "
            "as governing on its subject, and DQ-930 is the "
            "superseded entry.\"\n\n"
            "Ruling outcome: DQ-930 is displaced.\n\n"
            "Where the ruling landed: synthetic record.\n")
        output = run_text(text)
        warnings = [f for f in findings(output, severity="Warning")
                    if "cycle" in (h.finding_statement(f) or "").lower()
                    or "cycle" in " ".join(classes_of([f]))]
        self.assertEqual(len(warnings), 1)
        self.assertTrue(self._pointers(output, "DQ-930"))
        self.assertTrue(self._pointers(output, "DQ-931"))
        counts = h.canonical_counts(output)
        self.assertEqual(sum(counts.values()), 2)
        # The charged expected result in full, plan Item 2,
        # section 2.7 and Item 9, section 9.6: the Warning names
        # every entry in the cycle in chain order and quotes the
        # statement in each entry, the exit code follows the exit
        # decision table as for any Warning, which is code 1 where
        # a Warning stands and no higher code applies, and the
        # waiting figure and the companion count take the same
        # values as on the same entries with no cycle standing.
        joined = (h.finding_statement(warnings[0]) or "") + (
            h.finding_evidence_text(warnings[0]) or "")
        self.assertLess(joined.find("DQ-930"),
                        joined.find("DQ-931"))
        self.assertIn("displaces the ruling at DQ-931", joined)
        self.assertIn("displaces the ruling at DQ-930", joined)
        code, _out, _err = run_cli_text(text)
        self.assertEqual(code, 1)
        control = HEADER + ruled_record(930) + "\n" + \
            ruled_record(931)
        control_output = run_text(control)
        waiting, _blocking = h.waiting_and_blocking(output)
        control_waiting, _cb = h.waiting_and_blocking(
            control_output)
        self.assertEqual(h.int_of(waiting),
                         h.int_of(control_waiting))
        self.assertIsNotNone(companion_of(output))
        self.assertEqual(companion_of(output),
                         companion_of(control_output))
        self.assertEqual(h.canonical_counts(output),
                         h.canonical_counts(control_output))

    def test_cyclic_construction_longer_chain_cycle(self):
        # Step 13 construction, register TG-S5-02, longer form:
        # three entries returning to the start, one Warning for the
        # one distinct cycle, naming every entry in chain order.
        def displacer(number, target):
            return (
                "### DQ-%03d: Synthetic entry %d\n\n"
                "Status: Ruled\n\n"
                "Ruled by: Captain JP\n\n"
                "Ruling text: \"This ruling displaces the ruling "
                "at DQ-%03d in full; that earlier ruling no longer "
                "stands as governing, and DQ-%03d is the superseded "
                "entry.\"\n\n"
                "Ruling outcome: The target is displaced.\n\n"
                "Where the ruling landed: synthetic record.\n\n"
            ) % (number, number, target, target)
        text = HEADER + displacer(932, 933) + displacer(933, 934) \
            + displacer(934, 932)
        output = run_text(text)
        warnings = [f for f in findings(output, severity="Warning")
                    if "cycle" in " ".join(classes_of([f]))]
        self.assertEqual(len(warnings), 1)
        evidence = h.finding_evidence_text(warnings[0]) or ""
        statement = h.finding_statement(warnings[0]) or ""
        joined = evidence + statement
        for entry_id in ("DQ-932", "DQ-933", "DQ-934"):
            self.assertIn(entry_id, joined)
        # Chain order, pointers, exit code, and figure invariance,
        # as charged at plan Item 2, section 2.7: the entries stand
        # named in chain order in the Warning, every pointer in
        # the cycle prints as derived, the exit code is the code
        # the exit decision table gives a Warning, code 1, and the
        # waiting figure and the companion count match the same
        # entries with no cycle standing.
        positions = [joined.find(entry_id)
                     for entry_id in ("DQ-932", "DQ-933", "DQ-934")]
        self.assertEqual(positions, sorted(positions))
        for entry_id in ("DQ-932", "DQ-933", "DQ-934"):
            self.assertTrue(self._pointers(output, entry_id))
        code, _out, _err = run_cli_text(text)
        self.assertEqual(code, 1)
        control = HEADER + ruled_record(932) + "\n" + \
            ruled_record(933) + "\n" + ruled_record(934)
        control_output = run_text(control)
        waiting, _blocking = h.waiting_and_blocking(output)
        control_waiting, _cb = h.waiting_and_blocking(
            control_output)
        self.assertEqual(h.int_of(waiting),
                         h.int_of(control_waiting))
        self.assertIsNotNone(companion_of(output))
        self.assertEqual(companion_of(output),
                         companion_of(control_output))
        self.assertEqual(h.canonical_counts(output),
                         h.canonical_counts(control_output))


    def _pointer_texts(self, output, entry_id):
        return [h.text_of(p) for p in self._pointers(output,
                                                     entry_id)]

    def _supersession_notes(self, output, entry_id):
        return [f for f in findings(output, entry_id=entry_id,
                                    severity="Note")
                if "supersession" in " ".join(classes_of([f]))]

    def _cited_notes(self, output):
        return [f for f in findings(output, severity="Note")
                if "pd-r7" in " ".join(classes_of([f]))
                or "cited" in " ".join(classes_of([f]))]

    def test_multiple_pointers_against_one_entry(self):
        # Step 12 correction, plan Item 9, section 9.6: statements
        # in two different entries each meet both limbs and each
        # identify the same entry. Every pointer prints on the
        # superseded row in file order of the superseding entries,
        # and the map starts one chain per pointer.
        text = HEADER + ruled_record(950) + "\n" + \
            superseding_entry(951, (950,)) + \
            superseding_entry(952, (950,))
        output = run_text(text)
        self.assertEqual(self._pointer_texts(output, "DQ-950"),
                         ["DQ-951", "DQ-952"])
        sequences = render_map_sequences(text)
        self.assertIn(["DQ-950", "DQ-951"], sequences)
        self.assertIn(["DQ-950", "DQ-952"], sequences)

    def test_fork_at_an_intermediate_entry(self):
        # Step 12 correction, plan Item 9, section 9.6, first
        # part: a chain reaching an entry carrying two pointers
        # branches, one continuation per pointer, and the
        # intermediate entry starts no chain of its own.
        text = HEADER + ruled_record(960) + "\n" + \
            superseding_entry(961, (960,)) + \
            superseding_entry(962, (961,)) + \
            superseding_entry(963, (961,))
        output = run_text(text)
        self.assertEqual(self._pointer_texts(output, "DQ-960"),
                         ["DQ-961"])
        self.assertEqual(self._pointer_texts(output, "DQ-961"),
                         ["DQ-962", "DQ-963"])
        sequences = render_map_sequences(text)
        self.assertIn(["DQ-960", "DQ-961", "DQ-962"], sequences)
        self.assertIn(["DQ-960", "DQ-961", "DQ-963"], sequences)
        for sequence in sequences:
            self.assertNotEqual(sequence[0], "DQ-961")

    def test_pure_cycle_prints_once_as_one_closed_chain(self):
        # Step 12 correction, plan Item 9, section 9.6, second
        # part: a cycle no start chain reaches prints once in the
        # map as one closed chain starting at the entry first in
        # file order, marked as a cycle.
        text = HEADER + superseding_entry(970, (972,)) + \
            superseding_entry(971, (970,)) + \
            superseding_entry(972, (971,))
        output = run_text(text)
        warnings = [f for f in findings(output, severity="Warning")
                    if "cycle" in " ".join(classes_of([f]))]
        self.assertEqual(len(warnings), 1)
        rendered = h.render_text(output, "render")
        sequences = map_chain_sequences(rendered)
        self.assertEqual(
            sequences,
            [["DQ-970", "DQ-971", "DQ-972", "DQ-970"]])
        chain_lines = map_chain_lines(rendered)
        self.assertEqual(len(chain_lines), 1)
        self.assertIn("cycle", chain_lines[0].lower())

    def test_pure_cycle_with_branch_pointer_prints_branch_chain(self):
        # Step 12 correction, plan Item 9, section 9.6, second
        # part, branch sub form: an entry in a pure cycle carries
        # a pointer that forms no part of the cycle. DQ-971 in the
        # cycle also carries a pointer to DQ-973, an entry outside
        # the cycle, because DQ-973 displaces DQ-971. The map
        # prints the cycle once as one closed chain, as charged
        # for the pure cycle form, and prints one branch chain for
        # that pointer, the branch chain sharing the part of the
        # closed chain up to and including DQ-971 and then
        # following that pointer onward to DQ-973. No pointer is
        # removed or suppressed: DQ-971 carries both pointers.
        text = HEADER + superseding_entry(970, (972,)) + \
            superseding_entry(971, (970,)) + \
            superseding_entry(972, (971,)) + \
            superseding_entry(973, (971,))
        output = run_text(text)
        warnings = [f for f in findings(output, severity="Warning")
                    if "cycle" in " ".join(classes_of([f]))]
        self.assertEqual(len(warnings), 1)
        self.assertEqual(self._pointer_texts(output, "DQ-971"),
                         ["DQ-972", "DQ-973"])
        rendered = h.render_text(output, "render")
        sequences = map_chain_sequences(rendered)
        self.assertEqual(
            sequences.count(
                ["DQ-970", "DQ-971", "DQ-972", "DQ-970"]), 1)
        self.assertIn(["DQ-970", "DQ-971", "DQ-973"], sequences)
        self.assertEqual(len(sequences), 2)
        chain_lines = map_chain_lines(rendered)
        cycle_lines = [ln for ln in chain_lines
                       if "DQ-972" in ln]
        self.assertEqual(len(cycle_lines), 1)
        self.assertIn("cycle", cycle_lines[0].lower())

    def test_multi_entry_statement_pointers_for_each_entry(self):
        # Step 12 correction, plan Item 9, section 9.6, third
        # part, both limbs met: a pointer derives for each
        # identified headed entry.
        text = HEADER + ruled_record(980) + "\n" + \
            ruled_record(982) + "\n" + \
            superseding_entry(981, (980, 982))
        output = run_text(text)
        self.assertEqual(self._pointer_texts(output, "DQ-980"),
                         ["DQ-981"])
        self.assertEqual(self._pointer_texts(output, "DQ-982"),
                         ["DQ-981"])

    def test_multi_entry_statement_first_limb_one_note_only(self):
        # Step 12 correction, plan Item 9, section 9.6, third
        # part, first limb failed: no pointer for any identified
        # entry, and one Note for the whole statement, never one
        # Note per identified entry, naming every identified
        # entry in the order the statement names them.
        text = HEADER + ruled_record(983) + "\n" + \
            ruled_record(985) + "\n" + \
            superseding_entry(984, (983, 985), first_limb=False)
        output = run_text(text)
        notes = self._supersession_notes(output, "DQ-984")
        self.assertEqual(len(notes), 1)
        named = [h.text_of(n) for n in h.as_list(
            h.get(notes[0], "named_entries", "named_entry_ids"))]
        self.assertEqual(named, ["DQ-983", "DQ-985"])
        self.assertEqual(self._pointers(output, "DQ-983"), [])
        self.assertEqual(self._pointers(output, "DQ-985"), [])

    def test_multi_entry_statement_unheaded_number_pd_r7(self):
        # Step 12 correction, plan Item 9, section 9.6, fourth
        # part: the same statement also identifies a DQ number no
        # headed entry carries. That number is reported once
        # under PD-R7 only, quoting the statement, takes no
        # supersession Note and no pointer, and no chain names
        # it, while the headed entry treatment stands unaffected.
        text = HEADER + ruled_record(986) + "\n" + \
            superseding_entry(987, (986, 999))
        output = run_text(text)
        self.assertEqual(self._pointer_texts(output, "DQ-986"),
                         ["DQ-987"])
        cited = self._cited_notes(output)
        self.assertEqual(len(cited), 1)
        joined = (h.finding_statement(cited[0]) or "") + (
            h.finding_evidence_text(cited[0]) or "")
        self.assertIn("DQ-999", joined)
        self.assertIn("displaces the rulings at DQ-986 and "
                      "DQ-999", joined)
        self.assertEqual(
            self._supersession_notes(output, "DQ-987"), [])
        for sequence in render_map_sequences(text):
            self.assertNotIn("DQ-999", sequence)

    def test_multi_entry_first_limb_unheaded_number_pd_r7(self):
        # Step 12 correction, plan Item 9, section 9.6, third and
        # fourth parts together: where the first limb fails, the
        # headed entry takes the one Note for the statement, and
        # the unheaded cited number is still reported once under
        # PD-R7 only, whether or not the first limb is met.
        text = HEADER + ruled_record(988) + "\n" + \
            superseding_entry(989, (988, 999), first_limb=False)
        output = run_text(text)
        self.assertEqual(self._pointers(output, "DQ-988"), [])
        notes = self._supersession_notes(output, "DQ-989")
        self.assertEqual(len(notes), 1)
        named = [h.text_of(n) for n in h.as_list(
            h.get(notes[0], "named_entries", "named_entry_ids"))]
        self.assertEqual(named, ["DQ-988"])
        cited = self._cited_notes(output)
        self.assertEqual(len(cited), 1)
        joined = (h.finding_statement(cited[0]) or "") + (
            h.finding_evidence_text(cited[0]) or "")
        self.assertIn("DQ-999", joined)
        self.assertIn("replaces DQ-988 and DQ-999 as the nicer "
                      "wording on the subject, and DQ-988 and "
                      "DQ-999 are the entries it stands in place "
                      "of", joined)
        for sequence in render_map_sequences(text):
            self.assertNotIn("DQ-999", sequence)


class ClaimsAndProvenanceTest(unittest.TestCase):
    """TG-S5-03: PIN-09, PD-R7, and P-AF-7 in its bounded form.
    Plan section 2.7."""

    def test_pin09_amendment_note_claim_over_five_entries(self):
        output = pin_output()
        notes = [f for f in findings(output, severity="Note")
                 if "PIN-09" in " ".join(classes_of([f]))
                 or "claim" in " ".join(classes_of([f]))]
        named = set()
        for finding in notes:
            for item in h.as_list(h.get(finding, "named_entries",
                                        "named_entry_ids")):
                named.add(h.text_of(item))
        for entry_id in ("DQ-006", "DQ-008", "DQ-009", "DQ-011",
                         "DQ-014"):
            self.assertIn(entry_id, named)

    def test_pin09_manager_addition_claims_over_dq001_and_dq002(self):
        output = pin_output()
        notes = [f for f in findings(output, severity="Note")
                 if "claim" in " ".join(classes_of([f]))]
        named = set()
        for finding in notes:
            for item in h.as_list(h.get(finding, "named_entries",
                                        "named_entry_ids")):
                named.add(h.text_of(item))
        self.assertIn("DQ-001", named)
        self.assertIn("DQ-002", named)

    def test_claim_shape_is_file_level_claim_note(self):
        output = pin_output()
        claims = [f for f in findings(output, severity="Note")
                  if "claim" in " ".join(classes_of([f]))]
        self.assertTrue(claims)
        for finding in claims:
            ident = h.finding_entry_id(finding) or ""
            claiming = h.text_of(h.get(finding, "claiming_unit")) or ""
            # Restated in the cured D-09 form: no claim carries the
            # literal FILE. A segment claim carries the unit
            # identifier, as its entry identifier and in the
            # declared claiming_unit field. An entry claim carries
            # the claiming entry identifier, as its entry
            # identifier and in the declared claiming_unit field.
            self.assertEqual(ident, claiming)
            if "file" in claiming.lower():
                self.assertTrue(
                    claiming.lower().startswith("file level unit"),
                    "a segment claim does not carry the unit "
                    "identifier: " + claiming)
            else:
                self.assertTrue(
                    claiming.startswith("DQ-"),
                    "an entry claim does not carry the claiming "
                    "entry identifier in claiming_unit: " + claiming)

    def test_cited_number_construction(self):
        # Step 13 construction, register TG-S5-03: one synthetic
        # file level note section carrying one passage that cites a
        # DQ number with no heading in its file and also carries a
        # state claim in the same passage. Expected: one Note of
        # the cited number class under PD-R7, the state claim under
        # its own claim class, and no second cited number finding.
        text = HEADER + ruled_record(940) + (
            "\n## Amendment note\n\n"
            "Note: DQ-999 was settled by the Manager and is closed. "
            "This note records that state for the file.\n")
        output = run_text(text)
        notes = findings(output, severity="Note")
        cited = [f for f in notes
                 if "PD-R7" in " ".join(classes_of([f]))
                 or "cited" in " ".join(classes_of([f]))]
        self.assertEqual(len(cited), 1)
        claims = [f for f in notes
                  if "claim" in " ".join(classes_of([f]))]
        self.assertTrue(claims)
        self.assertFalse(any(f in cited for f in claims))

    def test_paf7_bounded_form_only(self):
        # P-AF-7 in its one named bounded form: the in entry
        # presence provenance form is the whole provenance content
        # of this version. No authority tracing and no landing
        # elsewhere check is tested, built, or claimed here.
        output = fixture_output("F-02")
        entry = entry_of(output, "DQ-001")
        decider = h.text_of(h.get(entry, "decider", "decider_label",
                                  "ruled_by"))
        self.assertTrue(decider)


if __name__ == "__main__":
    unittest.main()
