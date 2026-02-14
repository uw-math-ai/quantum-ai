import stim
import sys

def solve():
    try:
        with open("C:\\Users\\anpaz\\Repos\\quantum-ai\\rq1\\target_stabilizers_63_v2.txt", "r") as f:
            stabs = [line.strip() for line in f if line.strip()]
        
        # Check lengths
        for s in stabs:
            if len(s) != 63:
                print(f"Error: Stabilizer length {len(s)} != 63: {s}", file=sys.stderr)
                return

        print(f"Loaded {len(stabs)} stabilizers.", file=sys.stderr)

        tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabs], allow_underconstrained=True)
        circuit = tableau.to_circuit("elimination")
        with open("circuit_attempt_63.stim", "w") as f:
            print(circuit, file=f)
        print("Circuit written to circuit_attempt_63.stim")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)

if __name__ == "__main__":
    solve()
