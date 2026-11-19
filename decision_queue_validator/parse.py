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

import functools
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
_DATE_RE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
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


# The one leading run set stated at the round 3 triage ruling,
# section 26 ruling (d), applied at the heading prefix surface,
# the Status marker leading surface, and the separator surface:
# the cured set above together with a vertical tab, a form
# feed, U+200C, U+200D, U+2060, U+00AD, U+180E, U+2028, and
# U+0085, and combining marks as a class. The no break space
# and the zero width space stand in the cured set above.
_LEADING_RUN_EXTRA = "\x0b\x0c\u200c\u200d\u2060\u00ad\u180e\u2028\u0085"


@functools.lru_cache(maxsize=None)
def _in_leading_run(char):
    # The run characters are read by Unicode class, not by
    # enumerated list (Step 17 round 4 triage, record section
    # 38 ruling (e)), on the ground restated once for every
    # surface at record section 52 ruling (a): a character
    # stands in the run ground when it presents no visible
    # glyph, the categories Cn, Co, Cf, Cc (the governed
    # terminators excepted, and no terminator can stand in a
    # run position inside a partitioned line), Zs, Zl, Zp,
    # Mn, Mc, and Me, together with any character, in any
    # category, whose Unicode name carries BLANK, FILLER,
    # FILL, or REPLACEMENT, read at _is_blank_presenting.
    # The private use class Co stands inside the ground at
    # every surface, decided expressly at that ruling.
    # The classification is a pure function of the one
    # character, and it is cached on the character (Step 17
    # fix wave 10, CH-271): the near marker reading below
    # classifies every character of the label before a
    # line's first colon, so a long line closed by a colon
    # paid the full classification, its Unicode name read
    # included, once per character per scan, at a constant
    # factor of about 3.4 times the colon free cost. The
    # cache returns the identical classification for every
    # character on every construction; no reading changes.
    return char in _LEADING_STATUS_CHARS or \
        char in _LEADING_RUN_EXTRA or \
        unicodedata.category(char).startswith("M") or \
        unicodedata.category(char) in \
        ("Cf", "Cc", "Zl", "Zp", "Zs", "Cn", "Co") or \
        _is_blank_presenting(char)


def _leading_status_run(text):
    """The length of the leading run of the characters above."""
    index = 0
    while index < len(text) and _in_leading_run(text[index]):
        index += 1
    return index


@functools.lru_cache(maxsize=None)
def _is_blank_presenting(char):
    """Whether a character presents as blank, read from its
    Unicode name: a character in any category whose name
    carries BLANK, FILLER, FILL, or REPLACEMENT (a braille
    pattern blank, the hangul fillers, an object replacement
    character, the gap fillers of category Po, an ideographic
    half fill space), together with the null notehead, whose
    name names a null, absent, notehead and which presents
    no visible glyph. The name limb stands inside the run
    ground restated at record section 52 ruling (a) for
    charges CH-77 and CH-79: at the Status leading and
    separator surfaces such a character takes the near
    marker signal rather than a silent demotion or a silent
    folded extraction, on the cure bounds stated for charges
    CH-55 and CH-56 at record section 38 and restated for
    round 5 at record section 52."""
    name = unicodedata.name(char, "")
    return "BLANK" in name or "FILLER" in name or \
        "FILL" in name or "REPLACEMENT" in name or \
        "NULL NOTEHEAD" in name


def _separator_run(text):
    """The separator run at the head of the text after a Status
    marker: a run read on the one run ground stated at
    _in_leading_run (round 4 charge CH-56, on the ruling (e)
    class ground, restated at record section 52 ruling (a)
    for round 5 charge CH-79), whitespace and every character
    of that ground, so a control character, an unassigned or
    private use character, or a name limb character behind a
    leading plain space stands in the run and takes the near
    marker report where the earlier class let it fold into
    the value in silence."""
    index = 0
    while index < len(text) and (
            text[index].isspace() or _in_leading_run(text[index])):
        index += 1
    return text[:index]

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


def _content_carries_cut_reference(content):
    """Whether a text carries a DQ reference token that stands
    cut in form: a reference of fewer than three digits, or
    the DQ prefix standing with no digits after it. A full
    reference, three or more digits, carries no such reading.
    The labelled branch of the final line test and the Blocks
    branch already test a token for reference completeness in
    their own forms; this reading states the same test for
    the heading and bullet contents (Step 17 round 5, charge
    CH-81, ATK5-2-04)."""
    for reference in re.findall(r"DQ-[0-9]+", content):
        if re.fullmatch(r"DQ-[0-9]{3,}", reference) is None:
            return True
    return re.search(r"\bDQ-(?![0-9])", content) is not None


