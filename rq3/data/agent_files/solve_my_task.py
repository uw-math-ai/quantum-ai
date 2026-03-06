import stim
import sys

def count_metrics(circuit):
    cx = 0
    vol = 0
    for instr in circuit:
        name = instr.name
        
        # CX count
        if name == "CX" or name == "CNOT":
            # targets usually come in pairs
            n = len(instr.targets_copy()) // 2
            cx += n
            vol += n
        elif name in ["H", "S", "S_DAG", "X", "Y", "Z", "I", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "SQRT_Z", "SQRT_Z_DAG", "CY", "CZ", "SWAP", "ISWAP", "ISWAP_DAG", "C_XYZ", "C_ZYX"]:
             # Volume count
             n_targets = len(instr.targets_copy())
             if name in ["CX", "CY", "CZ", "SWAP", "ISWAP", "ISWAP_DAG", "C_XYZ", "C_ZYX"]:
                 # 2 qubit gates
                 # Each pair is 1 gate
                 n_gates = n_targets // 2
                 vol += n_gates
             else:
                 # 1 qubit gates
                 vol += n_targets
        elif name in ["R", "RX", "RY", "RZ", "M", "MX", "MY", "MZ", "MPP", "DETECTOR", "OBSERVABLE_INCLUDE", "TICK", "SHIFT_COORDS", "QUBIT_COORDS"]:
            # Measurements, resets, annotations don't count towards unitary metrics usually
            pass
            
    return cx, vol

def solve():
    # Load baseline
    try:
        with open(r"C:\Users\anpaz\Repos\quantum-ai\rq3\baseline.stim", "r") as f:
            baseline_text = f.read()
        baseline = stim.Circuit(baseline_text)
    except Exception as e:
        print(f"Error loading baseline: {e}")
        return

    b_cx, b_vol = count_metrics(baseline)
    print(f"Baseline: CX={b_cx}, Vol={b_vol}")

    # Load stabilizers
    try:
        with open(r"C:\Users\anpaz\Repos\quantum-ai\rq3\stabilizers.txt", "r") as f:
            lines = [l.strip() for l in f if l.strip()]
        stabs = [stim.PauliString(l) for l in lines]
    except Exception as e:
        print(f"Error loading stabilizers: {e}")
        return

    print(f"Loaded {len(stabs)} stabilizers.")

    # Synthesize new circuit
    print("Synthesizing...")
    try:
        # allow_underconstrained=True because 106 stabilizers < 115 qubits
        tableau = stim.Tableau.from_stabilizers(stabs, allow_underconstrained=True, allow_redundant=True)
        new_circuit = tableau.to_circuit(method="elimination")
    except Exception as e:
        print(f"Error synthesizing: {e}")
        return

    n_cx, n_vol = count_metrics(new_circuit)
    print(f"New:      CX={n_cx}, Vol={n_vol}")

    if n_cx < b_cx or (n_cx == b_cx and n_vol < b_vol):
        print("Candidate is strictly better.")
    else:
        print("Candidate is NOT strictly better.")
    
    # Verify correctness
    print("Verifying correctness...")
    sim = stim.TableauSimulator()
    sim.do(new_circuit)
    valid = True
    for s in stabs:
        if sim.peek_observable_expectation(s) != 1:
            valid = False
            # print(f"Failed: {s}")
            break
            
    if valid:
        print("Candidate is VALID.")
        with open(r"C:\Users\anpaz\Repos\quantum-ai\rq3\candidate.stim", "w") as f:
            f.write(str(new_circuit))
    else:
        print("Candidate is INVALID.")

if __name__ == "__main__":
    solve()
