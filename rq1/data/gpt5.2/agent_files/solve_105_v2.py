import stim
import sys
import os

def solve():
    # Read stabilizers
    stab_path = r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_105.txt"
    with open(stab_path, "r") as f:
        lines = [l.strip() for l in f if l.strip()]

    stabilizers = []
    for line in lines:
        stabilizers.append(stim.PauliString(line))

    print(f"Loaded {len(stabilizers)} stabilizers.")

    # Create tableau
    try:
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True, allow_redundant=True)
    except Exception as e:
        print(f"Failed to create tableau: {e}")
        return

    # Convert to circuit
    try:
        circuit = tableau.to_circuit("elimination")
    except Exception as e:
        print(f"Failed to generate circuit: {e}")
        return

    print("Circuit generated.")

    # Verify
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    # Check each stabilizer
    all_good = True
    for s in stabilizers:
        # Measure the stabilizer. Result should be deterministic +1 (False in stim convention usually means +1 eigenvalue for Z? No, measure returns True/False)
        # Wait, measurement results: False -> +1, True -> -1 usually.
        # But we can check expectation value directly.
        # expectation_value returns +1, -1, or 0.
        ev = sim.peek_observable_expectation(s)
        if ev != 1:
            print(f"Stabilizer {s} not satisfied! Expectation: {ev}")
            all_good = False
            break
    
    if all_good:
        print("Verification SUCCESS: All stabilizers satisfied.")
        out_path = r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_105.stim"
        with open(out_path, "w") as f:
            f.write(str(circuit))
        print(f"Circuit saved to {out_path}")
    else:
        print("Verification FAILED.")

if __name__ == "__main__":
    solve()
