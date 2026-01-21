import argparse
import itertools
from dataclasses import dataclass
from typing import List, Optional, Tuple

import stim  # type: ignore

from prepare_cat_state import prepare_cat_state


# Max samples to search for an accepted (postselected) branch.
MAX_SAMPLES = 300


@dataclass(frozen=True)
class FaultResult:
    detected_by_verify: bool
    cat_ok: bool


def _targets_as_ints(instr: stim.CircuitInstruction) -> List[int]:
    return [int(t.value) if hasattr(t, "value") else int(t) for t in instr.targets_copy()]


def _apply_pauli(sim: stim.TableauSimulator, qubit: int, pauli: str) -> None:
    if pauli == "I":
        return
    if pauli == "X":
        sim.x(qubit)
    elif pauli == "Y":
        sim.y(qubit)
    elif pauli == "Z":
        sim.z(qubit)
    else:
        raise ValueError(pauli)


def _pauli_string_for_qubits(*, qubits: List[int], pauli: str) -> stim.PauliString:
    if pauli not in {"X", "Y", "Z"}:
        raise ValueError(pauli)
    if not qubits:
        return stim.PauliString("")
    n = max(qubits) + 1
    chars = ["_"] * n
    for q in qubits:
        chars[q] = pauli
    return stim.PauliString("".join(chars))


def _peek_stabilizer_bit(sim: stim.TableauSimulator, p: stim.PauliString) -> int:
    """Return 0 for +1 eigenvalue, 1 for -1 eigenvalue.

    Uses peek when deterministic; otherwise measures the Pauli observable.
    """
    e = sim.peek_observable_expectation(p)
    if e == +1:
        return 0
    if e == -1:
        return 1
    if e == 0:
        return int(sim.measure_observable(p))
    raise RuntimeError(f"Unexpected expectation {e} for {p}")


def _expected_adjacent_zz_bits(*, n: int, cat_type: str, odd_string: Optional[str]) -> List[int]:
    t = cat_type.strip().lower().replace(" ", "")
    if t in {"even+", "even-", "phi+", "phi-"}:
        return [0] * (n - 1)

    if t not in {"odd+", "odd-", "psi+", "psi-"}:
        raise ValueError(f"Unknown cat_type {cat_type!r}")

    if odd_string is None or len(odd_string) != n:
        raise ValueError("odd_string (length n) required for odd cats")

    bits = [1 if c == "1" else 0 for c in odd_string]
    out: List[int] = []
    for i in range(n - 1):
        # ZZ eigenvalue is +1 when bits equal, -1 when different.
        out.append(0 if bits[i] == bits[i + 1] else 1)
    return out


def _expected_x_all_bit(*, cat_type: str) -> int:
    t = cat_type.strip().lower().replace(" ", "")
    if t.endswith("+"):
        return 0
    if t.endswith("-"):
        return 1
    raise ValueError(f"Unknown cat_type {cat_type!r}")


def _two_qubit_paulis() -> List[Tuple[str, str]]:
    ps = ["I", "X", "Y", "Z"]
    out = []
    for a, b in itertools.product(ps, ps):
        if a == "I" and b == "I":
            continue
        out.append((a, b))
    return out


def run_circuit_with_fault(
    circuit: stim.Circuit,
    *,
    n: int,
    cat_type: str,
    odd_string: Optional[str],
    fault_at_instruction_index: Optional[int],
    fault_qubits: Tuple[int, ...],
    fault_paulis: Tuple[str, ...],
) -> FaultResult:
    cat_qubits = list(range(n))
    # Matches prepare_cat_state layout: adjacent ZZ checks plus one global X^{⊗n} check.
    verify_qubits = set(range(n, n + n))

    expected_zz = _expected_adjacent_zz_bits(n=n, cat_type=cat_type, odd_string=odd_string)
    expected_x_all = _expected_x_all_bit(cat_type=cat_type)

    sim = stim.TableauSimulator()

    any_verify_one = False

    for idx, instr in enumerate(circuit):
        name = instr.name
        if name == "M":
            for q in _targets_as_ints(instr):
                m = sim.measure(q)
                if q in verify_qubits and m == 1:
                    any_verify_one = True
        else:
            sim.do(instr)

        if fault_at_instruction_index is not None and idx == fault_at_instruction_index:
            for q, p in zip(fault_qubits, fault_paulis):
                _apply_pauli(sim, q, p)

    # Check cat stabilizers on the prepared cat qubits.
    zz_ok = True
    for i in range(n - 1):
        bit = _peek_stabilizer_bit(sim, _pauli_string_for_qubits(qubits=[i, i + 1], pauli="Z"))
        if bit != expected_zz[i]:
            zz_ok = False
            break

    x_all_bit = _peek_stabilizer_bit(sim, _pauli_string_for_qubits(qubits=cat_qubits, pauli="X"))
    x_ok = x_all_bit == expected_x_all

    return FaultResult(detected_by_verify=any_verify_one, cat_ok=(zz_ok and x_ok))


