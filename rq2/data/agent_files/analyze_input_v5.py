import sys
import re
import json

def read_stabilizers(filename):
    with open(filename, 'r') as f:
        content = f.read().strip()
    # Split by comma and strip whitespace
    stabs = [s.strip() for s in content.split(',')]
    return stabs

def read_circuit(filename):
    with open(filename, 'r') as f:
        return f.read().strip()

def main():
    stabs = read_stabilizers('stabilizers_list.txt')
    circuit = read_circuit('input_circuit_v2.stim')
    
    # Calculate data qubits from stabilizer length
    num_qubits = len(stabs[0])
    data_qubits = list(range(num_qubits))
    
    print(f"Num stabilizers: {len(stabs)}")
    print(f"Stabilizer length: {num_qubits}")
    print(f"Data qubits: 0-{num_qubits-1}")
    
    # Use flag qubits 
    flag_qubits = []

    # Construct the arguments for the validation tool
    # Note: validation tool expects 'circuit' as a string, 'data_qubits' as list of int, 'flag_qubits' as list of int, 'stabilizers' as list of string
    
    output = {
        "circuit": circuit,
        "data_qubits": data_qubits,
        "flag_qubits": flag_qubits,
        "stabilizers": stabs
    }
    
    print(json.dumps(output))
    
if __name__ == "__main__":
    main()
