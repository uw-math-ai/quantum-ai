import stim
import sys

def count_cx(circuit):
    count = 0
    for instruction in circuit:
        if instruction.name == "CX" or instruction.name == "CNOT":
            targets = instruction.targets_copy()
            count += len(targets) // 2
    return count

def count_volume(circuit):
    count = 0
    for instruction in circuit:
        if instruction.name in ["CX", "CNOT", "CY", "CZ", "H", "S", "SQRT_X", "SQRT_Y", "SQRT_Z", "X", "Y", "Z", "I"]:
            targets = instruction.targets_copy()
            if instruction.name in ["CX", "CNOT", "CY", "CZ"]:
                count += len(targets) // 2
            else:
                count += len(targets)
    return count

def count_effective_cx(circuit):
    count = 0
    for instruction in circuit:
        if instruction.name in ["CX", "CNOT", "CY", "CZ"]:
            targets = instruction.targets_copy()
            count += len(targets) // 2
    return count

def analyze():
    # Load baseline
    try:
        with open("my_baseline_776.stim", "r") as f:
            baseline_text = f.read()
            baseline = stim.Circuit(baseline_text)
    except Exception as e:
        print(f"Error loading baseline: {e}")
        return

    baseline_cx = count_cx(baseline)
    baseline_vol = count_volume(baseline)
    print(f"Baseline CX count: {baseline_cx}")
    print(f"Baseline Volume: {baseline_vol}")

    # Load stabilizers
    try:
        with open("my_stabilizers_776.txt", "r") as f:
            lines = f.readlines()
            lines = [l.strip() for l in lines if l.strip()]
            
        stabilizers = []
        for l in lines:
            stabilizers.append(stim.PauliString(l))
            
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
        
        # Try elimination
        print("--- Elimination Method ---")
        try:
            synthesized_circuit_elim = tableau.to_circuit("elimination")
            syn_cx_elim = count_cx(synthesized_circuit_elim)
            syn_vol_elim = count_volume(synthesized_circuit_elim)
            print(f"Synthesized (elimination) CX count: {syn_cx_elim}")
            print(f"Synthesized (elimination) Volume: {syn_vol_elim}")
            
            with open("candidate_elimination.stim", "w") as f:
                f.write(str(synthesized_circuit_elim))
                
        except Exception as e:
            print(f"Elimination synthesis failed: {e}")

        # Try graph state
        print("--- Graph State Method ---")
        try:
            synthesized_circuit_graph = tableau.to_circuit("graph_state")
            syn_cx_graph = count_cx(synthesized_circuit_graph)
            syn_eff_cx_graph = count_effective_cx(synthesized_circuit_graph)
            syn_vol_graph = count_volume(synthesized_circuit_graph)
            
            print(f"Synthesized (graph_state) ACTUAL CX count: {syn_cx_graph}")
            print(f"Synthesized (graph_state) EFFECTIVE CX count (CX+CY+CZ): {syn_eff_cx_graph}")
            print(f"Synthesized (graph_state) Volume: {syn_vol_graph}")
            
            with open("candidate_graph.stim", "w") as f:
                f.write(str(synthesized_circuit_graph))
                
            # If we want to submit this, we should convert CZ to CX+H to match "cx_count" metric properly if needed
            # But let's see the numbers first.
            
        except Exception as e:
            print(f"Graph state synthesis failed: {e}")

    except Exception as e:
        print(f"Error analyzing stabilizers: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze()
