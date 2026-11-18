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
        _closed_form = re.search(
            r"\b(?:now closed|is closed|stands closed|"
            r"been closed|closed in full|closed)\b",
            claim_statement, re.IGNORECASE)
        if ((re.search(r"\b(?:ruled|settled|decided)\b",
                       claim_statement, re.IGNORECASE)
                and _closed_form)
                or (re.search(r"\bdecision\b",
                              claim_statement, re.IGNORECASE)
                    and _closed_form)
                or (re.search(r"\bshut\b",
                              claim_statement, re.IGNORECASE)
                    and re.search(r"\bruling\b",
                                  claim_statement, re.IGNORECASE))):
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
    return (_rule_order_key(finding.rule_id), start, end,
            evidence_text.encode("utf-8"),
            (finding.statement or "").encode("utf-8"))


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


def _options_alias_label(lowered):
    """Whether a lowered recorded label stands in one of the
    bounded Options alias forms: the words the options, or
    the three options, standing as whole words at the head
    of the label. The alias takes a word boundary after the
    options word: a label that merely opens with those
    letters and continues the word (a nonsense label opening
    the optionsXYZ) is no alias form (round 2 charge CH-22,
    finding S17-ATK2-17-03)."""
    for prefix in ("the three options", "the options"):
        if lowered == prefix:
            return True
        if lowered.startswith(prefix):
            following = lowered[len(prefix)]
            if not (following.isalnum() or following == "_"):
                return True
    return False


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
    for label in _field_labels(entry):
        lowered = label.lower()
        if label == "Options" or _options_alias_label(lowered):
            return True
    return _prose_options_line_index(entry) is not None


def _options_value_present(entry):
    """Whether an Options field stands present on its value:
    a recorded Options field carrying a non empty value, or
    the label alone with its option lines standing as the
    following body lines, the shape whose collected lines are
    the field value (Step 17 charge F-17-02)."""
    value = _field_value(entry, "Options")
    if value is not None:
        if value.strip():
            return True
        collected = False
        for _line, text in _body_lines(entry):
            stripped = (text or "").strip()
            if stripped.startswith("Options:"):
                collected = True
                continue
            if collected:
                if stripped.startswith("- "):
                    return True
                if stripped:
                    break
        return False
    for f in _get(entry, "fields") or []:
        label = str(_get(f, "label", "") or "")
        lowered = label.lower()
        if _options_alias_label(lowered):
            if (_get(f, "value") or "").strip():
                return True
            # The alias limb takes the collected lines reading
            # the exact label limb takes (round 3 charge CH-38,
            # alias limb of S17-ATK3-17-03): on an empty value
            # the label alone with its option lines standing as
            # the following body lines counts as present.
            collected = False
            for _line, text in _body_lines(entry):
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
                label.startswith(prefix) for prefix in prefixes):
            value = _get(f, "value") or ""
            if require_word_character:
                if re.search(r"\w", value):
                    return True
            elif value.strip():
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
    re.compile(r"\bDQ-([0-9]+)\s+is\s+(?:decided|closed|settled|"
               r"ruled)\b", re.IGNORECASE),
    # The verb first pattern reads its verbs in either case:
    # a verb standing lower case in a parenthetical on the
    # entry own Status line is the same form (Step 17 round 2
    # charge CH-7, S17-ATK2-7-04).
    re.compile(r"\b(?:Settle|Settles|Close|Closes|Rule|Rules)\s+"
               r"DQ-([0-9]+)\b", re.IGNORECASE),
    re.compile(r"\bquestion for DQ-([0-9]+)\b", re.IGNORECASE),
    # CH-39, S17-ATK3-7-02: the was form on the entry own
    # Status line, DQ-999 was closed, is read by this scan on
    # the same terms as the is form.
    re.compile(r"\bDQ-([0-9]+)\s+was\s+(?:decided|closed|settled|"
               r"ruled)\b", re.IGNORECASE),
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
                if next_stripped.startswith("- "):
                    landing = True
                break
            if landing:
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
                for match in pattern.finditer(text):
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


