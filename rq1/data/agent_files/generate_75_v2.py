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

# Iterate logical circuit
for instr in logical_circuit:
    if instr.name in ["QUBIT_COORDS", "R", "M"]: continue 
    
    new_targets = []
    for t in instr.targets_copy():
        if t.is_combiner:
            new_targets.append(stim.target_combiner())
        elif t.is_x_target:
            new_targets.append(stim.target_x(qubit_map[t.value]))
        elif t.is_y_target:
            new_targets.append(stim.target_y(qubit_map[t.value]))
        elif t.is_z_target:
            new_targets.append(stim.target_z(qubit_map[t.value]))
        elif t.is_inverted_result_target:
            # This shouldn't happen for Clifford circuits from tableau
            raise ValueError("Inverted result target found")
        elif t.is_measurement_record_target:
            # sweep bit?
            raise ValueError("Sweep bit target found")
        else:
            # Standard qubit target
            new_targets.append(qubit_map[t.value])
            
    final_circuit.append(instr.name, new_targets, instr.gate_args_copy())

# Apply block circuit on each block
for b in range(15):
    # Map 0..4 -> 5*b .. 5*b+4
    base = 5*b
    block_map = {i: base + i for i in range(5)}
    
    for instr in block_circuit:
        if instr.name in ["QUBIT_COORDS", "R", "M"]: continue
        
        new_targets = []
        for t in instr.targets_copy():
            if t.is_combiner:
                new_targets.append(stim.target_combiner())
            elif t.is_x_target:
                new_targets.append(stim.target_x(block_map[t.value]))
            elif t.is_y_target:
                new_targets.append(stim.target_y(block_map[t.value]))
            elif t.is_z_target:
                new_targets.append(stim.target_z(block_map[t.value]))
            else:
                new_targets.append(block_map[t.value])
        
        final_circuit.append(instr.name, new_targets, instr.gate_args_copy())

# Save to file
with open('circuit_75.stim', 'w') as f:
    f.write(str(final_circuit))

print("Circuit generated.")
