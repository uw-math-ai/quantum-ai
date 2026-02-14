import stim

def get_5_qubit_code_circuit():
    # Returns a circuit that maps |00000> to |0_L> of the [5,1,3] code.
    # Stabilizers: XZZXI, IXZZX, XIXZZ, ZXIXZ.
    # Logical Z: ZZZZZ.
    
    stabilizers_5 = [
        stim.PauliString("ZZZZZ"),
        stim.PauliString("XZZXI"),
        stim.PauliString("IXZZX"),
        stim.PauliString("XIXZZ"),
        stim.PauliString("ZXIXZ")
    ]
    t = stim.Tableau.from_stabilizers(stabilizers_5)
    return t.to_circuit()

def generate_circuit():
    circuit = stim.Circuit()
    
    # 9 blocks of 5 qubits. Total 45 qubits.
    # Logical qubits of the 9 blocks: L0..L8.
    # We map L0..L8 to physical qubits 0, 5, 10, ..., 40 (the first qubit of each block).
    # Then we run the encoding circuit on each block.
    
    # Outer code state preparation on L0..L8 (mapped to physical leads 0, 5, ... 40)
    # Target state:
    # Groups: A(L0,L1,L2), B(L3,L4,L5), C(L6,L7,L8).
    # Stabilizers:
    # Z0Z1, Z0Z2 (A is Repetition Z)
    # Z3Z4, Z3Z5 (B is Repetition Z)
    # Z6Z7, Z6Z8 (C is Repetition Z)
    # XA XB, XA XC (where XA=X0X1X2)
    # ZA ZB ZC (where ZA=Z0)
    
    # Strategy:
    # 1. Prepare A, B, C leaders (L0, L3, L6 -> physical 0, 15, 30) in state stabilized by:
    #    X0X15, X0X30, Z0Z15Z30.
    #    This is |GHZ_3>_X = |+++> + |--->.
    #    Circuit:
    #    H 0, H 15, H 30. (Start |+++>)
    #    No, that's |+> state.
    #    To get |GHZ_X>:
    #    Start |000>. H 0, CX 0 15, CX 0 30 -> |GHZ_Z> = |000>+|111>.
    #    H 0, H 15, H 30 -> |GHZ_X> = |+++> + |--->.
    
    circuit.append("H", [0])
    circuit.append("CX", [0, 15])
    circuit.append("CX", [0, 30])
    circuit.append("H", [0, 15, 30])
    
    # 2. Expand to groups (Repetition Z)
    #    A: 0 -> 5, 10
    circuit.append("CX", [0, 5])
    circuit.append("CX", [0, 10])
    #    B: 15 -> 20, 25
    circuit.append("CX", [15, 20])
    circuit.append("CX", [15, 25])
    #    C: 30 -> 35, 40
    circuit.append("CX", [30, 35])
    circuit.append("CX", [30, 40])
    
    # Now L0..L8 are prepared on 0, 5, ..., 40.
    # Apply 5-qubit encoding circuit to each block.
    
    enc_circuit = get_5_qubit_code_circuit()
    
    for k in range(9):
        offset = k * 5
        # The encoding circuit acts on 0,1,2,3,4.
        # It assumes input state is on 0..4.
        # Our input state for block k is on offset+0 (the lead).
        # The other qubits offset+1..offset+4 are |0>.
        # This matches the assumption of enc_circuit (it prepares |0_L> from |00000>).
        # Wait, does enc_circuit preserve the state of input qubit 0?
        # enc_circuit maps Z0 -> Z_L.
        # This means if input is eigenstate of Z0, output is eigenstate of Z_L.
        # So |0> -> |0_L>, |1> -> |1_L>.
        # What about X eigenstates?
        # enc_circuit maps X0 -> X_L?
        # Let's check the tableau property.
        # We constructed it with `from_stabilizers([ZZZZZ, ...])`.
        # The tableau T has Z outputs equal to these stabilizers.
        # So T |00000> = |0_L>.
        # But we need T to map |psi>|0000> -> |psi_L>.
        # This requires T * Z0 * T^dag = Z_L and T * X0 * T^dag = X_L.
        # We checked Z0 -> Z_L (by definition of from_stabilizers, Z_output[0] is the first stabilizer).
        # But X0 -> ?
        # If X0 -> X_L * S, it's fine.
        # If X0 -> Y_L or something, we are in trouble.
        # Stim's `from_stabilizers` guarantees the Z outputs.
        # It picks X outputs to make a valid Clifford.
        # It doesn't guarantee X0 -> X_L.
        # However, for [5,1,3], there is a unique code space.
        # The logical operators are unique up to stabilizers.
        # The "canonical" destablizers might not align with X0.
        
        # To be safe, we should use `from_conjugated_generators` as I thought before.
        # Or we can check what X0 maps to and correct it.
        # But let's try `from_conjugated_generators` to be sure.
        pass
    
    # Re-generating enc_circuit with from_conjugated_generators
    t = stim.Tableau.from_conjugated_generators(
        xs=[
            stim.PauliString("XXXXX"),
            stim.PauliString("ZIZII"), 
            stim.PauliString("IZIZI"), 
            stim.PauliString("IIZIZ"), 
            stim.PauliString("IIIZI")
        ],
        zs=[
            stim.PauliString("ZZZZZ"),
            stim.PauliString("XZZXI"),
            stim.PauliString("IXZZX"),
            stim.PauliString("XIXZZ"),
            stim.PauliString("ZXIXZ")
        ]
    )
    enc_circuit = t.to_circuit()
    
    for k in range(9):
        offset = k * 5
        for instr in enc_circuit:
            targets = []
            for t in instr.targets_copy():
                if t.is_qubit_target:
                    targets.append(t.value + offset)
                else:
                    targets.append(t)
            circuit.append(instr.name, targets, instr.gate_args)
            
    return circuit

if __name__ == "__main__":
    c = generate_circuit()
    print(str(c))
