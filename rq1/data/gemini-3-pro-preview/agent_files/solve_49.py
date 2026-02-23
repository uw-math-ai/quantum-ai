import stim
import sys

def solve():
    try:
        with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_49_v2.txt", "r") as f:
            lines = [l.strip() for l in f if l.strip()]

        stabilizers = [stim.PauliString(s) for s in lines]
        # This function finds a tableau T such that T|0> is stabilized by the given stabilizers.
        # It assumes the stabilizers are independent and commuting.
        # If not, it raises an error.
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
        circuit = tableau.to_circuit()
        
        print("SUCCESS")
        with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_49.stim", "w") as f:
            f.write(str(circuit))
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    solve()
