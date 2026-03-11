import stim
import sys

def solve():
    try:
        # Read file, split by newlines (or commas if they exist inside lines)
        with open('target_stabilizers_job.txt', 'r') as f:
            content = f.read()
            # Split by comma first if present, then cleanup
            if ',' in content:
                parts = content.split(',')
            else:
                parts = content.splitlines()
            
            lines = [p.strip() for p in parts if p.strip()]
        
        # Check lengths
        lengths = set(len(l) for l in lines)
        if len(lengths) > 1:
            print(f"Error: Inconsistent stabilizer lengths: {lengths}")
            for i, l in enumerate(lines):
                if len(l) != 125: # Assuming 125 is the target
                     print(f"Line {i} has length {len(l)}: '{l}'")
            return
            
        num_qubits = len(lines[0])
        print(f"Number of qubits: {num_qubits}")
        print(f"Number of stabilizers: {len(lines)}")
        
        # Attempt to create tableau
        # If the number of stabilizers is less than qubits, allow_underconstrained=True
        try:
            # Remove duplicates first
            unique_lines = sorted(list(set(lines)))
            if len(unique_lines) < len(lines):
                 print(f"Removed {len(lines) - len(unique_lines)} duplicate stabilizers.")
            
            pauli_stabilizers = [stim.PauliString(s) for s in unique_lines]
            tableau = stim.Tableau.from_stabilizers(pauli_stabilizers, allow_underconstrained=True, allow_redundant=True)
            print("Successfully created tableau from stabilizers.")
        except Exception as e:
            print(f"Error creating tableau: {e}")
            return

        # Generate graph state circuit
        try:
            circuit_graph = tableau.to_circuit(method='graph_state')
            print("Successfully created graph_state circuit.")
            with open('candidate_graph.stim', 'w') as f:
                f.write(str(circuit_graph))
        except Exception as e:
             print(f"Error creating graph_state circuit: {e}")

        # Generate elimination circuit
        try:
            circuit_elim = tableau.to_circuit(method='elimination')
            print("Successfully created elimination circuit.")
            with open('candidate_elim.stim', 'w') as f:
                f.write(str(circuit_elim))
        except Exception as e:
             print(f"Error creating elimination circuit: {e}")

    except Exception as e:
        print(f"General error: {e}")

if __name__ == "__main__":
    solve()
