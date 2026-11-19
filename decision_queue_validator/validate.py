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
import unicodedata

from .types import (
    CensusEntry,
    CountingUnitsKey,
    DistinctPhrasingCount,
    EntryResult,
    FileFactsData,
    Finding,
    HeadedEntryCount,
    ReconciliationBlock,
    ResidueItem,
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

DECIDED_OUTCOMES = (
    "Ruled",
    "Settled",
    "Settled in part",
    "Closed as decided",
    "Conditional",
)

_DECIDED_DISPOSITIONS = ("Ruled", "Settled", "Closed")
_STATUS_LINE_KINDS = ("line start Status line", "later Status line")
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
    heading = _get(entry, "heading") or _get(entry, "heading_text") or ""
    if identifier is not None and identifier != "":
        # The identifier may stand in the DQNumber type the
        # capture layer now carries; its string form is the DQ
        # label as written, which is the form every validate
        # comparison and display uses.
        if str(identifier) == heading and (
                heading == "R-7" or heading.startswith("R-7 ")):
            # The named unnumbered form, PIN-06: under the D-06
            # cure the entry identifier stands as the literal
            # heading text of the R-7 heading, and the display
            # identifier of that form is R-7.
            return "R-7"
        return str(identifier)
    if heading == "R-7" or heading.startswith("R-7 "):
        # The named unnumbered form, PIN-06: the literal R-7
        # heading. Its identifier is R-7; parse records no
        # identifier for the unnumbered form.
        return "R-7"
    return heading


def _entry_number(entry):
    identifier = _get(entry, "identifier")
    if isinstance(identifier, bool):
        return None
    if isinstance(identifier, int):
        return int(identifier)
    match = re.fullmatch(r"DQ-([0-9]+)", identifier or "")
    if match:
        return int(match.group(1))
    return None


def _is_dq_numbered(entry):
    """Whether the entry stands as a DQ numbered entry.

    The distinction stands in the D-06 form: a DQ numbered
    entry carries its identifier as an int DQNumber, the
    numeric value the heading digits denote (a seam double
    carrying the string DQ label gives the same number through
    _entry_number), while a named unnumbered entry carries its
    identifier as the literal heading text, which gives no
    number. Identifier presence alone distinguishes neither
    form, because the named unnumbered entry carries an
    identifier too.
    """
    return _entry_number(entry) is not None


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


def _first_family_value(entry, labels):
    """The governing value of a field family, under the one
    selection rule stated once for repeated and alias paired
    fields (Step 17 round 4 charge CH-59, seat 6 Finding 2):
    the first occurrence in file order governs, for a
    repeated label and for an alias pair alike. The recorded
    fields stand in file order, so the first recorded field
    whose label stands in the family is the governing one,
    whichever of the family's labels it carries. Returns
    None where no field of the family stands recorded."""
    for f in _get(entry, "fields") or []:
        if _get(f, "label") in labels:
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
    if (disposition == "Closed"
            and element.kind == "decision block matter"
            and element.decider == "a Manager grant form"
            and "setting the values" in (element.statement or "")):
        # The completion block form: a named actor setting the
        # outstanding values of the entry completes it, and the
        # brief extraction rule, form four, states a Settled
        # disposition for that prose. The DQ-054 derivation row
        # reads its completion block in exactly this form.
        return "Settled"
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


def _is_bare_closing_sentence(element):
    """A bare closing sentence element: a tail paragraph element
    whose whole verbatim text states closed and nothing more, in
    the PIN-11 form."""
    if element.kind != "tail paragraph element":
        return False
    text = (element.verbatim or element.statement or "").strip().lower()
    return text in ("closed.", "closed", "status: closed.",
                    "it is closed.", "it is closed")


def _heading_decided_disposition(elements):
    for element in elements:
        if (element.kind == "heading borne evidence"
                and element.disposition in ("Ruled", "Settled")):
            return element.disposition
    return None


def _is_record_closing_line(element):
    statement = (element.statement or "").lstrip()
    return (statement.startswith("- This queue:")
            or statement.startswith("This queue:")) and (
                "this entry is its record" in statement)


def _effective_elements(entry, elements):
    """The elements derivation reads, in element order.

    A segment that only states the remainder of an earlier part
    settlement carries no state of its own for derivation, and a
    terminal closure element at the end of an entry that carries
    a decided Status line is the record closing line of that
    decision, not a further state. The set asides below stand on
    the derivation record rows for the pin entries they name,
    each read in validate only, over the elements parse stands:

    A record closing line, the bullet under a landing label
    stating that the item is closed and this entry is its
    record, is a landing record wherever it stands in the
    entry, not a state statement (the Settled and Ruled rows
    of DQ-007 to DQ-034 rest on their Status lines). An element
    stating what remains open after a settlement or ruling
    states the residue of that decision, not a further state
    of the entry, and a closing line for a held bundle inside
    a settled entry completes the bundle and changes no whole
    entry state (the DQ-023 row). A bare closing sentence in
    the PIN-11 concordance form, standing in an entry whose
    heading element denotes Ruled or Settled, confirms that
    heading disposition and denotes no separate Closed state;
    the same concordance covers a Closed element extracted
    from the same paragraph and the same line as a Ruled or
    Settled element over identical verbatim text, and a Closed
    closing prose element whose statement ends with the
    embedded Status: closed sentence that a bare closing tail
    element on the same line carries (the DQ-153 to DQ-171
    rows, DQ-161 among them). Each set aside applies only
    where another element remains to read.
    """
    kept = []
    for element in elements:
        statement = (element.statement or "").lstrip()
        if element.kind in _BLOCK_KINDS and statement.startswith("Remainder:"):
            continue
        kept.append(element)
    heading_decided = _heading_decided_disposition(elements)
    filtered = []
    for index, element in enumerate(kept):
        statement = (element.statement or "").lstrip()
        drop = False
        if _is_record_closing_line(element):
            drop = True
        elif statement.startswith("What remains open"):
            drop = True
        elif (element.kind == "closing prose"
                and statement.startswith("Closing line for")):
            drop = True
        elif heading_decided is not None and _is_bare_closing_sentence(
                element):
            drop = True
        elif (element.disposition == "Closed"
                and any(other is not element
                        and other.line == element.line
                        and (other.verbatim or "") == (element.verbatim or "")
                        and other.disposition in ("Ruled", "Settled")
                        for other in kept)):
            drop = True
        elif (heading_decided is not None
                and element.kind == "closing prose"
                and element.disposition == "Closed"
                and statement.rstrip().lower().endswith("status: closed.")
                and any(_is_bare_closing_sentence(other)
                        and other.line == element.line
                        for other in kept)):
            drop = True
        elif (heading_decided is not None
                and element.kind == "closing prose"
                and element.disposition == "Closed"
                and re.search(r"(?:^|[.!?]\s+)(?:it is\s+)?closed\.\s*$",
                              statement.strip(), re.IGNORECASE)):
            # The PIN-11 concordance form at paragraph scale:
            # a closing prose paragraph whose final sentence is
            # the bare closing sentence, stating closed and
            # nothing more (the pronoun form "It is closed."
            # stands in the same form, Step 17 round 2 charge
            # CH-8, A2-10-F1), standing in an entry whose heading
            # element denotes Ruled or Settled, confirms that
            # heading disposition and denotes no separate
            # Closed state, so the paragraph element is set
            # aside exactly as the bare closing sentence form
            # above is (Step 17 charge A10-F1).
            drop = True
        if (element.kind == "closing prose"
                and element.disposition == "Closed"
                and statement.startswith("- DQ-")
                and ("neither is closed" in statement.lower()
                     or "not closed" in statement.lower())):
            # A landing bullet whose subject is another entry
            # and which states that subject is not closed by
            # this entry states no closure of this entry: the
            # brief extraction rule gives a statement about
            # another entry no disposition for this entry (the
            # DQ-144 landing bullet in its WV-1 form).
            drop = True
        if drop and len(kept) > 1:
            continue
        filtered.append(element)
    kept = filtered if filtered else kept
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


_NEGATED_CONDITIONS = (
    "no condition", "no conditions", "no stated condition",
    "none", "not subject to any condition",
)


def _effective_condition(element):
    """The condition a tuple carries for the PIN-03 mapping.

    A condition text that in words states there is no condition
    (for example the closing words "subject to no condition" of an
    express ruling paragraph) states the absence of a condition,
    not a condition. It maps as no condition stated. Any other
    condition text stands verbatim.
    """
    condition = element.condition
    if condition is None:
        # A conditional clause standing inside a Status line
        # value itself, in the form the value carries it (a
        # disposition word followed by an if clause, as in
        # "Ruled if the ferry runs"), states the condition of
        # that element although no condition tuple stands
        # recorded for it: the clause is extracted from the
        # value, under the PIN-03 extraction rule, so the
        # element takes its Conditional treatment instead of
        # the clause being dropped (Step 17 charge F-11-04).
        if element.kind in _STATUS_LINE_KINDS:
            value = (element.verbatim or element.statement
                     or "").strip()
            match = re.match(
                r"(?:RULED|Ruled|SETTLED|Settled|CLOSED|Closed|"
                r"BANKED|Banked|Parked|Presented)"
                r"(?:, closed)?\s+if\s+(.+?)\s*$", value)
            if match:
                text = match.group(1).strip().rstrip(".")
                if text:
                    return text
        return None
    cleaned = condition.strip().strip(".").lower()
    if cleaned in _NEGATED_CONDITIONS or cleaned.startswith(
            "no condition"):
        return None
    return condition


_REMAINDER_PATTERNS = (
    re.compile(r"[Tt]he remainder, (.+?), stays\b"),
    re.compile(r"[Tt]he remainder, (.+?) stays\b"),
    re.compile(r"[Tt]he remainder (.+?) stays\b"),
    re.compile(r"[Ww]hat stays banked: (.+?)(?:, and this item\b"
               r"|\.\s*$|\.$|$)"),
    re.compile(r"[Rr]emainder, (.+?), stays\b"),
    re.compile(r"([Tt]he remainder) stays\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?(?:still )?"
               r"stands open\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?(?:still )?"
               r"(?:stands open|stays\b)"),
    re.compile(r"([Tt]he rest) (?:also )?(?:still )?"
               r"(?:stands open|stays banked|stands banked)\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"(?:remains|stays) open\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?is still open\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"(?:remains|stays) open\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?is still open\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"(?:remains|stays) open\b"),
    re.compile(r"([Tt]he remainder) (?:also )?is still open\b"),
    re.compile(r"([Tt]he rest) (?:also )?(?:remains|stays) open\b"),
    re.compile(r"([Tt]he rest) (?:also )?is still open\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?is open\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?is open\b"),
    re.compile(r"([Tt]he remainder) (?:also )?is open\b"),
    re.compile(r"([Tt]he rest) (?:also )?is open\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"(?:remains|stays) pending\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"(?:remains|stays) pending\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"(?:remains|stays) pending\b"),
    re.compile(r"([Tt]he rest) (?:also )?"
               r"(?:remains|stays) pending\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"is still pending\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"is still pending\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"is still pending\b"),
    re.compile(r"([Tt]he rest) (?:also )?is still pending\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"remains unresolved\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"remains unresolved\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"remains unresolved\b"),
    re.compile(r"([Tt]he rest) (?:also )?"
               r"remains unresolved\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"is unresolved\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?is unresolved\b"),
    re.compile(r"([Tt]he remainder) (?:also )?is unresolved\b"),
    re.compile(r"([Tt]he rest) (?:also )?is unresolved\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"continues open\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?continues open\b"),
    re.compile(r"([Tt]he remainder) (?:also )?continues open\b"),
    re.compile(r"([Tt]he rest) (?:also )?continues open\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?lies open\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?lies open\b"),
    re.compile(r"([Tt]he remainder) (?:also )?lies open\b"),
    re.compile(r"([Tt]he rest) (?:also )?lies open\b"),
    # Round 5 limbs (charge CH-87, A5-10-F2), appended after
    # every standing pattern, so a form a standing pattern
    # already reads keeps that reading first: the bare
    # remainder with stands open, the very verb its named
    # form and the bare rest form are read in; the
    # outstanding forms; the still form of unresolved, as
    # the still form of pending stands read since CH-67;
    # the to be decided, left open, continues to stand
    # open, and awaits decision forms; and the undecided
    # forms, which the own paragraph reading did not reach
    # at all while the statement reading read them on the
    # parse side. Each verb stands for both subjects, the
    # rest and the remainder, in the named form and in the
    # bare form, as the CH-67 limbs stand.
    re.compile(r"([Tt]he remainder) (?:also )?(?:still )?"
               r"stands open\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"remains outstanding\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"remains outstanding\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"remains outstanding\b"),
    re.compile(r"([Tt]he rest) (?:also )?"
               r"remains outstanding\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"is outstanding\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?is outstanding\b"),
    re.compile(r"([Tt]he remainder) (?:also )?is outstanding\b"),
    re.compile(r"([Tt]he rest) (?:also )?is outstanding\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"is still unresolved\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"is still unresolved\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"is still unresolved\b"),
    re.compile(r"([Tt]he rest) (?:also )?is still unresolved\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"is yet to be decided\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"is yet to be decided\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"is yet to be decided\b"),
    re.compile(r"([Tt]he rest) (?:also )?is yet to be decided\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"remains to be decided\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"remains to be decided\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"remains to be decided\b"),
    re.compile(r"([Tt]he rest) (?:also )?"
               r"remains to be decided\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"is left open\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?is left open\b"),
    re.compile(r"([Tt]he remainder) (?:also )?is left open\b"),
    re.compile(r"([Tt]he rest) (?:also )?is left open\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"continues to stand open\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"continues to stand open\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"continues to stand open\b"),
    re.compile(r"([Tt]he rest) (?:also )?"
               r"continues to stand open\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"awaits decision\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?awaits decision\b"),
    re.compile(r"([Tt]he remainder) (?:also )?awaits decision\b"),
    re.compile(r"([Tt]he rest) (?:also )?awaits decision\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"stands undecided\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"stands undecided\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"stands undecided\b"),
    re.compile(r"([Tt]he rest) (?:also )?stands undecided\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"stays undecided\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?stays undecided\b"),
    re.compile(r"([Tt]he remainder) (?:also )?stays undecided\b"),
    re.compile(r"([Tt]he rest) (?:also )?stays undecided\b"),
    # Round 6 limbs (charge CH-106, A6-10-F2), appended after
    # every standing pattern, so a form a standing pattern
    # already reads keeps that reading first: the plain is
    # pending and is undecided forms; stands pending; stays
    # outstanding and is still outstanding; remains
    # undecided; is not yet decided; awaits a decision and
    # is awaiting decision; has yet to be decided; is left
    # undecided; stands unresolved; is held open; and
    # continues to remain open. Each verb stands for both
    # subjects, the rest and the remainder, in the named
    # form and in the bare form, as the CH-87 limbs stand.
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?is pending\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?is pending\b"),
    re.compile(r"([Tt]he remainder) (?:also )?is pending\b"),
    re.compile(r"([Tt]he rest) (?:also )?is pending\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"is undecided\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?is undecided\b"),
    re.compile(r"([Tt]he remainder) (?:also )?is undecided\b"),
    re.compile(r"([Tt]he rest) (?:also )?is undecided\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"stands pending\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"stands pending\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"stands pending\b"),
    re.compile(r"([Tt]he rest) (?:also )?stands pending\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"stays outstanding\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"stays outstanding\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"stays outstanding\b"),
    re.compile(r"([Tt]he rest) (?:also )?"
               r"stays outstanding\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"is still outstanding\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"is still outstanding\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"is still outstanding\b"),
    re.compile(r"([Tt]he rest) (?:also )?"
               r"is still outstanding\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"remains undecided\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"remains undecided\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"remains undecided\b"),
    re.compile(r"([Tt]he rest) (?:also )?"
               r"remains undecided\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"is not yet decided\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"is not yet decided\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"is not yet decided\b"),
    re.compile(r"([Tt]he rest) (?:also )?is not yet decided\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"awaits a decision\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"awaits a decision\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"awaits a decision\b"),
    re.compile(r"([Tt]he rest) (?:also )?awaits a decision\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"is awaiting decision\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"is awaiting decision\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"is awaiting decision\b"),
    re.compile(r"([Tt]he rest) (?:also )?"
               r"is awaiting decision\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"has yet to be decided\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"has yet to be decided\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"has yet to be decided\b"),
    re.compile(r"([Tt]he rest) (?:also )?"
               r"has yet to be decided\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"is left undecided\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"is left undecided\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"is left undecided\b"),
    re.compile(r"([Tt]he rest) (?:also )?is left undecided\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"stands unresolved\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"stands unresolved\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"stands unresolved\b"),
    re.compile(r"([Tt]he rest) (?:also )?stands unresolved\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"is held open\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?is held open\b"),
    re.compile(r"([Tt]he remainder) (?:also )?is held open\b"),
    re.compile(r"([Tt]he rest) (?:also )?is held open\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"continues to remain open\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"continues to remain open\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"continues to remain open\b"),
    re.compile(r"([Tt]he rest) (?:also )?"
               r"continues to remain open\b"),
    # Round 7 limbs (charge CH-147, A7-10-F2), appended after
    # every standing pattern, so a form a standing pattern
    # already reads keeps that reading first: the stays
    # unresolved, stands outstanding, is still undecided,
    # is awaiting a decision, awaits a ruling, has not been
    # decided, is not decided, is left pending, is left
    # unresolved, remains on hold, is deferred, continues
    # unresolved, still remains open, lies unresolved, and
    # is in abeyance forms. Each verb stands for both
    # subjects, the rest and the remainder, in the named
    # form and in the bare form, as the CH-106 limbs stand.
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"stays unresolved\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"stays unresolved\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"stays unresolved\b"),
    re.compile(r"([Tt]he rest) (?:also )?stays unresolved\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"stands outstanding\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"stands outstanding\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"stands outstanding\b"),
    re.compile(r"([Tt]he rest) (?:also )?stands outstanding\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"is still undecided\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"is still undecided\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"is still undecided\b"),
    re.compile(r"([Tt]he rest) (?:also )?is still undecided\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"is awaiting a decision\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"is awaiting a decision\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"is awaiting a decision\b"),
    re.compile(r"([Tt]he rest) (?:also )?is awaiting a decision\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"awaits a ruling\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"awaits a ruling\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"awaits a ruling\b"),
    re.compile(r"([Tt]he rest) (?:also )?awaits a ruling\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"has not been decided\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"has not been decided\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"has not been decided\b"),
    re.compile(r"([Tt]he rest) (?:also )?has not been decided\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"is not decided\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"is not decided\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"is not decided\b"),
    re.compile(r"([Tt]he rest) (?:also )?is not decided\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"is left pending\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"is left pending\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"is left pending\b"),
    re.compile(r"([Tt]he rest) (?:also )?is left pending\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"is left unresolved\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"is left unresolved\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"is left unresolved\b"),
    re.compile(r"([Tt]he rest) (?:also )?is left unresolved\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"remains on hold\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"remains on hold\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"remains on hold\b"),
    re.compile(r"([Tt]he rest) (?:also )?remains on hold\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"is deferred\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"is deferred\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"is deferred\b"),
    re.compile(r"([Tt]he rest) (?:also )?is deferred\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"continues unresolved\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"continues unresolved\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"continues unresolved\b"),
    re.compile(r"([Tt]he rest) (?:also )?continues unresolved\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"still remains open\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"still remains open\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"still remains open\b"),
    re.compile(r"([Tt]he rest) (?:also )?still remains open\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"lies unresolved\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"lies unresolved\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"lies unresolved\b"),
    re.compile(r"([Tt]he rest) (?:also )?lies unresolved\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"is in abeyance\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"is in abeyance\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"is in abeyance\b"),
    re.compile(r"([Tt]he rest) (?:also )?is in abeyance\b"),
    # Round 8 limbs (charge CH-163, A8-10-F2), appended after
    # every standing pattern, so a form a standing pattern
    # already reads keeps that reading first: the is waiting
    # for a decision, waits for a decision, stands deferred,
    # is on hold, lies pending, stands in abeyance, remains
    # in abeyance, has not been ruled, is not ruled, awaits
    # the decision, is adjourned, is postponed, is tabled,
    # is held in abeyance, lies undecided, and continues
    # outstanding forms. Each verb stands for both subjects,
    # the rest and the remainder, in the named form and in
    # the bare form, as the CH-147 limbs stand. The
    # asymmetries the attack paper names stand cured inside
    # these forms: the definite article in awaits the
    # decision beside the CH-106 awaits a decision and the
    # CH-147 awaits a ruling forms, the word held in is held
    # in abeyance beside the CH-147 is in abeyance form, and
    # the ruled verb forms has not been ruled and is not
    # ruled beside the CH-147 decided verb forms.
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"is waiting for a decision\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"is waiting for a decision\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"is waiting for a decision\b"),
    re.compile(r"([Tt]he rest) (?:also )?is waiting for a decision\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"waits for a decision\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"waits for a decision\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"waits for a decision\b"),
    re.compile(r"([Tt]he rest) (?:also )?waits for a decision\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"stands deferred\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"stands deferred\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"stands deferred\b"),
    re.compile(r"([Tt]he rest) (?:also )?stands deferred\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"is on hold\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"is on hold\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"is on hold\b"),
    re.compile(r"([Tt]he rest) (?:also )?is on hold\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"lies pending\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"lies pending\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"lies pending\b"),
    re.compile(r"([Tt]he rest) (?:also )?lies pending\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"stands in abeyance\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"stands in abeyance\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"stands in abeyance\b"),
    re.compile(r"([Tt]he rest) (?:also )?stands in abeyance\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"remains in abeyance\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"remains in abeyance\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"remains in abeyance\b"),
    re.compile(r"([Tt]he rest) (?:also )?remains in abeyance\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"has not been ruled\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"has not been ruled\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"has not been ruled\b"),
    re.compile(r"([Tt]he rest) (?:also )?has not been ruled\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"is not ruled\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"is not ruled\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"is not ruled\b"),
    re.compile(r"([Tt]he rest) (?:also )?is not ruled\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"awaits the decision\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"awaits the decision\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"awaits the decision\b"),
    re.compile(r"([Tt]he rest) (?:also )?awaits the decision\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"is adjourned\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"is adjourned\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"is adjourned\b"),
    re.compile(r"([Tt]he rest) (?:also )?is adjourned\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"is postponed\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"is postponed\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"is postponed\b"),
    re.compile(r"([Tt]he rest) (?:also )?is postponed\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"is tabled\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"is tabled\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"is tabled\b"),
    re.compile(r"([Tt]he rest) (?:also )?is tabled\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"is held in abeyance\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"is held in abeyance\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"is held in abeyance\b"),
    re.compile(r"([Tt]he rest) (?:also )?is held in abeyance\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"lies undecided\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"lies undecided\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"lies undecided\b"),
    re.compile(r"([Tt]he rest) (?:also )?lies undecided\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"continues outstanding\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"continues outstanding\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"continues outstanding\b"),
    re.compile(r"([Tt]he rest) (?:also )?continues outstanding\b"),
    # Round 9 limbs (charge CH-198, A9-10-F2), appended after
    # the round 8 limbs, so a form a standing pattern
    # already reads keeps that reading first: the is
    # awaiting a ruling, waits for a ruling, has not been
    # settled, is not settled, is in limbo, stands
    # adjourned, is held over, is carried over, awaits a
    # verdict, is suspended, and stands suspended forms.
    # Each verb stands for both subjects, the rest and the
    # remainder, in the named form and in the bare form,
    # as the CH-163 limbs stand. The asymmetries the
    # attack paper names stand cured inside these forms:
    # the noun ruling in is awaiting a ruling and waits
    # for a ruling beside the CH-163 waits for a decision
    # form and the CH-106 awaits a ruling form, and the
    # settled verb forms has not been settled and is not
    # settled beside the CH-147 decided verb forms and
    # the CH-163 ruled verb forms. Seat 12 observation
    # O-9-12-5's M25 form, the rest is in limbo, is the
    # limbo member of this limb, counted once inside
    # the finding.
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"is awaiting a ruling\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"is awaiting a ruling\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"is awaiting a ruling\b"),
    re.compile(r"([Tt]he rest) (?:also )?is awaiting a ruling\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"waits for a ruling\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"waits for a ruling\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"waits for a ruling\b"),
    re.compile(r"([Tt]he rest) (?:also )?waits for a ruling\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"has not been settled\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"has not been settled\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"has not been settled\b"),
    re.compile(r"([Tt]he rest) (?:also )?has not been settled\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"is not settled\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"is not settled\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"is not settled\b"),
    re.compile(r"([Tt]he rest) (?:also )?is not settled\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"is in limbo\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"is in limbo\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"is in limbo\b"),
    re.compile(r"([Tt]he rest) (?:also )?is in limbo\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"stands adjourned\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"stands adjourned\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"stands adjourned\b"),
    re.compile(r"([Tt]he rest) (?:also )?stands adjourned\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"is held over\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"is held over\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"is held over\b"),
    re.compile(r"([Tt]he rest) (?:also )?is held over\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"is carried over\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"is carried over\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"is carried over\b"),
    re.compile(r"([Tt]he rest) (?:also )?is carried over\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"awaits a verdict\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"awaits a verdict\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"awaits a verdict\b"),
    re.compile(r"([Tt]he rest) (?:also )?awaits a verdict\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"is suspended\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"is suspended\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"is suspended\b"),
    re.compile(r"([Tt]he rest) (?:also )?is suspended\b"),
    re.compile(r"[Tt]he remainder, (.+?), (?:also )?"
               r"stands suspended\b"),
    re.compile(r"[Tt]he rest, (.+?), (?:also )?"
               r"stands suspended\b"),
    re.compile(r"([Tt]he remainder) (?:also )?"
               r"stands suspended\b"),
    re.compile(r"([Tt]he rest) (?:also )?stands suspended\b"),
)


def _extract_remainder(element):
    """The remainder a part element names, verbatim where it can
    be read. The tuple remainder text governs where parse recorded
    one. Where it recorded none, the remainder named in the
    element statement itself is read from that statement, in the
    forms the corpus uses to name one."""
    if element.remainder_text:
        return element.remainder_text
    statement = element.statement or element.verbatim or ""
    for pattern in _REMAINDER_PATTERNS:
        match = pattern.search(statement)
        if match:
            text = match.group(1).strip().rstrip(".")
            if text:
                return text
    if (element.scope or "").startswith("Part"):
        match = re.search(r"[Ss]tays banked: (.+?)(?:, and this item"
                          r"|\.\s*$|\.$|$)", statement)
        if match:
            text = match.group(1).strip().rstrip(".")
            if text:
                return text
    return None


_PART_SCOPE_PATTERNS = (
    re.compile(r"\bthe (?:first|second|third|fourth|fifth|sixth|"
               r"seventh|eighth|ninth|tenth) part is "
               r"(?:ruled|settled|closed)\b", re.IGNORECASE),
    re.compile(r"\ba part of (?:this entry|the entry) is "
               r"(?:ruled|settled|closed)\b", re.IGNORECASE),
    re.compile(r"\bpart of this entry\b[^.]{0,60}?"
               r"\b(?:ruled|settled)\b", re.IGNORECASE),
)


def _scope_of(element, entry=None):
    """The scope a disposition statement carries, read in
    validate where the recorded scope does not already state
    it: scope is Part where the statement in words limits the
    act to a named part of the entry, under the PIN-01
    extraction rule (Step 17 charge A10-F5, widened at round 2
    charge CH-9, A2-10-F4). The part limit stands in the
    statement itself, so it states part scope whether the
    remainder is named in the same statement, in the words
    the rest, in a later paragraph of the entry, or not named
    at all: a part act with a named remainder derives Settled
    in part, and a part act naming no remainder takes the
    PIN-03 Ambiguous row in derivation, as the Status line
    form of the same shape does. A statement limiting nothing
    states no part scope here."""
    recorded = element.scope or ""
    if recorded.startswith("Part"):
        return recorded
    statement = element.statement or element.verbatim or ""
    for pattern in _PART_SCOPE_PATTERNS:
        if pattern.search(statement):
            return "Part"
    if re.search(r"\bin part\b", statement, re.IGNORECASE) and (
            _extract_remainder(element)
            or (entry is not None
                and _entry_body_remainder(entry))):
        return "Part"
    return recorded


def _entry_body_remainder(entry):
    """The remainder named anywhere in the entry body, in the
    remainder forms _extract_remainder reads, or None. A part
    disposition whose remainder stands in its own paragraph
    after the disposition statement names its remainder there,
    and the body is the only place that naming stands
    (Step 17 round 2 charge CH-9, A2-10-F4)."""
    body = _body_text(entry)
    if not body:
        return None
    for pattern in _REMAINDER_PATTERNS:
        match = pattern.search(body)
        if match:
            text = match.group(1).strip().rstrip(".")
            if text:
                return text
    match = re.search(r"[Ss]tays banked: (.+?)(?:, and this item"
                      r"|\.\s*$|\.$|$)", body, re.MULTILINE)
    if match:
        text = match.group(1).strip().rstrip(".")
        if text:
            return text
    return None


def _part_remainder(entry, element):
    """The remainder a part element names, for derivation:
    the remainder the element itself names where it names
    one, and otherwise, where the element carries part
    scope, the remainder the entry body names. An element
    carrying no part scope takes no remainder from the body,
    so a remainder named for another act never attaches to
    a whole act."""
    found = _extract_remainder(element)
    if found:
        return found
    if entry is None:
        return None
    if not _scope_of(element).startswith("Part"):
        return None
    return _entry_body_remainder(entry)


def _entry_decision_evidence(entry, elements):
    """Decision evidence anywhere in the entry, in any form: a
    decided element, a named decider on an element, or the recorded
    decider and ruling label forms standing in the entry body."""
    if _decision_evidence(elements):
        return True
    body = _body_text(entry)
    if re.search(r"\b(Ruled|Settled|Decided) by\b", body):
        return True
    if "by Captain JP" in body:
        return True
    for label in _field_labels(entry):
        if label in ("Ruling text", "Ruling texts", "Ruled by",
                     "Settlement", "Ruled", "Fill-in"):
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
            if "dq-145" in lowered and ("completion" in lowered or "completed" in lowered):
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
    if "dq-145" in lowered and ("completion" in lowered or "completed" in lowered):
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


def _listing_decider_label(entry, elements):
    """The decider label for the entry group listing, read from
    the whole entry in the forms the rule 5 decider check itself
    accepts (the _check5 decider limb), or None where no decider
    stands in any of those forms.

    The check reads a decider from the assessment cross
    reference in the body, from any element carrying a decider,
    from the body forms "(Ruled|Settled|Decided) by" and
    "by Captain JP", from the heading form "by Captain JP", and
    from an Origin field naming Captain JP. The listing label
    follows the same forms in the same order, so the listing
    states the decider the check finds and the not recorded
    annotation stands only where the check would find none.
    This label is the listing's alone: the decider label that
    feeds the decider subtotals stays the determining element's
    label, as _derive states it.
    """
    body = _body_text(entry)
    if "under DQ-148" in body:
        return "decided by assessment under DQ-148"
    for element in elements:
        if element.decider is not None or element.decider_text:
            label = _decider_label(element)
            if label:
                return label
    # The separator after "by" in each body step of this
    # listing is the whitespace the decider check itself
    # takes: the check's body pattern ends at a word
    # boundary after "by", so a tab or a line break stands
    # in that position as a space does, and a vertical tab
    # and a form feed stand there as word boundaries too,
    # and the listing steps below each take one whitespace
    # character of the same kinds there (findings A6-8-4
    # and A7-8-2). A doubled space stands exactly as it
    # stood: no step here takes it, and the named phrase
    # step below reads past it in the form Fix Seat Q
    # recorded.
    # The check's word boundary after "by" takes more
    # than whitespace, and the steps below take the
    # further boundary forms the boundary itself names
    # (finding A8-8-2): a comma, a semicolon or a full
    # stop followed by one whitespace character; a
    # hyphen, a slash or the en dash character standing
    # directly against the name; a non breaking space as
    # the separator itself; and a doubled colon followed
    # by one whitespace character. The punctuation
    # branches and the doubled colon branch take the
    # same whitespace slot as the colon branch, one
    # whitespace character of the standing class or a
    # non breaking space in that slot (finding A9-8-2).
    # The Manager and named
    # phrase steps carry those forms in their separator,
    # inside patterns already anchored on the verb form
    # the check takes. The Captain step above keeps the
    # whitespace class alone, because the check's own
    # "by Captain JP" test takes that form with no verb
    # standing; the Captain form of the further boundary
    # characters stands in the verb anchored step below,
    # so a bare "by" carrying one of them, with no verb
    # form the check accepts, stays denied here as the
    # check denies it.
    if re.search(r"by[ \t\r\n\v\f]Captain JP", body):
        return "Ruled by Captain JP"
    if re.search(
            r"\b(Ruled|Settled|Decided) by"
            r"(?:[.,;][ \t\r\n\v\f\xa0]|[-/\u2013]|\xa0"
            r"|::[ \t\r\n\v\f\xa0])Captain JP",
            body):
        return "Ruled by Captain JP"
    # The Manager form stands only where the Manager phrase
    # itself stands in the body form the decider check
    # accepts, "(Ruled|Settled|Decided) by", with the colon
    # variant the check's own pattern also takes: a bare
    # "by the Manager" mention in prose, in a sentence that
    # states a decision in a form the check does not take or
    # in a sentence stating no decision at all, is a form the
    # check does not accept, and the listing claims no
    # decider from it (finding A5-8-3).
    if re.search(
            r"\b(Ruled|Settled|Decided) by"
            r"(?::?[ \t\r\n\v\f\xa0]|::[ \t\r\n\v\f\xa0]"
            r"|[.,;][ \t\r\n\v\f\xa0]|[-/\u2013])"
            r"(the|The) Manager\b",
            body):
        shim = type("ListingShim", (), {})()
        shim.decider = "a Manager grant form"
        shim.decider_text = "The Manager"
        shim.statement = body
        shim.verbatim = ""
        return _decider_label(shim)
    match = re.search(
        r"\b(Ruled|Settled|Decided) by"
        r"(?::?[ \t\r\n\v\f\xa0]|::[ \t\r\n\v\f\xa0]"
        r"|[.,;][ \t\r\n\v\f\xa0]|[-/\u2013])([^.,;]+)",
        body)
    if match:
        named = match.group(2).strip()
        if named:
            return named
    heading = _get(entry, "heading") or ""
    if "by Captain JP" in heading:
        return "Ruled by Captain JP"
    for field in _get(entry, "fields") or []:
        if (_get(field, "label") == "Origin"
                and "Captain JP" in (_get(field, "value") or "")):
            return "Ruled by Captain JP"
    return None


def _concordant_state(entry, element, elements):
    """The state a bare closing sentence denotes under the
    PIN-11 concordance rule, or None where the rule does not
    apply: the sentence confirms the heading disposition where
    a heading element denoting Ruled or Settled stands."""
    if not _is_bare_closing_sentence(element):
        return None
    heading = _heading_decided_disposition(elements)
    if heading is None:
        return None
    if heading == "Closed":
        return "Closed as decided"
    return heading


def _denoted_state(entry, element, elements):
    concordant = _concordant_state(entry, element, elements)
    if concordant is not None:
        return concordant
    disposition = _effective_disposition(entry, element, elements)
    if disposition is None:
        return None
    if _effective_condition(element):
        return "Conditional"
    if disposition == "Closed":
        return "Closed as decided"
    if disposition in ("Banked", "Relative"):
        return "Open"
    if (disposition in ("Ruled", "Settled")
            and _scope_of(element, entry).startswith("Part")
            and _part_remainder(entry, element)):
        return "Settled in part"
    if disposition in ("Ruled", "Settled", "Closed", "Banked", "Open",
                       "Presented", "Parked") and (
            _scope_of(element, entry).startswith("Part")):
        return "Ambiguous"
    return disposition


def _underlying_state(entry, element, elements):
    """The state an element denotes with any stated condition
    disregarded, computed by validate only (plan Item 3, section
    3.5, field 9)."""
    concordant = _concordant_state(entry, element, elements)
    if concordant is not None:
        return concordant
    disposition = _effective_disposition(entry, element, elements)
    if disposition is None:
        return None
    if disposition == "Closed":
        return "Closed as decided"
    if disposition in ("Banked", "Relative"):
        return "Open"
    if (disposition in ("Ruled", "Settled")
            and _scope_of(element, entry).startswith("Part")
            and _part_remainder(entry, element)):
        return "Settled in part"
    return disposition


_PIN12_PROSE_PATTERNS = (
    re.compile(r"\bundecided\b", re.IGNORECASE),
    re.compile(r"carried as a new open item", re.IGNORECASE),
    re.compile(r"carries the undefined shape", re.IGNORECASE),
)


def _pin12_shape(entry, elements, effective):
    """PIN-12: an entry closed in its head form whose ruling
    outcome carries an expressly undecided part in prose only
    derives Closed as decided, never Settled in part. The head
    form is a line start Status line stating closed; the
    undecided part stands in the entry body prose, in the
    forms the two pin instances carry (a flagged consequence
    expressly undecided, as at DQ-003; a shape carried as a
    new open item, as at DQ-013); and no element carries a
    part scope, because no part form element stands."""
    head_closed = any(
        element.kind == "line start Status line"
        and "closed" in (element.statement or "").lower()
        for element in elements)
    record_closed = any(_is_record_closing_line(element)
                        for element in elements)
    if not head_closed and not record_closed:
        # The closed form stands either in the head form, as on
        # the pin, or in the record closing line, as on the
        # whole file variants whose head form is Banked (the
        # WV-1 and WV-2 census forms of DQ-003 and DQ-013).
        return False
    if any((element.scope or "").startswith("Part")
           for element in effective):
        return False
    body = _body_text(entry)
    return any(pattern.search(body) for pattern in _PIN12_PROSE_PATTERNS)


def _derive(entry):
    """Derive one entry. Returns a dict of derivation results."""
    result = {
        "state": None, "sub_label": None, "determining": None,
        "competing": [], "decider_label": None, "annotation": None,
        "listing_decider_label": None,
        "remainder": None, "condition": None, "banked_question_id": None,
        "unparsed": bool(_get(entry, "unparsed")),
        "effective_elements": [],
        "underlying_state": None, "denoted_states": [],
        "shape_a": False, "presence_results": None,
        "remainder_texts": [],
    }
    elements = list(_get(entry, "status_elements") or [])
    if result["unparsed"] and any(
            _get(element, "kind") == "heading borne evidence"
            for element in elements):
        # The PIN-05 exception, in the scope PIN-05 states it:
        # where a determining element stands extracted from the
        # entry heading, the unparsed assignment does not run
        # and derivation governs. A body element does not lift
        # the marker from a cut off entry, because the body is
        # not whole and no body element can be certified as
        # determining over the part that was cut off, as the
        # WV-8 truncation form at brief section 5.8 states.
        result["unparsed"] = False
    if result["unparsed"]:
        return result
    if not elements:
        result["state"] = "Ambiguous"
        result["sub_label"] = "No element"
        return result
    pair = _bq2_pair(elements)
    if pair is not None:
        result["state"] = "Ambiguous"
        result["sub_label"] = "Conflict"
        result["competing"] = [pair[0], pair[1]]
        result["denoted_states"] = [
            _denoted_state(entry, e, elements) for e in result["competing"]]
        result["banked_question_id"] = "BQ-2"
        result["effective_elements"] = _effective_elements(entry, elements)
        return result
    effective = _effective_elements(entry, elements)
    result["effective_elements"] = effective
    if not effective:
        result["state"] = "Ambiguous"
        result["sub_label"] = "No element"
        return result
    if len(effective) >= 2 and all(
            element.kind in _STATUS_LINE_KINDS
            for element in effective):
        # The entry carries nothing but bare Status lines and
        # they denote different states. No element of the entry
        # performs a ruling, a settlement, or a closure, and no
        # element carries a decider, so no element stands as an
        # unambiguous determining element between the competing
        # lines: the entry reports as Ambiguous, with the
        # competing elements quoted together (PIN-03, last row;
        # PIN-07, the disagreement with no unambiguous
        # determining element). A corroborated Banked head form,
        # where a decision block or a body paragraph element
        # stands beside the Status lines, never reaches this
        # branch, because such an element is not a Status line.
        denoted = [_denoted_state(entry, element, elements)
                   for element in effective]
        distinct = {state for state in denoted if state is not None}
        if len(distinct) >= 2:
            result["state"] = "Ambiguous"
            result["sub_label"] = "Conflict"
            result["competing"] = list(effective)
            result["denoted_states"] = denoted
            return result
    determining = effective[-1]
    bearing = [element for element in effective
               if element.disposition is not None
               or element.occurrence_kind is not None]
    if bearing and determining not in bearing:
        # A trailing element carrying no disposition and no
        # Status occurrence, a Decision label paragraph among
        # them, states no state of its own: the last element
        # that bears a disposition determines the entry.
        determining = bearing[-1]
    if (determining.decider is None
            and not any(element.occurrence_kind is not None
                        for element in elements)
            and all(element.kind == "labelled paragraph element"
                    for element in effective)):
        # An entry standing only in labelled paragraphs, the
        # F-02 form: the paragraphs together record one ruling,
        # and the element carrying the decider, the Ruled by
        # element, is the ruling element the row rests on, so
        # it is selected as determining where it carries the
        # same disposition the last element carries.
        for element in reversed(effective):
            if (element.decider is not None
                    and element.disposition == determining.disposition):
                determining = element
                break
    result["determining"] = determining
    disposition = _effective_disposition(entry, determining, elements)
    scope = _scope_of(determining, entry)
    condition = _effective_condition(determining)

    def finish(state, sub_label=None, label_element=None):
        result["state"] = state
        result["sub_label"] = sub_label
        primary = (label_element if label_element is not None
                   else determining)
        # The label comes from the determining element alone.
        # Brief section 5.4 rules a row whose determining element
        # names no decider carries no label and counts in no
        # decider subtotal, with "decider not recorded" in its
        # place; no fallback to any other element stands for that
        # label or for the subtotals it feeds.
        result["decider_label"] = _decider_label(primary)
        # The group listing carries its own label, read from the
        # whole entry in the forms the decider check accepts, so
        # the listing never states that a decider is not recorded
        # where the entry records one in such a form and no
        # decider finding fires. Where the determining element
        # itself names the decider, the two labels agree.
        listing_label = result["decider_label"]
        if listing_label is None and state in DECIDED_OUTCOMES:
            listing_label = _listing_decider_label(entry, elements)
        result["listing_decider_label"] = listing_label
        result["condition"] = condition
        result["remainder"] = _part_remainder(entry, determining)
        if result["remainder"]:
            result["remainder_texts"] = [result["remainder"]]
        result["underlying_state"] = _underlying_state(
            entry, determining, elements)
        if state in DECIDED_OUTCOMES and listing_label is None:
            result["annotation"] = "decider not recorded"
        return result

    # PIN-04 Shape B, second limb: an unclassifiable value as the
    # only Status line of an entry carrying decision evidence in
    # any form is determining and is not skipped, so no other
    # element governs in its place. Shape A, the only element with
    # no decision evidence anywhere, stands apart below.
    status_line_elements = [e for e in elements
                            if e.occurrence_kind is not None]
    unclassifiable_lines = [e for e in status_line_elements
                            if e.disposition is None]
    if (len(status_line_elements) == 1 and unclassifiable_lines
            and _entry_decision_evidence(entry, elements)):
        result["state"] = "Ambiguous"
        result["sub_label"] = "Single element"
        result["determining"] = unclassifiable_lines[0]
        result["competing"] = [unclassifiable_lines[0]]
        result["denoted_states"] = [None]
        result["condition"] = _effective_condition(
            unclassifiable_lines[0])
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
        if len(elements) == 1 and not _entry_decision_evidence(
                entry, elements):
            result["shape_a"] = True
            return finish("Open")
        result["state"] = "Ambiguous"
        result["sub_label"] = "Single element"
        result["competing"] = [determining]
        result["denoted_states"] = [None]
        result["condition"] = condition
        return result
    if scope.startswith("Part"):
        # The part rows stand before the Conditional row: a part
        # disposition with a named remainder and a stated condition
        # still derives its part state, with remainder and
        # condition both carried (plan Item 9, section 9.4). A
        # closure stated as decided for a part takes Closed as
        # decided for that part only and never Settled in part.
        if not _part_remainder(entry, determining):
            result["state"] = "Ambiguous"
            result["sub_label"] = "Single element"
            result["competing"] = [determining]
            result["denoted_states"] = [
                _denoted_state(entry, determining, elements)]
            result["condition"] = condition
            return result
        if disposition in ("Ruled", "Settled"):
            return finish("Settled in part")
        if disposition == "Closed":
            return finish("Closed as decided")
        result["state"] = "Ambiguous"
        result["sub_label"] = "Single element"
        result["competing"] = [determining]
        result["denoted_states"] = [
            _denoted_state(entry, determining, elements)]
        result["condition"] = condition
        return result
    if _pin12_shape(entry, elements, effective):
        return finish("Closed as decided")
    if condition:
        return finish("Conditional")
    if (determining.kind == "closing prose"
            and disposition in ("Banked", "Open")
            and not _decision_evidence(elements, exclude=determining)):
        # Closing prose the tool itself treats as a status
        # bearing element and names as the determining element,
        # stating in words that the entry was ruled or settled
        # and is closed, claims a decided state against the
        # open state its own disposition denotes: the two
        # readings disagree, and the entry takes the status
        # elements disagree treatment instead of deriving Open
        # in silence (Step 17 charge S17-ATK7-04, bounded to
        # closing prose standing as the determining element).
        claim_statement = determining.statement or ""
        # The two readings are stated in the neighbouring plain
        # words of the same contradiction, not only in the two
        # fixed phrases of the first cure: the decision verb
        # stands with a by phrase, with a time word, or with no
        # decider named at all, and the closure stands as now
        # closed, is closed, stands closed, been closed, closed
        # in full, or the bare word closed (Step 17 round 2
        # charge CH-8, S17-ATK2-7-02).
        # The same contradiction stands stated in noun forms
        # as well: a decision stated by its noun (the decision,
        # a decision) beside one of the closure forms above, or
        # closure stated by the word shut beside a ruling noun,
        # is the same status bearing statement in the
        # determining element position (Step 17 round 3 charge
        # CH-41, S17-ATK3-7-04). Each noun form stands only
        # beside its paired form: a decision noun with no
        # closure stated, and shut with no ruling noun stated,
        # stand outside this reading.
        # The pairings cross in the round 4 forms as well: the
        # decision noun beside shut, the ruling noun beside one
        # of the closure forms above, the verdict noun beside
        # one of those forms, and the decided verb beside the
        # closure word sealed each state the same contradiction
        # (Step 17 round 4 charge CH-62, S17-ATK4-7-04). The
        # crossings stand as charged and no further: a decision
        # noun beside sealed and a verdict noun beside shut are
        # not charged crossings and stand outside this reading,
        # as do the unpaired forms at the CH-41 bound.
        _closed_form = re.search(
            r"\b(?:now closed|is closed|stands closed|"
            r"been closed|closed in full|closed)\b",
            claim_statement, re.IGNORECASE)
        _decided_verb = re.search(r"\b(?:ruled|settled|decided)\b",
                                  claim_statement, re.IGNORECASE)
        _resolved_verb = re.search(r"\bresolved\b",
                                   claim_statement, re.IGNORECASE)
        _decision_noun = re.search(r"\bdecision\b",
                                   claim_statement, re.IGNORECASE)
        _ruling_noun = re.search(r"\bruling\b",
                                 claim_statement, re.IGNORECASE)
        _verdict_noun = re.search(r"\bverdict\b",
                                  claim_statement, re.IGNORECASE)
        _settlement_noun = re.search(r"\bsettlement\b",
                                      claim_statement,
                                      re.IGNORECASE)
        _shut_form = re.search(r"\bshut\b",
                               claim_statement, re.IGNORECASE)
        _sealed_form = re.search(r"\bsealed\b",
                                 claim_statement, re.IGNORECASE)
        # CH-83 stands elsewhere; this limb is CH-84, seat 7
        # S17-ATK5-7-04, ruled at record section 52 ruling
        # (f): two further named crossings only, the decided
        # verb beside shut and the verdict noun beside
        # sealed. The two K7 bound guards stand pinned
        # deriving Open in both directions: the decision noun
        # beside sealed and the verdict noun beside shut are
        # not crossings of this reading, and no cure here
        # widens by pattern family.
        # CH-102, S17-ATK6-7-04, named crossings only under
        # the same ruling (f) as restated at section 58: two
        # further named crossings, the ruling noun beside
        # sealed and the settlement noun beside shut, derive
        # as the CH-84 crossings derive. The two bound
        # guards stand pinned deriving Open in both
        # directions, and no cure here widens by pattern
        # family.
        # CH-135, S17-ATK7-7-04, named crossings only under
        # the same ruling: two further named crossings, the
        # settlement noun beside closed and the settlement
        # noun beside sealed, derive as the CH-102 crossings
        # derive. The two bound guards stand pinned deriving
        # Open in both directions, and no cure here widens
        # by pattern family.
        # CH-169, S17-ATK8-7-05, named crossings only under
        # the same ruling: two further named crossings, the
        # resolved verb beside closed and the sealed verb
        # beside closed, derive as the CH-135 crossings
        # derive. The resolved verb stands in its own search
        # and pairs with the closed form only, so no decided
        # verb pairing widens; the sealed form pairs with
        # the closed form only where it stands as the
        # deciding act itself beside a stated closure. The
        # two bound guards stand pinned deriving Open in
        # both directions, and no cure here widens by
        # pattern family.
        # CH-204, S17-ATK9-7-06, named crossings only under
        # the same ruling: three further named crossings,
        # the resolved verb beside shut, the sealed verb
        # beside shut, and the resolved verb beside sealed,
        # derive as the CH-169 crossings derive. Shut stands
        # as a closure form beside the decided verb, the
        # ruling noun, and the settlement noun in this same
        # reading, and sealed stands as a closure side
        # beside the decided verb, the verdict noun, the
        # ruling noun, and the settlement noun. The two
        # bound guards stand pinned deriving Open in both
        # directions, and no cure here widens by pattern
        # family.
        if ((_decided_verb and _closed_form)
                or (_resolved_verb and _closed_form)
                or (_sealed_form and _closed_form)
                or (_resolved_verb and _shut_form)
                or (_sealed_form and _shut_form)
                or (_resolved_verb and _sealed_form)
                or (_decision_noun and _closed_form)
                or (_shut_form and _ruling_noun)
                or (_decided_verb and _sealed_form)
                or (_decision_noun and _shut_form)
                or (_ruling_noun and _closed_form)
                or (_verdict_noun and _closed_form)
                or (_decided_verb and _shut_form)
                or (_verdict_noun and _sealed_form)
                or (_ruling_noun and _sealed_form)
                or (_settlement_noun and _shut_form)
                or (_settlement_noun and _closed_form)
                or (_settlement_noun and _sealed_form)):
            others = [e for e in effective
                      if e is not determining
                      and _denoted_state(entry, e, elements)
                      == "Open"]
            if others:
                result["state"] = "Ambiguous"
                result["sub_label"] = "Conflict"
                result["competing"] = [determining] + others
                result["denoted_states"] = (
                    ["Closed as decided"]
                    + [_denoted_state(entry, e, elements)
                       for e in others])
                result["condition"] = condition
                return result
    if disposition in ("Banked", "Open", "Relative"):
        if _decision_evidence(elements, exclude=determining):
            earlier = [e for e in effective[:-1]
                       if _effective_disposition(entry, e, elements)
                       in _DECIDED_DISPOSITIONS]
            if earlier and all(
                    e.kind == "heading borne evidence" for e in earlier):
                # The tail form pair at PIN-11: a heading element
                # against the closing sentence element of the
                # single paragraph. The later unambiguous element
                # governs under the governing rule, so the banked
                # closing sentence determines the entry as Open
                # and the heading element alone does not take the
                # entry back to the decided state or into the
                # Ambiguous form for earlier decision evidence.
                return finish("Open")
            if (determining.kind in ("variant phrasing",
                                     "tail paragraph element",
                                     "closing prose")
                    or (determining.kind == "labelled paragraph element"
                        and (determining.statement or "").lstrip(
                            ).startswith("Ruling outcome:"))) and earlier:
                determining = earlier[-1]
                result["determining"] = determining
                disposition = _effective_disposition(entry, determining,
                                                     elements)
                scope = _scope_of(determining, entry)
                condition = _effective_condition(determining)
                if condition:
                    return finish("Conditional")
                if (scope.startswith("Part")
                        and disposition in ("Ruled", "Settled")
                        and _part_remainder(entry, determining)):
                    # The trailing open element is the remainder
                    # naming itself, in one of the remainder verb
                    # forms (round 3 charge CH-44, A3-10-F2): the
                    # reassigned part act derives its part state
                    # here, as the same act does where the
                    # remainder paragraph bears no element.
                    return finish("Settled in part")
            else:
                result["state"] = "Ambiguous"
                result["sub_label"] = "Conflict"
                result["competing"] = [determining] + earlier
                result["denoted_states"] = [
                    _denoted_state(entry, e, elements)
                    for e in result["competing"]]
                result["condition"] = condition
                return result
        else:
            return finish("Open")
    if disposition == "Ruled":
        return finish("Ruled")
    if disposition == "Settled":
        return finish("Settled")
    if disposition == "Closed":
        # A completion form does not convert the row: the mapping
        # table's Closed row maps disposition Closed without a
        # ruling or settlement form to Closed as decided, and the
        # completion wording is already ruled as a decider label
        # on Closed rows ("completion under DQ-145", brief section
        # 5.4), which _decider_label supplies from the determining
        # element. No table row reads it as a settlement.
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
    result["denoted_states"] = [
        _denoted_state(entry, e, elements) for e in result["competing"]]
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


def _compose_unit_identifier(kind, start_line):
    """The unit identifier form at plan Item 3, section 3.3: the
    words file level unit, followed by the kind value, followed
    by the start line of the span."""
    return ("file level unit, kind %s, beginning at line %s"
            % (kind, start_line))


def _unit_identifier(model, span=None, segment=None):
    """The identifier of the file level unit a file level finding
    stands on, in the section 3.3 form. The unit is read from the
    File shape units list where one covers the finding span or
    the segment; where no unit stands in the list, the identifier
    is composed from the segment kind and span, and where neither
    stands, from the file header unit. The literal FILE stands
    only where the model carries no unit at all, as on a model
    double with an empty units list."""
    units = list(_get(model, "units") or [])
    wanted_start = None
    if span is not None:
        wanted_start = _get(span, "start_line")
    if segment is not None and wanted_start is None:
        segment_span = _get(segment, "span")
        if segment_span is not None:
            wanted_start = _get(segment_span, "start_line")
    if wanted_start is not None:
        for unit in units:
            unit_span = _get(unit, "span")
            if unit_span is None:
                continue
            start = _get(unit_span, "start_line")
            end = _get(unit_span, "end_line")
            if start is not None and start <= wanted_start and (
                    end is None or wanted_start <= end):
                identifier = _get(unit, "unit_identifier")
                if identifier:
                    return identifier
                return _compose_unit_identifier(
                    _get(unit, "kind"), start)
    for unit in units:
        if _get(unit, "kind") == "file header":
            identifier = _get(unit, "unit_identifier")
            if identifier:
                return identifier
            unit_span = _get(unit, "span")
            return _compose_unit_identifier(
                "file header",
                _get(unit_span, "start_line") if unit_span else 0)
    if segment is not None:
        segment_span = _get(segment, "span")
        start = (_get(segment_span, "start_line")
                 if segment_span is not None else 0)
        kind = _get(segment, "kind") or "other file level segment"
        return _compose_unit_identifier(kind, start or 0)
    if units:
        unit = units[0]
        identifier = _get(unit, "unit_identifier")
        if identifier:
            return identifier
        unit_span = _get(unit, "span")
        return _compose_unit_identifier(
            _get(unit, "kind"),
            _get(unit_span, "start_line") if unit_span else 0)
    return FILE_ID


def _rule_order_key(rule_id):
    if isinstance(rule_id, int):
        return (0, rule_id, "")
    return (1, 0, str(rule_id))


def _file_order_key(finding):
    span = finding.line_span
    start = span.start_line if span is not None else 0
    end = span.end_line if span is not None else 0
    evidence = finding.evidence
    evidence_text = evidence if isinstance(evidence, str) else str(evidence)
    # The key carries the evidence and statement texts
    # themselves, not an encoded copy of either (Step 17
    # round 7, CH-150): a sort holds the key of every finding
    # it sorts at once, and the encoded form held one whole
    # copy of the evidence line per finding, a transient peak
    # at the product of the cited token count and the line
    # length on the note segment citation form. The order
    # stands exactly as the encoded key ordered it, because
    # the UTF-8 byte order of a text is its code point order,
    # so the texts compare in the order their encodings
    # compared. The key now references texts the findings
    # already carry and allocates no copy of either.
    return (_rule_order_key(finding.rule_id), start, end,
            evidence_text,
            (finding.statement or ""))


# ---------------------------------------------------------------------
# Unit 3b: entry local checks (checks 2, 3, 4, 5, 7, 9 and 10)
# ---------------------------------------------------------------------

_OPTIONS_LABELS = ("Options",)
_QUESTION_LABELS = ("The question",)


_PROSE_OPTIONS_LINE = "The options, stated plainly:"


def _decision_block_line_numbers(entry):
    """The entry body line numbers standing inside a decision
    block: every line from a block heading line to its span
    end line, inclusive. Lines inside a decision block are
    the block's own, and no entry level presence scan reads
    them (Step 17 charge F-17-09, extended to the prose
    options limb by round 2 charge CH-22)."""
    numbers = set()
    for block in _get(entry, "decision_blocks") or []:
        span = _get(block, "span")
        if span is None:
            continue
        start = _get(span, "start_line")
        if start is None:
            start = _get(span, "start")
        end = _get(span, "end_line")
        if end is None:
            end = _get(span, "end")
        if start is None:
            continue
        if end is None:
            end = start
        for number in range(int(start), int(end) + 1):
            numbers.add(number)
    return numbers


def _options_alias_label(label):
    """Whether a recorded label, as written, stands in one
    of the bounded Options alias forms: the words the
    options, or the three options, standing as whole words
    at the head of the label. The alias takes a word
    boundary after the options word: a label that merely
    opens with those letters and continues the word (a
    nonsense label opening the optionsXYZ) is no alias form
    (round 2 charge CH-22, finding S17-ATK2-17-03).

    The label is read as written, at the same case exactness
    as every sibling field label (Step 17 round 4 charge
    CH-72, finding S17-ATK4-17-04): the alias stands only in
    its sentence case form, the first word standing as The
    and every following word in lower case, the form the
    corpus carries and the CH-22 cure enumerated. The all
    capitals, mixed case, title case, and all lower case
    forms count no more than the same forms of the exact
    label count, which is not at all."""
    words = (label or "").split()
    if not words or words[0] != "The":
        return False
    if any(word != word.lower() for word in words[1:]):
        return False
    lowered = (label or "").lower()
    for prefix in ("the three options", "the options"):
        if lowered == prefix:
            return True
        if lowered.startswith(prefix):
            following = lowered[len(prefix)]
            if not (following.isalnum() or following == "_"):
                return True
    return False


_QUESTION_AS_PUT_PREFIX = "Question as put"


def _question_as_put_label(label):
    """Whether a recorded label, as written, stands in the
    Question as put alias form of the question field: the
    alias words standing at the head of the label at a word
    boundary, in the form the Options alias boundary takes
    since CH-22. A label that merely opens with those words
    and continues the final word (Question as putative,
    Question as putXYZ, Question as putter, Question as
    putting) is no alias form (Step 17 fix wave 5, CH-92,
    finding S17-ATK5-17-04). The two recorded forms stand
    credited exactly as before: the alias alone, and the
    alias standing before its recorded continuation, Question
    as put on the Questions space, whose next character is a
    plain space and so stands at the boundary."""
    text = label or ""
    if text == _QUESTION_AS_PUT_PREFIX:
        return True
    if text.startswith(_QUESTION_AS_PUT_PREFIX):
        following = text[len(_QUESTION_AS_PUT_PREFIX)]
        return not (following.isalnum() or following == "_")
    return False


def _prefix_at_word_boundary(label, prefix):
    """Whether a recorded label stands in a prefix form at
    its word boundary: the prefix standing as the whole
    label, or standing at its head with the character
    after it no letter, digit, or underscore, the boundary
    form the Options alias takes since CH-22 and the
    Question as put alias takes since CH-92."""
    text = label or ""
    if text == prefix:
        return True
    if text.startswith(prefix):
        following = text[len(prefix)]
        return not (following.isalnum() or following == "_")
    return False


def _alias_prefix_matches(label, prefix):
    """Whether a recorded label matches one prefix of a
    presence test: every prefix reads at its word
    boundary, the Question as put alias under
    _question_as_put_label (CH-92) and every other prefix
    under _prefix_at_word_boundary, in the one boundary
    form (Step 17 round 7 charge CH-149, finding
    S17-ATK7-17-03). Before this cure the decided entry
    outcome and landing prefixes read as a plain
    startswith, so a label that merely opened with those
    words and continued the final word (Ruling
    outcomeXYZ, Ruling outcomes, Where the ruling
    landedness) counted as the outcome or the landing
    record."""
    if prefix == _QUESTION_AS_PUT_PREFIX:
        return _question_as_put_label(label)
    return _prefix_at_word_boundary(label, prefix)


def _field_line_blocked(entry, field, blocked=None):
    """Whether a recorded field stands on a line inside a
    decision block of its entry. A field carrying no line
    number stands unblocked: the recorded forms carry their
    line, and a carrier that records none stands as it
    stood."""
    if blocked is None:
        blocked = _decision_block_line_numbers(entry)
    line = _get(field, "line")
    return line is not None and line in blocked


def _prose_options_line_index(entry):
    """The body line index of the corpus prose options heading,
    the line "The options, stated plainly:", or None where no
    body line stands in that exact form. The test is equality
    of the whole stripped line, not a prefix: it restores the
    one prose form the corpus carries, and it takes no form
    of the Options label itself. A prose heading standing
    inside a level 4 decision block counts for nothing: the
    block's lines are the block's own, as every sibling
    presence test already reads them (round 2 charge CH-22,
    finding S17-ATK2-17-04)."""
    blocked = _decision_block_line_numbers(entry)
    for index, (line, text) in enumerate(_body_lines(entry)):
        if line in blocked:
            continue
        if (text or "").strip() == _PROSE_OPTIONS_LINE:
            return index
    return None


def _has_options_field(entry):
    # The Options presence test stands at the same exactness
    # as its sibling field tests: it reads the recorded field
    # labels, with no stripped line fallback over the body
    # lines for the Options label itself, so a leading space,
    # a tab separator, or a missing space form that every
    # sibling label rejects is rejected here too (Step 17
    # charge F-17-07). One bounded restoration stands beside
    # that exactness: the corpus prose options heading, the
    # line "The options, stated plainly:", for which parse
    # records no Options field, counts as the field standing
    # present, as it did before fix wave 1 (Step 17 fix wave 1
    # supplementary repair, seat D1, triage items U1 and U2).
    # The restoration is the whole line equality test in
    # _prose_options_line_index; it names no Options label
    # form and reopens none of the charged forms.
    # A field standing on a line inside a decision block is
    # the block's own, not a field of the entry, for the
    # alias limb as for every sibling presence test (Step 17
    # round 4 charge CH-72, finding S17-ATK4-17-05): parse
    # already withholds the exact open field labels inside a
    # block, and this test reads the recorded fields on the
    # same bound for both the exact label and its alias.
    blocked = _decision_block_line_numbers(entry)
    for field in _get(entry, "fields") or []:
        label = str(_get(field, "label", "") or "")
        if _field_line_blocked(entry, field, blocked):
            continue
        if label == "Options" or _options_alias_label(label):
            return True
    return _prose_options_line_index(entry) is not None


def _options_value_present(entry):
    """Whether an Options field stands present on its value:
    a recorded Options field carrying a non empty value, or
    the label alone with its option lines standing as the
    following body lines, the shape whose collected lines are
    the field value (Step 17 charge F-17-02)."""
    # The collected lines scans below skip decision block
    # lines, for the exact label and for its alias alike: a
    # line inside a block is the block's own, and dash lines
    # standing there are no field value of the entry (Step
    # 17 round 4 charge CH-72, finding S17-ATK4-17-05). A
    # recorded field standing itself on a block line counts
    # for nothing on either limb, as _has_options_field
    # reads it.
    blocked = _decision_block_line_numbers(entry)

    def collected_lines_present(label):
        collected = False
        for line, text in _body_lines(entry):
            if line in blocked:
                continue
            stripped = (text or "").strip()
            if stripped == label + ":" or \
                    stripped.startswith(label + ":"):
                collected = True
                continue
            if collected:
                if stripped.startswith("- "):
                    return True
                if stripped:
                    break
        return False

    exact_fields = [
        f for f in _get(entry, "fields") or []
        if str(_get(f, "label", "") or "") == "Options"
        and not _field_line_blocked(entry, f, blocked)]
    if exact_fields:
        value = _get(exact_fields[0], "value") or ""
        if value.strip():
            return True
        return collected_lines_present("Options")
    for f in _get(entry, "fields") or []:
        label = str(_get(f, "label", "") or "")
        if _field_line_blocked(entry, f, blocked):
            continue
        if _options_alias_label(label):
            if (_get(f, "value") or "").strip():
                return True
            # The alias limb takes the collected lines reading
            # the exact label limb takes (round 3 charge CH-38,
            # alias limb of S17-ATK3-17-03): on an empty value
            # the label alone with its option lines standing as
            # the following body lines counts as present.
            return collected_lines_present(label)
    # The corpus prose form, reached only where no recorded
    # Options field stands at all, so the empty value ground
    # above is untouched: the prose heading line counts as
    # value present only where its option lines stand as the
    # following body lines, blank lines aside, in the same
    # collected lines shape the label alone form takes (Step
    # 17 fix wave 1 supplementary repair, seat D1).
    prose_index = _prose_options_line_index(entry)
    if prose_index is not None:
        for _line, text in _body_lines(entry)[prose_index + 1:]:
            stripped = (text or "").strip()
            if not stripped:
                continue
            return stripped.startswith("- ")
    return False


def _field_value_present(entry, labels, prefixes=(),
                         require_word_character=False):
    """Whether a field stands present on its value, not on
    its label alone: a recorded field whose label matches and
    whose value carries non empty matter (Step 17 charge
    F-17-02). Where require_word_character stands, a value of
    punctuation only, carrying no word character, stands as no
    value, as a whitespace only value already does (Step 17
    round 3 charge CH-40, S17-ATK3-7-01, on the three decided
    entry limbs in _check5 that read through this test)."""
    for f in _get(entry, "fields") or []:
        label = str(_get(f, "label", "") or "")
        if label in labels or any(
                _alias_prefix_matches(label, prefix)
                for prefix in prefixes):
            value = _get(f, "value") or ""
            if require_word_character:
                if re.search(r"\w", value):
                    return True
            elif value.strip():
                return True
    return False


def _is_damaged_heading_marker_word(word):
    """Whether a heading marker word carries one interior
    damage of a cured class (round 9 charge CH-221, seat
    17 finding S17-ATK9-17-03): the word stands six
    characters long, its letters read without case stand
    one position from the Status word, that position is
    an interior position of the word, the second letter
    position through the last, and the character standing
    there stands in the interior classes of the CH-128
    limb (a punctuation, symbol, or number character, or
    a letter of a script other than the ASCII letters)
    or in the run ground categories of record section 52
    ruling (a) (the mark categories and the format,
    control, space separator, unassigned, and private
    use categories, read here by category). The CH-179
    heading limb as landed takes the marker word whole,
    so one such character removed the heading line from
    every reading at once: the line start Status reading
    does not reach a level 4 heading line, and the near
    marker reading does not reach it either. The bounds
    stand stated here: two interior damages on the
    marker word stand outside this reading, a marker
    word of any other length stands outside it, a damage
    at the first letter position stands outside it, and
    an ASCII letter standing in place of a marker letter
    stands outside it, the letter readings governing
    letters as before."""
    if len(word) != 6:
        return False
    differing = [index for index in range(6)
                 if word[index].lower() != "status"[index]]
    if len(differing) != 1:
        return False
    index = differing[0]
    if index == 0:
        return False
    category = unicodedata.category(word[index])
    if category.startswith(("P", "S", "N")):
        return True
    if category.startswith("L") and \
            not word[index].isascii():
        return True
    return category.startswith("M") or category in (
        "Cf", "Cc", "Zl", "Zp", "Zs", "Cn", "Co")


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
    # CH-83, S17-ATK5-7-06, on its own locus: a Status line
    # standing as a heading inside an entry is read by the
    # heading reading as a heading form and so stands outside
    # the line start Status reading: it is counted nowhere and
    # listed nowhere. It takes this signal, on the near marker
    # family terms, so the claim does not vanish in silence.
    # The bound: a heading line carrying the Status marker at
    # its head only; no governed heading form carries that
    # marker, and no heading becomes an occurrence by this
    # limb.
    # CH-101, S17-ATK6-7-06: the heading limb reads the
    # Status marker in either case, as the ghost and claim
    # scans of this surface read their forms in either
    # case; the capitalised form's counted and listed
    # treatment stands unmoved.
    # CH-137, S17-ATK7-7-06: the heading limb also reads
    # the Status marker standing in bold dress at the head
    # of the heading line, the marker wrapped in a pair of
    # asterisk runs with its colon inside the dress, the
    # one dress form charged. No other dress is read.
    # CH-179, S17-ATK8-7-08: the heading limb also reads
    # the Status marker standing in italic dress (a single
    # asterisk run on each side, its colon inside the
    # dress), in underscore dress (a double underscore run
    # on each side, its colon inside the dress), or in
    # bold dress with its colon standing outside the dress.
    # The dress run stands on either side of the marker or
    # before its colon, in the one combined form below; no
    # other dress is read.
    # CH-212, S17-ATK9-7-08: the heading limb also reads
    # the Status marker standing in single underscore
    # dress (a single underscore run on each side, its
    # colon inside the dress) or in triple asterisk dress
    # (a triple asterisk run on each side, its colon
    # inside the dress), in the same combined form; no
    # other dress is read.
    # CH-221, S17-ATK9-17-03: the heading limb also reads
    # the Status marker carrying one interior damage of a
    # cured class inside the marker word, in the same
    # dress forms, on the bound stated at
    # _is_damaged_heading_marker_word: the damaged marker
    # took no signal at all, counted nowhere and listed
    # nowhere in silence at a clean exit, where the clean
    # heading forms take this signal.
    for line_number, text in _body_lines(entry):
        if re.match(r"^\s*#{1,6}\s+(?:(?:\*\*\*|\*\*|\*|__|_)\s*)?Status\s*"
                    r"(?:(?:\*\*\*|\*\*|\*|__|_)\s*)?:"
                    r"(?:\s*(?:\*\*\*|\*\*|\*|__|_))?", text or "",
                    re.IGNORECASE):
            findings.append(_finding(
                2, "Warning", display_id,
                Span(line_number, line_number), text,
                "A Status line standing as a heading inside "
                "the entry is counted nowhere and listed "
                "nowhere: " + text,
                basis="a heading dressed status line carries "
                      "no element"))
            continue
        damaged = re.match(
            r"^\s*#{1,6}\s+(?:(?:\*\*\*|\*\*|\*|__|_)\s*)?(\S{6})\s*"
            r"(?:(?:\*\*\*|\*\*|\*|__|_)\s*)?:"
            r"(?:\s*(?:\*\*\*|\*\*|\*|__|_))?", text or "")
        if damaged and _is_damaged_heading_marker_word(
                damaged.group(1)):
            findings.append(_finding(
                2, "Warning", display_id,
                Span(line_number, line_number), text,
                "A Status line standing as a heading inside "
                "the entry is counted nowhere and listed "
                "nowhere: " + text,
                basis="a heading dressed status line carries "
                      "no element"))
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
    determining = derived["determining"]
    if determining is not None:
        # The tail form pair at PIN-11: the heading element and
        # the closing sentence element of the single paragraph
        # differ, and the later element governs. Where the
        # heading element is the only element denoting a state
        # other than the determining state, that pair takes no
        # disagreement Warning: the plan WV-7 finding results
        # name no such Warning for that shape.
        others = [element for value, holders in denoted.items()
                  if value != state for element in holders
                  if element is not determining]
        if others and all(
                element.kind == "heading borne evidence"
                for element in others):
            return []
    head = None
    for element in elements:
        if element.kind == "line start Status line":
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


_DECIDER_LINE_RE = re.compile(
    r"^\s*(Ruled|Settled|Decided) by:?\s+[^.]*\.?\s*$")


# The tokens of a decider attribution standing alone: the
# decider names the recorded forms carry, the grant words of
# the recorded Manager grant form, and the disposition words
# themselves. Matter made only of these tokens attributes a
# decision or restates its disposition; it records no ruling.
_ATTRIBUTION_TOKENS = frozenset((
    "captain", "jp", "manager", "grant", "under",
    "ruled", "settled", "decided", "closed",
))


# The person name words of the name only forms the round 7
# papers evidence beside the decider initials: the surname
# Morgan and the further name words Stanley and Mary. A
# matter made only of these words, in any case, is a name
# restated, not ruling matter.
_NAME_TOKENS = frozenset((
    "morgan", "stanley", "mary",
))


_MATTER_STOPWORDS = frozenset((
    "the", "a", "an", "and", "or", "of", "in", "on", "at", "to",
    "by", "for", "with", "from", "as", "it", "its", "this",
    "that", "these", "those", "now", "is", "are", "was", "were",
    "be", "been", "states", "stated", "form", "forms",
))


def _matter_tokens(text):
    """The content tokens of a text: its words with the
    function words and the generic form words set aside, so
    what remains is the matter the text is about."""
    return {token
            for token in re.findall(r"[a-z0-9]+", (text or "").lower())
            if token not in _MATTER_STOPWORDS}


def _is_token_sequence(joined):
    """Whether a joined run string reads whole as a sequence
    of attribution tokens and name tokens, in some order, with
    nothing left over: "captain" as one attribution token,
    "morganstanley" as the two name tokens "morgan" and
    "stanley". The test is reachability over the string, so
    its answer does not depend on the order the token set is
    read in."""
    if not joined:
        return False
    vocabulary = _ATTRIBUTION_TOKENS | _NAME_TOKENS
    reachable = {0}
    for start in range(len(joined)):
        if start not in reachable:
            continue
        for token in vocabulary:
            if joined.startswith(token, start):
                reachable.add(start + len(token))
    return len(joined) in reachable


def _labelled_matter_tokens(text):
    """The content tokens of the matter under a Ruled or
    Settled label, with the decider attribution set aside.

    The reduction starts from _matter_tokens with the
    attribution tokens removed, as the labelled paragraph
    condition reads it. A word broken by punctuation inside
    the word is read whole before it is set aside: where
    the runs of one word join to an attribution token, the
    word is that attribution in a punctuated spelling, and
    its runs are set aside with it, so "J.P." sets aside
    as "jp", "Cap-tain" as "captain", and "Man-ager" and
    "Man.ager" as "manager" (finding A6-8-1). The same
    attribution and its name are read whole across a space
    as well: two or three standing words whose runs join
    to an attribution token or to a name token are that
    attribution or that name in a spaced spelling, and
    their runs are set aside with it, so "Cap tain" sets
    aside as "captain", "Man ager" as "manager", "Gra nt"
    as "grant", "Mor gan" as the surname "morgan", and the
    spaced initials "J. P.", "J, P" and "J P" set aside as
    "jp" (findings A7-2-1 and A7-8-1). Where such an
    attribution word stands, fragmented inside the word or
    spaced, and every further word carrying a content
    token is a name word, capitalised or one of the name
    tokens, the matter is a name in initials form alone,
    as "J.P. Morgan" is: the name words stand as the name
    of that attribution and are set aside with it, in one
    word or in two, and in either case, so "J.P. morgan"
    and "J.P. Morgan Stanley" set aside with "J.P.
    Morgan". The two breaks also read together: two
    standing words, at least one of them itself broken by
    punctuation inside the word, whose runs together read
    whole as a sequence of attribution tokens and name
    tokens are that attribution or that name in a combined
    spelling, and their runs are set aside with it, so
    "Ca.p tain" and "Cap t.ain" set aside as "captain",
    "Ma.n ager" as "manager", and "Gr.a nt" as "grant"
    (finding A8-8-1 part (b)). And a name word itself
    counts in a joined spelling: a further word whose runs
    are two or three of the name tokens, joined by
    punctuation inside one word, is those name words, so
    "morgan-stanley" and "morgan-stanley-mary" set aside
    with "morgan stanley" and "morgan stanley mary"
    (findings A8-3-1 and A8-8-1 part (a)). The same name
    also counts where the separator stands inside a name
    token rather than at its boundary: a further word
    carrying two or more runs, no run of it itself an
    attribution token or a name token, whose joined form
    reads whole as a sequence of attribution tokens and
    name tokens under _is_token_sequence, is that
    sequence in a displaced spelling, so
    "morga-nstanley" sets aside as "morgan" and
    "stanley", and "capt-ainmorgan" as "captain" and
    "morgan" (finding A9-8-1). A word whose runs stand
    whole as tokens, as "morgan-captain" does, is not
    read by this step, and a word carrying one run
    alone, as the separator free "morganstanley" does,
    is not read by it either. A word carrying
    content in any other position
    stands, so genuine ruling matter beside such a name
    still counts: a further word that is neither
    capitalised nor a name token keeps the whole matter
    standing, and a name, a number, or a word that stands
    whole and unrecorded, with no fragmented or spaced
    attribution word beside it, still counts as it did
    before.
    """
    tokens = _matter_tokens(text) - _ATTRIBUTION_TOKENS
    words = []
    removed = set()
    anchored = False
    for index, word in enumerate((text or "").split()):
        runs = re.findall(r"[a-z0-9]+", word.lower())
        joined = "".join(runs)
        if len(runs) > 1 and joined in _ATTRIBUTION_TOKENS:
            anchored = True
            removed.add(index)
            tokens.difference_update(runs)
        words.append((word, runs, joined))
    entries = [index for index, (word, runs, joined)
               in enumerate(words) if runs]
    position = 0
    while position < len(entries):
        matched = 0
        for size in (2, 3):
            group = entries[position:position + size]
            if len(group) < size:
                continue
            if any(len(words[index][1]) != 1 for index in group):
                continue
            joined = "".join(words[index][2] for index in group)
            if joined in _ATTRIBUTION_TOKENS \
                    or joined in _NAME_TOKENS:
                matched = size
                break
        if matched:
            anchored = True
            for index in entries[position:position + matched]:
                removed.add(index)
                tokens.difference_update(words[index][1])
            position += matched
        else:
            position += 1
    remaining = [index for index in entries if index not in removed]
    position = 0
    while position < len(remaining):
        group = remaining[position:position + 2]
        if len(group) == 2 and any(
                len(words[index][1]) > 1 for index in group):
            joined = "".join(words[index][2] for index in group)
            if _is_token_sequence(joined):
                anchored = True
                for index in group:
                    removed.add(index)
                    tokens.difference_update(words[index][1])
                position += 2
                continue
        position += 1
    if anchored:
        others = [(word, runs, joined)
                  for index, (word, runs, joined) in enumerate(words)
                  if index not in removed and runs
                  and joined not in _ATTRIBUTION_TOKENS
                  and joined not in _MATTER_STOPWORDS]
        if others and all(
                joined in _NAME_TOKENS
                or (len(runs) >= 2
                    and all(run in _NAME_TOKENS for run in runs))
                or (len(runs) >= 2
                    and _is_token_sequence(joined)
                    and all(run not in _ATTRIBUTION_TOKENS
                            and run not in _NAME_TOKENS
                            for run in runs))
                or [char for char in word if char.isalpha()]
                and [char for char in word if char.isalpha()][0].isupper()
                for word, runs, joined in others):
            for word, runs, joined in others:
                tokens.difference_update(runs)
    return tokens


def _ruling_matter_tokens(entry):
    """The content tokens of the entry's own ruling text.

    The ruling text is read from the entry body: where a
    segment opens with the Ruled label, the ruling text runs
    from that segment on, and the segments before it, its
    origin framing among them, do not count. Where no segment
    opens with that label, every body segment counts except
    the Landed segments themselves and the Origin and Status
    segments. A Landed segment never counts toward its own
    ruling text, so a matter named only inside the landing
    claim itself earns nothing. The landing claim runs to the
    end of its paragraph, a paragraph being a run of body
    lines standing between blank lines, the segmentation the
    parse stage itself uses: every segment standing after a
    Landed segment in the same paragraph is part of that
    claim and counts toward the ruling text no more than the
    Landed segment itself does, so a matter named only in
    such a segment, a trailing sentence repeating the stated
    matter among them, earns nothing (finding A5-8-1).
    Within that same paragraph, a segment standing before
    the Landed segment counts only where it is itself a
    ruling segment, a segment carrying the Ruled label or
    the Ruling label as the opening of a ruling clause, at
    its head as in the DQ-167 shape or within it where the
    sentence segmentation joins the clause to the words
    standing before it in the same segment, as in the tail
    form: such a ruling segment, standing before the
    Landed segment in its paragraph, counts as a ruling
    segment does, and a plain prose sentence of that
    paragraph, standing before the Landed segment and
    outside the ruling segment run, counts no more than
    one standing after it does, so a matter named only in
    such a sentence earns nothing (findings A6-2-1 and
    A6-8-3). Segments standing in any other paragraph
    count under the rules above as they did before.
    """
    body = _body_text(entry)
    segments = _sentence_segments(body)
    # The paragraph each segment stands in, by the character
    # offset the segment starts at. Paragraphs are the runs
    # of non blank lines of the body, split on blank lines.
    paragraph_starts = [0]
    offset = 0
    for line in body.split("\n"):
        offset += len(line) + 1
        if line.strip() == "":
            paragraph_starts.append(offset)
    segment_paragraphs = []
    cursor = 0
    for segment in segments:
        found = body.find(segment, cursor)
        if found < 0:
            found = cursor
        cursor = found + len(segment)
        paragraph = 0
        for start in paragraph_starts:
            if start <= found:
                paragraph += 1
        segment_paragraphs.append(paragraph)
    landed_in_paragraph = {}
    for index, segment in enumerate(segments):
        if segment.lstrip().startswith("Landed:"):
            landed_in_paragraph.setdefault(
                segment_paragraphs[index], index)
    ruled_start = None
    for index, segment in enumerate(segments):
        if segment.lstrip().startswith(("Ruled:", "Ruling:")):
            ruled_start = index
            break
    tokens = set()
    for index, segment in enumerate(segments):
        stripped = segment.lstrip()
        if stripped.startswith("Landed:"):
            continue
        landed_index = landed_in_paragraph.get(
            segment_paragraphs[index])
        if landed_index is not None and index > landed_index:
            continue
        if landed_index is not None and index < landed_index \
                and not re.search(r"\b(?:Ruled|Ruling):", segment):
            continue
        if ruled_start is not None and index < ruled_start:
            continue
        if ruled_start is None and stripped.startswith(
                ("Origin:", "Status:")):
            continue
        tokens.update(_matter_tokens(segment))
    return tokens


def _is_decider_line(statement):
    """A statement that only names a decider, in the form "Ruled
    by: Captain JP". Such a line is decider evidence. It is not
    ruling text and it is not an outcome."""
    return bool(_DECIDER_LINE_RE.match(statement or ""))


_DECIDER_VERB_BY_RE = re.compile(
    r"\b(?:Ruled|Settled|Decided) by\b")


def _decider_verb_form_present(body):
    """Whether the body carries the decider verb form with
    decider matter standing after "by": the verb form (Ruled,
    Settled, or Decided, followed by "by" ending at a word
    boundary) counts only where a word character stands after
    "by" in the same paragraph, past the separator characters
    standing between "by" and the matter. The separator run
    takes every boundary character the Step 16 pins record:
    punctuation of every kind, doubled and triple separators,
    punctuation standing directly against the name, whitespace
    of every class including the line break and the non
    breaking space, and the boundary marks. The bare field
    line "Ruled by:" standing alone in its paragraph carries
    no word character after "by" in that paragraph, so it
    records no decider (Step 17 round 2 charge CH-6,
    S17-ATK2-7-01, narrowed at the fix wave 2 closing, defect
    D1, so the Step 16 bound forms the first cure reading
    lost stand recorded again)."""
    for match in _DECIDER_VERB_BY_RE.finditer(body or ""):
        rest = (body or "")[match.end():]
        paragraph_rest = re.split(
            r"\n\s*\n", rest, maxsplit=1)[0]
        if re.search(r"\w", paragraph_rest):
            return True
    return False


_GHOST_SUBJECT_PATTERNS = (
    # CH-132, S17-ATK7-7-01: the is pattern carries sealed
    # beside its standing words, the Seal family standing
    # in the closing prose reading of this product as a
    # closure word since CH-62.
    # CH-165, S17-ATK8-7-02: the is pattern carries parked
    # and presented beside its standing words, as the has
    # been, stands, and remains and stays patterns of this
    # scan carry both since CH-133 and the claim is list
    # has carried both as governed states all along.
    # CH-199, S17-ATK9-7-01: the is pattern carries
    # resolved beside its standing words, as the claim is
    # list of the claim scan carries it since CH-178 and
    # the Resolve forms stand in the verb first list of
    # this scan since CH-101.
    re.compile(r"\bDQ-([0-9]+)\s+is\s+(?:decided|closed|settled|"
               r"ruled|shut|sealed|parked|presented|resolved)\b",
               re.IGNORECASE),
    # The verb first pattern reads its verbs in either case:
    # a verb standing lower case in a parenthetical on the
    # entry own Status line is the same form (Step 17 round 2
    # charge CH-7, S17-ATK2-7-04).
    # CH-60, S17-ATK4-7-02: the Decide and Decides forms the
    # claim scan itself reads stand in this list beside the
    # standing forms.
    # CH-83, S17-ATK5-7-02: the past tense verb first forms
    # Ruled, Decided, and Settled stand in this list beside
    # the present forms, as Closed and Settled stand in the
    # evidence verb first list since CH-60.
    # CH-101, S17-ATK6-7-01: the Closed form and the
    # Resolve forms (Resolve, Resolves, Resolved) stand in
    # this list beside the standing forms, as Closed and
    # Resolve stand in the evidence verb first list since
    # CH-60. No other list member moves.
    # CH-132, S17-ATK7-7-01: the Seal forms (Seal, Seals,
    # Sealed) stand in this list beside the standing
    # forms, the Seal family standing in no ghost list
    # before this cure.
    # CH-167, S17-ATK8-7-03: the Shut forms (Shut, Shuts)
    # stand in this list beside the standing forms, shut
    # standing as a closure word in the predicate lists
    # of this same scan and in the closing prose reading.
    re.compile(r"\b(?:Settle|Settles|Close|Closes|Rule|Rules|"
               r"Decide|Decides|Ruled|Decided|Settled|Closed|"
               r"Resolve|Resolves|Resolved|Seal|Seals|Sealed|"
               r"Shut|Shuts)\s+"
               r"DQ-([0-9]+)\b", re.IGNORECASE),
    re.compile(r"\bquestion for DQ-([0-9]+)\b", re.IGNORECASE),
    # CH-39, S17-ATK3-7-02: the was form on the entry own
    # Status line, DQ-999 was closed, is read by this scan on
    # the same terms as the is form.
    # CH-60, S17-ATK4-7-06: shut stands in the state lists of
    # this scan beside the closed forms, as it stands in the
    # claim scan lists.
    # CH-164, S17-ATK8-7-01: the was pattern carries sealed
    # beside its standing words, as the is pattern of this
    # scan carries it since CH-132.
    # CH-200, S17-ATK9-7-02: the was pattern carries parked
    # and presented beside its standing words, as the has
    # been, stands, and remains and stays patterns of this
    # scan carry both since CH-133, the is pattern carries
    # both since CH-165, and the claim was list has
    # carried both all along.
    re.compile(r"\bDQ-([0-9]+)\s+was\s+(?:decided|closed|settled|"
               r"ruled|shut|sealed|parked|presented)\b",
               re.IGNORECASE),
    # CH-60, S17-ATK4-7-02: this scan reads the Status line
    # forms the prose claim scan reads, the has been, has,
    # got, bare past, and stands forms beside the is and was
    # forms, so a ghost named in any of them takes its Note.
    # CH-133, S17-ATK7-7-02: the has been pattern carries
    # parked and presented beside its standing words, as
    # the claim was list of the claim scan carries both.
    # CH-164, S17-ATK8-7-01: the has been pattern and the
    # got pattern carry sealed beside their standing
    # words, as the is pattern of this scan carries it
    # since CH-132.
    # CH-199, S17-ATK9-7-01: the has been pattern and the
    # got pattern carry resolved beside their standing
    # words, on the same ground as the is pattern above.
    re.compile(r"\bDQ-([0-9]+)\s+has\s+been\s+(?:settled|ruled|"
               r"closed|decided|shut|parked|presented|sealed|"
               r"resolved)\b",
               re.IGNORECASE),
    # CH-201, S17-ATK9-7-03: the has pattern carries
    # sealed beside its standing words, as the was, has
    # been, and got patterns of this scan carry it since
    # CH-164.
    re.compile(r"\bDQ-([0-9]+)\s+has\s+(?:settled|ruled|"
               r"closed|decided|shut|sealed)\b", re.IGNORECASE),
    re.compile(r"\bDQ-([0-9]+)\s+got\s+(?:settled|ruled|"
               r"closed|decided|shut|sealed|resolved)\b",
               re.IGNORECASE),
    # CH-201, S17-ATK9-7-03: the bare past pattern carries
    # the sealed verb beside its standing verbs, as the
    # bare past lists of the claim scan carry it since
    # CH-177.
    re.compile(r"\bDQ-([0-9]+)\s+(?:settled|ruled|closed|"
               r"decided|shut|sealed)(?:\s+(?:yesterday|today|"
               r"already|earlier|recently|now|last\s+week|"
               r"in\s+full)\b"
               r"|\s*\.)", re.IGNORECASE),
    # CH-101, S17-ATK6-7-02: the stands pattern carries
    # the same state list the remains and stays pattern
    # carries, decided included, and the left closed form
    # stands read by the predicate family in its own
    # pattern. No state word beyond the charged forms is
    # added to any list.
    # CH-133, S17-ATK7-7-02: the stands pattern and the
    # remains and stays pattern carry parked and presented
    # beside their standing words, as the claim predicate
    # list of the claim scan carries both since CH-101,
    # and the left pattern carries decided beside closed,
    # a state word every sibling ghost list carries.
    # CH-164, S17-ATK8-7-01: the stands pattern and the
    # remains and stays pattern carry sealed beside their
    # standing words, as the is pattern of this scan
    # carries it since CH-132.
    # CH-165, S17-ATK8-7-02: the left pattern carries shut
    # beside closed and decided, a state word every
    # sibling ghost list carries.
    # CH-199, S17-ATK9-7-01: the stands pattern and the
    # remains and stays pattern below carry resolved
    # beside their standing words, on the same ground as
    # the is pattern above.
    re.compile(r"\bDQ-([0-9]+)\s+stands\s+(?:closed|settled|"
               r"ruled|banked|open|shut|decided|parked|"
               r"presented|sealed|resolved)\b",
               re.IGNORECASE),
    # CH-202, S17-ATK9-7-04: the left pattern carries
    # sealed beside closed, decided, and shut, the word
    # every sibling ghost list gained at CH-164.
    re.compile(r"\bDQ-([0-9]+)\s+left\s+(?:closed|decided|shut|"
               r"sealed)\b",
               re.IGNORECASE),
    # CH-83, S17-ATK5-7-01: the remains and stays forms the
    # prose claim scan reads stand in this scan beside the
    # stands form CH-60 added, on the same Status line
    # surfaces, with the same state list.
    re.compile(r"\bDQ-([0-9]+)\s+(?:remains|stays)\s+"
               r"(?:closed|settled|ruled|banked|open|shut|"
               r"decided|parked|presented|sealed|resolved)\b",
               re.IGNORECASE),
)


_GHOST_FIELD_LABELS = (
    "Ruling text", "Ruling texts", "Settlement", "Ruling outcome",
    "Ruled", "Question as put", "The question that was open")


def _ghost_subject_texts(entry, derived, elements, field_span):
    """The texts the ghost subject scan reads, in one place, so
    every scan that defers to it defers to the same surfaces:
    the decision bearing statements of the entry, its effective
    elements carrying a decided disposition and its recorded
    decision field values, and the heading lines of its level
    4 decision blocks. A block heading is part of the recorded
    decision block form, so a ghost named in it stands on this
    ground (Step 17 round 2 charge CH-7, S17-ATK2-7-05)."""
    texts = []
    for element in derived["effective_elements"]:
        if _effective_disposition(entry, element, elements) \
                in _DECIDED_DISPOSITIONS:
            texts.append((element.statement or "",
                          Span(element.line, element.line)))
    for f in _get(entry, "fields") or []:
        label = str(_get(f, "label", "") or "")
        if label in _GHOST_FIELD_LABELS:
            texts.append((_get(f, "value") or "", field_span))
    for line_number, text in _body_lines(entry):
        if (text or "").strip().startswith("####"):
            texts.append((text or "", Span(line_number, line_number)))
    return texts


def _guarded_ghost_matches(pattern, text):
    """The ghost subject pattern matches of a text, under
    the CH-97 continuation guard: a match whose subject
    token continues in a character of the guard ground,
    inside its digits or after them, is refused whole,
    never read in part as its ASCII head. Every read of
    _GHOST_SUBJECT_PATTERNS stands on this guard (Step 17
    round 6, seat 4 F-2)."""
    text = text or ""
    for match in pattern.finditer(text):
        if _token_continues_at(text, match.end(1)):
            continue
        yield match


def _check5(entry, display_id, derived, elements,
            headed_numbers=None):
    if derived["state"] not in DECIDED_OUTCOMES:
        return []
    if derived["state"] == "Conditional":
        # The PIN-08 Conditional rule: the four tests run only
        # where the underlying state is Ruled, Settled, or Closed
        # as decided. On any other underlying state a recorded non
        # running result stands in place of the four results and no
        # presence failure is raised.
        underlying = derived.get("underlying_state")
        if underlying not in ("Ruled", "Settled", "Closed as decided"):
            derived["presence_results"] = {
                "ran": False,
                "underlying_state": underlying,
                "reason": "the Conditional rule: the underlying "
                          "state is not a decided state",
            }
            return []
    if not any(element.kind in _STATUS_LINE_KINDS
               for element in elements) \
            and not _field_labels(entry):
        # The tail single paragraph form: the entry carries no
        # line start Status line and no field of any form, its
        # whole body standing in one paragraph, and its evidence
        # stands in its heading element and its closing sentence
        # element, which derivation reads under PIN-01 form 4
        # and PIN-05. The four presence tests test for evidence
        # in the recorded label forms and recorded places, forms
        # that dialect does not carry, so the absence of those
        # forms is the normal condition of the dialect under
        # the PIN-13 class rule, not a presence failure, and
        # the tests do not run on it. This is the same shape
        # and the same rule the open entry field tests apply
        # at _check9. An entry carrying a line start Status
        # line or any field label is tested in full below.
        derived["presence_results"] = {
            "ran": False,
            "reason": "the tail single paragraph form: the "
                      "presence evidence forms are not forms "
                      "that dialect carries, under PIN-13",
        }
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
        # Presence is tested on the value, not on the label
        # alone: the verb form counts only where decider
        # matter stands after "by" in the same paragraph, so
        # the bare field line "Ruled by:" with an empty value
        # records no decider (Step 17 round 2 charge CH-6,
        # S17-ATK2-7-01, narrowed at the fix wave 2 closing,
        # defect D1: the first cure reading, an optional
        # single colon and whitespace on the same line, took
        # none of the boundary character forms the Step 16
        # pins record as accepted by this check, and those
        # pins stand again under the narrowed reading).
        decider = _decider_verb_form_present(body) or (
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
        # Presence on the value, as at the decider test above:
        # the label alone, carrying an empty value, records no
        # ruling text (charge CH-6).
        ruling_text = _field_value_present(
            entry, ("Ruling text", "Ruling texts", "Settlement"),
            require_word_character=True)
    if not ruling_text:
        for element in derived["effective_elements"]:
            if (element.kind in ("decision block matter", "closing prose",
                                 "bold lead in paragraph element")
                    and _effective_disposition(entry, element, elements)
                    in _DECIDED_DISPOSITIONS
                    and not _is_decider_line(element.statement or "")):
                if element.kind == "closing prose":
                    # A closing prose element satisfying by a
                    # labelled statement must meet the same
                    # matter condition the labelled paragraph
                    # block below applies: where the statement
                    # carries a Ruled or Settled label, the
                    # matter after the label must stand as
                    # ruling matter under
                    # _labelled_matter_tokens, at least one
                    # content token beyond the label and beyond
                    # attribution alone, attribution read whole
                    # across punctuation inside the word. A
                    # labelled statement carrying nothing, or
                    # nothing beyond a decider attribution,
                    # records no ruling text in any form,
                    # whichever limb classifies it, in plain
                    # text as much as in a fence or a quote
                    # (finding A6-8-2). A closing prose element
                    # carrying no such label satisfies exactly
                    # as it did before, and genuine matter after
                    # the label satisfies on the same evidence.
                    statement = element.statement or ""
                    labelled = re.search(r"(?:Ruled|Settled):", statement)
                    if labelled is not None and not _labelled_matter_tokens(
                            statement[labelled.end():]):
                        continue
                ruling_text = True
                break
    if not ruling_text:
        # The standalone labelled paragraph form: a labelled
        # paragraph element whose statement opens with the Ruled
        # label or the Settled label, the matter under the label
        # standing as the entry's ruling. PIN-08 at brief
        # section 5.3 states the ruling text test over all
        # recorded label forms, and PIN-01 form 2 at brief
        # section 5.2 lists Ruled and Settled among the recorded
        # label forms for an unheaded labelled paragraph; the
        # consolidated restart notes record the compact ruled
        # form at DQ-147 and DQ-148 as one long Ruled paragraph
        # dropping the Ruling text line. No locus enumerates a
        # narrower set for this limb that excludes this form,
        # so a ruling recorded in it satisfies the test. A
        # paragraph opening with the Ruled by label is a decider
        # line, not this form, and a paragraph opening with the
        # Ruling outcome label is an outcome record, not this
        # form: neither satisfies the test here. The matter
        # under the label must itself stand as ruling matter:
        # a paragraph carrying nothing beyond the label, or
        # nothing beyond a decider attribution (the decider
        # name, the grant words of the recorded grant form, and
        # the disposition words themselves), records no ruling
        # text, as fixture F-12 pins for the Ruled by and Ruling
        # outcome labels, and does not satisfy the test here.
        # The attribution is read whole where punctuation
        # inside a word breaks it: a name broken by
        # punctuation is the same attribution in a punctuated
        # spelling, and a name in initials form alone, its
        # surname standing beside the initials, is that
        # attribution standing alone in the same way, so
        # neither records ruling text (finding A6-8-1). That
        # reading stands in _labelled_matter_tokens.
        for element in derived["effective_elements"]:
            statement = (element.statement or "").lstrip()
            if (element.kind == "labelled paragraph element"
                    and _effective_disposition(entry, element, elements)
                    in _DECIDED_DISPOSITIONS
                    and not _is_decider_line(statement)
                    and statement.startswith(("Ruled:", "Settled:"))):
                matter = statement.split(":", 1)[1]
                if _labelled_matter_tokens(matter):
                    ruling_text = True
                    break
    outcome = cross_reference
    if not outcome:
        # Presence on the value, as at the ruling text test:
        # an outcome label carrying an empty value records no
        # outcome (charge CH-6).
        outcome = _field_value_present(
            entry, ("Decision", "Outcome", "Outcome of this decision"),
            prefixes=("Ruling outcome", "Form outcome"),
            require_word_character=True)
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
                # A statement standing in the Ruling outcome
                # labelled form counts on its matter, not on
                # its label alone: where the matter after that
                # label carries no word character, the statement
                # records no outcome on this limb (charge CH-40,
                # on the outcome limb of _check5).
                labelled = re.search(
                    r"Ruling outcome[^:]*:\s*(.*)$", statement,
                    re.DOTALL)
                if (labelled is not None
                        and "Ruled:" not in statement
                        and "Settled:" not in statement
                        and not re.search(r"\w", labelled.group(1))):
                    continue
                outcome = True
                break
    if not outcome:
        for element in derived["effective_elements"]:
            statement = (element.statement or "").lstrip()
            if (element.kind in ("decision block matter", "closing prose")
                    and _effective_disposition(entry, element, elements)
                    in _DECIDED_DISPOSITIONS
                    and not _is_decider_line(statement)
                    and statement.startswith((
                        "Ruled:", "Settled:", "Ruled.", "Settled.",
                        "Closed.", "Closed:"))):
                # The opening disposition word counts on the
                # matter standing after it, not on the word
                # alone: the disposition word by itself carries
                # no outcome content beyond the state the head
                # line already claims, so the matter after the
                # opening must stand as matter under the same
                # test the ruling text limb applies to its
                # labelled forms (Step 17 round 4 charge CH-61,
                # S17-ATK4-7-09).
                opening = re.match(
                    r"(?:Ruled|Settled|Closed)\s*[:.]",
                    statement)
                if opening is not None and not (
                        _labelled_matter_tokens(
                            statement[opening.end():])):
                    continue
                outcome = True
                break
    if not outcome:
        outcome = _field_value_present(
            entry, ("Ruled", "Settlement", "Fill-in"),
            require_word_character=True)
    landing = cross_reference
    if not landing:
        # Presence on the value, as at the tests above, with
        # one collected lines form standing beside it: a
        # landing label carrying an empty value whose record
        # stands as the bullet lines under the label, the
        # corpus form, records a landing; the bare label with
        # nothing under it records none (charge CH-6,
        # S17-ATK2-17-05).
        landing = _field_value_present(
            entry,
            ("Landing", "Landing record", "Lands", "Landed"),
            prefixes=("Where the ruling landed",
                      "Where the settlement landed",
                      "Where the settlement is to land",
                      "Where it landed"),
            require_word_character=True)
    if not landing:
        body_lines = _body_lines(entry)
        for index, (_line, text) in enumerate(body_lines):
            stripped = (text or "").strip()
            if not re.match(
                    r"(?:Where the ruling landed|Where the "
                    r"settlement landed|Where the settlement is "
                    r"to land|Where it landed|Landing|Landing "
                    r"record|Lands|Landed):\s*$", stripped):
                continue
            for _next_line, next_text in body_lines[index + 1:]:
                next_stripped = (next_text or "").strip()
                if not next_stripped:
                    continue
                # The bullet counts on its content, not on its
                # marker alone: the bullet standing as the
                # record under the empty label must carry a
                # word character in its content, as the cured
                # labelled limb above counts a value only
                # where a word character stands in it (Step 17
                # round 4 charge CH-61, S17-ATK4-7-01).
                if (next_stripped.startswith("- ")
                        and re.search(r"\w", next_stripped[2:])):
                    landing = True
                break
            if landing:
                break
    if not landing:
        # A body line carrying the words Where it landed
        # counts on the matter standing after those words,
        # not on the words alone: where nothing carrying a
        # word character stands after them on the line, the
        # line records no landing on this limb, as the cured
        # labelled limb counts a value only where a word
        # character stands in it (Step 17 round 4 charge
        # CH-61, S17-ATK4-7-01).
        for _line, text in _body_lines(entry):
            landed_match = re.search(r"\bWhere it landed\b",
                                     text or "")
            if landed_match is not None and re.search(
                    r"\w", (text or "")[landed_match.end():]):
                landing = True
                break
    if not landing:
        # The Landed colon label form, in the construction the
        # corpus itself carries it: a sentence opening with the
        # label Landed and a colon, naming the place the ruling
        # now stands by an in phrase, and stating that the named
        # place now states the ruled matter, as entry DQ-167 on
        # the corpus pin carries its landing (the warrant
        # paragraph in PLAID.md section 1 now states the
        # discernment form). PIN-08 states the test as no landing
        # record in any form, and no brief or plan locus excludes
        # this form, so a landing recorded in it satisfies the
        # test. A Landed sentence stating only an outcome of the
        # ruling, naming no place that now states it, is not
        # this form and does not satisfy the test here.
        for segment in _sentence_segments(body):
            segment = segment.lstrip()
            if (segment.startswith("Landed:")
                    and re.search(r"\bin\b", segment)
                    and "now states" in segment):
                # The stated matter must engage the ruled
                # matter: at least one content token of the
                # matter the place is stated to now state must
                # stand in the entry's own ruling text. A
                # sentence stating a matter that shares no
                # content token with the ruling states nothing
                # about the ruling, whatever place it names,
                # and does not satisfy the test (finding
                # A4-8-1). On the pin construction the test
                # holds in full: DQ-167 states the discernment
                # form, and discernment stands in its ruling.
                stated = segment.split("now states", 1)[1]
                if _matter_tokens(stated) & _ruling_matter_tokens(
                        entry):
                    landing = True
                    break
    if not landing:
        # The one further recorded form: a landing statement, a
        # statement in the entry body that a named thing landed in,
        # at, or as a named place, or that it is landed, as the
        # DQ-147 family carries its landing inside its Ruled
        # paragraph and the form decision entries carry theirs in
        # their outcome paragraph. Pin 8 and brief section 5.5 rule
        # the test over the recorded forms: a narrative use of the
        # word "landed" naming no place (for example "the change
        # landed somewhere last week"), a later Status line, or a
        # Decision label does not satisfy it.
        landing = bool(
            re.search(r"\blanded (in|at|as)\b", body, re.IGNORECASE)
            or re.search(r"\bis landed\b", body, re.IGNORECASE))
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
    # Two decider lines naming two different deciders in
    # one entry draw a finding naming the conflict of form
    # (round 4 charge CH-63, F4-8-7, under the FLAG 8
    # order: the decider presence reading above stands
    # untouched, and this limb reads the recorded decider
    # lines only). The finding judges no decider authority:
    # it names the two names as written and records that
    # the first stands as the decider of record. The same
    # decider line doubled word for word names one decider
    # twice and takes no finding, the bound form of the
    # charge standing as recorded. Round 5 charge CH-85,
    # F5-8-6, widens the reading of the decider line itself:
    # the verb and the word by stand case aside, and a
    # decider line whose value stands on the next line
    # names its decider from that line. The space before
    # colon form stands outside the colon form still, as
    # the attack paper records it at its observation 1, and
    # the limb names at most the first two distinct names
    # still. Round 7 charge CH-143, F7-8-6, widens the
    # marker reading of the line itself: a numbered list
    # marker or a bullet character stands before the line
    # as a dash, star, or plus bullet or a blockquote
    # marker does, markers standing nested together are
    # read off in turn, a no break space stands inside the
    # verb phrase as a space or a tab does, and a fullwidth
    # colon stands after the word by as the ASCII colon
    # does, with no space before it, as the bound above
    # states for the space form. Round 8 charge CH-182,
    # F8-8-6, widens the reading again: the letter marker
    # widens to six letters, the small black rightwards
    # triangle (U+25B8) joins the marker set, an
    # ideographic space stands inside the verb phrase as
    # a space, a tab, or a no break space does, and a
    # small colon (U+FE55) or a modifier letter colon
    # (U+A789) stands after the word by as the ASCII colon
    # does, with no space before it, as the bound above
    # states for the space form still. Round 9 charge
    # CH-211, F9-8-6, widens the reading again: the letter
    # marker widens to seven letters, the black rightwards
    # triangle (U+25B6) joins the marker set, a letter and
    # digit marker joins the marker readings, a hair space
    # (U+200A) or a thin space (U+2009) stands inside the
    # verb phrase as a space, a tab, a no break space, or
    # an ideographic space does, and a ratio sign (U+2236)
    # stands after the word by as the ASCII colon does,
    # with no space before it, as the bound above states
    # for the space form still.
    decider_names = []
    body_lines = _body_lines(entry)
    for index, (_line, text) in enumerate(body_lines):
        decider_match = re.match(
            r"^\s*(?:(?:[-*+\u2022\u25e6\u2023\u00b7\u25b8\u25b6]|\d+[.)]"
            r"|[A-Za-z]{1,7}[.)]|[A-Za-z]\d+[.)]|>)\s+)*"
            r"(?:Ruled|Settled|Decided)[ \t\u00a0\u3000\u200a\u2009]+by"
            r"(?::|\uff1a|\ufe55|\ua789|\u2236)\s*(.*?)\s*$",
            text or "", re.IGNORECASE)
        if not decider_match:
            continue
        decider_name = decider_match.group(1).rstrip(".")
        if not decider_name and index + 1 < len(body_lines):
            # A decider line whose value stands on the next
            # line names that decider (round 5 charge
            # CH-85, F5-8-6): the next line counts as the
            # value only where it stands alone as a name, a
            # short line carrying no sentence of its own.
            # Round 6 charge CH-103, F6-8-6: blank lines
            # standing between the decider line and its
            # value are read over, so the first non blank
            # line stands as the candidate value.
            follow_index = index + 1
            while follow_index < len(body_lines) and \
                    not (body_lines[follow_index][1] or "").strip():
                follow_index += 1
            following = ""
            if follow_index < len(body_lines):
                following = (
                    body_lines[follow_index][1] or "").strip()
            if re.fullmatch(r"[A-Za-z][A-Za-z .'-]{0,40}",
                            following) and \
                    not re.match(
                        r"(?:Ruled|Settled|Decided|Outcome|"
                        r"Landed|Status|Question|Options|"
                        r"Cost|Blocks)\b", following):
                decider_name = following.rstrip(".")
        if decider_name and \
                decider_name.lower() not in [
                    name.lower() for name in decider_names]:
            # Names are compared case aside, as the file
            # other label readings fold case, so one
            # decider typed in lower case beside the same
            # decider in sentence case names one decider;
            # a second line in lower case naming another
            # decider is a second decider line all the same
            # (round 5 charge CH-85, F5-8-6).
            decider_names.append(decider_name)
    if len(decider_names) >= 2:
        findings.append(_finding(
            5, "Warning", display_id, span, evidence,
            "Two decider lines name two different deciders, "
            "%s and %s: the conflict of form stands "
            "unresolved, the first named decider stands as "
            "the decider of record, and no judgement of "
            "decider authority is made." % (
                decider_names[0], decider_names[1]),
            basis="decision evidence presence: decider conflict"))
    derived["presence_results"] = {
        "ran": True,
        "decider": bool(decider),
        "ruling_text": bool(ruling_text),
        "outcome": bool(outcome),
        "landing_record": bool(landing),
    }
    if headed_numbers is not None:
        # Decision evidence that names a different entry as the
        # subject of the ruling or settlement, where no headed
        # entry carries that number, is not accepted as this
        # entry own evidence in silence: the cited number takes
        # its PD-R7 Note, the Note class brief section 5.4
        # names for a cited DQ number with no heading (Step 17
        # charge S17-ATK7-01). The scan reads the decision
        # bearing statements of the entry: its effective
        # elements and its recorded field values.
        host_number = _entry_number(entry)
        ghost_seen = {}
        texts = _ghost_subject_texts(entry, derived, elements, span)
        for text, text_span in texts:
            for pattern in _GHOST_SUBJECT_PATTERNS:
                for match in _guarded_ghost_matches(pattern, text):
                    number = int(match.group(1))
                    if number == host_number:
                        continue
                    if number in headed_numbers:
                        continue
                    ghost_seen.setdefault(number, (text, text_span))
        for number in sorted(ghost_seen):
            text, text_span = ghost_seen[number]
            findings.append(_pd_r7_finding(
                text, "DQ-%03d" % number, text_span,
                identifier=display_id))
    return findings


_QUESTION_LABELS = ("The question", "Question")
_COST_LABELS = ("Cost of deciding late", "Cost")
_BLOCKS_LABELS = ("What it blocks", "Blocks")

_EFFECTIVELY_OPEN_STATES = ("Open", "Presented", "Parked")


def _check9(entry, display_id, derived):
    # The open entry field tests run on effectively open entries:
    # Open, Presented, and Parked (brief section 5.4). An entry
    # whose Open state stands only under the PIN-04 Shape A
    # exception row is not tested for open fields: its openness is
    # the exception result for an unclassifiable value, not the
    # open form.
    if derived["state"] not in _EFFECTIVELY_OPEN_STATES:
        return []
    if derived.get("shape_a"):
        return []
    elements = list(_get(entry, "status_elements") or [])
    if not any(element.kind in _STATUS_LINE_KINDS
               for element in elements) and not _field_labels(entry):
        # The tail single paragraph form: the entry carries no
        # line start Status line and no field of any form, its
        # whole body standing in one paragraph. The absence of
        # the open form field set is the normal condition of
        # that dialect under PIN-13, not a missing field, so
        # the open entry field tests do not run on it. An open
        # form entry, which carries a head Status line or field
        # labels, is tested in full above this shape.
        return []
    # Presence is tested on the value, not on the label alone:
    # a field whose label stands recorded but whose value
    # carries no matter is missing, on the same Warning as a
    # field with no label at all (Step 17 charge F-17-02).
    missing = []
    if not _field_value_present(
            entry, _QUESTION_LABELS,
            prefixes=("Question as put",)):
        missing.append("its question")
    if not (_has_options_field(entry)
            and _options_value_present(entry)):
        missing.append("its options")
    if not _field_value_present(entry, _COST_LABELS):
        missing.append("its cost of deciding late")
    if not _field_value_present(entry, _BLOCKS_LABELS):
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


# The field families of the open entry field tests, under
# their canonical names, for the repeated and alias paired
# field conflict reading: each family stands as its exact
# labels and, for the Options family, its alias forms.
_FIELD_FAMILIES = (
    ("question", ("The question", "Question")),
    ("options", ("Options",)),
    ("cost of deciding late", ("Cost of deciding late", "Cost")),
    ("blocks", ("What it blocks", "Blocks")),
)


def _family_of_label(label):
    """The canonical field family a recorded label stands
    in, or None: the exact labels of each family, the
    Question as put alias form of the question family, read
    at its word boundary under _question_as_put_label
    (CH-92), and the Options alias forms, read as written."""
    for family, labels in _FIELD_FAMILIES:
        if label in labels:
            return family
    if _question_as_put_label(label or ""):
        return "question"
    if _options_alias_label(label or ""):
        return "options"
    return None


def _render_echo_lines(entry):
    """The body line numbers standing in the render append
    form inside this entry: a rendered per entry block, whose
    run opens with an entry label line, carries the rendered
    row lines (a Date line, a Status as written line, a State
    line, and a Determining element line) in their printed
    order, and then repeats the entry field lines as echoes
    of the rendered entries. Field lines standing after the
    Determining element line of such a run are echoes of the
    tool own output, not field statements of this entry
    (CH-94, disposition item D-5-1).

    CH-112, F-20-6-5, under ruling (i) of section 58: the
    run reading stands on the render append form in its
    printed order, and a blank line standing between any
    two lines of a rendered run stands as no break in the
    run, so the double spaced form a pasted output
    ordinarily takes reads as the same run. A field line
    standing in no rendered run stands as a field statement
    exactly as the CH-94 bound states."""
    echo = set()
    run = []

    def flush():
        if not run:
            return
        texts = [text for _number, text in run]
        if not re.match(r"^DQ-[0-9]+\s*:", texts[0] or ""):
            return
        if not any(text.startswith("Status as written:")
                   for text in texts):
            return
        for index, text in enumerate(texts):
            if text.startswith("Determining element:"):
                for number, _text in run[index + 1:]:
                    echo.add(number)
                return

    for number, text in _body_lines(entry):
        if not (text and text.strip()):
            # A blank line inside a run is no break in it,
            # and a blank line outside a run starts none.
            continue
        if not run and not re.match(r"^DQ-[0-9]+\s*:", text):
            # A run opens at an entry label line; lines
            # standing before one stand in no run.
            continue
        if run and re.match(r"^DQ-[0-9]+\s*:", text) and any(
                item.startswith("Determining element:")
                for _n, item in run):
            # A further entry label line standing after a
            # completed run opens the next rendered block.
            flush()
            run = []
        run.append((number, text))
    flush()
    return echo


def _blocks_value_identity(value):
    """The entry identity a blocks field value names
    where the whole value stands as one entry
    identifier, in one of the identifier forms the
    product reads on this surface: DQ- followed by its
    digits in any width (the form _entry_number reads,
    Step 17 round 7 charge CH-148), or R- followed by
    its digits in any width (Step 17 round 9 charge
    CH-224, seat 6 finding 2), returned as the pair of
    the identifier form and the entry number its digits
    name, or None where the value stands in any other
    form. The form stands in the identity because a DQ
    value and an R value naming the same digits name
    two different entries."""
    match = re.fullmatch(r"(DQ|R)-([0-9]+)", value or "")
    if match is None:
        return None
    return (match.group(1), int(match.group(2)))


def _field_values_contradict(family, first_value, value):
    """Whether two stated values of one field family
    contradict, at the comparison _check9_field_conflicts
    runs: identical strings state no contradiction, and
    at the blocks family two values that each stand as
    one entry identifier naming the one entry identity
    state no contradiction either, in any digit widths
    (Step 17 round 7 charge CH-148, seat 6 Finding 1,
    for the DQ form; Step 17 round 9 charge CH-224,
    seat 6 finding 2, for the R form), the entry
    identity being the identifier identity of this
    surface, as the duplicate reading takes heading
    copies in different widths as one number in each
    form. Every other pair of different strings
    contradicts, as CH-59 stands."""
    if value == first_value:
        return False
    if family == "blocks":
        first_identity = _blocks_value_identity(first_value)
        identity = _blocks_value_identity(value)
        if first_identity is not None and identity is not None:
            return first_identity != identity
    return True


def _check9_field_conflicts(entry, display_id, derived):
    """Two contradictory values for one field of an open
    entry, under a repeated label or under an alias pair,
    take a finding naming the conflict (Step 17 round 4
    charge CH-59, seat 6 Finding 2).

    The selection rule is stated once, at
    _first_family_value, and governs both forms: the first
    occurrence in file order governs. This reading runs on
    the same entries and under the same gates as the open
    entry field tests of _check9, beside them, and it reads
    the recorded fields in file order, skipping any field
    standing on a decision block line, as every entry level
    presence reading does. A family carrying one value,
    however many times that one value stands stated, states
    no contradiction and takes no finding, and a value
    carrying no matter states no value for this reading.
    One finding stands per family per entry, naming the
    governing value and the first value that contradicts
    it, with the labels as written."""
    if derived["state"] not in _EFFECTIVELY_OPEN_STATES:
        return []
    if derived.get("shape_a"):
        return []
    elements = list(_get(entry, "status_elements") or [])
    if not any(element.kind in _STATUS_LINE_KINDS
               for element in elements) and not _field_labels(entry):
        return []
    blocked = _decision_block_line_numbers(entry)
    # CH-94, under ruling (k): a field echo standing in the
    # render append form is not a repeated field. The stated
    # bounds of CH-59 and CH-72 stand restated in the open
    # with this exclusion added: this reading runs on
    # effectively open entries only, values are compared as
    # exact strings, and fields standing on decision block
    # lines are skipped, as the docstring above states.
    echo_lines = _render_echo_lines(entry)
    body_by_line = {line: text for line, text in _body_lines(entry)}
    governing = {}
    conflicts = []
    for field in _get(entry, "fields") or []:
        if _field_line_blocked(entry, field, blocked):
            continue
        if _get(field, "line") in echo_lines:
            continue
        label = str(_get(field, "label", "") or "")
        family = _family_of_label(label)
        if family is None:
            continue
        value = (_get(field, "value") or "").strip()
        if not value:
            continue
        if family not in governing:
            governing[family] = (label, value, field)
            continue
        first_label, first_value, first_field = governing[family]
        if not _field_values_contradict(family, first_value, value):
            continue
        if any(item[0] == family for item in conflicts):
            continue
        conflicts.append(
            (family, first_label, first_value, first_field,
             label, value, field))
    findings = []
    for (family, first_label, first_value, first_field,
            label, value, field) in conflicts:
        first_line = _get(first_field, "line")
        line = _get(field, "line")
        span = None
        if first_line is not None and line is not None:
            span = Span(first_line, line)
        elif first_line is not None:
            span = Span(first_line, first_line)
        evidence_parts = []
        for holder_line in (first_line, line):
            if holder_line is not None and \
                    holder_line in body_by_line:
                evidence_parts.append(body_by_line[holder_line])
        findings.append(_finding(
            9, "Warning", display_id, span,
            " ".join(evidence_parts),
            "This entry carries two contradictory values for "
            "its %s field: \"%s\" under the label %s and "
            "\"%s\" under the label %s. The first occurrence "
            "in file order governs, so the %s field stands "
            "as \"%s\"." % (
                family, first_value, first_label, value, label,
                family, first_value),
            basis="a repeated or alias paired field with "
                  "contradictory values"))
    return findings


def _check10(entry, display_id, derived):
    if derived["state"] != "Parked" and not (
            derived["state"] == "Conditional"
            and derived.get("underlying_state") == "Parked"):
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
    if any((text or "").strip() for _line, text in _body_lines(entry)):
        # The statement names the entry as it stands: an entry
        # carrying body matter in the file, cut off or otherwise
        # unread as a whole, is not described as a heading with
        # no body, and its statement does not send the operator
        # to add a body that already stands there (Step 17
        # charge T-2). The no body form below stands only for
        # an entry whose heading in fact stands with no body.
        statement = (
            "This entry stands unparsed: body matter stands "
            "under its heading in the file, but the entry as a "
            "whole could not be read, so no state can be "
            "determined for it.")
    else:
        statement = (
            "This entry stands unparsed: its heading stands "
            "with no body, so no state can be determined for "
            "it.")
    return _finding(
        12, "Error", display_id, span, heading, statement,
        basis="an unparsed entry, carried under pin 12")


# ---------------------------------------------------------------------
# Unit 3c: whole file checks (checks 1 and 6) and the unmatched
# heading finding
# ---------------------------------------------------------------------

_GAP_NAMING_BOUND = 2000000

# The number of times one run prints the gap naming on the
# validate form: once in the gap finding statement and once in
# its evidence line. The render form does not print the naming.
# The naming bound applies to the run total naming output, the
# naming size multiplied by the number of printings, and not
# only to one naming (Step 17, A21-5).
_GAP_NAMING_PRINTINGS = 2


def _gap_naming_size(numbers):
    """The gap naming size for a set of present entry numbers,
    in characters, in the form Fix 4 used in shell.py: the
    decimal digits of each missing value plus one separator
    character for each value after the first, computed by digit
    count, by subtraction at the powers of ten, without naming
    or listing the missing values, each distinct present value
    removed exactly once at the digit count of its integer
    value (plan Item 9, section 9.6, Step 12 correction)."""
    values = sorted(set(numbers))
    if len(values) < 2:
        return 0
    low = values[0]
    high = values[-1]
    missing_total = (high - low - 1) - (len(values) - 2)
    if missing_total <= 0:
        return 0
    # The cost form of the computation (Step 17, A21-2): the
    # digit length of each present interior value is taken
    # once, before the loop, and the span bounds advance by
    # one multiplication per digit count. No pass of the loop
    # forms a fresh power of ten or a fresh decimal string
    # conversion of a present value, so the cost of reaching
    # the size stays proportional to the work each pass does
    # on the span itself, even where the largest number
    # carries thousands of digits.
    interior_by_digit_count = {}
    for value in values:
        if low < value < high:
            digit_length = len(str(value))
            interior_by_digit_count[digit_length] = \
                interior_by_digit_count.get(digit_length, 0) + 1
    digit_total = 0
    span_low = 0
    span_high = 9
    for digit_count in range(1, len(str(high)) + 1):
        first = max(low + 1, span_low)
        last = min(high - 1, span_high)
        if last >= first:
            count = last - first + 1
            count -= interior_by_digit_count.get(digit_count, 0)
            digit_total += count * digit_count
        span_low = span_high + 1
        span_high = span_high * 10 + 9
    return digit_total + (missing_total - 1)


def _check1(entries, model=None):
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
                1, "Error", _unit_identifier(model),
                Span(lines[0], lines[-1]),
                "heading lines %s" % named,
                "The entry number DQ-%03d is used more than once: "
                "a duplicate entry number, heading lines %s."
                % (number, named),
                basis="an entry number used more than once"))
    # The recognised unnumbered identifier stands under the
    # same rule list text, no entry number used twice: the R-7
    # form carries an identifier instead of a DQ number, and
    # that identifier used by two headed entries takes the
    # same duplicate Error (Step 17 Finding 1 of seat 6).
    r7_holders = [entry for entry in entries
                  if _display_id(entry) == "R-7"
                  and _entry_number(entry) is None]
    if len(r7_holders) > 1:
        lines = sorted(_get(e, "heading_line") for e in r7_holders)
        named = " and ".join(str(n) for n in lines)
        findings.append(_finding(
            1, "Error", _unit_identifier(model),
            Span(lines[0], lines[-1]),
            "heading lines %s" % named,
            "The entry identifier R-7 is used more than once: "
            "a duplicate entry number, heading lines %s." % named,
            basis="an entry number used more than once"))
    numbers = sorted(by_number)
    if numbers:
        gap_size = _gap_naming_size(numbers)
        if gap_size * _GAP_NAMING_PRINTINGS > _GAP_NAMING_BOUND:
            # The gap naming bound (plan Item 9, section 9.6,
            # Step 12 correction): where the size stands over
            # the bound, the numeric gap class does not fire and
            # no part of the missing set is named, in process as
            # on the run surface. The size stands computed by
            # digit count above, without enumerating or joining
            # the missing values, and the refusal signal stands
            # on the validate output in the form the map bound
            # uses, through _gap_refusal_signal.
            return findings
        present = set(numbers)
        missing = [candidate
                   for candidate in range(numbers[0], numbers[-1] + 1)
                   if candidate not in present]
        if missing:
            # The numeric gap class fires once per run, as one
            # Warning naming the full missing set (plan Item 2,
            # section 2.8): the values strictly between the lowest
            # and the highest DQ number present that no headed
            # entry carries.
            heading_line_by_number = {}
            for entry in entries:
                number = _entry_number(entry)
                if number is not None and (
                        number not in heading_line_by_number):
                    heading_line_by_number[number] = _get(
                        entry, "heading_line")
            before = [n for n in numbers if n < missing[0]]
            if before:
                span_line = heading_line_by_number[max(before)]
                span = Span(span_line, span_line)
            else:
                span = Span(0, 0)
            named = ", ".join(str(n) for n in missing)
            findings.append(_finding(
                1, "Warning", _unit_identifier(model, span=span),
                span, named,
                "Entry numbers missing from the sequence form a "
                "gap in the sequence: %s." % named,
                basis="a gap in the entry number sequence"))
    return findings


def _gap_refusal_signal(entries):
    """The validate supplied gap refusal signal, in the form
    the map bound uses: (over_bound, size), the size computed
    by digit count in _gap_naming_size."""
    numbers = []
    for entry in entries:
        number = _entry_number(entry)
        if number is not None:
            numbers.append(number)
    size = _gap_naming_size(numbers)
    return (size * _GAP_NAMING_PRINTINGS > _GAP_NAMING_BOUND, size)


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
            6, "Error",
            _unit_identifier(model, span=Span(min(involved),
                                              max(involved))),
            Span(min(involved), max(involved)),
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
                "label; the entry span is not contiguous.",
                basis="a span fixed by label reattachment"))
    return findings


def _unmatched_heading_findings(model):
    findings = []
    for segment in _get(model, "orphan_segments") or []:
        if not _get(segment, "unmatched_heading"):
            continue
        heading_text = _get(segment, "heading_text") or ""
        findings.append(_finding(
            "PIN-06", "Warning",
            _unit_identifier(model, segment=segment),
            _get(segment, "span"),
            heading_text,
            "The heading %s matches no recognised heading form; no "
            "entry is raised for it." % heading_text,
            basis="a heading matching no recognised heading form"))
    return findings


# ---------------------------------------------------------------------
# Unit 3d: cross entry check (check 8)
# ---------------------------------------------------------------------

# Digit reading in this file stands pinned to ASCII digits
# only (round 2 charge CH-24, finding F-3 of seat 4): a
# citation, claim, or count written in any other decimal
# digit script is not read as a number, in either direction,
# on any runtime. The pin reaches every DQ number pattern
# in this file and the introduction count pattern below, so
# the count claim surface at the F-15-2-1 locus reads ASCII
# digits only as well. The one wider class left standing is
# a rejection guard, not a reading: the citation patterns
# refuse a match where the number continues in any decimal
# digit script, so a mixed script token is never read in
# part as its ASCII head.
# CH-39, seat 4 F-2: a citation token continues not only in a
# decimal digit or a colon but also in a combining mark or a
# format character, inside its digits or after them, and a
# token continuing in any of those is refused whole, never
# read in part. A full stop and punctuation that visibly ends
# a token stand as legitimate terminators, outside the charge.
_TOKEN_CONTINUATION = (
    r"\d:\u0300-\u036f\u1ab0-\u1aff\u1dc0-\u1dff\u20d0-\u20ff"
    r"\ufe00-\ufe0f\ufe20-\ufe2f\u200b-\u200f\u202a-\u202e"
    r"\u2060-\u2064\ufeff\u00ad")
_CITATION_PATTERNS = (
    re.compile(r"\bunder DQ-([0-9]+)(?![" + _TOKEN_CONTINUATION + r"])"),
    re.compile(r"\bunder the DQ-([0-9]+)(?![" + _TOKEN_CONTINUATION + r"])"),
    re.compile(r"\bat DQ-([0-9]+)(?![" + _TOKEN_CONTINUATION + r"])"),
    re.compile(r"\bsee DQ-([0-9]+)(?![" + _TOKEN_CONTINUATION + r"])"),
    re.compile(r"\bper DQ-([0-9]+)(?![" + _TOKEN_CONTINUATION + r"])"),
    re.compile(r"\bcross reference to DQ-([0-9]+)(?![" + _TOKEN_CONTINUATION + r"])"),
)

# CH-73, seat 4 F-1, ruled at record section 38 ruling (g) on
# the class ground of ruling (e): token continuation is
# admitted by Unicode class, not by enumerated list. The
# class boundary pinned here, by Unicode general category:
# a character continues a citation token where its category
# is Nd (decimal number), Mn, Mc, or Me (marks), Cf (format,
# which carries the tag characters), or Cn (unassigned), and
# the colon stands as a pin of the CH-39 reading inside the
# class reading. Every character the CH-39 list names falls
# inside this boundary, so every CH-39 pin stands as a pin
# inside the class reading, and a character of a governed
# class the list does not name (an Arabic letter mark, a
# Hebrew point, a variation selector supplement character,
# a tag character, an unassigned code point) refuses the
# read on the same terms. A full stop and punctuation that
# visibly ends a token stand in no governed class and remain
# legitimate terminators, outside the charge.
_TOKEN_CONTINUATION_CATEGORIES = frozenset(
    ("Nd", "Mn", "Mc", "Me", "Cf", "Cn"))

# CH-82, seat 4 F-1, ruled at record section 52 ruling (a):
# the guard ground is restated once for every surface. A
# character stands in the token continuation ground where it
# presents no visible glyph: the categories Cn, Co, Cf, Cc
# (the governed terminators excepted), Zs, Zl, Zp, Mn, Mc,
# and Me, together with any character, in any category, whose
# Unicode name carries BLANK, FILLER, FILL, or REPLACEMENT.
# That ground stands together with the standing digit ground
# of CH-73 (Nd, and the numeric classes Nl and No beside it,
# which are numeric as Nd is) and its colon pin. A visible
# letter, symbol, or connector punctuation character standing
# between two digits continues the token as well: the token
# as written plainly does not end at the interrupter where a
# digit follows it. Its trailing form, where no digit
# follows, stands at the terminator bound of record section
# 26 flag (f), as the full stop does.
_TOKEN_CONTINUATION_CATEGORIES = frozenset(
    ("Nd", "Nl", "No", "Mn", "Mc", "Me", "Cf", "Cn", "Co",
     "Cc", "Zs", "Zl", "Zp"))

_TOKEN_CONTINUATION_NAME_PARTS = (
    "BLANK", "FILLER", "FILL", "REPLACEMENT")


def _is_token_continuation(character):
    if character == ":":
        return True
    if character in " \t\n\r":
        # The governed terminators excepted, as ruling (a)
        # states: a plain space, tab, or line terminator ends
        # a token in the ordinary way and continues nothing.
        return False
    if unicodedata.category(character) in \
            _TOKEN_CONTINUATION_CATEGORIES:
        return True
    name = unicodedata.name(character, "")
    return any(part in name
               for part in _TOKEN_CONTINUATION_NAME_PARTS)


def _token_continues_at(text, position):
    """Whether a token whose digits end at position in text
    continues past that position, on the CH-82 ground: the
    character at the position stands in the continuation
    ground, or it is a visible letter, symbol, or connector
    punctuation character with a digit standing after it."""
    if position >= len(text):
        return False
    character = text[position]
    if _is_token_continuation(character):
        return True
    # CH-97, seat 4 F-1, as restated at section 58: the
    # digit following ground is classes L, S, and P whole.
    # The full stop stands excepted at the terminator
    # bound of CH-39 and CH-73: a full stop visibly ends a
    # token, and its governed pin form (a Blocks token
    # split by a full stop) still reads in part.
    if character == "." \
            or unicodedata.category(character)[0] not in "LSP":
        return False
    # CH-129, seat 4 F-1: the digit following limb reads
    # the whole continuation run, not one character only.
    # A run of visible characters of classes L, S, and P,
    # with characters of the continuation ground standing
    # inside the run beside them, that ends at a digit of
    # any script leaves the token plainly unended, on the
    # CH-97 ground itself: the digits on both sides of the
    # run are the token own digits. The foreign digit is
    # never read as a number (the CH-24 digit ground stands
    # unmoved); it stands here only as the mark that the
    # token does not end at the interrupter. A full stop
    # or a governed terminator standing inside the run
    # ends the run as it ends a token, so the trailing
    # forms and the full stop pin form stand unmoved.
    index = position
    while index < len(text):
        current = text[index]
        if unicodedata.category(current) in ("Nd", "Nl", "No"):
            return True
        if current == "." or current in " \t\n\r":
            return False
        if unicodedata.category(current)[0] in "LSP" \
                or _is_token_continuation(current):
            index += 1
            continue
        return False
    return False


def _claim_token_continues_at(text, position):
    """Whether a token whose digits end at position in text
    continues past that position for the token plus
    predicate claim scan of check 8, on the CH-131 ground:
    the continuation guard whole, and beside it a hyphen
    class character standing immediately after the digits,
    which marks the token as hyphenated matter and not the
    clean token on this scan, as the parse side guard has
    read it since CH-97. The scan's bridge predicate forms
    consume a hyphen standing in that position as bridge
    text, so the guard states the hyphen limb expressly
    here rather than in the shared guard, whose trailing
    bound stands unmoved for every other surface. The
    bound stands narrowed in one place, stated in the
    open: a colon standing immediately after the digits
    is no continuation for this scan, because the colon
    is the separator of a governed claim form of this
    scan itself (the corpus form naming a token, a colon,
    an assessment, and a bridge predicate state), and the
    cure's first form refused that pinned claim; the
    charged interrupters stand refused as before.
    CH-176, seat 4 F-1 of round 8: the bridge predicate
    forms of this scan (the remains family and the still
    waiting form) consume as bridge text every character
    that is neither a full stop nor a semicolon, so the
    limb beside the guard whole now stands for every
    visible character of classes L, S, and P standing
    immediately after the digits, not the hyphen class
    only: such a character is consumed as bridge text in
    exactly the same way, and the token as written is not
    the clean token on this scan. The full stop and the
    semicolon stand excepted, as the bridge's own form
    excludes them expressly and their forms stand closed
    by the bridge itself, unmoved.
    CH-190, on the determination of the eleven pin guard
    failures of fix wave 8: the possessive form stands
    beside the colon narrowing at the head of this guard.
    Where the character immediately after the digits is
    an apostrophe (U+0027, or U+2019 in the same dress)
    immediately followed by the letter s and then a
    character that is not alphanumeric, or the end of
    the text, the guard returns no continuation on that
    ground: the apostrophe and the s are the token own
    possessive dress, not an interrupter standing
    between the digit head and a bridge predicate, and
    the token reads as the clean token, so its bridge
    predicate claim takes its Note. An apostrophe with
    no s after it, and an apostrophe plus s glued to a
    further alphanumeric character, stand refused under
    the CH-176 limb exactly as before.
    CH-213, seat 4 F-1 of round 9: the possessive
    exception above is decided on its first three
    characters alone, so a possessive dress followed by
    an interrupter and a digit never reaches the CH-129
    run reading, and the token is read in part as its
    digit head. The exception therefore stands only
    where the run reading, applied at the first
    character after the possessive dress, does not read
    a continuation run ending at a digit: where such a
    run stands, the token continues on the CH-129
    ground and is refused whole. An interrupter with no
    digit after it stands where the CH-190 text stands
    it, at its stated bound, and the clean possessive
    forms, the comma boundary form, and the end of text
    form stand unmoved, because the run reading returns
    no continuation on any of them."""
    if position < len(text) and text[position] == ":":
        return False
    if position + 1 < len(text) \
            and text[position] in "'\u2019" \
            and text[position + 1] == "s" \
            and (position + 2 >= len(text)
                 or not text[position + 2].isalnum()) \
            and not _token_continues_at(text, position + 2):
        return False
    if _token_continues_at(text, position):
        return True
    if position < len(text) \
            and text[position] not in ".;" \
            and unicodedata.category(text[position])[0] in "LSP":
        return True
    return False


def _guarded_matches(pattern, text):
    """The matches of a citation pattern over a text, with
    every match whose number continues in a character of a
    governed class refused whole, never read in part. Every
    read of the framed citation patterns and of _DQ_TOKEN_RE
    in this file stands on this guard."""
    for match in pattern.finditer(text):
        end = match.end()
        if end < len(text) and _token_continues_at(text, end):
            continue
        yield match


def _dq_tokens(text):
    return _guarded_matches(_DQ_TOKEN_RE, text)


_CLAIM_PATTERNS = (
    re.compile(r"\bDQ-([0-9]+)\s+is\s+"
               r"(Settled|Ruled|Open|Banked|Closed|Parked|Presented)\b"),
    re.compile(r"\bDQ-([0-9]+)\b[^.;]{0,110}?\b"
               r"(stays|remains|stands|left)\s+"
               r"(banked|open|settled|ruled|closed)\b"),
)

_INTRODUCTION_PATTERN = re.compile(
    r"\b([0-9]+|one|two|three|four|five|six|seven|eight|nine|ten|"
    r"eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|"
    r"eighteen|nineteen|twenty)\s+(entries|questions|items|decisions)\b")


def _check8(model, entries, derived_by_id, derived_lists=None,
            derived_list=None):
    findings = []
    numbers = set()
    for entry in entries:
        number = _entry_number(entry)
        if number is not None:
            numbers.add(number)
    cited = set()

    # The supersession ground stands apart from the citation
    # scan: a number a supersession statement in an entry
    # names as its target is reported on that ground alone,
    # once, under PD-R7 where no headed entry carries it, and
    # the generic citation Warning does not stand over the
    # same statement as a second finding. The covered pairs
    # are the claiming entry and the number, read from the
    # statement lines themselves and from statement runs
    # split across the lines of one paragraph, on the same
    # terms the supersession unit reads them.
    sup_covered = set()
    for sup_index, entry in enumerate(entries):
        source_id = _display_id(entry)
        lines = _body_lines(entry)
        units = []
        for _line_number, text in lines:
            units.append(text)
        runs = []
        run = []
        for line_number, text in lines:
            if text and text.strip() and (
                    not run or line_number == run[-1][0] + 1):
                run.append((line_number, text))
            else:
                if run:
                    runs.append(run)
                run = ([(line_number, text)]
                       if text and text.strip() else [])
        if run:
            runs.append(run)
        for run in runs:
            units.append(" ".join(t for _n, t in run))
        for text in units:
            segments = _sentence_segments(text)
            if not any(_claims_displacement(s) for s in segments):
                continue
            targets = set()
            for segment in segments:
                targets.update(_identifications(segment))
            for token in _dq_tokens(text):
                targets.add("DQ-%03d" % int(token.group(1)))
            for target in targets:
                # CH-109, F-15-6-2: the coverage pair carries
                # the entry making the supersession statement
                # itself, by its enumeration index, not its
                # display identifier alone, so a twin copy
                # citation of the same number stands reported
                # on its own ground.
                sup_covered.add((sup_index, int(target[3:])))

    def scan_citations(lines, source_key, entry_identifier,
                       sup_key=None):
        for line_number, text in lines:
            for pattern in _CITATION_PATTERNS:
                for match in _guarded_matches(pattern, text):
                    number = int(match.group(1))
                    if number in numbers:
                        continue
                    if (sup_key if sup_key is not None
                            else source_key, number) in sup_covered:
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

    # CH-109, F-15-6-1: the framed citation set and its
    # snapshot carry the entry being scanned, by its
    # enumeration index, not its display identifier alone,
    # so one report stands per citing entry in both orders
    # and the same entry suppression stands exactly as
    # CH-90 states it.
    for framed_index, entry in enumerate(entries):
        scan_citations(_body_lines(entry),
                       ("entry", framed_index),
                       _display_id(entry),
                       sup_key=framed_index)
    segments = list(_get(model, "orphan_segments") or [])
    for index, segment in enumerate(segments):
        lines = [(n, t) for n, t in (_get(segment, "lines") or [])]
        if not lines:
            span = _get(segment, "span")
            if span is not None:
                lines = [(span.start_line, _get(segment, "heading_text")
                          or "")]
        scan_citations(lines, ("segment", index),
                       _unit_identifier(model, segment=segment))

    # A plain citation in entry body prose or in the file
    # preamble takes the same PD-R7 report: a cited DQ number
    # with no heading is a finding class of its own, at Note
    # grade, and the framed citation scan above is not the
    # only place a citation can stand (Step 17 charge
    # F-11-05). Numbers already reported on the citation
    # frame scan or on the supersession ground are not
    # reported again here, and a ghost number an entry names
    # as the subject of its own decision evidence, on a
    # decided entry, stands on the _check5 ground and is not
    # reported again here either.
    # CH-90, F-15-5-1: the plain citation suppression and
    # dedup key on the entry being scanned, never on its
    # display identifier. The framed scan reports stand in
    # framed_cited, keyed as that scan keys them, and suppress
    # a plain report of the same number from the same entry
    # as before; the plain dedup stands in plain_seen, keyed
    # by the entry itself, so over duplicate copies each copy
    # citation is judged on its own entry ground: one copy
    # report neither duplicates on its twin line nor silences
    # its twin citation.
    framed_cited = set(cited)
    plain_seen = set()

    def scan_plain_citations(lines, source_key, entry_identifier,
                             skip_numbers=(), entry_index=None):
        for line_number, text in lines:
            if (text or "").startswith("Status:"):
                continue
            for token in _dq_tokens(text or ""):
                number = int(token.group(1))
                if number in numbers or number in skip_numbers:
                    continue
                # CH-109: the coverage and framed suppression
                # tests of an entry scan read the entry being
                # scanned, by its enumeration index, on the
                # same entry bound as the dedup below.
                if entry_index is not None:
                    if (entry_index, number) in sup_covered:
                        continue
                    if (("entry", entry_index), number) \
                            in framed_cited:
                        continue
                    plain_key = (entry_index, number)
                    if plain_key in plain_seen:
                        continue
                    plain_seen.add(plain_key)
                elif (source_key, number) in sup_covered:
                    continue
                else:
                    key = (source_key, number)
                    if key in cited:
                        continue
                    cited.add(key)
                findings.append(_pd_r7_finding(
                    text, "DQ-%03d" % number,
                    Span(line_number, line_number),
                    identifier=entry_identifier))

    for entry_index, entry in enumerate(entries):
        source_id = _display_id(entry)
        skip = set()
        # The derived state this scan defers to is the derived
        # result of this entry, in derived list order, not the
        # result the display identifier map holds, where the
        # last standing copy wins (CH-90).
        if derived_list is not None and \
                entry_index < len(derived_list):
            derived = derived_list[entry_index]
        else:
            derived = derived_by_id.get(source_id)
        if derived is not None and derived.get("state") in \
                DECIDED_OUTCOMES:
            # The suppression stands only for a number the
            # _check5 ghost scan itself reads, on the surfaces
            # _ghost_subject_texts names: a number standing
            # only on a body line the ghost scan does not read
            # is not suppressed here (charge CH-7,
            # S17-ATK2-7-05).
            elements = list(_get(entry, "status_elements") or [])
            for text, _text_span in _ghost_subject_texts(
                    entry, derived, elements, None):
                for pattern in _GHOST_SUBJECT_PATTERNS:
                    for match in _guarded_ghost_matches(
                            pattern, text):
                        skip.add(int(match.group(1)))
        scan_plain_citations(_body_lines(entry), source_id,
                             source_id, skip_numbers=skip,
                             entry_index=entry_index)
        # The entry heading line is a citation surface of the
        # entry: a ghost number named in its title is reported
        # here as it is on a body line (charge CH-7,
        # S17-ATK2-7-06).
        heading_line = _get(entry, "heading_line")
        heading_text = _get(entry, "heading") or ""
        if heading_line is not None and heading_text:
            scan_plain_citations(
                [(heading_line, heading_text)], source_id,
                source_id, skip_numbers=skip,
                entry_index=entry_index)
    header_lines = list(_get(model, "lines") or [])
    for unit in _get(model, "units") or []:
        if _get(unit, "kind") != "file header":
            continue
        unit_span = _get(unit, "span")
        if unit_span is None:
            continue
        lines = [(number, header_lines[number - 1])
                 for number in range(unit_span.start_line,
                                     unit_span.end_line + 1)
                 if 1 <= number <= len(header_lines)]
        scan_plain_citations(
            lines, ("file header", unit_span.start_line),
            _unit_identifier(model, span=unit_span))

    def claim_finding(claiming_id, target_id, quoted, span):
        derived = derived_by_id.get(target_id)
        if derived is None:
            return None

        def state_text_of(one):
            if one["state"] == "Ambiguous":
                return "Ambiguous (%s)" % (one["sub_label"] or "")
            return str(one["state"])

        # Where two standing copies share the target identifier,
        # the Note states the derived state of every copy, in
        # file order: keying the statement on the identifier
        # alone stated the last copy state as the state of the
        # number, contradicting a standing copy in both orders
        # (Step 17 round 2 charge CH-7, seat 6 Finding 2).
        copies = (derived_lists or {}).get(target_id) or []
        # CH-39, seat 6 Finding 1: the Note lists one state for
        # each standing copy in file order, as its own closing
        # words state, at three or more copies as at two. The
        # singular same state form stands where every copy
        # shares one state.
        copy_states = [state_text_of(one) for one in copies]
        if len(copy_states) > 1 and len(set(copy_states)) > 1:
            listed = ", ".join(copy_states[:-1]) + " and " \
                + copy_states[-1]
            statement = (
                "%s records a claim about the state of %s: \"%s\" "
                "The claim is reported as a claim. The derived "
                "states of %s in this run are %s, one for each "
                "standing copy."
                % (claiming_id, target_id, quoted, target_id,
                   listed))
            finding = _finding(
                8, "Note", claiming_id, span, quoted, statement,
                basis="a cross entry state claim, reported as a claim")
            finding.named_entries = [target_id]
            finding.claiming_unit = claiming_id
            return finding
        state_text = state_text_of(derived)
        finding = _finding(
            8, "Note", claiming_id, span, quoted,
            "%s records a claim about the state of %s: \"%s\" The "
            "claim is reported as a claim. The derived state of %s "
            "in this run is %s."
            % (claiming_id, target_id, quoted, target_id, state_text),
            basis="a cross entry state claim, reported as a claim")
        finding.named_entries = [target_id]
        # The claiming entry stands in the declared claiming
        # field of its own, under plan Item 3, section 3.6: the
        # field is claiming_unit, and it carries the claiming
        # unit or the claiming entry in that field alone.
        finding.claiming_unit = claiming_id
        return finding

    seen_claims = set()
    token_pattern = re.compile(r"\bDQ-([0-9]+)\b")
    predicate_patterns = (
        # CH-136, S17-ATK7-7-05: the is list carries sealed
        # in both its cases beside its standing words, no
        # claim pattern of this scan carrying the word
        # sealed in any predicate family before this cure,
        # although sealed stands in the closing prose
        # reading as a closure word.
        # CH-178, S17-ATK8-7-07: the is list carries resolved
        # in both its cases beside its standing words, the
        # Resolve family standing in the ghost verb first
        # list and in the evidence verb first list of this
        # product since CH-60 and CH-101.
        re.compile(r"DQ-[0-9]+\s+is\s+(Settled|Ruled|Open|Banked|Closed|"
                   r"Parked|Presented|Decided|decided|Sealed|"
                   r"sealed|Resolved|resolved)\b"),
        # CH-83, S17-ATK5-7-05: the word decided stands in
        # this predicate state list beside the closed forms,
        # as it stands in the is, was, has been, has, and got
        # lists of this same scan.
        # CH-101, S17-ATK6-7-05: this list carries parked
        # and presented beside its standing words, as the is
        # list of this same scan already carries both as
        # governed states, for the remains parked and stands
        # presented forms only.
        # CH-136, S17-ATK7-7-05: this list carries sealed
        # beside its standing words, for the remains sealed
        # form.
        # CH-203, S17-ATK9-7-05, and CH-205,
        # S17-ATK9-7-07: the remains resolved and stands
        # resolved forms stand in the direct pattern after
        # this list, not in this list. The list form of the
        # cure also read the governed corpus tension forms
        # (a number, intervening prose, then the words
        # stands resolved) and moved the governed PIN
        # totals from Note 13 to Note 15; the charged forms
        # state the verb directly after the number, so the
        # cure stands narrowed to that direct form, and no
        # guard is re-pinned.
        re.compile(r"[^.;]{0,110}?\b(stays|remains|stands|left)\s+"
                   r"(banked|open|settled|ruled|closed|shut|"
                   r"decided|parked|presented|sealed)\b"),
        re.compile(r"DQ-[0-9]+\s+(?:remains|stands)\s+resolved\b",
                   re.IGNORECASE),
        # The still forms of the same claims, in the ordinary
        # phrasings a stale claim takes: a state stated with
        # still standing before it, and the waiting form that
        # states an open claim in words (Step 17 charge
        # F-11-06).
        # CH-101, S17-ATK6-7-05: the is still list carries
        # decided beside its standing words, as its sibling
        # lists of this scan already carry it, for the is
        # still decided form only.
        # CH-136, S17-ATK7-7-05: the is still list carries
        # shut and sealed beside its standing words, as the
        # was, has been, has, and got lists of this scan all
        # carry shut.
        # CH-205, S17-ATK9-7-07: the is still list carries
        # resolved beside its standing words, for the is
        # still resolved form, on the same ground as the
        # remains and stands list above.
        # CH-214, seat 6 finding 1 of round 9: this one
        # pattern also reads the token in its possessive
        # dress (an apostrophe, U+0027 or U+2019, and the
        # letter s) standing immediately before the verb,
        # the one anchored form the bridge families
        # already read in that dress since CH-190: the
        # possessive token standing directly before "is
        # still" takes its claim Note, in both apostrophe
        # dresses. The bound stands stated in the open:
        # the dress stands only where it stands
        # immediately after the digits and immediately
        # before the verb, so the intervening word forms
        # take no Note in either dress, as they take none
        # for the plain token, and no other anchored list
        # of this scan gains the dress by this charge.
        re.compile(r"DQ-[0-9]+(?:'s|\u2019s)?\s+is\s+still\s+"
                   r"(settled|ruled|open|banked|closed|parked|"
                   r"presented|decided|shut|sealed|resolved)\b",
                   re.IGNORECASE),
        re.compile(r"[^.;]{0,110}?\bstill waiting\b"),
        # The past tense forms of the same claims, and the is
        # decided form: the state word list of the first
        # pattern carries decided, and a claim stated with was
        # or has been takes the same Note (Step 17 round 2
        # charge CH-7, S17-ATK2-7-07 and S17-ATK2-7-08).
        # CH-177, S17-ATK8-7-06: the was list carries sealed
        # beside its standing words, as the is family of
        # this scan carries it since CH-136.
        # CH-203, S17-ATK9-7-05, and CH-205,
        # S17-ATK9-7-07: the was list carries resolved
        # beside its standing words, for the was resolved
        # form, on the same ground as the remains and
        # stands list above.
        re.compile(r"DQ-[0-9]+\s+was\s+(settled|ruled|closed|"
                   r"decided|banked|parked|presented|open|shut|"
                   r"sealed|resolved)\b",
                   re.IGNORECASE),
        # CH-136, S17-ATK7-7-05: the has been list carries
        # parked and presented beside its standing words,
        # as the was list and the is still list of this scan
        # carry both.
        # CH-177, S17-ATK8-7-06: the has been list carries
        # sealed beside its standing words, on the same
        # ground as the was list above.
        # CH-205, S17-ATK9-7-07: the has been list carries
        # resolved beside its standing words, for the has
        # been resolved form, on the same ground as the
        # remains and stands list above.
        re.compile(r"DQ-[0-9]+\s+has\s+been\s+(settled|ruled|"
                   r"closed|decided|shut|parked|presented|sealed|"
                   r"resolved)\b",
                   re.IGNORECASE),
        # CH-60, S17-ATK4-7-06: the is shut form, stated in the
        # lower case dress the paper measures, beside the
        # capitalised state list of the first pattern.
        re.compile(r"DQ-[0-9]+\s+is\s+shut\b", re.IGNORECASE),
        # CH-39, S17-ATK3-7-05: the present perfect without
        # been, the got passive, and the bare past forms state
        # the same decided state and take the same Note. The
        # future, progressive, and gerund forms state no such
        # state and stand outside the charge.
        re.compile(r"DQ-[0-9]+\s+has\s+(settled|ruled|"
                   r"closed|decided|shut)\b", re.IGNORECASE),
        # CH-177, S17-ATK8-7-06: the got list carries sealed
        # beside its standing words, on the same ground as
        # the was and has been lists above.
        re.compile(r"DQ-[0-9]+\s+got\s+(settled|ruled|"
                   r"closed|decided|shut|sealed)\b", re.IGNORECASE),
        # The bare past form stands as a sentence closing
        # on a time adverb (DQ-338 closed yesterday.); a
        # ruling reference carrying an object after the verb
        # (DQ-031 ruled that, DQ-029 settled R-92) is a
        # mention of that ruling, not a state claim, and the
        # governed corpus pins stand on that reading.
        # CH-177, S17-ATK8-7-06: the bare past lists carry
        # sealed beside their standing verbs, the sealed
        # verb standing in no bare past form before this
        # cure. A sealed verb carrying an object after it
        # still reads as a ruling mention, not a claim, on
        # the standing bound stated below.
        # CH-205, S17-ATK9-7-07: the bare past lists carry
        # the resolved verb beside their standing verbs,
        # for the bare past resolved form, on the same
        # ground as the remains and stands list above. A
        # resolved verb carrying an object after it still
        # reads as a ruling mention, not a claim, on the
        # standing bound stated below.
        re.compile(r"DQ-[0-9]+\s+(settled|ruled|closed|"
                   r"decided|shut|sealed|resolved)\s+(yesterday|"
                   r"today|already|"
                   r"earlier|recently|now)\b", re.IGNORECASE),
        # CH-60, S17-ATK4-7-03, ruled at record section 38
        # under FLAG 5: the bare past limb also reads the
        # claim where the sentence closes on the week phrase
        # (DQ-425 closed last week.), on the in full form
        # (DQ-427 closed in full.), or on its own full stop
        # (DQ-423 closed.). The bound restated in the open:
        # the CH-39 narrowing recorded LANDED at the fix wave
        # 3 closing trace read the bare past only where the
        # verb closes on a time adverb of the stated set; the
        # bound now stands as the adverb set, the week phrase,
        # the in full form, and the sentence closing full
        # stop, and no wider. A verb carrying an object after
        # it still reads as a ruling mention, not a claim, so
        # the governed corpus pin the narrowing protects
        # (DQ-031 ruled that, DQ-029 settled R-92) stands
        # unmoved on this reading.
        re.compile(r"DQ-[0-9]+\s+(settled|ruled|closed|"
                   r"decided|shut|sealed|resolved)(?:\s+(?:"
                   r"last\s+week|"
                   r"in\s+full)\b|\.(?=\s|$))", re.IGNORECASE),
    )
    # CH-39, S17-ATK3-7-03: the verb first form reads its
    # verbs in either case, as the ghost scan does.
    # CH-60, S17-ATK4-7-05: the past tense verb first forms
    # Closed and Settled stand in the list beside their
    # present forms, and S17-ATK4-7-07: the Resolve verb form
    # stands in the list beside them.
    # CH-83, S17-ATK5-7-03: the past tense verb first forms
    # Ruled and Decided stand in this list beside Closed and
    # Settled, the past forms CH-60 added, as the past forms
    # of two verbs the list itself reads in the present.
    # CH-101, S17-ATK6-7-03: Resolved, the past form of a
    # verb this list reads in the present since CH-60,
    # stands in the list beside its present form.
    # CH-134, S17-ATK7-7-03: the Seal forms (Seal, Seals,
    # Sealed) stand in this list beside the standing forms,
    # the one verb family this list never gained before
    # this cure, although sealed stands in the closing
    # prose reading of this product as a closure word.
    # CH-168, S17-ATK8-7-04: the Shut forms (Shut, Shuts)
    # stand in this list beside the standing forms, the
    # one verb family this list never gained before this
    # cure, although shut stands in the closing prose
    # reading of this product as a closure word and in
    # the predicate lists of this scan itself.
    verb_claim_pattern = re.compile(
        r"\b(?:Settle|Settles|Rule|Rules|Close|Closes|Decide|"
        r"Decides|Closed|Settled|Resolve|Resolves|Resolved|"
        r"Ruled|Decided|Seal|Seals|Sealed|Shut|Shuts)\s+"
        r"DQ-([0-9]+)\b", re.IGNORECASE)
    # CH-60, S17-ATK4-7-07: the Decision on noun form naming
    # a headed entry in decision evidence takes the same
    # Note as a verb first form.
    decision_on_pattern = re.compile(
        r"\bDecision\s+on\s+DQ-([0-9]+)\b", re.IGNORECASE)
    for claiming_index, entry in enumerate(entries):
        claiming_id = _display_id(entry)
        for line_number, text in _body_lines(entry):
            if text.startswith("Status:"):
                continue
            # The verb first form inside a decision evidence
            # line: a ruling text or outcome line that names
            # another entry as the subject of the act, in the
            # form "Settle DQ-238 as follows.", is a claim
            # about that entry and takes the same Note (charge
            # CH-7, S17-ATK2-7-07).
            stripped = (text or "").lstrip()
            label_head = stripped.split(":", 1)[0] if ":" in stripped \
                else ""
            if label_head in _GHOST_FIELD_LABELS:
                # CH-97, seat 4 F-2: the verb first matches
                # of this scan stand under the continuation
                # guard whole, refused where the target token
                # continues in a character of the guard
                # ground, never read in part.
                verb_matches = [
                    match for match in
                    verb_claim_pattern.finditer(text or "")
                    if not _token_continues_at(
                        text or "", match.end(1))]
                # CH-130, seat 4 F-2: the Decision on noun
                # matches of this same scan stand under the
                # same continuation guard, refused whole
                # where the target token continues, never
                # read in part as its digit head.
                verb_matches += [
                    match for match in
                    decision_on_pattern.finditer(text or "")
                    if not _token_continues_at(
                        text or "", match.end(1))]
                for match in verb_matches:
                    target_id = "DQ-%03d" % int(match.group(1))
                    if target_id == claiming_id:
                        continue
                    quoted = (text or "")[match.start():]
                    end = quoted.find(".")
                    if end >= 0:
                        quoted = quoted[:end + 1]
                    quoted = quoted.strip()
                    key = (claiming_index, claiming_id,
                           target_id, quoted)
                    if key in seen_claims:
                        continue
                    seen_claims.add(key)
                    finding = claim_finding(
                        claiming_id, target_id, quoted,
                        Span(line_number, line_number))
                    if finding is not None:
                        findings.append(finding)
            for token in token_pattern.finditer(text):
                target_id = "DQ-%03d" % int(token.group(1))
                if target_id == claiming_id:
                    continue
                # CH-131, seat 4 F-3: this token plus
                # predicate scan stands under the claim
                # continuation guard whole, in this entry
                # body form and in the heading form below,
                # refused where the token continues, never
                # read in part as its digit head.
                if _claim_token_continues_at(text, token.end(1)):
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
                key = (claiming_index, claiming_id,
                       target_id, quoted)
                if key in seen_claims:
                    continue
                seen_claims.add(key)
                finding = claim_finding(
                    claiming_id, target_id, quoted,
                    Span(line_number, line_number))
                if finding is not None:
                    findings.append(finding)
    # CH-60, S17-ATK4-7-08, under the FLAG 5 bound: the
    # claim scan reads a state claim standing in an entry
    # heading title, as the ghost scan already reads that
    # surface for ghost numbers. The reach is the heading
    # title only: no heading line is excluded from any other
    # reading (the CH-7 entry heading citation surface stands
    # untouched above), and no heading line is read for any
    # other scan by this limb.
    for claiming_index, entry in enumerate(entries):
        claiming_id = _display_id(entry)
        heading_line = _get(entry, "heading_line")
        heading_text = _get(entry, "heading") or ""
        if heading_line is None or not heading_text:
            continue
        for token in token_pattern.finditer(heading_text):
            target_id = "DQ-%03d" % int(token.group(1))
            if target_id == claiming_id:
                continue
            # CH-131, seat 4 F-3: the heading form of the
            # same scan stands under the same guard.
            if _claim_token_continues_at(
                    heading_text, token.end(1)):
                continue
            rest = heading_text[token.start():]
            quoted = None
            for predicate in predicate_patterns:
                match = predicate.match(rest)
                if match:
                    quoted = match.group(0)
                    break
            if quoted is None:
                continue
            key = (claiming_index, claiming_id, target_id, quoted)
            if key in seen_claims:
                continue
            seen_claims.add(key)
            finding = claim_finding(
                claiming_id, target_id, quoted,
                Span(heading_line, heading_line))
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
        # No entry heading bounds the section: entry headings
        # stand at level 2 as well as at level 3, under PIN-06,
        # and the entries a section holds stand inside it at
        # either level, so the section runs to the next file
        # level boundary, the next introduction or segment, or
        # to the end of the file. Section membership is what
        # the count compares, and membership does not change
        # when the held entries change their order, as the
        # WV-2 construction at brief section 5.8 holds it
        # invariant.
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
            # The finding stands on the introduction unit
            # itself: a section introduction is a file level
            # unit, and the disagreement is a property of that
            # unit and its section, not of any one entry the
            # section holds, so the unit identifier is its
            # marker on every file, whatever order the held
            # entries stand in.
            findings.append(_finding(
                8, "Warning",
                _unit_identifier(model, span=span), span,
                _get(unit, "heading_text") or "",
                "The section introduction states %d entries; %d "
                "recognised entry headings stand in the section."
                % (claimed, present),
                basis="a section introduction count against its section"))
    return findings


# ---------------------------------------------------------------------
# Unit 3d2: supersession pointers, cycles, chains, and the file
# level claim and cited number reports (PIN-10, PIN-09, PD-R7)
# ---------------------------------------------------------------------

_DQ_TOKEN_RE = re.compile(
    r"\bDQ-([0-9]+)(?![" + _TOKEN_CONTINUATION + r"])\b")

# A supersession target list: one or more DQ targets joined
# by commas, by the word and, or by both together (Step 17
# round 4, CH-64). Before this cure the list form in the
# patterns below joined its targets by the word and alone,
# so a comma separated list of four or more was read only
# at its head and at the and joined tail the patterns could
# reach, and every listed target between the first and the
# last two took no pointer and no Note.
_TARGET_LIST = (
    r"((?:DQ-[0-9]+)(?:(?:\s*,\s*and\s+|\s*,\s*|\s+and\s+)"
    r"DQ-[0-9]+)*)")

_IDENTIFICATION_PATTERNS = (
    re.compile(r"displaces the rulings? at " + _TARGET_LIST),
    re.compile(r"displaces " + _TARGET_LIST + r"\b"),
    re.compile(_TARGET_LIST + r"\s+"
               r"(?:is|are) the superseded entr"),
    re.compile(_TARGET_LIST + r"\s+"
               r"(?:is|are) the entr\w+ it stands in place of"),
    re.compile(r"replaces " + _TARGET_LIST + r"\s+as\b"),
    re.compile(r"supersedes " + _TARGET_LIST + r"\b"),
    re.compile(r"supersedes\b[^.;]{0,120}?\bat "
               + _TARGET_LIST + r"\b"),
)


# The tails of the two list first identification patterns
# (the superseded entries form and the stands in place of
# form), read on their own for the backward list reading in
# _identifications below (Step 17 round 5, CH-75).
_LIST_TAIL_PATTERNS = (
    re.compile(r"\s+(?:is|are) the superseded entr"),
    re.compile(r"\s+(?:is|are) the entr\w+ it stands in place of"),
)

_LIST_TOKEN_RE = re.compile(r"DQ-[0-9]+")

# One separator of the target list form of CH-64, the same
# alternation the list patterns carry.
_LIST_SEPARATOR_RE = re.compile(
    r"(?:\s*,\s*and\s+|\s*,\s*|\s+and\s+)")


# The charged joiner characters of the supersession
# signal reading (the semicolon form of CH-93, the four
# forms of CH-104, and the forms of CH-145 beside the
# colon), named for the no space exception in the
# identification reading below, Step 17 round 8, CH-166.
_CH166_JOINER_CHARACTERS = frozenset(
    ";/|&" + "；" + "+\\>=~" + ";" + "﹔")


# The CH-183 joiner characters that stand one character
# wide (the Arabic semicolon U+061B, the reversed
# semicolon U+204F, the presentation form vertical
# semicolon U+FE14, and the asterisk, at sign, hash, and
# percent forms), named for the CH-222 extension of the
# no space exception in the identification reading
# below, Step 17 round 9, CH-222. The double slash form
# of CH-183 stands two characters wide and is named in
# the reading itself.
_CH222_JOINER_CHARACTERS = frozenset(
    "؛" + "⁏" + "︔" + "*@#%")


def _list_target_stands_at(sentence, position):
    """Whether a list target of the DQ form, its first
    digit included, stands at position in sentence."""
    return (sentence[position:position + 3] == "DQ-"
            and position + 3 < len(sentence)
            and sentence[position + 3] in "0123456789")


def _token_heads_list_at(sentence, end):
    """Whether the token whose digits end at end in
    sentence stands at the head of a target list on a
    form the no space exception of the identification
    reading restores, CH-166 and, beside it, Step 17
    round 9, CH-222: a charged joiner character or a
    CH-183 joiner character standing with no space on
    either side of it, followed at once by the next
    target of its list; the double slash form of
    CH-183, two characters wide, on the same terms and
    read before the one character forms, since the
    slash stands among the charged characters itself;
    or the charged semicolon spaced by an en space
    (U+2002) or a no break space (U+00A0) standing on
    each side of it, the next target following the
    second space character at once. The two space
    characters stand in the continuation ground as
    space characters of the Zs class, where the plain
    space and the tab stand excepted as governed
    terminators, so the semicolon list spaced by one of
    them loses its head as the no space form did.
    Every other continuation stands outside this
    reading and refused whole, exactly as before."""
    if end >= len(sentence):
        return False
    if sentence[end:end + 2] == "//":
        return _list_target_stands_at(sentence, end + 2)
    if sentence[end] in _CH166_JOINER_CHARACTERS \
            or sentence[end] in _CH222_JOINER_CHARACTERS:
        return _list_target_stands_at(sentence, end + 1)
    if sentence[end] in "  ":
        return (sentence[end + 1:end + 2] == ";"
                and sentence[end + 2:end + 3] == sentence[end]
                and _list_target_stands_at(sentence, end + 3))
    return False


def _identifications(sentence):
    found = []

    def collect(list_start, list_text):
        for token in _dq_tokens(list_text):
            # CH-82, seat 4 F-2: the target list reading
            # takes the same continuation guard. A token
            # whose digits continue in the sentence past
            # the list group, in a character of the guard
            # ground, is refused whole, never read in part
            # as its ASCII head.
            if _token_continues_at(
                    sentence,
                    list_start + token.end()):
                # CH-166, seat 9 Finding 1: a token whose
                # continuation is a charged joiner standing
                # with no space on either side of it,
                # followed at once by the next target of
                # its list, is the head of a no space
                # charged joiner list, not a continued
                # token: the run the guard reads is the
                # joiner and the next list target, in the
                # list form the signal reading charges.
                # The head reading its spaced form derives
                # stands restored on that form only. The
                # colon stands outside this exception, as
                # its CH-145 pin states: a colon list head
                # derives no pointer. CH-222, seat 9
                # Finding 1 of round 9: the exception
                # stands extended on the same terms to
                # the CH-183 joiner characters at the no
                # space adjacency and to the charged
                # semicolon spaced by an en space or a
                # no break space on each side, as
                # _token_heads_list_at states them: the
                # head reading its spaced form derives
                # stands restored on those forms only,
                # and no middle pointer derives from any
                # CH-183 list. Every other continuation
                # stands refused whole.
                end = list_start + token.end()
                if not _token_heads_list_at(sentence, end):
                    continue
            found.append((list_start + token.start(),
                          "DQ-%03d" % int(token.group(1))))

    for pattern in (_IDENTIFICATION_PATTERNS[:2]
                    + _IDENTIFICATION_PATTERNS[4:]):
        for match in pattern.finditer(sentence):
            collect(match.start(1), match.group(1))
    # The two list first patterns are not run as searches
    # over the sentence (Step 17 round 5, CH-75): a search
    # tries the list at every suffix of a long list in turn,
    # with full backtracking at each, so one statement
    # naming n targets paid token work in the square of n
    # although the reading is correct at every size. A list
    # first match is fixed by its tail: the list is the
    # maximal run of targets joined by the list separators
    # that ends where the tail begins. The reading therefore
    # finds each tail once and walks the targets of the
    # sentence backwards from it over the separators, in
    # time standing in the length of the list, and the list
    # so read is the list the pattern read, token for token.
    raw_tokens = [(m.start(), m.end())
                  for m in _LIST_TOKEN_RE.finditer(sentence)]
    end_index = {}
    for idx, (_start, end) in enumerate(raw_tokens):
        end_index[end] = idx
    for tail in _LIST_TAIL_PATTERNS:
        for match in tail.finditer(sentence):
            idx = end_index.get(match.start())
            if idx is None:
                continue
            first = idx
            while first > 0:
                gap = sentence[raw_tokens[first - 1][1]:
                               raw_tokens[first][0]]
                if _LIST_SEPARATOR_RE.fullmatch(gap):
                    first -= 1
                else:
                    break
            list_start = raw_tokens[first][0]
            list_end = raw_tokens[idx][1]
            collect(list_start, sentence[list_start:list_end])
    found.sort()
    ordered = []
    seen_ids = set()
    for _pos, entry_id in found:
        if entry_id not in seen_ids:
            seen_ids.add(entry_id)
            ordered.append(entry_id)
    return ordered


_CASE_VARIANT_TOKEN_RE = re.compile(r"\b(?:DQ|Dq|dQ|dq)-([0-9]+)\b")


def _case_variant_identifications(sentence):
    """The entry identifiers a sentence names in a letter case
    variant of the DQ form, normalised to the DQ form. A case
    variant is not an identification: it derives no pointer.
    It is a near miss, a statement that claims displacement and
    names its target in a form the identification patterns do
    not take, and the supersession unit reports it under the
    not recognised treatment."""
    ordered = []
    for match in _CASE_VARIANT_TOKEN_RE.finditer(sentence or ""):
        if match.group(0).startswith("DQ-"):
            continue
        entry_id = "DQ-%03d" % int(match.group(1))
        if entry_id not in ordered:
            ordered.append(entry_id)
    return ordered


_NEAR_MISS_FORM_RES = (
    # The target written with no dash, with an underscore,
    # or with a space in place of the dash.
    re.compile(r"\bDQ([0-9]+)\b"),
    re.compile(r"\bDQ_([0-9]+)\b"),
    re.compile(r"\bDQ ([0-9]+)\b"),
    # The target written with non ASCII decimal digits.
    # The digit class here is the Unicode decimal class,
    # wider than the ASCII class every data reading stands
    # on: this pattern reads no data, it only recognises
    # the near miss form so the silence is told.
    re.compile(r"\bDQ-(\d+)\b"),
)


def _near_miss_identifications(sentence):
    """The entry identifiers a sentence names in a near miss
    form of the DQ identifier, normalised to the DQ form:
    the case variants, and the four forms charged at Step 17
    round 4, CH-65 Finding 3 (no dash, an underscore, a
    space, and non ASCII digits). A near miss derives no
    pointer and widens no data reading: the identification
    patterns above still read ASCII digits only, as FLAG 11
    states. It is reported under the not recognised
    treatment, so a missed pointer stands told from an
    absent one."""
    ordered = _case_variant_identifications(sentence)
    text = sentence or ""
    for pattern in _NEAR_MISS_FORM_RES:
        for match in pattern.finditer(text):
            digits = match.group(1)
            if digits.isascii():
                if match.group(0) == "DQ-" + digits:
                    # The standard form itself, read by the
                    # identification patterns, is no near miss.
                    continue
            else:
                try:
                    digits = str(int(digits))
                except ValueError:
                    continue
            entry_id = "DQ-%03d" % int(digits)
            if entry_id not in ordered:
                ordered.append(entry_id)
    return ordered


_SEMICOLON_LIST_RE = re.compile(
    r"DQ-[0-9]+(?:\s*;\s*DQ-[0-9]+)+")

# The charged joiner list forms of Step 17 round 6,
# CH-104, ruled at record section 58 ruling (h): a target
# list joined by a slash, a pipe, an ampersand, or a
# fullwidth semicolon (U+FF1B). Like the semicolon form,
# these lists are read for the near miss signal only: the
# CH-64 joiner set (commas, the word and, or both) stands
# unmoved and no pointer derives from any charged joiner
# list.
_CHARGED_JOINER_LIST_RES = (
    re.compile(r"DQ-[0-9]+(?:\s*/\s*DQ-[0-9]+)+"),
    re.compile(r"DQ-[0-9]+(?:\s*\|\s*DQ-[0-9]+)+"),
    re.compile(r"DQ-[0-9]+(?:\s*&\s*DQ-[0-9]+)+"),
    re.compile("DQ-[0-9]+(?:\\s*\uFF1B\\s*DQ-[0-9]+)+"),
)

# The joiner silence list forms of Step 17 round 7,
# CH-145, ruled at record section 66 ruling (e): a target
# list joined by a plus, a backslash, a greater than
# sign, a colon, an equals sign, or a tilde, and a list
# joined by a semicolon lookalike, the Greek question
# mark (U+037E) or the small semicolon (U+FE54). Like
# the forms above, these lists are read for the near
# miss signal only, in the CH-104 form of ruling (h) of
# record section 58: the charge is the silence only, no
# pointer derives from any list in this set, and the
# CH-64 joiner set stands unmoved. The colon form
# stands as its finding states it: the colon stands
# inside the clause punctuation the end readings read
# by, so a colon list takes its signal for every target
# no pointer stands for, its head among them, and still
# derives no pointer past the reading it already took.
_CH145_JOINER_LIST_RES = (
    re.compile(r"DQ-[0-9]+(?:\s*\+\s*DQ-[0-9]+)+"),
    re.compile(r"DQ-[0-9]+(?:\s*\\\s*DQ-[0-9]+)+"),
    re.compile(r"DQ-[0-9]+(?:\s*>\s*DQ-[0-9]+)+"),
    re.compile(r"DQ-[0-9]+(?:\s*=\s*DQ-[0-9]+)+"),
    re.compile(r"DQ-[0-9]+(?:\s*~\s*DQ-[0-9]+)+"),
    re.compile("DQ-[0-9]+(?:\\s*\u037E\\s*DQ-[0-9]+)+"),
    re.compile("DQ-[0-9]+(?:\\s*\uFE54\\s*DQ-[0-9]+)+"),
)

# The colon form of CH-145 stands apart from the set
# above for its token reading. The colon is a pin of
# the token continuation guard (CH-39, restated at
# CH-82), so the guarded token reading refuses every
# target of a colon list but its last, the target whose
# digits no colon follows: that refusal is the very
# mechanism that loses the list head reading its
# finding records. The signal reading below therefore
# takes a colon list match on the plain token form,
# inside the match only, where the list pattern itself
# has already fixed that each colon stands between two
# targets of the list. Signal only, as the whole charge
# stands: the guard itself stands unmoved on every
# other surface, and no pointer derives from this form.
_CH145_COLON_LIST_RE = re.compile(
    r"DQ-[0-9]+(?:\s*:\s*DQ-[0-9]+)+")
_CH145_PLAIN_TOKEN_RE = re.compile(r"DQ-([0-9]+)")

# The joiner silence list forms of Step 17 round 8,
# CH-183, ruled at record section 77 ruling (f): a
# target list joined by the Arabic semicolon (U+061B),
# the reversed semicolon (U+204F), or the presentation
# form vertical semicolon (U+FE14), and a list joined
# in list position by an asterisk, an at sign, a hash,
# a percent sign, or a double slash. Like the forms
# above, these lists are read for the near miss signal
# only, on the same bound: the charge is the silence
# only, no derivation is charged, and no pointer
# derives from any list in this set past the end
# readings those lists already took.
_CH183_JOINER_LIST_RES = (
    re.compile("DQ-[0-9]+(?:\\s*؛\\s*DQ-[0-9]+)+"),
    re.compile("DQ-[0-9]+(?:\\s*⁏\\s*DQ-[0-9]+)+"),
    re.compile("DQ-[0-9]+(?:\\s*︔\\s*DQ-[0-9]+)+"),
    re.compile(r"DQ-[0-9]+(?:\s*\*\s*DQ-[0-9]+)+"),
    re.compile(r"DQ-[0-9]+(?:\s*@\s*DQ-[0-9]+)+"),
    re.compile(r"DQ-[0-9]+(?:\s*#\s*DQ-[0-9]+)+"),
    re.compile(r"DQ-[0-9]+(?:\s*%\s*DQ-[0-9]+)+"),
    re.compile(r"DQ-[0-9]+(?:\s*//\s*DQ-[0-9]+)+"),
)


# The joiner silence list forms of Step 17 round 9,
# CH-223, ruled at record section 81 ruling (a): a
# target list joined by a doubled charged joiner (the
# double plus, double pipe, and double ampersand
# forms), by a semicolon lookalike in list position
# (the semicolon with modifier letter colon U+02F8),
# by a comma lookalike (the fullwidth comma U+FF0C or
# the ideographic comma U+3001), or by an underscore.
# Like the forms above, these lists are read for the
# near miss signal only, on the same bound: the charge
# is the silence only, no derivation is charged, and
# no pointer derives from any list in this set past
# the end readings those lists already took. The caret
# form stands outside this set, as its fix wave 8 K7
# pin states: it takes no signal.
_CH223_JOINER_LIST_RES = (
    re.compile(r"DQ-[0-9]+(?:\s*\+\+\s*DQ-[0-9]+)+"),
    re.compile(r"DQ-[0-9]+(?:\s*\|\|\s*DQ-[0-9]+)+"),
    re.compile(r"DQ-[0-9]+(?:\s*&&\s*DQ-[0-9]+)+"),
    re.compile("DQ-[0-9]+(?:\\s*;˸\\s*DQ-[0-9]+)+"),
    re.compile("DQ-[0-9]+(?:\\s*，\\s*DQ-[0-9]+)+"),
    re.compile("DQ-[0-9]+(?:\\s*、\\s*DQ-[0-9]+)+"),
    re.compile(r"DQ-[0-9]+(?:\s*_\s*DQ-[0-9]+)+"),
)


def _semicolon_list_identifications(sentence):
    """The entry identifiers a sentence names in a target
    list joined by semicolons, in list order. The CH-64
    joiner set (commas, the word and, or both) stands
    unmoved and no pointer derives from this form: the
    identification patterns read the head of the list in
    its first clause and its last target in its second, and
    the targets between them took no pointer and no signal.
    Under Step 17 round 5, CH-93, ruled at record section
    52 ruling (i), those middle targets take the near miss
    signal, so this reading names every target the list
    names and the supersession unit reports the ones the
    identification patterns did not reach. Signal only: it
    widens no derivation and moves no other reading."""
    ordered = []
    for match in _SEMICOLON_LIST_RE.finditer(sentence or ""):
        # CH-166, seat 9 Finding 1: the tokens of a list
        # match stand read on the plain token form,
        # inside the match only, on the colon limb form
        # of CH-145. Inside a list match the guarded
        # token reading refuses a token only where the
        # joiner stands with no space on either side of
        # it and the next list target follows the joiner
        # at once, which is the charged no space form
        # itself, so the plain reading inside the match
        # restores exactly that form and no other: the
        # list pattern has already fixed that each
        # joiner stands between two targets of the list,
        # and the guard itself stands unmoved on every
        # other surface.
        for token in _CH145_PLAIN_TOKEN_RE.finditer(
                match.group(0)):
            entry_id = "DQ-%03d" % int(token.group(1))
            if entry_id not in ordered:
                ordered.append(entry_id)
    return ordered


def _charged_list_identifications(sentence):
    """The entry identifiers a sentence names in a target
    list joined by a charged joiner, in list order: the
    semicolon form of CH-93 and the four joiner forms of
    Step 17 round 6, CH-104 (slash, pipe, ampersand, and
    fullwidth semicolon), and the eight joiner silence
    forms of Step 17 round 7, CH-145 (plus, backslash,
    greater than, colon, equals, and tilde, and the
    semicolon lookalikes U+037E and U+FE54), and the
    joiner silence forms of Step 17 round 8, CH-183
    (the Arabic semicolon U+061B, the reversed semicolon
    U+204F, the presentation form vertical semicolon
    U+FE14, and the asterisk, at sign, hash, percent,
    and double slash forms in list position), and the
    joiner silence forms of Step 17 round 9, CH-223
    (the doubled plus, pipe, and ampersand forms, the
    semicolon with modifier letter colon U+02F8, the
    comma lookalikes U+FF0C and U+3001, and the
    underscore form). Signal only,
    on the same bound as the semicolon reading: it widens
    no derivation, the CH-64 joiner set stands unmoved,
    and the supersession unit reports the named targets
    the identification patterns did not reach, subject to
    the signal condition of record section 58 ruling
    (h)."""
    ordered = _semicolon_list_identifications(sentence)
    for pattern in (_CHARGED_JOINER_LIST_RES
                    + _CH145_JOINER_LIST_RES
                    + _CH183_JOINER_LIST_RES
                    + _CH223_JOINER_LIST_RES):
        for match in pattern.finditer(sentence or ""):
            # The plain token form inside the match
            # only, as the semicolon reading above states
            # at CH-166: inside a list match the guarded
            # reading refuses exactly the no space form
            # this charge restores, and no other.
            for token in _CH145_PLAIN_TOKEN_RE.finditer(
                    match.group(0)):
                entry_id = "DQ-%03d" % int(token.group(1))
                if entry_id not in ordered:
                    ordered.append(entry_id)
    for match in _CH145_COLON_LIST_RE.finditer(sentence or ""):
        for token in _CH145_PLAIN_TOKEN_RE.finditer(
                match.group(0)):
            entry_id = "DQ-%03d" % int(token.group(1))
            if entry_id not in ordered:
                ordered.append(entry_id)
    return ordered


def _sentence_segments(text):
    parts = re.split(r"(?<=[.!?])\s+", text or "")
    return [part.strip() for part in parts if part and part.strip()]


def _claims_displacement(sentence):
    lowered = (sentence or "").lower()
    return ("displac" in lowered or "supersed" in lowered
            or "replaces" in lowered
            or "stands in place of" in lowered
            or "no longer stands" in lowered)


def _non_asserting_frame(text):
    """A statement frame that asserts no displacement by the
    entry carrying it, in the two forms charged at Step 17
    round 4, CH-65 Finding 2: a conditional frame (an if
    clause whose consequence stands in the would form), and
    a reported claim the same text withdraws (a draft claim
    standing beside its withdrawal). Such a frame meets no
    limb of the supersession test as an assertion, whatever
    displacement words stand inside the frame."""
    lowered = (text or "").lower()
    if "withdrawn" in lowered and (
            "draft" in lowered or "no displacement" in lowered):
        return True
    for segment in _sentence_segments(text):
        seg = segment.lower()
        if re.search(r"(?<![a-z])if\s", seg) and " would " in seg:
            return True
    return False


def _first_limb(sentence):
    if _non_asserting_frame(sentence):
        return False
    lowered = (sentence or "").lower()
    if "supersed" in lowered and (
            "ruling" in lowered or "ruled" in lowered
            or "figure" in lowered):
        # The supersedes form, PIN-10 first limb in its own
        # words: a statement that this entry supersedes an
        # earlier ruling, or a figure ruled earlier, states
        # displacement in the ruling sense. The two pin
        # instances stand in this form, This supersedes
        # DQ-122 and That supersedes the figure at DQ-168.
        return True
    if "displac" not in lowered:
        return False
    return ("no longer stands" in lowered
            or "displaces the ruling" in lowered
            or "is displaced" in lowered
            or "are displaced" in lowered)


def _pd_r7_finding(sentence, number_id, span, identifier=None):
    return _finding(
        "PD-R7", "Note",
        identifier if identifier is not None else FILE_ID,
        span, sentence,
        "%s is cited, but no headed entry in the file carries "
        "that number: the cited number is reported once under "
        "PD-R7 only." % number_id,
        basis="a cited number with no heading, PD-R7")


_PD_R7_SINGLE_STATEMENT_RE = re.compile(
    r"^(DQ-[0-9]+) is cited, but no headed entry in the file "
    r"carries that number: the cited number is reported once "
    r"under PD-R7 only\.$")


def _combine_pd_r7_statement_notes(findings):
    """Combine the PD-R7 Notes of one statement into one Note.

    The governed PD-R7 form stands whole: a Note quotes the
    line carrying the target reference. Where one statement
    names more than one ghost target, the scans above raise
    one Note per target, each quoting the whole statement, so
    the findings print of one statement grows with the product
    of its target count and its own length (Step 17 round 5,
    seat 5 Finding 1). Under record section 52 ruling (d),
    the Notes for such a statement stand combined here, at
    the findings assembly, into one Note per statement: the
    combined Note stands where the statement's first Note
    stood, on that Note's host and span, quotes the statement
    once as its evidence, and names every ghost target the
    statement carries, in the order the statement names them.
    A statement naming exactly one ghost target keeps its
    standing single Note whole, word for word, and no Note
    is combined across statements: the grouping key is the
    host, the span, and the quoted statement itself.
    """
    groups = {}
    order = []
    for finding in findings:
        if _get(finding, "rule_id") != "PD-R7":
            continue
        statement = _get(finding, "statement") or ""
        match = _PD_R7_SINGLE_STATEMENT_RE.match(statement)
        if match is None:
            continue
        evidence = _get(finding, "evidence")
        if not isinstance(evidence, str):
            continue
        span = _get(finding, "line_span")
        key = (_get(finding, "entry_identifier"),
               _get(span, "start_line") if span is not None else None,
               _get(span, "end_line") if span is not None else None,
               evidence, _get(finding, "basis"))
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append((finding, match.group(1)))
    combined_by_first = {}
    absorbed = set()
    for key in order:
        members = groups[key]
        numbers = []
        for _finding_obj, number_id in members:
            if number_id not in numbers:
                numbers.append(number_id)
        if len(numbers) < 2:
            continue
        evidence = key[3]
        numbers.sort(key=lambda number_id: (
            evidence.find(number_id)
            if evidence.find(number_id) >= 0
            else len(evidence)))
        if len(numbers) == 2:
            joined = "%s and %s" % (numbers[0], numbers[1])
        else:
            joined = ", ".join(numbers[:-1]) + " and " + numbers[-1]
        first = members[0][0]
        combined = _finding(
            "PD-R7", "Note",
            _get(first, "entry_identifier"),
            _get(first, "line_span"), evidence,
            "%s are cited, but no headed entry in the file "
            "carries those numbers: the cited numbers are "
            "reported once under PD-R7 only." % joined,
            basis=_get(first, "basis"))
        combined.named_entries = list(numbers)
        combined_by_first[id(first)] = combined
        for finding_obj, _number_id in members[1:]:
            absorbed.add(id(finding_obj))
    if not combined_by_first:
        return findings
    result = []
    for finding in findings:
        if id(finding) in combined_by_first:
            result.append(combined_by_first[id(finding)])
        elif id(finding) in absorbed:
            continue
        else:
            result.append(finding)
    return result


_MAP_SIZE_BOUND = 2000000
_MAP_SIZE_CAP = 2000001

# The supersession cycle count bound (Step 17 round 3, CH-32):
# the distinct simple cycle inventory of one run stands
# reported in full at or under this bound, and a run whose
# inventory passes it refuses at exit 3 in the standing
# refusal family, naming this bound. The enumeration itself
# stops during enumeration on passing the bound, so the
# refusal arrives before the factorial cost of the full
# inventory is paid, on validate and on render alike. The
# capped measured value is the bound plus one, the count at
# which enumeration stopped.
_CYCLE_COUNT_BOUND = 1000
_CYCLE_COUNT_CAP = 1001
# The supersession cycle enumeration work bound (Step 17
# round 4, CH-52, rulings (b) and (c)): beside the found
# cycle count above, the enumeration carries a work counter,
# the paths explored in the descent, counted once for every
# edge the descent examines from the head of the current
# path. A graph family whose simple paths vastly outnumber
# its cycles (the funnel of seat 5 Finding 1, the wall of
# seat 21 A4-21-1) pays that work before the found count can
# pass its bound, so on the work bound tripping the search
# stops during enumeration and the run refuses at exit 3 in
# the CH-32 form naming the work limit. The bound truncates
# no inventory below the count bound: every governed below
# count bound construction in the round papers completes
# exactly as before, as the K1 paper records with the
# measurements behind this figure. The capped measured
# value is the bound plus one, the count at which
# enumeration stopped.
# The accounting under the counter is restated at Step 17
# round 5, CH-74, under record section 52 ruling (b): a
# simple cycle is charged for its distinct cycle once. As
# first counted, a cycle of n entries paid the sum of its
# suffix lengths, once per start entry of its component,
# so the governed ring of 2,400 entries carrying exactly
# one distinct cycle crossed this bound at about 1,224
# entries and refused whole where rounds 2 to 4 record it
# completing. Under the restated accounting an examination
# that follows a cycle the search has already recorded,
# from a later start of that cycle, is charged to the
# recorded cycle and not counted again; every other
# examination is counted as before, so the funnel and wall
# families of the fix wave 4 K1 tables keep refusing at
# this bound on their re-measured figures, and the figure
# itself stands unmoved.
_CYCLE_WORK_BOUND = 750000
_CYCLE_WORK_CAP = 750001
_MAP_HEAD_LINE = (
    "Supersession concerns form and internal consistency only. "
    "No chain in this map judges which matter governs in "
    "substance.")
_MAP_SEPARATOR = " -> "
_MAP_CYCLE_MARK = " (cycle)"


def _map_print_size(pointers, headed_ids, pointer_cycles):
    """The supersession map print size, in characters, computed
    without enumerating the chains (plan Item 9, section 9.6, the
    map size bound correction and its two corrections).

    The size is the map head line and its line ending, plus, for
    each entry meeting the chain start condition, the continuation
    character total of that entry, plus, for each distinct cycle
    no start chain reaches, the characters of its one closed
    chain and of the branch chains for pointers of its entries
    that form no part of the cycle. Every count and total is held
    capped at the bound plus one, and the computation stops once
    the running total stands over the bound.
    """
    cap = _MAP_SIZE_CAP
    sep = len(_MAP_SEPARATOR)
    mark = len(_MAP_CYCLE_MARK)

    # The reach information this computation reads stands in
    # two places, and neither needs a per entry reach closure.
    # The first is the continuation frame key, which filters an
    # entry's ancestors to the ancestors its own reach set
    # holds. A frame's ancestors stand on a pointer path down
    # to the entry: the root ancestors stand on such a path by
    # the cycle prefix form of the second continuation call
    # site, and each child frame extends the path by the one
    # pointer it follows. An ancestor on that path stands in
    # the reach set of the entry exactly where the entry also
    # reaches the ancestor, which is exactly where the two
    # stand in one strongly connected component of the pointer
    # graph. The components are computed once here, in time
    # standing in the size of the graph, by two walks over it.
    # The second place is the set of entries any start reaches,
    # read further below by one walk that starts from every
    # start at once. The per entry closure form computed and
    # stored a full reach set for every entry, which on a chain
    # stores about N squared over two entry references in
    # total (Step 17, CH-12: seat 5 Finding 1 limb one and
    # A2-21-2).
    graph = {}
    for entry_id in headed_ids:
        if entry_id not in graph:
            graph[entry_id] = list(pointers.get(entry_id, []))
    for source, holders in pointers.items():
        if source not in graph:
            graph[source] = list(holders)
        for holder in holders:
            if holder not in graph:
                graph[holder] = list(pointers.get(holder, []))
    for cycle in pointer_cycles:
        for entry_id in cycle:
            if entry_id not in graph:
                graph[entry_id] = list(pointers.get(entry_id, []))
    reverse_graph = {entry_id: [] for entry_id in graph}
    for source, holders in graph.items():
        for holder in holders:
            reverse_graph[holder].append(source)
    finish_order = []
    walked = set()
    for node in graph:
        if node in walked:
            continue
        walk = [(node, False)]
        while walk:
            current, expanded = walk.pop()
            if expanded:
                finish_order.append(current)
                continue
            if current in walked:
                continue
            walked.add(current)
            walk.append((current, True))
            for nxt in graph[current]:
                if nxt not in walked:
                    walk.append((nxt, False))
    component = {}
    component_count = 0
    for node in reversed(finish_order):
        if node in component:
            continue
        walk = [node]
        component[node] = component_count
        while walk:
            current = walk.pop()
            for prev in reverse_graph[current]:
                if prev not in component:
                    component[prev] = component_count
                    walk.append(prev)
        component_count += 1

    memo = {}

    def continuation(root, root_ancestors):
        # The continuation of an entry, computed with an
        # explicit stack instead of recursion, and with the
        # ancestor filter of each entry read once per frame: the
        # recursive form re-read the reach set once per
        # ancestor at every step of a chain, and its depth
        # stood bounded by the interpreter recursion limit on
        # chains the stated limits admit. The arithmetic is
        # the recursive form's own, term for term: a leaf
        # counts one chain of its own length and a line
        # ending, a pointer back to the entry itself or to an
        # ancestor closes one chain with the cycle mark, and
        # any other pointer contributes its own continuation
        # widened by the entry and the separator once per
        # chain it carries, every total capped at the cap.
        def make_frame(entry, ancestors):
            entry_component = component.get(entry)
            key = (entry, frozenset(
                a for a in ancestors
                if entry_component is not None
                and component.get(a) == entry_component))
            return {
                "entry": entry, "ancestors": ancestors,
                "key": key, "holders": None, "index": 0,
                "total_count": 0, "total_chars": 0,
            }

        def deliver(done_frame, result):
            if not stack:
                return result
            parent = stack[-1]
            sub_count, sub_chars = result
            parent["total_count"] = min(
                cap, parent["total_count"] + sub_count)
            parent["total_chars"] = min(
                cap, parent["total_chars"] + sub_chars
                + sub_count * (len(parent["entry"]) + sep))
            return None

        stack = [make_frame(root, list(root_ancestors))]
        result = None
        while stack:
            frame = stack[-1]
            if frame["key"] in memo:
                stack.pop()
                result = deliver(frame, memo[frame["key"]])
                continue
            if frame["holders"] is None:
                frame["holders"] = pointers.get(frame["entry"], [])
            entry = frame["entry"]
            holders = frame["holders"]
            if not holders:
                leaf = (1, min(cap, len(entry) + 1))
                memo[frame["key"]] = leaf
                stack.pop()
                result = deliver(frame, leaf)
                continue
            pushed = False
            while (frame["index"] < len(holders)
                   and frame["total_chars"] < cap):
                pointer = holders[frame["index"]]
                frame["index"] += 1
                if pointer == entry or pointer in frame["ancestors"]:
                    frame["total_count"] = min(
                        cap, frame["total_count"] + 1)
                    frame["total_chars"] = min(
                        cap, frame["total_chars"] + len(entry)
                        + sep + len(pointer) + mark + 1)
                    continue
                child = make_frame(
                    pointer, frame["ancestors"] + [entry])
                if child["key"] in memo:
                    sub_count, sub_chars = memo[child["key"]]
                    frame["total_count"] = min(
                        cap, frame["total_count"] + sub_count)
                    frame["total_chars"] = min(
                        cap, frame["total_chars"] + sub_chars
                        + sub_count * (len(entry) + sep))
                    continue
                stack.append(child)
                pushed = True
                break
            if pushed:
                continue
            done = (frame["total_count"], frame["total_chars"])
            memo[frame["key"]] = done
            stack.pop()
            result = deliver(frame, done)
        return result

    superseding_set = set()
    for holders in pointers.values():
        superseding_set.update(holders)
    starts = [entry_id for entry_id in headed_ids
              if entry_id in pointers
              and entry_id not in superseding_set]
    total = len(_MAP_HEAD_LINE) + 1
    # The entries any start reaches, read by one walk that
    # starts from every start at once: the same union the per
    # start reach sets gave, read in time standing in the size
    # of the graph.
    reached_entries = set(starts)
    walk_stack = list(starts)
    while walk_stack:
        current = walk_stack.pop()
        for nxt in pointers.get(current, []):
            if nxt not in reached_entries:
                reached_entries.add(nxt)
                walk_stack.append(nxt)
    for start in starts:
        _count, chars = continuation(start, [])
        total = min(cap, total + chars)
        if total >= cap:
            return total
    for cycle in pointer_cycles:
        if any(entry_id in reached_entries for entry_id in cycle):
            continue
        closed_chars = (
            sum(len(entry_id) for entry_id in cycle)
            + len(cycle[0]) + sep * len(cycle) + mark + 1)
        total = min(cap, total + closed_chars)
        if total >= cap:
            return total
        for index, entry_id in enumerate(cycle):
            successor = cycle[(index + 1) % len(cycle)]
            prefix = (sum(len(cycle[i]) for i in range(index + 1))
                      + sep * index)
            for pointer in pointers.get(entry_id, []):
                if pointer == successor:
                    continue
                ancestors = cycle[:index + 1]
                if pointer in ancestors:
                    total = min(cap, total + prefix + sep
                                + len(pointer) + mark + 1)
                else:
                    sub_count, sub_chars = continuation(
                        pointer, ancestors)
                    total = min(cap, total
                                + sub_count * (prefix + sep)
                                + sub_chars)
                if total >= cap:
                    return total
    return total


def _supersession_unit(model, entries, derived_list):
    """Returns (pointers, findings, chains, cycle_records,
    map_over_bound, cycle_over_bound, work_over_bound,
    work_measured).

    pointers maps a superseded entry identifier to the list of
    superseding entry identifiers, in file order of the
    superseding entries. A pointer derives only where a statement
    in an entry that does not carry the unparsed marker meets both
    limbs of the PIN-10 test (plan Item 9, section 9.6).
    """
    headed_ids = []
    for entry in entries:
        display = _display_id(entry)
        if display and display not in headed_ids:
            headed_ids.append(display)
    headed_set = set(headed_ids)
    file_order = {entry_id: index
                  for index, entry_id in enumerate(headed_ids)}
    pointers = {}
    statements = {}
    findings = []
    pd_r7_seen = set()

    def note_pd_r7(sentence, number_id, span):
        key = (number_id, sentence)
        if key in pd_r7_seen:
            return
        pd_r7_seen.add(key)
        findings.append(_pd_r7_finding(
            sentence, number_id, span,
            identifier=_unit_identifier(model, span=span)))

    def note_not_recognised(self_id, named, quote, span):
        finding = _finding(
            "PIN-10", "Note", self_id, span, quote,
            "A supersession statement in this entry is not "
            "recognised: it names %s but does not meet both "
            "limbs of the supersession test, so no pointer "
            "stands for it." % ", ".join(named),
            basis="supersession statement not recognised")
        finding.named_entries = list(named)
        findings.append(finding)

    for entry, derived in zip(entries, derived_list):
        if derived.get("unparsed"):
            continue
        self_id = _display_id(entry)
        if self_id not in headed_set:
            continue
        body = _body_lines(entry)
        handled = set()
        # The charged list signal candidates of this entry
        # (Step 17 round 6, CH-104), each as (target, quote,
        # span) in the order its statement stands. The
        # signal is not emitted at the statement that names
        # it: under record section 58 ruling (h) the signal
        # stands only for a target for which no pointer
        # stands in the same run from this same entry, in
        # either statement order, and a later statement of
        # this entry may still derive that pointer. The
        # candidates are held here and emitted at the end
        # of the entry, filtered on the pointers then
        # standing.
        pending_signal = []
        pending_signal_seen = set()
        for line_number, text in body:
            # The statement unit is the whole line: a statement can
            # state its displacement in one sentence and identify
            # the superseded entry in the next, and the two limbs
            # are read over the statement as a whole.
            segments = _sentence_segments(text)
            claiming = [s for s in segments
                        if _claims_displacement(s)]
            if not claiming:
                continue
            unit = " ".join(segments)
            identified = []
            for segment in segments:
                for target in _identifications(segment):
                    if target not in identified:
                        identified.append(target)
            tokens = []
            for token in _dq_tokens(unit):
                token_id = "DQ-%03d" % int(token.group(1))
                if token_id != self_id and token_id not in tokens:
                    tokens.append(token_id)
            variants = [t for t in
                        _near_miss_identifications(unit)
                        if t != self_id]
            if not identified and not tokens and not variants:
                # A statement identifying no entry takes no Note
                # and gives no pointer: the DQ-161 form.
                continue
            span = Span(line_number, line_number)
            quote = claiming[0]
            if _first_limb(unit) and identified:
                for target in identified:
                    if target == self_id:
                        continue
                    handled.add(target)
                    if target in headed_set:
                        holders = pointers.setdefault(target, [])
                        if self_id not in holders:
                            holders.append(self_id)
                            statements[(target, self_id)] = quote
                    else:
                        note_pd_r7(quote, target, span)
                variant_named = []
                for target in variants:
                    handled.add(target)
                    if target in identified:
                        # A case variant naming of a target the
                        # same statement already identified in the
                        # standard form is the same naming, not a
                        # near miss: the pointer stands for that
                        # target, and no not recognised Note stands
                        # against it (Step 17 round 2, Finding 2
                        # of seat 9).
                        continue
                    if target in headed_set:
                        variant_named.append(target)
                    else:
                        note_pd_r7(quote, target, span)
                if variant_named:
                    note_not_recognised(
                        self_id, variant_named, quote, span)
                # A target list joined by a charged joiner
                # (the semicolon form of Step 17 round 5,
                # CH-93, and the slash, pipe, ampersand, and
                # fullwidth semicolon forms of Step 17 round
                # 6, CH-104, and the joiner silence forms of
                # Step 17 round 7, CH-145): the identification
                # patterns reach the head of the list and its
                # last target, and the targets between them
                # stand named in the statement with no
                # pointer. The colon form of CH-145 reaches
                # its last target only, its head standing
                # inside the clause punctuation, and its
                # signal covers that head on the same terms.
                # They take the near miss signal, a headed
                # middle target in the not recognised Note
                # and a ghost middle target under PD-R7, so
                # a missed pointer stands told from an
                # absent one. Signal only: no pointer
                # derives. Under record section 58 ruling
                # (h) the signal is held as a candidate and
                # emitted at the end of the entry, only for
                # a target for which no pointer stands in
                # the same run from this same entry, in
                # either statement order; the condition
                # governs every signal this charge produces,
                # in either limb.
                for target in _charged_list_identifications(
                        unit):
                    if target == self_id or target in identified:
                        continue
                    handled.add(target)
                    if target not in pending_signal_seen:
                        pending_signal_seen.add(target)
                        pending_signal.append(
                            (target, quote, span))
                continue
            for target in identified:
                if target not in headed_set and target != self_id:
                    handled.add(target)
                    note_pd_r7(quote, target, span)
            for target in tokens:
                # A ghost number named in a claiming statement
                # that the identification patterns do not reach
                # in the identified form still takes its one
                # PD-R7 Note: the seat 7 ghost form, where the
                # statement names its subject as the superseded
                # entry in words and no pattern captures it.
                if target not in headed_set and target not in identified:
                    handled.add(target)
                    note_pd_r7(quote, target, span)
            named = [t for t in (identified or tokens)
                     if t in headed_set and t != self_id]
            for target in variants:
                handled.add(target)
                if target in headed_set:
                    if target not in named:
                        named.append(target)
                else:
                    note_pd_r7(quote, target, span)
            if not named:
                continue
            for target in named:
                handled.add(target)
            note_not_recognised(self_id, named, quote, span)
        # A supersession statement split across two physical
        # lines of one paragraph run: no single line both claims
        # displacement and identifies its target, so the lines
        # above took no pointer and no Note for it. Read over
        # the joined run, the statement claims displacement and
        # names a target no single line handled: it takes the
        # near miss Note, so a missed pointer stands told apart
        # from an absent one.
        runs = []
        run = []
        quote_open = False
        # The standing run quote state is held as a running
        # count of the quote characters of the lines the run
        # already holds, added to line by line as each line is
        # appended and reset when the run closes. The joined
        # text of a run carries one plain space between its
        # lines, which holds no quote character, so the parity
        # of this count is the parity the joined text count
        # gave. Recomputing that count by joining the whole
        # standing run after every appended line paid the sum
        # of the run prefixes in joined characters, a quadratic
        # term in one unbroken run (Step 17 round 3, A3-21-2).
        run_quote_count = 0
        for line_number, text in body:
            if not (text and text.strip()):
                # A blank line does not break the run while a
                # quoted statement stands open across it: a
                # statement split across a paragraph break inside
                # its quotation is read over the joined run on
                # the same terms as one split across the lines
                # of one paragraph (Step 17 round 2, F-11R2-03).
                if run and quote_open:
                    continue
                if run:
                    runs.append(run)
                    run = []
                quote_open = False
                run_quote_count = 0
                continue
            if not run or quote_open or (
                    line_number == run[-1][0] + 1):
                run.append((line_number, text))
                run_quote_count += text.count('"')
            else:
                runs.append(run)
                run = [(line_number, text)]
                run_quote_count = text.count('"')
            quote_open = (run_quote_count % 2 == 1)
        if run:
            runs.append(run)
        for run in runs:
            if len(run) < 2:
                continue
            joined = " ".join(text for _number, text in run)
            segments = _sentence_segments(joined)
            claiming = [s for s in segments
                        if _claims_displacement(s)]
            if not claiming:
                continue
            # The targets of the joined run stand gathered
            # against a set beside the ordered list (Step 17
            # round 6, CH-99, under record section 58 ruling
            # (f) limb two): the list membership reading paid,
            # for each target the run named, a scan of every
            # target the run had already gathered, so the
            # reading cost of one entry grew with the square
            # of its statement count. The set reading gathers
            # the same targets in the same order at a per
            # statement cost independent of the statements the
            # entry already carries, and the findings below
            # stand exact.
            targets = []
            targets_seen = set()
            for segment in segments:
                for target in _identifications(segment):
                    if target not in targets_seen:
                        targets_seen.add(target)
                        targets.append(target)
            for target in _near_miss_identifications(joined):
                if target not in targets_seen:
                    targets_seen.add(target)
                    targets.append(target)
            pending = [t for t in targets
                       if t != self_id and t not in handled]
            if not pending:
                continue
            span = Span(run[0][0], run[0][0])
            quote = claiming[0]
            split_named = []
            for target in pending:
                handled.add(target)
                if target in headed_set:
                    split_named.append(target)
                else:
                    note_pd_r7(quote, target, span)
            if split_named:
                note_not_recognised(
                    self_id, split_named, quote, span)
        # The held charged list signals of this entry, emitted
        # now that every statement of the entry has been read
        # (Step 17 round 6, CH-104, record section 58 ruling
        # (h)): a candidate takes its signal only where no
        # pointer stands for its target from this same entry
        # in the same run, in either statement order. A
        # pointer another entry derives for the same target
        # does not answer this entry's statement and does not
        # suppress the signal. Headed candidates of one
        # statement stand together in one not recognised
        # Note, in list order, on that statement's quote and
        # span; a ghost candidate takes its PD-R7 Note.
        signal_groups = []
        signal_group_index = {}
        for target, quote, span in pending_signal:
            if self_id in pointers.get(target, []):
                continue
            key = (quote, span.start_line, span.end_line)
            if key not in signal_group_index:
                signal_group_index[key] = len(signal_groups)
                signal_groups.append((quote, span, []))
            signal_groups[signal_group_index[key]][2].append(
                target)
        for quote, span, group_targets in signal_groups:
            group_named = []
            for target in group_targets:
                if target in headed_set:
                    group_named.append(target)
                else:
                    note_pd_r7(quote, target, span)
            if group_named:
                note_not_recognised(
                    self_id, group_named, quote, span)

    # Distinct cycles, each reported once as one Warning naming
    # every entry in the cycle in chain order and quoting the
    # statement in each entry. Chain order for the report follows
    # the displacement direction: each entry in the cycle names
    # the next as the entry it displaces. The map chains below
    # follow the pointer direction instead, as the map contract
    # states, so the two cycle orders are computed separately.
    displaces = {}
    for target, holders in pointers.items():
        for holder in holders:
            displaces.setdefault(holder, []).append(target)

    class _CycleBoundExceeded(Exception):
        pass

    class _CycleWorkBoundExceeded(Exception):
        pass

    def find_cycles(relation, seeds):
        # Every distinct simple cycle of the relation stands
        # found, not only the first cycle a walk reaches through
        # each entry: a cycle that shares an entry with an
        # earlier walked branch was lost where the earlier walk
        # had finished the shared entry, so validate and render
        # disagreed on the cycle inventory (Step 17 round 2,
        # Finding 1 of seat 9). The search first takes the
        # strongly connected components of the relation, in the
        # size of the relation: an entry in no component of more
        # than one entry, and carrying no self edge, stands in
        # no cycle, so a chain and any other acyclic shape pay
        # only the component pass, which is the chain cost form
        # charged at M2. Inside a component, the search
        # enumerates the simple cycles through each entry in
        # file order, reading a cycle only from its earliest
        # entry in file order, so each distinct cycle stands
        # found exactly once, in chain order from that entry.
        # The enumeration is bounded during enumeration (Step
        # 17 round 3, CH-32): the moment the found count passes
        # _CYCLE_COUNT_BOUND the search stops and returns the
        # over bound flag beside the partial list, and the
        # caller refuses the run on that flag, so no partial
        # inventory is ever presented as complete and the
        # factorial cost of a dense inventory is never paid in
        # full. The work counter of CH-52 stands beside the
        # found count in the same search: the moment the work
        # passes _CYCLE_WORK_BOUND the search stops in the
        # same form and returns the work flag, so a family
        # whose paths outnumber its cycles refuses on the
        # work bound before the dead path cost is paid in
        # full. Returns (cycles, over_bound, work_over,
        # work_count).
        adjacency = {}
        for seed in seeds:
            if seed not in headed_set:
                continue
            targets = []
            for nxt in relation.get(seed, []):
                if nxt in headed_set and nxt not in targets:
                    targets.append(nxt)
            adjacency[seed] = targets
        for targets in list(adjacency.values()):
            for nxt in targets:
                if nxt not in adjacency:
                    adjacency[nxt] = [
                        t for t in relation.get(nxt, [])
                        if t in headed_set]
        # Strongly connected components, Kosaraju form, both
        # passes iterative.
        visited = set()
        finish_order = []
        for root in adjacency:
            if root in visited:
                continue
            stack = [(root, iter(adjacency[root]))]
            visited.add(root)
            while stack:
                node, edges = stack[-1]
                descended = False
                for nxt in edges:
                    if nxt not in visited:
                        visited.add(nxt)
                        stack.append(
                            (nxt, iter(adjacency[nxt])))
                        descended = True
                        break
                if not descended:
                    finish_order.append(node)
                    stack.pop()
        reversed_adjacency = {node: [] for node in adjacency}
        for node, targets in adjacency.items():
            for nxt in targets:
                reversed_adjacency[nxt].append(node)
        components = []
        assigned = set()
        for root in reversed(finish_order):
            if root in assigned:
                continue
            component = []
            stack = [root]
            assigned.add(root)
            while stack:
                node = stack.pop()
                component.append(node)
                for nxt in reversed_adjacency[node]:
                    if nxt not in assigned:
                        assigned.add(nxt)
                        stack.append(nxt)
            components.append(component)
        found_cycles = []
        seen_keys = set()
        work_counter = [0]
        try:
            cycles_out, over = _enumerate_components(
                components, adjacency, seen_keys, found_cycles,
                work_counter)
            return cycles_out, over, False, work_counter[0]
        except _CycleBoundExceeded:
            return found_cycles, True, False, work_counter[0]
        except _CycleWorkBoundExceeded:
            return found_cycles, False, True, work_counter[0]

    def _enumerate_components(
            components, adjacency, seen_keys, found_cycles,
            work_counter):
        # The recorded cycles of this relation, each as the
        # successor map of its entries in chain order, with
        # an index from each entry to the recorded cycles
        # that carry it. The work accounting of CH-74 reads
        # them: a descent whose path follows one recorded
        # cycle from its start, step for step, is traversing
        # that distinct cycle again, and its examinations
        # are charged to the recorded cycle, which was
        # charged when it was recorded, not counted again.
        cycle_successors = []
        cycle_pure = []
        cycle_block = []
        cycles_by_node = {}

        cycle_fast = {}
        pair_diff = {}
        # The recorded cycles indexed by the one cycle edge
        # each follows at an entry, in record order (Step 17
        # fix wave 9, A9-21-1): the trapped descent reading
        # below reads its candidate cycles from this index,
        # which carries exactly the cycles whose successor
        # at the entry is the edge in question, in the same
        # record order the per entry index carries them, so
        # the first candidate that agrees stands the same
        # cycle under either reading and every tally stands
        # exactly as counted.
        cycle_edge_cycles = {}

        def cycle_fast_data(ci0):
            # The standing data of one recorded cycle for
            # the trapped descent reading below, built once
            # per cycle since a recorded cycle never
            # changes: its entries in chain order with their
            # positions, their file orders, the running sum
            # of their non cycle edge counts over two turns
            # of the order, the file order of every entry
            # successor over two turns with a segment tree
            # of its range minima, and the hazard edges of
            # the cycle (an edge of a cycle entry that is
            # not the cycle edge and that points inside the
            # component), in position order.
            data = cycle_fast.get(ci0)
            if data is not None:
                return data
            succ_map = cycle_successors[ci0]
            first = next(iter(succ_map))
            cyc = [first]
            node = succ_map[first]
            while node != first:
                cyc.append(node)
                node = succ_map[node]
            span = len(cyc)
            pos = {n: i for i, n in enumerate(cyc)}
            fo = [file_order.get(n, 0) for n in cyc]
            degsum = [0] * (2 * span + 1)
            for k in range(2 * span):
                degsum[k + 1] = degsum[k] + len(
                    adjacency[cyc[k % span]]) - 1
            succ_fo = [fo[(k + 1) % span] for k in range(2 * span)]
            size = 1
            while size < 2 * span:
                size *= 2
            tree = [1 << 62] * (2 * size)
            tree[size:size + len(succ_fo)] = succ_fo
            for k in range(size - 1, 0, -1):
                tree[k] = tree[2 * k] if tree[2 * k] <= tree[
                    2 * k + 1] else tree[2 * k + 1]
            hazards = []
            for i, entry in enumerate(cyc):
                for edge in adjacency[entry]:
                    if edge != succ_map[entry] and \
                            edge in members:
                        hazards.append((i, entry, edge))
            hazards.sort()
            data = (cyc, pos, fo, degsum, tree, size, hazards)
            cycle_fast[ci0] = data
            return data

        def first_below(tree, size, lo, hi, threshold):
            # The first index in [lo, hi] whose leaf of the
            # segment tree stands below the threshold, or
            # None where no leaf in the range does: the
            # range stands partitioned into tree nodes in
            # order, the first node whose minimum stands
            # below the threshold is descended to its first
            # such leaf.
            left_nodes = []
            right_nodes = []
            lft, rgt = lo + size, hi + size
            while lft <= rgt:
                if lft % 2 == 1:
                    left_nodes.append(lft)
                    lft += 1
                if rgt % 2 == 0:
                    right_nodes.append(rgt)
                    rgt -= 1
                lft //= 2
                rgt //= 2
            for node in left_nodes + right_nodes[::-1]:
                if tree[node] < threshold:
                    while node < size:
                        node *= 2
                        if tree[node] >= threshold:
                            node += 1
                    return node - size
            return None

        def agrees(ci0, other, cyc, span, base, upto):
            # Whether the recorded cycle other follows the
            # cycle ci0 edge for edge along the segment
            # from base to upto, in the candidate narrowing
            # terms of the walk: the candidates of a descent
            # that has followed ci0 to the entry at upto
            # are the cycles that agreed at every step
            # before it. The difference count stands cached
            # per pair over two turns of the ci0 order.
            if upto <= base:
                return True
            pref = pair_diff.get((ci0, other))
            if pref is None:
                smap = cycle_successors[other]
                pref = [0] * (2 * span + 1)
                for k in range(2 * span):
                    pref[k + 1] = pref[k] + (
                        1 if smap.get(cyc[k % span])
                        != cyc[(k + 1) % span] else 0)
                pair_diff[(ci0, other)] = pref
            return pref[upto] - pref[base] == 0

        def trapped_descent_work(start, carried):
            # The trapped descent reading of Step 17 round
            # 8, CH-187. Where one recorded cycle carrying
            # the start traps the descent from the start on
            # that cycle, the reading tallies the counted
            # examinations the walk would pay, in the walk
            # own terms, without walking the segment: the
            # descent can do nothing but follow the cycle
            # from the start to the first entry whose cycle
            # edge stands refused by file order, that entry
            # standing found on the cycle successor orders;
            # every non cycle edge of an entry on that
            # segment is counted, as the walk counts it,
            # except where a candidate cycle of the descent
            # follows that edge at that entry and has
            # followed the cycle at every step before it.
            # The reading stands only where no hazard edge
            # of the segment stands live from this start:
            # an edge back to the start, which would close
            # a cycle, and an edge that would descend
            # (pointing inside the component at an entry
            # not already on the path and not standing
            # earlier in file order than the start) each
            # end the reading with no tally, and the start
            # is then walked exactly as before. Returns the
            # tally, or None where no carried cycle traps
            # the descent.
            start_order = file_order.get(start, 0)
            carried_set = set(carried)
            for ci0 in carried:
                cyc, pos, fo, degsum, tree, size, hazards = \
                    cycle_fast_data(ci0)
                if start not in pos:
                    continue
                span = len(cyc)
                base = pos[start]
                last = first_below(
                    tree, size, base, base + span - 1,
                    start_order)
                if last is None:
                    continue
                counted = degsum[last + 1] - degsum[base]
                trapped = True
                for at, entry, edge in hazards:
                    here = at if at >= base else at + span
                    if here > last:
                        continue
                    if edge == start:
                        trapped = False
                        break
                    target = pos.get(edge)
                    if target is None:
                        if file_order.get(edge, 0) \
                                >= start_order:
                            trapped = False
                            break
                    else:
                        occ = target if target >= base \
                            else target + span
                        if fo[target] >= start_order \
                                and occ > here:
                            trapped = False
                            break
                    for other in cycle_edge_cycles.get(
                            (entry, edge), ()):
                        if other == ci0 or \
                                other not in carried_set:
                            continue
                        if agrees(ci0, other, cyc, span,
                                  base, here):
                            counted -= 1
                            break
                if trapped:
                    return counted
            return None

        for component in components:
            if len(component) == 1:
                only = component[0]
                if only not in adjacency[only]:
                    continue
            members = set(component)
            ordered = sorted(
                members, key=lambda n: file_order.get(n, 0))
            for start in ordered:
                # The walk bound of Step 17 round 6, CH-113,
                # ruled at record section 58 ruling (a): a
                # recorded cycle is not re-walked from each
                # of its starts. Where a recorded cycle is
                # pure (every entry of the cycle carries the
                # cycle edge as its only edge in this
                # relation), a descent from a later start of
                # that cycle can do nothing but walk the
                # cycle edges in order: it has no branch to
                # take, it counts no examination (every edge
                # it would examine follows the recorded
                # cycle), and it can record no cycle, because
                # the cycle was recorded from its earliest
                # entry, which stands earlier in file order
                # than this start and blocks the walk before
                # it can close. Such a start is not walked at
                # all. Every other start is walked exactly as
                # before, so the inventory, the counts, the
                # refusal figures, and the PIN-10 counts stand
                # exactly as counted.
                # The skip ground widened at Step 17 round 7,
                # CH-152, at its charged bound: a start is
                # also not walked where every recorded cycle
                # carrying it stands clear, a cycle standing
                # clear where no edge of a cycle entry that is
                # not the cycle edge points inside the
                # component at all (its block order, recorded
                # with the cycle, stands at the empty mark):
                # every further edge of the cycle leaves the
                # component, so the walk refuses it on its
                # face, it can neither be descended nor close
                # a cycle, and the one edge that can be
                # descended at every entry of the cycle is the
                # cycle edge itself. A descent from such a
                # start can do nothing but follow the recorded
                # cycle until its earliest entry, which stands
                # earlier in file order, blocks it before it
                # can close, so it counts no examination and
                # can record no cycle, on the CH-113 ground.
                # The bound stands stated in the open: a cycle
                # carrying any further edge inside the
                # component, at whatever file order, stands
                # outside this limb and its starts are walked
                # exactly as before, so the work accounting of
                # the families whose figures stand governed
                # (the wall, detour, funnel, dense, and
                # bipartite forms) stands untouched, their
                # walks paying the examinations they paid.
                # The charged form stands inside the limb: one
                # leaf entry superseding one entry of a ring
                # adds, in the successor relation, one edge
                # from that entry to the leaf, and the leaf
                # stands outside the ring component.
                start_order = file_order.get(start, 0)
                carried = cycles_by_node.get(start, ())
                if any(cycle_pure[ci] for ci in carried):
                    continue
                if carried and all(
                        cycle_block[ci] < 0 for ci in carried):
                    continue
                if carried:
                    # The trapped descent limb of Step 17
                    # round 8, CH-187, beside the CH-113 and
                    # CH-152 limbs above: a recorded cycle
                    # carrying a further edge inside the
                    # component stands outside both limbs, so
                    # on the chorded ring of the charge every
                    # start was walked the long way along the
                    # recorded cycle, at the square of the
                    # ring length in descent steps. Where the
                    # trapped descent reading tallies the
                    # descent from this start in full, the
                    # descent can do nothing but follow that
                    # cycle to its refusal and it records no
                    # cycle, so the start is not walked and
                    # the tally is charged to the work counter
                    # in its place, bound check included, and
                    # the work figure stands exactly as the
                    # walk counted it. Where the reading
                    # tallies nothing, the start is walked
                    # exactly as before, so the walks of the
                    # governed families pay the examinations
                    # they paid.
                    trapped = trapped_descent_work(
                        start, carried)
                    if trapped is not None:
                        if work_counter[0] + trapped > \
                                _CYCLE_WORK_BOUND:
                            work_counter[0] = \
                                _CYCLE_WORK_BOUND + 1
                            raise _CycleWorkBoundExceeded
                        work_counter[0] += trapped
                        continue
                # Simple paths from start through entries of the
                # component that stand at or after start in file
                # order; an edge back to start closes a cycle.
                path = [start]
                in_path = {start}
                work = [(start, iter(adjacency[start]),
                         tuple(cycles_by_node.get(start, ())))]
                while work:
                    node, edges, candidates = work[-1]
                    descended = False
                    for nxt in edges:
                        # The work counter of CH-52, restated
                        # at Step 17 round 5, CH-74: one count
                        # for every edge the descent examines
                        # from the head of the current path,
                        # closing, rejected, and descending
                        # edges alike, since each examination
                        # is work the descent pays whether or
                        # not the edge closes a cycle, except
                        # where the examination follows a cycle
                        # already recorded on this search. A
                        # simple cycle is charged for its
                        # distinct cycle once: the descent from
                        # its earliest entry pays its edges as
                        # it records the cycle, and a descent
                        # from a later entry of the same cycle,
                        # walking the same edges in the same
                        # order, pays nothing again. Work on
                        # paths that follow no recorded cycle,
                        # the dead path work the bound stands
                        # against, is counted per examination
                        # exactly as before.
                        on_recorded = False
                        for ci in candidates:
                            if cycle_successors[ci].get(
                                    node) == nxt:
                                on_recorded = True
                                break
                        if not on_recorded:
                            work_counter[0] += 1
                            if work_counter[0] > _CYCLE_WORK_BOUND:
                                raise _CycleWorkBoundExceeded
                        if nxt == start:
                            key = tuple(path)
                            if key not in seen_keys:
                                seen_keys.add(key)
                                found_cycles.append(list(path))
                                succ = {}
                                for idx, cyc_node in \
                                        enumerate(path):
                                    succ[cyc_node] = path[
                                        (idx + 1) % len(path)]
                                cycle_successors.append(succ)
                                cycle_pure.append(all(
                                    adjacency[cyc_node] == [
                                        succ[cyc_node]]
                                    for cyc_node in path))
                                block_order = -1
                                for cyc_node in path:
                                    for target in adjacency[
                                            cyc_node]:
                                        if target != succ[
                                                cyc_node] and \
                                                target in members:
                                            target_order = \
                                                file_order.get(
                                                    target, 0)
                                            if target_order > \
                                                    block_order:
                                                block_order = \
                                                    target_order
                                cycle_block.append(block_order)
                                ci = len(cycle_successors) - 1
                                for cyc_node in path:
                                    cycles_by_node.setdefault(
                                        cyc_node, []).append(ci)
                                    cycle_edge_cycles.setdefault(
                                        (cyc_node, succ[cyc_node]),
                                        []).append(ci)
                                if len(found_cycles) > \
                                        _CYCLE_COUNT_BOUND:
                                    raise _CycleBoundExceeded
                            continue
                        if nxt not in members or nxt in in_path:
                            continue
                        if file_order.get(nxt, 0) < start_order:
                            continue
                        in_path.add(nxt)
                        path.append(nxt)
                        child = tuple(
                            ci for ci in candidates
                            if cycle_successors[ci].get(
                                node) == nxt)
                        work.append(
                            (nxt, iter(adjacency[nxt]), child))
                        descended = True
                        break
                    if descended:
                        continue
                    work.pop()
                    path.pop()
                    in_path.discard(node)
        found_cycles.sort(
            key=lambda cycle: (
                file_order.get(cycle[0], 0),
                [file_order.get(n, 0) for n in cycle]))
        return found_cycles, False

    (cycles, cycles_over_bound, cycles_work_over_bound,
     cycles_work) = find_cycles(displaces, headed_ids)
    (pointer_cycles, pointer_cycles_over_bound,
     pointer_work_over_bound, pointer_work) = find_cycles(
        pointers, headed_ids)
    cycle_over_bound = cycles_over_bound or \
        pointer_cycles_over_bound
    work_over_bound = cycles_work_over_bound or \
        pointer_work_over_bound
    work_measured = max(cycles_work, pointer_work)
    if cycle_over_bound or work_over_bound:
        # The run refuses on this flag at exit 3 in the standing
        # refusal family, on both subcommands, before any cycle
        # Warning is built and before the map print size is
        # computed: the render refusal is computed during
        # enumeration, never only after it, and no partial
        # inventory stands on the output as a complete one
        # (Step 17 round 3, CH-32; the work bound limb stands
        # at Step 17 round 4, CH-52).
        return (pointers, findings, [], cycles, False,
                cycle_over_bound, work_over_bound, work_measured)
    for cycle in cycles:
        named = ", ".join(cycle)
        quotes = []
        for index, entry_id in enumerate(cycle):
            target = cycle[(index + 1) % len(cycle)]
            sentence = statements.get((target, entry_id))
            if sentence:
                quotes.append(sentence)
        if len(quotes) > 1:
            # The quotes stand in the order their named entries
            # stand in the cycle: the quote naming the first entry
            # of the cycle is the statement of the last entry, so
            # the list rotates by one.
            quotes = quotes[-1:] + quotes[:-1]
        finding = _finding(
            "PIN-10", "Warning", cycle[0], None,
            " ".join(quotes),
            "A supersession cycle stands among %s: the pointers "
            "in the cycle print as derived, and no state or count "
            "changes on account of the cycle." % named,
            basis="supersession cycle")
        finding.named_entries = list(cycle)
        findings.append(finding)

    # The map print size, computed before any chain is built and
    # without enumerating the chains. Where the size stands over
    # the bound, the render model carries no chains in part and
    # shell takes the exit 3 refusal for a render run; a validate
    # run prints no map and takes no refusal (plan Item 9,
    # section 9.6; plan Item 3, section 3.7, field 14).
    map_size = _map_print_size(pointers, headed_ids, pointer_cycles)
    map_over_bound = map_size > _MAP_SIZE_BOUND
    if map_over_bound:
        return (pointers, findings, [], cycles, True, False,
                False, work_measured)

    # Chains for the render map, built from the pointers only.
    superseding_set = set()
    for holders in pointers.values():
        superseding_set.update(holders)

    def extend(chain, pointer):
        # The chains through one pointer, built with an
        # explicit stack of holder iterators instead of
        # recursion, in the recursive form's own order and
        # with its own terms: a pointer already in the chain
        # closes it with the cycle flag, a pointer with no
        # holders ends it, and any other pointer continues
        # through each of its holders in order.
        def step(base, step_pointer):
            new_chain = base + [step_pointer]
            if step_pointer in base:
                return ("leaf", (new_chain, True), None)
            holders = pointers.get(step_pointer, [])
            if not holders:
                return ("leaf", (new_chain, False), None)
            return ("branch", new_chain, holders)

        kind, value, holders = step(chain, pointer)
        if kind == "leaf":
            return [value]
        out = []
        stack = [(value, iter(holders))]
        while stack:
            frame_chain, frame_holders = stack[-1]
            descended = False
            for nxt in frame_holders:
                kind, value, holders = step(frame_chain, nxt)
                if kind == "leaf":
                    out.append(value)
                    continue
                stack.append((value, iter(holders)))
                descended = True
                break
            if descended:
                continue
            stack.pop()
        return out

    chains = []
    starts = [entry_id for entry_id in headed_ids
              if entry_id in pointers
              and entry_id not in superseding_set]
    for start in starts:
        for pointer in pointers[start]:
            chains.extend(extend([start], pointer))
    reached = [set(chain) for chain, _flag in chains]
    for cycle in pointer_cycles:
        cycle_set = set(cycle)
        if any(cycle_set <= chain_set for chain_set in reached):
            continue
        closed = cycle + [cycle[0]]
        chains.append((closed, True))
        for index, entry_id in enumerate(cycle):
            successor = cycle[(index + 1) % len(cycle)]
            for pointer in pointers.get(entry_id, []):
                if pointer == successor:
                    continue
                start_chain = cycle[:index + 1]
                chains.extend(extend(start_chain, pointer))
    return (pointers, findings, chains, cycles, False, False,
            False, work_measured)


_SEGMENT_CLAIM_RE = re.compile(
    r"\bDQ-([0-9]+)\b[^.]{0,90}?\b(was|is|stands|remains|stays|left)\b"
    r"[^.]{0,60}?\b(settled|ruled|closed|banked|open|parked|"
    r"presented)\b", re.IGNORECASE)


def _guarded_segment_claim_matches(text):
    """The segment claim matches of a text, under the CH-82
    continuation guard: a claim whose subject token continues
    in a character of the guard ground, inside its digits or
    after them, is refused whole, never read in part as its
    ASCII head (Step 17 round 5, seat 4 F-2). Every read of
    _SEGMENT_CLAIM_RE stands on this guard."""
    text = text or ""
    for match in _SEGMENT_CLAIM_RE.finditer(text):
        if _token_continues_at(text, match.end(1)):
            continue
        yield match


def _quarantined_heading_line(segment, span):
    """The heading line of a segment whose record carries
    unmatched_heading, or None: the supplementary cure
    quarantines that line, and every scan of the segment
    lines stands outside it, for claims as for citations
    (Step 17 round 2 charge CH-7, seat 4 F-1)."""
    if not _get(segment, "unmatched_heading"):
        return None
    if span is not None:
        line = _get(span, "start_line")
        if line is not None:
            return line
    segment_lines = _get(segment, "lines") or []
    if segment_lines:
        return segment_lines[0][0]
    return None


def _segment_claim_findings(model, entries):
    findings = []
    headed_set = {_display_id(e) for e in entries}
    for segment in _get(model, "orphan_segments") or []:
        span = _get(segment, "span")
        unit_id = _unit_identifier(model, segment=segment)
        quarantined_heading_line = _quarantined_heading_line(
            segment, span)
        claims = list(_get(segment, "claims") or [])
        combined_claimed = {}
        if claims:
            heading_line_text = None
            if quarantined_heading_line is not None:
                for _ln, _lt in (_get(segment, "lines") or []):
                    if _ln == quarantined_heading_line:
                        heading_line_text = _lt
                        break
            for claim in claims:
                statement = _get(claim, "statement") or ""
                if heading_line_text is not None and \
                        statement == heading_line_text:
                    continue
                named = list(_get(claim, "named_entries") or [])
                finding = _finding(
                    "PIN-09", "Note", unit_id, span, statement,
                    "A file level note section records a claim: %s "
                    "The claim is reported as a claim and is never "
                    "applied." % statement,
                    basis="a governing or state claim by a file "
                          "level note section, PIN-09")
                finding.named_entries = named
                finding.claiming_unit = unit_id
                findings.append(finding)
        else:
            seen_claims = set()
            combined_claimed = {}
            for line_number, text in (_get(segment, "lines") or []):
                if quarantined_heading_line is not None and \
                        line_number == quarantined_heading_line:
                    continue
                # The claim Notes of one line stand combined
                # where the line names more than one claim
                # target (Step 17 round 6, CH-98, under record
                # section 58 ruling (f) limb one, the combining
                # ground of section 52 ruling (d) reaching the
                # claim print): the fresh targets of the line
                # are gathered first, under the standing per
                # segment dedup, and the line then takes either
                # its governed single claim Note, word for word
                # as it stood, or one combined Note naming every
                # fresh target in line order and quoting the
                # line once as its evidence.
                fresh = []
                for match in _guarded_segment_claim_matches(text):
                    target = "DQ-%03d" % int(match.group(1))
                    if target in seen_claims:
                        continue
                    seen_claims.add(target)
                    fresh.append((target, match.group(0)))
                if len(fresh) == 1:
                    target, quoted = fresh[0]
                    finding = _finding(
                        "PIN-09", "Note", unit_id,
                        Span(line_number, line_number), text,
                        "A file level note section records a claim "
                        "about %s: \"%s\" The claim is reported as "
                        "a claim and is never applied."
                        % (target, quoted),
                        basis="a governing or state claim by a "
                              "file level note section, PIN-09")
                    finding.named_entries = [target]
                    finding.claiming_unit = unit_id
                    findings.append(finding)
                elif len(fresh) >= 2:
                    names = [target for target, _quoted in fresh]
                    combined_claimed[line_number] = set(names)
                    if len(names) == 2:
                        joined = "%s and %s" % (names[0], names[1])
                    else:
                        joined = ", ".join(names[:-1]) + \
                            " and " + names[-1]
                    finding = _finding(
                        "PIN-09", "Note", unit_id,
                        Span(line_number, line_number), text,
                        "A file level note section records claims "
                        "about %s: \"%s\" The claims are reported "
                        "as claims and are never applied."
                        % (joined, text),
                        basis="a governing or state claim by a "
                              "file level note section, PIN-09")
                    finding.named_entries = names
                    finding.claiming_unit = unit_id
                    findings.append(finding)
        seen_cited = set()
        for line_number, text in (_get(segment, "lines") or []):
            if quarantined_heading_line is not None and \
                    line_number == quarantined_heading_line:
                continue
            for token in _dq_tokens(text or ""):
                target = "DQ-%03d" % int(token.group(1))
                if target in headed_set or target in seen_cited:
                    continue
                # A target a combined claim Note of this same
                # line already names stands reported on that
                # line, in the combined Note that quotes the
                # line once (CH-98): the cited scan of the same
                # line does not report the same naming a second
                # time under PD-R7. A line carrying one claim
                # keeps its standing form whole, and its cited
                # Note stands beside its claim Note exactly as
                # governed (TG-S5-03), and a target cited on a
                # line that does not claim it stands reported
                # on that line as before.
                if target in combined_claimed.get(line_number, ()):
                    continue
                seen_cited.add(target)
                findings.append(_pd_r7_finding(
                    text, target, Span(line_number, line_number),
                    identifier=unit_id))
    return findings


# ---------------------------------------------------------------------
# Unit 3e: census
# ---------------------------------------------------------------------

def _head_element(entry):
    for element in _get(entry, "status_elements") or []:
        if element.kind == "line start Status line":
            return element
    return None


_CLASS_RULE_STATEMENTS = {
    "Banked head over a decided body": (
        "An entry whose head line gives Banked and whose derived "
        "state is a decided state or the Ambiguous reporting form "
        "stands in this class."),
    "Non header status value on a decided entry": (
        "A decided entry carrying a status value that stands "
        "outside its head line, in an embedded or variant "
        "occurrence or in a later line, stands in this class."),
    "Missing options block on a decided entry": (
        "A decided entry carrying no options field in any recorded "
        "form stands in this class."),
    "Missing ruling date on a decided entry": (
        "A decided entry carrying no recorded date stands in this "
        "class."),
    "Non numeric filing of a decided entry in the Ruled Record": (
        "A decided entry in the Ruled Record section whose entry "
        "number stands out of numeric order against its neighbours "
        "in that section stands in this class."),
    "Missing Owner line in a tail form entry": (
        "A decided entry in the tail section carrying neither an "
        "owner line nor the open entry fields stands in this "
        "class."),
    "Decided entry missing its question label or Cost field": (
        "A decided entry in open form, outside the Ruled Record, "
        "that carries one of its question label or its Cost field "
        "and not the other stands in this class."),
    "Open form fields carried by a decided entry in the Ruled "
    "Record": (
        "A decided entry in the Ruled Record section carrying an "
        "open form field, its question, its cost of deciding late, "
        "or its blocks field, stands in this class."),
    "Unclassified status values": (
        "An entry carrying a status element whose value the "
        "vocabulary does not classify stands in this class."),
    "Banked head evidence group: later Status line in the body": (
        "A Banked head entry carrying a later Status line in its "
        "body stands in this group, whatever else its body "
        "carries, under the precedence at plan Item 3, section "
        "3.8."),
    "Banked head evidence group: level 4 decision block only": (
        "A Banked head entry with no later Status line in its "
        "body and with a level 4 decision block stands in this "
        "group, under the precedence at plan Item 3, section 3.8."),
    "Banked head evidence group: unheaded paragraphs only": (
        "A Banked head entry with no later Status line and no "
        "level 4 decision block, whose body carries unheaded "
        "paragraphs, stands in this group, under the precedence "
        "at plan Item 3, section 3.8."),
    "Status occurrences at line start (file level census figure)": (
        "Status occurrences whose occurrence kind is line start, "
        "counted under the PIN-14 precedence, stand in this "
        "figure; it is a file level census figure only and never "
        "the status line total."),
    "Unmatched heading word": (
        "An entry whose heading carries a word with no canonical "
        "mapping in this version stands in this class."),
}


def _class_rule_statement(class_name):
    """The class rule statement in words for one census row, at
    plan Item 3, section 3.6: the row states its class rule in
    words, under PIN-13."""
    if class_name in _CLASS_RULE_STATEMENTS:
        return _CLASS_RULE_STATEMENTS[class_name]
    if class_name.startswith("Canonical state: "):
        state = class_name[len("Canonical state: "):]
        return ("Entries whose derived effective state is %s "
                "stand in this class." % state)
    return ("Entries counted in the class named %s under its "
            "class rule at PIN-13 stand in this class."
            % class_name)


def _census(entries, derived_list, banked_cut_ids=None,
            banked_fence_ids=None):
    pairs = list(zip(entries, derived_list))
    decided = [(e, d) for e, d in pairs if d["state"] in DECIDED_OUTCOMES]

    banked_head = []
    for entry, derived in pairs:
        head = _head_element(entry)
        if head is None or head.disposition != "Banked":
            continue
        if derived["state"] in DECIDED_OUTCOMES or (
                derived["state"] == "Ambiguous"):
            banked_head.append(_display_id(entry))

    non_header = []
    for entry, derived in decided:
        for element in _get(entry, "status_elements") or []:
            if element.occurrence_kind in ("embedded", "variant"):
                non_header.append(_display_id(entry))
                break
            if (element.occurrence_kind == "line start"
                    and element.kind != "line start Status line"):
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
            if out_of_order and derived["state"] in DECIDED_OUTCOMES:
                non_numeric.append(_display_id(entry))

    missing_owner_tail = []
    if pairs:
        tail_section = _get(pairs[-1][0], "section")
        for entry, derived in pairs:
            if _get(entry, "section") != tail_section:
                continue
            if derived["state"] not in DECIDED_OUTCOMES:
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
            # The class rule counts an entry carrying a status
            # element whose value the vocabulary does not
            # classify. An element carrying no status occurrence
            # states no status value at all: a heading borne
            # evidence element stands in that form, with no
            # disposition and no occurrence, on every one word
            # titled entry, and it places its entry in no class
            # here (Step 17, A2-10-F3 merged with F-15-2-2).
            if element.disposition is None and \
                    _get(element, "occurrence_kind") is not None:
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
    rows = [CensusEntry(class_name=name, count=len(members),
                        member_entry_ids=list(members),
                        class_rule_statement=_class_rule_statement(
                            name))
            for name, members in classes]
    for row in rows:
        row.counting_unit = "entries"

    # Canonical state rows, with the head line count and the
    # variance on a row where at least one entry has a head line
    # view giving that state (plan Item 3, section 3.6). The head
    # line view is a validate computation from the first line start
    # Status line element of the entry; it assigns no effective
    # state. The variance is the body derived count minus the head
    # line count, in that direction only.
    head_views = {}
    for entry, derived in pairs:
        elements = list(_get(entry, "status_elements") or [])
        first_line = None
        for element in elements:
            if element.occurrence_kind == "line start":
                first_line = element
                break
        if first_line is None:
            continue
        view = _underlying_state(entry, first_line, elements)
        if view in CANONICAL_STATES:
            head_views.setdefault(view, []).append(_display_id(entry))
    for state in CANONICAL_STATES:
        members = [_display_id(e) for e, d in pairs
                   if d["state"] == state and not d["unparsed"]]
        if not members and state not in head_views:
            continue
        row = CensusEntry(
            class_name="Canonical state: %s" % state,
            count=len(members), member_entry_ids=members,
            class_rule_statement=_class_rule_statement(
                "Canonical state: %s" % state))
        row.counting_unit = "entries"
        row.body_derived_count = len(members)
        if state in head_views:
            row.head_line_count = len(head_views[state])
            row.variance = len(members) - len(head_views[state])
        rows.append(row)

    # The Banked head evidence groups, under the precedence at
    # plan Item 3, section 3.8: a later Status line in the body
    # first, then a level 4 decision block only, then unheaded
    # paragraphs only. A Banked head entry carrying none of the
    # three forms stands in no group and no fourth group is
    # created for it.
    population, groups = _banked_evidence_groups(
        entries, derived_list, banked_cut_ids, banked_fence_ids)
    for name, members in groups:
        if not members:
            continue
        row = CensusEntry(class_name=name, count=len(members),
                          member_entry_ids=list(members),
                          class_rule_statement=_class_rule_statement(
                              name))
        row.counting_unit = "entries"
        rows.append(row)

    # The line start figure, a file level census figure only: the
    # count of Status occurrences at line start under the PIN-14
    # precedence. It is never the status line total.
    line_start_members = []
    line_start_count = 0
    for entry in entries:
        carried = False
        for element in _get(entry, "status_elements") or []:
            if element.occurrence_kind == "line start":
                line_start_count += 1
                carried = True
        if carried:
            line_start_members.append(_display_id(entry))
    row = CensusEntry(
        class_name="Status occurrences at line start (file level "
                   "census figure)",
        count=line_start_count, member_entry_ids=line_start_members,
        class_rule_statement=_class_rule_statement(
            "Status occurrences at line start (file level census "
            "figure)"))
    row.counting_unit = "Status lines"
    rows.append(row)

    # The unmatched heading word Note treatment (PIN-11): the
    # heading word ORDERED has no canonical mapping in this
    # version, and an entry whose heading carries it stands named
    # in the census as an unmatched heading word.
    unmatched_heading = []
    for entry in entries:
        heading = _get(entry, "heading") or _get(
            entry, "heading_text") or ""
        if re.search(r"\bORDERED\b", heading):
            unmatched_heading.append(_display_id(entry))
    if unmatched_heading:
        row = CensusEntry(
            class_name="Unmatched heading word",
            count=len(unmatched_heading),
            member_entry_ids=unmatched_heading,
            class_rule_statement=_class_rule_statement(
                "Unmatched heading word"))
        row.counting_unit = "entries"
        rows.append(row)
    return rows


_INVISIBLE_LINE_CHARS = frozenset(
    "\u00ad\u180e\u200b\u200c\u200d\u200e\u200f"
    "\u202a\u202b\u202c\u202d\u202e\u2060\ufeff")


def _is_run_character(char):
    """Whether a character stands in the run the census
    surfaces read before a heading or inside a line: the
    enumerated invisible characters above, and every
    character of the format, separator, and control classes
    and of the mark classes, read by Unicode class and not
    by enumerated list (Step 17 round 4 triage, record
    section 38 ruling (e), charge CH-63). An Arabic letter
    mark, a variation selector, and a combining mark stand
    in the run on this reading, in step with the parse side
    run the same ruling governs."""
    if char in _INVISIBLE_LINE_CHARS:
        return True
    category = unicodedata.category(char)
    return category in ("Cf", "Cc", "Zl", "Zp") or \
        category.startswith("M")

_OPEN_FIELD_LABELS_FOR_CENSUS = frozenset({
    "question", "the question", "question as put", "options",
    "cost of deciding late", "cost", "what it blocks", "blocks",
})


def _is_identifier_only_line(text):
    """Whether a line states nothing but entry identifiers:
    one or more identifiers, in their exact or respelled
    forms, standing alone, inside one wrapper, or joined to
    one another, and nothing else. The reading is a single
    scan, identifier by identifier and separator by
    separator, with no pattern that redivides the line on a
    failing match: a comma stands in the trailing
    punctuation of one identifier and in the separator
    before the next in the pattern this reading replaces,
    and on a long run of identifiers closing in other words
    that pattern redivided the run on every failing path
    (round 7 charge CH-144, A7-21-1, at the locus of round
    6 charge CH-103, F6-8-1). The scan reads the line once,
    left to right, and a line carrying any word beside its
    identifiers is no identifier only line."""
    line = (text or "").strip()
    wrapper_pairs = (("(", ")"), ("[", "]"), ("{", "}"),
                     ('"', '"'), ("'", "'"), ("<", ">"),
                     ("~", "~"), ("`", "`"),
                     ("“", "”"),
                     ("‘", "’"), ("_", "_"),
                     ("«", "»"),
                     ("„", "“"),
                     ("（", "）"))
    while len(line) >= 2:
        # Punctuation standing after a closing wrapper is
        # wrapper punctuation, read off before the wrapper
        # itself (round 7 charge CH-138, F7-8-1, the
        # parenthesis wrapper closed by a trailing comma).
        while len(line) >= 2 and line[-1] in ".,;:!?" \
                and line[-2] in ")]}\"'*>.,;:!?":
            # A question mark stands in the trailing
            # punctuation set beside the marks above, and
            # two marks standing after a closing wrapper
            # are read off together (round 8 charge CH-180,
            # F8-8-1, the parenthesis wrapper closed by two
            # exclamation marks).
            line = line[:-1].strip()
        pair = None
        for opening, closing in wrapper_pairs:
            if line.startswith(opening) \
                    and line.endswith(closing):
                pair = (opening, closing)
                break
        if pair is None and line.startswith("*") \
                and line.endswith("*"):
            pair = ("*", "*")
        if pair is None:
            break
        line = line[1:-1].strip()
    if not line:
        return False
    position = 0
    end = len(line)
    count = 0
    while position < end:
        match = re.match(r"(?:DQ|R)[\s\-_]?[0-9]+",
                         line[position:], re.IGNORECASE)
        if not match:
            return False
        position += match.end()
        count += 1
        while position < end and line[position] in ".,;:!?":
            position += 1
        if position >= end:
            break
        separated = False
        while position < end:
            char = line[position]
            if char.isspace() or char in ",;/&-+":
                position += 1
                separated = True
                continue
            word = re.match(r"(?:and|or|versus)(?![A-Za-z])",
                            line[position:], re.IGNORECASE)
            if word:
                # The word and standing as a joiner between
                # two identifiers (round 7 charge CH-138,
                # F7-8-1). The word or and the plus sign
                # stand as joiners on the same ground (round
                # 8 charge CH-180, F8-8-1). The word versus
                # stands as a joiner on the same ground, and
                # a guillemet pair, a low and high quotation
                # pair, and a fullwidth parenthesis pair
                # stand in the wrapper set above on the same
                # ground (round 9 charge CH-209, F9-8-1). A word standing
                # after the joiner that is no identifier ends
                # the scan as a failing scan above, so an
                # identifier standing beside genuine words
                # keeps its content reading.
                position += word.end()
                separated = True
                continue
            break
        if not separated or position >= end:
            return False
    return count >= 1


def _line_carries_content(text):
    """Whether a body line carries record content, for the
    Banked head evidence groups (Step 17 round 2 charge
    CH-19, F2-8-1 and F2-8-2, taken in one act in
    _banked_evidence_groups). Invisible format characters
    are removed first, so a line of a zero width space or a
    left to right mark alone carries nothing. What remains
    must hold word matter: at least one word of two or more
    characters carrying a letter. A line of punctuation alone (a full
    stop, a rule line), a single letter alone, two single
    characters, and one bare number carry no disposition
    and no record content, and state no content here
    (round 3 charge CH-42, F3-8-1: digits alone state no
    content, while a genuine short word in any script, two
    CJK characters forming one word among them, stands)."""
    visible = "".join(
        char for char in (text or "")
        if not _is_run_character(char))
    if re.fullmatch(r"(?:DQ-[0-9]+|R-[0-9]+)",
                    visible.strip()):
        # A line carrying only an entry identifier states
        # no content: it names a cross reference and no
        # disposition and no record matter, as the bare
        # number form above states none (round 4 charge
        # CH-63, F4-8-6).
        return False
    if re.fullmatch(
            r"(?:DQ|R)\s*-?\s*[0-9]+\.?"
            r"(?:\s+(?:DQ|R)\s*-?\s*[0-9]+\.?)*",
            visible.strip(), re.IGNORECASE):
        # The same identifier only line in a respelled
        # form states no content either (round 5 charge
        # CH-85, F5-8-1): a trailing full stop, a case
        # change, a dropped or spaced hyphen, or a second
        # identifier standing beside the first each leave
        # the line stating nothing but cross references.
        # An identifier standing beside other words keeps
        # its content reading below, untouched.
        return False
    if _is_identifier_only_line(visible.strip()):
        # The identifier only line in a further respelled
        # form states no content either (round 6 charge
        # CH-103, F6-8-1): trailing punctuation, a wrapper,
        # an underscore in place of the hyphen, or a second
        # identifier joined by punctuation each leave the
        # line stating nothing but cross references. Round
        # 7 charge CH-138, F7-8-1, widens the forms the scan
        # reads: an exclamation mark, a quotation mark,
        # angle bracket, or star wrapper, a wrapper closed
        # by trailing punctuation, and an ampersand, hyphen,
        # or word joiner. Round 8 charge CH-180, F8-8-1,
        # widens the forms the scan reads again: a question
        # mark, a tilde, backtick, curly quote, or
        # underscore wrapper, two punctuation marks after a
        # closing wrapper, and the word or or a plus sign
        # standing as a joiner. Round 9 charge CH-209,
        # F9-8-1, widens the forms the scan reads again: a
        # guillemet pair, a low and high quotation pair, or
        # a fullwidth parenthesis pair standing as a
        # wrapper, and the word versus standing as a
        # joiner. Round 7 charge CH-144, A7-21-1,
        # stands at the same locus: the reading is the scan
        # at _is_identifier_only_line, not the fullmatch
        # whose repeated group redivided a failing line.
        return False
    stripped = visible.strip()
    if re.match(r"Landed(?:\s|:|,|;)", stripped, re.IGNORECASE) or \
            re.match(r"Origins?(?:\s*:|\s*;)", stripped,
                       re.IGNORECASE) or \
            re.match(r"Filed(?:\s|:|,|;|\.)", stripped,
                       re.IGNORECASE) or \
            re.match(r"Recorded(?:\s|:|,|;)", stripped,
                       re.IGNORECASE) or \
            re.match(r"Sources?\s*[:,;]", stripped, re.IGNORECASE):
        # A landed line states where a ruling landed and
        # no disposition, and an Origin line is a label
        # only and carries no element by itself: a block
        # whose only body is one of these lines carries no
        # disposition statement and states no census
        # content (round 5 charge CH-85, F5-8-2, toward
        # the PIN-01 form 1 ground). Round 6 charge CH-103,
        # F6-8-2, widens the reading: the landed and Origin
        # forms stand case aside, and a Filed line, stating
        # where a record was filed, and a Source line, a
        # label only on the same PIN-05 ground, state no
        # census content either. Round 7 charge CH-139,
        # F7-8-2, widens the reading again on the same
        # grounds: the Source line stands case aside with
        # its neighbours, a comma standing after the word
        # Landed closes that line as a space, a tab, or a
        # colon does, a Recorded line states where a ruling
        # was recorded and no disposition, as the Filed line
        # does, and an Origins line is the Origin label in
        # its plural form, a label only on the same PIN-05
        # ground. Round 8 charge CH-170, F8-8-2, widens the
        # reading again on the same grounds: a comma
        # standing after the word Filed or the word
        # Recorded closes that line as a space or a colon
        # does, a Source line closed by a comma is the
        # label only line on the same PIN-05 ground, a
        # Sources line is the Source label in its plural
        # form on the ground the Origins form already
        # stands on, and a semicolon standing after the
        # word Landed closes that line as a comma does.
        # Round 9 charge CH-206, F9-8-2, widens the
        # reading again on the same grounds: a semicolon
        # standing after the word Filed, the word
        # Recorded, the word Source, or the word Origin
        # closes that line as a comma or a colon does, and
        # a full stop standing after the word Filed closes
        # that line on the same ground.
        return False
    words = re.findall(r"[^\W_]+", visible)
    return any(
        len(word) >= 2 and any(char.isalpha() for char in word)
        for word in words)


def _is_heading_shaped_line(text):
    """Whether a body line is a heading in its container: a
    line whose text, after any blockquote or list item
    prefix characters standing before it are read off, opens
    with a hash. A quoted or listed genuine prose paragraph
    is not heading shaped and keeps its paragraph reading
    (Step 17 round 2 charge CH-19, F2-8-2, bounded by its
    control G2). Round 3 charge CH-42 widens the reading:
    invisible format characters standing before the heading
    are removed first (F3-8-3), and the marker set read off
    covers a number of any width, a lettered or roman
    numeral marker, a bullet character beyond the plain
    dash, star, and plus forms, and a bold wrap (F3-8-4),
    each still only where the text behind it opens with a
    hash, so genuine prose behind the same markers keeps
    its paragraph reading."""
    stripped = "".join(
        char for char in (text or "")
        if not _is_run_character(char)).strip()
    while True:
        if stripped.startswith(">"):
            stripped = stripped[1:].lstrip()
            continue
        if stripped.startswith("**"):
            stripped = stripped[2:].lstrip()
            continue
        if stripped.startswith("__"):
            stripped = stripped[2:].lstrip()
            continue
        wrap = re.match(r"[*_~`]+(?=#)", stripped)
        if wrap:
            # A star or underscore wrap of any width
            # standing directly against the hash opening:
            # the triple star and single underscore forms
            # of round 5 charge CH-85, F5-8-4, beside the
            # two character bold openings above. A tilde
            # wrap stands beside them (round 7 charge
            # CH-141, F7-8-4). A wrap
            # standing against prose opens no hash and is
            # never read off here, so genuine prose behind
            # the same wraps keeps its paragraph reading.
            stripped = stripped[wrap.end():].lstrip()
            continue
        # The marker set: round 7 charge CH-141, F7-8-4,
        # widens the letter marker to five letters, joins
        # the double angle character (U+00BB) and the
        # rightwards arrow (U+2192) to the bullet set, and
        # joins a digit and letter marker, each still only
        # where the text behind it opens with a hash.
        # Round 8 charge CH-181, F8-8-4, widens the letter
        # marker to six letters, joins the small black
        # rightwards triangle (U+25B8) and the double
        # rightwards arrow (U+21D2) to the bullet set, and
        # joins a letter and digit marker, and a backtick
        # wrap stands in the wrap reading above.
        # Round 9 charge CH-210, F9-8-4, widens the letter
        # marker to seven letters, and joins the black
        # rightwards triangle (U+25B6) and the black
        # rightwards arrow (U+27A1) to the bullet set.
        match = re.match(
            r"(?:[-*+\u2022\u25e6\u2013\u2014\u2023\u00b7\u00bb\u2192\u25b8\u21d2\u25b6\u27a1]"
            r"|\d+[.)]|\d+[A-Za-z][.)]|[A-Za-z]\d+[.)]"
            r"|[A-Za-z]{1,7}[.)]|[ivxlcdmIVXLCDM]+[.)])\s+",
            stripped)
        if match:
            stripped = stripped[match.end():].lstrip()
            continue
        break
    return stripped.startswith("#")


def _is_open_field_labelled_line(text):
    """Whether a body line is a labelled line of one of the
    open entry field families, the labels parse records in
    its open field label set. The README states labelled
    field paragraphs count toward none of the three Banked
    head evidence groups, and a repeated open field line
    inside a level 4 block is such a line (Step 17 round 2
    charge CH-19, F2-8-1, its labelled field form). The
    decision evidence labels a block exists to carry stand
    outside this set and keep their content reading."""
    stripped = "".join(
        char for char in (text or "")
        if not _is_run_character(char)).strip()
    # The label reading reads respelled characters in
    # their plain forms first (round 7 charge CH-140,
    # F7-8-3): a letter standing in the fullwidth block
    # reads as the letter it respells, and a small colon
    # (U+FE55) or a modifier letter colon (U+A789) standing
    # at the label close reads as a colon, as the fullwidth
    # colon already does. The reading is this test's alone:
    # the line as written stands untouched everywhere else.
    read = stripped.replace("\ufe55", ":").replace(
        "\ua789", ":").replace("\u2236", ":")
    # A ratio sign (U+2236) standing at the label close
    # reads as a colon on the same ground (round 8 charge
    # CH-171, F8-8-3), and two letters that respell their
    # Latin shapes, the Greek small letter omicron
    # (U+03BF) and the Cyrillic small letter ie (U+0435),
    # read as the letters they respell, as the fullwidth
    # letters below do.
    read = read.replace("\u03bf", "o").replace(
        "\u0435", "e")
    # Two further letters that respell their Latin
    # shapes read as the letters they respell on the
    # same ground (round 9 charge CH-207, F9-8-3): the
    # Cyrillic small letter a (U+0430) reads as the
    # letter a, and the Greek capital letter omicron
    # (U+039F) reads as the letter O. A figure space
    # (U+2007), a narrow no break space (U+202F), or a
    # punctuation space (U+2008) standing inside the
    # label stands in the space set of the label pattern
    # below on the same ground.
    read = read.replace("\u0430", "a").replace(
        "\u039f", "O")
    read = "".join(
        chr(ord(char) - 0xFEE0)
        if "\uff01" <= char <= "\uff5e" else char
        for char in read)
    match = re.match(
        r"^([A-Za-z][A-Za-z0-9 \t\u00a0\u2009\u200a\u2007\u2008\u202f\u3000()_-]{0,80})"
        r"[ \t\u00a0\u2009\u3000]*"
        r"(?::|\uff1a)",
        read)
    if not match:
        # A taught multi word label standing as the opening
        # words of a label grown past the length the pattern
        # above admits is still the taught label it opens
        # with (round 5 charge CH-85, F5-8-3, the Cost label
        # grown past 80 characters): the opening words form
        # of the CH-63 cure, read at the length the line
        # itself carries.
        long_match = re.match(
            r"^(.{1,400}?)[ \t\u00a0\u3000]*:", read)
        if long_match:
            long_normalised = re.sub(
                r"\s+", " ",
                long_match.group(1).replace("-", " ")
                ).strip().lower()
            if any(
                    " " in taught and
                    long_normalised.startswith(taught + " ")
                    for taught in
                    _OPEN_FIELD_LABELS_FOR_CENSUS):
                return True
        return False
    normalised = re.sub(r"\s+", " ",
                        match.group(1).replace("-", " ")
                        .replace("_", " ")
                        ).strip().lower()
    if normalised in _OPEN_FIELD_LABELS_FOR_CENSUS:
        return True
    unparenthesised = re.sub(
        r"\s+", " ",
        re.sub(r"\([^)]*\)", " ", normalised)).strip()
    if unparenthesised != normalised and \
            unparenthesised in _OPEN_FIELD_LABELS_FOR_CENSUS:
        # A taught label carrying one of its own words in
        # parentheses stands as the label it respells
        # (round 5 charge CH-85, F5-8-3, the Question
        # (as put) form).
        return True
    # A taught label respelled stands as the label it
    # respells (round 4 charge CH-63, F4-8-2): a digit
    # standing in the label, as a trailing number on the
    # taught words; a hyphen standing where the taught
    # label carries a space, read above by the hyphen
    # replacement; a tab standing before the colon, read
    # by the label pattern above; and a taught multi word
    # label standing as the opening words of a longer
    # label, the taught Cost label grown past the length
    # cap among them. A label that is no respelling of a
    # taught label, a new label in letters and a colon,
    # stands outside this test exactly as before.
    trimmed = re.sub(r"\s*[0-9]+$", "", normalised)
    if trimmed != normalised and \
            trimmed in _OPEN_FIELD_LABELS_FOR_CENSUS:
        # The trailing number stands read off whether a
        # space stands before it or the digit stands
        # attached to the taught words (round 5 charge
        # CH-85, F5-8-3, the Question2 form).
        return True
    return any(
        " " in taught and normalised.startswith(taught + " ")
        for taught in _OPEN_FIELD_LABELS_FOR_CENSUS)


def _h4_block_has_body(entry, block):
    """Whether a level 4 decision block carries a body: at
    least one body line of the entry standing after the
    block heading line and within the block span, carrying
    record content under _line_carries_content. A block
    whose span holds its heading line alone has no body,
    and a non content line, a heading shaped line, or a
    repeated open field labelled line standing alone in
    the span is no body either (Step 17, F-8-1, widened at
    round 2 charge CH-19, F2-8-1)."""
    span = _get(block, "span")
    start = _get(span, "start_line", "start")
    end = _get(span, "end_line", "end")
    if start is None:
        return False
    for number, text in _body_lines(entry):
        if number <= start:
            continue
        if end is not None and number > end:
            continue
        if _is_heading_shaped_line(text):
            continue
        if _is_open_field_labelled_line(text):
            continue
        if _line_carries_content(text):
            return True
    return False


_BANKED_FENCE_RUN_RE = re.compile(r"(`{3,}|~{3,})")


def _fence_stored_form(text):
    """The stored form of one line for the fence reading in
    _fence_state_by_line: the comment segments of the line
    removed, in the form the parse fence reading states for
    its own stored form. A segment left unclosed at the end
    of the line leaves the comment open for the lines under
    it, and the matter behind it stands inside the comment.
    Returns the stored text and whether the line ends inside
    a comment."""
    parts = []
    in_comment = False
    rest = text
    while True:
        opening = rest.find("<!--")
        if opening < 0:
            parts.append(rest)
            break
        closing = rest.find("-->", opening + 4)
        if closing < 0:
            parts.append(rest[:opening])
            in_comment = True
            break
        parts.append(rest[:opening])
        rest = rest[closing + 3:]
    return "".join(parts), in_comment


def _fence_state_by_line(lines):
    """The fence state after each line, as a list parallel to
    lines: each item is the open fence as a character and run
    length pair, or None where no fence stands open after
    that line. The reading follows the parse fence reading
    on the same terms it states: a stored form opening with
    a fence run opens a fence; a fence closes only on a line
    whose stored form is a run of the fence own character, at
    least as long as the opening run, with nothing after the
    run but whitespace, a run carrying matter after it being
    fence content, not a delimiter; and a line standing
    inside a comment opens no fence, the rest of a comment
    closing line being read on its stored form (Step 17
    round 8 charge CH-189)."""
    states = []
    fence = None
    in_comment = False
    for text in lines:
        if fence is not None:
            stored, unclosed = _fence_stored_form(text)
            candidate = stored.strip()
            run = _BANKED_FENCE_RUN_RE.match(candidate)
            if run and run.group(1)[0] == fence[0] and \
                    len(run.group(1)) >= fence[1] and \
                    not candidate[run.end():].strip():
                fence = None
                in_comment = unclosed
            states.append(fence)
            continue
        if in_comment:
            closing = text.find("-->")
            if closing < 0:
                states.append(fence)
                continue
            stored, unclosed = _fence_stored_form(
                text[closing + 3:])
            run = _BANKED_FENCE_RUN_RE.match(stored.lstrip())
            if run:
                fence = (run.group(1)[0], len(run.group(1)))
                in_comment = False
            else:
                in_comment = unclosed
            states.append(fence)
            continue
        if "<!--" not in text and \
                not _BANKED_FENCE_RUN_RE.match(text.strip()):
            states.append(fence)
            continue
        stored, in_comment = _fence_stored_form(text)
        run = _BANKED_FENCE_RUN_RE.match(stored.lstrip())
        if run:
            fence = (run.group(1)[0], len(run.group(1)))
            in_comment = False
        states.append(fence)
    return states


def _banked_fence_entry_ids(model, entries):
    """The entries whose own body carries the opening line of
    a fence that stands open at the end of the body, returned
    as the entries themselves. The fence state is read over
    the model lines by _fence_state_by_line, on the parse
    fence reading terms: the entry qualifies only where no
    fence stands open before its first body line and a fence
    stands open after its last body line, so the opening
    line stands inside its own body. An entry whose body
    stands wholly inside a fence opened in an earlier entry
    body does not qualify: the opening line stands outside
    its own body, and that form stands outside this bound
    (Step 17 round 8 charge CH-189). The collection carries
    entries, never display identifiers, on the same terms as
    _banked_cut_entry_ids."""
    lines = list(_get(model, "lines") or [])
    if not lines:
        return []
    states = _fence_state_by_line(lines)
    fence_entries = []
    for entry in entries:
        body = _body_lines(entry)
        if not body:
            continue
        first = body[0][0]
        last = body[-1][0]
        if first is None or last is None:
            continue
        before = states[first - 2] if first >= 2 else None
        after = states[last - 1] if 1 <= last <= len(states) \
            else None
        if before is None and after is not None:
            fence_entries.append(entry)
    return fence_entries


def _banked_cut_entry_ids(model, entries):
    """The entries cut by an unmatched heading, returned as
    the entries themselves: entries whose span ends on the
    line directly before the span of an orphan segment whose
    record carries unmatched_heading. The heading that cuts
    such an entry is the heading the run itself reports
    under PIN-06, and the prose standing under it stands in
    the orphan segment, outside the entry body, quarantined
    as file level matter, so it can never stand as evidence
    of the entry it cut (fix wave 3 closing, defect D1,
    register item 17R-170). The collection carries entries,
    never display identifiers: where one identifier stands twice
    in a file, only the entry whose own span ends before
    the segment is cut, and its uncut twin keeps its
    population standing (fix wave 4 charge CH-53, register
    item 17R-183)."""
    cut_starts = set()
    for segment in _get(model, "orphan_segments") or []:
        if not _get(segment, "unmatched_heading"):
            continue
        span = _get(segment, "span")
        start = _get(span, "start_line") if span is not None else None
        if start is not None:
            cut_starts.add(start)
    cut_entries = []
    if not cut_starts:
        return cut_entries
    for entry in entries:
        span = _get(entry, "span")
        if span is None:
            spans = _get(entry, "spans") or []
            span = spans[-1] if spans else None
        end = _get(span, "end_line") if span is not None else None
        if end is not None and end + 1 in cut_starts:
            cut_entries.append(entry)
    return cut_entries


def _absorbed_h4_entry_heading(entry):
    """A level 4 heading standing in an entry body in a non
    exact entry heading form, returned as its line number
    and the heading line as written, or None.

    The exact numbered form and the named unnumbered form
    take the orphan unmatched treatment in parse (round 4
    charge CH-63, F4-8-1). The non exact forms stand
    outside that reading and are absorbed as decision
    block headings: a number standing in a digit script
    other than ASCII, a colon with no space after it, and
    an R number heading outside the one named form (round
    5 charge CH-85, F5-8-5). At the validate surfaces the
    form takes the orphan treatment here: the census reads
    the entry on the matter standing before the heading
    only, and the heading takes its PIN-06 Warning in
    _absorbed_h4_entry_heading_findings. The Arabic Indic
    digit member is read at this orphan reading only,
    under record section 52 ruling (g): the digit token is
    recognised as a digit token by its decimal digit
    shape, and no number is read from it as data, the
    ASCII digit ground standing unmoved everywhere else.
    """
    for number, text in _body_lines(entry):
        stripped = (text or "").strip()
        match = re.match(r"^####\s+(.+?)\s*$", stripped)
        if not match:
            continue
        heading_text = match.group(1)
        numbered = re.match(r"^DQ-([^:\s]+):", heading_text)
        if numbered:
            token = numbered.group(1)
            if re.match(r"^DQ-[0-9]+:\S", heading_text):
                return number, stripped
            if token and all(char.isdecimal() for char in token) \
                    and not token.isascii():
                return number, stripped
            if re.match(r"^DQ-[0-9]+:(?:\s{2,}|\t)", heading_text):
                # Two spaces or a tab after the colon (round
                # 6 charge CH-103, F6-8-5, the remaining forms
                # of that limb, stated at the fall through
                # reading below).
                return number, stripped
            if re.match(r"^DQ-[0-9]+:\u00a0", heading_text):
                # A single no break space after the colon
                # (round 7 charge CH-142, F7-8-5): it is
                # neither the non space character, nor the
                # two space run, nor the tab the readings
                # above ask.
                return number, stripped
            if re.match(r"^DQ-[0-9]+:$", heading_text):
                # A colon with no title after it (round 7
                # charge CH-142, F7-8-5): every other reading
                # asks matter after the colon to take hold
                # of, and this form gives it none.
                return number, stripped
            if re.match(r"^DQ-[0-9]+:\u3000", heading_text):
                # A single ideographic space after the colon
                # (round 8 charge CH-172, F8-8-5): it is
                # neither the non space character, nor the
                # two space run, nor the tab, nor the single
                # no break space the readings above ask.
                return number, stripped
            continue
        if re.match(r"^DQ-[0-9]+(?:\s+:|:\s{2,}|:\t|\uff1a|\s+\S)",
                    heading_text) or \
                re.match(r"^(?i:dq)-[0-9]+:", heading_text) or \
                re.match(r"^DQ_[0-9]+(?::|\s)", heading_text) or \
                re.match(r"^DQ[\u2013\uff0d][0-9]+(?::|\s)",
                         heading_text) or \
                re.match(r"^(?i:dq)[\u2010\u2012\u2013\u2212\u00ad]"
                         r"[0-9]+(?::|\s)",
                         heading_text) or \
                re.match(r"^(?i:dq)_[0-9]+(?::|\s)",
                         heading_text):
            # A level 4 entry heading in a further non exact
            # form (round 6 charge CH-103, F6-8-5): a space
            # before the colon, two spaces or a tab after it,
            # a lower case entry prefix, a fullwidth colon,
            # or no colon at all. Round 7 charge CH-142,
            # F7-8-5, joins the mixed case entry prefix and
            # the underscore standing in place of the hyphen
            # to the forms read here. Round 8 charge CH-172,
            # F8-8-5, joins an en dash (U+2013) or a fullwidth
            # hyphen (U+FF0D) standing in place of the hyphen,
            # and the underscore form under a mixed case
            # prefix, which stands between the case aside
            # hyphen reading and the upper case underscore
            # reading and is named by neither. Round 9
            # charge CH-208, F9-8-5, joins a hyphen
            # (U+2010), a figure dash (U+2012), a minus
            # sign (U+2212), or a soft hyphen (U+00AD)
            # standing in place of the hyphen under a
            # prefix in any case, and the en dash form
            # under a mixed case prefix, which stands
            # between the upper case en dash reading and
            # the case aside hyphen reading and is named
            # by neither. The exact form, a colon and
            # one space, stands outside this reading and keeps
            # its standing treatment, as the numbered branch
            # above leaves it.
            return number, stripped
        if re.match(r"^(?:R|r)-[0-9]+(?::|\s)", heading_text) and \
                heading_text != "R-7 closure conflict":
            # The R number heading in its lower case form
            # stands beside the upper case form (round 7
            # charge CH-142, F7-8-5); the one named form
            # above keeps its standing treatment.
            return number, stripped
        if re.match(r"^R[0-9]+(?::|\s)", heading_text):
            # The R number heading with no hyphen at all
            # (round 8 charge CH-172, F8-8-5): the reading
            # above asks a hyphen after the letter, and this
            # form gives it none.
            return number, stripped
            # The R number heading in its lower case form
            # stands beside the upper case form (round 7
            # charge CH-142, F7-8-5); the one named form
            # above keeps its standing treatment.
            return number, stripped
    return None


def _absorbed_h4_entry_heading_findings(entries):
    """The PIN-06 Warning for a level 4 heading in a non
    exact entry heading form absorbed into the entry above
    it, in the form the parse side orphan treatment prints
    for the exact forms (round 5 charge CH-85, F5-8-5)."""
    findings = []
    for entry in entries:
        absorbed = _absorbed_h4_entry_heading(entry)
        if absorbed is None:
            continue
        _number, heading_text = absorbed
        findings.append(_finding(
            "PIN-06", "Warning", _display_id(entry),
            _get(entry, "span"), heading_text,
            "The heading %s matches no recognised heading "
            "form; no entry is raised for it." % heading_text,
            basis="a heading matching no recognised heading "
                  "form"))
    return findings


def _banked_evidence_groups(entries, derived_list, cut_ids=None,
                            fence_ids=None):
    """The Banked head population and its three evidence groups.

    Population: entries whose first line start Status line is the
    exact Banked line. Precedence: an entry with a later Status
    line in the body is in the first group whatever else its body
    carries; an entry with no later Status line and a level 4
    decision block is in the second; an entry with neither, whose
    body carries unheaded paragraphs, is in the third. One
    bound on the population stands beside the unparsed bound
    below: an entry cut by an unmatched heading, standing
    in cut_ids as the entry itself, that takes no group
    stands outside the population,
    because its evidence body was cut off by that heading and
    the matter behind the heading is the segment's, not the
    entry's. A cut entry that takes a group keeps its population
    and group standing exactly as before, and an entry with no
    such cut that takes no group stays in the population, so
    its footing failure stands as before. A second bound of
    the same form stands beside it (Step 17 round 8 charge
    CH-189): an entry whose own body carries the opening line
    of a fence that stands open at the end of its body,
    standing in fence_ids as the entry itself, that takes no
    group stands outside the population, because the matter
    behind the opening line stands inside the fence and is
    not the entry's evidence, so the body the groups would
    read is not whole. A fence entry that takes a group keeps
    its population and group standing exactly as before. An
    entry with no fence standing open at the end of its body
    that takes no group stays in the population on the same
    terms as before: a plain entry carrying only labelled
    fields, and an entry whose only paragraph stands inside
    a fence that closes before its body ends, each keep
    their footing failure exactly as before, and no part of
    this bound settles that shape in either direction.
    """
    population = []
    group1, group2, group3 = [], [], []
    for entry, derived in zip(entries, derived_list):
        if derived.get("unparsed"):
            # An unparsed entry carries no derived state and
            # its body is not whole, so it stands in no census
            # population and in no evidence group: it is
            # counted once in the headed entry count and in
            # the unparsed entry count, and nowhere else, as
            # brief section 5.8 states for the truncation form.
            continue
        elements = list(_get(entry, "status_elements") or [])
        first_line = None
        for element in elements:
            if element.occurrence_kind == "line start":
                first_line = element
                break
        if first_line is None or first_line.verbatim != "Banked":
            continue
        display = _display_id(entry)
        population.append(display)
        population_index = len(population) - 1
        absorbed = _absorbed_h4_entry_heading(entry)
        absorbed_line = absorbed[0] if absorbed else None
        later = [e for e in elements
                 if e.occurrence_kind == "line start"
                 and e is not first_line
                 and (absorbed_line is None
                      or getattr(e, "line", None) is None
                      or getattr(e, "line", None) < absorbed_line)]
        if later:
            group1.append(display)
            continue
        if any(_get(block, "marking_form") == "H4 sub part"
               and _h4_block_has_body(entry, block)
               and (absorbed_line is None
                    or _get(_get(block, "span"), "start_line",
                            "start") is None
                    or _get(_get(block, "span"), "start_line",
                            "start") < absorbed_line)
               for block in _get(entry, "decision_blocks") or []):
            # The second group test is for a level 4 decision
            # block only, under plan Item 3, section 3.8 and
            # testing pin down 11: a decision block of any other
            # marking form, a bold supersession segment or an
            # unheaded labelled paragraph among them, is not a
            # level 4 block and places the entry in no group on
            # its own. A level 4 block whose span carries no
            # body line after its heading line is a bare
            # heading: under PIN-01 form 1 a heading that is
            # no container of record content carries no census
            # evidence element, so the bare heading takes no
            # credit here and the entry stands in no group on
            # its account (Step 17, F-8-1).
            group2.append(display)
            continue
        has_paragraph = False
        for _line, text in _body_lines(entry):
            if absorbed_line is not None and _line >= absorbed_line:
                # The matter standing at and after an
                # absorbed level 4 entry heading is the
                # absorbed entry own matter, not this entry
                # own paragraph (round 5 charge CH-85,
                # F5-8-5).
                continue
            stripped = (text or "").strip()
            if not stripped:
                continue
            if _is_heading_shaped_line(text):
                # A heading shaped line is no unheaded
                # paragraph, whether the hash opening stands
                # at the line start or behind one prefix
                # character in a blockquote or list item
                # container (Step 17 round 2 charge CH-19,
                # F2-8-2). A quoted or listed genuine prose
                # paragraph is not heading shaped and keeps
                # its credit below.
                continue
            if re.match(r"^[A-Z][A-Za-z ]{0,40}:", stripped):
                continue
            if _is_open_field_labelled_line(text):
                # A labelled field line takes no group credit
                # in any case form, on any surface of the
                # census: the same case aside reading the
                # level 4 body test takes, standing beside
                # the capitalised label skip above, which
                # keeps its own forms (round 3 charge CH-42,
                # F3-8-2).
                continue
            if not _line_carries_content(text):
                # The same content test as the level 4 group
                # test above, in one act: a non content line
                # that takes no group 2 credit takes no
                # group 3 credit in its place either
                # (charge CH-19, F2-8-1).
                continue
            has_paragraph = True
            break
        if has_paragraph:
            group3.append(display)
        elif (cut_ids and any(entry is cut_entry
                              for cut_entry in cut_ids)) or \
                (fence_ids and any(entry is fence_entry
                                   for fence_entry in fence_ids)):
            # The entry takes no group and stands cut by an
            # unmatched heading, or its own body carries the
            # opening line of a fence standing open at the
            # end of its body, so it stands outside the
            # population, on the bounds in the docstring
            # above. The test is on the entry itself, by
            # identity, never on its display identifier
            # (charge CH-53, and charge CH-189 for the fence
            # bound).
            del population[population_index]
    groups = [
        ("Banked head evidence group: later Status line in the "
         "body", group1),
        ("Banked head evidence group: level 4 decision block "
         "only", group2),
        ("Banked head evidence group: unheaded paragraphs only",
         group3),
    ]
    return population, groups


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
    "PIN-06": "Restate the heading in a recognised heading form, or take "
        "the heading and the lines under it out of the file.",
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


def _preamble_status_occurrences(model):
    """The status occurrences standing outside every entry.

    A Status line standing in the queue preamble, before the
    first entry heading, is a status occurrence in the file,
    and so is a Status line standing in any other file level
    unit: a section introduction, a note section standing
    between entries, or a trailing file level segment. Parse
    assigns every line outside an entry to one file level unit,
    and the occurrences are read from every unit text here,
    under the same marker and kind rules parse applies inside
    entries (Step 17, S17-ATK7-03; round 2, A2-3-F4 and
    S17-ATK2-7-03). Each occurrence is returned as
    (verbatim, occurrence kind, line, position in line), and
    stands in the appendix under the file level member FILE.

    The variant marker stands in its full form, as parse reads
    it inside entries: the verbatim phrasing is the whole
    marker text with its value, Status unchanged standing at
    its head, and the occurrence kind is variant (round 2,
    A2-3-F3). The plain marker reads its value alone, at kind
    line start or embedded by its position in the line.
    """
    occurrences = []
    if model is None:
        return occurrences
    for unit in _get(model, "units") or []:
        span = _get(unit, "span")
        first_line = _get(span, "start_line", "start") or 1
        text = _get(unit, "text") or ""
        for offset, line_text in enumerate(text.split("\n")):
            markers = []
            for marker in ("Status:", "Status unchanged"):
                start = line_text.find(marker)
                while start != -1:
                    markers.append((start, marker))
                    start = line_text.find(marker, start + 1)
            markers.sort()
            for index, (start, marker) in enumerate(markers):
                end = start + len(marker)
                stop = (markers[index + 1][0]
                        if index + 1 < len(markers) else None)
                if marker == "Status unchanged":
                    if not line_text[end:stop].strip():
                        continue
                    verbatim = line_text[start:stop].strip()
                    occurrences.append(
                        (verbatim, "variant",
                         first_line + offset, start))
                    continue
                verbatim = line_text[end:stop].strip()
                if not verbatim:
                    continue
                kind = "line start" if start == 0 else "embedded"
                occurrences.append(
                    (verbatim, kind, first_line + offset, start))
    return occurrences


def _appendix_rows(entries, vocabulary, model=None):
    rows = {}
    order = []
    for entry in entries:
        display_id = _display_id(entry)
        carried = list(_get(entry, "status_elements") or [])
        # Occurrences that stand on no element, the landing
        # record form at PIN-01 form 4 recorded by parse on its
        # own channel, count in the appendix under PIN-14 in
        # the same way as the occurrences elements carry.
        carried += list(
            _get(entry, "occurrence_only_elements") or [])
        for element in carried:
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
    # The status occurrences standing in the file header unit
    # enter the same rows, under the file level member, so the
    # appendix and the occurrence total count every status
    # occurrence in the file (Step 17, S17-ATK7-03).
    for verbatim, kind, line, position in \
            _preamble_status_occurrences(model):
        key = (verbatim, kind)
        if key not in rows:
            rows[key] = {"count": 0, "members": [],
                         "first": (line, position)}
            order.append(key)
        rows[key]["count"] += 1
        if "FILE" not in rows[key]["members"]:
            rows[key]["members"].append("FILE")
    order.sort(key=lambda key: rows[key]["first"])
    result = []
    for phrasing, kind in order:
        data = rows[(phrasing, kind)]
        row = VerbatimAppendixRow(
            phrasing=phrasing, occurrence_count=data["count"],
            kind=kind, member_entry_ids=data["members"])
        # The row stands in its declared shape only: no
        # unclassified flag stands attached to it here, the
        # declared VerbatimAppendixRow shape carrying no such
        # field (the A1-F6 cure form).
        result.append(row)
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
# Unit 3g: the Exit decision supply point
# ---------------------------------------------------------------------

# Validate supplies no Exit decision. The exit decision field of
# the render model stands unsupplied in the Validate output, and
# shell supplies it at run time after validate returns, under the
# supply point at plan Item 3, section 3.7. No decision builder
# stands in this module.


# ---------------------------------------------------------------------
# The validate boundary
# ---------------------------------------------------------------------

# The disposition a canonical family gives, for the translation
# below. The families the shipped vocabulary mapping states map
# to the disposition of the same name, except the Closed as
# decided family, whose disposition form is Closed. The Relative
# family gives no disposition, as it gave none in the table this
# translation replaces.
_FAMILY_DISPOSITIONS = {
    "Banked": "Banked",
    "Open": "Open",
    "Parked": "Parked",
    "Presented": "Presented",
    "Ruled": "Ruled",
    "Settled": "Settled",
    "Closed as decided": "Closed",
}


def _apply_vocabulary_translation(entries, vocabulary):
    """Translate disposition-less Status values, validate side.

    The translation of a verbatim phrasing to its canonical
    family is validate work under the seam at plan Item 3,
    section 3.5: parse records a Status element whose opening
    forms state no disposition with no disposition, under
    PIN-04, and validate alone performs every mapping. Where
    such an element's verbatim value stands in the vocabulary
    mapping by exact match, the family the mapping states gives
    the element its disposition, in the family form above. No
    normalisation is applied to the value, so a phrasing
    standing in the table in one code point sequence does not
    translate a canonically equivalent phrasing in another
    sequence; that phrasing stands untranslatable. Elements
    carrying a disposition from their opening forms, and
    elements that carry no Status occurrence, are untouched.
    """
    mapping = _get(vocabulary, "mapping") or {}
    for entry in entries:
        for element in _get(entry, "status_elements") or []:
            if _get(element, "occurrence_kind") is None:
                continue
            if _get(element, "disposition") is not None:
                continue
            family = mapping.get(_get(element, "verbatim"))
            disposition = _FAMILY_DISPOSITIONS.get(family)
            if disposition is None:
                continue
            try:
                element.disposition = disposition
            except Exception:
                try:
                    element["disposition"] = disposition
                except Exception:
                    pass


_BLOCKS_NO_ITEM_VALUES = frozenset({
    "none", "nothing", "nothing else", "nothing else at all",
    "no items", "no item",
    "nothing at all", "none at all", "nothing whatsoever",
    "nothing further", "no entries", "not applicable", "n/a",
    "nil", "empty",
    "no blockers", "no blocking items", "blocks nothing",
    "none whatsoever", "nothing else whatsoever",
    "no item at all", "not a single item",
    "zero items", "0", "0 items", "no one", "nothing pending",
    "no blocks", "none pending", "nothing to block",
    "no further entries", "nothing more", "none more",
    "no items at all", "empty list", "blank", "void",
    "does not block anything", "no", "nothing in particular",
    "n.a",
    "nothing blocked", "no outstanding items", "zero blockers",
    "0 blockers", "unblocked", "clear", "blocks no entry",
    "does not block any entry", "no entry blocked", "nought",
    "zip", "none recorded", "nothing recorded",
    "no blocks recorded", "not blocking", "non-blocking",
    "none at present", "nothing outstanding",
    "no pending entries", "nothing hinders", "free", "vacant",
    "zilch", "nada", "no blockage", "unobstructed",
    "nothing obstructs", "no obstruction",
    "nothing is blocked", "zero entries blocked",
    "no item blocks", "does not block", "all clear",
    "no impediments", "nothing impedes", "free of blockers",
    "blocked by none", "no entries blocked",
    "no blocking entries", "nothing blocks anything",
    "0 entries", "zero entries",
    "blocks no item", "blocks no items", "no item blocked",
    "no items blocked", "does not block any item",
    "not blocking anything", "no obstacles",
    "free of obstacles", "unimpeded",
    "nothing stands in the way", "no roadblocks",
    "no hindrances", "zero blocked", "0 blocked",
    "not a single entry", "nothing holds", "no holds",
    "does not impede", "empty set",
    "blocks no entries", "no entry is blocked",
    "nothing in the way", "zero items blocked",
    "0 items blocked", "does not hinder",
    "does not obstruct", "impedes nothing",
    "free of hindrances", "free of roadblocks",
    "not a single blocker", "no blocker",
    "blocks zero entries", "nothing is holding",
    "the list is empty", "no blocking at all",
    "holds nothing", "obstructs nothing",
    "no items are blocked", "blocks not one item",
    "0 entries blocked", "blocks zero items",
    "blocks not a single item",
    "not a single item blocked",
    "not one item is blocked", "no item is blocked",
    "hinders nothing", "holds up nothing",
    "free of obstructions", "no hindrance",
    "no roadblock", "nothing blocks",
    "is not blocking", "the way is clear",
    "blocks no questions", "blocks no decisions",
    "no question is blocked", "path is clear",
    "clear of blockers",
})


def _blocks_names_an_item(blocks):
    """Whether a Blocks field value names at least one item,
    under OP-Q12 as corrected (Step 17 round 2 charge CH-10,
    A2-10-F2, widened at round 3 charge CH-43, A3-10-F1).
    The value is read in its ordinary sentence
    form: case does not matter, ordinary sentence punctuation
    closing the value or a part of it (a full stop, an
    exclamation mark, a space before the closing mark) does
    not matter, and a value
    made of parts joined by commas, by semicolons, by and,
    by or, or by an ampersand names an item
    only where at least one part stands outside the no item
    values (none, nothing, nothing else, nothing else at
    all, no items, and the round 3 phrases nothing at all,
    none at all, nothing whatsoever, nothing further,
    no entries, not applicable, n/a, nil, and empty). A value naming a real reference beside
    a no item part, DQ-002, none among them, names that
    reference and counts. The corpus form nothing named.
    stands outside this set by the Fix C3 bound recorded at
    observation O4 of the seat 10 round 2 paper, and keeps
    its standing treatment: it is not a no item value here.
    One exact form stands apart from the sentence form
    reading, on the same Fix C3 bound: a part that is
    exactly the word nothing with its full stop, in any
    case, is one of the value forms that paper records as
    standing in the corpus and in the restart pins and
    keeping their standing treatment, and the CH-10 charge
    as prepared names the bare word nothing and the cured
    values with a full stop added, not that form. Such a
    part therefore names an item and counts, as the
    governed Step 15 pin for the unit carrying the value
    Nothing. records (fix wave 2 closing, Defect Repair
    Seat D2 narrowing).
    The reading widened again at round 4 charge CH-66
    (A4-10-F1), around the same two bounds and not through
    them: the no item set gains the further phrases the
    round 4 finding names (no blockers, blocks nothing,
    nothing in particular, and their fellows), zero stated
    as a count (0, 0 items, and zero items, the digit in
    its ASCII form only, as the digit ground states), a
    part standing inside a wrapper of parentheses is read
    by its wrapped words, a part joined by a slash, by a
    plus sign, or by a colon is read by its joined parts
    (the whole part reading stands first, so the cured
    abbreviation n/a keeps its set reading and is never
    re-read as two parts), and the dotted abbreviation
    n.a. is read as the cured value it abbreviates.
    The reading widened again at round 5 charge CH-86
    (A5-10-F1), around the same two bounds: the no item set
    gains the further phrases the round 5 finding names
    (nothing blocked, zero blockers, none recorded, and
    their fellows), a part standing inside a bracket, brace,
    quote, or asterisk wrapper is read by its wrapped words
    as the parenthesis form is, and a part joined by a pipe,
    by a backslash, or by a tilde is read by its joined
    parts as the slash, plus, and colon forms are.
    The reading widened again at round 7 charge CH-146
    (A7-10-F1), around the same two bounds: the no item set
    gains the further phrases the round 7 finding names
    (blocks no item, no obstacles, zero blocked, and their
    fellows, zero stated against the word blocked and the
    word entry standing in the not a single form among
    them), a part standing inside a backtick, guillemet, or
    curly quote wrapper is read by its wrapped words as
    the standing wrappers are, and a part joined by a full
    stop, by an underscore, by an em dash, by an en dash,
    or by a bullet mark is read by its joined parts as the
    slash, plus, and colon forms are. The D2 exact form
    stands first in the part reading and is untouched by
    the full stop joiner: a part that is exactly the word
    nothing with its full stop names an item before any
    joiner reading is reached.
    The reading widened again at round 8 charge CH-162
    (A8-10-F1), around the same two bounds: the no item set
    gains the further phrases the round 8 finding names
    (blocks no entries, nothing in the way, zero items
    blocked, and their fellows, the plural entries standing
    where the set read the singular entry forms, the hinder
    and obstruct verb families standing where the impede
    forms stood, and the object first word order standing
    where the subject first order stood among them), a part
    standing inside a single guillemet, low quote, or
    corner bracket wrapper is read by its wrapped words as
    the standing wrappers are, and a part joined by a plain
    space, by a percent sign, by a caret, by a dollar sign,
    by a question mark, or by a section sign is read by its
    joined parts as the slash, plus, and colon forms are.
    The whole part reading stands first, so a multi word
    phrase standing in the set keeps its set reading and is
    never re-read as its words, and a value naming a real
    reference beside a no item part still counts. The D2
    exact form stands first in the part reading and is
    untouched by the space and question mark joiners.
    The reading widened again at round 9 charge CH-197
    (A9-10-F1, with the seat 12 observation O-9-12-4
    members), around the same two bounds: the no item
    set gains the further phrases the round 9 finding
    names (0 entries blocked, blocks zero items, the
    single item negations, hinders nothing, holds up
    nothing, free of obstructions, no hindrance, no
    roadblock, nothing blocks, is not blocking, the
    way is clear, and the seat 12 members blocks no
    questions, blocks no decisions, no question is
    blocked, path is clear, and clear of blockers), a
    part joined by an exclamation mark is read by its
    joined parts as the slash, plus, and colon forms
    are, and a part standing inside the one mismatched
    wrapper pair the seat 12 member names, an opening
    parenthesis closed by a closing bracket, is read
    by its wrapped words as the standing wrappers are.
    No other mismatched wrapper pair stands in this
    cure. The whole part reading stands first, and the
    D2 exact form stands first in the part reading and
    is untouched by the exclamation joiner.
    """
    value = (blocks or "").strip().lower()
    if not value:
        return False
    parts = []
    for chunk in re.split(r"[,;]", value):
        for part in re.split(r"\s+(?:and|or)\s+|\s*&\s*", chunk):
            part = part.strip()
            if part:
                parts.append(part)
    if not parts:
        return False
    return any(_blocks_part_names_an_item(part) for part in parts)


def _blocks_part_names_an_item(part):
    """Whether one part of a Blocks value names an item, in
    the reading _blocks_names_an_item states. The D2 exact
    form stands first and untouched: a part that is exactly
    the word nothing with its full stop, in any case, names
    an item. The part is then read under ordinary sentence
    punctuation and, where it stands inside a wrapper of
    parentheses, by its wrapped words. A read part standing
    in the no item set names no item. A part joined by a
    slash, by a plus sign, or by a colon names an item only
    where at least one of its joined parts names one, each
    joined part read in this same form; a part in none of
    these forms and outside the set names an item."""
    if part == "nothing.":
        return True
    read = re.sub(r"[\s.!?]+$", "", part)
    # A part standing inside a wrapper is read by its
    # wrapped words (round 4 charge CH-66 for the
    # parenthesis wrapper; round 5 charge CH-86, A5-10-F1,
    # for the bracket, brace, quote, and asterisk wrappers
    # beside it).
    wrapper_pairs = (("(", ")"), ("[", "]"), ("{", "}"),
                     ('"', '"'), ("'", "'"), ("<", ">"),
                     ("`", "`"), ("\u00ab", "\u00bb"),
                     ("\u201c", "\u201d"),
                     ("\u2018", "\u2019"),
                     ("\u2039", "\u203a"),
                     ("\u201e", "\u201c"),
                     ("\u300c", "\u300d"),
                     ("(", "]"))
    changed = True
    while changed and len(read) >= 2:
        changed = False
        for opening, closing in wrapper_pairs:
            if read.startswith(opening) and \
                    read.endswith(closing):
                read = re.sub(
                    r"[\s.!?]+$", "", read[1:-1].strip())
                changed = True
                break
        if not changed and read.startswith("*") and \
                read.endswith("*"):
            read = re.sub(
                r"[\s.!?]+$", "", read.strip("*").strip())
            changed = True
        if not changed and read.startswith("_") and \
                read.endswith("_"):
            # An underscore wrapper stands beside the
            # asterisk wrapper (round 6 charge CH-105,
            # A6-10-F1, the _none_ form).
            read = re.sub(
                r"[\s.!?]+$", "", read.strip("_").strip())
            changed = True
    if read in _BLOCKS_NO_ITEM_VALUES:
        return False
    joined = re.split(r"\s*[/+:|~\\=@#\-._!"
                      r"\u2014\u2013\u2022%^$?\u00a7]\s*"
                      r"|\s+", read)
    if len(joined) > 1:
        return any(
            _blocks_part_names_an_item(sub)
            for sub in joined if sub)
    return True


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
    _apply_vocabulary_translation(entries, vocabulary)

    derived_list = []
    for entry in entries:
        derived = _derive(entry)
        derived_list.append(derived)
    # D-08: validate sets the two validate owned fields of the
    # Status bearing element shape, at plan Item 3, section 3.5,
    # fields 8 and 9. The determining flag stands on the one
    # determining element of the entry, and the underlying state
    # without condition stands on every element that carries a
    # stated condition, computed by validate only.
    for entry, derived in zip(entries, derived_list):
        elements = list(_get(entry, "status_elements") or [])
        determining = derived.get("determining")
        for element in elements:
            try:
                element.determining_flag = element is determining
            except Exception:
                continue
            if _get(element, "condition") is not None:
                try:
                    element.underlying_state_without_condition = (
                        _underlying_state(entry, element, elements))
                except Exception:
                    pass
    derived_by_id = {}
    derived_lists = {}
    for entry, derived in zip(entries, derived_list):
        derived_by_id[_display_id(entry)] = derived
        derived_lists.setdefault(_display_id(entry), []).append(
            derived)

    entry_results = []
    for entry, derived in zip(entries, derived_list):
        elements = list(_get(entry, "status_elements") or [])
        open_fields = {}
        for f in _get(entry, "fields") or []:
            open_fields[_get(f, "label")] = _get(f, "value") or ""
        if "Options" in open_fields and not open_fields["Options"]:
            # The Options label can stand alone with its option
            # lines as the following body lines (fixture S5's
            # shape). The field's value is then empty, and the
            # render form printed "Options: absent" for an entry
            # carrying two option lines, against brief sections
            # 5.5 and 6.1 (one computation, two views). The
            # options fact is computed here, once: the option
            # lines under the label are the field's value.
            collected = []
            collecting = False
            for _line, text in _body_lines(entry):
                stripped = (text or "").strip()
                if stripped.startswith("Options:"):
                    collecting = True
                    rest = stripped[len("Options:"):].strip()
                    if rest:
                        collected.append(rest)
                    continue
                if collecting:
                    if stripped.startswith("- "):
                        collected.append(stripped)
                    elif stripped:
                        break
            if collected:
                open_fields["Options"] = " ".join(collected)
        head = _head_element(entry)
        state = derived["state"]
        if derived["unparsed"]:
            state = None
        result = EntryResult(
            identifier=(_display_id(entry)
                        if _get(entry, "identifier") is not None
                        else ("R-7" if _display_id(entry) == "R-7"
                              else None)),
            heading=_get(entry, "heading")
            or _get(entry, "heading_text") or "",
            title=_get(entry, "title") or "",
            date=_get(entry, "date_text"),
            effective_state=state,
            sub_label=derived["sub_label"],
            determining_element=derived["determining"],
            competing_elements=list(derived["competing"]),
            element_summary=[
                # Brief section 5.5: the ordered element summary
                # carries kind, line number, and the verbatim value
                # in full; the disposition stands after it.
                "line %s: %s: %s: %s" % (
                    e.line, e.kind, e.verbatim, e.disposition)
                if e.verbatim else
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
        result.listing_decider_label = derived.get(
            "listing_decider_label")
        # Derived fields the plan shapes carry beside the declared
        # EntryResult fields (plan Item 3, section 3.4): the
        # underlying state, the remainder texts as a list, the
        # denoted states of the competing elements under PIN-07,
        # the presence test results under PIN-08, and the
        # supersession pointers under PIN-10, filled in below once
        # the supersession unit has run.
        result.underlying_state = derived.get("underlying_state")
        result.remainder_texts = list(derived.get("remainder_texts")
                                      or [])
        result.denoted_states = list(derived.get("denoted_states")
                                     or [])
        result.competing_pair = list(derived["competing"])
        result.presence_results = derived.get("presence_results")
        result.supersession_pointers = []
        # The Ambiguous reporting form stands in its own carrier
        # on the result, apart from the effective state field, at
        # plan Item 3, section 3.4, field 6.
        result.reporting_form = (
            "Ambiguous" if derived["state"] == "Ambiguous" else None)
        entry_results.append(result)

    (sup_pointers, sup_findings, sup_chains,
     _sup_cycles, sup_map_over_bound,
     sup_cycle_over_bound, sup_work_over_bound,
     sup_work_measured) = _supersession_unit(
        model, entries, derived_list)
    for entry, result in zip(entries, entry_results):
        result.supersession_pointers = list(
            sup_pointers.get(_display_id(entry), []))
    # D-07: validate fills the derived fields on the Entry itself,
    # at plan Item 3, section 3.4. The three outcome carriers
    # stand separate: the derived effective state holds a
    # canonical state or nothing, the reporting form holds the
    # Ambiguous reporting form or nothing, and the unparsed
    # marker stands as parse left it. The remainder texts stand
    # as a list, one text per remainder a part disposition names,
    # in element order. Entry values handed to validate as plain
    # mappings, as on a model double, carry no fields to fill and
    # are passed over.
    for entry, derived in zip(entries, derived_list):
        if isinstance(entry, dict):
            continue
        elements = list(_get(entry, "status_elements") or [])
        state = derived["state"]
        try:
            entry.effective_state = (
                state if state in CANONICAL_STATES else None)
            entry.reporting_form = (
                "Ambiguous" if state == "Ambiguous" else None)
            entry.decider_label = derived.get("decider_label")
            entry.condition_text = derived.get("condition")
            collected_remainders = []
            for element in derived.get("effective_elements") or []:
                if (_get(element, "scope") or "").startswith("Part") \
                        or _scope_of(element, entry).startswith("Part"):
                    text = _part_remainder(entry, element)
                    if text:
                        collected_remainders.append(text)
            if not collected_remainders:
                collected_remainders = list(
                    derived.get("remainder_texts") or [])
            entry.remainder_texts = collected_remainders
            entry.supersession_pointers = list(
                sup_pointers.get(_display_id(entry), []))
            entry.underlying_state = derived.get("underlying_state")
            if _pin12_shape(entry, elements,
                            derived.get("effective_elements") or []):
                note = None
                for _line, text in _body_lines(entry):
                    if any(pattern.search(text or "")
                           for pattern in _PIN12_PROSE_PATTERNS):
                        note = (text or "").strip()
                        break
                entry.internal_undecided_note = note
        except Exception:
            pass
    companion_count = 0
    for entry, derived in zip(entries, derived_list):
        display = _display_id(entry)
        if (derived.get("remainder") or derived.get("remainder_texts")) \
                and sup_pointers.get(display):
            companion_count += 1

    file_findings = []
    file_findings.extend(_check1(entries, model))
    file_findings.extend(_unmatched_heading_findings(model))
    file_findings.extend(
        _absorbed_h4_entry_heading_findings(entries))
    file_findings.extend(_segment_claim_findings(model, entries))
    check6_findings = _check6(model, entries)
    # The whole file assignment finding of check 6 is the one
    # check 6 finding that stands at file level; it is told apart
    # by its basis, because a file level finding now carries its
    # unit identifier and not the literal FILE.
    file_findings.extend(
        f for f in check6_findings
        if f.basis == "lines assigned to no unit or to two units")
    file_findings.sort(key=_file_order_key)

    entry_findings = []
    entry_findings.extend(
        f for f in check6_findings
        if f.basis != "lines assigned to no unit or to two units")
    # The headed number set is the same set for every entry of
    # the run: it is built once, before the per entry loop, and
    # handed to each _check5 call unchanged. Building it inside
    # the loop rebuilt the full set once per entry, a quadratic
    # term on every file (Step 17, CH-11: seat 5 Finding 1 limb
    # two and A2-21-1).
    headed_numbers = {number for number in
                      (_entry_number(other) for other in entries)
                      if number is not None}
    for entry, derived in zip(entries, derived_list):
        display_id = _display_id(entry)
        elements = list(_get(entry, "status_elements") or [])
        if derived["unparsed"]:
            entry_findings.append(_unparsed_finding(entry, display_id))
        entry_findings.extend(_check2(entry, display_id))
        entry_findings.extend(_check3(entry, display_id, derived,
                                      elements))
        entry_findings.extend(_check4(entry, display_id, derived))
        entry_findings.extend(_check5(
            entry, display_id, derived, elements,
            headed_numbers=headed_numbers))
        entry_findings.extend(_check9(entry, display_id, derived))
        entry_findings.extend(_check9_field_conflicts(
            entry, display_id, derived))
        entry_findings.extend(_check10(entry, display_id, derived))
        if len(entries) == 1 and derived.get("shape_a"):
            # An unclassified status value takes its Note
            # finding, brief section 5.4 (Step 17 charge
            # S17-ATK7-05, worded on its own construction only:
            # a lone entry whose only status element carries a
            # value no vocabulary class holds, deriving Open
            # under the Shape A exception). The multi entry
            # unclassified constructions stand outside this
            # charge; A12-F5 in particular stands CONFIRMED
            # ONLY and is cured by no part of this limb.
            sole = derived.get("determining")
            if sole is not None and sole.disposition is None:
                entry_findings.append(_finding(
                    "PIN-04", "Note", display_id,
                    Span(sole.line, sole.line),
                    sole.verbatim or sole.statement or "",
                    "The status value of this entry is an "
                    "unclassified status value: \"%s\" stands "
                    "in no class of the vocabulary, and the "
                    "entry derives Open under the Shape A "
                    "exception for an untranslatable sole "
                    "status element."
                    % (sole.verbatim or sole.statement or ""),
                    basis="an unclassified status value"))
    entry_findings.extend(_check8(model, entries, derived_by_id,
                                  derived_lists, derived_list))
    entry_findings.extend(sup_findings)
    for result, derived in zip(entry_results, derived_list):
        result.presence_results = derived.get("presence_results")

    entry_index = {}
    for index, entry in enumerate(entries):
        entry_index[_display_id(entry)] = index

    def entry_order_key(finding):
        index = entry_index.get(finding.entry_identifier, len(entries))
        span = finding.line_span
        line = span.start_line if span is not None else 0
        return (index, _rule_order_key(finding.rule_id), line)

    entry_findings.sort(key=entry_order_key)
    findings = _combine_pd_r7_statement_notes(
        file_findings + entry_findings)

    banked_cut_ids = _banked_cut_entry_ids(model, entries)
    banked_fence_ids = _banked_fence_entry_ids(model, entries)
    census = _census(entries, derived_list, banked_cut_ids,
                     banked_fence_ids)

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

    appendix_rows = _appendix_rows(entries, vocabulary, model)
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

    # The reconciliation components, in the contract order at
    # plan Item 3, section 3.8, in the footing order testing pin
    # down 11 fixes: one, population footing; two, canonical
    # footing; three, verbatim footing; four, component footing;
    # five, whole file assignment. Component six, render
    # agreement, stands as a component of the field but is not
    # summed by the in run self check and is evaluated only
    # externally after both subcommand outputs exist (plan Item
    # 1, section 1.7).
    failed_components = []
    component_failures = {1: [], 2: [], 3: [], 4: [], 5: []}

    def fail(component, text):
        component_failures[component].append(text)
        failed_components.append(text)

    # Component 1, population footing: the headed entry total and
    # the DQ entry total against the File shape lists. Both
    # stated totals are checked: the headed total against the
    # parse owned entry unit count where a carrier records one,
    # and the DQ entry total against the File number ledger,
    # whose values hold one list entry per headed entry carrying
    # that number.
    unit_counts = _get(header_facts, "unit_counts") or {}
    parse_entry_units = unit_counts.get("entry")
    if parse_entry_units is not None and parse_entry_units != entry_total:
        fail(1, "population footing: the entry list holds %d "
                "entries and the parse owned count records %d "
                "entry units" % (entry_total, parse_entry_units))
    # The DQ entry total counts DQ numbered entries only, in
    # the D-06 distinction _is_dq_numbered states: the named
    # unnumbered entry carries the literal heading text as its
    # identifier and stands in the unnumbered count, never in
    # this total, which is the total the File number ledger
    # keys on DQ numbers alone.
    dq_entry_count = sum(1 for e in entries
                         if _is_dq_numbered(e))
    number_ledger = _get(model, "number_ledger")
    if number_ledger is not None:
        ledger_total = 0
        for holders in number_ledger.values():
            if isinstance(holders, (list, tuple)):
                ledger_total += len(holders)
            else:
                ledger_total += 1
        if ledger_total != dq_entry_count:
            fail(1, "population footing: the DQ entry total is %d "
                    "against %d entries in the File number ledger"
                    % (dq_entry_count, ledger_total))
    # Component 2, canonical footing: the eight canonical counts
    # plus the Ambiguous reporting count plus the unparsed entry
    # count against the headed entry total.
    canonical_sum = sum(canonical_counts.values())
    if canonical_sum + ambiguous_count + unparsed_count != entry_total:
        fail(2, "canonical footing: the canonical rows sum to %d, "
                "the Ambiguous count is %d and the unparsed count "
                "is %d, against an entry total of %d"
                % (canonical_sum, ambiguous_count, unparsed_count,
                   entry_total))
    # Component 3, verbatim footing: the appendix occurrence
    # counts against the reported occurrence total.
    recounted_occurrences = 0
    for entry in entries:
        for element in _get(entry, "status_elements") or []:
            if element.occurrence_kind is not None:
                recounted_occurrences += 1
        for element in _get(entry, "occurrence_only_elements") \
                or []:
            if element.occurrence_kind is not None:
                recounted_occurrences += 1
    # The recount carries the same file header unit occurrences
    # the appendix rows carry, so the paired totals foot on the
    # same population (Step 17, S17-ATK7-03).
    recounted_occurrences += len(_preamble_status_occurrences(model))
    if recounted_occurrences != occurrence_total:
        fail(3, "verbatim footing: the verbatim appendix rows sum "
                "to %d and the elements counted directly give %d"
                % (occurrence_total, recounted_occurrences))
    # Component 4, component footing: every printed total
    # recomputed from its printed components, which includes the
    # findings views, the census group footing, and the crosswalk
    # footing. The census group footing: the Banked head evidence
    # groups sum against the Banked head population. A Banked
    # head entry carrying none of the three evidence forms stands
    # in no group, the footing fails, and the run takes the exit
    # 4 tool inconsistency outcome with no finding against the
    # file (plan Item 3, section 3.8). The population here is the
    # census population of _banked_evidence_groups, with its
    # bound for an entry cut by an unmatched heading and its
    # bound for an entry whose own body carries the opening
    # line of a fence standing open at the end of its body
    # (charge CH-189).
    if sum(findings_per_severity.values()) != len(findings):
        fail(4, "component footing: the severity view sums to %d "
                "against a findings list of %d"
                % (sum(findings_per_severity.values()), len(findings)))
    if sum(findings_per_rule.values()) != len(findings):
        fail(4, "component footing: the rule view sums to %d "
                "against a findings list of %d"
                % (sum(findings_per_rule.values()), len(findings)))
    census_population, census_groups = _banked_evidence_groups(
        entries, derived_list, banked_cut_ids, banked_fence_ids)
    census_group_total = sum(len(members)
                             for _name, members in census_groups)
    census_footing_holds = (
        census_group_total == len(census_population))
    if not census_footing_holds:
        fail(4, "component footing: the Banked head evidence "
                "groups sum to %d against a Banked head population "
                "of %d" % (census_group_total, len(census_population)))
    # The crosswalk footing, a part of component footing: the
    # Banked head crosswalk total against the count of entries
    # carrying the Banked head phrasing.
    crosswalk_counts = _crosswalk(entries, derived_list, vocabulary)
    banked_head_population = sum(
        1 for e, d in zip(entries, derived_list)
        if not d.get("unparsed")
        and _head_element(e) is not None
        and _head_element(e).verbatim == "Banked")
    banked_crosswalk_total = (
        crosswalk_counts.get("Banked", {}).get("total", 0))
    crosswalk_footing_holds = (
        banked_crosswalk_total == banked_head_population)
    if not crosswalk_footing_holds:
        fail(4, "component footing: the Banked head crosswalk "
                "total is %d against %d entries carrying the Banked "
                "head phrasing"
                % (banked_crosswalk_total, banked_head_population))
    # Component 5, whole file assignment: every line assigned to
    # exactly one unit or listed as unassigned. A line assigned
    # to no unit, or to two units, fails this component, and the
    # condition stands as a self check failure beside its check 6
    # finding form.
    unassigned_lines = list(_get(model, "unassigned_lines") or [])
    double_assigned_lines = list(
        _get(model, "double_assigned_lines") or [])
    whole_file_assignment_holds = not (
        unassigned_lines or double_assigned_lines)
    if not whole_file_assignment_holds:
        fail(5, "whole file assignment: %d lines assigned to no "
                "unit and %d lines assigned to two units"
                % (len(unassigned_lines), len(double_assigned_lines)))
    self_check = SelfCheckResult(
        sums_agree=not failed_components,
        failed_components=failed_components)
    if failed_components:
        # On a self check failure the run is a tool inconsistency
        # and no finding stands against the file: the findings
        # list is withheld in full, in the model as on the printed
        # surface (plan Item 9, section 9.7, OP-Q5). The findings
        # views in the reconciliation above were computed from the
        # list as assembled, which is what component footing
        # checks.
        findings = []
    # The in run self check components, components 1 to 5 only,
    # in the contract order and under the contract names.
    component_results = [
        {"component": 1, "name": "population footing",
         "holds": not component_failures[1]},
        {"component": 2, "name": "canonical footing",
         "holds": not component_failures[2]},
        {"component": 3, "name": "verbatim footing",
         "holds": not component_failures[3]},
        {"component": 4, "name": "component footing",
         "holds": not component_failures[4]},
        {"component": 5, "name": "whole file assignment",
         "holds": whole_file_assignment_holds},
    ]

    reconciliation = ReconciliationBlock(
        entry_total=HeadedEntryCount(entry_total),
        dq_entry_count=dq_entry_count,
        unnumbered_entry_count=sum(1 for e in entries
                                   if not _is_dq_numbered(e)),
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
        if derived["state"] in DECIDED_OUTCOMES and result.decider_label:
            decider_subtotals[result.decider_label] = (
                decider_subtotals.get(result.decider_label, 0) + 1)

    # The waiting figure (OP-Q12, plan Item 3, section 3.8):
    # distinct entries that are effectively open, or Settled in
    # part with at least one named remainder, or whose determining
    # element takes Closed as decided for a part with at least one
    # standing remainder. A part closed entry is counted once and
    # never also as effectively open.
    waiting_ids = []
    for entry, derived in zip(entries, derived_list):
        display = _display_id(entry)
        state = derived["state"]
        if state in _EFFECTIVELY_OPEN_STATES:
            waiting_ids.append(display)
        elif state == "Settled in part" and derived.get("remainder"):
            waiting_ids.append(display)
        elif state == "Closed as decided" \
                and derived.get("remainder") \
                and derived["determining"] is not None \
                and "part" in (derived["determining"].scope or "").lower():
            waiting_ids.append(display)
    # The figure counts entries, as every other count in this
    # report does: two headed entries that happen to carry the
    # same written identifier are two entries, and the list
    # above holds one identifier per qualifying entry, so its
    # length is the figure (Step 17, Finding 2 of seat 6 merged
    # with A10-F3).
    waiting = len(waiting_ids)
    open_results = [(e, r) for e, r, d in zip(
        entries, entry_results, derived_list)
        if d["state"] in _EFFECTIVELY_OPEN_STATES]
    blocking = 0
    blocking_list = []
    for entry, result in open_results:
        # The blocks value is read under the one selection
        # rule stated at _first_family_value (Step 17 round 4
        # charge CH-59): the first occurrence in file order
        # governs, for a repeated label and for the alias pair
        # alike, where the label priority reading this replaces
        # took the naming label's value in both orders.
        blocks = _first_family_value(entry, _BLOCKS_LABELS)
        # An entry counts in the blocking figure only where its
        # blocks field names at least one item, under OP-Q12 as
        # corrected: a blocks field whose whole value is one of
        # the no item values names no item and does not count
        # (Step 17, A10-F2, widened at round 2 charge CH-10,
        # A2-10-F2, in _blocks_names_an_item).
        if blocks and _blocks_names_an_item(blocks):
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
        labels = _field_labels(entry)
        if "What it blocks" in labels or "Blocks" in labels:
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

    # No Exit decision is formed here: the field stands
    # unsupplied in the output below, for shell to supply at run
    # time, under the supply point at plan Item 3, section 3.7.

    fired_rules = sorted({f.rule_id for f in findings},
                         key=_rule_order_key)
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

    # The file facts measurements stand on the File shape fields
    # of the model itself, at plan Item 3, section 3.2; the header
    # facts value is one verbatim text field and carries no
    # measurement. A carrier that still records a measurement on
    # the header facts value, as a model double does, stands as
    # the fallback. Validate writes nothing into the parse owned
    # model: the vocabulary version in force stands on the
    # Validate output alone, at its vocabulary_version field.
    def _measured(name, default):
        value = _get(model, name)
        if value is None:
            value = _get(header_facts, name)
        return default if value is None else value

    file_facts = FileFactsData(
        input_name=_measured("input_name", ""),
        byte_count=_measured("byte_count", 0),
        line_count=_measured("line_count", 0),
        entry_count=HeadedEntryCount(entry_total),
        digest=_measured("digest", ""),
        source_designation=_get(model, "source_designation")
        or "live")

    limits = _get(header_facts, "limits")
    if limits is None:
        from .types import Limits
        limits = Limits()

    segment_claim_reports = []
    for segment in _get(model, "orphan_segments") or []:
        claims = list(_get(segment, "claims") or [])
        report_q_line = _quarantined_heading_line(
            segment, _get(segment, "span"))
        report_heading_text = None
        if report_q_line is not None:
            for _ln, _lt in (_get(segment, "lines") or []):
                if _ln == report_q_line:
                    report_heading_text = _lt
                    break
        claims = [c for c in claims
                  if report_heading_text is None
                  or (_get(c, "statement") or "") != report_heading_text]
        for claim in claims:
            segment_claim_reports.append({
                "segment_heading": _get(segment, "heading_text") or "",
                "statement": _get(claim, "statement") or "",
                "named_entries": list(
                    _get(claim, "named_entries") or []),
                "reported_as": "claim",
            })
        if claims:
            continue
        # A segment carrying no parse level claim can still carry
        # a claim the findings scan recognises in plain prose, in
        # the fallback form _segment_claim_findings applies for
        # the PIN-09 findings of the same segment. The reports
        # carry those claims on the same terms as the findings:
        # one report per named entry where a line names one
        # claim target, and, where a line names more than one,
        # one combined report for the line naming every fresh
        # target it carries and carrying the line once as its
        # statement (Step 17 round 6, CH-98, the combining of
        # the claim print reaching the Segment claims section
        # the reports feed), so the Segment claims section of
        # both outputs stands for every claim the findings
        # report and no claim the findings recognise is dropped
        # from the render output, which prints no findings list.
        seen_reported = set()
        report_quarantined_line = _quarantined_heading_line(
            segment, _get(segment, "span"))
        for _line_number, text in (_get(segment, "lines") or []):
            if report_quarantined_line is not None and \
                    _line_number == report_quarantined_line:
                continue
            fresh_reported = []
            for match in _guarded_segment_claim_matches(text):
                target = "DQ-%03d" % int(match.group(1))
                if target in seen_reported:
                    continue
                seen_reported.add(target)
                fresh_reported.append(target)
            if not fresh_reported:
                continue
            segment_claim_reports.append({
                "segment_heading":
                    _get(segment, "heading_text") or "",
                "statement": text or "",
                "named_entries": fresh_reported,
                "reported_as": "claim",
            })

    # The residue list, in the ResidueItem contract form at plan
    # Item 3, section 3.6: one item per untranslatable phrasing
    # per entry carrying it, with the phrasing as written, the
    # identifier of the entry that carries it in the singular
    # field, and its line span. An item is never forced to a
    # nearest state and never assigned a canonical state.
    # The carrying elements stand gathered once, before the
    # row loop (Step 17 round 7, CH-151): for each entry, its
    # display identifier stands read once and its first
    # status element of each phrasing and kind stands in a
    # map, indexed by the display identifier in file order.
    # The form this replaces read the display identifier of
    # every entry for every row outside the vocabulary
    # mapping and scanned the elements of every member entry
    # row by row, a scan in the square of the entry count
    # where the phrasings stand distinct. Each row now reads
    # only the entries its member list names, through the
    # gathered map, and the items stand in the order the
    # replaced form stood them in: row by row in appendix
    # order, and inside a row in entry file order.
    residue_gathered = {}
    for gather_index, entry in enumerate(entries):
        display = _display_id(entry)
        first_elements = {}
        for element in _get(entry, "status_elements") or []:
            key = (_get(element, "verbatim"),
                   _get(element, "occurrence_kind"))
            if key not in first_elements:
                first_elements[key] = element
        residue_gathered.setdefault(display, []).append(
            (gather_index, first_elements))
    residue_items = []
    for row in appendix_rows:
        if row.phrasing in vocabulary.mapping:
            continue
        matched = []
        for display in row.member_entry_ids:
            for gather_index, first_elements in \
                    residue_gathered.get(display, ()):
                element = first_elements.get(
                    (row.phrasing, row.kind))
                if element is None:
                    continue
                # One phrasing holds one classification
                # across the report (Step 17, A10-F4 merged
                # with F1 of seat 19): where the carrying
                # element holds a disposition, the phrasing
                # stands translated to its canonical family,
                # by the vocabulary mapping in
                # _apply_vocabulary_translation or by a
                # status opening form at parse, and it is
                # not a residue item and is not held as
                # unknown, whatever the value side case or
                # whitespace of the phrasing as written. A
                # phrasing whose element holds no disposition
                # stands untranslated and keeps its item.
                if _get(element, "disposition") is not None:
                    continue
                matched.append((gather_index, ResidueItem(
                    phrasing=row.phrasing,
                    entry_identifier=display,
                    line_span=Span(element.line, element.line))))
        matched.sort(key=lambda pair: pair[0])
        residue_items.extend(item for _index, item in matched)
    residue_phrasings = {item.phrasing for item in residue_items}
    residue_entries = []
    for entry in entries:
        for element in _get(entry, "status_elements") or []:
            if element.verbatim in residue_phrasings:
                residue_entries.append(_display_id(entry))
                break
    # The entry groups in render order, at plan Item 3, section
    # 3.7, field 6, in the full group sequence that section
    # states once: Open; Settled in part; Presented; Parked;
    # Conditional; Ambiguous; Ruled; Settled; Closed as decided;
    # and the unparsed entries last.
    _GROUP_ORDER = (
        "Open", "Settled in part", "Presented", "Parked",
        "Conditional", "Ambiguous", "Ruled", "Settled",
        "Closed as decided", "Unparsed")
    grouped = {name: [] for name in _GROUP_ORDER}
    for result, derived in zip(entry_results, derived_list):
        if derived["unparsed"]:
            grouped["Unparsed"].append(result)
        elif derived["state"] == "Ambiguous":
            grouped["Ambiguous"].append(result)
        elif derived["state"] in grouped:
            grouped[derived["state"]].append(result)
    entry_groups = [
        {"group": name, "name": name, "entries": grouped[name]}
        for name in _GROUP_ORDER if grouped[name]]

    output = ValidateOutput(
        entries=entry_results,
        entry_groups=entry_groups,
        findings=findings,
        census=census,
        reconciliation=reconciliation,
        file_facts=file_facts,
        limits=limits,
        vocabulary_version=vocabulary.version,
        output_form_edition=output_form_edition,
        verbatim_appendix_rows=appendix_rows,
        per_rule_clearing_forms=clearing_forms,
        crosswalk_counts=crosswalk_counts,
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
        # The segment claim reports are a declared field of the
        # Validate output shape (brief section 5.5: the output is
        # the sole validate to render handoff, and every field
        # render prints has its named source inside it). They are
        # handed over at construction, never attached afterwards,
        # so a consumer building an output from the declared
        # fields alone carries the Segment claims section.
        segment_claim_reports=segment_claim_reports,
        fastest_item="not derivable from the file",
        # D-12: the canonical counts by state stand on the model
        # itself, at plan Item 3, section 3.7, field 2, and not
        # only inside the reconciliation block.
        canonical_counts=dict(canonical_counts),
        residue_items=residue_items,
        # D-13: the residue share stands as its exact pair, the
        # numerator in unit entries and the denominator the
        # headed entry count in unit headed entries, carried as
        # that pair and in no rounded form, at plan Item 3,
        # section 3.7, field 9. The field authorises no printing.
        residue_share=(len(residue_entries), entry_total),
        supersession_chains=[list(chain)
                             for chain, _flag in sup_chains],
        # D-14: the counting units key stands populated, naming
        # the unit of every count of this model, in the
        # CountingUnitsKey shape at plan Item 3, section 3.7.
        counting_units=CountingUnitsKey(
            canonical_counts="entries",
            headed_entry_count="headed entries",
            residue_items="residue items",
            supersession_chains="chains",
            waiting="entries",
            blocking="entries"))
    reconciliation.components = component_results
    reconciliation.component_results = component_results
    # The rule set version in force, at plan Item 3, section 3.8:
    # initial value 1, in the unsigned integer text form section
    # 9.11 pins. The declared field for this value on the model
    # stands with the types seat; the value is carried here so
    # the version fields of the run stand complete on the output.
    output.rule_set_version = "1"
    # Appendix aliases: the appendix rows under the names the
    # render model consumers read.
    output.verbatim_appendix = appendix_rows
    output.appendix = appendix_rows
    output.appendix_rows = appendix_rows
    output.residue = residue_items
    output.residue_list = residue_items
    output.residue_entries = residue_entries
    # The supersession map data and the companion count: entries
    # carrying a standing remainder whose entry carries a
    # supersession pointer, carried beside the waiting figure and
    # never merged into it (plan Item 3, section 3.7 field 10).
    output.supersession_chain_records = [
        {"entries": list(chain), "cycle": flag,
         "is_cycle": flag}
        for chain, flag in sup_chains]
    output.companion_count = companion_count
    output.map_over_bound = sup_map_over_bound
    output.supersession_map_over_bound = sup_map_over_bound
    # The cycle count bound flag of the run (Step 17 round 3,
    # CH-32): where the distinct cycle inventory passed the
    # bound during enumeration, this flag stands and shell
    # takes the exit 3 refusal naming the bound, on both
    # subcommands, in place of any output of this run. The
    # measured count stands capped at the bound plus one, the
    # count at which enumeration stopped.
    output.cycle_over_bound = sup_cycle_over_bound
    output.supersession_cycle_over_bound = sup_cycle_over_bound
    output.cycle_count_bound = _CYCLE_COUNT_BOUND
    output.cycle_count_measured = min(
        len(_sup_cycles), _CYCLE_COUNT_CAP)
    # The cycle work bound flag of the run (Step 17 round 4,
    # CH-52): where the enumeration work passed its bound
    # during enumeration, this flag stands and shell takes
    # the exit 3 refusal naming the work limit, on both
    # subcommands, in place of any output of this run. The
    # measured work stands capped at the bound plus one, the
    # count at which enumeration stopped.
    output.cycle_work_over_bound = sup_work_over_bound
    output.supersession_cycle_work_over_bound = sup_work_over_bound
    output.cycle_work_bound = _CYCLE_WORK_BOUND
    output.cycle_work_measured = min(
        sup_work_measured, _CYCLE_WORK_CAP)
    gap_over_bound, gap_naming_size = _gap_refusal_signal(entries)
    output.gap_over_bound = gap_over_bound
    output.gap_naming_over_bound = gap_over_bound
    output.gap_naming_size = gap_naming_size
    # The one gap naming measure of the run, in total form:
    # the single naming size multiplied by the number of
    # printings, the measure _check1 suppresses the gap class
    # on and _gap_refusal_signal sets the flag on. The shell
    # refusal reads this measure from the output, so the
    # Warning and the refusal stand on the one measure at
    # every size (Step 17 round 2, CH-18).
    output.gap_naming_total_size = (
        gap_naming_size * _GAP_NAMING_PRINTINGS)
    output.waiting_entry_ids = sorted(set(waiting_ids))
    return output
