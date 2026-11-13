"""Validate: the Queue file model plus the Vocabulary value.

The shapes validate hands to render are defined with the core types
and re-exported here: the Validate output, the Finding, the census
entry, the reconciliation block, the verbatim appendix row and the
Exit decision, together with the Vocabulary value validate is handed.

Validate is a pure function over values in memory. It is called with
the Queue file model and the Vocabulary value only; it never reads
the queue file directly and never re-splits a span. From the model it
derives the effective state of every entry, runs the checks as
predicates over the model, builds the census as its own type,
computes the reconciliation block once with its self check, and
forms the Exit decision.
"""

import re

from .types import (
    CensusEntry,
    DistinctPhrasingCount,
    EntryResult,
    ExitDecision,
    FileFactsData,
    Finding,
    HeadedEntryCount,
    ReconciliationBlock,
    SelfCheckResult,
    Span,
    ValidateOutput,
    VerbatimAppendixRow,
    Vocabulary,
)

__all__ = [
    "validate_model",
    "Vocabulary",
    "ValidateOutput",
    "EntryResult",
    "Finding",
    "CensusEntry",
    "ReconciliationBlock",
    "VerbatimAppendixRow",
    "ExitDecision",
    "FileFactsData",
    "SelfCheckResult",
    "HeadedEntryCount",
    "DistinctPhrasingCount",
]


FILE_ID = "FILE"

CANONICAL_STATES = (
    "Open",
    "Presented",
    "Parked",
    "Ruled",
    "Settled",
    "Settled in part",
    "Closed as decided",
    "Conditional",
)

DECIDED_STATES = (
    "Ruled",
    "Settled",
    "Settled in part",
    "Closed as decided",
    "Conditional",
)

_DECIDED_DISPOSITIONS = ("Ruled", "Settled", "Closed")
_STATUS_LINE_KINDS = ("head Status line", "later Status line")
_BLOCK_KINDS = ("decision block matter",)

_NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
    "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
    "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19,
    "twenty": 20,
}


def _get(obj, name, default=None):
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


def _display_id(entry):
    identifier = _get(entry, "identifier")
    if identifier:
        return identifier
    heading = _get(entry, "heading") or _get(entry, "heading_text") or ""
    return heading


def _entry_number(entry):
    identifier = _get(entry, "identifier") or ""
    match = re.fullmatch(r"DQ-(\d+)", identifier)
    if match:
        return int(match.group(1))
    return None


def _body_lines(entry):
    return list(_get(entry, "body_lines") or [])


def _body_text(entry):
    return "\n".join(text for _line, text in _body_lines(entry))


def _field_labels(entry):
    return [str(_get(f, "label", "") or "") for f in _get(entry, "fields") or []]


def _field_value(entry, label):
    for f in _get(entry, "fields") or []:
        if _get(f, "label") == label:
            return _get(f, "value") or ""
    return None


# ---------------------------------------------------------------------
# Unit 3a: derivation of the effective state of an entry
# ---------------------------------------------------------------------

_RULING_FORM_RE = re.compile(r"\bRULED\b|\bRuled\b")


def _effective_disposition(entry, element, elements):
    """The disposition an element carries for derivation.

    A closing prose element whose statement is itself a ruling form
    (a statement that the item stands ruled in full by the named
    decider) is read by that form, not by the closure word its
    disposition was first read from.
    """
    disposition = element.disposition
    if disposition == "Closed" and element.kind == "closing prose":
        same_line = [e for e in elements if e.line == element.line]
        statement = element.statement or ""
        if len(same_line) == 1 and _RULING_FORM_RE.search(statement) and (
                "by Captain JP" in statement or "Ruled:" in statement):
            return "Ruled"
    return disposition


def _has_decided_status_line(elements):
    for element in elements:
        if element.kind in _STATUS_LINE_KINDS and element.disposition in (
                "Ruled", "Settled", "Closed", "Parked", "Presented"):
            return True
    return False


def _effective_elements(entry, elements):
    """The elements derivation reads, in element order.

    A segment that only states the remainder of an earlier part
    settlement carries no state of its own for derivation, and a
    terminal closure element at the end of an entry that carries
    a decided Status line is the record closing line of that
    decision, not a further state. An element stating what
    remains open stands in element order like any other: brief
    section 5.4 names no exception that sets it aside, and under
    the mapping table it determines the state (the Step 19 fix
    register records the set asides that stand, and the design
    questions split out for them, in the open).
    """
    kept = []
    for element in elements:
        statement = (element.statement or "").lstrip()
        if element.kind in _BLOCK_KINDS and statement.startswith("Remainder:"):
            continue
        if statement.startswith("Closing line for"):
            continue
        lowered = statement.lower()
        if "stays banked" in lowered and (
                "not decided by this ruling" in lowered
                or "not finished under this ruling" in lowered
                or "not completed by this ruling" in lowered):
            continue
        kept.append(element)
    while (kept and kept[-1].kind == "closing prose"
           and _effective_disposition(entry, kept[-1], elements) == "Closed"
           and _has_decided_status_line(elements)):
        kept.pop()
    return kept


def _decision_evidence(elements, exclude=None):
    for element in elements:
        if element is exclude:
            continue
        if element.disposition in _DECIDED_DISPOSITIONS:
            return True
        if element.decider is not None:
            return True
    return False


def _bq2_pair(elements):
    """The banked remainder sequence: a remainder Status line that
    states the remainder stays banked, followed by a closing block in
    ruling form or in settlement form."""
    for index, element in enumerate(elements):
        if element.kind not in _STATUS_LINE_KINDS:
            continue
        remainder = element.remainder_text or ""
        if "banked" not in remainder.lower():
            continue
        for later in elements[index + 1:]:
            if (later.kind in _BLOCK_KINDS
                    and later.disposition in _DECIDED_DISPOSITIONS):
                return (element, later)
    return None


def _decider_label(element):
    """The decider label of an element, governed by its tuple.

    Where the element tuple names a decider, that decider category
    governs: the label is the label form for that category, and a
    naming found in the element statement or verbatim text, negated
    or otherwise, never takes the place of the tuple decider. The
    statement text is read only inside the Manager grant form, to
    tell its recorded grant forms apart, and inside the fallback
    below. Where the tuple names no decider, the fallback stands as
    it stood: the label forms are read from the element text, and
    the verbatim decider text stands where no listed form covers it.
    """
    if element is None:
        return None
    text = " ".join(part for part in (
        element.decider_text or "",
        element.statement or "",
        element.verbatim or "") if part)
    lowered = text.lower()
    if element.decider is not None:
        if element.decider == "Captain JP":
            return "Ruled by Captain JP"
        if element.decider == "assessment by cross reference":
            return "decided by assessment under DQ-148"
        if element.decider == "a Manager grant form":
            if "pass 2 grant" in lowered:
                return "under the pass 2 grant"
            if "dq-141" in lowered and (
                    "fill in" in lowered or "fill-in" in lowered):
                return "fill in under DQ-141"
            if "dq-145" in lowered and "completion" in lowered:
                return "completion under DQ-145"
            if "dq-143" in lowered and (
                    "settled" in lowered or "settlement" in lowered):
                return "settled under DQ-143"
            return "Settled by the Manager under the grant"
        if element.decider_text:
            return element.decider_text
        return None
    if "pass 2 grant" in lowered:
        return "under the pass 2 grant"
    if "dq-141" in lowered and ("fill in" in lowered or "fill-in" in lowered):
        return "fill in under DQ-141"
    if "dq-145" in lowered and "completion" in lowered:
        return "completion under DQ-145"
    if "dq-143" in lowered and ("settled" in lowered or "settlement" in lowered):
        return "settled under DQ-143"
    if "dq-148" in lowered:
        return "decided by assessment under DQ-148"
    if "by captain jp" in lowered:
        return "Ruled by Captain JP"
    if element.decider_text:
        return element.decider_text
    return None


