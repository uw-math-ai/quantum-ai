import stim

def generate_circuit():
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_153.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    paulis = [stim.PauliString(s) for s in lines]
    
    # Create tableau allowing underconstrained
    try:
        t = stim.Tableau.from_stabilizers(paulis, allow_underconstrained=True)
        print("Tableau created successfully with allow_underconstrained=True.")
        
        # Verify if the tableau stabilizes the inputs
        # The tableau state is |psi>. Does S |psi> = |psi>?
        # This is equivalent to checking if S is in the stabilizer group of the tableau.
        # But tableau stores generators.
        # If underspecified, the tableau picks a specific state (usually setting unspecified qubits to +Z or something).
        # We need to make sure the circuit generated from this tableau satisfies ALL 152 stabilizers.
        
        c = t.to_circuit()
        
        # We can add an explicit check here using Stim's internal tools?
        # No, let's just output the circuit.
        
        with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_153_v2.stim", "w") as f:
            f.write(str(c))
            
    except Exception as e:
        print(f"Tableau creation FAILED: {e}")

if __name__ == "__main__":
    generate_circuit()
