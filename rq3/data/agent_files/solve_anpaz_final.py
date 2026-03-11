import stim
import sys

def solve():
    print("Loading stabilizers...")
    with open("my_target_stabilizers.txt", "r") as f:
        # Filter empty lines
        lines = [line.strip() for line in f if line.strip()]
        # Convert to PauliString
        stabilizers = [stim.PauliString(line) for line in lines]

    print(f"Loaded {len(stabilizers)} stabilizers.")

    # Approach 1: From Stabilizers
    print("Approach 1: Synthesizing from Stabilizers...")
    try:
        t1 = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
        c1 = t1.to_circuit(method="graph_state")
        c1_clean = clean_circuit(c1)
        print(f"Candidate 1 (Stab -> Graph) Stats: {c1_clean.num_qubits} qubits, {len(c1_clean)} instructions.")
        with open("candidate1.stim", "w") as f:
            f.write(str(c1_clean))
    except Exception as e:
        print(f"Approach 1 failed: {e}")

    # Approach 2: From Baseline Circuit
    print("Approach 2: Synthesizing from Baseline...")
    try:
        with open("my_baseline.stim", "r") as f:
            baseline = stim.Circuit(f.read())
        
        sim = stim.TableauSimulator()
        sim.do(baseline)
        # Get tableau T such that T|0> = |psi>
        # sim.current_inverse_tableau() is T^-1.
        t2 = sim.current_inverse_tableau().inverse()
        c2 = t2.to_circuit(method="graph_state")
        c2_clean = clean_circuit(c2)
        print(f"Candidate 2 (Base -> Graph) Stats: {c2_clean.num_qubits} qubits, {len(c2_clean)} instructions.")
        with open("candidate2.stim", "w") as f:
            f.write(str(c2_clean))
    except Exception as e:
        print(f"Approach 2 failed: {e}")

def clean_circuit(circuit):
    new_c = stim.Circuit()
    for instruction in circuit:
        if instruction.name == "RX":
            # RX is Reset X. It resets the qubit to |+>.
            # If the qubit is in |0> (start), then H takes it to |+>.
            targets = instruction.targets_copy()
            new_c.append("H", targets)
        elif instruction.name == "R" or instruction.name == "RZ":
            # Reset Z. Resets to |0>.
            # Since we start with |0>, this is Identity.
            pass
        elif instruction.name == "CZ":
            new_c.append("CZ", instruction.targets_copy())
        elif instruction.name == "H":
            new_c.append("H", instruction.targets_copy())
        elif instruction.name == "S":
            new_c.append("S", instruction.targets_copy())
        elif instruction.name == "S_DAG":
            new_c.append("S_DAG", instruction.targets_copy())
        elif instruction.name == "X":
            new_c.append("X", instruction.targets_copy())
        elif instruction.name == "Y":
             new_c.append("Y", instruction.targets_copy())
        elif instruction.name == "Z":
             new_c.append("Z", instruction.targets_copy())
        elif instruction.name == "SQRT_X":
             new_c.append("SQRT_X", instruction.targets_copy())
        elif instruction.name == "SQRT_X_DAG":
             new_c.append("SQRT_X_DAG", instruction.targets_copy())
        elif instruction.name == "SQRT_Y":
             new_c.append("SQRT_Y", instruction.targets_copy())
        elif instruction.name == "SQRT_Y_DAG":
             new_c.append("SQRT_Y_DAG", instruction.targets_copy())
        elif instruction.name == "SQRT_Z":
             new_c.append("SQRT_Z", instruction.targets_copy())
        elif instruction.name == "SQRT_Z_DAG":
             new_c.append("SQRT_Z_DAG", instruction.targets_copy())
        elif instruction.name == "I":
             pass
        else:
            # Keep other gates if valid
            if instruction.name not in ["TICK", "SHIFT_COORDS", "QUBIT_COORDS", "DETECTOR", "OBSERVABLE_INCLUDE"]:
                 new_c.append(instruction)
    return new_c

if __name__ == "__main__":
    solve()
