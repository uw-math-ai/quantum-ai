import stim

def generate_encoder_circuit():
    # Stabilizers for [5,1,3] code
    # Logical Z: ZZZZZ
    # Logical X: XXXXX
    # Code Stabilizers: XZZXI, IXZZX, XIXZZ, ZXIXZ
    
    # We want Z0 -> ZZZZZ, X0 -> XXXXX.
    # Z1..Z4 -> Stabilizers.
    
    generators = [
        "ZZZZZ",
        "XZZXI",
        "IXZZX",
        "XIXZZ",
        "ZXIXZ"
    ]
    t = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in generators])
    
    # We verify mapping
    assert str(t.z_output(0)) == "+ZZZZZ"
    assert str(t.x_output(0)) == "+XXXXX"
    
    return t.to_circuit("elimination")

def generate_outer_circuit():
    # 9 logical qubits.
    # Stabilizers:
    # Z0Z1, Z0Z2
    # Z3Z4, Z3Z5
    # Z6Z7, Z6Z8
    # X0X1X2X3X4X5
    # X0X1X2X6X7X8
    # Z0Z3Z6
    
    stabs = [
        "ZZIIIIIII",
        "ZIZIIIIII",
        "IIIZZIIII",
        "IIIZIZIII",
        "IIIIIIZZI",
        "IIIIIIZIZ",
        "XXXXXXIII",
        "XXXIIIXXX",
        "ZIIZIIZII"
    ]
    t = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabs])
    return t.to_circuit("elimination")

def solve():
    encoder = generate_encoder_circuit()
    outer = generate_outer_circuit()
    
    full_circuit = stim.Circuit()
    
    # 1. Apply outer circuit on the 'logical' qubits.
    # Logical qubit k (0..8) is mapped to physical qubit 5*k.
    # The outer circuit acts on 0..8. We remap indices.
    
    qm_outer = {k: 5*k for k in range(9)}
    
    # We copy outer circuit instructions with remapped targets
    for instr in outer:
        targets = []
        for t in instr.targets_copy():
            if t.is_qubit_target:
                targets.append(qm_outer[t.value])
            else:
                targets.append(t)
        full_circuit.append(instr.name, targets, instr.gate_args_copy())
        
    # 2. Apply encoder on each block.
    # Block k uses qubits 5k..5k+4.
    # The encoder expects input on 0, and ancilla on 1..4.
    # The data is already on 5k (from outer circuit).
    # The ancilla 5k+1..5k+4 are |0> (untouched).
    # So we map encoder qubit j -> 5k + j.
    
    for k in range(9):
        offset = 5*k
        for instr in encoder:
            targets = []
            for t in instr.targets_copy():
                if t.is_qubit_target:
                    targets.append(t.value + offset)
                else:
                    targets.append(t)
            full_circuit.append(instr.name, targets, instr.gate_args_copy())
            
    print(full_circuit)

if __name__ == "__main__":
    solve()
