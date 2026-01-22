import mqt.qecc.codes as qecc
import json
import math

def generate_concatenated_codes(outer: qecc.StabilizerCode, inner: qecc.StabilizerCode) -> qecc.StabilizerCode:
    assert inner.x_logicals, "Inner code must have X logical operators defined."
    assert inner.z_logicals, "Inner code must have Z logical operators defined."
    assert outer.n % inner.k == 0, "Outer code's number of physical qubits must be a multiple of inner code's number of logical qubits."

    r = outer.n // inner.k
    new_generators = []
    for stab in inner.stabs_as_pauli_strings():
        for j in range(r):
            gen = ['I' * inner.n] * r
            gen[j] = stab
            new_generators.append(''.join(gen))
    
    x_logicals = [str(i) for i in inner.x_logicals]
    z_logicals = [str(i) for i in inner.z_logicals]

    for stab in outer.stabs_as_pauli_strings():
        new_stab = []
        for i in range(0, outer.n, inner.k):
            comps = []
            for j in range(inner.k):
                char = stab[i + j]
                if char == 'I':
                    comps.append('I' * inner.n)
                elif char == 'X':
                    comps.append(list(x_logicals[j]))
                elif char == 'Z':
                    comps.append(list(z_logicals[j]))
                else:
                    raise ValueError(f"Unsupported Pauli operator '{char}' in outer stabilizer.")
            
            # compose
            while len(comps) > 1:
                top = comps.pop()
                for idx, c in enumerate(top):
                    if comps[0][idx] == 'X':
                        if c == "Z":
                            comps[0][idx] = "Y"
                        elif c == "Y":
                            comps[0][idx] = "Z"
                        elif c == "X":
                            comps[0][idx] = "I"
                        else:
                            comps[0][idx] = "X"
                    elif comps[0][idx] == 'Z':
                        if c == "X":
                            comps[0][idx] = "Y"
                        elif c == "Y":
                            comps[0][idx] = "X"
                        elif c == "Z":
                            comps[0][idx] = "I"
                        else:
                            comps[0][idx] = "Z"
                    elif comps[0][idx] == 'Y':
                        if c == "X":
                            comps[0][idx] = "Z"
                        elif c == "Z":
                            comps[0][idx] = "X"
                        elif c == "Y":
                            comps[0][idx] = "I"
                        else:
                            comps[0][idx] = "Y"
                    else:
                        comps[0][idx] = c
            new_stab.append(''.join(comps[0]))
        new_generators.append(''.join(new_stab))

    new_n = r * inner.n # outer.n * inner.n // inner.k
    new_distance = math.ceil(outer.distance / inner.k) * inner.distance
    return qecc.StabilizerCode(generators = new_generators, distance = new_distance, n = new_n)

def ensure_logicals_defined(code: qecc.StabilizerCode, name: str) -> tuple[qecc.StabilizerCode, str]:
    """Ensure a code has x_logicals and z_logicals properties populated."""
    if code.x_logicals is not None and code.z_logicals is not None:
        return code, name
    
    # Compute logicals if method exists
    if hasattr(code, 'compute_logical'):
        code.compute_logical()
    
    # Extract logicals using the methods
    if hasattr(code, 'x_logicals_as_pauli_strings') and hasattr(code, 'z_logicals_as_pauli_strings'):
        try:
            x_logs = code.x_logicals_as_pauli_strings()
            z_logs = code.z_logicals_as_pauli_strings()
            
            # Create a new StabilizerCode with logicals explicitly set
            new_code = qecc.StabilizerCode(
                generators=code.stabs_as_pauli_strings(),
                x_logicals=x_logs,
                z_logicals=z_logs,
                distance=code.distance,
                n=code.n
            )
            return new_code, name
        except Exception as e:
            print(f"Warning: Could not extract logicals for {name}: {e}")
            return code, name
    
    return code, name

if __name__ == "__main__":
    codes: list[tuple[qecc.StabilizerCode, str]] = []
    distances = [3, 5, 7]
    codes.append(
        (qecc.StabilizerCode(
            generators = ["XZZXI", "IXZZX", "XIXZZ", "ZXIXZ"],
            x_logicals = ["XXXXX"],
            z_logicals = ["ZZZZZ"],
            distance = 3,
            n = 5
        ), "Perfect 5-Qubit Code")
    )

    codes += [
        (qecc.CSSCode.from_code_name(name), name) for name in ["Steane", "Shor", "Tetrahedral", "Hamming", "Carbon", "Golay"]
    ]
    codes += [
        (qecc.construct_bb_code(n), f"BB Code n={n}") for n in [72, 90]
    ]
    codes += [
        (qecc.construct_iceberg_code(m), f"Iceberg Code m={m}") for m in [2, 3, 4]
    ]
    codes += [
        (qecc.construct_many_hypercube_code(l), f"Hypercube Code l={l}") for l in [1, 2, 3]
    ]
    codes += [
        (qecc.HexagonalColorCode(d), f"Hex Color Code d={d}") for d in distances
    ]
    codes += [
        (qecc.SquareOctagonColorCode(d), f"Square Octagon Color Code d={d}") for d in distances
    ]
    codes += [
        (qecc.RotatedSurfaceCode(d), f"Rotated Surface Code d={d}") for d in distances
    ]

    # Ensure all codes have logical operators properly defined
    codes = [ensure_logicals_defined(code, name) for code, name in codes]

    codes.append(
        (qecc.StabilizerCode(
            generators = ["XXXX", "ZZZZ"],
            x_logicals = ["XIXI", "XXII"],
            z_logicals = ["ZZII", "ZIZI"],
            distance = 2,
            n = 4
        ), "4-Qubit Detector Code")
    )

    # Generate concatenated codes
    # Only concatenate single logical qubit codes (k=1) to avoid complexity
    single_logical_codes = [(code, name) for code, name in codes if code.k == 1]
    
    concatenated_codes = []
    for outer_code, outer_name in codes:  # Limit to first 5 to avoid too many combinations
        for inner_code, inner_name in single_logical_codes:
            # Only concatenate if inner code has logical operators
            if not (inner_code.x_logicals and inner_code.z_logicals):
                continue
            
            try:
                concat_code = generate_concatenated_codes(outer_code, inner_code)
                concat_name = f"({outer_name}) * ({inner_name})"
                
                # Only include if not too large
                if concat_code.n < 200:
                    concatenated_codes.append((concat_code, concat_name))
                    print(f"Generated: {concat_name} - [[{concat_code.n},{concat_code.k},{concat_code.distance}]]")
            except Exception as e:
                print(f"Failed to concatenate {outer_name} * {inner_name}: {e}")
    
    codes += concatenated_codes

    with open("data/benchmarks.json", "w") as f:
        json.dump(
            [
                {
                    "name": name,
                    "physical_qubits": code.n,
                    "logical_qubits": code.k,
                    "d": code.distance,
                    "generators": code.stabs_as_pauli_strings()
                } for code, name in filter(lambda c_n: c_n[0].n < 200, codes)
            ], fp=f, indent=4
        )