<div align="center">
  <img
    src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719"
    width="200"
    alt="AI Makerspace logo"
  />
  <h1>The AI Forward-Deployed Engineering Certification</h1>
  <p><strong>#FDE1 — v1.1</strong></p>
</div>

Welcome to [The AI Forward-Deployed Engineering Certification](https://maven.com/aimakerspace/ai-fde-certification).

> 🎯 **This course is built so that you engage with your own company as a
> world-class AI Forward-Deployed Engineer.** Not a sample dataset, not a demo
> use case — the actual problem you have at the actual place you work.

> [!NOTE]
> This repository is still being built out ahead of launch. Expect new notebooks
> and material to appear over the coming days. Everything you need will be here
> before each session.

---

## How this works

**10 weeks. Two sessions and one technical challenge per week.**

Each week is a directory. Inside it, `sessions/` holds the two notebooks and
`challenge/` holds that week's technical challenge.

> ### One use case, all ten weeks, no restarts
>
> You choose a problem in Week 1 and carry it the whole way. Week 2 generates
> data for it, Week 3 builds retrieval on it, Week 4 measures it, Week 8
> fine-tunes for it, and Week 10 reports on it to the people you have been
> talking to since Week 1.
>
> That work accumulates in [`use_case/`](./use_case/README.md) — your directory,
> in your fork. The most common way this cohort goes wrong is switching use cases
> halfway, so choose something you actually own and actually find annoying.

---

## The ten weeks

| Dir | Week | Sessions | Technical challenge |
| :---: | --- | --- | --- |
| [01](./01_Product_Engineering/README.md) | **1 · ☯️ Product Engineering** | Enterprise dev environment with Claude Code · The craft of AI consulting in 2026 | Enterprise FDE Challenge |
| [02](./02_Getting_to_Concreteness/README.md) | **1 · 🎯 Getting to Concreteness** | *(pre-work — no session)* | The Concreteness worksheet |
| [03](./03_Open_Weights/README.md) | **2 · 🏋️ Open Weights** | Local inference fundamentals · Synthetic data for private data | Generate synthetic data for your use case |
| [04](./04_Retrieval/README.md) | **3 · 🔍 Retrieval** | RAG, GraphRAG, agentic search, DCI, LLM Wikis · Multimodal retrieval | MVP using the right retrieval technique |
| [05](./05_Evals/README.md) | **4 · 📊 Evals** | Practical evals, back-testing, evals as shared language · Agent evals via simulation | Eval harness + 5-minute demo |
| [06](./06_Agent_Architecture/README.md) | **5 · 🧑‍💻 Agent Architecture** | Student demos with client-style critique · Tools vs. skills vs. subagents vs. MCP vs. Code Mode vs. UTCP | Refined demo, and why you chose that architecture |
| [07](./07_Guardrails/README.md) | **6 · 🛤️ Guardrails & Adversaries** | Levels of guardrails, and what each costs · Prompt injection: build the attack, then optimize it | Exploit your own app, then close it |
| [08](./08_Memory/README.md) | **7 · 🧠 Memory & Harness Engineering** | Semantic, procedural, episodic memory and how to evaluate them · Ralph loops & spec-driven development | Memory, plus evals that test memory directly |
| [09](./09_Fine_Tuning/README.md) | **8 · ⚖️ Fine-Tuning** | Fine-tuning in an open-weights world · Adding voice | Replace your closed model, pass the same harness |
| [10](./10_Infrastructure/README.md) | **9 · 🏗️ Infrastructure** | Docker, Kubernetes, Terraform, CI/CD, cloud primitives · SSO/SAML/OIDC, secrets, data boundaries | The "someone else's ecosystem" checklist, at your firm |
| [11](./11_Production/README.md) | **10 · 🏭 Production** | Observability, incident response, usage spikes · Final client readout: exec communication, scoping, pricing | Send the final report to your stakeholders |

> **Directory numbers run one ahead of week numbers from `03` on**, because Week
> 1 has two numbered directories: the Enterprise FDE Challenge and Getting to
> Concreteness are both Week 1 pre-work, delivered at enrollment. Directory `NN`
> is week `NN − 1` for `NN ≥ 03`.

---

## The stack

| | | Why |
| --- | --- | --- |
| **VS Code** | *(Zed works too)* | Where you work |
| **Claude Code** | *(Codex works too)* | The agent, and `CLAUDE.md` is how you steer it |
| **marimo** | *(not Jupyter)* | Notebooks are `.py` files — diffable, and deployable as apps |
| **uv** | *(not pixi/conda)* | One command to a working environment |
| **Gradio Server + Docker** | | Your app is an API with a disposable UI, shipped as a container |

**Gradio Server is the product; marimo is the instrument panel.** Gradio gives
you an API other things can call — which is what makes Week 5's MCP work
possible. marimo gives you notebooks that are also deployable: the eval harness
you write in Week 4 becomes a dashboard you can `marimo run` and containerize,
and the same file becomes your Week 10 observability console.

---

## Getting started

You need [uv](https://docs.astral.sh/uv/getting-started/installation/), Docker,
and Claude Code. Week 1's challenge walks through installing all three,
Windows-first.

> ### 🔑 You bring the model
>
> There is no shared class server. Bring **either** an API key from a provider
> (OpenAI, Anthropic, Azure) **or** an endpoint you can reach — your firm's
> internal gateway, a server you run, or a model on your own laptop.
>
> `.env.template` has a worked example of each. Everything routes through
> LiteLLM, so switching between them is one line and no code changes.
>
> This is deliberate. Plenty of you cannot reach `api.openai.com` from a work
> machine at all, and finding that out in Week 1 is much better than finding it
> out in Week 9.

```bash
git clone https://github.com/<YOUR_USERNAME>/The-AI-Forward-Deployed-Engineer-Certification.git
cd The-AI-Forward-Deployed-Engineer-Certification
cp .env.template .env      # add your API key
make setup
```

Open a notebook:

```bash
make nb F=01_Product_Engineering/sessions/S1_Enterprise_Dev_Environment.py
```

That runs it in its own sandboxed environment from the dependencies declared
inside the file, so it works even if you skipped `make setup`.

> **Prefer Jupyter?** Every notebook ships with an `.ipynb` next to it. Those are
> **generated** from the `.py` — read or run them freely, but make edits in the
> `.py`, or your changes will be overwritten.

---

## 🧑‍🤝‍🧑 Your team

- [Dr. Greg Loughnane](https://www.linkedin.com/in/gregloughnane/), Owner/CEO @ AI Makerspace
- [Chris Brousseau](https://www.linkedin.com/in/chris-brousseau/), Instructor — co-author of *LLMs in Production*
- [Jacob Kilpatrick](https://www.linkedin.com/in/jacobkilpatrickai/), Course Operations Lead @ AI Makerspace
- ["Coach Mark" Walker](https://www.linkedin.com/in/mark-l-walker/), Student Success Manager @ AI Makerspace

---

## 🙏 Contributions

Contributions, ideas, and feedback are welcome. Reach out to
`jacob@aimakerspace.io` with questions or suggestions.

Keep building, shipping, and sharing, and we'll do the same 🏗️🚢🚀
