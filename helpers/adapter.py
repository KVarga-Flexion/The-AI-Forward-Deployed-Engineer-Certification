"""The card that has to travel with a LoRA adapter.

Tier 2 by convention. Standard library only.

Week 8 trains an adapter and proves it passes the Week 4 harness. That is the
engineering. This is what makes it *shippable inside a firm*, and it is two
things engineers reliably skip.

**An adapter is a diff against one specific base model.** Load it onto a
different base — or the same name at a different revision, which is the one that
actually happens — and nothing errors. The shapes line up, the weights add, and
the model produces fluent, subtly wrong output forever. There is no exception to
catch and no log line to find. `verify_base()` is a cheap check against the base
model's own `config.json` that turns that into a loud failure at load time.

**Somebody will ask what it was trained on.** In a regulated firm that question
arrives from model risk, procurement, or an auditor, usually months later and
never with warning. A card written at training time costs a minute. Reconstructed
a quarter later from memory and shell history, it costs a week and is wrong.

The licence field is not decoration either: **an adapter inherits the base
model's terms.** Fine-tuning a model whose licence restricts commercial use does
not produce a model you may use commercially.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, asdict
from pathlib import Path


def fingerprint_file(path: str | Path, chunk: int = 1 << 20) -> str:
    """SHA-256 of a file, so "the same dataset" is checkable rather than asserted."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while block := handle.read(chunk):
            digest.update(block)
    return digest.hexdigest()[:32]


@dataclass
class AdapterCard:
    """What travels with the weights.

        card = AdapterCard(
            name="warehouse-triage-v3",
            base_model="Qwen/Qwen3-1.7B",
            base_licence="apache-2.0",
            rank=8, alpha=16,
            target_modules=["q_proj", "v_proj"],
        )
        card.record_data("use_case/data/train.jsonl", rows=1840)
        card.record_eval(baseline=0.71, candidate=0.88, harness="use_case/evals")
        card.save("adapters/warehouse-triage-v3/card.json")
    """

    name: str
    base_model: str
    base_licence: str = ""
    base_revision: str = ""

    rank: int = 0
    alpha: int = 0
    target_modules: list = field(default_factory=list)

    # Geometry of the base, recorded so a mismatch is catchable later.
    base_layers: int = 0
    base_hidden: int = 0
    base_architecture: str = ""

    data_path: str = ""
    data_rows: int = 0
    data_sha256: str = ""
    data_notes: str = ""

    eval_harness: str = ""
    eval_baseline: float | None = None
    eval_candidate: float | None = None

    trained_at: str = ""
    notes: str = ""

    # -- filling it in -----------------------------------------------------

    def record_base(self, config_path: str | Path) -> "AdapterCard":
        """Copy the base geometry out of its config.json at training time."""
        cfg = json.loads(Path(config_path).read_text("utf-8"))
        if "text_config" in cfg and "num_hidden_layers" not in cfg:
            cfg = {**cfg, **cfg["text_config"]}
        self.base_layers = int(cfg.get("num_hidden_layers") or 0)
        self.base_hidden = int(cfg.get("hidden_size") or 0)
        arch = cfg.get("architectures") or []
        self.base_architecture = str(arch[0]) if arch else ""
        return self

    def record_data(self, path: str | Path, *, rows: int = 0, notes: str = "") -> "AdapterCard":
        self.data_path = str(path)
        self.data_rows = rows
        self.data_notes = notes
        try:
            self.data_sha256 = fingerprint_file(path)
        except OSError:
            self.data_sha256 = ""
        return self

    def record_eval(self, *, baseline: float | None = None,
                    candidate: float | None = None, harness: str = "") -> "AdapterCard":
        self.eval_baseline = baseline
        self.eval_candidate = candidate
        self.eval_harness = harness
        return self

    # -- the checks that earn its keep -------------------------------------

    @property
    def improvement(self) -> float | None:
        if self.eval_baseline is None or self.eval_candidate is None:
            return None
        return self.eval_candidate - self.eval_baseline

    def verify_base(self, config_path: str | Path) -> tuple[bool, str]:
        """Is this the base this adapter was trained against?

        Compares architecture, layer count and hidden size. A mismatch here is
        the difference between an error at load time and a model that is quietly
        wrong in production for a quarter.
        """
        if not self.base_layers and not self.base_hidden:
            return False, (
                "this card never recorded the base geometry, so nothing can be "
                "verified — call record_base() at training time, not now"
            )
        other = AdapterCard(name="", base_model="").record_base(config_path)
        problems = []
        if self.base_architecture and other.base_architecture != self.base_architecture:
            problems.append(
                f"architecture {other.base_architecture!r} != {self.base_architecture!r}"
            )
        if other.base_layers != self.base_layers:
            problems.append(f"layers {other.base_layers} != {self.base_layers}")
        if other.base_hidden != self.base_hidden:
            problems.append(f"hidden {other.base_hidden} != {self.base_hidden}")
        if problems:
            return False, (
                f"base model mismatch for adapter {self.name!r}: "
                + "; ".join(problems)
                + ". Serving an adapter on the wrong base does not raise — it "
                  "produces fluent, subtly wrong output. Refusing to load."
            )
        return True, f"base matches {self.base_model}"

    def gaps(self) -> list[str]:
        """What a reviewer will ask for that is not filled in."""
        missing = []
        if not self.base_licence:
            missing.append("base_licence — an adapter inherits the base model's terms")
        if not self.data_sha256:
            missing.append("data_sha256 — 'the same dataset' has to be checkable")
        if self.eval_candidate is None:
            missing.append("eval_candidate — an untested adapter is not a deliverable")
        if self.eval_baseline is None:
            missing.append("eval_baseline — better than what?")
        if not self.base_layers:
            missing.append("base geometry — call record_base()")
        return missing

    # -- persistence -------------------------------------------------------

    def save(self, path: str | Path) -> Path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(asdict(self), indent=2) + "\n", encoding="utf-8")
        return target

    @classmethod
    def load(cls, path: str | Path) -> "AdapterCard":
        return cls(**json.loads(Path(path).read_text("utf-8")))

    def __str__(self) -> str:
        delta = self.improvement
        score = (
            f"{self.eval_baseline:.3f} → {self.eval_candidate:.3f} ({delta:+.3f})"
            if delta is not None else "unevaluated"
        )
        gaps = self.gaps()
        return (
            f"{self.name} · base {self.base_model} ({self.base_licence or 'licence UNKNOWN'}) "
            f"· r={self.rank} α={self.alpha} · {self.data_rows} rows · {score}"
            + (f" · ⚠️ {len(gaps)} gap(s)" if gaps else "")
        )
