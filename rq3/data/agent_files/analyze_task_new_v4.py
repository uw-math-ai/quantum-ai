import stim
import sys

def count_cx(circuit):
    count = 0
    for instruction in circuit:
        if instruction.name == "CX" or instruction.name == "CNOT":
            # instruction.targets contains the targets
            # Each pair is a gate application
            count += len(instruction.targets) // 2
    return count

def count_volume(circuit):
    count = 0
    for instruction in circuit:
        if instruction.name in ["CX", "CNOT", "CY", "CZ", "H", "S", "SQRT_X", "SQRT_Y", "SQRT_Z", "X", "Y", "Z", "I"]:
            if instruction.name in ["CX", "CNOT", "CY", "CZ"]:
                count += len(instruction.targets) // 2
            else:
                count += len(instruction.targets)
    return count

def analyze():
    # Load baseline
    try:
        with open("current_task_baseline.stim", "r") as f:
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
        with open("current_task_stabilizers.txt", "r") as f:
            lines = f.readlines()
            # Remove empty lines and whitespace
            lines = [l.strip() for l in lines if l.strip()]
            
        # Create tableau from stabilizers
        # stim.Tableau.from_stabilizers expects a list of stim.PauliString
        stabilizers = []
        for l in lines:
            # The input format is just the string, but we need to verify if it's X/Z/I or has +/i etc.
            # The prompt shows simple X/Z/I strings.
            # However, stim expects PauliStrings.
            stabilizers.append(stim.PauliString(l))
            
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
        
        # Synthesize circuit
        synthesized_circuit = tableau.to_circuit("mpz-mpp")
        
        # Count synthesized metrics
        # The synthesized circuit might contain operations that need decomposition to count as CX/Volume correctly for comparison
        # But let's check what gates it uses.
        print("Synthesized circuit gates:", set(inst.name for inst in synthesized_circuit))
        
        # We likely need to decompose into standard gate set (H, S, CX, etc)
        # stim's to_circuit output is usually fully Clifford gates.
        # But we need to ensure it's comparable.
        
        # Let's try to convert to H, S, CX if possible.
        # Simple synthesis often outputs H, S, CX, M, R.
        
        syn_cx = count_cx(synthesized_circuit)
        syn_vol = count_volume(synthesized_circuit)
        
        print(f"Synthesized CX count: {syn_cx}")
        print(f"Synthesized Volume: {syn_vol}")
        
        # If synthesized is better, we can use it.
        if syn_cx < baseline_cx:
            print("Synthesized circuit is better in CX count!")
            with open("candidate.stim", "w") as f:
                f.write(str(synthesized_circuit))
        elif syn_cx == baseline_cx and syn_vol < baseline_vol:
            print("Synthesized circuit is better in Volume!")
            with open("candidate.stim", "w") as f:
                f.write(str(synthesized_circuit))
        else:
            print("Synthesized circuit is NOT better.")
            
    except Exception as e:
        print(f"Error analyzing stabilizers: {e}")

if __name__ == "__main__":
    analyze()
