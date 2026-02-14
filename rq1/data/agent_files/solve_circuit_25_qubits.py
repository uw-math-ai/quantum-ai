import stim
import numpy as np
import sys

def solve_circuit():
    stabilizers_str = [
        "XZZXIIIIIIIIIIIIIIIIIIIII",
        "IIIIIXZZXIIIIIIIIIIIIIIII",
        "IIIIIIIIIIXZZXIIIIIIIIIII",
        "IIIIIIIIIIIIIIIXZZXIIIIII",
        "IIIIIIIIIIIIIIIIIIIIXZZXI",
        "IXZZXIIIIIIIIIIIIIIIIIIII",
        "IIIIIIXZZXIIIIIIIIIIIIIII",
        "IIIIIIIIIIIXZZXIIIIIIIIII",
        "IIIIIIIIIIIIIIIIXZZXIIIII",
        "IIIIIIIIIIIIIIIIIIIIIXZZX",
        "XIXZZIIIIIIIIIIIIIIIIIIII",
        "IIIIIXIXZZIIIIIIIIIIIIIII",
        "IIIIIIIIIIXIXZZIIIIIIIIII",
        "IIIIIIIIIIIIIIIXIXZZIIIII",
        "IIIIIIIIIIIIIIIIIIIIXIXZZ",
        "ZXIXZIIIIIIIIIIIIIIIIIIII",
        "IIIIIZXIXZIIIIIIIIIIIIIII",
        "IIIIIIIIIIZXIXZIIIIIIIIII",
        "IIIIIIIIIIIIIIIZXIXZIIIII",
        "IIIIIIIIIIIIIIIIIIIIZXIXZ",
        "XXXXXZZZZZZZZZZXXXXXIIIII",
        "IIIIIXXXXXZZZZZZZZZZXXXXX",
        "XXXXXIIIIIXXXXXZZZZZZZZZZ",
        "ZZZZZXXXXXIIIIIXXXXXZZZZZ"
    ]
    
    num_qubits = 25
    paulis = [stim.PauliString(s) for s in stabilizers_str]
    
    found_25 = None
    
    # Check single qubit Z
    for i in range(num_qubits):
        candidate = stim.PauliString(num_qubits)
        candidate[i] = "Z"
        if all(p.commutes(candidate) for p in paulis):
            try:
                t = stim.Tableau.from_stabilizers(paulis + [candidate])
                found_25 = candidate
                print(f"Found 25th stabilizer: Z{i}")
                break
            except Exception:
                pass
    
    if not found_25:
        # Check single qubit X
        for i in range(num_qubits):
            candidate = stim.PauliString(num_qubits)
            candidate[i] = "X"
            if all(p.commutes(candidate) for p in paulis):
                try:
                    t = stim.Tableau.from_stabilizers(paulis + [candidate])
                    found_25 = candidate
                    print(f"Found 25th stabilizer: X{i}")
                    break
                except Exception:
                    pass
    
    if not found_25:
        # Random search
        print("Starting random search...")
        for _ in range(5000):
            candidate = stim.PauliString.random(num_qubits)
            if all(p.commutes(candidate) for p in paulis):
                try:
                    t = stim.Tableau.from_stabilizers(paulis + [candidate])
                    found_25 = candidate
                    print(f"Found random stabilizer")
                    break
                except Exception:
                    pass
    
    if found_25 is None:
        print("Failed to find 25th stabilizer.")
        return

    full_stabilizers = paulis + [found_25]
    t = stim.Tableau.from_stabilizers(full_stabilizers)
    circuit = t.to_circuit()
    
    with open("circuit_solution.stim", "w") as f:
        f.write(str(circuit))
    print("Circuit generated.")

if __name__ == "__main__":
    solve_circuit()
