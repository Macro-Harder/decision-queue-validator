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
pre read size refusal fires, the shell takes the line and per
line measurements the refusal must name, from a read taken for
that naming alone, so the refusal names every breached limit.
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


def _deliver_stdout(text):
    """Deliver composed output on standard output.

    Returns 0 on delivery, or 2 where delivery fails, reporting
    the failure on standard error where that channel stands.
    """
    data = text.encode("utf-8")
    try:
        sys.stdout.buffer.write(data)
        sys.stdout.buffer.flush()
    except (OSError, AttributeError, ValueError) as exc:
        try:
            sys.stdout.close()
        except (OSError, AttributeError, ValueError):
            pass
        _write_stderr(
            "error: standard output was closed before the output "
            "was delivered (%s)\n" % escape_text(str(exc)))
        return 2
    return 0


def _usage_error(message):
    lines = [
        "Call fault: usage error. No run took place and no file "
        "was read as a queue.",
        "Usage error: %s" % escape_text(message),
        "Usage: python3 -m decision_queue_validator "
        "{validate|render} INPUT",
        closing_line(2, "usage error"),
    ]
    _write_stderr("\n".join(lines) + "\n")
    return 2


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
        return "it is missing"
    if isinstance(exc, PermissionError):
        return "it is unreadable"
    if isinstance(exc, IsADirectoryError):
        return "it is a directory"
    err = getattr(exc, "errno", None)
    if err in (errno.ENOENT, errno.ENOTDIR):
        return "it is missing"
    if err in (errno.EACCES, errno.EPERM):
        return "it is unreadable"
    if err == errno.EISDIR:
        return "it is a directory"
    return None


def _not_read_detail(input_name, cause):
    return "%s: %s" % (escape_text(input_name), cause)


def _not_read_output(input_name, detail):
    lines = _head_lines(input_name)
    lines.append("")
    lines.append(
        "Call fault: input not read. No run took place and no "
        "file was read as a queue.")
    lines.append("Input not read: %s" % detail)
    lines.append(closing_line(2, "input not read"))
    return "\n".join(lines) + "\n"


def _refusal_output(input_name, fault_lines, facts_line,
                    reason_text):
    lines = _head_lines(input_name, facts_line)
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


def _gap_refusal_output(input_name, facts_line, size):
    fault_lines = [
        "Gap naming size limit: the gap naming size stands over "
        "the limit of 2000000 characters; the measured gap naming "
        "size is %d characters." % size,
        "The numeric gap class does not fire on this run, and no "
        "part of the missing set is named.",
    ]
    return _refusal_output(
        input_name, fault_lines, facts_line,
        "whole file refusal: a limit breach")


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

    The byte breach stands from the stat. Every other breached
    limit is measured from a read taken for this naming alone:
    the line count under the terminator rule (a line feed ends a
    line, a carriage return before it is part of the terminator,
    and a final line with no terminator still counts), and the
    longest line in characters where the bytes decode as UTF-8.
    Where that read cannot be taken, the byte breach alone is
    named. Each breached limit is named in the form the parse
    layer uses, with its measured value and its limit in force.
    """
    breached = [("max bytes", byte_size, LIMITS.max_bytes)]
    try:
        with open(input_name, "rb") as stream:
            raw = stream.read()
    except OSError:
        raw = None
    if raw is not None:
        line_count = raw.count(b"\n")
        if raw and not raw.endswith(b"\n"):
            line_count += 1
        if line_count > LIMITS.max_lines:
            breached.append(
                ("max lines", line_count, LIMITS.max_lines))
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            text = None
        if text is not None:
            parts = text.split("\n")
            if text.endswith("\n"):
                parts = parts[:-1]
                terminated = len(parts)
            else:
                terminated = len(parts) - 1
            longest = 0
            for index, part in enumerate(parts):
                if index < terminated and part.endswith("\r"):
                    part = part[:-1]
                if len(part) > longest:
                    longest = len(part)
            if longest > LIMITS.max_characters_per_line:
                breached.append((
                    "max characters per line", longest,
                    LIMITS.max_characters_per_line))
    return [
        "Breached limit: %s, measured value %d. "
        "The limit in force is %d." % (name, measured, limit)
        for name, measured, limit in breached]


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
        return _usage_error("unexpected argument: %s" % argv[2])
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
        delivered = _deliver_stderr_run(_not_read_output(
            input_name, _not_read_detail(input_name, cause)))
        return delivered if delivered != 0 else 2
    if stat.S_ISDIR(input_stat.st_mode):
        delivered = _deliver_stderr_run(_not_read_output(
            input_name,
            _not_read_detail(input_name, "it is a directory")))
        return delivered if delivered != 0 else 2
    if not stat.S_ISREG(input_stat.st_mode):
        delivered = _deliver_stderr_run(_not_read_output(
            input_name,
            _not_read_detail(
                input_name, "it is not a regular file")))
        return delivered if delivered != 0 else 2
    if input_stat.st_size > LIMITS.max_bytes:
        fault_lines = _pre_read_fault_lines(
            input_name, input_stat.st_size)
        text = _refusal_output(
            input_name, fault_lines,
            _file_facts_line(input_stat.st_size, None, None),
            "whole file refusal: a limit breach")
        delivered = _deliver_stderr_run(text)
        return delivered if delivered != 0 else 3

    # Read the input once, as bytes.
    try:
        with open(input_name, "rb") as stream:
            raw_bytes = stream.read()
    except OSError as exc:
        cause = _os_error_cause(exc)
        if cause is None:
            cause = "it could not be read"
        delivered = _deliver_stderr_run(_not_read_output(
            input_name, _not_read_detail(input_name, cause)))
        return delivered if delivered != 0 else 2

    vocabulary = build_vocabulary()
    result = parse_queue(
        Input(input_name=input_name, raw_bytes=raw_bytes), LIMITS)
    if isinstance(result, FileLevelFailure):
        delivered = _deliver_stderr_run(_failure_output(result))
        if delivered != 0:
            return delivered
        decision = result.exit_decision
        return decision.code if decision is not None else 3

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
    gap_size = _gap_naming_size(output)
    if gap_size > GAP_NAMING_LIMIT:
        facts = _get(output, "file_facts", "file_facts_data")
        facts_line = None
        if facts is not None:
            facts_line = _file_facts_line(
                _number(_get(facts, "byte_count")),
                _number(_get(facts, "line_count")),
                _get(facts, "digest"),
                _get(facts, "source_designation"))
        delivered = _deliver_stderr_run(_gap_refusal_output(
            input_name, facts_line, gap_size))
        return delivered if delivered != 0 else 3

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
            delivered = _deliver_stderr_run(_map_refusal_output(
                input_name, facts_line))
            return delivered if delivered != 0 else 3

    decision, masked = _assemble_exit_decision(output)
    _supply_exit_decision(output, decision, masked)
    if subcommand == "validate":
        text = render_validate(output)
    else:
        text = render_summary(output)
    reason_text = "; ".join(decision.reason_classes)
    text += closing_line(decision.code, reason_text) + "\n"
    delivered = _deliver_stdout(text)
    if delivered != 0:
        return delivered
    return decision.code


def _deliver_stderr_run(text):
    """Deliver a refusal or not read surface on standard error."""
    if _write_stderr(text):
        return 0
    return 2
