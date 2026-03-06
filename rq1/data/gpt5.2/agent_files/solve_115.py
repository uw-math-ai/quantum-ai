import stim
import sys
import os

def solve():
    print("Starting solver...")
    try:
        stab_path = r'data\gemini-3-pro-preview\agent_files\stabilizers.txt'
        if not os.path.exists(stab_path):
             print(f"File not found: {stab_path}")
             return

        with open(stab_path, 'r') as f:
            lines = [l.strip() for l in f if l.strip()]

        stabilizers = []
        for line in lines:
            # Clean up line
            clean_line = line.replace(',', '').replace("'", "").strip()
            if clean_line:
                stabilizers.append(clean_line)
        
        print(f"Loaded {len(stabilizers)} stabilizers.")
        
        # Create tableau
        try:
            # Convert to PauliString
            pauli_stabilizers = [stim.PauliString(s) for s in stabilizers]
            
            # Try with allow_underconstrained=True
            tableau = stim.Tableau.from_stabilizers(pauli_stabilizers, allow_underconstrained=True)
            circuit = tableau.to_circuit()
            print("Successfully created circuit from stabilizers.")
            
            out_path = r'data\gemini-3-pro-preview\agent_files\circuit_115.stim'
            with open(out_path, 'w') as f:
                f.write(str(circuit))
            print(f"Circuit written to {out_path}")
                
        except Exception as e:
            print(f"Error creating tableau: {e}")
            
    except Exception as e:
        print(f"General error: {e}")

if __name__ == "__main__":
    solve()
