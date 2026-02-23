import stim
import sys

def solve():
    try:
        # Use the fixed stabilizers (subset of 97 commuting ones)
        with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_fixed.txt', 'r') as f:
            lines = [line.strip() for line in f if line.strip()]

        print(f"Read {len(lines)} stabilizers.", file=sys.stderr)

        stabilizers = []
        for line in lines:
            stabilizers.append(stim.PauliString(line))

        # Generate circuit for the 97 consistent stabilizers
        # allow_underconstrained=True is crucial as we have 97 stabilizers for 186 qubits (186-97 = 89 logical qubits)
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True, allow_redundant=True)
        circuit = tableau.to_circuit("elimination")
        print(circuit)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)

if __name__ == "__main__":
    solve()
