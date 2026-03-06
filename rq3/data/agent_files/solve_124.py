import stim
import sys

# Target stabilizers
stabilizers = [
    "IIXIIXIIXXIIIIIIIII", "IIIIIIIIIIXIXIIIIXX", "IIIIIIIIIIXXIXIIIIX", "XXIIIIIIIIIIIIXXIII", "XXIXXIXIIIIIIIIIXII", "IIXIXIIIXIIIIIIIXII", "IXIIIIXXIIIIIIIXIII", "IIIXIIXXIIXXXIIIIII", "IIIXXIIIXXIXIXIIIII", "IIZIIZIIZZIIIIIIIII", "IIIIIIIIIIZIZIIIIZZ", "IIIIIIIIIIZZIZIIIIZ", "ZZIIIIIIIIIIIIZZIII", "ZZIZZIZIIIIIIIIIZII", "IIZIZIIIZIIIIIIIZII", "IZIIIIZZIIIIIIIZIII", "IIIZIIZZIIZZZIIIIII", "IIIZZIIIZZIZIZIIIII"
]

# Baseline circuit
with open("baseline.stim", "r") as f:
    baseline_text = f.read()

baseline_circuit = stim.Circuit(baseline_text)

def count_metrics(circuit):
    cx = 0
    vol = 0
    for instr in circuit:
         if instr.name in ["CX", "CNOT", "CY", "CZ", "SWAP", "ISWAP", "CXSWAP", "SWAPCX", "SQRT_XX", "SQRT_YY", "SQRT_ZZ"]:
             n = len(instr.targets_copy())
             cx += n // 2
             vol += n // 2 # 1 gate per pair for volume
         elif instr.name in ["H", "S", "S_DAG", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "SQRT_Z", "SQRT_Z_DAG", "X", "Y", "Z", "I"]:
             n = len(instr.targets_copy())
             vol += n
    return cx, vol

baseline_cx, baseline_vol = count_metrics(baseline_circuit)

print(f"Baseline CX: {baseline_cx}")
print(f"Baseline Volume: {baseline_vol}")

# Synthesize circuit
try:
    # Convert string stabilizers to PauliStrings
    pauli_stabilizers = [stim.PauliString(s) for s in stabilizers]
    
    # Create tableau (map Z basis to these stabilizers)
    # Note: from_stabilizers might need allow_underconstrained=True
    tableau = stim.Tableau.from_stabilizers(pauli_stabilizers, allow_underconstrained=True)
    
    # Try different synthesis methods
    methods = ["elimination", "graph_state"] 
    
    best_circuit = None
    best_cx = float("inf")
    best_vol = float("inf")
    
    for method in methods:
        try:
            print(f"Trying synthesis method: {method}")
            # Synthesize T. T |0> is stabilized by S_k.
            synthesized = tableau.to_circuit(method=method)
            
            cx, vol = count_metrics(synthesized)
            
            print(f"Method {method}: CX={cx}, Vol={vol}")
            
            if cx < best_cx or (cx == best_cx and vol < best_vol):
                best_cx = cx
                best_vol = vol
                best_circuit = synthesized
                
        except Exception as e:
            print(f"Method {method} failed: {e}")

    if best_circuit:
        print(f"Best Synthesized: CX={best_cx}, Vol={best_vol}")
        if best_cx < baseline_cx or (best_cx == baseline_cx and best_vol < baseline_vol):
             print("Found improvement!")
             with open("synthesized.stim", "w") as f:
                 f.write(str(best_circuit))
        else:
             print("No improvement found via synthesis.")
    
except Exception as e:
    print(f"Error synthesizing: {e}")

