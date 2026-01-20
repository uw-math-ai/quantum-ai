import stim

# This circuit is a fault tolerant cat state
# Data qubits: 8 (0-7)
# Ancilla qubits: 8 (8-15)
# Reference: https://mqt.readthedocs.io/projects/qecc/en/latest/CatStates.html
def circuit_1():
    circuit = """
        H 0
        CX 0 4
        CX 0 2
        CX 0 1
        CX 2 3 
        CX 4 6 
        CX 4 5
        CX 6 7
        H 8
        CX 8 14
        CX 8 10
        CX 8 9
        CX 10 11 
        CX 12 14 
        CX 12 13
        CX 14 15
        CX 1 9
        CX 7 8
        M 9
        CX 2 10
        CX 3 11
        CX 4 12
        CX 5 13
        CX 0 15
        CX 6 14
        M 15
        M 8
        M 10
        M 11
        M 12
        M 13
        M 14
        """

    return str(circuit)


# This circuit represents a fault tolerant cat state (simpler than circuit_1)
# Data qubits: 3 (0-2)
# Ancilla Qubits: 2 (3-4)
# Reference: https://arxiv.org/pdf/2108.02184
def circuit_2():
    circuit = """
        H 0 
        CX 0 3
        CX 0 1
        CX 0 2
        CX 0 4
        M 3
        M 4
        """
    return str(circuit)



def visualize(circuit): 
    circ = stim.Circuit()
    split = circuit.splitlines()
    for index in range(1, len(split) - 1):
        line = split[index]
        tokens = line.split()
        gate = tokens[0]
        qubits = []
        for i in range(1, len(tokens)):
           qubits.append(int(tokens[i]))
        circ.append(gate, qubits)
    print(circ.diagram())


circuit = circuit_1()
visualize(circuit)