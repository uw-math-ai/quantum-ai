import sys
import stim
import traceback
import json
import os

base_dir = r"C:\Users\anpaz\Repos\quantum-ai\rq1"

def analyze_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [l.strip() for l in f if l.strip()]
    
    print(f"Number of stabilizers: {len(lines)}")
    if not lines:
        return

    num_qubits = len(lines[0])
    print(f"Number of qubits: {num_qubits}")
    
    try:
        # Convert strings to PauliStrings
        pauli_stabilizers = [stim.PauliString(s) for s in lines]
        
        # Create a tableau from the stabilizers
        t = stim.Tableau.from_stabilizers(pauli_stabilizers, allow_redundant=True, allow_underconstrained=True)
        print(f"Successfully created Tableau.")
        
        # Get the circuit.
        c = t.to_circuit()
        
        print(f"Circuit generated with {len(c)} instructions.")
        
        # Write tool input with correct structure
        output = {
            "circuit": str(c),
            "stabilizers": lines
        }
        
        output_path = os.path.join(base_dir, "data", "gemini-3-pro-preview", "agent_files", "tool_input_v2.json")
        with open(output_path, "w") as f:
            json.dump(output, f, indent=2)
        
        print(f"Written to {output_path}")

    except Exception as e:
        print(f"Error creating Tableau/Circuit: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    analyze_stabilizers(os.path.join(base_dir, "data", "gemini-3-pro-preview", "agent_files", "stabilizers_81_v2.txt"))
