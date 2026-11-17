Fixture: F-01
Kind: synthetic
Source: synthetic construction rule, two ruled record entries both headed DQ-142 at level 3 with different titles and different rulings, written fresh in the ruled record form; provenance, brief section 5.8 item F-01 and register item F-01; file F-01.md
Hash: c8746786ba808099139960680cd17c4410625647e5f7d02d56a00c9acb3c9ef7
Bytes: 602
Lines: 25
Expected counts: headed entries 2 (pinned); distinct DQ numbers 1 (pinned); gaps 0 (pinned); canonical state Ruled 2 (pinned)
Expected findings: one Error, duplicate number class, naming both heading lines, line 3 and line 15 (pinned); no other finding (pinned)
Expected exit: 1 (derived, Error present under OP-Q4)

Fixture: F-02
Kind: synthetic
Source: synthetic construction rule, one ruled record entry carrying a Ruled by line, a Ruling text line, a Ruling outcome line, and a landing line, with no line beginning with the Status marker anywhere in its span, written fresh in the ruled record form; provenance, brief section 5.8 item F-02 and register item F-02; file F-02.md
Hash: 16fd5e1b58217fdddf2527307dba87af22ef492a66b9bcb59b445d515c35e3a9
Bytes: 317
Lines: 11
Expected counts: headed entries 1 (pinned); canonical state Ruled 1 (pinned); decider recorded for the one entry (pinned)
Expected findings: none, and in particular no finding reporting a missing Status line as a defect in itself (pinned)
Expected exit: 0 (derived, no finding above Note grade under OP-Q4)

Fixture: F-03
Kind: synthetic
Source: synthetic construction rule, one open form entry with the full open field set and a decision block, followed by a closing Status line, followed by one further paragraph labelled as an addition to the same entry and carrying a further ruling statement, written fresh in the open form; provenance, brief section 5.8 item F-03 and register item F-03; file F-03.md
Hash: 60f976373bd069d58c4f3901ae5aaa7f4e26f6aeda5d0803a2bebc463d48ebe2
Bytes: 892
Lines: 34
Expected counts: headed entries 1 (pinned); every line assigned to that one entry (pinned); canonical state Ruled 1, derived from the whole body including the addition (pinned)
Expected findings: one Warning, label reattachment class, on DQ-001, for the post Status addition paragraph standing reattached to the entry by its label and flagged not contiguous (derived, grouping rule at testing pin down 6)
Expected exit: 1 (derived, Warning present under OP-Q4)

Fixture: F-04
Kind: synthetic
Source: synthetic construction rule, two open form entries, DQ-001 at level 3 and DQ-002 at level 2, with no section heading in the file, written fresh in the open form; provenance, brief section 5.8 item F-04 and register item F-04; file F-04.md
Hash: de21318ee2277149ac3b1535b6c455fc908d615008c9662d345de704878ef42a
Bytes: 1364
Lines: 47
Expected counts: headed entries 2 (pinned); canonical state Open 2, both entries receiving states from their bodies (derived)
Expected findings: none (derived, full open field set and no decision evidence in either entry)
Expected exit: 0 (derived, no finding above Note grade under OP-Q4)

Fixture: F-05
Kind: synthetic
Source: synthetic construction rule, two ruled record entries both numbered DQ-007, the first at level 3 and the second at level 2, written fresh in the ruled record form; provenance, brief section 5.8 item F-05, testing pin down 5, and register item F-05; file F-05.md
Hash: 5018cecbd7b82facb5ba05fcb485b6d0fa39e86e915d52589efe07c49dc917e9
Bytes: 616
Lines: 25
Expected counts: population assertion, headed entries 2 (pinned); distinct DQ numbers 1 (pinned); canonical state Ruled 2 (derived)
Expected findings: finding assertion, one Error, duplicate number class, naming both heading lines, line 3 and line 15 (pinned)
Expected exit: 1 (derived, Error present under OP-Q4)

Fixture: F-06
Kind: synthetic
Source: synthetic construction rule, one open form entry with the full field set, its blocks field naming exactly one blocked item, and no decision evidence of any form, written fresh in the open form; provenance, brief section 5.8 item F-06 and register item F-06; file F-06.md
Hash: 56b966beb5e18fd9e8131599a99c7deec43054eae52e9bf86c18e5ade0bf698d
Bytes: 694
Lines: 24
Expected counts: headed entries 1 (derived); canonical state Open 1 (pinned); waiting figure contribution 1 entry under the OP-Q12 formula (pinned); blocks field reported verbatim, one blocked item, counted under Q-49 with no link drawn (pinned)
Expected findings: no per entry finding (pinned)
Expected exit: 0 (derived, no finding above Note grade under OP-Q4)

