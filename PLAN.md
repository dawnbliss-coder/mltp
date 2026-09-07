# Project Plan — KG-Augmented Premise Retrieval for Lean 4

Team: Priyanka Agarwal, Akshith
Legend: **[Done]** = task fully completed. **[WIP]** = currently being worked on (should be checked by whoever is actively on it; uncheck when you pause).
Every task below starts with **[Paper: ...]** naming what must be read before starting it. **[Paper: None]** means it's pure engineering — no new reading required.

> Assign an owner (P / A / Both) in brackets as you pick up a task. Update the two checkboxes as work progresses — don't leave both ticked and abandon a task.

**Dependency note: Phase 2 depends on Phase 1.** The signature-edge and three-relation rework reuses the Phase 1 preprocessing script, and full-corpus validation needs the Phase 1 full 907-file run to finish first. Don't start Phase 2 before Phase 1's last two items are closed.

---

## Phase 0 — Literature Review (read before implementing the related component)

Core paper being reproduced/extended:
- [ ] Done   [ ] WIP — **[Paper: Petrovčič et al. 2025, arXiv:2510.23637]** Read in full — RGCN + text-embedding fusion, tagging modes (`all_dojo` vs 3-relation scheme). *[Owner: ]*
- [ ] Done   [ ] WIP — **[Paper: Yang et al. 2023, LeanDojo, arXiv:2306.15626]** Understand trace extraction, `get_premise_definitions`, `get_annotated_tactic` APIs, ReProver baseline. *[Owner: ]*

Graph-representation lineage (needed for the multi-hop / extends-edge extension, Section 3.2):
- [ ] Done   [ ] WIP — **[Paper: Kurgan et al. 2026, TheoremGraph/LeanGraph, arXiv:2606.25363]** Six-edge-type declaration graph (`extends, field, sig, proof, def, docref`); needed to design the `extends`/class-inheritance edges. *[Owner: ]*
- [ ] Done   [ ] WIP — **[Paper: Paliwal et al. 2020, AAAI]** Graph representations for higher-order logic — HOList/HOL Light graph encoder lineage. *[Owner: ]*
- [ ] Done   [ ] WIP — **[Paper: Wang et al. 2017, arXiv:1709.09994]** Premise selection by deep graph embedding. *[Owner: ]*
- [ ] Done   [ ] WIP — **[Paper: Aniva et al. 2026, Nazrin/ExprGraph, arXiv:2602.18767]** Expression-level GNN, atomic tactic set; relevant contrast case, not directly reused. *[Owner: ]*
- [ ] Done   [ ] WIP — **[Paper: Blaauwbroek et al. 2024, Graph2Tac, ICML]** Online graph representation learning for Coq; relevant to the "future work" note on the static-graph limitation. *[Owner: ]*

Retrieval baselines / ceiling:
- [ ] Done   [ ] WIP — **[Paper: Mikuła et al. 2023, Magnushammer, arXiv:2303.04488]** Contrastive transformer retriever, the no-graph ceiling to beat. *[Owner: ]*
- [ ] Done   [ ] WIP — **[Paper: Alemi et al. 2016, DeepMath, NeurIPS]** *[Owner: ]*

Classical premise selection (background/related work section only):
- [ ] Done   [ ] WIP — **[Paper: Meng & Paulson 2009 (MePo); Hoder & Voronkov 2011 (SInE); Böhme & Nipkow 2010 (Sledgehammer); Kühlwein et al. 2013 (MaSh)]** Skim for related-work framing. *[Owner: ]*

Stuck-recovery contrast:
- [ ] Done   [ ] WIP — **[Paper: arXiv:2606.04883, control-plane/data-plane cost-quality agent for Lean]** Read to make sure our controller is clearly differentiated (Section 3.4 claim). *[Owner: ]*

