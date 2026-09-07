# Project Plan — KG-Augmented Premise Retrieval for Lean 4

Team: Priyanka Agarwal, Akshith
Legend: **[Done]** = task fully completed. **[WIP]** = currently being worked on (should be checked by whoever is actively on it; uncheck when you pause).

> Assign an owner (P / A / Both) in brackets as you pick up a task. Update the two checkboxes as work progresses — don't leave both ticked and abandon a task.

---

## Phase 0 — Literature Review (read before implementing the related component)

Core paper being reproduced/extended:

- [ ] Done   [ ] WIP — **Petrovčič et al. 2025**, "Combining textual and structural information for premise selection in Lean" (arXiv:2510.23637) — read in full, understand RGCN + text-embedding fusion, tagging modes (`all_dojo` vs 3-relation scheme). *[Owner: ]*
- [ ] Done   [ ] WIP — **Yang et al. 2023**, LeanDojo (arXiv:2306.15626) — understand trace extraction, `get_premise_definitions`, `get_annotated_tactic` APIs, ReProver baseline. *[Owner: ]*

Graph-representation lineage (needed for the multi-hop / extends-edge extension, Section 3.2):

- [ ] Done   [ ] WIP — **Kurgan et al. 2026**, TheoremGraph / LeanGraph (arXiv:2606.25363) — six-edge-type declaration graph (`extends, field, sig, proof, def, docref`); needed to design the `extends`/class-inheritance edges. *[Owner: ]*
- [ ] Done   [ ] WIP — **Paliwal et al. 2020**, Graph representations for higher-order logic (AAAI) — HOList/HOL Light graph encoder lineage. *[Owner: ]*
- [ ] Done   [ ] WIP — **Wang et al. 2017**, Premise selection by deep graph embedding (arXiv:1709.09994). *[Owner: ]*
- [ ] Done   [ ] WIP — **Aniva et al. 2026**, Nazrin / ExprGraph (arXiv:2602.18767) — expression-level GNN, atomic tactic set; relevant contrast case, not directly reused. *[Owner: ]*
- [ ] Done   [ ] WIP — **Blaauwbroek et al. 2024**, Graph2Tac (ICML) — online graph representation learning for Coq; relevant to the "future work" note on static-graph limitation. *[Owner: ]*

Retrieval baselines / ceiling:

- [ ] Done   [ ] WIP — **Mikuła et al. 2023**, Magnushammer (arXiv:2303.04488) — contrastive transformer retriever, the no-graph ceiling to beat. *[Owner: ]*
- [ ] Done   [ ] WIP — **Alemi et al. 2016**, DeepMath (NeurIPS). *[Owner: ]*

Classical premise selection (background/related work section only):

- [ ] Done   [ ] WIP — Meng & Paulson 2009 (MePo), Hoder & Voronkov 2011 (SInE), Böhme & Nipkow 2010 (Sledgehammer), Kühlwein et al. 2013 (MaSh) — skim for related-work framing. *[Owner: ]*

Stuck-recovery contrast:

- [ ] Done   [ ] WIP — **arXiv:2606.04883**, control-plane/data-plane cost-quality agent for Lean — read to make sure our controller is clearly differentiated (Section 3.4 claim). *[Owner: ]*

Background needed but not cited (find + read):

- [ ] Done   [ ] WIP — Find and read the original **RGCN** paper (Schlichtkrull et al., relational GCN) — needed to actually implement/modify the relation-aware GNN. *[Owner: ]*
- [ ] Done   [ ] WIP — Find and read the **ByT5** paper — the pretrained encoder used inside `PremiseRetriever`. *[Owner: ]*

---

## Phase 1 — Environment & Reproduction Setup

