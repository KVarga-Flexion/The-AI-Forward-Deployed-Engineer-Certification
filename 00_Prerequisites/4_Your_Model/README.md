# 4 · Your model

**There is no shared class server.** You bring either an API key from a provider,
or an endpoint you can reach — your firm's internal gateway, a server you run, or
a model on your own laptop.

That is deliberate, and it is not us being unhelpful. It is the actual situation
you will be in at work. An application that treats its provider as *configuration*
survives being moved; one that hardcodes a vendor SDK gets rewritten in Week 9.
Everything in this course routes through [LiteLLM](https://docs.litellm.ai/), so
switching providers is one line and no code changes.

> Plenty of you cannot reach `api.openai.com` from a work machine at all.
> **Finding that out now is much better than finding it out in Week 9.**

---

## Two `.env` files, and they are not the same

This trips people up in the first hour, so it is worth being explicit.

| File | Read by | Set up in |
| --- | --- | --- |
| `.env` at the **repo root** | Every notebook, via `helpers.nb.bootstrap()` | Here |
| `.env` inside **`01_Product_Engineering/challenge/`** | The Week 1 application only | [Guide 3](../3_Clone_and_Run/README.md) |

Set up both. They take the same values; the challenge app just carries its own
copy so it stays a self-contained thing you could hand to someone.

And a third, unrelated one: `ANTHROPIC_API_KEY` in your shell environment is for
**Claude Code**, the agent. It has nothing to do with either file above.

---

## Set it up

From the repository root:

```bash
cp .env.template .env      # copy .env.template .env    on Windows
```

Open `.env` and pick **one** option.

### Option 1 — a hosted provider, with your own key

The default, and the fastest to get working. LiteLLM picks the provider from the
model string.

```bash
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4.1-mini
```

Anthropic, or Azure OpenAI — which is the common one inside large firms:

```bash
# ANTHROPIC_API_KEY=sk-ant-...
# LLM_MODEL=anthropic/claude-sonnet-5

# AZURE_API_KEY=...
# AZURE_API_BASE=https://your-resource.openai.azure.com
# AZURE_API_VERSION=2024-10-21
# LLM_MODEL=azure/your-deployment-name
```

**Budget.** A few dollars covers the whole course on a small model. Nothing here
requires a frontier model, and `gpt-4.1-mini` is the default for that reason.

### Option 2 — an endpoint you can reach

Anything OpenAI-compatible: your firm's internal gateway, vLLM, LM Studio,
llama.cpp, or a colleague's server. Prefix the model with `openai/` so LiteLLM
uses the OpenAI-compatible path, and set the base URL.

```bash
OPENAI_API_KEY=EMPTY
LLM_MODEL=openai/your-model-name
LLM_API_BASE=http://your-server:8000/v1
```

**If your firm has an internal gateway, use it.** It is the most realistic setup
in this course, it is usually already approved, and it means your coursework runs
where your real work would.

### Option 3 — a model on your own laptop

No key you have to buy, no network, nothing leaves the machine. **Do this one at
least once**, even if you also have an API key — several later sessions are
about what the local path gives you that a hosted API cannot, and they land much
harder if you have actually served a model yourself.

#### Unsloth Studio (recommended)

A no-code UI that runs GGUF models and exposes an **OpenAI-compatible endpoint**,
which is exactly what the rest of this course talks to.

**macOS / Linux / WSL:**
```bash
curl -fsSL https://unsloth.ai/install.sh | sh
```
**Windows (PowerShell):**
```powershell
irm https://unsloth.ai/install.ps1 | iex
```

Then start the UI and open <http://127.0.0.1:8888>:

```bash
unsloth studio -p 8888
```

You will be asked to set a password on first launch. Pick a model in the UI, then
create a key under **Settings → API** — every key starts with `sk-unsloth-`.

Point your `.env` at it:

```bash
OPENAI_API_KEY=sk-unsloth-...          # from Settings → API
LLM_MODEL=openai/<the model id>        # see below
LLM_API_BASE=http://localhost:8888/v1
```

The `openai/` prefix tells LiteLLM to use the OpenAI-compatible path. To get the
exact model id the server expects:

```bash
curl http://localhost:8888/v1/models -H "Authorization: Bearer sk-unsloth-..."
```

Use the `id` from the response. You can also serve a model without the UI:

```bash
unsloth run --model unsloth/gemma-4-26B-A4B-it-GGUF:UD-Q4_K_XL
```

which prints its endpoint URL and key to the console.

> **No GPU needed.** Unsloth Studio runs GGUF models on CPU across macOS,
> Windows, Linux and WSL. A GPU makes it faster; it is not a requirement for
> chat. Note that Unsloth's own Windows *install* page lists an NVIDIA GPU under
> prerequisites while its chat page says no GPU is required — that requirement is
> about training, not inference. If a CPU-only Windows install gives you trouble,
> use Ollama below and record it.
>
> **Python 3.11–3.13.** Unsloth Studio manages its own environment, so this does
> not have to be the same interpreter as the rest of the course.

#### Ollama (the smaller alternative)

Fewer moving parts, no UI, no key.

```bash
LLM_MODEL=ollama/llama3.2
LLM_API_BASE=http://localhost:11434
```

Install [Ollama](https://ollama.com/download), then:

```bash
ollama pull llama3.2
ollama serve
```

---

## Check it works

```bash
make nb F=01_Product_Engineering/sessions/S1_Enterprise_Dev_Environment.py
```

The setup cell prints `✅ model: <whatever you configured>`. Task 4 sends one
real message, behind a button so it does not fire on open.

Or just use the app from [guide 3](../3_Clone_and_Run/README.md): restart
`python app.py` and send a message. If it answers, you are done.

---

## 🧯 If it's blocked

### `api.openai.com` is unreachable

Expected on plenty of corporate networks, and it is a finding, not a failure.
Session 1 measures exactly which hosts you can reach and produces a table to put
in front of an infrastructure team.

In order of preference:

1. **Ask whether your firm has an internal LLM gateway.** Most large firms now
   do, and it is Option 2 above. This is the best outcome — it is approved,
   it is realistic, and it is the answer Week 9 wants anyway.
2. **Azure OpenAI**, if your firm is a Microsoft shop. Frequently allowed where
   `api.openai.com` is not, because it is inside the tenant.
3. **Ollama on your own machine** (Option 3). No network needed at all.

### TLS certificate errors when calling the API

Your firm is intercepting TLS. Set the CA bundle variables from
[guide 1](../1_Your_Machine/README.md) — `REQUESTS_CA_BUNDLE` and `SSL_CERT_FILE`
— and they will apply here too.

### It worked yesterday and stopped today

Check your credit balance before you debug anything else. A `401` with an
otherwise-correct key is almost always an exhausted balance or a rotated key.

### You have no key and no gateway and cannot install Ollama

Do [Getting to Concreteness](https://bit.ly/fde-concreteness)
while you sort it out. It needs no model, no tooling, and no network, and it is
the input to every other week. Then come back.

---

## ➡️ Next

[**5 · Your notebooks**](../5_Your_Notebooks/README.md) — marimo installed, one
session open, and the reactive rules that trip up Jupyter users.
