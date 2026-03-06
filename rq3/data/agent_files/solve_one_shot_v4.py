import stim
import sys

# Define the baseline circuit string
baseline_str = """
H 0
S 21 31
H 4 5 8 18 19 22 33
CX 0 4 0 5 0 8 0 18 0 19 0 21 0 22 0 31 0 32 0 33
H 14 28 29
CX 14 0 28 0 29 0 31 1 1 31 31 1
H 1
S 1
CX 1 32
S 7
H 4 5 7 8 14 18 19 22 32 33
CX 4 1 5 1 7 1 8 1 14 1 18 1 19 1 22 1 28 1 29 1 32 1 33 1 7 2 2 7 7 2
H 2
S 2
H 14
CX 14 2 28 2 29 2 21 3 3 21 21 3
S 3
H 3
S 3 14
CX 3 14 28 3 29 3 14 4 4 14 14 4
S 4
H 4
CX 28 4 29 4 31 5 5 31 31 5
H 5 32
CX 5 22 5 32
H 15
CX 15 5 28 5 8 6 6 8 8 6
H 6 10 16 21 22 23 34
CX 6 10 6 15 6 16 6 21 6 22 6 23 6 28 6 32 6 34 22 6 28 6 28 7 7 28 28 7
H 22
CX 7 10 7 16 7 21 7 22 7 23 7 32 7 34 15 7 15 8 8 15 15 8
H 8
CX 8 32
H 32
CX 22 8 32 8 22 9 9 22 22 9 32 9 28 10 10 28 28 10
H 10
S 23 33
H 14 17 18 19 22 31 34
CX 10 14 10 17 10 18 10 19 10 21 10 22 10 23 10 31 10 33 10 34
H 30
CX 16 10 29 10 30 10 22 11 11 22 22 11
S 33
CX 11 33 23 11 29 11 30 11 16 12 12 16 16 12
H 23 33
CX 12 14 12 17 12 18 12 19 12 21 12 23 12 31 12 33 12 34 29 12 30 12 23 13 13 23 23 13
H 13
S 13
CX 13 14 13 17 13 18 13 19 13 21 13 31 13 33 13 34 29 13 30 13 33 14 14 33 33 14
H 14 17 18 19 21 31 33 34
CX 17 14 18 14 19 14 21 14 29 14 30 14 31 14 33 14 34 14 17 15 15 17 17 15
H 15 32
CX 15 24 15 32 15 34
H 21
CX 21 15 30 15 24 16 16 24 24 16
H 16 21 34
CX 16 21 16 32 16 34 28 16 30 16 21 17 17 21 21 17
H 28
CX 17 28 17 32
H 32 34
CX 30 17 32 17 34 17 34 18 18 34 34 18
H 18 32
CX 18 28 18 32
H 28 32
CX 28 18 30 18 32 18 28 19 19 28 28 19
H 32
CX 19 32 30 19 29 20 20 29 29 20
H 21 22 23 33 34
CX 20 21 20 22 20 23 20 25 20 32 20 33 20 34 30 20 33 20 34 20 25 21 21 25 25 21
H 21 33
CX 21 32 21 33 22 21 30 21 33 22 22 33 33 22
H 33
CX 22 32 22 33
H 32
CX 30 22 32 22 34 22 34 23 23 34 34 23
H 23 32
CX 23 32 23 33
H 33
CX 30 23 33 23 33 24 24 33 33 24 30 24 28 25 25 28 28 25
H 25 31 33
CX 25 26 25 30 25 31 25 33 30 25 31 25
H 26 31
CX 26 31 30 26 33 26 31 27 27 31 31 27
H 33
CX 27 33 30 27 33 28 28 33 33 28
S 28
H 28
S 28 30
H 30
CX 30 28 30 29 29 30 30 29
H 29
S 29
H 30
CX 30 31 30 32 33 30
H 31
S 31 32 33
CX 31 32 31 33 34 31
H 32
S 32
H 33 34
CX 32 33 32 34
H 33
S 33
CX 33 34
H 34 1 3 8 17 23 27 32
S 1 1 3 3 8 8 17 17 23 23 27 27 32 32
H 1 3 8 17 23 27 32
S 0 0 2 2 3 3 4 4 7 7 10 10 11 11 12 12 14 14 16 16 18 18 19 19 20 20 21 21 23 23 24 24 26 26 28 28 30 30 32 32 33 33 34 34
"""

stabilizers = [
"XZZXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIXZZXIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIXZZXIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIXZZXIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIXZZXIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIXZZXIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXZZXI", "IXZZXIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIXZZXIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIXZZXIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIXZZXIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIXZZXIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIXZZXIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXZZX", "XIXZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIXIXZZIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIXIXZZIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIXIXZZIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIXIXZZIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIXIXZZIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXZZ", "ZXIXZIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIZXIXZIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIZXIXZIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIZXIXZIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIZXIXZIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIZXIXZIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZXIXZ", "XXXXXXXXXXXXXXXXXXXXIIIIIIIIIIIIIII", "XXXXXIIIIIXXXXXIIIIIXXXXXIIIIIXXXXX", "IIIIIIIIIIXXXXXXXXXXXXXXXXXXXXIIIII", "ZZZZZZZZZZZZZZZZZZZZIIIIIIIIIIIIIII", "ZZZZZIIIIIZZZZZIIIIIZZZZZIIIIIZZZZZ", "IIIIIIIIIIZZZZZZZZZZZZZZZZZZZZIIIII"
]

