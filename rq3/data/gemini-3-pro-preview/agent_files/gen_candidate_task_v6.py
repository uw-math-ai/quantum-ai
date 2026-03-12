import stim
import sys
import os

def generate():
    print("Reading stabilizers...")
    try:
        with open('task_stabilizers.txt', 'r') as f:
            lines = [l.strip() for l in f if l.strip()]
        
        # Stim 1.12+ supports from_stabilizers with list of PauliString
        stabs = [stim.PauliString(l) for l in lines]
        print(f"Loaded {len(stabs)} stabilizers.")
        
        # Try to create tableau from stabilizers directly
        # We use allow_redundant and allow_underconstrained to be flexible
        tableau = stim.Tableau.from_stabilizers(stabs, allow_redundant=True, allow_underconstrained=True)
        print("Tableau created from stabilizers.")
        
    except Exception as e:
        print(f"Failed to create tableau from stabilizers: {e}")
        print("Attempting to extract tableau from baseline...")
        
        try:
            with open('task_baseline.stim', 'r') as f:
                baseline_text = f.read()
            
            baseline = stim.Circuit(baseline_text)
            sim = stim.TableauSimulator()
            sim.do(baseline)
            # transform input Z basis to output stabilizers
            # The tableau T maps Z_i to S_i.
            # sim.current_inverse_tableau() gives T^-1
            tableau = sim.current_inverse_tableau().inverse()
            print("Tableau extracted from baseline.")
            
        except Exception as e2:
            print(f"Failed to extract from baseline: {e2}")
            return

    print("Synthesizing circuit with method='graph_state'...")
    # This method produces CZ + single qubit gates. CZ has 0 CX cost.
    candidate = tableau.to_circuit(method='graph_state')
    
    # Post-processing: Replace RX with H.
    # We iterate over instructions and build a new circuit.
    new_candidate = stim.Circuit()
    for instruction in candidate:
        if instruction.name == "RX":
            # Replace RX with H
            new_candidate.append("H", instruction.targets_copy())
        else:
            new_candidate.append(instruction)
            
    candidate = new_candidate
    
    # Convert to string
    cand_str = str(candidate)
    
    # Write to file
    with open('candidate.stim', 'w') as f:
        f.write(cand_str)
    
    print("Candidate written to candidate.stim")

if __name__ == "__main__":
    generate()
