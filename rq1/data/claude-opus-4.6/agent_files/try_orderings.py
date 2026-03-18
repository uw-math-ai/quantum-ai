import stim
import itertools
import random

# Define stabilizers
stabilizers = [
    "XZZXIIIIIIIIIIIIIIII",
    "IIIIIXZZXIIIIIIIIIII",
    "IIIIIIIIIIXZZXIIIIII",
    "IIIIIIIIIIIIIIIXZZXI",
    "IXZZXIIIIIIIIIIIIIII",
    "IIIIIIXZZXIIIIIIIIII",
    "IIIIIIIIIIIXZZXIIIII",
    "IIIIIIIIIIIIIIIIXZZX",
    "XIXZZIIIIIIIIIIIIIII",
    "IIIIIXIXZZIIIIIIIIII",
    "IIIIIIIIIIXIXZZIIIII",
    "IIIIIIIIIIIIIIIXIXZZ",
    "ZXIXZIIIIIIIIIIIIIII",
    "IIIIIZXIXZIIIIIIIIII",
    "IIIIIIIIIIZXIXZIIIII",
    "IIIIIIIIIIIIIIIZXIXZ",
    "XXXXXXXXXXXXXXXXXXXX",
    "ZZZZZZZZZZZZZZZZZZZZ",
]

pauli_strings = [stim.PauliString(s) for s in stabilizers]

# Try many random orderings of stabilizers
best_cz = float('inf')
best_circuit = None

random.seed(42)
for trial in range(100):
    # Shuffle stabilizers
    shuffled = list(pauli_strings)
    random.shuffle(shuffled)
    
    try:
        tableau = stim.Tableau.from_stabilizers(
            shuffled,
            allow_redundant=True,
            allow_underconstrained=True
        )
        
        circuit = tableau.to_circuit(method='graph_state')
        cz_count = sum(len(i.targets_copy())//2 for i in circuit if i.name == 'CZ')
        
        if cz_count < best_cz:
            best_cz = cz_count
            best_circuit = circuit
            print(f"Trial {trial}: CZ={cz_count}")
    except Exception as e:
        pass

print(f"\nBest CZ count: {best_cz}")

if best_circuit:
    # Clean up
    clean_lines = []
    for inst in best_circuit:
        name = inst.name
        if name == "RX":
            targets = inst.targets_copy()
            for t in targets:
                clean_lines.append(f"H {t.value}")
        else:
            clean_lines.append(str(inst))
    
    clean_circuit = stim.Circuit("\n".join(clean_lines))
    
    # Remove TICKs
    final_lines = []
    for inst in clean_circuit:
        if inst.name != "TICK":
            final_lines.append(str(inst))
    
    final_circuit = stim.Circuit("\n".join(final_lines))
    print(f"\nFinal circuit:\n{final_circuit}")
    
    with open("data/claude-opus-4.6/agent_files/candidate_best_ordering.stim", "w") as f:
        f.write(str(final_circuit))
