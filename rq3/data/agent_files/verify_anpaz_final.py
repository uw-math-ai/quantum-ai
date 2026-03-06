import stim

candidate_str = """
CX 0 6
S 4 5
H 3 4 5
CX 3 0 4 0 5 0
H 1 3
CX 1 3 1 6
S 5
H 5 6
CX 5 1 6 1 5 2 2 5 5 2
S 2
H 3
CX 2 3
S 4
H 4
CX 4 2
H 4 6
CX 3 4 3 6
H 6
CX 6 3
S 4
H 4
S 4
CX 6 4 6 5 5 6 6 5
H 5
CX 5 6
S 8 9
H 8 9
CX 8 5 9 5
S 6
H 6
S 6 8
CX 6 8
S 7
H 7
CX 7 6
H 7
S 7 9
H 9
CX 8 7 9 7
H 9
CX 8 9
S 9
H 9
S 9
H 0 8 9
S 0 0 8 8 9 9
H 0 8 9
S 2 2 6 6 7 7 8 8
CX 10 16
S 14 15
H 13 14 15
CX 13 10 14 10 15 10
H 11 13
CX 11 13 11 16
S 15
H 15 16
CX 15 11 16 11 15 12 12 15 15 12
S 12
H 13
CX 12 13
S 14
H 14
CX 14 12
H 14 16
CX 13 14 13 16
H 16
CX 16 13
S 14
H 14
S 14
CX 16 14 16 15 15 16 16 15
H 15
CX 15 16
S 18 19
H 18 19
CX 18 15 19 15
S 16
H 16
S 16 18
CX 16 18
S 17
H 17
CX 17 16
H 17
S 17 19
H 19
CX 18 17 19 17
H 19
CX 18 19
S 19
H 19
S 19
H 10 18 19
S 10 10 18 18 19 19
H 10 18 19
S 12 12 16 16 17 17 18 18
"""

targets_str = [
"XZZXIIIIIIIIIIIIIIII", "IIIIIXZZXIIIIIIIIIII", "IIIIIIIIIIXZZXIIIIII", "IIIIIIIIIIIIIIIXZZXI",
"IXZZXIIIIIIIIIIIIIII", "IIIIIIXZZXIIIIIIIIII", "IIIIIIIIIIIXZZXIIIII", "IIIIIIIIIIIIIIIIXZZX",
"XIXZZIIIIIIIIIIIIIII", "IIIIIXIXZZIIIIIIIIII", "IIIIIIIIIIXIXZZIIIII", "IIIIIIIIIIIIIIIXIXZZ",
"ZXIXZIIIIIIIIIIIIIII", "IIIIIZXIXZIIIIIIIIII", "IIIIIIIIIIZXIXZIIIII", "IIIIIIIIIIIIIIIZXIXZ",
"XXXXXXXXXXXXXXXXXXXX", "ZZZZZZZZZZZZZZZZZZZZ"
]

def verify():
    c = stim.Circuit(candidate_str)
    sim = stim.TableauSimulator()
    sim.do_circuit(c)
    
    all_good = True
    for i, t_str in enumerate(targets_str):
        # Handle trailing/leading spaces if any
        t_str = t_str.strip()
        p = stim.PauliString(t_str)
        exp = sim.peek_observable_expectation(p)
        if exp != 1:
            print(f"Failed stabilizer {i}: {t_str}, expectation={exp}")
            all_good = False
            
    if all_good:
        print("Verification SUCCESS: All stabilizers preserved.")
    else:
        print("Verification FAILED.")

if __name__ == "__main__":
    verify()
