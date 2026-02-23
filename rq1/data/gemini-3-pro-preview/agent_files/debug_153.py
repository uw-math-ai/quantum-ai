import stim
import sys

def check_stabilizer_indices():
    failing_stab = "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZZIIIIIIIIIIZII"
    # This stabilizer is index 144 in the tool output: "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZZIIIIIIIIIIZII"
    # Let's count length
    print(f"Length failing: {len(failing_stab)}")
    
    # Read the file
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_153.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    print(f"Loaded {len(lines)} stabilizers from file.")
    if failing_stab in lines:
        print(f"Failing stabilizer IS in the file at index {lines.index(failing_stab)}")
    else:
        print("Failing stabilizer NOT found in file.")
    
    # Create tableau
    t = stim.Tableau.from_stabilizers(lines)
    print(f"Tableau created. Size: {len(t)}")
    
    # Generate circuit
    c = t.to_circuit()
    print(f"Circuit num_qubits: {c.num_qubits}")
    
    # Check max qubit index used
    max_q = 0
    for instr in c:
        # Some instructions don't have targets (e.g. TICK), but usually they do
        for target in instr.targets_copy():
             if target.value > max_q:
                 max_q = target.value
    print(f"Max qubit index in circuit: {max_q}")

if __name__ == "__main__":
    check_stabilizer_indices()
