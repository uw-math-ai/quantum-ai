import stim
import sys

def solve():
    with open("stabilizers_35_task_v2.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]

    stabs = []
    for line in lines:
        stabs.append(stim.PauliString(line))

    print(f"Loaded {len(stabs)} stabilizers")
    
    # Check for anticommutativity
    for i in range(len(stabs)):
        for j in range(i+1, len(stabs)):
            if stabs[i].commutes(stabs[j]) == False:
                print(f"Anticommutation detected: {i} and {j}")
                # print(stabs[i])
                # print(stabs[j])

    # Try standard elimination
    try:
        t = stim.Tableau.from_stabilizers(stabs, allow_underconstrained=True)
        circuit = t.to_circuit("elimination")
        print("Circuit generated successfully")
        with open("circuit_35_task.stim", "w") as f:
            f.write(str(circuit))
    except Exception as e:
        print(f"Error generating circuit: {e}")

if __name__ == "__main__":
    solve()
