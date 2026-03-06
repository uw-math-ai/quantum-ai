import stim
import sys

def solve():
    # Read stabilizers
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\stabilizers_60.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]
    
    stabilizers = []
    for line in lines:
        # Handle comma separation if present (though I put them on newlines)
        parts = line.split(',')
        for part in parts:
            part = part.strip()
            if part:
                stabilizers.append(stim.PauliString(part))
    
    print(f"Loaded {len(stabilizers)} stabilizers.")
    
    # Create tableau
    try:
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # Convert to circuit
    circuit = tableau.to_circuit("elimination")
    
    # Verify
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    all_good = True
    for i, s in enumerate(stabilizers):
        exp = sim.peek_observable_expectation(s)
        if exp != 1:
            print(f"Stabilizer {i} not preserved. Expectation: {exp}")
            all_good = False
            
    if all_good:
        print("All stabilizers preserved.")
        with open("circuit_60.stim", "w") as f:
            f.write(str(circuit))
        print("Circuit saved to circuit_60.stim")
    else:
        print("Circuit failed verification.")

if __name__ == "__main__":
    solve()