Fixture: F-07
Kind: synthetic
Source: synthetic construction rule, one open form entry with the full open field set, stating Parked in words and carrying a reopening trigger in a labelled trigger line stating the event on which the entry reopens, in a separate file from F-08, written fresh in the open form; provenance, brief section 5.8 item F-07, testing pin down 8, and register item F-07; file F-07.md
Hash: a6548b1d26dc771bc645bdca7139559e73d5d2bdc1238cbe2587afee585704da
Bytes: 766
Lines: 26
Expected counts: headed entries 1 (derived); canonical state Parked 1 (pinned)
Expected findings: no Error (pinned); no other finding stated for this fixture in the brief (pinned)
Expected exit: 0 (derived, no finding above Note grade under OP-Q4)

Fixture: F-08
Kind: synthetic
Source: synthetic construction rule, one open form entry stating Parked in words, with no trigger named anywhere in the entry, in a separate file from F-07, written fresh in the open form; provenance, brief section 5.8 item F-08 and register item F-08; file F-08.md
Hash: 2f6b8f9872b474fe3f7a444de087902f82f1c9cf1a56403aed6677a7d576963f
Bytes: 540
Lines: 22
Expected counts: headed entries 1 (derived); canonical state Parked 1 (pinned)
Expected findings: one Error, Parked with no trigger (pinned)
Expected exit: 1 (derived, Error present under OP-Q4)

Fixture: F-09
Kind: synthetic
Source: synthetic construction rule, one open form entry with the full open field set and no decision block, whose only Status line states Presented in words, written fresh in the open form; provenance, brief section 5.8 item F-09 and register item F-09; file F-09.md
Hash: 91ab5f0b47d042ae2e4cd8a79f1bf5304b928e6e0ad2cfa65daf836c662f1dd2
Bytes: 542
Lines: 22
Expected counts: headed entries 1 (derived); canonical state Presented 1 (pinned)
Expected findings: no finding arising from the state itself (pinned)
Expected exit: 0 (derived, no finding above Note grade under OP-Q4)

Fixture: F-10
Kind: synthetic
Source: synthetic construction rule, three open form entries numbered DQ-035, DQ-036, and DQ-038, each with the full open field set and no decision block, written fresh in the open form; provenance, brief section 5.8 item F-10, testing pin down 6, and register item F-10; file F-10.md
Hash: b52986c86a666e3f22f6fc196badd00ddd15bfa1eb3a2c2628468dbf89dffc5e
Bytes: 2051
Lines: 70
Expected counts: headed entries 3 (pinned); numbers present 35, 36, and 38 (pinned); missing set exactly the single integer 37 (pinned); canonical state Open 3 (derived)
Expected findings: one Warning, numeric gap class, naming the full missing set, the single integer 37 (pinned, grouping rule at testing pin down 6)
Expected exit: 1 (derived, Warning present under OP-Q4)

Fixture: F-11
Kind: synthetic
Source: synthetic construction rule, one ruled record entry carrying a Status line, a Ruling text line, a Ruling outcome line, and a landing line, and no decider in any of the four recorded places at Q-17, written fresh in the ruled record form; provenance, brief section 5.8 item F-11 and register item F-11; file F-11.md
Hash: c218c44b31fd2a22c4c5aa8af46c3c31bacf3a4565ebdaf45a363c1798fb383e
Bytes: 288
Lines: 11
Expected counts: headed entries 1 (derived); the entry deriving a decided state, canonical state Ruled 1 (pinned as to a decided state, derived as to the state name)
Expected findings: one Error, decided entry with no decider (pinned)
Expected exit: 1 (derived, Error present under OP-Q4)

