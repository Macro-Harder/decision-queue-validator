# Corpus manifest: decision queue corpus

Corpus home: tests/fixtures/decision_queue_corpus/. This manifest is the only source for every derived value it records. Labels: pinned means stated in a named design source; derived means derived by hand from the pinned snapshot under the brief rules, with the derivation shown in the design record named; open means not stated, under the gate named. Derivations for the guarded values stand at design/research/step-13/derivations.md in the design repo, and the pinning act stands at design/research/step-13/pinning-act.md.

## Corpus structure splits (in-line header)

Pin record (derivation reference: the pinning act). Fixture R1 is a real extract of the live source at ~/workspace/build-flow-expansion/DECISION-QUEUE.md, lines 1 to 4,554, taken as the first 4,554 line feed terminated lines with terminators included. Computed SHA-256: 777478d0791d88f6947d95117b49cae93b8466cd979c61eba94ace225bc2a006. Computed byte size: 379,560 bytes. Comparison against register S10-E-03: match on both values. Protocol form: single-read. Pinning date: 2026-11-12. Append only verdict: append only, drawn from the hash comparison and the tail of the same read (tail: 32 lines, 17,799 bytes, eight added entries DQ-157 to DQ-164 standing after the prefix).

Canonical split for R1 (derivation reference: derivations.md section (a); label derived, unit headed entries): Open 0, Presented 0, Parked 0, Ruled 61, Settled 73, Settled in part 0, Closed as decided 18, Conditional 3; Ambiguous 2 as the reporting state; unparsed row 0. Sum check: 155 canonical rows plus 2 Ambiguous plus 0 unparsed equals 157 headed entries. Recomputed at Step 19 under the R-04 fix: an element stating what remains open now stands in element order, and ten R1 entries move on it (nine Settled or Ruled entries to Closed as decided, one Settled entry to Conditional); the Step 19 fix register carries the movement in full.

Status occurrence total for R1 (derivation reference: derivations.md section (c); label derived, unit occurrences): 238. Appendix accounting: variant rows sum to 2, line start rows sum to 233, embedded rows sum to 3; 2 plus 233 plus 3 equals 238.

Finding totals (derivation reference: derivations.md section (b); label derived): R1: Error 0, Warning 14, Note 6, total 20. Per rule for R1: check 1: none; check 2: none; check 3: 11 Warnings; check 4: 3 Notes; check 5: none; check 6: 2 Warnings; check 7: none; check 8: 1 Warning, 3 Notes; check 9: none; check 10: none. R6: Error 0, Warning 2, Note 0, total 2, with the dependent check 8 count at 0. R9: Error 0, Warning 2, Note 0, total 2. R2: Error 0, Warning 12, Note 6, total 18 (derived by difference from the R1 totals, under the gate discharged at the R2 entry below; derivation reference: design/research/step-13/span-comparison.md). Per rule for R2: check 1: none; check 2: none; check 3: 11 Warnings; check 4: 3 Notes; check 5: none; check 6: none; check 7: none; check 8: 1 Warning, 3 Notes; check 9: none; check 10: none. The R1 and R2 totals stand recomputed at Step 19 under the R-04 fix, as the canonical split note above records.

Fixture R8 exit (derivation reference: derivations.md section (d); label derived): check 8 citation count for the R8 span 0; exit code 0.

R1 census classes beyond the Banked head class (derivation reference: derivations.md section (e); label derived): a non header status value on a decided entry 76; a missing options block on a decided entry 93; a missing ruling date on a decided entry 146; non numeric filing in the Ruled Record 6; a missing Owner line in a tail form entry 8; a decided entry missing its question label or Cost field 1 (DQ-137); open form fields carried by a decided entry inside the Ruled Record 1 (DQ-034); unclassified status values 0. The Banked head class stands at 103, pinned.

Member entry ids for the missing options block class on a decided entry, 93 entries, in file order, with the unnumbered R-7 entry carried under its literal heading text: DQ-050, DQ-051, DQ-052, DQ-053, DQ-054, DQ-056, DQ-057, DQ-058, DQ-059, DQ-060,
DQ-061, DQ-062, DQ-063, DQ-064, DQ-065, DQ-066, DQ-067, DQ-068, DQ-069, DQ-070,
DQ-071, DQ-072, DQ-073, DQ-074, DQ-075, DQ-076, DQ-077, DQ-078, DQ-079, DQ-080,
DQ-081, DQ-082, DQ-083, DQ-084, DQ-085, DQ-086, DQ-088, DQ-089, DQ-092, DQ-093,
DQ-098, DQ-105, DQ-108, DQ-109, DQ-110, DQ-111, DQ-112, DQ-115, DQ-116, DQ-117,
DQ-118, DQ-119, DQ-120, DQ-121, DQ-123, DQ-124, R-7 closure conflict, DQ-002, DQ-001, DQ-003,
DQ-004, DQ-005, DQ-006, DQ-007, DQ-008, DQ-010, DQ-012, DQ-013, DQ-014, DQ-015,
DQ-016, DQ-017, DQ-033, DQ-138, DQ-139, DQ-140, DQ-141, DQ-142, DQ-143, DQ-144,
DQ-145, DQ-146, DQ-147, DQ-148, DQ-137, DQ-149, DQ-150, DQ-151, DQ-152, DQ-153,
DQ-154, DQ-155, DQ-156.

