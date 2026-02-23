import stim
import sys

def main():
    with open("data/gemini-3-pro-preview/agent_files/stabilizers_76.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    print(f"Loaded {len(lines)} stabilizers.")
    
    # Check length
    lengths = set(len(line) for line in lines)
    print(f"Lengths: {lengths}")
    
    if len(lengths) != 1:
        print("Error: Stabilizers have different lengths.")
        return

    n_qubits = list(lengths)[0]
    print(f"Number of qubits: {n_qubits}")

    # Check for consistency
    try:
        pauli_strings = [stim.PauliString(line) for line in lines]
        tableau = stim.Tableau.from_stabilizers(pauli_strings, allow_redundant=True, allow_underconstrained=True)
        print("Stabilizers are consistent.")
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # Check independence
    try:
        tableau_strict = stim.Tableau.from_stabilizers(pauli_strings, allow_redundant=False, allow_underconstrained=True)
        print("Stabilizers are independent.")
    except Exception as e:
        print(f"Stabilizers are NOT independent: {e}")

    # Generate circuit
    # If underconstrained, we might need to add Z stabilizers to fill the rest?
    # The prompt says "Act on exactly 76 data qubits".
    # If the tableau is underconstrained, to_circuit() will prepare the state stabilized by the given stabilizers 
    # and Z on the remaining degrees of freedom (init to 0).
    
    circuit = tableau.to_circuit()
    print("Circuit generated.")
    
    # Verify circuit locally
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    all_good = True
    for i, s in enumerate(pauli_strings):
        if sim.measure_observable(s) != 0: # 0 means +1 eigenvalue, 1 means -1
            print(f"Stabilizer {i} failed!")
            all_good = False
            break
            
    if all_good:
        print("Local verification passed!")
    else:
        print("Local verification FAILED!")

    # Save circuit to file
    with open("data/gemini-3-pro-preview/agent_files/circuit_76.stim", "w") as f:
        f.write(str(circuit))
        
if __name__ == "__main__":
    main()
