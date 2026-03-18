import stim
import traceback

def solve():
    try:
        lines = []
        with open("current_stabilizers.txt", "r") as f:
            for l in f:
                l = l.strip().replace(",", "")
                if l:
                    try:
                        lines.append(stim.PauliString(l))
                    except ValueError:
                        pass # Skip empty lines
        
        # Create tableau from stabilizers
        # allow_underconstrained=True handles cases where fewer stabilizers than qubits are provided
        tableau = stim.Tableau.from_stabilizers(lines, allow_underconstrained=True)
        
        # Synthesize circuit using graph state method
        # This typically produces a circuit with H and CZ gates.
        circuit = tableau.to_circuit(method="graph_state")
        
        # Post-process circuit
        new_circuit = stim.Circuit()
        for instruction in circuit:
            if instruction.name == "RX":
                # RX is reset to X-basis (|0> -> |+>). Since we start in |0>, this is just H.
                new_circuit.append("H", instruction.targets_copy())
            elif instruction.name == "R":
                # R is reset to Z-basis (|0> -> |0>). Since we start in |0>, this is identity.
                pass
            elif instruction.name == "RY":
                 # Prepare |i>. H -> |+>, S -> |i>.
                 new_circuit.append("H", instruction.targets_copy())
                 new_circuit.append("S", instruction.targets_copy())
            else:
                new_circuit.append(instruction)
        
        print(new_circuit)

    except Exception:
        traceback.print_exc()

if __name__ == "__main__":
    solve()
