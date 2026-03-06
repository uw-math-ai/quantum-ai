import stim
import sys

def analyze():
    # Load stabilizers
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq3\data\agent_files\target_stabilizers_new.txt', 'r') as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    print(f"Number of stabilizers: {len(stabilizers)}")
    if stabilizers:
        print(f"Length of first stabilizer: {len(stabilizers[0])}")

    # Load baseline
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq3\data\agent_files\baseline_new.stim', 'r') as f:
        baseline_text = f.read()
    
    circuit = stim.Circuit(baseline_text)
    
    cx_count = 0
    volume = 0
    max_qubit = 0
    
    for instr in circuit:
        # Count CX
        if instr.name == "CX" or instr.name == "CNOT":
            cx_count += len(instr.targets_copy()) // 2
        
        # Calculate Volume: gate count in volume gate set
        # (CX, CY, CZ, H, S, SQRT_X, etc.)
        # Stim instructions can have multiple targets, e.g. H 0 1 2 is 3 H gates.
        # Two qubit gates like CX 0 1 2 3 count as 2 gates (one for 0->1, one for 2->3).
        if instr.name in ["CX", "CY", "CZ", "H", "S", "SQRT_X", "S_DAG", "SQRT_X_DAG", "X", "Y", "Z", "I"]:
             # This is an approximation of volume. The prompt defines volume as "total gate count in the volume gate set".
             # Usually standard Clifford gates.
             if instr.name in ["CX", "CY", "CZ"]:
                 volume += len(instr.targets_copy()) // 2
             else:
                 volume += len(instr.targets_copy())
        
        for target in instr.targets_copy():
            if target.value > max_qubit:
                max_qubit = target.value
                
    print(f"Baseline CX count: {cx_count}")
    print(f"Baseline Volume: {volume}")
    print(f"Max qubit index in baseline: {max_qubit}")
    
    # Try to synthesize using Tableau
    try:
        # Create a tableau from stabilizers
        # Note: stim.Tableau.from_stabilizers expects a list of PauliStrings
        # We need to ensure we have N stabilizers for N qubits for a full graph state synthesis,
        # or we can use the tableau to synthesize a state preparation circuit.
        # But we only have stabilizers. We assume they stabilize the +1 eigenstate.
        
        stabilizer_paulis = []
        for s in stabilizers:
            stabilizer_paulis.append(stim.PauliString(s))
            
        # If the number of stabilizers equals the number of qubits, we can try to form a Tableau.
        # The prompt implies we need to preserve these stabilizers.
        # If we have N stabilizers for N qubits, it specifies a unique state (stabilizer state).
        
        num_qubits = len(stabilizers[0])
        print(f"Num qubits derived from stabilizer length: {num_qubits}")
        
        if len(stabilizers) == num_qubits:
            print("Full set of stabilizers provided. Synthesizing from Tableau...")
            tableau = stim.Tableau.from_stabilizers(stabilizer_paulis, allow_redundant=True, allow_underconstrained=True)
            
            # Synthesize circuit
            synthesized_circuit = tableau.to_circuit(method="elimination")
            
            syn_cx = 0
            syn_vol = 0
            for instr in synthesized_circuit:
                if instr.name == "CX" or instr.name == "CNOT":
                    syn_cx += len(instr.targets_copy()) // 2
                
                if instr.name in ["CX", "CY", "CZ", "H", "S", "SQRT_X", "S_DAG", "SQRT_X_DAG", "X", "Y", "Z", "I"]:
                     if instr.name in ["CX", "CY", "CZ"]:
                         syn_vol += len(instr.targets_copy()) // 2
                     else:
                         syn_vol += len(instr.targets_copy())
            
            print(f"Synthesized CX count: {syn_cx}")
            print(f"Synthesized Volume: {syn_vol}")
            
            # Save synthesized circuit
            with open(r'C:\Users\anpaz\Repos\quantum-ai\rq3\data\agent_files\candidate_synth.stim', 'w') as f:
                f.write(str(synthesized_circuit))
        else:
            print("Not a full set of stabilizers. Cannot use simple Tableau.from_stabilizers for full state.")
            # We might still be able to do it if we pad with dummy stabilizers or check if it is a graph state.
            
    except Exception as e:
        print(f"Synthesis failed: {e}")

if __name__ == "__main__":
    analyze()
