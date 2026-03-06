import stim
import sys
import os

def count_cx(circuit):
    return circuit.num_gates("CX") + circuit.num_gates("CNOT")

def count_volume(circuit):
    # Volume includes all unitary gates.
    # We can iterate over instructions and check if they are gates.
    # For now, let's just count all operations except annotations (DETECTOR, OBSERVABLE_INCLUDE, QUOTED_STRING_ARGS, etc.)
    # Actually, the prompt says: "total gate count in the volume gate set (CX, CY, CZ, H, S, SQRT_X, etc.)"
    # This implies 1-qubit and 2-qubit gates.
    # We'll approximate by counting all operations that are not noise or annotations.
    count = 0
    for instruction in circuit:
        if instruction.name not in ["DETECTOR", "OBSERVABLE_INCLUDE", "TICK", "SHIFT_COORDS", "QUOTED_STRING_ARGS", "MPP", "M", "R", "MR"]:
             # Assuming standard gates.
             # Note: M, R, MR are measurements/resets. If they exist, they might count to volume or not?
             # Prompt says "volume gate set". Usually excludes measurements.
             # Baseline has no measurements.
             count += len(instruction.targets_copy()) // (2 if instruction.name in ["CX", "CNOT", "CZ", "CY", "SWAP", "ISWAP"] else 1)
             # Wait, num_gates("CX") returns number of operations? Or number of gates decomposed?
             # circuit.num_gates("CX") returns number of CX instructions if they are not fused?
             # Actually, iterate instructions is safer.
             pass
    
    # Better way:
    return sum(1 for _ in circuit.flattened())

def get_metrics(circuit):
    # Precise metric calculation
    cx = 0
    vol = 0
    depth = 0 # Not easy to calculate precisely without a DAG, but we can approximate or use stim's internal tools if available?
    # Stim doesn't have built-in depth calc exposed easily.
    # We will ignore depth for now as it's tertiary.
    
    for instr in circuit:
        name = instr.name
        if name in ["CX", "CNOT"]:
            n = len(instr.targets_copy()) // 2
            cx += n
            vol += n
        elif name in ["CY", "CZ", "SWAP", "ISWAP"]:
             n = len(instr.targets_copy()) // 2
             vol += n
        elif name in ["H", "S", "S_DAG", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "SQRT_Z", "SQRT_Z_DAG", "X", "Y", "Z", "I"]:
            n = len(instr.targets_copy())
            vol += n
        # complex gates like MPP? Assuming not present in this pure stabilizer task.
        
    return cx, vol

def solve():
    print("Loading files...")
    with open("current_task_stabilizers.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]
    
    with open("current_task_baseline.stim", "r") as f:
        baseline_text = f.read()
        baseline = stim.Circuit(baseline_text)
    
    base_cx, base_vol = get_metrics(baseline)
    print(f"Baseline: CX={base_cx}, Vol={base_vol}")
    
    print(f"Loaded {len(stabilizers)} stabilizers.")
    print(f"First stabilizer: {stabilizers[0]}")
    
    # Method 1: Direct Synthesis from Stabilizers
    print("Attempting Method 1: Tableau Synthesis...")
    try:
        # Check supported arguments or just try with likely ones based on error message
        # Error said: (stabilizers: object, *, allow_redundant: bool = False, allow_underconstrained: bool = False)
        # Try converting to PauliString objects to be safe
        pauli_stabilizers = [stim.PauliString(s) for s in stabilizers]
        tableau = stim.Tableau.from_stabilizers(pauli_stabilizers, allow_redundant=True, allow_underconstrained=True)
        # Synthesize
        synth_circuit = tableau.to_circuit(method="elimination")
        
        synth_cx, synth_vol = get_metrics(synth_circuit)
        print(f"Method 1 (elimination): CX={synth_cx}, Vol={synth_vol}")
        
        if (synth_cx < base_cx) or (synth_cx == base_cx and synth_vol < base_vol):
            print("Method 1 is strictly better!")
            with open("candidate.stim", "w") as f:
                f.write(str(synth_circuit))
            return
        
        # Try method="graph_state" if available (older stim versions might not have it, or it's called differently)
        # Actually stim doesn't have method="graph_state" in to_circuit directly usually.
        # But we can try to find a graph state.
        
    except Exception as e:
        print(f"Method 1 failed: {e}")

    # Method 2: Graph State Synthesis (manual via graph state logic if possible)
    # Since I don't have a library for that handy, I'll rely on Stim's other methods if any.
    
    # Method 3: Optimization passes on Baseline
    # Maybe the baseline is already good but has redundancy?
    # I can try to run a simple optimizer if I had one.
    
    # Let's save the elimination one anyway if it's the only one we have, but we need strictly better.
    # If not better, we might need to rely on the "graph state" approach which usually produces low CX count.
    
    # Let's try to do a graph state synthesis using `stim.Tableau.to_circuit("graph_state")`?
    # Check if that exists.
    try:
        synth_circuit_graph = tableau.to_circuit(method="graph_state")
        gx, gv = get_metrics(synth_circuit_graph)
        print(f"Method 2 (graph_state): CX={gx}, Vol={gv}")
        
        if (gx < base_cx) or (gx == base_cx and gv < base_vol):
             print("Method 2 is strictly better!")
             with open("candidate.stim", "w") as f:
                 f.write(str(synth_circuit_graph))
             return
    except Exception as e:
        print(f"Method 2 failed or not supported: {e}")

    print("No strict improvement found with standard synthesis.")
    # If standard synthesis failed to beat baseline, we need to be creative.
    # Maybe the baseline IS a graph state circuit?
    
if __name__ == "__main__":
    solve()