def get_cx_count(circuit):
    count = 0
    for instr in circuit:
        if instr.name in ["CX", "CNOT", "CZ"]: # Treating CZ as 1 for now, will fix later
             count += len(instr.targets_copy()) // 2
    return count

def get_volume(circuit):
    return sum(len(instr.targets_copy()) for instr in circuit if instr.name not in ["TICK", "SHIFT_COORDS", "QUBIT_COORDS"])

def check_stabilizers_preserved(circuit, stabs):
    sim = stim.TableauSimulator()
    sim.do(circuit)
    for s in stabs:
        if sim.peek_observable_expectation(stim.PauliString(s)) != 1:
            return False
    return True

# Parse baseline
baseline = stim.Circuit(baseline_str)
base_cx = get_cx_count(baseline)
base_vol = get_volume(baseline)
print(f"Baseline metrics: CX={base_cx}, Vol={base_vol}")

candidates = []

# Method 1: Tableau Synthesis (Elimination)
try:
    # Note: We need to invert the tableau to get a circuit that PREPARES the state.
    # stim.Tableau.from_stabilizers gives a tableau that stabilizes the state |0> -> |S>.
    # Wait, from_stabilizers returns a tableau T such that T|0> has the stabilizers.
    # So T.to_circuit() prepares the state.
    t = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers], allow_underconstrained=True)
    c1 = t.to_circuit(method="elimination")
    
    # Check validity
    if check_stabilizers_preserved(c1, stabilizers):
        candidates.append(("elimination", c1))
        print(f"Elimination synthesis valid. CX={get_cx_count(c1)}")
    else:
        print("Elimination synthesis invalid.")

    # Method 2: Graph State Synthesis
    c2_raw = t.to_circuit(method="graph_state")
    # Convert CZ to CX
    c2 = stim.Circuit()
    for instr in c2_raw:
        if instr.name == "CZ":
            targs = instr.targets_copy()
            for k in range(0, len(targs), 2):
                q1, q2 = targs[k], targs[k+1]
                c2.append("H", [q2])
                c2.append("CX", [q1, q2])
                c2.append("H", [q2])
        else:
            c2.append(instr)
            
    if check_stabilizers_preserved(c2, stabilizers):
        candidates.append(("graph_state", c2))
        print(f"Graph state synthesis valid. CX={get_cx_count(c2)}")
    else:
        print("Graph state synthesis invalid.")

except Exception as e:
    print(f"Synthesis error: {e}")

# Method 3: Simple Optimization of Baseline
# Iteratively remove H-H, S-Sdag, etc.
def optimize_circuit(circ):
    # Convert to instructions
    insts = list(circ)
    changed = True
    while changed:
        changed = False
        new_insts = []
        i = 0
        while i < len(insts):
            # Check for cancellation with next
            if i + 1 < len(insts):
                op1 = insts[i]
                op2 = insts[i+1]
                # Same gate on same targets?
                if op1.name == op2.name and op1.targets_copy() == op2.targets_copy():
                    # Self-inverse gates
                    if op1.name in ["H", "X", "Y", "Z", "CX", "CZ", "SWAP"]:
                        i += 2
                        changed = True
                        continue
                # Inverse pairs (S/Sdag, etc) - Stim doesn't easily show inverse property on instruction object
                # We can implement specific checks
            new_insts.append(insts[i])
            i += 1
        insts = new_insts
    
    # Rebuild circuit
    new_circ = stim.Circuit()
    for inst in insts:
        new_circ.append(inst)
    return new_circ

c3 = optimize_circuit(baseline)
# Re-check validity just in case
if check_stabilizers_preserved(c3, stabilizers):
    candidates.append(("optimized_baseline", c3))
    print(f"Optimized baseline valid. CX={get_cx_count(c3)}")

# Select best candidate
best_cand = None
best_score = (base_cx, base_vol) # (cx, vol)

for name, circ in candidates:
    cx = get_cx_count(circ)
    vol = get_volume(circ)
    print(f"Candidate {name}: CX={cx}, Vol={vol}")
    
    if (cx < best_score[0]) or (cx == best_score[0] and vol < best_score[1]):
        best_score = (cx, vol)
        best_cand = circ

if best_cand:
    print("Found improvement!")
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq3\best_candidate.stim", "w") as f:
        f.write(str(best_cand))
else:
    print("No improvement found. Saving baseline as best fallback.")
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq3\best_candidate.stim", "w") as f:
        f.write(str(baseline))

