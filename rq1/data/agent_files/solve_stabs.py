import stim

def solve_circuit():
    stabilizers = [
        "XXXIIIXXXIII",
        "IIXXXIIIXXXI",
        "XIIIXXXIIIXX",
        "XXXXXXIIIIII",
        "IIIIIIXXXXXX",
        "IIZZZZIZIZII",
        "ZIIIZIZZZIIZ",
        "ZZZIIZZIIIZI",
        "ZIIZZZIIZIZI",
        "IZZIIIZZIZIZ"
    ]
    
    full_stabs = [stim.PauliString(s) for s in stabilizers]
    
    try:
        # Create a Tableau from the stabilizers.
        # This will find a clifford C such that C |0> is stabilized by the given stabilizers.
        # Note: stim.Tableau.from_stabilizers returns a Tableau representing the state.
        # Actually, it returns a Tableau T such that the Z outputs of T are the stabilizers.
        # So applying T^-1 (inverse) to the stabilizers gives Z_i.
        # Wait, usually we want T such that T * Z_i * T^-1 = S_i.
        # So applying T to |0> (stabilized by Z_i) gives state stabilized by S_i.
        # The method to_circuit() gives the circuit for T.
        t = stim.Tableau.from_stabilizers(full_stabs, allow_underconstrained=True)
        
        # However, to_circuit() might produce a circuit that is too complex or uses many ancillas if not careful.
        # "elimination" method usually produces a circuit with H, S, CX, etc.
        # Let's see what it produces.
        c = t.to_circuit("elimination")
        
        with open("circuit_final.stim", "w") as f:
            for instr in c:
                if instr.name == "CX" or instr.name == "CNOT":
                    targets = instr.targets_copy()
                    for i in range(0, len(targets), 2):
                        f.write(f"CX {targets[i].value} {targets[i+1].value}\n")
                else:
                    f.write(str(instr) + "\n")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    solve_circuit()