def _denoted_state(entry, element, elements):
    disposition = _effective_disposition(entry, element, elements)
    if disposition is None:
        return None
    if disposition == "Closed":
        return "Closed as decided"
    if disposition in ("Banked", "Relative"):
        return "Open"
    if (disposition == "Settled" and element.scope.startswith("Part")
            and element.remainder_text):
        return "Settled in part"
    return disposition


def _derive(entry):
    """Derive one entry. Returns a dict of derivation results."""
    result = {
        "state": None, "sub_label": None, "determining": None,
        "competing": [], "decider_label": None, "annotation": None,
        "remainder": None, "condition": None, "banked_question_id": None,
        "unparsed": bool(_get(entry, "unparsed")),
        "effective_elements": [],
    }
    if result["unparsed"]:
        return result
    elements = list(_get(entry, "status_elements") or [])
    if not elements:
        result["state"] = "Ambiguous"
        result["sub_label"] = "No element"
        return result
    pair = _bq2_pair(elements)
    if pair is not None:
        result["state"] = "Ambiguous"
        result["sub_label"] = "Conflict"
        result["competing"] = [pair[0], pair[1]]
        result["banked_question_id"] = "BQ-2"
        result["effective_elements"] = _effective_elements(entry, elements)
        return result
    effective = _effective_elements(entry, elements)
    result["effective_elements"] = effective
    if not effective:
        result["state"] = "Ambiguous"
        result["sub_label"] = "No element"
        return result
    determining = effective[-1]
    result["determining"] = determining
    disposition = _effective_disposition(entry, determining, elements)
    scope = determining.scope or ""
    condition = determining.condition

    def finish(state, sub_label=None, label_element=None):
        result["state"] = state
        result["sub_label"] = sub_label
        primary = (label_element if label_element is not None
                   else determining)
        # The label comes from the determining element alone.
        # Brief section 5.4 rules a row whose determining element
        # names no decider carries no label and counts in no
        # decider subtotal, with "decider not recorded" in its
        # place; no fallback to any other element stands.
        result["decider_label"] = _decider_label(primary)
        result["condition"] = condition
        result["remainder"] = determining.remainder_text
        if state in DECIDED_STATES and result["decider_label"] is None:
            result["annotation"] = "decider not recorded"
        return result

    if disposition is None:
        # An unclassifiable value is never assigned a disposition
        # (brief section 5.3), and pin 2 governs it: shape A, the
        # entry's only element with no decision evidence anywhere,
        # reports Open under the exception row, and shape B reports
        # Ambiguous, with pin 8 barring check 5 on it. A Condition
        # line attached to such an element does not convert it:
        # the Conditional row of the mapping table quantifies over
        # the dispositions the brief enumerates, and an element
        # with no disposition is not one of them. The condition
        # test below therefore stands after this branch, where it
        # governs every disposition bearing element.
        if len(elements) == 1 and not _decision_evidence(elements):
            return finish("Open")
        result["state"] = "Ambiguous"
        result["sub_label"] = "Single element"
        result["competing"] = [determining]
        result["condition"] = condition
        return result
    if condition:
        return finish("Conditional")
    if scope.startswith("Part"):
        if not determining.remainder_text:
            result["state"] = "Ambiguous"
            result["sub_label"] = "Single element"
            result["competing"] = [determining]
            result["condition"] = condition
            return result
        if disposition in ("Settled", "Closed"):
            return finish("Settled in part")
        if disposition == "Ruled":
            finished = finish("Settled in part")
            finished["decider_label"] = "Ruled by Captain JP"
            finished["annotation"] = None
            return finished
        result["state"] = "Ambiguous"
        result["sub_label"] = "Single element"
        result["competing"] = [determining]
        result["condition"] = condition
        return result
    if disposition in ("Banked", "Open", "Relative"):
        if _decision_evidence(elements, exclude=determining):
            earlier = [e for e in effective[:-1]
                       if _effective_disposition(entry, e, elements)
                       in _DECIDED_DISPOSITIONS]
            if (determining.kind in ("variant phrasing",
                                     "embedded status value",
                                     "closing prose") and earlier):
                determining = earlier[-1]
                result["determining"] = determining
                disposition = _effective_disposition(entry, determining,
                                                     elements)
                scope = determining.scope or ""
                condition = determining.condition
                if condition:
                    return finish("Conditional")
            else:
                result["state"] = "Ambiguous"
                result["sub_label"] = "Conflict"
                result["competing"] = [determining] + earlier
                result["condition"] = condition
                return result
        else:
            return finish("Open")
    if disposition == "Ruled":
        return finish("Ruled")
    if disposition == "Settled":
        return finish("Settled")
    if disposition == "Closed":
        statement = determining.statement or ""
        if "Completed by" in statement or "completed by" in statement.lower():
            return finish("Settled")
        return finish("Closed as decided")
    if disposition == "Parked":
        return finish("Parked")
    if disposition == "Presented":
        return finish("Presented")
    result["state"] = "Ambiguous"
    result["sub_label"] = "Conflict"
    result["competing"] = [determining] + [
        e for e in effective[:-1]
        if _effective_disposition(entry, e, elements) in _DECIDED_DISPOSITIONS]
    result["condition"] = condition
    return result


# ---------------------------------------------------------------------
# Findings
# ---------------------------------------------------------------------

def _finding(rule_id, severity, entry_identifier, span, evidence,
             statement, banked_question_id=None, basis=None):
    return Finding(
        rule_id=rule_id, severity=severity,
        entry_identifier=entry_identifier, line_span=span,
        evidence=evidence, statement=statement, basis=basis,
        banked_question_id=banked_question_id)


def _file_order_key(finding):
    span = finding.line_span
    start = span.start_line if span is not None else 0
    end = span.end_line if span is not None else 0
    evidence = finding.evidence
    evidence_text = evidence if isinstance(evidence, str) else str(evidence)
    return (finding.rule_id, start, end,
            evidence_text.encode("utf-8"),
            (finding.statement or "").encode("utf-8"))


