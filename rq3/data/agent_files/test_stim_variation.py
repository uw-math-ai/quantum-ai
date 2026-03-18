import stim
import random

def get_cx(circuit):
    cx = 0
    for instr in circuit:
        if instr.name == "CX":
            cx += len(instr.targets_copy()) // 2
        elif instr.name == "CZ":
            cx += len(instr.targets_copy()) // 2
    return cx

def test():
    # Create a random stabilizer state on 5 qubits
    sim = stim.TableauSimulator()
    for _ in range(10):
        a = random.randint(0, 4)
        b = random.randint(0, 4)
        if a != b:
            sim.do(stim.Circuit(f"H {a}\nCX {a} {b}"))
    
    # Get stabilizers
    tableau = sim.current_inverse_tableau() ** -1
    stabilizers = tableau.to_stabilizers()
    
    # Synthesize with random permutations
    results = set()
    for _ in range(20):
        perm = list(range(5))
        random.shuffle(perm)
        
        # Apply perm to stabilizers
        perm_stabs = []
        for s in stabilizers:
            s_str = str(s)
            # s_str is "+XZ..."
            phase = s_str[0]
            paulis = s_str[1:]
            new_paulis = ['I'] * 5
            for i, p in enumerate(paulis):
                new_paulis[perm[i]] = p
            perm_stabs.append(stim.PauliString(phase + "".join(new_paulis)))
            
        # Synthesize
        t = stim.Tableau.from_stabilizers(perm_stabs)
        c = t.to_circuit("elimination")
        cx = get_cx(c)
        results.add(cx)
        
    print(f"CX counts found: {sorted(list(results))}")

if __name__ == "__main__":
    test()
