
import stim
import sys

def load_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [l.strip() for l in f if l.strip()]
    return lines

def main():
    stabilizers = load_stabilizers("target_stabilizers_fresh.txt")
    
    # Create tableau from stabilizers
    # We need to make sure they are valid Pauli strings.
    try:
        tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers], allow_underconstrained=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # Synthesize using graph_state method
    candidate = tableau.to_circuit(method="graph_state")
    
    # Post-process to remove resets
    clean_candidate = stim.Circuit()
    for instr in candidate:
        if instr.name == "RX":
            # RX resets to |+>. From |0>, H does that.
            clean_candidate.append("H", instr.targets_copy())
        elif instr.name == "R" or instr.name == "RZ":
            # R resets to |0>. We start at |0>, so do nothing.
            pass
        elif instr.name == "MY" or instr.name == "MZ" or instr.name == "MX" or instr.name == "M":
             pass # Remove measurements
        else:
            clean_candidate.append(instr)
            
    with open("candidate_graph.stim", "w") as f:
        f.write(str(clean_candidate))
        
    print("Generated candidate_graph.stim")

if __name__ == "__main__":
    main()