# ---------------------------------------------------------------------
# Unit 3b: entry local checks (checks 2, 3, 4, 5, 7, 9 and 10)
# ---------------------------------------------------------------------

_OPTIONS_LABELS = ("Options",)
_QUESTION_LABELS = ("The question",)


def _has_options_field(entry):
    for label in _field_labels(entry):
        lowered = label.lower()
        if (label == "Options" or lowered.startswith("the options")
                or lowered.startswith("the three options")):
            return True
    for _line, text in _body_lines(entry):
        stripped = text.strip()
        lowered = stripped.lower()
        if (stripped.startswith("Options:")
                or lowered.startswith("the options")
                or lowered.startswith("the three options")):
            return True
    return False


def _check2(entry, display_id):
    findings = []
    for occurrence in _get(entry, "near_marker_occurrences") or []:
        line = _get(occurrence, "line")
        text = _get(occurrence, "text") or ""
        findings.append(_finding(
            2, "Warning", display_id, Span(line, line), text,
            "The line opens like a status line but carries no element: "
            + text,
            basis="a near marker line carries no element"))
    return findings


def _check3(entry, display_id, derived, elements):
    state = derived["state"]
    if state is None or state == "Ambiguous":
        return []
    effective = derived["effective_elements"]
    closed_lines = {e.line for e in effective
                    if _effective_disposition(entry, e, elements)
                    == "Closed"}
    decided_lines = {e.line for e in effective
                     if _effective_disposition(entry, e, elements)
                     in ("Ruled", "Settled")}
    denoted = {}
    for element in effective:
        if (_effective_disposition(entry, element, elements) == "Closed"
                and element.line in decided_lines
                and element.line in closed_lines):
            continue
        value = _denoted_state(entry, element, elements)
        if value is not None:
            denoted.setdefault(value, []).append(element)
    if len(denoted) < 2:
        return []
    head = None
    for element in elements:
        if element.kind == "head Status line":
            head = element
            break
    if head is not None and head.disposition == "Banked":
        return []
    determining = derived["determining"]
    evidence_parts = []
    for value, holders in denoted.items():
        for element in holders:
            quote = element.verbatim or element.statement or ""
            evidence_parts.append('"%s"' % quote)
    statement = (
        "The status elements of this entry disagree: the determining "
        "element at line %s states %s, and the entry also carries %s."
        % (determining.line if determining is not None else "?",
           _denoted_state(entry, determining, elements) if determining
           is not None else state,
           ", ".join(sorted(v for v in denoted if v != state))))
    return [_finding(
        3, "Warning", display_id,
        Span(determining.line, determining.line) if determining else None,
        " ".join(evidence_parts), statement,
        basis="status elements disagree within one entry")]


def _check4(entry, display_id, derived):
    if derived["state"] != "Conditional":
        return []
    determining = derived["determining"]
    span = (Span(determining.line, determining.line)
            if determining is not None else None)
    return [_finding(
        4, "Note", display_id, span,
        derived["condition"] or "",
        "Conditional closure is recorded for this entry: the decision "
        "stands subject to %s." % (derived["condition"] or ""),
        basis="conditional closure recorded")]


def _check5(entry, display_id, derived, elements):
    if derived["state"] not in DECIDED_STATES:
        return []
    labels = _field_labels(entry)
    body = _body_text(entry)
    cross_reference = "under DQ-148" in body
    decider = cross_reference
    if not decider:
        for element in elements:
            if element.decider_text or element.decider is not None:
                decider = True
                break
    if not decider:
        decider = bool(re.search(
            r"\b(Ruled|Settled|Decided) by\b", body)) or (
                "by Captain JP" in body)
    if not decider:
        heading = _get(entry, "heading") or ""
        if "by Captain JP" in heading:
            decider = True
    if not decider:
        for f in _get(entry, "fields") or []:
            if (_get(f, "label") == "Origin"
                    and "Captain JP" in (_get(f, "value") or "")):
                decider = True
                break
    ruling_text = cross_reference
    if not ruling_text:
        for label in labels:
            if label in ("Ruling text", "Ruling texts"):
                ruling_text = True
                break
    if not ruling_text:
        for element in derived["effective_elements"]:
            if (element.kind in ("decision block matter", "closing prose")
                    and _effective_disposition(entry, element, elements)
                    in _DECIDED_DISPOSITIONS):
                ruling_text = True
                break
    outcome = cross_reference
    if not outcome:
        for label in labels:
            if (label.startswith("Ruling outcome")
                    or label.startswith("Form outcome")
                    or label.startswith("Decision")
                    or label in ("Outcome", "Outcome of this decision")):
                outcome = True
                break
    if not outcome:
        for element in derived["effective_elements"]:
            statement = element.statement or ""
            if re.search(r"\b(is|stands)\s+(settled|ruled|closed)\b",
                         statement, re.IGNORECASE):
                outcome = True
                break
    if not outcome:
        for element in derived["effective_elements"]:
            statement = element.statement or ""
            if ("Ruled:" in statement or "Settled:" in statement
                    or "Ruling outcome" in statement):
                outcome = True
                break
    if not outcome:
        for element in derived["effective_elements"]:
            statement = (element.statement or "").lstrip()
            if (element.kind in ("decision block matter", "closing prose")
                    and _effective_disposition(entry, element, elements)
                    in _DECIDED_DISPOSITIONS
                    and statement.startswith(("Ruled", "Settled"))):
                outcome = True
                break
    if not outcome:
        for label in labels:
            if label in ("Ruled", "Settlement", "Fill-in"):
                outcome = True
                break
    landing = cross_reference
    if not landing:
        for label in labels:
            if (label.startswith("Where the ruling landed")
                    or label.startswith("Where the settlement landed")
                    or label.startswith("Where the settlement is to land")
                    or label in ("Landing", "Landing record", "Lands")):
                landing = True
                break
    if not landing:
        landing = bool(re.search(r"\blanded\b", body, re.IGNORECASE))
    if not landing:
        landing = bool(re.search(
            r"\blandings? recorded\b", body, re.IGNORECASE))
    if not landing:
        landing = any(element.kind == "later Status line"
                      for element in elements)
    if not landing:
        for label in labels:
            if label.startswith("Decision") or label == "Ruled":
                landing = True
                break
    findings = []
    determining = derived["determining"]
    span = (Span(determining.line, determining.line)
            if determining is not None else None)
    evidence = ""
    if determining is not None:
        evidence = determining.verbatim or determining.statement or ""
    if not decider:
        findings.append(_finding(
            5, "Error", display_id, span, evidence,
            "No decider is recorded for this decided entry in any "
            "form: the row is annotated decider not recorded.",
            basis="decision evidence presence: decider"))
    if not ruling_text:
        findings.append(_finding(
            5, "Error", display_id, span, evidence,
            "No ruling text is recorded for this decided entry in "
            "any form.",
            basis="decision evidence presence: ruling text"))
    if not outcome:
        findings.append(_finding(
            5, "Warning", display_id, span, evidence,
            "No outcome is recorded for this decided entry in any "
            "form.",
            basis="decision evidence presence: outcome"))
    if not landing:
        findings.append(_finding(
            5, "Warning", display_id, span, evidence,
            "No landing record is recorded for this decided entry in "
            "any form.",
            basis="decision evidence presence: landing record"))
    return findings


