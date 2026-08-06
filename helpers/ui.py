"""Small notebook affordances: progress, and tables that don't need pandas.

Tier 1: stdlib + marimo only. `table()` deliberately takes plain dicts rather than a
DataFrame, so a notebook can show results without pulling pandas into its sandbox.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Sequence
from contextlib import contextmanager
from typing import Any


@contextmanager
def spinner(label: str = "Working..."):
    """Show a spinner while a slow block runs.

        with spinner("Embedding 400 chunks..."):
            vectors = embed(chunks)
    """
    import marimo as mo

    with mo.status.spinner(title=label):
        yield


def track(items: Sequence[Any], label: str = "") -> Iterator[Any]:
    """Iterate with a progress bar. Needs a sequence, not a bare generator."""
    import marimo as mo

    with mo.status.progress_bar(total=len(items), title=label) as bar:
        for item in items:
            yield item
            bar.update()


def table(rows: Iterable[dict], *, title: str = "") -> Any:
    """Render a list of dicts as a markdown table.

    Column order follows first appearance across the rows, so the first dict's keys
    lead and any later additions get appended rather than silently dropped.
    """
    import marimo as mo

    rows = list(rows)
    if not rows:
        return mo.md(f"**{title}**\n\n_(no rows)_" if title else "_(no rows)_")

    columns: list[str] = []
    for row in rows:
        for key in row:
            if key not in columns:
                columns.append(key)

    def cell(value: Any) -> str:
        return "" if value is None else str(value).replace("|", r"\|")

    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    lines += [
        "| " + " | ".join(cell(row.get(col)) for col in columns) + " |" for row in rows
    ]

    body = "\n".join(lines)
    return mo.md(f"**{title}**\n\n{body}" if title else body)
