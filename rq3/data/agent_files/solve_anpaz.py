import stim

def generate_circuit():
    # Load stabilizers
    with open("my_target_stabilizers.txt", "r") as f:
        lines = f.readlines()
    
    # Parse line by line
    stabs = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Remove trailing commas if any
        line = line.strip(',')
        stabs.append(stim.PauliString(line))
    
    # Create tableau
    try:
        tableau = stim.Tableau.from_stabilizers(stabs, allow_underconstrained=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # Generate graph state circuit
    circuit = tableau.to_circuit(method="graph_state")
    
    # Process circuit to replace RX with H where possible (assuming |0> input)
    # Graph state circuit usually consists of:
    # 1. H gates on some qubits (or RX)
    # 2. CZ gates
    # 3. Final single qubit gates (H, S, etc.)
    
    # If we start from |0>, RX is equivalent to H.
    # We will parse the circuit string and replace RX with H.
    
    circuit_str = str(circuit)
    new_lines = []
    
    for line in circuit_str.split('\n'):
        if line.startswith("RX"):
            # Replace RX targets with H targets
            targets = line[3:].strip()
            new_lines.append(f"H {targets}")
        elif line.strip() == "TICK":
             continue
        else:
             new_lines.append(line)
             
    final_circuit_str = "\n".join(new_lines)
    
    with open("candidate.stim", "w") as f:
        f.write(final_circuit_str)
    
    print("Circuit written to candidate.stim")

    # Also try the standard elimination method which uses CX
    # circuit_elim = tableau.to_circuit(method="elimination")
    # print("---ELIM CIRCUIT---")
    # print(circuit_elim)

if __name__ == "__main__":
    generate_circuit()
