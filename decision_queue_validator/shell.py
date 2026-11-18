"""Shell: the only module that touches the filesystem and the terminal.

Duties: argument handling for the two subcommands, the pre read
size refusal by stat before reading, reading the input once as
bytes, constructing the Vocabulary value from the shipped copy,
calling parse, validate and render in that order, the exit decision
assembly as an explicit run time step, composing the output in
full, failure reports on the standard error channel, and return of
the exit code the run carries. The shell assigns no state, grades
no finding beyond the exit decision table, counts nothing beyond
that table and decodes nothing for its ordinary work. Where the
pre read size refusal fires, the refusal names the byte breach
from the stat alone, and the file is not read for that naming.
"""

import errno
import os
import stat
import sys

from .parse import parse_queue
from .render import (
    build_shared_head,
    escape_text,
    file_facts_line,
    render_summary,
    render_validate,
    shared_head_lines,
)
from .types import ExitDecision, FileLevelFailure, Input, Limits, Vocabulary
from .validate import validate_model

OUTPUT_FORM_EDITION = "1"

RULE_SET_VERSION = "1"

LIMITS = Limits()

VOCABULARY_VERSION = Vocabulary.shipped().version

MAP_SIZE_LIMIT = 2000000
MAP_SIZE_CAPPED_VALUE = 2000001

CYCLE_COUNT_LIMIT = 1000
CYCLE_COUNT_CAPPED_VALUE = 1001

GAP_NAMING_LIMIT = 2000000

__all__ = [
    "OUTPUT_FORM_EDITION",
    "RULE_SET_VERSION",
    "LIMITS",
    "VOCABULARY_VERSION",
    "build_vocabulary",
    "closing_line",
    "main",
]


def build_vocabulary():
    """Construct the Vocabulary value from the shipped copy."""
    return Vocabulary.shipped()


def _head_lines(input_name, facts_line=None):
    """The head of a shell surface, from the one shared head
    construction in render, and from no second construction.

    Every shell surface carries all five standing positions,
    the file facts line included: where no file facts stand for
    the surface, as on a run that did not take place, the facts
    line states absent at its position.
    """
    if facts_line is None:
        facts_line = file_facts_line(None, None, None, None)
    limits_line = (
        "Limits: %d bytes, %d lines, %d characters per line" % (
            LIMITS.max_bytes, LIMITS.max_lines,
            LIMITS.max_characters_per_line))
    versions_line = (
        "Versions: vocabulary %s, output form %s, rule set %s" % (
            VOCABULARY_VERSION, OUTPUT_FORM_EDITION,
            RULE_SET_VERSION))
    head = build_shared_head(input_name, facts_line, limits_line,
                             versions_line)
    return shared_head_lines(head)


def closing_line(code, reason_text):
    """The closing exit line, in the Item 3 form.

    The line states the exit code, then the reason classes present
    at that code in plain words, then the sentence the brief
    carries: the code is a findings signal and not a step verdict.
    """
    return (
        "Exit: code %d: %s. This code is a findings signal and "
        "not a step verdict." % (code, reason_text))


def _write_stderr(text):
    try:
        sys.stderr.write(text)
        sys.stderr.flush()
        return True
    except (OSError, AttributeError, ValueError):
        try:
            sys.stderr.close()
        except (OSError, AttributeError, ValueError):
            pass
        return False


def _closing_line_of(text):
    """The closing exit line of a composed output, or None."""
    for line in reversed(text.split("\n")):
        if line.startswith("Exit: code "):
            return line
    return None


def _surrogate_safe(text):
    """The text with lone surrogate code points in escaped form.

    A file name the operating system hands over through
    surrogateescape can carry lone surrogates into a report, in
    the input name line above all. Those code points have no
    UTF-8 encoding, so they print in the backslash, u form
    escape_text uses, and the delivery encode cannot crash on
    them.
    """
    out = []
    for char in text:
        code = ord(char)
        if 0xD800 <= code <= 0xDFFF:
            out.append("\\u%04X" % code)
        else:
            out.append(char)
    return "".join(out)


