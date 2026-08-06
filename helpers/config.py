"""What a notebook needs to know about where it is and which model to call.

Tier 1: stdlib + python-dotenv only. Nothing here may import litellm, numpy, or
anything else heavy — every notebook imports this, including the ones running in a
minimal sandbox.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    """Paths and model settings, resolved once per notebook."""

    root: Path          # repo root — the directory holding pyproject.toml
    data: Path          # our instructional corpus
    use_case: Path      # the student's own work; the through-line

    llm_model: str
    api_base: str | None
    embed_model: str
    embed_api_base: str | None

    def kwargs(self) -> dict:
        """LiteLLM kwargs for this config. Spread into completion(**cfg.kwargs())."""
        out = {"model": self.llm_model}
        if self.api_base:
            out["api_base"] = self.api_base
        return out

    def embed_kwargs(self) -> dict:
        """LiteLLM kwargs for embeddings.

        Separate from `kwargs()` because the embedding endpoint is often a
        different host from the chat one — a firm may serve embeddings locally
        while chat goes through a gateway, or the reverse.
        """
        out = {"model": self.embed_model}
        if self.embed_api_base:
            out["api_base"] = self.embed_api_base
        return out

    def __str__(self) -> str:
        where = f" @ {self.api_base}" if self.api_base else ""
        return f"{self.llm_model}{where}"


def from_env(root: Path) -> Config:
    return Config(
        root=root,
        data=root / "data",
        use_case=root / "use_case",
        llm_model=os.getenv("LLM_MODEL", "gpt-4.1-mini"),
        api_base=os.getenv("LLM_API_BASE"),
        embed_model=os.getenv("EMBED_MODEL", "text-embedding-3-small"),
        # Falls back to the chat endpoint, which is right for hosted providers
        # and for most single-gateway setups.
        embed_api_base=os.getenv("EMBED_API_BASE") or os.getenv("LLM_API_BASE"),
    )
