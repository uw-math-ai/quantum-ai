import stim

def generate_candidate():
    with open('baseline.stim', 'r') as f:
        circuit = stim.Circuit(f.read())

    new_circuit = stim.Circuit()
    next_ancilla = 81
    ancillas = []

    for instruction in circuit:
        if instruction.name == "CX":
            targets = instruction.targets_copy()
            pairs = []
            for i in range(0, len(targets), 2):
                pairs.append((targets[i].value, targets[i+1].value))
            
            groups = {}
            order = []
            for c, t in pairs:
                if c not in groups:
                    groups[c] = []
                    order.append(c)
                groups[c].append(t)
            
            for c in order:
                t_list = groups[c]
                if len(t_list) >= 4:
                    flag = next_ancilla
                    next_ancilla += 1
                    ancillas.append(flag)
                    
                    new_circuit.append("CX", [c, flag])
                    for t in t_list:
                        new_circuit.append("CX", [c, t])
                    new_circuit.append("CX", [c, flag])
                else:
                    for t in t_list:
                        new_circuit.append("CX", [c, t])
        else:
            new_circuit.append(instruction)

    if ancillas:
        new_circuit.append("M", ancillas)

    # Manual serialization to avoid line wrapping issues with str(circuit)
    circuit_str = ""
    for instruction in new_circuit:
        if instruction.name == "CX":
            # Print each pair or small group
            targets = instruction.targets_copy()
            for i in range(0, len(targets), 2):
                circuit_str += f"CX {targets[i].value} {targets[i+1].value}\n"
        elif instruction.name == "M":
             # Print M on one line, assuming it fits or split if needed
             targets = instruction.targets_copy()
             t_vals = [t.value for t in targets]
             # valid_circuit tool might not like super long lines, but M 81 ... 101 is short.
             circuit_str += f"M {' '.join(map(str, t_vals))}\n"
        else:
            circuit_str += str(instruction) + "\n"

    return circuit_str

nc = generate_candidate()
with open('candidate.stim', 'w') as f:
    f.write(nc)
