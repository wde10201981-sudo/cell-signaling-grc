# Cell Signaling GRC

This repository is the isolated, fresh-start prototype for the Cell Signaling GRC framework.

## Purpose

This project models one GRC cell with layered internal state, explicit relationships, and a signal-driven event system. It is intentionally small and deterministic, with no external dependencies and no real production integrations.

## Architecture

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
