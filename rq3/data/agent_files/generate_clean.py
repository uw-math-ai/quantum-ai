import stim

def solve():
    print("Generating clean circuit...")
    baseline = stim.Circuit.from_file("data/agent_files/baseline.stim")
    sim = stim.TableauSimulator()
    sim.do(baseline)
    stabilizers = sim.canonical_stabilizers()
    
    tableau = stim.Tableau.from_stabilizers(stabilizers)
    circuit_e = tableau.to_circuit("elimination")
    
    clean_str = ""
    for instr in circuit_e:
        if instr.name == "CX":
             targets = instr.targets_copy()
             for i in range(0, len(targets), 2):
                 c = targets[i].value
                 t = targets[i+1].value
                 clean_str += f"H {t}\n"
                 clean_str += f"CZ {c} {t}\n"
                 clean_str += f"H {t}\n"
        elif instr.name in ["H", "S", "X", "Y", "Z"]:
             targets = instr.targets_copy()
             for t in targets:
                 clean_str += f"{instr.name} {t.value}\n"
        else:
             # Keep other instructions as is (unlikely to be complex)
             clean_str += str(instr) + "\n"
             
    with open("data/agent_files/candidate_clean.stim", "w") as f:
        f.write(clean_str)
        
    print("Done.")

if __name__ == "__main__":
    solve()
