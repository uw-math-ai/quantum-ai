import stim
import sys

def main():
    try:
        # 1. Read stabilizers
        with open('target_stabilizers_150.txt', 'r') as f:
            lines = [l.strip() for l in f if l.strip()]
        
        print(f"Loaded {len(lines)} stabilizers.")
        
        # 2. Convert to Tableau
        # Use allow_underconstrained=True because we might have fewer stabilizers than qubits, 
        # or they might not fully define the state (though usually for optimization we assume they do).
        # We assume the qubits not involved are identity or irrelevant.
        # But wait, to_circuit needs a full tableau usually? 
        # Actually, from_stabilizers creates a Tableau. If underconstrained, it fills the rest with Z or X?
        # Let's see what happens.
        
        tableau = stim.Tableau.from_stabilizers(lines, allow_underconstrained=True)
        print(f"Tableau created. Size: {len(tableau)}")
        
        # 3. Synthesize circuit
        # method="graph_state" is the key for CX=0 (using CZs)
        circuit = tableau.to_circuit(method="graph_state")
        
        # 4. Clean circuit (Replace RX with H, remove R/M)
        # We iterate and rebuild
        new_circuit = stim.Circuit()
        
        for instruction in circuit:
            if instruction.name == "RX":
                # RX resets to |+>. Since we start at |0>, H does the same.
                # However, RX is a reset. H is a gate.
                # If the circuit relies on resetting an arbitrary state to |+>, then replacing with H is valid ONLY if the state is known to be |0>.
                # Since we are creating the state FROM SCRATCH (from |0>), the input to these RX gates IS |0> (or effectively we can assume we are preparing from |0>).
                # Wait, if `to_circuit` puts RX in the middle, it means it's resetting a qubit.
                # But for state preparation, usually it's at the beginning.
                targets = instruction.targets_copy()
                new_circuit.append("H", targets)
            elif instruction.name == "R" or instruction.name == "RZ":
                 # Reset to |0>. Since start is |0>, this is Identity.
                 # If in middle, it's a reset. But graph state synthesis shouldn't put resets in middle for pure state prep.
                 pass
            elif instruction.name == "M":
                 # Measurement. Should not happen.
                 pass
            else:
                 new_circuit.append(instruction)

        # 5. Output
        # Write to file for checking
        with open('candidate_150.stim', 'w') as f:
            f.write(str(new_circuit))
            
        print("Candidate circuit generated: candidate_150.stim")
        
        # Check metrics
        num_cx = new_circuit.num_gates("CX")
        num_cz = new_circuit.num_gates("CZ")
        print(f"CX count: {num_cx}")
        print(f"CZ count: {num_cz}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