Fixture: F-12
Kind: synthetic
Source: synthetic construction rule, one ruled record entry carrying a Status line, a Ruled by line naming Captain JP, a Ruling outcome line, and a landing line, and no ruling text in any recorded label form, singular or plural, written fresh in the ruled record form; provenance, brief section 5.8 item F-12 and register item F-12; file F-12.md
Hash: 893177c05040bb88ee478712e3def382a4db9878292ba0d33bcaf02fd109599a
Bytes: 259
Lines: 11
Expected counts: headed entries 1 (derived); canonical state Ruled 1 (derived)
Expected findings: one Error, decided entry with no ruling text (pinned); no decider finding (pinned)
Expected exit: 1 (derived, Error present under OP-Q4)

Fixture: F-13
Kind: synthetic
Source: synthetic construction rule, one ruled record entry carrying a Status line, a Ruled by line, a Ruling text line, and a Ruling outcome line, and no landing record in any form, written fresh in the ruled record form; provenance, brief section 5.8 item F-13 and register item F-13; file F-13.md
Hash: 49b0781d6310a8d3f04ec99709599156534a444cdcaa6225229b7a1d202a615e
Bytes: 233
Lines: 11
Expected counts: headed entries 1 (derived); canonical state Ruled 1 (pinned); decider recorded (pinned)
Expected findings: one Warning, decided entry with no landing record (pinned)
Expected exit: 1 (derived, Warning present under OP-Q4)

Fixture: F-14
Kind: synthetic
Source: synthetic construction rule, one open form entry carrying a Status line reading Banked, an Owner of record line, and a Source line, and no question field, no options block, no cost field, and no blocks field, and no decision evidence of any form, written fresh in a shortened open form; provenance, brief section 5.8 item F-14, testing pin down 6, and register item F-14; file F-14.md
Hash: 2f8f8819f271d34e5753aa00c1360e0a6e7b07d4cd860d48bdd3deb302c2db5d
Bytes: 356
Lines: 11
Expected counts: headed entries 1 (derived); canonical state Open 1 (pinned)
Expected findings: four Warning findings, missing field class, one per missing field, for question, options, cost, and blocks (pinned, grouping rule at testing pin down 6)
Expected exit: 1 (derived, Warning present under OP-Q4)

Fixture: F-15
Kind: synthetic
Source: synthetic construction rule, four tail form entries numbered DQ-901 to DQ-904 at level 2, with heading outcome words in file order RULED, SETTLED, ORDERED, and BANKED, each with exactly one body paragraph and no line beginning with the Status marker in any entry, written fresh as a synthetic replica of the settled tail form; provenance, brief section 5.8 item F-15 in its corrected and conformed form, testing pin down 2, and register item F-15; file F-15.md
Hash: 95ff3fe383945af639fb755e3b09371010ee23dda16db4bb899eb880a5ad6ac3
Bytes: 1008
Lines: 17
Expected counts: headed entries 4 (pinned); line start Status lines 0 (pinned); canonical states Ruled 1, Settled 1, Closed as decided 1, Open 1, in file order DQ-901, DQ-902, DQ-903, DQ-904 (pinned)
Expected findings: one Note, unmatched heading word counted as a census Note under PIN-11, with its entry named, the entry being DQ-903 (pinned); no other finding stated for this fixture in the brief (pinned)
Expected exit: 0 (derived, Note findings alone leave the code at 0 under OP-Q4)

Fixture: F-16
Kind: synthetic
Source: synthetic construction rule, three tail form entries numbered DQ-905 to DQ-907 at level 2, each heading carrying no outcome word that decides the entry on its own, and each carrying exactly one body paragraph whose closing inline sentence carries its embedded Status occurrence and states, in file order, ruled and closed, settled and closed, and banked awaiting the named decider, written fresh as a synthetic replica of the settled tail form; provenance, brief section 5.8 item F-16, testing pin down 2, and register item F-16; file F-16.md
Hash: fa3e1520708c06702132df6db7d90dc84b3c643d3b802f8f8d7cf1b45623ae70
Bytes: 650
Lines: 13
Expected counts: headed entries 3 (pinned); line start Status lines 0 (pinned); embedded Status occurrences 3 (pinned); canonical states Ruled 1, Settled 1, Open 1, in file order (pinned)
Expected findings: none stated for this fixture in the brief (pinned)
Expected exit: 0 (derived, no finding above Note grade under OP-Q4)