def _check9(entry, display_id, derived):
    if derived["state"] != "Open":
        return []
    labels = _field_labels(entry)
    missing = []
    if not any(label in _QUESTION_LABELS for label in labels):
        missing.append("its question")
    if not _has_options_field(entry):
        missing.append("its options")
    if "Cost of deciding late" not in labels:
        missing.append("its cost of deciding late")
    if "What it blocks" not in labels:
        missing.append("its blocks field")
    findings = []
    determining = derived["determining"]
    span = (Span(determining.line, determining.line)
            if determining is not None else None)
    for item in missing:
        findings.append(_finding(
            9, "Warning", display_id, span, item,
            "This open entry is missing %s." % item,
            basis="an open entry field is missing"))
    return findings


def _check10(entry, display_id, derived):
    if derived["state"] != "Parked":
        return []
    labels = _field_labels(entry)
    if any(label == "Reopening trigger" for label in labels):
        return []
    if "Reopening trigger:" in _body_text(entry):
        return []
    determining = derived["determining"]
    span = (Span(determining.line, determining.line)
            if determining is not None else None)
    return [_finding(
        10, "Error", display_id, span, "",
        "This parked entry names no reopening trigger under the "
        "Reopening trigger label.",
        basis="a parked entry with no named reopening trigger")]


def _unparsed_finding(entry, display_id):
    """The pin 12 Error finding for an entry carried as unparsed.

    Pin 12 rules the unparsed entry's finding grade as Error. The
    finding is raised under the pin's own rule number, on the entry
    itself, beside the carriage, the reconciliation row, and the
    exit 4 cause the entry already carries.
    """
    heading_line = _get(entry, "heading_line")
    span = (Span(heading_line, heading_line)
            if heading_line is not None else None)
    heading = _get(entry, "heading") or _get(entry, "heading_text") or ""
    return _finding(
        12, "Error", display_id, span, heading,
        "This entry stands unparsed: its heading stands with no "
        "body, so no state can be determined for it.",
        basis="an unparsed entry, carried under pin 12")


# ---------------------------------------------------------------------
# Unit 3c: whole file checks (checks 1 and 6) and the unmatched
# heading finding
# ---------------------------------------------------------------------

def _check1(entries):
    findings = []
    by_number = {}
    for entry in entries:
        number = _entry_number(entry)
        if number is not None:
            by_number.setdefault(number, []).append(entry)
    for number in sorted(by_number):
        holders = by_number[number]
        if len(holders) > 1:
            lines = sorted(_get(e, "heading_line") for e in holders)
            named = " and ".join(str(n) for n in lines)
            findings.append(_finding(
                1, "Error", FILE_ID, Span(lines[0], lines[-1]),
                "heading lines %s" % named,
                "The entry number DQ-%03d is used more than once: "
                "heading lines %s." % (number, named),
                basis="an entry number used more than once"))
    numbers = sorted(by_number)
    if numbers:
        present = set(numbers)
        runs = []
        current = []
        for candidate in range(numbers[0], numbers[-1] + 1):
            if candidate in present:
                if current:
                    runs.append(current)
                    current = []
            else:
                current.append(candidate)
        if current:
            runs.append(current)
        heading_line_by_number = {}
        for entry in entries:
            number = _entry_number(entry)
            if number is not None and number not in heading_line_by_number:
                heading_line_by_number[number] = _get(entry, "heading_line")
        for run in runs:
            before = [n for n in numbers if n < run[0]]
            if before:
                span_line = heading_line_by_number[max(before)]
                span = Span(span_line, span_line)
            else:
                span = Span(0, 0)
            named = ", ".join(str(n) for n in run)
            findings.append(_finding(
                1, "Warning", FILE_ID, span, named,
                "Entry numbers missing from the sequence: %s." % named,
                basis="a run of entry numbers missing from the sequence"))
    return findings


def _check6(model, entries):
    findings = []
    unassigned = list(_get(model, "unassigned_lines") or [])
    double_assigned = list(_get(model, "double_assigned_lines") or [])
    if unassigned or double_assigned:
        parts = []
        if unassigned:
            parts.append("Lines assigned to no unit: %s."
                         % ", ".join(str(n) for n in unassigned))
        if double_assigned:
            parts.append("Lines assigned to two units: %s."
                         % ", ".join(str(n) for n in double_assigned))
        involved = unassigned + double_assigned
        findings.append(_finding(
            6, "Error", FILE_ID, Span(min(involved), max(involved)),
            {"unassigned_lines": unassigned,
             "double_assigned_lines": double_assigned},
            " ".join(parts),
            basis="lines assigned to no unit or to two units"))
    for entry in entries:
        display_id = _display_id(entry)
        reattached = [s for s in _get(entry, "spans") or []
                      if _get(s, "non_contiguous")
                      or _get(s, "boundary_basis") == "label reattachment"]
        notes = [n for n in _get(entry, "parse_notes") or []
                 if _get(n, "kind") == "label reattachment"]
        count = max(len(reattached), len(notes))
        for index in range(count):
            span = None
            if index < len(reattached):
                span = reattached[index]
            elif notes:
                span = _get(notes[0], "line_span")
            findings.append(_finding(
                6, "Warning", display_id, span,
                "label reattachment",
                "A paragraph stands reattached to this entry by its "
                "label; the entry span is non contiguous.",
                basis="a span fixed by label reattachment"))
    return findings


def _unmatched_heading_findings(model):
    findings = []
    for segment in _get(model, "orphan_segments") or []:
        if not _get(segment, "unmatched_heading"):
            continue
        heading_text = _get(segment, "heading_text") or ""
        findings.append(_finding(
            5, "Warning", FILE_ID, _get(segment, "span"),
            heading_text,
            "The heading %s matches no recognised heading form; no "
            "entry is raised for it." % heading_text,
            basis="a heading matching no recognised heading form"))
    return findings


# ---------------------------------------------------------------------
# Unit 3d: cross entry check (check 8)
# ---------------------------------------------------------------------

_CITATION_PATTERNS = (
    re.compile(r"\bunder DQ-(\d+)(?![\d:])"),
    re.compile(r"\bunder the DQ-(\d+)(?![\d:])"),
    re.compile(r"\bat DQ-(\d+)(?![\d:])"),
    re.compile(r"\bsee DQ-(\d+)(?![\d:])"),
    re.compile(r"\bper DQ-(\d+)(?![\d:])"),
    re.compile(r"\bcross reference to DQ-(\d+)(?![\d:])"),
)

_CLAIM_PATTERNS = (
    re.compile(r"\bDQ-(\d+)\s+is\s+"
               r"(Settled|Ruled|Open|Banked|Closed|Parked|Presented)\b"),
    re.compile(r"\bDQ-(\d+)\b[^.;]{0,110}?\b"
               r"(stays|remains|stands|left)\s+"
               r"(banked|open|settled|ruled|closed)\b"),
)

