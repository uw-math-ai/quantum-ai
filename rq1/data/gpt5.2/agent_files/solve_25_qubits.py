import stim
import numpy as np

def solve():
    stabilizers = [
        "XXIIIXXIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIXXIIIXXIIIIIIII",
        "IIIIIIXXIIIXXIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIXXIIIXXII",
        "IIXXIIIXXIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIXXIIIXXIIIIII",
        "IIIIIIIIXXIIIXXIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIXXIIIXX",
        "IIIIXIIIIXIIIIIIIIIIIIIII",
        "IIIIIXIIIIXIIIIIIIIIIIIII",
        "IIIIIIIIIIIIXIIIIXIIIII",  # 10
        "IIIIIIIIIIIIIIIXIIIIXIIII", # 11
        "IIIIIZZIIIZZIIIIIIIIIIIII", # 12
        "IIIIIIIIIIIIIIIZZIIIZZIII", # 13
        "IZZIIIZZIIIIIIIIIIIIIIIII", # 14
        "IIIIIIIIIIIZZIIIZZIIIIIII", # 15
        "IIIIIIIZZIIIZZIIIIIIIIIII", # 16
        "IIIIIIIIIIIIIIIIIZZIIIZZI", # 17
        "IIIZZIIIZZIIIIIIIIIIIIIII", # 18
        "IIIIIIIIIIIIIZZIIIZZIIIII", # 19
        "ZZIIIIIIIIIIIIIIIIIIIIIII", # 20
        "IIIIIIIIIIIIIIIIIIIIIZZII", # 21
        "IIZZIIIIIIIIIIIIIIIIIIIII", # 22
        "IIIIIIIIIIIIIIIIIIIIIIIZZ"  # 23
    ]

    # Parse stabilizers into stim.PauliStrings
    pauli_stabilizers = [stim.PauliString(s) for s in stabilizers]

    # Verify we have 25 qubits
    num_qubits = len(stabilizers[0])
    print(f"Number of qubits: {num_qubits}")
    if num_qubits != 25:
        print("Error: Expected 25 qubits")
        return

    # Verify we have correct number of stabilizers
    # For a pure state, we expect N stabilizers for N qubits.
    # Here we have 24 stabilizers for 25 qubits? 
    # Let's check the list length.
    print(f"Number of stabilizers: {len(stabilizers)}")
    
    # If it is underconstrained (24 stabilizers for 25 qubits), we can add a dummy stabilizer or allow underconstrained.
    # However, usually these problems are full rank. Let's check if I missed one in copy-paste or if the problem is indeed underconstrained.
    # The user provided 24 lines.
    
    try:
        tableau = stim.Tableau.from_stabilizers(pauli_stabilizers, allow_underconstrained=True)
        circuit = tableau.to_circuit("elimination")
        print("CIRCUIT_START")
        print(circuit)
        print("CIRCUIT_END")
    except Exception as e:
        print(f"Error generating circuit: {e}")

if __name__ == "__main__":
    solve()
