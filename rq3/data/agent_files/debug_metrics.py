import stim

def count_metrics(circuit):
    cx = 0
    vol = 0
    for instr in circuit:
        if instr.name in ["CX", "CNOT"]:
            n = len(instr.targets_copy()) // 2
            cx += n
            vol += n
        elif instr.name in ["CY", "CZ"]:
            n = len(instr.targets_copy()) // 2
            vol += n
        elif instr.name in ["H", "S", "SQRT_X", "SQRT_Y", "SQRT_Z", "X", "Y", "Z", "I", "S_DAG", "SQRT_X_DAG", "SQRT_Y_DAG", "SQRT_Z_DAG"]:
            vol += len(instr.targets_copy())
    return cx, vol

def main():
    try:
        with open("candidate_final.stim", "r") as f:
            content = f.read()
        circuit = stim.Circuit(content)
        cx, vol = count_metrics(circuit)
        print(f"File content metrics: CX={cx}, Vol={vol}")
        
        # Check targets of first CX
        for instr in circuit:
            if instr.name == "CX":
                print(f"First CX targets: {instr.targets_copy()}")
                break
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
