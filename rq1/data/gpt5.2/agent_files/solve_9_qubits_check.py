import stim

stabilizers = [
    "XXIXXIIII",
    "IIIIXXIXX",
    "IIXIIXIII",
    "IIIXIIXII",
    "IIIZZIZZI",
    "IZZIZZIII",
    "ZZIIIIIII",
    "IIIIIIIZZ"
]

print(f"Checking {len(stabilizers)} stabilizers...")

def check_commutation(stabs_str):
    stabs = [stim.PauliString(s) for s in stabs_str]
    n = len(stabs)
    all_commute = True
    for i in range(n):
        for j in range(i + 1, n):
            if not stabs[i].commutes(stabs[j]):
                print(f"FAIL: Stabilizer {i} anticommutes with {j}")
                print(f"  {stabs[i]}")
                print(f"  {stabs[j]}")
                all_commute = False
    return all_commute

if check_commutation(stabilizers):
    print("All stabilizers commute.")
    try:
        # allow_underconstrained=True because 8 < 9
        tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers], allow_underconstrained=True)
        circuit = tableau.to_circuit("elimination")
        print("CIRCUIT_START")
        print(circuit)
        print("CIRCUIT_END")
    except Exception as e:
        print(f"Error creating tableau: {e}")
else:
    print("Stabilizers do not commute.")