def _deliver_stdout(text):
    """Deliver composed output on standard output.

    Returns True where the output was delivered and False where
    delivery failed. A delivery failure never decides the exit
    code: the caller returns the code the run decided, and the
    failure is reported on standard error together with the
    closing exit line of the output, so that line is not lost.
    """
    try:
        data = _surrogate_safe(text).encode("utf-8")
        sys.stdout.buffer.write(data)
        sys.stdout.buffer.flush()
    except (OSError, AttributeError, ValueError) as exc:
        try:
            sys.stdout.close()
        except (OSError, AttributeError, ValueError):
            pass
        lines = [
            "error: standard output was closed before the output "
            "was delivered (%s)" % escape_text(str(exc))]
        closing = _closing_line_of(text)
        if closing is not None:
            lines.append(closing)
        _write_stderr("\n".join(lines) + "\n")
        return False
    return True


ARGUMENT_ECHO_LIMIT = 120


def _bounded_echo(text):
    """One echoed argument text, carrying a length bound.

    Argument text the shell prints back on an error surface is
    cut at ARGUMENT_ECHO_LIMIT characters. Where the text stands
    over the bound, the cut form states the length of the text
    in full, so a reader can tell the echo was cut and by how
    much. Text at or under the bound prints whole.
    """
    text = str(text)
    if len(text) <= ARGUMENT_ECHO_LIMIT:
        return text
    return "%s [truncated: %d characters in full]" % (
        text[:ARGUMENT_ECHO_LIMIT], len(text))


def _is_flag_token(token):
    """Whether a token in the file position carries a flag form.

    The tool defines no flags. A long form (two dashes, the bare
    double dash separator included), a short form (one dash
    and one character), or a bundled short form (one dash
    carrying two or more ASCII letters and nothing else, as in
    -ab, several single letter flags bundled into one token)
    standing where the input file is expected is a flag token,
    not a file name. A dash leading file name of any other
    shape, such as -dashfile.md, or -ab.md, or -a1, is a file
    name: such names validate directly with no separator.
    """
    if token.startswith("--"):
        return True
    if not token.startswith("-") or len(token) < 2:
        return False
    body = token[1:]
    if len(body) == 1:
        return True
    return body.isascii() and body.isalpha()


def _unexpected_token(argv):
    """The token the arity check names as unexpected.

    The file token is examined: where a flag form stands in the
    file position, that token is the unexpected one, and the
    file token after it is not named. Otherwise the token after
    the file is the unexpected one, as in the two file case.
    """
    if _is_flag_token(argv[1]):
        return argv[1]
    return argv[2]


def _usage_error(message):
    """The usage error surface, delivered as every other
    standard error surface is delivered: through
    _deliver_stderr_run, so where standard error cannot take
    the surface its closing exit line is delivered on standard
    output and the decided code 2 stands in every case.
    """
    lines = [
        "Call fault: usage error. No run took place and no file "
        "was read as a queue.",
        "Usage error: %s" % escape_text(_bounded_echo(message)),
        "Usage: python3 -m decision_queue_validator "
        "{validate|render} INPUT",
        closing_line(2, "usage error"),
    ]
    return _deliver_stderr_run("\n".join(lines) + "\n", 2)


def _os_error_cause(exc):
    """The exact input not read cause an OS error names, or None.

    Where the error carries one of the causes the surface can
    state exactly, that cause stands in the detail in place of a
    list of possibilities. Where the error names none of them,
    None stands and the caller states only that the input could
    not be read.
    """
    if isinstance(exc, FileNotFoundError):
        return "it is missing"
    if isinstance(exc, NotADirectoryError):
        return "part of its path is not a directory"
    if isinstance(exc, PermissionError):
        return "it is unreadable"
    if isinstance(exc, IsADirectoryError):
        return "it is a directory"
    err = getattr(exc, "errno", None)
    if err == errno.ENOENT:
        return "it is missing"
    if err == errno.ENOTDIR:
        return "part of its path is not a directory"
    if err in (errno.EACCES, errno.EPERM):
        return "it is unreadable"
    if err == errno.EISDIR:
        return "it is a directory"
    if err == errno.ELOOP:
        return "it is a symlink loop"
    if err == errno.ENAMETOOLONG:
        return "its name is too long"
    if err == errno.EMFILE:
        return "too many files are open"
    if err == errno.ENFILE:
        return "too many files are open in the system"
    if err == errno.EIO:
        return "an input/output error occurred"
    return None