Member entry ids for the missing ruling date class on a decided entry, 146 entries, in file order: DQ-035, DQ-036, DQ-037, DQ-038, DQ-039, DQ-040, DQ-041, DQ-042, DQ-043, DQ-044,
DQ-045, DQ-046, DQ-047, DQ-048, DQ-049, DQ-050, DQ-051, DQ-052, DQ-053, DQ-054,
DQ-055, DQ-056, DQ-057, DQ-058, DQ-059, DQ-060, DQ-061, DQ-062, DQ-063, DQ-064,
DQ-065, DQ-066, DQ-067, DQ-068, DQ-069, DQ-070, DQ-071, DQ-072, DQ-073, DQ-074,
DQ-075, DQ-076, DQ-077, DQ-078, DQ-079, DQ-080, DQ-081, DQ-082, DQ-083, DQ-084,
DQ-085, DQ-086, DQ-088, DQ-089, DQ-090, DQ-091, DQ-092, DQ-093, DQ-094, DQ-095,
DQ-096, DQ-097, DQ-098, DQ-099, DQ-100, DQ-101, DQ-102, DQ-103, DQ-104, DQ-105,
DQ-107, DQ-108, DQ-109, DQ-110, DQ-111, DQ-112, DQ-113, DQ-114, DQ-115, DQ-116,
DQ-117, DQ-118, DQ-119, DQ-120, DQ-121, DQ-122, DQ-123, DQ-124, DQ-125, DQ-126,
DQ-127, DQ-128, DQ-129, DQ-130, DQ-002, DQ-001, DQ-003, DQ-004, DQ-005, DQ-006,
DQ-007, DQ-008, DQ-009, DQ-010, DQ-011, DQ-012, DQ-013, DQ-014, DQ-015, DQ-016,
DQ-018, DQ-017, DQ-019, DQ-020, DQ-021, DQ-022, DQ-023, DQ-024, DQ-025, DQ-027,
DQ-026, DQ-028, DQ-029, DQ-030, DQ-031, DQ-032, DQ-033, DQ-034, DQ-138, DQ-139,
DQ-140, DQ-141, DQ-142, DQ-143, DQ-144, DQ-145, DQ-146, DQ-147, DQ-148, DQ-131,
DQ-132, DQ-133, DQ-134, DQ-135, DQ-136, DQ-137.

## Fixture entries

### R1

- Fixture id: R1. Kind: real extract.
- Provenance: real extract of the live decision queue file, taken under the single read protocol at Step 13 from the source named below.
- Materialisation rule: source path ~/workspace/build-flow-expansion/DECISION-QUEUE.md, source line range lines 1 to 4,554, taken as the first 4,554 line feed terminated lines with terminators included, copied byte for byte with no line ending conversion and no edit.
- File path: tests/fixtures/decision_queue_corpus/R1.md.
- SHA-256: 777478d0791d88f6947d95117b49cae93b8466cd979c61eba94ace225bc2a006. Byte size: 379,560. Line count: 4,554.
- Expected counts: lines 4,554 (pinned); DQ entries 156 (pinned); headed entries 157 (pinned); duplicates 0 (pinned); gaps 0 (pinned); line start Status lines 233 (pinned); distinct status phrasings 29 (pinned); Banked heads carrying decision evidence 103 (pinned); H4 sub headings 113 (pinned); canonical counts as the header split (derived for the four decided states, pinned for Open 0, Presented 0, Parked 0, Ambiguous 2, Conditional 2); Status occurrence total 238 (derived).
- Expected findings: Error 0, Warning 3, Note 5 (derived; per rule in the header).
- Expected exit code: 4 (pinned, pin 9).

### R2

- Fixture id: R2. Kind: real snapshot.
- Provenance: the earlier staging copy of the same queue, the staging drift pair to R1, at the source named below, pinned as a snapshot copy with no edits.
- Materialisation rule: source path ~/workspace/github-staging/build-flow-design/expansion/DECISION-QUEUE.md, the whole file, copied byte for byte. R2 is never constructed by editing R1. At construction the staging copy was verified to agree with R1 line for line over all of its 4,542 lines, standing as the first 4,542 lines of the pinned snapshot, with the difference standing only in the 12 tail lines of R1 that it lacks.
- File path: tests/fixtures/decision_queue_corpus/R2.md.
- SHA-256: 84f74624b785253b9f77e45fe0cbba40bcb6122cd27002f997bfe470b04e9682. Byte size: 376,137. Line count: 4,542.
- Expected counts: lines 4,542 (pinned); DQ entries 155 (pinned); headed entries 156 (derived); line start Status lines 233 (pinned); distinct status phrasings 29 (derived); H4 sub headings 113 (derived); duplicates 0, gaps 0 over DQ-001 to DQ-155 (derived). Canonical counts (derived by difference from the R1 derivation, under the gate discharged below; unit headed entries): Open 0, Presented 0, Parked 0, Ruled 60, Settled 73, Settled in part 0, Closed as decided 18, Conditional 3; Ambiguous 2 as the reporting state; unparsed row 0. Recomputed at Step 19 under the R-04 fix on the same difference basis (DQ-156 stands in none of the moved entries). Gate, discharged: the values under the canonical split and the finding totals were derived by difference from the R1 derivation only after a byte level span comparison of the two pinned files stood performed and recorded as a precondition, with every differing span accounted for by one of the three named differences below. The span comparison stands at design/research/step-13/span-comparison.md, performed by Audit test seat 1, an agent other than the seat that derived the R1 values: one differing span, R1 bytes 376,137 to 379,559 at lines 4,543 to 4,554, with no counterpart in R2, accounted for in full by the three named differences, and no further span.
- Expected findings: Error 0, Warning 12, Note 6, total 18 (derived by difference from the R1 totals under the gate discharged above; derivation reference: design/research/step-13/span-comparison.md, with the starting figures at derivations.md section (b), recomputed at Step 19 under the R-04 fix). Per rule: check 1: none; check 2: none; check 3: 11 Warnings; check 4: 3 Notes; check 5: none; check 6: none; check 7: none; check 8: 1 Warning, 3 Notes; check 9: none; check 10: none. The three named differences stand as criterion 4 states them: DQ-156 absent; DQ-155 Closed as decided on its shorter span; the label reattachment Warnings absent, at minus 2 Warnings from the R1 check 6 total, which is the one adjustment the difference makes to the R1 finding totals.
- Expected exit code: 4 (pinned, criterion 4).

### R3

