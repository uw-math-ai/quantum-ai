import stim
import sys

def generate_circuit():
    try:
        # Read stabilizers
        with open(r"C:\Users\anpaz\Repos\quantum-ai\rq3\data\gemini-3-pro-preview\agent_files\target_stabilizers_fixed.txt", "r") as f:
            lines = [line.strip() for line in f if line.strip()]

        print(f"Number of stabilizers: {len(lines)}", file=sys.stderr)
        if len(lines) > 0:
            print(f"Length of stabilizer 0: {len(lines[0])}", file=sys.stderr)

        # Convert to PauliStrings to be sure
        paulis = []
        for line in lines:
            paulis.append(stim.PauliString(line))

        tableau = stim.Tableau.from_stabilizers(paulis, allow_redundant=True, allow_underconstrained=True)
        
        # Method "graph_state" is key for low CX count.
        circuit = tableau.to_circuit(method="graph_state")
        
        # Verify it uses CZ not CX? 
        # Stim's graph state synthesis uses H, S, CZ.
        # But we need to ensure the final circuit is printed to stdout.
        print(circuit)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)

if __name__ == "__main__":
    generate_circuit()
