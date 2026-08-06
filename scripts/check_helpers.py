"""Every tier-2 helper must have a named consumer in the curriculum.

The failure this prevents happened twice in this repo. Helpers get written
against an imagined future week, nothing references them, and they rot -- code
with tests and no callers, which reads as maintained and is not.

The rule is NOT "a notebook must import it." Tier 2 is deliberately app-side:
the sessions teach `completion()` and `span()` from scratch, and the packaged
version is what the student's own application imports. A markdown code block
showing `from helpers.trace import Tracer` is a legitimate reference.

What is not legitimate is zero mentions anywhere. If no week teaches toward it
and no challenge asks for it, it should be deleted rather than maintained.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OK, BAD = "✓", "✗"

# Tier 1 is imported by every notebook via `from helpers import nb, ui`; it does
# not need a per-module mention.
TIER1 = {"nb", "config", "display", "ui", "__init__"}


def curriculum_text() -> list[tuple[Path, str]]:
    out = []
    for pattern in ("*/sessions/*.py", "*/challenge/*.md", "*/README.md"):
        for path in ROOT.glob(pattern):
            if "/.venv/" in path.as_posix():
                continue
            out.append((path, path.read_text("utf-8")))
    return out


def main() -> int:
    helpers = sorted(
        p.stem for p in (ROOT / "helpers").glob("*.py") if p.stem not in TIER1
    )
    if not helpers:
        print(f"{OK} no tier-2 helpers")
        return 0

    texts = curriculum_text()
    orphans = []
    for name in helpers:
        needles = (f"helpers/{name}", f"helpers.{name}", f"helpers import {name}")
        where = [p for p, body in texts if any(n in body for n in needles)]
        if not where:
            orphans.append(name)
        else:
            rels = sorted({p.relative_to(ROOT).parts[0] for p in where})
            print(f"{OK} helpers/{name}.py  ← {', '.join(rels)}")

    for name in orphans:
        print(
            f"{BAD} helpers/{name}.py is referenced by no session, challenge, or week "
            f"README.\n"
            f"  Either name its consumer -- the week that teaches toward it or the\n"
            f"  challenge that asks for it -- or delete it. A helper with tests and\n"
            f"  no callers reads as maintained and is not."
        )
    return 1 if orphans else 0


if __name__ == "__main__":
    sys.exit(main())