- Fixture id: R3. Kind: real extract.
- Provenance: real extract of the pinned snapshot R1, the DQ-050 entry span.
- Materialisation rule: source path, the pinned snapshot R1; source line range lines 554 to 574 of the snapshot, the entry heading line to the last content line of the span, copied byte for byte.
- File path: tests/fixtures/decision_queue_corpus/R3.md.
- SHA-256: b97ab531a93b68365cc56cef8750b9be351671e2c436a1150dc302fa8a9f24cd. Byte size: 2,200. Line count: 21.
- Expected counts: headed entries 1 (pinned); line start Status lines 1 (pinned); H4 sub headings 1 (pinned); state Settled with decider label settled under DQ-143 (pinned).
- Expected findings: 1 Warning under check 8, for the citation of DQ-143, which has no heading inside the fixture (derived from criterion 4 as ruled at W-06).
- Expected exit code: 1 (pinned, criterion 4).

### R4

- Fixture id: R4. Kind: real extract.
- Provenance: real extract of the pinned snapshot R1, the DQ-087 and DQ-106 entry spans, the BQ-2 pair.
- Materialisation rule: source path, the pinned snapshot R1; source line ranges lines 1570 to 1618 and lines 2223 to 2267 of the snapshot, concatenated in file order with one blank separator line between the spans, each span copied byte for byte.
- File path: tests/fixtures/decision_queue_corpus/R4.md.
- SHA-256: 0a1abfab20182b93a81cbbd1b28c393c84cfd752dcb70afa989b0082dfcb81ce. Byte size: 9,951. Line count: 95.
- Expected counts: headed entries 2 (pinned); line start Status lines 6 (derived); both entries Ambiguous with sub label Conflict, both elements of each quoted, neither counted as closed in any total (pinned, pin 16).
- Expected findings: 1 Warning under check 1, one gap finding for the missing set 88 to 105, eighteen integers in one run (derived under W-09). No Error from the Ambiguous cause (pinned, section 3.3 of the brief).
- Expected exit code: 4 (pinned, pin 16 and pin 9).

### R5

- Fixture id: R5. Kind: real extract.
- Provenance: real extract of the pinned snapshot R1, the tail range DQ-149 to the end of the snapshot.
- Materialisation rule: source path, the pinned snapshot R1; source line range lines 4470 to 4554 of the snapshot, copied byte for byte.
- File path: tests/fixtures/decision_queue_corpus/R5.md.
- SHA-256: fef88ad94e5a5e660022ec39876603410ef356fc7370aab13e0bb5fe407cc636. Byte size: 14,206. Line count: 85.
- Expected counts: headed entries 8 (pinned); DQ entries 8 (pinned); line start Status lines 4 (derived); states Ruled 5 (DQ-149 to DQ-152 and DQ-156, by its heading borne ruling under pin 3) and Closed as decided 3 (DQ-153 to DQ-155) (derived).
- Expected findings: 2 Warnings under check 6, one per reattached paragraph, for the DQ-155 fifth and sixth additions (derived under W-09, class pinned at criterion 4).
- Expected exit code: 1 (pinned, criterion 4).

### R6

- Fixture id: R6. Kind: real extract.
- Provenance: real extract of the pinned snapshot R1, the DQ-002, DQ-016, and DQ-147 entry spans, one entry per evidence form.
- Materialisation rule: source path, the pinned snapshot R1; source line ranges lines 3005 to 3030, lines 3435 to 3464, and lines 4229 to 4235 of the snapshot, concatenated in that order with one blank separator line between spans, each span copied byte for byte.
- File path: tests/fixtures/decision_queue_corpus/R6.md.
- SHA-256: 919c8060cd90120feacce4c1071cea7ca4715cbf5b26116939ce7455011c2cf9. Byte size: 6,771. Line count: 65.
- Expected counts: headed entries 3 (pinned); states Ruled 3 (derived); no evidence finding on any of the three entries (pinned, criterion 4).
- Expected findings: Error 0, Warning 2, Note 0, total 2 (derived; derivations.md section (b)). The 2 Warnings are check 1 gap findings over the missing set of 143 integers in two runs, 3 to 15 and 17 to 146. The dependent check 8 count is 0 (derived).
- Expected exit code: 1 (pinned, criterion 4).

### R7

- Fixture id: R7. Kind: real extract.
- Provenance: real extract of the pinned snapshot R1, the six unheaded decision entries DQ-059, DQ-072, DQ-073, DQ-079, DQ-084, and DQ-117.
- Materialisation rule: source path, the pinned snapshot R1; source line ranges lines 794 to 834, lines 1190 to 1212, lines 1214 to 1232, lines 1364 to 1386, lines 1494 to 1516, and lines 2559 to 2575 of the snapshot, concatenated in numeric order with one blank separator line between spans, each span copied byte for byte.
- File path: tests/fixtures/decision_queue_corpus/R7.md.
- SHA-256: 2b7fd0a3f88596a76c17a02badaae5c249344aea19b9e641e8a12e27162e9ce3. Byte size: 16,842. Line count: 151.
- Expected counts: headed entries 6 (pinned); line start Status lines 6 (derived); states Ruled 4 and Conditional 2 (derived).
- Expected findings: 1 Warning under check 1, one gap finding for the missing set of 53 integers in one run, and 2 Notes for conditional closure recorded, one per Conditional entry (derived).
- Expected exit code: 4 (pinned, criterion 4).

### R8

- Fixture id: R8. Kind: real extract.
- Provenance: real extract of the pinned snapshot R1, the DQ-130 entry span followed by the three file level note sections after it.
- Materialisation rule: source path, the pinned snapshot R1; source line range lines 2917 to 2974 of the snapshot, one contiguous range, copied byte for byte.
- File path: tests/fixtures/decision_queue_corpus/R8.md.
- SHA-256: 27079f6785fa1dd292a50957758e6c54f3588ae412f8a5b611558b2b3582146a. Byte size: 8,741. Line count: 58.
- Expected counts: headed entries 1 (pinned); orphan note segments 3 (pinned); unassigned lines 0 and double assigned lines 0 (pinned); state of DQ-130 Settled (derived). The amendment governing claim is reported as a claim attached to its note segment and is never applied (pinned, criterion 4).
- Expected findings: none (derived; derivations.md section (d)). Check 8 citation count for the R8 span: 0 (derived).
- Expected exit code: 0 (derived; derivations.md section (d)).

