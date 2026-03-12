import stim
import sys

def solve():
    try:
        # Load stabilizers
        with open("target_stabilizers_job_v4.txt", "r") as f:
            lines = [l.strip() for l in f if l.strip()]
        
        print(f"Loaded {len(lines)} stabilizers.")
        
        # Create PauliStrings
        paulis = [stim.PauliString(l) for l in lines]
        
        # Check qubit count
        num_qubits = len(lines[0])
        print(f"Number of qubits: {num_qubits}")
        
        # Create Tableau
        # allow_redundant=True just in case, though usually for a full set it matches N
        # If len(lines) < num_qubits, allow_underconstrained=True
        
        t = stim.Tableau.from_stabilizers(paulis, allow_redundant=True, allow_underconstrained=True)
        
        # Synthesize circuit using graph state method (CZ gates, 0 CX)
        c = t.to_circuit(method="graph_state")
        
        new_c = stim.Circuit()
        for op in c:
            if op.name == "R":
                pass
            elif op.name == "RX":
                # RX is Reset to |+>. Input is |0>. Apply H to get |+>.
                new_c.append("H", op.targets_copy())
            elif op.name == "RY":
                pass
            else:
                new_c.append(op)
            
        # Verify the circuit has 0 CX
        cx_count = 0
        for op in new_c:
            if op.name == "CX" or op.name == "CNOT":
                cx_count += len(op.targets_copy()) // 2
            
        print(f"Generated circuit with {cx_count} CX gates.")
        
        with open("candidate_opt_v1.stim", "w") as f:
            f.write(str(new_c))
            
        print("Done.")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    solve()
