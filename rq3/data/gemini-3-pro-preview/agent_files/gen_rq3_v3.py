import stim
import sys

def main():
    try:
        with open("stabilizers_rq3.txt", "r") as f:
            lines = [line.strip() for line in f if line.strip()]

        # Truncate to 84 characters (qubits 0..83)
        # This assumes extra chars are "II" or padding.
        target_len = 84
        truncated_lines = []
        for line in lines:
            if len(line) > target_len:
                truncated_lines.append(line[:target_len])
            else:
                truncated_lines.append(line)

        stabilizers = []
        for line in truncated_lines:
            stabilizers.append(stim.PauliString(line))

        # Create tableau
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
        
        # Synthesize using graph state method
        circuit = tableau.to_circuit(method="graph_state")
        
        # Post-process: Remove RX (resets) as we assume |0> input
        clean_circuit = stim.Circuit()
        for op in circuit:
            if op.name in ["R", "RX", "RY", "RZ"]:
                # Check if it's resetting to |0>. If so, ignore.
                # If it's resetting to something else, we might need a gate.
                # RX usually resets to |0> (or measures Z). Wait.
                # RX is "Reset X". It resets to |+> or |->.
                # R is "Reset Z". It resets to |0> or |1>.
                # Stim's graph state synthesis often emits R or RX for initialization.
                # If the target state requires |+>, it uses RX? No, usually H on |0>.
                # If the circuit starts with RX, it prepares |+>.
                # If we remove RX, we start with |0>. Then we need H.
                # Wait.
                # If to_circuit emits "RX 0", it means "Reset qubit 0 to |+>".
                # If our input is |0>, we should apply H 0.
                # If to_circuit emits "R 0", it means "Reset qubit 0 to |0>".
                # If our input is |0>, we do nothing (Identity).
                # So:
                # RX -> H
                # R -> I (remove)
                # RY -> S H Sdag? (Reset to Y basis)
                # Usually graph state uses X basis initialization (RX).
                # So RX -> H is correct.
                # Let's verify if to_circuit emits RX or R.
                pass
            
            # Actually, to_circuit(method="graph_state") creates a circuit that PREPARES the state.
            # It starts from nothing (resets).
            # If we assume |0> input, we replace initialization with gates.
            pass
        
        # Let's inspect the circuit and replace resets.
        final_circuit = stim.Circuit()
        for op in circuit:
            if op.name == "RX":
                # RX resets to |+>. From |0>, H does this.
                final_circuit.append("H", op.targets_copy())
            elif op.name == "R":
                # R resets to |0>. From |0>, I does this.
                pass
            elif op.name == "RY":
                # RY resets to |i+>. From |0>, H S does this?
                # H -> |+>, S -> |i+>. Yes.
                targets = op.targets_copy()
                final_circuit.append("H", targets)
                final_circuit.append("S", targets)
            else:
                final_circuit.append(op)
                
        print(final_circuit)
        
    except Exception as e:
        sys.stderr.write(str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()