Fixture: F-17
Kind: synthetic
Source: synthetic construction rule, two open form entries DQ-001 and DQ-002 at level 3; DQ-001 with the full open field set, a Status line reading Banked, and exactly one decision block, a paragraph opening with a bold lead in sentence in the DQ-005 position, after its field set, recording a settlement in words, naming the decider, and stating the landing; DQ-002 with the full open field set, a Status line reading Banked, and no decision block of any form, as control; the fixture constructs no supersession and no quasi heading; provenance, brief section 5.8 item F-17, testing pin down 9, and register item F-17; file F-17.md
Hash: 8c1a76378a6fddfebf1bb9e140a218baa0b10da3796fc721cf66da4d118d44f2
Bytes: 1414
Lines: 47
Expected counts: headed entries 2 (pinned); DQ-001 deriving its decided state from the bold lead in paragraph, canonical state Settled 1 (pinned as to a decided state, derived as to the state name); DQ-002 deriving Open, canonical state Open 1 (pinned)
Expected findings: no missing evidence finding for DQ-001 (pinned); no finding stated for DQ-002 (derived)
Expected exit: 0 (derived, no finding above Note grade under OP-Q4)

Fixture: F-18
Kind: synthetic
Source: synthetic construction rule, two open form entries in one file; the first states Parked in words, carries a named reopening trigger in a labelled trigger line, carries a blocks field naming exactly one blocked item, and carries no cost field; the second carries a Status line stating Presented in words, carries a blocks field naming exactly one blocked item, and carries no question field; neither entry carries decision evidence of any form; provenance, brief section 5.8 item F-18, testing pin down 8, and register item F-18; file F-18.md
Hash: 45cb1bfa25536a202399217263ab99925fcf899c62948e46709e819ecc26508a
Bytes: 965
Lines: 41
Expected counts: headed entries 2 (derived); canonical states Parked 1 and Presented 1 (pinned); each blocks field reported verbatim and counted under Q-49 with no link drawn, one blocked item per entry (pinned); waiting figure contribution 2 entries, one per entry, with neither entry counted a second time (pinned)
Expected findings: exactly two Warning findings, missing field class under the effectively open class, one per entry, for the cost field on DQ-001 and the question field on DQ-002 (pinned); no other per entry finding, and in particular no Parked with no trigger Error on DQ-001 (pinned)
Expected exit: 1 (derived, Warning present under OP-Q4)

Fixture: WV-1
Kind: synthetic
Source: synthetic construction rule, a copy of the restart pin file with every head Status line reading Banked and every body unchanged, preceded by one synthetic marker line; the pin source is the live decision queue file at the restart pin, 4614 lines, 432268 bytes, digest 23f6128230632a5de7f133a65a2497ed6fc11753083e17cd1dfd4fa1e57c6132, whole file range; provenance, brief section 5.8 item WV-1 and register item WV-1; file WV-1.md, stood since the completion seat, see the corpus completion paper
Hash: 72a957aecec02c2ce8bfec67e94559225cd043a8de38f5c18eb66c62dd4bac99
Bytes: 430350
Lines: 4615
Expected counts: headed entries 172 (derived, testing pin down 4 record); canonical counts matching the true pin file, Open 3, Presented 0, Parked 0, Ruled 72, Settled 84, Settled in part 0, Conditional 2, Closed as decided 9, with the Ambiguous reporting count at 2 and the unparsed entry count at 0 (derived, testing pin down 4 record); census group for Banked heads over decided bodies 151 entries, being every decided entry that carries a first line start Status line, with the sixteen decided entries among DQ-153 to DQ-171 outside the group (derived at Step 13 by joining the canonical split derivation record to the pin bytes); status occurrence total 253 occurrences, variant 2, line start 233, embedded 18 (derived, derivation D-13-2)
Expected findings: finding totals (open, derivation D-13-3, no figure stated)
Expected exit: 4 (derived, Ambiguous entries present under OP-Q4, as on the true pin run)

