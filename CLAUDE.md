# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> [!IMPORTANT]
> **If you are helping a student work through a week's challenge, stop reading
> here and follow that challenge's own `CLAUDE.md` instead.**
>
> This file is for people *authoring* the curriculum. Claude Code also loads
> parent-directory `CLAUDE.md` files, so a student who opened the repository root
> will see this one — it does not apply to them, and it does not override the
> instructor-mode rules in `NN_Week/challenge/CLAUDE.md`.
>
> Telling them apart: a student is building the challenge app and filling in
> README blanks. An author is editing the teaching material itself.

## What this repository is

Curriculum for **The AI Forward-Deployed Engineer Certification** (#FDE1), a
**10-week** cohort course run by AI Makerspace: 2 sessions and 1 technical
challenge per week. It is a *content* repository whose deliverable is teaching
material, not a shipped application.

The audience is working enterprise engineers, many on managed Windows laptops
inside firms with real network restrictions. Content is practical and
production-aware, never academic.

The stated goal, which settles most design arguments: *each student engages with
their own company as a world-class AI Forward-Deployed Engineer.* Everything is
aimed at their real workplace, not a toy.

## The two kinds of files here

The most important thing to understand before editing anything.

| Kind | Example | Who reads it |
| --- | --- | --- |
| **Student-facing deliverable** | `NN_Week/challenge/**`, `NN_Week/sessions/*.py` | Students, and *their* Claude Code |
| **Repo-working guidance** | this file, `scripts/`, `helpers/` | You |

`NN_Week/challenge/CLAUDE.md` is **course content**, not instructions for you. It
runs the student's Claude Code in **instructor mode**: explain, debug, review,
teach — but decline to author the graded deliverables. That is a pedagogical
guardrail, not boilerplate. If you edit it, keep it consistent with the
challenge README's Steps 2 and 4, which describe the behaviour to students. **The
two must not drift.**

**`sessions/` gets no `CLAUDE.md`.** Session notebooks are taught, not graded — an
agent that declines to write code there is just broken.

**Never hand students a copy-pasteable solution to their own graded work.** Show
shape, signature, or pseudocode. Worked examples of *adjacent* things are fine
and encouraged.

## Layout

```
NN_Week_Name/
├── README.md            # week front page
├── sessions/
│   ├── S1_Title.py      # marimo notebook — THE SOURCE OF TRUTH
│   ├── S1_Title.ipynb   # GENERATED. Never hand-edit.
│   ├── S2_Title.py/.ipynb
│   └── data/
└── challenge/
    ├── README.md        # the week's technical challenge
    └── CLAUDE.md        # instructor mode
```

### ⚠️ Directory numbers are not week numbers

**Week 1 owns two numbered directories**, because TC1 is explicitly two
deliverables: `01_Product_Engineering` (the Enterprise FDE Challenge) and
`02_Getting_to_Concreteness` (the worksheet). Both are pre-work delivered at
enrollment.

Everything after shifts by one:

| Directory | Course week |
| --- | --- |
| `01_`, `02_` | Week 1 |
| `03_` … `11_` | Weeks 2 … 10 — **week = NN − 1** |

**Prose referring to "Week N" means the course week, not the directory.** Do not
"fix" a notebook that says *"in Week 5 these become MCP tools"* to say Week 6 —
Week 5 is `06_Agent_Architecture` and the prose is right. When renumbering,
rewrite **paths only**.

`02_Getting_to_Concreteness` has no `sessions/` and no `challenge/` of its own —
it is a worksheet, and it is owned by a different author (see below).

`use_case/` is unnumbered and is **the student's own directory**, not teaching
material. Every challenge reads and writes it; it is what makes the cohort's
arcs real instead of aspirational. Do not author content into it beyond
templates.

## Commands

```bash
make setup              # uv sync
make mirrors            # regenerate every .ipynb from its .py
make check              # what CI runs
make nb F=<path.py>     # open one notebook standalone, sandboxed

python scripts/new_session.py 04_Retrieval S1 "Retrieval Variants"
```

## Notebooks are marimo, and that has rules

Notebooks are marimo `.py` files. **The `.ipynb` next to each one is generated** —
`scripts/mirrors.py` enforces it and CI is the gate. On an `.ipynb` merge
conflict, never resolve by hand: `git checkout --ours <file> && make mirrors`.

Mirrors ship **without outputs** (`--include-outputs` would need API keys and
destroy byte-determinism). So a mirror is a *runnable* artifact, not a *readable*
one — which means each week's `README.md` carries more load than usual. It needs
the notebook outline and the key results, so someone browsing GitHub learns
something without executing anything.

**"Runnable" has a caveat, and it is measured, not assumed.** Every expensive
cell sits behind `mo.ui.run_button` + `mo.stop(...)`. In marimo, `mo.stop` raises
a `MarimoStopError` the runtime catches, halting that cell and marking its
dependents `ancestor-stopped` — the guard working. A plain Jupyter kernel has
nothing to catch it, so in the mirror the same guard surfaces as an uncaught
exception and every dependent cell then fails with `NameError`. **A mirror is
therefore not "Run All"-clean in Jupyter**, and cannot be without deleting the
guards, which would make a notebook fire hundreds of model calls on open.

`make execute` runs every notebook in **both** formats and classifies the three
outcomes — clean, guard fired, real error. Use it before shipping a notebook.
`make check` cannot substitute: it only proves the two formats are byte-identical,
and a notebook that raises on cell three exports identically to one that works.
That gap hid a duplicate `from dataclasses import dataclass, field` across two
cells in Week 4's S2 — reactive rule 1, the failure this file warns about first —
which shipped broken in marimo and passed every gate.

**The marimo bump ritual.** marimo is pinned exactly, because the `.ipynb`
metadata embeds its version — a bump rewrites every mirror in the repo. To bump:
edit the pin in `pyproject.toml`, run `python scripts/mirrors.py --sync-pins`,
then `uv lock && make mirrors`. **That commit contains nothing else.**

### Reactive-execution constraints

marimo derives execution order from a dependency graph, not file order. These
produce *silently wrong* notebooks, not errors:

1. **One definition per variable.** Two cells defining `df` is an error. Rename by
   stage (`df_raw`, `df_clean`). The #1 Jupyter-conversion failure.
2. **Never mutate a variable defined in another cell.** `chunks.append(...)`
   downstream is invisible to the graph — dependents don't re-run and nothing
   warns you.
3. **Loop variables leak to global scope.** Prefix throwaways with `_`
   (`for _doc in docs:`); marimo treats `_name` as cell-private.
4. **No IPython magics.** No `!pip`, `%%time`, `%matplotlib`. It's a `.py` file.
5. **`mo.ui` elements: define in one cell, read `.value` in another.** Reading
   `.value` in the creating cell always returns the default.
6. **Always `r"""` for markdown** — LaTeX, regexes, and Windows paths break
   otherwise.
7. **Guard expensive cells** with `mo.ui.run_button` + `mo.stop(...)`. A notebook
   that fires 200 model calls on open is hostile.

### Environments

Hybrid, and both halves are required. One root `uv` project for shared code and
the challenge apps; **plus** every notebook declares PEP 723 inline dependencies
so it also runs standalone:

```bash
uv run marimo edit --sandbox 04_Retrieval/sessions/S1_Retrieval_Variants.py
```

`scripts/mirrors.py` checks that a notebook's inline deps match the root
`pyproject.toml` exactly, or appear in `[tool.fde].sandbox-only`. Otherwise two
students on the same lesson get different library versions.

### `helpers/` is two tiers

**Tier 1** (`nb`, `config`, `display`, `ui`) — stdlib + `marimo` +
`python-dotenv` only, enforced by an AST check in CI. Every notebook imports it,
including sandboxed ones, so one stray heavy import at module scope breaks them
all. **`helpers/__init__.py` must never import tier 2.**

**Tier 2** (`llm`, `embeddings`, `judge`, `vectorstore`, `rag`, `sdg`) — imports
its heavy dependencies *inside functions*, so failure lands at the call site with
an actionable message rather than at import time.

**Tier 2 is app-side, and that is why notebooks do not import it.** The sessions
teach `completion()`, `span()`, `chunk()`, and a judge from scratch — that is the
lesson, and packaging it away would delete it. The tier-2 module is what the
*student's application* imports afterwards, so a markdown code block showing
`from helpers.trace import Tracer` is a legitimate reference, not a missing
import. What is **not** legitimate is a tier-2 module nothing mentions at all:
that is code with tests and no callers, which reads as maintained and is not. It
happened twice here. `scripts/check_helpers.py` now fails CI if any tier-2 module
is referenced by no session, challenge, or week README — name the consumer or
delete the file.

**`llm.py` is the one every other tier-2 module goes through.** It owns the
explicit timeout, the retry policy, and token accounting. Before adding another
`completion()` call anywhere in `helpers/`, use `llm.chat` / `llm.complete`
instead — there were three hand-rolled retry loops here once, two of them with no
timeout at all, and the failure that produced was a forty-minute silent hang.
`is_retryable()` is the rule they now share: 429 and 5xx are worth another
attempt, any other 4xx is not, and an unrecognised error surfaces immediately
rather than after the full backoff budget.

Every notebook opens the same way:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(mo.notebook_dir()).parent.parent))
from helpers import nb
CFG = nb.bootstrap(require=("OPENAI_API_KEY",))
```

`mo.notebook_dir()` resolves from the notebook's own file location, which is why
this works identically in the root env and under `--sandbox`.

**The boundary rule, which is the one people break:** keep the from-scratch
teaching code *in the notebook*; only pure plumbing goes in `helpers/`.
`helpers.rag.chunk` exists so Week 7 doesn't re-teach chunking — not so Week 3
can skip it. If reading it is the lesson, it stays in the lesson.

## House style

Match `NN_Week/sessions/` to the existing notebooks. Section rhythm:

Title → `## 🏗️ Build | 🚢 Ship | 📤 Share` → why-this-matters + estimated time →
`## Setup` (bootstrap cell ending in `✅`) → repeating `## Task N` (markdown →
code → reflection) → `## 🏗️ Activity` → `## What We Just Built vs. What's In
Production` → `## 🚀 Advanced Build`.