def _not_read_detail(input_name, cause):
    """The detail of an input not read line: the cause alone.

    The file name stands once on this surface, in the Input
    head line, in the bounded form _not_read_output prints.
    The detail line does not echo the name a second time; it
    states the exact cause the run knows, and nothing else.
    """
    return cause


def _not_read_output(input_name, detail):
    lines = _head_lines(_bounded_echo(input_name))
    lines.append("")
    lines.append(
        "Call fault: input not read. No run took place and no "
        "file was read as a queue.")
    lines.append("Input not read: %s" % detail)
    lines.append(closing_line(2, "input not read"))
    return "\n".join(lines) + "\n"


def _refusal_output(input_name, fault_lines, facts_line,
                    reason_text):
    """The whole file refusal surface. Its head is built from
    the bounded echo of the input name, as the not read surface
    builds its head: this surface prints on standard error, so
    the argument echo bound applies to it in full.
    """
    lines = _head_lines(_bounded_echo(input_name), facts_line)
    lines.append("")
    lines.append("File fault: this file was not validated.")
    lines.extend(fault_lines)
    lines.append(closing_line(3, reason_text))
    return "\n".join(lines) + "\n"


def _file_facts_line(byte_count, line_count, digest,
                     source_designation=None):
    """The file facts line of a refusal surface, in the shared
    head form render owns.

    The source designation prints only where a value carrying it
    stands for the run; no designation is supplied here where
    none stands.
    """
    return file_facts_line(source_designation, line_count,
                           byte_count, digest)


def _failure_output(failure):
    fault_lines = []
    for kind in failure.failure_kinds or []:
        fault_lines.append("Failure kind: %s" % escape_text(str(kind)))
    measured_values = dict(
        getattr(failure, "breached_measured_values", None) or {})
    if failure.breached_limit and \
            failure.breached_limit not in measured_values and \
            failure.measured_value is not None:
        measured_values[failure.breached_limit] = failure.measured_value
    named_limits = list(failure.breached_limits or [])
    if failure.breached_limit and \
            failure.breached_limit not in named_limits:
        named_limits.insert(0, failure.breached_limit)
    for name in named_limits:
        if name in measured_values:
            fault_lines.append(
                "Breached limit: %s, measured value %s." % (
                    escape_text(str(name)),
                    escape_text(str(measured_values[name]))))
        else:
            fault_lines.append(
                "Breached limit: %s." % escape_text(str(name)))
    if failure.missing_structure:
        fault_lines.append(
            "Missing structure: %s" % escape_text(
                str(failure.missing_structure)))
    invalid_byte_offset = getattr(
        failure, "invalid_byte_offset", None)
    if invalid_byte_offset is not None:
        fault_lines.append(
            "Invalid byte offset: %s" % escape_text(
                str(invalid_byte_offset)))
    reason_text = "whole file refusal"
    decision = failure.exit_decision
    if decision is not None and decision.reason_classes:
        reason_text = "; ".join(
            escape_text(str(item)) for item in decision.reason_classes)
    return _refusal_output(
        failure.input_name, fault_lines,
        _file_facts_line(
            failure.byte_count, failure.line_count, failure.digest,
            getattr(failure, "source_designation", None)),
        reason_text)


