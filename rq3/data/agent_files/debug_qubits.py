import stim

def debug():
    with open("my_baseline_v2.stim", "r") as f:
        base = stim.Circuit(f.read())
    
    print(f"Baseline num_qubits: {base.num_qubits}")
    
    tab = stim.Tableau.from_circuit(base)
    print(f"Tableau num_qubits: {len(tab)}")
    
    circ = tab.to_circuit(method="graph_state")
    print(f"Synthesized circuit num_qubits: {circ.num_qubits}")
    
    # Check max qubit index in synthesized circuit
    max_q = -1
    for instr in circ:
        for t in instr.targets_copy():
             if t.is_qubit_target:
                 max_q = max(max_q, t.value)
    print(f"Max qubit index in synthesized circuit: {max_q}")

if __name__ == "__main__":
    debug()
