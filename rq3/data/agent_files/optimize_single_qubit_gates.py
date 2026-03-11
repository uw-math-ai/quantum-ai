import stim
import collections

# Load the candidate circuit
# We will manually construct it or read it.
# Reading candidate_graph.stim
with open("candidate_graph.stim") as f:
    circuit_text = f.read()

circuit = stim.Circuit(circuit_text)

# Split into entangling part and local part
# Based on inspection:
# H 0...
# TICK
# CZ...
# TICK
# ... local gates ...

# Find the split point
split_index = -1
for i, instr in enumerate(circuit):
    if instr.name == "TICK":
        # We expect 2 ticks.
        pass
    if instr.name in ["X", "Y", "Z", "S", "H", "SQRT_X", "SQRT_Y", "SQRT_Z"] and i > 50: # After H and CZ
        # This is a heuristic.
        split_index = i
        break

# Actually, let's just assume the last contiguous block of single qubit gates is the target.
# Iterate backwards?
# No, let's look at the structure again.
# H ...
# TICK
# CZ ...
# TICK
# X ...
# Y ...
# Z ...
# S ...
# H ...
# S ...

# Everything after the second TICK is local.
# Let's count ticks.
tick_indices = [i for i, instr in enumerate(circuit) if instr.name == "TICK"]
if len(tick_indices) >= 2:
    local_start = tick_indices[1] + 1
else:
    # Fallback: assume last part is local
    local_start = len(circuit)
    for i in range(len(circuit)-1, -1, -1):
        if circuit[i].name == "CZ":
            local_start = i + 1
            break

print(f"Local part starts at index {local_start}")

entangling_part = circuit[:local_start]
local_part = circuit[local_start:]

# Analyze local part
# We want to optimize the sequence for each qubit.
# Construct a tableau for the local part.
num_qubits = 42
t = stim.Tableau(num_qubits)
for instr in local_part:
    # t.append(instr) # This is wrong
    gate_name = instr.name
    # Assuming single qubit gates for now
    if gate_name in ["CX", "CY", "CZ", "SWAP", "ISWAP"]:
        print(f"Skipping multi-qubit gate {gate_name} in local part analysis.")
        continue
        
    gate_tableau = stim.Tableau.from_named_gate(gate_name)
    targets = [t.value for t in instr.targets_copy()]
    
    # Apply gate to each target individually
    for target in targets:
        t.append(gate_tableau, [target])

# Precompute 1-qubit Cliffords
# BFS to find shortest sequence for each of the 24 single qubit Cliffords.
# Gates allowed: H, S, SQRT_X, SQRT_Y, SQRT_Z, X, Y, Z, I
# And their inverses? S_DAG, SQRT_X_DAG, etc.
# We want minimal volume.
# Volume counts: H(1), S(1), S_DAG(1), SQRT_X(1), X(1), Y(1), Z(1).
# We assume cost is 1 for all.
# If S_DAG is not available directly, use S S S (cost 3).
# Stim supports S_DAG.
allowed_gates = ["I", "X", "Y", "Z", "H", "S", "S_DAG", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "SQRT_Z", "SQRT_Z_DAG"]
# SQRT_Z is S. SQRT_Z_DAG is S_DAG.
# So remove SQRT_Z/DAG.
allowed_gates = ["I", "X", "Y", "Z", "H", "S", "S_DAG", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG"]

gate_map = {} # (x_z_pair) -> [gates]
queue = collections.deque([ (stim.Tableau(1), []) ])
seen = set()

# Canonical representation of tableau state: (x_output, z_output)
def get_state(tab):
    return (str(tab.x_output(0)), str(tab.z_output(0)))

start_state = get_state(stim.Tableau(1))
seen.add(start_state)
gate_map[start_state] = []

print("Building lookup table...")
while queue:
    tab, path = queue.popleft()
    
    if len(path) >= 3: # Limit search depth
        continue
        
    for g_name in allowed_gates:
        new_tab = tab.copy()
        if g_name != "I":
            # new_tab.append(stim.Circuit(f"{g_name} 0"), [0]) # Wrong
            gate_tab = stim.Tableau.from_named_gate(g_name)
            new_tab.append(gate_tab, [0])
        
        state = get_state(new_tab)
        if state not in seen:
            seen.add(state)
            new_path = path + [g_name] if g_name != "I" else path
            gate_map[state] = new_path
            queue.append((new_tab, new_path))
            
print(f"Found {len(gate_map)} Cliffords.")

# Optimize each qubit
new_local = stim.Circuit()

for q in range(num_qubits):
    # Extract the operation on qubit q
    # We need to see what the local part does to X_q and Z_q
    # t is the tableau for the whole local part.
    # Check x_output(q) and z_output(q).
    x_out = t.x_output(q)
    z_out = t.z_output(q)
    
    # Check locality
    # x_out must be single Pauli on q (plus sign)
    # verify only index q is non-identity
    # (Checking if len(x_out) > 0 and only q is there)
    # Actually, iterate through the Pauli string to be sure?
    # Or just trust it is local.
    
    # Create a 1-qubit tableau representing this
    # We need to extract the sign and Pauli type.
    # PauliString has sign (+1, -1) and Pauli (I,X,Y,Z) at index.
    
    # Construct a dummy 1-qubit tableau that matches
    target = stim.Tableau(1)
    # We can't set outputs directly.
    # But we can find the matching state in our map.
    
    x_str = str(x_out)
    z_str = str(z_out)
    
    # x_str is like "+_X___"
    # We want "+X"
    # The string format is Sign followed by Paulis.
    # Sign is + or -
    # Paulis are chars.
    
    # Alternatively, use methods
    # x_out[q] -> 0,1,2,3
    # x_out.sign -> +1, -1
    
    def format_pauli(ps, q):
        s = "+" if ps.sign.real > 0 else "-"
        p = "IXYZ"[ps[q]]
        return f"{s}{p}"

    x_key = format_pauli(x_out, q)
    z_key = format_pauli(z_out, q)
    
    # But wait, my lookup table uses str(tab.x_output(0)) which is "+X", "-Y".
    # Because tab is 1 qubit.
    # So the key format must match "+X", "-Y".
    # The str() of 1-qubit PauliString is exactly "+X", "-Y", etc.
    # So format_pauli should match that.
    
    state = (x_key, z_key)
    
    if state in gate_map:
        gate_seq = gate_map[state]
        for g in gate_seq:
            new_local.append(g, [q])
    else:
        print(f"Warning: State {state} for qubit {q} not found. Using identity.")


# Combine
final_circuit = entangling_part + new_local

# Save
with open("candidate_optimized.stim", "w") as f:
    f.write(str(final_circuit))
    
print("Optimized circuit written to candidate_optimized.stim")