### R9

- Fixture id: R9. Kind: real extract.
- Provenance: real extract of the pinned snapshot R1, the DQ-099 entry span including its Implementation addition after its closing Status line.
- Materialisation rule: source path, the pinned snapshot R1; source line range lines 1981 to 2014 of the snapshot, copied byte for byte.
- File path: tests/fixtures/decision_queue_corpus/R9.md.
- SHA-256: b6f212f92c9f0a6aff090a9a19031263246ffa6084eb16149d1d2ac10e8c9da0. Byte size: 3,569. Line count: 34.
- Expected counts: headed entries 1 (pinned); state Settled (pinned, criterion 4).
- Expected findings: Error 0, Warning 2, Note 0, total 2 (derived; derivations.md section (b)). Both Warnings stand under check 8, for DQ-129 and for DQ-002, cited with no heading inside the fixture.
- Expected exit code: 1 (pinned, criterion 4).

### S1

- Fixture id: S1. Kind: synthetic, marked synthetic in the corpus itself by a comment line at the head of the file.
- Provenance: synthetic fixture, the duplicate number fixture modelled on the DQ-142 collision recorded in the companion traces.
- Materialisation rule: construction rule, two short synthetic entries in the Ruled Record form, both headed DQ-142 with different titles and different rulings, each carrying a Status line, a Ruled by line, a Ruling text line, a question paragraph, a Ruling outcome line, and a landing line; neither entry cites any other DQ number.
- File path: tests/fixtures/decision_queue_corpus/S1.md.
- SHA-256: a31228199f228ad31256bc463a112b4cb6880c68a092a69b8d32a5f1b6a8f479. Byte size: 809. Line count: 29.
- Expected counts: headed entries 2 (pinned); states Ruled 2 (pinned).
- Expected findings: 1 Error under check 1, duplicate number naming both heading lines (pinned).
- Expected exit code: 1 (pinned, criterion 5).

### S2

- Fixture id: S2. Kind: real extract standing as a synthetic family fixture in the Grill corpus list; its construction is mechanical extraction, and it carries no synthetic marker because its bytes are snapshot bytes.
- Provenance: the entry spans of DQ-035, DQ-036, and DQ-038 from the pinned snapshot R1, with DQ-037 omitted and no other change.
- Materialisation rule: source path, the pinned snapshot R1; source line ranges lines 34 to 60, lines 62 to 90, and lines 128 to 164 of the snapshot, concatenated in that order with one blank separator line between spans, each span copied byte for byte.
- File path: tests/fixtures/decision_queue_corpus/S2.md.
- SHA-256: d642fef478dfc2fb70cf5d7ebdab3cf647a7a194ece757ce6f2ddf4a71afd787. Byte size: 10,833. Line count: 95.
- Expected counts: headed entries 3 (pinned); missing set exactly {37} (pinned); states Ruled 2 (DQ-035, DQ-036) and Settled 1 (DQ-038) (derived).
- Expected findings: 1 Warning under check 1, one gap finding naming the missing set {37} (pinned).
- Expected exit code: 1 (pinned, criterion 5).

### S3a

- Fixture id: S3a. Kind: synthetic, marked synthetic in the corpus itself.
- Provenance: synthetic fixture, the header defined but unattested value case.
- Materialisation rule: construction rule, one synthetic open form entry headed DQ-001 with all open fields present, whose only Status line reads Status: Parked with trigger, plus a reopening trigger line under the label Reopening trigger:, the label ruled at brief section 3.7 (S5-A-19) and recorded here as a brief ruled construction choice.
- File path: tests/fixtures/decision_queue_corpus/S3a.md.
- SHA-256: 8dd6a0f7527f5b86773e6a933e21b70e3a43184acc59e7d65755ccd04bdbb6bd. Byte size: 654. Line count: 23.
- Expected counts: Parked 1 (pinned).
- Expected findings: none (pinned).
- Expected exit code: 0 (pinned, criterion 5).

### S3b

- Fixture id: S3b. Kind: synthetic, marked synthetic in the corpus itself.
- Provenance: synthetic fixture, the wholly invented value case, pin 2 shape A.
- Materialisation rule: construction rule, one synthetic open form entry headed DQ-001 whose only Status line reads Status: Deferred, with every check 9 open field present (question, options, cost of deciding late, and what it blocks), so check 9 does not fire on it, and no decision evidence anywhere in the entry. Field completeness is recorded here as the brief requires.
- File path: tests/fixtures/decision_queue_corpus/S3b.md.
- SHA-256: 3469c48eb7014c44ed69fa50af0534d439e3ad5aacea82a6a4298d27a8836985. Byte size: 583. Line count: 21.
- Expected counts: Open 1, by the stipulated exception row of pin 2 (pinned).
- Expected findings: no finding; the value stands as a census Note, unclassified, with its entry named (pinned, pin 2 shape A).
- Expected exit code: 0 (pinned, pin 2 shape A).

### S3c

- Fixture id: S3c. Kind: synthetic, marked synthetic in the corpus itself.
- Provenance: synthetic fixture, the Presented assignment case, in the S3a shape.
- Materialisation rule: construction rule, one synthetic open form entry headed DQ-001 with all open fields present, whose only Status line reads Status: Presented, with no decision evidence.
- File path: tests/fixtures/decision_queue_corpus/S3c.md.
- SHA-256: c72f9480ebf288a11dc61f3ec3c3af622132951fa12becbda6fa0274ad6f1ac2. Byte size: 544. Line count: 21.
- Expected counts: Presented 1 (pinned).
- Expected findings: none (pinned).
- Expected exit code: 0 (pinned, brief section 3.4).

### S4

