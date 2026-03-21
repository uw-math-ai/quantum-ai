
def generate_circuit():
    circuit = []
    
    # Block 1: SWAP
    circuit.append("CX 2 0 0 2 2 0")
    
    # Check 0 and 2 (expect |0>)
    # Detects X errors.
    # CNOT target=ancilla, control=data.
    # If data is 1 (X error), ancilla flips to 1.
    # Use ancillas 7, 8
    circuit.append("CX 0 7 2 8")
    circuit.append("M 7 8")
    
    # Block 2: H
    circuit.append("H 0 1 2")
    
    # Check 0, 1, 2 (expect |+>)
    # Detects Z errors.
    # Use ancillas 9, 10, 11
    circuit.append("H 9 10 11")
    circuit.append("CX 9 0 10 1 11 2")
    circuit.append("H 9 10 11")
    circuit.append("M 9 10 11")
    
    # Block 3: Rest
    circuit.append("CX 0 1 0 2 0 5 1 4 1 5 1 6 2 3 2 5 2 6 4 3 3 4 4 3 5 3 6 3 5 4 6 4")
    
    return "\n".join(circuit)

if __name__ == "__main__":
    print(generate_circuit())
