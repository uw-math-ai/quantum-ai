# circuit_metric.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator, Union

import stim

DEFAULT_VOLUME_GATES = frozenset({"H", "S", "X", "Z", "CX", "CZ"})


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


StimItem = Union[stim.CircuitInstruction, stim.CircuitRepeatBlock]


def _iter_instructions(circuit: stim.Circuit) -> Iterator[stim.CircuitInstruction]:
    """
    Iterates over instructions in a circuit, recursively expanding REPEAT blocks.
    """
    for item in circuit:
        # Stim yields either CircuitInstruction or CircuitRepeatBlock.
        if isinstance(item, stim.CircuitRepeatBlock):
            body = item.body_copy()
            for _ in range(item.repeat_count):
                yield from _iter_instructions(body)
        else:
            yield item


def _qubit_targets(inst: stim.CircuitInstruction) -> list[int]:
    return [t.value for t in inst.targets_copy() if t.is_qubit_target]


def compute_metrics(
    circuit_text: str,
    volume_gates: frozenset[str] = DEFAULT_VOLUME_GATES,
    *,
    tick_is_barrier: bool = True,
) -> CircuitMetrics:
    circuit_text = _normalize_stim_text(circuit_text)
    circuit = stim.Circuit(circuit_text)
    cx_count = 0
    volume = 0
    one_qubit = 0
    two_qubit = 0

    # Greedy depth: last scheduled layer per qubit.
    last_layer: dict[int, int] = {}
    depth = 0

    # If tick_is_barrier, enforce that operations after a TICK occur strictly after prior layers.
    tick_floor = 1

    for inst in _iter_instructions(circuit):
        name = inst.name

        if name in {"QUBIT_COORDS", "SHIFT_COORDS", "DETECTOR", "OBSERVABLE_INCLUDE"}:
            continue

        if name == "TICK":
            if tick_is_barrier:
                # Next ops must start after everything scheduled so far.
                tick_floor = max(tick_floor, depth + 1)
            continue

        qubits = _qubit_targets(inst)
        if not qubits:
            continue

        # Expand into per-gate operations (important for Stim "packed" instructions).
        ops: list[tuple[int, ...]] = []
        if name in {"CX", "CZ", "SWAP"}:
            if len(qubits) % 2 != 0:
                raise ValueError(
                    f"Malformed {name} instruction with odd #qubit targets: {qubits}"
                )
            for i in range(0, len(qubits), 2):
                ops.append((qubits[i], qubits[i + 1]))
        else:
            for q in qubits:
                ops.append((q,))

        # Counting: one-/two-qubit counts are structural; volume is gate-set-defined.
        for op in ops:
            if len(op) == 1:
                one_qubit += 1
            elif len(op) == 2:
                two_qubit += 1

        if name in volume_gates:
            volume += len(ops)
            if name == "CX":
                cx_count += len(ops)

        # Depth scheduling per op (lets disjoint ops in same instruction parallelize).
        for op in ops:
            uq = set(op)

            layer = tick_floor if tick_is_barrier else 1
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
    *,
    tick_is_barrier: bool = True,
) -> tuple[bool, dict]:
    cand = compute_metrics(
        candidate_text,
        volume_gates=volume_gates,
        tick_is_barrier=tick_is_barrier,
    )
    base = compute_metrics(
        baseline_text,
        volume_gates=volume_gates,
        tick_is_barrier=tick_is_barrier,
    )

    better = (cand.cx_count, cand.volume, cand.depth) < (base.cx_count, base.volume, base.depth)

    return better, {
        "candidate": cand.as_dict(),
        "baseline": base.as_dict(),
        "better": better,
        "comparison_rule": "lexicographic: (cx_count, volume, depth)",
        "tick_is_barrier": tick_is_barrier,
        "volume_gates": sorted(volume_gates),
    }

def _normalize_stim_text(text: str) -> str:
    """
    Makes Stim text robust to:
    - literal "\\n" sequences inside strings
    - leading indentation from triple-quoted strings
    - trailing spaces / blank lines
    """
    if text is None:
        return ""

    # Convert literal backslash-n into actual newlines (common when circuits are stored/serialized)
    text = text.replace("\\n", "\n")

    # Normalize newlines and strip indentation/whitespace per line
    lines = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            lines.append(line)

    return "\n".join(lines) + "\n"

if __name__ == "__main__":
    # Example usage:
    circuit_a = """
    H 0 1\\nCX 0 1 0 4\\nH 2 3\\nCX 1 2 1 3 1 4 1 5 1 8 1 14 2 4 2 5 2 6 2 9 2 10 4 3 3 4 4 3 3 6 3 10 4 5 4 7 4 8 4 11 4 14 5 6 5 7 5 9 5 11 5 12 6 7 6 12 6 13 7 13 11 8 12 8 13 8 14 8 9 10 12 9 13 9 14 9 12 10 13 10 14 10 12 11 11 12 12 11 11 12 13 11 14 11 13 12 14 12 14 13
    """

    circuit_b = """
H 0 1
CX 0 1
CX 0 4
H 2 3
CX 1 2
CX 1 3
CX 1 4
CX 1 5
CX 1 8
CX 1 14
CX 2 4
CX 2 5
CX 2 6
CX 2 9
CX 2 10
SWAP 3 4
CX 3 6
CX 3 10
CX 4 5
CX 4 7
CX 4 8
CX 4 11
CX 4 14
CX 5 6
CX 5 7
CX 5 9
CX 5 11
CX 5 12
CX 6 7
CX 6 12
CX 6 13
CX 7 13
CX 11 8
CX 12 8
CX 13 8
CX 14 8
CX 9 10
CX 12 9
CX 13 9
CX 14 9
CX 12 10
CX 13 10
CX 14 10
SWAP 11 12
CX 11 12
CX 13 11
CX 14 11
CX 13 12
CX 14 12
CX 14 13
    """

    better, details = is_strictly_more_optimal(circuit_b, circuit_a)
    print(f"Circuit B is better than Circuit A: {better}")
    print("Details:", details)