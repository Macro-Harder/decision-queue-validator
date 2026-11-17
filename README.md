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
used. Check your version before the first run:

```
python3 --version
```

If it prints a version earlier than 3.11, use a newer python3 for
this tool.

To run it from the place you unpacked or cloned it, the directory
that holds the package must be your current working directory when
you type the command:

```
cd /the/directory/that/holds/the/package
python3 -m decision_queue_validator validate QUEUE.md
```

Run from any other directory in that form, the command fails before
the tool starts, with a Python error saying no module named
decision_queue_validator. To run it from anywhere else, copy the
package to a directory of your own and name that directory on the
Python path for the run:

```
mkdir -p ~/dqv-lib
cp -r decision_queue_validator ~/dqv-lib/
PYTHONPATH=~/dqv-lib python3 -m decision_queue_validator validate QUEUE.md
```

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
3. The file facts: its line count and byte count, a short form of
   its digest, and a source designation. In this version the
   designation reads live on every readable file, on the live file
   and on any copy of it alike: the designation does not tell you
   whether the file you ran is the live file or a copy of it. The
   digest on the same line identifies the bytes the run actually
   read, so two runs whose digests differ read different bytes,
   whatever their designations say.
4. The limits in force.
5. The version fields: vocabulary version, output form edition, and
   rule set version.

A completed output ends with two lines. The first points at the
other subcommand, which shows the other view of the same file. The
last is the closing exit line. It states the exit code, the reasons
for that code in plain words, and the sentence the code carries:
this code is a findings signal and not a step verdict. Refusal
outputs and usage outputs carry one closing line: the closing exit
line alone, with no line pointing at the other subcommand.

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

Save the example below to a file named QUEUE.md in the directory
you are running from, then run the commands under Running it on
that file. A minimal example of a queue file in those forms:

```
# Decision queue

### DQ-001: A sample open question

Status: Banked

This question is waiting for a decision.
```

The plain paragraph in the example is one of the three counted
elements described below, an unheaded paragraph. It is ordinary
prose recording what the entry is about, and it is not one of the
labelled fields.

Running `validate` on that example reports Warning findings for
DQ-001, because the entry records no question, no options, no cost
of deciding late, and no blocks field. Record those four fields
each as its own labelled paragraph, in this form:

```
Question: Which option should we take?

Options: Option A, Option B

Cost of deciding late: Work stays blocked.

Blocks: DQ-002
```

Recording those four fields in that form, on an entry that also
carries a counted element, clears the warnings.

Banked entries and the census. A Banked head entry is counted in
the census in exactly three evidence groups, assigned in this
order: (1) entries with a later Status line in the body; (2)
entries with a level 4 decision block and no later Status line in
the body; (3) entries with unheaded paragraphs in the body and
neither of the other two. Labelled field paragraphs count toward
none of the three groups. An entry carrying only labelled fields,
or nothing beyond its Status line, is counted in no group. Where
any Banked entry is counted in no group, the evidence groups fail
to foot to the Banked head population, the run is withheld in full
as a tool inconsistency at exit 4, and no findings are reported for
any entry in the file. So a Banked entry must carry at least one
of the three counted elements, in addition to any labelled fields,
if its file is to be reported on at all.

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

### If a run is withheld as a tool fault

If a run is withheld as a tool fault, report the run as a tool
fault, as the report itself advises, and do not edit the queue file
on the basis of that run, because it reported no findings. Where
the failed component named in the report is the Banked head
evidence footing, the file side cause to check is set out under
Input above: check each Banked entry in the file for one of the
three counted elements. An entry that carries none takes this
outcome for the whole file. Adding labelled fields alone does not
change this outcome: a passing Banked entry carries at least one
counted element, a later Status line in the body, a level 4
decision block, or unheaded paragraphs in the body, in addition to
any labelled fields it records, and the four fields are recorded
each as its own labelled paragraph in the form shown under Input.
Shaping the entries in that form is a change to the file form, made
on the strength of this section, not on the strength of the
withheld run.

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
- Redirecting a report onto the file it reports on: Do not redirect
  a report onto the input file own path, as in
  `validate QUEUE.md > QUEUE.md`. The tool never edits its input,
  but the shell empties the target file before the tool runs, so
  the run reads an empty file, refuses it at exit 3, and the
  original contents are gone. Redirect to a different file, or to
  none.

## The tests directory

The tests directory in this repo holds the tool own test suite and
the queue files it runs on. You do not need the tests to run the
tool. To run the suite, from the directory that holds the package,
run: `python3 -m unittest discover -s tests`. The bytecode files
shipped beside the sources are byproducts and carry no part of the
tool.

## Licence

Apache 2.0. Copyright: J.P. Picard aka Macro-Harder
