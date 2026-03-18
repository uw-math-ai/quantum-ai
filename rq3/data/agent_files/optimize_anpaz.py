import stim
import itertools

def count_cx(circuit):
    count = 0
    for instr in circuit:
        if instr.name in ["CX", "CNOT"]:
            count += len(instr.targets_copy()) // 2
    return count

def get_volume(circuit):
    count = 0
    for instr in circuit:
        if instr.name in ["QUBIT_COORDS", "SHIFT_COORDS", "DETECTOR", "OBSERVABLE_INCLUDE", "TICK"]:
            continue
        if instr.name in ["CX", "CNOT", "CY", "CZ", "SWAP"]:
            count += len(instr.targets_copy()) // 2
        else:
            count += len(instr.targets_copy())
    return count

def solve():
    # 1. Analyze Baseline
    try:
        with open("baseline.stim", "r") as f:
            baseline = stim.Circuit(f.read())
        print(f"Baseline CX: {count_cx(baseline)}")
        print(f"Baseline Vol: {get_volume(baseline)}")
    except:
        print("No baseline.stim found")
        return

    # 2. Define single block stabilizers (indices 0..6)
    # Extracted from prompt:
    # X: 0,1,4,5; 0,2,4,6; 3,4,5,6
    # Z: 0,1,4,5; 0,2,4,6; 3,4,5,6
    # Logical Z: 0,1,2,3,4,5,6 (Z_all)
    # Logical X: 0,1,2,3,4,5,6 (X_all)
    
    # We want to find optimal circuit for |0>_L (stabilized by Gens + Z_all)
    # And |+>_L (stabilized by Gens + X_all)
    
    x_gens = [[0,1,4,5], [0,2,4,6], [3,4,5,6]]
    z_gens = [[0,1,4,5], [0,2,4,6], [3,4,5,6]]
    
    # Create PauliStrings for |0>_L
    stabilizers_0 = []
    for g in x_gens:
        s = stim.PauliString(7)
        for i in g: s[i] = "X"
        stabilizers_0.append(s)
    for g in z_gens:
        s = stim.PauliString(7)
        for i in g: s[i] = "Z"
        stabilizers_0.append(s)
    # Add Z_all
    s = stim.PauliString(7)
    for i in range(7): s[i] = "Z"
    stabilizers_0.append(s)
    
    # Synthesis
    tableau_0 = stim.Tableau.from_stabilizers(stabilizers_0)
    circuit_0 = tableau_0.to_circuit("graph_state")
    
    print(f"Block |0> CX: {count_cx(circuit_0)}")
    
    # Create PauliStrings for |+>_L
    stabilizers_p = []
    for g in x_gens:
        s = stim.PauliString(7)
        for i in g: s[i] = "X"
        stabilizers_p.append(s)
    for g in z_gens:
        s = stim.PauliString(7)
        for i in g: s[i] = "Z"
        stabilizers_p.append(s)
    # Add X_all
    s = stim.PauliString(7)
    for i in range(7): s[i] = "X"
    stabilizers_p.append(s)
    
    # Synthesis
    tableau_p = stim.Tableau.from_stabilizers(stabilizers_p)
    circuit_p = tableau_p.to_circuit("graph_state")
    
    print(f"Block |+> CX: {count_cx(circuit_p)}")
    
    # 3. Construct Full Circuit
    # 3 pairs of logical Bell states.
    # Pair 1: Block 0 (+), Block 1 (0). Transversal CX 0->1.
    # Pair 2: Block 2 (+), Block 3 (0). Transversal CX 2->3.
    # Pair 3: Block 4 (+), Block 5 (0). Transversal CX 4->5.
    
    full_circuit = stim.Circuit()
    
    # Helper to append circuit with offset
    def append_offset(circ, offset):
        # We need to map qubits
        # Stim doesn't have a simple "offset" method for Circuit, we must parse or rebuild
        for instr in circ:
            targets = []
            for t in instr.targets_copy():
                if t.is_qubit_target:
                    targets.append(t.value + offset)
                else:
                    targets.append(t) # Measurement targets etc?
                    # Assuming only gate targets
            full_circuit.append(instr.name, targets, instr.gate_args_copy())

    # Pair 1
    append_offset(circuit_p, 0)   # Block 0 at 0..6
    append_offset(circuit_0, 7)   # Block 1 at 7..13
    # Transversal CX 0->7, 1->8...
    for i in range(7):
        full_circuit.append("CX", [0+i, 7+i])
        
    # Pair 2
    append_offset(circuit_p, 14)  # Block 2 at 14..20
    append_offset(circuit_0, 21)  # Block 3 at 21..27
    for i in range(7):
        full_circuit.append("CX", [14+i, 21+i])
        
    # Pair 3
    append_offset(circuit_p, 28)  # Block 4 at 28..34
    append_offset(circuit_0, 35)  # Block 5 at 35..41
    for i in range(7):
        full_circuit.append("CX", [28+i, 35+i])

    print(f"Full Circuit CX: {count_cx(full_circuit)}")
    print(f"Full Circuit Vol: {get_volume(full_circuit)}")
    
    # 4. Verify against Target Stabilizers
    # We use stim.TableauSimulator
    sim = stim.TableauSimulator()
    sim.do(full_circuit)
    
    with open("target_stabilizers.txt", "r") as f:
        targets = [l.strip() for l in f.readlines() if l.strip()]
        
    valid = True
    for t in targets:
        p = stim.PauliString(t)
        if sim.peek_observable_expectation(p) != 1:
            print(f"Failed stabilizer: {t}")
            valid = False
            # break # Don't break, see how many fail
            
    if valid:
        print("All stabilizers preserved!")
        with open("candidate.stim", "w") as f:
            f.write(str(full_circuit))
    else:
        print("Stabilizers verification failed.")
        # Debug: check expectation
        # Maybe -1?
        # If -1, we might need to fix phases.
        # But for |0> and |+>, phases should be +1 if constructed correctly.

if __name__ == "__main__":
    solve()