Fixture: WV-2
Kind: synthetic
Source: synthetic construction rule, a synthetic reversal of the restart pin file constructed mechanically, the headed entries within each section placed in reverse file order with each entry body unchanged byte for byte, section headings unmoved, section membership unchanged, file level note sections in their original positions, and reattached spans carried with the assembled entry to which the label reattachment rule reattaches them in the true pin run, preceded by one synthetic marker line; pin source as at WV-1, whole file range; provenance, brief section 5.8 item WV-2 and register item WV-2; file WV-2.md, stood since the completion seat, see the corpus completion paper
Hash: d26ffe9bb238fabce4176bb81598a01ef3f4f76ab759df1df5ba3538fd54418a
Bytes: 432300
Lines: 4615
Expected counts: canonical counts matching the true pin run, as at WV-1 (pinned as the required result, derived as to the figures at testing pin down 4); verbatim counts matching the true pin run (pinned as the required result); status occurrence total 253 occurrences, variant 2, line start 233, embedded 18 (derived, derivation D-13-2)
Expected findings: the finding set by rule and entry matching the true pin run, except for the label reattachment class, which is exempt from the match, and except that section introduction count disagreement is not exempt and must match (pinned as the required result); finding totals (open, derivation D-13-3, no figure stated)
Expected exit: 4 (derived, Ambiguous entries present under OP-Q4, as on the true pin run)

Fixture: WV-3
Kind: synthetic
Source: synthetic construction rule, a test harness record stating the oracle rule, its comparison set, and the reading of a disagreement, standing in the corpus under its identifier and shipping in no product; it is not a queue file and carries no queue entry; provenance, brief section 5.8 item WV-3, derivation D-13-5, and register item WV-3; file WV-3.md
Hash: e0d04eaecc2dc547e85c1b5d572a8db4f34b496cadae8c6a36563737dd51914d
Bytes: 1003
Lines: 13
Expected counts: oracle comparison result (open, derivation D-13-5, recorded inside Step 13 when the comparison runs in Slice 9)
Expected findings: none asserted in advance of the comparison (open, derivation D-13-5)
Expected exit: no exit code asserted for a test harness record (open, derivation D-13-5)

Fixture: WV-4
Kind: synthetic
Source: synthetic construction rule, one synthetic marker line followed by ten copies of the restart pin file, byte for byte, as a stress file at ten times the pin size; pin source as at WV-1, whole file range, ten times; the second part of this input, the recorded trigger for a later version where a live run reports a line count above 80 percent of the stated line limit, stands recorded in the brief and takes no file content; provenance, brief section 5.8 item WV-4, derivation D-13-7, and register item WV-4; file WV-4.md, stood since the completion seat, see the corpus completion paper; byte and line values by construction (derived, one marker line of 32 bytes plus ten copies of 432268 bytes, and one marker line plus ten copies of 4614 lines), and both values stand measured as recorded in the Hash, Bytes, and Lines fields
Hash: ec148f30f5f44f23f9128cce50ae72ecf674c0957880c3f915a4323e8af485dc
Bytes: 4322712
Lines: 46141
Expected counts: no entry count asserted, the run is a whole file refusal and no entry result stands (pinned)
Expected findings: none, a whole file refusal carries no finding result (pinned)
Expected exit: 3 (pinned, whole file refusal on a limit breach, the line count of 46141 standing over the line limit of 10000 and the byte count of 4322712 standing over the byte limit of 2000000, the refusal timed as a measurement only, with the timing itself open, derivation D-13-7)

Fixture: WV-6
Kind: synthetic
Source: synthetic construction rule, three short decided entries written in a fresh hand that did not produce the restart notes, in varied field order and varied recorded forms, classified by hand through the decided derivation rules at standing, before any code exists; provenance, brief section 5.8 item WV-6, derivation D-13-6, and register item WV-6; file WV-6.md
Hash: 0e835c85a1cacfdc62d67f0865e042dd82d3268d19f0285dc0f964850c9743be
Bytes: 940
Lines: 35
Expected counts: headed entries 3 (derived, by construction); canonical states Ruled 2, Settled 1, in file order, DQ-001 Ruled, DQ-002 Settled, DQ-003 Ruled (derived, derivation D-13-6, as confirmed by the independent reclassification at Step 13 audit 2); hand classification count 3 of 3 entries classified as their constructions intend, recorded in the corpus standing paper (derived, derivation D-13-6)
Expected findings: none (derived, each entry carrying decider, ruling or settlement text, outcome, and landing in a recorded form)
Expected exit: 0 (derived, no finding above Note grade under OP-Q4)

