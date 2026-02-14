import stim
import sys

def solve():
    with open("stabilizers_124.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]
    
    print(f"Number of stabilizers: {len(lines)}")
    if len(lines) > 0:
        print(f"Length of first stabilizer: {len(lines[0])}")

    try:
        pauli_strings = [stim.PauliString(line) for line in lines]
        # This will fail because len(lines) != 120
        tableau = stim.Tableau.from_stabilizers(pauli_strings) 
        print("Successfully created tableau from stabilizers.")
    except Exception as e:
        print(f"Failed to create tableau from stabilizers: {e}")

if __name__ == "__main__":
    solve()
