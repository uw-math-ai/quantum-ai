import stim
import sys

def main():
    try:
        print("Reading stabilizers...")
        with open("current_target_stabilizers.txt", "r") as f:
            lines = [line.strip() for line in f if line.strip()]
        
        print(f"Read {len(lines)} stabilizers.")
        paulis = []
        for l in lines:
            paulis.append(stim.PauliString(l))
            
        print("Creating tableau...")
        tableau = stim.Tableau.from_stabilizers(paulis, allow_redundant=True, allow_underconstrained=True)
        print(f"Tableau created. Qubits: {len(tableau)}")
        
        print("Synthesizing circuit...")
        circuit = tableau.to_circuit(method="graph_state")
        print(f"Circuit synthesized. Instructions: {len(circuit)}")
        
        new_circuit = stim.Circuit()
        for op in circuit:
            if op.name == "RX":
                for t in op.targets_copy():
                    new_circuit.append("H", [t])
            elif op.name in ["R", "RZ", "MY", "M"]:
                pass # Skip resets/measurements if input is |0>
            else:
                new_circuit.append(op)
                
        with open("candidate_graph.stim", "w") as f:
            f.write(str(new_circuit))
            
        print("candidate_graph.stim written.")
        
        cx = sum(1 for op in new_circuit if op.name == "CX")
        cz = sum(1 for op in new_circuit if op.name == "CZ")
        print(f"CX count: {cx}")
        print(f"CZ count: {cz}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
