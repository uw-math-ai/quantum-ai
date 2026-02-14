import stim
import sys

def solve():
    print("Reading stabilizers...")
    try:
        with open('target_stabilizers_60.txt', 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("Error: target_stabilizers_60.txt not found")
        return

    # Convert strings to stim.PauliString
    print(f"Loaded {len(lines)} stabilizers.")
    pauli_strings = []
    for line in lines:
        try:
            line_str = line
            # Ensure it's just Pauli characters
            if not all(c in 'IXYZ' for c in line_str):
                print(f"Invalid characters in stabilizer: {line_str}")
                continue
            pauli_strings.append(stim.PauliString(line_str))
        except Exception as e:
            print(f"Error parsing stabilizer '{line}': {e}")
            return

    if not pauli_strings:
        print("No valid stabilizers found.")
        return

    # Create tableau from stabilizers
    print("Generating tableau...")
    try:
        # allow_underconstrained=True is needed if we have < 60 stabilizers for 60 qubits
        tableau = stim.Tableau.from_stabilizers(pauli_strings, allow_underconstrained=True)
        
        print("Converting to circuit...")
        circuit = tableau.to_circuit("elimination")
        
        # Save circuit
        with open("circuit_attempt.stim", "w") as f:
            f.write(str(circuit))
            
        print("Circuit generated and saved to circuit_attempt.stim")
        
    except Exception as e:
        print(f"Error generating circuit: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    solve()
