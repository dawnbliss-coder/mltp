"""Phase 2, Task 1 — signature-edge preprocessing.

The public reference implementation (Petrovcic et al., 2025) ships the
*consumer* of a tagged premise-dependency corpus but not the *producer*:
specifically, the preprocessing that tags which premises appear in a proof
state's goal or local context (the paper's "signature" edge type, Section
3.1 of our proposal) is not published. Phase 1 already reverse-engineered
the sibling *proof-dependency* edge type from
``TracedTactic.get_annotated_tactic()`` (premises a tactic actually cites).
This module reimplements the signature-edge side: premises *referenced* in
a state's goal/hypotheses, regardless of whether the tactic went on to cite
them by name.

Approach
--------
LeanDojo exposes each proof state only as Lean's pretty-printed text
(``TracedTactic.state_before``), not as a typed ``Expr`` we could walk
directly. We therefore:

1. Parse that text into structured goals with ``lean_dojo.parse_goals``
   (LeanDojo's own parser — not something we invented), which separates
   local-context hypotheses (``Declaration.ident``/``lean_type``) from the
   goal's ``conclusion``.
2. Tokenize the hypothesis types and the conclusion into identifier-shaped
   substrings.
3. Resolve each token against a ``PremiseVocab`` built from
   ``get_premise_definitions()`` across the traced repo: an exact dotted
   match is unambiguous; an unqualified short name (e.g. ``add_comm``) may
   resolve to several declarations (e.g. ``Nat.add_comm``, ``Int.add_comm``)
   and is emitted as ambiguous rather than silently guessed at.

This is a heuristic, not a semantic analysis (Lean's actual name
resolution, which we cannot access from pretty-printed text alone) — the
ambiguous-match rate on a real trace is exactly the kind of thing Phase 2's
full-corpus validation task should report.

Known limitation: the tokenizer matches ASCII/Greek identifier characters
only, deliberately excluding blackboard-bold notation (``ℕ``, ``ℝ``, ...).
No Mathlib declaration is literally *named* that way — it is notation for
``Nat``/``Real``/etc. — so this costs no real matches, but is worth stating
explicitly rather than leaving implicit.

Next step once a live ``TracedRepo`` is available (not done automatically
here — see ``../README.md``)::

    from lean_dojo import TracedRepo
    from graph_retrieval.premise_vocab import PremiseVocab
    from graph_retrieval.signature_edges import extract_signature_edges_for_theorem

    traced_repo = TracedRepo.load_from_disk(path)
    vocab = PremiseVocab.from_traced_repo(traced_repo)
    for theorem in traced_repo.get_traced_theorems():
        edges = extract_signature_edges_for_theorem(theorem, vocab)
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterator, List, Set, Tuple

from lean_dojo import TracedTactic, TracedTheorem
from lean_dojo.interaction.parse_goals import Goal, parse_goals

from .premise_vocab import PremiseVocab

# Lean 4 identifier: a letter/underscore (ASCII or Greek, both common in
# Mathlib names) followed by letters/digits/underscore/prime, optionally
# dot-qualified (namespaced). See the module docstring for what this
# deliberately excludes.
_IDENT_RE = re.compile(
    r"[A-Za-zΑ-Ωα-ω_][A-Za-zΑ-Ωα-ω0-9_']*(?:\.[A-Za-zΑ-Ωα-ω_][A-Za-zΑ-Ωα-ω0-9_']*)*"
)


@dataclass(frozen=True)
class SignatureEdge:
    state_id: str
    premise_full_name: str
    source: str  # "hypothesis" or "conclusion"
    ambiguous: bool


def _state_id(theorem_full_name: str, tactic_index: int) -> str:
    """Id for a proof-state node, matching the dynamic state graph in
    Section 3.1 of the proposal (one node per proof state / tactic
    instance, generated per-theorem, never baked into the static graph)."""
    return f"{theorem_full_name}@{tactic_index}"


def _tokenize(text: str) -> Iterator[str]:
    for m in _IDENT_RE.finditer(text):
        yield m.group(0)


def _resolve(token: str, vocab: PremiseVocab) -> List[Tuple[str, bool]]:
    """Resolve one identifier token to candidate premise full names.

    Returns ``(full_name, ambiguous)`` pairs. An exact dotted match against
    a known full name is unambiguous. Otherwise we fall back to the token's
    last dot-component as a short-name lookup, which is ambiguous whenever
    more than one declaration shares that short name.
    """
    if token in vocab.by_full_name:
        return [(token, False)]

    short = token.rsplit(".", 1)[-1]
    candidates = vocab.by_short_name.get(short)
    if not candidates:
        return []
    ambiguous = len(candidates) > 1
    return [(c.full_name, ambiguous) for c in candidates]


def extract_signature_edges_for_goal(
    state_id: str, goal: Goal, vocab: PremiseVocab
) -> Iterator[SignatureEdge]:
    """Signature edges for a single goal: every known premise referenced in
    its hypothesis types or its conclusion. Hypothesis *names* (e.g. the
    ``hp`` in ``hp : Nat.Prime p``) are never matched — only their *types*
    are, since a local variable name is not a premise."""
    seen: Set[Tuple[str, str]] = set()

    def _emit(text: str, source: str) -> Iterator[SignatureEdge]:
        for token in _tokenize(text):
            for full_name, ambiguous in _resolve(token, vocab):
                key = (full_name, source)
                if key in seen:
                    continue
                seen.add(key)
                yield SignatureEdge(state_id, full_name, source, ambiguous)

    yield from _emit(goal.conclusion, "conclusion")
    for assumption in goal.assumptions:
        yield from _emit(assumption.lean_type, "hypothesis")


def extract_signature_edges_for_tactic(
    tactic: TracedTactic, tactic_index: int, vocab: PremiseVocab
) -> List[SignatureEdge]:
    """Signature edges for the proof state *before* a tactic is applied.

    We use ``state_before``, not ``state_after``: a signature edge
    represents what was available to the model at decision time, matching
    how each dynamic-graph node corresponds to one proof state / tactic
    instance.
    """
    theorem_full_name = tactic.traced_theorem.theorem.full_name
    state_id = _state_id(theorem_full_name, tactic_index)

    edges: List[SignatureEdge] = []
    for goal in parse_goals(tactic.state_before):
        edges.extend(extract_signature_edges_for_goal(state_id, goal, vocab))
    return edges


def extract_signature_edges_for_theorem(
    theorem: TracedTheorem, vocab: PremiseVocab
) -> List[SignatureEdge]:
    edges: List[SignatureEdge] = []
    for i, tactic in enumerate(theorem.get_traced_tactics(atomic_only=True)):
        edges.extend(extract_signature_edges_for_tactic(tactic, i, vocab))
    return edges
