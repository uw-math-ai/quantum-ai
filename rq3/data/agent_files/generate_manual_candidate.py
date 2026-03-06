import stim

def main():
    with open("candidate_formatted.stim", "r") as f:
        circuit = stim.Circuit(f.read())
    
    with open("candidate_manual.stim", "w") as f:
        for instr in circuit:
            if instr.name == "CZ":
                targets = instr.targets_copy()
                for i in range(0, len(targets), 2):
                    f.write(f"CZ {targets[i].value} {targets[i+1].value}\n")
            elif instr.name == "H":
                targets = instr.targets_copy()
                for t in targets:
                    f.write(f"H {t.value}\n")
            elif instr.name in ["X", "Y", "Z", "S", "S_DAG", "SQRT_X", "SQRT_X_DAG", "CX", "CY", "CZ", "H"]:
                # Generic splitter for single/two qubit gates
                targets = instr.targets_copy()
                if len(targets) > 0:
                     # Check arity. X,Y,Z,S,H are 1. CX,CY,CZ are 2.
                     # Actually stim.GateTarget doesn't know arity?
                     # instr.name knows arity.
                     arity = 1
                     if instr.name in ["CX", "CY", "CZ", "CNOT"]:
                         arity = 2
                     
                     for i in range(0, len(targets), arity):
                         args = " ".join([str(t.value) for t in targets[i:i+arity]])
                         f.write(f"{instr.name} {args}\n")
            else:
                f.write(str(instr) + "\n")
        
if __name__ == "__main__":
    main()
