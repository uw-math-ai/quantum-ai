import stim

def solve():
    # Load baseline
    try:
        with open("baseline.stim", "r") as f:
            baseline_text = f.read()
        baseline = stim.Circuit(baseline_text)
    except Exception as e:
        print(f"Error loading baseline: {e}")
        return

    # Convert to Tableau and re-synthesize using graph_state method
    # This usually minimizes CX count (by using CZs)
    tableau = baseline.to_tableau()
    
    # Generate circuit using graph_state method
    # "graph_state" allows outputting a circuit that prepares the state, using CZ gates.
    candidate = tableau.to_circuit(method="graph_state")
    
    # Convert back to string
    candidate_str = str(candidate)
    
    # Replace RX with H (assuming start from |0>)
    # RX is "Reset to X basis". If we are at |0>, H takes us to |+> (X basis 0).
    # If the circuit starts with RX on a qubit, it's equivalent to H on that qubit (since input is |0>).
    # Since 'graph_state' usually puts RX/H/R at the beginning, this should be safe.
    # We will just replace "RX" with "H".
    # Note: RX in stim is a reset gate. If it happens in the middle, it's a reset.
    # But graph_state method for a tableau typically produces state preparation.
    
    lines = candidate_str.splitlines()
    new_lines = []
    for line in lines:
        if line.strip().startswith("RX"):
            # Replace RX with H
            new_lines.append(line.replace("RX", "H"))
        else:
            new_lines.append(line)
            
    candidate_clean = "\n".join(new_lines)
    
    with open("candidate.stim", "w") as f:
        f.write(candidate_clean)
        
    print(f"Generated candidate.stim using graph_state method.")

if __name__ == "__main__":
    solve()
