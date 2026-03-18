import stim
import sys

def load_stabilizers(filename):
    with open(filename, 'r') as f:
        # Read stabilizers from file, one per line
        content = f.read()
        # Split by newline or comma, just in case
        content = content.replace(',', '\n')
        stabilizers = [s.strip() for s in content.split('\n') if s.strip()]
    return stabilizers

def solve_stabilizers(stabilizers):
    # Determine number of qubits from length of first stabilizer
    num_qubits = len(stabilizers[0])
    
    # Convert strings to stim.PauliString
    pauli_stabilizers = [stim.PauliString(s) for s in stabilizers]
    
    # Create a tableau from the stabilizers
    # We want a circuit that prepares a state stabilized by these operators.
    # stim.Tableau.from_stabilizers can do this.
    try:
        tableau = stim.Tableau.from_stabilizers(pauli_stabilizers, allow_underconstrained=True, allow_redundant=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return None, None

    return tableau, num_qubits

def synthesize_graph_state(tableau):
    # Synthesize using graph_state method which uses CZ gates
    circuit = tableau.to_circuit(method="graph_state")
    
    # Convert RX gates to H gates if present (graph state synthesis might use RX for resets, 
    # but we assume starting from |0> so RX is equivalent to H? 
    # Actually RX is a rotation. Wait. stim's RX is a reset? No, R is reset. RX is not a standard gate in Stim?
    # Stim has 'R' (reset to 0), 'RX' (reset to +).
    # If the method produces 'RX', it means it wants to reset the qubit to |+>.
    # If we start from |0> (implicit), we can get to |+> with H.
    # However, 'to_circuit' usually produces unitary circuits if possible, or circuits with resets if not.
    # Let's inspect the output.
    
    return circuit

def clean_circuit(circuit):
    new_circuit = stim.Circuit()
    for instruction in circuit:
        if instruction.name == "RX":
            # RX is reset to |+> (or X basis reset).
            # If we assume start state is |0>, RX is equivalent to H (since H|0> = |+>).
            # If start state is already |+> (e.g. after H), RX is just identity (resetting to same state).
            # But graph state synthesis usually puts RX at the beginning to init in X basis.
            # So replacing RX with H is correct for |0> start.
            targets = instruction.targets_copy()
            new_circuit.append("H", targets)
        elif instruction.name in ["R", "RZ"]:
            # R/RZ is reset to |0> (Z basis reset).
            # At the start of the circuit (from |0>), this is identity.
            # If it appears later, we might need to keep it, but graph state synthesis 
            # for stabilizer states typically only resets at the start if at all.
            # We will ignore it, assuming it's at the start or redundant.
            pass 
        else:
            new_circuit.append(instruction)
            
    return new_circuit

def main():
    stabilizers = load_stabilizers("target_stabilizers_agent.txt")
    print(f"Loaded {len(stabilizers)} stabilizers.")
    
    tableau, num_qubits = solve_stabilizers(stabilizers)
    if tableau is None:
        print("Failed to create tableau.")
        return

    print(f"Synthesizing circuit for {num_qubits} qubits...")
    circuit = synthesize_graph_state(tableau)
    
    # Check for RX/R gates
    has_reset = any(op.name in ["R", "RX", "RY"] for op in circuit)
    print(f"Circuit has resets: {has_reset}")
    
    if has_reset:
        circuit = clean_circuit(circuit)
    
    # Output the candidate
    with open("candidate_agent.stim", "w") as f:
        f.write(str(circuit))
        
    # Analyze metrics
    cx = circuit.num_operations("CX")
    cz = circuit.num_operations("CZ")
    print(f"Candidate metrics: CX={cx}, CZ={cz}, Total operations={len(circuit)}")

if __name__ == "__main__":
    main()
