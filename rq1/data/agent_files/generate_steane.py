import stim

# The stabilizers provided in the prompt
stabilizers = [
    stim.PauliString("XXIIXXI"),
    stim.PauliString("XIXIXIX"),
    stim.PauliString("IIIXXXX"),
    stim.PauliString("ZZIIZZI"),
    stim.PauliString("ZIZIZIZ"),
    stim.PauliString("IIIZZZZ"),
]

# Add a 7th stabilizer to fix the logical state.
# Let's try Logical Zero: ZZZZZZZ
stabilizers.append(stim.PauliString("ZZZZZZZ"))

try:
    # distinct stabilizers to full rank?
    # stim.Tableau.from_stabilizers expects a list of n stabilizers for n qubits.
    # It assumes these are the images of Z_0, ..., Z_{n-1}.
    tableau = stim.Tableau.from_stabilizers(stabilizers)
    
    # Generate circuit
    # The tableau represents the operation U such that U |0> is the stabilizer state.
    # Because U Z_k U^dag = stabilizer_k.
    # Since |0> is stabilized by Z_k, U |0> is stabilized by U Z_k U^dag.
    circuit = tableau.to_circuit(method="elimination")
    
    print("Circuit generated successfully.")
    print("---BEGIN CIRCUIT---")
    print(circuit)
    print("---END CIRCUIT---")

except Exception as e:
    print(f"Error: {e}")
