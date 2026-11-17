"""Parse: the Input value and the Limits value, and nothing else.

Parse is a pure function over values in memory. It decodes the raw
bytes as UTF-8, takes the measurements once, enforces the limits at
entry, partitions the lines under the terminator rule, cuts the
spans on the heading forms, collects the status bearing element
inventory in element order, the field occurrences, the decision
blocks, the file header facts, the orphan segments and the parse
notes, and returns either the Queue file model or the file level
failure result. It grades nothing, resolves no contradiction, and
never looks a phrasing up in any vocabulary: the forms are recognised
by their surface forms alone.
"""

import hashlib
import re
import sys
import unicodedata

from .types import (
    DQNumber,
    DecisionBlock,
    ElementTuple,
    EntryRecord,
    ExitDecision,
    FieldOccurrence,
    FileHeaderFacts,
    FileLevelFailure,
    Input,
    InputValue,
    Limits,
    LimitsValue,
    NearMarkerOccurrence,
    OrphanSegment,
    ParseNote,
    QueueFileModel,
    SegmentClaim,
    Span,
    StatusBearingElement,
    Unit,
    Vocabulary,
)

__all__ = [
    "parse_queue",
    "Input",
    "InputValue",
    "Limits",
    "LimitsValue",
    "Vocabulary",
]

_HEADING_RE = re.compile(r"^(#{1,6}) (.*)$")
_NUMBERED_RE = re.compile(r"^DQ-([0-9]+): (\S.*)$")
_NAMED_UNNUMBERED_HEADING = "R-7 closure conflict"
_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
_ADDITION_RE = re.compile(
    r"^(?:[A-Za-z]+ )?addition to (DQ-\d{3})\b", re.IGNORECASE)
_LABEL_RE = re.compile(r"^([A-Z][A-Za-z0-9 '&()/.-]{0,58}?):(?:[ ]+(.*)|[ ]*)$")
_BOLD_LEAD_RE = re.compile(r"^\*\*(.+?)\*\*")
_DQ_TOKEN_RE = re.compile(r"\bDQ-\d{3}\b")
_R_TOKEN_RE = re.compile(r"\bR-\d+\b")

_STATUS_MARKER = "Status:"
_VARIANT_MARKER = "Status unchanged"

# Characters that may stand in a run before a Status marker
# without reclassifying it: a space, a tab, and the invisible
# space and zero width characters (a byte order mark, a no
# break space, the Unicode space widths, a zero width space).
_LEADING_STATUS_CHARS = (
    " \t\ufeff\u00a0\u1680\u2000\u2001\u2002\u2003"
    "\u2004\u2005\u2006\u2007\u2008\u2009\u200a\u200b"
    "\u202f\u205f\u3000")


def _leading_status_run(text):
    """The length of the leading run of the characters above."""
    index = 0
    while index < len(text) and text[index] in _LEADING_STATUS_CHARS:
        index += 1
    return index

_DISPOSITION_WORDS = {
    "BANKED": "Banked",
    "OPEN": "Open",
    "PRESENTED": "Presented",
    "PARKED": "Parked",
    "RULED": "Ruled",
    "SETTLED": "Settled",
    "CLOSED": "Closed",
}

# Labels whose paragraphs carry entry fields and no prose element.
_FIELD_PARAGRAPH_LABELS = {
    "Owner of record",
    "Source",
    "The question",
    "Question",
    "Options",
    "The options",
    "Cost of deciding late",
    "What it blocks",
    "Ordering reason",
}

# First line labels that open an unheaded labelled paragraph block.
# The set is the recorded label list at brief section 5.2, PIN-01,
# form 2: labels of the ruling, settlement, assessment, and outcome
# families in their recorded forms.
_DECISION_LABELS = {
    "Ruled",
    "Settled",
    "Settlement",
    "Ruled by",
    "Settled by",
    "Decision",
    "Ruling text",
    "Ruling texts",
    "Ruling outcome",
    "Outcome of this decision",
    "Form outcome",
    "Addition to",
}

# The disposition a recorded label form itself carries, where the
# labelled matter states no disposition of its own: the matter
# under the label performs the act the label names, under PIN-01,
# form 2. A label standing in the decision set with no entry here,
# the Decision label, carries no disposition from its form.
_LABEL_DISPOSITIONS = {
    "Ruled": "Ruled",
    "Ruled by": "Ruled",
    "Ruling text": "Ruled",
    "Ruling texts": "Ruled",
    "Ruling outcome": "Ruled",
    "Outcome of this decision": "Ruled",
    "Form outcome": "Ruled",
    "Settled": "Settled",
    "Settled by": "Settled",
    "Settlement": "Settled",
}

# Single word lead in labels that are named forms of the contract.
_KNOWN_SINGLE_LABELS = {
    "Status", "Ruled", "Settled", "Settlement", "Landing", "Origin",
    "Source", "Options", "Decision", "Remainder", "Condition",
    "Examined", "Question", "Correction", "Addition", "Note",
    "Assessment", "Assessed", "Ruling", "Outcome", "Form", "Her",
    "His", "The", "Captain", "Flag", "Basis", "Where", "Deciding",
    "Governing", "Strictness", "Evidence", "Implementation",
    "Cross-reference", "Per-report", "Partial", "Ruling",
}


def _partition_lines(text):
    """The model lines of a decoded text, under the terminator rule.

    The terminator is a line feed, or a carriage return immediately
    before a line feed, the pair counting as one terminator. A lone
    carriage return is an ordinary character of its line. A final
    line with no terminator is a line, and a terminator at the end
    of the text closes the last line and begins no further line.
    """
    lines = []
    start = 0
    index = 0
    length = len(text)
    while index < length:
        char = text[index]
        if char == "\n":
            lines.append(text[start:index])
            index += 1
            start = index
        elif char == "\r" and index + 1 < length and \
                text[index + 1] == "\n":
            lines.append(text[start:index])
            index += 2
            start = index
        else:
            index += 1
    if start < length:
        lines.append(text[start:])
    return lines


def _final_line_is_cut_off(line_text):
    """Whether a final line with no terminator is cut off in form.

    A missing terminator alone does not cut a line off: under
    the terminator rule in _partition_lines a final line with
    no terminator is a line, and a carriage return standing as
    the last character of the text is part of the line ending
    and not content, as the plan states at Item 3, section
    9.3. The line is cut off only where its own form is
    incomplete: a Status line or variant line carrying no
    value, or a line of prose or field matter that closes no
    sentence, ending mid statement with no sentence closing
    punctuation. A line stands whole where it is a Status line
    or a variant line carrying a value, or where it closes a
    sentence, the closing punctuation standing before any
    closing quote or bracket characters. A labelled line
    carrying a value stands whole only where its value is
    complete in its own form, under
    _labelled_value_stands_whole. A line also stands whole in
    two further closed forms: a bullet item, which is complete
    in item form with no sentence close, and a line closing on
    a balanced bracket group, whose closing bracket is its
    terminal mark. A byte order mark standing on the line is
    inert, as it is in every other position this slice reads,
    and takes no part in the test. A label is read in its
    lower case form as well as its capital form, so a complete
    line under a lower case label is judged on its value, not
    on the label case.
    """
    text = line_text
    if text.endswith("\r"):
        text = text[:-1]
    text = text.replace("\ufeff", "")
    stripped = text.strip()
    if not stripped:
        return False
    if stripped.startswith(_STATUS_MARKER):
        return stripped[len(_STATUS_MARKER):].strip() == ""
    if stripped.startswith(_VARIANT_MARKER):
        return stripped[len(_VARIANT_MARKER):].strip() == ""
    label_match = _LABEL_RE.match(stripped)
    if label_match is None:
        ci_match = re.match(_LABEL_RE.pattern, stripped,
                            re.IGNORECASE)
        if ci_match is not None and \
                ci_match.group(1).strip().lower() not in (
                    "status", "status unchanged"):
            label_match = ci_match
    if label_match and (label_match.group(2) or "").strip():
        # A labelled line carrying a value stands whole only
        # where the value is complete in its own form: the
        # taught field lines close on their value, not on
        # sentence punctuation, so a complete final field line
        # is not cut off by the missing terminator alone, and a
        # labelled line whose value stands cut in form, as the
        # WV-8 truncation form final question line cut mid word,
        # is cut off.
        return not _labelled_value_stands_whole(
            label_match.group(1), label_match.group(2))
    if stripped.startswith("- "):
        return False
    if _final_bracket_group_start(
            stripped.rstrip("\"'”’")) is not None:
        return False
    core = stripped.rstrip("\"')]}"
                           "”’")
    return not core.endswith((".", "?", "!"))


# Labels whose values are sentences in the taught forms: a
# question value closes on its question mark and a cost value
# on its full stop, so either stands whole only where its
# sentence closes.
_SENTENCE_VALUE_LABELS = {
    "question", "the question", "question as put",
    "cost of deciding late", "cost",
}

# Lower case words that may stand inside a name form value
# without making the value sentence prose.
_NAME_FORM_WORDS = {
    "of", "the", "and", "or", "for", "de", "van", "von",
    "in", "di", "da", "del", "della", "der", "den", "ten",
    "ter", "la", "le", "du",
}

# Complete word forms of the taught queue surface, against
# which the last token of a value is read for a mid word
# cut: a value whose last token is a strict prefix of one of
# these words, and is not itself one of them, stands cut in
# form, as a name value ending in Cler stands cut against
# Clerk. A last token that is itself a complete word of the
# surface, or that no word of the surface extends, stands by
# its own form. A cut falling exactly on a word boundary, or
# inside a word the surface does not carry, is not visible
# in form; that is the stated bound of this test.
_FRAGMENT_REFERENCE_WORDS = {
    "adopted", "appendix", "banked", "blocked", "captain",
    "charge", "clerk", "clear", "closed", "cost", "decision",
    "deciding", "harbour", "late", "note", "open", "option",
    "options", "question", "queue", "record", "ruled",
    "settled", "taken", "unadopted", "waiting", "written",
}


def _final_bracket_group_start(core):
    """The start index of a closing bracket group, or None.

    A text closing on the closing bracket of a balanced,
    non empty bracket group is complete in bracket form: the
    closing bracket is its terminal mark, as a bracketed
    appendix reference stands whole and as a value ending in
    a parenthetical stands whole. An unbalanced text, or a
    group carrying nothing inside it, has no such form.
    """
    if not core.endswith((")", "]")):
        return None
    opening = "(" if core.endswith(")") else "["
    closing = core[-1]
    depth = 0
    for index in range(len(core) - 1, -1, -1):
        char = core[index]
        if char == closing:
            depth += 1
        elif char == opening:
            depth -= 1
            if depth == 0:
                if core[index + 1:-1].strip():
                    return index
                return None
    return None


