import stim

generators = [
    "XXXXXXIII",
    "XXXIIIXXX",
    "ZZIIIIIII",
    "ZIZIIIIII",
    "IIIZZIIII",
    "IIIZIZIII",
    "IIIIIIZZI",
    "IIIIIIZIZ"
]

circuit_str = """
CX 1 0 0 1 1 0
H 0
CX 0 2 0 3 0 8
H 1
CX 1 0 2 1 1 2 2 1 2 1 3 2 2 3 3 2 3 2 3 4 3 5 7 6 6 7 7 6 6 7 8 6 8 7
"""

try:
    c = stim.Circuit(circuit_str)
    print("Circuit parsed successfully.")
    
    t = stim.Tableau.from_circuit(c)
    t_inv = t.inverse()
    
    all_good = True
    for i, g_str in enumerate(generators):
        g = stim.PauliString(g_str)
        
        # Check if g is stabilized by the state prepared by c (from |0...0>)
        # This is equivalent to checking if t_inv(g) is a Z-type operator on |0...0>
        # (i.e. only I and Z terms, no X or Y) and has +1 phase.
        
        # Since t_inv maps output operators back to input operators,
        # and the input state is stabilized by +Z0, +Z1, ...,
        # any stabilizer of the output state must map back to a product of +Zi's.
        
        # However, t_inv(g) is a PauliString. We can check its components.
        # But wait, stim.PauliString.after() takes a Tableau.
        # So:
        g_back = g.after(t_inv)
        
        # Check if g_back has any X component.
        has_x = False
        for k in range(len(g_back)):
            # In stim, 0=I, 1=X, 2=Y, 3=Z
            # Actually, accessing components directly is tricky without converting to numpy.
            # But we can just check if it commutes with all Z's? No.
            # We can check if it's strictly Z-like.
            # A Pauli string is Z-like if it commutes with all Z_i? No, Z_i commutes with Z_j.
            # It is Z-like if it commutes with all X_i? No.
            # It is Z-like if it has no X component.
            pass

        # Easier way: Convert to numpy or check string representation.
        s = str(g_back)
        # s looks like "+Z_Z__Z"
        if 'X' in s or 'Y' in s:
            print(f"Generator {i} ({g_str}) maps to {s} (has X/Y) -> FAIL")
            all_good = False
        elif s.startswith('-'):
            print(f"Generator {i} ({g_str}) maps to {s} (negative) -> FAIL")
            all_good = False
        else:
            print(f"Generator {i} ({g_str}) maps to {s} -> OK")

    if all_good:
        print("All generators preserved.")
    else:
        print("Some generators failed.")

except Exception as e:
    print(f"Error: {e}")
