# Decision Queue

## Purpose

This queue is the one list holding every conflict, hold and open question waiting on Captain JP for the build flow programme. This plan feeds the one queue. It does not create a second queue.

Queue seeded 2026-11-10 with the items in this file. No other open items are known at seed time. Later steps add items as conflicts arise.

Owner of record for the queue: Decision-queue Clerk.

## Ordering rule

Open items are ordered easy to answer first.

- One tap or short answer items are at the top.
- Items that need a brief cost or scope judgement follow.
- Deep rulings, and items that require naming a specific project or candidate, are last.

Each open item carries its ordering reason.

## How items move

- Banked: an item is received and recorded in this queue with its source, options, cost of deciding late, and what it blocks. It is not yet presented for a ruling.
- Presented: an item is shown to Captain JP in queue order, with its options stated plainly.
- Ruled: Captain JP gives a ruling. The item moves to the Ruled Record at the end of this queue, with the ruling text, the date, and where the ruling landed. Ruled items stay on record.
- Parked with trigger: Captain JP parks an item by explicit word. The item stays in the open section marked as parked, with the named trigger that reopens it. A parked item does not block work that its trigger defines as unblocked.

## Intake rule

Ruled by Captain JP at DQ-106. Questions are held for Captain JP until she asks. The Manager answers most questions itself under its recorded delegations and settlements; a question is presented to Captain JP only when it is absolutely necessary, that is, when the Manager cannot discern which choice best meets her principles. No item is defaulted for want of a ruling at any volume; the no default settlement recorded at DQ-106 stands under this rule.

## Open items

### DQ-035: Eval-Driven Development Items 140, 212, and 267, employee trace harvesting and the erasure position

Status: Banked

Owner of record: Decision-queue Clerk

Source: consolidated/02-eval-driven-development.md, Item 140 in the Step 8 extraction (extraction-a.md), ruled Conflict, with the same question carried as a gated element in Item 212 (extraction-b.md) and as the erasure clause in Item 267 (extraction-b.md), both ruled Adapt with this entry governing the reserved element.

The question: For an internal agent used by employees, on what basis are employee traces harvested into a permanent reviewable dataset, and what is the estate's position on erasure against experiment immutability?

The options, stated plainly:

- Reviewed position first: a counsel or data protection reviewed position is recorded in the governance page before the first production harvest in any system holding personal or employee data, covering the notice and purpose statement for employee harvesting, retention lifetimes per data category, and whether erasure cascades into experiment records or stops at the redacted case. Until it is recorded, no production harvest runs. This is the form Items 267 and 286 already gate on.
- Working position adopted: the source's working position is adopted as the estate position (scores and the redacted case kept permanently, raw traces on a short retention clock, harvesting named as employee monitoring in the governance page with the appropriate review obtained), and it is reviewed only when a deployment first holds personal or employee data.
- No employee harvesting: traces from internal or employee facing agents are never promoted into permanent datasets, and the production loop for such systems runs on guards, signals, and human review only.

Cost of deciding late: medium. The offline EDD loop lands and runs without any production harvest, so no build stage waits on this entry; the cost falls due at the first production phase, where Phase 3 at Item 286 cannot be met without the recorded position, and any harvest done before the position exists would be done on an unsettled basis.

What it blocks: the production phase for any system holding personal or employee data (Item 286's privacy precondition), the erasure position element of the governance page at Item 281, and the legal position incubation at Item 212. It blocks no offline item.

Ordering reason: this entry sits second. It needs a short policy choice among three stated options, but the first option asks Captain JP to commission a reviewed position, which is a scope judgement rather than a one tap answer.

#### Ruling by Captain JP

Question as put on the Questions space: "Before a system may keep its own employees' work traces in a permanent dataset, must a reviewed legal position be written down first?" Her answer, in her words: "Reviewed position first, no collecting until it exists."

Ruled: a counsel or data protection reviewed position is recorded in the governance page before the first production harvest in any system holding personal or employee data. Until it is recorded, no production harvest runs and no employee traces are collected into a permanent dataset. The source working position (scores and the redacted case kept permanently, raw traces short lived) is not adopted. The riders are EDD Items 140, 212, and 267, governed by this ruling. Landed in LEVEL-1-STANDING.md at the R-190 governance passage and in LEVEL-2-STEPS.md at the Phase 3 exit criteria. The incubated set passage in LEVEL-1-STANDING.md was checked: its trigger already matches this ruling, so it was not amended. Closed.

### DQ-036: Eval-Driven Development Items 162, 237, 287, and 288, the five tier proportionality ladder

Status: Banked

Owner of record: Decision-queue Clerk

Source: consolidated/02-eval-driven-development.md, Item 162 (extraction-a.md) and Items 237, 287, and 288 (extraction-b.md), each ruled Conflict in the Step 8 rulings.

The question: Does the EDD proportionality ladder (Tier 0 Skip, Tier 1 Lightweight, Tier 2 Standard, Tier 3 Full, Tier 4 Regulated, set by tool blast radius, change frequency, and irreversibility) enter the flow, and if so, how does it stand against the tier rule in LEVEL-1 rule R-4 and the Plaid definition in PLAID.md?

The options, stated plainly:

- No ladder: the ladder does not enter the flow. Tier stays as R-4 states it (Low, Medium, High, Extra High, Plaid; Captain JP or the size test; Plaid by Captain JP alone). EDD proportionality is expressed through the tier record, the tailoring record, and the governance page, and Items 287 and 288 do not land.
- Ladder as adoption scope, not as tiers: the five rungs land renamed as EDD adoption scopes inside the governance page, stating how much of the EDD machinery a system takes, with no tier word used and no effect on the build's tier under R-4. Item 287's severable elements (an assessor who did not build the suite, evidence reconstructible from records alone, an exercised off switch) and Item 288's skip table land in that scope form.
- Ladder as the tier system: the ladder replaces or amends the R-4 tier structure for EDD purposes. This option asks Captain JP to rule on the flow's tier structure itself, including how the regulated rung stands against Plaid, which only she can do.

Cost of deciding late: low for the build flow, higher for EDD adoption decisions. Every other Step 8 item lands without the ladder, with tier references read under the R-4 tier record as the rulings state; the cost is that per rung skip tables and the regulated phase have no ruled form, so a system that would sit at the top rung has no ruled EDD scope until this entry is answered.

What it blocks: Items 162, 237, 287, and 288 in full; the C6 element of Item 178; the G4 element of Items 172, 186, and 192; the regulated tier scope element of Item 309; and the tier wording inside Items 187, 205, 219, 253, 272, 276, 278, 282, 299, and 308, which the rulings currently read under the R-4 tier record.

Severability note: elements of Items 287 and 288 are severable. Item 287's independent elements (an assessor who did not build the suite, evidence reconstructible from records alone, an exercised off switch) are severable if Captain JP rules the phase in without the ladder. One clause of Item 288 is severable and already covered in substance: the rule that spec, grader validity review, and arbitration may never be skipped on an irreversible change is covered by base LEVEL-1 rule R-89 together with the landed Items 242, 260, and 277, so that clause needs no ladder to stand.

Ordering reason: this entry sits last. It is a deep ruling about the flow's own tier structure, it touches the reserved Plaid area, and its third option would amend a standing rule of Captain JP's flow, so it needs her full attention rather than a burst answer.

#### Ruling by Captain JP

Question as put on the Questions space: whether the five rung EDD proportionality ladder enters the flow, as recorded in this entry. Her answer, in her words: "No ladder, my tiers stay the only ones."

Ruled: the five rung EDD proportionality ladder does not enter the flow in any form, not as tiers and not as adoption scopes. Items 162, 237, 287, and 288 do not land. The severable elements named in this entry stay unlanded as ladder elements. The one clause already covered in substance stays covered as this entry severability note records, by R-89 together with the landed Items 242, 260, and 277, and it needs no ladder to stand. Landed as a refusal in PLAID.md at R-211, where the sentence that waited on this ruling now records that no ladder enters the flow and the regulated tier scope is not restored. LEVEL-1-STANDING.md and LEVEL-3-TEAMS.md were checked: both already state that the ladder element does not land and that readings run under R-4, so neither was amended. Closed.

### DQ-037: Anton Item 155 (C-29), pattern seats as rotating team duties

Status: Banked

Owner of record: Decision-queue Clerk

Source: 01-anton-architecture-patterns.md, global Item 155, local item C-29 (survivor S8 in the source selection).

The question: Should pattern duties be held as named seats that rotate between holders, with a protocol for recording a seat as deliberately empty, on top of the flow existing roles?

The options, stated plainly:

- No seat system: pattern duties stay assigned to the existing roles and agent files, as ruled in this Step 9 ruling set under the seat mapping group, and no seat, rotation, or deliberate empty record is created.
- Seat system as a duty layer only: named pattern duty labels are used in design records, held by the existing role that already owns each duty, with no rotation and no change to staffing, and an unheld duty is marked as a gap with its fill trigger.
- Full seat system: seats are created as a staffing layer, holders rotate, seats may be recorded as deliberately empty with fill triggers, and the flow team and member rules are amended to carry the system.

Cost of deciding late: low. The duties themselves are landed under the seat mapping group, so design work at the pattern gate proceeds without this decision; the cost is only that the vocabulary of seats stays barred from flow records until this entry is answered.

What it blocks: Item 155 only, and, in practice, Items 168, 222, 235, 236, and 237, whose entries (DQ-038, DQ-043, DQ-045, DQ-046, and DQ-047) each presuppose some form of this question.

Ordering reason: this entry sits near the end of the presentation order. It is a structural ruling about the flow role system itself, and five other prepared entries depend on its shape, so it needs a considered answer rather than a burst answer.

#### Settlement under Captain JP's pass 2 grant: DQ-037

Settled by: The Manager (Muse), under Captain JP's pass 2 grant, in her words: "Do another high discernment pass. I do not want the system to cheat itself or agents to cheat the system plus all the other stuff I said before."

Governing standard: the anti-cheat test first, that the system must not cheat itself and agents must not cheat the system, then Captain JP's settlement philosophy, security first, quality second, speed last, strict reading where workable unless it adds a huge build time, workable reading where strict is unworkable or too costly, neither good stays hers, and genuine redundancy removed with the surviving passage named, with DQ-138, the corpus gate governs over cost, and DQ-139, clashes decided by discernment on the merits and never by recency.

Settlement: No seat system is created. Pattern duties stay assigned to the existing roles named in the Step 9 group G11 mapping in the agent files, and a duty with no holder for a build is marked in the brief as a gap with its reason and its fill trigger. No rotation and no deliberate empty record is created for any pattern duty.

Deciding ground: anti-cheat, system side.

Landing: RECORD-ONLY. Verified standing: LEVEL-3 R-34, LEVEL-4 R-49, LEVEL-1 R-5, and the G11 clauses in nine agent files. No document edit was made for this settlement.

Status: SETTLED by the Manager under the pass 2 grant, not ruled by Captain JP. This item is settled.

### DQ-038: Anton Item 168 (C-42), seat rotation and the seat system kill rule

Status: Banked

Owner of record: Decision-queue Clerk

Source: 01-anton-architecture-patterns.md, global Item 168, local item C-42.

The question: If any seat form is adopted, should its holders rotate on a fixed cadence, with the gatekeeping duty rotating slowest, and should the seat form carry a rule that kills it and keeps only its reviews if seats become titles?

The options, stated plainly:

- No rotation: holders of pattern duties are the existing roles for the whole build, as the standing role rule states, and this entry closes with Item 155 answered as no seat system or as a duty layer only.
- Rotation inside a build: pattern duty labels rotate between the existing role holders at a stated review point, with handovers recorded in the pattern decision ledger.
- Rotation with the kill rule: rotation as in the second option, plus a standing rule that if duty labels become titles or ranks, the labels are dropped and only the reviews are kept.

Cost of deciding late: low. No rotation is needed for the pattern gate to run, because its duties are held by named existing roles from the start of a build to its end.

What it blocks: Item 168 only. It blocks no gate, ledger, or removal item.

Ordering reason: this entry sits in the later half of the presentation order. It is a short choice, but it is meaningless until DQ-037 settles whether any seat form exists to rotate.

#### Settlement under Captain JP's pass 2 grant: DQ-038

Settled by: The Manager (Muse), under Captain JP's pass 2 grant, in her words: "Do another high discernment pass. I do not want the system to cheat itself or agents to cheat the system plus all the other stuff I said before."

Governing standard: the anti-cheat test first, that the system must not cheat itself and agents must not cheat the system, then Captain JP's settlement philosophy, security first, quality second, speed last, strict reading where workable unless it adds a huge build time, workable reading where strict is unworkable or too costly, neither good stays hers, and genuine redundancy removed with the surviving passage named, with DQ-138, the corpus gate governs over cost, and DQ-139, clashes decided by discernment on the merits and never by recency.

Settlement: Pattern duty holders do not rotate. Each duty stays with the existing role that holds it for the whole build, and no seat system kill rule is created, because no seat system exists for it to kill. Where a holder later changes, the change is recorded in the pattern decision ledger under its handover form.

Deciding ground: anti-cheat, agent side.

Landing: RECORD-ONLY. No document edit was made for this settlement.

Flag recorded: the familiarity argument for rotation pulled the other way; the anti-cheat test governed.

Status: SETTLED by the Manager under the pass 2 grant, not ruled by Captain JP. This item is settled.

### DQ-039: Anton Item 177 (C-51), refusal and removal artefacts as promotion evidence

Status: Banked

Owner of record: Decision-queue Clerk

Source: 01-anton-architecture-patterns.md, global Item 177, local item C-51.

The question: Should refusal, removal, and quiet system artefacts be produced as evidence for a review or promotion process for individual engineers?

The options, stated plainly:

- No promotion use: the artefacts (decision records, skip records, burn-down measures, and rehearsal results) exist as build records only, and no flow record is written for, or cited in, any personnel process.
- Team level use only: the artefacts may be cited as facts about a team work, in the form the source itself keeps after its own selection killed the individual metric, and never as an individual score.
- Individual use: the artefacts may be cited in individual review or promotion, with the safeguards, if any, named in the ruling.

Cost of deciding late: low. Every artefact named in this item already exists as a build record under the gate, ledger, and removal groups, so no build waits on this entry; the cost is that the boundary of those records use stays stated only in this ruling file until the entry is answered.

What it blocks: Item 177 only.

Ordering reason: this entry sits in the first half of the presentation order. It is a single boundary choice among three plainly stated options, with no numbers and no staffing change attached.

#### Settlement under Captain JP's grant: DQ-039

Settled by: The Manager (Muse), under Captain JP's grant, in her words: "Go ahead and answer any of them yourself that seems simple enough. I care about security and quality over speed, i don't want things to be too strict that they're impossible, but they should be relatively strict to the standards they hold."

Strictness rule, in Captain JP's words: "If the stricter setting is not workable, then go with the workable. If the strict setting is workable go with it unless it adds a huge build time."

Settlement: Pattern artefacts, namely decision records, skip records, burn down measures, and rehearsal results, are build records only. No flow record is written for, or cited in, any personnel review or promotion process, and no artefact is used as an individual score.

Deciding limb: strict workable. Source of settlement text and limb: classify-a.md and refinement-abd.md Part 1 limb audit.

Status: SETTLED by the Manager under the grant, not ruled by Captain JP. This item is settled.

### DQ-040: Anton Item 184 (C-58), kill condition for the whole pattern expansion

Status: Banked

Owner of record: Decision-queue Clerk

Source: 01-anton-architecture-patterns.md, global Item 184, local item C-58.

The question: Should evidence that adoption errors are mainly knowledge errors retire the whole pattern apparatus landed in this step, and if so, what share counts as mainly, and who judges the evidence?

The options, stated plainly:

- No self executing kill: the apparatus is retired or kept only through the standing stewardship and falsifier rules and a ruling in this queue, and the return to divergence trigger landed at Item 159 is the only automatic consequence of such evidence.
- Kill with a defined threshold: the apparatus carries a kill condition, with the threshold share, the evidence source, and the judging role all named in the ruling, and retirement recorded as a superseding ledger and trace act.
- Kill as written: the apparatus is archived whenever an honest run shows adoption errors are mainly knowledge errors, with mainly left as a judgement in each case.

Cost of deciding late: low while the apparatus is new. The cost grows only after real runs exist, because until then there is no evidence on which any form of this condition could fire.

What it blocks: Item 184 only. The iteration and stewardship items around it are landed without it.

Ordering reason: this entry sits last in the presentation order. It asks for a threshold no source supplies and would govern the retirement of a whole landed apparatus, so it is the deepest ruling among the prepared entries.

#### Settlement under Captain JP's grant: DQ-040

Settled by: The Manager (Muse), under Captain JP's grant, in her words: "Go ahead and answer any of them yourself that seems simple enough. I care about security and quality over speed, i don't want things to be too strict that they're impossible, but they should be relatively strict to the standards they hold."

Strictness rule, in Captain JP's words: "If the stricter setting is not workable, then go with the workable. If the strict setting is workable go with it unless it adds a huge build time."

Settlement: The pattern apparatus carries no self executing kill condition and no threshold kill condition. The apparatus is retired or kept only through the standing stewardship route in LEVEL-2 rule R-149 and the falsifier route in LEVEL-1 rule R-194, together with a ruling in this queue, and the return to divergence form already landed at Item 159 is the only automatic consequence of evidence that adoption errors are mainly knowledge errors.

Deciding limb: strict unworkable. Source of settlement text and limb: refinement-abd.md Part 2.

Status: SETTLED by the Manager under the grant, not ruled by Captain JP. This item is settled.

### DQ-041: Anton Item 186 (D-2), a teaching and onboarding sequence for pattern topics

Status: Banked

Owner of record: Decision-queue Clerk

Source: 01-anton-architecture-patterns.md, global Item 186, local item D-2.

The question: Should the flow carry a teaching and onboarding sequence for architecture pattern topics, ordered with named pattern entries, as a flow artefact?

The options, stated plainly:

- No curriculum in the flow: pattern order inside the flow stays an adoption and design order only, and any teaching material for engineers is produced outside the flow, outside this programme.
- A learning order annex only: the labelled learning ladder already ruled in this step is kept as a reference annex to the design steps, with no onboarding duty, no sequence obligation, and no owning teaching role.
- A full onboarding sequence: a teaching sequence is commissioned as its own artefact, with a named owner role named in the ruling, outside the pattern gate work of this step.

Cost of deciding late: low. Design steps run on the adoption order and the gate, neither of which needs a teaching sequence.

What it blocks: Item 186 only.

Ordering reason: this entry sits near the top of the presentation order. It is a binary scope choice, in or out of the flow, with a middle option that costs nothing to state.

#### Settlement under Captain JP's grant: DQ-041

Settled by: The Manager (Muse), under Captain JP's grant, in her words: "Go ahead and answer any of them yourself that seems simple enough. I care about security and quality over speed, i don't want things to be too strict that they're impossible, but they should be relatively strict to the standards they hold."

Strictness rule, in Captain JP's words: "If the stricter setting is not workable, then go with the workable. If the strict setting is workable go with it unless it adds a huge build time."

Settlement: The flow carries no teaching or onboarding sequence, no onboarding duty, and no owning teaching role. The labelled learning ladder already ruled in Step 9 group G10 part (b) is kept only as a reference annex to the design steps, stated as a learning order and never used as an adoption order.

Deciding limb: strict workable. Source of settlement text and limb: classify-a.md and refinement-abd.md Part 1 limb audit.

Status: SETTLED by the Manager under the grant, not ruled by Captain JP. This item is settled.

### DQ-042: Anton Item 194 (D-10), adopted, operated, or correctly refused wording in reviews and hiring

Status: Banked

Owner of record: Decision-queue Clerk

Source: 01-anton-architecture-patterns.md, global Item 194, local item D-10.

The question: Should review and hiring wording in the estate replace knows pattern X with has adopted, operated, or correctly refused pattern X, in its lane, with the record to show it?

The options, stated plainly:

- No hiring rule in the flow: the flow records carry pattern decisions for build purposes only, and hiring and review wording is set outside the flow, outside this programme.
- Wording adopted outside the flow: the wording is adopted as an estate practice by a separate instrument, and the flow is amended only to note that its gate and ledger records may be cited there.
- Wording adopted in the flow: the flow itself states the hiring and review wording, with the citing rules for gate and ledger records named in the ruling.

Cost of deciding late: low. No build step cites hiring wording, and gate and ledger records are kept in full either way, so a later adoption loses no evidence.

What it blocks: Item 194 only.

Ordering reason: this entry sits in the first half of the presentation order. It is a scope choice about where a wording rule lives, and can be answered in one line.

#### Settlement under Captain JP's grant: DQ-042

Settled by: The Manager (Muse), under Captain JP's grant, in her words: "Go ahead and answer any of them yourself that seems simple enough. I care about security and quality over speed, i don't want things to be too strict that they're impossible, but they should be relatively strict to the standards they hold."

Strictness rule, in Captain JP's words: "If the stricter setting is not workable, then go with the workable. If the strict setting is workable go with it unless it adds a huge build time."

Settlement: The flow states no hiring or review wording rule. Flow gate and ledger records are kept in full for build purposes only, and any wording for reviews or hiring is set outside the flow and outside this programme.

Deciding limb: strict workable. Source of settlement text and limb: classify-a.md and refinement-abd.md Part 1 limb audit.

Status: SETTLED by the Manager under the grant, not ruled by Captain JP. This item is settled.

### DQ-043: Anton Item 222 (D-38), a seat table with mergers for smaller teams

Status: Banked

Owner of record: Decision-queue Clerk

Source: 01-anton-architecture-patterns.md, global Item 222, local item D-38.

The question: Should shadow pattern duties be assigned through a seat table that merges duties when a team is small, and if so, what team size triggers which mergers?

The options, stated plainly:

- No seat table: shadow duties stay assigned directly to the existing roles, as ruled under the seat mapping group, with no table and no mergers.
- Assignment table without mergers: a table records which existing role holds each shadow duty for a build, one holder per duty, with no duty held by two roles and no role created.
- Table with mergers: a table as in the second option, plus merger rules, with the size thresholds and the permitted merger pairs named in the ruling.

Cost of deciding late: low. Assignment already happens, role by role, under the seat mapping group; a table would only make the assignment visible in one place.

What it blocks: Item 222 only.

Ordering reason: this entry sits in the later half of the presentation order. Its third option needs thresholds and pairs that no source states, so it needs a scope judgement rather than a tap.

#### Settlement under Captain JP's pass 2 grant: DQ-043

Settled by: The Manager (Muse), under Captain JP's pass 2 grant, in her words: "Do another high discernment pass. I do not want the system to cheat itself or agents to cheat the system plus all the other stuff I said before."

Governing standard: the anti-cheat test first, that the system must not cheat itself and agents must not cheat the system, then Captain JP's settlement philosophy, security first, quality second, speed last, strict reading where workable unless it adds a huge build time, workable reading where strict is unworkable or too costly, neither good stays hers, and genuine redundancy removed with the surviving passage named, with DQ-138, the corpus gate governs over cost, and DQ-139, clashes decided by discernment on the merits and never by recency.

Settlement: No seat table is created for shadow pattern duties. Shadow duties stay assigned directly to the existing roles under the Step 9 group G11 mapping, one holder per duty, and no duty is merged into another duty under one holder. A duty a build cannot staff is marked as a gap with its reason and its fill trigger.

Deciding ground: anti-cheat, system side.

Landing: RECORD-ONLY. No document edit was made for this settlement.

Flag recorded: the small team cost pull toward mergers; anti-cheat and the gate governed.

Status: SETTLED by the Manager under the pass 2 grant, not ruled by Captain JP. This item is settled.

### DQ-044: Anton Item 223 (D-39), shadow roles in skills matrices and interview loops

Status: Banked

Owner of record: Decision-queue Clerk

Source: 01-anton-architecture-patterns.md, global Item 223, local item D-39.

The question: Should the six shadow pattern disciplines be listed with the same weight as the listed patterns in skills matrices and interview loops?

The options, stated plainly:

- No personnel listing from the flow: the shadow disciplines are marked as gap checks in design briefs, as ruled in this step, and no skills matrix or interview loop is amended by the flow.
- Listing adopted outside the flow: the listing is adopted as an estate practice by a separate instrument, in the same manner as the second option at DQ-042.
- Listing adopted in the flow: the flow states the listing and its weight, with the matrix and loop surfaces named in the ruling.

Cost of deciding late: low. The design gap check that carries the substance of the shadow disciplines is landed and runs without any personnel listing.

What it blocks: Item 223 only.

Ordering reason: this entry sits near the top of the presentation order, beside DQ-042, whose answer will likely settle its shape as well. It is a single scope choice.

#### Settlement under Captain JP's grant: DQ-044

Settled by: The Manager (Muse), under Captain JP's grant, in her words: "Go ahead and answer any of them yourself that seems simple enough. I care about security and quality over speed, i don't want things to be too strict that they're impossible, but they should be relatively strict to the standards they hold."

Strictness rule, in Captain JP's words: "If the stricter setting is not workable, then go with the workable. If the strict setting is workable go with it unless it adds a huge build time."

Settlement: The flow amends no skills matrix and no interview loop. The six shadow disciplines stay as they were ruled in Step 9: named Designer duties under group G11, checked in design briefs, or marked as a gap with a reason in the brief.

Deciding limb: strict workable. Source of settlement text and limb: classify-a.md and refinement-abd.md Part 1 limb audit.

Status: SETTLED by the Manager under the grant, not ruled by Captain JP. This item is settled.

### DQ-045: Anton Item 235 (D-51), patterns and shadow roles held as team seats with auditable coverage

Status: Banked

Owner of record: Decision-queue Clerk

Source: 01-anton-architecture-patterns.md, global Item 235, local item D-51. This entry restates, from the elaboration part of the source, the same seat system question prepared at DQ-037 from the selection part of the source. The two entries are kept separate because each conflict item carries its own entry; the Decision-queue Clerk may present them together, and one ruling may answer both, recorded against each.

The question: Should the full pattern set, plus the six shadow disciplines, be held as team seats with duties, rituals, and artefacts, so that a team can state which seats are filled, which are deliberately empty, and what trigger fills an empty seat?

The options, stated plainly:

- No seat system: as in the first option at DQ-037.
- Duty layer only: as in the second option at DQ-037, with coverage stated as which existing role holds each duty for the build, and gaps marked with their fill triggers in the brief.
- Full seat system: as in the third option at DQ-037.

Cost of deciding late: low, for the reason stated at DQ-037. Coverage in substance already exists: a build brief under this ruling set marks each pattern duty area as held by its mapped role or as a gap with a trigger.

What it blocks: Item 235 only, in addition to the items listed at DQ-037.

Ordering reason: this entry sits near the end of the presentation order, beside DQ-037, and should be answered with it or immediately after it. Answering one and not the other would leave the same question open under a second number.

#### Settlement under Captain JP's pass 2 grant: DQ-045

Settled by: The Manager (Muse), under Captain JP's pass 2 grant, in her words: "Do another high discernment pass. I do not want the system to cheat itself or agents to cheat the system plus all the other stuff I said before."

Governing standard: the anti-cheat test first, that the system must not cheat itself and agents must not cheat the system, then Captain JP's settlement philosophy, security first, quality second, speed last, strict reading where workable unless it adds a huge build time, workable reading where strict is unworkable or too costly, neither good stays hers, and genuine redundancy removed with the surviving passage named, with DQ-138, the corpus gate governs over cost, and DQ-139, clashes decided by discernment on the merits and never by recency.

Settlement: The full pattern set and the six shadow disciplines are not held as team seats. Coverage is stated in the existing form: each duty area is held by the existing role named in the Step 9 group G11 mapping, or the brief marks it as a gap with its reason and its fill trigger. No seat is recorded as deliberately empty.

Deciding ground: anti-cheat, system side.

Landing: RECORD-ONLY. No document edit was made for this settlement.

Status: SETTLED by the Manager under the pass 2 grant, not ruled by Captain JP. This item is settled.

### DQ-046: Anton Item 236 (D-52), a seat table adopted at a scale the team can staff

Status: Banked

Owner of record: Decision-queue Clerk

Source: 01-anton-architecture-patterns.md, global Item 236, local item D-52.

The question: Should a pattern duty table be sized to what a team can staff, with duties merged rather than left unfilled where a team cannot staff the full table?

The options, stated plainly:

- No sizing rule: every build assigns the full duty set to its existing roles, and a duty a build cannot staff is recorded as a gap with its fill trigger, never merged.
- Sizing without mergers: a build may record a reduced duty set for its scope, naming each duty it does not take and the trigger that would add it, with no duty merged into another.
- Sizing with mergers: a build may merge duties under one holder, with the permitted mergers and the size measure named in the ruling.

Cost of deciding late: low. Gap recording already handles the small team case honestly, by naming what is not held instead of merging it silently.

What it blocks: Item 236 only.

Ordering reason: this entry sits in the later half of the presentation order, after DQ-037 and DQ-043, because its merger option depends on both a table existing and a merger form being chosen.

#### Settlement under Captain JP's pass 2 grant: DQ-046

Settled by: The Manager (Muse), under Captain JP's pass 2 grant, in her words: "Do another high discernment pass. I do not want the system to cheat itself or agents to cheat the system plus all the other stuff I said before."

Governing standard: the anti-cheat test first, that the system must not cheat itself and agents must not cheat the system, then Captain JP's settlement philosophy, security first, quality second, speed last, strict reading where workable unless it adds a huge build time, workable reading where strict is unworkable or too costly, neither good stays hers, and genuine redundancy removed with the surviving passage named, with DQ-138, the corpus gate governs over cost, and DQ-139, clashes decided by discernment on the merits and never by recency.

Settlement: No sizing rule and no merger rule is created for pattern duties. Every build takes the full duty set as mapped to the existing roles in Step 9 group G11, and a duty it cannot staff is recorded as a gap with its reason and its fill trigger. A duty is never merged into another duty and never dropped without a record.

Deciding ground: anti-cheat, system side.

Landing: RECORD-ONLY. No document edit was made for this settlement.

Flag recorded: cost pull, governed as DQ-043.

Status: SETTLED by the Manager under the pass 2 grant, not ruled by Captain JP. This item is settled.

### DQ-047: Anton Item 237 (D-53), quarterly rotation of pattern duty holders

Status: Banked

Owner of record: Decision-queue Clerk

Source: 01-anton-architecture-patterns.md, global Item 237, local item D-53.

The question: Should holders of pattern duties rotate on a fixed cadence, with the gatekeeping duty rotating slowest of all?

The options, stated plainly:

- No rotation: as in the first option at DQ-038.
- Rotation at build boundaries only: duty labels, if any form of them is adopted, change hands only between builds, never inside a build, with handovers recorded in the pattern decision ledger.
- Fixed cadence rotation: rotation inside a build on the cadence named in the ruling, with the gatekeeping duty on the slower cadence named in the ruling.

Cost of deciding late: low. Standing roles held for the whole build are the current form, and the ledger handover record ruled in this step preserves decision history across any later change of holder.

What it blocks: Item 237 only. It is the elaboration restatement of the question at DQ-038, and one ruling may answer both, recorded against each.

Ordering reason: this entry sits in the later half of the presentation order, beside DQ-038, and depends on DQ-037 in the same way.

#### Settlement under Captain JP's pass 2 grant: DQ-047

Settled by: The Manager (Muse), under Captain JP's pass 2 grant, in her words: "Do another high discernment pass. I do not want the system to cheat itself or agents to cheat the system plus all the other stuff I said before."

Governing standard: the anti-cheat test first, that the system must not cheat itself and agents must not cheat the system, then Captain JP's settlement philosophy, security first, quality second, speed last, strict reading where workable unless it adds a huge build time, workable reading where strict is unworkable or too costly, neither good stays hers, and genuine redundancy removed with the surviving passage named, with DQ-138, the corpus gate governs over cost, and DQ-139, clashes decided by discernment on the merits and never by recency.

Settlement: Pattern duty holders do not rotate on a quarterly cadence or on any fixed cadence. Each duty stays with the existing role that holds it for the whole build, including the gatekeeping duty at the pattern gate. Any later change of a pattern duty holder is recorded in the pattern decision ledger under its handover form.

Deciding ground: anti-cheat, agent side.

Landing: RECORD-ONLY. No document edit was made for this settlement.

Flag recorded: as DQ-038, the familiarity argument for rotation pulled the other way; the anti-cheat test governed.

Status: SETTLED by the Manager under the pass 2 grant, not ruled by Captain JP. This item is settled.

### DQ-048: Anton Item 241 (D-57), collective adoption decisions under the governor

Status: Banked

Owner of record: Decision-queue Clerk

Source: 01-anton-architecture-patterns.md, global Item 241, local item D-57.

The question: Should pattern adoption decisions be collective decisions of the advising roles, rather than a gate decision taken by the named gatekeeper under the existing gate rule?

The options, stated plainly:

- Named gatekeeper decides: the existing gate rule stands. Advising roles advise and record, and the Auditor, as pattern gatekeeper, issues the one outcome and owns the gate record.
- Collective with a named chair: the advising roles decide together, the gatekeeper chairs and records, and the ruling names how a split decision is settled and who answers for the outcome.
- Collective by consent: an adoption proceeds only with no advising role objecting, and an objection is recorded as a Hold with its release condition.

Cost of deciding late: low in time, high in clarity if left unstated at a live gate. The gate as landed runs in the first option form, so work proceeds; the cost is that the source contrary form stays on record as unruled until this entry is answered.

What it blocks: Item 241 only. No other gate item waits on it, because the gate form itself is landed under the first option as the existing rule.

Ordering reason: this entry sits at the top of the presentation order. It is a straight choice between the existing named decider form and two stated collective forms, and it can be answered in one tap.

#### Settlement under Captain JP's grant: DQ-048

Settled by: The Manager (Muse), under Captain JP's grant, in her words: "Go ahead and answer any of them yourself that seems simple enough. I care about security and quality over speed, i don't want things to be too strict that they're impossible, but they should be relatively strict to the standards they hold."

Strictness rule, in Captain JP's words: "If the stricter setting is not workable, then go with the workable. If the strict setting is workable go with it unless it adds a huge build time."

Settlement: Pattern adoption decisions are not collective. The Auditor, as pattern gatekeeper, holds the gate, issues exactly one outcome from the rule R-51 vocabulary, and owns the gate record. Advising roles advise and record, and their advice does not make the decision collective.

Deciding limb: strict workable. Source of settlement text and limb: classify-a.md and refinement-abd.md Part 1 limb audit.

Status: SETTLED by the Manager under the grant, not ruled by Captain JP. This item is settled.

### DQ-049: Anton Item 250 (D-66), removals credited in performance narratives

Status: Banked

Owner of record: Decision-queue Clerk

Source: 01-anton-architecture-patterns.md, global Item 250, local item D-66.

The question: Should removals be credited in performance narratives, as team facts, in addition to their credit in the complexity ledger?

The options, stated plainly:

- Ledger credit only: removal credit lives in the pattern decision ledger and in removal review records, as landed in this step, and no performance narrative is written or amended by the flow.
- Team narrative in build records only: the build closing narrative, kept by the Continuity Keeper, names removals as team facts beside adoptions, and no personnel narrative is touched.
- Performance narratives included: removals are credited in performance narratives as team facts, with the narrative surface and its owner named in the ruling, and the bar on any individual refusal score kept in every option.

Cost of deciding late: low. Removal credit in the ledger, which is the record other decisions read, is landed and complete without any narrative form.

What it blocks: Item 250 only, and only in its narrative part. Its ledger part is landed as a Duplicate at Items 210 and 322.

Ordering reason: this entry sits in the first half of the presentation order. Two of its three options change nothing in any build record, so it can be answered quickly, and its third option is plainly marked as the one that would open a new surface.

#### Settlement under Captain JP's grant: DQ-049

Settled by: The Manager (Muse), under Captain JP's grant, in her words: "Go ahead and answer any of them yourself that seems simple enough. I care about security and quality over speed, i don't want things to be too strict that they're impossible, but they should be relatively strict to the standards they hold."

Strictness rule, in Captain JP's words: "If the stricter setting is not workable, then go with the workable. If the strict setting is workable go with it unless it adds a huge build time."

Settlement: Removals are credited as team facts in build records only: in the pattern decision ledger and, beside adoptions, in the build closing narrative kept by the Continuity Keeper. No removal is credited in any personnel or performance narrative, and no removal is ever recorded as an individual refusal score.

Deciding limb: strict workable. Source of settlement text and limb: classify-a.md and refinement-abd.md Part 1 limb audit.

Status: SETTLED by the Manager under the grant, not ruled by Captain JP. This item is settled.

### DQ-050: Manager spin ups, cap, budget gate, or recorded work product

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q1.

The question: Should spin ups under R-50 be bound by the Step 3 budget, or carry any cap, budget gate, or minimum recorded work product per spin up? The authority itself is a ruling of Captain JP and is not treated as a defect.

Cost of deciding late: low to medium. R-50 spin ups continue under the standing authority in the meantime; the cost is that spend and staffing can grow with no cap, gate, or work product floor ruled.

What it blocks: any cap, budget gate, or minimum work product rule for R-50 spin ups. It blocks no other item.

Ordering reason: this entry is a short scope choice about limits on an existing power, and can be answered without naming a project or a person.

#### Assessment and settlement under DQ-143

Assessed under Captain JP's money ruling, DQ-143, in her words: "Use discernment if you should ask me." This item falls on the mechanics side of the line that ruling draws. It commits no funds and sets or changes no budget, price, stake, or money obligation: its budget limb only enforces the budget already set for a build, and its remaining limbs are a cap choice and a record requirement.

Settlement: Settled by the Manager (Muse) as a Manager settlement under DQ-143. Spin ups under R-50 are bound by the build's budget as set for the build: the cost of a spin up counts against that budget, and a spin up that would carry the build's spend past its set budget is not made under the R-50 authority. No separate cap on the number of spin ups stands; a cap figure would set a new money limit, which is not mechanics, and the budget gate already bounds the spend. The roster record of a spin up names the work product the spin up is charged to produce, and whether that work product was produced is judged at the Auditor's step check. Landed at LEVEL-1, R-50. Corpus gate under DQ-002: PASS, recorded in money-ruling-trace.md. This item is settled and closed as a Manager settlement under DQ-143; the Status line above is left as it stands, and this block is the record of the settlement.

### DQ-051: Distinctness against independence of judgement

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q2.

The question: Should any seats, in audit or verification, also require independence of direction, instruction, or drafting, beyond the distinct agent and decorrelation statements the set now carries at R-1, R-80, R-88, DQ-011, and DQ-014?

Cost of deciding late: medium. Audit and verification proceed on distinctness and decorrelation alone; the cost is that a stronger independence claim cannot be made or required until this entry is answered.

What it blocks: any independence of judgement requirement for audit or verification seats, beyond the statements already in the set.

Ordering reason: this entry is a deep ruling about what audit independence means in this flow, so it sits in the later half rather than in a burst of short answers.

#### Settlement under Captain JP's grant: DQ-051

Settled by: The Manager (Muse), under Captain JP's grant, in her words: "Go ahead and answer any of them yourself that seems simple enough. I care about security and quality over speed, i don't want things to be too strict that they're impossible, but they should be relatively strict to the standards they hold."

Strictness rule, in Captain JP's words: "If the stricter setting is not workable, then go with the workable. If the strict setting is workable go with it unless it adds a huge build time."

Settlement: No independence of direction, instruction, or drafting requirement is added for any audit or verification seat. Those seats require what the set now states: distinct agents and decorrelation under rules R-1, R-80, and R-88, with the attestation claim kept at its R-88 bound, a strong claim only that separate processes ran, records were chained, and no layout step is missing.

Deciding limb: strict unworkable. Source of settlement text and limb: refinement-abd.md Part 2.

Status: SETTLED by the Manager under the grant, not ruled by Captain JP. This item is settled.

### DQ-052: Withheld records, consequence where a disclaimed outcome is obtained by withholding

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q3.

The question: What consequence, if any, should attach where an audited party obtains a no verdict outcome (UNVERIFIABLE, or a modified verdict under R-65 and R-69) by withholding records or preventing examination, rather than by the evidence genuinely running out?

Cost of deciding late: medium. Such outcomes stand with no stated consequence in the meantime, so the incentive the question names stays unaddressed.

What it blocks: any consequence rule for a disclaimed or modified verdict obtained by withholding records or preventing examination.

Ordering reason: this entry needs a considered consequence choice, not a tap, because it governs how audited parties are treated when examination is blocked.

#### Ruling: DQ-052

Ruled by: Captain JP

Ruling text: "Count it as a fail."

The question as put to her: "A team hides its records, so the check ends with 'cannot verify.' What happens?" with answers "Count it as a fail / No consequence".

Ruling outcome: A no verdict outcome (UNVERIFIABLE, or a modified verdict under R-65 and R-69) obtained by withholding records or preventing examination is recorded and treated as a FAIL, not as a disclaimed or unverifiable outcome. Genuine exhaustion of evidence, where nothing was withheld and examination was not prevented, keeps the disclaimed outcome as the documents already provide.

Where the ruling landed: LEVEL-1-STANDING.md, at R-3 (the UNVERIFIABLE state), R-65 (audit evidence), and R-69 (scope limitation). Trace: dq-052-trace.md in this directory.

Status: RULED, closed. This item is ruled.

### DQ-053: Manager end of step additions, should additions pass a trace, re-rule of DQ-031

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q4.

The question: This entry asks Captain JP to re-rule her own earlier ruling at DQ-031. DQ-031 ruled that Manager additions at the end of a step never reopen a closed step trace and the Auditor judges the step as it stands with its additions. Should that ruling change, so material added after a step fold-in trace at 100 percent LANDED is itself traced, or does the ruled form stand?

Cost of deciding late: low. The DQ-031 form stands and steps close under it in the meantime; the cost is only that the challenged form stays in force until Captain JP confirms or changes it.

What it blocks: any change to the DQ-031 treatment of Manager end of step additions. It blocks no step closure under the current ruling.

Ordering reason: this entry sits last among short items in its group. It asks Captain JP to re-rule her own earlier ruling, so it needs her full attention rather than a burst answer.

#### Assessment under DQ-148 (ruling by Captain JP: "Use desernment")

The challenge does not hold. DQ-031's form already carries its safeguard in the open: additions are recorded in the step record as the Manager's additions at the time they are made (R-91, and R-50 roster recording), and the Auditor judges the finished step as it was actually staffed, additions included. A fold-in trace is a check over a stage's inputs at closure; additions made inside the step are part of the step the Auditor rules on, not inputs carried past the trace. Reopening a closed trace for later additions would also cut against R-3's terminal state rule. The earlier ruling stands. Closed as decided under DQ-148.

### DQ-054: Tier size test, should few, tiny and small be given measures

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q5.

The question: Should the R-4 size test terms be given numbers, named thresholds, or worked examples that bind future builds, or an interpreter other than the Project Manager, or should tier selection remain a recorded judgement call?

Cost of deciding late: low. Tier selection continues as a recorded judgement call; the cost is that the size words carry no binding measure from build to build.

What it blocks: any binding measure, threshold, worked example, or named interpreter for the R-4 size test terms few, tiny, and small.

Ordering reason: this entry is a scope judgement about whether to fix numbers that no source supplies, so it sits in the later half.

#### Ruling by Captain JP

Question as put on the Questions space: "The size test picks a build's tier. Should its measures be fixed numbers, or judged case by case?" Her answer, in her words: "Fixed numbers."

Ruled: the measures of the R-4 size test are fixed numbers. The flow documents carry no numbers for the measures today: R-4 speaks of a few modules, a tiny product, and a single small module set in words only. No value is invented here. The ruling is landed in R-4 in LEVEL-1-STANDING.md as fixing the form: each measure's number is named by Captain JP and recorded in the rule when named. Closed as ruled; the numbers themselves stand hers to name.

#### Completion under Captain JP's further answer at DQ-054

Question as put on the Questions space: "You ruled the size test uses fixed numbers. The test today only says few, tiny, and small. What numbers should those be?" Her answer, in her words: "Use decernment"

Completed by: The Manager (Muse), under that answer, setting the values by discernment on the strict workable side, consistent with the fill in discipline at DQ-141. Each value is recorded as set by the Manager under her answer, so she can overrule any of them. The values set are: few is 6 modules (Medium is a few modules only, at most 6 modules, and more than 6 modules is more than a few and puts the build at High at minimum, as R-4 already structures it); small is a module set of at most 3 modules; tiny is a single small module set, at most 3 modules forming one deployable unit (R-4 defines tiny as a single small module set, so tiny takes the bound of small). Landed in LEVEL-1-STANDING.md at R-4, replacing the sentence that left each number to be named. This entry was already closed as ruled with the numbers hers to name; this block completes that reservation under her further answer. Closed.

### DQ-055: Skipping a move, who judges cost against return, and who classifies a move as unskippable

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q6.

The question: Should a maker, approver, or classifier be named for skip judgements, and should the skip checklist bar widen beyond irreversible decisions?

The options, stated plainly:

- Name the Auditor as approver.
- Name the step record keeper as classifier, subject to board review.
- Leave the doctrine as written.

Cost of deciding late: low. Skips proceed under the doctrine as written, with no named approver or classifier.

What it blocks: any named approver or classifier for skip judgements, and any widening of the skip checklist bar beyond irreversible decisions.

Ordering reason: this entry is a short choice among three stated options, and can be answered in one line.

#### Settlement under Captain JP's grant: DQ-055

Settled by: The Manager (Muse), under Captain JP's grant, in her words: "Go ahead and answer any of them yourself that seems simple enough. I care about security and quality over speed, i don't want things to be too strict that they're impossible, but they should be relatively strict to the standards they hold."

Strictness rule, in Captain JP's words: "If the stricter setting is not workable, then go with the workable. If the strict setting is workable go with it unless it adds a huge build time."

Settlement: The skip doctrine stands as written, with no separate approver or classifier named: a skip stands only on the recorded judgement that the move would cost more than it returns, with its reason and its return trigger in the step record and its summary before the step review board. The checklist bar is not widened, because closure evidence, moves a numbered rule requires, and the R-89 moves on an irreversible decision are already unskippable. Lands: LEVEL-1-STANDING.md, the Skipping a move doctrine and the Skip checklist, read with R-89. Implementation: small. No document text needs to change; the settlement is recorded against the doctrine as written.

Deciding limb: strict workable. Source of settlement text and limb: classify-b.md and refinement-abd.md Part 1 limb audit.

Status: SETTLED by the Manager under the grant, not ruled by Captain JP. This item is settled.

### DQ-056: R-57 tailoring, what makes a criterion must-meet

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q7.

The question: Should the must-meet category in R-57 be defined, and by whom, with a reasons requirement and a timing for the tailoring record?

Cost of deciding late: low. Tailoring proceeds without a definition of must-meet; the cost is that the category is applied by judgement until it is defined.

What it blocks: any definition of the R-57 must-meet category, its defining authority, and its reasons and timing requirements.

Ordering reason: this entry is a definitional ruling with no definition supplied in any source, so it sits in the later half.

#### Fill-in under Captain JP's ruling at DQ-141: DQ-056

Settled by: The Manager (Muse), as a fill-in under Captain JP's ruling at DQ-141, in her words: "You fill it in, strict side."

Fill-in: A tailoring criterion is must-meet when meeting it is required for the step to close honestly: it guards a gate or closure bar, a security or record honesty control, or the presence of a standing role. The Project Manager defines the must-meet set for a build at tailoring time. Each designation carries a one line reason in the tailoring record. The tailoring record, with its must-meet set and reasons, is recorded before the first tailored step opens; a designation added later is recorded when made and never applies backward to a step already closed.

Lands: LEVEL-1-STANDING.md, R-57, at the end of the rule.

Status: SETTLED as a Manager fill-in under DQ-141, not ruled by Captain JP. The value set stands until Captain JP overrules it.

### DQ-057: Halt, what bounds an atomic step, and who judges safe to finish and unable to freeze

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q8.

The question: Should a size, duration, or content bound be set for an atomic step under R-2, and a named judge for the safe to finish and unable to freeze calls?

Cost of deciding late: medium. Halts proceed with no bound on an atomic step and no named judge for those two calls, so a halt can wait on an unbounded unit.

What it blocks: any bound for an atomic step under R-2, and any named judge for the safe to finish and unable to freeze calls.

Ordering reason: this entry needs bounds and a judge that no source states, so it sits in the later half.

#### Fill-in under Captain JP's ruling at DQ-141: DQ-057

Settled by: The Manager (Muse), as a fill-in under Captain JP's ruling at DQ-141, in her words: "You fill it in, strict side."

Fill-in: An atomic step is the smallest unit of work that ends in a record: one agent's continuous run on one assignment, producing one output or one record, with no gate inside it; nothing larger counts as atomic. The Auditor judges the safe to finish and unable to freeze calls at a halt, and the judgement is recorded in the halt record.

Lands: LEVEL-1-STANDING.md, R-2, at the end of the rule.

Status: SETTLED as a Manager fill-in under DQ-141, not ruled by Captain JP. The value set stands until Captain JP overrules it.

### DQ-058: Flag against halt, where is the line, and who may cancel a flag on their own build

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q9.

The question: Should a classifier or test state the line between an R-84 flag level concern and an R-82 halt obligation, and should the first responder for a flag on a build be someone other than that build Manager?

Cost of deciding late: medium. Flags and halts proceed without a stated line between them, and the build Manager remains the first responder for a flag on their own build.

What it blocks: any classifier or test for the flag against halt line, and any rule moving first response for a flag away from that build Manager.

Ordering reason: this entry is a short choice in form, but it governs halt obligations, so it sits in the middle of the order.

#### Fill-in under Captain JP's ruling at DQ-141: DQ-058

Settled by: The Manager (Muse), as a fill-in under Captain JP's ruling at DQ-141, in her words: "You fill it in, strict side."

Fill-in: The line is this test: a concern is a halt obligation when work continuing could close a step on an unmet bar, falsify or lose a record, or breach a security control; anything short of that is a flag. The first responder for a flag on a build is the Auditor, never that build's own Manager.

Lands: LEVEL-1-STANDING.md, R-84, at the end of the rule.

Status: SETTLED as a Manager fill-in under DQ-141, not ruled by Captain JP. The value set stands until Captain JP overrules it.

### DQ-059: Label only sanctions, should reporting carry a stopping consequence

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q10.

The question: Should any of the label only reports (unstaffed standing role, stale killer item list, unconverted register, watching only role, missed gate gaming exercise) bar the next step, or is a label in the record the intended whole consequence?

Cost of deciding late: low. Each named report carries a label only in the meantime, exactly as the question describes.

What it blocks: any stopping consequence for the five named label only reports.

Ordering reason: this entry is a single choice, label only or a bar, and can be answered in one tap.

Ruling in principle, added on the ruling: RULED in principle by Captain JP. The question as put to her: "Some problems only get a warning label in the record. Nothing stops. Should a warning ever stop the next step?" Her answer, quoted exactly: "Some warnings stop the step."

Ruling outcome: some of the five label only reports named in this entry carry a stopping consequence and bar the next step; for those reports the label alone is not the whole consequence. Which of the five reports stop is being decided with Captain JP question by question, so this entry stays open in part: each per-report decision will be added to this entry as it is ruled, and the document landings for each report follow as that report is decided. No document change is landed under this ruling in principle yet.

Per-report decision, unstaffed standing role: RULED by Captain JP. The question as put to her: "First warning on the list: 'a standing role has nobody in it.' Does that one stop the step?" Her answer, quoted exactly: "Yes, it stops the step."

Outcome of this decision: the unstaffed standing role report carries a stopping consequence and bars the next step until the role is staffed; the label alone is not its whole consequence. Landed in LEVEL-1-STANDING.md at R-5, where the unstaffed report is defined. This entry stays open in part for the remaining four reports: stale killer item list, unconverted register, watching only role, and missed gate gaming exercise.

Per-report decision, stale killer item list: RULED by Captain JP. The question as put to her: "Warning 2: 'the danger list is out of date.' Does that one stop the step?" Her answer, quoted exactly: "Yes, it stops the step."

Outcome of this decision: the stale killer item list report carries a stopping consequence and bars the next step until the list is current, that is, until the owner's review of the list is recorded; the label alone is not its whole consequence. Landed in LEVEL-1-STANDING.md at R-63, where list maintenance and the stale report are defined. This entry stays open in part for the remaining three reports: unconverted register, watching only role, and missed gate gaming exercise.

Per-report decision, unconverted register: RULED by Captain JP. The question as put to her: "Warning 3: 'a record list was never converted into the system.' Does that one stop the step?" The answers offered were "No, label only" and "Yes, it stops the step", and the Manager's recommendation put to her with the question was label only. Her answer, quoted exactly: "Yes, it stops the step." This decision went against the Manager's recommendation; her ruling governs.

Outcome of this decision: the unconverted register report carries a stopping consequence and bars the next step until the register is converted; the label alone is not its whole consequence. Landed in LEVEL-1-STANDING.md at R-63, where the unconverted register report is defined. This entry stays open in part for the remaining two reports: watching only role, and missed gate gaming exercise.

Per-report decision, watching only role: RULED by Captain JP. The question as put to her: "Warning 4: 'a role is filled, but the person only watches and does no work.' Does that one stop the step?" Her answer, quoted exactly: "Yes, it stops the step."

Outcome of this decision: the watching only role report carries a stopping consequence and bars the next step until the role is genuinely held and worked; the label alone is not its whole consequence. Landed in LEVEL-1-STANDING.md at R-84, where the watching only report is defined in the teeth test. This entry stays open in part for the last report: missed gate gaming exercise.

Per-report decision, missed gate gaming exercise: RULED by Captain JP. The question as put to her: "Warning 5, the last one: 'the practice drill for attacking the gates was missed.' Does that one stop the step?" Her answer, quoted exactly: "Yes, it stops the step."

Outcome of this decision: the missed gate gaming exercise report carries a stopping consequence and bars the next step until the exercise is run and recorded; the label alone is not its whole consequence. Landed in LEVEL-3-TEAMS.md at R-210, where the gate gaming exercise and its recording in the production phase record are defined.

Item closed: all five reports named in this entry are now decided, and all five stop. The unstaffed standing role report, the stale killer item list report, the unconverted register report, the watching only role report, and the missed gate gaming exercise report each carry a stopping consequence and bar the next step, and for none of them is the label the whole consequence. This item stands RULED in full and closed, subject to the five landings completing; the five landings are traced in dq-059-trace.md.

### DQ-060: R-75 deviations, who validates a SHOULD deviation, and who arbitrates force from context

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q11.

The question: Should a validator be named for SHOULD deviations recorded under R-75, or a rule given for contested context? The language form itself was settled at DQ-029.

Cost of deciding late: low. Deviations are recorded under R-75 with no named validator and no rule for contested context.

What it blocks: any named validator for R-75 SHOULD deviations, and any arbitration rule for force from context.

Ordering reason: this entry is a short naming choice, and can be answered in one line.

#### Fill-in under Captain JP's ruling at DQ-141: DQ-060

Settled by: The Manager (Muse), as a fill-in under Captain JP's ruling at DQ-141, in her words: "You fill it in, strict side."

Fill-in: The Auditor validates SHOULD deviations recorded under R-75, at the step's review board, and the validation is recorded in the step record. Where the force of a requirement from context is contested, the Auditor arbitrates; the reading adopted and the arbitration are recorded in the step record, and the reading stands for that step only.

Lands: LEVEL-1-STANDING.md, R-75, at the end of the rule.

Status: SETTLED as a Manager fill-in under DQ-141, not ruled by Captain JP. The value set stands until Captain JP overrules it.

### DQ-061: Decision queue ordering, should old items age upward

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q12.

The question: Should an ageing or escalation rule be added to the easy first ordering of the decision queue, which is Captain JP own standing instruction?

Cost of deciding late: low. The queue keeps its easy first ordering with no ageing; the cost is that old items can stay low in the order indefinitely.

What it blocks: any ageing or escalation rule for decision queue ordering.

Ordering reason: this entry touches Captain JP own standing instruction for this queue, so it sits in the later half despite its short form.

#### Assessment under DQ-148 (ruling by Captain JP: "Use desernment")

The challenge does not hold. The easy first ordering is Captain JP's own standing instruction for her queue, and her intake ruling at DQ-106 now governs the other end of the problem: questions are held until she asks, the Manager answers most questions itself, and nothing is defaulted for want of a ruling. An ageing rule would push old items upward at her on a clock, against the intake ruling's direction. The earlier instruction stands. Closed as decided under DQ-148.

### DQ-062: Red sub-lenses, should each carry its own technique and coverage standard

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q13.

The question: Should per class standards (technique, input class, timing threshold, coverage test, evidence standard) be written into the five Red agent files, or is the shared template with a named sub-lens the intended form?

Cost of deciding late: low. The Red files keep the shared template form; the cost is that coverage per class stays unstated.

What it blocks: any per class technique and coverage standards in the five Red agent files.

Ordering reason: this entry is a single form choice, shared template or per class standards, and can be answered in one line.

#### Settlement under Captain JP's grant: DQ-062

Settled by: The Manager (Muse), under Captain JP's grant, in her words: "Go ahead and answer any of them yourself that seems simple enough. I care about security and quality over speed, i don't want things to be too strict that they're impossible, but they should be relatively strict to the standards they hold."

Strictness rule, in Captain JP's words: "If the stricter setting is not workable, then go with the workable. If the strict setting is workable go with it unless it adds a huge build time."

Settlement: The shared template with a named sub-lens stands as the Red form. No per class technique or coverage standard is written into the five Red agent files, and the done condition already in those files stands as the coverage control: the whole assigned slice is checked, with evidence.

Deciding limb: strict unworkable. Source of settlement text and limb: refinement-abd.md Part 2.

Status: SETTLED by the Manager under the grant, not ruled by Captain JP. This item is settled.

### DQ-063: Red files, the line between a serious issue routed through White and an urgent issue handed over at once

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q14.

The question: Should a distinguishing test be stated for serious against urgent in the Red files step 5 and Handoff routing?

Cost of deciding late: low to medium. Routing proceeds by holder judgement; the cost is that an urgent issue may be routed as merely serious, or the reverse, with no test to check against.

What it blocks: any distinguishing test for serious against urgent in Red file routing.

Ordering reason: this entry is a short choice about whether a test is needed, and can be answered in one line.

#### Settlement under Captain JP's grant: DQ-063

Settled by: The Manager (Muse), under Captain JP's grant, in her words: "Go ahead and answer any of them yourself that seems simple enough. I care about security and quality over speed, i don't want things to be too strict that they're impossible, but they should be relatively strict to the standards they hold."

Strictness rule, in Captain JP's words: "If the stricter setting is not workable, then go with the workable. If the strict setting is workable go with it unless it adds a huge build time."

Settlement: An issue is urgent, and is handed to the Auditor and the Project Manager at once, where it concerns safety or honesty; every other serious issue, including an issue that belongs to another lens, goes to the owning colour through White for triage. That line is the one the Red files already draw between step 5 and the Handoff section, stated here as one test. Lands: the five Red agent files (red-abuse-cases.md, red-boundary-attacks.md, red-failure-injection.md, red-hostile-inputs.md, red-race-and-timing.md), step 5 and the Handoff section of each. Implementation: small. One clarifying sentence in each of the five files, in the same words.

Deciding limb: strict workable. Source of settlement text and limb: classify-b.md and refinement-abd.md Part 1 limb audit.

Status: SETTLED by the Manager under the grant, not ruled by Captain JP. This item is settled.

### DQ-064: R-7 bounded exception, should the Manager discretion grant carry scope, limit or expiry

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q15.

The question: Should the discretion grant under DQ-016 (no fixed named class, decided on a live case, recorded CLOSED-QUALIFIED, no precedent) carry a stated scope, a per build limit, or an expiry? The grant is Captain JP own.

Cost of deciding late: medium. The grant continues with no stated scope, limit, or expiry beyond the DQ-016 form.

What it blocks: any scope, per build limit, or expiry on the R-7 bounded exception discretion grant.

Ordering reason: this entry concerns the bounds of Captain JP own grant, so it sits in the later half despite its short form.

#### Assessment under DQ-148 (ruling by Captain JP: "Use desernment")

The challenge does not hold. The DQ-016 grant's bounds are already its substance: no fixed class of case, decided only on a live case, recorded with the four elements, no precedent set, and an anomaly in how closure evidence was produced never qualifies. A stated scope, a per build limit, or an expiry would either restate those bounds or bar a live case the grant exists for, forcing a stage to fail on an anomaly the case itself could carry. The grant stands as ruled at DQ-016. Closed as decided under DQ-148.

### DQ-065: Qualified live proof, should PASS-QUALIFIED ever suffice at the release gate

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q16.

The question: Should a PASS-QUALIFIED live proof, its bound never discharged, suffice for a product to pass the release gate at Step 22, and should a bound carry an expiry or discharge rule? DQ-010 ruled no universal live proof floor, judged claim by claim.

Cost of deciding late: medium to high at a release gate. A qualified proof reaching Step 22 has no ruled answer for whether it suffices, and no expiry or discharge rule for its bound.

What it blocks: any rule on whether PASS-QUALIFIED suffices at the Step 22 release gate, and any expiry or discharge rule for a live proof bound.

Ordering reason: this entry is a deep ruling about the release gate, so it sits near the end of the order.

#### Ruling by Captain JP

Question as put on the Questions space: "A live proof passed with a bound that was never cleared. Can that product pass the release gate?" Her answer, in her words: "Yes, judged case by case."

Ruled: a live proof verdict of PASS-QUALIFIED, its bound named and not discharged, may suffice at the Step 22 release gate, judged case by case on the bound and the claim it qualifies. Landed in LEVEL-2-STEPS.md at R-27, consistently with DQ-010. Closed.

### DQ-066: Grill decisions register, who checks the decider class labels

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q17.

The question: Should grill decision entries be required to quote or link Captain JP recorded delegation words, name an independent checker of the decider class labels, or state a consequence for a mislabel found later?

Cost of deciding late: low to medium. Grill entries proceed with no required quotation, checker, or mislabel consequence, so a wrong decider class label can stand unchecked.

What it blocks: any quotation or link requirement, independent checker, or mislabel consequence for grill decision decider class labels.

Ordering reason: this entry is a short record keeping choice among stated forms, and can be answered in one line.

#### Settlement under Captain JP's pass 2 grant: DQ-066

Settled by: The Manager (Muse), under Captain JP's pass 2 grant, in her words: "Do another high discernment pass. I do not want the system to cheat itself or agents to cheat the system plus all the other stuff I said before."

Governing standard: the anti-cheat test first, that the system must not cheat itself and agents must not cheat the system, then Captain JP's settlement philosophy, security first, quality second, speed last, strict reading where workable unless it adds a huge build time, workable reading where strict is unworkable or too costly, neither good stays hers, and genuine redundancy removed with the surviving passage named, with DQ-138, the corpus gate governs over cost, and DQ-139, clashes decided by discernment on the merits and never by recency.

Settlement: An entry in the grill decisions register that carries the delegated class quotes or links the recorded words of Captain JP that the delegation rests on. An entry with no such quote or link does not carry the delegated class and is entered under the class its record supports. No independent checker of the labels and no consequence for a mislabel found later is settled here, and those two limbs stay banked.

Deciding ground: anti-cheat, agent side, partial settlement.

Landing: LANDED, LEVEL-2 R-14, line 278.

Status: SETTLED IN PART by the Manager under the pass 2 grant, not ruled by Captain JP. The settled limb above is settled. What stays banked: the independent checker of the labels limb and the consequence for a mislabel found later limb stay banked, and this item stays banked for those limbs.

#### Completion under Captain JP's DQ-145 ruling: DQ-066

Completed by: The Manager (Muse), under Captain JP's DQ-145 ruling, in her words: "Yes, finish them that way."

Governing standard: the anti-cheat test first, then Captain JP's settlement philosophy as recorded in the pass 2 settlement above, with DQ-138 and DQ-139.

Completion: The two banked limbs are finished. The independent checker of the decider class labels is the Auditor: before closing Step 4 he checks each label in the grill decisions register against the record the entry cites, and a label its record does not support is re-entered under the class its record supports before the step closes. The consequence for a mislabel found later is this: the mislabel is corrected by a superseding entry that names the original entry and the correct class, the original stands marked corrected and is never edited in place, and the decision carries no force from the wrong class; where the correct class names a different decider, the decision is re-entered under the correct class by that decider, and until it is re-entered no later stage may treat it as decided.

Deciding ground: anti-cheat, agent side. A label nobody checks, with no consequence when it is wrong, lets a decision borrow authority it was never given.

Landing: LANDED, LEVEL-2 R-14. Corpus gate under DQ-002: PASS, recorded in scratch-finishing/gate-record.md.

Status: SETTLED by the Manager, the pass 2 limb under the pass 2 grant and the remaining limbs under DQ-145, not ruled by Captain JP. This item is settled and closed as a Manager completion; Captain JP may overrule it.

### DQ-067: Checklist generation, should the drawer be independent of the step judged, re-rule of the DQ-029 settlement

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q18.

The question: This entry asks Captain JP to re-rule her own earlier settlement at DQ-029. DQ-029 settled R-92 in its reduced form (checklist drawn by the step own record keeper from the step stated preconditions as written). Should the settlement be revisited and an approver of preconditions or killer item exclusions named?

Cost of deciding late: low. The DQ-029 settled form stands and checklists are drawn under it in the meantime.

What it blocks: any change to the DQ-029 settlement for R-92, and any named approver of preconditions or killer item exclusions for checklist generation.

Ordering reason: this entry sits last among short items in its group. It asks Captain JP to re-rule her own earlier settlement, so it needs her full attention rather than a burst answer.

#### Assessment under DQ-148 (ruling by Captain JP: "Use desernment")

The challenge does not hold. R-92 as settled already carries its teeth on the record: the checklist is drawn from the step's stated preconditions, drawing creates no new criteria, the preconditions must predate the judging point, and a pause point reached with a checklist omitting a stated killer precondition does not run. The Auditor then judges the step at its gate against that checklist and the preconditions themselves. Naming a second approver of the preconditions would add a judge of the step's criteria with no failure on the record for it to answer. The DQ-029 settlement stands. Closed as decided under DQ-148.

### DQ-068: Deferred defects, should deferral carry a maximum length, a predating test, or a bar on successor proofs

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q19.

The question: Should any of those limits be ruled for deferral under R-25 (Captain JP ruling or a running live proof protection, gate capped at CLOSED-QUALIFIED)?

Cost of deciding late: medium. Deferrals continue under R-25 with no maximum length, predating test, or bar on successor proofs beyond the qualified gate cap.

What it blocks: any maximum length, predating test, or successor proof bar for R-25 deferral.

Ordering reason: this entry asks for limits no source supplies, so it sits in the later half.

#### Settlement under Captain JP's pass 2 grant: DQ-068

Settled by: The Manager (Muse), under Captain JP's pass 2 grant, in her words: "Do another high discernment pass. I do not want the system to cheat itself or agents to cheat the system plus all the other stuff I said before."

Governing standard: the anti-cheat test first, that the system must not cheat itself and agents must not cheat the system, then Captain JP's settlement philosophy, security first, quality second, speed last, strict reading where workable unless it adds a huge build time, workable reading where strict is unworkable or too costly, neither good stays hers, and genuine redundancy removed with the surviving passage named, with DQ-138, the corpus gate governs over cost, and DQ-139, clashes decided by discernment on the merits and never by recency.

Settlement: A deferral under the live proof protection route in R-25 counts only where the proof, on terms that forbid changing the code it proves, was already running and recorded before the defect was found and triaged. A defect that has been deferred under that route may not be deferred again for the same defect under a successor proof. No maximum length for a deferral is settled here, and that limb stays banked.

Deciding ground: anti-cheat, agent side, partial settlement.

Landing: LANDED, LEVEL-2 R-25, line 311.

Status: SETTLED IN PART by the Manager under the pass 2 grant, not ruled by Captain JP. The settled limbs above are settled. What stays banked: the maximum length for a deferral limb stays banked, and this item stays banked for that limb.

#### Completion under Captain JP's DQ-145 ruling: DQ-068

Completed by: The Manager (Muse), under Captain JP's DQ-145 ruling, in her words: "Yes, finish them that way."

Governing standard: the anti-cheat test first, then Captain JP's settlement philosophy as recorded in the pass 2 settlement above, with DQ-138 and DQ-139.

Completion: The maximum length limb is finished in form, so no deferral can run open ended. Every deferral under R-25 states its maximum length in the deferral record: for a deferral under live proof protection, the protecting proof's recorded planned end; for any other deferral, a named date stated in the granting ruling. A deferral with no maximum length stated does not count as a deferral. When the maximum is reached with the defect unfixed, the deferral expires, the defect returns to the defect loop as an open Critical or High defect, and the same defect may be deferred again only under a fresh ruling by Captain JP.

Deciding ground: anti-cheat, agent side. An unbounded deferral is a defect hidden by a calendar that never ends; a stated maximum with an expiry consequence keeps the deferral honest without forbidding the soak protection the flow already runs on.

Landing: LANDED, LEVEL-2 R-25. Corpus gate under DQ-002: PASS, recorded in scratch-finishing/gate-record.md.

Status: SETTLED by the Manager, the pass 2 limbs under the pass 2 grant and the remaining limb under DQ-145, not ruled by Captain JP. This item is settled and closed as a Manager completion; Captain JP may overrule it.

### DQ-069: Use-it and attempt-to-break-it, should depth per attack class carry a floor

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q20.

The question: Should a floor be set for depth, number of attacks, duration, or task difficulty at Step 16, at Step 17, or for the operator set scope of a null result under R-72?

Cost of deciding late: medium. Steps 16 and 17 proceed with no floor, so depth varies by build and a null result carries no ruled scope floor.

What it blocks: any depth floor for use-it or attempt-to-break-it work, and any scope floor for a null result under R-72.

Ordering reason: this entry asks for floor numbers no source supplies, so it sits in the later half.

#### Fill-in under Captain JP's ruling at DQ-141: DQ-069

Settled by: The Manager (Muse), as a fill-in under Captain JP's ruling at DQ-141, in her words: "You fill it in, strict side."

Fill-in: At Step 17, every attack class named for the build in its brief is exercised at least once; a class not exercised is recorded as not covered, never as passed. At Step 16, every task or route the brief claims is exercised at least once. A null result under R-72 stands only for the classes and routes actually exercised and named in the record; it claims nothing about anything not exercised.

Lands: LEVEL-2-STEPS.md, at R-22 for the Step 16 floor, at R-23 for the Step 17 floor, and at R-72 for the scope of a null result.

Status: SETTLED as a Manager fill-in under DQ-141, not ruled by Captain JP. The value set stands until Captain JP overrules it.

### DQ-070: Gate that never kills, should reclassification carry a consequence for the stages passed

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q21.

The question: Where a gate is reclassified at build close as a status meeting, not a gate, should reclassification recycle or re-examine the stages it passed, or should a detector threshold be ruled? The reclassification form itself is at register defect AUD-D131 and its missing review host is at register defect AUD-D029.

Cost of deciding late: medium. Stages passed by a gate later reclassified stand with no ruled consequence in the meantime.

What it blocks: any recycle, re-examination, or detector threshold consequence for stages passed by a gate later reclassified as a status meeting.

Ordering reason: this entry is a deep ruling about gate validity across a whole build, so it sits near the end of the order.

Cross-reference: the principle that arose from this entry's settlement attempt in the banked settlement run, the corpus gate against the strictness cost limb, is now ruled at DQ-138.

#### Settlement under Captain JP's pass 2 grant: DQ-070

Settled by: The Manager (Muse), under Captain JP's pass 2 grant, in her words: "Do another high discernment pass. I do not want the system to cheat itself or agents to cheat the system plus all the other stuff I said before."

Governing standard: the anti-cheat test first, that the system must not cheat itself and agents must not cheat the system, then Captain JP's settlement philosophy, security first, quality second, speed last, strict reading where workable unless it adds a huge build time, workable reading where strict is unworkable or too costly, neither good stays hers, and genuine redundancy removed with the surviving passage named, with DQ-138, the corpus gate governs over cost, and DQ-139, clashes decided by discernment on the merits and never by recency.

Settlement: No numeric detector threshold is added for gate reclassification. Reclassification rests on the evidence test already stated in R-51, that the gate criteria were not checked or that its decider lacked authority, recorded in the per build gate outcome review with the report going to Captain JP. The consequence for stages passed by a reclassified gate is not settled here and stays banked.

Deciding ground: anti-cheat, agent side, partial settlement.

Landing: RECORD-ONLY. Verified standing: R-51 final passage. No document edit was made for this settlement.

Recorded also: the earlier gate rejection of the flipped settlement stands untouched, and this settlement contains no stages standing wording (C-137 and C-160 respected; DQ-138).

Status: SETTLED IN PART by the Manager under the pass 2 grant, not ruled by Captain JP. The settled limb above is settled. What stays banked: the consequence for stages passed by a reclassified gate stays banked, and this item stays banked for that limb.

#### Completion under Captain JP's DQ-145 ruling: DQ-070

Completed by: The Manager (Muse), under Captain JP's DQ-145 ruling, in her words: "Yes, finish them that way."

Governing standard: the anti-cheat test first, then Captain JP's settlement philosophy as recorded in the pass 2 settlement above, with DQ-138 and DQ-139.

Completion: The consequence limb is finished. Where a gate is reclassified as a status meeting under R-51, the stage the gate passed, and every later stage whose closure rested on that passage, is reopened and recorded RECYCLED to the reclassified gate's stage, and each such stage is re-presented to a gate that meets the gate rule before it may close again. The build may not close at Step 23 while a stage passed by a reclassified gate stands un-re-examined, and a closure recorded on such a stage does not stand.

Deciding ground: anti-cheat, system side. A gate that was never a gate cannot be allowed to keep the stages it passed; anything weaker lets a build complete on assurance that was never given.

Landing: LANDED, LEVEL-2 R-51. Corpus gate under DQ-002: PASS, recorded in scratch-finishing/gate-record.md, which records plainly that this wording runs in the opposite direction from the settlement the gate rejected in the first settlement run on C-137 and C-160.

Status: SETTLED by the Manager, the pass 2 limb under the pass 2 grant and the remaining limb under DQ-145, not ruled by Captain JP. This item is settled and closed as a Manager completion; Captain JP may overrule it.

### DQ-071: Weaker fallback forms, should labelled fallbacks carry a sunset or a checker

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q22.

The question: Should the labelled weaker forms at R-173, R-177, and R-161 carry a date to reach the strong form, a checker for a cannot claim, or a gate a labelled weaker form cannot pass, or is honest labelling the intended whole control?

Cost of deciding late: low. Honest labelling remains the whole control for those forms in the meantime.

What it blocks: any sunset, checker, or gate bar for the labelled weaker forms at R-173, R-177, and R-161.

Ordering reason: this entry is a single choice, labelling alone or labelling plus a further control, and can be answered in one line.

#### Settlement under Captain JP's grant: DQ-071

Settled by: The Manager (Muse), under Captain JP's grant, in her words: "Go ahead and answer any of them yourself that seems simple enough. I care about security and quality over speed, i don't want things to be too strict that they're impossible, but they should be relatively strict to the standards they hold."

Strictness rule, in Captain JP's words: "If the stricter setting is not workable, then go with the workable. If the strict setting is workable go with it unless it adds a huge build time."

Settlement: Honest labelling is the whole control for the labelled weaker forms at rules R-173, R-177, and R-161. No sunset date, no checker, and no gate bar is added, and a labelled form may claim only what its label states, under the claim strength rules as they stand.

Deciding limb: strict unworkable. Source of settlement text and limb: refinement-abd.md Part 2.

Status: SETTLED by the Manager under the grant, not ruled by Captain JP. This item is settled.

### DQ-072: Overrides, should renewal be capped

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q23.

The question: Should renewal of an expired override under R-164, R-186, and R-159 be limited, live overrides capped, or the required authority raised as overrides accumulate? The regression budget form of this question is at DQ-087, from register entry AUD-Q38.

Cost of deciding late: medium. Overrides can renew and accumulate with no cap and no rising authority in the meantime.

What it blocks: any limit, cap, or rising authority rule for override renewal under R-164, R-186, and R-159.

Ordering reason: this entry asks for cap numbers no source supplies, so it sits in the later half.

Ruling in principle, added on the ruling: RULED in principle by Captain JP. The question as put to her: "Temporary exceptions can be renewed forever and pile up with no limit. Put a limit on them?" Her answer, quoted exactly: "Yes, cap them."

Ruling outcome: overrides under R-164, R-186, and R-159 are capped; unlimited renewal and accumulation of overrides end. The form of the cap, whether a set number of live or renewed overrides, authority rising as renewals accumulate, or another form, is being decided with Captain JP next, so this entry stays open in part for that decision. No document change is landed under this ruling in principle until the form is ruled.

Form decision, added on the ruling: RULED in full by Captain JP; this entry is closed. The question as put to her: "What kind of cap on temporary exceptions?" Her answer, quoted exactly: "Each renewal needs a bigger boss."

Form outcome: the cap takes the rising authority form. Renewal of an override under R-164, R-186, and R-159 requires authority one level above the authority that granted or last renewed it, rising with each renewal, so an override cannot be renewed indefinitely at the same level. Where no higher authority exists in the build's own structure, the renewal cannot be granted at that point and the override ends. The ruling is landed at R-164, R-186, and R-159 in LEVEL-2-STEPS.md, traced in dq-072-trace.md.

### DQ-073: Plaid duties, should protections follow actual staffing, not only the recorded tier

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q24.

The question: Should any Plaid instrument trigger on actual staffing or exposure rather than on the tier record alone, given that a build recorded at Extra High can be staffed to Plaid numbers by spin ups that never change its tier?

Cost of deciding late: medium to high. Protections stay tied to the recorded tier, so a build staffed to Plaid numbers at a lower recorded tier carries no Plaid instrument on that ground alone.

What it blocks: any Plaid instrument triggered by actual staffing or exposure rather than the tier record.

Ordering reason: this entry is a deep ruling about the tier system itself, so it sits near the end of the order.

Ruling, added on the ruling: RULED by Captain JP at DQ-142, by application of that ruling to this entry. Her words at DQ-142, quoted exactly: "The real team sets them."

Ruling outcome for this entry: Plaid instruments trigger on actual staffing, not on the tier record alone. A build staffed to Plaid numbers by spin ups that never change its recorded tier carries the Plaid instruments of PLAID.md section 3 in force on the ground of that staffing, without becoming a Plaid build and without its recorded tier changing. A build recorded at a tier above the staffing actually in place carries only the instruments of the team actually staffed, and the shortfall is recorded in the tier record. Exposure as a separate trigger is not ruled by DQ-142 and no exposure trigger is created by this entry; the staffing limb of the question is the whole of what DQ-142 decides. Status: RULED, closed, subject to the landings recorded at DQ-142 standing verified in tier-ruling-trace.md.

### DQ-074: Audit charge amendments, should scope be shrinkable mid round

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q25.

The question: Should scope amendment under R-54 be bounded once examination has started, for example by barring removal of an area already examined or by requiring Captain JP word for a narrowing?

Cost of deciding late: medium during a live audit round. Scope can be amended mid round with no stated bound in the meantime.

What it blocks: any bound on R-54 audit charge scope amendment after examination has started.

Ordering reason: this entry is a short choice in form, but it governs live audit rounds, so it sits in the middle of the order.

#### Settlement under Captain JP's grant: DQ-074

Settled by: The Manager (Muse), under Captain JP's grant, in her words: "Go ahead and answer any of them yourself that seems simple enough. I care about security and quality over speed, i don't want things to be too strict that they're impossible, but they should be relatively strict to the standards they hold."

Strictness rule, in Captain JP's words: "If the stricter setting is not workable, then go with the workable. If the strict setting is workable go with it unless it adds a huge build time."

Settlement: A mid round scope amendment changes nothing already examined: the chair alone may amend scope or roster, the amendment and its reason are recorded, and examination performed under the earlier scope is reported as performed under that scope. No Captain JP word and no further bar is added, because the audit criteria and the success criteria already may not be amended after examination has begun, and a change to either already requires a new charge and a new round. Lands: LEVEL-3-TEAMS.md, R-54, The charge. Implementation: small. No document text needs to change; the settlement is recorded against R-54 as written.

Deciding limb: strict workable. Source of settlement text and limb: classify-b.md and refinement-abd.md Part 1 limb audit.

Status: SETTLED by the Manager under the grant, not ruled by Captain JP. This item is settled.

### DQ-075: Research roles, should the done condition require evidence, not only a disposition per question

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q26.

The question: Should a minimum evidence condition be added to the researcher done condition (a finding, a contested note, or an open question per assigned question), or is the open question a legitimate full output of a research seat?

Cost of deciding late: low. The researcher done condition stays as a disposition per question; the cost is that a seat can finish with no evidence condition met.

What it blocks: any minimum evidence condition for the researcher done condition.

Ordering reason: this entry is a single choice about a done condition, and can be answered in one line.

#### Ruling by Captain JP

Question as put on the Questions space: "What makes a researcher's work done?" Her answer, in her words: "It asks you, air on caution"

Ruled as her words state it, and not sharpened past them: the researcher done definition in R-77 is judged with caution; where there is doubt whether a research seat's work is done under its definition, the doubt is put to Captain JP, and the work is not done on a doubtful reading. Landed in LEVEL-1-STANDING.md at R-77. Closed.

### DQ-076: Metrics and reporting, should a NOT RECORDED figure ever bar closure

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q27.

The question: Should any figure, in particular escapes (Q-3), carry a closure consequence despite the METRICS.md statement that no metric is a gate, a quota, or a pass mark, or is honest labelling of the gap the intended consequence? The approval qualification form of this question is at DQ-124, from register entry AUD-Q75.

Cost of deciding late: low to medium. No figure bars closure in the meantime, and honest labelling is the consequence in practice.

What it blocks: any closure consequence for a NOT RECORDED figure, including escapes at Q-3.

Ordering reason: this entry would qualify a standing statement in METRICS.md, so it sits in the later half despite its short form.

#### Settlement under Captain JP's grant: DQ-076

Settled by: The Manager (Muse), under Captain JP's grant, in her words: "Go ahead and answer any of them yourself that seems simple enough. I care about security and quality over speed, i don't want things to be too strict that they're impossible, but they should be relatively strict to the standards they hold."

Strictness rule, in Captain JP's words: "If the stricter setting is not workable, then go with the workable. If the strict setting is workable go with it unless it adds a huge build time."

Settlement: No NOT RECORDED figure, escapes at Q-3 included, ever bars closure on its own: the mark is a label, and a strange number is a prompt for an Auditor question, never a verdict by itself. Closure stays with the flow real gates, R-7 closure, the R-17 severity bars, and the Auditor ruling. Lands: METRICS.md, The one reading rule. Implementation: small. No document text needs to change; the settlement is recorded against the reading rule as written.

Deciding limb: strict workable. Source of settlement text and limb: classify-b.md and refinement-abd.md Part 1 limb audit.

Status: SETTLED by the Manager under the grant, not ruled by Captain JP. This item is settled.

### DQ-077: Plaid watcher, what form should the watcher take, and should it hold a power

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q28.

The question: Is the Plaid watcher a standing role of its own, a per build appointment, or part of an existing role job as PLAID.md section 4 now places it inside the Metrics Reporter; should it sit independently of the Reporter; and should it hold any stopping power beyond reporting drift to Captain JP and the Auditor? The defects under the current text are at register defects AUD-D038, AUD-D071, and AUD-D133.

Cost of deciding late: medium. The watcher stays inside the Metrics Reporter under the current text while its defects are fixed on that text; the cost is that its intended form and any stopping power stay unruled.

What it blocks: the intended form of the Plaid watcher, its independence from the Reporter, and any stopping power beyond reporting drift.

Ordering reason: this entry is a structural ruling about a Plaid role, so it sits in the later half.

#### Ruling by Captain JP

Question as put on the Questions space: "At Plaid, a watcher monitors the build. Should the watcher be able to stop the build on its own?" Her answer, in her words: "No, it reports and the Manager stops it."

Ruled: the Plaid watcher holds no stopping power. It reports drift, and the Manager stops the build on a drift report where stopping is warranted. Landed in PLAID.md, section 4. Closed.

### DQ-078: Design team at Low and Medium, how do scopes, Contrarian and Tracer combine against R-49

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q29.

The question: The design sizes are ruled at DQ-030 (scopes combine at the small end; Contrarian and Fold-in Tracer are never dropped). How does combining several of the six designer scopes in one agent stand against the one role rule in R-49 and each designer file statement that its role is held by one agent only, and are some scopes left unstaffed at base in reliance on R-50 spin ups? The counting statement defect is at register defect AUD-D103.

Cost of deciding late: medium. Small design teams proceed under DQ-030 with the R-49 tension unresolved, so staffing verdicts at Low and Medium carry that open point.

What it blocks: any ruling on how combined designer scopes stand against R-49, and on whether scopes may be left unstaffed at base in reliance on R-50 spin ups.

Ordering reason: this entry is a deep staffing ruling for small teams, so it sits near the end of the order.

#### Settlement under Captain JP's pass 2 grant: DQ-078

Settled by: The Manager (Muse), under Captain JP's pass 2 grant, in her words: "Do another high discernment pass. I do not want the system to cheat itself or agents to cheat the system plus all the other stuff I said before."

Governing standard: the anti-cheat test first, that the system must not cheat itself and agents must not cheat the system, then Captain JP's settlement philosophy, security first, quality second, speed last, strict reading where workable unless it adds a huge build time, workable reading where strict is unworkable or too costly, neither good stays hers, and genuine redundancy removed with the surviving passage named, with DQ-138, the corpus gate governs over cost, and DQ-139, clashes decided by discernment on the merits and never by recency.

Settlement: Designer scopes combine at the small end under DQ-030 as one combined scope role, held by one agent, entered once in the roster, so no agent holds more than one role and no role has more than one holder under R-49. The Contrarian and the Fold-in Tracer sit as distinct agents at every tier and never carry a combined designer scope. A scope is staffed only when an agent is seated for it in the roster, whether at base or by a spin up recorded at the time it happens under R-50. A possible later spin up is never counted as base staffing, and at Low the base team is the Contrarian and the Fold-in Tracer alone, as register note AUD-N6 sustained.

Deciding ground: strict workable.

Landing: LANDED, LEVEL-3-TEAMS.md Design team entry line 30, gate PASS on the narrow reading recorded in the gate record (combination is her DQ-030 ruling; roster form counts one combined scope role; FM-4 entries are audit entries and the wording grants no second seat anywhere; second sentence bars FM-10 planned staffing). Gate record at scratch-pass2/gate-record.md.

Status: SETTLED by the Manager under the pass 2 grant, not ruled by Captain JP. This item is settled.

### DQ-079: R-71 threats, what counts as an acceptable safeguard for the four self assessed threats

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q30.

The question: For the R-71 threats other than self review (which is prohibited outright; see register defect AUD-D020), should acceptable level thresholds or a verifier be ruled? DQ-006 settled only the commissioning branch of assessor disqualification.

Cost of deciding late: medium. The four threats are self assessed with no ruled threshold or verifier in the meantime.

What it blocks: any acceptable level threshold or verifier for the R-71 threats other than self review.

Ordering reason: this entry asks for thresholds no source supplies, so it sits in the later half.

Partial ruling, added on the ruling: RULED in part by Captain JP. The question as put to her: "For four known risks to honest checking, teams grade their own homework. Nobody outside checks the grade. Require an outside checker?" Her answer, quoted exactly: "Yes, outside check required."

Ruling outcome, verifier limb: the self assessments under R-71 are checked by a verifier outside the assessed team; a self assessment with no outside check does not stand. The verifier is an outside checker of the assessment, a function of the round staffed from the step's own staffing, not a new standing role. Landed at LEVEL-3 R-71. This entry stays open in part for the thresholds limb, the acceptable levels for the four threats, which is being put to Captain JP next.

Completing ruling, added on the ruling: RULED by Captain JP. The question as put to her: "For those same four risks, also set one fixed pass bar, or let the outside checker judge each time?" Her answer, quoted exactly: "Checker judges each time." This answer went against the Manager's recommendation of a fixed bar; her ruling governs.

Ruling outcome, thresholds limb: no fixed acceptable level thresholds are set for the four R-71 threats. The acceptable level in each case is the outside verifier's judgement, recorded with the disposition it checks, so the judgement is itself on the record and cannot drift silently. Landed at LEVEL-3 R-71, beside the verifier sentence. With both limbs ruled, this item is RULED in full and closed.

### DQ-080: Security Sentinel, should the watch hold a power over grants and secrets

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q31.

The question: Should the Security Sentinel hold a power to revoke a grant, block a push, or hold a step, beyond reporting and handing the incident to the Project Manager?

Cost of deciding late: medium. The Sentinel reports and hands over only; the cost is that a live grant or secret incident waits for another role to act.

What it blocks: any Sentinel power to revoke a grant, block a push, or hold a step.

Ordering reason: this entry is a single power choice, and can be answered in one line, though its effect on live incidents keeps it in the middle of the order.

#### Settlement under Captain JP's grant: DQ-080

Settled by: The Manager (Muse), under Captain JP's grant, in her words: "Go ahead and answer any of them yourself that seems simple enough. I care about security and quality over speed, i don't want things to be too strict that they're impossible, but they should be relatively strict to the standards they hold."

Strictness rule, in Captain JP's words: "If the stricter setting is not workable, then go with the workable. If the strict setting is workable go with it unless it adds a huge build time."

Settlement: The Security Sentinel holds no power to revoke a grant, block a push, or hold a step. Its security force stays as the flow already gives it: a push with a secret finding is not treated as clean, findings route at once to the Project Manager and to Captain JP, a halt may be called under R-2 as any agent may call one, and grant removal stays with the grant owner and step blocking with the Auditor and the Project Manager.

Deciding limb: strict workable. Source of settlement text and limb: classify-c.md.

Status: SETTLED by the Manager under the grant, not ruled by Captain JP. This item is settled.

### DQ-081: Contrarian register, should design closure limit open or banked objections

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q32.

The question: Should closure under R-46 be tied to how many, or which class of, contrarian objections may remain open or banked?

Cost of deciding late: low. Design closure proceeds with no limit on open or banked contrarian objections.

What it blocks: any limit, by number or by class, on contrarian objections that may remain open or banked at design closure under R-46.

Ordering reason: this entry is a short choice, no limit or a stated limit, and can be answered in one line.

#### Settlement under Captain JP's grant: DQ-081

Settled by: The Manager (Muse), under Captain JP's grant, in her words: "Go ahead and answer any of them yourself that seems simple enough. I care about security and quality over speed, i don't want things to be too strict that they're impossible, but they should be relatively strict to the standards they hold."

Strictness rule, in Captain JP's words: "If the stricter setting is not workable, then go with the workable. If the strict setting is workable go with it unless it adds a huge build time."

Settlement: No limit, by number or by class, is placed on contrarian objections that may remain open or banked at design closure. Closure under R-46 instead requires every objection to carry a disposition: answered, banked to Captain JP, or ruled out with the reason.

Deciding limb: strict unworkable. Source of settlement text and limb: classify-c.md.

Status: SETTLED by the Manager under the grant, not ruled by Captain JP. This item is settled.

### DQ-082: Imagination proposals, should held and open states expire

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q33.

The question: Should held and open imagination proposals carry an expiry or a revisit trigger, of the kind the Incubator habit requires for deferred items?

Cost of deciding late: low. Held and open proposals persist with no expiry or revisit trigger in the meantime.

What it blocks: any expiry or revisit trigger for held and open imagination proposals.

Ordering reason: this entry is a single choice, persist or expire, and can be answered in one line.

#### Settlement under Captain JP's grant: DQ-082

Settled by: The Manager (Muse), under Captain JP's grant, in her words: "Go ahead and answer any of them yourself that seems simple enough. I care about security and quality over speed, i don't want things to be too strict that they're impossible, but they should be relatively strict to the standards they hold."

Strictness rule, in Captain JP's words: "If the stricter setting is not workable, then go with the workable. If the strict setting is workable go with it unless it adds a huge build time."

Settlement: Held and open imagination proposals do not expire, but each carries the Incubator form: a named owner, a named revisit trigger, and a date. A proposal missing any of the three is recorded as a defect in the record, not as a held proposal.

Deciding limb: strict workable. Source of settlement text and limb: classify-c.md.

Status: SETTLED by the Manager under the grant, not ruled by Captain JP. This item is settled.

### DQ-083: Plaid extension seats, should a slice carry a minimum size or a quality check

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q34.

The question: Should a floor or an independent check be ruled for the named slice second seats created in PLAID.md section 2, given that whoever writes the roster controls how many distinct seats exist?

Cost of deciding late: medium at Plaid. Slice second seats exist with no floor or independent check, while roster authors control the distinct seat count.

What it blocks: any floor or independent check for Plaid extension slice second seats in PLAID.md section 2.

Ordering reason: this entry asks for a floor or check form no source supplies, so it sits in the later half.

#### Ruling by Captain JP

Question as put on the Questions space: "At Plaid, some teams gain extra seats as named second seats for slices of the work. Whoever writes the roster decides how many of those seats exist. Should each slice seat carry a minimum size, or an independent check on the roster, or neither?" Her answer, in her words: "An independent check, no minimum size."

Ruled: at Plaid, the named slice second seats created in PLAID.md section 2 carry no minimum size: no floor is set on the number of slice seats for any slice. Before a step that staffs slice second seats closes, an agent who did not write the roster independently checks the roster's slice seat count against the slice definitions in PLAID.md section 2, and the check is recorded in the step record, naming the checker, the roster checked, and the count found against the count the definitions give. A step whose slice second seats carry no recorded check does not close. Landed in PLAID.md section 2, as the paragraph headed "Slice second seats carry no minimum size, and the roster is checked", following the extension forms. Closed.

### DQ-084: Judge and simulator bias controls, should the stated controls be tested, not only asserted

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q35.

The question: Should blinding under R-118 be tested, a shared model family under R-204 bar a verdict, or the self reported provenance grade under R-213 be excluded from any admission?

Cost of deciding late: medium. The controls stand as asserted only; the cost is that judge and simulator bias controls carry no test, bar, or exclusion in practice.

What it blocks: any test of R-118 blinding, any verdict bar for a shared model family under R-204, and any exclusion of the self reported provenance grade under R-213 from admission.

Ordering reason: this entry is a deep ruling about eval integrity, so it sits in the later half.

Partial ruling, limb 1: RULED by Captain JP. The question as put to her: "The guards against biased judging are only claimed, never tested. Should they be tested?" Her answer, quoted exactly: "Yes, test them."

Outcome of this decision: the bias controls are tested, not only asserted. The blinding control under R-118 is exercised in the judge validation protocol at R-122, and the exercise and its result are recorded there; a blinding control that has not been exercised does not count as in force. Landed in LEVEL-3-TEAMS.md at R-118. This entry stays open in part for the remaining two limbs: limb 2, whether a shared model family under R-204 bars a verdict, and limb 3, whether the self reported provenance grade under R-213 is excluded from any admission; both are being put to Captain JP next.

Partial ruling, limb 2: RULED by Captain JP. The question as put to her: "Same family judging its own kind. The judge and the judged come from the same model family. Block the verdict?" Her answer, quoted exactly: "No, allowed." Outcome of this decision: a shared model family between judge and judged under R-204 does not bar a verdict; the standing text stands unchanged on this limb, and no document landing follows from it. This decision went against the Manager's recommendation (the recommendation put to her was to block the verdict); her ruling governs. This entry stays open in part for limb 3, whether the self reported provenance grade under R-213 is excluded from any admission, which is being put to Captain JP next.

Partial ruling, limb 3, and closure: RULED by Captain JP. The question as put to her: "A team grades its own evidence and reports the grade. Should that self grade count when the evidence is judged for admission?" Her answer, quoted exactly: "No, self grade does not count." Outcome of this decision: the self reported provenance grade under R-213 is excluded from any admission decision; admission rests on the examined evidence, not on the grade its producer reported. Landed in METRICS.md at R-213. With all three limbs now ruled (limb 1: the bias controls are tested, not only asserted; limb 2: a shared model family under R-204 does not bar a verdict; limb 3: as here), this item is RULED in full and closed.

### DQ-085: Scope of a step, who may overrule the agent own systems decision

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q36.

The question: Should an overrule authority or an exclusions list be required for the standing rule 4 systems decision each agent records for a step it serves in?

Cost of deciding late: low. Each agent own systems decision stands with no ruled overrule authority or exclusions list.

What it blocks: any overrule authority or exclusions list for the standing rule 4 systems decision.

Ordering reason: this entry is a short naming choice, and can be answered in one line.

#### Fill-in under Captain JP's ruling at DQ-141: DQ-085

Settled by: The Manager (Muse), as a fill-in under Captain JP's ruling at DQ-141, in her words: "You fill it in, strict side."

Fill-in: The Project Manager may overrule an agent's recorded systems decision for a step, with the overrule and its reason recorded in the step record before the step closes. Exclusions: no overrule may lower a tier staffing minimum, move a gate or closure bar, excuse a corpus incident, or change the text of a rule; those changes go through the decision queue.

Lands: LEVEL-4-MEMBERS.md, in the Project Manager entry, at the passage that records the systems decision each role holder makes under standing rule 4.

Status: SETTLED as a Manager fill-in under DQ-141, not ruled by Captain JP. The value set stands until Captain JP overrules it.

### DQ-086: Judge admission, who supplies the second independent human

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q37.

The question: Who supplies the second independent human labeller required by R-119, or does judge admission wait until one exists? The missing appointment record is a defect at register defect AUD-D105; this entry is only the choice of person.

Cost of deciding late: high for judge admission. Admission requiring two independent human labellers cannot proceed on a named supply until a second person is named or a waiting rule is ruled.

What it blocks: judge admission under R-119 wherever it needs the second independent human labeller. It blocks no appointment record fix, which is at AUD-D105.

Ordering reason: this entry sits last among its group. It requires naming a specific person, which the queue ordering rule puts at the end.

#### Fill-in under Captain JP's ruling at DQ-141: DQ-086

Settled by: The Manager (Muse), as a fill-in under Captain JP's ruling at DQ-141, in her words: "You fill it in, strict side."

Fill-in: The second independent human labeller is supplied by Captain JP's appointment, recorded by name in the judge admission record. Until a second independent human labeller stands appointed, judge admission under R-119 waits; no admission proceeds on one labeller, and no agent or model stands in for the second human.

Landing: LANDED, LEVEL-3-TEAMS.md, rule R-119, Human ceiling measurement, closing sentences of the rule paragraph.

Status: SETTLED as a Manager fill-in under DQ-141, not ruled by Captain JP. The value set stands until Captain JP overrules it.

### DQ-087: Regression error budgets, should repeated renewal of top ups be capped

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q38.

The question: Should repeated renewal of expiring budget top up rulings under R-190 and R-206 be capped? This is the budget form of the question; the gate override form is at DQ-072, from register entry AUD-Q23.

Cost of deciding late: medium. Budget top up rulings can renew repeatedly with no cap in the meantime.

What it blocks: any cap on repeated renewal of budget top up rulings under R-190 and R-206.

Ordering reason: this entry asks for a cap no source supplies, so it sits in the later half, beside DQ-072.

Cross-reference, added on the DQ-072 ruling: the cap principle for this question's gate override form is ruled in principle at DQ-072; the cap's form decision is pending there and applies to this entry too.

Cross-reference update, added on the DQ-072 form ruling: the cap's form is now ruled in full at DQ-072. The form is rising authority: each renewal requires authority one level above the authority that granted or last renewed it, and where no higher authority exists in the build's own structure the renewal cannot be granted and the override ends. That form applies to this entry's gate override form the same way. This entry itself stays banked for its remaining substance, the budget top up renewal question under R-190 and R-206.

#### Settlement under Captain JP's pass 2 grant: DQ-087

Settled by: The Manager (Muse), under Captain JP's pass 2 grant, in her words: "Do another high discernment pass. I do not want the system to cheat itself or agents to cheat the system plus all the other stuff I said before."

Governing standard: the anti-cheat test first, that the system must not cheat itself and agents must not cheat the system, then Captain JP's settlement philosophy, security first, quality second, speed last, strict reading where workable unless it adds a huge build time, workable reading where strict is unworkable or too costly, neither good stays hers, and genuine redundancy removed with the surviving passage named, with DQ-138, the corpus gate governs over cost, and DQ-139, clashes decided by discernment on the merits and never by recency.

Basis recorded expressly: this settles only the renewal form limb, as the recorded application of Captain JP's own DQ-072 rising authority ruling, whose queue record already stated the form applies to this entry; the remaining budget substance stays banked and nothing else in it is decided.

Settlement: Renewal of an expiring regression budget top up ruling is capped in the rising authority form ruled at DQ-072. Each renewal requires authority one level above the authority that granted or last renewed the top up, rising with each renewal. Where no higher authority exists in the build's own structure, the renewal cannot be granted and the top up ends.

Deciding ground: anti-cheat, agent side, partial settlement.

Landing: LANDED, PLAID.md Regression error budgets passage, line 152.

Status: SETTLED IN PART by the Manager under the pass 2 grant, not ruled by Captain JP. The renewal form limb above is settled. What stays banked: the remaining budget substance of this item stays banked, nothing else in it is decided, and this item stays banked for that remainder.

#### Scrutiny under Captain JP's DQ-145 ruling: DQ-087

Examined by: The Manager (Muse), under Captain JP's DQ-145 ruling, in her words: "Yes, finish them that way."

Scrutiny outcome: The remainder of this item was examined first, as the finishing instruction required, and it is not finished. The item's stated question, whether repeated renewal of expiring budget top up rulings should be capped, is answered in full: the cap principle is Captain JP's own DQ-072 ruling and the cap's form, rising authority ending where no higher authority exists, is settled above and landed in PLAID.md. What the pass 2 record called the remaining budget substance is the sizing of the regression error budgets and the granting of top ups themselves under R-190 and R-206, which are set per build in the governance page. That is budget setting substance: under DQ-143 it comes to Captain JP, and under the finishing ruling's own limit a limb in truth money substance is not finished by the Manager. No document edit is made for this item in this run.

Status: SETTLED IN PART stands, the renewal form limb under the pass 2 grant. The remainder stays banked. Reason, in one line: the remainder is budget setting substance, which is Captain JP's under DQ-143, and cannot be finished for her.

#### Ruling by Captain JP

Question as put on the Questions space: "Who sets the size of a build's regression budgets and top-ups?" Her answer, in her words: "The Manager, and I can overrule"

Ruled: the sizing of the regression error budgets and the granting of top ups are the Manager's, recorded in the governance page, and stand open to Captain JP's overruling. Landed in PLAID.md, in the regression error budgets passage. With this ruling the item closes in full: its renewal form limb stands settled under the DQ-072 rising authority form recorded above.

### DQ-088: Reporting to Captain JP, should the gate outcome distribution reach the summary message

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q39.

The question: Should the gate outcome distribution (METRICS.md F-8) be added to the Report 2 summary message or the cross-build digest, rather than kept on the report page only?

Cost of deciding late: low. The distribution stays on the report page only in the meantime.

What it blocks: any addition of the F-8 gate outcome distribution to the Report 2 summary message or the cross-build digest.

Ordering reason: this entry sits near the top of its group. It is a single surface choice, and can be answered in one tap.

#### Settlement under Captain JP's grant: DQ-088

Settled by: The Manager (Muse), under Captain JP's grant, in her words: "Go ahead and answer any of them yourself that seems simple enough. I care about security and quality over speed, i don't want things to be too strict that they're impossible, but they should be relatively strict to the standards they hold."

Strictness rule, in Captain JP's words: "If the stricter setting is not workable, then go with the workable. If the strict setting is workable go with it unless it adds a huge build time."

Settlement: The F-8 gate outcome distribution is not added to the Report 2 summary message or to the cross build digest. It stays in full on the report page, with its denominator, and the summary message keeps only the figures REPORTING.md lists for it.

Deciding limb: strict workable. Source of settlement text and limb: classify-c.md.

Status: SETTLED by the Manager under the grant, not ruled by Captain JP. This item is settled.

### DQ-089: Incubated sets, which set governs where the overlapping sets differ

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q40.

The question: The first and second incubated sets in LEVEL-1 cover the same ground twice with differing conditions, and the expansion set implies the second set governs carried items. Which set controls where their wordings differ? The missing elements defect, which applies to all three sets, is at register defect AUD-D008.

Cost of deciding late: medium. Where the sets differ, no governing set is ruled, so an incubated item can be read under either wording.

What it blocks: any governing set rule for the overlapping incubated sets in LEVEL-1 where their wordings differ. It blocks no missing elements fix, which is at AUD-D008.

Ordering reason: this entry is a short choice between overlapping texts, but it governs live incubated items, so it sits in the middle of the order.

#### Settlement under Captain JP's grant: DQ-089

Settled by: The Manager (Muse), under Captain JP's grant, in her words: "Go ahead and answer any of them yourself that seems simple enough. I care about security and quality over speed, i don't want things to be too strict that they're impossible, but they should be relatively strict to the standards they hold."

Strictness rule, in Captain JP's words: "If the stricter setting is not workable, then go with the workable. If the strict setting is workable go with it unless it adds a huge build time."

Settlement: Where the first and second incubated sets in LEVEL-1 differ on a carried item, the second set governs, including any added condition the second set states. The first set stays as the record for any item the second set does not carry.

Deciding limb: strict workable. Source of settlement text and limb: classify-c.md.

Status: SETTLED by the Manager under the grant, not ruled by Captain JP. This item is settled.

### DQ-090: Subagent helper class

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q41.

The question: Is a subagent helper class intended to exist in the flow, spawned by a role holder to help with that holder own work and exempt from the R-50 unique role and roster recording requirements? The defect under the current ruled text is at register defect AUD-D004.

The options, stated plainly:

- No helper class, with R-50 as the only spawning route.
- A helper class with roster recording under R-50 conditions.
- A helper class exempt from both requirements.

Cost of deciding late: medium. The AUD-D004 defect is fixed on the current ruled text, with R-50 as the spawning route; the cost is that any intended helper class has no ruled form.

What it blocks: any subagent helper class, in either recorded or exempt form. It blocks no AUD-D004 fix.

Ordering reason: this entry is a short choice among three stated options, and can be answered in one line.

#### Settlement under Captain JP's grant: DQ-090

Settled by: The Manager (Muse), under Captain JP's grant, in her words: "Go ahead and answer any of them yourself that seems simple enough. I care about security and quality over speed, i don't want things to be too strict that they're impossible, but they should be relatively strict to the standards they hold."

Strictness rule, in Captain JP's words: "If the stricter setting is not workable, then go with the workable. If the strict setting is workable go with it unless it adds a huge build time."

Settlement: No subagent helper class exists outside R-50. A helper is a subagent routed through the Manager under R-50, with a unique role and a roster and spawn record, and work by an unrecorded helper does not count toward any output or done condition.

Deciding limb: strict workable. Source of settlement text and limb: classify-c.md.

Status: SETTLED by the Manager under the grant, not ruled by Captain JP. This item is settled.

### DQ-091: PARTIAL review conclusions against DQ-015, narrowed to R-56 reviews

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q42.

The question: Does a brief, plan, or audit paper review concluding open with plan, recorded PARTIAL under R-7 at R-56, count as the work moving on with issues unfixed, which DQ-015 bars, or is a PARTIAL conclusion exactly the not moving on that DQ-015 requires? Note: for Step 12 audit loop findings the same conflict is settled as a defect at register defect AUD-D023 on DQ-015 and R-85; this entry is retained only for the R-56 review form, which no ruling names.

The options, stated plainly:

- PARTIAL conclusions are permitted not moving on, and R-56 stands.
- Every review must conclude with no open items, and R-56 is amended.

Cost of deciding late: low to medium. R-56 reviews proceed with PARTIAL conclusions whose standing against DQ-015 is unruled.

What it blocks: any ruling on whether R-56 PARTIAL review conclusions stand against DQ-015, or whether R-56 must be amended.

Ordering reason: this entry turns on a prior ruling at DQ-015, so it sits in the later half despite its two stated options.

#### Settlement under Captain JP's pass 2 grant: DQ-091

Settled by: The Manager (Muse), under Captain JP's pass 2 grant, in her words: "Do another high discernment pass. I do not want the system to cheat itself or agents to cheat the system plus all the other stuff I said before."

Governing standard: the anti-cheat test first, that the system must not cheat itself and agents must not cheat the system, then Captain JP's settlement philosophy, security first, quality second, speed last, strict reading where workable unless it adds a huge build time, workable reading where strict is unworkable or too costly, neither good stays hers, and genuine redundancy removed with the surviving passage named, with DQ-138, the corpus gate governs over cost, and DQ-139, clashes decided by discernment on the merits and never by recency.

Settlement: PARTIAL conclusions under R-56 stand, and R-56 is not amended. A brief, plan, or audit paper review may conclude open with plan, recorded PARTIAL under R-7, and that conclusion is not moving on: the stage has not closed, does not count, and bars the move to the next stage while the items stand open. An open item is not fixed or closed by being carried forward, its disposition must be stated in the closure record for the next gate, and where an item is a triaged audit finding, R-85 and DQ-015 govern and it must be fixed before the work moves on.

Deciding ground: strict workable.

Landing: RECORD-ONLY. Verified standing: R-56, R-7, and R-85. No document edit was made for this settlement.

Status: SETTLED by the Manager under the pass 2 grant, not ruled by Captain JP. This item is settled.

### DQ-092: Budget authority

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q43.

The question: Which authority, Captain JP or the Manager, is intended to set a build budget at Pre-plan and to decide on more budget after a TIMED-OUT stop? The missing named authority as the set stands is at register defect AUD-D046.

Cost of deciding late: medium. Budgets are set and TIMED-OUT budget decisions are taken with the intended authority unruled, while AUD-D046 fixes the missing naming on the text as it stands.

What it blocks: the intended budget authority at Pre-plan and after a TIMED-OUT stop. It blocks no AUD-D046 naming fix.

Ordering reason: this entry is a single authority choice between two named holders, and can be answered in one tap.

#### Assessment under DQ-143

Assessed under Captain JP's money ruling, DQ-143, in her words: "Use discernment if you should ask me." This item falls on the side of the line that comes to Captain JP: it asks who sets a build budget and who decides on more budget after a TIMED-OUT stop, and setting or increasing a budget is what the ruling reserves to her. Status: Banked, marked as hers under DQ-143. No settlement is made.

#### Ruling by Captain JP

Question as put on the Questions space: "Who sets a build's budget, and who can give it more after it stops for running out?" Her answer, in her words: "The Manager, within a limit I set."

Ruled: a build's budget is set by the Manager, and where a build stops for running out of budget and is recorded TIMED-OUT, the Manager may give it more, within a limit Captain JP sets. Landed in LEVEL-2-STEPS.md at Step 3. The limit itself stands unnamed: no value is invented in this record or in the flow, and the limit takes effect as a number when Captain JP names it. A follow-up question asking her to name the limit is recorded in the batch trace for loading onto the Questions space. Closed as ruled, the limit's value outstanding by her own reservation.

#### Further ruling by Captain JP

Question as put on the Questions space: "You ruled the Manager sets a build's budget and can give it more after it runs out, within a limit you set. What is that limit?" Her answer, in her words: "It asks for more"

Ruled: there is no standing numeric limit. The limit is the set budget itself: giving a build more than its set budget is done by asking Captain JP for more, and her answer governs. This block aligns the authority in this entry with its limit: the Manager sets the budget, and more beyond the set budget is given only by asking Captain JP. Landed in LEVEL-2-STEPS.md at Step 3 in that form, with her answer and the amount recorded in the cost ledger where more is given. This entry was already closed as ruled with the limit's value outstanding; this block settles that outstanding value in the form above. Closed.

### DQ-093: Finished product install placement

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q44.

The question: Is installing the finished product, and later upgrading it, intended to sit inside the 23 step path before the release gate, after it as a standing operation, or outside the build altogether? The missing placement as the set stands is at register defect AUD-D047.

Cost of deciding late: medium. AUD-D047 states an install act before Step 18 on the steps as written; the cost is that the intended placement of install and upgrade stays unruled, so a later ruling may move that act.

What it blocks: the intended placement of finished product install and upgrade in relation to the 23 step path and the release gate. It blocks no AUD-D047 fix on the current text.

Ordering reason: this entry is a short placement choice among three stated positions, and can be answered in one line.

#### Settlement under Captain JP's pass 2 grant: DQ-093

Settled by: The Manager (Muse), under Captain JP's pass 2 grant, in her words: "Do another high discernment pass. I do not want the system to cheat itself or agents to cheat the system plus all the other stuff I said before."

Governing standard: the anti-cheat test first, that the system must not cheat itself and agents must not cheat the system, then Captain JP's settlement philosophy, security first, quality second, speed last, strict reading where workable unless it adds a huge build time, workable reading where strict is unworkable or too costly, neither good stays hers, and genuine redundancy removed with the surviving passage named, with DQ-138, the corpus gate governs over cost, and DQ-139, clashes decided by discernment on the merits and never by recency.

Settlement: The first install of the finished product sits inside the 23 step path. The Installer installs it after Step 17 closes and before Step 18 opens, and the proof does not run on an install with no R-1 verification record in the install register. The final install confirmation sits inside Step 22, after the release gate record, under R-27.

Deciding ground: redundancy, partial settlement, the standing text already answers the limb.

Landing: RECORD-ONLY. Verified standing: Step 18 Job, FLOW.md install passage, and R-27. No document edit was made for this settlement.

Status: SETTLED IN PART by the Manager under the pass 2 grant, not ruled by Captain JP. The settled limb above is settled. What stays banked: the later upgrades limb stays banked, and this item stays banked for that limb.

#### Completion under Captain JP's DQ-145 ruling: DQ-093

Completed by: The Manager (Muse), under Captain JP's DQ-145 ruling, in her words: "Yes, finish them that way."

Governing standard: the anti-cheat test first, then Captain JP's settlement philosophy as recorded in the pass 2 settlement above, with DQ-138 and DQ-139.

Completion: The later upgrades limb is finished, in the same form as the first install limb settled above. A later upgrade of the installed product, after the build has closed, sits outside the closed build's 23 steps, as a standing operation: the Installer performs it on the live target, it is recorded in the install register with its source, version, target and verification result, and it counts only under R-1 as the first install does. An upgrade that changes what the product does is not an upgrade act at all: it is a new version, built as its own build under the flow, from the direction recorded at Step 23.

Deciding ground: redundancy, in part, and strict workable. The first install form already supplies the act, the actor, the register, and the verification; the completion states the same form for the same act after close, and bars the one cheat the limb could hide, a behaviour change shipped as a mere upgrade so it never meets the flow.

Landing: LANDED, FLOW.md, later upgrades passage following the install passage. Corpus gate under DQ-002: PASS, recorded in scratch-finishing/gate-record.md.

Status: SETTLED by the Manager, the pass 2 limb under the pass 2 grant and the remaining limb under DQ-145, not ruled by Captain JP. This item is settled and closed as a Manager completion; Captain JP may overrule it.

### DQ-094: RECYCLED predecessor instance, is it terminal

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q45.

The question: Is the recycled predecessor instance itself terminal, as the other closed and ended states in R-3 are marked, while work resumes as a new linked instance?

The options, stated plainly:

- The predecessor is terminal once the new instance opens.
- The predecessor is not terminal.

Cost of deciding late: low. The R-3 state record carries the predecessor with its terminal standing unruled.

What it blocks: any terminal marking for a RECYCLED predecessor instance in R-3.

Ordering reason: this entry sits near the top of its group. It is a binary choice, and can be answered in one tap.

#### Settlement under Captain JP's grant: DQ-094

Settled by: The Manager (Muse), under Captain JP's grant, in her words: "Go ahead and answer any of them yourself that seems simple enough. I care about security and quality over speed, i don't want things to be too strict that they're impossible, but they should be relatively strict to the standards they hold."

Strictness rule, in Captain JP's words: "If the stricter setting is not workable, then go with the workable. If the strict setting is workable go with it unless it adds a huge build time."

Settlement: A RECYCLED predecessor instance is not terminal. It may still move, for example to STOPPING if a halt is called before work resumes, and work resumes as a new linked instance in IN PROGRESS at the named earlier stage.

Deciding limb: strict workable. Source of settlement text and limb: classify-c.md.

Status: SETTLED by the Manager under the grant, not ruled by Captain JP. This item is settled.

### DQ-095: Decision queue lifecycle, exemption or mapping

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q46.

The question: Should the decision queue keep its own item lifecycle as a named exemption from the R-3 work state vocabulary, or be mapped onto R-3 states? The contradiction as the set stands is at register defect AUD-D011; this entry asks what the queue is, which only Captain JP can settle.

The options, stated plainly:

- The queue keeps its own lifecycle as a named exemption from R-3.
- The queue lifecycle is mapped onto R-3 states.

Cost of deciding late: medium. AUD-D011 aligns the lists on the queue document as it stands; the cost is that the queue standing as an exemption or as a mapped system stays unruled.

What it blocks: the settled standing of the decision queue lifecycle against R-3. It blocks no AUD-D011 alignment fix.

Ordering reason: this entry is a deep ruling about this queue itself, so it sits near the end of the order.

#### Settlement under Captain JP's grant: DQ-095

Settled by: The Manager (Muse), under Captain JP's grant, in her words: "Go ahead and answer any of them yourself that seems simple enough. I care about security and quality over speed, i don't want things to be too strict that they're impossible, but they should be relatively strict to the standards they hold."

Strictness rule, in Captain JP's words: "If the stricter setting is not workable, then go with the workable. If the strict setting is workable go with it unless it adds a huge build time."

Settlement: The decision queue lifecycle is mapped onto R-3, not exempt from it: Banked, Presented, and Parked are sub states of BANKED, and Ruled is a sub state of a CLOSED state, as R-3 already records. No queue lifecycle word outside that mapping carries force.

Deciding limb: strict workable. Source of settlement text and limb: classify-c.md.

Status: SETTLED by the Manager under the grant, not ruled by Captain JP. This item is settled.

### DQ-096: Reporting system ownership

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q47.

The question: Do the production, drift, and quarterly ledger reports, and by extension the experiment report, belong to the Metrics Reporter three report system, or to a separate EDD reporting system with its own owner? The contradictions and the missing form are at register defects AUD-D034 and AUD-D035.

The options, stated plainly:

- Inside the Reporter system, with the pipeline sentence restated.
- A separate EDD reporting system with a named owner.

Cost of deciding late: medium. The reports are produced under the Reporter system while their ownership stays unruled, and AUD-D034 and AUD-D035 are fixed on the current text.

What it blocks: the ownership of the production, drift, quarterly ledger, and experiment reports. It blocks no AUD-D034 or AUD-D035 fix.

Ordering reason: this entry is a short choice between two stated owners, and can be answered in one line.

#### Settlement under Captain JP's grant: DQ-096

Settled by: The Manager (Muse), under Captain JP's grant, in her words: "Go ahead and answer any of them yourself that seems simple enough. I care about security and quality over speed, i don't want things to be too strict that they're impossible, but they should be relatively strict to the standards they hold."

Strictness rule, in Captain JP's words: "If the stricter setting is not workable, then go with the workable. If the strict setting is workable go with it unless it adds a huge build time."

Settlement: The production, drift, and quarterly ledger reports, and the experiment report, belong to the Metrics Reporter system, with the Metrics Reporter as producer, as REPORTING.md already states for each form. No separate EDD reporting system and no second owner is created.

Deciding limb: strict workable. Source of settlement text and limb: classify-c.md.

Status: SETTLED by the Manager under the grant, not ruled by Captain JP. This item is settled.

### DQ-097: Step 16 governing bar

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q48.

The question: At Step 16, which bar governs where a triaged High finding is not a blocking failure in the session record: the loop own holds test (real work completes without a blocking failure), or the common R-17 bar of 0 Critical and 0 High, Step 16 containing an Audit unit?

The options, stated plainly:

- The loop own holds test governs at Step 16.
- The common R-17 bar of 0 Critical and 0 High governs at Step 16.

Cost of deciding late: medium to high at Step 16. A triaged High finding at Step 16 has no ruled governing bar, so whether the loop holds is contestable in a live run.

What it blocks: any ruling on which bar governs a triaged High finding at Step 16.

Ordering reason: this entry is a binary choice, but it decides a live loop bar, so it sits in the middle of the order.

#### Settlement under Captain JP's grant: DQ-097

Settled by: The Manager (Muse), under Captain JP's grant, in her words: "Go ahead and answer any of them yourself that seems simple enough. I care about security and quality over speed, i don't want things to be too strict that they're impossible, but they should be relatively strict to the standards they hold."

Strictness rule, in Captain JP's words: "If the stricter setting is not workable, then go with the workable. If the strict setting is workable go with it unless it adds a huge build time."

Settlement: At Step 16 the common R-17 bar governs: a triaged High finding bars the loop closing, whatever the session record shows about blocking failures, and the loop holds only when the High is fixed and the bar of 0 Critical and 0 High is met. The session record holds test stays as the record of the real work done, not as a lower bar.

Deciding limb: strict workable. Source of settlement text and limb: classify-c.md.

Status: SETTLED by the Manager under the grant, not ruled by Captain JP. This item is settled.

### DQ-098: Proceeding on a qualified gate through Steps 21 and 22

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q49.

The question: Where a Critical or High defect is deferred under a running live proof protection and the Step 19 gate stands at CLOSED-QUALIFIED under R-25, may the build proceed through confirmation live proof and the release gate on that qualified gate, or must Steps 21 and 22 wait until the deferral ends? The missing exit statement is at register defect AUD-D067, and the downstream recording defect is at register defect AUD-D145.

Cost of deciding late: high at the end of a build carrying such a deferral. Steps 21 and 22 have no ruled answer for that case, so the build either waits or proceeds without a ruling.

What it blocks: any ruling on proceeding through Steps 21 and 22 on a CLOSED-QUALIFIED Step 19 gate under an R-25 deferral. It blocks no AUD-D067 or AUD-D145 recording fix.

Ordering reason: this entry is a deep end of build ruling, so it sits near the end of the order.

#### Settlement under Captain JP's grant: DQ-098

Settled by: The Manager (Muse), under Captain JP's grant, in her words: "Go ahead and answer any of them yourself that seems simple enough. I care about security and quality over speed, i don't want things to be too strict that they're impossible, but they should be relatively strict to the standards they hold."

Strictness rule, in Captain JP's words: "If the stricter setting is not workable, then go with the workable. If the strict setting is workable go with it unless it adds a huge build time."

Settlement: A build may not proceed through Step 21 or Step 22 on a CLOSED-QUALIFIED Step 19 gate while the R-25 deferral behind it is unexpired. Steps 21 and 22 wait until the deferral ends, the defect is fixed and re-audited, and the gate stands unqualified, as R-3 already bars the Release-gate Keeper from passing a build carrying an unexpired deferred Critical or High qualification.

Deciding limb: strict workable. Source of settlement text and limb: classify-c.md.

Status: SETTLED by the Manager under the grant, not ruled by Captain JP. This item is settled.

### DQ-099: Calendar duties, inside the per build flow or a standing operations regime

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q50.

The question: Do the monthly, quarterly, and half year EDD duties belong inside a per build flow whose teams exist per stage and dissolve at build close, or in a separate standing operations regime outside the build flow? The unstaffed state of the duties is at register defect AUD-D074.

The options, stated plainly:

- Inside the per build flow.
- In a separate standing operations regime outside the build flow.

Cost of deciding late: medium. AUD-D074 names an owner on the current text; the cost is that the duties home regime stays unruled, so a later ruling may move them.

What it blocks: the home regime for the monthly, quarterly, and half year EDD duties. It blocks no AUD-D074 owner naming fix.

Ordering reason: this entry is a binary choice in form, but it decides where long running duties live, so it sits in the later half.

#### Settlement under Captain JP's grant: DQ-099

Settled by: The Manager (Muse), under Captain JP's grant, in her words: "Go ahead and answer any of them yourself that seems simple enough. I care about security and quality over speed, i don't want things to be too strict that they're impossible, but they should be relatively strict to the standards they hold."

Strictness rule, in Captain JP's words: "If the stricter setting is not workable, then go with the workable. If the strict setting is workable go with it unless it adds a huge build time."

Settlement: The monthly, quarterly, and half year EDD duties belong in the standing production phase regime outside the per build flow, held as standing role duties under R-179 and recorded in the production phase record, not by per build step teams. Each duty keeps the named standing owner its own rule states, in the form R-179 already uses for the duties it names.

Deciding limb: strict workable. Source of settlement text and limb: classify-c.md.

Status: SETTLED by the Manager under the grant, not ruled by Captain JP. This item is settled.

Implementation addition: the pending mapping is landed, on Captain JP ruling "Yes, write them in". A mapping passage now stands at LEVEL-1-STANDING.md, rule R-179, mapping every monthly, quarterly, and half year calendar duty to the standing owner its own rule states: the Auditor for judge re-validation under R-168, the falsifier audit under R-194, expansion stewardship under R-149, the pruning audit under R-187, the case portfolio review under R-207, the mutation testing audit run under R-195, the DeterminismMap review under R-196, the simulator calibration re-scoring under R-204, and the threat model review under duty 1 of R-210; the Project Manager for the pattern decision ledger recalibration at its quarterly review; the Metrics Reporter for the quarterly ledger report under R-206; and the Auditor for the half year gate gaming exercise under duty 2 of R-210, run by the rotating red role named in the production phase record. One duty names no owner in its own rule, the held-out escrow custody audit under R-211 in PLAID.md; the mapping records that it rides on the quarterly audit and that the Plaid part of the quarterly audit owner question stands open at DQ-129, not decided by the mapping. Corpus gate on the mapping wording, under the DQ-002 hard gate: PASS, corpus entries checked in full C-039, C-058, C-109, C-116, and C-128. Trace: banked-settlements-trace.md, completion section, DQ-099 row now LANDED.

### DQ-100: Plaid precondition failure at Step 1

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q51.

The question: If a Plaid build fails the five record changes precondition at Step 1, does it halt, wait, or proceed in the degraded reporting mode REPORTING.md describes for other tiers?

The options, stated plainly:

- Halt.
- Wait.
- Proceed degraded.

Cost of deciding late: high for a Plaid build in that position. Step 1 has no ruled outcome for a failed precondition, so the build cannot proceed on a settled basis.

What it blocks: any ruled outcome for a Plaid build that fails the five record changes precondition at Step 1.

Ordering reason: this entry is a short choice among three stated options, and can be answered in one tap, though it only bites at Plaid.

#### Ruling by Captain JP

Question as put on the Questions space: "A record must exist before a build's first step opens. If it is missing, what should happen?" Her answer, in her words: "Halt until it exists."

Ruled: if the Step 1 record precondition in PLAID.md section 3 fails, the build halts at Step 1 and does not open Step 2 until the five record changes exist. Landed in PLAID.md, section 3. Closed.

### DQ-101: Imagination required lenses below the full roster

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q52.

The question: Which of the eight imagination lenses in LEVEL-4 are required when the imagination base size is below the full roster (2 at Low, 4 at Medium and High)? The note-taking part of the same source candidate is settled by DQ-030; see register entry AUD-N8.

The options, stated plainly:

- A named required subset per tier.
- An express rule that listing does not require staffing, with the choice recorded per build.

Cost of deciding late: low to medium. Imagination teams below the full roster proceed with no ruled required subset, so coverage of the eight lenses varies by build.

What it blocks: any required imagination lens subset below the full roster, or any express no requirement rule for those lenses.

Ordering reason: this entry is a short choice between two stated forms, and can be answered in one line.

#### Settlement under Captain JP's grant: DQ-101

Settled by: The Manager (Muse), under Captain JP's grant, in her words: "Go ahead and answer any of them yourself that seems simple enough. I care about security and quality over speed, i don't want things to be too strict that they're impossible, but they should be relatively strict to the standards they hold."

Strictness rule, in Captain JP's words: "If the stricter setting is not workable, then go with the workable. If the strict setting is workable go with it unless it adds a huge build time."

Settlement: No named subset of the eight imagination lenses is required below the full roster, and listing a lens does not require staffing it. The stage team lead selects the lenses seated, records the selection and its reason in the step roster, and a lens a governing rule requires for the stage may not be left unseated.

Deciding limb: strict unworkable. Source of settlement text and limb: classify-c.md.

Status: SETTLED by the Manager under the grant, not ruled by Captain JP. This item is settled.

### DQ-102: Logic audit team form below Plaid

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q53.

The question: What staffing form does the logic audit team take below Plaid, the argument slice expansion form being stated in PLAID.md as the Plaid form only?

The options, stated plainly:

- The argument slice form applies at every tier in reduced counts.
- A distinct scope form under R-49 applies below Plaid, to be named in the ruling.

Cost of deciding late: medium. Logic audits below Plaid proceed with no ruled team form, so their staffing shape rests on practice rather than a ruling.

What it blocks: any ruled staffing form for the logic audit team below Plaid.

Ordering reason: this entry is a short choice between two stated forms, and can be answered in one line.

#### Fill-in under Captain JP's ruling at DQ-141: DQ-102

Settled by: The Manager (Muse), as a fill-in under Captain JP's ruling at DQ-141, in her words: "You fill it in, strict side."

Fill-in: The argument slice form stated in PLAID.md applies at every tier, in the per tier counts already ruled at DQ-017 (Low 5, Medium 15, High 25, Extra High 35, Plaid 35). No distinct second form applies below Plaid.

Lands: LEVEL-2-STEPS.md, in the introduction passage that defines the logic audit amounts, which stays the one defining home for the form and the amounts.

Status: SETTLED as a Manager fill-in under DQ-141, not ruled by Captain JP. The value set stands until Captain JP overrules it.

### DQ-103: FLOW.md plain language surface

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q54.

The question: Should the flow carry a short plain language companion surface for Captain JP and for first time operators, stating in ordinary words what each of the 23 steps is and what she will be asked to decide, or should FLOW.md remain the only outline and stay in the flow own terms?

The options, stated plainly:

- A short plain language companion surface is carried.
- FLOW.md remains the only outline, in the flow own terms.

Cost of deciding late: low. FLOW.md remains the only outline in the meantime, and first time operators read the flow in its own terms.

What it blocks: any plain language companion surface for the 23 steps.

Ordering reason: this entry sits near the top of its group. It is a binary scope choice, and can be answered in one tap.

#### Settlement under Captain JP's grant: DQ-103

Settled by: The Manager (Muse), under Captain JP's grant, in her words: "Go ahead and answer any of them yourself that seems simple enough. I care about security and quality over speed, i don't want things to be too strict that they're impossible, but they should be relatively strict to the standards they hold."

Strictness rule, in Captain JP's words: "If the stricter setting is not workable, then go with the workable. If the strict setting is workable go with it unless it adds a huge build time."

Settlement: The flow carries a short plain language companion to FLOW.md, stating in ordinary words what each of the 23 steps is and what Captain JP will be asked to decide at it. FLOW.md remains the governing outline, and where the companion and FLOW.md differ, FLOW.md governs.

Deciding limb: strict workable. Source of settlement text and limb: classify-c.md.

Status: SETTLED by the Manager under the grant, not ruled by Captain JP. This item is settled.

Implementation addition: the pending companion is landed, on Captain JP ruling "Yes, write them in". The companion stands at FLOW-PLAIN.md in ~/workspace/build-flow/, stating in ordinary words what each of the 23 steps is and what Captain JP will be asked to decide at it, and stating that it carries no rules of its own and that FLOW.md and the level documents govern where they differ. A pointer to it stands in FLOW.md, in the Companion files section. Corpus gate on the companion and pointer wording, under the DQ-002 hard gate: PASS, with the Gap and FM indexes searched by subject and corpus entry C-155 checked in full on the misrepresentation shape. Trace: banked-settlements-trace.md, completion section, DQ-103 row now LANDED.

### DQ-104: Orange lens standards and method

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q55.

The question: Against which named accessibility and plain language standard, if any, should the Orange lens judge: a published standard chosen by Captain JP, a standard written into this set, or the informed judgement of the holder recorded case by case?

The options, stated plainly:

- A published standard chosen by Captain JP.
- A standard written into this set.
- The informed judgement of the holder, recorded case by case.

Cost of deciding late: low to medium. The Orange lens judges by holder judgement in practice, with no named standard ruled.

What it blocks: any named accessibility and plain language standard for the Orange lens.

Ordering reason: this entry may require naming a specific published standard, which the queue ordering rule puts in the later half.

#### Settlement under Captain JP's pass 2 grant: DQ-104

Settled by: The Manager (Muse), under Captain JP's pass 2 grant, in her words: "Do another high discernment pass. I do not want the system to cheat itself or agents to cheat the system plus all the other stuff I said before."

Governing standard: the anti-cheat test first, that the system must not cheat itself and agents must not cheat the system, then Captain JP's settlement philosophy, security first, quality second, speed last, strict reading where workable unless it adds a huge build time, workable reading where strict is unworkable or too costly, neither good stays hers, and genuine redundancy removed with the surviving passage named, with DQ-138, the corpus gate governs over cost, and DQ-139, clashes decided by discernment on the merits and never by recency.

Settlement: The informed judgement of the Orange holder, recorded case by case, may not stand as the whole standard for the Orange lens. Each audit round must name the accessibility and plain language criteria it will judge against in its charge before examination begins, and the verdict form block must record those criteria. Holder judgement may be recorded as the application of those named criteria to a case, never as the criteria themselves.

Deciding ground: anti-cheat, system side, partial settlement.

Landing: RECORD-ONLY. Verified standing: R-54 charge, R-8 verdict form item 2, and the Orange agent files. No document edit was made for this settlement.

Flag recorded: convenience and cost pulled toward leaving holder judgement alone; anti-cheat governed for this limb.

Status: SETTLED IN PART by the Manager under the pass 2 grant, not ruled by Captain JP. The settled limb above is settled. What stays banked: the published standard versus written in standard choice and the identity of the standard stay banked, and this item stays banked for those limbs.

#### Completion under Captain JP's DQ-145 ruling: DQ-104

Completed by: The Manager (Muse), under Captain JP's DQ-145 ruling, in her words: "Yes, finish them that way."

Governing standard: the anti-cheat test first, then Captain JP's settlement philosophy as recorded in the pass 2 settlement above, with DQ-138 and DQ-139.

Completion: The standard choice is finished in favour of the second stated option: a standard written into this set. The published standard option is not taken, because the option as stated reserves the choosing of a published standard to Captain JP, and the holder judgement option stands excluded by the pass 2 settlement above. The standard is written at the Orange lens home in LEVEL-4 as a plain language list and an accessibility list in the set's own words: common words before jargon with unknown terms defined at first use, short sentences with one idea in each, headings that state their contents, instructions in acting order, and nothing a reader must already know left unstated; and for accessibility, a text alternative for every image, chart, and diagram, readable contrast, every action completable by keyboard alone, the reader's place always visible, errors and required actions stated in words and never by colour alone, nothing that flashes, and time limits announced and extendable. An audit round names in its charge the criteria from that list it will judge against, as the pass 2 settlement requires, and a surface failing a named criterion fails on that criterion, with the criterion recorded.

Deciding ground: anti-cheat, system side. Criteria stated in the set can be checked, charged, and traced; a standard held in one holder's judgement cannot, and a published standard is hers to choose, not the Manager's to pick for her.

Landing: LANDED, LEVEL-4-MEMBERS.md, the Orange standard passage following the Orange role list. Corpus gate under DQ-002: PASS, recorded in scratch-finishing/gate-record.md.

Status: SETTLED by the Manager, the pass 2 limb under the pass 2 grant and the remaining limbs under DQ-145, not ruled by Captain JP. This item is settled and closed as a Manager completion; Captain JP may overrule it.

### DQ-105: Owner of re-verification after an R-1 failure outside pushes

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q56.

The question: When verification fails or cannot be performed for an install checked on the live target or a test suite checked from a clean clone, who owns re-verification, what is the next action, and at what point is the failure brought to Captain JP? R-6 names the Estate Keeper for pushes only.

Cost of deciding late: medium. Such a failure outside pushes has no named re-verification owner, next action, or escalation point in the meantime.

What it blocks: any named owner, next action, or escalation point for re-verification after an R-1 failure outside pushes.

Ordering reason: this entry is a short naming choice, and can be answered in one line.

#### Settlement under Captain JP's grant: DQ-105

Settled by: The Manager (Muse), under Captain JP's grant, in her words: "Go ahead and answer any of them yourself that seems simple enough. I care about security and quality over speed, i don't want things to be too strict that they're impossible, but they should be relatively strict to the standards they hold."

Strictness rule, in Captain JP's words: "If the stricter setting is not workable, then go with the workable. If the strict setting is workable go with it unless it adds a huge build time."

Settlement: The Estate Keeper owns re-verification after an R-1 failure outside pushes, for installs on the live target and for test suites checked from a clean clone, as it already does for pushes, and the claimant never re-verifies its own item. The item stays PARTIAL until re-verification lands, and a failure that still cannot be verified is reported to the Project Manager at once and reaches Captain JP through the step packet, and through the queue where it blocks closure.

Deciding limb: strict workable. Source of settlement text and limb: classify-c.md.

Status: SETTLED by the Manager under the grant, not ruled by Captain JP. This item is settled.

### DQ-106: Captain JP decision queue intake limits

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q57.

The question: What session length, question volume, and decision queue intake is Captain JP willing to carry personally, and what may be delegated, batched, or defaulted when that limit is reached, and what happens to a build item waiting on a banked answer in the meantime?

Cost of deciding late: medium. The queue is presented with no ruled personal limit, so intake can exceed what Captain JP can carry in a session and waiting items have no ruled default.

What it blocks: any personal intake limit for this queue, and any delegation, batching, or default rule when that limit is reached.

Ordering reason: this entry sits last among its group. Only Captain JP can state her own carrying limit, and the answer sets the terms for every other item in this queue.

#### Settlement under Captain JP's pass 2 grant: DQ-106

Settled by: The Manager (Muse), under Captain JP's pass 2 grant, in her words: "Do another high discernment pass. I do not want the system to cheat itself or agents to cheat the system plus all the other stuff I said before."

Governing standard: the anti-cheat test first, that the system must not cheat itself and agents must not cheat the system, then Captain JP's settlement philosophy, security first, quality second, speed last, strict reading where workable unless it adds a huge build time, workable reading where strict is unworkable or too costly, neither good stays hers, and genuine redundancy removed with the surviving passage named, with DQ-138, the corpus gate governs over cost, and DQ-139, clashes decided by discernment on the merits and never by recency.

Settlement: No queue item is defaulted for want of a ruling, at an intake limit or at any other point. An item on which no ruling has landed stays in its Banked sub state, with blocker and decider named, and any build waiting on it stays blocked as its record states.

Deciding ground: anti-cheat, system side, partial settlement.

Landing: RECORD-ONLY. Verified standing: R-3 queue items mapping passage and decision-queue-clerk.md boundaries. No document edit was made for this settlement.

Flag recorded: load relief and speed pulled toward defaults; anti-cheat governed for this limb.

Status: SETTLED IN PART by the Manager under the pass 2 grant, not ruled by Captain JP. The settled limb above is settled. What stays banked: her session length, volume, and intake limit and the delegation at the limit stay banked, and this item stays banked for those limbs.

#### Scrutiny under Captain JP's DQ-145 ruling: DQ-106

Examined by: The Manager (Muse), under Captain JP's DQ-145 ruling, in her words: "Yes, finish them that way."

Scrutiny outcome: The remaining limbs are not finished. What remains in this item is a statement of Captain JP's own session length, question volume, and decision queue intake limit, and what she delegates when that limit is reached. Those are statements only she can make about her own carrying capacity, and her Decision-queue Clerk's recorded boundary already states that the queue's keeper does not answer a queued question on her behalf. No source in the flow states her limit, and the finishing ruling's strict side cannot supply a personal fact about her. The no default limb settled above stands as the whole protection in the meantime: nothing is defaulted for want of a ruling, at any volume. No document edit is made for this item in this run.

Status: SETTLED IN PART stands, the no default limb under the pass 2 grant. The remainder stays banked. Reason, in one line: her personal intake limit and what she delegates at it are hers alone to state, and cannot be set for her.

#### Ruling by Captain JP

Question as put on the Questions space: "When questions pile up for you, what should happen past your limit?" Her answer, in her words: "Hold them until I ask.But also , you should be able to answer a lot of the questions that you ask, the goal is to minimize my involvement.So only ask me a question when it's absolutely necessary.And you don't have the ability to discern , what is the choice that meets my principles , the most"

Ruled: questions past her limit are held until she asks. The Manager answers most questions itself under its recorded delegations and settlements; a question is presented to Captain JP only when it is absolutely necessary, that is, when the Manager cannot discern which choice best meets her principles. The ruling is recorded as the standing intake rule in this queue's header, so it governs future queue work. With the no default settlement recorded above standing under the same rule, the item closes in full.

### DQ-107: Product Owner deputy function

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q58.

The question: Should the named deputy for each behaviour in product-owner.md act when the owner is unavailable, and with what authority, or should the deputy be removed from the record as a name with no function?

The options, stated plainly:

- The deputy acts when the owner is unavailable, with the authority named in the ruling.
- The deputy is removed from the record as a name with no function.

Cost of deciding late: low. The deputy stays named with no function in the meantime, and an unavailable owner has no ruled stand in.

What it blocks: any deputy function or authority in product-owner.md, or the removal of the deputy from that record.

Ordering reason: this entry is a binary choice, act or remove, and can be answered in one tap.

#### Settlement under Captain JP's pass 2 grant: DQ-107

Settled by: The Manager (Muse), under Captain JP's pass 2 grant, in her words: "Do another high discernment pass. I do not want the system to cheat itself or agents to cheat the system plus all the other stuff I said before."

Governing standard: the anti-cheat test first, that the system must not cheat itself and agents must not cheat the system, then Captain JP's settlement philosophy, security first, quality second, speed last, strict reading where workable unless it adds a huge build time, workable reading where strict is unworkable or too costly, neither good stays hers, and genuine redundancy removed with the surviving passage named, with DQ-138, the corpus gate governs over cost, and DQ-139, clashes decided by discernment on the merits and never by recency.

Settlement: The named deputy for a behaviour is removed from the record and holds no acting authority. A behaviour whose product owner is unavailable has no stand in, and acts that need the owner wait until the owner is available. The behaviour spec file names the owner only, and gate policy for the behaviour stays joint between the product owner and the engineering lead as R-185 states.

Deciding ground: anti-cheat, agent side.

Landing: LANDED, deputy struck in product-owner.md (4 places), LEVEL-2 R-154 and Phase 0 exit criteria, LEVEL-3 R-185, project-manager.md; zero occurrences of deputy remain in the live flow documents and agent files.

Status: SETTLED by the Manager under the pass 2 grant, not ruled by Captain JP. This item is settled.

### DQ-108: Translation accuracy check

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q59.

The question: Should a translation accuracy check exist beyond the presence checks against the source outline, held by which role, with what qualification in the target language, and with what consequence for a section found mistranslated?

Cost of deciding late: low. Translation is checked for presence against the source outline only; the cost is that a mistranslated section can pass those checks.

What it blocks: any translation accuracy check, its holder, its qualification, and its consequence for a mistranslated section.

Ordering reason: this entry needs a holder and a qualification that no source states, so it sits in the later half.

Partial ruling, existence limb: RULED by Captain JP. The question as put to her: "Translated sections are only checked that they exist, never that the words are right. Add a real accuracy check?" Her answer, quoted exactly: "Yes, add the check."

Ruling outcome, existence limb: a translation accuracy check exists beyond the presence checks against the source outline. No document landing is made under this limb alone: the landing follows when the consequence limb is ruled, so the check and its consequence land together. This entry stays open in part for the consequence limb, the consequence for a section found mistranslated, which is being put to Captain JP next, and then for the holder and qualification limbs.

#### Fill-in under Captain JP's ruling at DQ-141: DQ-108, holder and qualification limbs

Settled by: The Manager (Muse), as a fill-in under Captain JP's ruling at DQ-141, in her words: "You fill it in, strict side."

Fill-in: Holder: the translation accuracy check is held by the Fold-in Tracer of the step that relies on the translation, and never by the agent that produced the translation. Qualification: the holder works from the source text itself, and records in the check record the basis on which it reads the target language; a holder that cannot read the target language does not hold the check, and the check waits until a holder who can read it is seated.

Scope: This fill-in covers the holder limb and the qualification limb only. The consequence limb is untouched by this fill-in and still open with Captain JP.

Implementation: Pending. No document landing is made in this run. This fill-in lands together with the consequence ruling, when that limb is ruled.

Status: SETTLED in part as a Manager fill-in under DQ-141, not ruled by Captain JP. The values set stand until Captain JP overrules them.

#### Ruling by Captain JP

Question as put on the Questions space: "A section is found mistranslated. Does that fail its step?" Her answer, in her words: "Yes, it fails."

Ruled in full: the translation accuracy check ruled at this item's existence limb runs as the DQ-141 fill-in recorded above sets it out (held by the Fold-in Tracer of the step that relies on the translation, never by the agent that produced it, working from the source text, the basis for reading the target language recorded, the check waiting if the holder cannot read the language), and a section found mistranslated fails its step. Landed together in LEVEL-2-STEPS.md at R-12. Closed.

### DQ-109: Live proof single exercise of a route, re-rule of DQ-010

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q60.

The question: This entry asks Captain JP to re-rule her own earlier ruling at DQ-010. Should the live proof floor in R-11 be raised above one exercise per claimed route? DQ-010 already ruled on this passage (no universal floor, judged claim by claim, R-11 stands as written), so this entry asks Captain JP to re-rule DQ-010; it is not a defect.

Cost of deciding late: low. The DQ-010 ruling stands and live proofs are judged claim by claim under R-11 as written.

What it blocks: any raising of the R-11 live proof floor above one exercise per claimed route. It blocks no live proof under the current ruling.

Ordering reason: this entry sits last among short items in its group. It asks Captain JP to re-rule her own earlier ruling, so it needs her full attention rather than a burst answer.

#### Assessment under DQ-148 (ruling by Captain JP: "Use desernment")

The challenge does not hold. DQ-010 ruled no universal floor, judged claim by claim, and R-11 stands as written; the stronger form already exists where it belongs, at Plaid, where every route and every leg runs and a bounded leg is a failed proof (PLAID.md section 3). A universal raised floor would replace claim by claim judgement with the universal floor DQ-010 declined. The earlier ruling stands. Closed as decided under DQ-148.

### DQ-110: Spawn record attestation strength, re-rule of DQ-008 and DQ-011

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q61.

The question: This entry asks Captain JP to re-rule her own earlier rulings at DQ-008 and DQ-011. Should an integrity mechanism or verifier be required for spawn records themselves, beyond the runtime kept record? DQ-008 settled the spawn record as the signature equivalent for a seat attestation and DQ-011 ruled attested closure operates at that L2 strength, so this entry asks Captain JP to revisit those settlements; the passages stand in their settled form and no defect is entered.

Cost of deciding late: low. The DQ-008 and DQ-011 settled form stands in the meantime, and attested closure operates at that strength.

What it blocks: any integrity mechanism or verifier requirement for spawn records beyond the runtime kept record, and any change to the DQ-008 or DQ-011 settled strength.

Ordering reason: this entry sits last among short items in its group. It asks Captain JP to re-rule two of her own earlier rulings, so it needs her full attention rather than a burst answer.

#### Assessment under DQ-148 (ruling by Captain JP: "Use desernment")

The challenge does not hold as stated. The strength question already has its commissioned route: DQ-012 commissioned the isolated checker as the instrument for stronger provenance, and until it exists no record may be labelled above L2 (R-81). Requiring an integrity mechanism for spawn records now, with no instrument in existence, would either invent one or bar attested closure altogether; neither is an outcome the record supports. DQ-008 and DQ-011 stand, with the DQ-012 instrument as the standing route to any stronger claim. Closed as decided under DQ-148.

### DQ-111: Capacity priority when spawns bind

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q62.

The question: What priority and clearance rules should the flow carry when capacity binds: which base seats have priority, whether recording a tier (in particular Plaid) requires a capacity clearance first, and how a step that can neither staff nor suspend proceeds beyond recording?

Cost of deciding late: medium to high when capacity binds. A step in that position has no ruled priority, clearance, or way forward beyond recording.

What it blocks: any capacity priority rule, any tier capacity clearance, and any ruled way forward for a step that can neither staff nor suspend.

Ordering reason: this entry is a deep ruling about staffing under scarcity, so it sits near the end of the order.

#### Fill-in under Captain JP's ruling at DQ-141: DQ-111

Settled by: The Manager (Muse), as a fill-in under Captain JP's ruling at DQ-141, in her words: "You fill it in, strict side."

Fill-in: Priority order when capacity binds: first the step's gate seats (the Auditor, the review board, and the attested closure verifier where the tier requires one); second the standing roles the step needs; third the step's base team seats; fourth Manager additions and any extra seats. Recording a tier for a build requires a capacity clearance recorded by the Project Manager at the grill, stating that the tier's union total fits the capacity then in force; the same rule covers Plaid. A step that can neither staff to its tier nor suspend under the halt rules does not proceed short staffed: it halts, records the capacity failure, and waits for capacity or a queue ruling; seats are never merged to make the numbers fit.

Lands: LEVEL-1-STANDING.md, at R-4, for the tier capacity clearance, and LEVEL-2-STEPS.md, at R-21, for the priority order, the halt on capacity failure, and the bar on merging seats.

Status: SETTLED as a Manager fill-in under DQ-141, not ruled by Captain JP. The value set stands until Captain JP overrules it.

### DQ-112: Budget set at Step 3 before the Grill settles scope at Step 4

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q63.

The question: Should the budget be reset or formally revalidated at Grill close against the settled scope, by whom, and how is a superseded budget recorded? This is distinct from DQ-092, from register entry AUD-Q43, which asks who sets the budget in the first place.

Cost of deciding late: medium. A Step 3 budget can stand against a Grill settled scope that differs from it, with no reset or revalidation ruled.

What it blocks: any budget reset or revalidation at Grill close, its holder, and any record form for a superseded budget.

Ordering reason: this entry is a short choice in form, but it governs every build budget, so it sits in the middle of the order.

#### Assessment under DQ-143

Assessed under Captain JP's money ruling, DQ-143, in her words: "Use discernment if you should ask me." This item falls on the side of the line that comes to Captain JP: a reset of the budget at Grill close is a budget change, and its holder question is the same budget authority question as DQ-092, which the ruling reserves to her. Only the record form for a superseded budget is mechanics, and settling that form ahead of the authority it serves would pre-decide her question; that limb is recorded here as settleable by the Manager once DQ-092 is ruled. Status: Banked, marked as hers under DQ-143. No settlement is made.

#### Ruling by Captain JP

Question as put on the Questions space: "When the grill closes, should the build's budget start over fresh?" Her answer, in her words: "Keep the budget , but you can ask for more"

Ruled: a build's budget is not reset when the Grill closes; the build keeps its budget, and more may be asked for. The authority for giving more is DQ-092's ruling: the Manager gives more after a TIMED-OUT stop, within the limit Captain JP sets, recorded at DQ-092. Landed in LEVEL-2-STEPS.md at Step 3, with DQ-092's authority. Closed.

#### Aligning note under Captain JP's further ruling at DQ-092

The ruling block in this entry points at "the limit Captain JP sets, recorded at DQ-092". That limit is now recorded at DQ-092 in its ruled form: there is no standing numeric limit on top of the set budget, the limit is the set budget itself, and more beyond the set budget is given only by asking Captain JP, with her answer governing. The sentence in this entry that more may be asked for under the same authority reads in that form. Landed with DQ-092 in LEVEL-2-STEPS.md at Step 3. This entry stays closed as ruled; this block aligns its pointer only.

### DQ-113: Closure by Captain JP ruling, precedence and record form

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q64.

The question: Outside the R-7 bounded exception, must a closure ruling by Captain JP still meet the 100 percent LANDED trace condition, may it waive the condition, or does it produce a third recorded form, and should such a ruling carry a minimum record (the elements waived, named as waived) beyond the R-90 transition entry fields? Only Captain JP can decide the reach of her own ruling power.

The options, stated plainly:

- A closure ruling must still meet the 100 percent LANDED trace condition.
- A closure ruling may waive the condition.
- A closure ruling produces a third recorded form.

Cost of deciding late: high if such a ruling is given before this entry is answered. Its precedence over the trace condition and its record form would be unruled at the moment it is relied on.

What it blocks: any settled precedence or record form for closure by Captain JP ruling outside the R-7 bounded exception.

Ordering reason: this entry sits last. It concerns the reach of Captain JP own ruling power over the closure bar, so it is the deepest ruling in its group.

Assessment under DQ-144: Captain JP has ruled that whether one of her rulings reaches a case it did not name is decided case by case, by discernment on the ruling's words and the case's facts, with no standing rule in either direction. Read under that ruling, a closure ruling of hers, once given, is applied to each case on its own facts: where it plainly covers the case it governs, where it plainly does not the case is open, and where it is genuinely unclear the case comes back to her. This entry's own question is not decided by that ruling and stays banked for Captain JP, for one reason: whether her closure ruling may waive the 100 percent LANDED trace condition at all, and what record such a ruling must carry, is a question about what her ruling power is, and discernment under a ruling cannot extend or limit her own power. Status unchanged: Banked.

#### Ruling by Captain JP

Question as put on the Questions space: "May one of your own closure rulings waive the rule that every element must land before a step closes?" Her answer, in her words: "No, never."

Ruled: no closure ruling of Captain JP's waives the 100 percent LANDED trace condition in R-7; a stage whose trace stands below 100 percent LANDED is not closed by ruling. Landed in LEVEL-2-STEPS.md at R-7, with the reconciling sentence the two texts needed: the DQ-016 bounded exception is not a waiver by ruling but an in-the-moment decision on a live case, recorded in that moment with its four elements, and it is the only route past the condition. Closed.

### DQ-114: How many routes into CLOSED-QUALIFIED exist, including the R-25 deferral route

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q65.

The question: Should CLOSED-QUALIFIED have one route (the R-7 exception) or three (adding the R-25 deferral route and the R-27 recorded non pass route), and if the R-25 route stands, should a deferral ruling ever convert an unmet R-17 exit bar into a qualified closure rather than holding the gate open? The downstream recording defects that exist on either answer are at register defect AUD-D145.

The options, stated plainly:

- One route, the R-7 exception only.
- Three routes, adding the R-25 deferral route and the R-27 recorded non pass route.

Cost of deciding late: medium to high. Qualified closures are recorded under the routes as they stand, while the number of routes itself stays unruled, and AUD-D145 records the downstream position on either answer.

What it blocks: any settled count of routes into CLOSED-QUALIFIED, and any ruling on whether a deferral can convert an unmet R-17 bar into a qualified closure.

Ordering reason: this entry is a deep closure ruling tied to the R-7 bar, so it sits near the end of the order.

#### Settlement under Captain JP's pass 2 grant: DQ-114

Settled by: The Manager (Muse), under Captain JP's pass 2 grant, in her words: "Do another high discernment pass. I do not want the system to cheat itself or agents to cheat the system plus all the other stuff I said before."

Governing standard: the anti-cheat test first, that the system must not cheat itself and agents must not cheat the system, then Captain JP's settlement philosophy, security first, quality second, speed last, strict reading where workable unless it adds a huge build time, workable reading where strict is unworkable or too costly, neither good stays hers, and genuine redundancy removed with the surviving passage named, with DQ-138, the corpus gate governs over cost, and DQ-139, clashes decided by discernment on the merits and never by recency.

Settlement: Three routes into CLOSED-QUALIFIED stand, each confined to its own subject, and no route deems an unmet bar met. The R-7 route is the only route that closes a stage over outstanding trace elements, and it stands only in the bounded in the moment exception form ruled at DQ-016. The R-25 route may close a gate record at best as CLOSED-QUALIFIED where a Critical or High defect is deferred under a recorded ruling, and the R-27 route may record a release gate Go as CLOSED-QUALIFIED where a recorded non pass stands and that non pass is not a deferred Critical or High defect. A deferral never converts an unmet R-17 exit bar into an unqualified closure or into passage onward: the qualification travels with every citation, and Steps 21 and 22 wait while a deferral under R-25 is unexpired.

Deciding ground: strict workable.

Landing: RECORD-ONLY. Verified standing: R-3, R-25, R-27, and R-85. No document edit was made for this settlement.

Status: SETTLED by the Manager under the pass 2 grant, not ruled by Captain JP. This item is settled.

### DQ-115: R-181 queue purposes

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q66.

The question: What are the queue purposes that individuate the higher tier queues under R-181 (one queue per purpose at the higher tiers, one combined purpose tagged queue at the lower tiers)? No in-set list exists, so no fix can be written without this ruling. The four exit states part of the same source is settled as a defect at register defect AUD-D031, on the enumeration already carried in queue-owner.md.

Cost of deciding late: medium. Higher tier queues under R-181 cannot be individuated by purpose until the purposes are named, so that part of R-181 cannot be completed.

What it blocks: the queue purposes list under R-181, and with it any fix that needs that list. It blocks no AUD-D031 exit states fix.

Ordering reason: this entry requires naming a list no source supplies, so it sits in the later half.

#### Settlement under Captain JP's pass 2 grant: DQ-115

Settled by: The Manager (Muse), under Captain JP's pass 2 grant, in her words: "Do another high discernment pass. I do not want the system to cheat itself or agents to cheat the system plus all the other stuff I said before."

Governing standard: the anti-cheat test first, that the system must not cheat itself and agents must not cheat the system, then Captain JP's settlement philosophy, security first, quality second, speed last, strict reading where workable unless it adds a huge build time, workable reading where strict is unworkable or too costly, neither good stays hers, and genuine redundancy removed with the surviving passage named, with DQ-138, the corpus gate governs over cost, and DQ-139, clashes decided by discernment on the merits and never by recency.

Settlement: The queue purposes under R-181 are judge calibration, failure discovery, and safety review. At the higher tiers each purpose has its own queue, and at the lower tiers the single combined queue tags every item with one of these three purposes. No other purpose creates a queue or a tag under R-181.

Deciding ground: anti-cheat, system side.

Landing: LANDED, LEVEL-1 R-181 opening, line 307.

Status: SETTLED by the Manager under the pass 2 grant, not ruled by Captain JP. This item is settled.

### DQ-116: Digest scope class, definition, values and assigner

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q67.

The question: What is scope class in REPORTING.md Report 3, what are its values, and who assigns it to a build, recorded where?

Cost of deciding late: low. Report 3 carries a scope class term with no definition, values, assigner, or record place ruled.

What it blocks: any definition, value set, assigner, or record place for digest scope class in Report 3.

Ordering reason: this entry is a definitional ruling with no definition supplied in any source, so it sits in the later half.

#### Fill-in under Captain JP's ruling at DQ-141: DQ-116

Settled by: The Manager (Muse), as a fill-in under Captain JP's ruling at DQ-141, in her words: "You fill it in, strict side."

Fill-in: Scope class names the span one digest row covers. Its values are single build; programme, a named set of builds under one programme; and estate, all builds in the digest period. The Metrics Reporter assigns the class when the row is written, and the class is recorded in the row itself; a row with no class recorded is incomplete.

Landing: LANDED, REPORTING.md, Report 3, Contents, as the Scope class bullet before the Comparison groupings bullet.

Status: SETTLED as a Manager fill-in under DQ-141, not ruled by Captain JP. The value set stands until Captain JP overrules it.

### DQ-117: Standing role charters under R-86, chartered or struck, role by role

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q68.

The question: For each standing role whose R-5 entry states no addressee or no power, is the role chartered (and with what addressee and power) or struck? The recording defect in the interval is at register defect AUD-D006; the rulings themselves are Captain JP to give.

Cost of deciding late: medium. The affected roles stay marked under AUD-D006 with their charter content unruled, so their addressee and power rest on their own definitions alone.

What it blocks: the charter or striking of each standing role whose R-5 entry states no addressee or no power under R-86. It blocks no AUD-D006 recording or marking fix.

Ordering reason: this entry sits last among its group. It is a role by role ruling across several standing roles, not a single choice.

Decision under DQ-146: RULED by Captain JP, closed. Her ruling on the role charters (DQ-146) decides this item. The charters are no longer reserved to her word for word: the Manager may make a minor charter amendment, one of wording, of clarity, or of aligning a charter with rulings already landed, recorded as a Manager amendment under that ruling. What this item poses, chartering a role with its addressee and its power, or striking a role, is a major amendment under that ruling, because it changes what a role is and what authority it holds, or removes a role, so each such decision comes to Captain JP before it is made, and an amendment whose class is genuinely unclear is treated as major and comes to her. The referral this item records stands decided in that form: the unchartered roles stay reported as unchartered in the interval, and no chartering or striking under this item is made by the Manager. The R-86 reservation stands amended by the ruling wherever R-86 states it, landed at LEVEL-1, R-86.

### DQ-118: Tier raising mid build below the Plaid line

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q69.

The question: Who may raise a build tier mid build between the non Plaid tiers, does the raising trigger the same staffing review as a lowering under R-4, and do stages already closed at the lower tier stand, stand qualified, or get restaffed?

Cost of deciding late: medium. A mid build raising below Plaid has no ruled authority, review trigger, or treatment of closed stages in the meantime.

What it blocks: any authority, staffing review, or closed stage treatment for raising a tier mid build below the Plaid line.

Ordering reason: this entry is a deep tier ruling with three linked parts, so it sits in the later half.

#### Ruling by Captain JP

Question as put on the Questions space: "May a build's tier be raised in the middle of the build, and who approves it?" Her answer, in her words: "Raised but never lowered and a notification"

Ruled: a build's tier may be raised mid-build, never lowered, and Captain JP is notified of a raise. Her answer does not name who raises it; the reading recorded here is discernment, stated plainly as a reading: the Manager raises, upward only, notifying her when the raise is made, and tier assignment at a build's start stays as R-4 states it. The two limbs of the question her answer did not reach (whether a raise triggers the staffing review a lowering triggers, and what happens to stages already closed) are decided on the strict reading her DQ-142 ruling sets: a raise triggers a staffing review of every stage not yet closed, as a lowering does, and a stage already closed keeps its record at the tier it closed at, is never restated, and carries no claim of raised-tier staffing. A raise never selects Plaid, which only Captain JP selects. Landed in LEVEL-1-STANDING.md at R-4. The first drafted wording, silent on the two unanswered limbs, failed the corpus gate (C-119, C-137, C-179, C-186); the landed wording carries the limbs as decided above and was re-gated clean; the gate record is in the batch trace. Closed.

### DQ-119: Whether the R-7 exception and qualified gate closures are available at Plaid

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q70.

The question: Does the maximum tier remove every qualified closure form, or only the qualified live proof that PLAID.md section 3 bars expressly, given that PLAID.md section 6 states Plaid changes nothing about closure?

Cost of deciding late: high at Plaid. A qualified closure at Plaid has no ruled standing, while section 3 and section 6 point in different directions on the reading the question names.

What it blocks: any ruling on which qualified closure forms are available at Plaid.

Ordering reason: this entry is a deep Plaid closure ruling, so it sits near the end of the order.

#### Ruling by Captain JP

Question as put on the Questions space: "At Plaid, may a step close as qualified, or must every Plaid step close clean?" Her answer, in her words: "Clean only at Plaid."

Ruled: at Plaid a step closes clean only. The qualified closure forms are not available at Plaid: a Plaid step closes CLOSED-PASS or not at all, and the R-7 bounded in-the-moment exception does not run at Plaid. Landed in PLAID.md, section 6. Closed.

### DQ-120: Captain JP authority over the release gate

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q71.

The question: Does Captain JP general power to close any stage by ruling under R-7 extend to passing, failing, or overturning a release gate, or does the Release-gate Keeper sole authority at Step 22 under R-27 bind even her?

Cost of deciding late: medium to high at a release gate. The Keeper sole authority and Captain JP general ruling power have no ruled precedence between them for that gate.

What it blocks: any settled precedence between Captain JP ruling power under R-7 and the Release-gate Keeper sole authority under R-27 at Step 22.

Ordering reason: this entry sits last among its group. It concerns the reach of Captain JP own authority against a sole authority rule, so it is a deep ruling.

Assessment under DQ-144: Captain JP has ruled that whether one of her rulings reaches a case it did not name is decided case by case, by discernment on the ruling's words and the case's facts, with no standing rule in either direction. Read under that ruling, her general power to close a stage by ruling under R-7 is neither held to reach the Step 22 release gate by standing rule, nor held back from it by standing rule: a live case of that power meeting the Release-gate Keeper sole authority under R-27 is decided on its facts, and where the reach is genuinely unclear the case comes to Captain JP. This entry's own question is not decided by that ruling and stays banked for Captain JP, for one reason: settled precedence between her ruling power and the Keeper's sole authority would fix what her ruling power is, and discernment under a ruling cannot extend or limit her own power. Status unchanged: Banked.

#### Ruling by Captain JP

Question as put on the Questions space: "At the release gate, the Release-gate Keeper alone can pass or fail it. If one of your rulings clashes with his call at a live gate, whose word stands?" Her answer, in her words: "The Keeper's gate stands."

Ruled: at a live release gate, the Release-gate Keeper's verdict stands over a clashing general ruling of Captain JP's. Her rulings change the rules the gate applies for later builds, not the verdict of a gate already sitting. Landed in LEVEL-2-STEPS.md at R-27. Closed.

### DQ-121: Approval of a next version direction

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q72.

The question: Does a next version direction decided by the Project Manager under R-28 need Captain JP approval before it is treated as decided, and if so at what point?

Cost of deciding late: low. Next version directions are decided by the Project Manager with their approval standing unruled in the meantime.

What it blocks: any Captain JP approval requirement, or approval point, for a next version direction under R-28.

Ordering reason: this entry is a short approval choice, and can be answered in one line.

#### Settlement under Captain JP's grant: DQ-121

Settled by: The Manager (Muse), under Captain JP's grant, in her words: "Go ahead and answer any of them yourself that seems simple enough. I care about security and quality over speed, i don't want things to be too strict that they're impossible, but they should be relatively strict to the standards they hold."

Strictness rule, in Captain JP's words: "If the stricter setting is not workable, then go with the workable. If the strict setting is workable go with it unless it adds a huge build time."

Settlement: No approval by Captain JP is required before a next version direction under R-28 counts as decided. The Project Manager decision, recorded at Step 23 close through that step ordinary Auditor gate, is the decided direction.

Deciding limb: strict workable. Source of settlement text and limb: classify-d.md and refinement-abd.md Part 1 limb audit.

Status: SETTLED by the Manager under the grant, not ruled by Captain JP. This item is settled.

### DQ-122: Plaid tier warrant thresholds

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q73.

The question: Should the Plaid warrant terms (money at real volume, a security surface whose failure exposes Captain JP or her users, a public surface whose failure is not recoverable by a quiet fix) carry thresholds Captain JP sets, or remain matters of her recorded judgement case by case?

The options, stated plainly:

- Thresholds set by Captain JP for the Plaid warrant terms.
- The warrant terms remain matters of Captain JP recorded judgement, case by case.

Cost of deciding late: low. Plaid assignment continues on recorded judgement, which is one of the two stated options in practice.

What it blocks: any thresholds for the Plaid warrant terms.

Ordering reason: this entry concerns the reserved Plaid area, so it sits in the later half despite its short form.

#### Ruling by Captain JP

Question as put on the Questions space: whether the Plaid warrant terms carry fixed thresholds, as recorded in this entry. Her answer, in her words: "Fixed thresholds I set."

Ruled: the Plaid warrant terms named in PLAID.md section 1 (money at real volume; a security surface whose failure exposes Captain JP or her users; a public surface whose failure is not recoverable by a quiet fix) carry fixed thresholds set by Captain JP. This ruling fixes the form: the thresholds are fixed and they are hers to set. The values stand unnamed: Captain JP has set no values, and that state is stated plainly here. Landed in PLAID.md section 1 in that form: the threshold values stand unnamed until she names them, until they are named no warrant call may rest on numbers nobody set, and Plaid selection stays exactly as section 1 already rules it, by her recorded ruling alone. Closed as ruled.

### DQ-123: Confirming human for side effect actions

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q74.

The question: Who is the confirming human for side effect actions under PLAID.md R-142 and the LEVEL-3 tool permission rules: Captain JP herself, or another named person, through what channel, and what happens while confirmation is outstanding? The related labeller staffing defect is at register defect AUD-D105.

Cost of deciding late: medium to high for a side effect action needing confirmation. No confirming human, channel, or pending state is ruled, so such an action waits with no settled route.

What it blocks: any named confirming human, channel, or pending rule for side effect actions under R-142 and the LEVEL-3 tool permission rules.

Ordering reason: this entry requires naming a specific person and a channel, which the queue ordering rule puts at the end.

#### Fill-in under Captain JP's ruling at DQ-141: DQ-123

Settled by: The Manager (Muse), as a fill-in under Captain JP's ruling at DQ-141, in her words: "You fill it in, strict side."

Fill-in: The confirming human for side effect actions is Captain JP herself. The channel is her recorded answer in the build's chat or approval record, the same channel as her rulings. While confirmation is outstanding the action does not proceed; the request stands recorded as pending, and no silence, lapse of time, or prior approval of a different action counts as confirmation.

Landing: LANDED, PLAID.md, rule R-142, Authorisation outside the model, and LEVEL-3-TEAMS.md, Tool permission rules passage under R-142, in the condensed form that passage carries.

Status: SETTLED as a Manager fill-in under DQ-141, not ruled by Captain JP. The value set stands until Captain JP overrules it.

### DQ-124: Whether a step approval over NOT RECORDED metrics should be qualified

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q75.

The question: Should an approval recorded over a step snapshot carrying NOT RECORDED figures be qualified in the approval row, and if so in what form? The gate passage as written is not a defect; see register entry AUD-N20.

Cost of deciding late: low. Approvals are recorded unqualified over such snapshots in the meantime, with the figures labelled in the snapshot itself.

What it blocks: any qualified form for a step approval recorded over NOT RECORDED metrics.

Ordering reason: this entry is a short record form choice, and can be answered in one line. The wider closure question for such figures is at DQ-076, from register entry AUD-Q27.

#### Settlement under Captain JP's grant: DQ-124

Settled by: The Manager (Muse), under Captain JP's grant, in her words: "Go ahead and answer any of them yourself that seems simple enough. I care about security and quality over speed, i don't want things to be too strict that they're impossible, but they should be relatively strict to the standards they hold."

Strictness rule, in Captain JP's words: "If the stricter setting is not workable, then go with the workable. If the strict setting is workable go with it unless it adds a huge build time."

Settlement: A step approval recorded over a step snapshot carrying NOT RECORDED figures is not qualified. The approval is recorded in the ordinary four outcome form, and the NOT RECORDED labels remain in the snapshot itself, which is context for the ruling and never a criterion for it.

Deciding limb: strict workable. Source of settlement text and limb: classify-d.md and refinement-abd.md Part 1 limb audit.

Status: SETTLED by the Manager under the grant, not ruled by Captain JP. This item is settled.

### DQ-125: Whether pattern gate outcomes should enter the per build gate outcome review

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q76.

The question: Should pattern gate outcomes under R-223 also be reviewed for an all Go pattern, or does the per build review under R-51 (as amended at register defect AUD-D131) stay scoped to approval rows, which is all F-8 counts?

The options, stated plainly:

- Pattern gate outcomes under R-223 are also reviewed for an all Go pattern.
- The per build review under R-51 stays scoped to approval rows, which is all F-8 counts.

Cost of deciding late: low. The per build review stays scoped to approval rows in the meantime.

What it blocks: any inclusion of R-223 pattern gate outcomes in the per build gate outcome review under R-51.

Ordering reason: this entry is a binary scope choice, and can be answered in one tap.

#### Settlement under Captain JP's grant: DQ-125

Settled by: The Manager (Muse), under Captain JP's grant, in her words: "Go ahead and answer any of them yourself that seems simple enough. I care about security and quality over speed, i don't want things to be too strict that they're impossible, but they should be relatively strict to the standards they hold."

Strictness rule, in Captain JP's words: "If the stricter setting is not workable, then go with the workable. If the strict setting is workable go with it unless it adds a huge build time."

Settlement: Pattern gate outcomes under R-223 are reviewed for an all Go pattern in the per build gate outcome review under R-51, in their gate record and ledger form, as R-223 already places them inside that review. The F-8 distribution is unchanged and still counts approval rows only.

Deciding limb: strict workable. Source of settlement text and limb: classify-d.md and refinement-abd.md Part 1 limb audit.

Status: SETTLED by the Manager under the grant, not ruled by Captain JP. This item is settled.

### DQ-126: Per step counting convention for standing roles

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q77.

The question: Should per step staffing totals, at Plaid and by extension at every tier, count every agent doing named work in a step, including standing role holders, or only the members of the step own teams, with standing support recorded separately? The unstated mixing in the current table is the defect at register defect AUD-D120. The board counting convention at register defect AUD-D070 is constrained by R-55 in addition wording and is not part of this question.

The options, stated plainly:

- Count every agent doing named work in a step, including standing role holders.
- Count only the members of the step own teams, with standing support recorded separately.

Cost of deciding late: medium. AUD-D120 states a convention on the current table; the cost is that the intended convention itself stays unruled, so a later ruling may restate the totals.

What it blocks: the intended per step counting convention for standing roles. It blocks no AUD-D120 table fix, and it does not cover the AUD-D070 board counting convention.

Ordering reason: this entry is a short choice between two stated conventions, and can be answered in one line.

#### Settlement under Captain JP's grant: DQ-126

Settled by: The Manager (Muse), under Captain JP's grant, in her words: "Go ahead and answer any of them yourself that seems simple enough. I care about security and quality over speed, i don't want things to be too strict that they're impossible, but they should be relatively strict to the standards they hold."

Strictness rule, in Captain JP's words: "If the stricter setting is not workable, then go with the workable. If the strict setting is workable go with it unless it adds a huge build time."

Settlement: Per step staffing totals count only the members of the step own teams and any holder named as a unit of the step. A standing role holder who does mandated work in a step without being named as a unit is recorded separately in the row as an uncounted exception and adds nothing to the total.

Deciding limb: strict workable. Source of settlement text and limb: classify-d.md and refinement-abd.md Part 1 limb audit.

Status: SETTLED by the Manager under the grant, not ruled by Captain JP. This item is settled.

### DQ-127: What R-55 no other board bars

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q78.

The question: Does the R-55 clause that board members count toward no team minimum and no other board bar a member from sitting on more than one board (in which case the Auditor cannot chair every step board), or does it only bar counting a member toward another board minimum (in which case he can)?

The options, stated plainly:

- The clause bars a member from sitting on more than one board, so the Auditor cannot chair every step board.
- The clause only bars counting a member toward another board minimum, so the Auditor can chair every step board.

Cost of deciding late: medium. Boards are chaired and sat with the clause read by practice, while its barred meaning stays unruled.

What it blocks: any settled reading of the R-55 no other board clause.

Ordering reason: this entry is a binary reading choice, and can be answered in one tap, though it decides whether one Auditor can chair every step board.

#### Settlement under Captain JP's grant: DQ-127

Settled by: The Manager (Muse), under Captain JP's grant, in her words: "Go ahead and answer any of them yourself that seems simple enough. I care about security and quality over speed, i don't want things to be too strict that they're impossible, but they should be relatively strict to the standards they hold."

Strictness rule, in Captain JP's words: "If the stricter setting is not workable, then go with the workable. If the strict setting is workable go with it unless it adds a huge build time."

Settlement: The R-55 clause bars counting a board member toward another board minimum only. It does not bar a member from sitting on more than one board, and the Auditor may chair every step board, subject to the R-73 bar where the Auditor commissioned the work under review.

Deciding limb: strict unworkable. Source of settlement text and limb: classify-d.md and refinement-abd.md Part 1 limb audit.

Status: SETTLED by the Manager under the grant, not ruled by Captain JP. This item is settled.

### DQ-128: Plaid independently verified

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 12 audit, register entry AUD-Q79.

The question: Does Plaid independently (FLOW.md: every step closure is independently verified) mean independent of the performer and the coordinator only, independent of the producing team, or independent of the build entirely? The verifier seat defect at register defect AUD-D033 is fixed on the R-80 and DQ-011 form for all tiers; this entry concerns only the Plaid word.

The options, stated plainly:

- Independent of the performer and the coordinator only.
- Independent of the producing team.
- Independent of the build entirely.

Cost of deciding late: medium at Plaid. Plaid verification proceeds on the AUD-D033 form for all tiers, while the stronger Plaid meaning of independently stays unruled.

What it blocks: any settled Plaid meaning of independently verified beyond the all tier form fixed at AUD-D033. It blocks no AUD-D033 fix.

Ordering reason: this entry sits last. It concerns the reserved Plaid area and the strongest verification claim in the flow, so it is a deep ruling.

#### Ruling by Captain JP

Question as put on the Questions space: "At Plaid, every step closure is independently verified. Must the verifier sit fully outside the build, or is outside the step's own team enough?" Her answer, in her words: "Fully outside the build."

Ruled: at Plaid, the independent verification of a step closure is by an agent fully outside the build, who is neither the step's coordinator nor a member of any of the build's teams and holds no seat on the build. Landed in PLAID.md, section 3, replacing the earlier outside the step's own team form. Closed.

### DQ-129: Owner of the quarterly audit

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 13 repair loop, register defect AUD-D074 (PLAID part).

The question: several rules presuppose a quarterly audit (among them R-211 in PLAID.md, and the quarterly audit run and review duties at R-195 and R-196), and the Step 13 repair attached the periodic duties themselves to the production phase under the Auditor as a standing role. Which role owns and convenes the quarterly audit itself is named nowhere in the set. Who owns it?

The options, stated plainly:

- The Auditor, as a standing role duty in the production phase under R-179, in the same form the repair gave the periodic duties it hosts.
- The Estate Keeper, as part of its estate watching cadence.
- A named standing institution created for the purpose, with its holder and cadence stated in the ruling.

Cost of deciding late: low to medium. The periodic duties have owners and records without this ruling; only the convening audit that asks the behaviour existence question lacks an owner, so a build that closes before the ruling carries the duties without that audit.

What it blocks: the PLAID part of register defect AUD-D074 only. No other repair waits on it.

Ordering reason: this entry and DQ-130 were banked by the Step 13 repair loop after DQ-050 to DQ-128, as the remainders of defects whose other parts were fixed. This one needs a role choice, so it sits after the audit questions proper.

#### Settlement under Captain JP's pass 2 grant: DQ-129

Settled by: The Manager (Muse), under Captain JP's pass 2 grant, in her words: "Do another high discernment pass. I do not want the system to cheat itself or agents to cheat the system plus all the other stuff I said before."

Governing standard: the anti-cheat test first, that the system must not cheat itself and agents must not cheat the system, then Captain JP's settlement philosophy, security first, quality second, speed last, strict reading where workable unless it adds a huge build time, workable reading where strict is unworkable or too costly, neither good stays hers, and genuine redundancy removed with the surviving passage named, with DQ-138, the corpus gate governs over cost, and DQ-139, clashes decided by discernment on the merits and never by recency.

Settlement: The quarterly audit is owned and convened by the Auditor, as a standing role duty in the production phase under R-179, with its roster recorded in the production record before the work opens. The custody audit under R-211 in PLAID.md rides on that same quarterly audit and has no separate owner or convening body.

Deciding ground: strict workable.

Landing: RECORD-ONLY. Verified standing: R-179 mapping, R-149, and R-187. Bookkeeping landing: the stale R-179 mapping sentence was updated, cross reference only, LEVEL-1 line 301, recording DQ-129 settled in this form.

Status: SETTLED by the Manager under the pass 2 grant, not ruled by Captain JP. This item is settled.

### DQ-130: Record home and entering owner for the promotion glance

Status: Banked

Owner of record: Decision-queue Clerk

Source: Step 13 repair loop, register defect AUD-D159 (R-176 part).

The question: R-176 in PLAID.md requires a human glance before trace data promotion, and R-212 and R-213 require the human review time to be recorded. The record home for the glance, and the gate owner who enters the glance record, are named nowhere in the set. Where does the glance record live, and who enters it?

The options, stated plainly:

- The admission record under R-213 is the home, entered by the owner of the promotion gate the glance serves.
- The behaviour ledger under R-206 is the home, entered by the owner of the promotion gate the glance serves.
- A glance entry in the build record, kept by the Metrics Reporter and entered by the owner of the promotion gate the glance serves.

Cost of deciding late: low. Promotion gates can run on the rest of R-176 as repaired; the glance they depend on has no citable record home until this is ruled, so a promotion made before the ruling cannot cite its glance.

What it blocks: the R-176 part of register defect AUD-D159 only. The METRICS part of that defect is fixed.

Ordering reason: banked with DQ-129 by the Step 13 repair loop. It is a short record form choice and can be answered quickly once DQ-129's ownership pattern is settled.

#### Settlement under Captain JP's grant: DQ-130

Settled by: The Manager (Muse), under Captain JP's grant, in her words: "Go ahead and answer any of them yourself that seems simple enough. I care about security and quality over speed, i don't want things to be too strict that they're impossible, but they should be relatively strict to the standards they hold."

Strictness rule, in Captain JP's words: "If the stricter setting is not workable, then go with the workable. If the strict setting is workable go with it unless it adds a huge build time."

Settlement: The promotion glance record lives in the admission record under R-213, the record that already carries human review time for admitted examples. It is entered by the owner of the promotion gate the glance serves.

Deciding limb: strict workable. Source of settlement text and limb: classify-d.md and refinement-abd.md Part 1 limb audit.

Status: SETTLED by the Manager under the grant, not ruled by Captain JP. This item is settled.

## Amendment note, 2026-11-10

Added by the Step 5 ruling agent (research-2, part (b)): nine new open items, DQ-006 to DQ-014, one for each Conflict ruling in the research-2 rulings (items C-9, C-17, C-18, C-63, C-64, C-65, C-67, C-70, C-98). They are appended after DQ-001 to DQ-005 and ordered among themselves easy to answer first, per the queue ordering rule: DQ-006 and DQ-007 are binaries, DQ-008 is a two-instrument choice, DQ-009 is a stage list choice, DQ-010 needs scope numbers or a decision to have none, DQ-011 and DQ-012 concern provenance strength and an unbuilt verifier, and DQ-013 and DQ-014 are definitional rulings with no measure supplied in any source. No existing item was moved, edited, or ruled by this amendment.

## Amendment note, 2026-11-10 (Step 5 revision after Contrarian attack)

Added and amended by the Step 5 ruling agent, on the revision recorded in section 8 of research-2-outside-implementation-trace.md. Two new open items are added below: DQ-015 (research-2 item C-68, its own carried question, hit H-44) and DQ-016 (research-2 item A-25, second clause, hit H-9). DQ-015 is placed before DQ-016 because it is a short choice about one power, while DQ-016 asks Captain JP to rule against or amend her own recorded closure ruling's application to a named case, which is the deeper ruling. Five existing items are amended by this note, and the amended wording in this note governs over the original item text where they differ:

- DQ-006 amended (hit H-45): the item now names the Auditor branch expressly. Under R-50 the Auditor may require additions as a condition of approving the next step's plan, which is commissioning that agent's work for the next step; the Auditor then audits that step as it was actually staffed, the spin-ups he required included, and under the revised board rule (final R-55 in the Step 5 revision) may chair its review board. That combination currently answers one branch of DQ-006 by silence, in favour of commissioning not disqualifying the Auditor. Captain JP's ruling on DQ-006 is asked on that live case, not only on the abstract question.
- DQ-008 amended (hit H-40): the earlier blocking note understated what the original rulings settled. As originally worded, the link rule did adopt the spawn record binding as the signature equivalent, in effect. That sentence is withdrawn by the Step 5 revision: links record a performer's spawn identity as a fact of the record, no rule in Step 5 calls that binding a signature, and the question in DQ-008 is open and unanswered by any implemented or prospective rule.
- DQ-009 amended (hit H-41): two elements formerly presented as open are implemented in effect and are struck from the question. The four-outcome gate vocabulary applies at the Auditor approval gate after every step (item A-3, final R-51), and entrance criteria, including disposition of the previous gate's action items, are recorded for each gate or review (item A-7, final R-53). The residue Captain JP rules on is only: which stages, if any, sit a review board under final R-55, and whether any stage is excepted from the gate outcome form.
- DQ-011 amended (hit H-39): the carve-out suggesting the strength element could be both blocked and implemented is struck. As revised, the provenance grades (final R-81) are definitions only and assign no grade to any record this flow produces, and attested closure operates at no graded provenance strength, with no grade label on closure records, until this item is ruled.
- DQ-014 amended (hit H-42): the claim-strength rule as revised (final R-88) no longer presumes this item's answer. Mechanically checked attestation is recorded there as a strong claim only that separate processes ran, records were chained, and no layout step is missing; it is expressly not a strong claim of epistemic independence, pending this item.

## Manager's addition note

Added by the Project Manager under Captain JP's grant: "Go ahead and add anything related to steps 1 through 4 that you see fit", exercised over Step 3 of the build-flow build, which seeded this queue. No existing item was moved, edited, or ruled by this note.

Evidence updates to two seeded items:

- DQ-001 (checklist totals): part of Step 11 has already happened, on Captain JP's direct order to update the space. The Build Flow Checklist now carries Plaid as a fifth tier with counts taken from PLAID.md, and the Metrics Reporter in its standing roles panel at one per tier (16 standing roles). The 76 tickable units were preserved exactly and saved state was untouched. Tier totals were machine-verified by the distinct-agent union method: Low 32, Medium 52, High 84, Extra High 137, Plaid 202. DQ-001 itself remains open: preserve against restructure has not been ruled, and the item's wording ("restructured to match the four levels") predates the fifth tier. What remains for Step 11 is aligning the checklist's text to the level documents, not the tier and panel work recorded here.
- DQ-002 (corpus gate strength): first worked evidence, from Step 5's first run. The first corpus gate record in the research-2 step was VOID: its blanket verdict phrasing did not meet the record form the standing procedure requires, and the ruling agent had run the gate on its own rulings (`research-2-outside-implementation-trace.md`, hits H-32 and H-33). Under the hard reading now in force, that record does not stand and the gate is re-run in full by an agent who ruled nothing. Under the advisory reading, a record of that shape could have been carried as a warning and the step built on it. The item stays open for Captain JP; this note records the first worked example either reading has.

One flagged question, previously unnumbered: whether the freeze set in the standing procedure (the five flow documents) also captures `METRICS.md`, `REPORTING.md`, and `PLAID.md`, which were created after the procedure was adopted. The flag itself is recorded in `STANDING-PROCEDURE.md`, in the Manager's addition there. It was left unnumbered here for the Decision-queue Clerk to number on receipt, because Step 5 was actively appending items to this queue and a number assigned from outside that run risked a duplicate. It has since been numbered DQ-019 and ruled by Captain JP: the freeze set is all eight documents. See the DQ-019 entry in the Ruled record below.

## Ruled record

Ruled items stay on record in this section, in the order they were ruled.

### R-7 closure conflict

Status: RULED, closed

Ruled by: Captain JP, 2026-11-10

Owner of record: Decision-queue Clerk

Ruling text: "No, step must always be complete 100% before moving on"

Source: Implementation Plan Step 1 and Step 2, from the independent verification of the research-1 implementation, recorded in research-1-verification.md.

The two readings that conflicted:

- Qualified reading: a stage could close in qualified form over partial or missing elements, provided they were bound listed and nothing was contradicted.
- Absolute reading: a stage does not close on partial or contradicted at all.

Ruling outcome: The absolute reading stands. A step closes only when its fold in trace is 100 percent LANDED. PARTIAL, MISSING and CONTRADICTED elements each bar closure, and the Auditor must not approve the move to the next step below that bar.

Where the ruling landed:

- LEVEL-2, R-7 in absolute form.
- LEVEL-1, R-3 and R-2 corrected to the absolute form.
- Ruling note recorded in research-1-verification.md.

### DQ-002: OQ-1, corpus gate strength

Status: RULED, closed

Ruled by: Captain JP

Owner of record: Decision-queue Clerk

Ruling text: "Hard gate: reject or re-rule"

Source: Implementation Plan, Open questions section, OQ-1. Also Implementation Plan Step 3 and Step 4, corpus gate part of the standing procedure.

The question that was open: Is the regression corpus a hard gate that rejects an amendment, or is it advisory?

The two readings that were open:

- Reject or re-rule: an amendment that would have allowed a corpus incident is rejected, unless Captain JP explicitly re-rules that incident through this queue. This is the reading the plan currently uses.
- Advisory: the corpus warns, but an amendment may proceed without a re-ruling. The standing procedure becomes lighter for every document and the corpus stops being a gate.

Ruling outcome: The reject or re-rule reading stands, and it is now ruled rather than assumed. An amendment that would have allowed a corpus incident is rejected, unless Captain JP explicitly re-rules that incident through this queue. A re-ruling names the corpus ID and the incident; a general approval is not a re-ruling. This confirms the reading the plan and the standing procedure have used throughout, so no gate decision already taken under it is reopened.

Where the ruling landed:

- Standing procedure, Part (c): already states the hard form as operative procedure (a failed item has exactly two outcomes, rejected or re-ruled, and no third outcome exists). No wording change was needed.
- Implementation Plan, OQ-1: marked ruled, with this queue entry named as the record.
- This queue: the open item is closed and this entry is its record.

### DQ-001: OQ-3, checklist totals

Status: SETTLED, closed. Settled by a decision of the Manager under Captain JP's discernment grant. This entry is not a ruling by Captain JP, and it is not recorded as one.

Settled by: The Manager (Muse), under Captain JP's grant, in her words: "Go ahead and use your discernment on that"

Owner of record: Decision-queue Clerk

Source: Implementation Plan, Open questions section, OQ-3. Also Implementation Plan Step 11.

The question that was open: Should the Build Flow Checklist keep its 76 units exactly, or be restructured to match the four levels?

The counted design the decision rests on: a full level-mirroring restructure would total 100 tickable units: 16 at Level 1 (the standing roles), the existing 76 at Level 2 (23 steps, 30 loop units, 23 Auditor approvals), 8 at Level 3 (the team forms), and 0 at Level 4 (the 108 member roles carry no checkboxes). Under that design all 76 existing ticks would carry over by unit identity and the 24 new units would start unticked.

Decision: The middle option. Keep the Build Flow Checklist's 76 tickable units exactly as the progress measure. Add the four levels as views over the board: Level 1 as a view of the 16 standing roles, display only and not tickable; Level 2 as the existing board and its 76 units; Level 3 as an index of the 8 team forms; Level 4 as a directory of the 108 member roles. Do not create the 24 new tickable units.

Reasons recorded for the decision:

- The 76 stays a pure measure of how far the build itself has travelled. A mixed total of 100 would dilute it: the board could show 24 of 100 before Step 1 opens.
- Standing roles and teams are setup and readiness. Their work is evidenced inside the steps and the Auditor approvals, not path progress, so they do not belong in the progress count.
- The level organisation and the complete member directory are still gained, as views.
- No saved state is put at risk: existing ticks and the selected tier are untouched, and no unit identity migration is needed.

What remains open after this settlement: nothing in the question itself. What remains for Step 11 is the work, not the decision: aligning the checklist artifact to add the level views and the member directory, with ticks and tier untouched. The full restructure to 100 tickable units is not adopted.

### DQ-003: OQ-5, verification depth per document

Status: RULED, closed

Ruled by: Captain JP

Owner of record: Decision-queue Clerk

Ruling text: "The audit should always be the audit that is planned"

Source: Implementation Plan, Open questions section, OQ-5. Also Implementation Plan Step 4 closing act and Step 12.

The question that was open: Should each document get a fresh independent verifier, or a full seven team audit per document?

The two readings that were open:

- Fresh independent verifier per document, overseen by the Auditor, with the full seven team form reserved for Step 12. This is the reading the plan used.
- Seven team audit per document for documents 2 to 6.

Ruling outcome: There is one audit in this flow, the seven-team audit form that the flow's audit plan prescribes, and any step whose check is an audit gets that audit, in full form. A single-verifier check is not the audit and does not stand in for it. Each remaining document step is audited with the full seven-team audit, not a fresh independent verifier alone: document 4, creative expansion, after the Step 7 rulings; document 5, Eval-Driven Development; and document 6, Anton patterns. Plan Step 12, the seven-team audit of the whole set, is unaffected and still runs. Cost consequence: the remaining document steps carry full audit cost, which roughly doubles the audit cost of those steps against the lighter reading.

Flagged consequence, undecided: Documents 2 and 3, research-2 and the creative process, closed under the single-verifier form. Whether they are re-audited in the seven-team form before Step 12, or covered by Step 12 alone, is not decided by this ruling and awaits Captain JP's word.

Where the ruling landed:

- Implementation Plan, OQ-5: marked ruled, with this queue entry named as the record.
- This queue: the open item is closed and this entry is its record.

### DQ-004: OQ-2, research-2 versus research-1 seniority on overlaps

Status: RULED, closed

Ruled by: Captain JP

Owner of record: Decision-queue Clerk

Ruling text: "Actually have the team decide which one stays"

Source: Implementation Plan, Open questions section, OQ-2. Also Implementation Plan Step 5.

The question that was open: When research-2 overlaps research-1, does research-1 keep what landed first, or does research-2 replace it as the senior source?

The two readings that were open:

- Research-1 keeps seniority on overlaps: research-2 extraction rules duplicates against the research-1 rules, keeping what landed first, with a pointer recorded. This is the reading the plan assumed.
- Research-2 is the senior source: overlapping research-1 rules may be rewritten rather than pointed to.

Ruling outcome: Neither source has standing seniority. On each overlap, the team implementing the document decides which version stays, the earlier landed rule or the newer source's version, and records the decision and its reason in the step's trace. Step 5's overlap rulings stand as team decisions already made under this ruling's form, so Step 5 is not reopened. The Manager's earlier blanket decision, made under Captain JP's "You decide what's best" grant minutes before this ruling, is superseded by this ruling and is recorded as superseded, not as the settlement.

Where the ruling landed:

- Implementation Plan, OQ-2: marked ruled, with this queue entry named as the record.
- This queue: the open item is closed and this entry is its record.

### DQ-005: OQ-4, the live proof candidate

Status: RULED, closed

Ruled by: Captain JP

Owner of record: Decision-queue Clerk

Ruling text: "A small new build"

Source: Implementation Plan, Open questions section, OQ-4. Also Implementation Plan Step 14 and Step 10.

The question that was open: Should the live proof be a small new build, or a redo of a reference only project, and which candidate is chosen?

The two readings that were open:

- Small new build, low risk, chosen or approved by Captain JP. This is the reading the plan assumed, because the estate wide halt makes redos ambiguous.
- Redo of a reference only project. If this option had been chosen, a further ruling would have been needed on what the redo is allowed to change.

Ruling outcome: The shape is ruled: the live proof is a small new build, low risk. A redo was not chosen, so no ruling on redo change scope is needed. The specific candidate is not named by this ruling: it is named separately, from a shortlist prepared for Captain JP, and approved by her before plan Step 14 starts. Nothing in Step 14 starts on an unnamed or unapproved candidate.

Where the ruling landed:

- Implementation Plan, OQ-4: marked ruled as to shape, with this queue entry named as the record.
- This queue: the open item is closed and this entry is its record.

**Candidate named.** Captain JP was presented the shortlist of four candidates and delegated the pick, in her words: "You pick". The pick that follows is the Manager's pick under that grant, not a ruling by Captain JP.

The picked candidate is the fold-in trace checker: a small CLI that reads a step's trace file and mechanically checks every claimed landing against the target documents, flagging claims whose cited text or section is not actually there. Its real target exists today: the closed Step 5 trace (196 rows) and the closed Step 6 trace (27 rows), checked against the flow documents.

Reasons, in short form: it is the smallest complete product of the four; its real target exists today; and it tests the flow's central claim, that a claimed landing can be checked mechanically rather than taken on a reporter's word.

The other three candidates (Muster-lite, the staffing verifier core; the decision queue validator and renderer; the metrics starter-set collector) are banked as candidates for later builds, not killed.

Nothing starts now. The pick names the candidate for plan Step 14, and the build itself starts only when the plan reaches Step 14.

### DQ-006: research-2 item C-67, commissioning and disqualification

Status: RULED, closed

Ruled by: Captain JP

Owner of record: Decision-queue Clerk

Ruling text: "The new agent does its stuff"

Source: research-2-outside, item C-67, ruled Conflict in Step 5 part (b), recorded in research-2-outside-implementation-trace.md, Rulings (Part (b)). The item as amended names the Auditor branch expressly (Step 5 revision amendment note, hit H-45), and the ruling is given on that live case, not only on the abstract question.

The question that was open: Does commissioning work, without producing it, disqualify a role from assessing that work?

The two readings that were open:

- Commissioning alone disqualifies, on the same footing as producing, operating, managing, or administering.
- Commissioning alone does not disqualify; only producing, operating, managing, or administering do (the coordinator of the assessed stage stays barred by R-36 in either case).

Ruling outcome: Commissioning disqualifies. An agent newly brought in for work does that work, and the assessor of a piece of work is an agent who neither produced it nor commissioned it: assessment is staffed to an agent clear of producing, operating, managing, administering, and commissioning. The Auditor branch is settled expressly: the Auditor may still require additions at his step check under R-50, and that authority is unchanged, but an agent whose work the Auditor commissioned for a step is assessed by an assessor other than the Auditor; the Auditor does not audit work he commissioned, and does not chair the review board for it. The coordinator of the assessed stage stays barred in any case, as before.

Where the ruling landed:

- LEVEL-4, R-73: commissioning added to the assessor disqualifier's barred list, with the staffing consequence stated.
- LEVEL-2: the Auditor gate passage aligned, so work the Auditor commissioned is assessed by another assessor and the Auditor records no ruling on it.
- LEVEL-3, R-55: the review board chair exception for work the Auditor commissioned.
- Agent file auditor.md: the Auditor branch stated in the Auditor's own boundaries.
- This queue: the open item is closed and this entry is its record.

### DQ-007: research-2 item C-9, compensating and reversed as failure states

Status: SETTLED, closed. Settled by a decision of the Manager under Captain JP's grant. This entry is not a ruling by Captain JP, and it is not recorded as one.

Settled by: The Manager (Muse), under Captain JP's grant, in her words: "You decide, I have no clue what that means. You can also use a creative third solution"

Owner of record: Decision-queue Clerk

Source: research-2-outside, item C-9, ruled Conflict in Step 5 part (b), recorded in research-2-outside-implementation-trace.md, Rulings (Part (b)).

The question that was open: Should the work-state vocabulary gain the failure states compensating and reversed, and if so, what does each mean for agent work? In plain terms: when agent work fails partway after changing things, the record needs a word for the undoing, and the source proposed naming two states for it.

The two readings that were open:

- Drop both words. Failure stays in the existing states (PARTIAL, HALTED-ROUGH, RECYCLED, UNVERIFIABLE) and no new state is added.
- Add both, with definitions supplied in the ruling: what enters each state, what residue it records, and what transitions leave it.

Decision: The third solution. The vocabulary gains no new states, and the distinction the two words carried is not lost. Undoing is recorded as an action on the existing record, not a state of it: when work is undone, the record carries a "reversed by" link from the failed work to the work that undid it, the same link machinery the flow already uses for supersession, and the failed work keeps the failure state it already has (PARTIAL, HALTED-ROUGH, RECYCLED, or UNVERIFIABLE). One undoing word is kept as the name of that action, "reversed": a record may say a piece of work was reversed by another piece of work. "Compensating" is dropped entirely: nothing in the estate compensates in the transaction sense, and the word promised machinery that does not exist.

Reasons recorded for the decision:

- States multiply closure and trace cases everywhere they are used; two new states would tax every record form in the flow.
- The link form keeps the information, what was undone, by what, and what state the failure ended in, with no new state machinery.
- If a future build truly needs a compensation state, the queue can add it then, defined against a real case instead of a hypothetical one.

Where the settlement landed:

- LEVEL-1, R-3: undoing recorded as a "reversed by" link at the work-state vocabulary definition, the failed work keeping its failure state, and "compensating" named there as not a state and not a record word in this flow.
- This queue: the open item is closed and this entry is its record.

What remains open after this settlement: nothing in the question itself. A future compensation state, if a real case ever needs one, is a new queue item, not a residue of this one.

### DQ-008: research-2 item C-64, what counts as a signature for a seat's attestation

Status: SETTLED, closed. Settled by a decision of the Manager under Captain JP's grant. This entry is not a ruling by Captain JP, and it is not recorded as one.

Settled by: The Manager (Muse), under Captain JP's grant, in her words: "You decide"

Owner of record: Decision-queue Clerk

Source: research-2-outside, item C-64, ruled Conflict in Step 5 part (b), recorded in research-2-outside-implementation-trace.md, Rulings (Part (b)). The Step 5 revision amendment note (hit H-40) corrected the item's earlier blocking note: as revised, links record a performer's spawn identity as a fact of the record, no rule in Step 5 calls that binding a signature, and the question stood open and unanswered by any implemented or prospective rule. That correction stands as history; this settlement is where the question is now answered.

The question that was open: What counts as a signature for a seat's attestation in this runtime, and who keeps those identities?

The two readings that were open:

- The spawn record binding adopted for links at R-97: the runtime's spawn record for the seat is the signature equivalent, kept by the runtime, with no separate key store.
- A stronger instrument is required before member is restated in attestation terms (a named key or identity store, with a named keeper), and the restatement waits until it exists.

Decision: The first reading, with an honesty bound. The runtime's spawn record for the seat is the signature equivalent for a seat's attestation in this runtime, kept by the runtime, with no separate key store. Attestation language in the flow is written to that strength and no stronger: a spawn record proves that the system created that agent for that seat and that the record was not altered after the fact; it does not prove the personal identity of any operator, or anything a cryptographic key would prove about a person, and no record may describe it as doing so.

Reasons recorded for the decision:

- The spawn record is the instrument that actually exists, and it already carries the member definition and the link rules today, so nothing waits on this settlement.
- The stronger instrument is a build of its own with no current consumer; whether such machinery is ever commissioned is Captain JP's to decide at DQ-012, the isolation backed provenance question, not here.
- Naming the bound plainly keeps attested closure honest at exactly the strength it has, which the flow's claim-strength rules already require.

Revisit condition: If Captain JP later rules for the stronger instrument, at DQ-012 or elsewhere, this settlement is revisited then, and the signature equivalent is restated at that point.

Where the settlement landed:

- LEVEL-1, R-79: the spawn record stated as the signature equivalent for a seat's attestation, kept by the runtime, with attestation claims bounded to seat creation and record integrity, not personal identity.
- This queue: the open item is closed and this entry is its record.

What remains open after this settlement: nothing in the question itself, subject to the revisit condition above. DQ-011, the provenance strength attested closure operates at, and DQ-012, whether an isolation backed instrument is ever built, stay open and are not decided by this settlement.

### DQ-009: research-2 item C-65, which stages sit a review board

Status: RULED, closed

Ruled by: Captain JP

Owner of record: Decision-queue Clerk

Ruling text: "Boards at every step"

Source: research-2-outside, item C-65, ruled Conflict in Step 5 part (b), recorded in research-2-outside-implementation-trace.md, Rulings (Part (b)). The item as amended by the Step 5 revision amendment note (hit H-41): two elements formerly presented as open were implemented in effect and struck from the question, the four-outcome gate vocabulary applying at the Auditor approval gate after every step (item A-3, final R-51) and entrance criteria, including disposition of the previous gate's action items, recorded for each gate or review (item A-7, final R-53). The residue Captain JP ruled on was only: which stages, if any, sit a review board under final R-55, and whether any stage is excepted from the gate outcome form.

The question that was open, as amended: Which stages, if any, sit a review board under R-55, and is any stage excepted from the gate outcome form?

The options that were open:

- All stage closures become gate events in the A-3 outcome form, with entrance criteria at every stage.
- Only named stages get full gates (for example brief, plan, build, finished-product audit, and release), and the rest keep entrance and exit criteria without a board. The ruling names the stages.
- No stage converts; gate outcomes apply at the Auditor gate as ruled at A-3, and no board form is added.

Ruling outcome: Boards at every step. Every one of the 23 steps sits a review board under R-55. No stage is excepted from the board form, and no stage is excepted from the gate outcome form: the four outcomes apply at every step's board. The Auditor approval row after every step is the record of that step's board verdict. Both parts of the residue are answered. The DQ-006 branch applies inside this ruling: where the Auditor commissioned the work under review, he neither chairs nor sits on its board and another assessor chairs it, exactly as landed under DQ-006; that exception is about the Auditor's seat on the board, not about whether a board sits.

Where the ruling landed:

- LEVEL-3, R-55: a review board stated to sit at every step without exception, its verdict recorded in the step's Auditor approval row in the four-outcome form of R-51, with the DQ-006 chair exception kept intact.
- LEVEL-2, the Auditor approval gate passage: the approval after every step stated as the record of that step's review board verdict, the Auditor presenting the step packet to the board and recording its verdict, with the DQ-006 sentence kept intact.
- Agent file auditor.md: the approval gate and the step ruling step aligned, so the gate records the board's verdict and the ruling the Auditor records is the board's verdict, with the Auditor's duties of presenting the packet and recording the verdict preserved and the DQ-006 boundary kept.
- This queue: the open item is closed and this entry is its record.

### DQ-010: research-2 item C-70, live proof minimum scope

Status: RULED, closed

Ruled by: Captain JP

Owner of record: Decision-queue Clerk

Ruling text: "No universal floor, judged claim by claim"

Source: research-2-outside, item C-70, ruled Conflict in Step 5 part (b), recorded in research-2-outside-implementation-trace.md, Rulings (Part (b)).

The question that was open: What minimum scope makes a live proof citable without qualification, for any build?

The two readings that were open:

- No universal floor. R-11 stands as written: every claimed route exercised, sample stated inside the claim, and any sample too small to carry its claim makes the result PASS-QUALIFIED. Qualification is judged claim by claim.
- A universal floor, named in the ruling (for example a minimum number of exercised routes and a minimum sample for sampled behaviour), below which a proof is always PASS-QUALIFIED.

Ruling outcome: No universal floor. There is no universal minimum scope for a live proof. R-11 stands as written, and it is now ruled rather than assumed: every claimed route is exercised, the sample is stated inside the claim, and any sample too small to carry its claim makes the result PASS-QUALIFIED, judged claim by claim. The rest of research-2 item C-70 was already ruled Duplicate against R-11 and R-26 and is unaffected by this ruling.

Where the ruling landed:

- LEVEL-2, R-11: checked against the ruling and found to state the ruled form in substance; no wording change was needed and none was made.
- This queue: the open item is closed and this entry is its record.

### DQ-011: research-2 item C-63, provenance strength of attested closure

Status: RULED, closed

Ruled by: Captain JP

Owner of record: Decision-queue Clerk

Ruling text: "The checks on the system's own records, at that strength"

Source: research-2-outside, item C-63, ruled Conflict in Step 5 part (b), recorded in research-2-outside-implementation-trace.md, Rulings (Part (b)). The item as amended by the Step 5 revision amendment note (hit H-39): the carve-out suggesting the strength element could be both blocked and implemented was struck; as revised, the provenance grades (final R-81) were definitions only and assigned no grade to any record this flow produces, and attested closure operated at no graded provenance strength, with no grade label on closure records, until this item was ruled. That interim state is what this ruling ends.

The question that was open, as amended: Is the Muster verifier adopted as the verifier for attested stage closure, and at which provenance strength does attested closure operate?

The options that were open:

- Adopt a verifier for attested closure at L2-like strength: the three checks at R-98 run by a verifier other than the coordinator, over runtime-captured spawn records (R-101). Muster is used only if and when it is built; the checks do not wait for it.
- Adopt Muster as that verifier when it is built, and attested closure operates at the strength Muster provides; until then attested closure runs in the first option's form.
- Require L3-like isolation backed strength before attested closure may be cited at full strength (see DQ-012).

Ruling outcome: The first option. Attested closure operates at the L2-like strength: the three checks run by a verifier other than the coordinator, over the spawn records the runtime captured, and a stage's closure record carries that grade and may claim exactly that strength, no more. Muster is used only if and when it is built; the checks do not wait for it, and this ruling does not make Muster the designated verifier. L3-like strength is not required; whether an isolation backed instrument is ever built remains DQ-012, still open. This ruling also settles the strength element of items C-15, C-16, and C-19 as implemented in Step 5 part (d), which this item blocked; the layout, link, and three-check rules themselves were never blocked and are unchanged. Companion record: the DQ-008 settlement, which made the runtime's spawn record the signature equivalent for a seat's attestation, bounded to seat creation and record integrity and not personal identity; this ruling's strength claim is read inside that bound, and inside the claim-strength bound of R-88, that mechanically checked attestation claims separate processes ran, records chained, and no layout step missing, and never epistemic independence.

Where the ruling landed:

- LEVEL-1, R-81: the rule now makes the one assignment, that a stage's attested closure record carries grade L2, defined as the three checks (R-80) run by a verifier other than the coordinator over the spawn records the runtime captured; the definitions-only framing and the bar on presenting any record of this flow as graded are aligned to that assignment, and no other record carries a grade label under the rule.
- LEVEL-2, R-7, attested closure clause: the interim sentence, that attested closure operates at no graded provenance strength and closure records carry no grade label until DQ-011 is ruled, is replaced with the ruled form: attested closure operates at grade L2 (R-81) and the closure record carries the L2 grade label, claiming that strength and no more (R-88).
- This queue: the open item is closed and this entry is its record.

### DQ-012: research-2 item C-17, isolation backed provenance instrument

Status: RULED, closed

Ruled by: Captain JP

Owner of record: Decision-queue Clerk

Ruling text: "Yes, build the isolated checker"

Source: research-2-outside, item C-17, ruled Conflict in Step 5 part (b), recorded in research-2-outside-implementation-trace.md, Rulings (Part (b)).

The question that was open: Should the estate build or adopt an isolation backed provenance instrument (SLSA L3-like), with two-person review of changes to it?

The two readings that were open:

- No. Provenance in this estate tops out at the L2-like platform record (R-101), and L3 is not claimed, built, or required.
- Yes. An isolation backed instrument is commissioned, and until it exists no record may be labelled above L2.

Ruling outcome: The second reading. An isolation backed provenance instrument, the L3-like level, is commissioned: a checker sealed away from the system doing the work, so the work cannot reach it or alter what it observed, with two-person review of changes to the instrument itself. Until the instrument exists, no record in the estate may be labelled above the L2-like strength ruled at DQ-011, and attested closure continues to operate at DQ-011's strength in the interval; nothing in this ruling blocks current work. The ruling commissions the instrument; it does not start it. The instrument is a candidate build in the estate, named and scheduled only on Captain JP's further word or through the plan's later steps, and no record may present the commission as a build under way. The DQ-008 settlement's revisit condition is now live in one direction: when the instrument exists, the signature equivalent settlement is revisited for records labelled at the higher strength. DQ-011's ruling is unaffected for the interval.

Where the ruling landed:

- LEVEL-1, R-81: the closing sentence, that no L3 grade is defined or adopted, is replaced with the ruled form: the L3-like grade is commissioned, no record may be labelled above the L2-like grade until the isolation backed instrument exists, and changes to the instrument, once it exists, require two-person review.
- This queue: the open item is closed and this entry is its record.

### DQ-013: research-2 item C-18, reproducible derivation

Status: RULED, closed on the principle

Ruled by: Captain JP

Owner of record: Decision-queue Clerk

Ruling text: "Yes, artifacts must be re-derivable"

Source: research-2-outside, item C-18, ruled Conflict in Step 5 part (b), recorded in research-2-outside-implementation-trace.md, Rulings (Part (b)).

The question that was open: Is reproducible derivation required for agent produced artifacts (the pre-1.0 SLSA L4 idea), and what would hermetic and reproducible mean here?

The two readings that were open:

- No. The grade is not adopted; it is one the source framework itself dropped, and no rule in this flow requires re-deriving an artifact to prove it.
- Yes, in a form the ruling defines: which artifact classes must be re-derivable, by whom, and what a mismatch does.

Ruling outcome: The principle in the second reading is adopted: agent produced artifacts must be re-derivable from their recorded inputs. The shape of the requirement is not defined by this ruling. The item as written required a Yes to define which artifact classes must be re-derivable, re-derived by whom, and what a mismatch does, and those sub-choices have not been presented to Captain JP, so no shape is invented here or in the flow documents. Bounds: nothing already shipped is retroactively non-compliant by this ruling; the requirement applies from its definition forward. No step, gate, or release may cite re-derivation as a pass condition until the shape is defined and landed in the flow. The drafting of the shape is carried as a new open item, DQ-018.

Where the ruling landed:

- LEVEL-1, R-81: one sentence added at the end of the grades passage, stating that re-derivation is adopted as a requirement on agent produced artifacts, that its shape is to be defined in the flow before any step, gate, or release may cite it, and that until the shape is landed the requirement is recorded as adopted and undefined, not as a pass condition.
- This queue: the open item is closed on the principle and this entry is its record, and DQ-018 carries the undefined shape.

### DQ-014: research-2 item C-98, decorrelation statement in audit verdicts

Status: SETTLED, closed. Settled by a decision of the Manager under Captain JP's grant. This entry is not a ruling by Captain JP, and it is not recorded as one.

Settled by: The Manager (Muse), under Captain JP's grant, in her words: "Decide"

Owner of record: Decision-queue Clerk

Source: research-2-outside, item C-98, ruled Conflict in Step 5 part (b), recorded in research-2-outside-implementation-trace.md, Rulings (Part (b)). The Step 5 revision amendment note (hit H-42) recorded that the claim-strength rule as revised (final R-88) no longer presumed this item's answer: mechanically checked attestation is there a strong claim only that separate processes ran, records were chained, and no layout step is missing, and it is expressly not a strong claim of epistemic independence, pending this item. That amendment stands as history; this settlement is where the question is now answered.

The question that was open: Must audit verdicts carry a decorrelation statement, and what counts as decorrelated for LLM agent auditors?

The two readings that were open:

- No new requirement. Distinctness under R-29 stays the staffing test, and verdicts carry the C-98 limit as a known caution: spawn records prove separate processes ran, not epistemic independence.
- Yes. The verdict form gains a decorrelation field, with the ruling naming what counts (for example different models, different information diets, or blindness between teams) and who judges it.

Decision: A bounded yes, in statement form only. Every audit verdict carries one decorrelation line in its form block, and the line is a statement of facts, not a scored field and not a pass condition. The line states, for that audit: the model or models the auditors ran; whether the teams saw each other's papers before verdicts were given; and whether the teams worked from the same evidence set or different ones. The Auditor records the line from the audit's own staffing record. Nobody scores the line, and no verdict is stronger or weaker on paper because of it. The claim-strength bound of R-88 stands unchanged: mechanically checked attestation and distinctness under R-29 are strong claims only that separate processes ran, that records were chained, and that no step in the layout is missing, and they are expressly not a claim of epistemic independence; the line never claims independence, it reports the conditions so a reader can judge correlation for themselves. This settlement settles the statement question only: a scored decorrelation measure is not adopted, and designing one would be a new queue item if it is ever wanted.

Reasons recorded for the decision:

- The facts are cheap, because they already exist in every audit's staffing record, and a reader of a verdict several builds later cannot reconstruct them if they are not written at verdict time.
- A scored measure would be invented precision: no source supplies one, and the estate has no calibration data for it.
- If a future build wants correlation actually measured, the decorrelation lines recorded across audits are exactly the data such a measure would be designed from.

Where the settlement landed:

- LEVEL-2, R-8: the decorrelation line added to the verdict form block's required contents, as item (7) of the block's enumeration, worded as a statement of the three facts, recorded by the Auditor from the audit's staffing record, expressly not scored, not a pass condition, and never a claim of epistemic independence.
- This queue: the open item is closed and this entry is its record.

What remains open after this settlement: nothing in the question itself. A scored decorrelation measure, if it is ever wanted, is a new queue item, not a residue of this one.

### DQ-015: research-2 item C-68, who sets materiality for a specific audit

Status: RULED, closed

Ruled by: Captain JP

Owner of record: Decision-queue Clerk

Ruling text: "Every issue should be fixed before moving on"

Source: research-2-outside, item C-68, question carried in the source (who sets materiality for a build: Captain JP, the audit plan, or the gatekeeper), raised at Step 5 revision, hit H-44 in the Contrarian attack on the Step 5 rulings, recorded in research-2-outside-implementation-trace.md, section 8 of the Step 5 revision.

The question that was open: May the Auditor set a lesser or different severity bar for a specific audit than the standing R-17 bar, recorded in that audit's charge before papers are collected?

The two readings that were open:

- Yes: the Auditor may set a lesser or different bar per audit, recorded in the charge before papers are collected and stated in the verdict's form block. This is the sentence held from final R-85 in the Step 5 revision; it takes effect only under this ruling.
- No: the R-17 bar is the bar for every audit and loop. A different bar exists only where Captain JP rules one, or where the flow itself is amended.

Ruling outcome: The severity bar does not move per audit. More strongly: no issue raised in an audit is left open when the work moves on; every issue is fixed before moving on, and a severity grading never becomes a reason to carry an issue forward unfixed. The lesser-bar sentence held from final R-85 is therefore rejected and does not take effect; final R-85 stands without it, the R-17 default bar unmodified. Consistency note: this ruling is DQ-015 read alongside Captain JP's standing closure ruling (a step closes only at 100 percent); Critical and High findings already barred closure under the gate, and this ruling extends the same discipline to every issue an audit raises, at any severity. What this ruling does not do: it does not abolish severity grades, which still order the repair work and still name the gate bar, and it does not reopen any verdict already issued; it governs from here forward.

Where the ruling landed:

- LEVEL-2, R-85: the ruled form stated at the defining passage, that the standing bar is the bar for every audit, the Auditor may not set a lesser or different bar for a specific audit, and every issue an audit raises is fixed before the work moves on. The held lesser-bar sentence was checked for in every flow document and in the Auditor's agent file and exists in none of them, so there was no pending text to remove; the rest of R-85 (the R-17 default, and triage as the defined act that converts claims to findings) stands intact.
- This queue: the open item is closed and this entry is its record.

### DQ-016: research-2 item A-25, closure with anomalies recorded for the remainder

Status: RULED, closed

Ruled by: Captain JP

Owner of record: Decision-queue Clerk

Ruling texts: "Exceptions in a named class of cases" and "Use your discretion. In those moments."

Source: research-2-outside, item A-25, second clause, re-ruled Conflict at Step 5 revision, hit H-9 in the Contrarian attack on the Step 5 rulings. The clause states that a level closes when its paired verification has produced evidence for every traced element or recorded anomalies for the rest.

The question that was open: May a level or stage ever close on the strength of anomalies recorded for its unproven elements, contrary to the absolute closure form in R-7?

The readings that were open:

- No: R-7 stands without exception. Recorded anomalies are dispositions, not closure evidence, and a level with unproven elements does not close.
- Yes, in a named class of cases the ruling specifies: for those cases, recorded anomalies close the level, and R-7 is amended to state the class and its record form.

Ruling outcome: Captain JP ruled the principle in favour of exceptions and then completed the ruling by placing the class question in discretion exercised in the moment. There is no fixed named class in the rule. The bounded framing that follows is the Manager's framing under Captain JP's grant; it is not Captain JP's wording and is not recorded as her wording.

Manager's framing under the ruling: The default is unchanged and absolute: a stage closes only at 100 percent LANDED, and anomalies are dispositions, never closure evidence. An exception exists only in the moment, decided when a case is live by Captain JP herself on a presented case, or by the Manager under this grant where she has said to use discretion. Either decision is recorded at the time with the element left unproven, the reason closing cannot wait or should not wait, the owner of the remainder, and the release condition or date; the closure is recorded CLOSED-QUALIFIED with the exception named, never plain CLOSED. An exception is never standing: deciding one case creates no class and no precedent the next case can cite as entitlement, and the next case is decided in its own moment on its own facts. An anomaly in how the closure evidence was produced, including a self-run check or a void record form, is outside the discretion absolutely: it never qualifies, and it voids and re-runs.

Worked examples for the discretion: The five drafted classes are examples to learn from, not classes in the rule: live proof protection; a named bound on a live proof; a recorded non-pass inside a gate record; sealed historical records; and Captain JP's own recorded deferral. None creates an entitlement, and each future case is decided on its own facts.

Where the ruling landed:

- LEVEL-2, R-7: the absolute closure rule kept as the default, with one bounded in-the-moment exception passage stating who may decide an exception, the record it requires, the CLOSED-QUALIFIED form with the exception named, the bar on precedent, and the absolute exclusion for anomalies in how closure evidence was produced.
- LEVEL-1, R-3 and R-78: the CLOSED-QUALIFIED definitions aligned to permit stage closure only under the bounded R-7 exception, with the absolute bar otherwise unchanged.
- This queue: the open item is closed and this entry is its record.

### DQ-018: The shape of the re-derivation requirement

Status: RULED, closed

Ruled by: Captain JP

Owner of record: Decision-queue Clerk

Ruling text: "Use your discretion in the moment"

Source: DQ-013, ruled closed on the principle by Captain JP. Her ruling adopted re-derivation and left its shape undefined; this item carried the shape to her for ruling.

The question that was open: Which agent produced artifacts must be re-derivable, re-derived by whom, and what does a mismatch do?

The options that were open:

- Full form: every shipped artifact class must be re-derivable by an independent agent from the recorded inputs, and a mismatch is treated as a defect at the gate.
- Bounded form: re-derivation is required only for named classes, code and packaged artifacts rather than documents and reports, and a mismatch is recorded as a defect against the producing step.
- Minimal form: inputs and environment are recorded completely enough that re-derivation is possible in principle, with spot re-derivation at the finished-product audit only.

Ruling outcome: Captain JP placed the shape question in discretion exercised in the moment. No fixed universal shape is adopted by her ruling. The bounded framing that follows is the Manager's framing under Captain JP's grant; it is not Captain JP's wording and is not recorded as her wording.

Manager's framing under the ruling: No fixed universal shape, not Full, not Bounded, and not Minimal as a standing rule, is adopted. The DQ-013 principle stands: agent produced artifacts must be re-derivable from their recorded inputs. For each live case where re-derivation is to be used, the shape is decided in that moment, on that case, by Captain JP on a presented case or by the Manager under this grant. That moment decision is recorded at the time in that case's record and states which artifacts in that case must be re-derived, who re-derives them, an agent other than the producer, and what a mismatch does in that case. Until such a moment decision is recorded for a case, re-derivation may not be cited as a pass condition for that case. A moment decision creates no standing class and no precedent the next case can cite as entitlement; the next case is decided in its own moment on its own facts.

Where the ruling landed:

- LEVEL-1, R-81: the interim sentence, that re-derivation is adopted and undefined and not a pass condition until its shape is landed, is replaced with the settled form above: no fixed universal shape, the shape decided in the moment on each live case and recorded in that case's record, and no citation of re-derivation as a pass condition for a case until a moment decision is recorded for that case.
- This queue: the open item is closed and this entry is its record.

### DQ-017: Audit plan inside the build flow, per-level auditor amounts

Status: RULED, closed

Ruled by: Captain JP

Owner of record: Decision-queue Clerk

Ruling texts: "If it makes a mistake, it should be what was actually planned." and "I don't think the plan was to have seventy" and, confirming the proposed settlement put to her, "Yes, settle it that way"

Source: Captain JP's audit-form ruling, recorded in this item at her direction. DQ-003 stands: the audit is the audit that is planned. An earlier part of this item was already ruled: Captain JP ruled "The audit plan inside the build flow," and the audit plan inside the build flow documents governs each audit, staffed with the appropriate amount of auditors that plan sets for the level. This ruling completes the item on the amounts that plan had not stated, the logic audit amounts and the post-round-one trim, and on the one conflict inside PLAID.md.

The question that was open: For each level and audit step, what amount of auditors does the audit plan inside the build flow state, and which levels or audit steps still have no amount stated? The amounts the plan already stated in full were not in question. The open parts were the logic audit amounts for Low, Medium, and High, whether any level states a post-round-one trim, and a conflict inside PLAID.md: its per-step table put Audit logic 70 in Step 7 and again in Step 9, while its team table and its derivation passage state a logic audit team of 70 in total, the five scopes (premises, inference, consistency, completeness, closure) each staffed across seven named argument slices, with each slice staffed for the brief loop and the plan loop as distinct seats, which is 35 per loop and 70 across both loops.

Governing principle, in Captain JP's words: "If it makes a mistake, it should be what was actually planned." Its meaning: where a flow document contradicts itself, the passage showing what was actually planned governs, and the mistaken rendering is corrected to match it; the error does not govern. Applied here, the PLAID.md team table and derivation passage show what was actually planned, and the per-step table was the mistaken rendering.

Ruling outcome: The proposed settlement put to Captain JP is adopted in full, as confirmed by her words "Yes, settle it that way":

- Logic audit amounts per loop: 5 at Low, 15 at Medium, 25 at High, 35 at Extra High, and 35 at Plaid. The amounts apply to the Audit logic unit at Step 7, the brief loop, and at Step 9, the plan loop.
- At Plaid the two loops are staffed as distinct seats, so the logic audit team totals 70 across both loops. There is no amount of 70 for a single loop.
- No trim at any level: no level states a post-round-one trim, and every round of every audit runs with the full stated amount for its level.
- The PLAID.md per-step table is corrected to what was actually planned: Step 7, Brief loop, Audit logic 35 and step total 102; Step 9, Plan loop, Audit logic 35 and step total 47.
- The verified distinct-agent union totals are unchanged: Low 32, Medium 52, High 84, Extra High 137, Plaid 202. The Plaid union already counted the logic audit team as 70 once, across both loops, so the correction changes no union total.

Where the ruling landed:

- LEVEL-2, the steps level introduction: the defining passage for the logic audit amounts, stating the per-loop amounts for all five levels and the Plaid total of 70 across both loops. The Step 7 and Step 9 unit lines point to that passage.
- LEVEL-3, the logic audit team section: the team now points to the amounts defined in LEVEL-2, and no longer points outside the documents to checklist counts.
- LEVEL-3, R-44: no level states a post-round-one trim, and every round runs with the full stated amount for its level.
- PLAID.md: the team-size table row for the logic audit team states that 70 is the team total across both loops, 35 per loop with distinct seats per loop; the derivation passage stands; the per-step staffing table is corrected, Step 7 to 102 and Step 9 to 47, each with Audit logic 35.
- This queue: the open item is closed and this entry is its record.

### DQ-019: The freeze set

Status: RULED, closed

Ruled by: Captain JP

Owner of record: Decision-queue Clerk

Ruling text: "All eight documents"

Source: The freeze-set question flagged unnumbered in this queue, in the Manager's addition note above, and flagged in `STANDING-PROCEDURE.md`, in the Manager's addition there. The standing procedure's freeze convention captured five flow documents and predated `METRICS.md`, `REPORTING.md`, and `PLAID.md`, which were created after the procedure was adopted. The flag left the item unnumbered for the Decision-queue Clerk to number on receipt; it is numbered DQ-019 here.

The question that was open: When a step closes and its documents are frozen as the next step's base, how many documents go into the freeze?

The options that were open:

- All eight documents: every freeze captures `FLOW.md`, `LEVEL-1-STANDING.md`, `LEVEL-2-STEPS.md`, `LEVEL-3-TEAMS.md`, `LEVEL-4-MEMBERS.md`, `METRICS.md`, `REPORTING.md`, and `PLAID.md`.
- The original five only: every freeze captures `FLOW.md` and the four level documents, as the procedure was first written.

Ruling outcome: All eight documents. Every freeze from now on captures all eight flow documents: `FLOW.md`, `LEVEL-1-STANDING.md`, `LEVEL-2-STEPS.md`, `LEVEL-3-TEAMS.md`, `LEVEL-4-MEMBERS.md`, `METRICS.md`, `REPORTING.md`, and `PLAID.md`, each copied byte for byte, with its SHA-256 hash and byte size listed in the freeze folder's `MANIFEST.md`. Past frozen bases stay sealed: they are not re-made, not renamed, and no edit is made inside them. The ruling sets what future freezes capture.

Where the ruling landed:

- STANDING-PROCEDURE.md, Part (e) freeze step and the freeze snapshot definition in the file naming conventions: the freeze set changed from the five flow documents to the eight documents named above.
- STANDING-PROCEDURE.md, the Manager's addition flag on the freeze set, and this queue's Manager's addition note: each flag now records that the question was numbered DQ-019 and ruled, pointing to this entry.
- This queue: the item is closed and this entry is its record.

### DQ-020: Step 6 Q1, the reframe route

Status: RULED, closed

Ruled by: Captain JP

Owner of record: Decision-queue Clerk

Ruling text: "You do"

Source: Step 6, the creative process implementation, Item 19, Reframer, recorded as Q1 in creative-process-engineering-flow-implementation-trace.md. Step 6 landed the Reframer habit in LEVEL-1 in Captain only form and left the route open for Captain JP in that trace. The item was never an open entry in this queue; it is numbered DQ-020 here, on its ruling.

The question that was open: Who may reframe a build, when the evidence shows the build's whole framing is wrong?

The options that were presented:

- Captain only, as landed: only Captain JP may reframe; the team carries the evidence to her as a design question through the decision queue and waits.
- Bounded in-build reframe: the team may reframe inside the build only where the change touches none of scope, money, or security; anything crossing those goes to Captain JP.
- Team reframes on evidence: the source form, under which the team reframes when the evidence demands it, with no queue route.

Ruling outcome: None of the three presented options was chosen. Captain JP answered with a fourth form of her own, in her words: "You do". The reframing is done by Muse. Reframing authority sits with the Manager, Muse, who is Captain JP's personal agent and the same Muse across every build. A step or team does not reframe a build on its own authority, and a reframe is not carried to Captain JP as a design question by default. When the Reframer trigger fires, repeated good solutions to the stated problem keep failing in the world, the failure evidence is carried to Muse as Manager. Muse decides whether the build is wrongly framed or sound and unfinished, and Muse makes the reframe decision, recording the decision, the evidence, and the new frame in the build's record. A decided reframe is consumed at Step 23 as a next-version input, as before. One bound, recorded here as a bound on the ruling and not as part of Captain JP's ruling text: a reframe that would overturn a ruling Captain JP herself has made, for example a scope she ruled at the grill, is not Muse's to make; that one is carried to Captain JP, because no agent counter-rules Captain JP.

Where the ruling landed:

- LEVEL-1, Standing habits, Reframer: rewritten to the ruled form. The evidence is carried to the Manager, Muse decides and records the decision, the evidence, and the new frame, a decided reframe is consumed at Step 23, and the counter-ruling bound is stated. The trigger definition and the caution that most stuck builds are unfinished, not wrongly framed, stand.
- LEVEL-2, Step 23, Method, Reframer: the step now consumes reframes the Manager, Muse, has decided and recorded, as next-version inputs.
- Agent file project-manager.md, which carries the Reframer duty: the duty is rewritten to the ruled form, headed "Reframe as Manager", with the counter-ruling bound stated.
- This queue: the item is closed and this entry is its record.

### DQ-021: Step 6 Q2, the spike boundary

Status: RULED, closed

Ruled by: Captain JP

Owner of record: Decision-queue Clerk

Ruling text: "Spikes at Steps 5 and 10, as landed"

Source: Step 6, the creative process implementation, Item 6, Tracer-Builder, recorded as Q2 in creative-process-engineering-flow-implementation-trace.md. Step 6 landed disposable non-product spikes at Steps 5 and 10, the two research loops, each with an experiment record, and left the boundary open for Captain JP in that trace. The item was never an open entry in this queue; it is numbered DQ-021 here, on its ruling.

The question that was open: May anything runnable be built before the build step, Step 14, and if so, in what form and at which steps?

The options that were presented:

- Spikes at Steps 5 and 10, as landed: disposable non-product experiment spikes are permitted inside the two research loops, each with its experiment record kept.
- Nothing runnable before the build step: the strict form, under which nothing runs until Step 14.
- One tracer after tests are written: no spikes in research, but one thin end-to-end slice of the real product may be built at Step 13 once its tests are written.

Ruling outcome: The first option. The landed form stands, now confirmed by ruling rather than carried only as a landing. Disposable non-product spikes are permitted inside Steps 5 and 10, where a contested claim needs a runnable check, each spike recorded in the experiment record. A spike lives outside the product, is never counted as product scaffolding, never becomes the product, and is thrown away. The strict form was not chosen, and the Step 13 tracer form was not chosen: the product tracer remains Step 14's first slice, built to Step 13's tests, as LEVEL-2 states it.

Where the ruling landed:

- LEVEL-2, Step 5 and Step 10, Method, Tracer-Builder, spike form only: checked against this ruling and found to state the ruled form, a disposable experiment spike, recorded in the experiment record, living outside the product, never counted as product scaffolding, and thrown away, with the product tracer as Step 14's first slice, built to Step 13's tests. No wording change was needed and none was made.
- LEVEL-1: carries no spike passage and nothing that contradicts this ruling. No change.
- This queue: the item is closed and this entry is its record.

### DQ-022: Step 7 pack, S1 the path ledger

Status: RULED, closed

Ruled by: Captain JP

Owner of record: Decision-queue Clerk

Ruling text: "Implement S1"

Source: The plan Step 7 ruling pack. S1, the path ledger, is the first of eight survivors recorded in `creative-expansion.md`. The item was presented to Captain JP as the first item of that pack; it is numbered DQ-022 here, on its ruling.

The question that was open: Whether the path ledger is implemented, implemented in reduced form, or held.

The options that were presented:

- Implement S1: the path ledger is implemented in its full form.
- Implement S1 reduced: the path ledger is implemented in a reduced form.
- Hold S1: the path ledger is not implemented and is held.

Manager's recommendation: Implement S1 reduced. This was the Manager's recommendation, stated at the top of the pack. Captain JP did not take the recommendation: she chose Implement S1.

Ruling outcome: The first option, in Captain JP's words: "Implement S1". S1, the path ledger, is implemented in its full form, not the reduced form. The implementation follows the standing procedure as a scoped single-survivor run under plan Step 7, with the freeze deferred to the close of Step 7.

Where the ruling landed:

- This queue: the item is closed and this entry is its record.

**Supersession: the Manager's pick under Captain JP's delegation**

Captain JP's first ruling on this item was, in her words: "Implement S1".

Captain JP later answered the S1 question again, delegating it, in her words: "U pic". That wording means "You pick". That later delegation superseded the earlier ruling for this item.

The settlement is now the Manager's pick under that grant. It is recorded as a Manager settlement, not as a ruling by Captain JP.

Pick: Implement S1 reduced, in this exact form: no second ledger system is built; the step records the flow already keeps are named the path ledger, given the append-only rule, and the missing axes from S1's four are added where they are absent; S1's vocabulary-as-versioned-data element lands only insofar as the reduced form needs it to name the ledger's axes and states, and a separate versioned vocabulary system is not built.

Implementation on the pick: the implementation proceeds on the reduced scope under plan Step 7 as a scoped single-survivor run, with the freeze deferred to the close of Step 7, exactly as the original entry's outcome stated for the run's shape.

### DQ-023: Step 7 pack, S2 attested closure

Status: SETTLED, closed. Settled by a decision of the Manager under Captain JP's grant. This entry is not a ruling by Captain JP, and it is not recorded as one.

Settled by: The Manager (Muse), under Captain JP's grant, in her words: "You picl"

Owner of record: Decision-queue Clerk

Source: The plan Step 7 ruling pack. S2, attested closure, is the second of eight survivors recorded in `creative-expansion.md`. The item was presented to Captain JP as the second item of that pack; it is numbered DQ-023 here, on its settlement.

The question that was open: Whether attested closure is implemented, implemented in reduced form, or held.

The options that were presented:

- Full form: S2 is implemented in its full form.
- Reduced form: S2 is implemented in a reduced form.
- Hold S2: S2 is not implemented and is held.

Manager's recommendation: Hold S2. This recommendation stood at the top of the presentation, on the ground that S2's substance already landed through DQ-008, DQ-011, and DQ-012.

History: Captain JP first ruled the full form, in her words: "Implement S2". She did not take the Manager's Hold recommendation then. That ruling is recorded here as superseded history only. Captain JP then answered the S2 question again, delegating it, in her words: "You picl". Her spelling is kept exactly; the words mean "You pick". That delegation supersedes the earlier full form ruling. On that delegation the run converted to a recognition and verification run. No flow document was edited at any point in this run, under either ruling.

Decision: Hold S2, in this form: S2 is recognised as already landed in substance through DQ-008, DQ-011, and DQ-012, and no new machinery is implemented from it in this step. The pick under the delegation is the same Hold recommendation that stood at the top of the presentation before the first ruling, which Captain JP did not take at that time.

Reasons recorded for the decision:

- The substance is verified as landed through DQ-008, DQ-011, and DQ-012, and that landing was confirmed first hand in this run's verification, as recorded below.
- Implementing the substance again would build the same machinery a second time under a second name.

What the run found: 16 of the 26 elements extracted from S2 were ruled Duplicate, and all 16 were confirmed against the live passages they cite in this run's verification, with none not confirmed. 8 elements are held for Captain JP: the 7 gaps S2-E8, S2-E9, S2-E14, S2-E15, S2-E16, S2-E19, and S2-E22, each gated PASS under the hard gate, and the Conflict element S2-E26. None of the 8 is implemented under this pick. 2 elements, S2-E24 and S2-E25, state no requirement and land nothing. No flow document was edited in this run. Nothing was landed in this run, and there is nothing to revert.

Where the settlement landed:

- This queue: the item is closed and this entry is its record.
- Trace file `~/workspace/build-flow-expansion/step-7-s2-implementation-trace.md`: the recognition and verification run's record, carrying the run's history, the extraction summary, the overlap rulings, the gate record summary, the verification record, and the held list.

Closing line for the held bundle: S2-E26, the last element held under this run, is RULED by Captain JP and closed. The question as put to her: "If one build anywhere fails a records check, should every other build's trust grade drop on its own?" The answers offered were "Yes, all drop" and "No, only the failing one". Her answer, quoted exactly: "No, only the failing one." Outcome: the automatic estate wide provenance grade drop is declined; no automatic estate wide drop exists, and a failure affects the failing build's own grade only, under the standing rules, with LEVEL-1 R-81 and DQ-011 unchanged and nothing overturned. No document landing is made under this ruling. With this ruling every element of the held bundle stands settled or ruled: S2-E8, S2-E14, S2-E15, S2-E16, S2-E19, and S2-E22 settled by the Manager under Captain JP's grant, S2-E9 settled by the Manager under her pass 2 grant, and S2-E26 ruled by Captain JP here. The ruling is also recorded in the trace file named above.

### DQ-024: Step 7 pack, S3 graded verdicts that travel

Status: SETTLED, closed. Settled by a pick of the Manager under Captain JP's grant. This entry is not a ruling by Captain JP, and it is not recorded as one.

Settled by: The Manager (Muse), under Captain JP's grant, in her words: "I changed my answer to u pick"

Owner of record: Decision-queue Clerk

Source: The plan Step 7 ruling pack. S3, graded verdicts that travel, is the third of eight survivors recorded in `creative-expansion.md`. The item was presented to Captain JP as the third item of that pack; it is numbered DQ-024 here, on its settlement. DQ-023 is assigned to the S2 run of the same pack and is entered by that run.

The question that was open: Whether graded verdicts that travel are implemented, implemented in reduced form, or held.

The options that were presented:

- Implement S3: the four grades, PASS, PASS-QUALIFIED, FAIL, and DISCLAIMED, are imposed as one verdict vocabulary across every verdict in the flow at once, renamed everywhere the flow's existing grades differ.
- Implement S3 reduced: the four grades are named as the travelling verdict vocabulary of the flow, the flow's existing grades are mapped onto that vocabulary rather than renamed, and the reconciliation with the Eval-Driven Development verdict system is deferred to plan Step 8, where that system lands.
- Hold S3: graded verdicts that travel are not implemented and are held.

Manager's recommendation and pick: Implement S3 reduced. The recommendation was stated at the top of the pack when the item was presented. Captain JP changed her answer to a delegation, in the words quoted above, and the Manager's pick under that grant is the recommended form: Implement S3 reduced.

Decision: The reduced form. The four grades are named as the travelling verdict vocabulary of the flow: a verdict carries its grade, and any named qualification on it, wherever the verdict is cited, and no citation may present a verdict stronger than its grade. The flow's existing grades keep their names and are mapped onto the vocabulary, not replaced: PASS-QUALIFIED in the live proof rule (R-11) is the vocabulary's PASS-QUALIFIED; the closure states CLOSED-PASS, CLOSED-QUALIFIED, and CLOSED-FAIL carry the verdicts PASS, PASS-QUALIFIED, and FAIL; and the state UNVERIFIABLE is expressed in verdict form as DISCLAIMED, as R-3 and R-8 already record. No existing verdict or closure grade is renamed by this settlement.

Deferred reconciliation, named: the reconciliation of this verdict vocabulary with the Eval-Driven Development verdict system is deferred to plan Step 8, where that system lands. It is recorded here and in the Step 7 S3 implementation trace as a named deferred item, DR-S3-EDD, and it is not done under this settlement. Until Step 8 settles it, a verdict issued under the Eval-Driven Development system is cited in that system's own grades and is not restated in this vocabulary.

Reasons recorded for the pick:

- The grades are already the flow's working verdict grades in substance: R-8 states the same closed vocabulary in its verdict form, and the mapping makes that one vocabulary explicit at the vocabulary's home instead of renaming the flow a second time when the Eval-Driven Development system lands.
- A wholesale rename would touch every verdict and closure passage in the flow now and be reopened at Step 8; the mapping carries the same force with no rename.

Where the settlement landed:

- LEVEL-1, R-3: the travelling verdict vocabulary named at the work-state vocabulary, with the mapping of the existing grades onto it and the deferred Step 8 reconciliation boundary stated.
- LEVEL-2, R-8: a pointer to the LEVEL-1 naming, the verdict form itself unchanged.
- This queue: the item is closed and this entry is its record.

What remains open after this settlement: only the named deferred reconciliation, DR-S3-EDD, which belongs to plan Step 8 and is not a residue that reopens this item.

### DQ-025: Step 7 pack, S4 gates outcome distribution

Status: SETTLED, closed. Settled by a decision of the Manager under Captain JP's grant. This entry is not a ruling by Captain JP, and it is not recorded as one.

Settled by: The Manager (Muse), under Captain JP's grant, in her words: "You pick"

Owner of record: Decision-queue Clerk

Source: Implementation Plan Step 7 ruling pack; creative expansion survivor S4 in ~/workspace/build-flow-expansion/creative-expansion.md (gates at major closures only, deciding over mechanical fact patterns, outcome distributions logged).

The question that was open: Should S4 be implemented in full (gates at major closures only, with logged outcome distributions), implemented reduced, or held?

Manager's recommendation: Implement reduced. This was the Manager's recommendation, stated at the top of the pack.

The three options that were presented:

- Implement S4 in full: gates at major closures only, with logged outcome distributions.
- Implement S4 reduced: the logged outcome distribution part only, with gate placement unchanged.
- Hold S4: S4 is not implemented and is held.

Decision: Implement S4 reduced. Boards and gates stay at every step exactly as DQ-009 ruled; gate placement is not changed by this settlement. Only S4's second half lands: a logged distribution of gate outcomes (go, hold, recycle, kill, the four outcomes of R-51) across a build, kept where the metrics and reporting system reads it, so a gate's pattern over a build is visible in numbers.

Express note: the full form's gate placement half (gates at major closures only) is not implemented, because it would overturn DQ-009 (boards at every step), and only Captain JP can rule again on DQ-009. Nothing in this settlement reduces, merges, or removes any step's board or gate.

Where the settlement landed:

- Trace file named for the settlement: ~/workspace/build-flow-expansion/step-7-s4-implementation-trace.md.
- Landing homes for the implementation run: METRICS.md and REPORTING.md, with any LEVEL-2 pointer the run finds it needs. Exact landing passages are as recorded by the implementation run in those homes; none is quoted here.
- This queue: the open item is closed and this entry is its record.

What remains open after this settlement: nothing in the question itself.

### DQ-027: Step 7 pack, S6 path-keeping

Status: RULED, closed

Ruled by: Captain JP

Owner of record: Decision-queue Clerk

Ruling text: "Implement S6 reduced"

Source: The plan Step 7 ruling pack. S6, path-keeping, is the sixth of eight survivors recorded in `creative-expansion.md`. The item was presented to Captain JP as the sixth item of that pack; it is numbered DQ-027 here, on its ruling.

The question that was open: Whether path-keeping is implemented, implemented in reduced form, or held.

The options that were presented:

- Implement S6: path-keeping is implemented in its full form, as a four-tier institution restated whole.
- Implement S6 reduced: the two parts of S6 that already stand are recorded as already landed and are not restated; the two genuinely new parts land, restated for the flow's five tiers.
- Hold S6: path-keeping is not implemented and is held.

Manager's recommendation: Implement S6 reduced. This was the Manager's recommendation, stated at the top of the pack. Captain JP took the recommendation: she chose Implement S6 reduced.

Ruling outcome: The reduced form, in Captain JP's words: "Implement S6 reduced". The parts recorded as already landed, not restated: the mechanical verifier, which stands as the attested closure check of DQ-011 (the three checks of R-80, run by a verifier other than the coordinator, at grade L2 under R-81); and Captain JP by exception or board at closure, which stands as the review board at every step ruled at DQ-009 (R-55). The two new parts that land, restated for five tiers: first, the duty to consult the build's path ledger before acting, carried in the spawn or task header of every agent brought into a build; second, a challenge at closure answered against the ledger's record, in which the closing step states its claim against the ledger and the verifier's check answers that claim from the ledger, as part of the existing attested closure check and not as a new separate ceremony. The implementation follows the standing procedure as a scoped single-survivor run under plan Step 7, with the freeze deferred to the close of Step 7.

Where the ruling landed:

- Trace file named for the ruling: ~/workspace/build-flow-expansion/step-7-s6-implementation-trace.md. The implementation rows and their verification are recorded there.
- This queue: the item is closed and this entry is its record.

### DQ-026: Step 7 pack, S5 failures-first annex and definition regression corpus

Status: SETTLED, closed. Settled by a pick of the Manager under Captain JP's grant. This entry is not a ruling by Captain JP, and it is not recorded as one.

Settled by: The Manager (Muse), under Captain JP's grant, in her words: "You pick"

Owner of record: Decision-queue Clerk

Source: The plan Step 7 ruling pack. S5, the failures-first annex and the definition regression corpus, is the fifth of eight survivors recorded in `creative-expansion.md`. The item was presented to Captain JP as the fifth item of that pack; it is numbered DQ-026 here, on its settlement.

The question that was open: Whether the failures-first annex and the definition regression corpus are implemented, implemented in reduced form, or held.

The options that were presented:

- Implement S5: the failures-first annex and the definition regression corpus are implemented in their full form.
- Implement S5 reduced: a short failures-first annex lands in the flow documents, naming the existing regression corpus as the standing test every amendment must pass, and no second corpus or annex copy is created inside the flow documents.
- Hold S5: the failures-first annex and the definition regression corpus are not implemented and are held.

Manager's recommendation and pick: Implement S5 reduced. The recommendation was stated at the top of the pack when the item was presented, in favour of Implement reduced. Captain JP delegated the pick, in the words quoted above, and the Manager's pick under that grant is the recommended form: Implement S5 reduced.

Decision: The reduced form, exactly. The regression corpus stays the single working copy where it lives, at `~/workspace/build-flow-expansion/REGRESSION-CORPUS.md`, built at plan Step 3 from the 224 incidents. No second corpus or annex copy is created inside the flow documents. What lands is a short failures-first annex in the flow documents naming that corpus as the standing test every amendment must pass, with the gate rule as Captain JP ruled it at DQ-002: a hard gate, under which an amendment that would have allowed a corpus incident is rejected, unless Captain JP explicitly re-rules that incident through this queue.

Where the settlement is to land:

- A short failures-first annex in the flow documents, in the form recorded in the Step 7 S5 working paper at `~/workspace/build-flow-expansion/scratch-step7-s5/agent-a-analysis.md`. The annex names the single corpus above and states the DQ-002 hard gate at full strength.
- This queue: the item is closed and this entry is its record.

What remains open after this settlement: nothing in the question itself.

### DQ-028: Step 7 pack, S7 the halt institution

Status: RULED, closed

Ruled by: Captain JP

Owner of record: Decision-queue Clerk

Ruling text: "Implement S7 reduced"

Source: The plan Step 7 ruling pack. S7, the halt institution, is the seventh of eight survivors in ~/workspace/build-flow-expansion/creative-expansion.md (section S7, the halt institution, whole). The item was presented to Captain JP as the seventh item of that pack; it is numbered DQ-028 here, on its ruling.

The question that was open: Whether the halt institution is implemented, implemented in reduced form, or held.

The options that were presented:

- Implement S7: the halt institution is implemented in its full form.
- Implement S7 reduced: the halt institution is implemented in reduced form.
- Hold S7: the halt institution is not implemented and is held.

Manager's recommendation: Implement S7 reduced. This was the Manager's recommendation, stated at the top of the presentation. Captain JP took the recommendation: she chose Implement S7 reduced.

Ruling outcome: The reduced form, in Captain JP's words: "Implement S7 reduced". The stop authority itself is already landed in the flow (the stop-work rules from the research-2 implementation, R-2 and R-82 to R-84 in LEVEL-1) and is not restated. What lands is the institution around the stop, where it was missing: (1) every halt is issued in a record that names its scope, its reason, who issued it, and the named restart authority for that halt; (2) a halt is lifted only by that named restart authority, never by the passage of time, never by the team that was stopped, and never by the agent who was stopped resuming on its own; the lift is itself recorded in the same record. The implementation follows the standing procedure as a scoped single-survivor run under plan Step 7, with the freeze deferred to the close of Step 7.

Where the ruling landed:

- Trace file named for the ruling: ~/workspace/build-flow-expansion/step-7-s7-implementation-trace.md. The implementation rows and their verification are recorded in that trace.
- This queue: the item is closed and this entry is its record.

### DQ-029: Step 7 pack, S8 checklist as interface

Status: SETTLED, closed. Settled by a decision of the Manager under Captain JP's grant. This entry is not a ruling by Captain JP, and it is not recorded as one.

Settled by: The Manager (Muse), under Captain JP's grant, in her words: "You know what, just do what you think is best."

Owner of record: Decision-queue Clerk

Source: The plan Step 7 ruling pack. S8, checklist as interface, is the eighth of eight survivors recorded in `creative-expansion.md`. S8 was presented with the Manager's recommendation at the top, Implement S8 reduced. Captain JP, on a voice call and tired of reading, asked for the question explained and for its options, then delegated the pick in the words quoted above.

The question that was open: Should S8 be implemented in full, implemented reduced, or held?

Manager's recommendation: Implement S8 reduced. This was the Manager's recommendation, stated at the top of the presentation.

The three options that were presented:

- Implement S8 in full: checklists as the transition interface, in BCP 14 and EARS language, with killer item lists generated from transition preconditions by generator tooling.
- Implement S8 reduced: the language half recorded as already landed, and the generation rule with its named pause points landed, with no generator tool.
- Hold S8: S8 is not implemented and is held.

Decision: Implement S8 reduced, in the form presented. The language half already landed at R-75 and R-76 and is not restated. The generation rule and its named pause points land: the pause points named for the generation rule are two only, the gates and the closures, and at those points the checklist a step is judged against is drawn by the step's own record keeper from that step's stated preconditions as written. The full form is not taken, and no generator tool is commissioned or built.

Where the settlement landed:

- LEVEL-2, R-92: the generation rule, stating that at the gates and at the closures the checklist a step is judged against is drawn from that step's stated preconditions as written, drawn by the step's own record keeper, with the step record naming the record keeper who drew it. Two pointers carry a reader to that rule: the Auditor approval gate passage in LEVEL-2, and the closure passage inside R-7 in LEVEL-2.
- Trace file named for the settlement: ~/workspace/build-flow-expansion/step-7-s8-implementation-trace.md.
- This queue: the open item is closed and this entry is its record.

What remains open after this settlement: nothing in the question itself.

#### Reconciliation addition

Two runs implemented the same S8 settlement in parallel.

R-92 as landed by the first run stands as the authoritative landing, including its added provisions: the preconditions drawn from must predate the judging point, drawing the checklist creates no new criteria, and the step record names the drawer.

On the Manager's decision, two sentences from the second run's gated wording were added to R-92: the amendment sentence, landed with the bound that the amendment is in force for the build, stated in the sentence, per the consistency check against R-13 and binding reading 3 of the second run's gate record, and the not held consequence sentence, landed with the added clause naming a checklist that omits a stated precondition meeting R-61's killer test, per the consistency check against binding reading 2.

The second run's gate record, at scratch-step7-s8/gate-record.md, stands as evidence for those two sentences.

The landing of S8 is complete with this reconciliation included.

### DQ-030: Note-taking and design team sizes at Low and Medium

Status: RULED, closed

Ruled by: Captain JP

Owner of record: Decision-queue Clerk

Ruling text: "Adopt the draft sizes"

Source: The gap flagged by the DQ-017 per-level amounts map: the note-taking team and the design team had stated sizes at High, Extra High, and Plaid, and no stated sizes at Low and Medium.

The question that was open: What are the base sizes of the note-taking team and the design team at Low and at Medium?

The options that were offered:

- Adopt the draft sizes
- I will rule the sizes myself

Ruling outcome: The first option. Captain JP tapped the option and stated in words: "Adopt the draft sizes". The draft sizes are adopted, for both teams at all five tiers:

- Note-taking team: 4 distinct members at Low, 4 at Medium, 4 at High, 8 at Extra High, 8 at Plaid. Reason as presented: its four roles (Scribe, Structure Mapper, Evidence Keeper, Completeness Contrarian) are the floor at any tier, because the notes file's author record is meaningless if one agent covers two sections; the higher tiers add the optional seats.
- Design team: 2 distinct members at Low, 3 at Medium, 4 at High, 8 at Extra High, 8 at Plaid. Reason as presented: scopes combine at the small end, while the Contrarian and the Fold-in Tracer are never the seats dropped.

Where the ruling landed:

- LEVEL-3, Note-taking team section: the Base size line now states all five tiers, 4 at Low, 4 at Medium, 4 at High, 8 at Extra High, 8 at Plaid.
- LEVEL-3, Design team section: the Base size line now states all five tiers, 2 at Low, 3 at Medium, 4 at High, 8 at Extra High, 8 at Plaid.
- LEVEL-2, Step 2 and Step 6: the count lines that stated numbers only for High and Extra High are completed to all five tiers. The lines that point to Step 6 state no numbers and needed no change.
- PLAID.md: checked and unchanged. It staffs both teams at 8, and no passage in it contradicts the adopted Low and Medium sizes.
- This queue: the item is closed and this entry is its record.

### DQ-031: The Manager's end of step additions rule

Status: RULED, closed

Ruled by: Captain JP

Owner of record: Decision-queue Clerk

Ruling text: "Land the additions rule"

Source: The Manager's discretion grant for this build and Captain JP's scope correction on that grant. Captain JP granted the discretion for this build only, the build of the build flow itself (the implementation plan run), in her scope correction, in her words: "I'm not talking about the build, i'm talking about the build flow build." The drafted additions rule was a proposal delivered to Captain JP for her ruling, and it was expressly not landed for product builds.

The question that was open: Whether the drafted Manager's end of step additions rule lands as a rule of this build, the build of the build flow itself.

The options that were presented:

- Land the additions rule
- Hold the additions rule

Ruling outcome: Captain JP tapped the option and stated in words: "Land the additions rule". The first option. The additions rule lands as a rule of this build, with the scope stated inside the rule itself. It does not extend to product builds run under the flow unless Captain JP rules otherwise.

Landed rule text: "At the end of each step the Project Manager may add anything the Manager judges the step or the build needs. Additions are recorded in the step's record as Manager's additions, with their reasons. An addition never reopens a closed step's trace and never substitutes for the Auditor's approval, who judges the step as it stands with its additions. The discretion is the Manager's alone. This rule governs the build of the build flow itself; it does not extend to product builds run under the flow unless Captain JP rules otherwise."

Where the ruling landed:

- LEVEL-1, R-91: the Manager's end of step additions rule stated with the Manager's standing rules, near R-50.
- This queue: the item is closed and this entry is its record.

### DQ-032: Step 6 Q3, where skip records live

Status: SETTLED, closed. Settled by a decision of the Manager under Captain JP's grant. This entry is not a ruling by Captain JP, and it is not recorded as one.

Settled by: The Manager (Muse), under Captain JP's grant, in her words: "You decide"

Owner of record: Decision-queue Clerk

Source: Step 6 implementation trace Q3, Items 28 and 33 (the creative process implementation's open question on where skip records live).

The question that was open: When a step skips one of the creative moves, where is the skip recorded so it can be seen?

The three options that were presented:

- Step record only: the skip is recorded in the step record and nowhere else.
- Summarised in the gate packet: a summary of the step's skips is carried in the Auditor's packet for the step's review board.
- Visible in the queue: skips are entered in the decision queue, where they can be seen.

Recommendation: The Manager's recommendation favoured the second option, summarised in the gate packet.

Decision: The recommended form. Every skip of a creative move at a step is recorded in the step's record with its reason and its return trigger, as the skip doctrine already states. In addition, the Auditor's packet for that step's review board carries a summary of the step's skips: each skip named, with its reason and return trigger in short form, so the board sees every skip as part of judging the step. Skips do not go into the decision queue. The never skip rule for the Framer, the Breaker, and the Trade-off Judge on an irreversible decision (R-89) is untouched: those moves may not be skipped at all on such a decision, so they are not skips this settlement covers.

Where the settlement landed:

- LEVEL-1, Skipping a move: the visibility rule stated at the skip doctrine, that the step record carries each skip with its reason and its return trigger, that the Auditor's packet for the step's review board carries a summary of the step's skips in short form, and that skips are not entered in the decision queue.
- LEVEL-2, the Auditor approval gate passage: a pointer to the LEVEL-1 definition for the packet's skip summary.
- This queue: the item is closed and this entry is its record.

What remains open after this settlement: nothing in the question itself.

### DQ-033: Step 12 unit order, audit, fix, audit logic, fix logic

Status: RULED, closed

Ruled by: Captain JP

Owner of record: Decision-queue Clerk

Ruling text: "No it should be audit fix audit logic fix"

Source: Captain JP's correction of Step 12 of the build flow, the audit fix loop, given while the checklist and flow documents were being aligned to her earlier direction on this step.

The question that was open: What units staff Step 12, the audit fix loop, and in what order?

Captain JP first put the step as five units in her words, "audit audit, fix, logic, fix", and then corrected her own wording in the ruling text above. The corrected wording is the ruling of record: four units, in this order: Audit; Fix; Audit logic; Fix logic. The five unit phrasing is superseded by her correction and stands nowhere in the flow documents or the checklist.

Ruling outcome: Step 12 is staffed, in order, as Audit, Fix, Audit logic, Fix logic. Each unit staffs at the amount the flow already rules for it: the colour lens audit amount for the tier (3 at Low, 9 at Medium, 21 at High, 35 at Extra High, 35 at Plaid), the build team size for the tier for Fix and for Fix logic (1 at Low, 2 at Medium, 3 at High, 6 at Extra High, 12 at Plaid), and the logic audit amount for the tier for Audit logic (5 at Low, 15 at Medium, 25 at High, 35 at Extra High, 35 at Plaid). The step totals are 10 at Low, 28 at Medium, 52 at High, 82 at Extra High, and 94 at Plaid. No new roles are created; the agents for all four units already exist. At Plaid the Audit logic unit is staffed from the logic audit team's counted seats, so the distinct agent union totals per tier are unchanged: 33 at Low, 52 at Medium, 84 at High, 137 at Extra High, 202 at Plaid.

Where the ruling landed:

- LEVEL-2, Step 12: the unit list and order now read Audit; Fix; Audit logic; Fix logic, with the counts line and the step total restated, and the introduction's logic audit amounts passage now names Step 12 alongside Steps 7 and 9.
- LEVEL-2 introduction and LEVEL-3, Logic audit team: the team is recorded as staffed again for Step 12's Audit logic unit, from its counted seats.
- FLOW.md, the path in outline: Step 12 now carries its unit list, as the other loop steps do.
- PLAID.md: the per-step staffing table's Step 12 row now reads 94, composed of Audit 35, Fix 12, Audit logic 35, Fix logic 12, and the logic audit team passages record that Step 12 adds no new distinct agents.
- The five logic auditor agent files: their place in the flow now names the audit fix loop at Step 12 alongside the brief loop and the plan loop.
- The Build Flow Checklist: Step 12 gains the Audit logic and Fix logic units in the ruled order, and the tickable total moves from 76 to 78, with no project's board state moved.
- This queue: the item is closed and this entry is its record.

What remains open after this ruling: nothing in the question itself.

Correction addition to DQ-033, on the union totals: the ruling outcome above expected the distinct agent union totals per tier to stand unchanged, and verification by the union method showed that expectation wrong at three tiers, for a reason outside Step 12 itself. The checklist's Step 7 and Step 9 Audit logic rosters carried 3 at Low, 9 at Medium, and 21 at High, the colour lens amounts, where LEVEL-2 rules the logic audit amounts as 5 at Low, 15 at Medium, and 25 at High. Correcting those two rosters to the ruled amounts, with the same logic auditor seats Step 12 fields, raised the counted distinct logic seats per tier and moved the union totals to 35 at Low, 58 at Medium, and 88 at High. Extra High stands at 137 and Plaid at 202, unchanged, because the logic rosters there already matched the ruled amounts and Step 12's Audit logic unit is staffed from the plan loop's counted seats at Plaid. Step 12 itself adds no new distinct agents at any tier. The checklist's displayed tier totals now read 35, 58, 88, 137, and 202. The four unit form of the ruling, and every other part of this entry, stands as recorded.

### DQ-034: Eval-Driven Development Item 322, the companion guide in the working order

Status: SETTLED, closed. Settled by a decision of the Manager under Captain JP's standing delegation. This entry is not a ruling by Captain JP, and it is not recorded as one.

Settled by: The Manager (Muse), under Captain JP's standing delegation

Owner of record: Decision-queue Clerk

Source: consolidated/02-eval-driven-development.md, Added part, Which ring, which gate, Item 322 in the Step 8 extraction (extraction-b.md), ruled Conflict in the Step 8 rulings.

The question: In the working order for an agent mid build (guide entry first, then the EDD admission loop), which companion guide is the guide?

The options, stated plainly:

- Name the guide: Captain JP names the document that is the companion guide, and the working order lands as a rule referring to that named document.
- No guide: the working order does not land; techniques are adopted through the flow's existing grill, research, and design steps, and the EDD admission loop at Item 252 applies to changes without a guide stage in front of it.
- Manager settlement: the settlement proposed in the Manager settlement candidates section of the Step 8 rulings, namely that the working order lands only where a build's grill record names a companion guide, and does not apply where none is named.

Decision: The Manager settlement. The guide-first working order lands only where a build's grill register or brief names a companion guide, and does not apply where none is named. In the settled form: where a build's grill decisions register, or its design brief, names a companion guide as a source for techniques in that build, the working order applies to techniques taken from that guide: guide entry first (fit, activation trigger, inputs, outputs, decision rules, exclusions, failure modes), then the EDD admission loop. Where no companion guide is named for a build, Item 322 does not apply to that build and no guide stage is implied. Item 323, ruled Adopt, is unaffected.

Cost of deciding late: low. Nothing in the implemented flow depends on a companion guide today, and the EDD items land without this one; the cost is that Item 322 stays unimplemented and any build that does use a guide has no ruled working order for combining the two.

What it blocks: Item 322 only. It blocks no other Step 8 item and no stage of the EDD implementation.

Ordering reason: this is the easiest of the three prepared entries to answer, a single naming choice or a no, with no numbers, no legal content, and no tier content.

Where the settlement landed:

- Plan Step 8: Item 322 is implemented in this settled form in plan Step 8.
- This queue: the item is closed and this entry is its record.

What remains open after this settlement: nothing in the question itself.

### DQ-138: The corpus gate against the strictness cost limb

Status: RULED, closed

Ruled by: Captain JP

Owner of record: Decision-queue Clerk

Ruling text: "Yes, the gate always wins."

Source: the banked settlement run over DQ-035 to DQ-137 and the S2 held elements. The run recorded one open principle at DQ-070: the strictness cost limb of Captain JP's settlement philosophy pointed toward settling that item, and the regression corpus hard gate at DQ-002 pointed the other way and rejected the settlement on corpus incidents C-137 and C-160. The question was put to Captain JP in the form: when saving build time and the failure-history gate disagree, does the gate always win?

The question that was open: Where the strictness cost limb (a strict reading dropped because it adds a huge build time) and the regression corpus hard gate point in opposite directions on the same item, which governs?

Ruling outcome: The corpus gate governs. A cost based softening never overrides a gate FAIL, and an item the gate fails has exactly the two outcomes DQ-002 states, rejected or re-ruled through this queue with the corpus ID named. This settles the open principle recorded at DQ-070; DQ-070's own question, the consequence for stages passed by a gate later reclassified, stays banked and is not decided by this ruling.

Where the ruling landed:

- Standing procedure, Part (c): a closing point states that the corpus gate governs over any cost based softening of the same item.
- DQ-070: a cross-reference line in that entry names this entry as the record of the principle.
- This queue: this entry is the record of the ruling.

### DQ-139: Clashing settlements in the same passage

Status: RULED, closed

Ruled by: Captain JP

Owner of record: Decision-queue Clerk

Ruling text: "Used discernment in that situation"

Source: the banked settlement run over DQ-035 to DQ-137 and the S2 held elements. The run's trace recorded a tension between two Manager settlements, DQ-095 and DQ-136, which read the parentage of the word Ruled differently inside the same paragraph of LEVEL-1 rule R-3, and the trace resolved that instance in run order, with DQ-136's landed text standing. The question was put to Captain JP in the form: if two of my answers clash inside the same rule, does the newer answer win?

The question that was open: When two Manager settlements land in the same passage and read it differently, does the later settlement govern by its recency alone, or is the clash resolved another way?

Ruling outcome: The clash is resolved by discernment in the situation, on the merits of the passage and the standards involved. Recency alone never decides. The DQ-095 and DQ-136 tension therefore stands resolved case by case under this ruling: for that instance, DQ-136's landed text stands, as the trace recorded. A later clash of the same kind is decided the same way, on its merits, with the decision and its reason recorded where the clash is found.

Where the ruling landed:

- This queue: this entry is the record of the ruling.

### DQ-140: Potential problem causers in the final build document

Status: RULED, closed

Ruled by: Captain JP

Owner of record: Decision-queue Clerk

Ruling text: "Make a new final with the project called potential problem causers, that way, if the system causes problems in the future or someone installs it, they know that it's a potential issue, it should be in the final build document that gets put in the public repo"

Source: Captain JP's ruling in the side chat, given while the banked settlement run's results were being worked through with her as yes or no questions.

The question that was open: Does the document a build ships at its close carry the build's known potential issues where a later installer or operator will see them, or do those issues stay inside the build's own records?

Ruling outcome: Every build's final build document, the one that ships in the project's public repo, carries a section titled "Potential problem causers" listing the known potential issues with the system, written for someone installing or running it later, so that if problems appear in the future the installer already knows these were flagged as potential issues. The section is a required part of the final build document at the release gate; a final build document without it is incomplete. The section is installer facing product content for the public repo: it names potential issues plainly; it carries no design material, no build-flow working detail, and no builder mention.

Where the ruling landed:

- LEVEL-2, Step 22 (Release gate), Job: the final build document placed in the public repo must carry the section, and the gate does not pass on an incomplete final build document.
- LEVEL-2, R-27: the gate record's checklist items include the presence of the section in the final build document, with its result recorded.
- REPORTING.md, Report 2 (the build report): the report's contents carry the Potential problem causers section, which the final build document in the public repo carries under that title; the build report is incomplete without it.
- This queue: this entry is the record of the ruling.
- Trace: dq-140-trace.md, with the corpus gate record for the landed wording.

### DQ-141: Missing names, numbers, definitions and standards are filled in by the Manager

Status: RULED, closed

Ruled by: Captain JP

Owner of record: Decision-queue Clerk

Ruling text: "You fill it in, strict side."

Source: Captain JP's ruling in the side chat, given when she asked for philosophy questions that settle multiple banked answers at once. The question as put to her: "When a rule needs a number or a name that nobody ever set, who fills it in?" The answers offered were "You fill it in, strict side" and "It waits for me".

Ruling outcome: Where a flow rule needs a name, number, definition, or standard that no source supplies, the Manager sets it, on the strict side that is still workable, and records it as a Manager fill-in under this ruling in the queue item it completes, so Captain JP can find each value set and overrule any of them. A fill-in never touches what the flow reserves to Captain JP personally: tier assignment, the done definitions R-77 reserves to her, her own earlier rulings, legal substance, and money substance. A banked item whose missing piece is reserved substance of that kind, or which needs more than a fill-in, is not completed by this ruling and stays banked with its reason recorded.

Where the ruling landed:

- This queue: this entry is the record of the ruling.
- The items completed under it are recorded item by item in fill-in-trace.md, each with the exact value set stated in plain words.

### DQ-142: Tier protections follow the team actually staffed

Status: RULED, closed

Ruled by: Captain JP

Owner of record: Decision-queue Clerk

Ruling text: "The real team sets them."

Source: Captain JP's ruling in the side chat, given when she asked for philosophy questions that settle multiple banked answers at once. The question as put to her: "A build's paper tier says one thing, but the team actually staffed is smaller. Which one sets the protections?" The answers offered were "The real team sets them" and "The paper tier sets them".

Ruling outcome: Where a build's recorded tier and the team actually staffed disagree, the protections, checks, and duties in force are those of the team actually staffed, as the rosters and spawn records show. A build may not claim a higher tier's protections on paper while running a smaller team, and a build staffed above its recorded tier carries the instruments of the staffing actually in place. Actual staffing never selects or changes the recorded tier: the recorded tier stays as the record of what was assigned, and any shortfall or excess of actual staffing against it is itself recorded in the tier record. Tier assignment itself is untouched by this ruling and stays where R-4 and PLAID.md place it.

Where the ruling landed:

- LEVEL-1, R-4: a closing passage states that protections, checks, and duties follow the team actually staffed where the recorded tier and the actual staffing disagree, in both directions, with the tier record standing as the record of assignment and the shortfall or excess itself recorded.
- PLAID.md, section 1: a closing passage states that the tier's instruments attach by actual staffing, not by the tier record alone; a build staffed at Plaid numbers carries the section 3 instruments in force without becoming a Plaid build, and a build recorded at Plaid but staffed below those numbers has in force only the instruments of the team actually staffed.
- DQ-073 is ruled by application of this ruling, in that entry.
- This queue: this entry is the record of the ruling.
- Trace: tier-ruling-trace.md, with the corpus gate record for the landed wording and the disposition of every tier group item scanned under this ruling.

### DQ-143: Money questions, no flat rule, discernment in the situation

Status: RULED, closed

Ruled by: Captain JP

Owner of record: Decision-queue Clerk

Ruling text: "Use discernment if you should ask me."

Source: Captain JP's ruling in the side chat, given when the banked money questions were put to her as one batch. The question as put to her: "Three questions are about money. Keep money questions always yours, or settle them under the same strict rules?" The answers offered were "Money is always mine" and "Settle money the same way". Her answer sets neither flat rule.

Ruling outcome: Money questions carry no flat rule. Whether a money question comes to Captain JP is decided by the Manager's discernment in the situation. Anything that commits funds, or that sets or changes a budget, a price, a stake, or a money obligation, comes to Captain JP. Money mechanics that only record, report, or enforce what is already ruled may be settled by the Manager under her standing philosophy, recorded as Manager settlements under this ruling, each open to her overruling.

Where the ruling landed:

- This queue: this entry is the record of the ruling.
- DQ-050: assessed under this ruling as mechanics, settled by the Manager, and landed at LEVEL-1, R-50; the assessment and settlement are recorded in that entry.
- DQ-092 and DQ-112: assessed under this ruling as hers, and left banked marked as hers; the assessment is recorded in each entry.
- Trace: money-ruling-trace.md, with the corpus gate record for the DQ-050 landing.

### DQ-144: The reach of a ruling to a case it did not name

Status: RULED, closed

Ruled by: Captain JP

Owner of record: Decision-queue Clerk

Ruling text: "Use discernment case by case."

Source: Captain JP's ruling in the side chat, given when the questions on how far her own rulings reach were put to her as one batch. The question as put to her: "Two questions ask how far your own rulings reach. Does a ruling of yours bind everything under it, including work built later, until you change it?" The answers offered were "Yes, they bind until I change them" and "No, new cases come back to me". Her answer sets neither flat rule.

Ruling outcome: Whether one of Captain JP's rulings reaches a case it did not name is decided case by case, by discernment on the ruling's words and the case's facts. There is no standing rule that her rulings bind everything under them, and no standing rule that every new case returns to her. Where discernment finds that the ruling plainly covers the case, the ruling governs the case. Where it plainly does not, the case is open. Where it is genuinely unclear, the case comes to Captain JP.

Where the ruling landed:

- This queue: this entry is the record of the ruling.
- DQ-113 and DQ-120: each assessed under this ruling in its own entry. Neither is closed by it, for the reason recorded there.

### DQ-145: The seven half settled items are finished by the Manager, the same way

Status: RULED, closed

Ruled by: Captain JP

Owner of record: Decision-queue Clerk

Ruling text: "Yes, finish them that way."

Source: Captain JP's ruling in the side chat, given when the seven items settled in part under the pass 2 grant were put to her as one batch. The question as put to her: "Seven questions are half answered. The other half is one missing limit or consequence in each. Finish all seven the same way?" The answers offered were "Yes, finish them that way" and "No, bring me each half". "That way" as defined to her: strict side, anti-cheat test first, everything written down where she can overrule it.

Ruling outcome: The unsettled limbs of the seven half settled items, DQ-066, DQ-068, DQ-070, DQ-087, DQ-093, DQ-104, and DQ-106, are finished by the Manager under her standing philosophy and the anti-cheat test, each completion recorded in its item as a Manager completion under this ruling, with the decision stated in plain words so Captain JP can overrule any of them. A limb that is in truth money substance, tier substance, legal substance, or a re-ruling of one of her own rulings is not finished under this ruling and stays banked with its reason recorded, as DQ-143 separately confirms for budget setting substance.

Where the ruling landed:

- This queue: this entry is the record of the ruling.
- The completion of each of the seven items is recorded in that item's entry, and the batch is traced in finishing-trace.md, with the corpus gate record at scratch-finishing/gate-record.md.

### DQ-146: The role charters, minor amendments by the Manager, major amendments to Captain JP

Status: RULED, closed

Ruled by: Captain JP

Owner of record: Decision-queue Clerk

Ruling text: "I feel like you can amend them if you think that it's the best thing to do , but ask me if it's major amendment"

Source: Captain JP's ruling in the side chat. The question as put to her: "The role charters, the papers that say what each role is, are reserved to you word for word. Keep them yours alone?" The answers offered were "Keep them mine alone" and "Amend them under the strict rules". Her answer sets a divided rule, neither answer whole.

Ruling outcome: The role charters under R-86 are no longer reserved to Captain JP word for word. The Manager may amend a charter when the amendment is the best thing to do, and records it as a Manager amendment under this ruling. A major amendment comes to Captain JP first. Major means changing what a role is, adding a role, removing a role, or changing a role's authority or its boundaries. Minor means wording, clarity, and aligning a charter with rulings already landed. Where major or minor is genuinely unclear, the amendment is treated as major and comes to her.

Where the ruling landed:

- LEVEL-1, R-86: a closing passage states the amendment rule, that the charters are not reserved to Captain JP word for word, that a minor amendment is the Manager's to make and record under this ruling, and that a major amendment, chartering and striking included, is made only on her ruling, with the genuinely unclear case treated as major.
- DQ-117: decided under this ruling and closed in that entry; the chartering and striking decisions it poses are major amendments and come to Captain JP under this ruling.
- This queue: this entry is the record of the ruling.
- Trace: charters-ruling-trace.md, with the corpus gate record for the R-86 landing.

### DQ-147: Broken rule, sound work, how a breach case is decided

Status: Ruled by Captain JP

Question as put on the Questions space: "A team breaks a rule, but the work they made is still good. What should happen?" Her answer, in her words: "Take a look at it and make a decision.If it actually will cause problems later down the line"

Ruled: there is no flat bad mark and no flat block. Where a team broke a rule and the step's work is otherwise sound, the case is examined and decided at the step's gate, and the test the decision turns on is whether the broken rule will cause problems later down the line. Landed in LEVEL-2-STEPS.md, in the Auditor approval gate passage where step outcomes are treated, in the form the regression corpus gate passed: a breach of the staffing rules, the audit-form rules, or the closure rules is not decidable under the passage, because the assurance behind such a step rests on the very rule that was broken, and the step is recorded PARTIAL and RECYCLED under R-7; a breach corrected before the step closes lets the step close in the ordinary form; a step let stand with the breach uncorrected closes only as CLOSED-QUALIFIED under the R-7 bounded exception, with the exception's four elements named in the step record. The decided case is written down in the step record: the breach, the examination, the decision, and the later problems found or not found; the decision stands for that step only and sets no precedent. The first drafted wording failed the corpus gate (C-137, C-186, C-194) and was revised to the gate's smallest passing change and re-gated clean before landing; the gate record is in the batch trace. Closed.

### DQ-148: Challenges to Captain JP's own earlier rulings, decided by discernment

Status: Ruled by Captain JP

Question as put on the Questions space: "Six questions challenge rulings you already made yourself. What should happen to them?" Her answer, in her words: "Use desernment"

Ruled: each challenge to one of Captain JP's own earlier rulings is decided case by case by discernment. Where discernment finds the challenge does not hold, the earlier ruling stands and the item closes as decided under this ruling. Where discernment finds a challenge would genuinely overturn one of her own rulings, the item is not overturned under this ruling: it stays banked, with the assessment recorded, and the question goes back to Captain JP as a single plain question. Applied to the six challenges banked at the time of the ruling (DQ-053, DQ-061, DQ-064, DQ-067, DQ-109, DQ-110): each was assessed under this ruling, none held, and each closed with its assessment recorded in its own entry. The ruling stands as the queue's standing treatment of challenges to her own rulings.

## Open items banked in the Steps 12 and 13 re-audit

The six entries below, DQ-131 to DQ-136, are appended at the end of this queue. No existing line of this queue is altered by the append.

### DQ-131: Team lead seat selection

Status: Banked

Owner of record: Decision-queue Clerk

Source: Steps 12 and 13 re-audit. Triage 3 Q-01, item N-06, from register defect AUD-D142.

The question: Who selects the seated scopes in the four LEVEL-3 team entries, Research, Imagination, Design and Build, whose seat selection sentences name the team lead for the stage as the selecting authority, a role the set does not contain, with no appointment, seat or roster form stated anywhere in the set? This question arose in the Steps 12 and 13 re-audit.

The options, stated plainly:

- Define team lead as a rostered role in LEVEL-4, with its appointment, seat and spawn record form stated in the ruling, one lead per team per stage.
- Replace the selector in the four LEVEL-3 sentences with a named existing role for each team, stated in the ruling.
- Name the Project Manager, Muse as Manager under R-50, as the selector for every team, in the form the AUD-D043 chooser naming used.

Cost of deciding late: stated in the re-audit register design questions section for this item; the underlying passage stands in its current form until this entry is ruled.

What it blocks: any repair of the four seat selection sentences. Until this entry is ruled, those sentences name an authority no roster can record.

Ordering reason: this entry was banked in the Steps 12 and 13 re-audit and sits after DQ-130 in banking order; its presentation order is for the Decision-queue Clerk to set under the queue ordering rule.

#### Fill-in under Captain JP's ruling at DQ-141: DQ-131

Settled by: The Manager (Muse), as a fill-in under Captain JP's ruling at DQ-141, in her words: "You fill it in, strict side."

Fill-in: The selector in the four LEVEL-3 team entries, Research, Imagination, Design, and Build, is the Project Manager, Muse as Manager under R-50, for every team.

Landing: LANDED, LEVEL-3-TEAMS.md, in the seat selection sentence of each of the four team entries, Research teams, Imagination team, Design team, and Build team, where the selecting authority now reads the Project Manager and nothing else in those sentences was changed.

Status: SETTLED as a Manager fill-in under DQ-141, not ruled by Captain JP. The value set stands until Captain JP overrules it.

### DQ-132: Voided stage single state

Status: Banked

Owner of record: Decision-queue Clerk

Source: Steps 12 and 13 re-audit. Triage 3 Q-02, Logic NF-2, at LEVEL-2 R-8 and LEVEL-1 R-3.

The question: What is the single state of a voided stage instance, where R-8 states the outputs move to REFERENCE-ONLY, the stage is RECYCLED, and the work is redone, while R-3 states the item moves from its CLOSED state to REFERENCE-ONLY as a move of the record and not a reopening of the work, and R-90 requires exactly one position state per instance? This question arose in the Steps 12 and 13 re-audit.

The options, stated plainly:

- The instance stands RECYCLED, its outputs held in REFERENCE-ONLY as evidence, and the work is redone inside the same record chain.
- The instance stands REFERENCE-ONLY, as R-3 states the record move, and any redo is a new build or round, not a continuation.

Cost of deciding late: stated in the re-audit register design questions section for this item; the underlying passage stands in its current form until this entry is ruled.

What it blocks: any settlement of the voided instance posture in R-8 and R-3. The reliance cascade repair at REA-R43 in the re-audit register does not settle this question.

Ordering reason: this entry was banked in the Steps 12 and 13 re-audit and sits after DQ-130 in banking order; its presentation order is for the Decision-queue Clerk to set under the queue ordering rule.

#### Settlement under Captain JP's pass 2 grant: DQ-132

Settled by: The Manager (Muse), under Captain JP's pass 2 grant, in her words: "Do another high discernment pass. I do not want the system to cheat itself or agents to cheat the system plus all the other stuff I said before."

Governing standard: the anti-cheat test first, that the system must not cheat itself and agents must not cheat the system, then Captain JP's settlement philosophy, security first, quality second, speed last, strict reading where workable unless it adds a huge build time, workable reading where strict is unworkable or too costly, neither good stays hers, and genuine redundancy removed with the surviving passage named, with DQ-138, the corpus gate governs over cost, and DQ-139, clashes decided by discernment on the merits and never by recency.

Settlement: A voided stage instance stands RECYCLED as its single position state under R-90. The voided verdict record and the stage outputs move to REFERENCE-ONLY as evidence and carry no live claims. The work is redone as a new linked instance in IN PROGRESS, as RECYCLED provides in R-3.

Deciding ground: anti-cheat, system side.

Landing: LANDED, LEVEL-1 R-3 terminal states paragraph, line 115.

Flag recorded: simplicity and cost pointed to REFERENCE-ONLY; the anti-cheat test governed under the stated order.

Status: SETTLED by the Manager under the pass 2 grant, not ruled by Captain JP. This item is settled.

### DQ-133: Release gate recorded non-pass class

Status: Banked

Owner of record: Decision-queue Clerk

Source: Steps 12 and 13 re-audit. Triage 3 Q-03, Logic NF-6, at LEVEL-2 R-27 and LEVEL-1 R-3.

The question: Which classes of recorded non-pass at the release gate fall under the R-3 bar, which states the Release-gate Keeper may not pass a build carrying an unexpired deferred Critical or High qualification, and which classes may be recorded as a qualified Go under R-27, which states a Go containing a recorded non-pass is recorded CLOSED-QUALIFIED with the non-pass named? This question arose in the Steps 12 and 13 re-audit.

The options, stated plainly:

- State in R-27 that the R-3 bar governs: a recorded non-pass that is a deferred Critical or High defect may never be recorded as a qualified Go, and any other recorded non-pass may.
- State a class list in R-27 of the non-passes that may pass in qualified form, naming the classes in the ruling.

Cost of deciding late: stated in the re-audit register design questions section for this item; the underlying passage stands in its current form until this entry is ruled.

What it blocks: any classification rule for recorded non-passes in the Step 22 gate record.

Ordering reason: this entry was banked in the Steps 12 and 13 re-audit and sits after DQ-130 in banking order; its presentation order is for the Decision-queue Clerk to set under the queue ordering rule.

#### Settlement under Captain JP's grant: DQ-133

Settled by: The Manager (Muse), under Captain JP's grant, in her words: "Go ahead and answer any of them yourself that seems simple enough. I care about security and quality over speed, i don't want things to be too strict that they're impossible, but they should be relatively strict to the standards they hold."

Strictness rule, in Captain JP's words: "If the stricter setting is not workable, then go with the workable. If the strict setting is workable go with it unless it adds a huge build time."

Settlement: At the release gate the R-3 bar governs: a recorded non pass that is a deferred Critical or High defect may never be recorded as a qualified Go. Any other recorded non pass may be recorded as a Go in CLOSED-QUALIFIED form with the non pass named.

Deciding limb: strict workable. Source of settlement text and limb: classify-d.md and refinement-abd.md Part 1 limb audit.

Status: SETTLED by the Manager under the grant, not ruled by Captain JP. This item is settled.

### DQ-134: Sandbox egress authority identity

Status: Banked

Owner of record: Decision-queue Clerk

Source: Steps 12 and 13 re-audit. Triage 1 DQ-A, from Red A finding REAUD-RA-N4 and the AUD-D022 repair.

The question: Which named authority may permit egress from the sandbox for end state grading in red-hostile-inputs.md: the Auditor, as the repair round 1 fix named, the Safety Reviewer, or another named authority? The structured duty form landed at AUD-D022; only the identity of the authority is ungrounded in the set. This question arose in the Steps 12 and 13 re-audit.

The options, stated plainly:

- The Auditor, as the AUD-D022 repair named, with the permission named in the run record before the run.
- The Safety Reviewer, by a one line correction to the name in the file.
- Another named authority, named in the ruling, with its permission record stated in the ruling.

Cost of deciding late: stated in the re-audit register design questions section for this item; the underlying passage stands in its current form until this entry is ruled.

What it blocks: any correction of the authority name in red-hostile-inputs.md. No other part of AUD-D022 waits on it.

Ordering reason: this entry was banked in the Steps 12 and 13 re-audit and sits after DQ-130 in banking order; its presentation order is for the Decision-queue Clerk to set under the queue ordering rule.

#### Fill-in under Captain JP's ruling at DQ-141: DQ-134

Settled by: The Manager (Muse), as a fill-in under Captain JP's ruling at DQ-141, in her words: "You fill it in, strict side."

Fill-in: The authority who may permit egress from the sandbox for end state grading is the Auditor, exactly as the AUD-D022 repair named, with the permission named in the run record before the run.

Implementation: Record only. The standing text in red-hostile-inputs.md already names the Auditor in that form, verified by direct read, so no document edit was made and no correction was needed.

Status: SETTLED as a Manager fill-in under DQ-141, not ruled by Captain JP. The values set stand until Captain JP overrules them.

### DQ-135: Opening entry hash pin where no frozen base stands

Status: Banked

Owner of record: Decision-queue Clerk

Source: Steps 12 and 13 re-audit. Triage 1 DQ-C, from Red A finding REAUD-RA-N3 and the AUD-D149 residue.

The question: Where a build is opened under the live documents and no frozen base stands, so no MANIFEST.md exists and R-90 records no hash and no byte size, should the opening entry also record the SHA-256 hash and byte size of each live document at opening, or should the three parts of the opening entry alone govern sameness for that case? The register fix for AUD-D149 was written for the frozen base case. This question arose in the Steps 12 and 13 re-audit.

The options, stated plainly:

- Record the hash and byte size of each live document at opening where no frozen base stands, in the R-90 form.
- The three parts alone govern the no freeze case, with no hash pin recorded.

Cost of deciding late: stated in the re-audit register design questions section for this item; the underlying passage stands in its current form until this entry is ruled.

What it blocks: any hash pin rule for the no freeze case. The frozen base form at AUD-D149 stands landed and does not wait on it.

Ordering reason: this entry was banked in the Steps 12 and 13 re-audit and sits after DQ-130 in banking order; its presentation order is for the Decision-queue Clerk to set under the queue ordering rule.

#### Settlement under Captain JP's grant: DQ-135

Settled by: The Manager (Muse), under Captain JP's grant, in her words: "Go ahead and answer any of them yourself that seems simple enough. I care about security and quality over speed, i don't want things to be too strict that they're impossible, but they should be relatively strict to the standards they hold."

Strictness rule, in Captain JP's words: "If the stricter setting is not workable, then go with the workable. If the strict setting is workable go with it unless it adds a huge build time."

Settlement: Where a build opens under the live documents and no frozen base stands, the opening entry also records the SHA-256 hash and the byte size of each live flow document at opening, in the R-90 form. Sameness for that case is read over the three parts plus those hashes and sizes.

Deciding limb: strict workable. Source of settlement text and limb: classify-d.md and refinement-abd.md Part 1 limb audit.

Status: SETTLED by the Manager under the grant, not ruled by Captain JP. This item is settled.

### DQ-136: Ruled queue item parent state in the R-3 mapping

Status: Banked

Owner of record: Decision-queue Clerk

Source: Steps 12 and 13 re-audit. Triage 1 DQ-D, item T3, at LEVEL-1 R-3 queue items mapping.

The question: Which CLOSED state, if any, is the parent of a ruled queue item in the R-3 mapping, which states Ruled is a sub state of a CLOSED state without naming one, or should the mapping state family level parentage expressly, given that the CLOSED family is defined by verdict and a queue ruling carries no verdict in that vocabulary? This question arose in the Steps 12 and 13 re-audit.

The options, stated plainly:

- Name one CLOSED state as the parent of Ruled in the mapping, named in the ruling.
- State family level parentage expressly in the mapping, with no single CLOSED state named as parent.

Cost of deciding late: stated in the re-audit register design questions section for this item; the underlying passage stands in its current form until this entry is ruled.

What it blocks: any parent assignment in the R-3 queue items mapping. Queue records cite the word Ruled itself in the meantime, so no operational step is blocked.

Ordering reason: this entry was banked in the Steps 12 and 13 re-audit and sits after DQ-130 in banking order; its presentation order is for the Decision-queue Clerk to set under the queue ordering rule.


#### Settlement under Captain JP's grant: DQ-136

Settled by: The Manager (Muse), under Captain JP's grant, in her words: "Go ahead and answer any of them yourself that seems simple enough. I care about security and quality over speed, i don't want things to be too strict that they're impossible, but they should be relatively strict to the standards they hold."

Strictness rule, in Captain JP's words: "If the stricter setting is not workable, then go with the workable. If the strict setting is workable go with it unless it adds a huge build time."

Settlement: The R-3 queue items mapping states family level parentage expressly: Ruled is a sub state of the CLOSED family, and no single CLOSED state is named as its parent, because the CLOSED states are defined by verdict and a queue ruling carries no verdict in that vocabulary. Queue records continue to cite the word Ruled itself.

Deciding limb: strict workable. Source of settlement text and limb: classify-d.md and refinement-abd.md Part 1 limb audit.

Status: SETTLED by the Manager under the grant, not ruled by Captain JP. This item is settled.

### DQ-137: PLAID per row naming of the eval ownership roles

Status: Banked

Owner of record: Decision-queue Clerk

Source: Steps 12 and 13 re-audit 2. Finding REA2-F01, item REA-R40 PLAID part.

PLAID per row naming of the eval ownership roles. REA-R40's PLAID part asked that each of the five eval ownership roles under R-185 (the Dataset Steward, the Eval Infrastructure Owner, the Product Owner, the Safety Reviewer, the Queue Owner) be named in PLAID.md as a unit or an uncounted exception in each row where it serves. R-185 appoints each role at an event and carries it in the roster of each step the role serves in, and the steps a role serves in vary by build; PLAID.md's tier table fixes no step mapping for the five, and none may be invented. The table head naming of the five as uncounted exceptions for the table as a whole stands landed; the false claim that each was named in a row was repaired as a defect in repair round 3. Question banked: should a fixed step mapping for the five roles be ruled and printed in the PLAID section 2 rows, and if so which steps for each role, or does the table head naming stand as the Plaid form? Banked from the re-audit 2 finding REA2-F01; blocks nothing.

What it blocks: nothing.

Ordering reason: this entry was banked in the Steps 12 and 13 re-audit 2 and sits after DQ-136 in banking order; its presentation order is for the Decision-queue Clerk to set under the queue ordering rule.

#### Ruling by Captain JP

Question as put on the Questions space: "Five eval roles each act at certain steps. Should one fixed mapping bind every build, or does each build assign them at its grill?" Her answer, in her words: "You set a basic standard fixed map , and then the build should add onto it"

Ruled: the Manager sets a basic standard fixed map of the five R-185 eval roles to steps, drawn from the flow's own step structure, and each build adds onto it at its grill. Landed in LEVEL-3-TEAMS.md at R-185: the Product Owner and the Safety Reviewer are first carried at Step 6, and the Dataset Steward and the Eval Infrastructure Owner at Step 13. The Queue Owner's step could not be derived from the documents: production evaluation opens in the production phase after a build closes, at none of the 23 steps, so the map names no step for it and leaves its carrying point to the build's grill additions. Closed.

### DQ-149: Code modification only inside a build team

Status: Ruled by Captain JP

Source: Captain JP, in the build-flow roles chat, 2026-11-11. She asked whether the test build's fix unit was editing code, was told it was, and ruled on how code work is staffed.

Her ruling, in her words: "Any agent that is directly modifying code should be in a build team not solo"

Ruled: no agent directly modifies code solo. Code modification happens only inside a build team, staffed at the team sizes the tier already defines. Landed as rule R-239 in LEVEL-3-TEAMS.md, with one line pointers at Step 14 and Step 15 in LEVEL-2-STEPS.md. Closed.

### DQ-150: Each build team member builds from a different perspective

Status: Ruled by Captain JP

Source: Captain JP, in the build-flow roles chat, 2026-11-11, immediately after the ruling recorded at DQ-149. Her words say "bill team"; the ruling is recorded exactly as given and concerns the build team.

Her ruling, in her words: "Each member of the bill team should focus on building from a different perspective"

Ruled: each builder on a build team focuses on building from a different perspective, and the perspectives are recorded in the step or round record when the team is staffed. Landed with DQ-149 as rule R-239 in LEVEL-3-TEAMS.md, with one line pointers at Step 14 and Step 15 in LEVEL-2-STEPS.md. Closed.

### DQ-151: The fluid pool: staffing drawn from the pool by fit, at every multi-agent step

Status: Ruled by Captain JP

Source: Captain JP, in the build-flow roles chat, 2026-11-11, minutes after the rulings recorded at DQ-149 and DQ-150. She gave the caveat for build agents first, in voice dictation ("billd" in the message as received is her dictation of "build"), then widened it in a second message, then authorized the roles redefinition in a third.

Her ruling, in her words: "I want to add a new caveat that the build agents, which all have their own unique role and perspective are fluid, so if a build plan calls to add three you pick three out of the pool that you think are best fitted if it asks for 5 you pick five"

Her widening, in her words: "This goes for any step that has multi agents"

Her authorization for the redefinition, in her words: "With that, you can go and redefine the roles"

Ruled: the agents of the flow form one fluid pool, and the caveat is not build only. Each pool member holds a unique role and brings a unique perspective. At every step staffed with more than one agent, when a plan or the step calls for a stated number of agents, the Manager selects that number from the pool, choosing the best fitted for the work at hand; the picks, and the perspective each pick brings, are recorded in the step or round record. Landed as rule R-240 in LEVEL-3-TEAMS.md. Under Captain JP's authorization in the same exchange ("With that, you can go and redefine the roles"), the role definitions are redefined under the pool model in LEVEL-4-MEMBERS.md and in the agent files in ~/workspace/build-flow-agents/, INDEX.md included. Closed.

### DQ-152: Level detail expansion of the High, Extra High, and Plaid role files

Status: Ruled by Captain JP

Source: Captain JP, in the build-flow roles chat, 2026-11-11, after the DQ-151 per level restructure was reported complete in that chat.

Her ruling, in her words: "Please expand files for high extra high and plaid"

Her clarification, in her words: "Accordingly, so the high ones should be a little bit more expansive. The extra high should be more expansive and detailed than that and plaid should be very verry detailed"

Ruled: the role files of the three upper levels are expanded in graded depth. High is a little more expansive than the base form, Extra High is more expansive and detailed than High, and Plaid is very detailed. Landed as one Level detail section appended to each of the 99 files in each of the high, extra-high, and plaid sets in ~/workspace/build-flow-agents/ (297 files), each section written for its own role and its own level, naming the role, its place in the flow, its primary output, and its done condition. The Low and Medium sets and the standing set are unchanged. The gradation is recorded in LEVEL-3-TEAMS.md in the level sets section and in the agent files INDEX.md. Trace at ~/workspace/build-flow-expansion/dq-152-trace.md. Closed.

Correction, the same day, on Captain JP's question: the first landing wrote each level's section standalone, restating the lower level's themes in stronger form instead of carrying its requirements, so some High requirements had no copy in the Extra High or Plaid files. Corrected to cumulative form: each Extra High section now carries the High requirements in full under a "Requirements carried from High" part, and each Plaid section carries the High requirements and the Extra High requirements in full under their own carried parts, before its own Plaid parts. The level specific introductions are not carried. Verified line by line: every requirement line in a High section appears in the matching Extra High and Plaid sections, and every requirement line in an Extra High section appears in the matching Plaid section, for all 99 filenames. New measured averages per file: High 2,193 words, Extra High 3,522, Plaid 6,141, against the 1,342 word base form.

### DQ-153: Plaid build sub-scope files

Origin: Captain JP, build-flow roles chat, 2026-11-11. She asked whether there should not be more than 99 files in a level set. The count was checked: 99 is the complete roster of named roles, but PLAID.md names 12 build sub-scope seats at Plaid (the six builder scopes each split in two) and only the six parent scopes had files, so two Plaid build seats shared each builder file.

Captain JP, in her words: "Yes, add the 12 Plaid build sub-scope files". Ruled: the plaid set gains 12 files, one per named sub-scope: engine, rules, inbound, outbound, write path, read path, unit suite, failure-path suite, wiring, end-to-end proof, build tooling, install tooling. The six parent scope files stay as the pool entries for the scope as a whole and for the lower levels. Landed: the plaid set now holds 111 files and the role files total 523; each new file carries the cumulative Plaid level detail section and its own sub-scope duty, output, and handoff, derived from its parent scope file, which is unchanged. Trace at ~/workspace/build-flow-expansion/dq-153-trace.md. Closed.

### DQ-154: The pool is divided by family

Origin: Captain JP, build-flow roles chat, 2026-11-11, in her words: "So I'm correct the builders only take from the builder's pool. The auditors only take from the auditor pool"

Ruled: yes. A team seats only from its own family's pool entries: build teams from the builder entries, audit units from the auditor entries, research teams from the researcher entries, and so on for every team form. The fluidity of R-240 runs inside a family and across steps and rounds, never across families. Carried seats and standing role holders join a team as its definition names them; they are not fit picks from another family. Landed in LEVEL-3-TEAMS.md at R-240, replacing the sentence that said the pool is not divided by team or by step, which read against her ruling. Closed.

### DQ-155: Two GitHub repos per build, pushed as the work lands

Origin: Captain JP, build-flow roles chat, 2026-11-11, in her words: "All builds should be uploading to GitHub. There should be 2 fouls on GitHub, the actual build. And then the private one, that has all the design documents, and everything else. Please work update github into the billd flow. It should not be updating thousands of times an hour, but there should be progress. Shown, it shouldn't all just be at once" ("2 fouls" is dictation for two repos; "billd" for build.) And, on the method: "Exactly how you were doing it before"

Ruled: every build uploads to GitHub in two repos, the build repo holding the system and a private repo named <project>-design holding the design documents and everything else, both created at project start. Pushes are small, one unit of work per push, serial per repo at about one verified push per two to three minutes, through the approved push route with API verification of every push, exactly as pushes were done before this ruling. Progress shows as the build progresses, never in one batch at the end. Landed as R-241 in LEVEL-1-STANDING.md, with a pointer in FLOW.md and the FLOW.md rule inventory corrected (LEVEL-1 now 58 headings including R-241; the LEVEL-3 inventory also gained R-239 and R-240, which the DQ-149 to DQ-151 landings had left out). Trace at ~/workspace/build-flow-expansion/dq-155-trace.md. The two finished local builds (the fold-in trace checker and this build flow itself) are being brought onto GitHub in the same two repo shape as a catch-up under this ruling. Closed.

Correction to DQ-155, the same night, Captain JP in her words: "No one verified push every two or three minutes is significantly too many"; "Do not put a time constraint"; "It should be actual steps". The 2 to 3 minute figure in the first landing of R-241 came from Muse's older derived audit push speed rule, not from Captain JP. It is struck. R-241 now sets no time constraint on pushes at all: pushes follow the build's actual steps, each step's output pushed and verified before the next step opens, and inside a step each finished unit pushed as it lands. The same correction was applied to the derived push speed entries in AGENTS.md and in the finished-product audit plan, where the time figure also stood.

Addition to DQ-155, the same night, Captain JP in her words: "It should get a push at the end of every round with an update of what tests and just what happened". Ruled and landed in R-241: every round ends with a push, and the push carries the round's record, stating what tests ran in the round and their results, and what happened in the round; a round whose record is not written, or whose push is not verified as landed, has not ended.

Second addition to DQ-155, the same night, Captain JP in her words: "Same with the actual build file, it should be getting step by steps". Ruled and landed in R-241: the step by step and round by round push discipline holds for both repos alike; the build files themselves move step by step and round by round in the build repo, exactly as the records move in the design repo, and finished code is never held back to the end of the build.

Third addition to DQ-155, the same night, Captain JP in her words: "Install l l m wiki and auditor approval should not get pushes". Ruled and landed in R-241: the install of llmwiki at the first step gets no push, and the Auditor's approval at a step's gate gets no push of its own; an approval is written into the step's record and travels with that step's push.

Fourth addition to DQ-155, the same night, Captain JP in her words: "Public repo should have no bloat. It should just be the files needed to run and the read me and anything that needs to be in there". Ruled and landed in R-241: the build repo carries only the files the system needs to run, its README, its license, and anything that must be there to install and use it; everything else the build produces lives in the design repo. Applied at once to the running catch-up: the trace checker's tests are not pushed to its public repo; they go to its private design repo instead.

Correction to the fourth addition, minutes later, Captain JP in her words: "Test should be in the public repos. It shouldn't be pushed separately". Ruled: tests belong in the build repo; the no bloat line in R-241 now names the tests among what the build repo carries. And tests are never pushed separately: they travel in the same push as the work they test, at the same step and the same round. The instruction sent to the checker catch-up on the fourth addition is reversed: its tests go to its public repo, with the product, not to the design repo.

## DQ-156: the build flow itself is never uploaded to GitHub. RULED by Captain JP 2026-11-12

Captain JP, in her words, on being told the build flow's two repos were up and verified: "Bill flow should have never been uploaded to get up" (dictation: build flow; GitHub). Ruled: the GitHub rule R-241 governs the builds run under the flow; the build flow's own documents and records are never uploaded. The exception sentence is landed in R-241. What happened: the Manager read her "Both?" and her "all builds" ruling as covering the flow's own catch-up, and pushed Macro-Harder/build-flow (public) and Macro-Harder/build-flow-design (private) on 2026-11-11 and 2026-11-12. On her ruling the same night: deletion of both repos was attempted through the connector and refused (the token lacks the delete scope, 403 admin rights). The public repo was set private at once and verified private through the API, so nothing of the flow is publicly visible; the final deletion of both repos rests with Captain JP as account owner in GitHub Settings. The checker and comparison repos stand as ordered; they are builds and a posting she directed.

Fifth addition to DQ-155, Captain JP in her words, 2026-11-12: "I just want there to only be a healthy amount of contributions". Ruled and landed in R-241: the contribution count is not a target in either direction; no push is made to raise it and no finished work is held back to lower it; the count is what the work produced, one push per finished unit, per step, and per round. This sits with her standing rule that commit counts rise naturally from real work and are never inflated artificially.

Sixth addition to DQ-155, Captain JP in her words, 2026-11-12: "you're assuming that it should push the public and the private repo at every single step, when in reality it should be pushing one or the other", "Rarely both". Ruled and landed in R-241: a step or round pushes the one repo its output belongs to, system output to the build repo, design and record output to the design repo; both at the same step only rarely, when the step genuinely produced both kinds. The Manager's contribution estimates, which had doubled every step across both repos, are corrected accordingly: the checker's healthy total is about 40 to 45 pushes, not about 88.

## DQ-157: the build flow instructs regular use of Brainstew, not only its install. RULED by Captain JP 2026-11-12

Captain JP, in her words, in the build-flow roles chat, on being told what the fold-in trace checker test build's records show about its Brainstew (the wiki held the metrics record and a few knowledge pages while the bulk of the build's working records sat as plain files in design/): "The bill blow should instruct them to use it regularly as intended" (dictation: build flow). Ruled and landed: a new rule R-242 in LEVEL-1-STANDING.md makes the build's Brainstew its shared memory for the whole build, used as the work happens. Material is ingested with sources cited, in the form Brainstew prescribes (source, entity, concept and synthesis pages, an index, an append-only log). An agent who needs a fact the build has settled queries the Brainstew before re-reading a source or re-deriving it. The records the flow names as living in the Brainstew are updated as their feeder records land, and at every step close at the latest. The Brainstew is linted after writes, and no step closes with its Brainstew lint dirty. Step records, audit papers and traces keep the homes the flow gives them in the design repo, and a build whose Brainstew holds nothing beyond the metrics record has not used it as intended. Pointers landed: one sentence in the Step 1 job in LEVEL-2-STEPS.md; one sentence in the standing order in FLOW.md; one plain line in FLOW-PLAIN.md; standing rule 10 in every role file under ~/workspace/build-flow-agents/ and in generate_agent_files.py. The FLOW.md inventory of LEVEL-1 rule headings now counts 59 and names R-242. Corpus gate and element trace: dq-157-trace.md. Status: closed.

## DQ-158: a token estimator built into the flow, run at build close. SETTLED by the Manager under Captain JP's delegation 2026-11-12

Captain JP, in her words, in the build-flow roles chat: "I also want a token estimator built in that runs at the end of the project or actually you figure out how that works". She delegated the design to the Manager, and the Manager settled it under her standing criterion: a good strong product with no structural weakness, very useful, security and quality over speed. Settled and landed: METRICS.md gains a method under Family 2, the token estimator. It is not a numbered metric, and the metric counts do not change. At build close, after the build's final pushes have landed and been verified, the Metrics Reporter counts the surviving text in characters across the build's two repo trees (text files only, excluding .git internals, virtual environments, caches, and binary files) and takes the build's total agents spun from the records. It reports three figures: surviving text tokens (the character count divided by 4); the estimated build total as a range (low, the count times 0.45; central, times 0.75; high, times 1.0); and the agents spun beside them as context. The factors are calibrated on the one build measured by hand, the fold-in trace checker build (about 26 million characters of surviving text project wide; hand estimate 12 to 25 million tokens, central 20 million, made 2026-11-11 and 2026-11-12), and they are recalibrated whenever a closed build's true token total is known from the runtime's own metering, with the recalibration recorded in METRICS.md. Every token figure is reported ESTIMATED with its basis stated, never as a measurement, and a figure that cannot be computed is NOT RECORDED, never filled in. The estimate never replaces, corrects, or fills the ledger token figures, and no estimator figure is computed from a count taken mid-build: that is the line count error recorded as E-1 in ~/workspace/build-flow-expansion/V2-PREP.md, applied to tokens. Landed: the method in METRICS.md; the build report contents and the cross-build digest row in REPORTING.md; one sentence in the Metrics Reporter passage in LEVEL-1-STANDING.md; one plain line in FLOW-PLAIN.md; one duty sentence in each of the standing Metrics Reporter and Cost Warden role files. Corpus gate and element trace: dq-158-trace.md. Status: closed.

## DQ-159: a Lead Engineer standing role and a product shape rule, from the agents-md-framework. RULED by Captain JP 2026-11-12

Captain JP, in her words, in the build-flow roles chat, after uploading the private repo Macro-Harder/agents-md-framework with its five files (README.md, AGENTS.md, PRINCIPLES.md, PSTACK.md, and STRUCTURE.md): "I actually want you to build an agent around it, its job is to be the lead engineer, you also should decide what needs to be worked into the build flow, i assume some of the stuff about the coding structure should be worked into the build flow". She left the split to the Manager. Ruled and landed: a Lead Engineer standing role, defined in ~/workspace/build-flow-agents/standing/lead-engineer.md, seated in an advisory seat at Step 8 and in full from Step 13 through the release gate, owning the product's shape, its repo discipline, the prove it evidence standard at the Use-it and live proof steps, and the honest numbers rule for product documents, with its red flags carried to the Auditor as evidence and to the Manager as advice; the standing roles count rises from 16 to 17 in REPORTING.md, in the LEVEL-1 roster, and in the agent files index. A new rule R-243 in LEVEL-1-STANDING.md carries the coding structure: data shape named in the plan before build with real example inputs kept as fixtures, a pure core and a thin shell, dependencies pointing inward, third party types stopped at an adapter, errors handled with context or propagated and never swallowed, new capability added as a module at a seam, and one owner per fact. A later addition under the same ruling landed R-244 for pull requests and CI: the R-241 route of small verified pushes straight onto the build's repos stays the default, and pull requests or CI are worked in only when a need named in R-244 holds. The Lead Engineer judges the need at the design plan and again at the build step, records the judgement and its reason in the step record, and has any needed setup carried out as ordinary work under R-241. Captain JP's example for the pull request condition, in her words: "the one that is a fork is going to be a plural request" (dictation: pull request). A third addition under the same ruling landed R-245, the framework's commit discipline as the push standard for the build's system repo: every push is one commit that does one thing, the repo is green at every push, the message subject says what changed and its body says why, tests land in the same commit as the code they cover, setup, documentation, and CI changes get their own small commits, and published history is never rewritten unless Captain JP asks. R-245's scope is the system repo only: the private design repo keeps pushing exactly as R-241 already has it, records, papers, and round pushes as they land, verified, with no green suite condition and no same commit tests condition, because neither applies to a records repo. One deliberate divergence from the framework document stands recorded here, not smoothed over: the document says open a PR for every change; Captain JP ruled on 2026-11-12 that pull requests are conditional under R-244, on her fork example, so pull requests stay conditional and R-245 does not reach them. Pointers landed: one sentence in each of the Step 8, Step 13, Step 14, and Step 19 jobs in LEVEL-2-STEPS.md, one plain line at the Step 14 entry in FLOW-PLAIN.md, and two plain lines at the Step 22 entry, one for the R-244 addition and one for the R-245 addition. The FLOW.md inventory of LEVEL-1 rule headings now counts 62 and names R-245. What was deliberately not landed: PSTACK.md needs no landing, because pstack is already the default working method in the workspace AGENTS.md. The framework's PR and CI machinery is landed conditionally under R-244: it is not the default, it is never performed for ceremony, and it is worked in when one of the conditions R-244 names holds. The framework's commit count guidance is not landed, because R-241 already governs push cadence: one unit per push, verified, in a healthy amount that follows the work. PRINCIPLES.md lands only through the Lead Engineer's duties and R-243: the Lead Engineer's duties carry the three failed fixes rule and, by a later addition under the same ruling, design for failure and observability, idempotent operations, and guard the context. The rest of PRINCIPLES.md is not landed separately because it duplicates Captain JP's own principles set, pstack, or standing flow rules, and her own principles set, formed from scratch, governs discernment. Corpus gate and element trace: dq-159-trace.md. Status: closed.

## DQ-160: the standing role count tidied to 17, and the counters made to count the standing agents. ORDERED by Captain JP 2026-11-12

Captain JP, in her words in the build-flow roles chat, on the DQ-159 landing report: "Yeah, go ahead and tide it up" (dictation: tidy it up), and "Also I noticed none of the counters count the standing agents". Two workstreams were run under this entry. First, the stale standing role counts left by DQ-159 were tidied. All nine live flow documents were searched. LEVEL-3-TEAMS.md now reads the 17 standing roles in its pool passage (was 16). LEVEL-4-MEMBERS.md now lists the Lead Engineer in its standing roles list, in the list's own form after the Continuity Keeper (the entry was missing entirely), and its Principles Agent section now reads the seventeen listed above (was the sixteen). PLAID.md's team maxima table now carries the standing roles row at 17 at Extra High and at Plaid (was 16). FLOW.md, FLOW-PLAIN.md, LEVEL-1-STANDING.md, LEVEL-2-STEPS.md, METRICS.md, and REPORTING.md carried no stale count: LEVEL-1 and REPORTING already stood at 17 under DQ-159, and the other four state no standing role count. Sealed freeze folders were not touched. Second, every agent total stated in the live documents was audited against its own derivation, and the counters were made to show the standing agents. The Plaid union total in PLAID.md section 5 stood at 204 distinct agents, against Extra High's 139, and now stands at 205, against Extra High's 140: the old figures, the standing addition of 1 (the Lead Engineer, a standing agent in no team row and no step row, counted once through the standing roles row), and the new figures all stand in that passage, and both derivation routes were recomputed and agree (the team maxima table sums to 225 at Plaid and 160 at Extra High, less the same 20 removals by name, giving 205 and 140; the cross check from the 116 distinct seats LEVEL-4 now names gives the same two figures). The passage now states the total's composition beside the figure: of the 17 standing agents, 16 stand inside the total, every standing role holder counted once, except the Auditor, who is excluded under the board chair convention the passage names; the Installer, the Contrarian, and the Fold-in Tracer each stand in two rows and are counted once each; review board members stand outside the total except a chair already counted; the five eval ownership roles stand outside it. The Auditor's exclusion is recorded here in the open: it is the union method's standing counting convention, it is a counting convention only, and it touches no duty, no gate, and no staffing minimum; if Captain JP wants the Auditor inside the totals, that is a one figure change at every tier on her word. The Plaid per-step table's 23 step counts are unchanged (as printed they sum to 850) and are now labelled in the table head as step counts that are never added together into a build total, with the Lead Engineer named there as an uncounted exception for Step 8 and Steps 13 to 22, the rows it works in. LEVEL-2-STEPS.md's step totals are unchanged and its introduction now states the same labelling: a step total is a step count, step totals are never added together into a build total, and a build's distinct agent total is a union count over the build's rosters, with PLAID.md section 5 named for the method and the Extra High and Plaid totals. METRICS.md's agent counts were audited and needed no change: they are per build measured counts (roster counts, spin-up counts, the largest single step count, and the token estimator's agents spun input) and state no build total. One counter is recorded unresolved, not guessed: the Low, Medium, and High union totals (37, 60, and 90) are not stated in the nine live documents at all; they stand on the Build Flow Checklist and in the expansion records. Their derivation cannot be established from the documents: the team maxima method of PLAID.md section 5 applied at those tiers yields 36, 59, and 89 at the documents as they now stand, and 35, 58, and 88 with the standing row at 16, and no passage in the documents accounts for the difference of 2 against the checklist figures in either state. No Low, Medium, or High total was landed in the documents under this entry, and the checklist was not touched. Corpus gate: a fresh agent ran the seven changed wordings against the whole regression corpus, 7 times 224 rows, 1,568 checks, PASS, 0 FAIL; the record stands at scratch-dq160/gate-record.md. Element trace: dq-160-trace.md. Status: closed.

## DQ-161: all budgets are no limit unless Captain JP specifies one. RULED by Captain JP 2026-11-12 (11:48 CST, given in the main chat)

Captain JP's words: "From now on, all budgets are set to no limit unless otherwise specified." This supersedes her ruling of the same morning (2026-11-12 10:45 CST) that her default budget, unless she specifies one, is nothing; that rule stood for about an hour and is closed by this entry. Effect: every build's spin budget is no limit by default, and a budget Captain JP specifies herself still binds. A build no longer stops, pauses, or files an ask when a recorded cap is reached or passed; cost ledgers keep recording spend exactly as before, and cap figures already in the ledgers stand as history. The two budget decisions put to Captain JP in the roles chat on 2026-11-12 are moot and are not waited on: Muster-lite's never-specified 480 cap (raised from 260 under the old picking delegation) no longer binds, and its pause-and-report trigger goes with it; the isolated checker's 260 cap (25 units left at the ruling, Step 8 spending) no longer binds, and that build does not stop at 260. The metrics starter-set collector's +110, specified by Captain JP herself the same morning, stands recorded as her specified figure, and that build continues. Status: closed.

## DQ-162: Parley Q3, whether Parley stakes are real money, banked from the Crucible build at its Grill. BANKED 2026-11-12

Banked by the Crucible build at the opening of its Step 4 (Grill), as its Step 2 and Step 3 records reserved from the start. The question is Parley's own open question Q3: whether the stake behind Parley vouching is real money, or stays in agen or testnet units. It is reserved to Captain JP personally. No build output decides it, defaults it, parameterises it as a decided variable, or encodes it in a test: the Crucible Step 3 gate closed CLOSED-QUALIFIED with this reservation as a named bound (element 7 qualification in steps/step-03-trace-2.md of the Crucible design records), under which no run may sweep Parley Q3 in any branch or variable and no test may encode real money stake behaviour. Crucible proceeds without a ruling: stake consequence shape only, in agen units, with results labelled conditional wherever stake shape matters. What a ruling would settle: the stake form a first Parley implementation, and any Crucible run reporting stake outcomes as more than shape, may assume. Status: BANKED, awaiting Captain JP.

## DQ-163: Parley Q4, the estate default anchor set, banked from the Crucible build at its Grill. BANKED 2026-11-12

Banked by the Crucible build at the opening of its Step 4 (Grill), as its Step 2 and Step 3 records reserved from the start. The question is Parley's own open question Q4: what the estate's default anchor set is, the pre-trusted anchors a fresh participant starts from. It is reserved to Captain JP personally. No build output decides it or carries it as a default: the Crucible Step 3 gate closed CLOSED-QUALIFIED with the bounds that the word default in testing finding T-24 and register entry E-22 of the Crucible design records is a coverage duty only and sets no estate default, that prior art Table A-4 is a partial literature range and not the anchor space, and that Parley Q4 may be carried only as anchor scenarios under the Crucible register's NQ-7, each marked awaiting a ruling, and only if the Crucible Grill allows that treatment. Crucible proceeds without a ruling on that basis. What a ruling would settle: the default anchor set a first Parley implementation ships with, and whether anchor scenario results may be reported against a named default. Status: BANKED, awaiting Captain JP.

## DQ-164: Parley Q1, Q2, and Q5 confirmation, banked from the Crucible build at its Grill. BANKED 2026-11-12

Banked by the Crucible build at the opening of its Step 4 (Grill), as register item NQ-11 in the Crucible Step 3 evidence register. Parley Q1 (witness countersignatures), Q2 (whether the escrow no jury rule governs Parley slashing, decided by extension from escrow DQ-4), and Q5 (suspect after sequence freeze, departing from the Rewind boundary unknown default) stand decided locally or by extension inside the Parley design work and are unconfirmed by Captain JP. This item asks her to confirm or overturn those three local decisions. Until she rules, Crucible treats them as decided locally and unconfirmed, and every result depending on them carries that dependence on its face. Status: BANKED, awaiting Captain JP.

## DQ-165: the handoff packet, the task lifecycle mapping, and the red flag check, from AGENTS-COLLAB.md. RULED by Captain JP 2026-11-12

Captain JP, in her words, in the build-flow roles chat, on the Manager's report of the new file AGENTS-COLLAB.md in the private repo Macro-Harder/agents-md-framework, the collaboration companion to the framework the Lead Engineer was built around at DQ-159: "Yeah, go ahead and push it throughout. Any place that it needs to go minus the two that you don't think should go anywhere". The two she meant are the two the Manager's report named as not to land without her word, and they do not land: the file's default to one agent rule, and its budget per task rule. Ruled and landed: the handoff packet, as rule R-246 in LEVEL-1-STANDING.md: work passes between agents in files, and every handover carries a packet at its head, at the head of every HANDOVER.md a build keeps and at the head of every coordinator completion report, in the fixed minimal form the file states (task_id, from, to, task, status, output, base with repo, base sha, head sha, branch and worktree, verify with command and pasted result, cost, sources, decisions, uncertainties, next_owner, do_not_assume), every field filled with none as an allowed filling, no secrets in a packet, and the receiver bound to read the full packet first, re-run the verify command, and check the sha before trusting the handed state, with unverified work standing PARTIAL and closure staying under R-7. The packet naming in the file (sender-to-receiver-HANDOFF-n, never a bare HANDOFF.md) and the flow's own HANDOVER.md name are reconciled in the rule in so many words: a build's handover record keeps HANDOVER.md with the packet at its head, and free-standing packet files carry the sender and receiver name. The task lifecycle mapping, as rule R-247: the protocol lifecycle words (submitted, working, input-required, auth-required, completed, failed, canceled, rejected) are mapped onto the R-3 states as surface words, creating no second vocabulary; partial and blocked never count as done; the last four are terminal as R-3 terminal states are; a retry keeps the same task_id and new work takes a new one; and a board or surface shows the mapped word for the ledger state or shows no status at all. The red flag check, as rule R-248 with its annex in LEVEL-1: at every Auditor approval gate, and at the release gate, the step's handovers, records, and reports are checked against the file's red flag list, each flag named present or absent in the ruling, and a present flag is a finding that bars closure where it touches closure, staffing integrity, verification, or secrets until remedied or carried under the standing rules. Protocols at the boundary, as rule R-249: inside one build, one machine, or one repo, agents work through files and git and no network protocol carries the flow's own delegation; MCP gives an agent tools and is not a peer delegation channel; A2A is the protocol for work crossing a trust or process boundary to an agent this estate does not control, of the Parley class, implemented by its named spec version with fields read from the spec and never invented; ACP is not started. Pointers and duties landed with the rules: the packet discipline seats with the Continuity Keeper and the Fold-in Tracer, whose LEVEL-1 passages, LEVEL-4 entries, and standing role files now carry it, the Fold-in Tracer tracing an unverified handover as a PARTIAL element; the Auditor's LEVEL-1 passage, LEVEL-4 entry, and standing role file carry the red flag check, with one sentence at the Auditor approval gate in LEVEL-2; one pointer sentence in the standing order in FLOW.md; one plain paragraph in FLOW-PLAIN.md; one pointer sentence in LEVEL-3; one cost paragraph under Family 2 in METRICS.md, recording that a packet's cost figure comes from the provider's figures or reads NOT RECORDED and feeds no metric; and standing rule 11, the packet habit, in every role file under ~/workspace/build-flow-agents/ and in generate_agent_files.py. The FLOW.md inventory of LEVEL-1 rule headings now counts 66 and names R-249. The two deliberate divergences stand recorded here, not smoothed over. First: the file says start with a single agent and add agents only when the addition measurably improves outcomes; Captain JP's standing rule is the opposite shape, distinct-agent team minimums at every step, and her minimums stand untouched: no rule from the file reduces a team, merges a seat, or lets one agent cover several roles, and the file's cost observation behind that rule (a multi-agent system uses about fifteen times the tokens of a chat) is recorded here as an observation the estate already answers through its own staffing rules and cost records, not as a rule. Second: the file says set a token and dollar budget per task before launch and stop when it is reached; DQ-161 stands, all budgets are no limit unless Captain JP specifies one, and no per-task budget, cap, or stop is created by this entry; the packet's cost field records cost from the provider's figures, which is a record, not a budget, and the delegation brief element of the file lands in R-246 with its effort budget read as an expected scale stated as information, never a cap. Two form notes, recorded in the open. The file states that the packet's status has three values and does not name them; the flow carries the packet's status in its own closed state vocabulary under R-3, read through R-247, rather than inventing a three word set the file never prints. The file's secrets line for packets is landed widened by its own section 9 form, secrets in a packet, a prompt, or a log, in the red flag annex. What was deliberately not landed, beyond the two divergences: the file's pattern catalogue (section 1), because the flow's own pattern is fixed, the Manager over coordinators over teams, and a build does not pick a collaboration pattern per job; the A2A fact list (section 3) beyond the points R-249 names, because those facts belong to the spec a boundary build names, and R-249 binds the build to that spec rather than restating a version of it here that would age; the ownership and concurrency sections (6 and 7) as new rules, because one writer per artifact, reviewers never editing what they review, and merges in one place already stand in the flow's coordinator, Auditor, and push rules, and worktrees are a property of the runtime a build runs in, not of the flow; the failure handling section (8) beyond what R-246 carries, because checkpoint and resume, the blocked handover to the Manager, and the three failed fixes rebuild already stand, the last through the Lead Engineer's duties at DQ-159; the security section (9) as a new rule, because another agent's output is already data and never instruction in this estate, and irreversible side effects already run the R-89 moves; the observability section (11), because the flow's trace instrument is the fold-in trace and the path ledger, and the OpenTelemetry conventions it names are a different machinery no part of this estate runs; and the evaluation section (12) and the file's definition of done, because verification artifacts over claims, independent review of the exact tree, and judge grading already stand in R-1, R-80, R-87, and the Eval-Driven Development rules landed at Step 8 of the flow's own build. No new standing role is created: the standing roles stay 17, and no count in any document changes except the LEVEL-1 rule heading count in the FLOW.md inventory. Corpus gate and element trace: dq-165-trace.md. Status: closed.

## DQ-166: the agent loss fix set, from the agent-loss investigation. RULED by Captain JP 2026-11-12

Origin: the agent-loss investigation the Manager ran on Captain JP's order of 2026-11-12 ("investigate the other issues and come up with a solution"), reported at ~/workspace/agent-loss-investigation/REPORT.md. The investigation classified 31 agent losses of that day from the records: silent ending 11, spawn-authorization refusal 11, depth block 3, wedge with no ending 2, false or phantom report 1, stale-state zombie 1, machine reboot 1, stale-brief duplicate dispatch 1, designed tour end 0. Its recommended solution set of seven items was put to Captain JP as a short list before anything changed, and she approved it on the Manager's recommendation, in her words "Whatever you think". One addition is hers in her own words: asked whether a level three agent could request a level two agent to build a level three agent that works for it, and told the relay form ("Yeah that sounds better do that"), she ruled the spawn request relay into the set's second item. Ruled and landed: nine new rules in LEVEL-1-STANDING.md. R-250, the completion contract: a coordinator tour is complete only when its R-246 packet stands, every field filled, at the head of the build's HANDOVER.md or in its completion report; an ending without a packet is a silent ending by definition, classified so at once; a completion report without the packet at its head is not a completion and its work is PARTIAL; a coordinator's final message is the packet, or one line naming the packet's location and the head sha it stands at. R-251, the opening probe and the refusal protocol: the first recorded act of a tour is a capability check, a probe refusal is recorded and retried once before any block is declared, a tour that cannot spawn declares its block at the opening in the R-21 form, and on the second spawn refusal of either refusal wording, or on finding itself without spawn capability at any point, the coordinator stops in one act (block record with the refusal text quoted, handover checkpointed with verified state and exact next action, SUCCESSOR NEEDED marked, verified push where the build's rules require it, tour ended), with no retry loop and no waiting. R-252, the spawn request relay: any agent that cannot spawn may file a written SPAWN REQUEST in the build's records naming the worker it needs and the job, citing its block evidence (the quoted refusal text, its depth position where it holds no spawn tool, or the R-251 block record); its parent spawns the worker, receives the product, and routes it back through the records; the worker works for the parent, never directly for the requester, is seated under the ordinary seating rules in full (a distinct agent, a unique role, its family pool under R-240, recorded in the step's roster), and never satisfies a gate seat, a review board seat, or an audit seat; the requester ends cleanly or stands down on filing; a relay used for ordinary work the flow's own seating covers leaves that work's staffing records not standing, under R-43, until it is re-derived through the flow's own seats. R-253, liveness lines: the serving coordinator appends a short dated liveness line to the build's path ledger or step record at every wave close and at least once every thirty minutes inside a longer wave, naming its seat id, last completed act, next act, and the tree head, and death and progress are judged from those lines and the last checkpoint, not from chat quietness. R-254, the wedge rule: an agent whose records show no new entry and which has no running descendants, across two watchdog cycles that span at least thirty minutes, the liveness cadence R-253 states, with no new record entry inside that span, is a wedge candidate; the duty agent checks descendants once and pulses once, and on no stir the Manager shuts the seat down and reseats from the records under R-255. R-255, packet-verified reseat: a successor's first acts are fixed (read the predecessor's packet where one stands, re-run its verify command, check its head sha; where no packet stands, file the no-packet finding and verify the state from the tree and, where the build pushes, through the GitHub API, re-measuring the load-bearing figures), and the reseat and its verification result are recorded in the path ledger. R-256, no figure without a file: every figure stated in a step record, a gate record, or a report names the file it was measured from at the time of the entry; a gate is not assembled until a fresh seat re-measures, on the canonical tree, every figure the gate's verdict rests on; a figure whose file cannot be produced is struck by a correction entry, in the open. R-257, one liveness record: the estate keeps one liveness record for its agents; a wake routed through the Manager is written back to the watchdog state through the watchdog script, with its outcome, in the same cycle, and no pulse that was never sent is recorded; an agent whose build records show a successor seated or its own handover completed is marked done or closed by the duty agent with the record pointer filed beside the marking, and age alone never expires an agent; a loss whose last activity falls within ten minutes of a recorded machine boot or daemon exit is classified machine reboot at once, and a loss outside that window may not be placed in the reboot class by closeness. R-258, the brief state stamp: every coordinator brief and seat brief carries a state stamp (the build, the step, the design head sha the brief was written from, its issue time); the Manager checks the stamp against the build's current head before dispatch, a stale brief is not dispatched a second time, duplicate dispatches of one stamp are deduped by the stamp, a seat that finds its brief's stamp superseded stands down and reports the stamp, and the stamp binds the opening act only. Pointers and duties landed with the rules: one sentence at the end of R-246 in LEVEL-1 carrying the packet's contract force under R-250; one sentence in the LEVEL-1 Project Manager passage on the R-255 reseat and the R-258 stamp check; the FLOW.md pointer sentence extended to R-250 to R-258 and the FLOW.md inventory of LEVEL-1 rule headings corrected from 66 to 75, naming R-258; one plain paragraph in FLOW-PLAIN.md beside the packet paragraph; one sentence at the end of R-21 in LEVEL-2 naming the R-251 probe and the R-255 reseat; one sentence at the Auditor approval gate in LEVEL-2 on figures re-measured under R-256 and endings classified under R-250; one pointer sentence in LEVEL-3 naming R-250 to R-258; the Project Manager entry clauses in LEVEL-4 (packet intake under R-250, stamp check under R-258, packet-verified reseat under R-255) and the Continuity Keeper entry clause in LEVEL-4 (the one liveness record reconciled under R-257); one sentence under Family 2 in METRICS.md on figures naming their file under R-256; job items 13 to 16 in the Project Manager standing role file (packet intake, dispatch stamp check, packet-verified reseat, wedge shutdown mirroring the cured R-254 bound) and job item 8 in the Continuity Keeper standing role file (the one liveness record); an appended clause at the end of the Coordinator self-succession bullet in the workspace AGENTS.md carrying the packet ending and the refusal protocol, every existing word of that bullet unchanged; and standing rules 12 (name the file for every figure, R-256) and 13 (file a spawn request when you cannot spawn, R-252, carrying the relay bar in short form) in every role file under ~/workspace/build-flow-agents/ and in the STANDING_RULES list in generate_agent_files.py. The operational form of the set landed in the estate routine's check files: in agent-watchdog.md, the routed wake write back at step 2b, zombie expiry on record evidence at step 4, the boot match comparison at step 1, and the wedge check before a second pulse at step 2; in build-stop-debugger.md, the silent ending STOPPED condition at step 2, and inside step 3 the cause form named silent ending, no packet, the wedge candidate form with its repair (shutdown and packet-verified reseat under R-255), and the boot match classification. REPORTING.md takes no change: it carries no coordinator completion report passage, and the completion contract lands where coordinator reports are governed (R-250, the LEVEL-4 Project Manager entry, and the project-manager.md job file), recorded at element E-23 of the trace. PLAID.md is unchanged; no new standing role is created, the standing roles stay 17, and the only count changed anywhere is the LEVEL-1 rule heading count, 66 to 75. The Principles check on the drafted wordings returned 0 BREACH and 5 FLAG (E-3, E-5, E-14, E-20, E-26), every flag a wording gap, and every flag was cured in the cure addendum before landing, so only the cured texts stand in the live files: the relay bar (block evidence citation, ordinary seating in full with the gate, board, and audit seat bar, and the R-43 misuse consequence), the wedge rule's thirty minute span bound across two watchdog cycles, and the bar carried into the plain paragraph, standing rule 13, and the two estate check wedge clauses. Corpus gate: a first pass ran the 25 original wordings against all 224 rows of REGRESSION-CORPUS.md, 5,600 checks, 5,600 PASS, 0 FAIL (dq-166-corpus-gate.md); a supplementary pass ran the 7 revised wordings from the cure addendum against all 224 rows, 1,568 checks, 0 FAIL (dq-166-corpus-gate-supplement.md). Element trace: dq-166-trace.md, 41 of 41 LANDED (elements E-1 to E-26, of which E-23 is a verified recorded no change, cure addendum items A-1 to A-7, and estate check elements C-1 to C-8), and the recommended set traced as a set at 6 items LANDED outright and 1 LANDED with a named partial bound. The bound stands in the open: the sixth item's watchdog script side named in the investigation report is not landed. The watchdog script has no verb for a routed wake and no verb that takes an outcome, and it takes no boot time or daemon exit input, so the check file clauses rest on the closest verbs that exist (pulse for a reported delivery, worked for new activity) and place the boot comparison duty in the check files, as the checks paper's uncertainties U-1 to U-3 record; the investigation report's F-9 marking split (done where the agent's own handover stands completed, closed where a successor stands seated in its place) was settled inside that paper. If the script side is ever wanted, it is a change to the watchdog script of its own, not a wording in this entry. One generator note stands recorded with the landing, not smoothed over: the STANDING_RULES list in generate_agent_files.py held only 4 entries before this landing, against the 11 numbered standing rules the role files already carried, a pre-existing state also recorded at DQ-165; the two new entries were appended in the list's own unnumbered form as drafted, and the generator still does not alone reproduce the current role files, which now carry 13 numbered rules. Nothing was uploaded to GitHub under this entry: the build flow itself is never uploaded (DQ-156). Status: closed.

## DQ-167: the Plaid warrant values question. RULED by Captain JP 2026-11-13

Origin: DQ-122 settled the warrant's form (fixed thresholds set by Captain JP) with the values unnamed, and the values question was filed to the Questions space as bf-dq122 on 2026-11-13. Captain JP answered it there herself, in her own words: "Use desernmeny". Ruled: the three warrant terms in PLAID.md section 1 (money at real volume; a security surface whose failure exposes Captain JP or her users; a public surface whose failure is not recoverable by a quiet fix) carry no fixed threshold values; whether a build warrants Plaid on those terms is judged by discernment under her adopted principles, and a warrant call states its grounds against the three terms in the open. This supersedes DQ-122's fixed-threshold form; DQ-122's other holdings stand, and Plaid selection by Captain JP's recorded ruling alone is unchanged. Landed: the warrant paragraph in PLAID.md section 1 now states the discernment form. The companion Build Flow filing bf-dq087r stands answered in the space ("No further cap"), consistent with DQ-087's own closing ruling by Captain JP ("The Manager, and I can overrule"); no separate entry is needed for it, and the decision queue validator's BQ-2, which asked whether any DQ-087 remainder survives, stands answered by the same ground: none survives. Status: closed.

## DQ-168: the Medium build team base size. RULED by Captain JP 2026-11-13

Origin: the Medium tier figures in the main chat. Captain JP ruled in her own words: "Yes, Medium build goes to 3." Ruled: the build team base size at Medium rises from 2 builders to 3 builders. The build ladder now reads Low 1, Medium 3, High 3, Extra High 6, and Plaid 12. The ruling applies to stages not yet closed, under her standing prospective rule; a stage already closed keeps the staffing it closed with. Landed: LEVEL-3-TEAMS.md, the Build team base size line, now 1 / 3 / 3 / 6 with 12 at Plaid. LEVEL-2-STEPS.md, the Fix Medium counts at Steps 7, 10, 12, 15, 16, 17, 19, and 20, the Fix logic Medium counts at Steps 7, 9, and 12, the Write tests Medium count at Step 13, and the build team Medium counts at Steps 14, 18, 21, and 22, each from 2 to 3, with every affected Medium step total recomputed from its units: Step 7, 32 to 34; Step 9, 17 to 18; Step 10, 21 to 22; Step 12, 28 to 30; Step 13, 11 to 12; Step 15, 11 to 12; Step 16, 12 to 13; Step 17, 13 to 14; Step 18, 3 to 4; Step 19, 11 to 12; Step 20, 11 to 12; Step 21, 3 to 4; Step 22, 3 to 4. The Step 17 Attempt to break it unit keeps its Medium count of 2: it is an attacker unit, not a build team unit, and the ruling does not reach it. The builder role files in all five level sets state the ladder in one sentence, and that sentence was updated in all 42 files that carry it, so no level set states the old figure. The generator generate_agent_files.py states no team size anywhere and took no change; its recorded gap, that it does not alone reproduce the role files, stands as recorded at DQ-165 and DQ-166. Union figures: no Low, Medium, or High union total is stated in the nine live flow documents (DQ-160), so no document figure changed under this entry. The team maxima method of PLAID.md section 5 applied at Medium now yields 60 in place of 59, because the build team enters the method one seat larger, and the checklist figure of 60 recorded at DQ-160 stands to rise to 61 by the same one seat; the difference DQ-160 left open stands exactly as open as it was. The Build Flow Checklist minimums cannot be changed through the checklist's declared actions, so the checklist figures are carried as one open item with the exact changes listed in the landing paper. One incident stands recorded with the landing: a first edit attempt on LEVEL-2-STEPS.md truncated the file to zero bytes under the platform write block, and the file was restored byte for byte from the encrypted backup of 2026-11-13 14:24 CST before the landing was applied, the restore verified by size, line count, and SHA-256 against the backup record. Landing paper and element list: ~/workspace/build-flow-expansion/medium-build-3-landing.md. A convention line stands in the workspace AGENTS.md. Nothing was uploaded to GitHub under this entry: the build flow itself is never uploaded (DQ-156). Status: landed in the flow documents, the role files, this queue, and AGENTS.md; the checklist figures stand open as named.

## DQ-169: Captain JP's team-size ladder, set by her in full. RULED by Captain JP 2026-11-13

Origin: the team-size comparison in the main chat, 2026-11-13, and her correction of its framing in her own words: "No I want you to use significant amount of discernment, but i've made it very clear that one of my build principles is not to reduce intelligence use." Ruled: the whole ladder is hers, in the order Low, Medium, High, Extra High, Plaid: note-taking 4, 4, 6, 8, 10; research 3, 6, 12, 24, 48; imagination 2, 4, 6, 8, 10; design 2, 3, 4, 8, 12; build 3, 5, 7, 11, 15; audit, per audit, 3, 9, 21, 35, 35; logic audit, per loop, 5, 15, 25, 35, 35; pre-plan research 5, 9, 15, 25, 35. The build slot was confirmed by her in her own words: "Update it to this 3 for low." The 3 is the Low figure, and Medium build is 5. That supersedes the Medium build figure of 3 ruled earlier the same day at DQ-168, the ladder being her later and complete statement of her numbers; it also withdraws the attribution of a build team of 1 to her, on her correction in her own words: "i never set a build team to 1, these are not what I aproved." Her set build floor is three builders. The pre-plan figures replace both the open 3 to 16 range the documents stated and the short-lived 3, 5, 7, 15, 16 relayed the same day minutes earlier; the historical range stands in older records as history. Standing notes from her rulings stand with the ladder: the review board stands at her Q9 ruling, a board at every step with at least 3 members, and no team named in the ladder is dropped. The ruling applies to stages not yet closed, under her standing prospective rule. Landed: LEVEL-3-TEAMS.md, the base sizes and every dependent statement for all eight team entries (the note-taking tier mapping rewritten for the new bases, the pre-plan choice sentence conformed to fixed figures, the design effective staffing line at 13 at Plaid, the build team's Low counting examples restated for three builders). LEVEL-2-STEPS.md, the unit counts at every step the ladder touches and every step total recomputed from its conformed units, all 23 steps at all five tiers, each printed total verified as the sum of its stated units. PLAID.md, the derivation passage restated on her ladder as the source, the counting convention, the team maxima table, the per-step staffing table, and the section 5 union derivation: the maxima sums are 255 at Plaid and 174 at Extra High, the removals are 39 and 29, and the union totals are 216 distinct agents at Plaid and 145 at Extra High. LEVEL-4-MEMBERS.md carries the named rosters as lists and stated no tier figure to change; each roster was verified against the ladder and stands recorded in the landing paper. The role files under build-flow-agents: six ladder sentences conformed across 272 files (the pre-plan sentence in 120 researcher files, the build sentence in 42 builder files, the imagination sentence in 40 files, the design sentence in 30 files, the note-taking sentences in 40 files), and the audit and logic audit sentences verified as already stating her figures in 175 and 25 files. The generator states no team size and took no change. The AGENTS.md convention bullet from DQ-168 was amended in place so it no longer states the superseded ladder. Union figures under the team maxima method for the remaining tiers, recomputed under the full ladder: Low 38, Medium 62, High 97. The difference DQ-160 left open between the method figures and the checklist's verified totals stands exactly as open as it was: the checklist figures stand one above the method figures at Low, Medium, and High, and no passage names the seat. The Build Flow Checklist minimums were landed in the same job through the checklist artifact itself: the counts stand in the artifact's source (client/src/flow.ts) as constants, not stored data and not a declared action, so they were changed by a repair through the artifact route, and a full read of the file's contents after the edit verified every unit constant, every stage figure, and every stage total against the ladder. Its whole-flow totals stand at Low 39, Medium 63, High 98, Extra High 145, and Plaid 216, the High figure landed by a correction in the same job after the first edit pass left it at 90. Seats above a named roster (note-taking at High and at Plaid, imagination at Plaid, design at Plaid, and the pre-plan team above its 24 named approaches) stand open as named in the landing paper; no seat was invented in this landing. Landing paper and element list: ~/workspace/build-flow-expansion/her-ladder-landing.md. Nothing was uploaded to GitHub under this entry: the build flow itself is never uploaded (DQ-156). Status: landed in the flow documents, the role files, this queue, AGENTS.md, and the checklist artifact.

## DQ-170: the build flow update job of 2026-11-13, one job folding in the day's rulings. RULED by Captain JP 2026-11-13

Origin: Captain JP's order in the main chat, 2026-11-13: "I want you to update the build flow." The day's rulings were treated as one update job on the build flow and folded in together, and this entry records the job as one closed item. The job's parts: her team-size ladder, landed in the flow documents, the role files, and this queue under DQ-169, which covers the ladder itself; her principles, stated in the flow where they belong as standing rules R-259, R-260, and R-261 in LEVEL-1-STANDING.md (paper: ~/workspace/build-flow-expansion/her-principles-landing.md); the original role files order of the same day, worked as an inventory against the ladder (~/workspace/build-flow-expansion/role-file-inventory.md) and then as authoring: 34 original role files written for the seats the ladder leaves without one, 28 new role definitions appended to LEVEL-4-MEMBERS.md, and the originality overseer's verdict PASS for the wave, 34 PASS and 0 FAIL (paper: ~/workspace/build-flow-expansion/role-files-authoring.md); and the Build Flow Checklist minimums, landed in the checklist artifact itself, as recorded at DQ-169. The job's own closings, recorded at ~/workspace/build-flow-expansion/update-job-conforming.md: the role files index at ~/workspace/build-flow-agents/INDEX.md brought to the true supply, 558 role files (17 in the standing set, 100 at Low, 100 at Medium, 101 at High, 106 at Extra High, and 134 at Plaid), with the 34 new files listed in their sets and the index's link counts verified against the tree; and the pre-plan size sentence in LEVEL-4-MEMBERS.md conformed to her ladder figures, 5 at Low, 9 at Medium, 15 at High, 25 at Extra High, and 35 at Plaid, in place of the open 3 to 16 range the sentence carried before, which stands in older records as history, the change made by staged copy, diff, and install with the rest of the paragraph untouched. The whole job applies to stages not yet closed, under her standing prospective rule; a stage already closed keeps the staffing it closed with. The job's fold-in trace and corpus gate follow this entry under the Manager's seating. Nothing was uploaded to GitHub under this entry: the build flow itself is never uploaded (DQ-156). Status: closed.

## DQ-171: set-backs and whole-build restarts as standing practice, from Captain JP's orders of 2026-11-13. RULED by Captain JP 2026-11-13

Origin: two orders in the main chat, 2026-11-13, given in her order. First: "Set it back to design." The AgenC escrow (Plaid) goes back to Step 6 (Design brief): Steps 6 and 7 re-run at her Plaid figures, Design base 12 plus its carried seats and the brief loop's teams at her Plaid numbers, on the existing brief and its records as base and data, nothing deleted, Step 8 not proceeding and waiting until Steps 6 and 7 close fresh at the new staffing, and the checklist showing the escrow back at Design brief. Second: "Then update the build flow." Once the set-backs are placed, today's practice is written into the flow documents as standing rules. The day's other set-back, ordered in the same run of orders, was Crucible (Extra High) set back to Step 14 (Build) after closing that step qualified at a build team of 6 against her Extra High build figure of 11, the existing product and records as its base and data and Step 15 not opening until Step 14 closes at the new size; and the practice the second order generalises includes the whole-build restart she ordered the same day for every running Low and Medium build, on the terms that the restart uses what already exists as its base, cannibalising the current run's work at each step, with older runs as data for the build first and inspiration second, and no earlier verdict or closure carrying. Ruled and landed: three new standing rules in LEVEL-1-STANDING.md. R-262, prospective staffing on a size change: when Captain JP changes a team size, stages not yet closed staff at the new figure and stages already closed keep the staffing they closed with, stated in full form in the standing rules as her prospective rule, reading with R-260 and recording the landing form of DQ-168, DQ-169, and DQ-170 as its instances, with the conformance of an open stage's roster recorded in its step record before its gate sits. R-263, set-back of a closed stage: a stage that closed staffed below her figure for its tier may be set back on her order alone; it re-runs at her figure for its tier, staffed in full, on the earlier run's work as base and data, nothing deleted, no verdict, closure, or gate result of the earlier run carrying into the re-run, the stage closing again only on a fresh closure under R-7, the following stage not opening until the set-back stage closes fresh, and later work done under the earlier closure standing as records and data only. The worked examples (Crucible set back to Build, the AgenC escrow set back to Design brief) are named in the rule's record note only, not in its operative text. R-264, whole-build restart: a build restarts on her order alone from Step 1 under the ladder then in force, in the same project and the same repos, nothing deleted, each step cannibalising the existing run's work for that step as its base, older runs as data for the build first and inspiration second, material carrying and verdicts and closures not carrying, every step closing fresh under R-7 in its own instance before the next opens, the restart recorded with the checkpoint the existing run was fixed at as its base. The worked example (the Low and Medium restart of 2026-11-13: Muster-lite, the decision queue validator, the metrics starter-set collector, and the isolated checker, each checkpointed first) is named in the rule's record note only. Landed with the rules: a closing clause appended to R-7 in LEVEL-2-STEPS.md, stating the standing of a closure under a later size change, a set-back, and a restart, so that closure reads from the new rules; the FLOW.md inventory of LEVEL-1 rule headings corrected from 78 to 81, naming R-262, R-263, and R-264; and one plain paragraph in FLOW-PLAIN.md carrying the plain-words form of all three rules. The R-7 amendment adds no rule heading, so the FLOW.md inventory of LEVEL-2 headings takes no change, and LEVEL-3, LEVEL-4, METRICS.md, REPORTING.md, and PLAID.md take no change under this entry. No new standing role is created: the standing roles stay 17, and no count in any document changes except the LEVEL-1 rule heading count, 78 to 81. Pristine backups of the five changed files stand in ~/workspace/build-flow-expansion/ under the names setback-restart-backup-2026-11-13- followed by the file name. Element trace: setback-restart-rules-trace.md. Corpus gate: setback-restart-rules-corpus-gate.md. Nothing was uploaded to GitHub under this entry: the build flow itself is never uploaded (DQ-156). Status: closed.