def _last_token_is_fragment(tokens):
    """Whether a value last token stands cut mid word in form.

    The token stands as a fragment where it is a word of
    three or more letters, is not itself a complete word of
    the taught surface, and is a strict prefix of one, so a
    longer complete word of the surface stands cut down to
    it. Single and two letter tokens, numbers, and reference
    tokens carry no such reading.
    """
    if not tokens:
        return True
    last = tokens[-1].rstrip(",").lower()
    if len(last) < 3 or not last.isalpha():
        return False
    if last in _FRAGMENT_REFERENCE_WORDS:
        return False
    return any(word.startswith(last)
               for word in _FRAGMENT_REFERENCE_WORDS)


def _labelled_value_stands_whole(label, value):
    """Whether a labelled final line value is complete in form.

    The value stands whole in these forms. First, it
    closes a sentence, the closing punctuation standing before
    any closing quote or bracket characters. Second, it closes
    on a balanced bracket group, whose closing bracket is its
    terminal mark, where the matter before the group does not
    itself stand cut. Third, it is a closed form value, a
    value built only of complete closed tokens: a Blocks value
    of full DQ references or the word None, an Options value
    of full option items or of short single character items in
    the taught list form, or a name form value of capitalised
    words, numbers, and the short joining words a name may
    carry, where the token scan reads letters in any script,
    so an accented capital stands as a capital. A value under
    any other label stands whole where its tokens are word
    tokens, its last token is not a joining word, and its last
    token does not stand cut mid word against the taught
    surface word forms. A value in sentence prose form that
    closes no sentence is not whole: nothing in its surface
    form shows it complete, and its last word may stand cut
    mid word, as the WV-8 truncation form at brief section 5.8
    pins. A sentence valued label, the question and cost
    families, stands whole only on its sentence close or its
    bracket close.
    """
    raw = value.strip().rstrip("\"'”’")
    core = raw.rstrip(")]}")
    if core.endswith((".", "?", "!")):
        return True
    group_start = _final_bracket_group_start(raw)
    if group_start is not None:
        before = [token for token in re.findall(
            r"\w+(?:['’./-]\w+)*", raw[:group_start])]
        if not before:
            return True
        return not _last_token_is_fragment(before) and \
            before[-1].lower() not in _NAME_FORM_WORDS
    label_key = label.strip().lower()
    if label_key in _SENTENCE_VALUE_LABELS:
        return False
    if label_key in ("options", "the options"):
        items = [item.strip() for item in core.split(",")]
        return bool(items) and all(items) and all(
            re.match(r"^Option\s+\S", item) is not None or
            re.fullmatch(r"[A-Za-z0-9]", item) is not None
            for item in items)
    if label_key in ("blocks", "what it blocks"):
        parts = [part.strip() for part in
                 re.split(r",|\band\b", core)]
        return bool(parts) and all(parts) and all(
            part == "None" or
            re.fullmatch(r"DQ-[0-9]{3,}", part) is not None
            for part in parts)
    tokens = re.findall(r"\w+(?:['’./-]\w+)*", core)
    if not tokens:
        return False
    if _last_token_is_fragment(tokens):
        return False
    if tokens[-1].lower() in _NAME_FORM_WORDS:
        return False
    for token in tokens:
        token = token.rstrip(",")
        if token.startswith("DQ-"):
            if re.fullmatch(r"DQ-[0-9]{3,}", token) is None:
                return False
            continue
        if token[0].isupper() or token.isdigit() or \
                len(token) == 1 or token.isalpha():
            continue
        if token.lower() in _NAME_FORM_WORDS:
            continue
        return False
    return True


def _first_word(text):
    match = re.match(r"[A-Za-z]+", text.lstrip())
    return match.group(0) if match else ""


def _disposition_from_value(value):
    """The disposition of a status value, from its opening forms.

    The disposition is read from the surface forms of the value
    alone: its opening word, or a Ruled by or Settled by form it
    carries. A value whose opening forms state no disposition
    takes no disposition here. Parse holds no vocabulary mapping
    and performs no translation: the translation of a verbatim
    phrasing to a canonical family, and every mapping to a
    canonical state, is validate work under the seam at plan
    Item 3, section 3.5, and a phrasing parse cannot read stands
    in the element list with no disposition, under PIN-04.
    """
    word = _first_word(value).upper()
    if word in _DISPOSITION_WORDS:
        return _DISPOSITION_WORDS[word]
    if re.search(r"\bRuled by:", value):
        return "Ruled"
    if re.search(r"\bSettled by:", value):
        return "Settled"
    return None


_COUNT_ROW_RE = re.compile(
    r"(?i:canonical)[ \t]+(?:(?i:state)[ \t]*:[ \t]*)?"
    r"(Settled in part|Closed as decided|Ruled|Settled|Closed|"
    r"Open|Banked|Parked|Presented)[ \t]*:[ \t]*[0-9]+")

_GROUP_HEADING_RE = re.compile(
    r"(Settled in part|Closed as decided|Ruled|Settled|Closed|"
    r"Parked|Presented|Open|Banked|Conditional|Ambiguous) group",
    re.IGNORECASE)


def _mask_comment_segments(text):
    """The line with its HTML comment segments blanked to spaces.

    A comment segment runs from an opener to the next close
    marker on the same line, or to the end of the line where no
    close marker stands. Blanking is length preserving, so the
    offsets of genuine matter standing outside the segments do
    not move. Matter inside a comment segment is container
    matter: on the disposition reading surface it denotes no
    disposition, whether the segment carries an output row or
    a ruling (Step 17 fix wave 2, charge CH-16, F-20-2-4).
    """
    if "<!--" not in text:
        return text
    chars = list(text)
    index = 0
    while True:
        opening = text.find("<!--", index)
        if opening < 0:
            break
        closing = text.find("-->", opening + 4)
        end = len(text) if closing < 0 else closing + 3
        for position in range(opening, end):
            chars[position] = " "
        index = end
        if closing < 0:
            break
    return "".join(chars)


def _guarded_output_spans(text):
    """The spans of one line that state tool output, not a ruling.

    Two output forms stand guarded, recognised by their meaning
    wherever they stand in the line (Step 17 fix wave 2, charge
    CH-15, flag ruling (g) at record section 19):

    - A count row of the tool own output, in either spelling:
      the reconciliation spelling, Canonical, a state word, a
      colon, and a count; and the census spelling, Canonical
      state, a colon, a state word, a colon, and a count. The
      row states a file level count and names no decider,
      ruling text, or landing for the entry it stands in.
    - A rendered group heading line standing as its own
      sentence: a state word and the word group, with only
      quoting or emphasis decoration around it.

    The guard is confined to the row or heading itself: a
    disposition form standing outside these spans, later on
    the same line included, still counts.
    """
    spans = []
    for match in _COUNT_ROW_RE.finditer(text):
        spans.append((match.start(), match.end()))
    for span_start, span_end in _sentence_spans(text):
        core = text[span_start:span_end].strip(" \t*|>#-")
        if _GROUP_HEADING_RE.fullmatch(core.rstrip(".")):
            spans.append((span_start, span_end))
    return spans


def _find_disposition(text, start=0):
    """Find a disposition statement in one line of prose or a block.

    Returns a pair of the disposition and the offset at which the
    statement stands in the line, or None where the line states no
    disposition under the named forms. The search runs from the
    given offset, and the offset it returns is absolute in the line.
    """
    text = _mask_comment_segments(text)
    guarded = _guarded_output_spans(text)

    def _is_guarded(position):
        return any(span_start <= position < span_end
                   for span_start, span_end in guarded)

    checks = (
        (r"\bSETTLED IN PART\b", "Settled"),
        (r"\b[Rr]uled the\b[^.]{0,80}?\bof this entry\b", "Ruled"),
        (r"\b[Ss]ettled the\b[^.]{0,80}?\bof this entry\b", "Settled"),
        (r"\b[Rr]uled the entry\b", "Ruled"),
        (r"\b[Ss]ettled the entry\b", "Settled"),
        (r"\bRULED IN (PRINCIPLE|FULL)\b", "Ruled"),
        (r"\b(RULED|Ruled) by\b", "Ruled"),
        (r"\b(SETTLED|Settled) by\b", "Settled"),
        (r"\bis (Ruled|RULED) and closed\b", "Ruled"),
        (r"^(Ruled|RULED)\b", "Ruled"),
        (r"^(Settled|SETTLED|Settlement)\b", "Settled"),
        (r"^(Closed|CLOSED)\b", "Closed"),
        (r"^(Banked)\b", "Banked"),
        (r"^(Parked)\b", "Parked"),
        (r"^(Presented)\b", "Presented"),
        (r"^(Open)\b", "Open"),
        (r"\bdecided by assessment\b", "Closed"),
        (r"\bRULED, closed\b", "Ruled"),
        (r"\bRuled:\s", "Ruled"),
        (r"\bSettled:\s", "Settled"),
        (r"\bcloses in full\b", "Closed"),
        (r"\bitem closes\b", "Closed"),
        (r"\bis closed\b", "Closed"),
        (r"\bClosed\.\s*$", "Closed"),
        (r"\bstays banked\b", "Banked"),
        (r"\bstands banked\b", "Banked"),
        (r"\bremains banked\b", "Banked"),
        (r"\bstill banked\b", "Banked"),
        (r"\bnot finished\b", "Open"),
        (r"\bremains open\b", "Open"),
        (r"\bstays open\b", "Open"),
        (r"\bfurther [Rr]uled\b", "Ruled"),
        (r"\bfurther [Ss]ettled\b", "Settled"),
        (r"\b[Ss]ettled this entry\b", "Settled"),
        (r"\b[Rr]uled this entry\b", "Ruled"),
        (r"\bhas set the outstanding values\b", "Settled"),
        (r"\blimb of this entry is [Rr]uled\b", "Ruled"),
        (r"\blimb of this entry is [Ss]ettled\b", "Settled"),
    )
    best = None
    for priority, (pattern, disposition) in enumerate(checks):
        for match in re.finditer(pattern, text[start:]):
            position = start + match.start()
            if _is_guarded(position):
                # The form stands inside a count row or a group
                # heading: it is the output row itself, and it
                # denotes no disposition. A later unguarded
                # standing of the same form on this line, a
                # genuine ruling included, still counts.
                continue
            candidate = (position, priority, disposition)
            if best is None or candidate[:2] < best[:2]:
                best = candidate
            break
    if best is None:
        return None
    return best[2], best[0]


def _sentence_spans(text):
    """The sentence spans of a text, as start and end offsets.

    A sentence ends at a period followed by a space, the period
    standing inside its own sentence, or at the end of the text.
    """
    spans = []
    start = 0
    index = text.find(". ", start)
    while index >= 0:
        spans.append((start, index + 1))
        start = index + 2
        index = text.find(". ", start)
    if start < len(text):
        spans.append((start, len(text)))
    return spans


def _marked_statement(sentence):
    """Whether a sentence opens in a marked statement form.

    The marked forms are the ones PIN-01 names as carrying a
    statement at their head: a contained Status line form, a bold
    lead in start, or a recorded decision label. A sentence that
    opens in plain prose and only describes a state further in, as
    a remainder sentence does, carries no statement of its own:
    its matter belongs to the statement it follows, under the part
    and remainder machinery. A bare closure sentence forms no
    statement either: the terminal closure machinery owns that
    position, and inside a block segment it formed no element in
    the recorded reading.
    """
    stripped = sentence.strip()
    if stripped.startswith("Status:") or stripped.startswith("**"):
        return True
    label_match = _LABEL_RE.match(stripped)
    if label_match and \
            label_match.group(1).strip() in _DECISION_LABELS:
        return True
    return False