- Fixture id: S4. Kind: synthetic, built from a real extract by named whole line deletions; it carries no synthetic marker because the brief construction for S4 is deletion from snapshot bytes, and its deletions are recorded here.
- Provenance: the DQ-002 span of the pinned snapshot R1, with four whole lines deleted mechanically.
- Materialisation rule: source path, the pinned snapshot R1; source line range lines 3005 to 3030; deletions, the Ruled by line (source line 3009), the Ruling text line (source line 3013), the Ruling outcome line (source line 3024), and the landing label line (source line 3026). Nothing else is altered.
- File path: tests/fixtures/decision_queue_corpus/S4.md.
- SHA-256: 39c201864d80ada57f70347cc773daf0aeebd33e739139ca6db4acae4e9e8da1. Byte size: 1,141. Line count: 22.
- Expected counts: headed entries 1 (pinned); state Ruled with decider not recorded (pinned).
- Expected findings: 2 Errors and 2 Warnings under check 5, across the four independent presence tests: no decider (Error), no ruling text (Error), no outcome (Warning, pin 8), no landing record (Warning) (pinned, criterion 5).
- Expected exit code: 1 (pinned, criterion 5).

### S4b

- Fixture id: S4b. Kind: synthetic, built from a real extract by a named whole line deletion, on the same terms as S4.
- Provenance: the DQ-002 span of the pinned snapshot R1, with one whole line deleted mechanically.
- Materialisation rule: source path, the pinned snapshot R1; source line range lines 3005 to 3030; deletion, the landing label line only (source line 3026). Nothing else is altered.
- File path: tests/fixtures/decision_queue_corpus/S4b.md.
- SHA-256: c7a1ef76ea6caf3ab7b5a38f4301a45ba7ada9d3ce226e3614b95e21066770c9. Byte size: 1,670. Line count: 25.
- Expected counts: headed entries 1 (pinned); state Ruled, decider label Ruled by Captain JP (pinned).
- Expected findings: 1 Warning under check 5, no landing record (pinned).
- Expected exit code: 1 (pinned, criterion 5).

### S5

- Fixture id: S5. Kind: synthetic, marked synthetic in the corpus itself.
- Provenance: synthetic fixture, the genuinely open entry, the complete open entry template of the plan construction templates.
- Materialisation rule: construction rule, one synthetic open form entry headed DQ-001 with the full open field set (question, options with at least two options, cost of deciding late, what it blocks naming exactly one blocked item, ordering reason), one Status line reading Status: Banked, and no decision block in any marking form.
- File path: tests/fixtures/decision_queue_corpus/S5.md.
- SHA-256: bc151fed41d96abbad112aa64c409e8ec8689350e7a67c199efcd0ad1268d149. Byte size: 546. Line count: 21.
- Expected counts: Open 1 (pinned); waiting 1 (pinned); blocking 1 (pinned).
- Expected findings: none (pinned). The CA-3 banner is absent in both outputs on this fixture (pinned, pin 9 row of the plan mapping).
- Expected exit code: 0 (pinned, criterion 5).

### S5b

- Fixture id: S5b. Kind: synthetic, marked synthetic in the corpus itself.
- Provenance: synthetic fixture, the firing side of check 9, built on the complete open entry pair template with its delta.
- Materialisation rule: construction rule, two synthetic open form entries: DQ-901 missing its question field, with options, cost of deciding late, and blocks fields present; DQ-902 with its question present and its options, cost of deciding late, and blocks fields missing. Each carries one Status line reading Status: Banked and no decision evidence.
- File path: tests/fixtures/decision_queue_corpus/S5b.md.
- SHA-256: d3184c8e70fc7799932b8ac467eadba5a38e5a266cde05bed3a7493abaa2dd94. Byte size: 667. Line count: 31.
- Expected counts: Open 2 (pinned).
- Expected findings: 4 Warnings under check 9, one per missing field: 1 on DQ-901 and 3 on DQ-902 (pinned, brief section 3.4).
- Expected exit code: 1 (pinned, criterion 5).

### S6

- Fixture id: S6. Kind: synthetic, marked synthetic in the corpus itself. This one file holds the two synthetic entries S6a and S6b, as brief section 3.4 constructs fixture S6.
- Provenance: synthetic fixture, the parked pair.
- Materialisation rule: construction rule, S6a is the entry headed DQ-001, marked parked in words with a named reopening trigger recorded under the label Reopening trigger:; S6b is the entry headed DQ-002, marked parked in words with no trigger named anywhere in the entry. Numbers are consecutive, so no gap finding arises.
- File path: tests/fixtures/decision_queue_corpus/S6.md.
- SHA-256: 096af8bc31516af3a17ca0ae88943c5551dd045e9d70b79e099c2ecee93f8531. Byte size: 1,086. Line count: 43.
- Expected counts: Parked 2 (pinned, brief section 3.4).
- Expected findings: 1 Error under check 10, on S6b only (pinned, pin 7).
- Expected exit code: 1 (pinned, brief section 3.4).

### S7a

- Fixture id: S7a. Kind: synthetic. The file is empty, so no synthetic marker can stand inside it; its kind is recorded here.
- Provenance: synthetic fixture, the empty file case.
- Materialisation rule: construction rule, an empty file of zero bytes.
- File path: tests/fixtures/decision_queue_corpus/S7a.md.
- SHA-256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855. Byte size: 0. Line count: 0.
- Expected counts: no entry report (pinned).
- Expected findings: the file level result, not an entry findings list (pinned).
- Expected exit code: 3 (pinned, criterion 5).

### S7b

- Fixture id: S7b. Kind: synthetic in the Grill corpus list, materialised as a real extract of the snapshot header, so its bytes are snapshot bytes and carry no synthetic marker.
- Provenance: the queue header of the pinned snapshot R1, with no entries.
- Materialisation rule: source path, the pinned snapshot R1; source line range lines 1 to 30, copied byte for byte.
- File path: tests/fixtures/decision_queue_corpus/S7b.md.
- SHA-256: db273e88612ee2ac8a0129fb8e88a764f2b211817274c3d0d980783b6415ed74. Byte size: 1,887. Line count: 30.
- Expected counts: no entry report (pinned); no entry heading present (pinned).
- Expected findings: the file level result for the header only case (pinned).
- Expected exit code: 3 (pinned, criterion 5).

### S7c

