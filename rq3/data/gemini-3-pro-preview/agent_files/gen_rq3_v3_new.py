import stim
import sys

def main():
    try:
        # Load stabilizers
        with open("target_stabilizers_rq3_v3.txt", "r") as f:
            lines = [l.strip() for l in f if l.strip()]

        # Determine number of qubits from line length
        # All lines should be same length usually
        # But if inconsistent, use max length
        max_len = max(len(l) for l in lines)
        
        # Pad with I if needed? Or just create PauliStrings.
        # Stim handles different lengths if we are careful, but for Tableau we want consistent length.
        # Let's pad with 'I' to max_len.
        
        padded_lines = []
        for l in lines:
            if len(l) < max_len:
                l = l + "I" * (max_len - len(l))
            padded_lines.append(l)
            
        stabilizers = [stim.PauliString(l) for l in padded_lines]
        
        # Create Tableau
        # allow_redundant=True: if stabilizers are not independent
        # allow_underconstrained=True: if stabilizers don't specify full state (mixed state)
        # The prompt implies a pure state or subspace. 
        # If underconstrained, graph_state method might fill arbitrary values for remaining DOFs.
        # This is fine as long as it stabilizes the targets.
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
        
        # Synthesize
        circuit = tableau.to_circuit(method="graph_state")
        
        # Post-process to remove resets (assuming |0> input)
        # and convert RX/RY to gates
        clean_circuit = stim.Circuit()
        for op in circuit:
            # sys.stderr.write(f"Op: {op.name}, targets: {len(op.targets_copy())}\n")
            if op.name == "CZ" and len(op.targets_copy()) > 2:
                # Split large CZ into pairs
                targets = op.targets_copy()
                for i in range(0, len(targets), 2):
                    clean_circuit.append("CZ", targets[i:i+2])
            elif op.name == "R":
                # Reset to |0>. Input is |0>. Do nothing.
                continue
            elif op.name == "RX":
                # Reset to |+>. Input is |0>. Apply H.
                clean_circuit.append("H", op.targets_copy())
            elif op.name == "RY":
                # Reset to |i>. Input is |0>. Apply H, S.
                targets = op.targets_copy()
                clean_circuit.append("H", targets)
                clean_circuit.append("S", targets)
            elif op.name == "MPP":
                # Measurement based preparation? Graph state shouldn't use this usually.
                clean_circuit.append(op)
            else:
                clean_circuit.append(op)
        
        print(clean_circuit)

    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
