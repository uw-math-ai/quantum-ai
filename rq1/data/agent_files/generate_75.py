import stim
import sys

# 1. Get logical stabilizers
def get_logical_stabs():
    with open('stabilizers_75.txt') as f:
        lines = [l.strip() for l in f if l.strip()]
    
    logical_stabs = []
    # Lines 61-74 in file are indices 60-73 in list
    for line in lines[60:]:
        l_stab = ""
        for i in range(15):
            block = line[i*5:(i+1)*5]
            if block == "IIIII": l_stab += "I"
            elif block == "XXXXX": l_stab += "X"
            elif block == "ZZZZZ": l_stab += "Z"
            else:
                # Fallback: check if it's all I
                if set(block) == {'I'}: l_stab += "I"
                elif set(block) == {'X'}: l_stab += "X"
                elif set(block) == {'Z'}: l_stab += "Z"
                else:
                    raise ValueError(f"Unknown block: {block}")
        logical_stabs.append(stim.PauliString(l_stab))
    return logical_stabs

try:
    logical_stabs = get_logical_stabs()
except Exception as e:
    print(f"Error parsing stabilizers: {e}")
    sys.exit(1)

# 2. Logical circuit
logical_circuit = stim.Tableau.from_stabilizers(logical_stabs, allow_underconstrained=True).to_circuit()

# 3. Block circuit
# Stabilizers: XZZXI, IXZZX, XIXZZ, ZXIXZ, ZZZZZ
block_stabs = [
    stim.PauliString("XZZXI"),
    stim.PauliString("IXZZX"),
    stim.PauliString("XIXZZ"),
    stim.PauliString("ZXIXZ"),
    stim.PauliString("ZZZZZ")
]
block_circuit = stim.Tableau.from_stabilizers(block_stabs).to_circuit()

# 4. Construct final circuit
final_circuit = stim.Circuit()

# Init
# Implicitly |0>

# Apply logical circuit on representative qubits (indices 4, 9, ..., 74)
# Map: i -> 5*i + 4
qubit_map = {i: 5*i + 4 for i in range(15)}

for instr in logical_circuit:
    if instr.name in ["QUBIT_COORDS", "R", "M"]: 
        continue # Skip these
    targets = []
    for t in instr.targets_copy():
        if t.is_qubit_target:
            targets.append(stim.target_combiner(qubit_map[t.value]))
        elif t.is_x_target:
            targets.append(stim.target_x(qubit_map[t.value]))
        elif t.is_y_target:
            targets.append(stim.target_y(qubit_map[t.value]))
        elif t.is_z_target:
            targets.append(stim.target_z(qubit_map[t.value]))
        elif t.is_combiner:
             # Should handle combiner properly if present
             pass
    
    # Simple remapping for standard gates
    # We can use `instr.name` and remapped targets
    # Note: `targets_copy()` returns raw targets.
    # A cleaner way is to reconstruct the instruction
    
    remapped_targets = []
    for t in instr.targets_copy():
        val = t.value
        new_val = qubit_map[val]
        # preserving flags like is_x_target etc is tricky with just value.
        # But for clifford circuits from Tableau, usually just simple targets.
        # Let's check if there are any fancy targets.
        if t.is_x_target:
             remapped_targets.append(stim.target_x(new_val))
        elif t.is_y_target:
             remapped_targets.append(stim.target_y(new_val))
        elif t.is_z_target:
             remapped_targets.append(stim.target_z(new_val))
        elif t.is_inverted_result_target:
             # Measurement result interaction? Hopefully none.
             remapped_targets.append(stim.target_inv(new_val)) # This is not quite right
        else:
             remapped_targets.append(stim.target_combiner(new_val) if t.is_combiner else new_val)
             
    final_circuit.append(instr.name, remapped_targets, instr.gate_args_copy())

# Apply block circuit on each block
for b in range(15):
    # Map 0..4 -> 5*b .. 5*b+4
    # But wait!
    # The block circuit assumes inputs are Z states.
    # Specifically Z0, Z1, Z2, Z3 are initialized to |0> (stabilized by Z).
    # And Z4 is the "input" state from the logical circuit.
    # So we apply the block circuit to qubits {5b, ..., 5b+4}.
    # The qubits 5b..5b+3 are fresh |0>.
    # The qubit 5b+4 carries the state from logical_circuit.
    
    # We need to remap the block circuit targets.
    base = 5*b
    block_map = {i: base + i for i in range(5)}
    
    for instr in block_circuit:
        if instr.name in ["QUBIT_COORDS", "R", "M"]: continue
        
        remapped_targets = []
        for t in instr.targets_copy():
             val = t.value
             new_val = block_map[val]
             if t.is_x_target: remapped_targets.append(stim.target_x(new_val))
             elif t.is_y_target: remapped_targets.append(stim.target_y(new_val))
             elif t.is_z_target: remapped_targets.append(stim.target_z(new_val))
             else: remapped_targets.append(new_val)
        
        final_circuit.append(instr.name, remapped_targets, instr.gate_args_copy())

# Save to file
with open('circuit_75.stim', 'w') as f:
    f.write(str(final_circuit))

print("Circuit generated.")
