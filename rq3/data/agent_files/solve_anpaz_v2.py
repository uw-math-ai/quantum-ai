import stim
import sys

def solve():
    # Read stabilizers
    with open('target_stabilizers_anpaz.txt', 'r') as f:
        lines = [l.strip() for l in f if l.strip()]
    
    # Check length
    if not lines:
        print("No stabilizers found")
        return

    n_qubits = len(lines[0])
    print(f"Number of qubits: {n_qubits}")
    print(f"Number of stabilizers: {len(lines)}")

    stabilizers = []
    for line in lines:
        stabilizers.append(stim.PauliString(line))

    # Create tableau
    try:
        # allow_underconstrained=True because we might have fewer stabilizers than qubits
        # and we just want to find *a* state that satisfies them.
        t = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # Synthesize circuit
    # method='graph_state' is usually best for CZ count (and thus CX count)
    circuit = t.to_circuit(method="graph_state")
    
    # Post-process circuit
    # 1. Expand CZ to CX
    # 2. Replace RX with H
    # 3. Remove R
    
    new_circuit = stim.Circuit()
    
    for instruction in circuit:
        if instruction.name == "CZ":
            targets = instruction.targets_copy()
            for i in range(0, len(targets), 2):
                c = targets[i].value
                t_idx = targets[i+1].value
                # CZ(c, t) = H(t) CX(c, t) H(t)
                # But check if we can optimize. 
                # For now, just direct translation.
                new_circuit.append("H", [t_idx])
                new_circuit.append("CX", [c, t_idx])
                new_circuit.append("H", [t_idx])
        elif instruction.name == "RX":
            # RX assumes reset to 0 then H.
            # We assume start at 0. So just H.
            targets = instruction.targets_copy()
            new_circuit.append("H", [t.value for t in targets])
        elif instruction.name == "R":
            # Reset to 0. We assume start at 0. Ignore.
            pass
        elif instruction.name == "H":
            new_circuit.append("H", [t.value for t in instruction.targets_copy()])
        elif instruction.name == "S":
            new_circuit.append("S", [t.value for t in instruction.targets_copy()])
        elif instruction.name == "X":
             new_circuit.append("X", [t.value for t in instruction.targets_copy()])
        elif instruction.name == "Z":
             new_circuit.append("Z", [t.value for t in instruction.targets_copy()])
        elif instruction.name == "Y":
             new_circuit.append("Y", [t.value for t in instruction.targets_copy()])
        elif instruction.name == "CX":
             new_circuit.append("CX", [t.value for t in instruction.targets_copy()])
        else:
            # Pass through other gates (like SQRT_X, etc if they appear)
            new_circuit.append(instruction)

    print("\n---CANDIDATE START---")
    print(new_circuit)
    print("---CANDIDATE END---")

if __name__ == "__main__":
    solve()
