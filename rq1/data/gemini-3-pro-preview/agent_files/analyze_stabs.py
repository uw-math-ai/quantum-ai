import stim
import sys

def analyze_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    num_qubits = len(lines[0])
    print(f"Number of qubits: {num_qubits}")
    print(f"Number of stabilizers: {len(lines)}")

    # Check length consistency
    for i, line in enumerate(lines):
        if len(line) != num_qubits:
            print(f"Error: Stabilizer {i} has length {len(line)}, expected {num_qubits}")
            return

    # Check commutativity
    paulis = [stim.PauliString(line) for line in lines]
    anticommuting_pairs = []
    for i in range(len(paulis)):
        for j in range(i + 1, len(paulis)):
            if not paulis[i].commutes(paulis[j]):
                anticommuting_pairs.append((i, j))
    
    if anticommuting_pairs:
        print(f"Found {len(anticommuting_pairs)} anticommuting pairs.")
        for i, j in anticommuting_pairs[:10]:
            print(f"  {i} and {j} anticommute")
        if len(anticommuting_pairs) > 10:
            print("  ...")
    else:
        print("All stabilizers commute.")

    # Check for independent generators if they commute
    if not anticommuting_pairs:
        tableau = stim.Tableau.from_stabilizers(paulis, allow_underconstrained=True)
        print(f"Stabilizers are consistent and independent (or underconstrained).")
        print(f"Tableau shape: {len(tableau)} qubits")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        analyze_stabilizers(sys.argv[1])
    else:
        print("Usage: python analyze_stabs.py <filename>")