def verify_ideal_state(circuit: stim.Circuit, *, n: int, cat_type: str, odd_string: Optional[str]) -> None:
    """Check there exists an accepted branch that prepares the target cat state."""
    accepted = 0
    for _ in range(MAX_SAMPLES):
        res = run_circuit_with_fault(
            circuit,
            n=n,
            cat_type=cat_type,
            odd_string=odd_string,
            fault_at_instruction_index=None,
            fault_qubits=(),
            fault_paulis=(),
        )
        if res.detected_by_verify:
            continue
        accepted += 1
        if res.cat_ok:
            return

    if accepted == 0:
        raise RuntimeError(
            "No accepted (postselected) branch observed in ideal circuit. "
            "Increase MAX_SAMPLES or relax postselection conditions."
        )
    raise RuntimeError("Accepted branch observed, but none prepared the target cat stabilizers.")


def verify_fault_tolerance(
    circuit: stim.Circuit,
    *,
    n: int,
    cat_type: str,
    odd_string: Optional[str],
) -> Tuple[bool, Optional[str]]:
    """Postselected FT criterion:

    For any single-gate fault (including 2-qubit Pauli faults on 2-qubit gates),
    either verification flags (detected_by_verify), OR the prepared cat stabilizers are correct.

    Returns (passes, first_failure_message).
    """

    twoq = {"CX", "CNOT", "CZ"}
    oneq = {"H", "X", "Y", "Z"}

    for idx, instr in enumerate(circuit):
        name = instr.name
        if name not in oneq and name not in twoq:
            continue

        qs = _targets_as_ints(instr)

        if name in oneq:
            if len(qs) != 1:
                continue
            for p in ["X", "Y", "Z"]:
                for _ in range(MAX_SAMPLES):
                    res = run_circuit_with_fault(
                        circuit,
                        n=n,
                        cat_type=cat_type,
                        odd_string=odd_string,
                        fault_at_instruction_index=idx,
                        fault_qubits=(qs[0],),
                        fault_paulis=(p,),
                    )
                    if res.detected_by_verify:
                        continue
                    if not res.cat_ok:
                        return False, f"Accepted-but-wrong fault at instr {idx} ({instr}) with {p} on q{qs[0]}"

        if name in twoq:
            if len(qs) != 2:
                continue
            for p1, p2 in _two_qubit_paulis():
                for _ in range(MAX_SAMPLES):
                    res = run_circuit_with_fault(
                        circuit,
                        n=n,
                        cat_type=cat_type,
                        odd_string=odd_string,
                        fault_at_instruction_index=idx,
                        fault_qubits=(qs[0], qs[1]),
                        fault_paulis=(p1, p2),
                    )
                    if res.detected_by_verify:
                        continue
                    if not res.cat_ok:
                        return (
                            False,
                            f"Accepted-but-wrong fault at instr {idx} ({instr}) with {p1}{p2} on q{qs[0]},q{qs[1]}",
                        )

    return True, None


def main() -> None:
    parser = argparse.ArgumentParser(description="Strict postselected FT check for prepare_cat_state-generated circuits")
    parser.add_argument("--n", type=int, default=3)
    parser.add_argument("--cat_type", type=str, default="phi+")
    parser.add_argument("--odd_string", type=str, default=None)
    args = parser.parse_args()

    circuit_str = prepare_cat_state(n=args.n, cat_type=args.cat_type, odd_string=args.odd_string)
    circuit = stim.Circuit(circuit_str)

    verify_ideal_state(circuit, n=args.n, cat_type=args.cat_type, odd_string=args.odd_string)
    ok, msg = verify_fault_tolerance(circuit, n=args.n, cat_type=args.cat_type, odd_string=args.odd_string)
    if ok:
        print(f"PASS: {args.cat_type} n={args.n} (correct + postselected FT)")
    else:
        print(f"FAIL: {msg}")


if __name__ == "__main__":
    main()
