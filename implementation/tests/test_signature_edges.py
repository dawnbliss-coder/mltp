"""Unit tests for Phase 2, Task 1 (signature-edge preprocessing).

These test the extractor's actual logic (tokenizing + resolving goal/
hypothesis text against a premise vocabulary) using LeanDojo's real
``parse_goals``/``Goal``/``Declaration`` types, which are plain dataclasses
we can construct directly. This does not require a live LeanDojo trace —
see ``../README.md`` for what still does.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lean_dojo import parse_goals
from lean_dojo.interaction.parse_goals import Declaration, Goal

from graph_retrieval.premise_vocab import PremiseDef, PremiseVocab
from graph_retrieval.signature_edges import (
    extract_signature_edges_for_goal,
    _resolve,
    _tokenize,
)


def _vocab(*full_names: str) -> PremiseVocab:
    vocab = PremiseVocab()
    for name in full_names:
        vocab.add(PremiseDef(full_name=name, code="", file_path="Test.lean", kind="theorem"))
    return vocab


def test_tokenize_pulls_out_dotted_and_plain_identifiers():
    tokens = list(_tokenize("hp : Nat.Prime p\n⊢ p ≠ 2 → Odd p"))
    assert "Nat.Prime" in tokens
    assert "Odd" in tokens
    # local variable / hypothesis names are still tokenized; filtering
    # against the vocabulary (not the tokenizer) is what excludes them.
    assert "p" in tokens


def test_resolve_exact_dotted_match_is_unambiguous():
    vocab = _vocab("Nat.Prime", "Nat.add_comm")
    assert _resolve("Nat.Prime", vocab) == [("Nat.Prime", False)]


def test_resolve_short_name_ambiguous_across_namespaces():
    vocab = _vocab("Nat.add_comm", "Int.add_comm")
    results = dict(_resolve("add_comm", vocab))
    assert set(results) == {"Nat.add_comm", "Int.add_comm"}
    assert all(ambiguous for ambiguous in results.values())


def test_resolve_unknown_token_yields_nothing():
    vocab = _vocab("Nat.Prime")
    assert _resolve("not_a_premise", vocab) == []


def test_extract_signature_edges_for_goal_hits_hypothesis_and_conclusion():
    vocab = _vocab("Nat.Prime", "Odd", "Nat.add_comm")
    goal = Goal(
        assumptions=[
            Declaration(ident="p", lean_type="ℕ"),
            Declaration(ident="hp", lean_type="Nat.Prime p"),
        ],
        conclusion="Odd p",
    )

    edges = list(extract_signature_edges_for_goal("thm@0", goal, vocab))
    by_premise = {e.premise_full_name: e for e in edges}

    assert set(by_premise) == {"Nat.Prime", "Odd"}
    assert by_premise["Nat.Prime"].source == "hypothesis"
    assert by_premise["Nat.Prime"].ambiguous is False
    assert by_premise["Odd"].source == "conclusion"
    # local variable names (p, hp) and the ℕ notation must not appear
    assert "p" not in by_premise
    assert "hp" not in by_premise
    assert "Nat.add_comm" not in by_premise  # never referenced in this goal


def test_extract_signature_edges_deduplicates_repeated_mentions():
    vocab = _vocab("Nat.Prime")
    goal = Goal(
        assumptions=[Declaration(ident="hp", lean_type="Nat.Prime p ∧ Nat.Prime p")],
        conclusion="True",
    )
    edges = list(extract_signature_edges_for_goal("thm@0", goal, vocab))
    assert len(edges) == 1


def test_end_to_end_against_real_parse_goals():
    """Round-trips through LeanDojo's actual pretty-printed-goal parser,
    not just our own constructed Goal objects."""
    pp = "p : ℕ\nhp : Nat.Prime p\nh : p ≠ 2\n⊢ Odd p"
    vocab = _vocab("Nat.Prime", "Odd")

    (goal,) = parse_goals(pp)
    edges = list(extract_signature_edges_for_goal("thm@0", goal, vocab))
    premises = {e.premise_full_name for e in edges}

    assert premises == {"Nat.Prime", "Odd"}