def _final_line_is_cut_off(line_text, inside_fence=False,
                           inside_comment=False,
                           previous_line=None):
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
    further closed forms: a bullet item, which is complete
    in item form with no sentence close, its content read
    under the fragment and joining word guards; a line
    complete in a structural form the tool itself teaches, a
    heading closing on its text or a fence delimiter closing
    on its run; and a line closing on a balanced bracket
    group, whose closing bracket is its terminal mark. A byte order mark standing on the line is
    inert, as it is in every other position this slice reads,
    and takes no part in the test. A label is read in its
    lower case form as well as its capital form, so a complete
    line under a lower case label is judged on its value, not
    on the label case.

    Round 5 limbs (charge CH-81, record section 52): a
    labelled line carrying no value stands whole, the Status
    and variant members of that family standing cut in their
    own terms above as this docstring states; a final line
    standing inside a code fence stands whole as fence
    content, on the inside_fence argument the caller reads
    at _line_stands_inside_fence; complete lines in the
    structural forms of ATK5-2-01 (an HTML comment closing on
    its closing mark, a table row closing on its final pipe,
    a blockquote line, a setext underline of equals signs, a
    link reference definition, a footnote definition) stand
    whole in their own closing forms, under the fragment,
    joining word, and reference completeness guards stated
    at their branches, so a cut member of a newly reached
    form does not stand whole; the bullet marker set carries
    the parenthesis numbered marker beside the digits and
    full stop form; and a heading or bullet content carrying
    a cut DQ reference stands cut, the heading limb reaching
    level 4 and below only.

    Round 6 limbs (charge CH-95, record section 58): the
    structural branches disregard a trailing run of the
    ruling (a) ground classes after the closing mark, and
    the prose branch disregards such a run after the
    sentence closing punctuation; a final line standing
    inside an HTML comment stands whole as comment matter,
    on the inside_comment argument the caller reads at
    _line_stands_inside_comment; a labelled line whose only
    value matter is a run character stands as no value; the
    Blocks reading drops the empty part between two
    adjacent boundaries; the bullet marker set carries the
    parenthesised marker and the bracket marker; and the
    completeness reading reaches a dash setext underline in
    underline position, on the previous_line argument, and
    an underscore thematic break in its own closing form.

    Round 7 limbs (charges CH-116 to CH-120, record
    section 66): a labelled line whose only value matter
    is a run of the ground classes standing directly after
    the colon, with no space, is read on its label and
    stands as no value, as the spaced form of the limb
    above does; the prose branch disregards a trailing run
    before its closing quote and bracket strip as well as
    after it, so a run standing after a closing character
    hides no sentence close; the bullet marker set carries
    the single letter forms and the roman numeral and full
    stop form; and the table reading reaches a row closing
    on its final pipe in the form carrying no leading pipe
    as well as in the form carrying one.

    Round 8 limbs (charges CH-173 to CH-175, record
    section 77): the prose branch reads its closing
    characters and its trailing run in alternation until
    the end of the line stands stable, so a run standing
    between two closing characters hides no sentence
    close, and its closing character set carries the right
    guillemet and the asterisk beside the standing members,
    so a sentence closing on a closing character of that
    widened set is read; and the bullet marker set carries
    the roman numeral and closing parenthesis form, the
    parenthesised roman form, and the bracket form for a
    letter or a roman numeral.

    Round 9 limbs (charges CH-215 to CH-218, record
    section 81): the closing character set of the prose
    branch carries the single guillemet, the underscore,
    the backtick, the left double quotation mark, the
    fullwidth closing parenthesis, and the closing corner
    bracket beside the standing members, and its sentence
    close test carries the single character ellipsis
    beside the full stop, the question mark, and the
    exclamation mark; the bullet marker set carries the
    titlecase form of the roman numeral beside its two
    uniform cases, in every closing form the set reaches;
    and the bracket group reading strips the right
    guillemet beside its standing quote characters.

    Round 10 limbs (charges CH-257 to CH-263, record
    section 83): the closing character set of both
    branches carries eight further members beside the
    standing members (the left guillemet, the single
    left guillemet, the closing white corner bracket,
    the closing black lenticular bracket, the fullwidth
    closing bracket, the fullwidth closing brace, the
    tilde of a strikethrough span, and the closing angle
    bracket), and every sentence close test of both
    branches carries seven further marks beside the
    standing marks (the ideographic full stop, the
    fullwidth exclamation mark, the fullwidth question
    mark, the fullwidth full stop, the interrobang, the
    two dot leader, and the midline horizontal
    ellipsis); the bullet marker set carries the
    titlecase Lx tens family, a mixed case form of the
    standard roman numeral, and the single character
    Unicode roman numerals, in the closing forms the
    charges name; the bracket group strip of the prose
    branch carries the charged closing characters of
    the sentence strip beside its standing members and
    disregards a trailing run in alternation with them;
    and the labelled branch takes its bracket group
    probe of charge CH-262 as its own docstring states.
    """
    text = line_text
    if text.endswith("\r"):
        text = text[:-1]
    text = text.replace("\ufeff", "")
    stripped = text.strip()
    if not stripped:
        return False
    # The line is read behind the same leading run the
    # governed surfaces read (Step 17 round 4, charge
    # CH-57, ATK4-2-01): a final line standing behind a
    # leading run character of the format or mark classes
    # is read in the form its terminated twin is read in,
    # under the one run set at _in_leading_run, before any
    # of the completeness tests below. The members of that
    # set the plain strip already covered stand as before.
    stripped = stripped[_leading_status_run(stripped):]
    if not stripped:
        return False
    if inside_fence:
        # A final line standing inside a code fence is fence
        # content, as the parser reads it on every other line:
        # it is inert entry matter and stands whole in that
        # form, whatever its prose shape (Step 17 round 5,
        # charge CH-81, ATK5-2-02). The fence opener standing
        # as the final line itself stands outside this limb:
        # no fence stands open before it, and its reading
        # stands as the delimiter and prose branches give it.
        return False
    if inside_comment:
        # A final line standing inside an HTML comment is
        # comment matter, as the parser reads it on every
        # other line: it stands whole in that form, on the
        # posture of the fence content limb above (Step 17
        # round 6, charge CH-95, ATK6-2-03). The comment
        # opener standing as the final line itself stands
        # outside this limb: no comment stands open before
        # it, and its reading stands as the prose branch
        # gives it.
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
    if label_match is None:
        # A run of the ground classes standing directly
        # after the colon, with no space, matches neither
        # value alternative of _LABEL_RE, whose value group
        # reads one or more plain spaces after the colon
        # followed by the value, or nothing after the colon
        # at all, so a labelled line whose only value matter
        # is such a run took no label match above and fell
        # through to the prose branch. Read in its charged
        # form it carries no value, as the spaced form of
        # the same line does under the run only limb below:
        # the label is read on the line's head, in its
        # capital form and then in its lower case form on
        # the same exclusion the reading above takes, where
        # everything after the first colon is a run of the
        # ground classes and nothing else (Step 17 round 7,
        # charge CH-116, ATK7-2-01, the re-opened limb 4 of
        # CH-95). A run character standing before value
        # matter in the unspaced form stands outside this
        # reading, as the limb below states its bound, and
        # the line falls through as before.
        head, colon, tail = stripped.partition(":")
        if colon and tail and all(
                _in_leading_run(char) for char in tail):
            label_match = _LABEL_RE.match(head + ":")
            if label_match is None:
                ci_match = re.match(_LABEL_RE.pattern,
                                    head + ":",
                                    re.IGNORECASE)
                if ci_match is not None and \
                        ci_match.group(1).strip().lower() not in (
                            "status", "status unchanged"):
                    label_match = ci_match
    if label_match and (label_match.group(2) or "").strip() and \
            not "".join(
                char for char in label_match.group(2)
                if not _in_leading_run(char)).strip():
        # A labelled line whose only value matter is a run
        # of the ground classes carries no value in form: a
        # value carrying nothing but characters of those
        # classes stands as no value for the limb 6 reading
        # below, as its terminated twin stands parsed with a
        # Warning (Step 17 round 6, charge CH-95, ATK6-2-04).
        # A run character standing before value matter is a
        # value, not no value, and stands outside this limb.
        return False
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
    if label_match:
        # A labelled line carrying no value stands whole in
        # its own form (Step 17 round 5, charge CH-81,
        # ATK5-2-06): its terminated twin stands parsed with
        # a Warning, so the missing terminator alone does not
        # cut it. The bound is the labelled family this
        # branch reads: a Status line or variant line
        # carrying no value stands cut in its own terms
        # above, as the docstring of this rule states, and
        # that member is not reached here.
        return False
    bullet = re.match(
        r"(?:[-*+]|[0-9]+\.|[0-9]+\)|\([0-9]+\)|[0-9]+\]"
        r"|[A-Za-z]\.|[A-Za-z]\)|\([A-Za-z]\)|[A-Za-z]\]"
        r"|(?:(?=[MDCLXVImdclxvi]+\.)"
        r"M{0,3}(?:CM|CD|D?C{0,3})(?:XC|XL|L?X{0,3})"
        r"(?:IX|IV|V?I{0,3})"
        r"|(?=[MDCLXVImdclxvi]+\.)"
        r"m{0,3}(?:cm|cd|d?c{0,3})(?:xc|xl|l?x{0,3})"
        r"(?:ix|iv|v?i{0,3})"
        r"|(?=[MDCLXVImdclxvi]+\.)"
        r"(?:Mm{0,2}(?:cm|cd|d?c{0,3})(?:xc|xl|l?x{0,3})"
        r"(?:ix|iv|v?i{0,3})"
        r"|(?:Cm|Cd|Dc{0,3}|C)(?:xc|xl|l?x{0,3})"
        r"(?:ix|iv|v?i{0,3})"
        r"|(?:Xc|Xl|Xx{0,2}|Lx{1,3}|L)(?:ix|iv|v?i{0,3})"
        r"|(?:Iv|Ix|Vi{0,3}|Ii{0,2})|(?=[MDCLXVImdclxvi]+\.)[Mm]{0,3}(?:[Cc][Mm]|[Cc][Dd]|[Dd]?[Cc]{0,3})(?:[Xx][Cc]|[Xx][Ll]|[Ll]?[Xx]{0,3})(?:[Ii][Xx]|[Ii][Vv]|[Vv]?[Ii]{0,3})))\."
        r"|[Ⅰ-Ⅻⅰ-ⅻ]\."
        r"|[Ⅰ-Ⅻⅰ-ⅻ](?:\)|\])"
        r"|(?:(?=[MDCLXVImdclxvi]+[\)\]])"
        r"M{0,3}(?:CM|CD|D?C{0,3})(?:XC|XL|L?X{0,3})"
        r"(?:IX|IV|V?I{0,3})"
        r"|(?=[MDCLXVImdclxvi]+[\)\]])"
        r"m{0,3}(?:cm|cd|d?c{0,3})(?:xc|xl|l?x{0,3})"
        r"(?:ix|iv|v?i{0,3})"
        r"|(?=[MDCLXVImdclxvi]+[\)\]])"
        r"(?:Mm{0,2}(?:cm|cd|d?c{0,3})(?:xc|xl|l?x{0,3})"
        r"(?:ix|iv|v?i{0,3})"
        r"|(?:Cm|Cd|Dc{0,3}|C)(?:xc|xl|l?x{0,3})"
        r"(?:ix|iv|v?i{0,3})"
        r"|(?:Xc|Xl|Xx{0,2}|Lx{1,3}|L)(?:ix|iv|v?i{0,3})"
        r"|(?:Iv|Ix|Vi{0,3}|Ii{0,2})|(?=[MDCLXVImdclxvi]+[\)\]])[Mm]{0,3}(?:[Cc][Mm]|[Cc][Dd]|[Dd]?[Cc]{0,3})(?:[Xx][Cc]|[Xx][Ll]|[Ll]?[Xx]{0,3})(?:[Ii][Xx]|[Ii][Vv]|[Vv]?[Ii]{0,3})))(?:\)|\])"
        r"|\((?:(?=[MDCLXVImdclxvi]+\))"
        r"M{0,3}(?:CM|CD|D?C{0,3})(?:XC|XL|L?X{0,3})"
        r"(?:IX|IV|V?I{0,3})"
        r"|(?=[MDCLXVImdclxvi]+\))"
        r"m{0,3}(?:cm|cd|d?c{0,3})(?:xc|xl|l?x{0,3})"
        r"(?:ix|iv|v?i{0,3})"
        r"|(?=[MDCLXVImdclxvi]+\))"
        r"(?:Mm{0,2}(?:cm|cd|d?c{0,3})(?:xc|xl|l?x{0,3})"
        r"(?:ix|iv|v?i{0,3})"
        r"|(?:Cm|Cd|Dc{0,3}|C)(?:xc|xl|l?x{0,3})"
        r"(?:ix|iv|v?i{0,3})"
        r"|(?:Xc|Xl|Xx{0,2}|Lx{1,3}|L)(?:ix|iv|v?i{0,3})"
        r"|(?:Iv|Ix|Vi{0,3}|Ii{0,2})|(?=[MDCLXVImdclxvi]+\))[Mm]{0,3}(?:[Cc][Mm]|[Cc][Dd]|[Dd]?[Cc]{0,3})(?:[Xx][Cc]|[Xx][Ll]|[Ll]?[Xx]{0,3})(?:[Ii][Xx]|[Ii][Vv]|[Vv]?[Ii]{0,3})))\)"
        r")"
        r"\s+(.*)$", stripped)
    if bullet is not None:
        # A bullet item stands whole in item form with no
        # sentence close, but its content is read under the
        # same fragment and joining word guards the labelled
        # forms take (Step 17 fix wave 3, charge CH-34, ruling
        # (b) at record section 26): an item cut mid word, or
        # ending on a joining word, stands cut in form, and a
        # complete item stands whole, as the complete bullet
        # pin of ATK2-2-05 stands. The marker forms are the
        # dash, the star, the plus, and the numbered marker
        # (Step 17 round 4, charge CH-57, ATK4-2-03): the
        # completeness reading reaches complete items under
        # every one of them, and the cut side guards above
        # apply to each marker alike, so a cut item under a
        # new marker does not stand whole by this cure. The
        # parenthesis numbered marker stands in the set from
        # Step 17 round 5, charge CH-81, ATK5-2-03, the K9
        # bound of the digits and full stop form extended by
        # this one form as charged, under the same guards.
        # The parenthesised marker and the bracket marker
        # stand in the set from Step 17 round 6, charge
        # CH-95, ATK6-2-06, under the same guards, the cut
        # side stated for each newly reached marker.
        # The single letter forms (the letter and full stop
        # form, the letter and closing parenthesis form,
        # and the parenthesised letter form) and the roman
        # numeral and full stop form, in the standard
        # numeral forms in either case, stand in the set
        # from Step 17 round 7, charge CH-118, ATK7-2-03,
        # under the same guards, the cut side stated for
        # each newly reached marker. The roman numeral and
        # closing parenthesis form, the parenthesised roman
        # form, and the bracket form for a letter or a roman
        # numeral stand in the set from Step 17 round 8,
        # charge CH-175, ATK8-2-03, under the same guards,
        # the cut side stated for each newly reached marker.
        # The titlecase form of the roman numeral (one
        # capital letter followed by lower case letters in
        # the standard numeral order) stands in the set
        # from Step 17 round 9, charge CH-216, ATK9-2-02,
        # in every closing form the set reaches, under the
        # same guards; case mixes beyond the titlecase form
        # stand outside this limb. An item whose content
        # carries a colon is read as a labelled line on
        # that colon above and is not reached here. The
        # titlecase tens alternatives carry the Lx family
        # (Lx, Lxx, and Lxxx, the sixty to eighty nine
        # forms) from Step 17 round 10, charge CH-259,
        # ATK10-2-05, in every closing form the set
        # reaches, under the same guards. A mixed case
        # form of the standard numeral (each letter of the
        # numeral in either case) stands in the set from
        # Step 17 round 10, charge CH-260, seat 13 F-3, in
        # every closing form the set reaches, under the
        # same guards; a form that is no standard numeral
        # in any case matches no alternative. The single
        # character Unicode roman numerals (the capital
        # forms U+2160 to U+216B and the small forms
        # U+2170 to U+217B) stand in the set from Step 17
        # round 10, charge CH-263, ATK10-2-06, in the full
        # stop form and in the closing parenthesis and
        # bracket form, under the same guards.
        # The content is also tested for a cut DQ reference
        # (charge CH-81, ATK5-2-04): a reference token is not
        # alphabetic in the fragment guard form, so a cut
        # reference closing an item stood whole in silence
        # before this test.
        tokens = re.findall(r"\w+(?:['’./-]\w+)*",
                            bullet.group(1))
        if not tokens:
            return False
        return _content_carries_cut_reference(bullet.group(1)) or \
            _last_token_is_fragment(tokens) or \
            tokens[-1].lower() in _NAME_FORM_WORDS
    heading = _HEADING_RE.match(stripped)
    if heading is not None:
        # A final line complete in a structural form the tool
        # itself teaches stands whole in its own form (Step
        # 17 fix wave 3, charge CH-34): a heading closes on
        # its text, read under the same fragment and joining
        # word guards, so a heading whose text stands cut mid
        # word stands cut in form.
        tokens = re.findall(r"\w+(?:['’./-]\w+)*",
                            heading.group(2))
        if not tokens:
            return False
        if len(heading.group(1)) >= 4 and \
                _content_carries_cut_reference(heading.group(2)):
            # A cut DQ reference closing a heading final line
            # stands cut (Step 17 round 5, charge CH-81,
            # ATK5-2-04). The limb reaches the heading text of
            # the in entry headings at level 4 and below,
            # where the final line test itself reads the line:
            # an entry heading at levels 1 to 3 stands on the
            # heading recognition surface, which owns that
            # reading, and is not reached here.
            return True
        return _last_token_is_fragment(tokens) or \
            tokens[-1].lower() in _NAME_FORM_WORDS
    if re.fullmatch(r"(`{3,}|~{3,})", stripped):
        # A fence delimiter is complete as a delimiter: it
        # closes on its run and carries no prose to cut.
        return False
    # The structural branches disregard a trailing run of
    # the ground classes standing after the closing mark, as
    # the labelled branches disregard those characters at the
    # end of a labelled value (Step 17 round 6, charge CH-95,
    # ATK6-2-01): the closed form is read on the line with
    # its trailing run removed, so a line cut inside its
    # closing mark, whose mark stands incomplete on that
    # reading, falls through and stands cut.
    closed = stripped
    while closed and _in_leading_run(closed[-1]):
        closed = closed[:-1]
    if closed.startswith("<!--") and len(closed) >= 7 and \
            closed.find("-->", 4) == len(closed) - 3:
        # An HTML comment closing on its closing mark is
        # complete in its own form (Step 17 round 5, charge
        # CH-81, ATK5-2-01). A comment left unclosed falls
        # through to the prose branch below.
        return False
    if re.fullmatch(r"=+", closed):
        # A setext heading underline of equals signs is
        # complete in its own form: it closes on its run
        # (charge CH-81, ATK5-2-01).
        return False
    if re.fullmatch(r"-{3,}", closed) and \
            previous_line is not None and \
            previous_line.strip() != "":
        # A setext heading underline of dashes standing in
        # underline position, its preceding line carrying
        # matter, is complete in its own form (Step 17 round
        # 6, charge CH-95, ATK6-2-07). A dash run standing in
        # break position, after a blank line or at the head
        # of the file, stands as the thematic break forms
        # round 4 left it and is not reached here.
        return False
    if re.fullmatch(r"_{3,}", closed):
        # An underscore thematic break is complete in its
        # own form: it closes on its run of three or more
        # underscores (charge CH-95, ATK6-2-07). A shorter
        # run closes no form and falls through.
        return False
    if len(closed) > 1 and \
            closed.endswith("|") and closed.count("|") >= 2:
        # A table row closing on its final pipe is complete
        # in its own form (charge CH-81, ATK5-2-01), subject
        # to the reference completeness test of ATK5-2-04.
        # The row stands in the form carrying its leading
        # pipe and in the form carrying none, its first cell
        # standing before the first pipe in that form (Step
        # 17 round 7, charge CH-120, ATK7-2-05). A row
        # missing its final pipe falls through to the prose
        # branch below.
        return _content_carries_cut_reference(closed)
    blockquote = re.match(r">\s*(.+)$", stripped)
    if blockquote is not None:
        # A blockquote line is complete in its own form: it
        # closes on its text, read under the same fragment
        # and joining word guards and the reference
        # completeness test the bullet branch takes (charge
        # CH-81, ATK5-2-01 and ATK5-2-04).
        tokens = re.findall(r"\w+(?:['’./-]\w+)*",
                            blockquote.group(1))
        if not tokens:
            return False
        return _content_carries_cut_reference(
            blockquote.group(1)) or \
            _last_token_is_fragment(tokens) or \
            tokens[-1].lower() in _NAME_FORM_WORDS
    ref_def = re.match(r"\[\^?[^\]]+\]:\s*(.+)$", stripped)
    if ref_def is not None:
        # A link reference definition and a footnote
        # definition are complete in their own forms: each
        # closes on its value, read under the same fragment
        # and joining word guards and the reference
        # completeness test the bullet branch takes (charge
        # CH-81, ATK5-2-01 and ATK5-2-04).
        tokens = re.findall(r"\w+(?:['’./-]\w+)*",
                            ref_def.group(1))
        if not tokens:
            return False
        return _content_carries_cut_reference(ref_def.group(1)) or \
            _last_token_is_fragment(tokens) or \
            tokens[-1].lower() in _NAME_FORM_WORDS
    # The bracket group reading strips the standing quote
    # characters from the line end, and the right
    # guillemet beside them (Step 17 round 9, charge
    # CH-217, ATK9-2-03): a group standing behind a right
    # guillemet takes the same reading as a group standing
    # last. The strip carries seven further members (Step
    # 17 round 10, charge CH-261, ATK10-2-04): the single
    # guillemet, the asterisk, the underscore, the
    # backtick, the left double quotation mark, the
    # fullwidth closing parenthesis, and the closing
    # corner bracket, and it disregards a trailing run of
    # the ground classes in alternation with them (charge
    # CH-262, ATK10-2-04 case q28 and seat 13 case q26),
    # so a group standing behind any of them, or behind a
    # run and one of them, takes the same reading. No
    # ASCII closing bracket joins this strip, so a group
    # standing last keeps its own closing bracket. The
    # widened reading stands narrowed in the open: it
    # counts only where matter stands before the group
    # once the quote characters and the run are
    # disregarded, so a line carrying nothing before its
    # group but a quote and a run (the fix wave 8 K9 cut
    # side at test_prose_interleave_no_sentence_close)
    # takes no widened reading and stands as the
    # sentence test leaves it; the standing quote strip
    # reading above it stands unnarrowed, exactly as
    # CH-217 left it.
    if _final_bracket_group_start(
            stripped.rstrip("\"'”’»")) is not None:
        return False
    group_core = stripped
    while True:
        reduced = group_core
        while reduced and _in_leading_run(reduced[-1]):
            reduced = reduced[:-1]
        reduced = reduced.rstrip("\"'”’»›*`_“）」")
        if reduced == group_core:
            break
        group_core = reduced
    group_start = _final_bracket_group_start(group_core)
    if group_start is not None and \
            group_core[:group_start].strip(
                "\"'”’ \t") and \
            "".join(
                char for char in group_core[:group_start]
                if not _in_leading_run(char)).strip(
                    "\"'”’ \t"):
        return False
    core = stripped
    # The prose branch disregards a trailing run of the
    # ground classes standing after the sentence closing
    # punctuation, before its sentence close test (Step 17
    # round 6, charge CH-95, ATK6-2-02): a run character
    # standing after the punctuation hides no sentence
    # close, and a run character rescues no line that
    # closes no sentence. The run is disregarded before the
    # closing quote and bracket characters are stripped,
    # and again after them, so a run standing after a
    # closing character hides no sentence close either
    # (Step 17 round 7, charge CH-117, ATK7-2-02): the
    # strip order, closing characters first and the run
    # second, left the closing character standing last
    # where a run stood behind it. The two disregards now
    # stand read in alternation until the end of the line
    # stands stable (Step 17 round 8, charge CH-173,
    # ATK8-2-01): where a run stands between two closing
    # characters, the one strip order took the outer
    # character, stopped at the run, and left the inner
    # closing character standing last, with the sentence
    # close behind it invisible. The closing character set
    # the strip takes carries the right guillemet and the
    # asterisk beside the standing members (Step 17 round
    # 8, charge CH-174, ATK8-2-02), so a sentence closing
    # on a closing character of that widened set, the
    # closing mark of the guillemet pair or the closing
    # asterisks of a bold span among them, is read on the
    # same test. The set carries six further members (Step
    # 17 round 9, charge CH-215, ATK9-2-01): the single
    # guillemet, the underscore of an emphasis span, the
    # backtick of a code span, the left double quotation
    # mark, the fullwidth closing parenthesis, and the
    # closing corner bracket, and the sentence close test
    # carries the single character ellipsis beside the
    # three standing marks (charge CH-218, ATK9-2-04). The
    # set carries eight further members (Step 17 round
    # 10, charge CH-257, ATK10-2-01 and seat 13 F-1): the
    # left guillemet, the single left guillemet, the
    # closing white corner bracket, the closing black
    # lenticular bracket, the fullwidth closing bracket,
    # the fullwidth closing brace, the tilde of a
    # strikethrough span, and the closing angle bracket,
    # and the sentence close test carries seven further
    # marks beside the standing marks (charge CH-258,
    # ATK10-2-02 and ATK10-2-03 and seat 13 F-2): the
    # ideographic full stop, the fullwidth exclamation
    # mark, the fullwidth question mark, the fullwidth
    # full stop, the interrobang, the two dot leader, and
    # the midline horizontal ellipsis. A closing
    # character of the set, or a mark of the test,
    # rescues no line that closes no sentence.
    while True:
        reduced = core
        while reduced and _in_leading_run(reduced[-1]):
            reduced = reduced[:-1]
        reduced = reduced.rstrip("\"')]}"
                                 "”’»*›“_`)）」«‹』】］｝~⟩")
        if reduced == core:
            break
        core = reduced
    return not core.endswith((".", "?", "!", "…", "。", "！", "？", "．", "‽", "‥", "⋯"))


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

    Round 7 limbs (charges CH-117 and CH-119, record
    section 66): the value is read with a trailing run of
    the ground classes disregarded before its closing
    quote and bracket characters are stripped, and again
    after them, so a run standing after a closing
    character hides no sentence close in this branch
    either; and the Options reading drops the empty item
    standing between two adjacent part boundaries where
    that pair is the value's one join between its two
    items, as the Blocks reading drops its empty part, an
    empty item at any other boundary still failing, and
    the Oxford comma list form standing pinned as still
    cut under design question note (h).

    Round 8 limbs (charges CH-173 and CH-174, record
    section 77): the sentence close test of this branch
    also reads the value end in alternation, the closing
    characters and the trailing run disregarded in turn
    until the end stands stable, on the closing character
    set the prose branch carries as widened at CH-174, so
    a run standing between two closing characters, and a
    closing character of the widened set, hide no sentence
    close in this branch either. The reading stands as a
    probe on the sentence close test alone: the core the
    standing order reads, and every reading below that
    reads on it or on the raw value, stands unmoved.

    Round 9 limbs (charges CH-215 and CH-218, record
    section 81): the sentence close test of this branch
    carries the single character ellipsis beside the
    three standing marks, on the standing order's own
    test and on the probe alike, and the probe's closing
    character set carries the six further members the
    prose branch carries at CH-215, so a sentence closing
    behind one of them, or on the ellipsis, is read in
    this branch as in the prose branch. The probe stands
    on the sentence close test alone, as at round 8.

    Round 10 limbs (charges CH-257, CH-258, and CH-262,
    record section 83): the probe's closing character
    set carries the eight further members of charge
    CH-257 beside the standing members, and the
    sentence close tests of this branch, the standing
    order's own test and the probe alike, carry the
    seven further marks of charge CH-258 beside the
    standing marks, so a sentence closing behind a
    member of the widened set, or on one of the further
    marks, is read in this branch as in the prose
    branch. The bracket group reading takes a further
    probe on the value as written (charge CH-262): it
    disregards, in alternation, a trailing run and the
    two guillemet forms standing behind the group, and
    carries no quote character, so the p17 form (a
    group behind an interleaved run and a closing
    double quote) takes no probe reading and stands at
    its bound under ruling (f) of record section 81.
    """
    raw = value.strip()
    initial = raw
    # The value is read with a trailing run of the ground
    # classes disregarded before its closing quote and
    # bracket characters are stripped, and the core again
    # after them, on the same order the prose branch of
    # _final_line_is_cut_off takes (Step 17 round 7,
    # charge CH-117, ATK7-2-02): a run standing after a
    # closing character hid the sentence close of a
    # sentence valued label, as it hid the prose close.
    while raw and _in_leading_run(raw[-1]):
        raw = raw[:-1]
    raw = raw.rstrip("\"'”’")
    core = raw.rstrip(")]}")
    while core and _in_leading_run(core[-1]):
        core = core[:-1]
    if core.endswith((".", "?", "!", "…", "。", "！", "？", "．", "‽", "‥", "⋯")):
        return True
    # The sentence close test also reads the value end in
    # alternation (Step 17 round 8, charges CH-173 and
    # CH-174, ATK8-2-01 and ATK8-2-02): the standing order
    # strips the closing quotes from the raw value and the
    # closing brackets from the core in one pass each, so
    # a run standing between two closing characters left
    # the inner closing character standing last in the
    # core, and a closing character outside the standing
    # set, the right guillemet or the asterisk among them,
    # was never stripped at all, and the sentence close
    # behind either stood invisible in this branch as in
    # the prose branch. The probe disregards the trailing
    # run and the closing characters of the widened set in
    # turn until the end stands stable, and a close found
    # on that reading is the value's close. The probe
    # rescues no value that closes no sentence, and it
    # moves nothing else: the core and the raw value stand
    # as the standing order left them for the bracket
    # group reading and every reading below.
    probe = core
    while True:
        reduced = probe
        while reduced and _in_leading_run(reduced[-1]):
            reduced = reduced[:-1]
        reduced = reduced.rstrip("\"')]}"
                                 "”’»*›“_`)）」«‹』】］｝~⟩")
        if reduced == probe:
            break
        probe = reduced
    if probe.endswith((".", "?", "!", "…", "。", "！", "？", "．", "‽", "‥", "⋯")):
        return True
    group_start = _final_bracket_group_start(raw)
    group_text = raw
    if group_start is None:
        # The bracket group reading also takes a probe on
        # the value as written (Step 17 round 10, charge
        # CH-262, seat 13 cases q24 and q25 and seat 2 case
        # q40): the probe disregards, in alternation, a
        # trailing run of the ground classes and the two
        # guillemet forms (the right guillemet and the
        # single guillemet) standing behind the group, so a
        # group standing behind a guillemet alone, or
        # behind an interleaved run and a guillemet, takes
        # the group reading. The probe strip carries no
        # quote character: a group standing behind an
        # interleaved run and a closing double quote (seat
        # 2's p17 form) takes no probe reading on the value
        # as written, exactly as it took no reading on the
        # raw value, and stands at its bound under ruling
        # (f) of record section 81, unmoved.
        probe_group = initial
        while True:
            reduced = probe_group
            while reduced and _in_leading_run(reduced[-1]):
                reduced = reduced[:-1]
            reduced = reduced.rstrip("»›")
            if reduced == probe_group:
                break
            probe_group = reduced
        probe_start = _final_bracket_group_start(probe_group)
        if probe_start is not None:
            group_start = probe_start
            group_text = probe_group
    if group_start is not None:
        before = [token for token in re.findall(
            r"\w+(?:['’./-]\w+)*", group_text[:group_start])]
        if not before:
            return True
        return not _last_token_is_fragment(before) and \
            before[-1].lower() not in _NAME_FORM_WORDS
    label_key = label.strip().lower()
    if label_key in _SENTENCE_VALUE_LABELS:
        return False
    if label_key in ("options", "the options"):
        # Each item is tested whole, as the Blocks branch
        # tests each part whole, splitting on the comma and
        # on the joining word as the Blocks branch does, and
        # a value whose last token is a joining word is
        # refused, as the generic branch refuses it (Step 17
        # fix wave 3, charge CH-34). A prefix match on an item
        # admitted trailing matter after a full item, so a
        # list cut after a joining word stood whole.
        tokens = re.findall(r"\w+(?:['’./-]\w+)*", core)
        if tokens and tokens[-1].lower() in _NAME_FORM_WORDS:
            return False
        split_items = [item.strip() for item in
                       re.split(r",|\band\b", core)]
        # Two part boundaries standing adjacent yield an
        # empty item between them: that empty item stands
        # as the field reading of the same bytes takes it,
        # no item at all, so it is dropped here, as the
        # Blocks branch drops its empty part (Step 17
        # round 7, charge CH-119, ATK7-2-04). The drop
        # stands on the bound the charge names: the value
        # carries exactly one join, standing between its
        # two items, and that join is written as the two
        # adjacent boundaries, so the split reads three
        # parts with the empty item between them. A longer
        # list stands as the branch has always read it: the
        # Oxford comma list form among them stands pinned
        # as still cut under design question note (h), by
        # the round 2 ruling at record section 19, which no
        # charge of this wave moves. An empty item at any
        # other boundary, a trailing comma among them,
        # still fails its test below.
        items = split_items
        if len(split_items) == 3 and split_items[1] == "":
            items = [split_items[0], split_items[2]]
        return bool(items) and all(items) and all(
            re.fullmatch(r"Option\s+\S+", item) is not None or
            re.fullmatch(r"[A-Za-z0-9]", item) is not None
            for item in items)
    if label_key in ("blocks", "what it blocks"):
        # Each part is read whole, as the neighbouring
        # branches read their values: a part carries the
        # trailing inert characters of the run classes
        # disregarded, in the classes the leading limb of
        # charge CH-57 names (ATK4-2-02, a trailing zero
        # width space standing parsed as a trailing byte
        # order mark and a trailing no break space do), and
        # a lone carriage return standing between two
        # references is an ordinary character of its line
        # under the terminator rule, standing as a part
        # boundary here as the field reading of the same
        # bytes on a terminated line takes it (ATK4-2-04).
        # A part that is a cut reference on either side of
        # the carriage return still fails its full match.
        # Two lone carriage returns in succession stand as
        # the one boundary the field reading of the same
        # bytes takes (Step 17 round 5, charge CH-81,
        # ATK5-2-05): the run of carriage returns is read as
        # a single part boundary here, so the doubled form
        # takes the same value as the single form and as its
        # terminated twin. An empty part at any other
        # boundary, a trailing joining word among them,
        # still fails its test below.
        split_parts = []
        for part in re.split(
                r",|\band\b|\r", re.sub(r"\r+", "\r", core)):
            part = part.strip()
            while part and _in_leading_run(part[-1]):
                part = part[:-1]
            split_parts.append(part)
        # Two part boundaries standing adjacent yield an
        # empty part between them: that empty part stands as
        # the field reading of the same bytes takes it, no
        # part at all, so it is dropped here (Step 17 round
        # 6, charge CH-95, ATK6-2-05). An empty part at any
        # other boundary, a trailing joining word among
        # them, still fails its test below.
        parts = []
        for index, part in enumerate(split_parts):
            if part == "" and 0 < index < len(split_parts) - 1:
                continue
            parts.append(part)
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


