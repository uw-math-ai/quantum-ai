import stim
import os

def clean_circuit(circuit_str):
    # Replace RX with H (assuming start state is |0>)
    # Remove TICK
    lines = []
    for line in circuit_str.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("TICK"):
            continue
        if line.startswith("RX"):
            # RX targets
            # RX 0 1 2 -> H 0 H 1 H 2
            targets = line[3:].strip().split()
            # Construct H command
            new_line = "H " + " ".join(targets)
            lines.append(new_line)
        else:
            lines.append(line)
    return "\n".join(lines)

def main():
    # Load circuits
    with open("baseline.stim", "r") as f:
        baseline_text = f.read()
    
    if os.path.exists("candidate_graph.stim"):
        with open("candidate_graph.stim", "r") as f:
            graph_text = f.read()
        
        # Clean graph text just in case
        graph_clean = clean_circuit(graph_text)
        with open("candidate1_clean.stim", "w") as f:
            f.write(graph_clean)
            
        print(f"Baseline length: {len(baseline_text)}")
        print(f"Graph length: {len(graph_text)}")
        if baseline_text.strip() == graph_text.strip():
            print("candidate_graph.stim is IDENTICAL to baseline.")
        else:
            print("candidate_graph.stim is DIFFERENT from baseline.")

    if os.path.exists("candidate_elim.stim"):
        with open("candidate_elim.stim", "r") as f:
            elim_text = f.read()
        
        elim_clean = clean_circuit(elim_text)
        with open("candidate2_clean.stim", "w") as f:
            f.write(elim_clean)
            
        print(f"Elim length: {len(elim_text)}")
        
if __name__ == "__main__":
    main()
