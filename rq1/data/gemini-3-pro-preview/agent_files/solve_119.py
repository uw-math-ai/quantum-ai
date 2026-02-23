import stim
import sys

def check_stabilizers(filename):
    print(f"Reading from {filename}")
    try:
        with open(filename, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"File not found: {filename}")
        return

    stabs = [stim.PauliString(line) for line in lines]
    if not stabs:
        print("No stabilizers found.")
        return

    num_qubits = len(stabs[0])
    print(f"Number of stabilizers: {len(stabs)}")
    print(f"Number of qubits: {num_qubits}")

    # Check for commutativity
    print("Checking commutativity...")
    anticommuting_pairs = []
    for i in range(len(stabs)):
        for j in range(i + 1, len(stabs)):
            if not stabs[i].commutes(stabs[j]):
                anticommuting_pairs.append((i, j))

    if anticommuting_pairs:
        print(f"Found {len(anticommuting_pairs)} anticommuting pairs.")
        for i, j in anticommuting_pairs[:10]:
            print(f"  {i} and {j} anticommute")
    else:
        print("All stabilizers commute.")

    # Try to generate circuit
    print("Attempting to generate circuit...")
    try:
        tableau = stim.Tableau.from_stabilizers(stabs, allow_underconstrained=True, allow_redundant=True)
        print("Tableau created successfully.")
        circuit = tableau.to_circuit("elimination")
        print("Circuit created successfully.")
        
        # Write using absolute path to be safe, although script uses relative
        with open("data/gemini-3-pro-preview/agent_files/circuit_119.stim", "w") as f:
            f.write(str(circuit))
        print(f"Writing circuit to data/gemini-3-pro-preview/agent_files/circuit_119.stim")
    except Exception as e:
        print(f"Failed to generate circuit: {e}")

if __name__ == "__main__":
    check_stabilizers("data/gemini-3-pro-preview/agent_files/stabilizers_119.txt")