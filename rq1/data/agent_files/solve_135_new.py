import stim
import sys

def solve():
    print("Reading stabilizers...")
    with open("stabilizers_135_new.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    print(f"Read {len(lines)} lines.")
    if len(lines) == 0:
        print("No stabilizers found.")
        return

    num_qubits = len(lines[0])
    print(f"Num qubits: {num_qubits}")
    
    # Verify all lengths
    for i, line in enumerate(lines):
        if len(line) != num_qubits:
            print(f"Error: Line {i+1} has length {len(line)}, expected {num_qubits}")
            # return # Don't return, just warn for now to see all errors
    
    stabilizers = []
    for line in lines:
        if len(line) == num_qubits:
            stabilizers.append(stim.PauliString(line))

    print(f"Loaded {len(stabilizers)} valid stabilizers.")

    # Check for independence
    try:
        t = stim.Tableau.from_stabilizers(stabilizers)
        print("Tableau created successfully from the provided stabilizers.")
        c = t.to_circuit()
        with open("circuit_135_new.stim", "w") as f:
            f.write(str(c))
        print("Circuit saved to circuit_135_new.stim")
        return
    except Exception as e:
        print(f"Direct tableau creation failed: {e}")

    # If we are here, we might have fewer stabilizers than qubits, or they are dependent.
    # Let's check independence first.
    # We can do Gaussian elimination on the check matrix.
    
    # But wait, if they are independent but fewer than num_qubits, from_stabilizers SHOULD FAIL?
    # Documentation says: "The number of stabilizers must match the number of qubits."
    # If we have 128 stabilizers for 135 qubits, it will definitely fail.
    
    print("Stabilizer count < Num Qubits. Need to complete the stabilizer set.")
    
    # We need to add 135 - 128 = 7 stabilizers that commute with existing ones and are independent.
    # The simplest way is to find the logical operators or just fill the tableau.
    
    # We can use the check matrix to find the null space (Z stabilizers) and extend it?
    # Or simpler: try adding single-qubit Z or X operators on the qubits that are 'empty' or relevant.
    
    # Let's try to identify 'missing' stabilizers.
    # The stabilizers seem to come in groups.
    # Let's analyze the provided set.
    pass


if __name__ == "__main__":
    solve()
