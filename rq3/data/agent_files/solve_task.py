import stim
import sys

def count_cx(circuit):
    count = 0
    for instr in circuit:
        if instr.name == "CX" or instr.name == "CNOT":
            count += len(instr.targets_copy()) // 2
    return count

def main():
    with open("baseline_task.stim", "r") as f:
        baseline_text = f.read()
    baseline = stim.Circuit(baseline_text)
    
    with open("stabilizers_task.txt", "r") as f:
        stab_lines = [l.strip() for l in f.readlines() if l.strip()]

    print(f"Number of stabilizers: {len(stab_lines)}")
    if len(stab_lines) > 0:
        print(f"Stabilizer length: {len(stab_lines[0])}")

    cx = count_cx(baseline)
    print(f"Baseline CX count: {cx}")

    # Check stabilizer preservation
    sim = stim.TableauSimulator()
    sim.do(baseline)
    
    preserved = 0
    for s_str in stab_lines:
        pauli = stim.PauliString(s_str)
        if sim.peek_observable_expectation(pauli) == 1:
            preserved += 1
    
    print(f"Preserved stabilizers: {preserved}/{len(stab_lines)}")

    # Try Resynthesis
    pauli_stabs = [stim.PauliString(s) for s in stab_lines]
    
    try:
        # allow_underconstrained=True is key
        tableau = stim.Tableau.from_stabilizers(pauli_stabs, allow_underconstrained=True)
        
        # Method "graph_state"
        resynth_circuit = tableau.to_circuit("graph_state") 
        resynth_cx = count_cx(resynth_circuit)
        print(f"Resynthesized (graph_state) CX count: {resynth_cx}")
        
        with open("resynth_task.stim", "w") as f:
            f.write(str(resynth_circuit))

        # Check preservation
        sim2 = stim.TableauSimulator()
        sim2.do(resynth_circuit)
        preserved2 = 0
        for s_str in stab_lines:
            pauli = stim.PauliString(s_str)
            if sim2.peek_observable_expectation(pauli) == 1:
                preserved2 += 1
        print(f"Resynthesized Preserved: {preserved2}/{len(stab_lines)}")
        
        # Count CZ in graph state
        cz_count = 0
        for instr in resynth_circuit:
            if instr.name == "CZ":
                cz_count += len(instr.targets_copy()) // 2
        print(f"Resynthesized (graph_state) CZ count: {cz_count}")

    except Exception as e:
        print(f"Resynthesis failed: {e}")

    # Try method="elimination"
    try:
        tableau = stim.Tableau.from_stabilizers(pauli_stabs, allow_underconstrained=True)
        resynth_circuit_elim = tableau.to_circuit("elimination") 
        resynth_cx_elim = count_cx(resynth_circuit_elim)
        print(f"Resynthesized (elimination) CX count: {resynth_cx_elim}")
        
        # Save elimination circuit to check
        with open("resynth_elim.stim", "w") as f:
            f.write(str(resynth_circuit_elim))
            
    except Exception as e:
        print(f"Resynthesis (elimination) failed: {e}")


if __name__ == "__main__":
    main()