- [X] Done   [ ] WIP — Clone Petrovčič et al. reference implementation.
- [X] Done   [ ] WIP — Patch missing GPU-only `deepspeed` dependency to run CPU-only.
- [X] Done   [ ] WIP — Fix C++ extension that failed to compile against local macOS SDK.
- [X] Done   [ ] WIP — Fix Python path resolution issue.
- [X] Done   [ ] WIP — Write the missing preprocessing step (premise tagging with signature/proof provenance) using LeanDojo's `get_premise_definitions` + `get_annotated_tactic`, feed into `all_dojo` tagging mode.
- [X] Done   [ ] WIP — Run end-to-end on reduced corpus (4 files, `lean4-example`, 1,030 premises, 166 edges) and hand-verify ground-truth labels (`hello_world`, `foo`).
- [ ] Done   [ ] WIP — Finish the full 907-file / 19,239-premise closure run (was still running after several hours on CPU at proposal time) — get it to completion, sanity-check output size/shape. *[Owner: ]*
- [ ] Done   [ ] WIP — Verify the two edges (`Nat.add_comm`, `Nat.add_assoc`) plus a wider random sample at scale (not just the two touching example theorems). *[Owner: ]*

---

## Phase 2 — Close the Gaps Left Open by the Preliminary Trial

