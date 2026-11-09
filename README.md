# Cell Signaling GRC

This repository is the isolated, fresh-start prototype for the Cell Signaling GRC framework.

## Purpose

This project models one GRC cell with layered internal state, explicit relationships, and a signal-driven event system. It is intentionally small and deterministic, with no external dependencies and no real production integrations.

## Framework specification — draft for review

The proposed framework defines a common six-layer cell structure, specialized cell profiles, a versioned inter-cell signal contract, and evidence-bound AI analysis with explicit decision authority. Homeostasis is a core design requirement: cells detect deviations from authorized conditions, coordinate responses, and verify recovery through fresh evidence. This is architecture work, not an end-user application.

- [Framework foundation](docs/FRAMEWORK.md) — minimum valid cell, layer information, relationships, signal handling, AI analysis and decision boundaries.
- [Contrasting cell profiles](docs/CELL-PROFILES.md) — security assurance and identity operations, a worked exchange, and proposed acceptance cases.

The full specification remains forward-looking. A bounded two-cell exercise now tests scope, cycle timing and evidence withdrawal alongside the original skeleton. AI, authenticated transport and production approvals remain unimplemented.

## Implemented skeleton

- One GRC cell with layered records
- Explicit relationships between records
- A signal bus that routes events through the cell
- A first synthetic demo: requirement-change impact assessment

## Folder structure

- `cell_signaling/` — framework skeleton and tests
- `README.md` — project overview

## Run the demo

```bash
python -m cell_signaling.demo
```

## Run the tests

```bash
python -m unittest discover -s cell_signaling -p 'test_*.py' -v
```


## Two-cell coverage exercise

```bash
python -m cell_signaling.coverage_demo
```

No Ollama server is needed. See [contract and limits](docs/COVERAGE-EXERCISE.md).


## Assessment contract (backend only)

The first model-independent assessment contract defines scoped input packets,
per-population control-fit/implementation/execution judgments, a separate challenge
role, and failure/staleness handling. No model is connected yet.

```bash
python -m cell_signaling.assessment_demo
```

This uses four authored synthetic cases, not AI output. See
[assessment contract and limits](docs/ASSESSMENT-CONTRACT.md).