Background needed but not cited in the proposal (find + read):
- [ ] Done   [ ] WIP — **[Paper: Schlichtkrull et al., "Modeling Relational Data with Graph Convolutional Networks" (RGCN) — find it]** Needed to actually implement/modify the relation-aware GNN. *[Owner: ]*
- [ ] Done   [ ] WIP — **[Paper: Xue et al., "ByT5: Towards a token-free future..." — find it]** The pretrained encoder used inside `PremiseRetriever`. *[Owner: ]*
- [ ] Done   [ ] WIP — **[Paper: LEAN-GitHub dataset paper — find it]** Needed before using this dataset in Phase 3. *[Owner: ]*
- [ ] Done   [ ] WIP — **[Paper: miniF2F paper (Zheng et al., "miniF2F: a cross-system benchmark...") — find it]** Needed before using this benchmark in Phase 3/6. *[Owner: ]*
- [ ] Done   [ ] WIP — **[Paper: PutnamBench paper (Tsoukalas et al.) — find it]** Needed before using this benchmark in Phase 3/6. *[Owner: ]*
- [ ] Done   [ ] WIP — **[Paper: ProofNet paper (Azerbayev et al.) — find it]** Needed before using this benchmark in Phase 3/6. *[Owner: ]*

---

## Phase 1 — Environment & Reproduction Setup
*(depends on: Phase 0 core-paper reads)*

- [ ] Done   [ ] WIP — **[Paper: Petrovčič et al. 2025]** Clone reference implementation.
- [ ] Done   [ ] WIP — **[Paper: None]** Patch missing GPU-only `deepspeed` dependency to run CPU-only.
- [ ] Done   [ ] WIP — **[Paper: None]** Fix C++ extension that failed to compile against local macOS SDK.
- [ ] Done   [ ] WIP — **[Paper: None]** Fix Python path resolution issue.
- [ ] Done   [ ] WIP — **[Paper: Yang et al. 2023 (LeanDojo APIs); Petrovčič et al. 2025 (tagging scheme)]** Write the missing preprocessing step (premise tagging with signature/proof provenance) using `get_premise_definitions` + `get_annotated_tactic`, feed into `all_dojo` tagging mode.
- [ ] Done   [ ] WIP — **[Paper: None]** Run end-to-end on reduced corpus (4 files, `lean4-example`, 1,030 premises, 166 edges) and hand-verify ground-truth labels (`hello_world`, `foo`).
- [ ] Done   [ ] WIP — **[Paper: None]** Finish the full 907-file / 19,239-premise closure run (was still running after several hours on CPU at proposal time) — get it to completion, sanity-check output size/shape. *[Owner: ]*
- [ ] Done   [ ] WIP — **[Paper: None]** Verify the two edges (`Nat.add_comm`, `Nat.add_assoc`) plus a wider random sample at scale (not just the two touching example theorems). *[Owner: ]*

---

## Phase 2 — Close the Gaps Left Open by the Preliminary Trial
*(depends on: Phase 1 — reuses its preprocessing script and needs its full-corpus run finished)*