_MARKED_STATEMENT_WORD_RE = re.compile(
    r"(Ruled|Settled|Banked|Parked|Presented|Open|"
    r"RULED|SETTLED|BANKED)\b")


def _weak_marked_statement(sentence):
    """Whether a sentence opens with a bare disposition word.

    The weak marked form: a sentence whose first word is itself a
    disposition word, as a line standing as Ruled. or Settled in
    part. A closure word does not open a weak statement, for the
    reason _marked_statement states.
    """
    if _marked_statement(sentence):
        return True
    stripped = sentence.strip()
    return _MARKED_STATEMENT_WORD_RE.match(stripped) is not None


def _find_disposition_statements(text):
    """Every disposition statement in one line, in statement order.

    Returns a list of triples: the disposition, the offset at which
    its statement stands in the line, and the statement text, being
    the sentence the disposition form stands in. The first
    statement is the disposition the text as a whole carries, found
    as _find_disposition finds it. A further statement stands only
    where a later sentence opens in a marked statement form and
    carries a disposition, under the segmentation rule at brief
    section 5.2, PIN-01, form 1: a segment carrying two disposition
    statements splits at the second statement, wherever the two
    stand. Descriptive prose after the first statement, as a
    sentence describing what a remainder does, forms no statement
    of its own. A bare closure sentence standing last forms no
    statement here: the terminal closure machinery owns that
    position, and inside a block segment it formed no element in
    the recorded reading.
    """
    primary = _find_disposition(text)
    if primary is None:
        return []
    disposition, offset = primary
    sentences = _sentence_spans(text)
    primary_index = 0
    for index, (start, end) in enumerate(sentences):
        if start <= offset < end:
            primary_index = index
            break
    start, end = sentences[primary_index]
    results = [(disposition, offset, text[start:end])]
    for index in range(primary_index + 1, len(sentences)):
        start, end = sentences[index]
        sentence = text[start:end]
        if not _marked_statement(sentence):
            continue
        hit = _find_disposition(sentence)
        if hit:
            results.append((hit[0], start + hit[1], sentence))
    return results


def _statements_in_lines(lines):
    """The disposition statements standing in a run of lines.

    A run of lines, a block segment or a plain paragraph, carries
    one primary statement: the statements of its first line that
    carries one, under _find_disposition_statements. A later line
    adds a statement only where one of its sentences opens in a
    marked statement form, or its first sentence opens in the weak
    marked form, and carries a disposition: the two statements of
    the segmentation rule stand wherever they stand, on one line
    or on two lines, and descriptive prose lines after the primary
    statement form no statement of their own. Returns a list of
    five tuples: the line number, the line text, the disposition,
    the offset of the disposition expression within its line, and
    the statement text.
    """
    results = []
    primary_found = False
    for number, text in lines:
        if not primary_found:
            statements = _find_disposition_statements(text)
            if statements:
                primary_found = True
                for disposition, offset, statement in statements:
                    results.append((number, text, disposition,
                                    offset, statement))
            continue
        for index, (start, end) in enumerate(_sentence_spans(text)):
            sentence = text[start:end]
            if _marked_statement(sentence) or \
                    (index == 0 and _weak_marked_statement(sentence)):
                hit = _find_disposition(sentence)
                if hit:
                    results.append((number, text, hit[0],
                                    start + hit[1], sentence))
    return results


def _decider_from_text(text):
    """The decider category and decider text a statement names."""
    if re.search(r"by the Manager\b", text) or \
            re.search(r"(Settled|SETTLED) by:? The Manager\b", text) or \
            re.search(r"by a (decision|pick) of the Manager\b", text) or \
            re.search(r"the Manager's pick under .* delegation", text):
        named = re.search(r"The Manager \(Muse\)[^.]*", text)
        if named:
            return "a Manager grant form", named.group(0).rstrip()
        return "a Manager grant form", "The Manager"
    if re.search(r"(RULED|Ruled) by:? Captain JP\b", text):
        return "Captain JP", "Captain JP"
    if "DQ-148" in text and re.search(r"[Aa]ssessment", text):
        return "assessment by cross reference", "assessment under DQ-148"
    named = re.search(r"(?:Ruled|Settled) by:? ([A-Z][A-Za-z .]+?)(?:,|\.|$)",
                      text)
    if named:
        return "another named source", named.group(1).strip()
    if "Captain JP" in text and re.search(r"\b(Ruled|RULED)\b", text) and \
            "in her words" in text:
        return "Captain JP", "Captain JP"
    return None, None


def _remainder_from_text(text):
    """The remainder text a statement names, or None."""
    labelled = re.search(r"^Remainder:[ ]*(.+)$", text, re.MULTILINE)
    if labelled:
        return labelled.group(1).strip()
    banked = re.search(r"[Ww]hat stays banked:[ ]*(.+)", text, re.DOTALL)
    if banked:
        value = banked.group(1).strip()
        if value.endswith("."):
            value = value[:-1]
        return value
    leaving = re.search(r"\bleaving (.+?) (open|undecided)\b", text)
    if leaving:
        return leaving.group(1).strip()
    standing = re.search(
        r"[Tt]he remainder, (.+?),? (?:still )?(?:stands|stays) "
        r"(?:open|banked|undecided)\b", text)
    if standing:
        return standing.group(1).strip()
    if re.search(r"[Tt]he remainder stays banked", text):
        return "The remainder stays banked"
    return None


def _condition_from_text(text):
    """The condition text a statement carries, or None."""
    labelled = re.search(r"^Condition:[ ]*(.+)$", text, re.MULTILINE)
    if labelled:
        return labelled.group(1).strip()
    for marker in ("conditional on", "subject to"):
        at = text.find(marker)
        if at >= 0:
            value = text[at + len(marker):].strip()
            if value.endswith("."):
                value = value[:-1]
            return value
    return None


# The open entry field labels, lowercased: the field families
# the open entry field tests read. Inside a level 4 decision
# block these labels are the block's own lines, never fields of
# the entry (Step 17 charge F-17-09).
_OPEN_FIELD_LABELS = frozenset({
    "question", "the question", "question as put", "options",
    "cost of deciding late", "cost", "what it blocks", "blocks",
})


def _scope_of(text, remainder):
    """The scope of a disposition statement: Whole or Part.

    Scope is Part where the statement in words limits the act to a
    named part, limb, or portion of the entry, or where the
    statement names a remainder, as plan Item 3, section 3.5,
    field 6 states. The remainder itself is carried by the
    remainder text of the element, never by the scope word.
    """
    if remainder is not None:
        return "Part"
    if re.search(r"in part", text, re.IGNORECASE):
        return "Part"
    if re.search(r"\b(?:limb|portion|part) of this entry\b", text):
        return "Part"
    if re.search(r"\bOnly the\b.+\bof this entry is\b", text):
        return "Part"
    return "Whole"


def _make_element(kind, verbatim, disposition, line, position,
                  occurrence_kind, own_text, statement=None,
                  decision_block=None, decider_text_override=None):
    remainder = _remainder_from_text(own_text)
    condition = _condition_from_text(own_text)
    scope = _scope_of(own_text, remainder)
    decider, decider_text = _decider_from_text(own_text)
    if decider_text_override is not None:
        decider_text = decider_text_override
    core = ElementTuple(
        disposition=disposition,
        scope=scope,
        condition=condition,
        decider=decider,
        line=line,
    )
    return StatusBearingElement(
        kind=kind,
        verbatim=verbatim,
        tuple=core,
        line=line,
        position_in_line=position,
        occurrence_kind=occurrence_kind,
        remainder_text=remainder,
        decider_text=decider_text,
        statement=statement if statement is not None else verbatim,
        decision_block=decision_block,
        line_span=Span(line, line, "heading cut"),
    )


def _one_edit_away(word, target):
    """Whether word stands one edit from target.

    One substitution, one insertion, one deletion, or one
    transposition of two neighbouring characters.
    """
    if word == target:
        return False
    if abs(len(word) - len(target)) > 1:
        return False
    if len(word) == len(target):
        differing = [index for index in range(len(word))
                     if word[index] != target[index]]
        if len(differing) == 1:
            return True
        if len(differing) == 2:
            first, second = differing
            return second == first + 1 and \
                word[first] == target[second] and \
                word[second] == target[first]
        return False
    if len(word) > len(target):
        word, target = target, word
    index = 0
    while index < len(word) and word[index] == target[index]:
        index += 1
    return word[index:] == target[index + 1:]


def _is_near_marker(text):
    """The near marker forms.

    The recorded forms are a space before the colon, a semicolon
    in place of the colon, and the label in another letter case.
    A label standing one edit from the Status label, a one
    character typo, takes the same treatment: it opens like a
    status line and carries no element. A tab standing before
    the colon, alone or among spaces, is the space before the
    colon form with a tab in it, and a six letter label opening
    with the letters stat and standing two substitutions from
    the Status label is the one edit form at two edits: both
    take the same treatment.
    """
    if re.match(r"^Status[ \t]+:", text):
        return True
    if re.match(r"^Status;", text):
        return True
    match = re.match(r"^([A-Za-z]+):", text)
    if match and match.group(1).lower() == "status" and \
            match.group(1) != "Status":
        return True
    if match and 4 <= len(match.group(1)) <= 7 and \
            _one_edit_away(match.group(1).lower(), "status"):
        return True
    if match and len(match.group(1)) == 6 and \
            match.group(1).lower()[:4] == "stat" and \
            sum(1 for left, right in
                zip(match.group(1).lower(), "status")
                if left != right) == 2:
        return True
    return False


def _heading_info(line_text):
    # A prefix standing before a heading is absorbed: the
    # heading form is read from the text after any leading run
    # of byte order marks, spaces, and tabs, on every path, so
    # a mark combined with a space or a tab, or a space standing
    # alone, never deletes a heading.
    match = _HEADING_RE.match(line_text.lstrip("﻿ \t"))
    if not match:
        return None
    return len(match.group(1)), match.group(2)


def _numbered_heading(text):
    match = _NUMBERED_RE.match(text)
    if not match:
        return None
    return "DQ-" + match.group(1), int(match.group(1)), match.group(2)


def _corrupted_numbered_heading(text):
    """Whether a heading stands in numbered form with a corrupted
    identifier, beyond the strip class the header only branch
    already removes.

    The identifier token between the DQ prefix and the colon is
    read character by character: an ASCII digit stands as itself,
    a decimal digit of any other script stands as the digit it
    names, and any other character that is not a letter is
    dropped, as a mark, a format character, or a punctuation
    character standing inside the number. Where the token reads
    back as a nonempty digit string that differs from the token
    as written, the heading is a numbered heading whose
    identifier carries characters no entry form recognises. A
    token carrying a letter, or no digit at all, stands in no
    numbered form and is no corruption of one.
    """
    match = re.match(r"^DQ-([^:\s]+): (\S.*)$", text)
    if not match:
        return False
    token = match.group(1)
    if token.isascii() and token.isdigit():
        return False
    digits = []
    for char in token:
        if "0" <= char <= "9":
            digits.append(char)
        elif char.isdecimal():
            digits.append(str(unicodedata.digit(char)))
        elif char.isalpha():
            return False
    return bool(digits) and "".join(digits) != token


