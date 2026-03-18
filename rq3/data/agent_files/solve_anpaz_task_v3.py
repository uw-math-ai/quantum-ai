import stim
import random

baseline_str = """
CX 8 0 0 8 8 0
H 0
CX 0 12 0 17
H 8 16
CX 8 0 16 0 12 1 1 12 12 1
H 1
S 1 8
H 2 3 5 10 11 13 17
CX 1 2 1 3 1 5 1 8 1 10 1 11 1 13 1 17 1 18 1 19
H 4
CX 4 1 16 1 17 2 2 17 17 2
H 2 4 8
CX 2 4 2 8
H 3 5 10 11 13 17 18 19
CX 3 2 5 2 10 2 11 2 13 2 16 2 17 2 18 2 19 2 8 3 3 8 8 3
H 3
S 3
H 5 8 10 11 13 17 18 19
CX 3 4 3 5 3 8 3 10 3 11 3 13 3 17 3 18 3 19 16 3
H 4
CX 4 5 4 8 4 10 4 11 4 13 4 17 4 18 4 19 16 4 12 5 5 12 12 5
H 5 13
CX 5 13 5 19
H 9
CX 9 5 16 5 12 6 6 12 12 6
H 19
CX 6 19
H 13
CX 13 6 16 6 9 7 7 9 9 7
S 13 19
CX 7 13 7 19 16 7 19 8 8 19 19 8
S 8
H 8
CX 13 8 16 8 13 9 9 13 13 9
S 9
H 9
CX 16 9
H 12 13 18
CX 10 12 10 13 10 14 10 16 10 17 10 18 10 19 16 10 17 10 14 11 11 14 14 11
H 11 17
CX 11 17 12 11 16 11 17 12 12 17 17 12
H 17
CX 12 17 16 12 17 13 13 17 17 13
S 13
H 13
S 13 16
H 16 17 18 19
CX 16 13 17 13 18 13 19 13 16 14 14 16 16 14
H 14
S 14
H 17 18 19
CX 14 17 14 18 14 19 16 15 15 16 16 15 15 16 15 18 19 15
H 16 18 19
CX 16 18 16 19 17 16 19 17 17 19 19 17
H 19
CX 17 19
H 18
CX 18 17
H 18
CX 18 19
H 19
CX 19 18
H 2 8 9 12 17
S 2 2 8 8 9 9 12 12 17 17
H 2 8 9 12 17
S 0 0 2 2 3 3 4 4 10 10 12 12 14 14 15 15 17 17
"""

def get_metrics(circuit):
    num_cx = 0
    volume = 0
    for instr in circuit:
        if instr.name == "CX" or instr.name == "CNOT":
            n = len(instr.targets_copy()) // 2
            num_cx += n
            volume += n
        elif instr.name in ["H", "S", "S_DAG", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "SQRT_Z", "SQRT_Z_DAG", "X", "Y", "Z", "I"]:
            n = len(instr.targets_copy())
            volume += n
        else:
            n = len(instr.targets_copy())
            volume += n
    return num_cx, volume

def synthesize_best(stabilizers, attempts=1000):
    best_c = None
    best_metrics = (float('inf'), float('inf'))
    
    stabs_pauli = [stim.PauliString(s) for s in stabilizers]
    
    for _ in range(attempts):
        shuffled = list(stabs_pauli)
        random.shuffle(shuffled)
        
        try:
            t = stim.Tableau.from_stabilizers(shuffled)
            c = t.to_circuit("elimination")
            m = get_metrics(c)
            # Optimize: lexicographic (cx, vol)
            if m[0] < best_metrics[0] or (m[0] == best_metrics[0] and m[1] < best_metrics[1]):
                best_metrics = m
                best_c = c
        except Exception:
            continue
            
    return best_c, best_metrics

def main():
    base_circ = stim.Circuit(baseline_str)
    base_cx, base_vol = get_metrics(base_circ)
    print(f"Baseline: CX={base_cx}, Vol={base_vol}")
    
    # 5-qubit code generators
    stabs_code = ["XZZXI", "IXZZX", "XIXZZ", "ZXIXZ"]
    
    # Construct 10-qubit stabilizers for Block 0 (0-4) + Block 1 (5-9)
    # Bell state on logical: X_L0 X_L1, Z_L0 Z_L1
    
    stabs_10 = []
    # Block 0 local (extended to 10)
    for s in stabs_code:
        stabs_10.append(s + "IIIII")
    # Block 1 local (extended to 10)
    for s in stabs_code:
        stabs_10.append("IIIII" + s)
        
    # Global correlations
    # X_L = XXXXX
    # Z_L = ZZZZZ
    stabs_10.append("XXXXXXXXXX") # X_L0 X_L1
    stabs_10.append("ZZZZZZZZZZ") # Z_L0 Z_L1
    
    print("Synthesizing 10-qubit Bell pair...")
    c_bell, m_bell = synthesize_best(stabs_10, attempts=2000)
    print(f"Best 10-qubit Bell: {m_bell}")
    
    full = stim.Circuit()
    
    # Block 0+1
    for instr in c_bell:
        t = [q.value for q in instr.targets_copy()]
        full.append(instr.name, t)
        
    # Block 2+3 (shifted by 10)
    for instr in c_bell:
        t = [q.value + 10 for q in instr.targets_copy()]
        full.append(instr.name, t)
        
    cand_cx, cand_vol = get_metrics(full)
    print(f"Candidate: CX={cand_cx}, Vol={cand_vol}")
    
    with open("candidate.stim", "w") as f:
        f.write(str(full))

if __name__ == "__main__":
    main()
