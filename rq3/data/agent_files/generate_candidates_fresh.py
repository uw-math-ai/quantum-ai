import stim
import sys

def load_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    return [stim.PauliString(line) for line in lines]

def synthesize_circuit(stabilizers):
    # Try graph state synthesis
    try:
        # Create a tableau from the stabilizers
        # Note: from_stabilizers requires a full set of N stabilizers for N qubits
        # or we can use from_stabilizers with allow_underconstrained=True
        
        # Check qubit count
        num_qubits = len(stabilizers[0])
        print(f"Num qubits: {num_qubits}")
        
        # Need to ensure we have a full tableau or handle underconstrained
        # If the stabilizers are not full rank, we might need to complete them or use a different method.
        # But let's try assuming they define a stabilizer state.
        
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
        
        # Method 'graph_state' is usually good for low CX count (uses CZs)
        circuit = tableau.to_circuit(method="graph_state")
        
        return circuit
    except Exception as e:
        print(f"Error synthesizing: {e}")
        return None

def main():
    stabilizers = load_stabilizers("target_stabilizers.txt")
    print(f"Loaded {len(stabilizers)} stabilizers")
    
    circuit = synthesize_circuit(stabilizers)
    
    if circuit:
        with open("candidate.stim", "w") as f:
            f.write(str(circuit))
        print("Candidate circuit generated in candidate.stim")
        
        # Print stats
        print(f"Circuit instructions: {len(circuit)}")
        # Approximate CX count
        cx = 0
        cz = 0
        for instr in circuit:
            if instr.name == "CX" or instr.name == "CNOT":
                cx += len(instr.targets_copy()) // 2
            elif instr.name == "CZ":
                cz += len(instr.targets_copy()) // 2
        print(f"CX count: {cx}")
        print(f"CZ count: {cz}")
    else:
        print("Failed to generate circuit")

if __name__ == "__main__":
    main()
