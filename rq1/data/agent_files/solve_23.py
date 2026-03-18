import stim
import sys

stabilizers = [
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

def solve():
    print(f"Number of stabilizers: {len(stabilizers)}")
        # Try to check commutativity first
    try:
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
            print(f"Found {len(bad_pairs)} anti-commuting pairs.")
            
        t = stim.Tableau.from_stabilizers(
            [stim.PauliString(s) for s in stabilizers],
            allow_underconstrained=True
        )
            [stim.PauliString(s) for s in stabilizers],
            allow_underconstrained=True
        )
        print("Tableau created successfully.")
        
        # Convert to circuit
        # method="graph_state" uses CZs and is generally efficient for stabilizer states
        # It also handles the mapping from |0> to the stabilizer state
        circ = t.to_circuit(method="graph_state")
        
        print("Circuit generated.")
        
        # We can check if it works by simulating
        sim = stim.TableauSimulator()
        sim.do(circ)
        
        # Check stabilizers
        all_good = True
        for i, s in enumerate(stabilizers):
            p = stim.PauliString(s)
            res = sim.peek_observable_expectation(p)
            if res != 1:
                print(f"Stabilizer {i} {s} not preserved! Expectation: {res}")
                all_good = False
        
        if all_good:
            print("All stabilizers preserved by the generated circuit.")
            print("CIRCUIT_START")
            print(circ)
            print("CIRCUIT_END")
        else:
            print("Failed to preserve all stabilizers.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    solve()
