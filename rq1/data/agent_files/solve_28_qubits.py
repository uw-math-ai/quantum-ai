import stim
import numpy as np

# Target stabilizers
stabilizers = [
    "XXXXIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIXXXXIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIXXXXIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIXXXXIII",
    "XIXIXIXIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIXIXIXIXIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIXIXIXIXIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIXIXIXIX",
    "IIXXXXIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIXXXXIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIXXXXIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIXXXXI",
    "ZZZZIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIZZZZIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIZZZZIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIZZZZIII",
    "ZIZIZIZIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIZIZIZIZIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIZIZIZIZIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIZIZIZIZ",
    "IIZZZZIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIZZZZIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIZZZZIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIZZZZI",
    "IXXIXIIIXXIXIIIXXIXIIIXXIXII",
    "IZZIZIIIZZIZIIIZZIZIIIZZIZII"
]

def solve_tableau():
    try:
        t = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers], allow_underconstrained=True, allow_redundant=True)
        
        # Check if t stabilizes the inputs
        # t.inverse(s) should be Z-type.
        for i, s_str in enumerate(stabilizers):
            s = stim.PauliString(s_str)
            inv_s = t.inverse()(s)
            is_z = True
            for p in inv_s:
                if p == 1 or p == 2: # X or Y
                    is_z = False
                    break
            if not is_z or inv_s.sign != 1:
                print(f"Tableau check FAIL: Stabilizer {i} {s_str} -> {inv_s}")
            else:
                pass 

        circuit = t.to_circuit("elimination")
        with open("circuit_candidate.stim", "w") as f:
            f.write(str(circuit))
        print("Circuit written to circuit_candidate.stim")
        
    except Exception as e:
        print(f"Error creating tableau: {e}")


if __name__ == "__main__":
    solve_tableau()
