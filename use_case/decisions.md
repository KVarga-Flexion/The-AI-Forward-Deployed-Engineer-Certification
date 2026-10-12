# Decision log

One row per architectural decision, with the option you rejected and why.

> **Week 5 asks you to defend your agent architecture against the alternatives.**
> **Week 10's handoff doc is largely this file.** Both are much easier if you
> wrote the reasoning down while you still remembered it.

A decision without a rejected alternative is not a decision, it is a default.
If you cannot name what you did not do, you did not choose.

| Week | Decision | What you rejected | Why | What would change your mind |
| --- | --- | --- | --- | --- |
| 1 | **A function with retrieval in front, not an agent.** Score: 1 of 4. (1) Steps do not depend on input: compute the gap, pick a training per gap, write a reason. Fixed flowchart. (2) Yes, it must call the role library and training catalog to answer at all. (3) It does not retry on its own mistakes: invalid output is discarded and the manual path is shown (PRD §13 failure behaviour). (4) Input is enumerable: 15 roles × 55 skills × 3 levels. | An agent that reads unstructured training descriptions, searches provider sites, and loops until every gap has a route. | Deterministic control flow, fixed token cost per request, outputs that diff against the five goldens. The product's own rules want deterministic, documented scoring, and an agent that picks a training "creatively" is exactly the "pushed toward unnecessary paid training" failure. | If, after TC3, more than about a third of close-or-missing gaps have no approved catalog alignment, a single retrieval call cannot produce a grounded route and a bounded search loop would earn its cost. **Strongest counter-case:** the catalog is 40-odd calendar entries with no skill mapping yet, so "retrieve a training for this skill" may return nothing most of the time, and an agent that reads descriptions and proposes alignments is how that mapping gets built at all. The evidence that switches the verdict is the empty-result rate measured in Week 3. |
| 1 | "Close" means exactly one level below the required level (Entry vs Full Performance, or Full Performance vs Expert). Two levels below, or unrated, is "missing". | Treating any rating below requirement as "close"; treating a two-level gap as two gaps. | The research brief defines close as the same skill at a lower level; one step is the only gap one training plausibly closes. A two-level gap is one skill, one row, one honest "missing". | A stakeholder review showing explorers read "missing" as discouraging when they hold Entry against an Expert requirement. |
| 1 | Next steps are ranked close before missing, and free before paid within a group, capped at REC_MAX (3). | Missing first (biggest gap first); or one step per gap with no cap. | Strengths-first ordering and "free options first" come straight from the persona; a close skill is the cheapest credible win. BR-6.5 caps the list and the proposals README says the repo wins over the proposal. | The Step 12 demo: if the product owner or a corps member says the biggest gap is what they wanted first, flip it. The sixth golden records this as unresolved. |
| 3 | <!-- retrieval approach --> | <!-- --> | <!-- --> | <!-- --> |
| 5 | <!-- agent architecture --> | <!-- --> | <!-- --> | <!-- --> |
| 6 | <!-- guardrail level --> | <!-- --> | <!-- --> | <!-- --> |
| 7 | <!-- memory type --> | <!-- --> | <!-- --> | <!-- --> |
| 8 | <!-- model --> | <!-- --> | <!-- --> | <!-- --> |

---

The last column is the one people skip and the one clients ask about. "We chose
dense retrieval; we would switch to hybrid if exact-match queries went above ~20%
of traffic" is an engineering position. "We chose dense retrieval" is a
preference.
