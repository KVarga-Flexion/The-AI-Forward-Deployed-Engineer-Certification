# Working on Your Real Project Without Your Real Data

You work on your real company project all ten weeks, and none of your company's data comes to the course. This page is how: profile the real data with the team that owns it, bring back the shape but not the rows, generate a stand-in that matches that shape, build and test on the stand-in, and treat the move to real data as your firm's conversation rather than ours.

## The short answer

The default path is five steps, and the course is built around it.

1. **Collect a sample from the team that owns the data** and understand its structure, schema, and which characteristics matter for your use case. The sample stays where it lives.
2. **Bring the shape, never the rows.** No real data comes to the course, goes into your repo, or is sent to an external model.
3. **From Week 2, generate synthetic data** that preserves the structure and characteristics without containing the sensitive content. Session 4 is the notebook; TC2 is where you do it for your project.
4. **Build and test on the synthetic set** for the rest of the course: retrieval (Week 3), evals (Week 4), the demo (Week 5), guardrails, memory, fine-tuning.
5. **Moving to real data is your organization's security and compliance conversation**, not something the course prescribes. Week 9 gives you the checklist to have it with.

If you remember one thing: a stand-in dataset has to match your real data in *shape* (schema, formats, identifiers, distribution, the ugly cases), not in *content*. Shape is what makes the work transfer; content is what gets you a meeting with Legal.

## Step 1: profile the real data where it lives

Ask the team that owns the data for thirty minutes and a screen, not an export. You leave with a one-page profile, not rows. What to capture:

| Capture | Why it matters later |
| --- | --- |
| **Schema**: field names, types, which are required, which are free text | Your `Request`/`Response` models (TC1 Step 5) and the validator that throws bad synthetic rows away (Session 4, Task 5) |
| **Identifier formats**: `INC-30417`, `PC-4471-08`, a hostname convention, a 12-digit account number | Retrieval behaves differently on identifiers than on prose (Session 5); your synthetic ids must match the pattern or your regexes and lookups will never be tested |
| **Value distributions**: how many categories, which are rare, what fraction is the happy path | A generator that samples uniformly makes a dataset nothing like production; the rare category is usually the one that matters (Session 4, Task 2; Session 7, Task 7) |
| **The ugly cases**: pasted email chains, typos, empty fields, two records for one thing, a legal hold | These are the axes of variation; a dataset with none of them hides every failure your system has |
| **What "correct" looks like**: who judges an output, and where the judged ones already live | Your five golden examples (TC1 Step 7) and the back-testing source for Week 4 |
| **Volume and flow**: rows per day, where they arrive from, in what file format | Sizing (Week 3), and the format-fidelity checklist below |
| **Who may see it**: the classification label, the access scope, anything under hold | Decides which of the strategies below you are allowed to use at all |

