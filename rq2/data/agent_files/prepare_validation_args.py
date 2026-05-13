import stim
import json

def prepare():
    with open("candidate_narrow.stim", "r") as f:
        circuit_str = f.read()
    
    circuit = stim.Circuit(circuit_str)
    
    # Identify data and flag qubits
    # Data are 0-80 (d=9 code uses 81 qubits? Or maybe less? 
    # The prompt says "d=9". Usually d^2 = 81.
    # The highest index in original circuit is 80. So 0..80 are data.
    
    data_qubits = list(range(81))
    
    # Find all used qubits in the new circuit
    used_qubits = set()
    for op in circuit:
        for t in op.targets_copy():
            if t.is_qubit_target:
                used_qubits.add(t.value)
                
    # Flags are used_qubits - data_qubits
    flag_qubits = sorted(list(used_qubits - set(data_qubits)))
    
    # Read stabilizers
    with open("stabilizers.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]
        
    output = {
        "circuit": circuit_str,
        "data_qubits": data_qubits,
        "flag_qubits": flag_qubits,
        "stabilizers": stabilizers
    }
    
    # Print as JSON for me to copy, or just the flag list
    print(json.dumps(output))

if __name__ == "__main__":
    prepare()
