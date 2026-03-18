import stim

def main():
    candidate_path = "data/agent_files/best_candidate.stim"
    with open(candidate_path, 'r') as f:
        candidate_text = f.read()
    circuit = stim.Circuit(candidate_text)
    print(f"Num qubits: {circuit.num_qubits}")
    
    # Check max index used
    max_idx = -1
    for instr in circuit:
        for t in instr.targets_copy():
            if t.value > max_idx:
                max_idx = t.value
    print(f"Max qubit index: {max_idx}")

if __name__ == "__main__":
    main()
