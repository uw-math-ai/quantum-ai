import stim
import os

def generate_circuit():
    filepath = r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\stabilizers.txt"
    try:
        with open(filepath, "r") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        return
    
    # Clean up content: remove newlines, split by comma
    content = content.replace("\n", "").strip()
    # The stabilizers are separated by ", " in the prompt
    stabs = [s.strip() for s in content.split(",") if s.strip()]
    
    print(f"Found {len(stabs)} stabilizers.")
    if not stabs:
        print("No stabilizers found!")
        return

    n_qubits = len(stabs[0])
    print(f"Number of qubits: {n_qubits}")
    
    # Check consistency
    fixed_stabs = []
    for i, s in enumerate(stabs):
        if len(s) != n_qubits:
            print(f"Warning: Stabilizer {i} length mismatch. Expected {n_qubits}, got {len(s)}. Truncating/Padding.")
            if len(s) > n_qubits:
                s = s[:n_qubits]
            else:
                s = s.ljust(n_qubits, "I")
        fixed_stabs.append(s)
    
    stabs = fixed_stabs

    # Create tableau
    try:
        # Convert strings to stim.PauliString objects
        pauli_stabs = [stim.PauliString(s) for s in stabs]
        # allow_redundant=True handles potential redundant generators if any
        tableau = stim.Tableau.from_stabilizers(pauli_stabs, allow_redundant=True, allow_underconstrained=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # Synthesize circuit
    # graph_state method is generally good for creating a stabilizer state
    # It uses H, S, CZ gates.
    try:
        circuit = tableau.to_circuit(method="graph_state")
    except Exception as e:
        print(f"Error synthesizing circuit: {e}")
        return
    
    print("Generated circuit with ", len(circuit), " instructions.")
    # print(circuit)
    
    outpath = r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\circuit.stim"
    with open(outpath, "w") as f:
        f.write(str(circuit))

if __name__ == "__main__":
    generate_circuit()
