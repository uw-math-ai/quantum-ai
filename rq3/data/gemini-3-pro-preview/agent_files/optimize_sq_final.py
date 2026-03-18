import stim
import collections

# Load candidate circuit
with open("candidate.stim", "r") as f:
    circuit = stim.Circuit(f.read())

new_circuit = stim.Circuit()
final_tableaus = [stim.Tableau(1) for _ in range(45)]
seen_cz = False

# 1. Parse and accumulate SQ gates after CZ
for instr in circuit:
    if instr.name == "CZ":
        new_circuit.append(instr)
        seen_cz = True
    elif instr.name == "H" and not seen_cz:
        new_circuit.append(instr)
    elif seen_cz:
        if instr.name == "TICK":
            continue
        try:
            gate_tableau = stim.Circuit(f"{instr.name} 0").to_tableau()
        except:
            # Not a single qubit gate?
            new_circuit.append(instr)
            continue
            
        for t in instr.targets_copy():
            q = t.value
            if q < 45:
                final_tableaus[q] = final_tableaus[q].then(gate_tableau)
    else:
        new_circuit.append(instr)

# 2. BFS for optimal single-qubit sequences
SINGLE_QUBIT_GATES = [
    "I", "X", "Y", "Z", 
    "H", "S", "S_DAG", 
    "SQRT_X", "SQRT_X_DAG", 
    "SQRT_Y", "SQRT_Y_DAG",
    "C_XYZ", "C_ZYX"
]

optimal_sequences = {}
queue = collections.deque()
start_t = stim.Tableau(1)
optimal_sequences[start_t] = [] # Identity -> empty sequence
queue.append(start_t)

# BFS loop
while queue:
    curr_t = queue.popleft()
    curr_seq = optimal_sequences[curr_t]
    
    # Limit depth to 3 (covers all 24 Cliffords with this generator set)
    if len(curr_seq) >= 3:
        continue

    for gate in SINGLE_QUBIT_GATES:
        if gate == "I": continue
        
        gate_t = stim.Circuit(f"{gate} 0").to_tableau()
        next_t = curr_t.then(gate_t)
        
        if next_t not in optimal_sequences:
            new_seq = curr_seq + [gate]
            optimal_sequences[next_t] = new_seq
            queue.append(next_t)
            
            # Stop if we found all 24?
            if len(optimal_sequences) >= 24:
                # We can stop extending, but queue might still have shorter paths to check?
                # BFS ensures first time we see a node, it is via shortest path (in edges).
                # Since edge weights are all 1 (1 gate), this is correct.
                # But we might find another node later.
                pass

print(f"BFS Cache size: {len(optimal_sequences)}")

# 3. Apply optimal sequences
for q in range(45):
    t = final_tableaus[q]
    if t in optimal_sequences:
        seq = optimal_sequences[t]
        for gate_name in seq:
            new_circuit.append(gate_name, [q])
    else:
        # Fallback (should cover everything if BFS depth is enough)
        # If not found, try to synthesise with stim (sub-optimal but valid)
        print(f"Warning: Qubit {q} state not in cache. Synthesizing.")
        sub_circ = t.to_circuit()
        for sub_instr in sub_circ:
            for _ in sub_instr.targets_copy():
                new_circuit.append(sub_instr.name, [q])

with open("candidate_opt.stim", "w") as f:
    f.write(str(new_circuit))

print("Optimization complete.")
