"""The model call.

One function, one job: take a conversation, stream back the assistant's reply.

Everything provider-specific lives in environment variables, so switching from
OpenAI to Azure to a self-hosted model is a config change, not a code change.
That property matters more than it looks like it does right now -- see the
"Where does this live?" section of the README.
"""

import json
import os

import litellm
from litellm import completion

# litellm prints a "Provider List" banner on every call with a custom model
# name. Noise only; the calls succeed. Silence it.
litellm.suppress_debug_info = True

# LiteLLM picks the provider from the model string:
#   "gpt-4.1-mini"                    -> OpenAI
#   "azure/my-deployment"             -> Azure OpenAI
#   "anthropic/claude-sonnet-5"       -> Anthropic
#   "ollama/llama3.2"                 -> a model running on your laptop
#   "openai/my-model" + LLM_API_BASE  -> any OpenAI-compatible server (vLLM, LM Studio, ...)
MODEL = os.getenv("LLM_MODEL", "gpt-4.1-mini")
API_BASE = os.getenv("LLM_API_BASE")  # only needed for self-hosted / gateway endpoints
EXTRA_HEADERS = json.loads(os.getenv("LLM_EXTRA_HEADERS") or "{}")

SYSTEM_PROMPT = os.getenv(
    "SYSTEM_PROMPT",
    "You are a helpful assistant. Be concise and concrete.",
)


def stream_reply(message: str, history: list[dict] | None = None):
    """Yield the assistant's reply as it arrives, one growing string at a time.

    `history` is a list of {"role": ..., "content": ...} dicts. We rebuild the
    full message list on every turn -- the model is stateless, so the
    conversation only exists because we keep sending it.
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history or [])
    messages.append({"role": "user", "content": message})

    kwargs = {"model": MODEL, "messages": messages, "stream": True}
    if API_BASE:
        kwargs["api_base"] = API_BASE
    if EXTRA_HEADERS:
        kwargs["extra_headers"] = EXTRA_HEADERS

    reply = ""
    for chunk in completion(**kwargs):
        piece = chunk.choices[0].delta.content
        if piece:
            reply += piece
            yield reply


def complete(prompt: str, *, system: str | None = None, timeout: float = 20) -> str:
    """Return one whole reply, no streaming, or raise.

    For callers that need the full text before they can check it (pathfinder
    validates every line). The explicit timeout is the point: without one a
    slow provider hangs the request, and the caller's template fallback never
    gets its chance (BR-10.7).
    """
    messages = [{"role": "system", "content": system}] if system else []
    messages.append({"role": "user", "content": prompt})

    kwargs = {"model": MODEL, "messages": messages, "timeout": timeout}
    if API_BASE:
        kwargs["api_base"] = API_BASE
    if EXTRA_HEADERS:
        kwargs["extra_headers"] = EXTRA_HEADERS

    content = completion(**kwargs).choices[0].message.content
    if not content:
        raise ValueError("model returned an empty reply")
    return content