- Fixture id: S7c. Kind: synthetic. The file holds one heading line and nothing after it, so no marker line can stand inside it without breaking its construction; its heading title names it as the synthetic lone heading fixture, and its kind is recorded here.
- Provenance: synthetic fixture, the lone entry heading with no body.
- Materialisation rule: construction rule, one H3 entry heading line, headed DQ-901 with a synthetic title, and no body line at all.
- File path: tests/fixtures/decision_queue_corpus/S7c.md.
- SHA-256: 541504d7b9baa7683899cc7fc3955e782926fcb874170c250bf8c8a6e1146bd7. Byte size: 43. Line count: 1.
- Expected counts: headed entries 1 (pinned); unparsed entries 1, in its own reconciliation row outside the canonical table (pinned, pin 12).
- Expected findings: 1 Error, the unparsed entry finding (pinned, group 9 ruling of the brief).
- Expected exit code: 4 (pinned, pin 12).

### S8

- Fixture id: S8. Kind: synthetic, marked synthetic in the corpus itself.
- Provenance: synthetic fixture, the post heading addition, isolated.
- Materialisation rule: construction rule, two synthetic open form entries headed DQ-901 and DQ-902 in that order, each with the full open field set and no decision block inside its positional span; after the DQ-902 body stands one further paragraph labelled as an addition to DQ-901, carrying DQ-901 decision in the unheaded labelled paragraph form, naming Captain JP as decider and closing that entry in words.
- File path: tests/fixtures/decision_queue_corpus/S8.md.
- SHA-256: 18d8cfb3b75a130aa0ed6272e1762e60b80cfe1d0594a5187d2fdefdd5a8cd75. Byte size: 1,164. Line count: 43.
- Expected counts: headed entries 2 (pinned); DQ-901 Ruled by its reattached addition (pinned); DQ-902 Open and uncontaminated (pinned).
- Expected findings: 1 Warning under check 6, the label reattachment finding, with the DQ-901 span flagged non contiguous (pinned).
- Expected exit code: 1 (pinned, criterion 5).

### S10

- Fixture id: S10. Kind: synthetic, marked synthetic in the corpus itself.
- Provenance: synthetic fixture, the structured non queue file case.
- Materialisation rule: construction rule, a short structured Markdown document with headings, lists, and prose, and no DQ entry heading and no queue header.
- File path: tests/fixtures/decision_queue_corpus/S10.md.
- SHA-256: 7c42064fcd152dd9b42e1595a7952e20ac933f8bc1ded7c46fc0cff94f137ea9. Byte size: 241. Line count: 15.
- Expected counts: no entry report (pinned).
- Expected findings: the file level result, stating what recognisable queue structure is missing (pinned, brief section 3.4).
- Expected exit code: 3 (pinned, criterion 5).

### S11

- Fixture id: S11. Kind: synthetic, marked synthetic in the corpus itself.
- Provenance: synthetic fixture, the clean Settled in part entry, the Manager settlement form of the one part state, built on the part state single entry template.
- Materialisation rule: construction rule, one synthetic open form entry headed DQ-901, citation free, with a Manager part settlement block in the H4 sub part form naming a remainder in a Remainder line, the settled part carrying the check 5 evidence forms in full (a Settled by decider form, a Ruling text form, a Decision outcome form, and a Landing record), and no later closing block.
- File path: tests/fixtures/decision_queue_corpus/S11.md.
- SHA-256: 4985673bc7b96b16a703c337446be93c14cf24ecda06f15d2085558d9f75fc2d. Byte size: 1,143. Line count: 35.
- Expected counts: Settled in part 1, with the remainder text carried verbatim on its row and no closed count (pinned, brief section 3.7 at S5-A-21).
- Expected findings: none (pinned).
- Expected exit code: 0 (pinned, criterion 5).

### S12

- Fixture id: S12. Kind: synthetic, marked synthetic in the corpus itself.
- Provenance: synthetic fixture, the part ruling by Captain JP form of the one part state, built on the S11 construction with its delta.
- Materialisation rule: construction rule, the S11 construction with one change: its single entry ends on a part ruling block by Captain JP in the H4 sub part form naming a remainder in a Remainder line, with the decision evidence forms for the settled part present in full (a Ruled by decider form, a Ruling text form, a Ruling outcome form, and a landing record), and no later closing block.
- File path: tests/fixtures/decision_queue_corpus/S12.md.
- SHA-256: ef47d279fa223aec35e806cf4a41fb3468b1a3a899047445cf82a1414812ac2d. Byte size: 1,037. Line count: 35.
- Expected counts: Settled in part 1, with the decider label Ruled by Captain JP on its row, the remainder text carried verbatim, and no closed count (pinned, pin 1).
- Expected findings: none (pinned).
- Expected exit code: 0 (pinned, criterion 5).

### S13

- Fixture id: S13. Kind: synthetic, marked synthetic in the corpus itself.
- Provenance: synthetic fixture, the combined exit 4 fixture.
- Materialisation rule: construction rule, one entry headed DQ-901 in the pin 16 sequence shape (a remainder Status line followed by a closing ruling block), reporting as Ambiguous, and one lone entry heading headed DQ-902 with no body, carried as an unparsed entry, in one file.
- File path: tests/fixtures/decision_queue_corpus/S13.md.
- SHA-256: 5ed441b096e8c7c607b42d9d7b5f71d1543a5ed07cef85834eacd7aad5071695. Byte size: 869. Line count: 31.
- Expected counts: Ambiguous 1 (pinned); unparsed entries 1 (pinned).
- Expected findings: 1 Error, the unparsed entry finding (pinned).
- Expected exit code: 4, with both reason classes named in the Exit decision and in the closing line, the pin 9 class and the pin 12 class, and the CA-3 banner present in both outputs (pinned, brief section 3.4).

### S14

