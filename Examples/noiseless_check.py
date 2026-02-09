import stim
from ft_example_circuits import circuit_1, circuit_2, prompted_1


### Do not use

circuits = [circuit_1(), circuit_2(), prompted_1()]

info = {
    "circuit_1" : ["fault-tolerant cat state", 8, 8],
    "circuit_2" : ["fault-tolerant cat state", 3, 2],
    "prompted_1" : ["fault-tolerant bell state from ChatGPT prompt", 2, 1],
}

keys = info.keys()

for (key, value), i in zip(info.items(), range(len(info))):
    print("\n" + "_"*25)
    print("Circuit: ", key)
    print("\n")

    print("Description: ", value[0])
    print("Data qubits: ", value[1])
    print("Flag qubits: ", value[2])

    circuit = circuits[i]
    print("Diagram: ")
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
    print()
    print("Measurement: ")
    sampler = circ.compile_sampler()
    print(sampler.sample(shots=10))
    print()
    print("Detect: ")
    detectors = []
    for j in range(value[2]):
        num = -j - 1
        detectors.append(stim.target_rec(num))
    circ.append("DETECTOR", detectors)
    sampler = circ.compile_detector_sampler()
    print(sampler.sample(shots=10))
    

