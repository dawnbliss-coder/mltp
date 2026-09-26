# Implementation

Code for the tasks in `../PLAN.md`. Layout mirrors the two-person split:

- `graph_retrieval/` — Owner: Priyanka (P). Static/dynamic graph construction, signature/proof-dependency/`extends` edges, the RGCN retriever.
- `planning_closing/` — Owner: Akshith (A). M1–M5 tactic-count planners, the unified closing model, best-first search.
- `stuck_recovery/` — Owner: Akshith (A). The stuck-recovery controller (with a graph-query hook shared from `graph_retrieval/`).
- `ast_fallback/` — Owner: Akshith (A). The AST-only fallback path (Phase 5) — no graph/GNN dependency.
- `data/` — shared, gitignored. Local traced-repo output lands here; never commit it (a full Mathlib trace is many GB).
- `tests/` — unit tests that don't require a live LeanDojo trace.

## Setup

`lean_dojo` is already installed locally (verified: v4.20.0). To actually trace a repo (needed to run anything beyond the unit tests) you need:

1. A working `elan`/`lake` toolchain (already present on this machine).
2. `export GITHUB_ACCESS_TOKEN=...` if you hit GitHub API rate limits during tracing.
3. `lean_dojo.trace(LeanGitRepo(url, commit), dst_dir=...)` — **this builds the target repo's full dependency closure and can take from minutes to several hours** (the proposal's own 907-file Mathlib-core closure ran for hours on CPU). Don't kick this off on a laptop for anything beyond a tiny toy repo like `lean4-example` — use Ada for anything Mathlib-scale.

## Status

- Phase 2, Task 1 (signature-edge preprocessing): implemented in `graph_retrieval/signature_edges.py`, unit-tested in `tests/test_signature_edges.py` against LeanDojo's real `parse_goals`/`Goal`/`Declaration` types. **Not yet run against a live trace** — that requires tracing a repo first (see Setup), which is deliberately not done automatically here. See the module docstring for the exact next step once a `TracedRepo` is available.