_INTRODUCTION_PATTERN = re.compile(
    r"\b(\d+|one|two|three|four|five|six|seven|eight|nine|ten|"
    r"eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|"
    r"eighteen|nineteen|twenty)\s+(entries|questions|items|decisions)\b")


def _check8(model, entries, derived_by_id):
    findings = []
    numbers = set()
    for entry in entries:
        number = _entry_number(entry)
        if number is not None:
            numbers.add(number)
    cited = set()

    def scan_citations(lines, source_key, entry_identifier):
        for line_number, text in lines:
            for pattern in _CITATION_PATTERNS:
                for match in pattern.finditer(text):
                    number = int(match.group(1))
                    if number in numbers:
                        continue
                    key = (source_key, number)
                    if key in cited:
                        continue
                    cited.add(key)
                    findings.append(_finding(
                        8, "Warning", entry_identifier,
                        Span(line_number, line_number), text,
                        "DQ-%03d is cited in a citation frame, but no "
                        "entry heading in the file carries that number."
                        % number,
                        basis="a cited number with no heading"))

    for entry in entries:
        scan_citations(_body_lines(entry), _display_id(entry),
                       _display_id(entry))
    segments = list(_get(model, "orphan_segments") or [])
    for index, segment in enumerate(segments):
        lines = [(n, t) for n, t in (_get(segment, "lines") or [])]
        if not lines:
            span = _get(segment, "span")
            if span is not None:
                lines = [(span.start_line, _get(segment, "heading_text")
                          or "")]
        scan_citations(lines, ("segment", index),
                       _get(segment, "heading_text") or "note section")

    def claim_finding(claiming_id, target_id, quoted, span):
        derived = derived_by_id.get(target_id)
        if derived is None:
            return None
        state = derived["state"]
        if state == "Ambiguous":
            state_text = "Ambiguous (%s)" % (derived["sub_label"] or "")
        else:
            state_text = str(state)
        return _finding(
            8, "Note", claiming_id, span, quoted,
            "%s records a claim about the state of %s: \"%s\" The "
            "claim is reported as a claim. The derived state of %s "
            "in this run is %s."
            % (claiming_id, target_id, quoted, target_id, state_text),
            basis="a cross entry state claim, reported as a claim")

    seen_claims = set()
    token_pattern = re.compile(r"\bDQ-(\d+)\b")
    predicate_patterns = (
        re.compile(r"DQ-\d+\s+is\s+(Settled|Ruled|Open|Banked|Closed|"
                   r"Parked|Presented)\b"),
        re.compile(r"[^.;]{0,110}?\b(stays|remains|stands|left)\s+"
                   r"(banked|open|settled|ruled|closed)\b"),
    )
    for entry in entries:
        claiming_id = _display_id(entry)
        for line_number, text in _body_lines(entry):
            if text.startswith("Status:"):
                continue
            for token in token_pattern.finditer(text):
                target_id = "DQ-%03d" % int(token.group(1))
                if target_id == claiming_id:
                    continue
                rest = text[token.start():]
                quoted = None
                for predicate in predicate_patterns:
                    match = predicate.match(rest)
                    if match:
                        quoted = match.group(0)
                        break
                if quoted is None:
                    continue
                key = (claiming_id, target_id, quoted)
                if key in seen_claims:
                    continue
                seen_claims.add(key)
                finding = claim_finding(
                    claiming_id, target_id, quoted,
                    Span(line_number, line_number))
                if finding is not None:
                    findings.append(finding)
    model_lines = list(_get(model, "lines") or [])
    units = list(_get(model, "units") or [])
    introductions = [u for u in units
                     if _get(u, "kind") == "section introduction"]
    ordered_entries = sorted(
        entries, key=lambda e: _get(e, "heading_line") or 0)
    for unit in introductions:
        span = _get(unit, "span")
        if span is None:
            continue
        claimed = None
        for line_number in range(span.start_line, span.end_line + 1):
            if 1 <= line_number <= len(model_lines):
                text = model_lines[line_number - 1]
            else:
                continue
            match = _INTRODUCTION_PATTERN.search(text)
            if match:
                token = match.group(1)
                claimed = (int(token) if token.isdigit()
                           else _NUMBER_WORDS.get(token.lower()))
                break
        if claimed is None:
            continue
        boundary = None
        candidates = []
        for other in introductions:
            if other is unit:
                continue
            other_span = _get(other, "span")
            if other_span is not None:
                candidates.append(other_span.start_line)
        for segment in segments:
            segment_span = _get(segment, "span")
            if segment_span is not None:
                candidates.append(segment_span.start_line)
        for entry in entries:
            if (_get(entry, "heading_level") or 3) <= 2:
                candidates.append(_get(entry, "heading_line") or 0)
        for candidate in candidates:
            if candidate > span.end_line:
                if boundary is None or candidate < boundary:
                    boundary = candidate
        present = 0
        first_id = None
        for entry in ordered_entries:
            line = _get(entry, "heading_line") or 0
            if line > span.end_line and (boundary is None
                                         or line < boundary):
                present += 1
                if first_id is None:
                    first_id = _display_id(entry)
        if present != claimed:
            findings.append(_finding(
                8, "Warning", first_id or FILE_ID, span,
                _get(unit, "heading_text") or "",
                "The section introduction states %d entries; %d "
                "recognised entry headings stand in the section."
                % (claimed, present),
                basis="a section introduction count against its section"))
    return findings


# ---------------------------------------------------------------------
# Unit 3e: census
# ---------------------------------------------------------------------

def _head_element(entry):
    for element in _get(entry, "status_elements") or []:
        if element.kind == "head Status line":
            return element
    return None


