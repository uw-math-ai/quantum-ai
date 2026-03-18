import stim
import sys

def main():
    try:
        # Load baseline
        with open("baseline.stim", "r") as f:
            baseline_text = f.read()
        baseline_circuit = stim.Circuit(baseline_text)
        
        # Load stabilizers
        with open("target_stabilizers.txt", "r") as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
        
        num_qubits = len(lines[0])
        print(f"Number of qubits in stabilizers: {num_qubits}")
        
        stabilizers = []
        for line in lines:
            stabilizers.append(stim.PauliString(line))
            
        # Verify baseline stabilizes targets
        # Note: from_circuit computes T such that T|0> is the state.
        # We check if T|0> is stabilized by S.
        # i.e. S * (T|0>) = (T|0>)
        # <=> T^-1 * S * T * |0> = |0>
        # <=> T^-1 * S * T is a Z-type Pauli (all Z or I).
        # Actually stim has a helper for this.
        
        baseline_cx = sum(1 for op in baseline_circuit if op.name == "CX")
        print(f"Baseline CX count: {baseline_cx}")
        
        # Try graph state synthesis
        print("Synthesizing graph state...")
        # Note: allow_underconstrained=True fills missing stabilizers with Z operators.
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
        
        graph_circuit = tableau.to_circuit(method="graph_state")
        
        # Decompose CZ to CX
        final_circuit = stim.Circuit()
        for op in graph_circuit:
            if op.name == "CZ":
                targets = op.targets_copy()
                # CZ can take multiple pairs. Decompose each.
                for i in range(0, len(targets), 2):
                    c = targets[i]
                    t = targets[i+1]
                    # CZ(c, t) = H(t) CX(c, t) H(t)
                    final_circuit.append("H", [t])
                    final_circuit.append("CX", [c, t])
                    final_circuit.append("H", [t])
            elif op.name == "H":
                final_circuit.append("H", op.targets_copy())
            elif op.name == "S":
                final_circuit.append("S", op.targets_copy())
            elif op.name == "X":
                final_circuit.append("X", op.targets_copy())
            elif op.name == "Y":
                final_circuit.append("Y", op.targets_copy())
            elif op.name == "Z":
                final_circuit.append("Z", op.targets_copy())
            elif op.name == "I":
                pass
            else:
                # Other gates? Graph state usually only has H, S, CZ, X, Y, Z, I.
                # Maybe S_DAG?
                final_circuit.append(op)
                
        final_cx = sum(1 for op in final_circuit if op.name == "CX")
        print(f"Graph state circuit CX count (decomposed): {final_cx}")
        
        with open("candidate.stim", "w") as f:
            # Write without fences
            f.write(str(final_circuit).replace("circuit", "").strip())
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
