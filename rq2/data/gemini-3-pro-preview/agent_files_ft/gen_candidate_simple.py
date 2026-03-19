
import stim

def generate_circuit():
    input_circuit_str = "H 0 1\nCX 0 1 0 4\nH 2 3\nCX 1 2 1 3 1 4 1 5 1 8 1 14 2 4 2 5 2 6 2 9 2 10 4 3 3 4 4 3 3 6 3 10 4 5 4 7 4 8 4 11 4 14 5 6 5 7 5 9 5 11 5 12 6 7 6 12 6 13 7 13 11 8 12 8 13 8 14 8 9 10 12 9 13 9 14 9 12 10 13 10 14 10 12 11 11 12 12 11 11 12 13 11 14 11 13 12 14 12 14 13"
    stabilizers = [
        "XXXXXXXXIIIIIII", "IXXIXXIIXXIXXII", "IIXXIXXIIXXXIXI", "IIIIXXXXIIIXXXX", 
        "ZZZZIIIIIIIIIII", "IZZIZZIIIIIIIII", "IIZZIZZIIIIIIII", "IIIIZZZZIIIIIII", 
        "IZIIZIIIZIIIZII", "IIZIIZIIIZIZIII", "IIZZIIIIIZZIIII", "IIIIZZIIIIIZZII", 
        "IIIIIZZIIIIZIZI", "IIIIIIZZIIIIIZZ"
    ]
    
    circuit = stim.Circuit(input_circuit_str)
    
    data_qubits = 15
    ancilla_start = 15
    
    for i, stab in enumerate(stabilizers):
        ancilla = ancilla_start + i
        
        # Check if pure X or pure Z
        is_x = 'X' in stab and 'Z' not in stab
        is_z = 'Z' in stab and 'X' not in stab
        
        if is_x:
            circuit.append("H", [ancilla])
            for q in range(data_qubits):
                if stab[q] == 'X':
                    circuit.append("CX", [ancilla, q])
            circuit.append("H", [ancilla])
        elif is_z:
            for q in range(data_qubits):
                if stab[q] == 'Z':
                    circuit.append("CX", [q, ancilla])
                    
    return circuit

if __name__ == "__main__":
    c = generate_circuit()
    print(str(c))
