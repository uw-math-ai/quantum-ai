from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

# Keep the return annotation the user asked for.
String = str


@dataclass(frozen=True)
class CatSpec:
    parity: str  # "even" or "odd"
    phase: str  # "+" or "-"


def _normalize_cat_type(cat_type: str) -> CatSpec:
    t = cat_type.strip().lower().replace(" ", "")

    aliases = {
        # Even-parity cats ("phi-like")
        "even+": CatSpec("even", "+"),
        "even-": CatSpec("even", "-"),
        "phi+": CatSpec("even", "+"),
        "phi-": CatSpec("even", "-"),
        # Odd-parity cats ("psi-like")
        "odd+": CatSpec("odd", "+"),
        "odd-": CatSpec("odd", "-"),
        "psi+": CatSpec("odd", "+"),
        "psi-": CatSpec("odd", "-"),
    }

    if t not in aliases:
        raise ValueError(
            f"Unknown cat_type={cat_type!r}. Supported: "
            "even+/even-/odd+/odd- (also phi+/phi-/psi+/psi-)."
        )
    return aliases[t]


def _bits_of_string(s: str) -> list[int]:
    if any(c not in {"0", "1"} for c in s):
        raise ValueError(f"odd_string must be a 0/1 string, got {s!r}")
    return [1 if c == "1" else 0 for c in s]


def _validate_odd_inputs(*, n: int, odd_string: Optional[str]) -> list[int]:
    if odd_string is None:
        raise ValueError("odd_string is required when preparing an odd-parity cat")
    if len(odd_string) != n:
        raise ValueError(f"odd_string must have length n={n}, got length {len(odd_string)}")

    bits = _bits_of_string(odd_string)

    if n % 2 != 0:
        raise ValueError(
            "Odd-parity cats are defined here as (|s> +/- |~s>)/sqrt(2) "
            "with s having odd Hamming weight. This requires even n so ~s also has odd weight. "
            f"Got n={n}."
        )

    if sum(bits) % 2 != 1:
        raise ValueError(f"odd_string must have odd parity (odd number of '1's), got {odd_string!r}")

    return bits


def _append_multi_qubit_gate(lines: list[str], gate: str, qubits: Iterable[int]) -> None:
    qs = list(qubits)
    if not qs:
        return
    lines.append(f"{gate} " + " ".join(str(q) for q in qs))


# NOTE: Python syntax doesn’t allow a non-default argument after a default one.
# To keep the requested argument *order* while staying valid Python, cat_type defaults
# to 'phi+' and is validated.
def prepare_cat_state(n: int = 3, cat_type: str = "phi+", odd_string: str = None) -> String:
    """Return a Stim circuit string that fault-tolerantly prepares an n-qubit cat state.

    Supported `cat_type` values (4 states):
      - even+/even-  (aliases: phi+/phi-): (|0^n> +/- |1^n>)/sqrt(2)
      - odd+/odd-    (aliases: psi+/psi-): (|s>   +/- |~s>)/sqrt(2)

    For odd cats, `odd_string` provides s (length n, 0/1 string with odd parity).
    The circuit includes verification parity checks on adjacent cat qubits, with
    postselection (accept only if all verify measurements are 0).

        Qubit layout:
            - Cat qubits:       0 .. n-1
            - Verify ancillas:  n .. 2n-1
                    * n .. 2n-2: adjacent Z_i Z_{i+1} checks (i=0..n-2)
                    * 2n-1: global X^{⊗n} check

    Output format matches the plain-text Stim circuits in `single_qubit_states/*.txt`.
    """

    if n < 2:
        raise ValueError(f"n must be >= 2, got {n}")

    spec = _normalize_cat_type(cat_type)

    # Choose which computational-basis pair we want.
    x_mask: list[int] = []
    if spec.parity == "odd":
        bits = _validate_odd_inputs(n=n, odd_string=odd_string)
        x_mask = [i for i, b in enumerate(bits) if b == 1]

    cat_qubits = list(range(n))
    verify_adj_qubits = list(range(n, n + (n - 1)))
    verify_x_all_qubit = n + (n - 1)

    expected_adj_zz_bits = [0] * (n - 1)
    if spec.parity == "odd":
        # ZZ eigenvalue is +1 when bits equal, -1 when different.
        expected_adj_zz_bits = [0 if bits[i] == bits[i + 1] else 1 for i in range(n - 1)]

    expected_x_all_bit = 0 if spec.phase == "+" else 1

    lines: list[str] = []
    lines.append("# ===============================================")
    lines.append("# Fault-tolerant cat state (verified)")
    lines.append(f"# n = {n}")
    lines.append(f"# cat_type = {cat_type}")
    lines.append(f"# Cat qubits: {cat_qubits[0]}-{cat_qubits[-1]}")
    lines.append(f"# Verify ancilla (cat checks): {verify_adj_qubits[0]}-{verify_x_all_qubit}")
    lines.append("# ===============================================")
    lines.append("# Postselect (required): accept only if ALL verification measurements are 0.")
    if spec.parity == "odd":
        lines.append(f"# odd_string = {odd_string}")
    lines.append("")

    # --- Prepare the cat state (GHZ-style, chain of CX) ---
    lines.append("# ---------- Cat preparation ----------")
    lines.append("H 0")
    for i in range(n - 1):
        lines.append(f"CX {i} {i + 1}")

    # Turn |0^n>+|1^n> into |s>+|~s> when requested (odd cats).
    if x_mask:
        _append_multi_qubit_gate(lines, "X", x_mask)

    lines.append("")

    # Apply relative phase for the '-' variants.
    # Z on any cat qubit flips the relative phase between the two GHZ components.
    if spec.phase == "-":
        lines.append("# ---------- Phase select ----------")
        lines.append("Z 0")
        lines.append("")

    # --- Verification: adjacent Z-parities Z_i Z_{i+1} ---
    lines.append("# ---------- Verification (adjacent Z-parity checks) ----------")
    for i, v in enumerate(verify_adj_qubits):
        lines.append(f"CX {i} {v}")
        lines.append(f"CX {i + 1} {v}")
        # Normalize acceptance to 'M v == 0' even when expected eigenvalue is -1.
        if expected_adj_zz_bits[i] == 1:
            lines.append(f"X {v}")
        lines.append(f"M {v}")
        lines.append(f"R {v}")
        lines.append("")

    # --- Verification: global X^{⊗n} stabilizer ---
    lines.append("# ---------- Verification (global X^{⊗n} check) ----------")
    lines.append(f"H {verify_x_all_qubit}")
    for q in cat_qubits:
        lines.append(f"CX {verify_x_all_qubit} {q}")
    lines.append(f"H {verify_x_all_qubit}")
    # Normalize acceptance to 'M == 0' for both +/- phase variants.
    if expected_x_all_bit == 1:
        lines.append(f"X {verify_x_all_qubit}")
    lines.append(f"M {verify_x_all_qubit}")
    lines.append(f"R {verify_x_all_qubit}")

    return "\n".join(lines).rstrip() + "\n"


if __name__ == "__main__":
    # Tiny smoke demo (parsing requires stim installed in your environment).
    try:
        import stim  # type: ignore

        for (n, cat_type, odd) in [
            (3, "phi+", None),
            (3, "phi-", None),
            (4, "psi+", "0100"),
            (4, "psi-", "0100"),
        ]:
            s = prepare_cat_state(n=n, cat_type=cat_type, odd_string=odd)
            stim.Circuit(s)  # parse check
            print(f"OK: {cat_type} n={n}")
    except Exception as ex:
        print(f"Smoke check failed: {ex}")
