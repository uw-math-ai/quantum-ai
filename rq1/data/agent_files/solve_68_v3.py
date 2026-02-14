import stim
import json

def solve():
    with open("stabilizers_68.txt", 'r') as f:
        lines = [l.strip() for l in f if l.strip()]
    
    stabilizers = [stim.PauliString(l) for l in lines]
    
    print("Synthesizing circuit with stim (allow_underconstrained=True)...")
    try:
        t = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
        circuit = t.to_circuit()
        
        # Write to file
        with open("circuit_68.stim", "w") as f:
            f.write(str(circuit))
        print("Circuit written to circuit_68.stim")
            
    except Exception as e:
        print(f"Error during synthesis: {e}")

if __name__ == "__main__":
    solve()
