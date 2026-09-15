# 2 · Claude Code

Claude Code is the agent you will use every week of this course. It runs in your
terminal and, unlike a chat window, it **acts**: reads your files, edits them,
runs commands, executes your tests, and iterates — inside a permission system
that keeps you in control.

You do not need to be fluent by Session 1. You do need it installed,
authenticated, and to have driven it once.

> **⚠️ Read this before you buy anything.** Claude Code requires a **Pro, Max,
> Team, or Enterprise** subscription, a **Claude Console** account with credits,
> or access through a cloud provider your firm already uses. **The free Claude.ai
> plan does not include Claude Code.**

---

## Install

The **native installer** is the one to use. It is self-contained, needs no
Node.js, and updates itself in the background.

**macOS / Linux / WSL:**
```bash
curl -fsSL https://claude.ai/install.sh | bash
```

**Windows PowerShell:**
```powershell
irm https://claude.ai/install.ps1 | iex
```

**Windows CMD:**
```batch
curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd
```

> Your prompt shows `PS C:\` in PowerShell and `C:\` without the `PS` in CMD. If
> you see `The token '&&' is not a valid statement separator`, you are in
> PowerShell but ran the CMD command. If you see `'irm' is not recognized`, the
> reverse.

<details>
<summary><strong>Other install methods</strong></summary>

| Method | Command | Auto-updates? |
| --- | --- | --- |
| **Homebrew** (macOS/Linux) | `brew install --cask claude-code` | No — `brew upgrade claude-code` |
| **WinGet** (Windows) | `winget install Anthropic.ClaudeCode` | No — `winget upgrade Anthropic.ClaudeCode` |
| **apt / dnf / apk** (Linux) | see [the docs](https://code.claude.com/docs/en/setup#install-with-linux-package-managers) | No — via your normal system upgrade |
| **npm** | `npm install -g @anthropic-ai/claude-code` | No — `npm install -g @anthropic-ai/claude-code@latest` |

**On npm:** it needs Node.js 22+, and it is the only method that does. It
installs the same native binary as the standalone installer — the binary does not
use Node at runtime. If you do not already have Node for other reasons, the
native installer is strictly less to maintain.

Never use `sudo npm install -g`. It causes permission problems and is a security
risk.

</details>

**Windows note:** install
[Git for Windows](https://git-scm.com/downloads/win) — you already need Git from
guide 1, and having it lets Claude Code use Git Bash for shell commands. Without
it, Claude Code falls back to PowerShell, which works but behaves differently.

Verify:
```bash
claude --version      # prints e.g. 2.1.211 (Claude Code)
claude doctor         # read-only diagnostics: install health, settings, warnings
```

`claude doctor` is worth knowing now rather than later. It is the first thing to
run when something is off, and it prints its findings without starting a session.

---

## Authenticate

Start it in any directory and follow the browser prompt:

```bash
claude
```

To switch accounts or re-authenticate later, type `/login` inside a running
session.

| Your situation | What to use |
| --- | --- |
| **You have a Claude subscription** (Pro, Max, Team, Enterprise) | Recommended. Log in through the browser, nothing else to configure |
| **You want to pay per token** | A [Claude Console](https://console.anthropic.com/) account with pre-paid credits. A "Claude Code" workspace is created automatically for cost tracking |
| **Your firm uses AWS / Google Cloud / Azure** | [Amazon Bedrock, Google Cloud's Agent Platform, or Microsoft Foundry](https://code.claude.com/docs/en/third-party-integrations) — often the only route approved inside a bank |
| **Your firm runs a Claude apps gateway** | `/login` opens straight on the **Cloud gateway** screen and you sign in with corporate SSO. Your admin pre-configures the URL |

That last row is worth asking about explicitly. If your firm has already deployed
Claude, there is a sanctioned path and you do not need your own subscription —
and finding that out now is much better than finding it out in Week 9.

> If `ANTHROPIC_API_KEY` is already set in your environment, Claude Code will
> prompt you to approve that key instead of opening a browser. That environment
> variable is for *Claude Code*. The `.env` file you set up in
> [guide 4](../4_Your_Model/README.md) is for *your application's* model calls.
> Two different things, and confusing them is a common early mistake.

---

## Drive it once

Do this now, in the repo you are about to clone. Ten minutes.

```bash
cd path/to/The-AI-Forward-Deployed-Engineer-Certification
claude
```

Then, in order:

1. **Ask it to explain something.** `what does this repository do?` — it reads
   files as needed; you do not attach anything.
2. **Type `/help`.** Skim the command list. You do not need to memorize it.
3. **Press `Shift+Tab` a few times.** This cycles permission modes, and the
   current mode is shown in the interface. See below.
4. **Try plan mode.** Cycle to `plan`, then ask for something substantial:
   `add a /version endpoint to the Week 1 challenge app`. It will propose an
   approach without touching a file. Read the plan. This is the mode to use when
   you do not yet trust the change.
5. **Type `/clear`** when you move to an unrelated task. Context carries over
   otherwise, and stale context is the most common cause of a confusing answer.

### Permission modes

`Shift+Tab` cycles them. This is the safety model, and it is the thing to
understand before you let an agent run shell commands.

| Mode | What it does | When |
| --- | --- | --- |
| **default** | Asks before each file change | Most of the time |
| **plan** | Proposes without editing anything | Starting something big, or working in code you do not know |
| **acceptEdits** | Auto-approves file edits | A tight loop you are watching closely |

Some accounts also have an **auto** mode, which runs a background safety check
and blocks risky actions.

### Essential commands

| Command | What it does |
| --- | --- |
| `claude` | Start an interactive session |
| `claude -p "query"` | One-off query, print, exit — useful in scripts |
| `claude -c` | Continue the most recent conversation here |
| `claude -r` | Resume a previous conversation |
| `/clear` | Clear the conversation history |
| `/login` | Switch accounts |
| `/help` | Show available commands |
| `/init` | Generate a starter `CLAUDE.md` for a project |

---

## 🔑 `CLAUDE.md` is the part that matters

Everything above is mechanics. This is the idea.

**Claude Code reads `CLAUDE.md` automatically** before it touches anything. It is
not documentation — it is configuration, in prose, and it is the highest-leverage
file in any repository you work in.

The reflex to build, and it is the whole point of Session 1's Task 5:

> **If it gets the same thing wrong twice, stop and add a line to `CLAUDE.md`
> instead of correcting it again.**

Correcting it in chat fixes this conversation. Writing it down fixes every
conversation after. In forward-deployed work — where you are handing the work to
someone else's team — that difference is the whole deliverable.

You will see this in practice immediately: the Week 1 challenge ships a
`CLAUDE.md` that puts Claude Code into **instructor mode**, so it explains and
debugs but declines to write your graded work for you. Read it before you start.
It is a working example of a `CLAUDE.md` that changes behaviour, and it is also
the reason the agent will push back when you ask it to do your homework.

---

## 🧯 If it's blocked

### `npm install -g` fails with a permission error

Do not reach for `sudo`. Use the native installer instead — it installs to your
home directory and needs no elevation.

### Your firm blocks the install URL

Try WinGet or Homebrew, which are more often allowlisted than a raw
`curl | bash`. If your firm mirrors npm internally, the npm route may work when
nothing else does.

### You cannot get a subscription approved

Check the **Claude apps gateway** and cloud-provider rows above before assuming
you are stuck — a firm that has already bought Claude through Bedrock or Foundry
has a path that does not involve you expensing anything.

If there is genuinely no approved route, use a personal account on a personal
machine for the coursework, and write the blocker into
[`use_case/ecosystem.md`](../../use_case/ecosystem.md). "Which coding agents are
approved here, and who approves them?" is a legitimate Week 9 question and you
have just found the answer early.

### It works but every request is slow or fails behind the proxy

Claude Code respects `HTTPS_PROXY` and the certificate environment variables from
[guide 1](../1_Your_Machine/README.md). If you set `REQUESTS_CA_BUNDLE` and
`SSL_CERT_FILE` there, also set `NODE_EXTRA_CA_CERTS` to the same bundle. Run
`claude doctor` after changing any of them.

---

## 📚 Worth reading

- [Claude Code documentation](https://code.claude.com/docs) — setup, workflows, settings
- [Claude Code best practices](https://www.anthropic.com/engineering/claude-code-best-practices) — Anthropic's engineering guide
- [Common workflows](https://code.claude.com/docs/en/common-workflows) — step-by-step for tasks you will actually do

---

## ➡️ Next

[**3 · Clone and run**](../3_Clone_and_Run/README.md) — get the repository and the
Week 1 app running.