- Fixture id: S14. Kind: synthetic, marked synthetic in the corpus itself.
- Provenance: synthetic fixture, the check 8 recognition fixture, its construction pinned in full at brief section 3.4.
- Materialisation rule: construction rule, exactly two entries headed DQ-901 and DQ-902, consecutive numbers. DQ-901 is effectively open: its only status bearing element is a line start Status line with the value Banked, it carries no decision evidence, and every check 9 open field is present. DQ-902 carries a line start Status line with the value Banked as its only status element, no decision evidence, and every check 9 open field present; its body also carries a bare entry token mention, the token DQ-999, in none of the citation frames of brief section 5.3, and one state claim in the claim form of brief section 5.3 about DQ-901, stating a state DQ-901 does not derive.
- File path: tests/fixtures/decision_queue_corpus/S14.md.
- SHA-256: 96fdf20b81b698fc8ae39cbc068c425c6ae36aa645795093058063f33a2c660e. Byte size: 1,092. Line count: 45.
- Expected counts: Open 2 (pinned, brief section 3.4).
- Expected findings: 1 Note under check 8, for the state claim, reported as a claim; no citation Warning for the mere mention (pinned, brief section 3.4).
- Expected exit code: 0 (pinned, brief section 3.4).

### S15

- Fixture id: S15. Kind: synthetic, marked synthetic in the corpus itself.
- Provenance: synthetic fixture, the check 2 near marker fixture, built on the single open entry template.
- Materialisation rule: construction rule, one entry headed DQ-901 whose only status bearing element is a line start Status line with the value Banked, with no decision evidence and every check 9 open field present, and one near marker line in the first near form of brief section 5.3, the marker word in lower case followed by a colon.
- File path: tests/fixtures/decision_queue_corpus/S15.md.
- SHA-256: 3d61c1372372567dd3ab6217ab2ce90f6b1d98658ad6a2b48774eeb82fa5df4c. Byte size: 509. Line count: 23.
- Expected counts: Open 1 (pinned).
- Expected findings: 1 Warning under check 2, for the near marker line, and no other finding (pinned, brief section 3.4).
- Expected exit code: 1 (pinned, brief section 3.4).

### S17

- Fixture id: S17. Kind: synthetic, marked synthetic in the corpus itself.
- Provenance: synthetic fixture, the part scope Ambiguous rows fixture.
- Materialisation rule: construction rule, two entries in one file. The first entry, headed DQ-901, ends on a determining element with scope Part, condition None, and no remainder named: a part settlement block in the H4 sub part form that names no remainder, carrying as built a Settled by decider form and a Settlement statement, and no separate ruling text, outcome, or landing form. The second entry, headed DQ-902, ends on a determining element with disposition Banked, scope Part, a named remainder carried verbatim in its block in a Remainder line, and condition None, the catch row shape of brief section 5.4; as built it carries no check 5 evidence forms. Evidence completeness of the construction as built, recorded under OQ-4: the first entry carries the decider and settlement statement forms only, in part; the second entry carries no evidence forms. The expectation below holds in either case, because check 5 does not run on an Ambiguous entry under pin 8.
- File path: tests/fixtures/decision_queue_corpus/S17.md.
- SHA-256: 052fe0694a6599b8120e7393a573a53b6a70612a2e9f1b7106558a34e3874a99. Byte size: 1,446. Line count: 55.
- Expected counts: Ambiguous 2, each with the sub label Single element and the determining element quoted (pinned, brief section 3.4).
- Expected findings: no check 5 finding on either entry at any grade (pinned, pin 8 bound); no other finding (pinned).
- Expected exit code: 4 (pinned, brief section 3.4).

### S18

- Fixture id: S18. Kind: synthetic, marked synthetic in the corpus itself.
- Provenance: synthetic fixture, the check 3 Warning fixture.
- Materialisation rule: construction rule, one entry whose elements are a Status line denoting Ruled, followed by a later Status line denoting Settled as its determining element, with the decision evidence forms of check 5 present in full in its decision block (decider, ruling text, outcome, and landing record), and no Banked head element.
- File path: tests/fixtures/decision_queue_corpus/S18.md.
- SHA-256: aa0032c45d0527c9722e334042fbc0aa44c354b88057e9a455f4369db57d5196. Byte size: 702. Line count: 23.
- Expected counts: Settled 1 (pinned, brief section 3.4).
- Expected findings: 1 Warning under check 3, of the class status elements disagree, and no other finding (pinned, brief section 3.4).
- Expected exit code: 1 (pinned, brief section 3.4).

### S19

- Fixture id: S19. Kind: synthetic, marked synthetic in the corpus itself.
- Provenance: synthetic fixture, the pin 4 block position fixture.
- Materialisation rule: construction rule, one entry carrying an H4 decision block that contains a Status line, where the block segment before the contained Status line carries a disposition statement denoting Ruled, the contained Status line denotes Ruled, and the block segment after the contained Status line carries a disposition statement denoting Settled together with the check 5 evidence forms in full (decider, ruling text, outcome, and landing record).
- File path: tests/fixtures/decision_queue_corpus/S19.md.
- SHA-256: 6498e261a8cbb6961124b06b7a9a49eae6d0cbfd49c4418925c36f4f79b9b4af. Byte size: 865. Line count: 25.
- Expected counts: Settled 1, under the segment position rule of pin 4 (pinned, brief section 3.4).
- Expected findings: 1 Warning under check 3, for the earlier Ruled elements (pinned, brief section 3.4).
- Expected exit code: 1 (pinned, brief section 3.4).

### S20

- Fixture id: S20. Kind: synthetic, marked synthetic in the corpus itself.
- Provenance: synthetic fixture, the pin 2 shape B fixture pinned at plan item 2, Commitment 1.
- Materialisation rule: construction rule, stated in full at plan item 2. Two synthetic entries headed DQ-901 and DQ-902, consecutive numbers. The unclassifiable value in both entries is the same verbatim value, a line start Status line reading Status: To be classified. DQ-901 elements in order: a head Status line Banked, a later Status line Open, and the unclassifiable Status line last, with no closing block. DQ-902 carries decision evidence in a decision block in the H4 sub part form, with a decider form and a ruling text form present, and its only Status line is the unclassifiable Status line, standing as its last element.
- File path: tests/fixtures/decision_queue_corpus/S20.md.
- SHA-256: c9bec911ea677007fe8aac7de317ec7f08d4a748348457cc7e6676b402075e4c. Byte size: 1,014. Line count: 41.
- Expected counts: Ambiguous 2, each with the sub label Single element and the unclassifiable element quoted (pinned, pin 2).
- Expected findings: no finding; one census Note per entry for the unclassifiable value, as a census entry and not as a finding; no Error finding; no check 5 finding (pinned, pin 2 and brief section 3.3).
- Expected exit code: 4 (pinned, pin 2).

