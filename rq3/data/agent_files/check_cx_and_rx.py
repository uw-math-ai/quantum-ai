import stim

def check_metrics(filename):
    with open(filename, "r") as f:
        text = f.read()
    circuit = stim.Circuit(text)
    
    cx_count = 0
    rx_count = 0
    volume = 0
    
    for instr in circuit:
        targets = instr.targets_copy()
        n = len(targets)
        name = instr.name
        
        if name in ["QUBIT_COORDS", "TICK", "SHIFT_COORDS"]:
            continue
            
        if name == "CX" or name == "CNOT":
            count = n // 2
            cx_count += count
            volume += count
        elif name == "CZ":
            count = n // 2
            # CZ does not contribute to cx_count (usually)
            # But prompt says "cand.cx_count – number of CX (CNOT) gates".
            # So CZ is 0 CX.
            volume += count
        elif name == "RX":
            rx_count += n
            volume += n
        else:
            # Single qubit gates
            volume += n
            
    return cx_count, rx_count, volume

base_cx, base_rx, base_vol = check_metrics("baseline.stim")
cand_cx, cand_rx, cand_vol = check_metrics("candidate_elim.stim")

print(f"Baseline: CX={base_cx}, Vol={base_vol}")
print(f"Candidate: CX={cand_cx}, Vol={cand_vol}")
print(f"Strictly better? {(cand_cx < base_cx) or (cand_cx == base_cx and cand_vol < base_vol)}")
