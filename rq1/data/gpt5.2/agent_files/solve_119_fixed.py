import stim

def solve():
    try:
        with open("stabilizers_119_fixed.txt", "r") as f:
            lines = [line.strip() for line in f if line.strip()]

        print(f"Loaded {len(lines)} stabilizers")
        
        paulis = []
        for line in lines:
            paulis.append(stim.PauliString(line))
            
        print("Checking commutativity...")
        good_paulis = []
        dropped_count = 0
        
        # Greedy approach: keep if it commutes with all previously kept ones
        for i, p in enumerate(paulis):
            commutes = True
            for gp in good_paulis:
                if not p.commutes(gp):
                    commutes = False
                    # print(f"Stabilizer {i} anticommutes with an earlier kept stabilizer.")
                    break
            if commutes:
                good_paulis.append(p)
            else:
                dropped_count += 1
                
        print(f"Kept {len(good_paulis)} commuting stabilizers. Dropped {dropped_count}.")
        
        # If we dropped any, maybe we should try to discard the *other* one?
        # But for now let's see if this set is good enough.
        
        tableau = stim.Tableau.from_stabilizers(good_paulis, allow_underconstrained=True, allow_redundant=True)
        circuit = tableau.to_circuit("elimination")
        
        with open("circuit_119_fixed.stim", "w") as f:
            f.write(str(circuit))
        print("Circuit generated and saved to circuit_119_fixed.stim")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    solve()
