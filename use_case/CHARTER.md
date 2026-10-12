# Project charter

<!--
  Filled in during TC1. Every week's Session 2 notebook reads this file and
  stops if it is still the template. Amended as the cohort goes.
-->

**Department:** Flexion, TrailSkills 2.0 Career Exploration team (delivery partner to American Trails and PTBA)

**Working title:** Trail Pathfinder: gap and next step

---

## The problem

**Who has it?** One real role, not a department.

A second-season conservation corps member, a few weeks from the end of her
season with nothing lined up. No trail-specific credential, phone-only, poor
signal at the work site, explores in the evening. (The product persona calls
her Maya.)

**What are they trying to do?**

Find out which of the skills a real trail job requires she already has, which
she is close to, and the one thing she should do next. She wants one concrete
next action, not a menu of twelve, and free options first.

**How do they handle it today?**

- Self-assess on TrailSkills 1.0, where people rate themselves expert at
  everything and the result is not useful.
- Browse the skills library on her own. There is no guided pathway.
- Read job postings that name credentials she has never heard of and cannot
  price.
- Ask a supervisor, whose memory is the only record of what she can do.

**What does that cost — time, money, risk, or relationships?**

Unknown in hours or dollars; asking the product owner. The one sourced
indicator: of roughly 1,600 TrailSkills.org members, 300 to 400 have made a
profile and about 18 are any good, by the platform owner's own estimate. The
process fails for nearly everyone who tries. The named risk is that she gets
pushed toward unnecessary paid training.

**The problem in one sentence. No solution in it.**

A corps member nearing the end of her season has no way to see her skills
against a real trail job, so she guesses what she is missing and what to learn
next.

---

## Success

**What does the new world look like for that person?**

In about ten minutes, signed out, on her phone, she picks a role, rates
herself on the skills it actually requires, and leaves with her strengths
first, her gaps named, and one next step she can afford, with the reason
shown. Nothing is recorded on her behalf.

**How would the firm measure it? Which numbers should move?**

- Primary: share of comparisons that end with one next step accepted.
- Secondary: correction rate on suggested next steps (how often she edits or
  rejects one), reviewed in aggregate with the framework stewards.
- Gate, not a metric: every reason traces to a named skill and a catalog
  training. Anything that does not is discarded.

---

## The first product

**Your solution in one sentence.**

Given a target role and her self-rated level on each of its required skills,
return the gap ordered has, close, missing, and up to three next steps, each
tied to one gap, naming a catalog training with its cost, what it proves, and
a one-line reason.

**Input → Output.** Be specific enough that someone could build it wrong and you
would notice.

| | |
| --- | --- |
| **In** | A target role (one of 15 draft roles), plus her self-rated level on each skill that role requires: Entry, Full Performance, Expert, or none. |
| **Out** | The role's required skills grouped **has**, **close**, **missing**, in that order, each showing the required level and her level. Then at most **3** next steps, ranked, each tied to exactly one close or missing skill, naming a training from the catalog, its cost, what it proves, and a one-line reason. A skill with no catalog training says so instead of inventing one. No percentages anywhere. Nothing is saved as a claim. |

Constraints the output must respect (from the TrailSkills business rules):
skills stay scoped to their category; framework text and course details are
retrieved and cited, never generated; an agent-proposed training alignment is
a labeled draft until a steward approves it.

---

## Decisions made later

<!--
  Amended as the cohort goes. Keep the reasoning, not just the choice — Week 5
  asks you to defend your architecture against the options you rejected, and
  Week 10's handoff doc is largely this section.
-->

| Week | Decision | Why, and what you rejected |
| --- | --- | --- |
| 1 | Cap next steps at 3 total, ranked, not one per gap | BR-6.5 is a tested business rule; the Pathfinder proposal's "one per gap" is a proposal, and the proposals README says the repo wins where they disagree |
| 1 | User is the emerging professional (corps member), not the working crew leader | The crew leader's gap view needs the evidenced/unevidenced split, which depends on the credential wallet this app cannot reach |
| 3 | Retrieval approach | <!-- TC3 --> |
| 5 | Agent architecture | <!-- TC5 --> |
| 8 | Model | <!-- TC8 --> |
