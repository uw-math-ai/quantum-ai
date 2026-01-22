import itertools
import pathlib
from dataclasses import dataclass
from typing import List, Optional, Tuple

import stim

import ft_check as ft


# Verification (postselection) measurement qubits used in bell_states/*.txt
VERIFY_QUBITS = {11, 12, 13, 25, 26, 27}

# Max samples to search for an accepted (postselected) branch.
MAX_SAMPLES = 300

# Two Steane blocks used by bell_states/*.txt
BLOCK_A_OFFSET = 0
BLOCK_B_OFFSET = 14


@dataclass(frozen=True)
class FaultResult:
    detected_by_verify: bool
    logical_ok_after_decode: bool


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


def _targets_as_ints(instr: stim.CircuitInstruction) -> List[int]:
    return [int(t.value) if hasattr(t, "value") else int(t) for t in instr.targets_copy()]


def run_circuit_with_fault(
    circuit: stim.Circuit,
    *,
    fault_at_instruction_index: Optional[int],
    fault_qubits: Tuple[int, ...],
    fault_paulis: Tuple[str, ...],
    target_bell: str,
) -> FaultResult:
    sim = stim.TableauSimulator()

    any_verify_one = False

    for idx, instr in enumerate(circuit):
        name = instr.name
        if name == "M":
            for q in _targets_as_ints(instr):
                m = sim.measure(q)
                if q in VERIFY_QUBITS and m == 1:
                    any_verify_one = True
        else:
            sim.do(instr)

        if fault_at_instruction_index is not None and idx == fault_at_instruction_index:
            for q, p in zip(fault_qubits, fault_paulis):
                _apply_pauli(sim, q, p)

    # Non-demolition ideal decode per block (keeps entanglement intact).
    ft.fault_tolerant_decode_peek(sim, offset=BLOCK_A_OFFSET)
    ft.fault_tolerant_decode_peek(sim, offset=BLOCK_B_OFFSET)

    ok = ft.check_bell_state(sim, target_bell, offset_a=BLOCK_A_OFFSET, offset_b=BLOCK_B_OFFSET)
    return FaultResult(detected_by_verify=any_verify_one, logical_ok_after_decode=ok)


def _two_qubit_paulis() -> List[Tuple[str, str]]:
    ps = ["I", "X", "Y", "Z"]
    out = []
    for a, b in itertools.product(ps, ps):
        if a == "I" and b == "I":
            continue
        out.append((a, b))
    return out


def verify_ideal_state(circuit: stim.Circuit, target_bell: str) -> None:
    """Check there exists an accepted branch that prepares the target Bell state."""
    accepted = 0
    for _ in range(MAX_SAMPLES):
        res = run_circuit_with_fault(
            circuit,
            fault_at_instruction_index=None,
            fault_qubits=(),
            fault_paulis=(),
            target_bell=target_bell,
        )
        if res.detected_by_verify:
            continue
        accepted += 1
        if res.logical_ok_after_decode:
            return

    if accepted == 0:
        raise RuntimeError(
            "No accepted (postselected) branch observed in ideal circuit. "
            "Increase MAX_SAMPLES or relax postselection conditions."
        )
    raise RuntimeError("Accepted branch observed, but none prepared the target logical Bell state.")


def verify_fault_tolerance(circuit: stim.Circuit, target_bell: str) -> Tuple[bool, Optional[str]]:
    """
    Postselected FT criterion used here:
      For any single-gate fault (including 2-qubit Pauli faults on 2-qubit gates),
      either verification flags (detected_by_verify), OR the decoded logical Bell state is correct.

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
                        fault_at_instruction_index=idx,
                        fault_qubits=(qs[0],),
                        fault_paulis=(p,),
                        target_bell=target_bell,
                    )
                    if res.detected_by_verify:
                        continue
                    if not res.logical_ok_after_decode:
                        return False, f"Accepted-but-wrong fault at instr {idx} ({instr}) with {p} on q{qs[0]}"

        if name in twoq:
            if len(qs) != 2:
                continue
            for p1, p2 in _two_qubit_paulis():
                for _ in range(MAX_SAMPLES):
                    res = run_circuit_with_fault(
                        circuit,
                        fault_at_instruction_index=idx,
                        fault_qubits=(qs[0], qs[1]),
                        fault_paulis=(p1, p2),
                        target_bell=target_bell,
                    )
                    if res.detected_by_verify:
                        continue
                    if not res.logical_ok_after_decode:
                        return (
                            False,
                            f"Accepted-but-wrong fault at instr {idx} ({instr}) with {p1}{p2} on q{qs[0]},q{qs[1]}",
                        )

    return True, None


def main() -> None:
    base = pathlib.Path(__file__).resolve().parent
    bell_dir = base / "bell_states"

    cases = [
        (bell_dir / "ft_bell_phi_plus.txt", "phi+"),
        (bell_dir / "ft_bell_phi_minus.txt", "phi-"),
        (bell_dir / "ft_bell_psi_plus.txt", "psi+"),
        (bell_dir / "ft_bell_psi_minus.txt", "psi-"),
    ]

    for path, target in cases:
        circuit = stim.Circuit(path.read_text(encoding="utf-8"))
        verify_ideal_state(circuit, target)
        ok, msg = verify_fault_tolerance(circuit, target)
        if ok:
            print(f"{path.name}: PASS (correct + postselected FT)")
        else:
            print(f"{path.name}: FAIL: {msg}")


if __name__ == "__main__":
    main()
