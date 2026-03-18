import stim

# Load the candidate
try:
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq3\best_candidate.stim", "r") as f:
        content = f.read()
except FileNotFoundError:
    print("Error: best_candidate.stim not found")
    exit(1)

# Replace RX with H
# Parse line by line to handle variable length args
# Or better, parse with stim
circuit = stim.Circuit(content)
new_circuit = stim.Circuit()

for instr in circuit:
    if instr.name == "RX":
        new_circuit.append("H", instr.targets_copy())
    elif instr.name == "TICK":
        pass # Drop TICKs to clean up
    elif instr.name == "R":
        # R is Reset to 0. If it exists, keep it or replace?
        # Baseline doesn't have R.
        new_circuit.append("R", instr.targets_copy())
    else:
        new_circuit.append(instr)

def optimize_circuit(circ):
    insts = list(circ)
    changed = True
    while changed:
        changed = False
        new_insts = []
        i = 0
        while i < len(insts):
            if i + 1 < len(insts):
                op1 = insts[i]
                op2 = insts[i+1]
                # Check for H-H, X-X, Z-Z, Y-Y, SWAP-SWAP, CX-CX (same targets)
                if op1.name == op2.name and op1.name in ["H", "X", "Y", "Z", "SWAP", "CX", "CZ"] and op1.targets_copy() == op2.targets_copy():
                    i += 2
                    changed = True
                    continue
            new_insts.append(insts[i])
            i += 1
        insts = new_insts
    
    out = stim.Circuit()
    for inst in insts:
        out.append(inst)
    return out

# Run optimization multiple times
optimized = optimize_circuit(new_circuit)
for _ in range(5):
    optimized = optimize_circuit(optimized)

# Verify stabilizers
stabilizers = [
"XZZXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIXZZXIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIXZZXIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIXZZXIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIXZZXIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIXZZXIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXZZXI", "IXZZXIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIXZZXIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIXZZXIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIXZZXIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIXZZXIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIXZZXIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXZZX", "XIXZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIXIXZZIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIXIXZZIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIXIXZZIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIXIXZZIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIXIXZZIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXZZ", "ZXIXZIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIZXIXZIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIZXIXZIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIZXIXZIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIZXIXZIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIZXIXZIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZXIXZ", "XXXXXXXXXXXXXXXXXXXXIIIIIIIIIIIIIII", "XXXXXIIIIIXXXXXIIIIIXXXXXIIIIIXXXXX", "IIIIIIIIIIXXXXXXXXXXXXXXXXXXXXIIIII", "ZZZZZZZZZZZZZZZZZZZZIIIIIIIIIIIIIII", "ZZZZZIIIIIZZZZZIIIIIZZZZZIIIIIZZZZZ", "IIIIIIIIIIZZZZZZZZZZZZZZZZZZZZIIIII"
]

def check(circ, stabs):
    sim = stim.TableauSimulator()
    sim.do(circ)
    for s in stabs:
        p = stim.PauliString(s)
        if sim.peek_observable_expectation(p) != 1:
            return False
    return True

final_circ = optimized
if check(final_circ, stabilizers):
    print("Optimized candidate valid.")
else:
    print("Optimized candidate INVALID. Using unoptimized new_circuit.")
    final_circ = new_circuit
    if not check(final_circ, stabilizers):
        print("CRITICAL: Even unoptimized circuit is invalid!")

# Save
with open(r"C:\Users\anpaz\Repos\quantum-ai\rq3\candidate_final.stim", "w") as f:
    f.write(str(final_circ))

# Metrics
def get_metrics(circuit):
    cx_count = 0
    volume = 0
    for instr in circuit:
        if instr.name in ["CX", "CNOT", "CZ"]:
            cx_count += len(instr.targets_copy()) // 2
            volume += len(instr.targets_copy())
        elif instr.name in ["H", "S", "S_DAG", "X", "Y", "Z"]:
             volume += len(instr.targets_copy())
    return cx_count, volume

cx, vol = get_metrics(final_circ)
print(f"Final Candidate Metrics: CX={cx}, Vol={vol}")