### S21

- Fixture id: S21. Kind: synthetic, marked synthetic in the corpus itself.
- Provenance: synthetic fixture, the pin 10 Ambiguous target claim fixture named at plan item 2 under OQ-3, built on the S14 construction template with its delta stated in full in this entry.
- Materialisation rule: construction rule, the S14 template plus this delta, stated in full. The template part: two entries with consecutive headings, each carrying a Banked head Status line and every check 9 open field present. The delta: the first entry, headed DQ-901, stands in the pin 16 sequence shape, carrying in addition a remainder Status line followed by a closing ruling block, so it reports as Ambiguous under the BQ-2 interim rule, Conflict sub label, counted as closed in no total; the second entry, headed DQ-902, carries one state claim in the claim form of brief section 5.3 about DQ-901, stating a state the target does not derive, and no bare token mention stands in this fixture. BQ-2 stays banked: this fixture uses the interim rule reporting only and decides nothing about the remainder.
- File path: tests/fixtures/decision_queue_corpus/S21.md.
- SHA-256: b321ad6ccc364892370a2d0daaf15b1ec63bf0d450b4119acb3bac699a1a4e38. Byte size: 1,385. Line count: 51.
- Expected counts: Ambiguous 1 (DQ-901), Open 1 (DQ-902) (pinned, plan item 2 at OQ-3).
- Expected findings: 1 Note under check 8, the claim reported as a claim with the target Ambiguous status named, with no stale verdict and no agreement verdict; the claiming entry state is unchanged by its claim sentence (pinned, pin 10).
- Expected exit code: 4, from the Ambiguous target itself under pin 9 (pinned, plan item 2 at OQ-3).

## Generated inputs family, recorded by construction rules only

No generated case is a stored fixture, and none stands in this manifest as a stored file. The family has 14 variants in 5 groups, as plan item 6 counts them, and no variant is optional (PF-15).

Group 1, limit breaches, 3 variants. Construction rule: a test generates, at run time, an input breaching one limit each: the byte limit of 2,000,000 bytes; the line limit of 10,000 lines, by 10,001 lines of valid queue shaped lines; and the per line limit of 16,384 characters, by one line over that length. Each variant expects the file level result at exit 3, with the breached limit and its measured value named.

Group 2, terminator edges, 3 variants. Construction rules: exactly 10,000 terminated lines, which counts 10,000 lines and does not breach the line limit; the same input with one further terminator, which counts 10,001 lines, the last of them a final blank line, and breaches; and the lone carriage return variant, constructed in full at plan item 6: six model lines in the stated order, holding one lone carriage return inside a line, two lone carriage returns in one line, a lone carriage return before a carriage return and line feed terminator, a lone carriage return inside a Status value, and a final line ending in a lone carriage return with no terminator; its line count is six, no line splits at any carriage return it holds, and each lone carriage return counts as one character in its line and as no terminator.

Group 3, scale and model doubles, 2 variants. Construction rules: the generated doubled input, made by renumbered duplication of real extracts, run and recorded by its line count, byte count, output length, and run behaviour, and not stored; and the generated parse model test double for the firing side of check 6, a parse model in which one line is assigned to no unit and one line is assigned to two units, handed to validate, expecting the headline Error finding of check 6 naming both lines.

Group 4, generated run conditions, 5 variants. Construction rules: a named output file that is the input file itself; a named output file that is a link resolving to the input; a named output file that is a hard link to the input; a named output path that is a directory; and a run whose standard output is a closed pipe. The first three refuse at exit 2 in the OP-Q1 refusal form; the last two end at exit 2 under brief section 6.2.

Group 5, recovery combination, 1 variant. Construction rule: the combined defects variant, built under the constraints C-1 to C-5 at plan item 6: each defect on its own carrier; the unmatched heading placed so its orphan span contains no line any other defect needs; the near marker line inside an entry span no orphan assignment reaches; the duplicate pair both recognised entry headings; and the gap range read from recognised headings only. The four defects are one duplicate Error under check 1, one gap Warning under check 1, one near marker Warning under check 2, and one unmatched heading Warning under pin 5, all in a single run, at exit 1.

Generated unmatched heading variants under OQ-2, recorded by construction rule: a valid queue file carrying one further heading that matches no entry form, no known file level form, and no sub part form, in three variants, a second H1 heading, an H5 heading, and an H6 heading. Each expects one Warning finding under pin 5, its lines assigned to an orphan segment, and no entry created.

Generated pin 4 coincident case, recorded by construction rule: two status bearing elements in one paragraph, on one line, at different positions within the line. The two elements are ordered by line and then by the position of the value within the line, as pin 4 states.

## Recorded corpus gaps

Bold lead in form: a recorded corpus gap, in the form of brief section 3.4. The form named: the bold lead in form of decision evidence. Where held: only inside R1 and R2 in aggregate. Reason: the form is a named marking form of brief section 5.3, both its instances in the real file are exercised end to end by the acceptance run on R1, and at Low tier the corpus budget is spent on the unfixtured proof paths. Consequence: no isolating fixture for the form stands in this version. No exact occurrence count and no entry location is asserted for the form in this manifest.

Pin 3 isolating coverage: a recorded corpus gap, in the form of brief section 3.4, under OQ-1. The form named: heading borne evidence and the Origin line as element kinds, under pin 3. Where held: inside R1 in aggregate, with R2 as the contrast run in which DQ-156 is absent. Reason: both shapes are exercised end to end on the real file in the acceptance run on R1 and the contrast run separates the heading borne case, and at Low tier the corpus budget is spent on the proof paths the brief names first. Consequence: pin 3 is proved in aggregate only, and no test isolates either kind.