def _unnumbered_heading(text):
    """The named unnumbered entry form, and no other.

    The one unnumbered headed entry this version recognises is
    the named R-7 entry, under its literal heading text as
    measured. A heading in an R number form with any other
    number, or with the R-7 number under any other title, is no
    entry form: it takes the Warning and file level unit
    treatment under PIN-06.
    """
    if text != _NAMED_UNNUMBERED_HEADING:
        return None
    return "R-7", text[len("R-7 "):]


_HEADING_BY_RE = re.compile(
    r"(RULED|Ruled|SETTLED|Settled) by ([^.]+?)"
    r"( \d{4}-\d{2}-\d{2})?\s*$")
_HEADING_WORD_BY_RE = re.compile(
    r"\b(RULED|SETTLED|ORDERED|BANKED|CLOSED|PARKED|PRESENTED|OPEN|"
    r"Ruled|Settled|Ordered|Banked|Closed|Parked|Presented|Open)"
    r" by\b")
_HEADING_TAIL_WORD_RE = re.compile(
    r"\b(RULED|SETTLED|ORDERED|BANKED|CLOSED|PARKED|PRESENTED|OPEN|"
    r"Ruled|Settled|Ordered|Banked|Closed|Parked|Presented|Open)"
    r"( \d{4}-\d{2}-\d{2})?\s*$")
_ADDITION_THIS_ENTRY_RE = re.compile(
    r"^Addition to this entry\b", re.IGNORECASE)
_SEGMENT_STATE_CLAIM_RE = re.compile(
    r"\b(remains|stays|stands|is|was|left)\b[^.]{0,80}?"
    r"\b(open|settled|ruled|closed|banked|parked|presented)\b",
    re.IGNORECASE)


def _heading_borne(record):
    """The heading borne element of an entry, where one stands.

    Under PIN-05 the heading is a status bearing element where it
    carries status evidence: a heading outcome word, a decider
    named in the heading, or a ruling stated in the heading. The
    forms, in the order they are tried: a ruling or settlement
    stated in the heading in the by form at its end; an outcome
    word in the by form anywhere in the heading tail; an outcome
    word at the end of the heading, with a date after it where one
    stands; and a heading whose whole title is the one outcome
    word, classifiable or unclassifiable, as the MK-4 construction
    at plan Item 3, section 3.10, attack 3 states. An outcome word
    with no translation, as ORDERED, extracts an element with no
    disposition: the element stands, and PIN-04 governs it.

    Returns a pair of the disposition, or None, and the position of
    the outcome word within the heading line, or None where the
    heading carries no status evidence.
    """
    heading = record.heading
    prefix = "#" * record.heading_level + " "
    match = _HEADING_BY_RE.search(heading)
    if match:
        return (_DISPOSITION_WORDS[match.group(1).upper()],
                len(prefix) + match.start())
    match = _HEADING_WORD_BY_RE.search(heading)
    if match:
        return (_DISPOSITION_WORDS.get(match.group(1).upper()),
                len(prefix) + match.start())
    match = _HEADING_TAIL_WORD_RE.search(heading)
    if match:
        return (_DISPOSITION_WORDS.get(match.group(1).upper()),
                len(prefix) + match.start())
    title = (record.title or "").strip()
    if title and " " not in title and \
            title.replace("-", "").isalpha():
        at = heading.find(title)
        return (_DISPOSITION_WORDS.get(title.upper()),
                len(prefix) + (at if at >= 0 else 0))
    return None


def _addition_paragraphs_after_closing(record, closing_line):
    """Paragraphs labelled as additions to this entry, after a line.

    The paragraphs of the entry body that stand after the given
    closing Status line and open with an addition label naming this
    entry, by its number or as this entry, in file order.
    """
    paragraphs = []
    current = []
    for number, text in record.body_lines:
        if number <= closing_line:
            continue
        if text.strip() == "":
            if current:
                paragraphs.append(current)
                current = []
            continue
        current.append((number, text))
    if current:
        paragraphs.append(current)
    found = []
    for paragraph in paragraphs:
        first_text = paragraph[0][1]
        if _ADDITION_THIS_ENTRY_RE.match(first_text):
            found.append(paragraph)
            continue
        addition = _ADDITION_RE.match(first_text)
        if addition and addition.group(1) == str(record.identifier):
            found.append(paragraph)
    return found


def _is_note_section(text):
    """Whether a heading stands in a recorded note section form.

    The recorded forms are the forms the brief names at PIN-06:
    a heading opening with the word Note or Notes, an Amendment
    note heading, and the Manager addition note heading, in
    either of its written forms. A heading whose words merely
    contain the word note or notes in some other position stands
    in no recorded form and is no note section: it takes the
    recognition test, and where it names a single DQ entry as
    its subject it takes the Warning and file level unit
    treatment.
    """
    words = re.findall(r"[A-Za-z']+", text)
    if not words:
        return False
    lowered = [word.lower() for word in words]
    if lowered[0] in ("note", "notes"):
        return True
    if len(lowered) >= 2 and lowered[0] == "amendment" and \
            lowered[1] == "note":
        return True
    stripped = text.strip()
    if stripped.startswith("Manager's addition note") or \
            stripped.startswith("Manager addition note"):
        return True
    return False


def _failure(kinds, name, byte_count, line_count, digest,
             breached=None, missing=None, invalid_byte_offset=None):
    breached_limit = None
    measured = None
    breached_limits = []
    breached_measured_values = {}
    if breached:
        breached_limits = [item[0] for item in breached]
        breached_limit = breached[0][0]
        measured = breached[0][1]
        breached_measured_values = {
            item[0]: item[1] for item in breached}
    decision = ExitDecision(code=3, reason_classes=list(kinds))
    return FileLevelFailure(
        failure_kinds=list(kinds),
        input_name=name,
        byte_count=byte_count,
        line_count=line_count,
        digest=digest,
        breached_limit=breached_limit,
        measured_value=measured,
        breached_limits=breached_limits,
        breached_measured_values=breached_measured_values,
        missing_structure=missing,
        invalid_byte_offset=invalid_byte_offset,
        exit_decision=decision,
    )


