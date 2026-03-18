import stim
import sys

# Load stabilizers from baseline circuit to be safe
with open("current_baseline.stim", "r") as f:
    baseline_text = f.read()
    
print("Loading baseline...")
baseline = stim.Circuit(baseline_text)
tableau = stim.Tableau.from_circuit(baseline)
print(f"Extracted tableau with {len(tableau)} stabilizers")

try:
    # Synthesize
    # tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers], allow_redundant=True, allow_underconstrained=True)
    circuit = tableau.to_circuit(method='graph_state')
    
    # Clean RX/R
    cleaned = stim.Circuit()
    for op in circuit:
        if op.name == "RX":
            cleaned.append("H", op.targets_copy())
        elif op.name in ["R", "RZ"]:
            pass # Identity
        else:
            cleaned.append(op)
            
    # Format (split to avoid long lines and merging)
    formatted = stim.Circuit()
    for op in cleaned:
        name = op.name
        targets = op.targets_copy()
        
        if name in ["CZ", "CX", "CY", "XC", "YC", "ZC", "XX", "YY", "ZZ", "SWAP"]:
            # 2 qubit gates: split into individual gates
            for i in range(0, len(targets), 2):
                formatted.append(name, targets[i:i+2])
                formatted.append("TICK") # Prevent merging
        elif name in ["H", "S", "S_DAG", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "SQRT_Z", "SQRT_Z_DAG", "X", "Y", "Z", "I"]:
            # 1 qubit gates: split into individual gates (chunk size 1)
            for t in targets:
                formatted.append(name, [t])
                formatted.append("TICK") # Prevent merging
        elif name == "TICK":
            formatted.append("TICK")
        else:
            formatted.append(op)
            formatted.append("TICK")
            
    # Print stats
    cx = sum(1 for op in formatted if op.name == "CX")
    cz = sum(1 for op in formatted if op.name == "CZ")
    print(f"Stats: CX={cx}, CZ={cz}")
    
    # Save
    with open("candidate_final.stim", "w") as f:
        f.write(str(formatted))
        
    print("---CIRCUIT START---")
    print(formatted)
    print("---CIRCUIT END---")

except Exception as e:
    print(f"Error: {e}")
