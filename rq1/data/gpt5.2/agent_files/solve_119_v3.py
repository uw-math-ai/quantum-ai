import stim

def solve():
    print("Reading stabilizers from file stabilizers_119.txt...")
    with open("stabilizers_119_fixed_v2.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]
    
    ps = [stim.PauliString(l) for l in lines]
    print(f"Loaded {len(ps)} stabilizers from file.")
    
    try:
        # Generate circuit using elimination
        t = stim.Tableau.from_stabilizers(ps, allow_redundant=True, allow_underconstrained=True)
        circuit = t.to_circuit(method="elimination")
        
        with open("circuit_119_v3.stim", "w") as f:
            f.write(str(circuit))
            
        print("Successfully generated circuit_119_v3.stim")
        
    except Exception as e:
        print(f"Failed to generate circuit: {e}")

if __name__ == "__main__":
    solve()
