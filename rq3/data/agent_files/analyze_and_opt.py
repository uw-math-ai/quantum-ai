import stim
import sys

def count_cx(circuit):
    count = 0
    for instruction in circuit:
        if instruction.name == "CX" or instruction.name == "CNOT":
            count += len(instruction.targets_copy()) // 2
    return count

def count_volume(circuit):
    # Volume is total gate count (approx)
    count = 0
    for instruction in circuit:
        if instruction.name in ["CX", "CNOT", "CY", "CZ", "H", "S", "SQRT_X", "X", "Y", "Z", "I"]:
            if instruction.name in ["CX", "CNOT", "CY", "CZ"]:
                 count += len(instruction.targets_copy()) # 2 per gate
            else:
                 count += len(instruction.targets_copy()) # 1 per gate
    return count

def check_stabilizers(circuit, stabilizers):
    # This is a heuristic check using Tableau simulation
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    preserved = 0
    for stab in stabilizers:
        p = stim.PauliString(stab)
        # We need to check if the stabilizer expectation is +1
        # peek_observable_expectation returns +1 or -1 (or 0 if random)
        # But wait, peek_observable_expectation checks if the current state is an eigenstate of the observable.
        # If the state is stabilized by P, expectation is +1.
        try:
            exp = sim.peek_observable_expectation(p)
            if exp == 1:
                preserved += 1
        except:
            pass
    return preserved

def main():
    try:
        baseline_path = "C:\\Users\\anpaz\\Repos\\quantum-ai\\rq3\\data\\agent_files\\baseline.stim"
        with open(baseline_path, "r") as f:
            baseline_text = f.read()
        baseline = stim.Circuit(baseline_text)
        
        print(f"Baseline CX count: {count_cx(baseline)}")
        print(f"Baseline Volume: {count_volume(baseline)}")
        print(f"Baseline Depth: {len(baseline)}") # Rough depth
        
        # Parse stabilizers
        stabilizers = []
        with open("C:\\Users\\anpaz\\Repos\\quantum-ai\\rq3\\data\\agent_files\\current_task_stabilizers.txt", "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    stabilizers.append(line)
        
        print(f"Loaded {len(stabilizers)} stabilizers")
        
        # Check baseline preservation
        preserved = check_stabilizers(baseline, stabilizers)
        print(f"Baseline preserved stabilizers: {preserved}/{len(stabilizers)}")
        
        # Method 1: Resynthesis using stim.Tableau.from_stabilizers
        print("\nAttempting Resynthesis (Method 1)...")
        try:
            # stim.Tableau.from_stabilizers creates a tableau T such that T|0> is stabilized by stabilizers.
            # However, from_stabilizers requires independent stabilizers and N stabilizers for N qubits if we want a pure state.
            # If we have 62 stabilizers for 63 qubits, it's underconstrained (1 logical qubit).
            # allow_underconstrained=True
            
            # PauliString objects
            ps_stabs = [stim.PauliString(s) for s in stabilizers]
            
            tableau = stim.Tableau.from_stabilizers(ps_stabs, allow_underconstrained=True)
            resynth_circuit = tableau.to_circuit(method="elimination")
            
            cx = count_cx(resynth_circuit)
            vol = count_volume(resynth_circuit)
            print(f"Resynthesized CX count: {cx}")
            print(f"Resynthesized Volume: {vol}")
            
            pres = check_stabilizers(resynth_circuit, stabilizers)
            print(f"Resynthesized preserved: {pres}/{len(stabilizers)}")
            
            if pres == len(stabilizers):
                print("Resynthesis VALID.")
                res_str = str(resynth_circuit)
                print(f"Resynth string length: {len(res_str)}")
                print(f"Resynth string preview: {res_str[:200]}")
                with open("C:\\Users\\anpaz\\Repos\\quantum-ai\\rq3\\data\\agent_files\\candidate.stim", "w") as f:
                    f.write(res_str)
            else:
                print("Resynthesis INVALID.")
                
        except Exception as e:
            print(f"Resynthesis failed: {e}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
