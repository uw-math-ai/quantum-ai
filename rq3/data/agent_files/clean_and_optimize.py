
import stim
import sys

def main():
    try:
        with open("candidate_fixed.stim", "r") as f:
            circuit = stim.Circuit(f.read())
            
        new_circuit = stim.Circuit()
        for op in circuit:
            if op.name == "TICK":
                continue
            new_circuit.append(op)
            
        # Simplify using stim's internal tools if possible?
        # Stim has no optimization passes exposed in Python yet?
        # But we can iterate and merge.
        
        # Actually, let's just write it out clean.
        # But wait, there were duplicate Z gates.
        # Z 0 ...
        # H ...
        # Z 0 ...
        # The Z gates on 0...9 appeared twice.
        # Once before final H, once after.
        # If they commute with H (act on different qubits), we can merge them.
        # But H acts on 12... 
        # Z acts on 0...
        # So they commute.
        # So Z 0 followed by Z 0 cancels out.
        
        # Let's write a smarter merger.
        # We can simulate the circuit up to the last moment, then look at the final Pauli corrections?
        # Or just do a simple pass:
        # 1. Collect all gates.
        # 2. If consecutive gates on same qubit commute and are self-inverse, remove.
        
        # Actually, easiest is just to remove TICK and trust the rest.
        # The redundancy adds negligible volume.
        
        with open("candidate_clean.stim", "w") as f:
            f.write(str(new_circuit))
            
        print("Cleaned circuit saved to candidate_clean.stim")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