def _gap_naming_size(output):
    """The gap naming size for the run, in characters.

    The size is the number of characters the numeric gap class
    would print in naming every missing value: the decimal digits
    of each missing value plus one separator character for each
    value after the first. It is computed by digit count, by
    subtraction at the powers of ten, without naming or listing
    the missing values, and with each distinct DQ number value
    present in the span removed exactly once at its own digit
    count, as plan Item 9, section 9.6 states in its Step 12
    correction. The values are the integer values the entry
    identifiers denote, under the value key, never the width of
    the digit text as written.
    """
    values = set()
    entries = _items(_get(output, "entries", "entry_results",
                          "per_entry"))
    for entry in entries:
        ident = _get(entry, "identifier", "entry_id", "id",
                     "dq_number")
        if ident is None:
            continue
        text = str(ident).strip()
        if not text.startswith("DQ-"):
            continue
        digits = text[3:]
        if not digits.isdigit():
            continue
        try:
            values.add(int(digits))
        except ValueError:
            continue
    if len(values) < 2:
        return 0
    low = min(values)
    high = max(values)
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


def _gap_refusal_output(input_name, facts_line, size,
                        total_size=None):
    if total_size is not None and total_size != size:
        # The one measure of the bound is the run total naming
        # output: the measured single naming size, and the total
        # it stands at over the run's printings, which is the
        # measure that stands over the limit.
        fault_lines = [
            "Gap naming size limit: the run total gap naming "
            "output stands over the limit of 2000000 characters; "
            "the measured gap naming size is %d characters, and "
            "the run total naming output is %d characters."
            % (size, total_size),
            "The numeric gap class does not fire on this run, "
            "and no part of the missing set is named.",
        ]
    else:
        fault_lines = [
            "Gap naming size limit: the gap naming size stands "
            "over the limit of 2000000 characters; the measured "
            "gap naming size is %d characters." % size,
            "The numeric gap class does not fire on this run, "
            "and no part of the missing set is named.",
        ]
    return _refusal_output(
        input_name, fault_lines, facts_line,
        "whole file refusal: a limit breach")


def _cycle_refusal_output(input_name, facts_line,
                          measured=CYCLE_COUNT_CAPPED_VALUE):
    fault_lines = [
        "Supersession cycle count limit: the supersession "
        "cycle inventory stands over the limit of %d distinct "
        "cycles; counting stopped during enumeration at the "
        "capped measured value of %d cycles, and the true "
        "cycle inventory stands over the limit."
        % (CYCLE_COUNT_LIMIT, measured),
        "The cycle inventory does not stand complete on this "
        "run, and no part of it is reported as a complete "
        "inventory.",
    ]
    return _refusal_output(
        input_name, fault_lines, facts_line,
        "supersession cycle count limit")


def _map_refusal_output(input_name, facts_line):
    fault_lines = [
        "Supersession map size limit: the supersession map print "
        "size stands over the limit of 2000000 characters; "
        "counting stopped at the cap, the capped measured value "
        "is 2000001 characters, and the true map print size "
        "stands over the limit.",
    ]
    return _refusal_output(
        input_name, fault_lines, facts_line,
        "supersession map size limit")


def _get(value, *names, default=None):
    for name in names:
        if isinstance(value, dict):
            if name in value and value[name] is not None:
                return value[name]
        elif value is not None and hasattr(value, name):
            found = getattr(value, name)
            if found is not None and not callable(found):
                return found
    return default


def _items(value):
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return list(value)
    return [value]


def _number(value):
    if value is None:
        return 0
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    inner = getattr(value, "value", None)
    if isinstance(inner, int):
        return inner
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _cycle_refusal_signal(output):
    """The cycle count refusal signal validate may carry, or
    None. The signal stands where the distinct cycle
    inventory passed its bound during enumeration, on either
    subcommand (Step 17 round 3, CH-32)."""
    if isinstance(output, FileLevelFailure):
        return None
    for name in ("cycle_over_bound",
                 "supersession_cycle_over_bound"):
        if _get(output, name):
            return True
    return None