def _census(entries, derived_list):
    pairs = list(zip(entries, derived_list))
    decided = [(e, d) for e, d in pairs if d["state"] in DECIDED_STATES]

    banked_head = []
    for entry, derived in pairs:
        head = _head_element(entry)
        if head is None or head.disposition != "Banked":
            continue
        if derived["state"] in DECIDED_STATES or (
                derived["state"] == "Ambiguous"):
            banked_head.append(_display_id(entry))

    non_header = []
    for entry, derived in decided:
        for element in _get(entry, "status_elements") or []:
            if element.occurrence_kind in ("embedded", "variant"):
                non_header.append(_display_id(entry))
                break
            if (element.occurrence_kind == "line start"
                    and element.kind != "head Status line"):
                non_header.append(_display_id(entry))
                break

    missing_options = [_display_id(e) for e, d in decided
                       if not _has_options_field(e)]
    missing_date = [_display_id(e) for e, d in decided
                    if not _get(e, "date_text")]

    non_numeric = []
    ruled_sections = {}
    for entry, derived in pairs:
        section = _get(entry, "section") or ""
        if section.lower() == "ruled record":
            ruled_sections.setdefault(section, []).append((entry, derived))
    for section, holders in ruled_sections.items():
        numbered = [(n, e, d) for e, d in holders
                    for n in [_entry_number(e)] if n is not None]
        for index, (number, entry, derived) in enumerate(numbered):
            prev_number = numbered[index - 1][0] if index > 0 else None
            next_number = (numbered[index + 1][0]
                           if index + 1 < len(numbered) else None)
            out_of_order = (
                (prev_number is not None and number < prev_number)
                or (next_number is not None and number > next_number))
            if out_of_order and derived["state"] in DECIDED_STATES:
                non_numeric.append(_display_id(entry))

    missing_owner_tail = []
    if pairs:
        tail_section = _get(pairs[-1][0], "section")
        for entry, derived in pairs:
            if _get(entry, "section") != tail_section:
                continue
            if derived["state"] not in DECIDED_STATES:
                continue
            labels = _field_labels(entry)
            if any(label in ("Owner of record", "Owner")
                   for label in labels):
                continue
            if any(label in ("The question",
                             "Question as put on the Questions space",
                             "Cost of deciding late")
                   for label in labels):
                continue
            missing_owner_tail.append(_display_id(entry))

    missing_question_or_cost = []
    for entry, derived in decided:
        section = _get(entry, "section") or ""
        if section.lower() == "ruled record":
            continue
        labels = _field_labels(entry)
        in_open_form = any(
            label == "The question"
            or label.startswith("Question as put")
            or label == "Cost of deciding late"
            for label in labels)
        if not in_open_form:
            continue
        if ("The question" not in labels
                or "Cost of deciding late" not in labels):
            missing_question_or_cost.append(_display_id(entry))

    open_form_in_ruled = []
    for entry, derived in decided:
        section = _get(entry, "section") or ""
        if section.lower() != "ruled record":
            continue
        labels = _field_labels(entry)
        if any(label in ("The question", "Cost of deciding late",
                         "What it blocks") for label in labels):
            open_form_in_ruled.append(_display_id(entry))

    unclassified = []
    for entry, derived in pairs:
        for element in _get(entry, "status_elements") or []:
            if element.disposition is None:
                unclassified.append(_display_id(entry))
                break

    classes = [
        ("Banked head over a decided body", banked_head),
        ("Non header status value on a decided entry", non_header),
        ("Missing options block on a decided entry", missing_options),
        ("Missing ruling date on a decided entry", missing_date),
        ("Non numeric filing of a decided entry in the Ruled Record",
         non_numeric),
        ("Missing Owner line in a tail form entry", missing_owner_tail),
        ("Decided entry missing its question label or Cost field",
         missing_question_or_cost),
        ("Open form fields carried by a decided entry in the Ruled "
         "Record", open_form_in_ruled),
        ("Unclassified status values", unclassified),
    ]
    return [CensusEntry(class_name=name, count=len(members),
                        member_entry_ids=list(members))
            for name, members in classes]


# ---------------------------------------------------------------------
# Unit 3f: reconciliation, crosswalk, subtotals, waiting and blocking
# ---------------------------------------------------------------------

_CLEARING_FORMS = {
    1: "Record each entry heading once, in a recognised heading "
       "form, with no entry number used twice and no number missing "
       "from the sequence.",
    2: "Rewrite the line so it does not open with a status marker, "
       "or record the status it carries as a Status line of the "
       "entry.",
    3: "Bring the status elements of the entry into agreement, so "
       "one state stands for the entry.",
    4: "The finding stands as the record of the conditional "
       "closure; it clears when the condition is discharged and "
       "the entry is reported without it.",
    5: "Record the missing decider, ruling text, outcome or landing "
       "in one of its recorded forms.",
    6: "Assign every line to exactly one unit; a reattached "
       "paragraph clears when it stands inside its own entry span.",
    7: "Record the status value in the vocabulary, or restate the "
       "value in a recorded phrasing.",
    8: "Give the cited number an entry heading, or take the "
       "citation out of its frame; a claim clears when the claim "
       "is withdrawn or the entry it names is restated.",
    9: "Record the missing question, options, cost of deciding "
       "late or blocks field on the open entry.",
    10: "Name a reopening trigger under the Reopening trigger "
        "label.",
    12: "Give the entry a body in a recognised form under its "
        "heading, or take the heading out of the file.",
}

# The pin 5 unmatched heading finding is filed under rule id 5,
# whose number amendment 3 of the plan rules as its first order
# key, but check 5's clearing form cannot clear it: recording a
# decider, ruling text, outcome or landing does nothing for a
# heading that matches no recognised form. The finding therefore
# carries its own clearing form, printed under its pin name, and
# check 5's form is printed only where a check 5 finding fired.
_PIN5_CLEARING_FORM = (
    "Restate the heading in a recognised heading form, or take "
    "the heading and the lines under it out of the file.")


def _appendix_rows(entries, vocabulary):
    rows = {}
    order = []
    for entry in entries:
        display_id = _display_id(entry)
        for element in _get(entry, "status_elements") or []:
            if element.occurrence_kind is None:
                continue
            key = (element.verbatim, element.occurrence_kind)
            if key not in rows:
                rows[key] = {
                    "count": 0, "members": [],
                    "first": (element.line, element.position_in_line),
                }
                order.append(key)
            rows[key]["count"] += 1
            if display_id not in rows[key]["members"]:
                rows[key]["members"].append(display_id)
    order.sort(key=lambda key: rows[key]["first"])
    result = []
    for phrasing, kind in order:
        data = rows[(phrasing, kind)]
        result.append(VerbatimAppendixRow(
            phrasing=phrasing, occurrence_count=data["count"],
            kind=kind, member_entry_ids=data["members"],
            unclassified=phrasing not in vocabulary.mapping))
    return result


def _crosswalk(entries, derived_list, vocabulary):
    counts = {}
    for entry, derived in zip(entries, derived_list):
        head = _head_element(entry)
        if head is None or head.verbatim is None:
            continue
        phrasing = head.verbatim
        state = derived["state"]
        if state is None:
            continue
        bucket = counts.setdefault(phrasing, {})
        bucket[state] = bucket.get(state, 0) + 1
    result = {}
    for phrasing, bucket in counts.items():
        family = vocabulary.mapping.get(phrasing)
        differs = False
        for state in bucket:
            if state == "Ambiguous":
                differs = True
            elif family is None:
                differs = True
            elif family == "Closed" and state == "Closed as decided":
                continue
            elif family == "Banked" and state == "Open":
                continue
            elif family != state:
                differs = True
        if differs or phrasing == "Banked":
            row = dict(bucket)
            row["total"] = sum(bucket.values())
            result[phrasing] = row
    return result


# ---------------------------------------------------------------------
# Unit 3g: the Exit decision
# ---------------------------------------------------------------------