- [ ] Done   [ ] WIP — **[Paper: Petrovčič et al. 2025]** Reverse-engineer / reimplement the missing **signature-edge** preprocessing (which premises appear in a state's goal vs. local context) — currently unpublished in the reference repo. *[Owner: ]*
- [ ] Done   [ ] WIP — **[Paper: Petrovčič et al. 2025]** Replace the single generic `dependency` edge with the paper's full **three-relation scheme** (signature / proof-dependency / confirm the third relation from the paper). *[Owner: ]*
- [ ] Done   [ ] WIP — **[Paper: None]** Full-corpus edge validation (spot-check a statistically meaningful sample of the 19K-premise graph, not just 2 edges). *[Owner: ]*

---

## Phase 3 — Data Pipeline for Real Training
*(depends on: Phase 0 dataset-paper reads; Phase 2 for the graph-building items)*

- [ ] Done   [ ] WIP — **[Paper: Yang et al. 2023, LeanDojo Benchmark 4]** Set up as primary training data (~122K theorems, 260K tactics). *[Owner: ]*
- [ ] Done   [ ] WIP — **[Paper: LEAN-GitHub dataset paper]** Set up as supplementary training data (~28.6K theorems, 219K tactics). *[Owner: ]*
- [ ] Done   [ ] WIP — **[Paper: miniF2F paper]** Set up for tuning + reporting (244 val / 244 test). *[Owner: ]*
- [ ] Done   [ ] WIP — **[Paper: PutnamBench paper]** Set up as held-out test-only (1,709 problems). *[Owner: ]*
- [ ] Done   [ ] WIP — **[Paper: ProofNet paper]** Set up as held-out test-only (~371 problems). *[Owner: ]*
- [ ] Done   [ ] WIP — **[Paper: Petrovčič et al. 2025]** Build the static premise-dependency graph over a pinned Mathlib commit at real scale (not toy). *[Owner: ]*
- [ ] Done   [ ] WIP — **[Paper: Petrovčič et al. 2025; Yang et al. 2023]** Build per-theorem dynamic state graphs during data extraction. *[Owner: ]*
- [ ] Done   [ ] WIP — **[Paper: None]** Secure/allocate GPU compute for training at real scale (CPU-only was 8–10h for a tiny repo; won't scale). *[Owner: ]*

---

## Phase 4 — Core Architecture Implementation
*(depends on: Phase 2 gap closures; Phase 3 data pipeline)*

### 4.1 Representation
- [ ] Done   [ ] WIP — **[Paper: None — Lean 4 metaprogramming docs, not an academic paper]** Implement `Expr`/`Syntax` AST extraction via Lean 4 metaprogramming for local node features. *[Owner: ]*
- [ ] Done   [ ] WIP — **[Paper: Petrovčič et al. 2025]** Wire signature edges + proof-dependency edges from LeanDojo trace output (depends on Phase 2 preprocessing). *[Owner: ]*

### 4.2 Retrieval (extends Petrovčič et al.)
- [ ] Done   [ ] WIP — **[Paper: Petrovčič et al. 2025; RGCN paper; ByT5 paper]** Reproduce the RGCN + text-embedding fusion retriever on real data (baseline reproduction target: >25% over ReProver on LeanDojo Benchmark). *[Owner: ]*
- [ ] Done   [ ] WIP — **[Paper: RGCN paper; Kurgan et al. 2026]** Implement **multi-hop traversal** beyond the 2-layer RGCN neighborhood (core novel contribution #1). *[Owner: ]*
- [ ] Done   [ ] WIP — **[Paper: Kurgan et al. 2026]** Implement structural `extends`/class-inheritance edges, LeanGraph-style. *[Owner: ]*
- [ ] Done   [ ] WIP — **[Paper: Petrovčič et al. 2025 (graph); arXiv:2606.04883 (contrast)]** Reuse the retrieval graph inside the stuck-recovery controller (not just base retrieval) (core novel contribution #2, feeds Phase 4.4). *[Owner: ]*

### 4.3 Planning and Closing
- [ ] Done   [ ] WIP — **[Paper: Yang et al. 2023, ReProver]** Implement 5 independent tactic-count models M1–M5 (k = 1..5). *[Owner: ]*
- [ ] Done   [ ] WIP — **[Paper: None — novel design]** Implement unified multi-class closing model over `{rfl, simp, grind, omega, decide, not-yet-closable}` (core novel contribution #3). *[Owner: ]*
- [ ] Done   [ ] WIP — **[Paper: Yang et al. 2023, ReProver]** Wrap M1–M5 + closing model in ReProver-style best-first search over goal states. *[Owner: ]*
- [ ] Done   [ ] WIP — **[Paper: None]** Hook every predicted tactic through the Lean compiler for verification (no learned reward model). *[Owner: ]*

### 4.4 Stuck-Recovery Controller
- [ ] Done   [ ] WIP — **[Paper: arXiv:2606.04883]** Implement monitor tracking repeated goal states / no-progress steps. *[Owner: ]*
- [ ] Done   [ ] WIP — **[Paper: arXiv:2606.04883]** Implement trip actions: restart from next-best branch, widen graph-retrieval neighborhood, fall back to next Mk. *[Owner: ]*
- [ ] Done   [ ] WIP — **[Paper: arXiv:2606.04883]** Differentiate from its control-plane/data-plane agent (write up the comparison explicitly). *[Owner: ]*

---

## Phase 5 — AST-Only Fallback (required regardless of which path ships)
*(depends on: Phase 4.3 planners/closing model — reused as-is)*

- [ ] Done   [ ] WIP — **[Paper: Yang et al. 2023, ReProver]** Implement flat/tree-only AST representation (no graph libraries, no GNN). *[Owner: ]*
- [ ] Done   [ ] WIP — **[Paper: Yang et al. 2023; Mikuła et al. 2023 (Magnushammer, as alternative dense-retriever reference)]** Implement ReProver-style dense nearest-neighbor retrieval in place of the GNN. *[Owner: ]*
- [ ] Done   [ ] WIP — **[Paper: None]** Reuse the same M1–M5 planners + unified closing model, fed AST/state-text features directly. *[Owner: ]*
- [ ] Done   [ ] WIP — **[Paper: None]** Confirm this fallback runs end-to-end as the mandatory baseline for benchmarking the graph-augmented system. *[Owner: ]*

---

## Phase 6 — Evaluation
*(depends on: Phase 4 full system; Phase 5 fallback; Phase 3 benchmark data)*

- [ ] Done   [ ] WIP — **[Paper: Petrovčič et al. 2025]** Implement Recall@k and reciprocal-rank retrieval metrics vs. ReProver dense-retrieval baseline. *[Owner: ]*
- [ ] Done   [ ] WIP — **[Paper: Petrovčič et al. 2025]** Reproduce their reported >25% improvement number as a sanity check. *[Owner: ]*
- [ ] Done   [ ] WIP — **[Paper: Yang et al. 2023]** Implement end-to-end proof success rate measurement under a fixed tactic-attempt budget. *[Owner: ]*
- [ ] Done   [ ] WIP — **[Paper: None]** Run full graph-augmented system vs. AST-only fallback comparison. *[Owner: ]*
- [ ] Done   [ ] WIP — **[Paper: arXiv:2606.04883, for comparison framing]** Run ablation: stuck-recovery controller disabled, isolate its contribution. *[Owner: ]*
- [ ] Done   [ ] WIP — **[Paper: miniF2F paper]** Tune + report on miniF2F. *[Owner: ]*
- [ ] Done   [ ] WIP — **[Paper: PutnamBench paper]** Held-out test-only evaluation on PutnamBench. *[Owner: ]*
- [ ] Done   [ ] WIP — **[Paper: ProofNet paper]** Held-out test-only evaluation on ProofNet. *[Owner: ]*

---

## Phase 7 — Writeup / Submission
*(depends on: Phase 6 results)*

- [ ] Done   [ ] WIP — **[Paper: None]** Draft results section with real numbers (replacing the proposal's preliminary-only results). *[Owner: ]*
- [ ] Done   [ ] WIP — **[Paper: None]** Update "what this leaves open" section based on what Phase 2/3 actually closed vs. didn't. *[Owner: ]*
- [ ] Done   [ ] WIP — **[Paper: None]** Final paper writeup (ANLP course deliverable). *[Owner: ]*
- [ ] Done   [ ] WIP — **[Paper: None]** Prepare presentation/demo. *[Owner: ]*

---

## Notes
- Phase 2 depends on Phase 1 (see dependency note above) — its items are explicitly called out in the proposal as "concrete first items for the implementation phase," to be done before scaling up training in Phase 3.
- The AST-only fallback (Phase 5) isn't optional cleanup — the proposal states it's required either way, since it's the benchmark baseline for Phase 6.
- Dataset papers (LEAN-GitHub, miniF2F, PutnamBench, ProofNet) weren't cited in the proposal's reference list but are needed reading before Phase 3/6 — find and read them as part of Phase 0.
