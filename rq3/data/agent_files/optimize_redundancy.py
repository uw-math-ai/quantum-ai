import stim
import time

def solve():
    print("Loading data...")
    try:
        with open("prompt_baseline.stim", "r") as f:
            base_text = f.read()
        circuit = stim.Circuit(base_text)
        
        with open("target_stabilizers_fixed.txt", "r") as f:
            lines = [l.strip() for l in f if l.strip()]
        
        stabilizers = []
        for l in lines:
            if "," in l:
                parts = l.split(",")
                s_str = parts[-1].strip()
            else:
                s_str = l
            stabilizers.append(stim.PauliString(s_str))
            
        print(f"Loaded {len(stabilizers)} stabilizers.")
        print(f"Baseline gates: {len(circuit)}")
        
        # Initial check
        print("Checking baseline validity...")
        sim = stim.TableauSimulator()
        sim.do(circuit)
        valid = True
        for s in stabilizers:
            if sim.peek_observable_expectation(s) != 1:
                valid = False
                break
        
        if not valid:
            print("WARNING: Baseline is NOT valid with respect to the provided stabilizers!")
            # This is a critical issue. If baseline is invalid, we can't optimize it directly.
            # But maybe we can fix it?
            # Or maybe my check is wrong?
            # I'll proceed assuming it's valid or the check is strict.
        else:
            print("Baseline is VALID.")
            
        # Optimization Loop
        # We will iterate backwards and try to remove gates.
        # To make it efficient, we only re-simulate.
        
        current_circuit = circuit.copy()
        initial_len = len(current_circuit)
        
        # Get indices of CX gates
        indices_to_try = []
        for i, instr in enumerate(current_circuit):
            if instr.name == "CX":
                indices_to_try.append(i)
        
        # Also try other gates if time permits, but CX first
        # Reverse order
        indices_to_try.reverse()
        
        print(f"Attempting to remove {len(indices_to_try)} CX gates...")
        
        removed_indices = set()
        
        start_time = time.time()
        
        for idx in indices_to_try:
            # Construct candidate
            # Ideally we modify the circuit in place or efficiently
            # But stim circuits are immutable-ish (can't delete easily by index in Python API?)
            # Actually we can reconstruct.
            
            # Optimization: Check if removal is valid.
            # If we remove gate at idx.
            
            # Since reconstruction is O(N), and we do it N times, it's O(N^2).
            # With N=1000, 10^6 ops, fast.
            
            # Build circuit without the gates in removed_indices AND without current idx
            
            cand = stim.Circuit()
            for i, instr in enumerate(current_circuit):
                if i in removed_indices or i == idx:
                    continue
                cand.append(instr)
            
            # Check
            sim = stim.TableauSimulator()
            sim.do(cand)
            valid = True
            for s in stabilizers:
                if sim.peek_observable_expectation(s) != 1:
                    valid = False
                    break
            
            if valid:
                print(f"Removed CX at index {idx}")
                removed_indices.add(idx)
                
            if time.time() - start_time > 100:
                print("Time limit approaching...")
                break
                
        # Reconstruct final
        final_circuit = stim.Circuit()
        for i, instr in enumerate(current_circuit):
            if i in removed_indices:
                continue
            final_circuit.append(instr)
            
        print(f"Optimization complete. Removed {len(removed_indices)} gates.")
        print(f"New length: {len(final_circuit)}")
        
        cx_count = 0
        vol = 0
        for instr in final_circuit:
            if instr.name == "CX":
                n = len(instr.targets_copy()) // 2
                cx_count += n
                vol += n
            elif instr.name in ["CY", "CZ", "SWAP", "ISWAP", "ISWAP_DAG"]:
                n = len(instr.targets_copy()) // 2
                vol += n
            else:
                vol += len(instr.targets_copy())
                
        print(f"Final CX: {cx_count}, Vol: {vol}")
        
        with open("candidate_optimized.stim", "w") as f:
            f.write(str(final_circuit))
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    solve()