def _exit_decision(findings, ambiguous_count, unparsed_count,
                   conditional_count, self_check):
    if self_check is not None and not self_check.sums_agree:
        return ExitDecision(
            code=4,
            reason_classes=[
                "tool inconsistency: the reconciliation sums do not "
                "agree"])
    reasons = []
    if ambiguous_count or conditional_count:
        reasons.append(
            "ambiguous or conditional entries govern the exit")
    if unparsed_count:
        reasons.append("an unparsed entry stands in the file")
    if reasons:
        return ExitDecision(code=4, reason_classes=reasons)
    if any(f.severity in ("Error", "Warning") for f in findings):
        return ExitDecision(
            code=1,
            reason_classes=["findings at error or warning grade"])
    return ExitDecision(code=0, reason_classes=[])


# ---------------------------------------------------------------------
# The validate boundary
# ---------------------------------------------------------------------

def validate_model(model, vocabulary, output_form_edition=None):
    # The output form edition is a shell held constant of the tool
    # version. It arrives here as a received value beside the
    # Vocabulary, and it is copied verbatim into the Validate output
    # below. Validate holds no copy of the value itself.
    if vocabulary is None:
        vocabulary = Vocabulary.shipped()
    entries = list(_get(model, "entries") or [])
    header_facts = _get(model, "header_facts") or _get(
        model, "file_header_facts")

    derived_list = []
    for entry in entries:
        derived = _derive(entry)
        derived_list.append(derived)
    derived_by_id = {}
    for entry, derived in zip(entries, derived_list):
        derived_by_id[_display_id(entry)] = derived

    entry_results = []
    for entry, derived in zip(entries, derived_list):
        elements = list(_get(entry, "status_elements") or [])
        open_fields = {}
        for f in _get(entry, "fields") or []:
            open_fields[_get(f, "label")] = _get(f, "value") or ""
        head = _head_element(entry)
        state = derived["state"]
        if derived["unparsed"]:
            state = None
        result = EntryResult(
            identifier=_get(entry, "identifier"),
            heading=_get(entry, "heading")
            or _get(entry, "heading_text") or "",
            title=_get(entry, "title") or "",
            date=_get(entry, "date_text"),
            effective_state=state,
            sub_label=derived["sub_label"],
            determining_element=derived["determining"],
            competing_elements=list(derived["competing"]),
            element_summary=[
                "line %s: %s: %s" % (e.line, e.kind, e.disposition)
                for e in elements],
            decider_label=derived["decider_label"],
            banked_question_id=derived["banked_question_id"],
            status_phrasings=[e.verbatim for e in elements
                              if e.occurrence_kind is not None],
            head_phrasing=head.verbatim if head is not None else None,
            remainder_text=derived["remainder"],
            condition_text=derived["condition"],
            ordering_reason=open_fields.get("Ordering reason"),
            open_fields=open_fields,
            unparsed=derived["unparsed"])
        result.decider_annotation = derived["annotation"]
        entry_results.append(result)

    file_findings = []
    file_findings.extend(_check1(entries))
    file_findings.extend(_unmatched_heading_findings(model))
    check6_findings = _check6(model, entries)
    file_findings.extend(
        f for f in check6_findings if f.entry_identifier == FILE_ID)
    file_findings.sort(key=_file_order_key)

    entry_findings = []
    entry_findings.extend(
        f for f in check6_findings if f.entry_identifier != FILE_ID)
    for entry, derived in zip(entries, derived_list):
        display_id = _display_id(entry)
        elements = list(_get(entry, "status_elements") or [])
        if derived["unparsed"]:
            entry_findings.append(_unparsed_finding(entry, display_id))
        entry_findings.extend(_check2(entry, display_id))
        entry_findings.extend(_check3(entry, display_id, derived,
                                      elements))
        entry_findings.extend(_check4(entry, display_id, derived))
        entry_findings.extend(_check5(entry, display_id, derived,
                                      elements))
        entry_findings.extend(_check9(entry, display_id, derived))
        entry_findings.extend(_check10(entry, display_id, derived))
    entry_findings.extend(_check8(model, entries, derived_by_id))

    entry_index = {}
    for index, entry in enumerate(entries):
        entry_index[_display_id(entry)] = index

    def entry_order_key(finding):
        index = entry_index.get(finding.entry_identifier, len(entries))
        span = finding.line_span
        line = span.start_line if span is not None else 0
        return (index, finding.rule_id, line)

    entry_findings.sort(key=entry_order_key)
    findings = file_findings + entry_findings

    census = _census(entries, derived_list)

    canonical_counts = {name: 0 for name in CANONICAL_STATES}
    ambiguous_count = 0
    unparsed_count = 0
    for derived in derived_list:
        if derived["unparsed"]:
            unparsed_count += 1
        elif derived["state"] == "Ambiguous":
            ambiguous_count += 1
        elif derived["state"] in canonical_counts:
            canonical_counts[derived["state"]] += 1
    entry_total = len(entries)

    appendix_rows = _appendix_rows(entries, vocabulary)
    occurrence_total = sum(row.occurrence_count for row in appendix_rows)
    occurrences_by_kind = {}
    for row in appendix_rows:
        occurrences_by_kind[row.kind] = (
            occurrences_by_kind.get(row.kind, 0) + row.occurrence_count)
    distinct_phrasings = len({row.phrasing for row in appendix_rows})

    findings_per_severity = {}
    findings_per_rule = {}
    for finding in findings:
        findings_per_severity[finding.severity] = (
            findings_per_severity.get(finding.severity, 0) + 1)
        findings_per_rule[finding.rule_id] = (
            findings_per_rule.get(finding.rule_id, 0) + 1)

    failed_components = []
    unit_counts = _get(header_facts, "unit_counts") or {}
    parse_entry_units = unit_counts.get("entry")
    if parse_entry_units is not None and parse_entry_units != entry_total:
        failed_components.append(
            "entry total: the entry list holds %d entries and the "
            "parse owned count records %d entry units"
            % (entry_total, parse_entry_units))
    canonical_sum = sum(canonical_counts.values())
    if canonical_sum + ambiguous_count + unparsed_count != entry_total:
        failed_components.append(
            "entry total: the canonical rows sum to %d, the Ambiguous "
            "count is %d and the unparsed count is %d, against an "
            "entry total of %d"
            % (canonical_sum, ambiguous_count, unparsed_count,
               entry_total))
    recounted_occurrences = 0
    for entry in entries:
        for element in _get(entry, "status_elements") or []:
            if element.occurrence_kind is not None:
                recounted_occurrences += 1
    if recounted_occurrences != occurrence_total:
        failed_components.append(
            "status occurrence total: the verbatim appendix rows sum "
            "to %d and the elements counted directly give %d"
            % (occurrence_total, recounted_occurrences))
    if sum(findings_per_severity.values()) != len(findings):
        failed_components.append(
            "findings per severity: the severity view sums to %d "
            "against a findings list of %d"
            % (sum(findings_per_severity.values()), len(findings)))
    if sum(findings_per_rule.values()) != len(findings):
        failed_components.append(
            "findings per rule: the rule view sums to %d against a "
            "findings list of %d"
            % (sum(findings_per_rule.values()), len(findings)))
    self_check = SelfCheckResult(
        sums_agree=not failed_components,
        failed_components=failed_components)

    reconciliation = ReconciliationBlock(
        entry_total=HeadedEntryCount(entry_total),
        dq_entry_count=sum(1 for e in entries
                           if _get(e, "identifier")),
        unnumbered_entry_count=sum(1 for e in entries
                                   if not _get(e, "identifier")),
        headed_span_count=sum(len(_get(e, "spans") or [])
                              for e in entries),
        orphan_note_segment_count=sum(
            1 for s in _get(model, "orphan_segments") or []
            if not _get(s, "unmatched_heading")),
        h4_sub_heading_count=_get(model, "h4_sub_heading_count") or 0,
        status_occurrences_by_kind=occurrences_by_kind,
        status_occurrence_total=occurrence_total,
        canonical_counts=canonical_counts,
        ambiguous_count=ambiguous_count,
        unparsed_count=unparsed_count,
        findings_per_severity=findings_per_severity,
        findings_per_rule=findings_per_rule,
        distinct_phrasing_count=DistinctPhrasingCount(
            distinct_phrasings),
        self_check=self_check,
        paired_total_declarations=[
            "Headed entries: %d = %d canonical %s + %d Ambiguous "
            "+ %d unparsed" % (entry_total, canonical_sum,
                               "row" if canonical_sum == 1 else "rows",
                               ambiguous_count, unparsed_count),
            "Status occurrences: %d = %d counted in the verbatim "
            "appendix" % (occurrence_total, occurrence_total),
        ])

    decider_subtotals = {}
    for result, derived in zip(entry_results, derived_list):
        if derived["state"] in DECIDED_STATES and result.decider_label:
            decider_subtotals[result.decider_label] = (
                decider_subtotals.get(result.decider_label, 0) + 1)

    open_results = [(e, r) for e, r in zip(entries, entry_results)
                    if r.effective_state == "Open"]
    waiting = len(open_results) + sum(
        1 for r in entry_results
        if r.effective_state == "Settled in part")
    blocking = 0
    blocking_list = []
    for entry, result in open_results:
        blocks = _field_value(entry, "What it blocks")
        if blocks:
            blocking += 1
            blocking_list.append({
                "entry_id": _display_id(entry),
                "identifier": _display_id(entry),
                "title": _get(entry, "title") or "",
                "what_it_blocks": blocks,
                "blocks": blocks,
            })
    blocks_with = 0
    blocks_without = 0
    for entry, result in open_results:
        # The blocks field stands recorded where its label stands on
        # the entry, the same test check 9 applies. The coverage
        # counts state what the blocking figure rests on.
        if "What it blocks" in _field_labels(entry):
            blocks_with += 1
        else:
            blocks_without += 1
    effort_with = 0
    effort_without = 0
    for entry, result in open_results:
        signal = any("effort" in label.lower()
                     for label in _field_labels(entry))
        if not signal:
            signal = any(text.startswith("Effort")
                         for _n, text in _body_lines(entry))
        if signal:
            effort_with += 1
        else:
            effort_without += 1
    limbo_data = {
        "conditional_count": canonical_counts.get("Conditional", 0),
        "ambiguous_count": ambiguous_count,
        "unparsed_count": unparsed_count,
        "conditional_entry_ids": [
            _display_id(e) for e, d in zip(entries, derived_list)
            if d["state"] == "Conditional"],
        "ambiguous_entry_ids": [
            _display_id(e) for e, d in zip(entries, derived_list)
            if d["state"] == "Ambiguous" and not d["unparsed"]],
        "unparsed_entry_ids": [
            _display_id(e) for e, d in zip(entries, derived_list)
            if d["unparsed"]],
    }
    limbo_data["conditional"] = limbo_data["conditional_entry_ids"]
    limbo_data["ambiguous"] = limbo_data["ambiguous_entry_ids"]
    limbo_data["unparsed"] = limbo_data["unparsed_entry_ids"]

    conditional_count = canonical_counts.get("Conditional", 0)
    exit_decision = _exit_decision(
        findings, ambiguous_count, unparsed_count, conditional_count,
        self_check)

    fired_rules = sorted({f.rule_id for f in findings})
    clearing_forms = {rule: _CLEARING_FORMS[rule] for rule in fired_rules
                      if rule in _CLEARING_FORMS}
    if 5 in clearing_forms:
        check5_fired = any(
            f.rule_id == 5 and (f.basis or "").startswith(
                "decision evidence presence")
            for f in findings)
        pin5_fired = any(
            f.rule_id == 5 and f.basis ==
            "a heading matching no recognised heading form"
            for f in findings)
        if not check5_fired:
            del clearing_forms[5]
        if pin5_fired:
            clearing_forms["pin 5"] = _PIN5_CLEARING_FORM

    file_facts = FileFactsData(
        input_name=_get(header_facts, "input_name")
        or _get(model, "input_name") or "",
        byte_count=_get(header_facts, "byte_count") or 0,
        line_count=_get(header_facts, "line_count") or 0,
        entry_count=HeadedEntryCount(entry_total),
        digest=_get(header_facts, "digest") or "")

    if header_facts is not None and not isinstance(header_facts, dict):
        if getattr(header_facts, "vocabulary_version", None) is None:
            try:
                header_facts.vocabulary_version = vocabulary.version
            except Exception:
                pass

    limits = _get(header_facts, "limits")
    if limits is None:
        from .types import Limits
        limits = Limits()

    segment_claim_reports = []
    for segment in _get(model, "orphan_segments") or []:
        for claim in _get(segment, "claims") or []:
            segment_claim_reports.append({
                "segment_heading": _get(segment, "heading_text") or "",
                "statement": _get(claim, "statement") or "",
                "named_entries": list(
                    _get(claim, "named_entries") or []),
                "reported_as": "claim",
            })

    output = ValidateOutput(
        entries=entry_results,
        findings=findings,
        census=census,
        reconciliation=reconciliation,
        exit_decision=exit_decision,
        file_facts=file_facts,
        limits=limits,
        vocabulary_version=vocabulary.version,
        output_form_edition=output_form_edition,
        verbatim_appendix_rows=appendix_rows,
        per_rule_clearing_forms=clearing_forms,
        crosswalk_counts=_crosswalk(entries, derived_list, vocabulary),
        decider_subtotals=decider_subtotals,
        waiting=waiting,
        blocking=blocking,
        blocking_list=blocking_list,
        blocks_coverage={
            "with_blocks_field": blocks_with,
            "without_blocks_field": blocks_without,
            "with_field": blocks_with,
            "without_field": blocks_without,
        },
        effort_coverage={
            "with_signal": effort_with,
            "without_signal": effort_without,
            "with_effort_signal": effort_with,
            "without_effort_signal": effort_without,
        },
        limbo_data=limbo_data,
        fastest_item="not derivable from the file")
    output.segment_claim_reports = segment_claim_reports
    return output