Fixture: WV-7
Kind: synthetic
Source: synthetic construction rule, three fixture shapes in one synthetic append, a duplicate DQ number at a mismatched heading level, a tail form entry whose heading outcome and single paragraph disagree, and two unnumbered headed entries standing as file level units, written fresh; provenance, brief section 5.8 item WV-7 and register item WV-7; file WV-7.md
Hash: a9dcb5d9cb6b00a08caf2cdb48ead21cbf8898388d277945e7372043728454eb
Bytes: 1055
Lines: 37
Expected counts: headed entries 3 (derived, the two DQ-501 entries and DQ-502, with no headed entry count and no DQ number recorded for either unnumbered headed entry); distinct DQ numbers 2 (derived); canonical states Ruled 2 and Open 1, the tail entry deriving Open under the whole body governing rule at Q-6 (derived)
Expected findings: one Error, duplicate number class, for DQ-501 at mismatched heading levels (pinned); one Warning, unmatched heading class with rule identifier PIN-06, for the second unnumbered headed entry (pinned); one Warning, unmatched heading class with rule identifier PIN-06, for the first unnumbered headed entry (derived, by the same class rule at PIN-06)
Expected exit: 1 (derived, Error present under OP-Q4)

Fixture: WV-8 (removal)
Kind: synthetic
Source: synthetic construction rule, a two entry open form file standing as the file after one whole entry, DQ-002, was removed from the middle of the number range of a three entry base, DQ-001 to DQ-003, written fresh in the open form; provenance, brief section 5.8 item WV-8 and register item WV-8; file WV-8-removal.md
Hash: ce3cab41370c1092aedeb463868600f11aaa608561cb021b7198b9544e8f37e9
Bytes: 1364
Lines: 47
Expected counts: headed entries 2 (derived, every total recounted to the smaller population); canonical state Open 2 (derived); missing set exactly the single integer 2 (derived)
Expected findings: one Warning, numeric gap class, naming the missing set, the single integer 2 (pinned as to the class under Q-27, derived as to the set)
Expected exit: 1 (derived, Warning present under OP-Q4)

Fixture: WV-8 (truncation)
Kind: synthetic
Source: synthetic construction rule, a two entry file whose second entry body is cut off in the middle of a body line at end of file, the last body line carrying no line ending, written fresh in the open form; the file carries 33 line feed terminated lines and one final partial line; provenance, brief section 5.8 item WV-8 and register item WV-8; file WV-8-truncation.md
Hash: b277542b44a9116247d758fadac51acdd302408442ea4b71e69aece3569633e6
Bytes: 890
Lines: 34
Expected counts: headed entries 2, the partial entry counted exactly once in the headed entry count (pinned); unparsed entry count 1, the partial entry standing in the unparsed entry count and in no canonical state count and not in the Ambiguous reporting count (pinned); canonical state Open 1, for the surviving whole entry, with no state derived or printed for the partial entry (pinned)
Expected findings: no finding that derives or asserts a state for the partial entry (pinned); every surviving line assigned to exactly one unit or listed as unassigned (pinned)
Expected exit: 4 (pinned, on the unparsed entry reason class at OP-Q4, with any Error and Warning findings present named in the closing line under the masking rule at OP-Q4)

Fixture: WV-9
Kind: synthetic
Source: synthetic construction rule, three open form entries whose only Status elements carry invented untranslatable phrasings in recorded Status line form, standing as the WV entry set for the volume probe, written fresh in the open form; provenance, brief section 5.8 item WV-9, derivation D-13-9, and register item WV-9; file WV-9.md
Hash: 39cb014a5b4a5470d8897d4a1330640452c158c981623ba73db21d3c71d50d9d
Bytes: 1637
Lines: 64
Expected counts: headed entries 3 (derived, by construction); canonical state Open 3, under the Shape A exception for an unclassifiable value as the only status element with no decision evidence (derived); residue count for WV-9.md itself 3 entries of 3 headed entries (derived, by construction on this file, its three entries carrying only invented untranslatable phrasings); pin population probe outputs, not figures of WV-9.md: residue count 1 entry and share of entries resting on untranslatable phrasings 1 over 172 headed entries, both on the pin population for the D-13-9 probe outputs (derived, derivation D-13-9, and no output printing the share until the Manager decision on the probe evidence)
Expected findings: three Note findings, unclassified status value class, one per entry (derived, by construction under PIN-04 Shape A)
Expected exit: 0 (derived, Note findings alone leave the code at 0 under OP-Q4)