class _EntryBuilder:
    """Collects the fields, blocks and elements of one entry."""

    def __init__(self, record, lines_by_number):
        self.record = record
        self.lines_by_number = lines_by_number
        self.elements = []
        self.blocks = []
        self.fields = []
        self.notes = []
        self.near = []
        self.occurrence_only = []
        self.inert_line_numbers = set()
        self.inert_blanked_texts = {}
        self.seen_line_start = False
        self.closing_status_line = None
        self.closing_status_block = None
        self.closed_seen = False

    def line_text(self, number):
        return self.lines_by_number[number]

    def blanked(self, numbered_lines):
        """The numbered lines with inert container matter blanked.

        Field recording reads this form, so a field label
        standing inside an HTML comment or a fenced code block
        is recorded as no field of the entry, while the genuine
        part of a line that opens a comment on the same line
        stands and is recorded. Element extraction reads the
        genuine lines and never this form.
        """
        return [(number, self.inert_blanked_texts.get(number, text))
                for number, text in numbered_lines]

    def add_field_lines(self, numbered_lines, skip_labels=None):
        for number, text in numbered_lines:
            if text.startswith("#") or text.startswith("- "):
                continue
            if text.startswith(_STATUS_MARKER) or _is_near_marker(text):
                continue
            match = _LABEL_RE.match(text)
            if not match:
                continue
            if match.group(1) != match.group(1).strip():
                # A space before the colon on a field label: the
                # recorded field forms carry no such space, and
                # the off form takes the near marker report the
                # Status form takes, instead of passing silently
                # as the true label.
                self.near.append(
                    NearMarkerOccurrence(line=number, text=text))
            label = match.group(1).strip()
            if skip_labels is not None and (
                    label.lower() in skip_labels):
                continue
            if "," in label or "." in label or ";" in label:
                continue
            if len(re.findall(r"\S+", label)) > 7:
                continue
            value = match.group(2) or ""
            self.fields.append(
                FieldOccurrence(label=label, value=value, line=number))

    def scan_line_occurrences(self, number, text, decision_block=None):
        """Collect the marker occurrences of one line.

        Returns True where the line is a line start Status line.
        """
        # A leading run of space, tab, and invisible space or
        # format characters standing before a line start marker
        # does not reclassify the occurrence: the marker is read
        # from the text after the run, at its own position. The
        # M8 cure read the marker after exactly one such
        # character; the run is the same form at any width.
        # The scan reads the line with its HTML comment segments
        # blanked (Step 17 fix wave 2, charge CH-16): a marker
        # standing inside a comment segment is container matter
        # and is no occurrence, while a marker standing in
        # genuine matter on the same line, before or after a
        # comment segment, is read at its own position.
        scanned = _mask_comment_segments(text)
        offset = 0
        effective = scanned
        run = _leading_status_run(scanned)
        if run and run < len(scanned) and (
                scanned[run:].startswith(_STATUS_MARKER)
                or scanned[run:].startswith(_VARIANT_MARKER)
                or _is_near_marker(scanned[run:])):
            offset = run
            effective = scanned[run:]
        if _is_near_marker(effective):
            self.near.append(
                NearMarkerOccurrence(line=number, text=text))
            return False
        if effective.startswith(_STATUS_MARKER) and \
                len(effective) > len(_STATUS_MARKER):
            separator = re.match(
                r"[ \t]*", effective[len(_STATUS_MARKER):]).group(0)
            if effective[len(_STATUS_MARKER)] != " " or \
                    "\t" in separator:
                # A separator other than the taught colon and
                # space, a tab or no space at all, takes the
                # near marker report instead of passing as the
                # true form. A separator run of plain spaces
                # stands as it stood; a run carrying a tab in
                # any position is the tab form, not a plain
                # space separator.
                self.near.append(
                    NearMarkerOccurrence(line=number, text=text))
                return False
        if scanned.startswith("Origin:"):
            return self._scan_origin_line(number, scanned,
                                          decision_block)
        starts = []
        for match in re.finditer(re.escape(_VARIANT_MARKER), effective):
            starts.append((match.start(), "variant", match.end()))
        for match in re.finditer(re.escape(_STATUS_MARKER), effective):
            starts.append((match.start(), "marker", match.end()))
        starts.sort()
        is_line_start = False
        for index, (start, flavour, end) in enumerate(starts):
            stop = starts[index + 1][0] if index + 1 < len(starts) \
                else len(effective)
            if flavour == "variant":
                verbatim = effective[start:stop]
                if stop < len(effective):
                    verbatim = verbatim.rstrip(" ")
                self.elements.append(_make_element(
                    kind="variant phrasing",
                    verbatim=verbatim,
                    disposition="Relative",
                    line=number,
                    position=start + offset,
                    occurrence_kind="variant",
                    own_text=verbatim,
                    decision_block=decision_block,
                ))
                continue
            value = effective[end:stop].lstrip(" ")
            if stop < len(effective):
                value = value.rstrip(" ")
            if value.strip() == "":
                # An empty Status value is not a phrasing: it
                # carries no element and derivation never reads
                # it. The occurrence itself still counts, on the
                # occurrence only channel, exactly once. A line
                # start empty value also takes the near marker
                # report, so the entry does not reach its
                # Ambiguous state with no finding naming the
                # line that caused it; an embedded empty marker
                # takes no report, as it stood.
                if start == 0:
                    is_line_start = True
                    self.seen_line_start = True
                    self.near.append(
                        NearMarkerOccurrence(line=number, text=text))
                self.occurrence_only.append(_make_element(
                    kind="non element occurrence",
                    verbatim=value,
                    disposition=None,
                    line=number,
                    position=start + offset,
                    occurrence_kind="line start" if start == 0
                    else "embedded",
                    own_text=value,
                    decision_block=decision_block,
                ))
                continue
            disposition = _disposition_from_value(value)
            if start == 0:
                is_line_start = True
                if self.seen_line_start:
                    kind = "later Status line"
                else:
                    kind = "line start Status line"
                    self.seen_line_start = True
                occurrence = "line start"
            else:
                kind = "tail paragraph element"
                occurrence = "embedded"
            element = _make_element(
                kind=kind,
                verbatim=value,
                disposition=disposition,
                line=number,
                position=start + offset,
                occurrence_kind=occurrence,
                own_text=value,
                decision_block=decision_block,
            )
            self.elements.append(element)
            if start == 0 and kind == "later Status line" and \
                    disposition in ("Ruled", "Settled", "Closed"):
                self.closing_status_line = number
                self.closing_status_block = decision_block
        return is_line_start

    def _scan_origin_line(self, number, text, decision_block=None):
        """The matter under an Origin label, tested by its own form.

        The Origin line is not an element by itself, under PIN-05:
        the matter under the label is tested under the marking form
        that carries it. A terminal Status value in the matter is a
        tail paragraph element where its value states a disposition,
        a closure, or a remaining open state of the entry. A terminal
        Status sentence whose value states no disposition, as the
        landing record form at brief section 5.2, PIN-01, form 4,
        carries no element at all. A decider form stated in the
        matter is an element of the labelled paragraph that carries
        it.
        """
        body = text[len("Origin:"):]
        has_marker = _STATUS_MARKER in body
        has_decider_form = bool(
            re.search(r"\b(Ruled|Settled) by:", body))
        if not has_marker and not has_decider_form:
            return False
        if has_marker:
            at = body.find(_STATUS_MARKER)
            value = body[at + len(_STATUS_MARKER):].lstrip(" ")
            disposition = _disposition_from_value(value)
            if disposition is None:
                # A terminal Status sentence whose value states
                # no disposition, the landing record form at
                # PIN-01 form 4, is no status bearing element
                # and PIN-04 does not reach it. Its marker
                # standing inside the line is still a status
                # occurrence for the verbatim appendix count
                # under PIN-14, one embedded occurrence, so the
                # occurrence is recorded on its own channel,
                # apart from the entry elements, and derivation
                # never reads it.
                self.occurrence_only.append(_make_element(
                    kind="non element occurrence",
                    verbatim=value,
                    disposition=None,
                    line=number,
                    position=len("Origin:") + at,
                    occurrence_kind="embedded",
                    own_text=value,
                    decision_block=decision_block,
                ))
            if disposition is not None:
                self.elements.append(_make_element(
                    kind="tail paragraph element",
                    verbatim=value,
                    disposition=disposition,
                    line=number,
                    position=len("Origin:") + at,
                    occurrence_kind="embedded",
                    own_text=value,
                    decision_block=decision_block,
                ))
                return False
            if not has_decider_form:
                return False
        found = _find_disposition(body)
        disposition = found[0] if found else None
        self.elements.append(_make_element(
            kind="labelled paragraph element",
            verbatim=body.lstrip(" "),
            disposition=disposition,
            line=number,
            position=len("Origin:"),
            occurrence_kind=None,
            own_text=body,
            decision_block=decision_block,
        ))
        return False

    def note_unrecognised_lead_in(self, paragraph):
        number, text = paragraph[0]
        match = re.match(r"^([A-Z][A-Za-z]+):[ ]", text)
        if not match:
            return
        label = match.group(1)
        if label in _KNOWN_SINGLE_LABELS:
            return
        span = Span(paragraph[0][0], paragraph[-1][0], "heading cut")
        self.notes.append(ParseNote(
            kind="unrecognised label form",
            text="a paragraph begins with the label " + label +
                 ", which is no named label form; its matter is body "
                 "text only",
            line_span=span,
            entry_identifier=str(self.record.identifier)
            if self.record.identifier is not None
            else self.record.heading,
        ))

    def process_paragraph(self, paragraph, decision_block=None,
                          in_block_segment=False):
        """Process one plain paragraph outside any block segment."""
        if not paragraph:
            return
        self.assessment_closure_element(paragraph, decision_block)
        first_number, first_text = paragraph[0]
        if self.closing_status_line is not None and \
                first_number > self.closing_status_line and \
                decision_block is None:
            self.record.post_status_blocks = True
        produced_line_start = False
        for number, text in paragraph:
            if self.scan_line_occurrences(number, text, decision_block):
                produced_line_start = True
        self.add_field_lines(self.blanked(paragraph))
        self.note_unrecognised_lead_in(paragraph)
        if produced_line_start:
            return
        if re.match(r"^(Remainder|Condition)\s*:", first_text.strip(),
                    re.IGNORECASE):
            # A Remainder or Condition label standing as its own
            # paragraph is an attachment line, not a statement:
            # it extracts no element of its own, and the
            # attachment pass reads it from the body lines.
            return
        label_match = _LABEL_RE.match(first_text)
        label = label_match.group(1).strip() if label_match else ""
        if label in _FIELD_PARAGRAPH_LABELS:
            return
        joined = "\n".join(item[1] for item in paragraph)
        if label in _LABEL_DISPOSITIONS:
            first_value = (label_match.group(2) or "") \
                if label_match else ""
            rest_matter = " ".join(
                item[1].strip() for item in paragraph[1:])
            if not first_value.strip() and not rest_matter.strip():
                # A decision label with no matter under it
                # performs no act: the ground of the labelled
                # form is that the matter under the label
                # performs the act the label names.
                return
        bold = _BOLD_LEAD_RE.match(first_text)
        if bold is not None:
            lead = bold.group(1)
            lead_hit = _find_disposition(lead)
            if lead_hit is not None or "Supersession:" in lead:
                disposition = lead_hit[0] if lead_hit else None
                alone = len(paragraph) == 1 and \
                    first_text.strip() == "**" + lead + "**"
                if alone and "Supersession:" in lead:
                    # The bold supersession block reading, plan
                    # Item 6, section 6.7: a bold line standing
                    # alone carrying a supersession is read as a
                    # decision block segment carrying the
                    # supersession statement, and that statement is
                    # the determining element for its entry. It is
                    # not read as a bold lead in paragraph element,
                    # because the line stands alone and leads no
                    # paragraph. The disposition is the state the
                    # superseding act carries: a Manager pick under
                    # Captain JP's delegation settles, a ruling by
                    # Captain JP rules.
                    decider, _decider_text = _decider_from_text(lead)
                    if decider == "a Manager grant form":
                        disposition = "Settled"
                    elif decider == "Captain JP":
                        disposition = "Ruled"
                    block = DecisionBlock(
                        marking_form="bold supersession segment",
                        span=Span(paragraph[0][0], paragraph[-1][0],
                                  "heading cut"),
                        heading_text=None,
                        post_status_flag=bool(
                            self.closing_status_line is not None and
                            paragraph[0][0] >
                            self.closing_status_line),
                    )
                    self.blocks.append(block)
                    block_index = len(self.blocks) - 1
                    element = _make_element(
                        kind="decision block matter",
                        verbatim=first_text,
                        disposition=disposition,
                        line=first_number,
                        position=0,
                        occurrence_kind=None,
                        own_text=joined,
                        statement=joined,
                        decision_block=block_index,
                    )
                    block.elements.append(element)
                    self.elements.append(element)
                    if disposition == "Closed":
                        self.closed_seen = True
                    return
                element = _make_element(
                    kind="bold lead in paragraph element",
                    verbatim=first_text,
                    disposition=disposition,
                    line=first_number,
                    position=0,
                    occurrence_kind=None,
                    own_text=joined,
                    statement=joined,
                    decision_block=decision_block,
                )
                self.elements.append(element)
                if disposition == "Closed":
                    self.closed_seen = True
                return
        hits = _statements_in_lines(paragraph)
        labelled = label in _DECISION_LABELS or \
            first_text.startswith("Addition to") or \
            first_text.startswith("Decision under")
        if not hits:
            if labelled and (label in _LABEL_DISPOSITIONS
                             or label == "Decision"):
                block = DecisionBlock(
                    marking_form="unheaded labelled paragraph",
                    span=Span(paragraph[0][0], paragraph[-1][0],
                              "heading cut"),
                    heading_text=None,
                    post_status_flag=bool(
                        self.closing_status_line is not None and
                        paragraph[0][0] > self.closing_status_line),
                )
                self.blocks.append(block)
                block_index = len(self.blocks) - 1
                element = _make_element(
                    kind="labelled paragraph element",
                    verbatim=first_text,
                    disposition=_LABEL_DISPOSITIONS.get(label),
                    line=first_number,
                    position=0,
                    occurrence_kind=None,
                    own_text=joined,
                    statement=first_text,
                    decision_block=block_index,
                    decider_text_override=None,
                )
                block.elements.append(element)
                self.elements.append(element)
            return
        if labelled:
            block = DecisionBlock(
                marking_form="unheaded labelled paragraph",
                span=Span(paragraph[0][0], paragraph[-1][0],
                          "heading cut"),
                heading_text=None,
                post_status_flag=bool(
                    self.closing_status_line is not None and
                    paragraph[0][0] > self.closing_status_line),
            )
            self.blocks.append(block)
            block_index = len(self.blocks) - 1
            for number, text, disposition, offset, statement in hits:
                if len(hits) == 1:
                    verbatim, own, stmt = text, joined, text
                else:
                    verbatim, own, stmt = statement, statement, \
                        statement
                element = _make_element(
                    kind="labelled paragraph element",
                    verbatim=verbatim,
                    disposition=disposition,
                    line=number,
                    position=offset,
                    occurrence_kind=None,
                    own_text=own,
                    statement=stmt,
                    decision_block=block_index,
                    decider_text_override=None,
                )
                block.elements.append(element)
                self.elements.append(element)
                if disposition == "Closed":
                    self.closed_seen = True
        else:
            for number, text, disposition, offset, statement in hits:
                if len(hits) == 1:
                    verbatim, own, stmt = text, joined, text
                else:
                    verbatim, own, stmt = statement, statement, \
                        statement
                element = _make_element(
                    kind="closing prose",
                    verbatim=verbatim,
                    disposition=disposition,
                    line=number,
                    position=offset,
                    occurrence_kind=None,
                    own_text=own,
                    statement=stmt,
                    decision_block=decision_block,
                )
                self.elements.append(element)
                if disposition == "Closed":
                    self.closed_seen = True
        self._terminal_closure_element(paragraph, joined)

    def _terminal_closure_element(self, paragraph, joined):
        """A plain paragraph that ends on its own closure sentence.

        Where a paragraph carries an earlier disposition statement
        and then closes itself with a final closure sentence, the
        closure is its own element, positioned at the sentence.
        """
        stripped = joined.rstrip()
        match = re.search(
            r"(?:^|\.\s)(Closed\.|This (?:item|entry) is closed\.)\s*$",
            stripped)
        if not match:
            return
        if self.elements and self.elements[-1].tuple[0] == "Closed":
            return
        for number, text in reversed(paragraph):
            at = text.find("Closed.")
            if at >= 0:
                element = _make_element(
                    kind="closing prose",
                    verbatim=text,
                    disposition="Closed",
                    line=number,
                    position=at,
                    occurrence_kind=None,
                    own_text=text,
                    statement=text,
                )
                self.elements.append(element)
                self.closed_seen = True
                return

    def process_block(self, heading_text, numbered_lines):
        """Process one H4 sub part block of the entry."""
        block = DecisionBlock(
            marking_form="H4 sub part",
            span=Span(numbered_lines[0][0] if numbered_lines else 0,
                      numbered_lines[-1][0] if numbered_lines else 0,
                      "heading cut"),
            heading_text=heading_text,
            post_status_flag=bool(
                self.closing_status_line is not None and
                numbered_lines and
                numbered_lines[0][0] > self.closing_status_line and
                self.closing_status_block != len(self.blocks)),
        )
        self.blocks.append(block)
        block_index = len(self.blocks) - 1
        if block.post_status_flag:
            self.record.post_status_blocks = True
        body = numbered_lines[1:]
        # The block body lines are scanned for field lines with
        # the open entry field labels skipped: a Question,
        # Options, Cost, or Blocks label inside a level 4
        # decision block is the block's own line, not a field of
        # the entry, and it satisfies no open field test of the
        # entry (Step 17 charge F-17-09). The decision evidence
        # labels a block exists to carry, its decider, ruling
        # text, outcome, and landing lines, are recorded as
        # before.
        self.add_field_lines(self.blanked(body),
                             skip_labels=_OPEN_FIELD_LABELS)
        segment = []

        def flush_segment(run):
            if not run:
                return
            self.assessment_closure_element(run, block_index)
            if self.closing_status_line is not None and \
                    self.closing_status_block == block_index:
                for number, text in run:
                    if number > self.closing_status_line and \
                            re.match(r"^(Implementation addition:|"
                                     r"Addition to|Correction)", text):
                        self.record.post_status_blocks = True
            for number, text in run:
                self.scan_line_occurrences(number, text, block_index)
            hits = _statements_in_lines(run)
            if not hits:
                return
            joined = "\n".join(item[1] for item in run)
            own = (heading_text or "") + "\n" + joined
            for number, text, disposition, offset, statement in hits:
                if len(hits) == 1:
                    verbatim, own_text, stmt = text, own, text
                else:
                    verbatim, own_text, stmt = statement, statement, \
                        statement
                element = _make_element(
                    kind="decision block matter",
                    verbatim=verbatim,
                    disposition=disposition,
                    line=number,
                    position=offset,
                    occurrence_kind=None,
                    own_text=own_text,
                    statement=stmt,
                    decision_block=block_index,
                )
                block.elements.append(element)
                self.elements.append(element)
                if disposition == "Closed":
                    self.closed_seen = True

        for number, text in body:
            if text.startswith(_STATUS_MARKER):
                flush_segment(segment)
                segment = []
                self.scan_line_occurrences(number, text, block_index)
            else:
                segment.append((number, text))
        flush_segment(segment)
        for element in self.elements:
            if element.decision_block == block_index:
                block.elements.append(element) \
                    if element not in block.elements else None
        return block

    def assessment_closure_element(self, numbered_lines,
                                   decision_block=None):
        """The assessment closure element of a paragraph.

        A paragraph carrying an explicit statement of closure in
        the form Closed as decided under DQ-148 bears that closure
        as an element of its entry: disposition Closed, decider
        assessment by cross reference, at the closure line.
        """
        for number, text in numbered_lines:
            at = text.find("Closed as decided under DQ-148")
            if at < 0:
                continue
            for element in self.elements:
                if element.line == number and \
                        element.tuple[0] == "Closed":
                    return
            core = ElementTuple(
                disposition="Closed",
                scope="Whole",
                condition=None,
                decider="assessment by cross reference",
                line=number,
            )
            self.elements.append(StatusBearingElement(
                kind="closing prose",
                verbatim=text,
                tuple=core,
                line=number,
                position_in_line=at,
                occurrence_kind=None,
                remainder_text=None,
                decider_text="assessment under DQ-148",
                statement=text,
                decision_block=decision_block,
                line_span=Span(number, number, "heading cut"),
            ))
            self.closed_seen = True
            return

    def attach_remainders_and_conditions(self, numbered_lines):
        """Attach Remainder and Condition label lines to an element."""
        ordered = sorted(
            self.elements, key=lambda item: (item.line,
                                             item.position_in_line))
        for number, text in numbered_lines:
            kind = None
            value = None
            attach_match = re.match(
                r"^(Remainder|Condition)\s*:\s*(.*)$",
                text.strip(), re.IGNORECASE)
            if attach_match:
                kind = attach_match.group(1).lower()
                value = attach_match.group(2).strip()
            elif text.strip().startswith("Item closed") or \
                    "closed, subject to" in text:
                index = text.find("subject to")
                if index < 0:
                    continue
                value = text[index + len("subject to"):].strip()
                value = value.split(";")[0].strip().rstrip(".")
                if not value:
                    continue
                kind = "condition"
            if kind is None:
                continue
            target = None
            for element in ordered:
                if element.line < number:
                    target = element
                else:
                    break
            if target is None:
                continue
            if kind == "remainder" and target.remainder_text is None:
                target.remainder_text = value
                if target.tuple[1] != "Part":
                    target.tuple = target.tuple._replace(scope="Part")
            elif kind == "condition" and target.tuple[2] is None:
                target.tuple = target.tuple._replace(condition=value)


