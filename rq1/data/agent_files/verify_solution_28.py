import stim

stabilizers = [
    "XXXXIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIXXXXIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIXXXXIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIXXXXIII",
    "XIXIXIXIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIXIXIXIXIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIXIXIXIXIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIXIXIXIX",
    "IIXXXXIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIXXXXIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIXXXXIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIXXXXI",
    "ZZZZIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIZZZZIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIZZZZIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIZZZZIII",
    "ZIZIZIZIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIZIZIZIZIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIZIZIZIZIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIZIZIZIZ",
    "IIZZZZIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIZZZZIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIZZZZIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIZZZZI",
    "IXXIXIIIXXIXIIIXXIXIIIXXIXII",
    "IZZIZIIIZZIZIIIZZIZIIIZZIZII"
]

def check():
    with open("circuit_candidate.stim", "r") as f:
        circuit_text = f.read()
    
    circuit = stim.Circuit(circuit_text)
    # The circuit might use more qubits than 28.
    # We only care about the first 28 qubits.
    # However, to check stabilizers, we need to extend our Pauli strings to the full size
    # by padding with Identity.
    
    num_qubits = circuit.num_qubits
    tableau = stim.Tableau.from_circuit(circuit)
    inverse_tableau = tableau.inverse()
    
    all_good = True
    for s_str in stabilizers:
        # Pad s_str with I's to match num_qubits
        padded_s_str = s_str + "I" * (num_qubits - len(s_str))
        s = stim.PauliString(padded_s_str)
        conjugated = inverse_tableau(s)
        
        # Check if conjugated is identity or Z product with +1 sign
        if conjugated.sign != +1:
            print(f"FAIL: Stabilizer {s_str} mapped to {conjugated} (negative sign)")
            all_good = False
            continue
            
        # Check if X or Y present
        is_z = True
        for p in conjugated:
            if p == 1 or p == 2:
                is_z = False
                break
        
        if not is_z:
            print(f"FAIL: Stabilizer {s_str} mapped to {conjugated} (has X/Y)")
            all_good = False
    
    if all_good:
        print("SUCCESS: All stabilizers preserved.")
    else:
        print("FAILURE: Some stabilizers not preserved.")

if __name__ == "__main__":
    check()
