import stim

def main():
    with open("stabilizers_task_v2.txt", 'r') as f:
        line = f.readline().strip()
    print(f"Stabilizer length: {len(line)}")
    
    # Process the candidate circuit
    with open("candidate_graph_state.stim", 'r') as f:
        content = f.read()
        
    # Replace RX with H for initialization (assuming |0> input)
    # RX resets to |+>. H|0> = |+>.
    # Also remove TICKs to be clean
    
    lines = content.splitlines()
    new_lines = []
    for line in lines:
        if line.startswith("RX"):
            # Replace RX with H
            new_lines.append(line.replace("RX", "H"))
        elif line.startswith("TICK"):
            continue
        else:
            new_lines.append(line)
            
    new_circuit_text = "\n".join(new_lines)
    
    with open("best_candidate.stim", "w") as f:
        f.write(new_circuit_text)
        
    # Check metrics of the fixed circuit
    c = stim.Circuit(new_circuit_text)
    
    # Real count
    cx = 0
    for instr in c:
        if instr.name in ["CX", "CNOT"]:
            cx += len(instr.targets_copy()) // 2
    print(f"Best Candidate Real CX: {cx}")

if __name__ == "__main__":
    main()