def _check8(model, entries, derived_by_id, derived_lists=None):
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
    for entry in entries:
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
            for token in _DQ_TOKEN_RE.finditer(text):
                targets.add("DQ-%03d" % int(token.group(1)))
            for target in targets:
                sup_covered.add((source_id, int(target[3:])))

    def scan_citations(lines, source_key, entry_identifier):
        for line_number, text in lines:
            for pattern in _CITATION_PATTERNS:
                for match in pattern.finditer(text):
                    number = int(match.group(1))
                    if number in numbers:
                        continue
                    if (source_key, number) in sup_covered:
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
    def scan_plain_citations(lines, source_key, entry_identifier,
                             skip_numbers=()):
        for line_number, text in lines:
            if (text or "").startswith("Status:"):
                continue
            for token in _DQ_TOKEN_RE.finditer(text or ""):
                number = int(token.group(1))
                if number in numbers or number in skip_numbers:
                    continue
                if (source_key, number) in sup_covered:
                    continue
                key = (source_key, number)
                if key in cited:
                    continue
                cited.add(key)
                findings.append(_pd_r7_finding(
                    text, "DQ-%03d" % number,
                    Span(line_number, line_number),
                    identifier=entry_identifier))

    for entry in entries:
        source_id = _display_id(entry)
        skip = set()
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
                    for match in pattern.finditer(text or ""):
                        skip.add(int(match.group(1)))
        scan_plain_citations(_body_lines(entry), source_id,
                             source_id, skip_numbers=skip)
        # The entry heading line is a citation surface of the
        # entry: a ghost number named in its title is reported
        # here as it is on a body line (charge CH-7,
        # S17-ATK2-7-06).
        heading_line = _get(entry, "heading_line")
        heading_text = _get(entry, "heading") or ""
        if heading_line is not None and heading_text:
            scan_plain_citations(
                [(heading_line, heading_text)], source_id,
                source_id, skip_numbers=skip)
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
        re.compile(r"DQ-[0-9]+\s+is\s+(Settled|Ruled|Open|Banked|Closed|"
                   r"Parked|Presented|Decided|decided)\b"),
        re.compile(r"[^.;]{0,110}?\b(stays|remains|stands|left)\s+"
                   r"(banked|open|settled|ruled|closed)\b"),
        # The still forms of the same claims, in the ordinary
        # phrasings a stale claim takes: a state stated with
        # still standing before it, and the waiting form that
        # states an open claim in words (Step 17 charge
        # F-11-06).
        re.compile(r"DQ-[0-9]+\s+is\s+still\s+(settled|ruled|open|"
                   r"banked|closed|parked|presented)\b",
                   re.IGNORECASE),
        re.compile(r"[^.;]{0,110}?\bstill waiting\b"),
        # The past tense forms of the same claims, and the is
        # decided form: the state word list of the first
        # pattern carries decided, and a claim stated with was
        # or has been takes the same Note (Step 17 round 2
        # charge CH-7, S17-ATK2-7-07 and S17-ATK2-7-08).
        re.compile(r"DQ-[0-9]+\s+was\s+(settled|ruled|closed|"
                   r"decided|banked|parked|presented|open)\b",
                   re.IGNORECASE),
        re.compile(r"DQ-[0-9]+\s+has\s+been\s+(settled|ruled|"
                   r"closed|decided)\b", re.IGNORECASE),
        # CH-39, S17-ATK3-7-05: the present perfect without
        # been, the got passive, and the bare past forms state
        # the same decided state and take the same Note. The
        # future, progressive, and gerund forms state no such
        # state and stand outside the charge.
        re.compile(r"DQ-[0-9]+\s+has\s+(settled|ruled|"
                   r"closed|decided)\b", re.IGNORECASE),
        re.compile(r"DQ-[0-9]+\s+got\s+(settled|ruled|"
                   r"closed|decided)\b", re.IGNORECASE),
        # The bare past form stands as a sentence closing
        # on a time adverb (DQ-338 closed yesterday.); a
        # ruling reference carrying an object after the verb
        # (DQ-031 ruled that, DQ-029 settled R-92) is a
        # mention of that ruling, not a state claim, and the
        # governed corpus pins stand on that reading.
        re.compile(r"DQ-[0-9]+\s+(settled|ruled|closed|"
                   r"decided)\s+(yesterday|today|already|"
                   r"earlier|recently|now)\b", re.IGNORECASE),
    )
    # CH-39, S17-ATK3-7-03: the verb first form reads its
    # verbs in either case, as the ghost scan does.
    verb_claim_pattern = re.compile(
        r"\b(?:Settle|Settles|Rule|Rules|Close|Closes|Decide|"
        r"Decides)\s+DQ-([0-9]+)\b", re.IGNORECASE)
    for entry in entries:
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
                for match in verb_claim_pattern.finditer(text or ""):
                    target_id = "DQ-%03d" % int(match.group(1))
                    if target_id == claiming_id:
                        continue
                    quoted = (text or "")[match.start():]
                    end = quoted.find(".")
                    if end >= 0:
                        quoted = quoted[:end + 1]
                    quoted = quoted.strip()
                    key = (claiming_id, target_id, quoted)
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

_DQ_TOKEN_RE = re.compile(
    r"\bDQ-([0-9]+)(?![" + _TOKEN_CONTINUATION + r"])\b")

