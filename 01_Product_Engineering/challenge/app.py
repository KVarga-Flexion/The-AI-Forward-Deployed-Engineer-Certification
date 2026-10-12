"""The server.

`gradio.Server` is a FastAPI app with Gradio's API engine bolted in. You get
queueing, streaming, and MCP for free, but you bring your own frontend. That
split is the point: the API is the product, the UI is disposable.
"""

import json
import os
from pathlib import Path

from fastapi.responses import HTMLResponse
from gradio import Server
from pydantic import ValidationError

from llm import stream_reply
from pathfinder import NO_SCORE_SUMMARY, solve
from schema import Request, Response

app = Server()

FRONTEND = Path(__file__).parent / "frontend" / "index.html"
SAMPLE = Path(__file__).parent / "data" / "sample.json"


# --- The API -----------------------------------------------------------------
# The `-> str` return annotation is REQUIRED. Without it Gradio infers zero
# output components and silently returns nothing. Ask us how we know.


@app.api(name="chat")
def chat(message: str, history: list | None = None) -> str:
    """Stream a reply to one user message."""
    yield from stream_reply(message, history)


@app.api(name="compare_skills_to_role")
def compare_skills_to_role(
    role: str,
    required_skills: list,
    self_ratings: list,
    trainings: list | None = None,
) -> str:
    """Compare a trail worker's self-rated skills to one trail role and name up to three next steps.

    Every required skill comes back as has, close (exactly one level below) or
    missing (two levels below, or not rated), in that order. Next steps are only
    trainings from the given catalog whose approved skill alignment matches the
    gap's category and skill at or above the required level; close gaps come
    first, then free, then cheaper. Skills with no matching training are listed,
    not papered over. An unknown skill or a category mismatch returns
    needs_review=true and nothing else. No percentages; nothing is recorded.

    Args:
        role: The role name from the role library, e.g. "Trail Crew Leader".
        required_skills: The role's required skills, each {"category", "skill", "required_level"}. Levels are "Entry", "Full Performance" or "Expert"; category and skill use exact framework names.
        self_ratings: Her rating per skill, each {"category", "skill", "level"}; level null means not claimed yet.
        trainings: The catalog slice, each {"title", "skills_taught": [required skill], "cost_usd", "proves", "alignment_approved"}.

    Returns:
        A JSON-encoded Response: gaps, next_steps, no_training_for, summary, needs_review, review_reason.
    """
    try:
        request = Request(
            role=role,
            required_skills=required_skills,
            self_ratings=self_ratings,
            trainings=trainings or [],
        )
    except ValidationError as exc:
        # Malformed input is a no-answer, not a crash: say why and route to manual.
        first = exc.errors()[0]
        where = ".".join(str(part) for part in first["loc"])
        return Response(
            gaps=[],
            summary=NO_SCORE_SUMMARY,
            needs_review=True,
            review_reason=f"Invalid request ({exc.error_count()} problem(s)); first: {where}: {first['msg']}",
        ).model_dump_json()
    return solve(request).model_dump_json()


# --- The frontend ------------------------------------------------------------
# Defining a route at "/" replaces Gradio's default UI with ours.


@app.get("/", response_class=HTMLResponse)
def homepage() -> str:
    return FRONTEND.read_text(encoding="utf-8")


@app.get("/sample")
def sample() -> dict:
    """Synthetic roles and trainings for the UI. Week 3 replaces this with retrieval."""
    return json.loads(SAMPLE.read_text(encoding="utf-8"))


@app.get("/health")
def health() -> dict:
    """Your future ops team will thank you. Load balancers need this."""
    return {"status": "ok", "model": os.getenv("LLM_MODEL", "gpt-4.1-mini")}


if __name__ == "__main__":
    # 0.0.0.0 so the container is reachable from the host. On your laptop this
    # is fine. On a firm network, "reachable from where, exactly?" is the
    # question this challenge wants you to go ask.
    #
    # Read the port rather than hardcoding it, so a machine that already has
    # something on 7860 can move this one without editing code.
    port = int(os.getenv("GRADIO_SERVER_PORT", "7860"))

    # Gradio announces the address it BOUND to, which is 0.0.0.0 -- not an
    # address a browser can open. Windows rejects it outright; macOS and Linux
    # quietly redirect it to localhost, which is why it looks fine on some
    # machines and broken on others. Print the one that always works.
    print(f"\n  Open http://localhost:{port} in your browser\n", flush=True)
    app.launch(server_name="0.0.0.0", server_port=port)