Prose: plain, direct, short sentences. Emoji in headers, sparse in body. Inline
`code` for vars, files, commands. `---` between major sections.

**Imports are earned.** Build the primitive from scratch first — a plain function
using stdlib and numpy — then show the library in a *later* task with one line on
what it added. Teach **weak→strong** wherever there's a lever: show the bad
version running, then the good one, on the same input.

## The through-lines

Three arcs are deliberate. Do not let them drift:

- **Deployment.** Week 1's egress probe and Step 6 questions seed
  `use_case/ecosystem.md` → **TC9 extends that same file** with the full
  checklist → TC10's handoff doc is built from it.
- **Stakeholders.** Week 1 Step 6 starts `use_case/stakeholders.md`; every week
  appends; **TC10 is a report to those people** and is unfulfillable without it.
- **One use case, all ten weeks, no restarts.** Chosen in TC1, never changed. The
  Week 1 schema and 5 hand-written golden examples are what make this mechanical:
  TC2 generates data matching the schema, TC3's endpoint implements it, TC4
  scores against the goldens, TC8 must beat TC4's numbers.

Every challenge README opens by linking `use_case/CHARTER.md`; every submission
checklist has a `use_case/` line; every week's S2 notebook halts if the charter
is still the template.

## Reference material, and how to use it