# The joints of a guarded output row, widened at Step 17 fix
# wave 3, charges CH-50 and CH-51, to the disposition reading
# own width (record section 26, flag ruling (l)), and widened
# again at Step 17 fix wave 4, charge CH-68 (record section
# 38, ruling (d)): guard recognition is a matching matter,
# recognising whatever the disposition reading denotes at the
# disposition reading own width, on the count, joint, heading,
# and tally surfaces alike. The disposition forms fire on a
# state word wherever a word boundary stands before it and a
# colon followed by whitespace stands after it, so the words
# of a row may be joined by any run of non word characters,
# sentence punctuation included: a period, colon, semicolon,
# or question mark at a joint leaves the state word and its
# colon standing as a new sentence or clause, and the reading
# fires across exactly those characters. The run covers every
# whitespace character the reading takes, the zero width and
# format characters that leave the boundary standing, and
# decoration standing between the words of a row (emphasis,
# backticks, and link brackets around one word of the row). A
# word character at a joint, an underscore included, leaves
# no boundary for either reading, and stands in no joint.
_GUARD_JOINT = r"[^\w]+"
_GUARD_JOINT_OPT = r"[^\w]*"
# The guard state forms. At CH-88 (record section 52,
# ruling (c)) the multiword states take the heading
# pattern joint width, any run of non word characters
# standing between their words, where the CH-68 form read
# them at single literal spaces: a tally phrasing respaced
# at its internal joints is the same phrasing the heading
# limb of this programme already reads, and the
# disposition head forms fire on its first word alone.
_GUARD_STATE = (
    r"(?:Settled[^\w]+in[^\w]+part|Closed[^\w]+as[^\w]+"
    r"decided|Ruled|Settled|Closed|Open|Banked|Parked|"
    r"Presented)")

# A count at the disposition reading own width (CH-68): the
# reading needs no count at all and fires on the state word
# and its colon in every count form, so the guard count is a
# count phrase, one or more count tokens joined by a space, a
# no break space, or a hyphen, with an approximator word
# standing before it where one stands. A count token is a
# number word (the units, the tens, and the scale words
# hundred, thousand, million, and billion, and the word no
# standing as a count), a Roman numeral, or a run of numeric
# characters: a Unicode decimal digit in any script, or a
# character of another numeric class (superscript and
# subscript digits, vulgar fractions, and the numeric forms
# of the enclosed and Roman ranges). The phrase stops at the
# first token that is no count token, the word entries
# included, so a span ends at its count and a genuine ruling
# standing after the row on the same line still counts. This
# is a matching width only: no data reading in the product
# reads counts through this pattern, and data readings
# elsewhere keep their ASCII digit ground (FLAG 11).
_GUARD_COUNT_TOKEN = (
    r"(?:(?i:zero|one|two|three|four|five|six|seven|eight|"
    r"nine|ten|eleven|twelve|thirteen|fourteen|fifteen|"
    r"sixteen|seventeen|eighteen|nineteen|twenty|thirty|"
    r"forty|fifty|sixty|seventy|eighty|ninety|hundred|"
    r"thousand|million|billion|no)|(?i:[ivxlcdm]+)|"
    r"(?:\d|[\u00b2\u00b3\u00b9\u00bc-\u00be\u2070-\u2079"
    r"\u2080-\u2089\u2160-\u2189\u2460-\u2473])+"
    r"(?:[.,]\d+)*)(?!\w)")
_GUARD_COUNT = (
    r"(?:(?:(?i:about|around|approximately|nearly|roughly|"
    r"almost)[ \t ]+)?" + _GUARD_COUNT_TOKEN +
    r"(?:(?:[ \t ]+|-)" + _GUARD_COUNT_TOKEN + r")*)")

# The count at the reading own width (CH-88, record
# section 52, ruling (c)): the K3 enumerated count
# vocabulary bound stands superseded at the count limb in
# the open, because the disposition reading fires on the
# state word and its colon with no count, a nonsense
# count, and a count in any script standing after the
# colon alike. A count row of the tool own output carries
# its count between the colon and the row noun entries,
# so the wide count reading runs from the colon to that
# noun: one or more count region tokens, a token being a
# run of characters that are neither whitespace nor a
# clause breaking mark, joined by spaces, and the noun
# entries itself. A token carries no colon, semicolon,
# exclamation mark, or question mark, and the joints
# carry no such mark either, so the region cannot cross
# a clause boundary into a genuine ruling standing after
# the row: the span ends at the first entries word, and
# matter after the row stands outside it, as the CH-68
# phrase bound stood. Where no entries noun stands after
# the colon, the CH-68 count phrase at _GUARD_COUNT
# stands as the count reading, whole on its listed forms.
# At CH-107 (record section 58, ruling (b)) the count
# width stands restated in its own terms: the region
# joints take any whitespace character and the zero
# width characters, a clause breaking mark standing
# between the count and its noun is region matter, the
# row noun stands as entries, entry, items, questions,
# or cases, a trailing underscore on the noun standing
# as row matter, and a single count token standing
# alone takes its span where no noun form stands. The
# K3 stated bounds stand superseded at this limb in
# the open by that ruling. At CH-122 (record section
# 66, ruling (c) whole) the region width stands
# restated at one further point: a single clause
# breaking mark standing alone as the whole count
# region takes its span, where a region carrying no
# token and no noun took no span before, so the row
# Canonical Ruled: ; stands guarded as its token
# carrying fellows do. A run of marks standing alone,
# and a mark standing with any other matter that is
# neither a token sequence ending at the noun nor the
# CH-68 phrase, stands outside this restatement.
_GUARD_COUNT_WIDE = (
    r"(?:(?i:entries|entry|items|questions|cases)"
    r"_*(?!\w)|[^\s;:!?\u200b\u200c\u200d\ufeff]+"
    r"(?:(?:\s|[\u200b\u200c\u200d\ufeff])+"
    r"[^\s;:!?\u200b\u200c\u200d\ufeff]+)*?"
    r"(?:(?:\s|[\u200b\u200c\u200d\ufeff])+|"
    r"(?:\s|[\u200b\u200c\u200d\ufeff])*[;:!?]+"
    r"(?:\s|[\u200b\u200c\u200d\ufeff])*)"
    r"(?i:entries|entry|items|questions|cases)"
    r"_*(?!\w)|[^\s;:!?\u200b\u200c\u200d\ufeff]+|"
    r"[;:!?])")

# A tally count at the same width (CH-88): the CH-68
# count phrase, or any single count region token standing
# alone, the word dozen in that form. A tally count
# stands between its delimiters (the joint and total word
# of a crosswalk row, the pipes and occurrence word of an
# appendix row), so one token past the phrase vocabulary
# is the whole of its width, and no span lengthens past
# its delimiter into ruling matter. At CH-107 the tally
# count width stands restated in its own terms: the
# CH-68 count phrase, or one or more count region
# tokens joined by whitespace, so a tally count spelled
# in several words stands at the reading width between
# its delimiters, and no span lengthens past its
# delimiter into ruling matter on that ground either.
# At CH-122 (record section 66, ruling (c) whole) the
# token joints of the token sequence form stand
# restated at one further point: one semicolon
# standing between two count tokens, with whitespace
# or none around it, stands as a joint of the
# sequence, as the same mark already stands admitted
# at the tally joint before the total word. The mark
# stands as the semicolon alone: a colon at this
# joint would let a count cross into a decider form
# standing after it, and the other clause marks end
# the clause the count stands in, so they stand
# outside this restatement. The sequence still ends
# at its delimiters, which the row patterns require
# after it, so no span lengthens past a delimiter
# into ruling matter on this ground either.
_GUARD_COUNT_TALLY = (
    r"(?:" + _GUARD_COUNT + r"|[^\s;:!?,|]+"
    r"(?:(?:(?:\s|[\u200b\u200c\u200d\ufeff])+|"
    r"(?:\s|[\u200b\u200c\u200d\ufeff])*;"
    r"(?:\s|[\u200b\u200c\u200d\ufeff])*)"
    r"[^\s;:!?,|]+)*)")

# The crosswalk total word at its tally width (CH-88):
# the word total in either case, its plural, and its
# prefixed subtotal form, where the CH-68 pattern read
# the exact word total alone. At CH-107 the total word
# width stands restated in its own terms: the word
# total in either case, its plural, its prefixed
# subtotal form, the two word form grand total, and
# the word sum. At CH-124 (record section 66, ruling
# (c) whole) the total word width stands restated at
# its prefixed and aggregate points: one word token
# standing before the total word at a non word joint
# stands as its prefix, the grand form standing inside
# that restatement as before, and the word in standing
# at that point opens the in form of the tail and is
# no prefix; the two word form grand sum stands
# beside the word sum; and the word aggregate stands
# as a total word, in the joint form (Ruled 1,
# aggregate 1) and in the in form (Ruled 1 in
# aggregate) alike. Two words standing before the
# total word stand outside this restatement. At
# CH-161 (record section 77, ruling (g)) the total
# word width stands restated at its prefixed and
# plural points: up to two word tokens other than
# the word in standing before the total word at a
# non word joint stand as its prefix, the grand form
# standing inside that restatement as before; a
# prefix word standing before the word sum on the
# same terms stands as its prefix beside the two
# word form grand sum; and the word aggregate
# stands as a total word in its plural form
# aggregates beside its singular, in the joint form
# and in the in form alike, with a prefix word
# standing before it on the same terms. Three words
# standing before the total word stand outside this
# restatement. At CH-194 (record section 81, ruling
# (a)) the prefix width stands restated at the charged
# limb: up to three word tokens other than the word in
# standing before the total word at a non word joint
# stand as its prefix, on the same terms at the grand
# total form, at the word sum, and at the word
# aggregate in its singular and plural forms. Four
# words standing before the total word stand outside
# this restatement. At CH-196 (record section 81,
# ruling (a)) the word sum stands as a total word in
# its plural form sums beside its singular, in the
# plain form and in the grand form alike, as the word
# aggregate already stands in both its forms. At
# CH-235 (record section 83, ruling (a)) the prefix
# width stands restated at the charged limb: up to
# four word tokens other than the word in standing
# before the total word at a non word joint stand as
# its prefix, on the same terms at the grand total
# form, at the word sum, and at the word aggregate in
# its singular and plural forms. Five words standing
# before the total word stand outside this
# restatement. At the grand total form the same four
# word terms stand before the word grand itself, as
# seat 10 case g10-prefix-four-grand charges, so five
# word tokens standing before the total word at that
# form stand inside this restatement and six stand
# outside it. At CH-237 (record section 83, ruling
# (a)) the grand sums form with three words standing
# before the word grand stands cured at the same limb
# in the open: those three words and the word grand
# stand as four word tokens before the word sums, so
# the CH-235 restatement reads that form at the word
# sums, and the grand alternative itself carries no
# prefix terms of its own, as before. At CH-238
# (record section 83, ruling (a)) the word summation
# stands as a total word beside the words total, sum,
# and aggregate. No other form of the word summation
# stands admitted by this restatement.
_GUARD_TOTAL_WORD = (
    r"(?:(?:(?!(?i:in)(?!\w))[^\s;:!?,|]+[^\w]+){0,4}"
    r"(?i:(?:sub)?totals?|summation|sums?|aggregates?)|"
    r"(?:(?!(?i:in)(?!\w))[^\s;:!?,|]+[^\w]+){0,4}"
    r"(?i:grand)[^\w]+(?i:totals?)|"
    r"(?i:grand)[^\w]+(?i:sums?))")

# The count row pattern. At CH-122 (record section
# 66, ruling (c) whole) the joint standing after the
# colon takes no clause breaking mark: a mark standing
# after the colon stands in the count region, where
# _GUARD_COUNT_WIDE reads it, and no span crosses it
# into a word standing after it, so a genuine ruling
# standing after a lone mark region on the same line
# still counts. Every other joint of the row stands
# as before.
_COUNT_ROW_RE = re.compile(
    r"(?i:canonical)" + _GUARD_JOINT +
    r"(?:(?i:state)" + _GUARD_JOINT_OPT +
    r")?" + _GUARD_STATE + _GUARD_JOINT_OPT + r":" +
    r"[^\w;:!?]*" + r"(?:" + _GUARD_COUNT_WIDE + r"|" +
    _GUARD_COUNT + r")")

