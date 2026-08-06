"""Actually run both formats. The mirror gate only proves they are byte-identical.

`scripts/mirrors.py` re-exports every `.py` and byte-compares it to the committed
`.ipynb`. That catches drift and nothing else: a notebook that raises on cell
three exports identically to one that works.

This runs them.

  --py     execute the marimo .py    (via `marimo export ipynb --include-outputs`)
  --ipynb  execute the mirror        (via nbclient, a real Jupyter kernel)

Guarded cells are expected to halt. Every expensive cell in this curriculum sits
behind `mo.ui.run_button` + `mo.stop(...)`, and in marimo `mo.stop` raises a
`MarimoStopError` that the runtime catches. A plain Jupyter kernel has nothing to
catch it, so the same guard surfaces as an uncaught exception and stops "Run
All". That is reported separately from a real failure, because it is a property
of the export format rather than a bug in the notebook.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OK, BAD, WARN = "✓", "✗", "!"
# Both mean "a guard upstream fired", not "the notebook is broken".
GUARDS = ("MarimoStopError", "ancestor-stopped")


def is_notebook(path: Path) -> bool:
    """`sessions/` also holds plain scripts -- the MCP server in Week 5, for one.
    Only marimo notebooks have an App, and only they can be exported."""
    try:
        return "app = marimo.App(" in path.read_text("utf-8")
    except OSError:
        return False


def notebooks(targets: list[str] | None) -> list[Path]:
    if targets:
        out: list[Path] = []
        for t in targets:
            p = Path(t)
            p = (p if p.is_absolute() else ROOT / p).resolve()
            out.extend(sorted(p.glob("**/sessions/*.py")) if p.is_dir() else [p])
        # An explicitly named file is checked even so; a directory sweep is filtered.
        return [p for p in out if p.suffix == ".py" and is_notebook(p)]
    return [p for p in sorted(ROOT.glob("*/sessions/*.py")) if is_notebook(p)]


def errors_in(nb: dict) -> list[tuple[int, str, str]]:
    out = []
    for i, cell in enumerate(nb.get("cells", [])):
        for o in cell.get("outputs", []):
            if o.get("output_type") == "error":
                out.append((i, o.get("ename", "?"), str(o.get("evalue", ""))[:160]))
    return out


def run_py(path: Path, timeout: int) -> tuple[str, list]:
    """Execute the marimo notebook and report any cell that errored."""
    with tempfile.TemporaryDirectory() as tmp:
        dest = Path(tmp) / "out.ipynb"
        try:
            proc = subprocess.run(
                [sys.executable, "-m", "marimo", "export", "ipynb",
                 "--include-outputs", str(path), "-o", str(dest), "-f"],
                capture_output=True, text=True, timeout=timeout, cwd=ROOT,
            )
        except subprocess.TimeoutExpired:
            return "timeout", [(-1, "Timeout", f"exceeded {timeout}s")]
        if not dest.exists():
            return "failed", [(-1, "ExportFailed", (proc.stderr or proc.stdout)[-300:])]
        return "ok", errors_in(json.loads(dest.read_text("utf-8")))


def run_ipynb(path: Path, timeout: int) -> tuple[str, list]:
    """Execute the mirror in a real Jupyter kernel."""
    try:
        import nbformat
        from nbclient import NotebookClient
    except ModuleNotFoundError:
        return "skipped", [(-1, "MissingDep", "uv sync --group dev")]

    nb = nbformat.read(path, as_version=4)
    client = NotebookClient(
        nb, timeout=timeout, kernel_name="python3", allow_errors=True,
        resources={"metadata": {"path": str(path.parent)}},
    )
    try:
        client.execute()
    except Exception as exc:
        return "failed", [(-1, type(exc).__name__, str(exc)[:200])]
    return "ok", errors_in(nb)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("targets", nargs="*")
    ap.add_argument("--py", action="store_true")
    ap.add_argument("--ipynb", action="store_true")
    ap.add_argument("--timeout", type=int, default=420)
    args = ap.parse_args()
    do_py = args.py or not args.ipynb
    do_ipynb = args.ipynb or not args.py

    failures = 0
    for path in notebooks(args.targets):
        rel = path.relative_to(ROOT)
        for label, fn, enabled, target in (
            ("py   ", run_py, do_py, path),
            ("ipynb", run_ipynb, do_ipynb, path.with_suffix(".ipynb")),
        ):
            if not enabled:
                continue
            if not target.exists():
                print(f"{BAD} {label} {rel}  -- missing")
                failures += 1
                continue
            status, errs = fn(target, args.timeout)
            guards = [e for e in errs if e[1] in GUARDS]
            # In Jupyter a guard raises instead of halting, so the variables that
            # cell would have defined never exist and every dependent cell dies
            # with NameError. That is the guard working, one format removed --
            # not a broken notebook. Only count NameErrors that appear BEFORE
            # any guard fired, which are the real ones.
            first_guard = min((e[0] for e in guards), default=None)
            cascade = [
                e for e in errs
                if e[1] == "NameError" and first_guard is not None and e[0] > first_guard
            ]
            real = [e for e in errs if e[1] not in GUARDS and e not in cascade]
            if status != "ok":
                print(f"{BAD} {label} {rel}  -- {status}: {errs[0][2] if errs else ''}")
                failures += 1
            elif real:
                print(f"{BAD} {label} {rel}  -- {len(real)} error(s)")
                for i, name, val in real[:3]:
                    print(f"      cell {i}: {name}: {val}")
                failures += 1
            elif guards or cascade:
                tail = f", {len(cascade)} dependent cell(s) cascaded" if cascade else ""
                print(f"{WARN} {label} {rel}  -- ran; "
                      f"{len(guards)} guarded cell(s) halted{tail}")
            else:
                print(f"{OK} {label} {rel}")
    if failures:
        print(f"\n{BAD} {failures} execution failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
