import stim
import sys

def solve():
    try:
        with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers.txt', 'r') as f:
            lines = [line.strip() for line in f if line.strip()]

        print(f"Read {len(lines)} stabilizers.", file=sys.stderr)

        if not lines:
            print("No stabilizers found!", file=sys.stderr)
            return

        # Parse stabilizers
        stabilizers = []
        for line in lines:
            stabilizers.append(stim.PauliString(line))

        # Generate circuit
        # allow_underconstrained=True is important because we might not specify all degrees of freedom
        # but the prompt says "Act on exactly 186 data qubits".
        # The stabilizers are length 186.
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True, allow_redundant=True)
        circuit = tableau.to_circuit("elimination")
        print(circuit)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)

if __name__ == "__main__":
    solve()
