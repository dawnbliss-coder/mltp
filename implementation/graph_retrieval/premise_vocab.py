"""Premise vocabulary shared by the graph-construction pipeline.

Aggregates every declaration LeanDojo can see as a potential premise across a
traced repo (``TracedFile.get_premise_definitions()``, the same API Phase 1's
``all_dojo``-mode preprocessing already uses for proof-dependency edges) into
one lookup, indexed both by fully qualified name and by short (last
namespace component) name. ``signature_edges.py`` uses this to resolve
identifiers found in a proof state's goal/hypothesis text back to known
Mathlib declarations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List

from lean_dojo import TracedFile, TracedRepo


@dataclass(frozen=True)
class PremiseDef:
    full_name: str
    code: str
    file_path: str
    kind: str


@dataclass
class PremiseVocab:
    by_full_name: Dict[str, PremiseDef] = field(default_factory=dict)
    by_short_name: Dict[str, List[PremiseDef]] = field(default_factory=dict)

    def add(self, premise: PremiseDef) -> None:
        self.by_full_name[premise.full_name] = premise
        short = premise.full_name.rsplit(".", 1)[-1]
        self.by_short_name.setdefault(short, []).append(premise)

    def __len__(self) -> int:
        return len(self.by_full_name)

    @classmethod
    def from_traced_files(cls, traced_files: Iterable[TracedFile]) -> "PremiseVocab":
        vocab = cls()
        for tf in traced_files:
            for raw in tf.get_premise_definitions():
                vocab.add(
                    PremiseDef(
                        full_name=raw["full_name"],
                        code=raw["code"],
                        file_path=str(tf.path),
                        kind=raw["kind"],
                    )
                )
        return vocab

    @classmethod
    def from_traced_repo(cls, traced_repo: TracedRepo) -> "PremiseVocab":
        return cls.from_traced_files(traced_repo.traced_files)
