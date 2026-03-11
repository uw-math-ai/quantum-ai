import stim

def check_circuit(filename):
    with open(filename, "r") as f:
        c = stim.Circuit(f.read())
    
    cx = 0
    cz = 0
    meas = 0
    reset = 0
    volume = 0
    
    for instruction in c:
        if instruction.name == "CX" or instruction.name == "CNOT":
            cx += len(instruction.targets_copy()) // 2
            volume += len(instruction.targets_copy())
        elif instruction.name == "CZ":
            cz += len(instruction.targets_copy()) // 2
            volume += len(instruction.targets_copy())
        elif instruction.name.startswith("M"):
            meas += 1
            volume += len(instruction.targets_copy())
        elif instruction.name.startswith("R"):
            reset += 1
            volume += len(instruction.targets_copy())
        else:
            volume += len(instruction.targets_copy())
            
    print(f"File: {filename}")
    print(f"  CX: {cx}")
    print(f"  CZ: {cz}")
    print(f"  Meas: {meas}")
    print(f"  Reset: {reset}")
    print(f"  Volume (approx): {volume}")

check_circuit("candidate_graph.stim")
check_circuit("candidate_elim.stim")
