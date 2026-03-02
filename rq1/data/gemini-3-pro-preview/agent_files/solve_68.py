import stim
import sys

def solve():
    try:
        with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_68.txt", "r") as f:
            lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("Stabilizers file not found.")
        return

    stabilizers = []
    for line in lines:
        # Filter out invalid characters if any, though the file should be clean
        clean_line = "".join(c for c in line if c in "IXYZ")
        if len(clean_line) == 68:
            stabilizers.append(clean_line)
        else:
            print(f"Skipping line with invalid length: {len(clean_line)}")

    if not stabilizers:
        print("No valid stabilizers found.")
        return

    num_qubits = len(stabilizers[0])
    print(f"Number of qubits: {num_qubits}")
    print(f"Number of stabilizers: {len(stabilizers)}")

    # Check for commutativity
    print("Checking commutativity...")
    anticommuting_pairs = []
    for i in range(len(stabilizers)):
        p1 = stim.PauliString(stabilizers[i])
        for j in range(i + 1, len(stabilizers)):
            p2 = stim.PauliString(stabilizers[j])
            if not p1.commutes(p2):
                anticommuting_pairs.append((i, j))
                # print(f"Stabilizers {i} and {j} anticommute")
                if len(anticommuting_pairs) > 50:
                     break
        if len(anticommuting_pairs) > 50:
            break

    if anticommuting_pairs:
        print(f"Found {len(anticommuting_pairs)} anticommuting pairs.")
    else:
        print("All stabilizers commute.")

    # Try to generate tableau from stabilizers
    # If they anticommute, we might want to prioritize a maximal commuting set?
    # Or just try stim's best effort?
    
    try:
        tableau = stim.Tableau.from_stabilizers(
            [stim.PauliString(s) for s in stabilizers],
            allow_redundant=True,
            allow_underconstrained=True
        )
        circuit = tableau.to_circuit()
        print("Circuit generated successfully.")
        
        with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit.stim", "w") as f:
            f.write(str(circuit))
            
    except Exception as e:
        print(f"Error generating circuit: {e}")

if __name__ == "__main__":
    solve()
