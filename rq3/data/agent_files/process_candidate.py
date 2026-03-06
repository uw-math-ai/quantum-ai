import stim

def main():
    with open("candidate.stim", "r") as f:
        content = f.read()
    
    # Replace RX with H
    # We need to be careful not to replace R inside other words if any (unlikely in stim)
    # But stim instructions are space separated.
    # RX at start of line.
    
    lines = content.splitlines()
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("RX "):
            # Replace RX with H
            new_lines.append("H " + stripped[3:])
        elif stripped == "TICK":
            # Remove TICK
            pass
        else:
            new_lines.append(stripped)
            
    new_content = "\n".join(new_lines)
    
    with open("candidate_fixed.stim", "w") as f:
        f.write(new_content)
        
    print("Fixed candidate saved.")
    
    # Verify
    circuit = stim.Circuit(new_content)
    with open("target_stabilizers.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]
        
    sim = stim.TableauSimulator()
    sim.do_circuit(circuit)
    preserved = 0
    for s_str in stabilizers:
        s = stim.PauliString(s_str)
        if sim.peek_observable_expectation(s) == 1:
            preserved += 1
            
    print(f"Preserved: {preserved}/{len(stabilizers)}")
    
    # Check metrics
    cx = 0
    vol = 0
    for instr in circuit:
        n = len(instr.targets_copy())
        if instr.name in ["CX", "CNOT"]:
            cx += n // 2
            vol += n // 2
        elif instr.name in ["CZ", "CY"]:
             vol += n // 2
        elif instr.name in ["H", "S", "X", "Y", "Z", "I", "S_DAG", "SQRT_X", "SQRT_Y"]:
             vol += n
             
    print(f"Metrics: CX={cx}, Vol={vol}")

if __name__ == "__main__":
    main()