_FENCE_RUN_RE = re.compile(r"(`{3,}|~{3,})")


def _blank_line_genuine(text):
    """Blank one line standing outside any container.

    Returns a triple: the blanked text, the fence state the
    line leaves behind (a character and run length pair, or
    None), and whether the line ends inside an HTML comment.

    A line whose stripped form opens with a fence run opens a
    fence and is blank whole. Otherwise the blanking unit is
    the comment segment, not the line (Step 17 fix wave 2,
    charge CH-16): each comment segment on the line is removed,
    genuine matter before, between, and after segments stands,
    and a segment left unclosed at the end of the line leaves
    the comment open for the lines under it, a comment
    reopened on the same line after a closed one included.
    """
    run = _FENCE_RUN_RE.match(text.strip())
    if run:
        return "", (run.group(1)[0], len(run.group(1))), False
    parts = []
    index = 0
    while True:
        opening = text.find("<!--", index)
        if opening < 0:
            parts.append(text[index:])
            return "".join(parts), None, False
        parts.append(text[index:opening])
        closing = text.find("-->", opening + 4)
        if closing < 0:
            return "".join(parts), None, True
        index = closing + 3


def _inert_blanked_texts(lines):
    """The blanked form of every line carrying container matter.

    Returns a mapping of line number to blanked text, holding
    an entry only for a line that carries inert matter. A line
    standing wholly inside a container, and a fence delimiter
    line, blank to the empty string. A line carrying both
    genuine matter and a comment segment blanks to its genuine
    matter alone, so a genuine field line that opens a comment
    on the same line is recorded for its genuine part and is
    not blanked whole (F-11R2-04).

    A fence closes only on a line that can close it: a run of
    the fence own character, at least as long as the opening
    run, with nothing after the run but whitespace. A shorter
    run, a run of the other character, and a run carrying an
    info string are fence content, not delimiters (F-11R2-01).

    The blanked lines are inert for exactly the two surfaces
    the M6 charges name: the presence tests and the field
    tests. Field recording reads blanked lines, and the body
    lines the model carries are the blanked lines, so
    container matter satisfies no presence test and counts as
    no field. Element extraction is not a charged surface: it
    reads the genuine lines, as it did before fix wave 1, so a
    disposition element standing inside a fence is extracted
    and derives its entry state, as the D3 repair bound
    stands. Heading recognition is untouched by this pass.
    """
    blanked = {}
    fence = None
    in_comment = False
    for index, text in enumerate(lines):
        number = index + 1
        if fence is not None:
            blanked[number] = ""
            run = _FENCE_RUN_RE.match(text.strip())
            if run and run.group(1)[0] == fence[0] and \
                    len(run.group(1)) >= fence[1] and \
                    not text.strip()[run.end():].strip():
                fence = None
            continue
        if in_comment:
            closing = text.find("-->")
            if closing < 0:
                blanked[number] = ""
                continue
            rest, fence, in_comment = _blank_line_genuine(
                text[closing + 3:])
            blanked[number] = rest.lstrip() if rest.strip() else ""
            continue
        if "<!--" not in text and \
                not _FENCE_RUN_RE.match(text.strip()):
            continue
        blanked_text, fence, in_comment = _blank_line_genuine(text)
        if blanked_text != text:
            blanked[number] = blanked_text \
                if blanked_text.strip() else ""
    return blanked


def _inert_line_numbers(lines):
    """The lines carrying container matter, by line number."""
    return set(_inert_blanked_texts(lines))


def _paragraphs(numbered_lines):
    """Split numbered lines into paragraphs on blank lines."""
    paragraphs = []
    current = []
    for item in numbered_lines:
        if item[1].strip() == "":
            if current:
                paragraphs.append(current)
                current = []
        else:
            current.append(item)
    if current:
        paragraphs.append(current)
    return paragraphs


