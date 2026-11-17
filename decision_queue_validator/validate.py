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
    match = re.fullmatch(r"DQ-(\d+)", identifier or "")
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
    return text in ("closed.", "closed", "status: closed.")


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
    # in that position as a space does, and the listing
    # steps below each take one whitespace character of the
    # same kinds there (finding A6-8-4). A doubled space
    # stands exactly as it stood: no step here takes it,
    # and the named phrase step below reads past it in the
    # form Fix Seat Q recorded.
    if re.search(r"by[ \t\r\n]Captain JP", body):
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
            r"\b(Ruled|Settled|Decided) by:?[ \t\r\n](the|The) Manager\b",
            body):
        shim = type("ListingShim", (), {})()
        shim.decider = "a Manager grant form"
        shim.decider_text = "The Manager"
        shim.statement = body
        shim.verbatim = ""
        return _decider_label(shim)
    match = re.search(r"\b(Ruled|Settled|Decided) by:?[ \t\r\n]([^.,;]+)",
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
            and (element.scope or "").startswith("Part")
            and _extract_remainder(element)):
        return "Settled in part"
    if disposition in ("Ruled", "Settled", "Closed", "Banked", "Open",
                       "Presented", "Parked") and (
            element.scope or "").startswith("Part"):
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
            and (element.scope or "").startswith("Part")
            and _extract_remainder(element)):
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
    scope = determining.scope or ""
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
        result["remainder"] = _extract_remainder(determining)
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
        if not _extract_remainder(determining):
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
                scope = determining.scope or ""
                condition = _effective_condition(determining)
                if condition:
                    return finish("Conditional")
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
    return (_rule_order_key(finding.rule_id), start, end,
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
    "Man.ager" as "manager" (finding A6-8-1). Where such a
    fragmented attribution word stands and exactly one
    further word carries a content token, and that word is
    a capitalised word, the matter is a name in initials
    form alone, as "J.P. Morgan" is: the capitalised word
    stands as the surname of that name and is set aside
    with it. A word carrying content in any other position
    stands, so genuine ruling matter beside a fragmented
    name still counts, and a name, a number, or a word
    that stands whole and unrecorded still counts as it
    did before.
    """
    tokens = _matter_tokens(text) - _ATTRIBUTION_TOKENS
    words = []
    fragmented = False
    for word in (text or "").split():
        runs = re.findall(r"[a-z0-9]+", word.lower())
        joined = "".join(runs)
        if len(runs) > 1 and joined in _ATTRIBUTION_TOKENS:
            fragmented = True
            tokens.difference_update(runs)
        words.append((word, runs, joined))
    if fragmented:
        others = [(word, runs) for word, runs, joined in words
                  if runs and joined not in _ATTRIBUTION_TOKENS
                  and joined not in _MATTER_STOPWORDS]
        if len(others) == 1:
            word, runs = others[0]
            letters = [char for char in word if char.isalpha()]
            if letters and letters[0].isupper():
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


def _check5(entry, display_id, derived, elements):
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
            if label in ("Ruling text", "Ruling texts", "Settlement"):
                ruling_text = True
                break
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
        for label in labels:
            if (label.startswith("Ruling outcome")
                    or label.startswith("Form outcome")
                    or label == "Decision"
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
                    and not _is_decider_line(statement)
                    and statement.startswith((
                        "Ruled:", "Settled:", "Ruled.", "Settled.",
                        "Closed.", "Closed:"))):
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
                    or label.startswith("Where it landed")
                    or label in ("Landing", "Landing record", "Lands",
                                  "Landed")):
                landing = True
                break
    if not landing:
        for _line, text in _body_lines(entry):
            if re.search(r"\bWhere it landed\b", text or ""):
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
    derived["presence_results"] = {
        "ran": True,
        "decider": bool(decider),
        "ruling_text": bool(ruling_text),
        "outcome": bool(outcome),
        "landing_record": bool(landing),
    }
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
    labels = _field_labels(entry)
    missing = []
    if not any(label in _QUESTION_LABELS
               or label.startswith("Question as put")
               for label in labels):
        missing.append("its question")
    if not _has_options_field(entry):
        missing.append("its options")
    if not any(label in _COST_LABELS for label in labels):
        missing.append("its cost of deciding late")
    if not any(label in _BLOCKS_LABELS for label in labels):
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
    return _finding(
        12, "Error", display_id, span, heading,
        "This entry stands unparsed: its heading stands with no "
        "body, so no state can be determined for it.",
        basis="an unparsed entry, carried under pin 12")


# ---------------------------------------------------------------------
# Unit 3c: whole file checks (checks 1 and 6) and the unmatched
# heading finding
# ---------------------------------------------------------------------

_GAP_NAMING_BOUND = 2000000


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
    digit_total = 0
    for digit_count in range(1, len(str(high)) + 1):
        span_low = 0 if digit_count == 1 else 10 ** (digit_count - 1)
        span_high = 10 ** digit_count - 1
        first = max(low + 1, span_low)
        last = min(high - 1, span_high)
        if last < first:
            continue
        count = last - first + 1
        count -= sum(1 for value in values
                     if low < value < high
                     and len(str(value)) == digit_count)
        digit_total += count * digit_count
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
    numbers = sorted(by_number)
    if numbers:
        gap_size = _gap_naming_size(numbers)
        if gap_size > _GAP_NAMING_BOUND:
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
    return (size > _GAP_NAMING_BOUND, size)


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
                       _unit_identifier(model, segment=segment))

    def claim_finding(claiming_id, target_id, quoted, span):
        derived = derived_by_id.get(target_id)
        if derived is None:
            return None
        state = derived["state"]
        if state == "Ambiguous":
            state_text = "Ambiguous (%s)" % (derived["sub_label"] or "")
        else:
            state_text = str(state)
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

_DQ_TOKEN_RE = re.compile(r"\bDQ-(\d+)\b")

_IDENTIFICATION_PATTERNS = (
    re.compile(r"displaces the rulings? at "
               r"((?:DQ-\d+)(?:\s+and\s+DQ-\d+)*)"),
    re.compile(r"displaces (DQ-\d+)\b"),
    re.compile(r"((?:DQ-\d+)(?:\s+and\s+DQ-\d+)*)\s+"
               r"(?:is|are) the superseded entr"),
    re.compile(r"((?:DQ-\d+)(?:\s+and\s+DQ-\d+)*)\s+"
               r"(?:is|are) the entr\w+ it stands in place of"),
    re.compile(r"replaces ((?:DQ-\d+)(?:\s+and\s+DQ-\d+)*)\s+as\b"),
    re.compile(r"supersedes ((?:DQ-\d+)(?:\s+and\s+DQ-\d+)*)\b"),
    re.compile(r"supersedes\b[^.;]{0,120}?\bat (DQ-\d+)\b"),
)


def _identifications(sentence):
    found = []
    for pattern in _IDENTIFICATION_PATTERNS:
        for match in pattern.finditer(sentence):
            for token in _DQ_TOKEN_RE.finditer(match.group(1)):
                found.append((match.start(1) + token.start(),
                              "DQ-%03d" % int(token.group(1))))
    found.sort()
    ordered = []
    for _pos, entry_id in found:
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


def _first_limb(sentence):
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


_MAP_SIZE_BOUND = 2000000
_MAP_SIZE_CAP = 2000001
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

    reachable = {}

    def reach_set(start):
        if start in reachable:
            return reachable[start]
        seen = set()
        stack = [start]
        while stack:
            current = stack.pop()
            for nxt in pointers.get(current, []):
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        reachable[start] = seen
        return seen

    memo = {}

    def continuation(entry, ancestors):
        relevant = frozenset(
            a for a in ancestors if a in reach_set(entry))
        key = (entry, relevant)
        if key in memo:
            return memo[key]
        holders = pointers.get(entry, [])
        if not holders:
            result = (1, min(cap, len(entry) + 1))
            memo[key] = result
            return result
        total_count = 0
        total_chars = 0
        for pointer in holders:
            if pointer == entry or pointer in ancestors:
                contrib_count = 1
                contrib_chars = (len(entry) + sep + len(pointer)
                                 + mark + 1)
            else:
                sub_count, sub_chars = continuation(
                    pointer, ancestors + [entry])
                contrib_count = sub_count
                contrib_chars = (sub_chars
                                 + sub_count * (len(entry) + sep))
            total_count = min(cap, total_count + contrib_count)
            total_chars = min(cap, total_chars + contrib_chars)
            if total_chars >= cap:
                break
        result = (total_count, total_chars)
        memo[key] = result
        return result

    superseding_set = set()
    for holders in pointers.values():
        superseding_set.update(holders)
    starts = [entry_id for entry_id in headed_ids
              if entry_id in pointers
              and entry_id not in superseding_set]
    total = len(_MAP_HEAD_LINE) + 1
    reached_entries = set()
    for start in starts:
        reached_entries.add(start)
        reached_entries.update(reach_set(start))
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
    map_over_bound).

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

    for entry, derived in zip(entries, derived_list):
        if derived.get("unparsed"):
            continue
        self_id = _display_id(entry)
        if self_id not in headed_set:
            continue
        for line_number, text in _body_lines(entry):
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
            for token in _DQ_TOKEN_RE.finditer(unit):
                token_id = "DQ-%03d" % int(token.group(1))
                if token_id != self_id and token_id not in tokens:
                    tokens.append(token_id)
            if not identified and not tokens:
                # A statement identifying no entry takes no Note
                # and gives no pointer: the DQ-161 form.
                continue
            span = Span(line_number, line_number)
            quote = claiming[0]
            if _first_limb(unit) and identified:
                for target in identified:
                    if target == self_id:
                        continue
                    if target in headed_set:
                        holders = pointers.setdefault(target, [])
                        if self_id not in holders:
                            holders.append(self_id)
                            statements[(target, self_id)] = quote
                    else:
                        note_pd_r7(quote, target, span)
                continue
            for target in identified:
                if target not in headed_set and target != self_id:
                    note_pd_r7(quote, target, span)
            named = [t for t in (identified or tokens)
                     if t in headed_set and t != self_id]
            if not named:
                continue
            finding = _finding(
                "PIN-10", "Note", self_id, span, quote,
                "A supersession statement in this entry is not "
                "recognised: it names %s but does not meet both "
                "limbs of the supersession test, so no pointer "
                "stands for it." % ", ".join(named),
                basis="supersession statement not recognised")
            finding.named_entries = list(named)
            findings.append(finding)

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

    def find_cycles(relation, seeds):
        found_cycles = []
        seen_keys = set()

        def follow(start):
            path = [start]
            current = start
            while True:
                next_holders = relation.get(current, [])
                if not next_holders:
                    return
                nxt = next_holders[0]
                if nxt in path:
                    cycle = path[path.index(nxt):]
                    pivot = min(
                        range(len(cycle)),
                        key=lambda i: file_order.get(cycle[i], 0))
                    rotated = tuple(cycle[pivot:] + cycle[:pivot])
                    if rotated not in seen_keys:
                        seen_keys.add(rotated)
                        found_cycles.append(list(rotated))
                    return
                if nxt not in headed_set:
                    return
                path.append(nxt)
                current = nxt

        for seed in seeds:
            if seed in relation or seed in pointers:
                follow(seed)
        return found_cycles

    cycles = find_cycles(displaces, headed_ids)
    pointer_cycles = find_cycles(pointers, headed_ids)
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
        return pointers, findings, [], cycles, True

    # Chains for the render map, built from the pointers only.
    superseding_set = set()
    for holders in pointers.values():
        superseding_set.update(holders)

    def extend(chain, pointer):
        new_chain = chain + [pointer]
        if pointer in chain:
            return [(new_chain, True)]
        next_holders = pointers.get(pointer, [])
        if not next_holders:
            return [(new_chain, False)]
        out = []
        for nxt in next_holders:
            out.extend(extend(new_chain, nxt))
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
    return pointers, findings, chains, cycles, False


_SEGMENT_CLAIM_RE = re.compile(
    r"\bDQ-(\d+)\b[^.]{0,90}?\b(was|is|stands|remains|stays|left)\b"
    r"[^.]{0,60}?\b(settled|ruled|closed|banked|open|parked|"
    r"presented)\b", re.IGNORECASE)


def _segment_claim_findings(model, entries):
    findings = []
    headed_set = {_display_id(e) for e in entries}
    for segment in _get(model, "orphan_segments") or []:
        span = _get(segment, "span")
        unit_id = _unit_identifier(model, segment=segment)
        claims = list(_get(segment, "claims") or [])
        if claims:
            for claim in claims:
                statement = _get(claim, "statement") or ""
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
            for line_number, text in (_get(segment, "lines") or []):
                for match in _SEGMENT_CLAIM_RE.finditer(text or ""):
                    target = "DQ-%03d" % int(match.group(1))
                    if target in seen_claims:
                        continue
                    seen_claims.add(target)
                    finding = _finding(
                        "PIN-09", "Note", unit_id,
                        Span(line_number, line_number), text,
                        "A file level note section records a claim "
                        "about %s: \"%s\" The claim is reported as "
                        "a claim and is never applied."
                        % (target, match.group(0)),
                        basis="a governing or state claim by a "
                              "file level note section, PIN-09")
                    finding.named_entries = [target]
                    finding.claiming_unit = unit_id
                    findings.append(finding)
        seen_cited = set()
        for line_number, text in (_get(segment, "lines") or []):
            for token in _DQ_TOKEN_RE.finditer(text or ""):
                target = "DQ-%03d" % int(token.group(1))
                if target in headed_set or target in seen_cited:
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


def _census(entries, derived_list):
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
    population, groups = _banked_evidence_groups(entries, derived_list)
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


def _banked_evidence_groups(entries, derived_list):
    """The Banked head population and its three evidence groups.

    Population: entries whose first line start Status line is the
    exact Banked line. Precedence: an entry with a later Status
    line in the body is in the first group whatever else its body
    carries; an entry with no later Status line and a level 4
    decision block is in the second; an entry with neither, whose
    body carries unheaded paragraphs, is in the third.
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
        later = [e for e in elements
                 if e.occurrence_kind == "line start"
                 and e is not first_line]
        if later:
            group1.append(display)
            continue
        if any(_get(block, "marking_form") == "H4 sub part"
               for block in _get(entry, "decision_blocks") or []):
            # The second group test is for a level 4 decision
            # block only, under plan Item 3, section 3.8 and
            # testing pin down 11: a decision block of any other
            # marking form, a bold supersession segment or an
            # unheaded labelled paragraph among them, is not a
            # level 4 block and places the entry in no group on
            # its own.
            group2.append(display)
            continue
        has_paragraph = False
        for _line, text in _body_lines(entry):
            stripped = (text or "").strip()
            if not stripped or stripped.startswith("#"):
                continue
            if re.match(r"^[A-Z][A-Za-z ]{0,40}:", stripped):
                continue
            has_paragraph = True
            break
        if has_paragraph:
            group3.append(display)
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


def _appendix_rows(entries, vocabulary):
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
    for entry, derived in zip(entries, derived_list):
        derived_by_id[_display_id(entry)] = derived

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
     _sup_cycles, sup_map_over_bound) = _supersession_unit(
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
                if (_get(element, "scope") or "").startswith("Part"):
                    text = _extract_remainder(element)
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
    # file (plan Item 3, section 3.8).
    if sum(findings_per_severity.values()) != len(findings):
        fail(4, "component footing: the severity view sums to %d "
                "against a findings list of %d"
                % (sum(findings_per_severity.values()), len(findings)))
    if sum(findings_per_rule.values()) != len(findings):
        fail(4, "component footing: the rule view sums to %d "
                "against a findings list of %d"
                % (sum(findings_per_rule.values()), len(findings)))
    census_population, census_groups = _banked_evidence_groups(
        entries, derived_list)
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
    waiting = len(set(waiting_ids))
    open_results = [(e, r) for e, r, d in zip(
        entries, entry_results, derived_list)
        if d["state"] in _EFFECTIVELY_OPEN_STATES]
    blocking = 0
    blocking_list = []
    for entry, result in open_results:
        blocks = _field_value(entry, "What it blocks") \
            or _field_value(entry, "Blocks")
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
        # carry those claims on the same terms, one report per
        # named entry, so the Segment claims section of both
        # outputs stands for every claim the findings report and
        # no claim the findings recognise is dropped from the
        # render output, which prints no findings list.
        seen_reported = set()
        for _line_number, text in (_get(segment, "lines") or []):
            for match in _SEGMENT_CLAIM_RE.finditer(text or ""):
                target = "DQ-%03d" % int(match.group(1))
                if target in seen_reported:
                    continue
                seen_reported.add(target)
                segment_claim_reports.append({
                    "segment_heading":
                        _get(segment, "heading_text") or "",
                    "statement": text or "",
                    "named_entries": [target],
                    "reported_as": "claim",
                })

    # The residue list, in the ResidueItem contract form at plan
    # Item 3, section 3.6: one item per untranslatable phrasing
    # per entry carrying it, with the phrasing as written, the
    # identifier of the entry that carries it in the singular
    # field, and its line span. An item is never forced to a
    # nearest state and never assigned a canonical state.
    residue_items = []
    for row in appendix_rows:
        if row.phrasing in vocabulary.mapping:
            continue
        for entry in entries:
            display = _display_id(entry)
            if display not in row.member_entry_ids:
                continue
            for element in _get(entry, "status_elements") or []:
                if element.verbatim == row.phrasing and (
                        element.occurrence_kind == row.kind):
                    residue_items.append(ResidueItem(
                        phrasing=row.phrasing,
                        entry_identifier=display,
                        line_span=Span(element.line, element.line)))
                    break
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
    gap_over_bound, gap_naming_size = _gap_refusal_signal(entries)
    output.gap_over_bound = gap_over_bound
    output.gap_naming_over_bound = gap_over_bound
    output.gap_naming_size = gap_naming_size
    output.waiting_entry_ids = sorted(set(waiting_ids))
    return output
