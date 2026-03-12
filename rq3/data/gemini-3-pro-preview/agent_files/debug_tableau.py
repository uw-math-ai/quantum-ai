import stim
import sys

def main():
    try:
        with open("baseline_attempt_01.stim", "r") as f:
            baseline = stim.Circuit(f.read())
    except Exception as e:
        print(f"Error loading: {e}")
        return

    print(f"Baseline qubits: {baseline.num_qubits}")
    
    sim = stim.TableauSimulator()
    sim.do(baseline)
    tableau = sim.current_inverse_tableau().inverse()
    print(f"Tableau length: {len(tableau)}")
    
    # Check if there are non-identity operations on higher qubits
    # Check x_output and z_output for k >= 49
    
    max_active_qubit = -1
    for k in range(len(tableau)):
        # Check if qubit k is identity (X->X, Z->Z, phase=0)
        # Actually, if we start from |0>, the state is defined by Z outputs?
        # No, tableau represents the UNITARY.
        # If we act on |0>, we care about the state.
        pass

    # Print used qubits in baseline
    used_qubits = set()
    for instr in baseline:
        for t in instr.targets_copy():
            if t.is_qubit_target:
                used_qubits.add(t.value)
    print(f"Max used qubit index: {max(used_qubits) if used_qubits else -1}")
    
    circuit = tableau.to_circuit(method="graph_state")
    print(f"Graph circuit qubits: {circuit.num_qubits}")

if __name__ == "__main__":
    main()
