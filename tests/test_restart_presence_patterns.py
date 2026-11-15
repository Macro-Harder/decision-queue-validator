"""Restart presence pattern table. I7A-04, taken up in its
recorded form.

Source: design/steps/step-07r-imagination-1.md at I7A-04, the
register at section 5, item I7A-04, and plan Item 2, section 2.7
for the four presence tests and their grades. This file is a
fixture design aid in test form: one table driven test enumerates
all sixteen patterns of the four presence facts for an entry in
the PIN-08 domain and asserts, per pattern, the exact finding set
and grades the four tests produce.

The four facts are decider, ruling text, outcome, and landing
record, each present or absent. The charged finding set per
pattern is the union of the single fact results: Error for no
decider, Error for no ruling text, Warning for no outcome,
Warning for no landing record, and no finding for a present fact.

Stated inputs to the table, unchanged by it: domain scoping, the
tests run on an entry whose derived state stands in the PIN-08
domain list, and every pattern entry in this table is a Ruled
entry in the ruled record form; part scoping, no pattern entry
carries a part state, so no part scoping narrows any row;
the exclusion of Ambiguous entries, no pattern entry reports as
Ambiguous, so no row is excluded; and the accepted assessment
prose forms, which stand as stated inputs and are not varied
here, every pattern entry using the recorded label forms for the
facts it carries.
"""

import unittest

import dqv_harness as h

HEADER = "# Decision Queue\n\n## Open items\n\n"

# The sixteen patterns, in one fixed order: decider, ruling text,
# outcome, and landing record, present read as True and absent
# read as False, followed by the expected presence findings for
# the pattern as (fact keyword, severity) pairs.
PATTERNS = (
    (True, True, True, True, ()),
    (True, True, True, False, (("landing", "Warning"),)),
    (True, True, False, True, (("outcome", "Warning"),)),
    (True, True, False, False,
     (("outcome", "Warning"), ("landing", "Warning"))),
    (True, False, True, True, (("ruling text", "Error"),)),
    (True, False, True, False,
     (("ruling text", "Error"), ("landing", "Warning"))),
    (True, False, False, True,
     (("ruling text", "Error"), ("outcome", "Warning"))),
    (True, False, False, False,
     (("ruling text", "Error"), ("outcome", "Warning"),
      ("landing", "Warning"))),
    (False, True, True, True, (("decider", "Error"),)),
    (False, True, True, False,
     (("decider", "Error"), ("landing", "Warning"))),
    (False, True, False, True,
     (("decider", "Error"), ("outcome", "Warning"))),
    (False, True, False, False,
     (("decider", "Error"), ("outcome", "Warning"),
      ("landing", "Warning"))),
    (False, False, True, True,
     (("decider", "Error"), ("ruling text", "Error"))),
    (False, False, True, False,
     (("decider", "Error"), ("ruling text", "Error"),
      ("landing", "Warning"))),
    (False, False, False, True,
     (("decider", "Error"), ("ruling text", "Error"),
      ("outcome", "Warning"))),
    (False, False, False, False,
     (("decider", "Error"), ("ruling text", "Error"),
      ("outcome", "Warning"), ("landing", "Warning"))),
)

FACT_KEYWORDS = ("decider", "ruling text", "outcome", "landing")


def ruled_record(number, decider=True, ruling_text=True,
                 outcome=True, landing=True):
    lines = ["### DQ-%03d: Synthetic ruled entry %d"
             % (number, number), "", "Status: Ruled", ""]
    if decider:
        lines += ["Ruled by: Captain JP", ""]
    if ruling_text:
        lines += ["Ruling text: \"The synthetic ruling stands.\"",
                  ""]
    if outcome:
        lines += ["Ruling outcome: The synthetic outcome stands.",
                  ""]
    if landing:
        lines += ["Where the ruling landed: synthetic record.", ""]
    return "\n".join(lines)


def run_text(text):
    _model, output = h.run_pipeline(text.encode("utf-8"))
    if output is None:
        raise AssertionError("pipeline returned the failure result")
    return output


def classes_of(finding_list):
    out = []
    for finding in finding_list:
        text = (h.finding_statement(finding) or "") + " " + (
            h.text_of(h.get(finding, "rule_id", "rule",
                            "class_name")) or "")
        out.append(text.lower())
    return out


class PresencePatternTableTest(unittest.TestCase):
    """I7A-04: the presence tests as one exhaustive pattern
    table, sixteen patterns in one table driven test."""

    def test_all_sixteen_presence_patterns(self):
        self.assertEqual(len(PATTERNS), 16)
        seen = set()
        for index, row in enumerate(PATTERNS):
            decider, ruling_text, outcome, landing, expected = row
            seen.add((decider, ruling_text, outcome, landing))
            number = 950 + index
            entry_id = "DQ-%03d" % number
            with self.subTest(
                    pattern=index + 1, decider=decider,
                    ruling_text=ruling_text, outcome=outcome,
                    landing=landing):
                text = HEADER + ruled_record(
                    number, decider=decider,
                    ruling_text=ruling_text, outcome=outcome,
                    landing=landing)
                output = run_text(text)
                entry_findings = h.findings_for(
                    output, entry_id=entry_id)
                joined = classes_of(entry_findings)
                observed = {}
                presence_count = 0
                for finding, class_text in zip(
                        entry_findings, joined):
                    matched = [keyword for keyword in FACT_KEYWORDS
                               if keyword in class_text]
                    if not matched:
                        continue
                    presence_count += 1
                    for keyword in matched:
                        observed[keyword] = h.finding_severity(
                            finding)
                self.assertEqual(
                    observed, dict(expected),
                    "pattern %d presence findings stand as %s, "
                    "not the charged set %s"
                    % (index + 1, observed, dict(expected)))
                self.assertEqual(
                    presence_count, len(expected),
                    "pattern %d carries %d presence findings, "
                    "not the charged %d"
                    % (index + 1, presence_count, len(expected)))
        self.assertEqual(len(seen), 16)


if __name__ == "__main__":
    unittest.main()
