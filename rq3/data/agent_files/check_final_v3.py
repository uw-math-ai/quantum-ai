import stim
import sys

def main():
    try:
        # Load resynth
        with open("resynth_task.stim", "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print("resynth_task.stim not found.")
        return

    try:
        # Load stabilizers to check count and length
        with open("stabilizers_task.txt", "r") as f:
            stabs = [l.strip() for l in f.readlines() if l.strip()]
    except FileNotFoundError:
        print("stabilizers_task.txt not found.")
        return
    
    # Determine max qubit index from stabilizers
    if not stabs:
        max_qubit = 48
    else:
        max_qubit = len(stabs[0]) - 1
    
    print(f"Max qubit index allowed: {max_qubit}")

    new_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        parts = line.split()
        if not parts:
            continue
        gate_name = parts[0]
        
        # Handle RX -> H replacement
        if gate_name == "RX":
            # Extract targets
            targets = [int(x) for x in parts[1:]]
            # Filter targets
            valid_targets = [t for t in targets if t <= max_qubit]
            
            if valid_targets:
                # Replace with H
                new_lines.append(f"H {' '.join(map(str, valid_targets))}")
            continue

        # Handle TICK -> Remove
        if gate_name == "TICK":
            continue
            
        # Handle other gates
        # We need to filter targets > max_qubit
        # Assume standard Stim format: GATE t1 t2 ...
        
        targets = []
        try:
            targets = [int(x) for x in parts[1:]]
        except ValueError:
            # Maybe some args? resynth from tableau usually simple
            # print(f"Warning: could not parse targets in line: {line}")
            new_lines.append(line)
            continue
        
        valid_targets = [t for t in targets if t <= max_qubit]
        
        if len(valid_targets) == len(targets):
            new_lines.append(line)
        else:
            # Some targets invalid.
            # If 2-qubit gate, keep pairs if both valid.
            if gate_name in ["CX", "CNOT", "CZ", "SWAP", "ISWAP", "SQRT_XX", "SQRT_ZZ", "SQRT_YY"]:
                kept_args = []
                for i in range(0, len(targets), 2):
                    if i+1 >= len(targets): break
                    t1 = targets[i]
                    t2 = targets[i+1]
                    if t1 <= max_qubit and t2 <= max_qubit:
                        kept_args.append(t1)
                        kept_args.append(t2)
                
                if kept_args:
                    new_lines.append(f"{gate_name} {' '.join(map(str, kept_args))}")
            else:
                # Single qubit gate or others
                # If ANY target is invalid, keep valid ones
                if valid_targets:
                    new_lines.append(f"{gate_name} {' '.join(map(str, valid_targets))}")

    # Construct candidate string
    candidate_text = "\n".join(new_lines)
    
    # Save candidate
    with open("candidate.stim", "w") as f:
        f.write(candidate_text)
        
    # Parse with Stim to verify validity
    try:
        candidate_circuit = stim.Circuit(candidate_text)
        # print("Candidate circuit parsed successfully.")
    except Exception as e:
        print(f"Candidate circuit parsing failed: {e}")
        return

    # Check metrics
    cx_count = 0
    cz_count = 0
    volume = 0
    for instr in candidate_circuit:
        # Rudimentary volume check (gate count)
        n_targets = len(instr.targets_copy())
        if instr.name in ["CX", "CNOT"]:
            cx_count += n_targets // 2
            volume += n_targets // 2
        elif instr.name == "CZ":
            cz_count += n_targets // 2
            volume += n_targets // 2
        else:
            # Single qubit gates
            volume += n_targets
    
    print(f"Candidate CX count: {cx_count}")
    print(f"Candidate CZ count: {cz_count}")
    print(f"Candidate Volume (approx): {volume}")

    # Verify stabilizers
    sim = stim.TableauSimulator()
    sim.do(candidate_circuit)
    
    preserved = 0
    failed = []
    for s_str in stabs:
        pauli = stim.PauliString(s_str)
        if sim.peek_observable_expectation(pauli) == 1:
            preserved += 1
        else:
            failed.append(s_str)
    
    print(f"Candidate Preserved: {preserved}/{len(stabs)}")
    if failed:
        print(f"First failed: {failed[0]}")

if __name__ == "__main__":
    main()