Fixture: WV-10
Kind: synthetic
Source: synthetic construction rule, 172 tail form entries numbered DQ-001 to DQ-172 at level 2, generated in one repeated tail form, each with exactly one body paragraph stating banked awaiting the named decider in its closing sentence, and no Status line anywhere in the file, standing as a tail only fixture at full file scale; provenance, brief section 5.8 item WV-10 and register item WV-10; file WV-10.md
Hash: bcb5a1deb5a844aa580e3ffec5bf088417962f4f34937e551c4086b6a42ff5b9
Bytes: 30433
Lines: 689
Expected counts: headed entries 172 (derived, by construction); canonical state Open 172 (derived); Ambiguous reporting count 0 (derived); unparsed entry count 0 (derived); footing, 172 plus 0 plus 0 equals 172 headed entries, with the Ambiguous reporting count and the unparsed entry count each named as a component of that footing (pinned as the required result); line start Status lines 0 (derived); every line assigned exactly once (pinned as the required result)
Expected findings: none (derived, by construction)
Expected exit: 0 (derived, no finding above Note grade under OP-Q4)

Fixture: S5-C1 (no outcome construction)
Kind: synthetic
Source: synthetic construction rule, one synthetic decided entry DQ-910 in the ruled record form of F-13, with a decider present, ruling text present, and a landing record present, and with no outcome in any recorded form, built at Step 13 as the no outcome construction; provenance, plan Item 2, section 2.7, register item TG-S5-01, and the in test construction at product/tests/test_restart_slice5.py line 211; file S5-C1-no-outcome.md
Hash: b1c7ec110c163a3967c0b95a4663ea51eb8d657b96b6ab3020e9ab1f6e42e787
Bytes: 231
Lines: 15
Expected counts: headed entries 1 (derived, by construction); canonical state Ruled 1 (derived, by construction)
Expected findings: one Warning finding of the outcome class (derived, plan Item 2, section 2.7); no landing record Warning (derived, plan Item 2, section 2.7)
Expected exit: 1 (derived, Warning present under OP-Q4)

Fixture: S5-C2 (combined construction)
Kind: synthetic
Source: synthetic construction rule, one synthetic decided entry DQ-911 in the ruled record form of F-13, with a decider present and ruling text present, and with no outcome in any recorded form and no landing record in any form, built at Step 13 as the combined construction; provenance, plan Item 2, section 2.7, register item TG-S5-01, testing pin down 7, and the in test construction at product/tests/test_restart_slice5.py line 226; file S5-C2-combined.md
Hash: 0dcf7e4b98aeaa7d3f44a02874df75f2245169c032c3f26e5d2643922cbc6e4a
Bytes: 187
Lines: 13
Expected counts: headed entries 1 (derived, by construction); canonical state Ruled 1 (derived, by construction)
Expected findings: two Warning findings, one under the outcome test and one under the landing record test (derived, plan Item 2, section 2.7 and testing pin down 7)
Expected exit: 1 (derived, Warning present under OP-Q4)

Fixture: S5-C3 (first limb construction)
Kind: synthetic
Source: synthetic construction rule, two synthetic entries, DQ-920 in the ruled record form and DQ-921 carrying a statement that identifies exactly one entry, DQ-920, as the superseded subject and in words claims to displace it, but whose wording does not state displacement in the ruling sense, so the first limb only fails, built at Step 13 as the first limb construction; provenance, plan Item 2, section 2.7, register item TG-S5-02, and the in test construction at product/tests/test_restart_slice5.py line 325; file S5-C3-first-limb.md
Hash: 57aae9fe9df98efd6f10e0b227d826623857de3b5400c18fdeae0f7e97d6b47d
Bytes: 562
Lines: 29
Expected counts: headed entries 2 (derived, by construction); canonical state Ruled 2 (derived, by construction)
Expected findings: one Note finding, supersession near miss class, standing on DQ-921, with DQ-921 in the finding entry identifier field and DQ-920 in the named entries field (derived, plan Item 2, section 2.7); no pointer on DQ-920 (derived, plan Item 2, section 2.7)
Expected exit: 0 (derived, Note findings alone leave the code at 0 under OP-Q4)