Write the five golden examples **from memory, with every name, identifier and company invented** (Session 4's analyst did exactly this). They are the seed for everything generated later, and they are the only "data" you write down.

> **If you cannot get thirty minutes with the owning team, that is itself the first finding for `use_case/stakeholders.md`.** The course has a step for it in Week 1.

## Step 2: what never comes to the course

Four rules. They are the same rules your firm's security team would give you, stated so you can follow them without asking.

1. **No real rows, anywhere in the course.** Not in your repo, not in a notebook output, not in a screenshot on Maven, not in a demo. `use_case/data/` is gitignored for a reason; the datasheet next to it is not, because the datasheet describes shape.
2. **No real data to any model your firm has not approved for it.** That includes the course's default API key. If your firm has an approved gateway, use it; if it has none, generate from a description (Step 3) so there is nothing real to send.
3. **Records under legal hold, and anything with a classification above what you may share, are excluded before generation, not filtered after.** No filter in the course can substitute for choosing seeds that were never under hold (Session 4, Task 1).
4. **Assume a screenshot travels.** If it would embarrass you in a public repo, it does not go in a demo either.

**Vendor settings, in case your firm does allow an external model.** Get these in writing from the vendor's data-use terms, not from a colleague:

| Check | What to look for |
| --- | --- |
| Training use | Whether your prompts can be used to train models. Consumer chat products often can unless you opt out; API and enterprise plans usually cannot by default. Verify the exact product and plan you are using; "the API", "the app" and "the Team plan" are different contracts (the Anthropic specifics are in the setup example below) |
| Retention | How long prompts and outputs are stored, and whether a zero-retention option exists for your account |
| Region | Where the request is processed; some firms require in-region |
| Enterprise terms | Whether your firm's agreement overrides the public terms, and whether your key is under it |

The course's own answer to all four is Session 3: run the weights yourself. A model on your laptop sends nothing anywhere, and the local-inference session exists so that this is a choice you can make rather than a constraint you are stuck with.

## Example: setting up Claude Desktop and Claude Code to follow these rules

The four rules above are procedural. This is what they look like as settings in the two Anthropic tools most of the cohort uses. Everything here was checked against Anthropic's own documentation on 2026-09-29; settings move, so open the linked pages before you rely on a detail. Other vendors have equivalents, and the four checks in the vendor table are what to look for in theirs.

### 1. Your plan decides whether training is even a question

- **Free, Pro and Max (consumer) accounts, including Claude Code signed in on one of them.** Your chats and coding sessions can be used to improve Anthropic's models only if the model-improvement setting is on. Turn it off at [claude.ai/settings/data-privacy-controls](https://claude.ai/settings/data-privacy-controls) (Settings → Privacy → *Help improve Claude*). With it off, retention is 30 days; with it on, five years. An **Incognito** chat is never used for training and does not appear in your history, which is the right mode for anything you are unsure about.
- **Team, Enterprise, the API, and Claude through Amazon Bedrock, Google Vertex AI or Microsoft Foundry.** Never used for training by default; 30-day retention as standard; Enterprise can be put on zero data retention. If your firm has any of these, use it instead of a personal account. That is the *Enterprise terms* row of the vendor table, answered.
- Rule 2 still applies. A personal account with training switched off is a data-use setting, not your firm's approval for the model. The setting is what makes the vendor's terms acceptable; the approval is a separate conversation.

### 2. Claude Code: deny it the real data, and turn off the optional traffic

Claude Code reads its settings from `~/.claude/settings.json` (you, every project) and from `.claude/settings.json` inside a repo (shared with whoever clones it; commit it). A version that follows the four rules:

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./use_case/data/**)",
      "Read(~/Downloads/exports/**)"
    ]
  },
  "env": {
    "DISABLE_TELEMETRY": "1",
    "DISABLE_ERROR_REPORTING": "1",
    "DISABLE_FEEDBACK_COMMAND": "1",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"
  },
  "cleanupPeriodDays": 7
}
```

What each part does:

| Setting | Rule it enforces | What happens |
| --- | --- | --- |
| `permissions.deny` with `Read(...)` | 1 and 2 | Claude Code will not open those paths, even when you ask it to. `.env` holds your keys; `use_case/data/` is where the generated set lives and where a real export would land if you ever broke Rule 1; the last line is wherever a real sample could sit on your machine. Deny rules apply immediately, before you have even trusted the folder |
| `DISABLE_TELEMETRY` | 2 | No usage statistics leave your machine |
| `DISABLE_ERROR_REPORTING` | 2 | No crash reports, which can carry context from the session |
| `DISABLE_FEEDBACK_COMMAND` | 1 and 4 | Removes `/feedback`, which submits the transcript of the current session. A transcript with a real record in it is a screenshot that travels |
| `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` | 2 | All of the above plus update checks and feature flags in one line. Note that it also switches off Remote Control |
| `cleanupPeriodDays` | 1 | Local transcripts in `~/.claude/projects/` are deleted after seven days instead of the default thirty |

Two things to know about precedence. Settings your firm pushes as managed settings (`managed-settings.json`, MDM, or the admin console) override yours, so if IT has already set these you cannot loosen them from your file, which is the point. And `/status` inside Claude Code lists every settings file that is loaded and where each rule came from; run it once after saving.

**If your firm has a cloud tenant, route through it.** `CLAUDE_CODE_USE_BEDROCK=1`, `CLAUDE_CODE_USE_VERTEX=1` or `CLAUDE_CODE_USE_FOUNDRY=1` (with that provider's region and credentials) keeps every request inside your firm's own AWS, Google Cloud or Azure account under commercial terms, and telemetry to Anthropic is off by default on those routes. That is the *Region* row of the vendor table, answered.

### 3. Claude Desktop: point file access at the synthetic folder only

Claude Desktop reaches your files through MCP servers listed in `claude_desktop_config.json` (Windows: `%APPDATA%\Claude\claude_desktop_config.json`; macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`; or Settings → Developer → *Edit Config* in the app). A filesystem server only sees the directories you list after its name, so list one:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "C:\\dev\\my-fde-project\\use_case\\data\\synthetic"
      ]
    }
  }
}
```

(Windows paths in JSON need doubled backslashes.) Do not list your Downloads folder, your desktop, or anywhere a real export could be sitting. The app still asks you to approve each read or write, so an unexpected prompt for a path you did not list is a sign something is wrong. The same rule applies to any connected folder or Cowork task: connect the project directory, not your home directory. And the model-improvement setting in part 1 is an account setting, so the Desktop app follows it too.

None of this stops you pasting a real record into a chat "to give it an example". That is the FAQ's answer, and it is the leak every setting above cannot prevent.

### 4. The two-minute check before a session

- `/status` in Claude Code shows your deny list and which settings files are in force.
- Ask Claude Code to show you `.env`. It should refuse.
- The privacy settings page shows model improvement off, or you are on a Team, Enterprise or API account.
- `git status` does not list anything under `use_case/data/`.
- Nothing real is on screen before you share it.

Sources: [Claude Code settings](https://code.claude.com/docs/en/settings) · [Claude Code data usage](https://code.claude.com/docs/en/data-usage) · [Anthropic Privacy Center](https://privacy.claude.com/) · [Connecting local MCP servers to Claude Desktop](https://modelcontextprotocol.io/docs/develop/connect-local-servers)

## Step 3: synthetic data that is fit to build on

Three properties, and each has a check. Session 4 walks the loop; TC2 makes you do it on your own project.

**A. It matches the content of your real data.** Not the words; the *variation*. Name the axes along which real inputs differ (who writes them, how long, how hard, how messy) and generate across every combination, so the rare cases exist in the proportions you chose rather than by luck. Then throw most of it away: near-duplicates by character n-gram overlap, rows that fail your schema, anything that leaked. Report the number of rows you *kept* as the size of the dataset, not the number you generated. The check: sort by axis, read one row from each, and ask whether they actually differ or whether the model produced the same thing wearing different hats.

**B. It is created without sending confidential data anywhere.** The procedural answer is stronger than any technical one: **generate from the schema and a written description, not from real records.** Your seeds are the five goldens you wrote from memory with invented names. If that is the input, there is nothing confidential to leak, and the model you generate with can be a local one (Session 3) or your firm's approved gateway. Then run the leak check anyway, because "should be clean" is not what security asked for. The check: the regex pass over your seeds, then the four-item read-through in Session 4, Task 6, and a classification label on the output.

**C. It matches the format of your actual pipeline.** This is the property people skip, and it is what makes the course's work run at your desk on Monday. Match all of these, not just the schema:

| Format fidelity | What to match | How to check |
| --- | --- | --- |
| Field names and types | Exactly as the system of record exports them, including the ones you do not use | Your pydantic model is the *same object* the endpoint imports (Session 4, Task 5) |
| Identifier patterns | The regex of every id, hostname, code and reference number | Generate ids from the pattern, never from a list of examples; a lookup keyed on them should work |
| File shape | The format the pipeline emits: JSONL, CSV with that delimiter, Parquet, an API response with that envelope | Your loader reads the synthetic file with no branch that says "if synthetic" |
| Text shape | Email chains with quoted replies, ticket templates with their section headers, timestamps in the house format, the ticketing system's own line breaks | Print ten rows next to the profile from Step 1 and read them aloud |
| Distribution | The happy-path fraction, the rare categories, the length spread | A histogram per axis against what the owning team told you |
| Volume | Enough rows to see a five-point change (Session 7, Task 8), in the daily batch sizes the pipeline sees | The datasheet says how many, and how many per axis |
| Attachments | If the real records carry screenshots, scans or recordings, the synthetic ones carry stand-ins in the same file types | Session 6's four questions about non-text content |

**Then write the datasheet**, particularly *what this data cannot validate*. A synthetic set proves your pipeline runs, your schema holds and your harness scores; it cannot tell you how the system performs on real inputs, and the datasheet is what stops you, in six weeks, from mistaking it for that.

## Is synthetic generation the only way?

No. It is the default because it needs no approval and it is the one the course teaches end to end. Four others exist, and two of them are better when you can get them. Pick by what you are allowed to do, not by what is most interesting.

| Strategy | What it is | Use it when | What it costs you |
| --- | --- | --- | --- |
| **Generate from a description** (the default) | Five invented goldens plus a written description of the domain, expanded across axes of variation | You cannot get an export at all, or the data is under hold or classified | Fidelity: it inherits your understanding of the data, not the data. Session 4 is this |
| **Mask a real export** | A real sample with every identifier, name and free-text secret replaced by a stable placeholder; the mapping file never leaves the firm | The owning team will give you an export and your firm's policy allows pseudonymized data in a dev environment | Rare categories and distinctive scenarios survive masking and can still identify a customer; needs the owning team's sign-off, and the mapping is itself sensitive |
| **Statistically synthesize from a real sample** | Fit a model of the columns' distributions and correlations inside the firm, then sample new rows (open-source SDV, and the commercial tools around it) | Tabular data where the joint distribution matters more than any one row; the fitting runs where the data lives | Free text is poorly served; the fitted model can memorize outliers, so the same leak check applies; another tool to get approved |
| **A public dataset in the same shape** | Someone else's tickets, claims, contracts or calls, reshaped to your schema | Your domain has one (support tickets, invoices, clinical notes, legal contracts all do) and your pipeline's format is the thing you need to exercise | The content is not yours, so the distribution is wrong in ways you will not notice; good for format fidelity, weak for content fidelity |
| **Do the course inside your firm** | Run the notebooks against real data on your own machine, with a local model, and share only the numbers | Your firm allows development on real data locally and forbids only its export | Nothing to share for peer review; every demo needs a synthetic twin anyway; the strongest option for the eval weeks if you can get it |

**A combination is usually right.** Generate from a description for the course deliverables; if you can get a masked or in-firm sample, use it *only* to check that your synthetic set's distribution and format match (Session 5's replica bonus is exactly this: measure on the stand-in, confirm on the real thing, keep only the findings that survive the swap).

**Two things that are not strategies.** Removing names by hand from a real export and calling it anonymized is masking done badly, and the thing that identifies a customer is rarely the name. And "the model will not remember it" is not a data-handling policy; the vendor's written terms are.

## Step 5: when it is time for real data

That is your organization's conversation, and the course does not prescribe it. What the course does is make sure you arrive at it with the right things in hand:

- **A working system on a stand-in whose datasheet says what it cannot prove.** The first signature usually wants to see something running before it signs (Session 4's analyst lived this).
- **The numbers, with intervals, on data you did not pick**, and the failure taxonomy that says where it is soft (Week 4).
- **`use_case/ecosystem.md`**, which by Week 9 lists the network you deploy into, the gateway you are allowed to call, the classification of the data, and who signs. That file is the agenda for the meeting.
- **The lines from every week's Share step**: the data you would swap, the model or endpoint you would swap, and the approval you would need. Those three lines *are* the compliance conversation, written down a week at a time.

Expect the answer to involve a DPIA or its local equivalent, a data classification, an approved gateway or a local model, and an owner. None of those are the course's to hand you, and all of them are easier to ask for with a demo and a datasheet than without.

## FAQ

**My project's data is entirely PII (customers, patients, employees). Can I still participate?** Yes, and you are the normal case. Profile it (Step 1), write five goldens from memory with invented people, generate from a description. The claims analyst in Week 4 and the service-desk engineer in Week 3 both work on data they are not allowed to export.

**Can I just use ChatGPT or Claude to make the synthetic data?** Only if the input contains nothing real. If your seeds are invented and your description is generic, the prompt has nothing confidential in it and any model will do. If you were about to paste a real record in to "give it an example", stop: that is the leak. Use the course's local model or your firm's approved gateway if you want to be sure, check the vendor terms in Step 2 either way, and set the tool up as in the Claude Desktop and Claude Code example before you start.

**My firm blocks every external API and Hugging Face.** Session 3 runs a 350M model on your laptop with nothing downloaded at runtime beyond the model itself; if even that download is blocked, the session's Tasks 1 to 6 run on a committed trace, and the blockage is a finding for `ecosystem.md`. Ask your platform team for the internal model registry; most large firms have one.

**Can I anonymize a real export instead of generating?** If the owning team and your policy allow a pseudonymized sample in a dev environment, yes, and it is a better distribution than anything you generate. Do it properly: stable placeholders, the mapping kept inside the firm, and the read-through for rare categories and distinctive scenarios that survive masking. Then still keep a generated set for anything you will show on Maven or in a demo.

**My data is scans, screenshots or recordings, not text.** Same rules; the stand-ins are files of the same type. Session 6 has four questions for you: is the information actually visual or text-as-pixels, how small is the thing that matters, do you have (thing, description) pairs, and for video what is the shortest event you must catch. Public image and document sets in the same format are often the right stand-in here.

**I have no data yet. The system does not exist.** Then the profile in Step 1 is your interview with the people who would produce the data, and your goldens are what they tell you a good answer looks like. Generate from that. You are building the dataset your future system will be evaluated on, which is a stronger position than most projects start from.

**How much synthetic data do I need?** Hundreds of rows for prototyping (coverage matters), dozens with verified labels for evaluation (correctness matters), and enough eval cases to see the improvement you expect: a few dozen for a twenty-point change, a few hundred for five points (Session 7, Task 8). Report the kept count, not the generated count.

**How do I know it is good enough?** You do not, fully, until real data. What you can check: the format-fidelity table above; that a sample read against the profile looks like the real thing to the owning team (show them ten rows, and record what they said in `stakeholders.md`); and that the datasheet's *cannot validate* section is honest. A synthetic set that passes those is good enough to build on and not good enough to quote a production number from, and saying that out loud is the whole skill.

**Can I share my synthetic data with the class?** If it was generated from invented seeds and a generic description, and your leak check and read-through are clean, it is yours to share. If it was masked from a real export, treat it as your firm's and share only the numbers.

## This week: bring back a data profile, not data

One page, filled in with the owning team, nothing in it that is a row. Bring it to the Week 2 sessions; it is what Session 4's axes and TC2's generator are built from.

```markdown
# Data profile: <your use case>

**Source system and owner:** <system> / <team, role>
**Classification and scope:** <public | internal | confidential>; who may see it; anything under hold
**Arrives as:** <JSONL | CSV | Parquet | API response | PDF | image | audio>, <rows per day>

## Schema
| Field | Type | Required | Notes (free text? identifier pattern? enum values?) |
| --- | --- | --- | --- |

## Identifier patterns
<field>: <regex or example shape with digits replaced by 9s>

## What varies (the axes)
- Who produces it: ...
- How long / how messy: ...
- The rare categories, and roughly how rare: ...
- The case the system should decline: ...

## What "correct" looks like, and who judges it
<role>, in <system>; where the already-judged ones live

## Five golden examples
Written from memory, every name and id invented -> use_case/evals/golden.jsonl

## Non-text content
Scans / screenshots / recordings? Which of Session 6's four questions apply?

## What I am NOT allowed to do with this data
<export | send to external model | share pseudonymized | share numbers only>
```

That last line is the one to fill in first. It decides which of the strategies above you are choosing between, and it is the first entry in the compliance conversation you will eventually have.
