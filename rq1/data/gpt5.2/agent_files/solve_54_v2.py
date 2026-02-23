import stim
import sys

def solve():
    print("Reading stabilizers from stabilizers_54_v2.txt")
    with open("stabilizers_54_v2.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]

    print(f"Loaded {len(lines)} stabilizers.")
    
    try:
        stabilizers = [stim.PauliString(s) for s in lines]
        # Check commutativity
        print("Checking commutativity...")
        for i in range(len(stabilizers)):
            for j in range(i+1, len(stabilizers)):
                if not stabilizers[i].commutes(stabilizers[j]):
                    print(f"WARNING: Stabilizers {i} and {j} do not commute!")
                    # We continue anyway to see if stim can handle it (it won't)
        
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
        circuit = tableau.to_circuit("elimination")
        
        with open("circuit_54_v2.stim", "w") as f:
            f.write(str(circuit))
            
        print("Circuit generated successfully in circuit_54_v2.stim")
        
    except Exception as e:
        print(f"Error generating circuit: {e}")

if __name__ == "__main__":
    solve()