def _map_refusal_signal(output):
    """The map size refusal signal validate may carry, or None."""
    if isinstance(output, FileLevelFailure):
        return output
    for name in ("map_refusal", "supersession_map_refusal",
                 "map_size_refusal"):
        signal = _get(output, name)
        if signal is not None:
            return signal
    for name in ("map_over_bound", "map_size_over_bound",
                 "supersession_map_over_bound"):
        if _get(output, name):
            return True
    decision = _get(output, "exit_decision", "exit")
    reasons = [str(item) for item in _items(
        _get(decision, "reason_classes", "reasons"))]
    if any("supersession map size limit" in item for item in reasons):
        return True
    return None


def _assemble_exit_decision(output):
    """The exit decision assembly step of this slice.

    Shell applies the OP-Q4 precedence, highest first 2, then 3,
    then 4, then 1, then 0, to the reason classes validate
    supplies, and supplies the exit decision field of the render
    model before the model is handed to render. Codes 2 and 3 are
    decided on their own surfaces before this step runs, so the
    table here reads from the tool inconsistency row down.
    """
    findings = _items(_get(output, "findings", "findings_list"))
    errors = sum(1 for item in findings
                 if _get(item, "severity", "grade") == "Error")
    warnings = sum(1 for item in findings
                   if _get(item, "severity", "grade") == "Warning")
    recon = _get(output, "reconciliation", "reconciliation_block")
    check = _get(recon, "self_check", "self_check_result")
    if check is None:
        check = _get(output, "self_check", "self_check_result")
    tool_inconsistent = False
    if check is not None:
        ok = _get(check, "sums_agree", "ok", "passed", "agrees")
        if ok is not None and not bool(ok):
            tool_inconsistent = True
    ambiguous = _number(_get(recon, "ambiguous_count", "ambiguous"))
    unparsed = _number(_get(recon, "unparsed_count",
                            "unparsed_entries"))
    supplied = _get(output, "reason_class_inputs",
                    "exit_reason_inputs")
    supplied_text = " ".join(
        str(item) for item in _items(supplied)).lower()
    if "inconsist" in supplied_text:
        tool_inconsistent = True
    if tool_inconsistent:
        return ExitDecision(
            code=4, reason_classes=["tool inconsistency"]), None
    if ambiguous or unparsed:
        reasons = []
        if ambiguous:
            reasons.append(
                "a total stated under undetermined state: an "
                "Ambiguous entry stands in the file")
        if unparsed:
            reasons.append(
                "a total stated under undetermined state: an "
                "unparsed entry stands in the file")
        masked = None
        if errors or warnings:
            masked = (errors, warnings)
            reasons.append(
                "masked findings present: %d Error findings, "
                "%d Warning findings" % (errors, warnings))
        return ExitDecision(code=4, reason_classes=reasons), masked
    if errors or warnings:
        reasons = []
        if errors:
            reasons.append("Error findings present")
        if warnings:
            reasons.append("Warning findings present")
        return ExitDecision(code=1, reason_classes=reasons), None
    return ExitDecision(
        code=0, reason_classes=["no findings above Note grade"]), None


def _supply_exit_decision(output, decision, masked):
    """The supply point of the shell supplied model fields.

    Shell supplies the exit decision field of the render model,
    and the rule set version field from its own constant, after
    validate has handed its results over and before the model
    is handed to render. The masked findings summary stands on
    the Exit decision alone, in its declared field, and is
    attached to no other value.
    """
    try:
        output.exit_decision = decision
    except (AttributeError, TypeError):
        if isinstance(output, dict):
            output["exit_decision"] = decision
    try:
        output.rule_set_version = RULE_SET_VERSION
    except (AttributeError, TypeError):
        if isinstance(output, dict):
            output["rule_set_version"] = RULE_SET_VERSION
    if masked is not None:
        try:
            decision.masked_findings_summary = {
                "Error": masked[0], "Warning": masked[1]}
        except (AttributeError, TypeError):
            pass