Several of the topics in this course have mature implementations sitting on the
author's machine. They are **reading and lecture material, not dependencies.**

- **`lo-agent`** (`/home/imjonezz/Desktop/local_harness`) — the instructor's own
  agent harness for local models. Covers guardrails, agent memory, constrained
  decoding, logit manipulation, simulation-based evals, prompt optimization, and
  MCP/UTCP integrations. Directly relevant to Weeks 2, 4, 6, 7, and 8.

  **Students may use it.** It is source-available under the lo-agent Community
  License, and any week that references it must state the terms plainly, because
  a student who deploys it at their firm without reading them creates a problem
  for their employer:

  | Situation | Terms |
  | --- | --- |
  | You, learning, on your own machine | Free. Personal Use covers educational and evaluation work, and permits modifying it. |
  | Your firm running it **unmodified** | Free, including commercially — keep the branding and licence intact. |
  | Your firm **changing** it — behaviour, appearance, or branding | Needs an Enterprise License, negotiated with the licensor. |

  "Configuration" (flags, env vars, config files, documented extension points) is
  not modification. Editing the source is.

  This is worth teaching, not just disclosing. Reading a licence before putting
  someone's software inside a bank is an FDE skill, and this is a live example
  where the answer is "you can, and here is the conversation your employer needs
  to have." Week 9 is the natural place to make that explicit.

  **Still build from scratch first.** That is the pedagogical rule regardless of
  licensing. lo-agent's value here is the comparison — *you wrote a 30-line
  version; a production harness adds these six things, and here is why each one
  exists.* Its `docs/` essays (`access-ladder.md`, `frontier-vs-harness.md`,
  `uncertainty-done-right.md`) are good assigned reading.

- **`llms-from-scratch`** — mostly derived from Sebastian Raschka's Manning
  books, so treat the book-derived notebooks as reference for *us*, not material
  to redistribute. Two are original and safe to adapt:
  `build_deployment_from_scratch.ipynb` (vLLM serving, GGUF/AWQ quantization)
  and `build_jacobian_lens_from_scratch.ipynb` (activation steering).

- **Prior cohorts** — `Titanium_Engineer`, `Titanium_Engineer-02`,
  `AI_Challenge_Lab_Morgan_Stanley`, `AIE9`. Adapt freely; these are ours.
  `Titanium_Engineer-02/AGENTS.md` is the house-style source.

## Claims in student text must be verified

Student-facing instructions get followed literally by people who cannot debug
them yet. Before writing a version number, package name, keystroke, extension ID,
or API signature, check it.

Real examples from this repo's history: the Gradio capability is
`gradio.Server`, not `gr.Serve`; `@app.api` endpoints silently return nothing
without a `-> str` annotation; Cloudflare Quick Tunnels don't support SSE, which
breaks Gradio streaming; and the original AI Engineer Challenge this is modeled
on shipped a hardcoded `model="gpt-5"` and `allow_origins=["*"]` that were
deliberately not inherited.

## Multi-author workflow

Several authors work concurrently and merge via PRs from `agent/*` branches.
Ownership as of 2026-08-01:

- All week directories except `02_`, plus the shared infrastructure — Chris (IMJONEZZ), branch `Chris-working`
- `02_Getting_to_Concreteness/` — ToddLLM

Scope edits to owned areas unless told otherwise. Before claiming a week
directory, check it's free on unmerged branches:
`git ls-tree -r --name-only origin/<branch>`.
