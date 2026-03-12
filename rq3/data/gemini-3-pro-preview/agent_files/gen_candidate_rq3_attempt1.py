import stim
import sys

def generate_circuit():
    try:
        # Read stabilizers
        with open("target_stabilizers_rq3_unique_123.txt", "r") as f:
            lines = [line.strip() for line in f if line.strip()]

        # Convert to PauliStrings
        pauli_stabilizers = [stim.PauliString(line) for line in lines]

        # Create tableau
        # allow_redundant=True handles linearly dependent stabilizers
        # allow_underconstrained=True handles if we have fewer stabilizers than qubits
        t = stim.Tableau.from_stabilizers(pauli_stabilizers, allow_redundant=True, allow_underconstrained=True)

        # Synthesize circuit using graph state method (uses CZ, H, S, etc.)
        circuit = t.to_circuit(method="graph_state")

        # Post-process to replace RX with H
        new_circuit = stim.Circuit()
        for instr in circuit:
            if instr.name == "RX":
                # RX resets to |+>. Since we start at |0>, H transforms |0> to |+>.
                new_circuit.append("H", instr.targets_copy())
            elif instr.name == "R" or instr.name == "RZ":
                 # R resets to |0>. If we are already at |0> (at start), this is identity.
                 pass
            elif instr.name == "M":
                 # If synthesis added measurements, keep them but warn
                 # (graph state usually shouldn't for pure state prep)
                 print(f"Warning: Measurement found: {instr}", file=sys.stderr)
                 new_circuit.append(instr)
            else:
                new_circuit.append(instr)

        # Output to file
        with open("candidate_rq3_attempt1.stim", "w") as f:
            f.write(str(new_circuit))
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)

if __name__ == "__main__":
    generate_circuit()
