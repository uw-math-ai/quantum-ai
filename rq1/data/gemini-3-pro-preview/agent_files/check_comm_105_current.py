import stim
import sys

def check():
    path = r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_105_current.txt"
    with open(path, 'r') as f:
        lines = [l.strip() for l in f if l.strip()]

    print(f"Loaded {len(lines)} stabilizers.")
    if not lines:
        return

    length = len(lines[0])
    print(f"Qubits: {length}")

    paulis = []
    for i, line in enumerate(lines):
        if len(line) != length:
            print(f"Error: Stabilizer {i} has length {len(line)}, expected {length}")
            return
        paulis.append(stim.PauliString(line))

    # Check commutativity
    anticommuting = []
    for i in range(len(paulis)):
        for j in range(i + 1, len(paulis)):
            if not paulis[i].commutes(paulis[j]):
                anticommuting.append((i, j))

    if anticommuting:
        print(f"Found {len(anticommuting)} anticommuting pairs.")
        for i, j in anticommuting[:10]:
            print(f"  {i} vs {j}")
    else:
        print("All stabilizers commute.")

    try:
        tableau = stim.Tableau.from_stabilizers(paulis, allow_underconstrained=True, allow_redundant=True)
        print("Tableau creation successful.")
        circuit = tableau.to_circuit("elimination")
        print("Circuit generation successful.")
        
        out_path = r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_105_candidate.stim"
        with open(out_path, "w") as f:
            f.write(str(circuit))
        print(f"Circuit saved to {out_path}")
        
    except Exception as e:
        print(f"Tableau/Circuit generation failed: {e}")

if __name__ == "__main__":
    check()
