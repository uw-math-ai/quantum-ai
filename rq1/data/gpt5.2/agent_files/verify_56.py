import stim

# Stabilizers
stabilizers = [
    "IIXIXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIXIXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    # ... just take a few
]

# I need to verify what stim.Tableau.from_stabilizers does.
# Documentation says: "Returns a tableau T such that T|0> is the stabilized state."
# So T.to_circuit() should work.

# Let's try a simple example.
# Stabilizer: X
# Circuit: H 0
# T = from_stabilizers(["X"])
# Circuit = H 0
# State: |+>. Stabilizer of |+> is X. Correct.

# Stabilizer: Z
# Circuit: I 0 (or empty)
# State: |0>. Stabilizer is Z. Correct.

# So the logic should be correct.

# Why did it fail?
# Maybe the list of stabilizers I gave to the tool was different order?
# The tool returns {stabilizer: result}.
# If the circuit prepares the state, ALL stabilizers should be preserved.

# Maybe the issue is the extra qubits?
# The circuit uses qubits up to 55.
# Wait, look at the circuit.
# CX 0 24 0 32 0 49
# ...
# 1 8 2 2 8 8 2 2 24 48 2 16 3 3 16 16 3
# What is "1 8 2 2..."?
# Ah, I see "CX ... 1 8 ...".
# In the circuit file:
# CX 8 0 48 0 49 1 1 49 49 1 1 24 25 1 33 1 ...
# 49 1 is CX 49 1.
# 1 49 is CX 1 49.

# The circuit text looks valid.

# Let's re-run the solver but this time verify locallly if possible.
# I can use stim to verify the circuit against the stabilizers.

def verify_locally():
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_56.stim", 'r') as f:
        circuit_text = f.read()
    
    circuit = stim.Circuit(circuit_text)
    
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_56.txt", 'r') as f:
        stabilizers = [line.strip() for line in f if line.strip()]
        
    print(f"Verifying {len(stabilizers)} stabilizers locally...")
    
    tableau = stim.Tableau.from_circuit(circuit)
    
    # Check if stabilizers are preserved
    # A stabilizer S is preserved if tableau(S) = +S ? 
    # No, we start with |0>. The circuit maps |0> to |psi>.
    # So we want S |psi> = |psi>.
    # |psi> = U |0>.
    # S U |0> = U |0>
    # U^dag S U |0> = |0>
    # So U^dag S U should be a stabilizer of |0> (i.e. a product of Zs with + sign).
    
    # stim.Tableau.from_circuit(circuit) gives T such that T(P) = U P U^dag.
    # We want U^dag S U.
    # U^dag S U = T.inverse()(S).
    
    t_inv = tableau.inverse()
    
    preserved_count = 0
    for s_str in stabilizers:
        p = stim.PauliString(s_str)
        out = t_inv(p)
        
        # Check if out is a product of Zs with no phase flip
        # PauliString has .sign and can check if X or Y are present.
        
        is_stabilizer_of_zero = True
        if out.sign != +1:
            is_stabilizer_of_zero = False
        
        # Check if any X or Y components
        # We can iterate or use specialized methods.
        # But for 'stabilizer of |0>', it must consist only of I and Z.
        # So no X components.
        # And sign must be +1.
        
        # Actually, |0> is stabilized by Z_i.
        # So any product of Z_i is also a stabilizer.
        # So we just need to ensure no Xs (which would mean X or Y Pauli).
        
        # stim.PauliString can explain itself.
        # But simpler: convert to numpy or string and check.
        
        out_str = str(out)
        if '-' in out_str: # Phase -1
            is_stabilizer_of_zero = False
        elif 'i' in out_str: # Phase i
            is_stabilizer_of_zero = False
        elif 'X' in out_str or 'Y' in out_str:
            is_stabilizer_of_zero = False
            
        if is_stabilizer_of_zero:
            preserved_count += 1
        else:
            print(f"Failed: {s_str} mapped to {out_str}")
            
    print(f"Locally preserved: {preserved_count}/{len(stabilizers)}")

if __name__ == "__main__":
    verify_locally()
