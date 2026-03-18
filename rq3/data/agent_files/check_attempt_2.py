import stim

def verify():
    with open("current_task_baseline.stim", "r") as f:
        base = stim.Circuit(f.read())
    with open("candidate_attempt_2.stim", "r") as f:
        cand = stim.Circuit(f.read())
        
    tab_base = stim.Tableau.from_circuit(base)
    tab_cand = stim.Tableau.from_circuit(cand)
    
    if tab_base == tab_cand:
        print("Tableaus are identical.")
        print(f"CX gates: {cand.num_gates('CX')}")
        print(f"CZ gates: {cand.num_gates('CZ')}")
        # Volume is approximately total gates
        print(f"Total gates: {sum(1 for _ in cand)}") 
    else:
        print("Tableaus differ!")

if __name__ == "__main__":
    verify()
