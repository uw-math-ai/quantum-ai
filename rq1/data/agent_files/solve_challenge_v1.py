import stim
import sys

def analyze_and_solve():
    with open('stabilizers.txt', 'r') as f:
        lines = [l.strip() for l in f if l.strip()]

    print(f"Loaded {len(lines)} stabilizers.")
    num_qubits = len(lines[0])
    print(f"Qubits: {num_qubits}")

    # Check length
    for i, line in enumerate(lines):
        if len(line) != num_qubits:
            print(f"Error: Stabilizer {i} has length {len(line)}, expected {num_qubits}")
            return

    # Check commutativity
    stabs = [stim.PauliString(s) for s in lines]
    for i in range(len(stabs)):
        for j in range(i+1, len(stabs)):
            if not stabs[i].commutes(stabs[j]):
                print(f"Error: Stabilizers {i} and {j} anti-commute!")
                return
    print("All stabilizers commute.")

    # Try to find a circuit
    try:
        # allow_underconstrained=True is needed because we have 30 stabilizers for 31 qubits (or similar)
        # Actually count is 30 in the file? Let's check.
        # The user provided 30 lines in the prompt?
        # Let's count them again.
        # The user prompt has a list.
        # "IIXIIXIIIIIIIIIIIIIIIIIIIXIIXII, ..., IIZIIIIIIIIIIIIIIZIZIIIIIZIIIII"
        # I copied them into stabilizers.txt.
        
        tableau = stim.Tableau.from_stabilizers(stabs, allow_underconstrained=True)
        print("Tableau created successfully.")
        
        circuit = tableau.to_circuit("elimination")
        print("Circuit generated.")
        
        with open('solution.stim', 'w') as f:
            f.write(str(circuit))
            
    except Exception as e:
        print(f"Error generating circuit: {e}")

if __name__ == "__main__":
    analyze_and_solve()