# The crosswalk tally row the tool prints for one head phrasing:
# the phrasing, a colon, the canonical state, a count, and the
# total. Guarded at CH-51 on the same terms as the count rows:
# the row states file level tallies and names no decider,
# ruling text, or landing, so a phrasing carrying ruling text
# after its colon, which is no tally form, takes no span.
# At CH-88 the crosswalk tail stands at the programme
# width at its three literal points: the first colon
# takes any joint or none standing before it, as the
# count row colon does; the total word takes its tally
# width at _GUARD_TOTAL_WORD; and the total phrase
# stands in either of its stated forms, the count before
# the total word, or the words in total standing after
# the count with no second count. The tally counts take
# _GUARD_COUNT_TALLY, and a final count takes the row
# noun entries standing after it where it stands, so the
# span and the labelled branch wholly row test read the
# row at one width, one step past the CH-68 trailing
# punctuation form: a trailing word that is the row noun
# is row matter, and any other matter past the row takes
# its labelled element as before. At CH-107 the tail
# width stands restated in its own terms: a single word
# token standing after the final count at a whitespace
# joint is row matter, the final noun items in that
# form, and any further matter past that token takes
# its labelled element as before, so the span and the
# wholly row test still read the row at one width. At
# CH-121 (record section 66, ruling (c) whole) the tail
# width stands restated at its trailing matter points:
# the first trailing form stands as at CH-107, or as
# the row noun (entries, entry, items, questions, or
# cases, a trailing underscore standing as row matter)
# standing at a joint run of whitespace, the zero width
# characters, a comma, a period, or a hyphen; and in
# either form one further word token standing after it
# at a whitespace joint is row matter. The confinement
# edge of the limb stands as the noun form bounds it:
# the joint run takes no trailing token where the word
# after the joint is no row noun, so a genuine ruling
# standing after the row at a sentence joint stands
# outside the span exactly as before, and any matter
# past the second token takes its labelled element as
# before. At CH-159 (record section 77, ruling (g))
# the tail width stands restated at its trailing
# matter points: the joint run of the noun form takes
# a semicolon, a colon, or a slash beside the
# whitespace, zero width, comma, period, and hyphen
# joints; a second word token standing after the
# first at a comma joint is row matter where that
# token closes the line; a first word token that is
# no row noun standing at a comma joint is row matter
# on the same line closing terms, standing as its own
# tail form with no token after it; and in the forms
# above one further, third, word token standing after
# the second at a whitespace joint is row matter,
# where the token before its joint does not end at a
# period, so a sentence joint standing after the
# second token ends the span at that token and the
# word standing after the joint is no row matter. The
# confinement edges of the limb stand as the forms
# bound them: the joint run still takes no trailing
# token where the word after the joint is no row noun
# outside the noun form itself, the comma joint forms
# take no token that does not close the line, so a
# genuine ruling standing after the row at a sentence
# joint or at a comma joint stands outside the span
# exactly as before, and any matter past the third
# token takes its labelled element as before. At
# CH-195 (record section 81, ruling (a)) the tail
# width stands restated at its trailing matter
# points: the joint run of the noun form takes an
# exclamation mark, a question mark, a pipe, or an
# equals sign beside the joints above; a second word
# token standing after the first at a semicolon or
# colon joint is row matter where that token closes
# the line; a third word token standing after the
# second at a comma joint is row matter where that
# token closes the line; a comma joint token that
# does not close the line is row matter at the first
# token place and at the second token place alike
# where one further word token stands after it at a
# whitespace joint and closes the line; a first word
# token that is no row noun standing at a semicolon
# joint is row matter where it closes the line; a
# third word token standing after a second token
# that ends at a period is row matter where that
# token closes the line, on its non ruling form
# only, a genuine ruling standing after a period
# ending second token not closing the line on its
# first word and so standing outside the span as
# before; and in the whitespace forms above one
# further, fourth, word token standing after the
# third at a whitespace joint is row matter, where
# the token before its joint does not end at a
# period. The confinement edges stand as the forms
# bound them: the semicolon, colon, and comma joint
# forms beyond the noun form take no token that does
# not close the line or stand followed by its one
# closing whitespace token, and any matter past the
# fourth token takes its labelled element as before.
# At CH-236 (record section 83, ruling (a)) the tail
# width stands restated at its trailing matter
# points: in the whitespace forms above one further,
# fifth, word token standing after the fourth at a
# whitespace joint is row matter, where the token
# before its joint does not end at a period; the
# joint run of the noun form takes an at sign, a hash
# sign, a tilde, a plus sign, a percent sign, a caret,
# a dollar sign, an asterisk, a backslash, an opening
# parenthesis, or a double quote beside the joints
# above; a second word token standing after the first
# at a pipe, exclamation, or question joint is row
# matter where that token closes the line; a second
# word token standing after the first at a semicolon
# or colon joint is row matter where one further word
# token stands after it at a whitespace joint and
# closes the line; a third word token standing after
# the second at a semicolon, colon, or pipe joint is
# row matter where that token closes the line; a
# third word token standing after a period ending
# second token is row matter where one further word
# token stands after it at a whitespace joint and
# closes the line, on the same line closing terms as
# the CH-195 after period form; a fourth word token
# standing after the third at a comma joint is row
# matter where that token closes the line, and a
# fourth word token standing after a period ending
# third token is row matter where that token closes
# the line; a first word token that is no row noun
# standing at a colon, pipe, exclamation, or question
# joint is row matter where it closes the line,
# beside the semicolon form above; and a comma joint
# token is row matter where two further word tokens
# stand after it at whitespace joints and the last
# closes the line, at the first token place and at
# the second token place alike. The confinement
# edges stand as the forms bound them: the joint run
# still takes no trailing token where the word after
# the joint is no row noun outside the noun form
# itself, the joint forms beyond the noun form take
# no token that does not close the line or stand
# followed by its closing whitespace tokens, and any
# matter past the fifth token takes its labelled
# element as before.
_CROSSWALK_ROW_RE = re.compile(
    _GUARD_STATE + _GUARD_JOINT_OPT + r":" + _GUARD_JOINT +
    _GUARD_STATE + _GUARD_JOINT + _GUARD_COUNT_TALLY +
    r"(?:" + _GUARD_JOINT + _GUARD_TOTAL_WORD +
    _GUARD_JOINT + _GUARD_COUNT_TALLY +
    r"(?:(?:(?:\s|[\u200b\u200c\u200d\ufeff])+"
    r"[^\s;:!?,|]+|"
    r"(?:(?:\s|[\u200b\u200c\u200d\ufeff])|[,.\-;:/!?=|@#~+%^$*\\(\x22])+"
    r"(?i:entries|entry|items|questions|cases)"
    r"_*(?!\w))"
    r"(?:(?:\s|[\u200b\u200c\u200d\ufeff])+"
    r"[^\s;:!?,|]+|"
    r"(?:\s|[\u200b\u200c\u200d\ufeff])*[,]+"
    r"(?:\s|[\u200b\u200c\u200d\ufeff])*"
    r"[^\s;:!?,|]+"
    r"(?:\s|[\u200b\u200c\u200d\ufeff])+"
    r"[^\s;:!?,|]+"
    r"(?:(?:\s|[\u200b\u200c\u200d\ufeff])+"
    r"[^\s;:!?,|]+)?(?=[ \t.,:;!?]*$)|"
    r"(?:\s|[\u200b\u200c\u200d\ufeff])*[,]+"
    r"(?:\s|[\u200b\u200c\u200d\ufeff])*"
    r"[^\s;:!?,|]+(?=[ \t.,:;!?]*$)|"
    r"(?:\s|[\u200b\u200c\u200d\ufeff])*[;:]+"
    r"(?:\s|[\u200b\u200c\u200d\ufeff])*"
    r"[^\s;:!?,|]+(?=[ \t.,:;!?]*$)|"
    r"(?:\s|[\u200b\u200c\u200d\ufeff])*[;:]+"
    r"(?:\s|[\u200b\u200c\u200d\ufeff])*"
    r"[^\s;:!?,|]+"
    r"(?:\s|[\u200b\u200c\u200d\ufeff])+"
    r"[^\s;:!?,|]+(?=[ \t.,:;!?]*$)|"
    r"(?:\s|[\u200b\u200c\u200d\ufeff])*[!?|]+"
    r"(?:\s|[\u200b\u200c\u200d\ufeff])*"
    r"[^\s;:!?,|]+(?=[ \t.,:;!?]*$))?"
    r"(?:(?<!\.)(?:\s|[\u200b\u200c\u200d\ufeff])+"
    r"[^\s;:!?,|]+|"
    r"(?:\s|[\u200b\u200c\u200d\ufeff])*[,]+"
    r"(?:\s|[\u200b\u200c\u200d\ufeff])*"
    r"[^\s;:!?,|]+(?=[ \t.,:;!?]*$)|"
    r"(?:\s|[\u200b\u200c\u200d\ufeff])+"
    r"[^\s;:!?,|]+(?=[ \t.,:;!?]*$)|"
    r"(?:\s|[\u200b\u200c\u200d\ufeff])*[;:|]+"
    r"(?:\s|[\u200b\u200c\u200d\ufeff])*"
    r"[^\s;:!?,|]+(?=[ \t.,:;!?]*$)|"
    r"(?:\s|[\u200b\u200c\u200d\ufeff])+"
    r"[^\s;:!?,|]+"
    r"(?:\s|[\u200b\u200c\u200d\ufeff])+"
    r"[^\s;:!?,|]+(?=[ \t.,:;!?]*$))?"
    r"(?:(?<!\.)(?:\s|[\u200b\u200c\u200d\ufeff])+"
    r"[^\s;:!?,|]+|"
    r"(?:\s|[\u200b\u200c\u200d\ufeff])*[,]+"
    r"(?:\s|[\u200b\u200c\u200d\ufeff])*"
    r"[^\s;:!?,|]+(?=[ \t.,:;!?]*$)|"
    r"(?:\s|[\u200b\u200c\u200d\ufeff])+"
    r"[^\s;:!?,|]+(?=[ \t.,:;!?]*$))?"
    r"(?:(?<!\.)(?:\s|[\u200b\u200c\u200d\ufeff])+"
    r"[^\s;:!?,|]+)?|"
    r"(?:(?:\s|[\u200b\u200c\u200d\ufeff])*[,]+"
    r"(?:\s|[\u200b\u200c\u200d\ufeff])*"
    r"[^\s;:!?,|]+"
    r"(?:(?:\s|[\u200b\u200c\u200d\ufeff])+"
    r"[^\s;:!?,|]+"
    r"(?:(?:\s|[\u200b\u200c\u200d\ufeff])+"
    r"[^\s;:!?,|]+)?)?(?=[ \t.,:;!?]*$)|"
    r"(?:\s|[\u200b\u200c\u200d\ufeff])*[;:|!?]+"
    r"(?:\s|[\u200b\u200c\u200d\ufeff])*"
    r"[^\s;:!?,|]+(?=[ \t.,:;!?]*$)))?|" +
    _GUARD_JOINT + r"(?i:in)" + _GUARD_JOINT +
    _GUARD_TOTAL_WORD + r")")

# The verbatim appendix tally row the tool prints for one
# phrasing: the phrasing, its occurrence kind, and its
# occurrence count, with an entries list where members stand.
# Guarded at CH-51 on the same terms: a phrasing carrying a
# decider form or ruling text before the first pipe is no tally
# form and takes no span, so quoted ruling rows still denote.
# At CH-88 the appendix tally count takes
# _GUARD_COUNT_TALLY, and the occurrence word stands at
# the tally width as any single word token standing in
# the occurrence place (the printed occurrence, and the
# ordinary words time and hit a tally takes when it is
# copied through prose): the row shape, its phrasing,
# kind, count, and entries list, is the guard ground,
# not the one noun the printer puts in that place. At
# CH-107 the appendix kind width stands restated in
# its own terms, at the charged limb only: the kind
# slot stands as one to three word tokens joined by
# whitespace between its pipes, the word joined form
# line_start standing as one such token, a kind with a
# leading word standing as three, and a kind word
# outside the three printed kinds standing as one. At
# CH-123 (record section 66, ruling (c) whole) the
# kind width stands restated at the charged limb: the
# kind slot stands as one to five word tokens joined
# by whitespace between its pipes. A kind spelled in
# more tokens than five stands outside this
# restatement. At CH-160 (record section 77, ruling
# (g)) the kind width stands restated at the charged
# limb: the kind slot stands as one to six word
# tokens joined by whitespace between its pipes. A
# kind spelled in more tokens than six stands
# outside this restatement. At CH-193 (record
# section 81, ruling (a)) the kind width stands
# restated at the charged limb: the kind slot stands
# as one to seven word tokens joined by whitespace
# between its pipes. A kind spelled in more tokens
# than seven stands outside this restatement.
# At CH-234 (record section 83, ruling (a)) the kind
# width stands restated at the charged limb: the
# kind slot stands as one to eight word tokens
# joined by whitespace between its pipes. A kind
# spelled in more tokens than eight stands outside
# this restatement.
_APPENDIX_ROW_RE = re.compile(
    _GUARD_STATE + _GUARD_JOINT_OPT +
    r"\|" + _GUARD_JOINT_OPT +
    r"(?:[^\s;:!?,|]+"
    r"(?:(?:\s|[\u200b\u200c\u200d\ufeff])+"
    r"[^\s;:!?,|]+){0,7})" + _GUARD_JOINT_OPT +
    r"\|" + _GUARD_JOINT_OPT + _GUARD_COUNT_TALLY +
    _GUARD_JOINT_OPT + r"[^\s;:!?,|]+")

