import stim

with open("candidate.stim", "r") as f:
    circuit = stim.Circuit(f.read())

new_circuit = stim.Circuit()
# State tracking for single qubit Cliffords after the CZ layer
# Assuming max qubit index is 44 based on previous output
final_tableaus = [stim.Tableau(1) for _ in range(45)]
seen_cz = False

for instr in circuit:
    if instr.name == "CZ":
        new_circuit.append(instr)
        seen_cz = True
    elif instr.name == "H" and not seen_cz:
        # Initial H layer
        new_circuit.append(instr)
    elif seen_cz:
        # Accumulate single qubit operations into tableaus
        # Verify it's a single qubit gate
        # (It should be, based on graph state synthesis)
        try:
            gate_tableau = stim.Circuit(f"{instr.name} 0").to_tableau()
        except Exception as e:
            # If not a single qubit unitary gate (e.g. CX, Reset), just append it directly?
            # But graph state shouldn't have those here.
            # If it's TICK or something, ignore.
            if instr.name == "TICK":
                continue
            print(f"Warning: Non-single-qubit gate {instr.name} after CZ layer. Appending directly.")
            new_circuit.append(instr)
            continue

        for t in instr.targets_copy():
            q = t.value
            if q < 45:
                final_tableaus[q] = final_tableaus[q].then(gate_tableau)
    else:
        # Before CZ and not H? Unusual but keep it.
        new_circuit.append(instr)

# BFS to find optimal single qubit gate sequences
# Generators
SINGLE_QUBIT_GATES = [
    "I", "X", "Y", "Z", 
    "H", "S", "S_DAG", 
    "SQRT_X", "SQRT_X_DAG", 
    "SQRT_Y", "SQRT_Y_DAG",
    "C_XYZ", "C_ZYX" 
]

# We want to map Tableau -> shortest sequence of gates
optimal_sequences = {}
queue = [([], stim.Tableau(1))] # (sequence, tableau)

# Initialize with Identity
optimal_sequences[stim.Tableau(1)] = []

import collections
queue = collections.deque()
queue.append(([], stim.Tableau(1)))

# Max depth 3 should cover all 24 Cliffords (H, S generate all in length 3-4? With more gates, simpler)
found_count = 0
while queue:
    seq, tab = queue.popleft()
    
    # If we have found all 24, we can stop? 
    # But we want SHORTEST for each. BFS guarantees shortest.
    # We continue until queue empty? 
    # With many generators, branching factor is ~13.
    # Depth 1: 13.
    # Depth 2: 169.
    # Depth 3: ~2000.
    # Total Cliffords is 24.
    # So we will visit many redundant states.
    # We only add to queue if we found a NEW state or (maybe same state via different path? No, BFS finds shortest first).
    
    pass 
    # Logic is implemented below loop

# Re-implementation of BFS
optimal_sequences = {}
queue = collections.deque()

# Start with Identity
start_t = stim.Tableau(1)
optimal_sequences[start_t] = []
queue.append(start_t)

# Map string representation of tableau to sequence? 
# Tableau object is hashable in recent stim? 
# Let's verify.
# If not, we use str(t) as key.

while queue:
    curr_t = queue.popleft()
    curr_seq = optimal_sequences[curr_t]
    
    if len(curr_seq) >= 3:
        # Optimization: Most 1q Cliffords are length 1 or 2 with this rich set.
        # Maybe length 3 is needed?
        # Let's limit depth to avoid infinite loop if something is wrong, 
        # but 24 states should be found quickly.
        continue

    for gate in SINGLE_QUBIT_GATES:
        if gate == "I": continue
        
        # Apply gate
        next_t = curr_t.then(stim.Circuit(f"{gate} 0").to_tableau())
        
        if next_t not in optimal_sequences:
            new_seq = curr_seq + [gate]
            optimal_sequences[next_t] = new_seq
            queue.append(next_t)
            
            if len(optimal_sequences) >= 24:
                # Found all 24?
                # Actually, there are 24 single qubit Cliffords.
                pass

# Synthesize minimal single qubit operations
for q in range(45):
    t = final_tableaus[q]
    
    # Check lookup
    if t in optimal_sequences:
        seq = optimal_sequences[t]
        for gate_name in seq:
            new_circuit.append(gate_name, [q])
    else:
        # Should not happen if BFS is complete
        # Fallback to stim synthesis
        sub_circ = t.to_circuit()
        for sub_instr in sub_circ:
            for _ in sub_instr.targets_copy():
                new_circuit.append(sub_instr.name, [q])

with open("candidate_opt.stim", "w") as f:
    f.write(str(new_circuit))

print("Done")
