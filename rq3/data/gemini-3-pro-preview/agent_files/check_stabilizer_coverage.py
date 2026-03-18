def main():
    with open("current_task_stabilizers.txt", "r") as f:
        lines = f.read().strip().splitlines()
    
    stabs = []
    for line in lines:
        for s in line.split(','):
            if s.strip():
                stabs.append(s.strip())
                
    num_qubits = len(stabs[0])
    print(f"Num qubits in stabilizers: {num_qubits}")
    
    # Check coverage of qubits 135-160
    # They are indices 135 to 160 (0-based)
    
    involved = False
    for s in stabs:
        if len(s) != num_qubits:
            print(f"Error: length mismatch {len(s)}")
            continue
            
        for i in range(135, min(161, num_qubits)):
            if s[i] != 'I':
                print(f"Qubit {i} is involved in stabilizer: {s}")
                involved = True
                break
        if involved:
            break
            
    if not involved:
        print("Qubits 135-160 are NOT involved (all Identity).")
    else:
        print("Qubits 135-160 ARE involved.")

if __name__ == "__main__":
    main()
