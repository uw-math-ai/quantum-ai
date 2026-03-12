
import stim

c = stim.Circuit.from_file('candidate_graph_fixed.stim')
new_c = stim.Circuit()

allowed_qubits = set(range(105))

for instruction in c:
    targets = instruction.targets_copy()
    new_targets = [t for t in targets if t.value in allowed_qubits]
    
    if not new_targets:
        continue
        
    # If the instruction is a 2-qubit gate, we need to handle pairs.
    # CZ, CX etc take pairs.
    if instruction.name in ["CZ", "CX", "SWAP", "ISWAP"]:
        # Stim stores targets as a flat list. For 2-qubit gates, they are pairs.
        # We need to filter pairs where BOTH are allowed? Or ANY?
        # Usually if one is outside, we should drop the gate.
        # But wait, if 105/106 are not entangled, they shouldn't appear in 2-qubit gates with allowed qubits.
        # If they do, then removing them changes the circuit logic.
        # Let's check if there are any cross-boundary gates.
        
        filtered_targets = []
        for i in range(0, len(targets), 2):
            t1 = targets[i]
            t2 = targets[i+1]
            if t1.value in allowed_qubits and t2.value in allowed_qubits:
                filtered_targets.extend([t1, t2])
            elif t1.value in allowed_qubits or t2.value in allowed_qubits:
                print(f"Warning: Gate {instruction.name} involves boundary qubits: {t1.value}, {t2.value}")
        
        if filtered_targets:
            new_c.append(instruction.name, filtered_targets)
            
    else:
        # Single qubit gates or multi-target single qubit gates (like H 0 1 2)
        if new_targets:
            new_c.append(instruction.name, new_targets)

print(f"Filtered circuit num qubits: {new_c.num_qubits}")
with open('candidate_graph_final.stim', 'w') as f:
    f.write(str(new_c))
