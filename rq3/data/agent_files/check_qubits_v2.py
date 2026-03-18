import stim

def check():
    print("Checking...")
    try:
        with open("prompt_stabilizers.txt", "r") as f:
            lines = [l.strip() for l in f if l.strip()]
        line0 = lines[0]
        if "," in line0:
            line0 = line0.split(",")[-1].strip()
        print(f"Stabilizer length: {len(line0)}")
        
        with open("candidate_improved.stim", "r") as f:
            circ = stim.Circuit(f.read())
        
        print(f"Candidate num_qubits: {circ.num_qubits}")
        
        max_idx = -1
        for instr in circ:
            for t in instr.targets_copy():
                if t.value > max_idx:
                    max_idx = t.value
        print(f"Max qubit index in candidate: {max_idx}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check()