_IDENTIFICATION_PATTERNS = (
    re.compile(r"displaces the rulings? at "
               r"((?:DQ-[0-9]+)(?:\s+and\s+DQ-[0-9]+)*)"),
    re.compile(r"displaces ((?:DQ-[0-9]+)(?:\s+and\s+DQ-[0-9]+)*)\b"),
    re.compile(r"((?:DQ-[0-9]+)(?:\s+and\s+DQ-[0-9]+)*)\s+"
               r"(?:is|are) the superseded entr"),
    re.compile(r"((?:DQ-[0-9]+)(?:\s+and\s+DQ-[0-9]+)*)\s+"
               r"(?:is|are) the entr\w+ it stands in place of"),
    re.compile(r"replaces ((?:DQ-[0-9]+)(?:\s+and\s+DQ-[0-9]+)*)\s+as\b"),
    re.compile(r"supersedes ((?:DQ-[0-9]+)(?:\s+and\s+DQ-[0-9]+)*)\b"),
    re.compile(r"supersedes\b[^.;]{0,120}?\bat "
               r"((?:DQ-[0-9]+)(?:\s+and\s+DQ-[0-9]+)*)\b"),
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
    map_over_bound, cycle_over_bound).

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
            for token in _DQ_TOKEN_RE.finditer(unit):
                token_id = "DQ-%03d" % int(token.group(1))
                if token_id != self_id and token_id not in tokens:
                    tokens.append(token_id)
            variants = [t for t in
                        _case_variant_identifications(unit)
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
            targets = []
            for segment in segments:
                for target in _identifications(segment):
                    if target not in targets:
                        targets.append(target)
            for target in _case_variant_identifications(joined):
                if target not in targets:
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
        # full. Returns (cycles, over_bound).
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
        try:
            return _enumerate_components(
                components, adjacency, seen_keys, found_cycles)
        except _CycleBoundExceeded:
            return found_cycles, True

    def _enumerate_components(
            components, adjacency, seen_keys, found_cycles):
        for component in components:
            if len(component) == 1:
                only = component[0]
                if only not in adjacency[only]:
                    continue
            members = set(component)
            ordered = sorted(
                members, key=lambda n: file_order.get(n, 0))
            for start in ordered:
                start_order = file_order.get(start, 0)
                # Simple paths from start through entries of the
                # component that stand at or after start in file
                # order; an edge back to start closes a cycle.
                path = [start]
                in_path = {start}
                work = [(start, iter(adjacency[start]))]
                while work:
                    node, edges = work[-1]
                    descended = False
                    for nxt in edges:
                        if nxt == start:
                            key = tuple(path)
                            if key not in seen_keys:
                                seen_keys.add(key)
                                found_cycles.append(list(path))
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
                        work.append(
                            (nxt, iter(adjacency[nxt])))
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

    cycles, cycles_over_bound = find_cycles(displaces, headed_ids)
    pointer_cycles, pointer_cycles_over_bound = find_cycles(
        pointers, headed_ids)
    cycle_over_bound = cycles_over_bound or \
        pointer_cycles_over_bound
    if cycle_over_bound:
        # The run refuses on this flag at exit 3 in the standing
        # refusal family, on both subcommands, before any cycle
        # Warning is built and before the map print size is
        # computed: the render refusal is computed during
        # enumeration, never only after it, and no partial
        # inventory stands on the output as a complete one
        # (Step 17 round 3, CH-32).
        return pointers, findings, [], cycles, False, True
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
        return pointers, findings, [], cycles, True, False

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
    return pointers, findings, chains, cycles, False, False


_SEGMENT_CLAIM_RE = re.compile(
    r"\bDQ-([0-9]+)\b[^.]{0,90}?\b(was|is|stands|remains|stays|left)\b"
    r"[^.]{0,60}?\b(settled|ruled|closed|banked|open|parked|"
    r"presented)\b", re.IGNORECASE)


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
            for line_number, text in (_get(segment, "lines") or []):
                if quarantined_heading_line is not None and \
                        line_number == quarantined_heading_line:
                    continue
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
            if quarantined_heading_line is not None and \
                    line_number == quarantined_heading_line:
                continue
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


def _census(entries, derived_list, banked_cut_ids=None):
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
        entries, derived_list, banked_cut_ids)
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

