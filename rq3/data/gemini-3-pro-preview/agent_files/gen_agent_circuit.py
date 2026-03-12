import stim

def generate_circuit_from_stabilizers(filename):
    with open(filename, 'r') as f:
        content = f.read().strip()
    
    # Split by comma or newline, handle potential whitespace
    stabilizers = [s.strip() for s in content.replace('\n', '').split(',') if s.strip()]
    
    print(f"Loaded {len(stabilizers)} stabilizers.")
    if not stabilizers:
        raise ValueError("No stabilizers found")

    # Create PauliStrings
    paulis = [stim.PauliString(s) for s in stabilizers]
    
    # Synthesize tableau
    # Allow redundant because the list might be overcomplete or have dependencies
    # Allow underconstrained because we might not specify all qubits (though length suggests we do)
    tableau = stim.Tableau.from_stabilizers(paulis, allow_redundant=True, allow_underconstrained=True)
    
    # Synthesize circuit using graph_state method for optimal CX count (using CZ)
    circuit = tableau.to_circuit(method='graph_state')
    
    # Fix RX resets if present.
    # graph_state method often initializes with RX. If we assume start from |0>, RX is a reset.
    # We should replace RX with H on |0> to create |+> or similar.
    # But wait, RX gate in Stim IS a reset to X-basis? No, R_X is reset.
    # stim.Circuit.append("RX", targets) is a reset.
    # If the circuit starts with RX, it resets those qubits.
    # If the standard input is |0>, we don't need reset if we want to treat it as unitary on |0>.
    # However, if we want to ensure the state is prepared regardless of input, resets are good.
    # But often optimization challenges forbid resets if they weren't in baseline.
    # The baseline doesn't seem to have resets (it has CX and H).
    # So we should probably replace RX with H if the qubit is known to be 0.
    # Let's see what the circuit looks like.
    
    # Iterate and replace RX with H
    new_circuit = stim.Circuit()
    for instruction in circuit:
        if instruction.name == "RX":
            # Replace with H. RX resets to |+> (if it is a reset).
            # If we start at |0>, H takes us to |+>.
            # So RX is equivalent to H if we start at |0>.
            # But "RX" in Stim IS a reset.
            # We want to use unitary gates.
            new_circuit.append("H", instruction.targets_copy())
        else:
            new_circuit.append(instruction)
            
    return new_circuit

if __name__ == "__main__":
    circuit = generate_circuit_from_stabilizers("agent_stabilizers.txt")
    with open("agent_candidate.stim", "w") as f:
        f.write(str(circuit))
    print("Generated agent_candidate.stim")
