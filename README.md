# Decision Queue Validator

A small offline command line tool that checks one Markdown decision
queue file for form and internal consistency, and reports what it
finds. It checks the file only. It does not judge whether any ruling
recorded in the file was right, and its reports are advisory: a report
may not be cited as a pass or fail condition for any step, gate, or
release.

## Installing it

The tool runs with Python 3.11 or later and uses only the standard
library. Nothing else is installed and no network access is needed or
used. Copy the `decision_queue_validator` package to a place on your
Python path, or run it from the directory that holds the package.
Each run takes exactly one input file, reads it once, and prints its
output to standard output. The tool never edits its input file and
writes nothing else: no log file and no run record.

## Running it

```
python3 -m decision_queue_validator validate QUEUE.md
python3 -m decision_queue_validator render QUEUE.md
```

Both subcommands read the same file in the same way. They differ only
in the output they print.

- `validate` prints the findings report.
- `render` prints the readable summary of the same file.

## Reading the outputs

Every output opens with the same five head lines:

1. What the run checked, and what it did not check: merits, the truth
   of rulings, landings in other documents, companion file contents,
   and decider authority are not checked.
2. The input name, exactly as you supplied it.
3. The file facts: whether the file is the live file or a pinned
   copy, its line count and byte count, and a short form of its
   digest.
4. The limits in force.
5. The version fields: vocabulary version, output form edition, and
   rule set version.

Every output ends with two lines. The first points at the other
subcommand, which shows the other view of the same file. The last is
the closing exit line. It states the exit code, the reasons for that
code in plain words, and the sentence the code carries: this code is
a findings signal and not a step verdict.

The validate report carries, in order: a compact index of the per
entry findings; the full findings grouped by entry, under a line
stating that findings concern form and internal consistency only and
that no finding judges whether a ruling was right; a rule list
stating, once per rule that fired, what recorded form would clear a
finding of that rule; the entry groups in the order stated below
for the render summary, printing each group that stands in the
file; the counts, with a units key and, where the file carries the
Banked head phrasing, the crosswalk for that phrasing; the census,
with the class rule and the member entries of each class listed
under its row; the reconciliation block; the verbatim appendix of
Status phrasings as written; the residue list of phrasings the tool
could not translate; the Segment claims, where a note segment of
the file carries a claim over named entries, each claim reported
as a claim and not applied to any entry it names; and the figures
described below.

The render summary carries, in order: a line naming its layers and
their order; a marking that names the presentation set, being the
Open group and the Settled in part group for its remainders, with
the reasons the other groups stand outside the set, and a statement
that file order is not presentation order; the entry groups in this
order: Open, Settled in part, Presented, Parked, Conditional,
Ambiguous, Ruled, Settled, Closed as decided, and the unparsed
entries last; the supersession map, where the file carries
recognised displacements, printing each displacement as a chain of
entries; then the counts, with the units key and the crosswalk
where the file carries the Banked head phrasing, the census, the
reconciliation block, the verbatim appendix of Status phrasings as
written, the residue list of phrasings the tool could not
translate, the Segment claims where a note segment carries one,
and the figures.

The figures state how many entries are waiting and how many entries
block other work, each with its unit, entries. The waiting figure
prints with its formula in words beside it. Beside it, as a separate
figure, stands the companion count of entries carrying a standing
remainder whose entry carries a supersession pointer. A limbo
sentence states which classes stand outside both figures, with the
count and the entry identifiers of each class. The fastest item to
clear is reported as not derivable from the file, because the file
does not record it.

Operator text is printed in a visible escaped form where it carries
characters that could break the line structure of an output or write
a control sequence to a screen: a backslash prints doubled, and
newline, carriage return, tab, escape, and other control characters
print as backslash forms. The values in the file itself are never
changed by this. Only their printed form changes.

Running either subcommand twice over the same input produces the
same output and the same exit code. The tool keeps no state between
runs.

## Input

One Markdown decision queue file per run, written in the queue forms
the tool recognises: a queue header, entry headings, Status lines,
and the decision evidence recorded inside entries. The input must be
a regular file. A file with no recognisable queue structure is
refused as a whole, as described under exit code 3 below.