def _pre_read_fault_lines(input_name, byte_size):
    """The fault lines of the pre read size refusal.

    The byte breach stands from the stat alone, and it is the
    only breach this refusal names (Step 17, seat 5 Findings 1
    and 3, merged): the byte limit is checked from the file
    size before the file is read, so no read is taken for
    this naming, and no line count and no per line measurement
    of the refused file stands on the refusal. The refusal
    prints the byte count only. The byte breach is named in
    the form the parse layer uses, with its measured value
    and its limit in force. The input name stands in the
    signature for the call form in main; no use of it is made
    here, because any use that read the file would defeat the
    refusal.
    """
    return [
        "Breached limit: max bytes, measured value %d. "
        "The limit in force is %d." % (byte_size, LIMITS.max_bytes)]


def main(argv=None):
    """Run one command line invocation; return the exit code it carries."""
    try:
        sys.set_int_max_str_digits(16384)
    except (AttributeError, ValueError):
        pass
    if argv is None:
        argv = sys.argv[1:]
    argv = list(argv)
    if not argv:
        return _usage_error("a subcommand and an input file are required")
    if argv[0] not in ("validate", "render"):
        return _usage_error("unknown subcommand: %s" % argv[0])
    if len(argv) < 2:
        return _usage_error("an input file is required")
    if len(argv) > 2:
        return _usage_error(
            "unexpected argument: %s" % _unexpected_token(argv))
    subcommand = argv[0]
    input_name = argv[1]

    # The stat before reading decides the file kind and carries
    # the pre read size refusal, naming the limit and the measured
    # value at exit 3, before any byte is read.
    try:
        input_stat = os.stat(input_name)
    except OSError as exc:
        cause = _os_error_cause(exc)
        if cause is None:
            cause = "it could not be read"
        return _deliver_stderr_run(_not_read_output(
            input_name, _not_read_detail(input_name, cause)), 2)
    if stat.S_ISDIR(input_stat.st_mode):
        return _deliver_stderr_run(_not_read_output(
            input_name,
            _not_read_detail(input_name, "it is a directory")), 2)
    if not stat.S_ISREG(input_stat.st_mode):
        return _deliver_stderr_run(_not_read_output(
            input_name,
            _not_read_detail(
                input_name, "it is not a regular file")), 2)
    if input_stat.st_size > LIMITS.max_bytes:
        fault_lines = _pre_read_fault_lines(
            input_name, input_stat.st_size)
        text = _refusal_output(
            input_name, fault_lines,
            _file_facts_line(input_stat.st_size, None, None),
            "whole file refusal: a limit breach")
        return _deliver_stderr_run(text, 3)

    # Read the input once, as bytes.
    try:
        with open(input_name, "rb") as stream:
            raw_bytes = stream.read()
    except OSError as exc:
        cause = _os_error_cause(exc)
        if cause is None:
            cause = "it could not be read"
        return _deliver_stderr_run(_not_read_output(
            input_name, _not_read_detail(input_name, cause)), 2)

    vocabulary = build_vocabulary()
    result = parse_queue(
        Input(input_name=input_name, raw_bytes=raw_bytes), LIMITS)
    if isinstance(result, FileLevelFailure):
        decision = result.exit_decision
        code = decision.code if decision is not None else 3
        return _deliver_stderr_run(_failure_output(result), code)

    output = validate_model(result, vocabulary, OUTPUT_FORM_EDITION)

    # The gap naming bound (plan Item 9, section 9.6, Step 12
    # correction): where the gap naming size stands over the
    # bound, the run takes the whole file refusal at exit 3 as a
    # limit breach under OP-Q4, on either subcommand, before any
    # part of the ordinary output is delivered and before the
    # exit decision assembly, since code 3 stands above code 4
    # in that precedence. The refusal surface stands on standard
    # error, naming the limit and the measured size, and no part
    # of the missing set is named.
    # The bound stands on one measure in both places (Step 17
    # round 2, CH-18): the measure is the run total naming
    # output that validate suppresses the gap class on, carried
    # on the output as its gap over bound flag and its total
    # naming size. The refusal reads that measure from the
    # output and does not recompute a second measure of its
    # own; where an output carries no flag, the single naming
    # size measure stands as the fallback.
    gap_size = _gap_naming_size(output)
    gap_total_size = _get(output, "gap_naming_total_size")
    gap_over_bound = _get(
        output, "gap_naming_over_bound", "gap_over_bound")
    if gap_over_bound is None:
        gap_over_bound = gap_size > GAP_NAMING_LIMIT
        gap_total_size = None
    if gap_over_bound:
        facts = _get(output, "file_facts", "file_facts_data")
        facts_line = None
        if facts is not None:
            facts_line = _file_facts_line(
                _number(_get(facts, "byte_count")),
                _number(_get(facts, "line_count")),
                _get(facts, "digest"),
                _get(facts, "source_designation"))
        return _deliver_stderr_run(_gap_refusal_output(
            input_name, facts_line, gap_size,
            total_size=gap_total_size), 3)

    # The cycle count bound (Step 17 round 3, CH-32): where
    # the distinct cycle inventory passed its bound during
    # enumeration, the run takes the whole file refusal at
    # exit 3 naming the bound, on either subcommand, before
    # any part of the ordinary output is delivered and before
    # the render map refusal is read, since the cycle refusal
    # is computed during enumeration and the map refusal only
    # after it. No truncated cycle inventory is presented as
    # complete on this surface or any other.
    if _cycle_refusal_signal(output) is not None:
        facts = _get(output, "file_facts", "file_facts_data")
        facts_line = None
        if facts is not None:
            facts_line = _file_facts_line(
                _number(_get(facts, "byte_count")),
                _number(_get(facts, "line_count")),
                _get(facts, "digest"),
                _get(facts, "source_designation"))
        measured = _number(_get(output, "cycle_count_measured"))
        if not measured:
            measured = CYCLE_COUNT_CAPPED_VALUE
        return _deliver_stderr_run(_cycle_refusal_output(
            input_name, facts_line, measured), 3)

    if subcommand == "render":
        signal = _map_refusal_signal(output)
        if signal is not None:
            facts = _get(output, "file_facts", "file_facts_data")
            facts_line = None
            if facts is not None:
                facts_line = _file_facts_line(
                    _number(_get(facts, "byte_count")),
                    _number(_get(facts, "line_count")),
                    _get(facts, "digest"),
                    _get(facts, "source_designation"))
            elif isinstance(signal, FileLevelFailure):
                facts_line = _file_facts_line(
                    signal.byte_count, signal.line_count, signal.digest,
                    getattr(signal, "source_designation", None))
            return _deliver_stderr_run(_map_refusal_output(
                input_name, facts_line), 3)

    decision, masked = _assemble_exit_decision(output)
    _supply_exit_decision(output, decision, masked)
    if subcommand == "validate":
        text = render_validate(output)
    else:
        text = render_summary(output)
    reason_text = "; ".join(decision.reason_classes)
    text += closing_line(decision.code, reason_text) + "\n"
    _deliver_stdout(text)
    return decision.code


def _deliver_stderr_run(text, code):
    """Deliver a refusal or not read surface on standard error.

    Returns the exit code the surface carries, whether or not
    delivery succeeds: a delivery failure does not replace that
    code with 2. Where standard error cannot take the surface,
    the closing exit line is delivered on standard output, so
    that line is not lost.
    """
    if _write_stderr(text):
        return code
    closing = _closing_line_of(text)
    if closing is not None:
        try:
            data = _surrogate_safe(closing + "\n").encode("utf-8")
            sys.stdout.buffer.write(data)
            sys.stdout.buffer.flush()
        except (OSError, AttributeError, ValueError):
            try:
                sys.stdout.close()
            except (OSError, AttributeError, ValueError):
                pass
    return code
