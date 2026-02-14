import stim

def generate_circuit():
    # Define the stabilizers
    # Note: 1st stabilizer padded to 28
    stabs_str = [
        "XXIIXXIIIIIIIIIIIIIIIIIIIIII", 
        "IIIIIIIXXIIXXIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIXXIIXXIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIXXIIXXI",
        
        "XIXIXIXIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIXIXIXIXIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIXIXIXIXIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIXIXIXIX",
        
        "IIIXXXXIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIXXXXIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIXXXXIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIXXXX",
        
        "ZZIIZZIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIZZIIZZIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIZZIIZZIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIZZIIZZI",
        
        "ZIZIZIZIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIZIZIZIZIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIZIZIZIZIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIZIZIZIZ",
        
        "IIIZZZZIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIZZZZIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIZZZZIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIZZZZ",
        
        "XXXIIIIXXXIIIIXXXIIIIXXXIIII",
        "ZZZIIIIZZZIIIIZZZIIIIZZZIIII"
    ]
    
    try:
        # Create list of stim PauliStrings
        pauli_stabs = [stim.PauliString(s) for s in stabs_str]
        
        # Create tableau with underconstrained allowed
        tableau = stim.Tableau.from_stabilizers(pauli_stabs, allow_underconstrained=True)
        
        # Convert to circuit
        circuit = tableau.to_circuit()
        
        return circuit
        
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    circuit = generate_circuit()
    if circuit:
        with open("circuit_attempt.stim", "w") as f:
            f.write(str(circuit))
        print("Circuit generated successfully.")
