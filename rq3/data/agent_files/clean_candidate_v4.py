
import stim

def load_circuit(filename):
    with open(filename, 'r') as f:
        return stim.Circuit(f.read())

def main():
    candidate = load_circuit("candidate_graph.stim")
    clean = stim.Circuit()
    for instr in candidate:
        if instr.name == "TICK":
            continue
        clean.append(instr)
        
    with open("candidate_clean.stim", "w") as f:
        f.write(str(clean))

if __name__ == "__main__":
    main()