A minimal example of a queue file in those forms:

```
# Decision queue

### DQ-001: A sample open question

Status: Banked
```

Running `validate` on that example reports Warning findings for
DQ-001, because the entry records no question, no options, no cost
of deciding late, and no blocks field. Recording those four fields
on the entry clears the warnings.

Three size limits apply, and a file that breaches one is refused as
a whole:

- 2000000 bytes per file
- 10000 lines per file
- 16384 characters per line

The byte limit is checked from the file size before the file is
read, so an oversize file is refused without being read into the
tool.

## Exit codes

The exit code reports what the run found. It never means that the
queue itself is valid or invalid.

- 0: the run completed and reported no findings, or Note findings
  only.
- 1: the run completed and reported Error or Warning findings.
- 2: the run did not take place. This covers a usage error and an
  input that could not be read, including a missing file and an
  input that is not a regular file, such as a directory. The report
  prints on the standard error channel and states that no run took
  place and no file was read as a queue.
- 3: the file was refused as a whole and no entry report was
  produced. This covers a file that is not valid text, a file that
  breaches one of the size limits (the report names the breached
  limit and the measured value), an empty file, a header only file,
  and a file with no recognisable queue structure. On a render run
  it also covers a supersession map whose printed size stands over
  its limit of 2000000 characters; that report names the limit and
  the capped measured value of 2000001 characters, because counting
  stopped at the cap. The report prints on the standard error
  channel and states that the file was not validated.
- 4: the run completed, but a total in the report is stated under
  undetermined state, because the file contains an entry whose state
  could not be determined from its own elements, or an entry that
  could not be parsed as a whole body. The closing line then also
  names any Error and Warning findings present, with their counts,
  so the code does not hide them. Exit 4 also covers a tool
  inconsistency: the tool own counts did not sum. In that case the
  summary is withheld in full, the report names the fault as a tool
  fault, and its advice is to report the run as a tool fault and not
  edit the queue file on the basis of that run. No finding counts
  print on that report.

## Round close procedure for the Decision-queue Clerk

At the close of every queue round, before the round is recorded as
done, the Clerk runs both subcommands, validate and render, on the
queue file of that round and reads the findings while the entries
of that round are still being written, so a defect in an entry of
the round is found while that entry can still be corrected as part
of the round. This run is advisory. Its findings are advice to the
Clerk and to the round, and nothing more. A queue round is not
barred from closing by any finding the run reports, at any grade.
No exit code the run returns stands as a step verdict, and no exit
code in this procedure decides whether a round, a step, or any
other work passes or closes. In the words the closing exit line
itself carries: the code is a findings signal and not a step
verdict.

## Potential problem causers

- A file that changes while a run is reading it: the run reports on
  the bytes its read returned. It does not detect the change. Run
  the tool again on the settled file for a report on its final
  state.
- An entry whose Status elements disagree, or whose status value
  the tool cannot translate: the entry is reported with its state
  undetermined or its phrasing held as unknown in the residue list.
  It is never forced to a nearest state. Totals that depend on
  entry states are then stated under that condition, and the run
  exits 4.
- A very large web of supersessions: where the printed supersession
  map of a render run would stand over 2000000 characters, the run
  refuses the file at exit 3 rather than printing a shortened map.
  The validate subcommand prints no map and is not refused on this
  ground.
- A heading the tool does not recognise: no entry is raised for it,
  and it is reported as a warning at file level. Restate the heading
  in a recognised form if it was meant to be an entry.
- Text pasted from other tools can carry control characters or
  invisible characters. These print in the escaped form described
  above, which can look odd in a report. The file itself is
  unchanged; the odd spelling is the printed form only.
- The tool reads the file in front of it and nothing else. It does
  not read companion files, does not check that a ruling landed in
  another document, and does not check whether a named decider held
  authority. A clean report says nothing about any of those.

## Licence

Apache 2.0. Copyright: J.P. Picard aka Macro-Harder
