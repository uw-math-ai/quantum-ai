
import stim
import json

def get_params():
    with open(r"data\gemini-3-pro-preview\agent_files_ft\final_circuit.stim", "r") as f:
        circuit_str = f.read()
    
    with open(r"data\gemini-3-pro-preview\agent_files_ft\stabilizers.txt", "r") as f:
        stabs = f.read().splitlines()
        
    num_data = 161
    data_qubits = list(range(num_data))
    
    # Recalculate ancillas/flags based on same logic (or just infer from circuit)
    # Circuit has qubits > 160.
    circuit = stim.Circuit(circuit_str)
    used_qubits = set()
    for op in circuit:
        for t in op.targets_copy():
            if t.is_qubit_target:
                used_qubits.add(t.value)
    
    all_qubits = sorted(list(used_qubits))
    ancillas = [q for q in all_qubits if q >= 161]
    
    # We need to distinguish 'flag qubits' from 'measurement ancillas'.
    # In my logic:
    # Measurement ancillas are used to measure stabilizers.
    # Flag qubits are used to check the ancillas.
    # The prompt says: "triggers a flag ancilla".
    # Does 'validate_circuit' distinguish?
    # "List of flag qubit indices".
    # Usually this includes ALL ancillas that might signal an error.
    # If I measure a stabilizer and get -1 (when expected +1), that signals an error!
    # So the measurement ancillas ARE flags (syndrome bits).
    # And the 'flag' qubits (for hook errors) are ALSO flags.
    # So I should include ALL ancillas in `flag_qubits`.
    # "Any fault ... must trigger a flag ancilla".
    # A stabilizer measurement result IS a flag.
    # So `flag_qubits` = `ancillas`.
    
    print(json.dumps({
        "data_qubits": data_qubits,
        "flag_qubits": ancillas,
        "stabilizers": stabs
    }))

if __name__ == "__main__":
    get_params()
