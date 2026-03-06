import stim

def clean_circuit():
    with open("data/agent_files/candidate_graph.stim", "r") as f:
        lines = f.readlines()
    
    new_lines = []
    # Add H on all qubits 0..91
    qubits = " ".join(str(i) for i in range(92))
    new_lines.append(f"H {qubits}\n")
    
    for line in lines:
        if line.startswith("RX"):
            continue
        if line.strip() == "TICK":
            continue
        new_lines.append(line)
        
    circuit_text = "".join(new_lines)
    
    with open("data/agent_files/candidate_clean.stim", "w") as f:
        f.write(circuit_text)
    
    print("Created data/agent_files/candidate_clean.stim")
    
    # Verify
    c = stim.Circuit(circuit_text)
    
    # Count metrics
    cx = 0
    vol = 0
    for instr in c:
        if instr.name in ["CX", "CNOT"]:
            cx += len(instr.targets_copy()) // 2
        
        # Assume X, Y, Z, H, S, CZ etc are all volume 1 per target/interaction
        # Prompt: "volume gate set (CX, CY, CZ, H, S, SQRT_X, etc.)"
        # I will include X, Y, Z, I, S_DAG, etc.
        if instr.name in ["CX", "CNOT", "CY", "CZ"]:
             vol += len(instr.targets_copy()) // 2
        else:
             vol += len(instr.targets_copy())
             
    print(f"Cleaned CX: {cx}")
    print(f"Cleaned Volume (conservative): {vol}")
    
    # Check stabilizers
    check_preservation(c)

def check_preservation(circuit):
    with open("data/agent_files/raw_stabilizers.txt", 'r') as f:
        content = f.read()
    stabs = []
    for part in content.replace('\n', ',').split(','):
        s = part.strip()
        if s:
            stabs.append(stim.PauliString(s))

    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    preserved = 0
    for s in stabs:
        if sim.peek_observable_expectation(s) == 1:
            preserved += 1
            
    print(f"Preserved {preserved}/{len(stabs)} stabilizers")
    if preserved == len(stabs):
        print("VALID: All stabilizers preserved.")
    else:
        print("INVALID: Some stabilizers not preserved.")

if __name__ == "__main__":
    clean_circuit()
