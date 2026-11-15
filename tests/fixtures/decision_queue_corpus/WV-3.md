<!-- synthetic fixture WV-3 -->

# WV-3 oracle record, test harness only

This file is a test harness record. It is not a queue file, it carries no queue entry, and no part of it ships in the tool.

Oracle rule: the oracle derives the state of each entry of a corpus fixture from the render style groupings of that fixture, grouping entries by their derived state as a render output groups them, and the test stage compares that derivation against the validate derivation for the same fixture, entry by entry.

Comparison set: the corpus fixtures F-01 to F-18 and the landed inputs WV-1, WV-2, WV-6, WV-7, WV-8, WV-9, and WV-10, each as its manifest entry states it.

Reading of a disagreement: a disagreement between the oracle derivation and the validate derivation is a defect signal about one of the two, and the fixture verdict for the fixture compared decides which.

Standing: this record stands in the corpus before the code it tests. Its comparison runs inside the test stage only, in Slice 9.