Fixture: S5-C4 (second limb construction)
Kind: synthetic
Source: synthetic construction rule, two synthetic entries, DQ-922 in the ruled record form and DQ-923 carrying a statement that in words states displacement in the ruling sense and names one entry, DQ-922, but does not name that entry, or any ruling, figure, or subject, as the superseded subject in terms that identify exactly one entry, so the second limb only fails, built at Step 13 as the second limb construction; provenance, plan Item 2, section 2.7, register item TG-S5-02, and the in test construction at product/tests/test_restart_slice5.py line 352; file S5-C4-second-limb.md
Hash: 88999bea9b5f5e584386df5663ecbb05f82ee14b99c4df14818907cd7923bfc4
Bytes: 586
Lines: 29
Expected counts: headed entries 2 (derived, by construction); canonical state Ruled 2 (derived, by construction)
Expected findings: one Note finding, supersession near miss class, standing on DQ-923, with DQ-923 in the finding entry identifier field and DQ-922 in the named entries field (derived, plan Item 2, section 2.7); no pointer on DQ-922 (derived, plan Item 2, section 2.7)
Expected exit: 0 (derived, Note findings alone leave the code at 0 under OP-Q4)

Fixture: S5-C5 (cited number construction)
Kind: synthetic
Source: synthetic construction rule, one synthetic decided entry DQ-940 in the ruled record form and one synthetic file level note section, headed Amendment note, carrying one passage that cites DQ-999, a DQ number with no heading in its file, and that also carries a state claim in the same passage, built at Step 13 as the cited number construction; provenance, plan Item 2, section 2.7, register item TG-S5-03, and the in test construction at product/tests/test_restart_slice5.py line 761; file S5-C5-cited-number.md
Hash: dad4efb98f22d4bf1121a7f0e322883baf172d3cddc6dcff8995d3ba8d056050
Bytes: 396
Lines: 21
Expected counts: headed entries 1 (derived, by construction); canonical state Ruled 1 (derived, by construction); cited DQ number with no heading in its file 1, DQ-999 (derived, by construction)
Expected findings: one Note finding of the cited number class under PD-R7, reported once under its own class for the passage citing DQ-999 (derived, plan Item 2, section 2.7); the state claim in the same passage reported under its own claim class (derived, plan Item 2, section 2.7); no second cited number finding for that passage (derived, plan Item 2, section 2.7)
Expected exit: 0 (derived, Note findings alone leave the code at 0 under OP-Q4)

Fixture: PIN
Kind: real snapshot, acceptance pin copy for the acceptance run under testing pin down 11, the acceptance role stated in this entry, and every testing pin down 1 kind duty applies to this entry and none is waived
Source: ~/workspace/build-flow-expansion/DECISION-QUEUE.md, copied byte for byte with no line ending conversion and no edit, whole file line range lines 1 to 4614, the copy act standing as the source of this entry; provenance, brief section 4 pin facts, plan testing pin down 11, and Item 6 section 6.7; file PIN.md
Hash: 23f6128230632a5de7f133a65a2497ed6fc11753083e17cd1dfd4fa1e57c6132
Bytes: 432268
Lines: 4614
Expected counts: DQ entry headings 171 (pinned); distinct DQ numbers 171 (pinned); line start Status lines 233 (pinned); entries with no line start Status line 19, namely DQ-153 to DQ-171 (pinned); primary Banked entries 103 (pinned); headed entries 172 (derived, testing pin down 4 record); canonical counts Open 3, Presented 0, Parked 0, Ruled 72, Settled 84, Settled in part 0, Conditional 2, Closed as decided 9 (derived, testing pin down 4 record); Ambiguous reporting count 2, being DQ-087 and DQ-106 (derived, testing pin down 4 record); unparsed entry count 0 (derived, testing pin down 4 record); footing 170 plus 2 plus 0 equals 172 headed entries (derived, testing pin down 4 record); census groups of the 103 primary Banked entries, 73 with a later Status line in the body, 24 with a level 4 decision block only, and 6 with unheaded paragraphs only (derived, census groups derivation); Banked head crosswalk rows Ruled 22, Settled 71, Closed as decided 6, and Conditional 2, summing to 101, plus the Ambiguous reporting count 2, footing to 103 (derived, canonical split derivation); status occurrence total 253 occurrences, variant 2, line start 233, embedded 18 (derived, derivation D-13-2, confirmed); distinct verbatim appendix row count (open, contested at D-2, no figure stated)
Expected findings: finding totals (open, derivation D-13-3, no figure stated), as the acceptance run expectations at testing pin down 11, in the form the WV-1 entry records for the pin population
Expected exit: 4 (derived, Ambiguous entries present under OP-Q4, as the acceptance run expectation at testing pin down 11)
