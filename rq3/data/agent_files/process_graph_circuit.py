
import stim

def process():
    with open("candidate_graph.stim", "r") as f:
        content = f.read()
    
    circuit = stim.Circuit(content)
    new_circuit = stim.Circuit()
    
    for op in circuit:
        if op.name == "RX":
            # Replace RX with H, assuming start state |0>
            # RX resets to |+>. H|0> = |+>.
            targets = op.targets_copy()
            new_circuit.append("H", targets)
        elif op.name == "TICK":
            continue
        else:
            new_circuit.append(op)
            
    with open("candidate_cleaned.stim", "w") as f:
        f.write(str(new_circuit))

if __name__ == "__main__":
    process()
