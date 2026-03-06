import stim

def analyze():
    # Load target stabilizers
    try:
        stabilizers = []
        with open("task_v1_stabilizers.txt", "r") as f:
            for line in f:
                clean_line = line.strip().replace(',', '').replace('\n', '').replace('\r', '')
                if clean_line:
                    stabilizers.append(clean_line)
        
        print(f"Number of stabilizers: {len(stabilizers)}")
        if stabilizers:
            print(f"First stabilizer (repr): {repr(stabilizers[0])}")
            print(f"Stabilizer length: {len(stabilizers[0])}")
            
        # Debug specific pair
        if len(stabilizers) > 113:
            s15 = stabilizers[15]
            s113 = stabilizers[113]
            print(f"S15:  {s15}")
            print(f"S113: {s113}")
            
            anticommutes = 0
            for i in range(min(len(s15), len(s113))):
                p1 = s15[i]
                p2 = s113[i]
                if p1 != 'I' and p2 != 'I' and p1 != p2:
                    anticommutes += 1
                    # print(f"Index {i}: {p1} vs {p2}")
            print(f"Anticommutes count: {anticommutes}")
            
        paulis = [stim.PauliString(s) for s in stabilizers]
        print("Converted to PauliStrings")
        t = stim.Tableau.from_stabilizers(paulis, allow_redundant=True, allow_underconstrained=True)
        print("Stabilizers are consistent.")
        print(f"Tableau size: {len(t)}")
        
        # Try to synthesize a circuit from the tableau
        synthesized_circuit = t.to_circuit(method="elimination")
        
        syn_cx = 0
        for op in synthesized_circuit.flattened():
             if op.name in ["CX", "CNOT"]:
                 syn_cx += len(op.targets_copy()) // 2
                 
        syn_vol = sum(len(op.targets_copy()) for op in synthesized_circuit.flattened())
        print(f"Synthesized (elimination) CX count: {syn_cx}")
        print(f"Synthesized (elimination) Volume: {syn_vol}")
        
        with open("candidate_synthesis.stim", "w") as f:
            f.write(str(synthesized_circuit))

    except Exception as e:
        print(f"Error processing stabilizers: {e}")
    
    # Analyze the baseline circuit
    try:
        circuit = stim.Circuit.from_file("task_v1_baseline.stim")
        print(f"Baseline circuit instruction count: {len(circuit)}")
        
        cx_count = 0
        for op in circuit.flattened():
             if op.name in ["CX", "CNOT"]:
                 cx_count += len(op.targets_copy()) // 2
        print(f"Baseline CX count: {cx_count}")
        
        # Approximate volume
        volume = sum(len(op.targets_copy()) for op in circuit.flattened())
        print(f"Baseline volume: {volume}")

        # Check preservation
        print("Checking baseline preservation...")
        sim = stim.TableauSimulator()
        sim.do(circuit)
        
        preserved = 0
        failed_indices = []
        for i, s in enumerate(stabilizers):
            p = stim.PauliString(s)
            if sim.peek_observable_expectation(p) == 1:
                preserved += 1
            else:
                failed_indices.append(i)
        
        print(f"Baseline preserves {preserved}/{len(stabilizers)} stabilizers.")
        if failed_indices:
            print(f"Failed indices: {failed_indices[:5]}...")
            
    except Exception as e:
        print(f"Error parsing/simulating baseline circuit: {e}")

if __name__ == "__main__":
    analyze()
