import stim
import sys

stabilizers = [
    "IXIIXIIXXXXXIIIIIIIIIIX", # 0
    "XIIXIIXXXXXIIIIIIIIIIXI", # 1
    "IXXIXXXIIIXXIIIIIIIIXII", # 2
    "XXIXXXIIIXXIIIIIIIIXIII", # 3
    "XXXXIIIXIIXXIIIIIIXIIII", # 4 (CORRECTED based on tool output and length analysis)
    "XIXIXIXXXIIXIIIIIXIIIII", # 5
    "IIIXXXXIXXIXIIIIXIIIIII", # 6
    "IIXXXXIXXIXIIIIXIIIIIII", # 7
    "IXXXXIXXIXIIIIXIIIIIIII", # 8
    "XXXXIXXIXIIIIXIIIIIIIII", # 9
    "XIXIIXIIXXXXXIIIIIIIIII", # 10
    "IZIIZIIZZZZZIIIIIIIIIIZ", # 11
    "ZIIZIIZZZZZIIIIIIIIIIZI", # 12
    "IZZIZZZIIIZZIIIIIIIIZII", # 13
    "ZZIZZZIIIZZIIIIIIIIZIII", # 14
    "ZZZZIIIZIIZZIIIIIIZIIII", # 15
    "ZIZIZIZZZIIZIIIIIZIIIII", # 16
    "IIIZZZZIZZIZIIIIZIIIIII", # 17
    "IIZZZZIZZIZIIIIZIIIIIII", # 18
    "IZZZZIZZIZIIIIZIIIIIIII", # 19
    "ZZZZIZZIZIIIIZIIIIIIIII", # 20
    "ZIZIIZIIZZZZZIIIIIIIIII"  # 21
]

def solve():
    print(f"Number of stabilizers: {len(stabilizers)}")
    
    # Verify commutativity
    def commute(s1, s2):
        anti = 0
        for c1, c2 in zip(s1, s2):
            if c1 != 'I' and c2 != 'I' and c1 != c2:
                anti += 1
        return anti % 2 == 0

    print("Checking commutativity...")
    bad_pairs = []
    for i in range(len(stabilizers)):
        for j in range(i + 1, len(stabilizers)):
            if not commute(stabilizers[i], stabilizers[j]):
                print(f"Warning: {i} and {j} anti-commute!")
                bad_pairs.append((i, j))
    
    if bad_pairs:
        print(f"Found {len(bad_pairs)} anti-commuting pairs. Still failing?")
        # return
    else:
        print("All stabilizers commute!")

    try:
        t = stim.Tableau.from_stabilizers(
            [stim.PauliString(s) for s in stabilizers],
            allow_underconstrained=True
        )
        print("Tableau created successfully.")
        
        circ = t.to_circuit(method="graph_state")
        print("Circuit generated.")
        
        sim = stim.TableauSimulator()
        sim.do(circ)
        
        preserved_count = 0
        for i, s in enumerate(stabilizers):
            p = stim.PauliString(s)
            res = sim.peek_observable_expectation(p)
            if res == 1:
                preserved_count += 1
            else:
                print(f"Stabilizer {i} not preserved (Expectation: {res})")
        
        print(f"Preserved {preserved_count}/{len(stabilizers)} stabilizers.")
        
        # Save to file
        with open("circuit_corrected.stim", "w") as f:
            f.write(str(circ))
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    solve()