- [ ] Done   [ ] WIP — Reverse-engineer / reimplement the missing **signature-edge** preprocessing (which premises appear in a state's goal vs. local context) — currently unpublished in the reference repo. *[Owner: ]*
- [ ] Done   [ ] WIP — Replace the single generic `dependency` edge with the paper's full **three-relation scheme** (signature / proof-dependency / and confirm what the third relation is from the paper). *[Owner: ]*
- [ ] Done   [ ] WIP — Full-corpus edge validation (spot-check a statistically meaningful sample of the 19K-premise graph, not just 2 edges). *[Owner: ]*

---

## Phase 3 — Data Pipeline for Real Training

- [ ] Done   [ ] WIP — Set up **LeanDojo Benchmark 4** (~122K theorems, 260K tactics) as primary training data. *[Owner: ]*
- [ ] Done   [ ] WIP — Set up **LEAN-GitHub** (~28.6K theorems, 219K tactics) as supplementary training data. *[Owner: ]*
- [ ] Done   [ ] WIP — Set up **miniF2F** (244 val / 244 test) for tuning + reporting. *[Owner: ]*
- [ ] Done   [ ] WIP — Set up **PutnamBench** (1,709 problems) as held-out test-only. *[Owner: ]*
- [ ] Done   [ ] WIP — Set up **ProofNet** (~371 problems) as held-out test-only. *[Owner: ]*
- [ ] Done   [ ] WIP — Build the static premise-dependency graph over a pinned Mathlib commit at real scale (not toy). *[Owner: ]*
- [ ] Done   [ ] WIP — Build per-theorem dynamic state graphs during data extraction. *[Owner: ]*
- [ ] Done   [ ] WIP — Secure/allocate GPU compute for training at real scale (CPU-only was 8–10h for a tiny repo; won't scale). *[Owner: ]*

---

## Phase 4 — Core Architecture Implementation

### 4.1 Representation

- [ ] Done   [ ] WIP — Implement `Expr`/`Syntax` AST extraction via Lean 4 metaprogramming for local node features. *[Owner: ]*
- [ ] Done   [ ] WIP — Wire signature edges + proof-dependency edges from LeanDojo trace output (depends on Phase 2 preprocessing). *[Owner: ]*

### 4.2 Retrieval (extends Petrovčič et al.)

- [ ] Done   [ ] WIP — Reproduce the RGCN + text-embedding fusion retriever on real data (baseline reproduction target: >25% over ReProver on LeanDojo Benchmark). *[Owner: ]*
- [ ] Done   [ ] WIP — Implement **multi-hop traversal** beyond the 2-layer RGCN neighborhood (core novel contribution #1). *Requires: Phase 0 RGCN + LeanGraph reading.* *[Owner: ]*
- [ ] Done   [ ] WIP — Implement structural `extends`/class-inheritance edges, LeanGraph-style. *Requires: Kurgan et al. 2026 read.* *[Owner: ]*
- [ ] Done   [ ] WIP — Reuse the retrieval graph inside the stuck-recovery controller (not just base retrieval) (core novel contribution #2, feeds Phase 4.4). *[Owner: ]*

### 4.3 Planning and Closing

- [ ] Done   [ ] WIP — Implement 5 independent tactic-count models M1–M5 (k = 1..5). *[Owner: ]*
- [ ] Done   [ ] WIP — Implement unified multi-class closing model over `{rfl, simp, grind, omega, decide, not-yet-closable}` (core novel contribution #3). *[Owner: ]*
- [ ] Done   [ ] WIP — Wrap M1–M5 + closing model in ReProver-style best-first search over goal states. *[Owner: ]*
- [ ] Done   [ ] WIP — Hook every predicted tactic through the Lean compiler for verification (no learned reward model). *[Owner: ]*

### 4.4 Stuck-Recovery Controller

- [ ] Done   [ ] WIP — Implement monitor tracking repeated goal states / no-progress steps. *[Owner: ]*
- [ ] Done   [ ] WIP — Implement trip actions: restart from next-best branch, widen graph-retrieval neighborhood, fall back to next Mk. *[Owner: ]*
- [ ] Done   [ ] WIP — Differentiate from arXiv:2606.04883's control-plane/data-plane agent (write up the comparison explicitly). *Requires: Phase 0 reading.* *[Owner: ]*

---

## Phase 5 — AST-Only Fallback (required regardless of which path ships)

- [ ] Done   [ ] WIP — Implement flat/tree-only AST representation (no graph libraries, no GNN). *[Owner: ]*
- [ ] Done   [ ] WIP — Implement ReProver-style dense nearest-neighbor retrieval in place of the GNN. *[Owner: ]*
- [ ] Done   [ ] WIP — Reuse the same M1–M5 planners + unified closing model, fed AST/state-text features directly. *[Owner: ]*
- [ ] Done   [ ] WIP — Confirm this fallback runs end-to-end as the mandatory baseline for benchmarking the graph-augmented system. *[Owner: ]*

---

## Phase 6 — Evaluation

- [ ] Done   [ ] WIP — Implement Recall@k and reciprocal-rank retrieval metrics vs. ReProver dense-retrieval baseline. *[Owner: ]*
- [ ] Done   [ ] WIP — Reproduce Petrovčič et al.'s reported >25% improvement number as a sanity check. *[Owner: ]*
- [ ] Done   [ ] WIP — Implement end-to-end proof success rate measurement under a fixed tactic-attempt budget. *[Owner: ]*
- [ ] Done   [ ] WIP — Run full graph-augmented system vs. AST-only fallback comparison. *[Owner: ]*
- [ ] Done   [ ] WIP — Run ablation: stuck-recovery controller disabled, isolate its contribution. *[Owner: ]*
- [ ] Done   [ ] WIP — Tune + report on miniF2F. *[Owner: ]*
- [ ] Done   [ ] WIP — Held-out test-only evaluation on PutnamBench. *[Owner: ]*
- [ ] Done   [ ] WIP — Held-out test-only evaluation on ProofNet. *[Owner: ]*

---

## Phase 7 — Writeup / Submission

- [ ] Done   [ ] WIP — Draft results section with real numbers (replacing the proposal's preliminary-only results). *[Owner: ]*
- [ ] Done   [ ] WIP — Update "what this leaves open" section based on what Phase 2/3 actually closed vs. didn't. *[Owner: ]*
- [ ] Done   [ ] WIP — Final paper writeup (ANLP course deliverable). *[Owner: ]*
- [ ] Done   [ ] WIP — Prepare presentation/demo. *[Owner: ]*

---

## Notes

- Everything in Phase 1 is already accomplished per the proposal text and is pre-checked — verify nothing has drifted before building on top of it.
- Phase 2 items are explicitly called out in the proposal as "concrete first items for the implementation phase" — do these before scaling up training in Phase 3.
- The AST-only fallback (Phase 5) isn't optional cleanup — the proposal states it's required either way, since it's the benchmark baseline for Phase 6.
