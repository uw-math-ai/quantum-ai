# circuit_metrics.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
import stim

DEFAULT_VOLUME_GATES = frozenset({"H", "S", "X", "Z", "CX"})


@dataclass(frozen=True)
class CircuitMetrics:
    cx_count: int
    volume: int
    one_qubit_gates: int
    two_qubit_gates: int
    depth: int

    def as_dict(self) -> dict:
        return {
            "cx_count": self.cx_count,
            "volume": self.volume,
            "one_qubit_gates": self.one_qubit_gates,
            "two_qubit_gates": self.two_qubit_gates,
            "depth": self.depth,
        }


def _iter_instructions(circuit: stim.Circuit) -> Iterable[stim.CircuitInstruction]:
    yield from circuit


def _qubit_targets(inst: stim.CircuitInstruction) -> list[int]:
    return [t.value for t in inst.targets_copy() if t.is_qubit_target]


def compute_metrics(
    circuit_text: str,
    volume_gates: frozenset[str] = DEFAULT_VOLUME_GATES,
) -> CircuitMetrics:
    circuit = stim.Circuit(circuit_text)

    cx_count = 0
    volume = 0
    one_qubit = 0
    two_qubit = 0

    # greedy depth: last layer per qubit
    last_layer: dict[int, int] = {}
    depth = 0

    for inst in _iter_instructions(circuit):
        name = inst.name

        if name in {"TICK", "QUBIT_COORDS", "SHIFT_COORDS", "DETECTOR", "OBSERVABLE_INCLUDE"}:
            continue

        qubits = _qubit_targets(inst)
        if not qubits:
            continue

        # Expand into per-gate operations (important for Stim "packed" instructions)
        ops: list[tuple[int, ...]] = []
        if name == "CX":
            # CX targets come in pairs
            if len(qubits) % 2 != 0:
                raise ValueError(f"Malformed CX instruction with odd #qubit targets: {qubits}")
            for i in range(0, len(qubits), 2):
                ops.append((qubits[i], qubits[i + 1]))
        else:
            for q in qubits:
                ops.append((q,))

        # Counting
        if name in volume_gates:
            volume += len(ops)
            if name == "CX":
                cx_count += len(ops)
                two_qubit += len(ops)
            else:
                one_qubit += len(ops)

        # Depth scheduling per op (lets disjoint ops in same instruction parallelize)
        for op in ops:
            uq = set(op)
            layer = 1
            for q in uq:
                layer = max(layer, last_layer.get(q, 0) + 1)
            for q in uq:
                last_layer[q] = layer
            depth = max(depth, layer)

    return CircuitMetrics(
        cx_count=cx_count,
        volume=volume,
        one_qubit_gates=one_qubit,
        two_qubit_gates=two_qubit,
        depth=depth,
    )


def is_strictly_more_optimal(
    candidate_text: str,
    baseline_text: str,
    volume_gates: frozenset[str] = DEFAULT_VOLUME_GATES,
) -> tuple[bool, dict]:
    cand = compute_metrics(candidate_text, volume_gates=volume_gates)
    base = compute_metrics(baseline_text, volume_gates=volume_gates)

    better = (
        (cand.cx_count, cand.volume, cand.depth)
        < (base.cx_count, base.volume, base.depth)
    )

    return better, {
        "candidate": cand.as_dict(),
        "baseline": base.as_dict(),
        "better": better,
        "comparison_rule": "lexicographic: (cx_count, volume, depth)",
    }
