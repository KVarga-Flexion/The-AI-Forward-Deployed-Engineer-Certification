# Evals

## `golden.jsonl`

Five examples, written by hand, in Week 1 Session 2. Five — not fifty, and not
generated.

Each line is one object:

```json
{"input": "...", "output": "...", "why": "what makes this the right answer"}
```

The `why` field is the one that earns its keep. In Week 4 you calibrate an
LLM judge against these, and "why" is what you calibrate it on.

### Why you write these by hand

They are the fixed point of the whole cohort. A model-generated example encodes
what the model already does; a hand-written one encodes what *you* would accept,
which is the only thing worth measuring against.

| Week | What uses this file |
| --- | --- |
| 2 | Seeds for synthetic data generation — your variation axes come from these. |
| 4 | The eval harness scores against them, and the judge is calibrated on them. |
| 6 | Injection regressions get added alongside them. |
| 8 | **The bar.** A fine-tuned open model has to pass the same harness the closed one did. |

Get them wrong now and every number for the next nine weeks is measuring the
wrong thing.

### Writing good ones

- Use **real inputs** from your work, with names and identifiers removed.
- Write the output you would **actually accept**, not an idealized one.
- Include at least one **edge case** and one where the right answer is *"I don't
  know"* or *"escalate this"*. A system that never declines is not calibrated.
- Keep them short enough to read in full during review.