_GROUP_HEADING_RE = re.compile(
    r"((?:Settled[^\w]+in[^\w]+part|Closed[^\w]+as[^\w]+"
    r"decided|Ruled|Settled|Closed|Parked|Presented|Open|"
    r"Banked|Conditional|Ambiguous)[^\w]+group)",
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

    The output forms stand guarded, recognised by their meaning
    wherever they stand in the line (Step 17 fix wave 2, charge
    CH-15, flag ruling (g) at record section 19; widened at Step
    17 fix wave 3, charges CH-50 and CH-51, flag ruling (l) at
    record section 26, to whatever the disposition reading
    denotes, at that reading own width, neither wider nor
    narrower):

    - A count row of the tool own output, in either spelling:
      the reconciliation spelling, Canonical, a state word, a
      colon, and a count; and the census spelling, Canonical
      state, a colon, a state word, a colon, and a count. The
      row states a file level count and names no decider,
      ruling text, or landing for the entry it stands in. Its
      joints take the widened joint form at _GUARD_JOINT, and
      its count takes the digit forms and word forms the
      disposition reading accepts, since that reading needs no
      count at all and fires on the state word and its colon in
      every count form. At CH-68 the joints take sentence
      punctuation as well, the census label takes any joint
      after the word state in place of its colon alone, and
      the count takes the count phrase at _GUARD_COUNT.
    - A crosswalk tally row and a verbatim appendix tally row,
      in the forms the tool prints them: each states a state
      word and counts only, and names no decider, ruling text,
      or landing for the entry it is reused inside. At CH-68
      their tails take the count row width: the joints are any
      non word run (a doubled space, a tab, or a no break
      space before the word total, the comma standing or
      missing), the word total stands in either case, the
      appendix occurrence kind takes any joint inside it and
      either case, and every tally count takes the count
      phrase width at _GUARD_COUNT, Unicode decimal digits
      and word counts included. At CH-88 (record section
      52, ruling (c)) the count limb stands at the reading
      own width under _GUARD_COUNT_WIDE, the enumerated
      vocabulary bound superseded in the open at that
      limb; the tally state forms take the heading joint
      width; the tally counts take _GUARD_COUNT_TALLY; the
      crosswalk colon, total word, and total phrase take
      their tally widths; and the appendix occurrence word
      stands as any word token in its place.
    - A rendered group heading line standing as its own
      sentence: a state word and the word group, with only
      quoting or emphasis decoration around it, any whitespace
      standing between its words, and any trailing sentence
      punctuation standing after it, a period included. At
      CH-68 the heading joint is any non word run, a zero
      width space included, and a heading carrying trailing
      matter past the word group takes a span ending at the
      word group, so the trailing matter itself stands
      outside the span.

    The guard is confined to the row or heading itself: a
    disposition form standing outside these spans, later on
    the same line included, still counts. No span in this
    programme covers a line whose phrasing carries ruling text
    or a decider form, so quoted genuine ruling lines denote
    for their host entry exactly as they stood.
    """
    spans = []
    for match in _COUNT_ROW_RE.finditer(text):
        spans.append((match.start(), match.end()))
    for match in _CROSSWALK_ROW_RE.finditer(text):
        spans.append((match.start(), match.end()))
    for match in _APPENDIX_ROW_RE.finditer(text):
        spans.append((match.start(), match.end()))
    for span_start, span_end in _sentence_spans(text):
        core = text[span_start:span_end].strip(
            " \t*|>#- ​﻿")
        if _GROUP_HEADING_RE.fullmatch(core.rstrip(".,:;!?")):
            spans.append((span_start, span_end))
            continue
        # A heading carrying trailing matter past the word
        # group (CH-68, F-20-4-3): the head disposition form
        # still fires on the state word at the head of the
        # sentence, so the heading itself takes a span, and
        # the span ends at the word group. Trailing matter
        # stands outside the span, segment aware, so a genuine
        # ruling standing in it or after it still counts.
        lead = re.match(
            r"[ \t\*\|>#\-\u00a0\u200b\ufeff]*",
            text[span_start:span_end]).end()
        heading = _GROUP_HEADING_RE.match(
            text, span_start + lead)
        if heading is not None and heading.start() < span_end:
            spans.append((heading.start(), heading.end()))
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


def _is_charged_label_damage(label):
    """Whether a label carries one charged non letter
    character of round 6 charge CH-111: a digit, an
    underscore, a hyphen, or a braille dot pattern character
    substituted for one letter of the Status word, or one
    such character standing inside the word beside its whole
    letters, or one digit standing after the complete word.
    Two such characters, a letter in any of those positions,
    and any character other than a digit after the complete
    word stand outside the charge."""
    def charged(char):
        return (char.isascii() and char.isdigit()) or \
            char in "_-" or "\u2800" <= char <= "\u28ff"
    if len(label) == 6:
        differing = [index for index in range(6)
                     if label[index] != "Status"[index]]
        return len(differing) == 1 and \
            charged(label[differing[0]])
    if len(label) == 7:
        for index in range(7):
            if label[:index] + label[index + 1:] == "Status":
                char = label[index]
                if index == 6:
                    return char.isascii() and char.isdigit()
                return charged(char)
        return False
    return False


def _is_label_interior_damage(label):
    """Whether a label carries one character of round 7
    charge CH-128, at the reading where the CH-111 bound
    and the letter readings meet: one punctuation, symbol,
    or number character, or one letter of a script other
    than the ASCII letters, substituted for one letter of
    the Status word or standing inside the word beside its
    whole letters, or one punctuation, symbol, or number
    character standing after the complete word. The digit
    and braille members of the inside classes stand
    charged already at _is_charged_label_damage and take
    the same reading here. Two such characters, an ASCII
    letter in any of those positions, a letter after the
    complete word, and a hyphen or an underscore after the
    complete word stand outside the charge: the hyphen and
    underscore suffix forms are the CH-111 bound guards,
    pinned silent."""
    def interior(char):
        category = unicodedata.category(char)
        if category.startswith(("P", "S", "N")):
            return True
        return category.startswith("L") and \
            not char.isascii()
    def suffix(char):
        if char in "_-":
            return False
        return unicodedata.category(char).startswith(
            ("P", "S", "N"))
    if len(label) == 6:
        differing = [index for index in range(6)
                     if label[index] != "Status"[index]]
        return len(differing) == 1 and \
            interior(label[differing[0]])
    if len(label) == 7:
        for index in range(7):
            if label[:index] + label[index + 1:] == "Status":
                char = label[index]
                if index == 6:
                    return suffix(char)
                return interior(char)
        return False
    return False


def _is_run_ground_label_substitution(label):
    """Whether a label carries one character of the run
    ground of record section 52 ruling (a), read at
    _in_leading_run, substituted for one letter of the
    Status word (round 8 charge CH-185, seat 17 finding
    S17-ATK8-17-01): the label stands six characters long,
    exactly one position differs from the Status word,
    that position is an interior position of the word,
    the second letter position through the last, and the
    character standing there stands in the run ground.
    The cleaning at _is_near_marker rescues a character
    of that ground only where the whole letters of the
    word still stand, so in place of one letter the
    cleaned label is the five letters that remain and no
    reading named the form. Two such characters in one
    label stand outside the charge, as two characters
    stand outside the CH-128 charge, and the first letter
    position stands outside it: a character of the ground
    standing there is read by the leading run reading and
    the one edit reading above, as the attack paper
    records that position in the signal direction."""
    if len(label) != 6:
        return False
    differing = [index for index in range(6)
                 if label[index] != "Status"[index]]
    return len(differing) == 1 and differing[0] != 0 and \
        _in_leading_run(label[differing[0]])


def _is_case_joint_label_damage(label):
    """Whether a label carries one interior damage of a
    cured class together with a letter case damage (round
    8 charge CH-186, seat 17 finding S17-ATK8-17-02): the
    label stands six characters long, its letters read
    without case stand one position from the Status word,
    the character at that one position stands in the
    interior classes of _is_label_interior_damage (a
    punctuation, symbol, or number character, or a letter
    of a script other than the ASCII letters, the CH-111
    charged set standing inside those classes), and the
    label with that character read as the Status letter
    stands in a letter case other than the capitalised
    form. Each damage alone takes the near marker report:
    a label in another case through the case reading, and
    an interior character in the capitalised label
    through the CH-111 and CH-128 limbs. Standing together
    they took nothing, because the case and one edit
    readings read a run of ASCII letters only and the
    interior helpers take their charge only where exactly
    one position differs from the capitalised word. A
    label whose remaining letters stand in the capitalised
    form is the CH-128 form itself and stands outside
    this joint, as does a label standing one position
    from the word in its letters alone."""
    if len(label) != 6:
        return False
    differing = [index for index in range(6)
                 if label[index].lower() != "status"[index]]
    if len(differing) != 1:
        return False
    index = differing[0]
    char = label[index]
    category = unicodedata.category(char)
    if not (category.startswith(("P", "S", "N")) or
            (category.startswith("L") and
             not char.isascii())):
        return False
    restored = label[:index] + "Status"[index] + \
        label[index + 1:]
    return restored != "Status"


def _is_run_ground_case_joint_label_damage(label):
    """Whether a label carries one character of the run
    ground in place of one label letter together with a
    letter case damage (round 9 charge CH-219, seat 17
    finding S17-ATK9-17-01): the label stands six
    characters long, its letters read without case stand
    one position from the Status word, that position is
    an interior position of the word, the second letter
    position through the last, the character standing
    there stands in the run ground of record section 52
    ruling (a), read at _in_leading_run, and the label
    with that character read as the Status letter stands
    in a letter case other than the capitalised form.
    Each damage alone takes the near marker report: a
    run ground character in place of a letter through
    CH-185, where the remaining letters stand in the
    capitalised form, and a label in another case
    through the case reading. Standing together they
    took nothing, because the case reading reads a run
    of ASCII letters only, the CH-185 limb takes its
    charge only where exactly one position differs from
    the capitalised word, and the CH-186 joint takes its
    charge only where the character at its one position
    stands in the CH-128 interior classes, a ground the
    run ground character does not stand in. Record
    section 81 ruling (e) rules the joint a distinct
    construction family outside the bounds as pinned.
    The bounds stand stated here: two such characters in
    one label stand outside this joint, as two stand
    outside CH-185; a joint form at any other label
    length stands outside it; and the first letter
    position stands outside it, that position standing
    in the signal direction already through the leading
    run reading and the one edit reading, as the CH-185
    bound states it."""
    if len(label) != 6:
        return False
    differing = [index for index in range(6)
                 if label[index].lower() != "status"[index]]
    if len(differing) != 1:
        return False
    index = differing[0]
    if index == 0:
        return False
    if not _in_leading_run(label[index]):
        return False
    restored = label[:index] + "Status"[index] + \
        label[index + 1:]
    return restored != "Status"


def _is_run_ground_insertion_case_joint_label_damage(label):
    """Whether a label carries one character of the run
    ground inserted beside its whole letters together
    with a letter case damage (round 10 charge CH-265,
    seat 17 finding S17-ATK10-17-02): the label stands
    seven characters long, exactly one character stands
    in the run ground of record section 52 ruling (a),
    read at _in_leading_run, that character stands at
    an interior position of the label, not before the
    first letter and not after the last letter, and the
    label with that character removed is the whole
    Status word in a letter case other than the
    capitalised form. The insertion alone takes the
    near marker report through the cleaning at
    _is_near_marker, which removes the ground character
    and compares the cleaned label against the
    capitalised word, and a case damage alone takes it
    through the case reading, which reads a run of ASCII
    letters only, so standing together they took
    nothing: the cleaning comparison is made against
    the capitalised word, which the case damage defeats,
    and the case reading is broken by the ground
    character. The bounds stand stated here: two such
    characters in one label stand outside this joint; a
    joint form at any other label length stands outside
    it; a ground character standing before the first
    letter or after the last letter stands outside it;
    and the capitalised form of the insertion is the
    cleaning form itself and stands outside this joint,
    already signalled."""
    if len(label) != 7:
        return False
    inserted = [index for index in range(7)
                if _in_leading_run(label[index])]
    if len(inserted) != 1:
        return False
    index = inserted[0]
    if index == 0 or index == 6:
        return False
    remaining = label[:index] + label[index + 1:]
    return remaining.lower() == "status" and \
        remaining != "Status"


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
    # A label carrying one interior damage standing
    # before a semicolon in place of the colon separator
    # (round 9 charge CH-220, seat 17 finding
    # S17-ATK9-17-02): the readings that name the
    # separator damage read the label word whole, at the
    # semicolon form above, and the readings that name
    # the interior damage read the line through its colon
    # separator, so a line carrying both stood outside
    # each and took no report, where each damage alone
    # takes it (a semicolon separator with the label
    # letters whole, at the semicolon form above; an
    # interior damage with the colon separator standing,
    # at the CH-111, CH-128, and CH-185 limbs below). The
    # near marker reading takes the joint form where the
    # label before the semicolon stands in the CH-128
    # interior damage form or in the CH-185 run ground
    # substitution form, each with its remaining letters
    # in the capitalised form, on the bounds stated at
    # _is_label_interior_damage and at
    # _is_run_ground_label_substitution: a label carrying
    # a case damage together with its interior damage
    # before the semicolon, three damages on one line,
    # stands outside this joint.
    semicolon = text.find(";")
    colon = text.find(":")
    if semicolon > 0 and (colon < 0 or semicolon < colon):
        joint_label = text[:semicolon]
        if _is_label_interior_damage(joint_label) or \
                _is_run_ground_label_substitution(joint_label):
            return True
        # The same separator joint one damage further, in
        # the two forms round 10 charges (charges CH-264
        # and CH-266, seat 17 findings S17-ATK10-17-01 and
        # S17-ATK10-17-03): a label standing in the CH-219
        # run ground case joint form before the semicolon
        # (one run ground character in place of one label
        # letter, standing with a letter case damage), on
        # the bound stated at
        # _is_run_ground_case_joint_label_damage, and a
        # label carrying a letter case damage alone before
        # the semicolon (the whole label word in a letter
        # case other than the capitalised form). Each pair
        # of the CH-264 damages takes the report through
        # the limbs above and at the colon block below,
        # and the case damage alone takes it at the colon
        # separator through the case reading, while the
        # triples and the case and separator pair stood
        # outside each reading. The pinned member of the
        # neighbouring triple stands outside both forms
        # and stays silent: a case damage standing with a
        # CH-128 interior damage before the semicolon is
        # in neither form, as the CH-220 bound above
        # states it.
        if _is_run_ground_case_joint_label_damage(
                joint_label):
            return True
        if joint_label.lower() == "status" and \
                joint_label != "Status":
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
    colon = text.find(":")
    if colon > 0:
        # An invisible character standing inside the Status
        # label or at its colon edge: the label read with its
        # run ground characters removed is the Status label,
        # while the label as written is not (round 4 charge
        # CH-56, seat 17 finding S17-ATK4-17-03; round 5
        # charge CH-79, seat 17 finding S17-ATK5-17-03, on
        # the ground restated at record section 52 ruling
        # (a), so a character of the name limb or of the
        # private use class inside the label is removed by
        # the same cleaning). The line takes the near marker
        # report, so no Ambiguous stands unexplained on
        # those forms.
        label = text[:colon]
        cleaned = "".join(
            char for char in label if not _in_leading_run(char))
        if cleaned == "Status" and cleaned != label:
            return True
        # A label carrying one charged non letter character
        # inside the label word, or one digit standing after
        # the complete label word (round 6 charge CH-111,
        # seat 17 finding S17-ATK6-17-01): the character
        # stands in neither the letter readings above nor the
        # cleaning ground restated at record section 52
        # ruling (a), so the label took no near marker report
        # and its Ambiguous stood unexplained. The near
        # marker reading takes the charged forms at that
        # joint, on the bound stated at _is_charged_label_damage.
        if _is_charged_label_damage(label):
            return True
        # A label carrying one punctuation, symbol, or
        # number character, or one letter of a script
        # other than the ASCII letters, inside the label
        # word, or one punctuation, symbol, or number
        # character standing after the complete label word
        # (round 7 charge CH-128, seat 17 findings
        # S17-ATK7-17-01 and S17-ATK7-17-02): the letter
        # readings above admit ASCII letters alone, the
        # cleaning above removes the run ground characters
        # only, and the CH-111 limb takes its charged set
        # alone, so the two bounds met and the form took
        # no near marker report, its Ambiguous standing
        # unexplained. The near marker reading takes the
        # charged forms at that joint, on the bound stated
        # at _is_label_interior_damage.
        if _is_label_interior_damage(label):
            return True
        # A label carrying one character of the run ground
        # in place of one of its letters, at an interior
        # position of the word (round 8 charge CH-185, seat
        # 17 finding S17-ATK8-17-01): the character stands
        # in none of the classes the limbs above take, and
        # the cleaning above removes it only where the
        # whole letters of the word still stand, so in
        # place of one letter no reading named the form and
        # its Ambiguous stood unexplained. The near marker
        # reading takes the charged form at that joint, on
        # the bound stated at
        # _is_run_ground_label_substitution.
        if _is_run_ground_label_substitution(label):
            return True
        # A label carrying one interior damage of a cured
        # class together with a letter case damage (round 8
        # charge CH-186, seat 17 finding S17-ATK8-17-02):
        # the case and one edit readings read a run of
        # ASCII letters only, so the interior character
        # breaks their match, and the interior limbs above
        # compare the label against the capitalised word,
        # so a label whose remaining letters stand in
        # another case differs at five positions and took
        # no report, its Ambiguous standing unexplained
        # where each damage alone takes the report. The
        # near marker reading takes the joint form, on the
        # bound stated at _is_case_joint_label_damage.
        if _is_case_joint_label_damage(label):
            return True
        # A label carrying one character of the run ground
        # in place of one of its letters together with a
        # letter case damage (round 9 charge CH-219, seat
        # 17 finding S17-ATK9-17-01): the case reading
        # reads a run of ASCII letters only, so the run
        # ground character breaks its match, the CH-185
        # limb compares the label against the capitalised
        # word, so a label whose remaining letters stand
        # in another case differs at five positions from
        # it, and the CH-186 joint takes its charge only
        # on the CH-128 interior classes, so the joint
        # form took no report, its Ambiguous standing
        # unexplained where each damage alone takes the
        # report. The near marker reading takes the joint
        # form, on the bound stated at
        # _is_run_ground_case_joint_label_damage.
        if _is_run_ground_case_joint_label_damage(label):
            return True
        # A label carrying one character of the run ground
        # inserted beside its whole letters together with
        # a letter case damage (round 10 charge CH-265,
        # seat 17 finding S17-ATK10-17-02): the cleaning
        # above compares the cleaned label against the
        # capitalised word, which the case damage defeats,
        # and the case reading above reads a run of ASCII
        # letters only, which the ground character breaks,
        # so the joint form took no report, its Ambiguous
        # standing unexplained where the insertion alone
        # and the case damage alone each take the report.
        # The near marker reading takes the joint form, on
        # the bound stated at
        # _is_run_ground_insertion_case_joint_label_damage.
        if _is_run_ground_insertion_case_joint_label_damage(
                label):
            return True
        # A label standing before a space or tab run and
        # its colon, carrying one further damage (round 10
        # charges CH-266 and CH-267, seat 17 findings
        # S17-ATK10-17-03 and S17-ATK10-17-04): the
        # separator reading at the head of this function
        # takes the whole capitalised word before its
        # space or tab run, and the readings in this block
        # read the label as the text before the colon,
        # which on these lines carries the space or tab as
        # a further character and stands in none of the
        # stated forms, so a case damage standing with the
        # separator damage, and an interior damage
        # standing with the separator damage on the run
        # ground member at a plain space and on the full
        # stop member at a tab, each took no report where
        # each damage alone takes it. The near marker
        # reading takes the joint forms on the label
        # before the space or tab run: the whole label
        # word in a letter case other than the capitalised
        # form (the CH-266 member), and the CH-128
        # interior damage form and the CH-185 run ground
        # substitution form, each with its remaining
        # letters in the capitalised form (the CH-267
        # members), on the bounds those readings state.
        # The full stop member at the plain space
        # separator already takes the report in this block
        # and stands as the charged finding's contrast
        # pin, outside the charge.
        spaced_label = label.rstrip(" \t")
        if spaced_label != label and spaced_label:
            if spaced_label.lower() == "status" and \
                    spaced_label != "Status":
                return True
            if _is_label_interior_damage(spaced_label) or \
                    _is_run_ground_label_substitution(
                        spaced_label):
                return True
    return False


def _heading_info(line_text):
    # A prefix standing before a heading is absorbed: the
    # heading form is read from the text after any leading run
    # of the one run reading stated at ruling (e) of record
    # section 38 (the format, separator, control, and mark
    # classes, holding every character ruling (d) enumerated),
    # on every path, so a mark combined with a space or a tab,
    # or a space standing alone, never deletes a heading.
    match = _HEADING_RE.match(
        line_text[_leading_status_run(line_text):])
    if not match:
        return None
    return len(match.group(1)), match.group(2)


_TAB_HEADING_RE = re.compile(r"^(#{1,6})\t(.*)$")


def _separator_heading_info(line_text):
    """A heading line whose hashes stand separated from its
    text by a separator run of the ruling (a) ground, or
    None where the line is no such heading.

    The plain space is the only separator the heading reader
    takes after the hashes, so a heading separated by any
    other separator character is no heading at all to
    _heading_info: no unmatched heading Warning can fire for
    it, and its body falls inside the preceding entry span
    (Step 17 round 4, charge CH-58, seat 6 Finding 1, the tab
    form; Step 17 round 5, charge CH-80, seat 6 Finding 1,
    the wider separator forms). This reading names the form
    so the parse can give it the unmatched heading treatment
    its displaced neighbours take. The separator ground is
    the run ground of record section 52 ruling (a), stated
    once for every surface and read here at _in_leading_run:
    a character presenting no visible glyph, the categories
    Cn, Co, Cf, Cc (the governed terminators excepted), Zs,
    Zl, Zp, Mn, Mc, and Me, together with any character, in
    any category, whose Unicode name carries BLANK, FILLER,
    FILL, or REPLACEMENT. The separator run after the hashes
    is a run of characters of that ground carrying at least
    one character that is not the plain space: a run of
    plain spaces alone is the heading reader own separator
    in its wider form and is not this form. The no heading
    side stands in the open: a separator character outside
    the ground, a visible character among them, makes no
    heading here, and prose lines opening with hashes that
    are not headings keep their standing readings. It
    returns the heading level and the heading text as
    written after the separator run, read behind the same
    leading run _heading_info reads behind.
    """
    text = line_text[_leading_status_run(line_text):]
    match = re.match(r"^(#{1,6})", text)
    if not match:
        return None
    rest = text[match.end():]
    index = 0
    while index < len(rest) and _in_leading_run(rest[index]):
        index += 1
    if index == 0:
        return None
    separator = rest[:index]
    if not separator.strip(" "):
        return None
    heading_text = rest[index:]
    # The empty text form stands in this reading (Step 17
    # round 6, charge CH-100, seat 6 Finding 1): a heading
    # line separated from an empty text by a separator
    # character of the ground takes the same unmatched
    # heading treatment the plain space form takes, naming
    # the heading as written, where it was no heading at
    # all to the reader before and was named on no surface.
    # The no heading side stands as stated above: a
    # separator character outside the ground makes no
    # heading, and bare hashes with no separator at all
    # make no heading.
    return len(match.group(1)), heading_text


def _tab_heading_info(line_text):
    """The tab separated heading form of charge CH-58, read
    at _separator_heading_info from Step 17 round 5, charge
    CH-80: the tab stands in the separator ground, and the
    wider reading names every separator form of that ground
    in the one form. This name stands for the CH-58 form."""
    return _separator_heading_info(line_text)


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
    r"( [0-9]{4}-[0-9]{2}-[0-9]{2})?\s*$")
_ADDITION_THIS_ENTRY_RE = re.compile(
    r"^Addition to this entry\b", re.IGNORECASE)
_SEGMENT_STATE_CLAIM_RE = re.compile(
    r"\b(remains|stays|stands|is|was|left)\b[^.]{0,80}?"
    r"\b(open|settled|ruled|closed|banked|parked|presented)\b",
    re.IGNORECASE)


# CH-82, seat 4 F-2, ruled at record section 52 ruling (a):
# the bullet claim below takes the same token continuation
# guard the validate citation scans take. A character stands
# in the continuation ground where it presents no visible
# glyph: the categories Cn, Co, Cf, Cc (the governed
# terminators excepted), Zs, Zl, Zp, Mn, Mc, and Me, beside
# the digit classes Nd, Nl, and No and the colon, together
# with any character, in any category, whose Unicode name
# carries BLANK, FILLER, FILL, or REPLACEMENT; and a visible
# letter, symbol, or connector punctuation character standing
# between two digits continues the token as well.
_BULLET_TOKEN_CONTINUATION_CATEGORIES = frozenset(
    ("Nd", "Nl", "No", "Mn", "Mc", "Me", "Cf", "Cn", "Co",
     "Cc", "Zs", "Zl", "Zp"))


def _bullet_token_continues(text, position):
    """Whether a DQ token whose digits end at position in
    text continues past that position, on the CH-82 ground
    stated above."""
    if position >= len(text):
        return False
    character = text[position]
    if character == ":":
        return True
    if character in " \t\n\r":
        return False
    if unicodedata.category(character) in \
            _BULLET_TOKEN_CONTINUATION_CATEGORIES:
        return True
    name = unicodedata.name(character, "")
    if any(part in name for part in
           ("BLANK", "FILLER", "FILL", "REPLACEMENT")):
        return True
    # CH-129, seat 4 F-1: the digit following limb reads
    # the whole continuation run, not one character only,
    # on the same ground as the validate guard: a run of
    # visible characters of classes L, S, and P, with
    # characters of this guard's ground standing inside
    # the run beside them, that ends at a digit of any
    # script leaves the token plainly unended. The foreign
    # digit is never read as a number; it stands only as
    # the mark that the token does not end at the
    # interrupter. A full stop or a governed terminator
    # standing inside the run ends the run as it ends a
    # token.
    if unicodedata.category(character)[0] in "LSP":
        index = position
        while index < len(text):
            current = text[index]
            if unicodedata.category(current) in \
                    ("Nd", "Nl", "No"):
                return True
            if current == "." or current in " \t\n\r":
                break
            if unicodedata.category(current)[0] in "LSP" \
                    or unicodedata.category(current) in \
                    _BULLET_TOKEN_CONTINUATION_CATEGORIES \
                    or any(part in unicodedata.name(current, "")
                           for part in
                           ("BLANK", "FILLER", "FILL",
                            "REPLACEMENT")):
                index += 1
                continue
            break
    # CH-97, seat 4 F-2: a hyphen class character standing
    # immediately after a token's digits, in the trailing
    # position as in the inside position, marks the token
    # as hyphenated matter, not the clean token, on the
    # parse claim scans this guard serves.
    if unicodedata.category(character) == "Pd":
        return True
    return False


def _guarded_dq_tokens(text):
    """The DQ tokens of a segment line under the
    continuation guard: a token whose digits continue in a
    character of the guard ground, inside its digits or
    after them, is refused whole, never named in part as
    its ASCII head. The segment claim naming reading stands
    on this guard (Step 17 round 6, CH-97, seat 4 F-2)."""
    for match in _DQ_TOKEN_RE.finditer(text):
        if _bullet_token_continues(text, match.end()):
            continue
        yield match.group(0)


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
        stored_taken = False
        masked_head = scanned[_leading_status_run(scanned):]
        if "<!--" in text and not (
                masked_head.startswith(_STATUS_MARKER)
                or masked_head.startswith(_VARIANT_MARKER)):
            # The head Status element reading takes the same
            # stored form act the other labels take (Step 17
            # fix wave 5, charge CH-89, F-11R5-01): where a
            # comment segment stands at a word break of the
            # Status label, between the label and its colon,
            # or inside its one word, the masked form opens
            # with no marker, while the stored form of the
            # line, its segments removed and its parts joined
            # at the segment boundaries alone under the CH-69
            # act at _stored_form, opens with the marker or
            # the variant marker. The scan then reads the
            # stored form, so the head element stands credited
            # and no near marker Warning stands against it.
            # The act reaches segment positions only: where
            # the stored form opens with no marker, the line
            # as written governs exactly as before, so a space
            # before a colon written in the file keeps its
            # near marker form, a marker standing wholly
            # inside a segment counts nothing, and a segment
            # left unclosed credits nothing past its opening.
            stored, _unclosed = _stored_form(text)
            stored_head = stored[_leading_status_run(stored):]
            if stored_head.startswith(_STATUS_MARKER) or \
                    stored_head.startswith(_VARIANT_MARKER):
                scanned = stored
                stored_taken = True
        offset = 0
        effective = scanned
        run = _leading_status_run(scanned)
        if run and run < len(scanned) and (
                scanned[run:].startswith(_STATUS_MARKER)
                or scanned[run:].startswith(_VARIANT_MARKER)
                or _is_near_marker(scanned[run:])):
            if any(_is_blank_presenting(char)
                    for char in scanned[:run]):
                # A run carrying a blank presenting character
                # of the ruling (a) name limb (round 5 charges
                # CH-77 and CH-79): the marker takes the near
                # marker report the blank presenting forms
                # take, instead of reading at line start behind
                # a character a reader cannot see, the standing
                # CH-55 treatment on its restated ground.
                self.near.append(
                    NearMarkerOccurrence(line=number, text=text))
                return False
            offset = run
            effective = scanned[run:]
        if _is_near_marker(effective):
            self.near.append(
                NearMarkerOccurrence(line=number, text=text))
            return False
        # An embedded damaged label: a Status label carrying
        # one charged character of round 6 charge CH-111 or
        # round 7 charge CH-128, standing inside a line behind
        # other matter, is no exact marker, so the marker scan
        # below cannot select it and the line start reading
        # above does not reach it. It takes the near marker
        # report at its embedded position, as an embedded
        # exact marker takes its element and an embedded
        # damaged separator takes its report (round 7 charge
        # CH-128, the embedded only constructions of seat 17
        # findings S17-ATK7-17-01 and S17-ATK7-17-02). The
        # scan reads whole whitespace separated tokens
        # standing before a colon, on the same damage bounds
        # as the line start reading, and nothing wider: a
        # damaged form standing inside a longer token takes
        # no report here.
        # The scan takes the round 8 limbs on the same
        # bounds (charges CH-185 and CH-186, seat 17
        # findings S17-ATK8-17-01 and S17-ATK8-17-02, the
        # embedded only constructions k10, k11, and k36):
        # one character of the run ground in place of one
        # label letter, and one interior damage of a cured
        # class standing together with a letter case damage.
        # The scan takes the round 9 run ground case joint
        # limb on the same bound (charge CH-219, seat 17
        # finding S17-ATK9-17-01, the embedded only
        # construction m24): one character of the run
        # ground in place of one label letter standing
        # together with a letter case damage.
        # The scan takes the round 10 semicolon joint forms
        # at this position beside the colon forms (charges
        # CH-264 and CH-268, seat 17 findings
        # S17-ATK10-17-01 and S17-ATK10-17-05), on the bound
        # stated at the semicolon loop below.
        # The reading stands in its linear form (Step 17
        # fix wave 8, charge CH-155, finding F8-18-1): the
        # line is read once for its runs of non whitespace,
        # non colon characters, and a run takes the damage
        # reading only where a colon stands immediately
        # after it, which is exactly the token set the
        # earlier colon requiring pattern matched, at the
        # same positions and under the same start of line
        # exclusion. The colon requiring pattern itself
        # rescanned the remainder of a run from every
        # position of the run, so one colon free run cost
        # in proportion to the square of its length.
        for token in re.finditer(r"[^\s:]+", effective):
            if token.start() == 0:
                continue
            if token.end() >= len(effective) or \
                    effective[token.end()] != ":":
                continue
            if _is_charged_label_damage(token.group(0)) or \
                    _is_label_interior_damage(token.group(0)) or \
                    _is_run_ground_label_substitution(
                        token.group(0)) or \
                    _is_case_joint_label_damage(token.group(0)) or \
                    _is_run_ground_case_joint_label_damage(
                        token.group(0)):
                self.near.append(NearMarkerOccurrence(
                    line=number, text=text))
        # An embedded damaged label standing before a
        # semicolon separator (round 10 charges CH-264 and
        # CH-268, seat 17 findings S17-ATK10-17-01 and
        # S17-ATK10-17-05): the scan above requires a colon
        # after its token, and the CH-220 limb stands at
        # _is_near_marker only, so the joint forms at the
        # embedded only position took no report, where
        # their line start twins and the embedded colon
        # forms of the same damage classes take it. The
        # scan takes a whole token standing before a
        # semicolon, closed by the end of the line or by a
        # space or a tab, where the label before the
        # semicolon stands in the CH-128 interior damage
        # form or in the CH-185 run ground substitution
        # form (the CH-220 forms, charge CH-268), or in
        # the CH-219 run ground case joint form (the
        # CH-264 embedded member), each on the bounds
        # those helpers state, and nothing wider: the
        # clean label before a semicolon at this position
        # (separator damage alone, case n34 of round 10
        # seat 17) stands in none of the forms and stays
        # silent, the pinned case and interior triple
        # before a semicolon stands in none of them, and a
        # case damage alone before a semicolon at this
        # position stands outside this taking, its line
        # start form cured at CH-266 in _is_near_marker.
        # The embedded only semicolon joint form of round
        # 10 seat 19 observation O-3 is the CH-268 full
        # stop member on its own base and takes this same
        # report, riding inside the bound stated here.
        for token in re.finditer(r"[^\s:]+", effective):
            if token.start() == 0:
                continue
            token_text = token.group(0)
            if not token_text.endswith(";"):
                continue
            if token.end() < len(effective) and \
                    effective[token.end()] not in " \t":
                continue
            joint_label = token_text[:-1]
            if _is_label_interior_damage(joint_label) or \
                    _is_run_ground_label_substitution(
                        joint_label) or \
                    _is_run_ground_case_joint_label_damage(
                        joint_label):
                self.near.append(NearMarkerOccurrence(
                    line=number, text=text))
        if effective.startswith(_STATUS_MARKER) and \
                len(effective) > len(_STATUS_MARKER):
            separator = _separator_run(
                effective[len(_STATUS_MARKER):])
            folded = effective[
                len(_STATUS_MARKER) + len(separator):]
            if effective[len(_STATUS_MARKER)] != " " or \
                    any(char != " " for char in separator) or \
                    (folded and _is_blank_presenting(folded[0])):
                # A separator other than the taught colon and
                # space, a tab or no space at all, takes the
                # near marker report instead of passing as the
                # true form. A separator run of plain spaces
                # stands as it stood; a run carrying any
                # whitespace or format character beyond plain
                # spaces, a tab in any position among them, is
                # no plain space separator and takes the same
                # report, on the CH-21 ground (round 3 charge
                # CH-38).
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
                if not stored_taken and "<!--" in text:
                    # The variant element takes the stored
                    # form act for a segment standing after
                    # its phrasing (round 7 charge CH-127,
                    # F-11R7-03): where the segment stands
                    # after the phrasing and is the line's
                    # sole segment, the masked form opens
                    # with the variant marker itself, so the
                    # CH-89 gate above is not met and the
                    # CH-108 reading, which reaches marker
                    # elements only, never reaches this
                    # branch, and the masked spaces the
                    # segment leaves stand in the recorded
                    # verbatim. The verbatim is therefore
                    # read from the stored form of the
                    # element's own span of the line as
                    # written, its segments removed and its
                    # parts joined at the segment boundaries
                    # alone under the CH-69 act, so the
                    # phrasing stands as the line carries it.
                    # The reading reaches closed segments
                    # only: a segment left unclosed in the
                    # span credits nothing past its opening
                    # and the masked verbatim stands, and a
                    # span carrying no closed segment keeps
                    # its standing reading whole. That bound
                    # is read at its own width (round 8
                    # charge CH-184, F-11R8-03): where a
                    # closed segment stands before an
                    # unclosed segment in the same span, the
                    # stored form of the span removes the
                    # closed segment and credits nothing
                    # past the unclosed opening, so the
                    # stored reading is taken on that form
                    # alike; a span carrying an unclosed
                    # segment alone keeps the masked
                    # verbatim whole, as it stood.
                    span_end = offset + stop \
                        if stop < len(effective) else len(text)
                    span = text[offset + start:span_end]
                    if _closed_segment_openings(span):
                        stored_span, span_unclosed = \
                            _stored_form(span)
                        verbatim = stored_span
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
            if start > 0:
                prefix = effective[:start]
                if prefix and any(
                        _is_blank_presenting(char)
                        for char in prefix) and all(
                        _in_leading_run(char) or
                        _is_blank_presenting(char)
                        for char in prefix):
                    # A marker standing behind a run of run
                    # class and blank presenting characters
                    # only, at what reads as the head of the
                    # line, is demoted from its line start
                    # standing by characters a reader cannot
                    # see: it takes the near marker report
                    # instead of passing as an embedded
                    # element in silence (round 4 charge
                    # CH-55, seat 17 finding S17-ATK4-17-02).
                    self.near.append(NearMarkerOccurrence(
                        line=number, text=text))
                    continue
                embedded_separator = _separator_run(
                    effective[end:stop])
                embedded_folded = effective[
                    end + len(embedded_separator):stop]
                if (embedded_separator and any(
                        char != " " for char in embedded_separator)) or \
                        (embedded_folded and
                         _is_blank_presenting(embedded_folded[0])):
                    # The separator test reaches embedded
                    # occurrences on the same terms as line start
                    # occurrences (round 3 charge CH-38): a
                    # separator run carrying any whitespace or
                    # format character beyond plain spaces takes
                    # the near marker report and carries no
                    # element. A blank presenting character
                    # standing at the head of the value, behind
                    # a plain separator or as the whole
                    # separator, takes the same report at the
                    # embedded position alike, where it folded
                    # into the value in silence (round 4 charge
                    # CH-56, seat 17 finding S17-ATK4-17-01).
                    self.near.append(NearMarkerOccurrence(
                        line=number, text=text))
                    continue
            value = effective[end:stop].lstrip(" ")
            if stop < len(effective):
                value = value.rstrip(" ")
            if start == 0 and not stored_taken and \
                    "<!--" in text:
                # The element value reading on a plain label
                # line takes the stored form act (round 6
                # charge CH-108, F-11R6-01, ruled at record
                # section 58 ruling (d)): where the label
                # stands plain the masked form opens with the
                # marker, the CH-89 gate above is not met, and
                # the scan proceeds on the masked form, in
                # which a comment segment standing inside the
                # disposition value word or after it stands as
                # a run of spaces, splitting the word or
                # padding its recorded form. Where a closed
                # segment stands at or after the start of the
                # value on such a line, the value is read from
                # the stored form of the line, its segments
                # removed and its parts joined at the segment
                # boundaries alone under the CH-69 act, so the
                # value word stands whole and a segment after
                # it leaves no masked padding in the recorded
                # value. Every other position on the line
                # keeps its standing reading: the label and
                # the colon keep the masked and CH-89 readings,
                # the separator keeps the masked separator
                # reading that credits a segment standing
                # between the colon and the value, the
                # occurrence positions keep the masked
                # positions, and a segment left unclosed
                # credits nothing past its opening. That bound
                # is read at its own width (round 7 charge
                # CH-125, F-11R7-01): where the unclosed
                # segment stands after the complete value and
                # a closed segment stands at or after the
                # start of the value, the stored value stands
                # wholly before the unclosed opening, so the
                # stored reading is taken and credits nothing
                # past that opening; where the value runs
                # into the unclosed opening with no closed
                # segment standing at or after the start of
                # the value, standing unfinished at the
                # stored form's end, the masked reading
                # stands whole, as it stood.
                value_start = offset + end + len(
                    _separator_run(effective[end:]))
                openings = [match.start() for match in
                            re.finditer(re.escape("<!--"), text)]
                stored, unclosed = _stored_form(text)
                stored_head = stored[
                    _leading_status_run(stored):]
                if openings and \
                        stored_head.startswith(_STATUS_MARKER):
                    stored_rest = stored_head[
                        len(_STATUS_MARKER):]
                    stored_rest = stored_rest[
                        len(_separator_run(stored_rest)):]
                    stored_stop = len(stored_rest)
                    for marker in (_STATUS_MARKER,
                                   _VARIANT_MARKER):
                        found = stored_rest.find(marker, 1)
                        if 0 < found < stored_stop:
                            stored_stop = found
                    stored_value = stored_rest[:stored_stop]
                    if not unclosed:
                        if any(opening >= value_start
                               for opening in openings):
                            value = stored_value.rstrip(" ")
                    elif any(opening >= value_start for opening
                             in _closed_segment_openings(text)) \
                            and (stored_stop < len(stored_rest)
                                 or stored_value.endswith(" ")):
                        # The CH-125 limb: a closed segment
                        # stands at or after the start of the
                        # value, and the stored value stands
                        # terminated before the end of the
                        # stored form, by a following marker
                        # or by the written break that stood
                        # before the unclosed opening, so the
                        # value the reading credits stands
                        # complete before that opening and
                        # nothing past it is credited.
                        value = stored_value.rstrip(" ")
                    elif any(opening >= value_start for opening
                             in _closed_segment_openings(text)):
                        # The CH-154 limb (round 8 charge
                        # CH-154, F-11R8-01): a closed segment
                        # stands at or after the start of the
                        # value, and the stored value runs to
                        # the end of the stored form with no
                        # trailing plain space, so the
                        # unclosed opening itself stands as
                        # the terminator of the value: the
                        # opening stands adjacent after the
                        # complete value, or after a tab
                        # written before it, which the stored
                        # form treats as a break on the same
                        # terms as a space. The stored reading
                        # is taken and credits nothing past
                        # that opening, on the same bound as
                        # the CH-125 limb above. Where no
                        # closed segment stands at or after
                        # the start of the value, this limb is
                        # not reached and the masked reading
                        # stands whole, as it stood.
                        value = stored_value.rstrip(" \t")
            if start > 0 and not stored_taken and \
                    "<!--" in text and any(
                        other_start == 0 and
                        other_flavour in ("marker", "variant")
                        for other_start, other_flavour, _other_end
                        in starts):
                # An embedded element standing on the head
                # line itself takes the stored form act for
                # its own value (round 7 charge CH-126,
                # F-11R7-02): the CH-108 reading above reaches
                # the line start element only, and the CH-89
                # gate is not met on a plain head line, so a
                # segment inside the value word of a second
                # marker on that line stood as masked spaces
                # in the one reading the element ever took.
                # The head line condition reads the line
                # start element in either flavour (round 8
                # charge CH-158, F-11R8-02): the variant
                # element is a head element in its own
                # flavour, so a head line whose line start
                # element is the variant element is the head
                # line alike, and an embedded marker standing
                # after it on that line takes the stored form
                # reading on the same terms.
                # Where a closed segment stands at or after
                # the start of this element's value, the value
                # is read from the stored form of the
                # element's own span of the line as written,
                # its segments removed and its parts joined
                # at the segment boundaries alone under the
                # CH-69 act. The charge reaches the head line
                # only, where a line start element stands on
                # the same line: an embedded marker on any
                # other line keeps its standing reading, the
                # separator position keeps the masked
                # separator reading taken above, the
                # occurrence positions keep the masked
                # positions, and a segment left unclosed in
                # the span credits nothing, the masked reading
                # standing on such a span whole.
                # That guard stands at its stated bound on
                # the marker first head line (cases b2 and b3
                # of round 8, pinned in the K1 second seat's
                # module). On the variant first head line the
                # bound is read one limb wider (round 9
                # observation O-11R9-3, ruled TO FIX at record
                # section 81 ruling (d) as its own charge in
                # the K1 family cluster): where the line start
                # element is the variant element, a closed
                # segment stands at or after the start of this
                # element's value, and an unclosed segment
                # stands in the same span, the value is read
                # from the stored form of the span on the
                # CH-125 and CH-154 terms, the stored value
                # credited whole and nothing past the unclosed
                # opening credited, so the embedded element
                # stands at its plain twin's standing. Where
                # the line start element carries the marker
                # flavour the guard stands whole as bounded,
                # and where no closed segment stands in the
                # span this limb is not reached.
                # That bound is read one limb wider at the
                # third marker position on the marker first
                # head line (round 10 observation O-11R10-1,
                # ruled TO FIX at record section 83 ruling
                # (d) as its own unnumbered charge in the K1
                # family, in the route of O-11R9-3): where
                # the line start element carries the marker
                # flavour, this element stands at the third
                # marker position, a closed segment stands at
                # or after the start of this element's value,
                # and an unclosed segment stands in the same
                # span, the value is read from the stored
                # form of the span on the same CH-125 and
                # CH-154 terms, the stored value credited
                # whole and nothing past the unclosed opening
                # credited, so the embedded element stands at
                # its plain twin's standing. The limb is
                # narrowed to the third marker position
                # exactly: at the second marker position the
                # guard stands whole as cases b2 and b3 pin
                # it, and at the fourth marker position the
                # masked reading of the span stands whole as
                # it stood, no limb of this charge reaching
                # either.
                value_start = offset + end + len(
                    embedded_separator)
                span_end = offset + stop \
                    if stop < len(effective) else len(text)
                span = text[offset + end:span_end]
                if any(value_start <= opening < span_end
                       for opening in
                       _closed_segment_openings(text)):
                    stored_span, span_unclosed = \
                        _stored_form(span)
                    if not span_unclosed:
                        stored_value = stored_span.lstrip(" ")
                        if stop < len(effective):
                            stored_value = \
                                stored_value.rstrip(" ")
                        value = stored_value
                    elif any(other_start == 0 and
                             other_flavour == "variant"
                             for other_start, other_flavour,
                             _other_end in starts):
                        stored_value = stored_span.lstrip(" ")
                        value = stored_value.rstrip(" \t")
                    elif index == 2 and any(
                            other_start == 0 and
                            other_flavour == "marker"
                            for other_start, other_flavour,
                            _other_end in starts):
                        stored_value = stored_span.lstrip(" ")
                        value = stored_value.rstrip(" \t")
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
                masked_first = _mask_comment_segments(first_text)
                if any(span_start == 0 and
                       not masked_first[span_end:].strip(
                           " \t.,:;!?")
                       for span_start, span_end in
                       _guarded_output_spans(masked_first)):
                    # The paragraph first line is wholly a
                    # guarded output row, a crosswalk tally row
                    # in this branch (CH-51): its label word is
                    # the tally phrasing, not a decision label
                    # performing an act, so no labelled element
                    # stands on it. A first line carrying any
                    # matter past the row takes its element as
                    # before, and quoted ruling lines, which take
                    # no guarded span, are untouched. At CH-68
                    # the wholly test reads the row at the same
                    # width as the span test: trailing sentence
                    # punctuation standing after the row, a
                    # period included, is no matter past the
                    # row, so the two guard loci read the row at
                    # one width (F-20-4-4, second mechanism).
                    return
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


def _closed_segment_openings(text):
    """The opening positions of the closed comment segments
    of one line, in the segment reading _stored_form takes:
    a segment runs from an opener to the first close marker
    after it, and an opener standing inside a segment is
    part of that segment, not an opening of its own. A
    segment left unclosed ends the list, since nothing
    after its opening stands in a closed segment."""
    openings = []
    index = 0
    while True:
        opening = text.find("<!--", index)
        if opening < 0:
            break
        closing = text.find("-->", opening + 4)
        if closing < 0:
            break
        openings.append(opening)
        index = closing + 3
    return openings


def _stored_form(text):
    """The stored form of one line, and its comment state.

    Returns a pair: the line with its comment segments
    removed, and whether a segment stands unclosed at the
    end of the line. The parts of the line are joined at
    the segment boundaries, and the join is normalised at
    those boundaries alone (Step 17 fix wave 4, charge
    CH-69, FLAG 4 at record section 38): where a segment
    stood between two words, the spaces the segment was
    fenced by become the one word break the line as
    written carries, so a multiword label standing genuine
    in the file reads as the label it is; where a segment
    stood between a label and its colon, or before other
    closing punctuation, no space stands at the boundary;
    where a segment stood inside one word, the parts join
    as they stood. Whitespace standing elsewhere in the
    line, written in the file with no segment on it, is
    untouched, so a space before a colon written in the
    file keeps its form and its near marker treatment.
    """
    parts = []
    index = 0
    in_comment = False
    while True:
        opening = text.find("<!--", index)
        if opening < 0:
            parts.append(text[index:])
            break
        parts.append(text[index:opening])
        closing = text.find("-->", opening + 4)
        if closing < 0:
            in_comment = True
            break
        index = closing + 3
    stored = parts[0]
    for part in parts[1:]:
        if not part:
            continue
        if not stored:
            stored = part
            continue
        core = part.lstrip(" \t")
        if core and core[0] in ":,.;!?":
            stored = stored.rstrip(" \t") + core
        elif stored[-1] in " \t" or part[0] in " \t":
            stored = stored.rstrip(" \t") + " " + core
        else:
            stored = stored + part
    return stored, in_comment


def _blank_line_genuine(text):
    """Blank one line standing outside any container.

    Returns a triple: the blanked text, the fence state the
    line leaves behind (a character and run length pair, or
    None), and whether the line ends inside an HTML comment.

    The blanking unit is the comment segment, not the line
    (Step 17 fix wave 2, charge CH-16): each comment segment
    on the line is removed, genuine matter before, between,
    and after segments stands, and a segment left unclosed
    at the end of the line leaves the comment open for the
    lines under it, a comment reopened on the same line
    after a closed one included.

    The stored form of the blanked line is decided first, in
    one act (Step 17 fix wave 3, charge CH-45, ruling (e) at
    record section 26): the comment segments are removed and
    the separator space a segment leaves at the head of the
    line is stripped, on the same terms as the rest of a
    comment closing line is stripped in _inert_blanked_texts,
    so genuine matter after a closed segment stands at the
    head of its stored line and is read as the same matter on
    a closing line is read. The fence test then reads that
    stored form: a stored form opening with a fence run opens
    a fence and the line is blank whole, whether the run
    stood at the head of the line as written or stands at the
    head of the stored form after a closed segment.

    The stored form itself is built by _stored_form, in the
    same one act (Step 17 fix wave 4, charge CH-69): the
    join at a segment boundary is normalised at that
    boundary, at a word break and at a label colon, so the
    matter the stored form carries is the matter the line
    as written carries.
    """
    stored, in_comment = _stored_form(text)
    stored = stored.lstrip()
    run = _FENCE_RUN_RE.match(stored)
    if run:
        return "", (run.group(1)[0], len(run.group(1))), False
    return stored, None, in_comment


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

    The closing test reads the same stored form the opening
    side reads (Step 17 fix wave 4, charge CH-69, FLAG 4 at
    record section 38): a closing line carrying a comment
    segment, before its run or after it, is tested on its
    stored form with the segments removed, so such a line
    closes the fence on the same terms as a plain closing
    line, and genuine matter after it stands credited. A
    candidate whose stored form carries matter after its
    run, an info string included, closes nothing, in a
    segment position as in a plain one.

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
            stored, unclosed = _stored_form(text)
            candidate = stored.strip()
            run = _FENCE_RUN_RE.match(candidate)
            if run and run.group(1)[0] == fence[0] and \
                    len(run.group(1)) >= fence[1] and \
                    not candidate[run.end():].strip():
                fence = None
                in_comment = unclosed
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


def _line_stands_inside_fence(lines, final_index):
    """Whether the line at final_index stands inside a code
    fence: a fence opened by an earlier line of the file and
    not closed before it. The fence state is tracked on the
    same terms _inert_blanked_texts tracks it, the stored
    form test for the opening and the closing run test for
    the close, so the final line test reads the container
    the parser itself applies to every other line (Step 17
    round 5, charge CH-81, ATK5-2-02)."""
    fence = None
    in_comment = False
    for text in lines[:final_index]:
        if fence is not None:
            stored, unclosed = _stored_form(text)
            candidate = stored.strip()
            run = _FENCE_RUN_RE.match(candidate)
            if run and run.group(1)[0] == fence[0] and \
                    len(run.group(1)) >= fence[1] and \
                    not candidate[run.end():].strip():
                fence = None
                in_comment = unclosed
            continue
        if in_comment:
            closing = text.find("-->")
            if closing < 0:
                continue
            _rest, fence, in_comment = _blank_line_genuine(
                text[closing + 3:])
            continue
        if "<!--" not in text and \
                not _FENCE_RUN_RE.match(text.strip()):
            continue
        _blanked, fence, in_comment = _blank_line_genuine(text)
    return fence is not None


def _line_stands_inside_comment(lines, final_index):
    """Whether the line at final_index stands inside an HTML
    comment: a comment opened by an earlier line of the file
    and not closed before it. The comment state is tracked
    on the same terms _line_stands_inside_fence tracks the
    fence state, so the final line test reads the container
    the parser itself applies to every other line (Step 17
    round 6, charge CH-95, ATK6-2-03)."""
    fence = None
    in_comment = False
    for text in lines[:final_index]:
        if fence is not None:
            stored, unclosed = _stored_form(text)
            candidate = stored.strip()
            run = _FENCE_RUN_RE.match(candidate)
            if run and run.group(1)[0] == fence[0] and \
                    len(run.group(1)) >= fence[1] and \
                    not candidate[run.end():].strip():
                fence = None
                in_comment = unclosed
            continue
        if in_comment:
            closing = text.find("-->")
            if closing < 0:
                continue
            _rest, fence, in_comment = _blank_line_genuine(
                text[closing + 3:])
            continue
        if "<!--" not in text and \
                not _FENCE_RUN_RE.match(text.strip()):
            continue
        _blanked, fence, in_comment = _blank_line_genuine(text)
    return in_comment


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
    separator_heading_numbers = set()
    for index, line in enumerate(lines):
        info = _heading_info(line)
        if info is None:
            info = _separator_heading_info(line)
            if info is not None:
                separator_heading_numbers.add(index + 1)
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

    def live_entry_form(number, level, heading_text):
        # A separator separated heading stands in no live
        # entry form (charge CH-58 for the tab form, charge
        # CH-80 for the wider separator ground of ruling
        # (a)): it proves no entry heading presence and no
        # section, as the displaced forms at levels 4 to 6
        # prove none, and its treatment stands in the starts
        # loop below.
        if number in separator_heading_numbers:
            return None
        return entry_form(level, heading_text)

    has_entry_heading = any(
        live_entry_form(number, level, heading_text)
        for number, level, heading_text in headings)

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
            if later[1] == 2 and not live_entry_form(
                    later[0], later[1], later[2]):
                stop = later[0]
                break
        else:
            stop = line_count + 1
        window = []
        for other in headings[position + 1:]:
            if other[0] >= stop:
                break
            window.append(other)
        if not any(live_entry_form(other[0], other[1], other[2])
                   for other in window):
            return False
        if any(other[1] == 3 and live_entry_form(
                other[0], other[1], other[2])
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
            if live_entry_form(other[0], other[1], other[2]):
                first_entry_line = other[0]
                break
        return first_entry_line is not None \
            and number >= first_entry_line

    starts = []
    started = False
    current_kind = "file header"
    for position, (number, level, heading_text) in enumerate(headings):
        if number in separator_heading_numbers and not (
                position == 0 and level == 1) and \
                entry_form(level, heading_text):
            # A heading line whose hashes stand separated
            # from its text by a separator of the ruling (a)
            # ground, standing in entry heading form, is no
            # entry: it takes the unmatched heading treatment
            # under PIN-06, naming the heading as written, as
            # its displaced neighbours at levels 1 and 4 to 6
            # do, and its lines stand in an orphan segment,
            # in no entry span (Step 17 round 4, charge CH-58
            # for the tab form; Step 17 round 5, charge CH-80
            # for the wider separator ground, under ruling
            # (h) at record section 52). The cure names
            # displaced entry heading forms only: a separator
            # separated heading in no entry form takes the
            # ordinary heading handling below, and the queue
            # header at the first position stands as file
            # structure above, taking no Warning and no entry
            # from this cure, under the CH-49 bound at
            # FLAG 12.
            starts.append((number, "orphan unmatched",
                           (level, heading_text, None)))
            started = True
            current_kind = "orphan"
            continue
        form = entry_form(level, heading_text)
        if form:
            starts.append((number, "entry", (level, heading_text, form)))
            started = True
            current_kind = "entry"
            continue
        if level == 1:
            if position == 0:
                continue
            if _numbered_heading(heading_text) or \
                    _unnumbered_heading(heading_text):
                # An entry heading at level 1 stands in no
                # entry form: it takes the unmatched heading
                # treatment under PIN-06, naming the heading
                # as written, as the level 4 to 6 forms do
                # (round 3 charge CH-49). The cure names entry
                # heading forms only: a level 1 heading in no
                # entry form stands as file structure below,
                # and the queue header at the first position
                # stands untouched above.
                starts.append((number, "orphan unmatched",
                               (level, heading_text, None)))
                started = True
                current_kind = "orphan"
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
        if level == 4 and current_kind == "entry" and (
                _numbered_heading(heading_text) or
                _unnumbered_heading(heading_text)):
            # A level 4 heading in entry heading form, number
            # and title in the taught form at the wrong level,
            # is no decision block: it takes the unmatched
            # heading treatment under PIN-06, naming the
            # heading as written, as the level 1 entry form
            # does above, and its lines stand in an orphan
            # segment, in no entry above it (Step 17 round 4
            # charge CH-63, F4-8-1).
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
            # CH-39, seat 4 F-1: a segment whose record carries
            # unmatched_heading stands quarantined at its heading
            # line only. Every claim and citation reading of the
            # segment stands outside that one line; heading lines
            # generally are not excluded, and a valid entry
            # heading line stands as a citation surface.
            if unmatched:
                scan_lines = segment_lines[1:]
            else:
                scan_lines = segment_lines
            named = []
            for _number, segment_text in scan_lines:
                for token in _guarded_dq_tokens(segment_text):
                    if token not in named:
                        named.append(token)
                for token in _R_TOKEN_RE.findall(segment_text):
                    if token not in named:
                        named.append(token)
            claims = []
            segment_joined = "\n".join(
                item[1] for item in scan_lines)
            if "governs" in segment_joined:
                statement = ""
                for _number, segment_text in scan_lines:
                    if "governs" in segment_text:
                        statement = segment_text
                        break
                claim_named = []
                for _number, segment_text in scan_lines:
                    if segment_text.startswith("- "):
                        for token in _guarded_dq_tokens(segment_text):
                            if token not in claim_named:
                                claim_named.append(token)
                claims.append(SegmentClaim(
                    named_entries=claim_named or named,
                    statement=statement))
            for _number, segment_text in scan_lines:
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
                if _bullet_token_continues(
                        segment_text, bullet.end(1)):
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
        if form[0] == "numbered" and any(
                char in heading_text
                for char in "\r\u2028\u2029\u0085\x0b\x0c"):
            # A lone carriage return joining the heading line
            # and a Status line into one logical line: the
            # heading stands on its own part, and the Status
            # parts are scanned as the entry Status lines they
            # are, so each occurrence is counted exactly once.
            # Every tail part is scanned, not only the first:
            # a part whose marker stands behind a byte order
            # mark is selected on its run stripped form (the
            # one run set at ruling (d), so a tail behind one
            # plain space, or behind run characters, is selected
            # as the same text on an ordinary body line is) and
            # passed whole, so the scan reads the marker at its
            # own position, and a part carrying a near marker or
            # a marker in another letter case is selected as
            # well, so the damaged marker takes the near marker
            # report it takes at every body position instead of
            # passing in silence. A separator character standing
            # as the join takes the same split (round 5 charge
            # CH-78, seat 3 finding A5-3-F3): a line separator,
            # a paragraph separator, a next line character, a
            # vertical tab, or a form feed joining the heading
            # line to its Status line, each an ordinary character
            # of its line under the terminator rule, splits the
            # line at the same scan, so the occurrence behind
            # the join is selected and counted or signalled as
            # the carriage return form is, and no part that
            # carries no marker form changes the heading reading.
            parts = re.split(
                r"[\r\u2028\u2029\u0085\x0b\x0c]", heading_text)
            tails = []
            for part in parts[1:]:
                candidate = part[_leading_status_run(part):]
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

    # A split part opening with an entry heading, at either
    # charged join character, takes the file level signal
    # (Step 17 round 6, charge CH-96, seat 3 finding A6-3-F1,
    # ruled at record section 58 ruling (e), option (i)): the
    # CH-78 tail scan above splits a joined line on the join
    # characters but selects a split part only where it opens
    # with a marker, a variant marker, or a near marker, so a
    # part opening with an entry heading was selected by
    # nothing and the entry stood deleted from every count
    # in silence. The cure stands at the tail scan selection:
    # such a part is signalled at file level in the README
    # form, the unmatched heading Warning naming the heading
    # as written, on an orphan segment of the standing form.
    # The brief partition rule at _partition_lines stands
    # unmoved, no entry is raised for the joined heading, and
    # every CH-78 pin stands whole: a part opening with no
    # heading form, and a part opening with a heading in no
    # entry form, takes no signal.
    # The scan's scope stands stated once for charges
    # CH-114 and CH-115 (Step 17 round 7, record section 66
    # ruling (b)): the scan's ground is a heading that
    # stands in heading position and is not recognised, and
    # it does not fire where the line's own heading is
    # recognised and raised, or where the matter stands
    # inert or inside a recognised heading's title. Three
    # bounds give that scope its form here. First, the scan
    # reads each line in its inert blanked form, the form
    # the entry builders read, so heading shaped matter
    # standing inside a fence or a comment stands inert to
    # the scan as it stands inert to the other heading
    # readings (CH-115, the inert limb, seat 3 A7-3-F2).
    # Second, a part that is the line own heading takes no
    # signal: where the text before the part is leading run
    # and join matter only, and the heading readers read
    # the part to the same heading they read the line
    # itself to, the part is the heading the main reading
    # already recognised and raised, and the statement that
    # no entry is raised for it is false (CH-114, seat 1
    # F-7-1-1 and seat 3 A7-3-F1). Third, on a line whose
    # own heading stands in a live entry form, a part
    # standing inside that heading's title takes no signal
    # where no second entry body stands in the file behind
    # the heading line (CH-115, the title limb): the
    # signal's ground is the second entry deleted from
    # every count in silence, and where no entry body
    # stands behind the joined heading, no entry is deleted
    # and the heading shaped matter is title matter of the
    # recognised heading. The charged twin forms of CH-96,
    # whose second bodies stand in the file, stand whole
    # under their pins in both directions. The title limb
    # count stands cured in both of its directions at
    # round 8 (charges CH-156 and CH-157, seat 3 findings
    # A8-3-F1 and A8-3-F2): the body test at
    # _joined_heading_body_stands counts no part of the
    # heading line itself, so a Status shaped tail inside
    # the heading's own title supplies no occurrence, and
    # one body in the span stands for a body, so a genuine
    # joined heading on a single shared body takes its
    # signal; and a part takes no signal beside a standing
    # body where it stands inside the title of the heading
    # segment before it on its line, at
    # _joined_part_is_title_matter, in the narrowed form
    # that test states in the open. The title matter test
    # stands cured again at round 9 (charges CH-191 and
    # CH-192, seat 3 findings A9-3-F1 and A9-3-F2): the
    # word count comparison alone suppressed a genuine
    # joined heading whose title carries more words than
    # its host segment's title, and fired on a title part
    # whose title carries no more words than the segment
    # before it where the one body in the span is the host
    # heading's own; the test now reads the comparison
    # together with the span's body count and the part's
    # own form, in the bound its own comment states. The
    # test stands cured again at round 10 (charges CH-226
    # to CH-233, seat 1 findings A10-1-F1 to A10-1-F5 and
    # seat 3 findings A10-3-F1 to A10-3-F5): its word
    # readings are the title readings, its segment is
    # measured without a fake embedded in its title, and
    # each limb's bound stands stated expressly in the
    # test's own comment, the long title limb at six or
    # seven words of excess beside the one shared body,
    # the two body limb at the next number and at the
    # number after next where the skipped entry stands
    # later, and the single shared body limb on the
    # constructions its comment names.
    heading_by_number = {
        number: (level, heading_text)
        for number, level, heading_text in headings}
    heading_numbers = sorted(heading_by_number)
    headed_entry_numbers = set()
    for _headed_line, _headed_level, _headed_text in headings:
        _headed_form = entry_form(_headed_level, _headed_text)
        if _headed_form is not None and \
                _headed_form[0] == "numbered":
            headed_entry_numbers.add(_headed_form[1][1])

    _ORDINAL_WORDS = (
        "first", "second", "third", "fourth", "fifth",
        "sixth", "seventh", "eighth", "ninth", "tenth",
        "eleventh", "twelfth", "thirteenth", "fourteenth",
        "fifteenth", "sixteenth", "seventeenth",
        "eighteenth", "nineteenth", "twentieth")

    def _ordinal_word(number):
        # The ordinal word of an entry number, for the
        # single shared body limb bound at
        # _joined_part_is_title_matter: the file's own
        # entry titles open with the ordinal word of their
        # number (First question, Second question, Third
        # question), and a part whose title opens with the
        # ordinal word of its own number stands in that
        # form. Numbers past the twentieth carry no ordinal
        # word under this reading, as the bound there
        # states.
        if 1 <= number <= len(_ORDINAL_WORDS):
            return _ORDINAL_WORDS[number - 1]
        return None

    def _title_words(title):
        # The words of a title as the title is read (round
        # 10, charges CH-228 and CH-231, seat 1 finding
        # A10-1-F1 and seat 3 finding A10-3-F4): the heading
        # readers take the title text whole, so a title's
        # words stand separated by whitespace, by hyphens,
        # and by zero width spaces, letter case does not
        # divide a word, and sentence punctuation standing
        # at a word's edge is not part of the word. The
        # earlier reading counted split tokens alone, so a
        # word standing in the segment's own title terms
        # under this reading, and a two word title standing
        # in one split token, were each misread.
        words = []
        for token in re.split(r"[\s\-\u200b]+", title):
            word = token.strip(".,;:!?").casefold()
            if word:
                words.append(word)
        return words

    def _segment_title_reading(title):
        # The segment title as the title matter test
        # measures it (round 10, charge CH-230, seat 1
        # finding A10-1-F2): where the title carries a
        # space joined heading shaped fragment in numbered
        # entry form inside itself, the measured title ends
        # where that fragment begins. The fragment is the
        # title fake form that takes no signal of its own,
        # and counting its words as segment title inflated
        # the measurement and suppressed a genuine joined
        # heading standing behind the segment on the same
        # line.
        start = 0
        while True:
            index = title.find(" ### ", start)
            if index < 0:
                return title
            info = _heading_info(title[index + 1:])
            if info is not None:
                form = entry_form(info[0], info[1])
                if form is not None and \
                        form[0] == "numbered":
                    return title[:index]
            start = index + 1

    def _joined_heading_span_occurrences(number):
        # The line numbers of the entry span's Status
        # occurrences behind the heading line at number,
        # counted in the form _joined_heading_body_count
        # states, with the span's end line beside them.
        span_end = line_count + 1
        for other in heading_numbers:
            if other > number:
                span_end = other
                break
        found = []
        for span_number in range(number + 1, span_end):
            span_text = inert_texts.get(
                span_number, lines[span_number - 1])
            candidate = span_text[_leading_status_run(span_text):]
            if candidate.startswith(_STATUS_MARKER) or \
                    candidate.startswith(_VARIANT_MARKER) or \
                    _is_near_marker(candidate):
                found.append(span_number)
        return found, span_end

    def _joined_heading_extra_occurrences_are_tail(number):
        # Whether every Status occurrence after the first
        # in the span stands at the span's end, with no
        # non blank line behind it in the span (round 10,
        # charge CH-231 case u14 and charge CH-233, seat 3
        # finding A10-3-F4 and seat 1 finding A10-1-F5):
        # such an occurrence begins no further body, it is
        # a further occurrence inside the host entry's own
        # body (a second Status line standing in that body,
        # or a near marker line standing in its prose), so
        # it does not raise the span's body count against
        # the single shared body limb.
        found, span_end = _joined_heading_span_occurrences(
            number)
        if len(found) < 2:
            return False
        for occurrence in found[1:]:
            for span_number in range(occurrence + 1, span_end):
                span_text = inert_texts.get(
                    span_number, lines[span_number - 1])
                if span_text.strip():
                    return False
        return True

    def _joined_heading_one_body_is_full(number):
        # Whether the span's one body stands as a full
        # body, carrying its Question field line behind
        # its Status occurrence (round 10, charge CH-231,
        # seat 3 case u12): the single shared body limb's
        # two word floor was stated beside the near marker
        # body forms, and a part beside a full body stands
        # on the host heading's own complete body, not on
        # a damaged label line and its prose.
        found, span_end = _joined_heading_span_occurrences(
            number)
        if len(found) != 1:
            return False
        for span_number in range(found[0] + 1, span_end):
            span_text = inert_texts.get(
                span_number, lines[span_number - 1])
            if span_text.startswith("Question:"):
                return True
        return False

    def _joined_heading_body_count(number):
        # The number of entry bodies standing in the file
        # behind the heading line at number, for the title
        # limb bound above: the lines of the entry span
        # behind that heading line, running to the next
        # heading, carry Status occurrences, counted on
        # those lines in their inert blanked forms, on the
        # marker, variant
        # marker, and near marker forms the CH-78 tail scan
        # selects. No part of the heading line itself is
        # counted (Step 17 round 8, charge CH-157, seat 3
        # finding A8-3-F2): a Status shaped tail standing
        # inside the heading's own title supplied the
        # second occurrence of the earlier two occurrence
        # count on its own, and the scan fired on title
        # matter where no second entry body stood. And one
        # occurrence stands for a body (charge CH-156,
        # finding A8-3-F1): the one body in the span is the
        # body the joined heading and its host heading
        # share as the file is written, and the earlier
        # bound took no signal for a genuine joined entry
        # heading on that body, deleting the entry in
        # silence.
        found, _span_end = _joined_heading_span_occurrences(
            number)
        return len(found)

    def _joined_heading_body_stands(number):
        return _joined_heading_body_count(number) >= 1

    def _joined_part_is_title_matter(parts, part_index,
                                     joined_info, body_count,
                                     extra_tail_only,
                                     one_full_body):
        # Whether the joined part at part_index stands
        # inside the title of the heading segment before it
        # on its line, for the title limb bound above, in
        # the form cured at round 9 (charges CH-191 and
        # CH-192, seat 3 findings A9-3-F1 and A9-3-F2).
        # The narrowed form of the CH-156 and CH-157 cure
        # read the word count comparison alone: a part
        # stood as title matter wherever the segment before
        # it carried fewer words than the part itself, and
        # a part whose title stood no longer than the
        # segment's stood in heading position. That
        # comparison alone fails in both of its directions.
        # In the suppression direction, a genuine joined
        # entry heading whose title carries more words than
        # its host segment's title was read as title matter
        # beside a standing body and deleted with no signal
        # (CH-191). In the firing direction, a heading
        # shaped part inside a heading's own title whose
        # title carries no more words than the segment
        # before it was read as standing in heading
        # position, and the scan fired on title matter
        # where no entry body stands behind the part at
        # all, the one body in the span being the host
        # heading's own (CH-192). The cured test reads the
        # comparison together with the span's body count
        # and the part's own form, and its bound stands
        # stated here in the open. Where the segment's
        # title stands cut short against the part's title,
        # the part is title matter, except where the part's
        # title exceeds the segment's by seven words or
        # more beside the one shared body (the long title
        # limb: the genuine joined headings of CH-191 on a
        # single shared body), and except where two or
        # more bodies stand in the span and the part
        # carries the next entry number after the segment
        # before it (the two body limb: the genuine joined
        # headings of CH-191 with their own bodies
        # standing, the chain fakes of the held forms,
        # whose numbers are not the next number, standing
        # as title matter under the cut short limb as
        # before). Where the part's title stands no longer
        # than the segment's, the part is title matter
        # where the one body in the span is the host
        # heading's own shared body, the part's title
        # differs from the segment's title, the part's
        # title carries two words or more, and the part's
        # title shares no word with the segment's title
        # (the single shared body limb: the title parts of
        # CH-192, narrowed to that charged bound in the
        # open, because the first form of this limb, the
        # shared body and differing title conditions
        # alone, moved the governing CH-156 pin s02, a
        # genuine differing joined heading on one shared
        # body whose title stands in the host segment's
        # own title terms, First question against Second
        # question); a part carrying the segment's own
        # title (the twin forms), a part carrying a one
        # word title, a part sharing a word with the
        # segment's title, and a part beside two or more
        # standing bodies each stand in heading position
        # under this limb, as the pins state. The named unnumbered entry
        # form never stands as title matter under this
        # test: its heading text is one fixed literal
        # whole, so a part in that form is a complete
        # heading, never a title continuation. Where no
        # entry heading segment stands before the part on
        # the line, this test suppresses nothing.
        # The test stands cured again at round 10
        # (charges CH-226 to CH-233, seat 1 findings
        # A10-1-F1 to A10-1-F5 and seat 3 findings
        # A10-3-F1 to A10-3-F5), and its bound stands
        # stated here in the open, per limb. The word
        # readings of this test are the title readings at
        # _title_words, not split token counts (CH-228,
        # and the two word condition of CH-231), and the
        # segment's title is measured at
        # _segment_title_reading, without a space joined
        # fake embedded in it (CH-230). The long title
        # limb: beside the one shared body, a part whose
        # title exceeds the segment's by six or seven
        # words stands in heading position (CH-226); at
        # eight words of excess or more the part stands
        # as title matter under the cut short limb, the
        # one body in the span being the host heading's
        # own (CH-232), and below six words of excess the
        # cut short limb stands as before. The two body
        # limb: beside two or more standing bodies, a part
        # carrying the next entry number after the
        # segment stands in heading position, and so does
        # a part carrying the number after next where the
        # skipped number stands as a complete entry later
        # in the file (CH-227); a part at any wider number
        # distance stands as title matter under the cut
        # short limb, as the chain fakes of the held forms
        # stand. The single shared body limb: the part is
        # title matter where the bodies in the span are
        # the host heading's own, read with the tail rule
        # at _joined_heading_extra_occurrences_are_tail,
        # so a further occurrence standing at the span's
        # end inside the host entry's own body raises no
        # count against the limb (CH-231, CH-233), the
        # part's title differs from the segment's title,
        # and the part's title carries two words or more,
        # that floor standing waived where the span's one
        # body is a full body carrying its Question field
        # (CH-231), and either the part's title shares no
        # word with the segment's title or every word of
        # the part's title stands in the segment's own
        # title terms (CH-231); a part whose title opens
        # with the ordinal word of its own number stands
        # in heading position under this limb, whether or
        # not its title shares a word with the segment's
        # (CH-229), and a part carrying the segment's own
        # title stands in heading position, as the pins
        # state.
        joined_form = entry_form(joined_info[0], joined_info[1])
        if joined_form is None or joined_form[0] != "numbered":
            return False
        joined_title = joined_form[1][2]
        joined_number = joined_form[1][1]
        joined_word_list = _title_words(joined_title)
        joined_words = len(joined_word_list)
        for back in range(part_index - 1, -1, -1):
            segment_info = _heading_info(parts[back])
            if segment_info is None:
                segment_info = _separator_heading_info(parts[back])
            if segment_info is None:
                continue
            segment_form = entry_form(
                segment_info[0], segment_info[1])
            if segment_form is None:
                continue
            if segment_form[0] == "numbered":
                segment_title = segment_form[1][2]
                segment_number = segment_form[1][1]
            else:
                segment_title = segment_form[1][1]
                segment_number = None
            segment_title = _segment_title_reading(
                segment_title)
            segment_word_list = _title_words(segment_title)
            segment_words = len(segment_word_list)
            if segment_words < joined_words:
                if body_count == 1 and \
                        6 <= joined_words - segment_words <= 7:
                    return False
                if body_count >= 2 and \
                        segment_number is not None and \
                        (joined_number == segment_number + 1 or
                         (joined_number == segment_number + 2
                          and segment_number + 1 in
                          headed_entry_numbers)):
                    return False
                return True
            if (body_count == 1 or extra_tail_only) and \
                    segment_title != joined_title and \
                    (joined_words >= 2 or
                     (joined_words == 1 and one_full_body)):
                if joined_word_list and \
                        set(joined_word_list) <= \
                        set(segment_word_list):
                    return True
                if joined_word_list and \
                        _ordinal_word(joined_number) is not None and \
                        joined_word_list[0] == \
                        _ordinal_word(joined_number):
                    return False
                if not set(segment_word_list) & \
                        set(joined_word_list):
                    return True
            return False
        return False

    for index, line in enumerate(lines):
        number = index + 1
        text = inert_texts.get(number, line)
        if not any(char in text
                   for char in "\r\u2028\u2029\u0085\x0b\x0c"):
            continue
        own_info = _heading_info(text)
        if own_info is None:
            own_info = _separator_heading_info(text)
        own_live = False
        own_heading_text = None
        if number in heading_by_number:
            own_level, own_heading_text = \
                heading_by_number[number]
            own_live = live_entry_form(
                number, own_level, own_heading_text) is not None
        parts = re.split(
            r"[\r\u2028\u2029\u0085\x0b\x0c]", text)
        part_offsets = []
        part_position = 0
        for part in parts:
            part_offsets.append(part_position)
            part_position += len(part) + 1
        for part_index in range(1, len(parts)):
            part = parts[part_index]
            joined_info = _heading_info(part)
            if joined_info is None:
                joined_info = _separator_heading_info(part)
            if joined_info is None:
                continue
            if not entry_form(joined_info[0], joined_info[1]):
                continue
            if own_info is not None and \
                    joined_info == own_info and all(
                        _in_leading_run(char) or char in
                        "\r\u2028\u2029\u0085\x0b\x0c"
                        for char in
                        text[:part_offsets[part_index]]):
                continue
            if number in heading_by_number and all(
                    _in_leading_run(char) or char in
                    "\r\u2028\u2029\u0085\x0b\x0c"
                    for char in
                    text[:part_offsets[part_index]]):
                # The line own heading segment, where further
                # joined matter stands behind it on the line
                # (Step 17 round 8, the held form s32 of attack
                # seat 3, beside charges CH-156 and CH-157):
                # the whole line reading carries the joined
                # matter inside its heading text, so the part
                # does not read equal to that reading at the
                # test above, but the part is still the heading
                # the main reading raised for the line, where
                # the raised heading text opens with the part's
                # heading text at a join boundary and only
                # leading run and join matter stands before the
                # part. The statement that no entry is raised
                # for it is false there, on the CH-114 ground.
                raised_level, raised_text = \
                    heading_by_number[number]
                if raised_level == joined_info[0] and (
                        raised_text == joined_info[1] or any(
                            raised_text.startswith(
                                joined_info[1] + join_char)
                            for join_char in
                            "\r\u2028\u2029\u0085\x0b\x0c")):
                    continue
            if own_live and (not _joined_heading_body_stands(
                    number) or _joined_part_is_title_matter(
                        parts, part_index, joined_info,
                        _joined_heading_body_count(number),
                        _joined_heading_extra_occurrences_are_tail(
                            number),
                        _joined_heading_one_body_is_full(
                            number))):
                continue
            orphans.append(OrphanSegment(
                kind="other file level segment",
                span=Span(number, number, "heading cut"),
                heading_text=joined_info[1],
                unmatched_heading=True,
                lines=[(number, part)],
            ))
            parse_notes.append(ParseNote(
                kind="unmatched heading",
                text="the heading " + joined_info[1] +
                     " matches no entry form, no known file "
                     "level form and no sub part form; its lines "
                     "stand in an orphan segment",
                line_span=Span(number, number, "heading cut"),
            ))

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
                blank_lead = lead
                while blank_lead and \
                        _is_blank_presenting(blank_lead[0]):
                    blank_lead = blank_lead[1:]
                if lead.startswith(_STATUS_MARKER) or \
                        _is_near_marker(lead) or (
                        len(blank_lead) < len(lead) and (
                            blank_lead.startswith(_STATUS_MARKER)
                            or _is_near_marker(blank_lead))):
                    # The preamble reading takes the same run
                    # as the entry scan, and a blank presenting
                    # character standing before the marker takes
                    # the same report there, so a preamble line
                    # does not escape the rule 2 finding behind
                    # a character a reader cannot see (round 4
                    # charge CH-55, the preamble limb).
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
            and _final_line_is_cut_off(
                lines_by_number[line_count],
                _line_stands_inside_fence(lines, line_count - 1),
                _line_stands_inside_comment(lines, line_count - 1),
                lines_by_number[line_count - 1]
                if line_count >= 2 else None))
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
