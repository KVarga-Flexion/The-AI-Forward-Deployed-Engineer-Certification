# Your use case

**This directory is yours.** Everything else in this repository is teaching
material we wrote. This is the one place you work, and every technical challenge
across all ten weeks reads from it or writes to it.

> **One use case, all ten weeks, no restarts.**

That rule is the whole design. The most common way this cohort goes wrong is a
student switching use cases in Week 5 because the first one got hard — and then
Week 8 has nothing to fine-tune against and Week 10 has nobody to report to.
Choose something you actually own, at work, that annoys you weekly.

---

## The files

| File | Created in | Grows in | Collected in |
| --- | --- | --- | --- |
| [`CHARTER.md`](./CHARTER.md) | TC1 | TC3, TC5, TC8 | every week's Session 2 opens by reading it |
| [`stakeholders.md`](./stakeholders.md) | TC1 Step 6 | **every week** | **TC10** — the final report goes to these people |
| [`ecosystem.md`](./ecosystem.md) | TC1 Step 6 | **TC9** extends this same file | TC9, TC10 |
| [`decisions.md`](./decisions.md) | TC3 | TC5–TC8 | TC5's critique, TC10's handoff doc |
| [`evals/golden.jsonl`](./evals/) | Week 1 S2 | TC2, TC4, TC6 | **TC8** — the bar a fine-tuned model must clear |
| [`data/DATASHEET.md`](./data/DATASHEET.md) | TC2 | TC3, TC8 | reviewers |
| `app/` | TC1 | TC3, TC5–TC8 | TC10 handoff |

Nothing here is busywork. Each file exists because something later is impossible
without it. `stakeholders.md` is the clearest case: TC10 asks you to send a
client report to everyone you worked with during the cohort. If you did not keep
the log, you cannot write the report.

---

## 🔒 Never commit real company data

`data/` is gitignored except its datasheet. That is deliberate and it is not
negotiable — you are pushing this to a public fork.

| Don't commit | Do commit |
| --- | --- |
| Real records, tickets, documents, customer names | Synthetic data you generated |
| Internal hostnames, IPs, architecture diagrams | The *shape* of the answer: "on-prem k8s, SAML, no egress" |
| Credentials, tokens, connection strings | `.env.example` with placeholders |
| Screenshots of internal tools | Screenshots of your own app |

When describing your firm's infrastructure, describe the pattern, not the
specifics. "Images go to an internal registry; Docker Hub is blocked" is useful
to everyone and identifies nobody.

If in doubt, leave it out.
