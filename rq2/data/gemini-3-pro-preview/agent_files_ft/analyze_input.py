import sys
import os

def parse_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    # Handle comma separated stabilizers if they are in one line
    stabilizers = []
    for line in lines:
        parts = line.strip().split(',')
        for part in parts:
            if part.strip():
                stabilizers.append(part.strip())
    return stabilizers

def main():
    circuit_path = "data/gemini-3-pro-preview/agent_files_ft/circuit.stim"
    stabilizers_path = "data/gemini-3-pro-preview/agent_files_ft/stabilizers.txt"
    
    with open(circuit_path, 'r') as f:
        circuit_str = f.read()
    
    stabilizers = parse_stabilizers(stabilizers_path)
    
    print(f"Number of stabilizers: {len(stabilizers)}")
    if len(stabilizers) > 0:
        print(f"First stabilizer: {stabilizers[0]}")
        print(f"Length of first stabilizer: {len(stabilizers[0])}")
        
    num_data_qubits = len(stabilizers[0])
    print(f"Num data qubits inferred: {num_data_qubits}")
    
    # Simple qubit counting in circuit
    max_qubit = 0
    import re
    # Match integers
    qubits = [int(x) for x in re.findall(r'\b\d+\b', circuit_str)]
    if qubits:
        max_qubit = max(qubits)
    print(f"Max qubit index in circuit: {max_qubit}")

if __name__ == "__main__":
    main()