_OPEN_FIELD_LABELS_FOR_CENSUS = frozenset({
    "question", "the question", "question as put", "options",
    "cost of deciding late", "cost", "what it blocks", "blocks",
})


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
        if char not in _INVISIBLE_LINE_CHARS)
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
        if char not in _INVISIBLE_LINE_CHARS).strip()
    while True:
        if stripped.startswith(">"):
            stripped = stripped[1:].lstrip()
            continue
        if stripped.startswith("**"):
            stripped = stripped[2:].lstrip()
            continue
        match = re.match(
            r"(?:[-*+\u2022\u2013\u2014]|\d+[.)]"
            r"|[A-Za-z][.)]|[ivxlcdmIVXLCDM]+[.)])\s+",
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
    stripped = (text or "").strip()
    match = re.match(r"^([A-Za-z][A-Za-z ]{0,40}):", stripped)
    if not match:
        return False
    return match.group(1).strip().lower() in (
        _OPEN_FIELD_LABELS_FOR_CENSUS)


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


def _banked_cut_entry_ids(model, entries):
    """The display identifiers of entries cut by an unmatched
    heading: entries whose span ends on the line directly
    before the span of an orphan segment whose record carries
    unmatched_heading. The heading that cuts such an entry is
    the heading the run itself reports under PIN-06, and the
    prose standing under it stands in the orphan segment,
    outside the entry body, quarantined as file level matter,
    so it can never stand as evidence of the entry it cut
    (fix wave 3 closing, defect D1, register item 17R-170)."""
    cut_starts = set()
    for segment in _get(model, "orphan_segments") or []:
        if not _get(segment, "unmatched_heading"):
            continue
        span = _get(segment, "span")
        start = _get(span, "start_line") if span is not None else None
        if start is not None:
            cut_starts.add(start)
    cut_ids = set()
    if not cut_starts:
        return cut_ids
    for entry in entries:
        span = _get(entry, "span")
        if span is None:
            spans = _get(entry, "spans") or []
            span = spans[-1] if spans else None
        end = _get(span, "end_line") if span is not None else None
        if end is not None and end + 1 in cut_starts:
            cut_ids.add(_display_id(entry))
    return cut_ids


def _banked_evidence_groups(entries, derived_list, cut_ids=None):
    """The Banked head population and its three evidence groups.

    Population: entries whose first line start Status line is the
    exact Banked line. Precedence: an entry with a later Status
    line in the body is in the first group whatever else its body
    carries; an entry with no later Status line and a level 4
    decision block is in the second; an entry with neither, whose
    body carries unheaded paragraphs, is in the third. One
    bound on the population stands beside the unparsed bound
    below: an entry cut by an unmatched heading, named in
    cut_ids, that takes no group stands outside the population,
    because its evidence body was cut off by that heading and
    the matter behind the heading is the segment's, not the
    entry's. A cut entry that takes a group keeps its population
    and group standing exactly as before, and an entry with no
    such cut that takes no group stays in the population, so
    its footing failure stands as before.
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
        later = [e for e in elements
                 if e.occurrence_kind == "line start"
                 and e is not first_line]
        if later:
            group1.append(display)
            continue
        if any(_get(block, "marking_form") == "H4 sub part"
               and _h4_block_has_body(entry, block)
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
        elif cut_ids and display in cut_ids:
            # The entry takes no group and stands cut by an
            # unmatched heading, so it stands outside the
            # population, on the bound in the docstring above.
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
    for part in parts:
        if part == "nothing.":
            return True
        part_read = re.sub(r"[\s.!?]+$", "", part)
        if part_read not in _BLOCKS_NO_ITEM_VALUES:
            return True
    return False


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
     sup_cycle_over_bound) = _supersession_unit(
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
                                  derived_lists))
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

    banked_cut_ids = _banked_cut_entry_ids(model, entries)
    census = _census(entries, derived_list, banked_cut_ids)

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
    # bound for an entry cut by an unmatched heading.
    if sum(findings_per_severity.values()) != len(findings):
        fail(4, "component footing: the severity view sums to %d "
                "against a findings list of %d"
                % (sum(findings_per_severity.values()), len(findings)))
    if sum(findings_per_rule.values()) != len(findings):
        fail(4, "component footing: the rule view sums to %d "
                "against a findings list of %d"
                % (sum(findings_per_rule.values()), len(findings)))
    census_population, census_groups = _banked_evidence_groups(
        entries, derived_list, banked_cut_ids)
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
        blocks = _field_value(entry, "What it blocks") \
            or _field_value(entry, "Blocks")
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
        # carry those claims on the same terms, one report per
        # named entry, so the Segment claims section of both
        # outputs stands for every claim the findings report and
        # no claim the findings recognise is dropped from the
        # render output, which prints no findings list.
        seen_reported = set()
        report_quarantined_line = _quarantined_heading_line(
            segment, _get(segment, "span"))
        for _line_number, text in (_get(segment, "lines") or []):
            if report_quarantined_line is not None and \
                    _line_number == report_quarantined_line:
                continue
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
                        break
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
