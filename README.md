# Cell Signaling GRC

This repository is the isolated, fresh-start prototype for the Cell Signaling GRC framework.

## Purpose

This project models one GRC cell with layered internal state, explicit relationships, and a signal-driven event system. It is intentionally small and deterministic, with no external dependencies and no real production integrations.

## Framework specification — draft for review

The proposed framework defines a common six-layer cell structure, specialized cell profiles, a versioned inter-cell signal contract, and evidence-bound AI analysis with explicit decision authority. This is architecture work, not an end-user application.

- [Framework foundation](docs/FRAMEWORK.md) — minimum valid cell, layer information, relationships, signal handling, AI analysis and decision boundaries.
- [Contrasting cell profiles](docs/CELL-PROFILES.md) — security assurance and identity operations, a worked exchange, and proposed acceptance cases.

The specification is forward-looking. The Python code below remains the original single-cell deterministic skeleton; the new contracts and AI behaviors are not implemented yet.

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
