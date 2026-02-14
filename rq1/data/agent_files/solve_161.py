import stim

def solve_circuit():
    with open("stabilizers_161.txt", "r") as f:
        stabilizers_str = [line.strip() for line in f if line.strip()]
        
    num_qubits = len(stabilizers_str[0])
    stabilizers = [stim.PauliString(s) for s in stabilizers_str]
    
    # Try to find a completion
    sim = stim.TableauSimulator()
    # We can use the tableau simulator to check independence and find a completion.
    
    # Actually, stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
    # returns a tableau that prepares a state satisfying the stabilizers.
    # But does it guarantee +1 eigenstates?
    # The documentation says: "Returns a tableau where the first k Z generators match the given stabilizers."
    # The remaining n-k Z generators will be arbitrary completions.
    # So the state prepared by the inverse of this tableau (or the tableau itself acting on |0>?)
    # Let's check.
    # A Tableau T represents a Clifford C.
    # T.z_output(i) is the image of Z_i under C.
    # If we want a circuit C that prepares the state stabilized by S_0, ... S_{k-1},
    # we want C |0> to be stabilized by S_j.
    # Since |0> is stabilized by Z_i, we want C Z_i C^{-1} = S_i.
    # So we want the columns of the Tableau (the z_outputs) to be the stabilizers.
    
    try:
        # allow_underconstrained=True allows passing fewer than n stabilizers.
        # It will fill in the rest to make a complete basis.
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
        
        # Now we have a tableau T such that T(Z_i) = S_i for i < k.
        # The circuit that implements T will map |0...0> (stabilized by Z_i)
        # to a state stabilized by S_i.
        # Since the input state |0> is a +1 eigenstate of Z_i,
        # the output state T|0> will be a +1 eigenstate of T(Z_i) = S_i.
        # This is exactly what we want!
        
        # So we just need to convert the tableau to a circuit.
        circuit = tableau.to_circuit("elimination")
        
        print("Circuit generated successfully.")
        
        # Verify the circuit using the tool (simulated here first)
        # We can simulate it and check if stabilizers are preserved.
        
        with open("circuit_161.stim", "w") as f:
            f.write(str(circuit))
            
    except Exception as e:
        print(f"Failed to generate circuit: {e}")

if __name__ == "__main__":
    solve_circuit()
