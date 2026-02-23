import stim

try:
    with open("circuit_119_fixed.stim", "r") as f:
        circuit = stim.Circuit(f.read())
    
    for instruction in circuit:
        name = instruction.name
        targets = instruction.targets_copy()
        
        # Decompose into small chunks
        if name == "CX" or name == "CNOT" or name == "CZ" or name == "SWAP":
            # 2-qubit gates
            chunk_size = 2 # 1 pair
            for i in range(0, len(targets), 2):
                t1 = targets[i]
                t2 = targets[i+1]
                # Print 1 pair per line
                print(f"{name} {t1.value} {t2.value}")
        elif name in ["H", "S", "X", "Y", "Z", "I", "M", "R", "RX", "RY", "RZ", "SQRT_X", "SQRT_Y", "SQRT_Z", "S_DAG", "SQRT_X_DAG", "SQRT_Y_DAG", "SQRT_Z_DAG"]:
            # 1-qubit gates
            for t in targets:
                 print(f"{name} {t.value}")
        else:
            # Other gates (like DETECTOR, OBSERVABLE, or multi-qubit with args)
            # For this problem we likely only have Clifford gates.
            # But let's print them safely.
            print(instruction)

except Exception as e:
    print(f"Error: {e}")
