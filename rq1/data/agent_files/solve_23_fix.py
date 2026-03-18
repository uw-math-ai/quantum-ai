import stim
import sys

stabilizers = [
    "IXIIXIIXXXXXIIIIIIIIIIX", # 0
    "XIIXIIXXXXXIIIIIIIIIIXI", # 1
    "IXXIXXXIIIXXIIIIIIIIXII", # 2
    "XXIXXXIIIXXIIIIIIIIXIII", # 3
    # "XXXXIIXIIXXIIIIIIXIIII", # 4 (REMOVED due to anticommutation)
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
        
        # Check all original stabilizers (including 4)
        original_stabilizers = [
            "IXIIXIIXXXXXIIIIIIIIIIX",
            "XIIXIIXXXXXIIIIIIIIIIXI",
            "IXXIXXXIIIXXIIIIIIIIXII",
            "XXIXXXIIIXXIIIIIIIIXIII",
            "XXXXIIXIIXXIIIIIIXIIII",
            "XIXIXIXXXIIXIIIIIXIIIII",
            "IIIXXXXIXXIXIIIIXIIIIII",
            "IIXXXXIXXIXIIIIXIIIIIII",
            "IXXXXIXXIXIIIIXIIIIIIII",
            "XXXXIXXIXIIIIXIIIIIIIII",
            "XIXIIXIIXXXXXIIIIIIIIII",
            "IZIIZIIZZZZZIIIIIIIIIIZ",
            "ZIIZIIZZZZZIIIIIIIIIIZI",
            "IZZIZZZIIIZZIIIIIIIIZII",
            "ZZIZZZIIIZZIIIIIIIIZIII",
            "ZZZZIIIZIIZZIIIIIIZIIII",
            "ZIZIZIZZZIIZIIIIIZIIIII",
            "IIIZZZZIZZIZIIIIZIIIIII",
            "IIZZZZIZZIZIIIIZIIIIIII",
            "IZZZZIZZIZIIIIZIIIIIIII",
            "ZZZZIZZIZIIIIZIIIIIIIII",
            "ZIZIIZIIZZZZZIIIIIIIIII"
        ]
        
        preserved_count = 0
        for i, s in enumerate(original_stabilizers):
            p = stim.PauliString(s)
            res = sim.peek_observable_expectation(p)
            if res == 1:
                preserved_count += 1
            else:
                print(f"Stabilizer {i} not preserved (Expectation: {res})")
        
        print(f"Preserved {preserved_count}/{len(original_stabilizers)} stabilizers.")
        
        # Output circuit to a file
        with open("circuit_fix.stim", "w") as f:
            f.write(str(circ))
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    solve()
