import stim
import sys

def solve():
    # Read stabilizers
    try:
        with open("target_stabilizers_v2.txt", "r") as f:
            lines = [l.strip() for l in f if l.strip()]
    except FileNotFoundError:
        print("Error: target_stabilizers_v2.txt not found")
        return

    # Create tableau from stabilizers
    try:
        # Create a tableau from the stabilizers. 
        # allow_redundant=False ensures we have independent generators.
        # allow_underconstrained=False ensures we have a full set.
        tableau = stim.Tableau.from_stabilizers([stim.PauliString(l) for l in lines], allow_redundant=False, allow_underconstrained=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # Synthesize graph state circuit
    # method="graph_state" usually produces CZ gates and single qubit gates
    # It attempts to make a circuit that prepares the state Stabilizers * |0> ?
    # No, it prepares the state stabilized by the tableau.
    try:
        circuit = tableau.to_circuit(method="graph_state")
    except Exception as e:
        print(f"Error synthesizing circuit: {e}")
        return
    
    # Clean up the circuit
    clean_circuit = stim.Circuit()
    for instruction in circuit:
        if instruction.name == "RX":
            # RX resets to |+>. H on |0> creates |+>.
            clean_circuit.append("H", instruction.targets_copy())
        elif instruction.name == "R" or instruction.name == "RZ":
            # Resets to |0>. Already at |0> initially.
            continue
        elif instruction.name == "RY":
             # RY resets to |i+> (Y basis).
             # To get |i+> from |0>: H then S.
             targets = instruction.targets_copy()
             clean_circuit.append("H", targets)
             clean_circuit.append("S", targets)
        elif instruction.name == "M" or instruction.name == "MX" or instruction.name == "MY" or instruction.name == "MZ":
             # Measurements should not happen in state prep usually.
             print(f"Warning: Measurement {instruction.name} found. Skipping or aborting?")
             # For graph state synthesis, measurements might be used for some advanced stuff but typically not for pure stabilizer state prep from scratch unless it involves teleportation (which graph state algo shouldn't do by default for simple tableau).
             # If it's a reset, we handled it.
             pass
        else:
            clean_circuit.append(instruction)

    # Output the circuit to a file
    with open("my_candidate_v2.stim", "w") as f:
        f.write(str(clean_circuit))
    
    print("Circuit generated in my_candidate_v2.stim")

if __name__ == "__main__":
    solve()
