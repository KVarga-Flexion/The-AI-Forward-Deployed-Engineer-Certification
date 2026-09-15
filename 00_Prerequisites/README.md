<div align="center">
  <img
    src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719"
    width="200"
    alt="AI Makerspace logo"
  />
  <h1>Prerequisites</h1>
  <p><strong>🧰 Get your machine ready before Session 1</strong></p>
</div>

---

## 🎯 What you'll be able to do

Start Week 1 with a working environment: the tooling installed, Claude Code
authenticated, the repository cloned, the app running locally, a model you can
actually reach, and a session notebook that opens.

> **Do this before the first session.** Session 1 *verifies* your machine and
> probes what your network allows. If nothing is installed yet, there is nothing
> to verify, and you will spend the session watching instead of working.
>
> Budget **45–90 minutes**. It is longer on a managed corporate laptop, and the
> long pole is almost always approvals, not installation — which is exactly why
> you want to start early.

---

## 🔗 Quicklinks

| # | Guide | What it gets you |
| --- | --- | --- |
| 1 | [**Your machine**](./1_Your_Machine/README.md) | Docker, VS Code, Git, Python 3.12+, uv |
| 2 | [**Claude Code**](./2_Claude_Code/README.md) | Installed, authenticated, and you know how to drive it |
| 3 | [**Clone and run**](./3_Clone_and_Run/README.md) | The repo cloned, pushed to a repo of your own, and the Week 1 app serving on `localhost` |
| 4 | [**Your model**](./4_Your_Model/README.md) | An API key or an endpoint, and a `.env` that works |
| 5 | [**Your notebooks**](./5_Your_Notebooks/README.md) | marimo installed, one session open, and the reactive rules that trip up Jupyter users |

When you think you are done:

```bash
./00_Prerequisites/scripts/setup_check.sh        # macOS / Linux / WSL
```
```powershell
.\00_Prerequisites\scripts\setup_check.ps1       # Windows PowerShell
```

---

## 🛣️ Pick your path

The two situations are genuinely different, and most of the course material
assumes the first one. If you are on the second, this module is where you get the
attention the rest of the course does not give you.

<table>
  <tr>
    <td width="180"><strong>🏢 Managed work laptop</strong></td>
    <td>
      Someone else decides what you can install and what you can reach. There is
      a proxy you did not configure and a certificate authority you did not
      install. <strong>Expect to need approvals, and start asking now.</strong>
      Every blocker you hit is course material — Session 1 turns it into evidence
      and Week 9 turns that evidence into a deployment plan.
    </td>
  </tr>
  <tr>
    <td><strong>💻 Your own machine</strong></td>
    <td>
      Nothing is in your way, and the install is genuinely quick. Your risk is
      the opposite one: you will sail through setup and then find that half of
      Session 1 is about restrictions you do not have.
      <strong>Read <a href="#-if-you-are-on-a-personal-machine">the note below</a></strong>
      so you know what to do with that time.
    </td>
  </tr>
</table>

Doing both is the strongest option, and it is not as silly as it sounds — see
[Session 1's advanced build](../01_Product_Engineering/sessions/S1_Enterprise_Dev_Environment.py).
The *difference* between the two machines is your firm's security posture, stated
precisely, which is a far better opening with an infrastructure team than a list
of questions.

---

## 🧯 When something is blocked

**A blocker is not a failure to get past. It is a finding to write down.**

That is the single most important idea in this module, and it is why the course
starts here. An FDE who says *"it doesn't work"* is stuck. An FDE who says
*"outbound TLS to `huggingface.co` is intercepted by a certificate signed by our
own CA, so Weeks 2 and 8 need an internal model registry, and here is who owns
that"* is doing the job.

Each guide has a **🧯 If it's blocked** section with two things: how to actually
work around it, and what to write in
[`use_case/ecosystem.md`](../use_case/ecosystem.md). Do both. Week 9 picks up
that exact file, and Week 10's final report is built from it.

> Do not put real hostnames, internal URLs, or company data in a file you will
> push to a public repo. Describe the *shape* — "an internal PyPI mirror",
> not its address.

---

## 💻 If you are on a personal machine

Nothing here is a waste of your time, but the emphasis shifts.

- **Setup will take you 20 minutes, not 90.** Use the rest to get further into
  [Getting to Concreteness](https://bit.ly/fde-concreteness),
  which is the highest-leverage thing you can do before the cohort starts.
- **You still need an ecosystem story.** Most of you will eventually deploy
  something inside a firm that *does* have these restrictions. Session 1's probe
  will tell you "open network, nothing here will bite you" — that is a valid
  result, and the exercise becomes imagining the constrained case rather than
  measuring it.
- **The remediation sections are still worth reading.** Certificate interception
  and blocked registries are the two things most likely to break your first real
  deployment, and reading them once now is cheaper than meeting them
  under deadline.

---

## ✅ You are ready when

- [ ] `docker --version`, `git --version`, `python --version`, and `uv --version` all print something
- [ ] `claude --version` prints a version, and `claude doctor` is happy
- [ ] You have cloned the repository and pushed it to a repo of your own
- [ ] `python app.py` in the Week 1 challenge serves a chat window at <http://localhost:7860>
- [ ] `http://localhost:7860/health` returns OK
- [ ] A session notebook opens in your browser and its setup cell prints `✅` with your model name
- [ ] Anything that was blocked is written down in [`use_case/ecosystem.md`](../use_case/ecosystem.md)

The last box counts. It is the first entry in a file that Week 9 extends and
Week 10 reports from.

---

## 🆘 Still stuck

Post in the Maven Community with: your OS, the exact command you ran, and the
exact error text. "It doesn't work" cannot be debugged; a traceback can.

If you are blocked on an approval that will take days, say so — start the
material anyway. Every guide here notes what you can do without the thing that
is blocked.