def parse_queue(input_value, limits):
    """Parse the Input value under the Limits value.

    Returns the Queue file model, or the file level failure result
    where no model exists for the file.
    """
    if hasattr(sys, "set_int_max_str_digits"):
        # Plan Item 3, section 3.2, field 11, in its Step 12
        # correction: before any heading digit string is converted,
        # the run raises the integer string conversion limit to
        # 16,384, the per line limit, so a DQ number inside the
        # stated limits takes no refusal, no error, and no exception
        # on account of its digit count.
        sys.set_int_max_str_digits(16384)
    raw = input_value.raw_bytes
    name = input_value.input_name
    byte_count = len(raw)
    digest = hashlib.sha256(raw).hexdigest()

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        kinds = []
        breached = []
        if byte_count > limits.max_bytes:
            kinds.append("byte limit breach")
            breached.append(("max bytes", byte_count))
        kinds.append("invalid bytes")
        # The decoder knows the first invalid byte offset
        # exactly, in its start attribute: the refusal carries
        # that measured value, as the neighbouring refusals on
        # this surface carry theirs.
        return _failure(kinds, name, byte_count, None, digest,
                        breached=breached,
                        invalid_byte_offset=error.start)

    file_terminated = text.endswith("\n")
    lines = _partition_lines(text)
    line_count = len(lines)
    longest = 0
    for line in lines:
        if len(line) > longest:
            longest = len(line)

    breached = []
    kinds = []
    if byte_count > limits.max_bytes:
        kinds.append("byte limit breach")
        breached.append(("max bytes", byte_count))
    if line_count > limits.max_lines:
        kinds.append("line limit breach")
        breached.append(("max lines", line_count))
    if longest > limits.max_characters_per_line:
        kinds.append("per line limit breach")
        breached.append(("max characters per line", longest))
    if kinds:
        line_field = None if byte_count > limits.max_bytes \
            else line_count
        return _failure(kinds, name, byte_count, line_field, digest,
                        breached=breached)

    if line_count == 0:
        return _failure(
            ["empty file"], name, byte_count, 0, digest,
            missing="the file is empty: no queue header and no entry "
                    "heading is present")

    headings = []
    for index, line in enumerate(lines):
        info = _heading_info(line)
        if info is not None:
            headings.append((index + 1, info[0], info[1]))

    first_heading = headings[0] if headings else None
    # Brief section 5.3: the file header test is level and first
    # position only, with its text not tested. Any first heading at
    # level 1 is the queue header, whatever words it carries.
    queue_header_present = bool(
        first_heading and first_heading[1] == 1)

    def entry_form(level, heading_text):
        if level in (2, 3):
            numbered = _numbered_heading(heading_text)
            if numbered:
                return ("numbered", numbered)
            # The unnumbered form stands as an entry at level 2
            # as well as at level 3, as the numbered form does:
            # a copy of the named R-7 heading at level 2 is an
            # entry, not a section introduction.
            unnumbered = _unnumbered_heading(heading_text)
            if unnumbered:
                return ("unnumbered", unnumbered)
        return None

    has_entry_heading = any(
        entry_form(level, heading_text)
        for _number, level, heading_text in headings)

    if not has_entry_heading and not queue_header_present:
        return _failure(
            ["no recognisable queue structure"], name, byte_count,
            line_count, digest,
            missing="no queue header and no entry heading "
                    "is present")
    if not has_entry_heading and queue_header_present:
        for _number, _level, heading_text in headings:
            cleaned = re.sub(
                "[̀-ͯ​‌‍⁠﻿]", "",
                heading_text)
            # The class above reads: combining diacritical
            # marks, zero width space, non joiner and joiner,
            # word joiner, and the byte order mark.
            if (cleaned != heading_text and
                    _numbered_heading(cleaned)) or \
                    _corrupted_numbered_heading(heading_text):
                # A heading in entry form whose identifier
                # carries characters no entry form recognises:
                # the enumerated strip class above, or a
                # corruption the wider reading at
                # _corrupted_numbered_heading recognises, as a
                # non ASCII digit form or a mark outside the
                # strip class standing inside the number. The
                # file is not header only, it carries an entry
                # body under a heading the tool cannot raise.
                return _failure(
                    ["no recognisable queue structure"], name,
                    byte_count, line_count, digest,
                    missing="a heading in entry form is present "
                            "but its identifier carries characters "
                            "no entry form recognises, and no entry "
                            "heading in a recognised form is present")
        return _failure(
            ["header only"], name, byte_count, line_count, digest,
            missing="a queue header is present but no entry heading "
                    "in a numbered or unnumbered entry heading form "
                    "is present")

    def is_section_introduction(position):
        number, level, heading_text = headings[position]
        # The section a heading at level 2 heads runs to the
        # next level 2 heading that is not itself an entry
        # heading: entry headings stand at level 2 as well as
        # at level 3, under PIN-06, and a level 2 entry heading
        # inside the window is one of the entries the section
        # holds, not its end. A scan that stops at the first
        # level 2 heading of any form misreads a section whose
        # first held entry stands at level 2, as the reversed
        # tail of WV-2 puts DQ-171 first under its introduction.
        for later in headings[position + 1:]:
            if later[1] == 2 and not entry_form(later[1], later[2]):
                stop = later[0]
                break
        else:
            stop = line_count + 1
        window = []
        for other in headings[position + 1:]:
            if other[0] >= stop:
                break
            window.append(other)
        if not any(entry_form(other[1], other[2])
                   for other in window):
            return False
        if any(other[1] == 3 and entry_form(other[1], other[2])
               for other in window):
            return True
        # The window holds entry headings at level 2 only. Such
        # a heading proves a section where the tested heading
        # stands in the body of the file, at or after the first
        # entry heading: a level 2 heading standing before the
        # first entry, with only a level 2 entry after it, heads
        # no section and stands unmatched, as the random
        # heading form before the first entry pins.
        first_entry_line = None
        for other in headings:
            if entry_form(other[1], other[2]):
                first_entry_line = other[0]
                break
        return first_entry_line is not None \
            and number >= first_entry_line

    starts = []
    started = False
    current_kind = "file header"
    for position, (number, level, heading_text) in enumerate(headings):
        form = entry_form(level, heading_text)
        if form:
            starts.append((number, "entry", (level, heading_text, form)))
            started = True
            current_kind = "entry"
            continue
        if level == 1:
            if position == 0:
                continue
            starts.append((number, "file header",
                           (level, heading_text, None)))
            started = True
            current_kind = "file header"
            continue
        if level == 2:
            if _is_note_section(heading_text):
                starts.append((number, "orphan note",
                               (level, heading_text, None)))
                started = True
                current_kind = "orphan"
                continue
            if is_section_introduction(position):
                starts.append((number, "section introduction",
                               (level, heading_text, None)))
                started = True
                current_kind = "section introduction"
                continue
            starts.append((number, "orphan unmatched",
                           (level, heading_text, None)))
            started = True
            current_kind = "orphan"
            continue
        if level == 4 and current_kind == "entry":
            continue
        if level == 3 and _is_note_section(heading_text):
            starts.append((number, "orphan note",
                           (level, heading_text, None)))
            started = True
            current_kind = "orphan"
            continue
        starts.append((number, "orphan unmatched",
                       (level, heading_text, None)))
        started = True
        current_kind = "orphan"

    units = []
    unit_ranges = []
    if starts and starts[0][0] > 1:
        unit_ranges.append((1, starts[0][0] - 1, "file header", None))
    elif not starts:
        unit_ranges.append((1, line_count, "file header", None))
    for index, (number, kind, info) in enumerate(starts):
        end = starts[index + 1][0] - 1 if index + 1 < len(starts) \
            else line_count
        unit_ranges.append((number, end, kind, info))

    lines_by_number = {}
    for index, line in enumerate(lines):
        lines_by_number[index + 1] = line

    entries = []
    entries_by_id = {}
    orphans = []
    parse_notes = []
    h4_count = 0
    current_section = None
    builders = {}
    number_ledger = {}
    cr_tails = {}
    inert_texts = _inert_blanked_texts(lines)
    inert = set(inert_texts)

    def unit_text(start, end):
        return "\n".join(lines_by_number[number]
                         for number in range(start, end + 1))

    for start, end, kind, info in unit_ranges:
        span = Span(start, end, "heading cut")
        if kind == "section introduction":
            current_section = info[1]
            units.append(Unit(kind="section introduction", span=span,
                              heading_text=info[1],
                              text=unit_text(start, end)))
            continue
        if kind == "file header":
            heading_text = None
            if info is not None:
                heading_text = info[1]
            elif first_heading and first_heading[0] >= start and \
                    first_heading[0] <= end:
                heading_text = first_heading[2]
            units.append(Unit(kind="file header", span=span,
                              heading_text=heading_text,
                              text=unit_text(start, end)))
            continue
        if kind in ("orphan note", "orphan unmatched"):
            level, heading_text, _form = info
            if kind == "orphan note":
                orphan_kind = "note section"
                unmatched = False
            else:
                orphan_kind = "other file level segment"
                unmatched = True
            segment_lines = [(number, lines_by_number[number])
                             for number in range(start, end + 1)]
            named = []
            for _number, segment_text in segment_lines:
                for token in _DQ_TOKEN_RE.findall(segment_text):
                    if token not in named:
                        named.append(token)
                for token in _R_TOKEN_RE.findall(segment_text):
                    if token not in named:
                        named.append(token)
            claims = []
            segment_joined = "\n".join(
                item[1] for item in segment_lines)
            if "governs" in segment_joined:
                statement = ""
                for _number, segment_text in segment_lines:
                    if "governs" in segment_text:
                        statement = segment_text
                        break
                claim_named = []
                for _number, segment_text in segment_lines:
                    if segment_text.startswith("- "):
                        for token in _DQ_TOKEN_RE.findall(segment_text):
                            if token not in claim_named:
                                claim_named.append(token)
                claims.append(SegmentClaim(
                    named_entries=claim_named or named,
                    statement=statement))
            for _number, segment_text in segment_lines:
                # A state claim in the Manager addition note form:
                # a bullet naming one entry as its subject and
                # stating that entry's state, as the note at the
                # pin states DQ-001 and DQ-002 as still open
                # against their own ruled bodies. PIN-09 covers a
                # governing or state claim alike, and the claim is
                # recorded here, where the segment is built, in
                # the same shape as the governing claim above.
                bullet = re.match(r"^- (DQ-\d{3})\b", segment_text)
                if not bullet:
                    continue
                target = bullet.group(1)
                if any(target in claim.named_entries
                       for claim in claims):
                    continue
                if _SEGMENT_STATE_CLAIM_RE.search(segment_text):
                    claims.append(SegmentClaim(
                        named_entries=[target],
                        statement=segment_text))
            segment = OrphanSegment(
                kind=orphan_kind,
                span=span,
                heading_text=heading_text,
                named_entries=named,
                claims=claims,
                unmatched_heading=unmatched,
                lines=segment_lines,
            )
            orphans.append(segment)
            units.append(Unit(kind=orphan_kind, span=span,
                              heading_text=heading_text,
                              text=unit_text(start, end)))
            if unmatched:
                parse_notes.append(ParseNote(
                    kind="unmatched heading",
                    text="the heading " + heading_text +
                         " matches no entry form, no known file "
                         "level form and no sub part form; its lines "
                         "stand in an orphan segment",
                    line_span=Span(start, start, "heading cut"),
                ))
            continue
        level, heading_text, form = info
        if form[0] == "numbered" and "\r" in heading_text:
            # A lone carriage return joining the heading line
            # and a Status line into one logical line: the
            # heading stands on its own part, and the Status
            # parts are scanned as the entry Status lines they
            # are, so each occurrence is counted exactly once.
            # Every tail part is scanned, not only the first:
            # a part whose marker stands behind a byte order
            # mark is selected on its mark stripped form and
            # passed whole, so the scan reads the marker at its
            # own position, and a part carrying a near marker or
            # a marker in another letter case is selected as
            # well, so the damaged marker takes the near marker
            # report it takes at every body position instead of
            # passing in silence.
            parts = heading_text.split("\r")
            tails = []
            for part in parts[1:]:
                candidate = part.lstrip("﻿")
                if candidate.startswith(_STATUS_MARKER) or \
                        candidate.startswith(_VARIANT_MARKER) or \
                        _is_near_marker(candidate):
                    tails.append(part)
            if tails:
                main_numbered = _numbered_heading(parts[0])
                if main_numbered:
                    form = ("numbered", main_numbered)
                    heading_text = parts[0]
                    cr_tails[start] = tails
        form_kind, form_data = form
        if form_kind == "numbered":
            identifier = DQNumber(form_data[1], form_data[0])
            title = form_data[2]
            number_ledger.setdefault(form_data[1], []).append(
                identifier)
        else:
            identifier = heading_text
            title = form_data[1]
        record = EntryRecord(
            identifier=identifier,
            heading=heading_text,
            heading_level=level,
            heading_line=start,
            title=title,
            spans=[span],
            section=current_section,
        )
        entries.append(record)
        if identifier is not None:
            entries_by_id.setdefault(str(identifier), record)
        builders[start] = _EntryBuilder(record, lines_by_number)
        builders[start].inert_line_numbers = inert
        builders[start].inert_blanked_texts = inert_texts

    if builders:
        # A Status line standing in the file header or a section
        # introduction stands in no entry: it takes the near
        # marker report on the first entry, so the line is not
        # dropped in silence.
        first_builder = builders[min(builders)]
        for start, end, kind, info in unit_ranges:
            if kind not in ("file header", "section introduction"):
                continue
            for number in range(start, end + 1):
                text = lines_by_number[number]
                # The marker is read after a leading run of the
                # same characters as at an entry Status line, at
                # any width: the one character reading let a two
                # space preamble line escape this report while
                # its zero and one space forms took it.
                lead = text[_leading_status_run(text):]
                if lead.startswith(_STATUS_MARKER) or \
                        _is_near_marker(lead):
                    first_builder.near.append(
                        NearMarkerOccurrence(line=number, text=text))

    for index, line in enumerate(lines):
        info = _heading_info(line)
        if info and info[0] == 4:
            number = index + 1
            for start, end, kind, _info in unit_ranges:
                if kind == "entry" and start <= number <= end:
                    h4_count += 1
                    break

    pending_additions = []
    for start, end, kind, info in unit_ranges:
        if kind != "entry":
            continue
        builder = builders[start]
        record = builder.record
        body = [(number, lines_by_number[number])
                for number in range(start + 1, end + 1)]
        if start in cr_tails:
            for tail in cr_tails[start]:
                builder.scan_line_occurrences(start, tail)
        process_body = [(number, inert_texts.get(number, text))
                        for number, text in body]
        # The body lines the model carries are the processed
        # lines: container matter stands blank in them, so the
        # presence tests and the field tests, which read the
        # body lines and the recorded fields, take no container
        # matter as entry matter. Element extraction reads the
        # genuine body lines below, as it did before fix wave 1:
        # the blanking governs the two charged surfaces only.
        record.body_lines = list(process_body)
        blanked_by_number = dict(process_body)
        chunks = []
        chunk = []
        block = None
        for item in body:
            info_line = _heading_info(blanked_by_number[item[0]])
            if info_line and info_line[0] == 4:
                if block is not None:
                    chunks.append(("block", block))
                elif chunk:
                    chunks.append(("plain", chunk))
                chunk = []
                block = [item]
            elif block is not None:
                block.append(item)
            else:
                chunk.append(item)
        if block is not None:
            chunks.append(("block", block))
        elif chunk:
            chunks.append(("plain", chunk))

        for chunk_kind, chunk_lines in chunks:
            if chunk_kind == "block":
                heading_text = _heading_info(chunk_lines[0][1])[1]
                builder.process_block(heading_text, chunk_lines)
                continue
            for paragraph in _paragraphs(chunk_lines):
                first_text = paragraph[0][1]
                addition = _ADDITION_RE.match(first_text)
                if addition and addition.group(1) != str(
                        record.identifier):
                    pending_additions.append(
                        (addition.group(1), paragraph, record))
                    continue
                if addition and builder.closed_seen:
                    continue
                if first_text.startswith("Correction") and \
                        builder.closed_seen:
                    continue
                builder.process_paragraph(paragraph)

    for target_id, paragraph, source_record in pending_additions:
        target = entries_by_id.get(target_id)
        if target is None:
            continue
        span = Span(paragraph[0][0], paragraph[-1][0],
                    "label reattachment", True)
        target.spans.append(span)
        target.body_lines = sorted(
            target.body_lines + [(number, inert_texts.get(number,
                                                          text))
                                 for number, text in paragraph],
            key=lambda item: item[0])
        note = ParseNote(
            kind="label reattachment",
            text="a paragraph labelled for " + target_id +
                 " stands outside its span and is reattached to it",
            line_span=Span(paragraph[0][0], paragraph[-1][0],
                           "label reattachment", True),
            entry_identifier=target_id,
        )
        parse_notes.append(note)
        target.parse_notes.append(note)
        builder = builders[target.heading_line]
        if not builder.closed_seen:
            builder.process_paragraph(paragraph)
        source_record.body_lines = [
            item for item in source_record.body_lines
            if not (paragraph[0][0] <= item[0] <= paragraph[-1][0])]

    for start, end, kind, info in unit_ranges:
        if kind != "entry":
            continue
        builder = builders[start]
        record = builder.record
        if builder.closing_status_line is not None:
            additions = _addition_paragraphs_after_closing(
                record, builder.closing_status_line)
            for paragraph in additions:
                span = Span(paragraph[0][0], paragraph[-1][0],
                            "label reattachment", True)
                record.spans.append(span)
                note = ParseNote(
                    kind="label reattachment",
                    text="a paragraph labelled as an addition to "
                         "this entry stands after its closing "
                         "Status line and is reattached to it",
                    line_span=Span(paragraph[0][0], paragraph[-1][0],
                                   "label reattachment", True),
                    entry_identifier=str(record.identifier)
                    if record.identifier is not None
                    else record.heading,
                )
                parse_notes.append(note)
                record.parse_notes.append(note)
                if not any(paragraph[0][0] <= element.line <=
                           paragraph[-1][0]
                           for element in builder.elements):
                    # The addition paragraphs are read from the
                    # carried body lines, which stand blanked at
                    # container lines: element extraction reads
                    # the genuine lines of the paragraph instead,
                    # as at every other extraction point.
                    builder.process_paragraph(
                        [(number, lines_by_number[number])
                         for number, _text in paragraph])
            if additions and record.spans and \
                    record.spans[0].end_line > \
                    builder.closing_status_line:
                primary = record.spans[0]
                record.spans[0] = Span(
                    primary.start_line, builder.closing_status_line,
                    primary.boundary_basis, primary.non_contiguous)
        borne = _heading_borne(record)
        if borne is not None:
            disposition, position = borne
            element = _make_element(
                kind="heading borne evidence",
                verbatim=record.heading,
                disposition=disposition,
                line=record.heading_line,
                position=position,
                occurrence_kind=None,
                own_text=record.heading,
                statement=record.heading,
            )
            builder.elements.append(element)

        def assembled_key(element):
            # PIN-02: elements stand in assembled order, the in
            # place elements in file order first, then the
            # elements of the reattached spans in the order the
            # spans were collected, each span flagged not
            # contiguous. Raw file position orders only within
            # one span, never across the assembled entry.
            for index, span in enumerate(record.spans):
                if span.start_line <= element.line <= span.end_line:
                    return (index, element.line,
                            element.position_in_line)
            return (0, element.line, element.position_in_line)

        builder.elements.sort(key=assembled_key)
        record.status_elements = builder.elements
        record.decision_blocks = builder.blocks
        record.fields = builder.fields
        record.near_marker_occurrences = builder.near
        record.occurrence_only_elements = builder.occurrence_only
        record.parse_notes = record.parse_notes + builder.notes
        parse_notes.extend(builder.notes)
        builder.attach_remainders_and_conditions(
            [(number, lines_by_number[number])
             for number, _text in record.body_lines])
        has_body_line = any(
            _number > record.heading_line
            for _number, _text in record.body_lines)
        heading_is_last_line = record.heading_line == line_count
        # The cut off form is narrower than an unterminated
        # file: the entry is cut off only where its last body
        # line is itself cut off in form, under
        # _final_line_is_cut_off. A file whose final line
        # stands whole and merely carries no line feed
        # terminator, or a lone carriage return in the
        # terminator position, is not cut off at all, under
        # the terminator rule in _partition_lines, and no
        # marker question arises for its last entry.
        cut_off = bool(
            not file_terminated and has_body_line and record.spans
            and max(span.end_line for span in record.spans) ==
            line_count
            and _final_line_is_cut_off(lines_by_number[line_count]))
        # The unparsed marker, under the Entry shape at brief
        # section 5.5 and PIN-05: the express exception is the
        # heading borne determining element, the element PIN-05
        # extracts from the heading. A body element of a cut off
        # entry does not save it, because the body is not whole
        # and no body element can be certified as determining
        # over a remainder that may have stood in the cut off
        # part, as the WV-8 truncation form at brief section
        # 5.8 states in full. That reasoning reaches only an
        # entry whose last body line is cut off in form: where
        # the file ends on a whole body line, as it ends on a
        # complete Status line carrying its element, the entry
        # is not in the cut off form at all, and the element
        # extracted from that line governs under the exception
        # the Entry shape and the plan at Item 3 state for an
        # element extracted from any element of the entry.
        record.unparsed = bool(
            (heading_is_last_line or cut_off)
            and not any(
                element.kind == "heading borne evidence"
                for element in builder.elements))
        date = _DATE_RE.search(record.heading)
        if date:
            record.date_text = date.group(0)
        else:
            for _number, text in record.body_lines:
                if text.startswith(("Source:", "Origin:", "Ruled by:",
                                    "Settled by:")):
                    found_date = _DATE_RE.search(text)
                    if found_date:
                        record.date_text = found_date.group(0)
                        break

    header_text = ""
    if queue_header_present and first_heading is not None:
        header_text = lines_by_number[first_heading[0]]
    facts = FileHeaderFacts(header_text)
    return QueueFileModel(
        header_facts=facts,
        units=list(units),
        entries=entries,
        orphan_segments=orphans,
        parse_notes=parse_notes,
        unassigned_lines=[],
        double_assigned_lines=[],
        h4_sub_heading_count=h4_count,
        lines=lines,
        unmatched_headings=[
            segment for segment in orphans if segment.unmatched_heading],
        input_name=name,
        source_designation="live",
        raw_bytes=raw,
        line_count=line_count,
        byte_count=byte_count,
        digest=digest,
        number_ledger=number_ledger,
    )
